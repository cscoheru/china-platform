#!/usr/bin/env python3
"""Stage 1 / S1.5 — tests for backend/src/china_platform/connectors/sz_municipal_bulletin.py.

Per Cursor 44 §NOW + docs/19-stage1-s15-shenzhen-bulletin-plan-20260824.md §7:
  * hash — compute_sha256 reproducible across calls
  * obs count — extract() returns ≥1 observation from sample.html
  * ingest_run status — ingest() writes ingestion_run row with valid status

Per docs/19 §6 + §5: NO skip; FileNotFoundError → pytest.fail (mandatory).
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

from china_platform.connectors.sz_municipal_bulletin import (  # noqa: E402
    SzMunicipalBulletinConnector,
)

# Class-level constants
DOMAIN = SzMunicipalBulletinConnector.DEFAULT_REGISTRY_DOMAIN
CATEGORY = SzMunicipalBulletinConnector.DEFAULT_REGISTRY_CATEGORY

# Use the spike 03 sample directly so tests don't require package import dance
SAMPLE_HTML = REPO_ROOT / "spikes" / "03-municipal-bulletin" / "sample.html"
EXPECTED_SHA = "d5e2c73196b43cecc8efa20e174d30bf78c382e21a1cda956f0637aeb9022d29"

DSN = "postgresql://postgres:postgres@127.0.0.1:55440/cegr_test"
VALID_STATUSES = {"SUCCESS", "PARTIAL", "FAILED", "RUNNING"}

# spike 03 observed unit set (per docs/10 §2.1 / docs/19 §4)
EXPECTED_UNITS = {"亿元", "%", "万人", "元"}


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
def connector() -> SzMunicipalBulletinConnector:
    return SzMunicipalBulletinConnector()


# ---------------------------------------------------------------------
# Cursor 44 §NOW test 1 — hash reproducibility
# ---------------------------------------------------------------------


def test_compute_sha256_matches_known_digest() -> None:
    """compute_sha256 must match the recorded spike 03 sample SHA-256."""
    if not SAMPLE_HTML.exists():
        pytest.fail(f"mandatory sample missing: {SAMPLE_HTML}")
    data = SAMPLE_HTML.read_bytes()
    h = hashlib.sha256(data).hexdigest()
    assert h == EXPECTED_SHA, (
        f"sample SHA-256 drift: expected={EXPECTED_SHA} got={h}"
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
# Cursor 44 §NOW test 2 — extract produces ≥1 observation
# ---------------------------------------------------------------------


def test_extract_returns_observations(connector) -> None:
    """extract() returns dict with sha256 + observations + metadata.
    Per docs/19 §4 (docs/10 §2.1 mapping): spike 03 sample yields 8 obs
    (GDP / 人口 / 固投 / 零售 / 进出口 / 人均 / 财政 / 固投增速)."""
    if not SAMPLE_HTML.exists():
        pytest.fail(f"mandatory sample missing: {SAMPLE_HTML}")
    out = connector.extract(SAMPLE_HTML)
    assert "sha256" in out
    assert "observations" in out
    assert "metadata" in out
    assert out["sha256"] == EXPECTED_SHA
    assert isinstance(out["observations"], list)
    assert len(out["observations"]) >= 1, (
        "spike 03 sample must yield ≥1 observation; if 0, parser regressed"
    )
    first = out["observations"][0]
    assert isinstance(first, dict)
    # S1.5-specific observation schema (spike 03 + docs/19 §2 extract signature)
    for k in ("indicator", "period", "value", "unit", "source_url", "locator"):
        assert k in first, f"missing key {k!r} in observation: {list(first.keys())}"
    # S1.5增值字段 (per docs/19 §4 + Cursor 43 §1 备注)
    assert "comparison_basis" in first
    assert "context_quote" in first
    # 元数据校验
    md = out["metadata"]
    assert md["city"] == "深圳"
    assert md["year"] == 2024
    assert md["extraction_method"].startswith("beautifulsoup")
    assert md["file_size_bytes"] == SAMPLE_HTML.stat().st_size


def test_extract_units_within_expected_set(connector) -> None:
    """Per docs/10 §2.1: observation.unit must be from allowed_units whitelist.
    spike 03 实测单位 ∈ {'亿元', '%', '万人', '元'}."""
    if not SAMPLE_HTML.exists():
        pytest.fail(f"mandatory sample missing: {SAMPLE_HTML}")
    out = connector.extract(SAMPLE_HTML)
    units = {obs.get("unit") for obs in out["observations"]}
    assert units.issubset(EXPECTED_UNITS), (
        f"unexpected units in S1.5 sample: {units - EXPECTED_UNITS}"
    )


def test_extract_missing_file_raises(connector) -> None:
    """Per docs/19 §5: FileNotFoundError → pytest.fail-equivalent. We assert
    the connector surfaces the FileNotFoundError cleanly (no swallowing)."""
    ghost = REPO_ROOT / "spikes" / "03-municipal-bulletin" / "_nope.html"
    if ghost.exists():
        pytest.skip(f"unexpected: {ghost} exists")
    with pytest.raises(FileNotFoundError):
        connector.extract(ghost)


# ---------------------------------------------------------------------
# Cursor 44 §NOW test 3 — ingest_run row exists with valid status
# ---------------------------------------------------------------------


def _dsn_conn() -> psycopg2.extensions.connection:
    return psycopg2.connect(DSN)


def _registry_id_for_sz(conn: psycopg2.extensions.connection) -> str:
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
            "source_registry row for sz.gov.cn/MUNICIPAL_BULLETIN missing; "
            "run scripts/import_registry_csv.py first"
        )
    return str(row[0])


def test_ingest_writes_ingestion_run_with_valid_status(
    connector, imported_registry
) -> None:
    """ingest() writes a cegr.ingestion_run row with status in
    {SUCCESS, PARTIAL, FAILED}. S1.5 pilot: observation FK is expected to
    fail (no reference data yet) so PARTIAL is the honest outcome; this
    test only asserts the row exists with a valid enum status."""
    if not SAMPLE_HTML.exists():
        pytest.fail(f"mandatory sample missing: {SAMPLE_HTML}")

    conn = _dsn_conn()
    try:
        _registry_id_for_sz(conn)  # ensures registry imported
        summary = connector.ingest(
            SAMPLE_HTML, conn, triggered_by="test_sz_municipal_bulletin_connector"
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
    """Defense-in-depth: in S1.5 pilot (no reference data), observation INSERTs
    must fail FK. So records_inserted ≤ records_extracted. If it ever equals
    records_extracted, reference data was seeded and S1.5 pilot scope evolved —
    update docs/19 §3."""
    if not SAMPLE_HTML.exists():
        pytest.fail(f"mandatory sample missing: {SAMPLE_HTML}")

    conn = _dsn_conn()
    try:
        _registry_id_for_sz(conn)  # ensures registry imported
        summary = connector.ingest(
            SAMPLE_HTML, conn, triggered_by="test_sz_municipal_bulletin_connector"
        )
        assert summary["records_inserted"] <= summary["records_extracted"]
        if summary["records_inserted"] == 0:
            # Per docs/19 §5 + §3: 0 obs is SUCCESS (legitimate); 0 inserted
            # with N extracted is PARTIAL or FAILED depending on error log.
            if summary["records_extracted"] > 0:
                assert summary["status"] in {"PARTIAL", "FAILED"}, (
                    f"0 inserted but status={summary['status']!r}; "
                    f"expected PARTIAL/FAILED"
                )
    finally:
        conn.close()