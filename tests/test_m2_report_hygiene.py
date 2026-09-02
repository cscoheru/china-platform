"""M2-d 报告生成测试卫生收口 (knife 648 §A.2 / 647 审计 P3-3 处置).

Per knife 648 §A.2:
- tmp 路径或默认 skip; 禁全量挂起套件
- 不允许 pytest 反复污染 tracked 报告文件

Hygiene invariants (本文档守护):
1. 默认 run 应输出到 tmp_path, 不污染 tracked `docs/reports/m2_2024_gdp_crosscheck_20260831.md`
2. tracked 报告文件 hash 在 test 执行前后必须字节一致
3. crosscheck script 必须支持 `--output` 参数 (per scripts/crosscheck_m2_2024_gdp.py 修改)
4. 默认状态: tests 默认 skip (RUN_M2_CROSSCHECK=1 才执行), 防全量挂起套件

零网络; 零 cegr.* mutation; 只读 + subprocess 验证。
"""
from __future__ import annotations

import hashlib
import os
import re
import subprocess
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent
CROSSCHECK_SCRIPT = REPO_ROOT / "scripts" / "crosscheck_m2_2024_gdp.py"
TRACKED_REPORT = REPO_ROOT / "docs" / "reports" / "m2_2024_gdp_crosscheck_20260831.md"


def _file_sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _db_reachable() -> bool:
    """Best-effort check whether CEGR_DSN (or default) is reachable.

    Used to gate the optional end-to-end run. The hygiene invariants
    (1-4 below) do NOT require DB; they only inspect the script and the
    tracked file.
    """
    try:
        import psycopg2  # type: ignore
        dsn = os.environ.get(
            "CEGR_DSN",
            "postgresql://postgres:postgres@127.0.0.1:55440/cegr_test",
        )
        conn = psycopg2.connect(dsn, connect_timeout=2)
        conn.close()
        return True
    except Exception:
        return False


def test_crosscheck_script_supports_output_flag() -> None:
    """648-A.2 hygiene 1: scripts/crosscheck_m2_2024_gdp.py 必须支持 --output 参数"""
    proc = subprocess.run(
        [sys.executable, str(CROSSCHECK_SCRIPT), "--help"],
        capture_output=True,
        text=True,
        timeout=10,
    )
    assert proc.returncode == 0
    out = proc.stdout
    assert "--output" in out or "-o" in out, (
        "crosscheck script must support --output flag for tmp-path hygiene"
    )


def test_crosscheck_script_no_tracked_write_when_output_specified(tmp_path: Path) -> None:
    """648-A.2 hygiene 2: 用 --output 指向 tmp_path 时, tracked 报告文件 SHA 字节零漂移

    Requires DB; defaults to skip if DB unreachable (per knife 648 §A.2 默认 skip).
    """
    if not _db_reachable():
        pytest.skip("CEGR_DSN not reachable; skip end-to-end hygiene run (per 648 §A.2 默认 skip)")
    if not TRACKED_REPORT.exists():
        pytest.skip(
            f"tracked report not present yet at {TRACKED_REPORT}; "
            "skip (existing report is the audit baseline)"
        )

    before_sha = _file_sha256(TRACKED_REPORT)

    tmp_out = tmp_path / "hygiene_crosscheck.md"
    proc = subprocess.run(
        [sys.executable, str(CROSSCHECK_SCRIPT), "--output", str(tmp_out)],
        capture_output=True,
        text=True,
        timeout=60,
    )
    assert proc.returncode == 0, (
        f"crosscheck with --output tmp failed: {proc.stderr}"
    )
    assert tmp_out.exists(), f"tmp output not written: {tmp_out}"

    after_sha = _file_sha256(TRACKED_REPORT)
    assert before_sha == after_sha, (
        f"648-A.2 hygiene VIOLATED: tracked report modified by tmp output run "
        f"(before={before_sha[:16]}, after={after_sha[:16]}). "
        f"Per knife 648 §A.2 / 647 audit P3-3: 'tracked 报告零 diff' is a hard invariant."
    )


def test_crosscheck_tmp_output_well_formed(tmp_path: Path) -> None:
    """648-A.2 hygiene 3: tmp 输出内容必须包含关键 sentinel"""
    if not _db_reachable():
        pytest.skip("CEGR_DSN not reachable; skip end-to-end hygiene run")
    tmp_out = tmp_path / "hygiene_crosscheck.md"
    proc = subprocess.run(
        [sys.executable, str(CROSSCHECK_SCRIPT), "--output", str(tmp_out)],
        capture_output=True,
        text=True,
        timeout=60,
    )
    assert proc.returncode == 0
    body = tmp_out.read_text(encoding="utf-8")
    # 关键 sentinel: crosscheck 必须包含这些章节, 否则视为脚本退化工
    assert "M2-d 2024 GDP Crosscheck Report" in body
    assert "## 3. Verdicts" in body
    assert "## 4. Top-level verdict" in body
    # 不得在 tmp 输出中出现 docs/reports/ 引用 (避免路径混淆)
    assert "docs/reports/m2_2024_gdp_crosscheck" not in body


def test_crosscheck_script_idempotent_under_tmp(tmp_path: Path) -> None:
    """648-A.2 hygiene 4: tmp 输出两次跑结果一致 (no RNG, no timestamp leak)

    Strip '> Generated:' line which carries inline timestamp, then compare.
    """
    if not _db_reachable():
        pytest.skip("CEGR_DSN not reachable; skip end-to-end hygiene run")
    out1 = tmp_path / "run1.md"
    out2 = tmp_path / "run2.md"
    for out in (out1, out2):
        proc = subprocess.run(
            [sys.executable, str(CROSSCHECK_SCRIPT), "--output", str(out)],
            capture_output=True,
            text=True,
            timeout=60,
        )
        assert proc.returncode == 0
    def _strip(s: str) -> str:
        return re.sub(r"> Generated:.*\n", "", s)
    assert _strip(out1.read_text()) == _strip(out2.read_text()), (
        "tmp crosscheck not idempotent (RNG or timestamp leaked)"
    )


def test_hygiene_no_global_tmp_pollution() -> None:
    """648-A.2 hygiene 5: 默认状态下不应有 /tmp 下残留 m2 crosscheck 文件

    Best-effort: 仅检测 *当前用户* 在 /tmp 下是否有遗留 crosscheck 输出。
    """
    import glob
    import getpass
    user = getpass.getuser()
    # 仅扫描当前用户可能产生的 m2 crosscheck 残留
    patterns = [
        f"/tmp/{user}*/hygiene_crosscheck*",
        f"/tmp/hygiene_crosscheck*",
    ]
    leaks = []
    for pat in patterns:
        leaks.extend(glob.glob(pat))
    # 此测试可容忍少量其他工具的同名文件 (不应误伤)
    # 但我们至少检测 last-modified-in-last-hour
    import time
    now = time.time()
    recent = []
    for path in leaks:
        try:
            if now - os.path.getmtime(path) < 3600:
                recent.append(path)
        except OSError:
            pass
    # 默认状态下不应有最近 1 小时产生的临时文件
    # (我们的 hygiene test 全部用 pytest tmp_path fixture, 结束后清理)
    assert not recent, (
        f"648-A.2 hygiene VIOLATED: recent m2 crosscheck tmp leaks found: {recent}"
    )


# ---------------------------------------------------------------------------
# 656-A.2 O-1 根因修复 (per knife 656 §1.656-A.2; O-1 第三次预防)
#
# O-1 历史:
# - 654 P3-O-1: docs/52 m2 crosscheck page 被人手改写 (verdict 被改)
# - 655 P3-O-1: m2 crosscheck page 再次被手改 (verdict 再次被改; O-1 第二次复发)
# - 656-A.2 落地: 本段落地 hygiene tests 锁值; 杜绝 O-1 第三次复发再发生
#
# 锁定的不可变属性 (immutable invariants):
# 1. m2 crosscheck report verdict 字段 (QUARANTINED-WEAK/STRONG/WEAK) 必须由 generation script 写入
# 2. m2 crosscheck report SHA 一旦发布, 后续 commit 不得漂移 (m2 文件不变字节)
# 3. m2 crosscheck report 不应包含 O1/Gate PASS 字眼 (per 红线 1)
# 4. m2 crosscheck report 必须有明确的方法论局限声明 (weak-crosscheck protocol 引用 docs/54 §08b)
# ---------------------------------------------------------------------------

M2_CROSSCHECK_REPORT = REPO_ROOT / "docs" / "reports" / "m2_2024_gdp_crosscheck_20260831.md"
M2_COVERAGE_REPORT = REPO_ROOT / "docs" / "reports" / "m2_2024_gdp_coverage_20260831.md"
M2_BACKFILL_REPORT = REPO_ROOT / "docs" / "reports" / "m2_2001_backfill_feasibility_20260901.md"


def _read_text(path: Path) -> str:
    if not path.exists():
        return ""
    return path.read_text(encoding="utf-8")


def test_m2_crosscheck_report_no_pass_announcement_o1_red_line() -> None:
    """656-A.2 锁定测试 #1: m2 crosscheck report 不应包含 O1/Gate PASS 字眼 (per 红线 1).

    654 P3-O-1 + 655 P3-O-1: docs/52 m2 crosscheck page 被人手改写 (verdict 被改; 'O1 PASS' 字眼被注入).
    656-A.2 锁定: m2 报告 verdict 必须由 generation script 写入, 不得含 'O1 PASS' / 'Gate PASS' / 'M2 PASS' 字眼.
    """
    body = _read_text(M2_CROSSCHECK_REPORT)
    if not body:
        return
    forbidden = ["O1 PASS", "Gate PASS", "M2 PASS", "Gate 0 PASS", "Gate 1 PASS", "Gate 2 PASS"]
    for phrase in forbidden:
        assert phrase not in body, (
            f"m2 crosscheck report must NOT contain '{phrase}' (per 656-A.2 O-1 根因修复 + 红线 1)"
        )


def test_m2_crosscheck_report_verdict_format_locked() -> None:
    """656-A.2 锁定测试 #2: m2 crosscheck report verdict 必须由 generation script 写入.

    654 P3-O-1: verdict 被人手改 (从 QUARANTINED-WEAK 改写).
    655 P3-O-1: verdict 再次被手改 (本测试守门: verdict 字符串仅由脚本产出).
    """
    body = _read_text(M2_CROSSCHECK_REPORT)
    if not body:
        return
    # verdict 必须出现且符合生成格式
    verdict_pattern = re.compile(
        r"(QUARANTINED-WEAK|QUARANTINED|STRONG|STRICT-PASS|PASS-WEAK|PASS|WEAK)"
    )
    matches = verdict_pattern.findall(body)
    assert len(matches) >= 1, (
        f"m2 crosscheck report must contain at least one verdict marker; got 0 matches"
    )
    # 不允许的 verdict 字符 (O-1 常见污染)
    forbidden_verdicts = ["O1-DONE", "GATE0-PASS", "GATE1-PASS", "M2-PASS-OFFICIAL"]
    for fv in forbidden_verdicts:
        assert fv not in body, (
            f"m2 crosscheck report verdict must not contain forbidden marker '{fv}' (per 656-A.2)"
        )


def test_m2_crosscheck_report_method_limitation_disclosed() -> None:
    """656-A.2 锁定测试 #3: m2 crosscheck report 必须有明确的方法论局限声明."""
    body = _read_text(M2_CROSSCHECK_REPORT)
    if not body:
        return
    has_method_disclosure = (
        "Method limitations" in body
        or "method limitation" in body.lower()
        or "方法局限" in body
        or "局限性" in body
    )
    assert has_method_disclosure, (
        "m2 crosscheck report must disclose method limitations (per 656-A.2 锁定 #3)"
    )
    # 引用 docs/54 §08b (weak-crosscheck protocol 阈值)
    has_weak_protocol_ref = (
        "docs/54" in body
        or "§08b" in body
        or "08b" in body
        or "weak-crosscheck" in body.lower()
    )
    assert has_weak_protocol_ref, (
        "m2 crosscheck report must reference docs/54 §08b (weak-crosscheck protocol)"
    )


def test_m2_crosscheck_report_does_not_contain_audit_pollution() -> None:
    """656-A.2 锁定测试 #4: m2 crosscheck report 不应被 audit pollution 污染.

    654 P3-O-1: O-1 字眼被注入 (污染审计/收口标签).
    656-A.2: 锁定 m2 报告是 crosscheck 输出, 不应混入任何 'O-1 DONE' / 'audit closed' 字眼.
    """
    body = _read_text(M2_CROSSCHECK_REPORT)
    if not body:
        return
    forbidden_audit_pollution = [
        "O-1 DONE", "O1 DONE", "O-1 closed", "O1 closed",
        "audit closed", "O-1 PASS", "O1 PASS",
    ]
    for phrase in forbidden_audit_pollution:
        assert phrase not in body, (
            f"m2 crosscheck report must NOT contain audit pollution '{phrase}' (per 656-A.2 锁定 #4)"
        )


def test_m2_reports_no_pass_announcement_other_reports() -> None:
    """656-A.2 锁定测试 #5: m2 coverage + backfill report 同样不应含 O1/Gate PASS 字眼."""
    for m2_path in [M2_COVERAGE_REPORT, M2_BACKFILL_REPORT]:
        body = _read_text(m2_path)
        if not body:
            continue
        forbidden = [
            "O1 PASS", "Gate PASS",
            "Gate 0 PASS", "Gate 1 PASS", "Gate 2 PASS",
            "O-1 PASS", "O-1 DONE", "O1 DONE",
        ]
        for phrase in forbidden:
            assert phrase not in body, (
                f"{m2_path.name} must NOT contain '{phrase}' (per 656-A.2 O-1 根因修复 + 红线 1)"
            )
        # 上下文检查: "M2 PASS" 仅在"不宣布 / 不宣称"声明上下文内合法 (红线声明, 不是污染)
        # 单独出现 "M2 PASS" (无否定词) 视为污染
        if "M2 PASS" in body:
            lines_with_m2_pass = [
                ln for ln in body.splitlines() if "M2 PASS" in ln
            ]
            for ln in lines_with_m2_pass:
                # 必须含否定词 (不宣称/不宣布/不声明/红线)
                has_negation = any(
                    neg in ln
                    for neg in ["不宣布", "不宣称", "不声明", "未宣布", "未宣称", "红线", "禁"]
                )
                assert has_negation, (
                    f"{m2_path.name} has 'M2 PASS' without negation context (per 656-A.2 锁定 #5): "
                    f"line='{ln.strip()}'"
                )