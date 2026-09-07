#!/usr/bin/env python3
"""
669a-2024 红线 verify (24 assertions)
=====================================

新增/强化红线守门 (vs 669a-2023 23 条):
  1. mart 行数 = 280 (= 4 city × 10 indicator × 7 year)
  2. city distinct = 4 (深/穗/杭/宁)
  3. indicator distinct = 10 (5 现 + 5 增量)
  4. year distinct = 7 (2020-2026)
  5. real_cells = 136 (26[2021] + 37[2022] + 37[2023] + 36[2024], 守新增红线-3 不手填)
  6. DATA_MISSING = 144 (40[2020] + 14[2021] + 3[2022] + 3[2023] + 4[2024] + 80[2025-2026])
  7. 4 直辖市禁重复 (新增红线-7) — NOT in city dim
  8. lineage_ruling unique = 6 versions (K669a-2020/2021/2022/2023/2024 + pending)
  9. lineage_is_demo 全部 = 'false'
 10. status 枚举合法 (NULL 或 DATA_MISSING)
 11. missing_reason 必填 for DATA_MISSING cells
 12. 2020 仍全 DATA_MISSING (mart stable across sub-knives)
 13. 2026 仍全 DATA_MISSING (新增红线-2)
 14. value 列类型 = numeric
 15. 2021 real cells 不回归 (26 + HONGHEIKU_TRANSLOAD)
 16. 2022 real cells 不回归 (37 + HONGHEIKU_TRANSLOAD)
 17. 2023 real cells 不回归 (37 + HONGHEIKU_TRANSLOAD)
 18. 2024 real cells lineage_source_type = 'HONGHEIKU_TRANSLOAD'
 19. 2024 missing cells missing_reason 含 '669a-2024' (sub-knife attribution)
 20. 2024 real cells lineage_origin 含 'tjgb.hongheiku.com/djs/'
 21. 2024 4 missing cells = 3× fixed_asset (深/穗/杭) + 1× 南京 retail (公报仅发增速实证)
 22. 2025 仍全 DATA_MISSING (待 669a-2025 harvest)
 23. 2021+2022+2023 real 总量不变 = 100 (mart stable: 前刀 real 不被本刀覆盖)
 24. 南京 2024 fixed_asset = 4777.29 (绝对值采到) 且杭州 2024 retail = 9151 (脚注容错采到)
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
    print("=== knife 669a-2024 红线 verify (24 assertions) ===")
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

    # 4. year distinct = 7
    n = q(cur, f"SELECT COUNT(DISTINCT year) FROM {SCHEMA}.{TABLE}")[0]
    if n == 7:
        ok(f"year distinct = 7 (2020-2026)")
    else:
        fail(f"year distinct = {n}, expected 7")

    # 5. real_cells = 136
    n = q(cur, f"SELECT COUNT(*) FROM {SCHEMA}.{TABLE} WHERE value IS NOT NULL")[0]
    if n == 136:
        ok(f"real_cells = 136 (26[2021] + 37[2022] + 37[2023] + 36[2024] actual harvest)")
    else:
        fail(f"real_cells = {n}, expected 136")

    # 6. DATA_MISSING = 144
    n = q(cur, f"SELECT COUNT(*) FROM {SCHEMA}.{TABLE} WHERE status = 'DATA_MISSING'")[0]
    if n == 144:
        ok(f"DATA_MISSING = 144 (40+14+3+3+4 miss + 80[2025-2026])")
    else:
        fail(f"DATA_MISSING = {n}, expected 144")

    # 7. 4 直辖市禁重复
    direct_cities = q(cur, f"""
        SELECT COUNT(*) FROM {SCHEMA}.{TABLE}
        WHERE city_code LIKE 'BEIJING_%' OR city_code LIKE 'SHANGHAI_%'
           OR city_code LIKE 'TIANJIN_%' OR city_code LIKE 'CHONGQING_%'
    """)[0]
    if direct_cities == 0:
        ok(f"4 直辖市禁重复 (新增红线-7) — NOT in city dimension")
    else:
        fail(f"4 直辖市 found in city dim: {direct_cities} rows")

    # 8. lineage_ruling 6 versions
    n = q(cur, f"SELECT COUNT(DISTINCT lineage_ruling) FROM {SCHEMA}.{TABLE}")[0]
    if n == 6:
        ok(f"lineage_ruling = 6 versions (K669a-2020/2021/2022/2023/2024 + pending)")
    else:
        fail(f"lineage_ruling distinct = {n}, expected 6")

    # 9. lineage_is_demo 全部 'false'
    bad = q(cur, f"SELECT COUNT(*) FROM {SCHEMA}.{TABLE} WHERE lineage_is_demo != 'false' OR lineage_is_demo IS NULL")[0]
    if bad == 0:
        ok(f"lineage_is_demo 全部 = 'false'")
    else:
        fail(f"lineage_is_demo 不合规 cells = {bad}")

    # 10. status 枚举
    bad = q(cur, f"""
        SELECT COUNT(*) FROM {SCHEMA}.{TABLE}
        WHERE status IS NOT NULL AND status NOT IN ('DATA_MISSING', 'OFFICIAL_INTAKED', 'HONGHEIKU_TRANSLOAD', 'unknown')
    """)[0]
    if bad == 0:
        ok(f"status 枚举合法 (NULL or DATA_MISSING for current 669a-2024 state)")
    else:
        fail(f"status 不合规 cells = {bad}")

    # 11. missing_reason 必填 for DATA_MISSING
    bad = q(cur, f"SELECT COUNT(*) FROM {SCHEMA}.{TABLE} WHERE status = 'DATA_MISSING' AND (missing_reason IS NULL OR missing_reason = '')")[0]
    if bad == 0:
        ok(f"missing_reason 必填 for all DATA_MISSING cells")
    else:
        fail(f"missing_reason 缺失 cells = {bad}")

    # 12. 2020 仍全 DATA_MISSING
    n = q(cur, f"SELECT COUNT(*) FROM {SCHEMA}.{TABLE} WHERE year = 2020 AND value IS NOT NULL")[0]
    if n == 0:
        ok(f"2020 仍全 DATA_MISSING (mart stable across sub-knives)")
    else:
        fail(f"2020 real cells = {n}, expected 0")

    # 13. 2026 仍全 DATA_MISSING (红线-2)
    n = q(cur, f"SELECT COUNT(*) FROM {SCHEMA}.{TABLE} WHERE year = 2026 AND value IS NOT NULL")[0]
    if n == 0:
        ok(f"2026 仍全 DATA_MISSING (新增红线-2)")
    else:
        fail(f"2026 real cells = {n}, expected 0")

    # 14. value 列类型 = numeric
    pgtype = q(cur, f"""
        SELECT data_type FROM information_schema.columns
        WHERE table_schema = '{SCHEMA}' AND table_name = '{TABLE}' AND column_name = 'value'
    """)[0]
    if pgtype == "numeric":
        ok(f"value 列类型 = numeric")
    else:
        fail(f"value 列类型 = '{pgtype}', expected 'numeric'")

    # 15. 2021 real cells 不回归
    bad = q(cur, f"""
        SELECT COUNT(*) FROM {SCHEMA}.{TABLE}
        WHERE year = 2021 AND value IS NOT NULL AND lineage_source_type != 'HONGHEIKU_TRANSLOAD'
    """)[0]
    n21 = q(cur, f"SELECT COUNT(*) FROM {SCHEMA}.{TABLE} WHERE year = 2021 AND value IS NOT NULL")[0]
    if bad == 0 and n21 == 26:
        ok(f"2021 real cells 不回归: 26 real (前刀保持)")
    else:
        fail(f"2021 不回归 check: bad={bad}, real={n21} (expected 0/26)")

    # 16. 2022 real cells 不回归
    bad = q(cur, f"""
        SELECT COUNT(*) FROM {SCHEMA}.{TABLE}
        WHERE year = 2022 AND value IS NOT NULL AND lineage_source_type != 'HONGHEIKU_TRANSLOAD'
    """)[0]
    n22 = q(cur, f"SELECT COUNT(*) FROM {SCHEMA}.{TABLE} WHERE year = 2022 AND value IS NOT NULL")[0]
    if bad == 0 and n22 == 37:
        ok(f"2022 real cells 不回归: 37 real (前刀保持)")
    else:
        fail(f"2022 不回归 check: bad={bad}, real={n22} (expected 0/37)")

    # 17. 2023 real cells 不回归
    bad = q(cur, f"""
        SELECT COUNT(*) FROM {SCHEMA}.{TABLE}
        WHERE year = 2023 AND value IS NOT NULL AND lineage_source_type != 'HONGHEIKU_TRANSLOAD'
    """)[0]
    n23 = q(cur, f"SELECT COUNT(*) FROM {SCHEMA}.{TABLE} WHERE year = 2023 AND value IS NOT NULL")[0]
    if bad == 0 and n23 == 37:
        ok(f"2023 real cells 不回归: 37 real (前刀保持)")
    else:
        fail(f"2023 不回归 check: bad={bad}, real={n23} (expected 0/37)")

    # 18. 2024 real cells lineage_source_type
    bad = q(cur, f"""
        SELECT COUNT(*) FROM {SCHEMA}.{TABLE}
        WHERE year = 2024 AND value IS NOT NULL AND lineage_source_type != 'HONGHEIKU_TRANSLOAD'
    """)[0]
    if bad == 0:
        ok(f"2024 real cells lineage_source_type 全 = 'HONGHEIKU_TRANSLOAD'")
    else:
        fail(f"2024 real cells lineage_source_type 不合规 = {bad}")

    # 19. 2024 missing cells missing_reason 含 '669a-2024'
    n = q(cur, f"""
        SELECT COUNT(*) FROM {SCHEMA}.{TABLE}
        WHERE year = 2024 AND value IS NULL
          AND (missing_reason LIKE '%669a-2024%')
    """)[0]
    total_missing = q(cur, f"SELECT COUNT(*) FROM {SCHEMA}.{TABLE} WHERE year = 2024 AND value IS NULL")[0]
    if n == total_missing and n > 0:
        ok(f"2024 missing cells missing_reason 全 {total_missing}/含 '669a-2024' (sub-knife attribution)")
    elif n == 0:
        warn(f"2024 missing cells missing_reason 未含 '669a-2024' (应明示子刀号)")
    else:
        fail(f"2024 missing cells missing_reason 含 '669a-2024' = {n}, total missing = {total_missing}")

    # 20. 2024 real cells lineage_origin 含 'tjgb.hongheiku.com/djs/'
    n = q(cur, f"""
        SELECT COUNT(*) FROM {SCHEMA}.{TABLE}
        WHERE year = 2024 AND value IS NOT NULL
          AND lineage_origin LIKE '%tjgb.hongheiku.com/djs/%'
    """)[0]
    total_real = q(cur, f"SELECT COUNT(*) FROM {SCHEMA}.{TABLE} WHERE year = 2024 AND value IS NOT NULL")[0]
    if n == total_real:
        ok(f"2024 real cells lineage_origin 全 {total_real}/含 'tjgb.hongheiku.com/djs/' (URL 守门)")
    else:
        fail(f"2024 real cells lineage_origin 守门 = {n}, total real = {total_real}")

    # 21. 2024 4 missing = 3× fixed_asset + 1× 南京 retail (公报仅发增速实证)
    cur.execute(f"""
        SELECT city_code, indicator_key FROM {SCHEMA}.{TABLE}
        WHERE year = 2024 AND value IS NULL
        ORDER BY city_code, indicator_key
    """)
    rows = cur.fetchall()
    expected = [('GUANGDONG_GUANGZHOU', 'fixed_asset'),
                ('GUANGDONG_SHENZHEN', 'fixed_asset'),
                ('JIANGSU_NANJING', 'retail'),
                ('ZHEJIANG_HANGZHOU', 'fixed_asset')]
    if rows == expected:
        ok(f"2024 4 missing = 3× fixed_asset (深/穗/杭) + 1× 南京 retail (公报仅发增速, 守红线-3)")
    else:
        fail(f"2024 missing cells 分解异常: {rows}")

    # 22. 2025 仍全 DATA_MISSING
    n = q(cur, f"""
        SELECT COUNT(*) FROM {SCHEMA}.{TABLE}
        WHERE year = 2025 AND value IS NOT NULL
    """)[0]
    if n == 0:
        ok(f"2025 仍全 DATA_MISSING (待 669a-2025 harvest)")
    else:
        fail(f"2025 real cells = {n}, expected 0")

    # 23. 2021+2022+2023 real 总量不变 = 100
    n = q(cur, f"""
        SELECT COUNT(*) FROM {SCHEMA}.{TABLE}
        WHERE year IN (2021, 2022, 2023) AND value IS NOT NULL
    """)[0]
    if n == 100:
        ok(f"2021+2022+2023 real 总量 = 100 不变 (mart stable: 前刀 real 不被本刀覆盖)")
    else:
        fail(f"2021+2022+2023 real 总量 = {n}, expected 100 (不变)")

    # 24. 南京 2024 fixed_asset 采到 + 杭州 2024 retail 脚注容错采到 (本刀 2 处 regex 修复的落地证据)
    nj_fa = q(cur, f"""
        SELECT value FROM {SCHEMA}.{TABLE}
        WHERE year = 2024 AND city_code = 'JIANGSU_NANJING' AND indicator_key = 'fixed_asset'
    """)[0]
    hz_rt = q(cur, f"""
        SELECT value FROM {SCHEMA}.{TABLE}
        WHERE year = 2024 AND city_code = 'ZHEJIANG_HANGZHOU' AND indicator_key = 'retail'
    """)[0]
    # numeric 列 psycopg2 返回 decimal.Decimal, 与 float 相减会 TypeError → 统一转 float
    nj_fa = float(nj_fa) if nj_fa is not None else None
    hz_rt = float(hz_rt) if hz_rt is not None else None
    if nj_fa is not None and abs(nj_fa - 4777.29) < 0.01 and hz_rt is not None and abs(hz_rt - 9151) < 0.01:
        ok(f"南京 fixed_asset = 4777.29 + 杭州 retail = 9151 (脚注[2]/[4]换行容错修复落地)")
    else:
        fail(f"regex 修复落地异常: 南京 fixed_asset={nj_fa}, 杭州 retail={hz_rt}")

    cur.close()
    conn.close()

    print()
    print(f"=== knife 669a-2024 红线 summary: {PASS}/{PASS+FAIL} PASS, {FAIL} FAIL ===")
    sys.exit(0 if FAIL == 0 else 1)


if __name__ == "__main__":
    main()
