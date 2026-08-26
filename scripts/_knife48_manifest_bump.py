#!/usr/bin/env python3
"""Knife 48 bump script — Hubei EXCEL public-source connector (tasking 336).

落地：
  - scripts/auto_ingest_public_source.py (extended: extract_xlsx_tables +
    extract_tables dispatcher; Hubei pilot supported alongside NBS;
    CLI --pilot-domain + --pilot-category now route both HTML and XLSX)
  - tests/test_auto_ingest_public_source_s52.py (31 → 41 pytest cases;
  +10 Hubei cases: pilot_filter / dry-run / live-requires-confirm /
  xlsx_extract / empty-xlsx / dispatcher routing / WORM path /
  headless red-line / drift reuse / CANDIDATE_AUTO)
  - reviews/.../337-stage0-cc-hubei-excel-connector-receipt-20260826.md
  - 1 drift report from live probe (reviews/.../20260826T...sha-drift-
    tjj.hubei.gov.cn-PROVINCIAL_BULLETIN.md)

NEW_ARTIFACTS = +2 → 650 → 652

Recomputes role_count from artifacts (source of truth, per knife 16 fix).
The connector is a MODIFICATION (already in manifest from knife 46),
bump SKIPs it; pytest additions are inline edits (not separately counted).
"""
from __future__ import annotations

import hashlib
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
MANIFEST = ROOT / "evidence_pack" / "manifest.json"

NEW_ARTIFACTS = [
    (
        "scripts/_knife48_manifest_bump.py",
        "spike_helper",
    ),
    (
        "reviews/stage0-gate0-rework-2026-08-23/"
        "337-stage0-cc-hubei-excel-connector-receipt-20260826.md",
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