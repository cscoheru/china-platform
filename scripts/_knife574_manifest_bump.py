#!/usr/bin/env python3
"""Knife 574 bump script — 合刀：O1 docs 收口束 (tasking 574; 架构师治理模型首刀).

落地 (合刀 A–F 同 commit、单槽单回执; 零 SQL 改动; 锚点核验零网络):
  - docs/53-stage2-public-ingest-ops-handbook-20260826.md (MODIFIED):
    §5 新增第 39 项 O1 收口条件登记 (pilot 第 38 项经 `573` 架构师审计
    PASS; 不做 60 行铺满 flip——单一真实源铺 59 行 = 伪造 lineage;
    59 行真实源缺口登记; O1 收口定义 = pilot 限定域完成 + 缺口清单
    登记 + 用户裁定; 当前 O1 仍 OPEN).
  - docs/50-stage2-gate2-review-packet-draft-20260826.md (MODIFIED):
    §4.4 里程碑表新增第 39 项行 + intro ⚠ 收据链尾续接 `→ 574`
    (链尾以 `574` 收口; 第 21–38 项行既有正文原样未动).
    [房规] docs/50 本体未入 manifest (镜像 docs/52 先例) — 本脚本对
    其显式 SKIP, 不增计数.
  - docs/45-stage2-s210-lite-gate2-review-index-20260826.md (MODIFIED):
    文首架构师治理模型刷新行 (Cursor 退役、573 起架构师审计) + §1 一段
    + §6.2 行尾注 append (per `574`) + §7 链头 886 → 889 (knife 572
    demote; knife 574 = 合刀 A–F 同 commit、单槽单回执).
  - scripts/_knife574_manifest_bump.py (本文件)
  - reviews/.../573-stage0-architect-s572-mart-sha-pilot-audit-PASS-20260828.md
    (架构师资产, 只读随刀入库)
  - reviews/.../574-stage0-cc-o1-docs-closeout-bundle-receipt-20260828.md

本刀零 SQL 改动 (mart_city_evidence_chain.sql / seven_dim 原样),
registry 零改动, 不动 4 fixture 字节, 不做 60 行 flip;
pilot 1 行 + 收口条件登记 ≠ O1 收口, O1 仍 OPEN.

前置 knife 572 已落 pack (884 → 886); 本刀 +3 = 573 审计文件 +
574 回执 + bump 脚本 → 886 → 889.

NEW_ARTIFACTS = +3 → 886 → 889
REFRESH_ARTIFACTS = docs/45 + docs/53 + docs/50 (skip) + 574 回执
  — 已在 manifest 的文件 SHA REFRESH 不增计数 (tasking 574 D 项);
    支持二次执行: 回执粘贴 bump 输出后再跑一次, 将回执自身 SHA 刷至
    最终态 (SKIP 已在位条目, 仅 REFRESH).

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
        "scripts/_knife574_manifest_bump.py",
        "spike_helper",
    ),
    (
        "reviews/stage0-gate0-rework-2026-08-23/"
        "573-stage0-architect-s572-mart-sha-pilot-audit-PASS-20260828.md",
        "documentation",
    ),
    (
        "reviews/stage0-gate0-rework-2026-08-23/"
        "574-stage0-cc-o1-docs-closeout-bundle-receipt-20260828.md",
        "documentation",
    ),
]

# 已在 manifest 的文件: SHA REFRESH 不增计数 (tasking 574 D 项).
REFRESH_ARTIFACTS = [
    "docs/45-stage2-s210-lite-gate2-review-index-20260826.md",
    "docs/50-stage2-gate2-review-packet-draft-20260826.md",
    "docs/53-stage2-public-ingest-ops-handbook-20260826.md",
    "reviews/stage0-gate0-rework-2026-08-23/"
    "574-stage0-cc-o1-docs-closeout-bundle-receipt-20260828.md",
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
        print(f"ADD: {rel} ({size} bytes, sha={digest[:8]})")

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
    assert new_count == 889, (
        f"INVARIANT BROKEN: artifact_count={new_count} != expected 889 (886 + 3)"
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
