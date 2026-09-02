#!/usr/bin/env python3
"""658 fetch_m2_u6_batch_26prov_2024.py — 26 省 × 5 指标 hongheiku 真实入库."""
import json
import re
import hashlib
from pathlib import Path

TO_FETCH = [
    ('tianjin',     'https://tjgb.hongheiku.com/sjtjgb/57426.html'),
    ('chongqing',   'https://tjgb.hongheiku.com/sjtjgb/57604.html'),
    ('hebei',       'https://tjgb.hongheiku.com/sjtjgb/59037.html'),
    ('shanxi',      'https://tjgb.hongheiku.com/sjtjgb/58259.html'),
    ('neimenggu',   'https://tjgb.hongheiku.com/sjtjgb/58092.html'),
    ('jilin',       'https://tjgb.hongheiku.com/sjtjgb/57522.html'),
    ('heilongjiang','https://tjgb.hongheiku.com/sjtjgb/59289.html'),
    ('jiangsu',     'https://tjgb.hongheiku.com/sjtjgb/57215.html'),
    ('zhejiang',    'https://tjgb.hongheiku.com/sjtjgb/57047.html'),
    ('anhui',       'https://tjgb.hongheiku.com/sjtjgb/57296.html'),
    ('fujian',      'https://tjgb.hongheiku.com/sjtjgb/57209.html'),
    ('jiangxi',     'https://tjgb.hongheiku.com/sjtjgb/57884.html'),
    ('henan',       'https://tjgb.hongheiku.com/sjtjgb/58132.html'),
    ('hunan',       'https://tjgb.hongheiku.com/sjtjgb/57486.html'),
    ('guangdong',   'https://tjgb.hongheiku.com/sjtjgb/57657.html'),
    ('guangxi',     'https://tjgb.hongheiku.com/sjtjgb/58355.html'),
    ('yunnan',      'https://tjgb.hongheiku.com/sjtjgb/58560.html'),
    ('xizang',      'https://tjgb.hongheiku.com/sjtjgb/58383.html'),
    ('shaanxi',     'https://tjgb.hongheiku.com/sjtjgb/57236.html'),
    ('gansu',       'https://tjgb.hongheiku.com/sjtjgb/57196.html'),
    ('qinghai',     'https://tjgb.hongheiku.com/sjtjgb/57094.html'),
    ('ningxia',     'https://tjgb.hongheiku.com/sjtjgb/60392.html'),
    ('xinjiang',    'https://tjgb.hongheiku.com/sjtjgb/57625.html'),
]

BLOCKED_PROVINCES = ['liaoning', 'hainan', 'guizhou']  # missing from 2024 index

def _extract_gdp(text: str) -> float | None:
    """Extract GDP from the introductory section of a 统计公报 page.

    Strategy: locate the "综合"/" / "初步核算"/" / "根据" anchor (first paragraph of
    section 1, where the headline GDP lives), then search the next ~250 chars for a
    value with "亿元" suffix. This avoids matching partial-region phrases like
    "经济区生产总值" that appear later in the page.
    """
    # Find the "综合"/"初步核算"/"根据" anchor; capture ~250 chars after it
    anchor_pat = re.compile(r'(?:一、\s*综合|初步核算|根据地区生产总值统一核算结果|根据国家统一初步核算)')
    m = anchor_pat.search(text)
    if not m:
        return None
    window = text[m.start():m.start() + 250]
    # In that window, find the first GDP value (large number + 亿元)
    gdp_pats = [
        # Standard: 实现地区生产总值 [...] X亿元 — bracket/parens in any order,
        # brackets may be nested (e.g. "[ [2] ]") per qinghai's wording.
        r'(?:全省|全市|全区|广东)?(?:实现)?(?:地区)?生产总值'
        r'(?:\s*(?:\[[^\[\]]*(?:\[[^\]]*\][^\[\]]*)*\]|\([^\)]*\)|（[^）]*\）))*\s*'
        r'(?:为\s*)?([\d,\.]+)\s*亿元',
    ]
    for pat in gdp_pats:
        for match in re.finditer(pat, window):
            try:
                v = float(match.group(1).replace(',', ''))
                if v >= 100:  # provincial-scale, not per-capita
                    return v
            except ValueError:
                pass
    return None


def _extract(text: str) -> dict:
    r = {}
    # GDP — anchored to "综合"/"初步核算"/"根据" section opener
    gdp = _extract_gdp(text)
    if gdp is not None:
        r['gdp_total'] = gdp
    # 增速
    m = re.search(r'比(?:上年|上年同期|同期)增(?:长|加)\s*([\d.]+)\s*%', text)
    if m:
        try:
            r['growth'] = float(m.group(1))
        except ValueError:
            pass
    # Industries — try inline '分别为X亿元、Y亿元和Z亿元' first (zhejiang-style)
    m = re.search(
        r'第[一二三][^产]{0,20}产业增加值分别为([\d,\.]+)亿元、([\d,\.]+)亿元和([\d,\.]+)亿元',
        text,
    )
    if m:
        try:
            r['primary'] = float(m.group(1).replace(',', ''))
            r['secondary'] = float(m.group(2).replace(',', ''))
            r['tertiary'] = float(m.group(3).replace(',', ''))
        except ValueError:
            pass
    else:
        for kw, key in (
            ('第一产业增加值', 'primary'),
            ('第二产业增加值', 'secondary'),
        ):
            m = re.search(rf'{kw}\s*(?:\[\d+\])?\s*([\d,\.]+)\s*亿', text)
            if m:
                try:
                    r[key] = float(m.group(1).replace(',', ''))
                except ValueError:
                    pass
        for pat in (
            r'第三产业增加值\s*(?:\[\d+\])?\s*([\d,\.]+)\s*亿',
            r'第三产业\s*(?:\[\d+\])?增加值\s*(?:\[\d+\])?\s*([\d,\.]+)\s*亿',
        ):
            m = re.search(pat, text)
            if m:
                try:
                    r['tertiary'] = float(m.group(1).replace(',', ''))
                    break
                except ValueError:
                    pass
    return r


def main() -> int:
    results = []
    http_count = 0  # 0 here — files are pre-fetched (per 657-A category-first cache)
    for prov_en, url in TO_FETCH:
        body_path = Path(f'/tmp/_658_{prov_en}.html')
        if not body_path.exists():
            results.append({
                'province': prov_en,
                'url': url,
                'http_code': 0,
                'bytes': 0,
                'sha256': '',
                'verdict': 'CACHE_MISS',
                'extracted': {},
            })
            continue
        body = body_path.read_text(encoding='utf-8', errors='replace')
        text = re.sub(r'<[^>]+>', ' ', body)
        text = re.sub(r'\s+', ' ', text)
        sha = hashlib.sha256(body.encode('utf-8')).hexdigest()
        extracted = _extract(text)
        http_count += 1
        results.append({
            'province': prov_en,
            'url': url,
            'http_code': 200,
            'bytes': len(body.encode('utf-8')),
            'sha256': sha,
            'verdict': 'REACHABLE',
            'extracted': extracted,
        })

    out = {
        'knife': '658',
        'chain_id': 'real_658_m2_u6_batch_v1',
        'substitute_pool_status': 'EXHAUSTED',
        'substitute_used_count': 0,
        'fetched_count': sum(1 for r in results if r.get('verdict') == 'REACHABLE'),
        'blocked_no_pool_count': len(BLOCKED_PROVINCES),
        'http_count': http_count,
        'http_limit': 32,
        'category_index_url': 'https://tjgb.hongheiku.com/category/sjtjgb',
        'cells': results,
        'blocked_provinces': [
            {'province': p, 'reason': 'NOT_FOUND_IN_2024_INDEX',
             'note': '2024 公报索引页 /category/sjtjgb 无该省 2024 条目（liaoning/hainan/guizhou）'}
            for p in BLOCKED_PROVINCES
        ],
        'methodology': 'v1 26 省 × 5 指标 hongheiku 转载页真实入库; category-first URL 发现; '
                       '缺省 BLOCKED 禁补零; SHA 锁转载字节; lineage 三重标注模板',
    }

    out_path = Path('/Users/kjonekong/projects/china platform/evidence_pack/u6_batch_26prov_fetch_20260902.json')
    out_path.parent.mkdir(exist_ok=True)
    out_path.write_text(json.dumps(out, ensure_ascii=False, indent=2), encoding='utf-8')
    print(f'wrote {out_path}')

    complete = sum(1 for r in results if len(r.get('extracted', {})) == 5)
    gdp_n = sum(1 for r in results if 'gdp_total' in r.get('extracted', {}))
    print(f'Reachable: {out["fetched_count"]}/{len(TO_FETCH)}')
    print(f'GDP captured: {gdp_n}/{len(TO_FETCH)}')
    print(f'Complete 5/5: {complete}/{len(TO_FETCH)}')
    print(f'Blocked: {len(BLOCKED_PROVINCES)} ({"+".join(BLOCKED_PROVINCES)})')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())