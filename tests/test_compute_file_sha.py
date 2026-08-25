"""Stage 2 / S2.0.2.1 — tests for scripts/compute_file_sha.py.

Per tasking 157 §NOW.1: ≥5 pytest cases covering 合法 / 缺文件 / 越权 /
无 --url 选项 / SHA 格式. We ship 6 cases (the 5 mandated + one for
/private/tmp macOS alias resolution, per Cursor 156 §1).
"""
from __future__ import annotations

import os
import re
import subprocess
import sys
from pathlib import Path

import pytest

PROJECT_ROOT = Path(__file__).resolve().parents[1]
CLI = PROJECT_ROOT / "scripts" / "compute_file_sha.py"


def _run(args: list[str]) -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, str(CLI), *args],
        capture_output=True,
        text=True,
        cwd=str(PROJECT_ROOT),
        check=False,
    )


@pytest.fixture
def allowed_tmp_file(tmp_path: Path) -> Path:
    """A real file under /tmp/cegr_uploads/ (one of the allowed prefixes)."""
    upload_dir = Path("/tmp/cegr_uploads")
    upload_dir.mkdir(parents=True, exist_ok=True)
    f = upload_dir / f"pytest_compute_sha_{os.getpid()}.txt"
    f.write_bytes(b"hello world")
    yield f
    try:
        f.unlink()
    except FileNotFoundError:
        pass


@pytest.fixture
def allowed_seed_archive_file(tmp_path: Path) -> Path:
    """A real file under data/seed_archives/ (dev fixture prefix)."""
    archive_dir = PROJECT_ROOT / "data" / "seed_archives"
    archive_dir.mkdir(parents=True, exist_ok=True)
    f = archive_dir / f"pytest_compute_sha_{os.getpid()}.txt"
    f.write_bytes(b"fixture-content")
    yield f
    try:
        f.unlink()
    except FileNotFoundError:
        pass


# --- 1. 合法 /tmp/cegr_uploads 文件：exit 0 + 64-char hex ---
def test_valid_file_under_tmp_cegr_uploads_exits_0(allowed_tmp_file: Path) -> None:
    """Valid file under /tmp/cegr_uploads/ → exit 0, prints 64-char lowercase hex."""
    result = _run([str(allowed_tmp_file)])
    assert result.returncode == 0, (
        f"expected rc=0, got rc={result.returncode}\n"
        f"STDOUT:\n{result.stdout}\nSTDERR:\n{result.stderr}"
    )
    sha = result.stdout.strip()
    assert len(sha) == 64, f"SHA must be 64 chars, got {len(sha)}"
    assert re.fullmatch(r"[0-9a-f]{64}", sha), (
        f"SHA must be lowercase hex, got {sha!r}"
    )
    # Sanity: SHA-256 of "hello world" is well-known
    assert sha == "b94d27b9934d3e08a52e52d7da7dabfac484efe37a5380ee9088f7ace2efcde9", (
        f"SHA mismatch; got {sha!r}"
    )


# --- 2. 合法 /data/seed_archives/ 文件：exit 0 + 64-char hex ---
def test_valid_file_under_seed_archives_exits_0(allowed_seed_archive_file: Path) -> None:
    """Valid file under data/seed_archives/ → exit 0."""
    result = _run([str(allowed_seed_archive_file)])
    assert result.returncode == 0, (
        f"expected rc=0, got rc={result.returncode}\n"
        f"STDERR:\n{result.stderr}"
    )
    assert re.fullmatch(r"[0-9a-f]{64}", result.stdout.strip()), (
        f"stdout must be 64-char hex, got {result.stdout!r}"
    )


# --- 3. 缺文件：exit 1 ---
def test_missing_file_exits_1(tmp_path: Path) -> None:
    """Path does not exist (but is under an allowed prefix) → exit 1."""
    nonexistent = tmp_path / "does_not_exist.txt"
    # Construct an allowed-prefix path that does NOT exist
    allowed_missing = Path("/tmp/cegr_uploads") / f"pytest_missing_{os.getpid()}.txt"
    # If somehow present, remove first
    if allowed_missing.exists():
        allowed_missing.unlink()
    result = _run([str(allowed_missing)])
    assert result.returncode == 1, (
        f"expected rc=1 for missing file, got rc={result.returncode}\n"
        f"STDOUT:\n{result.stdout}\nSTDERR:\n{result.stderr}"
    )


# --- 4. 越权路径（不在白名单）：exit 2 ---
def test_out_of_prefix_path_exits_2(tmp_path: Path) -> None:
    """Path outside any allowed prefix → exit 2 (拒绝越权)."""
    out_of_prefix = tmp_path / "evil.txt"
    out_of_prefix.write_bytes(b"x")
    result = _run([str(out_of_prefix)])
    assert result.returncode == 2, (
        f"expected rc=2 for out-of-prefix, got rc={result.returncode}\n"
        f"STDOUT:\n{result.stdout}\nSTDERR:\n{result.stderr}"
    )


# --- 5. argparse 不接受 --url（防误用门槛） ---
def test_url_option_rejected_by_argparse() -> None:
    """Per docs/35 §4.2 防误用门槛: --url 必须不存在. argparse exits 2."""
    result = _run(["--url", "http://example.com/secret.pdf"])
    assert result.returncode == 2, (
        f"--url must be rejected with rc=2; got rc={result.returncode}\n"
        f"STDOUT:\n{result.stdout}\nSTDERR:\n{result.stderr}"
    )
    assert "unrecognized" in result.stderr.lower() or "unrecognized" in result.stdout.lower(), (
        f"argparse should report 'unrecognized arguments'; "
        f"got stdout={result.stdout!r}, stderr={result.stderr!r}"
    )


# --- 6. macOS /private/tmp alias（per Cursor 156 §1） ---
def test_private_tmp_alias_resolves_correctly(tmp_path: Path) -> None:
    """On macOS, /tmp is a symlink to /private/tmp. Files written to
    /tmp/cegr_uploads/ resolve to /private/tmp/cegr_uploads/. The CLI must
    accept both spellings because resolve() canonicalises them.

    This test only enforces the contract that an admin-uploaded file
    (typically written via /tmp/...) is accepted; on Linux, /tmp and
    /private/tmp are separate, but the test still passes because the
    allowlist contains both prefixes.
    """
    # Use the same fixture helper logic inline
    upload_dir = Path("/tmp/cegr_uploads")
    upload_dir.mkdir(parents=True, exist_ok=True)
    f = upload_dir / f"pytest_macos_alias_{os.getpid()}.txt"
    f.write_bytes(b"macos-alias-content")
    try:
        result = _run([str(f)])
        assert result.returncode == 0, (
            f"file written via /tmp/ must be accepted (resolves to "
            f"/private/tmp/ on macOS); got rc={result.returncode}\n"
            f"STDERR:\n{result.stderr}"
        )
        assert re.fullmatch(r"[0-9a-f]{64}", result.stdout.strip()), (
            f"SHA format check failed; got {result.stdout!r}"
        )
    finally:
        try:
            f.unlink()
        except FileNotFoundError:
            pass


# --- 7. SHA 格式 / 长度 / 单行输出（额外加固） ---
def test_sha_is_single_line_64_lowercase_hex(allowed_tmp_file: Path) -> None:
    """stdout must be EXACTLY one line of 64 lowercase hex chars, no stderr."""
    result = _run([str(allowed_tmp_file)])
    assert result.returncode == 0
    lines = result.stdout.strip().splitlines()
    assert len(lines) == 1, f"stdout must be exactly 1 line, got {len(lines)}"
    sha = lines[0]
    assert len(sha) == 64, f"SHA must be 64 chars, got {len(sha)}"
    assert sha == sha.lower(), "SHA must be lowercase"
    assert all(c in "0123456789abcdef" for c in sha), (
        f"SHA must be hex-only; got {sha!r}"
    )
    assert result.stderr == "", (
        f"stderr must be empty on success (downstream tooling captures stdout); "
        f"got {result.stderr!r}"
    )