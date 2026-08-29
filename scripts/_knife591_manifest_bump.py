#!/usr/bin/env python3
"""Knife 591 bump script — docs/50 §5.1 row 117 A 路 supersede refresh + 590 audit 入库刀
(per 590 audit §L 推荐 + 589 tasking 「审计文件不单独
commit，随下一刀入库」; per 2026-08-29 治理铁律 docs-only 零代码零 SQL).

落地 (合刀 A–D 同 commit、单槽单回执; docs/50 row 117 A 路 supersede 标注 append 与
原文共存 + 590 audit 入库 NEW documentation + 591 receipt NEW documentation +
docs/50 SHA REFRESH + 00-EXEC-QUEUE.md SHA REFRESH):
  - scripts/_knife591_manifest_bump.py (本文件, ADD, spike_helper).
  - reviews/.../590-stage0-architect-s589-o3-impl-docs50-supersede-refresh-audit-PASS-20260829.md
    (590 audit 文件, ADD, documentation).
  - reviews/.../591-stage0-cc-o1-impl-docs50-o1-row117-supersede-refresh-tasking-20260829-receipt.md
    (本刀回执, ADD, documentation).

COUNT CHECK (枚举即权威, 逐项实测 NOT-IN):
  589 落地后 manifest 926 (per 589 §4 enumeration: bump + 回执 → 926); 591 本刀
  +3 NEW = 929 (926 + 3 per enumeration 收口: bump 脚本 + 590 audit + 591 receipt);
  enumeration wins per 583 §F "枚举即权威" 原则.

NEW_ARTIFACTS = +3 → 926 → 929
REFRESH_ARTIFACTS = docs/50 (row 117 A 路 supersede append) + 00-EXEC-QUEUE.md
  (§CURRENT → 591 + status PENDING + rev 8) + 591 receipt (两阶段 paste+refresh
  模式 per 577/581/583/585/587/589 先例).

SKIP: docs/45 / docs/49 / docs/53 / scripts/intake_real_sha_if_present.py /
scripts/auto_ingest_public_source.py / 590 audit 文件本身 (计入 NEW) / 589
回执 / 589 tasking / 588 audit / 587 回执 / 587 tasking / 旧版 user-action 任务书 /
591 任务书本身 (按先例不入 manifest) / S0 源 PDF (不动) / 4 fixture 字节
(锁值不变) / migration 001-014 (零触碰) / 01-core.sql (零触碰) /
source_registry/registry.csv (零触碰) / spikes/04-scanned-pdf/gate_thresholds.json
(零触碰) / data/seed_archives/ (空目录) / 不动 001-014 migration 文件.

Recomputes role_count from artifacts (source of truth, per knife 16 fix).
"""
from __future__ import annotations

import hashlib
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
MANIFEST = ROOT / "evidence_pack" / "manifest.json"

R = "reviews/stage0-gate0-rework-2026-08-23/"

NEW_ARTIFACTS = [
    ("scripts/_knife591_manifest_bump.py", "spike_helper"),
    (R + "590-stage0-architect-s589-o3-impl-docs50-supersede-refresh-audit-PASS-20260829.md",
     "documentation"),
    (R + "591-stage0-cc-o1-impl-docs50-o1-row117-supersede-refresh-tasking-20260829-receipt.md",
     "documentation"),
]

# 已在 manifest 的文件: SHA REFRESH 不增计数 (tasking 591 §3.3 SKIP/REFRESH).
# docs/45 / docs/49 / docs/53 587 已 sync + 589 docs-only + 591 docs-only 不再触碰.
# scripts/intake_real_sha_if_present.py 零触碰.
# scripts/auto_ingest_public_source.py 零触碰.
# 590 audit 入库后即成为 NEW.
# 589 receipt / 589 tasking / 588 audit / 587 receipt / 587 tasking 保持现状.
# 旧版 user-action 任务书按先例不入 manifest.
# 591 任务书按先例不入 manifest.
# docs/50 row 117 原文不删不改 + 591 A 路 supersede 标注 append.
REFRESH_ARTIFACTS = [
    "docs/50-stage2-gate2-review-packet-draft-20260826.md",
    R + "00-EXEC-QUEUE.md",
    R + "591-stage0-cc-o1-impl-docs50-o1-row117-supersede-refresh-tasking-20260829-receipt.md",
]

EXPECTED_COUNT = 929  # 926 + 3 (per enumeration 收口: bump + 590 audit + 591 receipt)


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
    by_path = {a.get("path"): a for a in artifacts}

    added = 0
    for rel, role in NEW_ARTIFACTS:
        p = ROOT / rel
        if not p.exists():
            print(f"ERR: {rel} not on disk", file=sys.stderr)
            return 1
        if rel in by_path:
            print(f"SKIP: {rel}")
            continue
        size = p.stat().st_size
        digest = sha256(p)
        artifacts.append(
            {"path": rel, "size_bytes": size, "sha256": digest, "role": role}
        )
        by_path[rel] = artifacts[-1]
        added += 1
        print(f"ADD: {rel} ({size} bytes, sha={digest[:8]}, role={role})")

    for rel in REFRESH_ARTIFACTS:
        if rel not in by_path:
            print(f"NOT-IN-MANIFEST (房规 skip, no count change): {rel}")
            continue
        p = ROOT / rel
        if not p.exists():
            print(f"ERR: refresh target {rel} not on disk", file=sys.stderr)
            return 1
        entry = by_path[rel]
        old_digest = entry.get("sha256", "")
        new_digest = sha256(p)
        if new_digest == old_digest:
            print(f"REFRESH (unchanged): {rel} sha={new_digest[:8]}")
            continue
        entry["sha256"] = new_digest
        entry["size_bytes"] = p.stat().st_size
        print(
            f"REFRESH: {rel} sha={old_digest[:8]} → {new_digest[:8]} "
            f"({entry['size_bytes']} bytes; no count change)"
        )

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
    assert new_count == EXPECTED_COUNT, (
        f"INVARIANT BROKEN: artifact_count={new_count} != expected "
        f"{EXPECTED_COUNT} (926 + 3 per enumeration 收口: bump 脚本 + "
        f"590 audit + 591 receipt)"
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