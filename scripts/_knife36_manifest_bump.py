#!/usr/bin/env python3
"""Knife 36 bump script — docs/45 mart/intake/parity refresh (tasking 299).

落地：
  - docs/45-stage2-s210-lite-gate2-review-index-20260826.md (修改：§2 #1 +
    §3 O1 详细 + §5.5 OPEN + §6 + §6.1 + §6.2 反映 288/291/294/297 收口)
  - scripts/_knife36_manifest_bump.py (本脚本)
  - reviews/.../300-stage0-cc-docs45-mart-intake-parity-refresh-receipt-20260826.md

NEW_ARTIFACTS = +3 → 623 → 626

Recomputes role_count from artifacts (source of truth, per knife 16 fix).
"""
from __future__ import annotations

import hashlib
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
MANIFEST = ROOT / "evidence_pack" / "manifest.json"

NEW_ARTIFACTS = [
    (
        "scripts/_knife36_manifest_bump.py",
        "spike_helper",
    ),
    (
        "reviews/stage0-gate0-rework-2026-08-23/"
        "300-stage0-cc-docs45-mart-intake-parity-refresh-receipt-20260826.md",
        "documentation",
    ),
]


def sha256(path: pathlib.Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            h.update(chunk)
    return h.hexdigest()


def main() -> int:
    import json

    if not MANIFEST.exists():
        print(f"ERR: {MANIFEST} not found", file=sys.stderr)
        return 1

    with open(MANIFEST) as f:
        m = json.load(f)

    artifacts = m.setdefault("artifacts", [])
    paths = {a.get("path") for a in artifacts}

    added = 0
    for rel, role in NEW_ARTIFACTS:
        p = ROOT / rel
        if not p.exists():
            print(f"ERR: {rel} not on disk", file=sys.stderr)
            return 1
        if rel in paths:
            print(f"SKIP: {rel}")
            continue
        size = p.stat().st_size
        digest = sha256(p)
        artifacts.append(
            {"path": rel, "size_bytes": size, "sha256": digest, "role": role}
        )
        added += 1
        print(f"ADD: {rel} ({size} bytes, sha={digest[:8]})")

    # Refresh sha256 for the modified docs/45 file
    for rel in (
        "docs/45-stage2-s210-lite-gate2-review-index-20260826.md",
    ):
        p = ROOT / rel
        if not p.exists():
            continue
        size = p.stat().st_size
        digest = sha256(p)
        for a in artifacts:
            if a.get("path") == rel:
                old_sha = a.get("sha256", "")[:8]
                a["size_bytes"] = size
                a["sha256"] = digest
                print(f"REFRESH: {rel} (sha {old_sha} → {digest[:8]})")
                break

    new_rc: dict[str, int] = {}
    for a in artifacts:
        r = a.get("role", "<none>")
        new_rc[r] = new_rc.get(r, 0) + 1
    m["role_count"] = new_rc

    new_count = len(artifacts)
    old_count = m.get("artifact_count")
    if old_count != new_count:
        m["artifact_count"] = new_count
        print(f"UPDATE artifact_count: {old_count} → {new_count}")
    else:
        print(f"OK artifact_count: {new_count}")

    sum_rc = sum(new_rc.values())
    assert sum_rc == new_count, (
        f"INVARIANT BROKEN: sum(role_count)={sum_rc} != artifact_count={new_count}"
    )
    print(
        f"INVARIANT: sum(role_count)={sum_rc} == "
        f"artifact_count={new_count} == len(artifacts)={new_count}"
    )

    with open(MANIFEST, "w") as f:
        json.dump(m, f, indent=2, ensure_ascii=False, sort_keys=True)
        f.write("\n")

    print(f"OK manifest updated; added {added} artifacts")
    return 0


if __name__ == "__main__":
    sys.exit(main())