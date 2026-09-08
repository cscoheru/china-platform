#!/usr/bin/env python3
"""
669b-2020 fetch — 23 省会 city × 2020 hongheiku bulletins (≤23 HTTP)
=====================================================================

knife 669b-2020 范围: 23 省会 city (除 JILIN/TAIWAN) × 2020 × 10 指标 = 230 cells
JILIN_CHANGCHUN / TAIWAN_TAIPEI = DATA_MISSING (tag 页无 2020 公告)

URL pattern: https://tjgb.hongheiku.com/sjtjgb/{numeric_id}.html
HTTP: 23 (each bulletin = 1 HTTP)
Output: /tmp/669b/2020_{CITY_CODE}.html (23 files)

Critical: per docs/05 §8.3 + 新增红线-3: 禁手填, 禁爬第三方, 禁补零
"""

import urllib.request
import urllib.error
import time
from pathlib import Path

CITIES_2020 = [
    ("HEBEI_SHIJIAZHUANG",     1816),
    ("SHANXI_TAIYUAN",         1260),
    ("NEIMENGGU_HUHEHAOTE",    75),
    ("LIAONING_SHENYANG",      347),
    ("HEILONGJIANG_HARBIN",    9267),
    ("ANHUI_HEFEI",            719),
    ("FUJIAN_FUZHOU",          3413),
    ("JIANGXI_NANCHANG",       630),
    ("SHANDONG_JINAN",         7978),
    ("HENAN_ZHENGZHOU",        1804),
    ("HUBEI_WUHAN",            4553),
    ("HUNAN_CHANGSHA",         327),
    ("GUANGXI_NANNING",        7734),
    ("HAINAN_HAIKOU",          1226),
    ("SICHUAN_CHENGDU",        1460),
    ("GUIZHOU_GUIYANG",        3174),
    ("YUNNAN_KUNMING",         14086),
    ("XIZANG_LASA",            14174),
    ("SHAANXI_XIAN",           1229),
    ("GANSU_LANZHOU",          949),
    ("QINGHAI_XINING",         11065),
    ("NINGXIA_YINCHUAN",       7796),
    ("XINJIANG_WULUMUQI",      428),
]

URL_TEMPLATE = "https://tjgb.hongheiku.com/djs/{nid}.html"
OUT_DIR = Path("/tmp/669b")
HTTP_OK = 0
HTTP_FAIL = 0


def main():
    global HTTP_OK, HTTP_FAIL
    print(f"=== knife 669b-2020 fetch (23 city × 2020 bulletins, ≤23 HTTP) ===")
    print(f"Output: {OUT_DIR}/2020_{{CITY}}.html")
    print()

    for city_code, nid in CITIES_2020:
        url = URL_TEMPLATE.format(nid=nid)
        out_file = OUT_DIR / f"2020_{city_code}.html"
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
            with urllib.request.urlopen(req, timeout=30) as resp:
                body = resp.read()
                # try gbk then utf-8
                try:
                    text = body.decode("gbk")
                except UnicodeDecodeError:
                    text = body.decode("utf-8", errors="replace")
                out_file.write_text(text, encoding="utf-8")
                HTTP_OK += 1
                print(f"  ✓ {city_code:32s} id={nid:6d} {len(body)} bytes")
        except (urllib.error.URLError, urllib.error.HTTPError, TimeoutError) as e:
            HTTP_FAIL += 1
            print(f"  ✗ {city_code:32s} id={nid:6d} {type(e).__name__}: {e}")
        time.sleep(0.3)  # rate limit

    print()
    print(f"=== fetch summary: {HTTP_OK} ok, {HTTP_FAIL} fail, {HTTP_OK + HTTP_FAIL}/23 total HTTP ===")


if __name__ == "__main__":
    main()
