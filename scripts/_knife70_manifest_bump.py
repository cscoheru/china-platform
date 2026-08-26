#!/usr/bin/env python3
"""Knife 70 bump script — /public-extracts 四轨 CSV 静态下载 (tasking 403).

落地:
  - scripts/gen_public_extracts_csv.py (NEW — spike_helper): 确定性生成器,
    render_csv_bytes 纯函数 (UTF-8 无 BOM / \\n / QUOTE_MINIMAL; 列序=首行
    键序不重命名; row.get(key,"") 同页面语义).
  - frontend/public/public-extracts/{nbs,nbs-live-candidate,sz,hubei}.csv
    (NEW ×4 — data_contract_suite): 生成产物已 commit (63/60/71/21 数据行;
    重跑字节一致).
  - frontend/app/public-extracts/page.tsx (MODIFIED — 已入 manifest; bump
    SKIP, SHA REFRESH 不增计数 per knife 44 先例): 列头「下载 JSON / CSV」
    (含原 §12g needle 子串) + 4 同格 CSV 第二链 + 页脚非权威库注 + 头部
    注释 403 段.
  - frontend/smoke-check.py (MODIFIED — 已入 manifest; bump SKIP): §12i 门
    (4 CSV 在位非空 + 列头 + 4 href + 4 download attr + 非权威库守门 +
    JSON 4 链不回归, 15 针).
  - tests/test_public_extracts_csv_download.py (NEW — schema_negative_test):
    13 cases (表头一致 ×4 + 行数/字段数 ×4 + 确定性重渲 ×4 + 页面链/守门).
  - scripts/_knife70_manifest_bump.py (本文件)
  - reviews/.../404-stage0-cc-public-extracts-csv-download-receipt-20260826.md

前置 knife 69 已落 bump+receipt 入 pack (708 → 710); 本刀 +8 = 4 CSV +
生成器 + 测试 + bump + receipt → 710 → 718; page.tsx / smoke-check.py 皆
SHA REFRESH 不增计数.

NEW_ARTIFACTS = +8 → 710 → 718

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
        "frontend/public/public-extracts/nbs.csv",
        "data_contract_suite",
    ),
    (
        "frontend/public/public-extracts/nbs-live-candidate.csv",
        "data_contract_suite",
    ),
    (
        "frontend/public/public-extracts/sz.csv",
        "data_contract_suite",
    ),
    (
        "frontend/public/public-extracts/hubei.csv",
        "data_contract_suite",
    ),
    (
        "scripts/gen_public_extracts_csv.py",
        "spike_helper",
    ),
    (
        "tests/test_public_extracts_csv_download.py",
        "schema_negative_test",
    ),
    (
        "scripts/_knife70_manifest_bump.py",
        "spike_helper",
    ),
    (
        "reviews/stage0-gate0-rework-2026-08-23/"
        "404-stage0-cc-public-extracts-csv-download-receipt-20260826.md",
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
