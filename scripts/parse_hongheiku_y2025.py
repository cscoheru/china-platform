#!/usr/bin/env python3
"""665e parse_hongheiku_y2025.py — parse 10 指标 from cached 2025 hongheiku pages.

665e scope: 10 指标 ALL (5 现 + 5 增量). 2025 无 663 baseline (vs 665d 仅补 5 增量).
Reuses _extract_all from scripts/parse_hongheiku_10_indicators.py.

Cache path convention (mirroring 665a/665b/665c/665d):
  /tmp/_665e_y2025_{province_en}.html

Expected: 30/30 PARSED (NINGXIA + GUIZHOU curl retry 200 OK).
GUANGDONG 2025 cat URL id 72064 = /xjtjgb/xj2020/ 真公报 (与 2024 sjtjgb id 57657 等价).
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

# 30 entries — same as fetch_hongheiku_y2025.py
TO_FETCH_2025 = [
    ('ningxia',      'NINGXIA'),
    ('guizhou',      'GUIZHOU'),
    ('guangdong',    'GUANGDONG'),
    ('shaanxi',      'SHAANXI'),
    ('jilin',        'JILIN'),
    ('henan',        'HENAN'),
    ('hebei',        'HEBEI'),
    ('guangxi',      'GUANGXI'),
    ('neimenggu',    'NEI_MENGGU'),
    ('xizang',       'XIZANG'),
    ('yunnan',       'YUNNAN'),
    ('shanghai',     'SHANGHAI'),
    ('heilongjiang', 'HEILONGJIANG'),
    ('chongqing',    'CHONGQING'),
    ('jiangxi',      'JIANGXI'),
    ('beijing',      'BEIJING'),
    ('hunan',        'HUNAN'),
    ('shanxi',       'SHANXI'),
    ('gansu',        'GANSU'),
    ('tianjin',      'TIANJIN'),
    ('xinjiang',     'XINJIANG'),
    ('fujian',       'FUJIAN'),
    ('anhui',        'ANHUI'),
    ('jiangsu',      'JIANGSU'),
    ('hubei',        'HUBEI'),
    ('sichuan',      'SICHUAN'),
    ('shandong',     'SHANDONG'),
    ('zhejiang',     'ZHEJIANG'),
    ('qinghai',      'QINGHAI'),
    ('hainan',       'HAINAN'),
]

# 665e: 10 指标 ALL (5 现 + 5 增量; 2025 无 663 baseline,需全 harvest — 与 665d 5 增量 only 不同)
ALL_10_INDICATORS = list(INDICATOR_LABELS.keys())  # = 10 指标 (5 现 + 5 增量)


def main() -> int:
    out_records = []
    parse_failures = []

    for prov_en, prov_code in TO_FETCH_2025:
        cache_path = CACHE_DIR / f'_665e_y2025_{prov_en}.html'
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
        # 665e: ALL 10 指标 (5 现 + 5 增量) — 不 filter
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
        'total_provinces': len(TO_FETCH_2025),
        'parsed_count': sum(1 for r in out_records if r['verdict'] == 'PARSED'),
        'parse_empty_count': sum(1 for r in out_records if r['verdict'] == 'PARSE_EMPTY'),
        'cache_miss_count': sum(1 for r in out_records if r['verdict'] == 'CACHE_MISS'),
        'by_indicator': {},
    }
    for ind in ALL_10_INDICATORS:
        summary['by_indicator'][ind] = sum(
            1 for r in out_records if ind in r['extracted']
        )

    out = {
        'knife': '665',
        'sub_knife': '665e',
        'chain_id': 'parse_665e_m2_u10_batch_v1_y2025_10indicators',
        'year': 2025,
        'summary': summary,
        'parse_failures': parse_failures,
        'cells': out_records,
        'methodology': 'v1 10 指标 parse: 665e scope = 10 指标 ALL (5 现 + 5 增量). '
                       '2025 无 663 baseline → harvest 必须含 5 现 (vs 665d 仅 5 增量). '
                       'reuses _extract_all from parse_hongheiku_10_indicators.py; '
                       'missing values stay None → DATA_MISSING (新增红线-1 沿用, 禁补零).',
    }

    out_path = Path(
        '/Users/kjonekong/projects/china platform/evidence_pack/'
        'u6_batch_y2025_parse_20260904.json'
    )
    out_path.parent.mkdir(exist_ok=True)
    out_path.write_text(json.dumps(out, ensure_ascii=False, indent=2), encoding='utf-8')
    print(f'wrote {out_path}')
    print(f'Parsed: {summary["parsed_count"]}/{summary["total_provinces"]}')
    print(f'Empty: {summary["parse_empty_count"]}')
    print('Per-indicator coverage (10 指标):')
    for ind, n in summary['by_indicator'].items():
        print(f'  {ind}: {n}/{summary["total_provinces"]}')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())