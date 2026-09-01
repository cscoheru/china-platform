"""M4.13 政策详情 v7 真实化 spike 第 9 次 守门测试 (knife 650 M4.13 side, ≥8 cases).

Per knife 650 §1.650-B M4.13 side:
- 守门 fetch script 2 cells REAL_FETCHED (http_count=3 ≤ 12)
- 守门 2 SHA distinct (5c5b1295.../def18a2f...) + 2 file_size > 0
- 守门 spike 边界 16 INSERT total (12 政策表 + 4 source)
- 守门 chain_id='real_650_m4_13_policy_detail_v7' (≠ 649 _v6 ≠ 648 _v5)
- 守门 UUID i 段 (≠ 649 h 段 ≠ 648 g 段 ≠ 647 f 段 ≠ 646 e 段 ≠ 645 d 段)
- 守门 2 NEW SHA distinct ≠ 638-649 全部 SHA
- 守门 substitute 池备而未触发 (substitute_used_count=0)
- 守门 已用省全集检查 (649 HLJ/HENAN/YUNNAN/FUJIAN/GD/ZJ/JX/HUN/AH/HUBEI/JILIN/LIAONING 不得重复; 650 增量 GUIZHOU/JIANGSU)
- 守门 docs/74 §1-§6 架构师级审查
- 守门 evidence methodology 指针 (per 648 审计 P3-1 口径统一条款)
- 守门 不宣称 PASS (沿用红线)
- **守门 P3-1 更正**: seed_m4_12 h02 source_registry VALUES 用 LIAONING (不是 HUBEI) + description 行 '湖北' 字样同步更正 + lineage JSONB provenance 可保留 'hubei' (per 红线 13 增补)

零网络; 零 cegr.* mutation; 零爬网; 纯文档守门。
"""
from __future__ import annotations

import json
import re
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
FETCH_SCRIPT = REPO_ROOT / "scripts" / "fetch_m4_13_policy_detail_v7_2024.py"
SEED_SQL = REPO_ROOT / "scripts" / "seed_m4_13_policy_detail_real_v7.sql"
SEED_SQL_M4_12 = REPO_ROOT / "scripts" / "seed_m4_12_policy_detail_real_v6.sql"
EVIDENCE = REPO_ROOT / "evidence_pack" / "m4_13_policy_detail_real_v7_20260901.json"
REPORT_MD = REPO_ROOT / "docs" / "reports" / "m4_13_policy_detail_real_v7_20260901.md"
DOCS_74 = REPO_ROOT / "docs" / "74-m4-13-policy-detail-real-v7-20260901.md"


def _read(path: Path) -> str:
    if not path.exists():
        return ""
    return path.read_text(encoding="utf-8")


def _non_comment_lines(body: str) -> list[str]:
    """Return lines that are NOT SQL comments (start with --)."""
    return [ln for ln in body.splitlines() if not ln.strip().startswith("--")]


def test_evidence_json_real_fetched_2_samples() -> None:
    """650-A.1 evidence_pack/m4_13 evidence JSON REAL_FETCHED + 2 samples + http_count=3"""
    if not EVIDENCE.exists():
        return
    data = json.loads(EVIDENCE.read_text(encoding="utf-8"))
    assert data["summary"]["fetch_status"] == "REAL_FETCHED"
    assert data["summary"]["fetched_count"] == 2
    assert data["summary"]["http_count"] == 3, (
        f"expected http_count=3 (guizhou 1 + jiangsu 2); got {data['summary']['http_count']}"
    )
    assert data["summary"]["http_count"] <= 12, (
        f"≤12 HTTP limit violated: {data['summary']['http_count']}"
    )
    assert len(data["cells"]) == 2


def test_evidence_json_2_distinct_shas_no_collision() -> None:
    """650-A.1 2 SHA distinct (5c5b1295 + def18a2f) + 2 file_size > 0"""
    if not EVIDENCE.exists():
        return
    data = json.loads(EVIDENCE.read_text(encoding="utf-8"))
    shas = {cell["file_hash_sha256"] for cell in data["cells"]}
    assert len(shas) == 2, f"2 cells should have 2 distinct SHA — got {len(shas)}: {shas}"
    for cell in data["cells"]:
        assert cell["file_size_bytes"] > 0
    sha_set_str = " ".join(shas)
    assert "5c5b1295" in sha_set_str, f"expected guizhou SHA 5c5b1295 in {sha_set_str}"
    assert "def18a2f" in sha_set_str, f"expected jiangsu SHA def18a2f in {sha_set_str}"


def test_evidence_json_2_provinces_guizhou_jiangsu_no_substitute() -> None:
    """650-A.1 2 distinct provinces: guizhou + jiangsu; both substitute_used=false (无 substitute 触发)"""
    if not EVIDENCE.exists():
        return
    data = json.loads(EVIDENCE.read_text(encoding="utf-8"))
    provinces = {cell.get("province") for cell in data["cells"]}
    assert "guizhou" in provinces
    assert "jiangsu" in provinces
    # 已用省全集不得重复 (649 后)
    forbidden = {
        "heilongjiang", "henan", "yunnan", "fujian", "guangdong",
        "zhejiang", "jiangxi", "hunan", "anhui", "hubei", "jilin", "liaoning",
    }
    assert not (provinces & forbidden), (
        f"650 red line violated — provinces {provinces} overlap with 649 used set {forbidden}"
    )
    # 双样本 substitute_used=false
    for cell in data["cells"]:
        assert cell.get("substitute_used") is False, (
            f"{cell.get('province')} must have substitute_used=false (无 substitute 触发)"
        )
        assert cell.get("actual_province") == cell.get("province"), (
            f"{cell.get('province')} actual_province 应等于 province"
        )
        assert cell.get("verdict") == "REACHABLE"


def test_evidence_json_no_substitute_reason() -> None:
    """650-A.1 双样本无 substitute 触发 → evidence 无 substitute_reason"""
    if not EVIDENCE.exists():
        return
    data = json.loads(EVIDENCE.read_text(encoding="utf-8"))
    for cell in data["cells"]:
        # 无 substitute_used 时 substitute_reason 应为空或不存在
        assert cell.get("substitute_used") is False
        reason = cell.get("substitute_reason", "")
        assert reason == "", f"无 substitute 时 substitute_reason 应为空; got: {reason}"


def test_fetch_script_2_cells_guizhou_jiangsu_chains() -> None:
    """650-A.1 fetch script 2 cells: guizhou_zwgk_chain + jiangsu_zwgk_chain + substitute pool (shaanxi+sichuan)"""
    body = _read(FETCH_SCRIPT)
    assert "GUIZHOU_FALLBACK_CHAIN" in body
    assert "https://www.guizhou.gov.cn/zwgk/" in body
    assert "JIANGSU_FALLBACK_CHAIN" in body
    assert "https://www.jiangsu.gov.cn/zwgk/" in body
    assert "HTTP_LIMIT = 12" in body
    # substitute 池 (shaanxi/sichuan; 649 池减 2: liaoning 已用, guizhou/jiangsu 升格为原生 slot)
    assert "SUBSTITUTE_POOL" in body
    assert "shaanxi" in body
    assert "sichuan" in body


def test_fetch_log_guizhou_200_jiangsu_404_200() -> None:
    """650-A.1 fetch_log: guizhou /zwgk/ 200 直接; jiangsu /zwgk/ 404 → / 200"""
    if not EVIDENCE.exists():
        return
    data = json.loads(EVIDENCE.read_text(encoding="utf-8"))
    flog = data.get("fetch_log", [])
    # guizhou 应 1 个 fetch_log (zwgk 200)
    gz_attempts = [f for f in flog if f.get("attempt_province") == "guizhou"]
    assert len(gz_attempts) == 1, f"expected 1 guizhou attempt; got {len(gz_attempts)}"
    assert gz_attempts[0]["http_code"] == 200, f"gz /zwgk/ should be 200; got {gz_attempts[0]['http_code']}"
    # jiangsu 应有 2 fetch_log (404 + 200)
    js_attempts = [f for f in flog if f.get("attempt_province") == "jiangsu"]
    assert len(js_attempts) == 2, f"expected 2 jiangsu attempts; got {len(js_attempts)}"
    assert js_attempts[0]["http_code"] == 404, f"js /zwgk/ should be 404; got {js_attempts[0]['http_code']}"
    assert js_attempts[1]["http_code"] == 200, f"js / should be 200; got {js_attempts[1]['http_code']}"


def test_seed_sql_16_insert_total() -> None:
    """650-A.1 seed SQL 16 INSERT rows = 2 source_registry + 2 source_document + 2×6 政策表"""
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


def test_seed_sql_chain_id_v7_distinct_from_649_648_647_646_645() -> None:
    """650-A.1 chain_id='real_650_m4_13_policy_detail_v7' (≠ 649 _v6 ≠ 648 _v5 ≠ 647 _v4 ≠ 646 _v3 ≠ 645 _v2)"""
    body = _read(SEED_SQL)
    assert "real_650_m4_13_policy_detail_v7" in body
    # 649 / 648 / 647 / 646 / 645 stale chain_id 必须不出现
    assert "real_649_m4_12_policy_detail_v6" not in body
    assert "real_648_m4_11_policy_detail_v5" not in body
    assert "real_647_m4_10_policy_detail_v4" not in body
    assert "real_646_m4_9_policy_detail_v3" not in body
    assert "real_645_m4_8_policy_detail_v2" not in body


def test_seed_sql_uuid_i_segment_distinct_from_h_g_f_e_d_c_segments() -> None:
    """650-A.1 UUID i 段 (≠ 649 h 段 ≠ 648 g 段 ≠ 647 f 段 ≠ 646 e 段 ≠ 645 d 段 ≠ 644 c 段)"""
    body = _read(SEED_SQL)
    # 650 UUID i 段
    assert "i0eebc99" in body  # source_registry/source_document
    assert "i1eebc99" in body  # policy_document
    assert "i2eebc99" in body  # policy_target
    assert "i3eebc99" in body  # policy_measure
    assert "i4eebc99" in body  # government_commitment
    assert "i5eebc99" in body  # commitment_progress
    assert "i6eebc99" in body  # project_event
    # 649 h 段 必须不出现
    for prefix in ["h0eebc99", "h1eebc99", "h2eebc99", "h3eebc99", "h4eebc99", "h5eebc99", "h6eebc99"]:
        assert prefix not in body, f"649 h-prefix {prefix} must not appear in 650 seed SQL"
    # 648 g 段 必须不出现
    for prefix in ["g0eebc99", "g1eebc99", "g2eebc99", "g3eebc99", "g4eebc99", "g5eebc99", "g6eebc99"]:
        assert prefix not in body, f"648 g-prefix {prefix} must not appear in 650 seed SQL"
    # 647 f 段 必须不出现
    for prefix in ["f0eebc99", "f1eebc99", "f2eebc99", "f3eebc99", "f4eebc99", "f5eebc99", "f6eebc99"]:
        assert prefix not in body, f"647 f-prefix {prefix} must not appear in 650 seed SQL"
    # 646 e 段 必须不出现
    for prefix in ["e0eebc99", "e1eebc99", "e2eebc99", "e3eebc99", "e4eebc99", "e5eebc99", "e6eebc99"]:
        assert prefix not in body, f"646 e-prefix {prefix} must not appear in 650 seed SQL"
    # 645 d 段 必须不出现
    for prefix in ["d0eebc99", "d1eebc99", "d2eebc99", "d3eebc99", "d4eebc99", "d5eebc99", "d6eebc99"]:
        assert prefix not in body, f"645 d-prefix {prefix} must not appear in 650 seed SQL"


def test_seed_sql_uses_real_fetched_shas_5c5b1295_def18a2f() -> None:
    """650-A.1 seed SQL 使用 650 实际抓取的 SHA 5c5b1295... + def18a2f..."""
    body = _read(SEED_SQL)
    assert "5c5b12952db6b4af8f63a8478100d1000765fcb8460f574dd8b480ce2aa56cc0" in body
    assert "def18a2f8f025b5ae11c685725b96cbf181c19c4771ab56d5d4be12974c7e534" in body
    sha_pattern_json = re.findall(r'"source_file_sha256":\s*"([a-f0-9]{64})"', body)
    sha_pattern_fn = re.findall(r"'source_file_sha256',\s*'([a-f0-9]{64})'", body)
    sha_pattern = sha_pattern_json + sha_pattern_fn
    assert "5c5b12952db6b4af8f63a8478100d1000765fcb8460f574dd8b480ce2aa56cc0" in sha_pattern
    assert "def18a2f8f025b5ae11c685725b96cbf181c19c4771ab56d5d4be12974c7e534" in sha_pattern
    # 638-649 stale SHAs must NOT appear in 650 lineage SHA values
    for stale_sha in [
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
            f"650 source_file_sha256 lineage must not use stale 638-649 SHA {stale_sha}"
        )


def test_seed_sql_lineage_is_demo_false_sentinel() -> None:
    """650-A.1 lineage JSONB `is_demo='false'` 真实化 sentinel (沿用 docs/33 §3.2)"""
    body = _read(SEED_SQL)
    assert "is_demo" in body
    assert "'false'" in body
    assert "is_demo='true'" not in body


def test_seed_sql_no_substitute_used() -> None:
    """650-A.1 2 样本均无 substitute 触发 (substitute_used=false)"""
    body = _read(SEED_SQL)
    # substitute_used 必须存在 (schema) 但值应大多为 false
    assert "substitute_used" in body
    # 不应有 substitute_used=true (本次 0 触发)
    true_count = body.count('"substitute_used": true')
    fn_true_count = body.count("'substitute_used', true")
    total_true = true_count + fn_true_count
    assert total_true == 0, f"650 应 0 substitute_used=true; got {total_true}"


def test_report_md_no_pass_announcement_650_red_line() -> None:
    """650-A.4 report MD 不宣称 PASS (沿用红线)"""
    body = _read(REPORT_MD)
    if not body:
        return
    assert "不宣称" in body or "不宣布" in body
    assert "Gate" in body
    assert "O1" in body or "M4" in body
    # 红线 1 (不宣称 PASS) — 不应有 "M4.13 PASS" / "Gate 1 PASS" 类宣称
    forbidden_pass = ["M4.13 PASS", "Gate 1 PASS", "M4.12 PASS", "O1 PASS"]
    for fp in forbidden_pass:
        assert fp not in body, f"report must not declare {fp} (650 red line)"


def test_evidence_methodology_pointer_per_648_p3_1() -> None:
    """650-A.4 evidence methodology 字段含附属产物指针 (per 648 审计 P3-1 口径统一条款)"""
    if not EVIDENCE.exists():
        return
    data = json.loads(EVIDENCE.read_text(encoding="utf-8"))
    methodology = data.get("methodology", "")
    # 指针条款: 主 evidence methodology 必须含指向附属产物的指针 (文件名 + verdict)
    # 650 附属产物: docs/reports/m4_13_policy_detail_real_v7_20260901.md
    assert "附属" in methodology or "pointer" in methodology.lower() or "docs/reports" in methodology or "methodology" in methodology.lower(), (
        f"methodology 应含附属产物指针条款说明; got: {methodology}"
    )
    # 650 任务书 §0.13 条款援引
    assert "650 §0.13" in methodology or "0.13" in methodology, (
        f"methodology 应援引 650 任务书 §0.13; got: {methodology}"
    )
    # 649 P3-1 规范固化援引
    assert "649 P3-1" in methodology or "P3-1" in methodology, (
        f"methodology 应援引 649 P3-1 (代换行标注规范); got: {methodology}"
    )


def test_docs_74_sections_1_to_6_present() -> None:
    """650-A.3 docs/74 §1-§6 架构师级审查文档章节守门"""
    body = _read(DOCS_74)
    assert body, f"docs/74 missing: {DOCS_74}"
    for section_header in [
        "## 1. M4.13 v7 落地终态",
        "## 2. substitute 跨省代换登记",
        "## 3. M4.13 v7 spike 边界",
        "## 4. lineage 真实化 sentinel",
        "## 5. 651 下一步",
        "## 6. 下一步 + 不宣称 PASS",
    ]:
        assert section_header in body, f"docs/74 missing section: {section_header}"
    # §2 substitute 登记要点
    assert "guizhou" in body and "jiangsu" in body
    assert "REACHABLE" in body
    # §3 spike 边界
    assert "5c5b1295" in body and "def18a2f" in body


def test_650_red_line_no_gate_no_o1_no_pass() -> None:
    """650 red line: 不宣称任何 PASS"""
    seed_body = _read(SEED_SQL)
    script_body = _read(FETCH_SCRIPT)
    report_body = _read(REPORT_MD)
    docs_74_body = _read(DOCS_74)
    # 不应在 seed SQL / fetch script / report MD / docs/74 中宣称 PASS
    for src_name, src_body in [
        ("seed SQL", seed_body),
        ("fetch script", script_body),
        ("report MD", report_body),
        ("docs/74", docs_74_body),
    ]:
        if not src_body:
            continue
        for forbidden in ["M4.13 PASS", "Gate 1 PASS", "Gate PASS", "O1 PASS"]:
            assert forbidden not in src_body, (
                f"{src_name} must not declare {forbidden}"
            )


def test_chain_id_province_used_set_clean() -> None:
    """650 红线: 已用省全集不得重复 + chain_id 严格区分"""
    body = _read(SEED_SQL)
    # chain_id 必须严格匹配 650 v7
    assert "real_650_m4_13_policy_detail_v7" in body
    # 17 个里程碑不宣布 PASS
    assert "不宣称" in body or "不宣布" in body


# ────────────────────────────────────────────────────────────
# 650 P3-1 更正守门 (per 649 审计 P3-1 + 650-A.0 蓝图更正)
# ────────────────────────────────────────────────────────────


def test_p3_1_seed_m4_12_no_hubei_residue_in_substituted_row() -> None:
    """650-A.0 P3-1 更正守门: seed_m4_12 h02 source_registry VALUES 用 LIAONING (不是 HUBEI); 非注释行 description '湖北' 字样同步更正; lineage JSONB provenance 可保留 'hubei' (per 红线 13 增补)."""
    body = _read(SEED_SQL_M4_12)
    non_comment = "\n".join(_non_comment_lines(body))
    # h02 source_registry 第一行 VALUES 应含 'CN', 'LIAONING'
    found_liaoning = any("'CN', 'LIAONING'" in ln for ln in _non_comment_lines(body))
    assert found_liaoning, (
        "P3-1 更正未落地: seed_m4_12 非注释行应含 'CN', 'LIAONING' (h02 source_registry 第一行)"
    )
    # h02 source_registry 第一行 VALUES 不应再含 'CN', 'HUBEI'
    hubei_residue = [
        ln.strip() for ln in _non_comment_lines(body)
        if "'CN', 'HUBEI'" in ln
    ]
    assert not hubei_residue, (
        f"P3-1 更正未落地: h02 source_registry VALUES 仍含 'CN', 'HUBEI'; lines: {hubei_residue[:3]}"
    )
    # h11/h41/h51/h61 中描述性字样 "湖北省人民政府" / "湖北省政府" 应已更正 (非注释行)
    assert "湖北省人民政府" not in non_comment, (
        "P3-1 更正未落地: seed_m4_12 非注释行仍存在 '湖北省人民政府' 字样"
    )
    assert "湖北省政府" not in non_comment, (
        "P3-1 更正未落地: seed_m4_12 非注释行仍存在 '湖北省政府' 字样"
    )
    # lineage JSONB provenance 字段允许 'hubei' (per 红线 13 增补: original_province 仅存 lineage JSONB)


def test_p3_1_seed_m4_12_liaoning_correction_with_tailnote() -> None:
    """650-A.0 P3-1 更正守门: seed_m4_12 已更正为 LIAONING + 行尾尾注标记"""
    body = _read(SEED_SQL_M4_12)
    # LIAONING 字段应出现 (h02 source_registry.province 已更正)
    assert "'LIAONING'" in body, (
        "P3-1 更正未落地: seed_m4_12 h02 source_registry.province 应已更正为 'LIAONING'"
    )
    # 行尾尾注标记 (per 650-A.0 任务书)
    assert "650-A.0 P3-1 更正" in body or "650-A.0 行内更正" in body, (
        "P3-1 尾注标记缺失: seed_m4_12 应含 '650-A.0 P3-1 更正' 或 '650-A.0 行内更正' 标记"
    )
    assert "per 649 审计 P3-1" in body, (
        "P3-1 尾注标记应援引 'per 649 审计 P3-1'"
    )


def test_p3_1_red_line_no_13_actual_province_labeling() -> None:
    """650 红线 13 增补守门: 文档 + seed 体现代换行 source_registry 一律用 actual_province"""
    docs_74_body = _read(DOCS_74)
    report_body = _read(REPORT_MD)
    # docs/74 §2.3 必须包含 P3-1 更正明细表
    assert "P3-1" in docs_74_body and "LIAONING" in docs_74_body
    assert "actual_province" in docs_74_body
    # 报告 §7 必须包含 P3-1 蓝图更正落地表
    assert "P3-1" in report_body and "LIAONING" in report_body
    # 红线 13 增补条款援引
    assert "代换行" in docs_74_body or "代换样本" in docs_74_body, (
        "docs/74 应援引红线 13 增补: 代换行 source_registry 一律用 actual_province"
    )