#!/usr/bin/env python3
"""
669j-5 mart apply — INSERT-only psycopg2 pattern (NO-OP path)
==============================================================

knife 669j sub-knife 5/6 (2026-09-13): 5 city cross-province NO-OP
  HUNAN_XIANGTAN (湘潭), HUNAN_ZHUZHOU (株洲), HUNAN_YUEYANG (岳阳), HUNAN_CHANGDE (常德),
  ANHUI_WUHU (芜湖)

NO-OP discovery: 5 HTTP tag URL probe, all 404.

Apply pattern: INSERT-ONLY, 350 rows (5 city × 7 year × 10 indicator).
"""
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

# 5 city × 2 province (湘 4 + 皖 1)
CITY_5 = [
    ("HUNAN_XIANGTAN",   "湘潭市", "HUNAN"),
    ("HUNAN_ZHUZHOU",    "株洲市", "HUNAN"),
    ("HUNAN_YUEYANG",    "岳阳市", "HUNAN"),
    ("HUNAN_CHANGDE",    "常德市", "HUNAN"),
    ("ANHUI_WUHU",       "芜湖市", "ANHUI"),
]

YEARS = [2020, 2021, 2022, 2023, 2024, 2025, 2026]

LINEAGE_RULING = "K669j-5-2026-09-13"
MISSING_REASON = ("knife 669j-5: 5 city cross-province (湘 4 + 皖 1) hongheiku 0 entry "
                  "(tag /tag/{pinyin} 5/5 404, 5 HTTP 验证, "
                  "不手填, 守新增红线-3)")
LINEAGE_ORIGIN = ("tjgb.hongheiku.com (NO-OP, hongheiku tag 404 to "
                  "XIANGTAN/ZHUZHOU/YUEYANG/CHANGDE/WUHU)")


def main():
    print(f"=== knife 669j-5 mart apply (INSERT-only, NO-OP, 5 city × 7 year × 10 indicator = 350 cells) ===")
    print(f"DB: {DB_HOST}:{DB_PORT}/{DB_NAME} schema={TARGET_SCHEMA}")
    print()

    conn = psycopg2.connect(host=DB_HOST, port=DB_PORT, user=DB_USER,
                            password=DB_PASS, dbname=DB_NAME)
    try:
        with conn.cursor() as cur:
            city_list = ",".join(f"'{c}'" for c, _, _ in CITY_5)
            cur.execute(f"""
                SELECT COUNT(*) FROM {TARGET_SCHEMA}.{MART_NAME}
                WHERE city_code IN ({city_list})
            """)
            existing = cur.fetchone()[0]
            if existing > 0:
                print(f"  WARN: {existing} rows already exist — DELETE prior 5 city rows")
                cur.execute(f"""
                    DELETE FROM {TARGET_SCHEMA}.{MART_NAME}
                    WHERE city_code IN ({city_list})
                """)
                print(f"  DELETE prior 5 city rows: {cur.rowcount}")

            cur.execute("""
                SELECT DISTINCT ON (indicator_key) indicator_key, indicator_label, unit
                FROM cegr_mart.mart_city_timeseries
                WHERE city_code = 'GUANGDONG_DONGGUAN' AND year = 2024
                ORDER BY indicator_key
            """)
            indicators = cur.fetchall()
            assert len(indicators) == 10

            inserted = 0
            for city_code, city_name, province_code in CITY_5:
                for year in YEARS:
                    for ind_key, ind_label, ind_unit in indicators:
                        cur.execute(f"""
                            INSERT INTO {TARGET_SCHEMA}.{MART_NAME} (
                                city_code, city_name, province_code,
                                indicator_key, indicator_label, unit,
                                year, value, status, missing_reason,
                                lineage_source_type, lineage_origin, lineage_ruling, lineage_is_demo
                            ) VALUES (
                                %s, %s, %s,
                                %s, %s, %s,
                                %s, NULL, 'DATA_MISSING', %s,
                                'DATA_MISSING', %s, %s, 'false'
                            )
                        """, (
                            city_code, city_name, province_code,
                            ind_key, ind_label, ind_unit,
                            year, MISSING_REASON, LINEAGE_ORIGIN, LINEAGE_RULING,
                        ))
                        inserted += 1
            print(f"  INSERT rows: {inserted}    (expect 350 = 5 × 7 × 10)")

        conn.commit()

        with conn.cursor() as cur:
            cur.execute(f"SELECT COUNT(*) FROM {TARGET_SCHEMA}.{MART_NAME}")
            rows = cur.fetchone()[0]
            cur.execute(f"SELECT COUNT(DISTINCT city_code) FROM {TARGET_SCHEMA}.{MART_NAME}")
            cities = cur.fetchone()[0]
            cur.execute(f"SELECT COUNT(DISTINCT indicator_key) FROM {TARGET_SCHEMA}.{MART_NAME}")
            indicators_n = cur.fetchone()[0]
            cur.execute(f"SELECT COUNT(DISTINCT year) FROM {TARGET_SCHEMA}.{MART_NAME}")
            years_n = cur.fetchone()[0]
            cur.execute(f"SELECT COUNT(*) FROM {TARGET_SCHEMA}.{MART_NAME} WHERE value IS NOT NULL")
            real = cur.fetchone()[0]
            cur.execute(f"SELECT COUNT(*) FROM {TARGET_SCHEMA}.{MART_NAME} WHERE status = 'DATA_MISSING'")
            miss = cur.fetchone()[0]
            cur.execute(f"SELECT COUNT(DISTINCT lineage_ruling) FROM {TARGET_SCHEMA}.{MART_NAME}")
            rulings = cur.fetchone()[0]
            cur.execute(f"""
                SELECT COUNT(*) FROM {TARGET_SCHEMA}.{MART_NAME}
                WHERE city_code IN ({city_list})
            """)
            j5_cells = cur.fetchone()[0]
            cur.execute(f"""
                SELECT COUNT(*) FROM {TARGET_SCHEMA}.{MART_NAME}
                WHERE city_code IN ({city_list}) AND value IS NOT NULL
            """)
            j5_real = cur.fetchone()[0]
            cur.execute(f"""
                SELECT COUNT(*) FROM {TARGET_SCHEMA}.{MART_NAME}
                WHERE city_code IN ({city_list}) AND status = 'DATA_MISSING'
            """)
            j5_miss = cur.fetchone()[0]
            cur.execute(f"""
                SELECT province_code, COUNT(*) AS city_cells, COUNT(DISTINCT city_code) AS city_n
                FROM {TARGET_SCHEMA}.{MART_NAME}
                WHERE city_code IN ({city_list})
                GROUP BY province_code ORDER BY province_code
            """)
            j5_by_province = cur.fetchall()
            cur.execute(f"""
                SELECT COUNT(*) FROM {TARGET_SCHEMA}.{MART_NAME}
                WHERE city_code LIKE 'BEIJING_%' OR city_code LIKE 'SHANGHAI_%'
                   OR city_code LIKE 'TIANJIN_%' OR city_code LIKE 'CHONGQING_%'
            """)
            direct = cur.fetchone()[0]

        print()
        print("mart apply OK:")
        print(f"  rows               = {rows}    (expect 4340 = 62 × 10 × 7; 3990 prior + 350)")
        print(f"  cities (distinct)  = {cities}    (expect 62 = 57 prior + 5 city)")
        print(f"  indicators         = {indicators_n}    (expect 10)")
        print(f"  years              = {years_n}    (expect 7)")
        print(f"  real_cells         = {real}    (NO-OP 不增)")
        print(f"  DATA_MISSING       = {miss}    (expect 3194 = 2844 prior + 350)")
        print(f"  ruling_versions    = {rulings}    (expect 60 = 59 prior + K669j-5)")
        print(f"  4 直辖市禁 (红线-7) = {direct}    (expect 0)")
        print()
        print(f"=== knife 669j-5 5 city check ===")
        print(f"  5 city cells        = {j5_cells}    (expect 350)")
        print(f"  5 city real cells   = {j5_real}    (expect 0, NO-OP)")
        print(f"  5 city MISSING cells = {j5_miss}    (expect 350)")
        print()
        print(f"=== 5 city per-province breakdown ===")
        for prov, c, n in j5_by_province:
            print(f"  {prov}: {n} city, {c} cells")
        print()
        print("=== Decision (knife 669j-5) ===")
        print("  5 city cross-province (湘 4 + 皖 1)")
        print("  tag URL probe 5 HTTP 全 0 命中 (hongheiku 0 entry)")
    finally:
        conn.close()


if __name__ == "__main__":
    main()