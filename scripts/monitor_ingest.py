#!/usr/bin/env python3
"""Stage 1 / S1.8 — ingest_run 监控 CLI.

Per docs/22-stage1-s18-ingest-run-monitoring-plan-20260825.md §2.2 + Cursor 65 §NOW step 2.

Usage:
    python3 scripts/monitor_ingest.py report              # stdout JSON report
    python3 scripts/monitor_ingest.py check               # exit code 0/1/2/3
    python3 scripts/monitor_ingest.py failed              # table of failed runs
    python3 scripts/monitor_ingest.py partial             # table of partial runs
    python3 scripts/monitor_ingest.py stale               # table of stale RUNNING
    python3 scripts/monitor_ingest.py per-source          # per-source breakdown
    python3 scripts/monitor_ingest.py trend               # 30-day trend

CLI flags:
    --window-days N          Override default 7-day window
    --max-failure-rate F     Override default 0.25 threshold
    --hours N                Override default 6h stale threshold
    --days N                 Override default 30-day trend window
    --dsn URL                Override DSN (default: env CEGR_DSN or DATABASE_URL)
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT / "backend" / "src"))

from china_platform.monitoring.ingest_monitor import IngestMonitor  # noqa: E402


def _json_default(obj):
    """JSON serializer for datetime / date."""
    if hasattr(obj, "isoformat"):
        return obj.isoformat()
    raise TypeError(f"Object of type {type(obj)} is not JSON serializable")


def cmd_report(monitor: IngestMonitor, args: argparse.Namespace) -> int:
    """Generate combined report to stdout."""
    report = monitor.generate_report(window_days=args.window_days)
    print(json.dumps(report, indent=2, default=_json_default, ensure_ascii=False))
    return 0


def cmd_check(monitor: IngestMonitor, args: argparse.Namespace) -> int:
    """Check alert conditions; exit code 0/1/2/3."""
    ok, msg, exit_code = monitor.check_alerts(
        window_days=args.window_days,
        max_failure_rate=args.max_failure_rate,
        hours=args.hours,
    )
    print(msg, file=sys.stderr if not ok else sys.stdout)
    return exit_code


def cmd_failed(monitor: IngestMonitor, args: argparse.Namespace) -> int:
    """List failed/partial runs (table format)."""
    runs = monitor.failed_runs(limit=100, window_days=args.window_days)
    if not runs:
        print("No failed/partial runs in window.")
        return 0
    print(f"{'domain':<30} {'category':<25} {'extracted':>10} {'inserted':>10} {'error_preview'}")
    print("-" * 120)
    for r in runs:
        print(
            f"{r['domain']:<30} {r['category']:<25} "
            f"{r['records_extracted'] or 0:>10} {r['records_inserted'] or 0:>10} "
            f"{(r['error_preview'] or '')[:60]}"
        )
    return 0


def cmd_partial(monitor: IngestMonitor, args: argparse.Namespace) -> int:
    """List partial runs only (table format)."""
    runs = monitor.partial_runs(limit=100, window_days=args.window_days)
    if not runs:
        print("No partial runs in window.")
        return 0
    print(f"{'domain':<30} {'category':<25} {'extracted':>10} {'inserted':>10} {'error_preview'}")
    print("-" * 120)
    for r in runs:
        print(
            f"{r['domain']:<30} {r['category']:<25} "
            f"{r['records_extracted'] or 0:>10} {r['records_inserted'] or 0:>10} "
            f"{(r['error_preview'] or '')[:60]}"
        )
    return 0


def cmd_stale(monitor: IngestMonitor, args: argparse.Namespace) -> int:
    """List stale RUNNING (table format)."""
    runs = monitor.stale_running(hours=args.hours)
    if not runs:
        print(f"No stale RUNNING (>{args.hours}h).")
        return 0
    print(f"{'domain':<30} {'category':<25} {'started_at':<22} {'hours':>8} {'triggered_by'}")
    print("-" * 120)
    for r in runs:
        started = r["started_at"].isoformat() if r["started_at"] else "?"
        hours_r = f"{r['hours_running']:.1f}" if r["hours_running"] is not None else "?"
        print(
            f"{r['domain']:<30} {r['category']:<25} {started:<22} {hours_r:>8} "
            f"{(r['triggered_by'] or '')[:40]}"
        )
    return 0


def cmd_per_source(monitor: IngestMonitor, args: argparse.Namespace) -> int:
    """Per-source breakdown (table format)."""
    rows = monitor.per_source_breakdown(window_days=args.window_days)
    if not rows:
        print("No ingestion_run data in window.")
        return 0
    print(
        f"{'domain':<30} {'category':<25} {'total':>7} {'ok':>5} {'partial':>8} "
        f"{'failed':>7} {'fail%':>8} {'extracted':>10} {'inserted':>10}"
    )
    print("-" * 130)
    for r in rows:
        print(
            f"{r['domain']:<30} {r['category']:<25} {r['total_runs']:>7} "
            f"{r['success_count']:>5} {r['partial_count']:>8} {r['failed_count']:>7} "
            f"{r['per_source_failure_rate']*100:>7.1f}% "
            f"{r['total_extracted']:>10} {r['total_inserted']:>10}"
        )
    return 0


def cmd_trend(monitor: IngestMonitor, args: argparse.Namespace) -> int:
    """30-day trend (table format)."""
    rows = monitor.trend(days=args.days)
    if not rows:
        print(f"No ingestion_run data in last {args.days} days.")
        return 0
    print(f"{'date':<12} {'runs':>7} {'ok':>5} {'fail':>6} {'fail%':>8}")
    print("-" * 50)
    for r in rows:
        print(
            f"{r['run_date']:<12} {r['daily_runs']:>7} {r['success']:>5} "
            f"{r['failed']:>6} {r['daily_failure_rate']*100:>7.1f}%"
        )
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Stage 1 / S1.8 — ingest_run 监控 CLI",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    # Shared flags
    def add_common_flags(p: argparse.ArgumentParser) -> None:
        p.add_argument("--window-days", type=int, default=7, help="Lookback window (days)")
        p.add_argument(
            "--max-failure-rate", type=float, default=0.25,
            help="Max acceptable failure rate (0.0-1.0)",
        )
        p.add_argument("--hours", type=int, default=6, help="Stale RUNNING threshold (hours)")
        p.add_argument("--dsn", type=str, default=None, help="PostgreSQL DSN override")

    # Subcommands
    p_report = subparsers.add_parser("report", help="Generate combined JSON report")
    add_common_flags(p_report)
    p_report.set_defaults(func=cmd_report)

    p_check = subparsers.add_parser("check", help="Check alert conditions (exit code)")
    add_common_flags(p_check)
    p_check.set_defaults(func=cmd_check)

    p_failed = subparsers.add_parser("failed", help="List failed/partial runs")
    add_common_flags(p_failed)
    p_failed.set_defaults(func=cmd_failed)

    p_partial = subparsers.add_parser("partial", help="List partial runs")
    add_common_flags(p_partial)
    p_partial.set_defaults(func=cmd_partial)

    p_stale = subparsers.add_parser("stale", help="List stale RUNNING")
    add_common_flags(p_stale)
    p_stale.set_defaults(func=cmd_stale)

    p_per_source = subparsers.add_parser("per-source", help="Per-source breakdown")
    add_common_flags(p_per_source)
    p_per_source.set_defaults(func=cmd_per_source)

    p_trend = subparsers.add_parser("trend", help="Daily trend")
    add_common_flags(p_trend)
    p_trend.add_argument("--days", type=int, default=30, help="Trend lookback (days)")
    p_trend.set_defaults(func=cmd_trend)

    args = parser.parse_args()

    # Build monitor with CLI overrides
    monitor = IngestMonitor(
        dsn=args.dsn,
        max_failure_rate=args.max_failure_rate,
        stale_running_hours=args.hours,
        window_days=args.window_days,
    )

    try:
        with monitor:
            return args.func(monitor, args)
    except psycopg2.OperationalError as exc:
        print(f"DB connection error: {exc}", file=sys.stderr)
        return 11
    except psycopg2.errors.Error as exc:
        print(f"SQL error: {exc}", file=sys.stderr)
        return 12
    except Exception as exc:
        print(f"Internal error: {exc}", file=sys.stderr)
        return 99


if __name__ == "__main__":
    sys.exit(main())