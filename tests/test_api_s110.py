"""Stage 1 / S1.10 — FastAPI integration tests.

Per docs/24 §8 (≥9 tests).

Strategy:
  - Session-scoped autouse fixture seeds minimal data via raw SQL on a
    SEPARATE connection (the API session is read-only, so we can't seed
    through it).
  - Tests use the FastAPI TestClient against the lifespan-managed app.
  - DB is the same cegr_test that conftest applied schema to.
"""
from __future__ import annotations

import os
import subprocess
import sys
import uuid
from pathlib import Path
from typing import Iterator

# Ensure backend/src is on sys.path so `china_platform.*` imports resolve.
_BACKEND_SRC = Path(__file__).resolve().parents[1] / "backend" / "src"
if str(_BACKEND_SRC) not in sys.path:
    sys.path.insert(0, str(_BACKEND_SRC))

import psycopg2
import psycopg2.extras
import pytest
from fastapi.testclient import TestClient

from china_platform.api.main import app


DSN = os.environ.get(
    "STAGE0_DSN",
    "host=127.0.0.1 port=55440 user=postgres dbname=cegr_test",
)

# Stable UUIDs so tests can deterministically query seeded rows.
INDICATOR_ID = uuid.UUID("11111111-1111-1111-1111-111111111111")
INDICATOR_ID_2 = uuid.UUID("22222222-2222-2222-2222-222222222222")
GEO_ID = uuid.UUID("aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa")
GEO_ID_2 = uuid.UUID("bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbbbbb")
CALENDAR_PERIOD_ID = uuid.UUID("33333333-3333-3333-3333-333333333333")
SOURCE_ID = uuid.UUID("44444444-4444-4444-4444-444444444444")
SOURCE_DOC_ID = uuid.UUID("55555555-5555-5555-5555-555555555555")
RUN_ID = uuid.UUID("66666666-6666-6666-6666-666666666666")
OBS_ID_1 = uuid.UUID("77777777-7777-7777-7777-777777777777")
OBS_ID_2 = uuid.UUID("88888888-8888-8888-8888-888888888888")


def _connect() -> psycopg2.extensions.connection:
    return psycopg2.connect(DSN)


GEO_CODE_VERSION_ID = uuid.UUID("cccccccc-cccc-cccc-cccc-cccccccccccc")
INDICATOR_MV_ID = uuid.UUID("dddddddd-dddd-dddd-dddd-dddddddddddd")
SOURCE_LOC_ID = uuid.UUID("eeeeeeee-eeee-eeee-eeee-eeeeeeeeeeee")


def _seed() -> None:
    """Insert minimal fixture rows into cegr tables.

    Idempotent: uses INSERT ... ON CONFLICT DO NOTHING.
    Satisfies all observation FKs: indicator_methodology_version_id,
    geo_code_version_id, source_location_id, source_id.
    """
    psycopg2.extras.register_uuid()
    with _connect() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                INSERT INTO cegr.source_registry
                    (id, domain, organization, category, primary_url,
                     access_method, source_level, declared_source_level,
                     update_frequency, enabled)
                VALUES (%s, 'stats.gov.cn', '国家统计局',
                        'NATIONAL_BULLETIN', 'https://stats.gov.cn/test',
                        'HTML_PARSE', 'S1', 'S1', 'ANNUAL', TRUE)
                ON CONFLICT (id) DO NOTHING
                """,
                (str(SOURCE_ID),),
            )
            cur.execute(
                """
                INSERT INTO cegr.source_document
                    (id, source_registry_id, source_level, verification_status,
                     title, publisher, file_hash_sha256)
                VALUES (%s, %s, 'S1', 'VERIFIED',
                        'Test document', '国家统计局',
                        %s)
                ON CONFLICT (id) DO NOTHING
                """,
                (str(SOURCE_DOC_ID), str(SOURCE_ID), 'a' * 64),
            )
            cur.execute(
                """
                INSERT INTO cegr.calendar_period
                    (id, start_date, end_date, period_type, period_label,
                     fy_label, raw_label, period_basis)
                VALUES (%s, '2024-01-01', '2024-12-31', 'ANNUAL', '2024',
                        'FY2024', '2024', 'INSTANTANEOUS')
                ON CONFLICT (id) DO NOTHING
                """,
                (str(CALENDAR_PERIOD_ID),),
            )
            cur.execute(
                """
                INSERT INTO cegr.geo_entity
                    (id, canonical_name, canonical_name_en, level, parent_id)
                VALUES (%s, 'Test Geo A', 'Test Geo A', 'COUNTRY', NULL),
                       (%s, 'Test Geo B', 'Test Geo B', 'PROVINCE', NULL)
                ON CONFLICT (id) DO NOTHING
                """,
                (str(GEO_ID), str(GEO_ID_2)),
            )
            cur.execute(
                """
                INSERT INTO cegr.geo_code_version
                    (id, geo_entity_id, iso_code, valid_from, source_id)
                VALUES (%s, %s, 'TGA', '2024-01-01'::date, %s),
                       (%s, %s, 'TGB', '2024-01-01'::date, %s)
                ON CONFLICT (id) DO NOTHING
                """,
                (str(GEO_CODE_VERSION_ID), str(GEO_ID), str(SOURCE_DOC_ID),
                 uuid.UUID("99999999-9999-9999-9999-999999999999"),
                 str(GEO_ID_2), str(SOURCE_DOC_ID)),
            )
            cur.execute(
                """
                INSERT INTO cegr.indicator_definition
                    (id, canonical_name, canonical_name_en, unit_canonical,
                     frequency, geo_scope_default)
                VALUES (%s, '测试指标A', 'Test Indicator A', '亿元',
                        'ANNUAL', 'COUNTRY'),
                       (%s, '测试指标B', 'Test Indicator B', '万吨',
                        'ANNUAL', 'COUNTRY')
                ON CONFLICT (id) DO NOTHING
                """,
                (str(INDICATOR_ID), str(INDICATOR_ID_2)),
            )
            cur.execute(
                """
                INSERT INTO cegr.indicator_methodology_version
                    (id, indicator_id, version_label, valid_from, valid_to,
                     change_summary, source_id)
                VALUES (%s, %s, 'v1.0', '2024-01-01'::date, NULL,
                        'Initial methodology', %s),
                       (%s, %s, 'v1.0', '2024-01-01'::date, NULL,
                        'Initial methodology', %s)
                ON CONFLICT (id) DO NOTHING
                """,
                (str(INDICATOR_MV_ID), str(INDICATOR_ID), str(SOURCE_DOC_ID),
                 uuid.UUID("aaaaaaaa-bbbb-cccc-dddd-eeeeeeeeeeee"),
                 str(INDICATOR_ID_2), str(SOURCE_DOC_ID)),
            )
            cur.execute(
                """
                INSERT INTO cegr.source_location
                    (id, source_document_id, sheet_name, page_number,
                     cell_range)
                VALUES (%s, %s, 'Sheet1', 1, 'A1:B10')
                ON CONFLICT (id) DO NOTHING
                """,
                (str(SOURCE_LOC_ID), str(SOURCE_DOC_ID)),
            )
            cur.execute(
                """
                INSERT INTO cegr.ingestion_run
                    (id, source_registry_id, status, started_at, finished_at,
                     records_extracted, records_inserted, records_updated,
                     triggered_by)
                VALUES (%s, %s, 'SUCCESS', NOW() - INTERVAL '1 hour',
                        NOW() - INTERVAL '55 minutes', 100, 95, 5, 'TEST')
                ON CONFLICT (id) DO NOTHING
                """,
                (str(RUN_ID), str(SOURCE_ID)),
            )
            cur.execute(
                """
                INSERT INTO cegr.observation
                    (id, indicator_id, indicator_methodology_version_id,
                     geo_entity_id, geo_code_version_id, calendar_period_id,
                     value, raw_value, unit, is_imputed, missing_reason,
                     value_type, status, comparison_basis, source_id,
                     source_location_id, ingestion_run_id, extraction_method,
                     confidence, period_start, period_end, period_label,
                     period_type, lineage, caveat_text, extracted_at)
                VALUES
                    (%s, %s, %s, %s, %s, %s, 12345.67, '12345.67',
                     '亿元', FALSE, NULL, 'FACT', 'FINAL', 'CUMULATIVE', %s,
                     %s, %s, 'HTML_PARSE', 0.95, '2024-01-01',
                     '2024-12-31', '2024', 'ANNUAL',
                     '{"source_file_sha256": "abc"}'::jsonb, NULL,
                     NOW() - INTERVAL '50 minutes'),
                    (%s, %s, %s, %s, %s, %s, 67890.12, '67890.12',
                     '万吨', FALSE, NULL, 'FACT', 'FINAL', 'CUMULATIVE', %s,
                     %s, %s, 'HTML_PARSE', 0.88, '2024-01-01',
                     '2024-12-31', '2024', 'ANNUAL',
                     '{"source_file_sha256": "def"}'::jsonb, NULL,
                     NOW() - INTERVAL '40 minutes')
                ON CONFLICT (id) DO NOTHING
                """,
                (
                    str(OBS_ID_1), str(INDICATOR_ID), str(INDICATOR_MV_ID),
                    str(GEO_ID), str(GEO_CODE_VERSION_ID),
                    str(CALENDAR_PERIOD_ID), str(SOURCE_DOC_ID),
                    str(SOURCE_LOC_ID), str(RUN_ID),
                    str(OBS_ID_2), str(INDICATOR_ID_2),
                    uuid.UUID("aaaaaaaa-bbbb-cccc-dddd-eeeeeeeeeeee"),
                    str(GEO_ID_2),
                    uuid.UUID("99999999-9999-9999-9999-999999999999"),
                    str(CALENDAR_PERIOD_ID), str(SOURCE_DOC_ID),
                    str(SOURCE_LOC_ID), str(RUN_ID),
                ),
            )
        conn.commit()


@pytest.fixture(scope="session", autouse=True)
def _seed_test_data() -> Iterator[None]:
    """Seed test data once per pytest session + rebuild dbt staging views.

    The conftest does DROP SCHEMA cegr CASCADE at session start, which also
    drops cegr_staging views. After apply + seed, we rebuild the views so
    the API can read from them.
    """
    try:
        _seed()
    except Exception as e:
        pytest.skip(f"DB seed failed (is cegr_test reachable?): {e}", allow_module_level=True)

    # Rebuild dbt views (cegr_staging.*) — required by the API endpoints.
    repo_root = _BACKEND_SRC.parent.parent
    dbt_dir = repo_root / "dbt"
    dbt_venv = Path("/tmp/dbt_venv/bin/dbt")
    if dbt_venv.exists() and dbt_dir.is_dir():
        subprocess.run(
            [str(dbt_venv), "run", "--select", "staging+",
             "--profiles-dir", str(dbt_dir)],
            cwd=str(dbt_dir),
            capture_output=True, text=True, timeout=60,
        )
    yield


@pytest.fixture()
def client() -> Iterator[TestClient]:
    """Per-test FastAPI TestClient with lifespan."""
    with TestClient(app) as c:
        yield c


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------


def test_health_ok(client: TestClient) -> None:
    r = client.get("/health")
    assert r.status_code == 200, r.text
    body = r.json()
    assert body["status"] == "ok"
    assert body["db_reachable"] is True
    assert "timestamp_utc" in body


def test_openapi_schema(client: TestClient) -> None:
    r = client.get("/openapi.json")
    assert r.status_code == 200
    body = r.json()
    assert body["info"]["title"] == "CEGR Read-only API"
    # core endpoint present
    paths = body["paths"]
    assert "/api/indicator/{indicator_id}/series" in paths
    assert "/api/source/{source_id}" in paths
    assert "/api/observation/{observation_id}" in paths


def test_docs_swagger(client: TestClient) -> None:
    r = client.get("/docs")
    assert r.status_code == 200
    assert "swagger" in r.text.lower()


def test_indicator_list_returns_seeded(client: TestClient) -> None:
    r = client.get("/api/indicator?page_size=10")
    assert r.status_code == 200
    body = r.json()
    assert "indicators" in body
    assert "pagination" in body
    # at least our 2 seeded indicators should be visible
    ids = {i["indicator_id"] for i in body["indicators"]}
    assert str(INDICATOR_ID) in ids
    assert str(INDICATOR_ID_2) in ids
    # pagination shape
    p = body["pagination"]
    assert p["page"] == 1
    assert p["page_size"] == 10
    assert p["total_count"] >= 2


def test_indicator_series_returns_points(client: TestClient) -> None:
    r = client.get(f"/api/indicator/{INDICATOR_ID}/series")
    assert r.status_code == 200
    body = r.json()
    assert body["indicator_id"] == str(INDICATOR_ID)
    assert isinstance(body["series"], list)
    assert len(body["series"]) >= 1
    p = body["series"][0]
    assert p["indicator_id"] == str(INDICATOR_ID)
    assert p["geo_entity_id"] == str(GEO_ID)
    assert p["value"] == 12345.67
    assert p["source_domain"] == "stats.gov.cn"
    assert p["extraction_method"] == "HTML_PARSE"
    assert p["confidence"] == pytest.approx(0.95)


def test_indicator_series_empty_for_unknown_id(client: TestClient) -> None:
    """Per docs/24 §6.2 — unknown indicator returns 200 + empty series (not 404)."""
    unknown = uuid.uuid4()
    r = client.get(f"/api/indicator/{unknown}/series")
    assert r.status_code == 200
    body = r.json()
    assert body["indicator_id"] == str(unknown)
    assert body["series"] == []


def test_indicator_series_for_geo_filters(client: TestClient) -> None:
    r = client.get(f"/api/indicator/{INDICATOR_ID}/series/{GEO_ID}")
    assert r.status_code == 200
    body = r.json()
    assert len(body["series"]) >= 1
    for pt in body["series"]:
        assert pt["geo_entity_id"] == str(GEO_ID)


def test_source_list_contains_seeded(client: TestClient) -> None:
    r = client.get("/api/source")
    assert r.status_code == 200
    body = r.json()
    ids = {s["source_id"] for s in body["sources"]}
    assert str(SOURCE_ID) in ids
    # enabled_only filter
    r2 = client.get("/api/source?enabled_only=true")
    assert r2.status_code == 200


def test_source_get_404_for_unknown(client: TestClient) -> None:
    unknown = uuid.uuid4()
    r = client.get(f"/api/source/{unknown}")
    assert r.status_code == 404
    body = r.json()
    assert body["error_code"] == "SOURCE_NOT_FOUND"
    assert body["detail"]["resource"] == "source"


def test_source_get_seeded(client: TestClient) -> None:
    r = client.get(f"/api/source/{SOURCE_ID}")
    assert r.status_code == 200
    body = r.json()
    assert body["source_id"] == str(SOURCE_ID)
    assert body["domain"] == "stats.gov.cn"
    assert body["enabled"] is True


def test_source_coverage(client: TestClient) -> None:
    r = client.get(f"/api/source/{SOURCE_ID}/coverage")
    assert r.status_code == 200
    body = r.json()
    assert body["source_id"] == str(SOURCE_ID)
    assert body["total_runs"] >= 1
    assert body["success_runs"] >= 1
    assert body["total_extracted"] >= 100
    assert body["total_inserted"] >= 1


def test_source_coverage_404_for_unknown(client: TestClient) -> None:
    unknown = uuid.uuid4()
    r = client.get(f"/api/source/{unknown}/coverage")
    assert r.status_code == 404
    assert r.json()["error_code"] == "SOURCE_NOT_FOUND"


def test_source_runs_returns_seeded(client: TestClient) -> None:
    r = client.get(f"/api/source/{SOURCE_ID}/runs")
    assert r.status_code == 200
    body = r.json()
    assert body["source_id"] == str(SOURCE_ID)
    assert len(body["runs"]) >= 1
    run = body["runs"][0]
    assert run["status"] == "SUCCESS"
    assert run["duration_seconds"] is not None
    assert run["duration_seconds"] >= 0


def test_observation_list_filtered(client: TestClient) -> None:
    r = client.get(f"/api/observation?indicator_id={INDICATOR_ID}")
    assert r.status_code == 200
    body = r.json()
    ids = {o["observation_id"] for o in body["observations"]}
    assert str(OBS_ID_1) in ids
    for obs in body["observations"]:
        assert obs["indicator_id"] == str(INDICATOR_ID)


def test_observation_get_seeded(client: TestClient) -> None:
    r = client.get(f"/api/observation/{OBS_ID_1}")
    assert r.status_code == 200
    body = r.json()
    assert body["observation_id"] == str(OBS_ID_1)
    assert body["value"] == 12345.67
    assert body["unit"] == "亿元"


def test_observation_get_404_for_unknown(client: TestClient) -> None:
    unknown = uuid.uuid4()
    r = client.get(f"/api/observation/{unknown}")
    assert r.status_code == 404
    assert r.json()["error_code"] == "OBSERVATION_NOT_FOUND"


def test_invalid_uuid_422(client: TestClient) -> None:
    r = client.get("/api/indicator/not-a-uuid/series")
    assert r.status_code == 422


def test_page_size_too_large_422(client: TestClient) -> None:
    """FastAPI native Query validation returns 422 for page_size > le=500."""
    r = client.get("/api/source?page_size=10000")
    assert r.status_code == 422
    body = r.json()
    # FastAPI validation error structure
    assert "detail" in body


def test_source_runs_404_for_unknown(client: TestClient) -> None:
    unknown = uuid.uuid4()
    r = client.get(f"/api/source/{unknown}/runs")
    assert r.status_code == 404
    assert r.json()["error_code"] == "SOURCE_NOT_FOUND"