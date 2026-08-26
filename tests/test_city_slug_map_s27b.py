#!/usr/bin/env python3
"""Stage 2 / S2.7-b-lite — 10 地市 slug 守门测试。

Per docs/46 §3.1 (slug 约定) + §3.2 (路由) + `256` §NOW-2 "最小 pytest
（路由/slug 守门）":
  - 10 城 slug 唯一性
  - slug 字符集 `[a-z0-9-]+`
  - 10 城锁定清单（per Cursor 裁定，不得擅自增减）
  - 与省份 slug 不冲突（province 已用 jiangsu/zhejiang/guangdong 等）

红线 (per docs/46 §1.2 + `256` §红线):
  - 不擅自增减 10 城名单
  - 不宣布 Gate 2 PASS
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
TS_SRC = ROOT / "frontend" / "lib" / "city_slug_map.ts"

# Cursor 锁定的 10 城清单（per `256` §SCHEMA "10 城 slug"）
LOCKED_SLUGS = [
    "nanjing",
    "suzhou",
    "wuxi",
    "nantong",
    "hangzhou",
    "ningbo",
    "wenzhou",
    "guangzhou",
    "shenzhen",
    "dongguan",
]

# 省份 slug 已占用（per S2.7-a）
PROVINCE_SLUGS = {"jiangsu", "zhejiang", "guangdong", "sichuan", "shandong"}


def _parse_slugs_from_ts(src: str) -> list[str]:
    """从 city_slug_map.ts 中抽取 slug 字符串集合。

    仅匹配 `slug: "<value>"` 字面量；不引入运行时依赖。
    """
    return re.findall(r'slug:\s*"([^"]+)"', src)


def test_slug_unique() -> None:
    """10 城 slug 唯一性（per docs/46 §3.1）"""
    src = TS_SRC.read_text(encoding="utf-8")
    slugs = _parse_slugs_from_ts(src)
    assert len(slugs) == 10, f"expected 10 slugs; got {len(slugs)}: {slugs}"
    assert len(set(slugs)) == len(slugs), f"duplicate slugs: {slugs}"
    print(f"OK: 10 unique slugs = {sorted(slugs)}")


def test_slug_charset() -> None:
    """slug 字符集守门 `[a-z0-9-]+`（per docs/46 §3.1）"""
    src = TS_SRC.read_text(encoding="utf-8")
    slugs = _parse_slugs_from_ts(src)
    bad = [s for s in slugs if not re.match(r"^[a-z0-9-]+$", s)]
    assert not bad, f"slugs with bad charset: {bad}"
    print(f"OK: all {len(slugs)} slugs match [a-z0-9-]+")


def test_locked_list_match() -> None:
    """锁定清单必须命中 `256` §SCHEMA（per Cursor 裁定；不得擅自增减）"""
    src = TS_SRC.read_text(encoding="utf-8")
    slugs = sorted(_parse_slugs_from_ts(src))
    expected = sorted(LOCKED_SLUGS)
    assert slugs == expected, (
        f"slug set mismatch:\n  got      = {slugs}\n  expected = {expected}\n"
        "（per `256` §SCHEMA; 10 城名单 Cursor 锁定，不擅自增减）"
    )
    print(f"OK: slug set == locked list ({len(slugs)} slugs)")


def test_no_province_slug_conflict() -> None:
    """城市 slug 不与省份 slug 冲突（per docs/46 §3.1）"""
    src = TS_SRC.read_text(encoding="utf-8")
    slugs = set(_parse_slugs_from_ts(src))
    conflict = slugs & PROVINCE_SLUGS
    assert not conflict, f"city slug conflicts with province slug: {conflict}"
    print(f"OK: no city/province slug conflict")


def test_city_slug_list_order_and_length() -> None:
    """CITY_SLUG_LIST 顺序固定 + 长度 = 10（per Cursor 裁定）"""
    src = TS_SRC.read_text(encoding="utf-8")
    m = re.search(r"export const CITY_SLUG_LIST:\s*readonly string\[\]\s*=\s*\[([^\]]+)\]", src)
    assert m, "CITY_SLUG_LIST not found in city_slug_map.ts"
    items = [s.strip().strip('"') for s in m.group(1).split(",") if s.strip()]
    assert len(items) == 10, f"CITY_SLUG_LIST length {len(items)} != 10"
    assert items == LOCKED_SLUGS, (
        f"CITY_SLUG_LIST order mismatch:\n  got      = {items}\n  expected = {LOCKED_SLUGS}"
    )
    print(f"OK: CITY_SLUG_LIST ordered = {items}")


def test_meta_present() -> None:
    """meta 守门：本测试文件自身可达且 docstring 关键字段命中"""
    src = Path(__file__).read_text(encoding="utf-8")
    for needle in ("docs/46 §3.1", "`256`", "10 城", "slug 守门"):
        assert needle in src, f"missing {needle!r} in test docstring"
    print("OK: meta keys present in test docstring")


if __name__ == "__main__":
    failures: list[str] = []
    for fn in (
        test_slug_unique,
        test_slug_charset,
        test_locked_list_match,
        test_no_province_slug_conflict,
        test_city_slug_list_order_and_length,
        test_meta_present,
    ):
        try:
            fn()
        except AssertionError as e:
            print(f"❌ {fn.__name__}: {e}", file=sys.stderr)
            failures.append(fn.__name__)
    if failures:
        print(f"\n=== {len(failures)} FAIL ===", file=sys.stderr)
        sys.exit(1)
    print("\n=== test_city_slug_map_s27b.py: PASS ===")
    sys.exit(0)