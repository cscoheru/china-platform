#!/usr/bin/env python3
"""Stage 1 / S1.8 — tests for backend/src/china_platform/monitoring/ingest_monitor.py.

Per Cursor 65 §NOW + docs/22-stage1-s18-ingest-run-monitoring-plan-20260825.md §7:
  * failure rate calculation — with mocked ingestion_run rows
  * stale boundary (`<`) — started_at < NOW() - interval '6h'
  * empty table honesty — 0 rows → failure_rate=0.0 (no false positives)
  * exit code mapping — check_alerts returns 0/1/2/3 per docs/22 §4.1
  * status distribution — with mocked rows
  * duration stats — with finished runs

**用 fixture/mock DB，不跑 OCR** (per Cursor 65 §NOW step 3).

Uses SAVEPOINT pattern: INSERT fake ingestion_run rows within a savepoint,
run monitor queries, ROLLBACK savepoint. No permanent state change.
"""
from __future__ import annotations

import sys
import uuid
from datetime import datetime, timedelta, timezone
from pathlib import Path

import psycopg2
import psycopg2.extras
import pytest

# Register UUID adapter so psycopg2 can handle uuid.UUID → PostgreSQL UUID
psycopg2.extras.register_uuid()

REPO_ROOT = Path(__file__).resolve().parent.parent

# Make the package importable
sys.path.insert(0, str(REPO_ROOT / "backend" / "src"))

from china_platform.monitoring.ingest_monitor import IngestMonitor  # noqa: E402

DSN = "postgresql://postgres:postgres@127.0.0.1:55440/cegr_test"


# ---------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------


@pytest.fixture(scope="module")
def imported_registry() -> None:
    """Re-run the CSV import once for the whole module (idempotent)."""
    sys.path.insert(0, str(REPO_ROOT / "scripts"))
    import import_registry_csv as irc  # noqa: E402

    csv_path = REPO_ROOT / "source_registry" / "registry.csv"
    rc = irc.import_registry(csv_path, DSN)
    assert rc == 0, f"import_registry_csv returned rc={rc}"


@pytest.fixture
def conn() -> psycopg2.extensions.connection:
    """Fresh connection; single transaction; ROLLBACK at teardown."""
    c = psycopg2.connect(DSN)
    c.autocommit = False
    yield c
    c.rollback()
    c.close()


@pytest.fixture
def monitor_with_conn(conn) -> IngestMonitor:
    """IngestMonitor that reuses the test's connection.

    This is the key: monitor queries and test inserts share one connection,
    so uncommitted rows are visible to the monitor, and ROLLBACK at teardown
    undoes everything atomically.
    """
    m = IngestMonitor(
        dsn=DSN, max_failure_rate=0.25, stale_running_hours=6, window_days=7
    )
    m._conn = conn  # inject test connection
    return m


@pytest.fixture
def registry_id(conn, imported_registry) -> uuid.UUID:
    """Resolve a source_registry id for fake ingestion_run rows."""
    with conn.cursor() as cur:
        cur.execute("SELECT id FROM cegr.source_registry LIMIT 1")
        row = cur.fetchone()
    if row is None:
        pytest.fail("source_registry is empty; import_registry_csv failed?")
    return row[0]


def _insert_fake_ingestion_run(
    conn: psycopg2.extensions.connection,
    source_registry_id: uuid.UUID,
    status: str,
    started_at: datetime,
    finished_at: datetime | None,
    records_extracted: int | None,
    records_inserted: int | None,
    error_log: str | None = None,
    triggered_by: str = "test_ingest_monitor",
) -> uuid.UUID:
    """INSERT one fake ingestion_run row; return its id.

    No commit — stays in the test's transaction so ROLLBACK undoes it.
    """
    run_id = uuid.uuid4()
    with conn.cursor() as cur:
        cur.execute(
            """
            INSERT INTO cegr.ingestion_run
                (id, source_registry_id, started_at, finished_at, status,
                 records_extracted, records_inserted, error_log, triggered_by)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            """,
            (
                run_id, source_registry_id, started_at, finished_at, status,
                records_extracted, records_inserted, error_log, triggered_by,
            ),
        )
    return run_id


# ---------------------------------------------------------------------
# Cursor 65 §NOW test 1 — empty table honesty (failure_rate = 0.0)
# ---------------------------------------------------------------------


def test_empty_table_honests_zero_failure_rate(monitor_with_conn, conn) -> None:
    """Empty ingestion_run table → failure_rate=0.0 (no false positives)."""
    # Clear any recent runs in the window
    with conn.cursor() as cur:
        cur.execute(
            "DELETE FROM cegr.ingestion_run "
            "WHERE started_at >= NOW() - INTERVAL '7 days'"
        )
    rate = monitor_with_conn.failure_rate(window_days=7)
    assert rate == 0.0, f"empty table should yield 0.0; got {rate}"


def test_empty_table_honests_no_stale(monitor_with_conn, conn) -> None:
    """Empty ingestion_run table → stale_running=[] (no false positives)."""
    with conn.cursor() as cur:
        cur.execute(
            "DELETE FROM cegr.ingestion_run "
            "WHERE started_at >= NOW() - INTERVAL '7 days'"
        )
    stale = monitor_with_conn.stale_running(hours=6)
    assert stale == [], f"empty table should yield []; got {stale}"


# ---------------------------------------------------------------------
# Cursor 65 §NOW test 2 — failure rate calculation (with mocked rows)
# ---------------------------------------------------------------------


def test_failure_rate_calculation(monitor_with_conn, conn, registry_id) -> None:
    """Failure rate = (PARTIAL + FAILED) / total.

    Inserts 4 fake rows: 2 SUCCESS, 1 PARTIAL, 1 FAILED → rate = 0.50.
    """
    now = datetime.now(timezone.utc)
    # Clear any recent runs first
    with conn.cursor() as cur:
        cur.execute(
            "DELETE FROM cegr.ingestion_run "
            "WHERE started_at >= NOW() - INTERVAL '7 days'"
        )

    # Insert 4 fake runs: 2 SUCCESS, 1 PARTIAL, 1 FAILED
    for status in ("SUCCESS", "SUCCESS", "PARTIAL", "FAILED"):
        _insert_fake_ingestion_run(
            conn, registry_id, status,
            started_at=now - timedelta(hours=2),
            finished_at=now - timedelta(hours=1),
            records_extracted=10,
            records_inserted=10 if status == "SUCCESS" else 5 if status == "PARTIAL" else 0,
            error_log="test error" if status in ("PARTIAL", "FAILED") else None,
        )

    rate = monitor_with_conn.failure_rate(window_days=7)
    assert rate == pytest.approx(0.50, abs=0.01), f"expected 0.50 (2/4); got {rate}"


def test_status_distribution_with_rows(monitor_with_conn, conn, registry_id) -> None:
    """status_distribution returns correct counts per status."""
    now = datetime.now(timezone.utc)
    with conn.cursor() as cur:
        cur.execute(
            "DELETE FROM cegr.ingestion_run "
            "WHERE started_at >= NOW() - INTERVAL '7 days'"
        )

    for status in ("SUCCESS", "SUCCESS", "SUCCESS", "FAILED"):
        _insert_fake_ingestion_run(
            conn, registry_id, status,
            started_at=now - timedelta(hours=3),
            finished_at=now - timedelta(hours=2),
            records_extracted=10,
            records_inserted=10 if status == "SUCCESS" else 0,
        )

    dist = monitor_with_conn.status_distribution(window_days=7)
    assert "SUCCESS" in dist
    assert dist["SUCCESS"]["run_count"] == 3
    assert "FAILED" in dist
    assert dist["FAILED"]["run_count"] == 1


# ---------------------------------------------------------------------
# Cursor 65 §NOW test 3 — stale boundary (`<`)
# Per Cursor 64 §1 备注 + Cursor 65 §SCHEMA 决策 4: use `<` not `>`
# ---------------------------------------------------------------------


def test_stale_running_boundary_lt_6h(monitor_with_conn, conn, registry_id) -> None:
    """Stale RUNNING: started_at < NOW() - interval '6 hours'.

    Inserts 3 rows:
      * RUNNING started 2h ago → NOT stale (< 6h threshold)
      * RUNNING started 10h ago → stale (> 6h threshold)
      * RUNNING started 7h ago, finished → NOT stale (finished_at set)
    """
    now = datetime.now(timezone.utc)
    with conn.cursor() as cur:
        cur.execute(
            "DELETE FROM cegr.ingestion_run "
            "WHERE started_at >= NOW() - INTERVAL '7 days'"
        )

    # Row 1: RUNNING, started 2h ago → NOT stale (< 6h)
    _insert_fake_ingestion_run(
        conn, registry_id, "RUNNING",
        started_at=now - timedelta(hours=2),
        finished_at=None,
        records_extracted=None, records_inserted=None,
    )

    # Row 2: RUNNING, started 10h ago → stale (> 6h)
    _insert_fake_ingestion_run(
        conn, registry_id, "RUNNING",
        started_at=now - timedelta(hours=10),
        finished_at=None,
        records_extracted=None, records_inserted=None,
    )

    # Row 3: RUNNING started 7h ago, finished 6h ago → NOT stale (has finished_at)
    _insert_fake_ingestion_run(
        conn, registry_id, "RUNNING",
        started_at=now - timedelta(hours=7),
        finished_at=now - timedelta(hours=6),
        records_extracted=10, records_inserted=10,
    )

    stale = monitor_with_conn.stale_running(hours=6)
    assert len(stale) == 1, f"expected 1 stale run; got {len(stale)}: {stale}"
    assert stale[0]["hours_running"] > 6.0
    assert stale[0]["hours_running"] < 12.0  # sanity


def test_stale_running_custom_hours(monitor_with_conn, conn, registry_id) -> None:
    """Stale detection with custom hours threshold."""
    now = datetime.now(timezone.utc)
    with conn.cursor() as cur:
        cur.execute(
            "DELETE FROM cegr.ingestion_run "
            "WHERE started_at >= NOW() - INTERVAL '7 days'"
        )

    # RUNNING started 4h ago — stale only if threshold < 4h
    _insert_fake_ingestion_run(
        conn, registry_id, "RUNNING",
        started_at=now - timedelta(hours=4),
        finished_at=None,
        records_extracted=None, records_inserted=None,
    )

    stale_6h = monitor_with_conn.stale_running(hours=6)  # NOT stale (4h < 6h)
    stale_3h = monitor_with_conn.stale_running(hours=3)  # STALE (4h > 3h)
    assert len(stale_6h) == 0, "4h run should NOT be stale with 6h threshold"
    assert len(stale_3h) == 1, "4h run SHOULD be stale with 3h threshold"


# ---------------------------------------------------------------------
# Cursor 65 §NOW test 4 — exit code mapping (0/1/2/3)
# ---------------------------------------------------------------------


def test_check_alerts_exit_code_0_ok(monitor_with_conn, conn, registry_id) -> None:
    """Exit code 0 = OK (no alerts)."""
    now = datetime.now(timezone.utc)
    with conn.cursor() as cur:
        cur.execute(
            "DELETE FROM cegr.ingestion_run "
            "WHERE started_at >= NOW() - INTERVAL '7 days'"
        )

    for _ in range(4):
        _insert_fake_ingestion_run(
            conn, registry_id, "SUCCESS",
            started_at=now - timedelta(hours=2),
            finished_at=now - timedelta(hours=1),
            records_extracted=10, records_inserted=10,
        )

    ok, msg, exit_code = monitor_with_conn.check_alerts()
    assert ok is True
    assert exit_code == 0
    assert "OK" in msg


def test_check_alerts_exit_code_1_failure_rate(monitor_with_conn, conn, registry_id) -> None:
    """Exit code 1 = failure rate exceeded threshold."""
    now = datetime.now(timezone.utc)
    with conn.cursor() as cur:
        cur.execute(
            "DELETE FROM cegr.ingestion_run "
            "WHERE started_at >= NOW() - INTERVAL '7 days'"
        )

    _insert_fake_ingestion_run(
        conn, registry_id, "SUCCESS",
        started_at=now - timedelta(hours=2),
        finished_at=now - timedelta(hours=1),
        records_extracted=10, records_inserted=10,
    )
    for _ in range(3):
        _insert_fake_ingestion_run(
            conn, registry_id, "FAILED",
            started_at=now - timedelta(hours=2),
            finished_at=now - timedelta(hours=1),
            records_extracted=10, records_inserted=0,
            error_log="test failure",
        )

    ok, msg, exit_code = monitor_with_conn.check_alerts()
    assert ok is False
    assert exit_code == 1
    assert "failure_rate" in msg


def test_check_alerts_exit_code_2_stale(monitor_with_conn, conn, registry_id) -> None:
    """Exit code 2 = stale RUNNING detected."""
    now = datetime.now(timezone.utc)
    with conn.cursor() as cur:
        cur.execute(
            "DELETE FROM cegr.ingestion_run "
            "WHERE started_at >= NOW() - INTERVAL '7 days'"
        )

    for _ in range(2):
        _insert_fake_ingestion_run(
            conn, registry_id, "SUCCESS",
            started_at=now - timedelta(hours=2),
            finished_at=now - timedelta(hours=1),
            records_extracted=10, records_inserted=10,
        )
    _insert_fake_ingestion_run(
        conn, registry_id, "RUNNING",
        started_at=now - timedelta(hours=10),
        finished_at=None,
        records_extracted=None, records_inserted=None,
    )

    ok, msg, exit_code = monitor_with_conn.check_alerts()
    assert ok is False
    assert exit_code == 2
    assert "stale RUNNING" in msg


def test_check_alerts_exit_code_3_both(monitor_with_conn, conn, registry_id) -> None:
    """Exit code 3 = both failure rate + stale RUNNING."""
    now = datetime.now(timezone.utc)
    with conn.cursor() as cur:
        cur.execute(
            "DELETE FROM cegr.ingestion_run "
            "WHERE started_at >= NOW() - INTERVAL '7 days'"
        )

    _insert_fake_ingestion_run(
        conn, registry_id, "SUCCESS",
        started_at=now - timedelta(hours=2),
        finished_at=now - timedelta(hours=1),
        records_extracted=10, records_inserted=10,
    )
    for _ in range(3):
        _insert_fake_ingestion_run(
            conn, registry_id, "FAILED",
            started_at=now - timedelta(hours=2),
            finished_at=now - timedelta(hours=1),
            records_extracted=10, records_inserted=0,
            error_log="test failure",
        )
    _insert_fake_ingestion_run(
        conn, registry_id, "RUNNING",
        started_at=now - timedelta(hours=10),
        finished_at=None,
        records_extracted=None, records_inserted=None,
    )

    ok, msg, exit_code = monitor_with_conn.check_alerts()
    assert ok is False
    assert exit_code == 3
    assert "failure_rate" in msg
    assert "stale RUNNING" in msg


# ---------------------------------------------------------------------
# Duration stats (with finished runs)
# ---------------------------------------------------------------------


def test_duration_stats_with_finished_runs(monitor_with_conn, conn, registry_id) -> None:
    """Duration stats avg/min/max/median for finished runs."""
    now = datetime.now(timezone.utc)
    with conn.cursor() as cur:
        cur.execute(
            "DELETE FROM cegr.ingestion_run "
            "WHERE started_at >= NOW() - INTERVAL '7 days'"
        )

    for secs in (10, 20, 30, 40, 50):
        _insert_fake_ingestion_run(
            conn, registry_id, "SUCCESS",
            started_at=now - timedelta(hours=2, seconds=secs),
            finished_at=now - timedelta(hours=2),
            records_extracted=10, records_inserted=10,
        )

    stats = monitor_with_conn.duration_stats(window_days=7)
    assert stats["run_count"] == 5
    assert stats["avg_seconds"] == pytest.approx(30.0, abs=1.0)
    assert stats["min_seconds"] == pytest.approx(10.0, abs=1.0)
    assert stats["max_seconds"] == pytest.approx(50.0, abs=1.0)
    assert stats["median_seconds"] == pytest.approx(30.0, abs=1.0)


# ---------------------------------------------------------------------
# Generate report (smoke test)
# ---------------------------------------------------------------------


def test_generate_report_returns_dict(monitor_with_conn, conn) -> None:
    """generate_report returns a dict with expected keys."""
    with conn.cursor() as cur:
        cur.execute(
            "DELETE FROM cegr.ingestion_run "
            "WHERE started_at >= NOW() - INTERVAL '7 days'"
        )

    report = monitor_with_conn.generate_report(window_days=7)
    assert isinstance(report, dict)
    assert "generated_at_utc" in report
    assert "window_days" in report
    assert "status_distribution" in report
    assert "failure_rate" in report
    assert "stale_running_count" in report
    assert "per_source_breakdown" in report
    assert "duration_stats" in report