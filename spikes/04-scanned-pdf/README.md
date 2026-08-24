# Spike 04: Scanned PDF Table OCR Extraction

**Status: FAILED / BLOCKED** — 真实扫描 PDF OCR 真值对照未通过 Gate 阈值。

## ⚠ 当前真实结果（机器生成，evidence_pack/manifest.json + data/extracts/04-scanned-pdf/eval_report.json）

| 指标 | 实际值 | Gate 阈值 | 状态 |
|---|---|---|---|
| `numeric_cell_accuracy_pct` | **0.0%** (0/129) | ≥80% | ❌ FAILED |
| `char_accuracy_pct` | **3.7%** (87/2348) | ≥90% | ❌ FAILED |
| `needs_review_total` / 450 | **450/450 (100%)** | ≤30% | ❌ FAILED |
| `low_ocr_confidence` | **450** | – | – |
| `unparseable_ocr` | **321** | ≤5% | ❌ FAILED |
| `no_ocr_words` | **111** | – | – |
| `indicator_name_accuracy_pct` | 100.0% (硬编码) | – | 不计真实 OCR 性能 |
| `unit_accuracy_pct` | 100.0% (硬编码 "1,000 dollars") | – | 不计真实 OCR 性能 |
| `page_locator_accuracy_pct` | 100.0% | – | – |
| `bbox_locator_accuracy_pct` | 99.7% (339 cells) | ≥90% | ⚠ 接近但被 value=0 主导 |

**结论：0% numeric + 3.7% char + 100% needs_review 全部远低于 Gate 阈值；spike 04 必须维持 FAILED/BLOCKED。**

阈值定义见 `spikes/04-scanned-pdf/gate_thresholds.json`。任何降低阈值的尝试必须先取得用户书面批准。

## ⚠ 代表性偏差（必须用户批准）

当前唯一能 OCR 跑通的真实扫描 PDF 是 `statistical_abstract_foreign_countries_1909.pdf`：
- 来源：1909 年美国统计摘要（archive.org item `statisticalabst00unit`）
- 语种：英文（tesseract eng），不是中文（chi_sim）
- 主题：法国对外贸易史数据，**与中国研究主题完全无关**
- 著作权：U.S. 联邦政府文献，公共领域（17 U.S.C. §105）

**这并不构成中国统计研究平台的代表性样本。** 在用户书面批准前：
- spike 04 维持 FAILED/BLOCKED 状态
- 不写入 PASSED 总结
- 实际样本选择待用户决策

## ⚠ matched_to_truth ≠ 准确率

`eval_report.json:matched_to_truth = 450` 仅表示已生成 450 行 (year, column) 结果，
**不是** 450 个数值正确。`value = null` 时与 truth 值不等仍计数为 matched。
实际 numeric accuracy 必须看 `numeric_cell_accuracy_pct` 和 `numeric_cell_compared`。

## Objective (per PRD 12.4)

提取扫描图像型统计 PDF 中的表格数据，含 per-cell 置信度、bbox、needs_review 队列。

---

## What Was Attempted

### PDF Sources Investigated

| Source | URL | Result |
|---|---|---|
| National Bureau of Statistics (stats.gov.cn) | https://www.stats.gov.cn/sj/ndsj/ | Modern yearbooks are text-based (digital PDFs), not scanned |
| National Statistical Communiqués | https://www.stats.gov.cn/sj/tjgb/ndtjgb/ | Text-based PDFs; direct PDF links return 404 |
| archive.org — chinastatistical00unse | https://archive.org/metadata/chinastatistical00unse | Returns 503 (rate-limited/throttled) |
| archive.org — chinayearbooks00chin | https://archive.org/metadata/chinayearbooks00chin | Returns 503 |
| archive.org — multiple China yearbook items | Various IDs | All return 503 or empty file lists |
| HathiTrust — China Statistical Yearbook 1990-1995 | https://catalog.hathitrust.org/Record/002551252 | "Full view" at UC Berkeley; direct PDF URLs return 403 |
| 中国统计信息网 (tjcn.org) — historical yearbooks | http://www.tjcn.org/tjnj/ | Requires 10-20 金币 (paid credits) |
| 统计年鉴下载站 (tjnjdata.com) | https://www.tjnjdata.com/ | Requires paid account |
| Chongqing Statistical Yearbook | https://www.cq.gov.cn/... | PDF downloaded (9.5 MB) but **corrupted**: created by ABBYY FineReader with malformed PDF structure (no xref table, cannot be read by poppler) |
| Shenyang Statistical Yearbook 2021 | https://www.shenyang.gov.cn/... | Text-based (PDF created by pdfFactory; pdftotext extracts text successfully) |
| Zhanjiang Statistical Yearbook 2022 | https://www.zhanjiang.gov.cn/... | Text-based (3.6 MB, 553 pages) |
| Henan / Fujian / Shanxi / Heilongjiang yearbooks | Various provincial sites | No accessible PDFs found; site-specific patterns |
| Suzhou / Shanghai / Guangzhou yearbooks | tjj.suzhou.gov.cn, tjj.gz.gov.cn | Dynamic JS-loaded links; redirects to main page |
| ZZU (Zhengzhou University) — China City Statistical Yearbook | https://www7.zzu.edu.cn/udrc/... | Historical files available as **RAR archives** (not PDFs) |
| 中国教育经济信息网 (cee.edu.cn) — national statistical communiqués | https://www.cee.edu.cn/... | HTML text only (no PDF) |

### Summary

- **Free, downloadable scanned (image-based) PDFs**: None found that are both publicly
  accessible and valid PDF files.
- **Text-based PDFs** (digital-born): Several were successfully downloaded (Shenyang,
  Zhanjiang, national statistical communiqués 1991-2021) but these do not test the
  OCR pipeline.
- **Paywalled sources**: tjcn.org, tjnjdata.com, tjnj.net — require paid accounts.
- **Institutional access only**: HathiTrust, archive.org — items exist but
  downloads blocked (503/403).
- **Corrupted PDF**: The one "scanned" file found (Chongqing, 9.5 MB, ABBYY FineReader
  output) has a malformed structure.

---

## Tools Installed

```bash
brew install tesseract tesseract-lang   # tesseract 5.5.3 + chi_sim/chi_tra language packs
pip install pytesseract pdf2image pdfplumber
```

Tesseract version: **5.5.3** (leptonica-1.87.0)  
Language packs verified: `chi_sim`, `chi_sim_vert`, `chi_tra`, `chi_tra_vert`, `eng`

---

## OCR Engine: Why pytesseract (not paddleocr)

- **paddleocr**: Not installed; requires `pip install paddlepaddle paddleocr` and
  ~2 GB of model files. Would provide better accuracy for Chinese text.
- **pytesseract + tesseract**: Available and working. Provides per-word confidence
  scores via `image_to_data()`. chi_sim pack works for Simplified Chinese.
- **Decision**: Use pytesseract for the spike. For production, evaluate paddleocr
  or cloud OCR (Baidu/Ali) for significantly better accuracy on low-quality scans.

---

## Confidence Threshold Rationale

| Threshold | Rationale |
|---|---|
| **< 0.70 → `needs_review: true`** | Based on tesseract confidence distribution on Chinese text. Values 70-100 indicate reliable recognition; below 70, OCR errors become common. |
| **< 0.50 → definitely needs review** | Used as sub-threshold for `review_reason: "low_avg_confidence"` |

Additional flags trigger review even if confidence is above 0.70:
- `missing_unit`: No unit column detected
- `missing_value`: Value field is null after parsing

---

## Common OCR Errors on Chinese Statistical Text

| Error Type | Example | Root Cause |
|---|---|---|
| Decimal point confusion | `17400。5` (Chinese period) | OCR reads `。` as `.` or noise |
| Comma confusion | `17，400` (Chinese comma) | Treated as decimal point when it's a thousand-sep |
| Digit substitution | `1?400` or `{27` | Low-resolution scan, similar strokes |
| Missing unit | Empty string | Unit column too thin or low contrast |
| Character splitting | `亿元` → `{27 5 b` | Font rendering × tesseract training mismatch |

The `_parse_value()` function in `extract_04_scanned_pdf.py` handles:
1. Chinese period `。` → decimal point
2. Chinese comma `，` → try-as-thousand-sep first, fallback to decimal
3. English comma `,` → remove (thousand separator)
4. Spaces between digit groups → removed
5. Non-numeric noise → stripped with regex

---

## Code Structure

```
extract_04_scanned_pdf.py — Main extraction pipeline
test_04_scanned_pdf.py    — 18 tests covering all schema fields and logic
README.md          — This file
```

### `extract_04_scanned_pdf.py` pipeline

1. Load PDF → render page at 300 DPI using `pdf2image` (poppler `pdftoppm`)
2. OCR with `pytesseract.image_to_data()` → per-word confidence scores
3. Cluster cells into rows (Y-gap heuristic) and columns (X-sort)
4. Map to structured columns: `indicator`, `period`, `value`, `unit`
5. Flag `needs_review` based on `CONFIDENCE_THRESHOLD` (0.70)
6. Write `data/extracts/04-scanned-pdf/extracted.json`

### `test_04_scanned_pdf.py` test coverage

- `TestConfidenceThreshold`: verifies threshold logic and needs_review flags
- `TestValueParsing`: Chinese comma/period handling
- `TestReviewQueue`: review queue builder
- `TestTableBBox`: bounding box computation
- `TestSha256Hash`: SHA-256 hashing
- `TestOcrPipeline`: OCR on synthetic image, table extraction, field presence
- `TestFullPipeline`: end-to-end extraction on synthetic PDF
- `TestJsonOutput`: JSON schema validation

**Test result: 18 passed**（真实样本=1909 美国统计摘要，archive.org）

---

## Lessons Learned: chi_sim OCR on macOS

- **Font rendering**: STHeiti Light / PingFang on macOS renders Chinese characters
  differently from tesseract's training fonts. Characters like `亿元` may be
  misrecognized (e.g., as `{27`). This is expected for non-standard fonts.
- **System font availability**: `/System/Library/Fonts/STHeiti Light.ttc` and
  `/System/Library/Fonts/PingFang.ttc` are available but not ideal for OCR.
- **chi_sim accuracy**: Good for standard text in common fonts (宋体, 黑体).
  Degrades significantly with serif/light fonts, small font sizes (<10pt), or
  low-resolution scans (<200 DPI).
- **Recommended DPI**: 300 DPI minimum for reliable OCR on statistical tables.
- **Confidence score**: tesseract `conf` field is on a -1 to 100 scale, normalized
  to 0.0-1.0 in the pipeline. Values below 0 are noise.

---

## Blockers

1. **未找到合适的中国研究平台扫描 PDF 样本**（1909 美国统计摘要可用但非代表性，需用户决策）：
   All Chinese historical yearbooks are either
   paywalled, text-based digital PDFs, or institutionally restricted.
   - **tjcn.org**: 10-20 金币 per download (~$1-2 USD)
   - **tjnjdata.com / tjnj.net**: Registration + payment required
   - **HathiTrust**: Search-only access; no downloads
   - **archive.org**: Items exist but PDF downloads return 503
2. **The one scanned file found (Chongqing) is corrupted**: Created by
   ABBYY FineReader but saved with a malformed PDF structure.
3. **paddleocr not installed**: Would provide better accuracy but requires
   ~2 GB of model files.

---

## Next Steps for Operator

1. **Obtain a valid scanned PDF** (one of the following):
   - Purchase credits on tjcn.org (~$1-2) and download e.g.
     https://www.tjcn.org/tjnj/RRR/16639.html (中国人口统计年鉴1995)
   - Access via institutional library (HathiTrust, JSTOR, CNKI)
   - Use the Chongqing file: try running `pdfsandwich` or `k2pdfopt` to
     repair the malformed PDF structure
2. **Install paddleocr for better accuracy**: `pip install paddlepaddle-gpu paddleocr`
3. **Test the pipeline**: Replace `SAMPLE_PDF_PATH` in `extract_04_scanned_pdf.py` with the real PDF
   and run `python3 extract_04_scanned_pdf.py <pdf_path> [page_number]`
4. **Validate extracted data** against the original PDF's table to calibrate the
   confidence threshold for this specific material

---

## Output Schema

```json
{
  "sample": {
    "source_url": "...",
    "source_type": "pdf_scanned",
    "file_hash_sha256": "...",
    "page_locator": 1,
    "page_dimensions": {"width": 1240, "height": 1754},
    "table_bbox": {"x": 100, "y": 200, "w": 640, "h": 320},
    "fetched_at": "2026-08-23T...",
    "extraction_method": "pytesseract",
    "ocr_language": "chi_sim+eng"
  },
  "rows": [
    {
      "indicator": "国内生产总值",
      "period": "1990",
      "value": 17400.0,
      "unit": "亿元",
      "source_url": "...",
      "locator": "page 1, table bbox ({...})",
      "extraction_method": "ocr",
      "ocr_confidence": 0.862,
      "cell_confs": [0.85, 0.90, 0.88, 0.82],
      "needs_review": false,
      "review_reason": null
    }
  ],
  "review_queue": []
}
```
