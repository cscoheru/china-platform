#!/usr/bin/env python3
"""Stage 1 / S1.6 — tests for backend/src/china_platform/connectors/provincial_yearbook.py.

Per Cursor 50 §NOW + docs/20-stage1-s16-provincial-yearbook-plan-20260824.md §7:
  * hash — compute_sha256 reproducible across calls
  * obs count — extract() returns ≥1 observation (and ≥1 row with
                 quarterly_data_verified=False per B-06)
  * ingest_run status — ingest() writes ingestion_run row with valid status
  * period metadata completeness — every row carries period_start/end/label/type;
    lineage JSONB has chain_id + sha256 + url + extractor_version;
    indicator_canonical is snake-case English (no Chinese indicator_zh in DB-bound fields).

Per docs/20 §6: NO skip; FileNotFoundError → pytest.fail (mandatory).
"""
from __future__ import annotations

import hashlib
import json
import re
import sys
from pathlib import Path

import psycopg2
import psycopg2.errors
import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent

# Make the package importable
sys.path.insert(0, str(REPO_ROOT / "backend" / "src"))

from china_platform.connectors.provincial_yearbook import (  # noqa: E402
    ProvincialYearbookConnector,
)

# Class-level constants — access via class so we don't import private names
DOMAIN = ProvincialYearbookConnector.DEFAULT_REGISTRY_DOMAIN
CATEGORY = ProvincialYearbookConnector.DEFAULT_REGISTRY_CATEGORY

# Spike 02 sample — the single file used by the S1.6 pilot
SAMPLE_XLSX = REPO_ROOT / "spikes" / "02-provincial-yearbook" / "hubei_2026_06.xlsx"
EXPECTED_SHA = (
    "c5cf5abeb4fdf97af52567f0640470d631bc9ac329dcc98f14e5d40bf6a5cac7"
)

DSN = "postgresql://postgres:postgres@127.0.0.1:55440/cegr_test"
VALID_STATUSES = {"SUCCESS", "PARTIAL", "FAILED", "RUNNING"}

# Snake-case English canonical indicator regex — only [a-z0-9_]+ allowed
SNAKE_CASE_RE = re.compile(r"^[a-z][a-z0-9_]*$")

# Allowed period_type values per docs/20 §1.2
ALLOWED_PERIOD_TYPES = {
    "CUMULATIVE_HALF_YEAR",
    "CUMULATIVE_5MONTH",
    "PERIOD_END_OF_MONTH",
    "INDEX_YOY",
    "PERIOD_END_YOY",
    "CUMULATIVE_YOY",
    "CUMULATIVE_YOY_5MONTH",
}


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
def connector() -> ProvincialYearbookConnector:
    return ProvincialYearbookConnector()


# ---------------------------------------------------------------------
# Cursor 50 §NOW test 1 — hash reproducibility
# ---------------------------------------------------------------------


def test_compute_sha256_matches_known_digest() -> None:
    """compute_sha256 must match the recorded spike 02 sample SHA-256."""
    if not SAMPLE_XLSX.exists():
        pytest.fail(f"mandatory sample missing: {SAMPLE_XLSX}")
    h = hashlib.sha256()
    with open(SAMPLE_XLSX, "rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            h.update(chunk)
    assert h.hexdigest() == EXPECTED_SHA, (
        f"sample SHA-256 drift: expected={EXPECTED_SHA} got={h.hexdigest()}"
    )


def test_connector_compute_sha256_reproducible(connector) -> None:
    """Calling compute_sha256 on the same file twice returns the same digest."""
    if not SAMPLE_XLSX.exists():
        pytest.fail(f"mandatory sample missing: {SAMPLE_XLSX}")
    a = connector.compute_sha256(SAMPLE_XLSX)
    b = connector.compute_sha256(SAMPLE_XLSX)
    assert a == b
    assert len(a) == 64
    assert all(c in "0123456789abcdef" for c in a)


# ---------------------------------------------------------------------
# Cursor 50 §NOW test 2 — extract produces ≥1 observation with ≥1
# quarterly_data_verified=False row
# ---------------------------------------------------------------------


def test_extract_returns_observations(connector) -> None:
    """extract() returns ≥1 observation. spike 02 sample yields 19 data rows;
    ≥1 row must carry quarterly_data_verified=False (B-06: GDP / 居民收入
    are quarterly numbers labelled as half-year cumulative; authoritative
    methodology verification pending).
    """
    if not SAMPLE_XLSX.exists():
        pytest.fail(f"mandatory sample missing: {SAMPLE_XLSX}")
    out = connector.extract(SAMPLE_XLSX)
    assert "sha256" in out
    assert "observations" in out
    assert "metadata" in out
    assert out["sha256"] == EXPECTED_SHA
    assert isinstance(out["observations"], list)
    assert len(out["observations"]) >= 1, (
        "spike 02 sample must yield ≥1 observation; if 0, parser regressed"
    )
    # Per Cursor 50 §NOW: ≥1 行 quarterly_data_verified=False
    n_unverified = sum(
        1 for r in out["observations"] if r.get("quarterly_data_verified") is False
    )
    assert n_unverified >= 1, (
        f"expected ≥1 row with quarterly_data_verified=False per B-06; got {n_unverified}"
    )
    md = out["metadata"]
    assert md["extraction_method"].startswith("openpyxl")
    assert md["province_zh"] == "湖北"
    assert md["province_code_gb2260"] == "42"
    assert md["file_size_bytes"] == SAMPLE_XLSX.stat().st_size


def test_extract_missing_file_raises(connector) -> None:
    """Per docs/20 §5: FileNotFoundError → pytest.fail-equivalent. We assert
    the connector surfaces the FileNotFoundError cleanly (no swallowing)."""
    ghost = REPO_ROOT / "spikes" / "02-provincial-yearbook" / "_nope.xlsx"
    if ghost.exists():
        pytest.skip(f"unexpected: {ghost} exists")
    with pytest.raises(FileNotFoundError):
        connector.extract(ghost)


# ---------------------------------------------------------------------
# Cursor 50 §NOW test 3 — period metadata 完整性
# (含 ≥1 quarterly_data_verified=False + lineage JSONB 完整 + indicator_canonical 蛇形)
# ---------------------------------------------------------------------


def test_extract_period_metadata_completeness(connector) -> None:
    """Every observation must carry:
        * period_start / period_end (DATE strings)
        * period_label (Chinese source label, allowed in DB)
        * period_type (one of ALLOWED_PERIOD_TYPES — NOT collapsed to one value)
        * lineage (JSONB with chain_id + source_file_sha256 + source_file_url
          + extractor_version)
        * indicator_canonical (snake-case English; NO Chinese characters)

    Cursor 50 §NOW hard requirement: ≥1 row with quarterly_data_verified=False.
    """
    if not SAMPLE_XLSX.exists():
        pytest.fail(f"mandatory sample missing: {SAMPLE_XLSX}")
    out = connector.extract(SAMPLE_XLSX)
    rows = out["observations"]

    period_starts = set()
    period_types = set()
    unverified_indicators: list[str] = []

    for r in rows:
        # period metadata required
        assert r.get("period_start"), f"missing period_start in row {r.get('row_index')}"
        assert r.get("period_end"), f"missing period_end in row {r.get('row_index')}"
        assert r.get("period_label"), f"missing period_label in row {r.get('row_index')}"
        ptype = r.get("period_type")
        assert ptype in ALLOWED_PERIOD_TYPES, (
            f"unexpected period_type {ptype!r} in row {r.get('row_index')}; "
            f"allowed={ALLOWED_PERIOD_TYPES}"
        )
        period_starts.add(r["period_start"])
        period_types.add(ptype)

        # lineage required (migration 004 JSONB column contract)
        lin = r.get("lineage")
        assert isinstance(lin, dict), f"lineage must be dict, got {type(lin)}"
        for k in ("chain_id", "source_file_sha256", "source_file_url", "extractor_version"):
            assert k in lin, f"lineage missing key {k!r} in row {r.get('row_index')}"
        assert lin["source_file_sha256"] == EXPECTED_SHA
        assert lin["extractor_version"] == "2.0"
        assert "hubei-2026-h1" in lin["chain_id"]  # spike 02 chain_id prefix

        # indicator_canonical must be snake-case English (no Chinese)
        canonical = r.get("indicator_canonical")
        assert canonical, f"missing indicator_canonical in row {r.get('row_index')}"
        assert SNAKE_CASE_RE.match(canonical), (
            f"indicator_canonical {canonical!r} not snake-case English"
        )
        # 中文 indicator_zh 仅入 period_label / caveat — 不可在 DB 列上保留
        # 此处我们仅做结构校验：canonical 字段本身不应含 CJK 字符
        assert not re.search(r"[一-鿿]", canonical), (
            f"indicator_canonical contains CJK chars: {canonical!r}"
        )

        # quarterly_data_verified=False 行累计
        if r.get("quarterly_data_verified") is False:
            unverified_indicators.append(r["indicator_zh"])

    # B-06 强制：至少 1 行 quarterly_data_verified=False
    assert len(unverified_indicators) >= 1, (
        "B-06 hard requirement: ≥1 row with quarterly_data_verified=False "
        "(GDP / 居民收入 are quarterly numbers labelled half-year cumulative)"
    )

    # 红线 ❌ 不漂移 CUMULATIVE_HALF_YEAR：period_type 至少含 ≥2 个不同值
    assert len(period_types) >= 2, (
        f"period_type must NOT be collapsed to a single value; got {period_types}"
    )


def test_extract_indicator_canonical_no_chinese_in_db_bound_fields(connector) -> None:
    """Red line (docs/20 §6): ❌ 中文 indicator_zh 不进 DB.

    We assert that the *indicator_canonical* field (the one that lands in
    observation rows via FK resolution) is snake-case English, and that the
    *only* fields that may carry Chinese are period_label and caveat
    (allowed: they mirror source-sheet strings).
    """
    if not SAMPLE_XLSX.exists():
        pytest.fail(f"mandatory sample missing: {SAMPLE_XLSX}")
    out = connector.extract(SAMPLE_XLSX)
    rows = out["observations"]

    for r in rows:
        canonical = r["indicator_canonical"]
        # `unknown__` 前缀表示未映射（行级 fallback） — 也必须不含中文
        if canonical.startswith("unknown__"):
            assert not re.search(r"[一-鿿]", canonical)
            continue
        # 正常映射：英文蛇形
        assert SNAKE_CASE_RE.match(canonical)
        assert not re.search(r"[一-鿿]", canonical)

    # 期许：sample 中至少有一行 indicator_canonical 是 snake_case（非 unknown__）
    n_canonical = sum(
        1 for r in rows
        if r["indicator_canonical"]
        and not r["indicator_canonical"].startswith("unknown__")
    )
    assert n_canonical >= 5, (
        f"expected ≥5 rows with mapped snake_case canonical; got {n_canonical}"
    )


# ---------------------------------------------------------------------
# Cursor 50 §NOW test 4 — ingest_run row exists with valid status
# ---------------------------------------------------------------------


def _dsn_conn() -> psycopg2.extensions.connection:
    return psycopg2.connect(DSN)


def _registry_id_for_hubei(conn: psycopg2.extensions.connection) -> str:
    """Resolve the source_registry id used by the connector.

    Note: registry category is PROVINCIAL_BULLETIN (matches the CSV row for
    tjj.hubei.gov.cn). The connector class name "ProvincialYearbookConnector"
    reflects its technical role (xlsx yearbook parsing), not the administrative
    category.
    """
    with conn.cursor() as cur:
        cur.execute(
            """
            SELECT id FROM cegr.source_registry
            WHERE domain = %s AND category = %s
            LIMIT 1
            """,
            (DOMAIN, CATEGORY),
        )
        row = cur.fetchone()
    if row is None:
        pytest.fail(
            "source_registry row for tjj.hubei.gov.cn/PROVINCIAL_BULLETIN "
            "missing; run scripts/import_registry_csv.py first"
        )
    return str(row[0])


def test_ingest_writes_ingestion_run_with_valid_status(
    connector, imported_registry
) -> None:
    """ingest() writes a cegr.ingestion_run row with status in
    {SUCCESS, PARTIAL, FAILED}. S1.6 pilot: observation FK is expected to
    fail (no reference data yet) so PARTIAL/FAILED is the honest outcome;
    this test only asserts the row exists with a valid enum status."""
    if not SAMPLE_XLSX.exists():
        pytest.fail(f"mandatory sample missing: {SAMPLE_XLSX}")

    conn = _dsn_conn()
    try:
        _registry_id_for_hubei(conn)  # ensures registry imported
        summary = connector.ingest(
            SAMPLE_XLSX, conn, triggered_by="test_provincial_yearbook_connector"
        )
        assert summary["status"] in VALID_STATUSES, (
            f"unexpected ingest status: {summary['status']!r}"
        )
        assert summary["records_extracted"] >= 1
        # Verify the ingestion_run row exists in the DB
        with conn.cursor() as cur:
            cur.execute(
                "SELECT status, records_extracted, records_inserted "
                "FROM cegr.ingestion_run WHERE id = %s",
                (summary["ingestion_run_id"],),
            )
            row = cur.fetchone()
        assert row is not None, (
            f"ingestion_run row vanished: {summary['ingestion_run_id']}"
        )
        db_status, db_extracted, db_inserted = row
        assert db_status == summary["status"]
        assert db_extracted == summary["records_extracted"]
        assert db_inserted == summary["records_inserted"]
    finally:
        conn.close()


def test_ingest_records_inserted_le_records_extracted(
    connector, imported_registry
) -> None:
    """Defense-in-depth: in S1.6 pilot (no reference data), observation INSERTs
    must fail FK. So records_inserted ≤ records_extracted. If it ever equals
    records_extracted, reference data was seeded and S1.6 pilot scope evolved —
    update docs/20 §3."""
    if not SAMPLE_XLSX.exists():
        pytest.fail(f"mandatory sample missing: {SAMPLE_XLSX}")

    conn = _dsn_conn()
    try:
        _registry_id_for_hubei(conn)  # ensures registry imported
        summary = connector.ingest(
            SAMPLE_XLSX, conn, triggered_by="test_provincial_yearbook_connector"
        )
        assert summary["records_inserted"] <= summary["records_extracted"]
        if summary["records_inserted"] == 0:
            # 0 inserted but ≥1 extracted → PARTIAL or FAILED
            assert summary["status"] in {"PARTIAL", "FAILED"}, (
                f"0 inserted but status={summary['status']!r}; "
                f"expected PARTIAL/FAILED"
            )
    finally:
        conn.close()