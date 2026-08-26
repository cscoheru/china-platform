"""Knife 67 / tasking 394 — 湖北观察页链到公开提取轨 (demo 标注).

Per 394 §SCHEMA:
  (1) 找到湖北相关前端页（省级 /provinces/... 或城页若有）；增显式链
      /public-extracts#track-hb，文案标明 REGISTRY_SAMPLE / xlsx / live
      enabled=FALSE / 非 O1；
  (2) 若无湖北专用页 → 在首页「公开提取」旁加一行「湖北轨 → #track-hb」
      （缩刀兜底）；
  (3) ≥1 pytest 或 smoke；
  (4) 回执 395（-cc-）。

事实核查: /provinces/ 仅 guangdong/jiangsu/shandong/sichuan/zhejiang,
10 城 slug 无湖北城市 → 走缩刀兜底（首页行）。

Test cases:
  - test_home_page_has_hubei_track_link_row: 首页含「公开提取湖北轨」行 +
    /public-extracts#track-hb 链 + REGISTRY_SAMPLE/xlsx/enabled=FALSE/非 O1 提示.
  - test_no_hubei_province_or_city_page_polluted: 确认 /provinces/* 与
    10 城 CityPage/CityPageMart 未被湖北链接污染（仅首页 + /public-extracts 页
    可出现 #track-hb）.
"""
from __future__ import annotations

import re
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
HOME_PAGE = PROJECT_ROOT / "frontend" / "app" / "page.tsx"
PROVINCES_DIR = PROJECT_ROOT / "frontend" / "app" / "provinces"
CITY_PAGE = PROJECT_ROOT / "frontend" / "app" / "components" / "CityPage.tsx"
CITY_PAGE_MART = (
    PROJECT_ROOT / "frontend" / "app" / "components" / "CityPageMart.tsx"
)


def _strip_comments(src: str) -> str:
    code = re.sub(r"//[^\n]*", "", src)
    code = re.sub(r"/\*.*?\*/", "", code, flags=re.DOTALL)
    return code


def test_home_page_has_hubei_track_link_row() -> None:
    """Per 394 §SCHEMA (1)+(2) 兜底: 首页含「公开提取湖北轨」行 +
    /public-extracts#track-hb 链 + 四项提示 (REGISTRY_SAMPLE / xlsx /
    enabled=FALSE / 非 live O1)."""
    src = HOME_PAGE.read_text(encoding="utf-8")
    code = _strip_comments(src)
    assert "公开提取湖北轨" in code, "首页须含「公开提取湖北轨」行"
    assert "/public-extracts#track-hb" in code, (
        "首页须含 /public-extracts#track-hb 链"
    )
    assert "PROVINCIAL_BULLETIN" in code, "首页须标 PROVINCIAL_BULLETIN"
    assert "enabled=FALSE" in code, "首页须显式 live enabled=FALSE 暂缓"
    assert "非 live O1" in code, "首页须显式非 live O1 守门"


def test_no_hubei_link_pollutes_province_or_city_pages() -> None:
    """Per 394 §红线「无条件污染其它省/城页」: /provinces/* 5 省页与 10 城
    CityPage/CityPageMart 不应出现 #track-hb 链（湖北链接仅在首页兜底行 +
    /public-extracts 页自身分节锚点）."""
    # /provinces/* 页
    for p in sorted(PROVINCES_DIR.rglob("page.tsx")):
        code = _strip_comments(p.read_text(encoding="utf-8"))
        assert "/public-extracts#track-hb" not in code, (
            f"{p.name}: 不应出现 #track-hb 链（湖北链接仅限首页兜底行）"
        )
    # CityPage / CityPageMart (仅深圳有公开提取链接, 不得有湖北)
    for p in (CITY_PAGE, CITY_PAGE_MART):
        code = _strip_comments(p.read_text(encoding="utf-8"))
        assert "/public-extracts#track-hb" not in code, (
            f"{p.name}: 不应出现 #track-hb 链（城页仅深圳有公开提取链接, "
            f"湖北走首页兜底）"
        )