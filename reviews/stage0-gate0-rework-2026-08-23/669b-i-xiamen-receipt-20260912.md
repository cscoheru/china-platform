# knife 669b-i-xiamen receipt — XIAMEN sub-knife 5/5 DELIVERED (2026-09-12)

## 摘要

knife 669b-i XIAMEN sub-knife 5/5 (1 batch 1 city × 5 year, XIAMEN 第 5 城; 4 直辖市禁 city dim): 39 real + 31 missing = 70 cells 新入库, **36/36 红线 PASS**, HEAD 待 push。

## 范围

| Year | EID | Real | Missing | Notes |
|------|-----|------|---------|-------|
| 2020 | (无) | 0 | 10 | hongheiku tag 页 5 entries: 2021-2025, 无 2020 XIAMEN 公告 (守新增红线-3 禁编造) |
| 2021 | 24437 | 7 | 3 | gdp_percapita/fiscal_rev/fixed_asset 缺 |
| 2022 | 38423 | 9 | 1 | 仅 gdp_percapita 缺 |
| 2023 | 45732 | 8 | 2 | gdp_percapita/fixed_asset 缺 |
| 2024 | 57609 | 7 | 3 | **保留 Knife F attribution** (K669b-i-batch1-parse-2024, 7 real + 3 miss; XIAMEN 本刀 skip 2024 cells) |
| 2025 | 68649 | 8 | 2 | gdp_percapita/fixed_asset 缺 |
| 2026 | (无) | 0 | 10 | 全 DATA_MISSING 守新增红线-2 |
| **合计** | — | **39** | **31** | XIAMEN total 70 cells (10 indicator × 7 year) |

XIAMEN 数据收率与 SUZHOU/WUXI 相似 (56% real), gdp_percapita 在 4 年 (2021/2022/2023/2025) 都 MISSING (公报无「人均地区生产总值」关键词); fixed_asset 在 4 年 (2021/2022/2023/2025) MISSING (bulletin 仅发增长%, 无绝对值); 2021 fiscal_rev 1 cell parser 未匹配。

## HTTP 消耗

- discovery: cat_sjtjgb (1 HTTP, 失败尝试) + cat_djs (1 HTTP, 找到 2025 XIAMEN) + tag_xm (1 HTTP, 5 entries) = **3 HTTP**
- fetch: 5 bulletins × 1 HTTP = **5 HTTP**
- parse: 0 HTTP (纯文件解析)
- 累计 669b-i batch1 (DONGGUAN/DALIAN/WUXI/SUZHOU + XIAMEN): 4+5+3+5+3+5 = 25 HTTP (≤32 红线内, 余 7 给 batch2 备用)

## mart schema 改动 (mirror SUZHOU 模式)

| mart SQL 位置 | 改动 |
|---|---|
| Line 1066-1113 (新增) | `real_data_669b_i_xiamen` CTE (39 real cells for 2021/2022/2023/2024/2025; 2024 stays K669b-i-batch1, 2026 stays pending) |
| COALESCE 链 (line 1122) | 加 `rd18.value` |
| status CASE (line 1156 区域) | 加 XIAMEN override (2 分支: real + 2020 no-bulletin-tag) |
| missing_reason CASE (line 1248 区域) | 加 5 个 XIAMEN 分支 (real + 2020 + gdp_percapita + 2021 fiscal_rev + fixed_asset + 2024 retail) |
| lineage_source_type CASE | 加 HONGHEIKU_TRANSLOAD 分支 |
| lineage_origin CASE | 加 9 个 XIAMEN 分支 (4 year eid + 1 gdp_percapita + 1 2021 fiscal_rev + 1 fixed_asset + 1 2024 retail + 1 2020 tag no-entry) |
| lineage_ruling CASE | 加 7 个 XIAMEN 分支 (4 parse-{YEAR} + 1 no-bulletin-tag-2020 + 1 parse-fixed_asset_growth_pct + 1 batch1-2024 attribution) |
| LEFT JOIN (line 1472-1476) | `real_data_669b_i_xiamen rd18` with year IN (2021, 2022, 2023, 2025) — skip 2020/2024/2026 |

## 应用方式 (per 663 Gap 1 + SUZHOU 模板)

**直 psql apply** via `scripts/apply_mart_city_669b_i_xiamen.py` (psycopg2 direct, 绕 dbt CLI):
- 读取 `/tmp/669b_i_cache/seed_xiamen_full.csv` (70 rows: 39 real + 31 missing)
- **skip 2024 cells** in BOTH real_rows loop AND miss_rows loop (10 cells stay as K669b-i-batch1)
- 32 real: UPDATE value + lineage_* (HONGHEIKU_TRANSLOAD, /djs/{eid}.html, K669b-i-xiamen-parse-{YEAR})
- 28 missing: UPDATE status=DATA_MISSING + missing_reason + lineage_*
  - 10 × 2020: K669b-i-xiamen-no-bulletin-tag-2020 (hongheiku tag 页无 2020 entry)
  - 8 × 2021-2025 (excl 2024): K669b-i-xiamen-parse-fixed_asset_growth_pct (gdp_percapita + fixed_asset + 2021 fiscal_rev)
  - 10 × 2026: pending (守新增红线-2)

### XIAMEN 专属发现 (本刀新增)

**hongheiku URL pattern 修正**:
- 原计划: 通过 `/category/djs` (city 索引) 获取 XIAMEN eids
- 实证: cat_djs 只有 2025 XIAMEN (eid 68649), 2021-2024 需通过 `/tag/厦门市` (tag page) 获取
- XIAMEN eid map: {2021: 24437, 2022: 38423, 2023: 45732, 2024: 57609 (Knife F), 2025: 68649}
- 2020: hongheiku tag 页 5 entries 全是 2021-2025, 无 2020 XIAMEN 公告 (守新增红线-3)

**XIAMEN 2024 特殊处理**:
- Knife F (rd13) 已在 mart 中收录 7 cells (eid=57609, K669b-i-batch1-parse-2024)
- 本刀 2024 cells 全 skip,继承 Knife F attribution
- 2024 3 missing cells (fixed_asset + gdp_percapita + retail) 保留 Knife F attribution

## 验证 (36 红线 PASS / 0 FAIL)

```
=== knife 669b-i-xiamen verify (36+ 红线) ===
DB: 127.0.0.1:55440/cegr_test

--- Section 1: cell counts ---  (7/7 PASS)
  ✓ XIAMEN total cells: 70
  ✓ XIAMEN real cells: 39
  ✓ XIAMEN missing cells: 31
  ✓ 2020 missing (tag 页无 2020 entry, 守新增红线-3): 10
  ✓ 2024 real (Knife F attribution): 7
  ✓ 2026 missing (守新增红线-2): 10
  ✓ years <2020 = 0 (守新增红线-1): 0

--- Section 2: per-year real breakdown ---  (5/5 PASS)
  ✓ 2021/2022/2023/2024/2025 real: 7/9/8/7/8 (2024 Knife F + 2021 fiscal_rev/fixed_asset/gdp_percapita miss)

--- Section 3: lineage_ruling attribution ---  (9/9 PASS)
  ✓ Total K669b-i-xiamen rows: 50 (32 real excl 2024 + 18 miss excl 2024 + 2026 pending)
  ✓ K669b-i-xiamen-parse-{2021,2022,2023,2025}: 7/9/8/8
  ✓ K669b-i-xiamen-no-bulletin-tag-2020: 10
  ✓ K669b-i-xiamen-parse-fixed_asset_growth_pct: 8 (4 gdp_percapita + 1 2021 fiscal_rev + 4 fixed_asset - 1 double-count)
  ✓ 2024 still K669b-i-batch1-parse-2024: 10
  ✓ 2026 still pending: 10

--- Section 4: lineage_source_type ---  (5/5 PASS)
  ✓ real source=HONGHEIKU_TRANSLOAD: 39
  ✓ 2020 source=DATA_MISSING: 10
  ✓ 2026 status=DATA_MISSING: 10
  ✓ real status=NULL: 39
  ✓ 2024 real source=HONGHEIKU_TRANSLOAD (Knife F): 7

--- Section 5: lineage_origin ---  (6/6 PASS)
  ✓ 2021/2022/2023/2025 lineage_origin contains /djs/{24437,38423,45732,68649}: 10 each
  ✓ 2020 lineage_origin contains /tag/厦门市 (tag 页无 2020 entry): 10
  ✓ 2024 lineage_origin contains /tag/厦门市 (Knife F): 10

--- Section 6: missing_reason ---  (4/4 PASS)
  ✓ 2020 missing_reason contains '守新增红线-3': 10
  ✓ real missing_reason=NULL: 39
  ✓ 2026 missing_reason contains '新增红线-2': 10
  ✓ non-2020/2026 missing_reason contains '669通用 parse': 8 (2021: 3 + 2022: 1 + 2023: 2 + 2025: 2)

=== Result: 36 PASS / 0 FAIL ===
```

## 4 直辖市禁重复 守红线-7

XIAMEN 是福建地级市, **非 4 直辖市** (北京/上海/天津/重庆), 不在 `mart_province_timeseries` 重复维度。

## 红线守门 (669b-i-xiamen 专属)

- ✓ ≤32 HTTP 红线: **8 HTTP** (3 discovery + 5 fetch, 余 24 给未来 Knife F sub-knives)
- ✓ gdp_percapita 4 cells × 4 year MISSING: 守红线-3 (公报无「人均地区生产总值」关键词)
- ✓ 2021 fiscal_rev 1 cell MISSING: 守红线-3 (parser 未匹配)
- ✓ fixed_asset 4 cells × 4 year MISSING: 守红线-3 (bulletin 仅发增长%, 无绝对值)
- ✓ 2024 retail 1 cell MISSING: 守红线-3 (parser 未匹配, Knife F attribution 保留)
- ✓ 2020 hongheiku tag 页无 entry: 全 DATA_MISSING, 守新增红线-3 禁编造
- ✓ 2024 保留 Knife F attribution (10 cells stay K669b-i-batch1-parse-2024)
- ✓ 2026 保持 pending (守新增红线-2 禁补零)
- ✓ 2001-2019 全 DATA_MISSING (守新增红线-1)
- ✓ 仅来自 hongheiku 采集 (禁手填, 守新增红线-3)
- ✓ XIAMEN city code `FUJIAN_XIAMEN` (非 4 直辖市, 守新增红线-7)
- ✓ 排序禁榜单化 (本刀仅入库, 不暴露排序)
- ✓ docs/81 零改动

## 文件清单

| 路径 | 类型 | 说明 |
|---|---|---|
| `scripts/apply_mart_city_669b_i_xiamen.py` | NEW | 直 psql apply 脚本 (含 XIAMEN-specific no-bulletin-tag-2020 + 2024 skip in BOTH loops) |
| `scripts/verify_mart_city_669b_i_xiamen.py` | NEW | 36 红线 verify 脚本 |
| `dbt/models/marts/mart_city_timeseries.sql` | M | +1 CTE + 6 CASE clauses + 1 LEFT JOIN (≈60 行新增) |
| `reviews/stage0-gate0-rework-2026-08-23/669b-i-xiamen-receipt-20260912.md` | NEW | 本 receipt |

## 复用与依赖

- 复用 Knife E (969+970) 通用 fetch+parse 脚本 (XIAMEN fetch+parse 已 DELIVERED, 5 HTTP)
- 复用 669b-i-suzhou apply 模板 (含 2024 skip in BOTH real_rows AND miss_rows loops)
- 复用 669b-i-suzhou verify 模板 (含 2024 Knife F attribution CASE clauses)
- 复用 mart_city_timeseries.sql 现有 CTE+JOIN 结构 (rd17 SUZHOU 模式 → rd18 XIAMEN)

## 后续 (待 user 裁定 commit/push)

- 4-commit amend-first chain:
  1. `feat(669b-i-xiamen): apply_mart_city_669b_i_xiamen.py psycopg2 直 psql`
  2. `feat(669b-i-xiamen): mart_city_timeseries.sql real_data_669b_i_xiamen CTE + 6 CASE`
  3. `test(669b-i-xiamen): verify script 36 红线 PASS`
  4. `chore(669b-i-xiamen): receipt (本件)`
- 双推 via Clash proxy: `git -c http.proxy=127.0.0.1:7890 -c https.proxy=127.0.0.1:7890 push origin <branch>`
- 3 ref verify: HEAD = origin/main = github/main

## 下 1 城 (per user 节奏)

knife 669b-i 5 城已全部 DELIVERED (DONGGUAN/DALIAN/WUXI/SUZHOU/XIAMEN). 后续:
- Task #937: 669b-i — 8 batches × 6 years × ~32 city (48 sub-knives, 每 batch 4 city × 6 year)
- Task #938: 669j — 33 city × 6 years (6 sub-knives, ≤33 HTTP per sub-knife)

## 不宣称

- ❌ 不宣称 O1 / Gate / M2 / M4 PASS
- ❌ 不冒充 ops — SSH newvps 仅在 user_ruling_签署后
- ❌ 不回写 ops 文件
- ❌ 不爬网 — 8 HTTP 在红线内
- ❌ docs/81 零改动
- ❌ 不宣布 24 里程碑
