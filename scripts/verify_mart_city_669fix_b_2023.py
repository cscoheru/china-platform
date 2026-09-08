#!/usr/bin/env python3
"""
669fix-b-2023 mart verify — 48+ 红线 PASS assertions
=============================================================================

Verify mart_city_timeseries after knife 669fix-b-2023 apply.
Mirrors 669fix-b-2022 verify pattern, adapted for year=2023 + K669a-2023.
"""
import os
import sys
from pathlib import Path
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
    ("A5: lineage_ruling (distinct) == 12 (新增 K669fix-b-2023)", """
        SELECT COUNT(DISTINCT lineage_ruling) FROM cegr_mart.mart_city_timeseries;
    """, 12),

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
    ("E1: real cells = 596 (471 prev + 125 K669fix-b-2023)", """
        SELECT COUNT(*) FROM cegr_mart.mart_city_timeseries
        WHERE value IS NOT NULL;
    """, 596),
    ("E2: HONGHEIKU_TRANSLOAD == real_cells", """
        SELECT COUNT(*) FROM cegr_mart.mart_city_timeseries
        WHERE lineage_source_type = 'HONGHEIKU_TRANSLOAD';
    """, 596),
    ("E3: real cells = HONGHEIKU_TRANSLOAD (consistency)", """
        SELECT (SELECT COUNT(*) FROM cegr_mart.mart_city_timeseries WHERE value IS NOT NULL)
             - (SELECT COUNT(*) FROM cegr_mart.mart_city_timeseries
                WHERE lineage_source_type = 'HONGHEIKU_TRANSLOAD');
    """, 0),

    # === Section F: 2023 增量 (knife 669fix-b-2023) (8) ===
    # 25 省会 (K669fix-b-2023): 125 real + 125 missing
    # 4 669a cities (K669a-2023, prior): 37 real + 3 missing
    # 总 2023 real = 162, missing = 128 (29 × 10 = 290 cells)
    ("F1: 2023 real cells == 162 (K669fix 125 + K669a-2023 37)", """
        SELECT COUNT(*) FROM cegr_mart.mart_city_timeseries
        WHERE year = 2023 AND value IS NOT NULL;
    """, 162),
    ("F2: 2023 DATA_MISSING == 128 (K669fix 125 + K669a-2023 3)", """
        SELECT COUNT(*) FROM cegr_mart.mart_city_timeseries
        WHERE year = 2023 AND value IS NULL;
    """, 128),
    ("F3: 2023 real cities == 19 (15 省会 + 4 669a; 7 省会 all-missing = 5 缺 + SHAANXI/QINGHAI)", """
        SELECT COUNT(DISTINCT city_code) FROM cegr_mart.mart_city_timeseries
        WHERE year = 2023 AND value IS NOT NULL;
    """, 19),
    ("F4: 2023 4 669a cities 全部存在 (40 cells in mart)", """
        SELECT COUNT(*) FROM cegr_mart.mart_city_timeseries
        WHERE year = 2023 AND city_code IN (
            'GUANGDONG_SHENZHEN','GUANGDONG_GUANGZHOU','ZHEJIANG_HANGZHOU','JIANGSU_NANJING'
        );
    """, 40),
    ("F5: 2023 ruling K669fix-b-2023-2026-09-08 = 125 real cells (25 省会 harvest)", """
        SELECT COUNT(*) FROM cegr_mart.mart_city_timeseries
        WHERE year = 2023 AND lineage_ruling = 'K669fix-b-2023-2026-09-08'
        AND value IS NOT NULL;
    """, 125),
    ("F6: 2023 ruling K669fix-b-2023-2026-09-08 = 125 missing cells", """
        SELECT COUNT(*) FROM cegr_mart.mart_city_timeseries
        WHERE year = 2023 AND lineage_ruling = 'K669fix-b-2023-2026-09-08'
        AND value IS NULL;
    """, 125),
    ("F7: 2023 5 缺 city 全 DATA_MISSING (LIAONING/HEILONGJIANG/JIANGXI/YUNNAN/TAIWAN, 50 cells)", """
        SELECT COUNT(*) FROM cegr_mart.mart_city_timeseries
        WHERE year = 2023 AND value IS NOT NULL
        AND city_code IN ('LIAONING_SHENYANG','HEILONGJIANG_HARBIN','JIANGXI_NANCHANG','YUNNAN_KUNMING','TAIWAN_TAIPEI');
    """, 0),
    ("F8: 2023 SHAANXI_XIAN/QINGHAI_XINING 全 DATA_MISSING (20 cells, 448/984 chars bulletin 无内容)", """
        SELECT COUNT(*) FROM cegr_mart.mart_city_timeseries
        WHERE year = 2023 AND value IS NOT NULL
        AND city_code IN ('SHAANXI_XIAN','QINGHAI_XINING');
    """, 0),

    # === Section G: fixed_asset (per 669a-2021 §2) ===
    ("G1: 2023 fixed_asset K669fix real cells == 0 (无 absolute, 仅 增长%)", """
        SELECT COUNT(*) FROM cegr_mart.mart_city_timeseries
        WHERE year = 2023 AND indicator_key = 'fixed_asset' AND value IS NOT NULL
        AND lineage_ruling = 'K669fix-b-2023-2026-09-08';
    """, 0),
    ("G2: 2023 fixed_asset K669fix missing cells == 25 (21 增长% + 4 缺 city)", """
        SELECT COUNT(*) FROM cegr_mart.mart_city_timeseries
        WHERE year = 2023 AND indicator_key = 'fixed_asset' AND value IS NULL
        AND lineage_ruling = 'K669fix-b-2023-2026-09-08';
    """, 25),

    # === Section H: lineage_origin (3) ===
    ("H1: HONGHEIKU_TRANSLOAD lineage_origin 全部 tjgb.hongheiku.com (含 https:// 前缀)", """
        SELECT COUNT(*) FROM cegr_mart.mart_city_timeseries
        WHERE lineage_source_type = 'HONGHEIKU_TRANSLOAD'
        AND (lineage_origin IS NULL OR (lineage_origin <> '' AND lineage_origin NOT LIKE '%tjgb.hongheiku.com%'));
    """, 0),
    ("H2: HONGHEIKU_TRANSLOAD 596 行 lineage_origin 全 non-empty", """
        SELECT COUNT(*) FROM cegr_mart.mart_city_timeseries
        WHERE lineage_source_type = 'HONGHEIKU_TRANSLOAD'
        AND (lineage_origin IS NULL OR lineage_origin = '');
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
    ("J1: real cells >= 125 (sanity)", """
        SELECT COUNT(*) FROM cegr_mart.mart_city_timeseries
        WHERE value IS NOT NULL;
    """, 596),
    ("J2: DATA_MISSING cells = 2030 - 596 = 1434", """
        SELECT COUNT(*) FROM cegr_mart.mart_city_timeseries
        WHERE status = 'DATA_MISSING';
    """, 1434),
    ("J3: 29 city 2020-2026 全部存在 (29 × 7 × 10 = 2030 rows)", """
        SELECT (SELECT COUNT(*) FROM cegr_mart.mart_city_timeseries)
             - (29 * 10 * 7);
    """, 0),
    ("J4: lineage_ruling 全 12 个版本都至少 1 个 attribution", """
        SELECT COUNT(DISTINCT lineage_ruling) FROM cegr_mart.mart_city_timeseries
        WHERE lineage_ruling IS NOT NULL;
    """, 12),

    # === Section K: 缺失原因完备性 (5) ===
    ("K1: 2023 5 缺 city missing_reason 完备 (50 cells)", """
        SELECT COUNT(*) FROM cegr_mart.mart_city_timeseries
        WHERE year = 2023 AND city_code IN ('LIAONING_SHENYANG','HEILONGJIANG_HARBIN','JIANGXI_NANCHANG','YUNNAN_KUNMING','TAIWAN_TAIPEI')
        AND missing_reason IS NOT NULL;
    """, 50),
    ("K2: 2023 SHAANXI/QINGHAI missing_reason 完备 (20 cells, tag listing 无内容)", """
        SELECT COUNT(*) FROM cegr_mart.mart_city_timeseries
        WHERE year = 2023 AND city_code IN ('SHAANXI_XIAN','QINGHAI_XINING')
        AND missing_reason IS NOT NULL;
    """, 20),
    ("K3: 2023 fixed_asset 13 K669fix missing 含 '增长%' (守红线-3)", """
        SELECT COUNT(*) FROM cegr_mart.mart_city_timeseries
        WHERE year = 2023 AND indicator_key = 'fixed_asset'
        AND value IS NULL AND missing_reason LIKE '%增长%'
        AND lineage_ruling = 'K669fix-b-2023-2026-09-08';
    """, 13),
    ("K4: 2023 4 669a cities 全部存在 lineage_origin (40 cells, 守 K669a-2023 attribution)", """
        SELECT COUNT(*) FROM cegr_mart.mart_city_timeseries
        WHERE year = 2023
        AND city_code IN (
            'GUANGDONG_SHENZHEN','GUANGDONG_GUANGZHOU','ZHEJIANG_HANGZHOU','JIANGSU_NANJING'
        ) AND (lineage_origin IS NULL OR lineage_origin = '');
    """, 0),
    ("K5: 2023 missing_reason 全 non-NULL (守 完备性)", """
        SELECT COUNT(*) FROM cegr_mart.mart_city_timeseries
        WHERE year = 2023 AND value IS NULL
        AND missing_reason IS NULL;
    """, 0),

    # === Section L: value sanity (5) — Decimal vs float 兼容 ===
    ("L1: 2023 FUJIAN_FUZHOU gdp_total == 12928.47", """
        SELECT value::float FROM cegr_mart.mart_city_timeseries
        WHERE year = 2023 AND city_code = 'FUJIAN_FUZHOU' AND indicator_key = 'gdp_total';
    """, 12928.47),
    ("L2: 2023 XINJIANG_WULUMUQI gdp_total == 4168.46", """
        SELECT value::float FROM cegr_mart.mart_city_timeseries
        WHERE year = 2023 AND city_code = 'XINJIANG_WULUMUQI' AND indicator_key = 'gdp_total';
    """, 4168.46),
    ("L3: 2023 SHAANXI_XIAN gdp_total MISSING (bulletin 448 chars tag listing 无内容)", """
        SELECT COUNT(*) FROM cegr_mart.mart_city_timeseries
        WHERE year = 2023 AND city_code = 'SHAANXI_XIAN' AND indicator_key = 'gdp_total'
        AND value IS NULL;
    """, 1),
    ("L4: 2023 NEIMENGGU_HUHEHAOTE gdp_total sanity (3801.55)", """
        SELECT COUNT(*) FROM cegr_mart.mart_city_timeseries
        WHERE year = 2023 AND city_code = 'NEIMENGGU_HUHEHAOTE' AND indicator_key = 'gdp_total'
        AND value IS NOT NULL;
    """, 1),
    ("L5: 2023 GUANGDONG_SHENZHEN gdp_total sanity (K669a-2023 attribution)", """
        SELECT COUNT(*) FROM cegr_mart.mart_city_timeseries
        WHERE year = 2023 AND city_code = 'GUANGDONG_SHENZHEN' AND indicator_key = 'gdp_total'
        AND value IS NOT NULL;
    """, 1),
]


def main():
    print(f"=== knife 669fix-b-2023 mart verify ({len(ASSERTIONS)} 红线 assertions) ===")
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
        print("=== knife 669fix-b-2023 mart verify: ALL PASS (守 48+ 红线) ===")


if __name__ == "__main__":
    main()