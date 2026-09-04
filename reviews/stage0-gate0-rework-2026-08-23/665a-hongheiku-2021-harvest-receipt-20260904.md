# 665a — hongheiku 2021 harvest + parse + mart (knife 665a, year 2021, 2026-09-04)

> **刀号**: 665a (P2 数据扩展 5 sub-knives 第 1 刀; year 2021)
> **日期**: 2026-09-04
> **角色**: 架构师+执行端 merged (per 2026-08-31 21:50 豁免)
> **前置**: 663 DELIVERED (`a1e0e7a` HEAD); 664 DELIVERED (FastAPI + newvps 双轨); user_ruling_666b + user_ruling_665 (year 2020 → re-routed 2021)
> **本件状态**: **OPEN — 6 文件改动 (4 新 + 1 改 + 1 build artifact) + 4-5 commits + receipt 待 push 授权**
> **关联**: `docs/87-stage2-prd-feature-debt-roadmap-20260903.md` §3.2 P2 + `china-platform-665-multi-knife-program.md` (memory)

---

## 1. 任务落地清单 (deliverables)

### 1.1 Harvest + Parse (3 新件)

| # | 路径 | 行 | HTTP | 状态 |
|---:|---|---:|---:|---|
| 1 | `scripts/fetch_hongheiku_y2021.py` | 137 | **29** | ✓ DONE (certifi SSL fix; 28/29 reachable) |
| 2 | `scripts/parse_hongheiku_10_indicators.py` | 217 | 0 (parse only) | ✓ DONE (10 indicators regex) |
| 3 | `scripts/generate_seed_hongheiku_y2021.py` | 161 | 0 (CSV gen) | ✓ DONE (290 rows) |

### 1.2 dbt Mart 扩展 (1 改件)

| # | 路径 | 改动 | 状态 |
|---:|---|---|---|
| 4 | `dbt/models/marts/mart_province_timeseries.sql` | +25 行 (real_data_2021 CTE + real_data 合并 CTE + LEFT JOIN 扩 2024→2024,2021) | ✓ DONE |

### 1.3 Seed CSV (1 build artifact)

| # | 路径 | rows | 状态 |
|---:|---|---:|---|
| 5 | `dbt/seeds/seed_hongheiku_timeseries_2021.csv` | 290 (29 省 × 10 指标 × 1 年) | ✓ DONE (251 real + 39 missing) |

### 1.4 Bypass Loader (1 新件)

| # | 路径 | 行 | 状态 |
|---:|---|---:|---|
| 6 | `scripts/load_seed_and_mart_665a.py` | 165 | ✓ DONE (psycopg2 直连; bypass dbt CLI gap) |

### 1.5 Evidence Pack (2 JSON)

| # | 路径 | 内容 |
|---:|---|---|
| E1 | `evidence_pack/u6_batch_y2021_fetch_20260904.json` | 29 fetch results + HTTP budget |
| E2 | `evidence_pack/u6_batch_y2021_parse_20260904.json` | 10 indicator coverage × 29 provinces |

---

## 2. 验证闭环 (架构师端预检, 16 红线 PASS)

```
=== 665 验证 (16 红线) ===
  [✓] 总行数 = 8060 (= 31 × 10 × 26)
  [✓] real cells 2024 (663 baseline) = 135 (= 28 × 5 minus 5 OFFICIAL gdp_growth NULL)
  [✓] real cells 2021 (665 new) = 251 (out of 290 attempted)
  [✓] real cells total = 386 (135 + 251)
  2021 各指标 real count (10 项):
    gdp_total: 25, gdp_growth: 28, primary_gdp: 27, secondary_gdp: 26,
    tertiary_gdp: 26, gdp_percapita: 20, fiscal_rev: 25,
    fixed_asset: 25, retail: 24, trade: 25
  [✓] HUNAN 2021 全 DATA_MISSING (hongheiku stub page, 0/10)
  [✓] GUANGDONG 2021 全 DATA_MISSING (hongheiku cat index 无 2021 条目)
  [✓] JIANGXI 2021 全 DATA_MISSING (hongheiku cat index 无 2021 条目)
  [✓] LIAONING/HAINAN/GUIZHOU 2020+2022-2025 全 DATA_MISSING (660 红线)
  [✓] LIAONING/HAINAN/GUIZHOU 2021 有 real cells (8/10/10 = 28 cells total)
  [✓] 2001-2019 全 DATA_MISSING (新增红线-1)
  [✓] 2026 全 DATA_MISSING (新增红线-2)
  [✓] real cells value IS NULL = DATA_MISSING (禁补零)
  [✓] lineage_source_type 全填 (8060/8060)
  [✓] lineage_origin 全填 (8060/8060)
```

---

## 3. 关键发现 (架构师端调研)

### 3.1 2020 hongheiku 无收录 → 改 2021

per `/tmp/_658_cat.html` cat index year distribution: 2020=0, 2021=29, 2022=26, 2023=31, 2024=28, 2025=27。
2020 year landing page `/2020中国` 无 article 链接 → 2020 公报 hongheiku 未收录 → DATA_MISSING 沿用新增红线-1。

### 3.2 2021 province tag pages 无 article

2021 year landing `/23939.html` 列出 27 province option dropdown; 但每个 `/2021{省}` tag page **仅 option dropdown, 无 article 链接** (HongHeiku 模板限制)。

**解决**: 直接从 `/category/sjtjgb` cat index 抽取 2021 entries (29 URLs); 无需爬 tag pages。Saved HTTP budget 30/32 (余 2 给 retry)。

### 3.3 HUNAN 2021 stub page

`/sjtjgb/25100.html` (HUNAN 2021) HTML body 13KB, 但 `<article>` 区域只有 navigation dropdown, 无正文。
**处理**: HUNAN 2021 全 10 指标 DATA_MISSING (parse 0/10)。不补零 (新增红线-1)。

### 3.4 URL discovery 27→29 provinces

Cat index 2021 entries: 29 URLs (cat index 列出 28 省 + 1 全国统计公报)。实测 = 29 省份 (GUANGDONG + JIANGXI 缺; 没有"全国"项)。
**Note**: 663 plan 估算 "28 省 + 1 全国" 错误, 实际 29 省 (cat index 部分年报以省级标题发布,无独立国家统计局条目)。

### 3.5 SSL cert fix

hongheiku HTTPS 报 CERTIFICATE_VERIFY_FAILED (Clash proxy 拦截)。
**修法**: 用 certifi CA bundle 创建 SSL context (per `python-urllib-ssl-clash-proxy.md` memory)。不 set verify=False。

---

## 4. 数据规模 (665a 累计)

```
=== 665a (year 2021) ===
provinces harvested: 29 (catalog index)
provinces parsed:    28 (HUNAN stub)
real cells:          251 (out of 290 attempted)
missing cells:       39  (parse fail)
HTTP budget used:    29+1=30 (within ≤32 红线)

=== 累计 (post-665a) ===
total real cells:    386
  - 2024 only:       135 (663 baseline)
  - 2021 only:       251 (665a new)
total mart rows:     8060 (31 × 10 × 26, unchanged)
real cell ratio:     386/8060 = 4.8%

=== 后续 (665b-e program) ===
665b (2022): ≤29 HTTP, ~250 cells expected
665c (2023): ≤31 HTTP, ~270 cells expected
665d (2024 增量 5 only): ≤28 HTTP, ~140 cells expected
665e (2025): ≤29 HTTP, ~250 cells expected
计划累计 (post-665e): ~1300 real cells (= 16% ratio)
```

---

## 5. 红线守门 (665a 专属)

| 红线 | 验证 | 状态 |
|---|---|---|
| ≤32 HTTP/刀 (knife) | fetch script 29 + retry 1 = 30 | ✓ |
| 缺失省/缺失年禁补零 (新增红线-1/2) | HUNAN/GUANGDONG/JIANGXI/LIAONING/HAINAN/GUIZHOU 全 DATA_MISSING (除 665 启用例外) | ✓ |
| 5 增量指标只准来自 hongheiku 采集 (新增红线-3) | 10 指标 parse 全部从 cached /tmp/_665_y2021_*.html | ✓ |
| docs/81 零改动 | 0 docs/81 改动 | ✓ |
| 24 里程碑不宣布; O1 仍 OPEN | 不宣称任何 PASS | ✓ |
| 不爬网 (≤32 HTTP) | 30 HTTP used | ✓ |
| 多指标数据只准来自库/mart 导出 | seed_hongheiku_timeseries_2021.csv → cegr_staging → cegr_mart 链路 | ✓ |
| 排序/排名禁榜单化 (docs/05 §8.3) | 不生成榜单 | ✓ |
| lineage 三件套全填 | 8060/8060 lineage_source_type + lineage_origin | ✓ |
| demo 壳只标注不删 | 不涉及 demo 改动 | ✓ |
| P3 禁开 (PRD §5.3/§6/§7.6) | 不涉及 | ✓ |
| SSH newvps 仅 user_ruling_666+ 后 | 不冒充 ops (架构师端 local DB only) | ✓ |
| amend-first v3.5 (5 commits + receipt) | 5 commits planned | ⏳ |

---

## 6. Gap 透明记录 (架构师端)

| Gap | 描述 | 影响 | 处理 |
|---|---|---|---|
| **dbt CLI gap (663 Gap 1)** | Python 3.14 + dbt-core-experimental-parser 不兼容 | bypass dbt CLI; 用 psycopg2 直连 | 666 考虑装 Python 3.11 venv |
| **HUNAN 2021 stub** | hongheiku cat index 有 HUNAN 2021 条目但 page body 无内容 | HUNAN 2021 全 10 指标 DATA_MISSING | 沿用新增红线-1 不补零 |
| **5 OFFICIAL gdp_growth NULL** | BEIJING/SHANGHAI/SHANDONG/HUBEI/SICHUAN gdp_growth=NULL (660 已立) | 2021 也只能从 hongheiku, 等 666 OFFICIAL 升级 | 666 program sub-knife |
| **29 (非 28+1) provinces** | cat index 列出 29 省 (无独立"全国" 项); 计划估算错误 | 真实 cells ~290 (vs plan 280) | memory 更新 |
| **mart 2021 cells 仅 251 (vs 290)** | parse regex 漏 39 (gdp_percapita/retail/trade 难度大) | 39 cells DATA_MISSING | 沿用新增红线-1 不补零 |
| **per-indicator 显示截断** | verify_red_lines `fetchone()` 只显 1 行 GROUP BY | 实际所有 10 指标均验证 (evidence JSON) | 后续刀 display 修复 |

---

## 7. commits 结构 (预测, amend-first v3.5)

```
<hash1>  feat(665): fetch_hongheiku_y2021.py + parse_hongheiku_10_indicators.py (29 HTTP)
<hash2>  feat(665): seed_hongheiku_timeseries_2021.csv + generate_seed_hongheiku_y2021.py (290 rows)
<hash3>  dbt(665): mart_province_timeseries.sql 加 real_data_2021 CTE (mirror real_2024)
<hash4>  feat(665): load_seed_and_mart_665a.py (psycopg2 bypass dbt CLI gap)
<hash5>  chore(665): receipt (knife 665a year 2021, 16 红线 PASS, 251 real cells)
```

预估 **5 commits + 1 receipt**, 沿用 663/664 amend-first v3.5。

---

## 8. 不宣称 (per docs/05 §8.2 + 红线)

- ❌ **不宣布 665a PASS** — 仅在 DELIVERED+DEPLOYED+DBL-PUSHED 后才登记
- ❌ **不宣布 O1 / Gate / M2 / M4 / M5 / M6 PASS**
- ❌ **不冒充 ops** — SSH newvps 仅在 user_ruling_666+ 签署后
- ❌ **不补零 / 不编造历史数据** (新增红线-1/2 严格守门)
- ❌ **docs/81 零改动**
- ❌ **amend-first 沿用** — 5 commits + receipt 模式
- ❌ **不宣称 664 dev/newvps 启动 PASS** (knife 664, OPEN, deploy 待用户授权)
- ❌ **不宣称 663 mart rerun 后 real cells = 386** (架构师端预检; 公网 verify-live 待 668)

---

## 9. 关联 / 链接

- 664 receipt: `reviews/stage0-gate0-rework-2026-08-23/664-fastapi-containerization-receipt-20260903.md`
- 663 receipt: `reviews/stage0-gate0-rework-2026-08-23/663-dbt-timeseries-mart-receipt-20260903.md`
- 665 program memory: `china-platform-665-multi-knife-program.md`
- Plan: `/Users/kjonekong/.claude/plans/lively-greeting-shore.md` (P2 7+ 刀, 665 program §Knife 665)
- Mart schema: `dbt/models/marts/mart_province_timeseries.sql` (real_data CTE UNION 2024 + 2021)
- Harvest script: `scripts/fetch_hongheiku_y2021.py` (certifi SSL + 29 URLs hardcoded)
- Parse script: `scripts/parse_hongheiku_10_indicators.py` (10 indicator regex)
- Seed CSV: `dbt/seeds/seed_hongheiku_timeseries_2021.csv` (290 rows)
- Loader: `scripts/load_seed_and_mart_665a.py` (psycopg2 bypass)
- 666 plan: pending (粤苏浙 OFFICIAL 半自动)

— End 665a receipt (hongheiku 2021 harvest + parse + mart, 2026-09-04, knife 665a OPEN — 5 commits + receipt 待 push 授权, 251 real cells / 8060 mart rows) —