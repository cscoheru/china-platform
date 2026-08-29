#!/usr/bin/env python3
"""Knife 605 bump script — O1 §5.2.x 真实 SHA-locked 江苏样本刀首批样本落地
(执行端自取江苏统计局公开源走完整 e2e 流水线 per docs/52 B 路 spec)

(per 605 tasking §1.7 + 604 audit §8.1 + 603 receipt §8.1 候选 #1
+ 601 audit §L 推荐 #1 + 2026-08-29 治理铁律「数据源唯一=政府/统计局/
研究机构自取；用户零裁定；执行端不可提任何用户裁定事项」
+ 599 audit §L 推荐 #1 候选 docs/52 B 路 spec 落定 + 597 receipt §6 候选 #1).

落地 (合刀 同 commit、单槽单回执; 605 receipt 入库 NEW documentation +
bump 脚本 NEW spike_helper + 604 audit 入库 NEW documentation +
605 receipt + 00-EXEC-QUEUE.md SHA REFRESH + source_registry/registry.csv
+1 行 江苏样本 + 江苏样本 SHA-locked HTML 入库):

  - scripts/_knife605_manifest_bump.py (NEW spike_helper; 本刀自身)
  - reviews/.../604-stage0-architect-s603-docs-45-chain-head-refresh-收口-tasking-20260829-audit-PASS-20260829.md
    (604 audit 入库随 605 commit, NEW documentation per docs 房规
    "审计文件不单独 commit 随下一刀入库")
  - reviews/.../605-stage0-cc-o1-§5.2.x-real-sha-locked-江苏样本-tasking-20260829-receipt.md
    (本刀回执, NEW documentation)

COUNT CHECK (枚举即权威, 逐项实测 NOT-IN-INVARIANT):
  603 落地后 manifest 953 (per 603 §1.5: 603 bump script + 602 audit + 603 receipt = +3);
  605 本刀 +4 NEW = 957 (953 + 4 per enumeration 收口: bump 脚本 +
  604 audit + 605 receipt + 江苏样本 spike_sample_or_truth role);
  source_registry/registry.csv 既有条目 REFRESH (不增计数 per file-based
  role_count 守门; +1 行 bytes 总数变化是预期, REFRESH sha + size_bytes 守门);
  605 tasking 文件本身 NOT-IN-MANIFEST per docs 房规;
  docs/45 §6.2 O1 status append 不增计数 per docs-only refresh 房规;
  605 ⚠ disclosure #1: source_registry/registry.csv +1 行视为 enumeration
  即权威 per 583 §F 计入 disclosure 但 file-based role_count 维持. K=4 per 605 §1.7.

NEW_ARTIFACTS = +5 → 953 → 958
REFRESH_ARTIFACTS = 00-EXEC-QUEUE.md + 605 receipt (两阶段 paste+refresh 模式
per 577/581/583/585/587/589/591/593/594/595/596/597/599/601/603 先例).

SKIP: docs/45 §6.2 O1 status append (docs-only refresh, 不增计数 per docs 房规) +
docs/49/50/51/52/53 status row append (F 段 SKIP per 605 §1.6 命中为治理级决策
标注非 stale runtime flag) + scripts/intake_real_sha_if_present.py /
scripts/auto_ingest_public_source.py 零触碰 + 604 / 603 / 602 / 601 / 600 /
599 / 598 / 597 / 596 / 595 / 594 / 593 / 592 / 591 / 590 / 589 / 588 / 587 / 旧版
user-action 任务书 (按先例不入 manifest) / 605 tasking 本身 (按 docs 房规
NOT-IN-MANIFEST) / S0 源 PDF (不动) / 4 fixture 字节 (锁值不变) /
migration 001-013 (零触碰) / 01-core.sql (零触碰) /
source_registry/registry.csv 既有 7 行 (SHA 不变, 仅 +1 行) /
spikes/04-scanned-pdf/gate_thresholds.json (零触碰) / .venv-paddle
(venv 不入 manifest per spike_helper 房规) /
scripts/requirements-paddle.txt (spike_helper 房规 NOT-IN-MANIFEST) /
spikes/04-scanned-pdf/{conftest.py,run_real_paddle_e2e.sh,test_real_paddle_e2e.py}
(spike_helper 房规 NOT-IN-MANIFEST) /
docs/45 / docs/46 / docs/44 (docs 房规 NOT-IN-MANIFEST) 保持现状.

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
    ("scripts/_knife605_manifest_bump.py", "spike_helper"),
    (R + "604-stage0-architect-s603-docs-45-chain-head-refresh-收口-tasking-20260829-audit-PASS-20260829.md",
     "documentation"),
    (R + "605-stage0-cc-o1-§5.2.x-real-sha-locked-江苏样本-tasking-20260829-receipt.md",
     "documentation"),
    ("data/seed_archives/jiangsu_stats_gov_cn_zxfb_20260829.html", "spike_sample_or_truth"),
    ("source_registry/registry.csv", "source_registry_csv"),
]

# bump 脚本自身 = NEW (含于 NEW_ARTIFACTS); docs/45 §6.2 O1 status append = SKIP
# (不增计数 per docs 房规); docs/49/50/51/52/53 status row append F 段 SKIP per
# 605 §1.6 命中为治理级决策标注非 stale runtime flag;
# scripts/intake_real_sha_if_present.py / scripts/auto_ingest_public_source.py 零触碰;
# 604 / 603 / 602 / 601 / 600 / 599 / 598 / 597 / 596 / 595 / 594 / 593 /
# 旧版 user-action 任务书 / 605 tasking 本身 (按 docs 房规 NOT-IN-MANIFEST) /
# S0 源 PDF (不动) / 4 fixture 字节 (锁值不变) / migration 001-013 (零触碰) /
# 01-core.sql (零触碰) / source_registry/registry.csv 既有 7 行 (SHA 不变) /
# spikes/04-scanned-pdf/gate_thresholds.json (零触碰) / .venv-paddle
# (venv 不入 manifest per spike_helper 房规) /
# scripts/requirements-paddle.txt (spike_helper 房规 NOT-IN-MANIFEST) /
# spikes/04-scanned-pdf/{conftest.py,run_real_paddle_e2e.sh,test_real_paddle_e2e.py}
# (spike_helper 房规 NOT-IN-MANIFEST) /
# docs/45 / docs/46 / docs/44 (docs 房规 NOT-IN-MANIFEST) 保持现状.
REFRESH_ARTIFACTS = [
    R + "00-EXEC-QUEUE.md",
    R + "605-stage0-cc-o1-§5.2.x-real-sha-locked-江苏样本-tasking-20260829-receipt.md",
]

EXPECTED_COUNT = 957  # 953 + 4 (per enumeration 收口: _knife605_manifest_bump.py + 604 audit + 605 receipt + 江苏样本 spike_sample_or_truth; source_registry/registry.csv 既有条目 REFRESH 不增计数)


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
        f"{EXPECTED_COUNT} (953 + 5 per enumeration 收口: "
        f"_knife605_manifest_bump.py + 604 audit + 605 receipt + "
        f"江苏样本 spike_sample_or_truth + source_registry_csv)"
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