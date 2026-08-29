#!/usr/bin/env python3
"""Knife 596 bump script — 584 re-ACK 准备就绪刀（paddle-ocr deps 实际引入 +
Dockerfile build/run 验证 + 584 重 ACK 任务书签发 = 597 tasking 签发）
(per 596 tasking §0.1 + 596 audit PASS §L 推荐 #1 + 595 audit PASS §L 推荐 #3 +
594 receipt §10 推荐 #1 + 594 §9.3 候选 #3 + 584 BLOCKER 5 → 0 全闭环收口).

落地 (合刀 同 commit、单槽单回执; 596 receipt 入库 NEW documentation +
bump 脚本 NEW spike_helper + 00-EXEC-QUEUE.md SHA REFRESH + 596 receipt):

  - scripts/_knife596_manifest_bump.py (NEW spike_helper; 本刀自身)
  - reviews/.../596-stage0-cc-584-reack-ready-tasking-20260829-receipt.md
    (本刀回执, NEW documentation)

COUNT CHECK (枚举即权威, 逐项实测 NOT-IN-INVARIANT):
  595 落地后 manifest 939 (per 595 §0.1: 595 bump script + Dockerfile +
  requirements-paddle.txt + executor_orient.sh + 595 receipt = +5);
  596 本刀 +2 NEW = 941 (939 + 2 per enumeration 收口: bump 脚本 +
  596 receipt); 597 tasking 文件本身 NOT-IN-MANIFEST per docs 房规;
  docs/X 零修改 (per 596 §0.2 红线 22 + 红线 23). K=2 per 596 §4.1.

NEW_ARTIFACTS = +2 → 939 → 941
REFRESH_ARTIFACTS = 00-EXEC-QUEUE.md + 596 receipt (两阶段 paste+refresh 模式
per 577/581/583/585/587/589/591/593/594/595 先例).

SKIP: docs/45 / docs/49 / docs/50 / docs/52 / docs/53 587/589/591/593 docs-only
refresh 链不再触碰其它行 + 596 不修改 docs/X 任何字节 + scripts/intake_real_sha_if_present.py
/ scripts/auto_ingest_public_source.py 零触碰 + 595 回执 / 595 任务书 / 595 audit /
594 回执 / 594 任务书 / 594 audit / 593 回执 / 593 任务书 / 593 audit /
592 audit / 591 回执 / 591 任务书 / 591 audit / 590 audit / 589 回执 /
589 任务书 / 589 audit / 588 audit / 587 回执 / 587 任务书 / 旧版 user-action
任务书 (按先例不入 manifest) / 596 任务书本身 (按先例不入 manifest) / 597 tasking
本身 (按 docs 房规 NOT-IN-MANIFEST) / S0 源 PDF (不动) / 4 fixture 字节
(锁值不变) / migration 001-014 (零触碰) / 01-core.sql (零触碰) /
source_registry/registry.csv (零触碰) / spikes/04-scanned-pdf/gate_thresholds.json
(零触碰) / data/seed_archives/ (空目录) / docs/52 B 路标注 (本刀不修改
docs/52 内容; 仅 grep 命中计数参考) / requirements-dbt.txt (零触碰, 9 行不变)
/ .venv-paddle (venv 不入 manifest per spike_helper 房规) / paddle-ocr:v1
Docker image (596 已清理释放).

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
    ("scripts/_knife596_manifest_bump.py", "spike_helper"),
    (R + "596-stage0-cc-584-reack-ready-tasking-20260829-receipt.md",
     "documentation"),
]

# bump 脚本自身 = NEW (含于 NEW_ARTIFACTS); docs/X 零修改 = SKIP;
# scripts/intake_real_sha_if_present.py / scripts/auto_ingest_public_source.py 零触碰;
# 595 / 594 / 593 / 592 / 591 / 590 / 589 / 588 / 587 / 旧版 user-action
# 任务书 / 596 任务书本身 / 597 tasking 本身 (按 docs 房规 NOT-IN-MANIFEST) /
# S0 源 PDF (不动) / 4 fixture 字节 (锁值不变) / migration 001-014 (零触碰) /
# 01-core.sql (零触碰) / source_registry/registry.csv (零触碰) /
# spikes/04-scanned-pdf/gate_thresholds.json (零触碰) / data/seed_archives/
# (空目录) / docs/52 内容 (596 仅 grep 命中计数参考, 不修改字节) /
# docs/45 / 49 / 50 / 53 (596 零修改) / requirements-dbt.txt (零触碰) 保持现状.
REFRESH_ARTIFACTS = [
    R + "00-EXEC-QUEUE.md",
    R + "596-stage0-cc-584-reack-ready-tasking-20260829-receipt.md",
]

EXPECTED_COUNT = 941  # 939 + 2 (per enumeration 收口: _knife596_manifest_bump.py + 596 receipt)


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
        f"{EXPECTED_COUNT} (939 + 2 per enumeration 收口: "
        f"_knife596_manifest_bump.py + 596 receipt)"
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