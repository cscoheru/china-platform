#!/usr/bin/env python3
"""M1 T6 — Frontend /research/m1-series acceptance surface contract.

Per docs/55 §T6 (knife 629 §2 T6):
  * page.tsx exists at frontend/app/research/m1-series/page.tsx
  * USE_MOCK=false → fetch T5 API (do NOT use lib/mock.ts; no MOCK UUID literals)
  * Page header contains the required literal Chinese sentence.
  * Page exposes caveat, SHA prefix 8, and source URL.
  * frontend/app/page.tsx links to /research/m1-series.
  * frontend/smoke-check.py passes (separate file as the canonical gate).

Asserts:
  * The page file exists.
  * Required header literal is present.
  * No MOCK_*-UUID strings are present.
  * Calls indicatorSeries() from lib/api.ts (live path, not lib/mock.ts).
  * Renders caveat_text + source_hash_prefix + source_domain + c5cf5abe.
  * frontend/app/page.tsx links to /research/m1-series.
  * frontend/smoke-check.py exits 0.
"""
from __future__ import annotations

import re
import subprocess
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent
FRONTEND = REPO_ROOT / "frontend"
PAGE = FRONTEND / "app" / "research" / "m1-series" / "page.tsx"
HOME = FRONTEND / "app" / "page.tsx"
SMOKE = FRONTEND / "smoke-check.py"

REQUIRED_HEADER = (
    "M1 验收面 · 湖北 2026 上半年 GDP（公报样本）· 非 31 省 · 非 Gate PASS"
)
FORBIDDEN_MOCK_UUIDS = [
    "JIANGSU-GDP-INDICATOR-UUID-MOCK",
    "JIANGSU-GEO-UUID-MOCK",
]


def _strip_comments(src: str) -> str:
    """Strip JS line + block comments so scans hit only executable code."""
    src = re.sub(r"//[^\n]*", "", src)
    src = re.sub(r"/\*.*?\*/", "", src, flags=re.DOTALL)
    return src


# ---------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------


def test_page_file_exists() -> None:
    """Per knife 629 §2 T6: page.tsx at /research/m1-series/ must exist."""
    assert PAGE.is_file(), f"missing {PAGE}"


def test_required_header_present() -> None:
    """The exact literal header must be on the page (knife 629 §2 T6 字面量)."""
    src = PAGE.read_text(encoding="utf-8")
    assert REQUIRED_HEADER in src, (
        f"m1-series page missing required header literal:\n  expected={REQUIRED_HEADER!r}\n  source_head={src[:300]!r}"
    )


def test_no_mock_uuids() -> None:
    """The page must NOT hardcode any MOCK_*_UUID (knife §2 T5/T6 红线)."""
    src = _strip_comments(PAGE.read_text(encoding="utf-8"))
    for bad in FORBIDDEN_MOCK_UUIDS:
        assert bad not in src, f"m1-series page contains forbidden mock UUID: {bad}"


def test_uses_indicatorSeries_api() -> None:
    """Page must call indicatorSeries() from lib/api.ts (live API path)."""
    code = _strip_comments(PAGE.read_text(encoding="utf-8"))
    assert "indicatorSeries" in code, (
        "m1-series page must call indicatorSeries() from lib/api.ts (no mock path)"
    )


def test_does_not_import_mock_module() -> None:
    """Page must NOT import from lib/mock.ts (knife §2 T6 USE_MOCK=false path)."""
    code = _strip_comments(PAGE.read_text(encoding="utf-8"))
    assert 'from "../../../lib/mock"' not in code, (
        "m1-series page must not import from lib/mock.ts"
    )
    # Direct MOCK_* identifier also forbidden (catches non-import references)
    assert not re.search(r"\bMOCK_[A-Z_]+\b", code), (
        "m1-series page must not reference any MOCK_* identifier"
    )


def test_renders_caveat_and_provenance() -> None:
    """Page must render caveat_text + source_hash_prefix + SHA prefix + 源 URL."""
    src = PAGE.read_text(encoding="utf-8")
    for needle, label in [
        ("caveat_text", "caveat_text field"),
        ("source_hash_prefix", "source_hash_prefix field"),
        ("c5cf5abe", "SHA prefix 8 literal"),
        ("tjj.hubei.gov.cn", "source domain (non-homepage)"),
    ]:
        assert needle in src, f"m1-series page missing {label}: {needle!r}"


def test_home_page_links_to_m1_series() -> None:
    """frontend/app/page.tsx must contain a link to /research/m1-series."""
    assert HOME.is_file(), f"missing {HOME}"
    code = _strip_comments(HOME.read_text(encoding="utf-8"))
    assert 'href="/research/m1-series"' in code, (
        "frontend/app/page.tsx missing /research/m1-series nav anchor"
    )


def test_smoke_check_exits_zero() -> None:
    """The canonical frontend smoke gate must pass (it now includes §14 M1)."""
    proc = subprocess.run(
        [sys.executable, str(SMOKE)],
        capture_output=True,
        text=True,
        timeout=60,
        cwd=str(FRONTEND),
    )
    assert proc.returncode == 0, (
        f"frontend/smoke-check.py failed: rc={proc.returncode}\n"
        f"--- stdout ---\n{proc.stdout[-1500:]}\n--- stderr ---\n{proc.stderr[-500:]}"
    )
