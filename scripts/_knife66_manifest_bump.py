#!/usr/bin/env python3
"""Knife 66 bump script — 深圳城页链到公开提取轨 (tasking 391).

落地:
  - frontend/app/components/CityPage.tsx (MODIFIED — 已入 manifest; bump SKIP,
    SHA REFRESH 不增计数 per knife 44 先例):
    * 新增条件分支 `city.slug === 'shenzhen'` → `<section
      data-testid="city-page-public-extract-link">`, 含
      `<a href="/public-extracts#track-sz">` 链 + REGISTRY_SAMPLE demo
      标注 + 非 O1 守门 + 与 mock 观察卡互不覆盖声明.
  - frontend/app/components/CityPageMart.tsx (MODIFIED — 已入 manifest;
    bump SKIP): 镜像同上 (mart-shape 路径), 条件 `mart.cityId === 'shenzhen'`.
  - frontend/smoke-check.py (MODIFIED — 已入 manifest; bump SKIP): §13 门
    (CityPage.tsx + CityPageMart.tsx 各含 shenzhen 条件 + /public-extracts#track-sz
    链 + REGISTRY_SAMPLE demo + 非 O1 守门)
  - tests/test_shenzhen_city_link_public_extract.py (NEW — schema_negative_test):
    3 cases (CityPage 含 shenzhen 条件 + 链 + demo + 非 O1 + CityPageMart 同 + 链
    必须条件化, 不出现在条件之前)
  - scripts/_knife66_manifest_bump.py (本文件)
  - reviews/.../392-stage0-cc-shenzhen-city-link-public-extract-receipt-20260826.md

前置 knife 65 已落 4 public JSON 拷贝入 pack (694 → 700); 本刀 +3 = 1 新测
文件 + bump + receipt → 700 → 703; page.tsx / CityPage*.tsx / smoke-check.py
皆 SHA REFRESH 不增计数.

NEW_ARTIFACTS = +3 → 700 → 703

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
        "tests/test_shenzhen_city_link_public_extract.py",
        "schema_negative_test",
    ),
    (
        "scripts/_knife66_manifest_bump.py",
        "spike_helper",
    ),
    (
        "reviews/stage0-gate0-rework-2026-08-23/"
        "392-stage0-cc-shenzhen-city-link-public-extract-receipt-20260826.md",
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