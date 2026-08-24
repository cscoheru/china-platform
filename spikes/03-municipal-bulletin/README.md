# Spike 03: 地级市统计公报 Extraction

**Status: PASSED (R3 已闭环)** — 提取可工作；R3-E per-indicator period metadata 已在 spike 02 落地：schema comparison_basis 已移除 Q2_ONLY（01-core.sql:94）；spike 02 per-indicator 周期已建模（TestR3PeriodMetadata）。详细：`docs/12-stage0-closure-and-report.md` §3.4 + R3-E 返工指令。

## Sample

| Field | Value |
|-------|-------|
| City | 深圳 (Shenzhen) |
| Year | 2024 |
| Bulletin title | 深圳市2024年国民经济和社会发展统计公报 |
| Source URL | https://www.sz.gov.cn/zfgb/2025/gb1374/content/post_12212437.html |
| Publisher | 深圳市统计局 + 国家统计局深圳调查队 |
| Published | 2025-05-22 (via government bulletin, issue 1374) |
| Format | HTML (single-page, sz.gov.cn) |
| File | `sample.html` — 62,831 bytes |
| SHA-256 | See `extracted.json` → `sample.file_hash_sha256` |

## Extraction approach

- **Parser**: BeautifulSoup (`lxml`) over `sample.html`
- **Locator**: `<div class="news_cont_d_wrap">` holds the full article body
- **Method**: Section-aware regex on prose paragraphs

The bulletin has **9 numbered sections** (一、综合 through 九、居民收入消费和社会保障),
each a block of prose text.  Statistics are embedded inline in sentences, not in HTML tables:

```
深圳地区生产总值36801.87亿元，比上年增长5.8%。
全市年末常住人口1798.95万人，比上年末增加19.94万人。
```

Regex patterns per indicator family match the leading number and trailing unit in the
same sentence, then the entire sentence is stored as `context_quote`.

## Format variability observed

This is the key signal for spikes 04 + 08 planning:

1. **PROSE not tables** — The sz.gov.cn bulletin renders all statistics as running text.
   No `<table>` elements appear in the article body. Extraction requires sentence-level
   regex, not table-cell scraping.

2. **Units inline** — Units like "亿元", "万人", "元", "%", "微克/立方米" appear
   immediately after the number in the same sentence, not in a separate column header.

3. **Section headings as locators** — Each paragraph group is anchored by a section title
   (e.g. "一、综合", "六、固定资产投资").  These serve as reliable `locator` values.

4. **Comparison basis embedded in verb** — "增长" = up, "下降" = down; "按可比价格计算"
   or "按当年价格计算" sometimes appear in the same sentence, sometimes are omitted.
   The `comparison_basis` field is set to `当年价格`/`可比价格` when explicitly stated,
   otherwise `None`.

5. **Chart placeholders break flow** — At section 七 (foreign trade) a chart placeholder
   ("图1  2020-2024年货物出口和进口总额") interrupts the prose. The paragraph text
   resumes after it — the chart itself is not extracted.

6. **Footnote / qualifier inline** — Sentences like "其中，常住户籍人口631.01万人，
   占常住人口比重35.1%" include sub-components in the same sentence. The regex captures
   the primary value (常住人口 total) but the sub-value is NOT a separate row.

7. **Variable sentence length** — `context_quote` can be 80–200 chars. Short quotes
   (<5 chars) indicate the regex failed to capture the full sentence; long quotes (>200)
   indicate over-capture. Both are tested (`test_context_quote_length_reasonable`).

8. **Format stability caveat** — This bulletin is published as a government gazette issue
   on sz.gov.cn, which uses a stable CMS template. Direct tjj.sz.gov.cn URLs may differ.
   Other cities may use PDFs (see spike 04) or different HTML table structures.

## Gotchas

- **comparison_basis sometimes absent**: For some indicators (e.g. fixed asset investment
  growth), no price basis is stated in the sentence. `comparison_basis` is `null`.
- **Chart images are not extracted**: The chart placeholder is a `<img>` tag referencing
  a CDN URL; its data is lost. The figure caption is in prose text and preserved.
- **Sub-components not auto-expanded**: "其中，第一产业…第二产业…第三产业…" in the GDP
  paragraph is one sentence containing three sub-values. The regex captures the primary
  GDP total only — sub-sector values need separate regex patterns.
- **Yearbook vs bulletin difference**: This bulletin is published in May of the following
  year (e.g. 2024 data published 2025-05-22). Yearbook data (spike 01/02) may differ
  from bulletin data for the same year due to revisions.
- **HTML boilerplate**: Navigation, header, and footer `<div>` elements appear in the
  HTML source before and after the article. The article container (`news_cont_d_wrap`)
  must be identified before text extraction to avoid noise.

## Extracted rows (8 total)

| # | Indicator | Value | Unit | Locator |
|---|-----------|-------|------|---------|
| 1 | 地区生产总值(GDP) | 36,801.87 | 亿元 | 一、综合 |
| 2 | 地区生产总值(GDP)增速 | 5.8 | % | 一、综合 |
| 3 | 常住人口 | 1,798.95 | 万人 | 一、综合 |
| 4 | 固定资产投资增速 | 2.4 | % | 六、固定资产投资 |
| 5 | 社会消费品零售总额 | 10,637.70 | 亿元 | 五、国内贸易 |
| 6 | 货物进出口总额 | 45,048.24 | 亿元 | 七、对外经济 |
| 7 | 人均地区生产总值 | 205,714 | 元 | 一、综合 |
| 8 | 地方一般公共预算收入 | 3,914.18 | 亿元 | 八、财政金融 |

## Lessons

- Municipal bulletins are **prose-first**, not table-first. Extractor must handle
  paragraph-level regex, not just `<table>` parsing.
- Section headings ("一、综合", etc.) are stable anchors across most Chinese municipal
  bulletins, but the **content format** (prose vs tables) varies by city and year.
- `context_quote` is critical for provenance — proves the number came from the text,
  not hallucinated. Length bounds (5–200) catch extraction failures.
- A single bulletin can yield 8+ clean statistics via regex if section structure is known.
- For scale: each city needs ~2 regex pattern sets (one for prose-heavy cities like 深圳,
  one for table-heavy cities). The PRD recommends building both pattern families.

## Blockers

None. The sample bulletin is publicly accessible, parses cleanly, and yields 8 statistics
with high confidence.

## Pipeline libraries

```
beautifulsoup4 4.14.3
lxml 6.0.2
pandas 2.3.3
httpx 0.28.1
pytest 9.0.2
```
