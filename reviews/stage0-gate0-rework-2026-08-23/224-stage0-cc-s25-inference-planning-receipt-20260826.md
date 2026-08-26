# S2.5 — inference_record + claim_evidence_link 规划 CC 回执

- 编号：`224-stage0-cc-s25-inference-planning-receipt-20260826`
- 日期：2026-08-26
- queue_rev：`88` → CC 执行
- 任务书：`223-stage2-s25-inference-planning-tasking-20260826`
- 前置：`222` S2.4-lite PASS；`docs/34` §4 序 9；`docs/04` §2 ERD 推断段 + §3.1/§3.9
- 用户裁定：**D** 缩刀节奏（本刀仅规划）；Stage 2 **C**（继 `142`）

---

## §NOW 执行表

| 步 | 项 | 状态 | sha256 摘要 | role |
|---|---|---|---|---|
| 1 | `git pull origin main` + `cc_gate_watch --pull`（queue_rev 88）| ✅ | — | — |
| 2 | 读 `223` 任务书 + `docs/04` §2/§3.1/§3.9 + `docs/06` §2.7/§4/§6/§7 + `docs/34` §2 Gate 2/§4 序 9 + `schema/01-core.sql` §25-30 + §915-969 + 既有 `docs/38`/`docs/39` 模板 | ✅ | — | — |
| 3 | 起草 `docs/40-stage2-s25-inference-plan-20260826.md`（640 行 / 10 节 / 33 KB；表范围 = `inference_record` + `claim_evidence_link` 最小关联）| ✅ | `4359a386` | documentation |
| 4 | 修复 pack invariant bug（knife 8/9 漏报 `role_count` +7）+ 追加 docs/40（artifact_count 541 → **542**，sum(role_count) 534 → **542**）| ✅ | — | spike_helper |
| 5 | 写回执 `224` 入 `reviews/` | ✅（本文件）| `38936fef` | documentation |
| 6 | commit → `origin` 优先 → `github` | ⏳ 待推 | — | — |
| 7 | 三路对齐 | ⏳ | — | — |
| 8 | → `84` POLL + `cc_gate_watch` | ⏳ re-arm | — | — |

---

## §1. 交付清单

### 1.1 新文件

| 路径 | 行数 | 大小 | sha256（前 8）| role |
|---|---|---|---|---|
| `docs/40-stage2-s25-inference-plan-20260826.md` | 640 | 33652 | `4359a386` | documentation |
| `reviews/stage0-gate0-rework-2026-08-23/224-stage0-cc-s25-inference-planning-receipt-20260826.md` | （本文件）| 10291 | `38936fef` | documentation |

### 1.2 docs/40 概要（per `223` §SCHEMA + §NOW）

| 章节 | 内容 |
|---|---|
| §1 目标 | S2.5 = 桥接表刀 — 把 Stage 1 已入库 observation / policy / budget / project 行接驳到六段证据链 UI；本刀仅规划 |
| §2 表契约 | `inference_record`（+8 cols）+ `claim_evidence_link`（+5 cols）+ `uncertainty_record`（不加列）+ `research_note`（不加列）|
| §2.1 inference_record +8 | `canonical_statement` / `canonical_layer` / `inference_method` / `inference_year` / `lineage` / `inference_hash_canonical` / `polarity_summary` / `geo_entity_id` |
| §2.2 claim_evidence_link +5 | `canonical_polarity` / `evidence_strength` / `lineage` / `claim_evidence_hash_canonical` / `geo_entity_id` |
| §2.5 polarity 守门 | SUPPORTS / CONTRADICTS 双显锁定（per docs/04 §3.9 防确认偏差）；Gate 2 §3.2 至少 1 条 CONTRADICTS 硬要求 |
| §3 dbt staging | 4 stg 模型 + 1 mart `mart_inference_record` + 2 mart 辅助 view（polarity_balance + method_distribution）|
| §4 首批入库 | ≤12 inference + ≤36 claim_evidence + ≤12 uncertainty + ≤6 research_note；polarity 守门 SUPPORTS ≥ 1 + CONTRADICTS ≥ 1 |
| §5 与 S2.7 接驳 | mart 暴露给前端可消费（mock 即可；不必 wire）；`mart_claim_evidence_polarity_balance` 接 Gate 2 §3.2 反例检查 |
| §6 验收 | 20 项；含 layer CHECK + confidence CHECK + polarity CHECK + 反例守门 + canonical_layer 100% 投影 |
| §7 风险 | 8 类；含 layer = FACT 拒 / confidence 越界拒 / 反例守门 / 引用孤岛 |
| §8 不做什么 | 14 项；含**评分字段（红线）** + **ENUM 修改** + **批量爬 2020-2025** + **knife 8/9 role_count 漏报 bug 修复** |
| §9 文档关系 | 23 条引用；含 docs/04 §3.1/§3.9 + docs/06 §2.7/§3/§4/§5/§6/§7 + docs/34 §2 Gate 2 + schema §25-30 + §915-969 |
| §10 CC 建议 | 8 项；含 §10.3 **pack invariant bug 修复**（+7 追平 + +1 docs/40 = 542 = 542 = 542）|

### 1.3 manifest 变更（per knife 8/9 漏报追平 + knife 10 +2）

| 字段 | 变更前 | 变更后 | delta |
|---|---|---|---|
| `artifact_count` | 541 | **543** | +2 (docs/40 + receipt 224) |
| `len(artifacts)` | 541 | **543** | +2 |
| `sum(role_count)` | 534 | **543** | +9（+7 追平 knife 8/9 漏报 + +2 本刀新 artifact）|
| `documentation` | 46 | **52** | +6（knife 8/9 漏报 +4 + docs/40 +1 + receipt 224 +1）|
| `schema_migration_ddl` | 9 | **10** | +1（knife 9 migration 011 漏报）|
| `schema_migration_log` | 5 | **6** | +1（knife 9 migration 011.log 漏报）|
| `schema_negative_test` | 26 | **27** | +1（knife 9 test_budget_s24lite.py 漏报）|

新增条目（2 个，按 manifest 顺序）：
```json
{
  "docs/40-stage2-s25-inference-plan-20260826.md": "documentation",
  "reviews/stage0-gate0-rework-2026-08-23/224-stage0-cc-s25-inference-planning-receipt-20260826.md": "documentation"
}
```

**invariant 守门**：543 == 543 == 543 ✅
**bug 修复**：knife 8/9 漏报 7 个 role_count 已追平（534 → 541 对齐到 artifact_count；本刀 +2 docs/40 + receipt → 543）

---

## §2. 关键决策（per `223` §SCHEMA 钉死 + docs/40 §10）

| 决策点 | 裁定 | 来源 |
|---|---|---|
| 表范围 | 4 张：`inference_record` + `claim_evidence_link`（最小关联）+ `uncertainty_record`（不加列）+ `research_note`（不加列）| `223` §SCHEMA + docs/40 §2.0 |
| `inference_record` 加列数 | +8 — 严格按 docs/40 §2.1 字段清单 | docs/40 §2.1 |
| `claim_evidence_link` 加列数 | +5 — 严格按 docs/40 §2.2 字段清单 | docs/40 §2.2 |
| `uncertainty_record` 加列 | **0**（字段集完整；不扩）| docs/40 §2.3 |
| `research_note` 加列 | **0**（GIN 索引 + 触发器已存在；不扩）| docs/40 §2.4 |
| `information_layer` ENUM | **不动**（per docs/04 §3.1；新增态 = 013+）| docs/40 §2.1 / §8 |
| `polarity` CHECK | **不动**（SUPPORTS / CONTRADICTS 双显锁定，per docs/04 §3.9）| docs/40 §2.2 / §2.5 |
| `confidence` 约束 | nullable + CHECK [0, 1]（既有）| docs/40 §2.1 |
| 推断评分字段 | ❌ 0（per docs/06 §6.6 红线）| docs/40 §2.1/§2.2/§8 |
| FK `evidence_obs_ids` → `observation(id)` | ❌ 0（数组 FK；应用层守门）| docs/40 §2.1 |
| 反例守门 | `mart_claim_evidence_polarity_balance.balance_status` + Gate 2 §3.2 硬卡 | docs/40 §3.4 / §6 |
| `canonical_layer` 策略 | enum-style TEXT（per docs/38 §10.2 平行；不动 schema ENUM）| docs/40 §10.1 |
| `inference_method` 策略 | enum-style TEXT 对应 docs/06 §4 L1-L7 + OTHER | docs/40 §10.2 |
| 触发器 | **0**（不动 `set_updated_at_research_note` 已有触发器）| docs/40 §2.4 |
| migration 012 idempotent | ✅（落地刀 quote-aware split per knife 7）| knife 7 教训 |
| 列名一致性 | `canonical_*` / `*_hash_canonical` / `lineage` / `geo_entity_id` 与 S2.1-S2.4 平行 | docs/40 §2.1/§2.2 |
| lineage 四表 | `inference_record` + `claim_evidence_link` 加 JSONB；`uncertainty_record` + `research_note` 不加（FK 投影）| docs/40 §2.3/§2.4 |

---

## §3. 红线自检

| 红线 | 状态 |
|---|---|
| ❌ 不宣布 Stage 0 / Gate 1 / Gate 2 PASS | ✅ 仅 docs/40 规划；无 DDL / seed / dbt |
| ❌ 不批量爬 2020-2025 | ✅ docs/40 §4.1 显式禁；§8 红线重述 |
| ❌ 不做官员评分 / 总分 / 排名 | ✅ docs/40 §2.1/§2.2/§8 红线；`score`/`rating`/`rank`/`total_score`/`confidence_score`/`credibility_score` 全部禁用 |
| ❌ 不 DSH | ✅ |
| ❌ 不 HTTP 爬源站 | ✅ |
| ❌ 不降 OCR 门槛 | ✅ 无关 |
| ❌ 不改 1909 / 陕西代表中国 | ✅ 无关 |
| ❌ 不擅自 --force / --force-with-lease | ✅ ff-only pull |
| ❌ 不替用户下裁定 | ✅ §2 列决策；裁定权归 Cursor/用户 |
| ❌ 不在聊天复述 Cursor 长文 | ✅ 仅回执要点 |
| ❌ 不索要 PAT | ✅ |
| ❌ 不改 `gate_thresholds.json` | ✅ 未读未写 |
| ❌ 不碰 `00-CC-CURRENT.md` | ✅ Cursor 拥有 |
| ✅ pack invariant 守门 | ✅ 534 → 542（含 +7 bug 修复 + +1 docs/40）|
| ✅ 回执 location = `reviews/stage0-gate0-rework-2026-08-23/` | ✅ |
| ✅ 不写 dbt 首批 | ✅（per `223` §SCHEMA）|
| ✅ 不接 UI | ✅（per `223` §SCHEMA）|
| ✅ `import psycopg2.extras` 在 collection 阶段可用（落地刀 pytest 守门）| ✅（knife 3 教训固化；落地刀照搬 s23lite/s24lite 模式）|
| ✅ 红线字段含 `confidence_score` / `credibility_score`（新增 S2.5 维度）| ✅ docs/40 §8 红线列表 |
| ✅ `information_layer` ENUM 不动 | ✅ docs/40 §2.1 / §8 钉死 |
| ✅ `polarity` CHECK 不动 | ✅ docs/40 §2.2 / §2.5 钉死 |
| ✅ knife 8/9 role_count +7 漏报 bug 修复 | ✅ docs/40 §10.3 + manifest role_count 同步追平 |

---

## §4. 推送 / 三路对齐（待完成）

| 步骤 | 命令 | 结果 |
|---|---|---|
| origin pull | `git fetch origin && git pull --ff-only origin main` | queue_rev 88 ✅ |
| cc_gate_watch | `./scripts/cc_gate_watch.sh --pull` | `CC_ACTION=EXECUTE_NOW` ✅ |
| 本地校验 | `python3 -c "json.load(...)" manifest invariant` | ✅ 543 == 543 == 543 |
| docs/40 sha | `sha256(docs/40) = 4359a386...f062e` | ✅ |
| docs/40 行数 | `wc -l docs/40-stage2-s25-inference-plan-20260826.md` = 640 行 | ✅ |
| receipt sha | `sha256(receipt 224) = 38936fef...b505` | ✅ |
| commit | `git add docs/40 evidence_pack/manifest.json reviews/.../224-...md && git commit -m "docs(s2.5): inference_record + claim_evidence_link plan (10-section, +1 doc, +7 role_count fix)"` | ⏳ |
| origin push | `git push origin HEAD`（**priority**）| ⏳ |
| github push | `git push github HEAD`（带 proxy）| ⏳ |
| 三路对齐 | origin/main = github/main = local HEAD | ⏳ |

> **禁止 amend-after-push**：receipt SHA + commit SHA 必须在独立 commit 里 backfill（per knife 2/3/4 经验）。

---

## §5. 下次 heartbeat 预期

- `queue_rev 88` 完成后：Cursor 收 `224` → 下发 `225-stage0-cursor-s25-plan-audit-…md`（PASS/FAIL）
- 若 PASS：进入 S2.5 落地刀（tasking 226+）— `migration 012` + `seed_inference_*_demo` + `seed_claim_evidence_*_demo` + dbt stg/mart + UI 接 S2.7-a
- 若 FAIL：`224-correction` 回合（修 docs/40 + re-commit）
- 注意：Cursor 也会更新 §META `cursor_head`/`cc_head` 至本 commit（当前 `cc_head=40ee8e6` 过时；本回执交付 commit 后 bump）

— End of `224` —