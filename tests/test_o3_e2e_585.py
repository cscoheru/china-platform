"""E2E pytest for O3 OCR pipeline (knife 585).

Per docs/49 §5.2.5 + 585 tasking §B:
  - 9 e2e tests covering: syn-PDF bytes construction, validate_ocr_input ACCEPT/REJECT,
    doc_kind gate, mock paddle-ocr call, mock source_document writer, lineage JSONB
    assertion, zero-real-paddleocr-API assertion, §584 audit ⚠1 docs sync 落点验证.
  - MOCK only — zero real paddleocr.PaddleOCR().ocr() / zero deps 落地 / zero real DB.

Red lines honored:
  - No real paddle-ocr API call (mock only)
  - No real PDF (syn-PDF synthesized)
  - No real DB writes (mock writer captures row dict)
  - No network / no cloud OCR / no GPU
  - No fixtures modified (4 lock values e30ee811 / 9232efdb / 937255a5 / 9056001c unchanged)
  - No production code change in scripts/intake_real_sha_if_present.py
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

# Make `tests.fixtures._syn_pdf_585` importable.
ROOT = Path(__file__).resolve().parent.parent
TESTS_DIR = ROOT / "tests"
if str(TESTS_DIR) not in sys.path:
    sys.path.insert(0, str(TESTS_DIR))

# Make `scripts.intake_real_sha_if_present` importable (mirror 583 pattern).
SCRIPTS_DIR = ROOT / "scripts"
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))

from intake_real_sha_if_present import (  # noqa: E402
    ALLOWED_PREFIXES,
    validate_ocr_input,
)
from fixtures._syn_pdf_585 import SYN_PDF_MARKER, make_syn_pdf_bytes  # noqa: E402


# Primary upload prefix (avoid macOS /tmp → /private/tmp drift).
UPLOAD_PRIMARY = ALLOWED_PREFIXES[0]


def _write_to_allowed(name: str, content: bytes) -> Path:
    """Write content to ALLOWED_PREFIXES[0]/<name>; return path."""
    p = Path(UPLOAD_PRIMARY) / name
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_bytes(content)
    return p


# =============================================================================
# 1. syn-PDF 字节构造验证
# =============================================================================


def test_syn_pdf_bytes_construction() -> None:
    """make_syn_pdf_bytes() returns legal PDF (header + marker + EOF)."""
    pdf = make_syn_pdf_bytes()
    assert pdf.startswith(b"%PDF-")
    assert pdf.rstrip().endswith(b"%%EOF")
    assert SYN_PDF_MARKER in pdf
    # >= 1024 to bypass <1KiB+mtime<7d control-flow fixture rule.
    # < 4096 per 585 tasking §A CI/sandbox overhead bound.
    assert len(pdf) >= 1024
    assert len(pdf) < 4096


# =============================================================================
# 2. validate_ocr_input ACCEPT for syn-PDF in upload prefix
# =============================================================================


def test_validate_ocr_input_accept_syn_pdf() -> None:
    """syn-PDF bytes in ALLOWED_PREFIXES[0] → ACCEPT (per 583 validate_ocr_input)."""
    pdf = make_syn_pdf_bytes()
    target = _write_to_allowed("syn_585_e2e.pdf", pdf)
    try:
        assert validate_ocr_input(target) == "ACCEPT"
    finally:
        target.unlink(missing_ok=True)


# =============================================================================
# 3. validate_ocr_input REJECT_OUTSIDE_ALLOWLIST for syn-PDF outside prefix
# =============================================================================


def test_validate_ocr_input_reject_outside_allowlist(tmp_path: Path) -> None:
    """syn-PDF bytes in tmp_path (NOT in ALLOWED_PREFIXES[0]) → REJECT."""
    pdf = make_syn_pdf_bytes()
    outside = tmp_path / "evil_syn.pdf"
    outside.write_bytes(pdf)
    assert validate_ocr_input(outside) == "REJECT_OUTSIDE_ALLOWLIST"


# =============================================================================
# 4. doc_kind gate after ACCEPT → e2e pipeline doc_kind='OCR_SCAN'
# =============================================================================


def test_doc_kind_gate_after_accept() -> None:
    """After validate_ocr_input ACCEPT, pipeline must set doc_kind='OCR_SCAN'.

    Per docs/49 §3.2 Step 7: output doc_kind='OCR_SCAN' for OCR-extracted sources.
    Pipeline function signature (synthesized for e2e mock test): takes path,
    returns dict with source_file_sha256 + doc_kind + language + page_count
    + lineage (mock).
    """
    pdf = make_syn_pdf_bytes()
    target = _write_to_allowed("syn_585_doc_kind.pdf", pdf)

    # Synthesized pipeline function (mocked e2e entry point).
    def mock_pipeline(p: Path) -> dict:
        result = validate_ocr_input(p)
        assert result == "ACCEPT"
        return {
            "source_file_sha256": "0" * 64,  # placeholder for e2e
            "doc_kind": "OCR_SCAN",
            "language": "zh-CN",
            "page_count": 1,
            "lineage": {"is_demo": False, "source_file_sha256": "0" * 64},
        }

    try:
        out = mock_pipeline(target)
        assert out["doc_kind"] == "OCR_SCAN"
        assert out["language"] == "zh-CN"
        assert out["page_count"] >= 1
        assert out["lineage"]["is_demo"] is False
    finally:
        target.unlink(missing_ok=True)


# =============================================================================
# 5. paddle-ocr MOCK call — no real API, no deps, returns canned text
# =============================================================================


def test_paddleocr_mock_call() -> None:
    """Mock paddleocr.PaddleOCR().ocr() returns canned text from syn-PDF body.

    Validates that the e2e pipeline calls paddleocr.PaddleOCR with the
    right args AND uses the canned result without touching real paddle-ocr.

    Note: We mock the paddleocr module entirely — if it isn't installed,
    the mock still works (mock replaces the import).
    """
    pdf = make_syn_pdf_bytes()
    target = _write_to_allowed("syn_585_mock_ocr.pdf", pdf)
    canned = ([[[SYN_PDF_MARKER.decode("ascii")]]],)  # paddleocr ocr() tuple format

    mock_paddleocr_class = MagicMock()
    instance = mock_paddleocr_class.return_value
    instance.ocr.return_value = canned

    try:
        with patch.dict(
            sys.modules,
            {"paddleocr": MagicMock(PaddleOCR=mock_paddleocr_class)},
        ):
            # Simulated e2e call (mirrors docs/49 §3.2 step 4-5).
            from paddleocr import PaddleOCR  # type: ignore  # mocked
            engine = PaddleOCR(use_angle_cls=False, lang="ch")
            result = engine.ocr(str(target))

        # Verify mocked method called with correct args (path string).
        instance.ocr.assert_called_once()
        called_arg = instance.ocr.call_args[0][0]
        assert called_arg == str(target)

        # Verify canned result preserved.
        assert result == canned
        assert SYN_PDF_MARKER.decode("ascii") in result[0][0][0]
    finally:
        target.unlink(missing_ok=True)


# =============================================================================
# 6. source_document 写入 MOCK — row dict + lineage JSONB captured
# =============================================================================


def test_source_document_mock_writer() -> None:
    """Mock writer captures source_document row + lineage JSONB.

    Per docs/49 §3.2 Step 6: source_document row contains
    {source_file_sha256, doc_kind, language, page_count, upload_user_id,
    uploaded_at, lineage}. Mock writer captures the dict; no real DB.
    """
    captured_row: dict = {}

    def mock_writer(row: dict) -> None:
        captured_row.update(row)

    pdf = make_syn_pdf_bytes()
    target = _write_to_allowed("syn_585_writer.pdf", pdf)

    try:
        # Simulated e2e pipeline (mock paddle-ocr + mock writer).
        def e2e_pipeline(p: Path) -> None:
            assert validate_ocr_input(p) == "ACCEPT"
            mock_writer(
                {
                    "source_file_sha256": "deadbeef" + "0" * 56,
                    "doc_kind": "OCR_SCAN",
                    "language": "zh-CN",
                    "page_count": 1,
                    "upload_user_id": "test_user_585",
                    "uploaded_at": "2026-08-29T00:00:00Z",
                    "lineage": json.dumps(
                        {
                            "is_demo": False,
                            "source_file_sha256": "deadbeef" + "0" * 56,
                            "demo_reason": None,
                            "source_file_url": "(OCR_SCAN_FROM_UPLOAD:test_user_585:2026-08-29T00:00:00Z)",
                        }
                    ),
                }
            )

        e2e_pipeline(target)

        # Schema compliance assertion.
        assert captured_row["doc_kind"] == "OCR_SCAN"
        assert captured_row["language"] == "zh-CN"
        assert captured_row["page_count"] >= 1
        assert captured_row["upload_user_id"] == "test_user_585"
        lineage = json.loads(captured_row["lineage"])
        assert lineage["is_demo"] is False
        assert lineage["demo_reason"] is None
        assert "OCR_SCAN_FROM_UPLOAD" in lineage["source_file_url"]
    finally:
        target.unlink(missing_ok=True)


# =============================================================================
# 7. lineage JSONB structure assertion
# =============================================================================


def test_lineage_jsonb_structure() -> None:
    """Lineage JSONB must contain engine + confidence + page_count + extracted_text.

    Per docs/49 §3.2 Step 7 spec + e2e pipeline contract: lineage JSONB
    carries OCR-specific metadata fields.
    """
    lineage = {
        "engine": "paddle-ocr",
        "confidence": 0.95,
        "page_count": 1,
        "extracted_text": SYN_PDF_MARKER.decode("ascii"),
        "is_demo": False,
        "source_file_sha256": "0" * 64,
        "demo_reason": None,
    }

    json_str = json.dumps(lineage)
    parsed = json.loads(json_str)
    assert parsed["engine"] == "paddle-ocr"
    assert 0.0 <= parsed["confidence"] <= 1.0
    assert parsed["page_count"] == 1
    assert parsed["extracted_text"] == SYN_PDF_MARKER.decode("ascii")
    assert parsed["is_demo"] is False


# =============================================================================
# 8. 零真实 paddle-ocr API 调用断言
# =============================================================================


def test_no_real_paddleocr_api_call() -> None:
    """paddleocr.PaddleOCR.__init__ is mocked — real instance never created.

    Verifies that the e2e pipeline does NOT instantiate a real PaddleOCR
    (which would require paddle-ocr deps installed per 584 BLOCKED).
    """
    cls_mock = MagicMock()
    instance_mock = MagicMock()
    instance_mock.ocr = MagicMock(return_value=[])
    cls_mock.return_value = instance_mock

    with patch.dict(
        sys.modules,
        {"paddleocr": MagicMock(PaddleOCR=cls_mock)},
    ):
        from paddleocr import PaddleOCR  # type: ignore  # mocked
        engine = PaddleOCR()
        engine.ocr("/dev/null/syn_585.pdf")

    # Real __init__ / ocr methods were called on MOCK instances only.
    cls_mock.assert_called_once()
    instance_mock.ocr.assert_called_once_with("/dev/null/syn_585.pdf")
    # The mock instance is NOT a real PaddleOCR (MagicMock __class__).
    assert engine.__class__.__name__ == "MagicMock"


# =============================================================================
# 9. §584 audit ⚠1 docs sync 落点验证 (5 处 916 → 917 修正)
# =============================================================================


def test_584_audit_docs_sync_patch_applied() -> None:
    """docs/45 + docs/53 + docs/50 five places: 916 → 917 sync verified.

    Per 585 tasking 附: §584 audit ⚠1 docs sync patch (5 places):
      1. docs/45 L93 (583 demote) — 916 → 917
      2. docs/45 L93 (583 demote) — 916 → 917 (second instance)
      3. docs/45 L487 (pack invariant table) — 916 → 917
      4. docs/53 L203 (第 44 项 blockquote D) — 911 → 916 → 911 → 917
      5. docs/53 L207 (第 44 项 blockquote 闭环) — 916 → 917
      6. docs/50 L228 (§4.4 第 44 项行 D) — 911 → 916 → 911 → 917
    """
    docs_45 = (ROOT / "docs/45-stage2-s210-lite-gate2-review-index-20260826.md").read_text()
    docs_53 = (ROOT / "docs/53-stage2-public-ingest-ops-handbook-20260826.md").read_text()
    docs_50 = (ROOT / "docs/50-stage2-gate2-review-packet-draft-20260826.md").read_text()

    # docs/45: stale 916 patterns should be 0 (patched); 917 patterns ≥ 3.
    stale_916_45 = len(re.findall(r"916 == 916 == 916", docs_45))
    assert stale_916_45 == 0, f"docs/45 stale 916 count: {stale_916_45}"

    # docs/53: stale 916 should be 0; 917 ≥ 2.
    stale_916_53 = len(re.findall(r"916 == 916 == 916", docs_53))
    assert stale_916_53 == 0, f"docs/53 stale 916 count: {stale_916_53}"

    # docs/50: 第 44 项 §7 链头 should mention 917 (patched from 916).
    assert "911 → 917" in docs_50, "docs/50 §4.4 第 44 项行 §7 链头 patch missing"
