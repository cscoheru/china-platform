# knife 669b-i-dongguan receipt — DONGGUAN sub-knife 1/4 DELIVERED (2026-09-10)

## 摘要

knife 669b-i DONGGUAN sub-knife 1/4 (1 batch 4 city × 6 year, DONGGUAN 首城): 47 real + 23 missing = 70 cells 全部入库, **42/42 红线 PASS**, HEAD 待 push。

## 范围 (per AskUserQuestion locked answers)

- **1 batch**: 4 city × 6 year = 24 HTTP
- **4 city**: DONGGUAN + DALIAN + WUXI + SUZHOU (high 收率 优先)
- **节奏**: 单城 6 年 一气呵成 (DONGGUAN 2020-2025 → 下 1 城)

## DONGGUAN 数据点 (knife 669b-i Path A sub-knife 1/4)

| Year | EID | Real | Missing | Notes |
|------|-----|------|---------|-------|
| 2020 | — | 0 | 10 | hongheiku tag 页无 2020 DONGGUAN 公告, 全 DATA_MISSING 守红线-3 |
| 2021 | 25333 | 9 | 1 | fixed_asset 仅发增长%, 守红线-3 |
| 2022 | 42065 | 9 | 1 | fixed_asset 仅发增长% |
| 2023 | 47430 | 9 | 1 | fixed_asset 仅发增长% |
| 2024 | 60152 | 10 | 0 | **保留 Knife F attribution** (K669b-i-batch1-parse-2024) |
| 2025 | 69935 | 10 | 0 | 全 10 指标 real |
| **合计** | — | **47** | **23** | (10 + 3 = 13 in 669b-i-dongguan; 10 stays K669b-i-batch1) |

## HTTP 消耗

- fetch: 4 bulletin × 1 HTTP = **4 HTTP** (在 ≤32 红线内, 余 28 给 dalian/wuxi/suzhou)
- parse: 0 HTTP (纯文件解析)

## mart schema 改动 (5 CASE clauses + 1 LEFT JOIN + 1 CTE)

| mart SQL 位置 | 改动 |
|---|---|
| Line 903-948 | 新增 `real_data_669b_i_dongguan` CTE (37 real cells for 2021/2022/2023/2025) |
| Line 962 | COALESCE 链加 `rd14.value` |
| Line 987 | status CASE 加 DONGGUAN override |
| Line 1060-1063 | missing_reason CASE 加 3 个 DONGGUAN 分支 |
| Line 1079 | lineage_source_type CASE 加 HONGHEIKU_TRANSLOAD 分支 |
| Line 1109-1114 | lineage_origin CASE 加 5 个 DONGGUAN 分支 (4 year eid + 1 tag) |
| Line 1155-1160 | lineage_ruling CASE 加 5 个 DONGGUAN 分支 (4 year parse + 1 fixed_asset + 1 no-bulletin-2020) |
| Line 1218-1222 | LEFT JOIN `real_data_669b_i_dongguan rd14` with `year IN (2021, 2022, 2023, 2025)` |

## 应用方式 (per 663 Gap 1 + 669fix-b-2024 模板)

**直 psql apply** via `scripts/apply_mart_city_669b_i_dongguan.py` (psycopg2 direct, 绕 dbt CLI):
- 读取 `/tmp/669b_i_cache/seed_dongguan_full.csv` (60 rows: 47 real + 13 missing)
- **skip 2024 cells** (10 cells stay as K669b-i-batch1-parse-2024)
- 37 real: UPDATE value + lineage_* (HONGHEIKU_TRANSLOAD, /djs/{eid}.html, K669b-i-dongguan-parse-{YEAR})
- 13 missing: UPDATE status=DATA_MISSING + missing_reason + lineage_*
  - 10 × 2020: K669b-i-dongguan-no-bulletin-2020 (tag 页无 2020 entry)
  - 3 × fixed_asset (2021/2022/2023): K669b-i-dongguan-parse-fixed_asset_growth_pct

## 验证 (42 红线 PASS / 0 FAIL)

```
=== knife 669b-i-dongguan verify (40+ 红线) ===
DB: 127.0.0.1:55440/cegr_test

--- Section 1: cell counts ---  (8/8 PASS)
  ✓ DONGGUAN total cells: 70
  ✓ DONGGUAN real cells: 47
  ✓ DONGGUAN missing cells: 23
  ✓ 2020 missing (守新增红线-3): 10
  ✓ 2021+2022+2023 real: 27
  ✓ 2021+2022+2023 missing (fixed_asset): 3
  ✓ 2024 real (Knife F attribution): 10
  ✓ 2025 real: 10

--- Section 2: per-year real cell breakdown ---  (10/10 PASS)
  ✓ 2021-2025 real cells: 9/9/9/10/10
  ✓ 2021-2023 fixed_asset DATA_MISSING
  ✓ 2024-2025 fixed_asset real

--- Section 3: lineage_ruling attribution ---  (9/9 PASS)
  ✓ Total K669b-i-dongguan rows: 50 (NOT 60; 2024 stays K669b-i-batch1)
  ✓ K669b-i-dongguan-parse-{2021,2022,2023,2025}: 9/9/9/10
  ✓ K669b-i-dongguan-no-bulletin-2020: 10
  ✓ K669b-i-dongguan-parse-fixed_asset_growth_pct: 3
  ✓ 2024 still K669b-i-batch1-2024 (Knife F attribution): 10
  ✓ 2026 still pending (守新增红线-2): 10

--- Section 4: lineage_source_type ---  (5/5 PASS)
  ✓ real cells source=HONGHEIKU_TRANSLOAD: 47
  ✓ 2020 source=DATA_MISSING: 10
  ✓ fixed_asset 21-23 source=DATA_MISSING: 3
  ✓ 2026 status=DATA_MISSING (守新增红线-2): 10
  ✓ real cells status=NULL: 47

--- Section 5: lineage_origin ---  (5/5 PASS)
  ✓ 2021/2022/2023/2025 lineage_origin contains /djs/{25333,42065,47430,69935}: 10 each
  ✓ 2020 lineage_origin contains /tag/东莞市: 10

--- Section 6: missing_reason ---  (5/5 PASS)
  ✓ 2020 missing_reason contains '无 2020 年 DONGGUAN 公告': 10
  ✓ fixed_asset 21-23 missing_reason contains '669通用 parse': 3
  ✓ real cells missing_reason=NULL: 47
  ✓ 2026 missing_reason contains '新增红线-2': 10
  ✓ years <2020 = 0 (守新增红线-1): 0

=== Result: 42 PASS / 0 FAIL ===
```

## 4 直辖市禁重复 守红线-7

DONGGUAN 是广东地级市, **非 4 直辖市** (北京/上海/天津/重庆), 不在 `mart_province_timeseries` 重复维度。

## 红线守门 (669b-i-dongguan 专属)

- ✓ ≤32 HTTP 红线: **4 HTTP** (余 28 给后续 3 城)
- ✓ fixed_asset 增长% → DATA_MISSING: 守红线-3 (增速≠绝对值)
- ✓ 2020 hongheiku 无 entry: 全 DATA_MISSING, 守新增红线-3 禁编造
- ✓ 2024 保留 Knife F attribution (10 cells stay K669b-i-batch1-parse-2024)
- ✓ 2026 保持 pending (守新增红线-2 禁补零)
- ✓ 2001-2019 全 DATA_MISSING (守新增红线-1)
- ✓ 仅来自 hongheiku 采集 (禁手填, 守新增红线-3)
- ✓ DONGGUAN city code `GUANGDONG_DONGGUAN` (非 4 直辖市, 守新增红线-7)
- ✓ 排序禁榜单化 (本刀仅入库, 不暴露排序)
- ✓ docs/81 零改动

## 文件清单

| 路径 | 类型 | 说明 |
|---|---|---|
| `scripts/apply_mart_city_669b_i_dongguan.py` | NEW | 直 psql apply 脚本 (60 → 50 effective, 2024 skip) |
| `scripts/verify_mart_city_669b_i_dongguan.py` | NEW | 42 红线 verify 脚本 |
| `dbt/models/marts/mart_city_timeseries.sql` | M | +1 CTE + 5 CASE clauses + 1 LEFT JOIN (≈60 行新增) |
| `reviews/stage0-gate0-rework-2026-08-23/669b-i-dongguan-receipt-20260910.md` | NEW | 本 receipt |

## 复用与依赖

- 复用 Knife E (969+970) 通用 fetch+parse 脚本 (knife 669b-i-dongguan fetch + parse 路径已 DELIVERED)
- 复用 669fix-b-2024 直 psql apply 模式 (psycopg2 UPDATE-ONLY)
- 复用 mart_city_timeseries.sql 现有 CTE+JOIN 结构 (rd11~rd13 模式)
- 4 HTTP 已消耗 (DONGGUAN tag 4 bulletin fetch)

## 后续 (待 user 裁定 commit/push)

- 5-commit amend-first chain:
  1. `data(669b-i-dongguan): seed_dongguan_full.csv 47 real + 13 missing` (60 rows in /tmp, 不入库 — cache only)
  2. `feat(669b-i-dongguan): apply_mart_city_669b_i_dongguan.py psycopg2 直 psql`
  3. `feat(669b-i-dongguan): mart_city_timeseries.sql real_data_669b_i_dongguan CTE + 5 CASE`
  4. `test(669b-i-dongguan): verify script 42 红线 PASS`
  5. `chore(669b-i-dongguan): receipt (本件)`
- 双推 via Clash proxy: `git -c http.proxy=127.0.0.1:7890 -c https.proxy=127.0.0.1:7890 push origin <branch>`
- 3 ref verify: HEAD = origin/main = github/main

## 下 1 城 (per user 节奏)

DALIAN (LIAONING_DALIAN) sub-knife 2/4 — 沿用 Knife E 通用脚本, ≤4 HTTP fetch + parse + mart apply + verify, 然后 commit/push。

## 不宣称

- ❌ 不宣称 O1 / Gate / M2 / M4 PASS
- ❌ 不冒充 ops — SSH newvps 仅在 user_ruling 签署后
- ❌ 不回写 ops 文件
- ❌ 不爬网 — 4 HTTP 在红线内
- ❌ docs/81 零改动
- ❌ 不宣布 24 里程碑
