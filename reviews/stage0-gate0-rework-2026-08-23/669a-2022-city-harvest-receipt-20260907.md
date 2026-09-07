# 669a-2022 — 4 city × 2022 real-data harvest (37/40 cells, 守新增红线-3/7)

> **刀号**: 669a-2022 (knife 669 program third sub-knife, real-data harvest)
> **日期**: 2026-09-07
> **角色**: 架构师+执行端 merged (per 2026-08-31 21:50 豁免)
> **前置**: 669a-2020 + 669a-2021 DELIVERED (HEAD c526363)
> **本件状态**: **DELIVERED ✓** — 4 city × 2022 harvest 完成, 37 real + 3 DATA_MISSING, 22/22 红线 PASS
> **关联**: `669a-2021-city-harvest-receipt-20260904.md` + `china-platform-665-multi-knife-program.md`

---

## 1. 范围 (granular)

| 维度 | 详情 |
|---|---|
| 目标 | 抓取 4 优先 city × 2022 年 10 指标真实数据, 写入 mart_city_timeseries |
| city scope | 4 优先 city (深圳市/广州市/杭州市/南京市) — 669a 批次 |
| year scope | 2022 only |
| 指标 | 10 (5 现 + 5 增量) |
| Cross product | 4 × 10 × 1 = **40 cells** |
| Real cells | **37** (深圳 9 + 广州 9 + 杭州 9 + 南京 10) — 669 程序最佳年份 (2021 = 26/40) |
| DATA_MISSING | 3 (全部 fixed_asset, 深/穗/杭 公报仅发增速无绝对值) |
| HTTP budget | **4** (4 city 2022 bulletins; URL discovery 0 HTTP 复用 669a-2021 tag 缓存), ≤32 红线 ✓ |
| 红线 | 新增红线-1/2/3/7 全 PASS; 不冒充 ops; docs/81 零改动 |
| mart apply | 直 psql via psycopg2 (per 663 Gap 1) |

---

## 2. URL discovery (Phase 1, 0 HTTP)

669a-2021 抓取的 4 个 tag 页缓存仍在 `/tmp/669a-2021/`, 直接 grep 提取 2022 URL:

```
深圳 /djs/38197.html
广州 /djs/38118.html
杭州 /djs/37237.html
南京 /djs/38005.html
```

**本刀 URL discovery 0 HTTP** — tag 页缓存复用合法 (同源同刀程序, 无新抓取)。

---

## 3. 2022 公报表述变体 (regex 3 处适配, 实证)

2022 公报结构与 2021 有 3 处显著差异, 首轮解析 30/40, 修 regex 后 37/40:

### 变体 1: gdp_total 前缀 (2021 regex 全 miss, 0/4)

| 城市 | 2022 原文 |
|---|---|
| 深圳 | 「2022年**深圳**地区生产总值32387.68亿元」(城名前缀, 非实现/完成/地区) |
| 广州 | 「实现地区生产总值**（初步核算数）**28839.00亿元」(括号注插入) |
| 杭州 | 「实现地区生产总值**[2]**18753亿元」(脚注标记) |
| 南京 | 「实现地区生产总值**[2] **16907.85亿元」(脚注+空格) |

修法: `地区生产总值(?:（[^）]{0,20}）|\[\d+\])?\s*(NUM)\s*亿元`

### 变体 2: gdp_percapita 修饰词 (穗/杭 miss)

- 广州: 「人均地区生产总值**达到**153625元」
- 杭州: 「人均地区生产总值**为**152588元」

修法: `人均地区生产总值(?:达到|为)?\s*(NUM)\s*元`

### 变体 3: trade 口径表述 (穗 miss)

- 广州: 「**商品进出口总值**10948.40亿元」(2021 及深/杭/宁用 进出口总额/货物进出口总额)

修法: `(?:货物|商品)?进出口(?:总额|总值)\s*(NUM)\s*亿元`
**守门说明**: 商品进出口总值与进出口总额为同一商品/货物贸易口径, 采集自公报原文非手填 (不违反红线-3); lineage_origin 仍守 hongheiku URL。

---

## 4. 解析结果 (10 指标 by city, 2022)

| 城市 | gdp_total | gdp_growth | primary | secondary | tertiary | percapita | fiscal_rev | fixed_asset | retail | trade | **real** |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 深圳 | 32387.68 | 3.3 | 25.64 | 12405.88 | 19956.16 | 183274 | 4012.27 | — | 9708.28 | 36737.52 | **9/10** |
| 广州 | 28839.00 | 1.0 | 318.31 | 7909.29 | 20611.40 | 153625 | 1854.73 | — | 10298.15 | 10948.40 | **9/10** |
| 杭州 | 18753 | 1.5 | 346 | 5620 | 12787 | 152588 | 2451 | — | 7294 | 7565 | **9/10** |
| 南京 | 16907.85 | 2.1 | 315.56 | 6069.64 | 10522.65 | 178781 | 1558.2 | 5874.92 | 7832.41 | 6292.13 | **10/10** |
| **总计** | | | | | | | | | | | **37/40** |

### 3 missing cells 守新增红线-3 (禁手填/禁换算)

全部 = fixed_asset: 深圳/广州/杭州 2022 公报仅发增速 (8.4% / -2.1% / 6.0%), **无绝对值**。
parser 正确拒绝增速-only fallback (增速≠绝对值, 禁换算), 走 DATA_MISSING。
南京 2022 = 10/10 全齐 (含 fixed_asset 5874.92), 为 669 程序首个满格 city-year。

---

## 5. 文件改动清单 (5 文件, 1 改 + 4 新)

| 路径 | 类型 | 用途 |
|---|---|---|
| `dbt/models/marts/mart_city_timeseries.sql` | M | (a) 加 real_data_2022 CTE (37 values); (b) 加 LEFT JOIN real_data_2022 rd2 (cp.year=2022); (c) value = COALESCE(rd, rd2); (d) status/missing_reason/lineage 三件套 CASE 加 2022 分支; (e) lineage_ruling 加 K669a-2022-2026-09-07 |
| `source_registry/seed_hongheiku_city_2022.csv` | A | 40 rows (37 real + 3 missing) |
| `scripts/parse_hongheiku_city_y2022.py` | A | 2022 表述变体适配 parser (3 处 regex 实证修正) |
| `scripts/apply_mart_city_669a_2022.py` | A | 直 psql apply; 期望 280/4/10/7/63/217/4 |
| `scripts/verify_mart_city_669a_2022.py` | A | 22 红线 verify (新增 15/19/20/22 断言) |

---

## 6. mart SQL 设计要点 (多刀累积模式确立)

```sql
-- 双年 LEFT JOIN + COALESCE 累积 (每新增一年加一个 join + CASE 分支)
FROM cross_product cp
LEFT JOIN real_data_2021 rd
    ON cp.city_code = rd.city_code
    AND cp.indicator_key = rd.indicator_key
    AND cp.year = 2021
LEFT JOIN real_data_2022 rd2
    ON cp.city_code = rd2.city_code
    AND cp.indicator_key = rd2.indicator_key
    AND cp.year = 2022

-- value 列: COALESCE(rd.value, rd2.value) AS value
-- (注意: 必须 COALESCE 作为 value 列本身, 不能另开 value_final 列)
```

**multi-knife lineage 四件套**: 2020→K669a-2020 / 2021→K669a-2021 / 2022→K669a-2022 / 2023-2025→pending

---

## 7. 红线守门 (22/22 PASS)

| # | 红线 | 实际 | 状态 |
|---|---|---|---|
| 1 | mart 行数 = 280 | 280 | ✓ |
| 2 | city distinct = 4 | 4 | ✓ |
| 3 | indicator distinct = 10 | 10 | ✓ |
| 4 | year distinct = 7 | 7 | ✓ |
| 5 | real_cells = 63 (26+37) | 63 | ✓ |
| 6 | DATA_MISSING = 217 | 217 | ✓ |
| 7 | 4 直辖市禁重复 (红线-7) | 0 | ✓ |
| 8 | lineage_ruling = 4 versions | 4 | ✓ |
| 9 | lineage_is_demo 全 false | 0 bad | ✓ |
| 10 | status 枚举合法 | 0 bad | ✓ |
| 11 | missing_reason 必填 | 0 bad | ✓ |
| 12 | 2020 仍全 DATA_MISSING | 0 real | ✓ |
| 13 | 2026 仍全 DATA_MISSING (红线-2) | 0 real | ✓ |
| 14 | value 类型 numeric | numeric | ✓ |
| 15 | 2021 real 不回归 (26 + HONGHEIKU_TRANSLOAD) | 26/26 | ✓ |
| 16 | 2022 real lineage_source_type | 37/37 | ✓ |
| 17 | 2022 missing_reason 含 '669a-2022' | 3/3 | ✓ |
| 18 | 2022 lineage_origin 含 hongheiku/djs | 37/37 | ✓ |
| 19 | 2022 3 missing 全 = fixed_asset | 3/3 | ✓ |
| 20 | 2021 26 real 数量不变 | 26 | ✓ |
| 21 | 2023-2025 仍全 DATA_MISSING | 0 real | ✓ |
| 22 | 南京 2022 = 10/10 | 10/10 | ✓ |

---

## 8. HTTP 预算守门

| 阶段 | HTTP 消耗 | 累计 (本刀) | 红线 |
|---|---|---|---|
| Phase 1: URL discovery (tag 缓存复用) | 0 | 0 | ✓ |
| Phase 2: 4 city 2022 bulletins | 4 | 4 | ✓ |
| Phase 3-6: parse/apply/verify (无 HTTP) | 0 | 4 | ✓ |
| **本刀总 HTTP** | **4** | **4/32** (28 余量) | ✓ |
| 669 程序累计 (2020+2021+2022) | | 12 | ✓ |

---

## 9. 不宣称 (per docs/05 §8.2 + 红线)

- ❌ 不宣布 669a-2022 PASS — 仅 DELIVERED + 22/22 红线 PASS
- ❌ 不宣布 669a 批次完成 — 仅 3/6 sub-knives DELIVERED (2020/2021/2022), 剩余 2023/2024/2025
- ❌ 不宣布 669 program 完成 — 仅 3/60 sub-knives
- ❌ 不宣称 2022 harvest 完整 — 3 fixed_asset missing 是公报仅发增速实证, 非采集失败
- ❌ 不冒充 ops / 不爬网超预算 / 不手填 / 不补零 / 不合并 province-city mart
- ❌ O1 / Gate / M2 / M4 / M5 / M6 仍 OPEN

---

## 10. 后续 (per Option A)

| 刀号 | 范围 | 状态 |
|---|---|---|
| 669a-2023 | 4 city × 2023 | 待 "Start 669a-2023" |
| 669a-2024 | 4 city × 2024 | 待签署 |
| 669a-2025 | 4 city × 2025 | 待签署 |
| 669b-j | 54 sub-knives | 待签署 |
| 批量部署 668+669 | newvps 4-step granular | user "做完669后一起部署" 已锁, 669 program 完成后触发 (#934) |

---

## 11. 链接

- 前置 receipt: `669a-2021-city-harvest-receipt-20260904.md`
- 计划: `/Users/kjonekong/.claude/plans/lively-greeting-shore.md`
- 记忆: [[china-platform-665-multi-knife-program]]

— End 669a-2022 receipt (37/40 cells, 22/22 红线 PASS, DELIVERED ✓) —
