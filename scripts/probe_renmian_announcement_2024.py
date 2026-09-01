"""M4.1 — 任免公告 可达性 probe (knife 638 Block A.2).

Per knife 638 §2 / docs/54 §M4.1 / docs/57 §6:
- Probe targets: 中央纪委国家监委 + 全国人大 + 国务院 (3 URLs only — limited
  scope per tasking §2.638-A.2)
- 3 URLs total
- Verdict: REACHABLE / PARTIAL / BLOCKED
- Year probed: 2024 (current)

OUTPUT (read-only — does NOT write cegr.observation):
* docs/reports/m4_1_renmian_probe_20260901.md
* evidence_pack/m4_1_renmian_probe_20260901.json

Honesty rules:
- REACHABLE: HTTP 200 + body contains 任免/任免名单 marker
- PARTIAL: HTTP 200 + body loaded but no marker found
- BLOCKED: TLS reset / 403 WAF / 404 / connection error
- DSN-free: only network + filesystem.

Usage:
  python3 scripts/probe_renmian_announcement_2024.py
  python3 scripts/probe_renmian_announcement_2024.py --sample-only  # exit after 1 probe
"""
from __future__ import annotations

import argparse
import json
from collections import defaultdict
from pathlib import Path

from _probe_http_helpers import (
    RENMIAN_MARKER_RE,
    classify_people_probe,
    fetch,
    now_utc_iso,
)

REPO_ROOT = Path(__file__).resolve().parent.parent
REPORT_MD = REPO_ROOT / "docs" / "reports" / "m4_1_renmian_probe_20260901.md"
EVIDENCE_JSON = REPO_ROOT / "evidence_pack" / "m4_1_renmian_probe_20260901.json"

# 3 targets (limited scope per tasking §2.638-A.2)
RENMIAN_TARGETS: list[tuple[str, str, str]] = [
    ("central-discipline", "中央纪委国家监委", "https://www.ccdi.gov.cn/"),
    ("npc", "全国人大", "http://www.npc.gov.cn/"),
    ("central", "国务院", "https://www.gov.cn/zwgk/zfgbg.htm"),
]


def probe_target(slug: str, entity_zh: str, url: str) -> dict:
    cell = {
        "slug": slug, "entity": entity_zh, "year": 2024,
        "source": "RENMIAN_ANNOUNCEMENT", "url": url,
        "verdict": "NOT_PROBED", "http_code": 0,
        "reason": "", "probed_at": "",
    }
    if not url:
        cell["reason"] = "no URL resolved"
        cell["verdict"] = "BLOCKED"
        return cell
    cell["probed_at"] = now_utc_iso()
    code, reason, body = fetch(url)
    cell["http_code"] = code
    cell["reason"] = reason
    cell["verdict"] = classify_people_probe(code, reason, body, RENMIAN_MARKER_RE)
    return cell


def run_probe(sample_only: bool = False) -> dict:
    cells = []
    targets = RENMIAN_TARGETS[:1] if sample_only else RENMIAN_TARGETS
    for slug, entity_zh, url in targets:
        cells.append(probe_target(slug, entity_zh, url))

    by_verdict = defaultdict(int)
    for c in cells:
        by_verdict[c["verdict"]] += 1
    by_entity = defaultdict(int)
    for c in cells:
        by_entity[c["entity"]] = c["verdict"]

    return {
        "generated_at": now_utc_iso(),
        "summary": {
            "total_cells": len(RENMIAN_TARGETS),
            "probed_cells": len(cells),
            "sample_only": sample_only,
            "by_verdict": dict(by_verdict),
            "by_entity": dict(by_entity),
        },
        "probed_count": len(cells),
        "cells": cells,
        "probe_methodology": (
            "REACHABLE: HTTP 200 + body contains 任免/任免名单 marker. "
            "PARTIAL: HTTP 200 + body loaded but no marker. "
            "BLOCKED: TLS reset / 403 WAF / 404 / connection error. "
            "Targets: 中央纪委国家监委 (ccdi.gov.cn) + 全国人大 (npc.gov.cn) + 国务院. "
            "Limited scope (3 URLs) per tasking §2.638-A.2 — 任免公告可扩展至省级人大."
        ),
    }


def write_outputs(results: dict) -> None:
    EVIDENCE_JSON.parent.mkdir(parents=True, exist_ok=True)
    REPORT_MD.parent.mkdir(parents=True, exist_ok=True)
    EVIDENCE_JSON.write_text(
        json.dumps(results, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )

    bv = results["summary"]["by_verdict"]
    top = ("REACHABLE" if bv.get("REACHABLE", 0) == len(results["cells"])
            else "BLOCKED" if bv.get("BLOCKED", 0) == len(results["cells"])
            else "MIXED")
    lines = [
        "# M4.1 任免公告 可达性 probe 报告（2026-09-01，knife 638）",
        "",
        "> **类型**: 638-A.2 probe (read-only;不写 cegr.observation)",
        "> **前置**: 637 DELIVERED (路径 C 接受);docs/57 §6 下一步",
        "> **范围**: 3 URL (中央纪委 + 全国人大 + 国务院)",
        "",
        "## 0. 顶层裁定",
        "",
        f"**{top}** — 适用 {len(RENMIAN_TARGETS)} cell, 实测 {results['summary']['probed_cells']} cell。",
        "",
        "总分布:",
        "",
        f"- REACHABLE: {bv.get('REACHABLE', 0)}",
        f"- PARTIAL: {bv.get('PARTIAL', 0)}",
        f"- BLOCKED: {bv.get('BLOCKED', 0)}",
        "",
        "## 1. 实体逐项",
        "",
        "| slug | verdict | http_code | 备注 |",
        "|---|---|---|---|",
    ]
    for c in results["cells"]:
        note = c["reason"] if c["reason"] != "ok" else "ok"
        lines.append(
            f"| {c['entity']} ({c['slug']}) | {c['verdict']} | "
            f"{c['http_code']} | {note} |"
        )
    lines += [
        "",
        "## 2. 方法学",
        "",
        "REACHABLE: HTTP 200 + body 含 `任免|任免名单|appoint|removal|departure` marker。",
        "PARTIAL: HTTP 200 + body 已加载但 marker 未命中。",
        "BLOCKED: TLS reset / 403 WAF / 404 / connection error。",
        "Limited scope (3 URL): 任免公告省级人大公告可扩展 (后续刀 640+)。",
        "",
        "## 3. 数据源合规",
        "",
        "✓ 全部政府源 (ccdi.gov.cn / npc.gov.cn / www.gov.cn)；✓ 无商业库；✓ 无用户裁定 URL。",
        "",
        "## 4. 红线遵守",
        "",
        "- ✓ 不写 cegr.observation",
        "- ✓ 不静默硬编码 GDP 值",
        "- ✓ 不爬网（仅探可达性，不抓内容入库）",
        "- ✓ 脚本幂等",
        "- ✓ 不宣称 Gate / O1 / M2 / M4 PASS",
        "",
    ]
    REPORT_MD.write_text("\n".join(lines), encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description="638-A.2 任免公告 probe")
    parser.add_argument("--sample-only", action="store_true",
                        help="Exit after first 1 probe (smoke test)")
    args = parser.parse_args()
    results = run_probe(sample_only=args.sample_only)
    write_outputs(results)
    print(f"638-A.2: probed {results['summary']['probed_cells']}/3 targets; "
          f"verdict counts = {results['summary']['by_verdict']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())