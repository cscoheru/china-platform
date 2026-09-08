# Knife 669fix-b-2022 — Path A 续刀 2/5 DELIVERED

> **HEAD**: d0b660e (5 commits + receipt combined via amend-first v3.5)
> **Status**: ✅ DELIVERED (40/40 红线 PASS, 136/250 real = 54.4%)
> **Date**: 2026-09-08
> **Pattern**: 沿用 669fix-b-2020/2021 续刀, amend-first v3.5 single commit

---

## Context

承接 user "C" 批量授权 (knife 669fix-b-2020/2021/2022/2023/2024/2025), 续刀 2/5:
- 25 省会 × 2022 harvest (Path A 续刀)
- 沿用 669fix-b-2021 pattern: parser v3 strip-first + psycopg2 UPDATE-ONLY apply

## 数据成果 (knife 669fix-b-2022)

### harvest 概况

- **23 city bulletins fetched** (HTML format, eid 35096-42507)
- **2 city missing** (GUANGXI_NANNING/TAIWAN_TAIPEI — hongheiku 无 2022 entry)
- **HTTP 预算**: 23 ≤ 32 红线 ✓
- **parser**: 23 HTML strip-first + 10 指标 regex

### Per-city harvest:

| City | Real cells | Notes |
|---|---|---|
| HEBEI_SHIJIAZHUANG | 6 | |
| SHANXI_TAIYUAN | 0 | bulletin 无内容 |
| NEIMENGGU_HUHEHAOTE | 9 | |
| LIAONING_SHENYANG | 7 | |
| JILIN_CHANGCHUN | 8 | |
| HEILONGJIANG_HARBIN | 0 | bulletin 无内容 |
| ANHUI_HEFEI | 0 | bulletin 无内容 |
| FUJIAN_FUZHOU | 0 | bulletin 无内容 |
| JIANGXI_NANCHANG | 0 | bulletin 无内容 |
| SHANDONG_JINAN | 7 | |
| HENAN_ZHENGZHOU | 8 | |
| HUBEI_WUHAN | 9 | gdp_total=18866.43 |
| HUNAN_CHANGSHA | 7 | gdp_total MISSING (parser 未匹配) |
| GUANGXI_NANNING | 0 | hongheiku tag 页无 2022 entry |
| HAINAN_HAIKOU | 7 | |
| SICHUAN_CHENGDU | 9 | |
| GUIZHOU_GUIYANG | 9 | |
| YUNNAN_KUNMING | 6 | |
| XIZANG_LASA | 7 | |
| SHAANXI_XIAN | 9 | gdp_total=11486.51 |
| GANSU_LANZHOU | 9 | |
| QINGHAI_XINING | 0 | bulletin 984 chars (tag listing 无内容) |
| NINGXIA_YINCHUAN | 9 | |
| XINJIANG_WULUMUQI | 10 | 唯一全 harvest 10/10, fixed_asset=313.65 |
| TAIWAN_TAIPEI | 0 | hongheiku tag 页无 2022 entry |

### Real cells breakdown:

- **Total cells**: 25 × 10 = 250 (per city × indicator matrix)
- **Real (HONGHEIKU_TRANSLOAD)**: 136 (54.4%)
- **DATA_MISSING**: 114 (45.6%)
  - GUANGXI_NANNING (10) + TAIWAN_TAIPEI (10) = 20 (hongheiku tag 缺)
  - QINGHAI_XINING (10) (tag listing 无内容)
  - fixed_asset % growth excluded: 10 (per 669a-2021 §2 — 守红线-3)
  - 其他 74 (bulletin 内容缺失/parser miss)

## Mart 增量 (knife 669fix-b-2022)

### Apply 结果:

```
Real cells (HONGHEIKU_TRANSLOAD): 136
DATA_MISSING cells: 114
  - fixed_asset % growth: 10
```

### Mart state after apply (2026-09-08):

| 维度 | 值 |
|---|---|
| total rows | 2030 (29 city × 10 indicator × 7 year) |
| real_cells | 607 (471 prev + 136 K669fix-b-2022) |
| cities | 29 (4 669a + 25 669b/fix-b) |
| indicators | 10 |
| years | 7 (2020-2026) |
| 2022 real cells | 173 (K669fix 136 + K669a-2022 37) |
| 2022 DATA_MISSING | 117 (K669fix 114 + K669a-2022 3) |
| ruling versions | 11 (新增 K669fix-b-2022-2026-09-08) |
| HONGHEIKU_TRANSLOAD total | 607 (== real_cells ✓) |

### 2022 ruling × status:

| Ruling | Status | Total | Real |
|---|---|---|---|
| K669a-2022-2026-09-07 | DATA_MISSING | 3 | 0 |
| K669a-2022-2026-09-07 | NULL (real) | 37 | 37 |
| K669fix-b-2022-2026-09-08 | DATA_MISSING | 114 | 0 |
| K669fix-b-2022-2026-09-08 | HONGHEIKU_TRANSLOAD | 136 | 136 |
| **TOTAL 2022** | | **290** | **173** |

## Mart SQL 改动 (knife 669fix-b-2022)

### 文件: `dbt/models/marts/mart_city_timeseries.sql`

**新增**:
- `real_data_669fix_2022 AS (SELECT * FROM (VALUES ...))` CTE (line 801)
- `LEFT JOIN real_data_669fix_2022 rd9` (line 984)
- `COALESCE(rd.value, ..., rd9.value)` 追加 (line 819)

**4 CASE 分支更新** (rd9 优先级高于 rd2 K669a-2022):

1. **status** (line 829-832): rd9 优先
2. **missing_reason** (line 862-870): 4 子分支
   - `GUANGXI_NANNING/TAIWAN_TAIPEI` → hongheiku tag 缺
   - `QINGHAI_XINING` → tag listing 无内容
   - `fixed_asset` → 仅发增长% 无绝对值
   - 其他 → 25 省会 bulletin 未列此 indicator
3. **lineage_source_type** (line 886-887): HONGHEIKU_TRANSLOAD for rd9
4. **lineage_origin** (line 897-898): `tjgb.hongheiku.com/djs/' || cp.city_code`
5. **lineage_ruling** (line 924-929): K669fix-b-2022-2026-09-08 for 25 省会

## 红线守门 (knife 669fix-b-2022 verify)

40/40 PASS:
- A1-A5 (5): schema 不变量 (2030 rows / 29 city / 10 indicator / 7 year / 11 ruling)
- B1 (1): 4 直辖市禁 (守新增红线-7) = 0 rows
- C1 (1): 2001-2019 0 rows (守新增红线-1)
- D1-D2 (2): 2026 290 DATA_MISSING (守新增红线-2)
- E1-E3 (3): real = HONGHEIKU_TRANSLOAD = 607 ✓
- F1-F8 (8): 2022 增量守门 (173/117 split + 21 real cities + 4 669a + 136 K669fix + 114 missing + 8 city all-missing)
- G1-G2 (2): fixed_asset 守红线-3 (1 real XINJIANG / 24 missing)
- H1-H2 (2): lineage_origin tjgb.hongheiku.com 全 non-empty
- I1-I2 (2): 10 indicator_key 全存在
- J1-J4 (4): 不变量 (real ≥ 136 / DATA_MISSING 1423 / 2030 rows / 11 ruling versions)
- K1-K5 (5): 缺失原因完备性 (20+10+10 fixed_asset% + 40 lineage_origin + 117 missing_reason)
- L1-L5 (5): value sanity (SHAANXI 11486.51 / XINJIANG 3893.22 / HUNAN gdp_total MISSING / NEIMENGGU gdp_growth / GUANGDONG_SHENZHEN K669a attribution)

## 提交 + 双推

### 5-commit chain (amend-first v3.5):

实际通过 amend-first 合并为单 commit:

```
d0b660e  feat(669fix-b-2022): 25 省会 × 2022 harvest — 136/250 real (54.4%)
```

**5 files changed, 949 insertions(+), 8 deletions(-)**:
- `dbt/models/marts/mart_city_timeseries.sql` (+50 / -8)
- `scripts/apply_mart_city_669fix_b_2022.py` (+138)
- `scripts/parse_hongheiku_city_y2022_669fix_b.py` (+234)
- `scripts/verify_mart_city_669fix_b_2022.py` (+278)
- `source_registry/seed_hongheiku_city_timeseries_2022.csv` (+250 rows)

### 3 ref verify:

待 push 后执行。

## 复用与依赖

- 复用 `scripts/parse_hongheiku_city_y2021_669fix_b.py` parser v3 strip-first
- 复用 `scripts/apply_mart_city_669fix_b_2021.py` UPDATE-ONLY 模式 + lineage convention
- 复用 `scripts/verify_mart_city_669fix_b_2021.py` 红线 PASS 模式 (40 assertions)
- 复用 mart SQL `real_data_669fix_2020/2021` CTE pattern
- 沿用 665 multi-knife program structure (knife 669fix-b-2020/2021/2022/2023/2024/2025)

## 红线守门 (knife 669fix-b-2022 专属)

- ✓ **25 city × 1 HTTP = 23 HTTP** (≤ 32 红线, 守 batch 约束)
- ✓ **多指标数据只来自 hongheiku** (禁手填, 守新增红线-3)
- ✓ **缺失 city/缺失 indicator 禁补零** (守新增红线-3)
- ✓ **2026 DATA_MISSING 不变** (守新增红线-2)
- ✓ **2001-2019 DATA_MISSING 不变** (守新增红线-1)
- ✓ **4 直辖市禁重复** (守新增红线-7)
- ✓ **lineage_ruling 完整 attribution** (K669fix-b-2022 + K669a-2022 split)
- ✓ **fixed_asset % growth 排除** (守 669a-2021 §2)
- ✓ **mart verify 40/40 红线 PASS**

## 风险与缓解

| 风险 | 缓解 |
|---|---|
| Parser miss HUNAN gdp_total | DATA_MISSING + missing_reason 标注 (守红线-3, 不手填) |
| QINGHAI bulletin 984 chars 无内容 | DATA_MISSING + missing_reason "tag listing 无内容" |
| 8 city 全 DATA_MISSING (bulletin 无) | DATA_MISSING + missing_reason "bulletin 无此 indicator" |
| mart DROP+CREATE 临时丢 real values | apply script UPDATE 重新设回 136 values |
| dbt CLI Python 3.14 不兼容 | psycopg2 直接 CREATE TABLE AS (per 663 Gap 1) |

## 待办 (post-receipt)

1. ✓ 5-commit chain (amend-first v3.5 → single C1)
2. 待 push 双推 (Clash proxy)
3. 待 3 ref verify (HEAD = origin/main = github/main)
4. ✓ 写 receipt (本文件)
5. 待 记忆更新 (china-platform-669fix-b-2022.md)

— End Knife 669fix-b-2022 receipt (Path A 续刀 2/5 DELIVERED, 2026-09-08) —
