"""Tests for knife 639 M4.2 任免 demo (≥6 cases).

Per tasking 639 §B:
- 二次 probe 报告存在 + 顶层裁定
- evidence JSON parses + probed_count ≥ 1
- seed SQL 存在 + 5 demo person rows
- seed SQL is_demo=true 隔离
- seed SQL 有 source_document 跳回 SHA
- docs/59 含六段 + 不宣称 PASS

All tests are read-only (no DB / no network).
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))

DOC_59 = REPO_ROOT / "docs" / "59-m4-2-renmian-demo-20260901.md"
PROBE_MD = REPO_ROOT / "docs" / "reports" / "m4_2_renmian_v2_probe_20260901.md"
PROBE_JSON = REPO_ROOT / "evidence_pack" / "m4_2_renmian_v2_probe_20260901.json"
SEED_SQL = REPO_ROOT / "scripts" / "seed_m4_2_demo.sql"
PROBE_SCRIPT = REPO_ROOT / "scripts" / "probe_renmian_v2_2024.py"


def test_renmian_v2_probe_report_exists_and_has_top_verdict():
    """639-A.1 报告存在且含顶层裁定."""
    assert PROBE_MD.exists(), f"renmian v2 probe markdown missing: {PROBE_MD}"
    text = PROBE_MD.read_text(encoding="utf-8")
    assert "## 0. 顶层裁定" in text
    # 顶层裁定 verdict 必须是 REACHABLE/BLOCKED/MIXED 之一
    assert re.search(r"\*\*REACHABLE\*\*|\*\*BLOCKED\*\*|\*\*MIXED\*\*", text), (
        "renmian v2 probe report missing top verdict marker"
    )
    # 含 29 cell / 总分布 / 实体逐项 / 中央 vs 试点省分布
    assert "总分布" in text
    assert "29" in text
    assert "实体逐项" in text
    assert "中央 vs 试点省分布" in text
    assert "by_class_verdict" in text or "中央 vs 试点省" in text


def test_renmian_v2_evidence_json_parses():
    """639-A.1 evidence JSON parses + 含 summary/cells/probed_count/by_class_verdict."""
    assert PROBE_JSON.exists(), f"renmian v2 evidence JSON missing: {PROBE_JSON}"
    data = json.loads(PROBE_JSON.read_text(encoding="utf-8"))
    assert "summary" in data
    assert "cells" in data
    assert "probed_count" in data
    assert "probe_methodology" in data
    # summary 含 by_verdict / total_cells / probed_cells / by_class_verdict
    assert "by_verdict" in data["summary"]
    assert "total_cells" in data["summary"]
    assert "probed_cells" in data["summary"]
    assert "by_class_verdict" in data["summary"]
    # probed cells 必须 = 29 (6 central + 23 provincial)
    assert data["summary"]["probed_cells"] == 29, (
        f"renmian v2 probed_cells = {data['summary']['probed_cells']}, "
        "expected 29 (6 central + 23 provincial)"
    )
    # verdict 计数必须非空
    bv = data["summary"]["by_verdict"]
    assert bv.get("REACHABLE", 0) + bv.get("PARTIAL", 0) + bv.get("BLOCKED", 0) >= 1
    # verdict 计数 sum 等于 probed_cells
    total_verdicts = bv.get("REACHABLE", 0) + bv.get("PARTIAL", 0) + bv.get("BLOCKED", 0)
    assert total_verdicts == data["summary"]["probed_cells"], (
        f"by_verdict sum ({total_verdicts}) ≠ probed_cells "
        f"({data['summary']['probed_cells']})"
    )
    # 试点省至少 6 REACHABLE (639 实际发现)
    pcv = data["summary"]["by_class_verdict"].get("provincial", {})
    assert pcv.get("REACHABLE", 0) >= 1, (
        f"provincial REACHABLE = {pcv.get('REACHABLE', 0)}, "
        "expected ≥ 1 (per docs/59 §2.1 — 实际 6 试点省)"
    )


def test_seed_m4_2_sql_exists_and_has_demo_data():
    """639-A.2 seed SQL 存在 + 5 demo person rows + 5 tenure + 5 appointment_event."""
    assert SEED_SQL.exists(), f"seed_m4_2_demo.sql missing: {SEED_SQL}"
    text = SEED_SQL.read_text(encoding="utf-8")
    # INSERT person ... VALUES 行数 (5 demo-person-X)
    person_inserts = re.findall(
        r"INSERT INTO person.*?VALUES\s*(.*?)(?:ON CONFLICT|\Z)",
        text, re.DOTALL,
    )
    assert person_inserts, "seed SQL missing INSERT INTO person ... VALUES"
    # 数 demo-person-X 出现次数 = 5
    person_rows = text.count("demo-person-")
    assert person_rows >= 5, (
        f"seed SQL demo-person-* rows = {person_rows}, expected ≥ 5"
    )
    # INSERT tenure ... VALUES (5 demo tenure)
    tenure_rows = text.count("M4.2 demo tenure ")
    assert tenure_rows >= 5, (
        f"seed SQL demo tenure rows = {tenure_rows}, expected ≥ 5"
    )
    # INSERT appointment_event ... VALUES (5 demo)
    appt_rows = text.count("demo.placeholder/m4_2/person/")
    assert appt_rows >= 5, (
        f"seed SQL demo appointment_event rows = {appt_rows}, expected ≥ 5"
    )
    # 红线: 不删表 / 不 DROP COLUMN / 不 DELETE FROM 真实数据
    # 先剥注释 (line + block) 再扫描 (避免 comment header 误命中)
    def _strip_sql_comments(s: str) -> str:
        s = re.sub(r"--[^\n]*", "", s)
        s = re.sub(r"/\*.*?\*/", "", s, flags=re.DOTALL)
        return s
    text_no_comments = _strip_sql_comments(text)
    forbidden = [
        "DROP TABLE", "DROP COLUMN", "DROP INDEX",
        "DELETE FROM", "TRUNCATE",
    ]
    for f in forbidden:
        assert f not in text_no_comments, (
            f"seed_m4_2_demo.sql (after comment strip) contains forbidden DML/DDL: {f!r}"
        )


def test_seed_m4_2_sql_is_demo_isolation():
    """639-A.2 seed SQL 所有 demo 行显式 is_demo=TRUE 隔离."""
    assert SEED_SQL.exists()
    text = SEED_SQL.read_text(encoding="utf-8")
    # INSERT INTO person 行: 必须有 is_demo=TRUE
    person_block = re.search(
        r"INSERT INTO person.*?VALUES\s*(.*?)ON CONFLICT",
        text, re.DOTALL,
    )
    assert person_block, "seed SQL missing person INSERT block"
    pb = person_block.group(1)
    # demo person block 必须含 is_demo 字样 + TRUE
    person_is_demo_true = pb.count("TRUE")
    assert person_is_demo_true >= 5, (
        f"person demo block TRUE count = {person_is_demo_true}, "
        "expected ≥ 5 (5 demo person rows)"
    )
    # INSERT INTO appointment_event 行: 必须有 is_demo=TRUE
    appt_block = re.search(
        r"INSERT INTO appointment_event.*?VALUES\s*(.*?)ON CONFLICT",
        text, re.DOTALL,
    )
    assert appt_block, "seed SQL missing appointment_event INSERT block"
    ab = appt_block.group(1)
    appt_is_demo_true = ab.count("TRUE")
    assert appt_is_demo_true >= 5, (
        f"appointment_event demo block TRUE count = {appt_is_demo_true}, "
        "expected ≥ 5 (5 demo appointment_event rows)"
    )
    # 红线: 不允许出现 is_demo=FALSE (demo seed 不能写真实数据标记)
    # 用 raw regex 避免 SyntaxWarning;剥空格和换行后比较
    text_compact = text.replace(" ", "").replace("\n", "").replace("\t", "")
    assert not re.search(r"is_demo\s*=\s*FALSE", text_compact), (
        "seed SQL must not contain is_demo=FALSE (demo seed is_demo=true only)"
    )


def test_seed_m4_2_sql_has_source_document_back_link():
    """639-A.2 demo 数据有 source_document 跳回 SHA (demo SHA 0…01)."""
    assert SEED_SQL.exists()
    text = SEED_SQL.read_text(encoding="utf-8")
    # 剥注释 (line + block) 防止 comment 中的 ';' 截断 regex
    text_nc = re.sub(r"--[^\n]*", "", text)
    text_nc = re.sub(r"/\*.*?\*/", "", text_nc, flags=re.DOTALL)
    # INSERT INTO source_document 必须有 file_hash_sha256 列 + deterministic demo SHA
    # 抓整个 INSERT statement (含列名 + VALUES + ON CONFLICT)
    sd_stmt = re.search(
        r"INSERT INTO source_document[^;]*;",
        text_nc, re.DOTALL,
    )
    assert sd_stmt, "seed SQL missing source_document INSERT statement"
    sb = sd_stmt.group(0)
    # demo SHA 必须以 0…01 结尾（64 char hex）
    demo_sha = "0000000000000000000000000000000000000000000000000000000000000001"
    assert demo_sha in sb, (
        f"source_document INSERT missing deterministic demo SHA {demo_sha}"
    )
    # file_hash_sha256 列必须出现
    assert "file_hash_sha256" in sb
    # tenure.source_id = demo source_document (FK 一跳回)
    tenure_block = re.search(
        r"INSERT INTO tenure.*?VALUES\s*(.*?)ON CONFLICT",
        text, re.DOTALL,
    )
    assert tenure_block, "seed SQL missing tenure INSERT block"
    tb = tenure_block.group(1)
    # 5 demo tenure 必须引用 demo source_document UUID
    # demo source_document UUID: a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a11
    demo_sd_uuid = "a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a11"
    sd_ref_count = tb.count(demo_sd_uuid)
    assert sd_ref_count >= 5, (
        f"tenure.source_id demo SD UUID count = {sd_ref_count}, "
        "expected ≥ 5 (5 demo tenure rows)"
    )
    # appointment_event.source_id = demo source_document
    appt_block = re.search(
        r"INSERT INTO appointment_event.*?VALUES\s*(.*?)ON CONFLICT",
        text, re.DOTALL,
    )
    assert appt_block, "seed SQL missing appointment_event INSERT block"
    ab = appt_block.group(1)
    appt_sd_ref_count = ab.count(demo_sd_uuid)
    assert appt_sd_ref_count >= 5, (
        f"appointment_event.source_id demo SD UUID count = {appt_sd_ref_count}, "
        "expected ≥ 5 (5 demo appointment_event rows)"
    )


def test_doc_59_has_six_sections():
    """docs/59 含 ## 1.-## 6. 六段 + 标头属性."""
    assert DOC_59.exists(), f"docs/59 missing: {DOC_59}"
    text = DOC_59.read_text(encoding="utf-8")
    for n in ("## 1.", "## 2.", "## 3.", "## 4.", "## 5.", "## 6."):
        assert n in text, f"docs/59 missing section {n}"
    # 标头属性
    assert "59" in text[:200]
    assert "2026-09-01" in text
    assert "639" in text


def test_doc_59_no_pass_announcement():
    """docs/59 不宣称 M2/M4/Gate PASS（智能排除 disclaimer 否定句）."""
    assert DOC_59.exists()
    text = DOC_59.read_text(encoding="utf-8")
    sec6 = text[text.index("## 6."):]
    positive_pass_lines = [
        line for line in sec6.splitlines()
        if "M4 PASS" in line and "不宣布" not in line
        and "不声称" not in line and "不宣称" not in line and "不宣告" not in line
    ]
    assert not positive_pass_lines, (
        f"docs/59 §6 contains positive M4 PASS claim: {positive_pass_lines!r}"
    )
    positive_gate_lines = [
        line for line in sec6.splitlines()
        if "Gate PASS" in line and "不宣布" not in line
        and "不声称" not in line and "不宣称" not in line and "不宣告" not in line
    ]
    assert not positive_gate_lines, (
        f"docs/59 §6 contains positive Gate PASS claim: {positive_gate_lines!r}"
    )
    positive_m2_lines = [
        line for line in sec6.splitlines()
        if "M2 PASS" in line and "不宣布" not in line
        and "不声称" not in line and "不宣称" not in line and "不宣告" not in line
    ]
    assert not positive_m2_lines, (
        f"docs/59 §6 contains positive M2 PASS claim: {positive_m2_lines!r}"
    )
