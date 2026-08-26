#!/usr/bin/env python3
"""Knife 51 bump script — local-sample structured intake (tasking 346).

落地:
  - source_registry/registry.csv (sz.gov.cn 行 auth_note/failure_handling/
    purpose_note 三列注 SSL 暂缓;knife 50 已注,knife 51 维持)
  - scripts/auto_ingest_public_source.py:
    + PUBLIC_EXTRACTS_ROOT 常量
    + REGISTRY_SAMPLE_INTAKE_STATUS 常量
    + LocalSampleMismatch 异常
    + intake_from_local_sample() 5 步管道
    + write_extract_json() 结构化输出
    + main() --from-local-sample / --allow-disabled-local-sample flags
    + main() exit codes 8/9 新增
    + CLI docstring 更新
  - tests/test_auto_ingest_public_source_s52.py:
    +10 local-sample case (flag_routes_in_main / emits-status /
    SHA-mismatch-hard-fails / disabled-refused-without-opt-in /
    Hubei-with-allow-disabled-succeeds / extracts-to-structured-json /
    WORM-archive-under-ym-domain / no-network-calls /
    exit-code-8-on-SHA-mismatch / main-returns-0-for-sz)
  - reviews/.../347-stage0-cc-local-sample-structured-extract-receipt-20260826.md
  - data/public_extracts/{sz.gov.cn,stats.gov.cn}/<CATEGORY>.json
  - data/public_archives/2026-08/{sz.gov.cn,stats.gov.cn}/sample.html
  - reviews/.../_knife51_{sz,nbs}_local_sample.log + _knife51_nbs_live_probe.log
    (3 副产物,不入 manifest)
  - reviews/.../20260826T102849Z-...tech-blocked-stats.gov.cn-...md
    (1 副产物,不入 manifest)

NEW_ARTIFACTS = +2 → 656 → 658

Recomputes role_count from artifacts (source of truth, per knife 16 fix).
The connector is a MODIFICATION (already in manifest from knife 46),
bump SKIPs it; registry.csv is also a MODIFICATION (already in manifest),
bump SKIPs it; pytest additions are inline edits (not separately counted).
"""
from __future__ import annotations

import hashlib
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
MANIFEST = ROOT / "evidence_pack" / "manifest.json"

NEW_ARTIFACTS = [
    (
        "scripts/_knife51_manifest_bump.py",
        "spike_helper",
    ),
    (
        "reviews/stage0-gate0-rework-2026-08-23/"
        "347-stage0-cc-local-sample-structured-extract-receipt-20260826.md",
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