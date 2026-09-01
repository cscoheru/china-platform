"""M4.10 政策详情 v4 真实化 spike 第 5 次 守门测试 (knife 647 M4.10 side, ≥10 cases).

Per knife 647 §1.647-B M4.10 side:
- 守门 fetch script 2 cells REAL_FETCHED (http_count=7 ≤ 12)
- 守门 2 SHA distinct (8016ef08/56481050) + 2 file_size > 0
- 守门 spike 边界 16 INSERT total (12 政策表 + 4 source)
- 守门 chain_id='real_647_m4_10_policy_detail_v4' (≠ 646 _v3 ≠ 645 _v2)
- 守门 UUID f 段 (≠ 646 e 段 ≠ 645 d 段 ≠ 644 c 段)
- 守门 2 NEW SHA distinct ≠ 638-646 全部 SHA
- 守门 646 审计 P2-1 F7 补登记 (docs/70 §4 表尾 尾注)
- 守门 646 审计 P3-2 措辞更正 (docs/70 §6 行内 尾注)
- 守门 625 fall-through substitute: shandong BLOCKED → jiangxi
- 守门 不宣称 PASS (沿用红线)

零网络; 零 cegr.* mutation; 零爬网; 纯文档守门。
"""
from __future__ import annotations

import json
import re
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
FETCH_SCRIPT = REPO_ROOT / "scripts" / "fetch_m4_10_policy_detail_v4_2024.py"
SEED_SQL = REPO_ROOT / "scripts" / "seed_m4_10_policy_detail_real_v4.sql"
EVIDENCE = REPO_ROOT / "evidence_pack" / "m4_10_policy_detail_real_v4_20260901.json"
REPORT_MD = REPO_ROOT / "docs" / "reports" / "m4_10_policy_detail_real_v4_20260901.md"
DOCS_70 = REPO_ROOT / "docs" / "70-m4-9-policy-detail-real-v3-20260901.md"
DOCS_71 = REPO_ROOT / "docs" / "71-m4-10-policy-detail-real-v4-20260901.md"


def _read(path: Path) -> str:
    if not path.exists():
        return ""
    return path.read_text(encoding="utf-8")


def test_evidence_json_real_fetched_2_samples() -> None:
    """647-A.1 evidence_pack/m4_10 evidence JSON REAL_FETCHED + 2 samples + http_count=7"""
    if not EVIDENCE.exists():
        return
    data = json.loads(EVIDENCE.read_text(encoding="utf-8"))
    assert data["summary"]["fetch_status"] == "REAL_FETCHED"
    assert data["summary"]["fetched_count"] == 2
    assert data["summary"]["http_count"] == 7, f"expected http_count=7; got {data['summary']['http_count']}"
    assert data["summary"]["http_count"] <= 12, f"≤12 HTTP limit violated: {data['summary']['http_count']}"
    assert len(data["cells"]) == 2


def test_evidence_json_2_distinct_shas_no_collision() -> None:
    """647-A.1 2 SHA distinct (8016ef08/56481050) + 2 file_size > 0"""
    if not EVIDENCE.exists():
        return
    data = json.loads(EVIDENCE.read_text(encoding="utf-8"))
    shas = {cell["file_hash_sha256"] for cell in data["cells"]}
    assert len(shas) == 2, f"2 cells should have 2 distinct SHA — got {len(shas)}: {shas}"
    for cell in data["cells"]:
        assert cell["file_size_bytes"] > 0
    sha_set_str = " ".join(shas)
    assert "8016ef08" in sha_set_str, f"expected zhejiang SHA 8016ef08 in {sha_set_str}"
    assert "56481050" in sha_set_str, f"expected jiangxi SHA 56481050 in {sha_set_str}"


def test_evidence_json_shandong_blocked_625_substitute() -> None:
    """647-A.1 625 fall-through substitute: shandong BLOCKED 4 attempts → jiangxi 替代"""
    if not EVIDENCE.exists():
        return
    data = json.loads(EVIDENCE.read_text(encoding="utf-8"))
    fetch_log = data["fetch_log"]
    # shandong 4 attempts BLOCKED 必须在 fetch_log 可见
    shandong_attempts = [fl for fl in fetch_log if fl.get("province") == "shandong"]
    assert len(shandong_attempts) == 4, f"expected 4 shandong BLOCKED attempts; got {len(shandong_attempts)}"
    # HTTPS TLS handshake_failure 至少 2 次 (zwgk + 省府根)
    tls_failures = [fl for fl in shandong_attempts if "sslv3 alert" in fl.get("reason", "") or "SSL routines" in fl.get("reason", "")]
    assert len(tls_failures) >= 2, f"expected ≥2 TLS handshake_failure; got {len(tls_failures)}"
    # HTTP 404 + timeout 至少 1 次
    http_failures = [fl for fl in shandong_attempts if fl.get("http_code") in (0, 404) or "timeout" in fl.get("reason", "")]
    assert len(http_failures) >= 2, f"expected ≥2 HTTP 404/timeout; got {len(http_failures)}"
    # jiangxi substitute 必须在 fetch_log 可见
    jiangxi_attempts = [fl for fl in fetch_log if fl.get("province") == "jiangxi"]
    assert len(jiangxi_attempts) >= 1, f"expected ≥1 jiangxi attempt; got {len(jiangxi_attempts)}"
    # jiangxi cell 必须是 shandong_zwgk_chain_substitute slot
    jx_cell = next((c for c in data["cells"] if c.get("province") == "jiangxi"), None)
    assert jx_cell is not None
    assert jx_cell["slot"] == "shandong_zwgk_chain_substitute"
    assert jx_cell.get("original_province") == "shandong"
    assert "625" in jx_cell.get("substitute_reason", "")


def test_fetch_script_2_cells_with_625_substitute() -> None:
    """647-A.1 fetch script 2 cells 含 zhejiang_zwgk_chain + shandong_zwgk_chain + JIANGXI_FALLBACK_CHAIN substitute"""
    body = _read(FETCH_SCRIPT)
    assert "ZHEJIANG_FALLBACK_CHAIN" in body
    assert "zhejiang_zwgk_chain" in body
    assert "SHANDONG_FALLBACK_CHAIN" in body
    assert "JIANGXI_FALLBACK_CHAIN" in body
    assert "fallthrough_substitute" in body
    assert "shandong_blocked_substitute" in body
    assert "HTTP_LIMIT = 12" in body
    assert "https://www.zj.gov.cn/zwgk/" in body
    assert "https://www.shandong.gov.cn/zwgk/" in body
    assert "https://www.jiangxi.gov.cn/zwgk/" in body


def test_seed_sql_16_insert_total() -> None:
    """647-A.1 seed SQL 16 INSERT rows = 2 source_registry + 2 source_document + 2×6 政策表"""
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
    # 16 lineage source_file_sha256 rows total = 2 source_registry + 2 source_document + 2 policy_document + 2 policy_target + 2 policy_measure + 2 government_commitment + 2 commitment_progress + 2 project_event
    # seed SQL uses two forms: JSON literal `"source_file_sha256": "..."` and jsonb_build_object comma form `'source_file_sha256', '...'`
    sha_rows_json = re.findall(r'"source_file_sha256":\s*"([a-f0-9]{64})"', body)
    sha_rows_fn = re.findall(r"'source_file_sha256',\s*'([a-f0-9]{64})'", body)
    total_sha_rows = len(sha_rows_json) + len(sha_rows_fn)
    assert total_sha_rows == 16, f"expected 16 lineage source_file_sha256 rows total (JSON + jsonb_build_object); got {total_sha_rows} ({len(sha_rows_json)} JSON + {len(sha_rows_fn)} jsonb_build_object)"
    # INSERT statements 8-16 范围 (10 典型)
    insert_stmts = re.findall(r"INSERT INTO \w+", body)
    assert 8 <= len(insert_stmts) <= 16, f"expected 8-16 INSERT statements; got {len(insert_stmts)}"


def test_seed_sql_chain_id_v4_distinct_from_646_645_644() -> None:
    """647-A.1 chain_id='real_647_m4_10_policy_detail_v4' (≠ 646 _v3 ≠ 645 _v2 ≠ 644 _policy_detail)"""
    body = _read(SEED_SQL)
    assert "real_647_m4_10_policy_detail_v4" in body
    # 646 / 645 / 644 stale chain_id 必须不出现
    assert "real_646_m4_9_policy_detail_v3" not in body
    assert "real_645_m4_8_policy_detail_v2" not in body
    assert "real_644_m4_7_policy_detail" not in body


def test_seed_sql_lineage_is_demo_false_sentinel() -> None:
    """647-A.1 lineage JSONB `is_demo='false'` 真实化 sentinel (沿用 docs/33 §3.2)"""
    body = _read(SEED_SQL)
    assert "is_demo" in body
    assert "'false'" in body
    assert "is_demo='true'" not in body


def test_seed_sql_uuid_f_segment_distinct_from_e_d_c_segments() -> None:
    """647-A.1 UUID f 段 (≠ 646 e 段 ≠ 645 d 段 ≠ 644 c 段)"""
    body = _read(SEED_SQL)
    # 647 UUID f 段: f0eebc99 (source_registry/source_document) + f1eebc99 (policy_document) + f2eebc99 (policy_target) + f3eebc99 (policy_measure) + f4eebc99 (government_commitment) + f5eebc99 (commitment_progress) + f6eebc99 (project_event)
    assert "f0eebc99" in body  # source_registry/source_document
    assert "f1eebc99" in body  # policy_document
    assert "f2eebc99" in body  # policy_target
    assert "f3eebc99" in body  # policy_measure
    assert "f4eebc99" in body  # government_commitment
    assert "f5eebc99" in body  # commitment_progress
    assert "f6eebc99" in body  # project_event
    # 646 e 段 必须不出现
    assert "e0eebc99" not in body
    assert "e1eebc99" not in body
    assert "e2eebc99" not in body
    assert "e3eebc99" not in body
    assert "e4eebc99" not in body
    assert "e5eebc99" not in body
    assert "e6eebc99" not in body
    # 645 d 段 必须不出现
    assert "d0eebc99" not in body
    assert "d1eebc99" not in body
    assert "d2eebc99" not in body
    assert "d3eebc99" not in body
    assert "d4eebc99" not in body
    assert "d5eebc99" not in body
    assert "d6eebc99" not in body
    # 644 c 段 必须不出现
    assert "c1eebc99" not in body
    assert "c2eebc99" not in body


def test_seed_sql_uses_real_fetched_shas_8016ef08_56481050() -> None:
    """647-A.1 seed SQL 使用 647 实际抓取的 SHA 8016ef08 + 56481050 (≠ 638-646 全部 SHA)"""
    body = _read(SEED_SQL)
    assert "8016ef0874c49261d39fc83f79b7ba04b6ce109b2bf85444cca473f27c58f8a8" in body
    assert "56481050c810fbeec004ff68478d9f291c5eda39e005ec09e3fb6122dc28edd4" in body
    sha_pattern_json = re.findall(r'"source_file_sha256":\s*"([a-f0-9]{64})"', body)
    sha_pattern_fn = re.findall(r"'source_file_sha256',\s*'([a-f0-9]{64})'", body)
    sha_pattern = sha_pattern_json + sha_pattern_fn
    assert "8016ef0874c49261d39fc83f79b7ba04b6ce109b2bf85444cca473f27c58f8a8" in sha_pattern
    assert "56481050c810fbeec004ff68478d9f291c5eda39e005ec09e3fb6122dc28edd4" in sha_pattern
    # 638-646 stale SHAs must NOT appear in 647 lineage SHA values
    for stale_sha in ["bad8be51", "6237cd48", "dfa38998", "bd4c4c51", "f33eba53",
                      "e68099df", "63109491", "93fe23b3",
                      "cd6aff30", "4349ee0f", "fede03ba",
                      "26e5379d",
                      "fceb8c0a", "49eed23e"]:
        assert stale_sha not in sha_pattern, f"647 source_file_sha256 lineage must not use stale 638-646 SHA {stale_sha}"


def test_report_md_no_pass_announcement_647_red_line() -> None:
    """647-A.4 report MD 不宣称 PASS (沿用红线)"""
    body = _read(REPORT_MD)
    if not body:
        return
    assert "不宣称" in body or "不宣布" in body
    assert "Gate" in body
    assert "O1" in body or "M4" in body
    # 625 substitute 必须在 §4 数据源合规 可见
    assert "jiangxi" in body or "江西" in body
    assert "625" in body or "substitute" in body.lower()


def test_docs_71_section_completeness() -> None:
    """647-A.3 docs/71 §1-§6 全部存在 + 不宣称 PASS"""
    body = _read(DOCS_71)
    assert body, f"M4.10 docs/71 missing: {DOCS_71}"
    for section in [
        "## 1. M4.10 落地终态",
        "## 2. M4.10 spike 边界",
        "## 3. 真实化 demo SQL 结构",
        "## 4. lineage 真实化 sentinel",
        "## 5. 648 下一步",
        "## 6. 下一步 + 不宣称 PASS",
    ]:
        assert section in body, f"M4.10 docs/71 missing section: {section}"
    # 647 关键 sentinel
    assert "real_647_m4_10_policy_detail_v4" in body
    assert "f 段" in body
    assert "8016ef08" in body or "56481050" in body
    assert "O1 仍 OPEN" in body
    assert "不宣布" in body or "不宣称" in body


def test_docs_70_p2_1_f7_postscript_647_a0() -> None:
    """647-A.0 docs/70 §4 表尾 P2-1 F7 补登记 尾注存在 (646 审计 P2-1 处置)

    docs/70 §4.2 真实 SHA 区分表 表尾 行内 append 尾注 (不删行不删 OPEN 行)
    关键 sentinel: "henan-zwgk publication_date" + "2026-08-20" + "2026-08-30"
    """
    body = _read(DOCS_70)
    assert body, f"docs/70 missing: {DOCS_70}"
    # 646 审计 P2-1 F7 补登记 关键词
    assert "F7" in body, "docs/70 P2-1 F7 尾注 must exist"
    assert "henan-zwgk" in body, "docs/70 P2-1 F7 尾注 must mention henan-zwgk"
    assert "2026-08-20" in body, "docs/70 P2-1 F7 尾注 must cite publication_date evidence 2026-08-20"
    assert "2026-08-30" in body, "docs/70 P2-1 F7 尾注 must cite publication_date seed 2026-08-30"
    # 元数据日期差异说明
    assert "10 天" in body or "日期差异" in body or "元数据" in body


def test_docs_70_p3_2_wording_correction_647_a0() -> None:
    """647-A.0 docs/70 §6 行内 P3-2 措辞更正 尾注存在 (646 审计 P3-2 处置)

    docs/70 §6 行内 append 尾注 (不删行不删 OPEN 行)
    关键 sentinel: "P3-2" + "笔误" + "evidence_pack/o1" + "docs/reports/o1"
    """
    body = _read(DOCS_70)
    assert body, f"docs/70 missing: {DOCS_70}"
    # 646 审计 P3-2 措辞更正 关键词
    assert "P3-2" in body, "docs/70 P3-2 尾注 must exist"
    assert "笔误" in body, "docs/70 P3-2 尾注 must explain wording correction"
    # 实际登记落点 (evidence_pack/o1 + docs/reports/o1)
    assert "evidence_pack/o1" in body or "o1_live_candidate_probe" in body, "docs/70 P3-2 尾注 must reference evidence_pack/o1落点"
    assert "docs/reports/o1" in body or "docs/reports/o1_live_candidate" in body, "docs/70 P3-2 尾注 must reference docs/reports/o1 落点"
    # docs/52 本体零改动合规说明
    assert "docs/52" in body
    assert "PENDING_CANDIDATE_ONLY" in body or "PENDING_CANDIDATE" in body


def test_docs_70_no_destructive_edit_preserves_open_lines() -> None:
    """647-A.0 docs/70 修正项一律行内 append 尾注 (不删行不删 OPEN 行) — 红线 4

    验证 docs/70 既有正文未丢失: §6 必须包含 "O1 仍 OPEN" + "不宣布" 终结不变
    """
    body = _read(DOCS_70)
    assert body
    # §6 既有关键不变量
    assert "O1 仍 OPEN" in body, "docs/70 §6 O1 仍 OPEN 不变量 must be preserved (不删行)"
    assert "不宣布" in body, "docs/70 不宣布 红线 must be preserved"
    assert "B路 live-candidate" in body or "live-candidate" in body
    # 647-A.0 修正项已落地 (行内 append 尾注, 不删行)
    assert "647-A.0" in body or "647 审计" in body or "646 审计" in body, "docs/70 must reference 647-A.0 落地"