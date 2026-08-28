#!/usr/bin/env python3
"""Knife 581 bump script — 继承 4 failed 修复刀（恢复全量套件全绿）
(tasking 581; 架构师治理模型第四刀, 经 00-EXEC-QUEUE.md 签发;
零生产代码/零 SQL/零脚本变更 — 三处断言口径修正 + 白名单房规化).

落地 (合刀 A–H 同 commit、单槽单回执; 全量 pytest 0 failed 为核心证据):
  - tests/test_public_extract_frontend_fixture.py (MODIFIED, 在册 REFRESH):
    provenance 断言改 fixture.source_sha256 == sha256(sample.html 实字节)
    活锚定 + 三对象 docstring (registry a7e4029d 不变 / fixture 演示快照
    链自洽 / 原断言两对象错绑 per 580 审计定性).
  - tests/test_auto_ingest_public_source_s52.py (NOT-IN manifest → ADD):
    拆双路径 sz pilot 成功路径零改动 / stats pilot 预期 rc=8
    stderr "SHA mismatch; refusing intake" + 零落盘;
    scripts/auto_ingest_public_source.py 零改动 — SHA 闸零弱化 =
    转测试预期非放行.
  - tests/test_cleanliness.py (MODIFIED, 在册 REFRESH):
    allowed_top_level 扩 4 目录 (seeds S2.1 demo / public_extracts +
    public_archives WORM / seed_archives 归档链) — 房规化登记存量合法
    非放宽.
  - docs/53-stage2-public-ingest-ops-handbook-20260826.md (MODIFIED):
    §5 新增第 43 项 继承 4 failed 修复登记 (根因两对象两 SHA 错绑 +
    修法三则 + 修复后全量实跑证据 + 登记→修复闭环落定).
  - docs/50-stage2-gate2-review-packet-draft-20260826.md (MODIFIED):
    §4.4 +1 第 43 项行 + intro 链尾 → 579 续接 → 581;
    §5.1「继承 4 failed」行 append 处置标注 (不删既有 OPEN 行).
    [房规] docs/50 本体未入 manifest (镜像 574/577/579 先例) — SKIP.
  - docs/45-stage2-s210-lite-gate2-review-index-20260826.md (MODIFIED):
    文首 +1 刷新行 + §1 +1 修复登记段 + §5.5 尾 O1 bullet 行尾注
    (落点族 per 580 审计 ⚠2 统一「§5.5 尾 O1/O3 bullet」) +
    §7 链头 907 → 911 + knife 581 demote; §3 零涉.
  - reviews/.../580-stage0-architect-s579-o3-memo-inherited-audit-PASS-
    20260828.md (架构师资产, 只读随刀入库; ADD).
  - reviews/.../581-stage0-cc-inherited-4failed-fix-suite-green-receipt-
    20260828.md (本刀回执; ADD).
  - scripts/_knife581_manifest_bump.py (本文件; ADD).

COUNT CHECK (枚举即权威, 逐项核对): tasking 581 §F 标注 NEW +4
(bump 脚本 + 581 回执 + 580 审计 + s52 测试), 实测 4 个路径均不在
manifest — 无偏差.

前置 knife 579 已落 904 → 907; 本刀 +4 = 911.

NEW_ARTIFACTS = +4 → 907 → 911
REFRESH_ARTIFACTS = test_cleanliness.py + test_public_extract_frontend_
  fixture.py + docs/45 + docs/53 + 00-EXEC-QUEUE.md + 581 回执
  — 已在 manifest 的文件 SHA REFRESH 不增计数; 00-EXEC-QUEUE.md 自 577
    起已在 manifest (本刀 ACK/DELIVERED 改动 = SHA REFRESH 不增计数);
    支持二次执行: 回执粘贴 bump 输出后再跑一次, 将回执自身 SHA 刷至
    最终态 (两阶段 paste+refresh 模式 per 577 先例).

⚠3 教训 (per tasking §F): 先实测每路径 bump 前状态再定 ADD/REFRESH,
标注必须与枚举一致.

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
    ("scripts/_knife581_manifest_bump.py", "spike_helper"),
    (R + "581-stage0-cc-inherited-4failed-fix-suite-green-receipt-20260828.md",
     "documentation"),
    (R + "580-stage0-architect-s579-o3-memo-inherited-audit-PASS-20260828.md",
     "documentation"),
    ("tests/test_auto_ingest_public_source_s52.py", "schema_negative_test"),
]

# 已在 manifest 的文件: SHA REFRESH 不增计数 (tasking 581 §F).
# docs/50 按房规 SKIP (574/577/579 先例).
REFRESH_ARTIFACTS = [
    "tests/test_cleanliness.py",
    "tests/test_public_extract_frontend_fixture.py",
    "docs/45-stage2-s210-lite-gate2-review-index-20260826.md",
    "docs/53-stage2-public-ingest-ops-handbook-20260826.md",
    R + "00-EXEC-QUEUE.md",
    R + "581-stage0-cc-inherited-4failed-fix-suite-green-receipt-20260828.md",
]

EXPECTED_COUNT = 911  # 907 + 4 (per §F 枚举即权威; 实测无偏差)


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
        f"{EXPECTED_COUNT} (907 + 4; tasking §F 枚举即权威, 实测无偏差)"
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
