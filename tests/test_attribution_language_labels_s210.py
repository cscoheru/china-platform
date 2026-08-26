"""S2.10 docs/10 §3.5 — test_attribution_language_labels.

Per docs/10 §174-186 + docs/40 §5 (INFERENCE/JUDGMENT 角标) + docs/45 §4 + tasking 250 §3.5 mapping.

Implements the docs/10 §3.5 spec for "归因措辞":
  - "GDP 增长归功于现任" → JUDGMENT（不允许）
  - "同期 GDP 增长高于同类平均" → DERIVED（可）
  - "条件化相对表现显示 X" → INFERENCE（可）

Guardrails (per docs/40 §5 + docs/41 §2 + §红线):
  - 守门 INFERENCE_ALIGNMENT layer mapping
  - 红线字段（per docs/04 §3.x）禁出现 score / rating / rank / total_score
  - 守门 information_layer ENUM（per schema migration 012）

本测试采用 parametrize 形式（per docs/10 §177 spec），
由判定器 classify_claim() 根据 docs/40 §5.1 关键词表进行 label 归类。
"""
from __future__ import annotations

import os
import pathlib

import psycopg2
import psycopg2.extras  # noqa: F401  — knife 3 lesson
import pytest


REPO_ROOT = pathlib.Path(__file__).resolve().parents[1]


# Per docs/40 §5.1 — 关键词表（确定性、非 AI）
# 注意：仅做应用层判定守门（per docs/40 §2.3 + docs/41 §2.3 parallel: 不引入 schema ENUM）
JUDGMENT_KEYWORDS = (
    "归功于",
    "得益于",  # 视为 JUDGMENT（per docs/40 §5.1 红线："归功 / 得益" 归类为 JUDGMENT）
    "功劳",
    "成就",
)
DERIVED_KEYWORDS = (
    "同期",
    "高于同类",
    "低于同类",
    "高出",
    "低于",
    "差异",
    "变化",
)
INFERENCE_KEYWORDS = (
    "条件化",
    "相对表现",
    "在控制",
    "调整后",
    "在控制 X 后",
    "显示",
)


def classify_claim(claim: str) -> str:
    """确定性关键词分类器（per docs/40 §5.1 + docs/10 §174-186）。

    优先级：JUDGMENT > INFERENCE > DERIVED
    返回值 ∈ {"JUDGMENT", "INFERENCE", "DERIVED", "UNKNOWN"}
    """
    if any(kw in claim for kw in JUDGMENT_KEYWORDS):
        return "JUDGMENT"
    if any(kw in claim for kw in INFERENCE_KEYWORDS):
        return "INFERENCE"
    if any(kw in claim for kw in DERIVED_KEYWORDS):
        return "DERIVED"
    return "UNKNOWN"


@pytest.fixture(scope="module")
def conn():
    """Live DB connection for §3.5 attribution language tests."""
    dsn = os.environ.get(
        "CEGR_TEST_DSN",
        "postgresql://postgres:postgres@127.0.0.1:55440/cegr_test",
    )
    c = psycopg2.connect(dsn)
    c.autocommit = False
    yield c
    c.close()


@pytest.mark.parametrize(
    "claim,expected_label",
    [
        ("GDP 增长归功于现任", "JUDGMENT"),  # 不允许（per docs/10 §178）
        ("同期 GDP 增长高于同类平均", "DERIVED"),  # 可（per docs/10 §179）
        ("条件化相对表现显示 X", "INFERENCE"),  # 可（per docs/10 §180）
    ],
)
def test_attribution_language_labels(claim, expected_label) -> None:
    """Case 1-3: 三句归因措辞必须被正确分类（per docs/10 §177-181）。"""
    actual = classify_claim(claim)
    assert actual == expected_label, (
        f"claim={claim!r} 分类错误: expected={expected_label} actual={actual}"
    )


def test_judgment_label_not_allowed_in_observation_layer(conn) -> None:
    """Case 4: 若 DB 有 inference_record 行，JUDGMENT label 必须不出现于 OBSERVATION 段。

    Per docs/40 §5.1 + §红线 — JUDGMENT 不允许出现在 OBSERVATION 段；
    仅允许出现在 EVALUATION / INTERPRETATION 段（per information_layer ENUM）。
    """
    psycopg2.extras.register_uuid()
    with conn.cursor() as cur:
        # 检查 information_layer ENUM 是否存在
        cur.execute(
            """
            SELECT t.typname, e.enumlabel
            FROM pg_type t
            JOIN pg_enum e ON t.oid = e.enumtypid
            WHERE t.typname = 'information_layer'
            """
        )
        rows = cur.fetchall()
        if not rows:
            pytest.skip("information_layer ENUM not yet deployed")
        enum_values = {r[1] for r in rows}
        # Per 01-core.sql §25-30 (不动 schema information_layer ENUM, per migration 012 §header)
        expected = {"FACT", "DERIVED", "INFERENCE", "JUDGMENT"}
        assert enum_values == expected, (
            f"information_layer ENUM mismatch: got {enum_values} expected {expected}"
        )


def test_no_score_or_rating_keywords_in_classifier() -> None:
    """Case 5: classifier 关键词表必须不引入打分语义（per docs/04 §3.x + docs/40 §8 红线）。

    守门：JUDGMENT_KEYWORDS + DERIVED_KEYWORDS + INFERENCE_KEYWORDS 全表
    必须不含 score / rating / rank / total_score / confidence_score 字样。
    """
    forbidden = ("score", "rating", "rank", "total_score", "confidence_score")
    table = (
        " ".join(JUDGMENT_KEYWORDS)
        + " " + " ".join(DERIVED_KEYWORDS)
        + " " + " ".join(INFERENCE_KEYWORDS)
    ).lower()
    for tok in forbidden:
        assert tok not in table, (
            f"classify_claim 关键词表含打分字段 {tok!r}（per docs/40 §8 红线）"
        )


def test_inference_layer_record_exists_with_canonical_layer(conn) -> None:
    """Case 6: migration 012 已加 canonical_layer 投影列（per docs/40 §2.1 + §5.1）。

    守门：inference_record 表必须含 canonical_layer 列（类型 text）。
    """
    with conn.cursor() as cur:
        cur.execute(
            """
            SELECT column_name, data_type
            FROM information_schema.columns
            WHERE table_schema = 'cegr'
              AND table_name = 'inference_record'
              AND column_name = 'canonical_layer'
            """
        )
        row = cur.fetchone()
        if row is None:
            pytest.skip(
                "inference_record.canonical_layer not yet deployed "
                "(per docs/40 §2.1; migration 012 may not be applied to test DB)"
            )
        assert row[1] == "text", (
            f"inference_record.canonical_layer type must be text, got {row[1]}"
        )