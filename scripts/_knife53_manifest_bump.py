#!/usr/bin/env python3
"""Knife 53 bump script — protect public_extracts from pytest (tasking 352).

落地:
  - scripts/auto_ingest_public_source.py (MODIFIED — 已入 manifest; bump SKIP)
    * get_archive_root()/get_extracts_root() CALL-time resolvers:
      env CEGR_ARCHIVE_ROOT / CEGR_EXTRACT_ROOT > module default
      (fixes both clobber vectors: default-arg import binding +
      subprocess env inheritance)
    * archive()/write_extract_json()/write_sha_drift_report() route
      through resolvers
    * main() 新增 --archive-root=DIR / --extract-root=DIR (funnel into
      the same env vars BEFORE any write path)
  - tests/test_auto_ingest_public_source_s52.py (MODIFIED — 已入 manifest;
    bump SKIP)
    * tmp_archive_root fixture → autouse + setenv(CEGR_ARCHIVE_ROOT/
      CEGR_EXTRACT_ROOT) — 所有 pytest 含 subprocess 一律写入 tmp
    * test_sz_worm_archive_path_format 改用 setenv (env 优先于 attr)
    * +3 case: test_regression_real_extracts_not_clobbered_by_pytest /
      test_root_override_env_directs_in_process_intake /
      test_root_override_cli_flags_equal_env (79 passed; 运行后
      git status data/ 干净)
  - data/ 测试污染清理 (untracked, 已验证为 fake 内容后删除; 被误删的
    tracked sample.html 已 checkout 恢复; 不入 manifest)
  - scripts/_knife53_manifest_bump.py (本文件)
  - reviews/.../353-stage0-cc-protect-public-extracts-pytest-receipt-20260826.md

NEW_ARTIFACTS = +2 → 663 → 665

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
        "scripts/_knife53_manifest_bump.py",
        "spike_helper",
    ),
    (
        "reviews/stage0-gate0-rework-2026-08-23/"
        "353-stage0-cc-protect-public-extracts-pytest-receipt-20260826.md",
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
