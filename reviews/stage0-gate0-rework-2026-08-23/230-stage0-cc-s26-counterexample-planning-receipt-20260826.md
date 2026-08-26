# S2.6 — 反例登记 (counterexample) 规划 CC 回执

- 编号：`230-stage0-cc-s26-counterexample-planning-receipt-20260826`
- 日期：2026-08-26
- queue_rev：`90` → CC 执行
- 任务书：`229-stage2-s26-counterexample-planning-tasking-20260826`
- 前置：`227` S2.5-lite DDL PASS；`docs/40` §2.5 / §3.4 / §10.6 反例守门 + mart 规划；`docs/34` §2 Gate 2 §3.2 反例硬要求；`docs/04` §3.9 polarity 双显锁定
- 用户裁定：**D** 缩刀节奏（**只规划**；不写 migration）

---

## §NOW 执行表

| 步 | 项 | 状态 | sha256 摘要 | role |
|---|---|---|---|---|
| 1 | `git pull origin main` + `cc_gate_watch --pull`（queue_rev 90）| ✅ | — | — |
| 2 | 读 `229` + `docs/34` §2 + `docs/40` §2.5/§3.4 + `docs/04` §3.9 + `docs/06` §6.6 | ✅ | — | — |
| 3 | 起草 `docs/41-stage2-s26-counterexample-plan-20260826.md`（10 节，506 行）| ✅ | `dfb1aac7` | documentation |
| 4 | 补 pack（547 → **548**）| ✅ | — | spike_helper |
| 5 | 写回执 `230` 入 `reviews/` | ✅（本文件）| （见 backfill）| documentation |
| 6 | commit → `origin` 优先 → `github` | ⏳ 待推 | — | — |
| 7 | 三路对齐 | ⏳ | — | — |
| 8 | → `84` POLL + `cc_gate_watch` | ⏳ re-arm | — | — |

---

## §1. 交付清单

### 1.1 新文件

| 路径 | 行数 | 大小 | sha256（前 8）| role |
|---|---|---|---|---|
| `docs/41-stage2-s26-counterexample-plan-20260826.md` | 506 | 26068 | `dfb1aac7` | documentation |
| `reviews/stage0-gate0-rework-2026-08-23/230-stage0-cc-s26-counterexample-planning-receipt-20260826.md` | （本文件）| （backfill）| （backfill）| documentation |

### 1.2 docs/41 概要（per `229` §NOW 要求 1）

| 章节 | 内容 |
|---|---|
| §1 目标 | S2.6 流程刀定位（**非表刀**）+ S2.5/2.6 边界 |
| §2 契约 | workflow 5 阶段 + claim_evidence_link 消费形态 + uncertainty_record 中间态 + 反例守门三态 + 应用层守门函数 |
| §3 UI 最小形态 | admin 反例登记表单 + 列表 + 红色 banner 接驳 + reviewer 审核界面 |
| §4 首批入库策略 | ≤20 反例登记（INFERENCE ×6 + POLICY ×4 + BUDGET ×4 + PROJECT ×3 + PERSON ×3）|
| §5 与 S2.7 / S2.8 接驳 | mart_claim_evidence_polarity_balance → RegionCard 红色 banner + mart_counterexample_overview |
| §6 验收清单 | 17 项（含反例守门触发器 + lineage is_demo 流转 + pytest ≥5 cases）|
| §7 关键风险与回滚 | 7 项（DB 写权限 / reviewer 缺位 / is_demo 流转被绕过 / 性能 / 一致性）|
| §8 不做什么 | 15 项红线（含 Gate 2 §3.2 全量 UI 验收 / S2.8 全量接驳 / 评分字段 / 跨行 CHECK）|
| §9 文档关系 | docs/04 §3.4/§3.9/§6 + docs/06 §6/§6.6 + docs/34 §2/§4 + docs/40 §2.5/§3.4/§10.6 + 01-core.sql §932-940/§956-969 + migration 012 |
| §10 CC 建议 | 8 项决策点供 Cursor 审阅 / 用户裁定（含 workflow 5 阶段 / reviewer 角色 / CONTRADICTS 最少 1 / lineage 流转 / 触发器时机 / uncertainty_type / auto-reject timeout / 评分红线）|

### 1.3 反例守门契约（关键 §2.4 + §2.5）

| mart 列 | 枚举 | 触发 | UI |
|---|---|---|---|
| `balance_status = NO_CONTRADICTING_EVIDENCE` | 红色 banner | `COUNT(CONTRADICTS) = 0` | **Gate 2 §3.2 硬卡** |
| `NO_SUPPORTING_EVIDENCE` | 黄色 banner | `COUNT(SUPPORTS) = 0` | 评审层 catch |
| `SUPPORTS_DOMINANT` | 绿色 | SUPPORTS ≥ CONTRADICTS | "支持证据占优" |
| `CONTRADICTS_DOMINANT` | 橙色 | CONTRADICTS > SUPPORTS | "反例占优" — 不评分 |

**触发器函数 `assert_min_one_contradicts()`**（per §2.5）：
- AFTER INSERT OR UPDATE OR DELETE ON claim_evidence_link
- 若该 claim_id 删后 `COUNT(CONTRADICTS) = 0` → `RAISE EXCEPTION 'gate 2 §3.2 violation'`
- ❌ **不引入**跨行 CHECK 约束（PostgreSQL 不支持 subquery CHECK）
- ✅ 触发器 + 应用层 wrapper 三重守门

### 1.4 manifest 变更

| 字段 | 变更前 | 变更后 |
|---|---|---|
| `artifact_count` | 547 | **548** (+1: docs/41) |
| `len(artifacts)` | 547 | **548** |
| `sum(role_count)` | 547 | **548** |
| `documentation` | 53 | **54** |

新增条目：
```json
{
  "path": "docs/41-stage2-s26-counterexample-plan-20260826.md",
  "size_bytes": 26068,
  "sha256": "dfb1aac78d36296dd7f1adca89ed72d1b15af09331fa4fcc6ce55f3fd1894a9d",
  "role": "documentation"
}
```

**invariant 守门**：548 == 548 == 548 ✅

---

## §2. 关键决策（per `229` §SCHEMA 钉死 + docs/40 §2 + docs/34 §2）

| 决策点 | 裁定 | 来源 |
|---|---|---|
| 本刀性质 | **流程刀**（非表刀）— `claim_evidence_link` 既有 + `uncertainty_record` 既有 | `229` §SCHEMA + docs/41 §1 |
| 反例守门表层 | `mart_claim_evidence_polarity_balance` 视图（per docs/40 §3.4 已规划）| docs/40 §3.4 |
| 反例守门 DB 层 | `assert_min_one_contradicts()` 触发器函数（落地刀部署）| docs/41 §2.5 |
| 反例守门应用层 | admin UI 提交时前置校验 + reviewer 审核二次校验 | docs/41 §3 |
| workflow 阶段 | 5 阶段（DRAFT → PENDING_REVIEW → APPROVED → PUBLISHED + REJECTED/WITHDRAWN/ARCHIVED 终态）| docs/41 §2.1 |
| reviewer 角色 | admin role 可独立 APPROVE/REJECT（沿用现有 admin_upload 模式）| docs/41 §10.2 |
| 每 claim 最少 CONTRADICTS | ≥1（per Gate 2 §3.2 硬要求）| docs/41 §2.2 + §4.2 |
| `lineage.is_demo` 流转 | DRAFT/PENDING/REJECTED/WITHDRAWN → `"true"`；APPROVED/PUBLISHED → `"false"` | docs/41 §4.3 |
| 触发器部署时机 | AFTER INSERT OR UPDATE OR DELETE（落地刀）| docs/41 §10.5 |
| `uncertainty_record.uncertainty_type` 新增值 | 应用层 enum-style 守门（不引入 schema ENUM）| docs/41 §2.3 + §10.6 |
| reviewer auto-reject timeout | 30 天（属 S2.10 Gate 2 评审期；非本刀）| docs/41 §10.7 |
| 评分字段 | ❌ **不引入**（per docs/06 §6.6 红线）| docs/41 §10.8 |
| 评分字段含义 | 反例严重度 / 可信度 / 反驳力 — 全部 ❌ 红线 | docs/41 §8 |
| 跨行 CHECK 约束 | ❌ 不引入（PostgreSQL 不支持 subquery CHECK）| docs/41 §2.5 |
| `evidence_audit_trail` 新表 | 推迟（lineage 字段够用）| docs/41 §2.0 |
| Gate 2 §3.2 全量 UI 验收 | ❌ 不接（属 S2.10 Gate 2 评审刀）| docs/41 §5.3 |
| S2.8 七维度观察卡全量 | ❌ 不接（仅 §5.1 红色 banner 接驳）| docs/41 §5 |

---

## §3. 红线自检

| 红线 | 状态 |
|---|---|
| ❌ 不宣布 Stage 0 / Gate 1 / Gate 2 PASS | ✅ 仅 docs/41 规划 |
| ❌ 不批量爬政策研究 / 财政预决算 / 官员履历 | ✅ docs/41 §8 + §4 禁爬 |
| ❌ 不做官员评分（"准确率""可靠度""贡献度""反例严重度"）| ✅ docs/41 §10.8 红线 |
| ❌ 不 HTTP 爬源站 | ✅ |
| ❌ 不降 OCR 门槛 | ✅ 无关 |
| ❌ 不改 1909 / 陕西代表中国 | ✅ 无关 |
| ❌ 不擅自 --force / --force-with-lease | ✅ ff-only pull |
| ❌ 不替用户下裁定 | ✅ §2 列决策；裁定权归 Cursor/用户 |
| ❌ 不在聊天复述 Cursor 长文 | ✅ 仅回执要点 |
| ❌ 不索要 PAT | ✅ |
| ❌ 不改 `gate_thresholds.json` | ✅ 未读未写 |
| ❌ 不碰 `00-CC-CURRENT.md` | ✅ Cursor 拥有 |
| ✅ pack invariant 守门 | ✅ 547 → 548 |
| ✅ 回执 location = `reviews/stage0-gate0-rework-2026-08-23/` | ✅ |
| ✅ docs/41 仅规划；不写 migration | ✅ per `229` §SCHEMA + 用户裁定 D |
| ✅ docs/41 §2.1/§2.2/§2.3/§2.4/§2.5 不动 `polarity` CHECK | ✅ SUPPORTS/CONTRADICTS 锁定（per docs/04 §3.9）|
| ✅ docs/41 §2.1 不引入 `score` / `rating` / `rank` 字段 | ✅ enum-style TEXT |
| ✅ docs/41 §2.5 用触发器 + 应用层守门（不用跨行 CHECK）| ✅ PostgreSQL 不支持 |
| ✅ docs/41 §4 首批 ≤20 行（不爬网）| ✅ |
| ✅ docs/41 §5 仅 §5.1 红色 banner 接驳（不接 S2.8 全量）| ✅ per `229` §SCHEMA |
| ✅ docs/41 §8 + §10.8 评分字段全红线 | ✅ |

---

## §4. 推送 / 三路对齐（待完成）

| 步骤 | 命令 | 结果 |
|---|---|---|
| origin pull | `git fetch origin && git pull --ff-only origin main` | queue_rev 90 ✅ |
| cc_gate_watch | `./scripts/cc_gate_watch.sh --pull` | `CC_ACTION=EXECUTE_NOW` ✅ |
| 本地校验 | `python3 -c "json.load(...)" manifest invariant` | ✅ 548 == 548 == 548 |
| commit | `git add docs/41-stage2-s26-counterexample-plan-20260826.md evidence_pack/manifest.json && git commit -m "docs(s2): S2.6 反例登记规划（claim_evidence_link 消费形态 + 反例守门三态 + 触发器部署时机）"` | ⏳ |
| origin push | `git push origin HEAD`（**priority**）| ⏳ |
| github push | `git push github HEAD`（带 proxy）| ⏳ |
| 三路对齐 | origin/main = github/main = local HEAD | ⏳ |

> **禁止 amend-after-push**：receipt SHA + commit SHA 必须在独立 commit 里 backfill（per knife 2/3/4 经验）。

---

## §5. 下次 heartbeat 预期

- `queue_rev 90` 完成后：Cursor 收 `230` → 下发 `231-stage0-cursor-s26-plan-audit-…md`（PASS/FAIL）
- 若 PASS：进入 S2.6 落地刀（tasking 232+）— 触发器 `assert_min_one_contradicts()` + dbt mart + admin UI + pytest
- 若 FAIL：`230-correction` 回合（修 docs/41 + re-commit）
- S2.6 落地可与 S2.1-full 与 S2.2-dbt/seed 与 S2.3/4/5 落地可**并行**（不同 schema 域）；等 Cursor 裁定

— End of `230` —