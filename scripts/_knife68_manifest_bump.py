#!/usr/bin/env python3
"""Knife 68 bump script — /public-extracts 四轨轻量行筛选 (tasking 397).

落地:
  - frontend/app/public-extracts/page.tsx (MODIFIED — 已入 manifest; bump
    SKIP, SHA REFRESH 不增计数 per knife 44 先例):
    * "use client" + 4 useState (nbsSampleFilter / nbsLiveFilter / szFilter /
      hbFilter — 每轨独立) + filterRows (单元格文本包含匹配, 大小写不敏感,
      空查询=全量) + TrackFilterInput (受控 input, testId 渲染为 data-testid,
      匹配 X/Y 计数行 + 非权威库检索守门文案);
    * 4 数据表各增筛选 input; 4 tbody 改消费 filtered*Rows 视图数组 +
      空匹配占位行 (无匹配行 — 客户端筛选 demo 数据, 非权威库检索);
    * 静态路由不变 (无 params.*, 无 fetch), build 仍 ○ Static.
  - frontend/smoke-check.py (MODIFIED — 已入 manifest; bump SKIP): §12h 门
    (use client / useState / data-testid={props.testId} / 4 个 testId /
    toLowerCase().includes / 匹配计数 / 非权威库检索 / 无匹配行, 11 针)
  - tests/test_public_extract_frontend_fixture.py (MODIFIED — 已入 manifest;
    bump SKIP): +3 cases (24 → 27) — input 在位 + 受控绑定; 客户端包含匹配
    逻辑 + fetch 禁止; 守门 (非权威库/视图过滤/空匹配占位/demo 标注不受影响)
  - scripts/_knife68_manifest_bump.py (本文件)
  - reviews/.../398-stage0-cc-public-extracts-row-filter-receipt-20260826.md

前置 knife 67 已落 新测文件+recept 入 pack (703 → 706); 本刀 +2 = bump +
receipt → 706 → 708; page.tsx / smoke-check.py / 测试文件皆 SHA REFRESH
不增计数.

NEW_ARTIFACTS = +2 → 706 → 708

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
        "scripts/_knife68_manifest_bump.py",
        "spike_helper",
    ),
    (
        "reviews/stage0-gate0-rework-2026-08-23/"
        "398-stage0-cc-public-extracts-row-filter-receipt-20260826.md",
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
