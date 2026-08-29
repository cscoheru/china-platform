#!/usr/bin/env python3
"""Knife 599 bump script — docs/52 B 路 spec 落定刀
(docs/52 + docs/47 + docs/48 stale user-action selective refresh +
docs/49 + docs/50 状态行 append 598 audit 落标注 +
manifest bump + 598 audit 入库随 599 commit per docs 房规 + 599 receipt)

(per 599 tasking §1.5 + 598 audit §L 推荐 #1 + 597 audit §L 推荐 #1 +
597 receipt §6 + 596 audit §L 推荐 #2 + 595 audit §L 推荐 #3 +
594 receipt §10 推荐 #1).

落地 (合刀 同 commit、单槽单回执; 599 receipt 入库 NEW documentation +
bump 脚本 NEW spike_helper + 598 audit 入库 NEW documentation + 599 receipt +
00-EXEC-QUEUE.md SHA REFRESH):

  - scripts/_knife599_manifest_bump.py (NEW spike_helper; 本刀自身)
  - reviews/.../598-stage0-architect-s597-584-impl-tasking-20260829-audit-PASS-20260829.md
    (598 audit 入库随 599 commit, NEW documentation per docs 房规
    "审计文件不单独 commit 随下一刀入库")
  - reviews/.../599-stage0-cc-docs-52-b-route-spec-refresh-tasking-20260829-receipt.md
    (本刀回执, NEW documentation)

COUNT CHECK (枚举即权威, 逐项实测 NOT-IN-INVARIANT):
  597 落地后 manifest 944 (per 597 §0.1: 597 bump script + 596 audit + 597 receipt = +3);
  599 本刀 +3 NEW = 947 (944 + 3 per enumeration 收口: bump 脚本 +
  598 audit + 599 receipt); 599 tasking 文件本身 NOT-IN-MANIFEST per docs 房规;
  docs/52 / docs/47 / docs/48 / docs/49 / docs/50 stale 行 selective refresh
  不增计数 per docs-only refresh 房规. K=3 per 599 §1.5.

NEW_ARTIFACTS = +3 → 944 → 947
REFRESH_ARTIFACTS = 00-EXEC-QUEUE.md + 599 receipt (两阶段 paste+refresh 模式
per 577/581/583/585/587/589/591/593/594/595/596/597 先例).

SKIP: docs/52 / docs/47 / docs/48 / docs/49 / docs/50 stale 行 selective refresh
(docs-only refresh, 不增计数 per docs 房规) +
scripts/intake_real_sha_if_present.py / scripts/auto_ingest_public_source.py
零触碰 + 597 / 596 / 595 / 594 / 593 / 592 / 591 / 590 / 589 / 588 / 587 /
旧版 user-action 任务书 (按先例不入 manifest) / 599 tasking 本身
(按 docs 房规 NOT-IN-MANIFEST) / S0 源 PDF (不动) / 4 fixture 字节
(锁值不变) / migration 001-014 (零触碰) / 01-core.sql (零触碰) /
source_registry/registry.csv (零触碰) / spikes/04-scanned-pdf/gate_thresholds.json
(零触碰) / data/seed_archives/ (空目录) / requirements-dbt.txt (零触碰) /
.venv-paddle (venv 不入 manifest per spike_helper 房规) /
scripts/requirements-paddle.txt (spike_helper 房规 NOT-IN-MANIFEST) /
spikes/04-scanned-pdf/{conftest.py,run_real_paddle_e2e.sh,test_real_paddle_e2e.py}
(spike_helper 房规 NOT-IN-MANIFEST) /
docs/52 / docs/47 / docs/48 / docs/49 / docs/50 (docs 房规 NOT-IN-MANIFEST)
保持现状.

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
    ("scripts/_knife599_manifest_bump.py", "spike_helper"),
    (R + "598-stage0-architect-s597-584-impl-tasking-20260829-audit-PASS-20260829.md",
     "documentation"),
    (R + "599-stage0-cc-docs-52-b-route-spec-refresh-tasking-20260829-receipt.md",
     "documentation"),
]

# bump 脚本自身 = NEW (含于 NEW_ARTIFACTS); docs/X stale 行 selective refresh
# = SKIP (不增计数 per docs 房规);
# scripts/intake_real_sha_if_present.py / scripts/auto_ingest_public_source.py 零触碰;
# 597 / 596 / 595 / 594 / 593 / 592 / 591 / 590 / 589 / 588 / 587 /
# 旧版 user-action 任务书 / 599 tasking 本身 (按 docs 房规 NOT-IN-MANIFEST) /
# S0 源 PDF (不动) / 4 fixture 字节 (锁值不变) / migration 001-014 (零触碰) /
# 01-core.sql (零触碰) / source_registry/registry.csv (零触碰) /
# spikes/04-scanned-pdf/gate_thresholds.json (零触碰) / data/seed_archives/
# (空目录) / requirements-dbt.txt (零触碰) / .venv-paddle (venv 不入 manifest)
# 保持现状.
REFRESH_ARTIFACTS = [
    R + "00-EXEC-QUEUE.md",
    R + "599-stage0-cc-docs-52-b-route-spec-refresh-tasking-20260829-receipt.md",
]

EXPECTED_COUNT = 947  # 944 + 3 (per enumeration 收口: _knife599_manifest_bump.py + 598 audit + 599 receipt)


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
        f"{EXPECTED_COUNT} (944 + 3 per enumeration 收口: "
        f"_knife599_manifest_bump.py + 598 audit + 599 receipt)"
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