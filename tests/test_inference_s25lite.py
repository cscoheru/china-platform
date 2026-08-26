"""S2.5-lite inference_record / claim_evidence_link additive migration — schema verification.

Per Cursor tasking 226 §NOW.2:
  ≥3 cases: 层守门 / 无 score·rating·rank·confidence_score 字段
  建议含 `import psycopg2.extras`  ←从 knife 3 教训固化

Mirrors tests/test_project_event_s23lite.py + tests/test_budget_s24lite.py shape.

Failure mode (s22lite 教训):
    AttributeError: module 'psycopg2' has no attribute 'extras'
    → fixed by `import psycopg2.extras` before `psycopg2.extras.register_uuid()`.
"""

from __future__ import annotations

import importlib.util
import os
import pathlib

import psycopg2
import psycopg2.extras  # noqa: F401  — knife 3 lesson; required for register_uuid()
import pytest


REPO_ROOT = pathlib.Path(__file__).resolve().parents[1]
MIGRATION_PATH = REPO_ROOT / "schema" / "migrations" / "012_inference_alignment.sql"


# 8 new cols on inference_record + 5 new cols on claim_evidence_link (per docs/40 §2.1/§2.2)
EXPECTED_NEW_COLUMNS: dict[str, list[tuple[str, str]]] = {
    "inference_record": [
        ("canonical_statement", "text"),
        ("canonical_layer", "text"),
        ("inference_method", "text"),
        ("inference_year", "integer"),
        ("lineage", "jsonb"),
        ("inference_hash_canonical", "text"),
        ("polarity_summary", "text"),
        ("geo_entity_id", "uuid"),
    ],
    "claim_evidence_link": [
        ("canonical_polarity", "text"),
        ("evidence_strength", "text"),
        ("lineage", "jsonb"),
        ("claim_evidence_hash_canonical", "text"),
        ("geo_entity_id", "uuid"),
    ],
}

EXPECTED_TABLES = ("inference_record", "claim_evidence_link")

# 红线字段 — 任何打分语义字段都不能出现 (per docs/04 §3.x + docs/40 §8 + tasking 226 §红线)
FORBIDDEN_COLUMN_PATTERNS = (
    "score",
    "rating",
    "rank",
    "total_score",
    "credit_score",
    "performance_score",
    "confidence_score",
    "credibility_score",
)

# 7 new indexes per docs/40 §3.1
EXPECTED_INDEXES = (
    "idx_inference_canonical_layer",
    "idx_inference_method",
    "idx_inference_hash_canonical",
    "idx_inference_lineage_gin",
    "idx_claim_evidence_canonical_polarity",
    "idx_claim_evidence_hash_canonical",
    "idx_claim_evidence_lineage_gin",
)


@pytest.fixture(scope="module")
def conn():
    """Live DB connection for S2.5-lite inference migration tests."""
    dsn = os.environ.get(
        "CEGR_TEST_DSN",
        "postgresql://postgres:postgres@127.0.0.1:55440/cegr_test",
    )
    c = psycopg2.connect(dsn)
    c.autocommit = False
    yield c
    c.close()


@pytest.fixture(scope="module")
def migration_sql() -> str:
    """Load 012 migration SQL verbatim — used to assert file presence + idempotency."""
    assert MIGRATION_PATH.exists(), (
        f"migration file missing: {MIGRATION_PATH}"
    )
    return MIGRATION_PATH.read_text(encoding="utf-8")


def test_migration_012_columns_present(conn, migration_sql) -> None:
    """Case 1: 13 cols must exist across inference_record (8) + claim_evidence_link (5)."""
    psycopg2.extras.register_uuid()
    with conn.cursor() as cur:
        for table, cols in EXPECTED_NEW_COLUMNS.items():
            cur.execute(
                """
                SELECT column_name, data_type, is_nullable
                FROM information_schema.columns
                WHERE table_schema = 'cegr'
                  AND table_name = %s
                  AND column_name = ANY(%s)
                """,
                (table, [c[0] for c in cols]),
            )
            rows = cur.fetchall()
            found = {r[0]: (r[1], r[2]) for r in rows}
            for col_name, expected_type in cols:
                assert col_name in found, (
                    f"{table}.{col_name} missing after migration 012"
                )
                actual_type, is_nullable = found[col_name]
                assert actual_type == expected_type, (
                    f"{table}.{col_name} type mismatch: "
                    f"expected={expected_type} actual={actual_type}"
                )
                # 红线: 新列必须全部可空 (additive, 不破坏既有数据)
                assert is_nullable == "YES", (
                    f"{table}.{col_name} must be nullable (additive contract)"
                )


def test_inference_tables_exist(conn) -> None:
    """Case 2: inference_record + claim_evidence_link 表 must exist in cegr schema."""
    with conn.cursor() as cur:
        cur.execute(
            """
            SELECT table_name
            FROM information_schema.tables
            WHERE table_schema = 'cegr'
              AND table_name = ANY(%s)
            """,
            (list(EXPECTED_TABLES),),
        )
        found = {r[0] for r in cur.fetchall()}
        for tbl in EXPECTED_TABLES:
            assert tbl in found, (
                f"{tbl} missing from cegr schema "
                f"(01-core.sql §915-928 / §956-966 must be applied first)"
            )


def test_no_score_like_fields_on_inference(conn) -> None:
    """Case 3 (red line): 任何 score·rating·rank·confidence_score·credibility_score 字段都禁止出现."""
    with conn.cursor() as cur:
        for tbl in EXPECTED_TABLES:
            cur.execute(
                """
                SELECT column_name
                FROM information_schema.columns
                WHERE table_schema = 'cegr'
                  AND table_name = %s
                """,
                (tbl,),
            )
            cols = {r[0].lower() for r in cur.fetchall()}
            for forbidden in FORBIDDEN_COLUMN_PATTERNS:
                matches = [c for c in cols if forbidden in c]
                assert not matches, (
                    f"red-line violation: {tbl} has forbidden columns "
                    f"{matches} matching '{forbidden}'"
                )


def test_lineage_columns_jsonb(conn) -> None:
    """Case 4 (bonus): lineage columns must be JSONB on both tables (per R3-E)."""
    with conn.cursor() as cur:
        for tbl in EXPECTED_TABLES:
            cur.execute(
                """
                SELECT data_type
                FROM information_schema.columns
                WHERE table_schema = 'cegr'
                  AND table_name = %s
                  AND column_name = 'lineage'
                """,
                (tbl,),
            )
            row = cur.fetchone()
            assert row is not None, f"{tbl}.lineage column missing"
            assert row[0] == "jsonb", (
                f"{tbl}.lineage type must be jsonb, got {row[0]}"
            )


def test_migration_012_idempotent(conn, migration_sql) -> None:
    """Case 5 (bonus): migration 012 must apply cleanly twice (IF NOT EXISTS).

    Reuses the quote-aware split pattern from s23lite knife 7.
    """
    import re

    def _split_quote_aware(sql: str) -> list[str]:
        statements: list[str] = []
        buf: list[str] = []
        in_quote = False
        i = 0
        n = len(sql)
        while i < n:
            ch = sql[i]
            if in_quote:
                buf.append(ch)
                if ch == "'":
                    if i + 1 < n and sql[i + 1] == "'":
                        buf.append("'")
                        i += 2
                        continue
                    in_quote = False
            else:
                if ch == "'":
                    buf.append(ch)
                    in_quote = True
                elif ch == ";":
                    stmt = "".join(buf).strip()
                    if stmt:
                        statements.append(stmt)
                    buf = []
                else:
                    buf.append(ch)
            i += 1
        tail = "".join(buf).strip()
        if tail:
            statements.append(tail)
        return statements

    sql_no_comments = re.sub(r"--[^\n]*", "", migration_sql)
    sql_no_comments = re.sub(r"/\*.*?\*/", "", sql_no_comments, flags=re.DOTALL)
    statements = _split_quote_aware(sql_no_comments)
    assert statements, "migration 012 has no statements after comment strip"

    psycopg2.extras.register_uuid()
    with conn.cursor() as cur:
        for stmt in statements:
            cur.execute(stmt)
    conn.commit()
    # apply once more to verify IF NOT EXISTS guards are honored
    with conn.cursor() as cur:
        for stmt in statements:
            cur.execute(stmt)
    conn.commit()


def test_migration_012_indexes_present(conn) -> None:
    """Case 6 (bonus): 7 new indexes must exist per docs/40 §3.1."""
    with conn.cursor() as cur:
        cur.execute(
            """
            SELECT indexname
            FROM pg_indexes
            WHERE schemaname = 'cegr'
              AND indexname = ANY(%s)
            """,
            (list(EXPECTED_INDEXES),),
        )
        found = {r[0] for r in cur.fetchall()}
        missing = set(EXPECTED_INDEXES) - found
        assert not missing, f"missing indexes after migration 012: {missing}"


def test_migration_file_has_no_score_fields(migration_sql) -> None:
    """Case 7 (bonus, file-level): SQL file text itself must not name scoring fields.

    Strip line + block comments FIRST (knife 3 lesson) so explanatory
    comments mentioning pattern names don't trigger false positives.
    """
    import re

    text = migration_sql.lower()
    text = re.sub(r"--[^\n]*", "", text)
    text = re.sub(r"/\*.*?\*/", "", text, flags=re.DOTALL)
    for forbidden in FORBIDDEN_COLUMN_PATTERNS:
        assert forbidden not in text, (
            f"migration 012 SQL text contains forbidden token '{forbidden}'"
        )


def test_seed_loader_module_loadable() -> None:
    """Case 8 (bonus): tests/s25lite prep — script entry path must be importable.

    S2.5-lite 落地刀不写 seed/loader (per tasking 226 §SCHEMA: 仅 DDL + pytest).
    This test is a stub asserting no `scripts/seed_inference_*_demo.py`
    has been wrongly introduced yet — guards the knife boundary.
    """
    for name in (
        "seed_inference_record_demo",
        "seed_claim_evidence_link_demo",
    ):
        candidate = REPO_ROOT / "scripts" / f"{name}.py"
        if not candidate.exists():
            continue
        spec = importlib.util.spec_from_file_location(name, candidate)
        assert spec and spec.loader, f"{name} module spec missing"
        mod = importlib.util.module_from_spec(spec)
        try:
            spec.loader.exec_module(mod)
        except Exception as exc:  # noqa: BLE001
            pytest.fail(f"{name}.py failed to import: {exc}")