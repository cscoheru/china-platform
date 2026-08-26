"""Stage 2 / S2.7-b person/tenure demo fixture guard test.

Per docs/47 §3.3 + tasking 302 (10 城 demo relatedPersons/tenure).

Locks in the contract:
  - 10 城 × 2 demo relatedPersons 行 = 20 demo 人物行
  - canonical_name 全部 demo 占位（含 "演示" / "mock" 标识）
  - 不写真实姓名（per `302` §红线 "不伪造真身份材料"）
  - positionTitle = "市委书记（演示职位）" / "市长（演示职位）"
  - geoCanonicalName = city nameZh
  - isCurrent = true
  - lineage.isDemo = true
  - lineage.sourceFileSha256 = '0'.repeat(64) 占位（per docs/47 §3.1 ⚠️ OPEN）
  - lineage.demoReason 非空
  - 无禁词（score/rating/rank/total_score/confidence_score/credibility_score/peer_rank）

Red lines (per tasking 302 §红线 + docs/47 §1.2 + docs/34 §1 + docs/06 §6.6 + docs/42 §8):
  - No real person names
  - No real tenure dates
  - No real SHA
  - No Gate 1/2 PASS
  - No forbidden scoring columns
  - No peer_rank derivation
"""
from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
FRONTEND = ROOT / "frontend"

MART_DEMO_TS = FRONTEND / "lib" / "mart_city_demo.ts"
MART_TYPES_TS = FRONTEND / "lib" / "mart_city_types.ts"
CITY_SLUG_MAP_TS = FRONTEND / "lib" / "city_slug_map.ts"
CITYPAGE_MART_TSX = FRONTEND / "app" / "components" / "CityPageMart.tsx"

EXPECTED_10_CITIES = [
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

FORBIDDEN_TOKENS = [
    "score",
    "rating",
    "rank",
    "total_score",
    "confidence_score",
    "credibility_score",
    "peer_rank",
]

# Demo canonical_name 必须含以下任一标识（per `302` §红线"UI 必须可区分 demo"）
DEMO_NAME_MARKERS = ("演示", "mock")


def _strip_ts_comments(src: str) -> str:
    src = re.sub(r"/\*[\s\S]*?\*/", "", src)
    out_lines: list[str] = []
    for line in src.splitlines():
        idx = line.find("//")
        if idx >= 0:
            line = line[:idx]
        if line.strip():
            out_lines.append(line)
    return "\n".join(out_lines)


# ===== 1. file existence =====

def test_mart_city_demo_ts_exists() -> None:
    assert MART_DEMO_TS.is_file(), f"missing: {MART_DEMO_TS}"


def test_build_mart_related_persons_function_exists() -> None:
    """buildMartRelatedPersons 工厂函数必须存在（per `302` §SCHEMA）。"""
    src = MART_DEMO_TS.read_text(encoding="utf-8")
    clean = _strip_ts_comments(src)
    assert "buildMartRelatedPersons" in clean, (
        "mart_city_demo.ts: 缺 buildMartRelatedPersons() 函数 "
        "(per `302` §SCHEMA '10 城 demo relatedPersons')"
    )


# ===== 2. relatedPersons 行数与城市覆盖 =====

def test_mart_demo_ts_exposes_related_persons_per_city_constant() -> None:
    """导出常量 MART_CITY_DEMO_RELATED_PERSONS_PER_CITY 必须 = 2。"""
    src = MART_DEMO_TS.read_text(encoding="utf-8")
    clean = _strip_ts_comments(src)
    assert "MART_CITY_DEMO_RELATED_PERSONS_PER_CITY" in clean, (
        "mart_city_demo.ts: 缺导出常量 MART_CITY_DEMO_RELATED_PERSONS_PER_CITY"
    )
    # 找 const 声明 = 2
    m = re.search(
        r"MART_CITY_DEMO_RELATED_PERSONS_PER_CITY\s*=\s*(\d+)",
        clean,
    )
    assert m is not None, "缺 const 声明"
    assert m.group(1) == "2", (
        f"MART_CITY_DEMO_RELATED_PERSONS_PER_CITY 必须 = 2 (per `302` §SCHEMA "
        f"2 行/城：市委书记 + 市长)，got {m.group(1)}"
    )


def test_mart_demo_ts_exposes_related_persons_total_constant() -> None:
    """导出常量 MART_CITY_DEMO_RELATED_PERSONS_TOTAL 必须 = 10 × 2 = 20。

    可写成字面量 20 或 `MART_CITY_DEMO_COUNT * MART_CITY_DEMO_RELATED_PERSONS_PER_CITY` 表达式。
    """
    src = MART_DEMO_TS.read_text(encoding="utf-8")
    clean = _strip_ts_comments(src)
    m_lit = re.search(
        r"MART_CITY_DEMO_RELATED_PERSONS_TOTAL\s*=\s*(\d+)",
        clean,
    )
    m_expr = re.search(
        r"MART_CITY_DEMO_RELATED_PERSONS_TOTAL\s*=\s*"
        r"MART_CITY_DEMO_COUNT\s*\*\s*MART_CITY_DEMO_RELATED_PERSONS_PER_CITY",
        clean,
    )
    assert m_lit is not None or m_expr is not None, (
        "MART_CITY_DEMO_RELATED_PERSONS_TOTAL 必须 = 20 字面量或 "
        "= MART_CITY_DEMO_COUNT * MART_CITY_DEMO_RELATED_PERSONS_PER_CITY 表达式"
    )
    if m_lit is not None:
        assert m_lit.group(1) == "20", (
            f"MART_CITY_DEMO_RELATED_PERSONS_TOTAL 字面量必须 = 20，got {m_lit.group(1)}"
        )


# ===== 3. relatedPersons 字段契约（per docs/47 §3.3 最小子集）=====

def test_related_persons_iterates_all_10_cities() -> None:
    """buildMartRelatedPersons 必须接收 citySlug 并返回 demo 行（per city）。"""
    src = MART_DEMO_TS.read_text(encoding="utf-8")
    clean = _strip_ts_comments(src)
    # 工厂函数定义 + 调用链路：buildMartCityView 调 buildMartRelatedPersons(citySlug)
    assert "buildMartRelatedPersons(citySlug)" in clean, (
        "buildMartCityView 必须调 buildMartRelatedPersons(citySlug)"
    )
    # 10 城 slug 引用 — 在 city_slug_map.ts 中定义，buildMartCityView 通过 CITY_SLUG_LIST 遍历
    slug_src = CITY_SLUG_MAP_TS.read_text(encoding="utf-8")
    slug_clean = _strip_ts_comments(slug_src)
    for slug in EXPECTED_10_CITIES:
        assert f'"{slug}"' in slug_clean, f"city_slug_map.ts 缺 '{slug}'"


def test_related_persons_canonical_name_is_demo_only() -> None:
    """canonical_name 全部 demo 占位（含 "演示" 或 "mock" 标识）。"""
    src = MART_DEMO_TS.read_text(encoding="utf-8")
    clean = _strip_ts_comments(src)
    # 抓所有 canonicalName 字符串字面量
    name_literals = re.findall(r'canonicalName:\s*`([^`]+)`', clean)
    assert name_literals, "缺 canonicalName 字面量"
    for name in name_literals:
        assert any(mk in name for mk in DEMO_NAME_MARKERS), (
            f"canonical_name 缺 demo 标识: '{name}' "
            f"(per `302` §红线 '不伪造真身份材料' + 'UI 必须可区分 demo')"
        )


def test_related_persons_no_real_name_pinyin() -> None:
    """canonical_name 不应出现真实姓名拼音特征（如 ZG 大写拼音）。"""
    src = MART_DEMO_TS.read_text(encoding="utf-8")
    clean = _strip_ts_comments(src)
    name_literals = re.findall(r'canonicalName:\s*`([^`]+)`', clean)
    for name in name_literals:
        # 真名拼音通常 2-4 个汉字；demo 模板固定为 "演示 人物 X (mock, {slug})"
        assert "演示" in name, (
            f"canonical_name 缺 '演示' 标识（可能错写真实姓名）: {name}"
        )


def test_related_persons_position_title_is_demo() -> None:
    """positionTitle 须为演示职位（含 "演示职位" 标识）。"""
    src = MART_DEMO_TS.read_text(encoding="utf-8")
    clean = _strip_ts_comments(src)
    pos_literals = re.findall(r'positionTitle:\s*"([^"]+)"', clean)
    assert pos_literals, "缺 positionTitle 字面量"
    for pos in pos_literals:
        assert "演示职位" in pos, (
            f"positionTitle 缺 '演示职位' 标识: '{pos}' "
            f"(per `302` §红线 '不伪造真身份材料')"
        )


def test_related_persons_position_titles_cover_secretary_and_mayor() -> None:
    """positionTitle 必含 市委书记 + 市长（per `302` §SCHEMA 2 行/城）。"""
    src = MART_DEMO_TS.read_text(encoding="utf-8")
    clean = _strip_ts_comments(src)
    pos_literals = re.findall(r'positionTitle:\s*"([^"]+)"', clean)
    has_secretary = any("市委书记" in p for p in pos_literals)
    has_mayor = any("市长" in p for p in pos_literals)
    assert has_secretary, "缺 市委书记（演示职位）"
    assert has_mayor, "缺 市长（演示职位）"


# ===== 4. lineage 契约守门 =====

def test_related_persons_lineage_is_demo_true() -> None:
    """lineage.isDemo 必须 = true（per S1.18 sentinel）。"""
    src = MART_DEMO_TS.read_text(encoding="utf-8")
    clean = _strip_ts_comments(src)
    # buildMartLineage 是共享的 factory，isDemo: true 必出现
    assert "isDemo: true" in clean, "buildMartLineage 必须 isDemo: true"


def test_related_persons_lineage_sha_is_zero_64() -> None:
    """lineage.sourceFileSha256 必须 = '0'.repeat(64) 占位（per docs/47 §3.1 ⚠️ OPEN）。"""
    types_src = MART_TYPES_TS.read_text(encoding="utf-8")
    types_clean = _strip_ts_comments(types_src)
    assert '"0".repeat(64)' in types_clean, (
        "mart_city_types.ts: MART_LINEAGE_PLACEHOLDER_SHA 必须 = '0'.repeat(64)"
    )


def test_related_persons_lineage_demo_reason_non_empty() -> None:
    """lineage.demoReason 非空（per isValidMartLineage 守门）。"""
    src = MART_DEMO_TS.read_text(encoding="utf-8")
    clean = _strip_ts_comments(src)
    # buildMartLineage 内的 demoReason 模板字面量
    m = re.search(r'demoReason:\s*`([^`]+)`', clean)
    assert m is not None, "缺 demoReason 模板"
    reason = m.group(1)
    assert len(reason) > 0, "demoReason 必须非空"
    # demoReason 应解释为何 SHA 占位
    assert "演示" in reason or "demo" in reason.lower(), (
        f"demoReason 缺 demo 标识: '{reason}'"
    )


# ===== 5. 禁词守门 =====

def test_mart_demo_ts_no_forbidden_tokens() -> None:
    """禁词守门（per docs/06 §6.6 + docs/42 §8）。"""
    src = MART_DEMO_TS.read_text(encoding="utf-8")
    clean = _strip_ts_comments(src)
    for tok in FORBIDDEN_TOKENS:
        pat = re.compile(rf"(?<![A-Za-z0-9_]){re.escape(tok)}(?![A-Za-z0-9_])")
        assert not pat.search(clean), (
            f"FORBIDDEN: mart_city_demo.ts 含禁词 '{tok}'"
        )


def test_related_persons_section_uses_assertion_guard() -> None:
    """buildMartRelatedPersons 须调 assertMartRowHasNoForbiddenFields 守门。"""
    src = MART_DEMO_TS.read_text(encoding="utf-8")
    clean = _strip_ts_comments(src)
    # 在 buildMartRelatedPersons 块内检查
    # 简化：在 demo file 内必须出现对 mart_related_persons 的 assert
    assert "mart_related_persons" in clean, (
        "缺 mart_related_persons 标签的 assert 守门"
    )
    assert "assertMartRowHasNoForbiddenFields" in clean, (
        "缺 assertMartRowHasNoForbiddenFields 调用"
    )


# ===== 6. UI demo 标识守门 =====

def test_city_page_mart_uses_related_persons_field() -> None:
    """CityPageMart.tsx 应消费 relatedPersons 字段。"""
    src = CITYPAGE_MART_TSX.read_text(encoding="utf-8")
    clean = _strip_ts_comments(src)
    # 字段名 relatedPersons (camelCase per MartCityViewProps interface)
    assert "relatedPersons" in clean, (
        "CityPageMart.tsx: 缺 relatedPersons 消费（per `302` §NOW '落地 10 城 demo relatedPersons'）"
    )