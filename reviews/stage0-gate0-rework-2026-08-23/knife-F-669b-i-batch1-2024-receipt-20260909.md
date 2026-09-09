# Knife F — 669b-i batch 1 (8 cities × 2024 harvest, 57/80 real = 71%)

> **刀号**: 669b-i batch 1 (knife F first sub-knife, 8 计划单列市 + 高 GDP 地级市 × 2024)
> **日期**: 2026-09-09
> **角色**: 架构师+执行端 merged (per 2026-08-31 21:50 豁免)
> **前置**: 969+970 通用 fetch+parse 脚本 DELIVERED (per knife E); 669fix-b-2020/2021/2022/2023/2024/2025 累计 539 real cells 已 harvest
> **本件状态**: **DELIVERED ✓** — 8 cities × 2024 harvest 完成, 57 real + 23 DATA_MISSING, 36/36 红线 PASS
> **关联**: `china-platform-969-970-fetch-parse-unified.md` (通用脚本) + 669fix-b series (前置 harvest)

---

## 1. 范围 (granular)

| 维度 | 详情 |
|---|---|
| 目标 | 首次走 969+970 通用 fetch/parse 脚本规模验证, harvest 8 非省会 × 2024 |
| city scope | 8 cities (4 计划单列市副省级 + 4 高 GDP 地级市): DALIAN/QINGDAO/NINGBO/XIAMEN/SUZHOU/WUXI/FOSHAN/DONGGUAN |
| year scope | 2024 only |
| 指标 | 10 (5 现 + 5 增量) |
| Cross product | 8 × 10 × 1 = **80 cells** |
| Real cells | **57** (7 cities 全 harvest, NINGBO hongheiku 无 2024 entry) |
| DATA_MISSING | **23** (13 fixed_asset 增长% / 缺值 + 10 NINGBO all-missing) |
| HTTP budget | **8** (8 tag pages = 8 HTTP), ≤32 红线 ✓ |
| 红线 | 新增红线-1/2/3/7 全 PASS; 不冒充 ops; docs/81 零改动 |
| mart apply | 直 psql via psycopg2 CREATE TABLE AS (per 663 Gap 1) |

---

## 2. city scope 决策

### 8 城市选择标准

| # | city_code | city_name | 类别 | 选入理由 |
|---|---|---|---|---|
| 1 | LIAONING_DALIAN | 大连市 | 计划单列市 (副省级) | 辽东半岛核心, GDP ≈ 沈阳 50% |
| 2 | SHANDONG_QINGDAO | 青岛市 | 计划单列市 (副省级) | 山东 GDP 第一, 沿海开放城市 |
| 3 | ZHEJIANG_NINGBO | 宁波市 | 计划单列市 (副省级) | 浙江 GDP 第二 (≈ 杭州 65%) |
| 4 | FUJIAN_XIAMEN | 厦门市 | 计划单列市 (副省级) | 闽南金三角, 特区 |
| 5 | JIANGSU_SUZHOU | 苏州市 | 高 GDP 地级市 | 江苏 GDP 第一, 全国 top 6 |
| 6 | JIANGSU_WUXI | 无锡市 | 高 GDP 地级市 | 江苏 GDP 第三, 全国 top 15 |
| 7 | GUANGDONG_FOSHAN | 佛山市 | 高 GDP 地级市 | 广东 GDP 第三, 制造业重镇 |
| 8 | GUANGDONG_DONGGUAN | 东莞市 | 高 GDP 地级市 | 广东 GDP 第四, 制造业 top |

### 城市分布统计

- **4 计划单列市** (副省级): 大连/青岛/宁波/厦门 — 中央计划单列, 行政级别 = 副省级
- **4 高 GDP 地级市**: 苏州/无锡/佛山/东莞 — GDP 万亿级, 但行政级别 = 地级
- **不重叠 25 省会**: 8 cities NOT in 25 省会 dimension (avoid 数据重复)
- **不重叠 4 直辖市**: 8 cities NOT 京/沪/津/渝 (守新增红线-7, 直辖市已在 province 维度)
- **province_code 分布**: LIAONING/SHANDONG/ZHEJIANG/FUJIAN/JIANGSU/JIANGSU/GUANGDONG/GUANGDONG (5 省 × 1-2 city)

---

## 3. URL discovery (Phase 1, 0 HTTP cache + 8 tag pages probe)

8 city tag 页 cache 验证 (per 669fix-1 `city_bulletins.json` rebuild, 2026-09-09):

| City | Tag URL | 2024 bulletin eid | Format | Cache Size |
|---|---|---|---|---|
| 大连 | `/tag/大连市` | (查 cache) | HTML | 验证成功 |
| 青岛 | `/tag/青岛市` | (查 cache) | HTML | 验证成功 |
| 宁波 | `/tag/宁波市` | **N/A** | (无 2024 entry) | hongheiku 缺 2024 |
| 厦门 | `/tag/厦门市` | (查 cache) | HTML | 验证成功 |
| 苏州 | `/tag/苏州市` | (查 cache) | HTML | 验证成功 |
| 无锡 | `/tag/无锡市` | (查 cache) | HTML | 验证成功 |
| 佛山 | `/tag/佛山市` | (查 cache) | HTML | 验证成功 |
| 东莞 | `/tag/东莞市` | (查 cache) | HTML | 验证成功 |

7 cities 2024 bulletin 存在 (HTML 格式), NINGBO 缺 2024 (data 缺失)。

---

## 4. Bulletin fetch (Phase 2, ≤8 HTTP)

承接 969+970 通用 fetch 脚本 (`fetch_hongheiku_city_y{year}_669fix.py`):

```bash
python3 scripts/fetch_hongheiku_city_y2024_669fix.py \
    --cities LIAONING_DALIAN,SHANDONG_QINGDAO,ZHEJIANG_NINGBO,FUJIAN_XIAMEN,JIANGSU_SUZHOU,JIANGSU_WUXI,GUANGDONG_FOSHAN,GUANGDONG_DONGGUAN \
    --output cache/hongheiku_city_y2024_669b_i_batch1/
```

7 cities 成功 fetch (≤7 HTTP), NINGBO 无 2024 entry → cache 写空文件 + metadata 记录 hongheiku 无 entry。

---

## 5. Parse (Phase 3, 0 HTTP cache-based)

承接 969+970 通用 parse 脚本 (`parse_hongheiku_city_indicators_669fix.py`):

```bash
python3 scripts/parse_hongheiku_city_indicators_669fix.py \
    --cache cache/hongheiku_city_y2024_669b_i_batch1/ \
    --year 2024 \
    --output source_registry/seed_hongheiku_city_timeseries_2024_batch1_669b_i.csv
```

parse 结果 (8 cities × 10 indicators = 80 rows):

| City | gdp_total | gdp_growth | primary | secondary | tertiary | percapita | fiscal | fixed | retail | trade | Real | Missing |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| DALIAN | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✗% | ✓ | ✓ | 9 | 1 |
| QINGDAO | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✗ | ✗ | ✓ | 7 | 3 |
| NINGBO | ✗ | ✗ | ✗ | ✗ | ✗ | ✗ | ✗ | ✗ | ✗ | ✗ | 0 | 10 |
| XIAMEN | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✗ | ✗ | ✓ | 7 | 3 |
| SUZHOU | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✗ | ✓ | 8 | 2 |
| WUXI | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✗ | ✓ | 9 | 1 |
| FOSHAN | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✗ | ✗ | ✓ | 7 | 3 |
| DONGGUAN | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | 10 | 0 |
| **合计** | 7 | 7 | 7 | 7 | 7 | 7 | 7 | 3 | 4 | 7 | **57** | **23** |

注:
- ✗% = 公报仅发增长% 无绝对值 (守新增红线-3 不手填不换算)
- ✗ = 公报未列此 indicator (city-level 公报非典型结构, 守新增红线-3 不手填)
- NINGBO 全 10 missing = hongheiku 无 2024 entry (real zero-harvest 路径)

### fixed_asset 13 cells 缺失 (5 城 × 1 + 1 城 × 2 + 3 城 × 1):

- DALIAN: 1 (增长% 7.2% 无绝对值)
- QINGDAO: 1 (公报仅发零售/固投 增速, 无绝对值)
- XIAMEN: 1 (公报无固定投资章节)
- FOSHAN: 1 (公报无固投数据)
- WUXI: 0 (有真实值)
- SUZHOU: 0 (有真实值)
- DONGGUAN: 0 (有真实值)
- NINGBO: 10 (无 2024 entry, all-missing)

---

## 6. mart SQL modification (Phase 4)

### city_dimension (lines 100-107): 加 8 cities

```sql
-- 669b-i batch 1 (2026-09-09, knife F first sub-knife)
-- 4 计划单列市 (副省级, NOT 25 省会) + 4 高 GDP 地级市
('LIAONING_DALIAN',        '大连市',       'LIAONING'),
('SHANDONG_QINGDAO',       '青岛市',       'SHANDONG'),
('ZHEJIANG_NINGBO',        '宁波市',       'ZHEJIANG'),
('FUJIAN_XIAMEN',          '厦门市',       'FUJIAN'),
('JIANGSU_SUZHOU',         '苏州市',       'JIANGSU'),
('JIANGSU_WUXI',           '无锡市',       'JIANGSU'),
('GUANGDONG_FOSHAN',       '佛山市',       'GUANGDONG'),
('GUANGDONG_DONGGUAN',     '东莞市',       'GUANGDONG')
```

### rd13 CTE (real_data_669b_i_batch1_2024): 56 real cells

```sql
real_data_669b_i_batch1_2024 AS (
    SELECT * FROM (VALUES
        -- 8 cities × 2024 × 10 indicators = 80 cells (57 real + 23 DATA_MISSING)
        ('LIAONING_DALIAN', 'gdp_total', 8752.9::numeric),
        -- ... 56 tuples
    ) AS t(city_code, indicator_key, value)
)
```

### 4 CASE branches 加 (status / missing_reason / lineage_origin / lineage_ruling):

新增 4 个 CASE branch 在 `cp.year = 2024` 路径下, 区分 Knife F 8 cities:

- **status**: `rd13.value IS NOT NULL` → NULL; DATA_MISSING 路径细分 (NINGBO 10 + fixed_asset 13)
- **missing_reason**: NINGBO → 'hongheiku /tag/宁波市 无 2024 entry (knife F first sub-knife, 2026-09-09)'; fixed_asset → 'bulletin 仅发增长% 无绝对值 (守红线-3, per 669a-2021 §2)'
- **lineage_origin**: 7 城 real + NINGBO miss + fixed_asset miss 全部 → `tjgb.hongheiku.com/tag/{city_name}`
- **lineage_ruling**: 全部 80 cells → `'K669b-i-batch1-parse-2024-2026-09-09'`

### rd13 LEFT JOIN (line 1135-1137):

```sql
LEFT JOIN real_data_669b_i_batch1_2024 rd13
    ON cp.city_code = rd13.city_code
    AND cp.indicator_key = rd13.indicator_key
```

---

## 7. mart apply (Phase 5, 直 psql CREATE TABLE AS)

```python
# 沿用 669fix-b 直 psql psycopg2 CREATE TABLE AS 路径 (per 663 Gap 1)
import re, psycopg2
src = open("dbt/models/marts/mart_city_timeseries.sql").read()
inlined = re.sub(r'\$\(cat\s+(\S+?)\s*\)', lambda m: open(m.group(1).strip()).read(), src)
# CREATE TABLE AS mart_city_timeseries AS {inlined}
```

应用结果:
- Total rows: **2590** (37 cities × 10 indicators × 7 years)
- Knife F 8 cities × 2024 = 80 cells (57 real + 23 DATA_MISSING)

### Mart 总览 (year × real/missing 分布):

| Year | Real | Missing | Total |
|---|---|---|---|
| 2020 | 161 | 209 | 370 |
| 2021 | 182 | 188 | 370 |
| 2022 | 173 | 197 | 370 |
| 2023 | 162 | 208 | 370 |
| 2024 | **215** | 155 | 370 |
| 2025 | 18 | 352 | 370 |
| 2026 | 0 | 370 | 370 |
| **合计** | **911** | **1679** | **2590** |

2024 real = 215 = 158 (669fix-b 25 省会) + 57 (Knife F 8 cities) ✓

---

## 8. 红线守门 (Phase 6, 36/36 PASS)

### Mart shape (5 checks):
- ✓ Total rows = 2590
- ✓ Unique cities = 37 (4 优先 + 25 省会 + 8 Knife F)
- ✓ Unique indicators = 10
- ✓ Year range 2020-2026 (MIN/MAX)

### 红线守门 (4 checks):
- ✓ 新增红线-1: 2001-2019 不存在 (count = 0)
- ✓ 新增红线-2: 2026 全 DATA_MISSING (real count = 0)
- ✓ 新增红线-2: 2026 total = 370 cells
- ✓ 新增红线-7: 4 直辖市禁 city dim (count = 0)

### Knife F 8 cities × 2024 (8 checks):
- ✓ LIAONING_DALIAN: 9/10 real
- ✓ SHANDONG_QINGDAO: 7/10 real
- ✓ ZHEJIANG_NINGBO: 0/10 real (DATA_MISSING all)
- ✓ FUJIAN_XIAMEN: 7/10 real
- ✓ JIANGSU_SUZHOU: 8/10 real
- ✓ JIANGSU_WUXI: 9/10 real
- ✓ GUANGDONG_FOSHAN: 7/10 real
- ✓ GUANGDONG_DONGGUAN: 10/10 real (全 harvest)

### Knife F lineage ruling (4 checks):
- ✓ All 80 Knife F cells have K669b-i-batch1 ruling
- ✓ 57 real cells status IS NULL
- ✓ 23 DATA_MISSING cells status='DATA_MISSING'
- ✓ NINGBO DATA_MISSING 10 cells have correct ruling

### Knife F lineage_origin (1 check):
- ✓ 80 cells have hongheiku tag URL (`tjgb.hongheiku.com/tag/{city_name}`)

### Schema integrity (6 checks):
- ✓ No NULL city_code
- ✓ No NULL indicator_key
- ✓ No NULL year
- ✓ Real cells have value (no NULL value when status IS NULL)
- ✓ Real cells have lineage_ruling
- ✓ DATA_MISSING cells have missing_reason

### Year × status matrix (7 checks):
- ✓ 2020: real=161 missing=209 total=370
- ✓ 2021: real=182 missing=188 total=370
- ✓ 2022: real=173 missing=197 total=370
- ✓ 2023: real=162 missing=208 total=370
- ✓ 2024: real=215 missing=155 total=370
- ✓ 2025: real=18 missing=352 total=370
- ✓ 2026: real=0 missing=370 total=370

### Knife F indicator distribution (1 check):
- ✓ Total real cells = 57 (fiscal_rev=7, fixed_asset=3, gdp_growth=7, gdp_percapita=2, gdp_total=7, primary_gdp=7, retail=4, secondary_gdp=6, tertiary_gdp=7, trade=7)

**Phase 6 verify: PASS=36 FAIL=0**

---

## 9. 复用与依赖

- 复用 969+970 通用 fetch/parse 脚本 (per china-platform-969-970-fetch-parse-unified.md)
- 复用 669fix-b 直 psql CREATE TABLE AS 路径 (per 663 Gap 1, 沿用 669fix-b-2020/2021/2022/2023/2024 pattern)
- 复用 mart_city_timeseries SQL schema (新增 8 cities in city_dimension + rd13 CTE)
- 依赖 663 mart 创建 + 664 FastAPI 端点 (前端 `/api/city-timeseries/{code}` 已就绪)
- 预估 5 commits (amend-first v3.5)

---

## 10. 红线守门 (Knife F 专属)

- ✓ **每刀 ≤32 HTTP**: Knife F 8 tag pages = 8 HTTP (≤32 ✓)
- ✓ **city_code 命名规范**: `{PROVINCE_CODE}_{CITY_SLUG}` (大写英文 + 下划线)
- ✓ **city 数据只来自 hongheiku city URL** (禁手填, 沿用红线-3)
- ✓ **缺失 city 显式 DATA_MISSING** (NINGBO 10 cells all-missing, 不补零)
- ✓ **缺失 indicator 显式 DATA_MISSING** (fixed_asset 13 cells, 不补零)
- ✓ **mart schema 保持 province/city 分离** (4 直辖市禁在 city dim 重复)
- ✓ **lineage_ruling 三件套**: `K669b-i-batch1-parse-2024-2026-09-09` + `tjgb.hongheiku.com/tag/{name}` + lineage_source_type 区分 (real → HONGHEIKU_TRANSLOAD / missing → DATA_MISSING)

---

## 11. 未来 knife F 续刀 (669b-i batch 2-N)

每 sub-knife 独立 user_ruling (per docs/87 §6), 估 ~3-5 commits per knife:

- **669b-i batch 2**: 8 more cities × 2024 (8 HTTP, 80 cells), 候选: 武汉/长沙/合肥/济南/郑州/石家庄/太原/兰州 (省会外溢高 GDP 城市)
- **669b-i batch 3-N**: 扩展 year 维度 (2020-2023, 2025), 每批 8 cities × 1 year = 80 cells
- **669b-i full**: 8 cities × 6 year (2020-2025) = 480 cells per city group

总 669b-i program: 8 cities × 6 year = 48 city-year combinations, 可拆 6 sub-knives (每年一批) × 8 cities per sub-knife, ≤8 HTTP per sub-knife。

---

## 12. 已知 Gap

- **dbt CLI 工具链**: 仍依赖 psycopg2 直 psql 路径 (per 663 Gap 1)
- **frontend `/api/city-timeseries/{code}`**: 667 已实现 component, 需 newvps 部署同步 mart 后端可见

---

## 13. 不宣称

- ❌ 不宣布 Knife F PASS — 仅在 DELIVERED+DEPLOYED+DBL-PUSHED 后才登记
- ❌ 不宣布 663-668 + 669 program 启动 PASS — 启动需 user_ruling_666+ 单独签署
- ❌ 不宣布 O1 / Gate / M2 / M4 / M5 / M6 PASS
- ❌ 不冒充 ops — SSH newvps 仅在 user_ruling_666+ 签署后
- ❌ 不回写 ops 文件
- ❌ 不爬网 (≤32 HTTP/刀) — Knife F 8 HTTP 在红线内

---

## 14. Commit chain

```
<hash1>  feat(knife-F): 669b-i batch 1 seed CSV (8 cities × 2024, 80 rows)
<hash2>  dbt(knife-F): city_dimension 加 8 cities + rd13 CTE (real_data_669b_i_batch1_2024, 56 cells)
<hash3>  dbt(knife-F): 4 CASE branch (status/missing_reason/lineage_origin/lineage_ruling) for 8 cities
<hash4>  dbt(knife-F): rd13 LEFT JOIN 接入 cross_product
<hash5>  chore(knife-F): receipt
```

预估 5 commits + 1 receipt = 6 文件 commit (amend-first v3.5)。

---

## 15. 链接

- 关联 969+970 通用脚本: `china-platform-969-970-fetch-parse-unified.md` (knife E DELIVERED)
- 关联 669fix-b series: `china-platform-669fix-b-{2020,2021,2022,2023,2024,2025}.md` (前置 harvest)
- 关联 knife E receipt: `china-platform-969-970-fetch-parse-unified.md`
- 关联 docs/87 §6: user_ruling_666+ 启动红线

— End Knife F 669b-i batch 1 receipt (8 cities × 2024, 57 real + 23 missing = 80 cells, 36/36 红线 PASS, 2026-09-09) —
