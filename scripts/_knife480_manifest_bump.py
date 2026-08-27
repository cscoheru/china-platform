#!/usr/bin/env python3
"""Knife 480 bump script — docs/53 §5 第 21 项 O1 B 路 NATIONAL_BULLETIN 试点轴登记
(tasking 480).

落地:
  - docs/53-stage2-public-ingest-ops-handbook-20260826.md (MODIFIED):
    §5 新增第 21 项 blockquote (O1 B 路下一试点轴 = stats.gov.cn /
    NATIONAL_BULLETIN HTML; O1 仍 OPEN; 第 16–20 项既有正文原样).
  - docs/45-stage2-s210-lite-gate2-review-index-20260826.md (MODIFIED):
    文首 queue_rev 227 刷新行 / §1 登记段 / §6.2 +1 行 /
    §7 pack invariant 链 792 → 794.
  - docs/52-stage2-official-open-source-auto-ingest-plan-20260826.md
    (MODIFIED — 已入 manifest; bump SKIP, SHA REFRESH 不增计数 per knife 44 先例;
    可选 §0 一句互链: 第 21 项互链 per 480).
  - scripts/_knife480_manifest_bump.py (本文件)
  - reviews/.../480-stage0-cc-docs53-o1-bpath-nbs-pilot-axis-receipt-20260827.md

前置 knife 105 已落 pack (790 → 792); 本刀 +2 = bump + receipt → 792 → 794;
docs/45/docs/53/docs/52 已入 manifest, SHA REFRESH 不增计数.

NEW_ARTIFACTS = +2 → 792 → 794

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
        "scripts/_knife480_manifest_bump.py",
        "spike_helper",
    ),
    (
        "reviews/stage0-gate0-rework-2026-08-23/"
        "480-stage0-cc-docs53-o1-bpath-nbs-pilot-axis-receipt-20260827.md",
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
