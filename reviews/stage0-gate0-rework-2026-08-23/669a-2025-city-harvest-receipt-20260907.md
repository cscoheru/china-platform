# 669a-2025 — 4 city × 2025 real-data harvest (18/40 cells, 守新增红线-3)

> **刀号**: 669a-2025 (knife 669a 第六子刀, 收官 4 优先 city × 2025; 669a 批次 6/6 全部 DELIVERED)
> **日期**: 2026-09-07
> **角色**: 架构师+执行端 merged (per 2026-08-31 21:50 豁免)
> **前置**: 669a-2020 + 2021 + 2022 + 2023 + 2024 全部 DELIVERED (HEAD 642e64a)
> **本件状态**: **DELIVERED ✓** — 4 city × 2025 harvest 完成, 18 real + 22 DATA_MISSING, 26/26 红线 PASS
> **关联**: `669a-2024-city-harvest-receipt-20260907.md` + `china-platform-665-multi-knife-program.md`

---

## 1. 范围 (granular)

| 维度 | 详情 |
|---|---|
| 目标 | 抓取 4 优先 city × 2025 年 10 指标真实数据, 写入 mart_city_timeseries |
| city scope | 4 优先 city (深圳市/广州市/杭州市/南京市) — 669a 批次 |
| year scope | 2025 only |
| 指标 | 10 (5 现 + 5 增量) |
| Cross product | 4 × 10 × 1 = **40 cells** |
| Real cells | **18** (穗 9 + 杭 9; 深 0 + 宁 0) |
| DATA_MISSING | **22** (20× SZ+NJ 全 hongheiku 无 2025 entry + 2× fixed_asset 穗-6.7%/杭占比) |
| HTTP budget | **7** (URL discovery 5 + 2 bulletins; 详 §2), ≤32 红线 ✓ |
| 红线 | 新增红线-1/2/3/7 全 PASS; 不冒充 ops; docs/81 零改动 |
| mart apply | 直 psql via psycopg2 (per 663 Gap 1) |

---

## 2. URL discovery (Phase 1, 5 HTTP)

### Tag 缓存复用 (0 HTTP)

669a-2021 抓取的 4 个 tag 页缓存仍在 `/tmp/669a-2021/`, 但 grep 仅返 2021-2024 URLs — **2025 entry tag 缺失,需主动 probe**:

```
深圳 tag 页: 4 URLs (2021/2022/2023/2024) — 无 2025
广州 tag 页: 5 URLs (2021/2022/2023/2024/2025) — 含 69954 (2026-05-12 发布)
杭州 tag 页: 5 URLs (2021/2022/2023/2024/2025) — 含 69708 (2026-04-30 发布)
南京 tag 页: 4 URLs (2021/2022/2023/2024) — 无 2025
```

### 主动 probe 验证 SZ/NJ 无 2025 entry (5 HTTP)

确认 SZ/NJ tag 页缓存**当天仍只列 2021-2024**, 走 4 条 fallback 路径实证 hongheiku 2025 收录 gap:

| Probe | 目标 | 实证结果 |
|---|---|---|
| 1. SZ tag re-fetch | `https://tjgb.hongheiku.com/tag/深圳市` | 4 URLs only (无 2025) |
| 2. NJ tag re-fetch | `https://tjgb.hongheiku.com/tag/南京市` | 4 URLs only (无 2025) |
| 3. cat index | `https://tjgb.hongheiku.com/category/sjtjgb` | 108278 bytes, "2025" 出现 120 次, **深圳/南京 = 0 命中** (仅省 level) |
| 4. 站内搜索 SZ | `https://tjgb.hongheiku.com/?s=2025年深圳` | "search returned empty result" |
| 5. 站内搜索 NJ | `https://tjgb.hongheiku.com/?s=2025年南京` | "search returned empty result" |

**结论**: 实证 SZ/NJ hongheiku 2025 entry **不存在**, 守红线-3 不手填, 全部 DATA_MISSING。

---

## 3. Bulletin fetch (Phase 2, 2 HTTP)

| City | URL | Size | 发布日 | 验证 2025 |
|---|---|---|---|---|
| 广州 | `/djs/69954.html` | 57794 bytes | 2026-05-12 | ✓ GDP「(初步核算数)」32039.46亿元 |
| 杭州 | `/djs/69708.html` | 47144 bytes | 2026-04-30 | ✓ GDP 脚注 [2] 23011亿元 |

---

## 4. 2025 公报表述变体 (复用 2024 regex, 2 处校验)

### 变体 1: gdp_total 括号注「(初步核算数)」 (广州)

2025 公报格式: `地区生产总值(初步核算数)32039.46亿元`
沿用 2024 regex `地区生产总值\s*(?:（[^）]{0,20}）|\[\d+\])?\s*([\d,]+(?:\.\d+)?)\s*亿元` — 括号组加 `\s*` 容错已覆盖。

### 变体 2: gdp_total 脚注 [2] 前换行 (杭州)

2025 公报格式: `地区生产总值\n[2]\n23011亿元`
沿用 2024 加 `\s*` 容错 (前刀 fix #1), 直接采到。

### 4 cells DATA_MISSING (公报仅发增速/占比, 守红线-3)

| city | 指标 | 公报原文 | 处置 |
|---|---|---|---|
| 广州 | fixed_asset | 增长 -6.7% (无绝对值) | DATA_MISSING |
| 杭州 | fixed_asset | 「占比 32.5%」(无绝对值) | DATA_MISSING |
| 深圳 | 全部 10 | 公报未发布/未收录 | DATA_MISSING × 10 |
| 南京 | 全部 10 | 公报未发布/未收录 | DATA_MISSING × 10 |

---

## 5. 解析结果 (10 指标 by city, 2025)

| 城市 | gdp_total | gdp_growth | primary | secondary | tertiary | percapita | fiscal_rev | fixed_asset | retail | trade | **real** |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 深圳 | — | — | — | — | — | — | — | — | — | — | **0/10** |
| 广州 | 32039.46¹ | 4.0 | 317.02 | 7710.27 | 24012.17 | 168279 | 2184.82 | — | 11032.38 | 12407.24 | **9/10** |
| 杭州 | 23011² | 5.2 | 383 | 5631 | 16997 | 181732 | 2693 | — | 9499 | 9072 | **9/10** |
| 南京 | — | — | — | — | — | — | — | — | — | — | **0/10** |
| **总计** | | | | | | | | | | | **18/40** |

¹ 广州括号注「(初步核算数)」容错采到; ² 杭州脚注 [2] 换行容错采到。

---

## 6. 文件改动清单 (4 文件, 1 改 + 3 新)

| 路径 | 类型 | 用途 |
|---|---|---|
| `dbt/models/marts/mart_city_timeseries.sql` | M | (a) header "knife 669a-2020/2021/2022/2023/2024/2025"; (b) 加 real_data_2025 CTE (18 values); (c) 加 LEFT JOIN real_data_2025 rd5 (cp.year=2025); (d) value = COALESCE(rd, rd2, rd3, rd4, rd5) (5-way); (e) status/missing_reason/lineage_source_type/lineage_origin/lineage_ruling CASE 加 2025 分支; (f) lineage_ruling 加 K669a-2025-2026-09-07 第六 ruling |
| `source_registry/seed_hongheiku_city_2025.csv` | A | 40 rows (18 real + 22 missing; SZ/NJ 20 cells 标 DATA_MISSING + hongheiku origin 缺失注释) |
| `scripts/parse_hongheiku_city_y2025.py` | A | 2025 表述变体适配 parser (fresh write, 非 sed-template, 因 SZ/NJ files intentionally missing, parser 检查 `html_path.exists()` 优雅分支) |
| `scripts/apply_mart_city_669a_2025.py` | A | 直 psql apply; 期望 280/4/10/7/154/126/7 (含 `__main__` 入口守门, per 2023 §9 教训; **Python transform 派生 from 2024, print text 已编辑对齐本刀 154/126/7**) |
| `scripts/verify_mart_city_669a_2025.py` | A | 26 红线 verify (vs 2024 24 条: 加 2025 real 不回归 #19 + 2025 missing 分解 #21 + SZ+NJ hongheiku absence 守红线-3 #22 + 2025 missing_reason 含 '669a-2025' #24 + 2025 ruling 唯一 #25 + 2026 守红线-2 #26) |

---

## 7. mart 状态 (6 刀累积后, 669a 收官)

| 指标 | 值 |
|---|---|
| rows | 280 (4 × 10 × 7) |
| real_cells | **154** (26[2021] + 37[2022] + 37[2023] + 36[2024] + 18[2025]) |
| DATA_MISSING | 126 (40[2020] + 14[2021] + 3[2022] + 3[2023] + 4[2024] + 22[2025] + 40[2026]) |
| lineage_ruling | **7 versions** (K669a-2020/2021/2022/2023/2024/2025 + pending) |

**multi-knife lineage 六件套**: 2020→K669a-2020 / 2021→K669a-2021 / 2022→K669a-2022 / 2023→K669a-2023 / 2024→K669a-2024 / **2025→K669a-2025** / 2026→pending

**669a 收官统计**: 6/6 sub-knives DELIVERED, 4 city × 6 year × 10 指标 = 240 cells (累计 154 real + 86 missing); 7 lineage ruling versions。

---

## 8. 红线守门 (26/26 PASS)

| # | 红线 | 实际 | 状态 |
|---|---|---|---|
| 1 | mart 行数 = 280 | 280 | ✓ |
| 2 | city distinct = 4 | 4 | ✓ |
| 3 | indicator distinct = 10 | 10 | ✓ |
| 4 | year distinct = 7 | 7 | ✓ |
| 5 | real_cells = 154 (26+37+37+36+18) | 154 | ✓ |
| 6 | DATA_MISSING = 126 | 126 | ✓ |
| 7 | 4 直辖市禁重复 (红线-7) | 0 | ✓ |
| 8 | lineage_ruling = 7 versions | 7 | ✓ |
| 9 | lineage_is_demo 全 false | 0 bad | ✓ |
| 10 | status 枚举合法 | 0 bad | ✓ |
| 11 | missing_reason 必填 | 0 bad | ✓ |
| 12 | 2020 仍全 DATA_MISSING | 0 real | ✓ |
| 13 | 2026 仍全 DATA_MISSING (红线-2) | 0 real | ✓ |
| 14 | value 类型 numeric | numeric | ✓ |
| 15 | 2021 real 不回归 (26) | 26/26 | ✓ |
| 16 | 2022 real 不回归 (37) | 37/37 | ✓ |
| 17 | 2023 real 不回归 (37) | 37/37 | ✓ |
| 18 | 2024 real 不回归 (36) | 36/36 | ✓ |
| 19 | 2025 real lineage_source_type | 18/18 | ✓ |
| 20 | 2025 lineage_origin 含 hongheiku/djs | 18/18 | ✓ |
| 21 | 2025 22 missing = 20× SZ/NJ + 2× fixed_asset | 22/22 | ✓ |
| 22 | 2025 real by city = 仅穗/杭 各 9 | 2 cities | ✓ |
| 23 | 2021-2024 real 总量不变 = 136 | 136 | ✓ |
| 24 | 2025 missing_reason 含 '669a-2025' | 22/22 | ✓ |
| 25 | K669a-2025-2026-09-07 ruling 唯一 | 1 | ✓ |
| 26 | 2026 仍全 DATA_MISSING (红线-2) | 0 real | ✓ |

---

## 9. HTTP 预算守门

| 阶段 | HTTP 消耗 | 累计 (本刀) | 红线 |
|---|---|---|---|
| Phase 1.1: URL discovery tag 缓存复用 | 0 | 0 | ✓ |
| Phase 1.2: SZ tag re-fetch | 1 | 1 | ✓ |
| Phase 1.3: NJ tag re-fetch | 1 | 2 | ✓ |
| Phase 1.4: cat index probe | 1 | 3 | ✓ |
| Phase 1.5: 站内搜索 SZ | 1 | 4 | ✓ |
| Phase 1.6: 站内搜索 NJ | 1 | 5 | ✓ |
| Phase 2: 2 city 2025 bulletins (穗+杭) | 2 | 7 | ✓ |
| Phase 3-6: parse/apply/verify (无 HTTP) | 0 | 7 | ✓ |
| **本刀总 HTTP** | **7** | **7/32** (25 余量) | ✓ |
| 669 程序累计 (2020+2021+2022+2023+2024+2025) | | **27** | ✓ |

---

## 10. 执行插值 (透明记录)

1. **SZ/NJ hongheiku 2025 entry 缺失**: 5 HTTP probes 实证 (tag re-fetch + cat index + 2 site searches), 决定 harvest 仅穗/杭。**不手填, 不补零, 守红线-3**。
2. **parser fresh write 替代 sed 模板**: 因 SZ/NJ HTML files intentionally missing, parser 必须检查 `if not html_path.exists()` 优雅分支 (不能假设 4 files 都在)。sed 模板强行 s/2024/2025/ 会缺这一路径。**教训**: schema 差异的 sub-knife 必须 fresh write, 不能 sed。
3. **SyntaxWarning fix**: docstring 含 `\s` 非法转义, 改纯文本 + `python3 -W error::SyntaxWarning` ast.parse 验证干净。
4. **Python transform print text 对齐**: 从 2024 apply 派生 2025 版时, `replace()` 单源模式漏替换 print "expect 136 = ..." 等 3 行 (mart state 实际正确 154/126/7, 仅 print label stale)。**教训**: Python transform 派生后必须运行验证 print 标签一致, 不能依赖 mart state 反推 print。

---

## 11. 不宣称 (per docs/05 §8.2 + 红线)

- ❌ 不宣布 669a-2025 PASS — 仅 DELIVERED + 26/26 红线 PASS
- ❌ 不宣布 669a 批次完成 — 仅 6/6 sub-knives DELIVERED (2020/2021/2022/2023/2024/2025), 669a 收官 ✓
- ❌ 不宣布 669 program 完成 — 仅 6/60 sub-knives (批量部署 #934 触发条件未到, 仍待 54 sub-knives)
- ❌ 不宣称 2025 harvest 完整 — 22 missing (20× SZ/NJ hongheiku 缺失 + 2× fixed_asset 增速-禁), 守红线-3
- ❌ 不冒充 ops / 不爬网超预算 / 不手填 / 不补零 / 不合并 province-city mart
- ❌ O1 / Gate / M2 / M4 / M5 / M6 仍 OPEN
- ❌ docs/81 零改动

---

## 12. 后续 (per Option A)

| 刀号 | 范围 | 状态 |
|---|---|---|
| **669a-2025** | **4 city × 2025** | **DELIVERED ✓ (本件)** |
| 669b-i | 48 sub-knives | 待 "Start 669b" 签署 (#937) |
| 669j | 6 sub-knives | 待 "Start 669j" 签署 (#938) |
| 批量部署 668+669 | newvps 4-step granular | **669 全部完成后自动触发 (#934, user 2026-09-07 已授权)** |

---

## 13. 链接

- 前置 receipt: `669a-2024-city-harvest-receipt-20260907.md`
- 计划: `/Users/kjonekong/.claude/plans/lively-greeting-shore.md` (knife 663-668 + 669a-j)
- 记忆: [[china-platform-665-multi-knife-program]]

— End 669a-2025 receipt (18/40 cells, 26/26 红线 PASS, DELIVERED ✓; 669a 批次 6/6 收官) —
