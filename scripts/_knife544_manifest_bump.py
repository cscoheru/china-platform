#!/usr/bin/env python3
"""Knife 544 bump script — docs/45 §3 O1 B 路弧 21–30 刷新 + 四处同步 (tasking 544).

落地 (docs/45 §3 O1 详细段「B 路弧 21–30 已文档化」bullet 就地刷新 +
文首/§1/§6.2/§7 四处同步; registry 本刀零改动
per 538 已执行事实的文档登记节点): 
  - source_registry/registry.csv: 本刀零改动 (前置 538 已更
    a7e4029d…/180165; registry 更新 ≠ O1 收口, O1 仍 OPEN).
  - docs/50/52/53: 本刀零触碰 (tasking「不做动 docs/50/52/53 正文」).
  - docs/45-stage2-s210-lite-gate2-review-index-20260826.md (MODIFIED):
    §3「B 路弧 21–30 已文档化（per 536/544 §3 刷新）」bullet 就地刷新
    (第 30 项三面贯通节点 + 登记节点全引 21–30/26–30) + 文首 queue_rev
    292 刷新行 + §1 一句 + §6.2 行尾注 + §7 链 856 → 858.
  - scripts/_knife544_manifest_bump.py (本文件)
  - reviews/.../544-stage0-cc-docs45-o1-bpath-arc21-30-refresh-receipt-20260828.md

本刀纯文档（docs/45 only）零代码零运行零网络.

前置 knife 542 已落 pack (854 → 856); 本刀 +2 = bump + receipt → 856 → 858.

NEW_ARTIFACTS = +2 → 856 → 858

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
        "scripts/_knife544_manifest_bump.py",
        "spike_helper",
    ),
    (
        "reviews/stage0-gate0-rework-2026-08-23/"
        "544-stage0-cc-docs45-o1-bpath-arc21-30-refresh-receipt-20260828.md",
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
