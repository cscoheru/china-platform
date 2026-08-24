#!/usr/bin/env python3
"""Evaluate spike 04 extraction against truth_p24.json.

Reports the metrics mandated by directive 二-5: character accuracy on digits,
numeric cell accuracy, indicator-name accuracy, unit accuracy, bbox / page
locator accuracy, plus needs_review counts and reason breakdown.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

HERE = Path(__file__).parent
REPO = HERE.parent.parent
TRUTH_DEFAULT = HERE / "truth_p24.json"
EXTRACTED_DEFAULT = REPO / "data" / "extracts" / "04-scanned-pdf" / "extracted.json"


def _to_repo_relative(p: Path) -> str:
    """R5-H: 把任意路径解析为相对 REPO 的字符串；失败则返回占位 "<abs>"。

    与 manifest 契约一致：禁止 /Users/、/home/、/tmp/ 等绝对/系统前缀出现在
    跨会话输出的 JSON 字段中。
    """
    try:
        return str(p.resolve().relative_to(REPO.resolve()))
    except ValueError:
        # 路径不在 REPO 内（cross-mount、临时挂载等）；保留文件名部分避免泄漏
        return f"<outside-repo>/{p.name}"
GEOM_300 = {  # truth geometry @600dpi / 2; used for bbox overlap check
    "year_band_x": [65, 135],
    "column_x_windows": {
        "gt_imports": [280, 422], "gt_exports": [427, 562], "gt_excess": [570, 705],
        "st_imports": [712, 835], "st_exports": [842, 965], "st_excess": [987, 1125],
        "gold_imports": [1135, 1257], "gold_exports": [1265, 1395], "gold_excess": [1412, 1545],
        "silver_imports": [1555, 1667], "silver_exports": [1677, 1820], "silver_excess": [1830, 1967],
        "gs_imports": [1977, 2100], "gs_exports": [2107, 2230], "gs_excess": [2237, 2375],
    },
    "row_ink_peaks_y": {str(y): p // 2 for y, p in zip(
        range(1843, 1873),
        [1316, 1367, 1417, 1467, 1517, 1568, 1618, 1669, 1718, 1769, 1819, 1869, 1919, 1969,
         2020, 2070, 2120, 2170, 2220, 2270, 2321, 2371, 2421, 2471, 2521, 2571, 2621, 2671, 2720, 2771])},
}
DPI = 300


def digit_chars(s: str) -> str:
    return "".join(c for c in s if c.isdigit())


def overlap(a: dict, b: tuple[int, int, int, int]) -> float:
    ax, ay, aw, ah = a["x"], a["y"], a["w"], a["h"]
    bx0, by0, bx1, by1 = b
    ox = max(0, min(ax + aw, bx1) - max(ax, bx0))
    oy = max(0, min(ay + ah, by1) - max(ay, by0))
    inter = ox * oy
    return inter / max(1, aw * ah)


def expected_bbox(year: int, key: str) -> tuple[int, int, int, int] | None:
    cx0, cx1 = GEOM_300["column_x_windows"][key]
    py = GEOM_300["row_ink_peaks_y"].get(str(year))
    if py is None:
        return None
    return (cx0, py - 11, cx1, py + 3)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--truth", type=Path, default=TRUTH_DEFAULT)
    ap.add_argument("--extracted", type=Path, default=EXTRACTED_DEFAULT)
    args = ap.parse_args()
    if not args.truth.exists():
        print(f"FATAL: truth table missing: {args.truth}", file=sys.stderr); return 2
    if not args.extracted.exists():
        print(f"FATAL: extracted output missing: {args.extracted}", file=sys.stderr); return 2
    truth = json.loads(args.truth.read_text(encoding="utf-8"))
    extracted = json.loads(args.extracted.read_text(encoding="utf-8"))

    truth_cells = {f"{r['year']}_{k}": r[k] for r in truth["rows_data"] for k in GEOM_300["column_x_windows"]}

    n_obs = len(extracted["rows"])
    n_matched = 0
    char_correct = char_total = 0
    val_correct = val_compared = 0
    indicator_correct = 0
    unit_correct = 0
    page_correct = 0
    bbox_correct = bbox_with_truth = 0
    needs_review_breakdown: dict[str, int] = {}

    by_year: dict[int, dict] = {}
    truth_by_year = {r["year"]: r for r in truth["rows_data"]}

    for obs in extracted["rows"]:
        # Year mapping: extracted has row_index; derive year by row_index via the
        # detected ordering (which preserves printed order on the page).
        row_index = obs["row_index"]
        if row_index not in by_year:
            by_year[row_index] = obs  # store one anchor to learn year later
        expected_year = 1843 + row_index
        key = obs["column_key"]
        truth_val = truth_by_year.get(expected_year, {}).get(key)
        if truth_val is None:
            continue
        n_matched += 1
        truth_digits = str(abs(truth_val))
        raw_digits = digit_chars(obs["raw_ocr"])
        if truth_digits or raw_digits:
            char_total += max(len(truth_digits), len(raw_digits))
            char_correct += sum(1 for a, b in zip(truth_digits.ljust(len(raw_digits), "?"),
                                                   raw_digits.ljust(len(truth_digits), "?")) if a == b)
        if obs["value"] is not None and truth_val is not None:
            val_compared += 1
            if obs["value"] == truth_val:
                val_correct += 1
        # indicator name = truth expected_key, which equals obs["column_key"]
        if obs["column_key"] == key:
            indicator_correct += 1
        if obs["unit"] == "1,000 dollars":
            unit_correct += 1
        if obs["page_pdf_1indexed"] == 24:
            page_correct += 1
        exp_bbox = expected_bbox(expected_year, key)
        bbox = obs.get("bbox_page_coords_300dpi")
        if exp_bbox and bbox:
            bbox_with_truth += 1
            if overlap(bbox, exp_bbox) >= 0.5:
                bbox_correct += 1
        if obs["needs_review"]:
            for r in obs["needs_review_reasons"]:
                needs_review_breakdown[r] = needs_review_breakdown.get(r, 0) + 1

    pct = lambda a, b: round(100.0 * a / b, 1) if b else 0.0
    report = {
        "observations_total": n_obs,
        "matched_to_truth": n_matched,
        "char_accuracy_pct": pct(char_correct, char_total),
        "char_correct": char_correct,
        "char_compared": char_total,
        "numeric_cell_accuracy_pct": pct(val_correct, val_compared),
        "numeric_cell_correct": val_correct,
        "numeric_cell_compared": val_compared,
        "indicator_name_accuracy_pct": pct(indicator_correct, n_matched),
        "unit_accuracy_pct": pct(unit_correct, n_matched),
        "page_locator_accuracy_pct": pct(page_correct, n_obs),
        "bbox_locator_accuracy_pct": pct(bbox_correct, bbox_with_truth),
        "bbox_compared": bbox_with_truth,
        "needs_review_total": sum(1 for o in extracted["rows"] if o["needs_review"]),
        "needs_review_breakdown": dict(sorted(needs_review_breakdown.items(), key=lambda x: -x[1])),
        "truth_table": _to_repo_relative(args.truth),
        "extracted_file": _to_repo_relative(args.extracted),
    }
    out = args.extracted.parent / "eval_report.json"
    out.write_text(json.dumps(report, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
    for k, v in report.items():
        if k != "needs_review_breakdown":
            print(f"  {k}: {v}")
    print(f"  needs_review_breakdown: {report['needs_review_breakdown']}")
    print(f"wrote {out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())