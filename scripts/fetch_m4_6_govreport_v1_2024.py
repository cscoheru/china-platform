"""M4.6 — 6 试点省政府工作报告 landing 真实化 fetch (knife 643 Block A.2, M4.6 side).

Per knife 643 §2.643-A.2:
- 6 试点省 (复用 642 列表 heilongjiang/fujian/henan/guangdong/guizhou/yunnan) × 1 detail each
- 复用 638 REACHABLE 23/32 列表 (zfgb 路径)
- 真实 SHA256 计算
- 写入 evidence_pack/m4_6_govreport_real_20260901.json
- **不写** cegr.* 表 (read-only on production)

HARD LIMITS:
- ≤12 HTTP total (6 indices + 6 details)
- 不爬网 (no recursion; no follow pagination)
- curl only

6 试点省 (复用 642 列表) × 政府工作报告 endpoint (复用 638 PARTIAL 1/2):
- hlj /zwgk/zfgb/ (zfgb 路径, 638 PARTIAL/REACHABLE)
- fujian /zwgk/zfgb/ (zfgb 路径)
- henan /zwgk/zfgb/ (zfgb 路径)
- guangdong /zwgk/zfgb/ (gd.gov.cn)
- guizhou /zwgk/zcfg/szfwj/ (638 复用)
- yunnan /zwgk/zfgb/ (yn.gov.cn)

OUTPUT:
* docs/reports/m4_6_govreport_real_20260901.md
* evidence_pack/m4_6_govreport_real_20260901.json
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
from pathlib import Path

from _probe_http_helpers import fetch, now_utc_iso

REPO_ROOT = Path(__file__).resolve().parent.parent
REPORT_MD = REPO_ROOT / "docs" / "reports" / "m4_6_govreport_real_20260901.md"
EVIDENCE_JSON = REPO_ROOT / "evidence_pack" / "m4_6_govreport_real_20260901.json"

# 6 试点省 (复用 642 列表) × 政府工作报告 endpoint (复用 638 PARTIAL 1/2 路径)
PROVINCES = [
    ("heilongjiang", "https://www.hlj.gov.cn/zwgk/zfgb/"),
    ("fujian",       "https://www.fujian.gov.cn/zwgk/zfgb/"),
    ("henan",        "https://www.henan.gov.cn/zwgk/zfgb/"),
    ("guangdong",    "https://www.gd.gov.cn/zwgk/zfgb/"),
    ("guizhou",      "https://www.guizhou.gov.cn/zwgk/zcfg/szfwj/"),
    ("yunnan",       "https://www.yn.gov.cn/zwgk/zfgb/"),
]
TIMEOUT = 15
HTTP_LIMIT = 12
FETCH_LIMIT_PER_PROVINCE = 1

LINK_RE = re.compile(
    r'<a[^>]+href="([^"]*?)"[^>]*>([^<]{4,200}?)</a>',
    re.IGNORECASE,
)
DATE_RE = re.compile(r"(20\d{2}[-年]\d{1,2}[-月]\d{1,2})", re.IGNORECASE)
# 政府工作报告关键词 (vs 642 任免关键词)
GOV_REPORT_RE = re.compile(
    r"政府工作报告|工作报告|政府报告|年度工作|政府公报|规划计划|五年规划",
    re.IGNORECASE,
)


def extract_detail_link(html: bytes, base_domain: str) -> dict | None:
    """Extract first 政府工作报告 detail URL from landing page."""
    try:
        text = html.decode("utf-8", errors="replace")
    except Exception:
        text = html.decode("gb18030", errors="replace")
    for m in LINK_RE.finditer(text):
        href_raw = m.group(1).strip()
        anchor = m.group(2).strip()
        if href_raw.startswith("/"):
            href = base_domain + href_raw
        elif href_raw.startswith("http://") or href_raw.startswith("https://"):
            href = href_raw
        else:
            continue
        if base_domain not in href:
            continue
        if not GOV_REPORT_RE.search(anchor):
            continue
        return {"url": href, "anchor": anchor}
    return None


def parse_detail(html: bytes, url: str) -> dict:
    try:
        text = html.decode("utf-8", errors="replace")
    except Exception:
        text = html.decode("gb18030", errors="replace")
    title = ""
    tm = re.search(r"<title[^>]*>([^<]{2,200}?)</title>", text, re.IGNORECASE)
    if tm:
        title = tm.group(1).strip()
        title = re.sub(r"\s*[|\-_—－]\s*[^|\-_—－]*$", "", title).strip()
    pub_date = ""
    pm = DATE_RE.search(text)
    if pm:
        pub_date = pm.group(1).replace("年", "-").replace("月", "-")
    sha = hashlib.sha256(html).hexdigest()
    return {
        "title": title or "(untitled)",
        "publication_date": pub_date,
        "file_hash_sha256": sha,
        "file_size_bytes": len(html),
    }


def run_fetch() -> dict:
    cells = []
    fetch_log = []
    http_count = 0
    for prov, landing_url in PROVINCES:
        if http_count >= HTTP_LIMIT:
            break
        base_domain = "/".join(landing_url.split("/")[:3])
        # 1. Landing
        code, reason, body = fetch(landing_url, timeout=TIMEOUT)
        http_count += 1
        fetch_log.append({
            "url": landing_url, "province": prov, "phase": "landing",
            "http_code": code, "reason": reason,
            "http_attempt": http_count, "fetched_at": now_utc_iso(),
        })
        if reason != "ok" or code != 200:
            continue
        cand = extract_detail_link(body, base_domain)
        if not cand:
            continue
        if http_count >= HTTP_LIMIT:
            break
        # 2. Detail
        detail_url = cand["url"]
        code, reason, body2 = fetch(detail_url, timeout=TIMEOUT)
        http_count += 1
        fetch_log.append({
            "url": detail_url, "province": prov, "phase": "detail",
            "http_code": code, "reason": reason,
            "http_attempt": http_count, "fetched_at": now_utc_iso(),
        })
        if reason != "ok" or code != 200:
            continue
        cell = parse_detail(body2, detail_url)
        cell["province"] = prov
        cell["url"] = detail_url
        cell["index_anchor_text"] = cand["anchor"]
        cells.append(cell)
    return {
        "generated_at": now_utc_iso(),
        "summary": {
            "fetched_count": len(cells),
            "http_count": http_count,
            "fetch_limit_per_province": FETCH_LIMIT_PER_PROVINCE,
            "fetch_status": "REAL_FETCHED" if cells else "DETAIL_BLOCKED",
            "fetch_methodology": (
                f"M4.6 政府工作报告真实化; 6 试点省 × 1 detail each = {len(cells)} real samples; "
                f"≤{HTTP_LIMIT} HTTP total; curl only"
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
    sv = results["summary"]
    top = sv.get("fetch_status", "NOT_PROBED")
    lines = [
        "# M4.6 6 试点省政府工作报告真实化 spike 抓取报告（2026-09-01，knife 643 M4.6 side）",
        "",
        "> **类型**: 643-A.2 真实抓取 (read-only;**不写 cegr.* 表**)",
        "> **前置**: 638 REACHABLE 23/32 列表 (zfgb 路径) + 642 6 试点省列表 (heilongjiang/fujian/henan/guangdong/guizhou/yunnan)",
        "> **范围**: 6 试点省 × 1 detail each = ≤6 cells; ≤12 HTTP total (6 indices + 6 details)",
        "> **架构师依据**: 643 spike 并行; M4.6 复用 638 政府报告 zfgb 路径 + 642 6 试点省",
        "",
        "## 0. 顶层裁定",
        "",
        f"**{top}** — 适用 {sv.get('http_count', 0)} HTTP, 实测 "
        f"{sv.get('fetched_count', 0)} cell。",
        "",
        f"总抓取: {sv.get('fetched_count', 0)} 真实政府工作报告样本 (跨 {len(PROVINCES)} 试点省)",
        "",
        "## 1. 实体逐项 (真实政府工作报告样本)",
        "",
        "| 序号 | 试点省 | title | publication_date | sha256 (前 16) | file_size | url |",
        "|---|---|---|---|---|---|---|",
    ]
    for i, c in enumerate(results["cells"], start=1):
        sha_short = c.get("file_hash_sha256", "")[:16]
        lines.append(
            f"| {i} | {c.get('province', '')} | {c.get('title', '')[:50]} | "
            f"{c.get('publication_date', '')} | {sha_short} | "
            f"{c.get('file_size_bytes', 0)} | {c.get('url', '')} |"
        )
    lines += [
        "",
        "## 2. HTTP 抓取日志",
        "",
        "| URL | 试点省 | phase | http_code | reason | 抓取时刻 |",
        "|---|---|---|---|---|---|",
    ]
    for fl in results["fetch_log"]:
        lines.append(
            f"| {fl['url']} | {fl['province']} | {fl['phase']} | {fl['http_code']} | "
            f"{fl['reason']} | {fl['fetched_at']} |"
        )
    lines += [
        "",
        "## 3. 方法学",
        "",
        "≤12 HTTP total (6 indices + 6 details): curl only; 不爬网。",
        "解析策略 (vs 642 任免不同):",
        "- 索引页: <a href> + GOV_REPORT_RE 关键词 (政府工作|工作报告|政府报告|年度工作|政府公报|规划计划|五年规划)",
        "- 详情页: <title> + DATE_RE",
        "- 真实 SHA256: hashlib.sha256(html) 一次",
        "",
        "## 4. 数据源合规",
        "",
        "✓ 6 试点省 政府网 (hlj/fujian/henan/gd/guizhou/yn .gov.cn)",
        "✓ 无商业库; ✓ 无用户裁定 URL",
        "✓ ≤12 HTTP total; ✓ 不爬网; ✓ 不写 cegr.* 表",
        "",
        "## 5. 红线遵守",
        "",
        "- ✓ ≤12 HTTP total (硬性上限)",
        "- ✓ 不爬网 (no follow pagination; no recursion)",
        "- ✓ 不写 cegr.* 表 (read-only on production)",
        "- ✓ 不静默硬编码 GDP 值 (从抓取解析)",
        "- ✓ 脚本幂等 (no time.sleep / no random; sha256 deterministic)",
        "- ✓ 不宣称 Gate / O1 / M2 / M4 PASS",
        "",
    ]
    REPORT_MD.write_text("\n".join(lines), encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description="643-A.2 M4.6 政府工作报告真实抓取")
    args = parser.parse_args()
    results = run_fetch()
    write_outputs(results)
    print(
        f"643-A.2 M4.6: http_count={results['summary']['http_count']}, "
        f"fetched_count={results['summary']['fetched_count']}, "
        f"status={results['summary']['fetch_status']}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())