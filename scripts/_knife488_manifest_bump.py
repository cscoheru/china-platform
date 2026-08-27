#!/usr/bin/env python3
"""Knife 488 bump script — docs/52 正文残留 WAITING_FILE 措辞清理 (tasking 488).

落地:
  - docs/52-stage2-official-open-source-auto-ingest-plan-20260826.md
    (MODIFIED): §5 守门表行 2 + §10 checklist 项 + 文末 ⚠ 行三处旧措辞清理
    (O1 仍 OPEN; 主路径 = B 路; WAITING_FILE = intake 出口码 / mart 真 SHA 未入仓
    语义, 非「等用户投喂才可继续」; A 路仍可用非唯一、两路并存) per `484`/`486` 校准.
  - docs/45-stage2-s210-lite-gate2-review-index-20260826.md (MODIFIED):
    文首 queue_rev 235 刷新行 + §1 一句 + §6.2 行尾注 + §7 链 800 → 802.
  - scripts/_knife488_manifest_bump.py (本文件)
  - reviews/.../488-stage0-cc-docs52-body-waiting-file-phrase-cleanup-receipt-20260827.md

前置 knife 486 已落 pack (798 → 800); 本刀 +2 = bump + receipt → 800 → 802.

NEW_ARTIFACTS = +2 → 800 → 802

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
        "scripts/_knife488_manifest_bump.py",
        "spike_helper",
    ),
    (
        "reviews/stage0-gate0-rework-2026-08-23/"
        "488-stage0-cc-docs52-body-waiting-file-phrase-cleanup-receipt-20260827.md",
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
