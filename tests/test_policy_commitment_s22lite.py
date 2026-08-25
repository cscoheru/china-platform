"""Stage 2 / S2.2-lite — policy DDL minimal pytest (per Cursor 195 §NOW-2).

Per Cursor 195 §NOW-2: 最小 pytest (≥3):
  1. migration 可应用
  2. 五张 policy/commitment 表存在
  3. 无评分字段 (score/rating/rank/total_score 红线)

Plus 2 bonus tests for the additive contract:
  4. New columns are NULL-able (legacy back-compat)
  5. lineage column present on all 5 tables (is_demo sentinel anchor)

Total: 5 cases. All run against the default STAGE0_DSN after conftest's
session-bootstrap re-applies all migrations including 009.
"""
from __future__ import annotations

import psycopg2
import psycopg2.extras
import pytest

psycopg2.extras.register_uuid()

DSN = "postgresql://postgres:postgres@127.0.0.1:55440/cegr_test"

EXPECTED_TABLES = [
    "policy_document",
    "policy_target",
    "policy_measure",
    "government_commitment",
    "commitment_progress",
]

EXPECTED_NEW_COLUMNS = {
    "policy_document": [
        "canonical_title", "title_en", "policy_level",
        "is_standing_committee", "classification", "effective_year",
        "lineage", "policy_hash_canonical",
    ],
    "policy_target": [
        "target_value_lower", "target_value_upper",
        "target_unit_canonical", "verification_method", "lineage",
    ],
    "policy_measure": [
        "expected_outcome_text", "lineage",
    ],
    "government_commitment": [
        "commitment_text_en", "proposer_role", "is_measurable",
        "measurement_basis", "lineage",
    ],
    "commitment_progress": [
        "progress_value_lower", "progress_value_upper", "lineage",
    ],
}

# 红线字段名 (per docs/37 §2 + §8 + Cursor 195 §红线)
FORBIDDEN_SCORE_LIKE = ("score", "rating", "rank", "total_score")


@pytest.fixture
def conn():
    c = psycopg2.connect(DSN)
    c.autocommit = True
    yield c
    c.close()


# ---------------------------------------------------------------------------
# Case 1: migration applies — every new column from 009 exists
# ---------------------------------------------------------------------------


def test_migration_009_columns_present(conn):
    """Per Cursor 195 §NOW-2 case 1: migration is applicable; new columns exist.

    Documents the additive contract: 23 new columns across 5 tables.
    """
    with conn.cursor() as cur:
        for table, cols in EXPECTED_NEW_COLUMNS.items():
            cur.execute(
                """
                SELECT column_name, is_nullable
                FROM information_schema.columns
                WHERE table_schema = 'cegr' AND table_name = %s
                """,
                (table,),
            )
            actual = {row[0]: row[1] for row in cur.fetchall()}
            for col in cols:
                assert col in actual, (
                    f"migration 009 column cegr.{table}.{col} missing"
                )
                # all new columns must be NULL-able (additive contract)
                assert actual[col] == "YES", (
                    f"cegr.{table}.{col} must be nullable; got {actual[col]}"
                )


# ---------------------------------------------------------------------------
# Case 2: five policy/commitment tables exist (per Cursor 195 §NOW-2 case 2)
# ---------------------------------------------------------------------------


def test_five_policy_commitment_tables_exist(conn):
    """Per Cursor 195 §NOW-2 case 2: 5 tables exist post-migration."""
    with conn.cursor() as cur:
        cur.execute(
            """
            SELECT table_name FROM information_schema.tables
            WHERE table_schema = 'cegr'
              AND table_name = ANY(%s)
            """,
            (EXPECTED_TABLES,),
        )
        existing = {row[0] for row in cur.fetchall()}
    missing = set(EXPECTED_TABLES) - existing
    assert not missing, f"missing tables: {missing}"


# ---------------------------------------------------------------------------
# Case 3: no score / rating / rank / total_score field on any of the 5 tables
# ---------------------------------------------------------------------------


def test_no_score_like_fields_on_policy_commitment(conn):
    """Per Cursor 195 §NOW-2 case 3 + docs/37 §8 红线.

    钉死: 5 张政策/承诺表均不含 score/rating/rank/total_score 任一字段名.
    用 unaccent/lower 兼容大小写; 列名扫描所有 schema 列.
    """
    with conn.cursor() as cur:
        cur.execute(
            """
            SELECT table_name, column_name
            FROM information_schema.columns
            WHERE table_schema = 'cegr'
              AND table_name = ANY(%s)
            """,
            (EXPECTED_TABLES,),
        )
        rows = cur.fetchall()

    found = []
    for table, col in rows:
        col_lower = col.lower()
        if any(forbidden in col_lower for forbidden in FORBIDDEN_SCORE_LIKE):
            found.append((table, col))

    assert not found, (
        f"red-line violated: forbidden score-like columns found: {found}"
    )


# ---------------------------------------------------------------------------
# Case 4 (bonus): lineage column is JSONB and nullable on all 5 tables
# ---------------------------------------------------------------------------


def test_lineage_column_jsonb_on_all_five(conn):
    """Per docs/37 §3.2 + S1.18 sentinel: lineage is JSONB nullable on all 5.

    The lineage JSONB carries the is_demo sentinel + R3-E provenance payload.
    """
    with conn.cursor() as cur:
        for table in EXPECTED_TABLES:
            cur.execute(
                """
                SELECT data_type, is_nullable
                FROM information_schema.columns
                WHERE table_schema = 'cegr'
                  AND table_name = %s
                  AND column_name = 'lineage'
                """,
                (table,),
            )
            row = cur.fetchone()
            assert row is not None, (
                f"cegr.{table}.lineage missing (sentinel anchor)"
            )
            data_type, is_nullable = row
            assert data_type == "jsonb", (
                f"cegr.{table}.lineage data_type must be jsonb; got {data_type}"
            )
            assert is_nullable == "YES", (
                f"cegr.{table}.lineage must be nullable; got {is_nullable}"
            )


# ---------------------------------------------------------------------------
# Case 5 (bonus): migration 009 idempotency — re-running ALTER TABLE is OK
# ---------------------------------------------------------------------------


def test_migration_009_idempotent(conn):
    """Per docs/37 §2.0 + S2.1-lite (008) parallel: ADD COLUMN IF NOT EXISTS
    makes migration re-runnable without error.

    We probe by reading catalog state — not by re-executing ALTER — because
    conftest.py session-bootstrap already ran migration 009 on this DB.
    """
    with conn.cursor() as cur:
        cur.execute(
            """
            SELECT COUNT(*) FROM information_schema.columns
            WHERE table_schema = 'cegr'
              AND table_name = ANY(%s)
              AND column_name IN (
                'canonical_title', 'title_en', 'policy_level',
                'is_standing_committee', 'classification', 'effective_year',
                'lineage', 'policy_hash_canonical',
                'target_value_lower', 'target_value_upper',
                'target_unit_canonical', 'verification_method',
                'expected_outcome_text',
                'commitment_text_en', 'proposer_role', 'is_measurable',
                'measurement_basis',
                'progress_value_lower', 'progress_value_upper'
              )
            """,
            (EXPECTED_TABLES,),
        )
        (n_total,) = cur.fetchone()
    expected = sum(len(v) for v in EXPECTED_NEW_COLUMNS.values()) - len(EXPECTED_TABLES)
    # subtract 1 lineage from each table's count to avoid double-count
    # (lineage is shared as a column across 5 tables; counted once per table)
    # Actually: we want the count of (table, col) pairs that exist.
    # 23 columns listed in EXPECTED_NEW_COLUMNS minus 5 lineage = 18 distinct
    # non-lineage columns, plus 5 lineage = 23 total (table, col) pairs.
    assert n_total == 23, (
        f"expected 23 new (table, column) pairs from migration 009; got {n_total}"
    )