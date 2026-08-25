"""Stage 1 / S1.8 — ingest_run 监控器.

Per docs/22-stage1-s18-ingest-run-monitoring-plan-20260825.md + Cursor 65 §SCHEMA/语义裁定.

Reads `cegr.ingestion_run` table (populated by S1.4-1.7 connectors); reports:
  * status distribution (SUCCESS / PARTIAL / FAILED / RUNNING)
  * failure rate (PARTIAL + FAILED / total runs)
  * failed runs list (with error_log preview)
  * stale RUNNING (started_at < NOW() - INTERVAL '6 hours' AND finished_at IS NULL)
  * per-source breakdown (by source_registry domain + category)
  * records gap analysis (extracted vs inserted)
  * duration stats (avg/min/max/median/p95)
  * trend (daily success rate over N days)
  * generate_report (combined dict)
  * check_alerts (boolean + message for cron exit codes)

**只读**：不写 ingestion_run / source_document / observation（per Cursor 65 §SCHEMA 决策 5）。
**不新建表 / 不引入 DSH**（per Cursor 65 §SCHEMA 决策 1 + docs/22 §6）。

DSN from env var `CEGR_DSN` (preferred) or `DATABASE_URL` (fallback).
Cursor 65 §SCHEMA 决策 2: 禁止把生产密码写进仓库。
"""
from __future__ import annotations

import json
import os
from dataclasses import dataclass
from datetime import datetime

import psycopg2


@dataclass
class IngestMonitorConfig:
    """IngestMonitor configuration. All fields overridable via constructor."""

    dsn: str | None = None
    max_failure_rate: float = 0.25  # 25% threshold
    stale_running_hours: int = 6
    window_days: int = 7

    def __post_init__(self) -> None:
        if self.dsn is None:
            # Cursor 65 §SCHEMA 决策 2: env var; 禁止把生产密码写进仓库
            self.dsn = (
                os.environ.get("CEGR_DSN")
                or os.environ.get("DATABASE_URL")
                or "postgresql://postgres:postgres@127.0.0.1:55440/cegr_test"
            )


class IngestMonitor:
    """Stage 1 / S1.8 — ingest_run 监控器（只读）.

    Example:
        monitor = IngestMonitor()
        report = monitor.generate_report(window_days=7)
        print(json.dumps(report, indent=2, default=str))

        ok, message = monitor.check_alerts()
        if not ok:
            sys.exit(1)  # cron-friendly exit code
    """

    def __init__(
        self,
        dsn: str | None = None,
        max_failure_rate: float = 0.25,
        stale_running_hours: int = 6,
        window_days: int = 7,
    ) -> None:
        self.config = IngestMonitorConfig(
            dsn=dsn,
            max_failure_rate=max_failure_rate,
            stale_running_hours=stale_running_hours,
            window_days=window_days,
        )
        self._conn: psycopg2.extensions.connection | None = None

    def _get_conn(self) -> psycopg2.extensions.connection:
        """Lazy psycopg2 connection; reuse across calls."""
        if self._conn is None or self._conn.closed:
            self._conn = psycopg2.connect(self.config.dsn)
        return self._conn

    def close(self) -> None:
        """Close the underlying psycopg2 connection if open."""
        if self._conn is not None and not self._conn.closed:
            self._conn.close()
            self._conn = None

    def __enter__(self) -> "IngestMonitor":
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        self.close()

    # ------------------------------------------------------------------
    # Core queries (per docs/22 §3)
    # ------------------------------------------------------------------

    def status_distribution(self, window_days: int | None = None) -> dict:
        """Status distribution within window_days.

        Returns dict {status: {run_count, total_extracted, total_inserted}}.
        """
        window = window_days if window_days is not None else self.config.window_days
        sql = """
            SELECT status, COUNT(*) AS run_count,
                   SUM(records_extracted) AS total_extracted,
                   SUM(records_inserted) AS total_inserted
            FROM cegr.ingestion_run
            WHERE started_at >= NOW() - INTERVAL '%s days'
            GROUP BY status
            ORDER BY run_count DESC
        """
        conn = self._get_conn()
        with conn.cursor() as cur:
            cur.execute(sql, (window,))
            rows = cur.fetchall()
        return {
            row[0]: {
                "run_count": row[1],
                "total_extracted": row[2] or 0,
                "total_inserted": row[3] or 0,
            }
            for row in rows
        }

    def failure_rate(self, window_days: int | None = None) -> float:
        """Failure rate within window_days.

        Returns float [0.0, 1.0]. Empty table → 0.0 (honest report; no false positives).
        Per docs/22 §2.4: (count(PARTIAL) + count(FAILED)) / count(ALL).
        """
        window = window_days if window_days is not None else self.config.window_days
        sql = """
            SELECT
                (COUNT(*) FILTER (WHERE status IN ('PARTIAL', 'FAILED')))::float /
                NULLIF(COUNT(*), 0) AS failure_rate
            FROM cegr.ingestion_run
            WHERE started_at >= NOW() - INTERVAL '%s days'
        """
        conn = self._get_conn()
        with conn.cursor() as cur:
            cur.execute(sql, (window,))
            row = cur.fetchone()
        rate = row[0] if row and row[0] is not None else 0.0
        return float(rate)

    def failed_runs(self, limit: int = 100, window_days: int | None = None) -> list[dict]:
        """List failed/partial runs with error_log preview (LEFT 200 chars)."""
        window = window_days if window_days is not None else self.config.window_days
        sql = """
            SELECT ir.id, r.domain, r.category, ir.started_at, ir.finished_at,
                   ir.records_extracted, ir.records_inserted,
                   LEFT(ir.error_log, 200) AS error_preview
            FROM cegr.ingestion_run ir
            JOIN cegr.source_registry r ON ir.source_registry_id = r.id
            WHERE ir.status IN ('FAILED', 'PARTIAL')
              AND ir.started_at >= NOW() - INTERVAL '%s days'
            ORDER BY ir.started_at DESC
            LIMIT %s
        """
        conn = self._get_conn()
        with conn.cursor() as cur:
            cur.execute(sql, (window, limit))
            rows = cur.fetchall()
        return [
            {
                "id": str(row[0]),
                "domain": row[1],
                "category": row[2],
                "started_at": row[3],
                "finished_at": row[4],
                "records_extracted": row[5],
                "records_inserted": row[6],
                "error_preview": row[7],
            }
            for row in rows
        ]

    def partial_runs(self, limit: int = 100, window_days: int | None = None) -> list[dict]:
        """List partial runs only (subset of failed_runs)."""
        window = window_days if window_days is not None else self.config.window_days
        sql = """
            SELECT ir.id, r.domain, r.category, ir.started_at, ir.finished_at,
                   ir.records_extracted, ir.records_inserted,
                   LEFT(ir.error_log, 200) AS error_preview
            FROM cegr.ingestion_run ir
            JOIN cegr.source_registry r ON ir.source_registry_id = r.id
            WHERE ir.status = 'PARTIAL'
              AND ir.started_at >= NOW() - INTERVAL '%s days'
            ORDER BY ir.started_at DESC
            LIMIT %s
        """
        conn = self._get_conn()
        with conn.cursor() as cur:
            cur.execute(sql, (window, limit))
            rows = cur.fetchall()
        return [
            {
                "id": str(row[0]),
                "domain": row[1],
                "category": row[2],
                "started_at": row[3],
                "finished_at": row[4],
                "records_extracted": row[5],
                "records_inserted": row[6],
                "error_preview": row[7],
            }
            for row in rows
        ]

    def stale_running(self, hours: int | None = None) -> list[dict]:
        """Stale RUNNING detection: started_at < NOW() - interval 'N hours'.

        Per Cursor 65 §SCHEMA 决策 4: use `<` (not `>`); per docs/22 §3.4 SQL.
        Default N=6 hours (configurable via --hours CLI).
        """
        h = hours if hours is not None else self.config.stale_running_hours
        sql = """
            SELECT ir.id, r.domain, r.category, ir.started_at,
                   EXTRACT(EPOCH FROM (NOW() - ir.started_at))/3600 AS hours_running,
                   ir.records_extracted, ir.triggered_by
            FROM cegr.ingestion_run ir
            JOIN cegr.source_registry r ON ir.source_registry_id = r.id
            WHERE ir.status = 'RUNNING'
              AND ir.finished_at IS NULL
              AND ir.started_at < NOW() - INTERVAL '%s hours'
            ORDER BY ir.started_at ASC
        """
        conn = self._get_conn()
        with conn.cursor() as cur:
            cur.execute(sql, (h,))
            rows = cur.fetchall()
        return [
            {
                "id": str(row[0]),
                "domain": row[1],
                "category": row[2],
                "started_at": row[3],
                "hours_running": float(row[4]) if row[4] is not None else None,
                "records_extracted": row[5],
                "triggered_by": row[6],
            }
            for row in rows
        ]

    def per_source_breakdown(self, window_days: int | None = None) -> list[dict]:
        """Per-source breakdown (domain + category)."""
        window = window_days if window_days is not None else self.config.window_days
        sql = """
            SELECT r.domain, r.category,
                   COUNT(*) AS total_runs,
                   COUNT(*) FILTER (WHERE ir.status = 'SUCCESS') AS success_count,
                   COUNT(*) FILTER (WHERE ir.status = 'PARTIAL') AS partial_count,
                   COUNT(*) FILTER (WHERE ir.status = 'FAILED') AS failed_count,
                   (COUNT(*) FILTER (WHERE ir.status IN ('PARTIAL','FAILED'))::float /
                    NULLIF(COUNT(*), 0)) AS per_source_failure_rate,
                   SUM(ir.records_extracted) AS total_extracted,
                   SUM(ir.records_inserted) AS total_inserted
            FROM cegr.ingestion_run ir
            JOIN cegr.source_registry r ON ir.source_registry_id = r.id
            WHERE ir.started_at >= NOW() - INTERVAL '%s days'
            GROUP BY r.domain, r.category
            ORDER BY total_runs DESC
        """
        conn = self._get_conn()
        with conn.cursor() as cur:
            cur.execute(sql, (window,))
            rows = cur.fetchall()
        return [
            {
                "domain": row[0],
                "category": row[1],
                "total_runs": row[2],
                "success_count": row[3],
                "partial_count": row[4],
                "failed_count": row[5],
                "per_source_failure_rate": float(row[6]) if row[6] is not None else 0.0,
                "total_extracted": row[7] or 0,
                "total_inserted": row[8] or 0,
            }
            for row in rows
        ]

    def records_gap_analysis(
        self, limit: int = 20, window_days: int | None = None
    ) -> list[dict]:
        """Records gap (extracted - inserted); top `limit` by gap desc."""
        window = window_days if window_days is not None else self.config.window_days
        sql = """
            SELECT ir.id, r.domain, r.category,
                   ir.records_extracted, ir.records_inserted,
                   (ir.records_extracted - COALESCE(ir.records_inserted, 0)) AS gap,
                   CASE WHEN ir.records_extracted > 0
                        THEN ROUND((ir.records_inserted::numeric / ir.records_extracted) * 100, 1)
                        ELSE NULL END AS insertion_pct
            FROM cegr.ingestion_run ir
            JOIN cegr.source_registry r ON ir.source_registry_id = r.id
            WHERE ir.records_extracted > 0
              AND (ir.records_inserted IS NULL OR ir.records_inserted < ir.records_extracted)
              AND ir.started_at >= NOW() - INTERVAL '%s days'
            ORDER BY gap DESC
            LIMIT %s
        """
        conn = self._get_conn()
        with conn.cursor() as cur:
            cur.execute(sql, (window, limit))
            rows = cur.fetchall()
        return [
            {
                "id": str(row[0]),
                "domain": row[1],
                "category": row[2],
                "records_extracted": row[3],
                "records_inserted": row[4],
                "gap": row[5],
                "insertion_pct": float(row[6]) if row[6] is not None else None,
            }
            for row in rows
        ]

    def duration_stats(self, window_days: int | None = None) -> dict:
        """Duration stats (avg/min/max/median/p95) for finished runs."""
        window = window_days if window_days is not None else self.config.window_days
        sql = """
            SELECT
                COUNT(*) AS run_count,
                AVG(EXTRACT(EPOCH FROM (finished_at - started_at))) AS avg_seconds,
                MIN(EXTRACT(EPOCH FROM (finished_at - started_at))) AS min_seconds,
                MAX(EXTRACT(EPOCH FROM (finished_at - started_at))) AS max_seconds,
                PERCENTILE_CONT(0.5) WITHIN GROUP (
                    ORDER BY EXTRACT(EPOCH FROM (finished_at - started_at))
                ) AS median_seconds,
                PERCENTILE_CONT(0.95) WITHIN GROUP (
                    ORDER BY EXTRACT(EPOCH FROM (finished_at - started_at))
                ) AS p95_seconds
            FROM cegr.ingestion_run
            WHERE finished_at IS NOT NULL
              AND started_at >= NOW() - INTERVAL '%s days'
        """
        conn = self._get_conn()
        with conn.cursor() as cur:
            cur.execute(sql, (window,))
            row = cur.fetchone()
        if not row or row[0] == 0:
            return {
                "run_count": 0,
                "avg_seconds": None,
                "min_seconds": None,
                "max_seconds": None,
                "median_seconds": None,
                "p95_seconds": None,
            }
        return {
            "run_count": row[0],
            "avg_seconds": float(row[1]) if row[1] is not None else None,
            "min_seconds": float(row[2]) if row[2] is not None else None,
            "max_seconds": float(row[3]) if row[3] is not None else None,
            "median_seconds": float(row[4]) if row[4] is not None else None,
            "p95_seconds": float(row[5]) if row[5] is not None else None,
        }

    def trend(self, days: int = 30) -> list[dict]:
        """Daily trend (success/failure counts + failure rate) over `days`."""
        sql = """
            SELECT DATE(started_at) AS run_date,
                   COUNT(*) AS daily_runs,
                   COUNT(*) FILTER (WHERE status = 'SUCCESS') AS success,
                   COUNT(*) FILTER (WHERE status IN ('PARTIAL','FAILED')) AS failed,
                   (COUNT(*) FILTER (WHERE status IN ('PARTIAL','FAILED'))::float /
                    NULLIF(COUNT(*), 0)) AS daily_failure_rate
            FROM cegr.ingestion_run
            WHERE started_at >= NOW() - INTERVAL '%s days'
            GROUP BY DATE(started_at)
            ORDER BY run_date ASC
        """
        conn = self._get_conn()
        with conn.cursor() as cur:
            cur.execute(sql, (days,))
            rows = cur.fetchall()
        return [
            {
                "run_date": row[0].isoformat() if row[0] else None,
                "daily_runs": row[1],
                "success": row[2],
                "failed": row[3],
                "daily_failure_rate": float(row[4]) if row[4] is not None else 0.0,
            }
            for row in rows
        ]

    # ------------------------------------------------------------------
    # Aggregate + alert methods
    # ------------------------------------------------------------------

    def generate_report(self, window_days: int | None = None) -> dict:
        """Combined report dict (all core queries).

        Suitable for JSON serialization (with default=str for datetime).
        """
        window = window_days if window_days is not None else self.config.window_days
        return {
            "generated_at_utc": datetime.utcnow().isoformat() + "Z",
            "window_days": window,
            "max_failure_rate_threshold": self.config.max_failure_rate,
            "stale_running_hours_threshold": self.config.stale_running_hours,
            "status_distribution": self.status_distribution(window),
            "failure_rate": self.failure_rate(window),
            "failed_runs_count": len(self.failed_runs(limit=1000, window_days=window)),
            "stale_running_count": len(self.stale_running()),
            "per_source_breakdown": self.per_source_breakdown(window),
            "records_gap_top20": self.records_gap_analysis(limit=20, window_days=window),
            "duration_stats": self.duration_stats(window),
        }

    def check_alerts(
        self,
        window_days: int | None = None,
        max_failure_rate: float | None = None,
        hours: int | None = None,
    ) -> tuple[bool, str, int]:
        """Check alert conditions. Returns (ok, message, exit_code).

        Exit codes (per docs/22 §4.1):
          * 0 = OK (no alerts)
          * 1 = failure rate exceeded threshold
          * 2 = stale RUNNING detected
          * 3 = both

        Per Cursor 65 §NOW step 2: check exit codes 0/1/2/3.
        """
        window = window_days if window_days is not None else self.config.window_days
        threshold = max_failure_rate if max_failure_rate is not None else self.config.max_failure_rate
        stale_h = hours if hours is not None else self.config.stale_running_hours

        rate = self.failure_rate(window)
        stale = self.stale_running(stale_h)

        failure_alert = rate > threshold
        stale_alert = len(stale) > 0

        if failure_alert and stale_alert:
            exit_code = 3
            ok = False
            msg = (
                f"ALERT: failure_rate={rate:.3f} > threshold={threshold:.3f} AND "
                f"{len(stale)} stale RUNNING (>{stale_h}h)"
            )
        elif failure_alert:
            exit_code = 1
            ok = False
            msg = f"ALERT: failure_rate={rate:.3f} > threshold={threshold:.3f}"
        elif stale_alert:
            exit_code = 2
            ok = False
            msg = f"ALERT: {len(stale)} stale RUNNING (>{stale_h}h)"
        else:
            exit_code = 0
            ok = True
            msg = f"OK: failure_rate={rate:.3f} (threshold={threshold:.3f}); no stale RUNNING"

        return ok, msg, exit_code