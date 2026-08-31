#!/usr/bin/env python3
"""M2-e — Frontend /research/q1-2024-gdp acceptance surface contract.

Per docs/55 §T7 / knife 635 §1.E:
  * page.tsx exists at frontend/app/research/q1-2024-gdp/page.tsx
  * USE_MOCK=false → render real on-disk crosscheck report
    (docs/reports/m2_2024_gdp_crosscheck_20260831.md); NO mock UUID literals.
  * Page header contains the required literal Chinese sentence.
  * Page exposes per-covered-province SHA prefix (8 chars) + source URL.
  * Bottom smoke line shows national value + 5-province sum.
  * frontend/app/page.tsx links to /research/q1-2024-gdp (optional).

Asserts:
  * The page file exists.
  * Required header literal is present.
  * No MOCK_*-UUID strings or lib/mock.ts imports.
  * Renders 6 SHA prefixes (国家 + 5 省级) + 6 source URLs.
  * Renders the crosscheck markdown report (real on-disk artifact).
  * Has the bottom smoke line.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent
FRONTEND = REPO_ROOT / "frontend"
PAGE = FRONTEND / "app" / "research" / "q1-2024-gdp" / "page.tsx"

REQUIRED_HEADER = (
    "M2-e 验收面 · 2024 年全年 GDP（5/31 + 1 全国）· "
    "弱核对 QUARANTINED-WEAK · 非 Gate/O1/M2 PASS"
)
FORBIDDEN_MOCK_UUIDS = [
    "JIANGSU-GDP-INDICATOR-UUID-MOCK",
    "JIANGSU-GEO-UUID-MOCK",
]

# 6 SHA prefixes (knife 633 §PHOTO-2) the page must surface
REQUIRED_SHA_PREFIXES = [
    "3e732426d3cbdb84",  # 国家
    "80aa92406e9846c3",  # 上海
    "073a544f16a1f521",  # 北京
    "915c1b4537b3620c",  # 四川
    "6ffaaffb3a0e9bd4",  # 山东
    "3022e7cacdd44dce",  # 湖北
]

# 6 source domains (real .gov.cn URLs, not homepages)
REQUIRED_SOURCE_DOMAINS = [
    "stats.gov.cn",
    "tjj.sh.gov.cn",
    "tjj.beijing.gov.cn",
    "tjj.sc.gov.cn",
    "tjj.shandong.gov.cn",
    "tjj.hubei.gov.cn",
]


def _collapse(src: str) -> str:
    """Collapse JSX whitespace so multi-line JSX text becomes single string."""
    return re.sub(r"\s+", " ", src)


def _strip_comments(src: str) -> str:
    """Strip JS line + block comments so scans hit only executable code."""
    src = re.sub(r"//[^\n]*", "", src)
    src = re.sub(r"/\*.*?\*/", "", src, flags=re.DOTALL)
    return src


# ---------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------


def test_page_file_exists() -> None:
    """Per knife 635 §1.E: page.tsx at /research/q1-2024-gdp/ must exist."""
    assert PAGE.is_file(), f"missing {PAGE}"


def test_required_header_present() -> None:
    """The exact literal header must be on the page (knife 635 §PHOTO 字面量).

    JSX collapses whitespace, so multi-line text becomes a single string;
    we collapse whitespace before searching.
    """
    src = _collapse(PAGE.read_text(encoding="utf-8"))
    assert REQUIRED_HEADER in src, (
        f"q1-2024-gdp page missing required header literal:\n"
        f"  expected={REQUIRED_HEADER!r}\n  source_head={src[:300]!r}"
    )


def test_no_mock_uuids() -> None:
    """The page must NOT hardcode any MOCK_*_UUID (knife 635 §1.E 红线)."""
    src = _strip_comments(PAGE.read_text(encoding="utf-8"))
    for bad in FORBIDDEN_MOCK_UUIDS:
        assert bad not in src, (
            f"q1-2024-gdp page contains forbidden mock UUID: {bad}"
        )


def test_does_not_import_mock_module() -> None:
    """Page must NOT import from lib/mock.ts (USE_MOCK=false path)."""
    code = _strip_comments(PAGE.read_text(encoding="utf-8"))
    assert 'from "../../../lib/mock"' not in code and \
           'from "../../lib/mock"' not in code, (
        "q1-2024-gdp page must not import from lib/mock.ts"
    )
    assert not re.search(r"\bMOCK_[A-Z_]+\b", code), (
        "q1-2024-gdp page must not reference any MOCK_* identifier"
    )


def test_renders_all_6_sha_prefixes() -> None:
    """Page must surface the 6 SHA prefixes (国家 + 5 省级)."""
    src = PAGE.read_text(encoding="utf-8")
    for sha in REQUIRED_SHA_PREFIXES:
        assert sha in src, (
            f"q1-2024-gdp page missing SHA prefix {sha[:8]}: {sha!r}"
        )


def test_renders_all_6_source_domains() -> None:
    """Page must surface the 6 .gov.cn source domains (non-homepage)."""
    src = PAGE.read_text(encoding="utf-8")
    for d in REQUIRED_SOURCE_DOMAINS:
        assert d in src, (
            f"q1-2024-gdp page missing source domain {d!r}"
        )


def test_renders_crosscheck_report() -> None:
    """Page must read + render docs/reports/m2_2024_gdp_crosscheck_*.md.

    This is the USE_MOCK=false path: real on-disk artifact, not mock.
    """
    src = PAGE.read_text(encoding="utf-8")
    assert "m2_2024_gdp_crosscheck_20260831.md" in src, (
        "q1-2024-gdp page must read crosscheck markdown report"
    )
    assert "readFile" in src or "read_report" in src.lower(), (
        "q1-2024-gdp page must use fs.readFile() to load the report"
    )


def test_bottom_smoke_line() -> None:
    """Page must have the M2-e smoke line at the bottom (knife 635 §PHOTO-5)."""
    src = PAGE.read_text(encoding="utf-8")
    assert "[M2-e smoke]" in src, (
        "q1-2024-gdp page must include bottom [M2-e smoke] line"
    )
    assert "国家=" in src and "5省合计=" in src and "覆盖率=" in src, (
        "q1-2024-gdp page smoke line must include 国家 / 5省合计 / 覆盖率"
    )


def test_does_not_announce_pass() -> None:
    """Page must NOT claim Gate / O1 / M2 PASS (knife 635 §3 红线).

    Allowable forms: explicit "非 Gate/O1/M2 PASS" or "NOT Gate / O1 / M2 PASS"
    negations (header literal is one such negation).
    """
    src = _collapse(_strip_comments(PAGE.read_text(encoding="utf-8")))
    forbidden_unconditional = [
        "M2-e PASS",
        "O1 PASS",        # contiguous (M2 PASS may appear as "非 ... M2 PASS")
        "Gate PASS",      # contiguous
        "O1 完成",
        "Gate 完成",
    ]
    for bad in forbidden_unconditional:
        assert bad not in src, (
            f"q1-2024-gdp page contains forbidden claim: {bad!r}"
        )
    # Positive negation must appear (header carries it)
    assert (
        "非 Gate/O1/M2 PASS" in src
        or "NOT Gate / O1 / M2 PASS" in src
        or "非 Gate" in src
        or "不代表 Gate" in src
    ), "q1-2024-gdp page must contain explicit '非 Gate/O1/M2 PASS' negation"


def test_displays_blocked_count() -> None:
    """Page must explicitly display 26 BLOCKED provinces count (honest)."""
    src = PAGE.read_text(encoding="utf-8")
    assert "BLOCKED" in src, "q1-2024-gdp page must mention BLOCKED status"
    assert "26" in src, "q1-2024-gdp page must display 26 (blocked count)"