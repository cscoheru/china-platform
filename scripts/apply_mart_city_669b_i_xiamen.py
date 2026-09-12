#!/usr/bin/env python3
"""669b-i-xiamen mart apply — UPDATE-ONLY psycopg2 pattern.

knife 669b-i XIAMEN sub-knife 5/5 (2026-09-12): single-city 5-year harvest (tag page 5 entries).

Per 663 Gap 1 + 669b-i-suzhou pattern — does NOT DROP. Reads seed CSV with 70 rows
(39 real HONGHEIKU_TRANSLOAD + 31 DATA_MISSING), UPDATEs applicable cells with correct
value/status/missing_reason/lineage_*. Does NOT re-run mart SQL (dbt CLI bypass).

Stand-alone apply — mart SQL CASE clauses are documentation for future dbt rebuild.

XIAMEN-specific notes:
- 2020: hongheiku tag 页无 2020 XIAMEN entry (5 entries: 2021/2022/2023/2024/2025, 守新增红线-3)
- 2024: 保留 Knife F attribution (K669b-i-batch1-parse-2024, skip in apply; 7 cells 已在 rd13)
- 2026: 全 DATA_MISSING (守新增红线-2)
- gdp_percapita ×4 (2021/2022/2023/2025): bulletin 无数据 (守新增红线-3)
- 2021 fiscal_rev (1 cell): bulletin parser 未匹配
- fixed_asset ×4 (2021/2022/2023/2025): bulletin 仅发增长%, 无绝对值
- 2024 retail (1 cell): bulletin parser 未匹配 (2024 stays Knife F)
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
SEED_CSV = "/tmp/669b_i_cache/seed_xiamen_full.csv"
CITY_CODE = "FUJIAN_XIAMEN"
XIAMEN_EID = {2021: 24437, 2022: 38423, 2023: 45732, 2024: 57609, 2025: 68649}


def get_conn():
    return psycopg2.connect(host=DB_HOST, port=DB_PORT, user=DB_USER,
                            password=DB_PASS, dbname=DB_NAME)


def main():
    print(f"=== knife 669b-i-xiamen mart apply (UPDATE-ONLY) ===")
    print(f"DB: {DB_HOST}:{DB_PORT}/{DB_NAME}, city={CITY_CODE}")

    # Read seed CSV
    real_rows = []   # (indicator, year, value)
    miss_rows = []   # (indicator, year, missing_reason)
    with open(SEED_CSV, encoding="utf-8") as f:
        for r in csv.DictReader(f):
            if r["city_code"] != CITY_CODE:
                continue
            yr = int(r["year"])
            ind = r["indicator_key"]
            if r["status"] == "HONGHEIKU_TRANSLOAD":
                real_rows.append((ind, yr, r["value"]))
            elif r["status"] == "DATA_MISSING":
                miss_rows.append((ind, yr, r["missing_reason"]))

    print(f"  Real cells: {len(real_rows)}  Missing cells: {len(miss_rows)}")

    if len(real_rows) + len(miss_rows) != 70:
        print(f"  ✗ Expected 70 cells total, got {len(real_rows) + len(miss_rows)}")
        sys.exit(1)

    conn = get_conn()
    updated = 0
    try:
        with conn.cursor() as cur:
            # ---- REAL cells: SET value, status=NULL, missing_reason=NULL, lineage_* ----
            # Skip 2024: stays in rd13 (K669b-i-batch1-parse-2024, Knife F attribution)
            for indicator, year, value in real_rows:
                if year == 2024:
                    continue  # Knife F attribution preserved
                eid = XIAMEN_EID.get(year, "")
                lineage_origin = f"tjgb.hongheiku.com/djs/{eid}.html" if eid else ""
                lineage_ruling = f"K669b-i-xiamen-parse-{year}-2026-09-12"
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
                """, (value, lineage_origin, lineage_ruling, CITY_CODE, indicator, year))
                updated += cur.rowcount
            print(f"  ✓ Updated {updated} real cells (excl 2024 Knife F)")

            # ---- DATA_MISSING cells: SET status='DATA_MISSING', missing_reason, lineage_* ----
            # Skip 2024: stays in rd13 (K669b-i-batch1-parse-2024, Knife F attribution)
            miss_updated = 0
            for indicator, year, missing_reason in miss_rows:
                if year == 2024:
                    # 2024 stays as Knife F attribution — skip
                    continue
                elif year == 2020:
                    # 2020: hongheiku tag 页无 2020 XIAMEN 公告 (5 entries: 2021-2025)
                    lineage_origin = "tjgb.hongheiku.com/tag/厦门市 (no 2020 entry, 守新增红线-3 不手填)"
                    new_ruling = "K669b-i-xiamen-no-bulletin-tag-2020-2026-09-12"
                elif year == 2026:
                    # 2026: 全 DATA_MISSING 守新增红线-2
                    lineage_origin = "none"
                    new_ruling = "pending"
                else:
                    # 2021/2022/2023/2025: gdp_percapita + fixed_asset + 2021 fiscal_rev parser 未匹配
                    eid = XIAMEN_EID.get(year, "")
                    lineage_origin = f"tjgb.hongheiku.com/djs/{eid}.html (bulletin 无数据 / parser 未匹配)"
                    new_ruling = "K669b-i-xiamen-parse-fixed_asset_growth_pct-2026-09-12"
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
                """, (missing_reason, lineage_origin, new_ruling, CITY_CODE, indicator, year))
                miss_updated += cur.rowcount
            print(f"  ✓ Updated {miss_updated} DATA_MISSING cells (excl 2024 Knife F)")
        conn.commit()

        # ---- Sanity checks ----
        with conn.cursor() as cur:
            cur.execute(f"SELECT COUNT(*) FROM {TARGET_SCHEMA}.{MART_NAME} WHERE city_code = %s AND value IS NOT NULL", (CITY_CODE,))
            real_total = cur.fetchone()[0]
            cur.execute(f"SELECT COUNT(*) FROM {TARGET_SCHEMA}.{MART_NAME} WHERE city_code = %s AND value IS NULL", (CITY_CODE,))
            miss_total = cur.fetchone()[0]
            cur.execute(f"SELECT COUNT(*) FROM {TARGET_SCHEMA}.{MART_NAME} WHERE city_code = %s AND lineage_ruling LIKE 'K669b-i-xiamen-%%' AND value IS NOT NULL", (CITY_CODE,))
            ruling_real = cur.fetchone()[0]
            cur.execute(f"SELECT COUNT(*) FROM {TARGET_SCHEMA}.{MART_NAME} WHERE city_code = %s AND lineage_ruling LIKE 'K669b-i-xiamen-%%' AND value IS NULL", (CITY_CODE,))
            ruling_miss = cur.fetchone()[0]
            cur.execute(f"SELECT year, COUNT(*) FILTER (WHERE value IS NOT NULL) AS real, COUNT(*) FILTER (WHERE value IS NULL) AS miss FROM {TARGET_SCHEMA}.{MART_NAME} WHERE city_code = %s GROUP BY year ORDER BY year", (CITY_CODE,))
            year_breakdown = cur.fetchall()

        print(f"\n=== Apply summary ===")
        print(f"  XIAMEN total:       {real_total + miss_total} cells ({real_total} real + {miss_total} missing)")
        print(f"  K669b-i-xiamen:     {ruling_real} real + {ruling_miss} missing")
        print(f"\n  Per-year breakdown:")
        for yr, r, m in year_breakdown:
            print(f"    {yr}: {r} real + {m} missing")

    finally:
        conn.close()


if __name__ == "__main__":
    main()
