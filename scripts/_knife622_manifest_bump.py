#!/usr/bin/env python3
"""Knife 622 bump script — O1 §5.2.x 江苏样本第九刀（地市样本第八刀；泰州市统计局）

Per 622 tasking §0.1 (G) + 621 receipt §9 候选清单 #2 verbatim + 622 audit §7 候选 #2 verbatim
"江苏样本第九刀（地市样本第八刀；剩余江苏地市 = 宿迁 / 泰州（已用 per 622，本刀首选采用 = 泰州市统计局首页）/ 其它）"
+ 620 audit §7 候选 #2 verbatim + 619 receipt §9 候选 #1 verbatim + 618 audit §7.2 优先级 2 verbatim
+ 2026-08-29 治理铁律「数据源唯一=政府/统计局/研究机构自取；用户零裁定；执行端不可提任何用户裁定事项」
+ 619 tasking §0.1 enumeration 收口 precedent + 621 tasking §0.1 enumeration 收口 precedent.

本刀候选采用 = tjj.taizhou.gov.cn 泰州市统计局首页（首选 per 622 §0.2 候选清单 #1
verbatim；HTTP 200 34,117 bytes；SHA-256 =
55863f6553cdd13f18a26d4fb3d3b5b52c581ba3db41290c172c24a2c6d47307）.

落地 (合刀 同 commit、单槽单回执; 622 receipt 入库 NEW documentation + bump 脚本 NEW
spike_helper + 622 audit PASS 入库随 622 commit (per docs 房规「审计文件不单独 commit 随下
一刀入库」) + 江苏样本地市第九刀 HTML):

  - scripts/_knife622_manifest_bump.py (NEW spike_helper; 本刀自身)
  - reviews/.../622-stage0-architect-s621-o1-§5.2.x-real-sha-locked-江苏样本-地市第八刀-tasking-20260830-audit-PASS-20260830.md
    (622 audit PASS 入库随 622 commit, NEW documentation per docs 房规)
  - reviews/.../622-stage0-cc-o1-§5.2.x-real-sha-locked-江苏样本-地市第九刀-tasking-20260830-receipt.md
    (本刀回执, NEW documentation)
  - data/seed_archives/jiangsu_taizhou_tjj_gov_cn_20260830.html
    (NEW spike_sample_or_truth; 34,117 bytes / sha
    55863f6553cdd13f18a26d4fb3d3b5b52c581ba3db41290c172c24a2c6d47307)

COUNT CHECK (枚举即权威, 逐项实测 NOT-IN-INVARIANT):
  621 落地后 manifest 992 (per 621 §F K=4 → manifest 988 → 992
  per EXPECTED_COUNT 992; 621 计入 _knife621_manifest_bump.py +
  620 audit + 621 receipt + 江苏样本地市第八刀 HTML);
  622 本刀 +4 NEW = 996 (992 + 4 per enumeration 收口: bump 脚本 +
  622 audit + 622 receipt + 江苏样本地市第九刀 HTML);
  source_registry/registry.csv +1 行 (既有 15 行 = 既有 11 行 + 617 + 619 + 621 + 622
  新 1 行; line count 15 → 16; 既有 11 行 SHA `c404980f1eb542dad24504ae0e957c169de60b7d78859159986412fc83541277`
  实测不变; file-based role_count 守门 — registry.csv entry REFRESH
  不增计数);
  621 receipt 仅 narrative 措辞包裹形式 (不动);
  620 receipt 仅 narrative 措辞包裹形式 (不动);
  619 receipt 仅 narrative 措辞包裹形式 (不动);
  docs/45 §6.2 O1 status append line 567+ 不增计数 per docs-only refresh 房规;
  docs/49/50/51/52/53 F 段 SKIP 政策成立 (grep 命中 0 行 per 622 — 治理级决策
  标注 / 既有 supersede 标注共存非 stale `--confirm-*` runtime flag) → 不增计数;
  622 audit 文件本身 NOT modified (架构师自签; 执行端零修改); 仅随 622
  commit 入库 (per docs 房规);
  source_registry/registry.csv 既有 11 行 SHA 不变 (per file-based role_count 守门
  + bytes 总数变化是预期 per ⚠ disclosure #1);
  江苏样本 SHA-locked HTML 入 NEW spike_sample_or_truth +1;
  622 tasking 文件本身 NOT-IN-MANIFEST per docs 房规;
  scripts/intake_real_sha_if_present.py / scripts/auto_ingest_public_source.py
  零触碰;
  13 既有受保护文件 + source_registry/registry.csv +1 行 (既有 11 行 SHA 不变)
  + 江苏样本地市第九刀 HTML spike_sample_or_truth + 622 audit PASS 入库随 622 commit
  + 622 receipt 自身 = 14 受保护 (synthetic.png + S0 PDF + _syn_pdf_585.py +
  extracts dir + registry.csv 既有 11 行 + gate_thresholds.json + 01-core.sql +
  requirements-dbt.txt + scripts/requirements-paddle.txt +
  scripts/intake_real_sha_if_present.py + scripts/auto_ingest_public_source.py +
  .venv-paddle/pyvenv.cfg + migration 001-013).

NEW_ARTIFACTS = +4 → 992 → 996
REFRESH_ARTIFACTS = source_registry/registry.csv
(三阶段 paste+refresh 模式 per 577/581/583/585/587/589/591/593/594/595/
596/597/599/601/603/605/606/607/608/609/610/611/612/613/614/616/617/618/619/621 先例;
source_registry_csv file-based 守门不增计数).

SKIP: docs/45 §6.2 O1 status append (docs-only refresh, 不增计数 per docs 房规) +
docs/49/50/51/52/53 status row append (F 段 SKIP per 622 §1.6 grep 命中 0 行
per 622; 治理级决策标注 / 既有 supersede 标注共存非 stale `--confirm-*` runtime
flag → SKIP) + scripts/intake_real_sha_if_present.py /
scripts/auto_ingest_public_source.py 零触碰 + 旧版 user-action 任务书 (按先例不入
manifest) + 622 tasking 本身 (按 docs 房规 NOT-IN-MANIFEST) /
source_registry/registry.csv 既有 11 行 (SHA 不变, 622 仅 +1 行 bytes 总数变化是
预期) / spikes/04-scanned-pdf/gate_thresholds.json (零触碰) /
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
    ("scripts/_knife622_manifest_bump.py", "spike_helper"),
    # per docs 房规 "审计文件不单独 commit 随下一刀入库"：622 audit PASS
    # (审计 OF 621 tasking = 江苏样本地市第八刀) 落地入 622 commit (knife 622 是 622 的
    # 下一刀). 实际文件名以 knife-level = 622 命名.
    (R + "622-stage0-architect-s621-o1-§5.2.x-real-sha-locked-江苏样本-地市第八刀-tasking-20260830-audit-PASS-20260830.md",
     "documentation"),
    (R + "622-stage0-cc-o1-§5.2.x-real-sha-locked-江苏样本-地市第九刀-tasking-20260830-receipt.md",
     "documentation"),
    ("data/seed_archives/jiangsu_taizhou_tjj_gov_cn_20260830.html",
     "spike_sample_or_truth"),
]

REFRESH_ARTIFACTS = [
    "source_registry/registry.csv",  # REFRESH sha + size_bytes (file-based role_count 守门不增计数; 622 +1 行 bytes 总数变化是预期 per ⚠ disclosure #1)
]

EXPECTED_COUNT = 996  # 992 + 4 per enumeration 收口: _knife622_manifest_bump.py + 622 audit PASS (随 622 commit 入库 per docs 房规) + 622 receipt + 江苏样本地市第九刀 HTML; source_registry/registry.csv REFRESH 不增计数 per file-based role_count 守门


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
        f"{EXPECTED_COUNT} (992 + 4 per enumeration 收口: "
        f"_knife622_manifest_bump.py + 622 audit + 622 receipt + "
        f"江苏样本地市第九刀 HTML; "
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
