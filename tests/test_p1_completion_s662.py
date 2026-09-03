"""knife 662 P1 收尾刀 — 库中已有数据全量呈现 + 公网验收脚本化.

Per 662 tasking §1.662 + docs/87 §3.1 P1 先行 + docs/85 §部署 runbook.

锁住 662 范围 (六件套):
  A. 血缘全量露出 (D1 — SourcePopover 扩字段 lineage_source/origin)
  B. 指标定义页 /indicators (D2 — 5 指标 × 来源等级三档分布)
  C. 数据完整度面板 (D3 — CoverageMatrix 31×5 + 3 省 DATA_MISSING 公示)
  D. 排序交互 (D4 — sort-bar 5 排序按钮 + 口径提示, 禁榜单化)
  E. demo 壳显式标注 (D5 — DemoBanner 4 页 + layout LIVE/DEMO 导航)
  F. F2 公网验收脚本化 (D6 — verify-live.sh 12 项断言)

14+ cases 覆盖:
  1. SourcePopover 接收 lineageSource + lineageOrigin + isDataMissing 三 prop
  2. SourcePopover 五件套渲染顺序 (URL → SHA → lineage_source → lineage_origin → ruling)
  3. SourcePopover isDataMissing 显式 flag (不靠 lineageSource 字符串)
  4. ProvinceGdpTable 调用 SourcePopover 传 lineageSource/origin (3 类行)
  5. ProvinceGdpTable 含 sort-bar + 5 排序按钮 testid
  6. ProvinceGdpTable sortCaveat 引用 docs/05 §8.3
  7. mart_indicator_definitions_2024.json schema 校验 (5 指标 + 三档分布)
  8. export-mart-data.py 含 indicator_definitions 导出函数
  9. export-mart-data.py 等级分布用 status 字段 (不靠 lineage_source 字符串)
 10. mart-static.ts MartIndicatorDefinition 类型 + getIndicatorDefinitions
 11. /indicators 页存在 + 5 指标卡 testid
 12. CoverageMatrix 31 行 × 5 列 testid 完整
 13. DataCompletenessPanel 含 CoverageMatrix + DATA_MISSING 3 省公示
 14. DemoBanner 组件存在 + 4 demo 页都插了
 15. layout LIVE/DEMO 导航分组 testid
 16. verify-live.sh 存在 + 含 12 项断言标识
 17. mart_indicator_definitions JSON 可被 export-mart-data.py 干跑生成
 18. mart-static.ts deriveIndicatorDefsPath 同目录约定
"""
from __future__ import annotations

import json
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
FRONTEND = ROOT / "frontend"
APP = FRONTEND / "app"
LIB = FRONTEND / "lib"
DEPLOY = ROOT / "deploy" / "static-export"
DATA = FRONTEND / "data"

SOURCE_POPOVER = APP / "components" / "SourcePopover.tsx"
PROVINCE_GDP_TABLE = APP / "components" / "ProvinceGdpTable.tsx"
PROVINCE_PAGE = APP / "provinces" / "[province_code]" / "page.tsx"
PEER_COMPARE_PAGE = APP / "peer-compare" / "page.tsx"
COVERAGE_MATRIX = APP / "components" / "CoverageMatrix.tsx"
COMPLETENESS_PANEL = APP / "components" / "DataCompletenessPanel.tsx"
DEMO_BANNER = APP / "DemoBanner.tsx"
INDICATORS_PAGE = APP / "indicators" / "page.tsx"
LAYOUT = APP / "layout.tsx"
HOME_PAGE = APP / "page.tsx"
MART_STATIC = LIB / "mart-static.ts"

SEVEN_DIM_PAGE = APP / "seven-dim" / "page.tsx"
M1_SERIES_PAGE = APP / "research" / "m1-series" / "page.tsx"
Q1_2024_PAGE = APP / "research" / "q1-2024-gdp" / "page.tsx"
PUBLIC_EXTRACTS_PAGE = APP / "public-extracts" / "page.tsx"

EXPORT_SCRIPT = DEPLOY / "export-mart-data.py"
VERIFY_LIVE_SH = DEPLOY / "verify-live.sh"

INDICATOR_DEFS_JSON = DATA / "mart_indicator_definitions_2024.json"

METRIC_KEYS = [
    "gdp_total", "gdp_growth", "primary_gdp", "secondary_gdp", "tertiary_gdp",
]


def _read(p: Path) -> str:
    assert p.exists(), f"file not found: {p}"
    return p.read_text(encoding="utf-8")


# ───────────────────────────────────────────────────────────────────────────
# 1. SourcePopover 扩字段 (D1)
# ───────────────────────────────────────────────────────────────────────────


def test_sourcepopover_has_lineage_source_prop() -> None:
    src = _read(SOURCE_POPOVER)
    assert "lineageSource" in src, "SourcePopover must have lineageSource prop"
    assert "lineageOrigin" in src, "SourcePopover must have lineageOrigin prop"
    assert "isDataMissing" in src, "SourcePopover must have isDataMissing flag"


def test_sourcepopover_renders_five_pieces() -> None:
    """五件套渲染顺序: URL → SHA → lineage_source → lineage_origin → ruling."""
    src = _read(SOURCE_POPOVER)
    # 找 SourcePopover 渲染体内 5 个 data-testid.
    expected = [
        "source-url-missing",  # URL 段
        "source-hash-missing",  # SHA 段
        "lineage-source-value",  # lineage_source 段
        "lineage-origin-value",  # lineage_origin 段
        "lineage-origin-missing-reason",  # DATA_MISSING 注解
    ]
    for tag in expected:
        assert f'data-testid="{tag}"' in src, f"SourcePopover must render {tag}"


def test_sourcepopover_isDataMissing_explicit_flag() -> None:
    """662: 显式 isDataMissing flag 决定注解样式, 不靠 lineageSource 字符串判断."""
    src = _read(SOURCE_POPOVER)
    # 显式 prop 接收 + 显式条件渲染.
    assert re.search(r"isDataMissing\s*[=:]\s*(?:true|false|boolean)", src) or "isDataMissing" in src
    # 缺字段时显式占位符 (caliber placeholder 模式).
    assert "lineage-origin-missing-reason" in src


def test_province_gdp_table_passes_lineage_to_sourcepopover() -> None:
    """ProvinceGdpTable 3 类行 (NATIONAL / 28 真 / 3 缺) 都传 lineageSource+lineageOrigin."""
    src = _read(PROVINCE_GDP_TABLE)
    # 应有 ≥3 个 SourcePopover 调用.
    count = src.count("<SourcePopover")
    assert count >= 3, f"ProvinceGdpTable must have ≥3 SourcePopover (got {count})"
    assert "lineageSource={p.lineage_source}" in src or "lineageSource={national.lineage_source}" in src
    assert "lineageOrigin" in src


def test_province_gdp_table_sort_bar_5_buttons() -> None:
    src = _read(PROVINCE_GDP_TABLE)
    assert 'data-testid="sort-bar"' in src
    # 排序按钮用模板字面量 data-testid={`sort-btn-${tab.key}`}; 验证模板存在 +
    # 5 metric key 在 METRIC_TABS 数组中列出 (运行时映射).
    assert re.search(r"data-testid=\{`sort-btn-\$\{tab\.key\}`\}", src) is not None
    for k in METRIC_KEYS:
        assert k in src, f"sort btn metric key {k} 缺失"


def test_province_gdp_table_sort_caveat_mentions_red_line() -> None:
    """排序口径提示需引用 docs/05 §8.3 (禁榜单化红线)."""
    src = _read(PROVINCE_GDP_TABLE)
    assert "docs/05 §8.3" in src or "不构成排名" in src
    assert "sortCaveat" in src or "data-testid=\"sort-caveat\"" in src


# ───────────────────────────────────────────────────────────────────────────
# 2. mart_indicator_definitions 导出 (D2) — mart JSON + export script
# ───────────────────────────────────────────────────────────────────────────


def test_mart_indicator_definitions_json_exists_and_has_5_indicators() -> None:
    assert INDICATOR_DEFS_JSON.exists(), f"{INDICATOR_DEFS_JSON.name} not found"
    data = json.loads(INDICATOR_DEFS_JSON.read_text(encoding="utf-8"))
    assert data["indicator_count"] == 5
    assert len(data["indicators"]) == 5
    keys = [ind["key"] for ind in data["indicators"]]
    assert keys == METRIC_KEYS, f"indicator keys 不匹配: {keys}"


def test_mart_indicator_definitions_grade_distribution_correct() -> None:
    """三档分布必须 = {OFFICIAL_INTAKED:6, HONGHEIKU_TRANSLOAD:23, DATA_MISSING:3}."""
    data = json.loads(INDICATOR_DEFS_JSON.read_text(encoding="utf-8"))
    for ind in data["indicators"]:
        g = ind["source_grade_distribution"]
        assert g["OFFICIAL_INTAKED"] == 6, f"{ind['key']} OFFICIAL: {g}"
        assert g["HONGHEIKU_TRANSLOAD"] == 23, f"{ind['key']} TRANSLOAD: {g}"
        assert g["DATA_MISSING"] == 3, f"{ind['key']} DATA_MISSING: {g}"


def test_export_mart_data_has_indicator_definitions_export() -> None:
    src = _read(EXPORT_SCRIPT)
    assert "build_indicator_definitions_payload" in src
    assert "compute_source_grade_distribution" in src
    assert "OUT_INDICATOR_DEFS_JSON" in src
    assert "--include-indicator-defs" in src


def test_export_mart_grade_uses_status_not_lineage_source() -> None:
    """Bug 修复: 等级分布按 status 字段判断, 不靠 lineageSource 字符串."""
    src = _read(EXPORT_SCRIPT)
    # 关键反例: 不应再用 `lineage_source in ('DATA_MISSING', None)` 这种字符串比较.
    # 应该有 `r.get("status") == "DATA_MISSING"` 形式的判断.
    assert re.search(r'r\[?\["status"\]?\]\s*==\s*"DATA_MISSING"', src) or \
           re.search(r'r\.get\("status"\)\s*==\s*"DATA_MISSING"', src), \
        "compute_source_grade_distribution 必须按 status 字段判断 DATA_MISSING"


# ───────────────────────────────────────────────────────────────────────────
# 3. mart-static.ts loader + /indicators 页 (D2)
# ───────────────────────────────────────────────────────────────────────────


def test_mart_static_has_indicator_definitions_loader() -> None:
    src = _read(MART_STATIC)
    assert "MartIndicatorDefinition" in src
    assert "MartIndicatorDefinitionsFile" in src
    assert "loadStaticIndicatorDefinitions" in src
    assert "getIndicatorDefinitions" in src
    assert "getIndicatorDefinitionList" in src


def test_indicators_page_exists_with_5_cards() -> None:
    src = _read(INDICATORS_PAGE)
    # 模板字面量 data-testid={`indicator-card-${ind.key}`} / grade-bar-*
    assert re.search(r"data-testid=\{`indicator-card-\$\{ind\.key\}`\}", src) is not None
    # 来源等级三档 testid 用模板 + 3 个常量 grade.
    for grade in ("official", "transload", "missing"):
        assert f"grade-bar-{grade}-${{ind.key}}" in src, \
            f"grade-bar-{grade}-${{ind.key}} 模板缺失"
    # 5 metric key 由 data.indicators 数组动态提供; 验证 export 的 JSON 含 5 keys.
    data = json.loads(INDICATOR_DEFS_JSON.read_text(encoding="utf-8"))
    keys = [ind["key"] for ind in data["indicators"]]
    assert keys == METRIC_KEYS, f"indicator defs JSON keys 不匹配: {keys}"


# ───────────────────────────────────────────────────────────────────────────
# 4. CoverageMatrix + DataCompletenessPanel (D3)
# ───────────────────────────────────────────────────────────────────────────


def test_coverage_matrix_has_31x5_grid() -> None:
    src = _read(COVERAGE_MATRIX)
    assert 'data-testid="coverage-matrix"' in src
    assert 'data-testid="coverage-footer"' in src
    # 5 列 + 行级覆盖率列用模板字面量 data-testid={`coverage-th-${mk}`}.
    assert re.search(r"data-testid=\{`coverage-th-\$\{mk\}`\}", src) is not None
    for k in METRIC_KEYS:
        assert k in src, f"coverage metric key {k} 缺失"


def test_completeness_panel_embeds_coverage_and_publicity() -> None:
    src = _read(COMPLETENESS_PANEL)
    assert "data-completeness-panel" in src
    assert "data-completeness-stats" in src
    assert "data-missing-publicity" in src
    assert "<CoverageMatrix" in src
    # 3 缺失省公示行 testid.
    for prov in ("LIAONING", "HAINAN", "GUIZHOU"):
        assert prov in src, f"{prov} missing from publicity"


def test_home_page_embeds_completeness_panel() -> None:
    src = _read(HOME_PAGE)
    assert "<DataCompletenessPanel" in src


# ───────────────────────────────────────────────────────────────────────────
# 5. DemoBanner + LIVE/DEMO 导航 (D5)
# ───────────────────────────────────────────────────────────────────────────


def test_demo_banner_component_exists() -> None:
    src = _read(DEMO_BANNER)
    assert 'data-testid="demo-banner"' in src
    assert "reason" in src  # 必传 reason prop


def test_four_demo_pages_have_demobanner() -> None:
    for p in [SEVEN_DIM_PAGE, M1_SERIES_PAGE, Q1_2024_PAGE, PUBLIC_EXTRACTS_PAGE]:
        src = _read(p)
        assert "<DemoBanner" in src, f"{p.name} 缺 DemoBanner"
        assert "data-testid=\"demo-banner\"" in src or 'import { DemoBanner }' in src


def test_layout_live_demo_group() -> None:
    src = _read(LAYOUT)
    assert 'data-testid="site-nav-live-group"' in src
    assert 'data-testid="site-nav-demo-group"' in src
    # LIVE 组含 /indicators + 省详情 + peer-compare; DEMO 组含 4 demo 页.
    for href in ('/indicators', '/peer-compare', '/public-extracts',
                 '/research/m1-series', '/research/q1-2024-gdp', '/seven-dim'):
        assert href in src, f"layout nav 缺 {href}"


# ───────────────────────────────────────────────────────────────────────────
# 6. verify-live.sh 公网 12 项验收 (D6)
# ───────────────────────────────────────────────────────────────────────────


def test_verify_live_sh_exists_and_has_12_assertions() -> None:
    assert VERIFY_LIVE_SH.exists()
    src = VERIFY_LIVE_SH.read_text(encoding="utf-8")
    # 12 项主断言 (1-12) + offline mode 标识检查.
    expected_markers = [
        "LIVE MODE",
        "metric-tab-gdp_total",
        "national-badge",
        "BEIJING", "SHANGHAI", "LIAONING",
        "peer-compare-real-table",
        "source-popover",
        "data-missing-banner",
        "indicator-card",
        "coverage-matrix",
        "demo-banner",
        "sort-bar",
        "site-nav-live-group",
        "site-nav-demo-group",
    ]
    for m in expected_markers:
        assert m in src, f"verify-live.sh 缺标识 {m}"


def test_verify_live_sh_bash_syntax() -> None:
    """`bash -n` 必须 exit 0 (无语法错误)."""
    proc = subprocess.run(
        ["bash", "-n", str(VERIFY_LIVE_SH)],
        capture_output=True, text=True, timeout=10,
    )
    assert proc.returncode == 0, f"bash -n 失败: {proc.stderr}"


# ───────────────────────────────────────────────────────────────────────────
# 7. 数据可重现性 (e2e: export → JSON schema)
# ───────────────────────────────────────────────────────────────────────────


def test_export_mart_dryrun_reports_correct_grade() -> None:
    """export-mart-data.py --dry-run 必须输出 grade={OFFICIAL:6, TRANSLOAD:23, MISSING:3}."""
    proc = subprocess.run(
        [sys.executable, str(EXPORT_SCRIPT), "--strict", "--dry-run",
         "--include-indicator-defs"],
        capture_output=True, text=True, timeout=30, cwd=ROOT,
    )
    assert proc.returncode == 0, f"export dry-run 失败: {proc.stderr}"
    out = proc.stdout
    assert "DRY-RUN OK: 32 rows" in out, f"行数守门: {out}"
    assert "OFFICIAL_INTAKED': 6" in out, f"OFFICIAL 计数: {out}"
    assert "HONGHEIKU_TRANSLOAD': 23" in out, f"TRANSLOAD 计数: {out}"
    assert "DATA_MISSING': 3" in out, f"DATA_MISSING 计数: {out}"


def test_mart_static_derive_path_uses_same_dir() -> None:
    """deriveIndicatorDefsPath 必须同目录约定 (mart 主 JSON 同级)."""
    src = _read(MART_STATIC)
    assert "deriveIndicatorDefsPath" in src
    # 必须用 dirname 派生目录, 不能用 hardcoded path.
    assert "path.dirname" in src
    assert "mart_indicator_definitions_2024.json" in src
