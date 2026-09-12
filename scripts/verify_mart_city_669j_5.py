#!/usr/bin/env python3
"""
669j-5 红线 verify

knife 669j sub-knife 5/6 (2026-09-13): 5 city cross-province NO-OP
  HUNAN_XIANGTAN, HUNAN_ZHUZHOU, HUNAN_YUEYANG, HUNAN_CHANGDE, ANHUI_WUHU
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
    "HUNAN_XIANGTAN",
    "HUNAN_ZHUZHOU",
    "HUNAN_YUEYANG",
    "HUNAN_CHANGDE",
    "ANHUI_WUHU",
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
    print("=== knife 669j-5 红线 verify ===")
    print(f"DB: {DB_HOST}:{DB_PORT}/{DB_NAME} table={SCHEMA}.{TABLE}")
    print()
    conn = psycopg2.connect(host=DB_HOST, port=DB_PORT, user=DB_USER,
                            password=DB_PASS, dbname=DB_NAME)
    cur = conn.cursor()

    city_list = ",".join(f"'{c}'" for c in CITY_5)

    n = q(cur, f"SELECT COUNT(*) FROM {SCHEMA}.{TABLE}")[0]
    if n == 4340:
        p(f"row count = 4340 (62 × 10 × 7)")
    else:
        f(f"row count = {n}, expected 4340")

    n = q(cur, f"SELECT COUNT(DISTINCT city_code) FROM {SCHEMA}.{TABLE}")[0]
    if n == 62:
        p(f"city distinct = 62 (57 prior + 5)")
    else:
        f(f"city distinct = {n}, expected 62")

    n = q(cur, f"SELECT COUNT(DISTINCT indicator_key) FROM {SCHEMA}.{TABLE}")[0]
    if n == 10:
        p(f"indicator distinct = 10")
    else:
        f(f"indicator distinct = {n}")

    n = q(cur, f"SELECT COUNT(DISTINCT year) FROM {SCHEMA}.{TABLE}")[0]
    if n == 7:
        p(f"year distinct = 7")
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
    if n == 5:
        p(f"669j-* 唯一 lineage_ruling = 5 (K669j-1/2/3/4/5)")
    else:
        f(f"669j-* rulings = {n}, expected 5")

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

    for tag in ["669j-5", "hongheiku 0 entry", "5 HTTP", "不手填"]:
        n = q(cur, f"""
            SELECT COUNT(*) FROM {SCHEMA}.{TABLE}
            WHERE city_code IN ({city_list})
              AND missing_reason LIKE '%{tag}%'
        """)[0]
        if n == 350:
            p(f"missing_reason 含 '{tag}' (350)")
        else:
            f(f"missing_reason '{tag}' = {n}/350")

    bad = q(cur, f"""
        SELECT COUNT(*) FROM {SCHEMA}.{TABLE}
        WHERE city_code IN ({city_list})
          AND lineage_ruling != 'K669j-5-2026-09-13'
    """)[0]
    if bad == 0:
        p(f"5 city 全 lineage_ruling = 'K669j-5-2026-09-13'")
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

    n = q(cur, f"SELECT COUNT(DISTINCT lineage_ruling) FROM {SCHEMA}.{TABLE} WHERE lineage_ruling LIKE '%669j-5%'")[0]
    if n == 1:
        p(f"K669j-5-* 唯一版本")
    else:
        f(f"K669j-5 rulings 不唯一 = {n}")

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
          AND (lineage_origin LIKE '%XIANGTAN%' OR lineage_origin LIKE '%ZHUZHOU%'
               OR lineage_origin LIKE '%YUEYANG%' OR lineage_origin LIKE '%CHANGDE%'
               OR lineage_origin LIKE '%WUHU%')
    """)[0]
    if n == 350:
        p(f"lineage_origin 含 5 city 名")
    else:
        f(f"lineage_origin 含 city 名 = {n}/350")

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

    for ind in INDICATORS:
        n = q(cur, f"""
            SELECT COUNT(*) FROM {SCHEMA}.{TABLE}
            WHERE city_code IN ({city_list}) AND indicator_key = '{ind}'
        """)[0]
        if n == 35:
            p(f"5 city × {ind} = 35")
        else:
            f(f"5 city × {ind} = {n}")

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
        p(f"5 city 2020 + 2026 全 MISSING")
    else:
        f(f"5 city 2020/2026 real: {n_2020}/{n_2026}")

    n_prov = q(cur, f"""
        SELECT COUNT(DISTINCT province_code) FROM {SCHEMA}.{TABLE}
        WHERE city_code IN ({city_list})
    """)[0]
    if n_prov == 2:
        p(f"5 city 跨 2 province (HUNAN + ANHUI)")
    else:
        f(f"5 city 跨 {n_prov} province, expected 2")

    n = q(cur, f"""
        SELECT COUNT(DISTINCT city_code) FROM {SCHEMA}.{TABLE}
        WHERE province_code = 'HUNAN' AND city_code IN ({city_list})
    """)[0]
    if n == 4:
        p(f"HUNAN 新增 4 city (XIANGTAN/ZHUZHOU/YUEYANG/CHANGDE)")
    else:
        f(f"HUNAN 新增 city = {n}")

    n = q(cur, f"""
        SELECT COUNT(DISTINCT city_code) FROM {SCHEMA}.{TABLE}
        WHERE province_code = 'ANHUI' AND city_code IN ({city_list})
    """)[0]
    if n == 1:
        p(f"ANHUI 新增 1 city (WUHU)")
    else:
        f(f"ANHUI 新增 city = {n}")

    cur.close()
    conn.close()

    print()
    print(f"=== knife 669j-5 红线 summary: {PASS}/{PASS+FAIL} PASS, {FAIL} FAIL ===")
    sys.exit(0 if FAIL == 0 else 1)


if __name__ == "__main__":
    main()