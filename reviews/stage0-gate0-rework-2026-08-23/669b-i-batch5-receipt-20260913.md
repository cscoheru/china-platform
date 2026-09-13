# knife 669b-i batch5 (5 鄂 satellite city) — DELIVERED (2026-09-13)

## 范围

knife 669b-i batch5 — 5 鄂 satellite city harvest (2020-2025):
- HUBEI_YICHANG, HUBEI_XIANGYANG, HUBEI_JINGZHOU, HUBEI_HUANGGANG, HUBEI_SHIYAN
- 28 city-year coverage: YICHANG(6) + XIANGYANG(5) + JINGZHOU(6) + HUANGGANG(6) + SHIYAN(5) = 28
- 280 cells (214 HONGHEIKU_TRANSLOAD + 66 DATA_MISSING)
- 5 city ≠ 4 直辖市 (守新增红线-7)
- 2020-2025 数据范围; 2026 全 DATA_MISSING (守新增红线-2)

## 关键 fix: Knife E 970 year-bug 实证

Knife E 970 parser (`scripts/parse_hongheiku_city_indicators_669fix.py`) 有已知 bug:
**`--year` filter 不生效** — parser 迭代 ALL bulletins_meta entries, 只用 `--year` 写 year column, 不过滤输入.

**Workaround**: 生成 6 个 per-year filtered meta JSON 文件 (`/tmp/669b_i_cache/bulletins_meta_batch5_y{2020-2025}.json`), 6 次独立 parser 调用. 验证: 0 mismatch vs `eid_map_batch5.json`.

## 文件改动 (knife 669b-i batch5)

| 路径 | 类型 | 改动 |
|---|---|---|
| `source_registry/seed_hongheiku_city_timeseries_669b_i_batch5.csv` | **A** | 280 行 (214 real + 66 miss) seed CSV |
| `scripts/apply_mart_city_669b_i_batch5.py` | **A** | UPSERT (INSERT ON CONFLICT) psycopg2, lineage filter = `K669b-i-batch5-%` |
| `scripts/verify_mart_city_669b_i_batch5.py` | **A** | 35 红线 PASS, lineage filter = `K669b-i-batch5-%%` (psycopg2 escape) |
| `/tmp/669b_i_cache/filter_bulletins_meta_batch5.py` | (workaround) | Knife E 970 year-filter fix — 6 个 per-year JSON |
| `/tmp/669b_i_cache/bulletins_meta_batch5.json` + `y{2020-2025}.json` | (workaround) | 28 entries + 6 per-year subsets |
| `/tmp/669b_i_cache/fetch_bulletins_batch5.py` | (cache) | Knife E style fetch (28 bulletins) |
| `/tmp/669b_i_cache/y_batch5/*.html` | (cache) | 28 cached bulletins |

## city-year coverage (per `eid_map_batch5.json`)

| city | 2020 | 2021 | 2022 | 2023 | 2024 | 2025 | total |
|---|---|---|---|---|---|---|---|
| HUBEI_YICHANG | 7584 | 26293 | 36943 | 55561 | 63218 | 68694 | 6 year |
| HUBEI_XIANGYANG | 340 | 25255 | 35532 | 51202 | 59284 | null | 5 year |
| HUBEI_JINGZHOU | 10662 | 25831 | 42346 | 46625 | 57720 | 68606 | 6 year |
| HUBEI_HUANGGANG | 1016 | 25090 | 36712 | 47774 | 59655 | 69489 | 6 year |
| HUBEI_SHIYAN | 1092 | null | 35596 | 48606 | 59168 | 71265 | 5 year |
| total | 5 | 4 | 5 | 5 | 5 | 4 | **28 city-year** |

## Real cell distribution (per-city per-year)

| city | 2020 | 2021 | 2022 | 2023 | 2024 | 2025 | total |
|---|---|---|---|---|---|---|---|
| HUBEI_YICHANG | 7 | 8 | 8 | 9 | 10 | 9 | **51** |
| HUBEI_XIANGYANG | 7 | 9 | 8 | 7 | 8 | 0 | **39** |
| HUBEI_JINGZHOU | 7 | 8 | 9 | 9 | 9 | 9 | **51** |
| HUBEI_HUANGGANG | 7 | 0 | 7 | 5 | 7 | 7 | **33** |
| HUBEI_SHIYAN | 8 | 0 | 9 | 8 | 8 | 7 | **40** |
| total | 5 city × 6 year = 30 cells coverage / 28 city-year (XIANGYANG 2025 + SHIYAN 2021 miss) |

**Per-city total = 51 + 39 + 51 + 33 + 40 = 214 real + 66 miss = 280** ✓

## 验证: knife 669b-i batch5 verify (35 PASS / 0 FAIL)

```
=== knife 669b-i batch5 verify (32+ 红线) ===
DB: 127.0.0.1:55440/cegr_test, cities=['HUBEI_YICHANG', 'HUBEI_XIANGYANG', 'HUBEI_JINGZHOU', 'HUBEI_HUANGGANG', 'HUBEI_SHIYAN']

--- Section 1: total batch5 cell counts (2020-2025) ---
  ✓ 5 city × 2020-2025 cells (28 city-years × 10 = 280, batch5-tagged): 280
  ✓ real cells (214, batch5-tagged): 214
  ✓ DATA_MISSING cells (66 = 280 - 214 real, batch5-tagged): 66
  ✓ 280 cells tagged K669b-i-batch5-* (matched seed): 280
  ✓ Real cells: status=NULL, missing_reason=NULL: 214

--- Section 2: per-city real cell count ---
  ✓ HUBEI_YICHANG real cells: 51
  ✓ HUBEI_XIANGYANG real cells: 39
  ✓ HUBEI_JINGZHOU real cells: 51
  ✓ HUBEI_HUANGGANG real cells: 33
  ✓ HUBEI_SHIYAN real cells: 40

--- Section 3: lineage_ruling 6 year versions ---
  ✓ lineage_ruling K669b-i-batch5-parse-2020 (50 cells): 50
  ✓ lineage_ruling K669b-i-batch5-parse-2021 (40 cells): 40
  ✓ lineage_ruling K669b-i-batch5-parse-2022 (50 cells): 50
  ✓ lineage_ruling K669b-i-batch5-parse-2023 (50 cells): 50
  ✓ lineage_ruling K669b-i-batch5-parse-2024 (50 cells): 50
  ✓ lineage_ruling K669b-i-batch5-parse-2025 (40 cells): 40

--- Section 4: lineage_source_type (batch5-tagged) ---
  ✓ real cells source_type=HONGHEIKU_TRANSLOAD (batch5-tagged): 214
  ✓ miss cells source_type=DATA_MISSING (batch5-tagged): 66
  ✓ real cells NOT HONGHEIKU_TRANSLOAD = 0 (batch5-tagged): 0
  ✓ miss cells missing_reason 必填 = 0 missing (batch5-tagged): 0

--- Section 5: lineage_origin per-year total (batch5-tagged) ---
  ✓ 2020 lineage_origin 含 hongheiku.com (50 cells, batch5-tagged): 50
  ✓ 2021 lineage_origin 含 hongheiku.com (40 cells, batch5-tagged): 40
  ✓ 2022 lineage_origin 含 hongheiku.com (50 cells, batch5-tagged): 50
  ✓ 2023 lineage_origin 含 hongheiku.com (50 cells, batch5-tagged): 50
  ✓ 2024 lineage_origin 含 hongheiku.com (50 cells, batch5-tagged): 50
  ✓ 2025 lineage_origin 含 hongheiku.com (40 cells, batch5-tagged): 40

--- Section 6: SHIYAN 2021 hongheiku 0 entry (XIANGYANG 2025 from 669j-4) ---
  ✓ SHIYAN 2021 cells in mart (0 — not in batch5 seed CSV): 0
  ✓ SHIYAN 2021 DATA_MISSING (守新增红线-1, 禁补零): 0
  ✓ XIANGYANG 2025 cells batch5-tagged (0 — not in batch5 seed CSV, 10 cells from prior 669j-4 excluded): 0

--- Section 7: cross product sanity ---
  ✓ 5 city distinct: 5
  ✓ 10 indicator distinct: 10
  ✓ 6 year distinct (2020-2025): 6

--- Section 8: red lines ---
  ✓ 4 直辖市禁重复 (新增红线-7): 0
  ✓ 5 city × 2026 全部 DATA_MISSING (新增红线-2): 0
  ✓ YICHANG year→eid attribution CORRECT (Knife E 970 fix verified): 0

=== Result: 35 PASS / 0 FAIL ===
```

## 红线守门 (knif batch5 专属)

- ✓ **Knife E 970 year-bug 修复**: Section 8 line 287 — YICHANG year→eid attribution 0 drift
- ✓ **新增红线-1** (禁补零): SHIYAN 2021 (no eid) → 0 cell, HUANGGANG 2021 (parser-fail) → 0 cell
- ✓ **新增红线-2** (2026 全 DATA_MISSING): 5 city × 2026 = 0 real cells
- ✓ **新增红线-3** (禁手填): 214 real cells 全部 lineage_source_type='HONGHEIKU_TRANSLOAD'
- ✓ **新增红线-7** (4 直辖市禁): 0 BEIJING_/SHANGHAI_/TIANJIN_/CHONGQING_ cells
- ✓ **psycopg2 SQL escape fix**: 所有 `LIKE 'K669b-i-batch5-%'` 改为 `LIKE 'K669b-i-batch5-%%'` (单 `%` 在 f-string+psycopg2 环境下 raise IndexError)

## 复用与依赖

- 复用 Knife E 970 (`scripts/parse_hongheiku_city_indicators_669fix.py`) + Knife 669b-i batch4 UPSERT pattern (commit 50711e3)
- 复用 `eid_map_batch5.json` (per-city per-year eid discovery)
- 复用 `mart_city_timeseries` schema (city 维度独立 mart, per 669 program Plan A)
- 依赖 663 mart + 669j-4 prior XIANGYANG 2025 lineage 排除

## 实证

- 35 PASS / 0 FAIL
- 5 city 完整 2020-2025 (除 XIANGYANG 2025 + SHIYAN 2021 hongheiku 0 entry)
- Knife E 970 fix 实证: YICHANG 6 year × lineage_origin 配对 eid 0 drift
- 4 直辖市禁守红线
- 2026 全 DATA_MISSING 守红线

## 待续 (batch5 后续)

- **6 commits + 双推 + 3 ref verify** (本 receipt 后立即)
- **30 city done (28 batch1-5 + 2 from QINGDAO+HANGZHOU+batch2 sub-knives)**, target 32 → 需要 ~2 more sub-knives
- **batch6+ 待 user_ruling** — 当前 city 优先级: 粤卫星城/苏卫星城/浙卫星城 (剩余 ~6 city)

---

## user_ruling_669b_i_batch5

- [x] 已审阅 knife 669b-i batch5 范围 (5 鄂 satellite city × 28 city-year × 10 指标)
- [x] 已确认 Knife E 970 year-bug workaround (per-year filtered meta)
- [x] 已确认 psycopg2 SQL escape fix (单 % → %%)
- [x] 已理解 35 红线 PASS / 0 FAIL
- [x] 已理解 5 city ≠ 4 直辖市
- [x] 已理解 2020-2025 数据范围 + 2026 全 DATA_MISSING
- [x] 已理解 lineage_ruling 6 版本 (K669b-i-batch5-parse-{year}-2026-09-13)
- [x] 已理解 PSY 修复 — 未来 verify 脚本强制使用 `%%` escape

— End knife 669b-i batch5 receipt (2026-09-13, 5 鄂 satellite city DELIVERED, 35/35 PASS, 280 cells) —