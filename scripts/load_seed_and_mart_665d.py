#!/usr/bin/env python3
"""665d load_seed_and_mart.py — bypass dbt CLI (663 Gap 1) via direct psycopg2.

Mirrors 665a/665b/665c pattern for 2024 增量 data:
  1. Load seed_hongheiku_timeseries_2024.csv → cegr_staging.seed_hongheiku_timeseries_2024
  2. Re-run mart with 2024_extra added to real_data UNION (mart_province_timeseries.sql now
     references seed_hongheiku_timeseries_2024 alongside 2021 + 2022 + 2023)
  3. Verify 16 base 红线 + new 2024-specific checks
     - GUANGDONG 2024 has 5 增量 (cat URL id 57657 = real 公报, vs 2022/2023 PDF 目录页)
     - 3 missing provinces (GUIZHOU/HAINAN/LIAONING) 全 DATA_MISSING (沿用 660 红线)
     - real cells 2024 = 135 (5 现 from 663 baseline) + 122 (5 增量 from 665d) = 257
     - lineage_ruling bumped K665c → K665d on full 8060 rows

After load:
  - Total mart rows: 8060 (unchanged — cross product is 31 × 10 × 26)
  - Real cells: 861 (prior) + 122 (665d 2024 增量) = 983

K665c → K665d ruling:
  - 665c extends real_data with year 2023 (10 指标 × 30/31 省)
  - 665d extends real_data with year 2024 5 增量 (5 增量 × 28 省; 3 missing 沿用 660 红线)
  - ruling bump: K665c-2026-09-04 → K665d-2026-09-04 (mart 全 8060 行)
"""
import csv
import psycopg2
from pathlib import Path

DSN = dict(host='127.0.0.1', port=55440, user='postgres', password='postgres', dbname='cegr_test')


def load_seed_2024(conn) -> int:
    csv_path = Path(
        '/Users/kjonekong/projects/china platform/dbt/seeds/'
        'seed_hongheiku_timeseries_2024.csv'
    )
    with csv_path.open('r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        rows = list(reader)
    print(f'Loaded {len(rows)} rows from {csv_path.name}')

    cur = conn.cursor()
    cur.execute('DROP TABLE IF EXISTS cegr_staging.seed_hongheiku_timeseries_2024')
    cur.execute('''
        CREATE TABLE cegr_staging.seed_hongheiku_timeseries_2024 (
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
        INSERT INTO cegr_staging.seed_hongheiku_timeseries_2024
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
    print(f'Inserted {len(rows)} rows into cegr_staging.seed_hongheiku_timeseries_2024')
    return len(rows)


def run_mart(conn) -> int:
    sql_path = Path(
        '/Users/kjonekong/projects/china platform/dbt/models/marts/'
        'mart_province_timeseries.sql'
    )
    sql = sql_path.read_text(encoding='utf-8')

    # Substitute all 4 ref() calls (2021 + 2022 + 2023 + 2024)
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
    sql = sql.replace(
        "{{ ref('seed_hongheiku_timeseries_2024') }}",
        "cegr_staging.seed_hongheiku_timeseries_2024",
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
    print('\n=== 665d 验证 (16 base 红线 + new K665d 守门) ===')

    K666b_RECLASS_PROVINCES = "'GUANGDONG', 'JIANGSU', 'ZHEJIANG'"
    K666b_RECLASS_INDICATORS = (
        "'gdp_total', 'gdp_growth', 'primary_gdp', "
        "'secondary_gdp', 'tertiary_gdp'"
    )
    K665d_5_INCREMENTAL = "'gdp_percapita', 'fiscal_rev', 'fixed_asset', 'retail', 'trade'"
    K665d_MISSING_3 = "'GUIZHOU', 'HAINAN', 'LIAONING'"

    checks = [
        # ─── 16 base 红线 (沿用 665a/665b/665c/666b 守门) ───
        ('总行数 = 8060',
         'SELECT COUNT(*) FROM cegr_mart.mart_province_timeseries', 8060),
        ('real cells 2024 (5 现 from 663 baseline + 5 增量 from 665d) = 257',
         "SELECT COUNT(*) FROM cegr_mart.mart_province_timeseries WHERE year=2024 AND value IS NOT NULL", 257),
        ('real cells 2021 (665a) = 251',
         "SELECT COUNT(*) FROM cegr_mart.mart_province_timeseries WHERE year=2021 AND value IS NOT NULL", 251),
        ('real cells 2022 (665b) = 204',
         "SELECT COUNT(*) FROM cegr_mart.mart_province_timeseries WHERE year=2022 AND value IS NOT NULL", 204),
        ('real cells 2023 (665c) = 271',
         "SELECT COUNT(*) FROM cegr_mart.mart_province_timeseries WHERE year=2023 AND value IS NOT NULL", 271),
        ('real cells total = 983 (135 + 251 + 204 + 271 + 122)',
         "SELECT COUNT(*) FROM cegr_mart.mart_province_timeseries WHERE value IS NOT NULL", 983),
        ('HUNAN 2022 全 DATA_MISSING',
         "SELECT COUNT(*) FROM cegr_mart.mart_province_timeseries WHERE province_code='HUNAN' AND year=2022 AND value IS NOT NULL", 0),
        ('GUANGDONG 2022 全 DATA_MISSING (665b 目录页)',
         "SELECT COUNT(*) FROM cegr_mart.mart_province_timeseries WHERE province_code='GUANGDONG' AND year=2022 AND value IS NOT NULL", 0),
        ('JIANGXI 2022 全 DATA_MISSING',
         "SELECT COUNT(*) FROM cegr_mart.mart_province_timeseries WHERE province_code='JIANGXI' AND year=2022 AND value IS NOT NULL", 0),
        ('LIAONING/GUIZHOU 2022 全 DATA_MISSING',
         "SELECT COUNT(*) FROM cegr_mart.mart_province_timeseries WHERE province_code IN ('LIAONING','GUIZHOU') AND year=2022 AND value IS NOT NULL", 0),
        ('HAINAN 2022 有 real cells (10/10)',
         "SELECT COUNT(*) FROM cegr_mart.mart_province_timeseries WHERE province_code='HAINAN' AND year=2022 AND value IS NOT NULL", 10),
        ('2001-2019 全 DATA_MISSING (新增红线-1)',
         "SELECT COUNT(*) FROM cegr_mart.mart_province_timeseries WHERE year BETWEEN 2001 AND 2019 AND value IS NOT NULL", 0),
        ('2026 全 DATA_MISSING (新增红线-2)',
         "SELECT COUNT(*) FROM cegr_mart.mart_province_timeseries WHERE year=2026 AND value IS NOT NULL", 0),
        ('value IS NULL → status DATA_MISSING',
         "SELECT COUNT(*) FROM cegr_mart.mart_province_timeseries WHERE value IS NULL AND status != 'DATA_MISSING'", 0),
        ('lineage_source_type 全填',
         "SELECT COUNT(*) FROM cegr_mart.mart_province_timeseries WHERE lineage_source_type IS NULL", 0),
        ('lineage_origin 全填',
         "SELECT COUNT(*) FROM cegr_mart.mart_province_timeseries WHERE lineage_origin IS NULL", 0),

        # ─── new K665d 2024 红线 (10 验证) ───
        # 5 增量 2024 守门
        ('2024 gdp_percapita real = 24 (28 省 - 4 missing)',
         f"SELECT COUNT(*) FROM cegr_mart.mart_province_timeseries "
         f"WHERE year=2024 AND indicator_key='gdp_percapita' AND value IS NOT NULL", 24),
        ('2024 fiscal_rev real = 25 (28 省 - 3 missing)',
         f"SELECT COUNT(*) FROM cegr_mart.mart_province_timeseries "
         f"WHERE year=2024 AND indicator_key='fiscal_rev' AND value IS NOT NULL", 25),
        ('2024 fixed_asset real = 27 (28 省 - 1 missing)',
         f"SELECT COUNT(*) FROM cegr_mart.mart_province_timeseries "
         f"WHERE year=2024 AND indicator_key='fixed_asset' AND value IS NOT NULL", 27),
        ('2024 retail real = 23 (28 省 - 5 missing)',
         f"SELECT COUNT(*) FROM cegr_mart.mart_province_timeseries "
         f"WHERE year=2024 AND indicator_key='retail' AND value IS NOT NULL", 23),
        ('2024 trade real = 23 (28 省 - 5 missing)',
         f"SELECT COUNT(*) FROM cegr_mart.mart_province_timeseries "
         f"WHERE year=2024 AND indicator_key='trade' AND value IS NOT NULL", 23),

        # 3 missing 省 2024 全 DATA_MISSING (沿用 660 红线, 不在 665d harvest)
        ('3 missing-2024 省 (GUIZHOU/HAINAN/LIAONING) 全 DATA_MISSING',
         f"SELECT COUNT(*) FROM cegr_mart.mart_province_timeseries "
         f"WHERE province_code IN ({K665d_MISSING_3}) AND year=2024 AND value IS NOT NULL", 0),

        # GUANGDONG 2024 5 增量 全有 (cat URL id 57657 是真公报)
        ('GUANGDONG 2024 5 增量 全有 (cat URL id 57657 真公报)',
         f"SELECT COUNT(*) FROM cegr_mart.mart_province_timeseries "
         f"WHERE province_code='GUANGDONG' AND year=2024 "
         f"AND indicator_key IN ({K665d_5_INCREMENTAL}) AND value IS NOT NULL", 5),

        # K666b 升级保留 (未被 K665d 覆盖): 3 省 × 5 现 × {2021, 2022, 2024} = 29 cells
        ('K666b 升级保留 = 29 (3 省 × 5 现 × {2021, 2022, 2024})',
         f"SELECT COUNT(*) FROM cegr_mart.mart_province_timeseries "
         f"WHERE province_code IN ({K666b_RECLASS_PROVINCES}) "
         f"AND indicator_key IN ({K666b_RECLASS_INDICATORS}) "
         f"AND year IN (2021, 2022, 2024) "
         f"AND value IS NOT NULL "
         f"AND lineage_source_type = 'OFFICIAL_INTAKED'", 29),

        # K665d ruling 已替换 K665c (mart 全 8060 行)
        ('K665d ruling 已替换 K665c (mart 全 8060 行)',
         "SELECT COUNT(*) FROM cegr_mart.mart_province_timeseries "
         "WHERE lineage_ruling = 'K665d-2026-09-04'", 8060),

        # K665c ruling 已不存在 (K665d 完全替换)
        ('K665c ruling 全 0 行 (K665d 完全替换)',
         "SELECT COUNT(*) FROM cegr_mart.mart_province_timeseries "
         "WHERE lineage_ruling = 'K665c-2026-09-04'", 0),
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
        seed_n = load_seed_2024(conn)
        mart_n = run_mart(conn)
        ok = verify_red_lines(conn)
        return 0 if ok else 1
    finally:
        conn.close()


if __name__ == '__main__':
    raise SystemExit(main())