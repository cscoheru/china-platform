#!/usr/bin/env python3
"""Knife 55 bump script — live WORM extract + frontend LIVE_CANDIDATE (tasking 358).

落地:
  - data/public_extracts/stats.gov.cn/NATIONAL_BULLETIN_LIVE_CANDIDATE.json
    (NEW; live WORM 2026-08/stats.gov.cn/zxfb 435,469B sha=0b85212f… 一次性
    extract_tables 提取 60 行;intake_status=LIVE_CANDIDATE;is_demo=true
    per knife 333 CANDIDATE_AUTO 惯例)
  - frontend/lib/public_extract_nbs_live_candidate.json
    (NEW; byte-verbatim 快照; resolveJsonModule 导入)
  - frontend/app/public-extracts/page.tsx (MODIFIED — 已入 manifest; bump SKIP)
    (LIVE_CANDIDATE 分轨区块 + 非 O1 免责 + sample 注修正)
  - tests/test_public_extract_frontend_fixture.py (MODIFIED — 已入 manifest;
    bump SKIP; +4 case)
  - frontend/smoke-check.py (MODIFIED — knife 55 §12c gate; bump SKIP)
  - scripts/_knife55_manifest_bump.py (本文件)
  - reviews/.../359-stage0-cc-live-worm-frontend-candidate-receipt-20260826.md

sample 分轨不覆盖: NATIONAL_BULLETIN.json (63 行 / dea13b8a…) 与
frontend/lib/public_extract_nbs.json 均零改动 (§12c + pytest 双锁).

NEW_ARTIFACTS = +4 → 667 → 671

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
        "data/public_extracts/stats.gov.cn/"
        "NATIONAL_BULLETIN_LIVE_CANDIDATE.json",
        "data_contract_suite",
    ),
    (
        "frontend/lib/public_extract_nbs_live_candidate.json",
        "data_contract_suite",
    ),
    (
        "scripts/_knife55_manifest_bump.py",
        "spike_helper",
    ),
    (
        "reviews/stage0-gate0-rework-2026-08-23/"
        "359-stage0-cc-live-worm-frontend-candidate-receipt-20260826.md",
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
