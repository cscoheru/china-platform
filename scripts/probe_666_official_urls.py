#!/usr/bin/env python3
"""666 probe: 3 省 TJGB 入口 + 公报索引 (3 HTTP 预算).

Per memory china-platform-python-urllib-ssl-clash-proxy: 使用 certifi SSL context
绕 LibreSSL + Clash 代理的 CERTIFICATE_VERIFY_FAILED 坑。
"""
import json
import ssl
import sys
import urllib.request
import urllib.error
from pathlib import Path

import certifi

OUT_PATH = Path('/Users/kjonekong/projects/china platform/evidence_pack/'
                'u6_batch_y666_probe_20260904.json')
USER_AGENT = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) ResearchBot/1.0'

# Try both tjj.* and stats.* hostnames (modern provinces use stats.*)
INDEX_URLS = [
    ('GUANGDONG_tjj',  'https://tjj.gd.gov.cn/tjgb/'),
    ('GUANGDONG_stats', 'https://stats.gd.gov.cn/'),
    ('JIANGSU_tjj',    'https://tjj.jiangsu.gov.cn/tjgb/'),
    ('JIANGSU_stats',  'https://stats.js.gov.cn/'),
    ('ZHEJIANG_tjj',   'https://tjj.zj.gov.cn/tjgb/'),
    ('ZHEJIANG_stats', 'https://stats.zj.gov.cn/'),
]


def probe(url: str, timeout: int = 15) -> dict:
    ctx = ssl.create_default_context(cafile=certifi.where())
    req = urllib.request.Request(url, headers={'User-Agent': USER_AGENT})
    try:
        with urllib.request.urlopen(req, context=ctx, timeout=timeout) as r:
            body = r.read()
            return {
                'url': url,
                'verdict': 'REACHABLE',
                'http_code': r.status,
                'content_length': len(body),
                'content_type': r.headers.get('Content-Type', ''),
            }
    except urllib.error.HTTPError as e:
        return {
            'url': url,
            'verdict': f'HTTP_{e.code}',
            'http_code': e.code,
            'reason': str(e)[:200],
        }
    except Exception as e:
        return {
            'url': url,
            'verdict': 'ERR',
            'http_code': 0,
            'reason': f'{type(e).__name__}: {str(e)[:200]}',
        }


def main() -> int:
    results = []
    for label, url in INDEX_URLS:
        print(f'probing {label}: {url} ...', end=' ', flush=True)
        r = probe(url)
        r['label'] = label
        print(f'{r["verdict"]} (http={r["http_code"]}, {r.get("content_length", "?")} bytes)')
        results.append(r)

    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUT_PATH.write_text(
        json.dumps({
            'generated_at': '2026-09-04',
            'knife': '666',
            'probe_methodology': 'urllib + certifi SSL + Mozilla UA, timeout 15s',
            'probes': results,
        }, ensure_ascii=False, indent=2),
        encoding='utf-8',
    )
    print(f'\nResults saved to {OUT_PATH}')
    print(f'HTTP used: {len(results)}/9 (3 remaining for 公报 year pages)')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
