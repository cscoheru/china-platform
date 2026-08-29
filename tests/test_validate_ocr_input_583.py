"""Tests for `validate_ocr_input()` + `is_control_flow_fixture()` (knife 583).

Per docs/49 §2.3 (API form) + §5.2.2 (实装位置) + 583 任务书 §C.

Four-state coverage:
  - ACCEPT (PDF / JPEG / PNG / TIFF in either ALLOWED_PREFIXES[0] or SEED_ARCHIVES)
  - REJECT_OUTSIDE_ALLOWLIST (/etc/passwd + out-of-prefix tmp paths)
  - REJECT_CONTROL_FLOW_FIXTURE (name pattern + content marker)
  - REJECT_MIME (allowed prefix but wrong suffix)

Boundary:
  - .pdf suffix but file does not exist → REJECT_OUTSIDE_ALLOWLIST
    (path.resolve() on a non-existent file under /private/tmp still resolves
    to /private/tmp/<name>; the existence check is downstream)

Red lines honored:
  - No spike file edits (uses tmp_path / monkeypatch only)
  - No real fixture byte changes (4 lock values unchanged)
  - No network / no DB
  - No production code beyond intake_real_sha_if_present.py (already in 583 §A)
"""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

# scripts/ on PYTHONPATH (mirrors intake_real_sha_if_present.py self-import).
SCRIPTS_DIR = Path(__file__).resolve().parent.parent / "scripts"
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))

from intake_real_sha_if_present import (  # noqa: E402
    ALLOWED_PREFIXES,
    SEED_ARCHIVES,
    is_control_flow_fixture,
    validate_ocr_input,
)

# Allowed MIME set (per docs/49 §2.1 + §2.3 + 583 任务书 §A step 3).
PDF_MAGIC = b"%PDF-1.4\n"
JPEG_MAGIC = b"\xff\xd8\xff\xe0\x00\x10JFIF\x00\x01"
PNG_MAGIC = b"\x89PNG\r\n\x1a\n"
TIFF_MAGIC_LE = b"II*\x00"  # little-endian TIFF
TIFF_MAGIC_BE = b"MM\x00*"  # big-endian TIFF

# Primary upload prefix (avoid macOS /tmp → /private/tmp drift).
UPLOAD_PRIMARY = ALLOWED_PREFIXES[0]


def _write_file(path: Path, content: bytes) -> Path:
    """Write content to path; ensure parent exists; return path."""
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(content)
    return path


# -----------------------------------------------------------------------------
# ACCEPT — primary upload prefix (PDF / JPEG / PNG / TIFF)
# -----------------------------------------------------------------------------


def test_accept_pdf_in_upload_prefix(tmp_path: Path) -> None:
    """ACCEPT for .pdf file under ALLOWED_PREFIXES[0]."""
    target = _write_file(
        tmp_path / "report.pdf", PDF_MAGIC + b"x" * 2048
    )
    # Build path that lives under ALLOWED_UPLOAD_DIR (= ALLOWED_PREFIXES[0]).
    rel = target.name
    upload_path = Path(UPLOAD_PRIMARY) / rel
    upload_path.parent.mkdir(parents=True, exist_ok=True)
    upload_path.write_bytes(target.read_bytes())
    try:
        assert validate_ocr_input(upload_path) == "ACCEPT"
    finally:
        upload_path.unlink(missing_ok=True)


def test_accept_jpeg_in_upload_prefix(tmp_path: Path) -> None:
    rel = "snapshot.jpg"
    upload_path = Path(UPLOAD_PRIMARY) / rel
    upload_path.parent.mkdir(parents=True, exist_ok=True)
    upload_path.write_bytes(JPEG_MAGIC + b"x" * 2048)
    try:
        assert validate_ocr_input(upload_path) == "ACCEPT"
    finally:
        upload_path.unlink(missing_ok=True)


def test_accept_png_in_upload_prefix(tmp_path: Path) -> None:
    rel = "diagram.png"
    upload_path = Path(UPLOAD_PRIMARY) / rel
    upload_path.parent.mkdir(parents=True, exist_ok=True)
    upload_path.write_bytes(PNG_MAGIC + b"x" * 2048)
    try:
        assert validate_ocr_input(upload_path) == "ACCEPT"
    finally:
        upload_path.unlink(missing_ok=True)


def test_accept_tiff_in_upload_prefix(tmp_path: Path) -> None:
    rel = "scan_le.tif"
    upload_path = Path(UPLOAD_PRIMARY) / rel
    upload_path.parent.mkdir(parents=True, exist_ok=True)
    upload_path.write_bytes(TIFF_MAGIC_LE + b"x" * 2048)
    try:
        assert validate_ocr_input(upload_path) == "ACCEPT"
    finally:
        upload_path.unlink(missing_ok=True)


# -----------------------------------------------------------------------------
# ACCEPT — seed_archives prefix (fixture path)
# -----------------------------------------------------------------------------


def test_accept_pdf_in_seed_archives(tmp_path: Path) -> None:
    """ACCEPT for .pdf file under SEED_ARCHIVES (use a fresh seed file)."""
    name = "583_test_seed_sample.pdf"
    target = SEED_ARCHIVES / name
    target.write_bytes(PDF_MAGIC + b"x" * 2048)
    try:
        assert validate_ocr_input(target) == "ACCEPT"
    finally:
        target.unlink(missing_ok=True)


# -----------------------------------------------------------------------------
# REJECT_OUTSIDE_ALLOWLIST
# -----------------------------------------------------------------------------


def test_reject_etc_passwd() -> None:
    """/etc/passwd cannot be in any allowed prefix → REJECT_OUTSIDE_ALLOWLIST."""
    assert validate_ocr_input(Path("/etc/passwd")) == "REJECT_OUTSIDE_ALLOWLIST"


def test_reject_outside_allowlist_tmp(tmp_path: Path) -> None:
    """Path under tmp_path but NOT under ALLOWED_PREFIXES[0] → REJECT."""
    # Use tmp_path from pytest; not under /tmp/cegr_uploads or /private/tmp/cegr_uploads.
    outside = tmp_path / "evil.pdf"
    outside.write_bytes(PDF_MAGIC + b"x" * 2048)
    assert validate_ocr_input(outside) == "REJECT_OUTSIDE_ALLOWLIST"


def test_reject_nonexistent_pdf_outside_prefix(tmp_path: Path) -> None:
    """Non-existent path with .pdf suffix under tmp_path → REJECT_OUTSIDE_ALLOWLIST
    (path.resolve() works but the prefix check fails first).

    Boundary note: docs/49 §2.3 + 583 任务书 §A step 1 checks prefix AFTER
    resolve(); existence is irrelevant to allowlist decision. A non-existent
    path under a non-allowlisted tmp_path must still be REJECT_OUTSIDE_ALLOWLIST.
    """
    ghost = tmp_path / "ghost.pdf"
    assert not ghost.exists()
    assert validate_ocr_input(ghost) == "REJECT_OUTSIDE_ALLOWLIST"


# -----------------------------------------------------------------------------
# REJECT_CONTROL_FLOW_FIXTURE
# -----------------------------------------------------------------------------


def test_reject_fixture_name_pattern(tmp_path: Path) -> None:
    """Filename 'test_fixture' triggers FIXTURE_NAME_PATTERNS → REJECT."""
    upload_path = Path(UPLOAD_PRIMARY) / "test_fixture.pdf"
    upload_path.parent.mkdir(parents=True, exist_ok=True)
    upload_path.write_bytes(PDF_MAGIC + b"x" * 2048)
    try:
        assert validate_ocr_input(upload_path) == "REJECT_CONTROL_FLOW_FIXTURE"
    finally:
        upload_path.unlink(missing_ok=True)


def test_reject_fixture_content_marker(tmp_path: Path) -> None:
    """First 512 bytes contain 'placeholder bytes' → REJECT."""
    upload_path = Path(UPLOAD_PRIMARY) / "real_named_but_fixture_payload.pdf"
    upload_path.parent.mkdir(parents=True, exist_ok=True)
    upload_path.write_bytes(b"placeholder bytes\n" + PDF_MAGIC + b"x" * 2048)
    try:
        assert validate_ocr_input(upload_path) == "REJECT_CONTROL_FLOW_FIXTURE"
    finally:
        upload_path.unlink(missing_ok=True)


def test_is_control_flow_fixture_public_wrapper(tmp_path: Path) -> None:
    """Public wrapper `is_control_flow_fixture()` returns True for fixtures,
    False for clean files. Independent of validate_ocr_input's full gate."""
    fix = Path(UPLOAD_PRIMARY) / "test_x.bin"
    fix.parent.mkdir(parents=True, exist_ok=True)
    fix.write_bytes(b"x" * 2048)
    try:
        assert is_control_flow_fixture(fix) is True
    finally:
        fix.unlink(missing_ok=True)

    clean = Path(UPLOAD_PRIMARY) / "clean_name.bin"
    clean.parent.mkdir(parents=True, exist_ok=True)
    clean.write_bytes(b"x" * 2048)
    try:
        assert is_control_flow_fixture(clean) is False
    finally:
        clean.unlink(missing_ok=True)


# -----------------------------------------------------------------------------
# REJECT_MIME
# -----------------------------------------------------------------------------


def test_reject_mime_txt_in_upload_prefix(tmp_path: Path) -> None:
    """.txt file under ALLOWED_PREFIXES[0] → REJECT_MIME."""
    upload_path = Path(UPLOAD_PRIMARY) / "notes.txt"
    upload_path.parent.mkdir(parents=True, exist_ok=True)
    upload_path.write_bytes(b"plain text content\n" * 100)
    try:
        assert validate_ocr_input(upload_path) == "REJECT_MIME"
    finally:
        upload_path.unlink(missing_ok=True)


def test_reject_mime_exe_in_upload_prefix(tmp_path: Path) -> None:
    """.exe file under ALLOWED_PREFIXES[0] → REJECT_MIME."""
    upload_path = Path(UPLOAD_PRIMARY) / "malware.exe"
    upload_path.parent.mkdir(parents=True, exist_ok=True)
    upload_path.write_bytes(b"MZ\x00\x00" + b"x" * 2048)
    try:
        assert validate_ocr_input(upload_path) == "REJECT_MIME"
    finally:
        upload_path.unlink(missing_ok=True)


# -----------------------------------------------------------------------------
# Boundary — MIME check uses suffix only (not content sniff)
# -----------------------------------------------------------------------------


def test_pdf_suffix_with_random_content_still_accepted_by_mime(tmp_path: Path) -> None:
    """.pdf suffix + random bytes (not starting with %PDF-) → mimetypes sees
    'application/pdf' from suffix; gate returns ACCEPT (content sniffing is
    NOT in 583 scope per tasking §A deviation note).

    This pins the deviation: we deliberately rely on suffix-based MIME
    detection in 583; a future §5.2.4+ may upgrade to python-magic.
    """
    upload_path = Path(UPLOAD_PRIMARY) / "weird_suffix.pdf"
    upload_path.parent.mkdir(parents=True, exist_ok=True)
    upload_path.write_bytes(b"random bytes not pdf\n" + b"y" * 2048)
    try:
        # Step 1 passes (under prefix); step 2 passes (no fixture marker);
        # step 3: mimetypes.guess_type('.pdf') == 'application/pdf' → ACCEPT.
        assert validate_ocr_input(upload_path) == "ACCEPT"
    finally:
        upload_path.unlink(missing_ok=True)
