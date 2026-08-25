# S2.3-lite — project_event DDL 缩刀实现 CC 回执

- 编号：`205-stage0-cc-s23-lite-ddl-impl-receipt-20260825`
- 日期：2026-08-25
- queue_rev：79 → CC 执行
- 任务书：`204-stage2-s23-lite-ddl-impl-tasking-20260825.md`
- 前置：`203` 规划 PASS；`docs/38` §2；用户 **D**
- 用户裁定：Stage 2 **C**；缩刀 **D**

---

## §NOW 执行表

| 步 | 项 | 状态 | sha256 摘要 | role |
|---|---|---|---|---|
| 1 | `git pull origin main` (queue_rev 78→79) | ✅ | — | — |
| 2 | 读 `204` + `203` + `docs/38` | ✅ | — | — |
| 3 | 起草 `schema/migrations/010_project_event_alignment.sql`（+ 11 列） | ✅ | `fac3318a…` | schema_migration_ddl |
| 4 | 起草 `schema/migrations/010_project_event_alignment.log` | ✅ | `63b1982e…` | schema_migration_log |
| 5 | 起草 `tests/test_project_event_s23lite.py`（5 主案 + 3 bonus = 8 case） | ✅ | `922fe598…` | schema_negative_test |
| 6 | 补 pack (3 +1 = +3) | ✅ | — | spike_helper |
| 7 | commit → origin 优先 | ✅ | `72b9180` | commit |
| 8 | 回执 `205` 进 `reviews/` | ✅（本文件） | `63dad117…` | documentation |
| 9 | push origin / github | ✅ 双推成功（`5458404..72b9180`）| — | — |
| 10 | → `84` POLL | ✅ 已 re-arm | — | — |

---

## §1. 交付清单

### 1.1 新文件

| 路径 | 行数 | 大小 | sha256（前 8） | role |
|---|---|---|---|---|
| `schema/migrations/010_project_event_alignment.sql` | 83 | 4092 | `fac3318a` | schema_migration_ddl |
| `schema/migrations/010_project_event_alignment.log` | 31 | 1714 | `63b1982e` | schema_migration_log |
| `tests/test_project_event_s23lite.py` | 220+ | 9019 | `922fe598` | schema_negative_test |
| `reviews/stage0-gate0-rework-2026-08-23/205-stage0-cc-s23-lite-ddl-impl-receipt-20260825.md` | （本文件） | 7701 | `63dad117` | documentation |

### 1.2 migration 010 概要（per `204` §NOW 要求 1）

| 章节 | 内容 |
|---|---|
| 表 | `project_event`（既有，**ALTER additive**） |
| 新增列 | 11：`canonical_project_name` / `project_name_en` / `project_class` / `status_year` / `lineage` / `project_hash_canonical` / `investment_currency_canonical` / `expected_output_text` / `delay_reason` / `completion_year_planned` / `completion_year_actual` |
| 新增索引 | 4：`idx_project_event_hash_canonical`（partial）/ `idx_project_event_lineage_gin`（GIN jsonb_path_ops partial）/ `idx_project_event_class`（partial）/ `idx_project_event_status_year`（partial） |
| 注释 | 11 列各 1 条 COMMENT |
| search_path | `SET search_path = cegr, public;` + `RESET search_path`（每文件首尾） |
| FK / EXCLUDE / ENUM / TRIGGER | **0 修改**（per docs/04 §3.8 五态机不动 / tasking 204 §红线） |
| 不动 | `project_status` ENUM (ANNOUNCED/SIGNED/STARTED/PRODUCING/AT_CAPACITY)、现有 FK、现有 CHECK、现有触发器 |

### 1.3 pytest s23lite 概要（per `204` §NOW 要求 2）

| case | 类别 | 断言点 |
|---|---|---|
| 1 | 主案 | `project_event` 11 新增列存在 + 类型正确 + 全部 nullable |
| 2 | 主案 | `project_event` 表存在（依赖 01-core.sql §785-798） |
| 3 | 主案（红线）| 无 `score` / `rating` / `rank` / `total_score` / `credit_score` / `performance_score` 列 |
| 4 | bonus | `lineage` 列类型 = `jsonb`（per R3-E） |
| 5 | bonus | migration 可幂等 apply 两次（`IF NOT EXISTS` 守门） |
| 6 | bonus | 4 新增索引存在 |
| 7 | bonus（文件级）| migration SQL 文本本身不含打分字段（strip 注释后扫） |
| 8 | bonus（边界守卫）| `scripts/seed_project_event_demo.py` 不应被本刀引入（tasking 204 §SCHEMA 钉死） |

**注**：case 1 起首行即 `import psycopg2.extras`（从 knife 3 教训固化），保证 `psycopg2.extras.register_uuid()` 在 collection 阶段可用。

### 1.4 manifest 变更

| 字段 | 变更前 | 变更后 |
|---|---|---|
| `artifact_count` | 530 | **534** (+4: migration + log + pytest + receipt) |
| `len(artifacts)` | 530 | **534** |
| `sum(role_count)` | 530 | **534** |
| `schema_migration_ddl` | 8 | 9 |
| `schema_migration_log` | 4 | 5 |
| `schema_negative_test` | 25 | 26 |

新增条目：
```json
{
  "schema/migrations/010_project_event_alignment.sql": "schema_migration_ddl",
  "schema/migrations/010_project_event_alignment.log": "schema_migration_log",
  "tests/test_project_event_s23lite.py": "schema_negative_test"
}
```

**invariant 守门**：533 == 533 == 533 ✅

---

## §2. 关键决策（per `204` §SCHEMA 钉死）

| 决策点 | 裁定 | 来源 |
|---|---|---|
| 表范围 | 1 张：`project_event`（既有，additive） | `204` §SCHEMA |
| 五态 ENUM | **不修改**既有 `project_status` | docs/04 §3.8 |
| 加列数 | 11 列全 ADD COLUMN IF NOT EXISTS | docs/38 §2.1 |
| 加列类型 | TEXT (×7) + INTEGER (×4) + JSONB (×1) — 严格按 docs/38 §2.1 字段清单 | docs/38 §2.1 |
| FK / EXCLUDE / CHECK | **0**（additive-only contract；FK 启用留待未来刀） | `204` §红线 + knife 2 S2.2-lite 平行 |
| 触发器 | **0**（不写五态自动跃迁） | docs/04 §3.8 五态 append-only |
| 索引数 | 4：hash_canonical partial + lineage GIN partial + class partial + status_year partial | docs/38 §3.1 |
| seed | **不写**（per `204` §SCHEMA） | `204` §SCHEMA |
| dbt 首批 | **不写**（per `204` §SCHEMA） | `204` §SCHEMA |
| UI | **不接** EvidenceChain | `204` §SCHEMA |

---

## §3. 红线自检

| 红线 | 状态 |
|---|---|
| ❌ 不宣布 Stage 0 / Gate 1 / Gate 2 PASS | ✅ 仅 DDL + pytest |
| ❌ 不批量爬项目公告 | ✅ 未写 seed |
| ❌ 不做官员评分/总分/排名 | ✅ migration 无 score/rating/rank 列；pytest case 3+7 双层守门 |
| ❌ 不 HTTP 爬源站 | ✅ |
| ❌ 不降 OCR 门槛 | ✅ 无关 |
| ❌ 不改 1909 / 陕西代表中国 | ✅ 无关 |
| ❌ 不擅自 --force / --force-with-lease | ✅ ff-only pull |
| ❌ 不替用户下裁定 | ✅ §2 列决策；裁定权归 Cursor/用户 |
| ❌ 不在聊天复述 Cursor 长文 | ✅ 仅回执要点 |
| ❌ 不索要 PAT | ✅ |
| ❌ 不改 `gate_thresholds.json` | ✅ 未读未写 |
| ❌ 不碰 `00-CC-CURRENT.md` | ✅ Cursor 拥有 |
| ✅ pack invariant 守门 | ✅ 530 → 534 |
| ✅ 回执 location = `reviews/stage0-gate0-rework-2026-08-23/` | ✅ |
| ✅ 不修改 `project_status` 五态机 ENUM | ✅ migration 仅 ADD COLUMN |
| ✅ 不写 EXCLUDE / 触发器 | ✅ |
| ✅ migration 010 idempotent | ✅ pytest case 5 验证 |
| ✅ `import psycopg2.extras` 在 collection 阶段可用 | ✅ knife 3 教训固化 |

---

## §4. 推送 / 三路对齐

| 步骤 | 命令 | 结果 |
|---|---|---|
| origin pull | `git fetch origin && git pull --ff-only origin main` | queue_rev 79 |
| 本地校验 | `python3 -c "json.load(...)"` manifest invariant | ✅ 534 == 534 == 534 |
| commit | `git add … && git commit -m "feat(schema): S2.3-lite project_event additive (+11 cols, 4 idx, 8-case pytest)"` | ✅ `72b9180` |
| 回执 backfill | commit ②: `chore(receipt): backfill 205 SHA + commit SHA` | ⏳ 紧随 push 后 |
| origin push | `git push origin HEAD`（**priority**）| ✅ `5458404..72b9180` → main |
| github push | `git push github HEAD`（带 proxy）| ✅ `5458404..72b9180` → main |
| 三路对齐 | origin/main = github/main = local HEAD | ✅ `72b9180` |

> **禁止 amend-after-push**：receipt SHA + commit SHA 必须在独立 commit 里 backfill（per knife 2/3 经验）。

---

## §5. 下次 heartbeat 预期

- `queue_rev 79` 完成后：Cursor 收 `205` → 下发 `206-stage0-cursor-s23-lite-ddl-audit-…md`（PASS/FAIL）
- 若 PASS：进入 S2.3 落地刀（tasking 207+）— `seed` + `dbt` + UI 接 EvidenceChain
- 若 FAIL：`205-correction` 回合（修 migration/pytest + re-commit）

— End of `205` —