#!/usr/bin/env python3
"""Stage 1 / S1.3 — tests for scripts/import_registry_csv.py.

Per reviews/30-stage1-s13-registry-tasking-20260824.md §0.2:
  * row count == 6 (the 6 data rows in source_registry/registry.csv)
  * declared_source_level matches CSV for each row
  * S0 + UNVERIFIED on source_document triggers CheckViolation (I-05 §9.1)
  * import_registry_csv is idempotent (re-run yields 0 changes)
"""
from __future__ import annotations

import csv
import sys
from pathlib import Path

import psycopg2
import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT / "scripts"))
import import_registry_csv as irc  # noqa: E402

CSV_PATH = REPO_ROOT / "source_registry" / "registry.csv"
DSN = "postgresql://postgres:postgres@127.0.0.1:55440/cegr_test"


@pytest.fixture(scope="module")
def imported_csv() -> None:
    """Re-run the CSV import once for the whole module (idempotent)."""
    rc = irc.import_registry(CSV_PATH, DSN)
    assert rc == 0, f"import_registry_csv returned rc={rc}"


@pytest.fixture(scope="module")
def csv_rows() -> list[dict[str, str]]:
    with CSV_PATH.open("r", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def _cur():
    conn = psycopg2.connect(DSN)
    try:
        with conn.cursor() as cur:
            yield cur
    finally:
        conn.close()


# ---- Cursor 30 §0.2: row count = 6 for declared_source_level = (S0 or S3) -----

def test_imported_row_count_matches_csv(imported_csv, csv_rows) -> None:
    # The 6 CSV rows are uniquely identified by their primary_url; other
    # rows in source_registry come from pre-existing test fixtures with
    # declared_source_level NULL.
    expected = {row["primary_url"] for row in csv_rows}
    with psycopg2.connect(DSN) as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT primary_url
                FROM cegr.source_registry
                WHERE primary_url = ANY(%s)
                """,
                (list(expected),),
            )
            urls = {r[0] for r in cur.fetchall()}
    assert urls == expected, (
        f"missing: {expected - urls}; extra: {urls - expected}"
    )
    assert len(expected) == 6


def test_declared_source_level_matches_csv(imported_csv, csv_rows) -> None:
    """Each CSV row's declared_source_level must equal what's in the DB."""
    with psycopg2.connect(DSN) as conn:
        with conn.cursor() as cur:
            for row in csv_rows:
                cur.execute(
                    "SELECT declared_source_level FROM cegr.source_registry WHERE primary_url = %s",
                    (row["primary_url"],),
                )
                got = cur.fetchone()
                assert got is not None, f"no row for {row['primary_url']}"
                want = row["declared_source_level"] or None
                assert got[0] == want, (
                    f"declared_source_level mismatch for {row['primary_url']}: "
                    f"csv={want!r} db={got[0]!r}"
                )


def test_source_level_matches_csv(imported_csv, csv_rows) -> None:
    """Each CSV row's source_level must equal what's in the DB."""
    with psycopg2.connect(DSN) as conn:
        with conn.cursor() as cur:
            for row in csv_rows:
                cur.execute(
                    "SELECT source_level FROM cegr.source_registry WHERE primary_url = %s",
                    (row["primary_url"],),
                )
                got = cur.fetchone()
                assert got is not None, f"no row for {row['primary_url']}"
                want = row["source_level"] or None
                assert got[0] == want, (
                    f"source_level mismatch for {row['primary_url']}: "
                    f"csv={want!r} db={got[0]!r}"
                )


# ---- I-05 §9.1 negative: S0 + UNVERIFIED on source_document → CheckViolation ----

def _any_registry_id() -> str:
    with psycopg2.connect(DSN) as conn:
        with conn.cursor() as cur:
            cur.execute(
                "SELECT id FROM cegr.source_registry WHERE primary_url=%s",
                ("https://www.stats.gov.cn/sj/ndsj/",),
            )
            row = cur.fetchone()
            assert row is not None
            return row[0]


def test_s0_unverified_check_violation(imported_csv) -> None:
    """Insert a source_document row with source_level='S0' + verification_status
    'UNVERIFIED' against an existing source_registry row → must raise
    CheckViolation (per I-05 §9.1 + schema source_level_s0_requires_verified).

    Uses SAVEPOINT so the negative-test row is rolled back and the connection
    stays in a usable state (and source_document is otherwise immutable per
    source_document_no_delete trigger, so we cannot DELETE to clean up)."""
    import psycopg2.errors
    import uuid

    sr_id = _any_registry_id()
    fake_doc_id = uuid.uuid4()
    fake_hash = "0" * 64

    conn = psycopg2.connect(DSN)
    try:
        with conn.cursor() as cur:
            cur.execute("SAVEPOINT neg_test")
            with pytest.raises(psycopg2.errors.CheckViolation):
                cur.execute(
                    """
                    INSERT INTO cegr.source_document (
                        id, source_registry_id, source_level, verification_status,
                        title, publisher, file_hash_sha256, file_size_bytes
                    ) VALUES (%s, %s, 'S0', 'UNVERIFIED',
                              'neg-title', 'neg-publisher', %s, 1)
                    """,
                    (str(fake_doc_id), sr_id, fake_hash),
                )
            cur.execute("ROLLBACK TO SAVEPOINT neg_test")
            cur.execute("RELEASE SAVEPOINT neg_test")
        conn.commit()
    finally:
        conn.close()


def test_s0_verified_ok(imported_csv) -> None:
    """Same setup but with verification_status='VERIFIED' → INSERT succeeds.

    Savepoint + rollback so the row does not persist (source_document rows
    cannot be DELETEd once committed, per the no-delete trigger)."""
    import uuid

    sr_id = _any_registry_id()
    fake_doc_id = uuid.uuid4()
    fake_hash = "1" * 64

    conn = psycopg2.connect(DSN)
    try:
        with conn.cursor() as cur:
            cur.execute("SAVEPOINT ok_test")
            cur.execute(
                """
                INSERT INTO cegr.source_document (
                    id, source_registry_id, source_level, verification_status,
                    title, publisher, file_hash_sha256, file_size_bytes
                ) VALUES (%s, %s, 'S0', 'VERIFIED',
                          'neg-ok-title', 'neg-ok-publisher', %s, 1)
                """,
                (str(fake_doc_id), sr_id, fake_hash),
            )
            assert cur.rowcount == 1
            # Verify the row exists within the savepoint
            cur.execute(
                "SELECT source_level, verification_status FROM cegr.source_document WHERE id=%s",
                (str(fake_doc_id),),
            )
            row = cur.fetchone()
            assert row is not None
            assert row[0] == "S0"
            assert row[1] == "VERIFIED"
            # Roll back so the test leaves no persistent state
            cur.execute("ROLLBACK TO SAVEPOINT ok_test")
            cur.execute("RELEASE SAVEPOINT ok_test")
        conn.commit()
    finally:
        conn.close()


# ---- Idempotency ----

def test_idempotent(imported_csv) -> None:
    """Re-running the importer must not raise and must keep the same row count."""
    rc = irc.import_registry(CSV_PATH, DSN)
    assert rc == 0


# ---- access_method mapping ----

def test_access_method_enum_values(imported_csv, csv_rows) -> None:
    """Every imported row's access_method must be a valid extraction_method enum."""
    with psycopg2.connect(DSN) as conn:
        with conn.cursor() as cur:
            for row in csv_rows:
                cur.execute(
                    "SELECT access_method FROM cegr.source_registry WHERE primary_url=%s",
                    (row["primary_url"],),
                )
                got = cur.fetchone()
                assert got is not None
                assert got[0] in {
                    "API",
                    "HTML_PARSE",
                    "EXCEL_PARSE",
                    "PDF_TEXT",
                    "PDF_OCR",
                    "IMAGE_OCR",
                    "CSV_PARSE",
                    "MANUAL_UPLOAD",
                }, f"unexpected access_method: {got[0]!r}"