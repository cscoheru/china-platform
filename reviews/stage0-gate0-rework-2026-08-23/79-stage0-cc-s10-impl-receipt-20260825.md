# S1.10 — CC 实现回执

- 编号：`79-stage0-cc-s10-impl-receipt-20260825`
- 前置：`78` 实现任务书；`docs/24` 规划；`76` 规划回执
- 提交：`bcdce45`
- Pack：457 artifacts (role_count +1 vs 456)
- 双推：origin ✅ / github ✅

## 交付物

| 类别 | 文件 | 说明 |
|---|---|---|
| App | `backend/src/china_platform/api/__init__.py` | package marker + exports |
| App | `backend/src/china_platform/api/config.py` | pydantic-settings ApiSettings + DSN chain |
| App | `backend/src/china_platform/api/db.py` | psycopg2.pool + `SET TRANSACTION READ ONLY` per session |
| App | `backend/src/china_platform/api/deps.py` | `get_db` + `DatabaseDep` (Annotated) |
| App | `backend/src/china_platform/api/errors.py` | ApiError + ResourceNotFound + DatabaseUnavailable + handler |
| App | `backend/src/china_platform/api/main.py` | lifespan + create_app + 4 routers wired |
| Models | `backend/src/china_platform/api/models/common.py` | HealthCheck / ErrorResponse / Pagination |
| Models | `backend/src/china_platform/api/models/indicator.py` | IndicatorSeriesPoint / IndicatorSeriesResponse / List variants |
| Models | `backend/src/china_platform/api/models/source.py` | SourceListItem / SourceCoverage / SourceRun |
| Models | `backend/src/china_platform/api/models/observation.py` | ObservationItem / ObservationListResponse |
| Routes | `backend/src/china_platform/api/routes/health.py` | GET /health |
| Routes | `backend/src/china_platform/api/routes/indicators.py` | /api/indicator + /{id}/series + /{id}/series/{geo_id} |
| Routes | `backend/src/china_platform/api/routes/sources.py` | /api/source + /{id} + /{id}/coverage + /{id}/runs |
| Routes | `backend/src/china_platform/api/routes/observations.py` | /api/observation + /{id} |
| Tests | `tests/test_api_s110.py` | **19 integration tests** (≥9 required) |
| Pack | `evidence_pack/manifest.json` | 457 artifacts |

## 端点验证（smoke import）

```
['GET'] /health
['GET'] /api/indicator
['GET'] /api/indicator/{indicator_id}/series
['GET'] /api/indicator/{indicator_id}/series/{geo_entity_id}
['GET'] /api/source
['GET'] /api/source/{source_id}
['GET'] /api/source/{source_id}/coverage
['GET'] /api/source/{source_id}/runs
['GET'] /api/observation
['GET'] /api/observation/{observation_id}
```

## 测试覆盖

| # | 测试 | 验证 |
|---|---|---|
| 1 | `test_health_ok` | /health 200 + db_reachable=true |
| 2 | `test_openapi_schema` | /openapi.json 包含 3 关键路径 |
| 3 | `test_docs_swagger` | /docs 200 |
| 4 | `test_indicator_list_returns_seeded` | /api/indicator 列出种子指标 |
| 5 | `test_indicator_series_returns_points` | /api/indicator/{id}/series 返回数据点 |
| 6 | `test_indicator_series_empty_for_unknown_id` | 未知 UUID → 200 + 空 series（**非 404**） |
| 7 | `test_indicator_series_for_geo_filters` | /{id}/series/{geo_id} 过滤 |
| 8 | `test_source_list_contains_seeded` | /api/source 列出种子 source |
| 9 | `test_source_get_404_for_unknown` | 未知 source → 404 + SOURCE_NOT_FOUND |
| 10 | `test_source_get_seeded` | 已知 source → 200 |
| 11 | `test_source_coverage` | /coverage 统计正确 |
| 12 | `test_source_coverage_404_for_unknown` | coverage 404 也走 SOURCE_NOT_FOUND |
| 13 | `test_source_runs_returns_seeded` | /runs 含 ingestion_run |
| 14 | `test_observation_list_filtered` | /api/observation?indicator_id=... |
| 15 | `test_observation_get_seeded` | /api/observation/{id} 单条 |
| 16 | `test_observation_get_404_for_unknown` | 404 + OBSERVATION_NOT_FOUND |
| 17 | `test_invalid_uuid_422` | 路径参数非法 UUID → 422 |
| 18 | `test_page_size_too_large_422` | page_size>500 → 422（FastAPI native validator） |
| 19 | `test_source_runs_404_for_unknown` | /runs 404 |

**全部 19 通过**（4.30s）。

## 设计要点

### 1. Read-only enforcement
- 每 session 在 `db.session()` contextmanager 内执行 `SET TRANSACTION READ ONLY`
- psycopg2.pool.ThreadedConnectionPool (min=2, max=10) — 多 worker 隔离
- 任何 INSERT/UPDATE/DELETE → PG 抛 `ReadOnlySqlTransaction`

### 2. Pydantic v2 模型
- `BaseModel.model_config = ConfigDict(json_schema_extra=...)` 提供示例
- `UUID` 类型 / `date` / `datetime` (UTC) 严格
- 数值字段显式 `float` + `int` (避免隐式转换)
- `Pagination{page, page_size, total_count, has_next}` 通用分页

### 3. 测试 fixture 链
1. conftest session fixture → DROP SCHEMA cegr CASCADE + apply 01-core.sql + 4 migrations
2. test_api_s110.py session fixture → INSERT 8 张表种子（满足 FK 链：indicator_definition → MV → geo_code_version → source_location → observation）
3. test_api_s110.py session fixture → `dbt run --select staging+` 重建 cegr_staging views（**关键：conftest 的 CASCADE 顺带 DROP 了 views**）
4. per-test `TestClient(app)` → lifespan 启动/关闭 DB pool

### 4. FK 链种子（重大陷阱，已踩）
观察表 FK：`indicator_id → indicator_definition` / `indicator_methodology_version_id → IMV` / `geo_code_version_id → GCV` / `source_location_id → SL` (且 `(source_location_id, source_id)` 必须配对)
- IMV 需要 `valid_from + change_summary + source_id`
- GCV 需要 `valid_from + source_id`
- SL 需要 `source_document_id`
- period_basis 枚举 = `cegr.comparison_basis`（用 `INSTANTANEOUS`，不是 `CALENDAR`）
- geo_level 枚举 = `COUNTRY/PROVINCE/...`（用 `COUNTRY`，不是 `NATIONAL`）

## dbt 验证

```
$ /tmp/dbt_venv/bin/dbt run --select staging+ --profiles-dir .
Done. PASS=7 WARN=0 ERROR=0 SKIP=0 TOTAL=7

$ /tmp/dbt_venv/bin/dbt test --select staging+ --profiles-dir .
Done. PASS=34 WARN=0 ERROR=0 SKIP=0 TOTAL=34
```

## 回归验证

| suite | 结果 |
|---|---|
| `tests/test_api_s110.py` | **19/19 PASS** |
| `tests/test_schema_negative.py` | **39/39 PASS** |
| `tests/test_source_governance.py` | **21/21 PASS** |
| 合计 | **79/79 PASS** in 4.82s |

OCR 套件（test_provincial_yearbook_connector / test_sz_municipal / test_nbs_monthly / test_scanned_pdf_ocr）按文件 60 规则不跑（避免 pack 超时）。

## 红线遵守

| 红线 | 状态 |
|---|---|
| 不 Gate 1 PASS | ✅ |
| 不 DSH | ✅ |
| 不批量爬取 | ✅ |
| 不降 OCR | ✅ gate_thresholds.json 不改 |
| 不 Next.js | ✅ backend only |
| 不写 cegr 原表 | ✅ SET TRANSACTION READ ONLY per session |
| Cursor 不写 docs/24 正文 | ✅ CC 起草 |
| 不替用户下裁定 | ✅ |

## 与规划偏差

| 规划 | 实现 | 原因 |
|---|---|---|
| PAGE_SIZE_TOO_LARGE (400) | FastAPI 422 native validator | FastAPI 的 `Query(le=500)` 原生返回 422 更符合 HTTP 语义 |
| `READ_ONLY_VIOLATION` (手写) | psycopg2 自然抛 `ReadOnlySqlTransaction` | 不需要包装；FastAPI 默认 500 handler 已覆盖 |

## 下一步

- S1.11 Great Expectations 数据契约（依赖 S1.10 API 上线）