#!/usr/bin/env python3
"""Stage 1 / S1.7 — tests for backend/src/china_platform/connectors/scanned_pdf_ocr.py.

Per Cursor 56 §NOW + docs/21-stage1-s17-scanned-pdf-ocr-plan-20260825.md §7:
  * hash — compute_sha256 reproducible AND matches spike 04 provenance.json
  * extract ≥1 page — Shaanxi sample → 4 page observations
  * needs_review / caveat_text 语义 — per-page granularity; value=NULL +
    missing_reason='NOT_NUMERIC_SOURCE'; notes JSON 含 research_track +
    not_statistical_table + han_agreement_pending_evaluation;
    caveat_text mentions research_track
  * ingest_run status — ingest() writes ingestion_run row with valid status;
    records_inserted ≤ records_extracted (FK placeholder → PARTIAL/FAILED)

Additional red-line tests:
  * fail 透传 on missing tool (per Cursor 56 §NOW step 3)
  * period_* all NULL (Shaanxi 法规≠数据周期)
  * value_type='FACT' (enum 无 DEFINITION; Cursor 55 §1 备注)
  * lineage JSONB 含 render_dpi + ocr_language + psm + embedded_text_layer_used
  * 1909 fallback raises NotImplementedError (per Cursor 56 §SCHEMA 决策 6)

Per docs/21 §6: NO skip; FileNotFoundError / missing tools → fail 透传.
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

import psycopg2
import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent

# Make the package importable
sys.path.insert(0, str(REPO_ROOT / "backend" / "src"))

from china_platform.connectors.scanned_pdf_ocr import (  # noqa: E402
    ScannedPdfOcrConnector,
)

# Class-level constants — access via class so we don't import private names
DOMAIN = ScannedPdfOcrConnector.DEFAULT_REGISTRY_DOMAIN
CATEGORY = ScannedPdfOcrConnector.DEFAULT_REGISTRY_CATEGORY

# Spike 04 sample — single sample used by the S1.7 pilot (research track)
SAMPLE_PDF = REPO_ROOT / "spikes" / "04-scanned-pdf" / "data" / "shaanxi_fiscal_regulation_flk.pdf"
EXPECTED_SHA = (
    "f34b2e57ae08620cb6a6afb98b3983d805d53e3bae78b969795987a7ebe71488"
)

DSN = "postgresql://postgres:postgres@127.0.0.1:55440/cegr_test"
VALID_STATUSES = {"SUCCESS", "PARTIAL", "FAILED", "RUNNING"}

# Allowed value_type enum values (Cursor 55 §1 备注: 无 DEFINITION)
ALLOWED_VALUE_TYPES = {"FACT"}

# Allowed observation.status values
ALLOWED_OBS_STATUSES = {"PRELIMINARY", "VERIFIED", "SUPERSEDED", "REJECTED"}

# Per-page needs_review heuristic threshold (must mirror connector constant)
NEEDS_REVIEW_CONFIDENCE_THRESHOLD = 60.0


# ---------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------


@pytest.fixture(scope="module")
def imported_registry() -> None:
    """Re-run the CSV import once for the whole module (idempotent)."""
    sys.path.insert(0, str(REPO_ROOT / "scripts"))
    import import_registry_csv as irc  # noqa: E402

    csv_path = REPO_ROOT / "source_registry" / "registry.csv"
    rc = irc.import_registry(csv_path, DSN)
    assert rc == 0, f"import_registry_csv returned rc={rc}"


@pytest.fixture
def connector() -> ScannedPdfOcrConnector:
    return ScannedPdfOcrConnector()


@pytest.fixture
def extracted(connector):
    """Run extract() once for the module's tests that need observations."""
    if not SAMPLE_PDF.exists():
        pytest.fail(f"mandatory sample missing: {SAMPLE_PDF}")
    return connector.extract(SAMPLE_PDF)


# ---------------------------------------------------------------------
# Cursor 56 §NOW test 1 — hash reproducibility + provenance match
# ---------------------------------------------------------------------


def test_compute_sha256_matches_provenance(connector) -> None:
    """compute_sha256 must match spike 04 provenance.json sample SHA-256.

    Per docs/21 §3: "Source Document provenance verification" is mandatory
    before source_document INSERT (source_level=S0, verification_status=VERIFIED).
    """
    if not SAMPLE_PDF.exists():
        pytest.fail(f"mandatory sample missing: {SAMPLE_PDF}")
    assert connector.compute_sha256(SAMPLE_PDF) == EXPECTED_SHA, (
        f"sample SHA-256 drift: expected={EXPECTED_SHA}"
    )


def test_connector_compute_sha256_reproducible(connector) -> None:
    """Calling compute_sha256 on the same file twice returns the same digest."""
    if not SAMPLE_PDF.exists():
        pytest.fail(f"mandatory sample missing: {SAMPLE_PDF}")
    a = connector.compute_sha256(SAMPLE_PDF)
    b = connector.compute_sha256(SAMPLE_PDF)
    assert a == b
    assert len(a) == 64
    assert all(c in "0123456789abcdef" for c in a)


def test_provenance_sha256_matches_known_digest() -> None:
    """spike 04 provenance.json research_samples.shaanxi_fiscal_regulation_flk
    must carry the same SHA-256 — local origin guard against silent re-fetch."""
    provenance_path = REPO_ROOT / "spikes" / "04-scanned-pdf" / "provenance.json"
    if not provenance_path.exists():
        pytest.fail(f"provenance.json missing: {provenance_path}")
    prov = json.loads(provenance_path.read_text(encoding="utf-8"))
    sample = prov["research_samples"]["shaanxi_fiscal_regulation_flk"]
    assert sample["file_hash_sha256"] == EXPECTED_SHA, (
        f"provenance.json SHA drift: expected={EXPECTED_SHA} "
        f"got={sample['file_hash_sha256']}"
    )
    assert sample["source_url"] == (
        "https://wb.flk.npc.gov.cn/dfxfg/PDF/"
        "d31411b562fc4226a7465f1c875afe67.pdf"
    )


# ---------------------------------------------------------------------
# Cursor 56 §NOW test 2 — extract ≥1 page
# ---------------------------------------------------------------------


def test_extract_returns_page_observations(extracted) -> None:
    """extract() returns ≥1 observation. Shaanxi sample → 4 page observations
    (per Cursor 56 §SCHEMA 决策 1: per-page granularity)."""
    assert "sha256" in extracted
    assert "observations" in extracted
    assert "metadata" in extracted
    assert "lineage" in extracted
    assert extracted["sha256"] == EXPECTED_SHA
    assert isinstance(extracted["observations"], list)
    assert len(extracted["observations"]) >= 1, (
        "Shaanxi sample must yield ≥1 page observation; if 0, "
        "spike 04 OCR regressed or tesseract/chi_sim missing"
    )
    md = extracted["metadata"]
    assert md["track"] == "shaanxi_chinese_text"
    assert md["extraction_method"].startswith("pdftoppm")
    assert md["file_size_bytes"] == SAMPLE_PDF.stat().st_size
    assert md["page_observations"] == len(extracted["observations"])


def test_extract_page_count_matches_pdf(extracted) -> None:
    """Shaanxi sample is 4 pages per spike 04 README; extract should
    yield exactly 4 page observations (one per PDF page)."""
    pdf_pages = extracted["metadata"]["pdf_pages_total"]
    assert len(extracted["observations"]) == pdf_pages, (
        f"page-obs count ({len(extracted['observations'])}) must match "
        f"PDF pages ({pdf_pages})"
    )


def test_extract_missing_file_raises(connector) -> None:
    """Per docs/21 §5: FileNotFoundError surfaces cleanly (no swallowing)."""
    ghost = REPO_ROOT / "spikes" / "04-scanned-pdf" / "data" / "_nope.pdf"
    if ghost.exists():
        pytest.skip(f"unexpected: {ghost} exists")
    with pytest.raises(FileNotFoundError):
        connector.extract(ghost)


# ---------------------------------------------------------------------
# Cursor 56 §NOW test 3 — needs_review / caveat_text 语义
# (per-page granularity; value=NULL + missing_reason='NOT_NUMERIC_SOURCE';
#  notes 含 research_track + not_statistical_table + han_agreement_pending_evaluation)
# ---------------------------------------------------------------------


def test_per_page_granularity(extracted) -> None:
    """Per Cursor 56 §SCHEMA 决策 1: Shaanxi obs 粒度 = per-page (1 obs/page).
    Each obs must carry page_pdf_1indexed 1..N with no gaps."""
    rows = extracted["observations"]
    page_idxs = sorted(r["page_pdf_1indexed"] for r in rows)
    assert page_idxs == list(range(1, len(rows) + 1)), (
        f"per-page granularity violated; got page_idxs={page_idxs}"
    )


def test_value_is_null_with_not_numeric_source(extracted) -> None:
    """Per Cursor 56 §SCHEMA 决策 2: value=NULL + missing_reason='NOT_NUMERIC_SOURCE'
    for every Shaanxi observation. value_type='FACT' (enum 无 DEFINITION)."""
    for r in extracted["observations"]:
        assert r["value"] is None, (
            f"page {r['page_pdf_1indexed']}: value must be NULL for "
            f"Shaanxi research track; got {r['value']!r}"
        )
        assert r["missing_reason"] == "NOT_NUMERIC_SOURCE", (
            f"page {r['page_pdf_1indexed']}: missing_reason must be "
            f"'NOT_NUMERIC_SOURCE'; got {r['missing_reason']!r}"
        )
        assert r["value_type"] in ALLOWED_VALUE_TYPES, (
            f"page {r['page_pdf_1indexed']}: value_type must be FACT "
            f"(enum has no DEFINITION per Cursor 55 §1 备注); "
            f"got {r['value_type']!r}"
        )


def test_period_columns_all_null(extracted) -> None:
    """Per Cursor 56 §SCHEMA 决策 3: Shaanxi period_* = NULL
    (法规 != 数据周期; release date ≠ reporting period)."""
    for r in extracted["observations"]:
        assert r["period_start"] is None, (
            f"page {r['page_pdf_1indexed']}: period_start must be NULL"
        )
        assert r["period_end"] is None, (
            f"page {r['page_pdf_1indexed']}: period_end must be NULL"
        )
        assert r["period_label"] is None, (
            f"page {r['page_pdf_1indexed']}: period_label must be NULL"
        )
        assert r["period_type"] is None, (
            f"page {r['page_pdf_1indexed']}: period_type must be NULL"
        )


def test_notes_json_research_track_flags(extracted) -> None:
    """Per Cursor 56 §SCHEMA 决策 2: notes JSON must explicitly mark
    research_track + not_statistical_table + han_agreement_pending_evaluation
    so downstream consumers understand this is NOT statistical-table data."""
    for r in extracted["observations"]:
        notes = json.loads(r["notes"])
        assert notes["research_track"] is True
        assert notes["not_statistical_table"] is True
        assert notes["han_agreement_pending_evaluation"] is True
        assert notes["page_pdf_1indexed"] == r["page_pdf_1indexed"]
        assert "word_count" in notes
        assert "mean_word_confidence" in notes
        assert "needs_review" in notes
        assert "render_dpi" in notes
        assert "ocr_language" in notes


def test_caveat_text_explains_research_track(extracted) -> None:
    """caveat_text must explicitly mention Shaanxi research track + NOT
    statistical-table representative (per Cursor 56 §SCHEMA 决策 2).
    Status stays PRELIMINARY; review is content, not lifecycle."""
    for r in extracted["observations"]:
        caveat = r["caveat_text"]
        assert "Shaanxi research track" in caveat, (
            f"page {r['page_pdf_1indexed']}: caveat_text must mention "
            f"Shaanxi research track"
        )
        assert "NOT a statistical-table representative" in caveat, (
            f"page {r['page_pdf_1indexed']}: caveat_text must clarify NOT "
            f"statistical-table representative"
        )
        assert "han_agreement_pending_evaluation" in caveat


def test_needs_review_heuristic_threshold(extracted) -> None:
    """needs_review is set per-page using mean_word_confidence < 60.0
    heuristic. NOT a replacement for Han agreement evaluation (which needs
    ground truth; flagged via han_agreement_pending_evaluation=true)."""
    for r in extracted["observations"]:
        notes = json.loads(r["notes"])
        mean_conf = notes["mean_word_confidence"]
        if mean_conf is None:
            # No OCR output — connector sets needs_review=True
            assert notes["needs_review"] is True
            assert notes["needs_review_reason"] == "low_mean_word_confidence"
        elif mean_conf < NEEDS_REVIEW_CONFIDENCE_THRESHOLD:
            assert notes["needs_review"] is True
            assert notes["needs_review_reason"] == "low_mean_word_confidence"
        else:
            assert notes["needs_review"] is False
            assert notes["needs_review_reason"] is None


def test_lineage_jsonb_extended_keys(extracted) -> None:
    """Per Cursor 56 §SCHEMA 决策 4: bbox/dpi etc. enter lineage JSONB as
    extension keys (no migration 005). Required keys for OCR track:
    chain_id, source_file_sha256, source_file_url, extractor_version,
    render_dpi, ocr_language, ocr_psm, embedded_text_layer_used."""
    for r in extracted["observations"]:
        lin = r["lineage"]
        assert isinstance(lin, dict), f"lineage must be dict, got {type(lin)}"
        for k in (
            "chain_id",
            "source_file_sha256",
            "source_file_url",
            "extractor_version",
            "render_dpi",
            "ocr_language",
            "ocr_psm",
            "embedded_text_layer_used",
            "page_pdf_1indexed",
        ):
            assert k in lin, f"lineage missing key {k!r}"
        assert lin["source_file_sha256"] == EXPECTED_SHA
        assert lin["embedded_text_layer_used"] is False
        assert "shaanxi-flk-2026-page" in lin["chain_id"]
        assert r["page_pdf_1indexed"] == lin["page_pdf_1indexed"]


def test_raw_value_is_page_text(extracted) -> None:
    """raw_value is OCR text of the page (concatenated left+right region
    canonical_lines). Per-page granularity means raw_value text differs
    across pages — at minimum, ≥2 distinct raw_values."""
    raw_values = [r["raw_value"] for r in extracted["observations"]]
    distinct = len(set(raw_values))
    assert distinct >= 2, (
        f"per-page raw_value should differ across pages; "
        f"only {distinct} distinct values"
    )


# ---------------------------------------------------------------------
# Cursor 56 §NOW step 3 — fail 透传 on missing tool
# ---------------------------------------------------------------------


def test_missing_toolchain_fails_loudly(connector, monkeypatch) -> None:
    """Per Cursor 56 §NOW step 3: 缺 tesseract/pdftoppm → fail 透传
    (不 skip-as-PASS). We simulate by pointing require_tools to a non-existent
    binary directory; expect RuntimeError propagation, NOT silent skip."""
    # Build a temporary directory that shadows tesseract — but spike 04's
    # require_tools checks PATH. Simplest approach: monkeypatch require_tools
    # to raise RuntimeError, and assert connector.extract() surfaces it.
    import extract_04_shaanxi_text as spike04
    original_require_tools = spike04.require_tools
    spike04.require_tools = lambda: (_ for _ in ()).throw(
        RuntimeError("simulated: tesseract missing")
    )
    try:
        with pytest.raises(RuntimeError, match="tesseract missing"):
            connector.extract(SAMPLE_PDF)
    finally:
        spike04.require_tools = original_require_tools


# ---------------------------------------------------------------------
# Cursor 56 §SCHEMA 决策 6 — 1909 fallback raises NotImplementedError
# ---------------------------------------------------------------------


def test_1909_fallback_raises_not_implemented(connector, monkeypatch) -> None:
    """Per Cursor 56 §SCHEMA 决策 6: 1909 fallback is code-retained but
    NOT default-tested. Switching DEFAULT_TRACK should raise
    NotImplementedError (not silently invoke the BLOCKED track)."""
    monkeypatch.setattr(
        ScannedPdfOcrConnector, "DEFAULT_TRACK", "numeric_table_1909",
        raising=False,
    )
    with pytest.raises(NotImplementedError, match="1909"):
        connector.extract(SAMPLE_PDF)


# ---------------------------------------------------------------------
# Cursor 56 §NOW test 4 — ingest_run status
# ---------------------------------------------------------------------


def _dsn_conn() -> psycopg2.extensions.connection:
    return psycopg2.connect(DSN)


def _registry_id_for_flk(conn: psycopg2.extensions.connection) -> str:
    """Resolve the source_registry id used by the connector."""
    with conn.cursor() as cur:
        cur.execute(
            """
            SELECT id FROM cegr.source_registry
            WHERE domain = %s AND category = %s
            LIMIT 1
            """,
            (DOMAIN, CATEGORY),
        )
        row = cur.fetchone()
    if row is None:
        pytest.fail(
            "source_registry row for wb.flk.npc.gov.cn / SCANNED_PDF_RESEARCH "
            "missing; run scripts/import_registry_csv.py first"
        )
    return str(row[0])


def test_ingest_writes_ingestion_run_with_valid_status(
    connector, imported_registry
) -> None:
    """ingest() writes a cegr.ingestion_run row with status in
    {SUCCESS, PARTIAL, FAILED}. S1.7 pilot: observation FK is expected to
    fail (no reference data yet) so PARTIAL/FAILED is the honest outcome;
    this test only asserts the row exists with a valid enum status."""
    if not SAMPLE_PDF.exists():
        pytest.fail(f"mandatory sample missing: {SAMPLE_PDF}")

    conn = _dsn_conn()
    try:
        _registry_id_for_flk(conn)  # ensures registry imported
        summary = connector.ingest(
            SAMPLE_PDF, conn, triggered_by="test_scanned_pdf_ocr_connector"
        )
        assert summary["status"] in VALID_STATUSES, (
            f"unexpected ingest status: {summary['status']!r}"
        )
        assert summary["records_extracted"] >= 1
        # Verify the ingestion_run row exists in the DB
        with conn.cursor() as cur:
            cur.execute(
                "SELECT status, records_extracted, records_inserted "
                "FROM cegr.ingestion_run WHERE id = %s",
                (summary["ingestion_run_id"],),
            )
            row = cur.fetchone()
        assert row is not None, (
            f"ingestion_run row vanished: {summary['ingestion_run_id']}"
        )
        db_status, db_extracted, db_inserted = row
        assert db_status == summary["status"]
        assert db_extracted == summary["records_extracted"]
        assert db_inserted == summary["records_inserted"]
        # Verify source_document row exists with verification_status=VERIFIED
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT source_level, verification_status, extraction_method,
                       file_hash_sha256
                FROM cegr.source_document WHERE id = %s
                """,
                (summary["source_document_id"],),
            )
            doc_row = cur.fetchone()
        assert doc_row is not None, "source_document row missing"
        doc_level, doc_status, doc_method, doc_sha = doc_row
        assert doc_level == "S0"
        assert doc_status == "VERIFIED"
        assert doc_method == "PDF_OCR"
        assert doc_sha == EXPECTED_SHA
    finally:
        conn.close()


def test_ingest_records_inserted_le_records_extracted(
    connector, imported_registry
) -> None:
    """Defense-in-depth: in S1.7 pilot (no reference data), observation
    INSERTs must fail FK. So records_inserted ≤ records_extracted. If it
    ever equals records_extracted, reference data was seeded and S1.7 pilot
    scope evolved — update docs/21 §3."""
    if not SAMPLE_PDF.exists():
        pytest.fail(f"mandatory sample missing: {SAMPLE_PDF}")

    conn = _dsn_conn()
    try:
        _registry_id_for_flk(conn)  # ensures registry imported
        summary = connector.ingest(
            SAMPLE_PDF, conn, triggered_by="test_scanned_pdf_ocr_connector"
        )
        assert summary["records_inserted"] <= summary["records_extracted"]
        if summary["records_inserted"] == 0:
            # 0 inserted but ≥1 extracted → PARTIAL or FAILED
            assert summary["status"] in {"PARTIAL", "FAILED"}, (
                f"0 inserted but status={summary['status']!r}; "
                f"expected PARTIAL/FAILED"
            )
    finally:
        conn.close()


# ---------------------------------------------------------------------
# Red line — no Chinese in DB-bound fields that pass through FK resolution
# (Cursor 55 §1 备注: 指示词 canonical → snake_case; observation has no
#  indicator_canonical field, but raw_value text may mirror source content
#  for OCR; this test pins that we do NOT classify raw_value as
#  numeric-table content.)
# ---------------------------------------------------------------------


def test_raw_value_not_numeric_table_content(extracted) -> None:
    """Per Cursor 56 §SCHEMA 决策 2 + 决策 5: Shaanxi raw_value is OCR text of
    legal regulation pages (NOT a statistical-table representative). Each
    raw_value is flagged NOT_NUMERIC_SOURCE + notes.not_statistical_table=true."""
    for r in extracted["observations"]:
        # raw_value text length should be substantial (Chinese legal text,
        # not a numeric value)
        assert len(r["raw_value"]) > 50, (
            f"page {r['page_pdf_1indexed']}: raw_value suspiciously short "
            f"({len(r['raw_value'])} chars); expected OCR text of a legal "
            f"regulation page"
        )
        assert r["missing_reason"] == "NOT_NUMERIC_SOURCE"