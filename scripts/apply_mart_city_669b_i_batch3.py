#!/usr/bin/env python3
"""669b-i batch3 mart apply — UPDATE-ONLY psycopg2 pattern.

knife 669b-i batch3 (2026-09-13): 5 粤 satellite city harvest (2021-2025).
  GUANGDONG_FOSHAN, GUANGDONG_ZHUHAI, GUANGDONG_HUIZHOU,
  GUANGDONG_JIANGMEN, GUANGDONG_ZHANJIANG
  × 22 city-year × 10 indicators = 220 cells (45 real + 175 DATA_MISSING).

city-year coverage:
  FOSHAN: 2021/2022/2023/2024/2025 = 5 years
  ZHUHAI: 2021/2022/2024 = 3 years (2023/2025 hongheiku 0 entry)
  HUIZHOU: 2021/2022/2023/2024/2025 = 5 years
  JIANGMEN: 2021/2022/2023/2024 = 4 years (2025 hongheiku 0 entry)
  ZHANJIANG: 2021/2022/2023/2024/2025 = 5 years
  Total: 5+3+5+4+5 = 22 city-years × 10 indicator = 220 cells

Per 663 Gap 1 + 669b-i-batch2 UPDATE-ONLY pattern — does NOT DROP.
Reads seed CSV with 250 rows (45 real HONGHEIKU_TRANSLOAD + 205 DATA_MISSING),
UPDATEs applicable cells with correct value/status/missing_reason/lineage_*.
Does NOT re-run mart SQL (dbt CLI bypass).

Stand-alone apply — mart SQL CASE clauses are documentation for future dbt rebuild.

Batch3-specific notes:
- 5 city already in mart (K669a-2020 covered 2020 with DATA_MISSING).
- UPDATE-ONLY (no INSERT) — re-attribution of 2021-2025 lineage_ruling to K669b-i-batch3-*.
- 2020 cells stay at K669a-2020-2026-09-04 (守新增红线-1, 历史年不重复注入).
- 2026 cells stay at K669fix-b-2026-2026-09-09 (守新增红线-2 禁补零).
- 45 real cells breakdown:
    9 HUIZHOU 2021 (all 9 indicators extracted)
    10 JIANGMEN 2023 (all 10 indicators)
    9 ZHANJIANG 2023 (all 9 indicators — fixed_asset 增长% miss)
    8 ZHANJIANG 2024 (8 indicators — gdp_growth + fixed_asset parse miss)
    9 ZHANJIANG 2025 (9 indicators — fixed_asset + trade parse miss)
- 205 DATA_MISSING breakdown (220 total - 45 real = 175 DATA_MISSING):
    5 city × 2021: 50 - 9 (HUIZHOU real) = 41 miss (FOSHAN/ZHUHAI/JIANGMEN/ZHANJIANG 极简)
    5 city × 2022: 50 miss (parser 未匹配)
    4 city × 2023 (ZHUHAI 缺): 40 - 19 = 21 miss (FOSHAN/ZHUHAI/HUIZHOU 极简, ZHUHAI 缺)
    5 city × 2024: 50 - 8 = 42 miss (FOSHAN/ZHUHAI/HUIZHOU/JIANGMEN 极简)
    3 city × 2025 (FOSHAN+ZHUHAI+JIANGMEN 缺): 30 - 9 = 21 miss
- 5 粤 city ≠ 4 直辖市 (守新增红线-7)
- eid_map Format A nested year-keyed JSON loaded from /tmp/669b_i_cache/tag/batch3/
"""
import csv
import json
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
SEED_CSV = "/tmp/669b_i_cache/seed_batch3.csv"
EID_MAP_JSON = "/tmp/669b_i_cache/tag/batch3/eid_map_batch3.json"

CITIES = [
    "GUANGDONG_FOSHAN",
    "GUANGDONG_ZHUHAI",
    "GUANGDONG_HUIZHOU",
    "GUANGDONG_JIANGMEN",
    "GUANGDONG_ZHANJIANG",
]


def get_conn():
    return psycopg2.connect(host=DB_HOST, port=DB_PORT, user=DB_USER,
                            password=DB_PASS, dbname=DB_NAME)


def load_eid_map() -> dict:
    """Load Format A eid_map from JSON: {CITY_CODE: {YEAR: eid}}"""
    raw = json.loads(open(EID_MAP_JSON).read())
    return {city: {int(yr): eid for yr, eid in yrs.items()}
            for city, yrs in raw.items()}


def get_eid_for(city: str, year: int, eid_map: dict) -> str:
    eid = eid_map.get(city, {}).get(year)
    if eid is None:
        return ""
    return str(eid)


def build_origin(eid: str, miss: bool) -> str:
    if not eid:
        return "tjgb.hongheiku.com (no bulletin eid recorded)"
    base = f"tjgb.hongheiku.com/djs/{eid}.html"
    if miss:
        return f"{base} (bulletin parser 未匹配/仅发增长%)"
    return base


def main():
    print(f"=== knife 669b-i batch3 mart apply (UPDATE-ONLY) ===")
    print(f"DB: {DB_HOST}:{DB_PORT}/{DB_NAME}, cities={CITIES}")

    eid_map = load_eid_map()

    real_rows = []   # (city, indicator, year, value, eid)
    miss_rows = []   # (city, indicator, year, missing_reason, eid)
    with open(SEED_CSV, encoding="utf-8") as f:
        for r in csv.DictReader(f):
            if r["city_code"] not in CITIES:
                continue
            yr = int(r["year"])
            ind = r["indicator_key"]
            eid = r.get("bulletin_eid", "")
            if r["status"] == "HONGHEIKU_TRANSLOAD" and r["value"]:
                real_rows.append((r["city_code"], ind, yr, r["value"], eid))
            elif r["status"] == "DATA_MISSING":
                miss_rows.append((r["city_code"], ind, yr, r["missing_reason"], eid))

    print(f"  Real cells: {len(real_rows)}  Missing cells: {len(miss_rows)}")
    print(f"  Expected 220 cells total (22 city-years × 10), got {len(real_rows) + len(miss_rows)}")
    if len(real_rows) + len(miss_rows) != 220:
        print(f"  ✗ Mismatch: expected 220, got {len(real_rows) + len(miss_rows)}")
        sys.exit(1)

    conn = get_conn()
    real_updated = 0
    miss_updated = 0
    try:
        with conn.cursor() as cur:
            # ---- REAL cells: SET value, status=NULL, missing_reason=NULL, lineage_* ----
            for city, indicator, year, value, eid in real_rows:
                lineage_origin = build_origin(eid, miss=False)
                lineage_ruling = f"K669b-i-batch3-parse-{year}-2026-09-13"
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
                lineage_origin = build_origin(eid, miss=True)
                # All batch3 miss cells use K669b-i-batch3-parse-{year}-2026-09-13
                lineage_ruling = f"K669b-i-batch3-parse-{year}-2026-09-13"
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
            print(f"  ✓ Updated {miss_updated} DATA_MISSING cells (parser miss / bulletin 极简 / 增长%)")
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
                    if r > 0 or m > 0:
                        print(f"    {yr}: {r} real + {m} miss")

            # Total batch3 verification
            cur.execute(f"""
                SELECT COUNT(*) FROM {TARGET_SCHEMA}.{MART_NAME}
                WHERE city_code IN ('GUANGDONG_FOSHAN','GUANGDONG_ZHUHAI',
                                    'GUANGDONG_HUIZHOU','GUANGDONG_JIANGMEN',
                                    'GUANGDONG_ZHANJIANG')
                  AND year BETWEEN 2021 AND 2025
                  AND lineage_ruling LIKE 'K669b-i-batch3-%'
            """)
            batch3_tagged = cur.fetchone()[0]
            cur.execute(f"""
                SELECT COUNT(*) FROM {TARGET_SCHEMA}.{MART_NAME}
                WHERE city_code IN ('GUANGDONG_FOSHAN','GUANGDONG_ZHUHAI',
                                    'GUANGDONG_HUIZHOU','GUANGDONG_JIANGMEN',
                                    'GUANGDONG_ZHANJIANG')
                  AND year BETWEEN 2021 AND 2025
                  AND value IS NOT NULL
            """)
            total_real = cur.fetchone()[0]
            cur.execute(f"""
                SELECT COUNT(*) FROM {TARGET_SCHEMA}.{MART_NAME}
                WHERE city_code IN ('GUANGDONG_FOSHAN','GUANGDONG_ZHUHAI',
                                    'GUANGDONG_HUIZHOU','GUANGDONG_JIANGMEN',
                                    'GUANGDONG_ZHANJIANG')
                  AND year BETWEEN 2021 AND 2025
                  AND status = 'DATA_MISSING'
            """)
            total_miss = cur.fetchone()[0]

        print(f"\n=== knife 669b-i batch3 final summary ===")
        print(f"  5 city 2021-2025 tagged with K669b-i-batch3-* ruling: {batch3_tagged} / 220 (matched seed)")
        print(f"  5 city × 5 year real cells: {total_real} (expect 45)")
        print(f"  5 city × 5 year DATA_MISSING: {total_miss} (expect 205 = 250 cells - 45 real)")
        if batch3_tagged != 220 or total_real != 45 or total_miss != 205:
            print(f"  ✗ Mismatch detected — verify needed")
            sys.exit(1)
        print(f"  ✓ All batch3 cells applied correctly (220 updated + 30 pre-existing DATA_MISSING stay)")

    finally:
        conn.close()


if __name__ == "__main__":
    main()