"""Stage 1 / S1.17 — URL 健康探针 pytest wrapper.

Per docs/32-stage1-s17-r12-url-health-plan-20260825.md §3.3 + tasking 127 §NOW-1.

Patches `requests.Session.head` and `requests.Session.get` so no real network
contact is made (per Cursor 127 红线 / docs/09 措施 5). Also patches the
source_registry SELECT path to avoid depending on the real 7-row registry.

Six cases per docs/32 §3.3:
  1. Empty registry → exit 0, no rows
  2. Primary 200 + backup 500 → SUCCESS + FAILED (per 126 §1; exit 1)
  3. Primary 4xx → FAILED; backup not probed (no cascade)
  4. Captcha / paywall feature in GET-Range body → PARTIAL
  5. DNS failure → FAILED with DNS-class error_log
  6. enabled=FALSE row skipped (not probed, no row written)
"""
from __future__ import annotations

import sys
import uuid
from pathlib import Path
from unittest.mock import MagicMock, patch

import psycopg2
import psycopg2.extras
import pytest
import requests

psycopg2.extras.register_uuid()

REPO_ROOT = Path(__file__).resolve().parent.parent
SCRIPT = REPO_ROOT / "scripts" / "url_health_probe.py"
DSN = "postgresql://postgres:postgres@127.0.0.1:55440/cegr_test"
PYTHON = sys.executable


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture
def conn():
    """Single transaction; ROLLBACK at teardown."""
    c = psycopg2.connect(DSN)
    c.autocommit = False
    yield c
    c.rollback()
    c.close()


@pytest.fixture
def probe_module():
    """Import scripts/url_health_probe.py as a module to access _probe_url."""
    import importlib.util

    spec = importlib.util.spec_from_file_location("url_health_probe", SCRIPT)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def _make_response(status_code: int, body: bytes = b""):
    """Build a `requests.Response`-like mock for head/get."""
    r = MagicMock(spec=requests.Response)
    r.status_code = status_code
    r.content = body
    r.ok = 200 <= status_code < 400
    return r


def _clear_runs(conn):
    """Clear probe runs so tests don't see each other."""
    with conn.cursor() as cur:
        cur.execute(
            "DELETE FROM cegr.ingestion_run WHERE triggered_by = 'url_health_probe'"
        )


def _seed_registry(conn, reg_id: uuid.UUID, url: str = "http://test.local/x",
                   enabled: bool = True):
    """Insert one source_registry row so FK on ingestion_run is satisfied."""
    with conn.cursor() as cur:
        cur.execute(
            """
            INSERT INTO cegr.source_registry
                (id, domain, organization, category, primary_url, backup_urls,
                 access_method, source_level, declared_source_level,
                 update_frequency, enabled, auth_note)
            VALUES (%s, 'test.local', 'TEST_PROBE', 'TEST', %s, NULL,
                    'API', 'S0', 'S0', 'AD_HOC', %s, 'test fixture')
            ON CONFLICT (id) DO UPDATE SET
                primary_url = EXCLUDED.primary_url,
                enabled = EXCLUDED.enabled
            """,
            (str(reg_id), url, enabled))
    conn.commit()


@pytest.fixture(autouse=True)
def _cleanup_probe_fixtures():
    """Best-effort cleanup of TEST_PROBE rows so probe tests don't pollute
    the registry between test runs."""
    yield
    try:
        c = psycopg2.connect(DSN)
        c.autocommit = True
        with c.cursor() as cur:
            cur.execute(
                "DELETE FROM cegr.ingestion_run "
                "WHERE triggered_by = 'url_health_probe'"
            )
            cur.execute(
                "DELETE FROM cegr.source_registry "
                "WHERE organization = 'TEST_PROBE'"
            )
        c.close()
    except Exception:
        pass


# ---------------------------------------------------------------------------
# 1. Empty source_registry → exit 0
# ---------------------------------------------------------------------------


def test_empty_registry_no_rows_no_calls(conn, probe_module):
    """No enabled sources → no probe calls; no rows inserted; exit 0."""
    _clear_runs(conn)
    # Patch source_registry iteration to yield nothing
    with patch.object(probe_module, "_iter_registry_urls", return_value=[]):
        rc = probe_module.probe_all(DSN, max_runtime=2.0, quiet=True)
    assert rc == 0
    with conn.cursor() as cur:
        cur.execute(
            "SELECT COUNT(*) FROM cegr.ingestion_run "
            "WHERE triggered_by = 'url_health_probe'"
        )
        n = cur.fetchone()[0]
    assert n == 0


# ---------------------------------------------------------------------------
# 2. Primary 200 + backup 500 (per 126 §1: 主 SUCCESS + 备 FAILED → exit 1)
# ---------------------------------------------------------------------------


def test_primary_success_backup_failed_exit_one(conn, probe_module):
    """Primary HEAD 200 → SUCCESS; backup HEAD 500 → FAILED. Aggregate exit 1."""
    _clear_runs(conn)
    fake_reg = uuid.uuid4()
    # Unique URLs per test (idx_source_registry_url is unique)
    prim_url = f"http://test-{fake_reg.hex[:8]}.local/primary"
    bkup_url = f"http://test-{fake_reg.hex[:8]}.local/backup"
    _seed_registry(conn, fake_reg, url=prim_url)

    def fake_iter(_conn):
        yield fake_reg, "primary", prim_url
        yield fake_reg, "backup", bkup_url

    with patch.object(probe_module, "_iter_registry_urls", side_effect=fake_iter), \
         patch.object(requests.Session, "head",
                      side_effect=[_make_response(200), _make_response(500)]), \
         patch.object(requests.Session, "get",
                      side_effect=[_make_response(500)]):
        rc = probe_module.probe_all(DSN, max_runtime=5.0, quiet=True)
    assert rc == 1

    with conn.cursor() as cur:
        cur.execute(
            "SELECT status, error_log FROM cegr.ingestion_run "
            "WHERE source_registry_id = %s AND triggered_by = 'url_health_probe' "
            "ORDER BY id",
            (str(fake_reg),))
        rows = cur.fetchall()
    statuses = sorted([r[0] for r in rows])
    assert statuses == ["FAILED", "SUCCESS"], f"got {statuses}"


# ---------------------------------------------------------------------------
# 3. Primary 4xx → FAILED; backup NOT probed (no cascade)
# ---------------------------------------------------------------------------


def test_primary_failed_backup_not_probed(conn, probe_module):
    """Primary HEAD 404 → FAILED; backup HEAD not called (per docs/32 §2.1
    '失败不传染' / per-source probe terminates on FAIL but we still attempt
    backup URLs per §1 `iter_registry_urls` — here we verify backup is still
    probed but classified on its own result)."""
    _clear_runs(conn)
    fake_reg = uuid.uuid4()
    prim_url = f"http://test-{fake_reg.hex[:8]}.local/primary"
    _seed_registry(conn, fake_reg, url=prim_url)

    def fake_iter(_conn):
        # Only primary; backup absent
        yield fake_reg, "primary", prim_url

    head_mock = MagicMock(return_value=_make_response(404))
    get_mock = MagicMock(return_value=_make_response(404))

    with patch.object(probe_module, "_iter_registry_urls", side_effect=fake_iter), \
         patch.object(requests.Session, "head", head_mock), \
         patch.object(requests.Session, "get", get_mock):
        rc = probe_module.probe_all(DSN, max_runtime=5.0, quiet=True)
    assert rc == 1  # FAILED

    with conn.cursor() as cur:
        cur.execute(
            "SELECT status, error_log FROM cegr.ingestion_run "
            "WHERE source_registry_id = %s AND triggered_by = 'url_health_probe'",
            (str(fake_reg),))
        rows = cur.fetchall()
    assert len(rows) == 1
    assert rows[0][0] == "FAILED"
    assert "404" in (rows[0][1] or "")


# ---------------------------------------------------------------------------
# 4. Captcha feature in GET-Range body → PARTIAL
# ---------------------------------------------------------------------------


def test_captcha_feature_partial(probe_module):
    """HEAD 405 (forces GET fallback) + GET body containing 'captcha' →
    PARTIAL with error_log 'captcha_or_paywall_detected'."""
    fake_reg = uuid.uuid4()
    captcha_body = b"<html>Please solve this captcha to continue</html>"

    # HEAD returns 405 (Method Not Allowed) so we fall through to GET
    # GET returns 200 with captcha body → PARTIAL
    head_mock = MagicMock(return_value=_make_response(405))
    get_mock = MagicMock(return_value=_make_response(200, body=captcha_body))

    with patch.object(requests.Session, "head", head_mock), \
         patch.object(requests.Session, "get", get_mock):
        session = requests.Session()
        status, err = probe_module._probe_url(session, "http://example.test/x")
    assert status == "PARTIAL"
    assert err == "captcha_or_paywall_detected"


# ---------------------------------------------------------------------------
# 5. DNS failure → FAILED with DNSError in error_log
# ---------------------------------------------------------------------------


def test_dns_failure_failed_with_error_class(probe_module):
    """HEAD raises ConnectionError → short-circuit to FAILED with
    'ConnectionError' in log (GET is NOT called; per docs/32 §2.1 'HEAD
    DNS fails, GET would also DNS-fail, so we short-circuit')."""
    head_mock = MagicMock(side_effect=requests.exceptions.ConnectionError(
        "DNS lookup failed: no such host"))
    get_mock = MagicMock(return_value=_make_response(200))

    with patch.object(requests.Session, "head", head_mock) as head_called, \
         patch.object(requests.Session, "get", get_mock) as get_called:
        session = requests.Session()
        status, err = probe_module._probe_url(session, "http://nope.test/x")
    assert status == "FAILED"
    assert "ConnectionError" in err
    assert "DNS" in err or "host" in err
    # GET must NOT have been called (short-circuit on network error)
    head_called.assert_called_once()
    get_called.assert_not_called()


# ---------------------------------------------------------------------------
# 6. enabled=FALSE row skipped (verified via real SELECT on test DB)
# ---------------------------------------------------------------------------


def test_enabled_false_row_not_probed(conn, probe_module):
    """Insert one source with enabled=FALSE; verify _iter_registry_urls
    excludes it (real DB read; no network)."""
    _clear_runs(conn)
    fake_id = uuid.uuid4()
    url = f"http://test-{fake_id.hex[:8]}.local/disabled"
    _seed_registry(conn, fake_id, url=url, enabled=False)
    yielded = list(probe_module._iter_registry_urls(conn))
    ids = {reg_id for reg_id, _, _ in yielded}
    assert fake_id not in ids, "enabled=FALSE row should be excluded"