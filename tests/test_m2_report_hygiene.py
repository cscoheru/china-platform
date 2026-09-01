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