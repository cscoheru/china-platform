"""Tests for knife 640 M4.3 政策项目 demo (≥7 cases).

Per tasking 640 §B:
- 政策 probe 报告存在 + 顶层裁定
- evidence JSON parses + probed_count ≥ 1 + 试点省 REACHABLE ≥ 1
- seed SQL 存在 + 6 表 × 3 demo each (policy_document × 3 + policy_target × 3
  + policy_measure × 3 + government_commitment × 3 + commitment_progress × 3 +
  project_event × 3) + 3 demo geo_entity
- seed SQL lineage JSONB is_demo='true' 隔离 (no is_demo='false')
- seed SQL demo SHA 0…02 区分 639 demo SHA 0…01
- docs/60 含六段 + 不宣称 PASS

All tests are read-only (no DB / no network).
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))

DOC_60 = REPO_ROOT / "docs" / "60-m4-3-policy-demo-20260901.md"
PROBE_MD = REPO_ROOT / "docs" / "reports" / "m4_3_policy_v1_probe_20260901.md"
PROBE_JSON = REPO_ROOT / "evidence_pack" / "m4_3_policy_v1_probe_20260901.json"
SEED_SQL = REPO_ROOT / "scripts" / "seed_m4_3_policy_demo.sql"
PROBE_SCRIPT = REPO_ROOT / "scripts" / "probe_policy_v1_2024.py"


def _strip_sql_comments(s: str) -> str:
    """Strip SQL line (--) and block (/* */) comments before keyword scan."""
    s = re.sub(r"--[^\n]*", "", s)
    s = re.sub(r"/\*.*?\*/", "", s, flags=re.DOTALL)
    return s


def test_policy_v1_probe_report_exists_and_has_top_verdict():
    """640-A.1 政策 probe 报告存在且含顶层裁定."""
    assert PROBE_MD.exists(), f"policy v1 probe markdown missing: {PROBE_MD}"
    text = PROBE_MD.read_text(encoding="utf-8")
    assert "## 0. 顶层裁定" in text
    assert re.search(r"\*\*REACHABLE\*\*|\*\*BLOCKED\*\*|\*\*MIXED\*\*", text), (
        "policy v1 probe report missing top verdict marker"
    )
    assert "总分布" in text
    assert "实体逐项" in text
    assert "中央 vs 试点省分布" in text
    # 关键反发现段: docs/60 §2.1 / probe §3
    assert "REACHABLE" in text and "BLOCKED" in text
    # 黑龙江 REACHABLE 2 (only 1 province)
    assert "黑龙江" in text


def test_policy_v1_evidence_json_parses():
    """640-A.1 evidence JSON parses + probed_count = 12 + 试点省 REACHABLE ≥ 1."""
    assert PROBE_JSON.exists(), f"policy v1 evidence JSON missing: {PROBE_JSON}"
    data = json.loads(PROBE_JSON.read_text(encoding="utf-8"))
    assert "summary" in data
    assert "cells" in data
    assert "probed_count" in data
    assert "probe_methodology" in data
    assert "by_verdict" in data["summary"]
    assert "total_cells" in data["summary"]
    assert "probed_cells" in data["summary"]
    assert "by_class_verdict" in data["summary"]
    # probed cells must = 12 (10 provincial + 2 central)
    assert data["summary"]["probed_cells"] == 12, (
        f"policy v1 probed_cells = {data['summary']['probed_cells']}, "
        "expected 12 (10 provincial policy path + 2 central)"
    )
    bv = data["summary"]["by_verdict"]
    total_verdicts = (
        bv.get("REACHABLE", 0) + bv.get("PARTIAL", 0) + bv.get("BLOCKED", 0)
    )
    assert total_verdicts == data["summary"]["probed_cells"], (
        f"by_verdict sum ({total_verdicts}) ≠ probed_cells "
        f"({data['summary']['probed_cells']})"
    )
    # 试点省至少 1 REACHABLE (640 实际 = 黑龙江 REACHABLE 2)
    pcv = data["summary"]["by_class_verdict"].get("provincial", {})
    assert pcv.get("REACHABLE", 0) >= 1, (
        f"provincial REACHABLE = {pcv.get('REACHABLE', 0)}, "
        "expected ≥ 1 (per docs/60 §2.1 — 实际 2 黑龙江 /zwgk/zfwj/ + /zwgk/zfgb/)"
    )


def test_seed_m4_3_sql_exists_and_has_demo_data():
    """640-A.2 seed SQL 存在 + 6 表 × 3 demo each + 3 demo geo_entity."""
    assert SEED_SQL.exists(), f"seed_m4_3_policy_demo.sql missing: {SEED_SQL}"
    text = SEED_SQL.read_text(encoding="utf-8")
    # 6 政策表 × 3 demo each
    pd_rows = text.count("demo-policy-document-")
    pt_rows = text.count("demo-policy-target-")
    pm_rows = text.count("demo-policy-measure-")
    gc_rows = text.count("demo-commitment-")
    cp_rows = text.count("demo progress ")  # 'demo progress X%' in commitment_progress
    proj_rows = text.count("demo-project-")
    assert pd_rows >= 3, f"policy_document demo rows = {pd_rows}, expected ≥ 3"
    assert pt_rows >= 3, f"policy_target demo rows = {pt_rows}, expected ≥ 3"
    assert pm_rows >= 3, f"policy_measure demo rows = {pm_rows}, expected ≥ 3"
    assert gc_rows >= 3, f"government_commitment demo rows = {gc_rows}, expected ≥ 3"
    assert cp_rows >= 3, f"commitment_progress demo rows = {cp_rows}, expected ≥ 3"
    assert proj_rows >= 3, f"project_event demo rows = {proj_rows}, expected ≥ 3"
    # 3 demo geo_entity (synthetic PROVINCE, 不绑定真实省)
    geo_rows = text.count("M4.3 demo province")
    assert geo_rows >= 3, (
        f"demo geo_entity rows = {geo_rows}, expected ≥ 3 "
        "(synthetic M4.3 demo province 1/2/3)"
    )
    # 红线: 不删表 / 不 DROP COLUMN / 不 DELETE FROM 真实数据
    text_no_comments = _strip_sql_comments(text)
    forbidden = [
        "DROP TABLE", "DROP COLUMN", "DROP INDEX",
        "DELETE FROM", "TRUNCATE",
    ]
    for f in forbidden:
        assert f not in text_no_comments, (
            f"seed_m4_3_policy_demo.sql (after comment strip) "
            f"contains forbidden DML/DDL: {f!r}"
        )


def test_seed_m4_3_sql_lineage_is_demo_isolation():
    """640-A.2 seed SQL 所有 demo 6 表行 lineage JSONB is_demo='true' 隔离."""
    assert SEED_SQL.exists()
    text = SEED_SQL.read_text(encoding="utf-8")
    # 6 政策表每行 lineage JSONB 都含 is_demo 字段
    # 计数 is_demo 出现次数 = 6 tables × 3 demo rows = 18 (含 lineage JSONB 行)
    # 但我们保守断言每个 INSERT block 至少 3 个 is_demo='true'
    policy_tables = [
        "policy_document", "policy_target", "policy_measure",
        "government_commitment", "commitment_progress", "project_event",
    ]
    for tbl in policy_tables:
        # 抓 INSERT block (粗正则;每 block 含 3 demo 行)
        block = re.search(
            rf"INSERT INTO {tbl}.*?VALUES\s*(.*?)ON CONFLICT",
            text, re.DOTALL,
        )
        assert block, f"seed SQL missing INSERT INTO {tbl} ... VALUES block"
        bb = block.group(1)
        is_demo_count = bb.count('"is_demo": "true"')
        assert is_demo_count >= 3, (
            f"{tbl} demo block lineage is_demo='true' count = {is_demo_count}, "
            "expected ≥ 3 (3 demo rows each table)"
        )
    # 红线: lineage 不允许 is_demo='false' (demo seed 仅 true 隔离)
    text_compact = text.replace(" ", "").replace("\n", "").replace("\t", "")
    assert not re.search(r'"is_demo"\s*:\s*"false"', text_compact), (
        "seed SQL must not contain lineage is_demo='false' (demo seed only)"
    )
    assert not re.search(r'"is_demo"\s*:\s*false', text_compact), (
        "seed SQL must not contain JSON false value (demo seed only)"
    )


def test_seed_m4_3_sql_demo_sha_distinct_from_renmian():
    """640-A.2 demo SHA 0…02 与 639 demo SHA 0…01 区分."""
    assert SEED_SQL.exists()
    text = SEED_SQL.read_text(encoding="utf-8")
    # 剥注释防 ';' 截断
    text_nc = _strip_sql_comments(text)
    sd_stmt = re.search(
        r"INSERT INTO source_document[^;]*;",
        text_nc, re.DOTALL,
    )
    assert sd_stmt, "seed SQL missing source_document INSERT statement"
    sb = sd_stmt.group(0)
    # 640 demo SHA 必须以 0…02 结尾
    demo_sha_640 = "0000000000000000000000000000000000000000000000000000000000000002"
    assert demo_sha_640 in sb, (
        f"source_document INSERT missing 640 demo SHA {demo_sha_640}"
    )
    # file_hash_sha256 列必须出现
    assert "file_hash_sha256" in sb
    # 639 demo SHA 0…01 不应出现在 640 seed (避免 demo 污染混淆)
    demo_sha_639 = "0000000000000000000000000000000000000000000000000000000000000001"
    assert demo_sha_639 not in text, (
        "seed_m4_3_policy_demo.sql must not contain 639 demo SHA 0…01 "
        "(demo SHA 0…02 distinct from 639 SHA 0…01)"
    )
    # 6 表 demo source_id 必须跳回 demo SHA 0…02
    demo_sd_uuid = "b0eebc99-9c0b-4ef8-bb6d-6bb9bd380a11"
    # 数 demo SD UUID 在 6 政策表 INSERT block 出现次数
    # policy_document source_id (1) + government_commitment source_id (3) +
    # commitment_progress source_id (3) + project_event source_id (3) = ≥10
    sd_uuid_count = 0
    for tbl in ("policy_document", "government_commitment",
                "commitment_progress", "project_event"):
        m = re.search(
            rf"INSERT INTO {tbl}.*?ON CONFLICT",
            text, re.DOTALL,
        )
        if m:
            sd_uuid_count += m.group(0).count(demo_sd_uuid)
    assert sd_uuid_count >= 10, (
        f"6 tables demo source_id → demo SD UUID count = {sd_uuid_count}, "
        "expected ≥ 10 (1 policy_document + 3 + 3 + 3)"
    )


def test_doc_60_has_six_sections():
    """docs/60 含 ## 1.-## 6. 六段 + 标头属性."""
    assert DOC_60.exists(), f"docs/60 missing: {DOC_60}"
    text = DOC_60.read_text(encoding="utf-8")
    for n in ("## 1.", "## 2.", "## 3.", "## 4.", "## 5.", "## 6."):
        assert n in text, f"docs/60 missing section {n}"
    # 标头属性
    assert "60" in text[:200]
    assert "2026-09-01" in text
    assert "640" in text


def test_doc_60_no_pass_announcement():
    """docs/60 不宣称 M2/M4/Gate PASS（智能排除 disclaimer 否定句）."""
    assert DOC_60.exists()
    text = DOC_60.read_text(encoding="utf-8")
    sec6 = text[text.index("## 6."):]
    positive_pass_lines = [
        line for line in sec6.splitlines()
        if "M4 PASS" in line and "不宣布" not in line
        and "不声称" not in line and "不宣称" not in line and "不宣告" not in line
    ]
    assert not positive_pass_lines, (
        f"docs/60 §6 contains positive M4 PASS claim: {positive_pass_lines!r}"
    )
    positive_gate_lines = [
        line for line in sec6.splitlines()
        if "Gate PASS" in line and "不宣布" not in line
        and "不声称" not in line and "不宣称" not in line and "不宣告" not in line
    ]
    assert not positive_gate_lines, (
        f"docs/60 §6 contains positive Gate PASS claim: {positive_gate_lines!r}"
    )
    positive_m2_lines = [
        line for line in sec6.splitlines()
        if "M2 PASS" in line and "不宣布" not in line
        and "不声称" not in line and "不宣称" not in line and "不宣告" not in line
    ]
    assert not positive_m2_lines, (
        f"docs/60 §6 contains positive M2 PASS claim: {positive_m2_lines!r}"
    )