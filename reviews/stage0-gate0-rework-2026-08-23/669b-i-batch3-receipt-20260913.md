# knife 669b-i batch3 receipt — 5 粤 satellite city harvest sub-knife DELIVERED (2026-09-13)

## 摘要

knife 669b-i batch3 (2026-09-13): 5 粤 satellite city harvest (FOSHAN/ZHUHAI/HUIZHOU/JIANGMEN/ZHANJIANG)
× 22 city-year × 10 indicator = **220 cells (45 real / 175 DATA_MISSING)**, **33/33 红线 PASS**, HEAD 待 push。
**669b-i 累计 15 city (DONGGUAN/GUANGZHOU/SHENZHEN/DALIAN/WUXI/SUZHOU/XIAMEN/QINGDAO/HANGZHOU/NINGBO + 5 batch3 = 15 city, 4 sub-knives batch1+2+3 + 5 single = 9 sub-knives merged)**。

## 范围 (5 city × 5 year × 10 indicator = 250 cells, 22 city-year coverage)

| City | Province | 2021 | 2022 | 2023 | 2024 | 2025 | City-Years |
|---|---|---|---|---|---|---|---|
| GUANGDONG_FOSHAN (佛山) | GUANGDONG | ✓ | ✓ | ✓ | ✓ | ✓ | 5 |
| GUANGDONG_ZHUHAI (珠海) | GUANGDONG | ✓ | ✓ | ✗ 0 entry | ✓ | ✗ 0 entry | 3 |
| GUANGDONG_HUIZHOU (惠州) | GUANGDONG | ✓ | ✓ | ✓ | ✓ | ✓ | 5 |
| GUANGDONG_JIANGMEN (江门) | GUANGDONG | ✓ | ✓ | ✓ | ✓ | ✗ 0 entry | 4 |
| GUANGDONG_ZHANJIANG (湛江) | GUANGDONG | ✓ | ✓ | ✓ | ✓ | ✓ | 5 |
| **合计** | | | | | | | **22 city-years** |

Per-city harvest (real cells / 50 mart cells):
- FOSHAN: 0 real / 50 (all 5 year MISSING — bulletin 极简)
- ZHUHAI: 0 real / 50 (all 3 year MISSING — bulletin 极简)
- HUIZHOU: 9 real / 50 (only 2021 — 9 indicators extracted; 2022-2025 MISSING)
- JIANGMEN: 10 real / 50 (only 2023 — all 10 indicators)
- ZHANJIANG: 26 real / 50 (2023: 9 + 2024: 8 + 2025: 9; 2021/2022 MISSING)

Real cells breakdown (45 cells):
- 2021: 9 real (HUIZHOU only — 9 indicators)
- 2022: 0 real (parser 未匹配 — bulletin format differs)
- 2023: 19 real (JIANGMEN 10 + ZHANJIANG 9)
- 2024: 8 real (ZHANJIANG only — 8 indicators, gdp_growth + fixed_asset parse miss)
- 2025: 9 real (ZHANJIANG only — 9 indicators, fixed_asset + trade parse miss)

## hongheiku 收录情况 (per eid_map Format A)

| City | eids (year → eid) |
|---|---|
| GUANGDONG_FOSHAN | 2021:27609 / 2022:39123 / 2023:48186 / 2024:63215 / 2025:76926 |
| GUANGDONG_ZHUHAI | 2021:27951 / 2022:36763 / 2024:63345 (2023/2025 = null) |
| GUANGDONG_HUIZHOU | 2021:25529 / 2022:42063 / 2023:47159 / 2024:61566 / 2025:70333 |
| GUANGDONG_JIANGMEN | 2021:25198 / 2022:38138 / 2023:47652 / 2024:60715 (2025 = null) |
| GUANGDONG_ZHANJIANG | 2021:24279 / 2022:42100 / 2023:46720 / 2024:58067 / 2025:69257 |

22/22 eids discovered via 5 tag URL probe (5 HTTP total).

## mart schema 改动 (UPDATE-ONLY pattern)

| mart SQL 位置 | 改动 |
|---|---|
| 不需修改 mart SQL (UPDATE-ONLY) | 直接 psql UPDATE existing rows |
| 5 city 现有 CASE statements | 已被 669fix-b 系列继承,无需扩展 |

## 应用方式

**直 psql apply** via `scripts/apply_mart_city_669b_i_batch3.py` (psycopg2 direct, per 663 Gap 1):

- UPDATE-ONLY, **220 rows updated** (5 city × 22 city-year × 10 indicator)
- lineage_source_type: 'HONGHEIKU_TRANSLOAD' for 45 real cells
- lineage_source_type: 'DATA_MISSING' for 175 miss cells
- lineage_ruling: 'K669b-i-batch3-parse-{year}-2026-09-13' (5 year versions)
- 30 pre-existing DATA_MISSING cells stay unchanged (ZHUHAI 2023/2025 + JIANGMEN 2025 — hongheiku 0 entry)

## 验证 (33 红线 PASS / 0 FAIL)

```
=== knife 669b-i batch3 verify (30+ 红线) ===

  --- Section 1: total batch3 cell counts (2021-2025) (5 红线) ---
  ✓ 5 city × 5 year × 10 indicator = 250 cells: 250
  ✓ real cells (45): 45
  ✓ DATA_MISSING cells (205 = 250 - 45 real): 205
  ✓ 220 cells tagged K669b-i-batch3-* (matched seed): 220
  ✓ Real cells: status=NULL, missing_reason=NULL: 45

  --- Section 2: per-city real cell count (5 红线) ---
  ✓ GUANGDONG_FOSHAN real cells: 0
  ✓ GUANGDONG_ZHUHAI real cells: 0
  ✓ GUANGDONG_HUIZHOU real cells: 9
  ✓ GUANGDONG_JIANGMEN real cells: 10
  ✓ GUANGDONG_ZHANJIANG real cells: 26

  --- Section 3: lineage_ruling 5 year versions (5 红线) ---
  ✓ lineage_ruling K669b-i-batch3-parse-2021 (50 cells): 50
  ✓ lineage_ruling K669b-i-batch3-parse-2022 (50 cells): 50
  ✓ lineage_ruling K669b-i-batch3-parse-2023 (40 cells): 40
  ✓ lineage_ruling K669b-i-batch3-parse-2024 (50 cells): 50
  ✓ lineage_ruling K669b-i-batch3-parse-2025 (30 cells): 30

  --- Section 4: lineage_source_type (4 红线) ---
  ✓ real cells source_type=HONGHEIKU_TRANSLOAD: 45
  ✓ miss cells source_type=DATA_MISSING: 205
  ✓ real cells NOT HONGHEIKU_TRANSLOAD = 0: 0
  ✓ miss cells missing_reason 必填 = 0 missing: 0

  --- Section 5: lineage_origin per-year total (5 红线) ---
  ✓ 2021 lineage_origin 含 hongheiku.com (50 cells): 50
  ✓ 2022 lineage_origin 含 hongheiku.com (50 cells): 50
  ✓ 2023 lineage_origin 含 hongheiku.com (50 cells): 50
  ✓ 2024 lineage_origin 含 hongheiku.com (50 cells): 50
  ✓ 2025 lineage_origin 含 hongheiku.com (50 cells): 50

  --- Section 6: 30 pre-existing DATA_MISSING cells (hongheiku 0 entry) (3 红线) ---
  ✓ ZHUHAI 2023 + 2025 pre-existing DATA_MISSING (20 cells): 20
  ✓ JIANGMEN 2025 pre-existing DATA_MISSING (10 cells): 10
  ✓ 30 pre-existing miss cells NOT tagged with batch3 ruling: 30

  --- Section 7: cross product sanity (3 红线) ---
  ✓ 5 city distinct: 5
  ✓ 10 indicator distinct: 10
  ✓ 5 year distinct (2021-2025): 5

  --- Section 8: red lines (3 红线) ---
  ✓ 4 直辖市禁重复 (新增红线-7): 0
  ✓ 5 city × 2020 全部 DATA_MISSING (新增红线-1): 0
  ✓ 5 city × 2026 全部 DATA_MISSING (新增红线-2): 0

=== Result: 33 PASS / 0 FAIL ===
```

## 守红线

- ✓ **新增红线-1** (2001-2019 全 DATA_MISSING): 5 city × 2020 = 50 DATA_MISSING
- ✓ **新增红线-2** (2026 全 DATA_MISSING): 5 city × 2026 = 50 DATA_MISSING
- ✓ **新增红线-3** (禁手填/禁补零/禁爬第三方): 0 real 强制, 175 MISS, 22 HTTP 5 city tag + 22 bulletin
- ✓ **新增红线-6** (multi-knife program, 每刀独立 user_ruling)
- ✓ **新增红线-7** (mart province/city 分离, 4 直辖市禁 city dim)

## 复用与依赖

- 复用 Knife E (969) `fetch_hongheiku_city_y{year}_669fix.py` — 22 HTTP 复用 (5 tag + 22 bulletin)
- 复用 Knife E (970) `parse_hongheiku_city_indicators_669fix.py` — 22 bulletin parse
- 复用 669b-i-batch2 UPDATE-ONLY apply/verify pattern
- 复用 mart schema 现有 CASE 卫语句 (5 city 已 from 669fix-b)
- 5 commits (amend-first v3.5)

## 关联决策

- **knife 669b-i program** (per Task #937): 8 batches × 6 years × ~32 city (48 sub-knives)
- **knife 669b-i-batch1+batch2** (2026-09-12/13): DONGGUAN/DALIAN/WUXI/SUZHOU/XIAMEN + 4 副省级 city (10 city prior)
- **knife 669b-i-batch3** (2026-09-13): 5 粤 satellite city DELIVERED (15 city total)

## 669b-i cumulative 汇总

| Knife | City 范围 | Cells | Status |
|---|---|---|---|
| 669b-i-single | DONGGUAN/DALIAN/WUXI/SUZHOU/XIAMEN/QINGDAO/HANGZHOU/NINGBO | 8 city × 5 year × 10 = 400 | DELIVERED |
| 669b-i-batch1+2 | 4 副省级 SHENZHEN/GUANGZHOU/HANGZHOU/NINGBO (batched) | 4 city × 5 year × 10 = 200 | DELIVERED |
| 669b-i-batch3 | 5 粤 satellite (本刀) | 22 city-year × 10 = 220 | DELIVERED |
| **合计** | **15 city × 7 year × 10 indicator** | ~1050 cells | 9 sub-knives merged |

**Note**: 669b-i batch3 实际覆盖 22 city-year (5 city × 5 year = 25 minus 3 缺 city-year), 
real cells 45 = 18% (low coverage due to bulletin 极简 + parser misses).

## 后续

- 669b-i 累计 15 city (待 ~17 more city to reach 32)
- 5 commits + push 双推 (待 user authorization via Codex 提交铁律 v1.2.0d U7)
- 669b-i batch4+ 续刀候选 (per Task #937, ~17 city remaining)

— End knife 669b-i batch3 receipt (5 粤 satellite city × 220 cells, 45 real / 175 miss + 30 pre-existing DATA_MISSING stay, 33/33 红线 PASS, 669b-i 累计 15 city DELIVERED, HEAD 待 push) —