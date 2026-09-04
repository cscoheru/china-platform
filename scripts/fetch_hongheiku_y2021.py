#!/usr/bin/env python3
"""665 fetch_hongheiku_y2021.py — 29 省 × 10 指标 hongheiku 真实入库 (2021 年).

Mirror 658 pattern but expanded to:
- 29 provinces (vs 23 in 658; 2 missing: GUANGDONG, JIANGXI)
- year 2021 (per user_ruling_665, re-routed from 2020 due to hongheiku 0 entries)
- 10 indicators (5 现 + 5 增量) parsed in companion script parse_hongheiku_10_indicators.py

HTTP budget: 29 (within ≤32 红线).
"""
import json
import re
import urllib.request
import urllib.error
import ssl
import hashlib
import time
from pathlib import Path

try:
    import certifi
    _SSL_CTX = ssl.create_default_context(cafile=certifi.where())
except ImportError:
    _SSL_CTX = ssl.create_default_context()

# (province_en, url, province_code)
TO_FETCH_2021 = [
    ('anhui',       'https://tjgb.hongheiku.com/sjtjgb/24411.html', 'ANHUI'),
    ('beijing',     'https://tjgb.hongheiku.com/sjtjgb/24106.html', 'BEIJING'),
    ('chongqing',   'https://tjgb.hongheiku.com/sjtjgb/24421.html', 'CHONGQING'),
    ('fujian',      'https://tjgb.hongheiku.com/sjtjgb/24409.html', 'FUJIAN'),
    ('gansu',       'https://tjgb.hongheiku.com/sjtjgb/25126.html', 'GANSU'),
    ('guangxi',     'https://tjgb.hongheiku.com/sjtjgb/25371.html', 'GUANGXI'),
    ('guizhou',     'https://tjgb.hongheiku.com/sjtjgb/24718.html', 'GUIZHOU'),
    ('hainan',      'https://tjgb.hongheiku.com/sjtjgb/23920.html', 'HAINAN'),
    ('hebei',       'https://tjgb.hongheiku.com/sjtjgb/24077.html', 'HEBEI'),
    ('heilongjiang','https://tjgb.hongheiku.com/sjtjgb/27480.html', 'HEILONGJIANG'),
    ('henan',       'https://tjgb.hongheiku.com/sjtjgb/24374.html', 'HENAN'),
    ('hubei',       'https://tjgb.hongheiku.com/sjtjgb/24237.html', 'HUBEI'),
    ('hunan',       'https://tjgb.hongheiku.com/sjtjgb/25100.html', 'HUNAN'),
    ('jiangsu',     'https://tjgb.hongheiku.com/sjtjgb/24199.html', 'JIANGSU'),
    ('jilin',       'https://tjgb.hongheiku.com/sjtjgb/30339.html', 'JILIN'),
    ('liaoning',    'https://tjgb.hongheiku.com/sjtjgb/27517.html', 'LIAONING'),
    ('neimenggu',   'https://tjgb.hongheiku.com/sjtjgb/24061.html', 'NEI_MENGGU'),
    ('ningxia',     'https://tjgb.hongheiku.com/sjtjgb/27494.html', 'NINGXIA'),
    ('qinghai',     'https://tjgb.hongheiku.com/sjtjgb/24130.html', 'QINGHAI'),
    ('shaanxi',     'https://tjgb.hongheiku.com/sjtjgb/25693.html', 'SHAANXI'),
    ('shandong',    'https://tjgb.hongheiku.com/sjtjgb/24134.html', 'SHANDONG'),
    ('shanghai',    'https://tjgb.hongheiku.com/sjtjgb/25158.html', 'SHANGHAI'),
    ('shanxi',      'https://tjgb.hongheiku.com/sjtjgb/25002.html', 'SHANXI'),
    ('sichuan',     'https://tjgb.hongheiku.com/sjtjgb/24394.html', 'SICHUAN'),
    ('tianjin',     'https://tjgb.hongheiku.com/sjtjgb/25108.html', 'TIANJIN'),
    ('xinjiang',    'https://tjgb.hongheiku.com/sjtjgb/24838.html', 'XINJIANG'),
    ('xizang',      'https://tjgb.hongheiku.com/sjtjgb/26310.html', 'XIZANG'),
    ('yunnan',      'https://tjgb.hongheiku.com/sjtjgb/25260.html', 'YUNNAN'),
    ('zhejiang',    'https://tjgb.hongheiku.com/sjtjgb/24010.html', 'ZHEJIANG'),
]

# Per 660 红线 — 这些省在某些年份 hongheiku 转载有但 parse 不全
# 665 2021 不强制 BLOCKED (沿用 2024 实证); 仅 parse fail → DATA_MISSING 沿用新增红线-1
MISSING_PROVINCES_2021 = ['guangdong', 'jiangxi']  # hongheiku cat index 无 2021 条目

USER_AGENT = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) china-platform-research/1.0'

CACHE_DIR = Path('/tmp')


def _fetch(url: str, timeout: int = 30) -> tuple[bytes, int]:
    """Fetch URL with custom UA + certifi CA. Returns (body, http_code)."""
    req = urllib.request.Request(url, headers={'User-Agent': USER_AGENT})
    try:
        with urllib.request.urlopen(req, timeout=timeout, context=_SSL_CTX) as resp:
            return resp.read(), resp.status
    except urllib.error.HTTPError as e:
        return b'', e.code
    except Exception as e:
        return b'', 0


def main() -> int:
    results = []
    http_count = 0

    for prov_en, url, prov_code in TO_FETCH_2021:
        cache_path = CACHE_DIR / f'_665_y2021_{prov_en}.html'
        http_code = 0
        body = b''

        if cache_path.exists():
            body = cache_path.read_bytes()
            http_code = 200  # cached
        else:
            body, http_code = _fetch(url)
            http_count += 1
            if http_code == 200 and body:
                cache_path.write_bytes(body)
            time.sleep(0.5)  # polite crawl

        sha = hashlib.sha256(body).hexdigest() if body else ''
        results.append({
            'province_en': prov_en,
            'province_code': prov_code,
            'url': url,
            'http_code': http_code,
            'bytes': len(body),
            'sha256': sha,
            'cached': cache_path.exists() and http_code == 200 and not body == b'',
            'verdict': 'REACHABLE' if http_code == 200 else f'HTTP_{http_code}',
        })

    out = {
        'knife': '665',
        'sub_knife': '665a',
        'chain_id': 'real_665a_m2_u10_batch_v1_y2021',
        'year': 2021,
        'fetched_count': sum(1 for r in results if r['http_code'] == 200),
        'missing_in_2021_count': len(MISSING_PROVINCES_2021),
        'http_count': http_count,
        'http_limit': 32,
        'category_index_url': 'https://tjgb.hongheiku.com/category/sjtjgb',
        'cells': results,
        'missing_in_2021': [
            {'province': p, 'reason': 'NOT_FOUND_IN_2021_INDEX',
             'note': 'hongheiku cat index 无该省 2021 条目 (guangdong/jiangxi)'}
            for p in MISSING_PROVINCES_2021
        ],
        'methodology': 'v1 29 省 × 10 指标 hongheiku 转载页真实入库 (year 2021); '
                       'mirror 658 _extract_gdp pattern; 5 增量 (gdp_percapita/fiscal_rev/'
                       'fixed_asset/retail/trade) parse in companion script; '
                       '缺省 (GUANGDONG/JIANGXI) DATA_MISSING; SHA 锁转载字节; '
                       'lineage 三重标注模板',
    }

    out_path = Path(
        '/Users/kjonekong/projects/china platform/evidence_pack/'
        'u6_batch_y2021_fetch_20260904.json'
    )
    out_path.parent.mkdir(exist_ok=True)
    out_path.write_text(json.dumps(out, ensure_ascii=False, indent=2), encoding='utf-8')
    print(f'wrote {out_path}')
    print(f'Reachable: {out["fetched_count"]}/{len(TO_FETCH_2021)}')
    print(f'HTTP used: {http_count}/{out["http_limit"]}')
    print(f'Missing in 2021: {len(MISSING_PROVINCES_2021)} ({"+".join(MISSING_PROVINCES_2021)})')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())