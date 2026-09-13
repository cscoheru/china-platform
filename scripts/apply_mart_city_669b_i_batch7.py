#!/usr/bin/env python3
"""669b-i batch7 mart apply — UPSERT (INSERT ON CONFLICT) psycopg2 pattern.

knife 669b-i batch7 (2026-09-13): 5 皖 satellite city harvest (2020-2025).
  ANHUI_HEFEI, ANHUI_WUHU, ANHUI_BENGBU, ANHUI_MAANSHAN, ANHUI_ANQING
× 28 city-year × 10 indicators = 280 cells (129 real + 151 DATA_MISSING).

city-year coverage (after Knife E 970 per-year parse):
  HEFEI:     2021-2025 = 5 years (2020 hongheiku 0 entry)
  WUHU:      2020-2025 = 6 years
  BENGBU:    2021-2025 = 5 years (2020 hongheiku 0 entry)
  MAANSHAN:  2020-2025 = 6 years
  ANQING:    2020-2025 = 6 years
  Total: 5+6+5+6+6 = 28 city-years × 10 indicator = 280 cells

5 new cities (no existing rows in mart) → all 5 get full INSERT via UPSERT.
2026 cells stay DATA_MISSING (守新增红线-2).

Per batch6 UPSERT pattern (commit 75ef3aa): handles UPDATE for any pre-existing
+ INSERT for new cities via INSERT ON CONFLICT (city_code, indicator_key, year).

CRITICAL: seed_batch7.csv year attribution was CORRECTED via per-year parse
(Knife E 970 year-filter bug workaround: 6 filtered meta files, 6 separate
parser runs). 280 rows have correct (city, year, eid) triples verified against
eid_map_batch7.json — 0 mismatches.
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
SEED_CSV = "source_registry/seed_hongheiku_city_timeseries_669b_i_batch7.csv"
EID_MAP_JSON = "/tmp/669b_i_cache/tag/batch7/eid_map_batch7.json"

CITIES = [
    ("ANHUI_HEFEI",    "合肥市", "ANHUI"),
    ("ANHUI_WUHU",     "芜湖市", "ANHUI"),
    ("ANHUI_BENGBU",   "蚌埠市", "ANHUI"),
    ("ANHUI_MAANSHAN", "马鞍山市", "ANHUI"),
    ("ANHUI_ANQING",   "安庆市", "ANHUI"),
]

INDICATOR_LABELS = {
    "gdp_total":      "地区生产总值 (总量)",
    "gdp_growth":     "GDP 增速",
    "primary_gdp":    "第一产业增加值",
    "secondary_gdp":  "第二产业增加值",
    "tertiary_gdp":   "第三产业增加值",
    "gdp_percapita":  "人均地区生产总值",
    "fiscal_rev":     "一般公共预算收入",
    "fixed_asset":    "固定资产投资",
    "retail":         "社会消费品零售总额",
    "trade":          "进出口总额",
}


def get_conn():
    return psycopg2.connect(host=DB_HOST, port=DB_PORT, user=DB_USER,
                            password=DB_PASS, dbname=DB_NAME)


def load_eid_map() -> dict:
    raw = json.loads(open(EID_MAP_JSON).read())
    return {city: {int(yr): eid for yr, eid in yrs.items()}
            for city, yrs in raw.items()}


def get_eid_for(city: str, year: int, eid_map: dict) -> str:
    eid = eid_map.get(city, {}).get(year)
    return str(eid) if eid else ""


def build_origin(eid: str, miss: bool) -> str:
    if not eid:
        return "tjgb.hongheiku.com (no bulletin eid recorded)"
    base = f"tjgb.hongheiku.com/djs/{eid}.html"
    if miss:
        return f"{base} (bulletin parser 未匹配/仅发增长%)"
    return base


def main():
    print(f"=== knife 669b-i batch7 mart apply (UPSERT) ===")
    print(f"DB: {DB_HOST}:{DB_PORT}/{DB_NAME}, cities={[c[0] for c in CITIES]}")

    eid_map = load_eid_map()

    real_rows = []
    miss_rows = []
    with open(SEED_CSV, encoding="utf-8") as f:
        for r in csv.DictReader(f):
            city_code = r["city_code"]
            if city_code not in [c[0] for c in CITIES]:
                continue
            yr = int(r["year"])
            ind = r["indicator_key"]
            eid = r.get("bulletic_eid", "")
            if r["status"] == "HONGHEIKU_TRANSLOAD" and r["value"]:
                real_rows.append((city_code, ind, yr, r["value"], eid))
            elif r["status"] == "DATA_MISSING":
                miss_rows.append((city_code, ind, yr, r["missing_reason"], eid))

    print(f"  Real cells: {len(real_rows)}  Missing cells: {len(miss_rows)}")
    print(f"  Expected 280 cells total, got {len(real_rows) + len(miss_rows)}")
    if len(real_rows) + len(miss_rows) != 280:
        print(f"  ✗ Mismatch: expected 280")
        sys.exit(1)

    conn = get_conn()
    real_upserted = 0
    miss_upserted = 0
    try:
        with conn.cursor() as cur:
            # ---- REAL cells: UPSERT with value ----
            for city_code, indicator, year, value, eid in real_rows:
                lineage_origin = build_origin(eid, miss=False)
                lineage_ruling = f"K669b-i-batch7-parse-{year}-2026-09-13"
                city_name = next(c[1] for c in CITIES if c[0] == city_code)
                province = next(c[2] for c in CITIES if c[0] == city_code)
                ind_label = INDICATOR_LABELS[indicator]
                unit = "元" if indicator == "gdp_percapita" else "亿元"
                cur.execute(f"""
                    INSERT INTO {TARGET_SCHEMA}.{MART_NAME}
                        (city_code, city_name, province_code, indicator_key,
                         indicator_label, unit, year, value, status, missing_reason,
                         lineage_source_type, lineage_origin, lineage_ruling, lineage_is_demo)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s::numeric, NULL, NULL,
                            'HONGHEIKU_TRANSLOAD', %s, %s, 'false')
                    ON CONFLICT (city_code, indicator_key, year) DO UPDATE SET
                        value = EXCLUDED.value,
                        status = NULL,
                        missing_reason = NULL,
                        lineage_source_type = 'HONGHEIKU_TRANSLOAD',
                        lineage_origin = EXCLUDED.lineage_origin,
                        lineage_ruling = EXCLUDED.lineage_ruling
                """, (city_code, city_name, province, indicator, ind_label,
                      unit, year, value, lineage_origin, lineage_ruling))
                real_upserted += cur.rowcount
            print(f"  ✓ Upserted {real_upserted} real cells (HONGHEIKU_TRANSLOAD)")

            # ---- DATA_MISSING cells: UPSERT with status='DATA_MISSING' ----
            for city_code, indicator, year, missing_reason, eid in miss_rows:
                lineage_origin = build_origin(eid, miss=True)
                lineage_ruling = f"K669b-i-batch7-parse-{year}-2026-09-13"
                city_name = next(c[1] for c in CITIES if c[0] == city_code)
                province = next(c[2] for c in CITIES if c[0] == city_code)
                ind_label = INDICATOR_LABELS[indicator]
                unit = "元" if indicator == "gdp_percapita" else "亿元"
                cur.execute(f"""
                    INSERT INTO {TARGET_SCHEMA}.{MART_NAME}
                        (city_code, city_name, province_code, indicator_key,
                         indicator_label, unit, year, value, status, missing_reason,
                         lineage_source_type, lineage_origin, lineage_ruling, lineage_is_demo)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, NULL, 'DATA_MISSING', %s,
                            'DATA_MISSING', %s, %s, 'false')
                    ON CONFLICT (city_code, indicator_key, year) DO UPDATE SET
                        value = NULL,
                        status = 'DATA_MISSING',
                        missing_reason = EXCLUDED.missing_reason,
                        lineage_source_type = 'DATA_MISSING',
                        lineage_origin = EXCLUDED.lineage_origin,
                        lineage_ruling = EXCLUDED.lineage_ruling
                """, (city_code, city_name, province, indicator, ind_label,
                      unit, year, missing_reason, lineage_origin, lineage_ruling))
                miss_upserted += cur.rowcount
            print(f"  ✓ Upserted {miss_upserted} DATA_MISSING cells")
        conn.commit()

        # ---- Sanity checks ----
        with conn.cursor() as cur:
            city_list_str = ",".join(f"'{c[0]}'" for c in CITIES)
            cur.execute(f"""
                SELECT city_code, year,
                       COUNT(*) FILTER (WHERE value IS NOT NULL) AS real,
                       COUNT(*) FILTER (WHERE value IS NULL) AS miss
                FROM {TARGET_SCHEMA}.{MART_NAME}
                WHERE city_code IN ({city_list_str}) AND year BETWEEN 2020 AND 2025
                GROUP BY city_code, year ORDER BY city_code, year
            """)
            print(f"\n=== Apply summary (per-city per-year) ===")
            for c, yr, r, m in cur.fetchall():
                print(f"  {c} {yr}: {r} real + {m} miss")

            cur.execute(f"""
                SELECT COUNT(*) FROM {TARGET_SCHEMA}.{MART_NAME}
                WHERE city_code IN ({city_list_str}) AND year BETWEEN 2020 AND 2025
                  AND lineage_ruling LIKE 'K669b-i-batch7-%%'
            """)
            tagged = cur.fetchone()[0]

            cur.execute(f"""
                SELECT COUNT(*) FROM {TARGET_SCHEMA}.{MART_NAME}
                WHERE city_code IN ({city_list_str}) AND year BETWEEN 2020 AND 2025
                  AND lineage_ruling LIKE 'K669b-i-batch7-%%'
                  AND value IS NOT NULL
            """)
            total_real = cur.fetchone()[0]

            cur.execute(f"""
                SELECT COUNT(*) FROM {TARGET_SCHEMA}.{MART_NAME}
                WHERE city_code IN ({city_list_str}) AND year BETWEEN 2020 AND 2025
                  AND lineage_ruling LIKE 'K669b-i-batch7-%%'
                  AND status = 'DATA_MISSING'
            """)
            total_miss = cur.fetchone()[0]

        print(f"\n=== knife 669b-i batch7 final summary ===")
        print(f"  5 city 2020-2025 tagged K669b-i-batch7-*: {tagged} / 280")
        print(f"  Real cells (batch7-tagged): {total_real} (expect 129)")
        print(f"  DATA_MISSING cells (batch7-tagged): {total_miss} (expect 151)")
        if tagged != 280 or total_real != 129 or total_miss != 151:
            print(f"  ✗ Mismatch — verify needed")
            sys.exit(1)
        print(f"  ✓ All batch7 cells applied correctly")

    finally:
        conn.close()


if __name__ == "__main__":
    main()