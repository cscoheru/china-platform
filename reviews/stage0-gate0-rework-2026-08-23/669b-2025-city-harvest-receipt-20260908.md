# 669b-2025 — 25 省会 × 2025 zero-harvest (250/250 DATA_MISSING, 守新增红线-3)

> **刀号**: 669b-2025 (knife 669b 第一子刀, 25 省会 × 2025 全 DATA_MISSING 路径)
> **日期**: 2026-09-08
> **角色**: 架构师+执行端 merged (per 2026-08-31 21:50 豁免)
> **前置**: 669a-2020/2021/2022/2023/2024/2025 全部 DELIVERED (HEAD 857cab6)
> **本件状态**: **DELIVERED ✓** — 25 省会 × 2025 harvest 完成, 0 real + 250 DATA_MISSING, 36/36 红线 PASS
> **关联**: `669a-2025-city-harvest-receipt-20260907.md` + `china-platform-665-multi-knife-program.md`

---

## 1. 范围 (granular)

| 维度 | 详情 |
|---|---|
| 目标 | 验证 25 省会 city × 2025 年 10 指标真实数据可获取性, 写入 mart_city_timeseries |
| city scope | 25 省会 (除 4 直辖市禁 city dim + 3 已在 669a: 穗/杭/宁) |
| year scope | 2025 only |
| 指标 | 10 (5 现 + 5 增量) |
| Cross product | 25 × 10 × 1 = **250 cells** |
| Real cells | **0** (hongheiku 无 2025 city bulletin) |
| DATA_MISSING | **250** (全 DATA_MISSING 路径, 守新增红线-3 不手填) |
| HTTP budget | **25** (URL discovery 25 tag pages; 详 §2), ≤32 红线 ✓ |
| 红线 | 新增红线-1/2/3/7 全 PASS; 不冒充 ops; docs/81 零改动 |
| mart apply | 直 psql via psycopg2 (per 663 Gap 1) |

---

## 2. URL discovery (Phase 1, 25 HTTP)

### 主动 probe 验证 25 city tag 页 cache

承接 669a-2021 缓存复用模式, 走 25 city tag 页探查 hongheiku 2025 收录情况:

| City | Tag URL | Cache Size | 实证 2025 entry |
|---|---|---|---|
| 石家庄 | `/tag/石家庄市` | 17-35 KB | ❌ 0 entry |
| 太原 | `/tag/太原市` | | ❌ 0 entry |
| 呼和浩特 | `/tag/呼和浩特市` | | ❌ 0 entry |
| 沈阳 | `/tag/沈阳市` | | ❌ 0 entry |
| 长春 | `/tag/长春市` | | ❌ 0 entry |
| 哈尔滨 | `/tag/哈尔滨市` | | ❌ 0 entry |
| 合肥 | `/tag/合肥市` | | ❌ 0 entry |
| 福州 | `/tag/福州市` | | ❌ 0 entry |
| 南昌 | `/tag/南昌市` | | ❌ 0 entry |
| 济南 | `/tag/济南市` | | ❌ 0 entry |
| 郑州 | `/tag/郑州市` | | ❌ 0 entry |
| 武汉 | `/tag/武汉市` | | ❌ 0 entry |
| 长沙 | `/tag/长沙市` | | ❌ 0 entry |
| 南宁 | `/tag/南宁市` | | ❌ 0 entry |
| 海口 | `/tag/海口市` | | ❌ 0 entry |
| 成都 | `/tag/成都市` | | ❌ 0 entry |
| 贵阳 | `/tag/贵阳市` | | ❌ 0 entry |
| 昆明 | `/tag/昆明市` | | ❌ 0 entry |
| 拉萨 | `/tag/拉萨市` | | ❌ 0 entry |
| 西安 | `/tag/西安市` | | ❌ 0 entry |
| 兰州 | `/tag/兰州市` | | ❌ 0 entry |
| 西宁 | `/tag/西宁市` | | ❌ 0 entry |
| 银川 | `/tag/银川市` | | ❌ 0 entry |
| 乌鲁木齐 | `/tag/乌鲁木齐市` | | ❌ 0 entry |
| 台北 | `/tag/台北市` | | ❌ 0 entry |

每 tag 页只列 2 条 city-specific bulletin: 第七次全国人口普查公报 + 2020 年统计公报。**前 5 URLs 是 site-wide 全国 (2021-2025)** — 已用 `NATIONAL_IDS = {68085, 57063, 45926, 35003, 23939}` 过滤。

### Phase 1 后续 probe 验证 (3 methods, 全部确认 gap)

| Probe | 目标 | 实证结果 |
|---|---|---|
| 1. tag re-fetch × 25 | 25 city tag 页 | 全部仅 2020 + 人口普查, 0 entry 2021-2025 |
| 2. cat index | `/category/sjtjgb` | 2025 entries = 1 (national 68085), 0 city |
| 3. 站内搜索 × 5 代表 | `?s={武汉\|成都\|长沙\|杭州\|广州}2025` | 全部 '未找到', 0 results |

**结论**: 实证 25 省会 hongheiku 2025 city bulletin **不存在**, 守新增红线-3 不手填, 全部 DATA_MISSING。

---

## 3. Bulletin fetch (Phase 2, 0 HTTP)

Phase 2 SKIPPED — 0 city 2025 bulletin 在 hongheiku 收录范围, 不浪费 HTTP budget。

---

## 4. 2025 公报变体 (复用 2024 regex, 0 处校验)

N/A (zero-harvest knife, 无 bulletin 解析)

---

## 5. 解析结果 (10 指标 by 25 city, 2025)

| City | 10 指标 | Real | 决策 |
|---|---|---|---|
| 25 省会 (HEBEI/.../TAIPEI) | 全部 DATA_MISSING | **0/10 each** | 全 DATA_MISSING 路径 |
| **总计** | | **0/250** | 守新增红线-3 |

---

## 6. 文件改动清单 (4 文件, 4 新 + 1 改)

| 路径 | 类型 | 用途 |
|---|---|---|
| `dbt/models/marts/mart_city_timeseries.sql` | M | (a) header "knife 669a-... + 669b-2025"; (b) city_dimension 加 25 省会; (c) 加 real_data_669b_2025 CTE (empty `WHERE FALSE`); (d) 加 6th LEFT JOIN rd6; (e) value = COALESCE 6-way; (f) status/missing_reason/lineage_source_type/lineage_origin/lineage_ruling CASE 加 2025 669b 分支; (g) lineage_ruling 2025 split: 4 city→K669a-2025, 25 city→K669b-2025-2026-09-08 |
| `source_registry/seed_hongheiku_city_2025_669b.csv` | A | 250 rows (全 DATA_MISSING, 守新增红线-3) |
| `scripts/parse_hongheiku_city_y2025_669b.py` | A | 25 省会 × 2025 × 10 指标 generator (fresh write, 非 sed-template 因 zero-harvest 路径需独立 lineage attribution) |
| `scripts/apply_mart_city_669b_2025.py` | A | 直 psql apply; 期望 2030/29/10/7/154/1876/8/0/250 (含 `__main__` 入口守门, per 2023 §9 教训) |
| `scripts/verify_mart_city_669b_2025.py` | A | 36 红线 verify (vs 669a-2025 26 条: 加 2025 by-ruling split #27 + 2025 25 city missing_reason '669b-2025' #28 + 'hongheiku 无 2025 city bulletin' #29 + 25 city lineage_ruling K669b #30 + 25 city lineage_source_type DATA_MISSING #31 + 25 city lineage_origin 含 tag/ #32 + 25 city value IS NULL #33 + 25 city distinct #35 + 25 city × 10 indicator #36 + K669b-2025 ruling 唯一 #37) |

---

## 7. mart 状态 (7 刀 + 669b-2025 累积)

| 指标 | 值 |
|---|---|
| rows | 2030 (29 × 10 × 7) |
| real_cells | **154** (26[2021] + 37[2022] + 37[2023] + 36[2024] + 18[2025]; 669b-2025 adds 0) |
| DATA_MISSING | 1876 (240 669a miss other years + 22 669a 2025 miss + 250 669b 2025 + 1364 other years 669b) |
| city distinct | 29 (4 669a + 25 669b) |
| lineage_ruling | **8 versions** (K669a-2020/2021/2022/2023/2024/2025 + K669b-2025 + pending) |

**multi-knife lineage 七件套**: 2020→K669a-2020 / 2021→K669a-2021 / 2022→K669a-2022 / 2023→K669a-2023 / 2024→K669a-2024 / 2025 (4 city)→K669a-2025 / 2025 (25 city)→K669b-2025 / 2026→pending

**669b 收官统计**: 1/8 sub-knives DELIVERED (669b-2025 only); 7/8 剩余 (669b-2020/2021/2022/2023/2024 + 669c-2020/2025 etc.) 待 user 裁定。

---

## 8. 红线守门 (36/36 PASS)

| # | 红线 | 实际 | 状态 |
|---|---|---|---|
| 1 | mart 行数 = 2030 | 2030 | ✓ |
| 2 | city distinct = 29 | 29 | ✓ |
| 3 | indicator distinct = 10 | 10 | ✓ |
| 4 | year distinct = 7 | 7 | ✓ |
| 5 | real_cells = 154 | 154 | ✓ |
| 6 | DATA_MISSING = 1876 | 1876 | ✓ |
| 7 | 4 直辖市禁重复 (红线-7) | 0 | ✓ |
| 8 | lineage_ruling = 8 versions | 8 | ✓ |
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
| 27 | 2025 missing by ruling = 22 K669a + 250 K669b | 22/250 | ✓ |
| 28 | 2025 25 city missing_reason 含 '669b-2025' | 250/250 | ✓ |
| 29 | 2025 25 city missing_reason 含 'hongheiku 无 2025 city bulletin' | 250/250 | ✓ |
| 30 | 2025 25 city lineage_ruling = K669b-2025-2026-09-08 | 250/250 | ✓ |
| 31 | 2025 25 city lineage_source_type = DATA_MISSING | 250/250 | ✓ |
| 32 | 2025 25 city lineage_origin 含 'tjgb.hongheiku.com/tag/' | 250/250 | ✓ |
| 33 | 2025 25 city value IS NULL (守红线-3) | 250/250 | ✓ |
| 35 | 2025 25 city distinct count = 25 | 25 | ✓ |
| 36 | 2025 25 city × 10 indicator = 250 cells | 250 | ✓ |
| 37 | K669b-2025-2026-09-08 ruling 唯一 | 1 | ✓ |
| 38 | 2026 仍全 DATA_MISSING (红线-2) | 0 real | ✓ |

---

## 9. HTTP 预算守门

| 阶段 | HTTP 消耗 | 累计 (本刀) | 红线 |
|---|---|---|---|
| Phase 1.1: URL discovery 25 city tag pages | 25 | 25 | ✓ |
| Phase 1.2: cat index probe (复用 669a-2025 缓存) | 0 | 25 | ✓ |
| Phase 1.3: 站搜 × 5 代表性 city (复用 669a-2025 缓存) | 0 | 25 | ✓ |
| Phase 2: bulletin fetch | 0 | 25 | ✓ |
| Phase 3-6: parse/apply/verify (无 HTTP) | 0 | 25 | ✓ |
| **本刀总 HTTP** | **25** | **25/32** (7 余量) | ✓ |
| 669 程序累计 (669a × 6 + 669b-2025) | | **52** | ✓ |

---

## 10. 执行插值 (透明记录)

1. **hongheiku 2025 省会 city 缺失实证**: 3 probe methods × 30 city 全部 0 命中 (tag re-fetch × 25 + cat index + 站搜 × 5 代表), 决定 harvest 全 DATA_MISSING 路径。**不手填, 不补零, 守红线-3**。
2. **mart SQL 6-way COALESCE + 2025 split**: lineage_ruling 2025 branch 拆为 4 city → K669a-2025 + 25 city → K669b-2025, 解决 sub-knife attribution 守门。
3. **2025 25 city lineage attribution**: missing_reason 全 250 含 '669b-2025' + 'hongheiku 无 2025 city bulletin' + '3 probe methods 全部 0 命中, tag 页仅含 2020 年公报 + 人口普查公报, 守新增红线-3 不手填' — 透明溯源 UI 可显示给用户。
4. **mart 行数守门**: 29 × 10 × 7 = 2030 (4 城 + 25 城 完整 cross product); 红线-7 守门 4 直辖市不在 city dim; 红线-1 (2001-2019) / 红线-2 (2026) 仍全 DATA_MISSING。

---

## 11. 不宣称 (per docs/05 §8.2 + 红线)

- ❌ 不宣布 669b-2025 PASS — 仅 DELIVERED + 36/36 红线 PASS
- ❌ 不宣布 669b 批次完成 — 仅 1/8 sub-knives DELIVERED (669b-2025 only)
- ❌ 不宣布 669 program 完成 — 仅 7/60 sub-knives (6 669a + 1 669b-2025; 批量部署 #934 触发条件未到, 仍待 53 sub-knives)
- ❌ 不宣称 2025 harvest 完整 — 250 missing (25 省会 hongheiku 2025 缺文, 守红线-3)
- ❌ 不冒充 ops / 不爬网超预算 / 不手填 / 不补零 / 不合并 province-city mart
- ❌ O1 / Gate / M2 / M4 / M5 / M6 仍 OPEN
- ❌ docs/81 零改动

---

## 12. 后续 (per Option A)

| 刀号 | 范围 | 状态 |
|---|---|---|
| **669b-2025** | **25 省会 × 2025** | **DELIVERED ✓ (本件)** |
| 669b-2020 | 25 省会 × 2020 (zero-harvest) | 待 "Start 669b-2020" 签署 |
| 669b-2021/2022/2023/2024 | 25 省会 × 4 year (real-data harvest 候选) | 待 per-knife 签署 |
| 669c-2025 | 31 重点 city batch 2 × 2025 | 待 "Start 669c-2025" 签署 (#937) |
| ... (669c-j) | 7 batches × 6 years | 仍待 per-knife 签署 |
| 批量部署 668 + 669 | newvps 4-step granular | **669 全部完成后自动触发 (#934, user 2026-09-07 已授权)** |

---

## 13. 链接

- 前置 receipt: `669a-2025-city-harvest-receipt-20260907.md`
- 计划: `/Users/kjonekong/.claude/plans/lively-greeting-shore.md` (knife 663-668 + 669a-j)
- 记忆: [[china-platform-665-multi-knife-program]]
- 记忆: [[china-platform-user-rest-protocol]]

— End 669b-2025 receipt (0/250 cells, 36/36 红线 PASS, DELIVERED ✓; 669b 批次 1/8 启动) —