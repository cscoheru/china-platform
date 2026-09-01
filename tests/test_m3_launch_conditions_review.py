"""Tests for knife 637 M3 launch conditions review (≥5 cases).

Per tasking §B.1:
- 文档文件存在 + 含 §1-§6 全部 6 段
- §2 含 636 probe 引用 + REACHABLE 0 数据
- §3 含三条路径分析（非问句）
- §4 含明确推荐（路径 C 或等价）
- §5 含 M4 / M5 优先序
- §6 含 638 下一步刀序
- 不修改 cegr.observation（review 只读）
- 不静默硬编码 value

All tests are read-only (no DB / no network).
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))

DOC_57 = REPO_ROOT / "docs" / "57-m3-launch-conditions-review-20260901.md"
DOC_56 = REPO_ROOT / "docs" / "56-m2-gdp-coverage-task-breakdown-20260831.md"
DOC_54 = REPO_ROOT / "docs" / "54-milestone-replan-20260830.md"


def test_doc_57_exists_and_has_six_sections():
    """docs/57 exists and contains all 6 sections (## 1.-## 6.)."""
    assert DOC_57.exists(), f"M3 review doc missing at {DOC_57}"
    text = DOC_57.read_text(encoding="utf-8")
    for n in ("## 1.", "## 2.", "## 3.", "## 4.", "## 5.", "## 6."):
        assert n in text, f"docs/57 missing section {n}"
    # Header attribution
    assert "57" in text[:200]
    assert "2026-09-01" in text
    assert "knife 637" in text or "637" in text


def test_doc_57_section_2_cites_636_probe_with_zero_reachable():
    """§2 references 636 probe data and explicitly states REACHABLE 0."""
    assert DOC_57.exists()
    text = DOC_57.read_text(encoding="utf-8")
    # Must cite 636 probe
    assert "636" in text, "docs/57 §2 must cite 636 (probe source)"
    # Must state 0 REACHABLE
    sec2 = text[text.index("## 2."):text.index("## 3.")]
    assert "REACHABLE 0" in sec2 or "0 REACHABLE" in sec2 or "REACHABLE **0**" in sec2, (
        f"docs/57 §2 must state REACHABLE 0 (WAF-blocked). Got §2: {sec2[:300]!r}"
    )
    # Must identify WAF as root cause
    assert "WAF" in sec2, "docs/57 §2 must identify WAF as root cause"
    assert "IP" in sec2, "docs/57 §2 must mention IP-level block"


def test_doc_57_section_3_has_three_paths_no_user_question():
    """§3 analyzes 3 paths (data source mirror / commercial / maintain status).

    Critical: must NOT contain user-prompt phrasing (data source governance iron
    rule: 执行端不可提任何用户裁定事项).
    """
    assert DOC_57.exists()
    text = DOC_57.read_text(encoding="utf-8")
    sec3 = text[text.index("## 3."):text.index("## 4.")]

    # 3 paths must be present
    assert "路径 A" in sec3, "docs/57 §3 missing 路径 A (data source mirror)"
    assert "路径 B" in sec3, "docs/57 §3 missing 路径 B (commercial yearbook library)"
    assert "路径 C" in sec3, "docs/57 §3 missing 路径 C (maintain status + pivot to M4-M5)"

    # Forbidden user-prompt phrasing
    forbidden_prompts = [
        "请选择",
        "请用户",
        "您希望",
        "Which do you prefer",
        "Please select",
        "Your choice",
        "Please choose",
    ]
    for forbidden in forbidden_prompts:
        assert forbidden not in sec3, (
            f"docs/57 §3 contains forbidden user-prompt {forbidden!r} "
            f"(data source governance iron rule: 执行端不可提任何用户裁定事项)"
        )

    # Must contain "架构师推荐" or similar non-question framing
    assert "架构师" in sec3 or "架构师分析" in sec3 or "分析" in sec3, (
        "docs/57 §3 must be framed as architect analysis, not user prompt"
    )


def test_doc_57_section_4_has_explicit_recommendation_path_c():
    """§4 contains explicit architect recommendation: path C (maintain + pivot)."""
    assert DOC_57.exists()
    text = DOC_57.read_text(encoding="utf-8")
    sec4 = text[text.index("## 4."):text.index("## 5.")]
    # Explicit recommendation
    assert "路径 C" in sec4, "docs/57 §4 must mention 路径 C"
    # Verdict language
    assert ("推荐" in sec4) or ("裁定" in sec4), (
        "docs/57 §4 must use '推荐' or '裁定' (architect verdict language)"
    )
    # Reason keywords: data governance / WAF / U4
    assert "数据源治理" in sec4 or "WAF" in sec4 or "U4" in sec4, (
        "docs/57 §4 recommendation must cite data governance / WAF / U4"
    )
    # No PASS announcement
    assert "M2 PASS" not in sec4, "docs/57 §4 must NOT claim M2 PASS"
    assert "Gate PASS" not in sec4, "docs/57 §4 must NOT claim Gate PASS"


def test_doc_57_section_5_has_m4_m5_priority_order():
    """§5 contains M4 / M5 sub-knives priority."""
    assert DOC_57.exists()
    text = DOC_57.read_text(encoding="utf-8")
    sec5 = text[text.index("## 5."):text.index("## 6.")]
    assert "M4" in sec5, "docs/57 §5 must mention M4"
    assert "M5" in sec5, "docs/57 §5 must mention M5"
    # Sub-knives like M4.1 / M5.1
    assert "M4.1" in sec5, "docs/57 §5 must detail M4.1 (人物表 schema)"
    # No source policy violation (M4/M5 must use existing schema, not new data)
    assert "is_demo" in sec5 or "schema" in sec5, (
        "docs/57 §5 must mention is_demo/schema (no new data source)"
    )


def test_doc_57_section_6_points_to_638():
    """§6 names 638 as next knife (M4.1 人物表 schema + 数据可得性 probe)."""
    assert DOC_57.exists()
    text = DOC_57.read_text(encoding="utf-8")
    sec6 = text[text.index("## 6."):]
    assert "638" in sec6, "docs/57 §6 must name 638 as next knife"
    # M4.1 scope
    assert "M4.1" in sec6, "docs/57 §6 must detail 638 = M4.1 scope"
    # No PASS announcement (must NOT contain a positive claim like "M2 PASSED" /
    # "M2 已 PASS" / "M2 PASS ✅" etc.). Disclaimers ("不宣布…PASS") are fine.
    import re
    # Positive PASS claim: PASS preceded by char that is NOT a negation mark or
    # "不"/"未"/"NOT". Simpler: check that there's no line containing "M2 PASS"
    # that does NOT contain "不宣布" or "不宣告" or "不声称".
    positive_pass_lines = [
        line for line in sec6.splitlines()
        if "M2 PASS" in line and "不宣布" not in line and "不声称" not in line and "不宣称" not in line and "不宣告" not in line
    ]
    assert not positive_pass_lines, (
        f"docs/57 §6 contains positive M2 PASS claim: {positive_pass_lines!r}"
    )
    positive_gate_lines = [
        line for line in sec6.splitlines()
        if "Gate PASS" in line and "不宣布" not in line and "不声称" not in line and "不宣称" not in line and "不宣告" not in line
    ]
    assert not positive_gate_lines, (
        f"docs/57 §6 contains positive Gate PASS claim: {positive_gate_lines!r}"
    )


def test_docs_56_section_6_incremental_and_docs_54_section_m3_updated():
    """docs/56 §6 exists (pointing to docs/57); docs/54 §M3 has 637 recommendation."""
    assert DOC_56.exists()
    text56 = DOC_56.read_text(encoding="utf-8")
    assert "## 6." in text56, "docs/56 missing ## 6. (M3 启动审查)"
    sec6_56 = text56[text56.index("## 6."):]
    assert "637" in sec6_56 or "docs/57" in sec6_56, (
        "docs/56 §6 must reference 637 / docs/57"
    )

    assert DOC_54.exists()
    text54 = DOC_54.read_text(encoding="utf-8")
    assert "637" in text54, "docs/54 must reference 637"
    # §M3 should mention 637 recommendation
    sec_m3 = text54[text54.index("### M3"):text54.index("### M4")]
    assert "路径 C" in sec_m3 or "维持" in sec_m3, (
        "docs/54 §M3 must contain 637 path C recommendation"
    )


def test_doc_57_no_hardcoded_gdp_values():
    """docs/57 must not hardcode any GDP values (data source governance)."""
    assert DOC_57.exists()
    text = DOC_57.read_text(encoding="utf-8")
    forbidden_values = [
        "1349084", "53926.71", "49843.1", "98565.8", "60012.97",
        "18024.32", "32193.15", "53911.6", "25494.7", "26313.2",
    ]
    for v in forbidden_values:
        assert v not in text, (
            f"docs/57 contains hardcoded GDP value {v!r} "
            f"(data source governance iron rule: 不静默硬编码 value)"
        )
    # Allowed: years, REACHABLE counts (from probe), WAF eventID
    assert "125.93.9.191" in text or "网防G01" in text or "WAF" in text, (
        "docs/57 must identify the WAF IP/event source"
    )


def test_doc_57_no_ingest_statements():
    """docs/57 must not direct any DB write (review-only document)."""
    assert DOC_57.exists()
    text = DOC_57.read_text(encoding="utf-8")
    forbidden_writes = [
        "INSERT INTO cegr.observation",
        "UPDATE cegr.observation",
        "DELETE FROM cegr.observation",
        "TRUNCATE",
        "DROP TABLE",
    ]
    for forbidden in forbidden_writes:
        assert forbidden not in text, (
            f"docs/57 contains forbidden write statement {forbidden!r} "
            f"(637 review-only; no DB mutation)"
        )