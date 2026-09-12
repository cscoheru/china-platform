# knife 669b-i batch2 receipt — 4 副省级 city sub-knife DELIVERED (2026-09-13)

## 摘要

knife 669b-i batch2 (2026-09-13): 4 副省级 city harvest (SHENZHEN/GUANGZHOU/HANGZHOU/NINGBO) × 5 years (2021-2025) × 10 indicators = **200 cells (172 real / 28 missing)**, **49/49 红线 PASS**, HEAD 待 push。

## 范围 (4 副省级 city × 5 year × 10 indicator = 200 cells)

| City | Province | Year range | Cells | Real | Miss |
|---|---|---|---|---|---|
| GUANGDONG_SHENZHEN (深圳) | GUANGDONG | 2021-2025 | 50 | 45 | 5 |
| GUANGDONG_GUANGZHOU (广州) | GUANGDONG | 2021-2025 | 50 | 43 | 7 |
| ZHEJIANG_HANGZHOU (杭州) | ZHEJIANG | 2021-2025 | 50 | 40 | 10 |
| ZHEJIANG_NINGBO (宁波) | ZHEJIANG | 2021-2025 | 50 | 44 | 6 |
| **合计** | | **2021-2025** | **200** | **172** | **28** |

## HTTP 消耗

- Knife E 通用 fetch+parse 复用 (per 969+970): 4 city × 5 year × 1 HTTP = **20 HTTP** (在 32 红线内, 余 12)
- 实际 669b-i-qingdao 已用 4 HTTP + xiamen 4 HTTP + qingdao 5 HTTP + sundry = 复用 Knife E 0 额外 HTTP

## mart schema 改动

| mart SQL 位置 | 改动 |
|---|---|
| Line 1160-1365 (新增) | `real_data_669b_i_batch2` CTE — 172 VALUES tuples, 4 city × 5 year × real cells (per-city grouping with URL pattern comments) |
| Line 1386 (COALESCE 链) | 加 `rd21.value` |
| Line 1422-1428 (status CASE) | 4 city real/2020/2021-2025 partial miss 三段 |
| Line 1545-1568 (missing_reason CASE) | 4 city × 5 year × 7 类原因 (per-cell attribution) |
| Line 1594-1595 (lineage_source_type CASE) | 4 city rd21.value IS NOT NULL → HONGHEIKU_TRANSLOAD |
| Line 1681-1720 (lineage_origin CASE) | 4 city × 5 year URL mapping (20 eids) + DATA_MISSING explanations |
| Line 1782-1796 (lineage_ruling CASE) | 4 city × 5 year K669b-i-batch2-parse-{year}-2026-09-13 + DATA_MISSING paths |
| Line 1926-1930 (LEFT JOIN) | `real_data_669b_i_batch2 rd21` with year BETWEEN 2021 AND 2025 |

## 应用方式 (per 663 Gap 1 + 669b-i-qingdao UPDATE-ONLY 模式)

**直 psql apply** via `scripts/apply_mart_city_669b_i_batch2.py` (psycopg2 direct, 绕 dbt CLI):

- **UPDATE-ONLY** (4 副省级 city 已在 mart with prior cells from K669a-2020/2021/2022/2023/2024 + K669fix-b 路径)
- 200 rows updated: 172 real (HONGHEIKU_TRANSLOAD, value/missing_reason/lineage_*) + 28 DATA_MISSING (status/missing_reason/lineage_*)
- lineage_source_type: real → 'HONGHEIKU_TRANSLOAD', miss → 'DATA_MISSING'
- lineage_ruling: real/miss → K669b-i-batch2-parse-{year}-2026-09-13 (5 versions: 2021-2025)
- lineage_is_demo: 'false' (继承, 不变)

### 设计决策: UPDATE-only vs INSERT-only

**为啥 batch2 用 UPDATE-only**:
- 4 副省级 city (SHENZHEN/GUANGZHOU/HANGZHOU/NINGBO) 在 mart 已有 cells (from K669a-2020 + K669a-2021..2024 + K669fix-b-2025):
  - SHENZHEN/GUANGZHOU/HANGZHOU 2021-2024: K669a 路径 (9 real + 1 miss per year)
  - NINGBO 2021-2025: K669fix-b 路径 (0 real + 10 miss per year, 因为 K669a NINGBO 数据缺失, 后续归入 25 省会)
- batch2 UPDATE 替换 status/lineage_ruling/origin/source_type, 保留 value (real cells) 或 NULL (miss cells)
- 2020 cells 保持 K669a-2020-2026-09-04 ruling (历史年不重复注入, 守新增红线-1)
- 2026 cells 保持 K669fix-b-2026-2026-09-09 ruling (守新增红线-2 不补零)

**INSERT-only 适用于 5 粤 卫星城 (ZHUHAI/ZHANJIANG/SHANTOU/JIANGMEN/ZHAOQING) per 669j-1** (mart 里 0 prior cells)

## 验证 (49 红线 PASS / 0 FAIL)

```
=== knife 669b-i batch2 verify (49+ 红线) ===
DB: 127.0.0.1:55440/cegr_test table=cegr_mart.mart_city_timeseries

  --- Section 1: total batch2 cell counts (2021-2025) ---
  ✓ 4 city × 5 year × 10 indicator = 200 cells
  ✓ real cells (172)
  ✓ DATA_MISSING cells (28)
  ✓ All 200 cells tagged K669b-i-batch2-*
  ✓ Real cells: status=NULL, missing_reason=NULL

  --- Section 2: per-city real cell count ---
  ✓ GUANGDONG_SHENZHEN real cells: 45
  ✓ GUANGDONG_GUANGZHOU real cells: 43
  ✓ ZHEJIANG_HANGZHOU real cells: 40
  ✓ ZHEJIANG_NINGBO real cells: 44

  --- Section 3: per-city MISSING cell count ---
  ✓ GUANGDONG_SHENZHEN DATA_MISSING: 5
  ✓ GUANGDONG_GUANGZHOU DATA_MISSING: 7
  ✓ ZHEJIANG_HANGZHOU DATA_MISSING: 10
  ✓ ZHEJIANG_NINGBO DATA_MISSING: 6

  --- Section 4: per-year real cell count ---
  2021: 29, 2022: 36, 2023: 36, 2024: 35, 2025: 36 real cells (4 city)

  --- Section 5: per-year MISSING cell count ---
  2021: 11, 2022: 4, 2023: 4, 2024: 5, 2025: 4 DATA_MISSING cells (4 city)

  --- Section 6: lineage_ruling 5 year versions ---
  ✓ K669b-i-batch2-parse-2021 (40 cells)
  ✓ K669b-i-batch2-parse-2022 (40 cells)
  ✓ K669b-i-batch2-parse-2023 (40 cells)
  ✓ K669b-i-batch2-parse-2024 (40 cells)
  ✓ K669b-i-batch2-parse-2025 (40 cells)

  --- Section 7: lineage_source_type ---
  ✓ real cells source_type=HONGHEIKU_TRANSLOAD: 172
  ✓ miss cells source_type=DATA_MISSING: 28
  ✓ real cells NOT HONGHEIKU_TRANSLOAD = 0
  ✓ miss cells missing_reason 必填

  --- Section 8: lineage_origin per-year total ---
  ✓ 2021-2025 lineage_origin 含 hongheiku.com (40 cells each year)

  --- Section 9: missing_reason attribution ---
  ✓ fixed_asset 增长% cells (13): 13
  ✓ GUANGZHOU 2021 parse miss (6 cells)
  ✓ HANGZHOU 2021-2025 parse miss (6 cells)
  ✓ NINGBO 2024/2025 parse miss (3 cells)
  ✓ All 28 miss cells lineage_ruling = K669b-i-batch2-*

  --- Section 10: cross product sanity ---
  ✓ 4 city distinct
  ✓ 10 indicator distinct
  ✓ 5 year distinct (2021-2025)
  ✓ 4 city × 5 year × fixed_asset = 20 cells

  --- Section 11: red lines ---
  ✓ 4 直辖市禁重复 (新增红线-7): 0
  ✓ 4 city × 2020 全部 DATA_MISSING (新增红线-1): 0
  ✓ 4 city × 2026 全部 DATA_MISSING (新增红线-2): 0

=== Result: 49 PASS / 0 FAIL ===
```

## 守红线 (新增/沿用)

- ✓ **新增红线-1** (2001-2019 全 DATA_MISSING, 禁编造历史): 4 city × 2020 = 40 DATA_MISSING (covered by K669a-2020)
- ✓ **新增红线-2** (2026 全 DATA_MISSING, 禁补零): 4 city × 2026 = 40 DATA_MISSING (covered by K669fix-b-2026)
- ✓ **新增红线-3** (禁手填/禁补零/禁爬第三方): 28 DATA_MISSING cells 全部从 hongheiku 采集推断, 0 手填; 13 fixed_asset 增长% 排除 per 669a-2021 §2
- ✓ **新增红线-4** (Recharts 仅时序): N/A (本刀不涉及前端)
- ✓ **新增红线-6** (multi-knife program, 每刀独立 user_ruling): per 669j-sketch 6 sub-knives 各独立签署; batch2 是 669b-i program 内的 sub-knife
- ✓ **新增红线-7** (mart province/city 分离, 4 直辖市禁 city dim): 4 副省级 city ≠ BEIJING/SHANGHAI/TIANJIN/CHONGQING

## 复用与依赖

- 复用 969+970 通用 fetch+parse (Knife E 收口, 2026-09-09)
- 复用 669b-i-qingdao UPDATE-ONLY pattern (per 663 Gap 1)
- 复用 669j-1 INSERT-only pattern (NO-OP 路径不同, batch2 是真实 harvest)
- 复用 mart schema 现有 indicator_dimension (10 indicator × label × unit)
- 依赖 mart 当前 41 city (NOT +5 粤, just UPDATE 4 副省级 city)
- 依赖 docs/87 §3.2 P2 数据扩展 (knife 669 范围)
- 5 commits (amend-first v3.5)

## Per-cell attribution 详情 (28 miss breakdown)

| 城市 | Year | Indicator | Reason |
|---|---|---|---|
| SHENZHEN | 2021-2025 | fixed_asset × 5 | 增长% (守红线-3, per 669a-2021 §2) |
| GUANGZHOU | 2021 | gdp_total/gdp_growth/primary_gdp/secondary_gdp/tertiary_gdp/gdp_percapita × 6 | bulletin 极简, parser 未匹配 |
| GUANGZHOU | 2021 | fixed_asset × 1 | 增长% |
| HANGZHOU | 2021 | primary_gdp × 1 | parser 未匹配 |
| HANGZHOU | 2021-2023, 2025 | fixed_asset × 4 | 增长% |
| HANGZHOU | 2022 | gdp_total × 1 | parser 未匹配 |
| HANGZHOU | 2023 | gdp_total × 1 | parser 未匹配 |
| HANGZHOU | 2024 | fixed_asset × 1 | parser 未匹配 |
| HANGZHOU | 2024 | retail × 1 | parser 未匹配 |
| HANGZHOU | 2025 | gdp_total × 1 | parser 未匹配 |
| NINGBO | 2021-2023 | fixed_asset × 3 | 增长% |
| NINGBO | 2024 | fixed_asset × 1 | parser 未匹配 |
| NINGBO | 2024 | trade × 1 | parser 未匹配 |
| NINGBO | 2025 | fixed_asset × 1 | parser 未匹配 |

Total: 13 fixed_asset 增长% + 15 parse miss = 28 ✓

## 调试诊断 (2 bugs fixed)

1. **UnboundLocalError on PASS counter**: 直接 `PASS += 1` 在 main() 内无 `global PASS, FAIL` 声明, Python 视为局部变量。修复: 加 `global PASS, FAIL` 在 main() 起始.
2. **Verify assertion counts off**: HANGZHOU parse miss 是 6 不是 5 (primary_gdp 2021, gdp_total 2022/2023/2025, fixed_asset 2024, retail 2024); "669b-i batch2" attribution 仅在 13 增长% cells, 全部 28 miss 应该用 lineage_ruling LIKE 'K669b-i-batch2-%' 验证.

## 关联决策

- **knife 669b-i program** (per Task #937): 8 batches × 6 years × ~32 city (48 sub-knives), batch2 是其中之一 (4 副省级 city priority)
- **669b-i-qingdao** (2026-09-12, sub-knife 1/5 batch2): 同 UPDATE-ONLY pattern, 35 real + 35 miss
- **669b-i-xiamen** (2026-09-12, sub-knife 1 batch2): 同 pattern, 35 real + 35 miss
- **knife 969+970** (2026-09-09, 收口): 通用 fetch+parse 脚本, batch2 复用
- **knife E parse** (`scripts/parse_hongheiku_city_indicators_669fix.py` line 71): explicit "X% suffix for fixed_asset growth-only (will be marked DATA_MISSING per 669a-2021 §2)"

## 后续

- batch2 5 commits + push 双推待 user 授权
- 669b-i program 续刀: 其他 4 副省级 city / 重点 city sub-knives

— End knife 669b-i batch2 receipt (4 副省级 city × 200 cells, 172 real / 28 miss, 49/49 红线 PASS, HEAD 待 push) —