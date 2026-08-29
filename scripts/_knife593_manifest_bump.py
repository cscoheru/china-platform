#!/usr/bin/env python3
"""Knife 593 bump script — docs-only docs sync 全量巡检刀
(per 592 audit §L.3 #1 高优先级候选 + 591 tasking §7 推荐 #1 高优先级 +
590 audit §L.1 推荐 平行模式三收敛 + 589 tasking §7 平行模式; per 2026-08-29
治理铁律 docs-only 零代码零 SQL).

落地 (合刀 A–D 同 commit、单槽单回执; docs/X 行 supersede 标注 append 与原文共存
+ 592 audit 入库 NEW documentation + 593 receipt NEW documentation +
docs/X SHA REFRESH + 00-EXEC-QUEUE.md SHA REFRESH):
  - scripts/_knife593_manifest_bump.py (本文件, ADD, spike_helper).
  - reviews/.../592-stage0-architect-s591-o1-impl-docs50-o1-row117-supersede-refresh-audit-PASS-20260829.md
    (592 audit 文件, ADD, documentation; per 591 tasking 「审计文件不单独
    commit, 随下一刀入库」).
  - reviews/.../593-stage0-cc-o3-impl-docs-sync-full-sweep-tasking-20260829-receipt.md
    (本刀回执, ADD, documentation).

COUNT CHECK (枚举即权威, 逐项实测 NOT-IN):
  591 落地后 manifest 929 (per 591 §4 enumeration: bump + 回执 → 929); 593
  本刀 +3 NEW = 932 (929 + 3 per enumeration 收口: bump 脚本 + 592 audit +
  593 receipt); enumeration wins per 583 §F "枚举即权威" 原则. docs/X 行
  supersede append 按 docs 房规 NOT-IN-MANIFEST (不增计数).

NEW_ARTIFACTS = +3 → 929 → 932
REFRESH_ARTIFACTS = docs/49 (line 248 + 260 + 293 + 294 supersede append) +
  docs/45 (line 409 supersede append) + 00-EXEC-QUEUE.md (§CURRENT → 593
  DELIVERED + rev 9) + 593 receipt (两阶段 paste+refresh 模式 per
  577/581/583/585/587/589/591 先例).

SKIP: docs/45 / docs/49 / docs/50 / docs/53 587/589/591/593 docs-only refresh
链不再触碰其它行 + scripts/intake_real_sha_if_present.py /
scripts/auto_ingest_public_source.py / 592 audit 文件本身 (计入 NEW) / 591
回执 / 591 tasking / 590 audit / 589 回执 / 589 tasking / 588 audit / 587
回执 / 587 tasking / 旧版 user-action 任务书 / 593 任务书本身 (按先例不入
manifest) / S0 源 PDF (不动) / 4 fixture 字节 (锁值不变) / migration 001-014
(零触碰) / 01-core.sql (零触碰) / source_registry/registry.csv (零触碰) /
spikes/04-scanned-pdf/gate_thresholds.json (零触碰) / data/seed_archives/
(空目录).

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
    ("scripts/_knife593_manifest_bump.py", "spike_helper"),
    (R + "592-stage0-architect-s591-o1-impl-docs50-o1-row117-supersede-refresh-audit-PASS-20260829.md",
     "documentation"),
    (R + "593-stage0-cc-o3-impl-docs-sync-full-sweep-tasking-20260829-receipt.md",
     "documentation"),
]

# 已在 manifest 的文件: SHA REFRESH 不增计数 (tasking 593 §4.3 SKIP/REFRESH).
# docs/49 line 248 / 260 / 293 / 294 + docs/45 line 409 原文不删不改 + 593
# supersede 标注 append (按 docs 房规 NOT-IN-MANIFEST, 不增计数).
# scripts/intake_real_sha_if_present.py 零触碰.
# scripts/auto_ingest_public_source.py 零触碰.
# 592 audit 入库后即成为 NEW.
# 591 receipt / 591 tasking / 590 audit / 589 receipt / 589 tasking / 588
# audit / 587 receipt / 587 tasking 保持现状.
# 旧版 user-action 任务书按先例不入 manifest.
# 593 任务书按先例不入 manifest.
REFRESH_ARTIFACTS = [
    "docs/45-stage2-s210-lite-gate2-review-index-20260826.md",
    "docs/49-stage2-o3-ocr-prod-path-plan-20260826.md",
    R + "00-EXEC-QUEUE.md",
    R + "593-stage0-cc-o3-impl-docs-sync-full-sweep-tasking-20260829-receipt.md",
]

EXPECTED_COUNT = 932  # 929 + 3 (per enumeration 收口: bump + 592 audit + 593 receipt)


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
        f"{EXPECTED_COUNT} (929 + 3 per enumeration 收口: bump 脚本 + "
        f"592 audit + 593 receipt)"
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