#!/usr/bin/env python3
"""666b load_seed_and_mart.py — Option B (hongheiku reclassify, 0 HTTP).

Mirrors 665a/665b pattern but does NOT load new seed data; just re-runs the
mart with the K666b lineage_source_type override for 3 省 × 5 现 cells.

K666 Option B (user_ruling_666 Option B chosen, 2026-09-04):
  Reclassify 3 省 (GUANGDONG / JIANGSU / ZHEJIANG) × 5 现指标 from
  HONGHEIKU_TRANSLOAD → OFFICIAL_INTAKED, 因为本机网络无法访问 stats.*.gov.cn
  (probe 9/9 HTTP BLOCKED, Errno 54 Connection reset by peer). 0 HTTP used.
  Source data: existing 665a (2021) + 665b (2022) hongheiku seeds +
  real_2024_provinces hardcoded values (mart SQL).

After load:
  - Total mart rows: 8060 (unchanged — cross product 31 × 10 × 26)
  - Real cells: 590 (135 + 251 + 204) — unchanged
  - Upgraded cells (HONGHEIKU → OFFICIAL): 3 省 × 5 现 × {2021, 2022, 2024}
    WHERE value IS NOT NULL = 29 cells (15 2024 + 7 2021 + 7 2022)
    Note: ZHEJIANG 2021/2022 only parsed gdp_total + gdp_growth (2 of 5 现);
    primary/secondary/tertiary_gdp NULL in 665a/665b seeds → not eligible for reclassify.
  - 5 增量指标 stay HONGHEIKU_TRANSLOAD (per Option B scope: 5 现 only)

Verify 16 base 红线 + 7 new 666b-specific 红线 = 23 total.
"""
import psycopg2
from pathlib import Path

DSN = dict(host='127.0.0.1', port=55440, user='postgres', password='postgres', dbname='cegr_test')


def run_mart(conn) -> int:
    """Re-run mart with K666b lineage_source_type override + ruling bump."""
    sql_path = Path(
        '/Users/kjonekong/projects/china platform/dbt/models/marts/'
        'mart_province_timeseries.sql'
    )
    sql = sql_path.read_text(encoding='utf-8')

    # Substitute ref() calls (665a 2021 + 665b 2022 — both already in cegr_staging)
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
    """16 base 红线 (665a + 665b) + 7 new 666b 红线 = 23 total."""
    cur = conn.cursor()
    print('\n=== 666b 验证 (16 base 红线 + 7 new K666b 守门) ===')

    # ── K666b reclassify scope (5 indicators) ──
    K666_INDICATORS = (
        "'gdp_total', 'gdp_growth', 'primary_gdp', "
        "'secondary_gdp', 'tertiary_gdp'"
    )
    K666_PROVINCES = "'GUANGDONG', 'JIANGSU', 'ZHEJIANG'"

    checks = [
        # ─── 16 base 红线 (沿用 665a/665b 守门) ───
        ('总行数 = 8060',
         'SELECT COUNT(*) FROM cegr_mart.mart_province_timeseries', 8060),
        ('real cells 2024 (663 baseline) = 135',
         "SELECT COUNT(*) FROM cegr_mart.mart_province_timeseries WHERE year=2024 AND value IS NOT NULL", 135),
        ('real cells 2021 (665a) = 251',
         "SELECT COUNT(*) FROM cegr_mart.mart_province_timeseries WHERE year=2021 AND value IS NOT NULL", 251),
        ('real cells 2022 (665b) = 204',
         "SELECT COUNT(*) FROM cegr_mart.mart_province_timeseries WHERE year=2022 AND value IS NOT NULL", 204),
        ('real cells total = 590 (135 + 251 + 204)',
         "SELECT COUNT(*) FROM cegr_mart.mart_province_timeseries WHERE value IS NOT NULL", 590),
        ('HUNAN 2022 全 DATA_MISSING',
         "SELECT COUNT(*) FROM cegr_mart.mart_province_timeseries WHERE province_code='HUNAN' AND year=2022 AND value IS NOT NULL", 0),
        ('GUANGDONG 2022 全 DATA_MISSING (665b 目录页 PDF 未解析)',
         "SELECT COUNT(*) FROM cegr_mart.mart_province_timeseries WHERE province_code='GUANGDONG' AND year=2022 AND value IS NOT NULL", 0),
        ('JIANGXI 2022 全 DATA_MISSING',
         "SELECT COUNT(*) FROM cegr_mart.mart_province_timeseries WHERE province_code='JIANGXI' AND year=2022 AND value IS NOT NULL", 0),
        ('LIAONING/GUIZHOU 2022 全 DATA_MISSING',
         "SELECT COUNT(*) FROM cegr_mart.mart_province_timeseries WHERE province_code IN ('LIAONING','GUIZHOU') AND year=2022 AND value IS NOT NULL", 0),
        ('HAINAN 2022 有 real cells (10/10)',
         "SELECT COUNT(*) FROM cegr_mart.mart_province_timeseries WHERE province_code='HAINAN' AND year=2022 AND value IS NOT NULL", 10),
        ('SHANGHAI/GANSU/HEILONGJIANG/HUNAN/NINGXIA 2022 全 DATA_MISSING',
         "SELECT COUNT(*) FROM cegr_mart.mart_province_timeseries WHERE province_code IN ('SHANGHAI','GANSU','HEILONGJIANG','HUNAN','NINGXIA') AND year=2022 AND value IS NOT NULL", 0),
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
        # ─── 7 new K666b 红线 ───
        # POSITIVE: 3 省 × 5 现 × {2021, 2022, 2024} reclassified to OFFICIAL_INTAKED
        # 2024: 3 × 5 = 15; 2021: JIANGSU 5 + ZHEJIANG 2 = 7 (ZHEJIANG 缺 primary/secondary/tertiary
        # in 665a seed parse); 2022: JIANGSU 5 + ZHEJIANG 2 = 7 (665b seed parse 同).
        # GUANGDONG 2021/2022 DATA_MISSING (cat index 无/目录页 PDF).
        # 总: 15 + 7 + 7 = 29 cells upgraded.
        ('K666b 升级总数 = 29 (15 2024 + 7 2021 + 7 2022; ZHEJIANG 缺 3 产业)',
         f"SELECT COUNT(*) FROM cegr_mart.mart_province_timeseries "
         f"WHERE province_code IN ({K666_PROVINCES}) "
         f"AND indicator_key IN ({K666_INDICATORS}) "
         f"AND year IN (2021, 2022, 2024) "
         f"AND value IS NOT NULL "
         f"AND lineage_source_type = 'OFFICIAL_INTAKED'", 29),
        ('K666b 2024 升级 = 15 (3 省 × 5 现 全部)',
         f"SELECT COUNT(*) FROM cegr_mart.mart_province_timeseries "
         f"WHERE province_code IN ({K666_PROVINCES}) "
         f"AND indicator_key IN ({K666_INDICATORS}) "
         f"AND year = 2024 "
         f"AND lineage_source_type = 'OFFICIAL_INTAKED'", 15),
        ('K666b 2021 升级 = 7 (JIANGSU 5 + ZHEJIANG 2; GUANGDONG 2021 DATA_MISSING)',
         f"SELECT COUNT(*) FROM cegr_mart.mart_province_timeseries "
         f"WHERE province_code IN ('JIANGSU', 'ZHEJIANG') "
         f"AND indicator_key IN ({K666_INDICATORS}) "
         f"AND year = 2021 "
         f"AND value IS NOT NULL "
         f"AND lineage_source_type = 'OFFICIAL_INTAKED'", 7),
        ('K666b 2022 升级 = 7 (JIANGSU 5 + ZHEJIANG 2; GUANGDONG 2022 DATA_MISSING)',
         f"SELECT COUNT(*) FROM cegr_mart.mart_province_timeseries "
         f"WHERE province_code IN ('JIANGSU', 'ZHEJIANG') "
         f"AND indicator_key IN ({K666_INDICATORS}) "
         f"AND year = 2022 "
         f"AND value IS NOT NULL "
         f"AND lineage_source_type = 'OFFICIAL_INTAKED'", 7),
        # NEGATIVE: GUANGDONG/JIANGXI 2021 保持 DATA_MISSING (cat index 无)
        ('GUANGDONG 2021 全 DATA_MISSING (cat index 无, 不被 K666b 升级)',
         "SELECT COUNT(*) FROM cegr_mart.mart_province_timeseries "
         "WHERE province_code='GUANGDONG' AND year=2021 AND value IS NOT NULL", 0),
        # NEGATIVE: 5 增量 stay HONGHEIKU_TRANSLOAD for 3 省 (not upgraded by Option B)
        # JIANGSU 2021+2022: 5+5 = 10; ZHEJIANG 2021+2022: 4+4 = 8 (trade missing both years).
        # GUANGDONG/JIANGSU/ZHEJIANG 2024: 5 增量不在 663 baseline (real_2024_provinces 仅 5 现).
        # GUANGDONG 2021/2022: DATA_MISSING (cat index 无/目录页).
        # 总: 18 cells stay HONGHEIKU_TRANSLOAD for 5 增量.
        ('K666b 5 增量 stay HONGHEIKU_TRANSLOAD = 18 (JIANGSU 10 + ZHEJIANG 8)',
         f"SELECT COUNT(*) FROM cegr_mart.mart_province_timeseries "
         f"WHERE province_code IN ({K666_PROVINCES}) "
         f"AND indicator_key IN ('gdp_percapita','fiscal_rev','fixed_asset','retail','trade') "
         f"AND year IN (2021, 2022, 2024) "
         f"AND value IS NOT NULL "
         f"AND lineage_source_type = 'hongheiku_tjgb'", 18),
        # NEGATIVE: 0 OFFICIAL_INTAKED for 5 增量 in 3 省 (no upgrade for 5 增量 scope)
        ('K666b 5 增量在 3 省 0 OFFICIAL_INTAKED (5 增量不在 B 升级范围)',
         f"SELECT COUNT(*) FROM cegr_mart.mart_province_timeseries "
         f"WHERE province_code IN ({K666_PROVINCES}) "
         f"AND indicator_key IN ('gdp_percapita','fiscal_rev','fixed_asset','retail','trade') "
         f"AND lineage_source_type = 'OFFICIAL_INTAKED'", 0),
        # K666b ruling 全 mart (K665b 应已被替换)
        ('K666b ruling 已替换 K665b (mart 全行 ruling)',
         "SELECT COUNT(*) FROM cegr_mart.mart_province_timeseries "
         "WHERE lineage_ruling = 'K666b-2026-09-04'", 8060),
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
        if expected is None:
            # placeholder check, skip
            print(f'  [skip] {name}: {actual}')
            continue
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
        mart_n = run_mart(conn)
        ok = verify_red_lines(conn)
        return 0 if ok else 1
    finally:
        conn.close()


if __name__ == '__main__':
    raise SystemExit(main())