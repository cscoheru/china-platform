#!/usr/bin/env python3
"""Knife 89 bump script — china.3strategy.cc 预览 redeploy + 首页 deeplink HTTP 验收 (tasking 446).

落地:
  - 预览 redeploy（newvps 207.57.133.177 /opt/china-platform；rsync + npm ci +
    NEXT_PUBLIC_USE_MOCK=true npm run build + restart）由 ops 侧完成（per 用户
    2026-08-27 指示「在 newvps 上 rsync + build + restart」）；CC 自动分类器
    拦截生产写入，CC 未直接执行 deploy 命令。
  - CC 交付：HTTP 验收（curl 公网 china.3strategy.cc）+ 回执 446：
    首页 4/4 deeplink 在位 + /public-extracts 200 + 5 锚点 + site-nav + 4 行筛选。
  - scripts/_knife89_manifest_bump.py (本文件)
  - reviews/.../446-stage0-cc-preview-redeploy-home-deeplinks-receipt-20260826.md

前置 knife 88 已落 pack (756 → 758); 本刀 +2 = bump + receipt → 758 → 760.

NEW_ARTIFACTS = +2 → 758 → 760

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
        "scripts/_knife89_manifest_bump.py",
        "spike_helper",
    ),
    (
        "reviews/stage0-gate0-rework-2026-08-23/"
        "446-stage0-cc-preview-redeploy-home-deeplinks-receipt-20260826.md",
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