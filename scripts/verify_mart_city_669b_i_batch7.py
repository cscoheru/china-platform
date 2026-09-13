#!/usr/bin/env python3
"""669b-i batch7 verify script — 32+ 红线 PASS.

knife 669b-i batch7 (2026-09-13) verify for 5 皖 satellite city harvest (2020-2025):
  ANHUI_HEFEI, ANHUI_WUHU, ANHUI_BENGBU, ANHUI_MAANSHAN, ANHUI_ANQING
  - 28 city-year coverage (5+6+5+6+6) × 10 indicators = 280 cells
  - 129 real HONGHEIKU_TRANSLOAD + 151 DATA_MISSING
  - lineage_ruling K669b-i-batch7-parse-{year}-2026-09-13 (6 versions for 2020-2025)
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
    "ANHUI_HEFEI",
    "ANHUI_WUHU",
    "ANHUI_BENGBU",
    "ANHUI_MAANSHAN",
    "ANHUI_ANQING",
]

# Per-city real cell counts (129 real cells total)
EXPECTED_REAL = {
    "ANHUI_HEFEI":     8,   # 2020:0 + 2021:8 + 2022:0 + 2023:0 + 2024:0 + 2025:0 = 8
    "ANHUI_WUHU":     40,   # 2020:7 + 2021:8 + 2022:7 + 2023:7 + 2024:6 + 2025:5 = 40
    "ANHUI_BENGBU":   23,   # 2020:0 + 2021:0 + 2022:8 + 2023:8 + 2024:7 + 2025:0 = 23
    "ANHUI_MAANSHAN": 26,   # 2020:0 + 2021:0 + 2022:8 + 2023:0 + 2024:9 + 2025:9 = 26
    "ANHUI_ANQING":   32,   # 2020:6 + 2021:0 + 2022:9 + 2023:0 + 2024:8 + 2025:9 = 32
}

# Per-city per-year real cell counts for lineage_origin eid verification
EXPECTED_EID_PER_CITY_YEAR = {
    ("ANHUI_WUHU",      2020): "1314",
    ("ANHUI_WUHU",      2021): "26069",
    ("ANHUI_WUHU",      2022): "35845",
    ("ANHUI_WUHU",      2023): "47823",
    ("ANHUI_WUHU",      2024): "60177",
    ("ANHUI_WUHU",      2025): "74727",
    ("ANHUI_HEFEI",     2021): "25210",
    ("ANHUI_HEFEI",     2022): "38447",
    ("ANHUI_HEFEI",     2023): "46594",
    ("ANHUI_HEFEI",     2024): "57806",
    ("ANHUI_HEFEI",     2025): "68352",
    ("ANHUI_BENGBU",    2021): "26070",
    ("ANHUI_BENGBU",    2022): "35581",
    ("ANHUI_BENGBU",    2023): "49704",
    ("ANHUI_BENGBU",    2024): "57883",
    ("ANHUI_BENGBU",    2025): "70929",
    ("ANHUI_MAANSHAN",  2020): "1602",
    ("ANHUI_MAANSHAN",  2021): "26064",
    ("ANHUI_MAANSHAN",  2022): "38450",
    ("ANHUI_MAANSHAN",  2023): "48116",
    ("ANHUI_MAANSHAN",  2024): "60502",
    ("ANHUI_MAANSHAN",  2025): "76325",
    ("ANHUI_ANQING",    2020): "7778",
    ("ANHUI_ANQING",    2021): "28763",
    ("ANHUI_ANQING",    2022): "37154",
    ("ANHUI_ANQING",    2023): "51689",
    ("ANHUI_ANQING",    2024): "63949",
    ("ANHUI_ANQING",    2025): "75589",
}

# Cells expected per year (5 cities × 10 indicators = 50; HEFEI/BENGBU miss 2020 → 30 only)
EXPECTED_TAG_PER_YEAR = {
    2020: 30,  # 3 cities (WUHU/MAANSHAN/ANQING) × 10
    2021: 50,
    2022: 50,
    2023: 50,
    2024: 50,
    2025: 50,
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
    print(f"=== knife 669b-i batch7 verify (32+ 红线) ===")
    print(f"DB: {DB_HOST}:{DB_PORT}/{DB_NAME}, cities={CITIES}")
    print()

    city_list = ",".join(f"'{c}'" for c in CITIES)
    conn = get_conn()
    try:
        with conn.cursor() as cur:

            # ===== Section 1: total cell counts (5 红线) =====
            print("--- Section 1: total batch7 cell counts (2020-2025) ---")
            cur.execute(f"""
                SELECT COUNT(*) FROM {SCHEMA}.{TABLE}
                WHERE city_code IN ({city_list}) AND year BETWEEN 2020 AND 2025
                  AND lineage_ruling LIKE 'K669b-i-batch7-%%'
            """)
            assert_eq("5 city × 2020-2025 cells (28 city-years × 10 = 280, batch7-tagged)",
                      cur.fetchone()[0], 280)

            cur.execute(f"""
                SELECT COUNT(*) FROM {SCHEMA}.{TABLE}
                WHERE city_code IN ({city_list}) AND year BETWEEN 2020 AND 2025
                  AND lineage_ruling LIKE 'K669b-i-batch7-%%'
                  AND value IS NOT NULL
            """)
            assert_eq("real cells (129, batch7-tagged)", cur.fetchone()[0], 129)

            cur.execute(f"""
                SELECT COUNT(*) FROM {SCHEMA}.{TABLE}
                WHERE city_code IN ({city_list}) AND year BETWEEN 2020 AND 2025
                  AND lineage_ruling LIKE 'K669b-i-batch7-%%'
                  AND status = 'DATA_MISSING'
            """)
            assert_eq("DATA_MISSING cells (151 = 280 - 129 real, batch7-tagged)",
                      cur.fetchone()[0], 151)

            cur.execute(f"""
                SELECT COUNT(*) FROM {SCHEMA}.{TABLE}
                WHERE city_code IN ({city_list}) AND year BETWEEN 2020 AND 2025
                  AND lineage_ruling LIKE 'K669b-i-batch7-%%'
            """)
            assert_eq("280 cells tagged K669b-i-batch7-* (matched seed)", cur.fetchone()[0], 280)

            cur.execute(f"""
                SELECT COUNT(*) FROM {SCHEMA}.{TABLE}
                WHERE city_code IN ({city_list}) AND year BETWEEN 2020 AND 2025
                  AND lineage_ruling LIKE 'K669b-i-batch7-%%'
                  AND value IS NOT NULL AND status IS NULL AND missing_reason IS NULL
            """)
            assert_eq("Real cells: status=NULL, missing_reason=NULL", cur.fetchone()[0], 129)

            # ===== Section 2: per-city real cell count (5 红线) =====
            print("\n--- Section 2: per-city real cell count ---")
            for city, expected_real in EXPECTED_REAL.items():
                cur.execute(f"""
                    SELECT COUNT(*) FROM {SCHEMA}.{TABLE}
                    WHERE city_code = %s AND year BETWEEN 2020 AND 2025
                      AND lineage_ruling LIKE 'K669b-i-batch7-%%'
                      AND value IS NOT NULL
                """, (city,))
                assert_eq(f"{city} real cells (batch7-tagged)",
                          cur.fetchone()[0], expected_real)

            # ===== Section 3: lineage_ruling attribution (6 红线) =====
            print("\n--- Section 3: lineage_ruling 6 year versions ---")
            for yr in [2020, 2021, 2022, 2023, 2024, 2025]:
                cur.execute(f"""
                    SELECT COUNT(*) FROM {SCHEMA}.{TABLE}
                    WHERE city_code IN ({city_list}) AND year = %s
                      AND lineage_ruling = %s
                """, (yr, f"K669b-i-batch7-parse-{yr}-2026-09-13"))
                expected = EXPECTED_TAG_PER_YEAR[yr]
                assert_eq(f"lineage_ruling K669b-i-batch7-parse-{yr} ({expected} cells)",
                          cur.fetchone()[0], expected)

            # ===== Section 4: lineage_source_type (4 红线) =====
            print("\n--- Section 4: lineage_source_type (batch7-tagged) ---")
            cur.execute(f"""
                SELECT COUNT(*) FROM {SCHEMA}.{TABLE}
                WHERE city_code IN ({city_list}) AND year BETWEEN 2020 AND 2025
                  AND lineage_ruling LIKE 'K669b-i-batch7-%%'
                  AND value IS NOT NULL AND lineage_source_type = 'HONGHEIKU_TRANSLOAD'
            """)
            assert_eq("real cells source_type=HONGHEIKU_TRANSLOAD (batch7-tagged)",
                      cur.fetchone()[0], 129)

            cur.execute(f"""
                SELECT COUNT(*) FROM {SCHEMA}.{TABLE}
                WHERE city_code IN ({city_list}) AND year BETWEEN 2020 AND 2025
                  AND lineage_ruling LIKE 'K669b-i-batch7-%%'
                  AND status = 'DATA_MISSING' AND lineage_source_type = 'DATA_MISSING'
            """)
            assert_eq("miss cells source_type=DATA_MISSING (batch7-tagged)",
                      cur.fetchone()[0], 151)

            cur.execute(f"""
                SELECT COUNT(*) FROM {SCHEMA}.{TABLE}
                WHERE city_code IN ({city_list}) AND year BETWEEN 2020 AND 2025
                  AND lineage_ruling LIKE 'K669b-i-batch7-%%'
                  AND value IS NOT NULL AND lineage_source_type != 'HONGHEIKU_TRANSLOAD'
            """)
            assert_eq("real cells NOT HONGHEIKU_TRANSLOAD = 0 (batch7-tagged)",
                      cur.fetchone()[0], 0)

            cur.execute(f"""
                SELECT COUNT(*) FROM {SCHEMA}.{TABLE}
                WHERE city_code IN ({city_list}) AND year BETWEEN 2020 AND 2025
                  AND lineage_ruling LIKE 'K669b-i-batch7-%%'
                  AND status = 'DATA_MISSING' AND (missing_reason IS NULL OR missing_reason = '')
            """)
            assert_eq("miss cells missing_reason 必填 = 0 missing (batch7-tagged)",
                      cur.fetchone()[0], 0)

            # ===== Section 5: lineage_origin per-year (6 红线, batch7-tagged) =====
            print("\n--- Section 5: lineage_origin per-year total (batch7-tagged) ---")
            for yr in [2020, 2021, 2022, 2023, 2024, 2025]:
                cur.execute(f"""
                    SELECT COUNT(*) FROM {SCHEMA}.{TABLE}
                    WHERE city_code IN ({city_list}) AND year = %s
                      AND lineage_ruling LIKE 'K669b-i-batch7-%%'
                      AND lineage_origin LIKE '%%hongheiku.com%%'
                """, (yr,))
                expected = EXPECTED_TAG_PER_YEAR[yr]
                assert_eq(f"{yr} lineage_origin 含 hongheiku.com ({expected} cells, batch7-tagged)",
                          cur.fetchone()[0], expected)

            # ===== Section 6: HEFEI 2020 cross-batch contamination / BENGBU 2020 no eid =====
            # 守红线-3: hongheiku 0 entry, 禁补零
            # HEFEI 2020 有 10 cells from K669fix-b-2020 (跨批次, prior knife 25 省会 harvest),
            # 本批 batch7 不覆盖 HEFEI 2020, 守 batch7-tagged filter
            print("\n--- Section 6: HEFEI/BENGBU 2020 no batch7 eid (守红线-1/3, 禁补零) ---")
            cur.execute(f"""
                SELECT COUNT(*) FROM {SCHEMA}.{TABLE}
                WHERE city_code = 'ANHUI_HEFEI' AND year = 2020
                  AND lineage_ruling LIKE 'K669b-i-batch7-%%'
            """)
            assert_eq("HEFEI 2020 batch7-tagged cells (0 — not in batch7 scope)",
                      cur.fetchone()[0], 0)

            # HEFEI 2020 prior knife contamination (10 cells from K669fix-b-2020)
            cur.execute(f"""
                SELECT COUNT(*) FROM {SCHEMA}.{TABLE}
                WHERE city_code = 'ANHUI_HEFEI' AND year = 2020
                  AND lineage_ruling LIKE 'K669fix-b-2020-%%'
            """)
            assert_eq("HEFEI 2020 K669fix-b-2020 cross-batch (10 from prior knife, 守历史溯源)",
                      cur.fetchone()[0], 10)

            cur.execute(f"""
                SELECT COUNT(*) FROM {SCHEMA}.{TABLE}
                WHERE city_code = 'ANHUI_BENGBU' AND year = 2020
            """)
            assert_eq("BENGBU 2020 cells in mart (0 — not in batch7 seed CSV)",
                      cur.fetchone()[0], 0)

            # ===== Section 7: cross product sanity (3 红线) =====
            print("\n--- Section 7: cross product sanity ---")
            cur.execute(f"""
                SELECT COUNT(DISTINCT city_code) FROM {SCHEMA}.{TABLE}
                WHERE city_code IN ({city_list})
                  AND lineage_ruling LIKE 'K669b-i-batch7-%%'
            """)
            assert_eq("5 city distinct (batch7-tagged)", cur.fetchone()[0], 5)

            cur.execute(f"""
                SELECT COUNT(DISTINCT indicator_key) FROM {SCHEMA}.{TABLE}
                WHERE city_code IN ({city_list})
                  AND lineage_ruling LIKE 'K669b-i-batch7-%%'
            """)
            assert_eq("10 indicator distinct (batch7-tagged)", cur.fetchone()[0], 10)

            cur.execute(f"""
                SELECT COUNT(DISTINCT year) FROM {SCHEMA}.{TABLE}
                WHERE city_code IN ({city_list}) AND year BETWEEN 2020 AND 2025
                  AND lineage_ruling LIKE 'K669b-i-batch7-%%'
            """)
            assert_eq("6 year distinct (2020-2025, batch7-tagged)", cur.fetchone()[0], 6)

            # ===== Section 8: red lines (3 红线) =====
            print("\n--- Section 8: red lines ---")
            # 4 直辖市禁 (新增红线-7)
            cur.execute(f"""
                SELECT COUNT(*) FROM {SCHEMA}.{TABLE}
                WHERE (city_code LIKE 'BEIJING_%%' OR city_code LIKE 'SHANGHAI_%%'
                   OR city_code LIKE 'TIANJIN_%%' OR city_code LIKE 'CHONGQING_%%')
                  AND lineage_ruling LIKE 'K669b-i-batch7-%%'
            """)
            assert_eq("4 直辖市禁重复 (新增红线-7, batch7-tagged)", cur.fetchone()[0], 0)

            # 2026 全 DATA_MISSING (新增红线-2)
            cur.execute(f"""
                SELECT COUNT(*) FROM {SCHEMA}.{TABLE}
                WHERE city_code IN ({city_list}) AND year = 2026 AND value IS NOT NULL
            """)
            assert_eq("5 city × 2026 全部 DATA_MISSING (新增红线-2)", cur.fetchone()[0], 0)

            # year attribution CORRECT — no (city, year, eid) drift
            or_clauses = []
            params = ["K669b-i-batch7-%%"]  # lineage_ruling LIKE %s (FIRST in SQL)
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
            assert_eq("year→eid attribution CORRECT (Knife E 970 fix verified, 28 city-year × eid pairs)",
                      cur.fetchone()[0], 0)

    finally:
        conn.close()

    print(f"\n=== Result: {PASS} PASS / {FAIL} FAIL ===")
    return 0 if FAIL == 0 else 1


if __name__ == "__main__":
    sys.exit(main())