# S2.10 Gate 2 评审包 规划 CC 回执

- 编号：`248-stage0-cc-s210-gate2-package-planning-receipt-20260826`
- 日期：2026-08-26
- queue_rev：`96` → CC 执行
- 任务书：`247-stage2-s210-gate2-package-planning-tasking-20260826`
- 前置：`246` S2.9-lite PASS（无 OPEN）；`docs/08` §3.2（Gate 2 7 条）；`docs/10` §3.1-3.5；`docs/34` §2+§3

---

## §NOW 执行表

| 步 | 项 | 状态 | sha256 摘要 | role |
|---|---|---|---|---|
| 1 | `git pull origin main` + `cc_gate_watch --pull`（queue_rev 96）| ✅ | — | — |
| 2 | 读 `246` PASS（无 OPEN）+ `247` + `docs/08 §3.2` + `docs/10 §3.1-3.5` + `docs/34 §2/§3` | ✅ | — | — |
| 3 | 起草 **`docs/44-stage2-s210-gate2-package-plan-20260826.md`**（492 行；11 节）| ✅ | `2a34e089` | documentation |
| 4 | smoke-check 仍 PASS（无 frontend 改动）| ✅ | — | — |
| 5 | 文件级 forbidden-token guard（docs/44 CLEAN）| ✅ | — | — |
| 6 | 跨 lite 回归（s21lite..s26lite = **42/42**）| ✅ | — | — |
| 7 | 补 pack（566 → **568**；含 docs/44 + receipt 248）| ✅ | — | documentation |
| 8 | 写回执 `248` 入 `reviews/` | ✅（本文件）| （见 backfill）| documentation |
| 9 | commit → `origin` 优先 → `github` | ⏳ 待推 | — | — |
| 10 | 三路对齐 | ⏳ | — | — |
| 11 | → `84` POLL + `cc_gate_watch` | ⏳ re-arm | — | — |

---

## §1. 交付清单

### 1.1 新文件

| 路径 | 行数 | 大小 | sha256（前 8）| role |
|---|---|---|---|---|
| `docs/44-stage2-s210-gate2-package-plan-20260826.md` | **492** | （backfill）| `2a34e089` | documentation |
| `reviews/stage0-gate0-rework-2026-08-23/248-stage0-cc-s210-gate2-package-planning-receipt-20260826.md` | （本文件）| （backfill）| （backfill）| documentation |

### 1.2 docs/44 章节结构（11 节）

| § | 主题 | 来源 |
|---|---|---|
| §1 | 目标 + S2.10 与前置刀关系 + Gate 2 红线 | per `247` §SCHEMA + docs/08 §3.2 + docs/34 §1+§8+§10.4 + `247` §红线 |
| §2 | **Gate 2 验收 7 条 ↔ Stage 2 各刀映射表** | per docs/08 §3.2 + docs/34 §2 严格继承 |
| §3 | **docs/10 §3.1-3.5 方法层测试映射**（5 测试覆盖度）| per docs/10 §127-186 |
| §4 | **Stage 1 OPEN 继承清单**（7 项：O1-O7）| per docs/34 §3 必填依赖 + 显式携带 |
| §5 | Gate 2 演示场景（5 省 + 10 地市 + 6 段 + 7 维度）| per docs/08 §3.2 验收项 #1-#3 |
| §6 | 演示级 vs 不可降级 vs 仍 OPEN 守门表 | per docs/34 §2 "唯一不可降级" |
| §7 | **Gate 2 评审脚本清单**（pytest + smoke-check + dbt + DB schema + manifest + 演示）| per `247` §NOW |
| §8 | 关键风险与回滚（10 项）| per docs/42 §7 平行 + docs/34 §OPEN |
| §9 | 不做什么（22 项红线）| per docs/42 §8 平行 + docs/34 §8 #8 + §10.4 |
| §10 | 与现有文档的关系（22 引用）| per docs/42 §9 平行 |
| §11 | CC 建议（6 选项）| per docs/42 §10 平行 |

### 1.3 manifest 变更

| 字段 | 变更前 | 变更后 |
|---|---|---|
| `artifact_count` | 566 | **568** (+2: docs/44 + receipt 248) |
| `len(artifacts)` | 566 | **568** |
| `sum(role_count)` | 566 | **568**（bump script 重新从 artifacts 计算 source-of-truth）|

**invariant 守门**：568 == 568 == 568 ✅

**注**：knife 16 bug 修复后，本刀沿用 source-of-truth 模式，role_count 字段自动从 artifacts 列表重新计算，避免再次漂移。

---

## §2. 关键决策（per `247` §SCHEMA 钉死 + docs/08 §3.2 + docs/34 §2/§3）

| 决策点 | 裁定 | 来源 |
|---|---|---|
| 本刀性质 | **规划刀** — 仅 `docs/44`；无 migration / 无 dbt / 无 pytest | `247` §SCHEMA + 用户裁定 D |
| ❌ 宣布 Gate 2 PASS | 红线（per docs/34 §1 状态 + §8 #8 + §133 + `247` §红线）| 多重红线 |
| ❌ 伪造 SHA / 伪造证据 | 红线 | `247` §红线 |
| ❌ 真实 SHA-locked 江苏样本（O1） | **仍 OPEN** — Gate 2 评审包必带 | docs/34 §3 必填依赖 |
| ❌ OCR 生产路径（O3） | **仍 OPEN** — NBS 数字演示可过 | docs/34 §3 |
| ❌ 真实联外探针（O2） | 演示级可过 | docs/34 §3 |
| Gate 2 评审日期 | 暂定 W8（不擅自提前）| docs/34 §10.4 |
| Gate 2 演示数据策略 | 仅 mock（per docs/34 §141 "不要求真实 SHA 样本"）| docs/34 §8 + §11.2 |
| docs/10 §3.2-3.4 测试落地方案 | pytest stub + xfail 显式声明 "Stage 3 收口" | docs/08 §3.2 #7 + §11.3 |
| 不可降级验收项 | 仅六段证据链 UI（验收项 #2 — S2.7）| docs/34 §2 "唯一不可降级" |
| 演示级可过 | 5 省页面（#1）/ 七维度观察卡（#3）| docs/34 §2 |
| 已守门 | 官员能力总分（#4）| smoke-check + forbidden-token guard |
| 已交 | INFERENCE/JUDGMENT 角标（#5）| migration 012 + types |
| 已交 | 反例登记 trigger（#6）| migration 013 + docs/41 |
| 部分已交 | docs/10 §3.1-3.5（#7）| 3.1 + 3.5 已交；3.2-3.4 stub |
| 10 地市 | 待 tasking 249+ 用户/Cursor 裁定；本刀仅列候选 per §5.1.3 | docs/34 §10.4 + §11.6 |
| Gate 2 PASS 守门 | receipt 严禁 "Gate 2 PASS" 字样 + Cursor 审验把关 | docs/34 §8 #8 + §133 + `247` §红线 |

---

## §3. 红线自检

| 红线 | 状态 |
|---|---|
| ❌ 不宣布 Gate 1 / Gate 2 PASS | ✅ §1.2 + §2 + §11.5 多次显式守门；receipt 248 严禁 "Gate 2 PASS" 字样 |
| ❌ 不批量爬政策研究 / 财政预决算 / 官员履历 | ✅ 仅规划 |
| ❌ 不做官员评分（"准确率""可靠度""贡献度""维度严重度"）| ✅ §8 + docs/06 §6.6 + docs/41 §10.8 + docs/42 §10.6 + docs/43 §10.6 红线条目 |
| ❌ 不 HTTP 爬源站 | ✅ |
| ❌ 不降 OCR 门槛 | ✅ 无关 |
| ❌ 不改 1909 / 陕西代表中国 | ✅ 无关 |
| ❌ 不擅自 --force / --force-with-lease | ✅ ff-only pull |
| ❌ 不替用户下裁定 | ✅ §11 列决策；裁定权归 Cursor/用户 |
| ❌ 不在聊天复述 Cursor 长文 | ✅ 仅回执要点 |
| ❌ 不索要 PAT | ✅ |
| ❌ 不改 `gate_thresholds.json` | ✅ 未读未写 |
| ❌ 不碰 `00-CC-CURRENT.md` | ✅ Cursor 拥有 |
| ✅ pack invariant 守门 | ✅ 566 → 568；bump script source-of-truth |
| ✅ 回执 location = `reviews/stage0-gate0-rework-2026-08-23/` | ✅ |
| ✅ 不写 dbt mart | ✅（per `247` §SCHEMA）|
| ✅ 不写 migration | ✅（per `247` §SCHEMA）|
| ✅ 不写 pytest case | ✅（per `247` §SCHEMA + 落地刀 tasking 249+ 范围）|
| ✅ 不接全国实时排名 | ✅（per docs/34 §4.3）|
| ✅ 不擅自提前 Gate 2 评审日期 | ✅ W8（per docs/34 §10.4）|
| ✅ 必带 O1 + O3 OPEN 清单（per docs/34 §3）| ✅ §4 + §11.4 显式守门 |
| ✅ 不引入 score / rating / rank 字段 | ✅ §9 红线条目 |
| ✅ 不引入 schema ENUM | ✅ 应用层 enum-style 守门 |
| ✅ 不动 `polarity` CHECK | ✅ 无关 |
| ✅ 不动 `information_layer` ENUM | ✅ 无关 |
| ✅ 不引入跨行 CHECK 约束 | ✅ trigger + 应用层守门 |
| ✅ 跨 lite 回归 s21lite..s26lite = 42/42 | ✅ |
| ✅ smoke-check 仍 PASS | ✅ |
| ✅ docs/44 文件级 forbidden-token guard CLEAN | ✅ |

---

## §4. 推送 / 三路对齐（待完成）

| 步骤 | 命令 | 结果 |
|---|---|---|
| origin pull | `git fetch origin && git pull --ff-only origin main` | queue_rev 96 ✅ |
| cc_gate_watch | `./scripts/cc_gate_watch.sh --pull` | `CC_ACTION=EXECUTE_NOW` ✅ |
| docs/44 起草 | 492 行 / sha `2a34e089` | ✅ |
| docs/44 file-level guard | 扫描 forbidden tokens | ✅ CLEAN |
| 本地校验 | `python3 -c "json.load(...)" manifest invariant` | ✅ 568 == 568 == 568 |
| smoke-check | `python3 frontend/smoke-check.py` | ✅ PASS（无 frontend 改动）|
| pytest 跨 lite | `python3 -m pytest tests/test_*_s*lite.py -q` | ✅ 42/42 |
| commit | `git add docs/44-stage2-s210-gate2-package-plan-20260826.md evidence_pack/manifest.json reviews/.../248-...md && git commit -m "feat(docs): S2.10 Gate 2 评审包规划 (7 条验收 + Stage 1 OPEN 显式携带; 不宣布 PASS)"` | ⏳ |
| origin push | `git push origin HEAD`（**priority**）| ⏳ |
| github push | `git push github HEAD`（带 proxy）| ⏳ |
| 三路对齐 | origin/main = github/main = local HEAD | ⏳ |

> **禁止 amend-after-push**：receipt SHA + commit SHA 必须在独立 commit 里 backfill（per knife 2/3/4 经验）。

---

## §5. 下次 heartbeat 预期

- `queue_rev 96` 完成后：Cursor 收 `248` → 下发 `249-stage0-cursor-s210-plan-audit-…md`（PASS/FAIL）
- 若 PASS：进入 S2.10 落地刀（tasking 250+）— pytest 3.1/3.5 case + 3.2-3.4 stub + Gate 2 评审包封面
- 若 FAIL：`248-correction` 回合（修 docs/44 + re-commit）

---

## §6. 备注

- **本刀不宣布 Gate 2 PASS** — 这是 S2.10 最重要的红线。Gate 2 评审日期暂定 W8（per docs/34 §10.4），由 Cursor/用户裁定，不擅自提前。
- **Stage 1 OPEN 显式携带** — O1（真实 SHA）+ O3（OCR）是必带项；Gate 2 评审包必列 OPEN 清单 + 收口时间表，不允许假装已过。
- **docs/10 §3.2-3.4 测试仅 stub** — 这些测试属 Stage 3 L4+ 范围；Gate 2 评审仅要求测试**存在**（pytest xfail 占位），不要求实际 L4+ 分析跑通。

— End of `248` —