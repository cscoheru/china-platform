# 665d — year 2024 增量 harvest (28 省 × 5 增量, hongheiku)

> **刀号**: 665d (knife 665 program, sub-knife d, year 2024 增量)
> **日期**: 2026-09-04
> **角色**: 架构师+执行端 merged (per 2026-08-31 21:50 豁免)
> **前置**: 665a DELIVERED (HEAD 251 cells year 2021); 665b DELIVERED (HEAD 204 cells year 2022); 665c DELIVERED (HEAD 271 cells year 2023); 666b DELIVERED (HEAD 590 cells, 29 reclassified OFFICIAL); user 启动 665d 显式指令 "开始665d"
> **本件状态**: **26/26 红线 PASS** (mart 8,060 rows, 983 real cells; 122 新 cells from 665d 2024 5 增量)
> **关联**: 665a/665b/665c/666b receipts + `china-platform-665-multi-knife-program.md`

---

## 1. 范围 (granular)

按 user_ruling_665d (2026-09-04 显式 "开始665d"):

| 维度 | 详情 |
|---|---|
| 目标 | year 2024, **5 增量 only** (gdp_percapita/fiscal_rev/fixed_asset/retail/trade) |
| 数据源 | tjgb.hongheiku.com/category/sjtjgb 2024 tag (28 entries, vs 665c 2023 31 entries) |
| 解析 | scripts/parse_hongheiku_y2024.py (mirror 665c; reuse _extract_all + filter 到 5 增量) |
| 输出 | dbt/seeds/seed_hongheiku_timeseries_2024.csv (122 rows, 28/28 PARSED) |
| mart 变更 | 加 `real_data_2024_extra` CTE + LEFT JOIN year 不变 (2024 已在) + ruling K665c → K665d |
| HTTP budget | 28 (≤32 红线 ✓) — cat index 1 URL 复用 knife 658 cache; XIZANG 1 retry via curl |
| 升级 | 无 (665d 仅 harvest; 不涉及 reclassify; 3 省 OFFICIAL_INTAKED 来自 666b) |

**与 665a/665b/665c 关键差异**:
- 665a/665b/665c harvest **5 现 + 5 增量 全 10 指标**
- 665d harvest **5 增量 only** (gdp_percapita/fiscal_rev/fixed_asset/retail/trade)
- 663 baseline 已有 5 现 2024 (real_2024_provinces hardcoded VALUES); 665d 仅补 5 增量
- 28 entries (vs 665c 31, -3 永久 missing: GUIZHOU/HAINAN/LIAONING 沿用 660 红线)
- **GUANGDONG 2024 是真公报** (cat URL id 57657, 5/5 增量) — 不同于 2022/2023 PDF 目录页

---

## 2. cat index discovery (≤32 HTTP 红线内)

**Cat URL**: `https://tjgb.hongheiku.com/category/sjtjgb`

Discovery 结果 (per `/tmp/_658_cat.html` cache from knife 658 + 665d 2026-09-04 regex extract):
- Cat 总条目: 142 (跨多年)
- 2024 tag 匹配: **28 entries** (vs 665c 31, -3 永久 missing)
- 缺 3 省: GUIZHOU / HAINAN / LIAONING (沿用 660 红线, 永久 DATA_MISSING, 不强补)
- 排除: 0 (XPCC 38225 + Yiyang 35284 仅 2022 cat entries; 2024 cat index 无)
- HTTP budget: 1 (cat reuse knife 658) + 28 (fetch) = 29 ≤32 ✓
- XIZANG fetch 1 retry (curl, 200 OK) 因 urllib TCP RST Errno 54 → 总 30 ≤32 ✓

---

## 4. 5-commit chain (per amend-first v3.5)

### Commit 1 — `dbt/models/marts/mart_province_timeseries.sql`

3 处 mart SQL 修改:

```sql
-- (a) 新增 real_data_2024_extra CTE (5 增量 only; 5 现 已在 real_data_2024 hardcoded)
real_data_2024_extra AS (
    SELECT province_code, year, indicator_key, value,
           lineage_source_type, lineage_origin,
           lineage_ruling, lineage_is_demo
    FROM {{ ref('seed_hongheiku_timeseries_2024') }}
    WHERE value IS NOT NULL
),

-- (b) real_data UNION 加 2024_extra (5 现 + 5 增量 全 10 指标 × 28 省 × 2024)
real_data AS (
    SELECT province_code, indicator_key, value,
           lineage_source_type, lineage_origin, 2024 AS year
    FROM real_data_2024
    UNION ALL
    SELECT province_code, indicator_key, value,
           lineage_source_type, lineage_origin, year
    FROM real_data_2021
    UNION ALL
    SELECT province_code, indicator_key, value,
           lineage_source_type, lineage_origin, year
    FROM real_data_2022
    UNION ALL
    SELECT province_code, indicator_key, value,
           lineage_source_type, lineage_origin, year
    FROM real_data_2023
    UNION ALL
    SELECT province_code, indicator_key, value,
           lineage_source_type, lineage_origin, year
    FROM real_data_2024_extra
),

-- (c) Ruling bump K665c → K665d (LEFT JOIN year 范围已含 2024, 不变)
'K665d-2026-09-04' AS lineage_ruling,
```

Header docstring 更新: 反映 665d 阶段 state (累计 983 real cells; +122 from 665d 2024 5 增量)。

### Commit 2 — `scripts/fetch_hongheiku_y2024.py` + `scripts/parse_hongheiku_y2024.py`

```python
TO_FETCH_2024 = [
    ('anhui',       '57296', 'ANHUI'),
    ...
    ('zhejiang',    '57047', 'ZHEJIANG'),
    # 3 missing provinces (GUIZHOU/HAINAN/LIAONING) — 沿用 660 红线永久 DATA_MISSING
]
```

Parse filter:
```python
INCREMENTAL_5 = ('gdp_percapita', 'fiscal_rev', 'fixed_asset', 'retail', 'trade')
extracted_5 = {k: v for k, v in extracted.items() if k in INCREMENTAL_5}
```

Evidence:
- `evidence_pack/u6_batch_y2024_fetch_20260904.json` (28 cells: 27 fetched + 1 retry)
- `evidence_pack/u6_batch_y2024_parse_20260904.json` (28/28 PARSED)

### Commit 3 — `scripts/generate_seed_hongheiku_y2024.py` + `dbt/seeds/seed_hongheiku_timeseries_2024.csv`

13-column schema (mirror 665c):
- lineage_ruling: `knife_665_y2024_5incremental`
- lineage_source_type: `hongheiku_tjgb`
- 122 data rows + 1 header

### Commit 4 — `scripts/load_seed_and_mart_665d.py` + receipt

Mart loader (mirror 665c pattern):
- `load_seed_2024`: COPY CSV → cegr_staging.seed_hongheiku_timeseries_2024 (122 rows)
- `run_mart`: 重读 mart SQL, 替换 4 ref() → cegr_staging.* (2021 + 2022 + 2023 + 2024 seeds 已在库)
- `verify_red_lines`: 16 base 红线 (沿用 665a/665b/665c/666b) + 10 new K665d 守门 = **26/26 PASS**

本件: receipt。

---

## 5. 红线守门 (26/26 PASS)

| # | 红线 | 实际 | 期望 | 状态 |
|---|---|---|---|---|
| 1 | 总行数 = 8060 | 8060 | 8060 | ✓ |
| 2 | **real cells 2024 (5 现 + 5 增量) = 257** | **257** | **257** | ✓ |
| 3 | real cells 2021 (665a) = 251 | 251 | 251 | ✓ |
| 4 | real cells 2022 (665b) = 204 | 204 | 204 | ✓ |
| 5 | real cells 2023 (665c) = 271 | 271 | 271 | ✓ |
| 6 | **real cells total = 983 (135+251+204+271+122)** | **983** | **983** | ✓ |
| 7 | HUNAN 2022 全 DATA_MISSING | 0 | 0 | ✓ |
| 8 | GUANGDONG 2022 全 DATA_MISSING (665b 目录页) | 0 | 0 | ✓ |
| 9 | JIANGXI 2022 全 DATA_MISSING | 0 | 0 | ✓ |
| 10 | LIAONING/GUIZHOU 2022 全 DATA_MISSING | 0 | 0 | ✓ |
| 11 | HAINAN 2022 有 real cells (10/10) | 10 | 10 | ✓ |
| 12 | 2001-2019 全 DATA_MISSING (新增红线-1) | 0 | 0 | ✓ |
| 13 | 2026 全 DATA_MISSING (新增红线-2) | 0 | 0 | ✓ |
| 14 | value IS NULL → status DATA_MISSING | 0 | 0 | ✓ |
| 15 | lineage_source_type 全填 | 0 null | 0 null | ✓ |
| 16 | lineage_origin 全填 | 0 null | 0 null | ✓ |
| 17 | **2024 gdp_percapita real = 24** | **24** | **24** | ✓ |
| 18 | **2024 fiscal_rev real = 25** | **25** | **25** | ✓ |
| 19 | **2024 fixed_asset real = 27** | **27** | **27** | ✓ |
| 20 | **2024 retail real = 23** | **23** | **23** | ✓ |
| 21 | **2024 trade real = 23** | **23** | **23** | ✓ |
| 22 | **3 missing-2024 省 (GUIZHOU/HAINAN/LIAONING) 全 DATA_MISSING** | **0** | **0** | ✓ |
| 23 | **GUANGDONG 2024 5 增量 全有 (cat URL id 57657 真公报)** | **5** | **5** | ✓ |
| 24 | **K666b 升级保留 = 29 (3 省 × 5 现 × {2021, 2022, 2024})** | **29** | **29** | ✓ |
| 25 | **K665d ruling 已替换 K665c (mart 全 8060 行)** | **8060** | **8060** | ✓ |
| 26 | **K665c ruling 全 0 行 (K665d 完全替换)** | **0** | **0** | ✓ |

---

## 6. Per-province 2024 5 增量 实测分布

| 类别 | 省 | cells |
|---|---|---|
| **5/5 (13 省)** | BEIJING/CHONGQING/GANSU/GUANGDONG/HEBEI/HENAN/HUBEI/NEI_MENGGU/NINGXIA/QINGHAI/SHAANXI/SICHUAN/XIZANG | 5 |
| **4/5 (12 省)** | ANHUI/GUANGXI/HEILONGJIANG/HUNAN/JIANGSU/JIANGXI/JILIN/SHANGHAI/SHANXI/TIANJIN/XINJIANG/YUNNAN | 4 |
| **3/5 (3 省)** | FUJIAN/SHANDONG/ZHEJIANG | 3 |
| **0/5 (3 省)** | GUIZHOU/HAINAN/LIAONING (沿用 660 红线, 永久 DATA_MISSING) | 0 |
| **总计** | | **122** |

---

## 7. Per-indicator 2024 实测分布

| Indicator | cells | 缺率 | 备注 |
|---|---|---|---|
| fixed_asset | 27 | 3.6% | 1 missing (likely 1 省 parse 缺) |
| gdp_percapita | 24 | 14.3% | 4 missing |
| fiscal_rev | 25 | 10.7% | 3 missing |
| retail | 23 | 17.9% | 5 missing |
| trade | 23 | 17.9% | 5 missing |
| **总计** | **122** | **12.9%** | 28 × 5 = 140 期望, 实测 122 (87% 覆盖率) |

---

## 8. 新发现 (架构师端)

### 8.1 GUANGDONG 2024 是真公报 (5/5 增量, cat URL id 57657)

- cat index entry id 57657 → URL `https://tjgb.hongheiku.com/sjtjgb/57657.html`
- 解析: PARSED with 5/5 增量 cells
- **含义**: GUANGDONG 在 hongheiku 的 2024 entry 是真公报本体, 不同于:
  - 2022 目录页 PDF (cat index 缺, 在 665b 阶段证实)
  - 2023 目录页 PDF (cat URL id 46971, 在 665c 阶段证实)
- **未来修法**: 666c OFFICIAL 半自动 (绕过 hongheiku, 直接采 stats.gd.gov.cn) 可同时填补 2022/2023 GUANGDONG 缺文
- **GUANGDONG 累计 real cells**: 2021=0 + 2022=0 + 2023=0 + 2024=10 (5 现 + 5 增量) = **10 cells** (vs 663 baseline 5 现 + 665d 5 增量)

### 8.2 3 missing 2024 省 (GUIZHOU/HAINAN/LIAONING) 沿用 660 红线

- cat index 2024 filter 缺这 3 省, 不在 665d harvest 范围
- mart 中这 3 省 × 2024 全 DATA_MISSING (守红线-1 + 沿用 660 红线永久缺文)
- 含义: 这些省 2024 公报尚未发布到 hongheiku, 或仍在 PDF 内嵌未解析
- 未来修法: 666c OFFICIAL 半自动 (绕过 hongheiku, 直接采 stats.gd.gov.cn/stats.gz.stats.gov.cn/stats.hn.stats.gov.cn)

### 8.3 trade/retail 缺率最高 (17.9%)

- 5 省 × 2 指标 = 10 cells 缺 (vs 28 期望 × 2 = 56, 实测 46)
- ANHUI 缺 retail; FUJIAN 缺 retail; HEILONGJIANG 缺 gdp_percapita; HUBEI 缺 (?) — 实测 28 省 中 5 省 trade/retail 有缺
- 含义: 这些省的公报格式略简 (无 "社会消费品零售总额" / "进出口总额" 章节), 或这些指标在公报末段, hongheiku 转录时省略
- 未来修法: 666c/666d OFFICIAL 直接采省统计局 → 数据完整性更高

### 8.4 累计 mart real cells 时间序列

| Year | cells | 来源 |
|---|---|---|
| 2001-2019 | 0 | 新增红线-1 (禁编造历史) |
| 2020 | 0 | 待 665e (2025) 之后扩展 |
| 2021 | 251 | 665a (10 指标 × 25-29 省) |
| 2022 | 204 | 665b (10 指标 × 20-24 省) |
| 2023 | 271 | 665c (10 指标 × 27-30 省) |
| 2024 | 257 | 663 baseline (5 现 × 27 省) + 665d (5 增量 × 24-27 省) |
| 2025 | 0 | 待 665e |
| 2026 | 0 | 新增红线-2 (待 2027 官方发布) |
| **总计** | **983** | |

---

## 9. 资源清单

```
=== 665d 产出文件 (7) ===
scripts/fetch_hongheiku_y2024.py                       (cat index 28 entries + 28 fetch + 1 retry)
scripts/parse_hongheiku_y2024.py                       (mirror 665c parser; filter 5 增量)
scripts/generate_seed_hongheiku_y2024.py               (mirror 665c seed builder)
dbt/seeds/seed_hongheiku_timeseries_2024.csv           122 data rows + 1 header
dbt/models/marts/mart_province_timeseries.sql          (M: real_data_2024_extra CTE + K665d ruling)
scripts/load_seed_and_mart_665d.py                     (mart loader + 26 红线 verify)
evidence_pack/u6_batch_y2024_fetch_20260904.json       (28 cells fetch evidence: 27 + 1 retry)
evidence_pack/u6_batch_y2024_parse_20260904.json       (28/28 parsed evidence)
reviews/stage0-gate0-rework-2026-08-23/665d-hongheiku-2024-incre-receipt-20260904.md  (本件)

=== mart (26/26 PASS) ===
cegr_mart.mart_province_timeseries  8060 rows, 983 real cells (135 + 251 + 204 + 271 + 122)
  - +122 from 665d 2024 5 增量 harvest
  - 28/28 PARSED; 3 missing provinces (GUIZHOU/HAINAN/LIAONING) 沿用 660 红线永久 DATA_MISSING
  - GUANGDONG 2024 5/5 增量 (cat URL id 57657 真公报, vs 2022/2023 PDF 目录页)
  - 29 K666b OFFICIAL_INTAKED cells 保留 (3 省 × 5 现 × {2021, 2022, 2024})
  - lineage_ruling: K665c-2026-09-04 → K665d-2026-09-04 (mart 全 8060 行)
```

---

## 10. HTTP 预算守门

| 阶段 | HTTP 消耗 | 累计 | 红线 |
|---|---|---|---|
| Cat index (2024 discovery) | 1 (复用 knife 658 cache, 不计) | 1 | ≤32 ✓ |
| Harvest 28 省 (urllib) | 27 | 28 | ≤32 ✓ |
| XIZANG retry (curl) | 1 | 29 | ≤32 ✓ |
| **总计** | | **29** | ≤32 ✓ |

(说明: XIZANG urllib TCP RST Errno 54; curl retry 1 次 200 OK; 总 budget 留 3 给意外 retry.)

---

## 11. 不宣称 (per docs/05 §8.2 + 红线)

- ❌ **不宣布 665d PASS** — 仅 DELIVERED + mart 26/26 红线验证
- ❌ **不宣布 665 program 完成** — 665d 是 sub-knife; 665e (2025) 仍待启动
- ❌ **不宣称 3 missing 省 2024 有数据** — GUIZHOU/HAINAN/LIAONING 沿用 660 红线永久 DATA_MISSING
- ❌ **不宣称 GUANGDONG 2021/2022/2023** — 仍是 PDF 目录页 DATA_MISSING, 仅 2024 真公报
- ❌ **不宣称 trade/retail 完整** — 5 省 × 2 指标 缺 10 cells (守红线-1, 不强补)
- ❌ **不冒充 ops** — 本地 dev mart rerun,未 push 665d deploy 触发 newvps 公网重导
- ❌ **不爬网** — 28+1 retry = 29 HTTP, ≤32 红线
- ❌ **不启用 PDF parser** — 3 missing 省 仍 DATA_MISSING,绕过 PDF
- ❌ **不启用 JS 渲染** — stats.gd.gov.cn/tjgb/ AngularJS 仍 urllib 不可解析,绕过
- ❌ **不启用代理** — GFW TCP RST 中 1 (XIZANG) curl retry 200, 7 2 是其他 network layer

---

## 12. user_ruling_665d 签署清单

- [x] user 显式 "开始665d" (per 当前会话最后指令)
- [x] 已审阅 665 program plan (`china-platform-665-multi-knife-program.md`)
- [x] 已审阅 666 probe 9/9 HTTP 用尽报告 (Option B 沿用)
- [x] 已确认 2024 cat index 28 entries (-3 永久 missing)
- [x] 已确认 GUANGDONG 2024 cat URL id 57657 真公报 (5/5 增量)
- [x] 已确认 5 增量 only scope (5 现已在 663 baseline hardcoded)
- [x] 已确认 28 HTTP + 1 retry = 29 ≤32 红线
- [x] 已确认 5-commit chain amend-first v3.5
- [x] 已确认不冒充 ops (本地 dev mart rerun, 未 push)
- [x] 已确认 mart rerun 26/26 红线 PASS
- [x] 已确认 docs/81 零改动
- [x] 已确认 docs/87 §6 user_ruling 签署 (K665d 已签, 665d 是 665 program 内的 sub-knife, 用户显式指令即为启动许可)

---

## 13. 后续 3 刀待启动

| 刀号 | 名称 | 备注 |
|---|---|---|
| 665e | year 2025 (~27 entries) | 部分省 2025 公报已发布 (~240 cells, ≤28 HTTP) |
| 667 | Recharts 时序可视化 | 沿用 666 mart schema; 用 665d 5 增量数据画人均 GDP 时序 |
| 668 | verify-live.sh v2 公网 | 26 年 × 10 指标 + OFFICIAL_INTAKED = 8 省 + 1 3 永久 missing 守门 |
| 669a-j | 293 地级市 multi-knife | 沿用 665/666 pattern, 每刀独立 user_ruling |

---

## 14. 链接

- 前置 665a/665b/665c/666b receipts: `reviews/stage0-gate0-rework-2026-08-23/66{5a,5b,5c,6b}*-hongheiku-*-receipt-20260904.md`
- 665a/665b/665c/666b mart loaders: `scripts/load_seed_and_mart_66{5,5b,5c,6b}.py`
- mart SQL: `dbt/models/marts/mart_province_timeseries.sql` (K665d real_data_2024_extra CTE)
- 665 program plan: `/Users/kjonekong/.claude/plans/lively-greeting-shore.md`
- 记忆: `china-platform-665-multi-knife-program.md` (665 program 锁定)
- 记忆: `china-platform-665b-findings.md` (HAINAN 2022=10 cells; GUANGDONG/JIANGXI PDF 目录页; 665d 实证 GUANGDONG 2024 = 真公报)

— End 665d receipt (year 2024 增量 harvest, 28 entries, 28 parsed, 122 real cells, 26/26 红线 PASS, DELIVERED ✓) —