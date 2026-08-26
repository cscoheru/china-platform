#!/usr/bin/env python3
"""Knife 52 bump script — public-extract frontend wire (tasking 349).

落地:
  - frontend/lib/public_extract_nbs.json
    (build-time fixture; 快照自 data/public_extracts/stats.gov.cn/
    NATIONAL_BULLETIN.json 63 行; resolveJsonModule 导入)
  - frontend/app/public-extracts/page.tsx
    (专用静态路由; REGISTRY_SAMPLE · demo 显式标注; DemoBadge 复用;
    provenance 表含 source_sha256; 63 行全量展示; 禁词扫描通过)
  - tests/test_public_extract_frontend_fixture.py
    (7 case: row_count=63 / registry SHA 锚定 / sample path 锚定 /
    首行键形 / 页面标注 / 非 live O1 免责 / 首页导航链接)
  - frontend/app/page.tsx (MODIFIED — 未入 manifest,同 knife 280 homepage
    先例;bump SKIP)
  - frontend/smoke-check.py (MODIFIED — knife 52 §12 gate;bump SKIP)
  - scripts/_knife52_manifest_bump.py (本文件)
  - reviews/.../350-stage2-public-extract-frontend-wire-receipt-20260826.md

NEW_ARTIFACTS = +5 → 658 → 663

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
        "frontend/lib/public_extract_nbs.json",
        "data_contract_suite",
    ),
    (
        "frontend/app/public-extracts/page.tsx",
        "spike_helper",
    ),
    (
        "tests/test_public_extract_frontend_fixture.py",
        "schema_negative_test",
    ),
    (
        "scripts/_knife52_manifest_bump.py",
        "spike_helper",
    ),
    (
        "reviews/stage0-gate0-rework-2026-08-23/"
        "350-stage2-public-extract-frontend-wire-receipt-20260826.md",
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
