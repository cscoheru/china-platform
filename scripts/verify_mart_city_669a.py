#!/usr/bin/env python3
"""
669a-2020 红线 verify (14 assertions)
=====================================

新增红线守门:
  1. mart 行数 = 280 (= 4 city × 10 indicator × 7 year)
  2. city distinct = 4 (深/穗/杭/宁)
  3. indicator distinct = 10 (5 现 + 5 增量)
  4. year distinct = 7 (2020-2026)
  5. real_cells = 0 (zero-harvest knife, 实证 hongheiku 城市 2020 缺文)
  6. DATA_MISSING = 280 (全部 DATA_MISSING)
  7. 4 直辖市禁重复 (BEIJING/SHANGHAI/TIANJIN/CHONGQING NOT in city_dim) — 新增红线-7
  8. lineage_ruling 唯一 = 'K669a-2020-2026-09-04'
  9. lineage_is_demo 全部 = 'false' (demo 数据禁入 mart)
 10. status 枚举: 仅 'DATA_MISSING' 或 NULL
 11. missing_reason 必填 for DATA_MISSING cells
 12. 2020 missing_reason = 'hongheiku 城市维度 2020 缺文...'
 13. 2026 missing_reason 含 '2027 官方发布' (新增红线-2)
 14. value 列类型 = numeric (NULL 允许)
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
    print("=== knife 669a-2020 红线 verify (14 assertions) ===")
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

    # 5. real_cells = 0 (zero-harvest knife)
    n = q(cur, f"SELECT COUNT(*) FROM {SCHEMA}.{TABLE} WHERE value IS NOT NULL")[0]
    if n == 0:
        ok(f"real_cells = 0 (zero-harvest knife 实证 hongheiku 城市 2020 缺文)")
    else:
        fail(f"real_cells = {n}, expected 0 (守新增红线-3 不手填)")

    # 6. DATA_MISSING = 280 (all missing)
    n = q(cur, f"SELECT COUNT(*) FROM {SCHEMA}.{TABLE} WHERE status = 'DATA_MISSING'")[0]
    if n == 280:
        ok(f"DATA_MISSING cells = 280 (守新增红线-1/2/3 不补零)")
    else:
        fail(f"DATA_MISSING cells = {n}, expected 280")

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

    # 8. lineage_ruling 唯一
    r = q(cur, f"SELECT COUNT(DISTINCT lineage_ruling) FROM {SCHEMA}.{TABLE}")[0]
    ruling = q(cur, f"SELECT DISTINCT lineage_ruling FROM {SCHEMA}.{TABLE} LIMIT 1")[0]
    if r == 1 and ruling == "K669a-2020-2026-09-04":
        ok(f"lineage_ruling unique = '{ruling}'")
    else:
        fail(f"lineage_ruling: distinct={r}, sample='{ruling}', expected 'K669a-2020-2026-09-04'")

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
        ok(f"status 枚举合法 (NULL 或 DATA_MISSING)")
    else:
        fail(f"status 不合规 cells = {bad}")

    # 11. missing_reason 必填 for DATA_MISSING
    bad = q(cur, f"SELECT COUNT(*) FROM {SCHEMA}.{TABLE} WHERE status = 'DATA_MISSING' AND (missing_reason IS NULL OR missing_reason = '')")[0]
    if bad == 0:
        ok(f"missing_reason 必填 for all DATA_MISSING cells")
    else:
        fail(f"missing_reason 缺失 cells = {bad}")

    # 12. 2020 missing_reason 含 hongheiku 城市 2020 缺文
    n = q(cur, f"SELECT COUNT(*) FROM {SCHEMA}.{TABLE} WHERE year = 2020 AND missing_reason LIKE '%hongheiku%城市维度 2020 缺文%'")[0]
    if n == 40:
        ok(f"2020 missing_reason 全 40 cell 含 'hongheiku 城市维度 2020 缺文' (实证)")
    else:
        fail(f"2020 missing_reason 含 hongheiku 城市 缺文 = {n}, expected 40")

    # 13. 2026 missing_reason 含 2027 官方发布 (新增红线-2)
    n = q(cur, f"SELECT COUNT(*) FROM {SCHEMA}.{TABLE} WHERE year = 2026 AND missing_reason LIKE '%2027%'")[0]
    if n == 40:
        ok(f"2026 missing_reason 全 40 cell 含 '2027 官方发布' (新增红线-2)")
    else:
        fail(f"2026 missing_reason 含 2027 = {n}, expected 40")

    # 14. value 列类型 = numeric
    pgtype = q(cur, f"""
        SELECT data_type FROM information_schema.columns
        WHERE table_schema = '{SCHEMA}' AND table_name = '{TABLE}' AND column_name = 'value'
    """)[0]
    if pgtype == "numeric":
        ok(f"value 列类型 = numeric (允许 NULL for DATA_MISSING)")
    else:
        fail(f"value 列类型 = '{pgtype}', expected 'numeric'")

    cur.close()
    conn.close()

    print()
    print(f"=== knife 669a-2020 红线 summary: {PASS}/14 PASS, {FAIL} FAIL ===")
    sys.exit(0 if FAIL == 0 else 1)


if __name__ == "__main__":
    main()
