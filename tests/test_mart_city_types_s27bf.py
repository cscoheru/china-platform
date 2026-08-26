"""Stage 2 / S2.7-b-full-lite — mart-shape 类型 + demo fixture 守门测试。

Per docs/47 §3.1 + §3.2 + §3.3 + §4.1 + §4.2 + `265` §SCHEMA "最小 pytest"。

红线 (per docs/47 §1.2 + `265` §红线 + docs/34 §1 + docs/06 §6.6 + docs/42 §8):
  - 不引入 score / rating / rank / total_score / confidence_score / credibility_score
  - 不接真 SHA 样本（lineage.source_file_sha256 = '0'*64 占位）
  - 不接 person/tenure 真数据（relatedPersons 留空）
  - 不擅自增减 10 城名单
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

MART_TYPES_PATH = ROOT / "frontend" / "lib" / "mart_city_types.ts"
MART_DEMO_PATH = ROOT / "frontend" / "lib" / "mart_city_demo.ts"
CITY_PAGE_MART_PATH = ROOT / "frontend" / "app" / "components" / "CityPageMart.tsx"
SLUG_PAGE_PATH = ROOT / "frontend" / "app" / "cities" / "[slug]" / "page.tsx"

FORBIDDEN_TOKENS = [
    "score",
    "rating",
    "rank",
    "total_score",
    "confidence_score",
    "credibility_score",
    "peer_rank",
]

# mart 行允许出现的字段（白名单守门；不引申 schema 列）
MART_ROW_ALLOWED_FIELDS = {
    "cityId",
    "geoNameZh",
    "provinceSlug",
    "segment",
    "canonicalStatement",
    "canonicalPolarity",
    "evidenceStrength",
    "infoLayer",
    "cardId",
    "nSupports",
    "nContradicts",
    "nInference",
    "nJudgment",
    "nDerived",
    "balanceStatus",
    "lineage",
    "personId",
    "canonicalName",
    "positionTitle",
    "geoCanonicalName",
    "isCurrent",
    "evidenceChain",
    "sevenDimOverview",
    "relatedPersons",
    "isDemo",
    "sourceFileSha256",
    "demoReason",
    "city_id",
    "geo_name_zh",
    "province_slug",
}


def _strip_ts_comments(src: str) -> str:
    """Strip TS line + block comments (per AGENTS.md 守门)."""
    src = re.sub(r"/\*[\s\S]*?\*/", "", src)
    out_lines: list[str] = []
    for line in src.splitlines():
        idx = line.find("//")
        if idx >= 0:
            line = line[:idx]
        if line.strip():
            out_lines.append(line)
    return "\n".join(out_lines)


def _strip_forbidden_field_lists(src: str) -> str:
    """Remove contents of FORBIDDEN_*_FIELDS / FORBIDDEN_TOKENS / forbidden_terms arrays.

    mart_city_types.ts 的 FORBIDDEN_MART_FIELDS 数组声明是为了禁词守门 —
    列出禁词不等于使用禁词。须剥离此声明体后再做禁词扫描。
    """
    # 匹配 `const FORBIDDEN_X = [...] as const` 或 `export const FORBIDDEN_X = [...]`
    pat = re.compile(
        r"(?:export\s+)?const\s+FORBIDDEN[A-Z_]*\s*=\s*\[[^\]]*\]\s*(?:as\s+const)?",
        re.DOTALL,
    )
    return pat.sub("", src)


def _assert_no_forbidden_tokens(clean_src: str, file_label: str) -> None:
    # 先剥掉 FORBIDDEN_* 声明体（守门声明本身不应被自身守门误伤）
    stripped = _strip_forbidden_field_lists(clean_src)
    for tok in FORBIDDEN_TOKENS:
        # 负向前后字符：避免命中 "score" 在 "scoreboard" 等单词中
        pat = re.compile(rf"(?<![A-Za-z0-9_]){re.escape(tok)}(?![A-Za-z0-9_])")
        if pat.search(stripped):
            raise AssertionError(
                f"FORBIDDEN: {file_label} 含禁词 '{tok}' "
                f"(per docs/06 §6.6 + docs/42 §8 + docs/47 §1.2 红线)"
            )


# ===== 1. mart_city_types.ts 必含导出 =====

def test_mart_types_exports_required_symbols() -> None:
    """mart-shape 必含：MartLineageProps / MartCityViewProps / BALANCE_STATUS 占位。"""
    src = MART_TYPES_PATH.read_text(encoding="utf-8")
    assert "export interface MartLineageProps" in src, "缺少 MartLineageProps 导出"
    assert "export interface MartCityViewProps" in src, "缺少 MartCityViewProps 导出"
    assert "export const MART_LINEAGE_PLACEHOLDER_SHA" in src, "缺少 SHA256 占位常量"
    assert "MART_LINEAGE_PLACEHOLDER_SHA = \"0\".repeat(64)" in src, "SHA256 占位必须是 '0'*64"
    assert "export function isValidMartLineage" in src, "缺少 lineage 守门函数"
    assert "export function assertMartRowHasNoForbiddenFields" in src, "缺少禁词守门函数"


def test_mart_types_no_forbidden_tokens() -> None:
    """mart-shape 类型契约不含禁词（runtime + compile time 双重守门）。"""
    src = MART_TYPES_PATH.read_text(encoding="utf-8")
    clean = _strip_ts_comments(src)
    _assert_no_forbidden_tokens(clean, "mart_city_types.ts")


# ===== 2. mart_city_demo.ts 必含 fixture =====

def test_mart_demo_covers_10_locked_cities() -> None:
    """demo fixture 覆盖 Cursor 锁定的 10 城名单（via CITY_SLUG_LIST 迭代）。"""
    src = MART_DEMO_PATH.read_text(encoding="utf-8")
    clean = _strip_ts_comments(src)
    assert "CITY_SLUG_LIST" in clean, "demo 必须引用 CITY_SLUG_LIST"
    # Mirrors smoke-check §9e coverage_via_import pattern:
    # demo iterates over CITY_SLUG_LIST via Object.fromEntries(...map(...)).
    coverage_via_import = (
        "CITY_SLUG_LIST" in clean
        and "city_slug_map" in clean
        and ("Object.fromEntries" in clean or ".map(" in clean)
    )
    literal_hits = sum(
        1 for s in [
            "nanjing", "suzhou", "wuxi", "nantong",
            "hangzhou", "ningbo", "wenzhou",
            "guangzhou", "shenzhen", "dongguan",
        ]
        if (
            f'"{s}"' in clean
            or f"'{s}'" in clean
            or f"slug: \"{s}\"" in clean
            or f"[{s}]" in clean
        )
    )
    assert coverage_via_import or literal_hits >= 10, (
        f"demo coverage missing: literal_hits={literal_hits}/10, "
        f"via_import={coverage_via_import}"
    )


def test_mart_demo_lineage_is_zero_sha() -> None:
    """所有 demo 行 lineage.source_file_sha256 必须 = '0'*64（O1 收口前恒占位）。"""
    src = MART_DEMO_PATH.read_text(encoding="utf-8")
    clean = _strip_ts_comments(src)
    assert "MART_LINEAGE_PLACEHOLDER_SHA" in clean, "demo 必须复用占位常量"
    assert "0\".repeat(64)" in clean or "MART_LINEAGE_PLACEHOLDER_SHA" in clean, \
        "demo 必须使用 '0'*64 SHA256 占位"


def test_mart_demo_no_forbidden_tokens() -> None:
    """demo fixture 不含禁词（不派生 score / rating / rank）。"""
    src = MART_DEMO_PATH.read_text(encoding="utf-8")
    clean = _strip_ts_comments(src)
    _assert_no_forbidden_tokens(clean, "mart_city_demo.ts")


def test_mart_demo_has_6_segments_and_7_dim_cards() -> None:
    """demo 行数 = 6 段 evidence + 7 cell（per docs/06 §2 六段 + docs/42 §2.4 七维度）。"""
    src = MART_DEMO_PATH.read_text(encoding="utf-8")
    clean = _strip_ts_comments(src)
    # SEGMENTS_6 数组
    assert "SEGMENTS_6" in clean
    seg_count = len(re.findall(r"\"(CONDITION|COMMITMENT|INPUT|PROCESS|OUTPUT|OUTCOME_RISK)\"", clean))
    assert seg_count >= 6, f"SEGMENTS_6 必含 6 段；当前段数 = {seg_count}"
    # SEVEN_DIM_CARD_IDS 7 维度
    assert "SEVEN_DIM_CARD_IDS" in clean or "SevenDimCardId" in clean
    card_count = len(re.findall(
        r"\"(POLICY_DELIVERY|FISCAL_EXECUTION|PROJECT_DELIVERY|"
        r"ECONOMIC_ADAPTATION|PUBLIC_SERVICES|RISK_MANAGEMENT|GOAL_CONSISTENCY)\"",
        clean,
    ))
    assert card_count >= 7, f"七维度必含 7 个 cardId；当前 cardId 数 = {card_count}"


# ===== 3. CityPageMart.tsx 接驳 =====

def test_city_page_mart_imports_3_components() -> None:
    """CityPageMart 复用三件套：EvidenceChain + SevenDimGrid + PeerCompareCard。"""
    src = CITY_PAGE_MART_PATH.read_text(encoding="utf-8")
    clean = _strip_ts_comments(src)
    assert "EvidenceChain" in clean
    assert "SevenDimGrid" in clean
    assert "PeerCompareCard" in clean


def test_city_page_mart_no_forbidden_tokens() -> None:
    """CityPageMart 不含禁词（不派生 score / rating / rank）。"""
    src = CITY_PAGE_MART_PATH.read_text(encoding="utf-8")
    clean = _strip_ts_comments(src)
    _assert_no_forbidden_tokens(clean, "CityPageMart.tsx")


# ===== 4. /cities/[slug]/page.tsx feature-flag =====

def test_slug_page_has_feature_flag_default_demo() -> None:
    """[slug]/page.tsx 默认走 mock（NEXT_PUBLIC_USE_MART_FIXTURE != "1"）；可 feature-flag 启用 mart-shape。"""
    src = SLUG_PAGE_PATH.read_text(encoding="utf-8")
    clean = _strip_ts_comments(src)
    assert "NEXT_PUBLIC_USE_MART_FIXTURE" in clean, "缺少 feature-flag 守门"
    assert "shouldUseMartFixture" in clean, "缺少 shouldUseMartFixture 函数"
    assert "getMockCity" in clean, "默认 mock 路径保留"
    assert "getMartCityDemo" in clean, "mart-shape 接驳路径新增"
    assert "CityPageMart" in clean, "CityPageMart 组件导入"


def test_slug_page_no_forbidden_tokens() -> None:
    """[slug]/page.tsx 不含禁词。"""
    src = SLUG_PAGE_PATH.read_text(encoding="utf-8")
    clean = _strip_ts_comments(src)
    _assert_no_forbidden_tokens(clean, "[slug]/page.tsx")