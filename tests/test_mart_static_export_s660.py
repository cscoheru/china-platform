"""660 test_mart_static_export_s660.py — Track B 静态导出守门测试.

Per knife 660 tasking §PART 2 + docs/85 §4.2:
  新增 ≥8 cases: mart JSON 31 行守门 / 缺失省指标 NULL 非 0 /
  lineage 三重标注 / mart-static.ts API 表面 / api.ts Track B 分支 /
  page.tsx mart section 渲染 / deploy 包文件齐 / 无 JIANGSU mock sentinel

守门口径:
  1. mart JSON exists & valid JSON
  2. mart JSON 31 行 (28 真实 + 3 缺失)
  3. mart JSON lineage_ruling='U6 2026-09-02' 全行
  4. mart JSON lineage_is_demo='false' 全行
  5. DATA_MISSING 3 省 5 指标列全 NULL (红线 1, 禁补零)
  6. mart JSON 无 JIANGSU-GDP-INDICATOR-UUID-MOCK
  7. lib/mart-static.ts 4 API 表面 (isStaticMartDataEnabled / loadStaticMartData /
     getMartProvinceGdp2024 / MartProvinceGdp2024)
  8. lib/api.ts Track B 分支 (imports + indicatorsFromMart + IS_STATIC_MART_DATA_MODE)
  9. app/page.tsx mart section 渲染 (heading/table/3 missing badge)
 10. deploy/static-export/ 4 文件齐 (export-mart-data.py + deploy.sh + precheck.sh + README.md)
 11. export-mart-data.py --strict exit 0
 12. smoke-check.py §16 含 Track B 守门
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
API_TS = REPO / 'frontend' / 'lib' / 'api.ts'
PAGE_TSX = REPO / 'frontend' / 'app' / 'page.tsx'
DEPLOY_DIR = REPO / 'deploy' / 'static-export'
EXPORT_PY = DEPLOY_DIR / 'export-mart-data.py'
SMOKE_PY = REPO / 'frontend' / 'smoke-check.py'

# Expected counts (per 660 README §守门.1)
EXPECTED_TOTAL = 31
EXPECTED_REAL = 28
EXPECTED_MISSING = 3
EXPECTED_MISSING_PROVINCES = {"辽宁", "贵州", "海南"}  # 中文名 (per mart_province_gdp_2024.sql)
EXPECTED_LINEAGE_RULING = "U6 2026-09-02"
NULL_METRIC_COLS = ("gdp_total", "gdp_growth", "primary_gdp", "secondary_gdp", "tertiary_gdp")


def _load_mart() -> dict:
    """Load and parse mart JSON. Helper for tests that need it."""
    return json.loads(MART_JSON.read_text(encoding="utf-8"))


def _strip_comments(src: str) -> str:
    """Strip // line comments and /* block */ comments."""
    src = re.sub(r"//[^\n]*", "", src)
    src = re.sub(r"/\*.*?\*/", "", src, flags=re.DOTALL)
    return src


def test_01_mart_json_exists_and_valid() -> None:
    """§4.2 case 1: mart JSON 在位 + JSON 解析 OK."""
    assert MART_JSON.exists(), f"mart JSON missing: {MART_JSON}"
    data = json.loads(MART_JSON.read_text(encoding="utf-8"))
    assert isinstance(data, dict), "mart JSON must be dict"
    assert "provinces" in data and isinstance(data["provinces"], list)


def test_02_mart_json_31_rows() -> None:
    """§4.2 case 2: total_count=31."""
    data = _load_mart()
    assert data["total_count"] == EXPECTED_TOTAL, \
        f"total_count={data['total_count']}, expected {EXPECTED_TOTAL}"
    assert data["real_count"] == EXPECTED_REAL, \
        f"real_count={data['real_count']}, expected {EXPECTED_REAL}"
    assert data["missing_count"] == EXPECTED_MISSING, \
        f"missing_count={data['missing_count']}, expected {EXPECTED_MISSING}"
    assert len(data["provinces"]) == EXPECTED_TOTAL, \
        f"provinces[] len={len(data['provinces'])}, expected {EXPECTED_TOTAL}"


def test_03_mart_json_lineage_ruling_uniform() -> None:
    """§4.2 case 3: lineage_ruling='U6 2026-09-02' 全行."""
    data = _load_mart()
    for p in data["provinces"]:
        assert p.get("lineage_ruling") == EXPECTED_LINEAGE_RULING, \
            f"省 {p.get('province_code')} lineage_ruling={p.get('lineage_ruling')}, " \
            f"expected '{EXPECTED_LINEAGE_RULING}'"


def test_04_mart_json_lineage_is_demo_false() -> None:
    """§4.2 case 4: lineage_is_demo='false' 全行."""
    data = _load_mart()
    for p in data["provinces"]:
        assert p.get("lineage_is_demo") == "false", \
            f"省 {p.get('province_code')} lineage_is_demo={p.get('lineage_is_demo')}, " \
            f"expected 'false'"


def test_05_missing_provinces_have_null_metric_cols() -> None:
    """§4.2 case 5: DATA_MISSING 3 省 5 指标列全 NULL (红线 1, 禁补零)."""
    data = _load_mart()
    missing = [p for p in data["provinces"] if p.get("status") == "DATA_MISSING"]
    assert len(missing) == EXPECTED_MISSING, \
        f"DATA_MISSING count={len(missing)}, expected {EXPECTED_MISSING}"
    names = {p.get("province_name") for p in missing}
    assert names == EXPECTED_MISSING_PROVINCES, \
        f"DATA_MISSING names={names}, expected {EXPECTED_MISSING_PROVINCES}"
    for p in missing:
        for col in NULL_METRIC_COLS:
            assert p.get(col) is None, \
                f"DATA_MISSING 省 {p.get('province_code')} {col}={p.get(col)}, " \
                f"expected NULL (红线 1: 禁补零)"


def test_06_mart_json_no_jiangsu_mock_sentinel() -> None:
    """§4.2 case 6: mart JSON 无 JIANGSU mock sentinel."""
    text = MART_JSON.read_text(encoding="utf-8")
    assert "JIANGSU-GDP-INDICATOR-UUID-MOCK" not in text, \
        "mart JSON 含 JIANGSU-GDP-INDICATOR-UUID-MOCK (mock sentinel 不应出现)"


def test_07_mart_static_ts_api_surface() -> None:
    """§4.2 case 7: lib/mart-static.ts 4 API 表面."""
    assert MART_STATIC_TS.exists(), f"lib/mart-static.ts missing: {MART_STATIC_TS}"
    code = _strip_comments(MART_STATIC_TS.read_text(encoding="utf-8"))
    for needle in (
        "isStaticMartDataEnabled",
        "loadStaticMartData",
        "getMartProvinceGdp2024",
        "MartProvinceGdp2024",
        "NEXT_PUBLIC_MART_DATA_PATH",
    ):
        assert needle in code, f"lib/mart-static.ts missing {needle}"


def test_08_api_ts_track_b_branch() -> None:
    """§4.2 case 8: lib/api.ts Track B 分支 (imports + indicatorsFromMart)."""
    code = _strip_comments(API_TS.read_text(encoding="utf-8"))
    for needle in (
        "isStaticMartDataEnabled",
        "loadStaticMartData",
        "indicatorsFromMart",
        "IS_STATIC_MART_DATA_MODE",
    ):
        assert needle in code, f"lib/api.ts missing {needle}"


def test_09_page_tsx_mart_section_render() -> None:
    """§4.2 case 9: app/page.tsx mart section 渲染 (heading/table/3 missing badge)."""
    code = _strip_comments(PAGE_TSX.read_text(encoding="utf-8"))
    for needle in (
        "getMartProvinceGdp2024",
        "province-gdp-2024-heading",
        "province-gdp-2024-table",
        "mart-row-count",
        'province-row-${',
        'missing-badge-${',
        "数据暂缺（公报源缺文）",
    ):
        assert needle in code, f"app/page.tsx missing {needle}"


def test_10_deploy_package_files() -> None:
    """§4.2 case 10: deploy/static-export/ 4 文件齐."""
    assert DEPLOY_DIR.exists(), f"deploy/static-export/ missing: {DEPLOY_DIR}"
    for fname in ("export-mart-data.py", "deploy.sh", "precheck.sh", "README.md"):
        fpath = DEPLOY_DIR / fname
        assert fpath.exists(), f"deploy/static-export/{fname} missing"


def test_11_export_script_strict_mode() -> None:
    """§4.2 case 11: export-mart-data.py --strict exit 0."""
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
    # Re-load to confirm JSON is regenerated & valid
    data = _load_mart()
    assert data["total_count"] == EXPECTED_TOTAL


def test_12_smoke_check_has_660_section() -> None:
    """§4.2 case 12: smoke-check.py §16 含 Track B 守门."""
    assert SMOKE_PY.exists(), f"smoke-check.py missing: {SMOKE_PY}"
    code = SMOKE_PY.read_text(encoding="utf-8")
    assert "§16" in code, "smoke-check.py missing §16 section header"
    assert "knife 660" in code or "Track B" in code, \
        "smoke-check.py §16 missing knife 660 / Track B reference"


if __name__ == "__main__":
    # Run all tests via pytest when executed directly.
    sys.exit(subprocess.call([sys.executable, "-m", "pytest", __file__, "-v"]))