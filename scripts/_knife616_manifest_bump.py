#!/usr/bin/env python3
"""Knife 616 bump script — O1 §5.2.x 614 修复闭环刀
(执行端一次性 git grep scope 扩展 + 613 audit 修复 + 00-EXEC-QUEUE.md +
614 receipt narrative 改写 + 单元测试守门重写 per 615 audit §7.1 优先级 1 verbatim)

(per 616 tasking §0.1 + 615 audit §7.1 优先级 1 verbatim "**615 tasking =
614 修复闭环刀**（per FAIL #1 + FAIL #3 处置）" + 615 audit §4 FAIL items
#1 (scope miss) + #2 (v3 fix log 失实) + #3 (单元测试 2/6 FAIL 结构性悖论)
+ 614 tasking §3 验收清单 verbatim + 614 receipt §9 + 2026-08-29 治理铁律
「数据源唯一=政府/统计局/研究机构自取；用户零裁定；执行端不可提任何用户裁定事项」).

落地 (合刀 同 commit、单槽单回执; 616 receipt 入库 NEW documentation +
bump 脚本 NEW spike_helper + 615 audit 入库随 616 commit (per docs 房规
"审计文件不单独 commit 随下一刀入库") + 616 receipt):

  - scripts/_knife616_manifest_bump.py (NEW spike_helper; 本刀自身)
  - reviews/.../615-stage0-architect-s614-§5.2.x-sha-citation-drift-治理-tasking-20260830-audit-FAIL-20260830.md
    (615 audit 入库随 616 commit, NEW documentation per docs 房规)
  - reviews/.../616-stage0-cc-§5.2.x-614-修复闭环-tasking-20260830-receipt.md
    (本刀回执, NEW documentation)

COUNT CHECK (枚举即权威, 逐项实测 NOT-IN-INVARIANT):
  614 落地后 manifest 977 (per 614 §G K=4 → manifest 973 → 977
  per EXPECTED_COUNT 977; 614 计入 _knife614_manifest_bump.py +
  613 audit + 614 receipt + tests/test_sha_citation_drift_guard.py);
  616 本刀 +3 NEW = 980 (977 + 3 per enumeration 收口: bump 脚本 +
  615 audit + 616 receipt);
  source_registry/registry.csv REFRESH (不增计数 per file-based
  role_count 守门; 616 仅 narrative `3639e729<…>` 过期 8-char prefix 改写 +
  test_2/test_6 in-place edit 不增计数 per 615 audit §7.1 (C') priority 1
  verbatim「保留 test_1 + test_3 + test_4 + test_5 四个 PASS 用例」);
  615 audit 文件本身 NOT modified (架构师自签; 执行端零修改); 仅随 616
  commit 入库 (per docs 房规);
  614 receipt 仅 narrative 措辞包裹形式改写, 不增计数 (per 616 §0.1 (B') (iii));
  613 audit 4 处 bare `3639e729…` → narrative 改写 + `…` → `<…>` 过期 8-char
  prefix label 形式, 不增计数 (per 616 §0.1 (B') (i));
  00-EXEC-QUEUE.md §CURRENT/§DELIVERED 7 处 narrative 措辞包裹形式改写,
  不增计数 (per 616 §0.1 (B') (ii));
  docs/45 §6.2 O1 status append line 561 不增计数 per docs-only refresh 房规;
  docs/49/50/51/52/53 F 段 SKIP 政策成立 (E 段 grep 命中为治理级决策标注
  非 stale `--confirm-*` runtime flag) → 不增计数;
  SHA 串号 narrative 改写 (B') 不增计数 — 仅叙事措辞包裹形式改写不改
  其他原文 per 616 §0.1 (B');
  615 audit 文件本身 (架构师自签; 执行端零修改; 仅随 616 commit 入库);
  616 tasking 文件本身 NOT-IN-MANIFEST per docs 房规;
  scripts/intake_real_sha_if_present.py / scripts/auto_ingest_public_source.py
  零触碰;
  13 既有受保护文件 + 615 audit 入库随 616 commit + 616 receipt 自身
  + test_sha_citation_drift_guard.py in-place edit (不变) = 14 受保护
  (synthetic.png + S0 PDF + _syn_pdf_585.py + extracts dir + registry.csv 既有 11 行
  + gate_thresholds.json + 01-core.sql + requirements-dbt.txt + scripts/requirements-paddle.txt
  + scripts/intake_real_sha_if_present.py + scripts/auto_ingest_public_source.py
  + .venv-paddle/pyvenv.cfg + migration 001-013 + tests/test_sha_citation_drift_guard.py).

NEW_ARTIFACTS = +3 → 977 → 980
REFRESH_ARTIFACTS = 00-EXEC-QUEUE.md + 616 receipt + source_registry/registry.csv
(四阶段 paste+refresh 模式 per 577/581/583/585/587/589/591/593/594/595/
596/597/599/601/603/605/606/607/608/609/610/611/612/613/614 先例; source_registry_csv file-based 守门不增计数).

SKIP: docs/45 §6.2 O1 status append (docs-only refresh, 不增计数 per docs 房规) +
docs/49/50/51/52/53 status row append (E 段 SKIP per 616 §1.5 grep 命中为治理级决策
标注非 stale `--confirm-*` runtime flag) + scripts/intake_real_sha_if_present.py /
scripts/auto_ingest_public_source.py 零触碰 + 旧版 user-action 任务书 (按先例不入 manifest) +
616 tasking 本身 (按 docs 房规 NOT-IN-MANIFEST) / SHA 串号 narrative 改写 (B')
(按 docs 房规 仅叙事措辞包裹形式改写 不增计数) / source_registry/registry.csv 既有 11 行
(SHA 不变, 616 narrative 改写不涉及 registry.csv 行变动) / spikes/04-scanned-pdf/gate_thresholds.json
(零触碰) / .venv-paddle (venv 不入 manifest per spike_helper 房规) /
scripts/requirements-paddle.txt (spike_helper 房规 NOT-IN-MANIFEST) /
spikes/04-scanned-pdf/{conftest.py,run_real_paddle_e2e.sh,test_real_paddle_e2e.py}
(spike_helper 房规 NOT-IN-MANIFEST) /
docs/45 / docs/46 / docs/44 (docs 房规 NOT-IN-MANIFEST) /
4 fixture 锁值 (synthetic.png + S0 PDF + _syn_pdf_585.py + extracts dir) 零触碰 /
migration 001-013 (零触碰) / 01-core.sql (零触碰) 保持现状.

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
    ("scripts/_knife616_manifest_bump.py", "spike_helper"),
    (R + "615-stage0-architect-s614-§5.2.x-sha-citation-drift-治理-tasking-20260830-audit-FAIL-20260830.md",
     "documentation"),
    (R + "616-stage0-cc-§5.2.x-614-修复闭环-tasking-20260830-receipt.md",
     "documentation"),
]

REFRESH_ARTIFACTS = [
    R + "00-EXEC-QUEUE.md",
    R + "616-stage0-cc-§5.2.x-614-修复闭环-tasking-20260830-receipt.md",
    "source_registry/registry.csv",  # REFRESH sha + size_bytes (file-based role_count 守门不增计数; 616 narrative 改写不涉及 registry.csv 行变动)
]

EXPECTED_COUNT = 980  # 977 + 3 per enumeration 收口: _knife616_manifest_bump.py + 615 audit + 616 receipt; source_registry/registry.csv REFRESH 不增计数 per file-based role_count 守门


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
            print(f"SKIP (already in manifest): {rel}")
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
        f"{EXPECTED_COUNT} (977 + 3 per enumeration 收口: "
        f"_knife616_manifest_bump.py + 615 audit + 616 receipt; "
        f"source_registry/registry.csv REFRESH 不增计数 per file-based "
        f"role_count 守门)"
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
