#!/usr/bin/env python3
"""OCR the Shaanxi Chinese scanned-PDF research sample from page images only."""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import shutil
import struct
import subprocess
import sys
import tempfile
from pathlib import Path

from ocr_text_layout import (
    Word,
    calculate_region_divider,
    crossing_word_count,
    normalize_characters,
    split_page_regions,
)

HERE = Path(__file__).parent
REPO = HERE.parent.parent
DEFAULT_PDF = HERE / "data" / "shaanxi_fiscal_regulation_flk.pdf"
DEFAULT_OUT = REPO / "data" / "extracts" / "04-scanned-pdf" / "shaanxi_text_ocr.json"
PROVENANCE = HERE / "provenance.json"
SAMPLE_KEY = "shaanxi_fiscal_regulation_flk"
DPI = 300
PSM = 6
LANGUAGE = "chi_sim"


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


def command_version(command: list[str]) -> str:
    result = subprocess.run(command, capture_output=True, text=True, check=False)
    output = (result.stdout or result.stderr).splitlines()
    return output[0].strip() if output else "unknown"


def locate_traineddata(list_languages_output: str) -> Path:
    candidates = []
    prefix = os.environ.get("TESSDATA_PREFIX")
    if prefix:
        candidates.extend(
            [Path(prefix) / f"{LANGUAGE}.traineddata", Path(prefix) / "tessdata" / f"{LANGUAGE}.traineddata"]
        )
    match = re.search(r'available languages in "([^"]+)"', list_languages_output)
    if match:
        candidates.append(Path(match.group(1)) / f"{LANGUAGE}.traineddata")
    for candidate in candidates:
        if candidate.is_file():
            return candidate.resolve()
    raise RuntimeError(f"cannot locate tesseract language data: {LANGUAGE}.traineddata")


def require_tools() -> Path:
    missing = [tool for tool in ("pdfinfo", "pdftoppm", "tesseract") if shutil.which(tool) is None]
    if missing:
        raise RuntimeError(f"required executable not found: {', '.join(missing)}")
    result = subprocess.run(
        ["tesseract", "--list-langs"], capture_output=True, text=True, check=True
    )
    languages_output = result.stdout or result.stderr
    languages = {language.strip() for language in languages_output.splitlines()[1:]}
    if LANGUAGE not in languages:
        raise RuntimeError(f"tesseract language not installed: {LANGUAGE}")
    return locate_traineddata(languages_output)


def png_dimensions(path: Path) -> tuple[int, int]:
    header = path.read_bytes()[:24]
    if len(header) != 24 or header[:8] != b"\x89PNG\r\n\x1a\n":
        raise RuntimeError(f"rendered page is not PNG: {path.name}")
    return struct.unpack(">II", header[16:24])


def page_number(path: Path) -> int:
    return int(path.stem.rsplit("-", 1)[1])


def parse_tsv(tsv: str) -> tuple[list[Word], list[float]]:
    words = []
    confidences = []
    for line in tsv.splitlines()[1:]:
        columns = line.split("\t")
        if len(columns) < 12 or columns[0] != "5" or not columns[11].strip():
            continue
        x, y, width, height = map(int, columns[6:10])
        confidence = float(columns[10])
        words.append(
            Word(x, y, x + width, y + height, columns[11].strip(), confidence)
        )
        if confidence >= 0:
            confidences.append(confidence)
    return words, confidences


def extract(pdf: Path) -> dict:
    if not pdf.exists():
        raise FileNotFoundError(f"PDF not found: {pdf}")
    traineddata = require_tools()
    provenance = json.loads(PROVENANCE.read_text(encoding="utf-8"))
    sample = provenance["research_samples"][SAMPLE_KEY]
    actual_hash = sha256_file(pdf)
    if actual_hash != sample["file_hash_sha256"]:
        raise RuntimeError(
            f"sha256 mismatch: expected {sample['file_hash_sha256']}, got {actual_hash}"
        )
    pdf_info = subprocess.run(
        ["pdfinfo", str(pdf)], capture_output=True, text=True, check=True
    ).stdout
    pages_line = next(
        (line for line in pdf_info.splitlines() if line.startswith("Pages:")), None
    )
    if pages_line is None:
        raise RuntimeError("pdfinfo did not report page count")
    pages_total = int(pages_line.split(":", 1)[1].strip())
    if pages_total != sample["pdf_pages_total"]:
        raise RuntimeError(
            f"page count mismatch: expected {sample['pdf_pages_total']}, got {pages_total}"
        )

    pages = []
    with tempfile.TemporaryDirectory(prefix="shaanxi_ocr_") as temp_dir:
        prefix = Path(temp_dir) / "page"
        subprocess.run(
            ["pdftoppm", "-r", str(DPI), "-gray", "-png", str(pdf), str(prefix)],
            check=True,
            capture_output=True,
            text=True,
        )
        images = sorted(Path(temp_dir).glob("page-*.png"), key=page_number)
        if len(images) != pages_total:
            raise RuntimeError(f"rendered {len(images)} pages, expected {pages_total}")
        for index, image in enumerate(images, 1):
            width, height = png_dimensions(image)
            result = subprocess.run(
                [
                    "tesseract",
                    str(image),
                    "stdout",
                    "-l",
                    LANGUAGE,
                    "--psm",
                    str(PSM),
                    "tsv",
                ],
                capture_output=True,
                text=True,
                check=True,
            )
            words, confidences = parse_tsv(result.stdout)
            divider = calculate_region_divider(words, width)
            regions = split_page_regions(words, width)
            pages.append(
                {
                    "page_pdf_1indexed": index,
                    "render_width_pixels": width,
                    "render_height_pixels": height,
                    "word_count": len(words),
                    "mean_word_confidence": (
                        round(sum(confidences) / len(confidences), 2)
                        if confidences
                        else None
                    ),
                    "layout": {
                        "divider_x_pixels": round(divider, 2),
                        "physical_midpoint_x_pixels": round(width / 2, 2),
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
        "sample": {
            "sample_id": sample["sample_id"],
            "source_url": sample["source_url"],
            "source_file": repo_relative(pdf),
            "file_hash_sha256": actual_hash,
            "pdf_pages_total": pages_total,
            "role": sample["role"],
        },
        "extraction": {
            "input": "rendered_scanned_page_images_only",
            "embedded_text_layer_used": False,
            "render_dpi": DPI,
            "tesseract_language": LANGUAGE,
            "page_segmentation_mode": PSM,
            "layout_canonicalization": (
                "robust_content_bounds_midpoint_then_y_line_and_x_word_order"
            ),
            "content_bound_trim_ratio_each_side": 0.05,
            "crossing_word_policy": "assign_by_bbox_center_and_report",
        },
        "pages": pages,
        "toolchain": {
            "pdfinfo": command_version(["pdfinfo", "-v"]),
            "pdftoppm": command_version(["pdftoppm", "-v"]),
            "tesseract": command_version(["tesseract", "--version"]),
            "tesseract_language_data": {
                "filename": traineddata.name,
                "sha256": sha256_file(traineddata),
                "size_bytes": traineddata.stat().st_size,
            },
        },
    }


def fail(message: str) -> int:
    print(f"FATAL: {message}", file=sys.stderr)
    return 2


def main() -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Run image-only Chinese OCR on the pinned Shaanxi scanned PDF and write JSON."
        ),
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument("--pdf", type=Path, default=DEFAULT_PDF, help="source PDF")
    parser.add_argument("--out", type=Path, default=DEFAULT_OUT, help="OCR JSON output")
    args = parser.parse_args()
    try:
        result = extract(args.pdf)
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
        UnicodeDecodeError,
        ValueError,
    ) as exc:
        return fail(str(exc))
    print(f"wrote {args.out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
