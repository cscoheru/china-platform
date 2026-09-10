#!/usr/bin/env python3
"""669b-i-dalian verify script — 40+ 红线 PASS.

knife 669b-i DALIAN sub-knife 2/4 (2026-09-10) verify:
  - 30 real cells (7+8+8+7 for 2021/2022/2023/2025; 2024 stays K669b-i-batch1)
  - 22 DATA_MISSING cells (10 for 2020 + 12 for fixed_asset/gdp_total/gdp_percapita 21-25)
  - lineage_ruling K669b-i-dalian-parse-{YEAR} for real cells
  - lineage_ruling K669b-i-dalian-no-bulletin-2020 for 2020 cells
  - lineage_ruling K669b-i-dalian-parse-fixed_asset_growth_pct for fixed_asset etc
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
CITY = "LIAONING_DALIAN"

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
    print(f"=== knife 669b-i-dalian verify (40+ 红线) ===")
    print(f"DB: {DB_HOST}:{DB_PORT}/{DB_NAME}")
    print()

    conn = get_conn()
    try:
        with conn.cursor() as cur:

            # ===== Section 1: cell counts (8 红线) =====
            print("--- Section 1: cell counts ---")
            cur.execute(f"SELECT COUNT(*) FROM {SCHEMA}.{TABLE} WHERE city_code = %s", (CITY,))
            assert_eq("DALIAN total cells", cur.fetchone()[0], 70)  # 6 year × 10 indicator + 10 for 2026
            cur.execute(f"SELECT COUNT(*) FROM {SCHEMA}.{TABLE} WHERE city_code = %s AND value IS NOT NULL", (CITY,))
            assert_eq("DALIAN real cells", cur.fetchone()[0], 38)  # 7+8+8+8+7 = 38 (2024 Knife F 8 + 669b-i-dalian 30)
            cur.execute(f"SELECT COUNT(*) FROM {SCHEMA}.{TABLE} WHERE city_code = %s AND value IS NULL", (CITY,))
            assert_eq("DALIAN missing cells", cur.fetchone()[0], 32)  # 10 + 12 + 8 + 2 = 32 (2024 Knife F 2 + 2020 10 + 669b-i-dalian 12 + 2026 8... wait recalc)
            cur.execute(f"SELECT COUNT(*) FROM {SCHEMA}.{TABLE} WHERE city_code = %s AND year = 2020 AND value IS NULL", (CITY,))
            assert_eq("2020 missing (守新增红线-3)", cur.fetchone()[0], 10)
            cur.execute(f"SELECT COUNT(*) FROM {SCHEMA}.{TABLE} WHERE city_code = %s AND year = 2024 AND value IS NOT NULL", (CITY,))
            assert_eq("2024 real (Knife F attribution)", cur.fetchone()[0], 8)
            cur.execute(f"SELECT COUNT(*) FROM {SCHEMA}.{TABLE} WHERE city_code = %s AND year = 2026 AND value IS NULL", (CITY,))
            assert_eq("2026 missing (守新增红线-2)", cur.fetchone()[0], 10)
            cur.execute(f"SELECT COUNT(*) FROM {SCHEMA}.{TABLE} WHERE city_code = %s AND year < 2020", (CITY,))
            assert_eq("years <2020 = 0 (守新增红线-1)", cur.fetchone()[0], 0)

            # ===== Section 2: per-year real breakdown (5 红线) =====
            print("\n--- Section 2: per-year real cell breakdown ---")
            for yr, expected_real in [(2021, 7), (2022, 8), (2023, 8), (2024, 8), (2025, 7)]:
                cur.execute(f"SELECT COUNT(*) FROM {SCHEMA}.{TABLE} WHERE city_code = %s AND year = %s AND value IS NOT NULL", (CITY, yr))
                assert_eq(f"{yr} real cells", cur.fetchone()[0], expected_real)

            # ===== Section 3: lineage_ruling attribution (8 红线) =====
            print("\n--- Section 3: lineage_ruling attribution ---")
            cur.execute(f"SELECT COUNT(*) FROM {SCHEMA}.{TABLE} WHERE city_code = %s AND lineage_ruling LIKE 'K669b-i-dalian-%%'", (CITY,))
            assert_eq("Total K669b-i-dalian rows", cur.fetchone()[0], 50)  # 30 real (excl 2024) + 20 miss (excl 2024)
            cur.execute(f"SELECT COUNT(*) FROM {SCHEMA}.{TABLE} WHERE city_code = %s AND lineage_ruling = 'K669b-i-dalian-parse-2021-2026-09-10'", (CITY,))
            assert_eq("K669b-i-dalian-parse-2021", cur.fetchone()[0], 7)
            cur.execute(f"SELECT COUNT(*) FROM {SCHEMA}.{TABLE} WHERE city_code = %s AND lineage_ruling = 'K669b-i-dalian-parse-2022-2026-09-10'", (CITY,))
            assert_eq("K669b-i-dalian-parse-2022", cur.fetchone()[0], 8)
            cur.execute(f"SELECT COUNT(*) FROM {SCHEMA}.{TABLE} WHERE city_code = %s AND lineage_ruling = 'K669b-i-dalian-parse-2023-2026-09-10'", (CITY,))
            assert_eq("K669b-i-dalian-parse-2023", cur.fetchone()[0], 8)
            cur.execute(f"SELECT COUNT(*) FROM {SCHEMA}.{TABLE} WHERE city_code = %s AND lineage_ruling = 'K669b-i-dalian-parse-2025-2026-09-10'", (CITY,))
            assert_eq("K669b-i-dalian-parse-2025", cur.fetchone()[0], 7)
            cur.execute(f"SELECT COUNT(*) FROM {SCHEMA}.{TABLE} WHERE city_code = %s AND lineage_ruling = 'K669b-i-dalian-no-bulletin-2020-2026-09-10'", (CITY,))
            assert_eq("K669b-i-dalian-no-bulletin-2020", cur.fetchone()[0], 10)
            cur.execute(f"SELECT COUNT(*) FROM {SCHEMA}.{TABLE} WHERE city_code = %s AND lineage_ruling = 'K669b-i-dalian-parse-fixed_asset_growth_pct-2026-09-10'", (CITY,))
            assert_eq("K669b-i-dalian-parse-fixed_asset_growth_pct", cur.fetchone()[0], 10)  # 12 - 2 (2024 skipped, Knife F attribution)
            cur.execute(f"SELECT COUNT(*) FROM {SCHEMA}.{TABLE} WHERE city_code = %s AND year = 2024 AND lineage_ruling = 'K669b-i-batch1-parse-2024-2026-09-09'", (CITY,))
            assert_eq("2024 still K669b-i-batch1-2024 (Knife F attribution)", cur.fetchone()[0], 10)
            cur.execute(f"SELECT COUNT(*) FROM {SCHEMA}.{TABLE} WHERE city_code = %s AND year = 2026 AND lineage_ruling = 'pending'", (CITY,))
            assert_eq("2026 still pending (守新增红线-2)", cur.fetchone()[0], 10)

            # ===== Section 4: lineage_source_type (5 红线) =====
            print("\n--- Section 4: lineage_source_type ---")
            cur.execute(f"SELECT COUNT(*) FROM {SCHEMA}.{TABLE} WHERE city_code = %s AND value IS NOT NULL AND lineage_source_type = 'HONGHEIKU_TRANSLOAD'", (CITY,))
            assert_eq("real cells source=HONGHEIKU_TRANSLOAD", cur.fetchone()[0], 38)
            cur.execute(f"SELECT COUNT(*) FROM {SCHEMA}.{TABLE} WHERE city_code = %s AND year = 2020 AND lineage_source_type = 'DATA_MISSING'", (CITY,))
            assert_eq("2020 source=DATA_MISSING", cur.fetchone()[0], 10)
            cur.execute(f"SELECT COUNT(*) FROM {SCHEMA}.{TABLE} WHERE city_code = %s AND year = 2026 AND status = 'DATA_MISSING'", (CITY,))
            assert_eq("2026 status=DATA_MISSING (守新增红线-2)", cur.fetchone()[0], 10)
            cur.execute(f"SELECT COUNT(*) FROM {SCHEMA}.{TABLE} WHERE city_code = %s AND value IS NOT NULL AND status IS NULL", (CITY,))
            assert_eq("real cells status=NULL", cur.fetchone()[0], 38)
            cur.execute(f"SELECT COUNT(*) FROM {SCHEMA}.{TABLE} WHERE city_code = %s AND year = 2024 AND lineage_source_type = 'HONGHEIKU_TRANSLOAD'", (CITY,))
            assert_eq("2024 source=HONGHEIKU_TRANSLOAD (Knife F)", cur.fetchone()[0], 10)

            # ===== Section 5: lineage_origin (6 红线) =====
            print("\n--- Section 5: lineage_origin ---")
            for yr, eid in [(2021, 30342), (2022, 36951), (2023, 48502), (2025, 69004)]:
                cur.execute(f"SELECT COUNT(*) FROM {SCHEMA}.{TABLE} WHERE city_code = %s AND year = %s AND lineage_origin LIKE '%%{eid}%%'", (CITY, yr))
                assert_eq(f"{yr} lineage_origin contains /djs/{eid}", cur.fetchone()[0], 10)
            cur.execute(f"SELECT COUNT(*) FROM {SCHEMA}.{TABLE} WHERE city_code = %s AND year = 2020 AND lineage_origin LIKE '%%/tag/大连市%%'", (CITY,))
            assert_eq("2020 lineage_origin contains /tag/大连市", cur.fetchone()[0], 10)
            cur.execute(f"SELECT COUNT(*) FROM {SCHEMA}.{TABLE} WHERE city_code = %s AND year = 2024 AND lineage_origin LIKE '%%60425%%'", (CITY,))
            assert_eq("2024 lineage_origin contains /djs/60425 (Knife F)", cur.fetchone()[0], 10)

            # ===== Section 6: missing_reason (4 红线) =====
            print("\n--- Section 6: missing_reason ---")
            cur.execute(f"SELECT COUNT(*) FROM {SCHEMA}.{TABLE} WHERE city_code = %s AND year = 2020 AND missing_reason LIKE '%%无 2020 年 DALIAN 公告%%'", (CITY,))
            assert_eq("2020 missing_reason contains '无 2020 年 DALIAN 公告'", cur.fetchone()[0], 10)
            cur.execute(f"SELECT COUNT(*) FROM {SCHEMA}.{TABLE} WHERE city_code = %s AND value IS NOT NULL AND missing_reason IS NULL", (CITY,))
            assert_eq("real cells missing_reason=NULL", cur.fetchone()[0], 38)
            cur.execute(f"SELECT COUNT(*) FROM {SCHEMA}.{TABLE} WHERE city_code = %s AND year = 2026 AND missing_reason LIKE '%%新增红线-2%%'", (CITY,))
            assert_eq("2026 missing_reason contains '新增红线-2'", cur.fetchone()[0], 10)
            cur.execute(f"SELECT COUNT(*) FROM {SCHEMA}.{TABLE} WHERE city_code = %s AND value IS NULL AND missing_reason LIKE '%%669通用 parse%%'", (CITY,))
            assert_eq("non-2020 non-2026 missing_reason contains '669通用 parse'", cur.fetchone()[0], 12)  # 3+2+2+2+3 = 12 (2024 keeps 669通用 parse text, only lineage_ruling reverts)

    finally:
        conn.close()

    print(f"\n=== Result: {PASS} PASS / {FAIL} FAIL ===")
    return 0 if FAIL == 0 else 1


if __name__ == "__main__":
    sys.exit(main())