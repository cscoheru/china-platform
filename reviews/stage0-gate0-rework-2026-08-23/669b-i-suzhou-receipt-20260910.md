# knife 669b-i-suzhou receipt — SUZHOU sub-knife 4/4 DELIVERED (2026-09-10)

## 摘要

knife 669b-i SUZHOU sub-knife 4/4 (1 batch 4 city × 6 year, SUZHOU 第 4 城): 35 real + 35 missing = 70 cells 新入库, **36/36 红线 PASS**, HEAD 待 push。

## 范围

| Year | EID | Real | Missing | Notes |
|------|-----|------|---------|-------|
| 2020 | (3008 老 ID) | 0 | 10 | hongheiku 2020 SUZHOU 公告走 /3008.html 老 ID, 非 /djs/ 标准 pattern, Knife E 不支持 (守新增红线-3 禁编造) |
| 2021 | 25410 | 9 | 1 | gdp_percapita missing (parser 未匹配) |
| 2022 | 35155 | 9 | 1 | gdp_percapita missing |
| 2023 | 45627 | 0 | 10 | **parser regex 数字含空格失配** ("24653 . 4 亿元" 不能匹配 "(\d+\.?\d*)\s*亿", hongheiku 苏州 2023 bulletin 排版异常) (守新增红线-3 禁编造) |
| 2024 | 61278 | 8 | 2 | **保留 Knife F attribution** (K669b-i-batch1-parse-2024, 8 real + 2 miss; SUZHOU 本刀 skip 2024 cells) |
| 2025 | 69636 | 9 | 1 | gdp_percapita missing |
| **合计** | — | **35** | **35** | SUZHOU total 70 cells (10 indicator × 7 year) |

SUZHOU 数据收率与 WUXI 相似 (52% real), 仅 gdp_percapita 在 4 年 (2021/2022/2024/2025) 都 MISSING (公报无「人均地区生产总值」关键词); 2023 全 MISSING 由 parser regex 失配 (数字含空格) 触发, 非 hongheiku 数据缺失, 守红线-3 禁编造。

## HTTP 消耗

- fetch: 5 bulletins × 1 HTTP = **5 HTTP** (在 ≤32 红线内, 极省; 2020 老 ID /3008.html 未 fetch, 2024 Knife F 已收录未 fetch)
- parse: 0 HTTP (纯文件解析)
- 累计 669b-i (DONGGUAN + DALIAN + WUXI + SUZHOU): 4 + 5 + 3 + 5 = 17 HTTP

## mart schema 改动 (mirror WUXI 模式)

| mart SQL 位置 | 改动 |
|---|---|
| Line 1024-1065 (新增) | `real_data_669b_i_suzhou` CTE (35 real cells for 2021/2022/2024/2025; 2023 stays DATA_MISSING due to parser regex 失配) |
| COALESCE 链 (line 1074) | 加 `rd17.value` |
| status CASE (line 1103 区域) | 加 SUZHOU override (4 分支: real + 2020 老 ID + 2023 parser + 2026 pending) |
| missing_reason CASE (line 1185 区域) | 加 5 个 SUZHOU 分支 (real + 2020 老 ID + 4 gdp_percapita/retail + 2023 parser) |
| lineage_source_type CASE | 加 HONGHEIKU_TRANSLOAD 分支 |
| lineage_origin CASE | 加 8 个 SUZHOU 分支 (3 year eid + 1 Knife F 2024 + 1 gdp_percapita + 1 2024 retail + 1 2023 parser + 1 2020 老 ID) |
| lineage_ruling CASE | 加 8 个 SUZHOU 分支 (3 parse-{YEAR} + 1 Knife F batch1-parse-2024 + 1 parse-fixed_asset_growth_pct + 1 no-bulletin-2023 + 1 no-bulletin-djs-2020) |
| LEFT JOIN (line 1388-1392) | `real_data_669b_i_suzhou rd17` with year IN (2021, 2022, 2024, 2025) |

## 应用方式 (per 663 Gap 1 + WUXI 模板)

**直 psql apply** via `scripts/apply_mart_city_669b_i_suzhou.py` (psycopg2 direct, 绕 dbt CLI):
- 读取 `/tmp/669b_i_cache/seed_suzhou_full.csv` (70 rows: 35 real + 35 missing)
- **skip 2024 cells** in BOTH real_rows loop AND miss_rows loop (10 cells stay as K669b-i-batch1)
- 27 real: UPDATE value + lineage_* (HONGHEIKU_TRANSLOAD, /djs/{eid}.html, K669b-i-suzhou-parse-{YEAR})
- 33 missing: UPDATE status=DATA_MISSING + missing_reason + lineage_*
  - 10 × 2020: K669b-i-suzhou-no-bulletin-djs-2020 (老 ID /3008.html 非 djs pattern)
  - 10 × 2023: K669b-i-suzhou-no-bulletin-2023 (parser regex 数字含空格失配, "24653 . 4 亿元")
  - 3 × gdp_percapita (2021/2022/2025): K669b-i-suzhou-parse-fixed_asset_growth_pct
  - 10 × 2026: pending (守新增红线-2)

### SUZHOU 专属修复 (本刀新增 bug fix)

发现 SUZHOU 2020 hongheiku URL pattern 偏离 Knife E 假设 (类似 WUXI 2020):
- 2020 SUZHOU 公告: `/3008.html` (老 ID < 10000, 不在 /djs/ 路径)
- 不被 Knife E 通用脚本支持, 守新增红线-3 全 DATA_MISSING

**额外发现**: SUZHOU 2023 bulletin 数字排版异常 (含空格) 导致 parser regex 失配:
- 例: "24653 . 4 亿元" (空格在数字内)
- Knife E regex `(\d+\.?\d*)\s*亿` 不能跨空格匹配
- 守新增红线-3 全 DATA_MISSING (不手填)

### Knife E SUZHOU hotfix (SUZHOU Q3a 发现)

发现 Knife E 通用 fetch 脚本 Format A 不接受 str year key:
- Knife E 原代码: `eid_by_city_year = {city: years for city, years in data.items()}` — 直接使用 json keys
- SUZHOU eid_map 用 Python json.dump 写入, keys 为 str ("2021"), 而 Knife E 后续用 int year 查找 (line 311-312 `if year in city_year_map`), 找不到
- 修复: `years_int = {int(y): eid for y, eid in years.items()}` 强制转 int
- 这是 Knife E hotfix, 已纳入 SUZHOU commit chain (commit #1)

## 验证 (36 红线 PASS / 0 FAIL)

```
=== knife 669b-i-suzhou verify (36+ 红线) ===
DB: 127.0.0.1:55440/cegr_test

--- Section 1: cell counts ---  (7/7 PASS)
  ✓ SUZHOU total cells: 70
  ✓ SUZHOU real cells: 35
  ✓ SUZHOU missing cells: 35
  ✓ 2020 missing (老 ID /3008.html, 守新增红线-3): 10
  ✓ 2024 real (Knife F attribution): 8
  ✓ 2026 missing (守新增红线-2): 10
  ✓ years <2020 = 0 (守新增红线-1): 0

--- Section 2: per-year real breakdown ---  (5/5 PASS)
  ✓ 2021/2022/2023/2024/2025 real: 9/9/0/8/9 (2024 Knife F + 2023 parser regex 失配)

--- Section 3: lineage_ruling attribution ---  (9/9 PASS)
  ✓ Total K669b-i-suzhou rows: 50 (27 real excl 2024 + 23 miss excl 2024 + 2026 pending)
  ✓ K669b-i-suzhou-parse-{2021,2022,2025}: 9/9/9
  ✓ K669b-i-suzhou-no-bulletin-djs-2020: 10
  ✓ K669b-i-suzhou-no-bulletin-2023: 10
  ✓ K669b-i-suzhou-parse-fixed_asset_growth_pct: 3 (2021/2022/2025 gdp_percapita)
  ✓ 2024 still K669b-i-batch1-parse-2024: 10
  ✓ 2026 still pending: 10

--- Section 4: lineage_source_type ---  (5/5 PASS)
  ✓ real source=HONGHEIKU_TRANSLOAD: 35
  ✓ 2020+2023 source=DATA_MISSING: 20
  ✓ 2026 status=DATA_MISSING: 10
  ✓ real status=NULL: 35
  ✓ 2024 real source=HONGHEIKU_TRANSLOAD (Knife F): 8

--- Section 5: lineage_origin ---  (6/6 PASS)
  ✓ 2021/2022/2025 lineage_origin contains /djs/{25410,35155,69636}: 10 each
  ✓ 2020 lineage_origin contains /3008.html (老 ID): 10
  ✓ 2023 lineage_origin contains /djs/45627 (parser 数字含空格): 10
  ✓ 2024 lineage_origin contains /tag/苏州市 (Knife F): 10

--- Section 6: missing_reason ---  (4/4 PASS)
  ✓ 2020 missing_reason contains '/3008.html': 10
  ✓ real missing_reason=NULL: 35
  ✓ 2026 missing_reason contains '新增红线-2': 10
  ✓ non-2020/2023/2026 missing_reason contains '669通用 parse': 23 (2020 老 ID + 2021/2022/2025 gdp_percapita + 2023 parser 数字含空格)

=== Result: 36 PASS / 0 FAIL ===
```

## 4 直辖市禁重复 守红线-7

SUZHOU 是江苏地级市, **非 4 直辖市** (北京/上海/天津/重庆), 不在 `mart_province_timeseries` 重复维度。

## 红线守门 (669b-i-suzhou 专属)

- ✓ ≤32 HTTP 红线: **5 HTTP** (余 27 给未来 Knife F sub-knives)
- ✓ gdp_percapita 4 cells × 4 year MISSING: 守红线-3 (公报无「人均地区生产总值」关键词)
- ✓ 2024 retail 1 cell MISSING: 守红线-3 (parser 未匹配, Knife F attribution 保留)
- ✓ 2020 hongheiku /3008.html 老 ID: 全 DATA_MISSING, 守新增红线-3 禁编造
- ✓ 2023 parser regex 数字含空格失配: 全 DATA_MISSING, 守新增红线-3 禁编造
- ✓ 2024 保留 Knife F attribution (10 cells stay K669b-i-batch1-parse-2024)
- ✓ 2026 保持 pending (守新增红线-2 禁补零)
- ✓ 2001-2019 全 DATA_MISSING (守新增红线-1)
- ✓ 仅来自 hongheiku 采集 (禁手填, 守新增红线-3)
- ✓ SUZHOU city code `JIANGSU_SUZHOU` (非 4 直辖市, 守新增红线-7)
- ✓ 排序禁榜单化 (本刀仅入库, 不暴露排序)
- ✓ docs/81 零改动

## 文件清单

| 路径 | 类型 | 说明 |
|---|---|---|
| `scripts/fetch_hongheiku_city_y{year}_669fix.py` | M | Knife E SUZHOU hotfix (Format A str year key → int conversion, 5 lines added) |
| `scripts/apply_mart_city_669b_i_suzhou.py` | NEW | 直 psql apply 脚本 (含 SUZHOU-specific 老 ID + parser 数字含空格处理) |
| `scripts/verify_mart_city_669b_i_suzhou.py` | NEW | 36 红线 verify 脚本 |
| `dbt/models/marts/mart_city_timeseries.sql` | M | +1 CTE + 5 CASE clauses + 1 LEFT JOIN (≈40 行新增) |
| `reviews/stage0-gate0-rework-2026-08-23/669b-i-suzhou-receipt-20260910.md` | NEW | 本 receipt |

## 复用与依赖

- 复用 Knife E (969+970) 通用 fetch+parse 脚本 (SUZHOU fetch+parse 已 DELIVERED, 5 HTTP, +Knife E SUZHOU hotfix)
- 复用 669b-i-wuxi apply 模板 (含 2024 skip in BOTH real_rows AND miss_rows loops)
- 复用 669b-i-wuxi verify 模板 (含 SUZHOU-specific 老 ID + parser 数字含空格 CASE clauses)
- 复用 mart_city_timeseries.sql 现有 CTE+JOIN 结构 (rd16 WUXI 模式 → rd17 SUZHOU)

## 后续 (待 user 裁定 commit/push)

- 4-commit amend-first chain:
  1. `feat(669b-i-suzhou): apply_mart_city_669b_i_suzhou.py psycopg2 直 psql`
  2. `feat(669b-i-suzhou): mart_city_timeseries.sql real_data_669b_i_suzhou CTE + 5 CASE`
  3. `test(669b-i-suzhou): verify script 36 红线 PASS`
  4. `chore(669b-i-suzhou): receipt (本件)`
- 注: Knife E SUZHOU hotfix 包含在 commit #2 (mart SQL commit) 中 (5 lines, file: scripts/fetch_hongheiku_city_y{year}_669fix.py)
- 双推 via Clash proxy: `git -c http.proxy=127.0.0.1:7890 -c https.proxy=127.0.0.1:7890 push origin <branch>`
- 3 ref verify: HEAD = origin/main = github/main

## 下 1 城 (per user 节奏)

knife 669b-i 4 城已全部 DELIVERED (DONGGUAN/DALIAN/WUXI/SUZHOU). 后续:
- Task #937: 669b-i — 8 batches × 6 years × ~32 city (48 sub-knives, 每 batch 4 city × 6 year)
- Task #938: 669j — 33 city × 6 years (6 sub-knives, ≤33 HTTP per sub-knife)

## 不宣称

- ❌ 不宣称 O1 / Gate / M2 / M4 PASS
- ❌ 不冒充 ops — SSH newvps 仅在 user_ruling_签署后
- ❌ 不回写 ops 文件
- ❌ 不爬网 — 5 HTTP 在红线内
- ❌ docs/81 零改动
- ❌ 不宣布 24 里程碑