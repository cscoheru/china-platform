#!/usr/bin/env python3
"""
669a-2025 parse — extract 10 指标 from 4 city 2025 hongheiku bulletins
========================================================================

Mirror of parse_hongheiku_city_y2024.py (year 2025 edition).

10 指标 (mirror mart_city_timeseries indicator_dimension):
  5 现:
    gdp_total     地区生产总值 (亿元)
    gdp_growth    地区生产总值 (增速 %)
    primary_gdp   第一产业增加值 (亿元)
    secondary_gdp 第二产业增加值 (亿元)
    tertiary_gdp  第三产业增加值 (亿元)
  5 增量:
    gdp_percapita 人均地区生产总值 (元)
    fiscal_rev    一般公共预算收入 (亿元)
    fixed_asset   固定资产投资 (亿元)
    retail        社会消费品零售总额 (亿元)
    trade         进出口总额 (亿元)

2025 harvest 实测 (probe 实证):
- hongheiku 2025 entry available for GUANGZHOU (69954, 2026-05-12) + HANGZHOU (69708, 2026-04-30)
- hongheiku 2025 entry ABSENT for SHENZHEN (tag 页只列 2021-2024, 搜索无结果) + NANJING (同)
- SHENZHEN/NANJING 2025 = 全部 10 cells DATA_MISSING (守红线-3 不手填, 公报未发布/未收录)

2025 公报表述变体 (empirical probe):
- GDP: 广州括号注「(初步核算数)」 → 沿用 2024 括号容错; 杭州脚注 [2] 23011亿元 → 沿用 s* 脚注容错 (见代码 regex)
- 人均: 全称「人均地区生产总值」+ 无缩写 (2025 公报口径规范化)
- 财政/进出口: 同 2024 pattern
- 固投: 仅发增速 (穗-6.7% / 杭占比) → DATA_MISSING (守红线-3 增速≠绝对值)
- 零售: 广州 11032.38亿元 (实值) + 杭州 9499亿元 (实值)

Input:  /tmp/669a-2025/{city_code}.html (GUANGDONG_GUANGZHOU.html, ZHEJIANG_HANGZHOU.html)
        SZ/NJ HTML 不存在 → 全部 DATA_MISSING
Output: /tmp/669a-2025/seed_hongheiku_city_2025.csv (40 rows = 4 city × 10 indicator)
"""

import csv
import re
import html
from pathlib import Path

CITIES = [
    ("GUANGDONG_SHENZHEN",  "深圳市"),
    ("GUANGDONG_GUANGZHOU", "广州市"),
    ("ZHEJIANG_HANGZHOU",   "杭州市"),
    ("JIANGSU_NANJING",     "南京市"),
]

INDICATORS = [
    ("gdp_total",     "地区生产总值",      "亿元"),
    ("gdp_growth",    "地区生产总值.*?增长", "%"),
    ("primary_gdp",   "第一产业增加值",    "亿元"),
    ("secondary_gdp", "第二产业增加值",    "亿元"),
    ("tertiary_gdp",  "第三产业增加值",    "亿元"),
    ("gdp_percapita", "人均地区生产总值",  "元"),
    ("fiscal_rev",    "一般公共预算收入",  "亿元"),
    ("fixed_asset",   "固定资产投资",      "亿元"),
    ("retail",        "社会消费品零售总额", "亿元"),
    ("trade",         "进出口总额",        "亿元"),
]

YEAR = 2025
RULING = "K669a-2025-2026-09-07"
ORIGIN = "tjgb.hongheiku.com/djs"

# 2025 cities with hongheiku entry (per Phase 1 URL discovery)
CITIES_WITH_2025_DATA = {"GUANGDONG_GUANGZHOU", "ZHEJIANG_HANGZHOU"}


def strip_html(raw: str) -> str:
    text = re.sub(r"<script[^>]*>.*?</script>", "", raw, flags=re.DOTALL)
    text = re.sub(r"<style[^>]*>.*?</style>", "", text, flags=re.DOTALL)
    text = re.sub(r"<[^>]+>", "\n", text)
    text = html.unescape(text)
    text = re.sub(r"\n\s*\n", "\n", text)
    return text.strip()


def extract_one_indicator(text: str, key: str) -> str | None:
    """Extract single indicator value from text via hint pattern."""
    if key == "gdp_growth":
        m = re.search(r"地区生产总值.*?增长\s*([+-]?\d+(?:\.\d+)?)\s*%", text, re.DOTALL)
        if m:
            return m.group(1)
        return None
    if key == "gdp_total":
        m = re.search(r"地区生产总值\s*(?:（[^）]{0,20}）|\[\d+\])?\s*([\d,]+(?:\.\d+)?)\s*亿元", text)
        if m:
            return m.group(1).replace(",", "")
        return None
    if key == "primary_gdp":
        m = re.search(r"第一产业增加值\s*([\d,]+(?:\.\d+)?)\s*亿元", text)
        if m:
            return m.group(1).replace(",", "")
        return None
    if key == "secondary_gdp":
        m = re.search(r"第二产业增加值\s*([\d,]+(?:\.\d+)?)\s*亿元", text)
        if m:
            return m.group(1).replace(",", "")
        return None
    if key == "tertiary_gdp":
        m = re.search(r"第三产业增加值\s*([\d,]+(?:\.\d+)?)\s*亿元", text)
        if m:
            return m.group(1).replace(",", "")
        return None
    if key == "gdp_percapita":
        m = re.search(r"(?:人均地区生产总值|人均GDP)(?:达到|达|为)?\s*([\d,]+(?:\.\d+)?)\s*元", text)
        if m:
            return m.group(1).replace(",", "")
        return None
    if key == "fiscal_rev":
        m = re.search(r"(?:全年完成?|实现)?一般公共预算收入\s*([\d,]+(?:\.\d+)?)\s*亿元", text)
        if m:
            return m.group(1).replace(",", "")
        return None
    if key == "fixed_asset":
        m = re.search(r"(?:完成|全社会)?固定资产投资(?:（不含农户）|\(不含农户\))?\s*([\d,]+(?:\.\d+)?)\s*亿元", text)
        if m:
            return m.group(1).replace(",", "")
        m = re.search(r"固定资产投资(?:（不含农户）|\(不含农户\))?(?:增长|为)\s*([+-]?\d+(?:\.\d+)?)\s*%", text)
        if m:
            return None
        return None
    if key == "retail":
        m = re.search(r"社会消费品零售总额\s*(?:（[^）]{0,20}）|\[\d+\])?\s*([\d,]+(?:\.\d+)?)\s*亿元", text)
        if m:
            return m.group(1).replace(",", "")
        return None
    if key == "trade":
        m = re.search(r"(?:货物|商品)?进出口(?:总额|总值)\s*([\d,]+(?:\.\d+)?)\s*亿元", text)
        if m:
            return m.group(1).replace(",", "")
        return None
    return None


def main():
    in_dir = Path("/tmp/669a-2025")
    out_csv = in_dir / "seed_hongheiku_city_2025.csv"

    rows: list[dict] = []
    stats = {
        "cells_with_value": 0, "cells_null": 0,
        "by_indicator": {}, "by_city": {},
        "cities_missing_2025_entry": [],
    }

    for city_code, city_name in CITIES:
        html_path = in_dir / f"{city_code}.html"
        if not html_path.exists():
            # 2025 entry ABSENT on hongheiku for this city (守红线-3 不手填)
            print(f"  [WARN] {city_code}: HTML not found, hongheiku 2025 entry absent")
            stats["cities_missing_2025_entry"].append(city_code)
            for ind_key, ind_label, unit in INDICATORS:
                rows.append({
                    "city_code": city_code,
                    "indicator_key": ind_key,
                    "year": YEAR,
                    "value": "",
                    "unit": unit,
                    "status": "DATA_MISSING",
                    "missing_reason": (f"knife 669a-2025 {city_name} {ind_key} 公报未发布/未收录 "
                                       f"(hongheiku tag 页 + 站内搜索均无 2025 entry, 守红线-3 不手填)"),
                    "lineage_source_type": "DATA_MISSING",
                    "lineage_origin": f"{ORIGIN}/{city_name} (no 2025 entry)",
                    "lineage_ruling": RULING,
                    "lineage_is_demo": "false",
                })
                stats["cells_null"] += 1
            stats["by_city"][city_code] = 0
            continue

        text = strip_html(html_path.read_text(encoding="utf-8"))
        city_real = 0
        for ind_key, ind_label, unit in INDICATORS:
            val = extract_one_indicator(text, ind_key)
            if val:
                stats["cells_with_value"] += 1
                city_real += 1
                stats["by_indicator"][ind_key] = stats["by_indicator"].get(ind_key, 0) + 1
                status = ""
                missing_reason = ""
            else:
                stats["cells_null"] += 1
                val = ""
                status = "DATA_MISSING"
                missing_reason = (f"knife 669a-2025 {city_name} {ind_key} 公报仅发增速无绝对值 (守红线-3 不手填)")
            rows.append({
                "city_code": city_code,
                "indicator_key": ind_key,
                "year": YEAR,
                "value": val,
                "unit": unit,
                "status": status,
                "missing_reason": missing_reason,
                "lineage_source_type": "HONGHEIKU_TRANSLOAD" if val else "DATA_MISSING",
                "lineage_origin": f"{ORIGIN}/{city_name}",
                "lineage_ruling": RULING,
                "lineage_is_demo": "false",
            })
        stats["by_city"][city_code] = city_real

    fields = ["city_code", "indicator_key", "year", "value", "unit",
              "status", "missing_reason", "lineage_source_type",
              "lineage_origin", "lineage_ruling", "lineage_is_demo"]
    with out_csv.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        w.writerows(rows)

    print("=== knife 669a-2025 parse 结果 ===")
    print(f"  4 city × 10 indicator = 40 rows expected")
    print(f"  rows written: {len(rows)}")
    print(f"  cells with value: {stats['cells_with_value']} / 40")
    print(f"  cells null (待补采): {stats['cells_null']} / 40")
    print(f"  cities with hongheiku 2025 entry: {len(CITIES_WITH_2025_DATA)}/4 "
          f"(深圳/南京 tag 页 + 站内搜索均无 2025 entry → DATA_MISSING 不手填)")
    print()
    print("=== by_city (real cells per city) ===")
    for city_code, cnt in stats["by_city"].items():
        print(f"  {city_code:24s} = {cnt}/10")
    print()
    print("=== by_indicator (which indicators got values from how many cities) ===")
    for ind_key, _, _ in INDICATORS:
        cnt = stats["by_indicator"].get(ind_key, 0)
        print(f"  {ind_key:18s} = {cnt}/2 cities (only 广州/杭州)")
    print()
    print(f"=== seed CSV → {out_csv} ===")
    print(f"  size: {out_csv.stat().st_size} bytes")
    print()
    print("=== extracted values (evidence) ===")
    for r in rows:
        if r["value"]:
            print(f"  {r['city_code']:24s} {r['indicator_key']:16s} = {r['value']} {r['unit']}")


if __name__ == "__main__":
    main()