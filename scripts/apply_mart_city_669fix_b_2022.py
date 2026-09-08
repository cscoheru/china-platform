#!/usr/bin/env python3
"""
669fix-b-2022 mart apply — psychopg2 UPDATE-ONLY (no DROP) — v2 fixed
=============================================================================

knife 669fix-b-2022 sub-knife (Path A 续刀 2/5):
- 23 city × 2022 harvest (22 fetched + GUANGXI_NANNING missing + TAIWAN_TAIPEI missing)
- 136 HONGHEIKU_TRANSLOAD + 114 DATA_MISSING (守红线-3: 不手填)

Pattern: 2021 K669fix-b-2021 lineage convention
  - real cells:     lineage_source_type = 'HONGHEIKU_TRANSLOAD'
  - missing cells:  lineage_source_type = 'DATA_MISSING', lineage_origin = 'none'
"""
import os
import sys
import csv
from pathlib import Path
import psycopg2

SEED_CSV_PATH = Path("/Users/kjonekong/projects/china platform/source_registry/seed_hongheiku_city_timeseries_2022.csv")

DB_HOST = "127.0.0.1"
DB_PORT = 55440
DB_USER = "postgres"
DB_PASS = os.environ.get("DBT_DEV_PASS", "postgres")
DB_NAME = "cegr_test"


def get_conn():
    return psycopg2.connect(host=DB_HOST, port=DB_PORT, user=DB_USER,
                            password=DB_PASS, dbname=DB_NAME)


def main():
    print(f"=== knife 669fix-b-2022 mart apply (UPDATE-ONLY v2 fixed) ===")
    print(f"Seed CSV: {SEED_CSV_PATH}")

    conn = get_conn()
    real_count = 0
    miss_count = 0
    fixed_asset_pct = 0
    try:
        with conn.cursor() as cur:
            with open(SEED_CSV_PATH, "r", encoding="utf-8") as f:
                reader = csv.DictReader(f)
                for r in reader:
                    city = r["city_code"]
                    ind = r["indicator_key"]
                    val = r["value"]
                    status = r["status"]
                    missing_reason = r["missing_reason"]
                    source_url = r["source_url"]
                    eid = r["bulletic_eid"]

                    if status == "HONGHEIKU_TRANSLOAD" and val:
                        # Real cell: HONGHEIKU_TRANSLOAD
                        cur.execute("""
                            UPDATE cegr_mart.mart_city_timeseries
                            SET value = %s,
                                status = 'HONGHEIKU_TRANSLOAD',
                                lineage_origin = %s,
                                lineage_ruling = 'K669fix-b-2022-2026-09-08',
                                lineage_source_type = 'HONGHEIKU_TRANSLOAD'
                            WHERE city_code = %s AND indicator_key = %s AND year = 2022;
                        """, (float(val), source_url, city, ind))
                        real_count += 1
                    elif "增长%" in missing_reason:
                        fixed_asset_pct += 1
                        cur.execute("""
                            UPDATE cegr_mart.mart_city_timeseries
                            SET value = NULL,
                                status = 'DATA_MISSING',
                                missing_reason = %s,
                                lineage_origin = 'none',
                                lineage_ruling = 'K669fix-b-2022-2026-09-08',
                                lineage_source_type = 'DATA_MISSING'
                            WHERE city_code = %s AND indicator_key = %s AND year = 2022;
                        """, (missing_reason, city, ind))
                        miss_count += 1
                    elif city in ('GUANGXI_NANNING', 'TAIWAN_TAIPEI') or "tag 页" in missing_reason:
                        cur.execute("""
                            UPDATE cegr_mart.mart_city_timeseries
                            SET value = NULL,
                                status = 'DATA_MISSING',
                                missing_reason = %s,
                                lineage_origin = 'none',
                                lineage_ruling = 'K669fix-b-2022-2026-09-08',
                                lineage_source_type = 'DATA_MISSING'
                            WHERE city_code = %s AND indicator_key = %s AND year = 2022;
                        """, (missing_reason, city, ind))
                        miss_count += 1
                    else:
                        # Default: bulletin 无 indicator 数据 / parser 未匹配
                        cur.execute("""
                            UPDATE cegr_mart.mart_city_timeseries
                            SET value = NULL,
                                status = 'DATA_MISSING',
                                missing_reason = %s,
                                lineage_origin = 'none',
                                lineage_ruling = 'K669fix-b-2022-2026-09-08',
                                lineage_source_type = 'DATA_MISSING'
                            WHERE city_code = %s AND indicator_key = %s AND year = 2022;
                        """, (missing_reason, city, ind))
                        miss_count += 1

        conn.commit()

        print(f"\n=== Apply summary ===")
        print(f"  Real cells (HONGHEIKU_TRANSLOAD): {real_count}")
        print(f"  DATA_MISSING cells: {miss_count}")
        print(f"    - fixed_asset % growth: {fixed_asset_pct}")

        with conn.cursor() as cur:
            cur.execute("""
                SELECT
                    COUNT(*) AS total,
                    COUNT(*) FILTER (WHERE value IS NOT NULL) AS real_cells,
                    COUNT(DISTINCT city_code) AS cities,
                    COUNT(DISTINCT indicator_key) AS indicators,
                    COUNT(DISTINCT year) AS years,
                    COUNT(*) FILTER (WHERE year = 2022 AND value IS NOT NULL) AS y2022_real,
                    COUNT(*) FILTER (WHERE year = 2022 AND value IS NULL) AS y2022_missing,
                    COUNT(DISTINCT lineage_ruling) AS ruling_versions,
                    COUNT(*) FILTER (WHERE lineage_source_type = 'HONGHEIKU_TRANSLOAD') AS hk_total
                FROM cegr_mart.mart_city_timeseries;
            """)
            row = cur.fetchone()
            print(f"\n=== mart state after apply ===")
            print(f"  total: {row[0]}")
            print(f"  real_cells: {row[1]}")
            print(f"  cities: {row[2]}")
            print(f"  indicators: {row[3]}")
            print(f"  years: {row[4]}")
            print(f"  2022 real cells: {row[5]}")
            print(f"  2022 DATA_MISSING: {row[6]}")
            print(f"  ruling versions: {row[7]}")
            print(f"  HONGHEIKU_TRANSLOAD total: {row[8]}")
    finally:
        conn.close()


if __name__ == "__main__":
    main()