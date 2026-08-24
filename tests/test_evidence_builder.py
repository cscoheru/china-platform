"""R3-G + G-2: evidence builder 结构与负例测试。

关键约束（G-2）：
  * 每次构建把 manifest 写入 EVIDENCE_PACK_DIR 指定的临时目录，
    绝不覆盖仓库 evidence_pack/manifest.json —— 原生 evidence build 污染。
  * 结构测试用 SKIP_PYTEST/SKIP_PSQL=1 跳过真实子进程调用（避免 builder 内
    再运行 pytest 造成递归），仅校验 manifest 契约。
  * 负例测试用 FORCE_PYTEST/FORCE_PSQL/FORCE_HASH 确定性注入失败，
    验证 builder 以非 0 退出（绝不把失败标为 PASSED）。
  * 成功语义（pytest + DB 均 exit 0、无 skipped/SKIP 标记）用 FORCE=ok 校验。

注意：真正的“全程真实运行”（不设任何 SKIP/FORCE，真跑 spikes+tests 全套 +
真实 psql）不能作为 pytest 用例，因为 builder 内部会再次运行 pytest，与本
用例所在的 pytest 会话发生递归。该真实运行在最终交付（#54）中以外壳命令
`python3 scripts/build_evidence_pack.py` 单独执行并人工核验。
"""
from __future__ import annotations

import hashlib
import json
import os
import subprocess
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parent.parent
BUILDER = REPO / "scripts" / "build_evidence_pack.py"
REAL_MANIFEST = REPO / "evidence_pack" / "manifest.json"


def sha256_of(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            h.update(chunk)
    return h.hexdigest()


def run_builder(extra_env: dict[str, str], evidence_dir: Path) -> subprocess.CompletedProcess:
    """在临时 evidence_dir 里跑 builder，返回 completed process。

    R4-1: 测试钩子（SKIP_*/FORCE_*）必须显式 EVIDENCE_PACK_TEST_HOOKS=1 才能生效。
    本 helper 自动加上该标志，所有 SKIP/FORCE 场景均视为受控测试环境。
    """
    env = {
        **os.environ,
        "EVIDENCE_PACK_DIR": str(evidence_dir),
        "EVIDENCE_PACK_TEST_HOOKS": "1",
        **extra_env,
    }
    return subprocess.run(
        [sys.executable, str(BUILDER)],
        cwd=str(REPO), capture_output=True, text=True, env=env, timeout=120,
    )


# ---------------------------------------------------------------------------
# Structure (contract) tests — run in a temp dir, SKIP the subprocess calls
# ---------------------------------------------------------------------------

@pytest.fixture(scope="module")
def built_manifest(tmp_path_factory):
    """结构构建：skip pytest+psql，写入临时目录；返回 (manifest, process, real_before)。

    real_before 为构建前仓库真实 manifest 的 sha256（若存在），用于证明
    本次构建绝未覆盖真实 manifest。
    """
    real_before = sha256_of(REAL_MANIFEST) if REAL_MANIFEST.exists() else None
    ev = tmp_path_factory.mktemp("ev_struct")
    proc = run_builder({"SKIP_PYTEST": "1", "SKIP_PSQL": "1"}, ev)
    manifest = json.loads((ev / "manifest.json").read_text(encoding="utf-8"))
    return manifest, proc, real_before


def test_builder_exit_zero_on_clean_state(built_manifest):
    manifest, proc, _ = built_manifest
    assert proc.returncode == 0, f"builder stderr: {proc.stderr}"
    assert manifest["schema_version"].startswith("1.")
    assert manifest["artifact_count"] == len(manifest["artifacts"])


def test_builds_to_temp_dir_not_real_manifest(built_manifest):
    """G-2: 结构构建写入临时 dir，绝不覆盖仓库真实 manifest。"""
    _, _, real_before = built_manifest
    real_after = sha256_of(REAL_MANIFEST) if REAL_MANIFEST.exists() else None
    assert real_after == real_before, (
        "结构构建改写了仓库 evidence_pack/manifest.json —— 违反 G-2 临时目录隔离"
    )


def test_builder_excludes_self_hash(built_manifest):
    """R3-G-3: manifest 自身 hash 不应出现在 artifacts 列表中。"""
    manifest, _, _ = built_manifest
    paths = {a["path"] for a in manifest["artifacts"]}
    assert "evidence_pack/manifest.json" not in paths, (
        "manifest 包含自身 hash — chicken-and-egg 死锁违反 R3-G-3"
    )


def test_manifest_no_absolute_paths(built_manifest):
    """R3-G-6: manifest 不得含绝对路径。"""
    manifest, _, _ = built_manifest
    raw = json.dumps(manifest)
    assert "/Users/" not in raw, "manifest 包含 /Users/ 绝对路径"
    assert "/home/" not in raw, "manifest 包含 /home/ 绝对路径"
    assert "/tmp/" not in raw, "manifest 包含 /tmp/ 绝对路径"


def test_manifest_no_wall_clock_field(built_manifest):
    """R3-G-6: 禁止 generated_at_utc（不可复现）；仅 commit_timestamp_utc 可保留。"""
    manifest, _, _ = built_manifest
    forbidden = {"generated_at_utc", "wall_clock_now"}
    assert not (forbidden & set(manifest.keys())), (
        f"manifest 包含 wall-clock 字段: {forbidden & set(manifest.keys())}"
    )


def test_artifact_count_matches_role_count_sum(built_manifest):
    """R3-G-8: role_count 之和 = artifact_count。"""
    manifest, _, _ = built_manifest
    s = sum(manifest["role_count"].values())
    assert s == manifest["artifact_count"], (
        f"role_count sum={s} != artifact_count={manifest['artifact_count']}"
    )
    roles_by_path = {artifact["path"]: artifact["role"] for artifact in manifest["artifacts"]}
    assert roles_by_path["data/extracts/04-scanned-pdf/shaanxi_text_ocr.json"] == (
        "research_non_gating_extracted_artifact"
    )
    assert roles_by_path[
        "data/extracts/04-scanned-pdf/shaanxi_text_eval_report.json"
    ] == "research_non_gating_eval_report"


def test_schema_ddl_artifact_present_and_hash_matches(built_manifest):
    """manifest 必须包含 schema_ddl，且 hash 与磁盘匹配。"""
    manifest, _, _ = built_manifest
    ddl_artifacts = [a for a in manifest["artifacts"]
                     if a["role"] == "schema_ddl"]
    assert len(ddl_artifacts) >= 1, "schema_ddl 角色缺失"
    actual_sha = sha256_of(REPO / "schema" / "01-core.sql")
    assert any(a["sha256"] == actual_sha for a in ddl_artifacts), (
        "schema/01-core.sql 实际 hash 不匹配 manifest"
    )


def test_schema_ddl_sha_in_execution_block_matches(built_manifest):
    """R3-G-4: db_ddl_execution.ddl_sha256 与磁盘 schema/01-core.sql 一致。"""
    manifest, _, _ = built_manifest
    db_block = manifest.get("db_ddl_execution", {})
    recorded_sha = db_block.get("ddl_sha256")
    actual_sha = sha256_of(REPO / "schema" / "01-core.sql")
    assert recorded_sha == actual_sha, (
        f"db_ddl_execution.ddl_sha256={recorded_sha} 与磁盘 {actual_sha} 不一致"
    )


# ---------------------------------------------------------------------------
# Success semantics — FORCE=ok (no real subprocess, no recursion), proves
# the manifest carries exit_code 0 for BOTH pytest and DB and no skipped/SKIP.
# ---------------------------------------------------------------------------

def test_success_manifest_has_zero_exit_and_no_skip(tmp_path_factory):
    """G-2 + R4-1: 成功语义下 pytest + DB 均 exit 0，且无 skipped=True 标记。

    R4-1: 真实构建必须在 manifest 携带 pytest stats（含 skipped 计数键），
    但 stats 仅作为数值；真正的"跳过标记"是 skipped=True / SKIP_PYTEST 等字符串。
    """
    ev = tmp_path_factory.mktemp("ev_ok")
    proc = run_builder({"FORCE_PYTEST": "ok", "FORCE_PSQL": "ok"}, ev)
    assert proc.returncode == 0, f"builder stderr: {proc.stderr}"
    manifest = json.loads((ev / "manifest.json").read_text(encoding="utf-8"))
    assert manifest["pytest_run"]["exit_code"] == 0
    assert manifest["db_ddl_execution"]["exit_code"] == 0
    assert manifest["pytest_run"].get("skipped") is not True
    assert manifest["db_ddl_execution"].get("skipped") is not True
    # 禁止 SKIP_PYTEST/SKIP_PSQL 字符串（强制跳过标记）
    raw = json.dumps(manifest)
    assert "SKIP_PYTEST" not in raw, "成功 manifest 不应含 SKIP_PYTEST"
    assert "SKIP_PSQL" not in raw, "成功 manifest 不应含 SKIP_PSQL"


# ---------------------------------------------------------------------------
# Negative (fault injection) — each failure MUST yield non-zero exit
# ---------------------------------------------------------------------------

def test_pytest_failure_returns_nonzero(tmp_path_factory):
    """G-2: pytest 失败 → builder 非 0 退出（绝不当 PASSED）。"""
    ev = tmp_path_factory.mktemp("ev_pyfail")
    proc = run_builder({"FORCE_PYTEST": "fail", "FORCE_PSQL": "ok"}, ev)
    assert proc.returncode == 2, f"期望 return 2，实际 {proc.returncode}"
    assert "PYTEST FAILED" in proc.stderr


def test_db_failure_returns_nonzero(tmp_path_factory):
    """G-2: DB apply 失败 → builder 非 0 退出（此前被静默放行，现已是硬失败）。"""
    ev = tmp_path_factory.mktemp("ev_dbfail")
    proc = run_builder({"FORCE_PYTEST": "ok", "FORCE_PSQL": "fail"}, ev)
    assert proc.returncode == 5, f"期望 return 5，实际 {proc.returncode}"
    assert "DB APPLY FAILED" in proc.stderr


def test_hash_failure_returns_nonzero(tmp_path_factory):
    """G-2: hash 校验失败 → builder 非 0 退出（return 4）。"""
    ev = tmp_path_factory.mktemp("ev_hashfail")
    proc = run_builder(
        {"FORCE_PYTEST": "ok", "FORCE_PSQL": "ok", "FORCE_HASH": "fail"}, ev)
    assert proc.returncode == 4, f"期望 return 4，实际 {proc.returncode}"
    assert "HASH MISMATCH" in proc.stderr


def test_skip_mode_reports_skipped_not_passed(tmp_path_factory):
    """G-2: SKIP 模式必须在 manifest 中显式记录 skipped，而非伪装成 PASSED。"""
    ev = tmp_path_factory.mktemp("ev_skipmode")
    proc = run_builder({"SKIP_PYTEST": "1", "SKIP_PSQL": "1"}, ev)
    assert proc.returncode == 0  # 结构构建本身成功
    manifest = json.loads((ev / "manifest.json").read_text(encoding="utf-8"))
    assert manifest["pytest_run"].get("skipped") is True
    assert manifest["db_ddl_execution"].get("skipped") is True


# ---------------------------------------------------------------------------
# R4-1: 真实构建遇到测试钩子变量必须立即拒绝（除非 TEST_HOOKS 启用）
# ---------------------------------------------------------------------------

def _run_builder_real(extra_env: dict[str, str],
                      evidence_dir: Path) -> subprocess.CompletedProcess:
    """不带 EVIDENCE_PACK_TEST_HOOKS=1 的"真实"调用。"""
    env = {**os.environ, "EVIDENCE_PACK_DIR": str(evidence_dir), **extra_env}
    return subprocess.run(
        [sys.executable, str(BUILDER)],
        cwd=str(REPO), capture_output=True, text=True, env=env, timeout=120,
    )


def test_builder_refuses_hook_without_test_hooks_enabled(tmp_path_factory):
    """R4-1: 真实构建携带 SKIP_PYTEST=1 必须立即拒绝（rc=6）。"""
    ev = tmp_path_factory.mktemp("ev_refuse_skip")
    proc = _run_builder_real({"SKIP_PYTEST": "1"}, ev)
    assert proc.returncode == 6, (
        f"期望 rc=6 (refused)，实际 {proc.returncode}；"
        f"stderr={proc.stderr[-1000:]}"
    )
    assert "BUILDER REFUSED" in proc.stderr
    assert not (ev / "manifest.json").exists(), (
        "refused 路径下不应产出 manifest"
    )


def test_builder_refuses_force_hook_without_test_hooks(tmp_path_factory):
    """R4-1: 真实构建携带 FORCE_PYTEST=ok 必须立即拒绝。"""
    ev = tmp_path_factory.mktemp("ev_refuse_force")
    proc = _run_builder_real({"FORCE_PYTEST": "ok"}, ev)
    assert proc.returncode == 6
    assert "BUILDER REFUSED" in proc.stderr


# ---------------------------------------------------------------------------
# R4-3: 逐项验证（无随机抽样）+ 篡改负例
# ---------------------------------------------------------------------------

def test_builder_verifies_every_artifact_not_sampled(tmp_path_factory):
    """R4-3: 真实 builder 写出 manifest 后必须逐项验证所有 artifact。

    通过对比随机位置的篡改能否被 builder 捕获来证明确实"全量"校验，
    而非随机抽 5 个。
    """
    # 准备一个真实产物的代理环境：SKIP 跳过 pytest+DB，写入 tmp_dir，
    # 然后改一个非前 5 的 artifact 哈希；如果 builder 真逐项校验，
    # 修改后再次调用 verify 即可捕获。
    ev1 = tmp_path_factory.mktemp("ev_full1")
    proc1 = run_builder({"SKIP_PYTEST": "1", "SKIP_PSQL": "1"}, ev1)
    assert proc1.returncode == 0
    manifest = json.loads((ev1 / "manifest.json").read_text(encoding="utf-8"))
    # 选一个非前 5 的 artifact（如果总数 < 6 则选最后一个）
    if len(manifest["artifacts"]) >= 6:
        target = manifest["artifacts"][5]
    else:
        target = manifest["artifacts"][-1]
    target_rel = target["path"]
    # 用 EVIDENCE_PACK_TAMPER 模拟"磁盘被改" — builder 覆盖 sha256 后立即校验
    ev2 = tmp_path_factory.mktemp("ev_full2")
    proc2 = run_builder(
        {"SKIP_PYTEST": "1", "SKIP_PSQL": "1",
         "EVIDENCE_PACK_TAMPER": target_rel},
        ev2,
    )
    assert proc2.returncode == 4, (
        f"篡改应被逐项验证捕获 (rc=4)，实际 {proc2.returncode}"
    )
    assert target_rel in proc2.stderr, (
        f"stderr 应指明被篡改的 artifact；got stderr={proc2.stderr[-1000:]}"
    )


def test_builder_path_uniqueness_and_role_count_consistency(tmp_path_factory):
    """R4-3: 路径唯一 + role_count 之和 = artifact_count。"""
    ev = tmp_path_factory.mktemp("ev_uniq")
    proc = run_builder({"SKIP_PYTEST": "1", "SKIP_PSQL": "1"}, ev)
    assert proc.returncode == 0
    manifest = json.loads((ev / "manifest.json").read_text(encoding="utf-8"))
    paths = [a["path"] for a in manifest["artifacts"]]
    assert len(set(paths)) == len(paths), "artifacts 路径重复"
    for p in paths:
        assert not p.startswith("/"), f"非相对路径: {p}"
        assert "evidence_pack/manifest.json" not in paths, (
            "manifest 列入自身"
        )
    assert sum(manifest["role_count"].values()) == manifest["artifact_count"]
