"""Stage 2 / S2.7-b-full-demo-join — dbt mart SQL demo-join guard test.

Per docs/47 §3.1 + §3.2 + tasking 293 (S2.7-b-full mart demo-join).

This test evolves the S2.7-b-full mart skeleton (`288`) into the
demo-join (`293`): both mart views now emit **demo rows** (60 evidence_chain
+ 70 seven_dim_overview = 130 rows total) instead of `WHERE FALSE`.

Red lines (per docs/47 §1.2 + `293` §红线 + docs/34 §1 + docs/06 §6.6 + docs/42 §8):
  - dbt mart view demo-join must exist (mart_city_evidence_chain + mart_city_seven_dim_overview)
  - column contracts must align with docs/47 §3.1 / §3.2
  - no score / rating / rank / total_score / confidence_score / credibility_score
    / peer_rank columns anywhere in the SQL
  - lineage.source_file_sha256 MUST remain the '0'.repeat(64) / REPEAT('0', 64)
    placeholder (NO real SHA fabrication under any pretext)
  - all emitted rows must carry lineage_is_demo = 'true' (or is_demo = 'true'
    for the seven_dim mart) — demo-join may NOT leak real rows
  - 10 cities must be enumerated (per docs/46 §2): nanjing / suzhou / wuxi /
    nantong / hangzhou / ningbo / wenzhou / guangzhou / shenzhen / dongguan
  - 6 segments enumerated (per docs/06 §2): CONDITION / COMMITMENT / INPUT /
    PROCESS / OUTPUT / OUTCOME_RISK
  - 7 dimensions enumerated (per docs/42 §2.4): POLICY_DELIVERY /
    FISCAL_EXECUTION / PROJECT_DELIVERY / ECONOMIC_ADAPTATION /
    PUBLIC_SERVICES / RISK_MANAGEMENT / GOAL_CONSISTENCY
  - 5 balance_status enum (per docs/42 §2.5): NO_EVIDENCE /
    NO_CONTRADICTING_EVIDENCE / NO_SUPPORTING_EVIDENCE / SUPPORTS_DOMINANT /
    CONTRADICTS_DOMINANT
  - the SQL must NOT contain `WHERE FALSE` (skeleton mode is over)
  - do not commit dbt project.yml / sources.yml changes in this knife
"""
from __future__ import annotations

import re
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

# 10 城锁定清单（per docs/46 §2 江苏 4 + 浙江 3 + 广东 3）
EXPECTED_CITY_SLUGS = [
    "nanjing",
    "suzhou",
    "wuxi",
    "nantong",
    "hangzhou",
    "ningbo",
    "wenzhou",
    "guangzhou",
    "shenzhen",
    "dongguan",
]

# 6 段（per docs/06 §2 evidence chain）
EXPECTED_SEGMENTS = [
    "CONDITION",
    "COMMITMENT",
    "INPUT",
    "PROCESS",
    "OUTPUT",
    "OUTCOME_RISK",
]

# 7 维度（per docs/42 §2.4）
EXPECTED_SEVEN_DIM_CARDS = [
    "POLICY_DELIVERY",
    "FISCAL_EXECUTION",
    "PROJECT_DELIVERY",
    "ECONOMIC_ADAPTATION",
    "PUBLIC_SERVICES",
    "RISK_MANAGEMENT",
    "GOAL_CONSISTENCY",
]

# 5 balance_status 枚举（per docs/42 §2.5）
EXPECTED_BALANCE_STATUS = [
    "NO_EVIDENCE",
    "NO_CONTRADICTING_EVIDENCE",
    "NO_SUPPORTING_EVIDENCE",
    "SUPPORTS_DOMINANT",
    "CONTRADICTS_DOMINANT",
]


def _strip_sql_comments(src: str) -> str:
    """Strip SQL line + block comments per AGENTS.md 守门."""
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
    """Negative-context regex scan for forbidden scoring columns."""
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
        f"missing: {MART_EVIDENCE_CHAIN_PATH} (per docs/47 §3.1 + 293 §SCHEMA)"
    )


def test_mart_seven_dim_overview_file_exists() -> None:
    assert MART_SEVEN_DIM_OVERVIEW_PATH.is_file(), (
        f"missing: {MART_SEVEN_DIM_OVERVIEW_PATH} (per docs/47 §3.2 + 293 §SCHEMA)"
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
        f"(per docs/47 §3.1 + 293 §SCHEMA)"
    )


def test_mart_evidence_chain_sha_is_zero_placeholder() -> None:
    """lineage.source_file_sha256 必须为 '0'*64 占位；不得伪造非零 SHA。"""
    src = MART_EVIDENCE_CHAIN_PATH.read_text(encoding="utf-8")
    clean = _strip_sql_comments(src)
    assert (
        "REPEAT('0', 64)" in clean
        or "repeat('0', 64)" in clean.lower()
    ), (
        "mart_city_evidence_chain.sql: lineage_source_file_sha256 必须 = '0'*64 占位 "
        "(per docs/47 §3.1 ⚠️ OPEN + 293 §红线)"
    )


def test_mart_evidence_chain_no_where_false() -> None:
    """Demo-join must NOT have WHERE FALSE (skeleton mode is over)."""
    src = MART_EVIDENCE_CHAIN_PATH.read_text(encoding="utf-8")
    clean = _strip_sql_comments(src)
    assert "WHERE FALSE" not in clean, (
        "mart_city_evidence_chain.sql: 残留 WHERE FALSE 守门 "
        "(demo-join 已激活；per 293 §SCHEMA + §红线)"
    )


def test_mart_evidence_chain_emits_demo_rows() -> None:
    """Demo-join must enumerate all 10 cities × 6 segments = 60 rows.

    Cross-product structure must be visible (10 cities × 6 segments VALUES
    joined via CROSS JOIN). Standalone VALUES without CROSS JOIN would emit
    fewer rows and fail this check.
    """
    src = MART_EVIDENCE_CHAIN_PATH.read_text(encoding="utf-8")
    clean = _strip_sql_comments(src)
    # 10 城必须枚举（per docs/46 §2 锁定清单）
    for slug in EXPECTED_CITY_SLUGS:
        assert f"'{slug}'" in clean, (
            f"mart_city_evidence_chain.sql: 10 城清单缺 '{slug}' "
            f"(per docs/46 §2 + 293 §SCHEMA)"
        )
    # 6 段必须枚举（per docs/06 §2）
    for seg in EXPECTED_SEGMENTS:
        assert f"'{seg}'" in clean, (
            f"mart_city_evidence_chain.sql: 6 段清单缺 '{seg}' "
            f"(per docs/06 §2)"
        )
    # 必须用 CROSS JOIN 产生 10×6=60 行
    assert "CROSS JOIN" in clean, (
        "mart_city_evidence_chain.sql: 缺 CROSS JOIN 守门 "
        "(demo-join 须 10×6=60 行；per 293 §SCHEMA)"
    )


def test_mart_evidence_chain_lineage_is_demo_true() -> None:
    """All emitted rows must carry lineage_is_demo = 'true'."""
    src = MART_EVIDENCE_CHAIN_PATH.read_text(encoding="utf-8")
    clean = _strip_sql_comments(src)
    assert "'true'" in clean and "lineage_is_demo" in clean, (
        "mart_city_evidence_chain.sql: lineage_is_demo 必须 = 'true' "
        "(per S1.18 sentinel + 293 §红线)"
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
        f"(per docs/47 §3.2 + 293 §SCHEMA)"
    )


def test_mart_seven_dim_overview_no_where_false() -> None:
    src = MART_SEVEN_DIM_OVERVIEW_PATH.read_text(encoding="utf-8")
    clean = _strip_sql_comments(src)
    assert "WHERE FALSE" not in clean, (
        "mart_city_seven_dim_overview.sql: 残留 WHERE FALSE 守门 "
        "(demo-join 已激活；per 293 §SCHEMA + §红线)"
    )


def test_mart_seven_dim_overview_emits_demo_rows() -> None:
    """Demo-join must enumerate all 10 cities × 7 cards = 70 rows."""
    src = MART_SEVEN_DIM_OVERVIEW_PATH.read_text(encoding="utf-8")
    clean = _strip_sql_comments(src)
    for slug in EXPECTED_CITY_SLUGS:
        assert f"'{slug}'" in clean, (
            f"mart_city_seven_dim_overview.sql: 10 城清单缺 '{slug}' "
            f"(per docs/46 §2)"
        )
    for card in EXPECTED_SEVEN_DIM_CARDS:
        assert f"'{card}'" in clean, (
            f"mart_city_seven_dim_overview.sql: 7 维度清单缺 '{card}' "
            f"(per docs/42 §2.4)"
        )
    assert "CROSS JOIN" in clean, (
        "mart_city_seven_dim_overview.sql: 缺 CROSS JOIN 守门 "
        "(demo-join 须 10×7=70 行；per 293 §SCHEMA)"
    )


def test_mart_seven_dim_overview_is_demo_true() -> None:
    """All emitted rows must carry is_demo = 'true'."""
    src = MART_SEVEN_DIM_OVERVIEW_PATH.read_text(encoding="utf-8")
    clean = _strip_sql_comments(src)
    assert "'true'" in clean and "is_demo" in clean, (
        "mart_city_seven_dim_overview.sql: is_demo 必须 = 'true' "
        "(per S1.18 sentinel + 293 §红线)"
    )


def test_mart_seven_dim_overview_no_forbidden_tokens() -> None:
    src = MART_SEVEN_DIM_OVERVIEW_PATH.read_text(encoding="utf-8")
    clean = _strip_sql_comments(src)
    _assert_no_forbidden_columns(clean, "mart_city_seven_dim_overview.sql")


# ===== 4. 应用层 enum 守门（per docs/42 §2.5） =====

def test_mart_seven_dim_overview_lists_5_balance_status_values() -> None:
    """balance_status 5 枚举应在注释/字段定义中明示。"""
    src = MART_SEVEN_DIM_OVERVIEW_PATH.read_text(encoding="utf-8")
    expected = EXPECTED_BALANCE_STATUS
    missing = [v for v in expected if v not in src]
    assert not missing, (
        f"mart_city_seven_dim_overview.sql: 注释/字段定义缺 5 枚举值: {missing} "
        f"(per docs/42 §2.5)"
    )


# ===== 5. 应用层 info_layer / polarity / strength enum 守门 =====

def test_mart_evidence_chain_lists_info_layer_enum() -> None:
    """info_layer 4 枚举应在字段定义中明示 (FACT / DERIVED / INFERENCE / JUDGMENT)."""
    src = MART_EVIDENCE_CHAIN_PATH.read_text(encoding="utf-8")
    expected = ["FACT", "DERIVED", "INFERENCE", "JUDGMENT"]
    missing = [v for v in expected if v not in src]
    assert not missing, (
        f"mart_city_evidence_chain.sql: info_layer 4 枚举缺: {missing} "
        f"(per docs/40 §2.3)"
    )


def test_mart_evidence_chain_lists_polarity_enum() -> None:
    """canonical_polarity 2-3 枚举应在字段定义中明示."""
    src = MART_EVIDENCE_CHAIN_PATH.read_text(encoding="utf-8")
    # 必须至少有 SUPPORTS / NEUTRAL；CONTRADICTS 也应有
    expected = ["SUPPORTS", "NEUTRAL"]
    missing = [v for v in expected if v not in src]
    assert not missing, (
        f"mart_city_evidence_chain.sql: polarity 缺: {missing} "
        f"(per docs/40 §2.3)"
    )


def test_mart_evidence_chain_lists_strength_enum() -> None:
    """evidence_strength 3 枚举应在字段定义中明示 (STRONG / MODERATE / WEAK)."""
    src = MART_EVIDENCE_CHAIN_PATH.read_text(encoding="utf-8")
    expected = ["STRONG", "MODERATE", "WEAK"]
    missing = [v for v in expected if v not in src]
    assert not missing, (
        f"mart_city_evidence_chain.sql: evidence_strength 3 枚举缺: {missing} "
        f"(per docs/40 §2.3)"
    )


# ===== 6. 10 城对照（per docs/46 §2） =====

def test_all_10_cities_present_in_both_marts() -> None:
    """Both marts must enumerate all 10 cities (江苏 4 + 浙江 3 + 广东 3)."""
    src1 = MART_EVIDENCE_CHAIN_PATH.read_text(encoding="utf-8")
    src2 = MART_SEVEN_DIM_OVERVIEW_PATH.read_text(encoding="utf-8")
    for slug in EXPECTED_CITY_SLUGS:
        assert f"'{slug}'" in src1, f"mart_city_evidence_chain.sql 缺 '{slug}'"
        assert f"'{slug}'" in src2, f"mart_city_seven_dim_overview.sql 缺 '{slug}'"


# ===== 7. 计数契约（10 × 6 = 60; 10 × 7 = 70） =====

def test_evidence_chain_cross_join_yields_60_rows() -> None:
    """VALUES 列表长度守门: 10 城 + 6 段 → CROSS JOIN 60 行."""
    src = MART_EVIDENCE_CHAIN_PATH.read_text(encoding="utf-8")
    # 找 city_seed VALUES 段 (10 行)
    city_block = re.search(
        r"city_seed\s+AS\s*\([^)]*VALUES\s*(.*?)\)\s*AS\s*t\(city_slug",
        src,
        re.DOTALL | re.IGNORECASE,
    )
    assert city_block, "未找到 city_seed VALUES 块"
    cities = re.findall(r"\(\s*'([^']+)'", city_block.group(1))
    assert len(cities) == 10, f"city_seed 应有 10 行，实际 {len(cities)}: {cities}"

    seg_block = re.search(
        r"segments\s+AS\s*\([^)]*VALUES\s*(.*?)\)\s*AS\s*t\(segment\)",
        src,
        re.DOTALL | re.IGNORECASE,
    )
    assert seg_block, "未找到 segments VALUES 块"
    segs = re.findall(r"\(\s*'([^']+)'", seg_block.group(1))
    assert len(segs) == 6, f"segments 应有 6 行，实际 {len(segs)}: {segs}"


def test_seven_dim_overview_cross_join_yields_70_rows() -> None:
    """VALUES 列表长度守门: 10 城 + 7 维度 → CROSS JOIN 70 行."""
    src = MART_SEVEN_DIM_OVERVIEW_PATH.read_text(encoding="utf-8")
    city_block = re.search(
        r"city_seed\s+AS\s*\([^)]*VALUES\s*(.*?)\)\s*AS\s*t\(city_slug",
        src,
        re.DOTALL | re.IGNORECASE,
    )
    assert city_block, "未找到 city_seed VALUES 块"
    cities = re.findall(r"\(\s*'([^']+)'", city_block.group(1))
    assert len(cities) == 10, f"city_seed 应有 10 行，实际 {len(cities)}: {cities}"

    dim_block = re.search(
        r"seven_dim\s+AS\s*\([^)]*VALUES\s*(.*?)\)\s*AS\s*t\(card_id",
        src,
        re.DOTALL | re.IGNORECASE,
    )
    assert dim_block, "未找到 seven_dim VALUES 块"
    dims = re.findall(r"\(\s*'([^']+)'", dim_block.group(1))
    assert len(dims) == 7, f"seven_dim 应有 7 行，实际 {len(dims)}: {dims}"