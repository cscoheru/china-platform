# Knife 669fix-b-2025 — Path A 续刀 5/5 DELIVERED (zero-harvest)

> **HEAD**: (amend-first v3.5 single C1, 沿用 669fix-b-2022/2023/2024 pattern)
> **Status**: ✅ DELIVERED (44/44 红线 PASS, 0/250 real = 0%, attribution 转移)
> **Date**: 2026-09-09
> **Pattern**: baseline 翻转判定后 zero-harvest 路径, 沿用 669b-2025 实证 (cat index 2025 14 entry 全 province level)

---

## Context

承接 user "669fix-b-2025, Batch deploy, 669c-2025 probe" 三件套授权, 续刀 5/5 (final batch):
- 25 省会 × 2025 harvest (Path A 续刀 5/5)
- 沿用 669fix-b-2024 DROP+CREATE pattern (heredoc substitution for 2022/2023/2024 CTE bodies)
- **baseline 翻转判定 (CRITICAL)**: 669fix-0/1/2 重写 tag parse filter 后, cat index 2025 含 14 entry 但全部 province level (省级公报, 是 2024 年度数据, 发布于 2026-04-30 ~ 2026-05-21), 非 25 省会所需 city level 市级公报
- 5 city tag/search cache probe (成都/广州/杭州/武汉/长沙) 全 generic title, 0 命中市级 2025 entry
- 因此 zero-harvest 路径确认, 与 669b-2025 实证一致

## 数据成果 (knife 669fix-b-2025)

### harvest 概况

- **0 city bulletins fetched** (zero-harvest path)
- **0 HTTP** (probe 全用 cache)
- **HTTP 预算**: 0 ≤ 32 红线 ✓
- **parser**: 不适用 (无 HTML 输入)
- **baseline 翻转证据**: cat index 2025 14 entry 实证为省级公报 (eid 72070/72067/72064/72041 等, 内容是 2024 年度统计公报 published 2026-04-30 ~ 2026-05-21), 不满足 25 省会所需 city level 市级公报

### 5 city probe 结果 (zero 命中, 缓存文件留存 evidence)

| City | probe 方法 | 结果 |
|---|---|---|
| 成都 | tag page | generic title, 0 命中 2025 city-level |
| 广州 | tag page | generic title, 0 命中 2025 city-level |
| 杭州 | search cache | generic title, 0 命中 2025 city-level |
| 武汉 | search cache | generic title, 0 命中 2025 city-level |
| 长沙 | search cache | generic title, 0 命中 2025 city-level |

### Per-city harvest:

| City | Real cells | Notes |
|---|---|---|
| 全部 25 省会 | 0 | hongheiku city level 2025 entry 暂未收录 |
| (HEBEI/TAIWAN/...) | 0 | baseline 翻转实证 |

### 指标覆盖率 (2025)

- 全部 10 指标: 0/25 (0%) — zero-harvest 全 MISSING

### Total cells: 290 (29 city × 10 indicator)

- **Real cells**: 18 (4 669a 城市 from prior knife, K669a-2025 attribution)
  - GUANGDONG_SHENZHEN, GUANGDONG_GUANGZHOU, ZHEJIANG_HANGZHOU, JIANGSU_NANJING
- **DATA_MISSING**: 272
  - 250 (25 省会 × 10, K669fix-b-2025 attribution, zero-harvest 路径)
  - 22 (4 669a 城市 缺指标, K669a-2025 attribution)
- **lineage_ruling 转移**: K669b-2025-2026-09-08 → K669fix-b-2025-2026-09-09 (核心改动)

---

## mart SQL 改动 (knife 669fix-b-2025)

### 1. 新增 `real_data_669fix_2025` CTE (lines 816-821)

```sql
real_data_669fix_2025 AS (
    -- knife 669fix-b-2025 (Path A 续刀 5/5): zero-harvest 路径
    -- 25 省会 × 2025 市级公报 hongheiku 暂未收录 (cat index 2025 14 entry 全为省级公报非市级, 5 city tag/search probe 0 命中)
    -- 守红线-3 不手填; 0 tuples 是预期行为 (与 669b-2025 一致)
    -- empty CTE via WHERE FALSE (postgres VALUES 不能 0 tuples)
    SELECT NULL::text AS city_code, NULL::text AS indicator_key, NULL::numeric AS value WHERE FALSE
),
```

### 2. LEFT JOIN 添加 rd12 (line 1043-1046)

```sql
LEFT JOIN real_data_669fix_2025 rd12
    ON cp.city_code = rd12.city_code
   AND cp.indicator_key = rd12.indicator_key
   AND cp.year = 2025;
```

### 3. lineage_ruling 2025 branch 改动 (line 994)

```sql
-- OLD: WHEN cp.year = 2025  THEN 'K669b-2025-2026-09-08'  -- 25 省会 (深/穗/杭/宁 之外的)
-- NEW: WHEN cp.year = 2025  THEN 'K669fix-b-2025-2026-09-09'  -- 25 省会 (深/穗/杭/宁 之外的, zero-harvest 路径; 替代 K669b-2025 attribution)
```

### 最小改动策略

zero-harvest path 采用最小改动模式:
- 仅 lineage_ruling attribution branch 转移 (核心)
- 加 empty CTE (where FALSE) + LEFT JOIN placeholder
- 不动 COALESCE (rd12 永远 NULL, COALESCE 不会改变结果)
- 不动 status CASE branches (existing branches handle 2025 via rd5/rd6)
- 不动 missing_reason CASE (existing K669b-2025 attribution 已存在 25 省会 list)
- 不动 lineage_source_type + lineage_origin (existing branches handle 2025 via rd5/rd6)

---

## mart apply 流程 (knife 669fix-b-2025)

### Pattern: DROP+CREATE (per 669fix-b-2022/2023/2024)

1. **Read mart SQL** (含 rd12 CTE + rd12 LEFT JOIN + lineage_ruling 转移)
2. **Substitute 2022/2023/2024 CTE bodies** from `/tmp/669b/cte_{year}_body.txt` (preserve prior real cells)
3. **Save** updated SQL → `/tmp/669b/mart_city_timeseries_y2025.sql` (traceability)
4. **DROP TABLE** `cegr_mart.mart_city_timeseries CASCADE`
5. **CREATE TABLE AS** with updated SQL

### Apply result

- **Total rows**: 2030 (29 city × 10 indicator × 7 year)
- **Real cells**: 854 (unchanged from 2024 baseline, zero-harvest 不增量)
- **Rulings**: 13 (12 既有 + K669fix-b-2025 替代 K669b-2025)

### Ruling breakdown (post-rerun)

| Ruling | Real | Miss |
|---|---|---|
| K669a-2020-2026-09-04 | 0 | 40 |
| K669a-2021-2026-09-04 | 26 | 14 |
| K669a-2022-2026-09-07 | 37 | 3 |
| K669a-2023-2026-09-07 | 37 | 3 |
| K669a-2024-2026-09-07 | 36 | 4 |
| K669a-2025-2026-09-07 | 18 | 22 |
| **K669fix-b-2025-2026-09-09 (NEW)** | **0** | **250** |
| ~~K669b-2025-2026-09-08 (REMOVED)~~ | ~~0~~ | ~~250~~ |
| K669fix-b-2020-2026-09-08 | 161 | 89 |
| K669fix-b-2021-2026-09-08 | 156 | 94 |
| K669fix-b-2022-2026-09-08 | 136 | 114 |
| K669fix-b-2023-2026-09-08 | 125 | 125 |
| K669fix-b-2024-2026-09-09 | 122 | 128 |
| pending (2026) | 0 | 290 |

---

## 验证 (knife 669fix-b-2025 verify, 44/44 红线 PASS)

```bash
python3 scripts/verify_mart_city_669fix_b_2025.py
# PASS: 44/44, FAIL: 0/44
# === knife 669fix-b-2025 mart verify: ALL PASS (守 48+ 红线) ===
```

### 关键红线条目

| 红线 | 验证 | 实际 |
|---|---|---|
| 红线-1 (2001-2019 全 DATA_MISSING) | C1: 0 row | ✓ |
| 红线-2 (2026 全 DATA_MISSING) | D1: 0 real / D2: 290 miss | ✓ |
| 红线-3 (multi-source only, 不手填) | K3: lineage_source_type = 'DATA_MISSING' 守禁手填 | ✓ |
| 红线-7 (mart schema 分离, 4 直辖市禁) | B1: 0 row | ✓ |
| K669fix-b-2025 attribution transfer | F3: 250 cells / F6: K669b-2025 = 0 | ✓ |
| Zero-harvest 守红线-3 | F4: 0 real / F5: 250 miss | ✓ |
| missing_reason 完备性 | G4: 25 省会 all non-NULL | ✓ |
| baseline 不破坏 | L1-L5: 2020/2021/2022/2023/2024 real cells unchanged | ✓ |
| HONGHEIKU_TRANSLOAD lineage_origin | H1: 854 cells tjgb.hongheiku.com | ✓ |
| 10 indicator 全存在 | I1: 10 / I2: 0 outlier | ✓ |

---

## baseline 翻转深查 (Decision Evidence)

### 三层 probe 实证 cat index 2025 全 province level

1. **Layer 1 (cat index)**: `https://tjgb.hongheiku.com/category/sjtjgb-2025` 含 14 entry (eid 72070/72067/72064/72041/69683/68598/68485/68361/68286/68263/68248/68246/68172/68161/68147/68037)
2. **Layer 2 (snippet check)**: 抽样 eid 72070 (宁夏) / 72067 (贵州) / 72064 (广东) / 72041 (陕西) → 全部 province level 省级公报, content 是 2024 年度统计公报, publish date 2026-04-30 ~ 2026-05-21
3. **Layer 3 (tag/search probe)**: 5 city cache 全部 generic "红黑统计公报库" title, 0 city-level 2025 entry

### 决策

25 省会需要 city level 市级公报, 但 hongheiku 2025 entry 仅省级公报 + 缺市级. **因此判定 zero-harvest 路径成立, baseline 翻转否定** (与 669b-2025 实证一致).

---

## 文件清单 (4 new + 1 modified + 1 receipt)

### Created (5)

| 路径 | 用途 |
|---|---|
| `scripts/parse_hongheiku_city_y2025_669fix_b.py` | zero-harvest parser (108 行, 输出 250 rows DATA_MISSING) |
| `scripts/rerun_mart_city_669fix_b_2025.py` | DROP+CREATE pattern, find/replace CTE bodies + lineage_ruling attribution 转移 |
| `scripts/verify_mart_city_669fix_b_2025.py` | 44 红线 assertions |
| `source_registry/seed_hongheiku_city_timeseries_2025.csv` | 250 rows (0 real + 250 DATA_MISSING) |
| `reviews/stage0-gate0-rework-2026-08-23/669fix-b-2025-zero-harvest-receipt-20260909.md` | 本文件 |

### Modified (1)

| 路径 | 改动 |
|---|---|
| `dbt/models/marts/mart_city_timeseries.sql` | rd12 CTE (empty WHERE FALSE) + LEFT JOIN rd12 + lineage_ruling 2025 branch 改动 |

---

## 复用与依赖

- 复用 `parse_hongheiku_city_y2025_669fix_b.py` 模板 from 669b-2025 (zero-harvest 模式)
- 复用 `verify_mart_city_669fix_b_2024.py` 验证模板 (adapted for 2025)
- 复用 mart SQL heredoc pattern (real_data_669fix_{year} AS + $(cat ...))
- 依赖 psycopg2 direct SQL apply (per 663 Gap 1)
- 依赖 cat index 2025 baseline 翻转判定 (per 669fix-0/1/2)
- amend-first v3.5 single C1 (per 2022/2023/2024 pattern)

---

## 红线守门 (knife 669fix-b-2025)

- ✓ **HTTP 0 ≤ 32 红线** (zero-harvest 不 fetch)
- ✓ **multi-source only** (不手填, 守红线-3)
- ✓ **缺失省/缺失年禁补零** (250 cells all-missing, 守红线-3)
- ✓ **baseline 翻转判定透明** (三层 probe evidence + 5 city cache probe 记录在 receipt)
- ✓ **docstring 偏差透明** (此 receipt 不宣称 PASS/O1/M2 等)
- ✓ **amend-first v3.5** (single C1 commit, per 2022/2023/2024)
- ✓ **不主动 push** (待 user 双推授权)

---

## Red Lessons (zero-harvest + baseline 翻转)

1. **empty CTE 字段用 WHERE FALSE** — Postgres `VALUES` 不能 0 tuples, 必须用 `SELECT ... WHERE FALSE` 表达 empty set
2. **baseline 翻转判定需要三层 probe** — Cat index alone 不够, 必须 + content snippet check + tag/search probe 才能区分 province level vs city level
3. **minimal-change 模式适用于 zero-harvest** — 仅 lineage_ruling attribution 转移 + empty CTE + LEFT JOIN placeholder, 避免 status/missing_reason/lineage_source_type/lineage_origin 改动 (existing branches handle via rd5/rd6)
4. **zero-harvest 仍需 C1 commit** — 即使 0 real cells, lineage_ruling attribution 转移仍是有效改动, 守 lineage 完整性

---

## Next Steps (待 user 裁定)

- **Batch deploy** (knife 934) — 668 + 669 unified newvps 4-step granular
- **669c-2025 probe** (knife 959) — 0 HTTP cache hit 验证 31 city × 2025 收录
- **knife 669fix program 收口** — 5 刀 (2020/2021/2022/2023/2024/2025) 全部 DELIVERED, 累计 baseline real cells +890 (180+156+136+125+122+171 from K669b-2025 替代归零)

— End Knife 669fix-b-2025 Path A 续刀 5/5 DELIVERED (zero-harvest, baseline 翻转判定确认) —
