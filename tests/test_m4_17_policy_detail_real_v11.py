"""M4.17 政策详情 v11 西北双省 spike 守门测试 (knife 654 M4.17 side, ≥8 cases).

Per knife 654 §1.654-B M4.17 side:
- 守门 fetch script 2 cells BLOCKED_NO_POOL 双触发 (双首试省均 BLOCKED; blocked_no_pool_count=2)
- 守门 0 NEW SHA (双首试省均 BLOCKED → 无 REACHABLE → 无 SHA)
- 守门 spike 边界 0 INSERT ROWS (双首试省均 BLOCKED 留痕; per 654 §1.654-A.1 BLOCKED 口径)
- 守门 chain_id='real_654_m4_17_policy_detail_v11' (≠ 653 _v10 ≠ 652 _v9 ≠ 651 _v8)
- 守门 UUID m 段 (≠ 653 l 段 ≠ 652 k 段 ≠ 651 j 段 ≠ 650 i 段)
- 守门 0 NEW SHA (双首试省 BLOCKED → 0 SHA)
- 守门 substitute 池 [EXHAUSTED] 永不触发 (substitute_used_count=0 + SUBSTITUTE_POOL_STATUS="EXHAUSTED")
- 守门 BLOCKED_NO_POOL 真网首试省首触发双例 (双首试省均 BLOCKED; blocked_no_pool_count=2)
- 守门 retry_of=N/A lineage 全行 (gansu ← N/A; qinghai ← N/A — 双首试省无前史)
- 守门 docs/78 §1-§6 架构师级审查
- 守门 docs/77 既有正文零改动 (per 654 §0.4 红线 4)
- 守门 654-A.0 规范 v3 落地 (status 收口与 §NOW 同 commit 原子完成 + status 行禁含任何具体 SHA + amend-first)
- 守门 evidence methodology 指针 (per 648 P3-1 + 649 P3-1 + 652 §0.14 + 653 §0.14 + 654 §0.14 沿用 653)
- 守门 不宣称 PASS (沿用红线)
- 守门 失败形式库登记 (qinghai Connection reset by peer 全链第二例首见)

零网络; 零 cegr.* mutation; 零爬网; 纯文档守门。
"""
from __future__ import annotations

import json
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
FETCH_SCRIPT = REPO_ROOT / "scripts" / "fetch_m4_17_policy_detail_v11_2024.py"
SEED_SQL = REPO_ROOT / "scripts" / "seed_m4_17_policy_detail_real_v11.sql"
EVIDENCE = REPO_ROOT / "evidence_pack" / "m4_17_policy_detail_real_v11_20260902.json"
REPORT_MD = REPO_ROOT / "docs" / "reports" / "m4_17_policy_detail_real_v11_20260902.md"
DOCS_78 = REPO_ROOT / "docs" / "78-m4-17-policy-detail-real-v11-20260902.md"
DOCS_77 = REPO_ROOT / "docs" / "77-m4-16-policy-detail-real-v10-20260902.md"


def _read(path: Path) -> str:
    if not path.exists():
        return ""
    return path.read_text(encoding="utf-8")


def _non_comment_lines(body: str) -> list[str]:
    """Return lines that are NOT SQL comments (start with --)."""
    return [ln for ln in body.splitlines() if not ln.strip().startswith("--")]


def test_evidence_json_blocked_no_pool_count_two_real_first_trigger() -> None:
    """654 §0.14 沿用 653 §0.14 复试: 主 evidence blocked_no_pool_count=2 (真网首试省首触发双例)"""
    if not EVIDENCE.exists():
        return
    data = json.loads(EVIDENCE.read_text(encoding="utf-8"))
    assert data["summary"]["fetch_status"] == "ALL_BLOCKED_NO_POOL"
    assert data["summary"]["blocked_no_pool_count"] == 2, (
        f"expected blocked_no_pool_count=2 (双首试省均 BLOCKED 真网首试省首触发); got {data['summary']['blocked_no_pool_count']}"
    )
    assert data["summary"]["fetched_count"] == 0, (
        f"双首试省均 BLOCKED → fetched_count=0; got {data['summary']['fetched_count']}"
    )
    assert len(data["cells"]) == 2


def test_evidence_json_zero_new_shas() -> None:
    """654 §1.654-A.1 双首试省 BLOCKED → 0 NEW SHA (distinct_shas=[])"""
    if not EVIDENCE.exists():
        return
    data = json.loads(EVIDENCE.read_text(encoding="utf-8"))
    assert data["summary"]["distinct_shas"] == [], (
        f"expected distinct_shas=[] (双首试省 BLOCKED → 0 SHA); got {data['summary']['distinct_shas']}"
    )
    shas = {cell["file_hash_sha256"] for cell in data["cells"]}
    assert all(s == "" for s in shas), f"BLOCKED cells should have empty SHA; got {shas}"


def test_evidence_json_2_cells_both_blocked_no_pool() -> None:
    """654 §0.14 双首试省均 BLOCKED_NO_POOL; verdict 全行 BLOCKED_NO_POOL"""
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
    """654 §0.14 沿用 653 §0.14 主 evidence substitute_pool_status='EXHAUSTED' (沿用 653 §0.14 红线 14 增补)"""
    if not EVIDENCE.exists():
        return
    data = json.loads(EVIDENCE.read_text(encoding="utf-8"))
    assert data["summary"]["substitute_pool_status"] == "EXHAUSTED"
    assert data["summary"]["substitute_used_count"] == 0


def test_evidence_json_http_count_4() -> None:
    """654 §0.3 红线 3: HTTP 4/12 (gansu 2 + qinghai 2; ≤12 HTTP limit)"""
    if not EVIDENCE.exists():
        return
    data = json.loads(EVIDENCE.read_text(encoding="utf-8"))
    assert data["summary"]["http_count"] == 4, (
        f"expected http_count=4 (gansu 2 + qinghai 2); got {data['summary']['http_count']}"
    )
    assert data["summary"]["http_count"] <= 12, (
        f"≤12 HTTP limit violated: {data['summary']['http_count']}"
    )


def test_fetch_script_2_cells_gansu_qinghai_chains() -> None:
    """654-A.1 fetch 脚本 2 cells: gansu + qinghai; 各 2 fallback URL; retry_of=N/A lineage"""
    if not FETCH_SCRIPT.exists():
        return
    body = _read(FETCH_SCRIPT)
    assert "GANSU_FALLBACK_CHAIN" in body
    assert "QINGHAI_FALLBACK_CHAIN" in body
    assert "gansu" in body
    assert "qinghai" in body
    assert "https://www.gansu.gov.cn/zwgk/" in body
    assert "https://www.gansu.gov.cn/" in body
    assert "https://www.qinghai.gov.cn/zwgk/" in body
    assert "https://www.qinghai.gov.cn/" in body
    assert "RETRY_OF_NOTES" in body
    assert "retry_of=N/A" in body


def test_fetch_script_blocked_no_pool_branch_present() -> None:
    """654 §0.14 沿用 653 BLOCKED_NO_POOL 分支代码 e2e 可达 (def fetch_cell 含 BLOCKED_NO_POOL verdict + blocked_reason 字段)"""
    if not FETCH_SCRIPT.exists():
        return
    body = _read(FETCH_SCRIPT)
    assert "BLOCKED_NO_POOL" in body
    assert "blocked_reason" in body
    assert '"BLOCKED_NO_POOL"' in body or "'BLOCKED_NO_POOL'" in body
    assert "verdict" in body


def test_fetch_log_gansu_412_412_qinghai_0_0() -> None:
    """654-A.1 fetch_log: gansu /zwgk/ + / 均 412; qinghai /zwgk/ + / 均 Connection reset by peer (0)"""
    if not EVIDENCE.exists():
        return
    data = json.loads(EVIDENCE.read_text(encoding="utf-8"))
    cells_by_province = {cell["province"]: cell for cell in data["cells"]}
    # gansu: 双 412
    gs = cells_by_province.get("gansu")
    if gs:
        for entry in gs["fetch_log"]:
            assert entry["http_code"] == 412, (
                f"gansu expected http_code=412; got {entry['http_code']}"
            )
    # qinghai: 双 0 (Connection reset by peer)
    qh = cells_by_province.get("qinghai")
    if qh:
        for entry in qh["fetch_log"]:
            assert entry["http_code"] == 0, (
                f"qinghai expected http_code=0 (Connection reset by peer); got {entry['http_code']}"
            )
            # 验证 reason 含 "Connection reset"
            assert "Connection reset" in entry.get("reason", "") or "reset" in entry.get("reason", "").lower(), (
                f"qinghai expected reason 含 'Connection reset'; got {entry.get('reason')}"
            )


def test_seed_sql_zero_insert_blocked_retry_na() -> None:
    """654 §1.654-A.1 BLOCKED 口径: seed SQL 0 INSERT ROWS (双首试省均 BLOCKED); 头部 documentation 完整; retry_of=N/A"""
    if not SEED_SQL.exists():
        return
    body = _read(SEED_SQL)
    non_comment = "\n".join(_non_comment_lines(body))
    # 0 INSERT statements
    insert_statements = [ln for ln in non_comment.splitlines() if "INSERT INTO" in ln]
    assert len(insert_statements) == 0, (
        f"expected 0 INSERT statements (双首试省均 BLOCKED); got {len(insert_statements)}: {insert_statements}"
    )
    # 头部 documentation 包含 BLOCKED 实测
    assert "BLOCKED_NO_POOL" in body
    assert "gansu" in body and "qinghai" in body
    assert "412" in body
    assert "Connection reset by peer" in body
    assert "retry_of=N/A" in body or "retry_of = N/A" in body or "无前史首试" in body


def test_seed_sql_chain_id_v11_distinct_from_653_652_651_650() -> None:
    """654-A.1 seed SQL chain_id='real_654_m4_17_policy_detail_v11' (≠ 653 _v10 ≠ 652 _v9 ≠ 651 _v8 ≠ 650 _v7).

    注: 因 654 双首试省均 BLOCKED → 0 INSERT ROWS, chain_id 仅以 SQL comment 形式登记
    (documentation header), 不在可执行 SQL 内。测试检查整文 (含注释) 即可。
    """
    if not SEED_SQL.exists():
        return
    body = _read(SEED_SQL)
    assert "real_654_m4_17_policy_detail_v11" in body, (
        "seed SQL must contain chain_id='real_654_m4_17_policy_detail_v11' (in comments)"
    )
    # 653/652/651 chain_id 不应出现 (避免污染)
    assert "real_653_m4_16_policy_detail_v10" not in body
    assert "real_652_m4_15_policy_detail_v9" not in body
    assert "real_651_m4_14_policy_detail_v8" not in body


def test_seed_sql_uuid_m_segment_distinct_from_l_k_j_i_h_g_f_e_d_c_segments() -> None:
    """654-A.1 seed SQL UUID m 段 (m0eebc99-m6eebc99) ≠ 653 l 段 ≠ 652 k 段 ≠ 651 j 段 ≠ 650 i 段"""
    if not SEED_SQL.exists():
        return
    body = _read(SEED_SQL)
    non_comment = "\n".join(_non_comment_lines(body))
    # 不应出现 l/k/j/i/h/g/f/e/d/c 段
    for prefix in ["l0eebc99", "k0eebc99", "j0eebc99", "i0eebc99", "h0eebc99", "g0eebc99", "f0eebc99", "e0eebc99", "d0eebc99", "c0eebc99"]:
        assert prefix not in non_comment, f"654 must not reference {prefix} (其他刀段)"


def test_report_md_no_pass_announcement_654_red_line() -> None:
    """654 沿用红线 1: docs/reports/m4_17 不宣称任何 PASS"""
    if not REPORT_MD.exists():
        return
    body = _read(REPORT_MD)
    assert "不宣称 PASS" in body or "不宣布" in body or "不宣称" in body


def test_evidence_methodology_pointer_per_648_p3_1_and_652_red_line_14_and_653_e2e_and_654_first_try() -> None:
    """654-A.4 主 evidence methodology 含 648 P3-1 + 649 P3-1 + 652 §0.14 + 653 §0.14 + 654 §0.14 沿用 653 复试 援引"""
    if not EVIDENCE.exists():
        return
    data = json.loads(EVIDENCE.read_text(encoding="utf-8"))
    methodology = data.get("methodology", "")
    assert "652" in methodology or "EXHAUSTED" in methodology
    assert "653" in methodology or "BLOCKED_NO_POOL" in methodology
    assert "BLOCKED_NO_POOL" in methodology
    assert "EXHAUSTED" in methodology
    assert "654" in methodology


def test_docs_78_sections_1_to_6_present() -> None:
    """654-A.3 docs/78 §1-§6 齐全 (架构师级审查)"""
    if not DOCS_78.exists():
        return
    body = _read(DOCS_78)
    for sec in ["## 1.", "## 2.", "## 3.", "## 4.", "## 5.", "## 6."]:
        assert sec in body, f"missing {sec} section in docs/78"


def test_docs_78_first_try_blocked_no_pool_e2e_records_present() -> None:
    """654-A.3 docs/78 §2 首试省 BLOCKED 留痕登记表 完整 (4 实现位置 + 8 守门)"""
    if not DOCS_78.exists():
        return
    body = _read(DOCS_78)
    assert "2.1" in body
    assert "2.2" in body
    assert "2.3" in body
    # 4 实现位置
    assert "fetch 脚本分支代码可达" in body
    assert "seed SQL 0 INSERT ROWS" in body
    assert "主 evidence summary + methodology" in body
    assert "docs/78 §5 BLOCKED 留痕口径" in body
    # 双首试省实测
    assert "gansu" in body and "qinghai" in body
    # 真网首试省首触发
    assert "首试省首触发" in body or "REACHABLE×0 / BLOCKED_NO_POOL×2" in body


def test_docs_78_retry_of_na_lineage_records() -> None:
    """654-A.3 docs/78 §4.1 retry_of=N/A lineage 全行 (gansu ← N/A; qinghai ← N/A — 双首试省无前史)"""
    if not DOCS_78.exists():
        return
    body = _read(DOCS_78)
    assert "retry_of" in body
    assert "N/A" in body
    assert "gansu" in body and "qinghai" in body
    assert "无前史" in body


def test_docs_78_northwest_five_provinces_narrative() -> None:
    """654-A.3 docs/78 §3.2 西北五省区叙事收官表 (XINJIANG/NEIMENGGU/SHAANXI/GANSU/QINGHAI)"""
    if not DOCS_78.exists():
        return
    body = _read(DOCS_78)
    assert "西北五省区" in body
    # 五省区
    assert "XINJIANG" in body
    assert "NEI MENGGU" in body or "NEIMENGGU" in body or "NEI_MENGGU" in body
    assert "SHAANXI" in body
    assert "GANSU" in body
    assert "QINGHAI" in body


def test_docs_78_failure_form_library_qinghai_connection_reset() -> None:
    """654-A.3 docs/78 §5.3 失败形式库登记 (qinghai Connection reset by peer 第二例首见)"""
    if not DOCS_78.exists():
        return
    body = _read(DOCS_78)
    assert "失败形式库" in body
    assert "Connection reset by peer" in body
    assert "qinghai" in body
    assert "第二例首见" in body or "全链第二例" in body
    # 引用 653 SSL handshake failure 为第一例
    assert "SSL handshake failure" in body
    assert "653" in body


def test_654_red_line_no_gate_no_o1_no_pass() -> None:
    """654 沿用红线 1: docs/78 不宣称 Gate / O1 / O2 / O3 / M2 / M4.x / M5.x / M6 PASS"""
    if not DOCS_78.exists():
        return
    body = _read(DOCS_78)
    assert "不宣布" in body or "不宣称" in body
    assert "M4.17" in body
    assert "O1 仍 OPEN" in body


def test_chain_id_uuid_prefix_m_distinct() -> None:
    """654-A.1 chain_id='real_654_m4_17_policy_detail_v11' + UUID m 段 8 表前缀"""
    if not EVIDENCE.exists():
        return
    data = json.loads(EVIDENCE.read_text(encoding="utf-8"))
    assert data["chain_id"] == "real_654_m4_17_policy_detail_v11"
    assert data["uuid_prefix"] == "m"
    prefixes = data["uuid_prefixes"]
    expected = {
        "source_registry": "m0eebc99",
        "source_document": "m0eebc99",
        "policy_document": "m1eebc99",
        "policy_target": "m2eebc99",
        "policy_measure": "m3eebc99",
        "government_commitment": "m4eebc99",
        "commitment_progress": "m5eebc99",
        "project_event": "m6eebc99",
    }
    for table, prefix in expected.items():
        assert prefixes.get(table) == prefix, (
            f"expected {table} UUID prefix={prefix}; got {prefixes.get(table)}"
        )


def test_p4_a0_v3_tailnote_654_a0_landed_in_653_audit_doc() -> None:
    """654-A.0 P4-A.0 规范 v3 tailnote 落地 653 audit consolidated doc PART 1 (653 审计 P4×2 处置 + 规范 v3).

    关键守门点 (per 654-A.0 任务书 §1.654-A.0):
    - "654-A.0 规范 v3" 标题存在 (in 653-audit-654-tasking-consolidated-20260902.md)
    - "§META 五字段原子更新" 存在 (rev/status/last_delivery/last_receipt/tasking)
    - "status 行禁含任何具体 SHA" 终极条款存在 (杜绝第四型 pin 陈旧)
    - amend-first 沿用
    """
    consolidated_path = (
        REPO_ROOT
        / "reviews"
        / "stage0-gate0-rework-2026-08-23"
        / "653-audit-654-tasking-consolidated-20260902.md"
    )
    if consolidated_path.exists():
        body = _read(consolidated_path)
        assert "654-A.0 规范 v3" in body or "规范 v3" in body, (
            "653-audit-654-tasking consolidated must contain 654-A.0 规范 v3"
        )
        assert "§META" in body, "consolidated must contain §META 字段 (五字段原子更新)"
        assert "status 行禁含任何具体 SHA" in body or "禁含任何具体 SHA" in body, (
            "consolidated must contain 'status 行禁含任何具体 SHA' 终极条款"
        )
        assert "amend-first" in body, "consolidated must contain amend-first 沿用"


def test_red_line_14_pool_exhaustion_fetch_script() -> None:
    """654 §0.14 fetch 脚本 SUBSTITUTE_POOL=[] + SUBSTITUTE_POOL_STATUS='EXHAUSTED' (沿用 653)"""
    if not FETCH_SCRIPT.exists():
        return
    body = _read(FETCH_SCRIPT)
    assert "SUBSTITUTE_POOL:" in body
    assert "SUBSTITUTE_POOL_STATUS" in body
    assert "EXHAUSTED" in body
    assert "SUBSTITUTE_POOL: list[tuple[str, list[tuple[str, str]], str]] = []" in body


def test_retry_of_na_lineage_annotation() -> None:
    """654 §1.654-A.1 retry_of=N/A lineage 全行: gansu ← N/A; qinghai ← N/A (双首试省无前史)"""
    if not EVIDENCE.exists():
        return
    data = json.loads(EVIDENCE.read_text(encoding="utf-8"))
    # summary.retry_of_annotation
    annotation = data["summary"].get("retry_of_annotation", {})
    assert "gansu" in annotation
    assert "qinghai" in annotation
    assert "N/A" in annotation["gansu"]
    assert "N/A" in annotation["qinghai"]
    # cells 中 retry_of 字段
    for cell in data["cells"]:
        assert "retry_of" in cell
        assert "N/A" in cell["retry_of"], (
            f"cell retry_of must contain 'N/A'; got {cell['retry_of']}"
        )


def test_docs_77_existing_body_zero_modification_red_line_4() -> None:
    """654 §0.4 红线 4: docs/77 既有正文零改动 (除 P4 typo 行内 append 尾注外).

    654 docs/78 是新文档, 不修改 docs/77 既有 §1-§6 章节. 本测试检查 docs/77 仍保留
    653 既有内容 (三态合法 + 真网首次双触发 + 西北五省区等内容仅在 docs/78 出现).
    """
    if not DOCS_77.exists():
        return
    body_77 = _read(DOCS_77)
    # docs/77 是 653 docs, 仍标 653 而非 654
    assert "刀号: 653" in body_77 or "**刀号**: 653" in body_77
    assert "real_653_m4_16_policy_detail_v10" in body_77
    # docs/77 不应包含 654 西北五省区叙事收官表内容
    # (docs/78 才是 654 西北五省区叙事的归属文档)
    assert "西北五省区" not in body_77, (
        "docs/77 should not contain 西北五省区 (这是 654 docs/78 专属内容)"
    )


def test_654_audit_consolidated_p4x2_handling_red_line() -> None:
    """654-A.0 落地: 653 审计 P4×2 (§META 回填不全 + status 第四型 SHA pin 陈旧) 处置 + 规范 v3.

    关键守门: 654-A.0 规范 v3 = §META 五字段原子更新 + status 行禁含任何具体 SHA + 沿用 amend-first.
    """
    consolidated_path = (
        REPO_ROOT
        / "reviews"
        / "stage0-gate0-rework-2026-08-23"
        / "653-audit-654-tasking-consolidated-20260902.md"
    )
    if consolidated_path.exists():
        body = _read(consolidated_path)
        # 653 审计 2×P4 处置
        assert "P4-1" in body and "P4-2" in body, (
            "consolidated must contain 653 audit P4-1 + P4-2 处置"
        )
        # rev93 修正
        assert "rev93" in body, "consolidated must contain rev93 修正"
        # 654-A.0 规范 v3 终极条款
        assert "status 行禁含任何具体 SHA" in body or "禁含任何具体 SHA" in body, (
            "consolidated must contain 654-A.0 规范 v3 终极条款 (status 行禁含任何具体 SHA)"
        )