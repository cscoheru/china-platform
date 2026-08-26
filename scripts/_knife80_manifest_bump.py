#!/usr/bin/env python3
"""Knife 80 bump script — docs/50 §4.4 补登首页 deeplink 里程碑 (tasking 428).

落地:
  - docs/50-stage2-gate2-review-packet-draft-20260826.md (MODIFIED — 已入
    manifest; bump SKIP, SHA REFRESH 不增计数 per knife 44 先例):
    §4.4 里程碑表末尾 +2 行:
      (a) 首页 NBS sample 轨显式 deeplink (#track-nbs-sample; 回执 420 + cc_head
          backfill bee7950; smoke §12b' 4 针 + pytest 3 cases + 4 fixture byte
          SHA 锁 nbs=e30ee811/nbs_live=9232efdb/sz=937255a5/hb=9056001c);
      (b) 首页 NBS live 候选轨显式 deeplink (#track-nbs-live; 回执 424 + cc_head
          backfill 29467c4; smoke §12b'' 4 针 + pytest 3 cases + 4 fixture byte
          SHA 锁与 knife 76 完全一致).
    链 docs/45 §1 + §6.2 + §7 + docs/53 §5; 显式 demo/candidate 演示、非 O1/Gate PASS.
  - scripts/_knife80_manifest_bump.py (本文件)
  - reviews/.../428-stage0-cc-docs50-home-deeplinks-milestone-receipt-20260826.md

前置 knife 79 已落 pack (737 → 739); 本刀 +2 = bump + receipt → 739 → 741;
docs/50 已入 manifest, SHA REFRESH 不增计数.

NEW_ARTIFACTS = +2 → 739 → 741

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
        "scripts/_knife80_manifest_bump.py",
        "spike_helper",
    ),
    (
        "reviews/stage0-gate0-rework-2026-08-23/"
        "428-stage0-cc-docs50-home-deeplinks-milestone-receipt-20260826.md",
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
