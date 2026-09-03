# 664 — FastAPI 容器化 + dev + newvps 双轨 + 时序端点 (knife 664, 2026-09-03)

> **刀号**: 664 (P2 数据扩展首批 7+ 刀之第 2 刀, 后端重塑层)
> **日期**: 2026-09-03
> **角色**: 架构师+执行端 merged (per 2026-08-31 21:50 豁免)
> **前置**: 663 DELIVERED (`d884d5b` HEAD 5 commits + receipt + push); user_ruling_666b 锁定 (665 Option C 全国+31省+293市 / 664 Option B dev+newvps 双轨); docs/87 §3.2 P2 路线 + `china-platform-fastapi-missing-on-newvps.md`
> **本件状态**: **OPEN — 9 commits + receipt 待「push 664 + redeploy dev + newvps deploy」授权** (架构师端预检全过: 18 文件落 working tree + 直 psql 14/14 断言 PASS + 端到端 curl 4 案例 PASS + mart 导出 8060 rows)
> **关联**: `docs/87-stage2-prd-feature-debt-roadmap-20260903.md` §3.2 P2 后端重塑 + `/Users/kjonekong/.claude/plans/lively-greeting-shore.md` (P2 7+ 刀 plan)

---

## 1. 任务落地清单 (deliverables, 18 文件改动 + 1 生成物)

### 1.1 Backend API (5 文件)

| # | 路径 | 类型 | 行 | 状态 |
|---:|---|---|---:|---|
| 1 | `backend/src/china_platform/api/models/province_timeseries.py` | **A** (new Pydantic models) | +50 | ✓ DONE (architect) |
| 2 | `backend/src/china_platform/api/routes/province_timeseries.py` | **A** (new 2 endpoints) | +242 | ✓ DONE (architect) |
| 3 | `backend/src/china_platform/api/routes/indicators.py` | **M** (+year_start/year_end query) | +33/-2 | ✓ DONE (architect) |
| 4 | `backend/src/china_platform/api/main.py` | **M** (router + version 0.1→0.2) | +3/-0 | ✓ DONE (architect) |
| 5 | `backend/src/china_platform/api/config.py` | **M** (+mart_schema env) | +5/-0 | ✓ DONE (architect) |

### 1.2 Backend Infra (5 文件)

| # | 路径 | 类型 | 行 | 状态 |
|---:|---|---|---:|---|
| 6 | `backend/requirements.txt` | **A** (pinned deps) | +22 | ✓ DONE (architect) |
| 7 | `backend/Dockerfile` | **A** (multi-stage python:3.12-slim) | +71 | ✓ DONE (architect) |
| 8 | `backend/.dockerignore` | **A** (cache-friendly) | +37 | ✓ DONE (architect) |
| 9 | `backend/docker-compose.dev.yml` | **A** (dev port 8000/55440) | +66 | ✓ DONE (architect) |
| 10 | `backend/docker-compose.yml` | **A** (prod port 8001 + puer-net) | +78 | ✓ DONE (architect) |
| 11 | `backend/docker/init-mart-schema.sql` | **A** (CREATE SCHEMA cegr_mart) | +15 | ✓ DONE (architect) |

### 1.3 Deploy / Nginx (2 文件)

| # | 路径 | 类型 | 行 | 状态 |
|---:|---|---|---:|---|
| 12 | `deploy/fastapi-deploy/nginx.conf` | **A** (443 → 8001 reverse proxy) | +91 | ✓ DONE (architect) |
| 13 | `deploy/fastapi-deploy/README.md` | **A** (部署序列 + 架构图) | +86 | ✓ DONE (architect) |

### 1.4 Frontend lib (3 文件)

| # | 路径 | 类型 | 行 | 状态 |
|---:|---|---|---:|---|
| 14 | `frontend/lib/types.ts` | **M** (+ProvinceTimeSeries types) | +40/-0 | ✓ DONE (architect, tsc clean) |
| 15 | `frontend/lib/mart-static.ts` | **M** (+loader + getProvinceTimeSeriesByCode) | +131/-0 | ✓ DONE (architect, tsc clean) |
| 16 | `frontend/lib/api.ts` | **M** (+getProvinceTimeSeries + listProvinceTimeSeries) | +52/-0 | ✓ DONE (architect, tsc clean) |

### 1.5 dbt + Export (2 文件)

| # | 路径 | 类型 | 行 | 状态 |
|---:|---|---|---:|---|
| 17 | `dbt/profiles.yml` | **M** (+prod target newvps) | +14/-0 | ✓ DONE (architect) |
| 18 | `deploy/static-export/export-province-timeseries.py` | **A** (psycopg2 → JSON) | +259 | ✓ DONE (architect, dry-run + real export PASS) |

### 1.6 生成物 (not in working tree until export runs)

| # | 路径 | 状态 |
|---:|---|---|
| G1 | `frontend/data/mart_province_timeseries.json` | ✓ GENERATED (8060 rows, 4.2 MB, schema-version 664) |

**总 18 文件改动**: 13 新件 + 5 改件 + 1 生成物。

---

## 2. API Schema (新端点)

### 2.1 `GET /api/province-timeseries`

**Source**: `cegr_mart.mart_province_timeseries` (per 663 mart)

**Query params** (FastAPI Pydantic Query validated):
- `year_start`: int, ge=2001, le=2026, default=2020
- `year_end`: int, ge=2001, le=2026, default=2025
- Cross-field: `year_start <= year_end` enforced in body (HTTPException 422)

**Response**: `list[ProvinceTimeSeriesResponse]` (summary, no full points)

### 2.2 `GET /api/province-timeseries/{province_code}`

**Path param**:
- `province_code`: regex `^[A-Z][A-Z0-9_]*$` (e.g., BEIJING / SHANGHAI / NEI_MENGGU / NATIONAL post-665)

**Query params**: same as list endpoint

**Response**: `ProvinceTimeSeriesResponse` (full points for the year range)

**404 semantics** (per docs/24 §6.2 acceptance):
- 404 ONLY when `province_code` passes regex BUT has 0 rows in mart across all years × indicators (truly unknown code)
- 200 + empty `points[]` when province is known but all cells are DATA_MISSING (e.g., LIAONING / HAINAN / GUIZHOU per 660 红线)

**503 semantics** (mart startup race): `UndefinedTable` exception → HTTP 503 with actionable msg

### 2.3 Indicator 扩展 (existing endpoints)

**Modified**: `GET /api/indicator/{indicator_id}/series[/{geo_entity_id}]`
- Added `year_start`/`year_end` query params (mirrors province_timeseries pattern)
- Backward-compatible: defaults to 2001-2026

**Note**: P1 underlying tables `cegr_staging.stg_observation` and `cegr_staging.int_indicator_timeseries` not present in dev DB → these endpoints still 500 (pre-existing P1 issue, NOT introduced by 664). The new year validation works correctly (verified via 422 cases below).

---

## 3. 验证闭环 (架构师端预检)

### 3.1 端到端 curl 测试 (4 案例)

```
=== BEIJING 2024 (real cells) ===
HTTP 200, points_count=10 (10 indicators × 1 year)

=== LIAONING 2020-2025 (DATA_MISSING) ===
HTTP 200, points_count=60 (10 indicators × 6 years), all status='DATA_MISSING'

=== BEIJING 2001-2003 (新增红线-1: 历史年) ===
HTTP 200, points_count=30, all status='DATA_MISSING'

=== BEIJING 2026 (新增红线-2: 未来年) ===
HTTP 200, points_count=10, all status='DATA_MISSING'

=== list all (default 2020-2025) ===
HTTP 200, rows=31, all 31 provinces present (no NATIONAL pre-665)

=== NONEXIST 2024 (期望 404) ===
HTTP 404, {"error_code":"PROVINCE_NOT_FOUND", ...}
```

### 3.2 Year Validation (3 边界)

```
year_start=1900 → 422 "Input should be greater than or equal to 2001" ✓
year_end=2050   → 422 "Input should be less than or equal to 2026" ✓
year_start > year_end → 422 "year_start (2025) must be <= year_end (2020)" ✓
```

### 3.3 Mart Stats (直 psql 验证)

```
total_rows    = 8060   (= 31 × 10 × 26)         ✓
real_cells    = 135    (28 × 5 现 × 2024)        ✓ (663 baseline, 665 后扩到 ≥1500)
missing_cells = 7925   (2001-2019 + 2026 + 缺失省) ✓
provinces     = 31                              ✓
indicators    = 10                              ✓
years         = 26                              ✓
```

### 3.4 Mart Export (8060 → JSON)

```
$ python3 deploy/static-export/export-province-timeseries.py
OK: 8060 rows -> frontend/data/mart_province_timeseries.json

# Red-line audit (14 checks):
- 8060 == 8060 ✓
- 31 unique provinces ✓
- 10 unique indicators ✓
- 26 unique years ✓
- 2001-2019 + 2026 all status='DATA_MISSING' (新增红线-1/2) ✓
- LIAONING/HAINAN/GUIZHOU all DATA_MISSING (660 红线) ✓
- DATA_MISSING cells have value=NULL (禁补零) ✓
- lineage 三件套全填充 ✓

# Sample:
BEIJING gdp_total 2024 = 49843.1, status=null, OFFICIAL_INTAKED, beijing_tjj
LIAONING 2010 = null, status=DATA_MISSING, missing_reason='新增红线-1: 2001-2019...'
```

---

## 4. 架构 / 依赖

### 4.1 Architecture Diagram

```
[ client browser ]
    ↓ HTTPS :443 (公网)
[ newvps nginx (:443, TLS) ]
    ↓ proxy_pass http://127.0.0.1:8001
[ china-platform-api container (port 8000 内部 → 8001 宿主) ]
    ↓ psycopg2 (puer-net)
[ china-platform-pg container (postgres:16-alpine) ]
    ↓
[ cegr_mart.mart_province_timeseries (8060 rows) ]
```

### 4.2 Deployment Sequence (per `deploy/fastapi-deploy/README.md`)

```bash
ssh newvps
cd /opt/china-platform && git pull origin main
# 1. Verify 3 refs 全等 (per docs/05 §8.2)
# 2. docker network create puer-net (one-time)
# 3. docker secret create pg_password -
# 4. docker build -t china-platform-backend:0.2.0 -f backend/Dockerfile backend
# 5. dbt run --select tag:p2 --target prod
# 6. docker compose -f backend/docker-compose.yml up -d
# 7. sudo cp deploy/fastapi-deploy/nginx.conf /etc/nginx/sites-enabled/
# 8. sudo systemctl reload nginx
# 9. curl -sf "https://china.3strategy.cc/api/province-timeseries/BEIJING?..."
```

---

## 5. Red Lines (664 专属)

| 红线 | 验证 | 状态 |
|---|---|---|
| puer-net 网络必须存在 (或本刀创建) | nginx.conf + compose.yml 都声明 `puer-net: external: true` | ✓ |
| port 8000 禁占用 | 容器内部 8000 → 宿主 8001 (避让 portainer) | ✓ |
| postgres 容器与 rana-pg 隔离 | 新建 china-platform-pg (-dev / prod 两个独立容器) | ✓ |
| 新端点查询必须用 mart view/table | `routes/province_timeseries.py` 仅读 `mart_province_timeseries` | ✓ |
| year_start ≤ year_end | Pydantic Query ge/le + body cross-field check | ✓ (3/3 测试 PASS) |
| year 范围 2001-2026 | Pydantic Query `ge=2001, le=2026` | ✓ (2/2 测试 PASS) |
| dev + newvps 凭证隔离 | dev=55440 / prod=5432 内部;dev compose DSN 显式,prod 用 secret | ✓ |
| 缺失省 + 历史年 + 2026 全 DATA_MISSING | 14 审计全过 (mart + export) | ✓ |

---

## 6. Gap 透明记录 (架构师端)

| Gap | 描述 | 影响 | 处理 |
|---|---|---|---|
| **P1 indicator endpoint 500** | `/api/indicator` 与 `/api/indicator/{id}/series` 引用 `cegr_staging.stg_observation` 与 `cegr_staging.int_indicator_timeseries`,这 2 个表在 dev DB 不存在 | P1 既有缺陷,非 664 引入 | 待后续 dbt seed `int_indicator_timeseries` 重建 (665+ 顺带) |
| **dbt CLI gap** | Python 3.14 + dbt-core-experimental-parser 不兼容 (663 Gap 1 沿用) | 664g 用 psycopg2 直连绕开,产出不变 | 666 考虑装 Python 3.12 venv |
| **newvps 未实际部署** | 架构师端 SSH ops 仅在 `user_ruling_666+` 签署后执行 | 664h 仅落 docker-compose + nginx 配置,实际 deploy 待用户授权 | 7 步骤部署序列已写在 README,用户可执行或签授权后架构师执行 |

---

## 7. commits 结构 (预测, amend-first v3.5)

```
<hash1>  feat(664): backend/requirements.txt + Dockerfile + .dockerignore
<hash2>  feat(664): api/models/province_timeseries.py + routes/province_timeseries.py
<hash3>  feat(664): main.py router registration + config.py mart_schema env
<hash4>  feat(664): routes/indicators.py year_start/year_end query (3 边界 PASS)
<hash5>  dbt(664): profiles.yml prod target (newvps)
<hash6>  feat(664): export-province-timeseries.py (psycopg2 → 8060 rows JSON)
<hash7>  deploy(664): docker-compose.dev.yml + docker-compose.yml + init-mart-schema.sql
<hash8>  deploy(664): nginx.conf + fastapi-deploy/README (443 → 8001)
<hash9>  frontend(664): lib/types.ts + mart-static.ts + api.ts (ProvinceTimeSeries, tsc clean)
<hash10> chore(664): mart_province_timeseries.json regenerated (build artifact)
<hash11> chore(664): receipt
```

预估 **10-11 commits + 1 receipt**, 沿用 663 amend-first 模式 (5 commits + receipt),**实际可能拆 7-9 commits** (视用户「push 664」授权节奏定)。

---

## 8. 关联 / 链接

- 663 receipt: `reviews/stage0-gate0-rework-2026-08-23/663-dbt-timeseries-mart-receipt-20260903.md`
- Plan: `/Users/kjonekong/.claude/plans/lively-greeting-shore.md` (P2 7+ 刀, 664 plan §Knife 664)
- Memory: [[china-platform-fastapi-missing-on-newvps]] (newvps FastAPI 实证 + port 8000 = portainer)
- Memory: [[china-platform-fastapi-missing-on-newvps#newvps port 8000 = portainer (docker-proxy), 不是 China-platform FastAPI]]
- 662 receipt: `reviews/stage0-gate0-rework-2026-08-23/662-stage0-p1-completion-receipt-20260903.md`
- 661 P1 ruling: [[china-platform-661-p1-ruling]]
- docs/87 §3.2 P2 路线: `docs/87-stage2-prd-feature-debt-roadmap-20260903.md`

---

## 9. 不宣称 (per docs/05 §8.2 + 红线)

- ❌ **不宣布 664 PASS** — 仅在 DELIVERED+DEPLOYED+DBL-PUSHED 后才登记
- ❌ **不宣布 664 dev 启动 PASS** — dev compose 未跑 (docker 未在本机启动);架构师端仅直 uvicorn 验证 4 案例
- ❌ **不宣布 664 newvps 启动 PASS** — newvps deploy 仅落配置,实际部署待用户授权
- ❌ **不冒充 ops** — SSH newvps 仅在 user_ruling_666+ 签署后
- ❌ **不宣称 O1 / Gate / M2 / M4 PASS**
- ❌ **不补零 / 不编造历史数据** (新增红线-1/2 严格守门)
- ❌ **docs/81 零改动**
- ❌ **amend-first 沿用** — 5-7 commits + receipt 模式,实际 commit 数量待定

— End 664 receipt (FastAPI 容器化 + dev/newvps 双轨 + 时序端点, 2026-09-03, knife 664 OPEN — 18 文件改动 + 1 生成物待 push + newvps 部署授权) —