"""Stage 2 / S2.1-full — Person/tenure demo seed + dbt layer pytest
(per tasking 577 §E).

DB-backed suite reusing the conftest session bootstrap (DROP SCHEMA cegr
CASCADE + 01-core.sql + migrations 001-013). Six cases:

  1. seed load fills the six tables to the tasked caps (30/30/20/60/60/60;
     the tasking's 5 capped tables are person/position/tenure/
     appointment_event/person_source_evidence = 30/20/60/60/60)
  2. seed load is idempotent (2nd load leaves counts unchanged)
  3. seed ids stay disjoint from the S2.1-lite probe UUID family (no
     silent ON CONFLICT DO NOTHING row swallowing across seeds)
  4. mart_person_tenure (dbt run) exposes the tasked columns with is_demo
     as the LAST column; is_demo='true' covers all rows, 'false' is empty
  5. overlap-positive probe (lite semantics): two tenures on the same
     person + position with overlapping dates are insertable (no EXCLUDE
     constraint, per docs/36 §2.4)
  6. forbidden score-family token scan on the mart SQL (comments stripped)

Existing test files are NOT modified (test_person_tenure_s21lite.py /
test_mart_city_dbt_skel_s27bf.py must stay green).
"""
from __future__ import annotations

import json
import re
import subprocess
import sys
import uuid
from pathlib import Path

import psycopg2
import psycopg2.extras
import pytest

psycopg2.extras.register_uuid()

REPO_ROOT = Path(__file__).resolve().parent.parent
DSN = "postgresql://postgres:postgres@127.0.0.1:55440/cegr_test"
DBT_BIN = REPO_ROOT / ".venv-dbt" / "bin" / "dbt"
SEED_FILE = REPO_ROOT / "data" / "seeds" / "person_tenure_demo.json"
MART_SQL = REPO_ROOT / "dbt" / "models" / "marts" / "mart_person_tenure.sql"

SIX_TABLES = [
    "person", "person_name_alias", "position", "tenure",
    "appointment_event", "person_source_evidence",
]
EXPECTED_COUNTS = {
    "person": 30,
    "person_name_alias": 30,
    "position": 20,
    "tenure": 60,
    "appointment_event": 60,
    "person_source_evidence": 60,
}
MART_SCHEMA = "cegr_staging"
MART_TABLE = "mart_person_tenure"
EXPECTED_MART_COLUMNS = {
    "tenure_id", "person_id", "canonical_name", "canonical_name_pinyin",
    "gender", "position_id", "position_title", "canonical_title", "title_en",
    "position_level", "is_standing_committee", "geo_entity_id", "geo_name",
    "start_date", "end_date", "is_current", "departure_reason",
    "appointment_event_id", "event_type", "event_date", "source_id",
    "is_demo",
}

# Lite probe UUID family (scripts/seed_person_tenure_s21lite.py) — the demo
# seed must never reuse these (tasking 577 §B).
LITE_PROBE_IDS = {
    f"a0000000-0000-0000-0000-0000000000{n}"
    for n in ["4f"] + [f"{x:02x}" for x in range(0x50, 0x5B)]
}

# Seed constants (data/seeds/person_tenure_demo.json).
SEED_SRC_DOC_ID = "a0000000-0000-0000-0000-0000000007f1"
SEED_PERSON_1 = "a0000000-0000-0000-0000-700001000000"
SEED_POSITION_1 = "a0000000-0000-0000-0000-720001000000"

# Test-local overlap probe ids (76xx segment; disjoint from seed + lite).
PROBE_TENURE_X1 = "a0000000-0000-0000-0000-760001000000"
PROBE_TENURE_X2 = "a0000000-0000-0000-0000-760002000000"

FORBIDDEN_TOKENS = [
    "score", "rating", "rank", "total_score", "confidence_score",
    "credibility_score", "peer_rank",
]


@pytest.fixture(scope="module")
def loader_module():
    """Import scripts/seed_person_tenure_demo.py once for the module."""
    sys.path.insert(0, str(REPO_ROOT / "scripts"))
    import seed_person_tenure_demo as mod  # noqa: E402
    return mod


@pytest.fixture
def conn():
    c = psycopg2.connect(DSN)
    c.autocommit = True
    yield c
    c.close()


def _truncate_six_tables() -> None:
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


def _table_counts() -> dict[str, int]:
    c = psycopg2.connect(DSN)
    c.autocommit = True
    try:
        with c.cursor() as cur:
            counts = {}
            for tbl in SIX_TABLES:
                cur.execute(f"SELECT COUNT(*) FROM cegr.{tbl}")
                counts[tbl] = cur.fetchone()[0]
    finally:
        c.close()
    return counts


# ---------------------------------------------------------------------------
# Case 1: seed load fills the tables to the tasked caps
# ---------------------------------------------------------------------------


def test_seed_load_row_caps(loader_module):
    """Tasking 577 §E: 5-table caps (30/20/60/60/60) — assert exact counts
    under a clean DB (cap implied: exact == ≤ cap)."""
    _truncate_six_tables()
    loader_module.load_seed(verbose=False)
    counts = _table_counts()
    assert counts == EXPECTED_COUNTS, (
        f"expected {EXPECTED_COUNTS}; got {counts}"
    )


# ---------------------------------------------------------------------------
# Case 2: seed load is idempotent
# ---------------------------------------------------------------------------


def test_seed_load_idempotent(loader_module):
    """2nd load must not change counts (ON CONFLICT DO NOTHING + stable
    UUIDs; no silent row swallowing)."""
    _truncate_six_tables()
    loader_module.load_seed(verbose=False)
    loader_module.load_seed(verbose=False)
    counts = _table_counts()
    assert counts == EXPECTED_COUNTS, (
        f"second load changed counts; got {counts}"
    )


# ---------------------------------------------------------------------------
# Case 3: seed ids disjoint from lite probe UUIDs
# ---------------------------------------------------------------------------


def test_seed_ids_disjoint_from_lite_probes(loader_module):
    """Tasking 577 §B: verify the demo seed does not reuse lite probe UUIDs
    (loader also hard-aborts on collision)."""
    with open(SEED_FILE, encoding="utf-8") as f:
        seed = json.load(f)
    all_ids = {
        r["id"] for key in
        ("persons", "aliases", "positions", "tenures",
         "appointment_events", "evidences")
        for r in seed[key]
    } | {seed["source_registry"]["id"], seed["source_document"]["id"]}
    assert not (all_ids & LITE_PROBE_IDS), (
        f"seed reuses lite probe UUIDs: {sorted(all_ids & LITE_PROBE_IDS)}"
    )
    # loader guard mirrors the same rule
    assert loader_module.LITE_PROBE_IDS == LITE_PROBE_IDS


# ---------------------------------------------------------------------------
# Case 4: mart columns + is_demo filter (dbt run required)
# ---------------------------------------------------------------------------


def test_mart_columns_and_is_demo_filter(loader_module):
    """Tasking 577 §E: mart column existence + is_demo as LAST column;
    is_demo='true' covers all rows, 'false' returns none."""
    _truncate_six_tables()
    loader_module.load_seed(verbose=False)

    # NOTE: tasking 577 §G's literal selector is `stg_person+ mart_person_
    # tenure`, which on a COLD graph selects only {stg_person, mart} (the
    # "+" is downstream, not the mart's other upstream refs) and fails on
    # the missing stg_tenure. conftest's DROP SCHEMA CASCADE wipes views at
    # session start, so this test builds the full family from cold via the
    # ancestors selector `+mart_person_tenure` (= 6 stg + mart).
    result = subprocess.run(
        [str(DBT_BIN), "run", "--project-dir", "dbt",
         "--profiles-dir", "dbt", "--select", "+mart_person_tenure"],
        cwd=str(REPO_ROOT), capture_output=True, text=True, timeout=300,
    )
    assert result.returncode == 0, (
        f"dbt run failed (rc={result.returncode}):\n"
        f"{result.stdout[-2000:]}\n{result.stderr[-2000:]}"
    )

    c = psycopg2.connect(DSN)
    c.autocommit = True
    try:
        with c.cursor() as cur:
            cur.execute(
                """
                SELECT column_name, ordinal_position
                FROM information_schema.columns
                WHERE table_schema = %s AND table_name = %s
                """,
                (MART_SCHEMA, MART_TABLE),
            )
            cols = cur.fetchall()
            assert cols, (
                f"{MART_SCHEMA}.{MART_TABLE} not found — dbt run built it?"
            )
            names = {n for n, _ in cols}
            missing = EXPECTED_MART_COLUMNS - names
            assert not missing, f"mart missing columns: {sorted(missing)}"
            last_col = max(cols, key=lambda r: r[1])[0]
            assert last_col == "is_demo", (
                f"is_demo must be the LAST column; got {last_col!r}"
            )

            cur.execute(
                f"SELECT is_demo, COUNT(*) FROM {MART_SCHEMA}.{MART_TABLE} "
                "GROUP BY is_demo"
            )
            demo_counts = dict(cur.fetchall())
    finally:
        c.close()
    assert demo_counts == {"true": 60}, (
        f"expected is_demo='true' x60 and no 'false' rows; got {demo_counts}"
    )


# ---------------------------------------------------------------------------
# Case 5: overlap-positive probe (lite semantics, no EXCLUDE constraint)
# ---------------------------------------------------------------------------


def test_overlapping_tenures_insertable(loader_module):
    """docs/36 §2.4: two tenures on the SAME person + SAME position with
    overlapping dates must both insert (no EXCLUDE constraint). Uses test-
    local UUIDs (76xx), cleaned up afterwards."""
    _truncate_six_tables()
    loader_module.load_seed(verbose=False)

    c = psycopg2.connect(DSN)
    c.autocommit = True
    try:
        with c.cursor() as cur:
            cur.execute(
                """
                INSERT INTO cegr.tenure
                    (id, person_id, position_id, start_date, end_date,
                     is_current, source_id)
                VALUES (%s, %s, %s, '2020-01-01', '2020-12-31', FALSE, %s),
                       (%s, %s, %s, '2020-06-01', '2021-05-31', FALSE, %s)
                ON CONFLICT (id) DO NOTHING
                """,
                (
                    PROBE_TENURE_X1, SEED_PERSON_1, SEED_POSITION_1,
                    SEED_SRC_DOC_ID,
                    PROBE_TENURE_X2, SEED_PERSON_1, SEED_POSITION_1,
                    SEED_SRC_DOC_ID,
                ),
            )
            cur.execute(
                """
                SELECT start_date, end_date FROM cegr.tenure
                WHERE id IN (%s, %s) ORDER BY start_date
                """,
                (PROBE_TENURE_X1, PROBE_TENURE_X2),
            )
            rows = cur.fetchall()
            assert len(rows) == 2, (
                f"expected 2 overlapping tenures; got {len(rows)}: {rows}"
            )
            x1, x2 = rows
            assert x1[0] < x2[1] and x2[0] < x1[1], (
                f"probes must overlap: {x1} vs {x2}"
            )
            cur.execute(
                "DELETE FROM cegr.tenure WHERE id IN (%s, %s)",
                (PROBE_TENURE_X1, PROBE_TENURE_X2),
            )
    finally:
        c.close()


# ---------------------------------------------------------------------------
# Case 6: forbidden score-family token scan on the mart SQL
# ---------------------------------------------------------------------------


def test_mart_forbidden_tokens_absent():
    """Tasking 577 §D/§E: score-family tokens must not appear in the mart
    SQL (comments stripped before scanning)."""
    raw = MART_SQL.read_text(encoding="utf-8")
    stripped = re.sub(r"/\*.*?\*/", "", raw, flags=re.DOTALL)
    stripped = "\n".join(line.split("--", 1)[0] for line in stripped.splitlines())
    lowered = stripped.lower()
    hits = {tok for tok in FORBIDDEN_TOKENS if tok in lowered}
    assert not hits, (
        f"forbidden score-family tokens present in mart_person_tenure.sql: "
        f"{sorted(hits)}"
    )
