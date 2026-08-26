#!/usr/bin/env python3
"""Knife 34 bump script — mart demo-join (tasking 293).

落地：
  - dbt/models/marts/mart_city_evidence_chain.sql (修改：WHERE FALSE → 60 demo 行)
  - dbt/models/marts/mart_city_seven_dim_overview.sql (修改：WHERE FALSE → 70 demo 行)
  - tests/test_mart_city_dbt_skel_s27bf.py (修改：10 → 20 pytest cases；新增 demo-join 守门)
  - scripts/_knife34_manifest_bump.py (本脚本)
  - reviews/.../294-stage0-cc-s27b-full-mart-demo-join-receipt-20260826.md (回执)

NEW_ARTIFACTS = +3 → 618 → 621

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
        "scripts/_knife34_manifest_bump.py",
        "spike_helper",
    ),
    (
        "reviews/stage0-gate0-rework-2026-08-23/"
        "294-stage0-cc-s27b-full-mart-demo-join-receipt-20260826.md",
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

    # Refresh sha256 for the 2 modified mart SQL files + the modified pytest
    # (since their content has changed since they were added in knife 32).
    for rel in (
        "dbt/models/marts/mart_city_evidence_chain.sql",
        "dbt/models/marts/mart_city_seven_dim_overview.sql",
        "tests/test_mart_city_dbt_skel_s27bf.py",
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