#!/usr/bin/env python3
"""669b-i-qingdao verify script — 36+ 红线 PASS.

knife 669b-i QINGDAO sub-knife 1/5 (2026-09-12) verify:
  - 35 real cells (6+0+6+8+7+8+0 for 2020/2021/2022/2023/2024/2025/2026; 2021 bulletin sparse all MISSING)
  - 35 DATA_MISSING cells (4+10+4+2+3+2+10 for the same years)
  - lineage_ruling K669b-i-qingdao-parse-{YEAR} for 2020-2025 cells
  - 2026 cells stay DATA_MISSING with lineage_ruling='pending' (守新增红线-2)
  - QINGDAO NOT in Knife F batch1 (DONGGUAN/DALIAN/WUXI/SUZHOU/XIAMEN), 2024 fresh this knife
  - 2001-2019 all DATA_MISSING (守新增红线-1)
  - QINGDAO city code 'SHANDONG_QINGDAO' (非 4 直辖市, 守新增红线-7)
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
CITY = "SHANDONG_QINGDAO"

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
    print(f"=== knife 669b-i-qingdao verify (36+ 红线) ===")
    print(f"DB: {DB_HOST}:{DB_PORT}/{DB_NAME}")
    print()

    conn = get_conn()
    try:
        with conn.cursor() as cur:

            # ===== Section 1: cell counts (7 红线) =====
            print("--- Section 1: cell counts ---")
            cur.execute(f"SELECT COUNT(*) FROM {SCHEMA}.{TABLE} WHERE city_code = %s", (CITY,))
            assert_eq("QINGDAO total cells", cur.fetchone()[0], 70)  # 7 year × 10 indicator
            cur.execute(f"SELECT COUNT(*) FROM {SCHEMA}.{TABLE} WHERE city_code = %s AND value IS NOT NULL", (CITY,))
            assert_eq("QINGDAO real cells", cur.fetchone()[0], 35)  # 6+0+6+8+7+8 = 35
            cur.execute(f"SELECT COUNT(*) FROM {SCHEMA}.{TABLE} WHERE city_code = %s AND value IS NULL", (CITY,))
            assert_eq("QINGDAO missing cells", cur.fetchone()[0], 35)  # 4+10+4+2+3+2+10 = 35
            cur.execute(f"SELECT COUNT(*) FROM {SCHEMA}.{TABLE} WHERE city_code = %s AND year = 2021 AND value IS NULL", (CITY,))
            assert_eq("2021 missing (bulletin sparse, parser all miss)", cur.fetchone()[0], 10)
            cur.execute(f"SELECT COUNT(*) FROM {SCHEMA}.{TABLE} WHERE city_code = %s AND year = 2024 AND value IS NOT NULL", (CITY,))
            assert_eq("2024 real (QINGDO NOT in Knife F, fresh this knife)", cur.fetchone()[0], 7)
            cur.execute(f"SELECT COUNT(*) FROM {SCHEMA}.{TABLE} WHERE city_code = %s AND year = 2026 AND value IS NULL", (CITY,))
            assert_eq("2026 missing (守新增红线-2)", cur.fetchone()[0], 10)
            cur.execute(f"SELECT COUNT(*) FROM {SCHEMA}.{TABLE} WHERE city_code = %s AND year < 2020", (CITY,))
            assert_eq("years <2020 = 0 (守新增红线-1)", cur.fetchone()[0], 0)

            # ===== Section 2: per-year real breakdown (6 红线) =====
            print("\n--- Section 2: per-year real cell breakdown ---")
            for yr, expected_real in [(2020, 6), (2021, 0), (2022, 6), (2023, 8), (2024, 7), (2025, 8)]:
                cur.execute(f"SELECT COUNT(*) FROM {SCHEMA}.{TABLE} WHERE city_code = %s AND year = %s AND value IS NOT NULL", (CITY, yr))
                assert_eq(f"{yr} real cells", cur.fetchone()[0], expected_real)

            # ===== Section 3: lineage_ruling attribution (8 红线) =====
            print("\n--- Section 3: lineage_ruling attribution ---")
            cur.execute(f"SELECT COUNT(*) FROM {SCHEMA}.{TABLE} WHERE city_code = %s AND lineage_ruling LIKE 'K669b-i-qingdao-%%'", (CITY,))
            assert_eq("Total K669b-i-qingdao rows", cur.fetchone()[0], 60)  # 35 real + 25 miss (2020-2025; 2026 stays pending)
            cur.execute(f"SELECT COUNT(*) FROM {SCHEMA}.{TABLE} WHERE city_code = %s AND lineage_ruling = 'K669b-i-qingdao-parse-2020-2026-09-12'", (CITY,))
            assert_eq("K669b-i-qingdao-parse-2020", cur.fetchone()[0], 10)
            cur.execute(f"SELECT COUNT(*) FROM {SCHEMA}.{TABLE} WHERE city_code = %s AND lineage_ruling = 'K669b-i-qingdao-parse-2021-2026-09-12'", (CITY,))
            assert_eq("K669b-i-qingdao-parse-2021", cur.fetchone()[0], 10)
            cur.execute(f"SELECT COUNT(*) FROM {SCHEMA}.{TABLE} WHERE city_code = %s AND lineage_ruling = 'K669b-i-qingdao-parse-2022-2026-09-12'", (CITY,))
            assert_eq("K669b-i-qingdao-parse-2022", cur.fetchone()[0], 10)
            cur.execute(f"SELECT COUNT(*) FROM {SCHEMA}.{TABLE} WHERE city_code = %s AND lineage_ruling = 'K669b-i-qingdao-parse-2023-2026-09-12'", (CITY,))
            assert_eq("K669b-i-qingdao-parse-2023", cur.fetchone()[0], 10)
            cur.execute(f"SELECT COUNT(*) FROM {SCHEMA}.{TABLE} WHERE city_code = %s AND lineage_ruling = 'K669b-i-qingdao-parse-2024-2026-09-12'", (CITY,))
            assert_eq("K669b-i-qingdao-parse-2024", cur.fetchone()[0], 10)
            cur.execute(f"SELECT COUNT(*) FROM {SCHEMA}.{TABLE} WHERE city_code = %s AND lineage_ruling = 'K669b-i-qingdao-parse-2025-2026-09-12'", (CITY,))
            assert_eq("K669b-i-qingdao-parse-2025", cur.fetchone()[0], 10)
            cur.execute(f"SELECT COUNT(*) FROM {SCHEMA}.{TABLE} WHERE city_code = %s AND year = 2026 AND lineage_ruling = 'pending'", (CITY,))
            assert_eq("2026 still pending (守新增红线-2)", cur.fetchone()[0], 10)

            # ===== Section 4: lineage_source_type (5 红线) =====
            print("\n--- Section 4: lineage_source_type ---")
            cur.execute(f"SELECT COUNT(*) FROM {SCHEMA}.{TABLE} WHERE city_code = %s AND value IS NOT NULL AND lineage_source_type = 'HONGHEIKU_TRANSLOAD'", (CITY,))
            assert_eq("real cells source=HONGHEIKU_TRANSLOAD", cur.fetchone()[0], 35)
            cur.execute(f"SELECT COUNT(*) FROM {SCHEMA}.{TABLE} WHERE city_code = %s AND year IN (2020, 2021, 2022, 2023, 2024, 2025) AND status = 'DATA_MISSING'", (CITY,))
            assert_eq("2020-2025 DATA_MISSING (25 cells)", cur.fetchone()[0], 25)
            cur.execute(f"SELECT COUNT(*) FROM {SCHEMA}.{TABLE} WHERE city_code = %s AND year = 2026 AND status = 'DATA_MISSING'", (CITY,))
            assert_eq("2026 status=DATA_MISSING (守新增红线-2)", cur.fetchone()[0], 10)
            cur.execute(f"SELECT COUNT(*) FROM {SCHEMA}.{TABLE} WHERE city_code = %s AND value IS NOT NULL AND status IS NULL", (CITY,))
            assert_eq("real cells status=NULL", cur.fetchone()[0], 35)
            cur.execute(f"SELECT COUNT(*) FROM {SCHEMA}.{TABLE} WHERE city_code = %s AND year = 2024 AND value IS NOT NULL AND lineage_source_type = 'HONGHEIKU_TRANSLOAD'", (CITY,))
            assert_eq("2024 real source=HONGHEIKU_TRANSLOAD (QINGDO fresh)", cur.fetchone()[0], 7)

            # ===== Section 5: lineage_origin (8 红线) =====
            print("\n--- Section 5: lineage_origin ---")
            for yr, eid, suffix in [
                (2020, '1537', '/1537.html'),      # 老 ID URL
                (2021, '24614', '/djs/'),
                (2022, '36589', '/djs/'),
                (2023, '48448', '/djs/'),
                (2024, '58586', '/djs/'),
                (2025, '68442', '/xjtjgb/xj2020/'),
            ]:
                cur.execute(f"SELECT COUNT(*) FROM {SCHEMA}.{TABLE} WHERE city_code = %s AND year = %s AND lineage_origin LIKE '%%{eid}%%'", (CITY, yr))
                assert_eq(f"{yr} lineage_origin contains {eid}{suffix}", cur.fetchone()[0], 10)
            cur.execute(f"SELECT COUNT(*) FROM {SCHEMA}.{TABLE} WHERE city_code = %s AND year = 2020 AND lineage_origin LIKE '%%/1537.html%%'", (CITY,))
            assert_eq("2020 老 ID URL /1537.html", cur.fetchone()[0], 10)
            cur.execute(f"SELECT COUNT(*) FROM {SCHEMA}.{TABLE} WHERE city_code = %s AND year = 2025 AND lineage_origin LIKE '%%/xjtjgb/xj2020/%%'", (CITY,))
            assert_eq("2025 新 URL /xjtjgb/xj2020/", cur.fetchone()[0], 10)

            # ===== Section 6: missing_reason (4 红线) =====
            print("\n--- Section 6: missing_reason ---")
            cur.execute(f"SELECT COUNT(*) FROM {SCHEMA}.{TABLE} WHERE city_code = %s AND year = 2021 AND missing_reason LIKE '%%669通用 parse%%'", (CITY,))
            assert_eq("2021 missing_reason contains '669通用 parse'", cur.fetchone()[0], 10)
            cur.execute(f"SELECT COUNT(*) FROM {SCHEMA}.{TABLE} WHERE city_code = %s AND value IS NOT NULL AND missing_reason IS NULL", (CITY,))
            assert_eq("real cells missing_reason=NULL", cur.fetchone()[0], 35)
            cur.execute(f"SELECT COUNT(*) FROM {SCHEMA}.{TABLE} WHERE city_code = %s AND year = 2026 AND missing_reason LIKE '%%新增红线-2%%'", (CITY,))
            assert_eq("2026 missing_reason contains '新增红线-2'", cur.fetchone()[0], 10)
            cur.execute(f"SELECT COUNT(*) FROM {SCHEMA}.{TABLE} WHERE city_code = %s AND year IN (2020, 2022, 2023, 2024, 2025) AND missing_reason LIKE '%%669通用 parse%%'", (CITY,))
            assert_eq("non-2021/2026 missing_reason contains '669通用 parse'", cur.fetchone()[0], 15)  # 4+4+2+3+2 = 15

    finally:
        conn.close()

    print(f"\n=== Result: {PASS} PASS / {FAIL} FAIL ===")
    return 0 if FAIL == 0 else 1


if __name__ == "__main__":
    sys.exit(main())