#!/usr/bin/env python3
"""
669a-2025 红线 verify (26 assertions)
=====================================

vs 669a-2024 24 条 (+2 新增):
  1-24: mirror 2024 (real_cells=154 / DATA_MISSING=126 / rulings=7 / 2024 no-regression etc.)
  25: 2025 real cells 不回归 (18 + HONGHEIKU_TRANSLOAD) — 仅穗/杭 9 each
  26: 2025 missing cells missing_reason 全含 '669a-2025' (含 SZ/NJ 全部 DATA_MISSING 20 cells + GZ/HZ fixed_asset 2)
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
    print("=== knife 669a-2025 红线 verify (26 assertions) ===")
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

    # 5. real_cells = 154
    n = q(cur, f"SELECT COUNT(*) FROM {SCHEMA}.{TABLE} WHERE value IS NOT NULL")[0]
    if n == 154:
        ok(f"real_cells = 154 (26[2021] + 37[2022] + 37[2023] + 36[2024] + 18[2025])")
    else:
        fail(f"real_cells = {n}, expected 154")

    # 6. DATA_MISSING = 126
    n = q(cur, f"SELECT COUNT(*) FROM {SCHEMA}.{TABLE} WHERE status = 'DATA_MISSING'")[0]
    if n == 126:
        ok(f"DATA_MISSING = 126 (40[2020] + 14[2021] + 3[2022] + 3[2023] + 4[2024] + 22[2025] + 40[2026])")
    else:
        fail(f"DATA_MISSING = {n}, expected 126")

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

    # 8. lineage_ruling 7 versions
    n = q(cur, f"SELECT COUNT(DISTINCT lineage_ruling) FROM {SCHEMA}.{TABLE}")[0]
    if n == 7:
        ok(f"lineage_ruling = 7 versions (K669a-2020/2021/2022/2023/2024/2025 + pending)")
    else:
        fail(f"lineage_ruling distinct = {n}, expected 7")

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
        ok(f"status 枚举合法 (NULL or DATA_MISSING for current 669a-2025 state)")
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

    # 18. 2024 real cells 不回归
    bad = q(cur, f"""
        SELECT COUNT(*) FROM {SCHEMA}.{TABLE}
        WHERE year = 2024 AND value IS NOT NULL AND lineage_source_type != 'HONGHEIKU_TRANSLOAD'
    """)[0]
    n24 = q(cur, f"SELECT COUNT(*) FROM {SCHEMA}.{TABLE} WHERE year = 2024 AND value IS NOT NULL")[0]
    if bad == 0 and n24 == 36:
        ok(f"2024 real cells 不回归: 36 real (前刀保持)")
    else:
        fail(f"2024 不回归 check: bad={bad}, real={n24} (expected 0/36)")

    # 19. 2025 real cells lineage_source_type = HONGHEIKU_TRANSLOAD
    bad = q(cur, f"""
        SELECT COUNT(*) FROM {SCHEMA}.{TABLE}
        WHERE year = 2025 AND value IS NOT NULL AND lineage_source_type != 'HONGHEIKU_TRANSLOAD'
    """)[0]
    if bad == 0:
        ok(f"2025 real cells lineage_source_type 全 = 'HONGHEIKU_TRANSLOAD'")
    else:
        fail(f"2025 real cells lineage_source_type 不合规 = {bad}")

    # 20. 2025 real cells lineage_origin 含 'tjgb.hongheiku.com/djs/'
    n = q(cur, f"""
        SELECT COUNT(*) FROM {SCHEMA}.{TABLE}
        WHERE year = 2025 AND value IS NOT NULL
          AND lineage_origin LIKE '%tjgb.hongheiku.com/djs/%'
    """)[0]
    total_real = q(cur, f"SELECT COUNT(*) FROM {SCHEMA}.{TABLE} WHERE year = 2025 AND value IS NOT NULL")[0]
    if n == total_real:
        ok(f"2025 real cells lineage_origin 全 {total_real}/含 'tjgb.hongheiku.com/djs/' (URL 守门)")
    else:
        fail(f"2025 real cells lineage_origin 守门 = {n}, total real = {total_real}")

    # 21. 2025 22 missing = 20× SZ/NJ 全 miss + 2× fixed_asset (穗/杭)
    cur.execute(f"""
        SELECT city_code, indicator_key FROM {SCHEMA}.{TABLE}
        WHERE year = 2025 AND value IS NULL
        ORDER BY city_code, indicator_key
    """)
    rows = cur.fetchall()
    # Build expected: SZ 10 + NJ 10 + GZ fixed_asset + HZ fixed_asset = 22
    expected_set = set()
    for ind in ['gdp_total', 'gdp_growth', 'primary_gdp', 'secondary_gdp', 'tertiary_gdp',
                'gdp_percapita', 'fiscal_rev', 'fixed_asset', 'retail', 'trade']:
        expected_set.add(('GUANGDONG_SHENZHEN', ind))
        expected_set.add(('JIANGSU_NANJING', ind))
    expected_set.add(('GUANGDONG_GUANGZHOU', 'fixed_asset'))
    expected_set.add(('ZHEJIANG_HANGZHOU', 'fixed_asset'))
    if set(rows) == expected_set:
        ok(f"2025 22 missing = 20× SZ/NJ 全 (hongheiku 无 2025 entry) + 2× fixed_asset (穗-6.7%/杭占比, 守红线-3)")
    else:
        fail(f"2025 missing cells 分解异常: actual={set(rows) ^ expected_set}")

    # 22. 2025 real by city = only 穗/杭 9 each
    cur.execute(f"""
        SELECT city_code, COUNT(*) FROM {SCHEMA}.{TABLE}
        WHERE year = 2025 AND value IS NOT NULL
        GROUP BY city_code ORDER BY city_code
    """)
    rows = cur.fetchall()
    expected = [('GUANGDONG_GUANGZHOU', 9), ('ZHEJIANG_HANGZHOU', 9)]
    if rows == expected:
        ok(f"2025 real cells 分布: 仅穗/杭 各 9 (深/宁 hongheiku 无 2025 entry, 全部 DATA_MISSING)")
    else:
        fail(f"2025 real by city 异常: {rows}")

    # 23. 2021+2022+2023+2024 real 总量不变 = 136
    n = q(cur, f"""
        SELECT COUNT(*) FROM {SCHEMA}.{TABLE}
        WHERE year IN (2021, 2022, 2023, 2024) AND value IS NOT NULL
    """)[0]
    if n == 136:
        ok(f"2021+2022+2023+2024 real 总量 = 136 不变 (mart stable: 前刀 real 不被本刀覆盖)")
    else:
        fail(f"2021-2024 real 总量 = {n}, expected 136")

    # 24. lineage_ruling K669a-2025 全 22 missing cells 含 '669a-2025' (含 SZ/NJ legit DATA_MISSING)
    n = q(cur, f"""
        SELECT COUNT(*) FROM {SCHEMA}.{TABLE}
        WHERE year = 2025 AND value IS NULL
          AND (missing_reason LIKE '%669a-2025%')
    """)[0]
    total_missing = q(cur, f"SELECT COUNT(*) FROM {SCHEMA}.{TABLE} WHERE year = 2025 AND value IS NULL")[0]
    if n == total_missing and n == 22:
        ok(f"2025 missing cells missing_reason 全 22/含 '669a-2025' (sub-knife attribution + SZ/NJ hongheiku absense)")
    else:
        fail(f"2025 missing cells missing_reason 含 '669a-2025' = {n}, total missing = {total_missing} (expected 22/22)")

    # 25. lineage_ruling K669a-2025-2026-09-07 唯一 (not in older cells)
    n = q(cur, f"""
        SELECT COUNT(DISTINCT lineage_ruling) FROM {SCHEMA}.{TABLE}
        WHERE lineage_ruling LIKE '%669a-2025%'
    """)[0]
    if n == 1:
        ok(f"lineage_ruling K669a-2025-* 唯一版本: K669a-2025-2026-09-07")
    else:
        fail(f"669a-2025 rulings 不唯一 = {n}")

    # 26. 2026 仍全 DATA_MISSING (守 2025 harvest 不溢出)
    n = q(cur, f"SELECT COUNT(*) FROM {SCHEMA}.{TABLE} WHERE year = 2026 AND value IS NOT NULL")[0]
    if n == 0:
        ok(f"2026 仍全 DATA_MISSING (守新增红线-2: 待 2027 官方发布)")
    else:
        fail(f"2026 real cells = {n}, expected 0")

    cur.close()
    conn.close()

    print()
    print(f"=== knife 669a-2025 红线 summary: {PASS}/{PASS+FAIL} PASS, {FAIL} FAIL ===")
    sys.exit(0 if FAIL == 0 else 1)


if __name__ == "__main__":
    main()