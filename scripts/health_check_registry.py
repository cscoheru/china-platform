#!/usr/bin/env python3
"""Stage 1 / S1.3 — URL health-check dry-run (NO HTTP).

Per reviews/30-stage1-s13-registry-tasking-20260824.md §0.3 + docs/17 §1 S1.3.

Reads cegr.source_registry and *prints* what an HTTP health-check pass would
do — the URLs to probe, frequency hint, failure-handling rule, and CSV-side
declared source_level. **Never** opens a TCP connection, **never** sends an
HTTP request. The script is intentionally side-effect-free at the network layer
so it can run in CI, in scheduled dry-runs, and in audit replays without
risk of being mistaken for an ingestion pass.

Exit codes:
  0 = dry-run completed (rows inspected)
  2 = DB connection failed
"""
from __future__ import annotations

import os
import sys
from typing import Iterator

import psycopg2

DSN = os.environ.get(
    "DATABASE_URL",
    "postgresql://postgres:postgres@127.0.0.1:55440/cegr_test",
)


def _iter_registry_rows(dsn: str = DSN) -> Iterator[dict]:
    conn = psycopg2.connect(dsn)
    try:
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT
                    domain, organization, category, primary_url,
                    update_frequency, stability_note, failure_handling,
                    enabled, source_level, declared_source_level,
                    local_sample_path, file_hash_sha256
                FROM cegr.source_registry
                ORDER BY enabled DESC, domain, primary_url
                """
            )
            cols = [d[0] for d in cur.description]
            for row in cur.fetchall():
                yield dict(zip(cols, row))
    finally:
        conn.close()


def main(argv: list[str] | None = None) -> int:
    argv = argv if argv is not None else sys.argv[1:]
    dry_run = "--dry-run" in argv or "--no-http" in argv or True  # default ON

    print("=== source_registry URL health-check (DRY RUN) ===")
    print(f"DSN host : {DSN.split('@')[-1] if '@' in DSN else DSN}")
    print(f"mode     : {'DRY-RUN (no HTTP)' if dry_run else 'HTTP PROBE (NOT IMPLEMENTED)'}")
    print()

    total = 0
    enabled = 0
    by_freq: dict[str, int] = {}
    try:
        rows = list(_iter_registry_rows())
    except Exception as exc:
        print(f"FAIL: DB connection error: {exc}", file=sys.stderr)
        return 2

    for r in rows:
        total += 1
        if r["enabled"]:
            enabled += 1
        freq = (r["update_frequency"] or "UNKNOWN").upper()
        by_freq[freq] = by_freq.get(freq, 0) + 1

        flag_marker = "ENABLED " if r["enabled"] else "DISABLED"
        src_levels = f"{r['source_level'] or '-'} (declared {r['declared_source_level'] or '-'})"
        sample_path = r["local_sample_path"] or "(no local sample)"
        sample_hash = r["file_hash_sha256"] or "(no hash)"

        print(f"[{flag_marker}] {r['domain']} — {r['organization']}")
        print(f"    primary_url   : {r['primary_url']}")
        print(f"    category      : {r['category']}")
        print(f"    source_level  : {src_levels}")
        print(f"    update_freq   : {r['update_frequency']}")
        print(f"    stability     : {r['stability_note']}")
        print(f"    on_failure    : {r['failure_handling']}")
        print(f"    sample_path   : {sample_path}")
        print(f"    sample_sha256 : {sample_hash[:16]}…({sample_hash[:4]}…{sample_hash[-4:]})")
        print(f"    would_probe   : yes (DRY-RUN: not actually requested)")
        print()

    print("=== summary ===")
    print(f"total rows inspected : {total}")
    print(f"enabled              : {enabled}")
    print(f"by update_frequency  : {by_freq}")
    print()
    print("No HTTP traffic was generated. To run a real health check, implement a")
    print("separate script that consumes the same DB view and *does* send HTTP —")
    print("out of scope for S1.3 dry-run per reviews/30.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())