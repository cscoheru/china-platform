#!/usr/bin/env python3
"""
669fix-b-2024 mart apply — DROP+CREATE pattern with lineage preservation
=============================================================================

Re-creates mart_city_timeseries with 2024 harvest (K669fix-b-2024) data.
Mirrors 669fix-b-2023 apply pattern. Preserves previous real cells (594)
by re-running the SQL with updated CTE + rd11 LEFT JOIN.
"""
import os
import re
import sys
import psycopg2

DB_HOST = "127.0.0.1"
DB_PORT = 55440
DB_USER = "postgres"
DB_PASS = os.environ.get("DBT_DEV_PASS", "postgres")
DB_NAME = "cegr_test"
TARGET_SCHEMA = "cegr_mart"
MART_NAME = "mart_city_timeseries"
MART_SQL_PATH = "/Users/kjonekong/projects/china platform/dbt/models/marts/mart_city_timeseries.sql"


def get_conn():
    return psycopg2.connect(host=DB_HOST, port=DB_PORT, user=DB_USER,
                            password=DB_PASS, dbname=DB_NAME)


def replace_body(content: str, year: int, body: str) -> str:
    """Replace CTE body for `real_data_669fix_{year}` via find/substring."""
    prefix = f"real_data_669fix_{year} AS (\n    SELECT * FROM (VALUES\n"
    suffix = "\n    ) AS t(city_code, indicator_key, value)"

    start = content.find(prefix)
    if start == -1:
        raise RuntimeError(f"Failed to find CTE prefix for {year}")
    body_start = start + len(prefix)
    end = content.find(suffix, body_start)
    if end == -1:
        raise RuntimeError(f"Failed to find CTE suffix for {year}")
    # Strip trailing comma and newline from body
    body = body.rstrip().rstrip(",")
    # Replace content[body_start:end] (which is "$(cat /tmp/...)") with body
    return content[:body_start] + body + content[end:]


def main():
    print(f"=== knife 669fix-b-2024 mart apply ===")
    print(f"DB: {DB_HOST}:{DB_PORT}/{DB_NAME}")

    # 1. Read mart SQL and replace 2024 CTE body
    with open(MART_SQL_PATH, encoding="utf-8") as f:
        sql_template = f.read()

    # Need to also keep 2022 + 2023 body intact (preserve rd9/rd10 prior real cells)
    # Read existing cte bodies for all years present in mart SQL
    for year in (2022, 2023, 2024):
        with open(f"/tmp/669b/cte_{year}_body.txt", encoding="utf-8") as f:
            body = f.read().rstrip("\n")
        sql_template = replace_body(sql_template, year, body)

    # 2. Save updated SQL (for traceability)
    with open("/tmp/669b/mart_city_timeseries_y2024.sql", "w", encoding="utf-8") as f:
        f.write(sql_template)
    print(f"  Updated mart SQL saved: /tmp/669b/mart_city_timeseries_y2024.sql")

    # 3. DROP + CREATE
    conn = get_conn()
    try:
        with conn.cursor() as cur:
            print(f"  DROP TABLE IF EXISTS {TARGET_SCHEMA}.{MART_NAME}")
            cur.execute(f"DROP TABLE IF EXISTS {TARGET_SCHEMA}.{MART_NAME} CASCADE")

            print(f"  CREATE TABLE AS ({sql_template[:80]}...)")
            cur.execute(f"CREATE TABLE {TARGET_SCHEMA}.{MART_NAME} AS {sql_template}")
            print(f"  ✓ mart created")

        conn.commit()

        # 4. Quick sanity check
        with conn.cursor() as cur:
            cur.execute(f"SELECT COUNT(*) FROM {TARGET_SCHEMA}.{MART_NAME}")
            total = cur.fetchone()[0]
            cur.execute(f"SELECT COUNT(*) FROM {TARGET_SCHEMA}.{MART_NAME} WHERE value IS NOT NULL")
            real = cur.fetchone()[0]
            cur.execute(f"SELECT COUNT(DISTINCT lineage_ruling) FROM {TARGET_SCHEMA}.{MART_NAME}")
            rulings = cur.fetchone()[0]
        print(f"\n=== Apply summary ===")
        print(f"  Total rows: {total}")
        print(f"  Real cells: {real}")
        print(f"  Ruling versions: {rulings}")

    finally:
        conn.close()


if __name__ == "__main__":
    main()