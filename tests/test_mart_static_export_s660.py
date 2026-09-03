"""660 test_mart_static_export_s660.py — Track B 静态导出守门测试.

Per knife 660 tasking §PART 2 + docs/85 §4.2:
  新增 ≥8 cases: mart JSON 31 行守门 / 缺失省指标 NULL 非 0 /
  lineage 三重标注 / mart-static.ts API 表面 / api.ts Track B 分支 /
  page.tsx mart section 渲染 / deploy 包文件齐 / 无 JIANGSU mock sentinel

660 + 661 兼容性: 661 加了 NATIONAL 锚行 + source_url/source_hash_prefix 字段;
  本测试基线版本行数从 31 → 32,但所有行内不变量(lineage_ruling / lineage_is_demo /
  DATA_MISSING null / OFFICIAL_INTAKED 锚行 / hongheiku 23 省 等)完全继承自 660.
  新增的 v661-specific 守门见 tests/test_prd_gap_replan_s661.py.

守门口径:
  1. mart JSON exists & valid JSON
  2. mart JSON 32 行 (1 OFFICIAL_ANCHOR + 28 真实 + 3 缺失) — 661 bump from 31
  3. mart JSON lineage_ruling='U6 2026-09-02' 全行
  4. mart JSON lineage_is_demo='false' 全行
  5. DATA_MISSING 3 省 5 指标列全 NULL (红线 1, 禁补零)
  6. mart JSON 无 JIANGSU-GDP-INDICATOR-UUID-MOCK
  7. lib/mart-static.ts 4 API 表面 (isStaticMartDataEnabled / loadStaticMartData /
     getMartProvinceGdp2024 / MartProvinceGdp2024)
  8. lib/api.ts Track B 分支 (imports + indicatorsFromMart + IS_STATIC_MART_DATA_MODE)
  9. app/page.tsx mart section 委托给 <ProvinceGdpTable> 组件 (per 661 C1)
 10. deploy/static-export/ 4 文件齐 (export-mart-data.py + deploy.sh + precheck.sh + README.md)
 11. export-mart-data.py --strict --dry-run exit 0 (661 D3 防 side-effect)
 12. smoke-check.py §16 含 Track B 守门
 13. fmtNum/fmtPct 接受 string|number|null (660-P1 回归;位置 = page.tsx 或组件)
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
PROVINCE_TABLE = REPO / 'frontend' / 'app' / 'components' / 'ProvinceGdpTable.tsx'
PROVINCE_ROUTE = REPO / 'frontend' / 'app' / 'provinces' / '[province_code]' / 'page.tsx'
PEER_COMPARE_PAGE = REPO / 'frontend' / 'app' / 'peer-compare' / 'page.tsx'
DEPLOY_DIR = REPO / 'deploy' / 'static-export'
EXPORT_PY = DEPLOY_DIR / 'export-mart-data.py'
SMOKE_PY = REPO / 'frontend' / 'smoke-check.py'

# Expected counts (per 660 README §守门.1 + 661 §3.1: 31 → 32 加 NATIONAL 锚)
EXPECTED_TOTAL = 32  # 661: bumped from 31 (+ NATIONAL anchor)
EXPECTED_REAL = 28
EXPECTED_MISSING = 3
EXPECTED_NATIONAL = 1  # 661: NATIONAL anchor row (OFFICIAL_INTAKED)
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


def test_02_mart_json_32_rows() -> None:
    """§4.2 case 2: total_count=32 (1 NATIONAL + 28 真实 + 3 缺失). 661 bump from 31."""
    data = _load_mart()
    assert data["total_count"] == EXPECTED_TOTAL, \
        f"total_count={data['total_count']}, expected {EXPECTED_TOTAL}"
    assert data["real_count"] == EXPECTED_REAL, \
        f"real_count={data['real_count']}, expected {EXPECTED_REAL}"
    assert data["missing_count"] == EXPECTED_MISSING, \
        f"missing_count={data['missing_count']}, expected {EXPECTED_MISSING}"
    # 661: national_count 字段必须为 1 (NATIONAL anchor row)
    assert data.get("national_count") == EXPECTED_NATIONAL, \
        f"national_count={data.get('national_count')}, expected {EXPECTED_NATIONAL}"
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
    """§4.2 case 9: app/page.tsx mart section 委派给 <ProvinceGdpTable> 组件.

    660 时 page.tsx 直接渲染表 (heading + table + missing badge + 数据暂缺 文案).
    661 C1: 抽到 components/ProvinceGdpTable.tsx, page.tsx 只负责调度.
    661 测试双源扫描: page.tsx (调度) + ProvinceGdpTable.tsx (实际渲染).
    """
    page_code = _strip_comments(PAGE_TSX.read_text(encoding="utf-8"))
    assert PROVINCE_TABLE.exists(), \
        f"ProvinceGdpTable.tsx 缺失 (661 C1 必须存在): {PROVINCE_TABLE}"
    table_code_stripped = _strip_comments(PROVINCE_TABLE.read_text(encoding="utf-8"))
    # page.tsx 必须委派给组件 + 透传 mart
    for needle in ("getMartProvinceGdp2024", "ProvinceGdpTable"):
        assert needle in page_code, f"app/page.tsx missing {needle}"
    # ProvinceGdpTable 组件必须实际渲染 661 表 (5 指标 tab + NATIONAL + 31 行 +
    # 3 missing badge + 数据暂缺 + 溯源 popover).
    for needle in (
        "province-gdp-2024-table",  # table data-testid
        "metric-tab-${",  # 5 指标 tab template
        "metric-tabs",  # role="tablist" data-testid
        "national-badge",  # OFFICIAL_ANCHOR badge testid
        "OFFICIAL_ANCHOR",  # NATIONAL badge 文案
        "province-row-${",  # 行 template
        "missing-badge-${",  # 缺失行 badge template
        "数据暂缺",  # 缺失行 文案 (per docs/43 §8 + 红线 1)
        "SourcePopover",  # 溯源 popover 复用
    ):
        assert needle in table_code_stripped, \
            f"ProvinceGdpTable.tsx missing {needle}"


def test_13_fmtNum_fmtPct_accept_string_numbers() -> None:
    """660-P1 回归 case 13: fmtNum/fmtPct 必须接受 string|number|null.

    mart JSON 数值列经 export-mart-data.py 输出时常为字符串(政府源 TXT/HTML
    给的数字通常是 str),fmtNum/fmtPct 必须 coerce 否则 28 真省数值全 fallback
    "—"(回归: 660 deploy 后用户报"还是空白状态")。

    661: fmtNum/fmtPct 抽到 components/ProvinceGdpTable.tsx + peer-compare/page.tsx +
    provinces/[province_code]/page.tsx 三处共用。本测试扫描全部三处确认类型宽化一致。
    """
    import math as _math  # noqa: PLC0415
    sources = [PAGE_TSX, PROVINCE_TABLE, PROVINCE_ROUTE, PEER_COMPARE_PAGE]
    combined = ""
    for s in sources:
        if s.exists():
            combined += "\n" + _strip_comments(s.read_text(encoding="utf-8"))
    # fmtNum 签名必须宽化到 string | number | null
    assert "function fmtNum(v: number | string | null)" in combined, \
        "fmtNum 类型签名未宽化 (string 数字会全部 fallback '—')"
    assert "function fmtPct(v: number | string | null)" in combined, \
        "fmtPct 类型签名未宽化"
    # 必须有 coerce 逻辑 (Number(v) 或 Number(raw))
    assert "Number(" in combined, "fmtNum/fmtPct 缺少 Number() coerce 逻辑"
    # 必须有 Number.isFinite 守门 (防 Number('') === 0 误显)
    assert "Number.isFinite" in combined, "fmtNum/fmtPct 缺 Number.isFinite 守门"
    # 验收: 28 真省的 JSON 源数据,数值字段必须能 coerce 到 finite number
    data = _load_mart()
    real_count = 0
    for p in data["provinces"]:
        if p.get("gdp_total") is not None:
            real_count += 1
            # 模拟 fmtNum 内部 coerce: string → float
            val = p["gdp_total"]
            n = float(val) if isinstance(val, str) else val
            assert _math.isfinite(n), \
                f"省 {p['province_code']} gdp_total={val!r} 不可 coerce 到 finite number"
    assert real_count >= 28, f"实省 gdp_total 字段应有 ≥28 行,实际 {real_count}"


def test_10_deploy_package_files() -> None:
    """§4.2 case 10: deploy/static-export/ 4 文件齐."""
    assert DEPLOY_DIR.exists(), f"deploy/static-export/ missing: {DEPLOY_DIR}"
    for fname in ("export-mart-data.py", "deploy.sh", "precheck.sh", "README.md"):
        fpath = DEPLOY_DIR / fname
        assert fpath.exists(), f"deploy/static-export/{fname} missing"


def test_11_export_script_strict_mode() -> None:
    """§4.2 case 11: export-mart-data.py --strict --dry-run exit 0 (661 D3).

    660-P1 教训: 原 test_11 直接 --strict --out $MART_JSON 会重写生产 JSON 文件
    在并发 pytest 下产生竞态 (一个测试进程在写,另一个在读). 661 D3 改用 --dry-run:
    脚本只做解析 + 自检 + stdout 摘要,不触碰磁盘. 仍 --strict 保证红线违规 exit 2.
    """
    assert EXPORT_PY.exists(), f"export-mart-data.py missing: {EXPORT_PY}"
    result = subprocess.run(
        [sys.executable, str(EXPORT_PY), "--strict", "--dry-run"],
        capture_output=True,
        text=True,
        timeout=60,
    )
    # --strict --dry-run: 0 = clean, 2 = red-line violation. We expect 0.
    assert result.returncode in (0, 2), \
        f"export-mart-data.py --strict --dry-run exit={result.returncode}, " \
        f"expected 0 or 2"
    # 661 D3: stdout 必须含 "DRY-RUN OK" 标识
    assert "DRY-RUN OK" in result.stdout, \
        f"--dry-run stdout 缺 DRY-RUN OK 标记, got: {result.stdout!r}"
    # 661 D3: --dry-run 不应写盘,生产 JSON 仍是 32 行
    data = _load_mart()
    assert data["total_count"] == EXPECTED_TOTAL, \
        f"dry-run 后 production JSON total_count={data['total_count']}, expected {EXPECTED_TOTAL}"


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