#!/usr/bin/env python3
"""665 generate_seed_hongheiku_y2021.py — 29 省 × 10 指标 = 290 rows CSV.

Schema (mirror 660 seed):
  province_code, province_name_cn, year, value, unit,
  indicator_key, indicator_label_cn,
  status, missing_reason,
  lineage_source_type, lineage_origin, lineage_ruling, lineage_is_demo

Output: dbt/seeds/seed_hongheiku_timeseries_2021.csv (mirror 2024 pattern)
"""
import csv
import json
from pathlib import Path

PROVINCE_CN = {
    'BEIJING': '北京', 'TIANJIN': '天津', 'HEBEI': '河北', 'SHANXI': '山西',
    'NEI_MENGGU': '内蒙古', 'LIAONING': '辽宁', 'JILIN': '吉林', 'HEILONGJIANG': '黑龙江',
    'SHANGHAI': '上海', 'JIANGSU': '江苏', 'ZHEJIANG': '浙江', 'ANHUI': '安徽',
    'FUJIAN': '福建', 'JIANGXI': '江西', 'SHANDONG': '山东', 'HENAN': '河南',
    'HUBEI': '湖北', 'HUNAN': '湖南', 'GUANGDONG': '广东', 'GUANGXI': '广西',
    'HAINAN': '海南', 'CHONGQING': '重庆', 'SICHUAN': '四川', 'GUIZHOU': '贵州',
    'YUNNAN': '云南', 'XIZANG': '西藏', 'SHAANXI': '陕西', 'GANSU': '甘肃',
    'QINGHAI': '青海', 'NINGXIA': '宁夏', 'XINJIANG': '新疆',
}

INDICATORS = [
    # (key, label_cn, unit)
    ('gdp_total',     '地区生产总值', '亿元'),
    ('gdp_growth',    'GDP增速',     '%'),
    ('primary_gdp',   '第一产业增加值', '亿元'),
    ('secondary_gdp', '第二产业增加值', '亿元'),
    ('tertiary_gdp',  '第三产业增加值', '亿元'),
    ('gdp_percapita', '人均地区生产总值', '元'),
    ('fiscal_rev',    '一般公共预算收入', '亿元'),
    ('fixed_asset',   '固定资产投资', '亿元'),
    ('retail',        '社会消费品零售总额', '亿元'),
    ('trade',         '进出口总额', '亿元'),
]

TO_FETCH_2021_CODES = [
    ('anhui',       'ANHUI'),       ('chongqing',   'CHONGQING'),
    ('fujian',      'FUJIAN'),      ('gansu',       'GANSU'),
    ('guangxi',     'GUANGXI'),     ('guizhou',     'GUIZHOU'),
    ('hainan',      'HAINAN'),      ('hebei',       'HEBEI'),
    ('heilongjiang','HEILONGJIANG'),('henan',       'HENAN'),
    ('hubei',       'HUBEI'),       ('hunan',       'HUNAN'),
    ('jiangsu',     'JIANGSU'),     ('jilin',       'JILIN'),
    ('liaoning',    'LIAONING'),    ('neimenggu',   'NEI_MENGGU'),
    ('ningxia',     'NINGXIA'),     ('qinghai',     'QINGHAI'),
    ('shaanxi',     'SHAANXI'),     ('shandong',    'SHANDONG'),
    ('shanghai',    'SHANGHAI'),    ('shanxi',      'SHANXI'),
    ('sichuan',     'SICHUAN'),     ('tianjin',     'TIANJIN'),
    ('xinjiang',    'XINJIANG'),    ('xizang',      'XIZANG'),
    ('yunnan',      'YUNNAN'),      ('zhejiang',    'ZHEJIANG'),
    ('beijing',     'BEIJING'),
]

# URL → province_code (mirror fetch_hongheiku_y2021.py TO_FETCH_2021)
URL_BY_CODE = {
    'ANHUI':       'https://tjgb.hongheiku.com/sjtjgb/24411.html',
    'BEIJING':     'https://tjgb.hongheiku.com/sjtjgb/24106.html',
    'CHONGQING':   'https://tjgb.hongheiku.com/sjtjgb/24421.html',
    'FUJIAN':      'https://tjgb.hongheiku.com/sjtjgb/24409.html',
    'GANSU':       'https://tjgb.hongheiku.com/sjtjgb/25126.html',
    'GUANGXI':     'https://tjgb.hongheiku.com/sjtjgb/25371.html',
    'GUIZHOU':     'https://tjgb.hongheiku.com/sjtjgb/24718.html',
    'HAINAN':      'https://tjgb.hongheiku.com/sjtjgb/23920.html',
    'HEBEI':       'https://tjgb.hongheiku.com/sjtjgb/24077.html',
    'HEILONGJIANG':'https://tjgb.hongheiku.com/sjtjgb/27480.html',
    'HENAN':       'https://tjgb.hongheiku.com/sjtjgb/24374.html',
    'HUBEI':       'https://tjgb.hongheiku.com/sjtjgb/24237.html',
    'HUNAN':       'https://tjgb.hongheiku.com/sjtjgb/25100.html',
    'JIANGSU':     'https://tjgb.hongheiku.com/sjtjgb/24199.html',
    'JILIN':       'https://tjgb.hongheiku.com/sjtjgb/30339.html',
    'LIAONING':    'https://tjgb.hongheiku.com/sjtjgb/27517.html',
    'NEI_MENGGU':  'https://tjgb.hongheiku.com/sjtjgb/24061.html',
    'NINGXIA':     'https://tjgb.hongheiku.com/sjtjgb/27494.html',
    'QINGHAI':     'https://tjgb.hongheiku.com/sjtjgb/24130.html',
    'SHAANXI':     'https://tjgb.hongheiku.com/sjtjgb/25693.html',
    'SHANDONG':    'https://tjgb.hongheiku.com/sjtjgb/24134.html',
    'SHANGHAI':    'https://tjgb.hongheiku.com/sjtjgb/25158.html',
    'SHANXI':      'https://tjgb.hongheiku.com/sjtjgb/25002.html',
    'SICHUAN':     'https://tjgb.hongheiku.com/sjtjgb/24394.html',
    'TIANJIN':     'https://tjgb.hongheiku.com/sjtjgb/25108.html',
    'XINJIANG':    'https://tjgb.hongheiku.com/sjtjgb/24838.html',
    'XIZANG':      'https://tjgb.hongheiku.com/sjtjgb/26310.html',
    'YUNNAN':      'https://tjgb.hongheiku.com/sjtjgb/25260.html',
    'ZHEJIANG':    'https://tjgb.hongheiku.com/sjtjgb/24010.html',
}

YEAR = 2021
LINEAGE_RULING = 'knife_665_y2021'


def main() -> int:
    # Load parse evidence
    parse_path = Path(
        '/Users/kjonekong/projects/china platform/evidence_pack/'
        'u6_batch_y2021_parse_20260904.json'
    )
    parse_data = json.loads(parse_path.read_text(encoding='utf-8'))

    # Build province_code → extracted dict
    extracted_by_code = {}
    for r in parse_data['cells']:
        extracted_by_code[r['province_code']] = r['extracted']

    # Add GUANGDONG + JIANGXI as missing-in-2021 (hongheiku cat index 无)
    # NOTE: NOT included in seed CSV — seed represents harvested data only.
    # The mart handles missing provinces via cross product + DATA_MISSING fill.
    for missing_code in ('GUANGDONG', 'JIANGXI'):
        extracted_by_code[missing_code] = {}

    rows = []
    # Seed includes ONLY provinces with hongheiku 2021 entries (29, not 31)
    all_codes = sorted(set(c for _, c in TO_FETCH_2021_CODES))

    for prov_code in all_codes:
        extracted = extracted_by_code.get(prov_code, {})
        url = URL_BY_CODE.get(prov_code, '')
        in_index = prov_code in URL_BY_CODE

        for ind_key, ind_label_cn, ind_unit in INDICATORS:
            value = extracted.get(ind_key)
            in_index = True  # all 29 seed provinces are in hongheiku cat index

            # Determine status & missing_reason
            if value is None:
                # Page exists but parse couldn't extract this value
                status = 'DATA_MISSING'
                missing_reason = '新增红线-1: 2021 公报 parse 未捕获 (沿用禁补零)'
                value_out = ''
            else:
                status = ''
                missing_reason = ''
                value_out = f'{value:g}'

            rows.append({
                'province_code': prov_code,
                'province_name_cn': PROVINCE_CN.get(prov_code, ''),
                'year': YEAR,
                'value': value_out,
                'unit': ind_unit,
                'indicator_key': ind_key,
                'indicator_label_cn': ind_label_cn,
                'status': status,
                'missing_reason': missing_reason,
                'lineage_source_type': 'hongheiku_tjgb' if value is not None and in_index else 'DATA_MISSING',
                'lineage_origin': url,
                'lineage_ruling': LINEAGE_RULING,
                'lineage_is_demo': 'false',
            })

    # Write CSV
    out_path = Path(
        '/Users/kjonekong/projects/china platform/dbt/seeds/'
        'seed_hongheiku_timeseries_2021.csv'
    )
    out_path.parent.mkdir(exist_ok=True)
    with out_path.open('w', encoding='utf-8', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)

    real_cells = sum(1 for r in rows if r['value'] != '')
    missing_cells = sum(1 for r in rows if r['status'] == 'DATA_MISSING')
    print(f'wrote {out_path}')
    print(f'Total rows: {len(rows)} (expected 290 = 29 provinces × 10 indicators)')
    print(f'Real cells: {real_cells}')
    print(f'Missing cells: {missing_cells}')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())