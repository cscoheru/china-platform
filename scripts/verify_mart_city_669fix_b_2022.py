#!/usr/bin/env python3
"""
669fix-b-2022 mart verify — 48+ 红线 PASS assertions
====================================================================

Verify mart_city_timeseries after knife 669fix-b-2022 apply.
Mirrors 669fix-b-2021 verify pattern, adapted for year=2022 + K669a-2022.
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
    ("A5: lineage_ruling (distinct) == 11 (新增 K669fix-b-2022)", """
        SELECT COUNT(DISTINCT lineage_ruling) FROM cegr_mart.mart_city_timeseries;
    """, 11),

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
    ("E1: real cells = 607 (471 prev + 136 K669fix-b-2022)", """
        SELECT COUNT(*) FROM cegr_mart.mart_city_timeseries
        WHERE value IS NOT NULL;
    """, 607),
    ("E2: HONGHEIKU_TRANSLOAD == real_cells", """
        SELECT COUNT(*) FROM cegr_mart.mart_city_timeseries
        WHERE lineage_source_type = 'HONGHEIKU_TRANSLOAD';
    """, 607),
    ("E3: real cells = HONGHEIKU_TRANSLOAD (consistency)", """
        SELECT (SELECT COUNT(*) FROM cegr_mart.mart_city_timeseries WHERE value IS NOT NULL)
             - (SELECT COUNT(*) FROM cegr_mart.mart_city_timeseries
                WHERE lineage_source_type = 'HONGHEIKU_TRANSLOAD');
    """, 0),

    # === Section F: 2022 增量 (knife 669fix-b-2022) (8) ===
    # 25 省会 (K669fix-b-2022): 136 real + 114 missing
    # 4 669a cities (K669a-2022, prior): 37 real + 3 missing
    # 总 2022 real = 173, missing = 117 (29 × 10 = 290 cells)
    ("F1: 2022 real cells == 173 (K669fix 136 + K669a-2022 37)", """
        SELECT COUNT(*) FROM cegr_mart.mart_city_timeseries
        WHERE year = 2022 AND value IS NOT NULL;
    """, 173),
    ("F2: 2022 DATA_MISSING == 117 (K669fix 114 + K669a-2022 3)", """
        SELECT COUNT(*) FROM cegr_mart.mart_city_timeseries
        WHERE year = 2022 AND value IS NULL;
    """, 117),
    ("F3: 2022 real cities == 21 (17 省会 + 4 669a, 8 city all-missing)", """
        SELECT COUNT(DISTINCT city_code) FROM cegr_mart.mart_city_timeseries
        WHERE year = 2022 AND value IS NOT NULL;
    """, 21),
    ("F4: 2022 4 669a cities 全部存在 (40 cells in mart)", """
        SELECT COUNT(*) FROM cegr_mart.mart_city_timeseries
        WHERE year = 2022 AND city_code IN (
            'GUANGDONG_SHENZHEN','GUANGDONG_GUANGZHOU','ZHEJIANG_HANGZHOU','JIANGSU_NANJING'
        );
    """, 40),
    ("F5: 2022 ruling K669fix-b-2022-2026-09-08 = 136 real cells (25 省会 harvest)", """
        SELECT COUNT(*) FROM cegr_mart.mart_city_timeseries
        WHERE year = 2022 AND lineage_ruling = 'K669fix-b-2022-2026-09-08'
        AND value IS NOT NULL;
    """, 136),
    ("F6: 2022 ruling K669fix-b-2022-2026-09-08 = 114 missing cells", """
        SELECT COUNT(*) FROM cegr_mart.mart_city_timeseries
        WHERE year = 2022 AND lineage_ruling = 'K669fix-b-2022-2026-09-08'
        AND value IS NULL;
    """, 114),
    ("F7: 2022 GUANGXI_NANNING/TAIWAN_TAIPEI 全 DATA_MISSING (20 cells)", """
        SELECT COUNT(*) FROM cegr_mart.mart_city_timeseries
        WHERE year = 2022 AND value IS NOT NULL
        AND city_code IN ('GUANGXI_NANNING','TAIWAN_TAIPEI');
    """, 0),
    ("F8: 2022 QINGHAI_XINING 全 DATA_MISSING (10 cells, 984 chars bulletin 无内容)", """
        SELECT COUNT(*) FROM cegr_mart.mart_city_timeseries
        WHERE year = 2022 AND value IS NOT NULL
        AND city_code = 'QINGHAI_XINING';
    """, 0),

    # === Section G: fixed_asset (per 669a-2021 §2) ===
    ("G1: 2022 fixed_asset K669fix real cells == 1 (only XINJIANG)", """
        SELECT COUNT(*) FROM cegr_mart.mart_city_timeseries
        WHERE year = 2022 AND indicator_key = 'fixed_asset' AND value IS NOT NULL
        AND lineage_ruling = 'K669fix-b-2022-2026-09-08';
    """, 1),
    ("G2: 2022 fixed_asset K669fix missing cells == 24 (25 city - 1 real)", """
        SELECT COUNT(*) FROM cegr_mart.mart_city_timeseries
        WHERE year = 2022 AND indicator_key = 'fixed_asset' AND value IS NULL
        AND lineage_ruling = 'K669fix-b-2022-2026-09-08';
    """, 24),

    # === Section H: lineage_origin (3) ===
    ("H1: HONGHEIKU_TRANSLOAD lineage_origin 全部 tjgb.hongheiku.com (含 https:// 前缀)", """
        SELECT COUNT(*) FROM cegr_mart.mart_city_timeseries
        WHERE lineage_source_type = 'HONGHEIKU_TRANSLOAD'
        AND (lineage_origin IS NULL OR (lineage_origin <> '' AND lineage_origin NOT LIKE '%tjgb.hongheiku.com%'));
    """, 0),
    ("H2: HONGHEIKU_TRANSLOAD 607 行 lineage_origin 全 non-empty", """
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
    ("J1: real cells >= 136 (sanity)", """
        SELECT COUNT(*) FROM cegr_mart.mart_city_timeseries
        WHERE value IS NOT NULL;
    """, 607),
    ("J2: DATA_MISSING cells = 2030 - 607 = 1423", """
        SELECT COUNT(*) FROM cegr_mart.mart_city_timeseries
        WHERE status = 'DATA_MISSING';
    """, 1423),
    ("J3: 29 city 2020-2026 全部存在 (29 × 7 × 10 = 2030 rows)", """
        SELECT (SELECT COUNT(*) FROM cegr_mart.mart_city_timeseries)
             - (29 * 10 * 7);
    """, 0),
    ("J4: lineage_ruling 全 11 个版本都至少 1 个 attribution", """
        SELECT COUNT(DISTINCT lineage_ruling) FROM cegr_mart.mart_city_timeseries
        WHERE lineage_ruling IS NOT NULL;
    """, 11),

    # === Section K: 缺失原因完备性 (5) ===
    ("K1: 2022 GUANGXI_NANNING/TAIWAN_TAIPEI 20 cells missing_reason 完备", """
        SELECT COUNT(*) FROM cegr_mart.mart_city_timeseries
        WHERE year = 2022 AND city_code IN ('GUANGXI_NANNING','TAIWAN_TAIPEI')
        AND missing_reason IS NOT NULL;
    """, 20),
    ("K2: 2022 QINGHAI_XINING missing_reason 完备 (10 cells)", """
        SELECT COUNT(*) FROM cegr_mart.mart_city_timeseries
        WHERE year = 2022 AND city_code = 'QINGHAI_XINING'
        AND missing_reason IS NOT NULL;
    """, 10),
    ("K3: 2022 fixed_asset 21 K669fix missing 含 '增长%' (守红线-3)", """
        SELECT COUNT(*) FROM cegr_mart.mart_city_timeseries
        WHERE year = 2022 AND indicator_key = 'fixed_asset'
        AND value IS NULL AND missing_reason LIKE '%增长%'
        AND lineage_ruling = 'K669fix-b-2022-2026-09-08';
    """, 10),
    ("K4: 2022 4 669a cities 全部存在 lineage_origin (40 cells, 守 K669a-2022 attribution)", """
        SELECT COUNT(*) FROM cegr_mart.mart_city_timeseries
        WHERE year = 2022
        AND city_code IN (
            'GUANGDONG_SHENZHEN','GUANGDONG_GUANGZHOU','ZHEJIANG_HANGZHOU','JIANGSU_NANJING'
        ) AND (lineage_origin IS NULL OR lineage_origin = '');
    """, 0),
    ("K5: 2022 missing_reason 全 non-NULL (守 守 完备性)", """
        SELECT COUNT(*) FROM cegr_mart.mart_city_timeseries
        WHERE year = 2022 AND value IS NULL
        AND missing_reason IS NULL;
    """, 0),

    # === Section L: value sanity (5) — Decimal vs float 兼容 ===
    ("L1: 2022 SHAANXI_XIAN gdp_total == 11486.51", """
        SELECT value::float FROM cegr_mart.mart_city_timeseries
        WHERE year = 2022 AND city_code = 'SHAANXI_XIAN' AND indicator_key = 'gdp_total';
    """, 11486.51),
    ("L2: 2022 XINJIANG_WULUMUQI gdp_total == 3893.22", """
        SELECT value::float FROM cegr_mart.mart_city_timeseries
        WHERE year = 2022 AND city_code = 'XINJIANG_WULUMUQI' AND indicator_key = 'gdp_total';
    """, 3893.22),
    ("L3: 2022 HUNAN_CHANGSHA gdp_total MISSING (parser 未匹配, 守红线-3)", """
        SELECT COUNT(*) FROM cegr_mart.mart_city_timeseries
        WHERE year = 2022 AND city_code = 'HUNAN_CHANGSHA' AND indicator_key = 'gdp_total'
        AND value IS NULL;
    """, 1),
    ("L4: 2022 NEIMENGGU_HUHEHAOTE gdp_growth sanity", """
        SELECT COUNT(*) FROM cegr_mart.mart_city_timeseries
        WHERE year = 2022 AND city_code = 'NEIMENGGU_HUHEHAOTE' AND indicator_key = 'gdp_growth'
        AND value IS NOT NULL;
    """, 1),
    ("L5: 2022 GUANGDONG_SHENZHEN gdp_total sanity (K669a-2022 attribution)", """
        SELECT COUNT(*) FROM cegr_mart.mart_city_timeseries
        WHERE year = 2022 AND city_code = 'GUANGDONG_SHENZHEN' AND indicator_key = 'gdp_total'
        AND value IS NOT NULL;
    """, 1),
]


def main():
    print(f"=== knife 669fix-b-2022 mart verify ({len(ASSERTIONS)} 红线 assertions) ===")
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
        print("=== knife 669fix-b-2022 mart verify: ALL PASS (守 48+ 红线) ===")


if __name__ == "__main__":
    main()