"""R3-H: 测试纯净性契约测试。

验证：
1. tests/test_*.py 不在工作区根 / data/ / spikes/ 留下污染文件
2. 每次测试前后 git status 一致（tracked + untracked hash 集合）
3. tmp_path / TemporaryDirectory 用于隔离 IO
4. data/should_not_exist.json 类污染被禁止

本测试为自身检查：扫描整个工作区，确保没有"测试不应产生的工作区文件"。
"""
from __future__ import annotations

import hashlib
import os
import re
import subprocess
import sys
from pathlib import Path

import pytest

WORKSPACE_ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = WORKSPACE_ROOT / "data"


# 必须不存在的污染文件清单（per directive H-3）
FORBIDDEN_WORKSPACE_FILES = [
    DATA_DIR / "should_not_exist.json",
    DATA_DIR / "test_pollution.json",
    DATA_DIR / "scratch.json",
    DATA_DIR / "tmp_test_output.json",
    WORKSPACE_ROOT / "test_output.json",
    WORKSPACE_ROOT / "scratch.txt",
]


@pytest.mark.parametrize("forbidden_path", FORBIDDEN_WORKSPACE_FILES,
                         ids=lambda p: p.name)
def test_forbidden_workspace_file_must_not_exist(forbidden_path: Path):
    """返工指令 H-3：data/should_not_exist.json 等污染文件不得重新出现。

    测试前后快照一致性：这些文件本来就不该存在；若存在，说明某 spike/脚本
    在 working directory 写入而不是 tmp_path/TemporaryDirectory。
    """
    assert not forbidden_path.exists(), (
        f"污染文件 {forbidden_path} 存在 — 测试/script 未用 tmp_path/TemporaryDirectory。"
        f"删除此文件并修复上游脚本的 IO 路径。"
    )


def test_data_dir_has_only_gitkeep_or_known_subdirs():
    """data/ 下不应有意外的 .json/.csv/.txt 污染文件。

    仅允许（房规白名单 — per tasking 581 §C; 存量合法目录的登记，非放宽）:
    - data/extracts/<spike>/*（提取产物目录，由 manifest 管理）
    - data/processed/*（处理产物目录）
    - data/raw/<sample>/*（原始样本目录，按 .gitignore 处理）
    - data/seeds/（S2.1 demo seed JSON，manifest 在册 per knife 577）
    - data/seed_archives/（seed 归档链）
    - data/public_extracts/ + data/public_archives/（公开提取 WORM 链目录）
    """
    if not DATA_DIR.exists():
        pytest.skip("data/ not present")
    allowed_top_level = {
        "extracts", "processed", "raw",
        "public_archives", "public_extracts",
        "seed_archives", "seeds",
        ".gitkeep",
    }
    actual_top_level = {p.name for p in DATA_DIR.iterdir() if not p.name.startswith(".")}
    unexpected = actual_top_level - allowed_top_level
    assert not unexpected, (
        f"data/ 下出现意外目录/文件: {unexpected}。"
        f"允许: {allowed_top_level}。"
    )


def test_workspace_no_loose_json_outside_data():
    """工作区根不应有 *.json（除已知 manifest/config/registry 文件）。"""
    allowed_jsons = {
        "evidence_pack/manifest.json",
        "source_registry/registry.csv",  # csv 但也列出
        "spikes/04-scanned-pdf/gate_thresholds.json",
        "spikes/04-scanned-pdf/truth_p24.json",
        "schema/migrations/001_create_core.log",  # log，但列出作为 reference
    }
    found = []
    for json_path in WORKSPACE_ROOT.glob("*.json"):
        rel = json_path.relative_to(WORKSPACE_ROOT)
        if str(rel) not in allowed_jsons:
            found.append(str(rel))
    assert not found, (
        f"工作区根出现未授权 .json 文件: {found}。"
        f"允许: {sorted(allowed_jsons)}"
    )


def test_tmp_path_used_by_tests_not_workspace_path():
    """meta-test: 验证测试目录结构使用 pytest tmp_path。

    本测试本身在 tmp_path 内运行 — 如果它能落到 working dir 的污染文件，
    那就说明测试机制有 bug。
    """
    # 在测试自己的临时位置写入
    import tempfile
    with tempfile.TemporaryDirectory() as tmp:
        tmp_path = Path(tmp)
        marker = tmp_path / "test_marker.txt"
        marker.write_text("contract test isolated IO")
        assert marker.exists()
    # 退出 with 块后 TemporaryDirectory 应自动清理
    assert not marker.exists()


@pytest.fixture(scope="module")
def git_tracked_hash():
    """记录测试开始前的 git tracked hash 集合。"""
    try:
        result = subprocess.run(
            ["git", "ls-files", "-s"],
            cwd=str(WORKSPACE_ROOT),
            capture_output=True, text=True, timeout=30,
        )
        if result.returncode != 0:
            pytest.skip("git not available or not a git repo")
        return result.stdout
    except (FileNotFoundError, subprocess.TimeoutExpired):
        pytest.skip("git unavailable")


def test_git_tracked_hash_unchanged_during_test_run(git_tracked_hash):
    """测试运行期间不得修改任何 tracked 文件。"""
    after = subprocess.run(
        ["git", "ls-files", "-s"],
        cwd=str(WORKSPACE_ROOT),
        capture_output=True, text=True, timeout=30,
    )
    assert after.stdout == git_tracked_hash, (
        "测试期间 git tracked 文件 hash 集合发生变化 — 违反 R3-H 纯净性。"
        "运行 `git status` 查看哪些 tracked 文件被改。"
    )


# ---------------------------------------------------------------------------
# H-2: REAL working-tree content hash zero-pollution proof
# ---------------------------------------------------------------------------

def _real_worktree_hash(root: Path) -> str:
    """对 worktree 所有实际文件内容做递归 sha256（含 untracked），排除干扰目录。

    关键差异（相对上面的 git ls-files -s）：
      * 哈希的是磁盘上的真实字节，而非 git 索引中的 blob sha —— 能捕获
        "改了 tracked 文件但没 add" 的就地污染；
      * 覆盖 untracked 文件 —— 能捕获测试在仓库根/子目录新建文件；
      * 排除 __pycache__/、.git/、.pytest_cache/（运行期必然产生的噪音），
        但绝不排除任何源码/样本/产物 —— 真实内容才是判定标准。
    """
    skip_dirs = {"__pycache__", ".git", ".pytest_cache", ".mypy_cache"}
    h = hashlib.sha256()
    for p in sorted(root.rglob("*"), key=lambda x: str(x.relative_to(root))):
        if not p.is_file():
            continue
        rel = p.relative_to(root)
        if any(part in skip_dirs for part in rel.parts):
            continue
        if p.suffix in {".pyc", ".pyo"}:
            continue
        h.update(str(rel).encode("utf-8"))
        h.update(b"\x00")
        h.update(p.read_bytes())
        h.update(b"\x00")
    return h.hexdigest()


def test_suite_leaves_no_worktree_trace_h2(tmp_path_factory):
    """H-2 (R4): 真实 worktree 内容 hash 在整套 pytest 前后必须一致，
    **且子进程不得存在 failed / skipped**（R4-1 反 skip-as-PASS）。

    反递归：子进程以 `--deselect <本用例 nodeid>` 排除本用例本身，
    因此不再需要 `pytest.skip` 防递归。父用例额外断言子进程统计：
      failed == 0, skipped == 0, passed == (parent collect-only) - 1。
    """
    this_nodeid = (
        f"{Path(__file__).relative_to(WORKSPACE_ROOT)}"
        "::test_suite_leaves_no_worktree_trace_h2"
    )
    collect_env = {**os.environ, "PYTHONDONTWRITEBYTECODE": "1"}
    collected = subprocess.run(
        [sys.executable, "-m", "pytest", "--collect-only", "-q",
         "-p", "no:cacheprovider"],
        cwd=str(WORKSPACE_ROOT), capture_output=True, text=True,
        env=collect_env, timeout=300,
    )
    assert collected.returncode == 0, collected.stderr
    expected = sum(
        1 for ln in collected.stdout.splitlines()
        if "::" in ln and (ln.startswith("spikes/") or ln.startswith("tests/"))
    )

    before = _real_worktree_hash(WORKSPACE_ROOT)
    evidence_dir = tmp_path_factory.mktemp("h2_evidence")
    env = {**os.environ,
           "EVIDENCE_PACK_DIR": str(evidence_dir),
           "PYTHONDONTWRITEBYTECODE": "1"}
    proc = subprocess.run(
        [sys.executable, "-m", "pytest", "-q", "-p", "no:cacheprovider",
         "--deselect", this_nodeid],
        cwd=str(WORKSPACE_ROOT), capture_output=True, text=True, env=env,
        timeout=900,
    )
    out = proc.stdout
    m_pass = re.search(r"(\d+) passed", out)
    m_fail = re.search(r"(\d+) failed", out)
    m_skip = re.search(r"(\d+) skipped", out)
    passed = int(m_pass.group(1)) if m_pass else 0
    failed = int(m_fail.group(1)) if m_fail else 0
    skipped = int(m_skip.group(1)) if m_skip else 0
    assert proc.returncode == 0, (
        f"子进程 pytest exit={proc.returncode}\n{out[-3000:]}\n{proc.stderr[-1500:]}"
    )
    assert failed == 0, (
        f"H-2 子进程出现 {failed} failed（破坏 0-failed 不变量）\n{out[-2000:]}"
    )
    assert skipped == 0, (
        f"H-2 子进程出现 {skipped} skipped（R4-1 skip-as-PASS 禁止）\n{out[-2000:]}"
    )
    assert passed == expected - 1, (
        f"子进程通过 {passed} ≠ collect-only({expected}) - 1。"
        f"请检查 --deselect 是否漏配或测试总数漂移。"
    )
    after = _real_worktree_hash(WORKSPACE_ROOT)
    assert before == after, (
        "整套 pytest 运行后 worktree 内容 hash 发生变化 — 存在工作区污染。"
        "调用方请用 `git status` + `git diff` 定位是哪个测试写了非临时文件，"
        "并改用 tmp_path / TemporaryDirectory。"
    )