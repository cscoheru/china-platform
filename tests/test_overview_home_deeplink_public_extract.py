"""Knife 82 / tasking 432 — 首页四轨一览 overview 显式 deeplink.

Per 432 §SCHEMA "本刀做":
  (1) 首页 `frontend/app/page.tsx` 公开提取表: 新增一行「公开提取四轨一览
      (overview strip)」 → `/public-extracts#overview`（镜像 NBS sample
      `#track-nbs-sample` 行 + NBS live `#track-nbs-live` 行 + 湖北 `#track-hb`
      行; 文案标明 OVERVIEW / 四轨 demo / 非 O1; 含 data-testid 供 pytest 守门）;
  (2) ≥1 smoke 或 pytest 针 (smoke §12b''' 4 针 + 本文件 3 pytest cases);
  (3) 不改 fixture 字节;
  (4) 回执 432（-cc-）。

本文件对 (1)+(2) 落 pytest 守门: home 页含 /public-extracts#overview 显式链
+ testId + OVERVIEW / 四轨 demo / 非 O1 标注; 不污染其它省/城页; 不动 4 fixture
SHA。

Test cases:
  - test_home_page_has_overview_deeplink: 首页含「公开提取四轨一览（overview
    strip）」行 + /public-extracts#overview 链 + testId + OVERVIEW/四轨 demo/
    非 O1 标注.
  - test_no_overview_deeplink_pollutes_province_or_city_pages: /provinces/* 5 省
    页与 10 城 CityPage/CityPageMart 不应出现 #overview 链（overview 显式
    deeplink 仅在首页兜底行 + /public-extracts 页自身 overview strip 锚点）.
  - test_no_fixture_byte_modified: 4 fixture 文件 SHA 锁定未变
    （per 432 §红线「不改 4 fixture SHA」）.
"""
from __future__ import annotations

import hashlib
import re
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
HOME_PAGE = PROJECT_ROOT / "frontend" / "app" / "page.tsx"
PROVINCES_DIR = PROJECT_ROOT / "frontend" / "app" / "provinces"
CITY_PAGE = PROJECT_ROOT / "frontend" / "app" / "components" / "CityPage.tsx"
CITY_PAGE_MART = (
    PROJECT_ROOT / "frontend" / "app" / "components" / "CityPageMart.tsx"
)

FIXTURES = [
    PROJECT_ROOT / "frontend" / "lib" / "public_extract_nbs.json",
    PROJECT_ROOT / "frontend" / "lib" / "public_extract_nbs_live_candidate.json",
    PROJECT_ROOT / "frontend" / "lib" / "public_extract_sz.json",
    PROJECT_ROOT / "frontend" / "lib" / "public_extract_hubei.json",
]

# 4 fixture SHA 前 8 字符锁: 字节级锁定, 本刀不修改 fixture.
# 共享 knife 76 / knife 78 / knife 80 / knife 81 锁值, 因 fixture 字节保持不变.
EXPECTED_FIXTURE_SHA_PREFIX = {
    "public_extract_nbs.json": "e30ee811",
    "public_extract_nbs_live_candidate.json": "9232efdb",
    "public_extract_sz.json": "937255a5",
    "public_extract_hubei.json": "9056001c",
}


def _strip_comments(src: str) -> str:
    code = re.sub(r"//[^\n]*", "", src)
    code = re.sub(r"/\*.*?\*/", "", code, flags=re.DOTALL)
    return code


def _sha256_of(path: Path) -> str:
    h = hashlib.sha256()
    h.update(path.read_bytes())
    return h.hexdigest()


def test_home_page_has_overview_deeplink() -> None:
    """Per 432 §SCHEMA (1): 首页含四轨一览 overview 显式 deeplink 行 +
    /public-extracts#overview 链 + testId + OVERVIEW/四轨 demo/非 O1 标注."""
    src = HOME_PAGE.read_text(encoding="utf-8")
    code = _strip_comments(src)
    assert "公开提取四轨一览" in code, (
        "首页须含「公开提取四轨一览」行（镜像 NBS sample / NBS live / 湖北行）"
    )
    assert "/public-extracts#overview" in code, (
        "首页须含 /public-extracts#overview 显式 deeplink 链"
    )
    assert 'data-testid="home-public-extracts-overview"' in code, (
        "首页须含 data-testid='home-public-extracts-overview'"
    )
    assert "OVERVIEW" in code, "首页须标 OVERVIEW 轨类型"
    assert "四轨 demo" in code, "首页须显式四轨 demo 守门"
    assert "非 O1" in code, "首页须显式非 O1 守门"


def test_no_overview_deeplink_pollutes_province_or_city_pages() -> None:
    """Per 432 §红线: /provinces/* 5 省页与 10 城 CityPage/CityPageMart
    不应出现 #overview 链（overview 显式 deeplink 仅在首页兜底行 +
    /public-extracts 页自身 overview strip 锚点）."""
    for p in sorted(PROVINCES_DIR.rglob("page.tsx")):
        code = _strip_comments(p.read_text(encoding="utf-8"))
        assert "/public-extracts#overview" not in code, (
            f"{p.name}: 不应出现 #overview 链"
            f"（overview deeplink 仅限首页兜底行 + /public-extracts 页自身锚点）"
        )
    for p in (CITY_PAGE, CITY_PAGE_MART):
        code = _strip_comments(p.read_text(encoding="utf-8"))
        assert "/public-extracts#overview" not in code, (
            f"{p.name}: 不应出现 #overview 链"
            f"（城页不应出现 overview 显式 deeplink）"
        )


def test_no_fixture_byte_modified() -> None:
    """Per 432 §红线「不改 4 fixture SHA」: 4 fixture 文件 SHA 前 8 字符
    锁定未变（仅校验存在 + 前缀对账; 不写死全 SHA）."""
    for path in FIXTURES:
        assert path.is_file(), f"fixture 缺失: {path}"
        sha = _sha256_of(path)
        prefix = EXPECTED_FIXTURE_SHA_PREFIX[path.name]
        assert sha.startswith(prefix), (
            f"{path.name} SHA 前缀漂移: got {sha[:8]}, "
            f"expected prefix {prefix}"
        )