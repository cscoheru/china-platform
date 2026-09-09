#!/usr/bin/env python3
"""
669fix-b-2024 mart apply — UPDATE-ONLY psycopg2 pattern (per 2022/2023 fix)
=============================================================================

Per 669fix-b-2022/2023 — does NOT DROP. Reads seed CSV, sets real values
directly via UPDATE for city×indicator×2024 matching lineage_ruling.
"""
import csv
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
SEED_CSV = "/Users/kjonekong/projects/china platform/source_registry/seed_hongheiku_city_timeseries_2024.csv"
RULING = "K669fix-b-2024-2026-09-09"


def get_conn():
    return psycopg2.connect(host=DB_HOST, port=DB_PORT, user=DB_USER,
                            password=DB_PASS, dbname=DB_NAME)


def main():
    print(f"=== knife 669fix-b-2024 mart apply (UPDATE-ONLY) ===")
    print(f"DB: {DB_HOST}:{DB_PORT}/{DB_NAME}, ruling={RULING}")

    # Read seed CSV
    real_rows = []
    with open(SEED_CSV, encoding="utf-8") as f:
        for r in csv.DictReader(f):
            if r["status"] == "HONGHEIKU_TRANSLOAD":
                real_rows.append((r["city_code"], r["indicator_key"], r["value"]))
    print(f"  Real cells in seed CSV: {len(real_rows)}")

    if not real_rows:
        print("  ✗ No real cells — aborting")
        sys.exit(1)

    conn = get_conn()
    updated = 0
    try:
        with conn.cursor() as cur:
            # First, ensure all 25 省会 × 10 indicator × 2024 rows have ruling K669fix-b-2024
            # (This was set by the mart SQL's CASE branch, but let's update only the real cells)
            for city_code, indicator_key, value in real_rows:
                cur.execute(f"""
                    UPDATE {TARGET_SCHEMA}.{MART_NAME}
                    SET value = %s::numeric,
                        status = NULL,
                        missing_reason = NULL,
                        lineage_source_type = 'HONGHEIKU_TRANSLOAD',
                        lineage_origin = 'tjgb.hongheiku.com/djs/' || %s,
                        lineage_ruling = %s
                    WHERE city_code = %s
                      AND indicator_key = %s
                      AND year = 2024
                """, (value, city_code, RULING, city_code, indicator_key))
                updated += cur.rowcount
        conn.commit()
        print(f"  ✓ Updated {updated} rows with real values")

        # Sanity check
        with conn.cursor() as cur:
            cur.execute(f"SELECT COUNT(*) FROM {TARGET_SCHEMA}.{MART_NAME} WHERE value IS NOT NULL")
            real_count = cur.fetchone()[0]
            cur.execute(f"SELECT COUNT(*) FROM {TARGET_SCHEMA}.{MART_NAME} WHERE year = 2024 AND value IS NOT NULL")
            y2024_real = cur.fetchone()[0]
            cur.execute(f"SELECT COUNT(*) FROM {TARGET_SCHEMA}.{MART_NAME} WHERE year = 2024 AND value IS NULL")
            y2024_miss = cur.fetchone()[0]
            cur.execute(f"SELECT COUNT(*) FROM {TARGET_SCHEMA}.{MART_NAME} WHERE lineage_ruling = %s AND value IS NOT NULL", (RULING,))
            ruling_real = cur.fetchone()[0]
            cur.execute(f"SELECT COUNT(*) FROM {TARGET_SCHEMA}.{MART_NAME} WHERE lineage_ruling = %s AND value IS NULL", (RULING,))
            ruling_miss = cur.fetchone()[0]
        print(f"\n=== Apply summary ===")
        print(f"  Total real cells: {real_count}")
        print(f"  2024 real:        {y2024_real}  (K669a 4 + K669fix-b-2024 122)")
        print(f"  2024 missing:     {y2024_miss}  (K669a 0 + K669fix-b-2024 128)")
        print(f"  K669fix-b-2024:   {ruling_real} real + {ruling_miss} missing")

    finally:
        conn.close()


if __name__ == "__main__":
    main()