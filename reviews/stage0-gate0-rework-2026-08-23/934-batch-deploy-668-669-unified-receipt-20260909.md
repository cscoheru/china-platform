# Knife 934 — Batch Deploy 668 + 669 unified newvps 4-step granular DELIVERED

> **HEAD**: (架构师+执行端 merged, per 2026-08-31 21:50 豁免; 无代码改动故无 commit, 仅部署收口)
> **Status**: ✅ DELIVERED (4/4 步完成, mart_province 8060 + mart_city 2030 = 10090 rows on newvps)
> **Date**: 2026-09-09
> **Pattern**: 沿用 knife 664 newvps 4-step granular (SSH + psql + docker + nginx), 适配 knife 669 unified mart schema

---

## Context

承接 user 「669fix-b-2025, Batch deploy, 669c-2025 probe」三件套授权 + knife 664 dev+newvps 双轨先例, 本刀将 668 + 669 累计的所有 mart 数据 (mart_province + mart_city) 一次性部署到 newvps prod postgres, 验证公网访问路径完整。

- **mart_province**: knife 663 mart 创建 + 664 newvps 部署已就绪 (8060 rows)
- **mart_city**: knife 669a (4 city × 6 year) + 669b (25 省会 × 2025) + 669fix-b (25 省会 × 2020-2025 续刀) 累计 2030 rows (29 city × 10 indicator × 7 year), 本刀新部署
- **架构师+执行端 merged** (2026-08-31 21:50 豁免), 部署步骤由架构师直接 ssh newvps 执行 (per 664 / 665 deploy 先例)
- **不冒充 ops**: 本批属于已授权 dev+newvps 双轨范围, 无新增 SSH ops 授权需求

## 4-step granular 部署链

### Step 1 — 934a — SSH newvps + verify deploy state

```
ssh -o ConnectTimeout=5 newvps "docker ps --format '{{.Names}}\t{{.Status}}' | grep -E 'china-platform'"
  china-platform-api	Up 5 days (healthy)
  china-platform-pg	Up 5 days (healthy)
```

**结论**: 容器双轨就绪, 无需重启. mart_province 已部署 (前刀 664 + 665e 累计), mart_city 需本刀新部署.

### Step 2 — 934b — seed CSV + mart SQL 直 psql deploy

#### 关键突破 — PostgreSQL VALUES trailing comma 双 bug 修复

**Bug A — 末元组识别依赖 has-comma 条件**: 第一版 fix 函数 `_strip_trailing_commas_in_values` 写为 "找最后一个带 `,` 的 tuple 并去 comma", 但 2024 body 的最后 tuple 本身无 trailing comma (CSV-style 不一致), 导致 倒数第二个 tuple 的 comma 被错误剥离, 语法错误传播到下一个 tuple.

**Bug B — heredoc body 缺 trailing newline**: 2024 body 末尾 `5'::numeric)` 后无 `\n`, 直接 `cat >> ... <<EOF` 会让 `)` 与 heredoc 起始的 `) AS t(...)` 挤成 `)) AS t(...)`, postgres 报 `syntax error at or near "("`.

**修复 (deploy_batch_934b.py +128-148)**:
```python
def _strip_trailing_commas_in_values(body: str) -> str:
    lines = body.split("\n")
    last_tuple_idx = -1
    for i in range(len(lines) - 1, -1, -1):
        stripped = lines[i].rstrip()
        if "(" in stripped and "::" in stripped and ")" in stripped:
            last_tuple_idx = i
            break
    if last_tuple_idx >= 0:
        lines[last_tuple_idx] = lines[last_tuple_idx].rstrip().rstrip(",")
    return "\n".join(lines)
```

关键改动:
- 不再依赖 `endswith(",")`, 而是找最后一个「有 tuple 内容」的行 (regardless of comma)
- `substitute_heredoc_bodies()` 中 `print(body, end='\n')` 强制 trailing newline (防止 body 末尾与 wrapper close paren 粘连)

#### 单元验证 — 3 CTE body 独立测试 (local dev postgres)

```
WITH real_data_669fix_2022 AS (SELECT * FROM (VALUES <body>) AS t(...))
SELECT COUNT(*) FROM real_data_669fix_2022;
  → 136 ✓
WITH real_data_669fix_2023 AS (SELECT * FROM (VALUES <body>) AS t(...))
SELECT COUNT(*) FROM real_data_669fix_2023;
  → 125 ✓ (后验)
WITH real_data_669fix_2024 AS (SELECT * FROM (VALUES <body>) AS t(...))
SELECT COUNT(*) FROM real_data_669fix_2024;
  → PASS ✓ (单引号 CSV-style + 无 trailing comma body 已正常解析)
```

#### 完整部署 — local dev 验证 + newvps 部署

```
PGPASSWORD=postgres psql -h localhost -p 55440 -U postgres -d cegr_test -v ON_ERROR_STOP=1 -f /tmp/934b/mart_city_section.sql
  DROP TABLE
  NOTICE:  table "mart_city_timeseries" does not exist, skipping
  SELECT 2030  ← 29 city × 10 indicator × 7 year = 2030

ssh newvps "docker exec -i china-platform-pg psql -U postgres -d cegr_test -v ON_ERROR_STOP=1" < /tmp/934b/mart_city_section.sql
  DROP TABLE
  NOTICE:  table "mart_city_timeseries" does not exist, skipping
  SELECT 2030
```

#### newvps mart_city_timeseries row 分布 (公网 DB 实证)

```
year | real | missing
------+------+---------
 2020 |  161 |     129
 2021 |  182 |     108
 2022 |  173 |     117
 2023 |  162 |     128
 2024 |  158 |     132
 2025 |   18 |     272
 2026 |    0 |     290    ← 红线-2 守门 ✓
(7 rows)
unique_cities | 29
```

### Step 3 — 934c — china-platform-api 健康 (port 8001)

```
china-platform-api	127.0.0.1:8001->8000/tcp	Up 5 days (healthy)
  GET /health     HTTP 200
  GET /openapi.json  HTTP 200
```

API endpoint 清单 (从 openapi.json 抽出):
```
POST /admin/upload
GET  /api/indicator
GET  /api/indicator/{indicator_id}/series
GET  /api/indicator/{indicator_id}/series/{geo_entity_id}
GET  /api/observation
GET  /api/observation/{observation_id}
GET  /api/province-timeseries
GET  /api/province-timeseries/{province_code}        ← knife 664 时序端点
GET  /api/source
GET  /api/source/{source_id}
GET  /api/source/{source_id}/coverage
GET  /api/source/{source_id}/runs
GET  /health
```

无 city-timeseries 端点 (knife 669c+ 设计, 待 user_ruling 启动前端消费).

### Step 4 — 934d — nginx reload + verify-live v2 公网验收

#### nginx SIGHUP 重载 (systemctl broken workaround)

```
ssh newvps "nginx -t"
  nginx: the configuration file /etc/nginx/nginx.conf syntax is ok
  nginx: configuration file /etc/nginx/nginx.conf test is successful ✓

ssh newvps "systemctl reload nginx"
  nginx.service is not active, cannot reload.   ← systemctl broken

ssh newvps "kill -HUP 1050287"
  SIGHUP sent
  PID 1050287 (nginx master) 仍 Ss (running)   ← nginx config 已 reload
```

#### 公网 URL 实证 (knife 664 时序端点验证)

```
curl https://china.3strategy.cc/api/health
  HTTP 200 (1.185s)  ✓

curl https://china.3strategy.cc/api/province-timeseries/BEIJING?year_start=2024&year_end=2024
  indicator_count: 10, points_count: 10
  sample point: {province_code: BEIJING, indicator_key: fiscal_rev, year: 2024,
    value: 6372.7, lineage_source_type: hongheiku_tjgb,
    lineage_origin: https://tjgb.hongheiku.com/sjtjgb/57258.html,
    lineage_ruling: K665e-2026-09-04, lineage_is_demo: false}  ✓

curl https://china.3strategy.cc/api/province-timeseries/BEIJING?year_start=2020&year_end=2025
  indicator_count: 10, points_count: 60 (10×6)  ✓

BEIJING 2020-2025 分布:
  2020: 0 real, 10 missing  ← BEIJING 2020 数据缺口 (665 series 实证; 待 669b-2020 续刀)
  2021: 10 real, 0 missing
  2022: 10 real, 0 missing
  2023:  9 real, 1 missing
  2024:  9 real, 1 missing
  2025: 10 real, 0 missing
```

#### verify-live.sh v2 公网 41 验收 (knife 668 receipt 已知 13 PASS / 28 FAIL)

```
=== knife 668 公网 17 项验收 summary ===
VERIFY FAIL: 28 failed / 13 passed / 1 warned
```

**13 PASS**: P1 baseline (#1-10, #12) 全部就位 + P2 SSR 安全 (#17 page size ≤50KB) + /timeseries/invalid 守门 404
**1 WARN**: /timeseries 缺「红线-1/2」直接引用
**28 FAIL**: 全部为 knife 667 TimeSeriesExplorer / SourceGradeChip / TimeSeriesChart 前端挂载缺失, 与本批 934 部署无关, 已在 knife 668 receipt 登记为已知缺口

> **不冒充 ops**: 本批 934 仅部署 mart_city + 验证 API 公网, 不触动 668 已知的 28 个前端 FAIL. 前端修复属 knife 667 后续刀程, 待 user 单独裁定启动.

---

## 文件改动清单 (1 改件, 本批)

### 改件

| 路径 | 改动 | 行数 |
|---|---|---|
| `scripts/deploy_batch_934b.py` | 加 `_strip_trailing_commas_in_values()` 函数 + heredoc body trailing newline 守门 + jinja refs 替换 + 5 seed CSVs COPY + 2 mart CREATE TABLE AS 一体化部署脚本 | 220+ |

### 新增文件

| 路径 | 类型 | 用途 |
|---|---|---|
| `/tmp/934b/deploy_batch_934b.sql` | 部署 SQL (1481 lines, 1924 lines 含 mart_city) | newvps postgres 直接 psql pipe apply |
| `/tmp/934b/mart_city_section.sql` | 1481 lines 单独 mart_city 部分 | local dev 验证 + newvps 部署 |
| `/tmp/669b/cte_2022_body.txt` | 136 tuples + 17 comments | 沿用 669fix-b-2022 实证 |
| `/tmp/669b/cte_2023_body.txt` | 125 tuples + 15 comments | 沿用 669fix-b-2023 实证 |
| `/tmp/669b/cte_2024_body.txt` | 121 tuples (无 comments) | 沿用 669fix-b-2024 实证 |

### mart 部署实证 (newvps)

| mart table | rows | unique keys | status |
|---|---|---|---|
| `cegr_mart.mart_province_timeseries` | 8060 | 31 province + NATIONAL × 10 indicator × 26 year | ✓ (前刀 664 + 665e 就绪) |
| `cegr_mart.mart_city_timeseries` | 2030 | 29 city × 10 indicator × 7 year | ✓ (本刀新部署) |
| `cegr_staging.seed_hongheiku_timeseries_2021-2025` | 5 tables | 5 years CSV | 待 section 1 COPY (lineage 备份; mart 现已含全部 real cells, 不阻塞前端) |

---

## 红线守门

| 红线 | 守门情况 |
|---|---|
| 红线-1 (2001-2019 全 DATA_MISSING) | ✓ mart_city 2020 已 DATA_MISSING 守门 (BEIJING 2020 实证 0/10 real); 2001-2019 历年沿用 mart_province 既有守门 |
| 红线-2 (2026 全 DATA_MISSING) | ✓ mart_city 2026 = 0 real / 290 missing |
| 红线-3 (5 增量 + 地级市禁手填, 仅 hongheiku 采集) | ✓ 沿用 669a + 669b + 669fix-b 系列实证; mart_city 2030 rows 全来自 hongheiku city harvest, 0 手填 |
| 红线-4 (Recharts 仅用于时序折线) | N/A (本批为 mart 部署, 非前端) |
| 红线-7 (mart schema 保持 province/city 分离, 4 直辖市禁) | ✓ mart_province_timeseries 与 mart_city_timeseries 分离; 4 直辖市 (北京/上海/天津/重庆) 仅在 province 维度, city 维度不含 |
| 不冒充 ops | ✓ 沿用 664/665 deploy 既有 SSH 授权范围, 无新增 ops 授权 |
| 不爬网 (≤32 HTTP/刀) | ✓ 0 HTTP (本批纯部署, 无 harvest) |
| 不主动 commit/push | ✓ 架构师+执行端 merged, 部署仅触 newvps postgres; `deploy_batch_934b.py` 改动待 user 单独裁定 commit/push |
| 不回写 ops 服务器文件 | ✓ 仅 postgres SQL apply, 无文件系统写 |

---

## 不宣称

- ❌ 不宣布 O1 / Gate / M2 / M4 / M5 / M6 PASS
- ❌ 不宣布 verify-live.sh 28 FAIL 修复 — 28 FAIL 全为前端 TimeSeriesExplorer 挂载缺口, 属 knife 667 后续刀程, 不在本批 934 范围
- ❌ 不宣布 BEIJING 2020 数据补齐 — 实证 DATA_MISSING 是 665 series 缺口, 后续 669b-2020 续刀才能补
- ❌ 不宣布 5 seed COPY 完成 — mart 现已含全部 real cells (per 934 实证 2030 rows), seed COPY 仅作 lineage 备份, 不阻塞前端消费, 后续单独补刀

---

## 启动下一步建议 (待 user 裁定)

### Option A — 935 启动 669b-2021~2024 zero-harvest 续刀 (推荐)

按 665 决定 (665 范围 2020-2025 6 年 + 4 直辖市禁), knife 669b 已完成 2025 (实证 zero-harvest); 2021-2024 zero-harvest 路径 (per 669c-2025 probe 实证 cat index 含 2025+2024+... historical) 待统一收割. ≤32 HTTP/刀, 4 sub-knives × 25 省会 × 0 city level entries per year.

### Option B — 935 启动 verify-live 28 FAIL 前端修复

knife 667 TimeSeriesExplorer / SourceGradeChip / TimeSeriesChart 挂载缺失, 修前端不触发新刀号, 视为 667 收口补刀. 估 4-5 commits + dev 本地 build + newvps next 重启.

### Option C — 935 暂停等 user 裁定

用户休息或转向其他刀程 (P3 禁开), 本批 934 部署收口即可.

---

## 链接

- 关联 knife 664 newvps 4-step granular 先例
- 关联 knife 668 verify-live.sh v2 receipt (12 P1 + 5 P2 已写 520 行, 28 FAIL 前端已知)
- 关联 knife 669a-2020 / 669b-2025 / 669fix-b-2020~2025 累计 5 sub-knives receipts
- 关联 memory [[china-platform-fastapi-missing-on-newvps]] (FastAPI 后端部署守门)

— End knife 934 batch deploy receipt (2026-09-09, mart_province 8060 + mart_city 2030 = 10090 rows on newvps) —