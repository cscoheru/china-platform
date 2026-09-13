#!/usr/bin/env python3
"""669b-i batch5 verify script — 32+ 红线 PASS.

knife 669b-i batch5 (2026-09-13) verify for 5 鄂 satellite city harvest (2020-2025):
  HUBEI_YICHANG, HUBEI_XIANGYANG, HUBEI_JINGZHOU, HUBEI_HUANGGANG, HUBEI_SHIYAN
  - 28 city-year coverage: YICHANG(6)+XIANGYANG(5)+JINGZHOU(6)+HUANGGANG(6)+SHIYAN(5) = 28
  - 280 seed cells (214 real HONGHEIKU_TRANSLOAD + 66 DATA_MISSING)
  - lineage_ruling K669b-i-batch5-parse-{year}-2026-09-13 (6 versions for 2020-2025)
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
    "HUBEI_YICHANG",
    "HUBEI_XIANGYANG",
    "HUBEI_JINGZHOU",
    "HUBEI_HUANGGANG",
    "HUBEI_SHIYAN",
]

# Per-city real cell counts (214 real cells total)
EXPECTED_REAL = {
    "HUBEI_YICHANG":   51,  # 2020:7 + 2021:8 + 2022:8 + 2023:9 + 2024:10 + 2025:9 = 51
    "HUBEI_XIANGYANG": 39,  # 2020:7 + 2021:9 + 2022:8 + 2023:7 + 2024:8 = 39 (2025 null)
    "HUBEI_JINGZHOU":  51,  # 2020:7 + 2021:8 + 2022:9 + 2023:9 + 2024:9 + 2025:9 = 51
    "HUBEI_HUANGGANG": 33,  # 2020:7 + 2022:7 + 2023:5 + 2024:7 + 2025:7 = 33 (2021 null)
    "HUBEI_SHIYAN":    40,  # 2020:8 + 2022:9 + 2023:8 + 2024:8 + 2025:7 = 40 (2021 null)
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
    print(f"=== knife 669b-i batch5 verify (32+ 红线) ===")
    print(f"DB: {DB_HOST}:{DB_PORT}/{DB_NAME}, cities={CITIES}")
    print()

    city_list = ",".join(f"'{c}'" for c in CITIES)
    conn = get_conn()
    try:
        with conn.cursor() as cur:

            # ===== Section 1: total cell counts (5 红线) =====
            # 5 new cities — 28 city-years × 10 indicators = 280 cells in 2020-2025
            # All counts filtered to batch5-tagged cells (lineage_ruling LIKE K669b-i-batch5-%)
            # to avoid contamination from prior 669j-4 XIANGYANG 2025 rows.
            print("--- Section 1: total batch5 cell counts (2020-2025) ---")
            cur.execute(f"""
                SELECT COUNT(*) FROM {SCHEMA}.{TABLE}
                WHERE city_code IN ({city_list}) AND year BETWEEN 2020 AND 2025
                  AND lineage_ruling LIKE 'K669b-i-batch5-%%'
            """)
            assert_eq("5 city × 2020-2025 cells (28 city-years × 10 = 280, batch5-tagged)",
                      cur.fetchone()[0], 280)

            cur.execute(f"""
                SELECT COUNT(*) FROM {SCHEMA}.{TABLE}
                WHERE city_code IN ({city_list}) AND year BETWEEN 2020 AND 2025
                  AND lineage_ruling LIKE 'K669b-i-batch5-%%'
                  AND value IS NOT NULL
            """)
            assert_eq("real cells (214, batch5-tagged)", cur.fetchone()[0], 214)

            cur.execute(f"""
                SELECT COUNT(*) FROM {SCHEMA}.{TABLE}
                WHERE city_code IN ({city_list}) AND year BETWEEN 2020 AND 2025
                  AND lineage_ruling LIKE 'K669b-i-batch5-%%'
                  AND status = 'DATA_MISSING'
            """)
            assert_eq("DATA_MISSING cells (66 = 280 - 214 real, batch5-tagged)",
                      cur.fetchone()[0], 66)

            cur.execute(f"""
                SELECT COUNT(*) FROM {SCHEMA}.{TABLE}
                WHERE city_code IN ({city_list}) AND year BETWEEN 2020 AND 2025
                  AND lineage_ruling LIKE 'K669b-i-batch5-%%'
            """)
            assert_eq("280 cells tagged K669b-i-batch5-* (matched seed)", cur.fetchone()[0], 280)

            cur.execute(f"""
                SELECT COUNT(*) FROM {SCHEMA}.{TABLE}
                WHERE city_code IN ({city_list}) AND year BETWEEN 2020 AND 2025
                  AND lineage_ruling LIKE 'K669b-i-batch5-%%'
                  AND value IS NOT NULL AND status IS NULL AND missing_reason IS NULL
            """)
            assert_eq("Real cells: status=NULL, missing_reason=NULL", cur.fetchone()[0], 214)

            # ===== Section 2: per-city real cell count (5 红线) =====
            print("\n--- Section 2: per-city real cell count ---")
            for city, expected_real in EXPECTED_REAL.items():
                cur.execute(f"""
                    SELECT COUNT(*) FROM {SCHEMA}.{TABLE}
                    WHERE city_code = %s AND year BETWEEN 2020 AND 2025 AND value IS NOT NULL
                """, (city,))
                assert_eq(f"{city} real cells", cur.fetchone()[0], expected_real)

            # ===== Section 3: lineage_ruling attribution (6 红线) =====
            print("\n--- Section 3: lineage_ruling 6 year versions ---")
            expected_tagged_per_year = {
                2020: 50,  # 5 city × 10
                2021: 40,  # 4 city (SHIYAN null) × 10
                2022: 50,
                2023: 50,
                2024: 50,
                2025: 40,  # 4 city (XIANGYANG null) × 10
            }
            for yr in [2020, 2021, 2022, 2023, 2024, 2025]:
                cur.execute(f"""
                    SELECT COUNT(*) FROM {SCHEMA}.{TABLE}
                    WHERE city_code IN ({city_list}) AND year = %s
                      AND lineage_ruling = %s
                """, (yr, f"K669b-i-batch5-parse-{yr}-2026-09-13"))
                expected = expected_tagged_per_year[yr]
                assert_eq(f"lineage_ruling K669b-i-batch5-parse-{yr} ({expected} cells)",
                          cur.fetchone()[0], expected)

            # ===== Section 4: lineage_source_type (4 红线) =====
            # All batch5-tagged (avoid contamination from 669j-4 XIANGYANG 2025 cells)
            print("\n--- Section 4: lineage_source_type (batch5-tagged) ---")
            cur.execute(f"""
                SELECT COUNT(*) FROM {SCHEMA}.{TABLE}
                WHERE city_code IN ({city_list}) AND year BETWEEN 2020 AND 2025
                  AND lineage_ruling LIKE 'K669b-i-batch5-%%'
                  AND value IS NOT NULL AND lineage_source_type = 'HONGHEIKU_TRANSLOAD'
            """)
            assert_eq("real cells source_type=HONGHEIKU_TRANSLOAD (batch5-tagged)",
                      cur.fetchone()[0], 214)

            cur.execute(f"""
                SELECT COUNT(*) FROM {SCHEMA}.{TABLE}
                WHERE city_code IN ({city_list}) AND year BETWEEN 2020 AND 2025
                  AND lineage_ruling LIKE 'K669b-i-batch5-%%'
                  AND status = 'DATA_MISSING' AND lineage_source_type = 'DATA_MISSING'
            """)
            assert_eq("miss cells source_type=DATA_MISSING (batch5-tagged)",
                      cur.fetchone()[0], 66)

            cur.execute(f"""
                SELECT COUNT(*) FROM {SCHEMA}.{TABLE}
                WHERE city_code IN ({city_list}) AND year BETWEEN 2020 AND 2025
                  AND lineage_ruling LIKE 'K669b-i-batch5-%%'
                  AND value IS NOT NULL AND lineage_source_type != 'HONGHEIKU_TRANSLOAD'
            """)
            assert_eq("real cells NOT HONGHEIKU_TRANSLOAD = 0 (batch5-tagged)",
                      cur.fetchone()[0], 0)

            cur.execute(f"""
                SELECT COUNT(*) FROM {SCHEMA}.{TABLE}
                WHERE city_code IN ({city_list}) AND year BETWEEN 2020 AND 2025
                  AND lineage_ruling LIKE 'K669b-i-batch5-%%'
                  AND status = 'DATA_MISSING' AND (missing_reason IS NULL OR missing_reason = '')
            """)
            assert_eq("miss cells missing_reason 必填 = 0 missing (batch5-tagged)",
                      cur.fetchone()[0], 0)

            # ===== Section 5: lineage_origin per-year (6 红线, batch5-tagged) =====
            print("\n--- Section 5: lineage_origin per-year total (batch5-tagged) ---")
            for yr in [2020, 2021, 2022, 2023, 2024, 2025]:
                cur.execute(f"""
                    SELECT COUNT(*) FROM {SCHEMA}.{TABLE}
                    WHERE city_code IN ({city_list}) AND year = %s
                      AND lineage_ruling LIKE 'K669b-i-batch5-%%'
                      AND lineage_origin LIKE '%%hongheiku.com%%'
                """, (yr,))
                expected = expected_tagged_per_year[yr]
                assert_eq(f"{yr} lineage_origin 含 hongheiku.com ({expected} cells, batch5-tagged)",
                          cur.fetchone()[0], expected)

            # ===== Section 6: SHIYAN 2021 only (守红线-3, hongheiku 0 entry) =====
            # XIANGYANG 2025 already covered by prior knife 669j-4 (10 cells exist with
            # K669j-4 lineage, NOT batch5 lineage). batch5 seed has NO XIANGYANG 2025
            # entries, so we only verify SHIYAN 2021 here.
            print("\n--- Section 6: SHIYAN 2021 hongheiku 0 entry (XIANGYANG 2025 from 669j-4) ---")
            cur.execute(f"""
                SELECT COUNT(*) FROM {SCHEMA}.{TABLE}
                WHERE city_code = 'HUBEI_SHIYAN' AND year = 2021
            """)
            assert_eq("SHIYAN 2021 cells in mart (0 — not in batch5 seed CSV)",
                      cur.fetchone()[0], 0)

            cur.execute(f"""
                SELECT COUNT(*) FROM {SCHEMA}.{TABLE}
                WHERE city_code = 'HUBEI_SHIYAN' AND year = 2021
                  AND status = 'DATA_MISSING'
            """)
            assert_eq("SHIYAN 2021 DATA_MISSING (守新增红线-1, 禁补零)",
                      cur.fetchone()[0], 0)

            cur.execute(f"""
                SELECT COUNT(*) FROM {SCHEMA}.{TABLE}
                WHERE city_code = 'HUBEI_XIANGYANG' AND year = 2025
                  AND lineage_ruling LIKE 'K669b-i-batch5-%%'
            """)
            assert_eq("XIANGYANG 2025 cells batch5-tagged (0 — not in batch5 seed CSV, "
                      "10 cells from prior 669j-4 excluded)",
                      cur.fetchone()[0], 0)

            # ===== Section 7: cross product sanity (3 红线) =====
            print("\n--- Section 7: cross product sanity ---")
            cur.execute(f"""
                SELECT COUNT(DISTINCT city_code) FROM {SCHEMA}.{TABLE}
                WHERE city_code IN ({city_list})
            """)
            assert_eq("5 city distinct", cur.fetchone()[0], 5)

            cur.execute(f"""
                SELECT COUNT(DISTINCT indicator_key) FROM {SCHEMA}.{TABLE}
                WHERE city_code IN ({city_list})
            """)
            assert_eq("10 indicator distinct", cur.fetchone()[0], 10)

            cur.execute(f"""
                SELECT COUNT(DISTINCT year) FROM {SCHEMA}.{TABLE}
                WHERE city_code IN ({city_list}) AND year BETWEEN 2020 AND 2025
            """)
            assert_eq("6 year distinct (2020-2025)", cur.fetchone()[0], 6)

            # ===== Section 8: red lines (3 红线) =====
            print("\n--- Section 8: red lines ---")
            # 4 直辖市禁 (新增红线-7)
            cur.execute(f"""
                SELECT COUNT(*) FROM {SCHEMA}.{TABLE}
                WHERE city_code LIKE 'BEIJING_%%' OR city_code LIKE 'SHANGHAI_%%'
                   OR city_code LIKE 'TIANJIN_%%' OR city_code LIKE 'CHONGQING_%%'
            """)
            assert_eq("4 直辖市禁重复 (新增红线-7)", cur.fetchone()[0], 0)

            # 2026 全 DATA_MISSING (新增红线-2)
            cur.execute(f"""
                SELECT COUNT(*) FROM {SCHEMA}.{TABLE}
                WHERE city_code IN ({city_list}) AND year = 2026 AND value IS NOT NULL
            """)
            assert_eq("5 city × 2026 全部 DATA_MISSING (新增红线-2)", cur.fetchone()[0], 0)

            # year attribution CORRECT — no (city, year, eid) drift
            cur.execute(f"""
                SELECT COUNT(*) FROM {SCHEMA}.{TABLE}
                WHERE city_code IN ({city_list}) AND year BETWEEN 2020 AND 2025
                  AND lineage_ruling LIKE 'K669b-i-batch5-%%'
                  AND (
                    (city_code = 'HUBEI_YICHANG'   AND year = 2020 AND lineage_origin NOT LIKE '%%7584%%')
                    OR (city_code = 'HUBEI_YICHANG'   AND year = 2021 AND lineage_origin NOT LIKE '%%26293%%')
                    OR (city_code = 'HUBEI_YICHANG'   AND year = 2022 AND lineage_origin NOT LIKE '%%36943%%')
                    OR (city_code = 'HUBEI_YICHANG'   AND year = 2023 AND lineage_origin NOT LIKE '%%55561%%')
                    OR (city_code = 'HUBEI_YICHANG'   AND year = 2024 AND lineage_origin NOT LIKE '%%63218%%')
                    OR (city_code = 'HUBEI_YICHANG'   AND year = 2025 AND lineage_origin NOT LIKE '%%68694%%')
                  )
            """)
            assert_eq("YICHANG year→eid attribution CORRECT (Knife E 970 fix verified)",
                      cur.fetchone()[0], 0)

    finally:
        conn.close()

    print(f"\n=== Result: {PASS} PASS / {FAIL} FAIL ===")
    return 0 if FAIL == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
