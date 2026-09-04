#!/usr/bin/env python3
"""665b load_seed_and_mart.py — bypass dbt CLI (663 Gap 1) via direct psycopg2.

Mirrors 665a load_seed_and_mart_665a.py but for 2022 data:
  1. Load seed_hongheiku_timeseries_2022.csv → cegr_staging.seed_hongheiku_timeseries_2022
  2. Re-run mart with 2022 added to real_data UNION (mart_province_timeseries.sql now references
     seed_hongheiku_timeseries_2022 alongside 2021)
  3. Verify 14 red lines + new 2022-specific checks

After load:
  - Total mart rows: 8060 (unchanged — cross product is 31 × 10 × 26)
  - Real cells: 663 baseline 140 + 665 (2021) 251 + 665b (2022) ~204 ≈ 595
  - 2022 cells real = ~204 (out of 24 provinces attempted; 9 missing → DATA_MISSING)
"""
import csv
import psycopg2
from pathlib import Path

DSN = dict(host='127.0.0.1', port=55440, user='postgres', password='postgres', dbname='cegr_test')


def load_seed_2022(conn) -> int:
    csv_path = Path(
        '/Users/kjonekong/projects/china platform/dbt/seeds/'
        'seed_hongheiku_timeseries_2022.csv'
    )
    with csv_path.open('r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        rows = list(reader)
    print(f'Loaded {len(rows)} rows from {csv_path.name}')

    cur = conn.cursor()
    cur.execute('DROP TABLE IF EXISTS cegr_staging.seed_hongheiku_timeseries_2022')
    cur.execute('''
        CREATE TABLE cegr_staging.seed_hongheiku_timeseries_2022 (
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
        INSERT INTO cegr_staging.seed_hongheiku_timeseries_2022
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
    print(f'Inserted {len(rows)} rows into cegr_staging.seed_hongheiku_timeseries_2022')
    return len(rows)


def run_mart(conn) -> int:
    sql_path = Path(
        '/Users/kjonekong/projects/china platform/dbt/models/marts/'
        'mart_province_timeseries.sql'
    )
    sql = sql_path.read_text(encoding='utf-8')

    # Substitute both ref() calls (2021 + 2022)
    sql = sql.replace(
        "{{ ref('seed_hongheiku_timeseries_2021') }}",
        "cegr_staging.seed_hongheiku_timeseries_2021",
    )
    sql = sql.replace(
        "{{ ref('seed_hongheiku_timeseries_2022') }}",
        "cegr_staging.seed_hongheiku_timeseries_2022",
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
    print('\n=== 665b 验证 (14 红线 + 5 增量 2022 守门) ===')

    checks = [
        # ── 基线 (沿用 665a 14 红线) ──
        ('总行数 = 8060',
         'SELECT COUNT(*) FROM cegr_mart.mart_province_timeseries', 8060),
        ('real cells 2024 (663 baseline) = 135',
         "SELECT COUNT(*) FROM cegr_mart.mart_province_timeseries WHERE year=2024 AND value IS NOT NULL", 135),
        ('real cells 2021 (665a) = 251',
         "SELECT COUNT(*) FROM cegr_mart.mart_province_timeseries WHERE year=2021 AND value IS NOT NULL", 251),
        ('real cells 2022 (665b new) = 204',
         "SELECT COUNT(*) FROM cegr_mart.mart_province_timeseries WHERE year=2022 AND value IS NOT NULL", 204),
        ('real cells total = 590 (135 + 251 + 204)',
         "SELECT COUNT(*) FROM cegr_mart.mart_province_timeseries WHERE value IS NOT NULL", 590),
        ('HUNAN 2022 全 DATA_MISSING (hongheiku 索引无 2022 条目)',
         "SELECT COUNT(*) FROM cegr_mart.mart_province_timeseries WHERE province_code='HUNAN' AND year=2022 AND value IS NOT NULL", 0),
        ('GUANGDONG 2022 全 DATA_MISSING (cat index 是目录页, PDF 未解析)',
         "SELECT COUNT(*) FROM cegr_mart.mart_province_timeseries WHERE province_code='GUANGDONG' AND year=2022 AND value IS NOT NULL", 0),
        ('JIANGXI 2022 全 DATA_MISSING (同上)',
         "SELECT COUNT(*) FROM cegr_mart.mart_province_timeseries WHERE province_code='JIANGXI' AND year=2022 AND value IS NOT NULL", 0),
        ('LIAONING/GUIZHOU 2022 全 DATA_MISSING (年鉴滞后; HAINAN 2022 实有真公报, 不在此列)',
         "SELECT COUNT(*) FROM cegr_mart.mart_province_timeseries WHERE province_code IN ('LIAONING','GUIZHOU') AND year=2022 AND value IS NOT NULL", 0),
        ('HAINAN 2022 有 real cells (665b 实证: 10/10 indicators)',
         "SELECT COUNT(*) FROM cegr_mart.mart_province_timeseries WHERE province_code='HAINAN' AND year=2022 AND value IS NOT NULL", 10),
        ('SHANGHAI/GANSU/HEILONGJIANG/HUNAN/NINGXIA 2022 全 DATA_MISSING (5 missing 列表)',
         "SELECT COUNT(*) FROM cegr_mart.mart_province_timeseries WHERE province_code IN ('SHANGHAI','GANSU','HEILONGJIANG','HUNAN','NINGXIA') AND year=2022 AND value IS NOT NULL", 0),
        ('2001-2019 全 DATA_MISSING (新增红线-1)',
         "SELECT COUNT(*) FROM cegr_mart.mart_province_timeseries WHERE year BETWEEN 2001 AND 2019 AND value IS NOT NULL", 0),
        ('2026 全 DATA_MISSING (新增红线-2)',
         "SELECT COUNT(*) FROM cegr_mart.mart_province_timeseries WHERE year=2026 AND value IS NOT NULL", 0),
        ('real cells value IS NULL = DATA_MISSING (禁补零)',
         "SELECT COUNT(*) FROM cegr_mart.mart_province_timeseries WHERE value IS NULL AND status != 'DATA_MISSING'", 0),
        ('lineage_source_type 全填',
         "SELECT COUNT(*) FROM cegr_mart.mart_province_timeseries WHERE lineage_source_type IS NULL", 0),
        ('lineage_origin 全填',
         "SELECT COUNT(*) FROM cegr_mart.mart_province_timeseries WHERE lineage_origin IS NULL", 0),
    ]

    all_ok = True
    for name, sql, expected in checks:
        cur.execute(sql)
        result = cur.fetchone()
        if isinstance(result, tuple) and len(result) > 1:
            print(f'  {name}:')
            for r in result:
                print(f'    {r}')
            continue
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
        seed_n = load_seed_2022(conn)
        mart_n = run_mart(conn)
        ok = verify_red_lines(conn)
        return 0 if ok else 1
    finally:
        conn.close()


if __name__ == '__main__':
    raise SystemExit(main())