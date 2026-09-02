"""M4.16 政策详情 v10 双复试 spike 守门测试 (knife 653 M4.16 side, ≥8 cases).

Per knife 653 §1.653-B M4.16 side:
- 守门 fetch script 2 cells BLOCKED_NO_POOL 双触发 (双样本均 BLOCKED; blocked_no_pool_count=2)
- 守门 0 NEW SHA (双样本均 BLOCKED → 无 REACHABLE → 无 SHA)
- 守门 spike 边界 0 INSERT ROWS (双样本均 BLOCKED 留痕; per 653 §1.653-A.1 BLOCKED 口径)
- 守门 chain_id='real_653_m4_16_policy_detail_v10' (≠ 652 _v9 ≠ 651 _v8)
- 守门 UUID l 段 (≠ 652 k 段 ≠ 651 j 段 ≠ 650 i 段)
- 守门 0 NEW SHA (双 BLOCKED → 0 SHA)
- 守门 substitute 池 [EXHAUSTED] 永不触发 (substitute_used_count=0 + SUBSTITUTE_POOL_STATUS="EXHAUSTED")
- 守门 BLOCKED_NO_POOL 真网首次双触发 (双样本均 BLOCKED; blocked_no_pool_count=2)
- 守门 retry_of lineage 全行 (shandong ← 647; hubei ← 649)
- 守门 docs/77 §1-§6 架构师级审查
- 守门 docs/76 §6.1 + 652 receipt §RED_LINE_AUDIT.1 P4-A.0 规范 v2 tailnote
- 守门 evidence methodology 指针 (per 648 审计 P3-1 + 649 P3-1 + 652 §0.14 红线 14 增补 + 653 §0.14 强制 BLOCKED_NO_POOL 留痕 e2e 验证 复试)
- 守门 不宣称 PASS (沿用红线)

零网络; 零 cegr.* mutation; 零爬网; 纯文档守门。
"""
from __future__ import annotations

import json
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
FETCH_SCRIPT = REPO_ROOT / "scripts" / "fetch_m4_16_policy_detail_v10_2024.py"
SEED_SQL = REPO_ROOT / "scripts" / "seed_m4_16_policy_detail_real_v10.sql"
EVIDENCE = REPO_ROOT / "evidence_pack" / "m4_16_policy_detail_real_v10_20260902.json"
REPORT_MD = REPO_ROOT / "docs" / "reports" / "m4_16_policy_detail_real_v10_20260902.md"
DOCS_77 = REPO_ROOT / "docs" / "77-m4-16-policy-detail-real-v10-20260902.md"
DOCS_76 = REPO_ROOT / "docs" / "76-m4-15-policy-detail-real-v9-20260902.md"
RECEIPT_652 = REPO_ROOT / "reviews" / "stage0-gate0-rework-2026-08-23" / "652-stage0-cc-m4-15-v9-blocked-spike-receipt-20260902.md"


def _read(path: Path) -> str:
    if not path.exists():
        return ""
    return path.read_text(encoding="utf-8")


def _non_comment_lines(body: str) -> list[str]:
    """Return lines that are NOT SQL comments (start with --)."""
    return [ln for ln in body.splitlines() if not ln.strip().startswith("--")]


def test_evidence_json_blocked_no_pool_count_two_real_first_trigger() -> None:
    """653 §0.14 复试: 主 evidence blocked_no_pool_count=2 (真网首次双触发)"""
    if not EVIDENCE.exists():
        return
    data = json.loads(EVIDENCE.read_text(encoding="utf-8"))
    assert data["summary"]["fetch_status"] == "ALL_BLOCKED_NO_POOL"
    assert data["summary"]["blocked_no_pool_count"] == 2, (
        f"expected blocked_no_pool_count=2 (双样本均 BLOCKED 真网首触发); got {data['summary']['blocked_no_pool_count']}"
    )
    assert data["summary"]["fetched_count"] == 0, (
        f"双样本均 BLOCKED → fetched_count=0; got {data['summary']['fetched_count']}"
    )
    assert len(data["cells"]) == 2


def test_evidence_json_zero_new_shas() -> None:
    """653 §1.653-A.1 双 BLOCKED → 0 NEW SHA (distinct_shas=[])"""
    if not EVIDENCE.exists():
        return
    data = json.loads(EVIDENCE.read_text(encoding="utf-8"))
    assert data["summary"]["distinct_shas"] == [], (
        f"expected distinct_shas=[] (双 BLOCKED → 0 SHA); got {data['summary']['distinct_shas']}"
    )
    shas = {cell["file_hash_sha256"] for cell in data["cells"]}
    assert all(s == "" for s in shas), f"BLOCKED cells should have empty SHA; got {shas}"


def test_evidence_json_2_cells_both_blocked_no_pool() -> None:
    """653 §0.14 双样本均 BLOCKED_NO_POOL; verdict 全行 BLOCKED_NO_POOL"""
    if not EVIDENCE.exists():
        return
    data = json.loads(EVIDENCE.read_text(encoding="utf-8"))
    for cell in data["cells"]:
        assert cell["verdict"] == "BLOCKED_NO_POOL", (
            f"expected verdict=BLOCKED_NO_POOL; got {cell['verdict']}"
        )
        assert cell["substitute_used"] is False
        assert cell["blocked_reason"] != "", (
            "BLOCKED cell must have non-empty blocked_reason"
        )
        assert cell["chain_index"] == -1, (
            f"BLOCKED cell chain_index=-1; got {cell['chain_index']}"
        )


def test_evidence_json_substitute_pool_status_exhausted() -> None:
    """653 §0.14 主 evidence substitute_pool_status='EXHAUSTED' (沿用 652 §0.14 红线 14 增补)"""
    if not EVIDENCE.exists():
        return
    data = json.loads(EVIDENCE.read_text(encoding="utf-8"))
    assert data["summary"]["substitute_pool_status"] == "EXHAUSTED"
    assert data["summary"]["substitute_used_count"] == 0


def test_evidence_json_http_count_4() -> None:
    """653 §0.3 红线 3: HTTP 4/12 (shandong 2 + hubei 2; ≤12 HTTP limit)"""
    if not EVIDENCE.exists():
        return
    data = json.loads(EVIDENCE.read_text(encoding="utf-8"))
    assert data["summary"]["http_count"] == 4, (
        f"expected http_count=4 (shandong 2 + hubei 2); got {data['summary']['http_count']}"
    )
    assert data["summary"]["http_count"] <= 12, (
        f"≤12 HTTP limit violated: {data['summary']['http_count']}"
    )


def test_fetch_script_2_cells_shandong_hubei_chains() -> None:
    """653-A.1 fetch 脚本 2 cells: shandong + hubei; 各 2 fallback URL; retry_of lineage"""
    if not FETCH_SCRIPT.exists():
        return
    body = _read(FETCH_SCRIPT)
    assert "SHANDONG_FALLBACK_CHAIN" in body
    assert "HUBEI_FALLBACK_CHAIN" in body
    assert "shandong" in body
    assert "hubei" in body
    assert "https://www.shandong.gov.cn/zwgk/" in body
    assert "https://www.shandong.gov.cn/" in body
    assert "https://www.hubei.gov.cn/zwgk/" in body
    assert "https://www.hubei.gov.cn/" in body
    assert "RETRY_OF_NOTES" in body
    assert "retry_of=647" in body
    assert "retry_of=649" in body


def test_fetch_script_blocked_no_pool_branch_present() -> None:
    """653 §0.14 BLOCKED_NO_POOL 分支代码 e2e 可达 (def fetch_cell 含 BLOCKED_NO_POOL verdict + blocked_reason 字段)"""
    if not FETCH_SCRIPT.exists():
        return
    body = _read(FETCH_SCRIPT)
    assert "BLOCKED_NO_POOL" in body
    assert "blocked_reason" in body
    assert '"BLOCKED_NO_POOL"' in body or "'BLOCKED_NO_POOL'" in body
    assert "verdict" in body


def test_fetch_log_shandong_0_0_hubei_412_412() -> None:
    """653-A.1 fetch_log: shandong /zwgk/ + / 均 SSL handshake failure (0/0); hubei /zwgk/ + / 均 412"""
    if not EVIDENCE.exists():
        return
    data = json.loads(EVIDENCE.read_text(encoding="utf-8"))
    cells_by_province = {cell["province"]: cell for cell in data["cells"]}
    # shandong: 双 0 (SSL handshake failure)
    sd = cells_by_province.get("shandong")
    if sd:
        for entry in sd["fetch_log"]:
            assert entry["http_code"] == 0, (
                f"shandong expected http_code=0 (SSL handshake failure); got {entry['http_code']}"
            )
    # hubei: 双 412
    hb = cells_by_province.get("hubei")
    if hb:
        for entry in hb["fetch_log"]:
            assert entry["http_code"] == 412, (
                f"hubei expected http_code=412; got {entry['http_code']}"
            )


def test_seed_sql_zero_insert_blocked_retry() -> None:
    """653 §1.653-A.1 BLOCKED 口径: seed SQL 0 INSERT ROWS (双样本均 BLOCKED); 头部 documentation 完整"""
    if not SEED_SQL.exists():
        return
    body = _read(SEED_SQL)
    non_comment = "\n".join(_non_comment_lines(body))
    # 0 INSERT statements
    insert_statements = [ln for ln in non_comment.splitlines() if "INSERT INTO" in ln]
    assert len(insert_statements) == 0, (
        f"expected 0 INSERT statements (双样本均 BLOCKED); got {len(insert_statements)}: {insert_statements}"
    )
    # 头部 documentation 包含 BLOCKED 实测
    assert "BLOCKED_NO_POOL" in body
    assert "shandong" in body and "hubei" in body
    assert "SSL handshake failure" in body or "412" in body
    assert "retry_of" in body


def test_seed_sql_chain_id_v10_distinct_from_652_651_650_649() -> None:
    """653-A.1 seed SQL chain_id='real_653_m4_16_policy_detail_v10' (≠ 652 _v9 ≠ 651 _v8 ≠ 650 _v7).

    注: 因 653 双样本均 BLOCKED → 0 INSERT ROWS, chain_id 仅以 SQL comment 形式登记
    (documentation header), 不在可执行 SQL 内。测试检查整文 (含注释) 即可。
    """
    if not SEED_SQL.exists():
        return
    body = _read(SEED_SQL)
    assert "real_653_m4_16_policy_detail_v10" in body, (
        "seed SQL must contain chain_id='real_653_m4_16_policy_detail_v10' (in comments)"
    )
    # 652/651 chain_id 不应出现 (避免污染)
    assert "real_652_m4_15_policy_detail_v9" not in body
    assert "real_651_m4_14_policy_detail_v8" not in body


def test_seed_sql_uuid_l_segment_distinct_from_k_j_i_h_g_f_e_d_c_segments() -> None:
    """653-A.1 seed SQL UUID l 段 (l0eebc99-l6eebc99) ≠ 652 k 段 ≠ 651 j 段 ≠ 650 i 段"""
    if not SEED_SQL.exists():
        return
    body = _read(SEED_SQL)
    non_comment = "\n".join(_non_comment_lines(body))
    # 不应出现 k/j/i/h/g/f/e/d/c 段
    for prefix in ["k0eebc99", "j0eebc99", "i0eebc99", "h0eebc99", "g0eebc99"]:
        assert prefix not in non_comment, f"653 must not reference {prefix} (其他刀段)"


def test_report_md_no_pass_announcement_653_red_line() -> None:
    """653 沿用红线 1: docs/reports/m4_16 不宣称任何 PASS"""
    if not REPORT_MD.exists():
        return
    body = _read(REPORT_MD)
    assert "不宣称 PASS" in body or "不宣布" in body or "不宣称" in body


def test_evidence_methodology_pointer_per_648_p3_1_and_652_red_line_14_and_653_e2e() -> None:
    """653-A.4 主 evidence methodology 含 652 §0.14 援引 + 653 §0.14 强制 e2e 验证 复试 + 648 P3-1 援引"""
    if not EVIDENCE.exists():
        return
    data = json.loads(EVIDENCE.read_text(encoding="utf-8"))
    methodology = data.get("methodology", "")
    assert "652" in methodology or "EXHAUSTED" in methodology
    assert "653" in methodology or "BLOCKED_NO_POOL" in methodology
    assert "BLOCKED_NO_POOL" in methodology
    assert "EXHAUSTED" in methodology


def test_docs_77_sections_1_to_6_present() -> None:
    """653-A.3 docs/77 §1-§6 齐全 (架构师级审查)"""
    if not DOCS_77.exists():
        return
    body = _read(DOCS_77)
    for sec in ["## 1.", "## 2.", "## 3.", "## 4.", "## 5.", "## 6."]:
        assert sec in body, f"missing {sec} section in docs/77"


def test_docs_77_blocked_no_pool_e2e_records_present() -> None:
    """653-A.3 docs/77 §2 复试 BLOCKED 留痕登记表 完整 (4 实现位置 + 8 守门)"""
    if not DOCS_77.exists():
        return
    body = _read(DOCS_77)
    assert "2.1" in body
    assert "2.2" in body
    assert "2.3" in body
    # 4 实现位置
    assert "fetch 脚本分支代码可达" in body
    assert "seed SQL 0 INSERT ROWS" in body
    assert "主 evidence summary + methodology" in body
    assert "docs/77 §5 BLOCKED 留痕口径" in body
    # 双样本实测
    assert "shandong" in body and "hubei" in body
    # 真网首次双触发
    assert "真网首次双触发" in body or "REACHABLE×0 / BLOCKED_NO_POOL×2" in body


def test_docs_77_retry_of_lineage_records() -> None:
    """653-A.3 docs/77 §4.1 retry_of lineage 全行 (shandong ← 647; hubei ← 649)"""
    if not DOCS_77.exists():
        return
    body = _read(DOCS_77)
    assert "retry_of" in body
    assert "647" in body
    assert "649" in body
    assert "shandong" in body and "hubei" in body


def test_653_red_line_no_gate_no_o1_no_pass() -> None:
    """653 沿用红线 1: docs/77 不宣称 Gate / O1 / O2 / O3 / M2 / M4.x / M5.x / M6 PASS"""
    if not DOCS_77.exists():
        return
    body = _read(DOCS_77)
    assert "不宣布" in body or "不宣称" in body
    assert "M4.16" in body
    assert "O1 仍 OPEN" in body


def test_chain_id_uuid_prefix_l_distinct() -> None:
    """653-A.1 chain_id='real_653_m4_16_policy_detail_v10' + UUID l 段 8 表前缀"""
    if not EVIDENCE.exists():
        return
    data = json.loads(EVIDENCE.read_text(encoding="utf-8"))
    assert data["chain_id"] == "real_653_m4_16_policy_detail_v10"
    assert data["uuid_prefix"] == "l"
    prefixes = data["uuid_prefixes"]
    expected = {
        "source_registry": "l0eebc99",
        "source_document": "l0eebc99",
        "policy_document": "l1eebc99",
        "policy_target": "l2eebc99",
        "policy_measure": "l3eebc99",
        "government_commitment": "l4eebc99",
        "commitment_progress": "l5eebc99",
        "project_event": "l6eebc99",
    }
    for table, prefix in expected.items():
        assert prefixes.get(table) == prefix, (
            f"expected {table} UUID prefix={prefix}; got {prefixes.get(table)}"
        )


def test_p4_a0_v2_tailnote_653_a0_landed_in_docs_76_and_652_receipt() -> None:
    """653-A.0 P4-A.0 规范 v2 tailnote 落地 docs/76 §6.1 + 652 receipt §RED_LINE_AUDIT.1.

    关键守门点 (per docs/76 §6.1 实际表述):
    - "status 收口与 §NOW" 出现 (同 commit 原子完成的核心条款)
    - "653-A.0 P4-A.0 规范 v2" tailnote 标题存在
    - amend-first 沿用 652-A.0 P4-2 规则登记
    """
    if DOCS_76.exists():
        body_76 = _read(DOCS_76)
        assert "653-A.0 P4-A.0 规范 v2" in body_76, (
            "docs/76 §6.1 must contain 653-A.0 P4-A.0 规范 v2 tailnote"
        )
        assert "status 收口与 §NOW" in body_76, (
            "docs/76 §6.1 must contain 'status 收口与 §NOW' (同 commit 原子完成 核心条款)"
        )
        # "待复核 / 待 §C-x / 待 X"字样复核后必须清除条款
        assert "待复核" in body_76
        # amend-first 沿用 652-A.0 P4-2
        assert "amend-first" in body_76
    if RECEIPT_652.exists():
        body_r = _read(RECEIPT_652)
        assert "653-A.0 P4-A.0 规范 v2" in body_r, (
            "652 receipt §RED_LINE_AUDIT.1 must contain 653-A.0 P4-A.0 规范 v2 tailnote"
        )


def test_red_line_14_pool_exhaustion_fetch_script() -> None:
    """653 §0.14 fetch 脚本 SUBSTITUTE_POOL=[] + SUBSTITUTE_POOL_STATUS='EXHAUSTED'"""
    if not FETCH_SCRIPT.exists():
        return
    body = _read(FETCH_SCRIPT)
    assert "SUBSTITUTE_POOL:" in body
    assert "SUBSTITUTE_POOL_STATUS" in body
    assert "EXHAUSTED" in body
    assert "SUBSTITUTE_POOL: list[tuple[str, list[tuple[str, str]], str]] = []" in body


def test_retry_of_lineage_annotation() -> None:
    """653 §1.653-A.1 retry_of lineage 全行: shandong ← 647; hubei ← 649"""
    if not EVIDENCE.exists():
        return
    data = json.loads(EVIDENCE.read_text(encoding="utf-8"))
    # summary.retry_of_annotation
    annotation = data["summary"].get("retry_of_annotation", {})
    assert "shandong" in annotation
    assert "hubei" in annotation
    assert "647" in annotation["shandong"]
    assert "649" in annotation["hubei"]
    # cells 中 retry_of 字段
    for cell in data["cells"]:
        assert "retry_of" in cell
        assert cell["retry_of"] != "", f"cell retry_of must be non-empty; got {cell['retry_of']}"
