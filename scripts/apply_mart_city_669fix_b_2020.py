#!/usr/bin/env python3
"""
669fix-b-2020 mart apply — 25 省会 × 2020 (161/250 real, 64%)
====================================================================

Per 663 Gap 1: dbt CLI 工具链与 Python 3.14 不兼容,
直接用 psycopg2 跑 SQL 应用 mart_city_timeseries (knife 669fix-b-2020 sub-knife).

State after 669a-2020/2021/2022/2023/2024/2025 + 669b-2025 + 669fix-b-2020:
  - 2030 rows = 29 city × 10 indicator × 7 year (2020-2026)
  - 161 real cells 增量 (24 city 公告 + 161 absolute-value cells; 19 fixed_asset % growth excluded)
  - 89 DATA_MISSING 增量:
    - 10 TAIWAN (hongheiku 无 entry)
    - 20 JIANGXI/SHANXI image-only (无 OCR 范围)
    - 19 fixed_asset 增长% (无绝对值, per 669a-2021 §2 红线-3)
    - 40 城市级公报未列指标 (守新增红线-3 不手填)
  - Previous real cells = 154 (post-669b-2025)
  - New total real cells = 154 + 161 = 315
  - New total DATA_MISSING = 1715
  - lineage_ruling attribution:
    - K669a-2020-2026-09-04: 40 missing cells (4 669a cities × 10 indicator)
    - K669fix-b-2020-2026-09-08: 161 real + 89 missing (25 省会 全 attribution)
"""

import os
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
    in_j = False
    for line in lines:
        if line.strip().startswith("{{"):
            in_j = True
            continue
        if in_j:
            if line.strip().startswith("}}"):
                in_j = False
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
        # 2020 real by ruling (K669fix-b-2020 expected)
        cur.execute(f"""
            SELECT lineage_ruling, COUNT(*) FROM {TARGET_SCHEMA}.{MART_NAME}
            WHERE year = 2020 AND value IS NOT NULL
            GROUP BY lineage_ruling ORDER BY lineage_ruling;
        """)
        y2020_real_by_ruling = cur.fetchall()
        # 2020 real cells count
        cur.execute(f"""
            SELECT COUNT(*) FROM {TARGET_SCHEMA}.{MART_NAME}
            WHERE year = 2020 AND value IS NOT NULL;
        """)
        y2020_real = cur.fetchone()[0]
        # 2020 DATA_MISSING breakdown
        cur.execute(f"""
            SELECT lineage_ruling, COUNT(*) FROM {TARGET_SCHEMA}.{MART_NAME}
            WHERE year = 2020 AND value IS NULL
            GROUP BY lineage_ruling ORDER BY lineage_ruling;
        """)
        y2020_missing_by_ruling = cur.fetchall()
        # 2026 全 DATA_MISSING (守红线-2)
        cur.execute(f"""
            SELECT COUNT(*) FROM {TARGET_SCHEMA}.{MART_NAME}
            WHERE year = 2026 AND value IS NOT NULL;
        """)
        y2026_real = cur.fetchone()[0]
        # 4 直辖市禁 (红线-7)
        cur.execute(f"""
            SELECT COUNT(*) FROM {TARGET_SCHEMA}.{MART_NAME}
            WHERE city_code LIKE 'BEIJING_%' OR city_code LIKE 'SHANGHAI_%'
               OR city_code LIKE 'TIANJIN_%' OR city_code LIKE 'CHONGQING_%';
        """)
        direct_cities = cur.fetchone()[0]
        # HONGHEIKU_TRANSLOAD 数量
        cur.execute(f"""
            SELECT COUNT(*) FROM {TARGET_SCHEMA}.{MART_NAME}
            WHERE lineage_source_type = 'HONGHEIKU_TRANSLOAD';
        """)
        hk_transload = cur.fetchone()[0]
        # 2020 城市覆盖 (24 city real + 1 TAIWAN miss)
        cur.execute(f"""
            SELECT COUNT(DISTINCT city_code) FROM {TARGET_SCHEMA}.{MART_NAME}
            WHERE year = 2020 AND value IS NOT NULL;
        """)
        y2020_cities_real = cur.fetchone()[0]
    conn.commit()
    return {
        "rows": rows,
        "cities": cities,
        "indicators": indicators,
        "years": years,
        "real_cells": real,
        "data_missing_cells": missing,
        "ruling_versions": rulings,
        "y2020_real": y2020_real,
        "y2020_real_by_ruling": y2020_real_by_ruling,
        "y2020_missing_by_ruling": y2020_missing_by_ruling,
        "y2020_cities_real": y2020_cities_real,
        "y2026_real": y2026_real,
        "direct_cities": direct_cities,
        "hk_transload": hk_transload,
    }


def main():
    print(f"=== knife 669fix-b-2020 mart apply (25 省会 × 2020, 161/250 real = 64%) ===")
    print(f"DB: {DB_HOST}:{DB_PORT}/{DB_NAME} schema={TARGET_SCHEMA}")
    print(f"SQL: {SQL_FILE}")
    print()
    conn = psycopg2.connect(host=DB_HOST, port=DB_PORT, user=DB_USER,
                            password=DB_PASS, dbname=DB_NAME)
    try:
        s = apply_mart(conn)
        print("mart apply OK:")
        print(f"  rows                = {s['rows']}    (expect 2030 = 29 × 10 × 7)")
        print(f"  cities (distinct)   = {s['cities']}    (expect 29 = 4 669a + 25 669b)")
        print(f"  indicators          = {s['indicators']}   (expect 10)")
        print(f"  years               = {s['years']}    (expect 7 = 2020-2026)")
        print(f"  real_cells          = {s['real_cells']}    (expect 315 = 154 prev + 161 669fix-b-2020)")
        print(f"  DATA_MISSING        = {s['data_missing_cells']}    (expect 1715 = 2030 - 315)")
        print(f"  ruling_versions     = {s['ruling_versions']}    (expect 9 = 8 prev + K669fix-b-2020)")
        print(f"  4 直辖市禁 (红线-7) = {s['direct_cities']}    (expect 0)")
        print(f"  HONGHEIKU_TRANSLOAD = {s['hk_transload']}    (expect 315 = same as real_cells)")
        print(f"  2020 real cells     = {s['y2020_real']}    (expect 161 = 24 city 公告 - 19 fixed_asset % growth)")
        print(f"  2020 real cities    = {s['y2020_cities_real']}    (expect 22 city 至少 1 real cell, TAIWAN 0)")
        print(f"  2026 real cells     = {s['y2026_real']}    (expect 0, 守红线-2)")
        print()
        print("=== 2020 real cells by ruling (K669fix-b-2020 expected) ===")
        for ruling, cnt in s['y2020_real_by_ruling']:
            print(f"  {ruling}: {cnt} real cells")
        print()
        print("=== 2020 missing cells by ruling ===")
        for ruling, cnt in s['y2020_missing_by_ruling']:
            print(f"  {ruling}: {cnt} missing cells")
        print()
        print("=== Decision (knife 669fix-b-2020) ===")
        print("  25 省会 × 2020 = 161/250 real (64%)")
        print("  来源: hongheiku /{eid}.html (2020 root pattern, 24 city)")
        print("  + 4 PDF bulletins (ANHUI 719, SICHUAN 1460, GANSU 949, QINGHAI 11065)")
        print("  守新增红线-3: 增长% 不手填, 缺失 indicator 不补零")
        print("  - 19 fixed_asset 增长% excluded from rd7 CTE → DATA_MISSING (per 669a-2021 §2)")
        print("  - 22 city ≥1 real cell; TAIWAN/JIANGXI/SHANXI 全 miss (守红线-3)")
    finally:
        conn.close()


if __name__ == "__main__":
    main()
