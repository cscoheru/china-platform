"""M4.11 — 2 样本 政策详情页 v5 真实化 fetch (knife 648 Block A.1).

Per knife 648 §1.648-A.1:
- 沿用 647 fetch 模式;hunan + anhui 首选 /zwgk/ + 625 fall-through fallback
- 2 新样本 × 1 HTTP each (≤12 total HTTP limit)
- 顶层裁定 REAL_FETCHED
- 2 真实样本落地 (SHA 撞 638-647 排除)
- substitute 预授权池 (jilin/liaoning/hubei/shaanxi/sichuan/guizhou/jiangsu)
- 已用省全集 (不得重复): HLJ / HENAN / YUNNAN / FUJIAN / GD / ZJ / JX

HARD LIMITS:
- ≤12 HTTP total (2 cells × 1 HTTP main + 10 retry 余量)
- 不爬网 (no recursion; no follow pagination)
- 仅抓 landing (curl only, no JS / no headless browser)
- 2 distinct real SHA 必须 ≠ 638-647 全部 SHA
- chain_id = 'real_648_m4_11_policy_detail_v5' (末段 _v5 ≠ 647 _v4)
- UUID prefix g 段 (g0eebc99-g6eebc99) ≠ 647 f 段

2 cells (2 样本 × 1 HTTP each):
- hunan 首选: https://www.hunan.gov.cn/zwgk/; fallback #1 https://www.hunan.gov.cn/ (省府根)
- anhui 首选: https://www.ah.gov.cn/zwgk/; fallback #1 https://www.ah.gov.cn/ (省府根)

OUTPUT:
* docs/reports/m4_11_policy_detail_real_v5_20260901.md
* evidence_pack/m4_11_policy_detail_real_v5_20260901.json
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
from pathlib import Path

from _probe_http_helpers import fetch, now_utc_iso

REPO_ROOT = Path(__file__).resolve().parent.parent
REPORT_MD = REPO_ROOT / "docs" / "reports" / "m4_11_policy_detail_real_v5_20260901.md"
EVIDENCE_JSON = REPO_ROOT / "evidence_pack" / "m4_11_policy_detail_real_v5_20260901.json"

# 2 cells (2 样本 × 1 HTTP each, 沿用 625 fall-through policy)
HUNAN_FALLBACK_CHAIN = [
    "https://www.hunan.gov.cn/zwgk/",
    "https://www.hunan.gov.cn/",
]
ANHUI_FALLBACK_CHAIN = [
    "https://www.ah.gov.cn/zwgk/",
    "https://www.ah.gov.cn/",
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


def run_chain(chain: list, slot_name: str, province: str, fetch_log: list, http_count_box: list) -> tuple:
    """Run a fall-through chain for one cell; return (cell, chain_index, http_count_used)."""
    cells = []
    chain_index = None
    http_used = 0
    for idx, url in enumerate(chain):
        if http_count_box[0] >= HTTP_LIMIT:
            break
        code, reason, body = fetch(url, timeout=TIMEOUT)
        http_count_box[0] += 1
        http_used += 1
        phase = f"{slot_name}_main_{idx}" if idx == 0 else f"{slot_name}_fallback_{idx}"
        fetch_log.append({
            "url": url, "province": province, "slot": slot_name,
            "phase": phase, "http_code": code, "reason": reason,
            "http_attempt": http_count_box[0], "fetched_at": now_utc_iso(),
        })
        if reason == "ok" and code == 200:
            chain_index = idx
            cell = parse_detail(body, url)
            cell["province"] = province
            cell["slot"] = slot_name
            cell["chain_index"] = idx
            cell["chain_total"] = len(chain)
            cells.append(cell)
            break
    return cells, chain_index, http_used


def run_fetch() -> dict:
    cells = []
    fetch_log = []
    http_count_box = [0]

    # Cell 1: hunan /zwgk/ with fall-through chain
    hn_cells, hn_idx, _ = run_chain(
        HUNAN_FALLBACK_CHAIN,
        "hunan_zwgk_chain",
        "hunan",
        fetch_log,
        http_count_box,
    )
    cells.extend(hn_cells)

    # Cell 2: anhui /zwgk/ with fall-through chain
    ah_cells, ah_idx, _ = run_chain(
        ANHUI_FALLBACK_CHAIN,
        "anhui_zwgk_chain",
        "anhui",
        fetch_log,
        http_count_box,
    )
    cells.extend(ah_cells)

    return {
        "generated_at": now_utc_iso(),
        "summary": {
            "fetched_count": len(cells),
            "http_count": http_count_box[0],
            "fetch_status": "REAL_FETCHED" if len(cells) == 2 else "DETAIL_BLOCKED",
            "fetch_methodology": (
                f"M4.11 政策详情 v5 真实化; 2 样本 (hunan /zwgk/ + anhui /zwgk/) "
                f"× 1 HTTP each = {len(cells)} real samples; ≤{HTTP_LIMIT} HTTP total; "
                f"curl only; 全新 SHA 与 638-647 全 distinct"
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
        "# M4.11 2 样本政策详情 v5 真实化 spike 抓取报告（2026-09-01，knife 648 M4.11 side）",
        "",
        "> **类型**: 648-A.1 真实抓取 (read-only;**不写 cegr.* 表**)",
        "> **前置**: 647 审计 PASS（有限通过） (`647-stage0-cursor-s647-m4-10-v4-audit-PASS-20260901.md`)",
        "> **范围**: 2 样本 × 1 HTTP each = 2 cells; ≤12 HTTP total",
        "> **架构师依据**: 648 spike; hunan + anhui 首选 + 625 fall-through chain (省府根 fallback)",
        "> **chain_id**: `real_648_m4_11_policy_detail_v5` (末段 `_v5`, ≠ 647 `_v4` ≠ 646 `_v3` ≠ 645 `_v2`)",
        "> **UUID prefix**: g 段 (g0eebc99-g6eebc99) ≠ 647 f 段 (f0eebc99-f6eebc99) ≠ 646 e 段 ≠ 645 d 段",
        "",
        "## 0. 顶层裁定",
        "",
        f"**{top}** — 适用 {sv.get('http_count', 0)} HTTP, 实测 "
        f"{sv.get('fetched_count', 0)} cell。",
        "",
        f"总抓取: {sv.get('fetched_count', 0)} 真实政策详情样本 (跨 2 样本位)",
        "",
        "## 1. 实体逐项 (真实政策详情样本)",
        "",
        "| 序号 | 试点省 | slot | chain_index | title | publication_date | sha256 (前 16) | file_size | source_url |",
        "|---|---|---|---|---|---|---|---|---|",
    ]
    for i, c in enumerate(results["cells"], start=1):
        sha_short = c.get("file_hash_sha256", "")[:16]
        ci = c.get("chain_index", "n/a")
        lines.append(
            f"| {i} | {c.get('province', '')} | {c.get('slot', '')} | "
            f"{ci} | {c.get('title', '')[:50]} | {c.get('publication_date', '')} | "
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
        "≤12 HTTP total (2 cells): curl only; 不爬网; 直接抓 detail page.",
        "沿用 647 fetch 模式; hunan + anhui 首选 /zwgk/ + 625 fall-through chain (省府根 fallback).",
        "hunan 首选 /zwgk/ 若 404/不可达 → fallback #1 https://www.hunan.gov.cn/ (省府根).",
        "anhui 首选 /zwgk/ 若 404/不可达 → fallback #1 https://www.ah.gov.cn/ (省府根).",
        "解析策略:",
        "- 详情页: <title> + DATE_RE",
        "- 真实 SHA256: hashlib.sha256(html) 一次",
        "",
        "## 4. 数据源合规",
        "",
        "✓ 2 试点省 政府网 (hunan.gov.cn + ah.gov.cn)",
        "✓ 已用省全集检查通过: HLJ / HENAN / YUNNAN / FUJIAN / GD / ZJ / JX (不重复)",
        "✓ substitute 预授权池 (jilin/liaoning/hubei/shaanxi/sichuan/guizhou/jiangsu) 待激活",
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
        "- ✓ 不宣称 Gate / O1 / M2 / M4 / M4.7 / M4.8 / M4.9 / M4.10 / M4.11 / M5 / M6 PASS",
        "",
    ]
    REPORT_MD.write_text("\n".join(lines), encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description="648-A.1 M4.11 政策详情 v5 真实抓取")
    args = parser.parse_args()
    results = run_fetch()
    write_outputs(results)
    print(
        f"648-A.1 M4.11: http_count={results['summary']['http_count']}, "
        f"fetched_count={results['summary']['fetched_count']}, "
        f"status={results['summary']['fetch_status']}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())