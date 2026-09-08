#!/usr/bin/env python3
"""
669fix-b-2023 parse — Extract 10 指标 from 21 city bulletins (HTML)
=============================================================================

knife 669fix-b-2023 sub-knife (Path A 续刀 3/5):
- 21 HTML bulletins: text extraction with parser v3 strip-first
- 4 missing (LIAONING_SHENYANG/HEILONGJIANG_HARBIN/JIANGXI_NANCHANG/YUNNAN_KUNMING + TAIWAN_TAIPEI): DATA_MISSING
- 5 city 无 2023 entry: LIAONING/HEILONGJIANG/JIANGXI/YUNNAN/TAIWAN

Output: seed_hongheiku_city_timeseries_2023.csv (250 rows, 25 city × 10 indicator)
"""
import csv
import re
from pathlib import Path

CACHE_DIR = Path("/tmp/669b/bulletins_2023")
OUT_CSV = Path("/Users/kjonekong/projects/china platform/source_registry/seed_hongheiku_city_timeseries_2023.csv")

# 21 city with eid + 5 missing
CITY_BULLETINS = [
    # (city_code, eid, format, source_url, cache_filename)
    ("HEBEI_SHIJIAZHUANG",       45623,  "html",      "https://tjgb.hongheiku.com/djs/45623.html", "HEBEI_SHIJIAZHUANG_45623.html"),
    ("SHANXI_TAIYUAN",           55537,  "html",      "https://tjgb.hongheiku.com/djs/55537.html", "SHANXI_TAIYUAN_55537.html"),
    ("NEIMENGGU_HUHEHAOTE",      47464,  "html",      "https://tjgb.hongheiku.com/djs/47464.html", "NEIMENGGU_HUHEHAOTE_47464.html"),
    ("LIAONING_SHENYANG",        None,   "missing",   None, None),
    ("JILIN_CHANGCHUN",          53459,  "html",      "https://tjgb.hongheiku.com/djs/53459.html", "JILIN_CHANGCHUN_53459.html"),
    ("HEILONGJIANG_HARBIN",      None,   "missing",   None, None),
    ("ANHUI_HEFEI",              46594,  "html",      "https://tjgb.hongheiku.com/djs/46594.html", "ANHUI_HEFEI_46594.html"),
    ("FUJIAN_FUZHOU",            47449,  "html",      "https://tjgb.hongheiku.com/djs/47449.html", "FUJIAN_FUZHOU_47449.html"),
    ("JIANGXI_NANCHANG",         None,   "missing",   None, None),
    ("SHANDONG_JINAN",           53597,  "html",      "https://tjgb.hongheiku.com/djs/53597.html", "SHANDONG_JINAN_53597.html"),
    ("HENAN_ZHENGZHOU",          47058,  "html",      "https://tjgb.hongheiku.com/djs/47058.html", "HENAN_ZHENGZHOU_47058.html"),
    ("HUBEI_WUHAN",              46943,  "html",      "https://tjgb.hongheiku.com/djs/46943.html", "HUBEI_WUHAN_46943.html"),
    ("HUNAN_CHANGSHA",           49118,  "html",      "https://tjgb.hongheiku.com/djs/49118.html", "HUNAN_CHANGSHA_49118.html"),
    ("GUANGXI_NANNING",          48505,  "html",      "https://tjgb.hongheiku.com/djs/48505.html", "GUANGXI_NANNING_48505.html"),
    ("HAINAN_HAIKOU",            45493,  "html",      "https://tjgb.hongheiku.com/djs/45493.html", "HAINAN_HAIKOU_45493.html"),
    ("SICHUAN_CHENGDU",          46512,  "html",      "https://tjgb.hongheiku.com/djs/46512.html", "SICHUAN_CHENGDU_46512.html"),
    ("GUIZHOU_GUIYANG",          51284,  "html",      "https://tjgb.hongheiku.com/djs/51284.html", "GUIZHOU_GUIYANG_51284.html"),
    ("YUNNAN_KUNMING",           None,   "missing",   None, None),
    ("XIZANG_LASA",              48605,  "html",      "https://tjgb.hongheiku.com/djs/48605.html", "XIZANG_LASA_48605.html"),
    ("SHAANXI_XIAN",             46977,  "html",      "https://tjgb.hongheiku.com/djs/46977.html", "SHAANXI_XIAN_46977.html"),
    ("GANSU_LANZHOU",            46073,  "html",      "https://tjgb.hongheiku.com/djs/46073.html", "GANSU_LANZHOU_46073.html"),
    ("QINGHAI_XINING",           47585,  "html",      "https://tjgb.hongheiku.com/djs/47585.html", "QINGHAI_XINING_47585.html"),
    ("NINGXIA_YINCHUAN",         47605,  "html",      "https://tjgb.hongheiku.com/djs/47605.html", "NINGXIA_YINCHUAN_47605.html"),
    ("XINJIANG_WULUMUQI",        46740,  "html",      "https://tjgb.hongheiku.com/djs/46740.html", "XINJIANG_WULUMUQI_46740.html"),
    ("TAIWAN_TAIPEI",            None,   "missing",   None, None),
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

    for city, eid, fmt, source_url, cache_name in CITY_BULLETINS:
        print(f"\n=== {city} (eid={eid}, format={fmt}) ===")

        if fmt == "missing":
            for ind_key, ind_label in INDICATORS:
                rows.append({
                    "city_code": city, "indicator_key": ind_key, "year": 2023,
                    "value": "", "unit": "", "status": "DATA_MISSING",
                    "missing_reason": "669fix-b-2023: hongheiku tag 页无 2023 bulletin (LIAONING/HEILONGJIANG/JIANGXI/YUNNAN/TAIWAN, 守新增红线-3 不手填)",
                    "source_url": "", "bulletic_eid": "",
                })
                miss_count += 1
            print(f"  → 10 DATA_MISSING (no hongheiku 2023 entry)")
            continue

        html_path = CACHE_DIR / cache_name
        if not html_path.exists():
            print(f"  ✗ HTML missing: {html_path}")
            for ind_key, ind_label in INDICATORS:
                rows.append({
                    "city_code": city, "indicator_key": ind_key, "year": 2023,
                    "value": "", "unit": "", "status": "DATA_MISSING",
                    "missing_reason": "669fix-b-2023: bulletin cache 缺失 (守红线-3)",
                    "source_url": source_url, "bulletic_eid": eid,
                })
                miss_count += 1
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
                        "city_code": city, "indicator_key": ind_key, "year": 2023,
                        "value": "", "unit": "", "status": "DATA_MISSING",
                        "missing_reason": "669fix-b-2023: bulletin 仅发增长%, 无绝对值 (守红线-3, per 669a-2021 §2)",
                        "source_url": source_url, "bulletic_eid": eid,
                    })
                    miss_count += 1
                    print(f"    {ind_key:20s} = MISSING (only growth %)")
                else:
                    real_count += 1
                    rows.append({
                        "city_code": city, "indicator_key": ind_key, "year": 2023,
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
                    "city_code": city, "indicator_key": ind_key, "year": 2023,
                    "value": "", "unit": "", "status": "DATA_MISSING",
                    "missing_reason": f"669fix-b-2023: bulletin 无 {ind_key} 数据 (parser 未匹配)",
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