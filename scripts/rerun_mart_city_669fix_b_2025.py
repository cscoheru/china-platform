#!/usr/bin/env python3
"""
669fix-b-2025 mart apply — DROP+CREATE pattern with heredoc substitution
=============================================================================

knife 669fix-b-2025 (Path A 续刀 5/5) — zero-harvest path:
- Re-creates mart_city_timeseries with lineage_ruling 2025 attribution 改动
- rd12 CTE (real_data_669fix_2025) is empty (zero-harvest)
- K669fix-b-2025-2026-09-09 ruling 替代 K669b-2025-2026-09-08 (lineage_ruling branch)
- Heredoc substitution for 2022/2023/2024 CTE bodies (preserve prior real cells)
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
    """Replace CTE body for `real_data_669fix_{year}` via find/substring.

    Mart SQL has:
        real_data_669fix_{year} AS (
            SELECT * FROM (VALUES
        $(cat /tmp/669b/cte_{year}_body.txt)
            ) AS t(city_code, indicator_key, value)
        ),
    """
    prefix = f"real_data_669fix_{year} AS (\n    SELECT * FROM (VALUES\n"
    suffix = "\n    ) AS t(city_code, indicator_key, value)"

    start = content.find(prefix)
    if start == -1:
        raise RuntimeError(f"Failed to find CTE prefix for {year}")
    body_start = start + len(prefix)
    end = content.find(suffix, body_start)
    if end == -1:
        raise RuntimeError(f"Failed to find CTE suffix for {year}")
    body = body.rstrip().rstrip(",")
    return content[:body_start] + body + content[end:]


def main():
    print(f"=== knife 669fix-b-2025 mart apply (DROP+CREATE) ===")
    print(f"DB: {DB_HOST}:{DB_PORT}/{DB_NAME}")

    # 1. Read mart SQL
    with open(MART_SQL_PATH, encoding="utf-8") as f:
        sql_template = f.read()

    # 2. Substitute heredocs for 2022/2023/2024 CTE bodies
    #    2025 CTE has empty VALUES (zero-harvest), no heredoc
    for year in (2022, 2023, 2024):
        body_path = f"/tmp/669b/cte_{year}_body.txt"
        if not os.path.exists(body_path):
            raise RuntimeError(f"Missing CTE body file: {body_path}")
        with open(body_path) as f:
            body = f.read().rstrip("\n")
        sql_template = replace_body(sql_template, year, body)
        print(f"  ✓ Replaced heredoc cte_{year}_body.txt ({len(body)} chars)")

    # 3. Save for traceability
    out_path = "/tmp/669b/mart_city_timeseries_y2025.sql"
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(sql_template)
    print(f"  Updated mart SQL saved: {out_path}")

    # 4. DROP + CREATE
    conn = get_conn()
    try:
        with conn.cursor() as cur:
            print(f"  DROP TABLE IF EXISTS {TARGET_SCHEMA}.{MART_NAME}")
            cur.execute(f"DROP TABLE IF EXISTS {TARGET_SCHEMA}.{MART_NAME} CASCADE")

            print(f"  CREATE TABLE AS ({sql_template[:80]}...)")
            cur.execute(f"CREATE TABLE {TARGET_SCHEMA}.{MART_NAME} AS {sql_template}")
            print(f"  ✓ mart created")

        conn.commit()

        # 5. Sanity check
        with conn.cursor() as cur:
            cur.execute(f"SELECT COUNT(*) FROM {TARGET_SCHEMA}.{MART_NAME}")
            total = cur.fetchone()[0]
            cur.execute(f"SELECT COUNT(*) FROM {TARGET_SCHEMA}.{MART_NAME} WHERE value IS NOT NULL")
            real = cur.fetchone()[0]
            cur.execute(f"SELECT COUNT(DISTINCT lineage_ruling) FROM {TARGET_SCHEMA}.{MART_NAME}")
            rulings = cur.fetchone()[0]
            cur.execute(f"SELECT COUNT(*) FROM {TARGET_SCHEMA}.{MART_NAME} WHERE lineage_ruling = 'K669fix-b-2025-2026-09-09'")
            k2025 = cur.fetchone()[0]
            cur.execute(f"SELECT COUNT(*) FROM {TARGET_SCHEMA}.{MART_NAME} WHERE lineage_ruling = 'K669b-2025-2026-09-08'")
            kb2025 = cur.fetchone()[0]
            cur.execute(f"SELECT COUNT(*) FROM {TARGET_SCHEMA}.{MART_NAME} WHERE year=2025 AND value IS NOT NULL")
            y2025_real = cur.fetchone()[0]
            cur.execute(f"SELECT COUNT(*) FROM {TARGET_SCHEMA}.{MART_NAME} WHERE year=2025 AND status='DATA_MISSING'")
            y2025_miss = cur.fetchone()[0]
        print(f"\n=== Apply summary ===")
        print(f"  Total rows: {total}")
        print(f"  Real cells: {real}")
        print(f"  Ruling versions: {rulings}")
        print(f"  K669fix-b-2025-2026-09-09 cells: {k2025}")
        print(f"  K669b-2025-2026-09-08 cells (应=0): {kb2025}")
        print(f"  2025 real cells (应=0, zero-harvest): {y2025_real}")
        print(f"  2025 DATA_MISSING cells (应=290 = 29×10): {y2025_miss}")

    finally:
        conn.close()


if __name__ == "__main__":
    main()
