#!/usr/bin/env python3
"""
669fix-b-2023 mart rerun — DROP TABLE + CREATE TABLE AS WITH (dbt CLI 旁路, per 663 Gap 1)
=============================================================================
"""
import os
from pathlib import Path
import psycopg2

DB_HOST = "127.0.0.1"
DB_PORT = 55440
DB_USER = "postgres"
DB_PASS = os.environ.get("DBT_DEV_PASS", "postgres")
DB_NAME = "cegr_test"
MART_PATH = Path("/Users/kjonekong/projects/china platform/dbt/models/marts/mart_city_timeseries.sql")
CTE_2023_BODY = Path("/tmp/669b/cte_2023_body.txt")


def main():
    sql_text = MART_PATH.read_text(encoding="utf-8")
    cte_2022 = Path("/tmp/669b/cte_2022_body.txt").read_text(encoding="utf-8").rstrip().rstrip(",")
    cte_2023 = CTE_2023_BODY.read_text(encoding="utf-8").rstrip().rstrip(",")
    # Replace BOTH heredoc markers
    sql_with_cte = sql_text
    sql_with_cte = sql_with_cte.replace("$(cat /tmp/669b/cte_2022_body.txt)", cte_2022)
    sql_with_cte = sql_with_cte.replace("$(cat /tmp/669b/cte_2023_body.txt)", cte_2023)
    if cte_2023 not in sql_with_cte or cte_2022 not in sql_with_cte:
        print("ERROR: CTE body not inserted into mart SQL")
        return

    create_table_sql = "CREATE TABLE cegr_mart.mart_city_timeseries AS\n" + sql_with_cte

    conn = psycopg2.connect(host=DB_HOST, port=DB_PORT, user=DB_USER,
                            password=DB_PASS, dbname=DB_NAME)
    try:
        with conn.cursor() as cur:
            cur.execute("DROP TABLE IF EXISTS cegr_mart.mart_city_timeseries CASCADE;")
            print("✓ DROP TABLE mart_city_timeseries")
        conn.commit()

        with conn.cursor() as cur:
            cur.execute(create_table_sql)
        conn.commit()
        print("✓ CREATE TABLE mart_city_timeseries AS WITH...SELECT")

        with conn.cursor() as cur:
            cur.execute("SELECT COUNT(*) FROM cegr_mart.mart_city_timeseries;")
            row_count = cur.fetchone()[0]
            print(f"  Rows inserted: {row_count}")
            cur.execute("SELECT COUNT(*) FILTER (WHERE value IS NOT NULL) FROM cegr_mart.mart_city_timeseries;")
            real_count = cur.fetchone()[0]
            print(f"  Real cells (pre-apply): {real_count}")
    finally:
        conn.close()


if __name__ == "__main__":
    main()