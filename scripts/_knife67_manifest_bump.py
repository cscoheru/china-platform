#!/usr/bin/env python3
"""Knife 67 bump script — 湖北观察页链到公开提取轨 (tasking 394).

落地:
  - frontend/app/page.tsx (MODIFIED — 已入 manifest; bump SKIP, SHA REFRESH
    不增计数 per knife 44 先例):
    * 公开提取表格 + 一行「公开提取湖北轨（xlsx demo）」:
      `/public-extracts#track-hb` 链 + tjj.hubei.gov.cn PROVINCIAL_BULLETIN
      21 行 xlsx 说明 + REGISTRY_SAMPLE / xlsx / demo / live enabled=FALSE
      暂缓 / 非 live O1 四项提示 (per 394 §SCHEMA-1 兜底: 无湖北专用页 →
      首页行; /provinces/ 仅 5 省, 10 城 slug 无湖北城市).
  - frontend/smoke-check.py (MODIFIED — 已入 manifest; bump SKIP): §13b 门
    (首页湖北轨行 + #track-hb 链 + PROVINCIAL_BULLETIN + enabled=FALSE +
    非 live O1 5 针)
  - tests/test_hubei_home_link_public_extract.py (NEW — schema_negative_test):
    2 cases (首页湖北轨行 4 针 + 无污染: /provinces/* 与 CityPage/Mart 不得
    出现 #track-hb 链)
  - scripts/_knife67_manifest_bump.py (本文件)
  - reviews/.../395-stage0-cc-hubei-home-link-public-extract-receipt-20260826.md

前置 knife 66 已落 新测文件 入 pack (700 → 703); 本刀 +3 = 1 新测文件 +
bump + receipt → 703 → 706; page.tsx / smoke-check.py 皆 SHA REFRESH 不增计数.

NEW_ARTIFACTS = +3 → 703 → 706

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
        "tests/test_hubei_home_link_public_extract.py",
        "schema_negative_test",
    ),
    (
        "scripts/_knife67_manifest_bump.py",
        "spike_helper",
    ),
    (
        "reviews/stage0-gate0-rework-2026-08-23/"
        "395-stage0-cc-hubei-home-link-public-extract-receipt-20260826.md",
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