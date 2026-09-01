"""M5 — WAF 网防G01 假设验证 probe 二维 (knife 643 Block A.1, M5 side).

Per knife 643 §2.643-A.1:
- 5 BLOCKED 省 (642 实测 /zwgk/zfwj/ 404 路径别名) → 路径别名深挖
  - 4 替代 subpath: /zwgk/zfgb/ /zwgk/zcwj/ (福建/河南 + 广东/贵州 zfgb)
- 国务院 替代子路径探测 (沿用 642 WAF 网防G01 marker 验证)
  - /zhengceku/ + /zhengce/ + /zhengce/2024-XX/YY/content_xxx.htm (具体)
- 1 cell: 国务院 /zwgk/2024-XX/YY/content_xxx.htm (子路径 WAF)
- 2 cell: 河南 /zwgk/zcwj/ + 贵州 /zwgk/szfwj/

HARD LIMITS:
- ≤10 HTTP total
- 不爬网 (no recursion; no follow pagination)
- curl only

OUTPUT:
* docs/reports/m5_waf_v2_probe_20260901.md
* evidence_pack/m5_waf_v2_probe_20260901.json
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
REPORT_MD = REPO_ROOT / "docs" / "reports" / "m5_waf_v2_probe_20260901.md"
EVIDENCE_JSON = REPO_ROOT / "evidence_pack" / "m5_waf_v2_probe_20260901.json"

TIMEOUT = 15
HTTP_LIMIT = 10

# 10 cells: 4 替代 subpath (福建/河南/广东/贵州 zfgb/zcwj) + 3 国务院 (zhengceku/zhengce/具体) +
# 1 国务院 zwgk/子路径 + 2 (额外 zcwj/szfwj)
PROBE_CELLS = [
    # 5 BLOCKED 省 /zwgk/zfwj/ 路径别名深挖 (4 替代 subpath × 1 省 = 4 cells)
    ("fujian",  "https://www.fujian.gov.cn/zwgk/zfgb/",      "alt_zfgb",      "policy"),
    ("fujian",  "https://www.fujian.gov.cn/zwgk/zcwj/",      "alt_zcwj",      "policy"),
    ("henan",   "https://www.henan.gov.cn/zwgk/zfgb/",       "alt_zfgb",      "policy"),
    ("guangdong","https://www.gd.gov.cn/zwgk/zfgb/",         "alt_zfgb",      "policy"),
    # 国务院 替代子路径探测 (3 cells: zhengceku + zhengce + 具体 URL)
    ("gov",     "https://www.gov.cn/zhengceku/",             "fallback_ku",   "policy"),
    ("gov",     "https://www.gov.cn/zhengce/",               "fallback_root", "policy"),
    ("gov",     "https://www.gov.cn/zhengce/2024-08/15/content_1155106.htm",
                                                             "fallback_real", "policy"),
    # 国务院 /zwgk/子路径 (WAF 网防G01 marker 验证 - 沿用 642)
    ("gov",     "https://www.gov.cn/zwgk/2024-08/15/content_xxx.htm",
                                                             "zwgk_sub",      "policy"),
    # 2 cell 补足 (贵州 szfwj + 河南 wjzl)
    ("guizhou", "https://www.guizhou.gov.cn/zwgk/szfwj/",    "alt_szfwj",     "policy"),
    ("henan",   "https://www.henan.gov.cn/zwgk/wjzl/",       "alt_wjzl",      "policy"),
]


def classify_waf(http_code: int, reason: str, body: bytes) -> str:
    """Verdict for M5 WAF 网防G01 假设验证 probe 二次.

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
        # WAF 网防G01 marker 检查 (沿用 642)
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
                f"M5 WAF 网防G01 假设验证二次;{len(PROBE_CELLS)} cells; "
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
        "# M5 WAF 网防G01 假设验证 probe 二次报告（2026-09-01，knife 643 M5 side）",
        "",
        "> **类型**: 643-A.1 M5 探活 (read-only;**不写 cegr.* 表**)",
        "> **前置**: 642 关键反发现 = 5 BLOCKED 省 /zwgk/zfwj/ 全 404 路径别名（非 WAF）",
        "> **范围**: 10 URL (4 替代 subpath + 3 国务院 替代 + 1 国务院 zwgk/子路径 + 2 额外 zcwj/szfwj/wjzl)",
        "> **架构师依据**: 643 spike 并行; M5 二次路径别名深挖; WAF 网防G01 进一步验证",
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
        "## 2. 5 BLOCKED 省根因分析深化",
        "",
        "642 关键反发现: 5 BLOCKED 省 /zwgk/zfwj/ 全 404 (路径别名而非 WAF)。",
        "643 二次探活目的: 验证 4 替代 subpath /zwgk/zfgb/ /zwgk/zcwj/ /zwgk/szfwj/ /zwgk/wjzl/",
        "是否 REACHABLE;如果 ≥1 REACHABLE ⇒ 5 BLOCKED 省根因确实 = 路径别名（不是 WAF）。",
        "",
        "## 3. 国务院 替代路径 verdict",
        "",
        "| URL | 642 实测 | 643 实测 | 替代 verdict |",
        "|---|---|---|---|",
        "| /zhengce/content/ | 403 WAF | — | (642 BLOCKED 已记录) |",
        "| /zhengceku/ | — | 643 实测 | (本页探测) |",
        "| /zhengce/ | — | 643 实测 | (本页探测) |",
        "| /zhengce/具体 | — | 643 实测 | (本页探测) |",
        "| /zwgk/ | 403 WAF | — | (642 BLOCKED 已记录) |",
        "| /zwgk/2024-XX/YY/content_xxx.htm | — | 643 实测 | (本页探测) |",
        "",
        "## 4. 方法学",
        "",
        "≤10 HTTP total (10 cells 实测).",
        "verdict 映射 (沿用 642):",
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
    parser = argparse.ArgumentParser(description="643-A.1 M5 WAF probe 二次")
    args = parser.parse_args()
    results = run_probe()
    write_outputs(results)
    print(
        f"643-A.1 M5 v2: http_count={results['summary']['http_count']}, "
        f"probed_count={results['summary']['probed_count']}, "
        f"top_verdict={results['summary']['top_verdict']}, "
        f"by_verdict={results['summary']['by_verdict']}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
