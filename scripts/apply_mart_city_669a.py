#!/usr/bin/env python3
"""
669a-2020 mart apply + 红线 verify
=================================

Per 663 Gap 1: dbt CLI 工具链与 Python 3.14 不兼容 (dbt-core-experimental-parser),
直接用 psycopg2 跑 SQL 应用 mart_city_timeseries (knife 669a-2020 zero-harvest)。

mart_city_timeseries.sql 是 dbt model (canonical source of truth); 本脚本等价执行
dbt run 的 materialized='table' 步骤,绕 dbt CLI 工具链。

Cross product: 4 city × 10 indicator × 7 year = 280 rows
All DATA_MISSING (hongheiku 城市维度 2020 缺文; 2021-2025 待 669a-2021+ harvest)
"""

import os
import sys
from pathlib import Path
import psycopg2
import psycopg2.extras

# dev postgres (per 663 receipt + dbt/profiles.yml dev target)
DB_HOST = "127.0.0.1"
DB_PORT = 55440
DB_USER = "postgres"
DB_PASS = os.environ.get("DBT_DEV_PASS", "postgres")
DB_NAME = "cegr_test"
TARGET_SCHEMA = "cegr_mart"
MART_NAME = "mart_city_timeseries"

# mart_city_timeseries.sql — canonical source (dbt model)
SQL_FILE = Path(__file__).parent.parent / "dbt" / "models" / "marts" / "mart_city_timeseries.sql"


def load_sql() -> str:
    """Load mart SQL and extract the SELECT body (dbt model is a SELECT)."""
    if not SQL_FILE.exists():
        raise FileNotFoundError(f"mart SQL not found: {SQL_FILE}")
    text = SQL_FILE.read_text(encoding="utf-8")
    # Strip dbt-specific jinja config block at top
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
    # Strip leading SQL comments (lines starting with --)
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
    conn.commit()
    return {
        "rows": rows,
        "cities": cities,
        "indicators": indicators,
        "years": years,
        "real_cells": real,
        "data_missing_cells": missing,
        "ruling_versions": rulings,
    }


def main():
    print(f"=== knife 669a-2020 mart apply ===")
    print(f"DB: {DB_HOST}:{DB_PORT}/{DB_NAME} schema={TARGET_SCHEMA}")
    print(f"SQL: {SQL_FILE}")
    print()
    conn = psycopg2.connect(host=DB_HOST, port=DB_PORT, user=DB_USER,
                            password=DB_PASS, dbname=DB_NAME)
    try:
        s = apply_mart(conn)
        print(f"mart apply OK:")
        print(f"  rows             = {s['rows']}           (expect 280 = 4 × 10 × 7)")
        print(f"  cities (distinct)= {s['cities']}         (expect 4)")
        print(f"  indicators       = {s['indicators']}    (expect 10)")
        print(f"  years            = {s['years']}         (expect 7 = 2020-2026)")
        print(f"  real_cells       = {s['real_cells']}    (expect 0, zero-harvest)")
        print(f"  DATA_MISSING     = {s['data_missing_cells']}  (expect 280)")
        print(f"  ruling_versions  = {s['ruling_versions']}      (expect 1 = K669a-2020-2026-09-04)")
    finally:
        conn.close()


if __name__ == "__main__":
    main()
