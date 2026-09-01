"""Tests for knife 641 M4.4 黑龙江政策真实化 spike (≥6 cases).

Per tasking 641 §B:
- 真实抓取报告存在 + 顶层裁定 (REAL_FETCHED)
- evidence JSON parses + fetched_count ≥ 1 + 真实 SHA 64 hex chars
- seed SQL 6 表 × 1 真实 each (vs 640 demo × 3 each)
- seed lineage is_demo='false' (vs 640 demo is_demo='true');不含 true
- seed 真实 SHA ≠ 640 demo SHA '0…02'
- docs/61 含六段 + 不宣称 PASS

All tests are read-only (no DB / no network).
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))

DOC_61 = REPO_ROOT / "docs" / "61-m4-4-heilongjiang-real-20260901.md"
REPORT_MD = REPO_ROOT / "docs" / "reports" / "m4_4_heilongjiang_real_20260901.md"
EVIDENCE_JSON = REPO_ROOT / "evidence_pack" / "m4_4_heilongjiang_real_20260901.json"
SEED_SQL = REPO_ROOT / "scripts" / "seed_m4_4_heilongjiang_real.sql"
FETCH_SCRIPT = REPO_ROOT / "scripts" / "fetch_heilongjiang_policy_v1_2024.py"

# 真实 SHA from 641-A.1 王正军 detail page (calc on fetch)
REAL_SHA_641 = "26e5379d86e6a5c6a596acfef41293821a07413e973e1481b2b373f2e00b87ab"
# 640 demo SHA (from seed_m4_3_policy_demo.sql)
DEMO_SHA_640 = "0000000000000000000000000000000000000000000000000000000000000002"


def _strip_sql_comments(s: str) -> str:
    """Strip SQL line (--) and block (/* */) comments before keyword scan."""
    s = re.sub(r"--[^\n]*", "", s)
    s = re.sub(r"/\*.*?\*/", "", s, flags=re.DOTALL)
    return s


def test_heilongjiang_real_fetch_report_exists_and_has_top_verdict():
    """641-A.1 真实抓取报告存在 + 顶层裁定 (REAL_FETCHED)."""
    assert REPORT_MD.exists(), f"hlj real fetch markdown missing: {REPORT_MD}"
    text = REPORT_MD.read_text(encoding="utf-8")
    assert "## 0. 顶层裁定" in text
    assert "REAL_FETCHED" in text, (
        "hlj real fetch report missing REAL_FETCHED top verdict"
    )
    assert "总抓取" in text
    assert "实体逐项" in text or "政策样本" in text
    # 真实抓取源 URL 必出现
    assert "hlj.gov.cn" in text


def test_heilongjiang_real_evidence_json_parses():
    """641-A.1 evidence JSON parses + fetched_count ≥ 1 + 真实 SHA 64 hex."""
    assert EVIDENCE_JSON.exists(), f"hlj real evidence JSON missing: {EVIDENCE_JSON}"
    data = json.loads(EVIDENCE_JSON.read_text(encoding="utf-8"))
    assert "summary" in data
    assert "cells" in data
    assert "fetch_log" in data
    sv = data["summary"]
    assert sv["fetch_status"] == "REAL_FETCHED", (
        f"fetch_status = {sv['fetch_status']}, expected REAL_FETCHED"
    )
    assert sv["fetched_count"] >= 1, (
        f"fetched_count = {sv['fetched_count']}, expected ≥ 1"
    )
    # ≤4 HTTP total 红线
    assert sv["http_count"] <= 4, (
        f"http_count = {sv['http_count']}, exceeds ≤ 4 红线"
    )
    # 真实 SHA 64 hex chars
    for cell in data["cells"]:
        sha = cell.get("file_hash_sha256", "")
        assert re.match(r"^[0-9a-f]{64}$", sha), (
            f"cell sha not 64 hex: {sha}"
        )


def test_seed_m4_4_sql_exists_and_has_real_data():
    """641-A.2 seed SQL 存在 + 6 表 × 1 真实 each + 1 source_registry/source_document."""
    assert SEED_SQL.exists(), f"seed_m4_4_heilongjiang_real.sql missing: {SEED_SQL}"
    text = SEED_SQL.read_text(encoding="utf-8")
    # 6 政策表各 1 条 (vs 640 demo × 3)
    # 用 INSERT INTO + ( + VALUES 计数
    pd_count = len(re.findall(r"INSERT INTO policy_document", text))
    pt_count = len(re.findall(r"INSERT INTO policy_target", text))
    pm_count = len(re.findall(r"INSERT INTO policy_measure", text))
    gc_count = len(re.findall(r"INSERT INTO government_commitment", text))
    cp_count = len(re.findall(r"INSERT INTO commitment_progress", text))
    proj_count = len(re.findall(r"INSERT INTO project_event", text))
    assert pd_count == 1, f"policy_document INSERT count = {pd_count}, expected 1"
    assert pt_count == 1, f"policy_target INSERT count = {pt_count}, expected 1"
    assert pm_count == 1, f"policy_measure INSERT count = {pm_count}, expected 1"
    assert gc_count == 1, f"government_commitment INSERT count = {gc_count}, expected 1"
    assert cp_count == 1, f"commitment_progress INSERT count = {cp_count}, expected 1"
    assert proj_count == 1, f"project_event INSERT count = {proj_count}, expected 1"
    # 1 source_registry + 1 source_document (真实)
    sr_count = len(re.findall(r"INSERT INTO source_registry", text))
    sd_count = len(re.findall(r"INSERT INTO source_document", text))
    assert sr_count == 1, f"source_registry INSERT count = {sr_count}, expected 1"
    assert sd_count == 1, f"source_document INSERT count = {sd_count}, expected 1"
    # 红线: 不删表 / 不 DROP COLUMN / 不 DELETE FROM 真实数据
    text_no_comments = _strip_sql_comments(text)
    forbidden = [
        "DROP TABLE", "DROP COLUMN", "DROP INDEX",
        "DELETE FROM", "TRUNCATE",
    ]
    for f in forbidden:
        assert f not in text_no_comments, (
            f"seed_m4_4_heilongjiang_real.sql (after comment strip) "
            f"contains forbidden DML/DDL: {f!r}"
        )


def test_seed_m4_4_sql_lineage_is_demo_false_isolation():
    """641-A.2 seed SQL 所有 6 政策表行 lineage JSONB is_demo='false'."""
    assert SEED_SQL.exists()
    text = SEED_SQL.read_text(encoding="utf-8")
    # 6 政策表均需有 is_demo='false' (或 is_demo=false JSON)
    policy_tables = [
        "policy_document", "policy_target", "policy_measure",
        "government_commitment", "commitment_progress", "project_event",
    ]
    for tbl in policy_tables:
        # 抓 INSERT block (粗正则)
        block = re.search(
            rf"INSERT INTO {tbl}.*?ON CONFLICT",
            text, re.DOTALL,
        )
        assert block, f"seed SQL missing INSERT INTO {tbl} ... ON CONFLICT block"
        bb = block.group(0)
        # 含 is_demo='false' 或 "is_demo": "false" 或 jsonb_build_object 'is_demo','false'
        is_false = (
            "is_demo" in bb
            and ("false" in bb or "'false'" in bb)
        )
        assert is_false, f"{tbl} block missing is_demo='false' (real sentinel)"
    # 红线: 真实化 seed 不含 is_demo='true' (避免与 640 demo 混淆)
    text_compact = text.replace(" ", "").replace("\n", "").replace("\t", "")
    # "is_demo":"true" 不能出现
    assert '"is_demo":"true"' not in text_compact, (
        "seed_m4_4_heilongjiang_real.sql must not contain lineage is_demo='true' "
        "(real seed only; demo is_demo=true belongs to 640 seed only)"
    )
    # 也禁止 JSON false (必须是字符串 "false" per sentinel)
    # 但我们的 seed 用的是 'false' as JSON string value
    # 因此 is_demo false (JSON boolean) 不应出现
    bad_bool = re.search(r'"is_demo"\s*:\s*false\b(?!")', text_compact)
    assert not bad_bool, (
        "seed SQL must not contain JSON boolean false for is_demo "
        "(must be string 'false' per docs/33 §3.2 sentinel)"
    )


def test_seed_m4_4_sql_real_sha_distinct_from_demo_sha():
    """641-A.2 真实 SHA (from 641-A.1) ≠ 640 demo SHA '0…02'."""
    assert SEED_SQL.exists()
    text = SEED_SQL.read_text(encoding="utf-8")
    # 真实 SHA (64 char hex from 641-A.1) 必须出现在 seed
    assert REAL_SHA_641 in text, (
        f"seed_m4_4_heilongjiang_real.sql missing real SHA {REAL_SHA_641}"
    )
    # 真实 SHA 不应是 demo SHA (排除 0…02 / 0…01 模式)
    assert REAL_SHA_641 != DEMO_SHA_640
    assert REAL_SHA_641 != "0000000000000000000000000000000000000000000000000000000000000001"
    # 真实 URL 必须出现
    real_url = "https://www.hlj.gov.cn/hlj/c108378/202608/c00_31971131.shtml"
    assert real_url in text, (
        f"seed_m4_4_heilongjiang_real.sql missing real URL {real_url}"
    )
    # R3-E provenance chain_id='real_641_heilongjiang' 必须出现
    assert "real_641_heilongjiang" in text, (
        "seed SQL missing R3-E provenance chain_id='real_641_heilongjiang'"
    )
    # 红线: 真实化 seed 不含 640 demo SHA 0…02 (避免 demo 污染混淆)
    assert DEMO_SHA_640 not in text, (
        f"seed_m4_4_heilongjiang_real.sql must not contain 640 demo SHA "
        f"{DEMO_SHA_640} (real SHA must be distinct)"
    )
    # 红线: 真实化 seed 不含 639 demo SHA 0…01
    demo_sha_639 = "0000000000000000000000000000000000000000000000000000000000000001"
    assert demo_sha_639 not in text, (
        "seed_m4_4_heilongjiang_real.sql must not contain 639 demo SHA 0…01"
    )


def test_doc_61_has_six_sections():
    """docs/61 含 ## 1.-## 6. 六段 + 标头属性."""
    assert DOC_61.exists(), f"docs/61 missing: {DOC_61}"
    text = DOC_61.read_text(encoding="utf-8")
    for n in ("## 1.", "## 2.", "## 3.", "## 4.", "## 5.", "## 6."):
        assert n in text, f"docs/61 missing section {n}"
    # 标头属性
    assert "61" in text[:200]
    assert "2026-09-01" in text
    assert "641" in text


def test_doc_61_no_pass_announcement():
    """docs/61 不宣称 M2/M4/Gate PASS (智能排除 disclaimer 否定句)."""
    assert DOC_61.exists()
    text = DOC_61.read_text(encoding="utf-8")
    sec6 = text[text.index("## 6."):]
    for keyword in ("M4 PASS", "Gate PASS", "M2 PASS"):
        positive_lines = [
            line for line in sec6.splitlines()
            if keyword in line and "不宣布" not in line
            and "不声称" not in line and "不宣称" not in line
            and "不宣告" not in line
        ]
        assert not positive_lines, (
            f"docs/61 §6 contains positive {keyword} claim: "
            f"{positive_lines!r}"
        )
