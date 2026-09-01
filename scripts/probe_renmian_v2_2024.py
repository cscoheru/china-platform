"""M4.2 — 任免公告 可达性 二次探活 (knife 639 Block A.1).

Per knife 639 §2.639-A.1 / docs/58 §3 + 638 receipt:
- 638 PARTIAL ccdi 是首页非任免页;639 重探 ccdi 公告列表 (yaowen + 审查调查)
- 638 BLOCKED npc 用 http;639 重探 https n/c2 + n
- 638 BLOCKED 国务院 /zwgk/zfgbg.htm 404;639 重探 /zhengce/ + /yaowen/
- 23 REACHABLE 试点省 (继承 638 REACHABLE 23) 任免栏目 `/zwgk/` 探活
- 29 URLs total (6 central + 23 provincial)

OUTPUT (read-only — does NOT write cegr.observation):
* docs/reports/m4_2_renmian_v2_probe_20260901.md
* evidence_pack/m4_2_renmian_v2_probe_20260901.json

Honesty rules:
- REACHABLE: HTTP 200 + body contains 任免 marker
- PARTIAL: HTTP 200 + body loaded but no marker found
- BLOCKED: TLS reset / 403 WAF / 404 / connection error
- DSN-free: only network + filesystem.

Usage:
  python3 scripts/probe_renmian_v2_2024.py
  python3 scripts/probe_renmian_v2_2024.py --sample-only  # exit after first 6 probes
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
REPORT_MD = REPO_ROOT / "docs" / "reports" / "m4_2_renmian_v2_probe_20260901.md"
EVIDENCE_JSON = REPO_ROOT / "evidence_pack" / "m4_2_renmian_v2_probe_20260901.json"

# 638 BLOCKED 9: 国务院 / 天津 / 山东 / 湖北 / 江西 / 广西 / 西藏 / 甘肃 / 青海
# 639 REACHABLE 23 (继承): 北京 / 上海 / 重庆 / 河北 / 山西 / 内蒙古 / 辽宁 / 吉林 /
#                       黑龙江 / 江苏 / 浙江 / 安徽 / 福建 / 河南 / 湖南 / 广东 /
#                       海南 / 四川 / 贵州 / 云南 / 陕西 / 宁夏 / 新疆
RENMIAN_V2_TARGETS: list[tuple[str, str, str]] = [
    # 1. ccdi 公告列表 (638 PARTIAL 是首页;639 探公告列表栏目)
    ("central-discipline-yaowen", "中央纪委要闻", "https://www.ccdi.gov.cn/yaowen/"),
    ("central-discipline-shenji", "中央纪委审查调查", "https://www.ccdi.gov.cn/specialn/scjcf/"),

    # 2. npc 新 URL (HTTPS + 任免栏目)
    ("npc-renmian", "全国人大任免", "https://npc.gov.cn/npc/c2/"),
    ("npc-news", "全国人大要闻", "https://npc.gov.cn/npc/"),

    # 3. 国务院任免正确 URL
    ("central-zhengce", "国务院政策", "https://www.gov.cn/zhengce/"),
    ("central-yaowen", "国务院要闻", "https://www.gov.cn/yaowen/"),

    # 4. 23 REACHABLE 试点省任免栏目 (继承 638 23 个 www.*.gov.cn/ REACHABLE)
    ("beijing-renmian", "北京任免", "https://www.beijing.gov.cn/zwgk/"),
    ("shanghai-renmian", "上海任免", "https://www.shanghai.gov.cn/zwgk/"),
    ("chongqing-renmian", "重庆任免", "https://www.cq.gov.cn/zwgk/"),
    ("hebei-renmian", "河北任免", "https://www.hebei.gov.cn/zwgk/"),
    ("shanxi-renmian", "山西任免", "https://www.shanxi.gov.cn/zwgk/"),
    ("innermongolia-renmian", "内蒙古任免", "https://www.nmg.gov.cn/zwgk/"),
    ("liaoning-renmian", "辽宁任免", "https://www.ln.gov.cn/zwgk/"),
    ("jilin-renmian", "吉林任免", "https://www.jl.gov.cn/zwgk/"),
    ("heilongjiang-renmian", "黑龙江任免", "https://www.hlj.gov.cn/zwgk/"),
    ("jiangsu-renmian", "江苏任免", "https://www.jiangsu.gov.cn/zwgk/"),
    ("zhejiang-renmian", "浙江任免", "https://www.zj.gov.cn/zwgk/"),
    ("anhui-renmian", "安徽任免", "https://www.ah.gov.cn/zwgk/"),
    ("fujian-renmian", "福建任免", "https://www.fujian.gov.cn/zwgk/"),
    ("henan-renmian", "河南任免", "https://www.henan.gov.cn/zwgk/"),
    ("hunan-renmian", "湖南任免", "https://www.hunan.gov.cn/zwgk/"),
    ("guangdong-renmian", "广东任免", "https://www.gd.gov.cn/zwgk/"),
    ("hainan-renmian", "海南任免", "https://www.hainan.gov.cn/zwgk/"),
    ("sichuan-renmian", "四川任免", "https://www.sc.gov.cn/zwgk/"),
    ("guizhou-renmian", "贵州任免", "https://www.guizhou.gov.cn/zwgk/"),
    ("yunnan-renmian", "云南任免", "https://www.yn.gov.cn/zwgk/"),
    ("shaanxi-renmian", "陕西任免", "https://www.shaanxi.gov.cn/zwgk/"),
    ("ningxia-renmian", "宁夏任免", "https://www.nx.gov.cn/zwgk/"),
    ("xinjiang-renmian", "新疆任免", "https://www.xinjiang.gov.cn/zwgk/"),
]


def probe_target(slug: str, entity_zh: str, url: str) -> dict:
    cell = {
        "slug": slug, "entity": entity_zh, "year": 2024,
        "source": "RENMIAN_ANNOUNCEMENT_V2", "url": url,
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
    targets = RENMIAN_V2_TARGETS[:6] if sample_only else RENMIAN_V2_TARGETS
    for slug, entity_zh, url in targets:
        cells.append(probe_target(slug, entity_zh, url))

    by_verdict = defaultdict(int)
    for c in cells:
        by_verdict[c["verdict"]] += 1
    by_entity = defaultdict(int)
    for c in cells:
        by_entity[c["entity"]] = c["verdict"]
    by_class = defaultdict(int)
    for c in cells:
        # central vs provincial 分布 (协助 638 vs 639 对比)
        by_class["central" if "central" in c["slug"] or "npc" in c["slug"]
                 else "provincial"] += 1
    by_class_verdict = defaultdict(lambda: defaultdict(int))
    for c in cells:
        cls = ("central" if "central" in c["slug"] or "npc" in c["slug"]
               else "provincial")
        by_class_verdict[cls][c["verdict"]] += 1

    return {
        "generated_at": now_utc_iso(),
        "summary": {
            "total_cells": len(RENMIAN_V2_TARGETS),
            "probed_cells": len(cells),
            "sample_only": sample_only,
            "by_verdict": dict(by_verdict),
            "by_class": dict(by_class),
            "by_class_verdict": {k: dict(v) for k, v in by_class_verdict.items()},
            "by_entity": dict(by_entity),
        },
        "probed_count": len(cells),
        "cells": cells,
        "probe_methodology": (
            "REACHABLE: HTTP 200 + body contains 任免/任免名单 marker. "
            "PARTIAL: HTTP 200 + body loaded but no marker. "
            "BLOCKED: TLS reset / 403 WAF / 404 / connection error. "
            "Targets: 6 中央 (ccdi 2 + npc 2 + 国务院 2) + 23 REACHABLE 试点省 "
            "(继承 638 23 个 www.*.gov.cn/ REACHABLE) 任免栏目 /zwgk/. "
            "二次探活理由: 638 PARTIAL 是首页非任免页; nbc/npc URL 是 HTTP "
            "或错误路径; /zwgk/ 为任免公告栏目探针."
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
        "# M4.2 任免公告 二次探活 probe 报告（2026-09-01，knife 639）",
        "",
        "> **类型**: 639-A.1 probe (read-only;不写 cegr.observation)",
        "> **前置**: 638 DELIVERED;docs/58 §3 任免 PARTIAL/BLOCKED 已知 gap",
        "> **范围**: 29 URL (6 中央 + 23 REACHABLE 试点省任免栏目)",
        "> **架构师依据**: 638 PARTIAL 是首页非任免页;639 重打 6 中央 URL "
        "(HTTPS / 正确路径 / 任免栏目) + 23 试点省 `/zwgk/` 任免栏目",
        "",
        "## 0. 顶层裁定",
        "",
        f"**{top}** — 适用 {len(RENMIAN_V2_TARGETS)} cell, 实测 "
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
        f"- 中央 (ccdi 2 + npc 2 + 国务院 2 = 6): "
        f"{bcv.get('central', {})}",
        f"- 试点省 (23 REACHABLE 继承自 638): "
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
        "REACHABLE: HTTP 200 + body 含 `任免|任免名单|appoint|removal|departure` marker。",
        "PARTIAL: HTTP 200 + body 已加载但 marker 未命中（栏目命中任免路径不正确）。",
        "BLOCKED: TLS reset / 403 WAF / 404 / connection error。",
        "二次探活 URL 选择（继承 638 PARTIAL/BLOCKED 已知 gap）:",
        "- ccdi: 638 PARTIAL `https://www.ccdi.gov.cn/` 是首页;639 重打 "
        "`/yaowen/` (要闻) + `/specialn/scjcf/` (审查调查,含部分任免)。",
        "- npc: 638 BLOCKED `http://www.npc.gov.cn/` timeout;639 改 HTTPS "
        "`/npc/c2/` (任免) + `/npc/` (要闻)。",
        "- 国务院: 638 BLOCKED `https://www.gov.cn/zwgk/zfgbg.htm` 404 "
        "(是政府工作报告路径);639 重打 `/zhengce/` (政策) + `/yaowen/` (要闻)。",
        "- 试点省: 继承 638 23 个 `www.*.gov.cn/` REACHABLE;639 加探 `/zwgk/` "
        "任免栏目 (BLOCKED 9 省 天津/山东/湖北/江西/广西/西藏/甘肃/青海 + 国务院 不探)。",
        "",
        "## 3. 638 vs 639 对比",
        "",
        "- 638 PARTIAL/BLOCKED 3 URL (ccdi 首页 + npc HTTP + 国务院 404) "
        "⇒ 639 重打为 6 URL (ccdi 2 + npc 2 + 国务院 2)。",
        "- 638 23 REACHABLE 试点省 `/` ⇒ 639 加探 `/zwgk/` 任免栏目 23 URL。",
        "",
        "## 4. 数据源合规",
        "",
        "✓ 全部政府源 (ccdi.gov.cn / npc.gov.cn / www.gov.cn / 23 www.*.gov.cn);"
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
    parser = argparse.ArgumentParser(description="639-A.1 任免公告 二次探活")
    parser.add_argument("--sample-only", action="store_true",
                        help="Exit after first 6 probes (smoke test)")
    args = parser.parse_args()
    results = run_probe(sample_only=args.sample_only)
    write_outputs(results)
    print(f"639-A.1: probed {results['summary']['probed_cells']}/29 targets; "
          f"verdict counts = {results['summary']['by_verdict']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
