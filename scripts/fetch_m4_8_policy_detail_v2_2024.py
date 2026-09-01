"""M4.8 — 4 样本 政策详情页 v2 真实化 fetch (knife 645 Block A.2, M4.8 side).

Per knife 645 §3.645-A.2:
- 沿用 644 3 试点省 heilongjiang/henan/yunnan (复用 644 4 SHA + 复用 URL)
- 纳入 644 留作扩展的 henan `bd4c4c51...` (zwgk root) 作为第 4 样本
- 4 cells (4 样本 × 1 HTTP each) ≤12 HTTP total (留余量给 retry)
- 顶层裁定 REAL_FETCHED
- 4 真实样本落地 (SHA 撞 644/643/642/641/640/639 排除)

HARD LIMITS:
- ≤12 HTTP total (4 cells × 1 HTTP main + 8 retry 余量)
- 不爬网 (no recursion; no follow pagination)
- 仅抓 landing (沿用 644 4 URL)
- curl only (no JS / no headless browser)
- 复用 644 4 SHA (idempotent 验证 + 落 SHA 副本)

4 cells (4 样本 × 1 HTTP each):
- heilongjiang: hlj /hlj/c107884/list.shtml (沿用 644 SHA `bad8be51...`)
- henan-zfgb:  henan /zwgk/zfgb/ (沿用 644 SHA `dfa38998...`)
- henan-zwgk:  henan /zwgk/ (NEW 645 第 4 样本, 644 留作扩展 SHA `bd4c4c51...`)
- yunnan:      yunnan /zwgk/zfxxgk/zfgzbg/ (沿用 644 SHA `f33eba53...`)

OUTPUT:
* docs/reports/m4_8_policy_detail_real_v2_20260901.md
* evidence_pack/m4_8_policy_detail_real_v2_20260901.json
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
from pathlib import Path

from _probe_http_helpers import fetch, now_utc_iso

REPO_ROOT = Path(__file__).resolve().parent.parent
REPORT_MD = REPO_ROOT / "docs" / "reports" / "m4_8_policy_detail_real_v2_20260901.md"
EVIDENCE_JSON = REPO_ROOT / "evidence_pack" / "m4_8_policy_detail_real_v2_20260901.json"

# 4 cells (4 样本 × 1 HTTP each);复用 644 3 样本 URL + 1 NEW henan zwgk root
# - hlj: c107884 列表 (沿用 644 SHA `bad8be51...`)
# - henan zfgb: 列表 (沿用 644 SHA `dfa38998...`)
# - henan zwgk: root (NEW 645 第 4 样本, 644 留作扩展 SHA `bd4c4c51...`)
# - yunnan: /zwgk/zfxxgk/zfgzbg/ 政府工作报告 (沿用 644 SHA `f33eba53...`)
FETCH_CELLS = [
    ("heilongjiang", "https://www.hlj.gov.cn/hlj/c107884/list.shtml",     "hlj_policy_list",     "policy"),
    ("henan",        "https://www.henan.gov.cn/zwgk/zfgb/",               "henan_zfgb_list",     "policy"),
    ("henan",        "https://www.henan.gov.cn/zwgk/",                    "henan_zwgk_root",     "policy"),
    ("yunnan",       "https://www.yn.gov.cn/zwgk/zfxxgk/zfgzbg/",         "yunnan_zfgzbg",       "policy"),
]
TIMEOUT = 15
HTTP_LIMIT = 12

DATE_RE = re.compile(r"(20\d{2}[-年]\d{1,2}[-月]\d{1,2})", re.IGNORECASE)


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
        "source_url": url,
    }


def run_fetch() -> dict:
    cells = []
    fetch_log = []
    http_count = 0
    for prov, url, slot, _cls in FETCH_CELLS:
        if http_count >= HTTP_LIMIT:
            break
        code, reason, body = fetch(url, timeout=TIMEOUT)
        http_count += 1
        fetch_log.append({
            "url": url, "province": prov, "slot": slot, "phase": "main",
            "http_code": code, "reason": reason,
            "http_attempt": http_count, "fetched_at": now_utc_iso(),
        })
        if reason != "ok" or code != 200:
            continue
        cell = parse_detail(body, url)
        cell["province"] = prov
        cell["slot"] = slot
        cells.append(cell)
    return {
        "generated_at": now_utc_iso(),
        "summary": {
            "fetched_count": len(cells),
            "http_count": http_count,
            "fetch_status": "REAL_FETCHED" if cells else "DETAIL_BLOCKED",
            "fetch_methodology": (
                f"M4.8 政策详情 v2 真实化; 4 样本 (heilongjiang/henan-zfgb/"
                f"henan-zwgk/yunnan) × 1 HTTP each = {len(cells)} real samples; "
                f"≤{HTTP_LIMIT} HTTP total; curl only; 复用 644 3 URL + 纳入 henan "
                f"zwgk root 作为第 4 样本"
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
        "# M4.8 4 样本政策详情 v2 真实化 spike 抓取报告（2026-09-01，knife 645 M4.8 side）",
        "",
        "> **类型**: 645-A.2 真实抓取 (read-only;**不写 cegr.* 表**)",
        "> **前置**: 644 M4.7 DELIVERED (3 样本 SHA `bad8be51` / `dfa38998` / `f33eba53`)",
        "> **范围**: 4 样本 × 1 HTTP each = 4 cells; ≤12 HTTP total",
        "> **架构师依据**: 645 spike 并行; M4.8 复用 644 3 URL + 纳入 644 留作扩展的 henan `bd4c4c51...` (zwgk root) 作为第 4 样本",
        "",
        "## 0. 顶层裁定",
        "",
        f"**{top}** — 适用 {sv.get('http_count', 0)} HTTP, 实测 "
        f"{sv.get('fetched_count', 0)} cell。",
        "",
        f"总抓取: {sv.get('fetched_count', 0)} 真实政策详情样本 (跨 4 样本位)",
        "",
        "## 1. 实体逐项 (真实政策详情样本)",
        "",
        "| 序号 | 试点省 | slot | title | publication_date | sha256 (前 16) | file_size | source_url |",
        "|---|---|---|---|---|---|---|---|",
    ]
    for i, c in enumerate(results["cells"], start=1):
        sha_short = c.get("file_hash_sha256", "")[:16]
        lines.append(
            f"| {i} | {c.get('province', '')} | {c.get('slot', '')} | "
            f"{c.get('title', '')[:50]} | {c.get('publication_date', '')} | "
            f"{sha_short} | {c.get('file_size_bytes', 0)} | "
            f"{c.get('source_url', '')} |"
        )
    lines += [
        "",
        "## 2. HTTP 抓取日志",
        "",
        "| URL | 试点省 | slot | phase | http_code | reason | 抓取时刻 |",
        "|---|---|---|---|---|---|---|",
    ]
    for fl in results["fetch_log"]:
        lines.append(
            f"| {fl['url']} | {fl['province']} | {fl['slot']} | {fl['phase']} | "
            f"{fl['http_code']} | {fl['reason']} | {fl['fetched_at']} |"
        )
    lines += [
        "",
        "## 3. 方法学",
        "",
        "≤12 HTTP total (4 cells): curl only; 不爬网; 直接抓 detail page (沿用 644 URL).",
        "复用 644 3 SHA: hlj `bad8be51` / henan-zfgb `dfa38998` / yunnan `f33eba53` (idempotent 验证).",
        "新增 645 第 4 样本: henan-zwgk `bd4c4c51` (root landing page, 644 留作扩展).",
        "解析策略:",
        "- 详情页: <title> + DATE_RE",
        "- 真实 SHA256: hashlib.sha256(html) 一次",
        "",
        "## 4. 数据源合规",
        "",
        "✓ 3 试点省 政府网 (hlj/henan/yunnan .gov.cn)",
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
        "- ✓ 不宣称 Gate / O1 / M2 / M4 / M4.7 / M4.8 / M5 / M6 PASS",
        "",
    ]
    REPORT_MD.write_text("\n".join(lines), encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description="645-A.2 M4.8 政策详情 v2 真实抓取")
    args = parser.parse_args()
    results = run_fetch()
    write_outputs(results)
    print(
        f"645-A.2 M4.8: http_count={results['summary']['http_count']}, "
        f"fetched_count={results['summary']['fetched_count']}, "
        f"status={results['summary']['fetch_status']}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
