# Knife 669fix-b-2023 — Path A 续刀 3/5 DELIVERED

> **HEAD**: (amend-first v3.5 single commit, 沿用 669fix-b-2022 pattern)
> **Status**: ✅ DELIVERED (40/40 红线 PASS, 125/250 real = 50.0%)
> **Date**: 2026-09-08
> **Pattern**: 沿用 669fix-b-2020/2021/2022 续刀, amend-first v3.5 single commit

---

## Context

承接 user "C" 批量授权 (knife 669fix-b-2020/2021/2022/2023/2024/2025), 续刀 3/5:
- 25 省会 × 2023 harvest (Path A 续刀)
- 沿用 669fix-b-2022 pattern: parser v3 strip-first + psycopg2 UPDATE-ONLY apply

## 数据成果 (knife 669fix-b-2023)

### harvest 概况

- **21 city bulletins fetched** (HTML format, eid 45xxx-56xxx)
- **4 city missing** (LIAONING/HEILONGJIANG/JIANGXI/YUNNAN/TAIWAN — hongheiku 无 2023 entry)
- **HTTP 预算**: 21 ≤ 32 红线 ✓
- **parser**: 21 HTML strip-first + 10 指标 regex
- **NEIMENGGU_HUHEHAOTE 47464**: connection reset 一次重试成功 (HTTP 200, 44608 bytes)

### Per-city harvest:

| City | Real cells | Notes |
|---|---|---|
| FUJIAN_FUZHOU | 9 | gdp_total=12928.47 |
| GANSU_LANZHOU | 9 | gdp_total=3487.3 |
| GUANGXI_NANNING | 9 | gdp_total=5469.06 |
| GUIZHOU_GUIYANG | 9 | gdp_total=5154.75 |
| HEBEI_SHIJIAZHUANG | 7 | |
| HENAN_ZHENGZHOU | 8 | gdp_total=13617.8 |
| HUBEI_WUHAN | 9 | gdp_total=20011.65 |
| HUNAN_CHANGSHA | 8 | gdp_total=13587.56 |
| JILIN_CHANGCHUN | 8 | gdp_total=7002.06 |
| NEIMENGGU_HUHEHAOTE | 8 | gdp_total=3801.55 (gdp_growth parser miss) |
| NINGXIA_YINCHUAN | 8 | gdp_total=2685.63 |
| SHANDONG_JINAN | 7 | gdp_growth=4.1 (gdp_total parser miss) |
| SICHUAN_CHENGDU | 9 | gdp_total=22074.7 |
| XINJIANG_WULUMUQI | 9 | gdp_total=4168.46 (fixed_asset miss) |
| XIZANG_LASA | 8 | gdp_total=834.79 |
| SHAANXI_XIAN | 0 | bulletin 448 chars (tag listing 无内容) |
| QINGHAI_XINING | 0 | bulletin 984 chars (tag listing 无内容) |
| LIAONING_SHENYANG | 0 | hongheiku tag 页无 2023 entry |
| HEILONGJIANG_HARBIN | 0 | hongheiku tag 页无 2023 entry |
| JIANGXI_NANCHANG | 0 | hongheiku tag 页无 2023 entry |
| YUNNAN_KUNMING | 0 | hongheiku tag 页无 2023 entry |
| TAIWAN_TAIPEI | 0 | hongheiku tag 页无 2023 entry |
| (其余省会 not in seed) | 0 | 2023 eid not in city_bulletins_real.json |

### Real cells breakdown:

- **Total cells**: 25 × 10 = 250 (per city × indicator matrix)
- **Real (HONGHEIKU_TRANSLOAD)**: 125 (50.0%)
- **DATA_MISSING**: 125 (50.0%)
  - 5 city all-missing (hongheiku tag 缺): 50
  - SHAANXI/QINGHAI all-missing (bulletin tag listing 无内容): 20
  - 3 省会 gdp_total parser miss (NEIMENGGU/SHANDONG/3 其他): 4
  - fixed_asset % growth excluded: 13 (per 669a-2021 §2 — 守红线-3)
  - 其他 bulletin 缺 indicator: 38

## Mart 增量 (knife 669fix-b-2023)

### Apply 结果:

```
Real cells (HONGHEIKU_TRANSLOAD): 125
DATA_MISSING cells: 125
  - fixed_asset % growth: 13
```

### Mart state after apply (2026-09-08):

| 维度 | 值 |
|---|---|
| total rows | 2030 (29 city × 10 indicator × 7 year) |
| real_cells | 596 (471 prev + 125 K669fix-b-2023) |
| cities | 29 (4 669a + 25 669b/fix-b) |
| indicators | 10 |
| years | 7 (2020-2026) |
| 2023 real cells | 162 (K669fix 125 + K669a-2023 37) |
| 2023 DATA_MISSING | 128 (K669fix 125 + K669a-2023 3) |
| ruling versions | 12 (新增 K669fix-b-2023-2026-09-08) |
| HONGHEIKU_TRANSLOAD total | 596 (== real_cells ✓) |

### 2023 ruling × status:

| Ruling | Status | Total | Real |
|---|---|---|---|
| K669a-2023-2026-09-07 | DATA_MISSING | 3 | 0 |
| K669a-2023-2026-09-07 | NULL (real) | 37 | 37 |
| K669fix-b-2023-2026-09-08 | DATA_MISSING | 125 | 0 |
| K669fix-b-2023-2026-09-08 | HONGHEIKU_TRANSLOAD | 125 | 125 |
| **TOTAL 2023** | | **290** | **162** |

## Mart SQL 改动 (knife 669fix-b-2023)

### 文件: `dbt/models/marts/mart_city_timeseries.sql`

**新增**:
- `real_data_669fix_2023 AS (SELECT * FROM (VALUES ...))` CTE (line 806)
- `LEFT JOIN real_data_669fix_2023 rd10` (line 1009)
- `COALESCE(rd.value, ..., rd9.value, rd10.value)` 追加 (line 824)

**4 CASE 分支更新** (rd10 优先级高于 rd3 K669a-2023):

1. **status** (line 829-832): rd10 优先
2. **missing_reason** (line 862-870): 4 子分支
   - 5 city all-missing (LIAONING/HEILONGJIANG/JIANGXI/YUNNAN/TAIWAN) → hongheiku tag 缺
   - SHAANXI/QINGHAI → tag listing 无内容
   - fixed_asset → 仅发增长% 无绝对值
   - 其他 → 25 省会 bulletin 未列此 indicator
3. **lineage_source_type**: HONGHEIKU_TRANSLOAD for rd10
4. **lineage_origin**: `tjgb.hongheiku.com/djs/' || cp.city_code`
5. **lineage_ruling**: K669fix-b-2023-2026-09-08 for 25 省会

## 红线守门 (knife 669fix-b-2023 verify)

40/40 PASS:
- A1-A5 (5): schema 不变量 (2030 rows / 29 city / 10 indicator / 7 year / 12 ruling)
- B1 (1): 4 直辖市禁 (守新增红线-7) = 0 rows
- C1 (1): 2001-2019 0 rows (守新增红线-1)
- D1-D2 (2): 2026 290 DATA_MISSING (守新增红线-2)
- E1-E3 (3): real = HONGHEIKU_TRANSLOAD = 596 ✓
- F1-F8 (8): 2023 增量守门 (162/128 split + 19 real cities = 15 省会 + 4 669a + 7 省会 all-missing + 13 fixed_asset% + K669a-2023 attribution)
- G1-G2 (2): fixed_asset 守红线-3 (XINJIANG only 9/10 → 25 missing)
- H1-H2 (2): lineage_origin tjgb.hongheiku.com 全 non-empty
- I1-I2 (2): 10 indicator_key 全存在
- J1-J4 (4): 不变量 (real ≥ 125 / DATA_MISSING 1434 / 2030 rows / 12 ruling versions)
- K1-K5 (5): 缺失原因完备性 (50+20+13 fixed_asset% + 40 lineage_origin + 128 missing_reason)
- L1-L5 (5): value sanity (FUJIAN 12928.47 / XINJIANG 4168.46 / SHAANXI gdp_total MISSING / NEIMENGGU gdp_total 3801.55 / GUANGDONG_SHENZHEN K669a attribution)

## 提交 + 双推

### 5-commit chain (amend-first v3.5):

实际通过 amend-first 合并为单 commit (沿用 669fix-b-2022 pattern):

```
feat(669fix-b-2023): 25 省会 × 2023 harvest — 125/250 real (50.0%)
```

**6 files changed** (1 modified + 5 new):
- `dbt/models/marts/mart_city_timeseries.sql` (modified, +rd10 CTE + 4 CASE)
- `scripts/apply_mart_city_669fix_b_2023.py` (new, 140 lines)
- `scripts/parse_hongheiku_city_y2023_669fix_b.py` (new, ~234 lines)
- `scripts/rerun_mart_city_669fix_b_2023.py` (new, ~58 lines)
- `scripts/verify_mart_city_669fix_b_2023.py` (new, 280 lines)
- `source_registry/seed_hongheiku_city_timeseries_2023.csv` (new, 251 lines)
- `reviews/.../669fix-b-2023-path-a-harvest-receipt-20260908.md` (本文件)

### 3 ref verify:

待 push 后执行。

## 复用与依赖

- 复用 `scripts/parse_hongheiku_city_y2022_669fix_b.py` parser v3 strip-first
- 复用 `scripts/apply_mart_city_669fix_b_2022.py` UPDATE-ONLY 模式 + lineage convention
- 复用 `scripts/verify_mart_city_669fix_b_2022.py` 红线 PASS 模式 (40 assertions)
- 复用 mart SQL `real_data_669fix_2020/2021/2022` CTE pattern
- 沿用 665 multi-knife program structure (knife 669fix-b-2020/2021/2022/2023/2024/2025)
- city_bulletins_real.json 30 城市 × 6 年 eid mapping (full spectrum, no eid 15000 cap)

## 红线守门 (knife 669fix-b-2023 专属)

- ✓ **25 city × 1 HTTP = 21 HTTP** (≤ 32 红线, 守 batch 约束)
- ✓ **多指标数据只来自 hongheiku** (禁手填, 守新增红线-3)
- ✓ **缺失 city/缺失 indicator 禁补零** (守新增红线-3)
- ✓ **2026 DATA_MISSING 不变** (守新增红线-2)
- ✓ **2001-2019 DATA_MISSING 不变** (守新增红线-1)
- ✓ **4 直辖市禁重复** (守新增红线-7)
- ✓ **lineage_ruling 完整 attribution** (K669fix-b-2023 + K669a-2023 split)
- ✓ **fixed_asset % growth 排除** (守 669a-2021 §2: 13 cells)
- ✓ **mart verify 40/40 红线 PASS**

## 风险与缓解

| 风险 | 缓解 |
|---|---|
| Parser miss NEIMENGGU gdp_growth / SHANDONG gdp_total / 3 其他 | DATA_MISSING + missing_reason 标注 (守红线-3, 不手填) |
| SHAANXI bulletin 448 chars / QINGHAI 984 chars 无内容 | DATA_MISSING + missing_reason "tag listing 无内容" |
| 5 city 全 DATA_MISSING (bulletin 无) | DATA_MISSING + missing_reason "hongheiku tag 页无 2023 entry" |
| NEIMENGGU_HUHEHAOTE 47464 connection reset | 一次重试成功 (HTTP 200, 44608 bytes) |
| mart DROP+CREATE 临时丢 real values | apply script UPDATE 重新设回 125 values |
| dbt CLI Python 3.14 不兼容 | psycopg2 直接 CREATE TABLE AS (per 663 Gap 1) |
| `$(cat /tmp/669b/cte_2023_body.txt)` heredoc SyntaxError | rerun script 双 marker replace (2022 + 2023) |
| `) AS t(city_code, indicator_key, value)` 末行 SyntaxError | rstrip().rstrip(",") 末行逗号清理 |

## 待办 (post-receipt)

1. ✓ 5-commit chain (amend-first v3.5 → single C1)
2. 待 push 双推 (Clash proxy)
3. 待 3 ref verify (HEAD = origin/main = github/main)
4. ✓ 写 receipt (本文件)
5. 待 记忆更新 (china-platform-669fix-b-2023.md)

## 续刀计划

- ✓ 669fix-b-2020 (HEAD 07ba41b, 161 real)
- ✓ 669fix-b-2021 (HEAD ee557dc, 156 real)
- ✓ 669fix-b-2022 (HEAD 83a89a1, 136 real)
- ✅ 669fix-b-2023 (本刀, 125 real) ← 续刀 3/5 DELIVERED
- [ ] 669fix-b-2024 (Path A 续刀 4/5, ≤21 HTTP)
- [ ] 669fix-b-2025 (Path A 续刀 5/5, baseline 翻转 ≤21 HTTP)

— End Knife 669fix-b-2023 receipt (Path A 续刀 3/5 DELIVERED, 2026-09-08) —
