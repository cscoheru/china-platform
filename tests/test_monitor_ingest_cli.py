"""Stage 1 / S1.17 — monitor_ingest CLI pytest wrapper.

Per docs/32-stage1-s17-r12-url-health-plan-20260825.md §3.2 + tasking 127 §NOW-1.

Wraps `scripts/monitor_ingest.py` via subprocess; verifies exit codes map
to docs/22 §4.1 (S1.8) exit semantics. The underlying IngestMonitor SQL
semantics are already protected by `tests/test_ingest_monitor.py` — this
file covers only the CLI shim.

Fixture: SAVEPOINT pattern from test_ingest_monitor (test-level ROLLBACK).
"""
from __future__ import annotations

import json
import subprocess
import sys
import uuid
from datetime import datetime, timedelta, timezone
from pathlib import Path

import psycopg2
import psycopg2.extras
import pytest

psycopg2.extras.register_uuid()

REPO_ROOT = Path(__file__).resolve().parent.parent
SCRIPT = REPO_ROOT / "scripts" / "monitor_ingest.py"
DSN = "postgresql://postgres:postgres@127.0.0.1:55440/cegr_test"
PYTHON = sys.executable


@pytest.fixture(scope="module")
def imported_registry() -> None:
    """Import source_registry/registry.csv once for the module."""
    sys.path.insert(0, str(REPO_ROOT / "scripts"))
    import import_registry_csv as irc  # noqa: E402

    csv_path = REPO_ROOT / "source_registry" / "registry.csv"
    rc = irc.import_registry(csv_path, DSN)
    assert rc == 0, f"import_registry_csv returned rc={rc}"


@pytest.fixture
def conn():
    """Autocommit connection so subprocess's `monitor_ingest` can see
    the INSERTed rows. Cleanup via explicit DELETE in teardown."""
    c = psycopg2.connect(DSN)
    c.autocommit = True
    yield c
    with c.cursor() as cur:
        cur.execute(
            "DELETE FROM cegr.ingestion_run WHERE triggered_by = 'test_monitor_cli'"
        )
    c.close()


@pytest.fixture
def registry_id(conn, imported_registry) -> uuid.UUID:
    with conn.cursor() as cur:
        cur.execute("SELECT id FROM cegr.source_registry LIMIT 1")
        row = cur.fetchone()
    if row is None:
        pytest.fail("source_registry empty")
    return row[0]


def _insert_run(conn, reg_id, status, hours_ago=2):
    run_id = uuid.uuid4()
    now = datetime.now(timezone.utc)
    finished = now - timedelta(hours=hours_ago - 1) if status != "RUNNING" else None
    with conn.cursor() as cur:
        cur.execute(
            """
            INSERT INTO cegr.ingestion_run
                (id, source_registry_id, started_at, finished_at, status,
                 records_extracted, records_inserted, error_log, triggered_by)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, 'test_monitor_cli')
            """,
            (
                run_id, reg_id,
                now - timedelta(hours=hours_ago),
                finished, status,
                10, 10 if status == "SUCCESS" else 0,
                None if status == "SUCCESS" else "test",
            ),
        )
    return run_id


def _clear_window(conn):
    with conn.cursor() as cur:
        cur.execute(
            "DELETE FROM cegr.ingestion_run WHERE started_at >= NOW() - INTERVAL '7 days'"
        )


def _run_cli(*args: str) -> subprocess.CompletedProcess:
    return subprocess.run(
        [PYTHON, str(SCRIPT), *args],
        capture_output=True, text=True, timeout=60,
    )


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------

def test_cli_help():
    """--help exit 0; CLI is callable."""
    r = _run_cli("--help")
    assert r.returncode == 0
    assert "monitor_ingest" in r.stdout.lower() or "ingest" in r.stdout.lower()


def test_check_empty_table_returns_zero(conn):
    """Empty ingestion_run table → check exit 0 (空表诚实; per S1.8 docs/22 §4.1)."""
    _clear_window(conn)
    r = _run_cli("check")
    assert r.returncode == 0, (
        f"expected exit 0 on empty table; got {r.returncode}; "
        f"stdout={r.stdout[:200]}; stderr={r.stderr[:200]}"
    )


def test_check_failure_rate_exceeded_returns_one(conn, registry_id):
    """1 SUCCESS + 3 FAILED → failure rate 0.75 > 0.25 → exit 1."""
    _clear_window(conn)
    _insert_run(conn, registry_id, "SUCCESS", hours_ago=2)
    for _ in range(3):
        _insert_run(conn, registry_id, "FAILED", hours_ago=2)
    r = _run_cli("check")
    assert r.returncode == 1, (
        f"expected exit 1 for failure_rate; got {r.returncode}; "
        f"stderr={r.stderr[:200]}"
    )
    assert "failure_rate" in (r.stdout + r.stderr)


def test_check_stale_running_returns_two(conn, registry_id):
    """1 RUNNING >6h + ≥1 SUCCESS → exit 2."""
    _clear_window(conn)
    _insert_run(conn, registry_id, "SUCCESS", hours_ago=2)
    _insert_run(conn, registry_id, "RUNNING", hours_ago=10)
    r = _run_cli("check", "--hours", "6")
    assert r.returncode == 2, (
        f"expected exit 2 for stale; got {r.returncode}; "
        f"stderr={r.stderr[:200]}"
    )
    assert "stale" in (r.stdout + r.stderr).lower()


def test_check_both_alerts_returns_three(conn, registry_id):
    """1 SUCCESS + 3 FAILED + 1 RUNNING >6h → exit 3."""
    _clear_window(conn)
    _insert_run(conn, registry_id, "SUCCESS", hours_ago=2)
    for _ in range(3):
        _insert_run(conn, registry_id, "FAILED", hours_ago=2)
    _insert_run(conn, registry_id, "RUNNING", hours_ago=10)
    r = _run_cli("check", "--hours", "6")
    assert r.returncode == 3


def test_report_outputs_json_with_failure_rate(conn):
    """`report` outputs valid JSON containing failure_rate field."""
    _clear_window(conn)
    r = _run_cli("report")
    assert r.returncode == 0
    payload = json.loads(r.stdout)
    assert "failure_rate" in payload
    assert "status_distribution" in payload
    assert payload["failure_rate"] == 0.0  # empty table