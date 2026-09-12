#!/usr/bin/env python3
"""
669j-4 红线 verify
==================

knife 669j sub-knife 4/6 (2026-09-13): 5 city cross-province NO-OP
  ZHEJIANG_JINHUA, HUBEI_XIANGYANG, HUBEI_JINGMEN, HUBEI_HUANGGANG, HUBEI_XIAOGAN

baseline (post-669j-3): 52 cities, 3640 rows, 1146 real, 2494 miss, 58 ruling_versions
post-669j-4 expectation (delta-based):
  - cities 57 (52 + 5)
  - rows 3990 (57 × 10 × 7)
  - 5 city cells 350
  - 5 city real 0 (NO-OP)
  - 5 city MISSING 350
  - 4 lineage_ruling 669j-* versions
  - per-province: ZHEJIANG +1 city (JINHUA), HUBEI +4 city
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
NC = "\033[0m"

PASS = 0
FAIL = 0

CITY_5 = [
    "ZHEJIANG_JINHUA",
    "HUBEI_XIANGYANG",
    "HUBEI_JINGMEN",
    "HUBEI_HUANGGANG",
    "HUBEI_XIAOGAN",
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
    print("=== knife 669j-4 红线 verify ===")
    print(f"DB: {DB_HOST}:{DB_PORT}/{DB_NAME} table={SCHEMA}.{TABLE}")
    print()
    conn = psycopg2.connect(host=DB_HOST, port=DB_PORT, user=DB_USER,
                            password=DB_PASS, dbname=DB_NAME)
    cur = conn.cursor()

    city_list = ",".join(f"'{c}'" for c in CITY_5)

    # 1-13: mart 整体 shape
    n = q(cur, f"SELECT COUNT(*) FROM {SCHEMA}.{TABLE}")[0]
    if n == 3990:
        p(f"row count = 3990 (57 × 10 × 7)")
    else:
        f(f"row count = {n}, expected 3990")

    n = q(cur, f"SELECT COUNT(DISTINCT city_code) FROM {SCHEMA}.{TABLE}")[0]
    if n == 57:
        p(f"city distinct = 57 (52 prior + 5)")
    else:
        f(f"city distinct = {n}, expected 57")

    n = q(cur, f"SELECT COUNT(DISTINCT indicator_key) FROM {SCHEMA}.{TABLE}")[0]
    if n == 10:
        p(f"indicator distinct = 10")
    else:
        f(f"indicator distinct = {n}")

    n = q(cur, f"SELECT COUNT(DISTINCT year) FROM {SCHEMA}.{TABLE}")[0]
    if n == 7:
        p(f"year distinct = 7 (2020-2026)")
    else:
        f(f"year distinct = {n}")

    n = q(cur, f"SELECT COUNT(*) FROM {SCHEMA}.{TABLE} WHERE city_code IN ({city_list}) AND value IS NOT NULL")[0]
    if n == 0:
        p(f"5 city real = 0 (NO-OP)")
    else:
        f(f"5 city real = {n}")

    n = q(cur, f"SELECT COUNT(*) FROM {SCHEMA}.{TABLE} WHERE city_code IN ({city_list}) AND status = 'DATA_MISSING'")[0]
    if n == 350:
        p(f"5 city MISSING = 350")
    else:
        f(f"5 city MISSING = {n}")

    direct = q(cur, f"""
        SELECT COUNT(*) FROM {SCHEMA}.{TABLE}
        WHERE city_code LIKE 'BEIJING_%' OR city_code LIKE 'SHANGHAI_%'
           OR city_code LIKE 'TIANJIN_%' OR city_code LIKE 'CHONGQING_%'
    """)[0]
    if direct == 0:
        p(f"4 直辖市禁 (红线-7)")
    else:
        f(f"4 直辖市 found: {direct}")

    n = q(cur, f"SELECT COUNT(DISTINCT lineage_ruling) FROM {SCHEMA}.{TABLE} WHERE lineage_ruling LIKE '%669j%'")[0]
    if n == 4:
        p(f"669j-* 唯一 lineage_ruling = 4 (K669j-1/2/3/4)")
    else:
        f(f"669j-* rulings = {n}, expected 4")

    bad = q(cur, f"SELECT COUNT(*) FROM {SCHEMA}.{TABLE} WHERE lineage_is_demo != 'false' OR lineage_is_demo IS NULL")[0]
    if bad == 0:
        p(f"lineage_is_demo 全部 = 'false'")
    else:
        f(f"lineage_is_demo 异常: {bad}")

    bad = q(cur, f"""
        SELECT COUNT(*) FROM {SCHEMA}.{TABLE}
        WHERE status IS NOT NULL AND status NOT IN ('DATA_MISSING', 'OFFICIAL_INTAKED', 'HONGHEIKU_TRANSLOAD', 'unknown')
    """)[0]
    if bad == 0:
        p(f"status 枚举合法")
    else:
        f(f"status 不合规: {bad}")

    bad = q(cur, f"SELECT COUNT(*) FROM {SCHEMA}.{TABLE} WHERE status = 'DATA_MISSING' AND (missing_reason IS NULL OR missing_reason = '')")[0]
    if bad == 0:
        p(f"missing_reason 必填")
    else:
        f(f"missing_reason 缺失: {bad}")

    n = q(cur, f"SELECT COUNT(*) FROM {SCHEMA}.{TABLE} WHERE year = 2020 AND value IS NOT NULL")[0]
    if n == 167:
        p(f"2020 包含 669fix-b-2020 harvest (167)")
    else:
        f(f"2020 real = {n}")

    n = q(cur, f"SELECT COUNT(*) FROM {SCHEMA}.{TABLE} WHERE year = 2026 AND value IS NOT NULL")[0]
    if n == 0:
        p(f"2026 全 DATA_MISSING (红线-2)")
    else:
        f(f"2026 real = {n}")

    # 5 city 维度
    n = q(cur, f"SELECT COUNT(DISTINCT city_code) FROM {SCHEMA}.{TABLE} WHERE city_code IN ({city_list})")[0]
    if n == 5:
        p(f"5 city distinct = 5")
    else:
        f(f"5 city distinct = {n}")

    n = q(cur, f"SELECT COUNT(*) FROM {SCHEMA}.{TABLE} WHERE city_code IN ({city_list})")[0]
    if n == 350:
        p(f"5 city cells = 350")
    else:
        f(f"5 city cells = {n}")

    n = q(cur, f"""
        SELECT COUNT(*) FROM {SCHEMA}.{TABLE}
        WHERE city_code IN ({city_list})
          AND missing_reason LIKE '%669j-4%'
    """)[0]
    if n == 350:
        p(f"missing_reason 全 350/含 '669j-4'")
    else:
        f(f"missing_reason '669j-4' = {n}/350")

    n = q(cur, f"""
        SELECT COUNT(*) FROM {SCHEMA}.{TABLE}
        WHERE city_code IN ({city_list})
          AND missing_reason LIKE '%hongheiku 0 entry%'
    """)[0]
    if n == 350:
        p(f"missing_reason 含 'hongheiku 0 entry'")
    else:
        f(f"missing_reason 'hongheiku 0 entry' = {n}/350")

    n = q(cur, f"""
        SELECT COUNT(*) FROM {SCHEMA}.{TABLE}
        WHERE city_code IN ({city_list})
          AND missing_reason LIKE '%5 HTTP%'
    """)[0]
    if n == 350:
        p(f"missing_reason 含 '5 HTTP'")
    else:
        f(f"missing_reason '5 HTTP' = {n}/350")

    n = q(cur, f"""
        SELECT COUNT(*) FROM {SCHEMA}.{TABLE}
        WHERE city_code IN ({city_list})
          AND missing_reason LIKE '%不手填%'
    """)[0]
    if n == 350:
        p(f"missing_reason 含 '不手填'")
    else:
        f(f"missing_reason '不手填' = {n}/350")

    # lineage 三件套
    bad = q(cur, f"""
        SELECT COUNT(*) FROM {SCHEMA}.{TABLE}
        WHERE city_code IN ({city_list})
          AND lineage_ruling != 'K669j-4-2026-09-13'
    """)[0]
    if bad == 0:
        p(f"5 city 全 lineage_ruling = 'K669j-4-2026-09-13'")
    else:
        f(f"lineage_ruling 异常: {bad}")

    bad = q(cur, f"""
        SELECT COUNT(*) FROM {SCHEMA}.{TABLE}
        WHERE city_code IN ({city_list})
          AND lineage_source_type != 'DATA_MISSING'
    """)[0]
    if bad == 0:
        p(f"5 city 全 lineage_source_type = 'DATA_MISSING'")
    else:
        f(f"lineage_source_type 异常: {bad}")

    n = q(cur, f"SELECT COUNT(DISTINCT lineage_ruling) FROM {SCHEMA}.{TABLE} WHERE lineage_ruling LIKE '%669j-4%'")[0]
    if n == 1:
        p(f"K669j-4-* 唯一版本")
    else:
        f(f"K669j-4 rulings 不唯一 = {n}")

    n = q(cur, f"""
        SELECT COUNT(*) FROM {SCHEMA}.{TABLE}
        WHERE city_code IN ({city_list})
          AND lineage_origin LIKE '%tjgb.hongheiku.com%'
    """)[0]
    if n == 350:
        p(f"lineage_origin 含 'tjgb.hongheiku.com'")
    else:
        f(f"lineage_origin 'tjgb.hongheiku.com' = {n}/350")

    bad = q(cur, f"""
        SELECT COUNT(*) FROM {SCHEMA}.{TABLE}
        WHERE city_code IN ({city_list})
          AND (lineage_origin IS NULL OR lineage_origin = '')
    """)[0]
    if bad == 0:
        p(f"lineage_origin 必填")
    else:
        f(f"lineage_origin 缺失: {bad}")

    n = q(cur, f"""
        SELECT COUNT(*) FROM {SCHEMA}.{TABLE}
        WHERE city_code IN ({city_list})
          AND (lineage_origin LIKE '%JINHUA%' OR lineage_origin LIKE '%XIANGYANG%'
               OR lineage_origin LIKE '%JINGMEN%' OR lineage_origin LIKE '%HUANGGANG%'
               OR lineage_origin LIKE '%XIAOGAN%')
    """)[0]
    if n == 350:
        p(f"lineage_origin 含 5 city 名")
    else:
        f(f"lineage_origin 含 city 名 = {n}/350")

    # per-year breakdown
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
            p(f"5 city × {yr} = 50 MISS, 0 real")
        else:
            f(f"5 city × {yr} miss={n_miss} real={n_real}")

    # 10 indicator
    for ind in INDICATORS:
        n = q(cur, f"""
            SELECT COUNT(*) FROM {SCHEMA}.{TABLE}
            WHERE city_code IN ({city_list}) AND indicator_key = '{ind}'
        """)[0]
        if n == 35:
            p(f"5 city × {ind} = 35")
        else:
            f(f"5 city × {ind} = {n}")

    # NO-OP 守门
    n_real = q(cur, f"""
        SELECT COUNT(*) FROM {SCHEMA}.{TABLE}
        WHERE city_code IN ({city_list}) AND value IS NOT NULL
    """)[0]
    n_miss = q(cur, f"""
        SELECT COUNT(*) FROM {SCHEMA}.{TABLE}
        WHERE city_code IN ({city_list}) AND status = 'DATA_MISSING'
    """)[0]
    if n_real == 0 and n_miss == 350:
        p(f"NO-OP 不手填: real=0, MISS=350")
    else:
        f(f"NO-OP 异常: real={n_real}, MISS={n_miss}")

    n_2020 = q(cur, f"""
        SELECT COUNT(*) FROM {SCHEMA}.{TABLE}
        WHERE city_code IN ({city_list}) AND year = 2020 AND value IS NOT NULL
    """)[0]
    n_2026 = q(cur, f"""
        SELECT COUNT(*) FROM {SCHEMA}.{TABLE}
        WHERE city_code IN ({city_list}) AND year = 2026 AND value IS NOT NULL
    """)[0]
    if n_2020 == 0 and n_2026 == 0:
        p(f"5 city 2020 + 2026 全 MISSING (红线-1/-2)")
    else:
        f(f"5 city 2020/2026 real: {n_2020}/{n_2026}")

    # cross-province test (5 city 跨 2 province)
    n_prov = q(cur, f"""
        SELECT COUNT(DISTINCT province_code) FROM {SCHEMA}.{TABLE}
        WHERE city_code IN ({city_list})
    """)[0]
    if n_prov == 2:
        p(f"5 city 跨 2 province (ZHEJIANG + HUBEI)")
    else:
        f(f"5 city 跨 {n_prov} province, expected 2")

    # ZHEJIANG 新增 1 city
    n = q(cur, f"""
        SELECT COUNT(DISTINCT city_code) FROM {SCHEMA}.{TABLE}
        WHERE province_code = 'ZHEJIANG' AND city_code IN ({city_list})
    """)[0]
    if n == 1:
        p(f"ZHEJIANG 新增 1 city (JINHUA)")
    else:
        f(f"ZHEJIANG 新增 city = {n}")

    # HUBEI 新增 4 city
    n = q(cur, f"""
        SELECT COUNT(DISTINCT city_code) FROM {SCHEMA}.{TABLE}
        WHERE province_code = 'HUBEI' AND city_code IN ({city_list})
    """)[0]
    if n == 4:
        p(f"HUBEI 新增 4 city (XIANGYANG/JINGMEN/HUANGGANG/XIAOGAN)")
    else:
        f(f"HUBEI 新增 city = {n}")

    cur.close()
    conn.close()

    print()
    print(f"=== knife 669j-4 红线 summary: {PASS}/{PASS+FAIL} PASS, {FAIL} FAIL ===")
    sys.exit(0 if FAIL == 0 else 1)


if __name__ == "__main__":
    main()