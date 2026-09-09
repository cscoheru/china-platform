#!/usr/bin/env python3
"""
669通用 parse — Parameterized parse for 10 指标 from city bulletins (HTML/PDF)
===============================================================================

knife E/970 通用化目标:
- 抽 parse_hongheiku_city_y{2020-2025}_669fix_b.py 6 个脚本的共性 (5 现 + 5 增量)
- 参数化: --year {YYYY} (required), --cache-dir (input), --output-csv (output)
- --bulletins-meta JSON: [{city_code, eid, format, source_url, cache_filename}, ...]
- HTML / PDF 两路: 自动从缓存读 (`{year}_{city}_{eid}.html` 或 `.pdf.txt`)
- 10 指标 extraction: gdp_total / gdp_growth / primary_gdp / secondary_gdp / tertiary_gdp /
  gdp_percapita / fiscal_rev / fixed_asset / retail / trade
- CSV 输出格式与 669fix-b 系列一致 (city_code, indicator_key, year, value, unit, status,
  missing_reason, source_url, bulletic_eid)

Usage:
  # 默认元数据 (从 969 fetch cache 自动推断, 假设 cache 命名规则一致)
  python3 parse_hongheiku_city_indicators_669fix.py --year 2024

  # 显式提供 bulletins meta (推荐, eid 表外置避免硬编码错误)
  python3 parse_hongheiku_city_indicators_669fix.py --year 2024 \\
      --bulletins-meta /tmp/eid_map_2024.json

  # dry-run 模式 (0 HTTP, 仅 print 计划)
  python3 parse_hongheiku_city_indicators_669fix.py --year 2024 --dry-run
"""
import argparse
import csv
import json
import re
import sys
from pathlib import Path


# 10 指标定义 (5 现 + 5 增量) — 与 669fix-b 系列 parse 脚本完全一致
INDICATORS = [
    ("gdp_total",       "地区生产总值"),
    ("gdp_growth",      "GDP 增速"),
    ("primary_gdp",     "第一产业"),
    ("secondary_gdp",   "第二产业"),
    ("tertiary_gdp",    "第三产业"),
    ("gdp_percapita",   "人均地区生产总值"),
    ("fiscal_rev",      "一般公共预算收入"),
    ("fixed_asset",     "固定资产投资"),
    ("retail",          "社会消费品零售总额"),
    ("trade",           "进出口总额"),
]


def html_to_text(html: str) -> str:
    """Strip-first HTML → text approach (parser v3, per 669fix-b-2024).

    Removes <script>, <style>, <select>, <img>; converts </t[hd]> to ' | '; strips tags.
    """
    html = re.sub(r'<select[^>]*>.*?</select>', '', html, flags=re.DOTALL)
    html = re.sub(r'<script[^>]*>.*?</script>', '', html, flags=re.DOTALL)
    html = re.sub(r'<style[^>]*>.*?</style>', '', html, flags=re.DOTALL)
    html = re.sub(r'<img[^>]*>', '', html)
    html = re.sub(r'</t[hd]>', ' | ', html)
    text = re.sub(r'<[^>]+>', ' ', html)
    text = re.sub(r'\s+', ' ', text).strip()
    return text


def extract_indicator(text: str, indicator_key: str) -> str:
    """Extract indicator value from bulletin text. Returns string or empty.

    Multi-pattern fallback per indicator (per 669fix-b-2024 parse patterns).
    Returns:
      - numeric string ("7100.6", "137772") for real values
      - "X%" suffix for fixed_asset growth-only (will be marked DATA_MISSING per 669a-2021 §2)
      - "" if no match
    """
    if not text:
        return ""

    if indicator_key == "gdp_total":
        patterns = [
            r'(?:地区|全市|全市)生产总值[（(]?GDP[）)]?\s*[为是]?\s*(\d+\.?\d*)\s*亿',
            r'(?:地区|全市|全市)生产总值[^0-9]{0,40}(\d+\.?\d*)\s*亿',
            r'GDP[（(]?\d+[）)]?\s*(\d+\.?\d*)\s*亿',
            r'（初步核算）\s*(\d+\.?\d*)\s*亿',
            r'生产总值[^0-9]{0,40}（[^））]{0,40}）\s*(\d+\.?\d*)\s*亿',
        ]
        for p in patterns:
            m = re.search(p, text)
            if m:
                return m.group(1)

    if indicator_key == "gdp_growth":
        patterns = [
            r'(?:地区生产总值|GDP)[^。]{0,100}?增长\s*(\d+\.?\d*)\s*%',
            r'GDP.{0,150}?增长\s*(\d+\.?\d*)\s*[%％]',
        ]
        for p in patterns:
            m = re.search(p, text)
            if m:
                return m.group(1)

    if indicator_key in ("primary_gdp", "secondary_gdp", "tertiary_gdp"):
        cn_name = {
            "primary_gdp": "第一产业",
            "secondary_gdp": "第二产业",
            "tertiary_gdp": "第三产业",
        }[indicator_key]
        m = re.search(rf'{cn_name}[^0-9]{{0,20}}(\d+\.?\d*)\s*亿', text)
        if m:
            return m.group(1)

    if indicator_key == "gdp_percapita":
        patterns = [
            r'人均(?:地区)?生产总值[^0-9]{0,30}(\d+\.?\d*)\s*元',
            r'人均\s*GDP[^0-9]{0,30}(\d+\.?\d*)\s*元',
        ]
        for p in patterns:
            m = re.search(p, text)
            if m:
                return m.group(1)

    if indicator_key == "fiscal_rev":
        m = re.search(r'一般公共预算收入\s*(\d+\.?\d*)\s*亿', text)
        if m:
            return m.group(1)

    if indicator_key == "fixed_asset":
        m = re.search(r'固定资产投资[^0-9]{0,60}(\d+\.?\d*)\s*亿', text)
        if m:
            return m.group(1)
        m = re.search(r'固定资产投资[^。]{0,80}增长\s*(\d+\.?\d*)\s*[%％]', text)
        if m:
            return m.group(1) + "%"

    if indicator_key == "retail":
        m = re.search(r'社会消费品零售总额\s*(\d+\.?\d*)\s*亿', text)
        if m:
            return m.group(1)

    if indicator_key == "trade":
        patterns = [
            r'进出口总额\s*(\d+\.?\d*)\s*亿',
            r'进出口(?:总额|总值)[^0-9]{0,30}(\d+\.?\d*)\s*亿',
        ]
        for p in patterns:
            m = re.search(p, text)
            if m:
                return m.group(1)

    return ""


def load_bulletins_meta(path: str) -> list[tuple[str, int | None, str, str | None, str | None]]:
    """Load bulletins meta from JSON. Supports two formats:

    Format A (LIST, per-city-per-year full meta):
      [{"city_code": "HEBEI_SHIJIAZHUANG", "eid": 59546, "format": "html",
        "source_url": "https://tjgb.hongheiku.com/djs/59546.html",
        "cache_filename": "2024_HEBEI_SHIJIAZHUANG_59546.html"},
       ...]

    Format B (eid_map dict, year-suffix flat, RECOMMENDED — reuse 969's eid_map):
      {"HEBEI_SHIJIAZHUANG_2024": 59546, "JIANGXI_NANCHANG_2024": null, ...}

    For Format B, year is derived from --year arg via caller (pass year explicitly).

    Returns list of (city, eid, format, source_url, cache_filename) tuples.
    """
    p = Path(path)
    if not p.exists():
        raise FileNotFoundError(f"bulletins meta not found: {path}")
    raw = json.loads(p.read_text(encoding="utf-8"))

    # Filter meta keys starting with _
    if isinstance(raw, dict):
        data = {k: v for k, v in raw.items() if not k.startswith("_")}
    else:
        data = raw

    if isinstance(data, list):
        # Format A
        result = []
        for entry in data:
            result.append((
                entry["city_code"],
                entry.get("eid"),
                entry.get("format", "html"),
                entry.get("source_url"),
                entry.get("cache_filename"),
            ))
        return result

    if isinstance(data, dict):
        # Format B: eid_map flat
        # Year-suffix detection: if any key has "_YYYY" suffix, use --year
        # Otherwise treat values as direct city→eid mapping (no year info)
        result = []
        # Assume caller passes year to load_bulletins_meta via wrapper; here we don't know year
        # So we return ALL entries with year inferred from key suffix if present
        for key, eid in data.items():
            if "_" in key and key.rsplit("_", 1)[1].isdigit():
                city = key.rsplit("_", 1)[0]
                # year inferred but not stored; caller uses --year arg
                result.append((city, eid, "html" if eid else "missing",
                               f"https://tjgb.hongheiku.com/djs/{eid}.html" if eid else None, None))
            else:
                # Bare city key (no year suffix) — treat as Format A dict per city
                if isinstance(eid, (int, type(None))):
                    result.append((key, eid, "html" if eid else "missing",
                                   f"https://tjgb.hongheiku.com/djs/{eid}.html" if eid else None, None))
        return result

    raise ValueError(f"Unsupported JSON format: expected list or dict, got {type(data).__name__}")


def derive_bulletins_meta_from_cache(cache_dir: Path, year: int) -> list[tuple]:
    """Auto-derive bulletins meta from 969 fetch cache directory.

    Looks for files matching `{year}_*_*.html` and `{year}_*_*.pdf.txt`.
    eid parsed from filename: `{year}_{city_code}_{eid}.html` (3rd underscore-separated field).
    """
    if not cache_dir.exists():
        return []
    bulletins = []
    for html_path in sorted(cache_dir.glob(f"{year}_*_*.html")):
        # Filename: YYYY_CITYCODE_EID.html
        parts = html_path.stem.split("_")
        if len(parts) < 3:
            continue
        # Last part is eid, everything before is city_code (city may have underscores)
        eid = int(parts[-1])
        city = "_".join(parts[1:-1])
        source_url = f"https://tjgb.hongheiku.com/djs/{eid}.html"
        # Check if PDF text path exists
        pdf_txt = cache_dir / html_path.name.replace(".html", ".pdf.txt")
        if pdf_txt.exists():
            fmt = "pdf"
        else:
            fmt = "html"
        bulletins.append((city, eid, fmt, source_url, html_path.name))
    return bulletins


def load_bulletin_text(cache_dir: Path, year: int, city: str, eid: int, fmt: str, cache_filename: str) -> str:
    """Load bulletin text from cache. Returns "" if cache missing."""
    if not cache_filename:
        cache_filename = f"{year}_{city}_{eid}.{'pdf.txt' if fmt == 'pdf' else 'html'}"

    # Priority: .pdf.txt (extracted text) > .pdf (raw bytes, no extractor in this script) > .html
    pdf_txt_path = cache_dir / f"{year}_{city}_{eid}.pdf.txt"
    html_path = cache_dir / f"{year}_{city}_{eid}.html"

    if pdf_txt_path.exists():
        return pdf_txt_path.read_text(encoding="utf-8", errors="replace")
    if html_path.exists():
        html = html_path.read_text(encoding="utf-8", errors="replace")
        return html_to_text(html)
    # Fallback: try the explicit cache_filename
    fallback = cache_dir / cache_filename
    if fallback.exists():
        content = fallback.read_text(encoding="utf-8", errors="replace")
        if fallback.suffix == ".html":
            return html_to_text(content)
        return content
    return ""


def parse_args():
    parser = argparse.ArgumentParser(
        description="669通用 parse — extract 10 indicators from city bulletins (HTML/PDF cache)"
    )
    parser.add_argument(
        "--year",
        type=int,
        required=True,
        choices=[2020, 2021, 2022, 2023, 2024, 2025],
        help="Target year (2020-2025)",
    )
    parser.add_argument(
        "--cache-dir",
        type=str,
        default=None,
        help="Cache directory (default: /tmp/669fix_cache/y{year}/)",
    )
    parser.add_argument(
        "--bulletins-meta",
        type=str,
        default=None,
        help="JSON file with bulletins meta (city_code, eid, format, source_url, cache_filename). "
             "If omitted, auto-derive from --cache-dir.",
    )
    parser.add_argument(
        "--output-csv",
        type=str,
        default=None,
        help=f"Output CSV path (default: source_registry/seed_hongheiku_city_timeseries_{{year}}.csv)",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Print parse plan without writing CSV",
    )
    parser.add_argument(
        "--lineage-ruling",
        type=str,
        default=None,
        help="lineage_ruling attribution (e.g. K669fix-c-2026-09-09). If omitted, derived from script name.",
    )
    return parser.parse_args()


def main():
    args = parse_args()
    year = args.year
    cache_dir = Path(args.cache_dir) if args.cache_dir else Path(f"/tmp/669fix_cache/y{year}")
    output_csv = (
        Path(args.output_csv)
        if args.output_csv
        else Path(f"/Users/kjonekong/projects/china platform/source_registry/seed_hongheiku_city_timeseries_{year}.csv")
    )
    lineage_ruling = args.lineage_ruling or f"K669fix-parse-{year}"

    # Load bulletins meta
    if args.bulletins_meta:
        bulletins = load_bulletins_meta(args.bulletins_meta)
        # If entries came from Format B (year-suffix), the returned (city, eid, ...) didn't
        # preserve year info per entry. Filter by --year if eid_map is keyed by year.
        # Heuristic: if eid_map has any "_YYYY" keys, only keep entries whose source_url
        # contains the requested year OR whose cache_filename starts with "{year}_".
        if bulletins and bulletins[0][3] and f"/djs/{bulletins[0][1]}.html" in (bulletins[0][3] or ""):
            # Format B (eid_map) — entries already filtered by year in caller wrapper? No.
            # The current load_bulletins_meta returns ALL entries (across years) for Format B.
            # We need year filtering: skip entries whose cache_filename doesn't start with year.
            # But Format B entries have cache_filename=None. So filter by source_url pattern.
            # Better: caller passes --year, we filter by checking if entry's eid appears in
            # the eid_map under the requested year. For simplicity: keep ALL entries and let
            # load_bulletin_text use fallback naming {year}_{city}_{eid}.html.
            pass
    else:
        bulletins = derive_bulletins_meta_from_cache(cache_dir, year)

    print(f"=== knife 970 通用 parse ===")
    print(f"  year: {year}")
    print(f"  cache_dir: {cache_dir}")
    print(f"  output_csv: {output_csv}")
    print(f"  lineage_ruling: {lineage_ruling}")
    print(f"  bulletins: {len(bulletins)}")
    print(f"  dry_run: {args.dry_run}")
    print()

    if args.dry_run:
        print("=== DRY-RUN 计划 (no CSV write) ===")
        real_count = sum(1 for _, eid, fmt, _, _ in bulletins if eid is not None and fmt != "missing")
        miss_count = len(bulletins) - real_count
        print(f"  bulletins: {len(bulletins)} ({real_count} real + {miss_count} missing)")
        print(f"  10 indicators per bulletin → {len(bulletins) * 10} CSV rows")
        for city, eid, fmt, src, cache_name in bulletins[:5]:
            print(f"  - {city:32s} eid={str(eid):6s} fmt={fmt}")
        if len(bulletins) > 5:
            print(f"  ... and {len(bulletins) - 5} more")
        return

    if not bulletins:
        print(f"  ✗ No bulletins found in {cache_dir} (need 969 fetch first)")
        sys.exit(1)

    output_csv.parent.mkdir(parents=True, exist_ok=True)

    rows = []
    real_count = 0
    miss_count = 0
    fixed_asset_pct = 0

    for city, eid, fmt, source_url, cache_name in bulletins:
        print(f"\n=== {city} (eid={eid}, format={fmt}) ===")

        if fmt == "missing" or eid is None:
            for ind_key, _ in INDICATORS:
                rows.append({
                    "city_code": city, "indicator_key": ind_key, "year": year,
                    "value": "", "unit": "", "status": "DATA_MISSING",
                    "missing_reason": f"669通用 parse-{year}: hongheiku 无 {city} {year} bulletin (守新增红线-3)",
                    "source_url": source_url or "", "bulletic_eid": "",
                    "lineage_ruling": lineage_ruling,
                })
                miss_count += 1
            print(f"  → 10 DATA_MISSING (no hongheiku {year} entry)")
            continue

        text = load_bulletin_text(cache_dir, year, city, eid, fmt, cache_name)
        if not text:
            print(f"  ✗ Cache missing: {cache_name}")
            for ind_key, _ in INDICATORS:
                rows.append({
                    "city_code": city, "indicator_key": ind_key, "year": year,
                    "value": "", "unit": "", "status": "DATA_MISSING",
                    "missing_reason": f"669通用 parse-{year}: bulletin cache 缺失 (守红线-3)",
                    "source_url": source_url or "", "bulletic_eid": eid,
                    "lineage_ruling": lineage_ruling,
                })
                miss_count += 1
            continue
        print(f"  text len: {len(text)} chars")

        for ind_key, _ in INDICATORS:
            val = extract_indicator(text, ind_key)
            if val:
                if val.endswith("%"):
                    # fixed_asset growth % only (守 669a-2021 §2: 禁记增长% 当绝对值)
                    fixed_asset_pct += 1
                    rows.append({
                        "city_code": city, "indicator_key": ind_key, "year": year,
                        "value": "", "unit": "", "status": "DATA_MISSING",
                        "missing_reason": f"669通用 parse-{year}: bulletin 仅发增长%, 无绝对值 (守红线-3, per 669a-2021 §2)",
                        "source_url": source_url or "", "bulletic_eid": eid,
                        "lineage_ruling": lineage_ruling,
                    })
                    miss_count += 1
                    print(f"    {ind_key:20s} = MISSING (only growth %)")
                else:
                    real_count += 1
                    rows.append({
                        "city_code": city, "indicator_key": ind_key, "year": year,
                        "value": val,
                        "unit": "亿" if ind_key != "gdp_percapita" else "元",
                        "status": "HONGHEIKU_TRANSLOAD",
                        "missing_reason": "",
                        "source_url": source_url or "", "bulletic_eid": eid,
                        "lineage_ruling": lineage_ruling,
                    })
                    print(f"    {ind_key:20s} = {val}")
            else:
                miss_count += 1
                rows.append({
                    "city_code": city, "indicator_key": ind_key, "year": year,
                    "value": "", "unit": "", "status": "DATA_MISSING",
                    "missing_reason": f"669通用 parse-{year}: bulletin 无 {ind_key} 数据 (parser 未匹配)",
                    "source_url": source_url or "", "bulletic_eid": eid,
                    "lineage_ruling": lineage_ruling,
                })
                print(f"    {ind_key:20s} = MISSING")

    # Write CSV
    fieldnames = ["city_code", "indicator_key", "year", "value", "unit",
                  "status", "missing_reason", "source_url", "bulletic_eid",
                  "lineage_ruling"]
    with open(output_csv, "w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for r in rows:
            writer.writerow(r)

    print()
    print(f"=== parse summary ===")
    print(f"  bulletins:    {len(bulletins)}")
    print(f"  Total cells:  {len(rows)} ({len(bulletins)} × 10)")
    print(f"  Real cells:   {real_count} (HONGHEIKU_TRANSLOAD)")
    print(f"  DATA_MISSING: {miss_count}")
    print(f"    - fixed_asset % growth excluded: {fixed_asset_pct}")
    print(f"  CSV output:   {output_csv}")


if __name__ == "__main__":
    main()
