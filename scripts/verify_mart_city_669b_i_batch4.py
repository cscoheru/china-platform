#!/usr/bin/env python3
"""669b-i batch4 verify script — 33+ 红线 PASS.

knife 669b-i batch4 (2026-09-13) verify for 5 浙 satellite city harvest (2021-2025):
  ZHEJIANG_WENZHOU, ZHEJIANG_JINHUA, ZHEJIANG_SHAOXING,
  ZHEJIANG_JIAXING, ZHEJIANG_HUZHOU
  - 23 city-year coverage: WENZHOU(5)+JINHUA(5)+SHAOXING(5)+JIAXING(3)+HUZHOU(5) = 23
  - 230 seed cells (163 real HONGHEIKU_TRANSLOAD + 67 DATA_MISSING)
  - 230 mart cells for 5 city × 2021-2025 (4 new cities × 50 + JINHUA × 50 = 200 + 50 = 250? NO
    JIAXING × 30 only because 2024/2025 not in seed CSV → 4 × 50 + 1 × 50 - 20 (JIAXING 2024/2025) = 230)
  - lineage_ruling K669b-i-batch4-parse-{year}-2026-09-13 (5 versions for 2021-2025)
  - 2020 cells (JINHUA only) stay at K669a-2020-2026-09-04 (守新增红线-1)
  - 2026 cells (JINHUA only) stay at K669fix-b-2026-2026-09-09 (守新增红线-2 禁补零)
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
    "ZHEJIANG_WENZHOU",
    "ZHEJIANG_JINHUA",
    "ZHEJIANG_SHAOXING",
    "ZHEJIANG_JIAXING",
    "ZHEJIANG_HUZHOU",
]

# Per-city real cell counts (163 real cells total)
EXPECTED_REAL = {
    "ZHEJIANG_WENZHOU": 30,    # 2021: 6 + 2022: 6 + 2023: 6 + 2024: 6 + 2025: 6 = 30
    "ZHEJIANG_JINHUA": 39,     # 2021: 9 + 2022: 9 + 2023: 9 + 2024: 6 + 2025: 6 = 39
    "ZHEJIANG_SHAOXING": 24,   # 2021: 9 + 2022: 0 + 2023: 5 + 2024: 5 + 2025: 5 = 24
    "ZHEJIANG_JIAXING": 28,    # 2021: 9 + 2022: 9 + 2023: 10 = 28 (2024/2025 null)
    "ZHEJIANG_HUZHOU": 42,     # 2021: 9 + 2022: 9 + 2023: 9 + 2024: 8 + 2025: 7 = 42
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
    print(f"=== knife 669b-i batch4 verify (30+ 红线) ===")
    print(f"DB: {DB_HOST}:{DB_PORT}/{DB_NAME}, cities={CITIES}")
    print()

    city_list = ",".join(f"'{c}'" for c in CITIES)
    conn = get_conn()
    try:
        with conn.cursor() as cur:

            # ===== Section 1: total cell counts (5 红线) =====
            # 4 new cities (WENZHOU/HUZHOU/SHAOXING/JIAXING) have 50/50/50/30 cells
            # JINHUA (existing in mart) has 50 cells for 2021-2025
            # Total: 50+50+50+30+50 = 230 cells in 2021-2025
            print("--- Section 1: total batch4 cell counts (2021-2025) ---")
            cur.execute(f"""
                SELECT COUNT(*) FROM {SCHEMA}.{TABLE}
                WHERE city_code IN ({city_list}) AND year BETWEEN 2021 AND 2025
            """)
            assert_eq("5 city × 2021-2025 cells (4 new × 50/30 + JINHUA × 50 = 230)", cur.fetchone()[0], 230)

            cur.execute(f"""
                SELECT COUNT(*) FROM {SCHEMA}.{TABLE}
                WHERE city_code IN ({city_list}) AND year BETWEEN 2021 AND 2025
                  AND value IS NOT NULL
            """)
            assert_eq("real cells (163)", cur.fetchone()[0], 163)

            cur.execute(f"""
                SELECT COUNT(*) FROM {SCHEMA}.{TABLE}
                WHERE city_code IN ({city_list}) AND year BETWEEN 2021 AND 2025
                  AND status = 'DATA_MISSING'
            """)
            assert_eq("DATA_MISSING cells (67 = 230 - 163 real)", cur.fetchone()[0], 67)

            cur.execute(f"""
                SELECT COUNT(*) FROM {SCHEMA}.{TABLE}
                WHERE city_code IN ({city_list}) AND year BETWEEN 2021 AND 2025
                  AND lineage_ruling LIKE 'K669b-i-batch4-%'
            """)
            assert_eq("230 cells tagged K669b-i-batch4-* (matched seed)", cur.fetchone()[0], 230)

            cur.execute(f"""
                SELECT COUNT(*) FROM {SCHEMA}.{TABLE}
                WHERE city_code IN ({city_list}) AND year BETWEEN 2021 AND 2025
                  AND value IS NOT NULL AND status IS NULL AND missing_reason IS NULL
            """)
            assert_eq("Real cells: status=NULL, missing_reason=NULL", cur.fetchone()[0], 163)

            # ===== Section 2: per-city real cell count (5 红线) =====
            print("\n--- Section 2: per-city real cell count ---")
            for city, expected_real in EXPECTED_REAL.items():
                cur.execute(f"""
                    SELECT COUNT(*) FROM {SCHEMA}.{TABLE}
                    WHERE city_code = %s AND year BETWEEN 2021 AND 2025 AND value IS NOT NULL
                """, (city,))
                assert_eq(f"{city} real cells", cur.fetchone()[0], expected_real)

            # ===== Section 3: lineage_ruling attribution (5 红线) =====
            print("\n--- Section 3: lineage_ruling 5 year versions ---")
            for yr in [2021, 2022, 2023, 2024, 2025]:
                cur.execute(f"""
                    SELECT COUNT(*) FROM {SCHEMA}.{TABLE}
                    WHERE city_code IN ({city_list}) AND year = %s
                      AND lineage_ruling = %s
                """, (yr, f"K669b-i-batch4-parse-{yr}-2026-09-13"))
                # Per year tagged cells: 2021/2022/2023: 5 city × 10 = 50,
                # 2024: 4 city (JIAXING null) × 10 = 40, 2025: 4 × 10 = 40
                expected = {2021: 50, 2022: 50, 2023: 50, 2024: 40, 2025: 40}[yr]
                assert_eq(f"lineage_ruling K669b-i-batch4-parse-{yr} ({expected} cells)",
                          cur.fetchone()[0], expected)

            # ===== Section 4: lineage_source_type (4 红线) =====
            print("\n--- Section 4: lineage_source_type ---")
            cur.execute(f"""
                SELECT COUNT(*) FROM {SCHEMA}.{TABLE}
                WHERE city_code IN ({city_list}) AND year BETWEEN 2021 AND 2025
                  AND value IS NOT NULL AND lineage_source_type = 'HONGHEIKU_TRANSLOAD'
            """)
            assert_eq("real cells source_type=HONGHEIKU_TRANSLOAD", cur.fetchone()[0], 163)

            cur.execute(f"""
                SELECT COUNT(*) FROM {SCHEMA}.{TABLE}
                WHERE city_code IN ({city_list}) AND year BETWEEN 2021 AND 2025
                  AND status = 'DATA_MISSING' AND lineage_source_type = 'DATA_MISSING'
            """)
            assert_eq("miss cells source_type=DATA_MISSING", cur.fetchone()[0], 67)

            cur.execute(f"""
                SELECT COUNT(*) FROM {SCHEMA}.{TABLE}
                WHERE city_code IN ({city_list}) AND year BETWEEN 2021 AND 2025
                  AND value IS NOT NULL AND lineage_source_type != 'HONGHEIKU_TRANSLOAD'
            """)
            assert_eq("real cells NOT HONGHEIKU_TRANSLOAD = 0", cur.fetchone()[0], 0)

            cur.execute(f"""
                SELECT COUNT(*) FROM {SCHEMA}.{TABLE}
                WHERE city_code IN ({city_list}) AND year BETWEEN 2021 AND 2025
                  AND status = 'DATA_MISSING' AND (missing_reason IS NULL OR missing_reason = '')
            """)
            assert_eq("miss cells missing_reason 必填 = 0 missing", cur.fetchone()[0], 0)

            # ===== Section 5: lineage_origin per-year (5 红线) =====
            print("\n--- Section 5: lineage_origin per-year total ---")
            for yr in [2021, 2022, 2023, 2024, 2025]:
                cur.execute(f"""
                    SELECT COUNT(*) FROM {SCHEMA}.{TABLE}
                    WHERE city_code IN ({city_list}) AND year = %s
                      AND lineage_origin LIKE '%%hongheiku.com%%'
                """, (yr,))
                # 2021/2022/2023: 5 city × 10 = 50; 2024/2025: 4 city × 10 = 40
                expected = {2021: 50, 2022: 50, 2023: 50, 2024: 40, 2025: 40}[yr]
                assert_eq(f"{yr} lineage_origin 含 hongheiku.com ({expected} cells)",
                          cur.fetchone()[0], expected)

            # ===== Section 6: JIAXING 2024/2025 (守红线-3, hongheiku 0 entry, NOT yet seeded) =====
            print("\n--- Section 6: JIAXING 2024/2025 hongheiku 0 entry ---")
            # JIAXING 2024 + 2025 = 0 cells in mart (4 new cities were only inserted for years
            # in seed CSV; JIAXING 2024/2025 NOT in seed CSV because hongheiku has no entry).
            cur.execute(f"""
                SELECT COUNT(*) FROM {SCHEMA}.{TABLE}
                WHERE city_code = 'ZHEJIANG_JIAXING' AND year IN (2024, 2025)
            """)
            assert_eq("JIAXING 2024 + 2025 cells in mart (0 — not in seed CSV)",
                      cur.fetchone()[0], 0)

            cur.execute(f"""
                SELECT COUNT(*) FROM {SCHEMA}.{TABLE}
                WHERE city_code = 'ZHEJIANG_JIAXING' AND year IN (2024, 2025)
                  AND status = 'DATA_MISSING'
            """)
            assert_eq("JIAXING 2024 + 2025 DATA_MISSING (守新增红线-1, 禁补零)",
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
                WHERE city_code IN ({city_list}) AND year BETWEEN 2021 AND 2025
            """)
            assert_eq("5 year distinct (2021-2025)", cur.fetchone()[0], 5)

            # ===== Section 8: red lines (3 红线) =====
            print("\n--- Section 8: red lines ---")
            # 4 直辖市禁 (新增红线-7)
            cur.execute(f"""
                SELECT COUNT(*) FROM {SCHEMA}.{TABLE}
                WHERE city_code LIKE 'BEIJING_%%' OR city_code LIKE 'SHANGHAI_%%'
                   OR city_code LIKE 'TIANJIN_%%' OR city_code LIKE 'CHONGQING_%%'
            """)
            assert_eq("4 直辖市禁重复 (新增红线-7)", cur.fetchone()[0], 0)

            # 2020 全 DATA_MISSING (新增红线-1) — JINHUA had 2020 from prior knife, all DATA_MISSING
            cur.execute(f"""
                SELECT COUNT(*) FROM {SCHEMA}.{TABLE}
                WHERE city_code IN ({city_list}) AND year = 2020 AND value IS NOT NULL
            """)
            assert_eq("5 city × 2020 全部 DATA_MISSING (新增红线-1)", cur.fetchone()[0], 0)

            # 2026 全 DATA_MISSING (新增红线-2) — JINHUA had 2026 from prior knife, all DATA_MISSING
            cur.execute(f"""
                SELECT COUNT(*) FROM {SCHEMA}.{TABLE}
                WHERE city_code IN ({city_list}) AND year = 2026 AND value IS NOT NULL
            """)
            assert_eq("5 city × 2026 全部 DATA_MISSING (新增红线-2)", cur.fetchone()[0], 0)

    finally:
        conn.close()

    print(f"\n=== Result: {PASS} PASS / {FAIL} FAIL ===")
    return 0 if FAIL == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
