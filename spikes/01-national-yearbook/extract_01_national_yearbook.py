"""
Spike 1: 国家统计年鉴表 extraction
Source: stats.gov.cn monthly economic report (HTML table)
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
from pathlib import Path

# Relative to this file's location
SAMPLE_HTML = Path(__file__).parent / "sample.html"
EXTRACT_OUT = Path(__file__).parent.parent.parent / "data" / "extracts" / "01-national-yearbook" / "extracted.json"


def compute_sha256(path: Path) -> str:
    """Compute SHA-256 hex digest of a file."""
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            h.update(chunk)
    return h.hexdigest()


def parse_html_table(html_content: str) -> list[dict]:
    """
    Parse the main table from the monthly report HTML.
    Returns a list of row dicts with cleaned cell text.
    """
    rows_data = []
    # Find all tables
    table_pattern = re.compile(r"<table[^>]*>(.*?)</table>", re.DOTALL)
    tables = table_pattern.findall(html_content)

    if not tables:
        return []

    # Use the first (largest) table
    main_table = tables[0]

    # Extract rows
    row_pattern = re.compile(r"<tr[^>]*>(.*?)</tr>", re.DOTALL)
    rows = row_pattern.findall(main_table)

    # Extract cells from each row
    cell_pattern = re.compile(r"<t[dh][^>]*>(.*?)</t[dh]>", re.DOTALL)

    for row in rows:
        cells = cell_pattern.findall(row)
        cleaned = []
        for cell in cells:
            # Strip HTML tags and normalize whitespace
            text = re.sub(r"<[^>]+>", "", cell).strip()
            text = re.sub(r"\s+", " ", text)
            cleaned.append(text)
        rows_data.append(cleaned)

    return rows_data


def extract_rows(rows_data: list[list[str]], max_rows: int = 12) -> list[dict]:
    """
    Convert parsed table rows into structured observation dicts.

    The table structure is:
      Row 0: [指标, 7月, 1—7月]
      Row 1: [绝对量, 同比增长 (%), 绝对量, 同比增长 (%)]
      Rows 2+: data rows with indicator name + 4 values

    We extract rows 2..max_rows+2 (header + data rows).
    Each row maps to up to 4 observations (col groups for 7月 and 1-7月).
    Only rows with at least one non-null numeric value are included.
    """
    observations = []

    if len(rows_data) < 3:
        return observations

    # Section header patterns to skip
    SECTION_HEADERS = {"分三大门类", "分经济类型", "四、房地产开发", "五、能源",
                       "六、销售", "七、居民", "八、进出", "九、金融", "十、居民消费价格"}

    for row_idx in range(2, min(len(rows_data), max_rows + 2)):
        row = rows_data[row_idx]
        if not row or len(row) < 2:
            continue

        indicator = row[0].strip()
        if not indicator:
            continue

        # Skip section header rows (they have no numeric data)
        if indicator in SECTION_HEADERS or any(h in indicator for h in ["分", "其中", "其中："]):
            # Check if this row actually has numeric data before skipping
            has_data = any(
                _parse_value(row[i])[0] is not None
                for i in range(1, min(len(row), 5))
                if i < len(row)
            )
            if not has_data:
                continue

        row_observations = []
        # Column mapping: [col_idx, period, unit]
        for col_idx, period, unit in [
            (2, "2026-07", "%"),        # 7月 growth rate
            (4, "2026-01~07", "%"),    # 1-7月 growth rate
        ]:
            if col_idx < len(row):
                raw_value = row[col_idx].strip()
                value, confidence = _parse_value(raw_value)

                if value is not None:
                    obs = {
                        "indicator": _normalize_indicator(indicator),
                        "period": period,
                        "value": value,
                        "unit": unit,
                        "source_url": "https://www.stats.gov.cn/sj/zxfb/202608/t20260817_1965056.html",
                        "table_locator": "table[1]/tr[{}]/td[{}]".format(row_idx + 1, col_idx + 1),
                        "extraction_method": "html.parser + regex",
                        "confidence": confidence,
                    }
                    row_observations.append(obs)

        observations.extend(row_observations)

    return observations


def _parse_value(raw: str) -> tuple[float | None, float]:
    """
    Parse a numeric value from raw cell text.
    Returns (parsed_float, confidence).
    Confidence is lower when the value is suppressed (…)
    or has special annotations.
    """
    raw = raw.strip()

    # Suppressed / unavailable
    if raw in ("…", "—", "－", "-", "", "暂无"):
        return None, 0.0

    # Handle "(百分点)" annotations — extract the number
    has_百分点 = "百分点" in raw
    cleaned = re.sub(r"\s*\(.*?\)", "", raw).strip()

    # Remove unit-like suffixes and non-numeric characters except . and -
    cleaned = re.sub(r"[^\d.\-]", "", cleaned)

    if not cleaned:
        return None, 0.3  # suppressed with low confidence

    try:
        val = float(cleaned)
        # Confidence: lower for very small values or edge cases
        confidence = 0.95 if abs(val) < 100 else 0.9
        return val, confidence
    except ValueError:
        return None, 0.1


def _normalize_indicator(name: str) -> str:
    """Normalize indicator names for consistent storage."""
    return name.strip().replace("　", "").replace(" ", "")


def run_extraction(input_path: Path | None = None, output_path: Path | None = None) -> dict:
    """
    Main extraction pipeline.

    Args:
        input_path: HTML source file (default = SAMPLE_HTML)
        output_path: JSON output (default = EXTRACT_OUT)

    Raises:
        FileNotFoundError: if input_path doesn't exist
    """
    if input_path is None:
        input_path = SAMPLE_HTML
    if output_path is None:
        output_path = EXTRACT_OUT
    if not input_path.exists():
        raise FileNotFoundError(f"Sample HTML not found: {input_path}")

    with open(input_path, "r", encoding="utf-8", errors="replace") as f:
        html_content = f.read()

    file_hash = compute_sha256(input_path)
    rows_data = parse_html_table(html_content)
    observations = extract_rows(rows_data)

    result = {
        "sample": {
            "source_url": "https://www.stats.gov.cn/sj/zxfb/202608/t20260817_1965056.html",
            "source_type": "html",
            "file_hash_sha256": file_hash,
            "table_locator": "table[1] — 规模以上工业增加值月度数据表 (1—7月份)",
            # 锁定 fetched_at 以保证 deterministic rebuild（per directive 四-1）
            "fetched_at": "2026-08-17T00:00:00Z",
            "extraction_method": "html.parser + regex",
            "sample_rows_extracted": len(observations),
            "raw_table_rows": len(rows_data),
            "file_name": input_path.name,
            "file_size_bytes": input_path.stat().st_size,
        },
        "rows": observations,
    }

    # Write output
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)

    print(f"Extracted {len(observations)} observations -> {output_path}")
    return result


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", type=Path, default=SAMPLE_HTML)
    parser.add_argument("--out", type=Path, default=EXTRACT_OUT)
    args = parser.parse_args()
    try:
        run_extraction(args.input, args.out)
        return 0
    except FileNotFoundError as e:
        print(f"FATAL: {e}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    import sys
    sys.exit(main())
