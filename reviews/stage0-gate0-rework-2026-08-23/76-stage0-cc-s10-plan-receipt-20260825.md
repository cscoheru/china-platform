# S1.10 — CC 规划回执

- 编号：`76-stage0-cc-s10-plan-receipt-20260825`
- 前置：`75` 任务书；`docs/24`
- 提交：`619ab74`
- Pack：456 artifacts (role_count +1 vs 455)
- 双推：origin ✅ / github **HOLD** (443 timeout ×2)

## 交付物

| 文件 | 说明 |
|---|---|
| `docs/24-stage1-s10-fastapi-readonly-plan-20260825.md` | S1.10 FastAPI 规划文档 (~600行) |

## 规划摘要

### 12 Endpoints
| 方法 | 路径 | 数据来源 |
|---|---|---|
| GET | `/health` | `SELECT 1` |
| GET | `/api/openapi.json` | FastAPI auto |
| GET | `/api/docs` | FastAPI auto Swagger UI |
| **GET** | **`/api/indicator/{id}/series`** | `int_indicator_timeseries` (核心验收) |
| GET | `/api/indicator/{id}/series/{geo_id}` | `int_indicator_timeseries` |
| GET | `/api/indicator` | `stg_observation` 聚合 |
| GET | `/api/source` | `stg_source_registry` |
| GET | `/api/source/{id}` | `stg_source_registry` |
| GET | `/api/source/{id}/coverage` | `int_source_coverage` |
| GET | `/api/source/{id}/runs` | `stg_ingestion_run` |
| GET | `/api/observation` | `stg_observation` |
| GET | `/api/observation/{id}` | `stg_observation` |

### 核心安全策略
- **psycopg2 ThreadedConnectionPool** (min=2, max=10)
- **每 session SET TRANSACTION READ ONLY** (PG session-level read-only)
- INSERT/UPDATE/DELETE 自动抛 `ReadOnlySqlTransaction`
- API handler 禁止写操作 (lint 规则)

### 错误契约
- 200 OK / 400 invalid input / 404 not found / 422 validation / 500 unexpected / 503 DB unavailable
- `ErrorResponse{error_code, message, detail}` 模式
- 7 个 error codes: INDICATOR_NOT_FOUND / SOURCE_NOT_FOUND / INVALID_UUID / INVALID_DATE / PAGE_SIZE_TOO_LARGE / DB_UNAVAILABLE / READ_ONLY_VIOLATION

### Pydantic v2 响应模型
- `IndicatorSeriesResponse` / `IndicatorSeriesPoint`
- `SourceListItem` / `SourceCoverage`
- `ObservationItem` / `ObservationList`
- `Pagination` / `HealthCheck` / `ErrorResponse`

### 测试策略 (≥9 tests)
- `test_health_endpoint` — /health 200 + db_reachable=true
- `test_indicator_series_empty` — 未知 indicator → 200 + 空 series
- `test_indicator_series_with_data` — 已知 indicator → 返回数据
- `test_indicator_series_pagination` — page_size=2 → 2 项 + has_next
- `test_source_coverage` — 已知 source → 覆盖统计
- `test_invalid_uuid_returns_400`
- `test_db_unavailable_returns_503`
- `test_read_only_enforcement` — 尝试 INSERT → ReadOnlySqlTransaction
- `test_openapi_schema_complete` — openapi.json 包含所有 12 endpoints

### 依赖
- `fastapi>=0.110.0` / `uvicorn[standard]>=0.27.0`
- `pydantic>=2.5.0` / `pydantic-settings>=2.1.0`
- `httpx>=0.26.0` (TestClient)
- `psycopg2-binary>=2.9.9` (已有)
- **不用** SQLAlchemy / SQLModel / 任何 ORM

## 红线遵守

| 红线 | 状态 |
|---|---|
| 不 Gate 1 PASS | ✅ |
| 不 DSH | ✅ |
| 不批量爬取 | ✅ |
| 不降 OCR | ✅ gate_thresholds.json 不改 |
| 不 Next.js | ✅ backend only |
| 不写 cegr 原表 | ✅ SET TRANSACTION READ ONLY |
| Cursor 不写 docs/24 正文 | ✅ CC 起草 |

## Github HOLD

github 443 timeout ×2 (2026-08-25 12:43–12:46)。origin `619ab74` 已入库。待网络恢复后手动 `git push github HEAD`。