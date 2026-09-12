#!/usr/bin/env python3
"""
669j-1 红线 verify (38 assertions)
==================================

knife 669j sub-knife 1/6 (2026-09-12, batch2): 5 粤卫星城 NO-OP
  GUANGDONG_ZHUHAI, GUANGDONG_ZHANJIANG, GUANGDONG_SHANTOU, GUANGDONG_JIANGMEN, GUANGDONG_ZHAOQING

baseline (pre-669j-1): 37 cities, 2590 rows, 1090 real, 1500 miss, 9 ruling_versions
post-669j-1 expectation:
  - cities 42 (37 + 5)
  - rows 2940 (42 × 10 × 7)
  - real_cells 1090 (NO-OP 不增)
  - DATA_MISSING 1850 (1500 + 350)
  - ruling_versions 10 (+ K669j-1-2026-09-12)

Assertions (38):
  1-13: mart 整体 shape (rows/cities/indicators/years/real/miss/rulings + lineage 4 件套)
  14-22: 5 粤 city 维度 (5 distinct + 350 cells + 0 real + 350 miss + missing_reason attribution)
  23-28: 5 粤 city lineage 三件套 (source_type + origin + ruling)
  29-33: 5 粤 city per-year breakdown (year × miss = 50 each)
  34-36: 5 粤 city × 10 indicator cross product (sanity)
  37: NO-OP 不手填 (real=0, miss=350)
  38: 守新增红线-1/-2 (2020 + 2026 5 city 全 miss)
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

CITY_5 = [
    "GUANGDONG_ZHUHAI",
    "GUANGDONG_ZHANJIANG",
    "GUANGDONG_SHANTOU",
    "GUANGDONG_JIANGMEN",
    "GUANGDONG_ZHAOQING",
]

INDICATORS = [
    "gdp_total", "gdp_growth", "primary_gdp", "secondary_gdp", "tertiary_gdp",
    "gdp_percapita", "fiscal_rev", "fixed_asset", "retail", "trade",
]


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
    print("=== knife 669j-1 红线 verify (38 assertions) ===")
    print(f"DB: {DB_HOST}:{DB_PORT}/{DB_NAME} table={SCHEMA}.{TABLE}")
    print()
    conn = psycopg2.connect(host=DB_HOST, port=DB_PORT, user=DB_USER,
                            password=DB_PASS, dbname=DB_NAME)
    cur = conn.cursor()

    city_list = ",".join(f"'{c}'" for c in CITY_5)

    # ===== Mart 整体 shape (1-13) =====

    # 1. mart 行数 = 2940 (42 city × 10 × 7)
    n = q(cur, f"SELECT COUNT(*) FROM {SCHEMA}.{TABLE}")[0]
    if n == 2940:
        p(f"row count = 2940 (42 city × 10 indicator × 7 year)")
    else:
        f(f"row count = {n}, expected 2940")

    # 2. city distinct = 42
    n = q(cur, f"SELECT COUNT(DISTINCT city_code) FROM {SCHEMA}.{TABLE}")[0]
    if n == 42:
        p(f"city distinct = 42 (37 prior + 5 粤卫星城)")
    else:
        f(f"city distinct = {n}, expected 42")

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

    # 5. real_cells = 1090 (NO-OP 不增)
    n = q(cur, f"SELECT COUNT(*) FROM {SCHEMA}.{TABLE} WHERE value IS NOT NULL")[0]
    if n == 1090:
        p(f"real_cells = 1090 (NO-OP 不增, 守新增红线-3 不手填)")
    else:
        f(f"real_cells = {n}, expected 1090")

    # 6. DATA_MISSING = 1850
    n = q(cur, f"SELECT COUNT(*) FROM {SCHEMA}.{TABLE} WHERE status = 'DATA_MISSING'")[0]
    if n == 1850:
        p(f"DATA_MISSING = 1850 (1500 prior + 350 新 5 city)")
    else:
        f(f"DATA_MISSING = {n}, expected 1850")

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

    # 8. lineage_ruling = 51 versions (+ K669j-1)
    n = q(cur, f"SELECT COUNT(DISTINCT lineage_ruling) FROM {SCHEMA}.{TABLE}")[0]
    if n == 51:
        p(f"lineage_ruling = 51 versions (50 prior + K669j-1-2026-09-12)")
    else:
        f(f"lineage_ruling distinct = {n}, expected 51")

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
        p(f"status 枚举合法")
    else:
        f(f"status 不合规 cells = {bad}")

    # 11. missing_reason 必填 for DATA_MISSING
    bad = q(cur, f"SELECT COUNT(*) FROM {SCHEMA}.{TABLE} WHERE status = 'DATA_MISSING' AND (missing_reason IS NULL OR missing_reason = '')")[0]
    if bad == 0:
        p(f"missing_reason 必填 for all DATA_MISSING cells")
    else:
        f(f"missing_reason 缺失 cells = {bad}")

    # 12. 2020 仍包含 669fix-b-2020 harvest (167 real) — 全局非禁; 仅 5 粤 city 强制 2020 全 DATA_MISSING (新增红线-1)
    n = q(cur, f"SELECT COUNT(*) FROM {SCHEMA}.{TABLE} WHERE year = 2020 AND value IS NOT NULL")[0]
    if n == 167:
        p(f"2020 包含 669fix-b-2020 harvest (167 real cells, 25 省会 × 7 指标)")
    else:
        f(f"2020 real cells = {n}, expected 167 (669fix-b-2020 baseline)")

    # 13. 2026 仍全 DATA_MISSING (新增红线-2)
    n = q(cur, f"SELECT COUNT(*) FROM {SCHEMA}.{TABLE} WHERE year = 2026 AND value IS NOT NULL")[0]
    if n == 0:
        p(f"2026 仍全 DATA_MISSING (新增红线-2: 禁补零)")
    else:
        f(f"2026 real cells = {n}, expected 0")

    # ===== 5 粤 city 维度 (14-22) =====

    # 14. 5 city distinct = 5
    n = q(cur, f"SELECT COUNT(DISTINCT city_code) FROM {SCHEMA}.{TABLE} WHERE city_code IN ({city_list})")[0]
    if n == 5:
        p(f"5 粤 satellite city distinct = 5 (ZHUHAI/ZHANJIANG/SHANTOU/JIANGMEN/ZHAOQING)")
    else:
        f(f"5 粤 city distinct = {n}, expected 5")

    # 15. 5 city cells = 350 (5 × 10 × 7)
    n = q(cur, f"SELECT COUNT(*) FROM {SCHEMA}.{TABLE} WHERE city_code IN ({city_list})")[0]
    if n == 350:
        p(f"5 粤 city cells = 350 (5 × 10 × 7 cross product)")
    else:
        f(f"5 粤 city cells = {n}, expected 350")

    # 16. 5 city real cells = 0 (NO-OP)
    n = q(cur, f"SELECT COUNT(*) FROM {SCHEMA}.{TABLE} WHERE city_code IN ({city_list}) AND value IS NOT NULL")[0]
    if n == 0:
        p(f"5 粤 city real cells = 0 (NO-OP, hongheiku 0 entry)")
    else:
        f(f"5 粤 city real cells = {n}, expected 0")

    # 17. 5 city MISSING cells = 350
    n = q(cur, f"SELECT COUNT(*) FROM {SCHEMA}.{TABLE} WHERE city_code IN ({city_list}) AND status = 'DATA_MISSING'")[0]
    if n == 350:
        p(f"5 粤 city MISSING cells = 350 (full DATA_MISSING path)")
    else:
        f(f"5 粤 city MISSING = {n}, expected 350")

    # 18. missing_reason 全 350/含 '669j-1'
    n = q(cur, f"""
        SELECT COUNT(*) FROM {SCHEMA}.{TABLE}
        WHERE city_code IN ({city_list})
          AND missing_reason LIKE '%669j-1%'
    """)[0]
    if n == 350:
        p(f"5 粤 city missing_reason 全 350/含 '669j-1' (sub-knife attribution)")
    else:
        f(f"5 粤 city missing_reason 含 '669j-1' = {n}, expected 350")

    # 19. missing_reason 含 'hongheiku 0 entry'
    n = q(cur, f"""
        SELECT COUNT(*) FROM {SCHEMA}.{TABLE}
        WHERE city_code IN ({city_list})
          AND missing_reason LIKE '%hongheiku 0 entry%'
    """)[0]
    if n == 350:
        p(f"5 粤 city missing_reason 全 350/含 'hongheiku 0 entry' (守红线-3)")
    else:
        f(f"5 粤 city missing_reason 'hongheiku 0 entry' = {n}/350")

    # 20. missing_reason 含 'tag 404' or 'cat index 0 ref'
    n = q(cur, f"""
        SELECT COUNT(*) FROM {SCHEMA}.{TABLE}
        WHERE city_code IN ({city_list})
          AND (missing_reason LIKE '%tag 404%' OR missing_reason LIKE '%cat index 0 ref%')
    """)[0]
    if n == 350:
        p(f"5 粤 city missing_reason 全 350/含 'tag 404' 或 'cat index 0 ref' (验证 detail)")
    else:
        f(f"5 粤 city missing_reason 'tag 404' or 'cat index 0 ref' = {n}/350")

    # 21. missing_reason 含 '15 HTTP'
    n = q(cur, f"""
        SELECT COUNT(*) FROM {SCHEMA}.{TABLE}
        WHERE city_code IN ({city_list})
          AND missing_reason LIKE '%15 HTTP%'
    """)[0]
    if n == 350:
        p(f"5 粤 city missing_reason 全 350/含 '15 HTTP 验证' (probe 数透明)")
    else:
        f(f"5 粤 city missing_reason '15 HTTP' = {n}/350")

    # 22. missing_reason 含 '不手填' (守新增红线-3)
    n = q(cur, f"""
        SELECT COUNT(*) FROM {SCHEMA}.{TABLE}
        WHERE city_code IN ({city_list})
          AND missing_reason LIKE '%不手填%'
    """)[0]
    if n == 350:
        p(f"5 粤 city missing_reason 全 350/含 '不手填' (守新增红线-3)")
    else:
        f(f"5 粤 city missing_reason '不手填' = {n}/350")

    # ===== 5 粤 city lineage 三件套 (23-28) =====

    # 23. 5 city 全 lineage_ruling = K669j-1-2026-09-12
    bad = q(cur, f"""
        SELECT COUNT(*) FROM {SCHEMA}.{TABLE}
        WHERE city_code IN ({city_list})
          AND lineage_ruling != 'K669j-1-2026-09-12'
    """)[0]
    if bad == 0:
        p(f"5 粤 city 全 lineage_ruling = 'K669j-1-2026-09-12'")
    else:
        f(f"5 粤 city lineage_ruling 异常: {bad} cells not K669j-1")

    # 24. 5 city 全 lineage_source_type = DATA_MISSING
    bad = q(cur, f"""
        SELECT COUNT(*) FROM {SCHEMA}.{TABLE}
        WHERE city_code IN ({city_list})
          AND lineage_source_type != 'DATA_MISSING'
    """)[0]
    if bad == 0:
        p(f"5 粤 city 全 lineage_source_type = 'DATA_MISSING' (无 hongheiku bulletin)")
    else:
        f(f"5 粤 city lineage_source_type 异常: {bad} cells")

    # 25. 5 city lineage_ruling K669j-1 唯一版本
    n = q(cur, f"SELECT COUNT(DISTINCT lineage_ruling) FROM {SCHEMA}.{TABLE} WHERE lineage_ruling LIKE '%669j-1%'")[0]
    if n == 1:
        p(f"lineage_ruling K669j-1-* 唯一版本: K669j-1-2026-09-12")
    else:
        f(f"669j-1 rulings 不唯一 = {n}")

    # 26. 5 city lineage_origin 含 'tag' or 'cat_djs' or 'cat_sjtjgb' (probe URL 透明)
    n = q(cur, f"""
        SELECT COUNT(*) FROM {SCHEMA}.{TABLE}
        WHERE city_code IN ({city_list})
          AND (lineage_origin LIKE '%tag%' OR lineage_origin LIKE '%cat_djs%' OR lineage_origin LIKE '%cat_sjtjgb%')
    """)[0]
    if n == 350:
        p(f"5 粤 city 全 lineage_origin 含 'tag'/'cat_djs'/'cat_sjtjgb' (probe URL 透明)")
    else:
        f(f"5 粤 city lineage_origin 透明 = {n}/350")

    # 27. 5 city lineage_origin 不为 null/空
    bad = q(cur, f"""
        SELECT COUNT(*) FROM {SCHEMA}.{TABLE}
        WHERE city_code IN ({city_list})
          AND (lineage_origin IS NULL OR lineage_origin = '')
    """)[0]
    if bad == 0:
        p(f"5 粤 city 全 lineage_origin 必填")
    else:
        f(f"5 粤 city lineage_origin 缺失 = {bad} cells")

    # 28. 5 city lineage_origin 含 'tjgb.hongheiku.com'
    n = q(cur, f"""
        SELECT COUNT(*) FROM {SCHEMA}.{TABLE}
        WHERE city_code IN ({city_list})
          AND lineage_origin LIKE '%tjgb.hongheiku.com%'
    """)[0]
    if n == 350:
        p(f"5 粤 city 全 lineage_origin 含 'tjgb.hongheiku.com' (来源 hongheiku 透明)")
    else:
        f(f"5 粤 city lineage_origin 'tjgb.hongheiku.com' = {n}/350")

    # ===== 5 粤 city per-year breakdown (29-33) =====

    # 29-33. 5 city × 6 year (2020-2025) = 50 each, all miss; 2026 = 50 miss
    for yr in [2020, 2021, 2022, 2023, 2024, 2025, 2026]:
        n_miss = q(cur, f"""
            SELECT COUNT(*) FROM {SCHEMA}.{TABLE}
            WHERE city_code IN ({city_list}) AND year = {yr} AND status = 'DATA_MISSING'
        """)[0]
        n_real = q(cur, f"""
            SELECT COUNT(*) FROM {SCHEMA}.{TABLE}
            WHERE city_code IN ({city_list}) AND year = {yr} AND value IS NOT NULL
        """)[0]
        if n_miss == 50 and n_real == 0:
            p(f"5 city × {yr} = 50 MISSING, 0 real (守红线-1/2)")
        else:
            f(f"5 city × {yr} miss={n_miss} real={n_real} (expected 50/0)")

    # ===== 5 粤 city × 10 indicator cross product (34-36) =====

    # 34. 5 city × 10 indicator = 50 each indicator
    for ind in INDICATORS:
        n = q(cur, f"""
            SELECT COUNT(*) FROM {SCHEMA}.{TABLE}
            WHERE city_code IN ({city_list}) AND indicator_key = '{ind}'
        """)[0]
        if n == 35:  # 5 city × 7 year
            p(f"5 city × {ind} = 35 cells (cross product)")
        else:
            f(f"5 city × {ind} = {n}, expected 35")

    # 35. 5 city × 10 indicator distinct = 10
    n = q(cur, f"""
        SELECT COUNT(DISTINCT indicator_key) FROM {SCHEMA}.{TABLE}
        WHERE city_code IN ({city_list})
    """)[0]
    if n == 10:
        p(f"5 city distinct indicator = 10 (cross product sanity)")
    else:
        f(f"5 city distinct indicator = {n}, expected 10")

    # 36. 5 city × 6 year (excl 2026) = 300 (NO-OP window)
    n = q(cur, f"""
        SELECT COUNT(*) FROM {SCHEMA}.{TABLE}
        WHERE city_code IN ({city_list}) AND year BETWEEN 2020 AND 2025
    """)[0]
    if n == 300:
        p(f"5 city × 6 year (2020-2025) = 300 cells (NO-OP window)")
    else:
        f(f"5 city × 6 year = {n}, expected 300")

    # ===== NO-OP 守门 (37-38) =====

    # 37. NO-OP 不手填 (real=0, miss=350)
    n_real = q(cur, f"""
        SELECT COUNT(*) FROM {SCHEMA}.{TABLE}
        WHERE city_code IN ({city_list}) AND value IS NOT NULL
    """)[0]
    n_miss = q(cur, f"""
        SELECT COUNT(*) FROM {SCHEMA}.{TABLE}
        WHERE city_code IN ({city_list}) AND status = 'DATA_MISSING'
    """)[0]
    if n_real == 0 and n_miss == 350:
        p(f"NO-OP 不手填: 5 city real=0, MISS=350 (守新增红线-3)")
    else:
        f(f"NO-OP 不手填 异常: real={n_real}, MISS={n_miss}")

    # 38. 守新增红线-1 (2020 5 city 全 miss) + 守新增红线-2 (2026 5 city 全 miss)
    n_2020_real = q(cur, f"""
        SELECT COUNT(*) FROM {SCHEMA}.{TABLE}
        WHERE city_code IN ({city_list}) AND year = 2020 AND value IS NOT NULL
    """)[0]
    n_2026_real = q(cur, f"""
        SELECT COUNT(*) FROM {SCHEMA}.{TABLE}
        WHERE city_code IN ({city_list}) AND year = 2026 AND value IS NOT NULL
    """)[0]
    if n_2020_real == 0 and n_2026_real == 0:
        p(f"5 city 2020 + 2026 全 MISSING (守新增红线-1 禁编造历史年 / 红线-2 禁补零)")
    else:
        f(f"5 city 2020/2026 real: {n_2020_real}/{n_2026_real}, expected 0/0")

    cur.close()
    conn.close()

    print()
    print(f"=== knife 669j-1 红线 summary: {PASS}/{PASS+FAIL} PASS, {FAIL} FAIL ===")
    sys.exit(0 if FAIL == 0 else 1)


if __name__ == "__main__":
    main()
