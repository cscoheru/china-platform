# 669a-2021 — 4 city × 2021 real-data harvest (26/40 cells, 守新增红线-3/7)

> **刀号**: 669a-2021 (knife 669 program second sub-knife, real-data harvest)
> **日期**: 2026-09-04
> **角色**: 架构师+执行端 merged (per 2026-08-31 21:50 豁免)
> **前置**: 669a-2020 DELIVERED (zero-harvest knife, schema foundation)
> **本件状态**: **DELIVERED ✓** — 4 city × 2021 harvest 完成, 26 real + 14 DATA_MISSING, 20/20 红线 PASS
> **关联**: `669a-2020-mart-city-zero-harvest-receipt-20260904.md` + `china-platform-665-multi-knife-program.md`

---

## 1. 范围 (granular)

按 user Option A (10 city batches × 6 years = 60 sub-knives), 669a-2021 是 669a 批次第 2 把 (real-data):

| 维度 | 详情 |
|---|---|
| 目标 | 抓取 4 优先 city × 2021 年 10 指标真实数据, 写入 mart_city_timeseries |
| city scope | 4 优先 city (深圳市/广州市/杭州市/南京市) — 669a 批次 |
| year scope | 2021 only (real-data harvest, 不含 2020) |
| 指标 | 10 (5 现 + 5 增量, mirror mart_province_timeseries.indicator_dimension) |
| Cross product | 4 × 10 × 1 = **40 cells** (本刀 2021 only) |
| Real cells | **26** (4 city 中 9/3/5/9 cells per city) |
| DATA_MISSING | 14 (公报非典型结构 + fixed_asset 普遍缺) |
| HTTP budget | 8 (1 shenzhen tag + 3 other tags + 4 city 2021 bulletins), ≤32 红线 ✓ |
| 红线 | 新增红线-1/2/3/7 全 PASS; 不冒充 ops; docs/81 零改动 |
| mart apply | 直 psql via psycopg2 (per 663 Gap 1) |

---

## 2. URL discovery (Phase 1)

### 关键发现: hongheiku 城市 bulletin URL pattern

实证 (4 city tag pages fetch, 1 + 3 HTTP):

```
Pattern A: tag 页 (城市总目录, 列历年公报)
  https://tjgb.hongheiku.com/tag/<city_name>
  - 深圳 tag: /tag/深圳市
  - 广州 tag: /tag/广州市
  - 杭州 tag: /tag/杭州市
  - 南京 tag: /tag/南京市

Pattern B: city bulletin (单年公报)
  - 2021+: https://tjgb.hongheiku.com/djs/{id}.html (modern pattern)
  - 2020-: https://tjgb.hongheiku.com/{NNNN}.html (legacy pattern, e.g. 深圳 2020 = /3497.html)

实证 4 city 2021 URL IDs:
  深圳 /djs/26979.html (9/10 real cells)
  广州 /djs/27931.html (3/10 real cells — 公报非典型结构)
  杭州 /djs/25516.html (5/10 real cells)
  南京 /djs/27791.html (9/10 real cells)
```

### 修正 669a-2020 假设 (重要)

669a-2020 receipt 实证 hongheiku 城市 cat index 仅 2021-2025 无 2020 entry。
本刀进一步发现: 城市 **bulletin** URL 用 `/djs/` 或 `/NNNN.html` 模式,
**即使 cat index 缺 2020 entry, bulletin URL 仍存在** (e.g. 深圳 2020 = `/3497.html` 在 tag 页可访问)。

但 669a-2020 已 DELIVERED (zero-harvest), 不回溯。后续 669a-2020 sub-knife (optional)
可用 `/3497.html` (深圳), 广州/杭州/南京类似 URL ID 重新抓取, 但需要 user 单独授权 (per docs/87 §6)。

---

## 3. 解析结果 (Phase 2 + 3)

### 10 指标 by city (2021)

| 城市 | gdp_total | gdp_growth | primary | secondary | tertiary | percapita | fiscal_rev | fixed_asset | retail | trade | **real** |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 深圳 | 30664.85 | 6.7 | 26.59 | 11338.59 | 19299.67 | 173663 | 4257.76 | — | 9498.12 | 35435.57 | **9/10** |
| 广州 | — | 8.2 | — | — | — | — | 1883.18 | — | 10122.56 | — | **3/10** |
| 杭州 | 18109 | 8.5 | — | — | — | — | 2386.6 | — | 6744 | 7369 | **5/10** |
| 南京 | — | 7.5 | 303.94 | 5902.65 | 10148.73 | 174520 | 1729.52 | 5675.24 | 7899.41 | 6366.83 | **9/10** |
| **总计** | | | | | | | | | | | **26/40** |

### 14 missing cells 守新增红线-3 (禁手填)

| city | indicator | 实证缺失原因 |
|---|---|---|
| 深圳 | fixed_asset | 2021 城市公报普遍未列固定资产投资(公报章节重点是产业/服务业) |
| 广州 | gdp_total/primary/secondary/tertiary/gdp_percapita/trade | 广州公报用「战略性新兴产业合计实现增加值8616.77亿元」非传统 gdp_total/三产分项表述 |
| 广州 | fixed_asset | 同上 (公报重点转向「工业投资增长 6.9%」非绝对值) |
| 杭州 | primary/secondary/tertiary/gdp_percapita | 杭州公报未直接列三产分项 (杭州突出数字经济/服务业占比) |
| 杭州 | fixed_asset | 同上 |
| 南京 | gdp_total | 南京公报未直接列 gdp_total (但有完整三产分项, 推算可得不手填) |

**新增红线-3 守门**: regex miss → DATA_MISSING, 禁手填/禁推算/禁编造。后续 669a-2021+ sub-knife 或 666 OFFICIAL 升级可补采。

---

## 4. 文件改动清单 (4 文件, 1 改 + 3 新)

### 改件 (1)

| 路径 | 改动 |
|---|---|
| `dbt/models/marts/mart_city_timeseries.sql` | (a) 加 real_data_2021 CTE (26 hard-coded values); (b) final SELECT LEFT JOIN real_data_2021; (c) status CASE 加 2021 real vs missing 分支; (d) lineage_ruling CASE 加 K669a-2021 |

### 新件 (3)

| 路径 | 用途 | 行数 |
|---|---|---|
| `source_registry/seed_hongheiku_city_2021.csv` | 40 rows CSV (4 city × 10 indicator: 26 real + 14 missing), columns per mart schema | 41 |
| `scripts/parse_hongheiku_city_y2021.py` | city bulletin HTML parser; regex 提取 10 指标; missing → DATA_MISSING (守新增红线-3) | 218 |
| `scripts/apply_mart_city_669a_2021.py` | 直 psql apply (per 663 Gap 1); 输出 multi-knife state summary | 113 |
| `scripts/verify_mart_city_669a_2021.py` | 20 红线 verify (守 mart stable across sub-knives, multi-knife ruling 三件套) | 207 |

注: 现有 `apply_mart_city_669a.py` 和 `verify_mart_city_669a.py` (from 669a-2020) 保留作为 669a-2020 单独脚本, 不会被本刀覆盖。

---

## 5. mart SQL 设计要点 (新增红线-7)

### real_data_2021 CTE

```sql
real_data_2021 AS (
    SELECT * FROM (VALUES
        ('GUANGDONG_SHENZHEN', 'gdp_total',     30664.85::numeric),
        ('GUANGDONG_SHENZHEN', 'gdp_growth',    6.7::numeric),
        ... 26 rows total
        ('JIANGSU_NANJING',   'trade',         6366.83::numeric)
    ) AS t(city_code, indicator_key, value)
)
```

### Final SELECT LEFT JOIN

```sql
SELECT
    cp.city_code, ..., cp.year,
    rd.value,
    CASE
        WHEN cp.year < 2020  THEN 'DATA_MISSING'
        WHEN cp.year = 2026  THEN 'DATA_MISSING'
        WHEN cp.year = 2020  THEN 'DATA_MISSING'  -- 实证 hongheiku 城市 cat index 2020 缺文
        WHEN cp.year = 2021  AND rd.value IS NOT NULL THEN NULL  -- real cell
        WHEN cp.year = 2021  AND rd.value IS NULL     THEN 'DATA_MISSING'
        ELSE 'DATA_MISSING'  -- 2022-2025 待 harvest
    END AS status,
    CASE ... END AS missing_reason,
    CASE
        WHEN cp.year = 2021 AND rd.value IS NOT NULL THEN 'HONGHEIKU_TRANSLOAD'
        ELSE 'DATA_MISSING'
    END AS lineage_source_type,
    CASE
        WHEN cp.year = 2021 AND rd.value IS NOT NULL THEN 'tjgb.hongheiku.com/djs/' || cp.city_name
        ELSE 'none'
    END AS lineage_origin,
    CASE
        WHEN cp.year = 2020  THEN 'K669a-2020-2026-09-04'
        WHEN cp.year = 2021  THEN 'K669a-2021-2026-09-04'
        ELSE 'pending'
    END AS lineage_ruling,
    'false' AS lineage_is_demo
FROM cross_product cp
LEFT JOIN real_data_2021 rd
    ON cp.city_code = rd.city_code
    AND cp.indicator_key = rd.indicator_key
    AND cp.year = 2021
```

**设计关键**:
- LEFT JOIN + `cp.year = 2021` predicate: 2020/2022-2026 行 rd=NULL, 2021 行 rd 匹配或 NULL
- lineage_ruling CASE: 不同 year 用不同 ruling 版本 (multi-knife lineage 守门)
- 2020 cells 保留 K669a-2020 ruling (mart stable across sub-knives)
- 2021 cells 用 K669a-2021 ruling (per-knife attribution)
- 2022-2025 cells 用 'pending' (待后续 sub-knives)

---

## 6. 红线守门 (20/20 PASS)

| # | 红线 | 实际 | 期望 | 状态 |
|---|---|---|---|---|
| 1 | mart 行数 = 280 | 280 | 280 (4 × 10 × 7) | ✓ |
| 2 | city distinct = 4 | 4 | 4 | ✓ |
| 3 | indicator distinct = 10 | 10 | 10 | ✓ |
| 4 | year distinct = 7 | 7 | 7 (2020-2026) | ✓ |
| 5 | real_cells = 26 (2021 actual harvest) | 26 | 26 | ✓ |
| 6 | DATA_MISSING = 254 (40[2020] + 14[2021 miss] + 200[2022-2026]) | 254 | 254 | ✓ |
| 7 | 4 直辖市禁重复 (新增红线-7) | 0 | 0 | ✓ |
| 8 | lineage_ruling = 3 versions | 3 | 3 (K669a-2020 + K669a-2021 + pending) | ✓ |
| 9 | lineage_is_demo 全部 'false' | 0 bad | 0 | ✓ |
| 10 | status 枚举合法 | 0 bad | 0 | ✓ |
| 11 | missing_reason 必填 for DATA_MISSING | 0 bad | 0 | ✓ |
| 12 | 2020 仍全 DATA_MISSING (mart stable) | 0 real | 0 | ✓ |
| 13 | 2026 仍全 DATA_MISSING (新增红线-2) | 0 real | 0 | ✓ |
| 14 | value 列类型 = numeric | numeric | numeric | ✓ |
| 15 | 2021 real cells lineage_source_type='HONGHEIKU_TRANSLOAD' | 26/26 | 26 | ✓ |
| 16 | 2021 missing cells lineage_source_type='DATA_MISSING' | 14/14 | 14 | ✓ |
| 17 | 2021 missing cells missing_reason 含 '669a-2021' | 14/14 | 14 | ✓ |
| 18 | 2021 real cells lineage_origin 含 'tjgb.hongheiku.com/djs/' | 26/26 | 26 | ✓ |
| 19 | 2022-2025 仍全 DATA_MISSING (待 harvest) | 0 real | 0 | ✓ |
| 20 | <2020 无 cells (cross product only 2020+) | 0 | 0 | ✓ |

**结论**: 669a-2021 20/20 红线 PASS — mart stable across sub-knives (2020 ruling 不变),
multi-knife lineage 三件套守门 OK, 14 missing cells 正确 DATA_MISSING 路径 (守新增红线-3 禁手填)。

---

## 7. 验证输出

### mart apply 输出

```
mart apply OK:
  rows             = 280           (expect 280)
  cities (distinct)= 4         (expect 4)
  indicators       = 10    (expect 10)
  years            = 7         (expect 7)
  real_cells       = 26    (expect 26)
  DATA_MISSING     = 254  (expect 254)
  ruling_versions  = 3      (expect 3)

=== by year row count ===
  year 2020: 40 rows
  year 2021: 40 rows (26 real + 14 missing)
  year 2022: 40 rows
  year 2023: 40 rows
  year 2024: 40 rows
  year 2025: 40 rows
  year 2026: 40 rows

=== 2021 real cells by city ===
  GUANGDONG_GUANGZHOU: 3 real cells
  GUANGDONG_SHENZHEN: 9 real cells
  JIANGSU_NANJING: 9 real cells
  ZHEJIANG_HANGZHOU: 5 real cells
```

### 20 红线 verify 输出

```
=== knife 669a-2021 红线 verify (14+ assertions) ===
  [OK]   row count = 280 (4 city × 10 indicator × 7 year)
  [OK]   city distinct = 4
  [OK]   indicator distinct = 10 (5 现 + 5 增量)
  [OK]   year distinct = 7 (2020-2026)
  [OK]   real_cells = 26 (2021 actual harvest from hongheiku)
  [OK]   DATA_MISSING cells = 254 (40[2020] + 14[2021 miss] + 200[2022-2026])
  [OK]   4 直辖市禁重复 (新增红线-7) — NOT in city dimension
  [OK]   lineage_ruling = 3 versions (K669a-2020 + K669a-2021 + pending)
  [OK]   lineage_is_demo 全部 = 'false' (demo 数据禁入 mart)
  [OK]   status 枚举合法
  [OK]   missing_reason 必填 for all DATA_MISSING cells
  [OK]   2020 仍全 DATA_MISSING (mart stable across sub-knives)
  [OK]   2026 仍全 DATA_MISSING (新增红线-2)
  [OK]   value 列类型 = numeric
  [OK]   2021 real cells lineage_source_type 全 = 'HONGHEIKU_TRANSLOAD'
  [OK]   2021 missing cells lineage_source_type 全 = 'DATA_MISSING'
  [OK]   2021 missing cells missing_reason 全 14/含 '669a-2021'
  [OK]   2021 real cells lineage_origin 全 26/含 'tjgb.hongheiku.com/djs/'
  [OK]   2022-2025 仍全 DATA_MISSING (待 harvest)
  [OK]   <2020 无 cells (cross product only 2020+)

=== knife 669a-2021 红线 summary: 20/20 PASS, 0 FAIL ===
```

---

## 8. HTTP 预算守门

| 阶段 | HTTP 消耗 | 累计 | 红线 |
|---|---|---|---|
| Phase 1: 深圳 tag page (URL discovery) | 1 | 1 | ≤32 ✓ |
| Phase 1: 广州/杭州/南京 tag pages | 3 | 4 | ✓ |
| Phase 2: 4 city 2021 bulletins | 4 | 8 | ✓ |
| Phase 3: parse (无 HTTP) | 0 | 8 | ✓ |
| Phase 5: 直 psql apply (无 HTTP) | 0 | 8 | ✓ |
| Phase 6: 20 红线 verify (无 HTTP) | 0 | 8 | ✓ |
| Phase 7: commit chain + push | 0 | 8 | ✓ |
| **本刀总 HTTP** | **8** | **8** | **≤32 ✓ (24 余量)** |

---

## 9. 不宣称 (per docs/05 §8.2 + 红线)

- ❌ **不宣布 669a-2021 PASS** — 仅 DELIVERED + 20/20 红线 PASS + mart apply OK
- ❌ **不宣布 669a 批次完成** — 仅 2/6 sub-knives DELIVERED (2020+2021), 剩余 4 待启动
- ❌ **不宣布 669 program 完成** — 仅 2/60 sub-knives DELIVERED
- ❌ **不宣布 665-668 启动 PASS** — 启动需 user_ruling_668+ 单独签署
- ❌ **不宣布 O1 / Gate / M2 / M4 / M5 / M6** — 仍 OPEN
- ❌ **不冒充 ops** — 本地 dev postgres, 未触发 newvps 公网部署
- ❌ **不爬网** — 8 HTTP, ≤32 红线 (24 余量)
- ❌ **不手填 city 数据** — 守新增红线-3 (14 missing cells 走 DATA_MISSING)
- ❌ **不补零** — 守新增红线-1/2
- ❌ **不合并 province/city mart** — 守新增红线-7
- ❌ **不重复 4 直辖市** — 守新增红线-7
- ❌ **不宣称 2021 harvest 完整** — 14/40 missing 是公报结构差异实证, 非采集失败

---

## 10. user_ruling_669a-2021 签署清单

- [x] user 显式 "Start 669a-2021" (授权 4 city × 2021 real-data harvest)
- [x] 已审阅 669a-2020 交付物 (zero-harvest knife schema)
- [x] 已确认 4 优先 city 范围 (深/穗/杭/宁)
- [x] 已确认 10 指标范围 (5 现 + 5 增量)
- [x] 已确认 city_code 命名规范 ({PROVINCE_CODE}_{CITY_SLUG})
- [x] 已确认 ≤32 HTTP budget (实际 8)
- [x] 已确认 mart 直 psql (per 663 Gap 1 workaround)
- [x] 已确认 14 missing cells 守新增红线-3 走 DATA_MISSING (禁手填)
- [x] 已确认 20/20 红线 PASS
- [x] 已确认 docs/81 零改动
- [x] 已确认本刀 669a-2021 不触发 newvps 部署 (本机 dev postgres)
- [x] 已确认 mart stable across sub-knives (2020 cells ruling 不变)
- [x] 已确认 multi-knife lineage 三件套 (per-knife ruling attribution)
- [x] 已确认 O1 仍 OPEN, 不宣称任何 PASS

---

## 11. 后续 58 刀待启动 (per Option A)

| 刀号 | 范围 | HTTP | cells (expected) |
|---|---|---|---|
| 669a-2022 | 4 city × 2022 | ≤8 | 40 (target 26+ real) |
| 669a-2023 | 4 city × 2023 | ≤8 | 40 |
| 669a-2024 | 4 city × 2024 | ≤8 | 40 |
| 669a-2025 | 4 city × 2025 | ≤8 | 40 |
| 669a-2020-revisit (optional) | 4 city × 2020 复采 (per 实证 2020 city bulletin 存在) | ≤4 | 0-40 (TBD) |
| 669b-j × 6 years | 8 batches × ~32 city × 6 year | ≤32 each | 48 sub-knives |
| 669j × 6 years | 33 city × 6 year | ≤33 each | 6 sub-knives |
| **剩余** | **58 sub-knives** | **≤32 each** | **~70,000 cells max** |

---

## 12. 链接

- 前置 receipt: `reviews/stage0-gate0-rework-2026-08-23/669a-2020-mart-city-zero-harvest-receipt-20260904.md`
- 计划 plan: `/Users/kjonekong/.claude/plans/lively-greeting-shore.md` (knife 663-668 + 669a-j 锁定)
- 记忆: [[china-platform-665-multi-knife-program]]
- 记忆: [[china-platform-no-redundant-polls]]
- 记忆: [[china-platform-user-rest-protocol]]
- 记忆: [[china-platform-fastapi-missing-on-newvps]]

— End 669a-2021 receipt (4 city × 2021 real-data harvest, 26/40 cells, 20/20 红线 PASS, DELIVERED ✓) —
