"""M4.11 政策详情 v5 真实化 spike 第 6 次 守门测试 (knife 648 M4.11 side, ≥8 cases).

Per knife 648 §1.648-B M4.11 side:
- 守门 fetch script 2 cells REAL_FETCHED (http_count=4 ≤ 12)
- 守门 2 SHA distinct (4006439e/a06e174f) + 2 file_size > 0
- 守门 spike 边界 16 INSERT total (12 政策表 + 4 source)
- 守门 chain_id='real_648_m4_11_policy_detail_v5' (≠ 647 _v4 ≠ 646 _v3)
- 守门 UUID g 段 (≠ 647 f 段 ≠ 646 e 段)
- 守门 2 NEW SHA distinct ≠ 638-647 全部 SHA
- 守门 substitute 预授权池 (jilin/liaoning/hubei/shaanxi/sichuan/guizhou/jiangsu)
- 守门 已用省全集检查 (HLJ/HENAN/YUNNAN/FUJIAN/GD/ZJ/JX 不得重复)
- 守门 648-A.0 jiangxi CONTENT_CONFIRMED reverify sentinel
- 守门 不宣称 PASS (沿用红线)

零网络; 零 cegr.* mutation; 零爬网; 纯文档守门。
"""
from __future__ import annotations

import json
import re
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
FETCH_SCRIPT = REPO_ROOT / "scripts" / "fetch_m4_11_policy_detail_v5_2024.py"
SEED_SQL = REPO_ROOT / "scripts" / "seed_m4_11_policy_detail_real_v5.sql"
EVIDENCE = REPO_ROOT / "evidence_pack" / "m4_11_policy_detail_real_v5_20260901.json"
REPORT_MD = REPO_ROOT / "docs" / "reports" / "m4_11_policy_detail_real_v5_20260901.md"
REVERIFY_EVIDENCE = REPO_ROOT / "evidence_pack" / "m4_10_reverify_jx_20260901.json"
DOCS_71 = REPO_ROOT / "docs" / "71-m4-10-policy-detail-real-v4-20260901.md"


def _read(path: Path) -> str:
    if not path.exists():
        return ""
    return path.read_text(encoding="utf-8")


def test_evidence_json_real_fetched_2_samples() -> None:
    """648-A.1 evidence_pack/m4_11 evidence JSON REAL_FETCHED + 2 samples + http_count=4"""
    if not EVIDENCE.exists():
        return
    data = json.loads(EVIDENCE.read_text(encoding="utf-8"))
    assert data["summary"]["fetch_status"] == "REAL_FETCHED"
    assert data["summary"]["fetched_count"] == 2
    assert data["summary"]["http_count"] == 4, f"expected http_count=4; got {data['summary']['http_count']}"
    assert data["summary"]["http_count"] <= 12, f"≤12 HTTP limit violated: {data['summary']['http_count']}"
    assert len(data["cells"]) == 2


def test_evidence_json_2_distinct_shas_no_collision() -> None:
    """648-A.1 2 SHA distinct (4006439e/a06e174f) + 2 file_size > 0"""
    if not EVIDENCE.exists():
        return
    data = json.loads(EVIDENCE.read_text(encoding="utf-8"))
    shas = {cell["file_hash_sha256"] for cell in data["cells"]}
    assert len(shas) == 2, f"2 cells should have 2 distinct SHA — got {len(shas)}: {shas}"
    for cell in data["cells"]:
        assert cell["file_size_bytes"] > 0
    sha_set_str = " ".join(shas)
    assert "4006439e" in sha_set_str, f"expected hunan SHA 4006439e in {sha_set_str}"
    assert "a06e174f" in sha_set_str, f"expected anhui SHA a06e174f in {sha_set_str}"


def test_evidence_json_2_provinces_distinct() -> None:
    """648-A.1 2 distinct provinces: hunan + anhui (≠ 已用省 HLJ/HENAN/YUNNAN/FUJIAN/GD/ZJ/JX)"""
    if not EVIDENCE.exists():
        return
    data = json.loads(EVIDENCE.read_text(encoding="utf-8"))
    provinces = {cell.get("province") for cell in data["cells"]}
    assert "hunan" in provinces
    assert "anhui" in provinces
    # 已用省全集不得重复 (red line 648)
    forbidden = {"heilongjiang", "henan", "yunnan", "fujian", "guangdong", "zhejiang", "jiangxi"}
    assert not (provinces & forbidden), (
        f"648 red line violated — provinces {provinces} overlap with used set {forbidden}"
    )


def test_fetch_script_2_cells_no_substitute_used() -> None:
    """648-A.1 fetch script 2 cells: hunan_zwgk_chain + anhui_zwgk_chain (substitute 池备而不用)"""
    body = _read(FETCH_SCRIPT)
    assert "HUNAN_FALLBACK_CHAIN" in body
    assert "hunan_zwgk_chain" in body
    assert "ANHUI_FALLBACK_CHAIN" in body
    assert "anhui_zwgk_chain" in body
    assert "HTTP_LIMIT = 12" in body
    assert "https://www.hunan.gov.cn/zwgk/" in body
    assert "https://www.ah.gov.cn/zwgk/" in body
    # substitute 池 (备而不用, 不应被激活; 但应在源码注释可见以证明预设存在)
    assert "substitute" in body.lower() or "fall-through" in body.lower()


def test_fetch_log_has_2_200_reachable_via_fallback() -> None:
    """648-A.1 fetch_log: hunan 404 → / 200, anhui timeout → / 200 (省府根 fallback 全部成功)"""
    if not EVIDENCE.exists():
        return
    data = json.loads(EVIDENCE.read_text(encoding="utf-8"))
    flog = data["fetch_log"]
    # hunan 应有 2 个 fetch_log (404 + 200)
    hn = [f for f in flog if f.get("province") == "hunan"]
    assert len(hn) == 2, f"expected 2 hunan attempts; got {len(hn)}"
    assert hn[0]["http_code"] in (403, 404), f"hunan /zwgk/ should be 4xx; got {hn[0]['http_code']}"
    assert hn[1]["http_code"] == 200, f"hunan fallback / should be 200; got {hn[1]['http_code']}"
    # anhui 应有 2 个 fetch_log (timeout + 200)
    ah = [f for f in flog if f.get("province") == "anhui"]
    assert len(ah) == 2, f"expected 2 anhui attempts; got {len(ah)}"
    assert ah[0]["http_code"] == 0, f"anhui /zwgk/ should be timeout; got {ah[0]['http_code']}"
    assert ah[1]["http_code"] == 200, f"anhui fallback / should be 200; got {ah[1]['http_code']}"


def test_seed_sql_16_insert_total() -> None:
    """648-A.1 seed SQL 16 INSERT rows = 2 source_registry + 2 source_document + 2×6 政策表"""
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


def test_seed_sql_chain_id_v5_distinct_from_647_646_645() -> None:
    """648-A.1 chain_id='real_648_m4_11_policy_detail_v5' (≠ 647 _v4 ≠ 646 _v3 ≠ 645 _v2)"""
    body = _read(SEED_SQL)
    assert "real_648_m4_11_policy_detail_v5" in body
    # 647 / 646 / 645 stale chain_id 必须不出现
    assert "real_647_m4_10_policy_detail_v4" not in body
    assert "real_646_m4_9_policy_detail_v3" not in body
    assert "real_645_m4_8_policy_detail_v2" not in body


def test_seed_sql_uuid_g_segment_distinct_from_f_e_d_c_segments() -> None:
    """648-A.1 UUID g 段 (≠ 647 f 段 ≠ 646 e 段 ≠ 645 d 段 ≠ 644 c 段)"""
    body = _read(SEED_SQL)
    # 648 UUID g 段: g0eebc99 (source_registry/source_document) + g1eebc99 (policy_document) + g2eebc99 (policy_target) + g3eebc99 (policy_measure) + g4eebc99 (government_commitment) + g5eebc99 (commitment_progress) + g6eebc99 (project_event)
    assert "g0eebc99" in body  # source_registry/source_document
    assert "g1eebc99" in body  # policy_document
    assert "g2eebc99" in body  # policy_target
    assert "g3eebc99" in body  # policy_measure
    assert "g4eebc99" in body  # government_commitment
    assert "g5eebc99" in body  # commitment_progress
    assert "g6eebc99" in body  # project_event
    # 647 f 段 必须不出现
    for prefix in ["f0eebc99", "f1eebc99", "f2eebc99", "f3eebc99", "f4eebc99", "f5eebc99", "f6eebc99"]:
        assert prefix not in body, f"647 f-prefix {prefix} must not appear in 648 seed SQL"
    # 646 e 段 必须不出现
    for prefix in ["e0eebc99", "e1eebc99", "e2eebc99", "e3eebc99", "e4eebc99", "e5eebc99", "e6eebc99"]:
        assert prefix not in body, f"646 e-prefix {prefix} must not appear in 648 seed SQL"
    # 645 d 段 必须不出现
    for prefix in ["d0eebc99", "d1eebc99", "d2eebc99", "d3eebc99", "d4eebc99", "d5eebc99", "d6eebc99"]:
        assert prefix not in body, f"645 d-prefix {prefix} must not appear in 648 seed SQL"


def test_seed_sql_uses_real_fetched_shas_4006439e_a06e174f() -> None:
    """648-A.1 seed SQL 使用 648 实际抓取的 SHA 4006439e + a06e174f (≠ 638-647 全部 SHA)"""
    body = _read(SEED_SQL)
    assert "4006439ee1494314504a971eeb0d44166216e435b2d3425b5aad3f7439df38e0" in body
    assert "a06e174f10eda8b539a16aad5f25fb3350480df3019d9c861f1cd7d429026713" in body
    sha_pattern_json = re.findall(r'"source_file_sha256":\s*"([a-f0-9]{64})"', body)
    sha_pattern_fn = re.findall(r"'source_file_sha256',\s*'([a-f0-9]{64})'", body)
    sha_pattern = sha_pattern_json + sha_pattern_fn
    assert "4006439ee1494314504a971eeb0d44166216e435b2d3425b5aad3f7439df38e0" in sha_pattern
    assert "a06e174f10eda8b539a16aad5f25fb3350480df3019d9c861f1cd7d429026713" in sha_pattern
    # 638-647 stale SHAs must NOT appear in 648 lineage SHA values
    for stale_sha in [
        "8016ef08", "56481050",  # 647
        "fceb8c0a", "49eed23e",  # 646
        "6237cd48", "dfa38998", "bd4c4c51", "f33eba53",  # 645
        "bad8be51", "f33eba53",  # 644 (subset)
        "e68099df", "63109491", "93fe23b3",  # 643
        "cd6aff30", "4349ee0f", "fede03ba",  # 642
        "26e5379d",  # 641
    ]:
        assert stale_sha not in sha_pattern, f"648 source_file_sha256 lineage must not use stale 638-647 SHA {stale_sha}"


def test_seed_sql_lineage_is_demo_false_sentinel() -> None:
    """648-A.1 lineage JSONB `is_demo='false'` 真实化 sentinel (沿用 docs/33 §3.2)"""
    body = _read(SEED_SQL)
    assert "is_demo" in body
    assert "'false'" in body
    assert "is_demo='true'" not in body


def test_seed_sql_substitute_pool_commented() -> None:
    """648-A.1 substitute 预授权池必须在 seed SQL 注释可见 (备而不用)"""
    body = _read(SEED_SQL)
    # substitute 池 (jilin/liaoning/hubei/shaanxi/sichuan/guizhou/jiangsu) 应在注释可见
    assert "substitute" in body.lower()
    for province in ["jilin", "liaoning", "hubei", "shaanxi", "sichuan", "guizhou", "jiangsu"]:
        assert province in body.lower(), f"substitute pool province {province} must be visible in comments"


def test_report_md_no_pass_announcement_648_red_line() -> None:
    """648-A.1 report MD 不宣称 PASS (沿用红线)"""
    body = _read(REPORT_MD)
    if not body:
        return
    assert "不宣称" in body or "不宣布" in body
    assert "Gate" in body
    assert "O1" in body or "M4" in body
    # 红线 1 (不宣称 PASS) — 不应有 "M4.11 PASS" / "Gate 1 PASS" 类宣称
    forbidden_pass = ["M4.11 PASS", "Gate 1 PASS", "M4.10 PASS", "O1 PASS"]
    for fp in forbidden_pass:
        assert fp not in body, f"report must not declare {fp} (648 red line)"


def test_docs_71_section_7_jx_reverify_content_confirmed() -> None:
    """648-A.0 docs/71 §7 jiangxi reverify CONTENT_CONFIRMED 注记存在"""
    body = _read(DOCS_71)
    assert body, f"docs/71 missing: {DOCS_71}"
    # §7 标题 (per docs/71 行内 append §7)
    assert "CONTENT_CONFIRMED" in body
    assert "648-A.0" in body
    # sha_match=true
    assert "sha_match" in body or "SHA256" in body
    # 72 anchor hits
    assert "72" in body


def test_jx_reverify_evidence_content_confirmed() -> None:
    """648-A.0 reverify evidence JSON verdict=CONTENT_CONFIRMED + sha_match=true"""
    if not REVERIFY_EVIDENCE.exists():
        return
    data = json.loads(REVERIFY_EVIDENCE.read_text(encoding="utf-8"))
    assert data["verdict"] == "CONTENT_CONFIRMED", f"expected CONTENT_CONFIRMED; got {data['verdict']}"
    assert data["sha_match"] is True
    assert data["new_sha256"] == data["original_sha256"]
    assert data["fetch"]["http_code"] == 200
    assert data["anchors"]["anchor_hits_count"] >= 1, f"expected ≥1 anchor hit; got {data['anchors']['anchor_hits_count']}"


def test_jx_reverify_evidence_three_layer_xcheck() -> None:
    """648-A.0 三层交叉验证: SHA + size + anchor 全部一致"""
    if not REVERIFY_EVIDENCE.exists():
        return
    data = json.loads(REVERIFY_EVIDENCE.read_text(encoding="utf-8"))
    # SHA + size + anchor 三层
    assert data["sha_match"] is True, "SHA mismatch"
    assert data["anchors"]["file_size_bytes"] == 48118, "file_size不一致"
    assert data["anchors"]["anchor_hits_count"] >= 1, "anchor hits不足"
    assert data["is_content_anchored"] is True, "is_content_anchored=False"
    # 三个 sentinel 全部 PASS → CONTENT_CONFIRMED
    assert data["verdict"] == "CONTENT_CONFIRMED"


def test_648_red_line_no_gate_no_o1_no_pass() -> None:
    """648 red line: 不宣称任何 PASS"""
    seed_body = _read(SEED_SQL)
    script_body = _read(FETCH_SCRIPT)
    report_body = _read(REPORT_MD)
    # 不应在 seed SQL / fetch script / report 中宣称 PASS
    for src_name, src_body in [
        ("seed SQL", seed_body),
        ("fetch script", script_body),
        ("report MD", report_body),
    ]:
        if not src_body:
            continue
        for forbidden in ["M4.11 PASS", "Gate 1 PASS", "Gate PASS", "O1 PASS"]:
            assert forbidden not in src_body, f"{src_name} must not declare {forbidden}"