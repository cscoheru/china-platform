#!/usr/bin/env python3
"""669b-i batch8 mart verify — 35+ 红线 PASS / FAIL."""
import os
import sys
import psycopg2

DB_HOST = "127.0.0.1"
DB_PORT = 55440
DB_USER = "postgres"
DB_PASS = os.environ.get("DBT_DEV_PASS", "postgres")
DB_NAME = "cegr_test"
TARGET_SCHEMA = "cegr_mart"
MART_NAME = "mart_city_timeseries"

CITIES = [
    "SHANDONG_WEIFANG",
    "SHANDONG_YANTAI",
    "SHANDONG_ZIBO",
    "SHANDONG_JINING",
    "SHANDONG_LINYI",
]

PASS = 0
FAIL = 0


def get_conn():
    return psycopg2.connect(host=DB_HOST, port=DB_PORT, user=DB_USER,
                            password=DB_PASS, dbname=DB_NAME)


def assert_eq(label, actual, expected):
    global PASS, FAIL
    if actual == expected:
        print(f"  ✓ {label}: {actual}")
        PASS += 1
    else:
        print(f"  ✗ {label}: got {actual}, expected {expected}")
        FAIL += 1


def assert_zero(label, actual):
    assert_eq(label, actual, 0)


def main():
    global PASS, FAIL
    print("=== knife 669b-i batch8 verify (35+ 红线) ===\n")

    conn = get_conn()
    try:
        with conn.cursor() as cur:
            city_list_str = ",".join(f"'{c}'" for c in CITIES)

            # Section 1: total batch8 cell counts
            print("--- Section 1: total batch8 cell counts (2020-2025) ---")
            cur.execute(f"""
                SELECT COUNT(*) FROM {TARGET_SCHEMA}.{MART_NAME}
                WHERE city_code IN ({city_list_str}) AND year BETWEEN 2020 AND 2025
                  AND lineage_ruling LIKE 'K669b-i-batch8-%%'
            """)
            assert_eq("5 city × 2020-2025 cells (30 city-years × 10 = 300, batch8-tagged)", cur.fetchone()[0], 300)

            cur.execute(f"""
                SELECT COUNT(*) FROM {TARGET_SCHEMA}.{MART_NAME}
                WHERE city_code IN ({city_list_str}) AND year BETWEEN 2020 AND 2025
                  AND lineage_ruling LIKE 'K669b-i-batch8-%%' AND value IS NOT NULL
            """)
            assert_eq("real cells (109, batch8-tagged)", cur.fetchone()[0], 109)

            cur.execute(f"""
                SELECT COUNT(*) FROM {TARGET_SCHEMA}.{MART_NAME}
                WHERE city_code IN ({city_list_str}) AND year BETWEEN 2020 AND 2025
                  AND lineage_ruling LIKE 'K669b-i-batch8-%%' AND status = 'DATA_MISSING'
            """)
            assert_eq("DATA_MISSING cells (191 = 300 - 109 real, batch8-tagged)", cur.fetchone()[0], 191)

            cur.execute(f"""
                SELECT COUNT(*) FROM {TARGET_SCHEMA}.{MART_NAME}
                WHERE city_code IN ({city_list_str}) AND year BETWEEN 2020 AND 2025
                  AND lineage_ruling LIKE 'K669b-i-batch8-%%'
            """)
            assert_eq("300 cells tagged K669b-i-batch8-* (matched seed)", cur.fetchone()[0], 300)

            cur.execute(f"""
                SELECT COUNT(*) FROM {TARGET_SCHEMA}.{MART_NAME}
                WHERE city_code IN ({city_list_str}) AND year BETWEEN 2020 AND 2025
                  AND lineage_ruling LIKE 'K669b-i-batch8-%%' AND value IS NOT NULL
                  AND (status IS NOT NULL OR missing_reason IS NOT NULL)
            """)
            assert_eq("Real cells: status=NULL, missing_reason=NULL", cur.fetchone()[0], 0)

            # Section 2: per-city real cell count
            print("\n--- Section 2: per-city real cell count ---")
            expected_per_city = {
                "SHANDONG_WEIFANG": 50,
                "SHANDONG_LINYI": 34,
                "SHANDONG_YANTAI": 11,
                "SHANDONG_ZIBO": 14,
                "SHANDONG_JINING": 0,
            }
            for city, expected in expected_per_city.items():
                cur.execute(f"""
                    SELECT COUNT(*) FROM {TARGET_SCHEMA}.{MART_NAME}
                    WHERE city_code = '{city}' AND year BETWEEN 2020 AND 2025
                      AND lineage_ruling LIKE 'K669b-i-batch8-%%' AND value IS NOT NULL
                """)
                assert_eq(f"{city} real cells (batch8-tagged)", cur.fetchone()[0], expected)

            # Section 3: lineage_ruling 6 year versions
            print("\n--- Section 3: lineage_ruling 6 year versions ---")
            for y in [2020, 2021, 2022, 2023, 2024, 2025]:
                cur.execute(f"""
                    SELECT COUNT(*) FROM {TARGET_SCHEMA}.{MART_NAME}
                    WHERE city_code IN ({city_list_str}) AND year = {y}
                      AND lineage_ruling LIKE 'K669b-i-batch8-%%'
                """)
                assert_eq(f"lineage_ruling K669b-i-batch8-parse-{y} (50 cells)", cur.fetchone()[0], 50)

            # Section 4: lineage_source_type
            print("\n--- Section 4: lineage_source_type (batch8-tagged) ---")
            cur.execute(f"""
                SELECT COUNT(*) FROM {TARGET_SCHEMA}.{MART_NAME}
                WHERE city_code IN ({city_list_str}) AND year BETWEEN 2020 AND 2025
                  AND lineage_ruling LIKE 'K669b-i-batch8-%%' AND value IS NOT NULL
                  AND lineage_source_type = 'HONGHEIKU_TRANSLOAD'
            """)
            assert_eq("real cells source_type=HONGHEIKU_TRANSLOAD (batch8-tagged)", cur.fetchone()[0], 109)

            cur.execute(f"""
                SELECT COUNT(*) FROM {TARGET_SCHEMA}.{MART_NAME}
                WHERE city_code IN ({city_list_str}) AND year BETWEEN 2020 AND 2025
                  AND lineage_ruling LIKE 'K669b-i-batch8-%%' AND status = 'DATA_MISSING'
                  AND lineage_source_type = 'DATA_MISSING'
            """)
            assert_eq("miss cells source_type=DATA_MISSING (batch8-tagged)", cur.fetchone()[0], 191)

            cur.execute(f"""
                SELECT COUNT(*) FROM {TARGET_SCHEMA}.{MART_NAME}
                WHERE city_code IN ({city_list_str}) AND year BETWEEN 2020 AND 2025
                  AND lineage_ruling LIKE 'K669b-i-batch8-%%' AND value IS NOT NULL
                  AND lineage_source_type != 'HONGHEIKU_TRANSLOAD'
            """)
            assert_eq("real cells NOT HONGHEIKU_TRANSLOAD = 0 (batch8-tagged)", cur.fetchone()[0], 0)

            cur.execute(f"""
                SELECT COUNT(*) FROM {TARGET_SCHEMA}.{MART_NAME}
                WHERE city_code IN ({city_list_str}) AND year BETWEEN 2020 AND 2025
                  AND lineage_ruling LIKE 'K669b-i-batch8-%%' AND status = 'DATA_MISSING'
                  AND (missing_reason IS NULL OR missing_reason = '')
            """)
            assert_eq("miss cells missing_reason 必填 = 0 missing (batch8-tagged)", cur.fetchone()[0], 0)

            # Section 5: lineage_origin per-year total
            print("\n--- Section 5: lineage_origin per-year total (batch8-tagged) ---")
            for y in [2020, 2021, 2022, 2023, 2024, 2025]:
                cur.execute(f"""
                    SELECT COUNT(*) FROM {TARGET_SCHEMA}.{MART_NAME}
                    WHERE city_code IN ({city_list_str}) AND year = {y}
                      AND lineage_ruling LIKE 'K669b-i-batch8-%%'
                      AND lineage_origin LIKE '%hongheiku%'
                """)
                assert_eq(f"{y} lineage_origin 含 hongheiku.com (50 cells, batch8-tagged)", cur.fetchone()[0], 50)

            # Section 6: JINING 全 miss (守红线-3, 禁补零)
            print("\n--- Section 6: SHANDONG_JINING 全 DATA_MISSING (守红线-3, 禁补零) ---")
            cur.execute(f"""
                SELECT COUNT(*) FROM {TARGET_SCHEMA}.{MART_NAME}
                WHERE city_code = 'SHANDONG_JINING' AND year BETWEEN 2020 AND 2025
                  AND lineage_ruling LIKE 'K669b-i-batch8-%%' AND value IS NOT NULL
            """)
            assert_eq("SHANDONG_JINING real cells (batch8-tagged, expect 0 — 禁补零)", cur.fetchone()[0], 0)

            # Section 7: cross product sanity
            print("\n--- Section 7: cross product sanity ---")
            cur.execute(f"""
                SELECT COUNT(DISTINCT city_code) FROM {TARGET_SCHEMA}.{MART_NAME}
                WHERE city_code IN ({city_list_str}) AND year BETWEEN 2020 AND 2025
                  AND lineage_ruling LIKE 'K669b-i-batch8-%%'
            """)
            assert_eq("5 city distinct (batch8-tagged)", cur.fetchone()[0], 5)

            cur.execute(f"""
                SELECT COUNT(DISTINCT indicator_key) FROM {TARGET_SCHEMA}.{MART_NAME}
                WHERE city_code IN ({city_list_str}) AND year BETWEEN 2020 AND 2025
                  AND lineage_ruling LIKE 'K669b-i-batch8-%%'
            """)
            assert_eq("10 indicator distinct (batch8-tagged)", cur.fetchone()[0], 10)

            cur.execute(f"""
                SELECT COUNT(DISTINCT year) FROM {TARGET_SCHEMA}.{MART_NAME}
                WHERE city_code IN ({city_list_str}) AND year BETWEEN 2020 AND 2025
                  AND lineage_ruling LIKE 'K669b-i-batch8-%%'
            """)
            assert_eq("6 year distinct (2020-2025, batch8-tagged)", cur.fetchone()[0], 6)

            # Section 8: red lines
            print("\n--- Section 8: red lines ---")
            cur.execute(f"""
                SELECT COUNT(*) FROM {TARGET_SCHEMA}.{MART_NAME}
                WHERE city_code IN ({city_list_str}) AND year BETWEEN 2020 AND 2025
                  AND lineage_ruling LIKE 'K669b-i-batch8-%%'
                  AND city_code IN ('BEIJING_BEIJING','SHANGHAI_SHANGHAI','TIANJING_TIANJIN','CHONGQING_CHONGQING')
            """)
            assert_eq("4 直辖市禁重复 (新增红线-7, batch8-tagged)", cur.fetchone()[0], 0)

            cur.execute(f"""
                SELECT COUNT(*) FROM {TARGET_SCHEMA}.{MART_NAME}
                WHERE city_code IN ({city_list_str}) AND year = 2026
                  AND value IS NOT NULL
            """)
            assert_eq("5 city × 2026 全部 DATA_MISSING (新增红线-2)", cur.fetchone()[0], 0)

            cur.execute(f"""
                SELECT COUNT(*) FROM {TARGET_SCHEMA}.{MART_NAME}
                WHERE city_code IN ({city_list_str}) AND year < 2020
                  AND value IS NOT NULL
            """)
            assert_eq("2020前 (2001-2019) 禁 (新增红线-1)", cur.fetchone()[0], 0)

            # Section 9: lineage_origin 全部含 hongheiku eid
            print("\n--- Section 9: lineage_origin 全部含 hongheiku eid ---")
            cur.execute(f"""
                SELECT COUNT(*) FROM {TARGET_SCHEMA}.{MART_NAME}
                WHERE city_code IN ({city_list_str}) AND year BETWEEN 2020 AND 2025
                  AND lineage_ruling LIKE 'K669b-i-batch8-%%'
                  AND lineage_origin LIKE '%hongheiku.com%'
            """)
            assert_eq("2020-2025 lineage_origin 全含 hongheiku.com (300 cells)", cur.fetchone()[0], 300)

            cur.execute(f"""
                SELECT COUNT(*) FROM {TARGET_SCHEMA}.{MART_NAME}
                WHERE city_code IN ({city_list_str}) AND year BETWEEN 2020 AND 2025
                  AND lineage_ruling LIKE 'K669b-i-batch8-%%'
                  AND lineage_origin ~ 'tjgb\.hongheiku\.com/djs/[0-9]+\.html'
            """)
            assert_eq("2020-2025 lineage_origin 全含 /djs/{eid}.html (Knife E pattern)", cur.fetchone()[0], 300)

        # Final tally
        print(f"\n=== Result: {PASS} PASS / {FAIL} FAIL ===")
        if FAIL > 0:
            sys.exit(1)
        print("✓ knife 669b-i batch8 verify PASS — DELIVERED")

    finally:
        conn.close()


if __name__ == "__main__":
    main()
