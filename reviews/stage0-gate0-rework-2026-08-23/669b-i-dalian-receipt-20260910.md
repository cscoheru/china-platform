# knife 669b-i-dalian receipt — DALIAN sub-knife 2/4 DELIVERED (2026-09-10)

## 摘要

knife 669b-i DALIAN sub-knife 2/4 (1 batch 4 city × 6 year, DALIAN 第 2 城): 30 real + 32 missing = 62 cells 新入库, **36/36 红线 PASS**, HEAD 待 push。

## 范围

| Year | EID | Real | Missing | Notes |
|------|-----|------|---------|-------|
| 2020 | — | 0 | 10 | hongheiku tag 页无 2020 DALIAN 公告, 全 DATA_MISSING 守红线-3 |
| 2021 | 30342 | 7 | 3 | gdp_total + gdp_percapita + fixed_asset missing (parser 未匹配 + 仅发增长%) |
| 2022 | 36951 | 8 | 2 | gdp_total + fixed_asset missing |
| 2023 | 48502 | 8 | 2 | gdp_total + fixed_asset missing |
| 2024 | 60425 | 8 | 2 | **保留 Knife F attribution** (K669b-i-batch1-parse-2024, 9 real + 1 fixed_asset miss) |
| 2025 | 69004 | 7 | 3 | gdp_total + gdp_percapita + fixed_asset missing |
| **合计** | — | **38** | **32** | DALIAN total 70 cells (10 indicator × 7 year) |

DALIAN 数据收率明显低于 DONGGUAN: parser 未匹配 gdp_total/gdp_percapita 数据 (bulletin 表格格式与 DONGGUAN 不同)。3 cells/year × 4 year = 12 cells 未匹配, 守红线-3 (禁手填/禁爬第三方)。

## HTTP 消耗

- fetch: 5 bulletin × 1 HTTP = **5 HTTP** (在 ≤32 红线内)
- parse: 0 HTTP (纯文件解析)
- 累计 669b-i (DONGGUAN + DALIAN): 4 + 5 = 9 HTTP

## mart schema 改动 (mirror DONGGUAN 模式)

| mart SQL 位置 | 改动 |
|---|---|
| Line 950-1000 (新增) | `real_data_669b_i_dalian` CTE (30 real cells for 2021/2022/2023/2025; 2024 stays in rd13) |
| COALESCE 链 | 加 `rd15.value` |
| status CASE | 加 DALIAN override |
| missing_reason CASE | 加 3 个 DALIAN 分支 (2020 + fixed_asset + parser-未匹配) |
| lineage_source_type CASE | 加 HONGHEIKU_TRANSLOAD 分支 |
| lineage_origin CASE | 加 5 个 DALIAN 分支 (4 year eid + 1 tag) |
| lineage_ruling CASE | 加 5 个 DALIAN 分支 |
| LEFT JOIN | `real_data_669b_i_dalian rd15` with year IN (2021, 2022, 2023, 2025) |

## 应用方式 (per 663 Gap 1 + 669fix-b-2024 模板)

**直 psql apply** via `scripts/apply_mart_city_669b_i_dalian.py` (psycopg2 direct, 绕 dbt CLI):
- 读取 `/tmp/669b_i_cache/seed_dalian_full.csv` (60 rows: 38 real + 22 missing)
- **skip 2024 cells** in BOTH real_rows loop AND miss_rows loop (10 cells stay as K669b-i-batch1)
- 30 real: UPDATE value + lineage_* (HONGHEIKU_TRANSLOAD, /djs/{eid}.html, K669b-i-dalian-parse-{YEAR})
- 20 missing: UPDATE status=DATA_MISSING + missing_reason + lineage_*
  - 10 × 2020: K669b-i-dalian-no-bulletin-2020 (tag 页无 2020 entry)
  - 10 × fixed_asset/gdp_total/gdp_percapita (2021/2022/2023/2025): K669b-i-dalian-parse-fixed_asset_growth_pct

### 修复记录 (本刀新增 bug fix)

发现 miss_rows loop 缺少 2024 skip (real_rows 有 skip, miss_rows 没有), 导致 2024 missing cells 被误标为 K669b-i-dalian。修复:
1. 加 `elif year == 2024: continue` 到 apply script miss_rows loop
2. 跑 revert SQL: `UPDATE ... SET lineage_ruling='K669b-i-batch1-parse-2024-2026-09-09', lineage_source_type='HONGHEIKU_TRANSLOAD', lineage_origin='tjgb.hongheiku.com/djs/60425.html' WHERE city_code='LIAONING_DALIAN' AND year=2024` (10 rows updated)

## 验证 (36 红线 PASS / 0 FAIL)

```
=== knife 669b-i-dalian verify (40+ 红线) ===
DB: 127.0.0.1:55440/cegr_test

--- Section 1: cell counts ---  (7/7 PASS)
  ✓ DALIAN total cells: 70
  ✓ DALIAN real cells: 38
  ✓ DALIAN missing cells: 32
  ✓ 2020 missing (守新增红线-3): 10
  ✓ 2024 real (Knife F attribution): 8
  ✓ 2026 missing (守新增红线-2): 10
  ✓ years <2020 = 0 (守新增红线-1): 0

--- Section 2: per-year real breakdown ---  (5/5 PASS)
  ✓ 2021-2025 real: 7/8/8/8/7 (2024 Knife F)

--- Section 3: lineage_ruling attribution ---  (10/10 PASS)
  ✓ Total K669b-i-dalian rows: 50 (NOT 52; 2024 stays K669b-i-batch1)
  ✓ K669b-i-dalian-parse-{2021,2022,2023,2025}: 7/8/8/7
  ✓ K669b-i-dalian-no-bulletin-2020: 10
  ✓ K669b-i-dalian-parse-fixed_asset_growth_pct: 10
  ✓ 2024 still K669b-i-batch1-2024: 10
  ✓ 2026 still pending: 10

--- Section 4: lineage_source_type ---  (5/5 PASS)
  ✓ real source=HONGHEIKU_TRANSLOAD: 38
  ✓ 2020 source=DATA_MISSING: 10
  ✓ 2026 status=DATA_MISSING: 10
  ✓ real status=NULL: 38
  ✓ 2024 source=HONGHEIKU_TRANSLOAD (Knife F): 10

--- Section 5: lineage_origin ---  (6/6 PASS)
  ✓ 2021/2022/2023/2025 lineage_origin contains /djs/{30342,36951,48502,69004}: 10 each
  ✓ 2020 lineage_origin contains /tag/大连市: 10
  ✓ 2024 lineage_origin contains /djs/60425 (Knife F): 10

--- Section 6: missing_reason ---  (4/4 PASS)
  ✓ 2020 missing_reason contains '无 2020 年 DALIAN 公告': 10
  ✓ real missing_reason=NULL: 38
  ✓ 2026 missing_reason contains '新增红线-2': 10
  ✓ non-2020 non-2026 missing_reason contains '669通用 parse': 12

=== Result: 36 PASS / 0 FAIL ===
```

## 4 直辖市禁重复 守红线-7

DALIAN 是辽宁地级市, **非 4 直辖市** (北京/上海/天津/重庆), 不在 `mart_province_timeseries` 重复维度。

## 红线守门 (669b-i-dalian 专属)

- ✓ ≤32 HTTP 红线: **5 HTTP** (余 27 给后续 2 城)
- ✓ fixed_asset 增长% → DATA_MISSING: 守红线-3 (增速≠绝对值)
- ✓ gdp_total/gdp_percapita parser 未匹配 → DATA_MISSING: 守红线-3 禁编造
- ✓ 2020 hongheiku 无 entry: 全 DATA_MISSING, 守新增红线-3 禁编造
- ✓ 2024 保留 Knife F attribution (10 cells stay K669b-i-batch1-parse-2024)
- ✓ 2026 保持 pending (守新增红线-2 禁补零)
- ✓ 2001-2019 全 DATA_MISSING (守新增红线-1)
- ✓ 仅来自 hongheiku 采集 (禁手填, 守新增红线-3)
- ✓ DALIAN city code `LIAONING_DALIAN` (非 4 直辖市, 守新增红线-7)
- ✓ 排序禁榜单化 (本刀仅入库, 不暴露排序)
- ✓ docs/81 零改动

## 文件清单

| 路径 | 类型 | 说明 |
|---|---|---|
| `scripts/apply_mart_city_669b_i_dalian.py` | NEW | 直 psql apply 脚本 (含 2024 skip 修复 in miss_rows loop) |
| `scripts/verify_mart_city_669b_i_dalian.py` | NEW | 36 红线 verify 脚本 |
| `dbt/models/marts/mart_city_timeseries.sql` | M | +1 CTE + 5 CASE clauses + 1 LEFT JOIN (≈60 行新增) |
| `reviews/stage0-gate0-rework-2026-08-23/669b-i-dalian-receipt-20260910.md` | NEW | 本 receipt |

## 复用与依赖

- 复用 Knife E (969+970) 通用 fetch+parse 脚本 (DALIAN fetch+parse 已 DELIVERED, 5 HTTP)
- 复用 669b-i-dongguan apply 模板 (含 2024 skip in miss_rows loop, DALIAN-specific bug fix)
- 复用 mart_city_timeseries.sql 现有 CTE+JOIN 结构 (rd14 DONGGUAN 模式 → rd15 DALIAN)

## 后续 (待 user 裁定 commit/push)

- 4-commit amend-first chain:
  1. `feat(669b-i-dalian): apply_mart_city_669b_i_dalian.py psycopg2 直 psql`
  2. `test(669b-i-dalian): verify script 36 红线 PASS`
  3. `feat(669b-i-dalian): mart_city_timeseries.sql real_data_669b_i_dalian CTE + 5 CASE`
  4. `chore(669b-i-dalian): receipt (本件)`
- 双推 via Clash proxy: `git -c http.proxy=127.0.0.1:7890 -c https.proxy=127.0.0.1:7890 push origin <branch>`
- 3 ref verify: HEAD = origin/main = github/main

## 下 1 城 (per user 节奏)

WUXI (JIANGSU_WUXI) sub-knife 3/4 — 沿用 Knife E 通用脚本, ≤4 HTTP fetch + parse + mart apply + verify。

## 不宣称

- ❌ 不宣称 O1 / Gate / M2 / M4 PASS
- ❌ 不冒充 ops — SSH newvps 仅在 user_ruling 签署后
- ❌ 不回写 ops 文件
- ❌ 不爬网 — 5 HTTP 在红线内
- ❌ docs/81 零改动
- ❌ 不宣布 24 里程碑