#!/usr/bin/env python3
"""
669fix-b-2022 parse — Extract 10 指标 from 23 city bulletins (HTML)
=============================================================================

knife 669fix-b-2022 sub-knife (Path A 续刀 2/5):
- 23 HTML bulletins: text extraction with parser v3 strip-first
- 0 PDF (all HTML format per city_bulletins_real.json)
- 2 missing (GUANGXI_NANNING + TAIWAN_TAIPEI): DATA_MISSING

Output: seed_hongheiku_city_timeseries_2022.csv (230-250 rows, 23 city × 10 indicator)
"""
import csv
import re
from pathlib import Path

CACHE_DIR = Path("/tmp/669b")
OUT_CSV = Path("/Users/kjonekong/projects/china platform/source_registry/seed_hongheiku_city_timeseries_2022.csv")

# 23 city with eid (25 省会 - GUANGXI_NANNING - TAIWAN_TAIPEI)
CITY_BULLETINS = [
    # (city_code, eid, format, source_url)
    ("HEBEI_SHIJIAZHUANG",       34963,  "html",      "https://tjgb.hongheiku.com/djs/34963.html"),
    ("SHANXI_TAIYUAN",           36740,  "html",      "https://tjgb.hongheiku.com/djs/36740.html"),
    ("NEIMENGGU_HUHEHAOTE",      35499,  "html",      "https://tjgb.hongheiku.com/djs/35499.html"),
    ("LIAONING_SHENYANG",        35417,  "html",      "https://tjgb.hongheiku.com/djs/35417.html"),
    ("JILIN_CHANGCHUN",          39538,  "html",      "https://tjgb.hongheiku.com/djs/39538.html"),
    ("HEILONGJIANG_HARBIN",      37008,  "html",      "https://tjgb.hongheiku.com/djs/37008.html"),
    ("ANHUI_HEFEI",              38447,  "html",      "https://tjgb.hongheiku.com/djs/38447.html"),
    ("FUJIAN_FUZHOU",            36254,  "html",      "https://tjgb.hongheiku.com/djs/36254.html"),
    ("JIANGXI_NANCHANG",         35659,  "html",      "https://tjgb.hongheiku.com/djs/35659.html"),
    ("SHANDONG_JINAN",           36186,  "html",      "https://tjgb.hongheiku.com/djs/36186.html"),
    ("HENAN_ZHENGZHOU",          36348,  "html",      "https://tjgb.hongheiku.com/djs/36348.html"),
    ("HUBEI_WUHAN",              35546,  "html",      "https://tjgb.hongheiku.com/djs/35546.html"),
    ("HUNAN_CHANGSHA",           35823,  "html",      "https://tjgb.hongheiku.com/djs/35823.html"),
    ("GUANGXI_NANNING",          None,   "missing",   None),
    ("HAINAN_HAIKOU",            35096,  "html",      "https://tjgb.hongheiku.com/djs/35096.html"),
    ("SICHUAN_CHENGDU",          35562,  "html",      "https://tjgb.hongheiku.com/djs/35562.html"),
    ("GUIZHOU_GUIYANG",          37610,  "html",      "https://tjgb.hongheiku.com/djs/37610.html"),
    ("YUNNAN_KUNMING",           39200,  "html",      "https://tjgb.hongheiku.com/djs/39200.html"),
    ("XIZANG_LASA",              39048,  "html",      "https://tjgb.hongheiku.com/djs/39048.html"),
    ("SHAANXI_XIAN",             35633,  "html",      "https://tjgb.hongheiku.com/djs/35633.html"),
    ("GANSU_LANZHOU",            42090,  "html",      "https://tjgb.hongheiku.com/djs/42090.html"),
    ("QINGHAI_XINING",           42507,  "html",      "https://tjgb.hongheiku.com/djs/42507.html"),
    ("NINGXIA_YINCHUAN",         36119,  "html",      "https://tjgb.hongheiku.com/djs/36119.html"),
    ("XINJIANG_WULUMUQI",        35583,  "html",      "https://tjgb.hongheiku.com/djs/35583.html"),
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
        m = re.search(r'（初步核算）\s*(\d+\.?\d*)\s*亿', text)
        if m:
            return m.group(1)
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
                    "city_code": city, "indicator_key": ind_key, "year": 2022,
                    "value": "", "unit": "", "status": "DATA_MISSING",
                    "missing_reason": "669fix-b-2022: hongheiku tag 页无 2022 bulletin (GUANGXI_NANNING/TAIWAN_TAIPEI, 守新增红线-3 不手填)",
                    "source_url": "", "bulletic_eid": "",
                })
                miss_count += 1
            print(f"  → 10 DATA_MISSING (no hongheiku 2022 entry)")
            continue

        html_path = CACHE_DIR / f"bulletin_{eid}_y2022.html"
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
                        "city_code": city, "indicator_key": ind_key, "year": 2022,
                        "value": "", "unit": "", "status": "DATA_MISSING",
                        "missing_reason": "669fix-b-2022: bulletin 仅发增长%, 无绝对值 (守红线-3, per 669a-2021 §2)",
                        "source_url": source_url, "bulletic_eid": eid,
                    })
                    miss_count += 1
                    print(f"    {ind_key:20s} = MISSING (only growth %)")
                else:
                    real_count += 1
                    rows.append({
                        "city_code": city, "indicator_key": ind_key, "year": 2022,
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
                    "city_code": city, "indicator_key": ind_key, "year": 2022,
                    "value": "", "unit": "", "status": "DATA_MISSING",
                    "missing_reason": f"669fix-b-2022: bulletin 无 {ind_key} 数据 (parser 未匹配)",
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