#!/usr/bin/env python3
"""Knife 37 bump script — S2.7-b person/tenure demo 接驳 (tasking 302).

落地：
  - frontend/lib/mart_city_demo.ts (修改：buildMartRelatedPersons() +
    MART_CITY_DEMO_RELATED_PERSONS_PER_CITY/TOTAL 常量；10 城 × 2 行 = 20)
  - frontend/app/components/CityPageMart.tsx (修改：相关人物 demo 渲染区块 +
    data-testid 守门)
  - tests/test_mart_related_persons_demo_s302.py (NEW: 15 pytest cases)
  - scripts/_knife37_manifest_bump.py (本脚本)
  - reviews/.../303-stage0-cc-s27b-person-tenure-demo-receipt-20260826.md

NEW_ARTIFACTS = +3 → 625 → 628

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
        "tests/test_mart_related_persons_demo_s302.py",
        "schema_negative_test",
    ),
    (
        "scripts/_knife37_manifest_bump.py",
        "spike_helper",
    ),
    (
        "reviews/stage0-gate0-rework-2026-08-23/"
        "303-stage0-cc-s27b-person-tenure-demo-receipt-20260826.md",
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

    # Refresh sha256 for the 2 modified files (mart_city_demo.ts + CityPageMart.tsx)
    for rel in (
        "frontend/lib/mart_city_demo.ts",
        "frontend/app/components/CityPageMart.tsx",
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