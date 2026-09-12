#!/usr/bin/env python3
"""
669j-3 mart apply — INSERT-only psycopg2 pattern (NO-OP path)
==============================================================

knife 669j sub-knife 3/6 (2026-09-13): 5 city 苏 卫星城 NO-OP
  JIANGSU_YANGZHOU (扬州), JIANGSU_XUZHOU (徐州), JIANGSU_LIANYUNGANG (连云港),
  JIANGSU_YANCHENG (盐城), JIANGSU_SUQIAN (宿迁)

NO-OP discovery (per 669j-sketch 2026-09-12 + 669j-1 + 669j-2 pattern):
  - tag URL /tag/{pinyin} 5× 404 (5 HTTP, EN ASCII)
  - Total 5 HTTP attempted, all 0 hits
  - hongheiku tag page for JIANGSU currently lists: NANJING/SUZHOU/WUXI/CHANGZHOU/ZHENJIANG
    → YANGZHOU/XUZHOU/LIANYUNGANG/YANCHENG/SUQIAN all 0 entry on hongheiku (under JIANGSU)

Apply pattern: INSERT-ONLY (per 669j-1/669j-2 pattern, since 5 cities
don't yet exist in mart). Per-city 70 cells (5 city × 7 year × 10 indicator = 350 cells),
all status='DATA_MISSING' (NO-OP, no real data — 守新增红线-3 禁手填).

Expected post-state:
  - rows = 3290 + 350 = 3640 (47 prior + 5 city = 52 cities)
  - real_cells 不变 (NO-OP) = 1146
  - DATA_MISSING +350 = 2494
  - lineage_ruling +1 = 58 (新增 K669j-3-2026-09-13)
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

# 5 city 苏 卫星城 — 全 JIANGSU province (cross-city, same-province test)
CITY_5 = [
    ("JIANGSU_YANGZHOU",    "扬州市", "JIANGSU"),
    ("JIANGSU_XUZHOU",      "徐州市", "JIANGSU"),
    ("JIANGSU_LIANYUNGANG", "连云港市", "JIANGSU"),
    ("JIANGSU_YANCHENG",    "盐城市", "JIANGSU"),
    ("JIANGSU_SUQIAN",      "宿迁市", "JIANGSU"),
]

YEARS = [2020, 2021, 2022, 2023, 2024, 2025, 2026]

LINEAGE_RULING = "K669j-3-2026-09-13"
MISSING_REASON = ("knife 669j-3: 5 city 苏 卫星城 hongheiku 0 entry "
                  "(tag /tag/{pinyin} 5/5 404, 5 HTTP 验证, "
                  "不手填, 守新增红线-3)")
LINEAGE_ORIGIN = ("tjgb.hongheiku.com (NO-OP, hongheiku tag 404 to "
                  "YANGZHOU/XUZHOU/LIANYUNGANG/YANCHENG/SUQIAN)")


def main():
    print(f"=== knife 669j-3 mart apply (INSERT-only, NO-OP, 5 city × 7 year × 10 indicator = 350 cells) ===")
    print(f"DB: {DB_HOST}:{DB_PORT}/{DB_NAME} schema={TARGET_SCHEMA}")
    print()

    conn = psycopg2.connect(host=DB_HOST, port=DB_PORT, user=DB_USER,
                            password=DB_PASS, dbname=DB_NAME)
    try:
        with conn.cursor() as cur:
            # --- 1. Pre-check: 5 city must NOT already exist (idempotency) ---
            city_list = ",".join(f"'{c}'" for c, _, _ in CITY_5)
            cur.execute(f"""
                SELECT COUNT(*) FROM {TARGET_SCHEMA}.{MART_NAME}
                WHERE city_code IN ({city_list})
            """)
            existing = cur.fetchone()[0]
            if existing > 0:
                print(f"  WARN: {existing} rows already exist for 5 669j-3 cities — will overwrite with NO-OP rows")
                cur.execute(f"""
                    DELETE FROM {TARGET_SCHEMA}.{MART_NAME}
                    WHERE city_code IN ({city_list})
                """)
                print(f"  DELETE prior 5 city rows: {cur.rowcount}")

            # --- 2. Get 10 indicator dimension from existing mart (DONGGUAN 2024) ---
            cur.execute("""
                SELECT DISTINCT ON (indicator_key) indicator_key, indicator_label, unit
                FROM cegr_mart.mart_city_timeseries
                WHERE city_code = 'GUANGDONG_DONGGUAN' AND year = 2024
                ORDER BY indicator_key
            """)
            indicators = cur.fetchall()
            assert len(indicators) == 10, f"expected 10 indicators, got {len(indicators)}"

            # --- 3. INSERT 5 city × 7 year × 10 indicator = 350 rows ---
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

        # --- 4. Post-check summary ---
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
            j3_cells = cur.fetchone()[0]
            cur.execute(f"""
                SELECT COUNT(*) FROM {TARGET_SCHEMA}.{MART_NAME}
                WHERE city_code IN ({city_list}) AND value IS NOT NULL
            """)
            j3_real = cur.fetchone()[0]
            cur.execute(f"""
                SELECT COUNT(*) FROM {TARGET_SCHEMA}.{MART_NAME}
                WHERE city_code IN ({city_list}) AND status = 'DATA_MISSING'
            """)
            j3_miss = cur.fetchone()[0]
            cur.execute(f"""
                SELECT COUNT(*) FROM {TARGET_SCHEMA}.{MART_NAME}
                WHERE city_code IN ({city_list})
                  AND missing_reason LIKE '%669j-3%hongheiku 0 entry%'
            """)
            j3_miss_reason = cur.fetchone()[0]
            cur.execute(f"""
                SELECT COUNT(DISTINCT city_code) FROM {TARGET_SCHEMA}.{MART_NAME}
                WHERE city_code IN ({city_list})
            """)
            j3_distinct = cur.fetchone()[0]
            cur.execute(f"""
                SELECT COUNT(*) FROM {TARGET_SCHEMA}.{MART_NAME}
                WHERE city_code LIKE 'BEIJING_%' OR city_code LIKE 'SHANGHAI_%'
                   OR city_code LIKE 'TIANJIN_%' OR city_code LIKE 'CHONGQING_%'
            """)
            direct = cur.fetchone()[0]
            cur.execute(f"""
                SELECT year, COUNT(*) FILTER (WHERE value IS NOT NULL) AS real,
                       COUNT(*) FILTER (WHERE status = 'DATA_MISSING') AS miss
                FROM {TARGET_SCHEMA}.{MART_NAME}
                WHERE city_code IN ({city_list})
                GROUP BY year ORDER BY year
            """)
            j3_yearly = cur.fetchall()

        print()
        print("mart apply OK:")
        print(f"  rows               = {rows}    (expect 3640 = 52 × 10 × 7; 3290 prior + 350)")
        print(f"  cities (distinct)  = {cities}    (expect 52 = 47 prior + 5 city)")
        print(f"  indicators         = {indicators_n}    (expect 10)")
        print(f"  years              = {years_n}    (expect 7 = 2020-2026)")
        print(f"  real_cells         = {real}    (NO-OP 不增)")
        print(f"  DATA_MISSING       = {miss}    (expect 2494 = 2144 prior + 350)")
        print(f"  ruling_versions    = {rulings}    (expect 58 = 57 prior + K669j-3)")
        print(f"  4 直辖市禁 (红线-7) = {direct}    (expect 0)")
        print()
        print(f"=== knife 669j-3 5 city check ===")
        print(f"  5 city distinct     = {j3_distinct}    (expect 5)")
        print(f"  5 city cells        = {j3_cells}    (expect 350 = 5 × 10 × 7)")
        print(f"  5 city real cells   = {j3_real}    (expect 0, NO-OP)")
        print(f"  5 city MISSING cells = {j3_miss}    (expect 350)")
        print(f"  missing_reason w/ '669j-3 0 entry' = {j3_miss_reason}    (expect 350)")
        print()
        print(f"=== 5 city per-year breakdown (real / missing) ===")
        for yr, r, m in j3_yearly:
            print(f"  {yr}: real={r} miss={m}")
        print()
        print("=== Decision (knife 669j-3) ===")
        print("  5 city 苏 卫星城 (YANGZHOU/XUZHOU/LIANYUNGANG/YANCHENG/SUQIAN)")
        print("  tag URL probe 5 HTTP 全 0 命中 (hongheiku 0 entry)")
        print("  守新增红线-3 不手填, 不补零; 守新增红线-1 2020 全 DATA_MISSING; 守新增红线-2 2026 全 DATA_MISSING")
    finally:
        conn.close()


if __name__ == "__main__":
    main()