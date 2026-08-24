"""Stage 0 pytest configuration (R5-A: 默认 apply schema migrations).

确保：在 pytest 启动时（session 级别），若 DB 可达，自动链式 apply
schema/01-core.sql + schema/migrations/*.sql（按字典序），从而：
  - 测试不需要手动跑 `psql -f ...` 后才能 pytest
  - 缺 migration 002 时 governance 测试自然报红（assertion 失败 → pytest fail）
  - 已 apply 过 002 时 governance 测试正常 pass

约束：
  - 仅在 DB 可达且 psycopg 驱动存在时尝试 apply；否则跳过（让各测试自行 fail）
  - STAGE0_SKIP_SCHEMA_APPLY=1 可禁用本机制（例如已经手动 apply 过，且想保持数据）
  - 幂等：每次 session 启动都会 DROP+apply，避免脏数据
  - 不会修改仓库文件；仅对本地测试 DB（cegr_test）做操作
"""
from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parent.parent
SCHEMA_DIR = REPO / "schema"
MIGRATIONS_DIR = SCHEMA_DIR / "migrations"

DSN = os.environ.get(
    "STAGE0_DSN",
    "host=127.0.0.1 port=55440 user=postgres dbname=cegr_test",
)

# 兼容 .ci：可显式禁用自动 apply
SKIP_SCHEMA_APPLY = os.environ.get("STAGE0_SKIP_SCHEMA_APPLY") == "1"

# 测试用例中显式声明 "本测试不依赖 DB 已 apply" 的 marker。
# 当前未启用；保留以备未来扩展。
requires_db = pytest.mark.requires_db


def _parse_dsn(dsn: str) -> dict[str, str]:
    """解析 key=value 形式的 DSN 串。"""
    out: dict[str, str] = {}
    for token in dsn.split():
        if "=" in token:
            k, v = token.split("=", 1)
            out[k] = v
    return out


def _psql_base_args(dsn: str) -> list[str]:
    parts = _parse_dsn(dsn)
    return [
        "psql",
        "-h", parts.get("host", "127.0.0.1"),
        "-p", parts.get("port", "55440"),
        "-U", parts.get("user", "postgres"),
        "-d", parts.get("dbname", "cegr_test"),
        "-v", "ON_ERROR_STOP=1",
    ]


def _db_reachable(dsn: str) -> bool:
    """快速 ping DB（connect + close + SELECT 1）；失败返回 False。"""
    try:
        import psycopg
    except ImportError:
        try:
            import psycopg2 as psycopg  # type: ignore
        except ImportError:
            return False
    try:
        with psycopg.connect(dsn, connect_timeout=3) as c:
            with c.cursor() as cur:
                cur.execute("SELECT 1")
                cur.fetchone()
        return True
    except Exception:
        return False


def _collect_migrations() -> list[Path]:
    """按字典序返回所有需 apply 的 SQL：01-core.sql 在前，之后 migrations/*.sql。"""
    sqls: list[Path] = []
    core = SCHEMA_DIR / "01-core.sql"
    if core.exists():
        sqls.append(core)
    if MIGRATIONS_DIR.is_dir():
        for sql in sorted(MIGRATIONS_DIR.glob("*.sql")):
            sqls.append(sql)
    return sqls


def _apply_all_migrations(dsn: str) -> tuple[bool, str]:
    """DROP cegr + apply 01-core.sql + 所有 migrations/*.sql。

    Returns (ok, message). ok=False 时 message 含 stderr。
    """
    base_args = _psql_base_args(dsn)
    env = {**os.environ, "PGPASSWORD": "postgres"}

    # 1. DROP schema（清理脏数据，保证幂等）
    reset = subprocess.run(
        base_args + ["-c", "DROP SCHEMA IF EXISTS cegr CASCADE"],
        env=env, capture_output=True, text=True, timeout=60,
    )
    if reset.returncode != 0:
        return False, f"DROP failed: {reset.stderr.strip()[:500]}"

    # 2. apply 链
    for sql in _collect_migrations():
        rel = sql.relative_to(REPO)
        proc = subprocess.run(
            base_args + ["-f", str(rel)],
            cwd=str(REPO), env=env,
            capture_output=True, text=True, timeout=180,
        )
        if proc.returncode != 0:
            msg = (
                f"APPLY failed for {rel}: rc={proc.returncode}\n"
                f"stderr: {proc.stderr.strip()[:500]}\n"
                f"stdout-tail: {proc.stdout[-500:]}"
            )
            return False, msg
    return True, f"applied {len(_collect_migrations())} sql files (DROP+chain)"


def _stage0_apply_schema_once() -> None:
    """session-startup 钩子：DB 可达时链式 apply 全部 schema。

    不可达 / 失败时只记录不 raise —— 让具体测试自行报告。
    """
    if SKIP_SCHEMA_APPLY:
        print(
            "[conftest] STAGE0_SKIP_SCHEMA_APPLY=1 — 跳过自动 apply",
            file=sys.stderr,
        )
        return
    if not _db_reachable(DSN):
        print(
            f"[conftest] DB 不可达 ({DSN}) — 跳过自动 apply；"
            f"依赖 DB 的测试将自行 fail",
            file=sys.stderr,
        )
        return
    ok, msg = _apply_all_migrations(DSN)
    print(f"[conftest] schema apply: {msg}", file=sys.stderr)
    if not ok:
        # 仍不 raise；让具体测试报告。记录到 sys.stderr 便于排查。
        print(f"[conftest] !!! schema apply 失败 !!!", file=sys.stderr)


@pytest.fixture(autouse=True, scope="session")
def _stage0_session_bootstrap():
    """session 级 autouse fixture：触发一次 schema apply。"""
    _stage0_apply_schema_once()
    yield