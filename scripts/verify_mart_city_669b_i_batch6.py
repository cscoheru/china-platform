#!/usr/bin/env python3
"""669b-i batch6 verify script — 32+ 红线 PASS.

knife 669b-i batch6 (2026-09-13) verify for 5 闽 satellite city harvest (2020-2025):
  FUJIAN_FUZHOU, FUJIAN_QUANZHOU, FUJIAN_ZHANGZHOU, FUJIAN_PUTIAN, FUJIAN_LONGYAN
  - 30 city-year coverage (5 city × 6 year) × 10 indicators = 300 cells
  - 189 real HONGHEIKU_TRANSLOAD + 111 DATA_MISSING
  - lineage_ruling K669b-i-batch6-parse-{year}-2026-09-13 (6 versions for 2020-2025)
  - 2026 cells stay DATA_MISSING (守新增红线-2 禁补零)
  - 5 city ≠ 4 直辖市 (守新增红线-7)
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

CITIES = [
    "FUJIAN_FUZHOU",
    "FUJIAN_QUANZHOU",
    "FUJIAN_ZHANGZHOU",
    "FUJIAN_PUTIAN",
    "FUJIAN_LONGYAN",
]

# Per-city real cell counts (189 real cells total)
EXPECTED_REAL = {
    "FUJIAN_FUZHOU":    44,  # 2020:8 + 2021:10 + 2022:0 + 2023:9 + 2024:9 + 2025:8 = 44
    "FUJIAN_QUANZHOU":  47,  # 2020:7 + 2021:9 + 2022:9 + 2023:8 + 2024:7 + 2025:7 = 47
    "FUJIAN_ZHANGZHOU": 26,  # 2020:7 + 2021:0 + 2022:10 + 2023:0 + 2024:9 + 2025:0 = 26
    "FUJIAN_PUTIAN":    18,  # 2020:0 + 2021:0 + 2022:0 + 2023:9 + 2024:9 + 2025:0 = 18
    "FUJIAN_LONGYAN":   54,  # 2020:8 + 2021:9 + 2022:10 + 2023:9 + 2024:9 + 2025:9 = 54
}

# Per-city per-year real cell counts for lineage_origin eid verification
EXPECTED_EID_PER_CITY_YEAR = {
    ("FUJIAN_FUZHOU",    2020): "3413",
    ("FUJIAN_FUZHOU",    2021): "25196",
    ("FUJIAN_FUZHOU",    2022): "36254",
    ("FUJIAN_FUZHOU",    2023): "47449",
    ("FUJIAN_FUZHOU",    2024): "58216",
    ("FUJIAN_FUZHOU",    2025): "68665",
    ("FUJIAN_QUANZHOU",  2020): "442",
    ("FUJIAN_QUANZHOU",  2021): "27542",
    ("FUJIAN_QUANZHOU",  2022): "38424",
    ("FUJIAN_QUANZHOU",  2023): "46428",
    ("FUJIAN_QUANZHOU",  2024): "57942",
    ("FUJIAN_QUANZHOU",  2025): "72006",
    ("FUJIAN_ZHANGZHOU", 2020): "17422",
    ("FUJIAN_ZHANGZHOU", 2022): "38410",
    ("FUJIAN_ZHANGZHOU", 2024): "57814",
    ("FUJIAN_PUTIAN",    2023): "48344",
    ("FUJIAN_PUTIAN",    2024): "58915",
    ("FUJIAN_LONGYAN",   2020): "1562",
    ("FUJIAN_LONGYAN",   2021): "24561",
    ("FUJIAN_LONGYAN",   2022): "35072",
    ("FUJIAN_LONGYAN",   2023): "45677",
    ("FUJIAN_LONGYAN",   2024): "57726",
    ("FUJIAN_LONGYAN",   2025): "68737",
}

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
    global PASS, FAIL
    print(f"=== knife 669b-i batch6 verify (32+ 红线) ===")
    print(f"DB: {DB_HOST}:{DB_PORT}/{DB_NAME}, cities={CITIES}")
    print()

    city_list = ",".join(f"'{c}'" for c in CITIES)
    conn = get_conn()
    try:
        with conn.cursor() as cur:

            # ===== Section 1: total cell counts (5 红线) =====
            print("--- Section 1: total batch6 cell counts (2020-2025) ---")
            cur.execute(f"""
                SELECT COUNT(*) FROM {SCHEMA}.{TABLE}
                WHERE city_code IN ({city_list}) AND year BETWEEN 2020 AND 2025
                  AND lineage_ruling LIKE 'K669b-i-batch6-%%'
            """)
            assert_eq("5 city × 2020-2025 cells (30 city-years × 10 = 300, batch6-tagged)",
                      cur.fetchone()[0], 300)

            cur.execute(f"""
                SELECT COUNT(*) FROM {SCHEMA}.{TABLE}
                WHERE city_code IN ({city_list}) AND year BETWEEN 2020 AND 2025
                  AND lineage_ruling LIKE 'K669b-i-batch6-%%'
                  AND value IS NOT NULL
            """)
            assert_eq("real cells (189, batch6-tagged)", cur.fetchone()[0], 189)

            cur.execute(f"""
                SELECT COUNT(*) FROM {SCHEMA}.{TABLE}
                WHERE city_code IN ({city_list}) AND year BETWEEN 2020 AND 2025
                  AND lineage_ruling LIKE 'K669b-i-batch6-%%'
                  AND status = 'DATA_MISSING'
            """)
            assert_eq("DATA_MISSING cells (111 = 300 - 189 real, batch6-tagged)",
                      cur.fetchone()[0], 111)

            cur.execute(f"""
                SELECT COUNT(*) FROM {SCHEMA}.{TABLE}
                WHERE city_code IN ({city_list}) AND year BETWEEN 2020 AND 2025
                  AND lineage_ruling LIKE 'K669b-i-batch6-%%'
            """)
            assert_eq("300 cells tagged K669b-i-batch6-* (matched seed)", cur.fetchone()[0], 300)

            cur.execute(f"""
                SELECT COUNT(*) FROM {SCHEMA}.{TABLE}
                WHERE city_code IN ({city_list}) AND year BETWEEN 2020 AND 2025
                  AND lineage_ruling LIKE 'K669b-i-batch6-%%'
                  AND value IS NOT NULL AND status IS NULL AND missing_reason IS NULL
            """)
            assert_eq("Real cells: status=NULL, missing_reason=NULL", cur.fetchone()[0], 189)

            # ===== Section 2: per-city real cell count (5 红线) =====
            print("\n--- Section 2: per-city real cell count ---")
            for city, expected_real in EXPECTED_REAL.items():
                cur.execute(f"""
                    SELECT COUNT(*) FROM {SCHEMA}.{TABLE}
                    WHERE city_code = %s AND year BETWEEN 2020 AND 2025
                      AND lineage_ruling LIKE 'K669b-i-batch6-%%'
                      AND value IS NOT NULL
                """, (city,))
                assert_eq(f"{city} real cells (batch6-tagged)",
                          cur.fetchone()[0], expected_real)

            # ===== Section 3: lineage_ruling attribution (6 红线) =====
            print("\n--- Section 3: lineage_ruling 6 year versions ---")
            # All 5 city have full 6 year coverage in seed CSV (even if all-miss),
            # so each year has 5 × 10 = 50 cells tagged
            for yr in [2020, 2021, 2022, 2023, 2024, 2025]:
                cur.execute(f"""
                    SELECT COUNT(*) FROM {SCHEMA}.{TABLE}
                    WHERE city_code IN ({city_list}) AND year = %s
                      AND lineage_ruling = %s
                """, (yr, f"K669b-i-batch6-parse-{yr}-2026-09-13"))
                assert_eq(f"lineage_ruling K669b-i-batch6-parse-{yr} (50 cells)",
                          cur.fetchone()[0], 50)

            # ===== Section 4: lineage_source_type (4 红线) =====
            print("\n--- Section 4: lineage_source_type (batch6-tagged) ---")
            cur.execute(f"""
                SELECT COUNT(*) FROM {SCHEMA}.{TABLE}
                WHERE city_code IN ({city_list}) AND year BETWEEN 2020 AND 2025
                  AND lineage_ruling LIKE 'K669b-i-batch6-%%'
                  AND value IS NOT NULL AND lineage_source_type = 'HONGHEIKU_TRANSLOAD'
            """)
            assert_eq("real cells source_type=HONGHEIKU_TRANSLOAD (batch6-tagged)",
                      cur.fetchone()[0], 189)

            cur.execute(f"""
                SELECT COUNT(*) FROM {SCHEMA}.{TABLE}
                WHERE city_code IN ({city_list}) AND year BETWEEN 2020 AND 2025
                  AND lineage_ruling LIKE 'K669b-i-batch6-%%'
                  AND status = 'DATA_MISSING' AND lineage_source_type = 'DATA_MISSING'
            """)
            assert_eq("miss cells source_type=DATA_MISSING (batch6-tagged)",
                      cur.fetchone()[0], 111)

            cur.execute(f"""
                SELECT COUNT(*) FROM {SCHEMA}.{TABLE}
                WHERE city_code IN ({city_list}) AND year BETWEEN 2020 AND 2025
                  AND lineage_ruling LIKE 'K669b-i-batch6-%%'
                  AND value IS NOT NULL AND lineage_source_type != 'HONGHEIKU_TRANSLOAD'
            """)
            assert_eq("real cells NOT HONGHEIKU_TRANSLOAD = 0 (batch6-tagged)",
                      cur.fetchone()[0], 0)

            cur.execute(f"""
                SELECT COUNT(*) FROM {SCHEMA}.{TABLE}
                WHERE city_code IN ({city_list}) AND year BETWEEN 2020 AND 2025
                  AND lineage_ruling LIKE 'K669b-i-batch6-%%'
                  AND status = 'DATA_MISSING' AND (missing_reason IS NULL OR missing_reason = '')
            """)
            assert_eq("miss cells missing_reason 必填 = 0 missing (batch6-tagged)",
                      cur.fetchone()[0], 0)

            # ===== Section 5: lineage_origin per-year (6 红线, batch6-tagged) =====
            print("\n--- Section 5: lineage_origin per-year total (batch6-tagged) ---")
            for yr in [2020, 2021, 2022, 2023, 2024, 2025]:
                cur.execute(f"""
                    SELECT COUNT(*) FROM {SCHEMA}.{TABLE}
                    WHERE city_code IN ({city_list}) AND year = %s
                      AND lineage_ruling LIKE 'K669b-i-batch6-%%'
                      AND lineage_origin LIKE '%%hongheiku.com%%'
                """, (yr,))
                assert_eq(f"{yr} lineage_origin 含 hongheiku.com (50 cells, batch6-tagged)",
                          cur.fetchone()[0], 50)

            # ===== Section 6: PUTIAN partial coverage (守红线-3 禁补零) =====
            # PUTIAN 2020/2021/2022/2025: parser-fail miss, all-miss verified
            print("\n--- Section 6: PUTIAN 4 all-miss years (parser-fail, 禁补零) ---")
            for yr in [2020, 2021, 2022, 2025]:
                cur.execute(f"""
                    SELECT COUNT(*) FROM {SCHEMA}.{TABLE}
                    WHERE city_code = 'FUJIAN_PUTIAN' AND year = %s
                      AND lineage_ruling LIKE 'K669b-i-batch6-%%'
                      AND value IS NOT NULL
                """, (yr,))
                assert_eq(f"PUTIAN {yr} real cells (0 — parser-fail miss)",
                          cur.fetchone()[0], 0)

            # ZHANGZHOU 3 all-miss years (2021/2023/2025)
            print("\n--- Section 6b: ZHANGZHOU 3 all-miss years (parser-fail, 禁补零) ---")
            for yr in [2021, 2023, 2025]:
                cur.execute(f"""
                    SELECT COUNT(*) FROM {SCHEMA}.{TABLE}
                    WHERE city_code = 'FUJIAN_ZHANGZHOU' AND year = %s
                      AND lineage_ruling LIKE 'K669b-i-batch6-%%'
                      AND value IS NOT NULL
                """, (yr,))
                assert_eq(f"ZHANGZHOU {yr} real cells (0 — parser-fail miss)",
                          cur.fetchone()[0], 0)

            # FUZHOU 2022: parser-fail miss (single)
            print("\n--- Section 6c: FUZHOU 2022 all-miss (parser-fail, 禁补零) ---")
            cur.execute(f"""
                SELECT COUNT(*) FROM {SCHEMA}.{TABLE}
                WHERE city_code = 'FUJIAN_FUZHOU' AND year = 2022
                  AND lineage_ruling LIKE 'K669b-i-batch6-%%'
                  AND value IS NOT NULL
            """)
            assert_eq("FUZHOU 2022 real cells (0 — parser-fail miss)",
                      cur.fetchone()[0], 0)

            # ===== Section 7: cross product sanity (3 红线) =====
            print("\n--- Section 7: cross product sanity ---")
            cur.execute(f"""
                SELECT COUNT(DISTINCT city_code) FROM {SCHEMA}.{TABLE}
                WHERE city_code IN ({city_list})
                  AND lineage_ruling LIKE 'K669b-i-batch6-%%'
            """)
            assert_eq("5 city distinct (batch6-tagged)", cur.fetchone()[0], 5)

            cur.execute(f"""
                SELECT COUNT(DISTINCT indicator_key) FROM {SCHEMA}.{TABLE}
                WHERE city_code IN ({city_list})
                  AND lineage_ruling LIKE 'K669b-i-batch6-%%'
            """)
            assert_eq("10 indicator distinct (batch6-tagged)", cur.fetchone()[0], 10)

            cur.execute(f"""
                SELECT COUNT(DISTINCT year) FROM {SCHEMA}.{TABLE}
                WHERE city_code IN ({city_list}) AND year BETWEEN 2020 AND 2025
                  AND lineage_ruling LIKE 'K669b-i-batch6-%%'
            """)
            assert_eq("6 year distinct (2020-2025, batch6-tagged)", cur.fetchone()[0], 6)

            # ===== Section 8: red lines (3 红线) =====
            print("\n--- Section 8: red lines ---")
            # 4 直辖市禁 (新增红线-7)
            cur.execute(f"""
                SELECT COUNT(*) FROM {SCHEMA}.{TABLE}
                WHERE city_code LIKE 'BEIJING_%%' OR city_code LIKE 'SHANGHAI_%%'
                   OR city_code LIKE 'TIANJIN_%%' OR city_code LIKE 'CHONGQING_%%'
                  AND lineage_ruling LIKE 'K669b-i-batch6-%%'
            """)
            assert_eq("4 直辖市禁重复 (新增红线-7, batch6-tagged)", cur.fetchone()[0], 0)

            # 2026 全 DATA_MISSING (新增红线-2)
            cur.execute(f"""
                SELECT COUNT(*) FROM {SCHEMA}.{TABLE}
                WHERE city_code IN ({city_list}) AND year = 2026 AND value IS NOT NULL
            """)
            assert_eq("5 city × 2026 全部 DATA_MISSING (新增红线-2)", cur.fetchone()[0], 0)

            # year attribution CORRECT — no (city, year, eid) drift
            # Build large OR expression for all (city, year, expected_eid) tuples
            or_clauses = []
            params = ["K669b-i-batch6-%%"]  # lineage_ruling LIKE %s (FIRST in SQL)
            for (city, yr), eid in EXPECTED_EID_PER_CITY_YEAR.items():
                or_clauses.append("(city_code = %s AND year = %s AND lineage_origin NOT LIKE %s)")
                params.extend([city, yr, f"%%{eid}%%"])
            cur.execute(f"""
                SELECT COUNT(*) FROM {SCHEMA}.{TABLE}
                WHERE city_code IN ({city_list}) AND year BETWEEN 2020 AND 2025
                  AND value IS NOT NULL
                  AND lineage_ruling LIKE %s
                  AND (
                    {' OR '.join(or_clauses)}
                  )
            """, params)
            assert_eq("year→eid attribution CORRECT (Knife E 970 fix verified, 23 city-year × eid pairs)",
                      cur.fetchone()[0], 0)

    finally:
        conn.close()

    print(f"\n=== Result: {PASS} PASS / {FAIL} FAIL ===")
    return 0 if FAIL == 0 else 1


if __name__ == "__main__":
    sys.exit(main())