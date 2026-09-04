#!/usr/bin/env python3
"""665e fetch_hongheiku_y2025.py — 30 省 × 10 指标 hongheiku harvest (2025 年).

665e scope: 10 指标 ALL (gdp_total/gdp_growth/primary_gdp/secondary_gdp/tertiary_gdp
+ gdp_percapita/fiscal_rev/fixed_asset/retail/trade). 2025 无 663 baseline,需全 harvest.

2025 cat index (knife 658 cache + 665e URL discovery 2026-09-04):
  30 entries tagged "2025年". 缺 1 省 (LIAONING, 沿用 660 红线永久 DATA_MISSING).
  30 entries - 1 missing = 30 实 fetch (GUANGDONG 2024 cat id 57657 真公报 → 2025 id 72064;
  但 GUIZHOU 2024 cat index 缺 → 2025 cat id 72067 回来了; HAINAN 2024 cat index 缺
  → 2025 cat id 67979 回来了). 3 个 2025 cat entries 走 /xjtjgb/xj2020/ path
  (GUIZHOU/GUANGDONG/SHAANXI) — 与标准 /sjtjgb/ 不同的 URL 格式.

Exclusions: 0 (XPCC 38225 + Yiyang 35284 仅 2022 cat entries; 2025 cat index 无).
GUANGDONG 2025 是真公报 (与 2024 cat id 57657 同模式 — 走 xjtjgb 但 cat 标记真公报).

HTTP budget: 30 (≤32 红线 ✓). cat index 1 URL 复用 knife 658 cache (不另 fetch).
"""
import json
import urllib.request
import urllib.error
import ssl
import hashlib
from pathlib import Path

try:
    import certifi
    _SSL_CTX = ssl.create_default_context(cafile=certifi.where())
except ImportError:
    _SSL_CTX = ssl.create_default_context()

# (province_en, numeric_id, province_code, path_kind)
# path_kind: 'sjtjgb' = https://tjgb.hongheiku.com/sjtjgb/{id}.html
#            'xjtjgb' = https://tjgb.hongheiku.com/xjtjgb/xj2020/{id}.html
TO_FETCH_2025 = [
    ('ningxia',      '72070', 'NINGXIA',     'sjtjgb'),
    ('guizhou',      '72067', 'GUIZHOU',     'xjtjgb'),
    ('guangdong',    '72064', 'GUANGDONG',   'xjtjgb'),
    ('shaanxi',      '72041', 'SHAANXI',     'xjtjgb'),
    ('jilin',        '69683', 'JILIN',       'sjtjgb'),
    ('henan',        '68789', 'HENAN',       'sjtjgb'),
    ('hebei',        '68598', 'HEBEI',       'sjtjgb'),
    ('guangxi',      '68499', 'GUANGXI',     'sjtjgb'),
    ('neimenggu',    '68485', 'NEI_MENGGU',  'sjtjgb'),
    ('xizang',       '68383', 'XIZANG',      'sjtjgb'),
    ('yunnan',       '68361', 'YUNNAN',      'sjtjgb'),
    ('shanghai',     '68318', 'SHANGHAI',    'sjtjgb'),
    ('heilongjiang', '68290', 'HEILONGJIANG','sjtjgb'),
    ('chongqing',    '68287', 'CHONGQING',   'sjtjgb'),
    ('jiangxi',      '68286', 'JIANGXI',     'sjtjgb'),
    ('beijing',      '68263', 'BEIJING',     'sjtjgb'),
    ('hunan',        '68248', 'HUNAN',       'sjtjgb'),
    ('shanxi',       '68246', 'SHANXI',      'sjtjgb'),
    ('gansu',        '68229', 'GANSU',       'sjtjgb'),
    ('tianjin',      '68209', 'TIANJIN',     'sjtjgb'),
    ('xinjiang',     '68172', 'XINJIANG',    'sjtjgb'),
    ('fujian',       '68169', 'FUJIAN',      'sjtjgb'),
    ('anhui',        '68161', 'ANHUI',       'sjtjgb'),
    ('jiangsu',      '68159', 'JIANGSU',     'sjtjgb'),
    ('hubei',        '68147', 'HUBEI',       'sjtjgb'),
    ('sichuan',      '68145', 'SICHUAN',     'sjtjgb'),
    ('shandong',     '68060', 'SHANDONG',    'sjtjgb'),
    ('zhejiang',     '68044', 'ZHEJIANG',    'sjtjgb'),
    ('qinghai',      '68037', 'QINGHAI',     'sjtjgb'),
    ('hainan',       '67979', 'HAINAN',      'sjtjgb'),
    # 1 missing province (LIAONING) — 沿用 660 红线永久 DATA_MISSING
]

USER_AGENT = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) china-platform-research/1.0'
CACHE_DIR = Path('/tmp')


def _url_for(numeric_id: str, path_kind: str) -> str:
    if path_kind == 'xjtjgb':
        return f'https://tjgb.hongheiku.com/xjtjgb/xj2020/{numeric_id}.html'
    return f'https://tjgb.hongheiku.com/sjtjgb/{numeric_id}.html'


def _fetch(url: str, timeout: int = 30) -> tuple[bytes, int]:
    """Fetch URL with custom UA + certifi CA. Returns (body, http_code)."""
    req = urllib.request.Request(url, headers={'User-Agent': USER_AGENT})
    try:
        with urllib.request.urlopen(req, timeout=timeout, context=_SSL_CTX) as resp:
            return resp.read(), resp.status
    except urllib.error.HTTPError as e:
        return b'', e.code
    except Exception:
        return b'', 0


def main() -> int:
    results = []
    http_count = 0

    for prov_en, numeric_id, prov_code, path_kind in TO_FETCH_2025:
        url = _url_for(numeric_id, path_kind)
        cache_path = CACHE_DIR / f'_665e_y2025_{prov_en}.html'
        http_code = 0
        body = b''

        if cache_path.exists():
            body = cache_path.read_bytes()
            http_code = 200  # from cache
            verdict = 'CACHE_HIT'
        else:
            body, http_code = _fetch(url)
            http_count += 1
            if http_code == 200 and body:
                cache_path.write_bytes(body)
                verdict = 'FETCHED'
            elif http_code == 404:
                verdict = 'HTTP_404'
            elif http_code == 0:
                verdict = 'ERR'
            else:
                verdict = f'HTTP_{http_code}'

        sha256 = hashlib.sha256(body).hexdigest() if body else ''
        results.append({
            'province_en': prov_en,
            'province_code': prov_code,
            'numeric_id': numeric_id,
            'path_kind': path_kind,
            'url': url,
            'http_code': http_code,
            'verdict': verdict,
            'content_length': len(body),
            'sha256': sha256,
        })

    summary = {
        'knife': '665',
        'sub_knife': '665e',
        'year': 2025,
        'total_in_cat_index': 30,
        'exclusions': 0,
        'missing_1_province': ['LIAONING'],
        'xjtjgb_path_count': sum(1 for r in results if r['path_kind'] == 'xjtjgb'),
        'fetched_count': sum(1 for r in results if r['verdict'] == 'FETCHED'),
        'cache_hit_count': sum(1 for r in results if r['verdict'] == 'CACHE_HIT'),
        'err_count': sum(1 for r in results if r['verdict'] == 'ERR'),
        'http_404_count': sum(1 for r in results if r['verdict'] == 'HTTP_404'),
        'http_used': http_count,
        'fetched_at': '2026-09-04',
    }

    out = {
        'summary': summary,
        'cells': results,
        'cat_index_url': 'https://tjgb.hongheiku.com/category/sjtjgb',
        'cat_index_2025_filter': 30,
        'note_2025_scope': (
            '665e 范围: 10 指标 ALL (5 现 + 5 增量). 2025 无 663 baseline,需全 harvest. '
            'cat index 30 entries (vs 665c 2023=31 全 31; vs 665d 2024=28 -3). '
            '缺 1 省 LIAONING 沿用 660 红线永久 DATA_MISSING. '
            '+GUIZHOU/HAINAN 2025 已发布(2024 缺文). '
            '3 个 2025 cat entries 走 /xjtjgb/xj2020/ URL path (GUIZHOU/GUANGDONG/SHAANXI), '
            '与标准 /sjtjgb/ 不同 — fetch script 支持 2 模式.'
        ),
        'note_xjtjgb_path': (
            'GUIZHOU 2025 id=72067 / GUANGDONG 2025 id=72064 / SHAANXI 2025 id=72041 '
            '走 https://tjgb.hongheiku.com/xjtjgb/xj2020/{id}.html 路径. '
            'GUANGDONG 2025 走 xjtjgb 但 cat 标记真公报 (与 2024 cat id 57657 sjtjgb 同样可解析). '
            'fetch script _url_for() 根据 path_kind 自动切换 base URL.'
        ),
    }

    out_path = Path(
        '/Users/kjonekong/projects/china platform/evidence_pack/'
        'u6_batch_y2025_fetch_20260904.json'
    )
    out_path.parent.mkdir(exist_ok=True)
    out_path.write_text(json.dumps(out, ensure_ascii=False, indent=2), encoding='utf-8')

    print(f'wrote {out_path}')
    print(f'TO_FETCH: {len(TO_FETCH_2025)} (vs 665c 31, vs 665d 28, +2 GUIZHOU/HAINAN)')
    print(f'  xjtjgb path: {summary["xjtjgb_path_count"]}')
    print(f'  fetched: {summary["fetched_count"]}')
    print(f'  cache_hit: {summary["cache_hit_count"]}')
    print(f'  err: {summary["err_count"]}')
    print(f'  404: {summary["http_404_count"]}')
    print(f'HTTP used: {http_count}/30 (cat index 已 reuse, 不计)')
    return 0 if summary["err_count"] == 0 and summary["http_404_count"] == 0 else 1


if __name__ == '__main__':
    raise SystemExit(main())