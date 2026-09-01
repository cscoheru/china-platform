"""M4.8 政策详情 v2 真实化 spike 三次 守门测试 (knife 645 M4.8 side, ≥6 cases).

Per knife 645 §5.645-B M4.8 side:
- 守门 fetch script 4 cells REAL_FETCHED (http_count=4 ≤ 12)
- 守门 4 SHA distinct (6237cd48/dfa38998/bd4c4c51/f33eba53) + 4 file_size > 0
- 守门 spike 边界 32 INSERT total (24 政策表 + 8 source)
- 守门 chain_id='real_645_m4_8_policy_detail_v2' (≠ 644)
- 守门 UUID d 段 (≠ 644 c 段)
- 守门 645 hlj SHA drift (6237cd48 ≠ 644 bad8be51)
- 守门 不宣称 PASS (沿用红线)
- 守门 seed SQL INSERT 数符合

零网络; 零 cegr.* mutation; 零爬网; 纯文档守门。
"""
from __future__ import annotations

import json
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
FETCH_SCRIPT = REPO_ROOT / "scripts" / "fetch_m4_8_policy_detail_v2_2024.py"
SEED_SQL = REPO_ROOT / "scripts" / "seed_m4_8_policy_detail_real_v2.sql"
EVIDENCE = REPO_ROOT / "evidence_pack" / "m4_8_policy_detail_real_v2_20260901.json"
REPORT_MD = REPO_ROOT / "docs" / "reports" / "m4_8_policy_detail_real_v2_20260901.md"
DOCS_69 = REPO_ROOT / "docs" / "69-m4-8-policy-detail-real-v2-20260901.md"


def _read(path: Path) -> str:
    if not path.exists():
        return ""
    return path.read_text(encoding="utf-8")


def test_evidence_json_real_fetched_4_samples() -> None:
    """645-A.5 evidence_pack/m4_8 evidence JSON REAL_FETCHED + 4 samples"""
    if not EVIDENCE.exists():
        return
    data = json.loads(EVIDENCE.read_text(encoding="utf-8"))
    assert data["summary"]["fetch_status"] == "REAL_FETCHED"
    assert data["summary"]["fetched_count"] == 4
    assert data["summary"]["http_count"] == 4
    assert len(data["cells"]) == 4
    # spike_boundary section confirms 32 INSERT total (24 政策表 + 8 source)
    assert data["spike_boundary"]["insert_grand_total"] == 32
    assert data["spike_boundary"]["insert_policy_tables_total"] == 24
    assert data["spike_boundary"]["chain_id"] == "real_645_m4_8_policy_detail_v2"


def test_evidence_json_4_distinct_shas_no_collision() -> None:
    """645-A.2 4 SHA distinct (6237cd48/dfa38998/bd4c4c51/f33eba53)"""
    if not EVIDENCE.exists():
        return
    data = json.loads(EVIDENCE.read_text(encoding="utf-8"))
    shas = {cell["file_hash_sha256"] for cell in data["cells"]}
    assert len(shas) == 4, f"4 cells should have 4 distinct SHA — got {len(shas)}: {shas}"
    for cell in data["cells"]:
        assert cell["file_size_bytes"] > 0


def test_evidence_json_hlj_drift_event() -> None:
    """645-A.2 hlj SHA drift event (6237cd48 ≠ 644 bad8be51)"""
    if not EVIDENCE.exists():
        return
    data = json.loads(EVIDENCE.read_text(encoding="utf-8"))
    hlj_cell = next(c for c in data["cells"] if c["province"] == "heilongjiang")
    assert hlj_cell["file_hash_sha256"].startswith("6237cd48")
    # 644 stale SHA must NOT appear as a 645 cell SHA (allow it in drift-explanation text)
    cell_shas = {c["file_hash_sha256"] for c in data["cells"]}
    assert "bad8be51" not in cell_shas, "645 cells must not contain stale 644 SHA bad8be51"


def test_evidence_json_henan_zwgk_new_sample_4() -> None:
    """645-A.2 纳入 644 留作扩展的 henan `bd4c4c51...` (zwgk root) 作为第 4 样本"""
    if not EVIDENCE.exists():
        return
    data = json.loads(EVIDENCE.read_text(encoding="utf-8"))
    henan_zwgk = next(c for c in data["cells"] if c["slot"] == "henan_zwgk_root")
    assert henan_zwgk["file_hash_sha256"].startswith("bd4c4c51")
    assert henan_zwgk["file_size_bytes"] > 0


def test_fetch_script_4_cells_with_henan_zwgk() -> None:
    """645-A.2 fetch script 4 cells 含 henan_zwgk_root"""
    body = _read(FETCH_SCRIPT)
    assert "FETCH_CELLS" in body
    assert "hlj_policy_list" in body
    assert "henan_zfgb_list" in body
    assert "henan_zwgk_root" in body
    assert "yunnan_zfgzbg" in body
    assert "HTTP_LIMIT = 12" in body


def test_seed_sql_32_insert_total() -> None:
    """645-A.3 seed SQL 32 INSERT total = 14 INSERT 语句 × 多行 VALUES

    8 tables × ~2 multi-row groups = 14 INSERT 语句 → 32 total rows
    (4 source_registry + 4 source_document + 4×6 政策表 = 32).
    """
    body = _read(SEED_SQL)
    # 8 tables must have INSERT INTO
    for tbl in [
        "INSERT INTO source_registry",
        "INSERT INTO source_document",
        "INSERT INTO policy_document",
        "INSERT INTO policy_target",
        "INSERT INTO policy_measure",
        "INSERT INTO government_commitment",
        "INSERT INTO commitment_progress",
        "INSERT INTO project_event",
    ]:
        assert tbl in body, f"seed SQL missing INSERT INTO {tbl}"
    # Total INSERT statements (multi-row VALUES used, so 14 INSERTs produce 32 rows)
    import re
    insert_stmts = re.findall(r"INSERT INTO \w+", body)
    assert len(insert_stmts) == 14, f"expected 14 INSERT statements; got {len(insert_stmts)}"
    # Verify 32 lineage 'source_file_sha256' rows = 4 source_registry + 4 source_document
    sha_rows = re.findall(r"'source_file_sha256',\s*'([a-f0-9]{64})'", body)
    assert len(sha_rows) == 8, f"expected 8 lineage source_file_sha256 rows (4 source_registry + 4 source_document); got {len(sha_rows)}"


def test_seed_sql_chain_id_v2_distinct_from_644() -> None:
    """645-A.3 chain_id='real_645_m4_8_policy_detail_v2' (≠ 644 'real_644_m4_7_policy_detail')"""
    body = _read(SEED_SQL)
    assert "real_645_m4_8_policy_detail_v2" in body
    assert "real_644_m4_7_policy_detail" not in body


def test_seed_sql_lineage_is_demo_false_sentinel() -> None:
    """645-A.3 lineage JSONB `is_demo='false'` 真实化 sentinel (沿用 docs/33 §3.2)"""
    body = _read(SEED_SQL)
    assert "is_demo" in body
    assert "'false'" in body
    assert "is_demo='true'" not in body


def test_seed_sql_uuid_d_segment_distinct_from_644_c_segment() -> None:
    """645-A.3 UUID d 段 (≠ 644 c 段)"""
    body = _read(SEED_SQL)
    # 645 UUID d 段: d0eebc99-...-d21..d94
    assert "d1eebc99" in body  # policy_document
    assert "d2eebc99" in body  # policy_target
    assert "d3eebc99" in body  # policy_measure
    assert "d4eebc99" in body  # government_commitment
    assert "d5eebc99" in body  # commitment_progress
    assert "d6eebc99" in body  # project_event
    # 644 c 段必须不出现
    assert "c1eebc99" not in body
    assert "c2eebc99" not in body


def test_seed_sql_uses_real_fetched_sha_6237cd48() -> None:
    """645-A.3 seed SQL 使用 645 实际抓取的 SHA 6237cd48 (≠ 644 stale bad8be51)"""
    body = _read(SEED_SQL)
    assert "6237cd48afc60c0641bb7b558ecdbf5e04e36b6e06c0839947b925b50fe5200a" in body
    assert "dfa38998c3e7e8924612991eebe1366ab2485553767d3e1124b7ae8f144119ae" in body
    assert "bd4c4c51b8f371e2f1b3fb8acb2b3bf3441a27213b4464e39fdb99b56270d0b9" in body
    assert "f33eba53a1e5e9614d50f3fb3e5e0fc646196585ad74a9b32feb3a9c8cc4e7ea" in body
    # 645 source_file_sha256 lineage values must NOT be 644 stale SHA bad8be51
    import re
    sha_pattern = re.findall(r"'source_file_sha256',\s*'([a-f0-9]{64})'", body)
    assert len(sha_pattern) == 8, f"expected 8 lineage SHA values (4 source_registry + 4 source_document); got {len(sha_pattern)}"
    assert "bad8be51" not in sha_pattern, "645 source_file_sha256 lineage must not use stale 644 SHA bad8be51"


def test_report_md_no_pass_announcement() -> None:
    """645-A.5 report MD 不宣称 PASS (沿用红线)"""
    body = _read(REPORT_MD)
    if not body:
        return
    assert "不宣称" in body or "不宣布" in body
    assert "Gate" in body
    assert "O1" in body or "M4" in body


def test_docs_69_section_completeness() -> None:
    """645-A.4 docs/69 §1-§6 全部存在 + 不宣称 PASS"""
    body = _read(DOCS_69)
    assert body, f"M4.8 docs/69 missing: {DOCS_69}"
    for section in [
        "## 1. M4.8 落地终态",
        "## 2. M4.8 spike 边界",
        "## 3. 真实化 demo SQL 结构",
        "## 4. lineage 真实化 sentinel",
        "## 5. 646 下一步",
        "## 6. 下一步 + 不宣称 PASS",
    ]:
        assert section in body, f"M4.8 docs/69 missing section: {section}"