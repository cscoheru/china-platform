"""M4.1 — 政府工作报告 可达性 probe (knife 638 Block A.1).

Per knife 638 §2 / docs/54 §M4.1 / docs/57 §6:
- Probe targets: 国务院政府工作报告专栏 + 31 省人民政府首页/政府工作报告入口
- 32 URLs total (1 国务院 + 31 省)
- Verdict: REACHABLE / PARTIAL / BLOCKED (no NOT_APPLICABLE since this is target-list)
- Year probed: 2024 (current)

OUTPUT (read-only — does NOT write cegr.observation):
* docs/reports/m4_1_gov_report_probe_20260901.md
* evidence_pack/m4_1_gov_report_probe_20260901.json

Honesty rules:
- REACHABLE: HTTP 200 + body contains 政府工作报告 / 人民政府 marker
- PARTIAL: HTTP 200 + body loaded but no marker found (e.g. catalog landing only)
- BLOCKED: TLS reset / 403 WAF / 404 / connection error
- DSN-free: only network + filesystem.

Usage:
  python3 scripts/probe_gov_report_2024.py
  python3 scripts/probe_gov_report_2024.py --sample-only  # exit after 5 probes
"""
from __future__ import annotations

import argparse
import json
from collections import defaultdict
from pathlib import Path

from _probe_http_helpers import (
    GOV_REPORT_MARKER_RE,
    PROVINCE_SLUGS,
    classify_people_probe,
    fetch,
    now_utc_iso,
)

REPO_ROOT = Path(__file__).resolve().parent.parent
REPORT_MD = REPO_ROOT / "docs" / "reports" / "m4_1_gov_report_probe_20260901.md"
EVIDENCE_JSON = REPO_ROOT / "evidence_pack" / "m4_1_gov_report_probe_20260901.json"

PROV_LABEL = {
    "beijing": "北京市", "tianjin": "天津市", "shanghai": "上海市",
    "chongqing": "重庆市", "hebei": "河北省", "shanxi": "山西省",
    "innermongolia": "内蒙古自治区", "liaoning": "辽宁省",
    "jilin": "吉林省", "heilongjiang": "黑龙江省",
    "jiangsu": "江苏省", "zhejiang": "浙江省",
    "anhui": "安徽省", "fujian": "福建省", "jiangxi": "江西省",
    "shandong": "山东省", "henan": "河南省", "hubei": "湖北省",
    "hunan": "湖南省", "guangdong": "广东省", "guangxi": "广西壮族自治区",
    "hainan": "海南省", "sichuan": "四川省", "guizhou": "贵州省",
    "yunnan": "云南省", "tibet": "西藏自治区", "shaanxi": "陕西省",
    "gansu": "甘肃省", "qinghai": "青海省", "ningxia": "宁夏回族自治区",
    "xinjiang": "新疆维族自治区",
}

PROV_DOMAIN = {
    "beijing": "www.beijing.gov.cn", "tianjin": "www.tj.gov.cn",
    "shanghai": "www.shanghai.gov.cn", "chongqing": "www.cq.gov.cn",
    "hebei": "www.hebei.gov.cn", "shanxi": "www.shanxi.gov.cn",
    "innermongolia": "www.nmg.gov.cn", "liaoning": "www.ln.gov.cn",
    "jilin": "www.jl.gov.cn", "heilongjiang": "www.hlj.gov.cn",
    "jiangsu": "www.jiangsu.gov.cn", "zhejiang": "www.zj.gov.cn",
    "anhui": "www.ah.gov.cn", "fujian": "www.fujian.gov.cn",
    "jiangxi": "www.jx.gov.cn", "shandong": "www.shandong.gov.cn",
    "henan": "www.henan.gov.cn", "hubei": "www.hubei.gov.cn",
    "hunan": "www.hunan.gov.cn", "guangdong": "www.gd.gov.cn",
    "guangxi": "www.gxzf.gov.cn", "hainan": "www.hainan.gov.cn",
    "sichuan": "www.sc.gov.cn", "guizhou": "www.guizhou.gov.cn",
    "yunnan": "www.yn.gov.cn", "tibet": "www.xizang.gov.cn",
    "shaanxi": "www.shaanxi.gov.cn", "gansu": "www.gansu.gov.cn",
    "qinghai": "www.qinghai.gov.cn", "ningxia": "www.nx.gov.cn",
    "xinjiang": "www.xinjiang.gov.cn",
}

# 32 targets: 1 国务院 + 31 省
GOV_REPORT_TARGETS: list[tuple[str, str, str]] = [
    ("central", "国务院", "https://www.gov.cn/zwgk/zfgbg.htm"),
] + [
    (slug, PROV_LABEL[slug], f"https://{PROV_DOMAIN[slug]}/")
    for slug in PROVINCE_SLUGS
]


def probe_target(slug: str, entity_zh: str, url: str) -> dict:
    cell = {
        "slug": slug, "entity": entity_zh, "year": 2024,
        "source": "GOV_REPORT", "url": url,
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
    cell["verdict"] = classify_people_probe(code, reason, body, GOV_REPORT_MARKER_RE)
    return cell


def run_probe(sample_only: bool = False) -> dict:
    cells = []
    targets = GOV_REPORT_TARGETS[:5] if sample_only else GOV_REPORT_TARGETS
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
            "total_cells": len(GOV_REPORT_TARGETS),
            "probed_cells": len(cells),
            "sample_only": sample_only,
            "by_verdict": dict(by_verdict),
            "by_entity": dict(by_entity),
        },
        "probed_count": len(cells),
        "cells": cells,
        "probe_methodology": (
            "REACHABLE: HTTP 200 + body contains 政府工作报告/人民政府 marker. "
            "PARTIAL: HTTP 200 + body loaded but no marker. "
            "BLOCKED: TLS reset / 403 WAF / 404 / connection error. "
            "Targets: 1 国务院 (www.gov.cn/zwgk/zfgbg.htm) + 31 省人民政府首页. "
            "Inherits 636 WAF-IP-level block context (本机 IP 125.93.9.191)."
        ),
    }


def write_outputs(results: dict) -> None:
    EVIDENCE_JSON.parent.mkdir(parents=True, exist_ok=True)
    REPORT_MD.parent.mkdir(parents=True, exist_ok=True)
    EVIDENCE_JSON.write_text(
        json.dumps(results, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )

    # Markdown report
    bv = results["summary"]["by_verdict"]
    top = ("REACHABLE" if bv.get("REACHABLE", 0) == len(results["cells"])
            else "BLOCKED" if bv.get("BLOCKED", 0) == len(results["cells"])
            else "MIXED")
    lines = [
        "# M4.1 政府工作报告 可达性 probe 报告（2026-09-01，knife 638）",
        "",
        "> **类型**: 638-A.1 probe (read-only;不写 cegr.observation)",
        "> **前置**: 637 DELIVERED (路径 C 接受);docs/57 §6 下一步",
        "> **环境**: 本机 IP `125.93.9.191`（继承 636 WAF IP-level 阻断上下文）",
        "",
        "## 0. 顶层裁定",
        "",
        f"**{top}** — 适用 32 cell, 实测 {results['summary']['probed_cells']} cell。",
        "",
        "总分布:",
        "",
        f"- REACHABLE: {bv.get('REACHABLE', 0)}",
        f"- PARTIAL: {bv.get('PARTIAL', 0)}",
        f"- BLOCKED: {bv.get('BLOCKED', 0)}",
        "",
        "## 1. 实体逐项",
        "",
        "| slug | verdict | 备注 |",
        "|---|---|---|",
    ]
    for c in results["cells"]:
        note = c["reason"] if c["reason"] != "ok" else f"HTTP {c['http_code']}"
        lines.append(f"| {c['entity']} ({c['slug']}) | {c['verdict']} | {note} |")
    lines += [
        "",
        "## 2. 方法学",
        "",
        "REACHABLE: HTTP 200 + body 含 `政府工作报告|人民政府|工作报告` marker。",
        "PARTIAL: HTTP 200 + body 已加载但 marker 未命中（catalog-only landing）。",
        "BLOCKED: TLS reset / 403 WAF / 404 / connection error。",
        "Targets: 1 国务院 (www.gov.cn/zwgk/zfgbg.htm) + 31 省人民政府首页。",
        "继承 636 §2 WAF IP-level 阻断上下文（本机 IP 125.93.9.191）。",
        "",
        "## 3. 数据源合规",
        "",
        "✓ 全部 gov.cn 政府源；✓ 无商业库；✓ 无用户裁定 URL。",
        "",
        "## 4. 红线遵守",
        "",
        "- ✓ 不写 cegr.observation",
        "- ✓ 不静默硬编码 GDP 值",
        "- ✓ 不爬网（仅探可达性，不抓内容入库）",
        "- ✓ 脚本幂等（无 random / 无 time.sleep）",
        "- ✓ 不宣称 Gate / O1 / M2 / M4 PASS",
        "",
    ]
    REPORT_MD.write_text("\n".join(lines), encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description="638-A.1 政府工作报告 probe")
    parser.add_argument("--sample-only", action="store_true",
                        help="Exit after first 5 probes (smoke test)")
    args = parser.parse_args()
    results = run_probe(sample_only=args.sample_only)
    write_outputs(results)
    print(f"638-A.1: probed {results['summary']['probed_cells']}/32 targets; "
          f"verdict counts = {results['summary']['by_verdict']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())