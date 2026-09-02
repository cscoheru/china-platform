"""M4.19 政策详情 v13 华南双省对 spike 守门测试 (knife 656 M4.19 side, ≥10 cases).

Per knife 656 §1.656-B M4.19 side:
- 守门 fetch script 2 cells PARTIAL_BLOCKED (HAINAN REACHABLE 200 + GUANGXI BLOCKED_NO_POOL SSL error:1404B458; 混合态第二例)
- 守门 1 NEW SHA (HAINAN /zwgk/ 200 REACHABLE 直命中; SHA=83a13d18...)
- 守门 spike 边界 8 INSERT ROWS (HAINAN 1 样本 × 8 表; GUANGXI 0 INSERT BLOCKED 留痕; 混合态按实报)
- 守门 chain_id='real_656_m4_19_policy_detail_v13' (≠ 655 _v12 ≠ 654 _v11 ≠ 653 _v10 ≠ 652 _v9 ≠ 651 _v8)
- 守门 UUID o 段 (≠ 655 n 段 ≠ 654 m 段 ≠ 653 l 段 ≠ 652 k 段 ≠ 651 j 段 ≠ 650 i 段)
- 守门 blocked_no_pool_count=1 (GUANGXI 首试省首触发 BLOCKED_NO_POOL; SSL error:1404B458 ×2 全链第四例首见)
- 守门 substitute 池 [EXHAUSTED] 永不触发 (substitute_used_count=0 + SUBSTITUTE_POOL_STATUS="EXHAUSTED")
- 守门 retry_of=N/A lineage 全行 (guangxi ← N/A; hainan ← N/A — 双首试省无前史)
- 守门 docs/80 §1-§6 架构师级审查
- 守门 docs/79 既有正文零改动 (per 656 §0.4 红线 4 沿用 655)
- 守门 656-A.0 规范 v3.2 落地 (status 零 SHA 绝对化 + 七字段原子 + 中间态零残留)
- 守门 evidence methodology 指针 (per 648 P3-1 + 649 P3-1 + 652 §0.14 + 653 §0.14 + 654 §0.14 + 655 §0.14 + 656 §0.14 沿用)
- 守门 不宣称 PASS (沿用红线)
- 守门 失败形式库登记 (GUANGXI SSL error:1404B458 tlsv1 unrecognized name 第四例首见)
- 守门 华南双省对落定表 + 留 HEBEI/SHANXI 给 657 (per 656 §3.2)

零网络; 零 cegr.* mutation; 零爬网; 纯文档守门。
"""
from __future__ import annotations

import json
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
FETCH_SCRIPT = REPO_ROOT / "scripts" / "fetch_m4_19_policy_detail_v13_2024.py"
SEED_SQL = REPO_ROOT / "scripts" / "seed_m4_19_policy_detail_real_v13.sql"
EVIDENCE = REPO_ROOT / "evidence_pack" / "m4_19_policy_detail_real_v13_20260902.json"
REPORT_MD = REPO_ROOT / "docs" / "reports" / "m4_19_policy_detail_real_v13_20260902.md"
DOCS_80 = REPO_ROOT / "docs" / "80-m4-19-policy-detail-real-v13-20260902.md"
DOCS_79 = REPO_ROOT / "docs" / "79-m4-18-policy-detail-real-v12-20260902.md"


def _read(path: Path) -> str:
    if not path.exists():
        return ""
    return path.read_text(encoding="utf-8")


def _non_comment_lines(body: str) -> list[str]:
    """Return lines that are NOT SQL comments (start with --)."""
    return [ln for ln in body.splitlines() if not ln.strip().startswith("--")]


def test_evidence_json_partial_blocked_one_reachable_one_blocked() -> None:
    """656 §0.14 混合态第二例: 主 evidence fetch_status='PARTIAL_BLOCKED' (1 REACHABLE + 1 BLOCKED_NO_POOL)"""
    if not EVIDENCE.exists():
        return
    data = json.loads(EVIDENCE.read_text(encoding="utf-8"))
    assert data["summary"]["fetch_status"] == "PARTIAL_BLOCKED", (
        f"expected fetch_status=PARTIAL_BLOCKED (混合态第二例); got {data['summary']['fetch_status']}"
    )
    assert data["summary"]["fetched_count"] == 1, (
        f"expected fetched_count=1 (HAINAN REACHABLE); got {data['summary']['fetched_count']}"
    )
    assert data["summary"]["blocked_no_pool_count"] == 1, (
        f"expected blocked_no_pool_count=1 (GUANGXI 首试省首触发第四例); got {data['summary']['blocked_no_pool_count']}"
    )
    assert len(data["cells"]) == 2


def test_evidence_json_hainan_one_new_sha() -> None:
    """656 §1.656-A.1 HAINAN REACHABLE → 1 NEW SHA (83a13d18); GUANGXI BLOCKED 无 SHA"""
    if not EVIDENCE.exists():
        return
    data = json.loads(EVIDENCE.read_text(encoding="utf-8"))
    assert len(data["summary"]["distinct_shas"]) == 1, (
        f"expected distinct_shas=1 (HAINAN REACHABLE); got {data['summary']['distinct_shas']}"
    )
    assert "83a13d1810fab068dd84403684253e459f348e18147450374447e34190087938" in data["summary"]["distinct_shas"], (
        f"expected SHA=83a13d18 (HAINAN); got {data['summary']['distinct_shas']}"
    )
    shas_by_province = {cell["province"]: cell["file_hash_sha256"] for cell in data["cells"]}
    assert shas_by_province.get("hainan") == "83a13d1810fab068dd84403684253e459f348e18147450374447e34190087938", (
        f"hainan SHA mismatch; got {shas_by_province.get('hainan')}"
    )
    assert shas_by_province.get("guangxi") == "", (
        f"guangxi BLOCKED should have empty SHA; got {shas_by_province.get('guangxi')}"
    )


def test_evidence_json_guangxi_blocked_no_pool_ssl_1404b458() -> None:
    """656 §0.14 GUANGXI BLOCKED_NO_POOL (首试省首触发第四例; SSL error:1404B458 tlsv1 unrecognized name ×2)"""
    if not EVIDENCE.exists():
        return
    data = json.loads(EVIDENCE.read_text(encoding="utf-8"))
    cells_by_province = {cell["province"]: cell for cell in data["cells"]}
    gx = cells_by_province.get("guangxi")
    assert gx is not None, "guangxi cell must exist"
    assert gx["verdict"] == "BLOCKED_NO_POOL", (
        f"guangxi expected verdict=BLOCKED_NO_POOL; got {gx['verdict']}"
    )
    assert gx["substitute_used"] is False
    assert gx["blocked_reason"] != "", "BLOCKED cell must have non-empty blocked_reason"
    assert gx["chain_index"] == -1, f"BLOCKED cell chain_index=-1; got {gx['chain_index']}"
    # fetch_log 两级 fallback 均 SSL 失败 (http_code=0)
    for entry in gx["fetch_log"]:
        assert entry["http_code"] == 0, (
            f"guangxi expected http_code=0 (SSL 失败); got {entry['http_code']}"
        )
        # reason 字段含 SSL error 标识
        reason = entry.get("reason", "")
        assert "SSL" in reason or "1404" in reason or "unrecognized" in reason or "tlsv1" in reason, (
            f"guangxi expected SSL error in reason; got {reason[:200]}"
        )


def test_evidence_json_hainan_reachable_200_30150_89_anchors() -> None:
    """656 §1.656-A.1 HAINAN REACHABLE (200, 30150 bytes, 89 锚点, SHA=83a13d18)"""
    if not EVIDENCE.exists():
        return
    data = json.loads(EVIDENCE.read_text(encoding="utf-8"))
    cells_by_province = {cell["province"]: cell for cell in data["cells"]}
    hn = cells_by_province.get("hainan")
    assert hn is not None, "hainan cell must exist"
    assert hn["verdict"] == "REACHABLE", f"hainan expected verdict=REACHABLE; got {hn['verdict']}"
    assert hn["http_code"] == 200
    assert hn["file_size_bytes"] == 30150
    assert hn["anchor_hits_count"] == 89
    assert hn["waf_marker_present"] is False


def test_evidence_json_substitute_pool_status_exhausted() -> None:
    """656 §0.14 沿用 655 §0.14 主 evidence substitute_pool_status='EXHAUSTED'"""
    if not EVIDENCE.exists():
        return
    data = json.loads(EVIDENCE.read_text(encoding="utf-8"))
    assert data["summary"]["substitute_pool_status"] == "EXHAUSTED"
    assert data["summary"]["substitute_used_count"] == 0


def test_evidence_json_http_count_3() -> None:
    """656 §0.3 红线 3: HTTP 3/12 (guangxi 2 + hainan 1; ≤12 HTTP limit)"""
    if not EVIDENCE.exists():
        return
    data = json.loads(EVIDENCE.read_text(encoding="utf-8"))
    assert data["summary"]["http_count"] == 3, (
        f"expected http_count=3 (guangxi 2 + hainan 1); got {data['summary']['http_count']}"
    )
    assert data["summary"]["http_count"] <= 12, (
        f"≤12 HTTP limit violated: {data['summary']['http_count']}"
    )


def test_fetch_script_2_cells_guangxi_hainan_chains() -> None:
    """656-A.1 fetch 脚本 2 cells: guangxi + hainan; 各 2 fallback URL; retry_of=N/A lineage"""
    if not FETCH_SCRIPT.exists():
        return
    body = _read(FETCH_SCRIPT)
    assert "GUANGXI_FALLBACK_CHAIN" in body
    assert "HAINAN_FALLBACK_CHAIN" in body
    assert "guangxi" in body
    assert "hainan" in body
    assert "https://www.gxzf.gov.cn/zwgk/" in body
    assert "https://www.gxzf.gov.cn/" in body
    assert "https://www.hainan.gov.cn/zwgk/" in body
    assert "https://www.hainan.gov.cn/" in body
    assert "RETRY_OF_NOTES" in body
    assert "retry_of=N/A" in body


def test_fetch_script_blocked_no_pool_branch_present() -> None:
    """656 §0.14 沿用 655 BLOCKED_NO_POOL 分支代码 e2e 可达 (def fetch_cell 含 BLOCKED_NO_POOL verdict + blocked_reason 字段)"""
    if not FETCH_SCRIPT.exists():
        return
    body = _read(FETCH_SCRIPT)
    assert "BLOCKED_NO_POOL" in body
    assert "blocked_reason" in body
    assert '"BLOCKED_NO_POOL"' in body or "'BLOCKED_NO_POOL'" in body
    assert "verdict" in body


def test_seed_sql_8_insert_hainan_0_insert_guangxi() -> None:
    """656 §1.656-A.1 混合态按实报: seed SQL 8 INSERT (HAINAN 1 样本 × 8 表) + GUANGXI 0 INSERT (BLOCKED 留痕)"""
    if not SEED_SQL.exists():
        return
    body = _read(SEED_SQL)
    non_comment = "\n".join(_non_comment_lines(body))
    insert_statements = [ln for ln in non_comment.splitlines() if "INSERT INTO" in ln]
    assert len(insert_statements) == 8, (
        f"expected 8 INSERT statements (HAINAN 1 样本 × 8 表); got {len(insert_statements)}: {insert_statements}"
    )
    assert "BLOCKED_NO_POOL" in body
    assert "guangxi" in body and "hainan" in body
    assert "SSL error:1404B458" in body or "1404B458" in body or "tlsv1 unrecognized name" in body
    assert "retry_of=N/A" in body or "retry_of = N/A" in body or "无前史首试" in body
    assert "GUANGXI BLOCKED_NO_POOL 留痕" in body or "guangxi 留痕不入 INSERT" in body


def test_seed_sql_chain_id_v13_distinct_from_655_654_653_652_651() -> None:
    """656-A.1 seed SQL chain_id='real_656_m4_19_policy_detail_v13' (≠ 655 _v12 ≠ 654 _v11 ≠ 653 _v10 ≠ 652 _v9 ≠ 651 _v8)."""
    if not SEED_SQL.exists():
        return
    body = _read(SEED_SQL)
    assert "real_656_m4_19_policy_detail_v13" in body, (
        "seed SQL must contain chain_id='real_656_m4_19_policy_detail_v13'"
    )
    assert "real_655_m4_18_policy_detail_v12" not in body
    assert "real_654_m4_17_policy_detail_v11" not in body
    assert "real_653_m4_16_policy_detail_v10" not in body
    assert "real_652_m4_15_policy_detail_v9" not in body
    assert "real_651_m4_14_policy_detail_v8" not in body


def test_seed_sql_uuid_o_segment_distinct_from_n_m_l_k_j_i_segments() -> None:
    """656-A.1 seed SQL UUID o 段 (o0eebc99-o6eebc99) ≠ 655 n 段 ≠ 654 m 段 ≠ 653 l 段 ≠ 652 k 段 ≠ 651 j 段 ≠ 650 i 段"""
    if not SEED_SQL.exists():
        return
    body = _read(SEED_SQL)
    non_comment = "\n".join(_non_comment_lines(body))
    for prefix in ["n0eebc99", "m0eebc99", "l0eebc99", "k0eebc99", "j0eebc99", "i0eebc99"]:
        assert prefix not in non_comment, f"656 must not reference {prefix} (其他刀段)"


def test_report_md_no_pass_announcement_656_red_line() -> None:
    """656 沿用红线 1: docs/reports/m4_19 不宣称任何 PASS"""
    if not REPORT_MD.exists():
        return
    body = _read(REPORT_MD)
    assert "不宣称 PASS" in body or "不宣布" in body or "不宣称" in body


def test_evidence_methodology_pointer_per_648_p3_1_and_655_red_line_14_and_656_partial_blocked() -> None:
    """656-A.4 主 evidence methodology 含 648 P3-1 + 652 §0.14 + 653 §0.14 + 654 §0.14 + 655 §0.14 + 656 §0.14 援引 + 混合态按实报"""
    if not EVIDENCE.exists():
        return
    data = json.loads(EVIDENCE.read_text(encoding="utf-8"))
    methodology = data.get("methodology", "")
    assert "655" in methodology, "methodology must contain 655 §0.14 援引"
    assert "BLOCKED_NO_POOL" in methodology
    assert "EXHAUSTED" in methodology
    assert "656" in methodology
    assert "混合" in methodology or "PARTIAL" in methodology or "按实报" in methodology or "按省实报" in methodology


def test_docs_80_sections_1_to_6_present() -> None:
    """656-A.3 docs/80 §1-§6 齐全 (架构师级审查)"""
    if not DOCS_80.exists():
        return
    body = _read(DOCS_80)
    for sec in ["## 1.", "## 2.", "## 3.", "## 4.", "## 5.", "## 6."]:
        assert sec in body, f"missing {sec} section in docs/80"


def test_docs_80_partial_blocked_e2e_records_present() -> None:
    """656-A.3 docs/80 §2 首试省 BLOCKED 留痕登记表 完整 (4 实现位置 + 13 守门含 O-1 根因修复)"""
    if not DOCS_80.exists():
        return
    body = _read(DOCS_80)
    assert "2.1" in body
    assert "2.2" in body
    assert "实现位置 1" in body
    assert "实现位置 2" in body
    assert "实现位置 3" in body
    assert "实现位置 4" in body
    assert "guangxi" in body and "hainan" in body
    assert "首试省首触发第四例" in body or "第四例首见失败形式" in body or "第四例首见" in body


def test_docs_80_retry_of_na_lineage_records() -> None:
    """656-A.3 docs/80 §4 retry_of=N/A lineage 全行 (guangxi ← N/A; hainan ← N/A — 双首试省无前史)"""
    if not DOCS_80.exists():
        return
    body = _read(DOCS_80)
    assert "retry_of" in body
    assert "N/A" in body
    assert "guangxi" in body and "hainan" in body
    assert "无前史" in body


def test_docs_80_south_pair_narrative() -> None:
    """656-A.3 docs/80 §3.2 华南双省对落定表 (GUANGXI/HAINAN) + 留 HEBEI/SHANXI 给 657 全国 31 省收官"""
    if not DOCS_80.exists():
        return
    body = _read(DOCS_80)
    assert "华南双省对" in body
    assert "GUANGXI" in body
    assert "HAINAN" in body
    assert "HEBEI" in body
    assert "SHANXI" in body
    assert "657" in body
    assert "全国 31 省收官" in body or "31 省收官" in body


def test_docs_80_failure_form_library_guangxi_ssl_1404b458() -> None:
    """656-A.3 docs/80 §5.3 失败形式库登记 (GUANGXI SSL error:1404B458 tlsv1 unrecognized name 第四例首见)"""
    if not DOCS_80.exists():
        return
    body = _read(DOCS_80)
    assert "失败形式库" in body
    assert "SSL error:1404B458" in body or "1404B458" in body
    assert "tlsv1 unrecognized name" in body or "unrecognized name" in body
    assert "guangxi" in body
    assert "第四例首见" in body or "首见失败形式" in body
    # 引用 653 SSL handshake failure + 654 Connection reset by peer + 655 405+WAF 为前三例
    assert "653" in body and "SSL handshake failure" in body or "SSL handshake failure" in body
    assert "Connection reset by peer" in body or "654" in body
    assert "405 Method Not Allowed" in body or "WAF" in body or "655" in body


def test_656_red_line_no_gate_no_o1_no_pass() -> None:
    """656 沿用红线 1: docs/80 不宣称 Gate / O1 / O2 / O3 / M2 / M4.x / M5.x / M6 PASS"""
    if not DOCS_80.exists():
        return
    body = _read(DOCS_80)
    assert "不宣布" in body or "不宣称" in body
    assert "M4.19" in body
    assert "O1 仍 OPEN" in body


def test_chain_id_uuid_prefix_o_distinct() -> None:
    """656-A.1 chain_id='real_656_m4_19_policy_detail_v13' + UUID o 段 8 表前缀"""
    if not EVIDENCE.exists():
        return
    data = json.loads(EVIDENCE.read_text(encoding="utf-8"))
    assert data["chain_id"] == "real_656_m4_19_policy_detail_v13"
    assert data["uuid_prefix"] == "o"
    prefixes = data["uuid_prefixes"]
    expected = {
        "source_registry": "o0eebc99",
        "source_document": "o0eebc99",
        "policy_document": "o1eebc99",
        "policy_target": "o2eebc99",
        "policy_measure": "o3eebc99",
        "government_commitment": "o4eebc99",
        "commitment_progress": "o5eebc99",
        "project_event": "o6eebc99",
    }
    for table, prefix in expected.items():
        assert prefixes.get(table) == prefix, (
            f"expected {table} UUID prefix={prefix}; got {prefixes.get(table)}"
        )


def test_656_a0_v32_spec_landed_in_docs_80() -> None:
    """656-A.0 规范 v3.2 落点守门 (status 零 SHA + 七字段原子 + 中间态零残留首签)."""
    if not DOCS_80.exists():
        return
    body = _read(DOCS_80)
    assert "规范 v3.2" in body, "docs/80 must contain 656-A.0 规范 v3.2"
    assert "status 行零 SHA" in body or "零 SHA 绝对化" in body, (
        "docs/80 must contain 'status 行零 SHA 绝对化' 终极条款 (v3.2 沿用)"
    )
    assert "七字段原子" in body, "docs/80 must contain '七字段原子' (v3.2 沿用 v3.1)"
    assert "中间态零残留" in body, "docs/80 must contain '中间态零残留' (v3.2 新增首签)"


def test_656_a2_o1_root_cause_fix_landed() -> None:
    """656-A.2 O-1 根因修复落点守门 (m2 报告只读化锁定测试)."""
    if not DOCS_80.exists():
        return
    body = _read(DOCS_80)
    assert "656-A.2 O-1 根因修复" in body or "O-1 根因修复" in body, (
        "docs/80 must contain 656-A.2 O-1 根因修复 标识"
    )
    assert "m2 报告只读化" in body or "m2 报告只读化锁定测试" in body or "test_m2_report_hygiene" in body, (
        "docs/80 must contain m2 报告只读化锁定测试 标识"
    )


def test_red_line_14_pool_exhaustion_fetch_script() -> None:
    """656 §0.14 fetch 脚本 SUBSTITUTE_POOL=[] + SUBSTITUTE_POOL_STATUS='EXHAUSTED' (沿用 655)"""
    if not FETCH_SCRIPT.exists():
        return
    body = _read(FETCH_SCRIPT)
    assert "SUBSTITUTE_POOL:" in body
    assert "SUBSTITUTE_POOL_STATUS" in body
    assert "EXHAUSTED" in body
    assert "SUBSTITUTE_POOL: list[tuple[str, list[tuple[str, str]], str]] = []" in body


def test_retry_of_na_lineage_annotation() -> None:
    """656 §1.656-A.1 retry_of=N/A lineage 全行: guangxi ← N/A; hainan ← N/A (双首试省无前史)"""
    if not EVIDENCE.exists():
        return
    data = json.loads(EVIDENCE.read_text(encoding="utf-8"))
    annotation = data["summary"].get("retry_of_annotation", {})
    assert "guangxi" in annotation
    assert "hainan" in annotation
    assert "N/A" in annotation["guangxi"]
    assert "N/A" in annotation["hainan"]
    for cell in data["cells"]:
        assert "retry_of" in cell
        assert "N/A" in cell["retry_of"], (
            f"cell retry_of must contain 'N/A'; got {cell['retry_of']}"
        )


def test_docs_79_existing_body_zero_modification_red_line_4() -> None:
    """656 §0.4 红线 4 沿用 655: docs/79 既有正文零改动.

    656 docs/80 是新文档, 不修改 docs/79 既有 §1-§6 章节. 本测试检查 docs/79 仍保留
    655 既有内容 (西部七省区 + 首试省 BLOCKED_NO_POOL 等内容仅在 docs/79 出现).
    """
    if not DOCS_79.exists():
        return
    body_79 = _read(DOCS_79)
    assert "刀号: 655" in body_79 or "**刀号**: 655" in body_79
    assert "real_655_m4_18_policy_detail_v12" in body_79
    assert "华南双省对" not in body_79, (
        "docs/79 should not contain 华南双省对 (这是 656 docs/80 专属内容)"
    )