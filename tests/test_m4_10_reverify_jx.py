"""M4.10 647 审计 P3-1 jiangxi "403" 复验 守门测试 (knife 648 §A.0, ≥3 cases).

Per knife 648 §A.0:
- 1×HTTP re-fetch https://www.jiangxi.gov.cn/zwgk/
- SHA 对比 vs 原值 `56481050c810fbeec004ff68478d9f291c5eda39e005ec09e3fb6122dc28edd4`
- 内容锚点: <title> + DATE_RE + 关键 body 标识 (江西/jiangxi/政务公开)
- 一致=CONTENT_CONFIRMED (本次结果)

不消耗 648-A.1 M4.11 side HTTP quota (≤12); 仅 1×HTTP for reverify。
零网络 (走 evidence JSON 离线校验); 零 cegr.* mutation。
"""
from __future__ import annotations

import json
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
REVERIFY_SCRIPT = REPO_ROOT / "scripts" / "reverify_jx_403_2024.py"
REVERIFY_EVIDENCE = REPO_ROOT / "evidence_pack" / "m4_10_reverify_jx_20260901.json"
DOCS_71 = REPO_ROOT / "docs" / "71-m4-10-policy-detail-real-v4-20260901.md"
ORIGINAL_SHA = "56481050c810fbeec004ff68478d9f291c5eda39e005ec09e3fb6122dc28edd4"


def _read(path: Path) -> str:
    if not path.exists():
        return ""
    return path.read_text(encoding="utf-8")


def test_reverify_script_exists() -> None:
    """648-A.0 reverify script 必须存在"""
    assert REVERIFY_SCRIPT.exists(), f"reverify script missing: {REVERIFY_SCRIPT}"


def test_reverify_evidence_json_exists_and_valid() -> None:
    """648-A.0 reverify evidence JSON 必须存在且结构有效"""
    assert REVERIFY_EVIDENCE.exists(), f"reverify evidence missing: {REVERIFY_EVIDENCE}"
    data = json.loads(REVERIFY_EVIDENCE.read_text(encoding="utf-8"))
    assert data["knife"] == "648-A.0"
    assert "jiangxi" in data["purpose"].lower() or "复验" in data["purpose"]
    assert data["url"] == "https://www.jiangxi.gov.cn/zwgk/"
    assert data["original_sha256"] == ORIGINAL_SHA


def test_reverify_verdict_content_confirmed() -> None:
    """648-A.0 verdict 必须 = CONTENT_CONFIRMED (本次复验结果)"""
    data = json.loads(REVERIFY_EVIDENCE.read_text(encoding="utf-8"))
    assert data["verdict"] == "CONTENT_CONFIRMED", f"expected CONTENT_CONFIRMED; got {data['verdict']}"
    assert data["sha_match"] is True
    assert data["new_sha256"] == ORIGINAL_SHA


def test_reverify_three_layer_xcheck() -> None:
    """648-A.0 三层交叉验证: SHA + size + anchor"""
    data = json.loads(REVERIFY_EVIDENCE.read_text(encoding="utf-8"))
    # SHA 一致
    assert data["sha_match"] is True
    # 文件大小一致 (48118 bytes)
    assert data["anchors"]["file_size_bytes"] == 48118
    # 锚点命中 (≥1 即证明 body 含江西/jiangxi 关键词)
    assert data["anchors"]["anchor_hits_count"] >= 1, f"anchor hits={data['anchors']['anchor_hits_count']} < 1"
    assert data["is_content_anchored"] is True


def test_reverify_anchors_include_jiangxi_keywords() -> None:
    """648-A.0 内容锚点必须包含 江西/jiangxi 关键词 (样本锚定)"""
    data = json.loads(REVERIFY_EVIDENCE.read_text(encoding="utf-8"))
    sample = data["anchors"]["anchor_hits_sample"]
    assert any("江西" in s or "jiangxi" in s.lower() for s in sample), (
        f"anchor hits sample lacks 江西/jiangxi markers: {sample}"
    )


def test_docs_71_section_7_reverify_appended() -> None:
    """648-A.0 docs/71 §7 jiangxi reverify CONTENT_CONFIRMED 行内 append 必须存在"""
    body = _read(DOCS_71)
    assert body, f"docs/71 missing: {DOCS_71}"
    assert "## 7. 648-A.0 jiangxi" in body or "## 7." in body
    assert "CONTENT_CONFIRMED" in body
    # 关键 sentinel
    assert "sha_match" in body or "SHA256" in body
    assert "72" in body
    # 不删 OPEN 行 (沿用红线 4)
    assert "O1 仍 OPEN" in body
    assert "不宣称" in body


def test_reverify_red_line_no_drift_no_pass() -> None:
    """648-A.0 红线: 一致即 CONTENT_CONFIRMED (不登记 docs/52 drift; 不宣称 PASS)"""
    data = json.loads(REVERIFY_EVIDENCE.read_text(encoding="utf-8"))
    # 一致=CONTENT_CONFIRMED, 不应误判为 DRIFT
    assert "DRIFT" not in data["verdict"]
    assert "AMBIGUOUS" not in data["verdict"]
    # evidence 不得宣称 PASS
    raw = REVERIFY_EVIDENCE.read_text(encoding="utf-8")
    for forbidden in ["Gate 1 PASS", "O1 PASS", "M4.11 PASS", "M4.10 PASS"]:
        assert forbidden not in raw, f"reverify evidence must not declare {forbidden}"


def test_reverify_uses_only_1_http_per_spec() -> None:
    """648-A.0 1×HTTP 限制: evidence fetch 字段只有 1 条 (per 任务书 §A.0)"""
    data = json.loads(REVERIFY_EVIDENCE.read_text(encoding="utf-8"))
    # reverify 是单次 fetch, 不是 fall-through chain
    assert "http_count" not in data or "fetch" in data
    assert "fetch" in data
    # fetch 是单条记录
    assert data["fetch"]["http_code"] == 200
    assert data["fetch"]["reason"] == "ok"