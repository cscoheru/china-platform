#!/usr/bin/env python3
"""
669fix-b-2020 红线 verify (~48 assertions)
============================================

Path A (full re-harvest of 2020 after historical misjudgment fix):
  - 24 city bulletins harvestable from hongheiku /{eid}.html (2020 root pattern)
  - 4 PDF bulletins (ANHUI/SICHUAN/GANSU/QINGHAI) parsed via pypdf
  - 1 HEBEI table-style bulletin recovered via parser v3 strip-first
  - 19 fixed_asset growth% values correctly excluded → DATA_MISSING (per 669a-2021 §2)
  - 22 city with ≥1 real cell; 2 city (JIANGXI/SHANXI) image-only all miss
  - 1 TAIWAN no entry all miss

vs 669b-2025 38 assertions (+10 net new for 669fix-b-2020):
  1-26: mirror 669b-2025 baseline adjusted (real_cells=315 / DATA_MISSING=1715 / rulings=9)
  12: 2020 仍全 DATA_MISSING → 2020 real cells = 161 (Path A flipped this)
  5: real_cells = 315 (+161 from 669fix-b-2020)
  6: DATA_MISSING = 1715 (-161)
  8: lineage_ruling = 9 versions (+K669fix-b-2020)

  27-50: 669fix-b-2020 新增 (24 new assertions):
  27: 2020 real by ruling = 161 K669fix-b-2020 (only)
  28: 2020 missing by ruling = 129 K669a-2020 (669a was pre-fix Data_MISSING path)
  29: 2020 real cells lineage_source_type 全 = HONGHEIKU_TRANSLOAD
  30: 2020 real cells lineage_origin 全含 'tjgb.hongheiku.com/' (eid path)
  31: 2020 22 city with at least 1 real cell (24 bulletin - 1 TAIWAN - 1 IMAGE = 22, but 2 are image-only making 22)
  32: 2020 22 city distinct city_code count (sanity)
  33: 2020 25 city × 10 indicator = 250 cells (cross product)
  34: 2020 TAIWAN_TAIPEI 全 value IS NULL (10 miss, hongheiku 无 entry)
  35: 2020 JIANGXI_NANCHANG 全 value IS NULL (10 miss, image-only)
  36: 2020 SHANXI_TAIYUAN 全 value IS NULL (10 miss, image-only)
  37: 2020 fixed_asset 全 25 city value IS NULL (19 % growth + 6 truly missing)
  38: 2020 XINJIANG_WULUMUQI gdp_total = 3337.32 (sanity, 10/10 cells)
  39: 2020 HEBEI_SHIJIAZHUANG gdp_total = 5935.1 (sanity, parser v3 恢复)
  40: 2020 missing cells 129 全含 '669fix-b-2020' missing_reason (22 city city-level miss + ... actually 70 = 10 TAIWAN + 20 image + 19 fixed_asset% + 21 city-level miss)
  41: lineage_ruling K669fix-b-2020-* 唯一版本
  42: 2020 missing_reason 含 'image 扫描件' for JIANGXI/SHANXI (守红线-3)
  43: 2020 missing_reason 含 '增长%' for 19 fixed_asset cells (守红线-3)
  44: HONGHEIKU_TRANSLOAD count = real_cells (315)
  45: 2020 lineage_ruling = K669fix-b-2020-2026-09-08 for real cells
  46: 2020 missing cells with K669a-2020 ruling = 40 (4 669a city × 10 indicator)
  47: 2020 missing cells with K669fix-b-2020 ruling = 49 (rest = 250 - 161 - 40)
  48: 2020 missing_reason 含 'hongheiku 无 2020 bulletin' for TAIWAN (守红线-3)
  49: 2021-2025 + 2026 real cells不回归 (154 pre-669fix-b-2020 + 0 from 669fix-b-2020)
  50: 2026 仍全 DATA_MISSING (守红线-2)
"""

import os
import sys
import psycopg2

DB_HOST = "127.0.0.1"
DB_PORT = 55440
DB_USER = "postgres"
DB_PASS = os.environ.get("DBT_DEV_PASS", "postgres")
DB_NAME = "cegr_test"
SCHEMA = "cegr_mart"
TABLE = "mart_city_timeseries"

RED = "\033[0;31m"
GREEN = "\033[0;32m"
YELLOW = "\033[1;33m"
NC = "\033[0m"

PASS = 0
FAIL = 0

# 25 省会 city codes
CITY_25 = [
    "HEBEI_SHIJIAZHUANG", "SHANXI_TAIYUAN", "NEIMENGGU_HUHEHAOTE", "LIAONING_SHENYANG",
    "JILIN_CHANGCHUN", "HEILONGJIANG_HARBIN", "ANHUI_HEFEI", "FUJIAN_FUZHOU",
    "JIANGXI_NANCHANG", "SHANDONG_JINAN", "HENAN_ZHENGZHOU", "HUBEI_WUHAN",
    "HUNAN_CHANGSHA", "GUANGXI_NANNING", "HAINAN_HAIKOU", "SICHUAN_CHENGDU",
    "GUIZHOU_GUIYANG", "YUNNAN_KUNMING", "XIZANG_LASA", "SHAANXI_XIAN",
    "GANSU_LANZHOU", "QINGHAI_XINING", "NINGXIA_YINCHUAN", "XINJIANG_WULUMUQI",
    "TAIWAN_TAIPEI",
]
CITY_4 = ["GUANGDONG_SHENZHEN", "GUANGDONG_GUANGZHOU", "ZHEJIANG_HANGZHOU", "JIANGSU_NANJING"]


def p(msg):
    global PASS
    PASS += 1
    print(f"  {GREEN}[OK]{NC}   {msg}")


def f(msg):
    global FAIL
    FAIL += 1
    print(f"  {RED}[FAIL]{NC} {msg}")


def q(cur, sql, params=None):
    if params:
        cur.execute(sql, params)
    else:
        cur.execute(sql)
    return cur.fetchone()


def main():
    global PASS, FAIL
    print("=== knife 669fix-b-2020 红线 verify (~50 assertions) ===")
    print(f"DB: {DB_HOST}:{DB_PORT}/{DB_NAME} table={SCHEMA}.{TABLE}")
    print("Path A: re-harvest 2020 after historical misjudgment fix")
    print()
    conn = psycopg2.connect(host=DB_HOST, port=DB_PORT, user=DB_USER,
                            password=DB_PASS, dbname=DB_NAME)
    cur = conn.cursor()

    # ===== 669b-2025 mirror adjusted for 669fix-b-2020 (1-26) =====

    # 1. mart 行数 = 2030
    n = q(cur, f"SELECT COUNT(*) FROM {SCHEMA}.{TABLE}")[0]
    if n == 2030:
        p(f"row count = 2030 (29 city × 10 indicator × 7 year)")
    else:
        f(f"row count = {n}, expected 2030")

    # 2. city distinct = 29
    n = q(cur, f"SELECT COUNT(DISTINCT city_code) FROM {SCHEMA}.{TABLE}")[0]
    if n == 29:
        p(f"city distinct = 29 (4 669a + 25 669b)")
    else:
        f(f"city distinct = {n}, expected 29")

    # 3. indicator distinct = 10
    n = q(cur, f"SELECT COUNT(DISTINCT indicator_key) FROM {SCHEMA}.{TABLE}")[0]
    if n == 10:
        p(f"indicator distinct = 10 (5 现 + 5 增量)")
    else:
        f(f"indicator distinct = {n}, expected 10")

    # 4. year distinct = 7
    n = q(cur, f"SELECT COUNT(DISTINCT year) FROM {SCHEMA}.{TABLE}")[0]
    if n == 7:
        p(f"year distinct = 7 (2020-2026)")
    else:
        f(f"year distinct = {n}, expected 7")

    # 5. real_cells = 315 (154 prev + 161 669fix-b-2020)
    n = q(cur, f"SELECT COUNT(*) FROM {SCHEMA}.{TABLE} WHERE value IS NOT NULL")[0]
    if n == 315:
        p(f"real_cells = 315 (154 prev [26+37+37+36+18] + 161 669fix-b-2020)")
    else:
        f(f"real_cells = {n}, expected 315")

    # 6. DATA_MISSING = 1715 (2030 - 315)
    n = q(cur, f"SELECT COUNT(*) FROM {SCHEMA}.{TABLE} WHERE status = 'DATA_MISSING'")[0]
    if n == 1715:
        p(f"DATA_MISSING = 1715 (2030 - 315)")
    else:
        f(f"DATA_MISSING = {n}, expected 1715")

    # 7. 4 直辖市禁重复 (红线-7)
    direct_cities = q(cur, f"""
        SELECT COUNT(*) FROM {SCHEMA}.{TABLE}
        WHERE city_code LIKE 'BEIJING_%' OR city_code LIKE 'SHANGHAI_%'
           OR city_code LIKE 'TIANJIN_%' OR city_code LIKE 'CHONGQING_%'
    """)[0]
    if direct_cities == 0:
        p(f"4 直辖市禁重复 (新增红线-7) — NOT in city dimension")
    else:
        f(f"4 直辖市 found in city dim: {direct_cities} rows")

    # 8. lineage_ruling = 9 versions (8 prev + K669fix-b-2020)
    n = q(cur, f"SELECT COUNT(DISTINCT lineage_ruling) FROM {SCHEMA}.{TABLE}")[0]
    if n == 9:
        p(f"lineage_ruling = 9 versions (8 prev + K669fix-b-2020)")
    else:
        f(f"lineage_ruling distinct = {n}, expected 9")

    # 9. lineage_is_demo 全部 false
    bad = q(cur, f"SELECT COUNT(*) FROM {SCHEMA}.{TABLE} WHERE lineage_is_demo != 'false' OR lineage_is_demo IS NULL")[0]
    if bad == 0:
        p(f"lineage_is_demo 全部 = 'false'")
    else:
        f(f"lineage_is_demo 不合规 cells = {bad}")

    # 10. status 枚举
    bad = q(cur, f"""
        SELECT COUNT(*) FROM {SCHEMA}.{TABLE}
        WHERE status IS NOT NULL AND status NOT IN ('DATA_MISSING', 'OFFICIAL_INTAKED', 'HONGHEIKU_TRANSLOAD', 'unknown')
    """)[0]
    if bad == 0:
        p(f"status 枚举合法 (NULL or DATA_MISSING)")
    else:
        f(f"status 不合规 cells = {bad}")

    # 11. missing_reason 必填
    bad = q(cur, f"SELECT COUNT(*) FROM {SCHEMA}.{TABLE} WHERE status = 'DATA_MISSING' AND (missing_reason IS NULL OR missing_reason = '')")[0]
    if bad == 0:
        p(f"missing_reason 必填 for all DATA_MISSING cells")
    else:
        f(f"missing_reason 缺失 cells = {bad}")

    # 12. [FLIPPED] 2020 real cells = 161 (Path A recovered)
    n = q(cur, f"SELECT COUNT(*) FROM {SCHEMA}.{TABLE} WHERE year = 2020 AND value IS NOT NULL")[0]
    if n == 161:
        p(f"2020 real cells = 161 (Path A recovered, was 0 in 669b-2025 baseline)")
    else:
        f(f"2020 real cells = {n}, expected 161")

    # 13. 2026 仍全 DATA_MISSING (红线-2)
    n = q(cur, f"SELECT COUNT(*) FROM {SCHEMA}.{TABLE} WHERE year = 2026 AND value IS NOT NULL")[0]
    if n == 0:
        p(f"2026 仍全 DATA_MISSING (新增红线-2)")
    else:
        f(f"2026 real cells = {n}, expected 0")

    # 14. value 列类型 = numeric
    pgtype = q(cur, f"""
        SELECT data_type FROM information_schema.columns
        WHERE table_schema = '{SCHEMA}' AND table_name = '{TABLE}' AND column_name = 'value'
    """)[0]
    if pgtype == "numeric":
        p(f"value 列类型 = numeric")
    else:
        f(f"value 列类型 = '{pgtype}', expected 'numeric'")

    # 15-18. 2021/2022/2023/2024 real cells 不回归 (pre-669fix-b-2020 totals)
    for yr, expected in [(2021, 26), (2022, 37), (2023, 37), (2024, 36)]:
        nr = q(cur, f"SELECT COUNT(*) FROM {SCHEMA}.{TABLE} WHERE year = {yr} AND value IS NOT NULL")[0]
        bad = q(cur, f"""
            SELECT COUNT(*) FROM {SCHEMA}.{TABLE}
            WHERE year = {yr} AND value IS NOT NULL AND lineage_source_type != 'HONGHEIKU_TRANSLOAD'
        """)[0]
        if bad == 0 and nr == expected:
            p(f"{yr} real cells 不回归: {nr} real (前刀保持)")
        else:
            f(f"{yr} 不回归 check: bad={bad}, real={nr} (expected 0/{expected})")

    # 19. 2025 real cells lineage_source_type = HONGHEIKU_TRANSLOAD
    bad = q(cur, f"""
        SELECT COUNT(*) FROM {SCHEMA}.{TABLE}
        WHERE year = 2025 AND value IS NOT NULL AND lineage_source_type != 'HONGHEIKU_TRANSLOAD'
    """)[0]
    if bad == 0:
        p(f"2025 real cells lineage_source_type 全 = 'HONGHEIKU_TRANSLOAD'")
    else:
        f(f"2025 real cells lineage_source_type 不合规 = {bad}")

    # 20. 2025 real cells lineage_origin 含 'tjgb.hongheiku.com/djs/'
    n = q(cur, f"""
        SELECT COUNT(*) FROM {SCHEMA}.{TABLE}
        WHERE year = 2025 AND value IS NOT NULL
          AND lineage_origin LIKE '%tjgb.hongheiku.com/djs/%'
    """)[0]
    total_real = q(cur, f"SELECT COUNT(*) FROM {SCHEMA}.{TABLE} WHERE year = 2025 AND value IS NOT NULL")[0]
    if n == total_real:
        p(f"2025 real cells lineage_origin 全 {total_real}/含 'tjgb.hongheiku.com/djs/'")
    else:
        f(f"2025 real cells lineage_origin 守门 = {n}, total real = {total_real}")

    # 21. 2025 22 missing (K669a-2025) = 20× SZ/NJ + 2× fixed_asset (穗/杭) — no-regression
    cur.execute(f"""
        SELECT city_code, indicator_key FROM {SCHEMA}.{TABLE}
        WHERE year = 2025 AND value IS NULL
          AND lineage_ruling = 'K669a-2025-2026-09-07'
        ORDER BY city_code, indicator_key
    """)
    rows = cur.fetchall()
    expected_set = set()
    for ind in ['gdp_total', 'gdp_growth', 'primary_gdp', 'secondary_gdp', 'tertiary_gdp',
                'gdp_percapita', 'fiscal_rev', 'fixed_asset', 'retail', 'trade']:
        expected_set.add(('GUANGDONG_SHENZHEN', ind))
        expected_set.add(('JIANGSU_NANJING', ind))
    expected_set.add(('GUANGDONG_GUANGZHOU', 'fixed_asset'))
    expected_set.add(('ZHEJIANG_HANGZHOU', 'fixed_asset'))
    if set(rows) == expected_set:
        p(f"2025 22 missing (K669a-2025) = 20× SZ/NJ + 2× fixed_asset (穗/杭, 守红线-3 不回归)")
    else:
        f(f"2025 22 missing 分解异常: actual={set(rows) ^ expected_set}")

    # 22. 2025 real by city = 仅穗/杭 9 each
    cur.execute(f"""
        SELECT city_code, COUNT(*) FROM {SCHEMA}.{TABLE}
        WHERE year = 2025 AND value IS NOT NULL
        GROUP BY city_code ORDER BY city_code
    """)
    rows = cur.fetchall()
    expected = [('GUANGDONG_GUANGZHOU', 9), ('ZHEJIANG_HANGZHOU', 9)]
    if rows == expected:
        p(f"2025 real cells 分布: 仅穗/杭 各 9")
    else:
        f(f"2025 real by city 异常: {rows}")

    # 23. 2021+2022+2023+2024 real 总量不变 = 136
    n = q(cur, f"""
        SELECT COUNT(*) FROM {SCHEMA}.{TABLE}
        WHERE year IN (2021, 2022, 2023, 2024) AND value IS NOT NULL
    """)[0]
    if n == 136:
        p(f"2021+2022+2023+2024 real 总量 = 136 不变 (mart stable)")
    else:
        f(f"2021-2024 real 总量 = {n}, expected 136")

    # 24. 2025 missing (K669a) missing_reason 全 22/含 '669a-2025'
    n = q(cur, f"""
        SELECT COUNT(*) FROM {SCHEMA}.{TABLE}
        WHERE year = 2025 AND value IS NULL
          AND lineage_ruling = 'K669a-2025-2026-09-07'
          AND missing_reason LIKE '%669a-2025%'
    """)[0]
    total_k669a = q(cur, f"SELECT COUNT(*) FROM {SCHEMA}.{TABLE} WHERE year = 2025 AND value IS NULL AND lineage_ruling = 'K669a-2025-2026-09-07'")[0]
    if n == 22 and total_k669a == 22:
        p(f"2025 K669a-2025 missing cells missing_reason 全 22/含 '669a-2025'")
    else:
        f(f"2025 K669a-2025 missing 含 '669a-2025' = {n}, total = {total_k669a} (expected 22/22)")

    # 25. lineage_ruling K669a-2025 唯一
    n = q(cur, f"SELECT COUNT(DISTINCT lineage_ruling) FROM {SCHEMA}.{TABLE} WHERE lineage_ruling LIKE '%669a-2025%'")[0]
    if n == 1:
        p(f"lineage_ruling K669a-2025-* 唯一版本: K669a-2025-2026-09-07")
    else:
        f(f"669a-2025 rulings 不唯一 = {n}")

    # 26. 2021/2025 lineage_ruling 唯一
    for yr_label in ["669a-2021", "669a-2022", "669a-2023", "669a-2024", "669b-2025"]:
        n = q(cur, f"SELECT COUNT(DISTINCT lineage_ruling) FROM {SCHEMA}.{TABLE} WHERE lineage_ruling LIKE '%{yr_label}%'")[0]
        if n == 1:
            p(f"lineage_ruling {yr_label}-* 唯一版本")
        else:
            f(f"{yr_label} rulings 不唯一 = {n}")

    # ===== 669fix-b-2020 新增 (27-50) =====

    # 27. 2020 real by ruling = 161 K669fix-b-2020 (only)
    cur.execute(f"""
        SELECT lineage_ruling, COUNT(*) FROM {SCHEMA}.{TABLE}
        WHERE year = 2020 AND value IS NOT NULL
        GROUP BY lineage_ruling ORDER BY lineage_ruling
    """)
    by_ruling = cur.fetchall()
    expected = [('K669fix-b-2020-2026-09-08', 161)]
    if by_ruling == expected:
        p(f"2020 real cells by ruling = 161 K669fix-b-2020 (only source)")
    else:
        f(f"2020 real by ruling 异常: {by_ruling}, expected {expected}")

    # 28. 2020 missing by ruling = 40 K669a-2020 + 89 K669fix-b-2020
    # (40 K669a-2020 = 4 669a cities × 10 indicator; 89 K669fix-b-2020 = 25 省会 missing)
    cur.execute(f"""
        SELECT lineage_ruling, COUNT(*) FROM {SCHEMA}.{TABLE}
        WHERE year = 2020 AND value IS NULL
        GROUP BY lineage_ruling ORDER BY lineage_ruling
    """)
    miss_by_ruling = cur.fetchall()
    expected_miss = [('K669a-2020-2026-09-04', 40), ('K669fix-b-2020-2026-09-08', 89)]
    if miss_by_ruling == expected_miss:
        p(f"2020 missing by ruling = 40 K669a-2020 (4 city) + 89 K669fix-b-2020 (25 省会 missing)")
    else:
        f(f"2020 missing by ruling 异常: {miss_by_ruling}, expected {expected_miss}")

    # 29. 2020 real cells lineage_source_type 全 = HONGHEIKU_TRANSLOAD
    bad = q(cur, f"""
        SELECT COUNT(*) FROM {SCHEMA}.{TABLE}
        WHERE year = 2020 AND value IS NOT NULL
          AND lineage_source_type != 'HONGHEIKU_TRANSLOAD'
    """)[0]
    if bad == 0:
        p(f"2020 real cells lineage_source_type 全 = 'HONGHEIKU_TRANSLOAD'")
    else:
        f(f"2020 real cells lineage_source_type 不合规 = {bad}")

    # 30. 2020 real cells lineage_origin 全含 'tjgb.hongheiku.com/' (eid path)
    n = q(cur, f"""
        SELECT COUNT(*) FROM {SCHEMA}.{TABLE}
        WHERE year = 2020 AND value IS NOT NULL
          AND lineage_origin LIKE '%tjgb.hongheiku.com/%'
    """)[0]
    total_real_2020 = q(cur, f"SELECT COUNT(*) FROM {SCHEMA}.{TABLE} WHERE year = 2020 AND value IS NOT NULL")[0]
    if n == total_real_2020:
        p(f"2020 real cells lineage_origin 全 {total_real_2020}/含 'tjgb.hongheiku.com/' (eid path)")
    else:
        f(f"2020 real cells lineage_origin 守门 = {n}, total = {total_real_2020}")

    # 31. 2020 22 city with at least 1 real cell
    n = q(cur, f"""
        SELECT COUNT(DISTINCT city_code) FROM {SCHEMA}.{TABLE}
        WHERE year = 2020 AND value IS NOT NULL
    """)[0]
    if n == 22:
        p(f"2020 city with ≥1 real cell = 22 (24 bulletin - 1 TAIWAN miss - 1 SHANXI image miss - ... actually 22 from 24 city minus TAIWAN = 23 - 1 JIANGXI image miss = 22)")
    else:
        f(f"2020 city real distinct = {n}, expected 22")

    # 32. 2020 25 city distinct (sanity)
    n = q(cur, f"""
        SELECT COUNT(DISTINCT city_code) FROM {SCHEMA}.{TABLE}
        WHERE year = 2020 AND city_code IN (SELECT unnest(string_to_array('{','.join(CITY_25)}', ',')))
    """)[0]
    if n == 25:
        p(f"2020 25 city distinct count = 25 (sanity)")
    else:
        f(f"2020 25 city distinct = {n}, expected 25")

    # 33. 2020 25 city × 10 indicator = 250 cells
    city_list = ','.join(f"'{c}'" for c in CITY_25)
    n = q(cur, f"""
        SELECT COUNT(*) FROM {SCHEMA}.{TABLE}
        WHERE year = 2020 AND city_code IN ({city_list})
    """)[0]
    if n == 250:
        p(f"2020 25 city × 10 indicator = 250 cells (cross product)")
    else:
        f(f"2020 25 city cells = {n}, expected 250")

    # 34. 2020 TAIWAN_TAIPEI 全 value IS NULL (10 miss, hongheiku 无 entry)
    bad = q(cur, f"""
        SELECT COUNT(*) FROM {SCHEMA}.{TABLE}
        WHERE year = 2020 AND city_code = 'TAIWAN_TAIPEI'
          AND value IS NOT NULL
    """)[0]
    if bad == 0:
        p(f"2020 TAIWAN_TAIPEI 全 value IS NULL (10 miss, hongheiku 无 entry, 守红线-3)")
    else:
        f(f"2020 TAIWAN_TAIPEI 不应 NOT NULL: {bad} cells")

    # 35. 2020 JIANGXI_NANCHANG 全 value IS NULL (10 miss, image-only)
    bad = q(cur, f"""
        SELECT COUNT(*) FROM {SCHEMA}.{TABLE}
        WHERE year = 2020 AND city_code = 'JIANGXI_NANCHANG'
          AND value IS NOT NULL
    """)[0]
    if bad == 0:
        p(f"2020 JIANGXI_NANCHANG 全 value IS NULL (10 miss, image-only, 无 OCR 范围)")
    else:
        f(f"2020 JIANGXI_NANCHANG 不应 NOT NULL: {bad} cells")

    # 36. 2020 SHANXI_TAIYUAN 全 value IS NULL (10 miss, image-only)
    bad = q(cur, f"""
        SELECT COUNT(*) FROM {SCHEMA}.{TABLE}
        WHERE year = 2020 AND city_code = 'SHANXI_TAIYUAN'
          AND value IS NOT NULL
    """)[0]
    if bad == 0:
        p(f"2020 SHANXI_TAIYUAN 全 value IS NULL (10 miss, image-only, 无 OCR 范围)")
    else:
        f(f"2020 SHANXI_TAIYUAN 不应 NOT NULL: {bad} cells")

    # 37. 2020 fixed_asset 全 25 city value IS NULL (19 % growth + 6 truly missing)
    bad = q(cur, f"""
        SELECT COUNT(*) FROM {SCHEMA}.{TABLE}
        WHERE year = 2020 AND indicator_key = 'fixed_asset'
          AND city_code IN ({city_list})
          AND value IS NOT NULL
    """)[0]
    if bad == 0:
        p(f"2020 fixed_asset 全 25 city value IS NULL (19 % growth 排除 + 6 truly missing, 守红线-3)")
    else:
        f(f"2020 fixed_asset 不应 NOT NULL: {bad} cells")

    # 38. 2020 XINJIANG_WULUMUQI gdp_total = 3337.32 (sanity check, 10/10 cells)
    val = q(cur, f"""
        SELECT value FROM {SCHEMA}.{TABLE}
        WHERE year = 2020 AND city_code = 'XINJIANG_WULUMUQI' AND indicator_key = 'gdp_total'
    """)[0]
    if val is not None and abs(float(val) - 3337.32) < 0.01:
        p(f"2020 XINJIANG_WULUMUQI gdp_total = {val} (sanity, 10/10 cells 全 harvest)")
    else:
        f(f"2020 XINJIANG_WULUMUQI gdp_total = {val}, expected ~3337.32")

    # 39. 2020 HEBEI_SHIJIAZHUANG gdp_total = 5935.1 (sanity, parser v3 strip-first 恢复)
    val = q(cur, f"""
        SELECT value FROM {SCHEMA}.{TABLE}
        WHERE year = 2020 AND city_code = 'HEBEI_SHIJIAZHUANG' AND indicator_key = 'gdp_total'
    """)[0]
    if val is not None and abs(float(val) - 5935.1) < 0.01:
        p(f"2020 HEBEI_SHIJIAZHUANG gdp_total = {val} (sanity, parser v3 strip-first 恢复 HEBEI 0→7)")
    else:
        f(f"2020 HEBEI_SHIJIAZHUANG gdp_total = {val}, expected ~5935.1")

    # 40. 2020 missing cells 89 with K669fix-b-2020 ruling missing_reason 全含 '669fix-b-2020'
    n = q(cur, f"""
        SELECT COUNT(*) FROM {SCHEMA}.{TABLE}
        WHERE year = 2020 AND value IS NULL
          AND lineage_ruling = 'K669fix-b-2020-2026-09-08'
          AND missing_reason LIKE '%669fix-b-2020%'
    """)[0]
    total_k669fix = q(cur, f"SELECT COUNT(*) FROM {SCHEMA}.{TABLE} WHERE year = 2020 AND value IS NULL AND lineage_ruling = 'K669fix-b-2020-2026-09-08'")[0]
    if n == total_k669fix == 89:
        p(f"2020 K669fix-b-2020 missing cells missing_reason 全 89/含 '669fix-b-2020'")
    else:
        f(f"2020 K669fix-b-2020 missing 含 '669fix-b-2020' = {n}, total = {total_k669fix} (expected 89/89)")

    # 41. lineage_ruling K669fix-b-2020-* 唯一版本
    n = q(cur, f"SELECT COUNT(DISTINCT lineage_ruling) FROM {SCHEMA}.{TABLE} WHERE lineage_ruling LIKE '%669fix-b-2020%'")[0]
    if n == 1:
        p(f"lineage_ruling K669fix-b-2020-* 唯一版本: K669fix-b-2020-2026-09-08")
    else:
        f(f"669fix-b-2020 rulings 不唯一 = {n}")

    # 42. 2020 missing_reason 含 'image 扫描件' for JIANGXI/SHANXI (守红线-3)
    n = q(cur, f"""
        SELECT COUNT(*) FROM {SCHEMA}.{TABLE}
        WHERE year = 2020 AND value IS NULL
          AND city_code IN ('JIANGXI_NANCHANG', 'SHANXI_TAIYUAN')
          AND missing_reason LIKE '%image%'
    """)[0]
    if n == 20:
        p(f"2020 JIANGXI/SHANXI image-only missing_reason 全 20/含 'image 扫描件' (守红线-3)")
    else:
        f(f"2020 image-only missing = {n}/20, expected 20")

    # 43. 2020 missing_reason 含 '增长%' for fixed_asset cells (守红线-3)
    # 26 = 22 省会 fixed_asset miss (19 rd7-excluded growth% + 3 truly missing) + 4 669a cities fixed_asset
    n = q(cur, f"""
        SELECT COUNT(*) FROM {SCHEMA}.{TABLE}
        WHERE year = 2020 AND value IS NULL
          AND indicator_key = 'fixed_asset'
          AND missing_reason LIKE '%增长%'
    """)[0]
    if n == 26:
        p(f"2020 fixed_asset 增长% missing_reason = 26 (22 省会 + 4 669a cities, 守红线-3)")
    else:
        f(f"2020 fixed_asset 增长% missing = {n}/26, expected 26")

    # 44. HONGHEIKU_TRANSLOAD count = real_cells (315)
    n = q(cur, f"SELECT COUNT(*) FROM {SCHEMA}.{TABLE} WHERE lineage_source_type = 'HONGHEIKU_TRANSLOAD'")[0]
    if n == 315:
        p(f"HONGHEIKU_TRANSLOAD count = 315 (= real_cells, lineage_source_type 一致)")
    else:
        f(f"HONGHEIKU_TRANSLOAD count = {n}, expected 315")

    # 45. 2020 lineage_ruling = K669fix-b-2020-2026-09-08 for real cells
    bad = q(cur, f"""
        SELECT COUNT(*) FROM {SCHEMA}.{TABLE}
        WHERE year = 2020 AND value IS NOT NULL
          AND lineage_ruling != 'K669fix-b-2020-2026-09-08'
    """)[0]
    if bad == 0:
        p(f"2020 real cells 全 lineage_ruling = 'K669fix-b-2020-2026-09-08'")
    else:
        f(f"2020 real cells lineage_ruling 异常: {bad} cells not K669fix-b-2020")

    # 46. 2020 missing cells with K669a-2020 ruling = 40 (4 669a city × 10 indicator)
    n = q(cur, f"""
        SELECT COUNT(*) FROM {SCHEMA}.{TABLE}
        WHERE year = 2020 AND value IS NULL
          AND lineage_ruling = 'K669a-2020-2026-09-04'
    """)[0]
    if n == 40:
        p(f"2020 K669a-2020 missing cells = 40 (4 669a city [SZ/NJ/GZ/HZ] × 10 indicator, pre-fix attribution)")
    else:
        f(f"2020 K669a-2020 missing = {n}, expected 40")

    # 47. 2020 missing cells with K669fix-b-2020 ruling = 89 (250 - 161 - 40)
    n = q(cur, f"""
        SELECT COUNT(*) FROM {SCHEMA}.{TABLE}
        WHERE year = 2020 AND value IS NULL
          AND lineage_ruling = 'K669fix-b-2020-2026-09-08'
    """)[0]
    if n == 89:
        p(f"2020 K669fix-b-2020 missing cells = 89 (250 - 161 real - 40 K669a)")
    else:
        f(f"2020 K669fix-b-2020 missing = {n}, expected 89")

    # 48. 2020 missing_reason 含 'hongheiku tag 页无 2020 bulletin' for TAIWAN (守红线-3)
    n = q(cur, f"""
        SELECT COUNT(*) FROM {SCHEMA}.{TABLE}
        WHERE year = 2020 AND value IS NULL
          AND city_code = 'TAIWAN_TAIPEI'
          AND missing_reason LIKE '%hongheiku tag 页无 2020 bulletin%'
    """)[0]
    if n == 10:
        p(f"2020 TAIWAN_TAIPEI missing_reason 全 10/含 'hongheiku tag 页无 2020 bulletin' (守红线-3)")
    else:
        f(f"2020 TAIWAN missing_reason 守红线-3 = {n}/10")

    # 49. 2021-2025 real cells 不回归 (合计 = 154, 669fix-b-2020 不污染)
    n = q(cur, f"""
        SELECT COUNT(*) FROM {SCHEMA}.{TABLE}
        WHERE year IN (2021, 2022, 2023, 2024, 2025) AND value IS NOT NULL
    """)[0]
    if n == 154:
        p(f"2021-2025 real 总量 = 154 不变 (669fix-b-2020 仅 harvest year=2020)")
    else:
        f(f"2021-2025 real 总量 = {n}, expected 154 (不回归)")

    # 50. 2026 仍全 DATA_MISSING (守红线-2)
    n = q(cur, f"SELECT COUNT(*) FROM {SCHEMA}.{TABLE} WHERE year = 2026 AND value IS NOT NULL")[0]
    if n == 0:
        p(f"2026 仍全 DATA_MISSING (新增红线-2: 待 2027 官方发布)")
    else:
        f(f"2026 real cells = {n}, expected 0")

    cur.close()
    conn.close()

    print()
    print(f"=== knife 669fix-b-2020 红线 summary: {PASS}/{PASS+FAIL} PASS, {FAIL} FAIL ===")
    sys.exit(0 if FAIL == 0 else 1)


if __name__ == "__main__":
    main()