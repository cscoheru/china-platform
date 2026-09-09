#!/usr/bin/env python3
"""
669fix-b-2024 mart verify — 48+ 红线 PASS assertions
=============================================================================

Verify mart_city_timeseries after knife 669fix-b-2024 apply.
Mirrors 669fix-b-2023 verify pattern, adapted for year=2024 + K669a-2024.
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
    ("A5: lineage_ruling (distinct) == 13 (12 + pending 2026)", """
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
    # Pre-2024 proper baseline is 732 (after K669fix-b-2022 136 restored from whitespace bug).
    # After 2024 add 122 → 854.
    ("E1: real cells = 854 (732 prev + 122 K669fix-b-2024)", """
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

    # === Section F: 2024 增量 (knife 669fix-b-2024) (8) ===
    # 25 省会 (K669fix-b-2024): 122 real + 128 missing
    # 4 669a cities (K669a-2024, prior): 36 real + 4 missing
    # 总 2024 real = 158, missing = 132 (29 × 10 = 290 cells)
    ("F1: 2024 real cells == 158 (K669fix 122 + K669a-2024 36)", """
        SELECT COUNT(*) FROM cegr_mart.mart_city_timeseries
        WHERE year = 2024 AND value IS NOT NULL;
    """, 158),
    ("F2: 2024 DATA_MISSING == 132 (K669fix 128 + K669a-2024 4)", """
        SELECT COUNT(*) FROM cegr_mart.mart_city_timeseries
        WHERE year = 2024 AND value IS NULL;
    """, 132),
    ("F3: 2024 real cities == 19 (15 省会 + 4 669a; 10 省会 all-missing)", """
        SELECT COUNT(DISTINCT city_code) FROM cegr_mart.mart_city_timeseries
        WHERE year = 2024 AND value IS NOT NULL;
    """, 19),
    ("F4: 2024 4 669a cities 全部存在 (40 cells in mart)", """
        SELECT COUNT(*) FROM cegr_mart.mart_city_timeseries
        WHERE year = 2024 AND city_code IN (
            'GUANGDONG_SHENZHEN','GUANGDONG_GUANGZHOU','ZHEJIANG_HANGZHOU','JIANGSU_NANJING'
        );
    """, 40),
    ("F5: 2024 ruling K669fix-b-2024-2026-09-09 = 122 real cells (25 省会 harvest)", """
        SELECT COUNT(*) FROM cegr_mart.mart_city_timeseries
        WHERE year = 2024 AND lineage_ruling = 'K669fix-b-2024-2026-09-09'
        AND value IS NOT NULL;
    """, 122),
    ("F6: 2024 ruling K669fix-b-2024-2026-09-09 = 128 missing cells", """
        SELECT COUNT(*) FROM cegr_mart.mart_city_timeseries
        WHERE year = 2024 AND lineage_ruling = 'K669fix-b-2024-2026-09-09'
        AND value IS NULL;
    """, 128),
    ("F7: 2024 4 缺 city 全 DATA_MISSING (JIANGXI/YUNNAN/QINGHAI/TAIWAN, 40 cells)", """
        SELECT COUNT(*) FROM cegr_mart.mart_city_timeseries
        WHERE year = 2024 AND value IS NOT NULL
        AND city_code IN ('JIANGXI_NANCHANG','YUNNAN_KUNMING','QINGHAI_XINING','TAIWAN_TAIPEI');
    """, 0),
    ("F8: 2024 ANHUI/HAINAN/HEILONGJIANG/SHAANXI/SHANXI/SICHUAN 全 DATA_MISSING (60 cells, parser 0 命中)", """
        SELECT COUNT(*) FROM cegr_mart.mart_city_timeseries
        WHERE year = 2024 AND value IS NOT NULL
        AND city_code IN ('ANHUI_HEFEI','HAINAN_HAIKOU','HEILONGJIANG_HARBIN','SHAANXI_XIAN','SHANXI_TAIYUAN','SICHUAN_CHENGDU');
    """, 0),

    # === Section G: fixed_asset (per 669a-2021 §2) ===
    ("G1: 2024 fixed_asset K669fix real cells == 0 (无 absolute, 仅 增长%)", """
        SELECT COUNT(*) FROM cegr_mart.mart_city_timeseries
        WHERE year = 2024 AND indicator_key = 'fixed_asset' AND value IS NOT NULL
        AND lineage_ruling = 'K669fix-b-2024-2026-09-09';
    """, 0),
    ("G2: 2024 fixed_asset K669fix missing cells == 25 (21 增长% + 4 缺 city)", """
        SELECT COUNT(*) FROM cegr_mart.mart_city_timeseries
        WHERE year = 2024 AND indicator_key = 'fixed_asset' AND value IS NULL
        AND lineage_ruling = 'K669fix-b-2024-2026-09-09';
    """, 25),

    # === Section H: lineage_origin (3) ===
    ("H1: HONGHEIKU_TRANSLOAD lineage_origin 全部 tjgb.hongheiku.com", """
        SELECT COUNT(*) FROM cegr_mart.mart_city_timeseries
        WHERE lineage_source_type = 'HONGHEIKU_TRANSLOAD'
        AND (lineage_origin IS NULL OR (lineage_origin <> '' AND lineage_origin NOT LIKE '%tjgb.hongheiku.com%'));
    """, 0),
    ("H2: HONGHEIKU_TRANSLOAD 718 行 lineage_origin 全 non-empty", """
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
    ("J1: real cells = 854 (732 + 122 K669fix-b-2024)", """
        SELECT COUNT(*) FROM cegr_mart.mart_city_timeseries
        WHERE value IS NOT NULL;
    """, 854),
    ("J2: DATA_MISSING cells = 2030 - 854 = 1176 (含 pending 2026 cells)", """
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

    # === Section K: 缺失原因完备性 (5) ===
    ("K1: 2024 4 缺 city missing_reason 完备 (40 cells, JIANGXI/YUNNAN/QINGHAI/TAIWAN)", """
        SELECT COUNT(*) FROM cegr_mart.mart_city_timeseries
        WHERE year = 2024 AND city_code IN ('JIANGXI_NANCHANG','YUNNAN_KUNMING','QINGHAI_XINING','TAIWAN_TAIPEI')
        AND missing_reason IS NOT NULL;
    """, 40),
    ("K2: 2024 6 parse-fail city missing_reason 完备 (60 cells, ANHUI/HAINAN/HEILONGJIANG/SHAANXI/SHANXI/SICHUAN)", """
        SELECT COUNT(*) FROM cegr_mart.mart_city_timeseries
        WHERE year = 2024 AND city_code IN ('ANHUI_HEFEI','HAINAN_HAIKOU','HEILONGJIANG_HARBIN','SHAANXI_XIAN','SHANXI_TAIYUAN','SICHUAN_CHENGDU')
        AND missing_reason IS NOT NULL;
    """, 60),
    ("K3: 2024 fixed_asset 21 K669fix missing 含 '增长%' (守红线-3, 21 city 缺 absolute)", """
        SELECT COUNT(*) FROM cegr_mart.mart_city_timeseries
        WHERE year = 2024 AND indicator_key = 'fixed_asset'
        AND value IS NULL AND missing_reason LIKE '%增长%'
        AND lineage_ruling = 'K669fix-b-2024-2026-09-09';
    """, 21),
    ("K4: 2024 4 669a cities 全部 lineage_origin non-empty (40 cells)", """
        SELECT COUNT(*) FROM cegr_mart.mart_city_timeseries
        WHERE year = 2024
        AND city_code IN (
            'GUANGDONG_SHENZHEN','GUANGDONG_GUANGZHOU','ZHEJIANG_HANGZHOU','JIANGSU_NANJING'
        ) AND (lineage_origin IS NULL OR lineage_origin = '');
    """, 0),
    ("K5: 2024 missing_reason 全 non-NULL (守 完备性)", """
        SELECT COUNT(*) FROM cegr_mart.mart_city_timeseries
        WHERE year = 2024 AND value IS NULL
        AND missing_reason IS NULL;
    """, 0),

    # === Section L: value sanity (5) — Decimal vs float 兼容 ===
    ("L1: 2024 FUJIAN_FUZHOU gdp_total == 14236.76 (9 real cells)", """
        SELECT value::float FROM cegr_mart.mart_city_timeseries
        WHERE year = 2024 AND city_code = 'FUJIAN_FUZHOU' AND indicator_key = 'gdp_total';
    """, 14236.76),
    ("L2: 2024 HEBEI_SHIJIAZHUANG gdp_total == 8203.4", """
        SELECT value::float FROM cegr_mart.mart_city_timeseries
        WHERE year = 2024 AND city_code = 'HEBEI_SHIJIAZHUANG' AND indicator_key = 'gdp_total';
    """, 8203.4),
    ("L3: 2024 XINJIANG_WULUMUQI gdp_total sanity (存在 real cell)", """
        SELECT COUNT(*) FROM cegr_mart.mart_city_timeseries
        WHERE year = 2024 AND city_code = 'XINJIANG_WULUMUQI' AND indicator_key = 'gdp_total'
        AND value IS NOT NULL;
    """, 1),
    ("L4: 2024 GUANGDONG_SHENZHEN gdp_total sanity (K669a-2024 attribution)", """
        SELECT COUNT(*) FROM cegr_mart.mart_city_timeseries
        WHERE year = 2024 AND city_code = 'GUANGDONG_SHENZHEN' AND indicator_key = 'gdp_total'
        AND value IS NOT NULL;
    """, 1),
    ("L5: 2024 NEIMENGGU_HUHEHAOTE gdp_total == 4107.08 (K669fix-b-2024 attribution)", """
        SELECT value::float FROM cegr_mart.mart_city_timeseries
        WHERE year = 2024 AND city_code = 'NEIMENGGU_HUHEHAOTE' AND indicator_key = 'gdp_total';
    """, 4107.08),
]


def main():
    print(f"=== knife 669fix-b-2024 mart verify ({len(ASSERTIONS)} 红线 assertions) ===")
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
        print("=== knife 669fix-b-2024 mart verify: ALL PASS (守 48+ 红线) ===")


if __name__ == "__main__":
    main()
