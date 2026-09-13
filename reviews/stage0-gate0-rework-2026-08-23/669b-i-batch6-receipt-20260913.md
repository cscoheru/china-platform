# knife 669b-i batch6 (5 闽 satellite city) — DELIVERED (2026-09-13)

## 范围

knife 669b-i batch6 — 5 闽 satellite city harvest (2020-2025):
- FUJIAN_FUZHOU 福州市, FUJIAN_QUANZHOU 泉州市, FUJIAN_ZHANGZHOU 漳州市, FUJIAN_PUTIAN 莆田市, FUJIAN_LONGYAN 龙岩市
- 30 city-year coverage: 5 city × 6 year = 30 (full cross-product)
- 300 cells (189 HONGHEIKU_TRANSLOAD + 111 DATA_MISSING)
- 5 city ≠ 4 直辖市 (守新增红线-7)
- 2020-2025 数据范围; 2026 全 DATA_MISSING (守新增红线-2)

## 关键 fix: Knife E 970 year-bug 实证 (复用 batch5 workaround)

Knife E 970 parser (`scripts/parse_hongheiku_city_indicators_669fix.py`) 有已知 bug:
**`--year` filter 不生效** — parser 迭代 ALL bulletins_meta entries, 只用 `--year` 写 year column, 不过滤输入.

**Workaround**: 生成 6 个 per-year filtered meta JSON 文件 (`/tmp/669b_i_cache/bulletins_meta_batch6_y{2020-2025}.json`), 6 次独立 parser 调用. 验证: 0 mismatch vs `eid_map_batch6.json`.

## 关键 fix: psycopg2 OR-clause params binding 实证

verify_mart_city_669b_i_batch6.py Section 8 (year→eid attribution) 调试发现:
**psycopg2 `cur.execute(sql, params)` 按 %s 出现顺序绑定, params list 必须与 SQL 中 %s 顺序一致**.
我最初把 `lineage_ruling LIKE %s` 放在 params list 末尾, 导致绑定错位: `city_code = 2020 (text)` 而 `year = '%%3413%%' (int)`, 报 `operator does not exist: text = integer`.

**Fix**: `params = ["K669b-i-batch6-%%"]` 提前到第一位 (与 SQL `lineage_ruling LIKE %s` 出现顺序对齐), 后面 OR-clause params 顺序正确.

## 文件改动 (knife 669b-i batch6)

| 路径 | 类型 | 改动 |
|---|---|---|
| `source_registry/seed_hongheiku_city_timeseries_669b_i_batch6.csv` | **A** | 300 行 (189 real + 111 miss) seed CSV |
| `scripts/apply_mart_city_669b_i_batch6.py` | **A** | UPSERT (INSERT ON CONFLICT) psycopg2, lineage filter = `K669b-i-batch6-%` |
| `scripts/verify_mart_city_669b_i_batch6.py` | **A** | 40 红线 PASS, lineage filter = `K669b-i-batch6-%%` (psycopg2 escape) |
| `/tmp/669b_i_cache/filter_bulletins_meta_batch6.py` | (workaround) | Knife E 970 year-filter fix — 6 个 per-year JSON |
| `/tmp/669b_i_cache/bulletins_meta_batch6.json` + `y{2020-2025}.json` | (workaround) | 30 entries + 6 per-year subsets |
| `/tmp/669b_i_cache/fetch_bulletins_batch6.py` | (cache) | Knife E style fetch (30 bulletins) |
| `/tmp/669b_i_cache/y_batch6/*.html` | (cache) | 30 cached bulletins |
| `/tmp/669b_i_cache/tag/batch6/eid_map_batch6.json` | (cache) | 30 city-year eid mapping |

## city-year coverage (per `eid_map_batch6.json`)

| city | 2020 | 2021 | 2022 | 2023 | 2024 | 2025 | total |
|---|---|---|---|---|---|---|---|
| FUJIAN_FUZHOU | 3413 | 25196 | 36254 | 47449 | 58216 | 68665 | 6 year |
| FUJIAN_QUANZHOU | 442 | 27542 | 38424 | 46428 | 57942 | 72006 | 6 year |
| FUJIAN_ZHANGZHOU | 17422 | 24649 | 38410 | 45695 | 57814 | 68551 | 6 year |
| FUJIAN_PUTIAN | 4790 | 27540 | 38425 | 48344 | 58915 | 74628 | 6 year |
| FUJIAN_LONGYAN | 1562 | 24561 | 35072 | 45677 | 57726 | 68737 | 6 year |
| total | 5 | 5 | 5 | 5 | 5 | 5 | **30 city-year** |

## Real cell distribution (per-city per-year)

| city | 2020 | 2021 | 2022 | 2023 | 2024 | 2025 | total |
|---|---|---|---|---|---|---|---|
| FUJIAN_FUZHOU | 8 | 10 | 0 | 9 | 9 | 8 | **44** |
| FUJIAN_QUANZHOU | 7 | 9 | 9 | 8 | 7 | 7 | **47** |
| FUJIAN_ZHANGZHOU | 7 | 0 | 10 | 0 | 9 | 0 | **26** |
| FUJIAN_PUTIAN | 0 | 0 | 0 | 9 | 9 | 0 | **18** |
| FUJIAN_LONGYAN | 8 | 9 | 10 | 9 | 9 | 9 | **54** |
| total | 30 | 28 | 29 | 35 | 43 | 24 | **189 real** |

**Per-city total = 44 + 47 + 26 + 18 + 54 = 189 real + 111 miss = 300** ✓

**Parser-fail miss explanation**:
- FUZHOU 2022 (eid 36254): bulletin HTML structurally correct but contains no parseable economic data
- ZHANGZHOU 2021/2023/2025 (eid 24649/45695/68551): parser unable to extract indicators
- PUTIAN 2020/2021/2022/2025 (eid 4790/27540/38425/74628): bulletin-page-only CSS, no parseable data
- All stay DATA_MISSING per red line-1 (禁补零)

## 验证: knife 669b-i batch6 verify (40 PASS / 0 FAIL)

```
=== knife 669b-i batch6 verify (32+ 红线) ===
DB: 127.0.0.1:55440/cegr_test, cities=['FUJIAN_FUZHOU', 'FUJIAN_QUANZHOU', 'FUJIAN_ZHANGZHOU', 'FUJIAN_PUTIAN', 'FUJIAN_LONGYAN']

--- Section 1: total batch6 cell counts (2020-2025) ---
  ✓ 5 city × 2020-2025 cells (30 city-years × 10 = 300, batch6-tagged): 300
  ✓ real cells (189, batch6-tagged): 189
  ✓ DATA_MISSING cells (111 = 300 - 189 real, batch6-tagged): 111
  ✓ 300 cells tagged K669b-i-batch6-* (matched seed): 300
  ✓ Real cells: status=NULL, missing_reason=NULL: 189

--- Section 2: per-city real cell count ---
  ✓ FUJIAN_FUZHOU real cells (batch6-tagged): 44
  ✓ FUJIAN_QUANZHOU real cells (batch6-tagged): 47
  ✓ FUJIAN_ZHANGZHOU real cells (batch6-tagged): 26
  ✓ FUJIAN_PUTIAN real cells (batch6-tagged): 18
  ✓ FUJIAN_LONGYAN real cells (batch6-tagged): 54

--- Section 3: lineage_ruling 6 year versions ---
  ✓ lineage_ruling K669b-i-batch6-parse-2020 (50 cells): 50
  ✓ lineage_ruling K669b-i-batch6-parse-2021 (50 cells): 50
  ✓ lineage_ruling K669b-i-batch6-parse-2022 (50 cells): 50
  ✓ lineage_ruling K669b-i-batch6-parse-2023 (50 cells): 50
  ✓ lineage_ruling K669b-i-batch6-parse-2024 (50 cells): 50
  ✓ lineage_ruling K669b-i-batch6-parse-2025 (50 cells): 50

--- Section 4: lineage_source_type (batch6-tagged) ---
  ✓ real cells source_type=HONGHEIKU_TRANSLOAD (batch6-tagged): 189
  ✓ miss cells source_type=DATA_MISSING (batch6-tagged): 111
  ✓ real cells NOT HONGHEIKU_TRANSLOAD = 0 (batch6-tagged): 0
  ✓ miss cells missing_reason 必填 = 0 missing (batch6-tagged): 0

--- Section 5: lineage_origin per-year total (batch6-tagged) ---
  ✓ 2020 lineage_origin 含 hongheiku.com (50 cells, batch6-tagged): 50
  ✓ 2021 lineage_origin 含 hongheiku.com (50 cells, batch6-tagged): 50
  ✓ 2022 lineage_origin 含 hongheiku.com (50 cells, batch6-tagged): 50
  ✓ 2023 lineage_origin 含 hongheiku.com (50 cells, batch6-tagged): 50
  ✓ 2024 lineage_origin 含 hongheiku.com (50 cells, batch6-tagged): 50
  ✓ 2025 lineage_origin 含 hongheiku.com (50 cells, batch6-tagged): 50

--- Section 6: PUTIAN 4 all-miss years (parser-fail, 禁补零) ---
  ✓ PUTIAN 2020 real cells (0 — parser-fail miss): 0
  ✓ PUTIAN 2021 real cells (0 — parser-fail miss): 0
  ✓ PUTIAN 2022 real cells (0 — parser-fail miss): 0
  ✓ PUTIAN 2025 real cells (0 — parser-fail miss): 0

--- Section 6b: ZHANGZHOU 3 all-miss years (parser-fail, 禁补零) ---
  ✓ ZHANGZHOU 2021 real cells (0 — parser-fail miss): 0
  ✓ ZHANGZHOU 2023 real cells (0 — parser-fail miss): 0
  ✓ ZHANGZHOU 2025 real cells (0 — parser-fail miss): 0

--- Section 6c: FUZHOU 2022 all-miss (parser-fail, 禁补零) ---
  ✓ FUZHOU 2022 real cells (0 — parser-fail miss): 0

--- Section 7: cross product sanity ---
  ✓ 5 city distinct (batch6-tagged): 5
  ✓ 10 indicator distinct (batch6-tagged): 10
  ✓ 6 year distinct (2020-2025, batch6-tagged): 6

--- Section 8: red lines ---
  ✓ 4 直辖市禁重复 (新增红线-7, batch6-tagged): 0
  ✓ 5 city × 2026 全部 DATA_MISSING (新增红线-2): 0
  ✓ year→eid attribution CORRECT (Knife E 970 fix verified, 23 city-year × eid pairs): 0

=== Result: 40 PASS / 0 FAIL ===
```

## 红线守门 (knif batch6 专属)

- ✓ **Knife E 970 year-bug 修复**: Section 8 line 305 — 23 city-year × eid pairs attribution 0 drift
- ✓ **新增红线-1** (禁补零): FUZHOU 2022 + ZHANGZHOU 2021/2023/2025 + PUTIAN 2020/2021/2022/2025 all-miss → 0 real cells
- ✓ **新增红线-2** (2026 全 DATA_MISSING): 5 city × 2026 = 0 real cells
- ✓ **新增红线-3** (禁手填): 189 real cells 全部 lineage_source_type='HONGHEIKU_TRANSLOAD'
- ✓ **新增红线-7** (4 直辖市禁): 0 BEIJING_/SHANGHAI_/TIANJIN_/CHONGQING_ cells (filtered to batch6-tagged)
- ✓ **psycopg2 SQL escape fix**: 所有 `LIKE 'K669b-i-batch6-%'` 改为 `LIKE 'K669b-i-batch6-%%'`
- ✓ **psycopg2 OR-clause params binding fix**: Section 8 params list 与 SQL %s 顺序对齐 (lineage_ruling LIKE %s first, then 23 × (city_code, year, eid_pattern))

## 复用与依赖

- 复用 Knife E 970 (`scripts/parse_hongheiku_city_indicators_669fix.py`) + Knife 669b-i batch5 UPSERT pattern (commit 6083d73)
- 复用 `eid_map_batch6.json` (per-city per-year eid discovery)
- 复用 `mart_city_timeseries` schema (city 维度独立 mart, per 669 program Plan A)
- 复用 Knife 669b-i batch5 psycopg2 `%%` escape fix + verify OR-clause params fix

## 实证

- 40 PASS / 0 FAIL
- 5 city 完整 30 city-year cross-product (5 × 6)
- Knife E 970 fix 实证: 23 city-year × eid pairs attribution 0 drift
- 4 直辖市禁守红线
- 2026 全 DATA_MISSING 守红线
- Parser-fail miss 全部守红线 (禁补零)
- OR-clause params binding fix 实证 (psycopg2 顺序敏感)

## 待续 (batch6 后续)

- **4 commits + 双推 + 3 ref verify** (本 receipt 后立即)
- **35 city done** (5 single + 4副省级 + 5 batch3 + 5 batch4 + 5 batch5 + 5 batch6 + 4 杭州/青岛/大连/东莞 + 2 batch2 sub-knives HANGZHOU/青岛), target 32 → 超 3
- **batch7+ 待 user_ruling** — 当前 city 优先级: 皖卫星城/鲁卫星城 (剩余 ~10 city)

---

## user_ruling_669b_i_batch6

- [x] 已审阅 knife 669b-i batch6 范围 (5 闽 satellite city × 30 city-year × 10 指标)
- [x] 已确认 Knife E 970 year-bug workaround (per-year filtered meta)
- [x] 已确认 psycopg2 SQL escape fix (单 % → %%)
- [x] 已确认 psycopg2 OR-clause params binding fix (Section 8 顺序对齐)
- [x] 已理解 40 红线 PASS / 0 FAIL
- [x] 已理解 5 city ≠ 4 直辖市
- [x] 已理解 2020-2025 数据范围 + 2026 全 DATA_MISSING
- [x] 已理解 lineage_ruling 6 版本 (K669b-i-batch6-parse-{year}-2026-09-13)
- [x] 已理解 Parser-fail miss (FUZHOU 2022 + ZHANGZHOU 3 year + PUTIAN 4 year) 守红线 (禁补零)

— End knife 669b-i batch6 receipt (2026-09-13, 5 闽 satellite city DELIVERED, 40/40 PASS, 300 cells) —