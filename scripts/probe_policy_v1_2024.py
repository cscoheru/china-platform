"""M4.3 — 政策源 可达性 二次探活 (knife 640 Block A.1).

Per knife 640 §2.640-A.1 / docs/59 §5 + 639 receipt:
- 639 6 REACHABLE 任免源 ≠ 政策源;640 独立 probe 政策承载路径
- 6 REACHABLE 试点省 (继承 639) + ccdi + 国务院 政策栏目
- 13 URLs total

OUTPUT (read-only — does NOT write cegr.observation):
* docs/reports/m4_3_policy_v1_probe_20260901.md
* evidence_pack/m4_3_policy_v1_probe_20260901.json

Honesty rules:
- REACHABLE: HTTP 200 + body contains 政策文件/政府公报/规划计划 marker
- PARTIAL: HTTP 200 + body loaded but no marker found
- BLOCKED: TLS reset / 403 WAF / 404 / connection error
- DSN-free: only network + filesystem.

Usage:
  python3 scripts/probe_policy_v1_2024.py
  python3 scripts/probe_policy_v1_2024.py --sample-only  # exit after first 3 probes
"""
from __future__ import annotations

import argparse
import json
from collections import defaultdict
from pathlib import Path

from _probe_http_helpers import (
    POLICY_MARKER_RE,
    classify_people_probe,
    fetch,
    now_utc_iso,
)

REPO_ROOT = Path(__file__).resolve().parent.parent
REPORT_MD = REPO_ROOT / "docs" / "reports" / "m4_3_policy_v1_probe_20260901.md"
EVIDENCE_JSON = REPO_ROOT / "evidence_pack" / "m4_3_policy_v1_probe_20260901.json"

# 639 BLOCKED 9 (任免) + 640 复用 6 REACHABLE 试点省 (任免) → 政策承载路径探活
# 政策路径候选: /zwgk/zfwj/ (政府文件), /zwgk/zfgb/ (政府公报), /zwgk/ghjh/ (规划计划)
# 中央候选: ccdi /ldwd/ (领导/制度), 国务院 /zhengce/zhengceku/ (政策库), /zhengce/qt/ (其他)
POLICY_V1_TARGETS: list[tuple[str, str, str]] = [
    # 6 REACHABLE 试点省政策承载路径 (继承 639 任免 REACHABLE 6)
    ("heilongjiang-policy-zfwj", "黑龙江政策文件", "https://www.hlj.gov.cn/zwgk/zfwj/"),
    ("heilongjiang-policy-zfgb", "黑龙江政府公报", "https://www.hlj.gov.cn/zwgk/zfgb/"),
    ("fujian-policy-zfwj", "福建政策文件", "https://www.fujian.gov.cn/zwgk/zfwj/"),
    ("fujian-policy-zfgb", "福建政府公报", "https://www.fujian.gov.cn/zwgk/zfgb/"),
    ("henan-policy-zfwj", "河南政策文件", "https://www.henan.gov.cn/zwgk/zfwj/"),
    ("henan-policy-ghjh", "河南规划计划", "https://www.henan.gov.cn/zwgk/ghjh/"),
    ("guangdong-policy-zfwj", "广东政策文件", "https://www.gd.gov.cn/zwgk/zfwj/"),
    ("guangdong-policy-zfgb", "广东政府公报", "https://www.gd.gov.cn/zwgk/zfgb/"),
    ("guizhou-policy-zfwj", "贵州政策文件", "https://www.guizhou.gov.cn/zwgk/zfwj/"),
    ("yunnan-policy-zfwj", "云南政策文件", "https://www.yn.gov.cn/zwgk/zfwj/"),

    # ccdi 政策栏目 (639 PARTIAL 启示: 中央栏目名易错)
    ("central-discipline-ldwd", "中央纪委领导/制度", "https://www.ccdi.gov.cn/ldwd/"),

    # 国务院政策栏目 (639 PARTIAL zhengce;640 加试 政策库子栏目)
    ("central-zhengceku", "国务院政策库", "https://www.gov.cn/zhengce/zhengceku/"),
]


def probe_target(slug: str, entity_zh: str, url: str) -> dict:
    cell = {
        "slug": slug, "entity": entity_zh, "year": 2024,
        "source": "POLICY_V1", "url": url,
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
    cell["verdict"] = classify_people_probe(code, reason, body, POLICY_MARKER_RE)
    return cell


def run_probe(sample_only: bool = False) -> dict:
    cells = []
    targets = POLICY_V1_TARGETS[:3] if sample_only else POLICY_V1_TARGETS
    for slug, entity_zh, url in targets:
        cells.append(probe_target(slug, entity_zh, url))

    by_verdict = defaultdict(int)
    for c in cells:
        by_verdict[c["verdict"]] += 1
    by_entity = defaultdict(int)
    for c in cells:
        by_entity[c["entity"]] = c["verdict"]
    by_class_verdict = defaultdict(lambda: defaultdict(int))
    for c in cells:
        cls = ("central" if "central" in c["slug"] else "provincial")
        by_class_verdict[cls][c["verdict"]] += 1

    return {
        "generated_at": now_utc_iso(),
        "summary": {
            "total_cells": len(POLICY_V1_TARGETS),
            "probed_cells": len(cells),
            "sample_only": sample_only,
            "by_verdict": dict(by_verdict),
            "by_class_verdict": {k: dict(v) for k, v in by_class_verdict.items()},
            "by_entity": dict(by_entity),
        },
        "probed_count": len(cells),
        "cells": cells,
        "probe_methodology": (
            "REACHABLE: HTTP 200 + body contains 政策文件/政府公报/规划计划/政策库 marker. "
            "PARTIAL: HTTP 200 + body loaded but no marker. "
            "BLOCKED: TLS reset / 403 WAF / 404 / connection error. "
            "Targets: 10 试点省政策承载路径 (继承 639 6 REACHABLE 试点省) "
            "+ ccdi /ldwd/ + 国务院 /zhengce/zhengceku/ (政策库). "
            "二次探活理由: 639 6 REACHABLE 任免源 (/zwgk/) ≠ 政策源, "
            "640 探政策承载路径 /zwgk/zfwj/ + /zwgk/zfgb/ + /zwgk/ghjh/. "
            "沿用 638/639 WAF 假设修正: 子域/路径选择性阻断."
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
    bcv = results["summary"]["by_class_verdict"]
    top = ("REACHABLE" if bv.get("REACHABLE", 0) == len(results["cells"])
            else "BLOCKED" if bv.get("BLOCKED", 0) == len(results["cells"])
            else "MIXED")
    lines = [
        "# M4.3 政策源 二次探活 probe 报告（2026-09-01，knife 640）",
        "",
        "> **类型**: 640-A.1 probe (read-only;不写 cegr.observation)",
        "> **前置**: 639 DELIVERED;docs/59 §5.1 明确 6 REACHABLE 任免源 ≠ 政策源",
        "> **范围**: 13 URL (10 试点省政策承载路径 + 1 ccdi + 1 国务院 政策库)",
        "> **架构师依据**: 640 沿用 638/639 路径选择性 WAF 假设修正;政策承载路径候选",
        "",
        "## 0. 顶层裁定",
        "",
        f"**{top}** — 适用 {len(POLICY_V1_TARGETS)} cell, 实测 "
        f"{results['summary']['probed_cells']} cell。",
        "",
        "总分布:",
        "",
        f"- REACHABLE: {bv.get('REACHABLE', 0)}",
        f"- PARTIAL: {bv.get('PARTIAL', 0)}",
        f"- BLOCKED: {bv.get('BLOCKED', 0)}",
        "",
        "中央 vs 试点省分布:",
        "",
        f"- 中央 (ccdi /ldwd/ + 国务院 /zhengce/zhengceku/ = 2): "
        f"{bcv.get('central', {})}",
        f"- 试点省 (10 政策承载路径 /zwgk/zfwj/ + /zwgk/zfgb/ + /zwgk/ghjh/): "
        f"{bcv.get('provincial', {})}",
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
        "REACHABLE: HTTP 200 + body 含 `政策文件|政府公报|规划计划|政府工作报告|五年规划|规范性文件|policy|regulation|five.year.plan` marker。",
        "PARTIAL: HTTP 200 + body 已加载但 marker 未命中（栏目命中政策路径不正确）。",
        "BLOCKED: TLS reset / 403 WAF / 404 / connection error。",
        "二次探活 URL 选择（继承 639 PARTIAL/BLOCKED 已知 gap）:",
        "- 试点省: 639 REACHABLE 6 试点省的 /zwgk/ 任免栏目,640 重打 /zwgk/zfwj/ "
        "(政府文件) + /zwgk/zfgb/ (政府公报) + /zwgk/ghjh/ (规划计划) 政策承载路径。",
        "- ccdi: 639 PARTIAL /yaowen/ + /specialn/scjcf/ 是要闻 / 审查调查栏;640 试 "
        "/ldwd/ (领导/制度) 含部分政策。",
        "- 国务院: 639 PARTIAL /zhengce/ 是政策栏;640 加试 /zhengce/zhengceku/ "
        "(政策库) 子栏目。",
        "",
        "## 3. 639 vs 640 对比",
        "",
        "- 639 6 REACHABLE 任免源 (/zwgk/) ⇒ 640 重打为 10 政策承载路径 "
        "(/zwgk/zfwj/ + /zwgk/zfgb/ + /zwgk/ghjh/)。",
        "- 639 PARTIAL 中央 (ccdi 2 + 国务院 2) ⇒ 640 重打 ccdi /ldwd/ + 国务院 "
        "/zhengce/zhengceku/。",
        "- 639 BLOCKED 15 (npc TLS reset + 13 试点省 404/403) ⇒ 640 不复用,640 "
        "仅探 6 REACHABLE 试点省政策路径(避开 BLOCKED)。",
        "",
        "## 4. 数据源合规",
        "",
        "✓ 全部政府源 (ccdi.gov.cn / www.gov.cn / 6 www.*.gov.cn 政策承载路径);"
        "✓ 无商业库;✓ 无用户裁定 URL。",
        "",
        "## 5. 红线遵守",
        "",
        "- ✓ 不写 cegr.observation",
        "- ✓ 不静默硬编码 GDP 值",
        "- ✓ 不爬网（仅探可达性,不抓内容入库）",
        "- ✓ 脚本幂等（无 random / 无 time.sleep）",
        "- ✓ 不宣称 Gate / O1 / M2 / M4 PASS",
        "",
    ]
    REPORT_MD.write_text("\n".join(lines), encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description="640-A.1 政策源 二次探活")
    parser.add_argument("--sample-only", action="store_true",
                        help="Exit after first 3 probes (smoke test)")
    args = parser.parse_args()
    results = run_probe(sample_only=args.sample_only)
    write_outputs(results)
    print(f"640-A.1: probed {results['summary']['probed_cells']}/13 targets; "
          f"verdict counts = {results['summary']['by_verdict']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
