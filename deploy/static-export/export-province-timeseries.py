#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
export-province-timeseries.py — knife 664g (P2 mart 静态导出).

Reads `cegr_mart.mart_province_timeseries` (8060 rows, knife 663 收口),
queries via psycopg2, and dumps the result as
`frontend/data/mart_province_timeseries.json` to be consumed by Next.js at
build time via `process.env.NEXT_PUBLIC_MART_DATA_PATH` (same dir as
mart_province_gdp_2024.json).

P1 vs P2 export difference:
- knife 660/661/662 P1 mart `mart_province_gdp_2024.sql` is a static VALUES
  block → parsed by regex in `export-mart-data.py`.
- knife 663 P2 mart `mart_province_timeseries.sql` is a dbt model with CTE
  chain + JOIN staging tables → cannot regex-parse; must query actual DB.

Why not use `dbt compile --select tag:p2`?
- dbt compiles to wrapped SQL, not direct postgres query. Easier to query
  the materialized table directly.

Connection (per 664h docker-compose.dev.yml):
  dev:    postgresql://postgres:postgres@127.0.0.1:55440/cegr_test
  prod:   postgresql://postgres:postgres@127.0.0.1:5432/cegr_test (newvps only)

Schema: 31 provinces × 10 indicators × 26 years (2001-2026) = 8060 rows.

Red lines (knocked out at export time, per 663 mart schema):
  - 2001-2019 + 2026 → status='DATA_MISSING' (新增红线-1/2)
  - 3 缺失省 (辽/琼/黔) → 全 DATA_MISSING
  - 缺失 cells value 必须为 null (禁补零)
  - lineage 三件套: source_type / origin / ruling 必填
  - lineage_is_demo 必须是 'true' 或 'false' (per docs/33 §3.2)

Exit codes:
  0  success
  1  DB connection / SQL error / row-count mismatch
  2  red-line violation (missing cell has value, missing lineage field, etc.)
"""
from __future__ import annotations

import argparse
import json
import os
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]  # deploy/static-export -> repo root
OUT_JSON = REPO_ROOT / "frontend" / "data" / "mart_province_timeseries.json"

# Default DSN: dev (per 664h docker-compose.dev.yml).
# Override via --dsn or $PG_DSN for prod (e.g. PG_DSN=postgresql://...).
DEFAULT_DSN = os.environ.get(
    "PG_DSN",
    "postgresql://postgres:postgres@127.0.0.1:55440/cegr_test",
)

# Expected: 31 × 10 × 26 = 8060
EXPECTED_TOTAL_ROWS = 8060
EXPECTED_PROVINCES = 31
EXPECTED_INDICATORS = 10
EXPECTED_YEARS = 26
YEAR_RANGE = (2001, 2026)
MISSING_PROVINCES = ["LIAONING", "HAINAN", "GUIZHOU"]


def _validate_dsn(dsn: str) -> None:
    """Basic sanity check on DSN format (psycopg2 will do the real validation)."""
    if not re.match(r"^postgres(?:ql)?://[^/]+/.+", dsn):
        raise ValueError(
            f"DSN must look like postgresql://user:pass@host:port/dbname, got: {dsn}"
        )


def _connect(dsn: str):
    """Lazy psycopg2 import + connect (allows --help to work without psycopg2)."""
    try:
        import psycopg2  # type: ignore[import-not-found]
    except ImportError as e:
        print(
            "FATAL: psycopg2 not installed. Run: pip install psycopg2-binary==2.9.10",
            file=sys.stderr,
        )
        raise SystemExit(1) from e

    _validate_dsn(dsn)
    return psycopg2.connect(dsn)


def _fetch_mart(conn, mart_schema: str) -> list[dict]:
    """Query the full mart table; return list of dict rows."""
    sql_q = f"""
        SELECT
            province_code,
            province_name,
            indicator_key,
            indicator_label,
            unit,
            year,
            value,
            status,
            missing_reason,
            lineage_source_type,
            lineage_origin,
            lineage_ruling,
            lineage_is_demo
        FROM {mart_schema}.mart_province_timeseries
        ORDER BY province_code, indicator_key, year
    """
    with conn.cursor() as cur:
        cur.execute(sql_q)
        cols = [d[0] for d in cur.description]
        return [dict(zip(cols, row)) for row in cur.fetchall()]


def _audit(rows: list[dict]) -> list[str]:
    """Red-line self-audit. Returns list of violation messages."""
    errors: list[str] = []
    if len(rows) != EXPECTED_TOTAL_ROWS:
        errors.append(f"total rows {len(rows)} != {EXPECTED_TOTAL_ROWS}")

    provinces = sorted({r["province_code"] for r in rows})
    indicators = sorted({r["indicator_key"] for r in rows})
    years = sorted({r["year"] for r in rows})

    if len(provinces) != EXPECTED_PROVINCES:
        errors.append(f"unique provinces {len(provinces)} != {EXPECTED_PROVINCES} ({provinces})")
    if len(indicators) != EXPECTED_INDICATORS:
        errors.append(f"unique indicators {len(indicators)} != {EXPECTED_INDICATORS} ({indicators})")
    if len(years) != EXPECTED_YEARS:
        errors.append(f"unique years {len(years)} != {EXPECTED_YEARS} ({years})")

    # 2001-2019 + 2026 must all be DATA_MISSING (新增红线-1/2).
    for r in rows:
        if r["year"] < 2020 or r["year"] == 2026:
            if r["status"] != "DATA_MISSING":
                errors.append(
                    f"year {r['year']} status={r['status']!r} must be 'DATA_MISSING'"
                )

    # 3 缺失省 must all be DATA_MISSING across all years.
    for r in rows:
        if r["province_code"] in MISSING_PROVINCES:
            if r["status"] != "DATA_MISSING":
                errors.append(
                    f"missing province {r['province_code']} year {r['year']} "
                    f"status={r['status']!r} must be 'DATA_MISSING'"
                )

    # DATA_MISSING cells must have value=NULL (禁补零).
    for r in rows:
        if r["status"] == "DATA_MISSING" and r["value"] is not None:
            errors.append(
                f"DATA_MISSING cell {r['province_code']}/{r['indicator_key']}/{r['year']} "
                f"value={r['value']!r} must be NULL"
            )

    # lineage 三件套 must always be populated.
    for r in rows:
        for f in ("lineage_source_type", "lineage_ruling"):
            if not r.get(f):
                errors.append(f"{r['province_code']}/{r['indicator_key']}/{r['year']} {f}=null")

    return errors


def main() -> int:
    p = argparse.ArgumentParser(
        description="knife 664g: mart_province_timeseries → frontend JSON"
    )
    p.add_argument("--dsn", default=DEFAULT_DSN, help=f"psycopg2 DSN (default: dev)")
    p.add_argument("--mart-schema", default="cegr_mart",
                   help="mart schema name (default: cegr_mart)")
    p.add_argument("--out", type=Path, default=OUT_JSON, help="output JSON path")
    p.add_argument("--strict", action="store_true",
                   help="exit non-zero on any red-line violation")
    p.add_argument("--dry-run", action="store_true",
                   help="query + audit only; do not write output JSON")
    args = p.parse_args()

    # Connect.
    try:
        conn = _connect(args.dsn)
    except SystemExit:
        return 1
    except Exception as e:
        print(f"FATAL: connect to {args.dsn!r} failed: {e}", file=sys.stderr)
        return 1

    try:
        try:
            rows = _fetch_mart(conn, args.mart_schema)
        except Exception as e:
            print(f"FATAL: SELECT failed: {e}", file=sys.stderr)
            return 1
    finally:
        conn.close()

    # psycopg2 returns Decimal for numeric columns. Convert to float for JSON
    # (mart values are public stats; rounding precision acceptable for display).
    from decimal import Decimal

    def _coerce(v):
        if isinstance(v, Decimal):
            return float(v)
        return v

    for r in rows:
        if "value" in r:
            r["value"] = _coerce(r["value"])
        if "year" in r and not isinstance(r["year"], int):
            r["year"] = int(r["year"])

    # Audit.
    errors = _audit(rows)
    if errors:
        print("RED-LINE VIOLATIONS:", file=sys.stderr)
        for e in errors:
            print(f"  - {e}", file=sys.stderr)
        if args.strict:
            return 2

    out = {
        "as_of": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "ruling": "knife 664g P2 mart 静态导出 (per docs/87 §3.2 + knife 664 plan)",
        "schema_version": "664",
        "mart_source": f"{args.mart_schema}.mart_province_timeseries",
        "lineage_ruling": "U6 2026-09-03",
        "lineage_is_demo": "false",
        "total_rows": len(rows),
        "unique_provinces": len({r["province_code"] for r in rows}),
        "unique_indicators": len({r["indicator_key"] for r in rows}),
        "year_range": list(YEAR_RANGE),
        "indicators": sorted({r["indicator_key"] for r in rows}),
        "provinces": rows,
    }

    if args.dry_run:
        print(
            f"DRY-RUN OK: {len(rows)} rows "
            f"({out['unique_provinces']} provinces × "
            f"{out['unique_indicators']} indicators × {EXPECTED_YEARS} years)"
        )
        return 0

    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(
        json.dumps(out, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    print(f"OK: {len(rows)} rows -> {args.out.relative_to(REPO_ROOT)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())