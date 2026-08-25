#!/usr/bin/env python3
"""S2.0.2.1 — Compute SHA-256 of a local file for source_document.file_hash_sha256.

Per docs/35 §4.2 (Stage 2 / S2.0.2 真实 SHA 启动规划) and tasking 157 §SCHEMA.

Contract:
  - Accept exactly ONE positional argument: local file path.
  - Compute SHA-256, print 64-char lowercase hex on stdout, exit 0.
  - Refuse any HTTP / URL input: argparse does NOT register --url. Any
    flag-shaped argument besides --help / -h triggers argparse exit 2.
  - Path allowlist (must satisfy at least one AFTER resolve()):
      * /tmp/cegr_uploads/...        (admin upload落盘目录)
      * /private/tmp/cegr_uploads/... (macOS /tmp → /private/tmp symlink)
      * data/seed_archives/...        (dev fixture)
  - Exit codes:
      0 = OK, printed SHA on stdout
      1 = path exists but is not a regular file (or missing)
      2 = path resolves outside the allowlist
      3 = argparse error (caught and re-emitted so tests can assert)

Red lines honored:
  - No HTTP fetch. No URL option. No --stdin streaming (out of scope).
  - No silent success on missing file or out-of-prefix path.
  - Per tasking 157 §红线: "本刀不强制交付真实江苏文件（无文件诚实失败即可）".
"""
from __future__ import annotations

import argparse
import hashlib
import sys
from pathlib import Path

# Allowlist prefixes. Both /tmp and /private/tmp are required because macOS
# resolves /tmp → /private/tmp at the filesystem layer (per Cursor 156 §1).
# We compare against the *resolved* path so symlink games don't bypass the gate.
# The data/seed_archives/ prefix is built as an absolute path anchored to the
# script's own location (PROJECT_ROOT/scripts/compute_file_sha.py), so the
# check works regardless of the caller's CWD.
PROJECT_ROOT = Path(__file__).resolve().parent.parent
ALLOWED_PREFIXES = (
    "/tmp/cegr_uploads/",
    "/private/tmp/cegr_uploads/",
    str(PROJECT_ROOT / "data" / "seed_archives") + "/",
)


def _resolve_and_validate(path_str: str) -> Path:
    """Resolve the path; return it if and only if it lives under an allowed
    prefix. Otherwise print an error and raise SystemExit(2).

    Uses Path.resolve(strict=False) so that a missing path is still resolved
    against the symlink layer (catches the /tmp → /private/tmp case before
    the existence check).
    """
    p = Path(path_str).resolve()
    resolved = str(p)
    if not any(resolved.startswith(pref) for pref in ALLOWED_PREFIXES):
        print(
            f"❌ {resolved} is not under any allowed prefix:\n"
            + "\n".join(f"   - {p}" for p in ALLOWED_PREFIXES)
            + "\nTip: put the file under /tmp/cegr_uploads/ (admin upload) "
            + "or data/seed_archives/ (dev fixture).",
            file=sys.stderr,
        )
        raise SystemExit(2)
    return p


def _sha256_of_file(path: Path, chunk_size: int = 65536) -> str:
    """Stream the file through SHA-256. Returns lowercase hex (64 chars)."""
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(chunk_size), b""):
            h.update(chunk)
    return h.hexdigest()


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="compute_file_sha",
        description=(
            "Compute SHA-256 of a local file for source_document.file_hash_sha256. "
            "Refuses HTTP / URL input; path must be under an allowed prefix."
        ),
    )
    parser.add_argument(
        "path",
        help="local file path (must be under /tmp/cegr_uploads/, "
        "/private/tmp/cegr_uploads/, or data/seed_archives/)",
    )
    # NOTE: --url is intentionally NOT registered. argparse will exit(2) if
    # a caller tries --url, which is exactly the "防误用门槛" docs/35 §4.2
    # prescribes.

    try:
        args = parser.parse_args(argv)
    except SystemExit as e:
        # argparse already printed usage; tests can assert rc==2 for --url.
        return int(e.code) if isinstance(e.code, int) else 3

    path = _resolve_and_validate(args.path)

    if not path.is_file():
        print(f"❌ {path} is not a regular file (missing or directory)", file=sys.stderr)
        return 1

    sha = _sha256_of_file(path)
    print(sha)
    return 0


if __name__ == "__main__":
    sys.exit(main())