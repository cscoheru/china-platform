#!/usr/bin/env python3
"""Knife 56 bump script — LIVE_CANDIDATE 一键刷新 CLI (tasking 361).

落地:
  - scripts/auto_ingest_public_source.py (MODIFIED — 已入 manifest; bump SKIP)
    * --refresh-live-candidate flag: live 流水线跑通后 (壳门/deeplink/
      WORM/SHA) 双写 LIVE_CANDIDATE 轨 — data 侧
      {domain}/{category}_LIVE_CANDIDATE.json + NBS 前端 fixture
      byte-verbatim 同步 (write_live_candidate_files; 形状同 knife 55)
    * 无 --live 时拒绝 (rc=6): refresh 即 live, 同 confirm-live 授权纪律
    * get_frontend_lib_root(): CEGR_FRONTEND_LIB_ROOT env > 默认
      frontend/lib (352 同款 pytest 重定向纪律)
    * drift/match 两分支挂钩; AUTH/transport/tech-blocked 早退路径零改动
  - tests/test_auto_ingest_public_source_s52.py (MODIFIED — 已入 manifest;
    bump SKIP)
    * autouse fixture + setenv CEGR_FRONTEND_LIB_ROOT (护已提交 fixture)
    * +4 case (361 §SCHEMA 4 ≥4):
      test_refresh_writes_candidate_double_track /
      test_refresh_does_not_touch_sample_track /
      test_refresh_tech_blocked_writes_no_candidate /
      test_refresh_requires_live_authorization
  - scripts/_knife56_manifest_bump.py (本文件)
  - reviews/.../362-stage0-cc-live-candidate-refresh-receipt-20260826.md

sample 分轨锁定: sample JSON / sample fixture / registry 哈希零改动
(pytest 字节级前后对比 + git status 干净双证)。

NEW_ARTIFACTS = +2 → 671 → 673

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
        "scripts/_knife56_manifest_bump.py",
        "spike_helper",
    ),
    (
        "reviews/stage0-gate0-rework-2026-08-23/"
        "362-stage0-cc-live-candidate-refresh-receipt-20260826.md",
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
