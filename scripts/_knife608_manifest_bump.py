#!/usr/bin/env python3
"""Knife 608 bump script — O1 §5.2.x 江苏样本第三刀（地市样本第二刀）落地
(执行端自取 tjj.nanjing.gov.cn 南京市统计局公开源走完整 e2e 流水线 per docs/52 B 路 spec)

(per 608 tasking §1.7 + 607 audit §10 + 607 receipt §A 备选清单 verbatim
"| https://tjj.nanjing.gov.cn/ | ✅ 200 OK | 南京市统计局首页 (40065 bytes; 备选) |"
+ 606 audit §10 候选 #2 verbatim "O1 §5.2.x 江苏样本第三刀（地市样本第二刀；tjj.nanjing.gov.cn 40065 bytes 已备选）"
+ 2026-08-29 治理铁律「数据源唯一=政府/统计局/研究机构自取；用户零裁定；
执行端不可提任何用户裁定事项」+ docs/52 B 路 spec 已 CLOSED per 599
audit PASS 落地 + 607 audit PASS + 607 receipt PASS + 606 audit PASS +
605 audit PASS + 605 receipt PASS).

落地 (合刀 同 commit、单槽单回执; 608 receipt 入库 NEW documentation +
bump 脚本 NEW spike_helper + 607 audit 入库随 608 commit (per docs 房规
"审计文件不单独 commit 随下一刀入库") + 608 receipt + 江苏样本地市第二刀
SHA-locked HTML 入库 + source_registry/registry.csv +1 行 (REFRESH 不
增计数 per file-based role_count 守门)):

  - scripts/_knife608_manifest_bump.py (NEW spike_helper; 本刀自身)
  - reviews/.../607-stage0-architect-s606-o1-§5.2.x-real-sha-locked-江苏地市样本-tasking-20260829-audit-PASS-20260829.md
    (607 audit 入库随 608 commit, NEW documentation per docs 房规)
  - reviews/.../608-stage0-cc-o1-§5.2.x-real-sha-locked-江苏样本-地市第二刀-tasking-20260829-receipt.md
    (本刀回执, NEW documentation)
  - data/seed_archives/jiangsu_nanjing_tjj_gov_cn_20260829.html
    (江苏样本地市第二刀 SHA-locked HTML, spike_sample_or_truth role)

COUNT CHECK (枚举即权威, 逐项实测 NOT-IN-INVARIANT):
  607 落地后 manifest 961 (per 606 §G K=4 → manifest 957 → 961
  per EXPECTED_COUNT 961; 606 计入 source_registry_csv REFRESH 不增
  计数 per file-based role_count 守门 + spike_sample_or_truth role +1);
  608 本刀 +4 NEW = 965 (961 + 4 per enumeration 收口: bump 脚本 +
  607 audit + 608 receipt + 江苏样本地市第二刀 spike_sample_or_truth role);
  source_registry/registry.csv REFRESH (不增计数 per file-based
  role_count 守门; +1 行 bytes 总数变化是预期, REFRESH sha + size_bytes 守门);
  608 tasking 文件本身 NOT-IN-MANIFEST per docs 房规;
  docs/45 §6.2 O1 status append 不增计数 per docs-only refresh 房规;
  608 §1.7 disclosure: source_registry/registry.csv +1 行视为 enumeration
  即权威 per 583 §F 计入 disclosure 但 file-based role_count 维持. K=4 per 608 §1.7.

NEW_ARTIFACTS = +4 → 961 → 965
REFRESH_ARTIFACTS = 00-EXEC-QUEUE.md + 608 receipt + source_registry/registry.csv
(三阶段 paste+refresh 模式 per 577/581/583/585/587/589/591/593/594/595/
596/597/599/601/603/605/606/607 先例; source_registry_csv file-based 守门不增计数).

SKIP: docs/45 §6.2 O1 status append (docs-only refresh, 不增计数 per docs 房规) +
docs/49/50/51/52/53 status row append (F 段 SKIP per 608 §1.6 命中为治理级决策
标注非 stale runtime flag) + scripts/intake_real_sha_if_present.py /
scripts/auto_ingest_public_source.py 零触碰 + 607 / 606 / 605 / 604 / 603 /
602 / 601 / 600 / 599 / 598 / 597 / 596 / 595 / 594 / 593 / 592 / 591 / 590 /
589 / 588 / 587 / 旧版 user-action 任务书 (按先例不入 manifest) / 608 tasking 本身
(按 docs 房规 NOT-IN-MANIFEST) / S0 源 PDF (不动) / 4 fixture 字节
(锁值不变) / migration 001-013 (零触碰) / 01-core.sql (零触碰) /
source_registry/registry.csv 既有 9 行 (SHA 不变, 仅 +1 行) /
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
    ("scripts/_knife608_manifest_bump.py", "spike_helper"),
    (R + "607-stage0-architect-s606-o1-§5.2.x-real-sha-locked-江苏地市样本-tasking-20260829-audit-PASS-20260829.md",
     "documentation"),
    (R + "608-stage0-cc-o1-§5.2.x-real-sha-locked-江苏样本-地市第二刀-tasking-20260829-receipt.md",
     "documentation"),
    ("data/seed_archives/jiangsu_nanjing_tjj_gov_cn_20260829.html", "spike_sample_or_truth"),
]

# bump 脚本自身 = NEW (含于 NEW_ARTIFACTS); docs/45 §6.2 O1 status append = SKIP
# (不增计数 per docs 房规); docs/49/50/51/52/53 status row append F 段 SKIP per
# 608 §1.6 命中为治理级决策标注非 stale runtime flag;
# scripts/intake_real_sha_if_present.py / scripts/auto_ingest_public_source.py 零触碰;
# 607 / 606 / 605 / 604 / 603 / 602 / 601 / 600 / 599 / 598 / 597 / 596 / 595 / 594 / 593 /
# 旧版 user-action 任务书 / 608 tasking 本身 (按 docs 房规 NOT-IN-MANIFEST) /
# S0 源 PDF (不动) / 4 fixture 字节 (锁值不变) / migration 001-013 (零触碰) /
# 01-core.sql (零触碰) / source_registry/registry.csv 既有 9 行 (SHA 不变) /
# spikes/04-scanned-pdf/gate_thresholds.json (零触碰) / .venv-paddle
# (venv 不入 manifest per spike_helper 房规) /
# scripts/requirements-paddle.txt (spike_helper 房规 NOT-IN-MANIFEST) /
# spikes/04-scanned-pdf/{conftest.py,run_real_paddle_e2e.sh,test_real_paddle_e2e.py}
# (spike_helper 房规 NOT-IN-MANIFEST) /
# docs/45 / docs/46 / docs/44 (docs 房规 NOT-IN-MANIFEST) 保持现状.
REFRESH_ARTIFACTS = [
    R + "00-EXEC-QUEUE.md",
    R + "608-stage0-cc-o1-§5.2.x-real-sha-locked-江苏样本-地市第二刀-tasking-20260829-receipt.md",
    "source_registry/registry.csv",  # REFRESH sha + size_bytes (file-based role_count 守门不增计数)
]

EXPECTED_COUNT = 965  # 961 + 4 per enumeration 收口: _knife608_manifest_bump.py + 607 audit + 608 receipt + 江苏样本地市第二刀 spike_sample_or_truth; source_registry/registry.csv 既有条目 REFRESH 不增计数 per file-based role_count 守门


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
        f"{EXPECTED_COUNT} (961 + 4 per enumeration 收口: "
        f"_knife608_manifest_bump.py + 607 audit + 608 receipt + "
        f"江苏样本地市第二刀 spike_sample_or_truth; source_registry/registry.csv "
        f"REFRESH 不增计数 per file-based role_count 守门)"
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