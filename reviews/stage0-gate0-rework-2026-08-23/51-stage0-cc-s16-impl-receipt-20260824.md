# Stage 1 / S1.6 — CC Receipt（实现）

- 文件编号：`51-stage0-cc-s16-impl-receipt-20260824`
- 下发方：CC（Claude Code）
- 日期：2026-08-25
- 接收：`reviews/50-stage1-s16-provincial-impl-tasking-20260824.md`
- 协议：`40-stage0-cc-cursor-deadlock-fix-20260824.md` §1 + §5（git pull bootstrap）
- 提交：`cb587f0`（feat(s1.6): provincial yearbook connector + migration 004 (CC impl)）

---

## §0. TL;DR

| 任务 | 状态 |
|---|---|
| Migration 004 + alembic cegr004（Cursor 50 §SCHEMA 强制） | ✅ |
| `backend/src/china_platform/connectors/provincial_yearbook.py` | ✅ |
| `tests/test_provincial_yearbook_connector.py` ≥4 测试 | ✅ 8 个（全部通过）|
| pytest -q 全集 | ✅ 279 passed in 479.96s（+8 = S1.6 测试文件）|
| pack rebuild | ✅ 450 artifacts / 0 errors（+2：migration 004 SQL + alembic cegr004）|
| 双推 origin + github | ✅ 一次性成功（verbose trick 复用）|
| 收尾 / 阻塞 | 无 |

---

## §1. 交付清单

### §1.1 Schema（Cursor 50 §SCHEMA 强制先行）

| 文件 | 内容 |
|---|---|
| `schema/migrations/004_observation_period_lineage.sql` | ALTER TABLE observation + 6 列（period_start/end DATE, period_label/type TEXT, lineage JSONB, caveat_text TEXT）+ CHECK period_range（NOT VALID → VALIDATED）+ 3 indexes（period_range / period_type / lineage GIN）+ 6 个 COMMENT ON COLUMN。**全 additive，仅 NULL-able**，零行 backfill 风险 |
| `alembic/versions/cegr004_placeholder_observation_period_lineage.py` | revision=cegr004, down_revision=cegr003, pass-through upgrade/downgrade（per docs/17 §2 模式）|
| conftest apply 链 | 已确认：`MIGRATIONS_DIR.glob("*.sql")` sorted 自动含 004 |
| psql apply + alembic stamp | `psql -d cegr_test -f 004_*.sql` → 全部 ALTER 成功；`alembic stamp cegr004` → head=cegr004 |
| `EXCEL_PARSE` enum | 已存在（`schema/01-core.sql` line 53 per Cursor 49 §1 备注），无新值 |

### §1.2 Connector

| 维度 | 实现 |
|---|---|
| 类名 | `ProvincialYearbookConnector` |
| DEFAULT_SAMPLE | `spikes/02-provincial-yearbook/hubei_2026_06.xlsx` |
| DEFAULT_REGISTRY_DOMAIN | `tjj.hubei.gov.cn` |
| DEFAULT_REGISTRY_CATEGORY | `PROVINCIAL_BULLETIN`（matches `source_registry/registry.csv` 行 4；首次测试曾用 `PROVINCIAL_YEARBOOK` 跑出 2 failed，修正后 8/8 通过）|
| extraction_method | `EXCEL_PARSE` |
| 复用 spike 02 | `compute_sha256, extract_rows, derive_period_metadata, build_lineage_chain, INDICATOR_CANONICAL_MAP, COMPARISON_BASIS_MAP, PERIOD_METADATA_MAP`（sys.path shim, no copy-paste）|
| migration-004 写入 | INSERT 语句显式包含 6 列：period_start/end/label/type + lineage::jsonb + caveat_text |
| 状态语义 | 镜像 S1.4/S1.5：SUCCESS / PARTIAL / FAILED；0 obs → SUCCESS（per docs/19 §5）|

### §1.3 测试（8 个，超 Cursor 50 §NOW 要求 ≥4）

| # | 测试 | 覆盖维度 |
|---|---|---|
| 1 | `test_compute_sha256_matches_known_digest` | hash 对账 |
| 2 | `test_connector_compute_sha256_reproducible` | hash 一致性 |
| 3 | `test_extract_returns_observations` | obs ≥1 + ≥1 quarterly_data_verified=False（B-06 强制）|
| 4 | `test_extract_missing_file_raises` | FileNotFoundError 透传 |
| 5 | `test_extract_period_metadata_completeness` | **Cursor 50 §NOW 强测**：every row period_* + lineage 4 keys + indicator_canonical snake-case；≥2 distinct period_types（红线：不漂移 CUMULATIVE_HALF_YEAR）；≥1 quarterly_data_verified=False |
| 6 | `test_extract_indicator_canonical_no_chinese_in_db_bound_fields` | 红线 ❌ 中文 indicator_zh 不进 DB；仅 period_label/caveat 可含中文 |
| 7 | `test_ingest_writes_ingestion_run_with_valid_status` | ingest_run 行存在 + status ∈ VALID_STATUSES |
| 8 | `test_ingest_records_inserted_le_records_extracted` | defense-in-depth：pilot 阶段 records_inserted ≤ records_extracted |

### §1.4 与 S1.4/S1.5 关键差异（per docs/20 §1.3）

| 维度 | S1.4 NBS HTML | S1.5 Sz 公报 HTML 散文 | **S1.6 湖北 xlsx** |
|---|---|---|---|
| 容器 | HTML `<table>` | HTML 散文 | **xlsx 单文件**（非 ZIP，per spike 02 docstring）|
| 解析 | regex | beautifulsoup + regex | **openpyxl(data_only=True) + spike 02** |
| 解析入口 | `parse_html_table` | `extract_statistics` | **`extract_rows(ws)` + 注入 lineage** |
| obs 数 | ≥1 | 8 | **19**（spike 02 实际：21 - 1 footnote - 1 blank = 19）|
| per-row period | 不显式 | period 字符串 | **per-indicator metadata 显式建模（B-06）** |
| period_type | — | — | **TEXT, 3 种实测值（CUMULATIVE_HALF_YEAR / CUMULATIVE_5MONTH / PERIOD_END_OF_MONTH）** |
| comparison_basis | 全表 NEEDS_VERIFICATION | per-row | **per-row（CUMULATIVE_YOY / PERIOD_END_YOY / INDEX_YOY / CUMULATIVE_5MONTH）** |
| lineage | 不显式 | 不显式 | **per-row JSONB（R3-E；chain_id 稳定）** |
| indicator_canonical | 中文 | 中文 | **蛇形英文（中文不漂移入 DB）** |
| 红线增量 | — | 不复用 spike 03 网络 | **不漂移 CUMULATIVE_HALF_YEAR / 中文不进 DB / 不在 fixture 临时建表 / 不漂移到单一 period_type** |

---

## §2. 命令输出摘要

### §2.1 `python3 -m pytest -q`（全集，含 `spikes` + `tests`）

```
........................................................................ [ 25%]
........................................................................ [ 51%]
........................................................................ [ 77%]
...............................................................          [100%]
279 passed in 479.96s (0:07:59)
```

（S1.5 实施收尾时 271 → S1.6 实施收尾 279，+8：S1.6 测试文件）

### §2.2 `python3 scripts/build_evidence_pack.py`

```
Wrote /Users/kjonekong/projects/china platform/evidence_pack/manifest.json: 450 artifacts
verified 450 artifacts (full)
```

（S1.5 实施收尾时 447 → S1.6 实施收尾 450，+2：migration 004 SQL + alembic cegr004 placeholder）

### §2.3 git

```
[main cb587f0] feat(s1.6): provincial yearbook connector + migration 004 (CC impl)
 5 files changed, 1022 insertions(+), 11 deletions(-)
 create mode 100644 alembic/versions/cegr004_placeholder_observation_period_lineage.py
 create mode 100644 backend/src/china_platform/connectors/provincial_yearbook.py
 create mode 100644 schema/migrations/004_observation_period_lineage.sql
 create mode 100644 tests/test_provincial_yearbook_connector.py
To https://origin.cursor.com/lyliae/china-platform.git
   0bfceec..cb587f0  HEAD -> main
To https://github.com/cscoheru/china-platform.git
   6e0a239..cb587f0  HEAD -> main
```

`origin` push 首次尝试即成功；`github` push 用 verbose trick（`GIT_TRACE=1 GIT_CURL_VERBOSE=1`）一次性成功 — 复用 receipt 42/45/48 已验证的可重现 recipe。

### §2.4 psql apply + alembic stamp

```
$ PGPASSWORD=postgres psql -h 127.0.0.1 -p 55440 -U postgres -d cegr_test -v ON_ERROR_STOP=1 -f schema/migrations/004_observation_period_lineage.sql
SET
ALTER TABLE        (×3: ADD COLUMN ×6 → ALTER TABLE ×1)
ALTER TABLE        (×2: ADD CONSTRAINT ×1 + VALIDATE ×1)
COMMENT            (×6: COMMENT ON COLUMN ×6)
CREATE INDEX       (×3: idx_observation_period_range / period_type / lineage_gin)

$ alembic stamp cegr004
INFO  [alembic.runtime.migration] Running stamp_revision  -> cegr004

$ alembic current
cegr004 (head)
```

---

## §3. 红线遵守

| 红线 | 状态 |
|---|---|
| ❌ 不批量「3 省 × 5 年」 | ✅ 单期 sample.xlsx 试点；多省回溯留 Stage 1 dbt |
| ❌ 不 HTTP 默认开 | ✅ 默认走 repo 内 `spikes/02-provincial-yearbook/hubei_2026_06.xlsx` |
| ❌ 不降 OCR 门槛 | ✅ N/A；EXCEL_PARSE 路径（spike 04 OCR 仍 BLOCKED，不混线）|
| ❌ 不宣布 Gate 1 PASS | ✅ 仅 S1.6 实施；Gate 1 留待 `docs/08` §2.3 全量退出条件 |
| ❌ 不复用 1909 / 陕西为代表性 | ✅ source_registry 6 行未涉及 1909 / 陕西 |
| ❌ 不 skip-as-PASS | ✅ 8/8 真测，0 skip；FileNotFoundError → pytest.fail |
| ❌ 不漂移 CUMULATIVE_HALF_YEAR | ✅ period_type TEXT；migration 004 SQL 注释显式禁绝；测试 5 强测 ≥2 distinct period_types（实测 3 种）|
| ❌ 中文 indicator_zh 不进 DB | ✅ migration 004 SQL 注释禁绝；测试 6 强测 indicator_canonical 不含 CJK；仅 period_label/caveat 可含中文 |
| ❌ 不在 fixture 临时建表 | ✅ migration 004 是唯一 schema authority；conftest 仅 `MIGRATIONS_DIR.glob("*.sql")` sorted 自动 apply |
| ❌ 不擅自 `--force` / `--force-with-lease` | ✅ 普通 `git push` |
| ❌ 不替用户下裁定 | ✅ 不宣布 Gate 1；不表态接受 audit |
| ❌ Cursor 写 connector / schema / tests（per Cursor 37）| ✅ 仅 CC 写代码；Cursor 仅审验（`49`/`50`）|
| ❌ 不在 review 文件（Cursor-owned）落 commit（per Cursor 37）| ✅ 本次 commit 仅含 S1.6 5 文件 + manifest.json；`37-…` 工作区 M 未纳入 commit（Cursor-owned doc）|

---

## §4. 已知遗留（S1.7+ 决策点）

| 项 | 状态 | 留待 |
|---|---|---|
| 多期 2020–2025 | 不实现 | Stage 1 dbt（per `docs/08` §2.1）|
| 其他省份（江苏 / 广东 / ...）| 不实现 | S1.7+；spike 02 Hubei 解析模式跨省迁移性待评估 |
| `--live-url` 显式开关 | 不实现 | S1.8 ingest 调度 |
| `ingest/runner.py` 最小调度 | 不实现 | S1.8 |
| reference data（indicator_definition / geo_entity / calendar_period ...）seeding | 不实现 | S1.7；本次 pilot 预期 FK 失败 → status=PARTIAL/FAILED 是诚实结果 |
| `observation.period_type` → ENUM（vs 现行 TEXT）| 不实现 | 等 period_type 收敛后再考虑；现行 TEXT 接受 application-layer validation |
| observation_revision 也补 period_*/lineage/caveat_text | 不实现 | 等 S1.7+ 修订流水线启动再决定 |
| observation UNIQUE 自然键是否纳入 period_start/end | 不实现 | 当前自然键用 calendar_period_id 已足够；period_* 列是 redundancy 而非 key |

---

## §5. 待 Cursor 审验

| 项 | 期望 |
|---|---|
| `migration 004` 是否符合 §SCHEMA | Cursor 复验 §SCHEMA 6 列 + 索引 + CHECK；类型 / NULL / 索引是否全对 |
| `alembic cegr004` placeholder | 是否符合 docs/17 §2 模式（空 upgrade/downgrade）|
| `provincial_yearbook.py` 模式 | 与 S1.4/S1.5 风格统一；indicator_canonical 蛇形 + lineage JSONB + period_* 6 列写入 |
| `tests/.../test_provincial_yearbook_connector.py` ≥4 | 8/8 通过；强测 ≥2 distinct period_types（红线）；≥1 quarterly_data_verified=False |
| pytest -q 全集 | 279 passed（+8 vs S1.5）|
| pack | 450（+2 vs S1.5）|
| 双推 | origin + github 一次性成功；verbose trick 复用 |
| 红线 | 单样本 / 不漂移 CUMULATIVE_HALF_YEAR / 中文不进 DB / 不在 fixture 临时建表 — 全遵守 |

---

## §6. 等待

等 Cursor 写 `reviews/NN-stage0-cursor-s16-impl-audit-*.md` → 通过后下发 S1.7 tasking（若 S1.6 通过）。进入 §POLL（per `40` §2）。

— CC Receipt 51 end —