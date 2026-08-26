#!/usr/bin/env python3
"""Knife 54 bump script — JS-shell heuristic tighten + NBS live (tasking 355).

落地:
  - scripts/auto_ingest_public_source.py (MODIFIED — 已入 manifest; bump SKIP)
    * is_js_only_shell 收紧 (per 355 §SCHEMA 1): 仅 len(blob) < threshold
      且 (<script 或 window.location/location.replace) 才判壳; 大页一律
      False —— 修 NBS 388KB 大页含 redirect 片段被 rc=7 的误判
    * 新增 is_empty_content_page (355 §SCHEMA 2): 大页无 <table> → 空内容
    * main() 0-deeplink 分支按空内容/JS 渲染二分 phenomenon 文本;
      JS-shell 分支文本注明 size 条件
  - tests/test_auto_ingest_public_source_s52.py (MODIFIED — 已入 manifest;
    bump SKIP) +5 case (355 §SCHEMA 3 ≥4):
    test_is_js_only_shell_false_for_large_page_with_redirect /
    test_is_js_only_shell_small_redirect_without_script_tag_blocked /
    test_is_js_only_shell_hubei_71b_still_blocked /
    test_is_empty_content_page_classification /
    test_main_reports_empty_content_not_js_shell (in-process main,
    monkeypatch download + REVIEWS_DIR → tmp)
  - NBS live 一次 (355 §SCHEMA 4): 过壳门 → deeplink
    202608/t20260821_1965093.html → 435,469B sha=0b85212f… → drift rc=4
    (WORM 归档 data/public_archives/2026-08/stats.gov.cn/zxfb + drift 报告
    进 git 不入 pack, 同 sample.html 先例; registry pin 未做, 留 Cursor 裁定)
  - scripts/_knife54_manifest_bump.py (本文件)
  - reviews/.../356-stage0-cc-js-shell-nbs-live-receipt-20260826.md

NEW_ARTIFACTS = +2 → 665 → 667

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
        "scripts/_knife54_manifest_bump.py",
        "spike_helper",
    ),
    (
        "reviews/stage0-gate0-rework-2026-08-23/"
        "356-stage0-cc-js-shell-nbs-live-receipt-20260826.md",
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
