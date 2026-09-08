#!/usr/bin/env python3
"""
669fix-b-2021 mart apply — 25 省会 × 2021 (156/250 real, 62%)
====================================================================

Per 663 Gap 1: dbt CLI 工具链与 Python 3.14 不兼容,
直接用 psycopg2 跑 SQL 应用 mart_city_timeseries (knife 669fix-b-2021 sub-knife).

State after 669a-2020/2021/2022/2023/2024/2025 + 669b-2025 + 669fix-b-2020 + 669fix-b-2021:
  - 2030 rows = 29 city × 10 indicator × 7 year (2020-2026)
  - 156 real cells 增量 (21 city 公告 + 156 absolute-value cells; 13 fixed_asset % growth excluded)
  - 94 DATA_MISSING 增量:
    - 40 SICHUAN/XIZANG/QINGHAI/TAIWAN (hongheiku tag 页无 2021 entry)
    - 13 fixed_asset 增长% (无绝对值, per 669a-2021 §2 红线-3)
    - 41 城市级公报未列指标 (守新增红线-3 不手填)
    - 0 HUBEI_WUHAN (eid 28733) / SHANXI_TAIYUAN (eid 24774) → hongheiku URL 实为 tag listing, 无内容
  - Previous real cells = 315 (post-669fix-b-2020)
  - New total real cells = 315 + 156 = 471
  - New total DATA_MISSING = 1559
  - lineage_ruling attribution:
    - K669a-2021-2026-09-04: 4 city × 10 indicator (4 669a cities missing)
    - K669fix-b-2021-2026-09-08: 156 real + 94 missing (25 省会 全 attribution)
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
        # 2021 real by ruling
        cur.execute(f"""
            SELECT lineage_ruling, COUNT(*) FROM {TARGET_SCHEMA}.{MART_NAME}
            WHERE year = 2021 AND value IS NOT NULL
            GROUP BY lineage_ruling ORDER BY lineage_ruling;
        """)
        y2021_real_by_ruling = cur.fetchall()
        # 2021 real cells count
        cur.execute(f"""
            SELECT COUNT(*) FROM {TARGET_SCHEMA}.{MART_NAME}
            WHERE year = 2021 AND value IS NOT NULL;
        """)
        y2021_real = cur.fetchone()[0]
        # 2021 DATA_MISSING breakdown
        cur.execute(f"""
            SELECT lineage_ruling, COUNT(*) FROM {TARGET_SCHEMA}.{MART_NAME}
            WHERE year = 2021 AND value IS NULL
            GROUP BY lineage_ruling ORDER BY lineage_ruling;
        """)
        y2021_missing_by_ruling = cur.fetchall()
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
        # 2021 城市覆盖
        cur.execute(f"""
            SELECT COUNT(DISTINCT city_code) FROM {TARGET_SCHEMA}.{MART_NAME}
            WHERE year = 2021 AND value IS NOT NULL;
        """)
        y2021_cities_real = cur.fetchone()[0]
    conn.commit()
    return {
        "rows": rows,
        "cities": cities,
        "indicators": indicators,
        "years": years,
        "real_cells": real,
        "data_missing_cells": missing,
        "ruling_versions": rulings,
        "y2021_real": y2021_real,
        "y2021_real_by_ruling": y2021_real_by_ruling,
        "y2021_missing_by_ruling": y2021_missing_by_ruling,
        "y2021_cities_real": y2021_cities_real,
        "y2026_real": y2026_real,
        "direct_cities": direct_cities,
        "hk_transload": hk_transload,
    }


def main():
    print(f"=== knife 669fix-b-2021 mart apply (25 省会 × 2021, 156/250 real = 62%) ===")
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
        print(f"  real_cells          = {s['real_cells']}    (expect 471 = 315 prev + 156 669fix-b-2021)")
        print(f"  DATA_MISSING        = {s['data_missing_cells']}    (expect 1559 = 2030 - 471)")
        print(f"  ruling_versions     = {s['ruling_versions']}    (expect 10 = 9 prev + K669fix-b-2021)")
        print(f"  4 直辖市禁 (红线-7) = {s['direct_cities']}    (expect 0)")
        print(f"  HONGHEIKU_TRANSLOAD = {s['hk_transload']}    (expect 471 = same as real_cells)")
        print(f"  2021 real cells     = {s['y2021_real']}    (expect 156 = 21 city 公告 - 13 fixed_asset % growth)")
        print(f"  2021 real cities    = {s['y2021_cities_real']}    (expect 21 city 至少 1 real cell)")
        print(f"  2026 real cells     = {s['y2026_real']}    (expect 0, 守红线-2)")
        print()
        print("=== 2021 real cells by ruling ===")
        for ruling, cnt in s['y2021_real_by_ruling']:
            print(f"  {ruling}: {cnt} real cells")
        print()
        print("=== 2021 missing cells by ruling ===")
        for ruling, cnt in s['y2021_missing_by_ruling']:
            print(f"  {ruling}: {cnt} missing cells")
        print()
        print("=== Decision (knife 669fix-b-2021) ===")
        print("  25 省会 × 2021 = 156/250 real (62%)")
        print("  来源: hongheiku /djs/{eid}.html (2021 root pattern, 21 city)")
        print("  + 1 PDF bulletin (SHAANXI 25636)")
        print("  守新增红线-3: 增长% 不手填, 缺失 indicator 不补零")
        print("  - 13 fixed_asset 增长% excluded from rd8 CTE → DATA_MISSING (per 669a-2021 §2)")
        print("  - 21 city ≥1 real cell; SICHUAN/XIZANG/QINGHAI/TAIWAN 全 miss (守红线-3)")
        print("  - HUBEI_WUHAN/SHANXI_TAIYUAN hongheiku URL 实为 tag listing, 无内容")
    finally:
        conn.close()


if __name__ == "__main__":
    main()
