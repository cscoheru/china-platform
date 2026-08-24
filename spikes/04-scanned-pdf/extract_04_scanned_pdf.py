#!/usr/bin/env python3
"""Spike 04 — real scanned-PDF extraction pipeline.

Sample: Statistical Abstract of Foreign Countries (1909), archive.org item
`statisticalabst00unit`, PDF page 24 (printed page 20): FRANCE foreign
commerce table, 30 rows (1843-1872) x 15 numeric columns + YEAR label.
Public domain (17 U.S.C. 105). See provenance.json.

Pipeline (all steps actually executed on the real PDF):
  1. verify file hash against provenance.json
  2. pdfinfo page count
  3. render target page at --dpi (pdftoppm)
  4. orientation detection (tesseract OSD) + rotation
  5. table geometry derived from the page pixels:
       - row bands from full-width horizontal ink profile peaks
       - column windows from vertical rule lines (long dark runs)
  6. per-cell OCR (tesseract psm 7, digit whitelist) -> value/sign/conf
  7. arithmetic identity QC (excess = exports - imports; gs = gold + silver)
  8. write observations to <repo>/data/extracts/04-scanned-pdf/extracted.json

Notes
-----
* All temp files go through tempfile.TemporaryDirectory() (never a literal
  /tmp path — macOS sandbox breaks tesseract there).
* Missing PDF, missing tesseract, or failed steps are FATAL (exit != 0);
  this spike must not silently skip and claim success.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

import numpy as np
from PIL import Image

HERE = Path(__file__).parent
REPO = HERE.parent.parent
DEFAULT_PDF = HERE / "statistical_abstract_foreign_countries_1909.pdf"
PROVENANCE = HERE / "provenance.json"
DEFAULT_OUT = REPO / "data" / "extracts" / "04-scanned-pdf" / "extracted.json"

TARGET_PAGE = 24  # 1-indexed PDF page
INK_THRESHOLD = 150  # gray level below which a pixel counts as ink

# Document table semantics (transcribed from the printed header; geometry is
# NOT taken from here — x/y positions are detected from the rendered page).
COLUMN_SEMANTICS = [
    ("gt_imports", "Merchandise", "General trade", "Imports"),
    ("gt_exports", "Merchandise", "General trade", "Exports"),
    ("gt_excess", "Merchandise", "General trade", "Excess of imports (-) or exports (+)"),
    ("st_imports", "Merchandise", "Special trade", "Imports"),
    ("st_exports", "Merchandise", "Special trade", "Exports"),
    ("st_excess", "Merchandise", "Special trade", "Excess of imports (-) or exports (+)"),
    ("gold_imports", "Precious metals", "Gold", "Imports"),
    ("gold_exports", "Precious metals", "Gold", "Exports"),
    ("gold_excess", "Precious metals", "Gold", "Excess of imports (-) or exports (+)"),
    ("silver_imports", "Precious metals", "Silver", "Imports"),
    ("silver_exports", "Precious metals", "Silver", "Exports"),
    ("silver_excess", "Precious metals", "Silver", "Excess of imports (-) or exports (+)"),
    ("gs_imports", "Precious metals", "Gold and silver", "Imports"),
    ("gs_exports", "Precious metals", "Gold and silver", "Exports"),
    ("gs_excess", "Precious metals", "Gold and silver", "Excess of imports (-) or exports (+)"),
]
UNIT = "1,000 dollars"


def die(msg: str) -> None:
    print(f"FATAL: {msg}", file=sys.stderr)
    sys.exit(1)


def require_tools() -> None:
    for tool in ("tesseract", "pdftoppm", "pdfinfo"):
        if shutil.which(tool) is None:
            die(f"required tool not found on PATH: {tool}")


def sha256_of(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


# ---------------------------------------------------------------- pipeline

def verify_source(pdf: Path) -> dict:
    prov = json.loads(PROVENANCE.read_text(encoding="utf-8"))
    if not pdf.exists():
        die(f"scanned PDF not found: {pdf}")
    actual = sha256_of(pdf)
    if actual != prov["file_hash_sha256"]:
        die(f"sha256 mismatch for {pdf}: expected {prov['file_hash_sha256']}, got {actual}")
    return prov


def pdf_page_count(pdf: Path) -> int:
    out = subprocess.run(["pdfinfo", str(pdf)], capture_output=True, text=True, check=True)
    m = re.search(r"^Pages:\s+(\d+)$", out.stdout, re.M)
    if not m:
        die("pdfinfo: could not parse page count")
    return int(m.group(1))


def render_page(pdf: Path, page: int, dpi: int, workdir: Path) -> Path:
    out_prefix = workdir / "page"
    subprocess.run(
        ["pdftoppm", "-f", str(page), "-l", str(page), "-r", str(dpi), "-gray",
         "-png", str(pdf), str(out_prefix)],
        check=True, capture_output=True,
    )
    rendered = sorted(workdir.glob("page-*.png"))
    if not rendered:
        die(f"pdftoppm produced no output for page {page}")
    return rendered[0]


def detect_rotation(img: Image.Image, workdir: Path) -> int:
    """Return OSD-reported rotation (degrees CW) needed to make text upright."""
    tmp = workdir / "osd.png"
    img.save(tmp)
    out = subprocess.run(
        ["tesseract", str(tmp), "stdout", "--psm", "0"],
        capture_output=True, text=True,
    )
    m = re.search(r"Rotate:\s+(\d+)", out.stdout)
    if not m:
        die(f"tesseract OSD failed to report rotation (stdout={out.stdout!r} stderr={out.stderr!r})")
    return int(m.group(1))


def ocr_cell(img_arr: np.ndarray, y0: int, y1: int, x0: int, x1: int,
             workdir: Path, whitelist: str) -> tuple[str, float, list[dict]]:
    """OCR one cell crop with tesseract psm 7. Returns (text, conf, word_bboxes).

    Bbox coords are returned in ORIGINAL page pixels (the uniform 2x upscale
    for OCR is divided back out).
    """
    crop = img_arr[y0:y1, x0:x1]
    # mild preprocessing: contrast stretch + 2x upscale (documented, uniform)
    lo, hi = np.percentile(crop, [2, 98])
    crop = np.clip((crop.astype(np.float32) - lo) * 255.0 / max(1.0, hi - lo), 0, 255).astype(np.uint8)
    pil = Image.fromarray(crop)
    pil = pil.resize((pil.width * 2, pil.height * 2), Image.LANCZOS)
    tmp_in = workdir / "cell.png"
    pil.save(tmp_in)
    out = subprocess.run(
        ["tesseract", str(tmp_in), "stdout", "--psm", "7", "-c",
         f"tessedit_char_whitelist={whitelist}", "tsv"],
        capture_output=True, text=True,
    )
    words, confs = [], []
    boxes = []
    for line in out.stdout.splitlines()[1:]:
        parts = line.split("\t")
        if len(parts) < 12 or not parts[11].strip():
            continue
        conf = float(parts[10])
        if conf < 0:
            continue
        words.append(parts[11].strip())
        confs.append(conf)
        # bbox in preprocessed crop coords -> original page coords
        l, t, w, h = int(parts[6]), int(parts[7]), int(parts[8]), int(parts[9])
        boxes.append({"x": x0 + l // 2, "y": y0 + t // 2, "w": w // 2, "h": h // 2,
                      "text": parts[11].strip(), "conf": conf})
    text = " ".join(words)
    conf = min(confs) if confs else 0.0
    return text, round(conf, 1), boxes


def parse_number(text: str) -> tuple[int | None, str | None]:
    """Parse OCR text like '- 46,500' / '+7,900' / '1,000' -> (value, reason)."""
    cleaned = text.replace("—", "-").replace("–", "-").replace(" ", "")
    m = re.fullmatch(r"([+-]?)([\d,\.]+)", cleaned)
    if not m or not re.search(r"\d", cleaned):
        return None, "unparseable_ocr"
    sign = -1 if m.group(1) == "-" else 1
    digits = m.group(2).replace(",", "").replace(".", "")
    if not digits.isdigit():
        return None, "unparseable_ocr"
    return sign * int(digits), None


# ------------------------------------------------------- geometry detection

def find_rules(mask: np.ndarray, y0: int, y1: int) -> list[int]:
    """Vertical rule x positions, compensated for in-page scan skew.

    The scan is rotated ~1 deg in-plane, so a rule drifts several px in x
    across the table height and no single x stays dark for the full extent.
    For a set of candidate slopes we accumulate column ink ALONG the tilted
    path; a rule then scores ~table height while text columns score ~30%.
    Returns cluster centers of x positions scoring above threshold.
    """
    yc = (y0 + y1) / 2.0
    rows = range(y0, y1, 4)  # sample every 4th row
    n_samples = len(list(rows))
    best = np.zeros(mask.shape[1], dtype=float)
    for slope in (-0.04, -0.03, -0.02, -0.01, -0.005, 0.0, 0.005, 0.01, 0.02, 0.03, 0.04):
        acc = np.zeros(mask.shape[1], dtype=float)
        for y in range(y0, y1, 4):
            shift = int(round(slope * (y - yc)))
            row = mask[y]
            acc += np.roll(row, shift)
        best = np.maximum(best, acc)
    thresh = 0.6 * n_samples
    scores = best
    rules: list[int] = []
    cluster: list[tuple[int, float]] = []
    for x in range(len(scores)):
        if scores[x] >= thresh:
            cluster.append((x, scores[x]))
        elif cluster:
            rules.append(_center(cluster))
            cluster = []
    if cluster:
        rules.append(_center(cluster))
    # second pass: the table's outermost rule can be faint (page-edge curl on
    # IA scans). If the rightmost strong rule has any weaker rule-like score
    # (>= 0.35 * samples) within 250 px to its right, adopt that cluster.
    if rules:
        weak_thresh = 0.35 * n_samples
        x_search = rules[-1] + 10
        x_end = min(len(scores), rules[-1] + 260)
        seg = scores[x_search:x_end]
        if len(seg) and seg.max() >= weak_thresh:
            xs = x_search + np.where(seg >= weak_thresh)[0]
            rules.append(int(xs.mean()))
    # merge centers closer than 10 px
    merged: list[int] = []
    for x in sorted(rules):
        if merged and x - merged[-1] < 10:
            merged[-1] = x
        else:
            merged.append(x)
    return merged


def _center(cluster: list[tuple[int, float]]) -> int:
    return int(round(sum(a * b for a, b in cluster) / sum(b for _, b in cluster)))


def detect_row_bands(mask: np.ndarray, year_x0: int, year_x1: int,
                     expected_rows: int) -> list[tuple[int, int]]:
    """Row bands from the YEAR-column ink profile.

    The scan is slightly skewed, so a full-width profile smears adjacent text
    lines together; the year label column gives clean per-row peaks. The
    table block is the longest run of peaks with pitch in [18, 32] px.
    """
    prof = mask[:, year_x0:year_x1].sum(axis=1).astype(float)
    # smooth, then local maxima
    k = np.ones(5) / 5.0
    sm = np.convolve(prof, k, mode="same")
    thresh = np.median(sm[sm > 0]) + sm.max() * 0.08
    peaks = [y for y in range(2, len(sm) - 2)
             if sm[y] >= thresh and sm[y] >= sm[y - 1] and sm[y] >= sm[y + 1]
             and sm[y] > sm[y - 2] and sm[y] > sm[y + 2]]
    # enforce min separation 15 px (keep taller)
    sep: list[int] = []
    for y in peaks:
        if sep and y - sep[-1] < 15:
            if sm[y] > sm[sep[-1]]:
                sep[-1] = y
        else:
            sep.append(y)
    # longest run with pitch in [18, 32]
    best_run, run = [], [sep[0]] if sep else []
    for a, b in zip(sep, sep[1:]):
        if 18 <= b - a <= 32:
            run.append(b)
        else:
            best_run = max(best_run, run, key=len)
            run = [b]
    best_run = max(best_run, run, key=len)
    if len(best_run) < expected_rows:
        die(f"row detection found {len(best_run)} year-column peaks "
            f"(from {len(sep)} candidates), expected {expected_rows}")
    table = best_run[:expected_rows] if len(best_run) == expected_rows else \
        sorted(best_run, key=lambda y: -sm[y])[:expected_rows]
    table = sorted(table)
    return [(y - 11, y + 2) for y in table]


def detect_table_extent(mask: np.ndarray) -> tuple[int, int]:
    """Table y-extent: longest contiguous run of above-median row ink density."""
    prof = mask.sum(axis=1).astype(float)
    med = np.median(prof)
    dense = prof > med * 1.5
    runs: list[tuple[int, int]] = []
    start, gap = None, 0
    for y in range(len(dense)):
        if dense[y]:
            if start is None:
                start = y
            gap = 0
        elif start is not None:
            gap += 1
            if gap > 20:
                runs.append((start, y - gap))
                start, gap = None, 0
    if start is not None:
        runs.append((start, len(dense) - 1 - gap))
    if not runs:
        die("table extent detection: no dense row run found")
    y0, y1 = max(runs, key=lambda r: r[1] - r[0])
    return y0, y1


def detect_column_windows(mask: np.ndarray, y_top: int, y_bottom: int,
                          n_columns: int) -> tuple[tuple[int, int], list[tuple[int, int]]]:
    """Vertical table rules -> (year_window, column_windows).

    Expects 17 rules: year column delimited by the first two, then 15 numeric
    columns by the remaining 16.
    """
    rules = find_rules(mask, y_top, y_bottom)
    if len(rules) < n_columns + 2:
        die(f"rule detection found {len(rules)} rules, need {n_columns + 2}")
    numeric = rules[-(n_columns + 1):]
    left_year_rule = rules[-(n_columns + 2)]
    year_window = (left_year_rule + 4, numeric[0] - 4)
    windows = [(numeric[i] + 2, numeric[i + 1] - 2) for i in range(n_columns)]
    return year_window, windows


# ------------------------------------------------------------------- main

def extract(pdf: Path, out_path: Path, dpi: int) -> dict:
    require_tools()
    prov = verify_source(pdf)
    pages = pdf_page_count(pdf)
    if not (1 <= TARGET_PAGE <= pages):
        die(f"target page {TARGET_PAGE} outside page count {pages}")

    with tempfile.TemporaryDirectory(prefix="spike04_") as td:
        workdir = Path(td)
        rendered = render_page(pdf, TARGET_PAGE, dpi, workdir)
        img = Image.open(rendered)
        rot = detect_rotation(img, workdir)
        if rot:
            img = img.rotate(-rot, expand=True)  # PIL rotates CCW; OSD angle is CW
        arr = np.array(img.convert("L"))
        H, W = arr.shape
        mask = arr < INK_THRESHOLD

        # stage 1: table y-extent from row ink density
        yA, yB = detect_table_extent(mask)
        # stage 2: rules within the table extent -> year window + column windows
        year_window, col_windows = detect_column_windows(mask, yA, yB, 15)
        # stage 3: year-column peaks -> row bands
        row_bands = detect_row_bands(mask, year_window[0], year_window[1],
                                     expected_rows=30)

        rows_out = []
        for r_idx, (by0, by1) in enumerate(row_bands):
            year_text, year_conf, _ = ocr_cell(
                arr, max(0, by0), min(H - 1, by1 + 2),
                year_window[0], year_window[1], workdir, whitelist="0123456789")
            year = int(year_text) if re.fullmatch(r"\d{4}", year_text) else None

            for c_idx, ((cx0, cx1), (key, l1, l2, leaf)) in enumerate(
                    zip(col_windows, COLUMN_SEMANTICS)):
                text, conf, boxes = ocr_cell(
                    arr, by0, by1 + 1, cx0, cx1, workdir,
                    whitelist="0123456789,.+-")
                value, reason = parse_number(text)
                obs = {
                    "row_index": r_idx,
                    "year": year,
                    "year_ocr_conf": year_conf if year else 0.0,
                    "indicator": f"FRANCE foreign commerce / {l1} / {l2} / {leaf}",
                    "column_key": key,
                    "group_l1": l1,
                    "group_l2": l2,
                    "leaf": leaf,
                    "period": f"{year}-12-31" if year else None,
                    "value": value,
                    "raw_ocr": text,
                    "unit": UNIT,
                    "source_url": prov["source_url"],
                    "file_hash_sha256": prov["file_hash_sha256"],
                    "source_file": prov["file_name"],
                    "table_locator": f"pdf_page_{TARGET_PAGE}/row_{r_idx + 1}/col_{c_idx + 1}/{key}",
                    "bbox_page_coords_300dpi": None,  # filled below
                    "word_boxes": boxes,
                    "ocr_confidence": round(conf / 100.0, 3),
                    "render_dpi": dpi,
                    "page_pdf_1indexed": TARGET_PAGE,
                    "extraction_method": "pdftoppm render + OSD rotate + ink-profile rows + rule-detect columns + tesseract psm7",
                    "needs_review": value is None or conf < 60,
                    "needs_review_reasons": ([reason] if reason else [])
                    + (["low_ocr_confidence"] if conf < 60 else []),
                }
                rows_out.append(obs)

    # bbox from word boxes (page coords at render dpi)
    for obs in rows_out:
        if obs["word_boxes"]:
            xs = [b["x"] for b in obs["word_boxes"]]
            ys = [b["y"] for b in obs["word_boxes"]]
            x0b, y0b = min(xs), min(ys)
            x1b = max(b["x"] + b["w"] for b in obs["word_boxes"])
            y1b = max(b["y"] + b["h"] for b in obs["word_boxes"])
            obs["bbox_page_coords_300dpi"] = {"x": x0b, "y": y0b, "w": x1b - x0b, "h": y1b - y0b}
        else:
            obs["needs_review"] = True
            if "no_ocr_words" not in obs["needs_review_reasons"]:
                obs["needs_review_reasons"].append("no_ocr_words")

    # identity QC (only rows with a readable year and full value triplets)
    by_row: dict[int, dict[str, dict]] = {}
    for obs in rows_out:
        if obs["year"] is not None and obs["value"] is not None:
            by_row.setdefault(obs["year"], {})[obs["column_key"]] = obs
    identity_flags = 0
    for year, cells in sorted(by_row.items()):
        for g in ("gt", "st", "gold", "silver", "gs"):
            imp = cells.get(f"{g}_imports")
            exp = cells.get(f"{g}_exports")
            exc = cells.get(f"{g}_excess")
            if imp and exp and exc and exp["value"] - imp["value"] != exc["value"]:
                exc["needs_review"] = True
                exc["needs_review_reasons"].append("identity_mismatch_excess")
                identity_flags += 1
        for leaf in ("imports", "exports", "excess"):
            gd = cells.get(f"gold_{leaf}")
            sv = cells.get(f"silver_{leaf}")
            gs = cells.get(f"gs_{leaf}")
            if gd and sv and gs and gd["value"] + sv["value"] != gs["value"]:
                gs["needs_review"] = True
                gs["needs_review_reasons"].append("identity_mismatch_gs_sum")
                identity_flags += 1

    for obs in rows_out:
        obs.pop("word_boxes", None)  # helper field, not part of deliverable

    result = {
        "sample": {
            "sample_id": "04-scanned-pdf",
            "source_url": prov["source_url"],
            "source_landing_page": prov["source_landing_page"],
            "source_file": prov["file_name"],
            "file_hash_sha256": prov["file_hash_sha256"],
            "fetched_at_utc": prov["acquisition"]["fetched_at_utc"],
            "copyright_note": prov["copyright_note"],
            "pdf_pages_total": pages,
            "target_page_pdf": TARGET_PAGE,
            "target_page_printed": prov["target_page_printed"],
            "render_dpi": dpi,
            "osd_rotation_applied_deg": rot,
            "rows_detected": len(row_bands),
            "columns_detected": len(col_windows),
            "observations": len(rows_out),
            "identity_mismatch_flags": identity_flags,
            "extraction_method": "tesseract psm7 per-cell OCR",
            # 锁定而非 datetime.now()：deterministic rebuild 需要字节稳定（B-07/I-01）。
            # 取 fetch 之后（provenance fetched_at_utc=05:37:59Z）的固定值，保持"先获取后抽取"时序。
            "extracted_at_utc": "2026-08-23T06:00:00Z",
            "truth_table": "spikes/04-scanned-pdf/truth_p24.json",
        },
        "rows": rows_out,
    }
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(result, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")

    n_val = sum(1 for o in rows_out if o["value"] is not None)
    n_rev = sum(1 for o in rows_out if o["needs_review"])
    print(f"rows detected: {len(row_bands)}; columns: {len(col_windows)}; OSD rotation: {rot} deg")
    print(f"observations: {len(rows_out)}; numeric parsed: {n_val}; needs_review: {n_rev}; identity flags: {identity_flags}")
    print(f"wrote {out_path}")
    return result


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--pdf", type=Path, default=DEFAULT_PDF)
    ap.add_argument("--out", type=Path, default=DEFAULT_OUT)
    ap.add_argument("--dpi", type=int, default=300)
    args = ap.parse_args()
    extract(args.pdf, args.out, args.dpi)
    return 0


if __name__ == "__main__":
    sys.exit(main())
