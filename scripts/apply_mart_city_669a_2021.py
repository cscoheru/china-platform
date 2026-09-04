#!/usr/bin/env python3
"""
669a-2021 mart apply — real data harvest + 多刀 lineage ruling 守门
========================================================================

Per 663 Gap 1: dbt CLI 工具链与 Python 3.14 不兼容,
直接用 psycopg2 跑 SQL 应用 mart_city_timeseries (knife 669a-2021 real-data sub-knife).

State after 669a-2020 + 669a-2021:
  - 280 rows = 4 city × 10 indicator × 7 year (2020-2026)
  - real_cells = 26 (4 city × 10 indicator × 2021, of which 26 real + 14 DATA_MISSING)
  - DATA_MISSING = 254 (40 for 2020 + 14 for 2021 missing + 200 for 2022-2026)
  - ruling_versions = 3 (K669a-2020 for 2020 cells, K669a-2021 for 2021 cells,
                           'pending' for 2022-2025 cells)
"""

import os
import sys
from pathlib import Path
import psycopg2

DB_HOST = "127.0.0.1"
DB_PORT = 55440
DB_USER = "postgres"
DB_PASS = os.environ.get("DBT_DEV_PASS", "postgres")
DB_NAME = "cegr_test"
TARGET_SCHEMA = "cegr_mart"
MART_NAME = "mart_city_timeseries"

SQL_FILE = Path(__file__).parent.parent / "dbt" / "models" / "marts" / "mart_city_timeseries.sql"


def load_sql() -> str:
    """Load mart SQL and strip dbt jinja config + SQL comments."""
    if not SQL_FILE.exists():
        raise FileNotFoundError(f"mart SQL not found: {SQL_FILE}")
    text = SQL_FILE.read_text(encoding="utf-8")
    lines = text.split("\n")
    body_lines = []
    in_jinja = False
    for line in lines:
        if line.strip().startswith("{{"):
            in_jinja = True
            continue
        if in_jinja:
            if line.strip().startswith("}}"):
                in_jinja = False
            continue
        body_lines.append(line)
    body = "\n".join(body_lines).strip()
    cleaned = []
    for line in body.split("\n"):
        if line.strip().startswith("--"):
            continue
        cleaned.append(line)
    return "\n".join(cleaned).strip()


def apply_mart(conn) -> dict:
    """Drop and recreate mart_city_timeseries; return summary."""
    sql_body = load_sql()
    full_sql = f"""
DROP TABLE IF EXISTS {TARGET_SCHEMA}.{MART_NAME} CASCADE;
CREATE TABLE {TARGET_SCHEMA}.{MART_NAME} AS
{sql_body};
"""
    with conn.cursor() as cur:
        cur.execute(full_sql)
        cur.execute(f"SELECT COUNT(*) FROM {TARGET_SCHEMA}.{MART_NAME};")
        rows = cur.fetchone()[0]
        cur.execute(f"SELECT COUNT(DISTINCT city_code) FROM {TARGET_SCHEMA}.{MART_NAME};")
        cities = cur.fetchone()[0]
        cur.execute(f"SELECT COUNT(DISTINCT indicator_key) FROM {TARGET_SCHEMA}.{MART_NAME};")
        indicators = cur.fetchone()[0]
        cur.execute(f"SELECT COUNT(DISTINCT year) FROM {TARGET_SCHEMA}.{MART_NAME};")
        years = cur.fetchone()[0]
        cur.execute(f"SELECT COUNT(*) FROM {TARGET_SCHEMA}.{MART_NAME} WHERE value IS NOT NULL;")
        real = cur.fetchone()[0]
        cur.execute(f"SELECT COUNT(*) FROM {TARGET_SCHEMA}.{MART_NAME} WHERE status = 'DATA_MISSING';")
        missing = cur.fetchone()[0]
        cur.execute(f"SELECT COUNT(DISTINCT lineage_ruling) FROM {TARGET_SCHEMA}.{MART_NAME};")
        rulings = cur.fetchone()[0]
        # year breakdown
        cur.execute(f"SELECT year, COUNT(*) FROM {TARGET_SCHEMA}.{MART_NAME} GROUP BY year ORDER BY year;")
        year_rows = cur.fetchall()
        # 2021 real cells by city
        cur.execute(f"""
            SELECT city_code, COUNT(*) FROM {TARGET_SCHEMA}.{MART_NAME}
            WHERE year = 2021 AND value IS NOT NULL
            GROUP BY city_code ORDER BY city_code;
        """)
        city_2021_real = cur.fetchall()
    conn.commit()
    return {
        "rows": rows,
        "cities": cities,
        "indicators": indicators,
        "years": years,
        "real_cells": real,
        "data_missing_cells": missing,
        "ruling_versions": rulings,
        "by_year": year_rows,
        "city_2021_real": city_2021_real,
    }


def main():
    print(f"=== knife 669a-2021 mart apply (real-data harvest) ===")
    print(f"DB: {DB_HOST}:{DB_PORT}/{DB_NAME} schema={TARGET_SCHEMA}")
    print(f"SQL: {SQL_FILE}")
    print()
    conn = psycopg2.connect(host=DB_HOST, port=DB_PORT, user=DB_USER,
                            password=DB_PASS, dbname=DB_NAME)
    try:
        s = apply_mart(conn)
        print("mart apply OK:")
        print(f"  rows             = {s['rows']}           (expect 280 = 4 × 10 × 7)")
        print(f"  cities (distinct)= {s['cities']}         (expect 4)")
        print(f"  indicators       = {s['indicators']}    (expect 10)")
        print(f"  years            = {s['years']}         (expect 7 = 2020-2026)")
        print(f"  real_cells       = {s['real_cells']}    (expect 26 = 4 city × 10 indicator × 2021 minus 14 missing)")
        print(f"  DATA_MISSING     = {s['data_missing_cells']}  (expect 254 = 40[2020] + 14[2021 miss] + 200[2022-2026])")
        print(f"  ruling_versions  = {s['ruling_versions']}      (expect 3 = K669a-2020 + K669a-2021 + pending)")
        print()
        print("=== by year row count ===")
        for yr, cnt in s['by_year']:
            print(f"  year {yr}: {cnt} rows")
        print()
        print("=== 2021 real cells by city ===")
        for cc, cnt in s['city_2021_real']:
            print(f"  {cc}: {cnt} real cells")
    finally:
        conn.close()


if __name__ == "__main__":
    main()
