"""S2.3-lite project_event additive migration — schema verification.

Per Cursor tasking 204 §NOW.2:
  ≥3 cases: 列存在 / 表存在 / 无 score·rating·rank·total_score
  建议含 `import psycopg2.extras`  ←从 knife 3 教训固化

Mirrors tests/test_policy_commitment_s22lite.py shape.

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
MIGRATION_PATH = REPO_ROOT / "schema" / "migrations" / "010_project_event_alignment.sql"


# 11 new columns per docs/38 §2.1 (per-table subset of S2.2's 23 cols)
EXPECTED_NEW_COLUMNS: dict[str, list[tuple[str, str]]] = {
    "project_event": [
        ("canonical_project_name", "text"),
        ("project_name_en", "text"),
        ("project_class", "text"),
        ("status_year", "integer"),
        ("lineage", "jsonb"),
        ("project_hash_canonical", "text"),
        ("investment_currency_canonical", "text"),
        ("expected_output_text", "text"),
        ("delay_reason", "text"),
        ("completion_year_planned", "integer"),
        ("completion_year_actual", "integer"),
    ],
}

EXPECTED_TABLE = "project_event"

# 红线字段 — 任何打分语义字段都不能出现 (per docs/04 §3.8 + docs/38 §8 + tasking 204 §红线)
FORBIDDEN_COLUMN_PATTERNS = (
    "score",
    "rating",
    "rank",
    "total_score",
    "credit_score",
    "performance_score",
)

# 4 new indexes per docs/38 §3.1
EXPECTED_INDEXES = (
    "idx_project_event_hash_canonical",
    "idx_project_event_lineage_gin",
    "idx_project_event_class",
    "idx_project_event_status_year",
)


@pytest.fixture(scope="module")
def conn():
    """Live DB connection for S2.3-lite project_event migration tests."""
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
    """Load 010 migration SQL verbatim — used to assert file presence + idempotency."""
    assert MIGRATION_PATH.exists(), (
        f"migration file missing: {MIGRATION_PATH}"
    )
    return MIGRATION_PATH.read_text(encoding="utf-8")


def test_migration_010_columns_present(conn, migration_sql) -> None:
    """Case 1: 11 列 must exist on project_event (per docs/38 §2.1)."""
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
                    f"{table}.{col_name} missing after migration 010"
                )
                actual_type, is_nullable = found[col_name]
                # TEXT columns normalize to 'text'; INTEGER to 'integer'; JSONB to 'jsonb'
                assert actual_type == expected_type, (
                    f"{table}.{col_name} type mismatch: "
                    f"expected={expected_type} actual={actual_type}"
                )
                # 红线: 新列必须全部可空 (additive, 不破坏既有数据)
                assert is_nullable == "YES", (
                    f"{table}.{col_name} must be nullable (additive contract)"
                )


def test_project_event_table_exists(conn) -> None:
    """Case 2: project_event 表 must exist in cegr schema."""
    with conn.cursor() as cur:
        cur.execute(
            """
            SELECT 1
            FROM information_schema.tables
            WHERE table_schema = 'cegr'
              AND table_name = %s
            """,
            (EXPECTED_TABLE,),
        )
        assert cur.fetchone() is not None, (
            f"{EXPECTED_TABLE} missing from cegr schema "
            f"(01-core.sql §785-798 must be applied first)"
        )


def test_no_score_like_fields_on_project_event(conn) -> None:
    """Case 3 (red line): 任何 score·rating·rank·total_score 字段都禁止出现."""
    with conn.cursor() as cur:
        cur.execute(
            """
            SELECT column_name
            FROM information_schema.columns
            WHERE table_schema = 'cegr'
              AND table_name = %s
            """,
            (EXPECTED_TABLE,),
        )
        cols = {r[0].lower() for r in cur.fetchall()}
        for forbidden in FORBIDDEN_COLUMN_PATTERNS:
            matches = [c for c in cols if forbidden in c]
            assert not matches, (
                f"red-line violation: {EXPECTED_TABLE} has forbidden columns "
                f"{matches} matching '{forbidden}'"
            )


def test_lineage_column_jsonb_on_project_event(conn) -> None:
    """Case 4 (bonus): lineage column must be JSONB (per R3-E provenance)."""
    with conn.cursor() as cur:
        cur.execute(
            """
            SELECT data_type
            FROM information_schema.columns
            WHERE table_schema = 'cegr'
              AND table_name = 'project_event'
              AND column_name = 'lineage'
            """
        )
        row = cur.fetchone()
        assert row is not None, "project_event.lineage column missing"
        assert row[0] == "jsonb", (
            f"project_event.lineage type must be jsonb, got {row[0]}"
        )


def test_migration_010_idempotent(conn, migration_sql) -> None:
    """Case 5 (bonus): migration 010 must apply cleanly twice (IF NOT EXISTS).

    Per Cursor audit 206 FAIL fix:
      naive split on `;` broke two ways:
        (a) trailing `-- End of migration 010.` became an empty query;
        (b) `COMMENT ON COLUMN ... IS '...; ...'` lines have `;` inside a
            single-quoted string literal, so naive split chopped them mid-string
            and produced unterminated-quote SyntaxErrors.
      Fix: strip line + block comments first, then split on `;` with a
      quote-aware state machine that respects `'...'` literals (handling `''`
      as an escaped single quote). Empty / whitespace-only statements are
      dropped. The 010 file has no `$$`-quoted strings, so single-quote only
      is sufficient.
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
                    # check for escaped single quote ''
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

    # Strip line + block comments first so trailing `-- End of migration 010.`
    # becomes a no-op chunk rather than a fake empty query.
    sql_no_comments = re.sub(r"--[^\n]*", "", migration_sql)
    sql_no_comments = re.sub(r"/\*.*?\*/", "", sql_no_comments, flags=re.DOTALL)
    statements = _split_quote_aware(sql_no_comments)
    assert statements, "migration 010 has no statements after comment strip"

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


def test_migration_010_indexes_present(conn) -> None:
    """Case 6 (bonus): 4 new indexes must exist per docs/38 §3.1."""
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
        assert not missing, f"missing indexes after migration 010: {missing}"


def test_migration_file_has_no_score_fields(migration_sql) -> None:
    """Case 7 (bonus, file-level): SQL file text itself must not name scoring fields.

    Static guard — catches future regressions where someone re-adds a
    score/rating column directly to migration 010.
    """
    text = migration_sql.lower()
    # strip line + block comments (knife 3 lesson re: smoke-check scanner)
    import re

    text = re.sub(r"--[^\n]*", "", text)
    text = re.sub(r"/\*.*?\*/", "", text, flags=re.DOTALL)
    for forbidden in FORBIDDEN_COLUMN_PATTERNS:
        assert forbidden not in text, (
            f"migration 010 SQL text contains forbidden token '{forbidden}'"
        )


def test_seed_loader_module_loadable() -> None:
    """Case 8 (bonus): tests/s23lite prep — script entry path must be importable.

    S2.3-lite 落地刀不写 seed/loader (per tasking 204 §SCHEMA: 仅 DDL + pytest).
    This test is a stub asserting no `scripts/seed_project_event_demo.py`
    has been wrongly introduced yet — guards the knife boundary.
    """
    candidate = REPO_ROOT / "scripts" / "seed_project_event_demo.py"
    if not candidate.exists():
        # 符合任务书: 本刀不写 seed/loader
        return
    spec = importlib.util.spec_from_file_location("seed_project_event_demo", candidate)
    assert spec and spec.loader, "seed loader module spec missing"
    mod = importlib.util.module_from_spec(spec)
    try:
        spec.loader.exec_module(mod)
    except Exception as exc:  # noqa: BLE001
        pytest.fail(f"seed_project_event_demo.py failed to import: {exc}")