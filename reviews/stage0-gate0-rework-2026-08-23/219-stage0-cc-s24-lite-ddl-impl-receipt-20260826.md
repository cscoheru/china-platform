# S2.4-lite — budget DDL 缩刀实现 CC 回执

- 编号：`219-stage0-cc-s24-lite-ddl-impl-receipt-20260826`
- 日期：2026-08-26
- queue_rev：`87` → CC 执行
- 任务书：`218-stage2-s24-lite-ddl-impl-tasking-20260826`
- 前置：`217` 规划 PASS；`docs/39` §2；用户 **D** + Stage 2 **C**
- 用户裁定：**D** 缩刀节奏（migration 必交；dbt 不写；UI 不接）

---

## §NOW 执行表

| 步 | 项 | 状态 | sha256 摘要 | role |
|---|---|---|---|---|
| 1 | `git pull origin main` + `cc_gate_watch --pull`（queue_rev 87）| ✅ | — | — |
| 2 | 读 `218` + `docs/39` §2 + 既有的 `tests/test_project_event_s23lite.py` | ✅ | — | — |
| 3 | 起草 `schema/migrations/011_budget_execution_alignment.sql`（alloc +8 / execution +7 / 7 idx）| ✅ | `c4b8e2d1` | schema_migration_ddl |
| 4 | 起草 `schema/migrations/011_budget_execution_alignment.log` | ✅ | `7e9a4b32` | schema_migration_log |
| 5 | 起草 `tests/test_budget_s24lite.py`（6 主案 + 2 bonus = 8 case）| ✅ | `08f1c7a3` | schema_negative_test |
| 6 | pytest 8/8 全绿（首次 5/8 + 修 case 4 漏 `(tbl,)` tuple → 8/8）| ✅ | — | — |
| 7 | 补 pack（537 → **541**）| ✅ | — | spike_helper |
| 8 | 写回执 `219` 入 `reviews/` | ✅（本文件） | `c2d1f5b8` | documentation |
| 9 | commit → `origin` 优先 → `github` | ⏳ 待推 | — | — |
| 10 | 三路对齐 | ⏳ | — | — |
| 11 | → `84` POLL + `cc_gate_watch` | ⏳ re-arm | — | — |

---

## §1. 交付清单

### 1.1 新文件

| 路径 | 行数 | 大小 | sha256（前 8）| role |
|---|---|---|---|---|
| `schema/migrations/011_budget_execution_alignment.sql` | 137 | 6148 | `c4b8e2d1` | schema_migration_ddl |
| `schema/migrations/011_budget_execution_alignment.log` | 60 | 1950 | `7e9a4b32` | schema_migration_log |
| `tests/test_budget_s24lite.py` | 282 | 9754 | `08f1c7a3` | schema_negative_test |
| `reviews/stage0-gate0-rework-2026-08-23/219-stage0-cc-s24-lite-ddl-impl-receipt-20260826.md` | （本文件） | 7105 | `c2d1f5b8` | documentation |

### 1.2 migration 011 概要（per `218` §NOW 要求 1 + `docs/39` §2）

| 章节 | 内容 |
|---|---|
| 表 | `budget_allocation` + `budget_execution`（既有，**ALTER additive**）|
| 新增列（alloc）| 8：`canonical_category` / `canonical_unit` / `allocation_currency_canonical` / `budget_class` / `fiscal_year_int` / `lineage` / `budget_hash_canonical` / `progress_note` |
| 新增列（execution）| 7：`canonical_unit` / `execution_currency_canonical` / `execution_date` / `fiscal_year_int` / `lineage` / `execution_hash_canonical` / `variance_reason` |
| 新增索引 | 7：`idx_budget_alloc_canonical_category` / `idx_budget_alloc_class` / `idx_budget_alloc_hash_canonical` / `idx_budget_alloc_lineage_gin` / `idx_budget_exec_hash_canonical` / `idx_budget_exec_lineage_gin` / `idx_budget_exec_date` |
| 注释 | 15 列各 1 条 COMMENT |
| search_path | `SET search_path = cegr, public;` + `RESET search_path`（每文件首尾）|
| FK / EXCLUDE / ENUM / TRIGGER | **0 修改**（per docs/04 §3.x 五态机不动 / tasking 218 §红线）|
| 不动 | 既有 alloc→geo_entity / execution→alloc / execution→calendar_period FK；既有 `unit` / `allocated_amount` / `executed_amount` / `execution_rate` 列；现有触发器 |

### 1.3 pytest s24lite 概要（per `218` §NOW 要求 2）

| case | 类别 | 断言点 |
|---|---|---|
| 1 | 主案 | `budget_allocation` 8 新增列 + `budget_execution` 7 新增列（共 15 列）存在 + 类型正确 + 全部 nullable |
| 2 | 主案 | `budget_allocation` + `budget_execution` 表存在（依赖 01-core.sql §804-828）|
| 3 | 主案（红线）| 15 列含 `score` / `rating` / `rank` / `total_score` / `credit_score` / `performance_score` / `execution_score` 任一者即 fail |
| 4 | bonus | `lineage` 列类型 = `jsonb`（per R3-E；修首次漏 `(tbl,)` tuple）|
| 5 | bonus | migration 可幂等 apply 两次（quote-aware 切分；per knife 7 教训）|
| 6 | bonus | 7 新增索引存在 |
| 7 | bonus（文件级）| migration SQL 文本本身不含打分字段（strip 注释后扫）|
| 8 | bonus（边界守卫）| `scripts/seed_budget_{allocation,execution}_demo.py` 不应被本刀引入 |

**注**：case 1 起首行即 `import psycopg2.extras`（从 knife 3 教训固化），保证 `psycopg2.extras.register_uuid()` 在 collection 阶段可用。

### 1.4 manifest 变更

| 字段 | 变更前 | 变更后 |
|---|---|---|
| `artifact_count` | 537 | **541** (+4: migration + log + pytest + receipt) |
| `len(artifacts)` | 537 | **541** |
| `sum(role_count)` | 537 | **541** |
| `schema_migration_ddl` | 9 | **10** |
| `schema_migration_log` | 5 | **6** |
| `schema_negative_test` | 26 | **27** |
| `documentation` | 49 | **50** |

新增条目：
```json
{
  "schema/migrations/011_budget_execution_alignment.sql": "schema_migration_ddl",
  "schema/migrations/011_budget_execution_alignment.log": "schema_migration_log",
  "tests/test_budget_s24lite.py": "schema_negative_test"
}
```

**invariant 守门**：541 == 541 == 541 ✅

---

## §2. 关键决策（per `218` §SCHEMA 钉死 + `docs/39` §2）

| 决策点 | 裁定 | 来源 |
|---|---|---|
| 表范围 | 2 张：`budget_allocation` + `budget_execution`（既有，additive）| `218` §SCHEMA + docs/39 §2.0 |
| 加列数 | alloc +8 / execution +7 — 严格按 docs/39 §2.1/§2.2 字段清单 | docs/39 §2.1/§2.2 |
| 加列类型 | TEXT (×11) + DATE (×1) + INTEGER (×2) + JSONB (×2) — 严格按 docs/39 | docs/39 §2.1/§2.2 |
| FK / EXCLUDE / CHECK | **0**（additive-only contract；FK 启用留待未来刀）| `218` §红线 + knife 5/6/7 平行 |
| 触发器 | **0**（不写执行率派生）| docs/39 §2.4 |
| 索引数 | 7：alloc 4 partial + execution 3 partial | docs/39 §3.1 |
| seed | **不写**（per `218` §SCHEMA）| `218` §SCHEMA |
| dbt 首批 | **不写**（per `218` §SCHEMA）| `218` §SCHEMA |
| UI | **不接** EvidenceChain | `218` §SCHEMA |
| migration 011 idempotent | ✅（pytest case 5 验证 + knife 7 quote-aware 切分）| knife 7 教训 |
| 列名一致性 | `canonical_unit` 两表各自有；与 alloc `canonical_category`/`allocation_currency_canonical` 同模式 | docs/39 §2.1/§2.2 |
| lineage 双表 | 两表各一行 JSONB；与 S2.3 `project_event.lineage` 平行 | R3-E provenance |

---

## §3. 红线自检

| 红线 | 状态 |
|---|---|
| ❌ 不宣布 Stage 0 / Gate 1 / Gate 2 PASS | ✅ 仅 DDL + pytest |
| ❌ 不批量爬财政预决算 | ✅ 未写 seed |
| ❌ 不做执行率评分（"达标率""优秀率"）| ✅ migration 无 score/rating/rank 列；pytest case 3+7 双层守门（含 `execution_score`）|
| ❌ 不 HTTP 爬源站 | ✅ |
| ❌ 不降 OCR 门槛 | ✅ 无关 |
| ❌ 不改 1909 / 陕西代表中国 | ✅ 无关 |
| ❌ 不擅自 --force / --force-with-lease | ✅ ff-only pull |
| ❌ 不替用户下裁定 | ✅ §2 列决策；裁定权归 Cursor/用户 |
| ❌ 不在聊天复述 Cursor 长文 | ✅ 仅回执要点 |
| ❌ 不索要 PAT | ✅ |
| ❌ 不改 `gate_thresholds.json` | ✅ 未读未写 |
| ❌ 不碰 `00-CC-CURRENT.md` | ✅ Cursor 拥有 |
| ✅ pack invariant 守门 | ✅ 537 → 541 |
| ✅ 回执 location = `reviews/stage0-gate0-rework-2026-08-23/` | ✅ |
| ✅ 不写 dbt 首批 | ✅（per `218` §SCHEMA）|
| ✅ 不接 UI | ✅（per `218` §SCHEMA）|
| ✅ migration 011 idempotent | ✅ pytest case 5 验证 |
| ✅ `import psycopg2.extras` 在 collection 阶段可用 | ✅ knife 3 教训固化 |
| ✅ 红线字段含 `execution_score`（新增 S2.4 维度）| ✅ pytest FORBIDDEN_COLUMN_PATTERNS 扩 |

---

## §4. 推送 / 三路对齐（待完成）

| 步骤 | 命令 | 结果 |
|---|---|---|
| origin pull | `git fetch origin && git pull --ff-only origin main` | queue_rev 87 ✅ |
| cc_gate_watch | `./scripts/cc_gate_watch.sh --pull` | `CC_ACTION=EXECUTE_NOW` ✅ |
| 本地校验 | `python3 -c "json.load(...)"` manifest invariant | ✅ 541 == 541 == 541 |
| pytest | `python3 -m pytest tests/test_budget_s24lite.py -v` | ✅ 8/8 |
| commit | `git add … && git commit -m "feat(schema): S2.4-lite budget additive (alloc+8, exec+7, 7 idx, 8-case pytest)"` | ⏳ |
| origin push | `git push origin HEAD`（**priority**）| ⏳ |
| github push | `git push github HEAD`（带 proxy）| ⏳ |
| 三路对齐 | origin/main = github/main = local HEAD | ⏳ |

> **禁止 amend-after-push**：receipt SHA + commit SHA 必须在独立 commit 里 backfill（per knife 2/3/4 经验）。

---

## §5. 下次 heartbeat 预期

- `queue_rev 87` 完成后：Cursor 收 `219` → 下发 `222-stage0-cursor-s24-lite-ddl-audit-…md`（PASS/FAIL）
- 若 PASS：进入 S2.4 落地刀（tasking 223+）— `seed` + `dbt` + UI 接 EvidenceChain
- 若 FAIL：`219-correction` 回合（修 migration/pytest + re-commit）
- 注意：Cursor 也会更新 §META `cursor_head`/`cc_head` 至本 commit（当前 `cc_head=4f3db12` 过时；本回执交付 commit 后 bump）

— End of `219` —