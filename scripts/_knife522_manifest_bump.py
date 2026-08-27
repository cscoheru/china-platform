#!/usr/bin/env python3
"""Knife 522 bump script — docs/50 §4.4 第 28 项 SHA drift 分叉里程碑行补登 (tasking 522).

落地 (纯文档零运行零网络; registry 未改等用户裁定后另刀): 
  - docs/50-stage2-gate2-review-packet-draft-20260826.md (MODIFIED):
    §4.4 里程碑表新增第 28 项行「docs/53 §5 第 28 项 SHA drift
    候选轨处置分叉登记」(回执列 520; intro 收据链尾保持 → 512 原样未动;
    只登记不替用户选; O1 仍 OPEN; 第 21–27 项行既有正文原样未动).
  - docs/53-stage2-public-ingest-ops-handbook-20260826.md (MODIFIED):
    可选第 28 项补登句一句 (per 回执 522).
  - docs/45-stage2-s210-lite-gate2-review-index-20260826.md (MODIFIED):
    文首 queue_rev 269 刷新行 + §1 一句 + §6.2 行尾注 + §7 链 834 → 836.
  - scripts/_knife522_manifest_bump.py (本文件)
  - reviews/.../522-stage0-cc-docs50-item28-sha-drift-fork-milestone-receipt-20260827.md

本刀纯文档零代码.

前置 knife 520 已落 pack (832 → 834); 本刀 +2 = bump + receipt → 834 → 836.

NEW_ARTIFACTS = +2 → 834 → 836

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
        "scripts/_knife522_manifest_bump.py",
        "spike_helper",
    ),
    (
        "reviews/stage0-gate0-rework-2026-08-23/"
        "522-stage0-cc-docs50-item28-sha-drift-fork-milestone-receipt-20260827.md",
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
