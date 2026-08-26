#!/usr/bin/env python3
"""Knife 57 bump script — docs/53 公开提取 ops 手册 + docs/45 登记 (tasking 364).

落地:
  - docs/53-stage2-public-ingest-ops-handbook-20260826.md (NEW — documentation)
    * 公开源 connector ops 手册: 四种运行模式命令例 (dry-run /
      --from-local-sample / --live --confirm-live / --refresh-live-candidate)
      + 10 出口码速查 (0/1/2/3/4/5/6/7/8/9) + sample vs LIVE_CANDIDATE
      分轨契约 + 预览 /public-extracts + 红线 + 相关测试
    * 诚实标注 demo/candidate (tasking 364 §红线); 不宣称 Gate/O1 PASS
  - docs/45-stage2-s210-lite-gate2-review-index-20260826.md (MODIFIED — 已入
    manifest; bump SKIP, SHA REFRESH 不增计数 per knife 44 先例)
    * 刷新 queue_rev 150: 登记 docs/52 + docs/53 + 公开提取双轨
      (REGISTRY_SAMPLE ↔ LIVE_CANDIDATE; 回执 350/353/356/359/362);
      §1 + §6.2 + §7 pack invariant 注记; 仍不宣布 Gate 2 PASS
  - scripts/_knife57_manifest_bump.py (本文件)
  - reviews/.../365-stage0-cc-docs53-ops-handbook-receipt-20260826.md

不做 (per 364): 不改 connector 行为 / 不 Gate PASS / 不改 O1 / 不改 CF。

NEW_ARTIFACTS = +3 → 673 → 676

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
        "docs/53-stage2-public-ingest-ops-handbook-20260826.md",
        "documentation",
    ),
    (
        "scripts/_knife57_manifest_bump.py",
        "spike_helper",
    ),
    (
        "reviews/stage0-gate0-rework-2026-08-23/"
        "365-stage0-cc-docs53-ops-handbook-receipt-20260826.md",
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
