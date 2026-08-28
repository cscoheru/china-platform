#!/usr/bin/env python3
"""Knife 579 bump script — 合刀: O3 决策备忘 + 全量 4 failed 继承登记
(tasking 579; 架构师治理模型第三刀, 经 00-EXEC-QUEUE.md 签发; docs-only 零网络).

落地 (合刀 A–G 同 commit、单槽单回执; 零代码/零 SQL/零 pytest 变更):
  - docs/53-stage2-public-ingest-ops-handbook-20260826.md (MODIFIED):
    §5 新增第 41 项 O3 决策备忘登记 (三选项呈现 + 用户 2026-08-28 裁定
    A = paddle-ocr 照录; 裁定 ≠ O3 收口, 仅关闭 5.2.1, 实装链 5.2.2-5.2.6
    OPEN; O3 仍 OPEN) + 第 42 项 全量 4 failed 继承登记 (存量既有非 577
    引入; 登记 ≠ 修复).
  - docs/50-stage2-gate2-review-packet-draft-20260826.md (MODIFIED):
    §4.4 +2 行 (第 41/42 项里程碑行) + intro 收据链尾 续接 → 579 +
    §5.1 O3 行照录引擎已裁定 + 新增 继承 4 failed 行.
    [房规] docs/50 本体未入 manifest (镜像 574/577 先例) — 显式 SKIP.
  - docs/45-stage2-s210-lite-gate2-review-index-20260826.md (MODIFIED):
    文首第三刀刷新行 + §1 一段 + §3 O3 行尾注 (引擎已裁定 paddle-ocr)
    + §5.5 尾 O3 bullet 行尾注 (per 579) + §7 链头 904 → 907
    (knife 577 demote).
  - reviews/.../578-stage0-architect-s577-o1-close-s21full-audit-PASS-*
    (架构师资产, 只读随刀入库).
  - reviews/.../579-stage0-cc-o3-memo-inherited-failures-docs-bundle-
    receipt-*.md (本刀回执).
  - scripts/_knife579_manifest_bump.py (本文件).

COUNT CHECK (枚举即权威, 逐项核对): tasking 579 §E 标注 NEW +3 (bump 脚本
+ 578 审计文件 + 579 回执), 实测 3 个路径均不在 manifest — 无偏差
(577 §F 计数标注错误未复发).

前置 knife 577 已落 889 → 904; 本刀 +3 = 907.

NEW_ARTIFACTS = +3 → 904 → 907
REFRESH_ARTIFACTS = docs/45 + docs/50 (skip) + docs/53 + 00-EXEC-QUEUE.md
  + 579 回执
  — 已在 manifest 的文件 SHA REFRESH 不增计数; 00-EXEC-QUEUE.md 自 577
    起已在 manifest (本刀 ACK/DELIVERED 改动 = SHA REFRESH 不增计数);
    支持二次执行: 回执粘贴 bump 输出后再跑一次, 将回执自身 SHA 刷至最终态.

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
    ("scripts/_knife579_manifest_bump.py", "spike_helper"),
    (R + "578-stage0-architect-s577-o1-close-s21full-audit-PASS-20260828.md",
     "documentation"),
    (R + "579-stage0-cc-o3-memo-inherited-failures-docs-bundle-receipt-20260828.md",
     "documentation"),
]

# 已在 manifest 的文件: SHA REFRESH 不增计数 (tasking 579 §E).
REFRESH_ARTIFACTS = [
    "docs/45-stage2-s210-lite-gate2-review-index-20260826.md",
    "docs/50-stage2-gate2-review-packet-draft-20260826.md",
    "docs/53-stage2-public-ingest-ops-handbook-20260826.md",
    R + "00-EXEC-QUEUE.md",
    R + "579-stage0-cc-o3-memo-inherited-failures-docs-bundle-receipt-20260828.md",
]

EXPECTED_COUNT = 907  # 904 + 3 (per §E 枚举即权威; 实测无偏差)


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
    assert new_count == EXPECTED_COUNT, (
        f"INVARIANT BROKEN: artifact_count={new_count} != expected "
        f"{EXPECTED_COUNT} (904 + 3; tasking §E 枚举即权威, 实测无偏差)"
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
