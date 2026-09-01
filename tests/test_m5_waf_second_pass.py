"""Tests for knife 643 M5 WAF 网防G01 spike 二次 (≥7 cases).

Per tasking 643 §B.1:
- probe 报告存在 + 顶层裁定 (MIXED/BLOCKED/PARTIAL/REACHABLE) + 10 cells 实测
- evidence JSON parses + probed_count=10 + http_count ≤ 10
- 4 替代 subpath 路径别名深挖 ≥ 1 REACHABLE
- 国务院 /zhengceku/ + /zhengce/content/ 403 WAF 网防G01 marker 真出现
- docs/64 §1-§6 架构师级审查 + 不宣称 PASS
- probe 脚本幂等 (no time.sleep / no random)

All tests are read-only (no DB / no network).
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))

DOC_64 = REPO_ROOT / "docs" / "64-m5-waf-second-pass-20260901.md"
REPORT_MD = REPO_ROOT / "docs" / "reports" / "m5_waf_v2_probe_20260901.md"
EVIDENCE_JSON = REPO_ROOT / "evidence_pack" / "m5_waf_v2_probe_20260901.json"
PROBE_SCRIPT = REPO_ROOT / "scripts" / "probe_m5_waf_v2_2024.py"


def test_m5_v2_probe_report_exists_and_has_top_verdict():
    """643-A.1 probe 报告存在 + 顶层裁定 + 10 cells 实测."""
    assert REPORT_MD.exists(), f"M5 v2 probe markdown missing: {REPORT_MD}"
    text = REPORT_MD.read_text(encoding="utf-8")
    assert "## 0. 顶层裁定" in text
    top_match = re.search(r"\*\*(BLOCKED|PARTIAL|REACHABLE|MIXED)\*\*", text)
    assert top_match, "M5 v2 probe report missing top verdict"
    # 实体逐项
    assert "实体逐项" in text or "cells 实测" in text
    # 10 cells ≤10 HTTP
    assert "10 cells 实测" in text or "10 URL" in text


def test_m5_v2_evidence_json_parses_and_http_count():
    """643-A.1 evidence JSON parses + probed_count=10 + http_count ≤ 10."""
    assert EVIDENCE_JSON.exists(), f"M5 v2 evidence JSON missing: {EVIDENCE_JSON}"
    data = json.loads(EVIDENCE_JSON.read_text(encoding="utf-8"))
    assert "summary" in data
    assert "cells" in data
    assert "fetch_log" in data
    sv = data["summary"]
    assert sv["probed_count"] == 10, (
        f"probed_count = {sv['probed_count']}, expected 10"
    )
    # ≤10 HTTP 红线
    assert sv["http_count"] <= 10, (
        f"http_count = {sv['http_count']}, exceeds ≤ 10 红线"
    )
    # top_verdict in {BLOCKED, PARTIAL, REACHABLE, MIXED}
    assert sv["top_verdict"] in ("BLOCKED", "PARTIAL", "REACHABLE", "MIXED"), (
        f"top_verdict = {sv['top_verdict']}, expected one of "
        f"BLOCKED/PARTIAL/REACHABLE/MIXED"
    )
    # 10 cells
    assert len(data["cells"]) == 10, f"cells count = {len(data['cells'])}, expected 10"


def test_m5_v2_alternate_subpaths_reachable_or_blocked():
    """643-A.1 4 替代 subpath 路径别名深挖 至少 1 REACHABLE (henan /zwgk/zfgb/) ."""
    assert EVIDENCE_JSON.exists()
    data = json.loads(EVIDENCE_JSON.read_text(encoding="utf-8"))
    # 4 替代 subpath: alt_zfgb / alt_zcwj / alt_szfwj / alt_wjzl
    alt_subpath_slots = {"alt_zfgb", "alt_zcwj", "alt_szfwj", "alt_wjzl"}
    alt_cells = [c for c in data["cells"] if c["slot"] in alt_subpath_slots]
    assert len(alt_cells) >= 4, (
        f"alt_subpath cells = {len(alt_cells)}, expected ≥ 4"
    )
    # 至少 1 REACHABLE (架构师假设: henan /zwgk/zfgb/ 应 200 OK)
    reachable_alt = [c for c in alt_cells if c["verdict"] == "REACHABLE"]
    assert len(reachable_alt) >= 1, (
        f"alt_subpath REACHABLE count = {len(reachable_alt)}, expected ≥ 1 "
        f"(架构师假设: 路径别名深挖至少 1 REACHABLE)"
    )
    # 至少 1 BLOCKED 路径别名 (4 BLOCKED 省 zfgb/zcwj/szfwj/wjzl)
    blocked_alt = [c for c in alt_cells if c["verdict"] == "BLOCKED"]
    assert len(blocked_alt) >= 1, (
        f"alt_subpath BLOCKED count = {len(blocked_alt)}, expected ≥ 1 "
        f"(路径别名 ≠ WAF)"
    )


def test_m5_v2_gov_zhengce_waf_marker_confirmed():
    """643-A.1 国务院 /zhengceku/ + /zhengce/content/ 403 WAF 网防G01 marker 真出现."""
    assert EVIDENCE_JSON.exists()
    data = json.loads(EVIDENCE_JSON.read_text(encoding="utf-8"))
    # 国务院 403 WAF cells (含 zhengceku / zhengce/content / zwgk 子路径)
    gov_waf_cells = [
        c for c in data["cells"]
        if c["province"] == "gov"
        and c["http_code"] == 403
        and c["waf_g01_marker"] is True
    ]
    assert len(gov_waf_cells) >= 1, (
        f"国务院 403 WAF 网防G01 marker cells = {len(gov_waf_cells)}, expected ≥ 1 "
        f"(沿用 642 /zhengce/content/ + /zwgk/ 模式 + 643 新增 /zhengceku/)"
    )


def test_m5_v2_henan_zfgb_reachable():
    """643-A.1 河南 /zwgk/zfgb/ REACHABLE 200 (路径别名 zfwj 但 zfgb 可达)."""
    assert EVIDENCE_JSON.exists()
    data = json.loads(EVIDENCE_JSON.read_text(encoding="utf-8"))
    henan_zfgb = [
        c for c in data["cells"]
        if c["province"] == "henan" and c["slot"] == "alt_zfgb"
    ]
    assert len(henan_zfgb) == 1, "henan /zwgk/zfgb/ cell not found"
    cell = henan_zfgb[0]
    assert cell["http_code"] == 200, (
        f"henan /zwgk/zfgb/ http_code = {cell['http_code']}, expected 200"
    )
    assert cell["verdict"] == "REACHABLE", (
        f"henan /zwgk/zfgb/ verdict = {cell['verdict']}, expected REACHABLE"
    )
    # 不带 WAF marker (不是 WAF 拦截)
    assert cell["waf_g01_marker"] is False


def test_m5_v2_gov_zhengce_root_reachable():
    """643-A.1 国务院 /zhengce/ root REACHABLE 200 (WAF selective 验证)."""
    assert EVIDENCE_JSON.exists()
    data = json.loads(EVIDENCE_JSON.read_text(encoding="utf-8"))
    gov_zhengce_root = [
        c for c in data["cells"]
        if c["province"] == "gov" and c["slot"] == "fallback_root"
    ]
    assert len(gov_zhengce_root) == 1, "gov /zhengce/ root cell not found"
    cell = gov_zhengce_root[0]
    assert cell["http_code"] == 200, (
        f"gov /zhengce/ root http_code = {cell['http_code']}, expected 200"
    )
    assert cell["verdict"] == "REACHABLE", (
        f"gov /zhengce/ root verdict = {cell['verdict']}, expected REACHABLE"
    )
    # root 不带 WAF marker (WAF 是 selective, 仅子路径被拦截)
    assert cell["waf_g01_marker"] is False


def test_doc_64_has_six_sections():
    """643-A.1 docs/64 含 ## 1.-## 6. 六段 + 标头属性."""
    assert DOC_64.exists(), f"docs/64 missing: {DOC_64}"
    text = DOC_64.read_text(encoding="utf-8")
    for n in ("## 1.", "## 2.", "## 3.", "## 4.", "## 5.", "## 6."):
        assert n in text, f"docs/64 missing section {n}"
    # 标头属性
    assert "64" in text[:200]
    assert "2026-09-01" in text
    assert "643" in text
    # M5 关键要素
    assert "WAF" in text or "网防G01" in text
    assert "MIXED" in text or "BLOCKED" in text or "REACHABLE" in text
    assert "路径别名" in text or "path alias" in text


def test_doc_64_no_pass_announcement():
    """643-A.1 docs/64 不宣称 M2/M4/Gate PASS (智能排除 disclaimer 否定句)."""
    assert DOC_64.exists()
    text = DOC_64.read_text(encoding="utf-8")
    sec6 = text[text.index("## 6."):]
    for keyword in ("M4 PASS", "M5 PASS", "Gate PASS", "M2 PASS"):
        positive_lines = [
            line for line in sec6.splitlines()
            if keyword in line and "不宣布" not in line
            and "不声称" not in line and "不宣称" not in line
            and "不宣告" not in line
        ]
        assert not positive_lines, (
            f"docs/64 §6 contains positive {keyword} claim: "
            f"{positive_lines!r}"
        )


def test_m5_v2_probe_script_idempotent():
    """643-A.1 probe 脚本幂等 (去 docstring + # 注释后扫: no sleeps / no randomness)."""
    assert PROBE_SCRIPT.exists()
    text = PROBE_SCRIPT.read_text(encoding="utf-8")
    # 去 docstring + 注释
    text_no_docstring = re.sub(r'"""[\s\S]*?"""', "", text)
    text_no_comments = re.sub(r"#[^\n]*", "", text_no_docstring)
    forbidden = [
        "time.sleep", "random.random", "random.choice", "random.shuffle",
        "random.seed", "datetime.now",
    ]
    for f in forbidden:
        assert f not in text_no_comments, (
            f"probe_m5_waf_v2_2024.py contains non-idempotent call {f!r}"
        )
    # HTTP_LIMIT = 10 必须出现 (硬性上限)
    assert "HTTP_LIMIT = 10" in text or "HTTP_LIMIT=10" in text, (
        "probe script missing HTTP_LIMIT = 10 (硬性红线)"
    )