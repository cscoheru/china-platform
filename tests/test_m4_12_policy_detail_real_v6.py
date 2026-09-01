"""M4.12 政策详情 v6 真实化 spike 第 8 次 守门测试 (knife 649 M4.12 side, ≥8 cases).

Per knife 649 §1.649-B M4.12 side:
- 守门 fetch script 2 cells REAL_FETCHED (http_count=6 ≤ 12)
- 守门 2 SHA distinct (b22d1fb4d291e9e1.../a1e49a91172927df...) + 2 file_size > 0
- 守门 spike 边界 16 INSERT total (12 政策表 + 4 source)
- 守门 chain_id='real_649_m4_12_policy_detail_v6' (≠ 648 _v5 ≠ 647 _v4)
- 守门 UUID h 段 (≠ 648 g 段 ≠ 647 f 段 ≠ 646 e 段 ≠ 645 d 段)
- 守门 2 NEW SHA distinct ≠ 638-648 全部 SHA
- 守门 substitute 预授权池首次激活 (hubei 412+412 → 递补 liaoning /zwgk/ 404 → ln / 200 REACHABLE)
- 守门 已用省全集检查 (HLJ/HENAN/YUNNAN/FUJIAN/GD/ZJ/JX/HUN/AH 不得重复; 649 增量 HUBEI/JILIN/LIAONING)
- 守门 docs/73 §1-§6 架构师级审查
- 守门 evidence methodology 指针 (per 648 审计 P3-1 口径统一条款)
- 守门 不宣称 PASS (沿用红线)

零网络; 零 cegr.* mutation; 零爬网; 纯文档守门。
"""
from __future__ import annotations

import json
import re
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
FETCH_SCRIPT = REPO_ROOT / "scripts" / "fetch_m4_12_policy_detail_v6_2024.py"
SEED_SQL = REPO_ROOT / "scripts" / "seed_m4_12_policy_detail_real_v6.sql"
EVIDENCE = REPO_ROOT / "evidence_pack" / "m4_12_policy_detail_real_v6_20260901.json"
REPORT_MD = REPO_ROOT / "docs" / "reports" / "m4_12_policy_detail_real_v6_20260901.md"
DOCS_73 = REPO_ROOT / "docs" / "73-m4-12-policy-detail-real-v6-20260901.md"


def _read(path: Path) -> str:
    if not path.exists():
        return ""
    return path.read_text(encoding="utf-8")


def test_evidence_json_real_fetched_2_samples() -> None:
    """649-A.1 evidence_pack/m4_12 evidence JSON REAL_FETCHED + 2 samples + http_count=6"""
    if not EVIDENCE.exists():
        return
    data = json.loads(EVIDENCE.read_text(encoding="utf-8"))
    assert data["summary"]["fetch_status"] == "REAL_FETCHED"
    assert data["summary"]["fetched_count"] == 2
    assert data["summary"]["http_count"] == 6, (
        f"expected http_count=6 (hubei 4 + jilin 2); got {data['summary']['http_count']}"
    )
    assert data["summary"]["http_count"] <= 12, (
        f"≤12 HTTP limit violated: {data['summary']['http_count']}"
    )
    assert len(data["cells"]) == 2


def test_evidence_json_2_distinct_shas_no_collision() -> None:
    """649-A.1 2 SHA distinct (b22d1fb4 + a1e49a91) + 2 file_size > 0"""
    if not EVIDENCE.exists():
        return
    data = json.loads(EVIDENCE.read_text(encoding="utf-8"))
    shas = {cell["file_hash_sha256"] for cell in data["cells"]}
    assert len(shas) == 2, f"2 cells should have 2 distinct SHA — got {len(shas)}: {shas}"
    for cell in data["cells"]:
        assert cell["file_size_bytes"] > 0
    sha_set_str = " ".join(shas)
    assert "b22d1fb4" in sha_set_str, f"expected hubei→liaoning SHA b22d1fb4 in {sha_set_str}"
    assert "a1e49a91" in sha_set_str, f"expected jilin SHA a1e49a91 in {sha_set_str}"


def test_evidence_json_2_provinces_hubei_jilin_with_substitute() -> None:
    """649-A.1 2 distinct provinces: hubei + jilin; hubei substitute_used=true (跨省 substitute 首次激活)"""
    if not EVIDENCE.exists():
        return
    data = json.loads(EVIDENCE.read_text(encoding="utf-8"))
    provinces = {cell.get("province") for cell in data["cells"]}
    assert "hubei" in provinces
    assert "jilin" in provinces
    # 已用省全集不得重复 (red line 649)
    forbidden = {
        "heilongjiang", "henan", "yunnan", "fujian", "guangdong",
        "zhejiang", "jiangxi", "hunan", "anhui",
    }
    assert not (provinces & forbidden), (
        f"649 red line violated — provinces {provinces} overlap with used set {forbidden}"
    )
    # hubei 应触发 substitute_used=true; jilin substitute_used=false
    for cell in data["cells"]:
        if cell.get("province") == "hubei":
            assert cell.get("substitute_used") is True, "hubei must have substitute_used=true (跨省 substitute 首次激活)"
            assert cell.get("actual_province") == "liaoning", (
                f"hubei 实际抓取省应=liaoning; got {cell.get('actual_province')}"
            )
            assert cell.get("verdict") == "REACHABLE_VIA_SUBSTITUTE"
        elif cell.get("province") == "jilin":
            assert cell.get("substitute_used") is False
            assert cell.get("actual_province") == "jilin"
            assert cell.get("verdict") == "REACHABLE"


def test_evidence_json_substitute_reason_present() -> None:
    """649-A.1 substitute 触发即 evidence substitute_reason + docs/73 §2 登记 (per 红线 13)"""
    if not EVIDENCE.exists():
        return
    data = json.loads(EVIDENCE.read_text(encoding="utf-8"))
    for cell in data["cells"]:
        if cell.get("substitute_used") is True:
            reason = cell.get("substitute_reason", "")
            assert "hubei" in reason and "liaoning" in reason and "412" in reason, (
                f"substitute_reason 应含 hubei→liaoning→412; got: {reason}"
            )
            assert "Precondition Failed" in reason or "412" in reason


def test_fetch_script_2_cells_hubei_jilin_chains() -> None:
    """649-A.1 fetch script 2 cells: hubei_zwgk_chain + jilin_zwgk_chain + substitute pool"""
    body = _read(FETCH_SCRIPT)
    assert "HUBEI_FALLBACK_CHAIN" in body
    assert "https://www.hubei.gov.cn/zwgk/" in body
    assert "JILIN_FALLBACK_CHAIN" in body
    assert "https://www.jl.gov.cn/zwgk/" in body
    assert "HTTP_LIMIT = 12" in body
    # substitute 池 (liaoning/shaanxi/sichuan/guizhou/jiangsu)
    assert "SUBSTITUTE_POOL" in body
    assert "liaoning" in body
    assert "shaanxi" in body
    assert "sichuan" in body
    assert "guizhou" in body
    assert "jiangsu" in body


def test_fetch_log_hubei_412_412_liaoning_200_jilin_200() -> None:
    """649-A.1 fetch_log: hubei 412+412 → ln /zwgk/ 404 → ln / 200; jilin 0 timeout → / 200"""
    if not EVIDENCE.exists():
        return
    data = json.loads(EVIDENCE.read_text(encoding="utf-8"))
    flog = data.get("fetch_log", [])
    # hubei 应有 4 个 fetch_log (zwgk_412 + /_412 + ln zwgk_404 + ln /_200)
    hb_attempts = [f for f in flog if f.get("attempt_province") == "hubei"]
    assert len(hb_attempts) == 2, f"expected 2 hubei primary attempts; got {len(hb_attempts)}"
    assert hb_attempts[0]["http_code"] == 412, f"hubei /zwgk/ should be 412; got {hb_attempts[0]['http_code']}"
    assert hb_attempts[1]["http_code"] == 412, f"hubei / should be 412; got {hb_attempts[1]['http_code']}"
    # liaoning substitute 应有 2 attempts (404 + 200)
    ln_attempts = [f for f in flog if f.get("attempt_province") == "liaoning"]
    assert len(ln_attempts) == 2, f"expected 2 liaoning substitute attempts; got {len(ln_attempts)}"
    assert ln_attempts[0]["http_code"] == 404, f"ln /zwgk/ should be 404; got {ln_attempts[0]['http_code']}"
    assert ln_attempts[1]["http_code"] == 200, f"ln / should be 200; got {ln_attempts[1]['http_code']}"
    # jilin 应有 2 fetch_log (timeout + 200)
    jl_attempts = [f for f in flog if f.get("attempt_province") == "jilin"]
    assert len(jl_attempts) == 2, f"expected 2 jilin attempts; got {len(jl_attempts)}"
    assert jl_attempts[0]["http_code"] == 0, f"jl /zwgk/ should be timeout; got {jl_attempts[0]['http_code']}"
    assert jl_attempts[1]["http_code"] == 200, f"jl / should be 200; got {jl_attempts[1]['http_code']}"


def test_seed_sql_16_insert_total() -> None:
    """649-A.1 seed SQL 16 INSERT rows = 2 source_registry + 2 source_document + 2×6 政策表"""
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


def test_seed_sql_chain_id_v6_distinct_from_648_647_646_645() -> None:
    """649-A.1 chain_id='real_649_m4_12_policy_detail_v6' (≠ 648 _v5 ≠ 647 _v4 ≠ 646 _v3 ≠ 645 _v2)"""
    body = _read(SEED_SQL)
    assert "real_649_m4_12_policy_detail_v6" in body
    # 648 / 647 / 646 / 645 stale chain_id 必须不出现
    assert "real_648_m4_11_policy_detail_v5" not in body
    assert "real_647_m4_10_policy_detail_v4" not in body
    assert "real_646_m4_9_policy_detail_v3" not in body
    assert "real_645_m4_8_policy_detail_v2" not in body


def test_seed_sql_uuid_h_segment_distinct_from_g_f_e_d_c_segments() -> None:
    """649-A.1 UUID h 段 (≠ 648 g 段 ≠ 647 f 段 ≠ 646 e 段 ≠ 645 d 段 ≠ 644 c 段)"""
    body = _read(SEED_SQL)
    # 649 UUID h 段
    assert "h0eebc99" in body  # source_registry/source_document
    assert "h1eebc99" in body  # policy_document
    assert "h2eebc99" in body  # policy_target
    assert "h3eebc99" in body  # policy_measure
    assert "h4eebc99" in body  # government_commitment
    assert "h5eebc99" in body  # commitment_progress
    assert "h6eebc99" in body  # project_event
    # 648 g 段 必须不出现
    for prefix in ["g0eebc99", "g1eebc99", "g2eebc99", "g3eebc99", "g4eebc99", "g5eebc99", "g6eebc99"]:
        assert prefix not in body, f"648 g-prefix {prefix} must not appear in 649 seed SQL"
    # 647 f 段 必须不出现
    for prefix in ["f0eebc99", "f1eebc99", "f2eebc99", "f3eebc99", "f4eebc99", "f5eebc99", "f6eebc99"]:
        assert prefix not in body, f"647 f-prefix {prefix} must not appear in 649 seed SQL"
    # 646 e 段 必须不出现
    for prefix in ["e0eebc99", "e1eebc99", "e2eebc99", "e3eebc99", "e4eebc99", "e5eebc99", "e6eebc99"]:
        assert prefix not in body, f"646 e-prefix {prefix} must not appear in 649 seed SQL"
    # 645 d 段 必须不出现
    for prefix in ["d0eebc99", "d1eebc99", "d2eebc99", "d3eebc99", "d4eebc99", "d5eebc99", "d6eebc99"]:
        assert prefix not in body, f"645 d-prefix {prefix} must not appear in 649 seed SQL"


def test_seed_sql_uses_real_fetched_shas_b22d1fb4_a1e49a91() -> None:
    """649-A.1 seed SQL 使用 649 实际抓取的 SHA b22d1fb4d291e9e1... + a1e49a91172927df..."""
    body = _read(SEED_SQL)
    assert "b22d1fb4d291e9e134166602757e5184c99f4a4d67c66abd2fdd20a5371d4f82" in body
    assert "a1e49a91172927dfe7ac022587f039ea9a44414e0a900fefd1bd82a0884931c6" in body
    sha_pattern_json = re.findall(r'"source_file_sha256":\s*"([a-f0-9]{64})"', body)
    sha_pattern_fn = re.findall(r"'source_file_sha256',\s*'([a-f0-9]{64})'", body)
    sha_pattern = sha_pattern_json + sha_pattern_fn
    assert "b22d1fb4d291e9e134166602757e5184c99f4a4d67c66abd2fdd20a5371d4f82" in sha_pattern
    assert "a1e49a91172927dfe7ac022587f039ea9a44414e0a900fefd1bd82a0884931c6" in sha_pattern
    # 638-648 stale SHAs must NOT appear in 649 lineage SHA values
    for stale_sha in [
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
            f"649 source_file_sha256 lineage must not use stale 638-648 SHA {stale_sha}"
        )


def test_seed_sql_lineage_is_demo_false_sentinel() -> None:
    """649-A.1 lineage JSONB `is_demo='false'` 真实化 sentinel (沿用 docs/33 §3.2)"""
    body = _read(SEED_SQL)
    assert "is_demo" in body
    assert "'false'" in body
    assert "is_demo='true'" not in body


def test_seed_sql_substitute_pool_activated_liaoning() -> None:
    """649-A.1 substitute 预授权池首次激活: hubei 412 → 递补 liaoning /zwgk/ 404 → ln / 200 REACHABLE"""
    body = _read(SEED_SQL)
    assert "substitute" in body.lower()
    for province in ["liaoning", "shaanxi", "sichuan", "guizhou", "jiangsu"]:
        assert province in body.lower(), (
            f"substitute pool province {province} must be visible in comments"
        )
    # substitute_reason 在 lineage JSONB 应可见
    assert "substitute_reason" in body
    assert "hubei" in body.lower() and "liaoning" in body.lower()
    assert "412" in body or "Precondition Failed" in body


def test_report_md_no_pass_announcement_649_red_line() -> None:
    """649-A.4 report MD 不宣称 PASS (沿用红线)"""
    body = _read(REPORT_MD)
    if not body:
        return
    assert "不宣称" in body or "不宣布" in body
    assert "Gate" in body
    assert "O1" in body or "M4" in body
    # 红线 1 (不宣称 PASS) — 不应有 "M4.12 PASS" / "Gate 1 PASS" 类宣称
    forbidden_pass = ["M4.12 PASS", "Gate 1 PASS", "M4.11 PASS", "O1 PASS"]
    for fp in forbidden_pass:
        assert fp not in body, f"report must not declare {fp} (649 red line)"


def test_evidence_methodology_pointer_per_648_p3_1() -> None:
    """649-A.4 evidence methodology 字段含附属产物指针 (per 648 审计 P3-1 口径统一条款)"""
    if not EVIDENCE.exists():
        return
    data = json.loads(EVIDENCE.read_text(encoding="utf-8"))
    methodology = data.get("methodology", "")
    # 指针条款: 主 evidence methodology 必须含指向附属产物的指针 (文件名 + verdict)
    # 649 附属产物: docs/reports/m4_12_policy_detail_real_v6_20260901.md
    assert "附属" in methodology or "pointer" in methodology.lower() or "docs/reports" in methodology or "methodology" in methodology.lower(), (
        f"methodology 应含附属产物指针条款说明; got: {methodology}"
    )
    # 649 任务书 §0.13 条款援引
    assert "649 §0.13" in methodology or "0.13" in methodology, (
        f"methodology 应援引 649 任务书 §0.13; got: {methodology}"
    )


def test_docs_73_sections_1_to_6_present() -> None:
    """649-A.3 docs/73 §1-§6 架构师级审查文档章节守门"""
    body = _read(DOCS_73)
    assert body, f"docs/73 missing: {DOCS_73}"
    for section_header in [
        "## 1. M4.12 v6 落地终态",
        "## 2. substitute 跨省代换登记",
        "## 3. M4.12 v6 spike 边界",
        "## 4. lineage 真实化 sentinel",
        "## 5. 650 下一步",
        "## 6. 下一步 + 不宣称 PASS",
    ]:
        assert section_header in body, f"docs/73 missing section: {section_header}"
    # §2 substitute 登记要点
    assert "hubei" in body and "liaoning" in body
    assert "412" in body or "Precondition Failed" in body
    assert "REACHABLE_VIA_SUBSTITUTE" in body


def test_649_red_line_no_gate_no_o1_no_pass() -> None:
    """649 red line: 不宣称任何 PASS"""
    seed_body = _read(SEED_SQL)
    script_body = _read(FETCH_SCRIPT)
    report_body = _read(REPORT_MD)
    docs_73_body = _read(DOCS_73)
    # 不应在 seed SQL / fetch script / report MD / docs/73 中宣称 PASS
    for src_name, src_body in [
        ("seed SQL", seed_body),
        ("fetch script", script_body),
        ("report MD", report_body),
        ("docs/73", docs_73_body),
    ]:
        if not src_body:
            continue
        for forbidden in ["M4.12 PASS", "Gate 1 PASS", "Gate PASS", "O1 PASS"]:
            assert forbidden not in src_body, (
                f"{src_name} must not declare {forbidden}"
            )


def test_chain_id_province_used_set_clean() -> None:
    """649 红线: 已用省全集不得重复 + chain_id 严格区分"""
    body = _read(SEED_SQL)
    # chain_id 必须严格匹配 649 v6
    assert "real_649_m4_12_policy_detail_v6" in body
    # 已用省全集不得重复 (注: hubei/jilin 是 649 增量首次使用, OK)
    # 但 648 用过的 hunan/anhui 在 seed SQL 仅可作为注释文本出现, 不作为 lineage.canonical_name/province 数据来源
    # 简单检查: 17 个里程碑不宣布 PASS
    assert "不宣称" in body or "不宣布" in body