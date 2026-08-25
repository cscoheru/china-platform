"""Stage 2 / S2.0.1 — Next.js skeleton smoke (pytest wrapper).

Per tasking 146 §NOW.3: "pytest 或前端 smoke（最小可验收）".

This test wraps frontend/smoke-check.py so it runs under pytest. We avoid
spawning `next build` (which would require node_modules in the test env).

S2.0.1 is a *skeleton*, not a deployed app; pytest is the smallest acceptable
verification that satisfies tasking 146. Subsequent Stage 2 刀 (S2.7-b etc.)
will add real Playwright/Next.js e2e.
"""
from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

import pytest

FRONTEND_DIR = Path(__file__).resolve().parent.parent / "frontend"
SMOKE_SCRIPT = FRONTEND_DIR / "smoke-check.py"


def _run_smoke() -> subprocess.CompletedProcess:
    """Invoke frontend/smoke-check.py and capture output."""
    if not SMOKE_SCRIPT.is_file():
        pytest.fail(f"smoke-check.py missing at {SMOKE_SCRIPT}")
    return subprocess.run(
        [sys.executable, str(SMOKE_SCRIPT)],
        cwd=str(FRONTEND_DIR),
        capture_output=True,
        text=True,
        check=False,
    )


def test_frontend_skeleton_files_present() -> None:
    """Required skeleton files exist under frontend/."""
    required = [
        "package.json",
        "tsconfig.json",
        "next.config.js",
        "README.md",
        "app/layout.tsx",
        "app/page.tsx",
        "app/DemoBadge.tsx",
        "app/provinces/jiangsu/page.tsx",
        "lib/api.ts",
        "lib/types.ts",
        "lib/mock.ts",
    ]
    missing = [p for p in required if not (FRONTEND_DIR / p).is_file()]
    assert not missing, f"missing frontend files: {missing}"


def test_frontend_skeleton_smoke_passes() -> None:
    """frontend/smoke-check.py returns 0 and reports PASS."""
    result = _run_smoke()
    if result.returncode != 0:
        pytest.fail(
            f"smoke-check.py failed (rc={result.returncode})\n"
            f"STDOUT:\n{result.stdout}\nSTDERR:\n{result.stderr}"
        )
    assert "PASS" in result.stdout, (
        f"smoke-check.py did not print PASS marker; got:\n{result.stdout}"
    )


def test_frontend_package_declares_next_react() -> None:
    """package.json depends on next + react + react-dom."""
    import json

    pkg = json.loads((FRONTEND_DIR / "package.json").read_text(encoding="utf-8"))
    deps = pkg.get("dependencies", {})
    for dep in ("next", "react", "react-dom"):
        assert dep in deps, f"package.json missing dependency: {dep}"


def test_frontend_mock_data_has_is_demo_sentinel() -> None:
    """lib/mock.ts includes at least one row with lineage.is_demo === "true".

    Per docs/34 §4.2 + tasking 146 §SCHEMA: this is the load-bearing requirement
    that distinguishes S1.18 DEMO sentinels from future real SHA-locked samples.
    """
    import re

    mock = (FRONTEND_DIR / "lib/mock.ts").read_text(encoding="utf-8")
    assert re.search(r'is_demo:\s*"true"', mock), (
        "lib/mock.ts has no lineage.is_demo === 'true' sentinel row"
    )


def test_frontend_readme_documents_mock_toggle() -> None:
    """README.md explains NEXT_PUBLIC_USE_MOCK + is_demo badge contract."""
    readme = (FRONTEND_DIR / "README.md").read_text(encoding="utf-8")
    assert "NEXT_PUBLIC_USE_MOCK" in readme, "README does not document mock toggle"
    assert "is_demo" in readme, "README does not document is_demo badge contract"