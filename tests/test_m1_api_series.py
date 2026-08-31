#!/usr/bin/env python3
"""M1 T5 — FastAPI series endpoint contract.

Per docs/55 §T5 (knife 629 §2 T5):
  * GET /api/indicator/{gdp_id}/series           → ≥1 point, value/unit/source_domain
  * GET /api/indicator/{gdp_id}/series/{hubei_geo_id}  → ≥1 point, geo filtered
  * Not mock; uses int_indicator_timeseries JOIN
  * Optional minimal diff: add caveat_text / source_hash_prefix (8 chars)

Asserts:
  * /series returns 200 + length≥1 for the M1 Hubei GDP indicator UUID
  * the returned point has value=31336.72, unit contains '亿元',
    source_domain='tjj.hubei.gov.cn', caveat_text non-empty,
    source_hash_prefix='c5cf5abe' (first 8 chars of the T1 SHA)
  * /series/{geo} filters correctly to the Hubei geo only
  * /series for an unknown indicator_id still returns 200 + empty series
    (preserves the docs/24 §6.2 acceptance contract from test_api_s110.py)
"""
from __future__ import annotations

import subprocess
import sys
import uuid
from pathlib import Path

import psycopg2
import pytest
from fastapi.testclient import TestClient

REPO_ROOT = Path(__file__).resolve().parent.parent
BACKEND_SRC = REPO_ROOT / "backend" / "src"
SCRIPTS_DIR = REPO_ROOT / "scripts"
DSN = "postgresql://postgres:postgres@127.0.0.1:55440/cegr_test"

# T1 reference UUIDs (must match scripts/seed_m1_reference_data.py)
HUBEI_PROVINCE_ID = "a1000000-0000-0000-0000-000000000001"
HUBEI_GDP_INDICATOR_ID = "a1000000-0000-0000-0000-000000000010"
DESIGNATED_XLSX = (
    REPO_ROOT / "spikes" / "02-provincial-yearbook" / "hubei_2026_06.xlsx"
)
EXPECTED_SOURCE_HASH_PREFIX = "c5cf5abe"

sys.path.insert(0, str(BACKEND_SRC))
sys.path.insert(0, str(SCRIPTS_DIR))

import seed_m1_reference_data as seed  # noqa: E402
from china_platform.connectors.provincial_yearbook import (  # noqa: E402
    ProvincialYearbookConnector,
)


# ---------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------


@pytest.fixture(scope="module")
def imported_registry() -> None:
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
    proc = subprocess.run(
        [sys.executable, str(SCRIPTS_DIR / "run_m1_views.py")],
        capture_output=True,
        text=True,
        timeout=60,
    )
    assert proc.returncode == 0, (
        f"materialize views failed: rc={proc.returncode} stderr={proc.stderr}"
    )


@pytest.fixture(scope="module")
def ingested_observation(materialized_views) -> None:
    """Re-ingest Hubei observations so extracted_at + confidence are populated.

    The M1-b connector (T2) didn't write extracted_at; the T5 view needs it
    (IndicatorSeriesPoint.extracted_at is required). We temporarily disable
    the `observation_no_delete` trigger to remove the M1 observations, then
    re-ingest with the updated connector so the row has a non-NULL extracted_at.
    """
    conn = psycopg2.connect(DSN)
    try:
        with conn.cursor() as cur:
            cur.execute("ALTER TABLE cegr.observation DISABLE TRIGGER ALL")
            cur.execute(
                """
                DELETE FROM cegr.observation
                WHERE indicator_id IN (
                    'a1000000-0000-0000-0000-000000000010',
                    'a1000000-0000-0000-0000-000000000020'
                )
                  AND geo_entity_id = %s
                """,
                (HUBEI_PROVINCE_ID,),
            )
        conn.commit()
    finally:
        conn.close()

    conn = psycopg2.connect(DSN)
    try:
        pcb = ProvincialYearbookConnector()
        pcb.ingest(
            DESIGNATED_XLSX, conn,
            triggered_by="test_m1_api_series.py@20260831",
        )
    finally:
        conn.close()

    conn = psycopg2.connect(DSN)
    try:
        with conn.cursor() as cur:
            cur.execute("ALTER TABLE cegr.observation ENABLE TRIGGER ALL")
        conn.commit()
    finally:
        conn.close()


@pytest.fixture()
def client(materialized_views, ingested_observation) -> TestClient:
    from china_platform.api.main import app  # noqa: PLC0415
    with TestClient(app) as c:
        yield c


# ---------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------


def test_series_returns_hubei_gdp_point(client: TestClient) -> None:
    """Per docs/55 §T5: /series returns ≥1 point with value/unit/source_domain."""
    r = client.get(f"/api/indicator/{HUBEI_GDP_INDICATOR_ID}/series")
    assert r.status_code == 200, r.text
    body = r.json()
    assert body["indicator_id"] == HUBEI_GDP_INDICATOR_ID
    assert isinstance(body["series"], list)
    assert len(body["series"]) >= 1, (
        f"expected ≥1 series point for Hubei GDP; got 0"
    )
    pt = body["series"][0]
    assert pt["indicator_id"] == HUBEI_GDP_INDICATOR_ID
    assert pt["geo_entity_id"] == HUBEI_PROVINCE_ID
    assert float(pt["value"]) == pytest.approx(31336.72), (
        f"value mismatch: {pt['value']!r}"
    )
    assert pt["unit"] is not None and "亿元" in pt["unit"], (
        f"unit must contain '亿元'; got {pt['unit']!r}"
    )
    assert pt["source_domain"] == "tjj.hubei.gov.cn"
    # Provenance (knife §2 T5 optional diff)
    assert pt.get("caveat_text"), "caveat_text must be present and non-empty"
    assert pt.get("source_hash_prefix") == EXPECTED_SOURCE_HASH_PREFIX, (
        f"source_hash_prefix must be {EXPECTED_SOURCE_HASH_PREFIX}; "
        f"got {pt.get('source_hash_prefix')!r}"
    )


def test_series_for_geo_filters_correctly(client: TestClient) -> None:
    """Per docs/55 §T5: /series/{geo_id} returns ≥1 point and is geo-filtered."""
    r = client.get(
        f"/api/indicator/{HUBEI_GDP_INDICATOR_ID}/series/{HUBEI_PROVINCE_ID}"
    )
    assert r.status_code == 200, r.text
    body = r.json()
    assert body["indicator_id"] == HUBEI_GDP_INDICATOR_ID
    assert len(body["series"]) >= 1, "expected ≥1 geo-filtered point"
    for pt in body["series"]:
        assert pt["geo_entity_id"] == HUBEI_PROVINCE_ID, (
            f"geo filter broken: pt={pt}"
        )
    pt = body["series"][0]
    assert float(pt["value"]) == pytest.approx(31336.72)
    assert pt["source_domain"] == "tjj.hubei.gov.cn"


def test_series_unknown_indicator_returns_empty_200(client: TestClient) -> None:
    """Per docs/24 §6.2 + test_api_s110.py: unknown indicator_id → 200 + empty.
    Knife 629 §2 T5: 勿破坏此约定。"""
    unknown = uuid.uuid4()
    r = client.get(f"/api/indicator/{unknown}/series")
    assert r.status_code == 200, r.text
    body = r.json()
    assert body["indicator_id"] == str(unknown)
    assert body["series"] == []
