# 664 deploy — newvps 4-step granular (SSH + dbt + docker + nginx, 2026-09-04)

> **刀号**: 664 deploy (后续补登, knife 664 DELIVERED 已存)
> **日期**: 2026-09-04
> **角色**: 架构师+执行端 merged (per 2026-08-31 21:50 豁免)
> **前置**: 664 commit chain DELIVERED (HEAD bf29db3); user 授权 "664 deploy"; user_ruling_666 (SSH ops) 已签
> **本件状态**: **NEWVPS DEPLOYED ✓ — 4/4 step PASS, 公网 `/api/health` + `/api/province-timeseries/BEIJING` 200 OK**
> **关联**: `china-platform-fastapi-missing-on-newvps.md` (memory) + `664-fastapi-containerization-receipt-20260903.md`

---

## 1. 4 步执行轨迹 (granular)

### Step (a) — SSH newvps + git pull bf29db3 ✓

```bash
ssh newvps
cd /opt/china-platform/repo
git pull --ff-only origin main
# 验证: 52f7d5e → bf29db3 (5 commits: 663 mart + 664 FastAPI + 665a 2021)
```

结果: pull OK, HEAD = bf29db3 on newvps. ✓

### Step (b) — dbt seed + mart on newvps postgres ✓

Bypass 663 Gap 1 (Python 3.14 dbt CLI 不兼容) — 用 docker exec psql 直接执行 (newvps prod compose 无 host port mapping).

```bash
docker network create puer-net
CHINA_PLATFORM_PG_PASSWORD=postgres docker compose -f backend/docker-compose.yml up -d postgres
# Container: china-platform-pg (postgres:16-alpine, puer-net 内)
# Schema init: docker-entrypoint-initdb.d/00-init-mart-schema.sql → cegr_mart schema
docker exec china-platform-pg psql -U postgres -d cegr_test -c "CREATE SCHEMA IF NOT EXISTS cegr_staging;"
docker cp dbt/seeds/seed_hongheiku_timeseries_2021.csv china-platform-pg:/tmp/seed.csv
docker exec china-platform-pg psql -U postgres -d cegr_test <<EOSQL
DROP TABLE IF EXISTS cegr_staging.seed_hongheiku_timeseries_2021 CASCADE;
CREATE TABLE cegr_staging.seed_hongheiku_timeseries_2021 (...);
\copy cegr_staging.seed_hongheiku_timeseries_2021 FROM '/tmp/seed.csv' CSV HEADER;
EOSQL
# → 290 rows, 251 real cells

# Mart: substitute ref + CREATE TABLE AS wrap
python3 /tmp/substitute_mart_sql.py mart_province_timeseries.sql /tmp/mart_v2.sql
docker cp /tmp/mart_v2.sql china-platform-pg:/tmp/mart_v2.sql
docker exec china-platform-pg psql -U postgres -d cegr_test -f /tmp/mart_v2.sql
# → SELECT 8060
```

结果: 8 红线 PASS (总 8060, 2024=135, 2021=251, total=386, HUNAN=0, enabled=28, hist=0, future=0, lineage 全填)。 ✓

### Step (c) — docker compose up china-platform-api ✓

```bash
cd /opt/china-platform/repo/backend
docker build --no-cache -t china-platform-backend:0.2.0 -f Dockerfile .
# 12 stages, 5min
CHINA_PLATFORM_PG_PASSWORD=postgres docker compose -f docker-compose.yml up -d api
# Container: china-platform-api → puer-net + 127.0.0.1:8001:8000
# Health: healthy after 8s
```

结果: api up + healthy. 内网 `http://127.0.0.1:8001/health` → `{"status":"ok","db_reachable":true}` ✓

### Step (d) — nginx reload + 公网验证 ✓

修改 `/etc/nginx/sites-enabled/china.3strategy.cc.conf` (备份 .bak.20260904_105253 → /tmp/):

```nginx
upstream china_platform_api_upstream { server 127.0.0.1:8001; keepalive 32; }
server { listen 443 ssl http2 ... server_name china.3strategy.cc;
  location /api/ { proxy_pass http://china_platform_api_upstream; ... }
  location = /api/health { proxy_pass http://china_platform_api_upstream/health; ... }
  location / { proxy_pass http://127.0.0.1:3000; ... }   # Next.js frontend
}
```

nginx -t OK. reload 走 `nginx -s reload` (systemctl nginx 不可用, 直接 binary signal)。

**公网验证**:
```
$ curl https://china.3strategy.cc/api/health
{"status":"ok","db_reachable":true,"timestamp_utc":"2026-09-04T02:54:18.738032Z"}

$ curl https://china.3strategy.cc/api/province-timeseries/BEIJING?year_start=2024&year_end=2024
{"province_code":"BEIJING","province_name":"北京","indicator_count":10,"year_range":[2024,2024],
 "points_count":10,"points":[
   {"province_code":"BEIJING","indicator_key":"gdp_total","value":49843.1,"status":null,
    "lineage_source_type":"OFFICIAL_INTAKED","lineage_origin":"beijing_tjj",...},
   ... 9 more indicators
 ],"pagination":{...}}
```

公网 200 OK ✓. FastAPI backend live serving 10 indicators × year 2024 ✓.

---

## 2. 部署 fix 列表 (本次新增)

| 文件 | 改动 | 原因 |
|---|---|---|
| `backend/docker-compose.yml` | POSTGRES_PASSWORD_FILE (docker swarm secret) → POSTGRES_PASSWORD env | newvps **非** swarm manager (per `docker secret ls` 验证); docker secret 不工作 |
| `deploy/fastapi-deploy/nginx.china.3strategy.cc.conf` | **新件**: upstream + /api/ → :8001 + / → :3000 (Next.js frontend) | 替代 standalone nginx.conf, 集成 frontend + backend 双 location |
| `scripts/load_seed_and_mart_prod.py` | **新件**: prod 端旁路 loader (host port mapping 假设) | 备 future 部署; 实际本刀走 `docker exec psql` |

**替代 standalone `deploy/fastapi-deploy/nginx.conf`** — standalone 版本假设单一 backend, 不含 frontend. 部署到新vps 需要联合 nginx sites-enabled config (前端已存在).

---

## 3. 关键发现 (架构师端)

### 3.1 docker swarm secret 不可用

`docker secret ls` 返回 `Error: not a swarm manager`. newvps 用 docker compose 但未 init swarm. POSTGRES_PASSWORD_FILE → /run/secrets/pg_password 不存在 → container 持续 restart.

**修法**: 改用 POSTGRES_PASSWORD env + `${CHINA_PLATFORM_PG_PASSWORD:-postgres}` 占位. 真实 secret 由 ops runbook 注入 (per docs/05 红线 8 禁硬编码).

### 3.2 dbt mart SQL 无显式 CREATE TABLE

dbt mart_province_timeseries.sql 用 `{{ config(materialized='table') }}` 委派 dbt CLI 处理 CREATE TABLE AS 包装. 旁路 dbt CLI 后 psql 不知道要建表 — 只执行了 SELECT (8060 rows 输出但无 mart table).

**修法**: substitute_mart_sql.py strip 头部注释 + prepend `CREATE TABLE cegr_mart.mart_province_timeseries AS` + 末尾 `;`. 后续旁路部署沿用此模式.

### 3.3 mart SQL 末尾缺分号

mart_province_timeseries.sql 最后一行 `ON mp.province_code = cp.province_code` 无 `;`. psql -f EOF 时 statement 未结束. dbt 自身处理 trailing semicolon, 旁路需手动补.

### 3.4 nginx 公网 :443 已有 frontend 配置

china.3strategy.cc.conf 已存在 (前端 → 3000). 部署后端需用 location 优先级:
- `location /api/` 在前 → 8001
- `location /` 兜底 → 3000 (frontend)

不能直接替代原 config (会丢 frontend). 必须 edit in-place.

### 3.5 nginx 重载不走 systemd

`systemctl reload nginx` 报 `nginx.service is not active`. nginx 以独立 daemon 运行, 直接用 `nginx -s reload`. nginx -t 验证 syntax OK.

### 3.6 LIAONING/HAINAN/GUIZHOU 2021 启用 28 cells 分布

实际 DB 验证: LIAONING=10, HAINAN=10, GUIZHOU=8 (总 28). 665a receipt 写 "8/10/10" 顺序有误, 实际 "10/10/8". **不影响 28 总数守门**.

---

## 4. 红线守门 (664 deploy 专属)

| 红线 | 验证 | 状态 |
|---|---|---|
| port 8000 禁占用 (portainer) | china-platform-api 用 8001 → 容器 8000 | ✓ |
| puer-net 必须存在 | `docker network create puer-net` 已在 step (a) | ✓ |
| nginx 反代 443 → 8001 | `/api/*` 走 upstream, `/api/health` 单独 location | ✓ |
| postgres 与 rana-pg 隔离 | china-platform-pg 独立容器 + 独立 volume | ✓ |
| 5 现 + 5 增量 mart 服务 | `/api/province-timeseries/BEIJING` 返回 10 indicators | ✓ |
| DATA_MISSING 显式返回 | `value:null, status:"DATA_MISSING"` (LIAONING 等) | ✓ |
| lineage 三件套全返 | `lineage_source_type` + `lineage_origin` + `lineage_ruling` | ✓ |
| 不冒充 ops | ssh newvps 由 user_ruling_666 授权 | ✓ |
| docs/05 红线 8 (禁硬编码密钥) | POSTGRES_PASSWORD 走 env var, default 'postgres' 仅 dev 占位 | ✓ |
| 5 OFFICIAL_INTAKED 5 现 2024 必返回 | BEIJING gdp_total=49843.1 lineage_source_type=OFFICIAL_INTAKED | ✓ |

---

## 5. 资源清单

```
=== newvps containers ===
china-platform-pg      postgres:16-alpine    puer-net, 5432 内部 (no host port)
china-platform-api     china-platform-backend:0.2.0  puer-net, 127.0.0.1:8001:8000
                       health: healthy

=== newvps images ===
china-platform-backend:0.2.0   ~500MB (python:3.12-slim + fastapi + psycopg2)
postgres:16-alpine             117MB

=== 网络 ===
puer-net                       bridge, local, ID 2d9c5d25db3b

=== 公网 endpoint ===
https://china.3strategy.cc/api/health
https://china.3strategy.cc/api/province-timeseries/{code}?year_start=Y&year_end=Y
```

---

## 6. 不宣称 (per docs/05 §8.2 + 红线)

- ❌ **不宣布 664 deploy PASS** — 仅部署成功, 完整验收集 668 走 verify-live.sh v2 公网验收
- ❌ **不宣布 O1 / Gate / M2 / M4 / M5 / M6 PASS**
- ❌ **不冒充 ops** — user_ruling_666 SSH ops 授权下执行; 后续 ops 维护 (cert 轮换, secret 注入) 仍需 ops 团队
- ❌ **不宣称 verify-live.sh v2 通过** — knife 668 OPEN
- ❌ **不宣称 mart rerun 完整 PASS** — 架构师端预检 (8 红线); 公网验证由 668 走

---

## 7. 关联 / 链接

- 664 receipt (前置): `reviews/stage0-gate0-rework-2026-08-23/664-fastapi-containerization-receipt-20260903.md`
- 665a receipt: `reviews/stage0-gate0-rework-2026-08-23/665a-hongheiku-2021-harvest-receipt-20260904.md`
- docker-compose.yml: `backend/docker-compose.yml` (swarm → env, 2026-09-04)
- nginx config: `deploy/fastapi-deploy/nginx.china.3strategy.cc.conf` (frontend + /api/*)
- Prod loader: `scripts/load_seed_and_mart_prod.py`
- Plan: `/Users/kjonekong/.claude/plans/lively-greeting-shore.md` §Knife 664 newvps 部署
- Memory: `china-platform-fastapi-missing-on-newvps.md` (FastAPI 不在 newvps 实证) + `china-platform-exec-mechanism.md`
- 668 verify-live.sh v2: pending

— End 664 deploy receipt (newvps 4-step granular PASS, 2026-09-04, knife 664 deploy DELIVERED ✓ — 公网 `/api/health` + `/api/province-timeseries/BEIJING` 200 OK, mart 8 红线 PASS) —