#!/usr/bin/env python3
"""Knife 617 bump script — O1 §5.2.x 江苏样本第六刀（地市样本第五刀；盐城市统计局）

Per 617 tasking §0.1 (G) + 615 audit §7.1 优先级 2 verbatim
"江苏样本第六刀（地市样本第五刀；其它江苏地市政府/统计局公开源；接续 605 + 606 +
608 + 610 + 612 江苏样本链路 5/15 → 6/15）" + 616 receipt §9 候选 #2 verbatim
"徐州 / 盐城 / 扬州 / 镇江 / 泰州 / 宿迁地市统计局公开源" + 617 audit PASS + 2026-08-29
治理铁律「数据源唯一=政府/统计局/研究机构自取；用户零裁定；执行端不可提任何用户裁定
事项」+ 612 tasking §0.1 enumeration 收口 precedent + 616 tasking §0.1 enumeration
收口 precedent.

本刀候选采用 = tjj.yancheng.gov.cn 盐城市统计局首页（首选 tjj.xuzhou.gov.cn SSL
connection error exit 35 实测 fallback #1 → yancheng HTTP 200 23,721 bytes per
617 tasking §1.1 备选清单 #2 fallback #1）.

落地 (合刀 同 commit、单槽单回执; 617 receipt 入库 NEW documentation + bump 脚本 NEW
spike_helper + 617 audit 入库随 617 commit (per docs 房规「审计文件不单独 commit 随下
一刀入库」) + 江苏样本地市第六刀 HTML):

  - scripts/_knife617_manifest_bump.py (NEW spike_helper; 本刀自身)
  - reviews/.../617-stage0-architect-s616-o1-§5.2.x-real-sha-locked-江苏样本-地市第六刀-tasking-20260830-audit-PASS-20260830.md
    (617 audit 入库随 617 commit, NEW documentation per docs 房规)
  - reviews/.../617-stage0-cc-o1-§5.2.x-real-sha-locked-江苏样本-地市第六刀-tasking-20260830-receipt.md
    (本刀回执, NEW documentation)
  - data/seed_archives/jiangsu_yancheng_tjj_gov_cn_20260830.html
    (NEW spike_sample_or_truth; 23,721 bytes / sha
    f8a2d8ebbb6ce04fbe62cd54434dcde26f890102bf5f2c0eb6158632308b6c50)

COUNT CHECK (枚举即权威, 逐项实测 NOT-IN-INVARIANT):
  616 落地后 manifest 980 (per 616 §F K=3 → manifest 977 → 980
  per EXPECTED_COUNT 980; 616 计入 _knife616_manifest_bump.py +
  615 audit + 616 receipt);
  617 本刀 +4 NEW = 984 (980 + 4 per enumeration 收口: bump 脚本 +
  617 audit + 617 receipt + 江苏样本地市第六刀 HTML);
  source_registry/registry.csv +1 行 (既有 12 行 = 既有 11 行 + 617
  新 1 行; line count 12 → 13; 既有 11 行 SHA `c404980f1eb542dad24504ae0e957c169de60b7d78859159986412fc83541277`
  实测不变; file-based role_count 守门 — registry.csv entry REFRESH
  不增计数);
  616 receipt 仅 narrative 措辞包裹形式 (不动);
  docs/45 §6.2 O1 status append line 562+ 不增计数 per docs-only refresh 房规;
  docs/49/50/51/52/53 F 段 SKIP 政策成立 (grep 命中 0 行 per 617 — 治理级决策
  标注 / 既有 supersede 标注共存非 stale `--confirm-*` runtime flag) → 不增计数;
  617 audit 文件本身 NOT modified (架构师自签; 执行端零修改); 仅随 617
  commit 入库 (per docs 房规);
  source_registry/registry.csv 既有 11 行 SHA 不变 (per file-based role_count 守门
  + bytes 总数变化是预期 per ⚠ disclosure #1);
  江苏样本 SHA-locked HTML 入 NEW spike_sample_or_truth +1;
  617 tasking 文件本身 NOT-IN-MANIFEST per docs 房规;
  scripts/intake_real_sha_if_present.py / scripts/auto_ingest_public_source.py
  零触碰;
  13 既有受保护文件 + source_registry/registry.csv +1 行 (既有 11 行 SHA 不变)
  + 江苏样本地市第六刀 HTML spike_sample_or_truth + 617 audit 入库随 617 commit
  + 617 receipt 自身 = 13 受保护 (synthetic.png + S0 PDF + _syn_pdf_585.py +
  extracts dir + registry.csv 既有 11 行 + gate_thresholds.json + 01-core.sql +
  requirements-dbt.txt + scripts/requirements-paddle.txt +
  scripts/intake_real_sha_if_present.py + scripts/auto_ingest_public_source.py +
  .venv-paddle/pyvenv.cfg + migration 001-013).

NEW_ARTIFACTS = +4 → 980 → 984
REFRESH_ARTIFACTS = source_registry/registry.csv
(三阶段 paste+refresh 模式 per 577/581/583/585/587/589/591/593/594/595/
596/597/599/601/603/605/606/607/608/609/610/611/612/613/614/616 先例;
source_registry_csv file-based 守门不增计数).

SKIP: docs/45 §6.2 O1 status append (docs-only refresh, 不增计数 per docs 房规) +
docs/49/50/51/52/53 status row append (F 段 SKIP per 617 §1.6 grep 命中 0 行
per 617; 治理级决策标注 / 既有 supersede 标注共存非 stale `--confirm-*` runtime
flag → SKIP) + scripts/intake_real_sha_if_present.py /
scripts/auto_ingest_public_source.py 零触碰 + 旧版 user-action 任务书 (按先例不入
manifest) + 617 tasking 本身 (按 docs 房规 NOT-IN-MANIFEST) /
source_registry/registry.csv 既有 11 行 (SHA 不变, 617 仅 +1 行 bytes 总数变化是
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
    ("scripts/_knife617_manifest_bump.py", "spike_helper"),
    # per docs 房规 "审计文件不单独 commit 随下一刀入库"：616 audit PASS
    # (审计 OF 616 tasking = 614 修复闭环) 落地入 617 commit (knife 617 是 616 的
    # 下一刀). 实际文件名以 knife-level = 617 命名.
    (R + "617-stage0-architect-s616-§5.2.x-614-修复闭环-tasking-20260830-audit-PASS-20260830.md",
     "documentation"),
    (R + "617-stage0-cc-o1-§5.2.x-real-sha-locked-江苏样本-地市第六刀-tasking-20260830-receipt.md",
     "documentation"),
    ("data/seed_archives/jiangsu_yancheng_tjj_gov_cn_20260830.html",
     "spike_sample_or_truth"),
]

REFRESH_ARTIFACTS = [
    "source_registry/registry.csv",  # REFRESH sha + size_bytes (file-based role_count 守门不增计数; 617 +1 行 bytes 总数变化是预期 per ⚠ disclosure #1)
]

EXPECTED_COUNT = 984  # 980 + 4 per enumeration 收口: _knife617_manifest_bump.py + 616 audit PASS (随 617 commit 入库 per docs 房规) + 617 receipt + 江苏样本地市第六刀 HTML; source_registry/registry.csv REFRESH 不增计数 per file-based role_count 守门


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
        f"{EXPECTED_COUNT} (980 + 4 per enumeration 收口: "
        f"_knife617_manifest_bump.py + 617 audit + 617 receipt + "
        f"江苏样本地市第六刀 HTML; "
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