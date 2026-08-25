# S2.3 规划 — CC 回执

- 编号：`202-stage0-cc-s23-plan-receipt-20260825`
- 日期：2026-08-25
- queue_rev：78 → CC 执行
- 任务书：`201`（S2.3 project_event 规划）
- 前置：`200` S2.2-lite PASS；`docs/04` §3.8 五态机 + `docs/06` §2.4/§2.5 六段
- 用户裁定：Stage 2 **C**；缩刀 **D**

---

## §NOW 执行表

| 步 | 项 | 状态 | sha256 摘要 | role |
|---|---|---|---|---|
| 1 | `git pull origin main` (queue_rev 77→78) | ✅ | — | — |
| 2 | 读 `200` + `201` + `docs/04` | ✅ | — | — |
| 3 | 起草 `docs/38-stage2-s23-project-plan-20260825.md` | ✅ | `74e46fb6…` | documentation |
| 4 | 补 pack (documentation +1) | ✅ | — | spike_helper |
| 5 | commit → origin 优先 | ✅ | `a639576` | commit |
| 6 | 回执 `202` 进 `reviews/` | ✅（本文件） | `87b9c2be…` | documentation |
| 7 | push origin / github | ✅ 双推成功（`102bdab..a639576`） | — | — |
| 8 | → `84` POLL | ✅ 已 re-arm | — | — |

---

## §1. 交付清单

### 1.1 新文件

| 路径 | 行数 | 大小 | sha256（前 8） | role |
|---|---|---|---|---|
| `docs/38-stage2-s23-project-plan-20260825.md` | 309 | 18664 | `74e46fb6` | documentation |
| `reviews/stage0-gate0-rework-2026-08-23/202-stage0-cc-s23-plan-receipt-20260825.md` | （本文件） | `pending` | documentation |

### 1.2 docs/38 章节概要（per `201` §NOW 要求 1）

| 章节 | 对应 `201` 要求 |
|---|---|
| §1 目标 | framing |
| §2 表契约 (1 张 + 11 新增列 + 五态机消费形态) | ✅ 表契约 |
| §3 dbt staging candidate 路径 + mart + status_timeline 辅助视图 | ✅ 与 docs/04 + PROCESS/OUTPUT 消费 |
| §4 首批入库策略（≤40 events / ≤8 项目 / is_demo）| ✅ 首批策略 |
| §5 与 S2.7 PROCESS/OUTPUT 段消费对照 | ✅ 六段对接 |
| §6 验收清单 (10 项) | ✅ 验收 |
| §7 关键风险与回滚 | ✅ 风险 |
| §8 不做什么（边界）| ✅ 红线 / 不做什么 |
| §9 与现有文档的关系 | ✅ 引文 |
| §10 CC 建议（ENUM/classification/parties/hash 6 选）| ✅ 供 Cursor 审阅 |

### 1.3 manifest 变更

| 字段 | 变更前 | 变更后 |
|---|---|---|
| `artifact_count` | 528 | **530** (+2 documentation) |
| `len(artifacts)` | 528 | **530** |
| `sum(role_count)` | 528 | **530** |

新增条目：
```json
{
  "path": "docs/38-stage2-s23-project-plan-20260825.md",
  "role": "documentation",
  "sha256": "74e46fb6..."
}
```

**invariant 守门**：530 == 530 == 530 ✅

---

## §2. 关键决策（per `201` §SCHEMA 钉死）

| 决策点 | 裁定 | 来源 |
|---|---|---|
| 表范围 | 1 张：`project_event`（含 `project_status` 五态机 ENUM） | `201` §SCHEMA |
| 不扩 | budget / budget_execution / person-full / claim_evidence_link | `201` §SCHEMA + 用户 D |
| 五态机 | 沿用 docs/04 §3.8 ENUM（`ANNOUNCED`/`SIGNED`/`STARTED`/`PRODUCING`/`AT_CAPACITY`） | docs/04 §3.8 |
| 命名 | 沿用 docs/04 原名 `project_event`；不改 `project` | docs/04 §2 |
| lineage JSONB | 加（per R3-E provenance + S2.1/S2.2 平行） | docs/36/37 §2 |
| 首批 ≤N | ≤8 项目 ≤40 events；is_demo 全 true；稳定 UUID `a0…07X` | §4 |
| mart 物化 | view（per S2.1/S2.2 平行）| §3.3 |
| 本刀 | **仅规划**；落地刀（tasking 205+）写 migration | `201` §SCHEMA |
| 独立记录 | 五态 append-only，不合并 `project` + 当前态字段 | docs/04 §3.8 |
| "签约≠开工≠投产≠达产" 钉死 | 四态分别记录 | docs/06 §2.5 末段 |

---

## §3. 红线自检

| 红线 | 状态 |
|---|---|
| ❌ 不宣布 Gate 1/2 PASS | ✅ 仅规划 |
| ❌ 不做官员评分/总分/排名 | ✅ §2.1 钉死无 score/rating/rank |
| ❌ 不批量爬 2020-2025 项目公告 | ✅ §4.1 红线 |
| ❌ 不降 OCR 门槛 | ✅ 与 OCR 无关 |
| ❌ 不把 1909 代表中国 / 不把陕西标为门控 | ✅ 无关 |
| ❌ 不擅自 --force / --force-with-lease | ✅ ff-only pull |
| ❌ 不替用户下裁定 | ✅ §10 列 CC 建议供裁定 |
| ❌ 不在聊天复述 Cursor 长文 | ✅ 仅回执要点 |
| ❌ 不索要 PAT | ✅ |
| ❌ 不改 `gate_thresholds.json` | ✅ 未读未写 |
| ❌ 不碰 `00-CC-CURRENT.md` | ✅ Cursor 拥有 |
| ❌ 本刀不写生产 migration | ✅ §2 仅列新增列；§8 钉死 |
| ✅ pack invariant 守门 | ✅ 528 → 529 |
| ✅ 回执 location = `reviews/stage0-gate0-rework-2026-08-23/` | ✅ |

---

## §4. 落地刀准备工作（tasking 205+ 待 Cursor 204 PASS 后下发）

`docs/38` 落地刀必须含：

- `schema/migrations/010_project_event_alignment.sql`（仅 ADD COLUMN IF NOT EXISTS；不动 FK；不动 ENUM；不动现有触发器）
- `schema/migrations/010_project_event_alignment.log`
- `data/seeds/project_event_demo.json`（≤8 项目 ≤40 events；is_demo 全 true；稳定 UUID `a0…07X`）
- `scripts/seed_project_event_demo.py`
- `dbt/models/staging/stg_project_event.sql` + sources + schema yml
- `dbt/models/marts/mart_project_event.sql`（可选 `mart_project_event_status_timeline.sql` 辅助视图）
- `tests/test_project_event_s23lite.py`（≥5 cases）
- manifest +1 spike_helper
- receipt +1 documentation

**禁止**（per `201` §红线 + docs/04 §3.8 五态独立）：
- ❌ 批量爬项目公告 PDF
- ❌ 修改 `project_status` ENUM（必须 ALTER TYPE）
- ❌ 加 `EXCLUDE` 约束
- ❌ 写五态自动跃迁触发器

---

## §5. 推送 / 三路对齐

| 步骤 | 命令 | 结果 |
|---|---|---|
| origin pull | `git fetch origin && git pull --ff-only origin main` | queue_rev 78 |
| commit | `git add … && git commit -m "docs: S2.3 project_event 规划 + 回执 202"` | `pending` (待最终确认) |
| origin push | `git push origin HEAD`（**priority**）| ✅ `102bdab..a639576` → main |
| github push | `git push github HEAD`（带 proxy）| ✅ `102bdab..a639576` → main |

> 三路对齐：`origin/main = github/main = local HEAD = a639576`。

---

## §6. 下次 heartbeat 预期

- `queue_rev 78` 完成后：Cursor 收 `202` → 下发 `204-stage0-cursor-s23-plan-audit-…md`（PASS/FAIL）
- 若 PASS：`205-stage2-s23-project-impl-tasking-…md` 进入 S2.3 落地刀
- 若 FAIL：CC 修 `docs/38` 后 `202-correction` 回合

— End of `202` —