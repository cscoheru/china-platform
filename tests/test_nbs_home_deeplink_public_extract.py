"""Knife 76 / tasking 420 — 首页 NBS sample 轨显式 deeplink.

Per 420 §SCHEMA "本刀做":
  (1) 首页 `frontend/app/page.tsx` 公开提取表: 为 NBS sample 轨加显式链
      `/public-extracts#track-nbs-sample`（镜像湖北 `#track-hb` 行；文案标明
      REGISTRY_SAMPLE / demo / 非 O1；可改现有「四轨 demo」行 href 或新增
      一行）；
  (2) ≥1 smoke 或 pytest 针；
  (3) 不改 fixture 字节；
  (4) 回执 420（-cc-）。

本文件对 (1)+(2) 落 pytest 守门：home 页含 /public-extracts#track-nbs-sample
显式链 + testId + REGISTRY_SAMPLE/demo/非 O1 标注；不污染其它省/城页；
不动 4 fixture SHA。

Test cases:
  - test_home_page_has_nbs_sample_deeplink: 首页含 NBS sample 行 +
    /public-extracts#track-nbs-sample 链 + testId + REGISTRY_SAMPLE/demo/非 O1.
  - test_no_nbs_deeplink_pollutes_province_or_city_pages: /provinces/* 5 省页
    与 10 城 CityPage/CityPageMart 不应出现 #track-nbs-sample 链（NBS 显式
    deeplink 仅在首页兜底行 + /public-extracts 页自身分节锚点）.
  - test_no_fixture_byte_modified: 4 fixture 文件 SHA 锁定未变（per 420
    §红线「不改 4 fixture SHA」）.
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
# (registry/WORM archive SHA 与 fixture byte SHA 不同; 此处锁定 byte SHA.)
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


def test_home_page_has_nbs_sample_deeplink() -> None:
    """Per 420 §SCHEMA (1): 首页含 NBS sample 轨 deeplink 行 +
    /public-extracts#track-nbs-sample 链 + testId +
    REGISTRY_SAMPLE/demo/非 O1 标注."""
    src = HOME_PAGE.read_text(encoding="utf-8")
    code = _strip_comments(src)
    assert "公开提取 NBS sample 轨" in code, (
        "首页须含「公开提取 NBS sample 轨」行（镜像湖北「公开提取湖北轨」）"
    )
    assert "/public-extracts#track-nbs-sample" in code, (
        "首页须含 /public-extracts#track-nbs-sample 显式 deeplink 链"
    )
    assert 'data-testid="home-public-extracts-nbs-sample"' in code, (
        "首页须含 data-testid='home-public-extracts-nbs-sample'"
    )
    assert "REGISTRY_SAMPLE" in code, "首页须标 REGISTRY_SAMPLE 轨类型"
    assert "非 live O1" in code, "首页须显式非 live O1 守门"


def test_no_nbs_deeplink_pollutes_province_or_city_pages() -> None:
    """Per 420 §红线: /provinces/* 5 省页与 10 城 CityPage/CityPageMart 不应
    出现 #track-nbs-sample 链（NBS 显式 deeplink 仅在首页兜底行 +
    /public-extracts 页自身分节锚点）."""
    for p in sorted(PROVINCES_DIR.rglob("page.tsx")):
        code = _strip_comments(p.read_text(encoding="utf-8"))
        assert "/public-extracts#track-nbs-sample" not in code, (
            f"{p.name}: 不应出现 #track-nbs-sample 链"
            f"（NBS deeplink 仅限首页兜底行 + /public-extracts 页自身锚点）"
        )
    for p in (CITY_PAGE, CITY_PAGE_MART):
        code = _strip_comments(p.read_text(encoding="utf-8"))
        assert "/public-extracts#track-nbs-sample" not in code, (
            f"{p.name}: 不应出现 #track-nbs-sample 链"
            f"（城页不应出现 NBS 显式 deeplink）"
        )


def test_no_fixture_byte_modified() -> None:
    """Per 420 §红线「不改 4 fixture SHA」: 4 fixture 文件 SHA 前 8 字符
    锁定未变（仅校验存在 + 前缀对账; 不写死全 SHA）."""
    for path in FIXTURES:
        assert path.is_file(), f"fixture 缺失: {path}"
        sha = _sha256_of(path)
        prefix = EXPECTED_FIXTURE_SHA_PREFIX[path.name]
        assert sha.startswith(prefix), (
            f"{path.name} SHA 前缀漂移: got {sha[:8]}, "
            f"expected prefix {prefix}"
        )