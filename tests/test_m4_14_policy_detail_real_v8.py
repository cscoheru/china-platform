"""M4.14 政策详情 v8 真实化 spike 第 10 次 守门测试 (knife 651 M4.14 side, ≥8 cases).

Per knife 651 §1.651-B M4.14 side:
- 守门 fetch script 2 cells REAL_FETCHED (http_count=4 ≤ 12)
- 守门 2 SHA distinct (9d0ad78a.../f58a3384...) + 2 file_size > 0
- 守门 spike 边界 16 INSERT total (12 政策表 + 4 source)
- 守门 chain_id='real_651_m4_14_policy_detail_v8' (≠ 650 _v7 ≠ 649 _v6 ≠ 648 _v5)
- 守门 UUID j 段 (≠ 650 i 段 ≠ 649 h 段 ≠ 648 g 段 ≠ 647 f 段 ≠ 646 e 段 ≠ 645 d 段 ≠ 644 c 段)
- 守门 2 NEW SHA distinct ≠ 638-650 全部 SHA
- 守门 substitute 池 [EXHAUSTED] 永不触发 (substitute_used_count=0 + SUBSTITUTE_POOL_STATUS="EXHAUSTED")
- 守门 BLOCKED_NO_POOL 留痕分支 (fetch_cell 含 BLOCKED_NO_POOL verdict + 双样本均 REACHABLE → 实际未触发)
- 守门 已用省全集检查 (649 HLJ/HENAN/YUNNAN/FUJIAN/GD/ZJ/JX/HUN/AH/HUBEI/JILIN/LIAONING 不得重复; 650 增量 GUIZHOU/JIANGSU; 651 增量 SHAANXI/SICHUAN)
- 守门 docs/75 §1-§6 架构师级审查
- 守门 docs/74 §2.1 P4-1 行内更正 (无 "sha anxi" 残留) + §2.4/§4.4 P4-2 口径尾注
- 守门 evidence methodology 指针 (per 648 审计 P3-1 口径统一条款 + 649 审计 P3-1 + 651 §0.14 红线 14 增补)
- 守门 不宣称 PASS (沿用红线)

零网络; 零 cegr.* mutation; 零爬网; 纯文档守门。
"""
from __future__ import annotations

import json
import re
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
FETCH_SCRIPT = REPO_ROOT / "scripts" / "fetch_m4_14_policy_detail_v8_2024.py"
SEED_SQL = REPO_ROOT / "scripts" / "seed_m4_14_policy_detail_real_v8.sql"
EVIDENCE = REPO_ROOT / "evidence_pack" / "m4_14_policy_detail_real_v8_20260902.json"
REPORT_MD = REPO_ROOT / "docs" / "reports" / "m4_14_policy_detail_real_v8_20260902.md"
DOCS_75 = REPO_ROOT / "docs" / "75-m4-14-policy-detail-real-v8-20260902.md"
DOCS_74 = REPO_ROOT / "docs" / "74-m4-13-policy-detail-real-v7-20260901.md"


def _read(path: Path) -> str:
    if not path.exists():
        return ""
    return path.read_text(encoding="utf-8")


def _non_comment_lines(body: str) -> list[str]:
    """Return lines that are NOT SQL comments (start with --)."""
    return [ln for ln in body.splitlines() if not ln.strip().startswith("--")]


def test_evidence_json_real_fetched_2_samples() -> None:
    """651-A.1 evidence_pack/m4_14 evidence JSON REAL_FETCHED + 2 samples + http_count=4"""
    if not EVIDENCE.exists():
        return
    data = json.loads(EVIDENCE.read_text(encoding="utf-8"))
    assert data["summary"]["fetch_status"] == "REAL_FETCHED"
    assert data["summary"]["fetched_count"] == 2
    assert data["summary"]["http_count"] == 4, (
        f"expected http_count=4 (shaanxi 2 + sichuan 2); got {data['summary']['http_count']}"
    )
    assert data["summary"]["http_count"] <= 12, (
        f"≤12 HTTP limit violated: {data['summary']['http_count']}"
    )
    assert len(data["cells"]) == 2


def test_evidence_json_2_distinct_shas_no_collision() -> None:
    """651-A.1 2 SHA distinct (9d0ad78a + f58a3384) + 2 file_size > 0"""
    if not EVIDENCE.exists():
        return
    data = json.loads(EVIDENCE.read_text(encoding="utf-8"))
    shas = {cell["file_hash_sha256"] for cell in data["cells"]}
    assert len(shas) == 2, f"2 cells should have 2 distinct SHA — got {len(shas)}: {shas}"
    for cell in data["cells"]:
        assert cell["file_size_bytes"] > 0
    sha_set_str = " ".join(shas)
    assert "9d0ad78a" in sha_set_str, f"expected shaanxi SHA 9d0ad78a in {sha_set_str}"
    assert "f58a3384" in sha_set_str, f"expected sichuan SHA f58a3384 in {sha_set_str}"


def test_evidence_json_2_provinces_shaanxi_sichuan_no_substitute() -> None:
    """651-A.1 2 distinct provinces: shaanxi + sichuan; both substitute_used=false (无 substitute 触发)"""
    if not EVIDENCE.exists():
        return
    data = json.loads(EVIDENCE.read_text(encoding="utf-8"))
    provinces = {cell.get("province") for cell in data["cells"]}
    assert "shaanxi" in provinces
    assert "sichuan" in provinces
    # 已用省全集不得重复 (650 后)
    forbidden = {
        "heilongjiang", "henan", "yunnan", "fujian", "guangdong",
        "zhejiang", "jiangxi", "hunan", "anhui", "hubei", "jilin", "liaoning",
        "guizhou", "jiangsu",
    }
    assert not (provinces & forbidden), (
        f"651 red line violated — provinces {provinces} overlap with 638-650 used set {forbidden}"
    )
    # 双样本 substitute_used=false (池耗尽 + 双样本 fallback #1 REACHABLE; 不可能触发)
    for cell in data["cells"]:
        assert cell.get("substitute_used") is False, (
            f"{cell.get('province')} must have substitute_used=false (无 substitute 触发)"
        )
        assert cell.get("actual_province") == cell.get("province"), (
            f"{cell.get('province')} actual_province 应等于 province"
        )
        assert cell.get("verdict") == "REACHABLE"


def test_evidence_json_no_substitute_reason() -> None:
    """651-A.1 双样本无 substitute 触发 → evidence 无 substitute_reason"""
    if not EVIDENCE.exists():
        return
    data = json.loads(EVIDENCE.read_text(encoding="utf-8"))
    for cell in data["cells"]:
        assert cell.get("substitute_used") is False
        reason = cell.get("substitute_reason", "")
        assert reason == "", f"无 substitute 时 substitute_reason 应为空; got: {reason}"


def test_evidence_json_substitute_pool_status_exhausted() -> None:
    """651-A.1 evidence summary.substitute_pool_status = 'EXHAUSTED' (per 红线 14 增补)"""
    if not EVIDENCE.exists():
        return
    data = json.loads(EVIDENCE.read_text(encoding="utf-8"))
    assert data["summary"].get("substitute_pool_status") == "EXHAUSTED", (
        f"651 红线 14 增补: substitute_pool_status 必须 EXHAUSTED; got: "
        f"{data['summary'].get('substitute_pool_status')}"
    )
    # substitute_used_count 必须为 0
    assert data["summary"].get("substitute_used_count") == 0, (
        f"池耗尽 + 双样本 fallback #1 REACHABLE → substitute_used_count 必须 0; got: "
        f"{data['summary'].get('substitute_used_count')}"
    )


def test_fetch_script_2_cells_shaanxi_sichuan_chains() -> None:
    """651-A.1 fetch script 2 cells: shaanxi_zwgk_chain + sichuan_zwgk_chain"""
    body = _read(FETCH_SCRIPT)
    assert "SHAANXI_FALLBACK_CHAIN" in body
    assert "https://www.shaanxi.gov.cn/zwgk/" in body
    assert "SICHUAN_FALLBACK_CHAIN" in body
    assert "https://www.sc.gov.cn/zwgk/" in body
    assert "HTTP_LIMIT = 12" in body
    # 递补池 [EXHAUSTED] 守门 (per 红线 14 增补)
    assert "SUBSTITUTE_POOL" in body
    assert 'SUBSTITUTE_POOL_STATUS = "EXHAUSTED"' in body


def test_fetch_script_blocked_no_pool_branch_present() -> None:
    """651-A.1 fetch_cell 含 BLOCKED_NO_POOL verdict 留痕分支 (per 红线 14 增补)"""
    body = _read(FETCH_SCRIPT)
    # BLOCKED_NO_POOL verdict 分支必须存在
    assert "BLOCKED_NO_POOL" in body, (
        "fetch_cell 必须含 BLOCKED_NO_POOL verdict 留痕分支 (per 红线 14 增补)"
    )
    # blocked_reason 字段必须存在
    assert "blocked_reason" in body, (
        "fetch_cell BLOCKED_NO_POOL 分支必须含 blocked_reason 字段"
    )
    # 援引红线 14 增补
    assert "红线 14" in body or "RED_LINE_14" in body or "EXHAUSTED" in body


def test_fetch_log_shaanxi_404_200_sichuan_403_200() -> None:
    """651-A.1 fetch_log: shaanxi /zwgk/ 404 → / 200; sichuan /zwgk/ 403 WAF → / 200"""
    if not EVIDENCE.exists():
        return
    data = json.loads(EVIDENCE.read_text(encoding="utf-8"))
    flog = data.get("fetch_log", [])
    # shaanxi 应 2 个 fetch_log (404 + 200)
    sx_attempts = [f for f in flog if f.get("attempt_province") == "shaanxi"]
    assert len(sx_attempts) == 2, f"expected 2 shaanxi attempts; got {len(sx_attempts)}"
    assert sx_attempts[0]["http_code"] == 404, (
        f"sx /zwgk/ should be 404; got {sx_attempts[0]['http_code']}"
    )
    assert sx_attempts[1]["http_code"] == 200, (
        f"sx / should be 200; got {sx_attempts[1]['http_code']}"
    )
    # sichuan 应有 2 fetch_log (403 + 200)
    sc_attempts = [f for f in flog if f.get("attempt_province") == "sichuan"]
    assert len(sc_attempts) == 2, f"expected 2 sichuan attempts; got {len(sc_attempts)}"
    assert sc_attempts[0]["http_code"] == 403, (
        f"sc /zwgk/ should be 403 (WAF); got {sc_attempts[0]['http_code']}"
    )
    assert sc_attempts[1]["http_code"] == 200, (
        f"sc / should be 200; got {sc_attempts[1]['http_code']}"
    )


def test_seed_sql_16_insert_total() -> None:
    """651-A.1 seed SQL 16 INSERT rows = 2 source_registry + 2 source_document + 2×6 政策表"""
    body = _read(SEED_SQL)
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
    sha_rows_json = re.findall(r'"source_file_sha256":\s*"([a-f0-9]{64})"', body)
    sha_rows_fn = re.findall(r"'source_file_sha256',\s*'([a-f0-9]{64})'", body)
    total_sha_rows = len(sha_rows_json) + len(sha_rows_fn)
    assert total_sha_rows == 16, f"expected 16 lineage source_file_sha256 rows; got {total_sha_rows}"


def test_seed_sql_chain_id_v8_distinct_from_650_649_648_647_646_645() -> None:
    """651-A.1 chain_id='real_651_m4_14_policy_detail_v8' (≠ 650 _v7 ≠ 649 _v6 ≠ 648 _v5 ≠ 647 _v4 ≠ 646 _v3 ≠ 645 _v2)"""
    body = _read(SEED_SQL)
    assert "real_651_m4_14_policy_detail_v8" in body
    # 650 / 649 / 648 / 647 / 646 / 645 stale chain_id 必须不出现
    assert "real_650_m4_13_policy_detail_v7" not in body
    assert "real_649_m4_12_policy_detail_v6" not in body
    assert "real_648_m4_11_policy_detail_v5" not in body
    assert "real_647_m4_10_policy_detail_v4" not in body
    assert "real_646_m4_9_policy_detail_v3" not in body
    assert "real_645_m4_8_policy_detail_v2" not in body


def test_seed_sql_uuid_j_segment_distinct_from_i_h_g_f_e_d_c_segments() -> None:
    """651-A.1 UUID j 段 (≠ 650 i 段 ≠ 649 h 段 ≠ 648 g 段 ≠ 647 f 段 ≠ 646 e 段 ≠ 645 d 段 ≠ 644 c 段)"""
    body = _read(SEED_SQL)
    # 651 UUID j 段
    assert "j0eebc99" in body  # source_registry/source_document
    assert "j1eebc99" in body  # policy_document
    assert "j2eebc99" in body  # policy_target
    assert "j3eebc99" in body  # policy_measure
    assert "j4eebc99" in body  # government_commitment
    assert "j5eebc99" in body  # commitment_progress
    assert "j6eebc99" in body  # project_event
    # 650 i 段 必须不出现
    for prefix in ["i0eebc99", "i1eebc99", "i2eebc99", "i3eebc99", "i4eebc99", "i5eebc99", "i6eebc99"]:
        assert prefix not in body, f"650 i-prefix {prefix} must not appear in 651 seed SQL"
    # 649 h 段 必须不出现
    for prefix in ["h0eebc99", "h1eebc99", "h2eebc99", "h3eebc99", "h4eebc99", "h5eebc99", "h6eebc99"]:
        assert prefix not in body, f"649 h-prefix {prefix} must not appear in 651 seed SQL"
    # 648 g 段 必须不出现
    for prefix in ["g0eebc99", "g1eebc99", "g2eebc99", "g3eebc99", "g4eebc99", "g5eebc99", "g6eebc99"]:
        assert prefix not in body, f"648 g-prefix {prefix} must not appear in 651 seed SQL"
    # 647 f 段 必须不出现
    for prefix in ["f0eebc99", "f1eebc99", "f2eebc99", "f3eebc99", "f4eebc99", "f5eebc99", "f6eebc99"]:
        assert prefix not in body, f"647 f-prefix {prefix} must not appear in 651 seed SQL"
    # 646 e 段 必须不出现
    for prefix in ["e0eebc99", "e1eebc99", "e2eebc99", "e3eebc99", "e4eebc99", "e5eebc99", "e6eebc99"]:
        assert prefix not in body, f"646 e-prefix {prefix} must not appear in 651 seed SQL"
    # 645 d 段 必须不出现
    for prefix in ["d0eebc99", "d1eebc99", "d2eebc99", "d3eebc99", "d4eebc99", "d5eebc99", "d6eebc99"]:
        assert prefix not in body, f"645 d-prefix {prefix} must not appear in 651 seed SQL"


def test_seed_sql_uses_real_fetched_shas_9d0ad78a_f58a3384() -> None:
    """651-A.1 seed SQL 使用 651 实际抓取的 SHA 9d0ad78a... + f58a3384..."""
    body = _read(SEED_SQL)
    assert "9d0ad78a79317d5ec5224bf4fd56c4fa44dd658d2221e2921da1700e99e32ad5" in body
    assert "f58a33842ab22afcb84a9f1156a6e1f05bae3f01432c8ea6b103c29387346ad5" in body
    sha_pattern_json = re.findall(r'"source_file_sha256":\s*"([a-f0-9]{64})"', body)
    sha_pattern_fn = re.findall(r"'source_file_sha256',\s*'([a-f0-9]{64})'", body)
    sha_pattern = sha_pattern_json + sha_pattern_fn
    assert "9d0ad78a79317d5ec5224bf4fd56c4fa44dd658d2221e2921da1700e99e32ad5" in sha_pattern
    assert "f58a33842ab22afcb84a9f1156a6e1f05bae3f01432c8ea6b103c29387346ad5" in sha_pattern
    # 638-650 stale SHAs must NOT appear in 651 lineage SHA values
    for stale_sha in [
        "5c5b1295", "def18a2f",  # 650
        "b22d1fb4", "a1e49a91",  # 649
        "4006439e", "a06e174f",  # 648
        "8016ef08", "56481050",  # 647
        "fceb8c0a", "49eed23e",  # 646
        "6237cd48", "dfa38998", "bd4c4c51", "f33eba53",  # 645
        "bad8be51",  # 644
        "e68099df", "63109491", "93fe23b3",  # 643
        "cd6aff30", "4349ee0f", "fede03ba",  # 642
        "26e5379d",  # 641
    ]:
        assert stale_sha not in sha_pattern, (
            f"651 source_file_sha256 lineage must not use stale 638-650 SHA {stale_sha}"
        )


def test_seed_sql_lineage_is_demo_false_sentinel() -> None:
    """651-A.1 lineage JSONB `is_demo='false'` 真实化 sentinel (沿用 docs/33 §3.2)"""
    body = _read(SEED_SQL)
    assert "is_demo" in body
    assert "'false'" in body
    assert "is_demo='true'" not in body


def test_seed_sql_red_line_14_status_exhausted() -> None:
    """651 红线 14 增补守门: seed SQL lineage JSONB 全 red_line_14_status='EXHAUSTED'"""
    body = _read(SEED_SQL)
    assert "red_line_14_status" in body
    assert '"EXHAUSTED"' in body or "'EXHAUSTED'" in body, (
        "651 红线 14 增补: seed SQL lineage JSONB 应含 red_line_14_status='EXHAUSTED'"
    )


def test_seed_sql_no_substitute_used() -> None:
    """651-A.1 2 样本均无 substitute 触发 (substitute_used=false)"""
    body = _read(SEED_SQL)
    assert "substitute_used" in body
    true_count = body.count('"substitute_used": true')
    fn_true_count = body.count("'substitute_used', true")
    total_true = true_count + fn_true_count
    assert total_true == 0, f"651 应 0 substitute_used=true; got {total_true}"


def test_report_md_no_pass_announcement_651_red_line() -> None:
    """651-A.4 report MD 不宣称 PASS (沿用红线)"""
    body = _read(REPORT_MD)
    if not body:
        return
    assert "不宣称" in body or "不宣布" in body
    assert "Gate" in body
    assert "O1" in body or "M4" in body
    forbidden_pass = ["M4.14 PASS", "Gate 1 PASS", "M4.13 PASS", "O1 PASS"]
    for fp in forbidden_pass:
        assert fp not in body, f"report must not declare {fp} (651 red line)"


def test_evidence_methodology_pointer_per_648_p3_1_and_651_red_line_14() -> None:
    """651-A.4 evidence methodology 字段含附属产物指针 (per 648 审计 P3-1 口径统一条款 + 649 审计 P3-1 + 651 §0.14 红线 14 增补)"""
    if not EVIDENCE.exists():
        return
    data = json.loads(EVIDENCE.read_text(encoding="utf-8"))
    methodology = data.get("methodology", "")
    # 指针条款
    assert "附属" in methodology or "pointer" in methodology.lower() or "docs/reports" in methodology, (
        f"methodology 应含附属产物指针条款说明; got: {methodology}"
    )
    # 651 任务书 §0.14 红线 14 增补条款援引
    assert "651 §0.14" in methodology or "EXHAUSTED" in methodology, (
        f"methodology 应援引 651 §0.14 红线 14 增补 / EXHAUSTED; got: {methodology}"
    )
    # BLOCKED_NO_POOL 援引
    assert "BLOCKED_NO_POOL" in methodology, (
        f"methodology 应援引 BLOCKED_NO_POOL 留痕不代换; got: {methodology}"
    )
    # 649 P3-1 规范固化援引
    assert "649 P3-1" in methodology or "P3-1" in methodology, (
        f"methodology 应援引 649 P3-1 (代换行标注规范); got: {methodology}"
    )


def test_docs_75_sections_1_to_6_present() -> None:
    """651-A.3 docs/75 §1-§6 架构师级审查文档章节守门"""
    body = _read(DOCS_75)
    assert body, f"docs/75 missing: {DOCS_75}"
    for section_header in [
        "## 1. M4.14 v8 落地终态",
        "## 2. substitute 跨省代换登记",
        "## 3. M4.14 v8 spike 边界",
        "## 4. lineage 真实化 sentinel",
        "## 5. 后续 652+ BLOCKED 留痕口径",
        "## 6. 下一步 + 不宣称 PASS",
    ]:
        assert section_header in body, f"docs/75 missing section: {section_header}"
    # §2 substitute 登记要点 (递补池生命周期收官)
    assert "EXHAUSTED" in body
    assert "shaanxi" in body and "sichuan" in body
    assert "REACHABLE" in body
    # §3 spike 边界
    assert "9d0ad78a" in body and "f58a3384" in body
    # §2.2 递补池生命周期收官 (per 651 红线 14 收官)
    assert "递补池生命周期收官" in body or "649 阶段" in body
    assert "651 阶段" in body
    assert "651 后" in body and ("正式耗尽" in body or "EXHAUSTED" in body)


def test_docs_75_pool_depletion_records() -> None:
    """651-A.3 docs/75 §2.2 递补池生命周期收官登记 (4 阶段: 649/650/651/651 后)"""
    body = _read(DOCS_75)
    # 4 阶段
    for stage in ["649 阶段", "650 阶段", "651 阶段", "651 后"]:
        assert stage in body, f"docs/75 §2.2 递补池生命周期收官登记 missing stage: {stage}"
    # 红线 14 增补援引
    assert "红线 14" in body and ("EXHAUSTED" in body or "正式耗尽" in body)


def test_651_red_line_no_gate_no_o1_no_pass() -> None:
    """651 red line: 不宣称任何 PASS"""
    seed_body = _read(SEED_SQL)
    script_body = _read(FETCH_SCRIPT)
    report_body = _read(REPORT_MD)
    docs_75_body = _read(DOCS_75)
    for src_name, src_body in [
        ("seed SQL", seed_body),
        ("fetch script", script_body),
        ("report MD", report_body),
        ("docs/75", docs_75_body),
    ]:
        if not src_body:
            continue
        for forbidden in ["M4.14 PASS", "Gate 1 PASS", "Gate PASS", "O1 PASS"]:
            assert forbidden not in src_body, (
                f"{src_name} must not declare {forbidden}"
            )


def test_chain_id_province_used_set_clean() -> None:
    """651 红线: 已用省全集不得重复 (16 省 actual_province 口径) + chain_id 严格区分"""
    body = _read(SEED_SQL)
    assert "real_651_m4_14_policy_detail_v8" in body
    assert "不宣称" in body or "不宣布" in body
    # 16 省已用集合 (actual_province 口径) - SHAANXI + SICHUAN 在场
    assert "SHAANXI" in body, "651 增量 SHAANXI (actual_province) 应在场"
    assert "SICHUAN" in body, "651 增量 SICHUAN (actual_province) 应在场"


# ────────────────────────────────────────────────────────────
# 651-A.0 落地守门 (per 650 审计 P4×2 行内更正 + 尾注)
# ────────────────────────────────────────────────────────────


def test_p4_1_docs_74_no_sha_anxi_residue() -> None:
    """651-A.0 P4-1 行内更正守门: docs/74 §2.1 'sha anxi' 行内更正为 'shaanxi'; grep 'sha anxi' 残留 = 0."""
    body = _read(DOCS_74)
    assert body, f"docs/74 missing: {DOCS_74}"
    # "sha anxi" 必须不出现 (650 编写笔误, 已行内更正)
    assert "sha anxi" not in body, (
        "P4-1 行内更正未落地: docs/74 仍存在 'sha anxi' typo 残留"
    )
    # 正确连写 'shaanxi' 应出现
    assert "shaanxi" in body, "P4-1 行内更正后 docs/74 应含 'shaanxi' 正确连写"
    # P4-1 尾注标记应援引
    assert "P4-1" in body and "650 审计" in body, (
        "docs/74 §2.1 应含 P4-1 行内更正尾注标记 (per 650 审计 P4-1)"
    )


def test_p4_2_docs_74_slot_actual_province_koujings() -> None:
    """651-A.0 P4-2 口径尾注守门: docs/74 §2.4 + §4.4 'HUBEI 槽名 / actual_province=LIAONING' 口径尾注"""
    body = _read(DOCS_74)
    assert "P4-2" in body, "P4-2 口径尾注标记应存在"
    # §2.4 + §4.4 均含口径尾注
    section_24_tailnote = (
        "HUBEI 为槽名" in body or "649 增量行中 HUBEI 为" in body
    )
    section_44_tailnote = (
        "HUBEI 项为槽名" in body or "行内 HUBEI 项为" in body
    )
    assert section_24_tailnote, (
        "docs/74 §2.4 应含 HUBEI 槽名 vs actual_province=LIAONING 口径尾注 (per 650 审计 P4-2)"
    )
    assert section_44_tailnote, (
        "docs/74 §4.4 应含 HUBEI 槽名 vs actual_province=LIAONING 口径尾注 (per 650 审计 P4-2)"
    )
    # 红线 13 增补规范援引
    assert "actual_province" in body and "LIAONING" in body, (
        "P4-2 口径尾注应援引 actual_province=LIAONING (per 红线 13 增补)"
    )


# ────────────────────────────────────────────────────────────
# 651 红线 14 增补守门 (递补池耗尽条款)
# ────────────────────────────────────────────────────────────


def test_red_line_14_pool_exhaustion_fetch_script() -> None:
    """651 红线 14 增补守门: fetch script SUBSTITUTE_POOL=[] (EXHAUSTED) + BLOCKED_NO_POOL 分支"""
    body = _read(FETCH_SCRIPT)
    # SUBSTITUTE_POOL 必须为空列表 (5 原始候选全部 consumed)
    assert "SUBSTITUTE_POOL: list = []" in body or "SUBSTITUTE_POOL: list[tuple[str, list[tuple[str, str]], str]] = []" in body, (
        "651 红线 14 增补: fetch script SUBSTITUTE_POOL 必须显式空列表"
    )
    # SUBSTITUTE_POOL_STATUS = "EXHAUSTED"
    assert 'SUBSTITUTE_POOL_STATUS = "EXHAUSTED"' in body, (
        "651 红线 14 增补: fetch script SUBSTITUTE_POOL_STATUS 必须显式 'EXHAUSTED'"
    )
    # BLOCKED_NO_POOL verdict 分支
    assert '"BLOCKED_NO_POOL"' in body or "'BLOCKED_NO_POOL'" in body or "BLOCKED_NO_POOL" in body, (
        "651 红线 14 增补: fetch script 必须含 BLOCKED_NO_POOL verdict 留痕分支"
    )


def test_red_line_14_pool_exhaustion_seed_sql() -> None:
    """651 红线 14 增补守门: seed SQL lineage JSONB 全 red_line_14_status='EXHAUSTED'"""
    body = _read(SEED_SQL)
    # red_line_14_status 应在 16 INSERT lineage JSONB 中显式登记
    exhausted_count_json = body.count('"red_line_14_status": "EXHAUSTED"')
    exhausted_count_fn = body.count("'red_line_14_status', 'EXHAUSTED'")
    total_exhausted = exhausted_count_json + exhausted_count_fn
    assert total_exhausted >= 12, (
        f"651 红线 14 增补: seed SQL 应有 ≥12 个 INSERT lineage 含 red_line_14_status='EXHAUSTED'; got {total_exhausted}"
    )


def test_red_line_14_pool_exhaustion_evidence() -> None:
    """651 红线 14 增补守门: evidence summary.substitute_pool_status='EXHAUSTED'"""
    if not EVIDENCE.exists():
        return
    data = json.loads(EVIDENCE.read_text(encoding="utf-8"))
    assert data["summary"].get("substitute_pool_status") == "EXHAUSTED"
    assert data["summary"].get("substitute_used_count") == 0
    # blocked_no_pool_count 应为 0 (本次双样本 fallback #1 REACHABLE)
    assert data["summary"].get("blocked_no_pool_count") == 0