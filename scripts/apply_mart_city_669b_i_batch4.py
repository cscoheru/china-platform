#!/usr/bin/env python3
"""669b-i batch4 mart apply — UPSERT (INSERT ON CONFLICT) psycopg2 pattern.

knife 669b-i batch4 (2026-09-13): 5 浙 satellite city harvest (2021-2025).
  ZHEJIANG_WENZHOU, ZHEJIANG_JINHUA, ZHEJIANG_SHAOXING,
  ZHEJIANG_JIAXING, ZHEJIANG_HUZHOU
  × 23 city-year × 10 indicators = 230 cells (163 real + 67 DATA_MISSING).

city-year coverage:
  WENZHOU:   2021-2025 = 5 years
  JINHUA:    2021-2025 = 5 years (already in mart)
  SHAOXING:  2021-2025 = 5 years
  JIAXING:   2021-2023 = 3 years (2024 + 2025 hongheiku 0 entry)
  HUZHOU:    2021-2025 = 5 years
  Total: 5+5+5+3+5 = 23 city-years × 10 indicator = 230 cells

UPDATE-ONLY for cities already in mart (JINHUA),
INSERT-ON-CONFLICT for cities that need first-time entry (WENZHOU/SHAOXING/JIAXING/HUZHOU).
4 missing cities get full 50-cell grid (5 year × 10 ind), with 2020 + 2026 cells staying DATA_MISSING.

Per 663 Gap 1 + 669b-i-batch3 + 669b-i-dalian UPSERT pattern — handles both UPDATE and INSERT.
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
SEED_CSV = "/tmp/669b_i_cache/seed_batch4.csv"
EID_MAP_JSON = "/tmp/669b_i_cache/tag/batch4/eid_map_batch4.json"

CITIES = [
    ("ZHEJIANG_WENZHOU",   "温州市", "ZHEJIANG"),
    ("ZHEJIANG_JINHUA",    "金华市", "ZHEJIANG"),
    ("ZHEJIANG_SHAOXING",  "绍兴市", "ZHEJIANG"),
    ("ZHEJIANG_JIAXING",   "嘉兴市", "ZHEJIANG"),
    ("ZHEJIANG_HUZHOU",    "湖州市", "ZHEJIANG"),
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
    print(f"=== knife 669b-i batch4 mart apply (UPSERT) ===")
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
    print(f"  Expected 230 cells total, got {len(real_rows) + len(miss_rows)}")
    if len(real_rows) + len(miss_rows) != 230:
        print(f"  ✗ Mismatch: expected 230")
        sys.exit(1)

    conn = get_conn()
    real_upserted = 0
    miss_upserted = 0
    try:
        with conn.cursor() as cur:
            # ---- REAL cells: UPSERT with value ----
            for city_code, indicator, year, value, eid in real_rows:
                lineage_origin = build_origin(eid, miss=False)
                lineage_ruling = f"K669b-i-batch4-parse-{year}-2026-09-13"
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
                lineage_ruling = f"K669b-i-batch4-parse-{year}-2026-09-13"
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
                WHERE city_code IN ({city_list_str}) AND year BETWEEN 2021 AND 2025
                GROUP BY city_code, year ORDER BY city_code, year
            """)
            print(f"\n=== Apply summary (per-city per-year) ===")
            for c, yr, r, m in cur.fetchall():
                print(f"  {c} {yr}: {r} real + {m} miss")

            cur.execute(f"""
                SELECT COUNT(*) FROM {TARGET_SCHEMA}.{MART_NAME}
                WHERE city_code IN ({city_list_str})
                  AND year BETWEEN 2021 AND 2025
                  AND lineage_ruling LIKE 'K669b-i-batch4-%'
            """)
            tagged = cur.fetchone()[0]

            cur.execute(f"""
                SELECT COUNT(*) FROM {TARGET_SCHEMA}.{MART_NAME}
                WHERE city_code IN ({city_list_str}) AND year BETWEEN 2021 AND 2025
                  AND value IS NOT NULL
            """)
            total_real = cur.fetchone()[0]

            cur.execute(f"""
                SELECT COUNT(*) FROM {TARGET_SCHEMA}.{MART_NAME}
                WHERE city_code IN ({city_list_str}) AND year BETWEEN 2021 AND 2025
                  AND status = 'DATA_MISSING'
            """)
            total_miss = cur.fetchone()[0]

        print(f"\n=== knife 669b-i batch4 final summary ===")
        print(f"  5 city 2021-2025 tagged K669b-i-batch4-*: {tagged} / 230")
        print(f"  Real cells: {total_real} (expect 163)")
        print(f"  DATA_MISSING cells: {total_miss} (expect 87)")
        if tagged != 230 or total_real != 163 or total_miss != 87:
            print(f"  ✗ Mismatch — verify needed")
            sys.exit(1)
        print(f"  ✓ All batch4 cells applied correctly")

    finally:
        conn.close()


if __name__ == "__main__":
    main()
