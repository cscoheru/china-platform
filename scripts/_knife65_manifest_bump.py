#!/usr/bin/env python3
"""Knife 65 bump script — 四轨 JSON 静态下载 (tasking 388).

落地:
  - frontend/public/public-extracts/nbs.json (NEW — 字节一致拷自
    frontend/lib/public_extract_nbs.json; size=7183; sha e30ee811…)
  - frontend/public/public-extracts/nbs-live-candidate.json (NEW — 字节一致拷自
    frontend/lib/public_extract_nbs_live_candidate.json; size=13025; sha 9232efdb…)
  - frontend/public/public-extracts/sz.json (NEW — 字节一致拷自
    frontend/lib/public_extract_sz.json; size=24021; sha 937255a5…)
  - frontend/public/public-extracts/hubei.json (NEW — 字节一致拷自
    frontend/lib/public_extract_hubei.json; size=2907; sha 9056001c…)
  - frontend/app/public-extracts/page.tsx (MODIFIED — 已入 manifest; bump SKIP,
    SHA REFRESH 不增计数 per knife 44 先例):
    * header 注释更新 (per 388)
    * overview 表增「下载 JSON」列 (8 列) + 4 download 链 (nbs /
      nbs-live-candidate / sz / hubei; download attr + /public-extracts/*.json 锚)
  - frontend/smoke-check.py (MODIFIED — 已入 manifest; bump SKIP): §12g 门
    (4 public 文件字节 == fixture 字节 + 4 字节相等 + 4 download 链 + 4 download attr)
  - tests/test_public_extract_frontend_fixture.py (MODIFIED — 已入 manifest;
    bump SKIP): +5 cases (4 parametrized byte-identical + 1 page renders
    download column & links)
  - scripts/_knife65_manifest_bump.py (本文件)
  - reviews/.../389-stage0-cc-public-extracts-json-download-receipt-20260826.md

前置 knife 64 已落 docs/45/53 overview strip 登记入 pack (692 → 694);
本刀 +6 = 4 public 字节拷贝 (data_contract_suite) + bump + receipt →
694 → 700; page.tsx / smoke-check.py / 测 皆 SHA REFRESH 不增计数.

NEW_ARTIFACTS = +6 → 694 → 700

Recomputes role_count from artifacts (source of truth, per knife 16 fix).
"""
from __future__ import annotations

import hashlib
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
MANIFEST = ROOT / "evidence_pack" / "manifest.json"

NEW_ARTIFACTS = [
    # 4 public 字节一致拷贝 (data_contract_suite, per knife 58/61 precedent)
    (
        "frontend/public/public-extracts/nbs.json",
        "data_contract_suite",
    ),
    (
        "frontend/public/public-extracts/nbs-live-candidate.json",
        "data_contract_suite",
    ),
    (
        "frontend/public/public-extracts/sz.json",
        "data_contract_suite",
    ),
    (
        "frontend/public/public-extracts/hubei.json",
        "data_contract_suite",
    ),
    (
        "scripts/_knife65_manifest_bump.py",
        "spike_helper",
    ),
    (
        "reviews/stage0-gate0-rework-2026-08-23/"
        "389-stage0-cc-public-extracts-json-download-receipt-20260826.md",
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