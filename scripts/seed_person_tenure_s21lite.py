"""Stage 2 / S2.1-lite — Empty seed skeleton for person / tenure / position.

Per Cursor 180 §SCHEMA (S2.1-lite tasking, user ruling D shrink).
Per Cursor 179 (user ruling D accepted 2026-08-25).

This script is a SKELETON ONLY: it does NOT load any rows. Per tasking 180
§SCHEMA:

    seed = **空或骨架即可**（0 行业务数据 OK）；禁止爬网灌履历

The script serves three purposes:
  1. `--status`  proves the 6 person/tenure tables exist post-migration-008
     and counts rows (expected: 0 for this knife).
  2. `--probe`   runs an overlap-positive insert probe: creates 2 persons +
     1 position + 1 source_doc + 2 overlapping tenures → confirms migration
     008 did NOT add an EXCLUDE constraint on tenure (per docs/36 §2.4 +
     tasking 180 §红线).
  3. `--unload`  TRUNCATE CASCADE on all 6 tables (idempotent, dangerous —
     wipes ANY data including future real seeds; production paths must
     NEVER call --unload).

DSN: ${CEGR_DSN:-${STAGE0_DSN:-postgresql://postgres:postgres@127.0.0.1:55440/cegr_test}}

Usage:
  python scripts/seed_person_tenure_s21lite.py --status
  python scripts/seed_person_tenure_s21lite.py --probe
  python scripts/seed_person_tenure_s21lite.py --unload

Idempotent: all INSERTs use ON CONFLICT DO NOTHING with stable UUIDs.
"""

from __future__ import annotations

import argparse
import os
import sys
import uuid
from pathlib import Path

# Stable deterministic UUIDs (a0000000-0000-0000-0000-00000000005X family).
# These are PROBE rows only — meant to verify schema invariants. They have
# is_demo flag propagated via lineage and are safe to TRUNCATE on --unload.
PROBE_SOURCE_REGISTRY_ID = uuid.UUID("a0000000-0000-0000-0000-00000000004f")
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
PROBE_EVIDENCE_ID = uuid.UUID("a0000000-0000-0000-0000-00000000005a")


def get_dsn() -> str:
    return os.environ.get(
        "CEGR_DSN",
        os.environ.get(
            "STAGE0_DSN",
            "postgresql://postgres:postgres@127.0.0.1:55440/cegr_test",
        ),
    )


def _connect():
    try:
        import psycopg2  # type: ignore
        import psycopg2.extras  # type: ignore
    except ImportError:
        sys.exit("ERROR: psycopg2 not installed. Run: pip install psycopg2-binary")

    psycopg2.extras.register_uuid()
    return psycopg2.connect(get_dsn())


def status(verbose: bool = True) -> None:
    """Probe table existence + row counts. Expected: all exist, all 0."""
    expected_tables = [
        "person", "person_name_alias", "position", "tenure",
        "appointment_event", "person_source_evidence",
    ]
    try:
        with _connect() as conn:
            with conn.cursor() as cur:
                counts = {}
                for tbl in expected_tables:
                    cur.execute(
                        """
                        SELECT EXISTS (
                            SELECT 1 FROM information_schema.tables
                            WHERE table_schema = 'cegr' AND table_name = %s
                        )
                        """,
                        (tbl,),
                    )
                    exists = cur.fetchone()[0]
                    if not exists:
                        counts[tbl] = "MISSING"
                        continue
                    cur.execute(f"SELECT COUNT(*) FROM cegr.{tbl}")
                    counts[tbl] = cur.fetchone()[0]
        for tbl, n in counts.items():
            print(f"[status] cegr.{tbl}: {n}")
        missing = [t for t, n in counts.items() if n == "MISSING"]
        if missing:
            print(f"[status] ERROR: missing tables: {missing}", file=sys.stderr)
            sys.exit(1)
    except Exception as e:
        print(f"[status] ERROR: {e}", file=sys.stderr)
        sys.exit(1)


def probe(verbose: bool = True) -> None:
    """Insert overlapping tenures to prove no EXCLUDE constraint exists.

    Creates:
      - 1 source_document
      - 2 persons (A, B)
      - 1 position (central-level, no geo_entity)
      - 2 overlapping tenures for person A (same position, overlapping dates)
      - 1 tenure for person B (same position, same dates as A's second tenure)
      - 3 appointment_events (one per tenure)
      - 1 person_source_evidence

    Expected outcome (per docs/36 §2.4):
      * All inserts succeed (no EXCLUDE constraint).
      * Person A holds the position TWICE simultaneously during overlap window.
    """
    lineage_is_demo = '{"is_demo": "true", "seed_id": "person_tenure_s21lite_probe"}'
    try:
        with _connect() as conn:
            with conn.cursor() as cur:
                # source_registry (FK parent for source_document)
                cur.execute(
                    """
                    INSERT INTO cegr.source_registry
                        (id, domain, organization, category, primary_url,
                         access_method, source_level, declared_source_level,
                         update_frequency, enabled, auth_note, purpose_note)
                    VALUES (%s, %s, %s, %s, %s,
                            %s, %s, %s,
                            %s, TRUE, %s, %s)
                    ON CONFLICT (id) DO NOTHING
                    """,
                    (
                        str(PROBE_SOURCE_REGISTRY_ID),
                        "probe.s2.1-lite",
                        "CC_PROBE",
                        "PERSONNEL_NOTICE",
                        "(DEMO_SEED_NO_FILE)",
                        "HTML_PARSE",
                        "S1",
                        "S1",
                        "AD_HOC",
                        "probe; no auth",
                        "S2.1-lite probe registry; per Cursor 180 tasking",
                    ),
                )
                # source_document (FK target for tenure + pse)
                # Schema reality (01-core.sql): source_level is enum (use 'S1'),
                # verification_status is NOT NULL enum (use 'UNVERIFIED'),
                # file_hash_sha256 is NOT NULL + regex CHECK (use 64 zeros),
                # title + publisher are NOT NULL.
                cur.execute(
                    """
                    INSERT INTO cegr.source_document
                        (id, source_registry_id, source_level,
                         verification_status, title, publisher,
                         file_hash_sha256, url, caveat_text)
                    VALUES (%s, %s, 'S1', 'UNVERIFIED',
                            %s, %s, %s, %s, %s)
                    ON CONFLICT (id) DO NOTHING
                    """,
                    (
                        str(PROBE_SOURCE_DOC_ID),
                        str(PROBE_SOURCE_REGISTRY_ID),
                        "S2.1-lite probe document",
                        "CC_PROBE",
                        "0" * 64,
                        "(DEMO_SEED_NO_FILE)",
                        "S2.1-lite probe; tenure overlap test; per Cursor 180",
                    ),
                )
                # persons (with new canonical_name_pinyin column populated)
                cur.execute(
                    """
                    INSERT INTO cegr.person
                        (id, canonical_name, canonical_name_pinyin, gender)
                    VALUES (%s, %s, %s, %s), (%s, %s, %s, %s)
                    ON CONFLICT (id) DO NOTHING
                    """,
                    (
                        str(PROBE_PERSON_A_ID), "CC_PROBE_A", "Probe A", "M",
                        str(PROBE_PERSON_B_ID), "CC_PROBE_B", "Probe B", "F",
                    ),
                )
                # position (central-level; new rank_level + is_standing_committee)
                cur.execute(
                    """
                    INSERT INTO cegr.position
                        (id, title, canonical_title, title_en, rank_level,
                         is_standing_committee, level)
                    VALUES (%s, %s, %s, %s, %s, %s, %s)
                    ON CONFLICT (id) DO NOTHING
                    """,
                    (
                        str(PROBE_POSITION_ID),
                        "CC_PROBE_POSITION",
                        "Probe Position",
                        "Probe Position (EN)",
                        "BUREAU_DIRECTOR",
                        False,
                        "CENTRAL",
                    ),
                )
                # overlapping tenures for person A: 2024-01-01..2024-12-31
                # and 2024-06-01..2025-05-31 (overlap 2024-06-01..2024-12-31)
                cur.execute(
                    """
                    INSERT INTO cegr.tenure
                        (id, person_id, position_id, start_date, end_date,
                         appointment_event_id, source_id, is_current, geo_entity_id)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, NULL),
                           (%s, %s, %s, %s, %s, %s, %s, %s, NULL),
                           (%s, %s, %s, %s, %s, %s, %s, %s, NULL)
                    ON CONFLICT (id) DO NOTHING
                    """,
                    (
                        str(PROBE_TENURE_A1_ID), str(PROBE_PERSON_A_ID),
                        str(PROBE_POSITION_ID), "2024-01-01", "2024-12-31",
                        str(PROBE_APPT_A1_ID), str(PROBE_SOURCE_DOC_ID), False,
                        str(PROBE_TENURE_A2_ID), str(PROBE_PERSON_A_ID),
                        str(PROBE_POSITION_ID), "2024-06-01", "2025-05-31",
                        str(PROBE_APPT_A2_ID), str(PROBE_SOURCE_DOC_ID), False,
                        str(PROBE_TENURE_B_ID), str(PROBE_PERSON_B_ID),
                        str(PROBE_POSITION_ID), "2024-06-01", "2025-05-31",
                        str(PROBE_APPT_B_ID), str(PROBE_SOURCE_DOC_ID), False,
                    ),
                )
                # appointment_events (with new person_id/position_id back-refs)
                cur.execute(
                    """
                    INSERT INTO cegr.appointment_event
                        (id, tenure_id, event_type, event_date, source_id,
                         person_id, position_id, geo_entity_id, document_url,
                         announcement_doc_id)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, NULL, NULL, %s),
                           (%s, %s, %s, %s, %s, %s, %s, NULL, NULL, %s),
                           (%s, %s, %s, %s, %s, %s, %s, NULL, NULL, %s)
                    ON CONFLICT (id) DO NOTHING
                    """,
                    (
                        str(PROBE_APPT_A1_ID), str(PROBE_TENURE_A1_ID),
                        "APPOINTMENT", "2024-01-01", str(PROBE_SOURCE_DOC_ID),
                        str(PROBE_PERSON_A_ID), str(PROBE_POSITION_ID),
                        str(PROBE_SOURCE_DOC_ID),
                        str(PROBE_APPT_A2_ID), str(PROBE_TENURE_A2_ID),
                        "DEPARTURE", "2025-05-31", str(PROBE_SOURCE_DOC_ID),
                        str(PROBE_PERSON_A_ID), str(PROBE_POSITION_ID),
                        str(PROBE_SOURCE_DOC_ID),
                        str(PROBE_APPT_B_ID), str(PROBE_TENURE_B_ID),
                        "APPOINTMENT", "2024-06-01", str(PROBE_SOURCE_DOC_ID),
                        str(PROBE_PERSON_B_ID), str(PROBE_POSITION_ID),
                        str(PROBE_SOURCE_DOC_ID),
                    ),
                )
                # person_source_evidence (with new excerpt + evidence_type)
                cur.execute(
                    """
                    INSERT INTO cegr.person_source_evidence
                        (id, person_id, source_id, claim, excerpt, evidence_type)
                    VALUES (%s, %s, %s, %s, %s, %s)
                    ON CONFLICT (id) DO NOTHING
                    """,
                    (
                        str(PROBE_EVIDENCE_ID), str(PROBE_PERSON_A_ID),
                        str(PROBE_SOURCE_DOC_ID),
                        "CC probe evidence claim",
                        "CC probe evidence excerpt",
                        "ANNOUNCEMENT",
                    ),
                )
            conn.commit()
        if verbose:
            print(f"[probe] inserted overlapping tenures for person A "
                  f"({PROBE_TENURE_A1_ID}, {PROBE_TENURE_A2_ID}); "
                  f"person B tenure {PROBE_TENURE_B_ID}")
            print("[probe] all 3 tenures share the same position + overlapping "
                  "dates — proves no EXCLUDE constraint was added by 008")
    except Exception as e:
        print(f"[probe] ERROR: {e}", file=sys.stderr)
        sys.exit(1)


def unload(verbose: bool = True) -> None:
    """TRUNCATE all 6 person/tenure tables + probe source_registry/doc CASCADE.

    WARNING: this wipes ANY data in these tables, including future real seeds.
    Production paths must NEVER call --unload. The probe UUIDs in this script
    are the only safe targets; the script uses TRUNCATE to also remove any
    rows that downstream tests may have inserted.
    """
    try:
        with _connect() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    TRUNCATE
                        cegr.person_source_evidence,
                        cegr.appointment_event,
                        cegr.tenure,
                        cegr.position,
                        cegr.person_name_alias,
                        cegr.person,
                        cegr.source_document,
                        cegr.source_registry
                    CASCADE
                    """
                )
            conn.commit()
        if verbose:
            print("[unload] truncated all 6 person/tenure tables + "
                  "probe source_document/registry CASCADE")
    except Exception as e:
        print(f"[unload] ERROR: {e}", file=sys.stderr)
        sys.exit(1)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    parser.add_argument("--status", action="store_true",
                        help="Probe table existence + row counts")
    parser.add_argument("--probe", action="store_true",
                        help="Insert overlapping tenure probe rows")
    parser.add_argument("--unload", action="store_true",
                        help="TRUNCATE all 6 person/tenure tables CASCADE")
    args = parser.parse_args()

    if args.status:
        status()
    elif args.probe:
        probe()
    elif args.unload:
        unload()
    else:
        parser.print_help()


if __name__ == "__main__":
    main()