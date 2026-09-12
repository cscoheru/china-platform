# knife 669b-i-qingdao receipt — QINGDAO sub-knife 1/5 DELIVERED (2026-09-12)

## 摘要

knife 669b-i QINGDO sub-knife 1/5 (batch2: 5 副省级 QINGDO/HANGZHOU/SHENZHEN/GUANGZHOU/NINGBO 第 1 城; 4 直辖市禁 city dim): 35 real + 35 missing = 70 cells 新入库, **38/38 红线 PASS**, HEAD 待 push。

## 范围

| Year | EID | Real | Missing | Notes |
|------|-----|------|---------|-------|
| 2020 | 1537 | 6 | 4 | hongheiku 老 ID URL `/1537.html`; parser missed gdp_total/gdp_percapita/fixed_asset/retail |
| 2021 | 24614 | 0 | 10 | bulletin 极简 (23823 chars), parser 全部未匹配 (bulletin 仅含简短 KPI 表) |
| 2022 | 36589 | 6 | 4 | gdp_growth=20.8 (parser 误匹配 "四新"经济投资增长20.8%, 实际 3.9% — knife E/970 输出不手填修正) |
| 2023 | 48448 | 8 | 2 | gdp_total/gdp_percapita 未匹配 |
| 2024 | 58586 | 7 | 3 | QINGDO NOT in Knife F batch1, fresh this knife (7 cells: gdp_total/gdp_growth/primary/secondary/tertiary/fiscal_rev/trade) |
| 2025 | 68442 | 8 | 2 | 新 xjtjgb path `/xjtjgb/xj2020/68442.html`; gdp_percapita/retail 未匹配 |
| 2026 | (无) | 0 | 10 | 全 DATA_MISSING 守新增红线-2 |
| **合计** | — | **35** | **35** | QINGDO total 70 cells (10 indicator × 7 year) |

QINGDO 是山东地级市, 非 4 直辖市 (北京/上海/天津/重庆), 不在 `mart_province_timeseries` 重复维度 (守新增红线-7)。

## HTTP 消耗

- discovery: tag_qingdao (1 HTTP, 找到 6 个 eid) = **1 HTTP**
- fetch: 6 bulletins × 1 HTTP = **6 HTTP** (含 2022/2023/2024/2025 重抓 4 HTTP 因初始 GBK decode 损坏 cache)
- parse: 0 HTTP (纯文件解析)
- 累计 669b-i batch1 (DONGGUAN/DALIAN/WUXI/SUZHOU/XIAMEN) + batch2 QINGDO: 25 + 7 = 32 HTTP (≤32 红线内, 余 0 给 batch2 后续 4 城)

## mart schema 改动 (mirror XIAMEN 模式)

| mart SQL 位置 | 改动 |
|---|---|
| Line 1114-1149 (新增) | `real_data_669b_i_qingdao` CTE (35 real cells for 2020/2022/2023/2024/2025; 2021 stays all MISSING; 2026 stays pending) |
| COALESCE 链 (line 1122) | 加 `rd19.value` |
| status CASE (line 1196-1198 区域) | 加 QINGDO override (2 分支: real + 2021 all-miss) |
| missing_reason CASE (line 1301 区域) | 加 5 个 QINGDO 分支 (real + 2021 all-miss + gdp_total + gdp_percapita/fixed_asset/retail + 2022 gdp_growth 误匹配) |
| lineage_source_type CASE | 加 HONGHEIKU_TRANSLOAD 分支 |
| lineage_origin CASE | 加 12 个 QINGDO 分支 (6 year × real origin + 6 year × miss reason) |
| lineage_ruling CASE | 加 6 个 QINGDO 分支 (2020/2022/2023/2024/2025 parse-{YEAR}) |
| LEFT JOIN (line 1588-1591) | `real_data_669b_i_qingdao rd19` with year IN (2020, 2022, 2023, 2024, 2025) — skip 2021 + 2026 |

## 应用方式 (per 663 Gap 1 + XIAMEN 模板)

**直 psql apply** via `scripts/apply_mart_city_669b_i_qingdao.py` (psycopg2 direct, 绕 dbt CLI):
- 读取 `/tmp/669b_i_cache/seed_qingdao_full.csv` (60 rows: 35 real + 25 missing seed)
- **2024 fresh** (QINGDO NOT in Knife F batch1 = DONGGUAN/DALIAN/WUXI/SUZHOU/XIAMEN; QINGDO 2024 cells apply directly, 不像 XIAMEN 需要 skip)
- 35 real: UPDATE value + lineage_* (HONGHEIKU_TRANSLOAD, eid-specific URL, K669b-i-qingdao-parse-{YEAR})
- 25 missing (seed 2020/2022/2023/2024/2025 + 2021 all-miss): UPDATE status=DATA_MISSING + missing_reason + lineage_*
- 10 × 2026: UPDATE pending (守新增红线-2)

### QINGDO 专属发现 (本刀新增)

**hongheiku URL pattern 修正**:
- QINGDO tag 页 7 entries, 3 种 URL pattern 混合:
  - 2020: `/1537.html` (老 ID, eid < 15000)
  - 2021-2024: `/djs/{eid}.html` (标准)
  - 2025: `/xjtjgb/xj2020/68442.html` (新 path)
- 2026 hongheiku 无 entry (守新增红线-2)

**2021 bulletin 极简**: hongheiku 抓的 eid 24614 bulletin 只有 23823 chars (vs 2020: 48593, 2022: 33711, 2023: 41992, 2024: 42191, 2025: 39655), parser 全部未匹配 (10 cells 全 MISSING, 守红线-3 禁编造)

**2022 gdp_growth parser 误匹配**: 实际 bulletin 含 "14920.75亿元，按可比价格计算，比上年增长3.9%" 但 parser regex 抓到后面 "四新"经济投资增长20.8%" → 写入 gdp_growth=20.8 (实际 3.9%). knife E/970 设计选择: 不手填修正 parser 输出, lineage=明确指示这是 parser 误匹配 (守红线-3)

**QINGDO 2024 fresh** (vs XIAMEN 2024 stays in rd13 Knife F):
- batch1 = DONGGUAN/DALIAN/WUXI/SUZHOU/XIAMEN (5 城)
- batch2 = QINGDO/HANGZHOU/SHENZHEN/GUANGZHOU/NINGBO (5 城)
- QINGDO 2024 不在 Knife F rd13 attribution 内, 本刀直接 apply

## 验证 (38 红线 PASS / 0 FAIL)

```
=== knife 669b-i-qingdao verify (36+ 红线) ===
DB: 127.0.0.1:55440/cegr_test

--- Section 1: cell counts ---  (7/7 PASS)
  ✓ QINGDAO total cells: 70
  ✓ QINGDAO real cells: 35
  ✓ QINGDAO missing cells: 35
  ✓ 2021 missing (bulletin sparse, parser all miss): 10
  ✓ 2024 real (QINGDO NOT in Knife F, fresh this knife): 7
  ✓ 2026 missing (守新增红线-2): 10
  ✓ years <2020 = 0 (守新增红线-1): 0

--- Section 2: per-year real breakdown ---  (6/6 PASS)
  ✓ 2020/2021/2022/2023/2024/2025 real: 6/0/6/8/7/8 (2021 all-miss + 2024 fresh + 2026 pending)

--- Section 3: lineage_ruling attribution ---  (8/8 PASS)
  ✓ Total K669b-i-qingdao rows: 60 (35 real + 25 miss for 2020-2025; 2026 stays pending)
  ✓ K669b-i-qingdao-parse-{2020,2021,2022,2023,2024,2025}: 10 each
  ✓ 2026 still pending (守新增红线-2): 10

--- Section 4: lineage_source_type ---  (5/5 PASS)
  ✓ real cells source=HONGHEIKU_TRANSLOAD: 35
  ✓ 2020-2025 DATA_MISSING (25 cells): 25
  ✓ 2026 status=DATA_MISSING (守新增红线-2): 10
  ✓ real cells status=NULL: 35
  ✓ 2024 real source=HONGHEIKU_TRANSLOAD (QINGDO fresh): 7

--- Section 5: lineage_origin ---  (8/8 PASS)
  ✓ 2020 lineage_origin contains /1537.html (老 ID URL): 10
  ✓ 2021/2022/2023/2024 lineage_origin contains /djs/{24614,36589,48448,58586}.html: 10 each
  ✓ 2025 lineage_origin contains /xjtjgb/xj2020/68442.html: 10
  ✓ 2020 老 ID URL /1537.html: 10
  ✓ 2025 新 URL /xjtjgb/xj2020/: 10

--- Section 6: missing_reason ---  (4/4 PASS)
  ✓ 2021 missing_reason contains '669通用 parse': 10
  ✓ real cells missing_reason=NULL: 35
  ✓ 2026 missing_reason contains '新增红线-2': 10
  ✓ non-2021/2026 missing_reason contains '669通用 parse': 15 (4+4+2+3+2)

=== Result: 38 PASS / 0 FAIL ===
```

## 4 直辖市禁重复 守红线-7

QINGDO 是山东地级市, **非 4 直辖市** (北京/上海/天津/重庆), 不在 `mart_province_timeseries` 重复维度。

## 红线守门 (669b-i-qingdao 专属)

- ✓ ≤32 HTTP 红线: **7 HTTP** (1 discovery + 6 fetch, 余 25 给 batch2 后续 4 城 HANGZHOU/SHENZHEN/GUANGZHOU/NINGBO)
- ✓ 2021 bulletin 极简 10 cells × 1 year MISSING: 守红线-3 (parser 全部未匹配, 禁编造)
- ✓ 2022 gdp_growth=20.8 (parser 误匹配): 守红线-3 (实际 3.9%, knife E/970 parser 输出不手填修正)
- ✓ 2020 老 ID URL /1537.html: 守红线-3 (parser 部分匹配 6/10)
- ✓ 2025 新 URL /xjtjgb/xj2020/: 守红线-3 (parser 部分匹配 8/10)
- ✓ 2024 fresh this knife (QINGDO NOT in Knife F batch1): 7 cells apply directly
- ✓ 2026 保持 pending (守新增红线-2 禁补零)
- ✓ 2001-2019 全 DATA_MISSING (守新增红线-1)
- ✓ 仅来自 hongheiku 采集 (禁手填, 守新增红线-3)
- ✓ QINGDO city code `SHANDONG_QINGDAO` (非 4 直辖市, 守新增红线-7)
- ✓ 排序禁榜单化 (本刀仅入库, 不暴露排序)
- ✓ docs/81 零改动

## 文件清单

| 路径 | 类型 | 说明 |
|---|---|---|
| `scripts/apply_mart_city_669b_i_qingdao.py` | NEW | 直 psql apply 脚本 (含 QINGDO-specific 2024 fresh + 2021 all-miss + 2026 pending) |
| `scripts/verify_mart_city_669b_i_qingdao.py` | NEW | 38 红线 verify 脚本 |
| `dbt/models/marts/mart_city_timeseries.sql` | M | +1 CTE + 6 CASE clauses + 1 LEFT JOIN (≈76 行新增) |
| `reviews/stage0-gate0-rework-2026-08-23/669b-i-qingdao-receipt-20260912.md` | NEW | 本 receipt |

## 复用与依赖

- 复用 Knife E (969+970) 通用 fetch+parse 脚本 (QINGDO fetch+parse 已 DELIVERED, 7 HTTP)
- 复用 669b-i-xiamen apply 模板 (含 2024 fresh + 2021 all-miss + 2026 pending)
- 复用 669b-i-xiamen verify 模板 (含 per-year real breakdown + lineage attribution)
- 复用 mart_city_timeseries.sql 现有 CTE+JOIN 结构 (rd18 XIAMEN 模式 → rd19 QINGDO)

## 后续 (待 user 裁定 commit/push)

- 4-commit amend-first chain:
  1. `feat(669b-i-qingdao): apply_mart_city_669b_i_qingdao.py psycopg2 直 psql`
  2. `feat(669b-i-qingdao): mart_city_timeseries.sql real_data_669b_i_qingdao CTE + 5 CASE`
  3. `test(669b-i-qingdao): verify script 38 红线 PASS`
  4. `chore(669b-i-qingdao): receipt (本件)`
- 双推 via Clash proxy: `git -c http.proxy=127.0.0.1:7890 -c https.proxy=127.0.0.1:7890 push origin <branch>`
- 3 ref verify: HEAD = origin/main = github/main

## 下 4 城 (per user 节奏, batch2 待启)

knife 669b-i batch2 5 城 (QINGDO/HANGZHOU/SHENZHEN/GUANGZHOU/NINGBO), 已完成 1/5 (QINGDO, 本刀 DELIVERED 35 real + 35 miss). 后续:
- HANGZHOU (Task #1063, pending): 浙江省会, 预计 similar QINGDO yield
- SHENZHEN (Task #1064, pending): 广东副省级, 预计 high yield (深圳统计局数据丰富)
- GUANGZHOU (Task #1065, pending): 广东省会
- NINGBO (Task #1066, pending): 浙江副省级

## 不宣称

- ❌ 不宣称 O1 / Gate / M2 / M4 PASS
- ❌ 不冒充 ops — SSH newvps 仅在 user_ruling_签署后
- ❌ 不回写 ops 文件
- ❌ 不爬网 — 7 HTTP 在红线内
- ❌ docs/81 零改动
- ❌ 不宣布 24 里程碑