#!/usr/bin/env python3
"""Knife 594 bump script — docs-only 评估刀（584 deps 重 ACK 触发条件评估）
(per 594 audit §L 推荐 #2 中优先级候选 + 593 tasking §7.2 + 592 audit §L.3 +
591 tasking §7; per 2026-08-29 治理铁律 docs-only 零代码零 SQL 评估).

落地 (合刀 同 commit、单槽单回执; 594 receipt 入库 NEW documentation +
bump 脚本 NEW spike_helper + 00-EXEC-QUEUE.md SHA REFRESH):
  - scripts/_knife594_manifest_bump.py (本文件, ADD, spike_helper).
  - reviews/.../594-stage0-cc-eval-584-deps-reack-trigger-tasking-20260829-receipt.md
    (本刀回执, ADD, documentation).

COUNT CHECK (枚举即权威, 逐项实测 NOT-IN):
  593 落地后 manifest 932 (per 593 §4 enumeration: bump + 回执 → 932); 594
  本刀 +2 NEW = 934 (932 + 2 per enumeration 收口: bump 脚本 + 594 receipt);
  enumeration wins per 583 §F "枚举即权威" 原则. (E) docs/X stale BLOCKER
  表述 refresh 命中 = K=0 minimization (per 594 §7.2 注 + §5.2 命中行处理逻辑:
  候选 docs/49 line 297 / docs/50 line 91 / docs/53 line 77 全部 SKIP — 已
  supersede per 593 或非 §5.1 OPEN 表或 EXIT_CODE 表 per §1.2), 因此 docs/X
  supersede append 按 docs 房规 NOT-IN-MANIFEST (不增计数) = K 计数不变.

NEW_ARTIFACTS = +2 → 932 → 934
REFRESH_ARTIFACTS = 00-EXEC-QUEUE.md (§CURRENT → 594 DELIVERED + rev 11) +
  594 receipt (两阶段 paste+refresh 模式 per 577/581/583/585/587/589/591/593
  先例).

SKIP: docs/45 / docs/49 / docs/50 / docs/53 587/589/591/593 docs-only refresh
链不再触碰其它行 + 594 (E) docs/X 命中 = K=0 (docs/49 line 297 已 supersede
per 593; docs/50 line 91 非 §5.1 OPEN 表; docs/53 line 77 EXIT_CODE 表 SKIP
per §1.2) + scripts/intake_real_sha_if_present.py /
scripts/auto_ingest_public_source.py / 593 回执 / 593 任务书 / 593 audit /
592 audit / 591 回执 / 591 任务书 / 591 audit / 590 audit / 589 回执 / 589
任务书 / 589 audit / 588 audit / 587 回执 / 587 任务书 / 旧版 user-action 任务
书 (按先例不入 manifest) / 594 任务书本身 (按先例不入 manifest) / S0 源 PDF
(不动) / 4 fixture 字节 (锁值不变) / migration 001-014 (零触碰) / 01-core.sql
(零触碰) / source_registry/registry.csv (零触碰) /
spikes/04-scanned-pdf/gate_thresholds.json (零触碰) / data/seed_archives/
(空目录) / docs/52 B 路标注 (本刀不修改 docs/52 内容; 仅 grep 命中计数 = 11 B
路 + 0 Dockerfile + 0 paddle-ocr + 8 主路径).

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
    ("scripts/_knife594_manifest_bump.py", "spike_helper"),
    (R + "594-stage0-cc-eval-584-deps-reack-trigger-tasking-20260829-receipt.md",
     "documentation"),
]

# 已在 manifest 的文件: SHA REFRESH 不增计数 (tasking 594 §7.3 SKIP/REFRESH).
# docs/45 / docs/49 / docs/50 / docs/53 587/589/591/593 docs-only refresh 链
# 不再触碰其它行; (E) docs/X stale BLOCKER 表述 K=0 minimization, 因此 docs/X
# 命中行 supersede append = K=0 (按 docs 房规 NOT-IN-MANIFEST, 不增计数).
# scripts/intake_real_sha_if_present.py 零触碰.
# scripts/auto_ingest_public_source.py 零触碰.
# 593 回执 / 593 任务书 / 593 audit / 592 audit / 591 回执 / 591 任务书 / 591
# audit / 590 audit / 589 回执 / 589 任务书 / 589 audit / 588 audit / 587 回执 /
# 587 任务书 保持现状.
# 旧版 user-action 任务书按先例不入 manifest.
# 594 任务书按先例不入 manifest.
# docs/52 B 路标注 grep 仅评估, 不修改.
REFRESH_ARTIFACTS = [
    R + "00-EXEC-QUEUE.md",
    R + "594-stage0-cc-eval-584-deps-reack-trigger-tasking-20260829-receipt.md",
]

EXPECTED_COUNT = 934  # 932 + 2 (per enumeration 收口: bump 脚本 + 594 receipt)


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
        f"{EXPECTED_COUNT} (932 + 2 per enumeration 收口: bump 脚本 + "
        f"594 receipt)"
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