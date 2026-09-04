#!/usr/bin/env python3
"""665 fetch_hongheiku_y2022.py — 24 省 × 10 指标 hongheiku 真实入库 (2022 年).

Mirror 665a (year 2021) pattern but re-routed to 2022:
- 24 provinces (vs 29 in 665a; 7 missing from cat index)
- year 2022 (per knife 665 program, 2020-2025 多年采集中)
- 10 indicators (5 现 + 5 增量) parsed in companion script parse_hongheiku_10_indicators.py

Exclusions (NOT included in TO_FETCH_2022 — not provinces):
  - id 38225 新疆生产建设兵团 (XPCC, special entity — P3 禁开)
  - id 35284 益阳市 (Hunan prefecture-level city — belongs to 669 program city tier)

Missing provinces (DATA_MISSING per 新增红线-1):
  - GANSU / GUIZHOU / HEILONGJIANG / HUNAN / LIAONING / NINGXIA / SHANGHAI
  Note: GUANGDONG appears in 2022 (id 35295) but was missing in 2021;
        JIANGXI appears in 2022 (id 35571) but was missing in 2021.

HTTP budget: 24 (well within ≤32 红线).
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
TO_FETCH_2022 = [
    ('anhui',       'https://tjgb.hongheiku.com/sjtjgb/35433.html', 'ANHUI'),
    ('beijing',     'https://tjgb.hongheiku.com/sjtjgb/35301.html', 'BEIJING'),
    ('chongqing',   'https://tjgb.hongheiku.com/sjtjgb/35269.html', 'CHONGQING'),
    ('fujian',      'https://tjgb.hongheiku.com/sjtjgb/35073.html', 'FUJIAN'),
    ('guangdong',   'https://tjgb.hongheiku.com/sjtjgb/35295.html', 'GUANGDONG'),
    ('guangxi',     'https://tjgb.hongheiku.com/sjtjgb/35377.html', 'GUANGXI'),
    ('hainan',      'https://tjgb.hongheiku.com/sjtjgb/34829.html', 'HAINAN'),
    ('hebei',       'https://tjgb.hongheiku.com/sjtjgb/34861.html', 'HEBEI'),
    ('henan',       'https://tjgb.hongheiku.com/sjtjgb/35348.html', 'HENAN'),
    ('hubei',       'https://tjgb.hongheiku.com/sjtjgb/35242.html', 'HUBEI'),
    ('jiangsu',     'https://tjgb.hongheiku.com/sjtjgb/35036.html', 'JIANGSU'),
    ('jiangxi',     'https://tjgb.hongheiku.com/sjtjgb/35571.html', 'JIANGXI'),
    ('jilin',       'https://tjgb.hongheiku.com/sjtjgb/35559.html', 'JILIN'),
    ('neimenggu',   'https://tjgb.hongheiku.com/sjtjgb/35106.html', 'NEI_MENGGU'),
    ('qinghai',     'https://tjgb.hongheiku.com/sjtjgb/34947.html', 'QINGHAI'),
    ('shaanxi',     'https://tjgb.hongheiku.com/sjtjgb/35911.html', 'SHAANXI'),
    ('shandong',    'https://tjgb.hongheiku.com/sjtjgb/34971.html', 'SHANDONG'),
    ('shanxi',      'https://tjgb.hongheiku.com/sjtjgb/35324.html', 'SHANXI'),
    ('sichuan',     'https://tjgb.hongheiku.com/sjtjgb/35297.html', 'SICHUAN'),
    ('tianjin',     'https://tjgb.hongheiku.com/sjtjgb/35254.html', 'TIANJIN'),
    ('xinjiang',    'https://tjgb.hongheiku.com/sjtjgb/35463.html', 'XINJIANG'),
    ('xizang',      'https://tjgb.hongheiku.com/sjtjgb/36952.html', 'XIZANG'),
    ('yunnan',      'https://tjgb.hongheiku.com/sjtjgb/35442.html', 'YUNNAN'),
    ('zhejiang',    'https://tjgb.hongheiku.com/sjtjgb/35126.html', 'ZHEJIANG'),
]

# Per 660 + 665b 新发现 — 这些省在 2022 年 hongheiku cat index 无完整公报正文:
#   - 7 原 missing: 年鉴发布滞后
#   - +2 新 missing: GUANGDONG + JIANGXI — cat index 有目录页(包含 2022 链接列表),
#     但目录页自身不含公报正文;公报 PDF 通过 wp-content/uploads/...pdf 内嵌在 pdfjs viewer,
#     需 PDF parser 提取. 665b 不启用 PDF 解析路径, 标记 DATA_MISSING.
#     待 666 OFFICIAL_INTAKED 升级时绕过 (粤/苏/浙 OFFICIAL 源用 HTML 公报).
MISSING_PROVINCES_2022 = [
    'gansu', 'guangdong', 'guizhou', 'heilongjiang', 'hunan',
    'jiangxi', 'liaoning', 'ningxia', 'shanghai',
]

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

    for prov_en, url, prov_code in TO_FETCH_2022:
        cache_path = CACHE_DIR / f'_665_y2022_{prov_en}.html'
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
            'verdict': 'REACHABLE' if http_code == 200 else f'HTTP_{http_code}',
        })

    out = {
        'knife': '665',
        'sub_knife': '665b',
        'chain_id': 'real_665b_m2_u10_batch_v1_y2022',
        'year': 2022,
        'fetched_count': sum(1 for r in results if r['http_code'] == 200),
        'missing_in_2022_count': len(MISSING_PROVINCES_2022),
        'http_count': http_count,
        'http_limit': 32,
        'category_index_url': 'https://tjgb.hongheiku.com/category/sjtjgb',
        'cells': results,
        'missing_in_2022': [
            {'province': p, 'reason': 'NOT_FOUND_IN_2022_INDEX',
             'note': 'hongheiku cat index 无该省 2022 条目 (年鉴发布滞后)'}
            for p in MISSING_PROVINCES_2022
        ],
        'excluded_from_index': [
            {'id': 38225, 'title': '新疆生产建设兵团2022年', 'reason': 'XPCC special entity (P3 禁开)'},
            {'id': 35284, 'title': '益阳市2022年', 'reason': '地级市, 属 669 程序 city tier'},
        ],
        'methodology': 'v1 24 省 × 10 指标 hongheiku 转载页真实入库 (year 2022); '
                       'mirror 665a _extract pattern; 5 增量 (gdp_percapita/fiscal_rev/'
                       'fixed_asset/retail/trade) parse in companion script; '
                       '缺省 7 省 DATA_MISSING; SHA 锁转载字节; '
                       'lineage 三重标注模板',
    }

    out_path = Path(
        '/Users/kjonekong/projects/china platform/evidence_pack/'
        'u6_batch_y2022_fetch_20260904.json'
    )
    out_path.parent.mkdir(exist_ok=True)
    out_path.write_text(json.dumps(out, ensure_ascii=False, indent=2), encoding='utf-8')
    print(f'wrote {out_path}')
    print(f'Reachable: {out["fetched_count"]}/{len(TO_FETCH_2022)}')
    print(f'HTTP used: {http_count}/{out["http_limit"]}')
    print(f'Missing in 2022: {len(MISSING_PROVINCES_2022)} ({"+".join(MISSING_PROVINCES_2022)})')
    print(f'Excluded from index: 2 (XPCC + Yiyang city)')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())