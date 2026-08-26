"""Stage 2 / S2.7-b-full-dbt-skel — dbt mart SQL skeleton guard test.

Per docs/47 §3.1 + §3.2 + tasking 287 (S2.7-b-full dbt mart skeleton).

Red lines (per docs/47 §1.2 + `287` §红线 + docs/34 §1 + docs/06 §6.6 + docs/42 §8):
  - dbt mart view skeleton must exist (mart_city_evidence_chain + mart_city_seven_dim_overview)
  - column contracts must align with docs/47 §3.1 / §3.2
  - no score / rating / rank / total_score / confidence_score / credibility_score
    / peer_rank columns anywhere in the SQL
  - no real SHA fabrication: lineage_source_file_sha256 must be the
    `'0'.repeat(64)` / `REPEAT('0', 64)` placeholder only
  - skeleton emits zero rows (WHERE FALSE) since O1 + Stage 1 OPEN not closed
  - do not commit dbt project.yml / sources.yml changes in this knife
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

MART_EVIDENCE_CHAIN_PATH = ROOT / "dbt" / "models" / "marts" / "mart_city_evidence_chain.sql"
MART_SEVEN_DIM_OVERVIEW_PATH = ROOT / "dbt" / "models" / "marts" / "mart_city_seven_dim_overview.sql"

FORBIDDEN_COLUMN_TOKENS = [
    "score",
    "rating",
    "rank",
    "total_score",
    "confidence_score",
    "credibility_score",
    "peer_rank",
]


def _strip_sql_comments(src: str) -> str:
    """Strip SQL line + block comments per AGENTS.md 守门."""
    # Block comments /* ... */
    src = re.sub(r"/\*[\s\S]*?\*/", "", src)
    out_lines: list[str] = []
    for line in src.splitlines():
        idx = line.find("--")
        if idx >= 0:
            line = line[:idx]
        if line.strip():
            out_lines.append(line)
    return "\n".join(out_lines)


def _assert_no_forbidden_columns(clean_src: str, file_label: str) -> None:
    """Strip FORBIDDEN_* alias declarations first (some files declare
    `AS score`-style guards with literal token names in comments)."""
    for tok in FORBIDDEN_COLUMN_TOKENS:
        pat = re.compile(rf"(?<![A-Za-z0-9_]){re.escape(tok)}(?![A-Za-z0-9_])")
        if pat.search(clean_src):
            raise AssertionError(
                f"FORBIDDEN: {file_label} 含禁词 '{tok}' "
                f"(per docs/06 §6.6 + docs/42 §8 + docs/47 §1.2 红线)"
            )


# ===== 1. File existence =====

def test_mart_evidence_chain_file_exists() -> None:
    assert MART_EVIDENCE_CHAIN_PATH.is_file(), (
        f"missing: {MART_EVIDENCE_CHAIN_PATH} (per docs/47 §3.1 + 287 §SCHEMA)"
    )


def test_mart_seven_dim_overview_file_exists() -> None:
    assert MART_SEVEN_DIM_OVERVIEW_PATH.is_file(), (
        f"missing: {MART_SEVEN_DIM_OVERVIEW_PATH} (per docs/47 §3.2 + 287 §SCHEMA)"
    )


# ===== 2. mart_city_evidence_chain 字段契约 (per docs/47 §3.1) =====

def test_mart_evidence_chain_declares_required_columns() -> None:
    src = MART_EVIDENCE_CHAIN_PATH.read_text(encoding="utf-8")
    clean = _strip_sql_comments(src)
    expected = [
        "city_id",
        "geo_name_zh",
        "province_slug",
        "segment",
        "canonical_statement",
        "canonical_polarity",
        "evidence_strength",
        "info_layer",
        "lineage_is_demo",
        "lineage_source_file_sha256",
    ]
    missing = [c for c in expected if c not in clean]
    assert not missing, (
        f"mart_city_evidence_chain.sql 缺字段: {missing} "
        f"(per docs/47 §3.1 + 287 §SCHEMA)"
    )


def test_mart_evidence_chain_sha_is_zero_placeholder() -> None:
    """lineage.source_file_sha256 必须为 '0'*64 占位；不得伪造非零 SHA。"""
    src = MART_EVIDENCE_CHAIN_PATH.read_text(encoding="utf-8")
    clean = _strip_sql_comments(src)
    # Accept either Postgres REPEAT('0', 64) or the dbt/jinja equivalent.
    assert (
        "REPEAT('0', 64)" in clean
        or "repeat('0', 64)" in clean.lower()
        or "'0' || repeat('0'" in clean.lower()  # defensive: shouldn't match
    ), (
        "mart_city_evidence_chain.sql: lineage_source_file_sha256 必须 = '0'*64 占位 "
        "(per docs/47 §3.1 ⚠️ OPEN + 287 §红线)"
    )


def test_mart_evidence_chain_emits_zero_rows() -> None:
    """Skeleton must emit zero rows (WHERE FALSE) until O1 closes."""
    src = MART_EVIDENCE_CHAIN_PATH.read_text(encoding="utf-8")
    clean = _strip_sql_comments(src)
    assert "WHERE FALSE" in clean, (
        "mart_city_evidence_chain.sql: 缺 WHERE FALSE 守门 "
        "(skeleton 必须 emit 0 行；per docs/47 §6.3 + 287 §红线)"
    )


def test_mart_evidence_chain_no_forbidden_tokens() -> None:
    src = MART_EVIDENCE_CHAIN_PATH.read_text(encoding="utf-8")
    clean = _strip_sql_comments(src)
    _assert_no_forbidden_columns(clean, "mart_city_evidence_chain.sql")


# ===== 3. mart_city_seven_dim_overview 字段契约 (per docs/47 §3.2) =====

def test_mart_seven_dim_overview_declares_required_columns() -> None:
    src = MART_SEVEN_DIM_OVERVIEW_PATH.read_text(encoding="utf-8")
    clean = _strip_sql_comments(src)
    expected = [
        "city_id",
        "card_id",
        "n_supports",
        "n_contradicts",
        "n_inference",
        "n_judgment",
        "n_derived",
        "balance_status",
        "is_demo",
    ]
    missing = [c for c in expected if c not in clean]
    assert not missing, (
        f"mart_city_seven_dim_overview.sql 缺字段: {missing} "
        f"(per docs/47 §3.2 + 287 §SCHEMA)"
    )


def test_mart_seven_dim_overview_emits_zero_rows() -> None:
    """Skeleton must emit zero rows (WHERE FALSE) until O1 closes."""
    src = MART_SEVEN_DIM_OVERVIEW_PATH.read_text(encoding="utf-8")
    clean = _strip_sql_comments(src)
    assert "WHERE FALSE" in clean, (
        "mart_city_seven_dim_overview.sql: 缺 WHERE FALSE 守门 "
        "(skeleton 必须 emit 0 行；per docs/47 §6.3 + 287 §红线)"
    )


def test_mart_seven_dim_overview_no_forbidden_tokens() -> None:
    src = MART_SEVEN_DIM_OVERVIEW_PATH.read_text(encoding="utf-8")
    clean = _strip_sql_comments(src)
    _assert_no_forbidden_columns(clean, "mart_city_seven_dim_overview.sql")


# ===== 4. 应用层 enum 守门（per docs/42 §2.4 + §2.5 + docs/40 §2.3） =====

def test_mart_seven_dim_overview_lists_5_balance_status_values() -> None:
    """balance_status 5 枚举应在注释/文档中明示 (NO_EVIDENCE / SUPPORTS_DOMINANT / ...)"""
    src = MART_SEVEN_DIM_OVERVIEW_PATH.read_text(encoding="utf-8")
    # Comments may legitimately enumerate the 5 values; do NOT strip them
    # for this single check (only check the file's literal text).
    expected = [
        "NO_EVIDENCE",
        "NO_CONTRADICTING_EVIDENCE",
        "NO_SUPPORTING_EVIDENCE",
        "SUPPORTS_DOMINANT",
        "CONTRADICTS_DOMINANT",
    ]
    missing = [v for v in expected if v not in src]
    assert not missing, (
        f"mart_city_seven_dim_overview.sql: 注释/字段定义缺 5 枚举值: {missing} "
        f"(per docs/42 §2.5)"
    )