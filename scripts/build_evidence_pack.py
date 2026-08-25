#!/usr/bin/env python3
"""Generate machine manifest + evidence pack for Stage 0 (R3 G hardened + R4-1/R4-3).

R3 hardening (返工指令 G):
1. pytest / DB apply / hash 任一失败 → 非 0 退出
2. 先执行 (pytest, psql) 再收集 hash（不预先算自己）
3. manifest 不得对自身 hash（避免 chicken-and-egg）
4. 写完后重新读取所有 hash 重新验证一遍
5. 不包装旧 DB 日志为 fresh — 实际跑 psql，应用新日志
6. 删绝对路径（repository_root 用相对或 commit SHA）+ 不可复现时间字段（用 commit timestamp 而非 wall-clock）
7. 纳入 spikes/*.zip + *.pdf + *.xlsx 等原始输入
8. artifact_count / role_count 由代码生成（不手写）
9. 失败时打印失败原因，stderr 返回非零

R4-1 hardening:
10. 解析真实 pytest stdout 统计：skipped > 0 → 非 0 退出（反 skip-as-PASS）
11. SKIP_PYTEST/SKIP_PSQL/FORCE_* 测试钩子仅在 EVIDENCE_PACK_TEST_HOOKS=1 时生效；
    真实构建遇到这些钩子变量且未启用测试钩子 → 非 0 退出（不得用于生成正式证据）

R4-3 hardening:
12. 删除"随机抽查 5 个哈希"逻辑；对 manifest 中每一个 artifact 逐项验证
    存在性、大小、SHA-256。
13. 验证路径唯一、均为相对路径、role_count 之和等于 artifact_count、
    manifest 自身不在 artifacts 列表中。
14. 负例：EVIDENCE_PACK_TAMPER=<artifact-path> 模拟"磁盘产物被改" → 必须非 0。
15. 真实 Builder 遇到 pytest skipped / DB 未执行 / 任一哈希错误 → 非 0。
"""
from __future__ import annotations

import hashlib
import json
import os
import platform
import random
import re
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent

HOOK_ENV_VARS = ("SKIP_PSQL", "FORCE_PSQL", "SKIP_PYTEST",
                 "FORCE_PYTEST", "FORCE_HASH")


# ---------- hook gating (R4-1) ----------

def _test_hooks_enabled() -> bool:
    """R4-1: 测试钩子（SKIP_*/FORCE_*）必须显式启用才能生效。"""
    return os.environ.get("EVIDENCE_PACK_TEST_HOOKS") == "1"


def _check_hook_env_clean() -> int | None:
    """若启用正式构建却携带任一测试钩子环境变量，立即非 0。
    仅在 EVIDENCE_PACK_TEST_HOOKS != '1' 时启用此门控。
    """
    if _test_hooks_enabled():
        return None
    for k in HOOK_ENV_VARS:
        if os.environ.get(k):
            print(
                f"BUILDER REFUSED: env {k}={os.environ[k]!r} requires "
                f"EVIDENCE_PACK_TEST_HOOKS=1 (R4-1). Real evidence must not "
                f"use forced/skip hooks.",
                file=sys.stderr,
            )
            return 6
    return None


# ---------- helpers ----------

def sha256_of(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            h.update(chunk)
    return h.hexdigest()


def run_cmd(cmd: list[str], cwd: Path, env: dict | None = None,
            timeout: int = 600) -> dict:
    """Run a subprocess; return result dict with exit_code, stdout, stderr."""
    proc = subprocess.run(cmd, cwd=str(cwd), capture_output=True, text=True,
                          env=env or os.environ.copy(), timeout=timeout)
    return {
        "command": " ".join(cmd),
        "exit_code": proc.returncode,
        "stdout_tail": proc.stdout[-4000:],
        "stderr_tail": proc.stderr[-2000:],
    }


def evidence_dir() -> Path:
    """G-2: 证据包输出目录。

    默认 `REPO/evidence_pack`。测试用 `EVIDENCE_PACK_DIR` 覆盖为临时目录，
    使 manifest 在隔离目录构建，绝不覆盖仓库里的真实 manifest。
    """
    override = os.environ.get("EVIDENCE_PACK_DIR")
    d = Path(override) if override else (REPO / "evidence_pack")
    d.mkdir(parents=True, exist_ok=True)
    return d


def classify(path: Path) -> str:
    p = str(path).replace(os.sep, "/")
    if p == "data/extracts/04-scanned-pdf/shaanxi_text_ocr.json":
        return "research_non_gating_extracted_artifact"
    if p == "data/extracts/04-scanned-pdf/shaanxi_text_eval_report.json":
        return "research_non_gating_eval_report"
    if p.startswith("data/extracts/") and p.endswith(".json"):
        return "extracted_artifact"
    if p == "schema/01-core.sql":
        return "schema_ddl"
    if p.startswith("schema/migrations/") and p.endswith(".sql"):
        return "schema_migration_ddl"
    if p.startswith("schema/migrations/") and p.endswith(".log"):
        return "schema_migration_log"
    if p == "tests/conftest.py":
        return "test_conftest"
    if p.startswith("spikes/"):
        if "/test_" in p and p.endswith(".py"):
            return "spike_test"
        if "/extract_" in p and p.endswith(".py"):
            return "spike_extractor"
        if "/evaluate_" in p and p.endswith(".py"):
            return "spike_evaluator"
        if "/build_truth" in p and p.endswith(".py"):
            return "spike_truth_builder"
        if p.endswith(".py"):
            return "spike_helper"
        if (p.endswith(".pdf") or p.endswith(".html") or p.endswith(".xlsx")
                or p.endswith(".xls") or p.endswith(".zip")
                or p.endswith(".jpg") or p.endswith(".txt")
                or p.endswith(".csv") or p.endswith(".json")):
            return "spike_sample_or_truth"
    if p.startswith("tests/") and p.endswith(".py"):
        return "schema_negative_test"
    if p.startswith("docs/") and p.endswith(".md"):
        return "documentation"
    if p == "source_registry/registry.csv":
        return "source_registry_csv"
    if p.startswith("source_registry/"):
        return "source_registry_doc"
    if p.startswith("data/raw/"):
        return "raw_data"
    if p.startswith("evidence_pack/"):
        return "evidence_pack_artifact"
    # GE (S1.11) — all ge/ artifacts roll up to a single data_contract_suite
    # role per docs/25 + reviews/86 §NOW pack contract (role_count +1).
    if p.startswith("ge/") or p.startswith(".github/workflows/"):
        return "data_contract_suite"
    if p == "Makefile":
        return "data_contract_suite"
    return "other"


# ---------- core: collect artifacts WITHOUT hashing the manifest itself ----------

def collect_artifacts(self_path: Path) -> list[dict]:
    """Walk repo, hash every artifact except the generated manifest itself."""
    patterns = [
        "data/extracts/**/*.json",
        "schema/migrations/*.log",
        "schema/migrations/*.sql",
        "schema/*.sql",
        "spikes/**/extract_*.py",
        "spikes/**/test_*.py",
        "spikes/**/evaluate_*.py",
        "spikes/**/build_truth*.py",
        "spikes/**/*.py",
        "spikes/**/sample.html",
        "spikes/**/sample.pdf",
        "spikes/**/*.pdf",
        "spikes/**/*.xlsx",
        "spikes/**/*.xls",
        "spikes/**/*.zip",
        "spikes/**/*.jpg",
        "spikes/**/*.txt",
        "spikes/**/*.csv",
        "spikes/**/*.json",
        "tests/test_*.py",
        "tests/conftest.py",
        "docs/*.md",
        "docs/plans/*.md",
        # GE (S1.11) — data contracts per docs/25
        "ge/README.md",
        "ge/great_expectations.yml",
        "ge/expectations/*.json",
        "ge/checkpoints/*.yml",
        "ge/plugins/custom_data_docs/*.py",
        "ge/scripts/*.sh",
        "ge/tests/*.py",
        "Makefile",
        ".github/workflows/*.yml",
        "source_registry/*",
        "evidence_pack/*",
    ]
    seen: set[Path] = set()
    for pat in patterns:
        for p in REPO.glob(pat):
            if not p.is_file() or p.stat().st_size == 0:
                continue
            if p == self_path:
                continue
            try:
                rel = p.relative_to(REPO)
            except ValueError:
                rel = Path(p.name)
            if rel == Path("evidence_pack/manifest.json"):
                continue
            seen.add(p)
    artifacts = []
    for p in sorted(seen, key=lambda x: str(x.relative_to(REPO))):
        rel = p.relative_to(REPO)
        artifacts.append({
            "path": str(rel),
            "size_bytes": p.stat().st_size,
            "sha256": sha256_of(p),
            "role": classify(rel),
        })
    return artifacts


# ---------- DB execution: ACTUALLY run psql, not wrap old log ----------

def run_db_apply() -> dict:
    """R3-G-5: 真跑 psql，应用 schema；不包装旧日志。

    R4-1: SKIP_PSQL/FORCE_PSQL 仅在 EVIDENCE_PACK_TEST_HOOKS=1 时生效。
    真实构建时若携带这些变量 → _check_hook_env_clean 提前拒绝。

    R5-A: 默认链式 apply `schema/01-core.sql` + `schema/migrations/*.sql`
    (按字典序)。不再只 apply 01-core.sql，否则 governance 测试缺对象。
    """
    sqls: list[Path] = []
    core = REPO / "schema" / "01-core.sql"
    if not core.exists():
        return {"exit_code": -1, "stderr": "schema/01-core.sql missing",
                "command": "psql ... -f schema/01-core.sql"}

    if not _test_hooks_enabled():
        # 真实构建路径（既无 SKIP_PSQL 也无 FORCE_PSQL），直接真跑
        pass
    elif os.environ.get("SKIP_PSQL") == "1":
        return {"exit_code": -1, "ddl_sha256": sha256_of(core),
                "ddl_path": "schema/01-core.sql",
                "skipped": True, "note": "SKIP_PSQL=1 — psql skipped in test",
                "command": "<skipped via SKIP_PSQL=1>"}
    elif os.environ.get("FORCE_PSQL") == "ok":
        return {"exit_code": 0, "ddl_sha256": sha256_of(core),
                "ddl_path": "schema/01-core.sql",
                "note": "FORCE_PSQL=ok — simulated success (fault-injection test)",
                "command": "<simulated via FORCE_PSQL=ok>", "forced": True}
    elif os.environ.get("FORCE_PSQL") == "fail":
        return {"exit_code": 1, "ddl_sha256": sha256_of(core),
                "ddl_path": "schema/01-core.sql",
                "note": "FORCE_PSQL=fail — simulated failure (fault-injection test)",
                "stderr_tail": "simulated psql apply failure", "forced": True,
                "command": "<simulated via FORCE_PSQL=fail>"}

    base = ["psql", "-h", "127.0.0.1", "-p", "55440", "-U", "postgres",
            "-d", "cegr_test"]
    env = {**os.environ, "PGPASSWORD": "postgres"}

    # R5-A: 按字典序收集全部 SQL（core + migrations/*.sql）
    migrations_dir = REPO / "schema" / "migrations"
    if migrations_dir.is_dir():
        for sql in sorted(migrations_dir.glob("*.sql")):
            sqls.append(sql)
    sqls.insert(0, core)
    ddl_shas = {str(p.relative_to(REPO)): sha256_of(p) for p in sqls}

    # 1) DROP schema（保证幂等）
    reset = subprocess.run(
        [*base, "-c", "DROP SCHEMA IF EXISTS cegr CASCADE"],
        cwd=str(REPO), capture_output=True, text=True, env=env, timeout=60)
    if reset.returncode != 0:
        return {"command": "DROP SCHEMA IF EXISTS cegr CASCADE",
                "exit_code": reset.returncode,
                "stdout_tail": reset.stdout[-2000:],
                "stderr_tail": reset.stderr[-2000:],
                "ddl_sha256": ddl_shas[str(core.relative_to(REPO))],
                "ddl_path": str(core.relative_to(REPO))}

    # 2) 链式 apply（任一失败即终止）
    last_stdout = ""
    last_stderr = ""
    for sql in sqls:
        rel = str(sql.relative_to(REPO))
        apply_cmd = [*base, "-v", "ON_ERROR_STOP=1", "-f", rel]
        proc = subprocess.run(apply_cmd, cwd=str(REPO), capture_output=True,
                              text=True, env=env, timeout=120)
        last_stdout = proc.stdout[-4000:]
        last_stderr = proc.stderr[-2000:]
        if proc.returncode != 0:
            return {
                "command": "PGPASSWORD=postgres " + " ".join(apply_cmd),
                "exit_code": proc.returncode,
                "stdout_tail": last_stdout,
                "stderr_tail": last_stderr,
                "ddl_sha256": ddl_shas[rel],
                "ddl_path": rel,
                "ddl_shas": ddl_shas,
            }

    return {
        "command": "DROP+chain psql apply (R5-A)",
        "exit_code": 0,
        "stdout_tail": last_stdout,
        "stderr_tail": last_stderr,
        "ddl_sha256": ddl_shas[str(core.relative_to(REPO))],
        "ddl_path": str(core.relative_to(REPO)),
        "ddl_shas": ddl_shas,
        "applied_sqls": [str(p.relative_to(REPO)) for p in sqls],
    }


def run_pytest() -> dict:
    """R3-G-1: 真跑 pytest，exit != 0 时整体 build 非 0 退出。

    R4-1: SKIP_PYTEST/FORCE_PYTEST 仅在 EVIDENCE_PACK_TEST_HOOKS=1 时生效。
    R4-1: 解析 stdout 统计 skipped；real run 中 skipped > 0 → 视为 failed。
    """
    if not _test_hooks_enabled():
        pass
    elif os.environ.get("SKIP_PYTEST") == "1":
        return {"command": "<skipped via SKIP_PYTEST=1>", "exit_code": -1,
                "stdout_tail": "", "stderr_tail": "skipped in test",
                "skipped": True}
    elif os.environ.get("FORCE_PYTEST") == "ok":
        return {"command": "<simulated via FORCE_PYTEST=ok>", "exit_code": 0,
                "stdout_tail": "", "stderr_tail": "",
                "note": "FORCE_PYTEST=ok — simulated success (fault-injection test)",
                "forced": True}
    elif os.environ.get("FORCE_PYTEST") == "fail":
        return {"command": "<simulated via FORCE_PYTEST=fail>", "exit_code": 2,
                "stdout_tail": "", "stderr_tail": "simulated pytest failure",
                "note": "FORCE_PYTEST=fail — simulated failure (fault-injection test)",
                "forced": True}

    cmd = [sys.executable, "-m", "pytest", "-q",
           "--tb=line", "--no-header", "-p", "no:cacheprovider"]
    proc = subprocess.run(cmd, cwd=str(REPO), capture_output=True, text=True,
                          timeout=900)
    return {
        "command": " ".join(cmd),
        "exit_code": proc.returncode,
        "stdout_tail": proc.stdout[-4000:],
        "stderr_tail": proc.stderr[-2000:],
    }


def _parse_pytest_stats(stdout_tail: str) -> dict:
    """R4-1: 解析 pytest 摘要行。失败返回 -1。"""
    passed = re.search(r"(\d+) passed", stdout_tail)
    failed = re.search(r"(\d+) failed", stdout_tail)
    skipped = re.search(r"(\d+) skipped", stdout_tail)
    return {
        "passed": int(passed.group(1)) if passed else 0,
        "failed": int(failed.group(1)) if failed else 0,
        "skipped": int(skipped.group(1)) if skipped else 0,
    }


# ---------- commit metadata (R3-G-6: no wall-clock, no absolute paths) ----------

def git_info() -> dict:
    def _run(args: list[str]) -> str:
        try:
            r = subprocess.run(["git", *args], cwd=str(REPO),
                               capture_output=True, text=True, timeout=15)
            return r.stdout.strip() if r.returncode == 0 else ""
        except Exception:
            return ""

    head = _run(["rev-parse", "HEAD"])
    commit_ts = _run(["log", "-1", "--format=%cI"])
    committed = bool(head)
    info = {
        "committed": committed,
        "commit_sha": head,
        "commit_sha_short": head[:12] if head else None,
        "commit_timestamp_utc": commit_ts,
        "branch": _run(["symbolic-ref", "--short", "HEAD"]),
    }
    if not committed:
        info["index_tree_sha"] = _run(["write-tree"])
    return info


# ---------- full artifact verification (R4-3) ----------

def verify_all_artifacts(artifacts: list[dict]) -> tuple[int, str]:
    """R4-3: 对每个 artifact 逐项验证存在/大小/SHA-256 + 路径唯一 + role_count。

    返回 (rc, message)。rc=0 表示全部通过；非 0 表示第一个失败原因。
    """
    seen_paths: set[str] = set()
    for a in artifacts:
        p = a.get("path", "")
        if not p:
            return 1, f"artifact 缺 path: {a}"
        if p.startswith("/") or os.path.isabs(p):
            return 1, f"artifact 路径非相对: {p}"
        if p in seen_paths:
            return 1, f"artifact 路径重复: {p}"
        seen_paths.add(p)
        target = REPO / p
        if not target.exists():
            return 1, f"artifact 磁盘缺失: {p}"
        actual_size = target.stat().st_size
        if actual_size != a.get("size_bytes"):
            return 1, (
                f"artifact 大小不一致 {p}: manifest={a['size_bytes']} "
                f"actual={actual_size}"
            )
        actual_sha = sha256_of(target)
        if actual_sha != a.get("sha256"):
            return 1, (
                f"artifact SHA 不一致 {p}: manifest={a['sha256'][:16]} "
                f"actual={actual_sha[:16]}"
            )
    return 0, f"verified {len(artifacts)} artifacts (full)"


# ---------- main ----------

def main() -> int:
    """R3-G + R4-1/R4-3: 任一前置失败 → 非 0 退出。

    判定顺序：
      1) 测试钩子变量污染（非 TEST_HOOKS） → return 6
      2) pytest 真实失败 / skipped > 0 / skipped 真跑 → return 2
      3) DB apply 失败 → return 5
      4) artifact 路径/计数/role_count 不一致 → return 3
      5) 任一 artifact 哈希/大小/存在性错误 → return 4
      6) EVIDENCE_PACK_TAMPER 模拟磁盘产物被改 → return 7
    """
    self_path = evidence_dir() / "manifest.json"

    # Step 1: R4-1 钩子门控
    rc = _check_hook_env_clean()
    if rc is not None:
        return rc

    # Step 2: R4-3 篡改门控（仅测试钩子启用时生效）
    tamper_target = os.environ.get("EVIDENCE_PACK_TAMPER")

    # Step 3: 真跑 pytest
    py_result = run_pytest()
    stats = _parse_pytest_stats(py_result.get("stdout_tail", ""))
    py_result["stats"] = stats
    if not py_result.get("skipped"):
        # real + forced 两种模式都需遵守 exit_code；forced 失败仍非 0
        if py_result["exit_code"] != 0:
            print(
                f"PYTEST FAILED exit={py_result['exit_code']}",
                file=sys.stderr,
            )
            print(py_result.get("stderr_tail", ""), file=sys.stderr)
            return 2
        if not py_result.get("forced") and stats["skipped"] > 0:
            # R4-1: 真跑发现 skipped > 0 → 拒绝；forced 模式不计
            print(
                f"PYTEST 含 skipped={stats['skipped']}（R4-1 反 skip-as-PASS）",
                file=sys.stderr,
            )
            return 2

    # Step 4: 真跑 psql（DB 可用时）
    db_result = run_db_apply()
    db_applied = db_result["exit_code"] == 0
    if db_result.get("skipped"):
        db_result["note"] = "SKIP_PSQL=1 — psql skipped in test (exit -1)"
    elif not db_applied:
        print(
            f"DB APPLY FAILED exit={db_result['exit_code']}",
            file=sys.stderr,
        )
        print(db_result.get("stderr_tail", ""), file=sys.stderr)
        return 5

    # Step 5: 收集 hash（不包含 manifest 自身）
    artifacts = collect_artifacts(self_path)

    # Step 6: R3-G-8: role_count 由代码生成
    role_count: dict[str, int] = {}
    for a in artifacts:
        role_count[a["role"]] = role_count.get(a["role"], 0) + 1

    # Step 7: R4-3: 模拟篡改（仅测试钩子启用且指定路径时）
    if _test_hooks_enabled() and tamper_target:
        # 用一个错误哈希覆盖目标 artifact（在内存里；真实磁盘不变）
        for a in artifacts:
            if a["path"] == tamper_target:
                a["sha256"] = "0" * 64
                a["_tampered"] = True
                break
        else:
            print(
                f"TAMPER target not in artifacts: {tamper_target}",
                file=sys.stderr,
            )
            return 7

    # Step 8: R3-G-6: commit metadata 替代 wall-clock + 绝对路径
    meta = git_info()

    manifest = {
        "schema_version": "1.1-R3G-R4",
        "stage": "Stage 0 Gate 0 R3 rework + R4 hardening",
        "commit": meta,
        "python_version": sys.version.split()[0],
        "platform": platform.platform(),
        "artifacts": artifacts,
        "artifact_count": len(artifacts),
        "role_count": role_count,
        "db_ddl_execution": db_result,
        "pytest_run": py_result,
    }

    # Step 9: 写 manifest
    out = self_path
    out.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n",
                   encoding="utf-8")
    print(f"Wrote {out}: {len(artifacts)} artifacts")

    # Step 10: R4-3: 写完后重新读取，逐项验证所有 artifact
    verify = json.loads(out.read_text(encoding="utf-8"))
    # 不允许 self 在 artifacts 中
    for a in verify["artifacts"]:
        if a["path"] == "evidence_pack/manifest.json":
            print(
                "VERIFY FAILED: manifest 把自身列入 artifacts",
                file=sys.stderr,
            )
            return 3
    # role_count 之和必须等于 artifact_count
    if sum(verify["role_count"].values()) != verify["artifact_count"]:
        print(
            f"VERIFY FAILED: role_count 之和 {sum(verify['role_count'].values())} "
            f"≠ artifact_count {verify['artifact_count']}",
            file=sys.stderr,
        )
        return 3

    rc, msg = verify_all_artifacts(verify["artifacts"])
    if rc != 0:
        print(msg, file=sys.stderr)
        return 4

    # Step 11: 兼容 FORCE_HASH=fail（仅测试钩子时生效）
    if _test_hooks_enabled() and os.environ.get("FORCE_HASH") == "fail":
        print("HASH MISMATCH (forced): FORCE_HASH=fail", file=sys.stderr)
        return 4

    print(msg)
    return 0


if __name__ == "__main__":
    sys.exit(main())