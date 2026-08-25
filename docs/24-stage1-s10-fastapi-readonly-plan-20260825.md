# S1.10 — FastAPI 只读查询层规划

- 编号：`24-stage1-s10-fastapi-readonly-plan-20260825`
- 前置：`75` 任务书；`74` S1.9 通过；`docs/08` §2.1 S1.10；`docs/02` L5；`docs/10` §2
- 日期：2026-08-25
- 状态：**规划** — 实现另开任务书

---

## §0 TL;DR

在 S1.9 dbt staging 之上构建 **FastAPI + Uvicorn** 只读查询层，对接 `cegr_staging` schema 的 5 张 staging view + 2 张 intermediate model。

**核心验收**：`GET /api/indicator/{id}/series` 可调用，返回某 indicator 的时间序列（来自 `int_indicator_timeseries`）。

**本刀不做**: Next.js 前端、DSH、批量爬取、Gate 1 PASS、写 `cegr` 原表。

---

## §1 目录

| 节 | 内容 |
|---|---|
| §0 | TL;DR |
| §1 | 目录 |
| §2 | 项目结构 |
| §3 | 依赖 + 安装 |
| §4 | 数据库连接（DSN env var） |
| §5 | Pydantic 响应模型 |
| §6 | API 端点设计 |
| §7 | 错误契约 |
| §8 | OpenAPI 文档 |
| §9 | 与 docs/10 数据层测试映射 |
| §10 | 测试策略 |
| §11 | 配置 + 环境变量 |
| §12 | 红线 |
| §13 | 已知遗留 |
| §14 | 引用 |

---

## §2 项目结构

```
china-platform/
├── backend/
│   ├── src/
│   │   └── china_platform/
│   │       ├── connectors/        # 已有
│   │       ├── monitoring/        # 已有 (S1.8)
│   │       └── api/               # 🆕 S1.10 新增
│   │           ├── __init__.py
│   │           ├── main.py         # FastAPI app factory + lifespan
│   │           ├── deps.py         # 依赖注入 (DB session)
│   │           ├── config.py       # Settings (env var)
│   │           ├── db.py           # psycopg2 连接池 (read-only enforcement)
│   │           ├── errors.py       # 自定义异常 + handler
│   │           ├── models/         # Pydantic response models
│   │           │   ├── __init__.py
│   │           │   ├── indicator.py
│   │           │   ├── source.py
│   │           │   ├── observation.py
│   │           │   └── common.py   # Pagination / HealthCheck / ErrorResponse
│   │           └── routes/         # APIRouter per resource
│   │               ├── __init__.py
│   │               ├── health.py
│   │               ├── indicators.py
│   │               ├── sources.py
│   │               └── observations.py
│   └── tests/
│       └── test_api_*.py           # 🆕 httpx TestClient 集成测试
├── dbt/                            # S1.9 已有 (数据层)
└── docs/24-...-plan.md             # 本文件
```

**决策**：
- 单 FastAPI app（不分多个 microservice）
- 路由按资源拆 `APIRouter`（health / indicators / sources / observations）
- Pydantic v2（与 FastAPI 0.110+ 一致）
- 不引入 ORM（直接 psycopg2 + raw SQL；与现有 connector 模式一致）
- 不引入 SQLAlchemy（避免额外抽象层）

---

## §3 依赖 + 安装

### §3.1 新增 Python 依赖

```
fastapi>=0.110.0
uvicorn[standard]>=0.27.0
pydantic>=2.5.0
pydantic-settings>=2.1.0
httpx>=0.26.0          # 测试用 (TestClient)
psycopg2-binary>=2.9.9  # 已有 (connectors)
```

### §3.2 安装方式

```bash
# 创建 pyproject.toml (Poetry) 或 requirements.txt (本刀选 requirements.txt，简单)
cat > backend/requirements.txt <<EOF
fastapi>=0.110.0
uvicorn[standard]>=0.27.0
pydantic>=2.5.0
pydantic-settings>=2.1.0
httpx>=0.26.0
psycopg2-binary>=2.9.9
EOF

pip install -r backend/requirements.txt
```

### §3.3 pyproject.toml（可选，本刀不做）

如需正式打包，留待 S1.10+ 用 Poetry 整理（避免引入 poetry.lock 复杂度）。

---

## §4 数据库连接（DSN env var）

### §4.1 决策

| 项 | 决策 |
|---|---|
| 驱动 | `psycopg2`（已有；与 S1.8 IngestMonitor 一致） |
| 连接池 | `psycopg2.pool.ThreadedConnectionPool` (min=2, max=10) |
| DSN 来源 | `CEGR_DSN` env var → fallback `DATABASE_URL` → fallback dev default |
| 只读强制 | **连接后立即 `SET TRANSACTION READ ONLY`** (per-request session) |
| 超时 | `connect_timeout=5s`, `statement_timeout=30s` |
| 重连 | 失败抛 `DatabaseUnavailableError`，FastAPI 返回 503 |

### §4.2 config.py 设计

```python
# backend/src/china_platform/api/config.py
from pydantic_settings import BaseSettings

class ApiSettings(BaseSettings):
    dsn: str | None = None
    pool_min: int = 2
    pool_max: int = 10
    cors_origins: list[str] = ["http://localhost:3000"]
    log_level: str = "INFO"
    
    model_config = {"env_prefix": "CEGR_API_", "env_file": ".env"}
    
    def resolved_dsn(self) -> str:
        return (
            self.dsn
            or os.environ.get("CEGR_DSN")
            or os.environ.get("DATABASE_URL")
            or "postgresql://postgres:postgres@127.0.0.1:55440/cegr_test"
        )
```

### §4.3 db.py 设计

```python
# backend/src/china_platform/api/db.py
import psycopg2
from psycopg2 import pool
from contextlib import contextmanager

class Database:
    def __init__(self, dsn: str, min_conn: int = 2, max_conn: int = 10):
        self._pool = pool.ThreadedConnectionPool(min_conn, max_conn, dsn=dsn)
    
    @contextmanager
    def session(self):
        conn = self._pool.getconn()
        try:
            # Read-only enforcement (per session)
            with conn.cursor() as cur:
                cur.execute("SET TRANSACTION READ ONLY")
            yield conn
        finally:
            self._pool.putconn(conn)
    
    def close(self):
        self._pool.closeall()
```

**核心安全策略**：
- 每次 session 进入立即 `SET TRANSACTION READ ONLY` (PG session-level)
- 任何 INSERT/UPDATE/DELETE 自动抛 `psycopg2.errors.ReadOnlySqlTransaction`
- API handler 内禁止 `cursor.execute("SET TRANSACTION READ WRITE")` (lint 规则)

---

## §5 Pydantic 响应模型

### §5.1 common.py — 通用模型

```python
# backend/src/china_platform/api/models/common.py
from pydantic import BaseModel, Field
from datetime import datetime

class HealthCheck(BaseModel):
    status: str = "ok"
    db_reachable: bool
    timestamp_utc: datetime

class ErrorResponse(BaseModel):
    error_code: str          # e.g. "INDICATOR_NOT_FOUND"
    message: str
    detail: dict | None = None

class Pagination(BaseModel):
    page: int = Field(default=1, ge=1)
    page_size: int = Field(default=50, ge=1, le=500)
    total_count: int = Field(default=0, ge=0)
    has_next: bool = False
```

### §5.2 indicator.py — Indicator 模型

```python
class IndicatorSeriesPoint(BaseModel):
    period_start: date
    period_end: date | None = None
    period_type: str
    value: float
    unit: str | None = None
    geo_entity_id: UUID
    source_domain: str
    source_category: str
    source_level: str
    verification_status: str
    extraction_method: str
    confidence: float | None = None
    extracted_at: datetime

class IndicatorSeriesResponse(BaseModel):
    indicator_id: UUID
    series: list[IndicatorSeriesPoint]
    pagination: Pagination
```

### §5.3 source.py — Source 模型

```python
class SourceListItem(BaseModel):
    source_id: UUID
    domain: str
    organization: str
    category: str
    source_level: str
    enabled: bool

class SourceCoverage(BaseModel):
    source_id: UUID
    domain: str
    category: str
    source_level: str
    enabled: bool
    total_runs: int
    success_runs: int
    failure_runs: int
    failure_rate: float
    total_extracted: int
    total_inserted: int
    overall_insertion_pct: float | None
    avg_quality_score: float | None
    low_confidence_count: int
    missing_with_reason_count: int
    total_observations: int
    last_run_at: datetime | None
```

### §5.4 observation.py — Observation 模型

```python
class ObservationItem(BaseModel):
    observation_id: UUID
    indicator_id: UUID
    geo_entity_id: UUID
    calendar_period_id: UUID
    value: float | None
    unit: str | None
    confidence: float | None
    source_id: UUID
    period_start: date
    period_type: str

class ObservationList(BaseModel):
    observations: list[ObservationItem]
    pagination: Pagination
```

**决策**：
- 所有 ID 用 `UUID4` Pydantic 类型
- 时间戳用 `datetime` (UTC 强制)
- 所有数值类型显式标注 (避免 float/int 混淆)
- 可选字段用 `| None` 而非 `Optional[]` (Pydantic v2 推荐)

---

## §6 API 端点设计

### §6.1 端点清单

| 方法 | 路径 | 描述 | 数据来源 |
|---|---|---|---|
| GET | `/health` | 健康检查 (DB ping) | `SELECT 1` |
| GET | `/api/openapi.json` | OpenAPI schema (FastAPI 自动) | — |
| GET | `/api/docs` | Swagger UI (FastAPI 自动) | — |
| **GET** | **`/api/indicator/{id}/series`** | **核心验收** | `int_indicator_timeseries` |
| GET | `/api/indicator/{id}/series/{geo_id}` | 单 geo 时间序列 | `int_indicator_timeseries` |
| GET | `/api/indicator` | 列出所有 indicators (来源 stg_observation 聚合) | `stg_observation` |
| GET | `/api/source` | 列出所有 sources | `stg_source_registry` |
| GET | `/api/source/{id}` | 单 source 详情 | `stg_source_registry` |
| GET | `/api/source/{id}/coverage` | 单 source 覆盖统计 | `int_source_coverage` |
| GET | `/api/source/{id}/runs` | source 最近 ingestion runs | `stg_ingestion_run` |
| GET | `/api/observation` | 列出 observations (分页) | `stg_observation` |
| GET | `/api/observation/{id}` | 单 observation 详情 | `stg_observation` |

**总计**: 12 endpoints（health + 2 docs + 9 业务）。

### §6.2 核心端点：GET /api/indicator/{id}/series

**路径参数**: `id` (UUID)

**查询参数**:
- `geo_entity_id` (UUID, optional): 过滤地理实体
- `period_start` (date, optional): 起始时间
- `period_end` (date, optional): 结束时间
- `page` (int, default=1)
- `page_size` (int, default=50, max=500)

**SQL**:
```sql
SELECT
    indicator_id, geo_entity_id,
    period_start, period_end, period_type,
    value, unit, status, comparison_basis,
    source_domain, source_category, source_level, verification_status,
    extraction_method, confidence, extracted_at
FROM cegr_staging.int_indicator_timeseries
WHERE indicator_id = %(id)s
  [AND geo_entity_id = %(geo_id)s]
  [AND period_start >= %(start)s]
  [AND period_end <= %(end)s]
ORDER BY period_start ASC
LIMIT %(page_size)s OFFSET %(offset)s
```

**响应**: `IndicatorSeriesResponse` (见 §5.2)

**验收**: 返回空数组合法（indicator 不存在或无数据 → 200 + 空 series，不 404）

### §6.3 路由文件结构

```python
# backend/src/china_platform/api/routes/indicators.py
from fastapi import APIRouter, Depends, Query, Path
from uuid import UUID
from ..deps import get_db
from ..models.indicator import IndicatorSeriesResponse

router = APIRouter(prefix="/api/indicator", tags=["indicators"])

@router.get("/{id}/series", response_model=IndicatorSeriesResponse)
def get_indicator_series(
    id: UUID = Path(..., description="Indicator UUID"),
    geo_entity_id: UUID | None = Query(None),
    period_start: date | None = Query(None),
    period_end: date | None = Query(None),
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=500),
    db = Depends(get_db),
) -> IndicatorSeriesResponse:
    # build query + execute
    ...
```

---

## §7 错误契约

### §7.1 HTTP 状态码映射

| 状态码 | 触发条件 | 响应体 |
|---|---|---|
| 200 | 成功 | 资源数据 |
| 400 | 查询参数非法 (非 UUID/日期格式错) | `ErrorResponse` |
| 404 | 资源不存在 (source_id 不存在) | `ErrorResponse` |
| 422 | Pydantic 验证失败 (FastAPI 默认) | `ValidationErrorResponse` |
| 500 | 未预期异常 (BUG 路径) | `ErrorResponse` |
| 503 | DB 不可达 / 连接池耗尽 | `ErrorResponse` (error_code="DB_UNAVAILABLE") |

### §7.2 ErrorResponse 模式

```python
class ErrorResponse(BaseModel):
    error_code: str   # machine-readable: "INDICATOR_NOT_FOUND"
    message: str      # human-readable (英文/中文都可；本刀用英文)
    detail: dict | None = None  # 额外上下文
```

### §7.3 自定义异常 + handler

```python
# backend/src/china_platform/api/errors.py
class ApiError(Exception):
    def __init__(self, status_code: int, error_code: str, message: str, detail: dict | None = None):
        self.status_code = status_code
        self.error_code = error_code
        self.message = message
        self.detail = detail

class ResourceNotFound(ApiError):
    def __init__(self, resource: str, id: str):
        super().__init__(
            status_code=404,
            error_code=f"{resource.upper()}_NOT_FOUND",
            message=f"{resource} with id={id} not found",
            detail={"resource": resource, "id": str(id)},
        )

class DatabaseUnavailable(ApiError):
    def __init__(self, reason: str):
        super().__init__(
            status_code=503,
            error_code="DB_UNAVAILABLE",
            message="Database connection failed",
            detail={"reason": reason},
        )
```

**handler 注册**: `main.py` 中 `app.add_exception_handler(ApiError, api_error_handler)`

### §7.4 错误码清单

| 错误码 | 触发 |
|---|---|
| `INDICATOR_NOT_FOUND` | `GET /api/indicator/{id}/...` 但 id 在 stg_observation 无对应 |
| `SOURCE_NOT_FOUND` | `GET /api/source/{id}` 但 source 不在 registry |
| `INVALID_UUID` | 路径参数非合法 UUID |
| `INVALID_DATE` | 日期格式错误 |
| `PAGE_SIZE_TOO_LARGE` | page_size > 500 |
| `DB_UNAVAILABLE` | 连接池耗尽 / DB 不可达 |
| `READ_ONLY_VIOLATION` | 客户端尝试写 (防护机制触发) |

---

## §8 OpenAPI 文档

FastAPI 默认提供：
- `/api/openapi.json` — OpenAPI 3.1 schema
- `/api/docs` — Swagger UI
- `/api/redoc` — ReDoc UI

**增强**：
- 每个 endpoint 加 `summary` / `description` / `response_description`
- 每个 Pydantic model 加 `model_config.json_schema_extra` (example)
- tag 分组: `health` / `indicators` / `sources` / `observations`

**示例 (FastAPI 自动生成 OpenAPI)**:
```yaml
/api/indicator/{id}/series:
  get:
    summary: Get time series for an indicator
    tags: [indicators]
    parameters:
      - name: id
        in: path
        required: true
        schema: {type: string, format: uuid}
    responses:
      '200':
        content:
          application/json:
            schema:
              $ref: '#/components/schemas/IndicatorSeriesResponse'
      '400': {...}
      '503': {...}
```

---

## §9 与 docs/10 数据层测试映射

### §9.1 docs/10 §2 测试 + S1.10 映射

| docs/10 测试 | S1.10 暴露的端点 | 验证方式 |
|---|---|---|
| §2.1 单位白名单 (unit in allowed_units) | `/api/indicator/{id}/series` 返回 unit 字段 | integration test: 已知 indicator unit 在白名单 |
| §2.2 省级求和 = 全国 | `/api/indicator/{id}/series?geo_entity_id=...` | 客户端聚合测试 (S1.10+ 客户端写) |
| §2.3 YoY 一致性 | `/api/indicator/{id}/series?period_start=...&period_end=...` | 同上 |
| §2.4 跨源一致性 | `/api/source/{id}/coverage` + `/api/indicator/{id}/series` | 同上 |
| §2.5 时间序列异常 | 同 §2.3 | 同上 |
| §2.6 修订 append-only | `/api/observation/{id}` 返回所有 revisions | 客户端聚合测试 |
| §2.9 missing value = NULL + reason | `/api/indicator/{id}/series` 返回 value 字段 + 客户端检查 NULL | integration test |

**S1.10 范围**: 仅暴露原始数据 + 单位/confidence/source provenance 字段；**§2.2-2.6 客户端聚合测试不在 S1.10 本刀**（留待前端/客户端层）。

### §9.2 API 集成测试 (新)

| 测试名 | 验证 |
|---|---|
| `test_health_endpoint` | `/health` 返回 200 + `db_reachable=true` |
| `test_indicator_series_empty` | 未知 indicator → 200 + 空 series |
| `test_indicator_series_with_data` | 已知 indicator (试点数据) → 返回数据 |
| `test_indicator_series_pagination` | page_size=2 → 2 项 + has_next=true |
| `test_source_coverage` | 已知 source → 返回覆盖统计 |
| `test_invalid_uuid_returns_400` | `/api/indicator/not-a-uuid/series` → 400 |
| `test_db_unavailable_returns_503` | mock DB 失败 → 503 |
| `test_read_only_enforcement` | 尝试 INSERT via raw cursor → 抛 ReadOnlySqlTransaction |
| `test_openapi_schema_complete` | `/api/openapi.json` 包含所有 12 endpoints |

**总计**: ≥9 tests（tasking 要求 ≥4，按 docs/10 §2 子项扩展）。

---

## §10 测试策略

### §10.1 测试工具

- `httpx.AsyncClient` + FastAPI `TestClient`（同步测试）
- `TestClient(app=app)` 自动管理 lifespan (DB pool 创建/关闭)
- DB 连接 fixture: `psycopg2.connect(DSN)` + SAVEPOINT pattern (与 S1.8 测试一致)
- Mock: `monkeypatch.setattr(api.db, "Database", MockDatabase)` (for DB unavailable test)

### §10.2 测试 DB

- 使用 `cegr_test` DB (与 connector/monitor 测试一致)
- import_registry_csv (idempotent) + 可选 fixture 插入 sample observation rows
- **不引入 dbt run** 作为测试前置（避免依赖 dbt 环境）

### §10.3 跳过 OCR / dbt

- 本刀不测试 OCR 字段 (spike 仅在 dev 触发)
- 本刀不调 dbt run；直接读 `cegr_staging.int_indicator_timeseries` view (假设 S1.9 已 run 过)
- 测试 setup 显式说明: "需要 dbt run 至少一次" (CI 步骤)

---

## §11 配置 + 环境变量

| 变量 | 默认值 | 说明 |
|---|---|---|
| `CEGR_DSN` | (env) | PostgreSQL DSN (优先) |
| `DATABASE_URL` | (env) | Fallback DSN |
| `CEGR_API_DSN` | (env) | API-specific DSN override (rare) |
| `CEGR_API_POOL_MIN` | `2` | 连接池最小 |
| `CEGR_API_POOL_MAX` | `10` | 连接池最大 |
| `CEGR_API_CORS_ORIGINS` | `http://localhost:3000` | CORS 白名单 |
| `CEGR_API_LOG_LEVEL` | `INFO` | 日志级别 |

**profiles.yml.example 类似**: API 配置不入 git，仅 `.env.example`。

---

## §12 红线

| 红线 | 说明 |
|---|---|
| 不 Gate 1 PASS | 本刀不声称 Gate 1 通过 |
| 不 DSH | 不引入 DSH (Data Stage House) |
| 不批量爬取 | 不 HTTP 爬源站；不批量入库 |
| 不降 OCR | gate_thresholds.json 不改 |
| 不写 `cegr` 原表 | `SET TRANSACTION READ ONLY` 强制 |
| Cursor 不写 docs/24 正文 | CC 起草 |
| 不 Next.js | S1.10 是 backend only |
| profiles.yml 不入 git | .gitignore 排除 |

---

## §13 已知遗留

| 项 | 说明 | 处理 |
|---|---|---|
| 认证 / 授权 | S1.10 无 auth (内网部署；Stage 2 加) | 本刀不做 |
| Rate limiting | 无 (单节点；内网) | 本刀不做 |
| Caching | 无 (FastAPI 默认) | S1.10+ 加 Redis |
| WebSocket / SSE | 无 | 本刀不做 |
| GraphQL | 无 (REST only) | 本刀不做 |
| DTO 映射层 | 直接 psycopg2 row → Pydantic (无 ORM) | 接受 |
| 时间序列缓存 | 每次查询 PG | S1.10+ 加 Redis |
| dbt run 前置依赖 | 测试假设 dbt 已 run 至少一次 | CI 步骤补 |
| indicator / geo FK 解析 | S1.10 endpoint 仅返回 indicator_id / geo_entity_id；不解析为 name | S1.10+ 客户端 JOIN |
| 跨源一致性检查 | docs/10 §2.4 在客户端层 (S1.10+) | 本刀不做 |

---

## §14 引用

| 文档 | 说明 |
|---|---|
| `docs/08-mvp-plan.md` §2.1 | S1.10 任务定义 (W5, depends on S1.9, acceptance: `/api/indicator/{id}/series`) |
| `docs/02-target-architecture.md` | L5 API 层 (FastAPI + Uvicorn + Nginx); response 必带 source_id/vintage/confidence |
| `docs/10-acceptance-tests.md` §2 | 数据层测试 (2.1-2.6 + 2.9 Stage 1) |
| `docs/23-stage1-s19-dbt-staging-plan.md` | dbt staging schema (int_indicator_timeseries / int_source_coverage) |
| `docs/22-stage1-s18-ingest-run-monitoring-plan.md` | S1.8 监控 (DB session 模式参考) |
| `75-stage1-s10-fastapi-planning-tasking` | 本刀任务书 |