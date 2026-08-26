#!/usr/bin/env python3
"""Knife 47 bump script — SHA drift candidate path + one NBS live probe (tasking 333).

落地：
  - scripts/auto_ingest_public_source.py (extended: ShaDrift exception +
    write_sha_drift_report + main() drift branch with WORM archive +
    CANDIDATE_AUTO lineage)
  - tests/test_auto_ingest_public_source_s52.py (26 → 31 pytest cases;
  +5 drift cases: 5-field report / CANDIDATE_AUTO / no-registry-write /
  archive-still-written / no-DictWriter)
  - reviews/.../334-stage0-cc-live-probe-sha-drift-receipt-20260826.md

NEW_ARTIFACTS = +2 → 648 → 650

Recomputes role_count from artifacts (source of truth, per knife 16 fix).
The connector (scripts/auto_ingest_public_source.py) is a MODIFICATION of
knife 46's artifact, not a new artifact — already in manifest, skipped at
bump time. Pytest additions are inline edits to the existing test file;
not separately counted in manifest.
"""
from __future__ import annotations

import hashlib
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
MANIFEST = ROOT / "evidence_pack" / "manifest.json"

NEW_ARTIFACTS = [
    (
        "scripts/auto_ingest_public_source.py",
        "spike_helper",
    ),
    (
        "scripts/_knife47_manifest_bump.py",
        "spike_helper",
    ),
    (
        "reviews/stage0-gate0-rework-2026-08-23/"
        "334-stage0-cc-live-probe-sha-drift-receipt-20260826.md",
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
        print(f"OK obs: {new_count}")

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