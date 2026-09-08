#!/usr/bin/env python3
"""
669fix-b-2020 fetch — Download 4 PDF bulletins (PDF iframe format)
==================================================================

knock 669fix-b-2020 sub-knife (25 省会 × 2020):
- 23 HTML bulletins: already cached (12:06 mtime, 24 with JILIN at 13:24)
- 4 PDF iframe bulletins: ANHUI(719)/GANSU(949)/QINGHAI(11065)/SICHUAN(1460)
- 2 image-only (JIANGXI/SHANXI): DATA_MISSING (no OCR scope)
- 1 TAIWAN: DATA_MISSING (no hongheiku entry)

This script only handles the 4 PDF downloads.
Total HTTP: 4 (well under 32 red line).
"""
import re
import io
import ssl
import urllib.request
import urllib.parse
import urllib.error
import time
from pathlib import Path

try:
    import certifi
    SSL_CTX = ssl.create_default_context(cafile=certifi.where())
except ImportError:
    SSL_CTX = ssl.create_default_context()

try:
    import pypdf
    HAS_PYPDF = True
except ImportError:
    HAS_PYPDF = False

PDF_CITY_EIDS = [
    ("ANHUI_HEFEI",        719),
    ("GANSU_LANZHOU",      949),
    ("QINGHAI_XINING",    11065),
    ("SICHUAN_CHENGDU",   1460),
]

CACHE_DIR = Path("/tmp/669b")
HTTP_OK = 0
HTTP_FAIL = 0


def extract_pdf_url_from_iframe(html_text: str) -> str | None:
    """Extract the actual PDF file= path from the pdfjs viewer.php iframe URL."""
    m = re.search(r'<iframe[^>]+src="([^"]+)"', html_text)
    if not m:
        return None
    src = m.group(1)
    fm = re.search(r'file=([^&]+)', src)
    if not fm:
        return None
    file_path = urllib.parse.unquote(fm.group(1))
    return file_path


def fetch_pdf(city: str, eid: int) -> bool:
    """Download PDF for city bulletin; save both HTML wrapper + extracted PDF."""
    global HTTP_OK, HTTP_FAIL

    html_path = CACHE_DIR / f"bulletin_{eid}.html"
    pdf_path = CACHE_DIR / f"bulletin_{eid}.pdf"
    text_path = CACHE_DIR / f"bulletin_{eid}.pdf.txt"

    if not html_path.exists():
        print(f"  ✗ {city:25s} eid={eid:6d} HTML wrapper missing")
        HTTP_FAIL += 1
        return False

    html_text = html_path.read_text(encoding="utf-8", errors="replace")
    pdf_relpath = extract_pdf_url_from_iframe(html_text)
    if not pdf_relpath:
        print(f"  ✗ {city:25s} eid={eid:6d} no <iframe> PDF URL found")
        HTTP_FAIL += 1
        return False

    full_url = "https://tjgb.hongheiku.com" + pdf_relpath
    encoded_url = urllib.parse.quote(full_url, safe=':/?=&')
    print(f"  → {city:25s} eid={eid:6d} PDF: {encoded_url[:80]}...")

    try:
        req = urllib.request.Request(encoded_url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=60, context=SSL_CTX) as resp:
            pdf_bytes = resp.read()
        HTTP_OK += 1

        if pdf_bytes[:4] != b'%PDF':
            print(f"    ✗ not a PDF, header: {pdf_bytes[:30]!r}")
            HTTP_FAIL += 1
            return False

        pdf_path.write_bytes(pdf_bytes)
        print(f"    ✓ PDF saved: {len(pdf_bytes)} bytes")

        # Extract text immediately if pypdf available
        if HAS_PYPDF:
            reader = pypdf.PdfReader(io.BytesIO(pdf_bytes))
            all_text = ""
            for page in reader.pages:
                all_text += page.extract_text() + "\n"
            text_path.write_text(all_text, encoding="utf-8")
            print(f"    ✓ text extracted: {len(all_text)} chars, {len(reader.pages)} pages")
        return True
    except (urllib.error.URLError, urllib.error.HTTPError, TimeoutError, OSError) as e:
        print(f"    ✗ FAILED: {type(e).__name__}: {e}")
        HTTP_FAIL += 1
        return False


def main():
    global HTTP_OK, HTTP_FAIL
    print(f"=== knife 669fix-b-2020 PDF fetch (4 cities, ≤4 HTTP) ===")
    print(f"Output: {CACHE_DIR}/bulletin_{{eid}}.pdf + .pdf.txt")
    print(f"PyPDF available: {HAS_PYPDF}")
    print()

    for city, eid in PDF_CITY_EIDS:
        fetch_pdf(city, eid)
        time.sleep(0.3)

    print()
    print(f"=== fetch summary: {HTTP_OK} ok, {HTTP_FAIL} fail, {HTTP_OK + HTTP_FAIL}/4 HTTP ===")


if __name__ == "__main__":
    main()
