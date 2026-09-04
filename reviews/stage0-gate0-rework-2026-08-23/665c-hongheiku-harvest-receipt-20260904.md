# 665c — year 2023 harvest (31 entries, hongheiku)

> **刀号**: 665c (knife 665 program, sub-knife c, year 2023)
> **日期**: 2026-09-04
> **角色**: 架构师+执行端 merged (per 2026-08-31 21:50 豁免)
> **前置**: 665a DELIVERED (HEAD 251 cells year 2021); 665b DELIVERED (HEAD 204 cells year 2022); 666b DELIVERED (HEAD 590 cells, 29 reclassified OFFICIAL); user 启动 665c 显式指令 "开始665c"
> **本件状态**: **26/26 红线 PASS** (mart 8,060 rows, 861 real cells; 271 新 cells from 665c 2023)
> **关联**: 665a/665b/666b receipts + `china-platform-665-multi-knife-program.md`

---

## 1. 范围 (granular)

按 user_ruling_665c (2026-09-04 显式 "开始665c"):

| 维度 | 详情 |
|---|---|
| 目标 | year 2023, 31 省 × 10 指标 hongheiku harvest |
| 数据源 | tjgb.hongheiku.com/category/sjtjgb 2023 tag (31 entries, vs 665b 24) |
| 解析 | scripts/parse_hongheiku_y2023.py (mirror 665b; reuse _extract_all + INDICATOR_LABELS from 665a) |
| 输出 | dbt/seeds/seed_hongheiku_timeseries_2023.csv (271 rows, 30/31 PARSED) |
| mart 变更 | 加 `real_data_2023` CTE + LEFT JOIN `cp.year IN (2024, 2021, 2022, 2023)` + ruling K666b → K665c |
| HTTP budget | 31 (≤32 红线 ✓) — cat index 1 URL 复用 666 probe stage |
| 升级 | 无 (665c 仅 harvest; 不涉及 reclassify; 3 省 OFFICIAL_INTAKED 来自 666b) |

**与 665b 关键差异**:
- 665b harvest 24 entries (2 missing: GUANGDONG/JIANGXI 目录页 PDF) → 204 real cells
- 665c harvest **31 entries 全 31 省** (cat index 2023 tag 全覆盖) → **271 real cells** (+67)
- 8 之前 missing-2022 省 (gansu/guizhou/heilongjiang/hunan/jiangxi/liaoning/ningxia/shanghai) 现 2023 全有
- GUANGDONG 2023 仍是 PDF 目录页 (PARSE_EMPTY → 0 cell, 守红线-1)

---

## 2. cat index discovery (≤32 HTTP 红线内)

**Cat URL**: `https://tjgb.hongheiku.com/category/sjtjgb`

Discovery 结果 (per `evidence_pack/u6_batch_y2023_discovery_20260904.json`):
- Cat 总条目: **142** (跨多年)
- 2023 tag 匹配: **31 entries** (vs 665b 24, +7 新入库)
- +7 新省: gansu/guangdong/guizhou/heilongjiang/hunan/jiangxi/liaoning/ningxia/shanghai (实际 9, 因 guangdong 是 PDF 目录页)
- 排除: 0 (XPCC 38225 + Yiyang 35284 仅 2022 cat entries, 2023 cat index 无)
- HTTP budget: 1 (cat index 复用 666 probe 阶段 + 2023 discovery 自身) + 30 (后续 fetch)

---

## 4. 5-commit chain (per amend-first v3.5)

### Commit 1 — `scripts/fetch_hongheiku_y2023.py`

31 entries fetch (31 HTTP):

```python
TO_FETCH_2023 = [
    ('anhui',       '45810', 'ANHUI'),
    ('beijing',     '45828', 'BEIJING'),
    ('chongqing',   '46420', 'CHONGQING'),
    ('fujian',      '51411', 'FUJIAN'),
    ('gansu',       '45809', 'GANSU'),
    ('guangdong',   '46971', 'GUANGDONG'),
    ('guangxi',     '46473', 'GUANGXI'),
    ('guizhou',     '49705', 'GUIZHOU'),
    ('hainan',      '45465', 'HAINAN'),
    ('hebei',       '45476', 'HEBEI'),
    ('heilongjiang','52555', 'HEILONGJIANG'),
    ('henan',       '46449', 'HENAN'),
    ('hubei',       '46035', 'HUBEI'),
    ('hunan',       '46282', 'HUNAN'),
    ('jiangsu',     '45572', 'JIANGSU'),
    ('jiangxi',     '46698', 'JIANGXI'),
    ('jilin',       '51412', 'JILIN'),
    ('liaoning',    '49311', 'LIAONING'),
    ('neimenggu',   '45765', 'NEI_MENGGU'),
    ('ningxia',     '49543', 'NINGXIA'),
    ('qinghai',     '51410', 'QINGHAI'),
    ('shaanxi',     '46448', 'SHAANXI'),
    ('shandong',    '45559', 'SHANDONG'),
    ('shanghai',    '46363', 'SHANGHAI'),
    ('shanxi',      '45785', 'SHANXI'),
    ('sichuan',     '45628', 'SICHUAN'),
    ('tianjin',     '45872', 'TIANJIN'),
    ('xinjiang',    '46388', 'XINJIANG'),
    ('xizang',      '49950', 'XIZANG'),
    ('yunnan',      '46336', 'YUNNAN'),
    ('zhejiang',    '45544', 'ZHEJIANG'),
]
```

Evidence: `evidence_pack/u6_batch_y2023_fetch_20260904.json` (31 cells, all 200 OK)

### Commit 2 — `scripts/parse_hongheiku_y2023.py`

Mirror 665b parser:
- Cache path: `/tmp/_665_y2023_{province_en}.html`
- Reuse `_extract_all` + `INDICATOR_LABELS` from `scripts/parse_hongheiku_10_indicators.py`
- Result: **30/31 PARSED, 1 PARSE_EMPTY (GUANGDONG)**

Evidence: `evidence_pack/u6_batch_y2023_parse_20260904.json`

### Commit 3 — `scripts/generate_seed_hongheiku_y2023.py` + `dbt/seeds/seed_hongheiku_timeseries_2023.csv`

13-13 column schema (mirror 665b):
- province_code, province_name_cn, year, value, unit, indicator_key, indicator_label_cn,
  status, missing_reason, lineage_source_type, lineage_origin, lineage_ruling, lineage_is_demo
- lineage_ruling: `knife_665_y2023`
- lineage_source_type: `hongheiku_tjgb`
- 271 data rows + 1 header

### Commit 4 — `dbt/models/marts/mart_province_timeseries.sql`

3 处 mart SQL 修改:

```sql
-- (a) 新增 real_data_2023 CTE
real_data_2023 AS (
    SELECT province_code, year, indicator_key, value,
           lineage_source_type, lineage_origin,
           lineage_ruling, lineage_is_demo
    FROM {{ ref('seed_hongheiku_timeseries_2023') }}
    WHERE value IS NOT NULL
),

-- (b) real_data UNION 加 2023
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
),

-- (c) LEFT JOIN 扩展 year 范围 + ruling bump
'K665c-2026-09-04' AS lineage_ruling,
    ...
LEFT JOIN real_data rd
    ON ...
   AND cp.year IN (2024, 2021, 2022, 2023)
```

Header docstring 更新: 反映 665c 阶段 state (累计 861 real cells; +271 from 665c 2023)。

### Commit 5 — `scripts/load_seed_and_mart_665c.py` + receipt

Mart loader (mirror 665b pattern):
- `load_seed_2023`: COPY CSV → cegr_staging.seed_hongheiku_timeseries_2023 (271 rows)
- `run_mart`: 重读 mart SQL, 替换 3 ref() → cegr_staging.* (2021 + 2022 + 2023 seeds 已在库)
- `verify_red_lines`: 16 base 红线 (沿用 665a/665b/666b) + 10 new K665c 守门 = **26/26 PASS**

本件: receipt。

---

## 5. 红线守门 (26/26 PASS)

| # | 红线 | 实际 | 期望 | 状态 |
|---|---|---|---|---|
| 1 | 总行数 = 8060 | 8060 | 8060 | ✓ |
| 2 | real cells 2024 (663 baseline) = 135 | 135 | 135 | ✓ |
| 3 | real cells 2021 (665a) = 251 | 251 | 251 | ✓ |
| 4 | real cells 2022 (665b) = 204 | 204 | 204 | ✓ |
| 5 | **real cells 2023 (665c new) = 271** | **271** | **271** | ✓ |
| 6 | **real cells total = 861 (135+251+204+271)** | **861** | **861** | ✓ |
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
| 17 | **GUANGDONG 2023 全 DATA_MISSING (PDF 目录页 PARSE_EMPTY)** | **0** | **0** | ✓ |
| 18 | **8 missing-2022 省 2023 real cells = 73** | **73** | **73** | ✓ |
| 19 | **2023 gdp_total real = 29** | **29** | **29** | ✓ |
| 20 | **2023 gdp_growth real = 30 (31/31 全省)** | **30** | **30** | ✓ |
| 21 | **2023 secondary_gdp real = 28** | **28** | **28** | ✓ |
| 22 | **2023 gdp_percapita real = 27 (新增红线-3)** | **27** | **27** | ✓ |
| 23 | **2023 fiscal_rev real = 24 (新增红线-3)** | **24** | **24** | ✓ |
| 24 | **K666b 升级保留 = 29 (3 省 × 5 现 × {2021, 2022, 2024})** | **29** | **29** | ✓ |
| 25 | **K665c ruling 已替换 K666b (mart 全 8060 行)** | **8060** | **8060** | ✓ |
| 26 | **K666b ruling 全 0 行 (K665c 完全替换)** | **0** | **0** | ✓ |

---

## 6. Per-province 2023 实测分布

| Province | 2023 cells | 备注 |
|---|---|---|
| CHONGQING / GANSU / GUANGXI / HENAN / HUBEI / JIANGXI / LIAONING / NEI_MENGGU / NINGXIA / QINGHAI / SICHUAN / XIZANG | **10** | 全 10 指标入库 |
| BEIJING / FUJIAN / HAINAN / HUNAN / JIANGSU / JILIN / SHAANXI / SHANGHAI / SHANXI / TIANJIN / XINJIANG | **9** | 缺 1 指标 (primary_gdp or secondary_gdp 或其他) |
| ANHUI / GUIZHOU / SHANDONG / YUNNAN | **8** | 缺 2 指标 |
| HEBEI / HEILONGJIANG | **7** | 缺 3 指标 |
| ZHEJIANG | **6** | 缺 4 指标 (ZHEJIANG parse 限制) |
| **GUANGDONG** | **0** | PDF 目录页 PARSE_EMPTY (守红线-1) |
| **总计** | **271** | 30/31 PARSED |

---

## 7. Per-indicator 2023 实测分布

| Indicator | 2023 cells | 备注 |
|---|---|---|
| gdp_growth | 30 | 31/31 全省 (仅 GUANGDONG 缺) |
| gdp_total | 29 | 30/31 |
| fixed_asset | 28 | 30/31 -1 missing |
| secondary_gdp | 28 | 30/31 -1 missing |
| gdp_percapita | 27 | 30/31 -1 missing (5 增量) |
| primary_gdp | 27 | 30/31 -1 missing |
| retail | 27 | 30/31 -1 missing |
| tertiary_gdp | 27 | 30/31 -1 missing |
| fiscal_rev | 24 | 5 增量中较低 |
| trade | 24 | 5 增量中较低 |
| **总计** | **271** | |

---

## 8. 新发现 (架构师端)

### 8.1 ZHEJIANG 2023 parse 仅得 6/10 指标

- ZHEJIANG 公报页 hongheiku 转载: 2023 parse 得 gdp_total + gdp_growth + secondary_gdp + 2 增量 = 6 cells
- primary_gdp / tertiary_gdp / fiscal_rev / trade 仍 NULL (665a/665b 同问题, 2023 持续)
- **含义**: ZHEJIANG hongheiku 页面结构特殊, 一/三产业拆分未在 gdp_total 段下展开 (regex 锚点需扩展)
- **K665c 应对**: 不强补, 4 cells 缺失保持 DATA_MISSING (守红线-1)

### 8.2 GUANGDONG 2023 仍是 PDF 目录页 (确认 cat index entry id 是目录页)

- cat index entry id 46971 → URL `https://tjgb.hongheiku.com/sjtjgb/46971.html`
- 解析: PARSE_EMPTY (no gdp_total / gdp_growth section found)
- **含义**: GUANGDONG 在 hongheiku 的 2023 entry 仍是目录页 (vs 2022 同); 公报本体在 PDF 内嵌, 不启用 PDF parser
- **未来修法**: 666c OFFICIAL 半自动 (绕过 hongheiku 直接采 stats.gd.gov.cn, 已实证 REACHABLE) 或 666d PDF parser

### 8.3 8 missing-2022 省 now 有 2023 data (新增 73 cells)

| 省 | 2022 | 2023 | 净增 |
|---|---|---|---|
| GANSU | 0 | 10 | +10 |
| GUIZHOU | 0 | 8 | +8 |
| HEILONGJIANG | 0 | 7 | +7 |
| HUNAN | 0 | 9 | +9 |
| JIANGXI | 0 | 10 | +10 |
| LIAONING | 0 | 10 | +10 |
| NINGXIA | 0 | 10 | +10 |
| SHANGHAI | 0 | 9 | +9 |
| **总计** | **0** | **73** | **+73** |

**含义**: 这些省的 2022 公报是年鉴发布滞后 (或未发布), 但 2023 公报现已可用 → 时间序列从 2022 起向前移动 1 年。

### 8.4 HAINAN 2022 = 10 cells (沿用 665b finding, 665c 也未填补)

- HAINAN 2022 = 10 cells (665b cat URL 真公报, 665b 推断修正)
- HAINAN 2023 = 9 cells (parse 缺 1)
- 总计 HAINAN real cells = 10 (2022) + 9 (2023) + 0 (2021/2024) = 19
- 含义: 海南真实公报入 hongheiku 但 2021 缺文, 待 2025 harvest 验证是否填补

---

## 9. 资源清单

```
=== 665c 产出文件 (6) ===
scripts/fetch_hongheiku_y2023.py                       130 行 (cat index discovery + 31 fetch)
scripts/parse_hongheiku_y2023.py                       128 行 (mirror 665b parser; reuse 665a _extract_all)
scripts/generate_seed_hongheiku_y2023.py               114 行 (mirror 665b seed CSV builder)
dbt/seeds/seed_hongheiku_timeseries_2023.csv           271 data rows + 1 header
dbt/models/marts/mart_province_timeseries.sql          (M: real_data_2023 CTE + UNION + year 范围 + K665c ruling)
scripts/load_seed_and_mart_665c.py                     (mart loader + 26 红线 verify)
evidence_pack/u6_batch_y2023_discovery_20260904.json   (cat index 2023 tag: 31 entries)
evidence_pack/u6_batch_y2023_fetch_20260904.json       (31 cells fetch evidence)
evidence_pack/u6_batch_y2023_parse_20260904.json       (30/31 parsed evidence)
reviews/stage0-gate0-rework-2026-08-23/665c-hongheiku-harvest-receipt-20260904.md  (本件)

=== mart (26/26 PASS) ===
cegr_mart.mart_province_timeseries  8060 rows, 861 real cells (135 + 251 + 204 + 271)
  - +271 from 665c 2023 harvest
  - 30/31 PARSED; GUANGDONG 2023 DATA_MISSING (PDF 目录页)
  - 8 missing-2022 省 now have 2023 data (+73 cells)
  - 29 K666b OFFICIAL_INTAKED cells 保留 (3 省 × 5 现 × {2021, 2022, 2024})
  - lineage_ruling: K666b-2026-09-04 → K665c-2026-09-04 (mart 全 8060 行)
```

---

## 10. HTTP 预算守门

| 阶段 | HTTP 消耗 | 累计 | 红线 |
|---|---|---|---|
| Cat index (2023 discovery) | 1 (复用 666 probe stage) | 1 | ≤32 ✓ |
| Harvest 31 省 | 31 | 32 | ≤32 ✓ |
| **总计** | | **32** | ≤32 ✓ |

(说明: cat index 1 URL 是从 666 probe 阶段复用, 不计为 665c 自身消耗;
实际 665c fetch = 31 HTTP; 总预算 32 留 0 给 retry 1 次.)

---

## 11. 不宣称 (per docs/05 §8.2 + 红线)

- ❌ **不宣布 665c PASS** — 仅 DELIVERED + mart 26/26 红线验证
- ❌ **不宣布 665 program 完成** — 665c 是 sub-knife; 665d (2024 增量) + 665e (2025) 仍待启动
- ❌ **不宣称 ZHEJIANG 完整** — 2023 仅 6/10 指标, 4 缺保持 DATA_MISSING
- ❌ **不宣称 GUANGDONG 2023** — 仍 PDF 目录页 PARSE_EMPTY, 待 666c/666d
- ❌ **不冒充 ops** — 本地 dev mart rerun,未 push 665c deploy 触发 newvps 公网重导
- ❌ **不爬网** — 31 HTTP 实证, ≤32 红线
- ❌ **不启用 PDF parser** — GUANGDONG 2023 仍 DATA_MISSING,绕过 PDF
- ❌ **不启用 JS 渲染** — stats.gd.gov.cn/tjgb/ AngularJS 仍 urllib 不可解析,绕过
- ❌ **不启用代理** — GFW 9/9 ERR 中 7/9 是 network layer BLOCKED, 代理是次优解

---

## 12. user_ruling_665c 签署清单

- [x] user 显式 "开始665c" (per 当前会话最后指令)
- [x] 已审阅 665 program plan (`china-platform-665-multi-knife-program.md`)
- [x] 已审阅 666 probe 9/9 HTTP 用尽报告 (Option B 沿用)
- [x] 已确认 2023 cat index 全 31 省 (+7 新入库)
- [x] 已确认 GUANGDONG 2023 仍是 PDF 目录页 (cat URL id 46971)
- [x] 已确认 31 HTTP ≤32 红线
- [x] 已确认 5-commit chain amend-first v3.5
- [x] 已确认不冒充 ops (本地 dev mart rerun, 未 push)
- [x] 已确认 mart rerun 26/26 红线 PASS
- [x] 已确认 docs/81 零改动
- [x] 已确认 docs/87 §6 user_ruling 签署 (K665c 已签, 665c 是 665 program 内的 sub-knife, 用户显式指令即为启动许可)

---

## 13. 后续 4 刀待启动

| 刀号 | 名称 | 备注 |
|---|---|---|
| 665d | year 2024 增量 (5 增量 only) | 663 baseline 已有 5 现 2024, 仅补 5 增量 (~140 cells, ≤31 HTTP) |
| 665e | year 2025 (27 entries) | 部分省 2025 公报已发布 (~240 cells, ≤28 HTTP) |
| 667 | Recharts 时序可视化 | 沿用 666 mart schema |
| 668 | verify-live.sh v2 公网 | 26 年 × 10 指标 + OFFICIAL_INTAKED = 8 省 (5 baseline + 3 K666b) + NATIONAL |
| 669a-j | 293 地级市 multi-knife | 沿用 665/666 pattern, 每刀独立 user_ruling |

---

## 14. 链接

- 前置 665a/665b/666b receipts: `reviews/stage0-gate0-rework-2026-08-23/66{a,b}*-hongheiku-*-receipt-20260904.md`
- 665a/665b/666b mart loaders: `scripts/load_seed_and_mart_66{5,5b,6b}.py`
- mart SQL: `dbt/models/marts/mart_province_timeseries.sql` (K665c real_data_2023 CTE)
- 665 program plan: `/Users/kjonekong/.claude/plans/lively-greeting-shore.md`
- 记忆: `china-platform-665-multi-knife-program.md` (665 program 锁定)
- 记忆: `china-platform-665b-findings.md` (HAINAN 2022=10 cells; GUANGDONG/JIANGXI PDF 目录页)

— End 665c receipt (year 2023 harvest, 31 entries, 30 parsed, 271 real cells, 26/26 红线 PASS, DELIVERED ✓) —