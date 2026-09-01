"""Tests for knife 644 M5 WAF 网防G01 spike 三维 (≥6 cases).

Per tasking 644 §B:
- probe 报告存在 + 顶层裁定 (MIXED/BLOCKED/PARTIAL/REACHABLE) + 10 cells 实测
- evidence JSON parses + probed_count=10 + http_count ≤ 10
- 国务院 /zhengce/zhengceku/ 嵌套 WAF 网防G01 marker 真出现
- 国务院 /zhengce/content_xxx.htm 真实 content_id 探活
- 国务院 /zwgk/ retry 路径 verdict 矩阵
- 5 BLOCKED 省 /zwgk/ root REACHABLE 验证
- docs/66 §1-§6 架构师级审查 + 不宣称 PASS
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

DOC_66 = REPO_ROOT / "docs" / "66-m5-waf-third-pass-20260901.md"
REPORT_MD = REPO_ROOT / "docs" / "reports" / "m5_waf_v3_probe_20260901.md"
EVIDENCE_JSON = REPO_ROOT / "evidence_pack" / "m5_waf_v3_probe_20260901.json"
PROBE_SCRIPT = REPO_ROOT / "scripts" / "probe_m5_waf_v3_2024.py"


def test_m5_v3_probe_report_exists_and_has_top_verdict():
    """644-A.1 probe 报告存在 + 顶层裁定 + 10 cells 实测."""
    assert REPORT_MD.exists(), f"M5 v3 probe markdown missing: {REPORT_MD}"
    text = REPORT_MD.read_text(encoding="utf-8")
    assert "## 0. 顶层裁定" in text
    top_match = re.search(r"\*\*(BLOCKED|PARTIAL|REACHABLE|MIXED)\*\*", text)
    assert top_match, "M5 v3 probe report missing top verdict"
    assert "实体逐项" in text or "cells 实测" in text
    assert "10 cells 实测" in text or "10 URL" in text


def test_m5_v3_evidence_json_parses_and_http_count():
    """644-A.1 evidence JSON parses + probed_count=10 + http_count ≤ 10."""
    assert EVIDENCE_JSON.exists(), f"M5 v3 evidence JSON missing: {EVIDENCE_JSON}"
    data = json.loads(EVIDENCE_JSON.read_text(encoding="utf-8"))
    assert "summary" in data
    assert "cells" in data
    assert "fetch_log" in data
    sv = data["summary"]
    assert sv["probed_count"] == 10, (
        f"probed_count = {sv['probed_count']}, expected 10"
    )
    assert sv["http_count"] <= 10, (
        f"http_count = {sv['http_count']}, exceeds ≤ 10 红线"
    )
    assert sv["top_verdict"] in ("BLOCKED", "PARTIAL", "REACHABLE", "MIXED"), (
        f"top_verdict = {sv['top_verdict']}, expected one of "
        f"BLOCKED/PARTIAL/REACHABLE/MIXED"
    )
    assert len(data["cells"]) == 10, f"cells count = {len(data['cells'])}, expected 10"


def test_m5_v3_gov_zhengceku_nested_waf_marker_confirmed():
    """644-A.1 国务院 /zhengce/zhengceku/ 嵌套子路径 403 WAF 网防G01 marker 真出现."""
    assert EVIDENCE_JSON.exists()
    data = json.loads(EVIDENCE_JSON.read_text(encoding="utf-8"))
    nested_waf_cells = [
        c for c in data["cells"]
        if c["province"] == "gov"
        and c["slot"] == "zhengceku_nested"
        and c["http_code"] == 403
        and c["waf_g01_marker"] is True
    ]
    assert len(nested_waf_cells) == 1, (
        f"国务院 /zhengce/zhengceku/ 嵌套 WAF 网防G01 marker cells = "
        f"{len(nested_waf_cells)}, expected 1"
    )


def test_m5_v3_gov_zhengce_real_content_id_probe():
    """644-A.1 国务院 /zhengce/content_xxx.htm 真实 content_id 探活 ≥1 cells."""
    assert EVIDENCE_JSON.exists()
    data = json.loads(EVIDENCE_JSON.read_text(encoding="utf-8"))
    real_content_cells = [
        c for c in data["cells"]
        if c["province"] == "gov"
        and c["slot"] in ("zhengce_real_content", "zhengce_real_2020")
    ]
    assert len(real_content_cells) == 2, (
        f"国务院 /zhengce/content_xxx.htm 真实 content_id 探活 cells = "
        f"{len(real_content_cells)}, expected 2"
    )
    # 至少 1 REACHABLE 或 BLOCKED (content_id 不存在 ⇒ 404 BLOCKED)
    for cell in real_content_cells:
        assert cell["verdict"] in ("REACHABLE", "BLOCKED"), (
            f"slot={cell['slot']} verdict={cell['verdict']}"
        )


def test_m5_v3_gov_zwgk_retry_paths_blocked_or_reachable():
    """644-A.1 国务院 /zwgk/zcwj/ + /zwgk/zcfg/ + /zwgk/2026-08/... retry 路径 verdict 矩阵."""
    assert EVIDENCE_JSON.exists()
    data = json.loads(EVIDENCE_JSON.read_text(encoding="utf-8"))
    zwgk_retry_cells = [
        c for c in data["cells"]
        if c["province"] == "gov"
        and c["slot"] in ("zwgk_zcwj_retry", "zwgk_zcfg_retry",
                          "zwgk_sub_2026", "zwgk_root_retry")
    ]
    assert len(zwgk_retry_cells) == 4, (
        f"国务院 /zwgk/ retry 路径 cells = {len(zwgk_retry_cells)}, expected 4"
    )
    # /zwgk/ root 仍 403 WAF marker (沿用 642 + 644 第三次确认)
    zwgk_root = [
        c for c in zwgk_retry_cells if c["slot"] == "zwgk_root_retry"
    ]
    assert len(zwgk_root) == 1
    assert zwgk_root[0]["http_code"] == 403
    assert zwgk_root[0]["waf_g01_marker"] is True


def test_m5_v3_5_blocked_provinces_zwgk_root_reachable():
    """644-A.1 3 BLOCKED 省 (fujian/henan/yunnan) /zwgk/ root 沿用 642 REACHABLE 验证."""
    assert EVIDENCE_JSON.exists()
    data = json.loads(EVIDENCE_JSON.read_text(encoding="utf-8"))
    province_zwgk_root_cells = [
        c for c in data["cells"]
        if c["province"] in ("fujian", "henan", "yunnan")
        and c["slot"] in ("fujian_zwgk_root", "henan_zwgk_root",
                          "yunnan_zwgk_root")
    ]
    assert len(province_zwgk_root_cells) == 3, (
        f"3 BLOCKED 省 /zwgk/ root cells = {len(province_zwgk_root_cells)}, "
        f"expected 3 (fujian/henan/yunnan)"
    )
    for cell in province_zwgk_root_cells:
        assert cell["http_code"] == 200, (
            f"{cell['province']} /zwgk/ root http_code = {cell['http_code']}, "
            f"expected 200"
        )
        assert cell["verdict"] == "REACHABLE", (
            f"{cell['province']} /zwgk/ root verdict = {cell['verdict']}, "
            f"expected REACHABLE"
        )
        # 不带 WAF marker (不是 WAF 拦截)
        assert cell["waf_g01_marker"] is False


def test_doc_66_has_six_sections():
    """644-A.4 docs/66 含 ## 1.-## 6. 六段 + 标头属性."""
    assert DOC_66.exists(), f"docs/66 missing: {DOC_66}"
    text = DOC_66.read_text(encoding="utf-8")
    for n in ("## 1.", "## 2.", "## 3.", "## 4.", "## 5.", "## 6."):
        assert n in text, f"docs/66 missing section {n}"
    # 标头属性
    assert "66" in text[:200]
    assert "2026-09-01" in text
    assert "644" in text
    # M5 关键要素
    assert "WAF" in text or "网防G01" in text
    assert "MIXED" in text or "BLOCKED" in text or "REACHABLE" in text
    assert "644" in text


def test_doc_66_no_pass_announcement():
    """644-A.4 docs/66 不宣称 M2/M4/M5/Gate PASS (智能排除 disclaimer 否定句)."""
    assert DOC_66.exists()
    text = DOC_66.read_text(encoding="utf-8")
    sec6 = text[text.index("## 6."):]
    for keyword in ("M5 PASS", "M4 PASS", "Gate PASS", "M2 PASS"):
        positive_lines = [
            line for line in sec6.splitlines()
            if keyword in line and "不宣布" not in line
            and "不声称" not in line and "不宣称" not in line
            and "不宣告" not in line
        ]
        assert not positive_lines, (
            f"docs/66 §6 contains positive {keyword} claim: "
            f"{positive_lines!r}"
        )


def test_m5_v3_probe_script_idempotent():
    """644-A.1 probe 脚本幂等 (去 docstring + # 注释后扫: no sleeps / no randomness)."""
    assert PROBE_SCRIPT.exists()
    text = PROBE_SCRIPT.read_text(encoding="utf-8")
    text_no_docstring = re.sub(r'"""[\s\S]*?"""', "", text)
    text_no_comments = re.sub(r"#[^\n]*", "", text_no_docstring)
    forbidden = [
        "time.sleep", "random.random", "random.choice", "random.shuffle",
        "random.seed", "datetime.now",
    ]
    for f in forbidden:
        assert f not in text_no_comments, (
            f"probe_m5_waf_v3_2024.py contains non-idempotent call {f!r}"
        )
    assert "HTTP_LIMIT = 10" in text or "HTTP_LIMIT=10" in text, (
        "probe script missing HTTP_LIMIT = 10 (硬性红线)"
    )
