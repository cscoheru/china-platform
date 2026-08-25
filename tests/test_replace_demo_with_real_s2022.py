"""Stage 2 / S2.0.2.2 — `replace_demo_with_real.py` pytest wrapper.

Per tasking 162 §NOW-1: fixture 文件进 allowlist 前缀 → sha →（模拟或真实）
upload/seed 路径 → 断言 `is_demo` 清除或等价.

Test cases (≥3 required by §NOW-1):
  1. test_happy_path_fixture_under_tmp_uploads
     — fixture in /tmp/cegr_uploads/ → rc=0 + lineage.is_demo="false"
     + source_file_sha256 is non-zero 64-char hex + matches compute_file_sha
  2. test_out_of_prefix_path_exits_2
     — fixture outside allowlist → rc=2 (allowlist honored)
  3. test_missing_fixture_exits_1
     — path doesn't exist → rc=1
  4. test_url_flag_rejected_by_argparse
     — --url http://... → argparse rejects + rc=2 (防误用门槛)
  5. test_lineage_does_not_regress_to_demo_true
     — repeated calls with different fixtures → never returns is_demo="true"
  6. test_regression_compute_file_sha_still_green
     — explicitly invoke test_compute_file_sha's smoke case to confirm
       upstream allowlist behavior unchanged
"""
from __future__ import annotations

import json
import re
import subprocess
import sys
import textwrap
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]
SCRIPT = REPO_ROOT / "scripts" / "replace_demo_with_real.py"
COMPUTE_SHA = REPO_ROOT / "scripts" / "compute_file_sha.py"
ALLOWLIST_TMP_DIR = Path("/tmp/cegr_uploads")

# Ensure scripts/ is on sys.path so the wrapper can `import compute_file_sha`.
SCRIPTS_DIR = str(REPO_ROOT / "scripts")
if SCRIPTS_DIR not in sys.path:
    sys.path.insert(0, SCRIPTS_DIR)

import compute_file_sha  # noqa: E402  — scripts/ on sys.path


def _run_wrapper(*args: str, env_extra: dict | None = None) -> subprocess.CompletedProcess:
    """Invoke replace_demo_with_real.py as a subprocess (clean sys.argv)."""
    import os
    env = os.environ.copy()
    env["PYTHONPATH"] = SCRIPTS_DIR + (
        os.pathsep + env["PYTHONPATH"] if "PYTHONPATH" in env else ""
    )
    if env_extra:
        env.update(env_extra)
    return subprocess.run(
        [sys.executable, str(SCRIPT), *args],
        capture_output=True,
        text=True,
        env=env,
    )


@pytest.fixture(scope="module")
def happy_fixture(tmp_path_factory) -> Path:
    """Fixture under /tmp/cegr_uploads/ — exercises the canonical happy path."""
    ALLOWLIST_TMP_DIR.mkdir(parents=True, exist_ok=True)
    # NOTE: bytes are an honest placeholder. We are NOT forging Jiangsu
    # bulletin content (per Cursor 162 §红线). The test asserts that the
    # recorded SHA matches whatever the bytes actually are.
    fixture = ALLOWLIST_TMP_DIR / "s2022_test_fixture.txt"
    fixture.write_bytes(b"placeholder bytes for S2.0.2.2 overwrite flow -- NOT a forged Jiangsu bulletin")
    return fixture


# ---------- Case 1: happy path ----------
def test_happy_path_fixture_under_tmp_uploads(happy_fixture: Path) -> None:
    result = _run_wrapper(str(happy_fixture))
    assert result.returncode == 0, (
        f"expected rc=0; got {result.returncode}; stderr={result.stderr!r}"
    )
    lineage = json.loads(result.stdout)

    assert lineage["is_demo"] == "false", (
        f"is_demo must be cleared (per Cursor 162 §SCHEMA); got {lineage['is_demo']!r}"
    )
    assert lineage["is_demo"] != "true", "explicit is_demo != 'true' guard"

    sha = lineage["source_file_sha256"]
    assert re.fullmatch(r"[0-9a-f]{64}", sha), f"bad SHA format: {sha!r}"
    assert sha != "0" * 64, "all-zero SHA forbidden (would be placeholder forgery)"

    # Cross-check: SHA must match what compute_file_sha prints for the same file.
    cp = subprocess.run(
        [sys.executable, str(COMPUTE_SHA), str(happy_fixture)],
        capture_output=True,
        text=True,
        env={"PYTHONPATH": SCRIPTS_DIR},
    )
    assert cp.returncode == 0
    assert cp.stdout.strip() == sha, (
        f"SHA mismatch:\n  wrapper says {sha}\n  compute_file_sha says {cp.stdout.strip()}"
    )

    # stderr must be silent on the happy path (downstream curl-style callers
    # rely on stderr being empty so stdout parsing is clean).
    assert result.stderr == "", f"happy-path stderr must be empty; got {result.stderr!r}"


# ---------- Case 2: out-of-prefix ----------
def test_out_of_prefix_path_exits_2(tmp_path: Path) -> None:
    """Path outside ALLOWED_PREFIXES → rc=2 (mirrors compute_file_sha behavior)."""
    bad = tmp_path / "outside_allowlist.bin"
    bad.write_bytes(b"some bytes")
    result = _run_wrapper(str(bad))
    assert result.returncode == 2, (
        f"expected rc=2 for out-of-prefix; got {result.returncode}; "
        f"stderr={result.stderr!r}"
    )
    assert "allowed prefix" in result.stderr or "not under" in result.stderr


# ---------- Case 3: missing fixture ----------
def test_missing_fixture_exits_1(tmp_path: Path) -> None:
    """Path doesn't exist → rc=1 (mirrors compute_file_sha rc=1)."""
    ghost = tmp_path / "ghost.bin"
    result = _run_wrapper(str(ghost))
    assert result.returncode == 1, (
        f"expected rc=1 for missing file; got {result.returncode}; "
        f"stderr={result.stderr!r}"
    )
    assert "not found" in result.stderr or "regular file" in result.stderr


# ---------- Case 4: --url rejected ----------
def test_url_flag_rejected_by_argparse(happy_fixture: Path) -> None:
    """防误用门槛: --url not registered → argparse exit 2 (no silent acceptance)."""
    result = _run_wrapper("--url", "http://evil.example/foo.pdf", str(happy_fixture))
    assert result.returncode == 2, (
        f"--url should be rejected by argparse; got rc={result.returncode}; "
        f"stderr={result.stderr!r}"
    )
    assert "unrecognized arguments" in result.stderr or "unrecognized" in result.stderr


# ---------- Case 5: never returns is_demo="true" ----------
def test_lineage_does_not_regress_to_demo_true(happy_fixture: Path) -> None:
    """Repeated calls must never silently regress the sentinel."""
    for _ in range(3):
        result = _run_wrapper(str(happy_fixture))
        assert result.returncode == 0
        lineage = json.loads(result.stdout)
        assert lineage["is_demo"] != "true", "is_demo must never be 'true' post-overwrite"


# ---------- Case 6: upstream regression ----------
def test_upstream_compute_file_sha_allowlist_unchanged() -> None:
    """Sanity: compute_file_sha.py's allowlist still has all 3 entries.

    This is a guardrail — if upstream grows/shrinks the allowlist, the wrapper
    follows it automatically via direct import, but a reviewer should know.
    """
    prefixes = compute_file_sha.ALLOWED_PREFIXES
    assert any("/tmp/cegr_uploads/" in p for p in prefixes)
    assert any("/private/tmp/cegr_uploads/" in p for p in prefixes)
    assert any("seed_archives" in p for p in prefixes)


# ---------- Case 7: seed_archives path also allowed ----------
def test_seed_archives_path_also_allowed(tmp_path: Path) -> None:
    """data/seed_archives/ is the second allowlist entry — must also pass."""
    sa_dir = REPO_ROOT / "data" / "seed_archives"
    sa_dir.mkdir(parents=True, exist_ok=True)
    sa_file = sa_dir / "s2022_seed_archives_fixture.bin"
    sa_file.write_bytes(b"seed-archives fixture for S2.0.2.2")
    try:
        result = _run_wrapper(str(sa_file))
        assert result.returncode == 0, (
            f"seed_archives path must be allowed; got rc={result.returncode}; "
            f"stderr={result.stderr!r}"
        )
        lineage = json.loads(result.stdout)
        assert lineage["is_demo"] != "true"
    finally:
        sa_file.unlink(missing_ok=True)
