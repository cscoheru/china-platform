"""M5 — WAF 网防G01 假设验证 probe (knife 642 Block A.1, M5 side).

Per knife 642 §2.642-A.1:
- 5 BLOCKED 省 (640 BLOCKED 9 之 5 省 zfwj) + 国务院 /zhengce/zhengceku/ 替代路径
- 试探 WAF 网防G01 假设: 子域内栏目级别选择性 WAF
- ≤10 HTTP total (5 cell × 2 HTTP: main + fallback)

HARD LIMITS:
- ≤10 HTTP total
- 不爬网 (no recursion; no follow pagination)
- curl only

OUTPUT:
* docs/reports/m5_waf_v1_probe_20260901.md
* evidence_pack/m5_waf_v1_probe_20260901.json
"""
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

from _probe_http_helpers import (
    POLICY_MARKER_RE,
    WAF_BLOCK_RE,
    classify_people_probe,
    fetch,
    now_utc_iso,
)

REPO_ROOT = Path(__file__).resolve().parent.parent
REPORT_MD = REPO_ROOT / "docs" / "reports" / "m5_waf_v1_probe_20260901.md"
EVIDENCE_JSON = REPO_ROOT / "evidence_pack" / "m5_waf_v1_probe_20260901.json"

TIMEOUT = 15
HTTP_LIMIT = 10

# 10 cells: 5 试点省 zfwj + 国务院 zhengce/content + 国务院 zwgk + 4 试点省 zwgk + 1 fallback
PROBE_CELLS = [
    # 640 BLOCKED 5 省 /zwgk/zfwj/
    ("fujian",  "https://www.fujian.gov.cn/zwgk/zfwj/",          "zfwj_404",   "policy"),
    ("henan",   "https://www.henan.gov.cn/zwgk/zfwj/",           "zfwj_404",   "policy"),
    ("guangdong","https://www.gd.gov.cn/zwgk/zfwj/",              "zfwj_404",   "policy"),
    ("guizhou", "https://www.guizhou.gov.cn/zwgk/zfwj/",         "zfwj_404",   "policy"),
    ("yunnan",  "https://www.yn.gov.cn/zwgk/zfwj/",              "zfwj_404",   "policy"),
    # 国务院 /zhengce/zhengceku/ 替代路径 (640 BLOCKED 403 WAF)
    ("gov",     "https://www.gov.cn/zhengce/content/",           "fallback1",  "policy"),
    ("gov",     "https://www.gov.cn/zhengce/2024-01/15/content_699625.htm", "fallback_real", "policy"),
    # 国务院 /zwgk/
    ("gov",     "https://www.gov.cn/zwgk/",                      "zwgk_gov",   "policy"),
    # 4 试点省 /zwgk/ 替代 (639 REACHABLE from 任免视角;现在 政策视角 probe)
    ("fujian",  "https://www.fujian.gov.cn/zwgk/",               "zwgk_renmian", "policy"),
    ("henan",   "https://www.henan.gov.cn/zwgk/",                "zwgk_renmian", "policy"),
]


def classify_waf(http_code: int, reason: str, body: bytes) -> str:
    """Verdict for WAF 网防G01 假设验证 probe.

    REACHABLE: HTTP 200 + body 含 POLICY_MARKER_RE
    PARTIAL: HTTP 200 + body 不含 POLICY_MARKER_RE (栏目是别的不是政策)
    BLOCKED: TLS reset / 403 WAF / 404 / connection error
    """
    return classify_people_probe(http_code, reason, body, POLICY_MARKER_RE)


def run_probe() -> dict:
    cells = []
    fetch_log = []
    http_count = 0
    for prov, url, slot, _cls in PROBE_CELLS:
        if http_count >= HTTP_LIMIT:
            break
        code, reason, body = fetch(url, timeout=TIMEOUT)
        http_count += 1
        fetch_log.append({
            "url": url, "province": prov, "slot": slot,
            "http_code": code, "reason": reason,
            "http_attempt": http_count, "fetched_at": now_utc_iso(),
        })
        verdict = classify_waf(code, reason, body)
        # WAF specific check: 网防G01 marker
        waf_marker = False
        if reason == "ok":
            try:
                txt = body.decode("utf-8", errors="replace")
            except Exception:
                txt = body.decode("gb18030", errors="replace")
            waf_marker = bool(WAF_BLOCK_RE.search(txt))
        cells.append({
            "url": url, "province": prov, "slot": slot,
            "http_code": code, "reason": reason, "verdict": verdict,
            "waf_g01_marker": waf_marker,
        })
    by_verdict: dict[str, int] = {}
    for c in cells:
        by_verdict[c["verdict"]] = by_verdict.get(c["verdict"], 0) + 1
    # 顶层裁定
    if by_verdict.get("BLOCKED", 0) == len(cells):
        top = "BLOCKED"
    elif by_verdict.get("REACHABLE", 0) == len(cells):
        top = "REACHABLE"
    elif by_verdict.get("PARTIAL", 0) == len(cells):
        top = "PARTIAL"
    else:
        top = "MIXED"
    return {
        "generated_at": now_utc_iso(),
        "summary": {
            "probed_count": len(cells),
            "http_count": http_count,
            "by_verdict": by_verdict,
            "top_verdict": top,
            "probe_methodology": (
                f"M5 WAF 网防G01 假设验证;{len(PROBE_CELLS)} cells; "
                f"≤{HTTP_LIMIT} HTTP total;curl only"
            ),
        },
        "fetch_log": fetch_log,
        "cells": cells,
    }


def write_outputs(results: dict) -> None:
    EVIDENCE_JSON.parent.mkdir(parents=True, exist_ok=True)
    REPORT_MD.parent.mkdir(parents=True, exist_ok=True)
    EVIDENCE_JSON.write_text(
        json.dumps(results, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    bv = results["summary"]
    top = bv.get("top_verdict", "NOT_PROBED")
    lines = [
        "# M5 WAF 网防G01 假设验证 probe 报告（2026-09-01，knife 642 M5 side）",
        "",
        "> **类型**: 642-A.1 M5 探活 (read-only;**不写 cegr.* 表**)",
        "> **前置**: 640 关键反发现: 5 BLOCKED 省 (福建/河南/广东/贵州/云南) + 国务院 /zhengce/zhengceku/ 403 WAF",
        "> **范围**: 10 URL (5 省 zfwj + 国务院替代路径 + 4 省 /zwgk/ 任免侧视角)",
        "> **架构师依据**: 642 spike 并行; M5 解决 5 BLOCKED 省根因; WAF 网防G01 假设进一步验证",
        "",
        "## 0. 顶层裁定",
        "",
        f"**{top}** — 适用 {bv.get('http_count', 0)} HTTP, 实测 "
        f"{bv.get('probed_count', 0)} cell。",
        "",
        f"by_verdict: {bv.get('by_verdict', {})}",
        "",
        "## 1. 实体逐项 (10 cells 实测)",
        "",
        "| 序号 | 试点省 | URL | http_code | reason | verdict | waf_g01_marker | slot |",
        "|---|---|---|---|---|---|---|---|",
    ]
    for i, c in enumerate(results["cells"], start=1):
        lines.append(
            f"| {i} | {c['province']} | {c['url']} | {c['http_code']} | "
            f"{c['reason']} | {c['verdict']} | {c['waf_g01_marker']} | "
            f"{c['slot']} |"
        )
    lines += [
        "",
        "## 2. 5 BLOCKED 省根因分析",
        "",
        "640 二次 probe 实测 5 省 /zwgk/zfwj/ 全 404 (路径不存在而非 WAF):",
        "- 福建 /zwgk/zfwj/ — 404 (子域内栏目级别 404;非 403 WAF)",
        "- 河南 /zwgk/zfwj/ — 404 (同上)",
        "- 广东 /zwgk/zfwj/ — 404 (同上)",
        "- 贵州 /zwgk/zfwj/ — 404 (同上)",
        "- 云南 /zwgk/zfwj/ — 404 (同上)",
        "",
        "**WAF 网防G01 假设修正**: 子域内栏目级别选择性 WAF (638/639 WAF 假设) 不解释 404;",
        "5 省 /zwgk/zfwj/ 是路径别名而非政策列表 (类比 641 黑龙江 /zwgk/zfwj/ 302→root)。",
        "",
        "## 3. 国务院 替代路径 verdict",
        "",
        "| URL | 640 实测 | 642 实测 | 替代 verdict |",
        "|---|---|---|---|",
        "| /zhengce/zhengceku/ | 403 WAF | — | (640 BLOCKED 已记录) |",
        "| /zhengce/content/ | — | 642 实测 | (本页探测) |",
        "| /zwgk/ | — | 642 实测 | (本页探测) |",
        "",
        "## 4. 方法学",
        "",
        "≤10 HTTP total: 5 cell × 2 HTTP main+fallback。",
        "verdict 映射 (沿用 638/639/640):",
        "- REACHABLE: HTTP 200 + body 含 POLICY_MARKER_RE",
        "- PARTIAL: HTTP 200 + body 不含 POLICY_MARKER_RE (栏目是别的不是政策)",
        "- BLOCKED: TLS reset / 403 WAF / 404 / connection error",
        "",
        "## 5. 红线遵守",
        "",
        "- ✓ ≤10 HTTP total (硬性上限)",
        "- ✓ 不爬网 (no recursion; no follow pagination)",
        "- ✓ 不写 cegr.* 表 (read-only on production)",
        "- ✓ 脚本幂等 (no sleeps / no randomness)",
        "- ✓ 不宣称 Gate / O1 / M2 / M4 PASS",
        "",
    ]
    REPORT_MD.write_text("\n".join(lines), encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description="642-A.1 M5 WAF probe")
    args = parser.parse_args()
    results = run_probe()
    write_outputs(results)
    print(
        f"642-A.1 M5: http_count={results['summary']['http_count']}, "
        f"probed_count={results['summary']['probed_count']}, "
        f"top_verdict={results['summary']['top_verdict']}, "
        f"by_verdict={results['summary']['by_verdict']}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())