"""Tests for knife 642 M5 WAF 网防G01 假设验证 spike (≥6 cases).

Per tasking 642 §B:
- probe 报告存在 + 顶层裁定 (MIXED/BLOCKED/PARTIAL/REACHABLE)
- evidence JSON parses + probed_count = 10 + http_count ≤ 10
- WAF 网防G01 假设验证 (5 BLOCKED 省 404 + 国务院 zhengceku 403)
- 替代路径 verdict (国务院 /zwgk/ + 福建/河南 /zwgk/ REACHABLE)
- docs/62 六段 + 不宣称 PASS
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

DOC_62 = REPO_ROOT / "docs" / "62-m5-waf-spike-20260901.md"
REPORT_MD = REPO_ROOT / "docs" / "reports" / "m5_waf_v1_probe_20260901.md"
EVIDENCE_JSON = REPO_ROOT / "evidence_pack" / "m5_waf_v1_probe_20260901.json"
PROBE_SCRIPT = REPO_ROOT / "scripts" / "probe_m5_waf_v1_2024.py"


def test_m5_waf_probe_report_exists_and_has_top_verdict():
    """642-A.1 probe 报告存在 + 顶层裁定 (MIXED/BLOCKED/PARTIAL/REACHABLE)."""
    assert REPORT_MD.exists(), f"M5 probe markdown missing: {REPORT_MD}"
    text = REPORT_MD.read_text(encoding="utf-8")
    assert "## 0. 顶层裁定" in text
    # 顶层裁定必须为 BLOCKED/PARTIAL/REACHABLE/MIXED 之一
    top_match = re.search(r"\*\*(BLOCKED|PARTIAL|REACHABLE|MIXED)\*\*", text)
    assert top_match, "M5 probe report missing top verdict"
    # 实体逐项
    assert "实体逐项" in text or "cells 实测" in text
    # 10 cells ≤10 HTTP
    assert "10 cells 实测" in text or "10 URL" in text


def test_m5_waf_evidence_json_parses_and_http_count():
    """642-A.1 evidence JSON parses + probed_count=10 + http_count ≤ 10."""
    assert EVIDENCE_JSON.exists(), f"M5 probe evidence JSON missing: {EVIDENCE_JSON}"
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


def test_m5_waf_blocked_5_zfwj_404_not_waf():
    """5 BLOCKED 省 /zwgk/zfwj/ 实测 404 (路径别名而非 WAF)."""
    assert EVIDENCE_JSON.exists()
    data = json.loads(EVIDENCE_JSON.read_text(encoding="utf-8"))
    # 5 试点省 zfwj 404 BLOCKED
    zfwj_cells = [
        c for c in data["cells"]
        if c["slot"] == "zfwj_404"
    ]
    assert len(zfwj_cells) == 5, (
        f"zfwj_404 cells = {len(zfwj_cells)}, expected 5"
    )
    for c in zfwj_cells:
        assert c["http_code"] == 404, (
            f"{c['province']} /zwgk/zfwj/ http_code = {c['http_code']}, "
            f"expected 404 (path alias not WAF)"
        )
        assert c["verdict"] == "BLOCKED"
        # 5 BLOCKED 省 zfwj 不带 waf_g01_marker (是路径不存在而非 WAF 网防G01)
        assert c["waf_g01_marker"] is False, (
            f"{c['province']} /zwgk/zfwj/ should not have WAF 网防G01 marker "
            f"(it's a 404 path alias, not WAF block)"
        )


def test_m5_waf_gov_zhengce_waf_marker_true():
    """国务院 /zhengce/content/ + /zwgk/ 403 WAF 网防G01 marker 验证."""
    assert EVIDENCE_JSON.exists()
    data = json.loads(EVIDENCE_JSON.read_text(encoding="utf-8"))
    gov_waf_cells = [
        c for c in data["cells"]
        if c["province"] == "gov"
        and c["http_code"] == 403
    ]
    assert len(gov_waf_cells) >= 2, (
        f"gov 403 WAF cells = {len(gov_waf_cells)}, expected ≥ 2 "
        f"(/zhengce/content/ + /zwgk/)"
    )
    for c in gov_waf_cells:
        assert c["verdict"] == "BLOCKED"
        assert c["waf_g01_marker"] is True, (
            f"{c['url']} should have WAF 网防G01 marker "
            f"(real WAF block, not path alias)"
        )


def test_m5_waf_2_reachable_zwgk():
    """福建 / 河南 /zwgk/ 200 REACHABLE (任免 landing 真实可达)."""
    assert EVIDENCE_JSON.exists()
    data = json.loads(EVIDENCE_JSON.read_text(encoding="utf-8"))
    reachable_cells = [
        c for c in data["cells"]
        if c["slot"] == "zwgk_renmian"
    ]
    assert len(reachable_cells) == 2, (
        f"zwgk_renmian cells = {len(reachable_cells)}, expected 2"
    )
    for c in reachable_cells:
        assert c["http_code"] == 200, (
            f"{c['province']} /zwgk/ http_code = {c['http_code']}, expected 200"
        )
        assert c["verdict"] == "REACHABLE"
        assert c["waf_g01_marker"] is False


def test_doc_62_has_six_sections():
    """docs/62 含 ## 1.-## 6. 六段 + 标头属性."""
    assert DOC_62.exists(), f"docs/62 missing: {DOC_62}"
    text = DOC_62.read_text(encoding="utf-8")
    for n in ("## 1.", "## 2.", "## 3.", "## 4.", "## 5.", "## 6."):
        assert n in text, f"docs/62 missing section {n}"
    # 标头属性
    assert "62" in text[:200]
    assert "2026-09-01" in text
    assert "642" in text
    # 5 BLOCKED 省根因 + WAF 网防G01 修正
    assert "5 BLOCKED" in text or "5 省" in text
    assert "WAF" in text


def test_doc_62_no_pass_announcement():
    """docs/62 不宣称 M2/M4/Gate PASS (智能排除 disclaimer 否定句)."""
    assert DOC_62.exists()
    text = DOC_62.read_text(encoding="utf-8")
    sec6 = text[text.index("## 6."):]
    for keyword in ("M4 PASS", "Gate PASS", "M2 PASS"):
        positive_lines = [
            line for line in sec6.splitlines()
            if keyword in line and "不宣布" not in line
            and "不声称" not in line and "不宣称" not in line
            and "不宣告" not in line
        ]
        assert not positive_lines, (
            f"docs/62 §6 contains positive {keyword} claim: "
            f"{positive_lines!r}"
        )


def test_m5_waf_probe_script_idempotent():
    """642-A.1 probe 脚本幂等 (no time.sleep / no random).

    文档字符串 + 注释会被忽略;只扫可执行代码.
    """
    assert PROBE_SCRIPT.exists()
    text = PROBE_SCRIPT.read_text(encoding="utf-8")
    # 去掉 docstring + 行注释 + 块注释;扫可执行代码
    code = re.sub(r'"""[\s\S]*?"""', "", text)
    code = re.sub(r"#[^\n]*", "", code)
    # 不允许 time.sleep
    assert "time.sleep" not in code, (
        "probe_m5_waf_v1_2024.py must not use time.sleep in executable code "
        "(script idempotency)"
    )
    # 不允许 random.random
    assert "random.random" not in code, (
        "probe_m5_waf_v1_2024.py must not use random.random in executable code "
        "(deterministic)"
    )
    # HTTP_LIMIT 必须硬编码 ≤10
    assert "HTTP_LIMIT = 10" in code or "HTTP_LIMIT=10" in code, (
        "probe_m5_waf_v1_2024.py missing HTTP_LIMIT = 10 红线"
    )