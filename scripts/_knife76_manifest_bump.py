#!/usr/bin/env python3
"""Knife 76 bump script — 首页 NBS sample 轨显式 deeplink (tasking 420).

落地:
  - frontend/app/page.tsx (MODIFIED — 已入 manifest; bump SKIP, SHA REFRESH
    不增计数 per knife 44 先例): 公开提取表内"公开提取样本（四轨 demo）"
    行 → "公开提取 NBS sample 轨（demo）" 行, href 从 /public-extracts
    改为 /public-extracts#track-nbs-sample + 新 data-testid=
    "home-public-extracts-nbs-sample"; 文案保留 stats.gov.cn / NATIONAL_BULLETIN
    63 行; 数据模式标 "REGISTRY_SAMPLE · demo · 非 live O1".
  - frontend/smoke-check.py (MODIFIED — 已入 manifest; bump SKIP): §12b 后
    新增 §12b' 守门 (per tasking 420 §NOW-2 「≥1 smoke 或 pytest 针」):
    ① /public-extracts#track-nbs-sample href ② data-testid=
    home-public-extracts-nbs-sample ③ REGISTRY_SAMPLE / demo / 非 live O1
    标注 4 针.
  - tests/test_nbs_home_deeplink_public_extract.py (NEW) — pytest 守门:
    ① test_home_page_has_nbs_sample_deeplink (de 行 + href + testId +
       REGISTRY_SAMPLE / 非 O1) ② test_no_nbs_deeplink_pollutes_province_or_
       city_pages (5 省页 + 10 城 CityPage/Mart 无 #track-nbs-sample 污染)
       ③ test_no_fixture_byte_modified (4 fixture byte SHA 前 8 锁).
  - scripts/_knife76_manifest_bump.py (本文件)
  - reviews/.../420-stage0-cc-nbs-home-deeplink-receipt-20260826.md

前置 knife 75 已落 pack (727 → 729); 本刀 +3 = pytest + bump + receipt
→ 729 → 732; page.tsx / smoke-check.py 皆 SHA REFRESH 不增计数.

NEW_ARTIFACTS = +3 → 729 → 732

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
        "tests/test_nbs_home_deeplink_public_extract.py",
        "schema_negative_test",
    ),
    (
        "scripts/_knife76_manifest_bump.py",
        "spike_helper",
    ),
    (
        "reviews/stage0-gate0-rework-2026-08-23/"
        "420-stage0-cc-nbs-home-deeplink-receipt-20260826.md",
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