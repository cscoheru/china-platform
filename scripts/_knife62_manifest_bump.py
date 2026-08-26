#!/usr/bin/env python3
"""Knife 62 bump script — docs/45 四轨公开提取刷新 (tasking 379).

落地:
  - docs/45-stage2-s210-lite-gate2-review-index-20260826.md (MODIFIED — 已入
    manifest; bump SKIP, SHA REFRESH 不增计数 per knife 44 先例):
    * 头部 +queue_rev 158 刷新行 (per 379)
    * §1 公开提取段: 三轨 → 四轨 (湖北 PROVINCIAL_BULLETIN 第四轨 21 行 /
      c5cf5abeb4fdf97a / fixture public_extract_hubei.json / 第四分节 /
      回执 377; live enabled=FALSE 暂缓; 首页文案指向; 四轨皆
      demo/candidate 非 O1/Gate PASS)
    * §6.2 +湖北第四轨行 (深圳第三轨行措辞保留; 双轨行预览措辞不动)
    * §7 pack invariant 链更新 684 → 690 (补 knife 61/62 链)
  - docs/53-stage2-public-ingest-ops-handbook-20260826.md (MODIFIED — 已入
    manifest; bump SKIP): §5 预览 +第 4 区块 (湖北 xlsx 轨 21 行 +
    enabled=FALSE 暂缓免责 + per 回执 377); 冒烟注记补 §12e 门
  - frontend/app/page.tsx (MODIFIED — 已入 manifest; bump SKIP): 首页链接
    文案「公开提取样本（NBS）」→「公开提取样本（四轨 demo）」
  - scripts/_knife62_manifest_bump.py (本文件)
  - reviews/.../380-stage0-cc-docs45-four-track-extracts-refresh-receipt-20260826.md

前置 knife 61 已将湖北 extract + fixture 落 pack (684 → 688); 本刀仅 +2
(bump + receipt); docs/45/53 + page.tsx 皆 SHA REFRESH / 文案修订 不增计数.

NEW_ARTIFACTS = +2 → 688 → 690

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
        "scripts/_knife62_manifest_bump.py",
        "spike_helper",
    ),
    (
        "reviews/stage0-gate0-rework-2026-08-23/"
        "380-stage0-cc-docs45-four-track-extracts-refresh-receipt-20260826.md",
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