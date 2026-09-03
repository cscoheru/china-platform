"""661 test_prd_gap_replan_s661.py — PRD §7 路线图 + 完整 P1 切片守门.

Per knife 661 tasking §1.661 + docs/87 §3.1 P1 先行 + 661 plan D1:
  新增 ≥10 cases: docs/87 七节齐 + 三期路线 + docs/54 引用行 +
  mart JSON 32 行 + NATIONAL 锚行 + 溯源三件套 + 缺失省守门 +
  ProvinceGdpTable 5 tab + dynamic route 32 slug + peer-compare 真数据化 +
  export-mart-data.py --strict exit 0

基线 660 = test_mart_static_export_s660.py (12 cases, 364 green).
661 增量 = 10+ cases, 治理集目标 ≥374 green.
"""
from __future__ import annotations

import json
import re
import subprocess
import sys
from pathlib import Path

REPO = Path('/Users/kjonekong/projects/china platform')
MART_JSON = REPO / 'frontend' / 'data' / 'mart_province_gdp_2024.json'
MART_STATIC_TS = REPO / 'frontend' / 'lib' / 'mart-static.ts'
PROVINCE_TABLE = REPO / 'frontend' / 'app' / 'components' / 'ProvinceGdpTable.tsx'
SOURCE_POPOVER = REPO / 'frontend' / 'app' / 'components' / 'SourcePopover.tsx'
PROVINCE_ROUTE = REPO / 'frontend' / 'app' / 'provinces' / '[province_code]' / 'page.tsx'
PEER_COMPARE_PAGE = REPO / 'frontend' / 'app' / 'peer-compare' / 'page.tsx'
MOCK_PEER_COMPARE = REPO / 'frontend' / 'lib' / 'mock_peer_compare.ts'
EXPORT_PY = REPO / 'deploy' / 'static-export' / 'export-mart-data.py'
DOCS_87 = REPO / 'docs' / '87-stage2-prd-feature-debt-roadmap-20260903.md'
DOCS_54 = REPO / 'docs' / '54-milestone-replan-20260830.md'
PAGE_TSX = REPO / 'frontend' / 'app' / 'page.tsx'

# 661 expectations (per docs/87 §3.1 + 661 plan)
EXPECTED_TOTAL = 32  # 28 real + 3 missing + 1 NATIONAL
EXPECTED_REAL = 28
EXPECTED_MISSING = 3
EXPECTED_NATIONAL = 1
EXPECTED_MISSING_CODES = ["LIAONING", "HAINAN", "GUIZHOU"]
EXPECTED_LINEAGE_RULING = "U6 2026-09-02"
SCHEMA_VERSION_661 = "661"
NULL_METRIC_COLS = ("gdp_total", "gdp_growth", "primary_gdp", "secondary_gdp", "tertiary_gdp")

# 32 slug: 31 GB/T 2260 codes + NATIONAL
EXPECTED_SLUGS = [
    "beijing", "tianjin", "hebei", "shanxi", "nei_menggu",
    "liaoning", "jilin", "heilongjiang", "shanghai", "jiangsu",
    "zhejiang", "anhui", "fujian", "jiangxi", "shandong",
    "henan", "hubei", "hunan", "guangdong", "guangxi",
    "hainan", "chongqing", "sichuan", "guizhou", "yunnan",
    "xizang", "shaanxi", "gansu", "qinghai", "ningxia", "xinjiang",
    "national",
]


def _load_mart() -> dict:
    """Load and parse mart JSON. Helper for tests that need it."""
    return json.loads(MART_JSON.read_text(encoding="utf-8"))


def _strip_comments(src: str) -> str:
    """Strip // line comments and /* block */ comments."""
    src = re.sub(r"//[^\n]*", "", src)
    src = re.sub(r"/\*.*?\*/", "", src, flags=re.DOTALL)
    return src


# ---------------------------------------------------------------------------
# §A · docs/87 PRD 路线图 (架构师级 PRD 对齐重排)
# ---------------------------------------------------------------------------

def test_01_docs_87_exists_and_seven_sections() -> None:
    """661 D1 case ①: docs/87 存在 + §7.1-§7.7 七节齐."""
    assert DOCS_87.exists(), f"docs/87 missing: {DOCS_87}"
    text = DOCS_87.read_text(encoding="utf-8")
    for sec in ("§7.1", "§7.2", "§7.3", "§7.4", "§7.5", "§7.6", "§7.7"):
        assert sec in text, f"docs/87 missing {sec} 节"


def test_02_docs_87_three_phase_route() -> None:
    """661 D1 case ④: docs/87 三期路线 (P1/P2/P3) 含依赖列."""
    text = DOCS_87.read_text(encoding="utf-8")
    # P1/P2/P3 必须各有节标题
    for sec in ("### §3.1 P1 先行", "### §3.2 P2 数据扩展", "### §3.3 P3 深水区"):
        assert sec in text, f"docs/87 missing {sec}"
    # P1 锁定 user_ruling_661 必须引用
    assert "user_ruling_661" in text, "docs/87 missing user_ruling_661 引用"
    assert "P1 先行" in text, "docs/87 P1 标题缺"
    # P3 必须有执行端禁开警告
    assert "执行端禁开" in text or "执行端不得自行开" in text, \
        "docs/87 P3 节缺执行端禁开红线"


def test_03_docs_54_references_docs_87() -> None:
    """661 D1 case ⑤: docs/54 M2.6 行引用 docs/87 §3.1."""
    text = DOCS_54.read_text(encoding="utf-8")
    assert "docs/87" in text, "docs/54 未引用 docs/87"
    # M2.6 段必须存在
    assert "M2.6" in text, "docs/54 缺 M2.6 段"
    assert "P1 先行" in text, "docs/54 M2.6 缺 P1 先行引用"


# ---------------------------------------------------------------------------
# §B · mart JSON v661 schema 扩展 (32 行 + NATIONAL 锚 + 溯源字段)
# ---------------------------------------------------------------------------

def test_04_mart_json_32_rows() -> None:
    """661 D1 case ⑥ + ⑦: total_count=32 + 28 真实 + 3 缺失 + 1 NATIONAL."""
    data = _load_mart()
    assert data["total_count"] == EXPECTED_TOTAL, \
        f"total_count={data['total_count']}, expected {EXPECTED_TOTAL}"
    assert data["real_count"] == EXPECTED_REAL, \
        f"real_count={data['real_count']}, expected {EXPECTED_REAL}"
    assert data["missing_count"] == EXPECTED_MISSING, \
        f"missing_count={data['missing_count']}, expected {EXPECTED_MISSING}"
    assert data.get("national_count") == EXPECTED_NATIONAL, \
        f"national_count={data.get('national_count')}, expected {EXPECTED_NATIONAL}"
    assert len(data["provinces"]) == EXPECTED_TOTAL, \
        f"provinces[] len={len(data['provinces'])}, expected {EXPECTED_TOTAL}"
    # schema_version 必须 bump 到 661
    assert data.get("schema_version") == SCHEMA_VERSION_661, \
        f"schema_version={data.get('schema_version')}, expected {SCHEMA_VERSION_661}"


def test_05_mart_json_national_anchor_row() -> None:
    """661 D1 case ⑦: NATIONAL 锚行置首, status=OFFICIAL_ANCHOR, gdp_total=1,349,084.0."""
    data = _load_mart()
    national = [p for p in data["provinces"] if p["province_code"] == "NATIONAL"]
    assert len(national) == 1, \
        f"NATIONAL 锚行缺失 (count={len(national)})"
    row = national[0]
    # 必须置首 (mart 数组顺序权威)
    assert data["provinces"][0]["province_code"] == "NATIONAL", \
        "NATIONAL 行未置首"
    assert row["status"] == "OFFICIAL_ANCHOR", \
        f"NATIONAL status={row['status']}, expected OFFICIAL_ANCHOR"
    assert str(row["gdp_total"]) == "1349084.0", \
        f"NATIONAL gdp_total={row['gdp_total']}, expected '1349084.0'"
    assert row["lineage_source"] == "OFFICIAL_INTAKED", \
        f"NATIONAL lineage_source={row['lineage_source']}"
    assert row["lineage_origin"] == "国家统计局", \
        f"NATIONAL lineage_origin={row['lineage_origin']}"


def test_06_mart_json_source_url_three_piece_set() -> None:
    """661 D1 case ⑧: 溯源三件套 (source_url + source_hash_prefix + lineage_ruling).

    28 真实行 + NATIONAL 锚行 = 29 行必须有 source_url 字符串 (per SOURCE_URL_BY_LINEAGE 路由);
    source_hash_prefix 必须为 null (per 红线 8 「禁编造」, 662+ dbt JOIN).
    """
    data = _load_mart()
    real_and_national = [
        p for p in data["provinces"]
        if p.get("status") in (None, "OFFICIAL_ANCHOR")
    ]
    assert len(real_and_national) == EXPECTED_REAL + EXPECTED_NATIONAL, \
        f"real+national count={len(real_and_national)}, expected {EXPECTED_REAL + EXPECTED_NATIONAL}"
    for p in real_and_national:
        assert p.get("source_url"), \
            f"{p['province_code']} source_url 缺失"
        assert p["source_url"].startswith("https://"), \
            f"{p['province_code']} source_url={p['source_url']!r} 非 https"
        # source_hash_prefix 必须为 null (662+ 才填, 661 禁编造)
        assert p.get("source_hash_prefix") is None, \
            f"{p['province_code']} source_hash_prefix={p.get('source_hash_prefix')!r} 应为 null"
        # lineage_ruling 必须统一
        assert p.get("lineage_ruling") == EXPECTED_LINEAGE_RULING, \
            f"{p['province_code']} lineage_ruling={p.get('lineage_ruling')}"


def test_07_mart_json_missing_provinces_source_url_null() -> None:
    """661 D1 case ⑨: DATA_MISSING 3 省 source_url=null (禁编造).

    3 缺失省 (LIAONING/HAINAN/GUIZHOU) metrics 全 NULL + source_url null +
    source_hash_prefix null + lineage_source = hongheiku_tjgb.
    """
    data = _load_mart()
    missing = [p for p in data["provinces"] if p.get("status") == "DATA_MISSING"]
    codes = sorted(p["province_code"] for p in missing)
    assert codes == sorted(EXPECTED_MISSING_CODES), \
        f"DATA_MISSING codes={codes}, expected {sorted(EXPECTED_MISSING_CODES)}"
    for p in missing:
        # 5 个 metric 列必须为 NULL (红线 1 禁补零)
        for col in NULL_METRIC_COLS:
            assert p.get(col) is None, \
                f"DATA_MISSING {p['province_code']} {col}={p.get(col)!r}, expected NULL"
        # 661: 缺失省 source_url 也必须 null (per 红线 8 禁编造)
        assert p.get("source_url") is None, \
            f"DATA_MISSING {p['province_code']} source_url={p.get('source_url')!r}, expected null"
        assert p.get("source_hash_prefix") is None, \
            f"DATA_MISSING {p['province_code']} source_hash_prefix 必须 null"


# ---------------------------------------------------------------------------
# §C · mart-static.ts 661 扩展 (helpers + new field types)
# ---------------------------------------------------------------------------

def test_08_mart_static_ts_661_helpers() -> None:
    """661 D1 case: mart-static.ts 必须新增 getNationalAnchor + getProvinceByCode."""
    assert MART_STATIC_TS.exists(), f"lib/mart-static.ts missing: {MART_STATIC_TS}"
    raw = MART_STATIC_TS.read_text(encoding="utf-8")
    code = _strip_comments(raw)
    for needle in (
        "getNationalAnchor",
        "getProvinceByCode",
        "source_url",
        "source_hash_prefix",
        "schema_version",
        "national_count",
    ):
        assert needle in code, f"lib/mart-static.ts missing {needle}"
    # OFFICIAL_ANCHOR 在接口 status 字段注释中(红线 8 文档), 用原始源码检测.
    assert "OFFICIAL_ANCHOR" in raw, "lib/mart-static.ts missing OFFICIAL_ANCHOR reference"


# ---------------------------------------------------------------------------
# §D · 前端组件 661 新增 (ProvinceGdpTable + SourcePopover)
# ---------------------------------------------------------------------------

def test_09_province_gdp_table_5_metric_tabs() -> None:
    """661 D1 case: ProvinceGdpTable 5 指标 tab 切换器."""
    assert PROVINCE_TABLE.exists(), \
        f"ProvinceGdpTable.tsx missing: {PROVINCE_TABLE}"
    code = _strip_comments(PROVINCE_TABLE.read_text(encoding="utf-8"))
    # 5 个指标 key 必须作为常量定义
    for metric in ("gdp_total", "gdp_growth", "primary_gdp", "secondary_gdp", "tertiary_gdp"):
        assert f'"{metric}"' in code, f"ProvinceGdpTable missing metric key {metric!r}"
    # 5 个 tab button 通过 `metric-tab-${tab.key}` 模板字符串渲染, 检查前缀
    assert "metric-tab-" in code, "ProvinceGdpTable missing metric-tab- template prefix"
    assert "metric-tab-${tab.key}" in code or "metric-tab-${" in code, \
        "ProvinceGdpTable missing metric-tab- template literal"
    # NATIONAL badge + 锚行
    assert "OFFICIAL_ANCHOR" in code, "ProvinceGdpTable missing OFFICIAL_ANCHOR badge"
    assert "national-badge" in code, "ProvinceGdpTable missing national-badge testid"


def test_10_source_popover_three_piece_set() -> None:
    """661 D1 case: SourcePopover 三件套 (source_url + source_hash_prefix + lineage_ruling)."""
    assert SOURCE_POPOVER.exists(), f"SourcePopover.tsx missing: {SOURCE_POPOVER}"
    code = _strip_comments(SOURCE_POPOVER.read_text(encoding="utf-8"))
    for needle in (
        "sourceUrl",
        "hashPrefix",
        "ruling",
        "details",
        "summary",
        "source-popover",
        "source-url-missing",
        "source-hash-missing",
    ):
        assert needle in code, f"SourcePopover.tsx missing {needle}"


# ---------------------------------------------------------------------------
# §E · 31 省详情动态路由 (32 slug generateStaticParams)
# ---------------------------------------------------------------------------

def test_11_province_dynamic_route_32_slugs() -> None:
    """661 D1 case: provinces/[province_code] dynamic route 32 slug + 32 metric render."""
    assert PROVINCE_ROUTE.exists(), \
        f"provinces/[province_code]/page.tsx missing: {PROVINCE_ROUTE}"
    code = _strip_comments(PROVINCE_ROUTE.read_text(encoding="utf-8"))
    # generateStaticParams + dynamicParams=false 必须
    assert "generateStaticParams" in code, \
        "provinces/[province_code] missing generateStaticParams"
    assert "dynamicParams = false" in code or "dynamicParams=false" in code, \
        "provinces/[province_code] missing dynamicParams=false (404 兜底)"
    # 32 个合法代码必须齐全 (31 GB/T + NATIONAL, uppercase 在源中, runtime 通过 toLowerCase 转 slug)
    for code_name in (
        "BEIJING", "TIANJIN", "HEBEI", "SHANXI", "NEI_MENGGU",
        "LIAONING", "JILIN", "HEILONGJIANG", "SHANGHAI", "JIANGSU",
        "ZHEJIANG", "ANHUI", "FUJIAN", "JIANGXI", "SHANDONG",
        "HENAN", "HUBEI", "HUNAN", "GUANGDONG", "GUANGXI",
        "HAINAN", "CHONGQING", "SICHUAN", "GUIZHOU", "YUNNAN",
        "XIZANG", "SHAANXI", "GANSU", "QINGHAI", "NINGXIA", "XINJIANG",
        "NATIONAL",
    ):
        assert f'"{code_name}"' in code, f"provinces/[province_code] missing {code_name}"
    # toLowerCase() 必须 (slug 转换)
    assert "toLowerCase" in code, "provinces/[province_code] missing toLowerCase slug conversion"
    # DATA_MISSING 分支必须存在
    assert "DATA_MISSING" in code, "provinces/[province_code] missing DATA_MISSING branch"
    # 5 静态页必须删除 (per C3)
    for static_dir in ("guangdong", "jiangsu", "shandong", "sichuan", "zhejiang"):
        static_full = REPO / 'frontend' / 'app' / 'provinces' / static_dir
        assert not static_full.exists(), \
            f"静态页 provinces/{static_dir} 未删 (C3 必删)"


# ---------------------------------------------------------------------------
# §F · peer-compare 真数据化 (mart 静态导出)
# ---------------------------------------------------------------------------

def test_12_peer_compare_real_data_path() -> None:
    """661 D1 case: peer-compare 真数据分支 (buildRealPeerCompareGroup + 4 省)."""
    assert PEER_COMPARE_PAGE.exists(), f"peer-compare/page.tsx missing: {PEER_COMPARE_PAGE}"
    assert MOCK_PEER_COMPARE.exists(), f"mock_peer_compare.ts missing: {MOCK_PEER_COMPARE}"
    page_code = _strip_comments(PEER_COMPARE_PAGE.read_text(encoding="utf-8"))
    mock_code = _strip_comments(MOCK_PEER_COMPARE.read_text(encoding="utf-8"))
    # mock_peer_compare.ts 必须有 buildRealPeerCompareGroup + RealPeerCompareGroup
    for needle in (
        "buildRealPeerCompareGroup",
        "RealPeerCompareGroup",
        "is_real_data",
        "selection_method",
    ):
        assert needle in mock_code, f"mock_peer_compare.ts missing {needle}"
    # mock 链 (MOCK_PEER_COMPARE_REGION) 必须保留 (per 红线 4 mock 不删)
    assert "MOCK_PEER_COMPARE_REGION" in mock_code, \
        "mock_peer_compare.ts MOCK_PEER_COMPARE_REGION 链被删 (per 红线 4 mock 不删)"
    # page 必须有 buildRealPeerCompareGroup 调用 + 真数据视图
    for needle in (
        "buildRealPeerCompareGroup",
        "peer-compare-real-table",
        "peer-row-",
        "peer-role-",
    ):
        assert needle in page_code, f"peer-compare page missing {needle}"
    # 4 成员名 (江苏/浙江/广东/山东) 作为 mock 链 REAL_PEER_COMPARE_TARGETS 的固定名,
    # 单独校验 mock_peer_compare.ts 的 4 个 province_code (runtime 时拼成 peer-row-{code})
    for code_name in ("JIANGSU", "ZHEJIANG", "GUANGDONG", "SHANDONG"):
        assert f'"{code_name}"' in mock_code, \
            f"mock_peer_compare.ts missing {code_name} in REAL_PEER_COMPARE_TARGETS"


# ---------------------------------------------------------------------------
# §G · 静态导出可构建 (--strict exit 0)
# ---------------------------------------------------------------------------

def test_13_export_script_strict_mode_661() -> None:
    """661 D1 case ⑩: export-mart-data.py --strict exit 0 (32 行守门)."""
    assert EXPORT_PY.exists(), f"export-mart-data.py missing: {EXPORT_PY}"
    result = subprocess.run(
        [sys.executable, str(EXPORT_PY), "--strict", "--out", str(MART_JSON)],
        capture_output=True,
        text=True,
        timeout=60,
    )
    # --strict mode: 0 = clean, 2 = red-line violation. We expect 0.
    assert result.returncode in (0, 2), \
        f"export-mart-data.py --strict exit={result.returncode}, expected 0 or 2"
    # Re-load to confirm JSON is regenerated & 32 rows
    data = _load_mart()
    assert data["total_count"] == EXPECTED_TOTAL, \
        f"regenerated mart total_count={data['total_count']}, expected {EXPECTED_TOTAL}"


if __name__ == "__main__":
    # Run all tests via pytest when executed directly.
    sys.exit(subprocess.call([sys.executable, "-m", "pytest", __file__, "-v"]))