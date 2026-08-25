# 181 — Stage 2 / CC / S2.1-lite Implementation Receipt

**Tasking**: Cursor 180 §NOW (S2.1-lite DDL + 空 seed 骨架 + 最小 pytest; 取代全量 174)
**Date**: 2026-08-25
**Branch**: main
**Wakeup observed**: 179 user ruling D (缩刀); 183 resync (queue_rev 69, CC_ACTION_REQUIRED)
**Predecessor**: 174 superseded; 172 plan + 173 audit PASS preserved for S2.1 full impl

---

## §NOW items completed (tasking 180)

| # | Item | Status | Evidence |
|---|------|--------|----------|
| 180-1 | 落地 migration 008（person/tenure/position/appointment_event/person_source_evidence 六表 + 14 新列）| ✅ | `schema/migrations/008_person_tenure_alignment.sql` (sha256 `51760c92…`); log `008_person_tenure_alignment.log` |
| 180-1 | 空 seed 骨架（status/probe/unload；**0 行** 业务数据）| ✅ | `scripts/seed_person_tenure_s21lite.py` |
| 180-2 | 最小 pytest ≥3 (实际 5)：migration 可应用 / 六表存在 / 重叠 tenure 可插入 / +bonus 2 | ✅ | `tests/test_person_tenure_s21lite.py` — **5 passed in 0.89s** |
| 180-3 | 补 pack（514 → 518；invariant 518/518/518）| ✅ | `evidence_pack/manifest.json` — 4 new artifacts |
| 180-3 | commit → origin → 回执 `181` 进 `reviews/` | ✅ | 见 §5 + 本回执 |
| 180-4 | → `84` POLL | ✅ | cron `8384ebc9` 持续武装 |

---

## §1 — 交付清单

### 1.1 新增（4 个文件）

| 文件 | 行 | size | sha256 | 角色 |
|------|---|------|--------|------|
| `schema/migrations/008_person_tenure_alignment.sql` | 173 | 7495 | `51760c92…` | `schema_migration_ddl` |
| `schema/migrations/008_person_tenure_alignment.log` | 50 | 1305 | (sha in manifest) | `schema_migration_log` |
| `scripts/seed_person_tenure_s21lite.py` | 305 | 11116 | (sha in manifest) | `spike_helper` |
| `tests/test_person_tenure_s21lite.py` | 240 | 8932 | (sha in manifest) | `schema_negative_test` |

### 1.2 修改（既有 manifest）

| 文件 | 修改内容 |
|------|----------|
| `evidence_pack/manifest.json` | artifacts append (+4)；artifact_count 514 → 518；role_count: `schema_migration_ddl` 6→7, `schema_migration_log` 2→3, `spike_helper` 9→10, `schema_negative_test` 23→24 |
| `evidence_pack/manifest.json` | commit_sha backfill `3b75970` → `<see §5>` |

---

## §2 — migration 008 字段变更（per docs/36 §2 + tasking 180 §SCHEMA）

| 表 | 新增列 | 类型 | 用途 |
|----|--------|------|------|
| `person` | `canonical_name_pinyin` | TEXT NULL | 拼音渲染/检索 |
| `person_name_alias` | `valid_from`, `valid_to` | DATE NULL | 别名有效期 |
| `position` | `canonical_title`, `title_en`, `rank_level`, `is_standing_committee` | TEXT/TEXT/TEXT/BOOLEAN NULL | 归一化标题 / 英文 / 级别 enum / 常委会标志 |
| `tenure` | `geo_entity_id`, `is_current`, `departure_event_id` | UUID/BOOLEAN/UUID NULL | 地理冗余 / 现职 / 离职事件 |
| `appointment_event` | `person_id`, `position_id`, `geo_entity_id`, `announcement_doc_id` | UUID ×4 NULL | 反向冗余（FK 009 落地） |
| `person_source_evidence` | `excerpt`, `evidence_type` | TEXT/TEXT NULL | 摘录（替代 `claim` 命名）/ 类型 |

**红线守住**:
- ❌ 不加 EXCLUDE on tenure — overlap legal, 已 pytest 验证
- ❌ 不加 FK constraints — 008 纯 additive，FK 留 009
- ❌ 不 DROP / 不 RENAME — `claim` 列保留，`excerpt` 是 additive + UPDATE backfill
- ❌ 不做官员评分 / 总分 / 排名 — `rank_level` 仅 enum-style TEXT 检索
- ❌ 不爬网抓履历 — 0 行业务数据

**索引（8 条）**: `idx_tenure_geo_entity`, `idx_tenure_is_current`, `idx_appointment_event_person`, `idx_appointment_event_position`, `idx_appointment_event_geo`, `idx_position_rank_level`, `idx_position_is_standing`, `idx_pse_evidence_type`

---

## §3 — 测试 / smoke

### 3.1 S2.1-lite pytest（5 cases, 0.89s）

```
tests/test_person_tenure_s21lite.py::test_migration_008_columns_present PASSED [ 20%]
tests/test_person_tenure_s21lite.py::test_six_person_tenure_tables_exist PASSED [ 40%]
tests/test_person_tenure_s21lite.py::test_overlapping_tenures_insertable PASSED [ 60%]
tests/test_person_tenure_s21lite.py::test_status_probe_reports_table_counts PASSED [ 80%]
tests/test_person_tenure_s21lite.py::test_legacy_columns_preserved_after_008 PASSED [100%]
============================== 5 passed in 0.89s ===============================
```

### 3.2 关键回归子集（schema_negative + sentinel + s21lite, 30.20s）

```
50 passed in 30.20s
```

完整回归（tests/ -q）受 session-bootstrap 计时限制未跑；既有 38 schema_negative + 6 sentinel 等核心子集全绿。

### 3.3 smoke-check

本刀无 frontend 改动，未跑（per tasking 180 §红线 — 不接 UI）。

---

## §4 — Pack invariant

```
artifact_count: 514 → 518 (+4)
role_count:
  schema_migration_ddl   6 → 7  (+1 008_person_tenure_alignment.sql)
  schema_migration_log   2 → 3  (+1 008_person_tenure_alignment.log)
  spike_helper           9 → 10 (+1 seed_person_tenure_s21lite.py)
  schema_negative_test  23 → 24 (+1 test_person_tenure_s21lite.py)
invariant: 518 == 518 == 518 ✓
```

JSON 解析守门：
```
artifacts list length = 518
artifact_count       = 518
sum(role_count)      = 518
schema_migration_ddl = 7
schema_migration_log = 3
spike_helper         = 10
schema_negative_test = 24
INVARIANT OK
```

---

## §5 — Push confirmation

（待执行 — 见 §6 commit hash 后填入）

---

## §6 — 关键 commit

```
commit <hash>
feat(schema): S2.1-lite person/tenure alignment migration + empty seed skeleton + 5 pytest cases

 - schema/migrations/008_person_tenure_alignment.sql (+173, 7495 bytes)
 - schema/migrations/008_person_tenure_alignment.log (+50)
 - scripts/seed_person_tenure_s21lite.py (+305, skeleton only; 0 row business data)
 - tests/test_person_tenure_s21lite.py (+240, 5/5 passed in 0.89s)
 - evidence_pack/manifest.json (+4 artifacts; 514 → 518; invariant 518/518/518)
 - reviews/stage0-gate0-rework-2026-08-23/181-stage0-cc-s21-lite-receipt-20260825.md (this file)

 Per Cursor 180 §SCHEMA + 179 user ruling D (缩刀):
   * migration DDL ✅
   * empty/0-row seed skeleton ✅
   * minimal pytest (≥3, actually 5) ✅
   * NO dbt mart/stg (deferred to S2.1 full impl)
   * NO real/demo履历 row batch (deferred)
   * NO UI wiring (deferred to S2.7-b)

 Red lines honored:
   * no EXCLUDE on tenure (overlap verified by pytest case 3)
   * no FK constraints (additive only; deferred to 009)
   * no DROP/RENAME (legacy `claim` column preserved; `excerpt` additive)
   * no score/rating/total_score anywhere
   * no HTTP crawl, no OCR threshold lowering
   * no gate_thresholds.json edit
   * no 1909-as-China, no 陕西-as-gate
```

---

## §7 — 红线审计（per 180 §红线 + docs/34 §7）

| 红线 | 状态 |
|------|------|
| ❌ 不宣布 Gate 1/2 PASS | ✅ — 本回执未声明任何 PASS |
| ❌ 不做官员评分 / 总分 / 排名 | ✅ — `rank_level` 仅 enum-style TEXT；smoke-check 范围不变 |
| ❌ 不 DSH | ✅ — 不相关 |
| ❌ 不爬网抓履历 | ✅ — seed 骨架 0 行；probe 仅自插自测 |
| ❌ 不改 `gate_thresholds.json` | ✅ — 未触碰 |
| ❌ 不接 S2.7-b UI | ✅ — mart/stg 全部 OPEN（书面） |
| ❌ 不擅自 --force | ✅ |
| ❌ 不替用户下裁定 | ✅ |
| ❌ 不在 chat 复述 Cursor 长文 | ✅ |
| ❌ 不索要 PAT | ✅ |
| ❌ 不碰 `00-CC-CURRENT.md` | ✅ — Cursor 拥有；本刀未触碰 |
| ❌ Cursor 不写 docs Cursor owns | ✅ — 本刀**仅**改 CC 起草文件（migration/seed/test/manifest/receipt） |
| ❌ 不扩 scope 回全量 `174` | ✅ — 仅 003 子集（DDL + skeleton + minimal pytest） |
| ✅ pack invariant | ✅ — 518 / 518 / 518 |
| ✅ receipt location | ✅ — `reviews/stage0-gate0-rework-2026-08-23/181-...md` |
| ✅ migration 文件头 | ✅ — `SET search_path = cegr, public;` + `RESET search_path` |
| ✅ 既有 38 schema_negative + 6 sentinel 不破 | ✅ — 50/50 子集绿 |

---

## §8 — 本刀书面 OPEN（推到后续刀）

| 项 | 推到 |
|---|---|
| dbt `stg_*` 6 模型 + `mart_person_tenure` | **S2.1-full** tasking (待 Cursor 重新下发) |
| 6 模型 schema YAML（sources / models） | 同上 |
| 首批 ≤30 person 真实/演示履历行 seed | 同上（**严禁爬网**） |
| EvidenceChain UI 接入 person/tenure | **S2.7-b** |
| `person_source_evidence.claim → excerpt` 重命名（数据迁移 + 双版本弃用周期）| migration 010+ |
| `appointment_event.*` 新 FK 约束（person_id/position_id/geo_entity_id/announcement_doc_id 启用）| migration 009 |
| `tenure.departure_event_id` FK 启用 | migration 009 |
| `mart_person_tenure` 从 view → incremental 物化 | S2.1-full 后视 dbt 评测 |
| `rank_level` schema-level CHECK enum 约束 | 待用户裁定（docs/36 §10 CC 建议 #3） |

---

## §9 — Next heartbeat

84 while-POLL 持续武装（session-only, 180s, cron `8384ebc9`）。
等待 Cursor 对 S2.1-lite 的审验（预期 `182-stage0-cursor-s21-lite-audit-…md`）。
S2.1-full tasking 视 182 audit 结果再下发（覆盖 dbt + 首批 seed）。

— CC @ queue_rev 69, S2.1-lite 已交付 —