#!/usr/bin/env python3
"""Evaluate Shaanxi image-only OCR against the accepted embedded-text reference."""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from ocr_text_layout import score_region_pairs

HERE = Path(__file__).parent
REPO = HERE.parent.parent
DEFAULT_TRUTH = HERE / "truth_shaanxi_flk.json"
DEFAULT_EXTRACTED = (
    REPO / "data" / "extracts" / "04-scanned-pdf" / "shaanxi_text_ocr.json"
)
DEFAULT_OUT = DEFAULT_EXTRACTED.parent / "shaanxi_text_eval_report.json"
THRESHOLDS = HERE / "gate_thresholds.json"
REGION_NAMES = ("left", "right")


def repo_relative(path: Path) -> str:
    try:
        return str(path.resolve().relative_to(REPO.resolve()))
    except ValueError:
        return f"<outside-repo>/{path.name}"


def regions_by_name(page: dict) -> dict[str, str]:
    regions = {
        region["name"]: "\n".join(region["canonical_lines"])
        for region in page["regions"]
    }
    if set(regions) != set(REGION_NAMES):
        raise ValueError(f"unexpected region names: {sorted(regions)}")
    return regions


def evaluate(truth: dict, extracted: dict) -> dict:
    if truth["sample_id"] != extracted["sample"]["sample_id"]:
        raise ValueError("sample IDs differ")
    if truth["source_file_sha256"] != extracted["sample"]["file_hash_sha256"]:
        raise ValueError("source PDF hashes differ")
    truth_pages = truth["pages"]
    extracted_pages = extracted["pages"]
    if len(truth_pages) != len(extracted_pages):
        raise ValueError("page counts differ")

    thresholds = json.loads(THRESHOLDS.read_text(encoding="utf-8"))["thresholds"]
    char_minimum = float(thresholds["char_accuracy_min_pct"])
    review_maximum = float(thresholds["needs_review_max_pct"])
    all_truth_regions = []
    all_ocr_regions = []
    page_metrics = []
    review_pages = []

    for expected_page, observed_page in zip(truth_pages, extracted_pages, strict=True):
        page_number = expected_page["page_pdf_1indexed"]
        if observed_page["page_pdf_1indexed"] != page_number:
            raise ValueError(f"page ordering differs at page {page_number}")
        truth_regions = regions_by_name(expected_page)
        ocr_regions = regions_by_name(observed_page)
        truth_values = [truth_regions[name] for name in REGION_NAMES]
        ocr_values = [ocr_regions[name] for name in REGION_NAMES]
        all_truth_regions.extend(truth_values)
        all_ocr_regions.extend(ocr_values)
        all_characters = score_region_pairs(truth_values, ocr_values)
        han_characters = score_region_pairs(truth_values, ocr_values, han_only=True)
        needs_review = han_characters["accuracy_pct"] < char_minimum
        reasons = ["han_character_accuracy_below_unchanged_threshold"] if needs_review else []
        if needs_review:
            review_pages.append(page_number)
        page_metrics.append(
            {
                "page_pdf_1indexed": page_number,
                "han_characters": han_characters,
                "all_non_whitespace_characters": all_characters,
                "needs_review": needs_review,
                "needs_review_reasons": reasons,
            }
        )

    han_characters = score_region_pairs(
        all_truth_regions, all_ocr_regions, han_only=True
    )
    all_characters = score_region_pairs(all_truth_regions, all_ocr_regions)
    pages_total = len(page_metrics)
    needs_review_pct = round(100.0 * len(review_pages) / pages_total, 2) if pages_total else 0.0
    char_threshold_met = han_characters["accuracy_pct"] >= char_minimum
    review_threshold_met = needs_review_pct <= review_maximum

    return {
        "schema_version": "1.1",
        "sample_id": truth["sample_id"],
        "source_file_sha256": truth["source_file_sha256"],
        "truth_file": repo_relative(DEFAULT_TRUTH),
        "extracted_file": repo_relative(DEFAULT_EXTRACTED),
        "reference": {
            "type": truth["reference"]["type"],
            "text_sha256": truth["reference"]["text_sha256"],
            "accepted_policy": "U2",
            "known_limitation": truth["reference"]["known_limitation"],
            "interpretation": (
                "Scores are agreement with the accepted embedded OCR layer, not an "
                "estimate against human-corrected ground truth. Correct new OCR may be "
                "penalized where the reference layer is wrong."
            ),
        },
        "evaluation_method": {
            "layout": "adaptive_left_and_right_content_regions_scored_independently",
            "region_order": list(REGION_NAMES),
            "within_region_order": "physical_lines_top_to_bottom_words_left_to_right",
            "normalization": "Unicode_NFKC_remove_whitespace_and_control_characters",
            "primary_character_class": "Han_ideographs_U+3400_to_U+9FFF",
            "distance": "Levenshtein_per_region_summed_with_max_length_denominator",
        },
        "char_accuracy_pct": han_characters["accuracy_pct"],
        "han_character_accuracy": han_characters,
        "all_non_whitespace_char_accuracy_pct": all_characters["accuracy_pct"],
        "all_non_whitespace_character_accuracy": all_characters,
        "numeric_cell_accuracy_pct": None,
        "numeric_metric_status": "not_applicable_non_tabular_source",
        "pages_total": pages_total,
        "needs_review_total": len(review_pages),
        "needs_review_pages": review_pages,
        "needs_review_pct": needs_review_pct,
        "pages": page_metrics,
        "threshold_assessment": {
            "thresholds_source": repo_relative(THRESHOLDS),
            "threshold_values_unchanged": True,
            "char_accuracy_min_pct": char_minimum,
            "char_accuracy_met": char_threshold_met,
            "needs_review_max_pct": review_maximum,
            "needs_review_definition": "page_han_accuracy_below_char_accuracy_min_pct",
            "needs_review_scope": (
                "shaanxi_research_page_triage_not_legacy_numeric_cell_parse_signal"
            ),
            "needs_review_met": review_threshold_met,
            "numeric_cell_accuracy": "not_applicable_not_counted_as_pass",
            "applicable_thresholds_all_met": char_threshold_met and review_threshold_met,
            "research_track_result": (
                "MEETS_UNCHANGED_APPLICABLE_THRESHOLDS"
                if char_threshold_met and review_threshold_met
                else "DOES_NOT_MEET_UNCHANGED_APPLICABLE_THRESHOLDS"
            ),
        },
        "stage0_effect": "none_per_U3_non_gating_research_sample",
        "stage0_verdict": "not_determined_by_this_report_user_U4_required",
    }


def fail(message: str) -> int:
    print(f"FATAL: {message}", file=sys.stderr)
    return 2


def main() -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Compare Shaanxi image-only OCR JSON with the U-2 embedded-text reference."
        ),
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument("--truth", type=Path, default=DEFAULT_TRUTH, help="reference JSON")
    parser.add_argument(
        "--extracted", type=Path, default=DEFAULT_EXTRACTED, help="image-only OCR JSON"
    )
    parser.add_argument("--out", type=Path, default=DEFAULT_OUT, help="evaluation JSON output")
    args = parser.parse_args()
    try:
        if not args.truth.exists():
            raise FileNotFoundError(f"truth file missing: {args.truth}")
        if not args.extracted.exists():
            raise FileNotFoundError(f"extracted output missing: {args.extracted}")
        truth = json.loads(args.truth.read_text(encoding="utf-8"))
        extracted = json.loads(args.extracted.read_text(encoding="utf-8"))
        report = evaluate(truth, extracted)
        report["truth_file"] = repo_relative(args.truth)
        report["extracted_file"] = repo_relative(args.extracted)
        args.out.parent.mkdir(parents=True, exist_ok=True)
        args.out.write_text(
            json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )
    except (
        FileNotFoundError,
        json.JSONDecodeError,
        KeyError,
        OSError,
        TypeError,
        UnicodeDecodeError,
        ValueError,
    ) as exc:
        return fail(str(exc))
    print(f"wrote {args.out}")
    print(f"han_character_accuracy_pct: {report['char_accuracy_pct']}")
    print(
        "all_non_whitespace_char_accuracy_pct: "
        f"{report['all_non_whitespace_char_accuracy_pct']}"
    )
    print(f"needs_review_pct: {report['needs_review_pct']}")
    print(f"research_track_result: {report['threshold_assessment']['research_track_result']}")
    print(f"stage0_effect: {report['stage0_effect']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
