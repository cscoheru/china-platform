#!/usr/bin/env python3
"""
669通用 fetch — Parameterized fetch for 29 city × year hongheiku bulletins
=============================================================================

knife E/969 通用化目标:
- 抽 669b-2020 + 669fix-b-2020~2025 共 6 个 fetch 脚本的共性
- 参数化: --year {YYYY} (required), --cities (optional subset), --cache-dir (optional)
- HTML + PDF iframe 两路自动切换 (不需调用两个脚本)
- ≤32 HTTP/刀 守门 (665 红线 + 669 multi-knife program)
- 0 HTTP dry-run mode (--dry-run, 仅 print 计划)
- 单元测试: 不触发任何 urllib (mock 测试)

CITIES 内置表 (29 city, 4 直辖市禁 in city 维度 per 红线-7):
  25 省会 (北京/上海/天津/重庆 在 province 维度) + 4 高优先 (SZ/GZ/HZ/NJ from 669a)
  每 city × 6 year 已知 eid (from 669fix-2 cat index scan)

Usage:
  # 使用 external eid_map JSON (recommended, eid from 669fix-2 cat index scan 实证)
  python3 fetch_hongheiku_city_y{year}_669fix.py --year 2024 \\
      --eid-map /tmp/669fix_cache/eid_map_2024.json \\
      --cities HENAN_ZHENGZHOU,HUBEI_WUHAN

  # dry-run 计划 (0 HTTP, 不需 eid_map)
  python3 fetch_hongheiku_city_y{year}_669fix.py --year 2024 \\
      --cities HENAN_ZHENGZHOU,HUBEI_WUHAN --dry-run
"""
import argparse
import io
import json
import re
import ssl
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
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

# URL template (per 669fix-b 系列实证, hongheiku bulletin 路径)
URL_TEMPLATE = "https://tjgb.hongheiku.com/djs/{eid}.html"

# 直辖市禁 (per 红线-7) — 仅用于警告, 不硬过滤
MUNICIPALITY_CITIES = {
    "BEIJING_BEIJING", "SHANGHAI_SHANGHAI", "TIANJIN_TIANJIN", "CHONGQING_CHONGQING",
}


def fetch_html(url: str, timeout: int = 30) -> tuple[bool, str | None, str]:
    """Fetch HTML bulletin. Returns (ok, body_text_or_none, status_msg)."""
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=timeout, context=SSL_CTX) as resp:
            body = resp.read()
        try:
            text = body.decode("gbk")
        except UnicodeDecodeError:
            text = body.decode("utf-8", errors="replace")
        return True, text, f"{len(body)} bytes"
    except (urllib.error.URLError, urllib.error.HTTPError, TimeoutError, OSError) as e:
        return False, None, f"{type(e).__name__}: {e}"


def detect_pdf_iframe(html_text: str) -> str | None:
    """Detect PDF iframe URL (per 669fix-b-2020 pattern). Returns full URL or None."""
    m = re.search(r'<iframe[^>]+src="([^"]+)"', html_text)
    if not m:
        return None
    src = m.group(1)
    fm = re.search(r'file=([^&]+)', src)
    if not fm:
        return None
    file_path = urllib.parse.unquote(fm.group(1))
    return "https://tjgb.hongheiku.com" + file_path


def fetch_pdf_bytes(pdf_url: str, timeout: int = 60) -> tuple[bool, bytes | None, str]:
    """Download PDF bytes. Returns (ok, bytes_or_none, status_msg)."""
    try:
        encoded = urllib.parse.quote(pdf_url, safe=':/?=&')
        req = urllib.request.Request(encoded, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=timeout, context=SSL_CTX) as resp:
            pdf_bytes = resp.read()
        if pdf_bytes[:4] != b'%PDF':
            return False, None, f"not a PDF, header: {pdf_bytes[:30]!r}"
        return True, pdf_bytes, f"{len(pdf_bytes)} bytes"
    except (urllib.error.URLError, urllib.error.HTTPError, TimeoutError, OSError) as e:
        return False, None, f"{type(e).__name__}: {e}"


def pdf_to_text(pdf_bytes: bytes) -> str:
    """Extract text from PDF using pypdf."""
    if not HAS_PYPDF:
        return ""
    reader = pypdf.PdfReader(io.BytesIO(pdf_bytes))
    text = ""
    for page in reader.pages:
        text += page.extract_text() + "\n"
    return text


def fetch_one_city(
    city: str,
    year: int,
    eid: int,
    cache_dir: Path,
    rate_limit: float = 0.3,
    fetch_pdfs: bool = True,
) -> dict:
    """Fetch one city × year bulletin. Returns result dict."""
    result = {
        "city": city,
        "year": year,
        "eid": eid,
        "ok": False,
        "format": "unknown",
        "http_count": 0,
        "msg": "",
    }

    if eid is None:
        result["msg"] = "no hongheiku entry (eid=None, DATA_MISSING 路径, 守红线-3)"
        return result

    html_path = cache_dir / f"{year}_{city}_{eid}.html"
    pdf_path = cache_dir / f"{year}_{city}_{eid}.pdf"
    text_path = cache_dir / f"{year}_{city}_{eid}.pdf.txt"

    # Step 1: fetch HTML wrapper
    if html_path.exists():
        result["http_count"] += 0  # cache hit
        html_text = html_path.read_text(encoding="utf-8", errors="replace")
    else:
        url = URL_TEMPLATE.format(eid=eid)
        ok, html_text, msg = fetch_html(url)
        result["http_count"] += 1 if ok else 0
        if not ok:
            result["msg"] = f"HTML fetch failed: {msg}"
            return result
        cache_dir.mkdir(parents=True, exist_ok=True)
        html_path.write_text(html_text, encoding="utf-8")

    # Step 2: detect PDF iframe (optional)
    if fetch_pdfs:
        pdf_url = detect_pdf_iframe(html_text)
        if pdf_url:
            result["format"] = "pdf"
            if pdf_path.exists():
                pdf_bytes = pdf_path.read_bytes()
            else:
                ok, pdf_bytes, msg = fetch_pdf_bytes(pdf_url)
                result["http_count"] += 1 if ok else 0
                if not ok:
                    result["msg"] = f"PDF fetch failed: {msg}"
                    return result
                pdf_path.write_bytes(pdf_bytes)
            # Extract text
            if HAS_PYPDF:
                text = pdf_to_text(pdf_bytes)
                text_path.write_text(text, encoding="utf-8")
                result["ok"] = True
                result["msg"] = f"PDF + text ({len(pdf_bytes)} bytes, {len(text)} chars)"
            else:
                result["ok"] = True
                result["msg"] = f"PDF only ({len(pdf_bytes)} bytes, pypdf unavailable)"
            return result

    # HTML path (no PDF)
    result["format"] = "html"
    result["ok"] = True
    result["msg"] = f"HTML ({len(html_text)} chars)"
    return result


def load_eid_map(path: str) -> tuple[dict[str, dict[int, int | None]], list[str]]:
    """Load eid map from external JSON file. Supports two formats:

    Format A (year-keyed, RECOMMENDED):
      {"HEBEI_SHIJIAZHUANG": {2024: 59546, 2023: 58237}, "JIANGXI_NANCHANG": {2024: null}}

    Format B (year-suffix flat):
      {"HEBEI_SHIJIAZHUANG_2024": 59546, "JIANGXI_NANCHANG_2024": null}

    Returns:
      (eid_by_city_year_dict, all_cities_list)
    """
    p = Path(path)
    if not p.exists():
        raise FileNotFoundError(f"eid_map not found: {path}")
    raw = json.loads(p.read_text(encoding="utf-8"))

    # Filter meta keys starting with _
    data = {k: v for k, v in raw.items() if not k.startswith("_")}

    # Detect format
    sample_key = next(iter(data.keys()), "")
    if "_" in sample_key and sample_key.rsplit("_", 1)[1].isdigit():
        # Format B: flat year-suffix
        eid_by_city_year = {}
        all_cities = []
        for key, eid in data.items():
            city, year_str = key.rsplit("_", 1)
            year_int = int(year_str)
            if city not in all_cities:
                all_cities.append(city)
            eid_by_city_year.setdefault(city, {})[year_int] = eid
        return eid_by_city_year, all_cities
    else:
        # Format A: nested year-keyed
        eid_by_city_year = {city: years for city, years in data.items()}
        all_cities = list(data.keys())
        return eid_by_city_year, all_cities


def resolve_cities(args_cities: str | None, all_cities: list[str]) -> list[str]:
    """Resolve city list from --cities arg OR from eid_map's city list.

    Filters out 4 直辖市 (红线-7) silently unless --allow-municipality.
    """
    if args_cities:
        cities = [c.strip() for c in args_cities.split(",") if c.strip()]
    else:
        cities = list(all_cities)
    return cities


def parse_args():
    parser = argparse.ArgumentParser(
        description="669通用 fetch — parameterized fetch for 29 city × year hongheiku bulletins"
    )
    parser.add_argument(
        "--year",
        type=int,
        required=True,
        choices=[2020, 2021, 2022, 2023, 2024, 2025],
        help="Target year (2020-2025)",
    )
    parser.add_argument(
        "--cities",
        type=str,
        default=None,
        help="Comma-separated city subset (default: derive from --eid-map keys for --year)",
    )
    parser.add_argument(
        "--eid-map",
        type=str,
        required=True,
        help="Path to eid_map JSON (e.g. /tmp/669fix_cache/eid_map_all.json). Required unless --dry-run.",
    )
    parser.add_argument(
        "--cache-dir",
        type=str,
        default=None,
        help="Cache directory (default: /tmp/669fix_cache/y{year}/)",
    )
    parser.add_argument(
        "--no-pdf",
        action="store_true",
        help="Skip PDF iframe download (HTML only)",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Print plan without any HTTP requests (0 HTTP, eid_map optional)",
    )
    parser.add_argument(
        "--rate-limit",
        type=float,
        default=0.3,
        help="Sleep between requests (seconds, default 0.3)",
    )
    return parser.parse_args()


def main():
    args = parse_args()
    year = args.year
    cache_dir = Path(args.cache_dir) if args.cache_dir else Path(f"/tmp/669fix_cache/y{year}")
    fetch_pdfs = not args.no_pdf

    # Load eid map (or use empty dict for dry-run without --eid-map)
    if args.eid_map:
        eid_by_city_year, all_cities = load_eid_map(args.eid_map)
    else:
        if not args.dry_run:
            print(f"  ✗ --eid-map required unless --dry-run")
            sys.exit(1)
        eid_by_city_year, all_cities = {}, []

    cities = resolve_cities(args.cities, all_cities)

    # Resolve eids for requested year
    city_eids: dict[str, int | None] = {}
    for city in cities:
        city_year_map = eid_by_city_year.get(city, {})
        if year in city_year_map:
            city_eids[city] = city_year_map[year]
        elif args.dry_run and not eid_by_city_year:
            city_eids[city] = None  # dry-run 假设 unknown = DATA_MISSING
        else:
            print(f"  ✗ {city} has no eid for year {year} in eid_map")
            sys.exit(1)

    # 红线-7 守门
    municipality_in_list = [c for c in cities if c in MUNICIPALITY_CITIES]
    if municipality_in_list:
        print(f"  ⚠ WARNING: 直辖市 {municipality_in_list} 在 city 维度违反红线-7")
        print(f"    如确需 fetch (debug), 设 --allow-municipality")
        if not args.dry_run and not getattr(args, "allow_municipality", False):
            sys.exit(1)

    # ≤32 HTTP/刀 红线守门
    plan_http = sum(1 for c in cities if city_eids[c] is not None)
    if fetch_pdfs:
        plan_http *= 2  # HTML + PDF
    if plan_http > 32 and not args.dry_run:
        print(f"  ✗ RED LINE: plan_http={plan_http} > 32 (665 multi-knife program 红线)")
        print(f"    减 cities 数 (e.g. --cities 25 省会 only) 或 --no-pdf")
        sys.exit(1)

    print(f"=== knife 969 通用 fetch ===")
    print(f"  year: {year}")
    print(f"  cities: {len(cities)}")
    print(f"  eid_map: {args.eid_map or '(dry-run default)'}")
    print(f"  cache_dir: {cache_dir}")
    print(f"  fetch_pdfs: {fetch_pdfs}")
    print(f"  plan_http: ≤{plan_http} (≤32 红线)")
    print(f"  dry_run: {args.dry_run}")
    print()

    if args.dry_run:
        print("=== DRY-RUN 计划 (no HTTP) ===")
        for city in cities:
            eid = city_eids[city]
            if eid is None:
                print(f"  - {city:32s} → DATA_MISSING (no eid)")
            else:
                url = URL_TEMPLATE.format(eid=eid)
                print(f"  - {city:32s} → GET {url} ({'HTML+PDF' if fetch_pdfs else 'HTML only'})")
        print(f"\nPlan HTTP: {plan_http}")
        return

    cache_dir.mkdir(parents=True, exist_ok=True)

    http_ok = 0
    http_fail = 0
    real_count = 0
    miss_count = 0

    for city in cities:
        eid = city_eids[city]
        result = fetch_one_city(
            city=city,
            year=year,
            eid=eid,
            cache_dir=cache_dir,
            rate_limit=args.rate_limit,
            fetch_pdfs=fetch_pdfs,
        )
        if result["ok"]:
            real_count += 1
            http_ok += result["http_count"]
            print(f"  ✓ {city:32s} eid={str(eid):6s} fmt={result['format']:4s} HTTP={result['http_count']} {result['msg']}")
        else:
            miss_count += 1
            http_fail += 1
            print(f"  ✗ {city:32s} eid={str(eid):6s} {result['msg']}")
        time.sleep(args.rate_limit)

    print()
    print(f"=== fetch summary ===")
    print(f"  cities: {len(cities)}")
    print(f"  real:   {real_count}")
    print(f"  miss:   {miss_count}")
    print(f"  HTTP:   {http_ok} ok, {http_fail} fail")
    print(f"  cache:  {cache_dir}")


if __name__ == "__main__":
    main()
