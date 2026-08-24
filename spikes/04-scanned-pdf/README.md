# Spike 04: Scanned PDF OCR

## Status

Spike 04 is a **non-gating research track** under the user ruling recorded in
`docs/15-stage0-p0p1-handoff-20260824.md` §4a (U-3). It does not determine the
Stage 0 verdict and must not be reported as an automatic PASS.

Two independent tracks are retained:

| Track | Sample | Purpose | Current result |
|---|---|---|---|
| Legacy numeric-table track | 1909 U.S. Statistical Abstract, page 24 | Preserve the original 30×15 table OCR regression and its arithmetic truth | 0.0% numeric / 3.7% digit characters / 100% needs review; failed historical research result |
| Shaanxi Chinese-text track | `data/shaanxi_fiscal_regulation_flk.pdf` | Chinese OCR pressure research under U-1/U-2 | 93.93% Han agreement / 90.05% all non-whitespace agreement / 25% pages need review; meets unchanged applicable research thresholds, with numeric N/A not counted as pass |

The 1909 sample is not representative of China and is not relabelled as such.
The Shaanxi regulation is a non-tabular legal text, so numeric-cell accuracy is
`null` / `not_applicable_non_tabular_source`; not applicable is not counted as
PASS.

## Unchanged thresholds

`gate_thresholds.json` remains unchanged:

- numeric-cell accuracy ≥80%
- character accuracy ≥90%
- needs-review rate ≤30%

For the Chinese-text track, Han ideographs are the primary target character
class, analogous to the digit-only target class in the legacy numeric-table
track. The all-non-whitespace metric is disclosed alongside it. A page enters
the Shaanxi research review queue when its Han agreement is below 90%. This is
a page-triage definition for this research track, not a redefinition of the
legacy numeric-cell parser's confidence/null/raw-parse review signal; only the
numeric threshold values remain unchanged.

## Shaanxi source and provenance

| Field | Verified value |
|---|---|
| Title | 陕西省财政预算管理条例 |
| Official source | 全国人大常委会国家法律法规数据库 |
| Direct URL | `https://wb.flk.npc.gov.cn/dfxfg/PDF/d31411b562fc4226a7465f1c875afe67.pdf` |
| Local origin evidence | macOS `kMDItemWhereFroms` recorded the exact official URL; Chrome quarantine metadata was present |
| PDF SHA-256 | `f34b2e57ae08620cb6a6afb98b3983d805d53e3bae78b969795987a7ebe71488` |
| Size / pages | 1,007,943 bytes / 4 pages |
| Scan evidence | Canon SC1011 / MP Navigator EX; one 1259×1669 grayscale JPEG image per page at 200 DPI |
| Embedded text | SHA-256 `cec93b67f8da16ecdd97b7e08ab2baf23995f2e61530afff3f1d6295dfdfc0bf`; 3,230 Han characters |

The user downloaded the official URL and uploaded the resulting file after
CC's verified-TLS request path failed. CC validates the file magic, structure,
origin metadata, size and hashes, but does **not** claim to have independently
observed HTTP 200.

The regulation text is covered by the legal-document exclusion in Article 5(1)
of the Copyright Law of the People's Republic of China. This is not a blanket
public-domain assertion for the database interface, scan layout or unrelated
portal assets. Full machine-readable provenance is in `provenance.json`.

The four-page scan begins with the end of a preceding regulation; the Shaanxi
fiscal-budget regulation starts on PDF page 1 and continues through page 4. The
accepted pressure sample is the complete four-page file.

## Reference limitation

Per U-2, the PDF's embedded text layer is the comparison reference. It is an
older OCR layer, not a human-corrected transcription. Its errors are preserved,
not silently corrected. Examples include:

- reference `预箅` versus new image OCR `预算`
- reference `人会` versus new image OCR `大会`
- reference `收攴` versus new image OCR `收支`
- reference `本行畋区域` versus new image OCR `本行政区域`

Consequently, the reported accuracy is **agreement with the accepted embedded
layer**, not accuracy against human-corrected ground truth. Correct new OCR can
be penalized where the accepted reference is wrong.

## Layout-aware evaluation

The image OCR never reads the embedded text layer. The two streams are built
independently:

1. `build_truth_shaanxi_flk.py` runs `pdftotext -bbox` and locks the accepted
   reference hash.
2. `extract_04_shaanxi_text.py` renders the page images at 300 DPI and runs
   Tesseract 5.5.3 with `chi_sim`, PSM 6, TSV output. The committed artifact
   pins `chi_sim.traineddata` SHA-256
   `a5fcb6f0db1e1d6d8522f39db4e848f05984669172e584e8d76b6b3141e1f730`.
3. Both streams estimate a per-page divider from visible word bounds after
   trimming the outer 5% of bbox edges. This handles scans whose printed
   content is not centered on the physical page.
4. Words crossing the divider are assigned by bbox center, and each page
   reports the crossing count and policy rather than silently hiding it.
5. Within left/right regions, words are clustered by Y coordinate and sorted
   by X coordinate.
6. `evaluate_04_shaanxi_text.py` computes Levenshtein distance independently in
   each region, then sums edits and denominators. Edits cannot cross columns.

This removes both fixed-midpoint cross-column concatenation and two-column
reading-order drift without using recognized character identity to align OCR,
or a character-bag comparison that would hide real insertions, deletions or
substitutions.

## Current Shaanxi result

Source: `data/extracts/04-scanned-pdf/shaanxi_text_eval_report.json`.

| Page | Han agreement | All non-whitespace | Needs review |
|---:|---:|---:|---|
| 1 | 89.40% | 83.45% | yes |
| 2 | 97.62% | 94.70% | no |
| 3 | 92.13% | 88.49% | no |
| 4 | 95.69% | 92.25% | no |
| **Overall** | **93.93%** | **90.05%** | **1/4 = 25%** |

Assessment:

- Han character threshold: met (93.93% ≥90%).
- Needs-review threshold: met (25% ≤30%).
- Numeric-cell threshold: not applicable and not counted as pass.
- Research result: `MEETS_UNCHANGED_APPLICABLE_THRESHOLDS`.
- Stage 0 effect: `none_per_U3_non_gating_research_sample`.
- Final Stage 0 verdict remains reserved for Cursor re-verification and user U-4.

## Files

```text
# Legacy numeric-table track
build_truth_p24.py
truth_p24.json
extract_04_scanned_pdf.py
evaluate_04.py
test_04_scanned_pdf.py
statistical_abstract_foreign_countries_1909.pdf

# Shaanxi Chinese-text research track
ocr_text_layout.py
build_truth_shaanxi_flk.py
truth_shaanxi_flk.json
extract_04_shaanxi_text.py
evaluate_04_shaanxi_text.py
test_04_shaanxi_text.py
data/shaanxi_fiscal_regulation_flk.pdf

# Shared policy/provenance
provenance.json
gate_thresholds.json
```

Generated Shaanxi outputs:

```text
data/extracts/04-scanned-pdf/shaanxi_text_ocr.json
data/extracts/04-scanned-pdf/shaanxi_text_eval_report.json
```

## Prerequisites, rebuild and test

Required executables are `pdftotext`, `pdfinfo`, `pdftoppm` (Poppler) and
Tesseract with `chi_sim`. The committed OCR artifact was produced with
Tesseract 5.5.3, Poppler 26.08.0 and the traineddata hash pinned above. Verify
the local toolchain before rebuilding:

```bash
command -v pdftotext pdfinfo pdftoppm tesseract
tesseract --version
tesseract --list-langs | grep '^chi_sim$'
python3 spikes/04-scanned-pdf/build_truth_shaanxi_flk.py --help
python3 spikes/04-scanned-pdf/extract_04_shaanxi_text.py --help
python3 spikes/04-scanned-pdf/evaluate_04_shaanxi_text.py --help
```

Use explicit temporary outputs for a non-mutating reproduction. The evaluator
must receive those same temporary truth and OCR files:

```bash
tmp="$(mktemp -d)"
trap 'rm -rf "$tmp"' EXIT

python3 spikes/04-scanned-pdf/build_truth_shaanxi_flk.py \
  --out "$tmp/truth.json"
python3 spikes/04-scanned-pdf/extract_04_shaanxi_text.py \
  --out "$tmp/extracted.json"
python3 spikes/04-scanned-pdf/evaluate_04_shaanxi_text.py \
  --truth "$tmp/truth.json" \
  --extracted "$tmp/extracted.json" \
  --out "$tmp/report.json"

python3 -m pytest -q -p no:cacheprovider \
  spikes/04-scanned-pdf/test_04_shaanxi_text.py
# 14 passed

python3 -m pytest -q -p no:cacheprovider \
  spikes/04-scanned-pdf/test_04_scanned_pdf.py
# 18 passed
```

Spike 04 therefore has 32 tests: 18 legacy + 14 Shaanxi. Missing source files,
missing Tesseract, missing language data and missing evaluator inputs fail
rather than skip. The tests also rebuild all three formal artifacts and compare
their bytes with committed outputs.

## Red lines retained

- Do not lower `gate_thresholds.json` to obtain a pass.
- Do not count `null`, skipped, blocked or field-only assertions as pass.
- Do not describe the 1909 U.S. sample as representative of China.
- Do not use the embedded layer as OCR input.
- Do not silently correct the accepted U-2 reference.
- Do not batch crawl, bypass TLS verification, bypass login/paywalls or use paid OCR.
- Do not infer a Stage 0 PASS from this non-gating research result.
