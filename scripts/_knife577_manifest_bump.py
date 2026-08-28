#!/usr/bin/env python3
"""Knife 577 bump script — 合刀: O1 CLOSED (as-scoped) 裁定登记 + S2.1-full
dbt 层 (tasking 577; 架构师治理模型 + 00-EXEC-QUEUE.md 新调度第二刀).

落地 (合刀 A–H 同 commit、单槽单回执; 需本地 DB):
  - docs/53-stage2-public-ingest-ops-handbook-20260826.md (MODIFIED):
    §5 新增第 40 项 O1 CLOSED (as-scoped) 裁定登记 (用户裁定 2026-08-28;
    收口域 = NATIONAL_BULLETIN → nanjing CONDITION 真 SHA 端到端
    538→560→572→573 审计 PASS; 59 行 = 已登记缺口, 逐城真实源入仓保持
    OPEN (号位 576); 「O1 仍 OPEN」历史行不删).
  - docs/50-stage2-gate2-review-packet-draft-20260826.md (MODIFIED):
    §4.4 里程碑表 +1 第 40 项裁定行 + intro ⚠ 收据链尾续接 → 577.
    [房规] docs/50 本体未入 manifest (镜像 docs/52 先例) — 显式 SKIP.
  - docs/45-stage2-s210-lite-gate2-review-index-20260826.md (MODIFIED):
    文首架构师治理模型第二刀 + 新调度模型刷新行 + §1 一段 + §6.2 行尾注
    append (per 577) + §7 链头 889 → 904 (knife 574 demote).
  - data/seeds/person_tenure_demo.json (NEW): S2.1-full demo seed
    (30/30/20/60/60/60, 全 demo).
  - scripts/seed_person_tenure_demo.py (NEW): load/status/unload loader.
  - dbt/models/staging/stg_{person,person_name_alias,position,tenure,
    appointment_event,person_source_evidence}.sql (NEW ×6, view).
  - dbt/models/marts/mart_person_tenure.sql (NEW, view, is_demo 末列).
  - tests/test_person_tenure_s21_full.py (NEW, 6 例 DB-backed).
  - scripts/_knife577_manifest_bump.py (本文件).
  - reviews/.../575-stage0-architect-s574-docs-closeout-audit-PASS-*.md
    (架构师资产, 只读随刀入库).
  - reviews/.../00-EXEC-QUEUE.md (治理调度队列, 随 577 交付入库).
  - scripts/exec_wake.sh (执行端唤醒脚本, 随刀入库).
  - reviews/.../577-stage0-cc-o1-close-person-tenure-full-receipt-*.md.

COUNT DISCREPANCY (disclosed): tasking 577 §F 标注 "NEW +14 → 889 → 903"
但实列 15 项 (seed JSON + loader + 6 stg + mart + pytest + bump + 回执 +
575 审计 + 00-EXEC-QUEUE + exec_wake.sh), 且全部不预先存在于 manifest.
Tasking §A 明文授权 "§7 链头 903 == 903 == 903 (按 bump 实际值)" —
本脚本按实际值 889 + 15 = 904 收口并在断言中强制.

前置 knife 574 已落 pack (886 → 889); 本刀 +15 = 904.

NEW_ARTIFACTS = +15 → 889 → 904
REFRESH_ARTIFACTS = docs/45 + docs/53 + docs/50 (skip) + 577 回执
  — 已在 manifest 的文件 SHA REFRESH 不增计数; 支持二次执行: 回执粘贴
    bump 输出后再跑一次, 将回执自身 SHA 刷至最终态.

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
    ("data/seeds/person_tenure_demo.json", "data_contract_suite"),
    ("scripts/seed_person_tenure_demo.py", "spike_helper"),
    ("dbt/models/staging/stg_person.sql", "spike_helper"),
    ("dbt/models/staging/stg_person_name_alias.sql", "spike_helper"),
    ("dbt/models/staging/stg_position.sql", "spike_helper"),
    ("dbt/models/staging/stg_tenure.sql", "spike_helper"),
    ("dbt/models/staging/stg_appointment_event.sql", "spike_helper"),
    ("dbt/models/staging/stg_person_source_evidence.sql", "spike_helper"),
    ("dbt/models/marts/mart_person_tenure.sql", "spike_helper"),
    ("tests/test_person_tenure_s21_full.py", "schema_negative_test"),
    ("scripts/_knife577_manifest_bump.py", "spike_helper"),
    (R + "577-stage0-cc-o1-close-person-tenure-full-receipt-20260828.md",
     "documentation"),
    (R + "575-stage0-architect-s574-docs-closeout-audit-PASS-20260828.md",
     "documentation"),
    (R + "00-EXEC-QUEUE.md", "documentation"),
    ("scripts/exec_wake.sh", "spike_helper"),
]

# 已在 manifest 的文件: SHA REFRESH 不增计数 (tasking 577 §F).
REFRESH_ARTIFACTS = [
    "docs/45-stage2-s210-lite-gate2-review-index-20260826.md",
    "docs/50-stage2-gate2-review-packet-draft-20260826.md",
    "docs/53-stage2-public-ingest-ops-handbook-20260826.md",
    R + "577-stage0-cc-o1-close-person-tenure-full-receipt-20260828.md",
]

EXPECTED_COUNT = 904  # 889 + 15 (per bump 实际值; tasking §A 授权)


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
        print(f"ADD: {rel} ({size} bytes, sha={digest[:8]})")

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
        f"{EXPECTED_COUNT} (889 + 15; tasking §F 标注 +14→903 与实列 15 项"
        f"不符, per §A「按 bump 实际值」)"
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
