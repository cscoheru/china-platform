#!/usr/bin/env python3
"""
669b-2025 mart apply — 25 省会 city × 2025 (全 DATA_MISSING 路径)
====================================================================

Per 663 Gap 1: dbt CLI 工具链与 Python 3.14 不兼容,
直接用 psycopg2 跑 SQL 应用 mart_city_timeseries (knife 669b-2025 sub-knife).

State after 669a-2020/2021/2022/2023/2024/2025 + 669b-2025:
  - 2030 rows = 29 city × 10 indicator × 7 year (2020-2026)
    - 669a: 4 priority city (深/穗/杭/宁)
    - 669b: 25 省会 city (28 省会 - 3 已在 669a: 穗/杭/宁)
  - real_cells = 154 (no change, 669b-2025 adds 0)
    - 26 [2021] + 37 [2022] + 37 [2023] + 36 [2024] + 18 [2025]
  - DATA_MISSING = 1876
    - 40 [2020] + 14 [2021 miss] + 3 [2022 miss] + 3 [2023 miss] + 4 [2024 miss]
    + 22 [2025 669a miss] + 250 [2025 669b miss] + 2030-154-22-250=1604
    = 1540 from other years? Recompute: 29*10*7 = 2030; 154 real + 22 miss = 176; 2030-176 = 1854
    4 城 × 6 年 (2020/2021/2022/2023/2024/2026) × 10 = 240 (669a miss w/o 2025)
    25 城 × 7 年 × 10 = 1750 (669b all miss)
    + 22 [2025 669a miss] = 240 + 1750 + 22 = 2012, but 154 real so 2030-154 = 1876 ✓
  - ruling_versions = 8 (K669a-2020/2021/2022/2023/2024/2025 + K669b-2025 + pending)
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
        # 2025 missing by ruling (4 669a + 25 669b)
        cur.execute(f"""
            SELECT lineage_ruling, COUNT(*) FROM {TARGET_SCHEMA}.{MART_NAME}
            WHERE year = 2025 AND value IS NULL
            GROUP BY lineage_ruling ORDER BY lineage_ruling;
        """)
        y2025_missing_by_ruling = cur.fetchall()
        # 2025 669b city count
        cur.execute(f"""
            SELECT COUNT(*) FROM {TARGET_SCHEMA}.{MART_NAME}
            WHERE year = 2025
              AND city_code IN (
                'HEBEI_SHIJIAZHUANG','SHANXI_TAIYUAN','NEIMENGGU_HUHEHAOTE','LIAONING_SHENYANG',
                'JILIN_CHANGCHUN','HEILONGJIANG_HARBIN','ANHUI_HEFEI','FUJIAN_FUZHOU',
                'JIANGXI_NANCHANG','SHANDONG_JINAN','HENAN_ZHENGZHOU','HUBEI_WUHAN',
                'HUNAN_CHANGSHA','GUANGXI_NANNING','HAINAN_HAIKOU','SICHUAN_CHENGDU',
                'GUIZHOU_GUIYANG','YUNNAN_KUNMING','XIZANG_LASA','SHAANXI_XIAN',
                'GANSU_LANZHOU','QINGHAI_XINING','NINGXIA_YINCHUAN','XINJIANG_WULUMUQI',
                'TAIWAN_TAIPEI'
              );
        """)
        y2025_669b_cells = cur.fetchone()[0]
        # 4 直辖市禁 (红线-7)
        cur.execute(f"""
            SELECT COUNT(*) FROM {TARGET_SCHEMA}.{MART_NAME}
            WHERE city_code LIKE 'BEIJING_%' OR city_code LIKE 'SHANGHAI_%'
               OR city_code LIKE 'TIANJIN_%' OR city_code LIKE 'CHONGQING_%';
        """)
        direct_cities = cur.fetchone()[0]
    conn.commit()
    return {
        "rows": rows,
        "cities": cities,
        "indicators": indicators,
        "years": years,
        "real_cells": real,
        "data_missing_cells": missing,
        "ruling_versions": rulings,
        "y2025_missing_by_ruling": y2025_missing_by_ruling,
        "y2025_669b_cells": y2025_669b_cells,
        "direct_cities": direct_cities,
    }


def main():
    print(f"=== knife 669b-2025 mart apply (25 省会 × 2025, 全 DATA_MISSING 路径) ===")
    print(f"DB: {DB_HOST}:{DB_PORT}/{DB_NAME} schema={TARGET_SCHEMA}")
    print(f"SQL: {SQL_FILE}")
    print()
    conn = psycopg2.connect(host=DB_HOST, port=DB_PORT, user=DB_USER,
                            password=DB_PASS, dbname=DB_NAME)
    try:
        s = apply_mart(conn)
        print("mart apply OK:")
        print(f"  rows               = {s['rows']}    (expect 2030 = 29 × 10 × 7)")
        print(f"  cities (distinct)  = {s['cities']}    (expect 29 = 4 669a + 25 669b)")
        print(f"  indicators         = {s['indicators']}   (expect 10)")
        print(f"  years              = {s['years']}    (expect 7 = 2020-2026)")
        print(f"  real_cells         = {s['real_cells']}    (expect 154 = 26[2021]+37[2022]+37[2023]+36[2024]+18[2025])")
        print(f"  DATA_MISSING       = {s['data_missing_cells']}    (expect 1876 = 240 669a miss + 250 669b 2025 miss + 1386 other years)")
        print(f"  ruling_versions    = {s['ruling_versions']}    (expect 8 = K669a-2020/2021/2022/2023/2024/2025 + K669b-2025 + pending)")
        print(f"  4 直辖市禁 (红线-7) = {s['direct_cities']}    (expect 0)")
        print(f"  2025 669b cells    = {s['y2025_669b_cells']}    (expect 250 = 25 city × 10 indicator)")
        print()
        print("=== 2025 missing cells by ruling (4 669a + 25 669b) ===")
        for ruling, cnt in s['y2025_missing_by_ruling']:
            print(f"  {ruling}: {cnt} missing cells")
        print()
        print("=== Decision (knife 669b-2025) ===")
        print("  25 省会 × 2025 = 全 DATA_MISSING (hongheiku 无 2025 city bulletin)")
        print("  3 probe methods × 30 city 全部 0 命中 (tag + cat index + 站搜)")
        print("  守新增红线-3 不手填, 不补零")
    finally:
        conn.close()


if __name__ == "__main__":
    main()