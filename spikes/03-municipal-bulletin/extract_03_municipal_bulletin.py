#!/usr/bin/env python3
"""
Spike 03: Municipal Statistical Bulletin Extraction

Source: 深圳市2024年国民经济和社会发展统计公报
URL:    https://www.sz.gov.cn/zfgb/2025/gb1374/content/post_12212437.html
Format: HTML (single-page, prose + embedded figures)
City:   深圳 (Shenzhen)
Year:   2024

Extraction strategy:
  - The bulletin is a long HTML page rendered from sz.gov.cn.
  - The article body lives in <div class="news_cont_d_wrap">.
  - Statistics appear primarily as PROSE (paragraph text with embedded numbers),
    NOT as structured HTML tables.  This is the key variability signal for Spike 03.
  - We parse the text section by section (section headings like "一、综合", "二、农业").
  - We then apply targeted regex patterns per indicator family.

Format variability observations (documented for spikes 04 + 08 planning):
  - This city's bulletin uses PROSE paragraphs for most statistics.
    No visible HTML <table> elements in the article body — values are
    inline in sentences like "深圳地区生产总值36801.87亿元，比上年增长5.8%"."
  - Section headings anchor each paragraph group.
  - Units (亿元 / 万人 / 元) are embedded in text, not column headers.
  - Some rows contain ranges, footnotes, or qualifiers in the same sentence.
  - A chart placeholder (图1) interrupts the prose at the foreign trade section.
  - Comparison basis (当年价格 / 可比价格) is sometimes stated explicitly
    ("按可比价格计算") and sometimes omitted.
"""

import hashlib
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

try:
    from bs4 import BeautifulSoup
except ImportError:
    print("ERROR: beautifulsoup4 not installed. Run: pip install beautifulsoup4 lxml")
    sys.exit(1)


# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

BULLETIN_URL = (
    "https://www.sz.gov.cn/zfgb/2025/gb1374/content/post_12212437.html"
)
CITY = "深圳"
YEAR = 2024
SOURCE_TYPE = "html"

# Local cache of the downloaded HTML
CACHE_PATH = Path(__file__).parent / "sample.html"
OUTPUT_DIR = Path(__file__).parent.parent.parent / "data" / "extracts" / "03-municipal-bulletin"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


# ---------------------------------------------------------------------------
# Download / load
# ---------------------------------------------------------------------------

def fetch_bulletin() -> bytes:
    """Fetch the bulletin HTML, caching locally."""
    if CACHE_PATH.exists():
        print(f"[INFO] Using cached sample: {CACHE_PATH}")
        return CACHE_PATH.read_bytes()

    print(f"[INFO] Fetching {BULLETIN_URL}")
    try:
        import httpx
    except ImportError:
        import requests as _req
        resp = _req.get(BULLETIN_URL, timeout=30,
                        headers={"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)"})
        resp.raise_for_status()
        data = resp.content
    else:
        with httpx.Client(timeout=30.0) as client:
            resp = client.get(BULLETIN_URL,
                              headers={"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)"})
            resp.raise_for_status()
            data = resp.content

    CACHE_PATH.write_bytes(data)
    print(f"[INFO] Cached {len(data):,} bytes to {CACHE_PATH}")
    return data


def compute_sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


# ---------------------------------------------------------------------------
# Parsing helpers
# ---------------------------------------------------------------------------

def parse_value_unit(text: str) -> tuple[Optional[float], Optional[str]]:
    """
    Extract a numeric value and its unit from text like "36801.87亿元" or "5.8%" or "97.0%" or "17.3微克/立方米".
    Returns (float_value, unit_string) or (None, None) if no number found.
    """
    # Match a leading number (including comma-separated)
    m = re.search(r"([0-9,\.]+)", text)
    if not m:
        return None, None
    raw = m.group(1).replace(",", "")
    try:
        value = float(raw)
    except ValueError:
        return None, None

    # Determine unit: strip the number from the text and clean up
    unit = text[len(m.group(0)):].strip()
    # Normalise whitespace
    unit = re.sub(r"\s+", " ", unit)
    return value, unit


def extract_prose_stat(paragraph: str, indicator_keywords: list[str]) -> dict | None:
    """
    Scan a paragraph for indicator keywords; if found, extract the primary value + context.
    Returns a dict or None.
    """
    text = paragraph.strip()
    for kw in indicator_keywords:
        if kw in text:
            # Try to extract: number immediately adjacent to keyword, or nearby in sentence
            # Pattern: keyword + (some text with number)
            # Heuristic: find the first number in the same sentence (up to 。 or ；)
            sentence = re.split(r"[；；]", text)[0]
            # Look for numbers near the keyword
            pattern = (
                kw +
                r"[^\n。；]{{0,60}}"   # up to 60 chars
                r"([0-9,\.]+(?:\.[0-9]+)?)"  # the number
                r"([^\n。；]{{0,30}}?)"  # trailing unit text
            )
            m = re.search(pattern, sentence)
            if not m:
                # fallback: find first number in paragraph
                nm = re.search(r"([0-9,\.]+)", sentence)
                if nm:
                    num = float(nm.group(1).replace(",", ""))
                    unit_raw = sentence[nm.end():].strip()[:30]
                    return {
                        "raw_number": num,
                        "unit": unit_raw,
                        "sentence": sentence[:150],
                    }
                continue

            num_str = m.group(1).replace(",", "")
            unit_raw = m.group(2).strip()
            num = float(num_str)

            return {
                "raw_number": num,
                "unit": unit_raw,
                "sentence": sentence[:200],
            }
    return None


# ---------------------------------------------------------------------------
# Section-aware extraction
# ---------------------------------------------------------------------------

def extract_statistics(html_bytes: bytes) -> list[dict]:
    """
    Parse the bulletin HTML and extract 3-8 key statistics.
    The bulletin is sectioned (一、综合 / 二、农业 / ...).
    Statistics appear inline in prose paragraphs, NOT in HTML tables.
    """
    soup = BeautifulSoup(html_bytes, "lxml")

    # Locate the article body
    article = soup.find("div", class_="news_cont_d_wrap")
    if not article:
        article = soup.find("div", class_="zx_xxgk_cont")
    if not article:
        article = soup.body

    # Decompose non-content elements
    for elem in article.find_all(["script", "style", "nav", "iframe", "img"]):
        elem.decompose()

    full_text = article.get_text(separator="\n", strip=True)

    # Split into paragraphs
    paragraphs = [p.strip() for p in full_text.split("\n") if p.strip() and len(p.strip()) > 20]

    rows = []

    # ------------------------------------------------------------------
    # Row 1: GDP total — section 一、综合
    # ------------------------------------------------------------------
    gdp_pattern = re.compile(
        r"(?:深圳)?地区生产总值\s*([0-9,\.]+)\s*亿元.*?增长\s*([0-9,\.]+)%"
    )
    for p in paragraphs:
        m = gdp_pattern.search(p)
        if m:
            rows.append({
                "indicator": "地区生产总值(GDP)",
                "period": str(YEAR),
                "value": float(m.group(1).replace(",", "")),
                "unit": "亿元",
                "comparison_basis": "当年价格",
                "context_quote": p[:200],
                "source_url": BULLETIN_URL,
                "locator": "一、综合",
                "extraction_method": "beautifulsoup + regex on prose paragraph",
                "confidence": 0.97,
            })
            break

    # ------------------------------------------------------------------
    # Row 2: GDP growth rate
    # ------------------------------------------------------------------
    gdp_growth_pattern = re.compile(r"地区生产总值\s*[0-9,\.]+\s*亿元.*?增长\s*([0-9,\.]+)%")
    for p in paragraphs:
        m = gdp_growth_pattern.search(p)
        if m:
            rows.append({
                "indicator": "地区生产总值(GDP)增速",
                "period": str(YEAR),
                "value": float(m.group(1)),
                "unit": "%",
                "comparison_basis": "可比价格",
                "context_quote": p[:200],
                "source_url": BULLETIN_URL,
                "locator": "一、综合",
                "extraction_method": "beautifulsoup + regex on prose paragraph",
                "confidence": 0.97,
            })
            break

    # ------------------------------------------------------------------
    # Row 3: Permanent resident population
    # ------------------------------------------------------------------
    pop_pattern = re.compile(r"年末常住人口\s*([0-9,\.]+)\s*万人")
    for p in paragraphs:
        m = pop_pattern.search(p)
        if m:
            rows.append({
                "indicator": "常住人口",
                "period": f"{YEAR}年末",
                "value": float(m.group(1).replace(",", "")),
                "unit": "万人",
                "comparison_basis": None,
                "context_quote": p[:200],
                "source_url": BULLETIN_URL,
                "locator": "一、综合",
                "extraction_method": "beautifulsoup + regex on prose paragraph",
                "confidence": 0.97,
            })
            break

    # ------------------------------------------------------------------
    # Row 4: Fixed asset investment growth
    # ------------------------------------------------------------------
    inv_pattern = re.compile(r"固定资产投资.*?增长\s*([0-9,\.]+)%")
    for p in paragraphs:
        m = inv_pattern.search(p)
        if m:
            rows.append({
                "indicator": "固定资产投资增速",
                "period": str(YEAR),
                "value": float(m.group(1)),
                "unit": "%",
                "comparison_basis": None,
                "context_quote": p[:200],
                "source_url": BULLETIN_URL,
                "locator": "六、固定资产投资",
                "extraction_method": "beautifulsoup + regex on prose paragraph",
                "confidence": 0.95,
            })
            break

    # ------------------------------------------------------------------
    # Row 5: Total retail sales of consumer goods
    # ------------------------------------------------------------------
    retail_pattern = re.compile(r"社会消费品零售总额\s*([0-9,\.]+)\s*亿元.*?增长\s*([0-9,\.]+)%")
    for p in paragraphs:
        m = retail_pattern.search(p)
        if m:
            rows.append({
                "indicator": "社会消费品零售总额",
                "period": str(YEAR),
                "value": float(m.group(1).replace(",", "")),
                "unit": "亿元",
                "comparison_basis": "当年价格",
                "context_quote": p[:200],
                "source_url": BULLETIN_URL,
                "locator": "五、国内贸易",
                "extraction_method": "beautifulsoup + regex on prose paragraph",
                "confidence": 0.95,
            })
            break

    # ------------------------------------------------------------------
    # Row 6: Total foreign trade (imports + exports)
    # ------------------------------------------------------------------
    trade_pattern = re.compile(r"货物进出口总额\s*([0-9,\.]+)\s*亿元.*?增长\s*([0-9,\.]+)%")
    for p in paragraphs:
        m = trade_pattern.search(p)
        if m:
            rows.append({
                "indicator": "货物进出口总额",
                "period": str(YEAR),
                "value": float(m.group(1).replace(",", "")),
                "unit": "亿元",
                "comparison_basis": "当年价格",
                "context_quote": p[:200],
                "source_url": BULLETIN_URL,
                "locator": "七、对外经济",
                "extraction_method": "beautifulsoup + regex on prose paragraph",
                "confidence": 0.95,
            })
            break

    # ------------------------------------------------------------------
    # Row 7: Per capita GDP
    # ------------------------------------------------------------------
    percap_pattern = re.compile(r"人均地区生产总值\s*([0-9,\.]+)\s*元")
    for p in paragraphs:
        m = percap_pattern.search(p)
        if m:
            rows.append({
                "indicator": "人均地区生产总值",
                "period": str(YEAR),
                "value": float(m.group(1).replace(",", "")),
                "unit": "元",
                "comparison_basis": "当年价格",
                "context_quote": p[:200],
                "source_url": BULLETIN_URL,
                "locator": "一、综合",
                "extraction_method": "beautifulsoup + regex on prose paragraph",
                "confidence": 0.95,
            })
            break

    # ------------------------------------------------------------------
    # Row 8: General public budget revenue
    # ------------------------------------------------------------------
    fiscal_pattern = re.compile(r"地方一般公共预算收入\s*([0-9,\.]+)\s*亿元.*?(?:增长|下降)\s*([0-9,\.]+)%")
    for p in paragraphs:
        m = fiscal_pattern.search(p)
        if m:
            rows.append({
                "indicator": "地方一般公共预算收入",
                "period": str(YEAR),
                "value": float(m.group(1).replace(",", "")),
                "unit": "亿元",
                "comparison_basis": "当年价格",
                "context_quote": p[:200],
                "source_url": BULLETIN_URL,
                "locator": "八、财政金融",
                "extraction_method": "beautifulsoup + regex on prose paragraph",
                "confidence": 0.97,
            })
            break

    return rows


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", type=Path, default=CACHE_PATH,
                        help="Local HTML sample (default = cached sample.html)")
    parser.add_argument("--out", type=Path, default=OUTPUT_DIR / "extracted.json",
                        help="Output JSON path (default = data/extracts/.../extracted.json)")
    args = parser.parse_args()

    # 1. Load / fetch
    if not args.input.exists():
        print(f"FATAL: 输入 HTML 不存在: {args.input}", file=sys.stderr)
        return 2
    html_bytes = args.input.read_bytes()

    # 2. SHA-256
    file_hash = compute_sha256(html_bytes)

    # 3. Extract
    rows = extract_statistics(html_bytes)

    # 4. Build output — fetched_at 锁定保证 deterministic rebuild（per directive 四-1）
    output = {
        "sample": {
            "city": CITY,
            "year": YEAR,
            "source_url": BULLETIN_URL,
            "source_type": SOURCE_TYPE,
            "file_hash_sha256": file_hash,
            "file_name": args.input.name,
            "file_size_bytes": len(html_bytes),
            "page_or_section_locator": "sz.gov.cn government bulletin HTML",
            "fetched_at": "2026-04-01T00:00:00Z",
            "extraction_method": "beautifulsoup + section-aware regex on prose",
        },
        "rows": rows,
    }

    # 5. Write output
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(output, ensure_ascii=False, indent=2))
    print(f"[INFO] Wrote {len(rows)} rows to {args.out}")

    # 6. Print summary
    print("\nExtracted statistics:")
    for r in rows:
        print(f"  [{r['locator']}] {r['indicator']}: {r['value']} {r['unit']}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
