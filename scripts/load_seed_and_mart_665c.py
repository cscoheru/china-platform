#!/usr/bin/env python3
"""665c load_seed_and_mart.py — bypass dbt CLI (663 Gap 1) via direct psycopg2.

Mirrors 665a/665b/665c pattern for 2023 data:
  1. Load seed_hongheiku_timeseries_2023.csv → cegr_staging.seed_hongheiku_timeseries_2023
  2. Re-run mart with 2023 added to real_data UNION (mart_province_timeseries.sql now references
     seed_hongheiku_timeseries_2023 alongside 2021 + 2022)
  3. Verify 16 base 红线 + new 2023-specific checks
     - GUANGDONG 2023 still DATA_MISSING (PDF 目录页, parse_empty)
     - 7 之前 missing 省 now have 2023 real cells (gansu/guizhou/heilongjiang/hunan/jiangxi/
       liaoning/ningxia/shanghai)
     - real cells 2023 ~ 270 (one per (province, indicator) pair excluding GUANGDONG misses)
     - lineage_ruling bumped K666b → K665c on full 8060 rows

After load:
  - Total mart rows: 8060 (unchanged — cross product is 31 × 10 × 26)
  - Real cells: 590 (prior) + 270 (665c 2023) ≈ 860
  - 2023 cells real ≈ 270 (GUANGDONG 0; 30 其他省 × ~9 指标 avg)

K666b → K665c ruling:
  - 666b reclassify 3 省 × 5 现 × {2021, 2022, 2024} → OFFICIAL_INTAKED (29 cells)
  - 665c extends real_data with year 2023 (no reclassify — 2023 not in 666b 3 省 × {2021, 2022, 2024})
  - ruling bump: K666b-2026-09-04 → K665c-2026-09-04 (mart 全 8060 行)
"""
import csv
import psycopg2
from pathlib import Path

DSN = dict(host='127.0.0.1', port=55440, user='postgres', password='postgres', dbname='cegr_test')


def load_seed_2023(conn) -> int:
    csv_path = Path(
        '/Users/kjonekong/projects/china platform/dbt/seeds/'
        'seed_hongheiku_timeseries_2023.csv'
    )
    with csv_path.open('r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        rows = list(reader)
    print(f'Loaded {len(rows)} rows from {csv_path.name}')

    cur = conn.cursor()
    cur.execute('DROP TABLE IF EXISTS cegr_staging.seed_hongheiku_timeseries_2023')
    cur.execute('''
        CREATE TABLE cegr_staging.seed_hongheiku_timeseries_2023 (
            province_code VARCHAR(32),
            province_name_cn VARCHAR(64),
            year INTEGER,
            value NUMERIC,
            unit VARCHAR(16),
            indicator_key VARCHAR(64),
            indicator_label_cn VARCHAR(128),
            status VARCHAR(32),
            missing_reason TEXT,
            lineage_source_type VARCHAR(32),
            lineage_origin TEXT,
            lineage_ruling VARCHAR(64),
            lineage_is_demo VARCHAR(8)
        )
    ''')
    insert_sql = '''
        INSERT INTO cegr_staging.seed_hongheiku_timeseries_2023
        (province_code, province_name_cn, year, value, unit, indicator_key,
         indicator_label_cn, status, missing_reason, lineage_source_type,
         lineage_origin, lineage_ruling, lineage_is_demo)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    '''
    for r in rows:
        val = r['value']
        v_num = float(val) if val else None
        cur.execute(insert_sql, (
            r['province_code'], r['province_name_cn'], int(r['year']),
            v_num, r['unit'], r['indicator_key'], r['indicator_label_cn'],
            r['status'] or None, r['missing_reason'] or None,
            r['lineage_source_type'], r['lineage_origin'],
            r['lineage_ruling'], r['lineage_is_demo'],
        ))
    conn.commit()
    print(f'Inserted {len(rows)} rows into cegr_staging.seed_hongheiku_timeseries_2023')
    return len(rows)


def run_mart(conn) -> int:
    sql_path = Path(
        '/Users/kjonekong/projects/china platform/dbt/models/marts/'
        'mart_province_timeseries.sql'
    )
    sql = sql_path.read_text(encoding='utf-8')

    # Substitute all 3 ref() calls (2021 + 2022 + 2023)
    sql = sql.replace(
        "{{ ref('seed_hongheiku_timeseries_2021') }}",
        "cegr_staging.seed_hongheiku_timeseries_2021",
    )
    sql = sql.replace(
        "{{ ref('seed_hongheiku_timeseries_2022') }}",
        "cegr_staging.seed_hongheiku_timeseries_2022",
    )
    sql = sql.replace(
        "{{ ref('seed_hongheiku_timeseries_2023') }}",
        "cegr_staging.seed_hongheiku_timeseries_2023",
    )

    # Strip the Jinja config block
    sql = sql.replace(
        "{{\n    config(\n        materialized='table',\n        schema='mart',\n        tags=['mart', 'timeseries', 'p2', 'china_platform']\n    )\n}}",
        "",
    )

    cur = conn.cursor()
    cur.execute('DROP TABLE IF EXISTS cegr_mart.mart_province_timeseries CASCADE')
    cur.execute('CREATE TABLE cegr_mart.mart_province_timeseries AS ' + sql)
    conn.commit()
    cur.execute('SELECT COUNT(*) FROM cegr_mart.mart_province_timeseries')
    n = cur.fetchone()[0]
    print(f'mart rows: {n}')
    return n


def verify_red_lines(conn) -> bool:
    cur = conn.cursor()
    print('\n=== 665c 验证 (16 base 红线 + new K665c 守门) ===')

    K666b_RECLASS_PROVINCES = "'GUANGDONG', 'JIANGSU', 'ZHEJIANG'"
    K666b_RECLASS_INDICATORS = (
        "'gdp_total', 'gdp_growth', 'primary_gdp', "
        "'secondary_gdp', 'tertiary_gdp'"
    )

    checks = [
        # ─── 16 base 红线 (沿用 665a/665b/666b 守门) ───
        ('总行数 = 8060',
         'SELECT COUNT(*) FROM cegr_mart.mart_province_timeseries', 8060),
        ('real cells 2024 (663 baseline) = 135',
         "SELECT COUNT(*) FROM cegr_mart.mart_province_timeseries WHERE year=2024 AND value IS NOT NULL", 135),
        ('real cells 2021 (665a) = 251',
         "SELECT COUNT(*) FROM cegr_mart.mart_province_timeseries WHERE year=2021 AND value IS NOT NULL", 251),
        ('real cells 2022 (665b) = 204',
         "SELECT COUNT(*) FROM cegr_mart.mart_province_timeseries WHERE year=2022 AND value IS NOT NULL", 204),
        ('real cells 2023 (665c new) = 271 (30/31 PARSED + 1 gdp_growth cell)',
         "SELECT COUNT(*) FROM cegr_mart.mart_province_timeseries WHERE year=2023 AND value IS NOT NULL", 271),
        ('real cells total = 861 (135 + 251 + 204 + 271)',
         "SELECT COUNT(*) FROM cegr_mart.mart_province_timeseries WHERE value IS NOT NULL", 861),
        ('HUNAN 2022 全 DATA_MISSING (年鉴滞后, 665c 2023 才入库)',
         "SELECT COUNT(*) FROM cegr_mart.mart_province_timeseries WHERE province_code='HUNAN' AND year=2022 AND value IS NOT NULL", 0),
        ('GUANGDONG 2022 全 DATA_MISSING (665b 目录页 PDF 未解析)',
         "SELECT COUNT(*) FROM cegr_mart.mart_province_timeseries WHERE province_code='GUANGDONG' AND year=2022 AND value IS NOT NULL", 0),
        ('JIANGXI 2022 全 DATA_MISSING (同上)',
         "SELECT COUNT(*) FROM cegr_mart.mart_province_timeseries WHERE province_code='JIANGXI' AND year=2022 AND value IS NOT NULL", 0),
        ('LIAONING/GUIZHOU 2022 全 DATA_MISSING',
         "SELECT COUNT(*) FROM cegr_mart.mart_province_timeseries WHERE province_code IN ('LIAONING','GUIZHOU') AND year=2022 AND value IS NOT NULL", 0),
        ('HAINAN 2022 有 real cells (10/10)',
         "SELECT COUNT(*) FROM cegr_mart.mart_province_timeseries WHERE province_code='HAINAN' AND year=2022 AND value IS NOT NULL", 10),
        ('2001-2019 全 DATA_MISSING (新增红线-1)',
         "SELECT COUNT(*) FROM cegr_mart.mart_province_timeseries WHERE year BETWEEN 2001 AND 2019 AND value IS NOT NULL", 0),
        ('2026 全 DATA_MISSING (新增红线-2)',
         "SELECT COUNT(*) FROM cegr_mart.mart_province_timeseries WHERE year=2026 AND value IS NOT NULL", 0),
        ('value IS NULL → status DATA_MISSING (禁补零)',
         "SELECT COUNT(*) FROM cegr_mart.mart_province_timeseries WHERE value IS NULL AND status != 'DATA_MISSING'", 0),
        ('lineage_source_type 全填',
         "SELECT COUNT(*) FROM cegr_mart.mart_province_timeseries WHERE lineage_source_type IS NULL", 0),
        ('lineage_origin 全填',
         "SELECT COUNT(*) FROM cegr_mart.mart_province_timeseries WHERE lineage_origin IS NULL", 0),

        # ─── new K665c 2023 红线 (10 验证) ───
        # GUANGDONG 2023 PARSE_EMPTY (PDF 目录页, no row in seed) → DATA_MISSING 守红线-1
        ('GUANGDONG 2023 全 DATA_MISSING (PDF 目录页 PARSE_EMPTY)',
         "SELECT COUNT(*) FROM cegr_mart.mart_province_timeseries WHERE province_code='GUANGDONG' AND year=2023 AND value IS NOT NULL", 0),

        # 7 之前 missing 2022 省 now has 2023 real cells
        # (gansu/guizhou/heilongjiang/hunan/jiangxi/liaoning/ningxia/shanghai — 8 省 not 7)
        # 实际是 8 省; 计数 = 8 × 10 = ~80 cells for 2023, 但 primary/secondary/tertiary
        # 缺失率高 (27/31 per indicator), 实际 ≥60 cells.
        ('8 missing-2022 省 now have 2023 real cells = 73 (gansu 10/guizhou 8/heilongjiang 7/hunan 9/jiangxi 10/liaoning 10/ningxia 10/shanghai 9)',
         "SELECT COUNT(*) FROM cegr_mart.mart_province_timeseries "
         "WHERE province_code IN ('GANSU','GUIZHOU','HEILONGJIANG','HUNAN','JIANGXI','LIAONING','NINGXIA','SHANGHAI') "
         "AND year=2023 AND value IS NOT NULL", 73),

        # 5 现 2023 指标守门 (gdp_total ≥ 29, gdp_growth = 30, primary/secondary/tertiary ≥ 27)
        ('2023 gdp_total real = 29 (30/31 - GUANGDONG PDF)',
         "SELECT COUNT(*) FROM cegr_mart.mart_province_timeseries WHERE year=2023 AND indicator_key='gdp_total' AND value IS NOT NULL", 29),
        ('2023 gdp_growth real = 30 (31/31 — all 省)',
         "SELECT COUNT(*) FROM cegr_mart.mart_province_timeseries WHERE year=2023 AND indicator_key='gdp_growth' AND value IS NOT NULL", 30),
        ('2023 secondary_gdp real = 28 (30/31 - GUANGDONG - 1 missing)',
         "SELECT COUNT(*) FROM cegr_mart.mart_province_timeseries WHERE year=2023 AND indicator_key='secondary_gdp' AND value IS NOT NULL", 28),

        # 5 增量 2023 守门 (新增红线-3)
        ('2023 gdp_percapita real ≥ 27',
         "SELECT COUNT(*) FROM cegr_mart.mart_province_timeseries WHERE year=2023 AND indicator_key='gdp_percapita' AND value IS NOT NULL", 27),
        ('2023 fiscal_rev real ≥ 24',
         "SELECT COUNT(*) FROM cegr_mart.mart_province_timeseries WHERE year=2023 AND indicator_key='fiscal_rev' AND value IS NOT NULL", 24),

        # K666b 升级保留 (未被 K665c 覆盖): 3 省 × 5 现 × {2021, 2022, 2024} = 29 cells
        ('K666b 升级保留 = 29 (3 省 × 5 现 × {2021, 2022, 2024})',
         f"SELECT COUNT(*) FROM cegr_mart.mart_province_timeseries "
         f"WHERE province_code IN ({K666b_RECLASS_PROVINCES}) "
         f"AND indicator_key IN ({K666b_RECLASS_INDICATORS}) "
         f"AND year IN (2021, 2022, 2024) "
         f"AND value IS NOT NULL "
         f"AND lineage_source_type = 'OFFICIAL_INTAKED'", 29),

        # K665c ruling 已替换 K666b (mart 全 8060 行)
        ('K665c ruling 已替换 K666b (mart 全 8060 行)',
         "SELECT COUNT(*) FROM cegr_mart.mart_province_timeseries "
         "WHERE lineage_ruling = 'K665c-2026-09-04'", 8060),

        # K666b ruling 已不存在 (K665c 完全替换)
        ('K666b ruling 全 0 行 (K665c 完全替换)',
         "SELECT COUNT(*) FROM cegr_mart.mart_province_timeseries "
         "WHERE lineage_ruling = 'K666b-2026-09-04'", 0),
    ]

    all_ok = True
    for name, sql, expected in checks:
        cur.execute(sql)
        result = cur.fetchone()
        actual = result[0]
        if actual == expected:
            status = '✓'
        else:
            status = '✗ FAIL'
            all_ok = False
        print(f'  [{status}] {name}: {actual} (expected {expected})')

    return all_ok


def main() -> int:
    conn = psycopg2.connect(**DSN)
    try:
        seed_n = load_seed_2023(conn)
        mart_n = run_mart(conn)
        ok = verify_red_lines(conn)
        return 0 if ok else 1
    finally:
        conn.close()


if __name__ == '__main__':
    raise SystemExit(main())