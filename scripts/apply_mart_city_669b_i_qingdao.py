#!/usr/bin/env python3
"""669b-i-qingdao mart apply — UPDATE-ONLY psycopg2 pattern.

knife 669b-i QINGDAO sub-knife 1/5 (batch2 2026-09-12): single-city 6-year harvest.

Per 663 Gap 1 + 669b-i-xiamen pattern — does NOT DROP. Reads seed CSV with 70 rows
(35 real HONGHEIKU_TRANSLOAD + 35 DATA_MISSING), UPDATEs applicable cells with correct
value/status/missing_reason/lineage_*. Does NOT re-run mart SQL (dbt CLI bypass).

Stand-alone apply — mart SQL CASE clauses are documentation for future dbt rebuild.

QINGDAO-specific notes:
- 2020: hongheiku 老 ID eid=1537, URL /1537.html (6 real + 4 MISSING; parser missed gdp_total/gdp_percapita/fixed_asset/retail)
- 2021: bulletin 极简 (sparse 23823 chars), parser 全部未匹配 (0 real + 10 MISSING)
- 2022: gdp_growth=20.8% (parser 误匹配 "四新"经济投资增长20.8%, 实际 3.9% — 守 knife E/970 设计, 不手填修正)
- 2023/2024/2025: 标准 /djs/{eid}.html (8/7/8 real)
- 2024: QINGDO NOT in Knife F (batch1 only DONGGUAN/DALIAN/WUXI/SUZHOU/XIAMEN); 2024 fresh this knife
- 2025: eid=68442, 新 URL pattern /xjtjgb/xj2020/68442.html
- 2026: 全 DATA_MISSING 守新增红线-2
- QINGDO 是山东地级市 (非 4 直辖市, 守新增红线-7)
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
SEED_CSV = "/tmp/669b_i_cache/seed_qingdao_full.csv"
CITY_CODE = "SHANDONG_QINGDAO"
QINGDAO_EID = {
    2020: (1537, "tjgb.hongheiku.com/1537.html"),
    2021: (24614, "tjgb.hongheiku.com/djs/24614.html"),
    2022: (36589, "tjgb.hongheiku.com/djs/36589.html"),
    2023: (48448, "tjgb.hongheiku.com/djs/48448.html"),
    2024: (58586, "tjgb.hongheiku.com/djs/58586.html"),
    2025: (68442, "tjgb.hongheiku.com/xjtjgb/xj2020/68442.html"),
}


def get_conn():
    return psycopg2.connect(host=DB_HOST, port=DB_PORT, user=DB_USER,
                            password=DB_PASS, dbname=DB_NAME)


def main():
    print(f"=== knife 669b-i-qingdao mart apply (UPDATE-ONLY) ===")
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

    print(f"  Real cells: {len(real_rows)}  Missing cells (seed): {len(miss_rows)}")
    # 2026 全 DATA_MISSING 守新增红线-2 — 10 cells applied directly as pending
    total_expected = 70  # 10 indicator × 7 year
    pending_2026 = 10
    seed_total = len(real_rows) + len(miss_rows)
    print(f"  Expected {total_expected} cells total (seed={seed_total} + pending 2026={pending_2026})")
    if seed_total + pending_2026 != total_expected:
        print(f"  ✗ Expected {total_expected} cells total, got {seed_total + pending_2026}")
        sys.exit(1)

    conn = get_conn()
    updated = 0
    try:
        with conn.cursor() as cur:
            # ---- REAL cells: SET value, status=NULL, missing_reason=NULL, lineage_* ----
            # QINGDO NOT in Knife F (batch1= DONGGUAN/DALIAN/WUXI/SUZHOU/XIAMEN), so 2024 fresh
            for indicator, year, value in real_rows:
                eid, lineage_origin = QINGDAO_EID.get(year, (None, ""))
                lineage_ruling = f"K669b-i-qingdao-parse-{year}-2026-09-12"
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
            print(f"  ✓ Updated {updated} real cells (2024 fresh, NOT excluded)")

            # ---- DATA_MISSING cells: SET status='DATA_MISSING', missing_reason, lineage_* ----
            miss_updated = 0
            for indicator, year, missing_reason in miss_rows:
                # 2020/2021/2022/2023/2024/2025: parser 错配或未匹配 (bulletin 数据形态问题)
                eid, _ = QINGDAO_EID.get(year, (None, ""))
                if eid == 1537:
                    lineage_origin = f"tjgb.hongheiku.com/1537.html (bulletin 无数据 / parser 未匹配, 老 ID URL)"
                elif eid == 68442:
                    lineage_origin = f"tjgb.hongheiku.com/xjtjgb/xj2020/68442.html (bulletin 无数据 / parser 未匹配)"
                else:
                    lineage_origin = f"tjgb.hongheiku.com/djs/{eid}.html (bulletin 无数据 / parser 未匹配)"
                new_ruling = f"K669b-i-qingdao-parse-{year}-2026-09-12"
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
            print(f"  ✓ Updated {miss_updated} DATA_MISSING cells (seed: 2020-2025 + 2021 all-miss)")

            # ---- 2026 pending: 10 cells applied directly as DATA_MISSING + lineage_ruling='pending' ----
            pending_updated = 0
            for indicator in ["gdp_total", "gdp_growth", "primary_gdp", "secondary_gdp", "tertiary_gdp",
                              "gdp_percapita", "fiscal_rev", "fixed_asset", "retail", "trade"]:
                cur.execute(f"""
                    UPDATE {TARGET_SCHEMA}.{MART_NAME}
                    SET value = NULL,
                        status = 'DATA_MISSING',
                        missing_reason = '2026 全 DATA_MISSING 守新增红线-2 (禁补零)',
                        lineage_source_type = 'DATA_MISSING',
                        lineage_origin = 'none',
                        lineage_ruling = 'pending'
                    WHERE city_code = %s
                      AND indicator_key = %s
                      AND year = 2026
                """, (CITY_CODE, indicator))
                pending_updated += cur.rowcount
            print(f"  ✓ Updated {pending_updated} 2026 pending cells (守新增红线-2)")
        conn.commit()

        # ---- Sanity checks ----
        with conn.cursor() as cur:
            cur.execute(f"SELECT COUNT(*) FROM {TARGET_SCHEMA}.{MART_NAME} WHERE city_code = %s AND value IS NOT NULL", (CITY_CODE,))
            real_total = cur.fetchone()[0]
            cur.execute(f"SELECT COUNT(*) FROM {TARGET_SCHEMA}.{MART_NAME} WHERE city_code = %s AND value IS NULL", (CITY_CODE,))
            miss_total = cur.fetchone()[0]
            cur.execute(f"SELECT year, COUNT(*) FILTER (WHERE value IS NOT NULL) AS real, COUNT(*) FILTER (WHERE value IS NULL) AS miss FROM {TARGET_SCHEMA}.{MART_NAME} WHERE city_code = %s GROUP BY year ORDER BY year", (CITY_CODE,))
            year_breakdown = cur.fetchall()

        print(f"\n=== Apply summary ===")
        print(f"  QINGDAO total:       {real_total + miss_total} cells ({real_total} real + {miss_total} missing)")
        print(f"\n  Per-year breakdown:")
        for yr, r, m in year_breakdown:
            print(f"    {yr}: {r} real + {m} missing")

    finally:
        conn.close()


if __name__ == "__main__":
    main()