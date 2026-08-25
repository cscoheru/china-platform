# 31 — Stage 1 / S1.16 — R03 / docs/10 §2.4 跨源一致性 dbt 阈值测试规划

- 编号：`31-stage1-s16-r03-cross-source-dbt-plan-20260825`
- 作者：CC（规划 only；实现另开任务书）
- 前置：Cursor `117` S1.15 PASS；`118` 任务书；用户裁定 A
- 缺口定位（`docs/26` §1.4 / `docs/27` §4.1-2）：S1.14 交付了**检测并落表**（migration 006 + candidate/mart models + 9 pytest）；仍缺 **dbt `test_cross_source_consistency_threshold`**（§2.4 阈值**断言**）与 R03 **运行时可重复**冲突检测（当前仅 spike 人工核对 + pytest SQL 镜像）

---

## §0. docs/10 §2.4 阈值语义（先钉死，再谈测试）

docs/10 §2.4 原文语义（逐条翻译为工程判定）：

| 语义 | 数值 | 工程含义 |
|---|---|---|
| 相对偏差 | `abs(a−b)/a×100`，**a = 参照源**（例中 NBS，即 S0 优先） | 与 S1.14 candidate 的 `diff_pct` 同式；A 侧即低 source_level（staging 已实现 UUID tiebreak） |
| 记录线 | `> 2.0` → `record_disagreement` | S1.14 mart 已实现：`diff_pct < 2.0` WITHIN_TOLERANCE 不落表；`≥2 <5` RECORDED |
| 断言线 | `assert diff_pct < 5.0`（5% 阈值，超出人工核查） | **本刀要补的**：>5% 的 pair 若无人工核查结论 = 自动化红灯 |
| 分层 | S0 之间应一致；与 S1/S2 可有差异，**记录但不阻塞** | 断言线只对「应一致」域生效（见 §2.1 范围过滤） |

**与 gate_thresholds.json 无关声明**：2%/5% 是 docs/10 §2.4 验收常量（SQL 内实现，S1.14 既定）；`gate_thresholds.json` 是 spike-04 OCR 评测 gate（0–100 标度），不同构件，只读不写（与 S1.15 同一红线）。

## §1. 与 S1.14 的边界：复用什么、新交什么

| 构件 | 复用/新增 | 说明 |
|---|---|---|
| `stg_source_disagreement_candidate` | **复用** | ordered-pair 构造 + diff 计算 + A 侧选择规则（S0<S1 优先，UUID tiebreak）不动 |
| `mart_source_disagreement` | **复用** | severity 分类 + 落表（RECORDED/NEEDS_REVIEW）+ resolution 字段不动 |
| `dbt/tests/…/test_cross_source_consistency_threshold.sql` | **新增（singular test）** | §2.4 断言线的 dbt 化 — 唯一新 dbt 构件 |
| pytest | **新增 wrapper** | R03 自动化入口（§3） |
| migration | **无** | 无 schema 变更；006 表已够 |

**设计原则**：S1.14 回答「哪里不一致、记下来」（model 责任）；本刀回答「不可接受的不一致有没有被人工闭环」（test 责任）。不造新 model，不加第二套分类逻辑。

## §2. dbt test 设计

### §2.1 singular test：`dbt/tests/test_cross_source_consistency_threshold.sql`

```sql
-- docs/10 §2.4 断言线: diff_pct >= 5% 的 pair 必须已有人工核查结论。
-- 返回行 = 失败 (PENDING 的 NEEDS_REVIEW = 未闭环的 >5% 冲突)。
-- 阈值 2%/5% 与 mart_source_disagreement 内常量互为镜像 (docs/29 §7:
-- 参数化属 Stage 2, 改动须过用户)。
SELECT *
FROM {{ ref('mart_source_disagreement') }}
WHERE severity = 'NEEDS_REVIEW'          -- > 5% (与 mart 分类一致)
  AND resolution = 'PENDING'             -- 无 USE_A/USE_B/PARSE/PARALLEL 结论
  {{ -- S0↔S0 域才断言; S0↔S1 及以下记录不阻塞 (docs/10 §2.4 分层)
     '' }}
```

- 失败语义 = 存在**未闭环**的 >5% 冲突；`resolution ∈ {USE_A, USE_B, PARSE, PARALLEL}` 视为已人工核查（有结论即放行，结论本身在表里可审计）
- 「S0 之间应一致」的范围收紧（排除 S0↔S1 pair 出断言）实现时以 `source_a_level='S0' AND source_b_level='S0'` 过滤——mart 已携带两侧 level 列
- 第二个轻量 test（可选）：`test_mart_severity_matches_thresholds` 断言 mart 落表行 `diff_pct >= 2.0`（防止 WITHIN_TOLERANCE 泄入）——实现时若 mart WHERE 已保证则以注释说明免重复

### §2.2 为什么不是 generic test / 不改 mart

- 断言对象是**行的存在性**（aggregate 语义），singular test 一条 SQL 最短路径
- mart 改动 = 改变已 PASS 构件行为，无必要（S1.14 审计边界，117 §0）

## §3. R03「自动化」最小可验收定义

**定义**：一条命令、可重复、无网络、退出码即判定 —— `dbt test --select test_cross_source_consistency_threshold` 在 fixture 干净态 rc=0；注入一条 PENDING 的 NEEDS_REVIEW 行后 rc=1。

### §3.1 环境前提（诚实：dbt 当前在 3.14 不可用）

- 已知：dbt-core 在 Python 3.14 因 mashumaro `UnserializableField` 不可用（receipt 101/107 诚实缺口）
- 本机存在 `/opt/homebrew/bin/python3.11` → 计划以 **`.venv-dbt`（3.11 venv + dbt-core/dbt-postgres 钉版本）** 作为执行环境；pytest wrapper 以 subprocess 调用，PATH 指向 venv
- venv 不入 pack（环境构件非证据构件）；`requirements-dbt.txt` 钉版本入 repo（documentation/spike_helper 角色）

### §3.2 pytest 入口：`tests/test_r03_cross_source_dbt.py`

| 用例（实现时落） | 断言 |
|---|---|
| `test_dbt_env_available` | venv 内 `dbt --version` 可执行（不可用则 skip+诚实标记，不 fail——环境缺≠逻辑错） |
| `test_dbt_run_then_test_clean` | fixture（1%/3.5% 对）→ `dbt run` + `dbt test --select …` rc=0 |
| `test_dbt_test_fails_on_pending_needs_review` | 注入 8% PENDING 对 → rc≠0 且 stderr 含 test 名 |
| `test_dbt_test_passes_when_resolved` | 8% 对但 `resolution='PARSE'` → rc=0（已闭环放行语义） |
| `test_s0_s1_pair_not_asserted` | 8% 且一侧 S1 → 不触发断言（分层语义） |

### §3.3 CI 一步（建议，非本刀交付）

`make r03` 或 CI job：`source .venv-dbt/bin/activate && dbt build --select mart_source_disagreement+ && dbt test --select test_cross_source_consistency_threshold`。Stage 2 接入 CI 时引用本节。

## §4. seed / fixture 策略（不爬网）

- **不用 dbt seeds 承载观测数据**：seeds 仅适合静态参照（目前空，保持空）；观测对由 pytest fixture 直插（复用 s141 骨架：indicator/geo/period/双 S0 文档/observation）
- 数值矩阵：1%（WITHIN_TOLERANCE 不落表）/ 3.5%（RECORDED 不触发断言）/ 8%（NEEDS_REVIEW：PENDING 触发、RESOLVED 放行）——与 s141 同源，语义互补
- 无任何 HTTP；dbt 走 profiles.yml → 本地 `cegr_test`（127.0.0.1:55440）

## §5. 空表诚实

- 现库**无真实双 S0 源对**（second S0 缺席，receipt 107 §3 既列）：自动化语义全部由 fixture 证明
- 真实 pair 的 e2e 属 Stage 2（依赖第二 S0 源接入，非本刀可控）
- `.venv-dbt` 在 CI/他人环境需重建（requirements 钉版本缓解）；pytest 对缺环境 skip 不 fail 的取舍已在 §3.2 声明

## §6. 红线

❌ 不 Gate 1 PASS；❌ 不 DSH；❌ 不爬网；❌ 不改 `gate_thresholds.json`（§0 声明无关性）；❌ 不改 S1.14 已 PASS 构件行为（mart/candidate 只读复用）；❌ 规划 only，不写实现。

## §7. 诚实缺口 + 后续

1. 2%/5% 常量在 mart SQL + test 注释两处镜像 → 参数化（dbt var）与 S1.15 的 0.70 一并 Stage 2 过用户
2. `resolution` 结论的正确性（PARSE/PARALLEL 是否合理）无自动校验 — 人工域，Stage 2 research_note 表承接
3. dbt build 全链（staging→intermediate→marts）在 3.11 venv 下的首次全量回归未在本规划内验证 — 实现刀首步即跑
4. CI 接入（§3.3）待 Stage 2 基础设施裁定

— CC @ queue_rev 40，S1.16 规划（docs/31）—
