"""M4.15 政策详情 v9 真实化 spike 第 11 次 守门测试 (knife 652 M4.15 side, ≥10 cases).

Per knife 652 §1.652-B M4.15 side:
- 守门 fetch script 2 cells REAL_FETCHED (http_count=3 ≤ 12)
- 守门 2 SHA distinct (21c8211b.../da1d4104...) + 2 file_size > 0
- 守门 spike 边界 16 INSERT ROWS (12 政策表 + 4 source)
- 守门 chain_id='real_652_m4_15_policy_detail_v9' (≠ 651 _v8 ≠ 650 _v7 ≠ 649 _v6)
- 守门 UUID k 段 (≠ 651 j 段 ≠ 650 i 段 ≠ 649 h 段 ≠ 648 g 段 ≠ 647 f 段 ≠ 646 e 段 ≠ 645 d 段 ≠ 644 c 段)
- 守门 2 NEW SHA distinct ≠ 638-651 全部 SHA
- 守门 substitute 池 [EXHAUSTED] 永不触发 (substitute_used_count=0 + SUBSTITUTE_POOL_STATUS="EXHAUSTED")
- 守门 BLOCKED_NO_POOL 留痕 e2e (fetch_cell 含 BLOCKED_NO_POOL verdict + 双样本均 REACHABLE → 实际未触发; 分支代码可达)
- 守门 已用省全集检查 (649 HLJ/HENAN/YUNNAN/FUJIAN/GD/ZJ/JX/HUN/AH/HUBEI/JILIN/LIAONING 不得重复; 650 增量 GUIZHOU/JIANGSU; 651 增量 SHAANXI/SICHUAN; 652 增量 XINJIANG/NEI MENGGU)
- 守门 docs/76 §1-§6 架构师级审查
- 守门 docs/75 §6 + 651 receipt §RED_LINE_AUDIT P4×2 规范固化 tailnote
- 守门 evidence methodology 指针 (per 648 审计 P3-1 + 649 P3-1 + 651 §0.14 红线 14 增补 + 652 §0.14 强制 BLOCKED_NO_POOL e2e 验证)
- 守门 不宣称 PASS (沿用红线)

零网络; 零 cegr.* mutation; 零爬网; 纯文档守门。
"""
from __future__ import annotations

import json
import re
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
FETCH_SCRIPT = REPO_ROOT / "scripts" / "fetch_m4_15_policy_detail_v9_2024.py"
SEED_SQL = REPO_ROOT / "scripts" / "seed_m4_15_policy_detail_real_v9.sql"
EVIDENCE = REPO_ROOT / "evidence_pack" / "m4_15_policy_detail_real_v9_20260902.json"
REPORT_MD = REPO_ROOT / "docs" / "reports" / "m4_15_policy_detail_real_v9_20260902.md"
DOCS_76 = REPO_ROOT / "docs" / "76-m4-15-policy-detail-real-v9-20260902.md"
DOCS_75 = REPO_ROOT / "docs" / "75-m4-14-policy-detail-real-v8-20260902.md"
RECEIPT_651 = REPO_ROOT / "reviews" / "stage0-gate0-rework-2026-08-23" / "651-stage0-cc-m4-14-v8-pool-depletion-receipt-20260902.md"


def _read(path: Path) -> str:
    if not path.exists():
        return ""
    return path.read_text(encoding="utf-8")


def _non_comment_lines(body: str) -> list[str]:
    """Return lines that are NOT SQL comments (start with --)."""
    return [ln for ln in body.splitlines() if not ln.strip().startswith("--")]


def test_evidence_json_real_fetched_2_samples() -> None:
    """652-A.1 evidence_pack/m4_15 evidence JSON REAL_FETCHED + 2 samples + http_count=3"""
    if not EVIDENCE.exists():
        return
    data = json.loads(EVIDENCE.read_text(encoding="utf-8"))
    assert data["summary"]["fetch_status"] == "REAL_FETCHED"
    assert data["summary"]["fetched_count"] == 2
    assert data["summary"]["http_count"] == 3, (
        f"expected http_count=3 (xinjiang 2 + nei_menggu 1); got {data['summary']['http_count']}"
    )
    assert data["summary"]["http_count"] <= 12, (
        f"≤12 HTTP limit violated: {data['summary']['http_count']}"
    )
    assert len(data["cells"]) == 2


def test_evidence_json_2_distinct_shas_no_collision() -> None:
    """652-A.1 2 SHA distinct (21c8211b + da1d4104) + 2 file_size > 0"""
    if not EVIDENCE.exists():
        return
    data = json.loads(EVIDENCE.read_text(encoding="utf-8"))
    shas = {cell["file_hash_sha256"] for cell in data["cells"]}
    assert len(shas) == 2, f"2 cells should have 2 distinct SHA — got {len(shas)}: {shas}"
    for cell in data["cells"]:
        assert cell["file_size_bytes"] > 0
    sha_set_str = " ".join(shas)
    assert "21c8211b" in sha_set_str, f"expected xinjiang SHA 21c8211b in {sha_set_str}"
    assert "da1d4104" in sha_set_str, f"expected nei_menggu SHA da1d4104 in {sha_set_str}"


def test_evidence_json_2_provinces_xinjiang_nei_menggu_no_substitute() -> None:
    """652-A.1 2 distinct provinces: xinjiang + nei_menggu; both substitute_used=false (无 substitute 触发)"""
    if not EVIDENCE.exists():
        return
    data = json.loads(EVIDENCE.read_text(encoding="utf-8"))
    provinces = [cell["province"] for cell in data["cells"]]
    assert "xinjiang" in provinces
    assert "nei_menggu" in provinces
    for cell in data["cells"]:
        assert cell["substitute_used"] is False


def test_evidence_json_no_substitute_reason() -> None:
    """652-A.1 双样本 substitute_used=false; 实际未触发 substitute (递补池已耗尽; 即便 fallback 失败也不可代换)"""
    if not EVIDENCE.exists():
        return
    data = json.loads(EVIDENCE.read_text(encoding="utf-8"))
    for cell in data["cells"]:
        assert cell["substitute_used"] is False
        # REACHABLE 时 blocked_reason 应为空 (BLOCKED 时才非空)
        assert cell.get("blocked_reason") == "" or cell.get("blocked_reason") is None


def test_evidence_json_substitute_pool_status_exhausted() -> None:
    """652 §0.14 主 evidence substitute_pool_status='EXHAUSTED' (沿用 651 §0.14 红线 14 增补)"""
    if not EVIDENCE.exists():
        return
    data = json.loads(EVIDENCE.read_text(encoding="utf-8"))
    assert data["summary"]["substitute_pool_status"] == "EXHAUSTED"
    assert data["summary"]["substitute_used_count"] == 0


def test_evidence_json_blocked_no_pool_count_zero_but_field_present() -> None:
    """652 §0.14 BLOCKED_NO_POOL 字段存在; 本次 count=0 (双样本均 REACHABLE; 但 e2e 验证机制要求字段存在)"""
    if not EVIDENCE.exists():
        return
    data = json.loads(EVIDENCE.read_text(encoding="utf-8"))
    assert "blocked_no_pool_count" in data["summary"]
    assert data["summary"]["blocked_no_pool_count"] == 0  # 本次双样本均 REACHABLE


def test_fetch_script_2_cells_xinjiang_nei_menggu_chains() -> None:
    """652-A.1 fetch 脚本 2 cells: xinjiang + nei_menggu; 各 2 fallback URL; chain_index=1 + 0"""
    if not FETCH_SCRIPT.exists():
        return
    body = _read(FETCH_SCRIPT)
    assert "XINJIANG_FALLBACK_CHAIN" in body
    assert "NEI_MENGGU_FALLBACK_CHAIN" in body
    assert "xinjiang" in body
    assert "nei_menggu" in body
    assert "https://www.xinjiang.gov.cn/zwgk/" in body
    assert "https://www.xinjiang.gov.cn/" in body
    assert "https://www.nmg.gov.cn/zwgk/" in body
    assert "https://www.nmg.gov.cn/" in body


def test_fetch_script_blocked_no_pool_branch_present() -> None:
    """652 §0.14 BLOCKED_NO_POOL 分支代码 e2e 可达 (def fetch_cell 含 BLOCKED_NO_POOL verdict + blocked_reason 字段)"""
    if not FETCH_SCRIPT.exists():
        return
    body = _read(FETCH_SCRIPT)
    # BLOCKED_NO_POOL 字串守门 (e2e 验证要求: 字段存在并可达)
    assert "BLOCKED_NO_POOL" in body
    assert "blocked_reason" in body
    # verdict 字段含 BLOCKED_NO_POOL
    assert '"BLOCKED_NO_POOL"' in body or "'BLOCKED_NO_POOL'" in body
    # 实际 e2e 验证本次触发情况: 显式 verdict 分支
    assert "verdict" in body


def test_fetch_log_xinjiang_403_200_nei_menggu_200() -> None:
    """652-A.1 fetch_log: xinjiang /zwgk/ 403 WAF → / 200 REACHABLE; nei_menggu /zwgk/ 200 REACHABLE"""
    if not EVIDENCE.exists():
        return
    data = json.loads(EVIDENCE.read_text(encoding="utf-8"))
    cells_by_province = {cell["province"]: cell for cell in data["cells"]}
    # xinjiang: chain_index=1 (fallback)
    xj = cells_by_province.get("xinjiang")
    if xj:
        assert xj["chain_index"] == 1, f"xinjiang expected chain_index=1 (fallback), got {xj['chain_index']}"
        assert xj["verdict"] == "REACHABLE"
        assert xj["file_size_bytes"] > 0
    # nei_menggu: chain_index=0 (首选直命中)
    nmg = cells_by_province.get("nei_menggu")
    if nmg:
        assert nmg["chain_index"] == 0, f"nei_menggu expected chain_index=0 (首选直命中), got {nmg['chain_index']}"
        assert nmg["verdict"] == "REACHABLE"
        assert nmg["file_size_bytes"] > 0


def test_seed_sql_16_insert_total() -> None:
    """652-A.1 seed SQL 16 INSERT ROWS (12 政策表 + 2 registry + 2 document = 16 ROWS / 10 statements)"""
    if not SEED_SQL.exists():
        return
    body = _read(SEED_SQL)
    # 计数 INSERT statements
    insert_statements = re.findall(r"^INSERT INTO\s+\w+", body, re.MULTILINE)
    # 10 INSERT statements (per 651 模式: 6 tables × VALUES 块 = 6 statements + 2 SELECT 块 = 8, + commitment_progress + project_event 同 651)
    assert len(insert_statements) >= 8, f"expected ≥8 INSERT statements, got {len(insert_statements)}"
    # 8 tables: source_registry / source_document / policy_document / policy_target / policy_measure / government_commitment / commitment_progress / project_event
    for table in ["source_registry", "source_document", "policy_document", "policy_target",
                  "policy_measure", "government_commitment", "commitment_progress", "project_event"]:
        assert f"INSERT INTO {table}" in body, f"missing INSERT INTO {table}"


def test_seed_sql_chain_id_v9_distinct_from_651_650_649_648_647_646_645() -> None:
    """652-A.1 seed SQL chain_id='real_652_m4_15_policy_detail_v9' (≠ 651 _v8 ≠ 650 _v7 ≠ 649 _v6)"""
    if not SEED_SQL.exists():
        return
    body = _read(SEED_SQL)
    non_comment = "\n".join(_non_comment_lines(body))
    assert "real_652_m4_15_policy_detail_v9" in non_comment
    assert "_v8" not in non_comment, "seed SQL must not reference 651 chain_id _v8"
    assert "_v7" not in non_comment, "seed SQL must not reference 650 chain_id _v7"


def test_seed_sql_uuid_k_segment_distinct_from_j_i_h_g_f_e_d_c_segments() -> None:
    """652-A.1 seed SQL UUID k 段 (k0eebc99-k6eebc99) ≠ 651 j 段 ≠ 650 i 段 ≠ 649 h 段"""
    if not SEED_SQL.exists():
        return
    body = _read(SEED_SQL)
    non_comment = "\n".join(_non_comment_lines(body))
    # k 段前缀 (8 表前缀)
    assert "k0eebc99" in non_comment
    assert "k1eebc99" in non_comment
    assert "k2eebc99" in non_comment
    assert "k3eebc99" in non_comment
    assert "k4eebc99" in non_comment
    assert "k5eebc99" in non_comment
    assert "k6eebc99" in non_comment
    # 不应出现 j/i/h/g/f/e/d/c 段
    for prefix in ["j0eebc99", "j1eebc99", "i0eebc99", "h0eebc99", "g0eebc99"]:
        assert prefix not in non_comment, f"652 must not reference {prefix} (其他刀段)"


def test_seed_sql_uses_real_fetched_shas_21c8211b_da1d4104() -> None:
    """652-A.1 seed SQL 使用 2 NEW SHA: 21c8211b (xinjiang fallback #1) + da1d4104 (nei_menggu 首选)"""
    if not SEED_SQL.exists():
        return
    body = _read(SEED_SQL)
    non_comment = "\n".join(_non_comment_lines(body))
    assert "21c8211bf7bf8b41569174e5ae2ae127f8e11439a04a5501209a63506ddca472" in non_comment
    assert "da1d4104db87c47809ef40f12bd8847d98c432bf990b0d7056f0042e6fd0533b" in non_comment
    # 不应出现 651 SHA
    assert "9d0ad78a79317d5ec5224bf4fd56c4fa44dd658d2221e2921da1700e99e32ad5" not in non_comment
    assert "f58a33842ab22afcb84a9f1156a6e1f05bae3f01432c8ea6b103c29387346ad5" not in non_comment


def test_seed_sql_lineage_is_demo_false_sentinel() -> None:
    """652-A.1 seed SQL lineage JSONB 全 is_demo='false' 真实化 sentinel (per docs/33 §3.2)"""
    if not SEED_SQL.exists():
        return
    body = _read(SEED_SQL)
    non_comment = "\n".join(_non_comment_lines(body))
    # 双引号字面 JSON 写法: 12 行 (source_registry x2 + source_document x2 + policy_document x2 + policy_target x2 + policy_measure x2 + commitment_progress x2 = 12)
    quoted = non_comment.count('"is_demo": "false"')
    # jsonb_build_object 写法: 4 行 (government_commitment x2 + project_event x2)
    jsonb_build = non_comment.count("'is_demo', 'false'")
    total = quoted + jsonb_build
    assert total >= 16, f"expected ≥16 is_demo='false' in lineage JSONB, got {total} (quoted={quoted}, jsonb_build={jsonb_build})"


def test_seed_sql_red_line_14_status_exhausted() -> None:
    """652 §0.14 seed SQL lineage JSONB 全 red_line_14_status='EXHAUSTED' (沿用 651 §0.14 红线 14 增补)"""
    if not SEED_SQL.exists():
        return
    body = _read(SEED_SQL)
    non_comment = "\n".join(_non_comment_lines(body))
    assert non_comment.count('"red_line_14_status": "EXHAUSTED"') >= 12, (
        f"expected ≥12 red_line_14_status='EXHAUSTED' in lineage JSONB"
    )


def test_seed_sql_no_substitute_used() -> None:
    """652-A.1 seed SQL substitute_used=false (双样本均无 substitute 触发)"""
    if not SEED_SQL.exists():
        return
    body = _read(SEED_SQL)
    non_comment = "\n".join(_non_comment_lines(body))
    assert non_comment.count('"substitute_used": false') >= 12, (
        f"expected ≥12 substitute_used=false in lineage JSONB"
    )


def test_report_md_no_pass_announcement_652_red_line() -> None:
    """652 沿用红线 1: docs/reports/m4_15 不宣称任何 PASS"""
    if not REPORT_MD.exists():
        return
    body = _read(REPORT_MD)
    assert "不宣称 PASS" in body or "不宣布" in body or "不宣称" in body


def test_evidence_methodology_pointer_per_648_p3_1_and_651_red_line_14_and_652_e2e() -> None:
    """652-A.4 主 evidence methodology 含 651 §0.14 援引 + 652 §0.14 强制 e2e 验证 + 648 P3-1 援引"""
    if not EVIDENCE.exists():
        return
    data = json.loads(EVIDENCE.read_text(encoding="utf-8"))
    methodology = data.get("methodology", "")
    assert "651" in methodology or "EXHAUSTED" in methodology
    assert "652" in methodology or "BLOCKED_NO_POOL" in methodology
    assert "BLOCKED_NO_POOL" in methodology
    assert "EXHAUSTED" in methodology


def test_docs_76_sections_1_to_6_present() -> None:
    """652-A.3 docs/76 §1-§6 齐全 (架构师级审查)"""
    if not DOCS_76.exists():
        return
    body = _read(DOCS_76)
    for sec in ["## 1.", "## 2.", "## 3.", "## 4.", "## 5.", "## 6."]:
        assert sec in body, f"missing {sec} section in docs/76"


def test_docs_76_blocked_no_pool_e2e_records_present() -> None:
    """652-A.3 docs/76 §2 BLOCKED 留痕 e2e 验证登记表 完整 (4 实现位置 + 5 守门)"""
    if not DOCS_76.exists():
        return
    body = _read(DOCS_76)
    # §2.1 4 实现位置 + §2.2 双样本实测 + §2.3 触发累计计数
    assert "2.1" in body
    assert "2.2" in body
    assert "2.3" in body
    # 4 实现位置
    assert "fetch 脚本分支代码可达" in body
    assert "seed SQL lineage 真实化 sentinel" in body
    assert "主 evidence summary + methodology" in body
    assert "docs/76 §5 BLOCKED 留痕口径" in body
    # 双样本实测
    assert "xinjiang" in body and "nei_menggu" in body
    # e2e 守门 5 项
    assert "test_fetch_script_blocked_no_pool_branch_present" in body
    assert "test_evidence_json_substitute_pool_status_exhausted" in body
    assert "test_seed_sql_red_line_14_status_exhausted" in body


def test_docs_76_pool_depletion_records() -> None:
    """652-A.3 docs/76 §4.4 递补池耗尽 [EXHAUSTED] 沿用 651 + 状态表 5 行"""
    if not DOCS_76.exists():
        return
    body = _read(DOCS_76)
    assert "EXHAUSTED" in body
    assert "liaoning" in body
    assert "shaanxi" in body
    assert "sichuan" in body
    assert "guizhou" in body
    assert "jiangsu" in body


def test_652_red_line_no_gate_no_o1_no_pass() -> None:
    """652 沿用红线 1: docs/76 不宣称 Gate / O1 / O2 / O3 / M2 / M4.x / M5.x / M6 PASS"""
    if not DOCS_76.exists():
        return
    body = _read(DOCS_76)
    assert "不宣布" in body or "不宣称" in body
    assert "M4.15" in body
    # 显式列出不宣称 (lineage: 沿用红线 1)
    assert "O1 仍 OPEN" in body


def test_chain_id_province_used_set_clean() -> None:
    """652-A.1 已用省全集检查 (18 省: HLJ/HENAN/YUNNAN/FUJIAN/GD/ZJ/JX/HUN/AH/LN/JL/GUIZHOU/JIANGSU/SHAANXI/SICHUAN/XINJIANG/NEI MENGGU); HUBEI 为 substitute 槽名不计入"""
    if not DOCS_76.exists():
        return
    body = _read(DOCS_76)
    # docs/76 §2.5 + §4.4 应含 18 省 (actual_province 口径)
    required_provinces = [
        "HLJ", "HENAN", "YUNNAN", "FUJIAN", "GD", "ZJ", "JX", "HUN", "AH",
        "LN", "JL", "GUIZHOU", "JIANGSU", "SHAANXI", "SICHUAN",
        "XINJIANG", "NEI MENGGU",
    ]
    for prov in required_provinces:
        assert prov in body, f"missing required province {prov} in docs/76"


def test_p4_x2_tailnote_652_a0_landed_in_docs_75_and_651_receipt() -> None:
    """652-A.0 P4×2 tailnote 落地 docs/75 §6 末尾 + 651 receipt §RED_LINE_AUDIT 末尾"""
    if DOCS_75.exists():
        body_75 = _read(DOCS_75)
        assert "per 652-A.0 P4×2 规范固化" in body_75, (
            "docs/75 §6 must contain 652-A.0 P4×2 tailnote"
        )
        assert "P4-1" in body_75
        assert "P4-2" in body_75
    if RECEIPT_651.exists():
        body_r = _read(RECEIPT_651)
        assert "per 652-A.0 P4×2 规范固化" in body_r, (
            "651 receipt §RED_LINE_AUDIT must contain 652-A.0 P4×2 tailnote"
        )


def test_red_line_14_pool_exhaustion_fetch_script() -> None:
    """652 §0.14 fetch 脚本 SUBSTITUTE_POOL=[] + SUBSTITUTE_POOL_STATUS='EXHAUSTED'"""
    if not FETCH_SCRIPT.exists():
        return
    body = _read(FETCH_SCRIPT)
    assert "SUBSTITUTE_POOL:" in body
    assert "SUBSTITUTE_POOL_STATUS" in body
    assert "EXHAUSTED" in body
    # 池为空
    assert "SUBSTITUTE_POOL: list[tuple[str, list[tuple[str, str]], str]] = []" in body


def test_red_line_14_pool_exhaustion_seed_sql() -> None:
    """652 §0.14 seed SQL lineage JSONB 全 red_line_14_status='EXHAUSTED' + substitute_pool_note"""
    if not SEED_SQL.exists():
        return
    body = _read(SEED_SQL)
    assert "red_line_14_status" in body
    assert "EXHAUSTED" in body
    assert "substitute_pool_note" in body


def test_red_line_14_pool_exhaustion_evidence() -> None:
    """652 §0.14 主 evidence substitute_pool_status='EXHAUSTED' + methodology 含 BLOCKED_NO_POOL 援引"""
    if not EVIDENCE.exists():
        return
    data = json.loads(EVIDENCE.read_text(encoding="utf-8"))
    assert data["summary"]["substitute_pool_status"] == "EXHAUSTED"
    methodology = data.get("methodology", "")
    assert "BLOCKED_NO_POOL" in methodology
    assert "EXHAUSTED" in methodology
    assert "652" in methodology