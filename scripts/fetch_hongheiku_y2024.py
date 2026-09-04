#!/usr/bin/env python3
"""665d fetch_hongheiku_y2024.py — 28 省 × 5 增量 hongheiku harvest (2024 年).

665d scope: 5 增量指标 ONLY (gdp_percapita/fiscal_rev/fixed_asset/retail/trade).
663 baseline 已有 5 现 2024 (real_2024_provinces hardcoded); 665d 仅补 5 增量.

2024 cat index (knife 658 cache + 665d URL discovery 2026-09-04):
  28 entries tagged "2024年" — 缺 3 省 (GUIZHOU/HAINAN/LIAONING, 沿用 660 红线永久 DATA_MISSING).
  vs 665c 2023 (31 entries, 全 31 省); vs 665b 2022 (24 entries, 缺 7 省);
  GUANGDONG 2024 cat URL id 57657 (不同于 2022/2023 PDF 目录页 id, 需 fetch 验证是否真公报).

Exclusions: 0 (XPCC 38225 + Yiyang 35284 仅 2022 cat entries; 2024 cat index 无).

HTTP budget: 28 (≤32 红线 ✓). cat index 1 URL 复用 knife 658 cache.
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

# (province_en, numeric_id, province_code) — 2024 cat index 实证
TO_FETCH_2024 = [
    ('anhui',       '57296', 'ANHUI'),
    ('beijing',     '57258', 'BEIJING'),
    ('chongqing',   '57604', 'CHONGQING'),
    ('fujian',      '57209', 'FUJIAN'),
    ('gansu',       '57196', 'GANSU'),
    ('guangdong',   '57657', 'GUANGDONG'),
    ('guangxi',     '58355', 'GUANGXI'),
    ('hebei',       '59037', 'HEBEI'),
    ('heilongjiang','59289', 'HEILONGJIANG'),
    ('henan',       '58132', 'HENAN'),
    ('hubei',       '57472', 'HUBEI'),
    ('hunan',       '57486', 'HUNAN'),
    ('jiangsu',     '57215', 'JIANGSU'),
    ('jiangxi',     '57884', 'JIANGXI'),
    ('jilin',       '57522', 'JILIN'),
    ('neimenggu',   '58092', 'NEI_MENGGU'),
    ('ningxia',     '60392', 'NINGXIA'),
    ('qinghai',     '57094', 'QINGHAI'),
    ('shaanxi',     '57236', 'SHAANXI'),
    ('shandong',    '57113', 'SHANDONG'),
    ('shanghai',    '57536', 'SHANGHAI'),
    ('shanxi',      '58259', 'SHANXI'),
    ('sichuan',     '57219', 'SICHUAN'),
    ('tianjin',     '57426', 'TIANJIN'),
    ('xinjiang',    '57625', 'XINJIANG'),
    ('xizang',      '58383', 'XIZANG'),
    ('yunnan',      '58560', 'YUNNAN'),
    ('zhejiang',    '57047', 'ZHEJIANG'),
    # 3 missing provinces (GUIZHOU/HAINAN/LIAONING) — 沿用 660 红线永久 DATA_MISSING
]

USER_AGENT = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) china-platform-research/1.0'
CACHE_DIR = Path('/tmp')


def _fetch(url: str, timeout: int = 30) -> tuple[bytes, int]:
    """Fetch URL with custom UA + certifi CA. Returns (body, int)."""
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

    for prov_en, numeric_id, prov_code in TO_FETCH_2024:
        url = f'https://tjgb.hongheiku.com/sjtjgb/{numeric_id}.html'
        cache_path = CACHE_DIR / f'_665d_y2024_{prov_en}.html'
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
            'url': url,
            'numeric_id': numeric_id,
            'http_code': http_code,
            'verdict': verdict,
            'content_length': len(body),
            'sha256': sha256,
        })

    summary = {
        'knife': '665',
        'sub_knife': '665d',
        'year': 2024,
        'total_in_cat_index': 28,
        'exclusions': 0,
        'missing_3_provinces': ['GUIZHOU', 'HAINAN', 'LIAONING'],
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
        'cat_index_2024_filter': 28,
        'note_2024_scope': (
            '665d 范围: 5 增量 only (gdp_percapita/fiscal_rev/fixed_asset/retail/trade). '
            '663 baseline 已有 5 现 2024 hardcoded in real_2024_provinces. '
            'GUANGDONG 2024 cat URL id 57657 不同于 2023 (46971 PDF) / 2022 目录页; '
            '需 fetch 后 parse 验证是否真公报 vs PDF 目录页.'
        ),
        'note_missing_3_provinces': (
            'GUIZHOU/HAINAN/LIAONING 2024 cat index 无 (沿用 660 红线, 永久 DATA_MISSING). '
            '不在 665d fetch 范围, mart mart_province_timeseries 中这 3 省 × 2024 status=DATA_MISSING.'
        ),
    }

    out_path = Path(
        '/Users/kjonekong/projects/china platform/evidence_pack/'
        'u6_batch_y2024_fetch_20260904.json'
    )
    out_path.parent.mkdir(exist_ok=True)
    out_path.write_text(json.dumps(out, ensure_ascii=False, indent=2), encoding='utf-8')

    print(f'wrote {out_path}')
    print(f'TO_FETCH: {len(TO_FETCH_2024)} (vs 665c 31, -3 永久 missing)')
    print(f'  fetched: {summary["fetched_count"]}')
    print(f'  cache_hit: {summary["cache_hit_count"]}')
    print(f'  err: {summary["err_count"]}')
    print(f'  404: {summary["http_404_count"]}')
    print(f'HTTP used: {http_count}/28 (cat index 已 reuse, 不计)')
    return 0 if summary["err_count"] == 0 and summary["http_404_count"] == 0 else 1


if __name__ == '__main__':
    raise SystemExit(main())