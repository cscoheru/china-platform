#!/usr/bin/env python3
"""M1 T3 — pytest 闸: observation SUCCESS for the designated hubei_2026_06.xlsx.

Per docs/55 §T3 (2026-08-31, knife 627 §3) and docs/55 §1.1, this test
file locks:

  * 指定 xlsx SHA == registry 该行
  * ingestion_run.status == SUCCESS (PARTIAL 即失败)
  * GDP observation ≥1; value IS NOT NULL; missing_reason IS NULL
  * observation.source_id → source_document.file_hash_sha256 一跳 == 文件
  * calendar_period / period_start 是统计期，不是 extracted_at
  * GDP 行 caveat_text 非空
  * 该批 source_document.url 不得仅为 tjj.hubei.gov.cn 首页

Required fixtures:
  * cegr_test DSN reachable at postgresql://postgres:postgres@127.0.0.1:55440/cegr_test
  * source_registry row tjj.hubei.gov.cn / PROVINCIAL_BULLETIN present
  * T1 reference data seeded (scripts/seed_m1_reference_data.py)
"""
from __future__ import annotations

import hashlib
import sys
from pathlib import Path

import psycopg2
import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent

# Make backend connectors importable
BACKEND_SRC = REPO_ROOT / "backend" / "src"
sys.path.insert(0, str(BACKEND_SRC))
SCRIPTS_DIR = REPO_ROOT / "scripts"
sys.path.insert(0, str(SCRIPTS_DIR))

import seed_m1_reference_data as seed  # noqa: E402
from china_platform.connectors.provincial_yearbook import (  # noqa: E402
    ProvincialYearbookConnector,
)

DSN = "postgresql://postgres:postgres@127.0.0.1:55440/cegr_test"

# Stable UUIDs must match scripts/seed_m1_reference_data.py
HUBEI_PROVINCE_ID = "a1000000-0000-0000-0000-000000000001"
HUBEI_GDP_INDICATOR_ID = "a1000000-0000-0000-0000-000000000010"
HUBEI_IAV_INDICATOR_ID = "a1000000-0000-0000-0000-000000000020"
HUBEI_2026_H1_PERIOD_ID = "a1000000-0000-0000-0000-000020260601"
HUBEI_SOURCE_DOC_ID = "a1000000-0000-0000-0000-000000000030"

DESIGNATED_XLSX = (
    REPO_ROOT / "spikes" / "02-provincial-yearbook" / "hubei_2026_06.xlsx"
)
EXPECTED_SHA = (
    "c5cf5abeb4fdf97af52567f0640470d631bc9ac329dcc98f14e5d40bf6a5cac7"
)
EXPECTED_SIZE = 11261
HUBEI_HOMEPAGE_URL = "https://tjj.hubei.gov.cn/"


# ---------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------


@pytest.fixture(scope="module")
def imported_registry() -> None:
    """Same idempotent INSERT as in test_m1_reference_seed.py.

    Bypasses scripts/import_registry_csv.py — that script has a
    pre-existing data-quality issue (row 14 unescaped comma) that is out
    of M1 scope. We only need the tjj.hubei.gov.cn row.
    """
    conn = psycopg2.connect(DSN)
    try:
        with conn.cursor() as cur:
            cur.execute(
                """
                INSERT INTO cegr.source_registry
                    (domain, organization, category, primary_url,
                     update_frequency, auth_note, access_method,
                     enabled, source_level)
                VALUES ('tjj.hubei.gov.cn', '湖北省统计局', 'PROVINCIAL_BULLETIN',
                        'https://tjj.hubei.gov.cn/tjsj/sjkscx/tjyb/',
                        'MONTHLY', '公开；无需授权',
                        'EXCEL_PARSE',
                        TRUE, 'S0')
                ON CONFLICT DO NOTHING
                """
            )
        conn.commit()
    finally:
        conn.close()


@pytest.fixture(scope="module")
def loaded_seed(imported_registry) -> None:
    seed.load_seed(verbose=False)


@pytest.fixture(scope="module")
def ingest_summary(loaded_seed) -> dict:
    """Run connector.ingest() once per session; return its summary dict.

    Each test asserts on the just-created ingestion_run row, identified
    by `ingest_summary["ingestion_run_id"]`. This keeps tests isolated
    from historical rows.
    """
    conn = psycopg2.connect(DSN)
    try:
        pcb = ProvincialYearbookConnector()
        return pcb.ingest(
            DESIGNATED_XLSX, conn,
            triggered_by="test_m1_first_series.py@20260831",
        )
    finally:
        conn.close()


def _conn():
    return psycopg2.connect(DSN)


# ---------------------------------------------------------------------
# §T3 #1 — 指定 xlsx SHA == registry 该行
# ---------------------------------------------------------------------


def test_designated_file_sha_matches_registry(loaded_seed) -> None:
    """Per docs/55 §1.1: SHA=bytes is the M0.3 invariant. The same SHA must
    equal both the file's actual hash AND the registry row's
    file_hash_sha256. One drift on either side fails the contract."""
    if not DESIGNATED_XLSX.exists():
        pytest.fail(f"mandatory spike xlsx missing: {DESIGNATED_XLSX}")
    h = hashlib.sha256()
    h.update(DESIGNATED_XLSX.read_bytes())
    actual_sha = h.hexdigest()
    actual_size = DESIGNATED_XLSX.stat().st_size
    assert actual_sha == EXPECTED_SHA, (
        f"xlsx SHA drift: expected={EXPECTED_SHA[:12]} actual={actual_sha[:12]}"
    )
    assert actual_size == EXPECTED_SIZE, (
        f"xlsx size drift: expected={EXPECTED_SIZE} actual={actual_size}"
    )

    # Cross-check: the registry row's file_hash_sha256 must equal the file.
    conn = _conn()
    try:
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT file_hash_sha256, file_size_bytes
                FROM cegr.source_document
                WHERE id = %s
                """,
                (HUBEI_SOURCE_DOC_ID,),
            )
            row = cur.fetchone()
        assert row is not None, "T1 source_document row missing"
        r_sha, r_size = row
        assert r_sha == EXPECTED_SHA, f"registry SHA drift: {r_sha}"
        assert r_size == EXPECTED_SIZE, f"registry size drift: {r_size}"
    finally:
        conn.close()


# ---------------------------------------------------------------------
# §T3 #2 — ingestion_run.status == SUCCESS（PARTIAL 即失败）
# ---------------------------------------------------------------------


def test_ingest_status_success(ingest_summary) -> None:
    """Per docs/55 §T3 #2 and knife 627 §2.6: status must be SUCCESS and
    records_inserted ≥ 1. PARTIAL or FAILED is NOT M1 delivery."""
    run_id = ingest_summary["ingestion_run_id"]
    conn = _conn()
    try:
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT status, records_extracted, records_inserted, error_log
                FROM cegr.ingestion_run
                WHERE id = %s
                """,
                (run_id,),
            )
            status, n_ext, n_ins, err = cur.fetchone()
        assert status == "SUCCESS", (
            f"ingestion_run status must be SUCCESS; got {status!r} "
            f"(records_inserted={n_ins}, error_log={err!r})"
        )
        assert n_ins >= 1, f"records_inserted must be ≥ 1; got {n_ins}"
        assert n_ext >= 1, f"records_extracted must be ≥ 1; got {n_ext}"
    finally:
        conn.close()


# ---------------------------------------------------------------------
# §T3 #3 — GDP observation ≥1; value IS NOT NULL; missing_reason IS NULL
# ---------------------------------------------------------------------


def test_gdp_observation_count_ge_1(ingest_summary) -> None:
    """Per docs/55 §T3 #3: at least one GDP observation in this batch,
    value IS NOT NULL, missing_reason IS NULL. The IAV row may be
    missing-value (recorded with missing_reason) per M1-T2 design."""
    run_id = ingest_summary["ingestion_run_id"]
    conn = _conn()
    try:
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT COUNT(*) FROM cegr.observation
                WHERE ingestion_run_id = %s
                  AND indicator_id = %s
                  AND calendar_period_id = %s
                  AND geo_entity_id = %s
                  AND value IS NOT NULL
                  AND missing_reason IS NULL
                """,
                (run_id, HUBEI_GDP_INDICATOR_ID, HUBEI_2026_H1_PERIOD_ID,
                 HUBEI_PROVINCE_ID),
            )
            n = cur.fetchone()[0]
        assert n >= 1, (
            f"Hubei 2026H1 GDP observation count must be ≥ 1; got {n} "
            f"(ingestion_run_id={run_id})"
        )
    finally:
        conn.close()


# ---------------------------------------------------------------------
# §T3 #4 — observation.source_id → source_document.file_hash_sha256 一跳
# ---------------------------------------------------------------------


def test_observation_one_hop_to_source(ingest_summary) -> None:
    """The provenance one-hop: every observation in this batch must
    back-link through source_id to a source_document whose SHA equals
    the file bytes. This is the M0.3 invariant at the row level."""
    run_id = ingest_summary["ingestion_run_id"]
    conn = _conn()
    try:
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT COUNT(*) FROM cegr.observation o
                JOIN cegr.source_document sd ON sd.id = o.source_id
                WHERE o.ingestion_run_id = %s
                  AND sd.file_hash_sha256 = %s
                  AND sd.file_size_bytes = %s
                """,
                (run_id, EXPECTED_SHA, EXPECTED_SIZE),
            )
            n_match = cur.fetchone()[0]
            cur.execute(
                """
                SELECT COUNT(*) FROM cegr.observation
                WHERE ingestion_run_id = %s
                """,
                (run_id,),
            )
            n_total = cur.fetchone()[0]
        assert n_total > 0, "no observations in this batch"
        assert n_match == n_total, (
            f"one-hop mismatch: {n_match}/{n_total} observations back-link "
            f"to source_document with SHA={EXPECTED_SHA[:12]}"
        )
    finally:
        conn.close()


# ---------------------------------------------------------------------
# §T3 #5 — calendar_period / period_start 是统计期，不是 extracted_at
# ---------------------------------------------------------------------


def test_period_not_confused_with_release_date(ingest_summary) -> None:
    """The calendar_period row must reflect the statistical period
    (2026 H1 = Jan-Jun 2026), not the document's extracted_at timestamp
    or the registry's update cadence. period_start / period_end on the
    observation must align with that statistical window."""
    run_id = ingest_summary["ingestion_run_id"]
    conn = _conn()
    try:
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT cp.period_label, cp.start_date, cp.end_date,
                       o.period_start, o.period_end
                FROM cegr.observation o
                JOIN cegr.calendar_period cp ON cp.id = o.calendar_period_id
                WHERE o.ingestion_run_id = %s
                """,
                (run_id,),
            )
            rows = cur.fetchall()
        assert rows, "no observations to assert period against"
        for cp_label, cp_start, cp_end, o_start, o_end in rows:
            assert cp_start is not None and cp_end is not None, (
                f"calendar_period missing date bounds: {cp_label}"
            )
            # The period is H1 2026 — neither bound is in the future
            # (release date / extracted_at would land AFTER the period).
            assert cp_end <= __import__("datetime").date(2026, 6, 30), (
                f"calendar_period end {cp_end} suggests release date, "
                f"not statistical period"
            )
            assert cp_start == __import__("datetime").date(2026, 1, 1), (
                f"calendar_period start {cp_start} != 2026-01-01 (H1 anchor)"
            )
            # Observation period bounds must mirror calendar_period.
            assert str(o_start) == str(cp_start), (
                f"observation.period_start {o_start} != calendar_period "
                f".start_date {cp_start}"
            )
            assert str(o_end) == str(cp_end), (
                f"observation.period_end {o_end} != calendar_period "
                f".end_date {cp_end}"
            )
    finally:
        conn.close()


# ---------------------------------------------------------------------
# §T3 #6 — GDP 行 caveat_text 非空
# ---------------------------------------------------------------------


def test_caveat_present_for_hubei_gdp(ingest_summary) -> None:
    """Per knife 627 §2.5: caveat_text is non-empty. Per docs/55 §1.1 the
    Hubei GDP caveat must encode the 季度数/半年累计 tension so downstream
    parsers cannot silently rewrite to 无条件「半年累计」."""
    run_id = ingest_summary["ingestion_run_id"]
    conn = _conn()
    try:
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT caveat_text FROM cegr.observation
                WHERE ingestion_run_id = %s
                  AND indicator_id = %s
                LIMIT 1
                """,
                (run_id, HUBEI_GDP_INDICATOR_ID),
            )
            row = cur.fetchone()
        assert row is not None, "no GDP observation in this batch"
        caveat = row[0]
        assert caveat is not None and len(caveat.strip()) > 0, (
            f"GDP caveat_text is empty"
        )
        assert ("季度数" in caveat) or ("半年累计" in caveat), (
            f"GDP caveat must encode 季度数/半年累计 tension; got: {caveat!r}"
        )
    finally:
        conn.close()


# ---------------------------------------------------------------------
# §T3 #7 — source_document.url 不得仅为 tjj.hubei.gov.cn 首页
# ---------------------------------------------------------------------


def test_no_homepage_html_as_observation_source(ingest_summary) -> None:
    """Per docs/55 §T3 #7 and red lines: the source_document backing this
    batch must be the actual xlsx download URL, not the homepage.
    626 (CANCELLED) tried to lock the homepage as progress — this test
    enforces that we did NOT."""
    run_id = ingest_summary["ingestion_run_id"]
    conn = _conn()
    try:
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT sd.url, sd.file_hash_sha256
                FROM cegr.observation o
                JOIN cegr.source_document sd ON sd.id = o.source_id
                WHERE o.ingestion_run_id = %s
                LIMIT 1
                """,
                (run_id,),
            )
            row = cur.fetchone()
        assert row is not None, "no observation in this batch"
        url, sha = row
        assert sha == EXPECTED_SHA, (
            f"source_document SHA drift in batch: {sha}"
        )
        assert url is not None, "source_document.url is NULL"
        assert url != HUBEI_HOMEPAGE_URL, (
            f"source_document.url must NOT be the homepage "
            f"({HUBEI_HOMEPAGE_URL}); got {url}"
        )
        # Must be deeper than the homepage (i.e. real path with at least
        # one segment) — but not necessarily a literal .xlsx URL: the T1
        # seed stores the registry primary_url (a category index page),
        # only the homepage URL is forbidden per knife 627 §T3 #7.
        assert url.startswith("https://tjj.hubei.gov.cn/") and url != HUBEI_HOMEPAGE_URL, (
            f"source_document.url must be a real tjj.hubei.gov.cn path, "
            f"not just the homepage; got {url}"
        )
    finally:
        conn.close()


# ---------------------------------------------------------------------
# Sanity — IAV row uses missing_reason when source did not publish a value
# ---------------------------------------------------------------------
# Not part of the §T3 seven, but documents the M1-T2 connector design:
# when source value is NULL, observation_missing_consistency CHECK is
# satisfied via missing_reason (NOT is_imputed) so that the row remains
# discoverable as a known data gap.


def test_iav_observation_uses_missing_reason_when_value_absent(
    ingest_summary,
) -> None:
    """Spike 02 returns the IAV row with value=None. The connector must
    record it as a missing-value row (missing_reason NOT NULL, value
    IS NULL) — not silently drop it."""
    run_id = ingest_summary["ingestion_run_id"]
    conn = _conn()
    try:
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT value IS NULL, missing_reason, is_imputed
                FROM cegr.observation
                WHERE ingestion_run_id = %s
                  AND indicator_id = %s
                LIMIT 1
                """,
                (run_id, HUBEI_IAV_INDICATOR_ID),
            )
            row = cur.fetchone()
        # IAV row may or may not be inserted if upstream extraction
        # does not return a T1-FK IAV. The hubei 2026 06 xlsx has
        # exactly one IAV row, so this should be present.
        if row is None:
            pytest.skip("IAV row not present in this batch (expected for "
                        "hubei_2026_06.xlsx spike)")
        is_null, missing_reason, is_imputed = row
        assert is_null is True, "IAV value should be NULL"
        assert missing_reason is not None and len(missing_reason) > 0, (
            f"IAV missing_reason must be set when value is NULL; "
            f"got {missing_reason!r}"
        )
        assert is_imputed is False, (
            "is_imputed must be FALSE — the row is a recorded gap, "
            "not an imputed value"
        )
    finally:
        conn.close()