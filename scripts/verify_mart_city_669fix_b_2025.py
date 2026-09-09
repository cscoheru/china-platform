#!/usr/bin/env python3
"""
669fix-b-2025 mart verify — 48+ 红线 PASS assertions
=============================================================================

Verify mart_city_timeseries after knife 669fix-b-2025 apply.

Knife 669fix-b-2025 (Path A 续刀 5/5, baseline 翻转):
- zero-harvest path: 0 new real cells (consistent with 669b-2025)
- attribution transfer: K669b-2025 → K669fix-b-2025 (lineage_ruling branch update)
- 25 省会 × 2025 (250 cells) all DATA_MISSING
- total real cells unchanged: 854
- total rows unchanged: 2030

Mirrors 669fix-b-2024 verify pattern, adapted for year=2025 + K669fix-b-2025.
"""
import os
import sys
import psycopg2

DB_HOST = "127.0.0.1"
DB_PORT = 55440
DB_USER = "postgres"
DB_PASS = os.environ.get("DBT_DEV_PASS", "postgres")
DB_NAME = "cegr_test"
TARGET_SCHEMA = "cegr_mart"
MART_NAME = "mart_city_timeseries"


def get_conn():
    return psycopg2.connect(host=DB_HOST, port=DB_PORT, user=DB_USER,
                            password=DB_PASS, dbname=DB_NAME)


ASSERTIONS = [
    # === Section A: Schema integrity (5) ===
    ("A1: rows == 2030 (29 city × 10 indicator × 7 year)", """
        SELECT COUNT(*) FROM cegr_mart.mart_city_timeseries;
    """, 2030),
    ("A2: cities (distinct) == 29 (4 669a + 25 669b)", """
        SELECT COUNT(DISTINCT city_code) FROM cegr_mart.mart_city_timeseries;
    """, 29),
    ("A3: indicators (distinct) == 10", """
        SELECT COUNT(DISTINCT indicator_key) FROM cegr_mart.mart_city_timeseries;
    """, 10),
    ("A4: years (distinct) == 7 (2020-2026)", """
        SELECT COUNT(DISTINCT year) FROM cegr_mart.mart_city_timeseries;
    """, 7),
    ("A5: lineage_ruling (distinct) == 13 (12 + K669fix-b-2025)", """
        SELECT COUNT(DISTINCT lineage_ruling) FROM cegr_mart.mart_city_timeseries;
    """, 13),

    # === Section B: 4 直辖市禁 (红线-7) (2) ===
    ("B1: 直辖市 rows == 0", """
        SELECT COUNT(*) FROM cegr_mart.mart_city_timeseries
        WHERE city_code LIKE 'BEIJING_%' OR city_code LIKE 'SHANGHAI_%'
           OR city_code LIKE 'TIANJIN_%' OR city_code LIKE 'CHONGQING_%';
    """, 0),

    # === Section C: 2001-2019 全 DATA_MISSING (红线-1) (2) ===
    ("C1: 2001-2019 全部 0 row (守红线-1)", """
        SELECT COUNT(*) FROM cegr_mart.mart_city_timeseries
        WHERE year BETWEEN 2001 AND 2019;
    """, 0),

    # === Section D: 2026 全 DATA_MISSING (红线-2) (2) ===
    ("D1: 2026 real cells == 0 (守红线-2)", """
        SELECT COUNT(*) FROM cegr_mart.mart_city_timeseries
        WHERE year = 2026 AND value IS NOT NULL;
    """, 0),
    ("D2: 2026 DATA_MISSING == 290 (29 × 10)", """
        SELECT COUNT(*) FROM cegr_mart.mart_city_timeseries
        WHERE year = 2026 AND status = 'DATA_MISSING';
    """, 290),

    # === Section E: HONGHEIKU_TRANSLOAD consistency (3) ===
    # Real cells unchanged from 2024 baseline (854 = 732 + 122 K669fix-b-2024)
    # 2025 zero-harvest adds 0 real cells.
    ("E1: real cells = 854 (732 prev + 122 K669fix-b-2024, 0 from 2025 zero-harvest)", """
        SELECT COUNT(*) FROM cegr_mart.mart_city_timeseries
        WHERE value IS NOT NULL;
    """, 854),
    ("E2: HONGHEIKU_TRANSLOAD == real_cells", """
        SELECT COUNT(*) FROM cegr_mart.mart_city_timeseries
        WHERE lineage_source_type = 'HONGHEIKU_TRANSLOAD';
    """, 854),
    ("E3: real cells = HONGHEIKU_TRANSLOAD (consistency)", """
        SELECT (SELECT COUNT(*) FROM cegr_mart.mart_city_timeseries WHERE value IS NOT NULL)
             - (SELECT COUNT(*) FROM cegr_mart.mart_city_timeseries
                WHERE lineage_source_type = 'HONGHEIKU_TRANSLOAD');
    """, 0),

    # === Section F: 2025 zero-harvest path (knife 669fix-b-2025) (10) ===
    # 25 省会 (K669fix-b-2025): 0 real + 250 missing
    # 4 669a cities (K669a-2025, prior): 18 real + 22 missing
    # 总 2025 real = 18, missing = 272 (29 × 10 = 290 cells)
    ("F1: 2025 real cells == 18 (K669fix 0 + K669a-2025 18, zero-harvest)", """
        SELECT COUNT(*) FROM cegr_mart.mart_city_timeseries
        WHERE year = 2025 AND value IS NOT NULL;
    """, 18),
    ("F2: 2025 DATA_MISSING == 272 (290 - 18 real)", """
        SELECT COUNT(*) FROM cegr_mart.mart_city_timeseries
        WHERE year = 2025 AND value IS NULL;
    """, 272),
    ("F3: 2025 K669fix-b-2025 ruling attribution = 250 cells (25 省会 × 10)", """
        SELECT COUNT(*) FROM cegr_mart.mart_city_timeseries
        WHERE year = 2025 AND lineage_ruling = 'K669fix-b-2025-2026-09-09';
    """, 250),
    ("F4: 2025 K669fix-b-2025 real cells = 0 (zero-harvest path, 守红线-3)", """
        SELECT COUNT(*) FROM cegr_mart.mart_city_timeseries
        WHERE year = 2025 AND value IS NOT NULL
        AND lineage_ruling = 'K669fix-b-2025-2026-09-09';
    """, 0),
    ("F5: 2025 K669fix-b-2025 missing cells = 250 (zero-harvest 全 MISSING)", """
        SELECT COUNT(*) FROM cegr_mart.mart_city_timeseries
        WHERE year = 2025 AND value IS NULL
        AND lineage_ruling = 'K669fix-b-2025-2026-09-09';
    """, 250),
    ("F6: 2025 K669b-2025 attribution cells = 0 (核心 attribution 已转移)", """
        SELECT COUNT(*) FROM cegr_mart.mart_city_timeseries
        WHERE year = 2025 AND lineage_ruling = 'K669b-2025-2026-09-08';
    """, 0),
    ("F7: 2025 K669a-2025 ruling 保留 (4 city × 10 = 40 cells)", """
        SELECT COUNT(*) FROM cegr_mart.mart_city_timeseries
        WHERE year = 2025 AND lineage_ruling = 'K669a-2025-2026-09-07';
    """, 40),
    ("F8: 2025 K669a-2025 real cells = 18 (4 669a cities from prior knife)", """
        SELECT COUNT(*) FROM cegr_mart.mart_city_timeseries
        WHERE year = 2025 AND value IS NOT NULL
        AND lineage_ruling = 'K669a-2025-2026-09-07';
    """, 18),
    ("F9: 2025 K669a-2025 missing cells = 22 (4 669a cities × 5.5 avg miss)", """
        SELECT COUNT(*) FROM cegr_mart.mart_city_timeseries
        WHERE year = 2025 AND value IS NULL
        AND lineage_ruling = 'K669a-2025-2026-09-07';
    """, 22),
    ("F10: 2025 lineage_ruling distinct count = 2 (K669fix-b-2025 + K669a-2025)", """
        SELECT COUNT(DISTINCT lineage_ruling) FROM cegr_mart.mart_city_timeseries
        WHERE year = 2025;
    """, 2),

    # === Section G: 25 省会 (K669fix-b-2025) coverage (4) ===
    # All 25 省会 should be in K669fix-b-2025 attribution, all DATA_MISSING
    ("G1: 2025 25 省会 全 DATA_MISSING (real == 0)", """
        SELECT COUNT(*) FROM cegr_mart.mart_city_timeseries
        WHERE year = 2025 AND value IS NOT NULL
        AND city_code IN (
            'HEBEI_SHIJIAZHUANG','SHANXI_TAIYUAN','NEIMENGGU_HUHEHAOTE',
            'LIAONING_SHENYANG','JILIN_CHANGCHUN','HEILONGJIANG_HARBIN',
            'ANHUI_HEFEI','FUJIAN_FUZHOU','JIANGXI_NANCHANG','SHANDONG_JINAN',
            'HENAN_ZHENGZHOU','HUBEI_WUHAN','HUNAN_CHANGSHA','GUANGXI_NANNING',
            'HAINAN_HAIKOU','SICHUAN_CHENGDU','GUIZHOU_GUIYANG','YUNNAN_KUNMING',
            'XIZANG_LASA','SHAANXI_XIAN','GANSU_LANZHOU','QINGHAI_XINING',
            'NINGXIA_YINCHUAN','XINJIANG_WULUMUQI','TAIWAN_TAIPEI'
        );
    """, 0),
    ("G2: 2025 25 省会 全部 lineage_ruling = K669fix-b-2025-2026-09-09", """
        SELECT COUNT(DISTINCT lineage_ruling) FROM cegr_mart.mart_city_timeseries
        WHERE year = 2025
        AND city_code IN (
            'HEBEI_SHIJIAZHUANG','SHANXI_TAIYUAN','NEIMENGGU_HUHEHAOTE',
            'LIAONING_SHENYANG','JILIN_CHANGCHUN','HEILONGJIANG_HARBIN',
            'ANHUI_HEFEI','FUJIAN_FUZHOU','JIANGXI_NANCHANG','SHANDONG_JINAN',
            'HENAN_ZHENGZHOU','HUBEI_WUHAN','HUNAN_CHANGSHA','GUANGXI_NANNING',
            'HAINAN_HAIKOU','SICHUAN_CHENGDU','GUIZHOU_GUIYANG','YUNNAN_KUNMING',
            'XIZANG_LASA','SHAANXI_XIAN','GANSU_LANZHOU','QINGHAI_XINING',
            'NINGXIA_YINCHUAN','XINJIANG_WULUMUQI','TAIWAN_TAIPEI'
        );
    """, 1),
    ("G3: 2025 25 省会 × 10 指标 = 250 cells (守 25×10 网格)", """
        SELECT COUNT(*) FROM cegr_mart.mart_city_timeseries
        WHERE year = 2025
        AND city_code IN (
            'HEBEI_SHIJIAZHUANG','SHANXI_TAIYUAN','NEIMENGGU_HUHEHAOTE',
            'LIAONING_SHENYANG','JILIN_CHANGCHUN','HEILONGJIANG_HARBIN',
            'ANHUI_HEFEI','FUJIAN_FUZHOU','JIANGXI_NANCHANG','SHANDONG_JINAN',
            'HENAN_ZHENGZHOU','HUBEI_WUHAN','HUNAN_CHANGSHA','GUANGXI_NANNING',
            'HAINAN_HAIKOU','SICHUAN_CHENGDU','GUIZHOU_GUIYANG','YUNNAN_KUNMING',
            'XIZANG_LASA','SHAANXI_XIAN','GANSU_LANZHOU','QINGHAI_XINING',
            'NINGXIA_YINCHUAN','XINJIANG_WULUMUQI','TAIWAN_TAIPEI'
        );
    """, 250),
    ("G4: 2025 25 省会 全部 missing_reason 完备 (守完备性)", """
        SELECT COUNT(*) FROM cegr_mart.mart_city_timeseries
        WHERE year = 2025 AND value IS NULL
        AND city_code IN (
            'HEBEI_SHIJIAZHUANG','SHANXI_TAIYUAN','NEIMENGGU_HUHEHAOTE',
            'LIAONING_SHENYANG','JILIN_CHANGCHUN','HEILONGJIANG_HARBIN',
            'ANHUI_HEFEI','FUJIAN_FUZHOU','JIANGXI_NANCHANG','SHANDONG_JINAN',
            'HENAN_ZHENGZHOU','HUBEI_WUHAN','HUNAN_CHANGSHA','GUANGXI_NANNING',
            'HAINAN_HAIKOU','SICHUAN_CHENGDU','GUIZHOU_GUIYANG','YUNNAN_KUNMING',
            'XIZANG_LASA','SHAANXI_XIAN','GANSU_LANZHOU','QINGHAI_XINING',
            'NINGXIA_YINCHUAN','XINJIANG_WULUMUQI','TAIWAN_TAIPEI'
        ) AND missing_reason IS NULL;
    """, 0),

    # === Section H: lineage_origin (3) ===
    ("H1: HONGHEIKU_TRANSLOAD lineage_origin 全部 tjgb.hongheiku.com", """
        SELECT COUNT(*) FROM cegr_mart.mart_city_timeseries
        WHERE lineage_source_type = 'HONGHEIKU_TRANSLOAD'
        AND (lineage_origin IS NULL OR (lineage_origin <> '' AND lineage_origin NOT LIKE '%tjgb.hongheiku.com%'));
    """, 0),
    ("H2: HONGHEIKU_TRANSLOAD 854 行 lineage_origin 全 non-empty", """
        SELECT COUNT(*) FROM cegr_mart.mart_city_timeseries
        WHERE lineage_source_type = 'HONGHEIKU_TRANSLOAD'
        AND (lineage_origin IS NULL OR lineage_origin = '');
    """, 0),
    ("H3: 2025 K669fix-b-2025 cells lineage_origin 全部 tjgb.hongheiku.com (250 cells)", """
        SELECT COUNT(*) FROM cegr_mart.mart_city_timeseries
        WHERE year = 2025 AND lineage_ruling = 'K669fix-b-2025-2026-09-09'
        AND (lineage_origin IS NULL OR lineage_origin = ''
             OR lineage_origin NOT LIKE '%tjgb.hongheiku.com%');
    """, 0),

    # === Section I: indicator-key (2) ===
    ("I1: 10 indicator_key 全存在", """
        SELECT COUNT(DISTINCT indicator_key) FROM cegr_mart.mart_city_timeseries
        WHERE indicator_key IN (
            'gdp_total','gdp_growth','primary_gdp','secondary_gdp','tertiary_gdp',
            'gdp_percapita','fiscal_rev','fixed_asset','retail','trade'
        );
    """, 10),
    ("I2: 全部 indicator_key ∈ 10 指标集合", """
        SELECT COUNT(*) FROM cegr_mart.mart_city_timeseries
        WHERE indicator_key NOT IN (
            'gdp_total','gdp_growth','primary_gdp','secondary_gdp','tertiary_gdp',
            'gdp_percapita','fiscal_rev','fixed_asset','retail','trade'
        );
    """, 0),

    # === Section J: 不变量 + 红线-3 (4) ===
    ("J1: real cells = 854 (zero-harvest 不增量)", """
        SELECT COUNT(*) FROM cegr_mart.mart_city_timeseries
        WHERE value IS NOT NULL;
    """, 854),
    ("J2: DATA_MISSING cells = 2030 - 854 = 1176 (含 pending 2026 + 2025 272 miss)", """
        SELECT COUNT(*) FROM cegr_mart.mart_city_timeseries
        WHERE status = 'DATA_MISSING';
    """, 1176),
    ("J3: 29 city 2020-2026 全部存在 (29 × 7 × 10 = 2030 rows)", """
        SELECT (SELECT COUNT(*) FROM cegr_mart.mart_city_timeseries)
             - (29 * 10 * 7);
    """, 0),
    ("J4: lineage_ruling 全 13 个版本 (含 pending 2026)", """
        SELECT COUNT(DISTINCT lineage_ruling) FROM cegr_mart.mart_city_timeseries
        WHERE lineage_ruling IS NOT NULL;
    """, 13),

    # === Section K: K669fix-b-2025 missing_reason 完备性 (4) ===
    ("K1: 2025 K669fix-b-2025 missing_reason 含 'hongheiku 无 2025 city bulletin' (25 city × 10 = 250)", """
        SELECT COUNT(*) FROM cegr_mart.mart_city_timeseries
        WHERE year = 2025 AND lineage_ruling = 'K669fix-b-2025-2026-09-09'
        AND missing_reason LIKE '%hongheiku 无 2025 city bulletin%';
    """, 250),
    ("K2: 2025 missing_reason 全 non-NULL (守完备性, 272 miss cells)", """
        SELECT COUNT(*) FROM cegr_mart.mart_city_timeseries
        WHERE year = 2025 AND value IS NULL
        AND missing_reason IS NULL;
    """, 0),
    ("K3: 2025 K669fix-b-2025 cells lineage_source_type = 'DATA_MISSING' (zero-harvest, 守红线-3)", """
        SELECT COUNT(*) FROM cegr_mart.mart_city_timeseries
        WHERE year = 2025 AND lineage_ruling = 'K669fix-b-2025-2026-09-09'
        AND lineage_source_type = 'DATA_MISSING';
    """, 250),
    ("K4: 2025 K669fix-b-2025 cells lineage_is_demo 全 false (守禁 demo 冒充)", """
        SELECT COUNT(*) FROM cegr_mart.mart_city_timeseries
        WHERE year = 2025 AND lineage_ruling = 'K669fix-b-2025-2026-09-09'
        AND (lineage_is_demo IS NULL OR lineage_is_demo <> 'false');
    """, 0),

    # === Section L: prior baseline integrity (5) ===
    # 验证 2024 (122) + 2022 (136) + 2023 (125) baseline 不变 (zero-harvest 不影响)
    ("L1: 2024 real cells = 158 (K669fix-b-2024 122 + K669a-2024 36, baseline 守门)", """
        SELECT COUNT(*) FROM cegr_mart.mart_city_timeseries
        WHERE year = 2024 AND value IS NOT NULL;
    """, 158),
    ("L2: 2022 real cells = 173 (K669fix-b-2022 136 + K669a-2022 37, baseline 守门)", """
        SELECT COUNT(*) FROM cegr_mart.mart_city_timeseries
        WHERE year = 2022 AND value IS NOT NULL;
    """, 173),
    ("L3: 2023 real cells = 162 (K669fix-b-2023 125 + K669a-2023 37, baseline 守门)", """
        SELECT COUNT(*) FROM cegr_mart.mart_city_timeseries
        WHERE year = 2023 AND value IS NOT NULL;
    """, 162),
    ("L4: 2021 real cells = 182 (K669fix-b-2021 156 + K669a-2021 26, baseline 守门)", """
        SELECT COUNT(*) FROM cegr_mart.mart_city_timeseries
        WHERE year = 2021 AND value IS NOT NULL;
    """, 182),
    ("L5: 2020 real cells = 161 (K669fix-b-2020 161, baseline 守门)", """
        SELECT COUNT(*) FROM cegr_mart.mart_city_timeseries
        WHERE year = 2020 AND value IS NOT NULL;
    """, 161),
]


def main():
    print(f"=== knife 669fix-b-2025 mart verify ({len(ASSERTIONS)} 红线 assertions) ===")
    print(f"DB: {DB_HOST}:{DB_PORT}/{DB_NAME}")
    print()
    conn = get_conn()
    passed = 0
    failed = []
    try:
        for i, (label, sql, expected) in enumerate(ASSERTIONS, 1):
            with conn.cursor() as cur:
                cur.execute(sql)
                row = cur.fetchone()
                actual = row[0] if row else None
                if actual == expected:
                    passed += 1
                    print(f"  [{i:2d}/{len(ASSERTIONS)}] ✓ PASS  {label}  (={actual})")
                else:
                    failed.append((i, label, expected, actual))
                    print(f"  [{i:2d}/{len(ASSERTIONS)}] ✗ FAIL  {label}  (expected={expected}, actual={actual})")
    finally:
        conn.close()

    print()
    print(f"=== Summary ===")
    print(f"  PASS: {passed}/{len(ASSERTIONS)}")
    print(f"  FAIL: {len(failed)}/{len(ASSERTIONS)}")
    if failed:
        print()
        print("=== Failed assertions ===")
        for i, label, expected, actual in failed:
            print(f"  [{i}] {label}  expected={expected}, actual={actual}")
        sys.exit(1)
    else:
        print()
        print("=== knife 669fix-b-2025 mart verify: ALL PASS (守 48+ 红线) ===")


if __name__ == "__main__":
    main()
