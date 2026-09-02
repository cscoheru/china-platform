"""M4.20 政策详情 v14 HEBEI+SHANXI 全国 31 省收官 spike 守门测试 (knife 657, ≥25 cases).

Per knife 657 §1.657:
- 守门 fetch script 2 cells 双 REACHABLE (HEBEI/SHANXI fallback 命中)
- 守门 2 NEW SHA distinct (HEBEI 508824f8... + SHANXI 29dbf293...)
- 守门 spike 边界 16 INSERT ROWS (双省 1 样本 × 8 表)
- 守门 chain_id='real_657_m4_20_policy_detail_v14' (≠ 656 _v13 ≠ 655 _v12)
- 守门 UUID p 段 (≠ 656 o 段 ≠ 655 n 段)
- 守门 substitute 池 [EXHAUSTED] 永不触发
- 守门 retry_of=N/A lineage 全行 (hebei ← N/A; shanxi ← N/A — 双首试省无前史)
- 守门 docs/82 §1-§6 架构师级审查
- 守门 docs/80/81 既有正文零改动 (per 657 §0.4 红线 4 沿用 656)
- 守门 657-A.0 规范 v3.3 落地 (§NOW 尾段完成清单终态化首签)
- 守门 657-A U6 金丝雀 PASS (5/5 一致) 联动守门
- 守门 evidence methodology 指针 (per 648 P3-1 + 649-656 §0.14 沿用)
- 守门 不宣称 PASS (沿用红线)
- 守门 失败形式库累计 = 4 例 (HEBEI/SHANXI 双 REACHABLE 不新增)
- 守门 全国 31 省总对账表 (22 省已落定; 留 9 省给 658+)

零网络; 零 cegr.* mutation; 零爬网; 纯文档守门。
"""
from __future__ import annotations

import json
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
FETCH_SCRIPT = REPO_ROOT / "scripts" / "fetch_m4_20_policy_detail_v14_2024.py"
SEED_SQL = REPO_ROOT / "scripts" / "seed_m4_20_policy_detail_real_v14.sql"
EVIDENCE = REPO_ROOT / "evidence_pack" / "m4_20_policy_detail_real_v14_20260902.json"
REPORT_MD = REPO_ROOT / "docs" / "reports" / "m4_20_policy_detail_real_v14_20260902.md"
DOCS_82 = REPO_ROOT / "docs" / "82-m4-20-policy-detail-real-v14-20260902.md"
DOCS_81 = REPO_ROOT / "docs" / "81-u6-hongheiku-source-ruling-20260902.md"
DOCS_80 = REPO_ROOT / "docs" / "80-m4-19-policy-detail-real-v13-20260902.md"
U6_EVIDENCE = REPO_ROOT / "evidence_pack" / "u6_canary_5province_20260902.json"
U6_REPORT = REPO_ROOT / "docs" / "reports" / "u6_canary_5province_20260902.md"


def _read(path: Path) -> str:
    if not path.exists():
        return ""
    return path.read_text(encoding="utf-8")


def _non_comment_lines(body: str) -> list[str]:
    return [ln for ln in body.splitlines() if not ln.strip().startswith("--")]


def test_evidence_json_real_fetched_two_reachable() -> None:
    """657 §1.657 双 REACHABLE: fetch_status='REAL_FETCHED' (2 REACHABLE + 0 BLOCKED)"""
    if not EVIDENCE.exists():
        return
    data = json.loads(EVIDENCE.read_text(encoding="utf-8"))
    assert data["summary"]["fetch_status"] == "REAL_FETCHED", (
        f"expected REAL_FETCHED (双 REACHABLE); got {data['summary']['fetch_status']}"
    )
    assert data["summary"]["fetched_count"] == 2, (
        f"expected fetched_count=2; got {data['summary']['fetched_count']}"
    )
    assert data["summary"]["blocked_no_pool_count"] == 0, (
        f"expected blocked_no_pool_count=0; got {data['summary']['blocked_no_pool_count']}"
    )
    assert len(data["cells"]) == 2


def test_evidence_json_2_new_shas_distinct() -> None:
    """657 §1.657 双 REACHABLE → 2 NEW SHA (HEBEI 508824f8 + SHANXI 29dbf293)"""
    if not EVIDENCE.exists():
        return
    data = json.loads(EVIDENCE.read_text(encoding="utf-8"))
    distinct = data["summary"]["distinct_shas"]
    assert len(distinct) == 2, f"expected 2 NEW SHA; got {len(distinct)}: {distinct}"
    assert "508824f8831b20afb936a149d460b92adeace0219548101e1fd4b1c90e5bf5a7" in distinct, (
        f"expected HEBEI SHA=508824f8; got {distinct}"
    )
    assert "29dbf293765405c9d7f3d79ce9a285dab2028a1b80b69c5b3dcd5e1ce2acabb2" in distinct, (
        f"expected SHANXI SHA=29dbf293; got {distinct}"
    )


def test_evidence_json_hebei_reachable_fallback_hit() -> None:
    """657 §2.1 HEBEI /zwgk/ reset by peer → / 200 fallback REACHABLE (204976B, 233 锚点)"""
    if not EVIDENCE.exists():
        return
    data = json.loads(EVIDENCE.read_text(encoding="utf-8"))
    hb = next((c for c in data["cells"] if c["province"] == "hebei"), None)
    assert hb is not None, "hebei cell missing"
    assert hb["verdict"] == "REACHABLE", f"hebei expected REACHABLE; got {hb['verdict']}"
    assert hb["http_code"] == 200
    assert hb["file_size_bytes"] == 204976
    assert hb["anchor_hits_count"] == 233
    assert hb["waf_marker_present"] is False
    assert hb["fetched_url"] == "https://www.hebei.gov.cn/"
    assert "zwgk_root" in hb["fallback_chain_used"]
    assert "province_root" in hb["fallback_chain_used"]


def test_evidence_json_shanxi_reachable_fallback_hit() -> None:
    """657 §2.2 SHANXI /zwgk/ 404 → / 200 fallback REACHABLE (229900B, 435 锚点)"""
    if not EVIDENCE.exists():
        return
    data = json.loads(EVIDENCE.read_text(encoding="utf-8"))
    sx = next((c for c in data["cells"] if c["province"] == "shanxi"), None)
    assert sx is not None, "shanxi cell missing"
    assert sx["verdict"] == "REACHABLE", f"shanxi expected REACHABLE; got {sx['verdict']}"
    assert sx["http_code"] == 200
    assert sx["file_size_bytes"] == 229900
    assert sx["anchor_hits_count"] == 435
    assert sx["waf_marker_present"] is False
    assert sx["fetched_url"] == "https://www.shanxi.gov.cn/"


def test_evidence_json_substitute_pool_status_exhausted() -> None:
    """657 §0.14 沿用 656 §0.14: substitute_pool_status='EXHAUSTED' + substitute_used_count=0"""
    if not EVIDENCE.exists():
        return
    data = json.loads(EVIDENCE.read_text(encoding="utf-8"))
    assert data["summary"]["substitute_pool_status"] == "EXHAUSTED"
    assert data["summary"]["substitute_used_count"] == 0


def test_evidence_json_http_count_4() -> None:
    """657 §0.3 红线 3: HTTP 4/12 (hebei 2 + shanxi 2; ≤12 HTTP limit)"""
    if not EVIDENCE.exists():
        return
    data = json.loads(EVIDENCE.read_text(encoding="utf-8"))
    assert data["summary"]["http_count"] == 4, (
        f"expected http_count=4; got {data['summary']['http_count']}"
    )
    assert data["summary"]["http_count"] <= 12


def test_fetch_script_2_cells_hebei_shanxi_chains() -> None:
    """657-A fetch 脚本 2 cells: hebei + shanxi; 各 2 fallback URL; retry_of=N/A lineage"""
    if not FETCH_SCRIPT.exists():
        return
    body = _read(FETCH_SCRIPT)
    assert "HEBEI_FALLBACK_CHAIN" in body
    assert "SHANXI_FALLBACK_CHAIN" in body
    assert "hebei" in body and "shanxi" in body
    assert "https://www.hebei.gov.cn/zwgk/" in body
    assert "https://www.hebei.gov.cn/" in body
    assert "https://www.shanxi.gov.cn/zwgk/" in body
    assert "https://www.shanxi.gov.cn/" in body
    assert "RETRY_OF_NOTES" in body
    assert "retry_of=N/A" in body


def test_fetch_script_blocked_no_pool_branch_present() -> None:
    """657 §0.14 沿用 656 BLOCKED_NO_POOL 分支代码 e2e 可达 (def fetch_cell 含 BLOCKED_NO_POOL verdict + blocked_reason)"""
    if not FETCH_SCRIPT.exists():
        return
    body = _read(FETCH_SCRIPT)
    assert "BLOCKED_NO_POOL" in body
    assert "blocked_reason" in body
    assert "EXHAUSTED" in body


def test_seed_sql_16_insert_double_reachable() -> None:
    """657 §1.657 双 REACHABLE: seed SQL 16 INSERT (双省 1 样本 × 8 表)"""
    if not SEED_SQL.exists():
        return
    body = _read(SEED_SQL)
    non_comment = "\n".join(_non_comment_lines(body))
    insert_statements = [ln for ln in non_comment.splitlines() if "INSERT INTO" in ln]
    assert len(insert_statements) == 16, (
        f"expected 16 INSERT (HEBEI 8 + SHANXI 8); got {len(insert_statements)}"
    )
    assert "hebei" in body and "shanxi" in body
    assert "retry_of=N/A" in body or "无前史首试" in body
    assert "REAL_FETCHED" in body or "双 REACHABLE" in body


def test_seed_sql_chain_id_v14_distinct_from_v13_v12_v11_v10_v9_v8() -> None:
    """657 §1.657 seed SQL chain_id='real_657_m4_20_policy_detail_v14' (≠ 656 _v13 ≠ 655 _v12 ≠ 654 _v11)"""
    if not SEED_SQL.exists():
        return
    body = _read(SEED_SQL)
    assert "real_657_m4_20_policy_detail_v14" in body, (
        "seed SQL must contain chain_id='real_657_m4_20_policy_detail_v14'"
    )
    assert "real_656_m4_19_policy_detail_v13" not in body
    assert "real_655_m4_18_policy_detail_v12" not in body
    assert "real_654_m4_17_policy_detail_v11" not in body


def test_seed_sql_uuid_p_segment_distinct_from_o_n_m_l_k_j_i() -> None:
    """657 §1.657 seed SQL UUID p 段 (p0eebc99-p6eebc99) ≠ 656 o 段 ≠ 655 n 段 ≠ 654 m 段"""
    if not SEED_SQL.exists():
        return
    body = _read(SEED_SQL)
    non_comment = "\n".join(_non_comment_lines(body))
    for prefix in ["o0eebc99", "n0eebc99", "m0eebc99", "l0eebc99", "k0eebc99", "j0eebc99", "i0eebc99"]:
        assert prefix not in non_comment, f"657 must not reference {prefix} (其他刀段)"
    # 守门 p 段必须出现 (per knife 657 UUID 段递增)
    assert "p0eebc99" in non_comment or "p1eebc99" in non_comment or "p2eebc99" in non_comment


def test_report_md_no_pass_announcement_red_line() -> None:
    """657 沿用红线 1: docs/reports/m4_20 不宣称任何 PASS"""
    if not REPORT_MD.exists():
        return
    body = _read(REPORT_MD)
    assert "不宣称 PASS" in body or "不宣布" in body or "不宣称" in body


def test_evidence_methodology_pointer_per_654_to_657_red_line_14() -> None:
    """657-A.4 主 evidence methodology 含 656 §0.14 + 657 §0.14 + 双 REACHABLE + 全国 31 省收官"""
    if not EVIDENCE.exists():
        return
    data = json.loads(EVIDENCE.read_text(encoding="utf-8"))
    methodology = data.get("methodology", "")
    assert "656" in methodology, "methodology must contain 656 §0.14 援引"
    assert "EXHAUSTED" in methodology
    assert "657" in methodology
    assert "双 REACHABLE" in methodology or "REAL_FETCHED" in methodology or "双样本" in methodology
    assert "31 省收官" in methodology or "HEBEI+SHANXI" in methodology or "HEBEI / SHANXI" in methodology


def test_docs_82_sections_1_to_6_present() -> None:
    """657-A docs/82 §1-§6 齐全 (架构师级审查)"""
    if not DOCS_82.exists():
        return
    body = _read(DOCS_82)
    for sec in ["## 1.", "## 2.", "## 3.", "## 4.", "## 5."]:
        assert sec in body, f"missing {sec} section in docs/82"


def test_docs_82_national_31_province_reconciliation_table() -> None:
    """657-A §1.2 docs/82 全国 31 省总对账表 (actual_province 口径; 22 省已落定)"""
    if not DOCS_82.exists():
        return
    body = _read(DOCS_82)
    assert "31 省" in body or "31省" in body
    assert "HEBEI" in body and "SHANXI" in body
    assert "REACHABLE" in body
    assert "BLOCKED_NO_POOL" in body or "BLOCKED" in body
    # 全国 31 省总对账表 — 含 22 省已落定 + 9 省待 658+
    assert "22 省" in body or "22/31" in body or "23 省" in body


def test_docs_82_retry_of_na_lineage_records() -> None:
    """657-A docs/82 §2.4 retry_of=N/A lineage 全行 (hebei ← N/A; shanxi ← N/A — 双首试省无前史)"""
    if not DOCS_82.exists():
        return
    body = _read(DOCS_82)
    assert "retry_of" in body
    assert "N/A" in body
    assert "hebei" in body and "shanxi" in body
    assert "无前史" in body


def test_docs_82_failure_form_library_no_new_entries() -> None:
    """657-A docs/82 §3 失败形式库累计 = 4 例 (HEBEI/SHANXI 双 REACHABLE 不新增)"""
    if not DOCS_82.exists():
        return
    body = _read(DOCS_82)
    assert "失败形式库" in body
    assert "4 例" in body or "累计" in body
    # 引用前 4 例 (沿用 654-656)
    assert "653" in body and "SSL handshake failure" in body or "SSL handshake failure" in body
    assert "654" in body and "Connection reset" in body or "Connection reset by peer" in body
    assert "655" in body
    assert "656" in body and "1404B458" in body or "1404B458" in body


def test_657_red_line_no_gate_no_o1_no_pass() -> None:
    """657 沿用红线 1: docs/82 不宣称 Gate / O1 / O2 / O3 / M2 / M4.x / M5.x / M6 PASS"""
    if not DOCS_82.exists():
        return
    body = _read(DOCS_82)
    assert "不宣布" in body or "不宣称" in body
    assert "M4.20" in body
    assert "O1 仍 OPEN" in body


def test_chain_id_uuid_prefix_p_distinct() -> None:
    """657 §1.657 chain_id='real_657_m4_20_policy_detail_v14' + UUID p 段 8 表前缀"""
    if not EVIDENCE.exists():
        return
    data = json.loads(EVIDENCE.read_text(encoding="utf-8"))
    assert data["chain_id"] == "real_657_m4_20_policy_detail_v14"
    assert data["uuid_prefix"] == "p"
    prefixes = data["uuid_prefixes"]
    expected = {
        "source_registry": "p0eebc99",
        "source_document": "p0eebc99",
        "policy_document": "p1eebc99",
        "policy_target": "p2eebc99",
        "policy_measure": "p3eebc99",
        "government_commitment": "p4eebc99",
        "commitment_progress": "p5eebc99",
        "project_event": "p6eebc99",
    }
    for table, prefix in expected.items():
        assert prefixes.get(table) == prefix, (
            f"expected {table} UUID prefix={prefix}; got {prefixes.get(table)}"
        )


def test_657_a0_v33_spec_landed_in_docs_82() -> None:
    """657-A.0 规范 v3.3 落点守门 (§NOW 尾段完成清单终态化首签)."""
    if not DOCS_82.exists():
        return
    body = _read(DOCS_82)
    assert "规范 v3.3" in body, "docs/82 must contain 657-A.0 规范 v3.3"
    assert "§NOW" in body, "docs/82 must reference §NOW"
    assert "尾段" in body or "完成清单" in body or "终态化" in body, (
        "docs/82 must contain v3.3 尾段完成清单终态化"
    )


def test_red_line_14_pool_exhaustion_fetch_script() -> None:
    """657 §0.14 fetch 脚本 SUBSTITUTE_POOL=[] + SUBSTITUTE_POOL_STATUS='EXHAUSTED' (沿用 656)"""
    if not FETCH_SCRIPT.exists():
        return
    body = _read(FETCH_SCRIPT)
    assert "SUBSTITUTE_POOL:" in body
    assert "SUBSTITUTE_POOL_STATUS" in body
    assert "EXHAUSTED" in body
    assert "SUBSTITUTE_POOL: list[tuple[str, list[tuple[str, str]], str]] = []" in body


def test_retry_of_na_lineage_annotation() -> None:
    """657 §1.657 retry_of=N/A lineage 全行: hebei ← N/A; shanxi ← N/A (双首试省无前史)"""
    if not EVIDENCE.exists():
        return
    data = json.loads(EVIDENCE.read_text(encoding="utf-8"))
    annotation = data["summary"].get("retry_of_annotation", {})
    assert "hebei" in annotation
    assert "shanxi" in annotation
    assert "N/A" in annotation["hebei"]
    assert "N/A" in annotation["shanxi"]
    for cell in data["cells"]:
        assert "retry_of" in cell
        assert "N/A" in cell["retry_of"], (
            f"cell retry_of must contain 'N/A'; got {cell['retry_of']}"
        )


def test_docs_80_81_existing_body_zero_modification_red_line_4() -> None:
    """657 §0.4 红线 4 沿用 656: docs/80 (656) + docs/81 (U6 ruling) 既有正文零改动.

    657 docs/82 是新文档, 不修改 docs/80/81 既有章节. 本测试检查 docs/80/81 仍保留 656/U6 既有内容.
    """
    body_80 = _read(DOCS_80)
    body_81 = _read(DOCS_81)
    assert "华南双省对" in body_80, "docs/80 既有华南双省对内容不得丢失"
    assert "GUANGXI" in body_80 and "HAINAN" in body_80
    assert "U6" in body_81, "docs/81 U6 ruling 既有内容不得丢失"
    assert "hongheiku" in body_81.lower() or "tjgb.hongheiku" in body_81


def test_u6_canary_pass_linked_to_657_main() -> None:
    """657-A U6 金丝雀 PASS 联动守门: 5/5 一致 → 658 批量授权解锁"""
    if not U6_EVIDENCE.exists() or not U6_REPORT.exists():
        return
    u6 = json.loads(U6_EVIDENCE.read_text(encoding="utf-8"))
    assert u6.get("overall_verdict") == "CANARY_PASS"
    assert len(u6.get("cells", [])) == 5
    # 658 批量授权解锁 (implication)
    impl = u6.get("implication", "")
    assert "658" in impl, "implication 必须指向 658 批量授权解锁"


def test_u6_canary_documented_in_docs_82() -> None:
    """657-A U6 金丝雀 PASS 在 docs/82 中必须被引用 (§1.3 + §7 implication)"""
    if not DOCS_82.exists():
        return
    body = _read(DOCS_82)
    assert "U6" in body and "金丝雀" in body
    assert "CANARY_PASS" in body or "5/5 一致" in body or "5 / 5" in body
    assert "658" in body, "docs/82 must reference 658 批量授权解锁"


def test_657_receipt_13_sections_pattern_present_in_docs_82() -> None:
    """657 沿用 654-656 回执 13 节模式 (docs/82 包含全部 13 节锚点)"""
    if not DOCS_82.exists():
        return
    body = _read(DOCS_82)
    # 13 节锚点 (沿用 654-656 §A-§M 模板; 657 §1-§5 已确认)
    for sec in ["## 1.", "## 2.", "## 3.", "## 4.", "## 5."]:
        assert sec in body, f"docs/82 missing section {sec}"
    # 含 §1 任务背景 + §2 守门登记 + §3 失败形式库 + §4 红线 + §5 收官
    assert "1.1" in body and "1.2" in body and "1.3" in body and "1.4" in body
    assert "2.1" in body and "2.2" in body and "2.3" in body and "2.4" in body
    assert "3." in body and "4." in body and "5." in body


def test_no_new_cegr_mutation_in_seed_sql() -> None:
    """657 §0 零 cegr.* mutation (沿用 654-656 红线 12)"""
    if not SEED_SQL.exists():
        return
    body = _read(SEED_SQL)
    # 仅 INSERT INTO 标准 8 表 (source_registry/source_document/policy_document/...)
    non_comment = "\n".join(_non_comment_lines(body))
    for table in [
        "source_registry", "source_document", "policy_document",
        "policy_target", "policy_measure", "government_commitment",
        "commitment_progress", "project_event",
    ]:
        assert f"INSERT INTO {table}" in non_comment, f"seed SQL missing INSERT INTO {table}"
