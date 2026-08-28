#!/usr/bin/env python3
"""Knife 558 bump script — 合刀：docs/50 intro 链尾 → 556 + docs/45 §3 第 32 项下一轴刷新 + docs/53 尾注 (tasking 558).

落地 (合刀 A+B+C 同 commit、单槽单回执; registry 本刀零改动):
  - source_registry/registry.csv: 本刀零改动 (registry 更新 ≠ O1
    收口, O1 仍 OPEN; 未实跑 --live).
  - docs/53-stage2-public-ingest-ops-handbook-20260826.md (MODIFIED):
    §5 第 32 项互链句 +1 句 (intro 链尾 per 558;
    第 21–32 项既有 blockquote 正文原样未动).
  - docs/50-stage2-gate2-review-packet-draft-20260826.md (MODIFIED):
    §4.4 intro ⚠ 收据链尾 +1 续接 → 556 (第 32 项下一轴
    post-(a) live refresh → mart 真 SHA 入仓; 只登记未运行;
    链尾以 556 收口; 里程碑表 21–32 行正文原样未动).
  - docs/52: 本刀零触碰.
  - docs/45-stage2-s210-lite-gate2-review-index-20260826.md (MODIFIED):
    §3「B 路弧 21–31 已文档化」bullet 就地刷新为「B 路弧
    21–31 + 第 32 项下一轴已文档化（per 536/544/552/558 §3 刷新）」——
    第 32 项下一轴三面贯通节点 + 登记节点全引 21–32;
    文首 queue_rev 306 刷新行 + §1 一句 + §6.2 行尾注 + §7 链 870 → 872.
  - scripts/_knife558_manifest_bump.py (本文件)
  - reviews/.../558-stage0-cc-docs50-intro-chain-556-and-docs45-next-axis-refresh-bundle-receipt-20260828.md

本刀纯文档零代码零运行零网络.

前置 knife 556 已落 pack (868 → 870); 本刀 +2 = bump + receipt → 870 → 872.

NEW_ARTIFACTS = +2 → 870 → 872

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
        "scripts/_knife558_manifest_bump.py",
        "spike_helper",
    ),
    (
        "reviews/stage0-gate0-rework-2026-08-23/"
        "558-stage0-cc-docs50-intro-chain-556-and-docs45-next-axis-refresh-bundle-receipt-20260828.md",
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
