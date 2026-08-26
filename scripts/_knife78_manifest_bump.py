#!/usr/bin/env python3
"""Knife 78 bump script — 首页 NBS live 候选轨 deeplink (tasking 424).

落地:
  - frontend/app/page.tsx (MODIFIED — 已入 manifest; bump SKIP, SHA REFRESH
    不增计数 per knife 44 先例): 公开提取表新增「公开提取 NBS live 候选轨
    (candidate demo)」行 (镜像 NBS sample #track-nbs-sample 行 + 湖北
    #track-hb 行); href /public-extracts#track-nbs-live + testId
    home-public-extracts-nbs-live; 文案标明 LIVE_CANDIDATE / drift 候选 /
    非 O1 收口.
  - frontend/smoke-check.py (MODIFIED — 已入 manifest; SHA REFRESH 不增计数):
    新增 §12b'' 4 针: href + testId + LIVE_CANDIDATE / drift 候选 / 非 O1
    收口 标注 + 综合 PASS 行.
  - tests/test_nbs_live_home_deeplink_public_extract.py (NEW)
  - scripts/_knife78_manifest_bump.py (本文件)
  - reviews/.../424-stage0-cc-nbs-live-home-deeplink-receipt-20260826.md

前置 knife 77 已落 pack (732 → 734); 本刀 +3 (pytest + bump + receipt) =
bump → 734 → 737; frontend/app/page.tsx 与 frontend/smoke-check.py 皆已入
manifest, SHA REFRESH 不增计数.

NEW_ARTIFACTS = +3 → 734 → 737

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
        "tests/test_nbs_live_home_deeplink_public_extract.py",
        "schema_negative_test",
    ),
    (
        "scripts/_knife78_manifest_bump.py",
        "spike_helper",
    ),
    (
        "reviews/stage0-gate0-rework-2026-08-23/"
        "424-stage0-cc-nbs-live-home-deeplink-receipt-20260826.md",
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
