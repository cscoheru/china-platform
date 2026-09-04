#!/usr/bin/env python3
"""665 parse_hongheiku_y2022.py — parse 10 指标 from cached 2022 hongheiku pages.

Reuses _extract_* functions from scripts/parse_hongheiku_10_indicators.py
(imported directly, no duplication of regex logic).

Cache path convention (mirroring 665a):
  /tmp/_665_y2022_{province_en}.html
"""
import json
import re
import sys
from pathlib import Path

# Import extraction functions from 665a parser (no fork of regex logic)
sys.path.insert(0, '/Users/kjonekong/projects/china platform/scripts')
from parse_hongheiku_10_indicators import (
    _extract_all,
    INDICATOR_LABELS,
)

CACHE_DIR = Path('/tmp')

# Same province list as fetch_hongheiku_y2022.py
TO_FETCH_2022 = [
    ('anhui',       'ANHUI'),
    ('beijing',     'BEIJING'),
    ('chongqing',   'CHONGQING'),
    ('fujian',      'FUJIAN'),
    ('guangdong',   'GUANGDONG'),
    ('guangxi',     'GUANGXI'),
    ('hainan',      'HAINAN'),
    ('hebei',       'HEBEI'),
    ('henan',       'HENAN'),
    ('hubei',       'HUBEI'),
    ('jiangsu',     'JIANGSU'),
    ('jiangxi',     'JIANGXI'),
    ('jilin',       'JILIN'),
    ('neimenggu',   'NEI_MENGGU'),
    ('qinghai',     'QINGHAI'),
    ('shaanxi',     'SHAANXI'),
    ('shandong',    'SHANDONG'),
    ('shanxi',      'SHANXI'),
    ('sichuan',     'SICHUAN'),
    ('tianjin',     'TIANJIN'),
    ('xinjiang',    'XINJIANG'),
    ('xizang',      'XIZANG'),
    ('yunnan',      'YUNNAN'),
    ('zhejiang',    'ZHEJIANG'),
]


def main() -> int:
    out_records = []
    parse_failures = []

    for prov_en, prov_code in TO_FETCH_2022:
        cache_path = CACHE_DIR / f'_665_y2022_{prov_en}.html'
        if not cache_path.exists():
            out_records.append({
                'province_en': prov_en,
                'province_code': prov_code,
                'verdict': 'CACHE_MISS',
                'extracted': {},
            })
            continue
        body = cache_path.read_text(encoding='utf-8', errors='replace')
        text = re.sub(r'<[^>]+>', ' ', body)
        text = re.sub(r'\s+', ' ', text)
        extracted = _extract_all(text)
        verdict = 'PARSED' if extracted else 'PARSE_EMPTY'
        if not extracted:
            parse_failures.append(prov_en)
        out_records.append({
            'province_en': prov_en,
            'province_code': prov_code,
            'verdict': verdict,
            'extracted': extracted,
        })

    summary = {
        'total_provinces': len(TO_FETCH_2022),
        'parsed_count': sum(1 for r in out_records if r['verdict'] == 'PARSED'),
        'parse_empty_count': sum(1 for r in out_records if r['verdict'] == 'PARSE_EMPTY'),
        'cache_miss_count': sum(1 for r in out_records if r['verdict'] == 'CACHE_MISS'),
        'by_indicator': {},
    }
    for ind in INDICATOR_LABELS:
        summary['by_indicator'][ind] = sum(
            1 for r in out_records if ind in r['extracted']
        )

    out = {
        'knife': '665',
        'sub_knife': '665b',
        'chain_id': 'parse_665b_m2_u10_batch_v1_y2022',
        'year': 2022,
        'summary': summary,
        'parse_failures': parse_failures,
        'cells': out_records,
        'methodology': 'v1 10 指标 parse: 5 现 (gdp_total/gdp_growth/primary/secondary/tertiary) '
                       'mirror 665a _extract pattern + 5 增量 (gdp_percapita/fiscal_rev/'
                       'fixed_asset/retail/trade) regex with section-anchored; missing '
                       'values stay None → DATA_MISSING (新增红线-1 沿用, 禁补零); '
                       'reuses _extract_* from parse_hongheiku_10_indicators.py.',
    }

    out_path = Path(
        '/Users/kjonekong/projects/china platform/evidence_pack/'
        'u6_batch_y2022_parse_20260904.json'
    )
    out_path.parent.mkdir(exist_ok=True)
    out_path.write_text(json.dumps(out, ensure_ascii=False, indent=2), encoding='utf-8')
    print(f'wrote {out_path}')
    print(f'Parsed: {summary["parsed_count"]}/{summary["total_provinces"]}')
    print(f'Empty: {summary["parse_empty_count"]}')
    print('Per-indicator coverage:')
    for ind, n in summary['by_indicator'].items():
        print(f'  {ind}: {n}/{summary["total_provinces"]}')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())