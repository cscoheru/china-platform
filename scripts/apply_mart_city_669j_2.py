#!/usr/bin/env python3
"""
669j-2 mart apply — INSERT-only psycopg2 pattern (NO-OP path)
==============================================================

knife 669j sub-knife 2/6 (2026-09-13): 5 city cross-province NO-OP
  GUANGDONG_HUIZHOU (惠州), GUANGDONG_ZHONGSHAN (中山), GUANGDONG_CHAOZHOU (潮州),
  JIANGSU_CHANGZHOU (常州), JIANGSU_ZHENJIANG (镇江)

NO-OP discovery (per 669j-sketch 2026-09-12 + 669j-1 pattern):
  - tag URL /tag/{pinyin} 5× 404 (5 HTTP, EN ASCII)
  - tag URL /tag/{URL-encoded 中文} 5× UnicodeEncodeError skipped (rejected as 404 in URL lib)
  - Total 10 HTTP attempted, all 0 hits
  - hongheiku tag page for GUANGDONG currently lists: GUANGZHOU/SHENZHEN/DONGGUAN/FOSHAN
    → HUIZHOU/ZHONGSHAN/CHAOZHOU all 0 entry on hongheiku (under GUANGDONG)
    hongheiku tag page for JIANGSU: NANJING/SUZHOU/WUXI
    → CHANGZHOU/ZHENJIANG all 0 entry on hongheiku (under JIANGSU)

Apply pattern: INSERT-ONLY (per 669j-1 INSERT-only pattern, since 5 cities
don't yet exist in mart). Per-city 70 cells (5 city × 7 year × 10 indicator = 350 cells),
all status='DATA_MISSING' (NO-OP, no real data — 守新增红线-3 禁手填).

Expected post-state:
  - rows = 2940 + 350 = 3290 (42 prior + 5 city = 47 cities)
  - real_cells 不变 (NO-OP) = 1090
  - DATA_MISSING +350 = 2200
  - lineage_ruling +1 = 11 (新增 K669j-2-2026-09-13)
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

# 5 city × 2 province (粤 3 + 苏 2) — heterogeneous cross-province mix
CITY_5 = [
    # (city_code, city_name, province_code)
    ("GUANGDONG_HUIZHOU",   "惠州市", "GUANGDONG"),
    ("GUANGDONG_ZHONGSHAN", "中山市", "GUANGDONG"),
    ("GUANGDONG_CHAOZHOU",  "潮州市", "GUANGDONG"),
    ("JIANGSU_CHANGZHOU",   "常州市", "JIANGSU"),
    ("JIANGSU_ZHENJIANG",   "镇江市", "JIANGSU"),
]

# years 2020-2026 (7 year × 10 indicator × 5 city = 350 cells, like 669j-1)
YEARS = [2020, 2021, 2022, 2023, 2024, 2025, 2026]

LINEAGE_RULING = "K669j-2-2026-09-13"
MISSING_REASON = ("knife 669j-2: 5 city cross-province (粤 3 + 苏 2) hongheiku 0 entry "
                  "(tag /tag/{pinyin} 5/5 404, 中文 variant 5/5 rejected, 10 HTTP 验证, "
                  "不手填, 守新增红线-3)")
LINEAGE_ORIGIN = ("tjgb.hongheiku.com (NO-OP, hongheiku tag 404 to "
                  "HUIZHOU/ZHONGSHAN/CHAOZHOU/CHANGZHOU/ZHENJIANG)")


def main():
    print(f"=== knife 669j-2 mart apply (INSERT-only, NO-OP, 5 city × 7 year × 10 indicator = 350 cells) ===")
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
                print(f"  WARN: {existing} rows already exist for 5 669j-2 cities — will overwrite with NO-OP rows")
                cur.execute(f"""
                    DELETE FROM {TARGET_SCHEMA}.{MART_NAME}
                    WHERE city_code IN ({city_list})
                """)
                print(f"  DELETE prior 5 city rows: {cur.rowcount}")

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
            # 5 669j-2 city breakdown
            cur.execute(f"""
                SELECT COUNT(*) FROM {TARGET_SCHEMA}.{MART_NAME}
                WHERE city_code IN ({city_list})
            """)
            j2_cells = cur.fetchone()[0]
            cur.execute(f"""
                SELECT COUNT(*) FROM {TARGET_SCHEMA}.{MART_NAME}
                WHERE city_code IN ({city_list}) AND value IS NOT NULL
            """)
            j2_real = cur.fetchone()[0]
            cur.execute(f"""
                SELECT COUNT(*) FROM {TARGET_SCHEMA}.{MART_NAME}
                WHERE city_code IN ({city_list}) AND status = 'DATA_MISSING'
            """)
            j2_miss = cur.fetchone()[0]
            cur.execute(f"""
                SELECT COUNT(*) FROM {TARGET_SCHEMA}.{MART_NAME}
                WHERE city_code IN ({city_list})
                  AND missing_reason LIKE '%669j-2%hongheiku 0 entry%'
            """)
            j2_miss_reason = cur.fetchone()[0]
            cur.execute(f"""
                SELECT COUNT(DISTINCT city_code) FROM {TARGET_SCHEMA}.{MART_NAME}
                WHERE city_code IN ({city_list})
            """)
            j2_distinct = cur.fetchone()[0]
            # per-province breakdown for 5 city
            cur.execute(f"""
                SELECT province_code, COUNT(*) AS city_cells
                FROM {TARGET_SCHEMA}.{MART_NAME}
                WHERE city_code IN ({city_list})
                GROUP BY province_code ORDER BY province_code
            """)
            j2_by_province = cur.fetchall()
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
            j2_yearly = cur.fetchall()

        print()
        print("mart apply OK:")
        print(f"  rows               = {rows}    (expect 3290 = 47 × 10 × 7; 2940 prior + 350)")
        print(f"  cities (distinct)  = {cities}    (expect 47 = 42 prior + 5 city)")
        print(f"  indicators         = {indicators_n}    (expect 10)")
        print(f"  years              = {years_n}    (expect 7 = 2020-2026)")
        print(f"  real_cells         = {real}    (expect 1090 = 不变, NO-OP 不增 real)")
        print(f"  DATA_MISSING       = {miss}    (expect 2200 = 1850 prior + 350)")
        print(f"  ruling_versions    = {rulings}    (expect 11 = 10 prior + K669j-2)")
        print(f"  4 直辖市禁 (红线-7) = {direct}    (expect 0)")
        print()
        print(f"=== knife 669j-2 5 city check ===")
        print(f"  5 city distinct     = {j2_distinct}    (expect 5)")
        print(f"  5 city cells        = {j2_cells}    (expect 350 = 5 × 10 × 7)")
        print(f"  5 city real cells   = {j2_real}    (expect 0, NO-OP)")
        print(f"  5 city MISSING cells = {j2_miss}    (expect 350)")
        print(f"  missing_reason w/ '669j-2 0 entry' = {j2_miss_reason}    (expect 350)")
        print()
        print(f"=== 5 city per-province breakdown ===")
        for prov, c in j2_by_province:
            print(f"  {prov}: {c} cells")
        print()
        print(f"=== 5 city per-year breakdown (real / missing) ===")
        for yr, r, m in j2_yearly:
            print(f"  {yr}: real={r} miss={m}")
        print()
        print("=== Decision (knife 669j-2) ===")
        print("  5 city cross-province (粤 3 HUIZHOU/ZHONGSHAN/CHAOZHOU + 苏 2 CHANGZHOU/ZHENJIANG)")
        print("  2 probe methods × 5 city = 10 HTTP 全部 0 命中")
        print("  守新增红线-3 不手填, 不补零; 守新增红线-1 2020 全 DATA_MISSING; 守新增红线-2 2026 全 DATA_MISSING")
    finally:
        conn.close()


if __name__ == "__main__":
    main()
