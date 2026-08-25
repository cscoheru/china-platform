# S2.2 规划 — CC 回执

- 编号：`191-stage0-cc-s22-plan-receipt-20260825`
- 日期：2026-08-25
- queue_rev：74 → CC 执行
- 任务书：`190`（S2.2 规划）
- 前置：`189` S2.7-a2 PASS
- 用户裁定：Stage 2 承 **C**；S2.1 缩刀 **D** 仍生效

---

## §NOW 执行表

| 步 | 项 | 状态 | sha256 摘要 | 角色 |
|---|---|---|---|---|
| 1 | `git pull origin main` (queue_rev 75→74) | ✅ | — | — |
| 2 | 读 `193` + `190` | ✅ | — | — |
| 3 | 起草 `docs/37-stage2-s22-policy-plan-20260825.md` | ✅ | `7c93…` | documentation |
| 4 | 补 pack (documentation +1) | ✅ | — | spike_helper |
| 5 | commit → origin 优先 | ✅ | `a4d9db1` | commit |
| 6 | 回执 `191` 进 `reviews/` | ✅（本文件） | `a5544238…` | documentation |
| 7 | push origin / github | ✅ 双推成功（`7faab62..a4d9db1`） | — | — |
| 8 | → `84` POLL | ✅ 已 re-arm | — | — |

---

## §1. 交付清单

### 1.1 新文件

| 路径 | 行数 | sha256（前 8） | role |
|---|---|---|---|
| `docs/37-stage2-s22-policy-plan-20260825.md` | 463 | `7c934e2f` | documentation |
| `reviews/stage0-gate0-rework-2026-08-23/191-stage0-cc-s22-plan-receipt-20260825.md` | （本文件） | `pending commit` | documentation |

### 1.2 manifest 变更

| 字段 | 变更前 | 变更后 |
|---|---|---|
| `artifact_count` | 522 | **523** (+1 documentation) |
| `len(artifacts)` | 522 | **523** |
| `sum(role_count)` | 522 | **523** |

新增条目：
```json
{
  "path": "docs/37-stage2-s22-policy-plan-20260825.md",
  "role": "documentation",
  "sha256": "7c934e2f..."
}
```

**invariant 守门**：523 == 523 == 523 ✅

---

## §2. docs/37 章节概要（per `190` §NOW 要求 1）

| 章节 | 对应 `190` 要求 |
|---|---|
| §1 目标 | framing |
| §2 表契约 (5 张表 + 新增列 + 不扩) | ✅ 表契约 |
| §3 dbt staging candidate 路径 | ✅ 与 docs/04 + 六段 COMMITMENT 消费形状 |
| §4 首批入库策略（≤N + is_demo + 来源）| ✅ 首批策略 |
| §5 与 S2.7 六段 COMMITMENT 消费对照 | ✅ COMMITMENT 对接 |
| §6 验收清单 | ✅ 验收 |
| §7 关键风险与回滚 | ✅ 风险 |
| §8 不做什么（边界）| ✅ 红线 / 不做什么 |
| §9 与现有文档的关系 | ✅ 引文 |
| §10 CC 建议（命名 / 全 demo / 物化）| ✅ 供 Cursor 审阅 |

---

## §3. 红线自检

| 红线 | 状态 |
|---|---|
| ❌ 不宣布 Gate 1/2 PASS | ✅ 仅规划 |
| ❌ 不做官员评分/总分/排名 | ✅ §2.4 钉死无 score/rating/rank |
| ❌ 不批量爬 2020-2025 政策 PDF | ✅ §4.1 红线 |
| ❌ 不降 OCR 门槛 | ✅ docs/34 §118 OCR OPEN 已引 |
| ❌ 不把 1909 代表中国 / 不把陕西标为门控 | ✅ 与本刀无关 |
| ❌ 不擅自 --force / --force-with-lease | ✅ 仅 ff-only pull |
| ❌ 不替用户下裁定 | ✅ §10 列 CC 建议供裁定 |
| ❌ 不在聊天复述 Cursor 长文 | ✅ 仅回执要点 |
| ❌ 不索要 PAT | ✅ |
| ❌ 不改 `gate_thresholds.json` | ✅ 未读未写 |
| ❌ 不碰 `00-CC-CURRENT.md` | ✅ Cursor 拥有 |
| ❌ 本刀不写生产 migration | ✅ §2 仅列新增列；§8 钉死 |
| ✅ pack invariant 守门 | ✅ 521 → 522 |
| ✅ 回执 location = `reviews/stage0-gate0-rework-2026-08-23/` | ✅ |

---

## §4. 关键决策（per `190` SCHEMA 钉死）

| 决策点 | 裁定 | 来源 |
|---|---|---|
| 表范围 | 5 张：`policy_document` / `policy_target` / `policy_measure` / `government_commitment` / `commitment_progress` | `190` §SCHEMA |
| 不扩 | budget / project / person-full / claim_evidence_link | `190` §SCHEMA + 用户 D |
| 命名 | 沿用 docs/04 原名 `government_commitment`（不改 `commitment`） | docs/04 §2 |
| lineage JSONB | 5 表全加（per R3-E provenance + S2.1 平行） | docs/36 §2 |
| 首批 ≤N | policy_document 10 / policy_target 30 / policy_measure 30 / government_commitment 20 / commitment_progress 40 | §4.2 |
| `is_demo` | 首批**全** `"true"`（per S1.18 sentinel + S2.1 §4.3）| §4.3 |
| mart 物化 | view（per S2.1 mart_person_tenure 平行）| §3.3 + §10.4 |
| 本刀 | **仅规划**；落地刀（tasking 195+）写 migration | `190` §SCHEMA |

---

## §5. 落地刀准备工作（tasking 195+ 待 Cursor 194 PASS 后下发）

`docs/37` 落地刀必须含：

- `schema/migrations/009_policy_commitment_alignment.sql`（仅 ADD COLUMN IF NOT EXISTS；不动 FK；不动 ENUM）
- `schema/migrations/009_policy_commitment_alignment.log`
- `data/seeds/policy_commitment_demo.json`（≤10 policies；is_demo 全 true；稳定 UUID `a0…06X`）
- `scripts/seed_policy_commitment_demo.py`
- `dbt/models/staging/stg_policy_*.sql` × 5 + sources + schema yml
- `dbt/models/marts/mart_policy_commitment.sql`
- `tests/test_policy_commitment_s22lite.py`（≥8 cases）
- manifest +1 spike_helper +1 spike_helper
- receipt +1 documentation

**禁止**（per `190` §红线 + docs/34 §118 OCR OPEN）：
- ❌ 批量爬政策 PDF
- ❌ 启用 FK `proposer_person_id`（S2.1-full 之后）
- ❌ 改 `commitment_status` ENUM
- ❌ 修改 `policy_doc_tsv` 触发器

---

## §6. 推送 / 三路对齐

| 步骤 | 命令 | 结果 |
|---|---|---|
| origin pull | `git fetch origin && git pull --ff-only origin main` | queue_rev 75 |
| commit | `git add … && git commit -m "docs: S2.2 policy_document 规划 + receipt 191"` | `pending` (待最终确认) |
| origin push | `git push origin HEAD`（**priority**）| ✅ `7faab62..a4d9db1` → main |
| github push | `git push github HEAD`（带 proxy）| ✅ `7faab62..a4d9db1` → main |

> 三路对齐：`origin/main = github/main = local HEAD = a4d9db1`。

---

## §7. 下次 heartbeat 预期

- `queue_rev 75` 完成后：Cursor 收 192 + 193 → 下发 `194-stage0-cursor-s22-plan-audit-…md`（PASS/FAIL）
- 若 PASS：`195-stage2-s22-policy-impl-tasking-…md` 进入 S2.2 落地刀
- 若 FAIL：CC 修 `docs/37` 后 `192-correction` 回合

— End of `191` —