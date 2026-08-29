#!/usr/bin/env python3
"""Knife 585 bump script — O3 §5.2.5 e2e pytest 刀 (paddle-ocr MOCK only +
§584 audit ⚠1 docs sync patch 5/6 处 closure)
(tasking 585; 架构师治理模型第七刀, 经 00-EXEC-QUEUE.md 签发, 前置
584-stage0-architect-s584-o3-impl-paddle-ocr-deps-audit-BLOCKED-20260829
(Path C 采纳 = paddle-ocr deps 引入走后续刀 + 585 e2e pytest 刀 paddle-ocr
MOCK only 与 deps 解耦) + 582 审计 PASS + 583 实装首刀 PASS;
583 落地后 manifest 917 → 585 落地后 921).

落地 (合刀 A–D 同 commit、单槽单回执; 9/9 pytest PASS 为核心证据):
  - tests/test_o3_e2e_585.py (NEW, test_e2e):
    9 例覆盖 = ① syn-PDF bytes construction ② validate_ocr_input ACCEPT
    for syn-PDF in upload prefix ③ REJECT_OUTSIDE_ALLOWLIST for syn-PDF
    outside ④ doc_kind gate after ACCEPT ⑤ paddle-ocr MOCK call
    (patch.dict(sys.modules, {"paddleocr": MagicMock(PaddleOCR=cls_mock)}))
    ⑥ source_document mock writer 捕获 row dict + lineage JSONB
    ⑦ lineage JSONB structure ⑧ 零真实 paddle-ocr API 调用断言
    (engine.__class__.__name__ == "MagicMock") ⑨ §584 audit ⚠1 docs sync
    落点验证 (5/6 处 stale 916 = 0 + 917 ≥ 3).
  - reviews/.../584-stage0-architect-s584-o3-impl-paddle-ocr-deps-audit-
    BLOCKED-20260829.md (架构师资产, 只读随刀入库, ADD; per 581 先例
    580 audit ADD in 581 bump; per 583 先例 582 audit ADD in 583 bump).
  - reviews/.../585-stage0-cc-o3-impl-e2e-pytest-tasking-20260829-receipt.md
    (本刀回执, ADD).
  - scripts/_knife585_manifest_bump.py (本文件, ADD).

COUNT CHECK (枚举即权威, 逐项实测 NOT-IN):
  583 落地后 manifest 917 (per 583 §E enumeration: 014.sql + 014.log 双 ADD
  → 917); 585 本刀 +4 NEW = 921 (917 + 4 per enumeration 收口);
  enumeration wins per 583 §F "枚举即权威" 原则.
  本脚本 EXPECTED_COUNT = 921 (与 enumeration 一致).

NEW_ARTIFACTS = +4 → 917 → 921
REFRESH_ARTIFACTS = docs/45 + docs/49 + docs/50 + docs/53 + 00-EXEC-QUEUE.md
  + 585 回执 — 已在 manifest 的文件 SHA REFRESH 不增计数; 支持二次执行:
  回执粘贴 bump 输出后再跑一次, 将回执自身 SHA 刷至最终态 (两阶段
  paste+refresh 模式 per 577/581/583 先例).

SKIP: docs/50 房规未入 manifest (574/577/579/581/583 先例一致); 任务书按先例
不计数; tests/fixtures/_syn_pdf_585.py (fixture 不入 manifest per 583 audit
4 fixture 锁值不变先例); scripts/intake_real_sha_if_present.py (583 落地后
零修改 → 无需 REFRESH); scripts/auto_ingest_public_source.py (零触碰); 不动
001-014 migration 文件 + 不动 01-core.sql.

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
    ("scripts/_knife585_manifest_bump.py", "spike_helper"),
    (R + "585-stage0-cc-o3-impl-e2e-pytest-tasking-20260829-receipt.md",
     "documentation"),
    (R + "585-stage0-architect-s584-o3-impl-paddle-ocr-deps-audit-BLOCKED-20260829.md",
     "documentation"),
    ("tests/test_o3_e2e_585.py", "test_e2e"),
]

# 已在 manifest 的文件: SHA REFRESH 不增计数 (tasking 585 §D SKIP/REFRESH).
# docs/50 按房规 SKIP (574/577/579/581/583 先例).
# tests/fixtures/_syn_pdf_585.py fixture 不入 manifest (per 583 audit 4 fixture
# 锁值不变先例).
# scripts/intake_real_sha_if_present.py 零修改 → 无需 REFRESH.
REFRESH_ARTIFACTS = [
    "docs/45-stage2-s210-lite-gate2-review-index-20260826.md",
    "docs/49-stage2-o3-ocr-prod-path-plan-20260826.md",
    "docs/50-stage2-gate2-review-packet-draft-20260826.md",
    "docs/53-stage2-public-ingest-ops-handbook-20260826.md",
    R + "00-EXEC-QUEUE.md",
    R + "585-stage0-cc-o3-impl-e2e-pytest-tasking-20260829-receipt.md",
]

EXPECTED_COUNT = 921  # 917 + 4 (per enumeration 收口: bump 脚本 +
                      # 585 回执 + 584 审计文件 + test_e2e 角色)


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
        f"{EXPECTED_COUNT} (917 + 4 per enumeration 收口: bump 脚本 + "
        f"585 回执 + 584 审计文件 + test_e2e 角色)"
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