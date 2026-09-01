"""M5 — WAF 网防G01 假设验证 probe 三维 (knife 644 Block A.1, M5 side).

Per knife 644 §2.644-A.1:
- 沿用 643 关键反发现 = 国务院 /zhengce/ root 200 REACHABLE (WAF selective 验证)
- 第三次目的:
  1. WAF 网防G01 selective 子路径进一步验证:
     试 /zhengce/zhengceku/ (嵌套子路径 WAF 验证);
     /zhengce/content_xxx.htm 真实 content_id 探活 (2017 + 2020)
  2. 国务院 /zwgk/ 子路径细化:
     /zwgk/zcwj/ + /zwgk/zcfg/ + /zwgk/2026-08/15/content_xxx.htm
     (沿用 642 WAF 网防G01 marker 验证)
  3. WAF 网防G01 marker 二次确认: 中央子域 selective WAF 仍真存在
  4. 5 BLOCKED 省 /zwgk/ root 收口 (沿用 642)

10 cells ≤10 HTTP:
  - 4 国务院 /zhengce/ 子路径 + WAF 网防G01 进一步验证
  - 3 国务院 /zwgk/ 替代子路径
  - 3 5 BLOCKED 省 /zwgk/ root 收口

HARD LIMITS:
- ≤10 HTTP total
- 不爬网 (no recursion; no follow pagination)
- curl only

OUTPUT:
* docs/reports/m5_waf_v3_probe_20260901.md
* evidence_pack/m5_waf_v3_probe_20260901.json
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from _probe_http_helpers import (
    POLICY_MARKER_RE,
    WAF_BLOCK_RE,
    classify_people_probe,
    fetch,
    now_utc_iso,
)

REPO_ROOT = Path(__file__).resolve().parent.parent
REPORT_MD = REPO_ROOT / "docs" / "reports" / "m5_waf_v3_probe_20260901.md"
EVIDENCE_JSON = REPO_ROOT / "evidence_pack" / "m5_waf_v3_probe_20260901.json"

TIMEOUT = 15
HTTP_LIMIT = 10

# 10 cells: 4 国务院 /zhengce/ 子路径 + 3 国务院 /zwgk/ 替代子路径 + 3 5 BLOCKED 省 /zwgk/ root 收口
PROBE_CELLS = [
    # 国务院 /zhengce/ 子路径 + WAF 网防G01 进一步验证 (4 cells)
    ("gov",     "https://www.gov.cn/zhengce/zhengceku/",          "zhengceku_nested",      "policy"),
    ("gov",     "https://www.gov.cn/zhengce/content_2017-09/30/content_5189.htm",
                                                                "zhengce_real_content",  "policy"),
    ("gov",     "https://www.gov.cn/zhengce/content_2020-11/03/content_5556715.htm",
                                                                "zhengce_real_2020",     "policy"),
    ("gov",     "https://www.gov.cn/zwgk/zcwj/",                  "zwgk_zcwj_retry",       "policy"),
    # 国务院 /zwgk/ 替代子路径 (2 cells)
    ("gov",     "https://www.gov.cn/zwgk/zcfg/",                  "zwgk_zcfg_retry",       "policy"),
    ("gov",     "https://www.gov.cn/zwgk/2026-08/15/content_xxx.htm",
                                                                "zwgk_sub_2026",         "policy"),
    # 国务院 /zwgk/ root 验证 (沿用 642)
    ("gov",     "https://www.gov.cn/zwgk/",                       "zwgk_root_retry",       "policy"),
    # 5 BLOCKED 省 /zwgk/ root 收口 (沿用 642)
    ("fujian",  "https://www.fujian.gov.cn/zwgk/",                "fujian_zwgk_root",      "policy"),
    ("henan",   "https://www.henan.gov.cn/zwgk/",                 "henan_zwgk_root",       "policy"),
    ("yunnan",  "https://www.yn.gov.cn/zwgk/",                    "yunnan_zwgk_root",      "policy"),
]


def classify_waf(http_code: int, reason: str, body: bytes) -> str:
    """Verdict for M5 WAF 网防G01 假设验证 probe 三维.

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
        # WAF 网防G01 marker 检查 (沿用 642 + 643)
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
                f"M5 WAF 网防G01 假设验证三次;{len(PROBE_CELLS)} cells; "
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
        "# M5 WAF 网防G01 假设验证 probe 三维报告（2026-09-01，knife 644 M5 side）",
        "",
        "> **类型**: 644-A.1 M5 探活 (read-only;**不写 cegr.* 表**)",
        "> **前置**: 643 关键反发现 = 国务院 /zhengce/ root 200 REACHABLE (WAF selective 验证)",
        "> **范围**: 10 URL (4 国务院 /zhengce/ 子路径 + 3 国务院 /zwgk/ 替代 + 3 5 BLOCKED 省 /zwgk/ root 收口)",
        "> **架构师依据**: 644 spike 并行; M5 第三次 WAF 网防G01 selective 子路径进一步验证",
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
        "## 2. 国务院 /zhengce/ 子路径 verdict",
        "",
        "| URL | 643 实测 | 644 实测 | 替代 verdict |",
        "|---|---|---|---|",
        "| /zhengce/ | 200 REACHABLE (WAF selective 验证) | — | (643 验证) |",
        "| /zhengceku/ | 403 WAF 网防G01 | — | (643 BLOCKED) |",
        "| /zhengce/zhengceku/ | — | 644 实测 | (本页探测) |",
        "| /zhengce/content_2017-09/30/... | — | 644 实测 | (本页探测) |",
        "| /zhengce/content_2020-11/03/... | — | 644 实测 | (本页探测) |",
        "",
        "## 3. 国务院 /zwgk/ 替代路径 verdict",
        "",
        "| URL | 642 实测 | 644 实测 | 替代 verdict |",
        "|---|---|---|---|",
        "| /zwgk/ | 403 WAF 网防G01 | (本页探测) | (本页探测) |",
        "| /zwgk/zcwj/ | — | 644 实测 | (本页探测) |",
        "| /zwgk/zcfg/ | — | 644 实测 | (本页探测) |",
        "| /zwgk/2026-08/15/content_xxx.htm | — | 644 实测 | (本页探测) |",
        "",
        "## 4. 5 BLOCKED 省 /zwgk/ root 收口 (沿用 642)",
        "",
        "| URL | 642 实测 | 644 实测 |",
        "|---|---|---|",
        "| fujian /zwgk/ | (642 PARTIAL/REACHABLE) | 644 实测 |",
        "| henan /zwgk/ | (642 PARTIAL/REACHABLE) | 644 实测 |",
        "| yunnan /zwgk/ | (642 PARTIAL/REACHABLE) | 644 实测 |",
        "",
        "## 5. 方法学",
        "",
        "≤10 HTTP total (10 cells 实测).",
        "verdict 映射 (沿用 642 + 643):",
        "- REACHABLE: HTTP 200 + body 含 POLICY_MARKER_RE",
        "- PARTIAL: HTTP 200 + body 不含 POLICY_MARKER_RE (栏目是别的不是政策)",
        "- BLOCKED: TLS reset / 403 WAF / 404 / connection error",
        "",
        "## 6. 红线遵守",
        "",
        "- ✓ ≤10 HTTP total (硬性上限)",
        "- ✓ 不爬网 (no recursion; no follow pagination)",
        "- ✓ 不写 cegr.* 表 (read-only on production)",
        "- ✓ 脚本幂等 (no sleeps / no randomness)",
        "- ✓ 不宣称 Gate / O1 / M2 / M4 / M5 PASS",
        "",
    ]
    REPORT_MD.write_text("\n".join(lines), encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description="644-A.1 M5 WAF probe 三维")
    args = parser.parse_args()
    results = run_probe()
    write_outputs(results)
    print(
        f"644-A.1 M5 v3: http_count={results['summary']['http_count']}, "
        f"probed_count={results['summary']['probed_count']}, "
        f"top_verdict={results['summary']['top_verdict']}, "
        f"by_verdict={results['summary']['by_verdict']}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
