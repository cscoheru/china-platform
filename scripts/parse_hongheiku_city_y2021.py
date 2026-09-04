#!/usr/bin/env python3
"""
669a-2021 parse — extract 10 指标 from 4 city 2021 hongheiku bulletins
========================================================================

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
    fixed_asset   固定资产投资 (亿元) — 表述: 固定资产投资(不含农户)
    retail        社会消费品零售总额 (亿元)
    trade         进出口总额 (亿元)

Parse strategy:
  - HTML strip via regex
  - 模式匹配: <城市>2021年实现地区生产总值<NUM>亿元，比上年增长<NUM>%
  - 容错: 中间可能有「全年」「完成」「总计」等修饰词
  - 缺值: regex 失败 → 字段为 NULL (守新增红线-3 不手填)

Input: /tmp/669a-2021/{city_code}.html
Output: /tmp/669a-2021/seed_hongheiku_city_2021.csv (40 rows)
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

YEAR = 2021
RULING = "K669a-2021-2026-09-04"
ORIGIN = "tjgb.hongheiku.com/djs"


def strip_html(raw: str) -> str:
    text = re.sub(r"<script[^>]*>.*?</script>", "", raw, flags=re.DOTALL)
    text = re.sub(r"<style[^>]*>.*?</style>", "", text, flags=re.DOTALL)
    text = re.sub(r"<[^>]+>", "\n", text)
    text = html.unescape(text)
    text = re.sub(r"\n\s*\n", "\n", text)
    return text.strip()


def first_num_after(pattern: str, text: str, max_offset: int = 80) -> str | None:
    """
    在 text 中找 pattern 后跟数字(可含小数点).
    max_offset: 数字距离 pattern 的最大字符数 (防止跨段误匹配).
    """
    m = re.search(pattern + r".{0,80}?([\d,]+(?:\.\d+)?)", text)
    if not m:
        return None
    return m.group(1).replace(",", "")


def extract_one_indicator(text: str, key: str, hint: str) -> str | None:
    """Extract single indicator value from text via hint pattern."""
    if key == "gdp_growth":
        # 增长 X.X% (specific)
        m = re.search(r"地区生产总值.*?增长\s*([+-]?\d+(?:\.\d+)?)\s*%", text)
        if m:
            return m.group(1)
        return None
    if key == "gdp_total":
        # 实现地区生产总值 30664.85亿元
        m = re.search(r"(?:实现|完成|地区)地区生产总值\s*([\d,]+(?:\.\d+)?)\s*亿元", text)
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
        # 人均地区生产总值173663元
        m = re.search(r"人均地区生产总值\s*([\d,]+(?:\.\d+)?)\s*元", text)
        if m:
            return m.group(1).replace(",", "")
        return None
    if key == "fiscal_rev":
        m = re.search(r"(?:全年完成?|实现)?一般公共预算收入\s*([\d,]+(?:\.\d+)?)\s*亿元", text)
        if m:
            return m.group(1).replace(",", "")
        return None
    if key == "fixed_asset":
        # 固定资产投资(不含农户) X.XX亿元 or 增长 X.X%
        m = re.search(r"固定资产投资(?:（不含农户）|\(不含农户\))?\s*([\d,]+(?:\.\d+)?)\s*亿元", text)
        if m:
            return m.group(1).replace(",", "")
        m = re.search(r"固定资产投资(?:（不含农户）|\(不含农户\))?(?:增长|为)\s*([+-]?\d+(?:\.\d+)?)\s*%", text)
        if m:
            return None  # 增速不是绝对值
        return None
    if key == "retail":
        m = re.search(r"社会消费品零售总额\s*([\d,]+(?:\.\d+)?)\s*亿元", text)
        if m:
            return m.group(1).replace(",", "")
        return None
    if key == "trade":
        m = re.search(r"进出口(?:总额)?\s*([\d,]+(?:\.\d+)?)\s*亿元", text)
        if m:
            return m.group(1).replace(",", "")
        return None
    return None


def main():
    in_dir = Path("/tmp/669a-2021")
    out_csv = in_dir / "seed_hongheiku_city_2021.csv"

    rows: list[dict] = []
    stats = {"cells_with_value": 0, "cells_null": 0, "by_indicator": {}}

    for city_code, city_name in CITIES:
        html_path = in_dir / f"{city_code}.html"
        if not html_path.exists():
            print(f"  [WARN] {city_code}: HTML not found, skip")
            continue
        text = strip_html(html_path.read_text(encoding="utf-8"))
        # restrict to first 5000 chars (intro + 综合 section most indicators live here)
        # secondary indicators (fiscal_rev/fixed_asset/retail/trade) are in later sections
        text_full = text

        for ind_key, ind_label, unit in INDICATORS:
            val = extract_one_indicator(text_full, ind_key, ind_label)
            if val:
                stats["cells_with_value"] += 1
                stats["by_indicator"][ind_key] = stats["by_indicator"].get(ind_key, 0) + 1
                status = ""
                missing_reason = ""
            else:
                stats["cells_null"] += 1
                val = ""
                status = "DATA_MISSING"
                missing_reason = f"knife 669a-2021 {city_name} {ind_key} 待 harvest/补采 (regex miss or 不在该公报)"
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

    # write CSV
    fields = ["city_code", "indicator_key", "year", "value", "unit",
              "status", "missing_reason", "lineage_source_type",
              "lineage_origin", "lineage_ruling", "lineage_is_demo"]
    with out_csv.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        w.writerows(rows)

    print("=== knife 669a-2021 parse 结果 ===")
    print(f"  4 city × 10 indicator = 40 rows expected")
    print(f"  rows written: {len(rows)}")
    print(f"  cells with value: {stats['cells_with_value']} / 40")
    print(f"  cells null (待补采): {stats['cells_null']} / 40")
    print()
    print("=== by_indicator (which indicators got values from how many cities) ===")
    for ind_key, _, _ in INDICATORS:
        cnt = stats["by_indicator"].get(ind_key, 0)
        print(f"  {ind_key:18s} = {cnt}/4 cities")
    print()
    print(f"=== seed CSV → {out_csv} ===")
    print(f"  size: {out_csv.stat().st_size} bytes")
    # print first 10 rows
    with out_csv.open() as f:
        for i, line in enumerate(f):
            if i < 12:
                print(f"  {line.rstrip()}")


if __name__ == "__main__":
    main()
