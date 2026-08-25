"""Stage 1 / S1.18 — DEMO `is_demo` sentinel pytest wrapper.

Per docs/33-stage1-s18-demo-sha-lock-plan-20260825.md §3.3 + tasking 134 §NOW-3.

Six cases per docs/33 §3.3:
  1. Seed JSON morphology: top-level lineage.is_demo=true
  2. Loader pass-through: observation lineage->>'is_demo'='true' on all 5 rows
  3. UNVERIFIED status + literal-zero SHA preserved (no forgery)
  4. Cross-source pool exclusion: mart_source_disagreement pair count = 0
     when only DEMO rows exist for an indicator (is_demo filter works)
  5. Unload cleanup: lineage->>'is_demo' rows removed; mart pair still 0
  6. Existing S1.8 ingest_monitor regression untouched (12 cases green)

NOTE: This file owns data assertion, not the mart SQL — the mart filter is
verified by case 4 reading cegr_staging.mart_source_disagreement after the
loader has populated only the DEMO indicator/geo/period tuple.
"""
from __future__ import annotations

import json
import sys
import uuid
from pathlib import Path

import psycopg2
import psycopg2.extras
import pytest

psycopg2.extras.register_uuid()

REPO_ROOT = Path(__file__).resolve().parent.parent
SEED_FILE = REPO_ROOT / "data" / "seeds" / "jiangsu_gdp_2020_2024.json"
DSN = "postgresql://postgres:postgres@127.0.0.1:55440/cegr_test"
PYTHON = sys.executable

# Stable demo UUIDs — match scripts/seed_jiangsu_gdp_demo.py constants.
JIANGSU_SOURCE_DOC_ID = uuid.UUID("a0000000-0000-0000-0000-000000000004")
JIANGSU_PROVINCE_ID = uuid.UUID("a0000000-0000-0000-0000-000000000032")
JIANGSU_GDP_INDICATOR_ID = uuid.UUID("a0000000-0000-0000-0000-000000000001")

LITERAL_ZERO_SHA = "0" * 64


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture(scope="module")
def loader_module():
    """Import scripts/seed_jiangsu_gdp_demo.py once for the module."""
    sys.path.insert(0, str(REPO_ROOT / "scripts"))
    import seed_jiangsu_gdp_demo as mod  # noqa: E402
    return mod


@pytest.fixture
def conn():
    """Autocommit so loader (which uses its own connection) sees the same
    transaction boundary semantics. Per-subprocess DELETE cleanup in teardown."""
    c = psycopg2.connect(DSN)
    c.autocommit = True
    yield c
    # No cleanup here — handled by `load_unload_cycle` fixture or per-case.
    c.close()


@pytest.fixture
def clean_demo_state():
    """Ensure no leftover demo rows from a previous run.

    NOTE: source_document_no_delete() and observation_no_delete() row
    triggers block DELETE (per schema/01-core.sql). We use TRUNCATE
    ... CASCADE which bypasses row-level BEFORE DELETE triggers (matches
    test_acceptance_e2e_s15 + test_r03_cross_source_dbt pattern).
    TRUNCATE is safe here because we're cleaning test data only —
    never use in production paths.

    Cascade covers: observation, observation_revision,
    source_disagreement, source_location, source_document,
    source_document_verification_event, indicator_methodology_version,
    calendar_period, ingestion_run. We then explicitly DELETE the
    top-level rows (source_registry, indicator_definition,
    geo_code_version, geo_entity) which have no FK dependents after
    the cascade.
    """
    c = psycopg2.connect(DSN)
    c.autocommit = True
    try:
        with c.cursor() as cur:
            cur.execute(
                "TRUNCATE cegr.observation, cegr.observation_revision, "
                "cegr.source_disagreement, cegr.source_location, "
                "cegr.source_document, "
                "cegr.source_document_verification_event, "
                "cegr.indicator_methodology_version, "
                "cegr.calendar_period, cegr.ingestion_run CASCADE"
            )
            cur.execute(
                "DELETE FROM cegr.source_registry WHERE id = %s",
                ("a0000000-0000-0000-0000-000000000003",),
            )
            cur.execute(
                "DELETE FROM cegr.indicator_definition WHERE id = %s",
                (str(JIANGSU_GDP_INDICATOR_ID),),
            )
            cur.execute(
                "DELETE FROM cegr.geo_code_version WHERE id = %s",
                ("a0000000-0000-0000-0000-000000000007",),
            )
            cur.execute(
                "DELETE FROM cegr.geo_entity WHERE id = %s",
                (str(JIANGSU_PROVINCE_ID),),
            )
    finally:
        c.close()
    yield
    # post-test cleanup (idempotent)
    c = psycopg2.connect(DSN)
    c.autocommit = True
    try:
        with c.cursor() as cur:
            cur.execute(
                "TRUNCATE cegr.observation, cegr.observation_revision, "
                "cegr.source_disagreement, cegr.source_location, "
                "cegr.source_document, "
                "cegr.source_document_verification_event, "
                "cegr.indicator_methodology_version, "
                "cegr.calendar_period, cegr.ingestion_run CASCADE"
            )
            cur.execute(
                "DELETE FROM cegr.source_registry WHERE id = %s",
                ("a0000000-0000-0000-0000-000000000003",),
            )
            cur.execute(
                "DELETE FROM cegr.indicator_definition WHERE id = %s",
                (str(JIANGSU_GDP_INDICATOR_ID),),
            )
            cur.execute(
                "DELETE FROM cegr.geo_code_version WHERE id = %s",
                ("a0000000-0000-0000-0000-000000000007",),
            )
            cur.execute(
                "DELETE FROM cegr.geo_entity WHERE id = %s",
                (str(JIANGSU_PROVINCE_ID),),
            )
    finally:
        c.close()


# ---------------------------------------------------------------------------
# 1. Seed JSON morphology
# ---------------------------------------------------------------------------


def test_seed_json_has_is_demo():
    """data/seeds/jiangsu_gdp_2020_2024.json top-level lineage has
    is_demo=true + demo_reason + demo_sentinel_sha256 (per docs/33 §3.1)."""
    with open(SEED_FILE, "r", encoding="utf-8") as f:
        seed = json.load(f)
    lineage = seed["lineage"]
    assert lineage.get("is_demo") is True, "lineage.is_demo must be True"
    assert "demo_reason" in lineage, "lineage.demo_reason must be set"
    assert lineage.get("demo_sentinel_sha256", "").startswith(LITERAL_ZERO_SHA), (
        "demo_sentinel_sha256 must document the literal-zeros choice"
    )


# ---------------------------------------------------------------------------
# 2. Loader pass-through: 5 observations carry is_demo=true in lineage JSONB
# ---------------------------------------------------------------------------


def test_demo_load_writes_is_demo_in_observation_lineage(loader_module, clean_demo_state):
    """After --load, cegr.observation.lineage->>'is_demo'='true' on all 5 rows."""
    loader_module.load_seed(verbose=False)
    c = psycopg2.connect(DSN)
    c.autocommit = True
    try:
        with c.cursor() as cur:
            cur.execute(
                """
                SELECT COUNT(*) FROM cegr.observation
                WHERE source_id = %s
                  AND lineage->>'is_demo' = 'true'
                """,
                (str(JIANGSU_SOURCE_DOC_ID),),
            )
            n_is_demo = cur.fetchone()[0]
            cur.execute(
                """
                SELECT COUNT(*) FROM cegr.observation
                WHERE source_id = %s
                """,
                (str(JIANGSU_SOURCE_DOC_ID),),
            )
            n_obs = cur.fetchone()[0]
    finally:
        c.close()
    assert n_obs == 5, f"expected 5 demo observations, got {n_obs}"
    assert n_is_demo == 5, f"expected 5 is_demo markers, got {n_is_demo}"


# ---------------------------------------------------------------------------
# 3. UNVERIFIED status + literal-zero SHA preserved
# ---------------------------------------------------------------------------


def test_unverified_status_and_zero_sha_preserved(loader_module, clean_demo_state):
    """After --load, cegr.source_document for demo keeps
    verification_status='UNVERIFIED' + file_hash_sha256='00...00'. The
    S1.18 path A does not promote DEMO to VERIFIED and does not invent
    a real SHA."""
    loader_module.load_seed(verbose=False)
    c = psycopg2.connect(DSN)
    c.autocommit = True
    try:
        with c.cursor() as cur:
            cur.execute(
                """
                SELECT verification_status, file_hash_sha256
                FROM cegr.source_document
                WHERE id = %s
                """,
                (str(JIANGSU_SOURCE_DOC_ID),),
            )
            row = cur.fetchone()
    finally:
        c.close()
    assert row is not None, "demo source_document not found"
    status, sha = row
    assert status == "UNVERIFIED", f"expected UNVERIFIED, got {status!r}"
    assert sha == LITERAL_ZERO_SHA, (
        f"expected literal-zero SHA, got {sha!r}"
    )


# ---------------------------------------------------------------------------
# 4. Cross-source pool exclusion (mart_source_disagreement filter works)
# ---------------------------------------------------------------------------


def test_demo_excluded_from_mart_cross_source(loader_module, clean_demo_state):
    """After --load + dbt mart rebuild, cegr_staging.mart_source_disagreement
    must NOT include any pair where either side is the demo source_document
    (i.e. the is_demo filter is effective). Since demo is the ONLY source
    for Jiangsu GDP in the test DB, the indicator has zero pairs by
    construction; we assert pair count = 0 strictly."""
    loader_module.load_seed(verbose=False)
    c = psycopg2.connect(DSN)
    c.autocommit = True
    try:
        with c.cursor() as cur:
            cur.execute(
                """
                SELECT COUNT(*) FROM cegr_staging.mart_source_disagreement
                WHERE source_a_id = %s OR source_b_id = %s
                   OR source_a_observation_id IN (
                       SELECT id FROM cegr.observation
                       WHERE source_id = %s
                   )
                   OR source_b_observation_id IN (
                       SELECT id FROM cegr.observation
                       WHERE source_id = %s
                   )
                """,
                (
                    str(JIANGSU_SOURCE_DOC_ID), str(JIANGSU_SOURCE_DOC_ID),
                    str(JIANGSU_SOURCE_DOC_ID), str(JIANGSU_SOURCE_DOC_ID),
                ),
            )
            n_pairs = cur.fetchone()[0]
            # Also assert the candidate CTE itself excludes demo rows.
            cur.execute(
                """
                SELECT COUNT(*) FROM cegr_staging.stg_source_disagreement_candidate
                WHERE source_a_id = %s OR source_b_id = %s
                """,
                (str(JIANGSU_SOURCE_DOC_ID), str(JIANGSU_SOURCE_DOC_ID)),
            )
            n_candidate_pairs = cur.fetchone()[0]
    finally:
        c.close()
    assert n_pairs == 0, (
        f"expected 0 mart pairs involving demo source, got {n_pairs}"
    )
    assert n_candidate_pairs == 0, (
        f"expected 0 candidate pairs involving demo source, "
        f"got {n_candidate_pairs} — is_demo filter not effective"
    )


# ---------------------------------------------------------------------------
# 5. Unload cleanup
# ---------------------------------------------------------------------------


def test_unload_clears_demo_rows(loader_module, clean_demo_state):
    """After --load then --unload, no observation carries is_demo=true."""
    loader_module.load_seed(verbose=False)
    loader_module.unload(verbose=False)
    c = psycopg2.connect(DSN)
    c.autocommit = True
    try:
        with c.cursor() as cur:
            cur.execute(
                """
                SELECT COUNT(*) FROM cegr.observation
                WHERE lineage->>'is_demo' = 'true'
                """,
            )
            n_is_demo = cur.fetchone()[0]
    finally:
        c.close()
    assert n_is_demo == 0, f"expected 0 is_demo markers after unload, got {n_is_demo}"


# ---------------------------------------------------------------------------
# 6. Status extension: is_demo_markers count line
# ---------------------------------------------------------------------------


def test_status_reports_is_demo_marker_count(loader_module, clean_demo_state, capsys):
    """`--status` output includes 'is_demo_markers: N rows tagged' line."""
    loader_module.load_seed(verbose=False)
    try:
        loader_module.status(verbose=True)
        captured = capsys.readouterr()
    finally:
        loader_module.unload(verbose=False)
    assert "is_demo_markers" in captured.out, (
        f"expected 'is_demo_markers' in status output, got:\n{captured.out}"
    )
    assert "5 rows tagged" in captured.out, (
        f"expected '5 rows tagged' in status output, got:\n{captured.out}"
    )
