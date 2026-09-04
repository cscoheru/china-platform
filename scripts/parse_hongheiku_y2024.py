#!/usr/bin/env python3
"""665d parse_hongheiku_y2024.py — parse 5 增量指标 from cached 2024 hongheiku pages.

665d scope: 5 增量指标 ONLY (gdp_percapita/fiscal_rev/fixed_asset/retail/trade).
Reuses _extract_* functions from scripts/parse_hongheiku_10_indicators.py.
NOTE: 5 现指标 (gdp_total/gdp_growth/primary/secondary/tertiary) 不强制 parse — 663 baseline 已 hardcoded.

Cache path convention (mirroring 665a/665b/665c):
  /tmp/_665d_y2024_{province_en}.html

Expected: 28/28 PARSED (XIZANG cached via curl retry after urllib ERR).
GUANGDONG 2024 cat URL id 57657 — 不同于 2022/2023 PDF 目录页 id (需 parse 验证是否真公报).
"""
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, '/Users/kjonekong/projects/china platform/scripts')
from parse_hongheiku_10_indicators import (
    _extract_all,
    INDICATOR_LABELS,
)

CACHE_DIR = Path('/tmp')

# 28 entries — same as fetch_hongheiku_y2024.py
TO_FETCH_2024 = [
    ('anhui',       'ANHUI'),
    ('beijing',     'BEIJING'),
    ('chongqing',   'CHONGQING'),
    ('fujian',      'FUJIAN'),
    ('gansu',       'GANSU'),
    ('guangdong',   'GUANGDONG'),
    ('guangxi',     'GUANGXI'),
    ('hebei',       'HEBEI'),
    ('heilongjiang','HEILONGJIANG'),
    ('henan',       'HENAN'),
    ('hubei',       'HUBEI'),
    ('hunan',       'HUNAN'),
    ('jiangsu',     'JIANGSU'),
    ('jiangxi',     'JIANGXI'),
    ('jilin',       'JILIN'),
    ('neimenggu',   'NEI_MENGGU'),
    ('ningxia',     'NINGXIA'),
    ('qinghai',     'QINGHAI'),
    ('shaanxi',     'SHAANXI'),
    ('shandong',    'SHANDONG'),
    ('shanghai',    'SHANGHAI'),
    ('shanxi',      'SHANXI'),
    ('sichuan',     'SICHUAN'),
    ('tianjin',     'TIANJIN'),
    ('xinjiang',    'XINJIANG'),
    ('xizang',      'XIZANG'),
    ('yunnan',      'YUNNAN'),
    ('zhejiang',    'ZHEJIANG'),
]

# 665d: 5 增量 only (5 现 已在 663 baseline hardcoded)
INCREMENTAL_5 = ('gdp_percapita', 'fiscal_rev', 'fixed_asset', 'retail', 'trade')


def main() -> int:
    out_records = []
    parse_failures = []

    for prov_en, prov_code in TO_FETCH_2024:
        cache_path = CACHE_DIR / f'_665d_y2024_{prov_en}.html'
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
        # 665d: filter to 5 增量 only
        extracted_5 = {k: v for k, v in extracted.items() if k in INCREMENTAL_5}
        verdict = 'PARSED' if extracted_5 else 'PARSE_EMPTY'
        if not extracted_5:
            parse_failures.append(prov_en)
        out_records.append({
            'province_en': prov_en,
            'province_code': prov_code,
            'verdict': verdict,
            'extracted': extracted_5,
        })

    summary = {
        'total_provinces': len(TO_FETCH_2024),
        'parsed_count': sum(1 for r in out_records if r['verdict'] == 'PARSED'),
        'parse_empty_count': sum(1 for r in out_records if r['verdict'] == 'PARSE_EMPTY'),
        'cache_miss_count': sum(1 for r in out_records if r['verdict'] == 'CACHE_MISS'),
        'by_indicator': {},
    }
    for ind in INCREMENTAL_5:
        summary['by_indicator'][ind] = sum(
            1 for r in out_records if ind in r['extracted']
        )

    out = {
        'knife': '665',
        'sub_knife': '665d',
        'chain_id': 'parse_665d_m2_u10_batch_v1_y2024_5incremental',
        'year': 2024,
        'summary': summary,
        'parse_failures': parse_failures,
        'cells': out_records,
        'methodology': 'v1 5 增量 parse: 665d scope = gdp_percapita/fiscal_rev/fixed_asset/'
                       'retail/trade only (5 现 已在 663 baseline hardcoded, 不需 harvest). '
                       'reuses _extract_all from parse_hongheiku_10_indicators.py; '
                       'missing values stay None → DATA_MISSING (新增红线-1 沿用, 禁补零).',
    }

    out_path = Path(
        '/Users/kjonekong/projects/china platform/evidence_pack/'
        'u6_batch_y2024_parse_20260904.json'
    )
    out_path.parent.mkdir(exist_ok=True)
    out_path.write_text(json.dumps(out, ensure_ascii=False, indent=2), encoding='utf-8')
    print(f'wrote {out_path}')
    print(f'Parsed: {summary["parsed_count"]}/{summary["total_provinces"]}')
    print(f'Empty: {summary["parse_empty_count"]}')
    print('Per-indicator coverage (5 增量):')
    for ind, n in summary['by_indicator'].items():
        print(f'  {ind}: {n}/{summary["total_provinces"]}')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())