"""Knife 66 / tasking 391 — 深圳城页链到 /public-extracts#track-sz (demo 标注).

Per 391 §SCHEMA:
  (1) frontend/app/cities/ 深圳相关页 (CityPage / CityPageMart) 增显式链接
      /public-extracts#track-sz (文案标明 REGISTRY_SAMPLE demo, 非 O1);
  (2) ≥1 pytest 或 smoke 针;
  (3) 红线: 链接必须带 demo/REGISTRY_SAMPLE 提示.

Test cases:
  - test_city_page_has_shenzhen_public_extract_link:
    CityPage.tsx 含 slug==='shenzhen' 条件 + /public-extracts#track-sz 链 +
    REGISTRY_SAMPLE demo 标注 + 非 O1 守门.
  - test_city_page_mart_has_shenzhen_public_extract_link:
    CityPageMart.tsx 含 cityId==='shenzhen' 条件 + /public-extracts#track-sz 链
    + REGISTRY_SAMPLE demo 标注 + 非 O1 守门.
  - test_other_cities_do_not_render_link:
    其他城市 slug 不应触发深圳公开提取链接（条件分支仅 shenzhen 命中）.
"""
from __future__ import annotations

import re
from pathlib import Path

import pytest

PROJECT_ROOT = Path(__file__).resolve().parent.parent
CITY_PAGE = PROJECT_ROOT / "frontend" / "app" / "components" / "CityPage.tsx"
CITY_PAGE_MART = (
    PROJECT_ROOT / "frontend" / "app" / "components" / "CityPageMart.tsx"
)


def _strip_comments(src: str) -> str:
    code = re.sub(r"//[^\n]*", "", src)
    code = re.sub(r"/\*.*?\*/", "", code, flags=re.DOTALL)
    return code


def test_city_page_has_shenzhen_public_extract_link() -> None:
    """Per 391 §SCHEMA (1) + §红线: CityPage.tsx 含 shenzhen 条件分支 +
    /public-extracts#track-sz 链 + REGISTRY_SAMPLE demo 标注 + 非 O1 守门."""
    src = CITY_PAGE.read_text(encoding="utf-8")
    code = _strip_comments(src)
    assert 'city.slug === "shenzhen"' in code, (
        "CityPage.tsx 必须含 slug==='shenzhen' 条件分支"
    )
    assert "/public-extracts#track-sz" in code, (
        "CityPage.tsx 必须含 /public-extracts#track-sz 链"
    )
    assert "REGISTRY_SAMPLE" in code, "链旁必须标 REGISTRY_SAMPLE demo"
    assert "非 O1" in code or "非 O1 收口" in code, "必须显式非 O1 守门"


def test_city_page_mart_has_shenzhen_public_extract_link() -> None:
    """Per 391 §SCHEMA (1) + §红线: CityPageMart.tsx 含 shenzhen 条件 +
    /public-extracts#track-sz 链 + REGISTRY_SAMPLE demo 标注 + 非 O1 守门."""
    src = CITY_PAGE_MART.read_text(encoding="utf-8")
    code = _strip_comments(src)
    assert 'mart.cityId === "shenzhen"' in code, (
        "CityPageMart.tsx 必须含 cityId==='shenzhen' 条件分支"
    )
    assert "/public-extracts#track-sz" in code, (
        "CityPageMart.tsx 必须含 /public-extracts#track-sz 链"
    )
    assert "REGISTRY_SAMPLE" in code, "链旁必须标 REGISTRY_SAMPLE demo"
    assert "非 O1" in code or "非 O1 收口" in code, "必须显式非 O1 守门"


def test_other_cities_do_not_render_link_unconditionally() -> None:
    """红线条目化: 链接必须条件化 (shenzhen slug 命中才显示);
    若无条件分支则视为破坏其它城页。

    检测策略: 在文件中找最近的「条件分支」pattern (slug/cityId === "shenzhen" ?)
    出现, 然后 任何 /public-extracts#track-sz 链必须出现在该条件之 '下' (即
    文件偏移更大)."""
    for label, path, cond_pattern in (
        (
            "CityPage",
            CITY_PAGE,
            re.compile(r"slug\s*===\s*[\"']shenzhen[\"']"),
        ),
        (
            "CityPageMart",
            CITY_PAGE_MART,
            re.compile(r"cityId\s*===\s*[\"']shenzhen[\"']"),
        ),
    ):
        src = _strip_comments(path.read_text(encoding="utf-8"))
        cond_iter = list(cond_pattern.finditer(src))
        assert cond_iter, f"{label}: 必须含 shenzhen 条件分支 pattern"
        # 最后一个条件分支出现位置 (即最近的)
        last_cond_end = cond_iter[-1].end()
        # 任何 /public-extracts#track-sz 链必须出现在条件之后 (offset >= last_cond_end)
        for m in re.finditer(r"/public-extracts#track-sz", src):
            assert m.start() >= last_cond_end, (
                f"{label}: /public-extracts#track-sz 链出现位置早于最后一个 "
                f"shenzhen 条件分支, 可能未条件化"
            )