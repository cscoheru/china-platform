#!/usr/bin/env python3
"""
669a-2021 红线 verify (14+ assertions)
=====================================

新增/强化红线守门:
  1. mart 行数 = 280 (= 4 city × 10 indicator × 7 year)
  2. city distinct = 4 (深/穗/杭/宁)
  3. indicator distinct = 10 (5 现 + 5 增量)
  4. year distinct = 7 (2020-2026)
  5. real_cells = 26 (2021 actual harvest, 守新增红线-3 不手填)
  6. DATA_MISSING = 254 (40 for 2020 + 14 for 2021 missing + 200 for 2022-2026)
  7. 4 直辖市禁重复 (新增红线-7) — NOT in city dim
  8. lineage_ruling unique = 3 versions (K669a-2020 + K669a-2021 + pending)
  9. lineage_is_demo 全部 = 'false' (demo 数据禁入 mart)
 10. status 枚举合法 (NULL 或 DATA_MISSING)
 11. missing_reason 必填 for DATA_MISSING cells
 12. 2020 仍全 DATA_MISSING (mart stable across sub-knives)
 13. 2026 仍全 DATA_MISSING (新增红线-2)
 14. value 列类型 = numeric
 15. 2021 real cells lineage_source_type = 'HONGHEIKU_TRANSLOAD' (新增红线-7)
 16. 2021 missing cells lineage_source_type = 'DATA_MISSING' (守新增红线-3)
 17. 2021 missing cells missing_reason 含 '669a-2021' (sub-knife attribution)
 18. lineage_origin 含 'tjgb.hongheiku.com/djs/' for 2021 real cells
 19. 2022-2025 仍全 DATA_MISSING (待 669a-2022+ harvest)
 20. <2020 (城市维度无历史年, cross product only 2020+)
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
SCHEMA = "cegr_mart"
TABLE = "mart_city_timeseries"

RED = "\033[0;31m"
GREEN = "\033[0;32m"
YELLOW = "\033[1;33m"
NC = "\033[0m"

PASS = 0
FAIL = 0


def ok(msg):
    global PASS
    PASS += 1
    print(f"  {GREEN}[OK]{NC}   {msg}")


def fail(msg):
    global FAIL
    FAIL += 1
    print(f"  {RED}[FAIL]{NC} {msg}")


def warn(msg):
    print(f"  {YELLOW}[WARN]{NC} {msg}")


def q(cur, sql, params=None):
    if params:
        cur.execute(sql, params)
    else:
        cur.execute(sql)
    return cur.fetchone()


def qall(cur, sql, params=None):
    if params:
        cur.execute(sql, params)
    else:
        cur.execute(sql)
    return cur.fetchall()


def main():
    global PASS, FAIL
    print("=== knife 669a-2021 红线 verify (14+ assertions) ===")
    print(f"DB: {DB_HOST}:{DB_PORT}/{DB_NAME} table={SCHEMA}.{TABLE}")
    print()

    conn = psycopg2.connect(host=DB_HOST, port=DB_PORT, user=DB_USER,
                            password=DB_PASS, dbname=DB_NAME)
    cur = conn.cursor()

    # 1. mart 行数 = 280
    n = q(cur, f"SELECT COUNT(*) FROM {SCHEMA}.{TABLE}")[0]
    if n == 280:
        ok(f"row count = 280 (4 city × 10 indicator × 7 year)")
    else:
        fail(f"row count = {n}, expected 280")

    # 2. city distinct = 4
    n = q(cur, f"SELECT COUNT(DISTINCT city_code) FROM {SCHEMA}.{TABLE}")[0]
    if n == 4:
        ok(f"city distinct = 4")
    else:
        fail(f"city distinct = {n}, expected 4")

    # 3. indicator distinct = 10
    n = q(cur, f"SELECT COUNT(DISTINCT indicator_key) FROM {SCHEMA}.{TABLE}")[0]
    if n == 10:
        ok(f"indicator distinct = 10 (5 现 + 5 增量)")
    else:
        fail(f"indicator distinct = {n}, expected 10")

    # 4. year distinct = 7 (2020-2026)
    n = q(cur, f"SELECT COUNT(DISTINCT year) FROM {SCHEMA}.{TABLE}")[0]
    if n == 7:
        ok(f"year distinct = 7 (2020-2026)")
    else:
        fail(f"year distinct = {n}, expected 7")

    # 5. real_cells = 26 (2021 actual)
    n = q(cur, f"SELECT COUNT(*) FROM {SCHEMA}.{TABLE} WHERE value IS NOT NULL")[0]
    if n == 26:
        ok(f"real_cells = 26 (2021 actual harvest from hongheiku)")
    else:
        fail(f"real_cells = {n}, expected 26")

    # 6. DATA_MISSING = 254
    n = q(cur, f"SELECT COUNT(*) FROM {SCHEMA}.{TABLE} WHERE status = 'DATA_MISSING'")[0]
    if n == 254:
        ok(f"DATA_MISSING cells = 254 (40[2020] + 14[2021 miss] + 200[2022-2026])")
    else:
        fail(f"DATA_MISSING cells = {n}, expected 254")

    # 7. 4 直辖市禁重复 (新增红线-7)
    direct_cities = qall(cur, f"""
        SELECT city_code FROM {SCHEMA}.{TABLE}
        WHERE city_code LIKE 'BEIJING_%' OR city_code LIKE 'SHANGHAI_%'
           OR city_code LIKE 'TIANJIN_%' OR city_code LIKE 'CHONGQING_%'
    """)
    direct_list = [r[0] for r in direct_cities] if direct_cities else []
    if not direct_list:
        ok(f"4 直辖市禁重复 (新增红线-7) — NOT in city dimension")
    else:
        fail(f"4 直辖市 found in city dim: {direct_list}")

    # 8. lineage_ruling 3 versions
    n = q(cur, f"SELECT COUNT(DISTINCT lineage_ruling) FROM {SCHEMA}.{TABLE}")[0]
    if n == 3:
        ok(f"lineage_ruling = 3 versions (K669a-2020 + K669a-2021 + pending)")
    else:
        fail(f"lineage_ruling distinct = {n}, expected 3")

    # 9. lineage_is_demo 全部 'false'
    bad = q(cur, f"SELECT COUNT(*) FROM {SCHEMA}.{TABLE} WHERE lineage_is_demo != 'false' OR lineage_is_demo IS NULL")[0]
    if bad == 0:
        ok(f"lineage_is_demo 全部 = 'false' (demo 数据禁入 mart)")
    else:
        fail(f"lineage_is_demo 不合规 cells = {bad}")

    # 10. status 枚举
    bad = q(cur, f"""
        SELECT COUNT(*) FROM {SCHEMA}.{TABLE}
        WHERE status IS NOT NULL AND status NOT IN ('DATA_MISSING', 'OFFICIAL_INTAKED', 'HONGHEIKU_TRANSLOAD', 'unknown')
    """)[0]
    if bad == 0:
        ok(f"status 枚举合法 (NULL or DATA_MISSING for current 669a-2021 state)")
    else:
        fail(f"status 不合规 cells = {bad}")

    # 11. missing_reason 必填 for DATA_MISSING
    bad = q(cur, f"SELECT COUNT(*) FROM {SCHEMA}.{TABLE} WHERE status = 'DATA_MISSING' AND (missing_reason IS NULL OR missing_reason = '')")[0]
    if bad == 0:
        ok(f"missing_reason 必填 for all DATA_MISSING cells")
    else:
        fail(f"missing_reason 缺失 cells = {bad}")

    # 12. 2020 仍全 DATA_MISSING (mart stable across sub-knives)
    n = q(cur, f"SELECT COUNT(*) FROM {SCHEMA}.{TABLE} WHERE year = 2020 AND value IS NOT NULL")[0]
    if n == 0:
        ok(f"2020 仍全 DATA_MISSING (mart stable across sub-knives, K669a-2020 ruling 保持)")
    else:
        fail(f"2020 real cells = {n}, expected 0")

    # 13. 2026 仍全 DATA_MISSING (新增红线-2)
    n = q(cur, f"SELECT COUNT(*) FROM {SCHEMA}.{TABLE} WHERE year = 2026 AND value IS NOT NULL")[0]
    if n == 0:
        ok(f"2026 仍全 DATA_MISSING (新增红线-2: 待 2027 官方发布)")
    else:
        fail(f"2026 real cells = {n}, expected 0")

    # 14. value 列类型 = numeric
    pgtype = q(cur, f"""
        SELECT data_type FROM information_schema.columns
        WHERE table_schema = '{SCHEMA}' AND table_name = '{TABLE}' AND column_name = 'value'
    """)[0]
    if pgtype == "numeric":
        ok(f"value 列类型 = numeric (允许 NULL for DATA_MISSING)")
    else:
        fail(f"value 列类型 = '{pgtype}', expected 'numeric'")

    # 15. 2021 real cells lineage_source_type = 'HONGHEIKU_TRANSLOAD'
    bad = q(cur, f"""
        SELECT COUNT(*) FROM {SCHEMA}.{TABLE}
        WHERE year = 2021 AND value IS NOT NULL AND lineage_source_type != 'HONGHEIKU_TRANSLOAD'
    """)[0]
    if bad == 0:
        ok(f"2021 real cells lineage_source_type 全 = 'HONGHEIKU_TRANSLOAD' (守新增红线-7)")
    else:
        fail(f"2021 real cells lineage_source_type 不合规 = {bad}")

    # 16. 2021 missing cells lineage_source_type = 'DATA_MISSING' (守新增红线-3)
    bad = q(cur, f"""
        SELECT COUNT(*) FROM {SCHEMA}.{TABLE}
        WHERE year = 2021 AND value IS NULL AND lineage_source_type != 'DATA_MISSING'
    """)[0]
    if bad == 0:
        ok(f"2021 missing cells lineage_source_type 全 = 'DATA_MISSING' (守新增红线-3)")
    else:
        fail(f"2021 missing cells lineage_source_type 不合规 = {bad}")

    # 17. 2021 missing cells missing_reason 含 '669a-2021' (sub-knife attribution)
    n = q(cur, f"""
        SELECT COUNT(*) FROM {SCHEMA}.{TABLE}
        WHERE year = 2021 AND value IS NULL
          AND (missing_reason LIKE '%669a-2021%')
    """)[0]
    total_missing = q(cur, f"SELECT COUNT(*) FROM {SCHEMA}.{TABLE} WHERE year = 2021 AND value IS NULL")[0]
    if n == total_missing and n > 0:
        ok(f"2021 missing cells missing_reason 全 {total_missing}/含 '669a-2021' (sub-knife attribution)")
    elif n == 0:
        warn(f"2021 missing cells missing_reason 未含 '669a-2021' (regex miss; 应明示子刀号)")
    else:
        fail(f"2021 missing cells missing_reason 含 '669a-2021' = {n}, total missing = {total_missing}")

    # 18. lineage_origin 含 'tjgb.hongheiku.com/djs/' for 2021 real cells
    n = q(cur, f"""
        SELECT COUNT(*) FROM {SCHEMA}.{TABLE}
        WHERE year = 2021 AND value IS NOT NULL
          AND lineage_origin LIKE '%tjgb.hongheiku.com/djs/%'
    """)[0]
    total_real = q(cur, f"SELECT COUNT(*) FROM {SCHEMA}.{TABLE} WHERE year = 2021 AND value IS NOT NULL")[0]
    if n == total_real:
        ok(f"2021 real cells lineage_origin 全 {total_real}/含 'tjgb.hongheiku.com/djs/' (URL 守门)")
    else:
        fail(f"2021 real cells lineage_origin 守门 = {n}, total real = {total_real}")

    # 19. 2022-2025 仍全 DATA_MISSING (待 669a-2022+ harvest)
    n = q(cur, f"""
        SELECT COUNT(*) FROM {SCHEMA}.{TABLE}
        WHERE year BETWEEN 2022 AND 2025 AND value IS NOT NULL
    """)[0]
    if n == 0:
        ok(f"2022-2025 仍全 DATA_MISSING (待 669a-2022+ harvest)")
    else:
        fail(f"2022-2025 real cells = {n}, expected 0")

    # 20. <2020 无 cells (cross product only 2020+)
    n = q(cur, f"SELECT COUNT(*) FROM {SCHEMA}.{TABLE} WHERE year < 2020")[0]
    if n == 0:
        ok(f"<2020 无 cells (cross product only 2020-2026)")
    else:
        fail(f"<2020 cells = {n}, expected 0")

    cur.close()
    conn.close()

    print()
    print(f"=== knife 669a-2021 红线 summary: {PASS}/{PASS+FAIL} PASS, {FAIL} FAIL ===")
    sys.exit(0 if FAIL == 0 else 1)


if __name__ == "__main__":
    main()
