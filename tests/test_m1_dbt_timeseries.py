#!/usr/bin/env python3
"""M1 T4 — dbt/staging view contract.

Per docs/55 §T4 (knife 629 §2 T4): the cegr_staging
int_indicator_timeseries view must contain the Hubei 2026H1 GDP row
that was inserted by the M1-b T2 ingest. This proves the SQL pipeline
(`cegr.observation` → `stg_observation` JOIN `stg_source_document` →
`int_indicator_timeseries`) reaches the read surface.

Asserts:
  * The 3 views exist in cegr_staging.
  * int_indicator_timeseries contains the Hubei 2026H1 GDP row:
    value=31336.72, unit='亿元', source_domain='tjj.hubei.gov.cn'.

Required fixtures:
  * cegr_test DSN reachable at postgresql://postgres:postgres@127.0.0.1:55440/cegr_test
  * T1 reference data seeded + T2 ingest run (provides the 2 observations)
  * Materialize views: `scripts/materialize_m1_views.sql`
"""
from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import psycopg2
import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent
BACKEND_SRC = REPO_ROOT / "backend" / "src"
SCRIPTS_DIR = REPO_ROOT / "scripts"
DSN = "postgresql://postgres:postgres@127.0.0.1:55440/cegr_test"

sys.path.insert(0, str(BACKEND_SRC))
sys.path.insert(0, str(SCRIPTS_DIR))

import seed_m1_reference_data as seed  # noqa: E402
from china_platform.connectors.provincial_yearbook import (  # noqa: E402
    ProvincialYearbookConnector,
)

HUBEI_PROVINCE_ID = "a1000000-0000-0000-0000-000000000001"
HUBEI_GDP_INDICATOR_ID = "a1000000-0000-0000-0000-000000000010"
EXPECTED_VALUE = 31336.72
EXPECTED_SOURCE_DOMAIN = "tjj.hubei.gov.cn"
DESIGNATED_XLSX = (
    REPO_ROOT / "spikes" / "02-provincial-yearbook" / "hubei_2026_06.xlsx"
)


# ---------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------


@pytest.fixture(scope="module")
def imported_registry() -> None:
    """Idempotent INSERT of tjj.hubei.gov.cn / PROVINCIAL_BULLETIN row.

    Bypasses scripts/import_registry_csv.py (row 14 unescaped comma is a
    pre-existing data quality issue outside M1 scope).
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
def materialized_views(loaded_seed) -> None:
    """Run scripts/run_m1_views.py to (re)create the 3 cegr_staging views.

    dbt run is unavailable in this environment (Python 3.14 incompatibility);
    the SQL script creates views with the same semantics as the dbt Jinja
    originals (knife 629 §2 T4 Approach B).
    """
    proc = subprocess.run(
        [sys.executable, str(SCRIPTS_DIR / "run_m1_views.py")],
        capture_output=True,
        text=True,
        timeout=60,
    )
    assert proc.returncode == 0, (
        f"materialize views failed: rc={proc.returncode} "
        f"stderr={proc.stderr}"
    )


@pytest.fixture(scope="module")
def ingested_observation(materialized_views) -> None:
    """Run T2 connector.ingest() so int_indicator_timeseries has a row.

    Re-runs even if observations already exist (idempotent via natural
    key UNIQUE NULLS NOT DISTINCT — the second INSERT would fail and
    fall back to missing_reason branch).
    """
    conn = psycopg2.connect(DSN)
    try:
        # Check whether the GDP observation already exists.
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT COUNT(*) FROM cegr.observation
                WHERE indicator_id = %s
                  AND geo_entity_id = %s
                  AND calendar_period_id = %s
                  AND value IS NOT NULL
                """,
                (
                    HUBEI_GDP_INDICATOR_ID,
                    HUBEI_PROVINCE_ID,
                    "a1000000-0000-0000-0000-000020260601",
                ),
            )
            n = cur.fetchone()[0]
        if n >= 1:
            return  # already there; nothing to do
        pcb = ProvincialYearbookConnector()
        pcb.ingest(
            DESIGNATED_XLSX, conn,
            triggered_by="test_m1_dbt_timeseries.py@20260831",
        )
    finally:
        conn.close()


def _conn():
    return psycopg2.connect(DSN)


# ---------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------


def test_three_views_exist(materialized_views) -> None:
    """The 3 dbt-mirrored views must be present in cegr_staging."""
    expected = {
        "cegr_staging.stg_observation",
        "cegr_staging.stg_source_document",
        "cegr_staging.int_indicator_timeseries",
    }
    conn = _conn()
    try:
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT table_schema || '.' || table_name AS fqtn
                FROM information_schema.tables
                WHERE table_schema = 'cegr_staging'
                  AND table_name IN ('stg_observation', 'stg_source_document',
                                     'int_indicator_timeseries')
                """
            )
            present = {r[0] for r in cur.fetchall()}
    finally:
        conn.close()
    missing = expected - present
    assert not missing, (
        f"missing cegr_staging views: {missing} (present: {present})"
    )


def test_int_indicator_timeseries_has_hubei_gdp_row(ingested_observation) -> None:
    """Per docs/55 §T4: the Hubei 2026H1 GDP point must be visible in
    int_indicator_timeseries with the expected value, unit, and
    source_domain."""
    conn = _conn()
    try:
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT value, unit, source_domain, period_start, period_end
                FROM cegr_staging.int_indicator_timeseries
                WHERE indicator_id = %s
                  AND geo_entity_id = %s
                """,
                (HUBEI_GDP_INDICATOR_ID, HUBEI_PROVINCE_ID),
            )
            row = cur.fetchone()
    finally:
        conn.close()
    assert row is not None, (
        "int_indicator_timeseries missing the Hubei 2026H1 GDP row"
    )
    value, unit, source_domain, period_start, period_end = row
    assert float(value) == pytest.approx(EXPECTED_VALUE), (
        f"Hubei GDP value mismatch: expected={EXPECTED_VALUE} got={value}"
    )
    assert unit is not None and "亿元" in unit, (
        f"Hubei GDP unit must contain '亿元'; got {unit!r}"
    )
    assert source_domain == EXPECTED_SOURCE_DOMAIN, (
        f"source_domain must be {EXPECTED_SOURCE_DOMAIN}; got {source_domain!r}"
    )
    assert str(period_start) == "2026-01-01", (
        f"period_start must be 2026-01-01; got {period_start}"
    )
    assert str(period_end) == "2026-06-30", (
        f"period_end must be 2026-06-30; got {period_end}"
    )


def test_int_indicator_timeseries_excludes_null_values(
    materialized_views,
) -> None:
    """Per the int_indicator_timeseries definition: `WHERE o.value IS NOT NULL`.
    The IAV row has value=NULL — it must NOT appear in the view (its
    row stays in cegr.observation + stg_observation but is filtered
    from the timeseries surface)."""
    conn = _conn()
    try:
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT COUNT(*) FROM cegr_staging.int_indicator_timeseries
                WHERE value IS NULL
                """
            )
            n_null = cur.fetchone()[0]
    finally:
        conn.close()
    assert n_null == 0, (
        f"int_indicator_timeseries must exclude NULL values; found {n_null}"
    )
