# S2.8 — 七维度观察卡 规划 CC 回执

- 编号：`236-stage0-cc-s28-seven-dim-planning-receipt-20260826`
- 日期：2026-08-26
- queue_rev：`92` → CC 执行
- 任务书：`235-stage2-s28-seven-dim-planning-tasking-20260826`
- 前置：`234` S2.6-lite PASS；`docs/34` §4 序 11；`docs/06` §3 七维度定义
- 用户裁定：**D** 缩刀节奏（**只规划**；不写 migration）

---

## §NOW 执行表

| 步 | 项 | 状态 | sha256 摘要 | role |
|---|---|---|---|---|
| 1 | `git pull origin main` + `cc_gate_watch --pull`（queue_rev 92）| ✅ | — | — |
| 2 | 读 `234` PASS + `235` + `docs/34` §4 序 11 + `docs/06` §3 七维度 + `docs/40` §5.1 + `docs/41` §5.1 | ✅ | — | — |
| 3 | 起草 `docs/42-stage2-s28-seven-dim-plan-20260826.md`（10 节，633 行）| ✅ | `3d2fcd73` | documentation |
| 4 | 补 pack（552 → **553**）| ✅ | — | spike_helper |
| 5 | 写回执 `236` 入 `reviews/` | ✅（本文件）| （见 backfill）| documentation |
| 6 | commit → `origin` 优先 → `github` | ⏳ 待推 | — | — |
| 7 | 三路对齐 | ⏳ | — | — |
| 8 | → `84` POLL + `cc_gate_watch` | ⏳ re-arm | — | — |

---

## §1. 交付清单

### 1.1 新文件

| 路径 | 行数 | 大小 | sha256（前 8）| role |
|---|---|---|---|---|
| `docs/42-stage2-s28-seven-dim-plan-20260826.md` | 633 | 31348 | `3d2fcd73` | documentation |
| `reviews/stage0-gate0-rework-2026-08-23/236-stage0-cc-s28-seven-dim-planning-receipt-20260826.md` | （本文件）| （backfill）| （backfill）| documentation |

### 1.2 docs/42 概要（per `235` §NOW 要求 1）

| 章节 | 内容 |
|---|---|
| §1 目标 | S2.8 契约/UI 刀定位（**非表刀**）+ S2.5/2.6/2.7/2.8/2.9 边界 |
| §2 契约 | 七维度卡契约（7 维度 + PRD 8 项映射表）+ mart_seven_dim_overview + EvidenceChain 段接驳 + 反例红色 banner 接驳 + INFERENCE 角标接驳 + 应用层 enum-style 守门 |
| §3 UI 形态 | 七维度卡网格（折叠态）+ 展开态 + React 组件最小形态 + 与 S2.7 EvidenceChain 路由接驳 |
| §4 首批入库策略 | ≤140 cell (20 claim × 7 维度) + polarity 守门 + is_demo 流转 + 稳定 cell 标识 |
| §5 与 S2.7 / S2.9 接驳 | EvidenceChain 段接驳表 + 反例红色 banner 接驳 + **不接 S2.9 对比全量**（红线）|
| §6 验收清单 | 19 项（含 7 维度枚举守门 / balance_status 5 枚举 / 红色 banner / 触发器守门 / pytest ≥5 cases）|
| §7 关键风险与回滚 | 8 项（trigger 守门 / 越界枚举 / 段级与维度级 evidence 不对齐 / 评分字段越界 / S2.9 越界）|
| §8 不做什么 | 16 项红线（含 S2.9 全量 / S2.7 UI 改动 / S2.5 inference_card UI 改动 / 评分字段 / schema ENUM）|
| §9 文档关系 | docs/06 §3/§2.7/§4 L1-L7/§6.6 + docs/04 §3.4/§3.9/§6 + docs/08 §77/§85 + docs/33 §3.2 + docs/34 §1/§4 + docs/40 §5.1 + docs/41 §5.1 + 01-core.sql + migration 012/013 |
| §10 CC 建议 | 8 项决策点供 Cursor 审阅 / 用户裁定（cell 投影策略 / 关联键 / 角标聚合 / NO_EVIDENCE 枚举 / evidence_gaps 来源 / 评分红线 / 落地形态 / 同类区间占位）|

### 1.3 七维度 cell 契约（关键 §2.1 + §2.4）

| card_id | canonical_name_zh | 接驳 EvidenceChain 段 | 反例守门 |
|---|---|---|---|
| `POLICY_DELIVERY` | 政策兑现与政务透明 | COMMITMENT + PROCESS + OUTPUT | balance_status 5 枚举 |
| `FISCAL_EXECUTION` | 财政执行 | COMMITMENT + PROCESS + OUTPUT | 同上 |
| `PROJECT_DELIVERY` | 项目交付 | PROCESS + OUTPUT | 同上 |
| `ECONOMIC_ADAPTATION` | 经济适应 | OUTPUT + OUTCOME | 同上 |
| `PUBLIC_SERVICES` | 公共服务 | OUTPUT + OUTCOME | 同上 |
| `RISK_MANAGEMENT` | 风险管理 | INPUT + OUTPUT | 同上 |
| `GOAL_CONSISTENCY` | 目标一致性 | CONDITION + COMMITMENT + OUTPUT | 同上 |

**balance_status 5 枚举**（per §2.4）：
- `NO_EVIDENCE`（灰，无证据）
- `NO_CONTRADICTING_EVIDENCE`（🔴 红，反例未登记 — Gate 2 §3.2 硬卡）
- `NO_SUPPORTING_EVIDENCE`（🟡 黄，支持缺失）
- `SUPPORTS_DOMINANT`（🟢 绿）
- `CONTRADICTS_DOMINANT`（🟠 橙 — 不评分）

**mart_seven_dim_overview 投影**：每 claim × 7 维度 = 7 cell（笛卡尔积 per §10.1 A）；空 cell = NO_EVIDENCE 灰色。

### 1.4 manifest 变更

| 字段 | 变更前 | 变更后 |
|---|---|---|
| `artifact_count` | 552 | **553** (+1: docs/42) |
| `len(artifacts)` | 552 | **553** |
| `sum(role_count)` | 552 | **553** |
| `documentation` | 55 | **56** |

新增条目：
```json
{
  "path": "docs/42-stage2-s28-seven-dim-plan-20260826.md",
  "size_bytes": 31348,
  "sha256": "3d2fcd73c25f9...",
  "role": "documentation"
}
```

**invariant 守门**：553 == 553 == 553 ✅

---

## §2. 关键决策（per `235` §SCHEMA 钉死 + docs/34 §4 序 11 + docs/06 §3）

| 决策点 | 裁定 | 来源 |
|---|---|---|
| 本刀性质 | **契约/UI 刀**（非表刀）— 七维度是 docs/06 §3 观察维度，不增新 schema | `235` §SCHEMA + docs/06 §3 + docs/34 §4 序 11 |
| 七维度定义 | docs/06 §3 7 项 + PRD 8 项映射表（POLICY_DELIVERY 合并 PRD 政策兑现 + 政务透明）| docs/06 §3 §113-119 |
| 七维度 cell 投影 | 笛卡尔积（每 claim × 7 维度 = 7 cell；空 cell 显示 NO_EVIDENCE）| docs/42 §10.1 A |
| `card_id` 与 `claim_evidence_link` 关联键 | `cel.geo_entity_id` LEFT JOIN | docs/42 §10.2 A |
| INFERENCE / JUDGMENT 角标聚合 | 多角标聚合 "2 INFERENCE / 1 JUDGMENT" | docs/42 §10.3 B + §2.5 |
| balance_status 5 枚举 | 含 NO_EVIDENCE（per docs/42 §2.4）| docs/42 §10.4 A |
| evidence_gaps 来源 | 复用 S2.7 evidence_gaps 段级（per §5.1）| docs/42 §10.5 A |
| `card_id` 落地 | 应用层 enum-style 守门（不引入 schema ENUM）| docs/40 §2.3 + docs/41 §2.3 平行 |
| `mart_seven_dim_overview` 触发器 | 不重新触发 `assert_min_one_contradicts()`（DB trigger 已守门）| docs/41 §2.5 + migration 013 |
| 评分字段 | ❌ **不引入**（per docs/06 §6.6 红线）| docs/42 §10.6 红线 |
| `card_id` 越界（PRD 8 项 vs 框架 7 项）| 框架 7 项是基线；PRDs 8 项映射见 docs/42 §2.1 | docs/06 §113-119 |
| `evidence_audit_trail` 新表 | 不引入（lineage + mart 够用）| docs/41 §2.0 平行 |
| 触发器部署时机 | 既有 migration 013 已部署（per S2.6-lite）；S2.8 不重新部署 | migration 013 + docs/41 §2.5 |
| `uncertainty_record.uncertainty_type` 新增值 | 不引入（七维度 cell 状态变化不走 uncertainty_record；走 lineage.is_demo + mart balance_status）| docs/41 §2.3 平行 |
| 反例超时 | 不在本刀（属 S2.10 Gate 2 评审期）| docs/41 §10.7 |
| S2.9 同类对比全量 | ❌ **不接**（per `235` §SCHEMA 红线；§3.2 同类区间位占位 + 注）| docs/42 §5.3 + §10.8 A |
| S2.7 UI 改动 | ❌ 不接（per `235` §SCHEMA 红线）| docs/42 §8 |
| S2.5 inference_card UI 改动 | ❌ 不接（per `235` §SCHEMA 红线）| docs/42 §8 |
| S2.6 反例登记 UI 改动 | ❌ 不接（per `235` §SCHEMA 红线）| docs/42 §8 |

---

## §3. 红线自检

| 红线 | 状态 |
|---|---|
| ❌ 不宣布 Stage 0 / Gate 1 / Gate 2 PASS | ✅ 仅 docs/42 规划 |
| ❌ 不批量爬政策研究 / 财政预决算 / 官员履历 | ✅ docs/42 §8 + §4 禁爬 |
| ❌ 不做官员评分（"准确率""可靠度""贡献度""维度严重度"）| ✅ docs/42 §10.6 + §8 红线 |
| ❌ 不 HTTP 爬源站 | ✅ |
| ❌ 不降 OCR 门槛 | ✅ 无关 |
| ❌ 不改 1909 / 陕西代表中国 | ✅ 无关 |
| ❌ 不擅自 --force / --force-with-lease | ✅ ff-only pull |
| ❌ 不替用户下裁定 | ✅ §2 列决策；裁定权归 Cursor/用户 |
| ❌ 不在聊天复述 Cursor 长文 | ✅ 仅回执要点 |
| ❌ 不索要 PAT | ✅ |
| ❌ 不改 `gate_thresholds.json` | ✅ 未读未写 |
| ❌ 不碰 `00-CC-CURRENT.md` | ✅ Cursor 拥有 |
| ✅ pack invariant 守门 | ✅ 552 → 553 |
| ✅ 回执 location = `reviews/stage0-gate0-rework-2026-08-23/` | ✅ |
| ✅ docs/42 仅规划；不写 migration | ✅ per `235` §SCHEMA + 用户裁定 D |
| ✅ docs/42 §2.1 不引入 score / rating / rank 字段 | ✅ enum-style TEXT |
| ✅ docs/42 §2.6 应用层 enum-style 守门（不引入 schema ENUM）| ✅ |
| ✅ docs/42 §3.2 同类区间位保留 + 注 "S2.9 范围; 此刀不接" | ✅ per `235` §SCHEMA 红线 |
| ✅ docs/42 §4 首批 ≤140 cell（不爬网）| ✅ |
| ✅ docs/42 §5 仅 §5.1/5.2/5.3 接驳（不接 S2.9 全量）| ✅ per `235` §SCHEMA |
| ✅ docs/42 §8 + §10.6 评分字段全红线 | ✅ |
| ✅ docs/42 §10.7 `card_id` 应用层守门（不引入 schema ENUM）| ✅ per docs/40 §2.3 + docs/41 §2.3 平行 |

---

## §4. 推送 / 三路对齐（待完成）

| 步骤 | 命令 | 结果 |
|---|---|---|
| origin pull | `git fetch origin && git pull --ff-only origin main` | queue_rev 92 ✅ |
| cc_gate_watch | `./scripts/cc_gate_watch.sh --pull` | `CC_ACTION=EXECUTE_NOW` ✅ |
| 本地校验 | `python3 -c "json.load(...)" manifest invariant` | ✅ 553 == 553 == 553 |
| commit | `git add docs/42-stage2-s28-seven-dim-plan-20260826.md evidence_pack/manifest.json && git commit -m "docs(s2): S2.8 七维度观察卡规划（7 维度契约 + mart_seven_dim_overview + 反例/EvidenceChain/INFERENCE 三接驳）"` | ⏳ |
| origin push | `git push origin HEAD`（**priority**）| ⏳ |
| github push | `git push github HEAD`（带 proxy）| ⏳ |
| 三路对齐 | origin/main = github/main = local HEAD | ⏳ |

> **禁止 amend-after-push**：receipt SHA + commit SHA 必须在独立 commit 里 backfill（per knife 2/3/4 经验）。

---

## §5. 下次 heartbeat 预期

- `queue_rev 92` 完成后：Cursor 收 `236` → 下发 `237-stage0-cursor-s28-plan-audit-…md`（PASS/FAIL）
- 若 PASS：进入 S2.8 落地刀（tasking 238+）— dbt `mart_seven_dim_overview` + React `SevenDimGrid` + 首批 ≤140 cell + pytest s28lite
- 若 FAIL：`236-correction` 回合（修 docs/42 + re-commit）
- S2.8 落地可与 S2.1-full 与 S2.2-dbt/seed 与 S2.3/4/5/6 落地可**并行**（不同 schema 域）；等 Cursor 裁定

— End of `236` —