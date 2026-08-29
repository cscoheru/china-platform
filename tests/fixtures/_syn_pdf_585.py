"""Synthesized minimal PDF fixture for knife 585 e2e pytest.

Per docs/49 §5.2.5 (e2e pytest) + 585 tasking §A:
  - Minimum legal PDF byte sequence (header + 1 page object + xref + trailer + EOF)
  - Controlled content marker = "__SYN_PDF_585_E2E__" embedded in body
  - File size < 4 KB (CI/sandbox overhead avoidance)
  - NOT a real PDF (--confirm-o3=PATH = §5.2.6 user-retention action)
  - Does NOT use PyPDF2 / pypdf / pdfplumber (per tasking red line)

This fixture exists only for tests/test_o3_e2e_585.py. It is NOT a real
government document; it is a synthetic byte sequence used to exercise the
validate_ocr_input → doc_kind='OCR_SCAN' → mock paddle-ocr → source_document
mock writer → lineage JSONB assertion chain.
"""
from __future__ import annotations

# Controlled content marker (per 585 tasking §A); embedded in PDF body
# so mock paddle-ocr can extract it deterministically.
SYN_PDF_MARKER = b"__SYN_PDF_585_E2E__"


def make_syn_pdf_bytes(marker: bytes = SYN_PDF_MARKER) -> bytes:
    """Return minimal legal PDF byte sequence with controlled content marker.

    Structure (intentionally minimal):
      - %PDF-1.4 header
      - 1 page catalog + 1 page object (ref 1 0 / 2 0)
      - Content stream with marker embedded
      - xref table (offsets computed)
      - trailer pointing to catalog
      - %%EOF marker
      - Padding comment block to push size >= 1024 bytes (otherwise the
        <1KiB + mtime<7d rule in scripts/intake_real_sha_if_present._is_fixture
        would mis-classify this as a control-flow fixture).
    """
    # Pre-compute relative offsets for xref table.
    # Build pieces first, then assemble with measured offsets.
    header = b"%PDF-1.4\n"
    body_marker = marker + b"\n"
    # Object 1 = Catalog
    obj1 = b"1 0 obj\n<< /Type /Catalog /Pages 2 0 R >>\nendobj\n"
    # Object 2 = Pages (single page)
    obj2 = b"2 0 obj\n<< /Type /Pages /Kids [3 0 R] /Count 1 >>\nendobj\n"
    # Object 3 = Page
    obj3 = (
        b"3 0 obj\n<< /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] "
        b"/Contents 4 0 R /Resources << /Font << /F1 5 0 R >> >> >>\nendobj\n"
    )
    # Object 4 = Content stream (contains the marker)
    content_body = b"BT /F1 12 Tf 72 720 Td (" + body_marker.rstrip(b"\n") + b") Tj ET"
    obj4 = (
        b"4 0 obj\n<< /Length "
        + str(len(content_body)).encode("ascii")
        + b" >>\nstream\n"
        + content_body
        + b"\nendstream\nendobj\n"
    )
    # Object 5 = Font
    obj5 = b"5 0 obj\n<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>\nendobj\n"

    # Compute xref offsets.
    body = obj1 + obj2 + obj3 + obj4 + obj5
    # Padding comment block (just a single %-comment line of sufficient length)
    # to push total size >= 1024 bytes (avoid control-flow fixture rule).
    pad_size = max(0, 1024 - (len(header) + len(body) + 80))  # leave 80 for xref/trailer
    padding = b"%" + (b"x" * pad_size) + b"\n" if pad_size > 1 else b""
    xref_offset = len(header) + len(padding) + len(body)

    xref_lines = [b"xref\n", b"0 6\n", b"0000000000 65535 f \n"]
    # offsets for objects 1-5 relative to start of file
    cur = len(header) + len(padding)
    for obj_bytes in (obj1, obj2, obj3, obj4, obj5):
        xref_lines.append(f"{cur:010d} 00000 n \n".encode("ascii"))
        cur += len(obj_bytes)

    xref = b"".join(xref_lines)
    trailer = (
        b"trailer\n<< /Size 6 /Root 1 0 R >>\nstartxref\n"
        + str(xref_offset).encode("ascii")
        + b"\n%%EOF\n"
    )

    pdf_bytes = header + padding + body + xref + trailer
    assert pdf_bytes.startswith(b"%PDF-")
    assert pdf_bytes.rstrip().endswith(b"%%EOF")
    assert marker in pdf_bytes, "synthetic marker missing from body"
    assert len(pdf_bytes) >= 1024, f"too small: {len(pdf_bytes)} bytes (need >= 1024)"
    assert len(pdf_bytes) < 4096, f"too large: {len(pdf_bytes)} bytes (must be < 4096)"
    return pdf_bytes


__all__ = ["make_syn_pdf_bytes", "SYN_PDF_MARKER"]
