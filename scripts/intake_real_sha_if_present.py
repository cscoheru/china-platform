#!/usr/bin/env python3
"""Stage 2 / S2.0.2.3 — Real SHA intake live (control-flow witness).

Per docs/48 + tasking 290 (real SHA intake live).

This is NOT a DB mutator. It is a single-step intake witness:
  1. Scan allowlist (`/tmp/cegr_uploads/`, `/private/tmp/cegr_uploads/`,
     `data/seed_archives/`) for any user-provided files.
  2. For each candidate file:
       a. Compute SHA-256 (delegated to scripts/compute_file_sha.py).
       b. Build lineage record with `is_demo != "true"` (per S1.18 sentinel).
       c. Tag fixture files (filename contains 'fixture' or starts with 'test_',
          or content has 'NOT a forged' / 'placeholder bytes', or <1 KiB with
          mtime within 7 days) as CONTROL_FLOW_FIXTURE, NOT O1 candidates.
  3. Emit a JSON manifest on stdout with the per-file verdict and an overall
     intake_status:
       - WAITING_FILE     (no candidates / only fixtures)
       - CANDIDATE_FOUND  (≥1 candidate but no user `--confirm-o1`)
       - O1_INTAKED       (≥1 candidate AND user passed `--confirm-o1=PATH`)
       - CONTRACT_VIOLATION (candidate failed is_demo / SHA contract)
  4. Exit codes:
       0 = WAITING_FILE or O1_INTAKED (both are honest endpoints)
       2 = CANDIDATE_FOUND (user-confirm gate open; not a red-line fail)
       3 = CONTRACT_VIOLATION
       4 = internal error

Red lines honored (per tasking 290 §红线 + docs/34 §1):
  - No HTTP fetch / crawl.
  - No SHA forgery. SHA comes only from `compute_file_sha.py`.
  - No fixture-as-O1. Fixtures get CONTROL_FLOW_FIXTURE tag; rc still 0
    but intake_status stays WAITING_FILE.
  - No Gate / O1 PASS without explicit user `--confirm-o1`.
  - No `gate_thresholds.json` edit.

Usage:
    python3 scripts/intake_real_sha_if_present.py
    python3 scripts/intake_real_sha_if_present.py --confirm-o1=PATH
"""
from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
import time
from pathlib import Path
from typing import Any

import compute_file_sha  # type: ignore[import-not-found]  # scripts/ on PYTHONPATH via __file__

SCRIPT_DIR = Path(__file__).resolve().parent
COMPUTE_SHA = SCRIPT_DIR / "compute_file_sha.py"

PROJECT_ROOT = Path(__file__).resolve().parent.parent
SEED_ARCHIVES = PROJECT_ROOT / "data" / "seed_archives"

# Reuse compute_file_sha's allowlist (do NOT duplicate prefix list).
ALLOWED_PREFIXES = compute_file_sha.ALLOWED_PREFIXES

# Fixture detection thresholds.
MIN_CANDIDATE_SIZE_BYTES = 1024
CONTROL_FLOW_MTIME_WINDOW_S = 7 * 24 * 3600
CANDIDATE_MTIME_WINDOW_S = 90 * 24 * 3600
FIXTURE_NAME_PATTERNS = (
    re.compile(r"fixture", re.IGNORECASE),
    re.compile(r"^test_|_test\.", re.IGNORECASE),
)
FIXTURE_CONTENT_MARKERS = (
    b"NOT a forged",
    b"placeholder bytes",
)

# Sentinel: must NOT be `"true"` (per S1.18 + replace_demo_with_real contract).
ZERO_SHA = "0" * 64
SHA_PATTERN = re.compile(r"^[0-9a-f]{64}$")


def _is_fixture(path: Path) -> tuple[bool, str]:
    """Return (is_fixture, reason). True ⇒ control-flow fixture, NOT O1."""
    name = path.name
    for pat in FIXTURE_NAME_PATTERNS:
        if pat.search(name):
            return True, f"name pattern matched: {pat.pattern}"
    try:
        size = path.stat().st_size
    except OSError:
        return False, "stat failed"
    if size < MIN_CANDIDATE_SIZE_BYTES:
        mtime = path.stat().st_mtime
        age = time.time() - mtime
        if age <= CONTROL_FLOW_MTIME_WINDOW_S:
            return True, (
                f"size={size} < 1KiB and mtime={int(age)}s ago (within 7d window)"
            )
    try:
        with path.open("rb") as f:
            head = f.read(512)
    except OSError:
        return False, "head read failed"
    for marker in FIXTURE_CONTENT_MARKERS:
        if marker in head:
            return True, f"content marker: {marker!r}"
    return False, "passed all fixture checks"


def _is_candidate_window(path: Path) -> tuple[bool, str]:
    """Real candidate requires size ≥ 1 KiB and recent mtime (≤ 90 d)."""
    try:
        st = path.stat()
    except OSError as e:
        return False, f"stat failed: {e}"
    if st.st_size < MIN_CANDIDATE_SIZE_BYTES:
        return False, f"size {st.st_size} < {MIN_CANDIDATE_SIZE_BYTES}"
    age = time.time() - st.st_mtime
    if age > CANDIDATE_MTIME_WINDOW_S:
        return False, f"mtime {int(age)}s old > 90d window"
    return True, "size ≥ 1KiB and mtime within 90d"


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
        raise SystemExit(result.returncode or 4)
    sha = result.stdout.strip()
    if not SHA_PATTERN.fullmatch(sha):
        sys.stderr.write(f"❌ bad SHA from compute_file_sha: {sha!r}\n")
        raise SystemExit(4)
    return sha


def _scan_allowlist() -> list[Path]:
    """Enumerate regular files under all allowed prefixes (best-effort)."""
    out: list[Path] = []
    for pref in ALLOWED_PREFIXES:
        root = Path(pref)
        if not root.exists():
            continue
        try:
            for child in root.rglob("*"):
                if child.is_file():
                    out.append(child)
        except OSError as e:
            sys.stderr.write(f"⚠ scan error in {root}: {e}\n")
    return sorted(out)


def _build_lineage(
    *,
    chain_id: str,
    sha: str,
    path: Path,
    source_agency: str,
    intake_status: str,
    intake_ts: str,
    is_fixture: bool,
    fixture_reason: str,
    candidate_window_ok: bool,
    candidate_window_reason: str,
) -> dict[str, Any]:
    """Build the post-upload observation lineage record (per docs/48 §5)."""
    lineage: dict[str, Any] = {
        "chain_id": chain_id,
        "source_file_sha256": sha,
        "source_file_path": str(path),
        "source_agency": source_agency,
        "is_demo": "false",  # SENTINEL: must NOT be "true"
        "overwrite_reason": "S2.0.2.3 intake_real_sha_if_present.py",
        "intake_status": intake_status,
        "intake_ts": intake_ts,
        "control_flow_fixture": is_fixture,
        "fixture_reason": fixture_reason,
        "candidate_window_ok": candidate_window_ok,
        "candidate_window_reason": candidate_window_reason,
    }
    return lineage


def _assert_contract(lineage: dict[str, Any]) -> None:
    """Per docs/48 §5: is_demo != "true" + SHA is valid non-zero 64-char hex."""
    if lineage.get("is_demo") == "true":
        raise ValueError(f"contract violation: is_demo == 'true' for {lineage}")
    sha = lineage.get("source_file_sha256", "")
    if not SHA_PATTERN.fullmatch(sha):
        raise ValueError(f"contract violation: bad SHA format {sha!r}")
    if sha == ZERO_SHA:
        raise ValueError(f"contract violation: all-zero SHA for {lineage}")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="intake_real_sha_if_present",
        description=(
            "Stage 2 / S2.0.2.3 — Scan allowlist for user-uploaded files; "
            "compute SHA + lineage; emit WAITING_FILE / CANDIDATE_FOUND / "
            "O1_INTAKED verdict. NEVER auto-closes O1 without "
            "`--confirm-o1=PATH`."
        ),
    )
    parser.add_argument(
        "--chain-id",
        default="jiangsu_gdp_2020_2024",
        help="chain_id for candidate lineage records",
    )
    parser.add_argument(
        "--source-agency",
        default="江苏省统计局",
        help="source_agency for candidate lineage records",
    )
    parser.add_argument(
        "--confirm-o1",
        default=None,
        metavar="PATH",
        help=(
            "EXPLICIT user confirmation that PATH is the O1 sample. "
            "Without this flag, candidates get status=CANDIDATE_FOUND; "
            "O1 is NEVER auto-closed."
        ),
    )
    # NOTE: --url intentionally NOT registered (mirrors compute_file_sha).
    args = parser.parse_args(argv)

    files = _scan_allowlist()
    intake_ts = time.strftime("%Y-%m-%dT%H:%M:%S%z", time.localtime())

    verdicts: list[dict[str, Any]] = []
    candidates: list[dict[str, Any]] = []
    fixtures: list[dict[str, Any]] = []
    contract_violations: list[dict[str, Any]] = []

    for f in files:
        try:
            sha = _compute_sha_via_cli(f)
        except SystemExit as e:
            sys.stderr.write(f"⚠ skipping {f.name} (sha fail rc={e.code})\n")
            continue

        is_fix, fix_reason = _is_fixture(f)
        cand_ok, cand_reason = _is_candidate_window(f)

        # Provisional status: WAITING_FILE / CANDIDATE_FOUND will be
        # finalized below based on the per-file role.
        status = (
            "WAITING_FILE" if is_fix
            else ("CANDIDATE_FOUND" if cand_ok else "WAITING_FILE")
        )

        lineage = _build_lineage(
            chain_id=args.chain_id,
            sha=sha,
            path=f,
            source_agency=args.source_agency,
            intake_status=status,
            intake_ts=intake_ts,
            is_fixture=is_fix,
            fixture_reason=fix_reason,
            candidate_window_ok=cand_ok,
            candidate_window_reason=cand_reason,
        )

        try:
            _assert_contract(lineage)
        except ValueError as e:
            contract_violations.append(
                {
                    "file": str(f),
                    "error": str(e),
                    "lineage": lineage,
                }
            )
            continue

        verdict = {
            "file": str(f),
            "size_bytes": f.stat().st_size,
            "sha256": sha,
            "is_fixture": is_fix,
            "fixture_reason": fix_reason,
            "candidate_window_ok": cand_ok,
            "candidate_window_reason": cand_reason,
            "intake_status": status,
            "lineage": lineage,
        }
        verdicts.append(verdict)
        if is_fix:
            fixtures.append(verdict)
        elif cand_ok:
            candidates.append(verdict)

    # Finalize overall status.
    if contract_violations:
        overall_status = "CONTRACT_VIOLATION"
        rc = 3
    elif candidates and args.confirm_o1:
        confirm_path = Path(args.confirm_o1).resolve()
        matched = [
            c for c in candidates if Path(c["file"]).resolve() == confirm_path
        ]
        if matched:
            for c in matched:
                c["lineage"]["intake_status"] = "O1_INTAKED"
                c["intake_status"] = "O1_INTAKED"
            overall_status = "O1_INTAKED"
            rc = 0
        else:
            overall_status = "CANDIDATE_FOUND"
            rc = 2
            sys.stderr.write(
                f"❌ --confirm-o1={confirm_path} did not match any candidate\n"
            )
    elif candidates:
        overall_status = "CANDIDATE_FOUND"
        rc = 2
    else:
        overall_status = "WAITING_FILE"
        rc = 0

    summary = {
        "intake_ts": intake_ts,
        "overall_status": overall_status,
        "files_scanned": len(files),
        "n_fixtures": len(fixtures),
        "n_candidates": len(candidates),
        "n_contract_violations": len(contract_violations),
        "verdicts": verdicts,
        "contract_violations": contract_violations,
        "red_lines": {
            "no_http_fetch": True,
            "no_sha_forgery": True,
            "no_fixture_as_o1": True,
            "no_auto_o1_close": args.confirm_o1 is None,
            "no_gate_thresholds_edit": True,
        },
    }

    json.dump(summary, sys.stdout, ensure_ascii=False, sort_keys=True)
    sys.stdout.write("\n")
    return rc


if __name__ == "__main__":
    sys.exit(main())