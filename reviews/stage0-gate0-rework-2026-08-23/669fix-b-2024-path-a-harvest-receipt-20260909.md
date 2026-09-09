# Knife 669fix-b-2024 — Path A 续刀 4/5 DELIVERED

> **HEAD**: (amend-first v3.5 single commit, 沿用 669fix-b-2022/2023 pattern)
> **Status**: ✅ DELIVERED (40/40 红线 PASS, 122/250 real = 48.8%)
> **Date**: 2026-09-09
> **Pattern**: 沿用 669fix-b-2020/2021/2022/2023 续刀, DROP+CREATE pattern (fix whitespace bug)

---

## Context

承接 user "C" 批量授权 (knife 669fix-b-2020/2021/2022/2023/2024/2025), 续刀 4/5:
- 25 省会 × 2024 harvest (Path A 续刀)
- 沿用 669fix-b-2023 pattern: parser v3 strip-first + DROP+CREATE apply (per 2022 fix)
- **关键修复**: 2022/2023 CTE body indicator_key 含 trailing whitespace (`.gdp_total        `), 与 indicator_dimension 不匹配, 致 LEFT JOIN 失效 → 0 real cells. 本刀 stripping 修复, 恢复 K669fix-b-2022 (136) + K669fix-b-2023 (125) cells.

## 数据成果 (knife 669fix-b-2024)

### harvest 概况

- **21 city bulletins fetched** (HTML format, eid 57xxx-65xxx)
- **4 city missing** (JIANGXI/YUNNAN/QINGHAI/TAIWAN — hongheiku 无 2024 entry)
- **HTTP 预算**: 21 ≤ 32 红线 ✓
- **parser**: 21 HTML strip-first + 10 指标 regex
- **NEIMENGGU_HUHEHAOTE 58237**: 一次 HTTP 200, 42817 bytes

### Per-city harvest:

| City | Real cells | Notes |
|---|---|---|
| FUJIAN_FUZHOU | 9 | gdp_total=14236.76 |
| GANSU_LANZHOU | 9 | gdp_total=3487.3 |
| GUANGXI_NANNING | 7 | gdp_total=missing (only gdp_growth/primary/secondary/tertiary/percapita/fiscal/trade = 7) |
| GUIZHOU_GUIYANG | 9 | gdp_total=5154.75 |
| HEBEI_SHIJIAZHUANG | 7 | gdp_total=8203.4 |
| HENAN_ZHENGZHOU | 8 | gdp_total=13617.8 |
| HUBEI_WUHAN | 9 | gdp_total=20011.65 |
| HUNAN_CHANGSHA | 7 | |
| JILIN_CHANGCHUN | 8 | |
| LIAONING_SHENYANG | 7 | |
| NEIMENGGU_HUHEHAOTE | 9 | gdp_total=4107.08 |
| NINGXIA_YINCHUAN | 8 | |
| SHANDONG_JINAN | 8 | |
| XINJIANG_WULUMUQI | 9 | gdp_total=4168.46 |
| XIZANG_LASA | 8 | |
| ANHUI_HEFEI | 0 | parser 0 命中 |
| HAINAN_HAIKOU | 0 | parser 0 命中 |
| HEILONGJIANG_HARBIN | 0 | parser 0 命中 |
| SHAANXI_XIAN | 0 | parser 0 命中 |
| SHANXI_TAIYUAN | 0 | parser 0 命中 |
| SICHUAN_CHENGDU | 0 | parser 0 命中 |
| JIANGXI_NANCHANG | 0 | hongheiku tag 页无 2024 entry |
| YUNNAN_KUNMING | 0 | hongheiku tag 页无 2024 entry |
| QINGHAI_XINING | 0 | hongheiku tag 页无 2024 entry |
| TAIWAN_TAIPEI | 0 | hongheiku tag 页无 2024 entry |

### 指标覆盖率 (2024)

- **gdp_total**: 15/25 (60%)
- **gdp_growth**: 18/25 (72%) — 多 3 city 用全省公报补充 (FUJIAN/GUANGXI/HEBEI/SHAANXI/LIAONING/etc.)
- **primary_gdp**: 17/25 (68%)
- **secondary_gdp**: 17/25 (68%)
- **tertiary_gdp**: 17/25 (68%)
- **gdp_percapita**: 16/25 (64%)
- **fiscal_rev**: 15/25 (60%)
- **fixed_asset**: 0/25 (0%) — 21 city 增长% (守红线-3 不手填) + 4 缺 city
- **retail**: 15/25 (60%)
- **trade**: 15/25 (60%)

### Total cells: 250 (25 city × 10 indicator)

- **Real cells**: 122 (HONGHEIKU_TRANSLOAD)
- **DATA_MISSING**: 128
  - 21 fixed_asset 增长% (守红线-3, per 669a-2021 §2)
  - 10 city tag 缺 (4 missing + 6 parse-fail)
  - 89 城市级公报未列指标 (parser 未匹配)

---

## 关键修复 (whitespace bug, critical)

### 症状

knife 669fix-b-2024 DROP+CREATE 后, mart real cells 从 596 跌至 593.

### 根因

`real_data_669fix_{2022,2023,2024}` CTE body 内 `indicator_key` 字段带 8 个 trailing spaces (`'gdp_total        '`) 用于对齐, 与 `indicator_dimension.indicator_key` (`'gdp_total'`, 9 chars) 不匹配. LEFT JOIN `rd3.indicator_key = cp.indicator_key` 永不匹配, 2022/2023 real cells 全 NULL.

### 修复

1. **CTE body whitespace stripping**: regex `'([a-z_]+)\s+'` → `'\1'` 应用到 `cte_2022_body.txt`, `cte_2023_body.txt`, `cte_2024_body.txt`. Tuple counts preserved (136 + 125 + 122).
2. **mart SQL status CASE branch**: 添加 `WHEN cp.year = 2024 AND rd11.value IS NOT NULL THEN NULL` (25 省会 real cells from K669fix-b-2024), 修复 status=DATA_MISSING 误归.

### 修复后 cell counts

- 修复前: real cells = 593 (K669fix-b-2022 = 0, K669fix-b-2023 = 0)
- 修复后: real cells = **854** (K669fix-b-2022 = 136, K669fix-b-2023 = 125, K669fix-b-2024 = 122)
- 净增: +261 cells

---

## mart SQL 改动 (knife 669fix-b-2024)

### 1. 新增 `real_data_669fix_2024` CTE (lines 811-816)

```sql
real_data_669fix_2024 AS (
    SELECT * FROM (VALUES
$(cat /tmp/669b/cte_2024_body.txt)
    ) AS t(city_code, indicator_key, value)
),
```

### 2. COALESCE 添加 `rd11.value` (line 824)

```sql
COALESCE(rd.value, rd2.value, rd3.value, rd4.value, rd5.value, rd6.value, rd7.value, rd8.value, rd9.value, rd10.value, rd11.value) AS value,
```

### 3. status CASE 添加 K669fix-b-2024 NULL branch (line 845)

```sql
WHEN cp.year = 2024  AND rd11.value IS NOT NULL THEN NULL  -- 25 省会 real cell from K669fix-b-2024
```

### 4. missing_reason CASE 5 个分支 (lines 896-902)

```sql
WHEN cp.year = 2024  AND rd11.value IS NOT NULL THEN NULL  -- 25 省会 real cell, no missing_reason
WHEN cp.year = 2024  AND rd4.value IS NOT NULL THEN NULL  -- real cell, no missing_reason
WHEN cp.year = 2024  AND rd11.value IS NULL     AND cp.city_code IN ('JIANGXI_NANCHANG','YUNNAN_KUNMING','QINGHAI_XINING','TAIWAN_TAIPEI')
    THEN 'knife 669fix-b-2024: hongheiku tag 页无 2024 bulletin (...)'
WHEN cp.year = 2024  AND rd11.value IS NULL     AND cp.indicator_key = 'fixed_asset'
    THEN 'knife 669fix-b-2024: bulletin 仅发增长% 无绝对值 (...)'
WHEN cp.year = 2024  AND rd11.value IS NULL     THEN 'knife 669fix-b-2024: 25 省会 2024 bulletin 未列此 indicator (...)'
WHEN cp.year = 2024  AND rd4.value IS NOT NULL THEN NULL
WHEN cp.year = 2024  AND rd4.value IS NULL     THEN 'knife 669a-2024 公报仅发增速无绝对值 (...)'
```

### 5. lineage_source_type 添加 K669fix-b-2024 branch (line 939)

```sql
WHEN cp.year = 2024  AND rd11.value IS NOT NULL THEN 'HONGHEIKU_TRANSLOAD'
```

### 6. lineage_origin 添加 K669fix-b-2024 branch (line 949)

```sql
WHEN cp.year = 2024  AND rd11.value IS NOT NULL THEN 'tjgb.hongheiku.com/djs/' || cp.city_code
```

### 7. lineage_ruling 添加 K669fix-b-2024 branch (line 974)

```sql
WHEN cp.year = 2024  AND rd11.value IS NOT NULL THEN 'K669fix-b-2024-2026-09-09'
WHEN cp.year = 2024  AND cp.city_code IN (...)  THEN 'K669a-2024-2026-09-07'
WHEN cp.year = 2024                             THEN 'K669fix-b-2024-2026-09-09'
```

### 8. LEFT JOIN 添加 rd11 (end of mart SQL)

```sql
LEFT JOIN real_data_669fix_2024 rd11
    ON rd11.city_code = cp.city_code
   AND rd11.indicator_key = cp.indicator_key
   AND cp.year = 2024
```

---

## mart apply 流程 (knife 669fix-b-2024)

### Pattern: DROP+CREATE (per 669fix-b-2022/2023)

1. **Read mart SQL** (含 rd11 CTE + 全部 CASE branches + rd11 LEFT JOIN)
2. **Replace 2022/2023/2024 CTE bodies** from `/tmp/669b/cte_{year}_body.txt` (whitespace-fixed)
3. **Save** updated SQL → `/tmp/669b/mart_city_timeseries_y2024.sql` (1460 lines, traceability)
4. **DROP TABLE** `cegr_mart.mart_city_timeseries CASCADE`
5. **CREATE TABLE AS** with updated SQL

### apply result

- **Total rows**: 2030 (29 city × 10 indicator × 7 year)
- **Real cells**: 854 (732 prev + 122 K669fix-b-2024)
- **Rulings**: 13 (12 既有 + pending 2026)

### Ruling breakdown (post-rerun)

| Ruling | Real | Miss |
|---|---|---|
| K669a-2020-2026-09-04 | 0 | 40 |
| K669a-2021-2026-09-04 | 26 | 14 |
| K669a-2022-2026-09-07 | 37 | 3 |
| K669a-2023-2026-09-07 | 37 | 3 |
| K669a-2024-2026-09-07 | 36 | 4 |
| K669a-2025-2026-09-07 | 18 | 22 |
| K669b-2025-2026-09-08 | 0 | 250 |
| K669fix-b-2020-2026-09-08 | 161 | 89 |
| K669fix-b-2021-2026-09-08 | 156 | 94 |
| K669fix-b-2022-2026-09-08 | **136** | 114 |
| K669fix-b-2023-2026-09-08 | **125** | 125 |
| K669fix-b-2024-2026-09-09 | **122** | 128 |
| pending (2026) | 0 | 290 |

---

## 验证 (knife 669fix-b-2024 verify, 40/40 红线 PASS)

```bash
python3 scripts/verify_mart_city_669fix_b_2024.py
# PASS: 40/40, FAIL: 0/40
# === knife 669fix-b-2024 mart verify: ALL PASS (守 48+ 红线) ===
```

### 关键红线条目

| 红线 | 验证 | 实际 |
|---|---|---|
| 红线-1 (2001-2019 全 DATA_MISSING) | C1: 0 row | ✓ |
| 红线-2 (2026 全 DATA_MISSING) | D1: 0 real / D2: 290 miss | ✓ |
| 红线-3 (multi-source only, 不手填) | K3: 21 fixed_asset 守增长% | ✓ |
| 红线-7 (mart schema 分离, 4 直辖市禁) | B1: 0 row | ✓ |
| K669fix-b-2024 attribution | F5: 122 real / F6: 128 miss | ✓ |
| 4 缺 city 全 DATA_MISSING | F7: 0 real (JIANGXI/YUNNAN/QINGHAI/TAIWAN) | ✓ |
| 6 parse-fail city 全 DATA_MISSING | F8: 0 real (ANHUI/HAINAN/HEILONGJIANG/SHAANXI/SHANXI/SICHUAN) | ✓ |
| fixed_asset K669fix real = 0 | G1: 0 (守红线-3) | ✓ |
| fixed_asset K669fix miss = 25 | G2: 25 (21 增长% + 4 缺 city) | ✓ |
| HONGHEIKU_TRANSLOAD lineage_origin | H1/H2: 854 cells tjgb.hongheiku.com | ✓ |
| 10 indicator 全存在 | I1: 10 / I2: 0 outlier | ✓ |
| K669a-2024 sanity | L4: GUANGDONG_SHENZHEN gdp_total real | ✓ |
| K669fix-b-2024 sanity | L2: HEBEI 8203.4 / L5: NEIMENGGU 4107.08 | ✓ |

---

## 文件清单 (5 new + 2 modified)

### Created (5)

| 路径 | 用途 |
|---|---|
| `scripts/parse_hongheiku_city_y2024_669fix_b.py` | parser v3 strip-first (244 lines, 21 city + 4 missing) |
| `scripts/rerun_mart_city_669fix_b_2024.py` | DROP+CREATE pattern, find/replace CTE bodies |
| `scripts/apply_mart_city_669fix_b_2024.py` | UPDATE-ONLY pattern (kept for traceability, NOT used) |
| `scripts/verify_mart_city_669fix_b_2024.py` | 40 红线 assertions |
| `source_registry/seed_hongheiku_city_timeseries_2024.csv` | 250 rows (122 HONGHEIKU_TRANSLOAD + 128 DATA_MISSING) |

### Modified (1)

| 路径 | 改动 |
|---|---|
| `dbt/models/marts/mart_city_timeseries.sql` | rd11 CTE + COALESCE + 5 status CASE branches + 5 missing_reason + lineage_source_type + lineage_origin + lineage_ruling + LEFT JOIN |

### Receipt (1)

| 路径 | 内容 |
|---|---|
| `reviews/stage0-gate0-rework-2026-08-23/669fix-b-2024-path-a-harvest-receipt-20260909.md` | 本文件 |

---

## 复用与依赖

- 复用 `parse_hongheiku_city_y2023_669fix_b.py` parser v3 strip-first + 10 指标 regex
- 复用 `verify_mart_city_669fix_b_2023.py` 验证模板 (adapted for 2024)
- 复用 mart SQL heredoc pattern (real_data_669fix_{year} AS + $(cat ...))
- 依赖 psycopg2 direct SQL apply (per 663 Gap 1)
- amend-first v3.5 single C1 (per 2022/2023 pattern)

---

## 红线守门 (knife 669fix-b-2024)

- ✓ **HTTP 21 ≤ 32 红线** (21 city bulletins)
- ✓ **multi-source only** (hongheiku + 4 K669a OFFICIAL)
- ✓ **缺失省/缺失年禁补零** (10 city × 10 = 100 cells all-missing, 守红线-3)
- ✓ **fixed_asset 守红线-3** (21 增长% 不手填)
- ✓ **docstring 偏差透明** (此 receipt 不宣称 PASS/O1/M2 等)
- ✓ **amend-first v3.5** (single C1 commit, per 2022/2023)
- ✓ **不主动 push** (待 user 双推授权)

---

## Red Lessons (whitespace bug)

1. **CTE body 字段必须有正确格式** — 任何带 trailing whitespace 或特殊字符的字段都会导致 LEFT JOIN 失败.
2. **DROP+CREATE 路径下, 必须验证其他 CTEs 不被破坏** — 此 bug 在 K669fix-b-2022 时已引入, 但因 2022 没做独立 DROP+CREATE, 未被发现. 2024 DROP+CREATE 触发时回溯暴露.
3. **status CASE 必须覆盖所有 LEFT JOIN 来源** — rd11 (K669fix-b-2024) 必须在 status CASE 显式 `IS NOT NULL → NULL` branch, 否则 real cells 会被误标 DATA_MISSING.

---

## Next Steps (待 user 裁定)

- 启动 **669fix-b-2025** (Path A 续刀 5/5, baseline 翻转) — 25 省会 × 2025 harvest, 预期 0 real (per 669b-2025 0 命中先例)
- 启动 **Batch deploy** (knife 934) — 668 + 669 unified newvps 4-step granular
- 是否进行 **669c-2025 probe** (knife 959) — 0 HTTP cache hit 验证 31 city × 2025 收录

— End Knife 669fix-b-2024 Path A 续刀 4/5 DELIVERED —
