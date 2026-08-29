#!/usr/bin/env python3
"""Knife 595 bump script — BLOCKER 解除刀（P2 Docker 安装 + P3 Dockerfile 起草 +
P4 paddlepaddle==2.6.2 manifest 写入 + 档 2 spec 落地）
(per 595 audit PASS + 594 audit PASS + 594 receipt §10 推荐 #1 + 594 §6.1 P2/P3/P4 解除条件 +
594 §9.3 候选 #3; 584 BLOCKER 5 → 1 → 0 全闭环 + 档 2 user 批准 2026-08-28 夜起同步执行).

落地 (合刀 同 commit、单槽单回执; 595 receipt 入库 NEW documentation +
bump 脚本 NEW spike_helper + 00-EXEC-QUEUE.md SHA REFRESH + Dockerfile +
requirements-paddle.txt + executor_orient.sh NEW spike_helper +
exec_wake.sh enhancement REFRESH):
  - Dockerfile (NEW spike_helper; per 595 tasking §2 + docs/52 B 路 spec)
  - requirements-paddle.txt (NEW spike_helper; per 595 tasking §3)
  - scripts/executor_orient.sh (NEW spike_helper; architect 起草 spec 已存在 untracked)
  - scripts/exec_wake.sh (REFRESH spike_helper; enhancement sound + title flash)
  - reviews/.../595-stage0-cc-blocker-relief-dockerfile-deps-tasking-20260829-receipt.md
    (本刀回执, NEW documentation).

COUNT CHECK (枚举即权威, 逐项实测 NOT-IN):
  594 落地后 manifest 934 (per 594 §6 enumeration: bump + 回执 → 934); 595
  本刀 +5 NEW = 939 (934 + 5 per enumeration 收口: Dockerfile +
  requirements-paddle.txt + executor_orient.sh + bump 脚本 + 595 receipt);
  exec_wake.sh REFRESH (不增计数, 仅 SHA/size 更新); enumeration wins per
  583 §F "枚举即权威" 原则. docs/X 零修改 (per 595 §0.2 红线 22 + 红线 23).

NEW_ARTIFACTS = +5 → 934 → 939
REFRESH_ARTIFACTS = 00-EXEC-QUEUE.md + 595 receipt (两阶段 paste+refresh 模式
per 577/581/583/585/587/589/591/593/594 先例) + scripts/exec_wake.sh (enhancement
SHA REFRESH).

SKIP: docs/45 / docs/49 / docs/50 / docs/52 / docs/53 587/589/591/593 docs-only
refresh 链不再触碰其它行 + 595 不修改 docs/X 任何字节 + scripts/intake_real_sha_if_present.py
/ scripts/auto_ingest_public_source.py 零触碰 + 594 回执 / 594 任务书 / 594 audit /
593 回执 / 593 任务书 / 593 audit / 592 audit / 591 回执 / 591 任务书 / 591 audit /
590 audit / 589 回执 / 589 任务书 / 589 audit / 588 audit / 587 回执 / 587 任务书 /
旧版 user-action 任务书 (按先例不入 manifest) / 595 任务书本身 (按先例不入 manifest) /
S0 源 PDF (不动) / 4 fixture 字节 (锁值不变) / migration 001-014 (零触碰) /
01-core.sql (零触碰) / source_registry/registry.csv (零触碰) /
spikes/04-scanned-pdf/gate_thresholds.json (零触碰) / data/seed_archives/
(空目录) / docs/52 B 路标注 (本刀不修改 docs/52 内容; 仅 grep 命中计数参考) /
requirements-dbt.txt (零触碰, 独立 paddle 文件不污染 dbt env).

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
    ("Dockerfile", "spike_helper"),
    ("requirements-paddle.txt", "spike_helper"),
    ("scripts/executor_orient.sh", "spike_helper"),
    ("scripts/_knife595_manifest_bump.py", "spike_helper"),
    (R + "595-stage0-cc-blocker-relief-dockerfile-deps-tasking-20260829-receipt.md",
     "documentation"),
]

# exec_wake.sh 已在 manifest (sha=0149f533, 2023 bytes; 增强后 SHA REFRESH);
# bump 脚本自身 = NEW (含于 NEW_ARTIFACTS); docs/X 零修改 = SKIP;
# scripts/intake_real_sha_if_present.py / scripts/auto_ingest_public_source.py 零触碰;
# 594 回执 / 594 任务书 / 594 audit / 593 回执 / 593 任务书 / 593 audit /
# 592 audit / 591 回执 / 591 任务书 / 591 audit / 590 audit / 589 回执 /
# 589 任务书 / 589 audit / 588 audit / 587 回执 / 587 任务书 / 旧版 user-action
# 任务书 (按先例不入 manifest) / 595 任务书本身 (按先例不入 manifest) / S0 源 PDF
# (不动) / 4 fixture 字节 (锁值不变) / migration 001-014 (零触碰) / 01-core.sql
# (零触碰) / source_registry/registry.csv (零触碰) /
# spikes/04-scanned-pdf/gate_thresholds.json (零触碰) / data/seed_archives/
# (空目录) / docs/52 内容 (595 仅 grep 命中计数参考, 不修改字节) / docs/45 / 49 /
# 50 / 53 (595 零修改) / requirements-dbt.txt (零触碰) 保持现状.
REFRESH_ARTIFACTS = [
    R + "00-EXEC-QUEUE.md",
    R + "595-stage0-cc-blocker-relief-dockerfile-deps-tasking-20260829-receipt.md",
    "scripts/exec_wake.sh",
]

EXPECTED_COUNT = 939  # 934 + 5 (per enumeration 收口: Dockerfile + requirements-paddle.txt + executor_orient.sh + bump 脚本 + 595 receipt)


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
        f"{EXPECTED_COUNT} (934 + 5 per enumeration 收口: Dockerfile + "
        f"requirements-paddle.txt + executor_orient.sh + bump 脚本 + 595 receipt)"
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