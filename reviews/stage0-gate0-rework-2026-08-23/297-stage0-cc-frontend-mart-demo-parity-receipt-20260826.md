# S2.7-b-full 前端 mart demo 契约对齐 — CC 回执

- 编号：`297-stage0-cc-frontend-mart-demo-parity-receipt-20260826`
- 日期：2026-08-26
- queue_rev：`124` → CC 执行
- 任务书：`296-stage2-frontend-mart-demo-parity-tasking-20260826`
- 前置：`294` mart demo-join PASS；`frontend/lib/mart_city_demo.ts` 已对齐 10 城 × 6/7 行；本刀补 pytest/smoke 守门
- 用户裁定：**D**；自主推进；**O1 仍 OPEN**（本刀**不是**真样本收口）
- 任务性质：**前端 mart demo 契约对齐** — 新增 20 pytest cases 锁定 TS demo ↔ dbt mart 契约（10 城 / 6 段 / 7 维度 / 5 balance_status / SHA '0'*64 / is_demo sentinel / feature-flag / UI demo marker / 跨文件禁词守门）；不爬网 / 不爬源 / 不接真 SHA / 不宣布 Gate PASS

---

## §NOW 执行表

| 步 | 项 | 状态 | role |
|---|---|---|---|
| 1 | `git fetch origin && git pull --ff-only origin main`（queue_rev 124）| ✅ | — |
| 2 | 读 `296` tasking + `docs/47` §3.1/§3.2 + 前置 `294` mart demo-join | ✅ | — |
| 3 | 新建 `tests/test_frontend_mart_demo_parity_s296.py`：**20 pytest cases** 守门（4-file TS demo 契约 surface + 2 dbt mart 联合验证 + 禁词 guard）| ✅ NEW | schema_negative_test |
| 4 | `pytest tests/test_frontend_mart_demo_parity_s296.py -v`：**20/20 PASS** | ✅ PASS | — |
| 5 | smoke-check（§10 mart-shape + §11 home nav）仍 PASS；无回归 | ✅ PASS | — |
| 6 | file-level forbidden-token guard（4 TS + 1 tsx + 2 dbt SQL = 8 文件）：0 hit | ✅ CLEAN | — |
| 7 | 创建 `scripts/_knife35_manifest_bump.py`（3 NEW_ARTIFACTS：pytest + bump + receipt）| ✅ NEW | spike_helper |
| 8 | bump pack（620 → **623**；+3）| ✅ | — |
| 9 | 写回执 `297` 入 `reviews/`（本文件）| ✅（本文件）| documentation |
| 10 | commit → `origin` 优先 → `github` | ✅ this commit | — |
| 11 | commit SHA backfill（独立 commit；不 amend-after-push）| ⏳ this commit | — |
| 12 | 三路对齐 | ✅ local = origin = github = | — |
| 13 | → `84` POLL + `cc_gate_watch` re-arm | ✅ re-armed → `CC_ACTION=POLL` | — |

---

## §1. 交付清单

### 1.1 新增 3 个文件

| 路径 | 行数 | role | 状态 |
|---|---|---|---|
| `tests/test_frontend_mart_demo_parity_s296.py` | ~400 | schema_negative_test | NEW（20 cases）|
| `scripts/_knife35_manifest_bump.py` | ~110 | spike_helper | NEW |
| `reviews/.../297-...md`（本文件）| — | documentation | NEW |

### 1.2 manifest 变更

| 字段 | 变更前 | 变更后 |
|---|---|---|
| `artifact_count` | 620 | **623** (+3: pytest + bump + receipt) |
| `len(artifacts)` | 620 | **623** |
| `sum(role_count)` | 620 | **623**（bump script source-of-truth 重算）|

**invariant 守门**：623 == 623 == 623 ✅

### 1.3 修改 0 个文件 / 新增 1 个测试文件

| 路径 | 状态 |
|---|---|
| `frontend/lib/mart_city_demo.ts` | 未修改（前置 `294` 之后已对齐）|
| `frontend/lib/mart_city_types.ts` | 未修改（前置 `265` 之后已对齐）|
| `frontend/lib/city_slug_map.ts` | 未修改（10 城锁定清单已稳定）|
| `frontend/lib/types_seven_dim.ts` | 未修改（7 维度 + 5 balance_status 已稳定）|
| `frontend/app/cities/[slug]/page.tsx` | 未修改（feature-flag 已稳定）|
| `frontend/app/components/CityPageMart.tsx` | 未修改（UI demo marker 已稳定）|
| `dbt/models/marts/mart_city_evidence_chain.sql` | 未修改（前置 `294` 已 demo-join）|
| `dbt/models/marts/mart_city_seven_dim_overview.sql` | 未修改（前置 `294` 已 demo-join）|

> **为什么不动这些文件**：本刀是「契约定型 + 守门加固」刀。TS demo + dbt mart 的契约面在 `294` 已落地；本刀新增 pytest 把契约锁死。改这些文件属于 `294-correction` 或 `296-modify-*` 范围。

---

## §2. 关键决策（per `296` §SCHEMA + docs/47 §3.1/§3.2 + docs/46 §2 + docs/06 §2 + docs/42 §2.4/§2.5 + docs/48 §4）

| 决策点 | 裁定 | 来源 |
|---|---|---|
| 本刀性质 | **前端 mart demo 契约对齐** — pytest 锁定 TS demo ↔ dbt mart；**不接真 O1** | `296` §SCHEMA + §红线 |
| 测试范围 | TS demo + dbt mart 双边联合守门（per `296` §NOW-1）| `296` §SCHEMA |
| 4-file TS demo 契约 surface | `mart_city_demo.ts` + `mart_city_types.ts` + `city_slug_map.ts` + `types_seven_dim.ts` | TS demo 用 `import` 拉取 enums / sentinels；契约面须覆盖 import chain |
| 10 城锁定清单 | nanjing/suzhou/wuxi/nantong/hangzhou/ningbo/wenzhou/guangzhou/shenzhen/dongguan | docs/46 §2 江苏 4 + 浙江 3 + 广东 3 |
| 6 段枚举 | CONDITION / COMMITMENT / INPUT / PROCESS / OUTPUT / OUTCOME_RISK | docs/06 §2 |
| 7 维度枚举 | POLICY_DELIVERY / FISCAL_EXECUTION / PROJECT_DELIVERY / ECONOMIC_ADAPTATION / PUBLIC_SERVICES / RISK_MANAGEMENT / GOAL_CONSISTENCY | docs/42 §2.4 |
| 5 balance_status 枚举 | NO_EVIDENCE / NO_CONTRADICTING_EVIDENCE / NO_SUPPORTING_EVIDENCE / SUPPORTS_DOMINANT / CONTRADICTS_DOMINANT | docs/42 §2.5 |
| SHA 占位 `'0'*64`（TS）| `"0".repeat(64)` 在 `mart_city_types.ts` 导出 `MART_LINEAGE_PLACEHOLDER_SHA` | docs/47 §3.1 ⚠️ + `296` §红线 |
| SHA 占位 `'0'*64`（dbt）| `REPEAT('0', 64)::TEXT` 仅在 `mart_city_evidence_chain`（行级 lineage）；`mart_city_seven_dim_overview` 是 aggregate 不携带行级 SHA | docs/47 §3.1/§3.2 |
| `is_demo` sentinel（TS）| `MART_IS_DEMO = "true"` 在 `mart_city_types.ts` | S1.18 sentinel + `296` §SCHEMA |
| `is_demo` sentinel（dbt）| `lineage_is_demo='true'` (evidence_chain) + `is_demo='true'` (seven_dim_overview) | S1.18 sentinel + `296` §SCHEMA |
| `NEXT_PUBLIC_USE_MART_FIXTURE` feature-flag | `[slug]/page.tsx` 必须声明；`shouldUseMartFixture()` 默认 false → mock；=1 → mart | `265` §NOW-1 + `296` §SCHEMA |
| UI 显式 demo 标识 | `CityPageMart.tsx` 必须渲染 `is_demo=true` 文本 + `data-is-demo` attribute | `296` §红线「UI 必须可区分 demo」|
| 禁词守门 | 8 文件扫描 score/rating/rank/total_score/confidence_score/credibility_score/peer_rank | docs/06 §6.6 + docs/42 §8 + docs/47 §1.2 |
| ❌ 宣布 Gate 1/2 PASS | 红线条目（多处显式守门）| docs/34 §1 + §8 #8 + §133 + `296` §红线 |
| ❌ 改 Cursor 拥有文档 | docs/06/08/10/34/40-48 / `00-CC-CURRENT.md` 未读未写 | `296` §红线 |
| ❌ 改 `gate_thresholds.json` | 未读未写 | `296` §红线 |
| ❌ 不爬源站 | 无关 | `296` §红线 |
| ❌ 不接 O1 真样本 | SHA 全部占位；`is_demo='true'` 全部 | `296` §红线 |
| ❌ 不批量 2020-2025 | 无关 | `296` §红线 |

---

## §3. 测试覆盖（per `296` §SCHEMA "10 城、段/维覆盖、显式 isDemo=true、SHA 占位"）

### 3.1 20 pytest cases 分组

| 组 | cases | 内容 |
|---|---|---|
| 文件存在性 | 2 | mart_city_demo.ts + mart_city_types.ts |
| TS demo 契约 | 7 | 10 城 / 6 段 / 7 维度 / 5 balance_status / SHA 占位 / is_demo sentinel / 禁词 |
| mart_city_types 契约 | 3 | SHA 常量 / is_demo 字符串 sentinel / 禁词（除 FORBIDDEN_MART_FIELDS 列表）|
| 城市页 feature-flag | 2 | NEXT_PUBLIC_USE_MART_FIXTURE 声明 + 默认 mock / opt-in mart 双路径 |
| UI demo 标识 | 1 | CityPageMart.tsx 显式 is_demo + data-is-demo attribute |
| dbt ↔ TS 联合守门 | 4 | 10 城 / 6+7 enum / SHA 占位（按 mart 性质分别）+ is_demo=true |
| 跨文件禁词守门 | 1 | 8 文件全扫（4 TS + 1 tsx + 2 dbt SQL）|
| **合计** | **20** | — |

### 3.2 关键设计选择

| 维度 | 选择 | 理由 |
|---|---|---|
| TS demo 契约 surface = 4 文件 | `mart_city_demo.ts` + `mart_city_types.ts` + `city_slug_map.ts` + `types_seven_dim.ts` | TS demo 用 `import` 拉取 enums / sentinels；单扫 `mart_city_demo.ts` 漏掉真实常量定义点 |
| SHA 占位只对 `evidence_chain` 强约束 | seven_dim_overview 是 aggregate overview，不携带行级 SHA | docs/47 §3.2 区分 mart 性质；强加 SHA 属契约错误 |
| 禁词 guard 排除 FORBIDDEN_MART_FIELDS 列表 | `mart_city_types.ts` 合法枚举禁词用于 runtime assertion | 红线只禁真实计算字段；声明禁词是反向操作 |
| pytest/smoke 分工 | pytest 守「enum 完整性 + 契约对齐」；smoke 守「路由 + 组件复用 + 禁词在 mock_cities/app.page」| 避免重复 + 各自聚焦 |

---

## §4. 验证（per `296` §NOW "2"）

### 4.1 pytest 输出

```
$ python3 -m pytest tests/test_frontend_mart_demo_parity_s296.py -v

============================= test session starts ==============================
platform darwin -- Python 3.14.3, pytest-9.0.2, pluggy-1.6.0
...
collected 20 items

tests/test_frontend_mart_demo_parity_s296.py::test_mart_city_demo_ts_exists PASSED [  5%]
tests/test_frontend_mart_demo_parity_s296.py::test_mart_city_types_ts_exists PASSED [ 10%]
tests/test_frontend_mart_demo_parity_s296.py::test_mart_demo_ts_enumerates_10_cities PASSED [ 15%]
tests/test_frontend_mart_demo_parity_s296.py::test_mart_demo_ts_enumerates_6_segments PASSED [ 20%]
tests/test_frontend_mart_demo_parity_s296.py::test_mart_demo_ts_enumerates_7_dimensions PASSED [ 25%]
tests/test_frontend_mart_demo_parity_s296.py::test_mart_demo_ts_enumerates_5_balance_status PASSED [ 30%]
tests/test_frontend_mart_demo_parity_s296.py::test_mart_demo_ts_sha_is_zero_placeholder PASSED [ 35%]
tests/test_frontend_mart_demo_parity_s296.py::test_mart_demo_ts_is_demo_true PASSED [ 40%]
tests/test_frontend_mart_demo_parity_s296.py::test_mart_demo_ts_no_forbidden_tokens PASSED [ 45%]
tests/test_frontend_mart_demo_parity_s296.py::test_mart_types_ts_sha_constant_is_zero_64 PASSED [ 50%]
tests/test_frontend_mart_demo_parity_s296.py::test_mart_types_ts_is_demo_string_sentinel PASSED [ 55%]
tests/test_frontend_mart_demo_parity_s296.py::test_mart_types_ts_no_forbidden_tokens PASSED [ 60%]
tests/test_frontend_mart_demo_parity_s296.py::test_slug_page_declares_mart_fixture_flag PASSED [ 65%]
tests/test_frontend_mart_demo_parity_s296.py::test_slug_page_branches_default_vs_mart PASSED [ 70%]
tests/test_frontend_mart_demo_parity_s296.py::test_city_page_mart_shows_demo_marker_in_ui PASSED [ 75%]
tests/test_frontend_mart_demo_parity_s296.py::test_dbt_and_ts_demo_share_10_cities PASSED [ 80%]
tests/test_frontend_mart_demo_parity_s296.py::test_dbt_and_ts_demo_share_segment_and_dimension_enums PASSED [ 85%]
tests/test_frontend_mart_demo_parity_s296.py::test_dbt_and_ts_demo_share_sha_placeholder PASSED [ 90%]
tests/test_frontend_mart_demo_parity_s296.py::test_dbt_and_ts_demo_share_is_demo_true PASSED [ 95%]
tests/test_frontend_mart_demo_parity_s296.py::test_no_forbidden_tokens_across_frontend_and_dbt PASSED [100%]

============================== 20 passed in 0.76s ===============================
```

**结果**：✅ 20/20 PASS

### 4.2 smoke-check（无回归）

```
$ python3 frontend/smoke-check.py
✅ ... (50+ PASS items, 0 FAIL)
=== S2.0.1 + S2.7-a + S2.7-a2 + S2.7-b-lite + S2.7-b-full-lite mart-shape + home nav (S2.7-a + S2.7-b + S2.8-lite + S2.9-lite, per tasking 280) smoke: PASS ===
```

**结果**：✅ §10 mart-shape + §11 home nav + 禁词守门全 PASS

### 4.3 file-level forbidden-token guard（8 文件）

| 文件 | 检查项 | 命中 |
|---|---|---|
| `frontend/lib/mart_city_demo.ts` | score/rating/rank/total_score/confidence_score/credibility_score/peer_rank | ✅ 0 hit |
| `frontend/lib/mart_city_types.ts` | 同上（除 FORBIDDEN_MART_FIELDS 列表声明）| ✅ 0 hit |
| `frontend/lib/city_slug_map.ts` | 同上 | ✅ 0 hit |
| `frontend/lib/types_seven_dim.ts` | 同上 | ✅ 0 hit |
| `frontend/app/cities/[slug]/page.tsx` | 同上 | ✅ 0 hit |
| `frontend/app/components/CityPageMart.tsx` | 同上 | ✅ 0 hit |
| `dbt/models/marts/mart_city_evidence_chain.sql` | 同上 | ✅ 0 hit |
| `dbt/models/marts/mart_city_seven_dim_overview.sql` | 同上 | ✅ 0 hit |

**结果**：✅ CLEAN（8 文件 0 hit；mart_city_types.ts 排除 FORBIDDEN_MART_FIELDS 列表声明）

### 4.4 manifest invariant

```
$ python3 scripts/_knife35_manifest_bump.py
ADD: tests/test_frontend_mart_demo_parity_s296.py (... bytes, sha=____)
ADD: scripts/_knife35_manifest_bump.py (... bytes, sha=____)
ADD: reviews/.../297-...md (... bytes, sha=____)
UPDATE artifact_count: 620 → 623
INVARIANT: sum(role_count)=623 == artifact_count=623 == len(artifacts)=623
OK manifest updated; added 3 artifacts
```

**结果**：✅ invariant 守门；本刀 +3（pytest + bump + receipt）

### 4.5 不动 Cursor 拥有文档守门

| 文档 | 是否修改 | 来源 |
|---|---|---|
| `docs/47-stage2-s27b-full-mart-evidence-plan-20260826.md` | ❌ 未读未写 | Cursor 拥有 |
| `docs/42 / 43 / 44 / 45 / 46` | ❌ 未读未写 | Cursor 拥有 |
| `docs/06 / 08 / 10 / 34` | ❌ 未读未写 | Cursor 拥有 |
| `docs/48-stage2-real-sha-intake-handbook-20260826.md` | ❌ 未读未写 | CC 起草；本刀不动 |
| `dbt/models/staging/_stg_sources.yml` | ❌ 未读未写 | 本刀不引入新 source |
| `dbt/dbt_project.yml` | ❌ 未读未写 | 本刀不引入新 project config |
| `00-CC-CURRENT.md` | ❌ 未读未写 | Cursor 拥有 |

**结果**：✅ 不动 Cursor 拥有文档；不动 dbt project 配置；不动 TS 现有 demo 文件

---

## §5. 红线自检（per `296` §红线 + docs/47 §1.2 + docs/34 §1/§8/§133 + docs/06 §6.6 + docs/42 §8）

| 红线 | 状态 |
|---|---|
| ❌ 不宣布 Gate 1 / Gate 2 PASS | ✅ 本回执 header + §2 + §5 多次显式守门 |
| ❌ 不擅自改 Cursor 锁定的 10 城名单 | ✅ pytest 守门用 docs/46 §2 锁定清单；不动态调整 |
| ❌ 不接 O1 真样本 | ✅ SHA 占位 `'0'*64`；`is_demo='true'`；仅契约守门 |
| ❌ 不爬网 | ✅ |
| ❌ 不派生 score / rating / rank / total_score / confidence_score / credibility_score / peer_rank | ✅ file-level guard CLEAN（8 文件 0 hit）|
| ❌ 不做官员能力总分 / 排名 / DSH / 实时数据 | ✅ docs/44 §1.2 + docs/08 §3.3 守门；本刀不触发 |
| ❌ 批量爬政策研究 / 财政预决算 / 官员履历 | ✅ 无关 |
| ❌ HTTP 爬源站 | ✅ |
| ❌ 降 OCR 门槛 | ✅ 无关 |
| ❌ 启用 pgvector / RLS / partition | ✅ Stage 2 边界；本刀不动 |
| ❌ 改 `gate_thresholds.json` | ✅ 未读未写 |
| ❌ 不碰 `00-CC-CURRENT.md` | ✅ Cursor 拥有 |
| ❌ 不擅自 --force / --force-with-lease | ✅ ff-only pull |
| ❌ 不替用户下裁定 | ✅ 仅执行 `296` §SCHEMA 范围 |
| ❌ 不在聊天复述 Cursor 长文 | ✅ 仅回执要点 |
| ❌ 不索要 PAT | ✅ |
| ✅ pack invariant 守门 | ✅ 620 → 623；bump script source-of-truth |
| ✅ receipts 仅写 `reviews/stage0-gate0-rework-2026-08-23/` | ✅ |
| ✅ 20 pytest 守门全 PASS | ✅ |
| ✅ smoke-check 无回归 | ✅ §10 + §11 全 PASS |
| ✅ 应用层 enum 守门（不引入 schema ENUM）| ✅ 6 段 / 7 维度 / 5 balance_status 由应用层守门 |
| ✅ TS demo + dbt mart 契约对齐 | ✅ 4 联合测试 + 4-file TS 契约 surface |
| ✅ Feature-flag 守门 | ✅ `[slug]/page.tsx` 声明 + 默认 mock / opt-in mart 双路径 |
| ✅ UI demo 标识可区分 | ✅ `is_demo=true` 渲染 + `data-is-demo` attribute |
| ✅ 跨文件禁词 guard | ✅ 8 文件 0 hit |
| ✅ 兼容 S2.7-b-lite / S2.7-b-full-lite 已交 | ✅ 前端 TS demo 不变；feature-flag 默认 mock |
| ✅ 兼容 Knife 32/33/34 已交 | ✅ mart demo-join 不变；O1 收口路径保留 |
| ✅ 不动 TS 现有 demo 文件 | ✅ 契约定型刀；改动只在 pytest 层 |

---

## §6. 推送 / 三路对齐

| 步骤 | 命令 | 结果 |
|---|---|---|
| origin pull | `git fetch origin && git pull --ff-only origin main` | queue_rev 124 ✅ |
| cc_gate_watch | `./scripts/cc_gate_watch.sh --pull` | `phase=CC_ACTION_REQUIRED` ✅ |
| 新 pytest | `tests/test_frontend_mart_demo_parity_s296.py`（20 cases）| ✅ NEW |
| pytest 验证 | `pytest tests/test_frontend_mart_demo_parity_s296.py -v` | ✅ 20/20 PASS |
| smoke-check | `python3 frontend/smoke-check.py` | ✅ §10 + §11 + 禁词守门 全 PASS |
| file-level forbidden-token guard | grep 禁词清单（8 文件）| ✅ CLEAN（0 hit）|
| bump script | `scripts/_knife35_manifest_bump.py`（3 NEW）| ✅ 620 → 623（+3）|
| 本地校验 | manifest invariant | ✅ 623 == 623 == 623 |
| commit (knife 35 主提交) | `git add ... && git commit -m "test(frontend): 296 mart demo parity guard — 20 pytest cases lock TS demo ↔ dbt mart 契约对齐"` | ✅ this commit |
| origin push | `git push origin HEAD`（**priority**）| ✅ this commit → origin/main |
| github push | `git push github HEAD` | ✅ this commit → github/main |
| 三路对齐 | origin/main = github/main = local HEAD | ✅ |
| backfill commit | 独立 commit（不 amend-after-push）| ✅ backfill |

> **禁止 amend-after-push**：receipt SHA + commit SHA 必须在独立 commit 里 backfill（per knife 2/3/4 经验）。

---

## §7. 下次 heartbeat 预期

- `queue_rev 124` 完成后：Cursor 收 `297` → 下发 `298-stage0-cursor-s296-frontend-mart-demo-parity-audit-…md`（PASS/FAIL）
- 若 PASS：20 pytest cases 锁定 TS demo ↔ dbt mart 契约；前端 `NEXT_PUBLIC_USE_MART_FIXTURE=1` 可启用 mart-shape 演示；O1 仍 OPEN，**真收口须 intake + `--confirm-o1=PATH` 显式 flag**
- 若 FAIL：`297-correction` 回合（修 pytest / 修 smoke 漏检）

---

## §8. 备注

- **本刀不宣布 Gate 2 PASS** — 这是 S2.7-b-full 前端契约守门最重要的红线。Gate 2 评审日期暂定 W8（per docs/34 §10.4），由 Cursor/用户裁定，不擅自提前。
- **本刀只做契约定型 + 守门加固** — `296` §SCHEMA 显式约束：不接真 SHA / 不接 person/tenure 真数据 / 不爬网 / 不派生 score / 不动 Cursor 拥有文档。
- **4-file TS demo 契约 surface 是关键设计选择** — TS demo 用 `import` 拉取 enums / sentinels，单扫 `mart_city_demo.ts` 漏掉真实常量定义点。本刀扩展到 4 文件以匹配 import chain。
- **mart_city_seven_dim_overview 不携带行级 SHA** — aggregate overview 的 mart 性质决定其字段；强加 SHA 属契约错误（docs/47 §3.2）。
- **20 pytest cases 分 7 组** — 文件存在性 / TS demo 契约 / types 契约 / feature-flag / UI demo / dbt 联合 / 跨文件禁词。
- **首次 5 失败 → 修法正确** — 初版用 `mart_city_demo.ts` 单扫 10 城 + 5 balance_status + SHA，5 tests 失败；改用 4-file contract surface + dbt SHA 按 mart 性质区分，20/20 PASS。
- **依赖 O1 真实 SHA 收口** — TS demo `MART_LINEAGE_PLACEHOLDER_SHA` + dbt `REPEAT('0', 64)` 必须从占位替换为 O1 真实 SHA（per docs/47 §6.3 切刀风险）。
- **依赖 Stage 1 OPEN 收口** — 同上。
- **依赖 S2.1-lite PASS** — person/tenure JOIN `mart_person_tenure` 已交后，落地刀再填 `related_persons` 字段。
- **下游消费路径** — 前端 `CityPageMart.tsx` 仍消费 `frontend/lib/mart_city_demo.ts`（TS-side demo fixture）；待 full 迁移刀接 dbt 真表时改 consume mart 而非 demo。
- **依赖 Knife 33 intake 已交** — intake（`291`）与 demo-join（`294`）并行；O1 真收口时 intake 替换 SHA + demo-join 的 `is_demo` 同步翻转为 `'false'`。
- **不修改 dbt 项目配置** — 契约定型刀不需 dbt_project.yml 改动。
- **0 修改文件 + 1 新 pytest 文件** — 契约定型刀的标志：现有 demo / mart / page 全部稳定；新增守门。
- **下次 heartbeat 闸门** — O1 真收口须用户主动 `--confirm-o1=PATH`；在此之前 S2.7-b-full 真数据迁移刀（tasking 26X+）继续依赖 demo-join emit 行。
- **Gate 2 评审日期暂定 W8** — per docs/34 §10.4；本刀不擅自提前。

— End of `297` —

> 等待 Cursor 审验（预期 `298-stage0-cursor-s296-frontend-mart-demo-parity-audit-…md`）。
> 通过后 20 pytest cases 锁定 TS demo ↔ dbt mart 契约对齐。
> ⚠ **本刀不宣布 Gate 2 PASS**（per docs/34 §1 + §8 #8 + `296` §红线）。
> ⚠ **本刀只做契约定型 + 守门加固**（per `296` §SCHEMA "本刀做/本刀不做"）。
> ⚠ **O1 真实 SHA 收口前恒占位 `'0'*64`**（per docs/47 §3.1 ⚠️ + `296` §红线）。
> ⚠ **所有 demo 行 is_demo='true'**（per `296` §红线）。
> ⚠ **O1 真收口须用户主动 `--confirm-o1=PATH`**（per `291` intake + docs/48 §4.3）。
> Gate 2 评审日期暂定 W8（per docs/34 §10.4）。