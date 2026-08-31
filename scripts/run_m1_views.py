"""Materialize cegr_staging views from scripts/materialize_m1_views.sql.

Per docs/55 §T4 (knife 629 §2 T4 Approach B). Idempotent: each
CREATE OR REPLACE replaces the view in place; safe to re-run.

Usage:
    PYTHONPATH=backend/src python3 scripts/run_m1_views.py

Exit 0 = all 3 views replaced successfully.
Exit 1 = any view creation failed (DSN unreachable, SQL error, etc.).
"""
from __future__ import annotations

import sys
from pathlib import Path

import psycopg2

REPO_ROOT = Path(__file__).resolve().parent.parent
SQL_FILE = REPO_ROOT / "scripts" / "materialize_m1_views.sql"
DSN = "postgresql://postgres:postgres@127.0.0.1:55440/cegr_test"


def main() -> int:
    if not SQL_FILE.exists():
        print(f"SQL file missing: {SQL_FILE}", file=sys.stderr)
        return 1

    sql_text = SQL_FILE.read_text(encoding="utf-8")

    conn = psycopg2.connect(DSN)
    try:
        with conn.cursor() as cur:
            cur.execute(sql_text)
        conn.commit()
    except psycopg2.Error as exc:
        print(f"materialize_m1_views failed: {exc}", file=sys.stderr)
        conn.rollback()
        return 1
    finally:
        conn.close()

    # Verify: the 3 expected views must exist after the SQL runs.
    expected = (
        "cegr_staging.stg_observation",
        "cegr_staging.stg_source_document",
        "cegr_staging.int_indicator_timeseries",
    )
    conn = psycopg2.connect(DSN)
    try:
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT table_schema, table_name, table_type
                FROM information_schema.tables
                WHERE table_schema = 'cegr_staging'
                  AND table_name IN ('stg_observation', 'stg_source_document',
                                     'int_indicator_timeseries')
                ORDER BY table_name
                """
            )
            rows = cur.fetchall()
        present = {(r[0], r[1]): r[2] for r in rows}
    finally:
        conn.close()

    missing = [name for name in expected if tuple(name.split(".")) not in present]
    if missing:
        print(
            f"views missing after materialize: {missing} (present: {present})",
            file=sys.stderr,
        )
        return 1

    print("materialize_m1_views: 3 views present (stg_observation, "
          "stg_source_document, int_indicator_timeseries)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
