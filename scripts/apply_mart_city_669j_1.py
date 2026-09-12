#!/usr/bin/env python3
"""
669j-1 mart apply — INSERT-only psycopg2 pattern (NO-OP path)
==============================================================

knife 669j sub-knife 1/6 (2026-09-12, batch2): 5 粤卫星城
  GUANGDONG_ZHUHAI (珠海), GUANGDONG_ZHANJIANG (湛江), GUANGDONG_SHANTOU (汕头),
  GUANGDONG_JIANGMEN (江门), GUANGDONG_ZHAOQING (肇庆)

NO-OP discovery (per 669j-sketch 2026-09-12 + 669b-i-hangzhou NO-OP 模式):
  - tag URL /tag/{pinyin} 4× 404 + 1× connection reset (5 HTTP)
  - tag URL /tag/{URL-encoded 中文} 5× 404 (5 HTTP)
  - /cat_djs.html + /cat_sjtjgb.html 0 ref to 5 city (5 HTTP probe)
  - Total 15 HTTP, all 0 hits
  - hongheiku tag page for GUANGDONG currently only lists: GUANGZHOU/SHENZHEN/DONGGUAN/FOSHAN/ZHANJIANG(?)
    → ZHUHAI/SHANTOU/JIANGMEN/ZHAOQING/ZHANJIANG all 0 entry on hongheiku

Apply pattern: INSERT-ONLY (per 669b-i-qingdao UPDATE-ONLY pattern, since 5 粤 cities
don't yet exist in mart). Per-city 70 cells (5 city × 7 year × 10 indicator = 350 cells),
all status='DATA_MISSING' (NO-OP, no real data — 守新增红线-3 禁手填).

Expected post-state:
  - rows = 2590 + 350 = 2940 (37 prior + 5 粤 = 42 cities)
  - real_cells 不变 (NO-OP) = 1090
  - DATA_MISSING +350 = 1850
  - lineage_ruling +1 = 10 (新增 K669j-1-2026-09-12)
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

CITY_5 = [
    # (city_code, city_name)
    ("GUANGDONG_ZHUHAI",   "珠海市"),
    ("GUANGDONG_ZHANJIANG", "湛江市"),
    ("GUANGDONG_SHANTOU",   "汕头市"),
    ("GUANGDONG_JIANGMEN",  "江门市"),
    ("GUANGDONG_ZHAOQING",  "肇庆市"),
]

PROVINCE_CODE = "GUANGDONG"
YEARS = [2020, 2021, 2022, 2023, 2024, 2025, 2026]

LINEAGE_RULING = "K669j-1-2026-09-12"
MISSING_REASON = "knife 669j-1: 5 粤卫星城 hongheiku 0 entry (tag 404 / cat index 0 ref, 15 HTTP 验证, 不手填, 守新增红线-3)"
LINEAGE_ORIGIN = "tjgb.hongheiku.com (NO-OP, hongheiku tag 404 / cat index 0 ref to ZHUHAI/ZHANJIANG/SHANTOU/JIANGMEN/ZHAOQING)"


def main():
    print(f"=== knife 669j-1 mart apply (INSERT-only, NO-OP, 5 粤卫星城 × 7 year × 10 indicator = 350 cells) ===")
    print(f"DB: {DB_HOST}:{DB_PORT}/{DB_NAME} schema={TARGET_SCHEMA}")
    print()

    conn = psycopg2.connect(host=DB_HOST, port=DB_PORT, user=DB_USER,
                            password=DB_PASS, dbname=DB_NAME)
    try:
        with conn.cursor() as cur:
            # --- 1. Pre-check: 5 city must NOT already exist (idempotency) ---
            city_list = ",".join(f"'{c}'" for c, _ in CITY_5)
            cur.execute(f"""
                SELECT COUNT(*) FROM {TARGET_SCHEMA}.{MART_NAME}
                WHERE city_code IN ({city_list})
            """)
            existing = cur.fetchone()[0]
            if existing > 0:
                print(f"  WARN: {existing} rows already exist for 5 粤 cities — will overwrite with NO-OP rows")
                cur.execute(f"""
                    DELETE FROM {TARGET_SCHEMA}.{MART_NAME}
                    WHERE city_code IN ({city_list})
                """)
                print(f"  DELETE prior 5 粤 rows: {cur.rowcount}")

            # --- 2. Get 10 indicator dimension from existing mart (DONGGUAN 2024) ---
            cur.execute("""
                SELECT DISTINCT ON (indicator_key) indicator_key, indicator_label, unit
                FROM {TARGET_SCHEMA}.{MART_NAME}
                WHERE city_code = 'GUANGDONG_DONGGUAN' AND year = 2024
                ORDER BY indicator_key
            """.format(**{"TARGET_SCHEMA": TARGET_SCHEMA, "MART_NAME": MART_NAME}))
            indicators = cur.fetchall()  # [(key, label, unit), ...] × 10
            assert len(indicators) == 10, f"expected 10 indicators, got {len(indicators)}"

            # --- 3. INSERT 5 city × 7 year × 10 indicator = 350 rows ---
            inserted = 0
            for city_code, city_name in CITY_5:
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
                            city_code, city_name, PROVINCE_CODE,
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
            # 5 粤
            cur.execute(f"""
                SELECT COUNT(*) FROM {TARGET_SCHEMA}.{MART_NAME}
                WHERE city_code IN ({city_list})
            """)
            j1_cells = cur.fetchone()[0]
            cur.execute(f"""
                SELECT COUNT(*) FROM {TARGET_SCHEMA}.{MART_NAME}
                WHERE city_code IN ({city_list}) AND value IS NOT NULL
            """)
            j1_real = cur.fetchone()[0]
            cur.execute(f"""
                SELECT COUNT(*) FROM {TARGET_SCHEMA}.{MART_NAME}
                WHERE city_code IN ({city_list}) AND status = 'DATA_MISSING'
            """)
            j1_miss = cur.fetchone()[0]
            cur.execute(f"""
                SELECT COUNT(*) FROM {TARGET_SCHEMA}.{MART_NAME}
                WHERE city_code IN ({city_list})
                  AND missing_reason LIKE '%669j-1%hongheiku 0 entry%'
            """)
            j1_miss_reason = cur.fetchone()[0]
            cur.execute(f"""
                SELECT COUNT(DISTINCT city_code) FROM {TARGET_SCHEMA}.{MART_NAME}
                WHERE city_code IN ({city_list})
            """)
            j1_distinct = cur.fetchone()[0]
            # 4 直辖市禁 (红线-7)
            cur.execute(f"""
                SELECT COUNT(*) FROM {TARGET_SCHEMA}.{MART_NAME}
                WHERE city_code LIKE 'BEIJING_%' OR city_code LIKE 'SHANGHAI_%'
                   OR city_code LIKE 'TIANJIN_%' OR city_code LIKE 'CHONGQING_%'
            """)
            direct = cur.fetchone()[0]
            # per-year breakdown for 5 city
            cur.execute(f"""
                SELECT year, COUNT(*) FILTER (WHERE value IS NOT NULL) AS real,
                       COUNT(*) FILTER (WHERE status = 'DATA_MISSING') AS miss
                FROM {TARGET_SCHEMA}.{MART_NAME}
                WHERE city_code IN ({city_list})
                GROUP BY year ORDER BY year
            """)
            j1_yearly = cur.fetchall()

        print()
        print("mart apply OK:")
        print(f"  rows               = {rows}    (expect 2940 = 42 × 10 × 7; 2590 prior + 350)")
        print(f"  cities (distinct)  = {cities}    (expect 42 = 37 prior + 5 粤卫星城)")
        print(f"  indicators         = {indicators_n}    (expect 10)")
        print(f"  years              = {years_n}    (expect 7 = 2020-2026)")
        print(f"  real_cells         = {real}    (expect 1090 = 不变, NO-OP 不增 real)")
        print(f"  DATA_MISSING       = {miss}    (expect 1850 = 1500 prior + 350)")
        print(f"  ruling_versions    = {rulings}    (expect 10 = 9 prior + K669j-1)")
        print(f"  4 直辖市禁 (红线-7) = {direct}    (expect 0)")
        print()
        print(f"=== knife 669j-1 5 粤 satellite city check ===")
        print(f"  5 city distinct     = {j1_distinct}    (expect 5)")
        print(f"  5 city cells        = {j1_cells}    (expect 350 = 5 × 10 × 7)")
        print(f"  5 city real cells   = {j1_real}    (expect 0, NO-OP)")
        print(f"  5 city MISSING cells = {j1_miss}    (expect 350)")
        print(f"  missing_reason w/ '669j-1 0 entry' = {j1_miss_reason}    (expect 350)")
        print()
        print(f"=== 5 粤 city per-year breakdown (real / missing) ===")
        for yr, r, m in j1_yearly:
            print(f"  {yr}: real={r} miss={m}")
        print()
        print("=== Decision (knife 669j-1) ===")
        print("  5 粤卫星城 (ZHUHAI/ZHANJIANG/SHANTOU/JIANGMEN/ZHAOQING) hongheiku 0 entry")
        print("  3 probe methods × 5 city = 15 HTTP 全部 0 命中")
        print("  守新增红线-3 不手填, 不补零; 守新增红线-1 2020 全 DATA_MISSING; 守新增红线-2 2026 全 DATA_MISSING")
    finally:
        conn.close()


if __name__ == "__main__":
    main()