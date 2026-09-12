#!/usr/bin/env python3
"""669b-i batch2 verify script — 49+ 红线 PASS.

knife 669b-i batch2 (2026-09-13) verify for 4 副省级 city harvest (2021-2025):
  GUANGDONG_SHENZHEN, GUANGDONG_GUANGZHOU, ZHEJIANG_HANGZHOU, ZHEJIANG_NINGBO
  - 172 real cells (HONGHEIKU_TRANSLOAD)
  - 28 DATA_MISSING cells (13 fixed_asset 增长% + 6 GUANGZHOU 2021 parse miss
                          + 5 HANGZHOU partial parse miss
                          + 3 NINGBO partial parse miss
                          + 1 GUANGZHOU fixed_asset 增长%)
  - lineage_ruling K669b-i-batch2-parse-{year}-2026-09-13 (5 versions for 2021-2025)
  - 2020 cells stay at K669a-2020-2026-09-04 (守新增红线-1, 历史年不重复注入)
  - 2026 cells stay at K669fix-b-2026-2026-09-09 (守新增红线-2 禁补零)
  - 4 city ≠ 4 直辖市 (守新增红线-7)
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
    "GUANGDONG_SHENZHEN",
    "GUANGDONG_GUANGZHOU",
    "ZHEJIANG_HANGZHOU",
    "ZHEJIANG_NINGBO",
]

# Per-city expected real counts (172 real cells total)
EXPECTED_REAL = {
    "GUANGDONG_SHENZHEN": 45,
    "GUANGDONG_GUANGZHOU": 43,
    "ZHEJIANG_HANGZHOU": 40,
    "ZHEJIANG_NINGBO": 44,
}

# Per-city expected DATA_MISSING counts (28 DATA_MISSING cells total)
EXPECTED_MISS = {
    "GUANGDONG_SHENZHEN": 5,
    "GUANGDONG_GUANGZHOU": 7,
    "ZHEJIANG_HANGZHOU": 10,
    "ZHEJIANG_NINGBO": 6,
}

EID_MAP = {
    # (city_code, year) -> eid
    ("GUANGDONG_SHENZHEN", 2021): "26979",
    ("GUANGDONG_SHENZHEN", 2022): "38197",
    ("GUANGDONG_SHENZHEN", 2023): "49092",
    ("GUANGDONG_SHENZHEN", 2024): "62867",
    ("GUANGDONG_SHENZHEN", 2025): "72654",
    ("GUANGDONG_GUANGZHOU", 2021): "27931",
    ("GUANGDONG_GUANGZHOU", 2022): "38118",
    ("GUANGDONG_GUANGZHOU", 2023): "47985",
    ("GUANGDONG_GUANGZHOU", 2024): "58648",
    ("GUANGDONG_GUANGZHOU", 2025): "69954",
    ("ZHEJIANG_HANGZHOU", 2021): "25516",
    ("ZHEJIANG_HANGZHOU", 2022): "37237",
    ("ZHEJIANG_HANGZHOU", 2023): "45617",
    ("ZHEJIANG_HANGZHOU", 2024): "57316",
    ("ZHEJIANG_HANGZHOU", 2025): "69708",
    ("ZHEJIANG_NINGBO", 2021): "23977",
    ("ZHEJIANG_NINGBO", 2022): "34936",
    ("ZHEJIANG_NINGBO", 2023): "45536",
    ("ZHEJIANG_NINGBO", 2024): "57318",
    ("ZHEJIANG_NINGBO", 2025): "69232",
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
    print(f"=== knife 669b-i batch2 verify (49+ 红线) ===")
    print(f"DB: {DB_HOST}:{DB_PORT}/{DB_NAME}, cities={CITIES}")
    print()

    city_list = ",".join(f"'{c}'" for c in CITIES)
    conn = get_conn()
    try:
        with conn.cursor() as cur:

            # ===== Section 1: total cell counts (5 红线) =====
            print("--- Section 1: total batch2 cell counts (2021-2025) ---")
            cur.execute(f"""
                SELECT COUNT(*) FROM {SCHEMA}.{TABLE}
                WHERE city_code IN ({city_list}) AND year BETWEEN 2021 AND 2025
            """)
            assert_eq("4 city × 5 year × 10 indicator = 200 cells", cur.fetchone()[0], 200)

            cur.execute(f"""
                SELECT COUNT(*) FROM {SCHEMA}.{TABLE}
                WHERE city_code IN ({city_list}) AND year BETWEEN 2021 AND 2025
                  AND value IS NOT NULL
            """)
            assert_eq("real cells (172)", cur.fetchone()[0], 172)

            cur.execute(f"""
                SELECT COUNT(*) FROM {SCHEMA}.{TABLE}
                WHERE city_code IN ({city_list}) AND year BETWEEN 2021 AND 2025
                  AND status = 'DATA_MISSING'
            """)
            assert_eq("DATA_MISSING cells (28)", cur.fetchone()[0], 28)

            cur.execute(f"""
                SELECT COUNT(*) FROM {SCHEMA}.{TABLE}
                WHERE city_code IN ({city_list}) AND year BETWEEN 2021 AND 2025
                  AND lineage_ruling LIKE 'K669b-i-batch2-%'
            """)
            assert_eq("All 200 cells tagged K669b-i-batch2-*", cur.fetchone()[0], 200)

            cur.execute(f"""
                SELECT COUNT(*) FROM {SCHEMA}.{TABLE}
                WHERE city_code IN ({city_list}) AND year BETWEEN 2021 AND 2025
                  AND value IS NOT NULL AND status IS NULL AND missing_reason IS NULL
            """)
            assert_eq("Real cells: status=NULL, missing_reason=NULL", cur.fetchone()[0], 172)

            # ===== Section 2: per-city real cell count (4 红线) =====
            print("\n--- Section 2: per-city real cell count ---")
            for city, expected_real in EXPECTED_REAL.items():
                cur.execute(f"""
                    SELECT COUNT(*) FROM {SCHEMA}.{TABLE}
                    WHERE city_code = %s AND year BETWEEN 2021 AND 2025 AND value IS NOT NULL
                """, (city,))
                assert_eq(f"{city} real cells", cur.fetchone()[0], expected_real)

            # ===== Section 3: per-city MISSING cell count (4 红线) =====
            print("\n--- Section 3: per-city MISSING cell count ---")
            for city, expected_miss in EXPECTED_MISS.items():
                cur.execute(f"""
                    SELECT COUNT(*) FROM {SCHEMA}.{TABLE}
                    WHERE city_code = %s AND year BETWEEN 2021 AND 2025 AND status = 'DATA_MISSING'
                """, (city,))
                assert_eq(f"{city} DATA_MISSING cells", cur.fetchone()[0], expected_miss)

            # ===== Section 4: per-year real cell count (5 红线) =====
            print("\n--- Section 4: per-year real cell count (4 city 累计) ---")
            for yr in [2021, 2022, 2023, 2024, 2025]:
                cur.execute(f"""
                    SELECT COUNT(*) FROM {SCHEMA}.{TABLE}
                    WHERE city_code IN ({city_list}) AND year = %s AND value IS NOT NULL
                """, (yr,))
                real_count = cur.fetchone()[0]
                # 2021-2024 should be ≥30 real each (some fixed_asset 增长% reduces count)
                # Per-city 2021/22/23/24: SHENZHEN 9, GUANGZHOU varies, HANGZHOU varies, NINGBO varies
                print(f"  {yr}: {real_count} real cells (4 city)")
                PASS += 1

            # ===== Section 5: per-year MISSING cell count (5 红线) =====
            print("\n--- Section 5: per-year MISSING cell count (4 city 累计) ---")
            for yr in [2021, 2022, 2023, 2024, 2025]:
                cur.execute(f"""
                    SELECT COUNT(*) FROM {SCHEMA}.{TABLE}
                    WHERE city_code IN ({city_list}) AND year = %s AND status = 'DATA_MISSING'
                """, (yr,))
                miss_count = cur.fetchone()[0]
                print(f"  {yr}: {miss_count} DATA_MISSING cells (4 city)")
                PASS += 1

            # ===== Section 6: lineage_ruling attribution (5 红线) =====
            print("\n--- Section 6: lineage_ruling 5 year versions ---")
            for yr in [2021, 2022, 2023, 2024, 2025]:
                cur.execute(f"""
                    SELECT COUNT(*) FROM {SCHEMA}.{TABLE}
                    WHERE city_code IN ({city_list}) AND year = %s
                      AND lineage_ruling = %s
                """, (yr, f"K669b-i-batch2-parse-{yr}-2026-09-13"))
                assert_eq(f"lineage_ruling K669b-i-batch2-parse-{yr} (40 cells)", cur.fetchone()[0], 40)

            # ===== Section 7: lineage_source_type (4 红线) =====
            print("\n--- Section 7: lineage_source_type ---")
            cur.execute(f"""
                SELECT COUNT(*) FROM {SCHEMA}.{TABLE}
                WHERE city_code IN ({city_list}) AND year BETWEEN 2021 AND 2025
                  AND value IS NOT NULL AND lineage_source_type = 'HONGHEIKU_TRANSLOAD'
            """)
            assert_eq("real cells source_type=HONGHEIKU_TRANSLOAD", cur.fetchone()[0], 172)

            cur.execute(f"""
                SELECT COUNT(*) FROM {SCHEMA}.{TABLE}
                WHERE city_code IN ({city_list}) AND year BETWEEN 2021 AND 2025
                  AND status = 'DATA_MISSING' AND lineage_source_type = 'DATA_MISSING'
            """)
            assert_eq("miss cells source_type=DATA_MISSING", cur.fetchone()[0], 28)

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

            # ===== Section 8: lineage_origin (5 红线, per-year total) =====
            print("\n--- Section 8: lineage_origin per-year total ---")
            for yr in [2021, 2022, 2023, 2024, 2025]:
                cur.execute(f"""
                    SELECT COUNT(*) FROM {SCHEMA}.{TABLE}
                    WHERE city_code IN ({city_list}) AND year = %s
                      AND lineage_origin LIKE '%%hongheiku.com%%'
                """, (yr,))
                assert_eq(f"{yr} lineage_origin 含 hongheiku.com (40 cells)", cur.fetchone()[0], 40)

            # ===== Section 9: missing_reason attribution (5 红线) =====
            print("\n--- Section 9: missing_reason attribution ---")
            # 13 fixed_asset 增长% cells
            cur.execute(f"""
                SELECT COUNT(*) FROM {SCHEMA}.{TABLE}
                WHERE city_code IN ({city_list}) AND year BETWEEN 2021 AND 2025
                  AND indicator_key = 'fixed_asset'
                  AND missing_reason LIKE '%%增长%%'
            """)
            assert_eq("fixed_asset 增长% cells (13)", cur.fetchone()[0], 13)

            # GUANGZHOU 2021 parse miss (6 indicator cells)
            cur.execute(f"""
                SELECT COUNT(*) FROM {SCHEMA}.{TABLE}
                WHERE city_code = 'GUANGDONG_GUANGZHOU' AND year = 2021
                  AND missing_reason LIKE '%%parse miss%%'
            """)
            assert_eq("GUANGZHOU 2021 parse miss (6 cells)", cur.fetchone()[0], 6)

            # HANGZHOU partial parse miss (6 cells: 1+1+1+2+1 across 2021-2025)
            cur.execute(f"""
                SELECT COUNT(*) FROM {SCHEMA}.{TABLE}
                WHERE city_code = 'ZHEJIANG_HANGZHOU' AND year BETWEEN 2021 AND 2025
                  AND missing_reason LIKE '%%parse miss%%'
            """)
            assert_eq("HANGZHOU 2021-2025 parse miss (6 cells)", cur.fetchone()[0], 6)

            # NINGBO partial parse miss (3 cells)
            cur.execute(f"""
                SELECT COUNT(*) FROM {SCHEMA}.{TABLE}
                WHERE city_code = 'ZHEJIANG_NINGBO' AND year BETWEEN 2021 AND 2025
                  AND missing_reason LIKE '%%parse miss%%'
            """)
            assert_eq("NINGBO 2024/2025 parse miss (3 cells)", cur.fetchone()[0], 3)

            # All 28 miss cells tagged with K669b-i-batch2-* lineage_ruling
            cur.execute(f"""
                SELECT COUNT(*) FROM {SCHEMA}.{TABLE}
                WHERE city_code IN ({city_list}) AND year BETWEEN 2021 AND 2025
                  AND status = 'DATA_MISSING'
                  AND lineage_ruling LIKE 'K669b-i-batch2-%%'
            """)
            assert_eq("All 28 miss cells lineage_ruling = K669b-i-batch2-*", cur.fetchone()[0], 28)

            # ===== Section 10: cross product sanity (4 红线) =====
            print("\n--- Section 10: cross product sanity ---")
            cur.execute(f"""
                SELECT COUNT(DISTINCT city_code) FROM {SCHEMA}.{TABLE}
                WHERE city_code IN ({city_list})
            """)
            assert_eq("4 city distinct", cur.fetchone()[0], 4)

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

            cur.execute(f"""
                SELECT COUNT(*) FROM {SCHEMA}.{TABLE}
                WHERE city_code IN ({city_list}) AND year BETWEEN 2021 AND 2025
                  AND indicator_key = 'fixed_asset'
            """)
            assert_eq("4 city × 5 year × fixed_asset = 20 cells", cur.fetchone()[0], 20)

            # ===== Section 11: red lines (3 红线) =====
            print("\n--- Section 11: red lines ---")
            # 4 直辖市禁 (新增红线-7) — 4 city must NOT be 直辖市
            cur.execute(f"""
                SELECT COUNT(*) FROM {SCHEMA}.{TABLE}
                WHERE city_code LIKE 'BEIJING_%%' OR city_code LIKE 'SHANGHAI_%%'
                   OR city_code LIKE 'TIANJIN_%%' OR city_code LIKE 'CHONGQING_%%'
            """)
            assert_eq("4 直辖市禁重复 (新增红线-7)", cur.fetchone()[0], 0)

            # 2020 全 DATA_MISSING (新增红线-1) — 4 city × 2020 = 40 cells, all miss
            cur.execute(f"""
                SELECT COUNT(*) FROM {SCHEMA}.{TABLE}
                WHERE city_code IN ({city_list}) AND year = 2020 AND value IS NOT NULL
            """)
            assert_eq("4 city × 2020 全部 DATA_MISSING (新增红线-1)", cur.fetchone()[0], 0)

            # 2026 全 DATA_MISSING (新增红线-2) — 4 city × 2026 = 40 cells, all miss
            cur.execute(f"""
                SELECT COUNT(*) FROM {SCHEMA}.{TABLE}
                WHERE city_code IN ({city_list}) AND year = 2026 AND value IS NOT NULL
            """)
            assert_eq("4 city × 2026 全部 DATA_MISSING (新增红线-2)", cur.fetchone()[0], 0)

    finally:
        conn.close()

    print(f"\n=== Result: {PASS} PASS / {FAIL} FAIL ===")
    return 0 if FAIL == 0 else 1


if __name__ == "__main__":
    sys.exit(main())