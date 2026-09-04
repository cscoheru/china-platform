#!/usr/bin/env python3
"""665 parse_hongheiku_10_indicators.py — 10 指标 parse from cached hongheiku pages.

5 现 indicators (mirror 658 _extract logic):
  - gdp_total        地区生产总值
  - gdp_growth       GDP 增速
  - primary_gdp      第一产业增加值
  - secondary_gdp    第二产业增加值
  - tertiary_gdp     第三产业增加值

5 增量 indicators (new for 665):
  - gdp_percapita    人均地区生产总值
  - fiscal_rev       一般公共预算收入 (地方)
  - fixed_asset      固定资产投资 (含括号说明)
  - retail           社会消费品零售总额
  - trade            进出口总额

Each indicator uses a section anchor + value pattern; missing values stay None
→ DATA_MISSING downstream.
"""
import json
import re
from pathlib import Path

CACHE_DIR = Path('/tmp')

# Reuse TO_FETCH_2021 from fetch script
TO_FETCH_2021 = [
    ('anhui',       'ANHUI'),
    ('beijing',     'BEIJING'),
    ('chongqing',   'CHONGQING'),
    ('fujian',      'FUJIAN'),
    ('gansu',       'GANSU'),
    ('guangxi',     'GUANGXI'),
    ('guizhou',     'GUIZHOU'),
    ('hainan',      'HAINAN'),
    ('hebei',       'HEBEI'),
    ('heilongjiang','HEILONGJIANG'),
    ('henan',       'HENAN'),
    ('hubei',       'HUBEI'),
    ('hunan',       'HUNAN'),
    ('jiangsu',     'JIANGSU'),
    ('jilin',       'JILIN'),
    ('liaoning',    'LIAONING'),
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

INDICATOR_LABELS = {
    'gdp_total':      ('地区生产总值', '亿元'),
    'gdp_growth':     ('GDP 增速', '%'),
    'primary_gdp':    ('第一产业增加值', '亿元'),
    'secondary_gdp':  ('第二产业增加值', '亿元'),
    'tertiary_gdp':   ('第三产业增加值', '亿元'),
    'gdp_percapita':  ('人均地区生产总值', '元'),
    'fiscal_rev':     ('一般公共预算收入', '亿元'),
    'fixed_asset':    ('固定资产投资', '亿元'),
    'retail':         ('社会消费品零售总额', '亿元'),
    'trade':          ('进出口总额', '亿元'),
}


def _extract_gdp_total(text: str) -> float | None:
    """5 现 — gdp_total. Anchor on 综合/初步核算 section opener."""
    anchor = re.compile(r'(?:一、\s*综合|初步核算|根据地区生产总值统一核算结果|根据国家统一初步核算)')
    m = anchor.search(text)
    if not m:
        return None
    window = text[m.start():m.start() + 280]
    pat = re.compile(
        r'(?:全省|全市|全区|广东)?(?:实现)?(?:地区)?生产总值'
        r'(?:\s*(?:\[[^\[\]]*(?:\[[^\]]*\][^\[\]]*)*\]|\([^\)]*\)|（[^）]*\）))*\s*'
        r'(?:为\s*)?([\d,\.]+)\s*亿元'
    )
    for match in pat.finditer(window):
        try:
            v = float(match.group(1).replace(',', ''))
            if v >= 100:
                return v
        except ValueError:
            pass
    return None


def _extract_gdp_growth(text: str) -> float | None:
    """5 现 — gdp_growth. Pattern: 比上年增长 X.X%."""
    m = re.search(r'比(?:上年|上年同期|同期)增(?:长|加)\s*([\d.]+)\s*[%％]', text)
    if m:
        try:
            return float(m.group(1))
        except ValueError:
            pass
    return None


def _extract_industry(text: str, kw: str) -> float | None:
    """5 现 — primary/secondary/tertiary. Pattern: 第X产业增加值 Y 亿元."""
    pat = re.compile(rf'{kw}\s*(?:\[\d+\])?\s*([\d,\.]+)\s*亿')
    m = pat.search(text)
    if m:
        try:
            return float(m.group(1).replace(',', ''))
        except ValueError:
            pass
    return None


def _extract_gdp_percapita(text: str) -> float | None:
    """5 增量 — gdp_percapita. Pattern: 人均地区生产总值 X 元."""
    pats = [
        # "人均地区生产总值为18.4万元" — 北京 style (万元 unit)
        re.compile(
            r'人均(?:地区)?生产总值(?:为|达到|为达|是)?\s*'
            r'(?:\[[^\[\]]*(?:\[[^\]]*\][^\[\]]*)*\])?\s*'
            r'([\d,\.]+)\s*万元'
        ),
        # "人均地区生产总值 70321 元（折合 10900 美元）" — with parenthesis
        re.compile(
            r'人均(?:地区)?生产总值(?:为|达到|是)?\s*'
            r'(?:\[[^\[\]]*(?:\[[^\]]*\][^\[\]]*)*\])?\s*'
            r'([\d,\.]+)\s*元\s*[\(（]'
        ),
        # "人均生产总值X元" — Hebei style (no 地区)
        re.compile(
            r'人均生产总值(?:为|达到|是)?\s*'
            r'([\d,\.]+)\s*元'
        ),
        # "人均地区生产总值65026元" — standard
        re.compile(
            r'人均(?:地区)?生产总值(?:为|达到|是)?\s*'
            r'(?:\[[^\[\]]*(?:\[[^\]]*\][^\[\]]*)*\])?\s*'
            r'([\d,\.]+)\s*元'
        ),
    ]
    for i, pat in enumerate(pats):
        m = pat.search(text)
        if m:
            try:
                v = float(m.group(1).replace(',', ''))
                # 万元 → 元 conversion
                if i == 0:
                    v = v * 10000
                return v
            except ValueError:
                pass
    return None


def _extract_fiscal_rev(text: str) -> float | None:
    """5 增量 — fiscal_rev. Pattern: 一般公共预算收入 X 亿元 (often 同 X.X%)."""
    # Try "地方一般公共预算收入 X 亿元" first (more specific)
    pats = [
        re.compile(r'地方一般公共预算收入\s*([\d,\.]+)\s*亿元'),
        re.compile(r'(?:全省|全市|全区)?一般公共预算收入\s*([\d,\.]+)\s*亿元'),
        re.compile(r'(?:全省|全市|全区)?一般公共预算(?:收入|总收入)\s*[\d,\.]+(?:、)?\s*其中[\s\S]{0,30}?([\d,\.]+)\s*亿元'),
    ]
    for pat in pats:
        m = pat.search(text)
        if m:
            try:
                return float(m.group(1).replace(',', ''))
            except ValueError:
                pass
    return None


def _extract_fixed_asset(text: str) -> float | None:
    """5 增量 — fixed_asset. Pattern: 固定资产投资 X 亿元 (含 X% etc.)."""
    pats = [
        re.compile(r'(?:全省|全市|全区)?(?:完成|实现)?固定资产投资(?:\s*\(?含[^)]*\)?)?\s*\(?[^)]*?\)?\s*([\d,\.]+)\s*亿元'),
        re.compile(r'(?:全省|全市|全区)?(?:完成|实现)?固定资产投资\s*[\d,\.]+(?:、\s*)?(?:增长|同比(?:增长|下降))\s*[\d.]+%\s*[,，]?\s*为\s*([\d,\.]+)\s*亿元'),
        re.compile(r'(?:全省|全市|全区)?固定资产投资(?:\s*\([^)]*\))?\s*(?:为|达到|完成)\s*([\d,\.]+)\s*亿元'),
    ]
    for pat in pats:
        m = pat.search(text)
        if m:
            try:
                return float(m.group(1).replace(',', ''))
            except ValueError:
                pass
    return None


def _extract_retail(text: str) -> float | None:
    """5 增量 — retail. Pattern: 社会消费品零售总额 X 亿元."""
    pats = [
        re.compile(r'(?:全省|全市|全区)?社会消费品零售总额\s*([\d,\.]+)\s*亿元'),
        re.compile(r'社会消费品零售总额\s*达(?:到)?\s*([\d,\.]+)\s*亿元'),
    ]
    for pat in pats:
        m = pat.search(text)
        if m:
            try:
                return float(m.group(1).replace(',', ''))
            except ValueError:
                pass
    return None


def _extract_trade(text: str) -> float | None:
    """5 增量 — trade. Pattern: 进出口总额/总值 X 亿元 (or 万美元)."""
    pats = [
        # 亿元 (most common)
        re.compile(r'(?:全省|全市|全区)?进出口(?:总额|总值)\s*([\d,\.]+)\s*亿元'),
        re.compile(r'进出口(?:总额|总值)\s*达(?:到)?\s*([\d,\.]+)\s*亿元'),
        # 万美元 (Shandong/Guangdong style)
        re.compile(r'(?:全省|全市|全区)?进出口(?:总额|总值)\s*([\d,\.]+)\s*万美元'),
    ]
    for i, pat in enumerate(pats):
        m = pat.search(text)
        if m:
            try:
                v = float(m.group(1).replace(',', ''))
                # 万美元 → convert to 亿元 (1 亿美元 = 7.2 亿元 approx)
                if i == 2:
                    v = v * 7.2 / 10000  # 万美元 to 亿元
                return v
            except ValueError:
                pass
    return None


def _extract_all(text: str) -> dict:
    """Extract all 10 indicators from text."""
    r = {}
    g = _extract_gdp_total(text)
    if g is not None:
        r['gdp_total'] = g
    g = _extract_gdp_growth(text)
    if g is not None:
        r['gdp_growth'] = g
    for kw, key in (
        ('第一产业增加值', 'primary_gdp'),
        ('第二产业增加值', 'secondary_gdp'),
        ('第三产业增加值', 'tertiary_gdp'),
    ):
        v = _extract_industry(text, kw)
        if v is not None:
            r[key] = v
    for key, fn in (
        ('gdp_percapita', _extract_gdp_percapita),
        ('fiscal_rev', _extract_fiscal_rev),
        ('fixed_asset', _extract_fixed_asset),
        ('retail', _extract_retail),
        ('trade', _extract_trade),
    ):
        v = fn(text)
        if v is not None:
            r[key] = v
    return r


def main() -> int:
    out_records = []
    parse_failures = []

    for prov_en, prov_code in TO_FETCH_2021:
        cache_path = CACHE_DIR / f'_665_y2021_{prov_en}.html'
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
        'total_provinces': len(TO_FETCH_2021),
        'parsed_count': sum(1 for r in out_records if r['verdict'] == 'PARSED'),
        'parse_empty_count': sum(1 for r in out_records if r['verdict'] == 'PARSE_EMPTY'),
        'cache_miss_count': sum(1 for r in out_records if r['verdict'] == 'CACHE_MISS'),
        'by_indicator': {},
    }
    for ind in INDICATOR_LABELS:
        summary['by_indicator'][ind] = sum(
            1 for r in out_records if ind in r['extracted']
        )

    out = {
        'knife': '665',
        'sub_knife': '665a',
        'chain_id': 'parse_665a_m2_u10_batch_v1_y2021',
        'year': 2021,
        'summary': summary,
        'parse_failures': parse_failures,
        'cells': out_records,
        'methodology': 'v1 10 指标 parse: 5 现 (gdp_total/gdp_growth/primary/secondary/tertiary) '
                       'mirror 658 _extract pattern + 5 增量 (gdp_percapita/fiscal_rev/'
                       'fixed_asset/retail/trade) regex with section-anchored; missing '
                       'values stay None → DATA_MISSING (新增红线-1 沿用, 禁补零).',
    }

    out_path = Path(
        '/Users/kjonekong/projects/china platform/evidence_pack/'
        'u6_batch_y2021_parse_20260904.json'
    )
    out_path.parent.mkdir(exist_ok=True)
    out_path.write_text(json.dumps(out, ensure_ascii=False, indent=2), encoding='utf-8')
    print(f'wrote {out_path}')
    print(f'Parsed: {summary["parsed_count"]}/{summary["total_provinces"]}')
    print(f'Empty: {summary["parse_empty_count"]}')
    print('Per-indicator coverage:')
    for ind, n in summary['by_indicator'].items():
        print(f'  {ind}: {n}/{summary["total_provinces"]}')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())