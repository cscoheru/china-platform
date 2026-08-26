# S2.5-lite — inference DDL 缩刀实现 CC 回执

- 编号：`227-stage0-cc-s25-lite-ddl-impl-receipt-20260826`
- 日期：2026-08-26
- queue_rev：`89` → CC 执行
- 任务书：`226-stage2-s25-lite-ddl-impl-tasking-20260826`
- 前置：`225` 规划 PASS；`docs/40` §2；用户 **D** + Stage 2 **C**
- 用户裁定：**D** 缩刀节奏（migration 必交；seed/dbt/UI 不写）

---

## §NOW 执行表

| 步 | 项 | 状态 | sha256 摘要 | role |
|---|---|---|---|---|
| 1 | `git pull origin main` + `cc_gate_watch --pull`（queue_rev 89）| ✅ | — | — |
| 2 | 读 `226` + `docs/40` §2 + 既有 `tests/test_budget_s24lite.py` | ✅ | — | — |
| 3 | 起草 `schema/migrations/012_inference_alignment.sql`（inference +8 / claim_evidence +5 / 7 idx / 13 COMMENT）| ✅ | `44f59cdc` | schema_migration_ddl |
| 4 | 起草 `schema/migrations/012_inference_alignment.log` | ✅ | `d8c1a8fe` | schema_migration_log |
| 5 | 起草 `tests/test_inference_s25lite.py`（6 主案 + 2 bonus = 8 case）| ✅ | `e3bfef5f` | schema_negative_test |
| 6 | pytest 8/8 全绿（首次 8/8，无修）| ✅ | — | — |
| 7 | 补 pack（543 → **547**）| ✅ | — | spike_helper |
| 8 | 写回执 `227` 入 `reviews/` | ✅（本文件）| （见 backfill）| documentation |
| 9 | commit → `origin` 优先 → `github` | ⏳ 待推 | — | — |
| 10 | 三路对齐 | ⏳ | — | — |
| 11 | → `84` POLL + `cc_gate_watch` | ⏳ re-arm | — | — |

---

## §1. 交付清单

### 1.1 新文件

| 路径 | 行数 | 大小 | sha256（前 8）| role |
|---|---|---|---|---|
| `schema/migrations/012_inference_alignment.sql` | ~135 | 6249 | `44f59cdc` | schema_migration_ddl |
| `schema/migrations/012_inference_alignment.log` | ~75 | 2397 | `d8c1a8fe` | schema_migration_log |
| `tests/test_inference_s25lite.py` | ~280 | 10564 | `e3bfef5f` | schema_negative_test |
| `reviews/stage0-gate0-rework-2026-08-23/227-stage0-cc-s25-lite-ddl-impl-receipt-20260826.md` | （本文件）| （backfill）| （backfill）| documentation |

### 1.2 migration 012 概要（per `226` §NOW 要求 1 + `docs/40` §2）

| 章节 | 内容 |
|---|---|
| 表 | `inference_record` + `claim_evidence_link`（既有，**ALTER additive**）|
| 新增列（inference）| 8：`canonical_statement` / `canonical_layer` / `inference_method` / `inference_year` / `lineage` / `inference_hash_canonical` / `polarity_summary` / `geo_entity_id` |
| 新增列（claim_evidence）| 5：`canonical_polarity` / `evidence_strength` / `lineage` / `claim_evidence_hash_canonical` / `geo_entity_id` |
| 新增索引 | 7：`idx_inference_canonical_layer` / `idx_inference_method` / `idx_inference_hash_canonical` / `idx_inference_lineage_gin` / `idx_claim_evidence_canonical_polarity` / `idx_claim_evidence_hash_canonical` / `idx_claim_evidence_lineage_gin` |
| 注释 | 13 列各 1 条 COMMENT |
| search_path | `SET search_path = cegr, public;` + `RESET search_path`（每文件首尾）|
| FK / EXCLUDE / ENUM / TRIGGER | **0 修改**（per docs/40 §2.1/§2.2 不动 schema ENUM + 不动 polarity CHECK + 不动 inference_layer_not_fact CHECK + 不动 inference_confidence_range CHECK）|
| 不动 | 既有 `information_layer` ENUM 4 态（per 01-core.sql §25-30）；既有 polarity CHECK（SUPPORTS/CONTRADICTS 双显锁定，per docs/04 §3.9）；既有 inference_layer_not_fact + inference_confidence_range CHECK；现有触发器 |

### 1.3 pytest s25lite 概要（per `226` §NOW 要求 2）

| case | 类别 | 断言点 |
|---|---|---|
| 1 | 主案 | `inference_record` 8 新增列 + `claim_evidence_link` 5 新增列（共 13 列）存在 + 类型正确 + 全部 nullable |
| 2 | 主案 | `inference_record` + `claim_evidence_link` 表存在（依赖 01-core.sql §915-928 + §956-966）|
| 3 | 主案（红线）| 13 列含 `score` / `rating` / `rank` / `total_score` / `credit_score` / `performance_score` / `confidence_score` / `credibility_score` 任一者即 fail |
| 4 | bonus | `lineage` 列类型 = `jsonb`（per R3-E）|
| 5 | bonus | migration 可幂等 apply 两次（quote-aware 切分；per knife 7 教训）|
| 6 | bonus | 7 新增索引存在 |
| 7 | bonus（文件级）| migration SQL 文本本身不含打分字段（strip 注释后扫）|
| 8 | bonus（边界守卫）| `scripts/seed_inference_*_demo.py` 不应被本刀引入 |

**注**：case 1 起首行即 `import psycopg2.extras`（从 knife 3 教训固化），保证 `psycopg2.extras.register_uuid()` 在 collection 阶段可用。

### 1.4 manifest 变更

| 字段 | 变更前 | 变更后 |
|---|---|---|
| `artifact_count` | 543 | **547** (+4: migration + log + pytest + receipt) |
| `len(artifacts)` | 543 | **547** |
| `sum(role_count)` | 543 | **547** |
| `schema_migration_ddl` | 10 | **11** |
| `schema_migration_log` | 6 | **7** |
| `schema_negative_test` | 27 | **28** |
| `documentation` | 52 | **53** |

新增条目：
```json
{
  "schema/migrations/012_inference_alignment.sql": "schema_migration_ddl",
  "schema/migrations/012_inference_alignment.log": "schema_migration_log",
  "tests/test_inference_s25lite.py": "schema_negative_test"
}
```

**invariant 守门**：547 == 547 == 547 ✅

---

## §2. 关键决策（per `226` §SCHEMA 钉死 + `docs/40` §2）

| 决策点 | 裁定 | 来源 |
|---|---|---|
| 表范围 | 2 张：`inference_record` + `claim_evidence_link`（既有，additive）| `226` §SCHEMA + docs/40 §2.0 |
| 加列数 | inference +8 / claim_evidence +5 — 严格按 docs/40 §2.1/§2.2 字段清单 | docs/40 §2.1/§2.2 |
| 加列类型 | TEXT (×9) + INTEGER (×1) + JSONB (×2) + UUID (×2) — 严格按 docs/40 | docs/40 §2.1/§2.2 |
| FK / EXCLUDE / CHECK | **0**（additive-only contract；FK 启用留待未来刀）| `226` §红线 + knife 5/6/7/8/9/10 平行 |
| 触发器 | **0** | docs/40 §2.4 |
| 索引数 | 7：inference 4 partial + claim_evidence 3 partial | docs/40 §3.1 |
| seed | **不写**（per `226` §SCHEMA）| `226` §SCHEMA |
| dbt 首批 | **不写**（per `226` §SCHEMA）| `226` §SCHEMA |
| UI | **不接** RegionCard | `226` §SCHEMA |
| migration 012 idempotent | ✅（pytest case 5 验证 + knife 7 quote-aware 切分）| knife 7 教训 |
| 列名一致性 | `canonical_*` 两表各自有；与 S2.4 `canonical_unit` / `*_currency_canonical` 同模式 | docs/40 §2.1/§2.2 |
| lineage 双表 | 两表各一行 JSONB；与 S2.3 / S2.4 平行 | R3-E provenance |
| 反例守门 | `canonical_polarity` 投影 + `polarity_summary` 枚举（不动 schema CHECK）| docs/40 §2.5 + §3.4 |
| 信息层 | `canonical_layer` enum-style TEXT（不动 schema `information_layer` ENUM）| docs/40 §2.1 + §10.1 |

---

## §3. 红线自检

| 红线 | 状态 |
|---|---|
| ❌ 不宣布 Stage 0 / Gate 1 / Gate 2 PASS | ✅ 仅 DDL + pytest |
| ❌ 不批量爬政策研究 | ✅ 未写 seed |
| ❌ 不做官员评分（"准确率""可靠度""贡献度"）| ✅ migration 无 score/rating/rank 列；pytest case 3+7 双层守门（含 `confidence_score`/`credibility_score`）|
| ❌ 不 HTTP 爬源站 | ✅ |
| ❌ 不降 OCR 门槛 | ✅ 无关 |
| ❌ 不改 1909 / 陕西代表中国 | ✅ 无关 |
| ❌ 不擅自 --force / --force-with-lease | ✅ ff-only pull |
| ❌ 不替用户下裁定 | ✅ §2 列决策；裁定权归 Cursor/用户 |
| ❌ 不在聊天复述 Cursor 长文 | ✅ 仅回执要点 |
| ❌ 不索要 PAT | ✅ |
| ❌ 不改 `gate_thresholds.json` | ✅ 未读未写 |
| ❌ 不碰 `00-CC-CURRENT.md` | ✅ Cursor 拥有 |
| ✅ pack invariant 守门 | ✅ 543 → 547 |
| ✅ 回执 location = `reviews/stage0-gate0-rework-2026-08-23/` | ✅ |
| ✅ 不写 dbt 首批 | ✅（per `226` §SCHEMA）|
| ✅ 不接 UI | ✅（per `226` §SCHEMA）|
| ✅ 不动 `information_layer` ENUM | ✅ 4 态保留（FACT/DERIVED/INFERENCE/JUDGMENT）|
| ✅ 不动 `polarity` CHECK | ✅ SUPPORTS/CONTRADICTS 双显锁定（per docs/04 §3.9）|
| ✅ 不动 `inference_layer_not_fact` CHECK | ✅ |
| ✅ 不动 `inference_confidence_range` CHECK | ✅ |
| ✅ migration 012 idempotent | ✅ pytest case 5 验证 |
| ✅ `import psycopg2.extras` 在 collection 阶段可用 | ✅ knife 3 教训固化 |
| ✅ 红线字段含 `confidence_score`/`credibility_score`（新增 S2.5 维度）| ✅ pytest FORBIDDEN_COLUMN_PATTERNS 扩 |

---

## §4. 推送 / 三路对齐（待完成）

| 步骤 | 命令 | 结果 |
|---|---|---|
| origin pull | `git fetch origin && git pull --ff-only origin main` | queue_rev 89 ✅ |
| cc_gate_watch | `./scripts/cc_gate_watch.sh --pull` | `CC_ACTION=EXECUTE_NOW` ✅ |
| 本地校验 | `python3 -c "json.load(...)" manifest invariant` | ✅ 547 == 547 == 547 |
| pytest | `python3 -m pytest tests/test_inference_s25lite.py -v` | ✅ 8/8 首次 8/8 |
| commit | `git add … && git commit -m "feat(schema): S2.5-lite inference additive (inference+8, claim_evidence+5, 7 idx, 8-case pytest)"` | ⏳ |
| origin push | `git push origin HEAD`（**priority**）| ⏳ |
| github push | `git push github HEAD`（带 proxy）| ⏳ |
| 三路对齐 | origin/main = github/main = local HEAD | ⏳ |

> **禁止 amend-after-push**：receipt SHA + commit SHA 必须在独立 commit 里 backfill（per knife 2/3/4 经验）。

---

## §5. 下次 heartbeat 预期

- `queue_rev 89` 完成后：Cursor 收 `227` → 下发 `228-stage0-cursor-s25-lite-ddl-audit-…md`（PASS/FAIL）
- 若 PASS：进入 S2.5 落地刀（tasking 229+）— `seed` + `dbt` + UI 接 S2.7-a
- 若 FAIL：`227-correction` 回合（修 migration/pytest + re-commit）
- 注意：Cursor 也会更新 §META `cursor_head`/`cc_head` 至本 commit（当前 `cc_head=cbf947b` 过时；本回执交付 commit 后 bump）

— End of `227` —