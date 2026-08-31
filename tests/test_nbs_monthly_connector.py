#!/usr/bin/env python3
"""Stage 1 / S1.4 — tests for backend/src/china_platform/connectors/nbs_monthly.py.

Per Cursor 36 §NOW + docs/18-stage1-s14-nbs-connector-plan-20260824.md §7:
  * hash — compute_sha256 reproducible across calls
  * obs count — extract() returns ≥1 observation from sample.html
  * ingest_run status — ingest() writes ingestion_run row with valid status

Per docs/18 §6 + §5: NO skip; FileNotFoundError → pytest.fail (mandatory).
"""
from __future__ import annotations

import hashlib
import sys
from pathlib import Path

import psycopg2
import psycopg2.errors
import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent

# Make the package importable
sys.path.insert(0, str(REPO_ROOT / "backend" / "src"))

from china_platform.connectors.nbs_monthly import NbsMonthlyConnector  # noqa: E402

# Class-level constants — access via class so we don't import private names
DOMAIN = NbsMonthlyConnector.DEFAULT_REGISTRY_DOMAIN
CATEGORY = NbsMonthlyConnector.DEFAULT_REGISTRY_CATEGORY

# Use the spike 01 sample directly so tests don't require package import dance
SAMPLE_HTML = REPO_ROOT / "spikes" / "01-national-yearbook" / "sample.html"
EXPECTED_SHA = "dea13b8a4ff116ca91403b189cdd60705545b28200f9023c3d56e6db03f3939d"

DSN = "postgresql://postgres:postgres@127.0.0.1:55440/cegr_test"
VALID_STATUSES = {"SUCCESS", "PARTIAL", "FAILED", "RUNNING"}


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
def connector() -> NbsMonthlyConnector:
    return NbsMonthlyConnector()


# ---------------------------------------------------------------------
# Cursor 36 §NOW test 1 — hash reproducibility
# ---------------------------------------------------------------------


def test_compute_sha256_matches_known_digest() -> None:
    """compute_sha256 must match the recorded spike 01 sample SHA-256."""
    if not SAMPLE_HTML.exists():
        pytest.fail(f"mandatory sample missing: {SAMPLE_HTML}")
    h = hashlib.sha256()
    with open(SAMPLE_HTML, "rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            h.update(chunk)
    assert h.hexdigest() == EXPECTED_SHA, (
        f"sample SHA-256 drift: expected={EXPECTED_SHA} got={h.hexdigest()}"
    )


def test_connector_compute_sha256_reproducible(connector) -> None:
    """Calling compute_sha256 on the same file twice returns the same digest."""
    if not SAMPLE_HTML.exists():
        pytest.fail(f"mandatory sample missing: {SAMPLE_HTML}")
    a = connector.compute_sha256(SAMPLE_HTML)
    b = connector.compute_sha256(SAMPLE_HTML)
    assert a == b
    assert len(a) == 64
    assert all(c in "0123456789abcdef" for c in a)


# ---------------------------------------------------------------------
# Cursor 36 §NOW test 2 — extract produces ≥1 observation
# ---------------------------------------------------------------------


def test_extract_returns_observations(connector) -> None:
    """extract() must return a dict with sha256, observations list, metadata.
    Per docs/10 §2.1–2.6 mapping (docs/18 §4): observations have indicator /
    period / value / unit; sample is the 2026-07 NBS monthly bulletin."""
    if not SAMPLE_HTML.exists():
        pytest.fail(f"mandatory sample missing: {SAMPLE_HTML}")
    out = connector.extract(SAMPLE_HTML)
    assert "sha256" in out
    assert "observations" in out
    assert "metadata" in out
    assert out["sha256"] == EXPECTED_SHA
    assert isinstance(out["observations"], list)
    assert len(out["observations"]) >= 1, (
        "spike 01 sample must yield ≥1 observation; if 0, parser regressed"
    )
    # Spot-check observation schema
    first = out["observations"][0]
    assert isinstance(first, dict)
    assert "indicator" in first or "value" in first, (
        f"unexpected observation keys: {list(first.keys())}"
    )
    md = out["metadata"]
    assert md["extraction_method"].startswith("html.parser")
    assert md["file_size_bytes"] == SAMPLE_HTML.stat().st_size


def test_extract_missing_file_raises(connector) -> None:
    """Per docs/18 §5: FileNotFoundError → pytest.fail-equivalent. We assert
    the connector surfaces the FileNotFoundError cleanly (no swallowing)."""
    ghost = REPO_ROOT / "spikes" / "01-national-yearbook" / "_nope.html"
    if ghost.exists():
        pytest.skip(f"unexpected: {ghost} exists")
    with pytest.raises(FileNotFoundError):
        connector.extract(ghost)


# ---------------------------------------------------------------------
# Cursor 36 §NOW test 3 — ingest_run row exists with valid status
# ---------------------------------------------------------------------


def _dsn_conn() -> psycopg2.extensions.connection:
    return psycopg2.connect(DSN)


def _registry_id_for_nbs(conn: psycopg2.extensions.connection) -> str:
    """Resolve the source_registry id used by the connector (NATIONAL_BULLETIN_SPIKE
    after M1 T0 split, 2026-08-31)."""
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
            f"source_registry row for {DOMAIN}/{CATEGORY} missing; "
            "run scripts/import_registry_csv.py first"
        )
    return str(row[0])


# ---------------------------------------------------------------------
# M1 T0 split assertions (2026-08-31)
# ---------------------------------------------------------------------


def test_spike_registry_hash_matches_file_bytes(imported_registry) -> None:
    """Per docs/55 §T0: NATIONAL_BULLETIN_SPIKE row file_hash_sha256 must equal
    spikes/01-national-yearbook/sample.html bytes. This is the invariant the
    M0.3 split restores: SHA=file bytes for any row that claims a local sample."""
    if not SAMPLE_HTML.exists():
        pytest.fail(f"mandatory sample missing: {SAMPLE_HTML}")
    conn = _dsn_conn()
    try:
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT file_hash_sha256, file_size_bytes, local_sample_path
                FROM cegr.source_registry
                WHERE domain = %s AND category = 'NATIONAL_BULLETIN_SPIKE'
                LIMIT 1
                """,
                (DOMAIN,),
            )
            row = cur.fetchone()
        assert row is not None, (
            "NATIONAL_BULLETIN_SPIKE row missing — M1 T0 split not applied; "
            "re-run scripts/import_registry_csv.py"
        )
        reg_hash, reg_size, reg_path = row
        assert reg_path == "spikes/01-national-yearbook/sample.html"
        assert reg_hash == EXPECTED_SHA, (
            f"SPIKE hash drift: registry={reg_hash} file={EXPECTED_SHA}"
        )
        assert reg_size == SAMPLE_HTML.stat().st_size, (
            f"SPIKE size drift: registry={reg_size} "
            f"file={SAMPLE_HTML.stat().st_size}"
        )
    finally:
        conn.close()


def test_live_registry_no_local_sample(imported_registry) -> None:
    """Per docs/55 §T0: NATIONAL_BULLETIN (live) row must have empty
    local_sample_path; it is now live-only and the file hash 180165 B is a
    2026-08-27 live snapshot, not the local sample.html hash."""
    conn = _dsn_conn()
    try:
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT local_sample_path, file_hash_sha256, file_size_bytes,
                       purpose_note
                FROM cegr.source_registry
                WHERE domain = %s AND category = 'NATIONAL_BULLETIN'
                LIMIT 1
                """,
                (DOMAIN,),
            )
            row = cur.fetchone()
        assert row is not None, "NATIONAL_BULLETIN live row missing"
        live_path, live_hash, live_size, live_note = row
        assert live_path in (None, ""), (
            f"NATIONAL_BULLETIN live row still claims local_sample_path={live_path!r}; "
            "M1 T0 split requires this be empty (live-only)"
        )
        # Live row keeps the 2026-08-27 snapshot hash+size verbatim per docs/55 §T0.
        assert live_hash == (
            "a7e4029df707918a552ad2580e8088a945bfe43ec3a2447742553258d0f1f8eb"
        ), f"NATIONAL_BULLETIN live hash drift: {live_hash}"
        assert live_size == 180165, (
            f"NATIONAL_BULLETIN live size drift: {live_size}"
        )
        assert "live-only" in (live_note or "").lower(), (
            f"NATIONAL_BULLETIN purpose_note must mention live-only: {live_note!r}"
        )
    finally:
        conn.close()


def test_ingest_writes_ingestion_run_with_valid_status(
    connector, imported_registry
) -> None:
    """ingest() writes a cegr.ingestion_run row with status in
    {SUCCESS, PARTIAL, FAILED}. S1.4 pilot: observation FK is expected to fail
    (no reference data yet) so PARTIAL is the honest outcome; this test only
    asserts the row exists with a valid enum status."""
    if not SAMPLE_HTML.exists():
        pytest.fail(f"mandatory sample missing: {SAMPLE_HTML}")

    conn = _dsn_conn()
    try:
        sr_id = _registry_id_for_nbs(conn)
        summary = connector.ingest(
            SAMPLE_HTML, conn, triggered_by="test_nbs_monthly_connector"
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
    finally:
        conn.close()


def test_ingest_records_inserted_le_records_extracted(
    connector, imported_registry
) -> None:
    """Defense-in-depth: in S1.4 pilot (no reference data), observation INSERTs
    must fail FK. So records_inserted ≤ records_extracted. If it ever equals
    records_extracted, reference data was seeded and S1.4 pilot scope evolved —
    update docs/18 §3."""
    if not SAMPLE_HTML.exists():
        pytest.fail(f"mandatory sample missing: {SAMPLE_HTML}")

    conn = _dsn_conn()
    try:
        _registry_id_for_nbs(conn)  # ensures registry imported
        summary = connector.ingest(
            SAMPLE_HTML, conn, triggered_by="test_nbs_monthly_connector"
        )
        assert summary["records_inserted"] <= summary["records_extracted"]
        # When FK fails for all rows (expected in S1.4 pilot), status='FAILED';
        # when reference data lands, the connector transitions to SUCCESS/PARTIAL.
        if summary["records_inserted"] == 0:
            # PARTIAL is also valid: source_document persisted, obs FK failed.
            assert summary["status"] in {"PARTIAL", "FAILED"}, (
                f"0 inserted but status={summary['status']!r}; expected PARTIAL/FAILED"
            )
    finally:
        conn.close()