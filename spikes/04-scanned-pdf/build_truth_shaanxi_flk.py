#!/usr/bin/env python3
"""Build the accepted embedded-text reference for the Shaanxi OCR sample."""
from __future__ import annotations

import argparse
import hashlib
import json
import shutil
import subprocess
import sys
import tempfile
import xml.etree.ElementTree as ET
from pathlib import Path

from ocr_text_layout import (
    Word,
    calculate_region_divider,
    crossing_word_count,
    is_han,
    normalize_characters,
    split_page_regions,
)

HERE = Path(__file__).parent
REPO = HERE.parent.parent
DEFAULT_PDF = HERE / "data" / "shaanxi_fiscal_regulation_flk.pdf"
DEFAULT_OUT = HERE / "truth_shaanxi_flk.json"
PROVENANCE = HERE / "provenance.json"
SAMPLE_KEY = "shaanxi_fiscal_regulation_flk"


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def repo_relative(path: Path) -> str:
    try:
        return str(path.resolve().relative_to(REPO.resolve()))
    except ValueError:
        return f"<outside-repo>/{path.name}"


def tool_version(executable: str) -> str:
    result = subprocess.run([executable, "-v"], capture_output=True, text=True, check=False)
    output = (result.stderr or result.stdout).splitlines()
    return output[0].strip() if output else "unknown"


def fail(message: str) -> int:
    print(f"FATAL: {message}", file=sys.stderr)
    return 2


def build(pdf: Path) -> dict:
    if not pdf.exists():
        raise FileNotFoundError(f"PDF not found: {pdf}")
    if shutil.which("pdftotext") is None:
        raise RuntimeError("pdftotext is required")
    provenance = json.loads(PROVENANCE.read_text(encoding="utf-8"))
    sample = provenance["research_samples"][SAMPLE_KEY]
    actual_hash = sha256_file(pdf)
    if actual_hash != sample["file_hash_sha256"]:
        raise RuntimeError(
            f"sha256 mismatch: expected {sample['file_hash_sha256']}, got {actual_hash}"
        )

    with tempfile.TemporaryDirectory(prefix="shaanxi_truth_") as temp_dir:
        root = Path(temp_dir)
        text_path = root / "embedded.txt"
        bbox_path = root / "embedded.html"
        subprocess.run(
            ["pdftotext", "-enc", "UTF-8", str(pdf), str(text_path)],
            check=True,
            capture_output=True,
            text=True,
        )
        subprocess.run(
            ["pdftotext", "-bbox", str(pdf), str(bbox_path)],
            check=True,
            capture_output=True,
            text=True,
        )
        text_bytes = text_path.read_bytes()
        text_hash = hashlib.sha256(text_bytes).hexdigest()
        expected_text_hash = sample["embedded_text_layer"]["text_sha256"]
        if text_hash != expected_text_hash:
            raise RuntimeError(
                f"embedded text sha256 mismatch: expected {expected_text_hash}, got {text_hash}"
            )
        embedded_text = text_bytes.decode("utf-8")
        tree = ET.parse(bbox_path)

    namespace = {"x": "http://www.w3.org/1999/xhtml"}
    pages = []
    for page_number, page in enumerate(tree.findall(".//x:page", namespace), 1):
        words = [
            Word(
                float(word.attrib["xMin"]),
                float(word.attrib["yMin"]),
                float(word.attrib["xMax"]),
                float(word.attrib["yMax"]),
                word.text or "",
            )
            for word in page.findall(".//x:word", namespace)
        ]
        page_width = float(page.attrib["width"])
        divider = calculate_region_divider(words, page_width)
        regions = split_page_regions(words, page_width)
        pages.append(
            {
                "page_pdf_1indexed": page_number,
                "page_width_points": page_width,
                "page_height_points": float(page.attrib["height"]),
                "layout": {
                    "divider_x_points": round(divider, 2),
                    "physical_midpoint_x_points": round(page_width / 2, 2),
                    "crossing_word_count": crossing_word_count(words, divider),
                    "crossing_word_policy": "assign_by_bbox_center_and_report",
                },
                "regions": [
                    {
                        "name": name,
                        "canonical_lines": lines,
                        "normalized_non_whitespace_chars": len(
                            normalize_characters("\n".join(lines))
                        ),
                        "normalized_han_chars": len(
                            normalize_characters("\n".join(lines), han_only=True)
                        ),
                    }
                    for name, lines in regions.items()
                ],
            }
        )

    return {
        "schema_version": "1.1",
        "sample_id": sample["sample_id"],
        "source_file": repo_relative(pdf),
        "source_file_sha256": actual_hash,
        "reference": {
            "type": "embedded_pdf_text_layer_accepted_by_U2",
            "text_sha256": hashlib.sha256(text_bytes).hexdigest(),
            "text_characters": len(embedded_text),
            "han_characters": sum(is_han(character) for character in embedded_text),
            "non_whitespace_characters": sum(
                not character.isspace() for character in embedded_text
            ),
            "known_limitation": (
                "The embedded layer is prior OCR, not human-corrected ground truth; "
                "its recognition errors remain unchanged in this reference."
            ),
        },
        "layout_canonicalization": {
            "method": "robust_content_bounds_midpoint_then_y_line_and_x_word_order",
            "regions": ["left", "right"],
            "content_bound_trim_ratio_each_side": 0.05,
            "crossing_word_policy": "assign_by_bbox_center_and_report",
            "line_y_tolerance": "max(3 points, median_word_height * 0.45)",
            "recognized_character_identity_used_for_bounds": False,
        },
        "pages_total": len(pages),
        "pages": pages,
        "toolchain": {"pdftotext": tool_version("pdftotext")},
    }


def main() -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Build the U-2 accepted embedded-text reference from the pinned Shaanxi PDF."
        ),
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument("--pdf", type=Path, default=DEFAULT_PDF, help="source PDF")
    parser.add_argument("--out", type=Path, default=DEFAULT_OUT, help="reference JSON output")
    args = parser.parse_args()
    try:
        result = build(args.pdf)
        args.out.parent.mkdir(parents=True, exist_ok=True)
        args.out.write_text(
            json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )
    except (
        FileNotFoundError,
        json.JSONDecodeError,
        KeyError,
        OSError,
        RuntimeError,
        subprocess.CalledProcessError,
        ET.ParseError,
        UnicodeDecodeError,
    ) as exc:
        return fail(str(exc))
    print(f"wrote {args.out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
