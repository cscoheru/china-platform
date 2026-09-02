"""M4.18 政策详情 v12 西部终章双省 spike 守门测试 (knife 655 M4.18 side, ≥8 cases).

Per knife 655 §1.655-B M4.18 side:
- 守门 fetch script 2 cells PARTIAL_BLOCKED (XIZANG REACHABLE 200 + NINGXIA BLOCKED_NO_POOL 405+WAF; 混合态首刀)
- 守门 1 NEW SHA (XIZANG /zwgk/ 200 REACHABLE 直命中; SHA=855af02f)
- 守门 spike 边界 8 INSERT ROWS (XIZANG 1 样本 × 8 表; NINGXIA 0 INSERT BLOCKED 留痕; 混合态按实报)
- 守门 chain_id='real_655_m4_18_policy_detail_v12' (≠ 654 _v11 ≠ 653 _v10 ≠ 652 _v9 ≠ 651 _v8)
- 守门 UUID n 段 (≠ 654 m 段 ≠ 653 l 段 ≠ 652 k 段 ≠ 651 j 段 ≠ 650 i 段)
- 守门 blocked_no_pool_count=1 (NINGXIA 首试省首触发 BLOCKED_NO_POOL; vs 654 双触发=2, 655 混合态单触发=1)
- 守门 substitute 池 [EXHAUSTED] 永不触发 (substitute_used_count=0 + SUBSTITUTE_POOL_STATUS="EXHAUSTED")
- 守门 retry_of=N/A lineage 全行 (ningxia ← N/A; xizang ← N/A — 双首试省无前史)
- 守门 docs/79 §1-§6 架构师级审查
- 守门 docs/78 既有正文零改动 (per 655 §0.4 红线 4 沿用 654)
- 守门 655-A.0 规范 v3.1 落地 (status 零 SHA 绝对化 + 七字段原子 + amend-first)
- 守门 evidence methodology 指针 (per 648 P3-1 + 649 P3-1 + 652 §0.14 + 653 §0.14 + 654 §0.14 + 655 §0.14 沿用)
- 守门 不宣称 PASS (沿用红线)
- 守门 失败形式库登记 (NINGXIA 405 Method Not Allowed + WAF 网防 G01 marker 第三例首见)

零网络; 零 cegr.* mutation; 零爬网; 纯文档守门。
"""
from __future__ import annotations

import json
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
FETCH_SCRIPT = REPO_ROOT / "scripts" / "fetch_m4_18_policy_detail_v12_2024.py"
SEED_SQL = REPO_ROOT / "scripts" / "seed_m4_18_policy_detail_real_v12.sql"
EVIDENCE = REPO_ROOT / "evidence_pack" / "m4_18_policy_detail_real_v12_20260902.json"
REPORT_MD = REPO_ROOT / "docs" / "reports" / "m4_18_policy_detail_real_v12_20260902.md"
DOCS_79 = REPO_ROOT / "docs" / "79-m4-18-policy-detail-real-v12-20260902.md"
DOCS_78 = REPO_ROOT / "docs" / "78-m4-17-policy-detail-real-v11-20260902.md"


def _read(path: Path) -> str:
    if not path.exists():
        return ""
    return path.read_text(encoding="utf-8")


def _non_comment_lines(body: str) -> list[str]:
    """Return lines that are NOT SQL comments (start with --)."""
    return [ln for ln in body.splitlines() if not ln.strip().startswith("--")]


def test_evidence_json_partial_blocked_one_reachable_one_blocked() -> None:
    """655 §0.14 混合态首刀: 主 evidence fetch_status='PARTIAL_BLOCKED' (1 REACHABLE + 1 BLOCKED_NO_POOL)"""
    if not EVIDENCE.exists():
        return
    data = json.loads(EVIDENCE.read_text(encoding="utf-8"))
    assert data["summary"]["fetch_status"] == "PARTIAL_BLOCKED", (
        f"expected fetch_status=PARTIAL_BLOCKED (混合态); got {data['summary']['fetch_status']}"
    )
    assert data["summary"]["fetched_count"] == 1, (
        f"expected fetched_count=1 (XIZANG REACHABLE); got {data['summary']['fetched_count']}"
    )
    assert data["summary"]["blocked_no_pool_count"] == 1, (
        f"expected blocked_no_pool_count=1 (NINGXIA 首试省首触发); got {data['summary']['blocked_no_pool_count']}"
    )
    assert len(data["cells"]) == 2


def test_evidence_json_xizang_one_new_sha() -> None:
    """655 §1.655-A.1 XIZANG REACHABLE → 1 NEW SHA (855af02f); NINGXIA BLOCKED 无 SHA"""
    if not EVIDENCE.exists():
        return
    data = json.loads(EVIDENCE.read_text(encoding="utf-8"))
    assert len(data["summary"]["distinct_shas"]) == 1, (
        f"expected distinct_shas=1 (XIZANG REACHABLE); got {data['summary']['distinct_shas']}"
    )
    assert "855af02fd8ee76a1913d27b91fa3928a68b3e8131d5a5b92b2a3225499ffc82a" in data["summary"]["distinct_shas"], (
        f"expected SHA=855af02f (XIZANG); got {data['summary']['distinct_shas']}"
    )
    # 区分 REACHABLE/BLOCKED cells
    shas_by_province = {cell["province"]: cell["file_hash_sha256"] for cell in data["cells"]}
    assert shas_by_province.get("xizang") == "855af02fd8ee76a1913d27b91fa3928a68b3e8131d5a5b92b2a3225499ffc82a", (
        f"xizang SHA mismatch; got {shas_by_province.get('xizang')}"
    )
    assert shas_by_province.get("ningxia") == "", (
        f"ningxia BLOCKED should have empty SHA; got {shas_by_province.get('ningxia')}"
    )


def test_evidence_json_ningxia_blocked_no_pool_405_waf() -> None:
    """655 §0.14 NINGXIA BLOCKED_NO_POOL (首试省首触发第三例; 405 Method Not Allowed + WAF 网防 G01 marker)"""
    if not EVIDENCE.exists():
        return
    data = json.loads(EVIDENCE.read_text(encoding="utf-8"))
    cells_by_province = {cell["province"]: cell for cell in data["cells"]}
    nx = cells_by_province.get("ningxia")
    assert nx is not None, "ningxia cell must exist"
    assert nx["verdict"] == "BLOCKED_NO_POOL", (
        f"ningxia expected verdict=BLOCKED_NO_POOL; got {nx['verdict']}"
    )
    assert nx["substitute_used"] is False
    assert nx["blocked_reason"] != "", "BLOCKED cell must have non-empty blocked_reason"
    assert nx["chain_index"] == -1, f"BLOCKED cell chain_index=-1; got {nx['chain_index']}"
    # fetch_log 两级 fallback 均 405 + WAF marker
    for entry in nx["fetch_log"]:
        assert entry["http_code"] == 405, (
            f"ningxia expected http_code=405; got {entry['http_code']}"
        )
        assert entry.get("waf_marker_present") is True, (
            f"ningxia expected WAF marker present; got {entry.get('waf_marker_present')}"
        )


def test_evidence_json_xizang_reachable_200_76304_191_anchors() -> None:
    """655 §1.655-A.1 XIZANG REACHABLE (200, 76304 bytes, 191 锚点, SHA=855af02f)"""
    if not EVIDENCE.exists():
        return
    data = json.loads(EVIDENCE.read_text(encoding="utf-8"))
    cells_by_province = {cell["province"]: cell for cell in data["cells"]}
    xz = cells_by_province.get("xizang")
    assert xz is not None, "xizang cell must exist"
    assert xz["verdict"] == "REACHABLE", f"xizang expected verdict=REACHABLE; got {xz['verdict']}"
    assert xz["http_code"] == 200
    assert xz["file_size_bytes"] == 76304
    assert xz["anchor_hits_count"] == 191
    assert xz["waf_marker_present"] is False


def test_evidence_json_substitute_pool_status_exhausted() -> None:
    """655 §0.14 沿用 654 §0.14 主 evidence substitute_pool_status='EXHAUSTED'"""
    if not EVIDENCE.exists():
        return
    data = json.loads(EVIDENCE.read_text(encoding="utf-8"))
    assert data["summary"]["substitute_pool_status"] == "EXHAUSTED"
    assert data["summary"]["substitute_used_count"] == 0


def test_evidence_json_http_count_3() -> None:
    """655 §0.3 红线 3: HTTP 3/12 (ningxia 2 + xizang 1; ≤12 HTTP limit)"""
    if not EVIDENCE.exists():
        return
    data = json.loads(EVIDENCE.read_text(encoding="utf-8"))
    assert data["summary"]["http_count"] == 3, (
        f"expected http_count=3 (ningxia 2 + xizang 1); got {data['summary']['http_count']}"
    )
    assert data["summary"]["http_count"] <= 12, (
        f"≤12 HTTP limit violated: {data['summary']['http_count']}"
    )


def test_fetch_script_2_cells_ningxia_xizang_chains() -> None:
    """655-A.1 fetch 脚本 2 cells: ningxia + xizang; 各 2 fallback URL; retry_of=N/A lineage"""
    if not FETCH_SCRIPT.exists():
        return
    body = _read(FETCH_SCRIPT)
    assert "NINGXIA_FALLBACK_CHAIN" in body
    assert "XIZANG_FALLBACK_CHAIN" in body
    assert "ningxia" in body
    assert "xizang" in body
    assert "https://www.nx.gov.cn/zwgk/" in body
    assert "https://www.nx.gov.cn/" in body
    assert "https://www.xizang.gov.cn/zwgk/" in body
    assert "https://www.xizang.gov.cn/" in body
    assert "RETRY_OF_NOTES" in body
    assert "retry_of=N/A" in body


def test_fetch_script_blocked_no_pool_branch_present() -> None:
    """655 §0.14 沿用 654 BLOCKED_NO_POOL 分支代码 e2e 可达 (def fetch_cell 含 BLOCKED_NO_POOL verdict + blocked_reason 字段)"""
    if not FETCH_SCRIPT.exists():
        return
    body = _read(FETCH_SCRIPT)
    assert "BLOCKED_NO_POOL" in body
    assert "blocked_reason" in body
    assert '"BLOCKED_NO_POOL"' in body or "'BLOCKED_NO_POOL'" in body
    assert "verdict" in body


def test_fetch_log_waf_marker_detection_present() -> None:
    """655 §0.14 NINGXIA WAF marker 检测 (网防 G01 / eventID) 已在 fetch_log 内"""
    if not EVIDENCE.exists():
        return
    data = json.loads(EVIDENCE.read_text(encoding="utf-8"))
    cells_by_province = {cell["province"]: cell for cell in data["cells"]}
    nx = cells_by_province.get("ningxia")
    if nx:
        # WAF marker 字段在 fetch_log
        waf_entries = [e for e in nx["fetch_log"] if e.get("waf_marker_present")]
        assert len(waf_entries) == 2, (
            f"expected 2 WAF marker entries (ningxia /zwgk/ + /); got {len(waf_entries)}"
        )


def test_seed_sql_8_insert_xizang_0_insert_ningxia() -> None:
    """655 §1.655-A.1 混合态按实报: seed SQL 8 INSERT (XIZANG 1 样本 × 8 表) + NINGXIA 0 INSERT (BLOCKED 留痕)"""
    if not SEED_SQL.exists():
        return
    body = _read(SEED_SQL)
    non_comment = "\n".join(_non_comment_lines(body))
    insert_statements = [ln for ln in non_comment.splitlines() if "INSERT INTO" in ln]
    assert len(insert_statements) == 8, (
        f"expected 8 INSERT statements (XIZANG 1 样本 × 8 表); got {len(insert_statements)}: {insert_statements}"
    )
    # 头部 documentation 包含 BLOCKED 实测
    assert "BLOCKED_NO_POOL" in body
    assert "ningxia" in body and "xizang" in body
    assert "405" in body
    assert "WAF" in body
    assert "retry_of=N/A" in body or "retry_of = N/A" in body or "无前史首试" in body
    # NINGXIA BLOCKED 留痕注释存在
    assert "NINGXIA BLOCKED_NO_POOL 留痕" in body or "ningxia 留痕不入 INSERT" in body


def test_seed_sql_chain_id_v12_distinct_from_654_653_652_651_650() -> None:
    """655-A.1 seed SQL chain_id='real_655_m4_18_policy_detail_v12' (≠ 654 _v11 ≠ 653 _v10 ≠ 652 _v9 ≠ 651 _v8 ≠ 650 _v7)."""
    if not SEED_SQL.exists():
        return
    body = _read(SEED_SQL)
    assert "real_655_m4_18_policy_detail_v12" in body, (
        "seed SQL must contain chain_id='real_655_m4_18_policy_detail_v12'"
    )
    # 654/653/652/651 chain_id 不应出现 (避免污染)
    assert "real_654_m4_17_policy_detail_v11" not in body
    assert "real_653_m4_16_policy_detail_v10" not in body
    assert "real_652_m4_15_policy_detail_v9" not in body
    assert "real_651_m4_14_policy_detail_v8" not in body


def test_seed_sql_uuid_n_segment_distinct_from_m_l_k_j_i_segments() -> None:
    """655-A.1 seed SQL UUID n 段 (n0eebc99-n6eebc99) ≠ 654 m 段 ≠ 653 l 段 ≠ 652 k 段 ≠ 651 j 段 ≠ 650 i 段"""
    if not SEED_SQL.exists():
        return
    body = _read(SEED_SQL)
    non_comment = "\n".join(_non_comment_lines(body))
    # 不应出现 m/l/k/j/i 段
    for prefix in ["m0eebc99", "l0eebc99", "k0eebc99", "j0eebc99", "i0eebc99"]:
        assert prefix not in non_comment, f"655 must not reference {prefix} (其他刀段)"


def test_report_md_no_pass_announcement_655_red_line() -> None:
    """655 沿用红线 1: docs/reports/m4_18 不宣称任何 PASS"""
    if not REPORT_MD.exists():
        return
    body = _read(REPORT_MD)
    assert "不宣称 PASS" in body or "不宣布" in body or "不宣称" in body


def test_evidence_methodology_pointer_per_648_p3_1_and_654_red_line_14_and_655_partial_blocked() -> None:
    """655-A.4 主 evidence methodology 含 648 P3-1 + 652 §0.14 + 653 §0.14 + 654 §0.14 + 655 §0.14 援引 + 混合态按实报"""
    if not EVIDENCE.exists():
        return
    data = json.loads(EVIDENCE.read_text(encoding="utf-8"))
    methodology = data.get("methodology", "")
    assert "654" in methodology, "methodology must contain 654 §0.14 援引"
    assert "BLOCKED_NO_POOL" in methodology
    assert "EXHAUSTED" in methodology
    assert "655" in methodology
    # 混合态按实报
    assert "混合" in methodology or "PARTIAL" in methodology or "按实报" in methodology or "按省实报" in methodology


def test_docs_79_sections_1_to_6_present() -> None:
    """655-A.3 docs/79 §1-§6 齐全 (架构师级审查)"""
    if not DOCS_79.exists():
        return
    body = _read(DOCS_79)
    for sec in ["## 1.", "## 2.", "## 3.", "## 4.", "## 5.", "## 6."]:
        assert sec in body, f"missing {sec} section in docs/79"


def test_docs_79_partial_blocked_e2e_records_present() -> None:
    """655-A.3 docs/79 §2 首试省 BLOCKED 留痕登记表 完整 (4 实现位置 + 8 守门)"""
    if not DOCS_79.exists():
        return
    body = _read(DOCS_79)
    assert "2.1" in body
    assert "2.2" in body
    # 4 实现位置
    assert "实现位置 1" in body
    assert "实现位置 2" in body
    assert "实现位置 3" in body
    assert "实现位置 4" in body
    # 双首试省实测
    assert "ningxia" in body and "xizang" in body
    # 首试省首触发第三例
    assert "首试省首触发第三例" in body or "第三例首见失败形式" in body or "第三例首见" in body


def test_docs_79_retry_of_na_lineage_records() -> None:
    """655-A.3 docs/79 §4 retry_of=N/A lineage 全行 (ningxia ← N/A; xizang ← N/A — 双首试省无前史)"""
    if not DOCS_79.exists():
        return
    body = _read(DOCS_79)
    assert "retry_of" in body
    assert "N/A" in body
    assert "ningxia" in body and "xizang" in body
    assert "无前史" in body


def test_docs_79_west_seven_provinces_narrative() -> None:
    """655-A.3 docs/79 §3.2 西部七省区全覆盖叙事终章表 (SHAANXI/XINJIANG/NEIMENGGU/GANSU/QINGHAI/NINGXIA/XIZANG)"""
    if not DOCS_79.exists():
        return
    body = _read(DOCS_79)
    assert "西部七省区" in body
    # 七省区
    assert "SHAANXI" in body
    assert "XINJIANG" in body
    assert "NEI MENGGU" in body or "NEIMENGGU" in body or "NEI_MENGGU" in body
    assert "GANSU" in body
    assert "QINGHAI" in body
    assert "NINGXIA" in body
    assert "XIZANG" in body


def test_docs_79_failure_form_library_ningxia_405_waf() -> None:
    """655-A.3 docs/79 §5.3 失败形式库登记 (NINGXIA 405 Method Not Allowed + WAF 网防 G01 marker 第三例首见)"""
    if not DOCS_79.exists():
        return
    body = _read(DOCS_79)
    assert "失败形式库" in body
    assert "405 Method Not Allowed" in body or "405" in body
    assert "WAF" in body
    assert "ningxia" in body
    assert "第三例首见" in body or "首见失败形式" in body
    # 引用 653 SSL handshake failure + 654 Connection reset by peer 为前两例
    assert "SSL handshake failure" in body or "653" in body
    assert "Connection reset by peer" in body or "654" in body


def test_655_red_line_no_gate_no_o1_no_pass() -> None:
    """655 沿用红线 1: docs/79 不宣称 Gate / O1 / O2 / O3 / M2 / M4.x / M5.x / M6 PASS"""
    if not DOCS_79.exists():
        return
    body = _read(DOCS_79)
    assert "不宣布" in body or "不宣称" in body
    assert "M4.18" in body
    assert "O1 仍 OPEN" in body


def test_chain_id_uuid_prefix_n_distinct() -> None:
    """655-A.1 chain_id='real_655_m4_18_policy_detail_v12' + UUID n 段 8 表前缀"""
    if not EVIDENCE.exists():
        return
    data = json.loads(EVIDENCE.read_text(encoding="utf-8"))
    assert data["chain_id"] == "real_655_m4_18_policy_detail_v12"
    assert data["uuid_prefix"] == "n"
    prefixes = data["uuid_prefixes"]
    expected = {
        "source_registry": "n0eebc99",
        "source_document": "n0eebc99",
        "policy_document": "n1eebc99",
        "policy_target": "n2eebc99",
        "policy_measure": "n3eebc99",
        "government_commitment": "n4eebc99",
        "commitment_progress": "n5eebc99",
        "project_event": "n6eebc99",
    }
    for table, prefix in expected.items():
        assert prefixes.get(table) == prefix, (
            f"expected {table} UUID prefix={prefix}; got {prefixes.get(table)}"
        )


def test_p4_a0_v31_tailnote_654_audit_consolidated_landed() -> None:
    """655-A.0 P4-A.0 规范 v3.1 tailnote 落地 654 审计 consolidated doc PART 1 (654 审计 P4×2 处置 + 规范 v3.1).

    关键守门点 (per 655-A.0 任务书 §1.655-A.0):
    - "655-A.0 规范 v3.1" 标题存在 (in 654-audit-655-tasking-consolidated-20260902.md)
    - "status 行零 SHA 绝对化" 终极条款存在 (v3.1 升级 v3: 654 P4-1 字面违反杜绝)
    - "七字段原子" 落地 (v3.1 升级 v3: header line 3 rev / §META 五字段 / §CHAIN_TAIL 当前行 同 commit 同步)
    - amend-first 沿用
    """
    consolidated_path = (
        REPO_ROOT
        / "reviews"
        / "stage0-gate0-rework-2026-08-23"
        / "654-audit-655-tasking-consolidated-20260902.md"
    )
    if consolidated_path.exists():
        body = _read(consolidated_path)
        assert "655-A.0 规范 v3.1" in body or "规范 v3.1" in body, (
            "654-audit-655-tasking consolidated must contain 655-A.0 规范 v3.1"
        )
        assert "status 行零 SHA" in body or "零 SHA 绝对化" in body, (
            "consolidated must contain 'status 行零 SHA 绝对化' 终极条款 (v3.1 升级)"
        )
        assert "七字段原子" in body, "consolidated must contain '七字段原子' (v3.1 落地)"
        assert "amend-first" in body, "consolidated must contain amend-first 沿用"


def test_red_line_14_pool_exhaustion_fetch_script() -> None:
    """655 §0.14 fetch 脚本 SUBSTITUTE_POOL=[] + SUBSTITUTE_POOL_STATUS='EXHAUSTED' (沿用 654)"""
    if not FETCH_SCRIPT.exists():
        return
    body = _read(FETCH_SCRIPT)
    assert "SUBSTITUTE_POOL:" in body
    assert "SUBSTITUTE_POOL_STATUS" in body
    assert "EXHAUSTED" in body
    assert "SUBSTITUTE_POOL: list[tuple[str, list[tuple[str, str]], str]] = []" in body


def test_retry_of_na_lineage_annotation() -> None:
    """655 §1.655-A.1 retry_of=N/A lineage 全行: ningxia ← N/A; xizang ← N/A (双首试省无前史)"""
    if not EVIDENCE.exists():
        return
    data = json.loads(EVIDENCE.read_text(encoding="utf-8"))
    # summary.retry_of_annotation
    annotation = data["summary"].get("retry_of_annotation", {})
    assert "ningxia" in annotation
    assert "xizang" in annotation
    assert "N/A" in annotation["ningxia"]
    assert "N/A" in annotation["xizang"]
    # cells 中 retry_of 字段
    for cell in data["cells"]:
        assert "retry_of" in cell
        assert "N/A" in cell["retry_of"], (
            f"cell retry_of must contain 'N/A'; got {cell['retry_of']}"
        )


def test_docs_78_existing_body_zero_modification_red_line_4() -> None:
    """655 §0.4 红线 4 沿用 654: docs/78 既有正文零改动 (除 P4 typo 行内 append 尾注外).

    655 docs/79 是新文档, 不修改 docs/78 既有 §1-§6 章节. 本测试检查 docs/78 仍保留
    654 既有内容 (西北五省区 + 首试省双 BLOCKED_NO_POOL 等内容仅在 docs/78 出现).
    """
    if not DOCS_78.exists():
        return
    body_78 = _read(DOCS_78)
    # docs/78 是 654 docs, 仍标 654 而非 655
    assert "刀号: 654" in body_78 or "**刀号**: 654" in body_78
    assert "real_654_m4_17_policy_detail_v11" in body_78
    # docs/78 不应包含 655 西部七省区叙事终章表内容
    # (docs/79 才是 655 西部七省区叙事的归属文档)
    assert "西部七省区" not in body_78, (
        "docs/78 should not contain 西部七省区 (这是 655 docs/79 专属内容)"
    )


def test_654_audit_p4x2_handling_v31_spec_landed() -> None:
    """655-A.0 落地: 654 审计 P4×2 (§META 回填不全 + status 第四型 SHA pin 陈旧) 处置 + 规范 v3.1.

    关键守门: 655-A.0 规范 v3.1 = status 行零 SHA 绝对化 + 七字段原子 (header line 3 rev / §META 五字段 / §CHAIN_TAIL 当前行 同 commit 同步) + 沿用 amend-first.
    """
    consolidated_path = (
        REPO_ROOT
        / "reviews"
        / "stage0-gate0-rework-2026-08-23"
        / "654-audit-655-tasking-consolidated-20260902.md"
    )
    if consolidated_path.exists():
        body = _read(consolidated_path)
        # 654 审计 2×P4 处置
        assert "P4-1" in body and "P4-2" in body, (
            "consolidated must contain 654 audit P4-1 + P4-2 处置"
        )
        # rev95 修正
        assert "rev95" in body, "consolidated must contain rev95 修正"
        # 655-A.0 规范 v3.1 终极条款
        assert "status 行零 SHA" in body or "零 SHA 绝对化" in body, (
            "consolidated must contain 655-A.0 规范 v3.1 终极条款 (status 行零 SHA 绝对化)"
        )
        assert "七字段原子" in body, (
            "consolidated must contain 655-A.0 规范 v3.1 七字段原子"
        )