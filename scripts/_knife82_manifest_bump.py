#!/usr/bin/env python3
"""Knife 82 bump script — 首页四轨一览 overview 显式 deeplink (tasking 432).

落地:
  - frontend/app/page.tsx (MODIFIED — 已入 manifest; bump SKIP, SHA REFRESH
    不增计数 per knife 44 先例): 公开提取表内湖北行后新增「公开提取四轨一览
    (overview strip)」行; href `/public-extracts#overview`; 新增
    `data-testid="home-public-extracts-overview"`; 描述列「stats.gov.cn /
    sz.gov.cn / tjj.hubei.gov.cn 7 列 × 4 行 overview (轨 / domain / category
    / 行数 / SHA 前 8 / demo|candidate 标注 / 分节锚点; 数据只读自既有 4 fixture,
    不重算; per 回执 `383`; smoke §12f 门)」; 数据模式标
    `OVERVIEW · 四轨 demo · 非 O1`; 镜像 knife 76 tasking 420 NBS sample 行 +
    knife 78 tasking 424 NBS live 行 + knife 67 tasking 394 湖北 #track-hb 行.
  - frontend/smoke-check.py (MODIFIED — 已入 manifest; bump SKIP): §12b''' 新增
    4 针 (href + testId + OVERVIEW / 四轨 demo / 非 O1 + 综合 PASS).
  - tests/test_overview_home_deeplink_public_extract.py (NEW, role
    schema_negative_test): 3 pytest cases (de 行内容 / 5 省 + 10 城 CityPage/
    CityPageMart 无 #overview 污染 / 4 fixture byte SHA 前 8 锁不漂:
    nbs=e30ee811/nbs_live=9232efdb/sz=937255a5/hb=9056001c, 与 knife 76/78/80/81
    锁值完全一致).
  - scripts/_knife82_manifest_bump.py (本文件)
  - reviews/.../432-stage0-cc-home-overview-deeplink-receipt-20260826.md

前置 knife 81 已落 pack (741 → 743); 本刀 +3 = pytest + bump + receipt
→ 743 → 746; page.tsx + smoke 皆 SHA REFRESH 不增计数.

NEW_ARTIFACTS = +3 → 743 → 746

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
        "tests/test_overview_home_deeplink_public_extract.py",
        "schema_negative_test",
    ),
    (
        "scripts/_knife82_manifest_bump.py",
        "spike_helper",
    ),
    (
        "reviews/stage0-gate0-rework-2026-08-23/"
        "432-stage0-cc-home-overview-deeplink-receipt-20260826.md",
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