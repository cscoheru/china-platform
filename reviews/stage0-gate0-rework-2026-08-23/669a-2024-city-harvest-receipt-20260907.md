# 669a-2024 — 4 city × 2024 real-data harvest (36/40 cells, 守新增红线-3/7)

> **刀号**: 669a-2024 (knife 669 program fifth sub-knife, real-data harvest)
> **日期**: 2026-09-07
> **角色**: 架构师+执行端 merged (per 2026-08-31 21:50 豁免)
> **前置**: 669a-2020 + 669a-2021 + 669a-2022 + 669a-2023 DELIVERED (HEAD e8afdd9)
> **本件状态**: **DELIVERED ✓** — 4 city × 2024 harvest 完成, 36 real + 4 DATA_MISSING, 24/24 红线 PASS
> **关联**: `669a-2023-city-harvest-receipt-20260907.md` + `china-platform-665-multi-knife-program.md`

---

## 1. 范围 (granular)

| 维度 | 详情 |
|---|---|
| 目标 | 抓取 4 优先 city × 2024 年 10 指标真实数据, 写入 mart_city_timeseries |
| city scope | 4 优先 city (深圳市/广州市/杭州市/南京市) — 669a 批次 |
| year scope | 2024 only |
| 指标 | 10 (5 现 + 5 增量) |
| Cross product | 4 × 10 × 1 = **40 cells** |
| Real cells | **36** (深圳 9 + 广州 9 + 杭州 9 + 南京 9) — 各城均掉 1 (深/穗/杭 fixed_asset, 宁 retail) |
| DATA_MISSING | 4 (3× fixed_asset 深/穗/杭 + 1× retail 南京, 全部公报仅发增速实证) |
| HTTP budget | **4** (4 city 2024 bulletins; URL discovery 0 HTTP 复用 669a-2021 tag 缓存), ≤32 红线 ✓ |
| 红线 | 新增红线-1/2/3/7 全 PASS; 不冒充 ops; docs/81 零改动 |
| mart apply | 直 psql via psycopg2 (per 663 Gap 1) |

---

## 2. URL discovery (Phase 1, 0 HTTP)

669a-2021 抓取的 4 个 tag 页缓存仍在 `/tmp/669a-2021/`, 直接 grep 提取 2024 URL — **第 4 个连续 sub-knife 零 HTTP URL discovery**:

```
深圳 /djs/62867.html
广州 /djs/58648.html
杭州 /djs/57316.html
南京 /djs/57850.html
```

---

## 3. 2024 公报表述变体 (regex 2 处适配, 首跑 34/40 修后 36/40)

### 变体 1: gdp_total 脚注 [2] **前有换行** (南京)

hongheiku 2024 南京公报 strip 后为:

```
地区生产总值⏎[2]⏎18500.81亿元
```

2022 版为同行空格「生产总值[2] 16907.85」; 2023 版无脚注。旧 regex `地区生产总值(?:（...）|\[\d+\])?\s*(NUM)` 在「生产总值」后遇 `\n`, 可选脚注组在 `[` 前失败, `\s*` 吃掉换行后撞 `[` 非数字 → 整体 MISS。

修法: **脚注组前加 `\s*`** → `地区生产总值\s*(?:（[^）]{0,20}）|\[\d+\])?\s*(NUM)\s*亿元`

### 变体 2: retail 脚注 [4] (杭州)

- 杭州: 「社会消费品零售总额**[4]**9151亿元」 → retail regex 同加脚注/括号容错

### 4 处 legit DATA_MISSING (公报仅发增速, 守红线-3 不手填)

| city | 指标 | 公报原文 | 处置 |
|---|---|---|---|
| 深圳 | fixed_asset | 增长 2.4% (无绝对值) | DATA_MISSING |
| 广州 | fixed_asset | 增长 0.2% (无绝对值) | DATA_MISSING |
| 杭州 | fixed_asset | 下降 2.9% (无绝对值) | DATA_MISSING |
| 南京 | retail | 增长 4.3% (无绝对值) | DATA_MISSING |

---

## 4. 解析结果 (10 指标 by city, 2024)

| 城市 | gdp_total | gdp_growth | primary | secondary | tertiary | percapita | fiscal_rev | fixed_asset | retail | trade | **real** |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 深圳 | 36801.87 | 5.8 | 26.37 | 13909.28 | 22866.22 | 205714 | 3914.18 | — | 10637.70 | 45048.24 | **9/10** |
| 广州 | 31032.50 | 2.1 | 334.47 | 7839.45 | 22858.58 | 164171 | 1954.74 | — | 11055.77 | 11238.38 | **9/10** |
| 杭州 | 21860 | 4.7 | 369 | 5529 | 15962 | 173867 | 2640 | — | 9151¹ | 8549 | **9/10** |
| 南京 | 18500.81² | 4.5 | 331.00 | 5831.06 | 12338.75 | 193483 | 1596.02 | 4777.29 | — | 5459.2 | **9/10** |
| **总计** | | | | | | | | | | | **36/40** |

¹ 杭州零售脚注 [4] 容错采集; ² 南京 GDP 脚注 [2] 换行容错采集 (本刀 2 处 regex 修复落地点, verify #24 断言锁定)。

南京 2024 断 10/10 连胜 (2022/2023 均 10/10, 2024 retail 公报仅发增速)。

---

## 5. 文件改动清单 (5 文件, 1 改 + 4 新)

| 路径 | 类型 | 用途 |
|---|---|---|
| `dbt/models/marts/mart_city_timeseries.sql` | M | (a) 加 real_data_2024 CTE (36 values); (b) 加 LEFT JOIN real_data_2024 rd4 (cp.year=2024); (c) value = COALESCE(rd, rd2, rd3, rd4); (d) status/missing_reason/lineage 三件套 CASE 加 2024 分支; (e) lineage_ruling 加 K669a-2024-2026-09-07 |
| `source_registry/seed_hongheiku_city_2024.csv` | A | 40 rows (36 real + 4 missing) |
| `scripts/parse_hongheiku_city_y2024.py` | A | 2024 表述变体适配 parser (脚注换行容错 ×2, 首跑 34/40 修后 36/40) |
| `scripts/apply_mart_city_669a_2024.py` | A | 直 psql apply; 期望 280/4/10/7/136/144/6 (含 `__main__` 入口守门, per 2023 §9 教训) |
| `scripts/verify_mart_city_669a_2024.py` | A | 24 红线 verify (vs 2023 23 条: 加 2023 不回归 #17 + 2024 missing 分解 #21 + regex 修复落地 #24) |

---

## 6. mart 状态 (5 刀累积后)

| 指标 | 值 |
|---|---|
| rows | 280 (4 × 10 × 7) |
| real_cells | **136** (26[2021] + 37[2022] + 37[2023] + 36[2024]) |
| DATA_MISSING | 144 (40[2020] + 14[2021] + 3[2022] + 3[2023] + 4[2024] + 80[2025-2026]) |
| lineage_ruling | **6 versions** (K669a-2020/2021/2022/2023/2024 + pending) |

**multi-knife lineage 四件套**: 2020→K669a-2020 / 2021→K669a-2021 / 2022→K669a-2022 / 2023→K669a-2023 / 2024→K669a-2024 / 2025-2026→pending

---

## 7. 红线守门 (24/24 PASS)

| # | 红线 | 实际 | 状态 |
|---|---|---|---|
| 1 | mart 行数 = 280 | 280 | ✓ |
| 2 | city distinct = 4 | 4 | ✓ |
| 3 | indicator distinct = 10 | 10 | ✓ |
| 4 | year distinct = 7 | 7 | ✓ |
| 5 | real_cells = 136 (26+37+37+36) | 136 | ✓ |
| 6 | DATA_MISSING = 144 | 144 | ✓ |
| 7 | 4 直辖市禁重复 (红线-7) | 0 | ✓ |
| 8 | lineage_ruling = 6 versions | 6 | ✓ |
| 9 | lineage_is_demo 全 false | 0 bad | ✓ |
| 10 | status 枚举合法 | 0 bad | ✓ |
| 11 | missing_reason 必填 | 0 bad | ✓ |
| 12 | 2020 仍全 DATA_MISSING | 0 real | ✓ |
| 13 | 2026 仍全 DATA_MISSING (红线-2) | 0 real | ✓ |
| 14 | value 类型 numeric | numeric | ✓ |
| 15 | 2021 real 不回归 (26) | 26/26 | ✓ |
| 16 | 2022 real 不回归 (37) | 37/37 | ✓ |
| 17 | 2023 real 不回归 (37) | 37/37 | ✓ |
| 18 | 2024 real lineage_source_type | 36/36 | ✓ |
| 19 | 2024 missing_reason 含 '669a-2024' | 4/4 | ✓ |
| 20 | 2024 lineage_origin 含 hongheiku/djs | 36/36 | ✓ |
| 21 | 2024 4 missing = 3× fixed_asset + 1× 南京 retail | 4/4 | ✓ |
| 22 | 2025 仍全 DATA_MISSING | 0 real | ✓ |
| 23 | 2021+2022+2023 real 总量不变 = 100 | 100 | ✓ |
| 24 | 南京 fixed_asset 4777.29 + 杭州 retail 9151 (regex 修复落地) | 双双采到 | ✓ |

---

## 8. HTTP 预算守门

| 阶段 | HTTP 消耗 | 累计 (本刀) | 红线 |
|---|---|---|---|
| Phase 1: URL discovery (tag 缓存复用) | 0 | 0 | ✓ |
| Phase 2: 4 city 2024 bulletins | 4 | 4 | ✓ |
| Phase 3-6: parse/apply/verify (无 HTTP) | 0 | 4 | ✓ |
| **本刀总 HTTP** | **4** | **4/32** (28 余量) | ✓ |
| 669 程序累计 (2020+2021+2022+2023+2024) | | 20 | ✓ |

---

## 9. 执行插值 (透明记录)

1. **sed 模板漏替换**: 从 2023 parser sed 派生 2024 版, `s/669a-2023/669a-2024/g` 等三组替换未覆盖 docstring 裸 "2023" 与输出文件名 `seed_hongheiku_city_2023.csv` → 首跑写出错文件名。补 Python patch pass (docstring + out_csv 全替换) + rm 残留。**教训**: sed 派生必须 grep 验证零残留旧年份字符串。
2. **verify #24 TypeError**: psycopg2 对 numeric 列返回 `decimal.Decimal`, 与 float 字面量直接相减抛 TypeError (非数据问题)。统一 `float(...)` 转换后 24/24。**教训**: psycopg2 + numeric 比较必须显式转 float。
3. **SyntaxWarning**: docstring 含 `\s` 非法转义 (patch 时引入), 已改纯文本 + `python3 -W error::SyntaxWarning` ast.parse 验证干净。

---

## 10. 不宣称 (per docs/05 §8.2 + 红线)

- ❌ 不宣布 669a-2024 PASS — 仅 DELIVERED + 24/24 红线 PASS
- ❌ 不宣布 669a 批次完成 — 仅 5/6 sub-knives DELIVERED (2020/2021/2022/2023/2024), 剩余 2025
- ❌ 不宣布 669 program 完成 — 仅 5/60 sub-knives (批量部署 #934 触发条件未到)
- ❌ 不宣称 2024 harvest 完整 — 4 missing 是公报仅发增速实证, 非采集失败
- ❌ 不冒充 ops / 不爬网超预算 / 不手填 / 不补零 / 不合并 province-city mart
- ❌ O1 / Gate / M2 / M4 / M5 / M6 仍 OPEN

---

## 11. 后续 (per Option A)

| 刀号 | 范围 | 状态 |
|---|---|---|
| 669a-2025 | 4 city × 2025 | 待 "Start 669a-2025" (669a 批次收官刀) |
| 669b-i | 48 sub-knives | 待签署 (#937) |
| 669j | 6 sub-knives | 待签署 (#938) |
| 批量部署 668+669 | newvps 4-step granular | **669 全部完成后自动触发 (#934, user 2026-09-07 已授权)** |

---

## 12. 链接

- 前置 receipt: `669a-2023-city-harvest-receipt-20260907.md`
- 计划: `/Users/kjonekong/.claude/plans/lively-greeting-shore.md`
- 记忆: [[china-platform-665-multi-knife-program]]

— End 669a-2024 receipt (36/40 cells, 24/24 红线 PASS, DELIVERED ✓) —
