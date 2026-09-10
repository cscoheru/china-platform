#!/usr/bin/env python3
"""669b-i-wuxi verify script — 36+ 红线 PASS.

knife 669b-i WUXI sub-knife 3/4 (2026-09-10) verify:
  - 26 real cells (8+9+9 for 2021/2023/2025; 2024 stays in rd13 Knife F attribution)
  - 34 DATA_MISSING cells (10 for 2020 + 10 for 2022 + 4 for gdp_percapita/fiscal_rev + 10 for 2026)
  - lineage_ruling K669b-i-wuxi-parse-{YEAR} for real cells
  - lineage_ruling K669b-i-wuxi-no-bulletin-djs-2020 for 2020 cells
  - lineage_ruling K669b-i-wuxi-no-bulletin-2022 for 2022 cells
  - lineage_ruling K669b-i-wuxi-parse-fixed_asset_growth_pct for gdp_percapita/fiscal_rev cells
  - 2024 cells stay as K669b-i-batch1-parse-2024 (Knife F attribution)
  - 2026 cells stay DATA_MISSING (守新增红线-2)
  - 2020 = 10 DATA_MISSING (老 ID /1707.html, 守新增红线-3 禁编造)
  - 2022 = 10 DATA_MISSING (hongheiku tag 页无 /djs/{eid}.html, 守新增红线-3)
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
CITY = "JIANGSU_WUXI"

PASS = 0
FAIL = 0


def get_conn():
    return psycopg2.connect(host=DB_HOST, port=DB_PORT, user=DB_USER,
                            password=DB_PASS, dbname=DB_NAME)


def assert_eq(label: str, got, expected) -> None:
    global PASS, FAIL
    if got == expected:
        PASS += 1
        print(f"  ✓ {label}: {got}")
    else:
        FAIL += 1
        print(f"  ✗ {label}: got {got!r}, expected {expected!r}")


def assert_true(label: str, cond, detail: str = "") -> None:
    global PASS, FAIL
    if cond:
        PASS += 1
        print(f"  ✓ {label}{(' — ' + detail) if detail else ''}")
    else:
        FAIL += 1
        print(f"  ✗ {label}{(' — ' + detail) if detail else ''}")


def main() -> int:
    print(f"=== knife 669b-i-wuxi verify (36+ 红线) ===")
    print(f"DB: {DB_HOST}:{DB_PORT}/{DB_NAME}")
    print()

    conn = get_conn()
    try:
        with conn.cursor() as cur:

            # ===== Section 1: cell counts (7 红线) =====
            print("--- Section 1: cell counts ---")
            cur.execute(f"SELECT COUNT(*) FROM {SCHEMA}.{TABLE} WHERE city_code = %s", (CITY,))
            assert_eq("WUXI total cells", cur.fetchone()[0], 70)  # 7 year × 10 indicator = 70
            cur.execute(f"SELECT COUNT(*) FROM {SCHEMA}.{TABLE} WHERE city_code = %s AND value IS NOT NULL", (CITY,))
            assert_eq("WUXI real cells", cur.fetchone()[0], 35)  # 8+9+9+9 = 35 (2024 Knife F 9 + 669b-i-wuxi 26)
            cur.execute(f"SELECT COUNT(*) FROM {SCHEMA}.{TABLE} WHERE city_code = %s AND value IS NULL", (CITY,))
            assert_eq("WUXI missing cells", cur.fetchone()[0], 35)  # 10 + 2 + 10 + 1 + 1 + 1 + 10 = 35
            cur.execute(f"SELECT COUNT(*) FROM {SCHEMA}.{TABLE} WHERE city_code = %s AND year = 2020 AND value IS NULL", (CITY,))
            assert_eq("2020 missing (老 ID /1707.html, 守新增红线-3)", cur.fetchone()[0], 10)
            cur.execute(f"SELECT COUNT(*) FROM {SCHEMA}.{TABLE} WHERE city_code = %s AND year = 2024 AND value IS NOT NULL", (CITY,))
            assert_eq("2024 real (Knife F attribution)", cur.fetchone()[0], 9)
            cur.execute(f"SELECT COUNT(*) FROM {SCHEMA}.{TABLE} WHERE city_code = %s AND year = 2026 AND value IS NULL", (CITY,))
            assert_eq("2026 missing (守新增红线-2)", cur.fetchone()[0], 10)
            cur.execute(f"SELECT COUNT(*) FROM {SCHEMA}.{TABLE} WHERE city_code = %s AND year < 2020", (CITY,))
            assert_eq("years <2020 = 0 (守新增红线-1)", cur.fetchone()[0], 0)

            # ===== Section 2: per-year real breakdown (5 红线) =====
            print("\n--- Section 2: per-year real cell breakdown ---")
            for yr, expected_real in [(2021, 8), (2022, 0), (2023, 9), (2024, 9), (2025, 9)]:
                cur.execute(f"SELECT COUNT(*) FROM {SCHEMA}.{TABLE} WHERE city_code = %s AND year = %s AND value IS NOT NULL", (CITY, yr))
                assert_eq(f"{yr} real cells", cur.fetchone()[0], expected_real)

            # ===== Section 3: lineage_ruling attribution (10 红线) =====
            print("\n--- Section 3: lineage_ruling attribution ---")
            cur.execute(f"SELECT COUNT(*) FROM {SCHEMA}.{TABLE} WHERE city_code = %s AND lineage_ruling LIKE 'K669b-i-wuxi-%%'", (CITY,))
            assert_eq("Total K669b-i-wuxi rows", cur.fetchone()[0], 50)  # 26 real (excl 2024) + 24 miss (excl 2024)
            cur.execute(f"SELECT COUNT(*) FROM {SCHEMA}.{TABLE} WHERE city_code = %s AND lineage_ruling = 'K669b-i-wuxi-parse-2021-2026-09-10'", (CITY,))
            assert_eq("K669b-i-wuxi-parse-2021", cur.fetchone()[0], 8)
            cur.execute(f"SELECT COUNT(*) FROM {SCHEMA}.{TABLE} WHERE city_code = %s AND lineage_ruling = 'K669b-i-wuxi-parse-2023-2026-09-10'", (CITY,))
            assert_eq("K669b-i-wuxi-parse-2023", cur.fetchone()[0], 9)
            cur.execute(f"SELECT COUNT(*) FROM {SCHEMA}.{TABLE} WHERE city_code = %s AND lineage_ruling = 'K669b-i-wuxi-parse-2025-2026-09-10'", (CITY,))
            assert_eq("K669b-i-wuxi-parse-2025", cur.fetchone()[0], 9)
            cur.execute(f"SELECT COUNT(*) FROM {SCHEMA}.{TABLE} WHERE city_code = %s AND lineage_ruling = 'K669b-i-wuxi-no-bulletin-djs-2020-2026-09-10'", (CITY,))
            assert_eq("K669b-i-wuxi-no-bulletin-djs-2020", cur.fetchone()[0], 10)
            cur.execute(f"SELECT COUNT(*) FROM {SCHEMA}.{TABLE} WHERE city_code = %s AND lineage_ruling = 'K669b-i-wuxi-no-bulletin-2022-2026-09-10'", (CITY,))
            assert_eq("K669b-i-wuxi-no-bulletin-2022", cur.fetchone()[0], 10)
            cur.execute(f"SELECT COUNT(*) FROM {SCHEMA}.{TABLE} WHERE city_code = %s AND lineage_ruling = 'K669b-i-wuxi-parse-fixed_asset_growth_pct-2026-09-10'", (CITY,))
            assert_eq("K669b-i-wuxi-parse-fixed_asset_growth_pct", cur.fetchone()[0], 4)  # 3 gdp_percapita + 1 fiscal_rev
            cur.execute(f"SELECT COUNT(*) FROM {SCHEMA}.{TABLE} WHERE city_code = %s AND year = 2024 AND lineage_ruling = 'K669b-i-batch1-parse-2024-2026-09-09'", (CITY,))
            assert_eq("2024 still K669b-i-batch1-2024 (Knife F attribution)", cur.fetchone()[0], 10)
            cur.execute(f"SELECT COUNT(*) FROM {SCHEMA}.{TABLE} WHERE city_code = %s AND year = 2026 AND lineage_ruling = 'pending'", (CITY,))
            assert_eq("2026 still pending (守新增红线-2)", cur.fetchone()[0], 10)

            # ===== Section 4: lineage_source_type (5 红线) =====
            print("\n--- Section 4: lineage_source_type ---")
            cur.execute(f"SELECT COUNT(*) FROM {SCHEMA}.{TABLE} WHERE city_code = %s AND value IS NOT NULL AND lineage_source_type = 'HONGHEIKU_TRANSLOAD'", (CITY,))
            assert_eq("real cells source=HONGHEIKU_TRANSLOAD", cur.fetchone()[0], 35)
            cur.execute(f"SELECT COUNT(*) FROM {SCHEMA}.{TABLE} WHERE city_code = %s AND year IN (2020, 2022) AND lineage_source_type = 'DATA_MISSING'", (CITY,))
            assert_eq("2020+2022 source=DATA_MISSING", cur.fetchone()[0], 20)
            cur.execute(f"SELECT COUNT(*) FROM {SCHEMA}.{TABLE} WHERE city_code = %s AND year = 2026 AND status = 'DATA_MISSING'", (CITY,))
            assert_eq("2026 status=DATA_MISSING (守新增红线-2)", cur.fetchone()[0], 10)
            cur.execute(f"SELECT COUNT(*) FROM {SCHEMA}.{TABLE} WHERE city_code = %s AND value IS NOT NULL AND status IS NULL", (CITY,))
            assert_eq("real cells status=NULL", cur.fetchone()[0], 35)
            cur.execute(f"SELECT COUNT(*) FROM {SCHEMA}.{TABLE} WHERE city_code = %s AND year = 2024 AND value IS NOT NULL AND lineage_source_type = 'HONGHEIKU_TRANSLOAD'", (CITY,))
            assert_eq("2024 real source=HONGHEIKU_TRANSLOAD (Knife F)", cur.fetchone()[0], 9)

            # ===== Section 5: lineage_origin (6 红线) =====
            print("\n--- Section 5: lineage_origin ---")
            for yr, eid in [(2021, 23931), (2023, 45593), (2025, 70051)]:
                cur.execute(f"SELECT COUNT(*) FROM {SCHEMA}.{TABLE} WHERE city_code = %s AND year = %s AND lineage_origin LIKE '%%{eid}%%'", (CITY, yr))
                assert_eq(f"{yr} lineage_origin contains /djs/{eid}", cur.fetchone()[0], 10)
            cur.execute(f"SELECT COUNT(*) FROM {SCHEMA}.{TABLE} WHERE city_code = %s AND year = 2020 AND lineage_origin LIKE '%%1707.html%%'", (CITY,))
            assert_eq("2020 lineage_origin contains /1707.html (老 ID)", cur.fetchone()[0], 10)
            cur.execute(f"SELECT COUNT(*) FROM {SCHEMA}.{TABLE} WHERE city_code = %s AND year = 2022 AND lineage_origin LIKE '%%xjtjgb%%'", (CITY,))
            assert_eq("2022 lineage_origin contains /xjtjgb (非标准 path)", cur.fetchone()[0], 10)
            cur.execute(f"SELECT COUNT(*) FROM {SCHEMA}.{TABLE} WHERE city_code = %s AND year = 2024 AND lineage_origin LIKE '%%/tag/无锡市%%'", (CITY,))
            assert_eq("2024 lineage_origin contains /tag/无锡市 (Knife F)", cur.fetchone()[0], 10)

            # ===== Section 6: missing_reason (4 红线) =====
            print("\n--- Section 6: missing_reason ---")
            cur.execute(f"SELECT COUNT(*) FROM {SCHEMA}.{TABLE} WHERE city_code = %s AND year = 2020 AND missing_reason LIKE '%%1707.html%%'", (CITY,))
            assert_eq("2020 missing_reason contains '/1707.html'", cur.fetchone()[0], 10)
            cur.execute(f"SELECT COUNT(*) FROM {SCHEMA}.{TABLE} WHERE city_code = %s AND value IS NOT NULL AND missing_reason IS NULL", (CITY,))
            assert_eq("real cells missing_reason=NULL", cur.fetchone()[0], 35)
            cur.execute(f"SELECT COUNT(*) FROM {SCHEMA}.{TABLE} WHERE city_code = %s AND year = 2026 AND missing_reason LIKE '%%新增红线-2%%'", (CITY,))
            assert_eq("2026 missing_reason contains '新增红线-2'", cur.fetchone()[0], 10)
            cur.execute(f"SELECT COUNT(*) FROM {SCHEMA}.{TABLE} WHERE city_code = %s AND value IS NULL AND missing_reason LIKE '%%669通用 parse%%'", (CITY,))
            assert_eq("non-2020/2022/2026 missing_reason contains '669通用 parse'", cur.fetchone()[0], 4)  # 2 (2021) + 1 (2023) + 1 (2025) = 4

    finally:
        conn.close()

    print(f"\n=== Result: {PASS} PASS / {FAIL} FAIL ===")
    return 0 if FAIL == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
