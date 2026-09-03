# deploy/fastapi-deploy/ — China Platform FastAPI production deployment (knife 664h)

Reverse proxy + Docker Compose artifacts for deploying FastAPI backend to newvps.

## Files

| File | Purpose | Deploy to |
|---|---|---|
| `nginx.conf` | TLS termination + reverse proxy 443 → 127.0.0.1:8001 | `/etc/nginx/sites-enabled/china-platform-api.conf` |
| `README.md` | This file | — |

## Deployment Sequence (per knife 664 plan §newvps 部署)

Per user_ruling_666 SSH ops authorization (2026-09-03 locked):

```bash
# 1. Verify 3 refs (assumes architect already pushed main)
ssh newvps
cd /opt/china-platform && git rev-parse HEAD
git rev-parse origin/main
git rev-parse github/main
# 期望: 3 hash 全等 (per docs/05 §8.2 三 ref 守门)

# 2. (One-time) Create puer-net docker network if missing
docker network ls | grep puer-net || docker network create puer-net

# 3. (One-time) Create docker secret for pg password
echo "$PG_PASSWORD" | docker secret create pg_password -

# 4. Build image (架构师端 docker build, 不主动 push)
cd backend
docker build -t china-platform-backend:0.2.0 -f Dockerfile .

# 5. dbt run — materialize mart in china-platform-pg (NOT cegr_staging)
cd ../dbt
.venv-dbt/bin/dbt run --select tag:p2 --target prod
# 期望: mart_province_timeseries (8060 rows) + _mart_models.yml accept_values

# 6. Start FastAPI + postgres containers
cd ../backend
docker compose -f docker-compose.yml up -d
# 期望: china-platform-pg + china-platform-api (port 8001)

# 7. Install nginx.conf (one-time)
sudo cp ../deploy/fastapi-deploy/nginx.conf /etc/nginx/sites-enabled/china-platform-api.conf
sudo nginx -t
sudo systemctl reload nginx

# 8. Verify
curl -sf "https://china.3strategy.cc/health" | jq .
curl -sf "https://china.3strategy.cc/api/province-timeseries/BEIJING?year_start=2024&year_end=2024" | jq '.points_count'
# 期望: 10 (10 indicators × 1 year)
```

## Key Constraints (per memory `china-platform-fastapi-missing-on-newvps`)

- **port 8000 = portainer** (NOT China-platform FastAPI). Use port 8001.
- **postgres**: `china-platform-pg` (this compose), NOT `rana-pg`.
- **puer-net**: docker network create BEFORE compose up; nginx + containers all attach.
- **nginx**: 443 → 127.0.0.1:8001 (NOT 8000).
- **CORS**: only `https://china.3strategy.cc` (no wildcard, no localhost in prod).

## Red Lines (664 专属)

- ✓ puer-net 网络必须存在 (或本刀创建);禁与 portainer 共用 default bridge
- ✓ port 8000 禁占用;FastAPI 容器用 8001
- ✓ postgres 容器与 rana-pg 隔离;新建 china-platform-pg
- ✓ CEGR_API_DSN 经 secret 注入,禁硬编码密码
- ✓ dev (55440) + prod (5432 内部) 两套 psql 凭证隔离
- ✓ nginx 反代禁用 wildcard CORS (per docs/24 §11.2)

## Rollback

```bash
# Disable nginx site (instant rollback to direct frontend if it serves static)
sudo rm /etc/nginx/sites-enabled/china-platform-api.conf
sudo systemctl reload nginx

# Stop containers (preserves postgres data)
cd /opt/china-platform/backend
docker compose -f docker-compose.yml down

# Full reset (postgres data LOST):
docker compose -f docker-compose.yml down -v
```

## Architecture Diagram

```
[ client browser ]
    ↓ HTTPS :443
[ newvps nginx (:443) ]
    ↓ proxy_pass http://127.0.0.1:8001
[ china-platform-api container (port 8000 inside → 8001 host) ]
    ↓ psycopg2 (puer-net)
[ china-platform-pg container (postgres:16-alpine) ]
    ↓
[ cegr_mart.mart_province_timeseries (8060 rows) ]
```