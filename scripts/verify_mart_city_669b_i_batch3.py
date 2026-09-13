#!/usr/bin/env python3
"""669b-i batch3 verify script — 30+ 红线 PASS.

knife 669b-i batch3 (2026-09-13) verify for 5 粤 satellite city harvest (2021-2025):
  GUANGDONG_FOSHAN, GUANGDONG_ZHUHAI, GUANGDONG_HUIZHOU,
  GUANGDONG_JIANGMEN, GUANGDONG_ZHANJIANG
  - 22 city-year coverage: FOSHAN(5)+ZHUHAI(3)+HUIZHOU(5)+JIANGMEN(4)+ZHANJIANG(5) = 22
  - 220 seed cells (45 real HONGHEIKU_TRANSLOAD + 175 DATA_MISSING)
  - 250 total mart cells for 5 city × 2021-2025 (45 real + 205 DATA_MISSING)
  - 30 cells pre-existing DATA_MISSING stay (ZHUHAI 2023/2025 + JIANGMEN 2025)
  - lineage_ruling K669b-i-batch3-parse-{year}-2026-09-13 (5 versions for 2021-2025)
  - 2020 cells stay at K669a-2020-2026-09-04 (守新增红线-1, 历史年不重复注入)
  - 2026 cells stay at K669fix-b-2026-2026-09-09 (守新增红线-2 禁补零)
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
    "GUANGDONG_FOSHAN",
    "GUANGDONG_ZHUHAI",
    "GUANGDONG_HUIZHOU",
    "GUANGDONG_JIANGMEN",
    "GUANGDONG_ZHANJIANG",
]

# Per-city real cell counts (45 real cells total)
EXPECTED_REAL = {
    "GUANGDONG_FOSHAN": 0,    # all 5 years MISSING
    "GUANGDONG_ZHUHAI": 0,    # all 3 years (2021/22/24) MISSING
    "GUANGDONG_HUIZHOU": 9,   # 2021 only
    "GUANGDONG_JIANGMEN": 10, # 2023 only (all 10 indicators)
    "GUANGDONG_ZHANJIANG": 26,  # 2023: 9 + 2024: 8 + 2025: 9
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
    print(f"=== knife 669b-i batch3 verify (30+ 红线) ===")
    print(f"DB: {DB_HOST}:{DB_PORT}/{DB_NAME}, cities={CITIES}")
    print()

    city_list = ",".join(f"'{c}'" for c in CITIES)
    conn = get_conn()
    try:
        with conn.cursor() as cur:

            # ===== Section 1: total cell counts (5 红线) =====
            print("--- Section 1: total batch3 cell counts (2021-2025) ---")
            cur.execute(f"""
                SELECT COUNT(*) FROM {SCHEMA}.{TABLE}
                WHERE city_code IN ({city_list}) AND year BETWEEN 2021 AND 2025
            """)
            assert_eq("5 city × 5 year × 10 indicator = 250 cells", cur.fetchone()[0], 250)

            cur.execute(f"""
                SELECT COUNT(*) FROM {SCHEMA}.{TABLE}
                WHERE city_code IN ({city_list}) AND year BETWEEN 2021 AND 2025
                  AND value IS NOT NULL
            """)
            assert_eq("real cells (45)", cur.fetchone()[0], 45)

            cur.execute(f"""
                SELECT COUNT(*) FROM {SCHEMA}.{TABLE}
                WHERE city_code IN ({city_list}) AND year BETWEEN 2021 AND 2025
                  AND status = 'DATA_MISSING'
            """)
            assert_eq("DATA_MISSING cells (205 = 250 - 45 real)", cur.fetchone()[0], 205)

            cur.execute(f"""
                SELECT COUNT(*) FROM {SCHEMA}.{TABLE}
                WHERE city_code IN ({city_list}) AND year BETWEEN 2021 AND 2025
                  AND lineage_ruling LIKE 'K669b-i-batch3-%'
            """)
            assert_eq("220 cells tagged K669b-i-batch3-* (matched seed)", cur.fetchone()[0], 220)

            cur.execute(f"""
                SELECT COUNT(*) FROM {SCHEMA}.{TABLE}
                WHERE city_code IN ({city_list}) AND year BETWEEN 2021 AND 2025
                  AND value IS NOT NULL AND status IS NULL AND missing_reason IS NULL
            """)
            assert_eq("Real cells: status=NULL, missing_reason=NULL", cur.fetchone()[0], 45)

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
                """, (yr, f"K669b-i-batch3-parse-{yr}-2026-09-13"))
                # 2021: 5+3+5+4+5 = 22 cells (real), only 9 (HUIZHOU 9 real). Wait actually...
                # lineage_ruling tagged all 220 cells, not just real.
                # For year=2021: 5 cities have 2021 eid, so 5 city × 10 ind = 50 cells tagged.
                # For year=2022: 5 cities, 50 cells.
                # For year=2023: 4 cities (ZHUHAI miss), 40 cells.
                # For year=2024: 5 cities, 50 cells.
                # For year=2025: 3 cities (FOSHAN+ZHUHAI+JIANGMEN miss), 30 cells.
                expected = {2021: 50, 2022: 50, 2023: 40, 2024: 50, 2025: 30}[yr]
                assert_eq(f"lineage_ruling K669b-i-batch3-parse-{yr} ({expected} cells)",
                          cur.fetchone()[0], expected)

            # ===== Section 4: lineage_source_type (4 红线) =====
            print("\n--- Section 4: lineage_source_type ---")
            cur.execute(f"""
                SELECT COUNT(*) FROM {SCHEMA}.{TABLE}
                WHERE city_code IN ({city_list}) AND year BETWEEN 2021 AND 2025
                  AND value IS NOT NULL AND lineage_source_type = 'HONGHEIKU_TRANSLOAD'
            """)
            assert_eq("real cells source_type=HONGHEIKU_TRANSLOAD", cur.fetchone()[0], 45)

            cur.execute(f"""
                SELECT COUNT(*) FROM {SCHEMA}.{TABLE}
                WHERE city_code IN ({city_list}) AND year BETWEEN 2021 AND 2025
                  AND status = 'DATA_MISSING' AND lineage_source_type = 'DATA_MISSING'
            """)
            assert_eq("miss cells source_type=DATA_MISSING", cur.fetchone()[0], 205)

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

            # ===== Section 5: lineage_origin (5 红线, per-year total) =====
            print("\n--- Section 5: lineage_origin per-year total ---")
            for yr in [2021, 2022, 2023, 2024, 2025]:
                cur.execute(f"""
                    SELECT COUNT(*) FROM {SCHEMA}.{TABLE}
                    WHERE city_code IN ({city_list}) AND year = %s
                      AND lineage_origin LIKE '%%hongheiku.com%%'
                """, (yr,))
                # All 5 city × 10 indicator = 50 cells per year have hongheiku.com in
                # lineage_origin (220 from batch3 + 30 pre-existing from initial mart setup).
                assert_eq(f"{yr} lineage_origin 含 hongheiku.com (50 cells)",
                          cur.fetchone()[0], 50)

            # ===== Section 6: pre-existing 30 DATA_MISSING cells (守红线-3) =====
            print("\n--- Section 6: 30 pre-existing DATA_MISSING cells (hongheiku 0 entry) ---")
            # ZHUHAI 2023 (10 cells) + ZHUHAI 2025 (10 cells) + JIANGMEN 2025 (10 cells) = 30 cells
            # These should have lineage_ruling NOT LIKE 'K669b-i-batch3-%'
            cur.execute(f"""
                SELECT COUNT(*) FROM {SCHEMA}.{TABLE}
                WHERE city_code = 'GUANGDONG_ZHUHAI' AND year IN (2023, 2025)
                  AND status = 'DATA_MISSING'
            """)
            assert_eq("ZHUHAI 2023 + 2025 pre-existing DATA_MISSING (20 cells)",
                      cur.fetchone()[0], 20)

            cur.execute(f"""
                SELECT COUNT(*) FROM {SCHEMA}.{TABLE}
                WHERE city_code = 'GUANGDONG_JIANGMEN' AND year = 2025
                  AND status = 'DATA_MISSING'
            """)
            assert_eq("JIANGMEN 2025 pre-existing DATA_MISSING (10 cells)",
                      cur.fetchone()[0], 10)

            cur.execute(f"""
                SELECT COUNT(*) FROM {SCHEMA}.{TABLE}
                WHERE city_code IN ({city_list}) AND year BETWEEN 2021 AND 2025
                  AND status = 'DATA_MISSING'
                  AND lineage_ruling NOT LIKE 'K669b-i-batch3-%%'
            """)
            assert_eq("30 pre-existing miss cells NOT tagged with batch3 ruling",
                      cur.fetchone()[0], 30)

            # ===== Section 7: cross product sanity (4 红线) =====
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

            # 2020 全 DATA_MISSING (新增红线-1)
            cur.execute(f"""
                SELECT COUNT(*) FROM {SCHEMA}.{TABLE}
                WHERE city_code IN ({city_list}) AND year = 2020 AND value IS NOT NULL
            """)
            assert_eq("5 city × 2020 全部 DATA_MISSING (新增红线-1)", cur.fetchone()[0], 0)

            # 2026 全 DATA_MISSING (新增红线-2)
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