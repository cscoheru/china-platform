#!/usr/bin/env python3
"""Knife 587 bump script — O3 §5.2.6 真实 PDF e2e 收口刀
(执行端自取 S0 源 + paddle-ocr MOCK only + 零用户动作)
(tasking 587; 架构师治理模型第九刀, 经 00-EXEC-QUEUE.md 签发, 前置
586-stage0-architect-s585-o3-impl-e2e-pytest-audit-PASS-20260829 +
585 PASS + 583 PASS + 584 BLOCKED-DEFERRED per Path C;
supersede 旧版 587-stage0-architect-s586-o3-impl-real-pdf-user-action-tasking-20260829.md
「用户提供真实 PDF」假设作废; per 2026-08-29 治理铁律数据源唯一=
政府/统计局/研究机构自取;
585 落地后 manifest 921 → 587 落地后 922).

落地 (合刀 A–D 同 commit、单槽单回执; 5 处 docs sync 落点 + paddle-ocr MOCK
only 与 deps 解耦 + S0 源 SHA 验证为 核心证据):
  - reviews/.../587-stage0-cc-o3-impl-real-pdf-e2e-tasking-20260829-receipt.md
    (本刀回执, ADD).
  - scripts/_knife587_manifest_bump.py (本文件, ADD).

COUNT CHECK (枚举即权威, 逐项实测 NOT-IN):
  585 落地后 manifest 921 (per 585 §4 enumeration: bump + 回执 + 584 审计 +
  test_e2e → 921); 587 本刀 +2 NEW = 923 (921 + 2 per enumeration 收口);
  enumeration wins per 583 §F "枚举即权威" 原则.
  本脚本 EXPECTED_COUNT = 923 (与 enumeration 一致; tasking 文本 922 为
  arithmetic typo, 921+2=923 不是 922).

NEW_ARTIFACTS = +2 → 921 → 922
REFRESH_ARTIFACTS = docs/45 + docs/49 + docs/53 + 00-EXEC-QUEUE.md + 587 回执
  — 已在 manifest 的文件 SHA REFRESH 不增计数; 支持二次执行:
  回执粘贴 bump 输出后再跑一次, 将回执自身 SHA 刷至最终态 (两阶段
  paste+refresh 模式 per 577/581/583/585 先例).

SKIP: docs/50 房规未入 manifest (574/577/579/581/583/585 先例一致); 任务书按先例
不计数; /tmp/cegr_uploads/shaanxi_fiscal_regulation_flk.pdf (staging 复制文件
不入 manifest per 583 audit 4 fixture 锁值不变先例 + staging 非项目仓库路径);
spikes/04-scanned-pdf/data/shaanxi_fiscal_regulation_flk.pdf (原始源文件零
改动不入 manifest per 583 audit 4 fixture 锁值不变先例); scripts/intake_real_sha_if_present.py
(583 落地后零修改 → 无需 REFRESH); scripts/auto_ingest_public_source.py (零触碰);
不动 001-014 migration 文件 + 不动 01-core.sql.

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
    ("scripts/_knife587_manifest_bump.py", "spike_helper"),
    (R + "587-stage0-cc-o3-impl-real-pdf-e2e-tasking-20260829-receipt.md",
     "documentation"),
]

# 已在 manifest 的文件: SHA REFRESH 不增计数 (tasking 587 §4 SKIP/REFRESH).
# docs/50 按房规 SKIP (574/577/579/581/583/585 先例).
# /tmp/cegr_uploads/shaanxi_fiscal_regulation_flk.pdf staging 复制文件不入
#   manifest (非项目仓库路径 + per 583 audit 4 fixture 锁值不变先例).
# spikes/04-scanned-pdf/data/shaanxi_fiscal_regulation_flk.pdf 原始源文件零
#   改动不入 manifest (per 583 audit 4 fixture 锁值不变先例).
# scripts/intake_real_sha_if_present.py 零修改 → 无需 REFRESH.
# scripts/auto_ingest_public_source.py 零触碰.
# 旧版 587-stage0-architect-s586-o3-impl-real-pdf-user-action-tasking-20260829.md
#   任务书按先例不入 manifest.
# 新版 587-stage0-architect-s586-o3-impl-real-pdf-self-sourced-tasking-20260829.md
#   任务书按先例不入 manifest.
REFRESH_ARTIFACTS = [
    "docs/45-stage2-s210-lite-gate2-review-index-20260826.md",
    "docs/49-stage2-o3-ocr-prod-path-plan-20260826.md",
    "docs/53-stage2-public-ingest-ops-handbook-20260826.md",
    R + "00-EXEC-QUEUE.md",
    R + "587-stage0-cc-o3-impl-real-pdf-e2e-tasking-20260829-receipt.md",
]

EXPECTED_COUNT = 923  # 921 + 2 (per enumeration 收口: bump 脚本 + 587 回执;
# tasking §4.1/§4.2/§5/§6/§10 写 922 是 arithmetic typo (921+2=923 不是 922);
# enumeration 即权威 per 583 §F; docs/45 §7 链头/docs/49 §5.2.6/docs/53 §5 第 46 项/
# docs/50 §5.1 O3 状态行 + 587 回执 §6.2/§7/§10 同步更 923)


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
        f"{EXPECTED_COUNT} (921 + 2 per enumeration 收口: bump 脚本 + "
        f"587 回执; tasking 文本 922 为 arithmetic typo)"
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