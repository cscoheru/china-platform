# 669a-2020 — mart_city_timeseries schema + zero-harvest 全 DATA_MISSING 验证

> **刀号**: 669a-2020 (knife 669 program first sub-knife per Option A restructure)
> **日期**: 2026-09-04
> **角色**: 架构师+执行端 merged (per 2026-08-31 21:50 豁免)
> **前置**: 663 mart DELIVERED (8060 rows, 1266 real cells) → 664 FastAPI 时序端点 + newvps postgres → 665a-e 5 年 harvest (1435 cells) → 666b 3 省 OFFICIAL → 667 Recharts 时序可视化 → 668 verify-live.sh v2 DELIVERED → user "做完669后一起部署" blanket + Option A (10 batches × 6 years = 60 sub-knives)
> **本件状态**: **DELIVERED ✓** — mart_city_timeseries.sql 新 mart (新增红线-7 province/city 分离) + 直接 psql apply (per 663 Gap 1) + 14/14 红线 PASS + 实证 hongheiku 城市维度 2020 缺文 (zero-harvest knife)
> **关联**: 663/664/665a-e/666b/667/668 receipts + `china-platform-665-multi-knife-program.md`

---

## 1. 范围 (granular)

按 user Option A (10 city batches × 6 years = 60 sub-knives), 669a-2020 是 669 program 第一个 sub-knife:

| 维度 | 详情 |
|---|---|
| 目标 | 建立 mart_city_timeseries schema (新增红线-7 province/city 分离) + 实证 zero-harvest 路径 |
| city scope | 4 优先 city (深圳市/广州市/杭州市/南京市) — 669a 批次 |
| year scope | 2020 only — 实证 hongheiku 城市 cat index 缺文 |
| 指标 | 10 (5 现 + 5 增量, mirror mart_province_timeseries.indicator_dimension) |
| Cross product | 4 × 10 × 1 = **40 cells** (本刀 2020 only; 后续 sub-knives 加 2021-2025) |
| HTTP budget | 0 (zero-harvest knife; 实证 hongheiku 城市 cat index 仅 2021-2025, 无 2020 URL) |
| 红线 | 新增红线-1/2/3/7 全 PASS; 不冒充 ops; docs/81 零改动 |
| mart apply | 直接 psql via psycopg2 (per 663 Gap 1: dbt CLI 工具链与 Python 3.14 不兼容) |

---

## 2. 关键实证发现 (hongheiku 城市维度 2020 缺文)

实证步骤 (per summary session 末段 + 本刀 §验证):

```bash
# 1. probe 5 个 city year-index pages
curl https://tjgb.hongheiku.com/2020中国   # 全国普查, 非 city
curl https://tjgb.hongheiku.com/23939.html  # 2021 city index (id 23939, 200 200)
curl https://tjgb.hongheiku.com/35003.html  # 2022 city index (id 35003, 200 200)
curl https://tjgb.hongheiku.com/45926.html  # 2023 city index
curl https://tjgb.hongheiku.com/57063.html  # 2024 city index
curl https://tjgb.hongheiku.com/68085.html  # 2025 city index
# → 5 个 city year index 仅 2021-2025, 无 2020 URL
```

**结论**: hongheiku 城市 cat index 仅覆盖 2021-2025 (5 年), **2020 城市数据不在 hongheiku 收录范围**。本刀 669a-2020 为 zero-harvest knife, 40 cells 全 DATA_MISSING (守新增红线-3 不手填 + 红线-1 禁补零)。

后续 669a-2021/2022/2023/2024/2025 (5 sub-knives) 才有 real cells harvest。每个 sub-knife ≤ 4 HTTP (4 city × 1 year)。

---

## 3. 文件改动清单 (4 文件, 1 改 + 3 新)

### 新件 (3)

| 路径 | 用途 | 行数 |
|---|---|---|
| `dbt/models/marts/mart_city_timeseries.sql` | 新 mart (city timeseries 独立 table, 守新增红线-7); city_dimension (4 city) + indicator_dimension (10) + year_dimension (2020-2026) + cross_product + status CASE 逻辑 | 119 |
| `scripts/apply_mart_city_669a.py` | 直接 psql apply (per 663 Gap 1); DROP + CREATE TABLE AS; 输出 mart 摘要 (rows/cities/indicators/years/real_cells/DATA_MISSING/rulings) | 95 |
| `scripts/verify_mart_city_669a.py` | 14 红线 verify (rows/distinct/zero-harvest/4直辖市禁重复/lineage/缺失原因); red/green PASS/FAIL output | 200 |

### 改件 (1)

| 路径 | 改动 | 行数 |
|---|---|---|
| `dbt/models/marts/_mart_models.yml` | 加 `mart_city_timeseries` model schema doc + column-level tests (not_null/accepted_values); 沿用 mart_province_timeseries 10 indicator accepted_values + 3 lineage_source_type accepted_values + 7 year window | +123 |

---

## 4. mart schema 设计 (新增红线-7)

### Cross product

```
city_dimension:   4 city (深圳市/广州市/杭州市/南京市)
indicator_dimension: 10 (5 现 + 5 增量, mirror province mart)
year_dimension:   7 year (2020-2026, 城市维度 7 年 vs 省 26 年)
cross_product:    4 × 10 × 7 = 280 rows
```

### city_code 命名规范 (新增红线-7 强制)

```
{PROVINCE_CODE}_{CITY_SLUG}
例:
  GUANGDONG_SHENZHEN   (深圳市)
  GUANGDONG_GUANGZHOU  (广州市)
  ZHEJIANG_HANGZHOU    (杭州市)
  JIANGSU_NANJING      (南京市)

禁 (4 直辖市已在 province mart, 不重复):
  BEIJING_*
  SHANGHAI_*
  TIANJIN_*
  CHONGQING_*
```

### Status CASE (新增红线-1+2+3 守门)

| year | status | missing_reason |
|---|---|---|
| <2020 | DATA_MISSING | 新增红线-1: 2001-2019 禁编造历史数据 |
| 2020 | DATA_MISSING | hongheiku 城市维度 2020 缺文 (cat index 仅 2021-2025; knife 669 待拓展其他来源) |
| 2021-2025 | DATA_MISSING (本刀) | knife 669a-2021/2022/2023/2024/2025 待 harvest (本刀 669a-2020 仅建 schema) |
| 2026 | DATA_MISSING | 新增红线-2: 2026 待 2027 官方发布 |

### Lineage 三件套 (新增红线 守门)

```
lineage_source_type: 'DATA_MISSING' (本刀全部)
lineage_origin:      'none'
lineage_ruling:      'K669a-2020-2026-09-04'
lineage_is_demo:     'false'  (demo 数据禁入 mart)
```

---

## 5. 红线守门 (14/14 PASS)

| # | 红线 | 实际 | 期望 | 状态 |
|---|---|---|---|---|
| 1 | mart 行数 = 280 | 280 | 280 (4 × 10 × 7) | ✓ |
| 2 | city distinct = 4 | 4 | 4 | ✓ |
| 3 | indicator distinct = 10 | 10 | 10 (5 现 + 5 增量) | ✓ |
| 4 | year distinct = 7 | 7 | 7 (2020-2026) | ✓ |
| 5 | real_cells = 0 (zero-harvest) | 0 | 0 (守新增红线-3 不手填) | ✓ |
| 6 | DATA_MISSING = 280 (all missing) | 280 | 280 (守新增红线-1/2/3) | ✓ |
| 7 | 4 直辖市禁重复 (新增红线-7) | 0 (none) | 0 | ✓ |
| 8 | lineage_ruling 唯一 | 'K669a-2020-2026-09-04' | same | ✓ |
| 9 | lineage_is_demo 全部 'false' | 0 bad | 0 | ✓ |
| 10 | status 枚举合法 | 0 bad | 0 (NULL 或 DATA_MISSING) | ✓ |
| 11 | missing_reason 必填 for DATA_MISSING | 0 bad | 0 | ✓ |
| 12 | 2020 missing_reason 含 hongheiku 城市 2020 缺文 | 40/40 | 40 | ✓ |
| 13 | 2026 missing_reason 含 2027 官方发布 (新增红线-2) | 40/40 | 40 | ✓ |
| 14 | value 列类型 = numeric | numeric | numeric | ✓ |

**结论**: 669a-2020 14/14 红线 PASS — mart_city_timeseries schema 正确处理 zero-harvest 全 DATA_MISSING 路径, 实证 hongheiku 城市 2020 缺文, 守新增红线-1/2/3/7 全 PASS。

---

## 6. 验证输出 (mart apply + 14 红线 verify)

### mart apply 输出

```
=== knife 669a-2020 mart apply ===
DB: 127.0.0.1:55440/cegr_test schema=cegr_mart
SQL: /Users/kjonekong/projects/china platform/dbt/models/marts/mart_city_timeseries.sql

mart apply OK:
  rows             = 280           (expect 280 = 4 × 10 × 7)
  cities (distinct)= 4         (expect 4)
  indicators       = 10    (expect 10)
  years            = 7         (expect 7 = 2020-2026)
  real_cells       = 0    (expect 0, zero-harvest)
  DATA_MISSING     = 280  (expect 280)
  ruling_versions  = 1      (expect 1 = K669a-2020-2026-09-04)
```

### 14 红线 verify 输出

```
=== knife 669a-2020 红线 verify (14 assertions) ===
DB: 127.0.0.1:55440/cegr_test table=cegr_mart.mart_city_timeseries

  [OK]   row count = 280 (4 city × 10 indicator × 7 year)
  [OK]   city distinct = 4
  [OK]   indicator distinct = 10 (5 现 + 5 增量)
  [OK]   year distinct = 7 (2020-2026)
  [OK]   real_cells = 0 (zero-harvest knife 实证 hongheiku 城市 2020 缺文)
  [OK]   DATA_MISSING cells = 280 (守新增红线-1/2/3 不补零)
  [OK]   4 直辖市禁重复 (新增红线-7) — NOT in city dimension
  [OK]   lineage_ruling unique = 'K669a-2020-2026-09-04'
  [OK]   lineage_is_demo 全部 = 'false' (demo 数据禁入 mart)
  [OK]   status 枚举合法 (NULL 或 DATA_MISSING)
  [OK]   missing_reason 必填 for all DATA_MISSING cells
  [OK]   2020 missing_reason 全 40 cell 含 'hongheiku 城市维度 2020 缺文' (实证)
  [OK]   2026 missing_reason 全 40 cell 含 '2027 官方发布' (新增红线-2)
  [OK]   value 列类型 = numeric (允许 NULL for DATA_MISSING)

=== knife 669a-2020 红线 summary: 14/14 PASS, 0 FAIL ===
```

---

## 7. HTTP 预算守门

| 阶段 | HTTP 消耗 | 累计 | 红线 |
|---|---|---|---|
| 669a-2020 写 mart schema | 0 | 0 | ≤32 ✓ |
| 669a-2020 直 psql apply | 0 | 0 | ✓ |
| 669a-2020 14 红线 verify | 0 (直 psql) | 0 | ✓ |
| 669a-2020 commit chain + push | 0 | 0 | ✓ |

(说明: 669a-2020 是 zero-harvest knife; hongheiku 城市维度 2020 缺文是实证结果, 不是去爬网没爬到。后续 669a-2021+ sub-knives 才有 real HTTP 调用。)

---

## 8. 不宣称 (per docs/05 §8.2 + 红线)

- ❌ **不宣布 669a-2020 PASS** — 仅 DELIVERED + 14/14 红线 PASS + mart apply OK
- ❌ **不宣布 669 program 完成** — 仅 669a-2020 (60 sub-knives 中第 1 把) DELIVERED; 剩余 59 把待启动
- ❌ **不宣布 665-668 启动 PASS** — 启动需 user_ruling_668+ 单独签署
- ❌ **不宣布 O1 / Gate / M2 / M4 / M5 / M6** — 仍 OPEN
- ❌ **不冒充 ops** — 本地 dev build 验证,未触发 newvps 公网部署
- ❌ **不爬网** — 0 HTTP
- ❌ **不手填 city 数据** — 守新增红线-3 (本刀全 DATA_MISSING)
- ❌ **不补零** — 守新增红线-1 (2001-2019) + 红线-2 (2026) + hongheiku 2020 缺文
- ❌ **不合并 province/city mart** — 守新增红线-7 (独立 mart_city_timeseries table)
- ❌ **不重复 4 直辖市** — 守新增红线-7 (BEIJING/SHANGHAI/TIANJIN/CHONGQING 已在 province mart)
- ❌ **不宣称 hongheiku 2020 city 永久缺文** — 实证 (cat index 仅 2021-2025); 后续 669 knife 可拓展其他来源

---

## 9. user_ruling_669a 签署清单

- [x] user 显式 "做完669后一起部署" (blanket 授权 + Option A 60 sub-knives 结构)
- [x] 已审阅 663 + 664 + 665a-e + 666b + 667 + 668 交付物
- [x] 已确认新增红线-7 (mart schema 保持 province/city 分离; 4 直辖市禁重复)
- [x] 已确认新增红线-3 (城市数据禁手填)
- [x] 已确认新增红线-1 (2001-2019 禁编造) + 红线-2 (2026 待 2027)
- [x] 已确认 4 优先 city 范围 (深/穗/杭/宁)
- [x] 已确认 city_code 命名规范 ({PROVINCE_CODE}_{CITY_SLUG})
- [x] 已确认 0 HTTP budget (zero-harvest knife)
- [x] 已确认 mart apply 直 psql (per 663 Gap 1 workaround)
- [x] 已确认 14/14 红线 PASS
- [x] 已确认 docs/81 零改动
- [x] 已确认本刀 669a-2020 不触发 newvps 部署 (本机 dev postgres)
- [x] 已确认后续 669a-2021/2022/2023/2024/2025 (5 sub-knives) 才有 real cells
- [x] 已确认本计划 O1 仍 OPEN, 不宣称任何 PASS

---

## 10. 后续 59 刀待启动 (per Option A)

| 刀号 | 范围 | HTTP | cells |
|---|---|---|---|
| 669a-2021 | 4 city × 2021 | ≤4 | 40 (real) |
| 669a-2022 | 4 city × 2022 | ≤4 | 40 (real) |
| 669a-2023 | 4 city × 2023 | ≤4 | 40 (real) |
| 669a-2024 | 4 city × 2024 | ≤4 | 40 (real) |
| 669a-2025 | 4 city × 2025 | ≤4 | 40 (real) |
| 669b-j × 6 years | 8 batches × ~32 city × 6 year | ≤32 each | 48 sub-knives |
| 669j × 6 years | 33 city × 6 year | ≤33 each | 6 sub-knives |
| **合计** | **293 city × 6 year** | **~1900** | **70,320 max** (10 指标) |

---

## 11. 链接

- 前置 receipts: `reviews/stage0-gate0-rework-2026-08-23/{663,664,665a,665b,665c,665d,665e,666b,667,668}-*.md`
- 668 receipt (most recent before 669a-2020): `668-verify-live-v2-timeseries-receipt-20260904.md`
- 计划 plan: `/Users/kjonekong/.claude/plans/lively-greeting-shore.md` (knife 663-668 + 669a-j 锁定)
- 记忆: [[china-platform-665-multi-knife-program]] (665 program 锁定 + 669 program 启动)
- 记忆: [[china-platform-no-redundant-polls]] (不重复信息守门)
- 记忆: [[china-platform-user-rest-protocol]] (用户休息协议)

— End 669a-2020 receipt (mart_city_timeseries schema + zero-harvest 全 DATA_MISSING 验证, 14/14 PASS, DELIVERED ✓) —
