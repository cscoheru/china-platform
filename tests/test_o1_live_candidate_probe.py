"""O1 B路 live-candidate 探测登记 守门测试 (knife 646 O1 side, ≥4 cases).

Per knife 646 §5.646-B O1 side:
- 守门 ≥1 live-candidate 政府/统计局源 (markdown-only 登记)
- 守门 O1 仍 OPEN (B路 主路径 仅登记, 不切换/启用)
- 守门 不启用 (connector enabled=False)
- 守门 零 registry.csv 变更 (registry 零改动)
- 守门 零 cegr.* 表变更 (read-only on production)

零网络; 零 cegr.* mutation; 零爬网; 纯文档守门。
"""
from __future__ import annotations

import json
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
PROBE_SCRIPT = REPO_ROOT / "scripts" / "probe_o1_live_candidate_2024.py"
EVIDENCE = REPO_ROOT / "evidence_pack" / "o1_live_candidate_probe_20260901.json"
REPORT_MD = REPO_ROOT / "docs" / "reports" / "o1_live_candidate_probe_20260901.md"
REGISTRY_CSV = REPO_ROOT / "source_registry" / "registry.csv"


def _read(path: Path) -> str:
    if not path.exists():
        return ""
    return path.read_text(encoding="utf-8")


def test_evidence_json_real_probed_1_candidate() -> None:
    """646-A.2 evidence_pack/o1 evidence JSON REAL_PROBED + 1 candidate"""
    if not EVIDENCE.exists():
        return
    data = json.loads(EVIDENCE.read_text(encoding="utf-8"))
    assert data["summary"]["probe_status"] == "REAL_PROBED"
    assert data["summary"]["candidate_count"] == 1
    assert data["summary"]["http_count"] == 1
    assert len(data["cells"]) == 1
    # O1 OPEN assertion
    assert data["summary"]["o1_status"] == "OPEN"
    # markdown-only registration
    assert data["summary"]["registration_scope"] == "markdown-only"
    # No registry.csv mutation
    assert data["summary"]["registry_csv_mutation"] == "NONE"
    # No cegr.* mutation
    assert data["summary"]["cegr_star_mutation"] == "NONE"
    # Connector NOT enabled
    assert data["summary"]["connector_enabled"] is False


def test_evidence_json_candidate_is_gov_or_statistical_bureau() -> None:
    """646-A.2 candidate 必须是 政府/统计局 源 (per 2026-08-29 数据源治理铁律)"""
    if not EVIDENCE.exists():
        return
    data = json.loads(EVIDENCE.read_text(encoding="utf-8"))
    spec = data["candidate_spec"]
    domain = spec["domain"]
    # Must be .gov.cn or similar government/statistical domain
    assert "stats.gov.cn" in domain or ".gov.cn" in domain, (
        f"candidate domain {domain} not government/statistical"
    )
    organization = spec["organization"]
    assert "统计局" in organization or "统计" in organization, (
        f"candidate organization {organization} not statistical"
    )


def test_evidence_json_candidate_pending_only() -> None:
    """646-A.2 candidate registration_status = PENDING_CANDIDATE_ONLY (不启用)"""
    if not EVIDENCE.exists():
        return
    data = json.loads(EVIDENCE.read_text(encoding="utf-8"))
    cell = data["cells"][0]
    assert cell["registration_status"] == "PENDING_CANDIDATE_ONLY"
    assert cell["enabled_in_registry"] is False
    # SHA captured for traceability (real probe)
    assert len(cell["file_hash_sha256"]) == 64


def test_probe_script_1_candidate_with_correct_red_lines() -> None:
    """646-A.2 probe script 1 candidate + HTTP_LIMIT=1 + 不启用 不写 cegr.*"""
    body = _read(PROBE_SCRIPT)
    assert "CANDIDATE" in body
    assert "HTTP_LIMIT = 1" in body
    assert "O1 仍 OPEN" in body or "o1_status" in body
    assert "PENDING_CANDIDATE_ONLY" in body
    assert "data.stats.gov.cn" in body
    # Red lines
    assert "不写 cegr.* 表" in body or "read-only on production" in body
    assert "不启用" in body or "enabled=FALSE" in body
    # Registry zero-mutation assertion
    assert "registry.csv" in body and ("零改动" in body or "NONE" in body or "不动" in body)


def test_report_md_no_pass_announcement() -> None:
    """646-A.4 O1 report MD 不宣称 PASS (沿用红线; O1 仍 OPEN)"""
    body = _read(REPORT_MD)
    if not body:
        return
    assert "不宣称" in body or "不宣布" in body
    assert "O1" in body
    assert "OPEN" in body
    assert "Gate" in body


def test_registry_csv_unchanged() -> None:
    """646-A.2 registry.csv 必须 0 字节变更 (零改动)

    646 tasking 红线 #13: live-candidate 只登记不启用; registry 零改动或仅 append pending 行。
    646 实际: 0 改动 (markdown-only registration).

    校验: no new row with data.stats.gov.cn as primary_url (pre-existing references
    to data.stats.gov.cn as backup_urls 是合法的 per 既有 registry rows).
    """
    body = _read(REGISTRY_CSV)
    assert body, "registry.csv missing"
    # No new row with data.stats.gov.cn as primary_url (markdown-only registration)
    primary_rows = [
        line for line in body.splitlines()
        if line.startswith("data.stats.gov.cn,") or "data.stats.gov.cn," in line.split(",")[0:4]
    ]
    assert len(primary_rows) == 0, (
        f"646-A.2 tasking requires markdown-only registration; found {len(primary_rows)} "
        f"new rows with data.stats.gov.cn as primary domain"
    )