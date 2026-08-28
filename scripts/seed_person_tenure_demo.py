"""Stage 2 / S2.1-full — Demo seed loader for person / tenure / position.

Loads data/seeds/person_tenure_demo.json (30 person / 30 alias / 20 position
/ 60 tenure / 60 appointment_event / 60 person_source_evidence) into the six
person-domain tables of cegr_test.

Per tasking 577 §B (O1 CLOSED as-scoped unlocks S2.1-full):
  - all rows are DEMO (lineage.is_demo='true', source_file_sha256='0'*64,
    source_file_url='(DEMO_SEED_NO_FILE)') — no real names/dates/SHA, no crawl
  - stable deterministic UUIDs, disjoint from the S2.1-lite probe UUID family
    (a0000000-0000-0000-0000-00000000004f..05a) — the loader hard-aborts if
    any seed id collides with a lite probe id, so ON CONFLICT DO NOTHING can
    never silently swallow a probe row or vice versa
  - contract: docs/36 §2 (S2.1 person/tenure field contract)

Usage:
  python scripts/seed_person_tenure_demo.py --load
  python scripts/seed_person_tenure_demo.py --status
  python scripts/seed_person_tenure_demo.py --unload

Idempotent: all INSERTs use ON CONFLICT DO NOTHING with stable UUIDs.

--unload TRUNCATEs the six person/tenure tables CASCADE. The two DEMO source
parents (source_registry / source_document rows) are intentionally left in
place: source_document_no_delete blocks plain DELETE, and TRUNCATE on
source_document would CASCADE into cegr.observation (out of this seed's
scope). conftest's session bootstrap (DROP SCHEMA cegr CASCADE) is the
canonical full reset.

DSN: ${CEGR_DSN:-${STAGE0_DSN:-postgresql://postgres:postgres@127.0.0.1:55440/cegr_test}}
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
SEED_FILE = REPO_ROOT / "data" / "seeds" / "person_tenure_demo.json"

SIX_TABLES = [
    "person", "person_name_alias", "position", "tenure",
    "appointment_event", "person_source_evidence",
]

# Mirror of scripts/seed_person_tenure_s21lite.py probe UUIDs — keep disjoint.
LITE_PROBE_IDS = {
    f"a0000000-0000-0000-0000-0000000000{n}"
    for n in ["4f"] + [f"{x:02x}" for x in range(0x50, 0x5B)]
}


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


def _load_seed_json() -> dict:
    if not SEED_FILE.exists():
        sys.exit(f"ERROR: seed file not found: {SEED_FILE}")
    with open(SEED_FILE, "r", encoding="utf-8") as f:
        seed = json.load(f)

    # Hard guard: seed ids must never collide with lite probe UUIDs, else
    # ON CONFLICT DO NOTHING would silently swallow rows across seeds.
    row_sets = [
        seed["persons"], seed["aliases"], seed["positions"],
        seed["tenures"], seed["appointment_events"], seed["evidences"],
    ]
    all_ids = {r["id"] for rows in row_sets for r in rows}
    all_ids.add(seed["source_registry"]["id"])
    all_ids.add(seed["source_document"]["id"])
    clash = all_ids & LITE_PROBE_IDS
    if clash:
        sys.exit(f"ERROR: seed reuses lite probe UUIDs: {sorted(clash)}")

    expected = seed["metadata"]["counts"]
    actual = {
        "person": len(seed["persons"]),
        "person_name_alias": len(seed["aliases"]),
        "position": len(seed["positions"]),
        "tenure": len(seed["tenures"]),
        "appointment_event": len(seed["appointment_events"]),
        "person_source_evidence": len(seed["evidences"]),
    }
    if actual != expected:
        sys.exit(f"ERROR: seed row counts {actual} != metadata.counts {expected}")
    if seed["lineage"]["is_demo"] != "true":
        sys.exit("ERROR: seed lineage.is_demo must be 'true'")
    if seed["lineage"]["source_file_sha256"] != "0" * 64:
        sys.exit("ERROR: demo seed must carry the all-zero placeholder SHA")
    if seed["lineage"]["source_file_url"] != "(DEMO_SEED_NO_FILE)":
        sys.exit("ERROR: demo seed must carry the (DEMO_SEED_NO_FILE) sentinel")
    return seed


def _insert_many(cur, sql_prefix: str, rows: list[dict], fields: list[str],
                 n_placeholders: int) -> None:
    """Batched multi-row INSERT ... ON CONFLICT (id) DO NOTHING."""
    params: list = []
    for r in rows:
        params.extend(r[f] for f in fields)
    cur.execute(
        sql_prefix + ",".join(
            f"({','.join(['%s'] * n_placeholders)})" for _ in rows
        ) + " ON CONFLICT (id) DO NOTHING",
        params,
    )


def load_seed(verbose: bool = True) -> None:
    """Insert the person/tenure demo seed (idempotent)."""
    seed = _load_seed_json()
    src_reg = seed["source_registry"]
    src_doc = seed["source_document"]

    if verbose:
        counts = seed["metadata"]["counts"]
        print(f"[seed] loading person_tenure_demo ({counts}) into cegr_test")

    with _connect() as conn:
        with conn.cursor() as cur:
            # source_registry (FK parent for source_document)
            cur.execute(
                """
                INSERT INTO cegr.source_registry
                    (id, domain, organization, category, primary_url,
                     access_method, source_level, declared_source_level,
                     update_frequency, enabled, auth_note, purpose_note)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, TRUE, %s, %s)
                ON CONFLICT (id) DO NOTHING
                """,
                (
                    src_reg["id"], src_reg["domain"], src_reg["organization"],
                    src_reg["category"], src_reg["primary_url"],
                    src_reg["access_method"], src_reg["source_level"],
                    src_reg["declared_source_level"],
                    src_reg["update_frequency"], src_reg["auth_note"],
                    src_reg["purpose_note"],
                ),
            )
            # source_document (FK target for tenure/appt/evidence source_id)
            cur.execute(
                """
                INSERT INTO cegr.source_document
                    (id, source_registry_id, source_level, verification_status,
                     title, publisher, file_hash_sha256, url, caveat_text)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (id) DO NOTHING
                """,
                (
                    src_doc["id"], src_doc["source_registry_id"],
                    src_doc["source_level"], src_doc["verification_status"],
                    src_doc["title"], src_doc["publisher"],
                    src_doc["file_hash_sha256"], src_doc["url"],
                    src_doc["caveat_text"],
                ),
            )

            _insert_many(
                cur,
                """
                INSERT INTO cegr.person
                    (id, canonical_name, canonical_name_pinyin, gender,
                     birth_year, ethnicity, education_summary, notes)
                VALUES
                """,
                seed["persons"],
                ["id", "canonical_name", "canonical_name_pinyin", "gender",
                 "birth_year", "ethnicity", "education_summary", "notes"],
                8,
            )
            _insert_many(
                cur,
                """
                INSERT INTO cegr.person_name_alias
                    (id, person_id, alias, alias_type, valid_from, valid_to)
                VALUES
                """,
                seed["aliases"],
                ["id", "person_id", "alias", "alias_type",
                 "valid_from", "valid_to"],
                6,
            )
            _insert_many(
                cur,
                """
                INSERT INTO cegr.position
                    (id, title, canonical_title, title_en, rank_level,
                     is_standing_committee, level, geo_entity_id)
                VALUES
                """,
                seed["positions"],
                ["id", "title", "canonical_title", "title_en", "rank_level",
                 "is_standing_committee", "level", "geo_entity_id"],
                8,
            )
            # FK-safe order: person + position first (above), then tenure,
            # then events/evidence. tenure.appointment_event_id carries no
            # FK (core schema), so pre-filling is safe.
            _insert_many(
                cur,
                """
                INSERT INTO cegr.tenure
                    (id, person_id, position_id, geo_entity_id, start_date,
                     end_date, is_current, appointment_event_id,
                     departure_reason, source_id)
                VALUES
                """,
                seed["tenures"],
                ["id", "person_id", "position_id", "geo_entity_id",
                 "start_date", "end_date", "is_current",
                 "appointment_event_id", "departure_reason", "source_id"],
                10,
            )
            _insert_many(
                cur,
                """
                INSERT INTO cegr.appointment_event
                    (id, tenure_id, event_type, event_date, document_url,
                     source_id, person_id, position_id, geo_entity_id,
                     announcement_doc_id)
                VALUES
                """,
                seed["appointment_events"],
                ["id", "tenure_id", "event_type", "event_date",
                 "document_url", "source_id", "person_id", "position_id",
                 "geo_entity_id", "announcement_doc_id"],
                10,
            )
            _insert_many(
                cur,
                """
                INSERT INTO cegr.person_source_evidence
                    (id, person_id, source_id, claim, excerpt, evidence_type)
                VALUES
                """,
                seed["evidences"],
                ["id", "person_id", "source_id", "claim", "excerpt",
                 "evidence_type"],
                6,
            )
        conn.commit()
    if verbose:
        print("[seed] person_tenure_demo loaded (idempotent ON CONFLICT DO NOTHING)")


def status(verbose: bool = True) -> None:
    """Print per-table row counts + demo-source marker count."""
    try:
        with _connect() as conn:
            with conn.cursor() as cur:
                counts = {}
                for tbl in SIX_TABLES:
                    cur.execute(f"SELECT COUNT(*) FROM cegr.{tbl}")
                    counts[tbl] = cur.fetchone()[0]
                # is_demo proxy: rows whose source doc carries the
                # DEMO_SEED marker (same rule mart_person_tenure applies).
                cur.execute(
                    """
                    SELECT COUNT(*) FROM cegr.tenure t
                    JOIN cegr.source_document sd ON sd.id = t.source_id
                    WHERE sd.caveat_text LIKE '%%DEMO_SEED%%'
                       OR sd.url = '(DEMO_SEED_NO_FILE)'
                    """
                )
                n_demo = cur.fetchone()[0]
        if verbose:
            for tbl, n in counts.items():
                print(f"[status] cegr.{tbl}: {n}")
            print(f"[status] tenures backed by DEMO_SEED source: {n_demo}")
    except Exception as e:
        print(f"[status] ERROR: {e}", file=sys.stderr)
        sys.exit(1)


def unload(verbose: bool = True) -> None:
    """TRUNCATE the six person/tenure tables CASCADE (demo wipe).

    The two DEMO source parents stay (see module docstring). Production
    paths must NEVER call --unload.
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
                        cegr.person
                    CASCADE
                    """
                )
            conn.commit()
        if verbose:
            print("[unload] truncated all 6 person/tenure tables CASCADE "
                  "(DEMO source parents retained)")
    except Exception as e:
        print(f"[unload] ERROR: {e}", file=sys.stderr)
        sys.exit(1)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    parser.add_argument("--load", action="store_true",
                        help="Insert demo seed (idempotent)")
    parser.add_argument("--status", action="store_true",
                        help="Show per-table row counts")
    parser.add_argument("--unload", action="store_true",
                        help="TRUNCATE the 6 person/tenure tables CASCADE")
    args = parser.parse_args()

    if args.load:
        load_seed()
    elif args.status:
        status()
    elif args.unload:
        unload()
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
