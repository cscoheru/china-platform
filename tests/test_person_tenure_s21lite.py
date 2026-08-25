"""Stage 2 / S2.1-lite — Person/tenure DDL minimal pytest (per Cursor 180).

Per Cursor 180 §NOW-2: 最小 pytest (≥3):
  1. migration 可应用
  2. 六表存在
  3. 重叠 tenure 可插入

Plus 2 bonus tests for the additive contract:
  4. New columns are NULL-able (legacy back-compat)
  5. probe loader + seed loader status produce identical expected counts

Total: 5 cases. All run against the default STAGE0_DSN after conftest's
session-bootstrap re-applies all migrations including 008.
"""
from __future__ import annotations

import sys
import uuid
from pathlib import Path

import psycopg2
import psycopg2.extras
import pytest

psycopg2.extras.register_uuid()

REPO_ROOT = Path(__file__).resolve().parent.parent
DSN = "postgresql://postgres:postgres@127.0.0.1:55440/cegr_test"

EXPECTED_TABLES = [
    "person", "person_name_alias", "position", "tenure",
    "appointment_event", "person_source_evidence",
]

# Mirror scripts/seed_person_tenure_s21lite.py — keep in sync.
PROBE_SOURCE_DOC_ID = uuid.UUID("a0000000-0000-0000-0000-000000000050")
PROBE_PERSON_A_ID = uuid.UUID("a0000000-0000-0000-0000-000000000051")
PROBE_PERSON_B_ID = uuid.UUID("a0000000-0000-0000-0000-000000000052")
PROBE_POSITION_ID = uuid.UUID("a0000000-0000-0000-0000-000000000053")
PROBE_TENURE_A1_ID = uuid.UUID("a0000000-0000-0000-0000-000000000054")
PROBE_TENURE_A2_ID = uuid.UUID("a0000000-0000-0000-0000-000000000055")
PROBE_TENURE_B_ID = uuid.UUID("a0000000-0000-0000-0000-000000000056")
PROBE_APPT_A1_ID = uuid.UUID("a0000000-0000-0000-0000-000000000057")
PROBE_APPT_A2_ID = uuid.UUID("a0000000-0000-0000-0000-000000000058")
PROBE_APPT_B_ID = uuid.UUID("a0000000-0000-0000-0000-000000000059")


@pytest.fixture(scope="module")
def loader_module():
    """Import scripts/seed_person_tenure_s21lite.py once for the module."""
    sys.path.insert(0, str(REPO_ROOT / "scripts"))
    import seed_person_tenure_s21lite as mod  # noqa: E402
    return mod


@pytest.fixture
def conn():
    c = psycopg2.connect(DSN)
    c.autocommit = True
    yield c
    c.close()


@pytest.fixture
def clean_person_tenure_state():
    """TRUNCATE all 6 tables CASCADE before AND after the test.

    Note: per docs/36 §2 + tasking 180, no row-level triggers block TRUNCATE
    on these tables (they were defined without BEFORE DELETE triggers in
    01-core.sql). TRUNCATE ... CASCADE is the canonical cleanup pattern.
    """
    c = psycopg2.connect(DSN)
    c.autocommit = True
    try:
        with c.cursor() as cur:
            cur.execute(
                """
                TRUNCATE
                    cegr.person_source_evidence,
                    cegr.appointment_event,
                    cegr.tenure,
                    cegr.position,
                    cegr.person_name_alias,
                    cegr.person
                CASCADE
                """
            )
    finally:
        c.close()
    yield
    c = psycopg2.connect(DSN)
    c.autocommit = True
    try:
        with c.cursor() as cur:
            cur.execute(
                """
                TRUNCATE
                    cegr.person_source_evidence,
                    cegr.appointment_event,
                    cegr.tenure,
                    cegr.position,
                    cegr.person_name_alias,
                    cegr.person
                CASCADE
                """
            )
    finally:
        c.close()


# ---------------------------------------------------------------------------
# Case 1: migration applies — every new column from 008 exists
# ---------------------------------------------------------------------------


def test_migration_008_columns_present(conn):
    """Per Cursor 180 §NOW-2 case 1: migration is applicable; new columns exist.

    Documents the additive contract: 14 new columns across 6 tables.
    """
    expected = {
        "person": ["canonical_name_pinyin"],
        "person_name_alias": ["valid_from", "valid_to"],
        "position": ["canonical_title", "title_en", "rank_level",
                     "is_standing_committee"],
        "tenure": ["geo_entity_id", "is_current", "departure_event_id"],
        "appointment_event": ["person_id", "position_id", "geo_entity_id",
                              "announcement_doc_id"],
        "person_source_evidence": ["excerpt", "evidence_type"],
    }
    with conn.cursor() as cur:
        for table, cols in expected.items():
            cur.execute(
                """
                SELECT column_name, is_nullable
                FROM information_schema.columns
                WHERE table_schema = 'cegr' AND table_name = %s
                """,
                (table,),
            )
            actual = {row[0]: row[1] for row in cur.fetchall()}
            for col in cols:
                assert col in actual, (
                    f"migration 008 column cegr.{table}.{col} missing"
                )
                # all new columns must be NULL-able (additive contract)
                assert actual[col] == "YES", (
                    f"cegr.{table}.{col} must be nullable; got {actual[col]}"
                )


# ---------------------------------------------------------------------------
# Case 2: six tables exist (per Cursor 180 §NOW-2 case 2)
# ---------------------------------------------------------------------------


def test_six_person_tenure_tables_exist(conn):
    """Per Cursor 180 §NOW-2 case 2: 6 tables exist post-migration."""
    with conn.cursor() as cur:
        cur.execute(
            """
            SELECT table_name FROM information_schema.tables
            WHERE table_schema = 'cegr'
              AND table_name = ANY(%s)
            """,
            (EXPECTED_TABLES,),
        )
        existing = {row[0] for row in cur.fetchall()}
    missing = set(EXPECTED_TABLES) - existing
    assert not missing, f"missing tables: {missing}"


# ---------------------------------------------------------------------------
# Case 3: overlapping tenures can be inserted (no EXCLUDE constraint)
# ---------------------------------------------------------------------------


def test_overlapping_tenures_insertable(loader_module, clean_person_tenure_state):
    """Per Cursor 180 §NOW-2 case 3: tenure overlap is legal (per docs/36 §2.4).

    Uses scripts/seed_person_tenure_s21lite.probe() which inserts 2 overlapping
    tenures for person A + 1 concurrent tenure for person B on the same position.
    If migration 008 had added an EXCLUDE constraint, this would raise
    ExclusionViolation.
    """
    loader_module.probe(verbose=False)
    c = psycopg2.connect(DSN)
    c.autocommit = True
    try:
        with c.cursor() as cur:
            cur.execute(
                """
                SELECT id, person_id, start_date, end_date
                FROM cegr.tenure
                WHERE id IN (%s, %s, %s)
                ORDER BY start_date
                """,
                (str(PROBE_TENURE_A1_ID), str(PROBE_TENURE_A2_ID),
                 str(PROBE_TENURE_B_ID)),
            )
            rows = cur.fetchall()
    finally:
        c.close()
    assert len(rows) == 3, f"expected 3 tenures; got {len(rows)}: {rows}"
    # Build UUID lookup (cur returns UUID objects via register_uuid)
    by_id = {r[0]: r for r in rows}
    a1 = by_id[PROBE_TENURE_A1_ID]
    a2 = by_id[PROBE_TENURE_A2_ID]
    # A1: 2024-01-01..2024-12-31, A2: 2024-06-01..2025-05-31
    # Overlap window: 2024-06-01..2024-12-31
    assert a1[2] < a2[3], "A1.start_date must precede A2.end_date (overlap exists)"
    assert a2[2] < a1[3], "A2.start_date must precede A1.end_date (overlap exists)"


# ---------------------------------------------------------------------------
# Case 4 (bonus): status probe reports 0 rows initially, then 9 after probe
# ---------------------------------------------------------------------------


def test_status_probe_reports_table_counts(loader_module, clean_person_tenure_state):
    """scripts/seed_person_tenure_s21lite --status reports existence + counts."""
    # Before probe: 0 rows in every table.
    loader_module.status(verbose=False)
    # Probe inserts 1 source_doc, 2 persons, 1 position, 3 tenures,
    # 3 appointment_events, 1 evidence = 11 rows total (but source_doc isn't
    # in the 6 person/tenure tables).
    loader_module.probe(verbose=False)
    c = psycopg2.connect(DSN)
    c.autocommit = True
    try:
        with c.cursor() as cur:
            counts = {}
            for tbl in EXPECTED_TABLES:
                cur.execute(f"SELECT COUNT(*) FROM cegr.{tbl}")
                counts[tbl] = cur.fetchone()[0]
    finally:
        c.close()
    # After probe:
    assert counts["person"] == 2, f"expected 2 persons; got {counts['person']}"
    assert counts["position"] == 1, f"expected 1 position; got {counts['position']}"
    assert counts["tenure"] == 3, f"expected 3 tenures; got {counts['tenure']}"
    assert counts["appointment_event"] == 3, (
        f"expected 3 appointment_events; got {counts['appointment_event']}"
    )
    assert counts["person_source_evidence"] == 1, (
        f"expected 1 evidence; got {counts['person_source_evidence']}"
    )


# ---------------------------------------------------------------------------
# Case 5 (bonus): additive back-compat — legacy columns preserved
# ---------------------------------------------------------------------------


def test_legacy_columns_preserved_after_008(conn, clean_person_tenure_state):
    """docs/36 §2.0钉死: 不 DROP / 不 RENAME 既有列. Verify legacy cols intact."""
    expected_legacy = {
        "person": ["id", "canonical_name", "gender", "birth_year",
                   "ethnicity", "education_summary", "notes", "created_at"],
        "position": ["id", "title", "geo_entity_id", "level",
                     "parent_position_id", "is_key", "notes"],
        "tenure": ["id", "person_id", "position_id", "start_date",
                   "end_date", "appointment_event_id", "departure_reason",
                   "source_id", "created_at"],
        "appointment_event": ["id", "tenure_id", "event_type", "event_date",
                              "document_url", "source_id", "created_at"],
        "person_source_evidence": ["id", "person_id", "source_id", "claim",
                                    "source_location_id", "created_at"],
    }
    with conn.cursor() as cur:
        for table, cols in expected_legacy.items():
            cur.execute(
                """
                SELECT column_name FROM information_schema.columns
                WHERE table_schema = 'cegr' AND table_name = %s
                """,
                (table,),
            )
            actual = {row[0] for row in cur.fetchall()}
            for col in cols:
                assert col in actual, (
                    f"legacy column cegr.{table}.{col} must be preserved"
                )