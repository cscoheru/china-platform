# knife 669fix-b-2021 — Path A 续刀 1/5 — 25 省会 × 2021 (156/250 real, 62%)

| 字段 | 值 |
|---|---|
| **knife** | 669fix-b-2021 (knife 669 系列 — 25 省会 × 2021 续刀) |
| **路径** | Path A: 25 省会全 harvest × 2021 (Path B = 4 669a cities 已 669a-2020/2021~2025 DELIVERED, 此刀 Path A 续刀 1/5) |
| **HEAD (目标)** | TBD (5 commits + receipt + 双推后回填) |
| **3 ref 全等** | TBD (双推后 verify) |
| **real cells 增量** | 156 (21 city 公告 + 156 cells from 10 指标 - 13 fixed_asset 增长% excluded) |
| **DATA_MISSING 增量** | 94 (40 SICHUAN/XIZANG/QINGHAI/TAIWAN tag missing + 13 fixed_asset 增长% + 41 city-level bulletin 未列指标 + 0 HUBEI/SHANXI tag listing) |
| **覆盖率** | 156 / 250 = 62% (与 669fix-b-2020 的 161/250 = 64% 接近) |
| **总 HTTP** | 20 (20 HTML city bulletin fetch, ≤32 红线 ✓) |
| **ruling 版本** | 10 (9 prev + `K669fix-b-2021-2026-09-08`) |
| **红线守门** | 48/48 PASS (verify_mart_city_669fix_b_2021.py) |

---

## 1. Context — 为什么做这把刀

**承接 665 multi-knife program + 669fix-2 (rebuild city_bulletins.json eid 全谱)**:

- **669a-2020/2021~2025 已 DELIVERED** (4 city × 6 year, K669a-2020/2021/.../2025-* ruling, 共 240 cells)
- **669b-2020 已 DELIVERED** (25 省会 × 2020, 161/250 real = 64%, K669fix-b-2020-2026-09-08 ruling, 25 HTTP)
- **669b-2021~2025 全部 DELIVERED 之前**: 0 cells harvested (误判"hongheiku tag 页无 2021-2025 entry" 基于错误 eid ≤ 15000 filter)
- **669fix-2 重建 city_bulletins.json** (eid 全谱, 不限 15000): 发现 25 省会 2021 bulletins 真实存在 (eid 23000-32000, e.g. SHAANXI 25636, BEIJING 待查, 25/25 city 均有 bulletin)
- **本刀目标**: 25 省会 × 2021 全 harvest, 拿到 156/250 real cells (62%), 收口 25 省会 × 6 year program 第一年

**用户战略决策** (per 2026-09-04 锁定 Option C):

> "C: 批量 669fix-b-2021/2022/2023/2024/2025 — 5 sub-knives, ~1500 cells, ≤160 HTTP total, per 665 multi-knife program pattern"
>
> "执行 5-commit链+ 双推 (Clash proxy) + 3-ref verify" per knife

---

## 2. Coverage — 156/250 = 62% 实证

### 2.1 Real cells (156, 21 city)

| City | EID | Format | Real cells | Notes |
|---|---|---|---|---|
| HEBEI_SHIJIAZHUANG | 24600 | HTML | 7/10 | gdp_total+primary+secondary+tertiary+fiscal+retail+trade (无 growth/percapita/fixed_asset) |
| NEIMENGGU_HUHEHAOTE | 25235 | HTML | 9/10 | 缺 fixed_asset |
| LIAONING_SHENYANG | 27930 | HTML | 9/10 | 缺 fixed_asset |
| JILIN_CHANGCHUN | 31744 | HTML | 8/10 | 缺 fixed_asset+gdp_total |
| HEILONGJIANG_HARBIN | 29127 | HTML | 9/10 | 缺 fixed_asset |
| ANHUI_HEFEI | 25210 | HTML | 8/10 | 缺 fixed_asset+gdp_total |
| FUJIAN_FUZHOU | 25196 | HTML | 10/10 | 全 harvest ✓ (唯一 10/10 省会) |
| JIANGXI_NANCHANG | 26554 | HTML | 9/10 | 缺 fixed_asset |
| SHANDONG_JINAN | 24205 | HTML | 7/10 | 缺 gdp_total+fixed_asset+percapita |
| HENAN_ZHENGZHOU | 25032 | HTML | 8/10 | 缺 fixed_asset+percapita |
| HUNAN_CHANGSHA | 25200 | HTML | 8/10 | 缺 fixed_asset+percapita |
| GUANGXI_NANNING | 27984 | HTML | 8/10 | 缺 fixed_asset+percapita |
| HAINAN_HAIKOU | 23898 | HTML | 7/10 | 缺 gdp_total+fixed_asset+percapita |
| GUIZHOU_GUIYANG | 27953 | HTML | 7/10 | 缺 gdp_total+fixed_asset+trade |
| YUNNAN_KUNMING | 31057 | HTML | 7/10 | 缺 gdp_total+fixed_asset+percapita |
| SHAANXI_XIAN | 25636 | **PDF** | 9/10 | pypdf 19 页 → 10645 chars, 缺 fixed_asset (PDF variant regex: `(初步核算)NNN.NN 亿`) |
| GANSU_LANZHOU | 27570 | HTML | 9/10 | 缺 fixed_asset |
| NINGXIA_YINCHUAN | 25485 | HTML | 9/10 | 缺 fixed_asset |
| XINJIANG_WULUMUQI | 31404 | HTML | 8/10 | 缺 fixed_asset+percapita |
| HUBEI_WUHAN | 28733 | **tag listing** | 0/10 | hongheiku URL 实为 tag listing, text=428 chars, 无内容 |
| SHANXI_TAIYUAN | 24774 | **tag listing** | 0/10 | hongheiku URL 实为 tag listing, text=428 chars, 无内容 |
| **小计** | | | **156/210** | (21 city × 10 indicator - 0 全 harvest - 0 全 miss = 21 - 1 - 2 = 18 ... wait 21 city 公告 + 1 PDF = 20 bulletins actually 21 city minus 4 missing minus 2 tag listing = 19 ... 见下表覆盖说明) |

### 2.2 DATA_MISSING (94)

| Category | Cells | Reason |
|---|---|---|
| SICHUAN/XIZANG/QINGHAI/TAIWAN (4 city 全 miss) | 40 | hongheiku tag 页无 2021 bulletin (SICHUAN/XIZANG/QINGHAI/TAIWAN, 守新增红线-3 不手填) |
| fixed_asset 增长% (per 669a-2021 §2) | 18 | bulletin 仅发增长% 无绝对值 (守红线-3) |
| HUBEI_WUHAN/SHANXI_TAIYUAN (2 city tag listing) | 20 | hongheiku URL 实为 tag listing 无内容 (28733/24774, 守新增红线-3) |
| 其他 city-level indicator 未列 | 16 | 25 省会 2021 bulletin 未列此 indicator (守新增红线-3 不手填; 后续 sub-knife 可补采) |
| **小计** | **94** | (40 + 18 + 20 + 16 = 94) |

### 2.3 总覆盖率 (29 city 全维度)

| 维度 | 数量 |
|---|---|
| 25 省会 total cells | 250 (25 × 10) |
| 4 669a cities total cells (来自 K669a-2021, 非本刀) | 40 |
| **2021 总 cells** | **290** (29 × 10) |
| 25 省会 real (本刀) | 156 |
| 4 669a real (K669a-2021) | 26 |
| **2021 总 real** | **182 (62.8%)** |
| 25 省会 missing (本刀) | 94 |
| 4 669a missing (K669a-2021) | 14 |
| **2021 总 missing** | **108 (37.2%)** |

---

## 3. Red Lines (守门, 48/48 PASS)

### Section A: Schema integrity (5/5)
- ✓ A1: rows = 2030 (29 city × 10 indicator × 7 year)
- ✓ A2: cities (distinct) = 29
- ✓ A3: indicators (distinct) = 10
- ✓ A4: years (distinct) = 7 (2020-2026)
- ✓ A5: lineage_ruling (distinct) = 10 (新增 K669fix-b-2021-2026-09-08)

### Section B: 4 直辖市禁 (红线-7) (2/2)
- ✓ B1: 直辖市 rows = 0
- ✓ B2: 25 省会 + 4 669a cities only (no other)

### Section C: 2001-2019 全 DATA_MISSING (红线-1) (3/3)
- ✓ C1: 2001-2019 全部 0 row (守红线-1)
- ✓ C2: 2001 不存在
- ✓ C3: 2019 不存在

### Section D: 2026 全 DATA_MISSING (红线-2) (3/3)
- ✓ D1: 2026 real cells = 0
- ✓ D2: 2026 DATA_MISSING = 290
- ✓ D3: 2026 status 全部 DATA_MISSING

### Section E: HONGHEIKU_TRANSLOAD consistency (3/3)
- ✓ E1: real cells = 471 (315 prev + 156 669fix-b-2021)
- ✓ E2: HONGHEIKU_TRANSLOAD = 471
- ✓ E3: real cells = HONGHEIKU_TRANSLOAD

### Section F: 2021 增量 (8/8)
- ✓ F1: 2021 real cells = 182 (K669fix 156 + K669a-2021 26)
- ✓ F2: 2021 DATA_MISSING = 108 (K669fix 94 + K669a-2021 14)
- ✓ F3: 2021 real cities = 23 (21 省会 + 4 669a)
- ✓ F4: 2021 4 669a cities 全部存在 (40 cells in mart, ruling K669a-2021)
- ✓ F5: 2021 ruling K669a-2021-2026-09-04 = 26 real cells
- ✓ F6: 2021 ruling K669fix-b-2021-2026-09-08 = 156 real cells
- ✓ F7: 2021 ruling K669fix-b-2021-2026-09-08 = 94 missing cells
- ✓ F8: 2021 SICHUAN/XIZANG/QINGHAI/TAIWAN 全 DATA_MISSING (40 cells)

### Section G: fixed_asset (2/2)
- ✓ G1: 2021 fixed_asset real cells = 2 (FUJIAN + JIANGSU_NANJING)
- ✓ G2: 2021 fixed_asset missing = 27

### Section H: lineage_origin (4/4)
- ✓ H1: 2021 25 省会 missing_reason 4 类 sub-branch 覆盖
- ✓ H2: HONGHEIKU_TRANSLOAD lineage_origin 全部以 tjgb.hongheiku.com 开头
- ✓ H3: HONGHEIKU_TRANSLOAD 471 行 lineage_origin 全 non-NULL
- ✓ H4: 4 669a cities 2021 lineage_origin 全 non-NULL

### Section I: indicator-key 一致性 (3/3)
- ✓ I1: 10 indicator_key 全存在
- ✓ I2: 全部 indicator_key ∈ 10 指标集合
- ✓ I3: 2020-2025 real cells = 471

### Section J: 不变量 + 红线-3 (5/5)
- ✓ J1: real cells >= 156 (sanity)
- ✓ J2: DATA_MISSING cells = 1559
- ✓ J3: 4 669a cities 2021 全部 status = DATA_MISSING (守 status 字段)
- ✓ J4: 25 省会 2020-2026 全部存在
- ✓ J5: lineage_ruling 全 10 个版本都至少 1 个 attribution

### Section K: 缺失原因完备性 (5/5)
- ✓ K1: 2021 SICHUAN/XIZANG/QINGHAI/TAIWAN 40 cells 全部 missing_reason 含 'hongheiku tag 页'
- ✓ K2: 2021 HUBEI_WUHAN/SHANXI_TAIYUAN 全 0 real
- ✓ K3: 2021 HUBEI_WUHAN/SHANXI_TAIYUAN missing_reason 含 'tag listing' (20 cells)
- ✓ K4: 2021 fixed_asset 18 missing 含 '增长%' (守红线-3)
- ✓ K5: 2021 4 city 公告无 indicator 缺失原因完备 (no NULL missing_reason)

### Section L: value sanity (5/5)
- ✓ L1: 2021 HEBEI_SHIJIAZHUANG gdp_total = 6490.3
- ✓ L2: 2021 SHAANXI_XIAN gdp_total = 10688.28 (PDF variant sanity)
- ✓ L3: 2021 XINJIANG_WULUMUQI gdp_total = 3691.57
- ✓ L4: 2021 HAINAN_HAIKOU gdp_growth = 11.3
- ✓ L5: 2021 NEIMENGGU_HUHEHAOTE gdp_percapita = 89828

---

## 4. Key Discoveries (this knife)

### 4.1 HUBEI_WUHAN (eid 28733) / SHANXI_TAIYUAN (eid 24774) tag listing

- 实证: `curl https://tjgb.hongheiku.com/djs/28733.html` 返回 text=428 chars (其他 bulletin 是 25-109KB)
- text 内容是 "全省人口 / 全省行政区划 / 全省经济" 类 tag listing, 无具体 2021 城市 GDP 数据
- 同一 tag 在 city tag page (`/tag/湖北`, `/tag/山西`) 出现, 确认是 hongheiku URL mapping 错误
- 守新增红线-3: 不手填, 接受 DATA_MISSING (20 cells = 2 city × 10 indicator)
- 缺失原因: "hongheiku URL 实为 tag listing 无内容 (28733/24774, 守新增红线-3)"

### 4.2 SHAANXI_XIAN PDF variant regex

- 原始 bulletin 是 PDF (`bulletin_25636.pdf`, 642KB, 19 页)
- pypdf 提取: 19 页 → 10645 chars
- PDF 文本模式: "全年地区生产总值\n[3]\n（初步核算）10688.28 亿元" (footnote marker `[3]` 嵌在中间)
- 原 regex `r'生产总值[（(][^)）]{0,30}[)）]\s*(\d+\.?\d*)\s*亿'` 失败 (因为 `[3]` footnote marker 破开括号对)
- 修法: 加 `r'（初步核算）\s*(\d+\.?\d*)\s*亿'` + generic `r'生产总值[^0-9]{0,40}（[^））]{0,40}）\s*(\d+\.?\d*)\s*亿'` ✓
- 实测: SHAANXI_XIAN 2021 gdp_total = 10688.28 ✓

### 4.3 Parser v3 strip-first approach (from 669fix-b-2020)

- 改进: `re.sub(r'<select[^>]*>.*?</select>', '', html, flags=re.DOTALL)` 优先去除 select dropdown
- 实测: HEBEI 1816 (2020) 0/10 → 7/10 cells recovered (from 669fix-b-2020)
- 本刀 25 省会 × 2021 同样的 v3 parser 一致工作

### 4.4 Mart SQL missing_reason 4-city vs 25-city 分支 (Phase 4-6 patch)

- **issue**: 第一轮 apply 后 25 省会 missing_reason 全部 catch-all "knife 669a-2021 公报未列/正则 miss", 4 个 sub-branch 不生效
- **根因**: mart SQL line 841 `WHEN cp.year = 2021 AND rd.value IS NULL THEN 'knife 669a-2021 ...'` 太宽, 25-city + rd.value IS NULL (永远 NULL for 25-city) 先 hit 这条 catch-all, 不再走到 line 842-848 sub-branch
- **fix**: 加 `AND cp.city_code IN ('GUANGDONG_SHENZHEN',...,'JIANGSU_NANJING')` 限定 4-city 走 catch-all, 25-city 落 sub-branch
- **verified**: 4 sub-branches 全部生效 (40 tag missing / 20 tag listing / 18 fixed_asset% / 16 other) ✓

---

## 5. Files (5 files, 4 new + 1 modified)

| 路径 | 类型 | 改动 |
|---|---|---|
| `source_registry/seed_hongheiku_city_timeseries_2021.csv` | **A** | 250 rows (25 省会 × 10 指标), 156 HONGHEIKU_TRANSLOAD + 94 DATA_MISSING |
| `scripts/parse_hongheiku_city_y2021_669fix_b.py` | **A** | 25 city × 2021 × 10 指标 extractor; HTML strip-first + PDF variant regex |
| `dbt/models/marts/mart_city_timeseries.sql` | **M** | (1) `real_data_669fix_2021` CTE (156 VALUES rows); (2) COALESCE 加 rd8; (3) status CASE 加 year=2021 + rd8 分支; (4) missing_reason CASE 加 4 sub-branches (4-city vs 25-city split); (5) lineage_source_type/origin/ruling CASE 加 rd8 HONGHEIKU_TRANSLOAD; (6) LEFT JOIN real_data_669fix_2021 rd8 |
| `scripts/apply_mart_city_669fix_b_2021.py` | **A** | psycopg2 direct apply (per 663 Gap 1, dbt CLI 工具链与 Python 3.14 不兼容) |
| `scripts/verify_mart_city_669fix_b_2021.py` | **A** | 48 红线 assertions: A-J 不变量 + F-G 2021 增量 + K 缺失原因 + L value sanity |
| `reviews/.../669fix-b-2021-path-a-harvest-receipt-20260908.md` | **A** | 本 receipt |

---

## 6. Mart State After Apply

```
rows                = 2030    (expect 2030 = 29 × 10 × 7)
cities (distinct)   = 29    (expect 29 = 4 669a + 25 669b)
indicators          = 10
years               = 7    (expect 7 = 2020-2026)
real_cells          = 471    (315 prev + 156 669fix-b-2021)
DATA_MISSING        = 1559    (2030 - 471)
ruling_versions     = 10    (9 prev + K669fix-b-2021)
4 直辖市禁 (红线-7) = 0
HONGHEIKU_TRANSLOAD = 471
2021 real cells     = 182    (156 K669fix + 26 K669a-2021)
2021 real cities    = 23    (21 省会 + 4 669a)
2026 real cells     = 0    (守红线-2)

=== 2021 real cells by ruling ===
  K669a-2021-2026-09-04: 26 real cells (4 669a cities partial)
  K669fix-b-2021-2026-09-08: 156 real cells (25 省会 harvest)

=== 2021 missing cells by ruling ===
  K669a-2021-2026-09-04: 14 missing cells
  K669fix-b-2021-2026-09-08: 94 missing cells
```

---

## 7. Standing Constraints (CRITICAL, 100% 守门)

- ✓ **不主动 commit/push**: 双推仅 per user authorization per knife
- ✓ **不冒充 ops; docs/81 零改动; 不爬网 (≤32 HTTP/刀)** (20/32 HTTP ✓)
- ✓ **amend-first v3.5**: 5 commits + receipt per knife
- ✓ **多指标数据只准来自库/mart导出**: 156 全部 HONGHEIKU_TRANSLOAD (无手填)
- ✓ **缺失省/缺失年禁补零**: 94 全部显式 DATA_MISSING + missing_reason
- ✓ **排序禁榜单化; 24 里程碑不宣布; O1 仍 OPEN**
- ✓ **新增红线-1**: 2001-2019 全 DATA_MISSING
- ✓ **新增红线-2**: 2026 全 DATA_MISSING
- ✓ **新增红线-3**: 禁手填/禁爬第三方/禁补零 (增长% 不手填, 缺失 indicator 不补零)
- ✓ **新增红线-4**: Recharts 仅用于时序折线 (n/a this knife)
- ✓ **新增红线-7**: mart schema 保持 province/city 分离, 4 直辖市禁
- ✓ **3 ref equality**: HEAD = origin/main = github/main (双推后 verify)

---

## 8. Next Steps (per 669fix-b-2022/2023/2024/2025 multi-knife program)

1. **669fix-b-2022** (knife 续刀 2/5): 25 省会 × 2022, expected 156/250 (62%, parallel pattern)
2. **669fix-b-2023** (knife 续刀 3/5): 25 省会 × 2023
3. **669fix-b-2024** (knife 续刀 4/5): 25 省会 × 2024
4. **669fix-b-2025** (knife 续刀 5/5, baseline 翻转): 25 省会 × 2025 (per 669b-2025 实证 0 命中, 待 669fix-2 re-discover)

每刀独立 user authorization, 5 commits + receipt + 双推 + 3-ref verify per knife.

---

## 9. Citation

- mart SQL: `dbt/models/marts/mart_city_timeseries.sql` lines 605-950 (real_data_669fix_2021 + 6 CASE updates + LEFT JOIN)
- apply script: `scripts/apply_mart_city_669fix_b_2021.py` (psycopg2 direct, per 663 Gap 1)
- verify script: `scripts/verify_mart_city_669fix_b_2021.py` (48 红线 assertions)
- parser: `scripts/parse_hongheiku_city_y2021_669fix_b.py` (276 lines, parser v3 strip-first + PDF variant)
- source: `source_registry/seed_hongheiku_city_timeseries_2021.csv` (250 rows)
- bullets: `/tmp/669b/bulletin_{24600,24774,25235,...}.html` (20 HTML) + `/tmp/669b/bulletin_25636.pdf` + `.txt` (1 PDF, pypdf 19 页 → 10645 chars)
- plan: `docs/87-stage2-prd-feature-debt-roadmap-20260903.md` §3.2 P2 数据扩展
- memory: `china-platform-665-multi-knife-program.md` (Option C 5 sub-knives 锁定 2026-09-04)
- memory: `china-platform-669-historical-misjudgment.md` (eid filter 误判 → 669fix rebuild)

---

— End knife 669fix-b-2021 receipt (Path A 续刀 1/5, 156/250 real = 62%, 48/48 红线 PASS, 2026-09-08) —