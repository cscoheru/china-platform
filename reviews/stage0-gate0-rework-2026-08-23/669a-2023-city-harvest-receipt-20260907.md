# 669a-2023 — 4 city × 2023 real-data harvest (37/40 cells, 守新增红线-3/7)

> **刀号**: 669a-2023 (knife 669 program fourth sub-knife, real-data harvest)
> **日期**: 2026-09-07
> **角色**: 架构师+执行端 merged (per 2026-08-31 21:50 豁免)
> **前置**: 669a-2020 + 669a-2021 + 669a-2022 DELIVERED (HEAD 38c6b41)
> **本件状态**: **DELIVERED ✓** — 4 city × 2023 harvest 完成, 37 real + 3 DATA_MISSING, 23/23 红线 PASS
> **关联**: `669a-2022-city-harvest-receipt-20260907.md` + `china-platform-665-multi-knife-program.md`

---

## 1. 范围 (granular)

| 维度 | 详情 |
|---|---|
| 目标 | 抓取 4 优先 city × 2023 年 10 指标真实数据, 写入 mart_city_timeseries |
| city scope | 4 优先 city (深圳市/广州市/杭州市/南京市) — 669a 批次 |
| year scope | 2023 only |
| 指标 | 10 (5 现 + 5 增量) |
| Cross product | 4 × 10 × 1 = **40 cells** |
| Real cells | **37** (深圳 9 + 广州 9 + 杭州 9 + 南京 10) — 与 2022 持平 |
| DATA_MISSING | 3 (全部 fixed_asset, 深/穗/杭 公报仅发增速 11.0%/3.6%/2.8%) |
| HTTP budget | **4** (4 city 2023 bulletins; URL discovery 0 HTTP 复用 669a-2021 tag 缓存), ≤32 红线 ✓ |
| 红线 | 新增红线-1/2/3/7 全 PASS; 不冒充 ops; docs/81 零改动 |
| mart apply | 直 psql via psycopg2 (per 663 Gap 1) |

---

## 2. URL discovery (Phase 1, 0 HTTP)

669a-2021 抓取的 4 个 tag 页缓存仍在 `/tmp/669a-2021/`, 直接 grep 提取 2023 URL:

```
深圳 /djs/49092.html
广州 /djs/47985.html
杭州 /djs/45617.html
南京 /djs/46614.html
```

**本刀 URL discovery 0 HTTP** — tag 页缓存复用合法 (同源同刀程序, 无新抓取)。

---

## 3. 2023 公报表述变体 (regex 2 处适配, 实证 probe 后首跑 37/40)

2023 公报 probe 阶段先行确认变体, parser 首跑即 37/40 (2022 刀是 30/40 修后 37/40):

### 变体 1: gdp_percapita 缩写 + 单字「达」(宁/穗/杭)

| 城市 | 2023 原文 |
|---|---|
| 南京 | 「**人均GDP达**183015元」(缩写「人均GDP」, 非「人均地区生产总值」) |
| 广州 | 「人均地区生产总值**达**161634元」(单字「达」, 2022 为「达到」) |
| 杭州 | 「人均地区生产总值**为**161129元」 |

修法: `(?:人均地区生产总值|人均GDP)(?:达到|达|为)?\s*(NUM)\s*元`
**守门说明**: 「人均GDP」与「人均地区生产总值」为同一人均国内生产总值口径, 采集自公报原文非手填 (不违反红线-3); lineage_origin 仍守 hongheiku URL。

### 变体 2: fixed_asset 完成前缀 (宁)

- 南京: 「**完成**固定资产投资5763.64亿元」
- 深圳/广州/杭州: 仅发增速 11.0% / 3.6% / 2.8% (无绝对值 → DATA_MISSING)

修法: `(?:完成|全社会)?固定资产投资...\s*(NUM)\s*亿元`; 增速-only 仍正确拒绝 (守红线-3 增速≠绝对值)

### probe 方法论教训 (记录)

ad-hoc probe 用 `.{20}` 上下文 regex 全部 FIRST-PATTERN MISS — 因 strip 时 `<tag>→\n` 注入换行而 `.` 不匹配 `\n`。改用 `re.sub(r'<[^>]+>','',text)` + `re.sub(r'\s+','',text)` 无换行归一化后 probe 全通。parser 本体的字面锚点 + `\s*` pattern 不受影响 (2021/2022 刀实证)。

---

## 4. 解析结果 (10 指标 by city, 2023)

| 城市 | gdp_total | gdp_growth | primary | secondary | tertiary | percapita | fiscal_rev | fixed_asset | retail | trade | **real** |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 深圳 | 34606.40 | 6.0 | 24.71 | 13015.32 | 21566.38 | 195230.17 | 4112.78 | — | 10486.19 | 38710.70 | **9/10** |
| 广州 | 30355.73 | 4.6 | 317.78 | 7775.71 | 22262.24 | 161634 | 1944.15 | — | 11012.62 | 10914.28 | **9/10** |
| 杭州 | 20059 | 5.6 | 347 | 5667 | 14045 | 161129 | 2617 | — | 7671 | 8030 | **9/10** |
| 南京 | 17421.40 | 4.6 | 317.75 | 5929.00 | 11174.65 | 183015 | 1620 | 5763.64 | 8201.07 | 5659.9 | **10/10** |
| **总计** | | | | | | | | | | | **37/40** |

南京 2023 = 10/10 全齐 (连续第二年: 2022 也是 10/10), percapita 走「人均GDP」缩写 + fixed_asset 走「完成」前缀。

---

## 5. 文件改动清单 (5 文件, 1 改 + 4 新)

| 路径 | 类型 | 用途 |
|---|---|---|
| `dbt/models/marts/mart_city_timeseries.sql` | M | (a) 加 real_data_2023 CTE (37 values); (b) 加 LEFT JOIN real_data_2023 rd3 (cp.year=2023); (c) value = COALESCE(rd, rd2, rd3); (d) status/missing_reason/lineage 三件套 CASE 加 2023 分支; (e) lineage_ruling 加 K669a-2023-2026-09-07 |
| `source_registry/seed_hongheiku_city_2023.csv` | A | 40 rows (37 real + 3 missing) |
| `scripts/parse_hongheiku_city_y2023.py` | A | 2023 表述变体适配 parser (人均GDP 缩写 + 完成前缀, probe 先行首跑 37/40) |
| `scripts/apply_mart_city_669a_2023.py` | A | 直 psql apply; 期望 280/4/10/7/100/180/5 |
| `scripts/verify_mart_city_669a_2023.py` | A | 23 红线 verify (新增 16/21/23 断言 + 18 修正) |

---

## 6. mart 状态 (4 刀累积后)

| 指标 | 值 |
|---|---|
| rows | 280 (4 × 10 × 7) |
| real_cells | **100** (26[2021] + 37[2022] + 37[2023]) |
| DATA_MISSING | 180 (40[2020] + 14[2021] + 3[2022] + 3[2023] + 120[2024-2026]) |
| lineage_ruling | **5 versions** (K669a-2020/2021/2022/2023 + pending) |

**multi-knife lineage 四件套**: 2020→K669a-2020 / 2021→K669a-2021 / 2022→K669a-2022 / 2023→K669a-2023 / 2024-2025→pending

---

## 7. 红线守门 (23/23 PASS)

| # | 红线 | 实际 | 状态 |
|---|---|---|---|
| 1 | mart 行数 = 280 | 280 | ✓ |
| 2 | city distinct = 4 | 4 | ✓ |
| 3 | indicator distinct = 10 | 10 | ✓ |
| 4 | year distinct = 7 | 7 | ✓ |
| 5 | real_cells = 100 (26+37+37) | 100 | ✓ |
| 6 | DATA_MISSING = 180 | 180 | ✓ |
| 7 | 4 直辖市禁重复 (红线-7) | 0 | ✓ |
| 8 | lineage_ruling = 5 versions | 5 | ✓ |
| 9 | lineage_is_demo 全 false | 0 bad | ✓ |
| 10 | status 枚举合法 | 0 bad | ✓ |
| 11 | missing_reason 必填 | 0 bad | ✓ |
| 12 | 2020 仍全 DATA_MISSING | 0 real | ✓ |
| 13 | 2026 仍全 DATA_MISSING (红线-2) | 0 real | ✓ |
| 14 | value 类型 numeric | numeric | ✓ |
| 15 | 2021 real 不回归 (26 + HONGHEIKU_TRANSLOAD) | 26/26 | ✓ |
| 16 | 2022 real 不回归 (37 + HONGHEIKU_TRANSLOAD) | 37/37 | ✓ |
| 17 | 2023 real lineage_source_type | 37/37 | ✓ |
| 18 | 2023 missing_reason 含 '669a-2023' | 3/3 | ✓ |
| 19 | 2023 lineage_origin 含 hongheiku/djs | 37/37 | ✓ |
| 20 | 2023 3 missing 全 = fixed_asset | 3/3 | ✓ |
| 21 | 2024-2025 仍全 DATA_MISSING | 0 real | ✓ |
| 22 | 南京 2023 = 10/10 | 10/10 | ✓ |
| 23 | 2021+2022 real 总量不变 = 63 | 63 | ✓ |

---

## 8. HTTP 预算守门

| 阶段 | HTTP 消耗 | 累计 (本刀) | 红线 |
|---|---|---|---|
| Phase 1: URL discovery (tag 缓存复用) | 0 | 0 | ✓ |
| Phase 2: 4 city 2023 bulletins | 4 | 4 | ✓ |
| Phase 3-6: parse/apply/verify (无 HTTP) | 0 | 4 | ✓ |
| **本刀总 HTTP** | **4** | **4/32** (28 余量) | ✓ |
| 669 程序累计 (2020+2021+2022+2023) | | 16 | ✓ |

---

## 9. 执行插值 (透明记录)

- apply 脚本首版漏 `if __name__ == "__main__"` 入口 → 跑了 verify 才暴露 (mart 未更新 18/23 FAIL)。补入口后 23/23 PASS。**教训**: 脚本「无输出退出 0」≠ 执行成功, apply 必须有 banner 输出确认。

---

## 10. 不宣称 (per docs/05 §8.2 + 红线)

- ❌ 不宣布 669a-2023 PASS — 仅 DELIVERED + 23/23 红线 PASS
- ❌ 不宣布 669a 批次完成 — 仅 4/6 sub-knives DELIVERED (2020/2021/2022/2023), 剩余 2024/2025
- ❌ 不宣布 669 program 完成 — 仅 4/60 sub-knives (批量部署 #934 触发条件未到)
- ❌ 不宣称 2023 harvest 完整 — 3 fixed_asset missing 是公报仅发增速实证, 非采集失败
- ❌ 不冒充 ops / 不爬网超预算 / 不手填 / 不补零 / 不合并 province-city mart
- ❌ O1 / Gate / M2 / M4 / M5 / M6 仍 OPEN

---

## 11. 后续 (per Option A)

| 刀号 | 范围 | 状态 |
|---|---|---|
| 669a-2024 | 4 city × 2024 | 待 "Start 669a-2024" |
| 669a-2025 | 4 city × 2025 | 待签署 |
| 669b-j | 54 sub-knives | 待签署 |
| 批量部署 668+669 | newvps 4-step granular | **669 全部完成后自动触发 (#934, user 2026-09-07 已授权)** |

---

## 12. 链接

- 前置 receipt: `669a-2022-city-harvest-receipt-20260907.md`
- 计划: `/Users/kjonekong/.claude/plans/lively-greeting-shore.md`
- 记忆: [[china-platform-665-multi-knife-program]]

— End 669a-2023 receipt (37/40 cells, 23/23 红线 PASS, DELIVERED ✓) —
