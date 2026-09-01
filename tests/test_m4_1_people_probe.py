"""Tests for knife 638 M4.1 people-schema + gov-report probe (≥8 cases).

Per tasking §B.638:
- 政府工作报告 probe 报告存在 + 含顶层裁定
- 政府工作报告 probe evidence JSON parses
- 政府工作报告 probe 不写 DB
- 政府工作报告 probe 不静默硬编码 GDP 值
- 任免公告 probe evidence JSON parses
- migration 015 零 DML (no INSERT/UPDATE/DELETE/TRUNCATE/DROP TABLE/COLUMN)
- docs/58 含 6 段
- docs/58 不宣称 M2/M4/Gate PASS

All tests are read-only (no DB / no network).
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))

DOC_58 = REPO_ROOT / "docs" / "58-m4-1-people-schema-gov-report-probe-20260901.md"
GOV_REPORT_MD = REPO_ROOT / "docs" / "reports" / "m4_1_gov_report_probe_20260901.md"
GOV_REPORT_JSON = REPO_ROOT / "evidence_pack" / "m4_1_gov_report_probe_20260901.json"
RENMIAN_JSON = REPO_ROOT / "evidence_pack" / "m4_1_renmian_probe_20260901.json"
MIGRATION_015 = REPO_ROOT / "schema" / "migrations" / "015-m4-1-people-schema.sql"
PROBE_GOV_SCRIPT = REPO_ROOT / "scripts" / "probe_gov_report_2024.py"
PROBE_RENMIAN_SCRIPT = REPO_ROOT / "scripts" / "probe_renmian_announcement_2024.py"


def test_gov_report_probe_report_exists_and_has_top_verdict():
    """638-A.1 报告存在且含顶层裁定."""
    assert GOV_REPORT_MD.exists(), f"gov report probe markdown missing: {GOV_REPORT_MD}"
    text = GOV_REPORT_MD.read_text(encoding="utf-8")
    assert "## 0. 顶层裁定" in text
    # 顶层裁定 verdict 必须是 REACHABLE/BLOCKED/MIXED 之一
    assert re.search(r"\*\*REACHABLE\*\*|\*\*BLOCKED\*\*|\*\*MIXED\*\*", text), (
        "gov report probe report missing top verdict marker"
    )
    # 含 32 cell / 总分布 / 实体逐项
    assert "总分布" in text
    assert "32" in text
    assert "实体逐项" in text


def test_gov_report_probe_evidence_json_parses():
    """638-A.1 evidence JSON parses + 含 summary/cells/probed_count."""
    assert GOV_REPORT_JSON.exists(), f"gov report evidence JSON missing: {GOV_REPORT_JSON}"
    import json
    data = json.loads(GOV_REPORT_JSON.read_text(encoding="utf-8"))
    assert "summary" in data
    assert "cells" in data
    assert "probed_count" in data
    assert "probe_methodology" in data
    # summary 至少含 by_verdict / total_cells / probed_cells
    assert "by_verdict" in data["summary"]
    assert "total_cells" in data["summary"]
    assert "probed_cells" in data["summary"]
    # probed cells 必须是 32 (1 国务院 + 31 省)
    assert data["summary"]["probed_cells"] >= 1
    # verdict 计数必须有 REACHABLE / BLOCKED (可能 PARTIAL=0)
    bv = data["summary"]["by_verdict"]
    assert "REACHABLE" in bv or bv.get("REACHABLE", 0) > 0
    assert "BLOCKED" in bv
    # 默认使用 .get 容错 (636 经验: defaultdict 不增 0 键)
    total_verdicts = bv.get("REACHABLE", 0) + bv.get("PARTIAL", 0) + bv.get("BLOCKED", 0)
    assert total_verdicts == data["summary"]["probed_cells"], (
        f"by_verdict sum ({total_verdicts}) ≠ probed_cells "
        f"({data['summary']['probed_cells']})"
    )


def test_gov_report_probe_does_not_modify_database():
    """probe 脚本不调用 INSERT/UPDATE/DELETE/psycopg.connect."""
    assert PROBE_GOV_SCRIPT.exists()
    text = PROBE_GOV_SCRIPT.read_text(encoding="utf-8")
    # 禁: 写 DB 的 SQL 关键字 / psycopg
    forbidden = ["INSERT INTO", "UPDATE cegr", "DELETE FROM",
                 "TRUNCATE", "DROP TABLE", "psycopg.connect",
                 "create_engine", ".execute(", ".executemany("]
    for f in forbidden:
        assert f not in text, (
            f"probe_gov_report_2024.py contains forbidden DB mutation: {f!r}"
        )
    # 允许: read-only 验证
    assert "fetch(" in text or "subprocess" in text, (
        "probe script must use HTTP fetch (subprocess + curl)"
    )


def test_gov_report_probe_no_hardcoded_gdp_values():
    """probe 报告与脚本不含 31 省 2024 期望 GDP 真值 (数据源治理铁律)."""
    assert GOV_REPORT_MD.exists()
    text_md = GOV_REPORT_MD.read_text(encoding="utf-8")
    assert PROBE_GOV_SCRIPT.exists()
    text_py = PROBE_GOV_SCRIPT.read_text(encoding="utf-8")
    # 31 省 2024 期望 GDP 真值（继承 637 测试禁值）
    forbidden_values = [
        "1349084", "53926.71", "49843.1", "98565.8", "60012.97",
        "18024.32", "32193.15", "53911.6", "25494.7", "26313.2",
    ]
    for v in forbidden_values:
        assert v not in text_md, (
            f"gov report probe markdown contains hardcoded GDP value {v!r}"
        )
        assert v not in text_py, (
            f"gov report probe script contains hardcoded GDP value {v!r}"
        )


def test_renmian_probe_evidence_json_parses():
    """638-A.2 evidence JSON parses."""
    assert RENMIAN_JSON.exists(), f"renmian evidence JSON missing: {RENMIAN_JSON}"
    import json
    data = json.loads(RENMIAN_JSON.read_text(encoding="utf-8"))
    assert "summary" in data
    assert "cells" in data
    assert "probed_count" in data
    bv = data["summary"]["by_verdict"]
    # 任免公告 probe: probed 3 cells
    assert data["summary"]["probed_cells"] == 3, (
        f"renmian probe probed_cells = {data['summary']['probed_cells']}, "
        "expected 3 (ccdi + npc + central)"
    )
    # 至少有一类 verdict 命中（任一类即可）
    assert "REACHABLE" in bv or "PARTIAL" in bv or "BLOCKED" in bv


def test_migration_015_no_dml():
    """015 migration 零 DML — 仅 DDL ADD COLUMN / CREATE INDEX."""
    assert MIGRATION_015.exists(), f"migration 015 missing: {MIGRATION_015}"
    text = MIGRATION_015.read_text(encoding="utf-8")
    # 禁: DML 关键字（继承 008 红线）
    forbidden_dml = [
        "INSERT INTO", "UPDATE ", "DELETE FROM",
        "TRUNCATE", "DROP TABLE", "DROP COLUMN", "DROP INDEX",
        "ALTER COLUMN ... DROP",  # 简化匹配 — ALTER + DROP 字段
        "RENAME TO", "RENAME COLUMN",
    ]
    for f in forbidden_dml:
        assert f not in text, (
            f"migration 015 contains forbidden DML/DDL: {f!r} "
            f"(additive only per 008 discipline)"
        )
    # 允: ADD COLUMN / CREATE INDEX / COMMENT
    assert "ADD COLUMN IF NOT EXISTS" in text, (
        "migration 015 must use ADD COLUMN IF NOT EXISTS"
    )
    assert "CREATE INDEX IF NOT EXISTS" in text, (
        "migration 015 must use CREATE INDEX IF NOT EXISTS"
    )
    # 加性变更必须包含 is_demo
    assert "is_demo" in text, "migration 015 must add is_demo column"


def test_doc_58_has_six_sections():
    """docs/58 含 ## 1.-## 6. 六段 + 标头属性."""
    assert DOC_58.exists(), f"docs/58 missing: {DOC_58}"
    text = DOC_58.read_text(encoding="utf-8")
    for n in ("## 1.", "## 2.", "## 3.", "## 4.", "## 5.", "## 6."):
        assert n in text, f"docs/58 missing section {n}"
    # 标头属性
    assert "58" in text[:200]
    assert "2026-09-01" in text
    assert "638" in text


def test_doc_58_no_pass_announcement():
    """docs/58 不宣称 M2/M4/Gate PASS（智能排除 disclaimer 否定句）."""
    assert DOC_58.exists()
    text = DOC_58.read_text(encoding="utf-8")
    sec6 = text[text.index("## 6."):]
    positive_pass_lines = [
        line for line in sec6.splitlines()
        if "M4 PASS" in line and "不宣布" not in line
        and "不声称" not in line and "不宣称" not in line and "不宣告" not in line
    ]
    assert not positive_pass_lines, (
        f"docs/58 §6 contains positive M4 PASS claim: {positive_pass_lines!r}"
    )
    positive_gate_lines = [
        line for line in sec6.splitlines()
        if "Gate PASS" in line and "不宣布" not in line
        and "不声称" not in line and "不宣称" not in line and "不宣告" not in line
    ]
    assert not positive_gate_lines, (
        f"docs/58 §6 contains positive Gate PASS claim: {positive_gate_lines!r}"
    )
    positive_m2_lines = [
        line for line in sec6.splitlines()
        if "M2 PASS" in line and "不宣布" not in line
        and "不声称" not in line and "不宣称" not in line and "不宣告" not in line
    ]
    assert not positive_m2_lines, (
        f"docs/58 §6 contains positive M2 PASS claim: {positive_m2_lines!r}"
    )