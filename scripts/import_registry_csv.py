#!/usr/bin/env python3
"""Stage 1 / S1.3 — import source_registry/registry.csv into cegr.source_registry.

Per reviews/30-stage1-s13-registry-tasking-20260824.md §0.1.

Reads `source_registry/registry.csv` (18 columns) and UPSERTs each row into
the `cegr.source_registry` table (15 DB columns + 6 CSV-side metadata columns
added in migration 003_source_registry_declared_level.sql).

Mapping rules:
  * CSV `access_method` (free-text description) → extraction_method enum via
    a small lookup table. Unknown values raise (caller should patch).
  * CSV `backup_urls` is JSON-encoded list-as-string → TEXT[] via json.loads.
  * CSV `enabled` is "TRUE"/"FALSE" → Python bool.
  * CSV `file_size_bytes` → int (NULL allowed).
  * CSV `file_hash_sha256` must match `^[a-f0-9]{64}$` if present (DB CHECK).
  * CSV `source_level` and `declared_source_level` are both populated
    (NULL allowed for legacy/partial rows).

Connection: hard-coded to Stage 0 dev rig
  host=127.0.0.1 port=55440 user=postgres dbname=cegr_test
Override with DATABASE_URL env var (see .env.example).

Idempotent: re-running the script UPSERTs in place keyed on `primary_url`
(the existing unique index `idx_source_registry_url`). 6 rows expected.

Exit codes:
  0 = success
  2 = CSV missing or empty
  3 = DB connection / apply error
  4 = unknown access_method (script bug; needs maintenance)
"""
from __future__ import annotations

import csv
import json
import os
import re
import sys
from pathlib import Path

import psycopg2
from psycopg2.extras import execute_values

REPO_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_CSV = REPO_ROOT / "source_registry" / "registry.csv"

# CSV free-text → DB extraction_method enum (per schema/01-core.sql:50-58).
ACCESS_METHOD_MAP: dict[str, str] = {
    "OCR（JPG 扫描）": "IMAGE_OCR",
    "OCR（JPG扫描）": "IMAGE_OCR",
    "JPG 扫描": "IMAGE_OCR",
    "HTML": "HTML_PARSE",
    "HTML（散文形式 + 嵌入表格）": "HTML_PARSE",
    "HTML(散文形式)": "HTML_PARSE",
    "EXCEL": "EXCEL_PARSE",
    "XLSX": "EXCEL_PARSE",
    "OCR": "PDF_OCR",
    "OCR（四页灰度扫描 + 嵌入旧 OCR 文本层）": "PDF_OCR",
    "PDF_TEXT": "PDF_TEXT",
    "PDF_OCR": "PDF_OCR",
    "API": "API",
    "CSV_PARSE": "CSV_PARSE",
    "MANUAL_UPLOAD": "MANUAL_UPLOAD",
}

HEX64 = re.compile(r"^[a-f0-9]{64}$")


def _db_dsn() -> str:
    return os.environ.get(
        "DATABASE_URL",
        "postgresql://postgres:postgres@127.0.0.1:55440/cegr_test",
    )


def _coerce_access_method(raw: str) -> str:
    raw = (raw or "").strip()
    if raw in ACCESS_METHOD_MAP:
        return ACCESS_METHOD_MAP[raw]
    # Partial / fuzzy: try to find a key that appears as substring (e.g. "HTML" inside "HTML（散文形式）")
    for k, v in ACCESS_METHOD_MAP.items():
        if k in raw or raw in k:
            return v
    raise ValueError(f"unknown access_method in CSV: {raw!r}; extend ACCESS_METHOD_MAP")


def _coerce_backup_urls(raw: str) -> list[str] | None:
    raw = (raw or "").strip()
    if not raw:
        return None
    # CSV writes JSON list, possibly empty; tolerate stray quotes
    try:
        parsed = json.loads(raw)
    except json.JSONDecodeError as exc:
        raise ValueError(f"backup_urls not JSON: {raw!r}") from exc
    if not isinstance(parsed, list):
        raise ValueError(f"backup_urls not a JSON list: {raw!r}")
    return [str(x) for x in parsed]


def _coerce_bool(raw: str) -> bool:
    raw = (raw or "").strip().upper()
    if raw in ("TRUE", "1", "YES", "Y"):
        return True
    if raw in ("FALSE", "0", "NO", "N", ""):
        return False
    raise ValueError(f"unparseable bool: {raw!r}")


def _coerce_int_or_none(raw: str) -> int | None:
    raw = (raw or "").strip()
    if not raw:
        return None
    return int(raw)


def _validate_hash(raw: str) -> str | None:
    raw = (raw or "").strip()
    if not raw:
        return None
    if not HEX64.match(raw):
        raise ValueError(f"file_hash_sha256 not 64-hex: {raw!r}")
    return raw


def _row_to_params(row: dict[str, str]) -> tuple:
    """Map one CSV row to UPSERT params matching the SQL below."""
    return (
        row["domain"],
        row["organization"],
        row["category"],
        row["primary_url"],
        _coerce_backup_urls(row["backup_urls"]),
        row["update_frequency"] or None,
        row["auth_note"] or None,
        _coerce_access_method(row["access_method"]),
        row["historical_coverage"] or None,
        row["stability_note"] or None,
        row["failure_handling"] or None,
        _coerce_bool(row["enabled"]),
        row["source_level"] or None,
        row["declared_source_level"] or None,
        row["local_sample_path"] or None,
        _validate_hash(row["file_hash_sha256"]),
        _coerce_int_or_none(row["file_size_bytes"]),
        row["purpose_note"] or None,
    )


UPSERT_SQL = """
INSERT INTO cegr.source_registry (
    domain, organization, category, primary_url, backup_urls,
    update_frequency, auth_note, access_method,
    historical_coverage, stability_note, failure_handling, enabled,
    source_level, declared_source_level,
    local_sample_path, file_hash_sha256, file_size_bytes, purpose_note
) VALUES %s
ON CONFLICT (primary_url) DO UPDATE SET
    domain              = EXCLUDED.domain,
    organization        = EXCLUDED.organization,
    category            = EXCLUDED.category,
    backup_urls         = EXCLUDED.backup_urls,
    update_frequency    = EXCLUDED.update_frequency,
    auth_note           = EXCLUDED.auth_note,
    access_method       = EXCLUDED.access_method,
    historical_coverage = EXCLUDED.historical_coverage,
    stability_note      = EXCLUDED.stability_note,
    failure_handling    = EXCLUDED.failure_handling,
    enabled             = EXCLUDED.enabled,
    source_level        = EXCLUDED.source_level,
    declared_source_level = EXCLUDED.declared_source_level,
    local_sample_path   = EXCLUDED.local_sample_path,
    file_hash_sha256    = EXCLUDED.file_hash_sha256,
    file_size_bytes     = EXCLUDED.file_size_bytes,
    purpose_note        = EXCLUDED.purpose_note,
    updated_at          = NOW()
"""


def import_registry(csv_path: Path = DEFAULT_CSV, dsn: str | None = None) -> int:
    dsn = dsn or _db_dsn()
    if not csv_path.exists():
        print(f"FAIL: CSV not found: {csv_path}", file=sys.stderr)
        return 2
    with csv_path.open("r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        rows = list(reader)
    if not rows:
        print(f"FAIL: CSV has no data rows: {csv_path}", file=sys.stderr)
        return 2

    params = [_row_to_params(r) for r in rows]
    try:
        with psycopg2.connect(dsn) as conn:
            with conn.cursor() as cur:
                execute_values(cur, UPSERT_SQL, params, page_size=100)
            conn.commit()
    except Exception as exc:
        print(f"FAIL: DB apply error: {exc}", file=sys.stderr)
        return 3

    print(f"OK: imported {len(params)} rows from {csv_path} into cegr.source_registry")
    return 0


def main(argv: list[str] | None = None) -> int:
    argv = argv if argv is not None else sys.argv[1:]
    csv_arg = Path(argv[0]).resolve() if argv else DEFAULT_CSV
    return import_registry(csv_arg)


if __name__ == "__main__":
    raise SystemExit(main())