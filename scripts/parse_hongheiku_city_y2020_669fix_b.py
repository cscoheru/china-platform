#!/usr/bin/env python3
"""
669fix-b-2020 parse — Extract 10 指标 from 24 city bulletins (HTML + PDF)
=============================================================================

knock 669fix-b-2020 sub-knife:
- 18 HTML bulletins: extract text from article-content section
- 1 HEBEI 1816: extract text from HTML tables
- 4 PDF bulletins (already converted to .pdf.txt): use pypdf-extracted text
- 2 image-only (JIANGXI/SHANXI): DATA_MISSING (no OCR scope)
- 1 TAIWAN: DATA_MISSING (no hongheiku entry)

Output: seed_hongheiku_city_timeseries_2020.csv (220-240 rows, 22-24 city × 10 indicator)
"""
import csv
import re
from pathlib import Path

CACHE_DIR = Path("/tmp/669b")
OUT_CSV = Path("/Users/kjonekong/projects/china platform/source_registry/seed_hongheiku_city_timeseries_2020.csv")

# 25 省会 city with their bulletin eid + content format
CITY_BULLETINS = [
    # (city_code, eid, format, source_url)
    ("HEBEI_SHIJIAZHUANG",       1816,  "html",      "https://tjgb.hongheiku.com/1816.html"),
    ("SHANXI_TAIYUAN",           1260,  "image",     "https://tjgb.hongheiku.com/1260.html"),  # image-only
    ("NEIMENGGU_HUHEHAOTE",        75,  "html",      "https://tjgb.hongheiku.com/75.html"),
    ("LIAONING_SHENYANG",         347,  "html",      "https://tjgb.hongheiku.com/347.html"),
    ("HEILONGJIANG_HARBIN",      9267,  "html",      "https://tjgb.hongheiku.com/9267.html"),
    ("JILIN_CHANGCHUN",         13562,  "html",      "https://tjgb.hongheiku.com/13562.html"),
    ("ANHUI_HEFEI",               719,  "pdf",       "https://tjgb.hongheiku.com/719.html"),
    ("FUJIAN_FUZHOU",            3413,  "html",      "https://tjgb.hongheiku.com/3413.html"),
    ("JIANGXI_NANCHANG",          630,  "image",     "https://tjgb.hongheiku.com/630.html"),  # image-only
    ("SHANDONG_JINAN",           7978,  "html",      "https://tjgb.hongheiku.com/7978.html"),
    ("HENAN_ZHENGZHOU",          1804,  "html",      "https://tjgb.hongheiku.com/1804.html"),
    ("HUBEI_WUHAN",              4553,  "html",      "https://tjgb.hongheiku.com/4553.html"),
    ("HUNAN_CHANGSHA",            327,  "html",      "https://tjgb.hongheiku.com/327.html"),
    ("GUANGXI_NANNING",          7734,  "html",      "https://tjgb.hongheiku.com/7734.html"),
    ("HAINAN_HAIKOU",            1226,  "html",      "https://tjgb.hongheiku.com/1226.html"),
    ("SICHUAN_CHENGDU",          1460,  "pdf",       "https://tjgb.hongheiku.com/1460.html"),
    ("GUIZHOU_GUIYANG",          3174,  "html",      "https://tjgb.hongheiku.com/3174.html"),
    ("YUNNAN_KUNMING",          14086,  "html",      "https://tjgb.hongheiku.com/14086.html"),
    ("XIZANG_LASA",             14174,  "html",      "https://tjgb.hongheiku.com/14174.html"),
    ("SHAANXI_XIAN",             1229,  "html",      "https://tjgb.hongheiku.com/1229.html"),
    ("GANSU_LANZHOU",             949,  "pdf",       "https://tjgb.hongheiku.com/949.html"),
    ("QINGHAI_XINING",          11065,  "pdf",       "https://tjgb.hongheiku.com/11065.html"),
    ("NINGXIA_YINCHUAN",         7796,  "html",      "https://tjgb.hongheiku.com/7796.html"),
    ("XINJIANG_WULUMUQI",         428,  "html",      "https://tjgb.hongheiku.com/428.html"),
    ("TAIWAN_TAIPEI",            None,  "missing",   None),  # no hongheiku entry
]

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
    """Extract article text from HTML bulletin.

    v3 strategy: strip navigation/script/style FIRST, then drop all HTML tags.
    Avoids the article-content non-greedy regex trap where HEBEI-style pages have
    navigation <select> embedded inside article-content and the regex stops at the
    first </div> after navigation.
    """
    # Strip multi-tag blocks that contain no indicator text
    html = re.sub(r'<select[^>]*>.*?</select>', '', html, flags=re.DOTALL)
    html = re.sub(r'<script[^>]*>.*?</script>', '', html, flags=re.DOTALL)
    html = re.sub(r'<style[^>]*>.*?</style>', '', html, flags=re.DOTALL)
    html = re.sub(r'<img[^>]*>', '', html)
    # Convert table cells to pipe-delimited for tabular indicators
    html = re.sub(r'</t[hd]>', ' | ', html)
    # Strip all remaining tags
    text = re.sub(r'<[^>]+>', ' ', html)
    text = re.sub(r'\s+', ' ', text).strip()
    return text


def extract_indicator(text: str, indicator_key: str, indicator_label: str) -> str:
    """Extract indicator value from city bulletin text. Returns string or empty."""
    if not text:
        return ""

    # 1. Primary search: indicator_label near a number
    if indicator_key == "gdp_total":
        # "地区生产总值5935.1亿元" or "全市生产总值10045.72亿元"
        m = re.search(r'(?:地区|全市|全市)生产总值[（(]?GDP[）)]?\s*[为是]?\s*(\d+\.?\d*)\s*亿', text)
        if m:
            return m.group(1)
        m = re.search(r'(?:地区|全市|全市)生产总值[^0-9]{0,20}(\d+\.?\d*)\s*亿', text)
        if m:
            return m.group(1)
        # "GDP 10045.72 亿元"
        m = re.search(r'GDP[（(]?\d+[）)]?\s*(\d+\.?\d*)\s*亿', text)
        if m:
            return m.group(1)

    if indicator_key == "gdp_growth":
        # "比上年增长3.9%" near GDP
        # Look in a context of 200 chars before "增长"
        m = re.search(r'(?:地区生产总值|GDP)[^。]{0,100}?增长\s*(\d+\.?\d*)\s*%', text)
        if m:
            return m.group(1)
        # Fallback: any "GDP" with growth rate
        m = re.search(r'GDP.{0,150}?增长\s*(\d+\.?\d*)\s*[%％]', text)
        if m:
            return m.group(1)

    if indicator_key in ("primary_gdp", "secondary_gdp", "tertiary_gdp"):
        cn_name = {"primary_gdp": "第一产业", "secondary_gdp": "第二产业", "tertiary_gdp": "第三产业"}[indicator_key]
        m = re.search(rf'{cn_name}[^0-9]{{0,20}}(\d+\.?\d*)\s*亿', text)
        if m:
            return m.group(1)

    if indicator_key == "gdp_percapita":
        # "人均地区生产总值" or "人均GDP"
        m = re.search(r'人均(?:地区)?生产总值[^0-9]{0,30}(\d+\.?\d*)\s*元', text)
        if m:
            return m.group(1)
        m = re.search(r'人均\s*GDP[^0-9]{0,30}(\d+\.?\d*)\s*元', text)
        if m:
            return m.group(1)

    if indicator_key == "fiscal_rev":
        m = re.search(r'一般公共预算收入\s*(\d+\.?\d*)\s*亿', text)
        if m:
            return m.group(1)

    if indicator_key == "fixed_asset":
        # Fixed asset: "固定资产投资比上年增长3.5%" (only growth % mode) OR "固定资产投资(不含农户) XXXX亿元"
        m = re.search(r'固定资产投资[^0-9]{0,60}(\d+\.?\d*)\s*亿', text)
        if m:
            return m.group(1)
        m = re.search(r'固定资产投资[^。]{0,80}增长\s*(\d+\.?\d*)\s*[%％]', text)
        if m:
            return m.group(1) + "%"  # mark as growth-only

    if indicator_key == "retail":
        m = re.search(r'社会消费品零售总额\s*(\d+\.?\d*)\s*亿', text)
        if m:
            return m.group(1)

    if indicator_key == "trade":
        # Trade can be 亿美元 or 万元
        m = re.search(r'进出口总额\s*(\d+\.?\d*)\s*亿', text)
        if m:
            return m.group(1)
        m = re.search(r'进出口(?:总额|总值)[^0-9]{0,30}(\d+\.?\d*)\s*亿', text)
        if m:
            return m.group(1)

    return ""


def main():
    OUT_CSV.parent.mkdir(parents=True, exist_ok=True)

    rows = []
    real_count = 0
    miss_count = 0

    for city, eid, fmt, source_url in CITY_BULLETINS:
        print(f"\n=== {city} (eid={eid}, format={fmt}) ===")

        if fmt == "missing":
            # TAIWAN — DATA_MISSING all 10 indicators
            for ind_key, ind_label in INDICATORS:
                rows.append({
                    "city_code": city,
                    "indicator_key": ind_key,
                    "year": 2020,
                    "value": "",
                    "unit": "",
                    "status": "DATA_MISSING",
                    "missing_reason": "669fix-b-2020: hongheiku tag 页无 2020 bulletin (TAIWAN)",
                    "source_url": "",
                    "bulletic_eid": "",
                })
                miss_count += 1
            print(f"  → 10 DATA_MISSING (TAIWAN no entry)")
            continue

        if fmt == "image":
            # Image-only (JIANGXI/SHANXI) — bulletin's content is in image (scanned PDF/image)
            for ind_key, ind_label in INDICATORS:
                rows.append({
                    "city_code": city,
                    "indicator_key": ind_key,
                    "year": 2020,
                    "value": "",
                    "unit": "",
                    "status": "DATA_MISSING",
                    "missing_reason": "669fix-b-2020: bulletin 内容为 image 扫描件,无 OCR 范围 (守红线-3)",
                    "source_url": source_url,
                    "bulletic_eid": eid,
                })
                miss_count += 1
            print(f"  → 10 DATA_MISSING (image-only, OCR out of scope)")
            continue

        # Get text content
        if fmt == "pdf":
            text_path = CACHE_DIR / f"bulletin_{eid}.pdf.txt"
            if not text_path.exists():
                print(f"  ✗ PDF text missing: {text_path}")
                continue
            text = text_path.read_text(encoding="utf-8", errors="replace")
        else:  # html
            html_path = CACHE_DIR / f"bulletin_{eid}.html"
            if not html_path.exists():
                print(f"  ✗ HTML missing: {html_path}")
                continue
            html = html_path.read_text(encoding="utf-8", errors="replace")
            text = html_to_text(html)

        print(f"  text len: {len(text)} chars")

        for ind_key, ind_label in INDICATORS:
            val = extract_indicator(text, ind_key, ind_label)
            if val:
                real_count += 1
                rows.append({
                    "city_code": city,
                    "indicator_key": ind_key,
                    "year": 2020,
                    "value": val,
                    "unit": "亿" if ind_key != "gdp_percapita" else "元",
                    "status": "HONGHEIKU_TRANSLOAD",
                    "missing_reason": "",
                    "source_url": source_url,
                    "bulletic_eid": eid,
                })
                print(f"    {ind_key:20s} = {val}")
            else:
                miss_count += 1
                rows.append({
                    "city_code": city,
                    "indicator_key": ind_key,
                    "year": 2020,
                    "value": "",
                    "unit": "",
                    "status": "DATA_MISSING",
                    "missing_reason": f"669fix-b-2020: bulletin 无 {ind_key} 数据 (parser 未匹配)",
                    "source_url": source_url,
                    "bulletic_eid": eid,
                })
                print(f"    {ind_key:20s} = MISSING")

    # Write CSV
    fieldnames = ["city_code", "indicator_key", "year", "value", "unit",
                  "status", "missing_reason", "source_url", "bulletic_eid"]
    with open(OUT_CSV, "w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for r in rows:
            writer.writerow(r)

    print()
    print(f"=== parse summary ===")
    print(f"  Total cells: {len(rows)} (25 × 10)")
    print(f"  Real cells:  {real_count} (HONGHEIKU_TRANSLOAD)")
    print(f"  DATA_MISSING: {miss_count}")
    print(f"  CSV output: {OUT_CSV}")


if __name__ == "__main__":
    main()
