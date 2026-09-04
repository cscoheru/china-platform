#!/usr/bin/env python3
"""666 probe round 2: 3 targeted URL (final 3 HTTP budget)."""
import json
import ssl
import urllib.request
import urllib.error
from pathlib import Path

import certifi

OUT_PATH = Path('/Users/kjonekong/projects/china platform/evidence_pack/'
                'u6_batch_y666_probe2_20260904.json')
USER_AGENT = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) ResearchBot/1.0'

# Round 2: try 3 most likely alternative URLs for 公报
TARGET_URLS = [
    ('GUANGDONG_stats_tjgb', 'https://stats.gd.gov.cn/tjgb/'),
    ('GUANGDONG_www_tjj',   'https://www.tjj.gd.gov.cn/'),
    ('ZHEJIANG_stats_root', 'https://tjj.zj.gov.cn/col/col1229316002/'),  # 公报栏目
]


def probe(url: str, timeout: int = 15) -> dict:
    ctx = ssl.create_default_context(cafile=certifi.where())
    req = urllib.request.Request(url, headers={'User-Agent': USER_AGENT})
    try:
        with urllib.request.urlopen(req, context=ctx, timeout=timeout) as r:
            body = r.read()
            return {
                'url': url, 'verdict': 'REACHABLE', 'http_code': r.status,
                'content_length': len(body),
                'content_type': r.headers.get('Content-Type', ''),
            }
    except urllib.error.HTTPError as e:
        return {'url': url, 'verdict': f'HTTP_{e.code}', 'http_code': e.code,
                'reason': str(e)[:200]}
    except Exception as e:
        return {'url': url, 'verdict': 'ERR', 'http_code': 0,
                'reason': f'{type(e).__name__}: {str(e)[:200]}'}


def main() -> int:
    results = []
    for label, url in TARGET_URLS:
        print(f'probing {label}: {url[:70]} ...', end=' ', flush=True)
        r = probe(url)
        r['label'] = label
        print(f'{r["verdict"]} (http={r["http_code"]})')
        results.append(r)

    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUT_PATH.write_text(
        json.dumps({
            'generated_at': '2026-09-04',
            'knife': '666',
            'probe_methodology': 'urllib + certifi SSL, 3 HTTP budget remaining',
            'probes': results,
            'total_http_used_so_far': 9,
        }, ensure_ascii=False, indent=2),
        encoding='utf-8',
    )
    print(f'\nResults saved to {OUT_PATH}')
    print(f'TOTAL HTTP used: 9/9 (knife budget EXHAUSTED)')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
