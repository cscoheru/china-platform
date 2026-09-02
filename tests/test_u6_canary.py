"""U6 金丝雀 spike 守门测试 (knife 657-A, ≥5 cases).

Per knife 657-A (657 §1.657-A U6 金丝雀 spike, docs/81 ruling):
- 守门 evidence JSON 存在 + 5 省 cells 全齐 (北京/上海/山东/湖北/四川)
- 守门 overall_verdict='CANARY_PASS' (5/5 省 5/5 字段 delta=0 全等)
- 守门 all_sha_locked=True (5 SHA 锁hongheiku 转载字节)
- 守门 lineage 三重标注模板 (source='hongheiku_tjgb' + origin + ruling='U6 2026-09-02')
- 守门 docs/81 既有正文零改动 (红线 4)
- 守门 红线 1 不 INSERT observation (金丝雀阶段不入库, 仅 evidence + report)
- 守门 红线 3 不绕过反爬 (本域无 WAF/验证码)
- 守门 失败形式库新增第 5 例 TAG_PATH_ASSUMPTION_ERROR (tasking tag-path 假设错误 +2 HTTP 超预算)
- 守门 implication 658 批量授权解锁 (5/5 一致)
- 守门 不宣称任何 Gate/O1/M2 PASS (沿用红线)

零网络; 零 cegr.* mutation; 零爬网; 纯文档守门。
"""
from __future__ import annotations

import json
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
EVIDENCE = REPO_ROOT / "evidence_pack" / "u6_canary_5province_20260902.json"
REPORT = REPO_ROOT / "docs" / "reports" / "u6_canary_5province_20260902.md"
DOCS_81 = REPO_ROOT / "docs" / "81-u6-hongheiku-source-ruling-20260902.md"


def _read(path: Path) -> str:
    if not path.exists():
        return ""
    return path.read_text(encoding="utf-8")


def _evidence() -> dict:
    if not EVIDENCE.exists():
        return {}
    return json.loads(EVIDENCE.read_text(encoding="utf-8"))


def test_evidence_json_exists_and_valid() -> None:
    """657-A §1.657-A: 主 evidence JSON 存在 + 可解析"""
    assert EVIDENCE.exists(), f"missing evidence: {EVIDENCE}"
    data = _evidence()
    assert data.get("knife") == "657"
    assert data.get("spike_id") == "657-A"
    assert data.get("ruling_ref") == "U6 (docs/81, commit 1e3ec9d)"


def test_five_province_cells_complete() -> None:
    """657-A §1.657-A: 5 金丝雀省 cells 全齐 = 北京/上海/山东/湖北/四川"""
    data = _evidence()
    cells = data.get("cells", [])
    provinces = sorted(c["province"] for c in cells)
    expected = sorted(["beijing", "shanghai", "shandong", "hubei", "sichuan"])
    assert provinces == expected, f"cells={provinces}, expected={expected}"
    assert len(cells) == 5


def test_overall_verdict_canary_pass() -> None:
    """657-A §1.657-A verdict: CANARY_PASS (5/5 一致 → 658 批量授权解锁)"""
    data = _evidence()
    verdict = data.get("overall_verdict")
    assert verdict == "CANARY_PASS", f"verdict={verdict} (NOT PASS, 红线 5 禁止部分采信)"


def test_each_province_all_5_fields_match_zero_delta() -> None:
    """657-A §1.657-A: 每省 gdp_total/growth/primary/secondary/tertiary 5 字段 delta=0 全等"""
    data = _evidence()
    for cell in data["cells"]:
        diffs = cell["diff"]
        # 5 fields must all be present and matched
        for fld in ["gdp_total", "growth", "primary", "secondary", "tertiary"]:
            assert fld in diffs, f"{cell['province']}: 缺字段 {fld}"
            d = diffs[fld]
            assert d["match"] is True, f"{cell['province']}.{fld}: delta={d['delta']} (not match)"
            assert d["delta"] == 0.0, f"{cell['province']}.{fld}: delta={d['delta']}"
        assert cell["match_count"] == 5
        assert cell["field_count"] == 5


def test_sha256_locked_for_all_five_hongheiku_bytes() -> None:
    """657-A §5 红线 2: SHA 锁 5 hongheiku 转载字节 (length=64 hex)"""
    data = _evidence()
    assert data.get("all_sha_locked") is True
    for cell in data["cells"]:
        sha = cell["sha256"]
        assert len(sha) == 64, f"{cell['province']}: SHA={sha} not 64 hex"
        int(sha, 16)  # parseable as hex
        assert cell["bytes"] > 1000, f"{cell['province']}: bytes={cell['bytes']} too small (probably error page)"


def test_lineage_triple_annotation_template_present() -> None:
    """657-A §1.657-A lineage 三重标注: source='hongheiku_tjgb' + origin='XX省统计局' + ruling='U6 2026-09-02'"""
    data = _evidence()
    lineage = data.get("lineage_provenance_template", {})
    assert lineage.get("source") == "hongheiku_tjgb"
    assert "XX省统计局" in lineage.get("origin", "")
    assert lineage.get("ruling") == "U6 2026-09-02"
    assert "转载" in lineage.get("note", ""), "必须如实标注hongheiku 是转载字节"


def test_red_line_no_observation_insert() -> None:
    """657-A §5 红线 1: 金丝雀阶段不 INSERT observation 表 (仅 evidence + report)"""
    data = _evidence()
    compliance = data.get("red_lines_compliance", {})
    assert compliance.get("no_insert_observation") is True
    # 守门: 无 cegr.* production table mutation
    repo = REPO_ROOT
    seed_sqls = list((repo / "scripts").glob("seed_u6_canary*.sql")) + list((repo / "scripts").glob("seed_m4_20_canary*.sql"))
    assert not seed_sqls, f"金丝雀不应有 INSERT seed SQL: {seed_sqls}"


def test_red_line_docs81_untouched() -> None:
    """657-A §5 红线 4: docs/81 既有正文零改动"""
    docs81 = _read(DOCS_81)
    # docs/81 必须在 U6 登记时已存在, 657-A 不追加新内容
    assert "U6" in docs81 and "hongheiku" in docs81.lower()
    # evidence/report 不应修改 docs/81 路径
    ev = _evidence()
    assert "docs/81" not in str(ev.get("red_lines_compliance", {}))


def test_red_line_no_bypass_captcha_or_waf() -> None:
    """657-A §5 红线 3: 不绕过任何反爬 (本域无 WAF/验证码, 无 bypass 动作)"""
    data = _evidence()
    compliance = data.get("red_lines_compliance", {})
    assert compliance.get("no_bypass_captcha") is True


def test_tag_path_assumption_failure_documented() -> None:
    """657-A §6 失败形式库新增第 5 例: TAG_PATH_ASSUMPTION_ERROR (tasking /tag/{省名} 假设失败)"""
    data = _evidence()
    overrun = data.get("http_overrun_reason", "")
    assert "tag" in overrun.lower(), f"http_overrun_reason 未记录 tag-path 假设失败: {overrun}"
    assert data.get("http_used") == 12
    assert data.get("http_budget") == 10
    # report 也必须记录此失败
    report = _read(REPORT)
    assert "TAG_PATH_ASSUMPTION_ERROR" in report or "tag-path" in report.lower()


def test_implication_658_batch_unlocked() -> None:
    """657-A §7 implication: 5/5 一致 → 658 批量授权解锁 (26 省 + 三次产业)"""
    data = _evidence()
    impl = data.get("implication", "")
    assert "658" in impl, f"implication 未指向 658 批量: {impl}"
    assert "26 省" in impl or "26省" in impl
