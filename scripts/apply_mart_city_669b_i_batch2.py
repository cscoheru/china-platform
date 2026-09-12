#!/usr/bin/env python3
"""669b-i batch2 mart apply — UPDATE-ONLY psycopg2 pattern.

knife 669b-i batch2 (2026-09-13): 4 副省级 city harvest (2021-2025).
  GUANGDONG_SHENZHEN, GUANGDONG_GUANGZHOU, ZHEJIANG_HANGZHOU, ZHEJIANG_NINGBO
  × 5 years × 10 indicators = 200 cells (172 real + 28 DATA_MISSING).

Per 663 Gap 1 + 669b-i-qingdao UPDATE-ONLY pattern — does NOT DROP.
Reads seed CSV with 200 rows (172 real HONGHEIKU_TRANSLOAD + 28 DATA_MISSING),
UPDATEs applicable cells with correct value/status/missing_reason/lineage_*.
Does NOT re-run mart SQL (dbt CLI bypass).

Stand-alone apply — mart SQL CASE clauses are documentation for future dbt rebuild.

Batch2-specific notes:
- 4 city already in mart (K669a-2020 covered 2020 with DATA_MISSING; K669a-2021..2024 covered
  SHENZHEN/GUANGZHOU/HANGZHOU partial; NINGBO was treated as 25 省会 in 669fix-b).
- UPDATE-ONLY (no INSERT) — re-attribution of 2021-2025 lineage_ruling to K669b-i-batch2-*.
- 2020 cells stay at K669a-2020-2026-09-04 (per 4 city 2020 real DATA_MISSING path).
- 2026 cells stay at K669fix-b-2026-2026-09-09 (守新增红线-2 不手填).
- 28 DATA_MISSING breakdown:
    13 fixed_asset 增长% (4 cities, 守红线-3 per 669a-2021 §2)
     6 GUANGZHOU 2021 bulletin 极简 (gdp_total/gdp_growth/primary/secondary/tertiary/gdp_percapita)
     1 HANGZHOU 2021 primary_gdp parse miss
     1 HANGZHOU 2022 gdp_total parse miss
     1 HANGZHOU 2023 gdp_total parse miss
     2 HANGZHOU 2024 fixed_asset+retail parse miss
     1 HANGZHOU 2025 gdp_total parse miss
     3 NINGBO 2024/2025 fixed_asset/trade parse miss (3 cells)
- 4 副省级 city ≠ 4 直辖市 (守新增红线-7)
"""
import csv
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
SEED_CSV = "/Users/kjonekong/projects/china platform/source_registry/seed_hongheiku_city_timeseries_669b_i_batch2.csv"

CITIES = [
    "GUANGDONG_SHENZHEN",
    "GUANGDONG_GUANGZHOU",
    "ZHEJIANG_HANGZHOU",
    "ZHEJIANG_NINGBO",
]


def get_conn():
    return psycopg2.connect(host=DB_HOST, port=DB_PORT, user=DB_USER,
                            password=DB_PASS, dbname=DB_NAME)


def main():
    print(f"=== knife 669b-i batch2 mart apply (UPDATE-ONLY) ===")
    print(f"DB: {DB_HOST}:{DB_PORT}/{DB_NAME}, cities={CITIES}")

    # Read seed CSV
    real_rows = []   # (city, indicator, year, value, eid)
    miss_rows = []   # (city, indicator, year, missing_reason, eid)
    with open(SEED_CSV, encoding="utf-8") as f:
        for r in csv.DictReader(f):
            if r["city_code"] not in CITIES:
                continue
            yr = int(r["year"])
            ind = r["indicator_key"]
            eid = r.get("bulletin_eid", "")
            if r["status"] == "real":
                real_rows.append((r["city_code"], ind, yr, r["value"], eid))
            elif r["status"] == "DATA_MISSING":
                miss_rows.append((r["city_code"], ind, yr, r["missing_reason"], eid))

    print(f"  Real cells: {len(real_rows)}  Missing cells: {len(miss_rows)}")
    print(f"  Expected 200 cells total (4 × 5 × 10), got {len(real_rows) + len(miss_rows)}")
    if len(real_rows) + len(miss_rows) != 200:
        print(f"  ✗ Mismatch: expected 200, got {len(real_rows) + len(miss_rows)}")
        sys.exit(1)

    conn = get_conn()
    real_updated = 0
    miss_updated = 0
    try:
        with conn.cursor() as cur:
            # ---- REAL cells: SET value, status=NULL, missing_reason=NULL, lineage_* ----
            for city, indicator, year, value, eid in real_rows:
                if int(eid) >= 70000:  # 2025 eids are 69xxx-72xxx, xjtjgb pattern
                    lineage_origin = f"tjgb.hongheiku.com/xjtjgb/xj2020/{eid}.html"
                else:
                    lineage_origin = f"tjgb.hongheiku.com/djs/{eid}.html"
                lineage_ruling = f"K669b-i-batch2-parse-{year}-2026-09-13"
                cur.execute(f"""
                    UPDATE {TARGET_SCHEMA}.{MART_NAME}
                    SET value = %s::numeric,
                        status = NULL,
                        missing_reason = NULL,
                        lineage_source_type = 'HONGHEIKU_TRANSLOAD',
                        lineage_origin = %s,
                        lineage_ruling = %s
                    WHERE city_code = %s
                      AND indicator_key = %s
                      AND year = %s
                """, (value, lineage_origin, lineage_ruling, city, indicator, year))
                real_updated += cur.rowcount
            print(f"  ✓ Updated {real_updated} real cells (HONGHEIKU_TRANSLOAD)")

            # ---- DATA_MISSING cells: SET status='DATA_MISSING', missing_reason, lineage_* ----
            for city, indicator, year, missing_reason, eid in miss_rows:
                if eid:
                    if int(eid) >= 70000:
                        lineage_origin = f"tjgb.hongheiku.com/xjtjgb/xj2020/{eid}.html (bulletin parser 未匹配/仅发增长%)"
                    else:
                        lineage_origin = f"tjgb.hongheiku.com/djs/{eid}.html (bulletin parser 未匹配/仅发增长%)"
                else:
                    lineage_origin = "tjgb.hongheiku.com (no bulletin eid recorded)"
                # All batch2 miss cells use K669b-i-batch2-parse-{year}-2026-09-13 (parser outcome, same ruling as real)
                lineage_ruling = f"K669b-i-batch2-parse-{year}-2026-09-13"
                cur.execute(f"""
                    UPDATE {TARGET_SCHEMA}.{MART_NAME}
                    SET value = NULL,
                        status = 'DATA_MISSING',
                        missing_reason = %s,
                        lineage_source_type = 'DATA_MISSING',
                        lineage_origin = %s,
                        lineage_ruling = %s
                    WHERE city_code = %s
                      AND indicator_key = %s
                      AND year = %s
                """, (missing_reason, lineage_origin, lineage_ruling, city, indicator, year))
                miss_updated += cur.rowcount
            print(f"  ✓ Updated {miss_updated} DATA_MISSING cells (parser miss / 增长% / bulletin 极简)")
        conn.commit()

        # ---- Sanity checks per city ----
        with conn.cursor() as cur:
            print(f"\n=== Apply summary (per-city 2021-2025 cell counts) ===")
            for city in CITIES:
                cur.execute(f"""
                    SELECT year,
                           COUNT(*) FILTER (WHERE value IS NOT NULL) AS real,
                           COUNT(*) FILTER (WHERE value IS NULL) AS miss
                    FROM {TARGET_SCHEMA}.{MART_NAME}
                    WHERE city_code = %s AND year BETWEEN 2021 AND 2025
                    GROUP BY year ORDER BY year
                """, (city,))
                rows = cur.fetchall()
                city_real = sum(r for _, r, _ in rows)
                city_miss = sum(m for _, _, m in rows)
                print(f"  {city}: {city_real} real + {city_miss} miss (50 cells 2021-2025)")
                for yr, r, m in rows:
                    if m > 0:
                        print(f"    {yr}: {r} real + {m} miss")

            # Total batch2 verification
            cur.execute(f"""
                SELECT COUNT(*) FROM {TARGET_SCHEMA}.{MART_NAME}
                WHERE city_code IN ('GUANGDONG_SHENZHEN','GUANGDONG_GUANGZHOU',
                                    'ZHEJIANG_HANGZHOU','ZHEJIANG_NINGBO')
                  AND year BETWEEN 2021 AND 2025
                  AND lineage_ruling LIKE 'K669b-i-batch2-%'
            """)
            batch2_tagged = cur.fetchone()[0]
            cur.execute(f"""
                SELECT COUNT(*) FROM {TARGET_SCHEMA}.{MART_NAME}
                WHERE city_code IN ('GUANGDONG_SHENZHEN','GUANGDONG_GUANGZHOU',
                                    'ZHEJIANG_HANGZHOU','ZHEJIANG_NINGBO')
                  AND year BETWEEN 2021 AND 2025
                  AND value IS NOT NULL
            """)
            total_real = cur.fetchone()[0]
            cur.execute(f"""
                SELECT COUNT(*) FROM {TARGET_SCHEMA}.{MART_NAME}
                WHERE city_code IN ('GUANGDONG_SHENZHEN','GUANGDONG_GUANGZHOU',
                                    'ZHEJIANG_HANGZHOU','ZHEJIANG_NINGBO')
                  AND year BETWEEN 2021 AND 2025
                  AND status = 'DATA_MISSING'
            """)
            total_miss = cur.fetchone()[0]

        print(f"\n=== knife 669b-i batch2 final summary ===")
        print(f"  4 副省级 city 2021-2025 tagged with K669b-i-batch2-* ruling: {batch2_tagged} / 200")
        print(f"  4 city × 5 year real cells: {total_real} (expect 172)")
        print(f"  4 city × 5 year DATA_MISSING: {total_miss} (expect 28)")
        if batch2_tagged != 200 or total_real != 172 or total_miss != 28:
            print(f"  ✗ Mismatch detected — verify needed")
            sys.exit(1)
        print(f"  ✓ All 200 batch2 cells applied correctly")

    finally:
        conn.close()


if __name__ == "__main__":
    main()