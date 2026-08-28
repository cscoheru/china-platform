#!/usr/bin/env python3
"""Knife 566 bump script — 合刀：26X 轴 kickoff 登记 + mart-shape 预览路径实跑证据 (tasking 566).

落地 (合刀 A+B+C+D+E 同 commit、单槽单回执; registry 本刀零改动; D 实跑守门 pytest+smoke):
  - source_registry/registry.csv: 本刀零改动 (MART_FIXTURE 预览 = demo mart-shape
    管道, 非 O1 收口; O1 defer 至 26X 后, O1 仍 OPEN; 未启用 Hubei live).
  - docs/53-stage2-public-ingest-ops-handbook-20260826.md (MODIFIED):
    §5 新增第 34 项 26X 轴 kickoff 登记 (用户分叉 = 先 26X·合刀·再 O1;
    MART_FIXTURE 预览路径; 第 21–33 项既有 blockquote 正文原样未动).
  - docs/50-stage2-gate2-review-packet-draft-20260826.md (MODIFIED):
    §4.4 里程碑表新增第 34 项行「26X 轴 kickoff 登记」+ intro ⚠
    收据链尾续接 `→ 566` (链尾以 `566` 收口; MART_FIXTURE 预览 ≠ O1 收口;
    里程碑表 21–33 行正文原样未动).
  - docs/52: 本刀零触碰.
  - docs/45-stage2-s210-lite-gate2-review-index-20260826.md (MODIFIED):
    文首 queue_rev 315 刷新行 + §1 一段 +
    §6.2 行尾注 append + §7 链 878 → 880 (26X 活跃轴 + O1 defer 同步).
  - scripts/_knife566_manifest_bump.py (本文件)
  - reviews/.../566-stage0-cc-s27b-26x-kickoff-mart-fixture-verify-bundle-receipt-20260828.md

本刀 D 实跑守门 (pytest 30 passed exit 0 + smoke PASS exit 0 含 §10a–§10e);
registry 零改动, MART_FIXTURE 预览 ≠ O1 收口, O1 defer 至 26X 后, O1 仍 OPEN.

前置 knife 564 已落 pack (876 → 878); 本刀 +2 = bump + receipt → 878 → 880.

NEW_ARTIFACTS = +2 → 878 → 880

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
        "scripts/_knife566_manifest_bump.py",
        "spike_helper",
    ),
    (
        "reviews/stage0-gate0-rework-2026-08-23/"
        "566-stage0-cc-s27b-26x-kickoff-mart-fixture-verify-bundle-receipt-20260828.md",
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
