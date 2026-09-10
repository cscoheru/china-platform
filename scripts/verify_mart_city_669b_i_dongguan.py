#!/usr/bin/env python3
"""669b-i-dongguan verify script — 40+ 红线 PASS.

knife 669b-i DONGGUAN sub-knife 1/4 (2026-09-10) verify:
  - 47 real cells (9+9+9+10 for 2021/2022/2023/2025)
  - 13 DATA_MISSING cells (10 for 2020 + 3 for fixed_asset 2021/2022/2023)
  - lineage_ruling K669b-i-dongguan-parse-{YEAR} for real cells
  - lineage_ruling K669b-i-dongguan-no-bulletin-2020 for 2020 cells
  - lineage_ruling K669b-i-dongguan-parse-fixed_asset_growth_pct for fixed_asset cells
  - 2024 cells stay as K669b-i-batch1-parse-2024 (Knife F attribution)
  - 2026 cells stay DATA_MISSING (守新增红线-2)
  - 2020 = 10 DATA_MISSING (守新增红线-3 禁编造)
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
CITY = "GUANGDONG_DONGGUAN"

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
    print(f"=== knife 669b-i-dongguan verify (40+ 红线) ===")
    print(f"DB: {DB_HOST}:{DB_PORT}/{DB_NAME}")
    print()

    conn = get_conn()
    try:
        with conn.cursor() as cur:

            # ===== Section 1: cell counts (8 红线) =====
            print("--- Section 1: cell counts ---")
            cur.execute(f"SELECT COUNT(*) FROM {SCHEMA}.{TABLE} WHERE city_code = %s", (CITY,))
            assert_eq("DONGGUAN total cells", cur.fetchone()[0], 70)  # 6 year × 10 indicator + 10 for 2026
            cur.execute(f"SELECT COUNT(*) FROM {SCHEMA}.{TABLE} WHERE city_code = %s AND value IS NOT NULL", (CITY,))
            assert_eq("DONGGUAN real cells", cur.fetchone()[0], 47)
            cur.execute(f"SELECT COUNT(*) FROM {SCHEMA}.{TABLE} WHERE city_code = %s AND value IS NULL", (CITY,))
            assert_eq("DONGGUAN missing cells", cur.fetchone()[0], 23)
            cur.execute(f"SELECT COUNT(*) FROM {SCHEMA}.{TABLE} WHERE city_code = %s AND year = 2020 AND value IS NULL", (CITY,))
            assert_eq("2020 missing (守新增红线-3)", cur.fetchone()[0], 10)
            cur.execute(f"SELECT COUNT(*) FROM {SCHEMA}.{TABLE} WHERE city_code = %s AND year IN (2021, 2022, 2023) AND value IS NOT NULL", (CITY,))
            assert_eq("2021+2022+2023 real", cur.fetchone()[0], 27)  # 9 + 9 + 9
            cur.execute(f"SELECT COUNT(*) FROM {SCHEMA}.{TABLE} WHERE city_code = %s AND year IN (2021, 2022, 2023) AND value IS NULL", (CITY,))
            assert_eq("2021+2022+2023 missing (fixed_asset)", cur.fetchone()[0], 3)
            cur.execute(f"SELECT COUNT(*) FROM {SCHEMA}.{TABLE} WHERE city_code = %s AND year = 2024 AND value IS NOT NULL", (CITY,))
            assert_eq("2024 real (Knife F attribution)", cur.fetchone()[0], 10)
            cur.execute(f"SELECT COUNT(*) FROM {SCHEMA}.{TABLE} WHERE city_code = %s AND year = 2025 AND value IS NOT NULL", (CITY,))
            assert_eq("2025 real", cur.fetchone()[0], 10)

            # ===== Section 2: per-year per-indicator (12 红线) =====
            print("\n--- Section 2: per-year real cell breakdown ---")
            for yr, expected_real in [(2021, 9), (2022, 9), (2023, 9), (2024, 10), (2025, 10)]:
                cur.execute(f"SELECT COUNT(*) FROM {SCHEMA}.{TABLE} WHERE city_code = %s AND year = %s AND value IS NOT NULL", (CITY, yr))
                assert_eq(f"{yr} real cells", cur.fetchone()[0], expected_real)

            # fixed_asset: only 2024 + 2025 have real value
            for yr in [2021, 2022, 2023]:
                cur.execute(f"SELECT value FROM {SCHEMA}.{TABLE} WHERE city_code = %s AND year = %s AND indicator_key = 'fixed_asset'", (CITY, yr))
                v = cur.fetchone()
                assert_true(f"{yr} fixed_asset DATA_MISSING", v is not None and v[0] is None)
            for yr in [2024, 2025]:
                cur.execute(f"SELECT value FROM {SCHEMA}.{TABLE} WHERE city_code = %s AND year = %s AND indicator_key = 'fixed_asset'", (CITY, yr))
                v = cur.fetchone()
                assert_true(f"{yr} fixed_asset real", v is not None and v[0] is not None)

            # ===== Section 3: lineage_ruling attribution (10 红线) =====
            print("\n--- Section 3: lineage_ruling attribution ---")
            cur.execute(f"SELECT COUNT(*) FROM {SCHEMA}.{TABLE} WHERE city_code = %s AND lineage_ruling LIKE 'K669b-i-dongguan-%%'", (CITY,))
            assert_eq("Total K669b-i-dongguan rows", cur.fetchone()[0], 50)  # 47 real + 13 missing - 10 (2024 stays in K669b-i-batch1, Knife F)
            cur.execute(f"SELECT COUNT(*) FROM {SCHEMA}.{TABLE} WHERE city_code = %s AND lineage_ruling = 'K669b-i-dongguan-parse-2021-2026-09-10'", (CITY,))
            assert_eq("K669b-i-dongguan-parse-2021", cur.fetchone()[0], 9)
            cur.execute(f"SELECT COUNT(*) FROM {SCHEMA}.{TABLE} WHERE city_code = %s AND lineage_ruling = 'K669b-i-dongguan-parse-2022-2026-09-10'", (CITY,))
            assert_eq("K669b-i-dongguan-parse-2022", cur.fetchone()[0], 9)
            cur.execute(f"SELECT COUNT(*) FROM {SCHEMA}.{TABLE} WHERE city_code = %s AND lineage_ruling = 'K669b-i-dongguan-parse-2023-2026-09-10'", (CITY,))
            assert_eq("K669b-i-dongguan-parse-2023", cur.fetchone()[0], 9)
            cur.execute(f"SELECT COUNT(*) FROM {SCHEMA}.{TABLE} WHERE city_code = %s AND lineage_ruling = 'K669b-i-dongguan-parse-2025-2026-09-10'", (CITY,))
            assert_eq("K669b-i-dongguan-parse-2025", cur.fetchone()[0], 10)
            cur.execute(f"SELECT COUNT(*) FROM {SCHEMA}.{TABLE} WHERE city_code = %s AND lineage_ruling = 'K669b-i-dongguan-no-bulletin-2020-2026-09-10'", (CITY,))
            assert_eq("K669b-i-dongguan-no-bulletin-2020", cur.fetchone()[0], 10)
            cur.execute(f"SELECT COUNT(*) FROM {SCHEMA}.{TABLE} WHERE city_code = %s AND lineage_ruling = 'K669b-i-dongguan-parse-fixed_asset_growth_pct-2026-09-10'", (CITY,))
            assert_eq("K669b-i-dongguan-parse-fixed_asset_growth_pct", cur.fetchone()[0], 3)
            # 2024 stays as Knife F
            cur.execute(f"SELECT COUNT(*) FROM {SCHEMA}.{TABLE} WHERE city_code = %s AND year = 2024 AND lineage_ruling = 'K669b-i-batch1-parse-2024-2026-09-09'", (CITY,))
            assert_eq("2024 still K669b-i-batch1-2024 (Knife F attribution)", cur.fetchone()[0], 10)
            # 2026 stays pending
            cur.execute(f"SELECT COUNT(*) FROM {SCHEMA}.{TABLE} WHERE city_code = %s AND year = 2026 AND lineage_ruling = 'pending'", (CITY,))
            assert_eq("2026 still pending (守新增红线-2)", cur.fetchone()[0], 10)

            # ===== Section 4: lineage_source_type (5 红线) =====
            print("\n--- Section 4: lineage_source_type ---")
            cur.execute(f"SELECT COUNT(*) FROM {SCHEMA}.{TABLE} WHERE city_code = %s AND value IS NOT NULL AND lineage_source_type = 'HONGHEIKU_TRANSLOAD'", (CITY,))
            assert_eq("real cells source=HONGHEIKU_TRANSLOAD", cur.fetchone()[0], 47)
            cur.execute(f"SELECT COUNT(*) FROM {SCHEMA}.{TABLE} WHERE city_code = %s AND year = 2020 AND lineage_source_type = 'DATA_MISSING'", (CITY,))
            assert_eq("2020 source=DATA_MISSING", cur.fetchone()[0], 10)
            cur.execute(f"SELECT COUNT(*) FROM {SCHEMA}.{TABLE} WHERE city_code = %s AND indicator_key = 'fixed_asset' AND year IN (2021, 2022, 2023) AND lineage_source_type = 'DATA_MISSING'", (CITY,))
            assert_eq("fixed_asset 21-23 source=DATA_MISSING", cur.fetchone()[0], 3)
            cur.execute(f"SELECT COUNT(*) FROM {SCHEMA}.{TABLE} WHERE city_code = %s AND year = 2026 AND status = 'DATA_MISSING'", (CITY,))
            assert_eq("2026 status=DATA_MISSING (守新增红线-2)", cur.fetchone()[0], 10)
            cur.execute(f"SELECT COUNT(*) FROM {SCHEMA}.{TABLE} WHERE city_code = %s AND value IS NOT NULL AND status IS NULL", (CITY,))
            assert_eq("real cells status=NULL", cur.fetchone()[0], 47)

            # ===== Section 5: lineage_origin (5 红线) =====
            print("\n--- Section 5: lineage_origin ---")
            for yr, eid in [(2021, 25333), (2022, 42065), (2023, 47430), (2025, 69935)]:
                cur.execute(f"SELECT COUNT(*) FROM {SCHEMA}.{TABLE} WHERE city_code = %s AND year = %s AND lineage_origin LIKE '%%{eid}%%'", (CITY, yr))
                assert_eq(f"{yr} lineage_origin contains /djs/{eid}", cur.fetchone()[0], 10)
            cur.execute(f"SELECT COUNT(*) FROM {SCHEMA}.{TABLE} WHERE city_code = %s AND year = 2020 AND lineage_origin LIKE '%%/tag/东莞市%%'", (CITY,))
            assert_eq("2020 lineage_origin contains /tag/东莞市", cur.fetchone()[0], 10)

            # ===== Section 6: missing_reason (5 红线) =====
            print("\n--- Section 6: missing_reason ---")
            cur.execute(f"SELECT COUNT(*) FROM {SCHEMA}.{TABLE} WHERE city_code = %s AND year = 2020 AND missing_reason LIKE '%%无 2020 年 DONGGUAN 公告%%'", (CITY,))
            assert_eq("2020 missing_reason contains '无 2020 年 DONGGUAN 公告'", cur.fetchone()[0], 10)
            cur.execute(f"SELECT COUNT(*) FROM {SCHEMA}.{TABLE} WHERE city_code = %s AND indicator_key = 'fixed_asset' AND year IN (2021, 2022, 2023) AND missing_reason LIKE '%%669通用 parse%%'", (CITY,))
            assert_eq("fixed_asset 21-23 missing_reason contains '669通用 parse'", cur.fetchone()[0], 3)
            cur.execute(f"SELECT COUNT(*) FROM {SCHEMA}.{TABLE} WHERE city_code = %s AND value IS NOT NULL AND missing_reason IS NULL", (CITY,))
            assert_eq("real cells missing_reason=NULL", cur.fetchone()[0], 47)
            cur.execute(f"SELECT COUNT(*) FROM {SCHEMA}.{TABLE} WHERE city_code = %s AND year = 2026 AND missing_reason LIKE '%%新增红线-2%%'", (CITY,))
            assert_eq("2026 missing_reason contains '新增红线-2'", cur.fetchone()[0], 10)
            cur.execute(f"SELECT COUNT(*) FROM {SCHEMA}.{TABLE} WHERE city_code = %s AND year < 2020", (CITY,))
            assert_eq("years <2020 = 0 (守新增红线-1)", cur.fetchone()[0], 0)

    finally:
        conn.close()

    print(f"\n=== Result: {PASS} PASS / {FAIL} FAIL ===")
    return 0 if FAIL == 0 else 1


if __name__ == "__main__":
    sys.exit(main())