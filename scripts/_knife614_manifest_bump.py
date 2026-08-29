#!/usr/bin/env python3
"""Knife 614 bump script — O1 §5.2.x SHA 串号 drift 治理刀
(执行端一次性 git grep + 全文校对修复 + 单元测试守门 per 613 audit §7 候选 #1)

(per 614 tasking §0.1 + 613 audit §7 候选 #1 verbatim "§CURRENT/历史 receipt
SHA 串号问题治理刀；候选根因：60X receipt 误把 `head -10`/`head -12` 等不同
SHA 串号传递；§CURRENT/612 tasking line 110/120/266 + 611 audit + 610 receipt
文本 SHA `3639e729…` 与 HEAD 实测 `c404980f1eb542dad24504ae0e957c169de60b7d78859159986412fc83541277`
不符；以实测为准；建议 614 audit 一次性 git grep + 全文校对修复 + 增单元测试守门"
+ 612 receipt §9 候选 #4 + 612 tasking §4 关联文件清单 + 2026-08-29 治理铁律
「数据源唯一=政府/统计局/研究机构自取；用户零裁定；执行端不可提任何用户裁定事项」).

落地 (合刀 同 commit、单槽单回执; 614 receipt 入库 NEW documentation +
bump 脚本 NEW spike_helper + 613 audit 入库随 614 commit (per docs 房规
"审计文件不单独 commit 随下一刀入库") + 614 receipt + tests/test_sha_citation_drift_guard.py):

  - scripts/_knife614_manifest_bump.py (NEW spike_helper; 本刀自身)
  - reviews/.../613-stage0-architect-s612-o1-§5.2.x-real-sha-locked-江苏样本-地市第四刀-tasking-20260829-audit-PASS-20260829.md
    (613 audit 入库随 614 commit, NEW documentation per docs 房规)
  - reviews/.../614-stage0-cc-§5.2.x-sha-citation-drift-治理-tasking-20260829-receipt.md
    (本刀回执, NEW documentation)
  - tests/test_sha_citation_drift_guard.py (NEW documentation; 6 unit tests guard)

COUNT CHECK (枚举即权威, 逐项实测 NOT-IN-INVARIANT):
  612 落地后 manifest 973 (per 612 §G K=4 → manifest 969 → 973
  per EXPECTED_COUNT 973; 612 计入 source_registry_csv REFRESH 不增
  计数 per file-based role_count 守门 + spike_sample_or_truth role +1);
  614 本刀 +4 NEW = 977 (973 + 4 per enumeration 收口: bump 脚本 +
  613 audit + 614 receipt + tests/test_sha_citation_drift_guard.py);
  source_registry/registry.csv REFRESH (不增计数 per file-based
  role_count 守门; bytes 总数零变化 是预期 — 614 零行变动
  per 614 §0.2 "source_registry/registry.csv 既有 11 行未改；614 零行变动");
  614 tasking 文件本身 NOT-IN-MANIFEST per docs 房规;
  docs/45 §6.2 O1 status append 不增计数 per docs-only refresh 房规;
  docs/49/50/51/52/53 status row append (E 段 SKIP per 614 §1.5 grep 命中为
  治理级决策标注非 stale `--confirm-*` runtime flag);
  SHA 串号 校对修复 (B)(B+) 不增计数 — 仅 SHA 字面替换不改其他原文
  per 614 §0.2 "SHA 字面校对修复视为'实测对齐'非'内容改动'";
  scripts/intake_real_sha_if_present.py / scripts/auto_ingest_public_source.py
  零触碰;
  13 既有受保护文件 + 614 新增 test_sha_citation_drift_guard.py 守门 = 14 受保护
  (synthetic.png + S0 PDF + _syn_pdf_585.py + extracts dir + registry.csv 既有 11 行
  + gate_thresholds.json + 01-core.sql + requirements-dbt.txt + scripts/requirements-paddle.txt
  + scripts/intake_real_sha_if_present.py + scripts/auto_ingest_public_source.py
  + .venv-paddle/pyvenv.cfg + migration 001-013 + tests/test_sha_citation_drift_guard.py).

NEW_ARTIFACTS = +4 → 973 → 977
REFRESH_ARTIFACTS = 00-EXEC-QUEUE.md + 614 receipt + source_registry/registry.csv
(四阶段 paste+refresh 模式 per 577/581/583/585/587/589/591/593/594/595/
596/597/599/601/603/605/606/607/608/609/610/611/612/613 先例; source_registry_csv file-based 守门不增计数).

SKIP: docs/45 §6.2 O1 status append (docs-only refresh, 不增计数 per docs 房规) +
docs/49/50/51/52/53 status row append (E 段 SKIP per 614 §1.5 grep 命中为治理级决策
标注非 stale `--confirm-*` runtime flag) + scripts/intake_real_sha_if_present.py /
scripts/auto_ingest_public_source.py 零触碰 + 旧版 user-action 任务书 (按先例不入 manifest) +
614 tasking 本身 (按 docs 房规 NOT-IN-MANIFEST) / SHA 串号 drift 校对修复 (B)(B+) (按
docs 房规 仅 SHA 字面替换 不增计数) / source_registry/registry.csv 既有 11 行 (SHA 不变,
零行变动 per 614 §0.2) / spikes/04-scanned-pdf/gate_thresholds.json (零触碰) /
.venv-paddle (venv 不入 manifest per spike_helper 房规) /
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
    ("scripts/_knife614_manifest_bump.py", "spike_helper"),
    (R + "613-stage0-architect-s612-o1-§5.2.x-real-sha-locked-江苏样本-地市第四刀-tasking-20260829-audit-PASS-20260829.md",
     "documentation"),
    (R + "614-stage0-cc-§5.2.x-sha-citation-drift-治理-tasking-20260829-receipt.md",
     "documentation"),
    ("tests/test_sha_citation_drift_guard.py", "documentation"),
]

REFRESH_ARTIFACTS = [
    R + "00-EXEC-QUEUE.md",
    R + "614-stage0-cc-§5.2.x-sha-citation-drift-治理-tasking-20260829-receipt.md",
    "source_registry/registry.csv",  # REFRESH sha + size_bytes (file-based role_count 守门不增计数; 614 零行变动)
]

EXPECTED_COUNT = 977  # 973 + 4 per enumeration 收口: _knife614_manifest_bump.py + 613 audit + 614 receipt + tests/test_sha_citation_drift_guard.py; source_registry/registry.csv REFRESH 不增计数 per file-based role_count 守门


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
        f"{EXPECTED_COUNT} (973 + 4 per enumeration 收口: "
        f"_knife614_manifest_bump.py + 613 audit + 614 receipt + "
        f"tests/test_sha_citation_drift_guard.py; source_registry/registry.csv "
        f"REFRESH 不增计数 per file-based role_count 守门)"
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