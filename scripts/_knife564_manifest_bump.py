#!/usr/bin/env python3
"""Knife 564 bump script — 合刀：docs/50 intro ⚠ 收据链尾 +1 续接 → 562 + docs/45 §3 第 33 项刷新 (tasking 564).

落地 (合刀 A+B+C 同 commit、单槽单回执; registry 本刀零改动; 纯文档零运行零网络):
  - source_registry/registry.csv: 本刀零改动 (`560`/`562` ≠ O1 收口, O1 仍 OPEN;
    未启用 Hubei live).
  - docs/53-stage2-public-ingest-ops-handbook-20260826.md (MODIFIED):
    §5 第 33 项互链句 +1 句 (docs/50 §4.4 intro 链尾续接 → 562 per 564;
    第 21–33 项既有 blockquote 正文原样未动).
  - docs/50-stage2-gate2-review-packet-draft-20260826.md (MODIFIED):
    §4.4 intro ⚠ 收据链尾 +1 续接 `→ 562` (第 33 项 post-(a) live
    refresh 证据里程碑 per 560 落地 / 562 行补登; hash 匹配 ≠ O1 收口;
    链尾以 `562` 收口; 里程碑表 21–33 行正文原样未动).
  - docs/52: 本刀零触碰.
  - docs/45-stage2-s210-lite-gate2-review-index-20260826.md (MODIFIED):
    文首 queue_rev 312 刷新行 + §1 一句 +
    §6.2 行尾注 append + §7 链 876 → 878 (§3 第 33 项证据刷新段 +1).
  - scripts/_knife564_manifest_bump.py (本文件)
  - reviews/.../564-stage0-cc-docs50-intro-chain-562-and-docs45-item33-refresh-bundle-receipt-20260828.md

本刀纯文档 (实跑 per 560 已落, 本刀未实跑 --live);
registry 零改动, hash 匹配 ≠ O1 收口, O1 仍 OPEN.

前置 knife 562 已落 pack (874 → 876); 本刀 +2 = bump + receipt → 876 → 878.

NEW_ARTIFACTS = +2 → 876 → 878

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
        "scripts/_knife564_manifest_bump.py",
        "spike_helper",
    ),
    (
        "reviews/stage0-gate0-rework-2026-08-23/"
        "564-stage0-cc-docs50-intro-chain-562-and-docs45-item33-refresh-bundle-receipt-20260828.md",
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
