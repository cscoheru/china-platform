#!/usr/bin/env python3
"""665c fetch_hongheiku_y2023.py — 31 省 × 10 指标 hongheiku 真实入库 (2023 年).

Mirror 665b pattern but re-routed to 2023:
- 31 provinces (vs 24 in 665b; all cat index entries present)
- year 2023 (per knife 665 program, 2020-2025 多年采集中)
- 10 indicators (5 现 + 5 增量) parsed in companion script parse_hongheiku_y2023.py

2023 cat index (665c URL discovery 2026-09-04, 142 total cat entries):
  31 entries tagged "2023年" 全 31 省 — 比 665b (24 省) +7 (gansu/guangdong/guizhou/
  heilongjiang/hunan/jiangxi/liaoning/ningxia/shanghai 全 2023 入库).

Exclusions: 0 (XPCC 38225 + Yiyang 35284 仅 2022 年条目, 2023 cat index 无).
  P3 禁开 + 669 程序 city tier 沿用.

HTTP budget: 31 (≤32 红线 ✓). cat index 1 URL 复用 knife 666 probe 阶段 + 本次
discovery, evidence 写入 u6_batch_y2023_discovery_20260904.json.
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

# (province_en, numeric_id, province_code) — 2023 cat index 实证全 31 省
TO_FETCH_2023 = [
    ('anhui',       '45810', 'ANHUI'),
    ('beijing',     '45828', 'BEIJING'),
    ('chongqing',   '46420', 'CHONGQING'),
    ('fujian',      '51411', 'FUJIAN'),
    ('gansu',       '45809', 'GANSU'),
    ('guangdong',   '46971', 'GUANGDONG'),
    ('guangxi',     '46473', 'GUANGXI'),
    ('guizhou',     '49705', 'GUIZHOU'),
    ('hainan',      '45465', 'HAINAN'),
    ('hebei',       '45476', 'HEBEI'),
    ('heilongjiang','52555', 'HEILONGJIANG'),
    ('henan',       '46449', 'HENAN'),
    ('hubei',       '46035', 'HUBEI'),
    ('hunan',       '46282', 'HUNAN'),
    ('jiangsu',     '45572', 'JIANGSU'),
    ('jiangxi',     '46698', 'JIANGXI'),
    ('jilin',       '51412', 'JILIN'),
    ('liaoning',    '49311', 'LIAONING'),
    ('neimenggu',   '45765', 'NEI_MENGGU'),
    ('ningxia',     '49543', 'NINGXIA'),
    ('qinghai',     '51410', 'QINGHAI'),
    ('shaanxi',     '46448', 'SHAANXI'),
    ('shandong',    '45559', 'SHANDONG'),
    ('shanghai',    '46363', 'SHANGHAI'),
    ('shanxi',      '45785', 'SHANXI'),
    ('sichuan',     '45628', 'SICHUAN'),
    ('tianjin',     '45872', 'TIANJIN'),
    ('xinjiang',    '46388', 'XINJIANG'),
    ('xizang',      '49950', 'XIZANG'),
    ('yunnan',      '46336', 'YUNNAN'),
    ('zhejiang',    '45544', 'ZHEJIANG'),
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

    for prov_en, numeric_id, prov_code in TO_FETCH_2023:
        url = f'https://tjgb.hongheiku.com/sjtjgb/{numeric_id}.html'
        cache_path = CACHE_DIR / f'_665_y2023_{prov_en}.html'
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
        'sub_knife': '665c',
        'year': 2023,
        'total_in_cat_index': 31,
        'exclusions': 0,
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
        'cat_index_total_entries': 142,
        'cat_index_2023_filter': 31,
        'note_2023_finds': (
            '2023 cat index 全 31 省 (vs 665b 24 省); 7 之前 missing 全部入库: '
            'GANSU/GUIZHOU/HEILONGJIANG/HUNAN/LIAONING/NINGXIA/SHANGHAI. '
            'GUANGDONG/JIANGXI 2021+2022 目录页, 2023 入口 id 不同, 需 fetch 后验证是否真公报.'
        ),
        'note_exclusions': (
            'XPCC (38225) + Yiyang (35284) 仅 2022 cat entries; 2023 cat index 0 排除.'
        ),
    }

    out_path = Path(
        '/Users/kjonekong/projects/china platform/evidence_pack/'
        'u6_batch_y2023_fetch_20260904.json'
    )
    out_path.parent.mkdir(exist_ok=True)
    out_path.write_text(json.dumps(out, ensure_ascii=False, indent=2), encoding='utf-8')

    print(f'wrote {out_path}')
    print(f'TO_FETCH: {len(TO_FETCH_2023)} (vs 665b 24, +7 新入库)')
    print(f'  fetched: {summary["fetched_count"]}')
    print(f'  cache_hit: {summary["cache_hit_count"]}')
    print(f'  err: {summary["err_count"]}')
    print(f'  404: {summary["http_404_count"]}')
    print(f'HTTP used: {http_count}/31 (cat index 已 reuse 666 probe stage, 不计)')
    return 0 if summary["err_count"] == 0 and summary["http_404_count"] == 0 else 1


if __name__ == '__main__':
    raise SystemExit(main())