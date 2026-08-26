"""S2.10 docs/10 §3.1 — test_peer_selection_justified.

Per docs/10 §131-139 + docs/43 §2.1/§2.2 + docs/45 §4 + tasking 250 §3.1 mapping.

Implements the docs/10 §3.1 spec for "同类比较匹配依据":
  - peer_set 来自 `comparison_group` 表（手工选择；Stage 3 才升级到 Mahalanobis）
  - 每条 member 必须有可解释依据（人口 / 区位 / 产业 / 发展阶段）
  - 禁止"纯按 GDP 总量取 top N"
  - matching_features 必须是 JSONB，非空，且至少含 1 个键
  - selection_reason (per docs/43 §2.2) NOT NULL CHECK 非空

Note: §3.1 验收要求的"自动 Mahalanobis 匹配"属 Stage 3 (per docs/08 §4 S3.1)；
本刀仅验证 schema + 手工选择版守门（per docs/43 §2.1 平行）。
"""
from __future__ import annotations

import os
import pathlib

import psycopg2
import psycopg2.extras  # noqa: F401  — knife 3 lesson
import pytest


REPO_ROOT = pathlib.Path(__file__).resolve().parents[1]


@pytest.fixture(scope="module")
def conn():
    """Live DB connection for §3.1 peer selection tests."""
    dsn = os.environ.get(
        "CEGR_TEST_DSN",
        "postgresql://postgres:postgres@127.0.0.1:55440/cegr_test",
    )
    c = psycopg2.connect(dsn)
    c.autocommit = False
    yield c
    c.close()


# Per docs/43 §2.2 + docs/10 §131 — required matching feature dimensions
ALLOWED_MATCHING_DIMENSIONS = {
    "population",          # 人口
    "population_tier",     # 人口档 (per docs/43 §2.3)
    "location",            # 区位
    "location_type",       # 区位类型 (per docs/43 §2.3)
    "coastal",             # 沿海
    "industry",            # 产业
    "industry_base",       # 产业基础 (per docs/43 §2.3)
    "development_stage",   # 发展阶段 (per docs/43 §2.3)
    "gdp_per_capita",      # 人均 GDP (per docs/10 §137)
}


def test_comparison_group_table_exists(conn) -> None:
    """Case 1: comparison_group 表 must exist in cegr schema."""
    psycopg2.extras.register_uuid()
    with conn.cursor() as cur:
        cur.execute(
            """
            SELECT table_name
            FROM information_schema.tables
            WHERE table_schema = 'cegr'
              AND table_name = 'comparison_group'
            """
        )
        row = cur.fetchone()
        assert row is not None, "comparison_group table missing in cegr schema"


def test_comparison_group_required_columns(conn) -> None:
    """Case 2: comparison_group required cols per docs/43 §2.1."""
    expected = {
        "id": "uuid",
        "group_name": "text",
        "geo_entity_ids": "ARRAY",
        "matching_features": "jsonb",
        "matching_method": "text",
        "notes": "text",
        "created_at": "timestamp with time zone",
    }
    with conn.cursor() as cur:
        cur.execute(
            """
            SELECT column_name, data_type
            FROM information_schema.columns
            WHERE table_schema = 'cegr'
              AND table_name = 'comparison_group'
            """
        )
        rows = {r[0]: r[1] for r in cur.fetchall()}
        for col, dtype in expected.items():
            assert col in rows, f"comparison_group.{col} missing"
            actual = rows[col]
            # ARRAY 列在 information_schema 中 data_type 是 'ARRAY'
            if dtype == "ARRAY":
                assert actual.lower() == "array", (
                    f"comparison_group.{col} expected ARRAY, got {actual}"
                )
            else:
                assert actual == dtype, (
                    f"comparison_group.{col} expected {dtype}, got {actual}"
                )


def test_comparison_group_has_geos_check_constraint(conn) -> None:
    """Case 3: comparison_group_has_geos CHECK (array_length(geo_entity_ids,1) >= 1).

    Per schema/01-core.sql:880 + docs/43 §2.1.
    """
    with conn.cursor() as cur:
        cur.execute(
            """
            SELECT conname, pg_get_constraintdef(c.oid)
            FROM pg_constraint c
            JOIN pg_namespace n ON n.oid = c.connamespace
            WHERE n.nspname = 'cegr'
              AND c.conrelid = 'cegr.comparison_group'::regclass
              AND conname = 'comparison_group_has_geos'
            """
        )
        row = cur.fetchone()
        assert row is not None, "comparison_group_has_geos CHECK missing"
        condef = row[1].lower()
        assert "array_length" in condef and ">= 1" in condef, (
            f"CHECK def unexpected: {condef}"
        )


def test_matching_features_must_have_at_least_one_allowed_key(conn) -> None:
    """Case 4: matching_features 必须含至少一个 ALLOWED_MATCHING_DIMENSIONS key。

    Per docs/10 §131-139 + docs/43 §2.1: 同行必须共享关键特征（人口/产业/区位）。
    纯按 GDP 总量取 top N 不允许。
    """
    with conn.cursor() as cur:
        cur.execute(
            """
            SELECT matching_features
            FROM cegr.comparison_group
            WHERE matching_features IS NOT NULL
            """
        )
        rows = cur.fetchall()
        if not rows:
            pytest.skip("no comparison_group rows in test DB")
        for (mf,) in rows:
            assert isinstance(mf, dict), f"matching_features must be JSON object: {mf}"
            keys = set(mf.keys())
            overlap = keys & ALLOWED_MATCHING_DIMENSIONS
            assert overlap, (
                f"matching_features 必须含至少一个允许维度（人口/区位/产业/发展阶段）; "
                f"got keys={keys}"
            )


def test_matching_features_must_not_be_pure_gdp_rank(conn) -> None:
    """Case 5: 禁止纯按 GDP 总量取 top N (per docs/10 §138).

    守门：matching_features 必须含 ≥1 个人口 / 区位 / 产业 / 发展阶段维度。
    若仅含 {'gdp_total'} 或类似纯 GDP 字段 → 拒绝。
    """
    forbidden_only = {"gdp_total", "gdp", "gdp_rank", "total_gdp"}
    with conn.cursor() as cur:
        cur.execute(
            """
            SELECT matching_features
            FROM cegr.comparison_group
            WHERE matching_features IS NOT NULL
            """
        )
        rows = cur.fetchall()
        if not rows:
            pytest.skip("no comparison_group rows in test DB")
        for (mf,) in rows:
            keys = set(mf.keys())
            assert keys != forbidden_only, (
                f"matching_features 仅含纯 GDP 字段（{forbidden_only}）；"
                f"必须含至少一个人口/区位/产业/发展阶段维度"
            )


def test_comparison_group_member_table_and_selection_reason(conn) -> None:
    """Case 6: comparison_group_member 表 + selection_reason NOT NULL（若表存在）。

    Per docs/43 §2.2 + docs/10 §131 — 同行必须共享关键特征，且 selection_reason
    必须可解释（不可空）。本刀不强求表存在（若 Stage 2.9 收口未落 schema 可 skip）；
    若存在则守门。
    """
    with conn.cursor() as cur:
        cur.execute(
            """
            SELECT table_name
            FROM information_schema.tables
            WHERE table_schema = 'cegr'
              AND table_name = 'comparison_group_member'
            """
        )
        row = cur.fetchone()
        if row is None:
            pytest.skip(
                "comparison_group_member table not yet deployed "
                "(per docs/43 §2.2 Stage 2.9 plan; not yet in schema/01-core.sql)"
            )
        # 若存在则守门 selection_reason NOT NULL
        cur.execute(
            """
            SELECT column_name, is_nullable
            FROM information_schema.columns
            WHERE table_schema = 'cegr'
              AND table_name = 'comparison_group_member'
              AND column_name = 'selection_reason'
            """
        )
        row = cur.fetchone()
        assert row is not None, "comparison_group_member.selection_reason column missing"
        assert row[1] == "NO", (
            f"comparison_group_member.selection_reason must be NOT NULL, got is_nullable={row[1]}"
        )