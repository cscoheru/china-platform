#!/usr/bin/env python3
"""
669c-2025 probe — 0 HTTP cache hit verification for 31 city × 2025
=============================================================================

Knife 669c-2025 (独立探针, 与 669b-2025 / 669fix-b-2025 互补):
- 验证 cat_index_2025.html 收录的所有 2025 entry
- 区分 province level (/sjtjgb/, /xjtjgb/xj2020/) vs city level (/djs/)
- 不发起任何 HTTP 请求 (0 HTTP, 0 cache 写入)
- 输出 entry 列表 + 判定

判定:
- 若 cat_index_2025 含 ≥1 /djs/{eid}.html 城市 entry → 后续 knife 可 harvest
- 若仅 /sjtjgb/ province entry → 与 669b-2025 / 669fix-b-2025 一致, hongheiku 暂未收录 city level 2025
"""
import re
import sys
from pathlib import Path
from urllib.parse import unquote

CACHE_DIR = Path("/tmp/669b")
CAT_INDEX_2025 = CACHE_DIR / "_cat_index_2025.html"
SEARCH_CACHE = sorted(CACHE_DIR.glob("_search_*.html"))


def parse_cat_index():
    """Parse cat_index_2025.html — extract all href entries."""
    if not CAT_INDEX_2025.exists():
        print(f"  [WARN] cat index file missing: {CAT_INDEX_2025}")
        return {}
    with open(CAT_INDEX_2025) as f:
        html = f.read()

    # Extract full URLs
    href_pattern = re.compile(r'href="(https?://tjgb\.hongheiku\.com/[^"]+)"')
    urls = href_pattern.findall(html)

    # Categorize by URL pattern
    city_entries = []    # /djs/{eid}.html
    province_entries = []  # /sjtjgb/ or /xjtjgb/xj{year}/
    year_index_entries = []  # /{eid}.html (no category prefix — likely year index)
    national_entries = []   # /category/zgtjgb
    category_entries = []   # /category/{...}
    tag_entries = []        # /tag/{...}

    for url in urls:
        path = url.replace("https://tjgb.hongheiku.com", "")
        if "/djs/" in path:
            city_entries.append(url)
        elif "/sjtjgb/" in path or "/xjtjgb/" in path:
            province_entries.append(url)
        elif re.match(r"^/\d+\.html$", path):
            year_index_entries.append(url)
        elif path.startswith("/category/"):
            category_entries.append(url)
        elif path.startswith("/tag/"):
            tag_entries.append(url)

    # Extract eids
    city_eids = sorted(set(int(re.search(r'/(\d+)\.html', u).group(1)) for u in city_entries))
    province_eids = sorted(set(int(re.search(r'/(\d+)\.html', u).group(1)) for u in province_entries))
    year_index_eids = sorted(set(int(re.search(r'/(\d+)\.html', u).group(1)) for u in year_index_entries))

    return {
        "total_urls": len(urls),
        "unique_urls": len(set(urls)),
        "city_entries": city_entries,
        "province_entries": province_entries,
        "year_index_entries": year_index_entries,
        "category_entries": category_entries,
        "tag_entries": tag_entries,
        "city_eids": city_eids,
        "province_eids": province_eids,
        "year_index_eids": year_index_eids,
    }


def parse_search_cache():
    """Parse each _search_{city}2025.html cache — extract result links."""
    results = {}
    for cache_file in SEARCH_CACHE:
        city_name_raw = cache_file.stem.replace("_search_", "")
        city_name = unquote(city_name_raw)
        with open(cache_file) as f:
            html = f.read()
        # Extract href (full URLs)
        href_pattern = re.compile(r'href="(https?://tjgb\.hongheiku\.com/[^"]+)"')
        urls = href_pattern.findall(html)
        # Look for city-level /djs/ entries
        city_2025 = [u for u in urls if "/djs/" in u]
        # Look for province-level /sjtjgb/ entries
        province_2025 = [u for u in urls if "/sjtjgb/" in u]
        # Look for tag pages with 2025 in URL
        tag_2025 = [u for u in urls if "/tag/" in u and ("2025" in u or "2024" in u)]
        results[city_name] = {
            "file": cache_file.name,
            "total_urls": len(urls),
            "city_djs_count": len(city_2025),
            "province_sjtjgb_count": len(province_2025),
            "tag_2025_count": len(tag_2025),
            "city_djs_sample": city_2025[:3],
            "province_sjtjgb_sample": province_2025[:3],
            "tag_2025_sample": tag_2025[:3],
        }
    return results


def main():
    print(f"=== knife 669c-2025 probe (0 HTTP cache verification) ===")
    print(f"Cache dir: {CACHE_DIR}")
    print(f"Cat index: {CAT_INDEX_2025.name} ({CAT_INDEX_2025.stat().st_size if CAT_INDEX_2025.exists() else 0} bytes)")
    print(f"Search cache files: {len(SEARCH_CACHE)}")
    print()

    print(f"=== cat_index_2025.html parse ===")
    cat = parse_cat_index()
    if cat:
        print(f"  Total URLs: {cat['total_urls']} (unique: {cat['unique_urls']})")
        print()
        print(f"  City level entries (/djs/): {len(cat['city_entries'])} (eids: {cat['city_eids']})")
        print(f"  Province level entries (/sjtjgb/, /xjtjgb/): {len(cat['province_entries'])}")
        for url in cat['province_entries']:
            print(f"    {url}")
        print(f"  Year index entries (/{'{eid}'}.html): {len(cat['year_index_entries'])} (eids: {cat['year_index_eids']})")
        for url in cat['year_index_entries']:
            print(f"    {url}")
        print(f"  Category entries: {len(cat['category_entries'])}")
        for url in cat['category_entries']:
            print(f"    {url}")
        print(f"  Tag entries: {len(cat['tag_entries'])}")
        for url in cat['tag_entries'][:5]:
            print(f"    {url[:100]}{'...' if len(url) > 100 else ''}")
    print()

    print(f"=== search cache parse ({len(SEARCH_CACHE)} files) ===")
    search = parse_search_cache()
    city_level_hit = 0
    province_level_hit = 0
    for city_name, info in search.items():
        city_marker = "✓" if info["city_djs_count"] > 0 else "✗"
        prov_marker = "✓" if info["province_sjtjgb_count"] > 0 else "✗"
        print(f"  {city_name}: {info['total_urls']} URLs total")
        print(f"    {city_marker} /djs/ (city): {info['city_djs_count']}")
        if info["city_djs_count"] > 0:
            city_level_hit += 1
            for s in info["city_djs_sample"]:
                print(f"      sample: {s}")
        print(f"    {prov_marker} /sjtjgb/ (province): {info['province_sjtjgb_count']}")
        if info["province_sjtjgb_count"] > 0:
            province_level_hit += 1
            for s in info["province_sjtjgb_sample"]:
                print(f"      sample: {s}")
        if info["tag_2025_count"] > 0:
            print(f"    tag_2025: {info['tag_2025_count']}")
            for s in info["tag_2025_sample"]:
                print(f"      sample: {s}")
    print()

    print(f"=== 669c-2025 probe verdict ===")
    if cat.get("city_entries"):
        print(f"  [HIT] cat_index_2025 contains {len(cat['city_entries'])} /djs/ entries (city level)")
        print(f"        eids: {cat['city_eids']}")
        print(f"        后续 knife 可 harvest 这些 city level 2025 entry")
    else:
        print(f"  [ZERO-HARVEST] cat_index_2025 has 0 /djs/ entries (city level)")
        print(f"        cat_index_2025 only has {len(cat.get('province_entries', []))} /sjtjgb/ entries (province level)")
        print(f"        与 669b-2025 / 669fix-b-2025 一致, hongheiku 暂未收录 city level 2025")
        print(f"        search cache hit: city_djs {city_level_hit}/{len(SEARCH_CACHE)}, province {province_level_hit}/{len(SEARCH_CACHE)}")

    print()
    print(f"=== Matrix reference ===")
    print(f"  31 city = 4 669a (深/穗/杭/宁) + 25 省会 + 4 直辖市禁 city dim")
    print(f"  29 city × 2025 × 10 indicator = 290 cells (per mart_city_timeseries)")
    print(f"  2025 real cells (current mart): 18 (4 669a cities from prior knife)")
    print(f"  2025 DATA_MISSING: 272 (250 省会 K669fix-b-2025 + 22 4 669a K669a-2025)")


if __name__ == "__main__":
    main()
