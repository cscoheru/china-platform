#!/usr/bin/env python3
"""
669b-2025 parse — extract 10 指标 from 25 省会 city × 2025 hongheiku bulletins
==============================================================================

knife 669b-2025 范围: 25 省会城市 (除 4 直辖市禁 city dim + 3 已在 669a: 穗/杭/宁)
                    × year 2025 × 10 指标 = 250 cells

Phase 1 URL discovery 实证 (per /tmp/669b/city_urls.json):
- 25 tag pages fetched + parsed
- 5 national bulletin URLs (2021-2025) 全部出现 in every tag (site-wide nav, 不是 city-specific)
- 2 city-specific URLs per city (most cities): 第七次全国人口普查公报 + 2020 年统计公报
- 0/25 cities have 2021-2025 city-specific bulletin
- Phase 1.4 cat index /category/sjtjgb 2025: 1 entry (national 68085), 0 city
- Phase 1.5 站搜 × 5 代表性 city (武汉/成都/长沙/杭州/广州) 2025: 0 results
- 杭州/广州 已知 in 669a 2025 (tag 有 5 years), 但 站搜 "杭州2025"/"广州2025年" 0 命中
  → 站搜算法 keyword-based 不友好, 但 tag 缓存直接命中

结论: 25 省会 city × 2025 = 全 DATA_MISSING (守红线-3 不手填, 公报未发布/未收录)
- 25 cities × 10 indicators = 250 cells, 全部 DATA_MISSING, 0 real
- lineage_source_type = DATA_MISSING
- lineage_origin = "tjgb.hongheiku.com/tag/{city_name} (no 2025 entry)"
- lineage_ruling = K669b-2025-2026-09-08

Output: /tmp/669b/seed_hongheiku_city_2025.csv (250 rows, 全部 DATA_MISSING)
"""

import csv
from pathlib import Path

CITIES = [
    ("HEBEI_SHIJIAZHUANG",     "石家庄市"),
    ("SHANXI_TAIYUAN",         "太原市"),
    ("NEIMENGGU_HUHEHAOTE",    "呼和浩特市"),
    ("LIAONING_SHENYANG",      "沈阳市"),
    ("JILIN_CHANGCHUN",        "长春市"),
    ("HEILONGJIANG_HARBIN",    "哈尔滨市"),
    ("ANHUI_HEFEI",            "合肥市"),
    ("FUJIAN_FUZHOU",          "福州市"),
    ("JIANGXI_NANCHANG",       "南昌市"),
    ("SHANDONG_JINAN",         "济南市"),
    ("HENAN_ZHENGZHOU",        "郑州市"),
    ("HUBEI_WUHAN",            "武汉市"),
    ("HUNAN_CHANGSHA",         "长沙市"),
    ("GUANGXI_NANNING",        "南宁市"),
    ("HAINAN_HAIKOU",          "海口市"),
    ("SICHUAN_CHENGDU",        "成都市"),
    ("GUIZHOU_GUIYANG",        "贵阳市"),
    ("YUNNAN_KUNMING",         "昆明市"),
    ("XIZANG_LASA",            "拉萨市"),
    ("SHAANXI_XIAN",           "西安市"),
    ("GANSU_LANZHOU",          "兰州市"),
    ("QINGHAI_XINING",         "西宁市"),
    ("NINGXIA_YINCHUAN",       "银川市"),
    ("XINJIANG_WULUMUQI",      "乌鲁木齐市"),
    ("TAIWAN_TAIPEI",          "台北市"),
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
RULING = "K669b-2025-2026-09-08"
ORIGIN = "tjgb.hongheiku.com/tag"


def main():
    out_dir = Path("/tmp/669b")
    out_csv = out_dir / "seed_hongheiku_city_2025.csv"

    rows: list[dict] = []

    for city_code, city_name in CITIES:
        for ind_key, ind_label, unit in INDICATORS:
            rows.append({
                "city_code": city_code,
                "indicator_key": ind_key,
                "year": YEAR,
                "value": "",
                "unit": unit,
                "status": "DATA_MISSING",
                "missing_reason": (f"knife 669b-2025 {city_name} {ind_key} 公报未发布/未收录 "
                                   f"(hongheiku tag 页 + cat index 2025 + 站搜均无 2025 entry, "
                                   f"tag 页仅含 2020 年统计公报 + 人口普查公报, 守红线-3 不手填)"),
                "lineage_source_type": "DATA_MISSING",
                "lineage_origin": f"{ORIGIN}/{city_name} (no 2025 entry)",
                "lineage_ruling": RULING,
                "lineage_is_demo": "false",
            })

    fields = ["city_code", "indicator_key", "year", "value", "unit",
              "status", "missing_reason", "lineage_source_type",
              "lineage_origin", "lineage_ruling", "lineage_is_demo"]
    with out_csv.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        w.writerows(rows)

    print("=== knife 669b-2025 parse 结果 (全 DATA_MISSING 路径) ===")
    print(f"  25 city × 10 indicator = 250 rows expected")
    print(f"  rows written: {len(rows)}")
    print(f"  cells with value: 0 / 250")
    print(f"  cells null (DATA_MISSING): 250 / 250")
    print()
    print("=== 25 cities (3 已在 669a: 穗/杭/宁 excluded; 4 直辖市禁 city dim) ===")
    for i, (cc, cn) in enumerate(CITIES, 1):
        print(f"  {i:2d}. {cc:32s} {cn}")
    print()
    print(f"=== seed CSV → {out_csv} ===")
    print(f"  size: {out_csv.stat().st_size} bytes")
    print()
    print("=== URL discovery 实证 (3 probe methods) ===")
    print("  Phase 1.1: tag 页 × 25 cities — 全部仅含 2020 年公报 + 人口普查公报 (无 2021-2025)")
    print("  Phase 1.2: cat index /category/sjtjgb 2025 — 1 entry (national), 0 city")
    print("  Phase 1.3: 站搜 ?s={city}2025 × 5 代表 — 全部 '未找到', 0 results")
    print()
    print("=== Decision (per docs/05 §8.3 + 新增红线-3) ===")
    print("  25 cities × 2025 = 全 DATA_MISSING")
    print("  不手填, 不补零, 不爬第三方源, 不冒充 ops")
    print(f"  lineage_ruling: {RULING}")


if __name__ == "__main__":
    main()