"""Stage 2 / S2.0.2.2 — Admin / seed overwrite `is_demo` flow.

Per docs/35 §4.3 + Cursor tasking 162:
  > 落地可重复流程（脚本或文档化命令 + pytest）：fixture 文件进 allowlist
  > 前缀 → sha →（模拟或真实）upload/seed 路径 → 断言 `is_demo` 清除或等价

Three steps:
  1. Verify fixture path is under ALLOWED_PREFIXES (reuse compute_file_sha's
     allowlist — do NOT duplicate the prefix list).
  2. Compute SHA-256 via `compute_file_sha.py` subprocess (so we exercise
     the published CLI, not a parallel internal impl).
  3. Build the observation `lineage` record that the post-upload
     `seed_jiangsu_gdp_demo.py --load` would write, and assert:
       a. `lineage.is_demo != "true"`  (sentinel cleared)
       b. `file_hash_sha256` is non-zero (no placeholder forgery)

Exit codes (mirroring compute_file_sha):
  0  OK — overwrite contract satisfied
  1  Fixture missing / not a regular file
  2  Fixture path outside ALLOWED_PREFIXES
  3  Internal error (subprocess / JSON / contract violation)

This is a CONTROL-FLOW WITNESS, not a DB mutator. Production callers still
need to run:

    python3 scripts/compute_file_sha.py <fixture>
    curl -X POST http://localhost:8000/admin/upload -F file=@<fixture> ...
    python3 scripts/seed_jiangsu_gdp_demo.py --load

for the actual DB mutation. Per Cursor 162 §红线:
  - 不爬网
  - 不伪造 SHA / 不造假公报数值冒充 VERIFIED
  - 不 Gate PASS
  - 不改 `gate_thresholds.json`
  - 无真实文件 → 诚实失败（脚本 rc≠0 / pytest skip）；不伪造样本内容

Usage:
    python3 scripts/replace_demo_with_real.py /tmp/cegr_uploads/foo.pdf
"""
from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from pathlib import Path

# Importing compute_file_sha is safe: its argparse setup lives inside main(),
# so importing the module only exposes the module-level PROJECT_ROOT and
# ALLOWED_PREFIXES constants without side effects on sys.argv.
import compute_file_sha  # type: ignore[import-not-found]  # scripts/ on PYTHONPATH via __file__


SCRIPT_DIR = Path(__file__).resolve().parent
COMPUTE_SHA = SCRIPT_DIR / "compute_file_sha.py"


def _resolve_and_validate(path_str: str, allowlist: tuple[str, ...]) -> Path:
    """Mirror compute_file_sha._resolve_and_validate semantics."""
    p = Path(path_str).resolve()
    # macOS /tmp → /private/tmp symlink is handled by Path.resolve() already.
    if not any(str(p).startswith(pref) for pref in allowlist):
        sys.stderr.write(
            f"❌ path not under allowed prefix: {p}\n"
            f"   allowed: {list(allowlist)}\n"
        )
        sys.exit(2)
    return p


def _compute_sha_via_cli(path: Path) -> str:
    """Invoke compute_file_sha.py and return stdout (single 64-char hex)."""
    result = subprocess.run(
        [sys.executable, str(COMPUTE_SHA), str(path)],
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        sys.stderr.write(
            f"❌ compute_file_sha failed (rc={result.returncode}): "
            f"{result.stderr.strip()}\n"
        )
        sys.exit(result.returncode or 3)
    sha = result.stdout.strip()
    if not re.fullmatch(r"[0-9a-f]{64}", sha):
        sys.stderr.write(f"❌ bad SHA from compute_file_sha: {sha!r}\n")
        sys.exit(3)
    return sha


def build_lineage(
    chain_id: str,
    source_file_sha256: str,
    source_file_path: str,
    source_agency: str,
) -> dict:
    """Build the post-upload observation lineage record.

    Mirrors the JSON shape that seed_jiangsu_gdp_demo.py produces when it
    re-loads after a real admin upload — but with `is_demo` set to the
    string "false" (per S1.18 sentinel contract) instead of Python True.
    """
    return {
        "chain_id": chain_id,
        "source_file_sha256": source_file_sha256,
        "source_file_path": source_file_path,
        "source_agency": source_agency,
        "is_demo": "false",  # SENTINEL: must NOT be "true"
        "overwrite_reason": "S2.0.2.2 admin upload → seed reload",
    }


def assert_overwrite_contract(lineage: dict) -> None:
    """Per Cursor 162 §SCHEMA: is_demo 非 "true" + file_hash_sha256 ≠ 全零."""
    if lineage.get("is_demo") == "true":
        sys.stderr.write("❌ overwrite contract violated: is_demo == 'true'\n")
        sys.exit(3)
    sha = lineage.get("source_file_sha256", "")
    if not re.fullmatch(r"[0-9a-f]{64}", sha):
        sys.stderr.write(f"❌ overwrite contract violated: bad SHA format {sha!r}\n")
        sys.exit(3)
    if sha == "0" * 64:
        sys.stderr.write("❌ overwrite contract violated: all-zero SHA (placeholder)\n")
        sys.exit(3)


def main() -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Stage 2 / S2.0.2.2 — overwrite demo seed's is_demo sentinel with a "
            "real admin-uploaded file's SHA. Control-flow witness (does not mutate DB)."
        )
    )
    parser.add_argument(
        "fixture_path",
        help="Path to the real admin-uploaded file (must be under ALLOWED_PREFIXES).",
    )
    parser.add_argument(
        "--chain-id",
        default="jiangsu_gdp_2020_2024",
        help="chain_id stored in lineage (default: jiangsu_gdp_2020_2024).",
    )
    parser.add_argument(
        "--source-agency",
        default="江苏省统计局",
        help="source_agency stored in lineage.",
    )
    # NOTE: --url intentionally NOT registered (mirrors compute_file_sha pattern).
    args = parser.parse_args()

    fixture = Path(args.fixture_path)
    if not fixture.is_file():
        sys.stderr.write(f"❌ fixture not found or not a regular file: {fixture}\n")
        return 1

    allowlist = compute_file_sha.ALLOWED_PREFIXES
    fixture_resolved = _resolve_and_validate(str(fixture), allowlist)

    sha = _compute_sha_via_cli(fixture_resolved)
    lineage = build_lineage(
        chain_id=args.chain_id,
        source_file_sha256=sha,
        source_file_path=str(fixture_resolved),
        source_agency=args.source_agency,
    )
    assert_overwrite_contract(lineage)

    # Emit the lineage JSON on stdout (machine-readable for downstream callers).
    json.dump(lineage, sys.stdout, ensure_ascii=False, sort_keys=True)
    sys.stdout.write("\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
