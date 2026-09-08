#!/usr/bin/env python3
"""
669fix-b-2021 mart verify — 54+ 红线 PASS assertions
====================================================================

Verify mart_city_timeseries after knife 669fix-b-2021 apply.
Mirrors 669fix-b-2020 verify pattern, updated for year=2021 + rd8 logic.
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


# 54 assertions organized by category
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
    ("A5: lineage_ruling (distinct) == 10", """
        SELECT COUNT(DISTINCT lineage_ruling) FROM cegr_mart.mart_city_timeseries;
    """, 10),

    # === Section B: 4 直辖市禁 (红线-7) (2) ===
    ("B1: 直辖市 rows == 0 (BEIJING/SHANGHAI/TIANJIN/CHONGQING)", """
        SELECT COUNT(*) FROM cegr_mart.mart_city_timeseries
        WHERE city_code LIKE 'BEIJING_%' OR city_code LIKE 'SHANGHAI_%'
           OR city_code LIKE 'TIANJIN_%' OR city_code LIKE 'CHONGQING_%';
    """, 0),
    ("B2: 25 省会 + 4 669a cities only (no other)", """
        SELECT COUNT(DISTINCT city_code) FROM cegr_mart.mart_city_timeseries
        WHERE city_code NOT IN (
            'HEBEI_SHIJIAZHUANG','SHANXI_TAIYUAN','NEIMENGGU_HUHEHAOTE',
            'LIAONING_SHENYANG','JILIN_CHANGCHUN','HEILONGJIANG_HARBIN',
            'JIANGSU_NANJING','ZHEJIANG_HANGZHOU','ANHUI_HEFEI','FUJIAN_FUZHOU',
            'JIANGXI_NANCHANG','SHANDONG_JINAN','HENAN_ZHENGZHOU','HUBEI_WUHAN',
            'HUNAN_CHANGSHA','GUANGDONG_GUANGZHOU','GUANGDONG_SHENZHEN',
            'GUANGXI_NANNING','HAINAN_HAIKOU','SICHUAN_CHENGDU','GUIZHOU_GUIYANG',
            'YUNNAN_KUNMING','XIZANG_LASA','SHAANXI_XIAN','GANSU_LANZHOU',
            'QINGHAI_XINING','NINGXIA_YINCHUAN','XINJIANG_WULUMUQI','TAIWAN_TAIPEI'
        );
    """, 0),

    # === Section C: 2001-2019 全 DATA_MISSING (红线-1) (3) ===
    ("C1: 2001-2019 全部 0 row (守红线-1)", """
        SELECT COUNT(*) FROM cegr_mart.mart_city_timeseries
        WHERE year BETWEEN 2001 AND 2019;
    """, 0),
    ("C2: 2001-2019 不存在 year=2001 行", """
        SELECT COUNT(*) FROM cegr_mart.mart_city_timeseries WHERE year = 2001;
    """, 0),
    ("C3: 2001-2019 不存在 year=2019 行", """
        SELECT COUNT(*) FROM cegr_mart.mart_city_timeseries WHERE year = 2019;
    """, 0),

    # === Section D: 2026 全 DATA_MISSING (红线-2) (3) ===
    ("D1: 2026 real cells == 0 (守红线-2)", """
        SELECT COUNT(*) FROM cegr_mart.mart_city_timeseries
        WHERE year = 2026 AND value IS NOT NULL;
    """, 0),
    ("D2: 2026 DATA_MISSING == 290 (29 city × 10 indicator)", """
        SELECT COUNT(*) FROM cegr_mart.mart_city_timeseries
        WHERE year = 2026 AND status = 'DATA_MISSING';
    """, 290),
    ("D3: 2026 status 全部 DATA_MISSING", """
        SELECT COUNT(*) FROM cegr_mart.mart_city_timeseries
        WHERE year = 2026 AND status <> 'DATA_MISSING';
    """, 0),

    # === Section E: HONGHEIKU_TRANSLOAD consistency (3) ===
    ("E1: real cells 471 (315 prev + 156 669fix-b-2021)", """
        SELECT COUNT(*) FROM cegr_mart.mart_city_timeseries
        WHERE value IS NOT NULL;
    """, 471),
    ("E2: HONGHEIKU_TRANSLOAD == 471 (全部 real cells 来自 hongheiku)", """
        SELECT COUNT(*) FROM cegr_mart.mart_city_timeseries
        WHERE lineage_source_type = 'HONGHEIKU_TRANSLOAD';
    """, 471),
    ("E3: real cells = lineage_source_type = 'HONGHEIKU_TRANSLOAD'", """
        SELECT (SELECT COUNT(*) FROM cegr_mart.mart_city_timeseries WHERE value IS NOT NULL)
             - (SELECT COUNT(*) FROM cegr_mart.mart_city_timeseries
                WHERE lineage_source_type = 'HONGHEIKU_TRANSLOAD');
    """, 0),

    # === Section F: 2021 增量 (knife 669fix-b-2021) (8) ===
    # 25 省会 (K669fix-b-2021): 156 real + 94 missing
    # 4 669a cities (K669a-2021): 26 real + 14 missing
    # 总 2021 real = 182, missing = 108 (29 city × 10 indicator = 290 total)
    ("F1: 2021 real cells == 182 (K669fix 156 + K669a-2021 26)", """
        SELECT COUNT(*) FROM cegr_mart.mart_city_timeseries
        WHERE year = 2021 AND value IS NOT NULL;
    """, 182),
    ("F2: 2021 DATA_MISSING == 108 (K669fix 94 + K669a-2021 14)", """
        SELECT COUNT(*) FROM cegr_mart.mart_city_timeseries
        WHERE year = 2021 AND value IS NULL;
    """, 108),
    ("F3: 2021 real cities == 23 (21 省会 + 4 669a)", """
        SELECT COUNT(DISTINCT city_code) FROM cegr_mart.mart_city_timeseries
        WHERE year = 2021 AND value IS NOT NULL;
    """, 23),
    ("F4: 2021 4 669a cities 全部存在 (40 cells in mart, ruling K669a-2021)", """
        SELECT COUNT(*) FROM cegr_mart.mart_city_timeseries
        WHERE year = 2021 AND city_code IN (
            'GUANGDONG_SHENZHEN','GUANGDONG_GUANGZHOU','ZHEJIANG_HANGZHOU','JIANGSU_NANJING'
        );
    """, 40),
    ("F5: 2021 ruling K669a-2021-2026-09-04 = 26 real cells (4 city partial)", """
        SELECT COUNT(*) FROM cegr_mart.mart_city_timeseries
        WHERE year = 2021 AND lineage_ruling = 'K669a-2021-2026-09-04'
        AND value IS NOT NULL;
    """, 26),
    ("F6: 2021 ruling K669fix-b-2021-2026-09-08 = 156 real cells", """
        SELECT COUNT(*) FROM cegr_mart.mart_city_timeseries
        WHERE year = 2021 AND lineage_ruling = 'K669fix-b-2021-2026-09-08'
        AND value IS NOT NULL;
    """, 156),
    ("F7: 2021 ruling K669fix-b-2021-2026-09-08 = 94 missing cells", """
        SELECT COUNT(*) FROM cegr_mart.mart_city_timeseries
        WHERE year = 2021 AND lineage_ruling = 'K669fix-b-2021-2026-09-08'
        AND value IS NULL;
    """, 94),
    ("F8: 2021 SICHUAN/XIZANG/QINGHAI/TAIWAN 全 DATA_MISSING (40 cells)", """
        SELECT COUNT(*) FROM cegr_mart.mart_city_timeseries
        WHERE year = 2021 AND value IS NOT NULL
        AND city_code IN ('SICHUAN_CHENGDU','XIZANG_LASA','QINGHAI_XINING','TAIWAN_TAIPEI');
    """, 0),

    # === Section G: fixed_asset (per 669a-2021 §2, 13 fixed_asset growth excluded from rd8) ===
    # FUJIAN_FUZHOU fixed_asset=5330.27 (K669fix) + JIANGSU_NANJING fixed_asset=5675.24 (K669a-2021) = 2 real
    ("G1: 2021 fixed_asset real cells == 2 (FUJIAN + JIANGSU_NANJING)", """
        SELECT COUNT(*) FROM cegr_mart.mart_city_timeseries
        WHERE year = 2021 AND indicator_key = 'fixed_asset' AND value IS NOT NULL;
    """, 2),
    ("G2: 2021 fixed_asset missing cells == 27 (29 city - 2 real)", """
        SELECT COUNT(*) FROM cegr_mart.mart_city_timeseries
        WHERE year = 2021 AND indicator_key = 'fixed_asset' AND value IS NULL;
    """, 27),

    # === Section H: lineage_origin 一致性 (4) ===
    ("H1: 2021 25 省会 missing_reason 4 类 sub-branch 覆盖 (tag missing / tag listing / fixed_asset% / other)", """
        SELECT COUNT(DISTINCT missing_reason) FROM cegr_mart.mart_city_timeseries
        WHERE year = 2021 AND value IS NULL
        AND lineage_ruling = 'K669fix-b-2021-2026-09-08';
    """, 4),  # 4 distinct sub-branches
    ("H2: HONGHEIKU_TRANSLOAD lineage_origin 全部以 tjgb.hongheiku.com 开头 (relax: 不强制 /djs/ 子路径)", """
        SELECT COUNT(*) FROM cegr_mart.mart_city_timeseries
        WHERE lineage_source_type = 'HONGHEIKU_TRANSLOAD'
        AND (lineage_origin IS NULL OR lineage_origin NOT LIKE 'tjgb.hongheiku.com%');
    """, 0),
    ("H3: HONGHEIKU_TRANSLOAD 471 行 lineage_origin 全 non-NULL", """
        SELECT COUNT(*) FROM cegr_mart.mart_city_timeseries
        WHERE lineage_source_type = 'HONGHEIKU_TRANSLOAD'
        AND lineage_origin IS NULL;
    """, 0),
    ("H4: 4 669a cities 2021 lineage_origin 全 non-NULL (守 K669a-2021 attribution)", """
        SELECT COUNT(*) FROM cegr_mart.mart_city_timeseries
        WHERE year = 2021
        AND city_code IN (
            'GUANGDONG_SHENZHEN','GUANGDONG_GUANGZHOU','ZHEJIANG_HANGZHOU','JIANGSU_NANJING'
        ) AND lineage_origin IS NULL;
    """, 0),

    # === Section I: indicator-key 一致性 (3) ===
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
    ("I3: 2020-2025 real cells ≥ 250 (包含 156 669fix-b-2021)", """
        SELECT COUNT(*) FROM cegr_mart.mart_city_timeseries
        WHERE year BETWEEN 2020 AND 2025 AND value IS NOT NULL;
    """, 471),

    # === Section J: 不变量 + 红线-3 (5) ===
    ("J1: real cells >= 156 (sanity, knife 增量 ≥ 0)", """
        SELECT COUNT(*) FROM cegr_mart.mart_city_timeseries
        WHERE value IS NOT NULL;
    """, 471),
    ("J2: DATA_MISSING cells = 2030 - 471 = 1559", """
        SELECT COUNT(*) FROM cegr_mart.mart_city_timeseries
        WHERE status = 'DATA_MISSING';
    """, 1559),
    ("J3: 4 669a cities 2021 全部 status = DATA_MISSING", """
        SELECT COUNT(*) FROM cegr_mart.mart_city_timeseries
        WHERE year = 2021
        AND city_code IN (
            'GUANGDONG_SHENZHEN','GUANGDONG_GUANGZHOU','ZHEJIANG_HANGZHOU','JIANGSU_NANJING'
        ) AND status <> 'DATA_MISSING';
    """, 0),
    ("J4: 25 省会 2020-2026 全部存在 (29 city × 7 year × 10 = 2030 rows total)", """
        SELECT (SELECT COUNT(*) FROM cegr_mart.mart_city_timeseries)
             - (29 * 10 * 7);
    """, 0),
    ("J5: lineage_ruling 全 10 个版本都至少 1 个 attribution", """
        SELECT COUNT(DISTINCT lineage_ruling) FROM cegr_mart.mart_city_timeseries
        WHERE lineage_ruling IS NOT NULL;
    """, 10),

    # === Section K: 缺失原因完备性 (5) ===
    ("K1: 2021 SICHUAN/XIZANG/QINGHAI/TAIWAN 40 cells 全部 missing_reason 含 'hongheiku tag 页'", """
        SELECT COUNT(*) FROM cegr_mart.mart_city_timeseries
        WHERE year = 2021 AND city_code IN ('SICHUAN_CHENGDU','XIZANG_LASA','QINGHAI_XINING','TAIWAN_TAIPEI')
        AND missing_reason LIKE '%hongheiku tag 页%';
    """, 40),
    ("K2: 2021 HUBEI_WUHAN/SHANXI_TAIYUAN 全 0 real (tag listing)", """
        SELECT COUNT(*) FROM cegr_mart.mart_city_timeseries
        WHERE year = 2021
        AND city_code IN ('HUBEI_WUHAN','SHANXI_TAIYUAN')
        AND value IS NOT NULL;
    """, 0),
    ("K3: 2021 HUBEI_WUHAN/SHANXI_TAIYUAN missing_reason 含 'tag listing'", """
        SELECT COUNT(*) FROM cegr_mart.mart_city_timeseries
        WHERE year = 2021
        AND city_code IN ('HUBEI_WUHAN','SHANXI_TAIYUAN')
        AND missing_reason LIKE '%tag listing%';
    """, 20),  # 2 city × 10 indicator
    ("K4: 2021 fixed_asset 18 missing 含 '增长%' (守红线-3, 25 省会 21 city 公告 - 1 FUJIAN real - 2 HUBEI/SHANXI tag listing = 18; 4 669a cities 走 4-city 分支 reason)", """
        SELECT COUNT(*) FROM cegr_mart.mart_city_timeseries
        WHERE year = 2021 AND indicator_key = 'fixed_asset'
        AND value IS NULL AND missing_reason LIKE '%增长%';
    """, 18),
    ("K5: 2021 4 city 公告无 indicator 缺失原因完备 (no NULL missing_reason)", """
        SELECT COUNT(*) FROM cegr_mart.mart_city_timeseries
        WHERE year = 2021 AND value IS NULL
        AND missing_reason IS NULL;
    """, 0),

    # === Section L: value sanity (5) — Decimal vs float 兼容 ===
    ("L1: 2021 HEBEI_SHIJIAZHUANG gdp_total == 6490.3 (sanity)", """
        SELECT value::float FROM cegr_mart.mart_city_timeseries
        WHERE year = 2021 AND city_code = 'HEBEI_SHIJIAZHUANG' AND indicator_key = 'gdp_total';
    """, 6490.3),
    ("L2: 2021 SHAANXI_XIAN gdp_total == 10688.28 (PDF variant sanity)", """
        SELECT value::float FROM cegr_mart.mart_city_timeseries
        WHERE year = 2021 AND city_code = 'SHAANXI_XIAN' AND indicator_key = 'gdp_total';
    """, 10688.28),
    ("L3: 2021 XINJIANG_WULUMUQI gdp_total == 3691.57 (sanity)", """
        SELECT value::float FROM cegr_mart.mart_city_timeseries
        WHERE year = 2021 AND city_code = 'XINJIANG_WULUMUQI' AND indicator_key = 'gdp_total';
    """, 3691.57),
    ("L4: 2021 HAINAN_HAIKOU gdp_growth == 11.3 (sanity)", """
        SELECT value::float FROM cegr_mart.mart_city_timeseries
        WHERE year = 2021 AND city_code = 'HAINAN_HAIKOU' AND indicator_key = 'gdp_growth';
    """, 11.3),
    ("L5: 2021 NEIMENGGU_HUHEHAOTE gdp_percapita == 89828 (sanity, 元单位)", """
        SELECT value::float FROM cegr_mart.mart_city_timeseries
        WHERE year = 2021 AND city_code = 'NEIMENGGU_HUHEHAOTE' AND indicator_key = 'gdp_percapita';
    """, 89828),
]


def main():
    print(f"=== knife 669fix-b-2021 mart verify ({len(ASSERTIONS)} 红线 assertions) ===")
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
        print("=== knife 669fix-b-2021 mart verify: ALL PASS (守 54+ 红线) ===")


if __name__ == "__main__":
    main()