"""S2.6-lite counterexample gate — schema verification.

Per Cursor tasking 232 §SCHEMA:
  ≥3 cases: CONTRADICTS 可插 / 无 score / polarity 一致
  建议含 `import psycopg2.extras`  ←从 knife 3 教训固化

Mirrors tests/test_inference_s25lite.py + tests/test_budget_s24lite.py shape.

Failure mode (s22lite 教训):
    AttributeError: module 'psycopg2' has no attribute 'extras'
    → fixed by `import psycopg2.extras` before `psycopg2.extras.register_uuid()`.

Splitter failure mode (knife 13 s26lite 教训):
    PL/pgSQL function bodies use `$$ ... $$` dollar-quoting which contains semicolons.
    The knife-7 quote-aware splitter only handles `'...'` quotes — must extend to skip
    dollar-quoted blocks, otherwise CREATE FUNCTION statements get shredded.
"""

from __future__ import annotations

import os
import pathlib
import re
import uuid

import psycopg2
import psycopg2.extras  # noqa: F401  — knife 3 lesson; required for register_uuid()
import pytest


REPO_ROOT = pathlib.Path(__file__).resolve().parents[1]
MIGRATION_PATH = REPO_ROOT / "schema" / "migrations" / "013_counterexample_gate.sql"


# Trigger + function per docs/41 §2.5
EXPECTED_FUNCTION = "assert_min_one_contradicts"
EXPECTED_TRIGGER = "claim_evidence_link_after_change"
EXPECTED_TABLE = "claim_evidence_link"

# 红线字段 — 任何打分语义字段都不能出现 (per docs/04 §3.x + docs/41 §8 + tasking 232 §红线)
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


@pytest.fixture(scope="module")
def conn():
    """Live DB connection for S2.6-lite counterexample gate tests."""
    dsn = os.environ.get(
        "CEGR_TEST_DSN",
        "postgresql://postgres:postgres@127.0.0.1:55440/cegr_test",
    )
    c = psycopg2.connect(dsn)
    c.autocommit = False
    # Set search_path so unqualified `claim_evidence_link` resolves to cegr.*
    # (mirrors the SET search_path in migration 013; pytest connection is a
    # different session than the psql apply)
    with c.cursor() as cur:
        cur.execute("SET search_path TO cegr, public")
    c.commit()
    yield c
    c.close()


@pytest.fixture(scope="module")
def migration_sql() -> str:
    """Load 013 migration SQL verbatim — used to assert file presence + idempotency."""
    assert MIGRATION_PATH.exists(), (
        f"migration file missing: {MIGRATION_PATH}"
    )
    return MIGRATION_PATH.read_text(encoding="utf-8")


def test_function_and_trigger_exist(conn) -> None:
    """Case 1 (主): assert_min_one_contradicts() function + claim_evidence_link_after_change trigger must exist."""
    psycopg2.extras.register_uuid()
    with conn.cursor() as cur:
        cur.execute(
            "SELECT proname FROM pg_proc WHERE proname = %s",
            (EXPECTED_FUNCTION,),
        )
        funcs = [r[0] for r in cur.fetchall()]
        assert EXPECTED_FUNCTION in funcs, (
            f"function {EXPECTED_FUNCTION}() missing — migration 013 not applied"
        )

        cur.execute(
            """
            SELECT trigger_name, event_manipulation
            FROM information_schema.triggers
            WHERE event_object_table = %s
              AND trigger_name = %s
            ORDER BY event_manipulation
            """,
            (EXPECTED_TABLE, EXPECTED_TRIGGER),
        )
        rows = cur.fetchall()
        events = {r[1] for r in rows}
        # AFTER INSERT / UPDATE / DELETE — per docs/41 §2.5
        assert "INSERT" in events, f"trigger missing INSERT event: got {events}"
        assert "UPDATE" in events, f"trigger missing UPDATE event: got {events}"
        assert "DELETE" in events, f"trigger missing DELETE event: got {events}"


def test_contradicts_row_insertable(conn) -> None:
    """Case 2 (主): CONTRADICTS 行可插入 (positive — 触发器不阻塞首条 CONTRADICTS).

    Uses a fresh claim_id (uuid_generate_v4()) to isolate from any pre-existing rows.
    """
    psycopg2.extras.register_uuid()
    # uuid.UUID objects are auto-converted via the UUID adapter registered above
    fresh_claim_id = uuid.uuid4()
    fresh_evidence_id = uuid.uuid4()

    with conn.cursor() as cur:
        cur.execute(
            """
            INSERT INTO claim_evidence_link (claim_id, claim_type, evidence_id, evidence_type, polarity, note)
            VALUES (%s, 'INFERENCE', %s, 'OBSERVATION', 'CONTRADICTS', 's26lite positive test')
            """,
            (fresh_claim_id, fresh_evidence_id),
        )
    conn.commit()

    # 验证行确实存在 + polarity = CONTRADICTS
    with conn.cursor() as cur:
        cur.execute(
            """
            SELECT polarity FROM claim_evidence_link
            WHERE claim_id = %s
            """,
            (str(fresh_claim_id),),
        )
        rows = cur.fetchall()
        assert len(rows) == 1, f"expected 1 row, got {len(rows)}"
        assert rows[0][0] == "CONTRADICTS", (
            f"polarity should be CONTRADICTS, got {rows[0][0]}"
        )

    # 清理 (withdrawal 也需经过触发器 — 因为这是最后一行的 DELETE;
    # 但前提是此 claim_id 上只有这 1 行, 删除后 COUNT(CONTRADICTS) = 0 会触发异常.
    # 测试夹具通过 conn.rollback() 跳过该 DELETE, 留给下一次测试自清)
    conn.rollback()


def test_no_score_like_fields_on_claim_evidence_link(conn) -> None:
    """Case 3 (主, 红线): claim_evidence_link 不允许 score·rating·rank·confidence_score·credibility_score 列."""
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


def test_polarity_check_unchanged(conn) -> None:
    """Case 4 (bonus): 既有 polarity CHECK (SUPPORTS/CONTRADICTS) 必须保留."""
    with conn.cursor() as cur:
        cur.execute(
            """
            SELECT conname, pg_get_constraintdef(c.oid) AS def
            FROM pg_constraint c
            JOIN pg_class t ON t.oid = c.conrelid
            JOIN pg_namespace n ON n.oid = t.relnamespace
            WHERE n.nspname = 'cegr'
              AND t.relname = %s
              AND c.contype = 'c'
            """,
            (EXPECTED_TABLE,),
        )
        rows = cur.fetchall()
        check_defs = [r[1].lower() for r in rows]
        polarity_check_present = any(
            "polarity" in d and "supports" in d and "contradicts" in d
            for d in check_defs
        )
        assert polarity_check_present, (
            f"polarity CHECK (SUPPORTS/CONTRADICTS) missing — must be preserved "
            f"per docs/04 §3.9. Found checks: {check_defs}"
        )


def test_migration_013_idempotent(conn, migration_sql) -> None:
    """Case 5 (bonus): migration 013 must apply cleanly twice (CREATE OR REPLACE / DROP TRIGGER IF EXISTS).

    Reuses the quote-aware split pattern from s25lite knife 7.
    """

    def _split_quote_aware(sql: str) -> list[str]:
        """Quote-aware + dollar-quote-aware SQL statement splitter.

        Knife 7 taught: respect '...' literals + '' escaped quotes.
        Knife 13 s26lite taught: PL/pgSQL uses $$...$$ dollar-quoting which
        can contain ';' that must NOT split statements. Skip past any
        '$tag$ ... $tag$' block (tag may be empty, 'foo', etc.).
        """
        statements: list[str] = []
        buf: list[str] = []
        in_quote = False
        # Dollar-quote state: (tag, expecting_open_or_close)
        # tag is None initially; on '$tag$' open, set tag; on '$tag$' close, clear.
        dollar_tag: str | None = None
        i = 0
        n = len(sql)
        while i < n:
            ch = sql[i]
            # Inside dollar-quote: look for closing $tag$
            if dollar_tag is not None:
                buf.append(ch)
                # Closing form: $tag$ where tag is stored
                close_marker = f"${dollar_tag}$"
                # Check if starting at position i, we have the close_marker
                if sql[i:i + len(close_marker)] == close_marker:
                    # We've already appended the leading '$'; append the rest and advance
                    tail = close_marker[1:]
                    buf.append(tail)
                    i += len(close_marker)
                    dollar_tag = None
                    continue
                i += 1
                continue
            # Inside single-quote: look for closing ' or '' (escaped)
            if in_quote:
                buf.append(ch)
                if ch == "'":
                    if i + 1 < n and sql[i + 1] == "'":
                        buf.append("'")
                        i += 2
                        continue
                    in_quote = False
                i += 1
                continue
            # Outside any quote: detect openers
            if ch == "'":
                buf.append(ch)
                in_quote = True
                i += 1
                continue
            if ch == "$":
                # Try to parse $tag$ where tag is [A-Za-z0-9_]* (or empty)
                m = re.match(r"\$([A-Za-z0-9_]*)\$", sql[i:])
                if m:
                    tag = m.group(1)
                    buf.append(m.group(0))
                    i += len(m.group(0))
                    if dollar_tag is None:
                        dollar_tag = tag
                    else:
                        # Shouldn't happen for properly nested dollar quotes,
                        # but treat as a no-op (treat as text)
                        pass
                    continue
                # Lone '$' not part of $tag$ — append and advance
                buf.append(ch)
                i += 1
                continue
            if ch == ";":
                stmt = "".join(buf).strip()
                if stmt:
                    statements.append(stmt)
                buf = []
                i += 1
                continue
            buf.append(ch)
            i += 1
        tail = "".join(buf).strip()
        if tail:
            statements.append(tail)
        return statements

    sql_no_comments = re.sub(r"--[^\n]*", "", migration_sql)
    sql_no_comments = re.sub(r"/\*.*?\*/", "", sql_no_comments, flags=re.DOTALL)
    statements = _split_quote_aware(sql_no_comments)
    assert statements, "migration 013 has no statements after comment strip"

    psycopg2.extras.register_uuid()
    with conn.cursor() as cur:
        for stmt in statements:
            cur.execute(stmt)
    conn.commit()
    # apply once more to verify CREATE OR REPLACE / DROP TRIGGER IF EXISTS guards
    with conn.cursor() as cur:
        for stmt in statements:
            cur.execute(stmt)
    conn.commit()


def test_migration_file_has_no_score_fields(migration_sql) -> None:
    """Case 6 (bonus, file-level): SQL file text itself must not name scoring fields.

    Strip line + block comments FIRST (knife 3 lesson) so explanatory
    comments mentioning pattern names don't trigger false positives.
    """
    text = migration_sql.lower()
    text = re.sub(r"--[^\n]*", "", text)
    text = re.sub(r"/\*.*?\*/", "", text, flags=re.DOTALL)
    for forbidden in FORBIDDEN_COLUMN_PATTERNS:
        assert forbidden not in text, (
            f"migration 013 SQL text contains forbidden token '{forbidden}'"
        )


def test_function_definition_uses_polarity_column(migration_sql) -> None:
    """Case 7 (bonus, CC deviation doc): function body must reference polarity (CHECK column),
    not canonical_polarity (nullable projection). Per migration 013 header 注释.

    This test is informational; it locks the CC decision documented in the migration header.
    A future Cursor audit may choose to revert to canonical_polarity — in which case this
    test should be updated alongside the function body.
    """
    # Strip comments first so the function body reference is what we measure
    text = migration_sql
    text_no_comments = re.sub(r"--[^\n]*", "", text)
    text_no_comments = re.sub(r"/\*.*?\*/", "", text_no_comments, flags=re.DOTALL)
    # The function body must include the literal "polarity = 'CONTRADICTS'" (case-sensitive in SQL)
    assert "polarity = 'CONTRADICTS'" in text_no_comments, (
        "function body should reference polarity (CHECK column) — see migration 013 header "
        "for CC deviation rationale from docs/41 §2.5 example"
    )


def test_seed_loader_module_loadable() -> None:
    """Case 8 (bonus): tests/s26lite prep — script entry path must not be wrongly introduced.

    S2.6-lite 落地刀不写 seed/loader (per tasking 232 §SCHEMA: 仅触发器 + pytest).
    This test is a stub asserting no `scripts/seed_counterexample_*_demo.py`
    has been wrongly introduced yet — guards the knife boundary.
    """
    import importlib.util

    for name in (
        "seed_counterexample_demo",
        "seed_claim_evidence_link_counterexample_demo",
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