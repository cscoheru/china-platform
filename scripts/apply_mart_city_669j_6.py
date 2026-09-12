#!/usr/bin/env python3
"""
669j-6 mart apply — INSERT-only psycopg2 pattern (NO-OP path)
==============================================================

knife 669j sub-knife 6/6 (2026-09-13): 6 city cross-province NO-OP
  SICHUAN_MIANYANG (绵阳), SICHUAN_DEYANG (德阳), SICHUAN_NANCHONG (南充),
  SHAANXI_BAOJI (宝鸡), SHAANXI_XIANYANG (咸阳),
  LIAONING_ANSHAN (鞍山)

NO-OP discovery: 6 HTTP tag URL probe, all 404.

Apply pattern: INSERT-ONLY, 420 rows (6 city × 7 year × 10 indicator).

Expected post-state:
  - rows = 4340 + 420 = 4760 (62 prior + 6 city = 68 cities)
  - real_cells 不变 (NO-OP) = 1146
  - DATA_MISSING +420 = 3614
  - lineage_ruling +1 = 61
"""
import os
import sys
import psycopg2

DB_HOST = "127.0.0.1"
DB_PORT = 55440
DB_USER = "postgres"
DB_PASS = os.environ.get("DB_DEV_PASS", "postgres")
DB_NAME = "cegr_test"
TARGET_SCHEMA = "cegr_mart"
MART_NAME = "mart_city_timeseries"

# 6 city × 3 province (川 3 + 陕 2 + 辽 1)
CITY_6 = [
    ("SICHUAN_MIANYANG",  "绵阳市", "SICHUAN"),
    ("SICHUAN_DEYANG",    "德阳市", "SICHUAN"),
    ("SICHUAN_NANCHONG",  "南充市", "SICHUAN"),
    ("SHAANXI_BAOJI",     "宝鸡市", "SHAANXI"),
    ("SHAANXI_XIANYANG",  "咸阳市", "SHAANXI"),
    ("LIAONING_ANSHAN",   "鞍山市", "LIAONING"),
]

YEARS = [2020, 2021, 2022, 2023, 2024, 2025, 2026]

LINEAGE_RULING = "K669j-6-2026-09-13"
MISSING_REASON = ("knife 669j-6: 6 city cross-province (川 3 + 陕 2 + 辽 1) hongheiku 0 entry "
                  "(tag /tag/{pinyin} 6/6 404, 6 HTTP 验证, "
                  "不手填, 守新增红线-3)")
LINEAGE_ORIGIN = ("tjgb.hongheiku.com (NO-OP, hongheiku tag 404 to "
                  "MIANYANG/DEYANG/NANCHONG/BAOJI/XIANYANG/ANSHAN)")


def main():
    print(f"=== knife 669j-6 mart apply (INSERT-only, NO-OP, 6 city × 7 year × 10 indicator = 420 cells) ===")
    print(f"DB: {DB_HOST}:{DB_PORT}/{DB_NAME} schema={TARGET_SCHEMA}")
    print()

    conn = psycopg2.connect(host=DB_HOST, port=DB_PORT, user=DB_USER,
                            password=DB_PASS, dbname=DB_NAME)
    try:
        with conn.cursor() as cur:
            city_list = ",".join(f"'{c}'" for c, _, _ in CITY_6)
            cur.execute(f"""
                SELECT COUNT(*) FROM {TARGET_SCHEMA}.{MART_NAME}
                WHERE city_code IN ({city_list})
            """)
            existing = cur.fetchone()[0]
            if existing > 0:
                print(f"  WARN: {existing} rows already exist — DELETE prior 6 city rows")
                cur.execute(f"""
                    DELETE FROM {TARGET_SCHEMA}.{MART_NAME}
                    WHERE city_code IN ({city_list})
                """)
                print(f"  DELETE prior 6 city rows: {cur.rowcount}")

            cur.execute("""
                SELECT DISTINCT ON (indicator_key) indicator_key, indicator_label, unit
                FROM cegr_mart.mart_city_timeseries
                WHERE city_code = 'GUANGDONG_DONGGUAN' AND year = 2024
                ORDER BY indicator_key
            """)
            indicators = cur.fetchall()
            assert len(indicators) == 10

            inserted = 0
            for city_code, city_name, province_code in CITY_6:
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
            print(f"  INSERT rows: {inserted}    (expect 420 = 6 × 7 × 10)")

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
            j6_cells = cur.fetchone()[0]
            cur.execute(f"""
                SELECT COUNT(*) FROM {TARGET_SCHEMA}.{MART_NAME}
                WHERE city_code IN ({city_list}) AND value IS NOT NULL
            """)
            j6_real = cur.fetchone()[0]
            cur.execute(f"""
                SELECT COUNT(*) FROM {TARGET_SCHEMA}.{MART_NAME}
                WHERE city_code IN ({city_list}) AND status = 'DATA_MISSING'
            """)
            j6_miss = cur.fetchone()[0]
            cur.execute(f"""
                SELECT province_code, COUNT(*) AS city_cells, COUNT(DISTINCT city_code) AS city_n
                FROM {TARGET_SCHEMA}.{MART_NAME}
                WHERE city_code IN ({city_list})
                GROUP BY province_code ORDER BY province_code
            """)
            j6_by_province = cur.fetchall()
            cur.execute(f"""
                SELECT COUNT(*) FROM {TARGET_SCHEMA}.{MART_NAME}
                WHERE city_code LIKE 'BEIJING_%' OR city_code LIKE 'SHANGHAI_%'
                   OR city_code LIKE 'TIANJIN_%' OR city_code LIKE 'CHONGQING_%'
            """)
            direct = cur.fetchone()[0]

        print()
        print("mart apply OK:")
        print(f"  rows               = {rows}    (expect 4760 = 68 × 10 × 7; 4340 prior + 420)")
        print(f"  cities (distinct)  = {cities}    (expect 68 = 62 prior + 6 city)")
        print(f"  indicators         = {indicators_n}    (expect 10)")
        print(f"  years              = {years_n}    (expect 7)")
        print(f"  real_cells         = {real}    (NO-OP 不增)")
        print(f"  DATA_MISSING       = {miss}    (expect 3614 = 3194 prior + 420)")
        print(f"  ruling_versions    = {rulings}    (expect 61 = 60 prior + K669j-6)")
        print(f"  4 直辖市禁 (红线-7) = {direct}    (expect 0)")
        print()
        print(f"=== knife 669j-6 6 city check ===")
        print(f"  6 city cells        = {j6_cells}    (expect 420)")
        print(f"  6 city real cells   = {j6_real}    (expect 0, NO-OP)")
        print(f"  6 city MISSING cells = {j6_miss}    (expect 420)")
        print()
        print(f"=== 6 city per-province breakdown ===")
        for prov, c, n in j6_by_province:
            print(f"  {prov}: {n} city, {c} cells")
        print()
        print("=== Decision (knife 669j-6) ===")
        print("  6 city cross-province (川 3 + 陕 2 + 辽 1)")
        print("  tag URL probe 6 HTTP 全 0 命中 (hongheiku 0 entry)")
        print("  669j program sub-knife 6/6 收口")
    finally:
        conn.close()


if __name__ == "__main__":
    main()