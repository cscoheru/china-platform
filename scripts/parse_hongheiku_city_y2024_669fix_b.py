#!/usr/bin/env python3
"""
669fix-b-2024 parse — Extract 10 指标 from 21 city bulletins (HTML)
=============================================================================

knife 669fix-b-2024 sub-knife (Path A 续刀 4/5):
- 21 HTML bulletins: text extraction with parser v3 strip-first
- 4 missing (JIANGXI_NANCHANG/YUNNAN_KUNMING/QINGHAI_XINING/TAIWAN_TAIPEI): DATA_MISSING
- 4 city all-missing: JIANGXI/YUNNAN/QINGHAI/TAIWAN
- 4 669a (SZ/GZ/HZ/NJ): K669a-2024 已 attribution, 不 in this seed CSV

Output: seed_hongheiku_city_timeseries_2024.csv (250 rows, 25 city × 10 indicator)
"""
import csv
import re
from pathlib import Path

CACHE_DIR = Path("/tmp/669b/bulletins_2024")
OUT_CSV = Path("/Users/kjonekong/projects/china platform/source_registry/seed_hongheiku_city_timeseries_2024.csv")

# 25 省会 = 21 with 2024 eid + 4 missing
# 4 669a (SZ/GZ/HZ/NJ) excluded (K669a-2024 已 attribution)
CITY_BULLETINS = [
    # (city_code, eid, format, source_url, cache_filename)
    ("HEBEI_SHIJIAZHUANG",       59546,  "html",      "https://tjgb.hongheiku.com/djs/59546.html", "HEBEI_SHIJIAZHUANG_59546.html"),
    ("SHANXI_TAIYUAN",           59384,  "html",      "https://tjgb.hongheiku.com/djs/59384.html", "SHANXI_TAIYUAN_59384.html"),
    ("NEIMENGGU_HUHEHAOTE",      58237,  "html",      "https://tjgb.hongheiku.com/djs/58237.html", "NEIMENGGU_HUHEHAOTE_58237.html"),
    ("LIAONING_SHENYANG",        60025,  "html",      "https://tjgb.hongheiku.com/djs/60025.html", "LIAONING_SHENYANG_60025.html"),
    ("JILIN_CHANGCHUN",          65055,  "html",      "https://tjgb.hongheiku.com/djs/65055.html", "JILIN_CHANGCHUN_65055.html"),
    ("HEILONGJIANG_HARBIN",      64081,  "html",      "https://tjgb.hongheiku.com/djs/64081.html", "HEILONGJIANG_HARBIN_64081.html"),
    ("ANHUI_HEFEI",              57806,  "html",      "https://tjgb.hongheiku.com/djs/57806.html", "ANHUI_HEFEI_57806.html"),
    ("FUJIAN_FUZHOU",            58216,  "html",      "https://tjgb.hongheiku.com/djs/58216.html", "FUJIAN_FUZHOU_58216.html"),
    ("JIANGXI_NANCHANG",         None,   "missing",   None, None),
    ("SHANDONG_JINAN",           57483,  "html",      "https://tjgb.hongheiku.com/djs/57483.html", "SHANDONG_JINAN_57483.html"),
    ("HENAN_ZHENGZHOU",          59120,  "html",      "https://tjgb.hongheiku.com/djs/59120.html", "HENAN_ZHENGZHOU_59120.html"),
    ("HUBEI_WUHAN",              58204,  "html",      "https://tjgb.hongheiku.com/djs/58204.html", "HUBEI_WUHAN_58204.html"),
    ("HUNAN_CHANGSHA",           58642,  "html",      "https://tjgb.hongheiku.com/djs/58642.html", "HUNAN_CHANGSHA_58642.html"),
    ("GUANGXI_NANNING",          62300,  "html",      "https://tjgb.hongheiku.com/djs/62300.html", "GUANGXI_NANNING_62300.html"),
    ("HAINAN_HAIKOU",            57678,  "html",      "https://tjgb.hongheiku.com/djs/57678.html", "HAINAN_HAIKOU_57678.html"),
    ("SICHUAN_CHENGDU",          57761,  "html",      "https://tjgb.hongheiku.com/djs/57761.html", "SICHUAN_CHENGDU_57761.html"),
    ("GUIZHOU_GUIYANG",          58090,  "html",      "https://tjgb.hongheiku.com/djs/58090.html", "GUIZHOU_GUIYANG_58090.html"),
    ("YUNNAN_KUNMING",           None,   "missing",   None, None),
    ("XIZANG_LASA",              60539,  "html",      "https://tjgb.hongheiku.com/djs/60539.html", "XIZANG_LASA_60539.html"),
    ("SHAANXI_XIAN",             59301,  "html",      "https://tjgb.hongheiku.com/djs/59301.html", "SHAANXI_XIAN_59301.html"),
    ("GANSU_LANZHOU",            57470,  "html",      "https://tjgb.hongheiku.com/djs/57470.html", "GANSU_LANZHOU_57470.html"),
    ("QINGHAI_XINING",           None,   "missing",   None, None),
    ("NINGXIA_YINCHUAN",         61220,  "html",      "https://tjgb.hongheiku.com/djs/61220.html", "NINGXIA_YINCHUAN_61220.html"),
    ("XINJIANG_WULUMUQI",        60312,  "html",      "https://tjgb.hongheiku.com/djs/60312.html", "XINJIANG_WULUMUQI_60312.html"),
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
                    "city_code": city, "indicator_key": ind_key, "year": 2024,
                    "value": "", "unit": "", "status": "DATA_MISSING",
                    "missing_reason": "669fix-b-2024: hongheiku tag 页无 2024 bulletin (JIANGXI/YUNNAN/QINGHAI/TAIWAN, 守新增红线-3 不手填)",
                    "source_url": "", "bulletic_eid": "",
                })
                miss_count += 1
            print(f"  → 10 DATA_MISSING (no hongheiku 2024 entry)")
            continue

        html_path = CACHE_DIR / cache_name
        if not html_path.exists():
            print(f"  ✗ HTML missing: {html_path}")
            for ind_key, ind_label in INDICATORS:
                rows.append({
                    "city_code": city, "indicator_key": ind_key, "year": 2024,
                    "value": "", "unit": "", "status": "DATA_MISSING",
                    "missing_reason": "669fix-b-2024: bulletin cache 缺失 (守红线-3)",
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
                        "city_code": city, "indicator_key": ind_key, "year": 2024,
                        "value": "", "unit": "", "status": "DATA_MISSING",
                        "missing_reason": "669fix-b-2024: bulletin 仅发增长%, 无绝对值 (守红线-3, per 669a-2021 §2)",
                        "source_url": source_url, "bulletic_eid": eid,
                    })
                    miss_count += 1
                    print(f"    {ind_key:20s} = MISSING (only growth %)")
                else:
                    real_count += 1
                    rows.append({
                        "city_code": city, "indicator_key": ind_key, "year": 2024,
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
                    "city_code": city, "indicator_key": ind_key, "year": 2024,
                    "value": "", "unit": "", "status": "DATA_MISSING",
                    "missing_reason": f"669fix-b-2024: bulletin 无 {ind_key} 数据 (parser 未匹配)",
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