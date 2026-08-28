#!/usr/bin/env python3
"""Knife 572 bump script — 合刀：mart 真 SHA pilot（nanjing CONDITION）+ docs (tasking 572).

落地 (合刀 A–F 同 commit、单槽单回执; registry 本刀零改动; 锚点核验零网络 + mart skel pytest 25 passed):
  - source_registry/registry.csv: 本刀零改动 (pilot 1 行真 SHA ≠ O1 收口;
    mart 全量 60 行 flip / person 真数据仍 OPEN; O1 仍 OPEN; 未启用 Hubei live).
  - dbt/models/marts/mart_city_evidence_chain.sql (MODIFIED):
    lineage 两列 CASE 条件式 — pilot 行 (nanjing + CONDITION) =
    registry `a7e4029d…` (per `538` (a) 裁定值 + `560` hash 匹配 live
    refresh) + `lineage_is_demo` = 'false'; 其余 59 行原样 demo + '0'*64
    (mart_city_seven_dim_overview.sql 本刀未动).
  - tests/test_mart_city_dbt_skel_s27bf.py (MODIFIED):
    新增 §8 五例锁定 pilot (真 SHA executable count == 1 / 条件恰 2 处 /
    ELSE 占位 / is_demo CASE 结构 / 真 SHA 在位; 既有 20 例 docstring
    语义对齐) → pytest 25 passed / exit 0.
  - docs/53-stage2-public-ingest-ops-handbook-20260826.md (MODIFIED):
    §5 新增第 38 项 mart 真 SHA 入仓 pilot 实装证据 (第 21–37 项既有
    blockquote 正文原样未动).
  - docs/50-stage2-gate2-review-packet-draft-20260826.md (MODIFIED):
    §4.4 里程碑表新增第 38 项行「mart 真 SHA 入仓 pilot 实装」+
    intro ⚠ 收据链尾续接 `→ 572` (链尾以 `572` 收口;
    pilot 1 行 ≠ O1 收口; 里程碑表 21–37 行正文原样未动).
  - docs/45-stage2-s210-lite-gate2-review-index-20260826.md (MODIFIED):
    文首 queue_rev 320 刷新行 + §1 一段 + §6.2 占位行 pilot 注 +
    §6.2 行尾注 append + §7 链 884 → 886 (mart SHA pilot 同步).
  - scripts/_knife572_manifest_bump.py (本文件)
  - reviews/.../572-stage0-cc-o1-mart-sha-pilot-impl-bundle-receipt-20260828.md

本刀锚点核验零网络 (registry `a7e4029d` grep 实证 + 4 fixture 锁值实测 +
mart skel pytest 25 passed exit 0);
registry 零改动, pilot 1 行真 SHA ≠ O1 收口, O1 仍 OPEN.

前置 knife 570 已落 pack (882 → 884); 本刀 +2 = bump + receipt → 884 → 886.

NEW_ARTIFACTS = +2 → 884 → 886

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
        "scripts/_knife572_manifest_bump.py",
        "spike_helper",
    ),
    (
        "reviews/stage0-gate0-rework-2026-08-23/"
        "572-stage0-cc-o1-mart-sha-pilot-impl-bundle-receipt-20260828.md",
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
