#!/usr/bin/env python3
"""Knife 72 bump script — 全站顶栏 /public-extracts 常驻链 (tasking 409).

落地:
  - frontend/app/layout.tsx (MODIFIED — 已入 manifest; bump SKIP, SHA REFRESH
    不增计数 per knife 44 先例): <nav data-testid="site-nav"> + 首页 +
    /public-extracts 链 + 旁注「全站顶栏常驻链；四轨 demo / 非 O1 / 不宣布
    Gate PASS（per tasking 409）」; 纯 <a href> 锚链未引入 next/link; 不分支
    params.* (AGENTS.md 静态路由红线).
  - frontend/smoke-check.py (MODIFIED — 已入 manifest; bump SKIP): + §13c 门
    6 针 (site-nav 容器 + /public-extracts 链 + 链 testId + 四轨 demo + 非 O1
    + 不宣布 Gate PASS + 不分支 params.*).
  - tests/test_layout_site_nav_public_extracts.py (NEW — schema_negative_test):
    5 cases (container / link / disclaimer / no-params-branch / anchor-not-Link).
  - scripts/_knife72_manifest_bump.py (本文件)
  - reviews/.../410-stage0-cc-layout-public-extracts-nav-receipt-20260826.md

前置 knife 70 已落 pack (710 → 718); knife 71 docs 登记 718 → 720;
本刀 +3 = test + bump + receipt → 720 → 723; layout.tsx / smoke-check.py
皆 SHA REFRESH 不增计数.

NEW_ARTIFACTS = +3 → 720 → 723

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
        "tests/test_layout_site_nav_public_extracts.py",
        "schema_negative_test",
    ),
    (
        "scripts/_knife72_manifest_bump.py",
        "spike_helper",
    ),
    (
        "reviews/stage0-gate0-rework-2026-08-23/"
        "410-stage0-cc-layout-public-extracts-nav-receipt-20260826.md",
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