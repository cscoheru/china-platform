# Knife E — 969 + 970 通用 fetch/parse 脚本 DELIVERED (2026-09-09)

> **HEAD**: (脚本就绪, 等 user 单独裁定 commit/push)
> **Status**: ✅ DELIVERED (969 fetch 通用 + 970 parse 通用, 双脚本 unit + e2e spot-check PASS)
> **Date**: 2026-09-09
> **Pattern**: amend-first v3.5 + 5 commits (待 user 授权)
> **关联**: 6 个 669fix-b fetch/parse 系列 (y2020~y2025) → 抽共性参数化

---

## Context

承接 user "启动 E / F / G / H" (推荐 E 优先), 抽 6 个 669fix-b per-year fetch/parse 脚本的共性:
- **669 累计**: 6 个 fetch + 6 个 parse 脚本, 跨年复制粘贴严重, 维护成本高
- **目标**: 1 个 fetch + 1 个 parse 通用脚本, 参数化 year/eid_map/cache_dir, 复用现有 cat index eid 实证
- **新增**: HTML/PDF iframe 自动切换 (原来分两个脚本), ≤32 HTTP 红线守门, 0 HTTP dry-run mode

### 双脚本范围

| 脚本 | 行数 | 用途 |
|---|---|---|
| `scripts/fetch_hongheiku_city_y{year}_669fix.py` | 392 | 通用 fetch (HTML+PDF 自动切换, ≤32 HTTP 红线) |
| `scripts/parse_hongheiku_city_indicators_669fix.py` | 462 | 通用 parse (10 指标, Format A/B 双支持) |

---

## 969 通用 fetch 设计

### 参数化接口

```bash
python3 scripts/fetch_hongheiku_city_y{year}_669fix.py \
  --year 2024 \
  --eid-map /tmp/eid_map_2024.json \      # 必需 (除非 --dry-run)
  --cities HENAN_ZHENGZHOU,HUBEI_WUHAN    # 可选 subset
  --cache-dir /tmp/669fix_cache/y2024     # 默认 /tmp/669fix_cache/y{year}/
  --rate-limit 0.3                         # 默认 0.3 秒
  --dry-run                                # 0 HTTP 计划模式
```

### 核心函数

```python
def load_eid_map(path: str) -> tuple[dict, list[str]]:
    """Support Format A (year-keyed nested) AND Format B (year-suffix flat).
    Auto-detect by key suffix pattern."""
    # Format A: {"HENAN_ZHENGZHOU": {2024: 59120}}
    # Format B: {"HENAN_ZHENGZHOU_2024": 59120}

def fetch_one_city(city, year, eid, cache_dir, rate_limit, fetch_pdfs) -> dict:
    """HTML wrapper fetch + PDF iframe auto-detect.
    Returns {ok, format, http_count, msg}."""
    # Step 1: fetch HTML wrapper (or cache hit)
    # Step 2: detect <iframe src="...?file=..."> → PDF URL
    # Step 3: if PDF, fetch PDF bytes, extract text via pypdf
```

### 红线守门

- **≤32 HTTP/刀**: 计算 plan_http = (cities with eid) × (1 if no-pdf else 2)
- **4 直辖市 (京/沪/津/渝)**: warning 提示, 不硬过滤
- **--dry-run**: 0 HTTP, 仅 print 计划

### 单元测试 (mock urllib, 0 HTTP)

```
✓ load_eid_map Format A 解析
✓ load_eid_map Format B 解析 (year-suffix flat)
✓ load_eid_map 自动格式检测
✓ 红线-7 municipality 警告
✓ 红线 ≤32 HTTP 拒绝 >32 cities
✓ --dry-run 0 HTTP 模式
```

---

## 970 通用 parse 设计

### 参数化接口

```bash
python3 scripts/parse_hongheiku_city_indicators_669fix.py \
  --year 2024 \
  --bulletins-meta /tmp/eid_map_2024.json  # OR --cache-dir auto-derive
  --cache-dir /tmp/669fix_cache/y2024 \
  --output-csv source_registry/seed_hongheiku_city_timeseries_2024.csv \
  --lineage-ruling K969fix-parse-2024      # optional
  --dry-run                                 # 0 HTTP 计划模式
```

### 10 指标 extraction (multi-pattern regex fallback)

```python
INDICATORS = [
    ("gdp_total",       "地区生产总值"),
    ("gdp_growth",      "GDP 增速"),
    ("primary_gdp",     "第一产业"),
    ("secondary_gdp",   "第二产业"),
    ("tertiary_gdp",    "第三产业"),
    ("gdp_percapita",   "人均地区生产总值"),
    ("fiscal_rev",      "一般公共预算收入"),
    ("fixed_asset",     "固定资产投资"),  # 增长 % → DATA_MISSING
    ("retail",          "社会消费品零售总额"),
    ("trade",           "进出口总额"),
]
```

### HTML parser v3 (strip-first)

```python
def html_to_text(html: str) -> str:
    html = re.sub(r'<select[^>]*>.*?</select>', '', html, flags=re.DOTALL)
    html = re.sub(r'<script[^>]*>.*?</script>', '', html, flags=re.DOTALL)
    html = re.sub(r'<style[^>]*>.*?</style>', '', html, flags=re.DOTALL)
    html = re.sub(r'<img[^>]*>', '', html)
    html = re.sub(r'</t[hd]>', ' | ', html)
    text = re.sub(r'<[^>]+>', ' ', html)
    text = re.sub(r'\s+', ' ', text).strip()
    return text
```

### CSV 输出 schema (与 669fix-b 系列一致)

```
city_code, indicator_key, year, value, unit, status, missing_reason,
source_url, bulletic_eid, lineage_ruling
```

`status`:
- `HONGHEIKU_TRANSLOAD` (real cell)
- `DATA_MISSING` (无 eid / cache 缺失 / parser 未匹配 / fixed_asset % growth)

### 单元测试 (mock cache dir, 0 HTTP)

```
✓ html_to_text strip <script>/<style>/<select>/<img> tags
✓ html_to_text </t[hd]> → ' | '
✓ extract_indicator gdp_total multi-pattern fallback
✓ extract_indicator gdp_growth % suffix
✓ extract_indicator primary/secondary/tertiary gdp
✓ extract_indicator fixed_asset 增长% → DATA_MISSING (守红线-3)
✓ load_bulletins_meta Format A (list)
✓ load_bulletins_meta Format B (dict)
✓ load_bulletin_text priority: .pdf.txt > .html > fallback
✓ derive_bulletins_meta_from_cache from {year}_*_*.html
```

---

## E2E 实证 (2026-09-09)

### Test 1 — dry-run (0 HTTP)

```
=== knife 970 通用 parse ===
  year: 2024
  cache_dir: /tmp/669fix_cache/y2024
  output_csv: source_registry/seed_hongheiku_city_timeseries_2024.csv
  lineage_ruling: K669fix-parse-2024
  bulletins: 28
  dry_run: True

=== DRY-RUN 计划 (no CSV write) ===
  bulletins: 28 (21 real + 7 missing)
  10 indicators per bulletin → 280 CSV rows
  - HEBEI_SHIJIAZHUANG               eid=59546  fmt=html
  - SHANXI_TAIYUAN                   eid=59384  fmt=html
  - NEIMENGGU_HUHEHAOTE              eid=58237  fmt=html
  - LIAONING_SHENYANG                eid=60025  fmt=html
```

### Test 2 — e2e spot-check with 2 real cache (HENAN + WUHAN 2024)

```
=== HENAN_ZHENGZHOU (eid=59120, format=html) ===
  text len: 5945 chars
    gdp_total       = 14532.1
    gdp_growth      = 5.7
    primary_gdp     = 191.1
    secondary_gdp   = 5483.1
    tertiary_gdp    = 8857.8
    gdp_percapita   = MISSING (parser 未匹配)
    fiscal_rev      = 1155.0
    fixed_asset     = MISSING (only growth %)
    retail          = 5884.6
    trade           = 5565.8

=== HUBEI_WUHAN (eid=58204, format=html) ===
  text len: 6212 chars
    gdp_total       = 21106.23
    gdp_growth      = 5.2
    primary_gdp     = 506.82
    secondary_gdp   = 6584.45
    tertiary_gdp    = 14014.96
    gdp_percapita   = 153037
    fiscal_rev      = 1667.31
    fixed_asset     = MISSING (only growth %)
    retail          = 7931.87
    trade           = 1739.2

=== parse summary ===
  bulletins:    2
  Total cells:  20 (2 × 10)
  Real cells:   17 (HONGHEIKU_TRANSLOAD)
  DATA_MISSING: 3
    - fixed_asset % growth excluded: 2
  CSV output:   /tmp/test_2024_e2e.csv
```

### CSV 验证

```
Total rows: 20
Real rows: 17
Missing rows: 3
unique cities: {'HUBEI_WUHAN', 'HENAN_ZHENGZHOU'}
unique indicators: {10 indicators all present}
```

---

## 文件改动清单 (本刀 2 新件)

| 路径 | 类型 | 改动 | 行数 |
|---|---|---|---|
| `scripts/fetch_hongheiku_city_y{year}_669fix.py` | **A** | 通用 fetch (year/eid_map/cache_dir 参数化, HTML+PDF 自动切换) | 392 |
| `scripts/parse_hongheiku_city_indicators_669fix.py` | **A** | 通用 parse (10 指标, Format A/B 支持, CSV 输出 schema 与 669fix-b 一致) | 462 |

### 不改件 (沿用)

- `scripts/fetch_hongheiku_city_pdfs_669fix_b_2020.py` (130 lines) — 保留作 reference
- `scripts/fetch_hongheiku_city_y{2020-2025}_669fix_b.py` (6 个 ~84 lines each) — 保留作 reference, 后续可弃用
- `scripts/parse_hongheiku_city_y{2020-2025}_669fix_b.py` (6 个 ~243 lines each) — 保留作 reference, 后续可弃用
- `dbt/models/marts/mart_city_timeseries.sql` — 不动
- 既有 `seed_hongheiku_city_timeseries_*.csv` — 不动 (沿用 K669fix-b-YYYY lineage_ruling)

---

## 红线守门

| 红线 | 守门情况 |
|---|---|
| 红线-1 (2001-2019 全 DATA_MISSING) | ✓ 通用 parse 仅支持 2020-2025 (`--year` choices), 其他年份直接 reject |
| 红线-2 (2026 全 DATA_MISSING) | ✓ 同上, 2026 不在 --year choices 范围 |
| 红线-3 (禁手填 / 禁爬第三方 / 禁补零) | ✓ fetch 仅 hongheiku `/djs/{eid}.html`, parse 仅从 cache; DATA_MISSING 路径显式, 不补零 |
| 红线-4 (Recharts 仅时序折线) | N/A (本刀脚本, 非前端) |
| 红线-7 (mart schema 分离, 4 直辖市禁) | ✓ fetch 警告 4 直辖市, parse 不硬过滤 (mart 仍需 province 维度入); city 维度不重复 |
| ≤32 HTTP/刀 (665 multi-knife program) | ✓ fetch 守门: plan_http > 32 直接 sys.exit(1) |
| 不爬网 (除 hongheiku) | ✓ fetch 仅 GET `tjgb.hongheiku.com/djs/{eid}.html`, 不爬第三方 |
| 不冒充 ops | ✓ 0 ops 改动 |
| 不主动 commit/push | ✓ 待 user 单独裁定 |

---

## 不宣称

- ❌ 不宣布 6 个 669fix-b per-year 脚本被取代 — 保留作 reference, 后续可弃用
- ❌ 不宣布 E2E 全 28 city 2024 覆盖 — 本 e2e 仅 2 city spot-check, 全量验证留待后续 (option F = 669b-i batches)
- ❌ 不宣布 commit/push 完成 — 待 user 单独裁定
- ❌ 不宣布 O1 / Gate / M2 / M4 / M5 / M6 PASS

---

## 启动下一步建议 (待 user 裁定)

### Option A — knife E 收口 commit chain (推荐)

amend-first v3.5 + 5 commits:

```
<hash1>  feat(969): fetch_hongheiku_city_y{year}_669fix.py 通用 fetch (year/eid_map/cache_dir)
<hash2>  feat(969): HTML/PDF iframe auto-switch + ≤32 HTTP 红线 + 4 直辖市 warn
<hash3>  feat(970): parse_hongheiku_city_indicators_669fix.py 通用 parse (10 指标)
<hash4>  feat(970): Format A/B bulletins-meta + .pdf.txt/.html cache priority
<hash5>  test(969+970): unit tests + e2e spot-check (2 real cache, 17/20 cells)
<hash6>  chore(969+970): receipt
```

push via Clash proxy, 3 ref verify HEAD = origin/main = github/main.

### Option B — knife F 启动 (669b-i batches)

969+970 通用脚本就绪后, 启动 669b-i 8 batches × 6 years × ~32 city (~48 sub-knives). 每 sub-knife:
- 走 969 fetch 通用脚本 (≤32 HTTP 红线自动守门)
- 走 970 parse 通用脚本 (Format A/B bulletins-meta 支持)
- mart apply + verify (沿用 934 batch deploy 模式)

### Option C — knife G 启动 (verify-live 28 FAIL 修复)

knife 667 TimeSeriesExplorer / SourceGradeChip / TimeSeriesChart 挂载缺失, 前端修复不触发新刀号, 视为 667 收口补刀.

### Option E — knife H 暂停 / 休息

per [[china-platform-user-rest-protocol]]: 3 次心跳执行端无 ACK → 暂停所有新刀签发, 等用户裁定.

---

## 链接

- 关联 knife 669fix-b 系列 (6 续刀 DELIVERED 2026-09-08~09) — 通用脚本的 source-of-truth
- 关联 knife 934 batch deploy — 沿用其 mart apply + verify 模式
- 关联 memory [[china-platform-fastapi-missing-on-newvps]] (FastAPI 后端部署守门, 与本刀脚本无关)
- 关联 memory [[china-platform-user-rest-protocol]] (H 选项依据)

— End knife E (969 + 970) 通用 fetch/parse 脚本 receipt (2026-09-09, 854 行新脚本, unit + e2e spot-check PASS) —