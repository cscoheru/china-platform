#!/usr/bin/env python3
"""
669fix-b-2025 parse — Zero-harvest path: 25 city × 10 indicator, all DATA_MISSING
=============================================================================

knife 669fix-b-2025 sub-knife (Path A 续刀 5/5):
- baseline 翻转判定: 669fix-1 重写 tag parse filter 后, cat index 2025 含 14 entry 但全部 province level
  (省级公报 eid 72070/72067/72064/72041 等, 是 2024 年度数据, 发布于 2026-04-30 ~ 2026-05-21).
- 25 省会需要 city level 市级公报, 实证 5 个 city tag/search cache (成都/广州/杭州/武汉/长沙) 全 generic title, 0 命中.
- 与 669b-2025 zero-harvest 一致: hongheiku city level 市级 2025 entry 暂未收录, 守红线-3 不手填.
- 期望: 250 rows 全 DATA_MISSING (0 real, 250 miss)

Output: seed_hongheiku_city_timeseries_2025.csv (250 rows, 25 city × 10 indicator, all DATA_MISSING)
"""
import csv
from pathlib import Path

OUT_CSV = Path("/Users/kjonekong/projects/china platform/source_registry/seed_hongheiku_city_timeseries_2025.csv")

# 25 省会 — 沿用 669fix-b-2024 city list
CITY_LIST = [
    "HEBEI_SHIJIAZHUANG",
    "SHANXI_TAIYUAN",
    "NEIMENGGU_HUHEHAOTE",
    "LIAONING_SHENYANG",
    "JILIN_CHANGCHUN",
    "HEILONGJIANG_HARBIN",
    "ANHUI_HEFEI",
    "FUJIAN_FUZHOU",
    "JIANGXI_NANCHANG",
    "SHANDONG_JINAN",
    "HENAN_ZHENGZHOU",
    "HUBEI_WUHAN",
    "HUNAN_CHANGSHA",
    "GUANGXI_NANNING",
    "HAINAN_HAIKOU",
    "SICHUAN_CHENGDU",
    "GUIZHOU_GUIYANG",
    "YUNNAN_KUNMING",
    "XIZANG_LASA",
    "SHAANXI_XIAN",
    "GANSU_LANZHOU",
    "QINGHAI_XINING",
    "NINGXIA_YINCHUAN",
    "XINJIANG_WULUMUQI",
    "TAIWAN_TAIPEI",
]

INDICATORS = [
    ("gdp_total",       "亿元",  "地区生产总值"),
    ("gdp_growth",      "%",     "GDP 增速"),
    ("primary_gdp",     "亿元",  "第一产业"),
    ("secondary_gdp",   "亿元",  "第二产业"),
    ("tertiary_gdp",    "亿元",  "第三产业"),
    ("gdp_percapita",   "元",    "人均地区生产总值"),
    ("fiscal_rev",      "亿元",  "一般公共预算收入"),
    ("fixed_asset",     "亿元",  "固定资产投资"),
    ("retail",          "亿元",  "社会消费品零售总额"),
    ("trade",           "亿元",  "进出口总额"),
]

RULING = "K669fix-b-2025-2026-09-09"
YEAR = 2025


def main():
    rows = []
    for city_code in CITY_LIST:
        for indicator_key, unit, indicator_label in INDICATORS:
            rows.append({
                "city_code": city_code,
                "indicator_key": indicator_key,
                "year": YEAR,
                "value": "",
                "unit": unit,
                "status": "DATA_MISSING",
                "missing_reason": (
                    f"knife 669fix-b-2025 {city_code} {indicator_key} 2025 年度市级统计公报 "
                    f"hongheiku 暂未收录 (cat index 2025 14 entry 全为省级公报非市级, "
                    f"5 city tag/search cache probe 0 命中, 守红线-3 不手填, "
                    f"待 2026 城市公报陆续发布后再 harvest)"
                ),
                "lineage_source_type": "DATA_MISSING",
                "lineage_origin": "tjgb.hongheiku.com/tag/{city_slug} (no 2025 city-level entry)",
                "lineage_ruling": RULING,
                "lineage_is_demo": "false",
            })

    with open(OUT_CSV, "w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=[
            "city_code", "indicator_key", "year", "value", "unit", "status",
            "missing_reason", "lineage_source_type", "lineage_origin", "lineage_ruling", "lineage_is_demo",
        ])
        writer.writeheader()
        writer.writerows(rows)

    real_count = sum(1 for r in rows if r["status"] != "DATA_MISSING")
    miss_count = len(rows) - real_count
    print(f"=== knife 669fix-b-2025 seed CSV generated ===")
    print(f"  Output: {OUT_CSV}")
    print(f"  Total rows: {len(rows)} (25 city × 10 indicator)")
    print(f"  Real cells: {real_count}")
    print(f"  Missing cells: {miss_count}")
    print(f"  Ruling: {RULING}")


if __name__ == "__main__":
    main()
