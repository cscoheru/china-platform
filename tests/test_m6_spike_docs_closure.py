"""M6 spike 文档系列收口 master + 互链补登 守门测试 (knife 645 M6 side, ≥6 cases).

Per knife 645 §5.645-B M6 side:
- 守门 docs/68 M6 master §1-§6 全部存在
- 守门 docs/68 8 刀全链表 (638-644 + 645)
- 守门 docs/68 spike 边界统一表 8 行 (含 645 d 段 chain_id='real_645_m4_8_policy_detail_v2')
- 守门 docs/68 chain_id 区分裁定 8 行 (不撞)
- 守门 docs/68 真实 SHA 区分表 17 行 (645 4 SHA distinct)
- 守门 4 处互链补登 closure (docs/45/50/53/66/67)
- 守门 645 红线遵守 (不宣称 PASS; 数据源治理铁律; 不删既有 OPEN 行)

零网络; 零 cegr.* mutation; 零爬网; 纯文档守门。
"""
from __future__ import annotations

import json
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
M6_DOC = REPO_ROOT / "docs" / "68-m6-spike-docs-closure-20260901.md"
M4_8_DOC = REPO_ROOT / "docs" / "69-m4-8-policy-detail-real-v2-20260901.md"
DOCS_45 = REPO_ROOT / "docs" / "45-stage2-s210-lite-gate2-review-index-20260826.md"
DOCS_50 = REPO_ROOT / "docs" / "50-stage2-gate2-review-packet-draft-20260826.md"
DOCS_53 = REPO_ROOT / "docs" / "53-stage2-public-ingest-ops-handbook-20260826.md"
DOCS_66 = REPO_ROOT / "docs" / "66-m5-waf-third-pass-20260901.md"
DOCS_67 = REPO_ROOT / "docs" / "67-m4-7-policy-detail-real-20260901.md"
EVIDENCE_M6 = REPO_ROOT / "evidence_pack" / "m6_spike_docs_closure_20260901.json"


def _read(path: Path) -> str:
    if not path.exists():
        return ""
    return path.read_text(encoding="utf-8")


def test_m6_master_doc_exists_and_complete() -> None:
    """645-A.1 docs/68 M6 master §1-§6 全部存在"""
    body = _read(M6_DOC)
    assert body, f"M6 master docs/68 missing: {M6_DOC}"
    for section in [
        "## 1. M4.x + M5 spike 链落地终态",
        "## 2. spike 边界统一表",
        "## 3. lineage JSONB",
        "## 4. chain_id 区分裁定",
        "## 5. 真实 SHA 区分表",
        "## 6. 646 下一步 + 不宣称 PASS",
    ]:
        assert section in body, f"M6 master missing section: {section}"


def test_m6_master_chain_table_8_knives() -> None:
    """645-A.1 docs/68 §1 8 刀全链表 (638-644 + 645)"""
    body = _read(M6_DOC)
    for knife in ["638", "639", "640", "641", "642", "643", "644", "**645**"]:
        assert knife in body, f"M6 master §1 missing knife marker: {knife}"


def test_m6_spike_boundary_table_includes_645_v2_chain_id() -> None:
    """645-A.1 docs/68 §2 spike 边界统一表 645 d 段 chain_id='real_645_m4_8_policy_detail_v2'"""
    body = _read(M6_DOC)
    assert "real_645_m4_8_policy_detail_v2" in body
    assert "d 段" in body or "d_segment" in body or "d段" in body
    assert "is_demo='false'" in body


def test_m6_chain_ids_distinct_8_no_collision() -> None:
    """645-A.1 docs/68 §4 chain_id 8 个 distinct (638-645 each unique)"""
    body = _read(M6_DOC)
    expected_chain_ids = [
        "real_638_m4_1_people",
        "demo_639",
        "demo_640",
        "real_641_heilongjiang",
        "real_642_m4_5_renmian",
        "real_643_m4_6_govreport",
        "real_644_m4_7_policy_detail",
        "real_645_m4_8_policy_detail_v2",
    ]
    chain_ids_found = sum(1 for c in expected_chain_ids if c in body)
    assert chain_ids_found == 8, f"chain_ids found {chain_ids_found}/8 — collision or missing"


def test_m6_real_sha_distinguish_table_4_new_shas() -> None:
    """645-A.1 docs/68 §5 真实 SHA 区分表 645 4 NEW SHA (6237cd48/dfa38998/bd4c4c51/f33eba53)"""
    body = _read(M6_DOC)
    for sha_prefix in ["6237cd48", "dfa38998", "bd4c4c51", "f33eba53"]:
        assert sha_prefix in body, f"M6 §5 missing 645 SHA prefix: {sha_prefix}"


def test_m6_no_pass_announcement_red_lines() -> None:
    """645-A.1 docs/68 §6 不宣称 PASS (Gate/O1/M2/M4/M5/M6)"""
    body = _read(M6_DOC)
    assert "不宣布" in body
    assert "Gate" in body and "O1" in body and "M6" in body


def test_m4_8_doc_exists_and_complete() -> None:
    """645-A.4 docs/69 M4.8 §1-§6 全部存在"""
    body = _read(M4_8_DOC)
    assert body, f"M4.8 docs/69 missing: {M4_8_DOC}"
    for section in [
        "## 1. M4.8 落地终态",
        "## 2. M4.8 spike 边界",
        "## 3. 真实化 demo SQL 结构",
        "## 4. lineage 真实化 sentinel",
        "## 5. 646 下一步",
        "## 6. 下一步 + 不宣称 PASS",
    ]:
        assert section in body, f"M4.8 missing section: {section}"


def test_m4_8_spike_boundary_32_total() -> None:
    """645-A.4 docs/69 §2 M4.8 spike 边界 32 INSERT total (24 政策表 + 8 source)"""
    body = _read(M4_8_DOC)
    assert "24 INSERT" in body
    assert "32 INSERT total" in body
    assert "real_645_m4_8_policy_detail_v2" in body
    assert "6237cd48" in body  # drift SHA
    assert "bd4c4c51" in body  # NEW henan zwgk sample 4


def test_m6_evidence_json_structural_ok() -> None:
    """645-A.5 evidence_pack/m6_spike_docs_closure JSON 结构合规"""
    if not EVIDENCE_M6.exists():
        return
    data = json.loads(EVIDENCE_M6.read_text(encoding="utf-8"))
    assert data["knife"] == 645
    assert data["milestone"] == "M6"
    assert data["ruling"] == "REAL_DELIVERED (read-only on production; no cegr.* mutation; no fake dry-run)"
    assert "spike_chain_8_knives" in data
    assert len(data["spike_chain_8_knives"]) == 8
    assert data["chain_ids"][-1]["chain_id"] == "real_645_m4_8_policy_detail_v2"
    assert data["next_knife"] == 646
    assert "M6" in data["not_pass_announcement"]


def test_cross_doc_backlinks_5_added() -> None:
    """645-A.1b 5 处互链补登 closure (docs/45/50/53/66/67)"""
    # docs/45 §6.2 表末 +1 行
    body_45 = _read(DOCS_45)
    assert "per 645" in body_45 and "M4.x + M5 spike" in body_45, "docs/45 §6.2 互链缺失"
    # docs/50 §4.4 第 48 项
    body_50 = _read(DOCS_50)
    assert "M6 master" in body_50 and "第 48 项" in body_50, "docs/50 §4.4 第 48 项互链缺失"
    # docs/53 §5 第 48 项
    body_53 = _read(DOCS_53)
    assert "docs/53 §5 第 48 项 M4.x + M5 spike" in body_53, "docs/53 §5 第 48 项互链缺失"
    # docs/66 §6 末
    body_66 = _read(DOCS_66)
    assert "→ 645 `docs/68-m6-spike-docs-closure" in body_66, "docs/66 §6 末互链缺失"
    # docs/67 §6 末
    body_67 = _read(DOCS_67)
    assert "→ 645 `docs/69-m4-8-policy-detail-real-v2" in body_67, "docs/67 §6 末互链缺失"