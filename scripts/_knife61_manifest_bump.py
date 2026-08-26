#!/usr/bin/env python3
"""Knife 61 bump script — 湖北 PROVINCIAL_BULLETIN 第四分节 (tasking 376).

落地:
  - frontend/lib/public_extract_hubei.json (NEW — data_contract_suite)
    * byte-verbatim 快照自 data/public_extracts/tjj.hubei.gov.cn/
      PROVINCIAL_BULLETIN.json (21 行 xlsx 提取, sha 9056001c 双侧一致)
    * 走 scripts/auto_ingest_public_source.py --from-local-sample
      --allow-disabled-local-sample (live enabled=FALSE 暂缓, 本地样本
      路径与 registry SHA 锚定) 取得 rc=0
  - frontend/app/public-extracts/page.tsx (MODIFIED — 已入 manifest;
    bump SKIP) — 第四区块: 湖北月报样本提取 PROVINCIAL_BULLETIN
    (REGISTRY_SAMPLE, xlsx) + DemoBadge + 8 字段 provenance + 21 行 xlsx
    月报统计表全量 + live FALSE 暂缓非 live 免责; NBS 双轨 + 深圳 sample
    三区块零改动
  - frontend/smoke-check.py (MODIFIED — 已入 manifest; bump SKIP)
    * §12e gate: HB fixture 在位 (21 行/registry SHA c5cf5abeb4fdf97a 锚)
      + 页面针 (fixture import / PROVINCIAL_BULLETIN / 月报统计表 /
      enabled=FALSE); 注释先剥再扫
  - tests/test_public_extract_frontend_fixture.py (MODIFIED — 已入
    manifest; bump SKIP) — +3 case:
    test_hb_fixture_mirrors_extract_and_shape /
    test_hb_track_isolated_from_nbs_and_sz /
    test_page_renders_hb_registry_sample_track
  - scripts/_knife61_manifest_bump.py (本文件)
  - reviews/.../377-stage0-cc-hubei-extract-frontend-section-receipt-20260826.md

NEW_ARTIFACTS = +4 → 684 → 688

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
        "data/public_extracts/tjj.hubei.gov.cn/PROVINCIAL_BULLETIN.json",
        "data_contract_suite",
    ),
    (
        "frontend/lib/public_extract_hubei.json",
        "data_contract_suite",
    ),
    (
        "scripts/_knife61_manifest_bump.py",
        "spike_helper",
    ),
    (
        "reviews/stage0-gate0-rework-2026-08-23/"
        "377-stage0-cc-hubei-extract-frontend-section-receipt-20260826.md",
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