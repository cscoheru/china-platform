# Spike 1: 国家统计年鉴表 Extraction

## Sample

**Source**: 国家统计局 monthly economic data report
**URL**: https://www.stats.gov.cn/sj/zxfb/202608/t20260817_1965056.html
**Title**: "1—7月份国民经济保持总体平稳、向新向优发展态势" (National Economy Jan-Jul 2026)
**Type**: HTML table
**File**: `sample.html` (388 KB)
**SHA-256**: `dea13b8a4ff116ca91403b189cdd60705545b28200f9023c3d56e6db03f3939d`

**What the data contains**: Monthly macro-economic indicators for China (2026 Jan-Jul).
The table includes industrial增加值, services, fixed asset investment, real estate, and other
key indicators with year-on-year growth rates.

**Extracted scope**: 10 indicators x 2 periods (7月 / 1-7月 cumulative) = 20 observations.
Sample indicators: 规模以上工业增加值, 采矿业, 制造业, 电力/热力/燃气, 国有控股企业,
股份制企业, 外商及港澳台投资企业, 私营企业, 产品销售率, 出口交货值.

## Extraction Approach

**Library**: Python stdlib `re` (regex) — no external dependencies beyond Python 3.12+.
**Method**:
1. `compute_sha256()` — hash the raw HTML for provenance
2. `parse_html_table()` — regex-based table extraction (finds `<table>`, `<tr>`, `<td>` tags)
3. `extract_rows()` — maps header/sub-header structure to structured observations, filters
   section header rows, skips null/placeholder cells ("…"), extracts growth rate columns
4. `run_extraction()` — orchestrates pipeline and writes `data/extracts/01-nationalbook/extracted.json`

**Complexity**: Low. HTML tables are well-structured. The main challenge is mapping the two-row
header (指标 / 7月 / 1-7月 + 绝对量 / 同比增长 / 绝对量 / 同比增长) to clean column groups.

**Key gotchas**:
- Some cells contain "…" (suppressed data) — treated as `null` with `confidence: 0.0`
- Some values have "(百分点)" annotations — regex strips these before numeric parsing
- Section header rows (e.g., "分三大门类", "分经济类型") are skipped unless they have numeric data
- The indicator name column may contain Chinese full-width spaces (`　`) — normalized out

## Validation Results

```
python3 -m pytest spikes/01-national-yearbook/test_01_national_yearbook.py -v
============================== 20 passed ==============================
```

All tests pass:
- extracted.json exists and parses
- SHA-256 hash matches raw file
- >= 3 rows extracted (actual: 20)
- All rows have required fields (indicator, period, value, unit, source_url)
- Unit is non-empty for all rows
- Values are numeric or null
- Confidence is between 0.0 and 1.0
- Source URL is from stats.gov.cn
- Timestamps are ISO format

## Key Lessons

1. **stats.gov.cn structure**: The official yearbook (ndsj/) uses .jpg image scans for tables —
   not machine-readable. The monthly data release pages (zxfb/) use HTML tables, which are
   extractable. The monthly report pages are the more reliable programmatic target.

2. **Table header complexity**: Two-row headers require column group mapping (absolute vs growth
   rate). A single-row parser would misassign columns.

3. **Suppressed data**: "…" means the data is suppressed or not applicable — must be preserved
   as `null` with low confidence, not silently dropped.

4. **Section header rows**: Many rows in Chinese statistical tables are section dividers with
   no numeric values — need explicit filtering to avoid null-only observations.

5. **Period notation**: Chinese tables use "1—7月" with an em-dash. Need to normalize to
   `YYYY-MM~MM` format for machine processing.

6. **Data.stats.gov.cn API**: The API at data.stats.gov.cn returns 403 (WAF blocking). The
   HTML page scraping approach is the reliable fallback.

## Schema Decisions

- `period`: ISO-like `YYYY-MM` or `YYYY-01~MM` (not full ISO 8601 date) — readable and
  unambiguous for monthly/annual data
- `unit`: Preserved from source table header (e.g., "%", "亿元") — may need standardization later
- `confidence`: 0.95 for clean numeric extraction, 0.0 for suppressed ("…"), 0.3 for parse failure
- `table_locator`: XPath-like `table[1]/tr[N]/td[M]` — human-readable provenance for QA
- `value`: Always numeric (float) or null — never 0 for missing data

## Blockers

None for this spike.

**Known limitation**: The monthly report HTML page changes URL with each publication
(`/YYYYMM/tYYYYMMDD_XXXXX.html`). A production pipeline needs a list of known URLs or
a discovery crawler. The yearbook (ndsj/) Excel files are mostly image scans — true Excel
extraction requires a different source (e.g., provincial yearbook PDFs or the data API).

## Stage 1 Recommendations

1. Build a URL registry for monthly/quarterly/annual report pages by category
2. Invest in PDF extraction for yearbook chapters (use PyMuPDF/fitz)
3. For yearbook image tables, evaluate Tesseract OCR or cloud OCR (e.g., Alibaba OCR)
4. Standardize indicator names with a mapping table (CN <-> canonical name)
5. Consider the national data API as a secondary source once WAF behavior is understood
