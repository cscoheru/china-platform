# Spike 02: Provincial Statistical Yearbook Extraction

**Status: PASSED (R3 已闭环)** — 测试 30/30 通过；R3-E per-indicator period metadata 已实施（`TestR3PeriodMetadata`：1-5月→CUMULATIVE_5MONTH / 月末→PERIOD_END_OF_MONTH 等）；R3-D tracked-ZIP-only 已在 `spikes/00-provincial-yearbook-table/` 实施（zip-slip 防护 + locate_0109_in_zip + clean-clone 缺 ZIP fail）。详细：`docs/12-stage0-closure-and-report.md` §3.2 + R3-D 返工指令。

## Province & Source

| Field | Value |
|---|---|
| Province | 湖北 (Hubei) |
| Province Code | 42 (GB/T 2260) |
| Source Agency | 湖北省统计局 (Hubei Provincial Bureau of Statistics) |
| Sample URL | https://tjj.hubei.gov.cn/tjsj/sjkscx/tjyb/2026yb/202608/P020260804600767306528.xlsx |
| File Type | Excel (.xlsx) |
| File Size | 11,261 bytes |
| File Hash (SHA256) | `c5cf5abeb4fdf97af52567f0640470d631bc9ac329dcc98f14e5d40bf6a5cac7` |
| Period | 2026-01 to 2026-06 (cumulative half-year) |
| Rows Extracted | 19 data rows |
| Test Result | **30/30 PASSED** |

## Extraction Approach

1. **Download**: `curl` fetches the .xlsx from Hubei stats bureau (direct public URL, no auth)
2. **Hash**: SHA-256 computed on raw bytes before any processing
3. **Parse**: `openpyxl` with `data_only=True` reads cell values; single sheet "Sheet1"
4. **Structure**:
   - Row 1: table title ("全省主要经济指标")
   - Row 2: column headers ("", "单位", "1-6月", "增速(%)")
   - Rows 3+: data rows (stop at footnote row starting with "注")
5. **Footnotes**: Inline footnote text captured from the bottom of the sheet

## Validation Results

```
30 passed
```

All tests pass:
- File integrity (hash matches raw bytes)
- JSON structure (province, code, period, source URL, agency, title, column headers)
- Data rows (>=3 rows, indicators, units for value-rows, GDP row present)
- Footnotes (footnote text present, GDP quarterly note captured)
- Provincial-vs-national schema diff (indicator_alias field present, sub-item prefix validated)

## Schema Differences vs. National Yearbook (PRD Doc 04 will use this)

These are the key findings that make Spike 02 valuable:

1. **Unit placement differs**: National yearbook tables use a separate unit-row above the column headers (e.g., a row where column B says "单位" and column C says "亿元"). Provincial monthly reports put units in a column (Col B = "单位") alongside the data — a column-oriented unit convention, not a row-oriented one.

2. **Rate-only rows have no unit**: The industrial value-added row ("规模以上工业增加值") has no explicit unit in column B — only a growth rate. This requires schema-level unit inference (the implied unit is percentage growth, implied by the column header "增速(%)"). National yearbook typically has units for all rows.

3. **Sub-item prefix convention**: Provincial format uses `#` prefix for sub-items (e.g., `#工业用电量`, `#民间投资`, `#进 口`). National yearbook uses indentation or sub-row convention. The extraction must strip the prefix for canonical naming while preserving it for source fidelity.

4. **Indicator naming embedded with period info**: Provincial indicator names embed the period ("上半年") directly in the indicator string ("一、地区生产总值(上半年)"). National yearbook uses period-agnostic names in the column headers, keeping indicator names clean.

5. **Footnotes carry non-obvious metadata**: The footnote "注：1.地区生产总值（GDP）、居民收入为季度数。" reveals that GDP and income figures are QUARTERLY data even though the table title says "1-6月". This is critical for time-series comparisons — the values appear to be H1 cumulative but are actually Q2 (quarterly) figures, not comparable to other half-year cumulative rows.

6. **No sheet/table numbering**: Provincial monthly reports are single-sheet Excel files without the chapter numbering (e.g., "E0201") used in the national yearbook. Table reference must come from URL or title.

7. **Value-only rows vs rate-only rows**: Some rows (e.g., industrial value-added) provide only growth rate, not absolute value. Others (e.g., GDP, retail sales) provide both. National yearbook typically provides absolute values for all rows in the same chapter table.

## Lessons Learned

- Hubei stats bureau is the most reliable public provincial source found — serves Excel .xlsx files directly without auth or CAPTCHA (tested Aug 2026)
- Jiangsu, Guangdong, Sichuan stats bureau sites block headless browsers (ERR_CONNECTION_RESET, ERR_EMPTY_RESPONSE) — must use `curl` for those provinces
- Provincial monthly reports are better samples than yearbook ZIPs for spike validation (smaller, direct Excel, no unpacking needed)
- Footnotes carry critical metadata not visible in the table structure — always capture the footnote text
- Unit inference is needed for rate-only rows — schema must allow `unit: null` for rows without explicit units

## Blockers

None. Sample was successfully downloaded and extracted.

## Files

```
spikes/02-provincial-yearbook/
├── extract_02_provincial_yearbook.py  # Extraction script
├── test_02_provincial_yearbook.py     # 30 unit tests (pytest)
├── README.md               # This file
├── hubei_2026_06.xlsx      # Raw file (11 KB, freely distributable)
data/extracts/02-provincial-yearbook/
└── extracted.json          # Extracted data (19 rows)
```

## Pipeline Libraries

- Python 3.14 (stdlib: `hashlib`, `json`, `pathlib`)
- `openpyxl` (Excel parsing, data_only mode)
- `pytest` (unit testing)
