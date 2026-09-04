#!/usr/bin/env python3
"""665e load_seed_and_mart.py — bypass dbt CLI (663 Gap 1) via direct psycopg2.

Mirrors 665a/665b/665c/665d pattern for 2025 全量 (10 指标) data:
  1. Load seed_hongheiku_timeseries_2025.csv → cegr_staging.seed_hongheiku_timeseries_2025
  2. Re-run mart with 2025 added to real_data UNION (mart_province_timeseries.sql now
     references seed_hongheiku_timeseries_2025 alongside 2021 + 2022 + 2023 + 2024)
  3. Verify 16 base 红线 + new 2025-specific checks
     - LIAONING 2025 全 DATA_MISSING (沿用 660 红线永久缺文)
     - real cells 2025 = 283 (10 指标 ALL: 29+30+30+30+29+26+27+29+26+27)
     - GUANGDONG 2025 = 10/10 (cat URL id 72064 真公报; xjtjgb path)
     - GUIZHOU/HAINAN 2025 已发布 (2024 缺文, 2025 回来; 30 entries total)
     - lineage_ruling bumped K665d → K665e on full 8060 rows

After load:
  - Total mart rows: 8060 (unchanged — cross product is 31 × 10 × 26)
  - Real cells: 983 (prior) + 283 (665e 2025 10 指标) = 1266

K665d → K665e ruling:
  - 665d extends real_data with year 2024 5 增量 (5 增量 × 28 省; 3 missing 沿用 660 红线)
  - 665e extends real_data with year 2025 10 指标 ALL (10 指标 × 30 省; 1 missing LIAONING 沿用 660 红线)
  - ruling bump: K665d-2026-09-04 → K665e-2026-09-04 (mart 全 8060 行)
"""
import csv
import psycopg2
from pathlib import Path

DSN = dict(host='127.0.0.1', port=55440, user='postgres', password='postgres', dbname='cegr_test')


def load_seed_2025(conn) -> int:
    csv_path = Path(
        '/Users/kjonekong/projects/china platform/dbt/seeds/'
        'seed_hongheiku_timeseries_2025.csv'
    )
    with csv_path.open('r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        rows = list(reader)
    print(f'Loaded {len(rows)} rows from {csv_path.name}')

    cur = conn.cursor()
    cur.execute('DROP TABLE IF EXISTS cegr_staging.seed_hongheiku_timeseries_2025')
    cur.execute('''
        CREATE TABLE cegr_staging.seed_hongheiku_timeseries_2025 (
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
        INSERT INTO cegr_staging.seed_hongheiku_timeseries_2025
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
    print(f'Inserted {len(rows)} rows into cegr_staging.seed_hongheiku_timeseries_2025')
    return len(rows)


def run_mart(conn) -> int:
    sql_path = Path(
        '/Users/kjonekong/projects/china platform/dbt/models/marts/'
        'mart_province_timeseries.sql'
    )
    sql = sql_path.read_text(encoding='utf-8')

    # Substitute all 5 ref() calls (2021 + 2022 + 2023 + 2024 + 2025)
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
    sql = sql.replace(
        "{{ ref('seed_hongheiku_timeseries_2025') }}",
        "cegr_staging.seed_hongheiku_timeseries_2025",
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
    print('\n=== 665e 验证 (16 base 红线 + new K665e 守门) ===')

    K666b_RECLASS_PROVINCES = "'GUANGDONG', 'JIANGSU', 'ZHEJIANG'"
    K666b_RECLASS_INDICATORS = (
        "'gdp_total', 'gdp_growth', 'primary_gdp', "
        "'secondary_gdp', 'tertiary_gdp'"
    )
    K665e_10_INDICATORS = (
        "'gdp_total', 'gdp_growth', 'primary_gdp', 'secondary_gdp', 'tertiary_gdp', "
        "'gdp_percapita', 'fiscal_rev', 'fixed_asset', 'retail', 'trade'"
    )
    K665e_MISSING_1 = "'LIAONING'"

    checks = [
        # ─── 16 base 红线 (沿用 665a/665b/665c/665d/666b 守门) ───
        ('总行数 = 8060',
         'SELECT COUNT(*) FROM cegr_mart.mart_province_timeseries', 8060),
        ('real cells 2024 (5 现 + 5 增量) = 257',
         "SELECT COUNT(*) FROM cegr_mart.mart_province_timeseries WHERE year=2024 AND value IS NOT NULL", 257),
        ('real cells 2021 (665a) = 251',
         "SELECT COUNT(*) FROM cegr_mart.mart_province_timeseries WHERE year=2021 AND value IS NOT NULL", 251),
        ('real cells 2022 (665b) = 204',
         "SELECT COUNT(*) FROM cegr_mart.mart_province_timeseries WHERE year=2022 AND value IS NOT NULL", 204),
        ('real cells 2023 (665c) = 271',
         "SELECT COUNT(*) FROM cegr_mart.mart_province_timeseries WHERE year=2023 AND value IS NOT NULL", 271),
        ('real cells 2025 (665e) = 283',
         "SELECT COUNT(*) FROM cegr_mart.mart_province_timeseries WHERE year=2025 AND value IS NOT NULL", 283),
        ('real cells total = 1266 (135 + 257 + 251 + 204 + 271 + 283)',
         "SELECT COUNT(*) FROM cegr_mart.mart_province_timeseries WHERE value IS NOT NULL", 1266),
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

        # ─── new K665e 2025 红线 (10 验证) ───
        # 10 指标 2025 守门 (mirror 663 parser distribution)
        ('2025 gdp_total real = 29 (30 省 - 1 missing)',
         f"SELECT COUNT(*) FROM cegr_mart.mart_province_timeseries "
         f"WHERE year=2025 AND indicator_key='gdp_total' AND value IS NOT NULL", 29),
        ('2025 gdp_growth real = 30',
         f"SELECT COUNT(*) FROM cegr_mart.mart_province_timeseries "
         f"WHERE year=2025 AND indicator_key='gdp_growth' AND value IS NOT NULL", 30),
        ('2025 primary_gdp real = 30',
         f"SELECT COUNT(*) FROM cegr_mart.mart_province_timeseries "
         f"WHERE year=2025 AND indicator_key='primary_gdp' AND value IS NOT NULL", 30),
        ('2025 secondary_gdp real = 30',
         f"SELECT COUNT(*) FROM cegr_mart.mart_province_timeseries "
         f"WHERE year=2025 AND indicator_key='secondary_gdp' AND value IS NOT NULL", 30),
        ('2025 tertiary_gdp real = 29 (30 省 - 1 missing)',
         f"SELECT COUNT(*) FROM cegr_mart.mart_province_timeseries "
         f"WHERE year=2025 AND indicator_key='tertiary_gdp' AND value IS NOT NULL", 29),
        ('2025 gdp_percapita real = 26 (30 省 - 4 missing)',
         f"SELECT COUNT(*) FROM cegr_mart.mart_province_timeseries "
         f"WHERE year=2025 AND indicator_key='gdp_percapita' AND value IS NOT NULL", 26),
        ('2025 fiscal_rev real = 27 (30 省 - 3 missing)',
         f"SELECT COUNT(*) FROM cegr_mart.mart_province_timeseries "
         f"WHERE year=2025 AND indicator_key='fiscal_rev' AND value IS NOT NULL", 27),
        ('2025 fixed_asset real = 29 (30 省 - 1 missing)',
         f"SELECT COUNT(*) FROM cegr_mart.mart_province_timeseries "
         f"WHERE year=2025 AND indicator_key='fixed_asset' AND value IS NOT NULL", 29),
        ('2025 retail real = 26 (30 省 - 4 missing)',
         f"SELECT COUNT(*) FROM cegr_mart.mart_province_timeseries "
         f"WHERE year=2025 AND indicator_key='retail' AND value IS NOT NULL", 26),
        ('2025 trade real = 27 (30 省 - 3 missing)',
         f"SELECT COUNT(*) FROM cegr_mart.mart_province_timeseries "
         f"WHERE year=2025 AND indicator_key='trade' AND value IS NOT NULL", 27),

        # 1 missing-2025 省 LIAONING 全 DATA_MISSING (沿用 660 红线, 不在 665e harvest)
        ('1 missing-2025 省 (LIAONING) 全 DATA_MISSING',
         f"SELECT COUNT(*) FROM cegr_mart.mart_province_timeseries "
         f"WHERE province_code IN ({K665e_MISSING_1}) AND year=2025 AND value IS NOT NULL", 0),

        # GUANGDONG 2025 10 指标 全有 (cat URL id 72064 xjtjgb path 真公报)
        ('GUANGDONG 2025 10 指标 全有 (cat URL id 72064 xjtjgb 真公报)',
         f"SELECT COUNT(*) FROM cegr_mart.mart_province_timeseries "
         f"WHERE province_code='GUANGDONG' AND year=2025 "
         f"AND indicator_key IN ({K665e_10_INDICATORS}) AND value IS NOT NULL", 10),

        # GUIZHOU 2025 已发布 (2024 缺文, 2025 回来; retail 指标缺 1 cell, 类似 GUANGDONG 2024 retail 缺)
        ('GUIZHOU 2025 = 9 (10 指标 - retail 缺; 2024 缺文回归)',
         f"SELECT COUNT(*) FROM cegr_mart.mart_province_timeseries "
         f"WHERE province_code='GUIZHOU' AND year=2025 AND value IS NOT NULL", 9),

        # HAINAN 2025 已发布 (2024 缺文, 2025 回来)
        ('HAINAN 2025 ≥ 9 (2024 缺文回归)',
         f"SELECT COUNT(*) FROM cegr_mart.mart_province_timeseries "
         f"WHERE province_code='HAINAN' AND year=2025 AND value IS NOT NULL", 10),

        # K666b 升级保留 (未被 K665e 覆盖): 3 省 × 5 现 × {2021, 2022, 2024} = 29 cells
        ('K666b 升级保留 = 29 (3 省 × 5 现 × {2021, 2022, 2024})',
         f"SELECT COUNT(*) FROM cegr_mart.mart_province_timeseries "
         f"WHERE province_code IN ({K666b_RECLASS_PROVINCES}) "
         f"AND indicator_key IN ({K666b_RECLASS_INDICATORS}) "
         f"AND year IN (2021, 2022, 2024) "
         f"AND value IS NOT NULL "
         f"AND lineage_source_type = 'OFFICIAL_INTAKED'", 29),

        # K665e ruling 已替换 K665d (mart 全 8060 行)
        ('K665e ruling 已替换 K665d (mart 全 8060 行)',
         "SELECT COUNT(*) FROM cegr_mart.mart_province_timeseries "
         "WHERE lineage_ruling = 'K665e-2026-09-04'", 8060),

        # K665d ruling 已不存在 (K665e 完全替换)
        ('K665d ruling 全 0 行 (K665e 完全替换)',
         "SELECT COUNT(*) FROM cegr_mart.mart_province_timeseries "
         "WHERE lineage_ruling = 'K665d-2026-09-04'", 0),
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
        seed_n = load_seed_2025(conn)
        mart_n = run_mart(conn)
        ok = verify_red_lines(conn)
        return 0 if ok else 1
    finally:
        conn.close()


if __name__ == '__main__':
    raise SystemExit(main())