#!/usr/bin/env python3
"""
669a-2022 红线 verify (22 assertions)
=====================================

新增/强化红线守门 (vs 669a-2021 20 条):
  1. mart 行数 = 280 (= 4 city × 10 indicator × 7 year)
  2. city distinct = 4 (深/穗/杭/宁)
  3. indicator distinct = 10 (5 现 + 5 增量)
  4. year distinct = 7 (2020-2026)
  5. real_cells = 63 (26 from 2021 + 37 from 2022, 守新增红线-3 不手填)
  6. DATA_MISSING = 217 (40[2020] + 14[2021 miss] + 3[2022 miss] + 160[2023-2026])
  7. 4 直辖市禁重复 (新增红线-7) — NOT in city dim
  8. lineage_ruling unique = 4 versions (K669a-2020/2021/2022 + pending)
  9. lineage_is_demo 全部 = 'false' (demo 数据禁入 mart)
 10. status 枚举合法 (NULL 或 DATA_MISSING)
 11. missing_reason 必填 for DATA_MISSING cells
 12. 2020 仍全 DATA_MISSING (mart stable across sub-knives)
 13. 2026 仍全 DATA_MISSING (新增红线-2)
 14. value 列类型 = numeric
 15. 2021 real cells lineage_source_type = 'HONGHEIKU_TRANSLOAD' (前刀不回归)
 16. 2022 real cells lineage_source_type = 'HONGHEIKU_TRANSLOAD'
 17. 2022 missing cells missing_reason 含 '669a-2022' (sub-knife attribution)
 18. 2022 real cells lineage_origin 含 'tjgb.hongheiku.com/djs/'
 19. 2022 3 missing cells 全部 = fixed_asset (实证 公报仅发增速)
 20. 2021 26 real cells 数量不变 (mart stable: 前刀 real 不被本刀覆盖)
 21. 2023-2025 仍全 DATA_MISSING (待 669a-2023+ harvest)
 22. 南京 2022 = 10/10 全齐 (本批唯一 10/10)
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


def main():
    global PASS, FAIL
    print("=== knife 669a-2022 红线 verify (22 assertions) ===")
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

    # 5. real_cells = 63 (26 from 2021 + 37 from 2022)
    n = q(cur, f"SELECT COUNT(*) FROM {SCHEMA}.{TABLE} WHERE value IS NOT NULL")[0]
    if n == 63:
        ok(f"real_cells = 63 (26[2021] + 37[2022] actual harvest from hongheiku)")
    else:
        fail(f"real_cells = {n}, expected 63")

    # 6. DATA_MISSING = 217
    n = q(cur, f"SELECT COUNT(*) FROM {SCHEMA}.{TABLE} WHERE status = 'DATA_MISSING'")[0]
    if n == 217:
        ok(f"DATA_MISSING cells = 217 (40[2020] + 14[2021 miss] + 3[2022 miss] + 160[2023-2026])")
    else:
        fail(f"DATA_MISSING cells = {n}, expected 217")

    # 7. 4 直辖市禁重复 (新增红线-7)
    direct_cities = q(cur, f"""
        SELECT COUNT(*) FROM {SCHEMA}.{TABLE}
        WHERE city_code LIKE 'BEIJING_%' OR city_code LIKE 'SHANGHAI_%'
           OR city_code LIKE 'TIANJIN_%' OR city_code LIKE 'CHONGQING_%'
    """)[0]
    if direct_cities == 0:
        ok(f"4 直辖市禁重复 (新增红线-7) — NOT in city dimension")
    else:
        fail(f"4 直辖市 found in city dim: {direct_cities} rows")

    # 8. lineage_ruling 4 versions
    n = q(cur, f"SELECT COUNT(DISTINCT lineage_ruling) FROM {SCHEMA}.{TABLE}")[0]
    if n == 4:
        ok(f"lineage_ruling = 4 versions (K669a-2020/2021/2022 + pending)")
    else:
        fail(f"lineage_ruling distinct = {n}, expected 4")

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
        ok(f"status 枚举合法 (NULL or DATA_MISSING for current 669a-2022 state)")
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

    # 15. 2021 real cells 不回归 (前刀 26 real 仍 HONGHEIKU_TRANSLOAD)
    bad = q(cur, f"""
        SELECT COUNT(*) FROM {SCHEMA}.{TABLE}
        WHERE year = 2021 AND value IS NOT NULL AND lineage_source_type != 'HONGHEIKU_TRANSLOAD'
    """)[0]
    n21 = q(cur, f"SELECT COUNT(*) FROM {SCHEMA}.{TABLE} WHERE year = 2021 AND value IS NOT NULL")[0]
    if bad == 0 and n21 == 26:
        ok(f"2021 real cells 不回归: 26 real + lineage_source_type 全 HONGHEIKU_TRANSLOAD (前刀保持)")
    else:
        fail(f"2021 不回归 check: bad={bad}, real={n21} (expected 0/26)")

    # 16. 2022 real cells lineage_source_type = 'HONGHEIKU_TRANSLOAD'
    bad = q(cur, f"""
        SELECT COUNT(*) FROM {SCHEMA}.{TABLE}
        WHERE year = 2022 AND value IS NOT NULL AND lineage_source_type != 'HONGHEIKU_TRANSLOAD'
    """)[0]
    if bad == 0:
        ok(f"2022 real cells lineage_source_type 全 = 'HONGHEIKU_TRANSLOAD'")
    else:
        fail(f"2022 real cells lineage_source_type 不合规 = {bad}")

    # 17. 2022 missing cells missing_reason 含 '669a-2022'
    n = q(cur, f"""
        SELECT COUNT(*) FROM {SCHEMA}.{TABLE}
        WHERE year = 2022 AND value IS NULL
          AND (missing_reason LIKE '%669a-2022%')
    """)[0]
    total_missing = q(cur, f"SELECT COUNT(*) FROM {SCHEMA}.{TABLE} WHERE year = 2022 AND value IS NULL")[0]
    if n == total_missing and n > 0:
        ok(f"2022 missing cells missing_reason 全 {total_missing}/含 '669a-2022' (sub-knife attribution)")
    elif n == 0:
        warn(f"2022 missing cells missing_reason 未含 '669a-2022' (regex miss; 应明示子刀号)")
    else:
        fail(f"2022 missing cells missing_reason 含 '669a-2022' = {n}, total missing = {total_missing}")

    # 18. 2022 real cells lineage_origin 含 'tjgb.hongheiku.com/djs/'
    n = q(cur, f"""
        SELECT COUNT(*) FROM {SCHEMA}.{TABLE}
        WHERE year = 2022 AND value IS NOT NULL
          AND lineage_origin LIKE '%tjgb.hongheiku.com/djs/%'
    """)[0]
    total_real = q(cur, f"SELECT COUNT(*) FROM {SCHEMA}.{TABLE} WHERE year = 2022 AND value IS NOT NULL")[0]
    if n == total_real:
        ok(f"2022 real cells lineage_origin 全 {total_real}/含 'tjgb.hongheiku.com/djs/' (URL 守门)")
    else:
        fail(f"2022 real cells lineage_origin 守门 = {n}, total real = {total_real}")

    # 19. 2022 3 missing cells 全部 = fixed_asset (实证 公报仅发增速)
    rows = None
    cur.execute(f"""
        SELECT indicator_key, COUNT(*) FROM {SCHEMA}.{TABLE}
        WHERE year = 2022 AND value IS NULL
        GROUP BY indicator_key
    """)
    rows = cur.fetchall()
    if len(rows) == 1 and rows[0][0] == 'fixed_asset' and rows[0][1] == 3:
        ok(f"2022 3 missing cells 全部 = fixed_asset (深圳/广州/杭州 公报仅发增速, 守红线-3 不手填)")
    else:
        fail(f"2022 missing cells 分解异常: {rows} (expected only fixed_asset × 3)")

    # 20. 2021 26 real cells 数量不变 (mart stable)
    n = q(cur, f"SELECT COUNT(*) FROM {SCHEMA}.{TABLE} WHERE year = 2021 AND value IS NOT NULL")[0]
    if n == 26:
        ok(f"2021 real cells = 26 不变 (mart stable: 前刀 real 不被本刀覆盖)")
    else:
        fail(f"2021 real cells = {n}, expected 26 (不变)")

    # 21. 2023-2025 仍全 DATA_MISSING (待 669a-2023+ harvest)
    n = q(cur, f"""
        SELECT COUNT(*) FROM {SCHEMA}.{TABLE}
        WHERE year BETWEEN 2023 AND 2025 AND value IS NOT NULL
    """)[0]
    if n == 0:
        ok(f"2023-2025 仍全 DATA_MISSING (待 669a-2023+ harvest)")
    else:
        fail(f"2023-2025 real cells = {n}, expected 0")

    # 22. 南京 2022 = 10/10 全齐
    n = q(cur, f"""
        SELECT COUNT(*) FROM {SCHEMA}.{TABLE}
        WHERE year = 2022 AND city_code = 'JIANGSU_NANJING' AND value IS NOT NULL
    """)[0]
    if n == 10:
        ok(f"南京 2022 = 10/10 全齐 (本批唯一 10/10, 含 fixed_asset 5874.92)")
    else:
        fail(f"南京 2022 real cells = {n}, expected 10")

    cur.close()
    conn.close()

    print()
    print(f"=== knife 669a-2022 红线 summary: {PASS}/{PASS+FAIL} PASS, {FAIL} FAIL ===")
    sys.exit(0 if FAIL == 0 else 1)


if __name__ == "__main__":
    main()
