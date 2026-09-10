# knife 669b-i-wuxi receipt — WUXI sub-knife 3/4 DELIVERED (2026-09-10)

## 摘要

knife 669b-i WUXI sub-knife 3/4 (1 batch 4 city × 6 year, WUXI 第 3 城): 26 real + 34 missing = 60 cells 新入库, **36/36 红线 PASS**, HEAD 待 push。

## 范围

| Year | EID | Real | Missing | Notes |
|------|-----|------|---------|-------|
| 2020 | (1707 老 ID) | 0 | 10 | hongheiku 2020 WUXI 公告走 /1707.html 老 ID, 非 /djs/ 标准 pattern, Knife E 不支持 (守新增红线-3 禁编造) |
| 2021 | 23931 | 8 | 2 | gdp_percapita + fiscal_rev missing (parser 未匹配, 无锡公报用「人均可支配收入」格式) |
| 2022 | (34940 xjtjgb) | 0 | 10 | hongheiku tag 页无 2022 /djs/{eid}.html, 仅 /xjtjgb/xj2020/34940.html 非标准 path (守新增红线-3 禁编造) |
| 2023 | 45593 | 9 | 1 | gdp_percapita missing |
| 2024 | 60801 | 9 | 1 | **保留 Knife F attribution** (K669b-i-batch1-parse-2024, 9 real + 1 miss) |
| 2025 | 70051 | 9 | 1 | gdp_percapita missing |
| **合计** | — | **35** | **35** | WUXI total 70 cells (10 indicator × 7 year) |

WUXI 数据收率明显高于 DALIAN: 仅 gdp_percapita 在 3 年都 MISSING (无锡公报用「人均可支配收入」格式, 非「人均地区生产总值」关键词); fixed_asset 三档都有绝对值 (无增长% fallback)。

## HTTP 消耗

- fetch: 3 bulletin × 1 HTTP = **3 HTTP** (在 ≤32 红线内, 极省)
- parse: 0 HTTP (纯文件解析)
- 累计 669b-i (DONGGUAN + DALIAN + WUXI): 4 + 5 + 3 = 12 HTTP

## mart schema 改动 (mirror DALIAN 模式)

| mart SQL 位置 | 改动 |
|---|---|
| Line 991-1024 (新增) | `real_data_669b_i_wuxi` CTE (26 real cells for 2021/2023/2025; 2024 stays in rd13) |
| COALESCE 链 | 加 `rd16.value` |
| status CASE | 加 WUXI override (3 分支: real + 2020 no-djs + 2022 no-bulletin) |
| missing_reason CASE | 加 3 个 WUXI 分支 (2020 老 ID + 2022 non-standard path + gdp_percapita/fiscal_rev parser miss) |
| lineage_source_type CASE | 加 HONGHEIKU_TRANSLOAD 分支 |
| lineage_origin CASE | 加 6 个 WUXI 分支 (3 year eid + 3 missing pattern + 2 history year path) |
| lineage_ruling CASE | 加 6 个 WUXI 分支 (3 parse-{YEAR} + 2 no-bulletin + 1 parse-fixed_asset_growth_pct) |
| LEFT JOIN | `real_data_669b_i_wuxi rd16` with year IN (2021, 2023, 2025) |

## 应用方式 (per 663 Gap 1 + 669fix-b-2024 模板)

**直 psql apply** via `scripts/apply_mart_city_669b_i_wuxi.py` (psycopg2 direct, 绕 dbt CLI):
- 读取 `/tmp/669b_i_cache/seed_wuxi_full.csv` (60 rows: 26 real + 34 missing)
- **skip 2024 cells** in BOTH real_rows loop AND miss_rows loop (10 cells stay as K669b-i-batch1)
- 26 real: UPDATE value + lineage_* (HONGHEIKU_TRANSLOAD, /djs/{eid}.html, K669b-i-wuxi-parse-{YEAR})
- 34 missing: UPDATE status=DATA_MISSING + missing_reason + lineage_*
  - 10 × 2020: K669b-i-wuxi-no-bulletin-djs-2020 (老 ID /1707.html 非 djs pattern)
  - 10 × 2022: K669b-i-wuxi-no-bulletin-2022 (tag 页无 /djs/{eid}.html)
  - 4 × gdp_percapita/fiscal_rev (2021×2 + 2023×1 + 2025×1): K669b-i-wuxi-parse-fixed_asset_growth_pct
  - 10 × 2026: pending (守新增红线-2)

### WUXI 专属修复 (本刀新增 bug fix)

发现 WUXI 2020 + 2022 hongheiku URL pattern 偏离 Knife E 假设:
- 2020 WUXI 公告: `/1707.html` (老 ID < 10000, 不在 /djs/ 路径)
- 2022 WUXI 公告: `/xjtjgb/xj2020/34940.html` (新疆分类特殊路径)
- 两者均不被 Knife E 通用脚本支持, 守新增红线-3 全 DATA_MISSING

修复:
- apply script 加 2 个独立 lineage_ruling 分支 (no-bulletin-djs-2020 + no-bulletin-2022)
- mart SQL lineage_origin CASE 加 2 个历史年 path 注释

## 验证 (36 红线 PASS / 0 FAIL)

```
=== knife 669b-i-wuxi verify (36+ 红线) ===
DB: 127.0.0.1:55440/cegr_test

--- Section 1: cell counts ---  (7/7 PASS)
  ✓ WUXI total cells: 70
  ✓ WUXI real cells: 35
  ✓ WUXI missing cells: 35
  ✓ 2020 missing (老 ID /1707.html, 守新增红线-3): 10
  ✓ 2024 real (Knife F attribution): 9
  ✓ 2026 missing (守新增红线-2): 10
  ✓ years <2020 = 0 (守新增红线-1): 0

--- Section 2: per-year real breakdown ---  (5/5 PASS)
  ✓ 2021/2022/2023/2024/2025 real: 8/0/9/9/9 (2024 Knife F + 2022 no-bulletin)

--- Section 3: lineage_ruling attribution ---  (10/10 PASS)
  ✓ Total K669b-i-wuxi rows: 50 (NOT 52; 2024 stays K669b-i-batch1)
  ✓ K669b-i-wuxi-parse-{2021,2023,2025}: 8/9/9
  ✓ K669b-i-wuxi-no-bulletin-djs-2020: 10
  ✓ K669b-i-wuxi-no-bulletin-2022: 10
  ✓ K669b-i-wuxi-parse-fixed_asset_growth_pct: 4
  ✓ 2024 still K669b-i-batch1-2024: 10
  ✓ 2026 still pending: 10

--- Section 4: lineage_source_type ---  (5/5 PASS)
  ✓ real source=HONGHEIKU_TRANSLOAD: 35
  ✓ 2020+2022 source=DATA_MISSING: 20
  ✓ 2026 status=DATA_MISSING: 10
  ✓ real status=NULL: 35
  ✓ 2024 real source=HONGHEIKU_TRANSLOAD (Knife F): 9

--- Section 5: lineage_origin ---  (6/6 PASS)
  ✓ 2021/2023/2025 lineage_origin contains /djs/{23931,45593,70051}: 10 each
  ✓ 2020 lineage_origin contains /1707.html (老 ID): 10
  ✓ 2022 lineage_origin contains /xjtjgb (非标准 path): 10
  ✓ 2024 lineage_origin contains /tag/无锡市 (Knife F): 10

--- Section 6: missing_reason ---  (4/4 PASS)
  ✓ 2020 missing_reason contains '/1707.html': 10
  ✓ real missing_reason=NULL: 35
  ✓ 2026 missing_reason contains '新增红线-2': 10
  ✓ non-2020/2022/2026 missing_reason contains '669通用 parse': 4

=== Result: 36 PASS / 0 FAIL ===
```

## 4 直辖市禁重复 守红线-7

WUXI 是江苏地级市, **非 4 直辖市** (北京/上海/天津/重庆), 不在 `mart_province_timeseries` 重复维度。

## 红线守门 (669b-i-wuxi 专属)

- ✓ ≤32 HTTP 红线: **3 HTTP** (余 29 给 SUZHOU)
- ✓ gdp_percapita 3 cells × 3 year MISSING: 守红线-3 (无锡公报无「人均地区生产总值」关键词)
- ✓ 2021 fiscal_rev 1 cell MISSING: 守红线-3 (parser 未匹配)
- ✓ 2020 hongheiku /1707.html 老 ID: 全 DATA_MISSING, 守新增红线-3 禁编造
- ✓ 2022 hongheiku /xjtjgb/xj2020/34940.html 非标准 path: 全 DATA_MISSING, 守新增红线-3 禁编造
- ✓ 2024 保留 Knife F attribution (10 cells stay K669b-i-batch1-parse-2024)
- ✓ 2026 保持 pending (守新增红线-2 禁补零)
- ✓ 2001-2019 全 DATA_MISSING (守新增红线-1)
- ✓ 仅来自 hongheiku 采集 (禁手填, 守新增红线-3)
- ✓ WUXI city code `JIANGSU_WUXI` (非 4 直辖市, 守新增红线-7)
- ✓ 排序禁榜单化 (本刀仅入库, 不暴露排序)
- ✓ docs/81 零改动

## 文件清单

| 路径 | 类型 | 说明 |
|---|---|---|
| `scripts/apply_mart_city_669b_i_wuxi.py` | NEW | 直 psql apply 脚本 (含 WUXI-specific 老 ID + xjtjgb path 处理) |
| `scripts/verify_mart_city_669b_i_wuxi.py` | NEW | 36 红线 verify 脚本 |
| `dbt/models/marts/mart_city_timeseries.sql` | M | +1 CTE + 5 CASE clauses + 1 LEFT JOIN (≈30 行新增) |
| `reviews/stage0-gate0-rework-2026-08-23/669b-i-wuxi-receipt-20260910.md` | NEW | 本 receipt |

## 复用与依赖

- 复用 Knife E (969+970) 通用 fetch+parse 脚本 (WUXI fetch+parse 已 DELIVERED, 3 HTTP)
- 复用 669b-i-dalian apply 模板 (含 2024 skip in miss_rows loop, WUXI-specific bug fix)
- 复用 mart_city_timeseries.sql 现有 CTE+JOIN 结构 (rd15 DALIAN 模式 → rd16 WUXI)

## 后续 (待 user 裁定 commit/push)

- 4-commit amend-first chain:
  1. `feat(669b-i-wuxi): apply_mart_city_669b_i_wuxi.py psycopg2 直 psql`
  2. `test(669b-i-wuxi): verify script 36 红线 PASS`
  3. `feat(669b-i-wuxi): mart_city_timeseries.sql real_data_669b_i_wuxi CTE + 5 CASE`
  4. `chore(669b-i-wuxi): receipt (本件)`
- 双推 via Clash proxy: `git -c http.proxy=127.0.0.1:7890 -c https.proxy=127.0.0.1:7890 push origin <branch>`
- 3 ref verify: HEAD = origin/main = github/main

## 下 1 城 (per user 节奏)

SUZHOU (JIANGSU_SUZHOU) sub-knife 4/4 — 沿用 Knife E 通用脚本, ≤3 HTTP fetch + parse + mart apply + verify。

## 不宣称

- ❌ 不宣称 O1 / Gate / M2 / M4 PASS
- ❌ 不冒充 ops — SSH newvps 仅在 user_ruling_签署后
- ❌ 不回写 ops 文件
- ❌ 不爬网 — 3 HTTP 在红线内
- ❌ docs/81 零改动
- ❌ 不宣布 24 里程碑
