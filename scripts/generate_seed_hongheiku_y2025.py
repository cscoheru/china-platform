#!/usr/bin/env python3
"""665e generate_seed_hongheiku_timeseries_2025.py — build seed CSV from parse JSON.

Mirror 665a seed CSV schema (dbt seed format) but for 2025 ALL 10 指标 (5 现 + 5 增量).
2025 无 663 baseline,需全 10 指标 harvest (vs 665d 仅 5 增量).

Sources:
  - evidence_pack/u6_batch_y2025_parse_20260904.json (extract ALL 10 指标 per province)
  - evidence_pack/u6_batch_y2025_fetch_20260904.json (URL per province)

Output:
  dbt/seeds/seed_hongheiku_timeseries_2025.csv (~283 rows; 30/30 provinces PARSED;
  1 missing province LIAONING not included — 沿用 660 红线 DATA_MISSING)

Scope: ALL 10 指标 (5 现 + 5 增量) — 与 665a/665b/665c 一致.
"""
import csv
import json
from pathlib import Path

PARSE_PATH = Path('/Users/kjonekong/projects/china platform/evidence_pack/'
                  'u6_batch_y2025_parse_20260904.json')
FETCH_PATH = Path('/Users/kjonekong/projects/china platform/evidence_pack/'
                  'u6_batch_y2025_fetch_20260904.json')
SEED_PATH = Path('/Users/kjonekong/projects/china platform/dbt/seeds/'
                 'seed_hongheiku_timeseries_2025.csv')

PROVINCE_NAME_CN = {
    'ANHUI': '安徽', 'BEIJING': '北京', 'CHONGQING': '重庆', 'FUJIAN': '福建',
    'GANSU': '甘肃', 'GUANGDONG': '广东', 'GUANGXI': '广西', 'GUIZHOU': '贵州',
    'HAINAN': '海南', 'HEBEI': '河北', 'HEILONGJIANG': '黑龙江', 'HENAN': '河南',
    'HUBEI': '湖北', 'HUNAN': '湖南', 'JIANGSU': '江苏', 'JIANGXI': '江西',
    'JILIN': '吉林', 'LIAONING': '辽宁', 'NEI_MENGGU': '内蒙古', 'NINGXIA': '宁夏',
    'QINGHAI': '青海', 'SHAANXI': '陕西', 'SHANDONG': '山东', 'SHANGHAI': '上海',
    'SHANXI': '山西', 'SICHUAN': '四川', 'TIANJIN': '天津', 'XINJIANG': '新疆',
    'XIZANG': '西藏', 'YUNNAN': '云南', 'ZHEJIANG': '浙江',
}

INDICATOR_LABELS_10 = {
    'gdp_total':     ('地区生产总值',                 '亿元'),
    'gdp_growth':    ('地区生产总值增速',             '%'),
    'primary_gdp':   ('第一产业增加值',               '亿元'),
    'secondary_gdp': ('第二产业增加值',               '亿元'),
    'tertiary_gdp':  ('第三产业增加值',               '亿元'),
    'gdp_percapita': ('人均地区生产总值',             '元'),
    'fiscal_rev':    ('一般公共预算收入',             '亿元'),
    'fixed_asset':   ('固定资产投资',                 '亿元'),
    'retail':        ('社会消费品零售总额',           '亿元'),
    'trade':         ('进出口总额',                   '亿元'),
}

LINEAGE_RULING = 'knife_665_y2025_10indicators'
LINEAGE_SOURCE = 'hongheiku_tjgb'


def main() -> int:
    parse_data = json.loads(PARSE_PATH.read_text(encoding='utf-8'))
    fetch_data = json.loads(FETCH_PATH.read_text(encoding='utf-8'))

    url_by_code = {r['province_code']: r['url'] for r in fetch_data['cells']}

    rows = []
    for cell in parse_data['cells']:
        prov_code = cell['province_code']
        if cell['verdict'] != 'PARSED':
            continue
        url = url_by_code.get(prov_code, '')
        for ind_key, value in cell['extracted'].items():
            label_cn, unit = INDICATOR_LABELS_10[ind_key]
            rows.append({
                'province_code': prov_code,
                'province_name_cn': PROVINCE_NAME_CN.get(prov_code, prov_code),
                'year': 2025,
                'value': value,
                'unit': unit,
                'indicator_key': ind_key,
                'indicator_label_cn': label_cn,
                'status': '',
                'missing_reason': '',
                'lineage_source_type': LINEAGE_SOURCE,
                'lineage_origin': url,
                'lineage_ruling': LINEAGE_RULING,
                'lineage_is_demo': 'false',
            })

    SEED_PATH.parent.mkdir(parents=True, exist_ok=True)
    fieldnames = [
        'province_code', 'province_name_cn', 'year', 'value', 'unit',
        'indicator_key', 'indicator_label_cn', 'status', 'missing_reason',
        'lineage_source_type', 'lineage_origin', 'lineage_ruling', 'lineage_is_demo',
    ]
    with SEED_PATH.open('w', encoding='utf-8', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for r in rows:
            writer.writerow(r)

    by_ind = {}
    for r in rows:
        by_ind[r['indicator_key']] = by_ind.get(r['indicator_key'], 0) + 1

    print(f'wrote {SEED_PATH}')
    print(f'rows: {len(rows)}')
    print('per-indicator coverage (10 指标):')
    for k in INDICATOR_LABELS_10:
        print(f'  {k}: {by_ind.get(k, 0)}')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())