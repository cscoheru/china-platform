#!/usr/bin/env python3
"""Knife 583 bump script — O3 实装首刀 (validate_ocr_input API + migration 014)
(tasking 583; 架构师治理模型第五刀, 经 00-EXEC-QUEUE.md 签发, 前置 582 审计 PASS;
581 修复刀恢复全量 0 failed + manifest 911 → 583 落地后 917).

落地 (合刀 A–D 同 commit、单槽单回执; 全量 pytest 0 failed 为核心证据):
  - scripts/intake_real_sha_if_present.py (MODIFIED, 在册 REFRESH):
    新增 is_control_flow_fixture(path) 公开 wrapper (包装既有私有 _is_fixture)
    + 新增 validate_ocr_input(path) 五态守门 (ALLOWED_PREFIXES + SEED_ARCHIVES +
    fixture 判定 + stdlib mimetypes.guess_type MIME 后缀匹配);
    scripts/auto_ingest_public_source.py 零触碰; SHA 闸 rc=8 语义零弱化
    (转测试预期非放行); 零新依赖 (不引入 python-magic/libmagic).
  - schema/migrations/014_source_document_doc_kind.sql (NEW, schema_migration_ddl):
    ADD COLUMN doc_kind TEXT NOT NULL DEFAULT 'NORMAL' + ADD CONSTRAINT
    source_document_doc_kind_check CHECK (doc_kind IN ('NORMAL','OCR_SCAN')) +
    CREATE INDEX idx_source_doc_doc_kind + COMMENT ON COLUMN;
    既有列 file_hash_sha256 / language / uploader_id / created_at / file_format
    复用不新增 (避免列冗余); 不动 001-013 + 01-core.sql + dbt + mart + 前端.
  - schema/migrations/014_source_document_doc_kind.log (NEW, schema_migration_log):
    旁车按 001-013.log 范式; 复核 013.log 独立文件 → 双 ADD (per §E 条件).
  - tests/test_validate_ocr_input_583.py (NEW, schema_negative_test):
    14 例四态覆盖 = ACCEPT 5 (PDF/JPEG/PNG/TIFF in upload prefix + PDF in
    seed_archives) / REJECT_OUTSIDE_ALLOWLIST 3 / REJECT_CONTROL_FLOW_FIXTURE 3 /
    REJECT_MIME 2 / boundary 1 (.pdf 后缀随机内容由 suffix 决定).
  - reviews/.../582-stage0-architect-s581-inherited-fix-audit-PASS-20260828.md
    (架构师资产, 只读随刀入库, ADD; per 581 先例 580 audit ADD in 581 bump).
  - reviews/.../583-stage0-cc-o3-impl-validate-api-doc-kind-receipt-20260828.md
    (本刀回执, ADD).
  - scripts/_knife583_manifest_bump.py (本文件, ADD).

COUNT CHECK (枚举即权威, 逐项实测 NOT-IN):
  tasking §E 头部标 +5 + 911→916; 实测 6 个路径均不在 manifest — 计数偏差.
  §E 条件: "schema_migration_log 旁车; 或并入 sql 单条 ADD 如 013.log 范式 —
  复核 013.log 独立文件则双 ADD". 013.log = 独立文件 (29 lines 独立 vs 013.sql
  114 lines) → 双 ADD = 014.sql + 014.log 各一条 = 6 NEW.
  §F 头部 "+5 911 → 916" 在条件解析后应为 "+6 911 → 917"; enumeration wins
  per tasking §F "枚举即权威" 原则 (condition resolves to double ADD → 917).
  本脚本 EXPECTED_COUNT = 917 (与 enumeration 一致); 偏差记入回执 (不阻塞).

NEW_ARTIFACTS = +6 → 911 → 917
REFRESH_ARTIFACTS = scripts/intake_real_sha_if_present.py + docs/45 + docs/49 +
  docs/50 + docs/53 + 00-EXEC-QUEUE.md + 583 回执 — 已在 manifest 的文件 SHA
  REFRESH 不增计数; 支持二次执行: 回执粘贴 bump 输出后再跑一次, 将回执自身
  SHA 刷至最终态 (两阶段 paste+refresh 模式 per 577/581 先例).

SKIP: docs/50 房规未入 manifest (574/577/579/581 先例一致); 任务书按先例
不计数.

Recomputes role_count from artifacts (source of truth, per knife 16 fix).
"""
from __future__ import annotations

import hashlib
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
MANIFEST = ROOT / "evidence_pack" / "manifest.json"

R = "reviews/stage0-gate0-rework-2026-08-23/"

NEW_ARTIFACTS = [
    ("scripts/_knife583_manifest_bump.py", "spike_helper"),
    (R + "583-stage0-cc-o3-impl-validate-api-doc-kind-receipt-20260828.md",
     "documentation"),
    (R + "582-stage0-architect-s581-inherited-fix-audit-PASS-20260828.md",
     "documentation"),
    ("schema/migrations/014_source_document_doc_kind.sql", "schema_migration_ddl"),
    ("schema/migrations/014_source_document_doc_kind.log", "schema_migration_log"),
    ("tests/test_validate_ocr_input_583.py", "schema_negative_test"),
]

# 已在 manifest 的文件: SHA REFRESH 不增计数 (tasking 583 §E SKIP/REFRESH).
# docs/50 按房规 SKIP (574/577/579/581 先例).
REFRESH_ARTIFACTS = [
    "scripts/intake_real_sha_if_present.py",
    "docs/45-stage2-s210-lite-gate2-review-index-20260826.md",
    "docs/49-stage2-o3-ocr-prod-path-plan-20260826.md",
    "docs/50-stage2-gate2-review-packet-draft-20260826.md",
    "docs/53-stage2-public-ingest-ops-handbook-20260826.md",
    R + "00-EXEC-QUEUE.md",
    R + "583-stage0-cc-o3-impl-validate-api-doc-kind-receipt-20260828.md",
]

EXPECTED_COUNT = 917  # 911 + 6 (per §E enumeration resolution; 013.log
                      # 独立文件 → 双 ADD → 014.sql + 014.log 各一条;
                      # tasking §F header "+5" 偏差记入回执)


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
    by_path = {a.get("path"): a for a in artifacts}

    added = 0
    for rel, role in NEW_ARTIFACTS:
        p = ROOT / rel
        if not p.exists():
            print(f"ERR: {rel} not on disk", file=sys.stderr)
            return 1
        if rel in by_path:
            print(f"SKIP: {rel}")
            continue
        size = p.stat().st_size
        digest = sha256(p)
        artifacts.append(
            {"path": rel, "size_bytes": size, "sha256": digest, "role": role}
        )
        by_path[rel] = artifacts[-1]
        added += 1
        print(f"ADD: {rel} ({size} bytes, sha={digest[:8]}, role={role})")

    for rel in REFRESH_ARTIFACTS:
        if rel not in by_path:
            print(f"NOT-IN-MANIFEST (房规 skip, no count change): {rel}")
            continue
        p = ROOT / rel
        if not p.exists():
            print(f"ERR: refresh target {rel} not on disk", file=sys.stderr)
            return 1
        entry = by_path[rel]
        old_digest = entry.get("sha256", "")
        new_digest = sha256(p)
        if new_digest == old_digest:
            print(f"REFRESH (unchanged): {rel} sha={new_digest[:8]}")
            continue
        entry["sha256"] = new_digest
        entry["size_bytes"] = p.stat().st_size
        print(
            f"REFRESH: {rel} sha={old_digest[:8]} → {new_digest[:8]} "
            f"({entry['size_bytes']} bytes; no count change)"
        )

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
    assert new_count == EXPECTED_COUNT, (
        f"INVARIANT BROKEN: artifact_count={new_count} != expected "
        f"{EXPECTED_COUNT} (911 + 6 per §E enumeration; §F header '+5' is "
        f"under-count, resolved by 013.log independence → double ADD)"
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
