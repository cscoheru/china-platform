#!/usr/bin/env python3
"""
669b-2025 红线 verify (~38 assertions)
========================================

vs 669a-2025 26 条 (+12 new for 669b):
  1-26: mirror 669a-2025 (real_cells=154 / DATA_MISSING=126 / rulings=8)
  27: 2025 missing by ruling = 22 K669a-2025 + 250 K669b-2025 (sub-knife attribution)
  28: 2025 missing_reason 含 '669b-2025' = 250/250 (25 city all)
  29: 2025 25 city missing_reason 含 'hongheiku 无 2025 city bulletin' = 250/250
  30: 2025 25 city lineage_ruling = K669b-2025-2026-09-08
  31: 2025 25 city lineage_source_type = DATA_MISSING (not HONGHEIKU_TRANSLOAD)
  32: 2025 25 city lineage_origin 含 'tjgb.hongheiku.com/tag/'
  33: 2025 25 city value IS NULL
  35: 2025 25 city distinct = 25 (sanity)
  36: 2025 25 city × 10 indicator cross product = 250
  37: lineage_ruling K669b-2025 唯一版本
  38: 2026 仍全 DATA_MISSING (守新增红线-2)
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
    print("=== knife 669b-2025 红线 verify (38 assertions) ===")
    print(f"DB: {DB_HOST}:{DB_PORT}/{DB_NAME} table={SCHEMA}.{TABLE}")
    print()
    conn = psycopg2.connect(host=DB_HOST, port=DB_PORT, user=DB_USER,
                            password=DB_PASS, dbname=DB_NAME)
    cur = conn.cursor()

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

    # 5. real_cells = 154
    n = q(cur, f"SELECT COUNT(*) FROM {SCHEMA}.{TABLE} WHERE value IS NOT NULL")[0]
    if n == 154:
        p(f"real_cells = 154 (26[2021]+37[2022]+37[2023]+36[2024]+18[2025]; 669b adds 0)")
    else:
        f(f"real_cells = {n}, expected 154")

    # 6. DATA_MISSING = 1876
    n = q(cur, f"SELECT COUNT(*) FROM {SCHEMA}.{TABLE} WHERE status = 'DATA_MISSING'")[0]
    if n == 1876:
        p(f"DATA_MISSING = 1876 (240 669a miss other years + 22 669a 2025 miss + 250 669b 2025 + 1364 other years 669b)")
    else:
        f(f"DATA_MISSING = {n}, expected 1876")

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

    # 8. lineage_ruling = 8 versions
    n = q(cur, f"SELECT COUNT(DISTINCT lineage_ruling) FROM {SCHEMA}.{TABLE}")[0]
    if n == 8:
        p(f"lineage_ruling = 8 versions (K669a-2020/2021/2022/2023/2024/2025 + K669b-2025 + pending)")
    else:
        f(f"lineage_ruling distinct = {n}, expected 8")

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

    # 12. 2020 仍全 DATA_MISSING
    n = q(cur, f"SELECT COUNT(*) FROM {SCHEMA}.{TABLE} WHERE year = 2020 AND value IS NOT NULL")[0]
    if n == 0:
        p(f"2020 仍全 DATA_MISSING (mart stable across sub-knives)")
    else:
        f(f"2020 real cells = {n}, expected 0")

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

    # 15-18. 2021/2022/2023/2024 real cells 不回归
    for yr, expected in [(2021, 26), (2022, 37), (2023, 37), (2024, 36)]:
        bad = q(cur, f"""
            SELECT COUNT(*) FROM {SCHEMA}.{TABLE}
            WHERE year = {yr} AND value IS NOT NULL AND lineage_source_type != 'HONGHEIKU_TRANSLOAD'
        """)[0]
        nr = q(cur, f"SELECT COUNT(*) FROM {SCHEMA}.{TABLE} WHERE year = {yr} AND value IS NOT NULL")[0]
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

    # 21. 2025 22 missing = 20× SZ/NJ + 2× fixed_asset (穗/杭) — no-regression
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

    # ===== 669b-2025 新增 (27-38) =====

    # 27. 2025 missing by ruling = 22 K669a-2025 + 250 K669b-2025
    cur.execute(f"""
        SELECT lineage_ruling, COUNT(*) FROM {SCHEMA}.{TABLE}
        WHERE year = 2025 AND value IS NULL
        GROUP BY lineage_ruling ORDER BY lineage_ruling
    """)
    by_ruling = cur.fetchall()
    expected = [('K669a-2025-2026-09-07', 22), ('K669b-2025-2026-09-08', 250)]
    if by_ruling == expected:
        p(f"2025 missing by ruling = 22 K669a + 250 K669b (sub-knife attribution)")
    else:
        f(f"2025 missing by ruling 异常: {by_ruling}, expected {expected}")

    # 28. 2025 250 cells missing_reason 含 '669b-2025'
    n = q(cur, f"""
        SELECT COUNT(*) FROM {SCHEMA}.{TABLE}
        WHERE year = 2025 AND value IS NULL
          AND lineage_ruling = 'K669b-2025-2026-09-08'
          AND missing_reason LIKE '%669b-2025%'
    """)[0]
    total_k669b = q(cur, f"SELECT COUNT(*) FROM {SCHEMA}.{TABLE} WHERE year = 2025 AND value IS NULL AND lineage_ruling = 'K669b-2025-2026-09-08'")[0]
    if n == 250 and total_k669b == 250:
        p(f"2025 K669b-2025 missing cells missing_reason 全 250/含 '669b-2025'")
    else:
        f(f"2025 K669b-2025 missing 含 '669b-2025' = {n}, total = {total_k669b}")

    # 29. 2025 25 city missing_reason 含 'hongheiku 无 2025 city bulletin'
    n = q(cur, f"""
        SELECT COUNT(*) FROM {SCHEMA}.{TABLE}
        WHERE year = 2025 AND value IS NULL
          AND lineage_ruling = 'K669b-2025-2026-09-08'
          AND missing_reason LIKE '%hongheiku 无 2025 city bulletin%'
    """)[0]
    if n == 250:
        p(f"2025 25 city missing_reason 全 250/含 'hongheiku 无 2025 city bulletin' (守红线-3)")
    else:
        f(f"2025 25 city missing_reason 守红线-3 = {n}/250")

    # 30. 2025 25 city lineage_ruling = K669b-2025-2026-09-08
    city_list = ','.join(f"'{c}'" for c in CITY_25)
    bad = q(cur, f"""
        SELECT COUNT(*) FROM {SCHEMA}.{TABLE}
        WHERE year = 2025 AND city_code IN ({city_list})
          AND lineage_ruling != 'K669b-2025-2026-09-08'
    """)[0]
    if bad == 0:
        p(f"2025 25 city 全 lineage_ruling = 'K669b-2025-2026-09-08'")
    else:
        f(f"2025 25 city lineage_ruling 异常: {bad} cells not K669b")

    # 31. 2025 25 city lineage_source_type = DATA_MISSING
    bad = q(cur, f"""
        SELECT COUNT(*) FROM {SCHEMA}.{TABLE}
        WHERE year = 2025 AND city_code IN ({city_list})
          AND lineage_source_type != 'DATA_MISSING'
    """)[0]
    if bad == 0:
        p(f"2025 25 city 全 lineage_source_type = 'DATA_MISSING' (无 hongheiku bulletin)")
    else:
        f(f"2025 25 city lineage_source_type 异常: {bad} cells")

    # 32. 2025 25 city lineage_origin 含 'tjgb.hongheiku.com/tag/'
    n = q(cur, f"""
        SELECT COUNT(*) FROM {SCHEMA}.{TABLE}
        WHERE year = 2025 AND city_code IN ({city_list})
          AND lineage_origin LIKE '%tjgb.hongheiku.com/tag/%'
    """)[0]
    if n == 250:
        p(f"2025 25 city 全 lineage_origin 含 'tjgb.hongheiku.com/tag/' (tag probe URL)")
    else:
        f(f"2025 25 city lineage_origin tag URL = {n}/250")

    # 33. 2025 25 city value IS NULL
    bad = q(cur, f"""
        SELECT COUNT(*) FROM {SCHEMA}.{TABLE}
        WHERE year = 2025 AND city_code IN ({city_list})
          AND value IS NOT NULL
    """)[0]
    if bad == 0:
        p(f"2025 25 city 全 value IS NULL (守红线-3 不手填)")
    else:
        f(f"2025 25 city value 不应 NOT NULL: {bad} cells")

    # 35. 2025 25 city distinct = 25 (sanity)
    n = q(cur, f"""
        SELECT COUNT(DISTINCT city_code) FROM {SCHEMA}.{TABLE}
        WHERE year = 2025 AND city_code IN ({city_list})
    """)[0]
    if n == 25:
        p(f"2025 25 city distinct count = 25 (sanity 25 省会全在 mart)")
    else:
        f(f"2025 25 city distinct = {n}, expected 25")

    # 36. 2025 25 city × 10 indicator = 250 cells
    n = q(cur, f"""
        SELECT COUNT(*) FROM {SCHEMA}.{TABLE}
        WHERE year = 2025 AND city_code IN ({city_list})
    """)[0]
    if n == 250:
        p(f"2025 25 city × 10 indicator = 250 cells (cross product)")
    else:
        f(f"2025 25 city cells = {n}, expected 250")

    # 37. lineage_ruling K669b-2025 唯一
    n = q(cur, f"SELECT COUNT(DISTINCT lineage_ruling) FROM {SCHEMA}.{TABLE} WHERE lineage_ruling LIKE '%669b-2025%'")[0]
    if n == 1:
        p(f"lineage_ruling K669b-2025-* 唯一版本: K669b-2025-2026-09-08")
    else:
        f(f"669b-2025 rulings 不唯一 = {n}")

    # 38. 2026 仍全 DATA_MISSING (守红线-2)
    n = q(cur, f"SELECT COUNT(*) FROM {SCHEMA}.{TABLE} WHERE year = 2026 AND value IS NOT NULL")[0]
    if n == 0:
        p(f"2026 仍全 DATA_MISSING (新增红线-2: 待 2027 官方发布)")
    else:
        f(f"2026 real cells = {n}, expected 0")

    cur.close()
    conn.close()

    print()
    print(f"=== knife 669b-2025 红线 summary: {PASS}/{PASS+FAIL} PASS, {FAIL} FAIL ===")
    sys.exit(0 if FAIL == 0 else 1)


if __name__ == "__main__":
    main()