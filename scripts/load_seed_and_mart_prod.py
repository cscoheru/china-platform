#!/usr/bin/env python3
"""664 load_seed_and_mart_prod.py — bypass dbt CLI for newvps prod deployment.

Mirrors 665a load_seed_and_mart_665a.py but for prod target:
  - Connects to china-platform-pg inside puer-net (no host port mapping)
  - Loads seed_hongheiku_timeseries_2021.csv into cegr_staging.seed_hongheiku_timeseries_2021
  - Substitutes {{ ref('seed_hongheiku_timeseries_2021') }} → cegr_staging.seed_hongheiku_timeseries_2021
  - Wraps mart SQL in CREATE TABLE cegr_mart.mart_province_timeseries AS <SELECT>
  - Verifies 8 red lines

Run from newvps host (after docker compose up postgres):
  python3 scripts/load_seed_and_mart_prod.py

Alternative (used in 664 deploy): run via `docker exec china-platform-pg psql`
because newvps prod compose has NO host port mapping for postgres.
This script is kept for future / alternative deploy paths where host port is exposed.
"""
import csv
import psycopg2
import re
from pathlib import Path

# Default: assumes host port mapping (e.g., dev or test setup with 5432 exposed)
DSN = dict(host='127.0.0.1', port=5432, user='postgres', password='postgres', dbname='cegr_test')


def load_seed(conn) -> int:
    csv_path = Path(
        '/Users/kjonekong/projects/china platform/dbt/seeds/'
        'seed_hongheiku_timeseries_2021.csv'
    )
    with csv_path.open('r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        rows = list(reader)
    print(f'Loaded {len(rows)} rows from {csv_path.name}')

    cur = conn.cursor()
    cur.execute('DROP TABLE IF EXISTS cegr_staging.seed_hongheiku_timeseries_2021')
    cur.execute('''
        CREATE TABLE cegr_staging.seed_hongheiku_timeseries_2021 (
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
        INSERT INTO cegr_staging.seed_hongheiku_timeseries_2021
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
    print(f'Inserted {len(rows)} rows into cegr_staging.seed_hongheiku_timeseries_2021')
    return len(rows)


def run_mart(conn) -> int:
    sql_path = Path(
        '/Users/kjonekong/projects/china platform/dbt/models/marts/'
        'mart_province_timeseries.sql'
    )
    sql = sql_path.read_text(encoding='utf-8')
    # Substitute ref
    sql = sql.replace(
        "{{ ref('seed_hongheiku_timeseries_2021') }}",
        "cegr_staging.seed_hongheiku_timeseries_2021",
    )
    # Strip leading comment block + first blank lines, prepend CREATE TABLE AS
    lines = sql.split('\n')
    i = 0
    while i < len(lines) and (lines[i].startswith('--') or lines[i].strip() == ''):
        i += 1
    sql_body = '\n'.join(lines[i:])
    full_sql = (
        'CREATE TABLE cegr_mart.mart_province_timeseries AS\n'
        + sql_body.rstrip().rstrip(';')
        + ';\n'
    )

    cur = conn.cursor()
    cur.execute('DROP TABLE IF EXISTS cegr_mart.mart_province_timeseries CASCADE')
    cur.execute(full_sql)
    conn.commit()
    cur.execute('SELECT COUNT(*) FROM cegr_mart.mart_province_timeseries')
    n = cur.fetchone()[0]
    print(f'mart rows: {n}')
    return n


def verify_red_lines(conn) -> bool:
    cur = conn.cursor()
    print('\n=== 664 prod 验证 (8 红线) ===')
    checks = [
        ('总行数 = 8060', 'SELECT COUNT(*) FROM cegr_mart.mart_province_timeseries', 8060),
        ('real cells 2024 (663 baseline) = 135',
         "SELECT COUNT(*) FROM cegr_mart.mart_province_timeseries WHERE year=2024 AND value IS NOT NULL", 135),
        ('real cells 2021 (665a) = 251',
         "SELECT COUNT(*) FROM cegr_mart.mart_province_timeseries WHERE year=2021 AND value IS NOT NULL", 251),
        ('real cells total = 386',
         "SELECT COUNT(*) FROM cegr_mart.mart_province_timeseries WHERE value IS NOT NULL", 386),
        ('HUNAN 2021 全 DATA_MISSING',
         "SELECT COUNT(*) FROM cegr_mart.mart_province_timeseries WHERE province_code='HUNAN' AND year=2021 AND value IS NOT NULL", 0),
        ('LIAONING/HAINAN/GUIZHOU 2021 启用 = 28',
         "SELECT COUNT(*) FROM cegr_mart.mart_province_timeseries WHERE province_code IN ('LIAONING','HAINAN','GUIZHOU') AND year=2021 AND value IS NOT NULL", 28),
        ('2001-2019 全 DATA_MISSING',
         "SELECT COUNT(*) FROM cegr_mart.mart_province_timeseries WHERE year < 2020 AND value IS NOT NULL", 0),
        ('2026 全 DATA_MISSING',
         "SELECT COUNT(*) FROM cegr_mart.mart_province_timeseries WHERE year=2026 AND value IS NOT NULL", 0),
    ]
    all_ok = True
    for name, sql, expected in checks:
        cur.execute(sql)
        actual = cur.fetchone()[0]
        status = '✓' if actual == expected else '✗ FAIL'
        if actual != expected:
            all_ok = False
        print(f'  [{status}] {name}: {actual} (expected {expected})')
    return all_ok


def main() -> int:
    conn = psycopg2.connect(**DSN)
    try:
        seed_n = load_seed(conn)
        mart_n = run_mart(conn)
        ok = verify_red_lines(conn)
        return 0 if ok else 1
    finally:
        conn.close()


if __name__ == '__main__':
    raise SystemExit(main())