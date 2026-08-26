#!/usr/bin/env python3
"""Knife 58 bump script — 深圳样本表抽取修复 (tasking 367).

落地:
  - scripts/auto_ingest_public_source.py (MODIFIED — 已入 manifest; bump SKIP)
    * 新增 extract_municipal_tables(): MUNICIPAL_BULLETIN 专用抽取器 —
      先走全表遍历 (每张 <table> 用 NBS header/row 逻辑, 空壳 JS 表贡献 0 行),
      无表行时回退散文抽取 (news_cont_d_wrap 容器内每个非空 <p> 一行
      {"section": <中文序号节标>, "paragraph": <text>}; 0 伪造)
    * 根因: 深圳公报正文纯散文 + 数据表全部以 PNG 嵌入, 页面唯一 <table>
      是 JS 填充的空搜索壳 → 原 first-table walker 0 行
    * extract_tables dispatcher: MUNICIPAL_BULLETIN → extract_municipal_tables;
      NATIONAL_BULLETIN 路由不变 (63 行契约不动, per 367 §红线)
  - tests/test_auto_ingest_public_source_s52.py (MODIFIED — 已入 manifest;
    bump SKIP) — Section 15 +5 case:
    test_municipal_extract_real_sample_prose_rows /
    test_municipal_extract_prefers_embedded_tables /
    test_nbs_extract_no_regression_63_rows /
    test_sz_delivered_extract_json_shape /
    test_municipal_dispatch_routes_prose_fallback
  - data/public_extracts/sz.gov.cn/MUNICIPAL_BULLETIN.json (NEW to pack;
    git 里是 0 行→71 行的 MODIFIED) — 重跑 --from-local-sample 的真实产物
  - scripts/_knife58_manifest_bump.py (本文件)
  - reviews/.../368-stage0-cc-shenzhen-extract-fix-receipt-20260826.md

不入 pack (per 先例): WORM archive data/public_archives/2026-08/sz.gov.cn/
sample.html (git 已跟踪, 幂等未变); lineage JSONL 20260826-local-sample-
sz-gov-cn-MUNICIPAL_BULLETIN.jsonl (git 跟踪, _knife47/48 先例不入 pack)。

NEW_ARTIFACTS = +3 → 676 → 679

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
        "data/public_extracts/sz.gov.cn/MUNICIPAL_BULLETIN.json",
        "data_contract_suite",
    ),
    (
        "scripts/_knife58_manifest_bump.py",
        "spike_helper",
    ),
    (
        "reviews/stage0-gate0-rework-2026-08-23/"
        "368-stage0-cc-shenzhen-extract-fix-receipt-20260826.md",
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
