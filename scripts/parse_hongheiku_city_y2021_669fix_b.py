#!/usr/bin/env python3
"""
669fix-b-2021 parse — Extract 10 指标 from 21 city bulletins (HTML + PDF)
=============================================================================

knock 669fix-b-2021 sub-knife (Path A 续刀 1/5):
- 20 HTML bulletins: text extraction with parser v3 strip-first
- 1 PDF bulletin (SHAANXI 25636): pypdf-extracted text
- 4 missing (SICHUAN/XIZANG/QINGHAI/TAIWAN): DATA_MISSING

Output: seed_hongheiku_city_timeseries_2021.csv (210-250 rows, 21 city × 10 indicator)
"""
import csv
import re
from pathlib import Path

CACHE_DIR = Path("/tmp/669b")
OUT_CSV = Path("/Users/kjonekong/projects/china platform/source_registry/seed_hongheiku_city_timeseries_2021.csv")

# 21 city with eid + format (25 省会 - 4 missing)
CITY_BULLETINS = [
    # (city_code, eid, format, source_url)
    ("HEBEI_SHIJIAZHUANG",       24600,  "html",      "https://tjgb.hongheiku.com/djs/24600.html"),
    ("SHANXI_TAIYUAN",           24774,  "html",      "https://tjgb.hongheiku.com/djs/24774.html"),
    ("NEIMENGGU_HUHEHAOTE",      25235,  "html",      "https://tjgb.hongheiku.com/djs/25235.html"),
    ("LIAONING_SHENYANG",        27930,  "html",      "https://tjgb.hongheiku.com/djs/27930.html"),
    ("JILIN_CHANGCHUN",          31744,  "html",      "https://tjgb.hongheiku.com/djs/31744.html"),
    ("HEILONGJIANG_HARBIN",      29127,  "html",      "https://tjgb.hongheiku.com/djs/29127.html"),
    ("ANHUI_HEFEI",              25210,  "html",      "https://tjgb.hongheiku.com/djs/25210.html"),
    ("FUJIAN_FUZHOU",            25196,  "html",      "https://tjgb.hongheiku.com/djs/25196.html"),
    ("JIANGXI_NANCHANG",         26554,  "html",      "https://tjgb.hongheiku.com/djs/26554.html"),
    ("SHANDONG_JINAN",           24205,  "html",      "https://tjgb.hongheiku.com/djs/24205.html"),
    ("HENAN_ZHENGZHOU",          25032,  "html",      "https://tjgb.hongheiku.com/djs/25032.html"),
    ("HUBEI_WUHAN",              28733,  "html",      "https://tjgb.hongheiku.com/djs/28733.html"),
    ("HUNAN_CHANGSHA",           25200,  "html",      "https://tjgb.hongheiku.com/djs/25200.html"),
    ("GUANGXI_NANNING",          27984,  "html",      "https://tjgb.hongheiku.com/djs/27984.html"),
    ("HAINAN_HAIKOU",            23898,  "html",      "https://tjgb.hongheiku.com/djs/23898.html"),
    ("SICHUAN_CHENGDU",          None,   "missing",   None),
    ("GUIZHOU_GUIYANG",          27953,  "html",      "https://tjgb.hongheiku.com/djs/27953.html"),
    ("YUNNAN_KUNMING",           31057,  "html",      "https://tjgb.hongheiku.com/djs/31057.html"),
    ("XIZANG_LASA",              None,   "missing",   None),
    ("SHAANXI_XIAN",             25636,  "pdf",       "https://tjgb.hongheiku.com/djs/25636.html"),
    ("GANSU_LANZHOU",            27570,  "html",      "https://tjgb.hongheiku.com/djs/27570.html"),
    ("QINGHAI_XINING",           None,   "missing",   None),
    ("NINGXIA_YINCHUAN",         25485,  "html",      "https://tjgb.hongheiku.com/djs/25485.html"),
    ("XINJIANG_WULUMUQI",        31404,  "html",      "https://tjgb.hongheiku.com/djs/31404.html"),
    ("TAIWAN_TAIPEI",            None,   "missing",   None),
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
    """Strip-first approach (parser v3)."""
    html = re.sub(r'<select[^>]*>.*?</select>', '', html, flags=re.DOTALL)
    html = re.sub(r'<script[^>]*>.*?</script>', '', html, flags=re.DOTALL)
    html = re.sub(r'<style[^>]*>.*?</style>', '', html, flags=re.DOTALL)
    html = re.sub(r'<img[^>]*>', '', html)
    html = re.sub(r'</t[hd]>', ' | ', html)
    text = re.sub(r'<[^>]+>', ' ', html)
    text = re.sub(r'\s+', ' ', text).strip()
    return text


def extract_indicator(text: str, indicator_key: str, indicator_label: str) -> str:
    """Extract indicator value from bulletin text. Returns string or empty."""
    if not text:
        return ""

    if indicator_key == "gdp_total":
        m = re.search(r'(?:地区|全市|全市)生产总值[（(]?GDP[）)]?\s*[为是]?\s*(\d+\.?\d*)\s*亿', text)
        if m:
            return m.group(1)
        m = re.search(r'(?:地区|全市|全市)生产总值[^0-9]{0,40}(\d+\.?\d*)\s*亿', text)
        if m:
            return m.group(1)
        m = re.search(r'GDP[（(]?\d+[）)]?\s*(\d+\.?\d*)\s*亿', text)
        if m:
            return m.group(1)
        # PDF variant: "(初步核算)10688.28 亿元" with footnote markers
        m = re.search(r'（初步核算）\s*(\d+\.?\d*)\s*亿', text)
        if m:
            return m.group(1)
        # Generic PDF variant: 总产值 [N] (XXX) NNN.NN 亿
        m = re.search(r'生产总值[^0-9]{0,40}（[^））]{0,40}）\s*(\d+\.?\d*)\s*亿', text)
        if m:
            return m.group(1)

    if indicator_key == "gdp_growth":
        m = re.search(r'(?:地区生产总值|GDP)[^。]{0,100}?增长\s*(\d+\.?\d*)\s*%', text)
        if m:
            return m.group(1)
        m = re.search(r'GDP.{0,150}?增长\s*(\d+\.?\d*)\s*[%％]', text)
        if m:
            return m.group(1)

    if indicator_key in ("primary_gdp", "secondary_gdp", "tertiary_gdp"):
        cn_name = {"primary_gdp": "第一产业", "secondary_gdp": "第二产业", "tertiary_gdp": "第三产业"}[indicator_key]
        m = re.search(rf'{cn_name}[^0-9]{{0,20}}(\d+\.?\d*)\s*亿', text)
        if m:
            return m.group(1)

    if indicator_key == "gdp_percapita":
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
    fixed_asset_pct = 0

    for city, eid, fmt, source_url in CITY_BULLETINS:
        print(f"\n=== {city} (eid={eid}, format={fmt}) ===")

        if fmt == "missing":
            for ind_key, ind_label in INDICATORS:
                rows.append({
                    "city_code": city, "indicator_key": ind_key, "year": 2021,
                    "value": "", "unit": "", "status": "DATA_MISSING",
                    "missing_reason": "669fix-b-2021: hongheiku tag 页无 2021 bulletin (SICHUAN/XIZANG/QINGHAI/TAIWAN)",
                    "source_url": "", "bulletic_eid": "",
                })
                miss_count += 1
            print(f"  → 10 DATA_MISSING (no hongheiku 2021 entry)")
            continue

        # Get text content
        if fmt == "pdf":
            text_path = CACHE_DIR / f"bulletin_{eid}.pdf.txt"
            if not text_path.exists():
                print(f"  ✗ PDF text missing: {text_path}")
                continue
            text = text_path.read_text(encoding="utf-8", errors="replace")
        else:
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
                if val.endswith("%"):
                    fixed_asset_pct += 1
                    rows.append({
                        "city_code": city, "indicator_key": ind_key, "year": 2021,
                        "value": "", "unit": "", "status": "DATA_MISSING",
                        "missing_reason": "669fix-b-2021: bulletin 仅发增长%, 无绝对值 (守红线-3, per 669a-2021 §2)",
                        "source_url": source_url, "bulletic_eid": eid,
                    })
                    miss_count += 1
                    print(f"    {ind_key:20s} = MISSING (only growth %)")
                else:
                    real_count += 1
                    rows.append({
                        "city_code": city, "indicator_key": ind_key, "year": 2021,
                        "value": val,
                        "unit": "亿" if ind_key != "gdp_percapita" else "元",
                        "status": "HONGHEIKU_TRANSLOAD",
                        "missing_reason": "",
                        "source_url": source_url, "bulletic_eid": eid,
                    })
                    print(f"    {ind_key:20s} = {val}")
            else:
                miss_count += 1
                rows.append({
                    "city_code": city, "indicator_key": ind_key, "year": 2021,
                    "value": "", "unit": "", "status": "DATA_MISSING",
                    "missing_reason": f"669fix-b-2021: bulletin 无 {ind_key} 数据 (parser 未匹配)",
                    "source_url": source_url, "bulletic_eid": eid,
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
    print(f"    - fixed_asset % growth excluded: {fixed_asset_pct}")
    print(f"  CSV output: {OUT_CSV}")


if __name__ == "__main__":
    main()
