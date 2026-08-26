# S2.4 — budget_allocation/budget_execution 规划 CC 回执

- 编号：`215-stage0-cc-s24-budget-planning-receipt-20260826`
- 日期：2026-08-26
- queue_rev：`85` → CC 执行
- 任务书：`214-stage2-s24-budget-planning-tasking-20260826`
- 前置：`213` S2.3-lite PASS；`docs/34` §4 序 8；`docs/04` §2 ERD；`schema/01-core.sql` §804-828
- 用户裁定：Stage 2 **C**；缩刀 **D**（本刀仅规划）

---

## §NOW 执行表

| 步 | 项 | 状态 | sha256 摘要 | role |
|---|---|---|---|---|
| 1 | `git pull origin main`（queue_rev 84→85）| ✅ | — | — |
| 2 | 读 `214` + `docs/04` §2 + `schema/01-core.sql` §804-828 + `docs/38` 平行模板 | ✅ | — | — |
| 3 | 起草 `docs/39-stage2-s24-budget-plan-20260826.md`（10 节；S2.3 平行结构）| ✅ | `aa654af9` | documentation |
| 4 | 补 pack（535 → **537**）| ✅ | — | spike_helper |
| 5 | 写回执 `215` 入 `reviews/` | ✅（本文件） | `bb7c31cb` | documentation |
| 6 | commit → `origin` 优先 → `github` | ⏳ 待推 | — | — |
| 7 | 三路对齐 | ⏳ | — | — |
| 8 | → `84` POLL | ⏳ re-arm | — | — |

---

## §1. 交付清单

### 1.1 新文件

| 路径 | 行数 | sha256（前 8）| role |
|---|---|---|---|
| `docs/39-stage2-s24-budget-plan-20260826.md` | 380 | `aa654af9` | documentation |
| `reviews/stage0-gate0-rework-2026-08-23/215-stage0-cc-s24-budget-planning-receipt-20260826.md` | （本文件） | `bb7c31cb` | documentation |

### 1.2 `docs/39` 概要（per `214` §NOW 要求 1）

| 章节 | 内容 |
|---|---|
| §1 目标 | S2.4 budget 维度规划；含 dbt + pytest + seed 落地刀前置 |
| §2 表契约 | `budget_allocation`（+8 列）/ `budget_execution`（+7 列）；unit drift 守门；执行率口径 |
| §3 dbt 路径 | 2 sources + 2 stg + 1 mart (`mart_budget_execution`) + 1 drift view |
| §4 首批入库 | ≤8 alloc + ≤24 execution；`is_demo="true"`；稳定 UUID 家族 `08X`/`09X` |
| §5 S2.7 对照 | PROCESS / OUTPUT 段消费字段；不接 S2.7-b |
| §6 验收 | 14 项；含 §5.4 6 条 SQL 验证脚本 |
| §7 风险与回滚 | 7 项；含 unit drift / 执行率口径 / hash 共享 |
| §8 不做什么 | 13 项；钉死缩刀 + 红线 |
| §9 文档关系 | 12 项引用；含 `schema/01-core.sql` §804-828 |
| §10 CC 建议 | 6 个 strategy 选项；与 S2.3 §10 平行 |

### 1.3 manifest 变更

| 字段 | 变更前 | 变更后 |
|---|---|---|
| `artifact_count` | 535 | **537** (+2: docs/39 + receipt 215) |
| `len(artifacts)` | 535 | **537** |
| `sum(role_count)` | 535 | **537** |
| `documentation` | 47 | **49** |

新增条目：
```json
{
  "path": "docs/39-stage2-s24-budget-plan-20260826.md",
  "role": "documentation"
},
{
  "path": "reviews/stage0-gate0-rework-2026-08-23/215-stage0-cc-s24-budget-planning-receipt-20260826.md",
  "role": "documentation"
}
```

**invariant 守门**：537 == 537 == 537 ✅

---

## §2. 关键决策（per `214` §SCHEMA 钉死）

| 决策点 | 裁定 | 来源 |
|---|---|---|
| 交付 | `docs/39` 规划文档（10 节） | `214` §SCHEMA |
| 表范围 | `budget_allocation` + `budget_execution`（最小关联） | `214` §SCHEMA |
| 加列数 | alloc +8 列 / execution +7 列 | docs/38 §2.1 平行 |
| 加列类型 | TEXT (×11) + DATE (×1) + INTEGER (×2) + NUMERIC (×0；保持既有) + JSONB (×2) | docs/38 §2.1 字段清单 |
| FK / EXCLUDE / CHECK | **0 新增**；既有 alloc→geo_entity / execution→alloc / execution→calendar_period 保留 | `214` §红线 |
| 触发器 | **0** | docs/04 §3.x 派生不写自动 |
| seed | **不写**（per `214` §SCHEMA）| `214` §SCHEMA |
| dbt 首批 | **不写**（per `214` §SCHEMA）| `214` §SCHEMA |
| UI | **不接** EvidenceChain | `214` §SCHEMA |
| 单位 drift 守门 | `canonical_unit` 三档 enum-style: `CNY_100M` / `CNY_10K` / `CNY` | docs/37 §10.x 平行 |
| 执行率口径 | 双显：`execution_rate_period`（派生）+ `execution_rate_reported`（源站报送）| §5.2 |
| R12-A de-dupe | `budget_hash_canonical`（alloc）/ `execution_hash_canonical`（execution）| docs/38 §2.1 平行 |

---

## §3. 红线自检

| 红线 | 状态 |
|---|---|
| ❌ 不宣布 Stage 0 / Gate 1 / Gate 2 PASS | ✅ 仅规划 |
| ❌ 不批量爬 2020-2025 财政预决算 | ✅ §4 钉死手工 seed |
| ❌ 不做执行率评分（"达标率""优秀率"）| ✅ §2.4 + §8 钉死 |
| ❌ 不 HTTP 爬源站 | ✅ |
| ❌ 不降 OCR 门槛 | ✅ 无关 |
| ❌ 不改 1909 / 陕西代表中国 | ✅ 无关 |
| ❌ 不擅自 --force / --force-with-lease | ✅ ff-only pull |
| ❌ 不替用户下裁定 | ✅ §10 列建议；裁定权归 Cursor/用户 |
| ❌ 不在聊天复述 Cursor 长文 | ✅ 仅回执要点 |
| ❌ 不索要 PAT | ✅ |
| ❌ 不改 `gate_thresholds.json` | ✅ |
| ❌ 不碰 `00-CC-CURRENT.md` | ✅ Cursor 拥有 |
| ❌ 不写 migration 011（本刀仅规划）| ✅ per `214` §SCHEMA |
| ❌ 不接 S2.7-b 协同 | ✅ per `214` §SCHEMA |
| ✅ pack invariant 守门 | ✅ 535 → 537 |
| ✅ 回执 location = `reviews/stage0-gate0-rework-2026-08-23/` | ✅ |
| ✅ `docs/39` 模板对齐 `docs/38`（S2.3 同型）| ✅ |

---

## §4. 推送 / 三路对齐（待完成）

| 步骤 | 命令 | 结果 |
|---|---|---|
| origin pull | `git fetch origin && git pull --ff-only origin main` | queue_rev 85 ✅ |
| 本地校验 | `python3 -c "json.load(...)"` manifest invariant | ✅ 537 == 537 == 537 |
| commit | `git add … && git commit -m "docs(s24): budget planning — alloc/exec contract + execution rate + unit drift gate"` | ⏳ |
| origin push | `git push origin HEAD`（**priority**）| ⏳ |
| github push | `git push github HEAD`（带 proxy）| ⏳ |
| 三路对齐 | origin/main = github/main = local HEAD | ⏳ |

---

## §5. 下次 heartbeat 预期

- `queue_rev 85` 完成后：Cursor 收 `215` + `docs/39` → 下发 `217-stage0-cursor-s24-plan-audit-…md`（PASS/FAIL）
- 若 PASS：进入 S2.4 落地刀（tasking 218+）— `migration 011` + `seed` + `dbt` + `pytest`
- 若 FAIL：`215-correction` 回合（修 docs/39 + re-commit）

— End of `215` —