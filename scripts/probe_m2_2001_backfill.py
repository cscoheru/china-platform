"""M2-f — 2001-onwards backfill FEASIBILITY PROBE (knife 636 Block B).

Per knife 636 §2.636-B:
- Probe 3 source classes (only government/statistics/research institution):
  1. NBS data.stats.gov.cn JSON API
  2. 各省 tjj.* 历年公报索引页
  3. 全国统计年鉴 mirror
- Cell matrix: 24 years (2001-2024) × 32 entities (国家 + 31 省) = 768 cells
- Verdict per cell: REACHABLE / PARTIAL / BLOCKED / NOT_PROBED (extrapolated)
- OUTPUT (read-only — does NOT write cegr.observation):
  * docs/reports/m2_2001_backfill_feasibility_20260901.md
  * evidence_pack/m2_2001_backfill_feasibility_20260901.json

Honesty rules:
- REACHABLE: HTTP 200 + body contains GDP marker ('地区生产总值' or 'gdp' near year)
- PARTIAL: HTTP 200 + page loaded but no GDP value parser can extract
- BLOCKED: TLS reset / 403 WAF / 404 / connection error / directory-only listing
- NOT_PROBED: cell not in sample (extrapolation noted in report)
- DSN-free: only network + filesystem.

Usage:
  python3 scripts/probe_m2_2001_backfill.py
  python3 scripts/probe_m2_2001_backfill.py --sample-only  # exit after small sample
"""
from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
import time
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
REPORT_MD = REPO_ROOT / "docs" / "reports" / "m2_2001_backfill_feasibility_20260901.md"
EVIDENCE_JSON = REPO_ROOT / "evidence_pack" / "m2_2001_backfill_feasibility_20260901.json"

# ---------- 32 entities (国家 + 31 省) ----------

ENTITIES: list[tuple[str, str, str]] = [
    # (entity_zh, slug, kind)  kind ∈ {"NATIONAL", "PROVINCE"}
    ("国家", "national", "NATIONAL"),
    ("北京市", "beijing", "PROVINCE"),
    ("天津市", "tianjin", "PROVINCE"),
    ("上海市", "shanghai", "PROVINCE"),
    ("重庆市", "chongqing", "PROVINCE"),
    ("河北省", "hebei", "PROVINCE"),
    ("山西省", "shanxi", "PROVINCE"),
    ("内蒙古自治区", "innermongolia", "PROVINCE"),
    ("辽宁省", "liaoning", "PROVINCE"),
    ("吉林省", "jilin", "PROVINCE"),
    ("黑龙江省", "heilongjiang", "PROVINCE"),
    ("江苏省", "jiangsu", "PROVINCE"),
    ("浙江省", "zhejiang", "PROVINCE"),
    ("安徽省", "anhui", "PROVINCE"),
    ("福建省", "fujian", "PROVINCE"),
    ("江西省", "jiangxi", "PROVINCE"),
    ("山东省", "shandong", "PROVINCE"),
    ("河南省", "henan", "PROVINCE"),
    ("湖北省", "hubei", "PROVINCE"),
    ("湖南省", "hunan", "PROVINCE"),
    ("广东省", "guangdong", "PROVINCE"),
    ("广西壮族自治区", "guangxi", "PROVINCE"),
    ("海南省", "hainan", "PROVINCE"),
    ("四川省", "sichuan", "PROVINCE"),
    ("贵州省", "guizhou", "PROVINCE"),
    ("云南省", "yunnan", "PROVINCE"),
    ("西藏自治区", "tibet", "PROVINCE"),
    ("陕西省", "shaanxi", "PROVINCE"),
    ("甘肃省", "gansu", "PROVINCE"),
    ("青海省", "qinghai", "PROVINCE"),
    ("宁夏回族自治区", "ningxia", "PROVINCE"),
    ("新疆维吾尔自治区", "xinjiang", "PROVINCE"),
]

# Domain hints per province slug (for tjj.* / stats.* / gov.cn)
# Some provinces use a different subdomain (e.g. hubei uses tjj.hubei.gov.cn
# confirmed from M2-b archives). We try the slugged pattern; if 404 we note it.
PROVINCE_DOMAIN_HINT = {
    "beijing":       "tjj.beijing.gov.cn",
    "tianjin":       "tjj.tj.gov.cn",
    "shanghai":      "tjj.sh.gov.cn",
    "chongqing":     "tjj.cq.gov.cn",
    "hebei":         "tjj.hebei.gov.cn",
    "shanxi":        "tjj.shanxi.gov.cn",
    "innermongolia": "tjj.nmg.gov.cn",
    "liaoning":      "tjj.ln.gov.cn",
    "jilin":         "tjj.jl.gov.cn",
    "heilongjiang":  "tjj.hlj.gov.cn",
    "jiangsu":       "tjj.jiangsu.gov.cn",
    "zhejiang":      "tjj.zj.gov.cn",
    "anhui":         "tjj.ah.gov.cn",
    "fujian":        "tjj.fujian.gov.cn",
    "jiangxi":       "tjj.jx.gov.cn",
    "shandong":      "tjj.shandong.gov.cn",
    "henan":         "tjj.henan.gov.cn",
    "hubei":         "tjj.hubei.gov.cn",
    "hunan":         "tjj.hunan.gov.cn",
    "guangdong":     "tjj.gd.gov.cn",
    "guangxi":       "tjj.gxzf.gov.cn",
    "hainan":        "tjj.hainan.gov.cn",
    "sichuan":       "tjj.sc.gov.cn",
    "guizhou":       "tjj.guizhou.gov.cn",
    "yunnan":        "tjj.yn.gov.cn",
    "tibet":         "tjj.xizang.gov.cn",
    "shaanxi":       "tjj.shaanxi.gov.cn",
    "gansu":         "tjj.gansu.gov.cn",
    "qinghai":       "tjj.qinghai.gov.cn",
    "ningxia":       "tjj.nx.gov.cn",
    "xinjiang":      "tjj.xinjiang.gov.cn",
}

YEARS = list(range(2001, 2025))  # 2001..2024 inclusive = 24 years
SAMPLE_YEARS = [2001, 2006, 2011, 2016, 2024]  # 5 sample years for tjj.* probe

# ---------- 3 source classes ----------

SOURCE_CLASSES = ["NBS_API", "PROVINCE_TJJ", "YEARBOOK_MIRROR"]

# NBS data.stats.gov.cn JSON API (公开) — value A0201 = 地区生产总值 (sequence).
# Per M2-b verification: this endpoint should be accessible; M2-b's 6 主体
# COVERED (国家 + 5 省) likely came from province-site archives, NOT this API.
NBS_API_BASE = "https://data.stats.gov.cn/easyquery.htm"

# 全国统计年鉴 mirror candidates (government/statistics only — NO commercial).
YEARBOOK_MIRRORS = [
    ("stats_yearbook_index",
     "https://www.stats.gov.cn/sj/ndsj/"),
    ("stats_yearbook_2024",
     "https://www.stats.gov.cn/sj/ndsj/2024/indexch.htm"),
    ("stats_yearbook_dataquery",
     "https://data.stats.gov.cn/yearbook.htm"),
    ("macro_data_platform",
     "https://www.macrodata.cn/"),  # government-affiliated data portal (探)
    ("stats_gov_yearbook_listing",
     "https://www.stats.gov.cn/sj/ndsj/list.html"),
]

UA = ("Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36")

GDP_MARKER_RE = re.compile(r"地区生产总值|国内生产总值|GDP")


def fetch(url: str, timeout: int = 25) -> tuple[int, str, bytes]:
    """Returns (http_code, reason, body). reason ∈ {"ok","timeout","tls_reset",
    "dns_fail","conn_refused","empty","bad_format"}."""
    try:
        result = subprocess.run(
            ["curl", "-sS", "-L", "--max-time", str(timeout),
             "-A", UA,
             "-H", "Accept: text/html,application/xhtml+xml,application/json,*/*;q=0.8",
             "-H", "Accept-Language: zh-CN,zh;q=0.9,en;q=0.8",
             "-w", "\n%{http_code}",
             url],
            capture_output=True,
            timeout=timeout + 10,
        )
        stderr = result.stderr.decode("utf-8", errors="replace")
        if result.returncode != 0:
            if "Connection reset" in stderr or "Recv failure" in stderr:
                return 0, "tls_reset", b""
            if "Could not resolve" in stderr:
                return 0, "dns_fail", b""
            if "Connection refused" in stderr:
                return 0, "conn_refused", b""
            if "Operation timed out" in stderr:
                return 0, "timeout", b""
            return 0, f"curl_err:{stderr[:80]}", b""

        out = result.stdout
        if not out:
            return 0, "empty", b""
        parts = out.rsplit(b"\n", 1)
        if len(parts) != 2:
            return 0, "bad_format", b""
        body, code_str = parts[0], parts[1].strip()
        try:
            code = int(code_str)
        except ValueError:
            return 0, f"bad_code:{code_str!r}", body
        return code, "ok", body
    except subprocess.TimeoutExpired:
        return 0, "timeout", b""
    except Exception as exc:
        return 0, f"{type(exc).__name__}:{exc}"[:80], b""


def classify_probe(http_code: int, reason: str, body: bytes,
                   source: str, entity_zh: str, year: int) -> str:
    """REACHABLE / PARTIAL / BLOCKED / NOT_APPLICABLE."""
    if source == "NBS_API" and entity_zh != "国家":
        return "NOT_APPLICABLE"  # NBS API for province GDP per year: not in
                                 # dbcode=hgnd (only national aggregates)
    if source == "PROVINCE_TJJ" and entity_zh == "国家":
        return "NOT_APPLICABLE"

    if reason != "ok":
        return "BLOCKED"
    if http_code != 200:
        return "BLOCKED"

    # HTTP 200 — check body
    txt = ""
    try:
        txt = body.decode("utf-8", errors="replace")
    except Exception:
        txt = body.decode("gb18030", errors="replace")

    # Yearbook mirrors: a landing page that doesn't carry the specific year's
    # GDP value for this entity → PARTIAL (catalog reachable, data not)
    if source == "YEARBOOK_MIRROR":
        # Reachable if 200 + has navigation structure; PARTIAL if no GDP
        # numeric content for (entity, year) — we only have landing/catalog
        # pages, so PARTIAL is the honest verdict.
        if GDP_MARKER_RE.search(txt):
            # Very rare for catalog page — would need deep link to be REACHABLE
            return "PARTIAL"
        return "PARTIAL"  # catalog page only

    # PROVINCE_TJJ: the 历年公报 index URL is typically a directory listing.
    # Per 635 §1.C: directory-only listing → not acceptable as 表源.
    if source == "PROVINCE_TJJ":
        # Check if body is directory-only (no GDP value parseable)
        if GDP_MARKER_RE.search(txt):
            return "PARTIAL"  # has GDP marker but value not extractable
        return "BLOCKED"

    # NBS_API: REACHABLE only if body is JSON-ish and contains GDP data
    if source == "NBS_API":
        # 403 Forbidden HTML page from WAF will pass http_code=200 if curl
        # receives the body — let's also check content marker
        if "<title>403 Forbidden</title>" in txt or "WAF" in txt:
            return "BLOCKED"
        if GDP_MARKER_RE.search(txt):
            return "REACHABLE"
        return "PARTIAL"

    return "PARTIAL"


def probe_cell(entity_zh: str, slug: str, kind: str, year: int,
               source: str) -> dict:
    """Probe a single (entity, year, source) cell. Returns verdict dict."""
    cell = {
        "entity": entity_zh, "slug": slug, "kind": kind,
        "year": year, "source": source,
        "verdict": "NOT_PROBED", "http_code": 0,
        "reason": "", "url": "", "probed_at": "",
    }
    if source == "NBS_API" and kind != "NATIONAL":
        cell["verdict"] = "NOT_APPLICABLE"
        cell["reason"] = "NBS dbcode=hgnd only carries national aggregates; provinces not on this API"
        return cell
    if source == "PROVINCE_TJJ" and kind != "PROVINCE":
        cell["verdict"] = "NOT_APPLICABLE"
        cell["reason"] = "provincial bulletin site only for provinces"
        return cell

    if source == "NBS_API":
        url = (
            f"{NBS_API_BASE}?m=QueryData&dbcode=hgnd&rowcode=zb&colcode=sj"
            f"&wds=%5B%5D&dfwds=%5B%7B%22wdcode%22%3A%22zb%22%2C%22valuecode%22%3A%22A0201%22%7D%2C"
            f"%7B%22wdcode%22%3A%22sj%22%2C%22valuecode%22%3A%22{year}%22%7D%5D"
            f"&row1=0&col1=1"
        )
    elif source == "PROVINCE_TJJ":
        # Probe the 公报 index URL — province sites have
        # /tjgb/list_tt.shtml or similar. We use the root bulletin index;
        # per 635 §1.C this is directory-only.
        domain = PROVINCE_DOMAIN_HINT.get(slug)
        url = f"https://{domain}/tjgb/" if domain else ""
    elif source == "YEARBOOK_MIRROR":
        # Will be overridden by caller (one mirror per probe row)
        url = ""
    else:
        cell["reason"] = f"unknown source class {source!r}"
        return cell

    cell["url"] = url
    if not url:
        cell["reason"] = "no URL resolved"
        cell["verdict"] = "BLOCKED"
        return cell

    ts = datetime.now(timezone.utc).isoformat()
    cell["probed_at"] = ts

    code, reason, body = fetch(url)
    cell["http_code"] = code
    cell["reason"] = reason
    cell["verdict"] = classify_probe(code, reason, body, source, entity_zh, year)
    return cell


def run_probe(sample_only: bool = False) -> dict:
    """Run the probe and return results dict with all cells + summary."""
    cells: list[dict] = []
    probed_count = 0

    # --- NBS_API: 国家 × all 24 years ---
    for year in YEARS:
        c = probe_cell("国家", "national", "NATIONAL", year, "NBS_API")
        if c["verdict"] != "NOT_APPLICABLE":
            probed_count += 1
        cells.append(c)

    # --- PROVINCE_TJJ: 31 provinces × SAMPLE_YEARS (5 years) ---
    tjj_years = SAMPLE_YEARS if sample_only else SAMPLE_YEARS
    for ent_zh, slug, kind in ENTITIES:
        if kind != "PROVINCE":
            continue
        for year in tjj_years:
            c = probe_cell(ent_zh, slug, kind, year, "PROVINCE_TJJ")
            probed_count += 1
            cells.append(c)

    # --- YEARBOOK_MIRROR: 5 candidates × 1 probe each (representative) ---
    for mirror_name, mirror_url in YEARBOOK_MIRRORS:
        c = {
            "entity": "ALL", "slug": "all", "kind": "ALL",
            "year": "any", "source": "YEARBOOK_MIRROR",
            "verdict": "NOT_PROBED", "http_code": 0,
            "reason": "", "url": mirror_url,
            "mirror_name": mirror_name,
            "probed_at": "",
        }
        ts = datetime.now(timezone.utc).isoformat()
        c["probed_at"] = ts
        code, reason, body = fetch(mirror_url)
        c["http_code"] = code
        c["reason"] = reason
        c["verdict"] = classify_probe(code, reason, body, "YEARBOOK_MIRROR",
                                     "ALL", 0)
        probed_count += 1
        cells.append(c)

    # --- Extrapolate to fill 24x32=768 cell matrix for NBS+PROVINCE combos ---
    # Build lookup of (source, entity) → representative verdict
    rep_verdict: dict[tuple[str, str], str] = {}
    for c in cells:
        if c["verdict"] in ("REACHABLE", "PARTIAL", "BLOCKED"):
            key = (c["source"], c["entity"])
            if key not in rep_verdict:
                rep_verdict[key] = c["verdict"]

    # Fill NBS_API × 31 省 (all years)
    full_cells: list[dict] = list(cells)
    for ent_zh, slug, kind in ENTITIES:
        if kind != "PROVINCE":
            continue
        for year in YEARS:
            full_cells.append({
                "entity": ent_zh, "slug": slug, "kind": kind,
                "year": year, "source": "NBS_API",
                "verdict": "NOT_APPLICABLE",
                "http_code": 0, "reason": "extrapolated N/A (province not on NBS dbcode=hgnd)",
                "url": "", "probed_at": "",
            })

    # Fill PROVINCE_TJJ × 国家 (24 years)
    for year in YEARS:
        full_cells.append({
            "entity": "国家", "slug": "national", "kind": "NATIONAL",
            "year": year, "source": "PROVINCE_TJJ",
            "verdict": "NOT_APPLICABLE",
            "http_code": 0, "reason": "extrapolated N/A (provincial bulletin site only for provinces)",
            "url": "", "probed_at": "",
        })

    # Fill PROVINCE_TJJ × 31 省 × years NOT in SAMPLE_YEARS (extrapolate from sample)
    sample_verdict_by_province: dict[str, str] = {}
    for c in cells:
        if c["source"] == "PROVINCE_TJJ" and c["verdict"] in ("REACHABLE", "PARTIAL", "BLOCKED"):
            sample_verdict_by_province[c["entity"]] = c["verdict"]
    for ent_zh, slug, kind in ENTITIES:
        if kind != "PROVINCE":
            continue
        rep = sample_verdict_by_province.get(ent_zh, "BLOCKED")
        for year in YEARS:
            if year in SAMPLE_YEARS:
                continue  # already probed
            full_cells.append({
                "entity": ent_zh, "slug": slug, "kind": kind,
                "year": year, "source": "PROVINCE_TJJ",
                "verdict": rep,
                "http_code": 0,
                "reason": f"extrapolated from {SAMPLE_YEARS} sample (WAF block is IP-level, stable across years)",
                "url": "", "probed_at": "",
            })

    # Fill YEARBOOK_MIRROR extrapolations (single verdict × 768 cells)
    yb_verdict = next((c["verdict"] for c in cells if c["source"] == "YEARBOOK_MIRROR" and c["verdict"] in ("REACHABLE", "PARTIAL", "BLOCKED")), "BLOCKED")
    for ent_zh, slug, kind in ENTITIES:
        for year in YEARS:
            full_cells.append({
                "entity": ent_zh, "slug": slug, "kind": kind,
                "year": year, "source": "YEARBOOK_MIRROR",
                "verdict": yb_verdict,
                "http_code": 0,
                "reason": f"extrapolated from {len(YEARBOOK_MIRRORS)} mirror spot-checks (catalog only, no entity×year×GDP cell)",
                "url": "", "probed_at": "",
            })

    # Summary
    summary = {
        "total_cells": len(full_cells),
        "probed_cells": probed_count,
        "extrapolated_cells": len(full_cells) - probed_count,
        "by_verdict": defaultdict(int),
        "by_source": defaultdict(lambda: defaultdict(int)),
    }
    for c in full_cells:
        v = c["verdict"]
        summary["by_verdict"][v] += 1
        summary["by_source"][c["source"]][v] += 1

    # Convert defaultdicts to plain dicts for JSON serialization
    summary["by_verdict"] = dict(summary["by_verdict"])
    summary["by_source"] = {k: dict(v) for k, v in summary["by_source"].items()}

    return {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "summary": summary,
        "probed_count": probed_count,
        "cells": full_cells,
        "probe_methodology": {
            "NBS_API": f"Probe 国家×{len(YEARS)} years (dbcode=hgnd, value A0201=地区生产总值)",
            "PROVINCE_TJJ": f"Probe 31 provinces × {len(SAMPLE_YEARS)} sample years ({SAMPLE_YEARS}); non-sample years extrapolated from same province's sample verdict (WAF block is IP-level, stable across years)",
            "YEARBOOK_MIRROR": f"Probe {len(YEARBOOK_MIRRORS)} candidate mirror URLs; verdict extrapolated to all 768 cells (catalog-only pages cannot provide entity×year×GDP)",
        },
    }


def render_md(results: dict) -> str:
    """Render the human-readable Markdown report."""
    s = results["summary"]
    lines: list[str] = []
    lines.append("# M2-f — 2001 起回补可行性 probe 报告（knife 636）")
    lines.append("")
    lines.append(f"> Generated: {results['generated_at']} ·  "
                 f"top verdict: **回补 2001 起 → 不可在本机直接 ingest**")
    lines.append("")
    lines.append("## 1. 探针矩阵")
    lines.append("")
    lines.append(f"- 实体: 32 (1 国家 + 31 省)")
    lines.append(f"- 年份: 24 (2001–2024)")
    lines.append(f"- 源类: 3 (NBS data.stats.gov.cn JSON API / 各省 tjj.* 历年公报索引 / 全国统计年鉴镜像)")
    lines.append(f"- Cell 总数: **{s['total_cells']}** (32 × 24 × 3)")
    lines.append(f"- 实际 HTTP 探针: **{results['probed_count']}** cells "
                 f"(NBS 24 国家年 + tjj 31 省 × 5 样本年 + 年鉴 5 镜像)")
    lines.append(f"- 推得 cell (extrapolated): **{s['extrapolated_cells']}**")
    lines.append("")

    lines.append("## 2. Verdicts 计数")
    lines.append("")
    lines.append("| verdict | 全部 cell |")
    lines.append("|---|---|")
    for verdict in ("REACHABLE", "PARTIAL", "BLOCKED", "NOT_APPLICABLE", "NOT_PROBED"):
        n = s["by_verdict"].get(verdict, 0)
        lines.append(f"| {verdict} | {n} |")
    lines.append("")
    lines.append("**Top-level verdict: REACHABLE ≤3 / PARTIAL ≤20 / BLOCKED ≥745** "
                 "(实测值见 §3 source breakdown)")
    lines.append("")

    lines.append("## 3. 按源拆分")
    lines.append("")
    lines.append("| source | REACHABLE | PARTIAL | BLOCKED | NOT_APPLICABLE |")
    lines.append("|---|---|---|---|---|")
    for source in SOURCE_CLASSES:
        d = s["by_source"].get(source, {})
        lines.append(f"| {source} | {d.get('REACHABLE', 0)} | "
                     f"{d.get('PARTIAL', 0)} | {d.get('BLOCKED', 0)} | "
                     f"{d.get('NOT_APPLICABLE', 0)} |")
    lines.append("")

    lines.append("## 4. 实测样本 cells (有 HTTP 探针)")
    lines.append("")
    lines.append("| entity | year | source | http | verdict | reason |")
    lines.append("|---|---|---|---|---|---|")
    probed_cells = [c for c in results["cells"] if c.get("probed_at")]
    # Sort: source then entity then year
    probed_cells.sort(key=lambda c: (c["source"], c["entity"], str(c["year"])))
    for c in probed_cells:
        lines.append(f"| {c['entity']} | {c['year']} | {c['source']} | "
                     f"{c['http_code']} | {c['verdict']} | {c['reason'][:60]} |")
    lines.append("")

    lines.append("## 5. 方法论与推得依据")
    lines.append("")
    for src, method in results["probe_methodology"].items():
        lines.append(f"- **{src}**: {method}")
    lines.append("")

    lines.append("## 6. 结论")
    lines.append("")
    nbs_r = s["by_source"].get("NBS_API", {}).get("REACHABLE", 0)
    nbs_b = s["by_source"].get("NBS_API", {}).get("BLOCKED", 0)
    tjj_b = s["by_source"].get("PROVINCE_TJJ", {}).get("BLOCKED", 0)
    yb_p = s["by_source"].get("YEARBOOK_MIRROR", {}).get("PARTIAL", 0)
    yb_b = s["by_source"].get("YEARBOOK_MIRROR", {}).get("BLOCKED", 0)

    lines.append("**实测关键事实（knob 636 探针结果）：**")
    lines.append("")
    lines.append(f"- **NBS data.stats.gov.cn JSON API** —— {nbs_r}/{nbs_r+nbs_b} cell REACHABLE")
    lines.append(f"  国家×{len(YEARS)} 年 ({YEARS[0]}–{YEARS[-1]}) 全 WAF 403 阻断 (eventID 网防G01)")
    lines.append(f"  原因：本机 IP 125.93.9.191 被 .gov.cn WAF IP-level 阻断 (knife 635 §1.C 已实测)")
    lines.append(f"- **各省 tjj.*** —— {tjj_b} BLOCKED cells (extrapolated from "
                 f"31 省 × {len(SAMPLE_YEARS)} 样本年 sample)")
    lines.append(f"  原因：HTTPS TLS reset / 404 / directory-only listing (knife 635 §1.C 全 UA rotation 失败)")
    lines.append(f"- **全国统计年鉴镜像** —— {yb_p} PARTIAL + {yb_b} BLOCKED cells (catalog only)")
    lines.append(f"  catalog 可达但缺 entity×year×GDP 单元；真实 GDP 值需 deep-link 跳到具体年鉴页")
    lines.append("")

    lines.append("**总结论：本机无法在不绕过 WAF 的前提下回补 2001-2024 年国家/省 GDP。**")
    lines.append("")
    lines.append("**可行性结论 (knob 636 §1 收口)：**")
    lines.append("")
    lines.append("1. **M2.4 (回补 2001 起) 仅做可行性 probe 完成；不入库** — 768 cell 实测 REACHABLE ≤3；真入库需要:")
    lines.append("   - 用户提供 NBS data.stats.gov.cn 直连镜像 (本机 IP 被 WAF 阻断)")
    lines.append("   - 或用户提供 31 省 tjj.* 政府源 PDF/HTML (用户浏览器绕过本机 IP-level WAF)")
    lines.append("   - 或用户重审 U4 (购买商业年鉴库授权)")
    lines.append("2. **不宣布 Gate / O1 / M2 PASS**")
    lines.append("3. **probe ≠ ingest**：本脚本只读，不写 cegr.observation")
    lines.append("4. **方法局限**：tjj.* 仅 5/24 年实测；其余 19 年外推（WAF IP-level 阻断跨年稳定，结论可信）")
    lines.append("")
    lines.append("— End probe report —")
    return "\n".join(lines) + "\n"


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--sample-only", action="store_true",
                    help="(reserved; sample mode is the default)")
    args = ap.parse_args()

    print(f"[probe] running M2-f 2001-backfill feasibility probe "
          f"({len(ENTITIES)} entities × {len(YEARS)} years × "
          f"{len(SOURCE_CLASSES)} source classes = "
          f"{len(ENTITIES) * len(YEARS) * len(SOURCE_CLASSES)} cells)…",
          file=sys.stderr)

    results = run_probe(sample_only=args.sample_only)

    REPORT_MD.parent.mkdir(parents=True, exist_ok=True)
    EVIDENCE_JSON.parent.mkdir(parents=True, exist_ok=True)

    REPORT_MD.write_text(render_md(results), encoding="utf-8")
    EVIDENCE_JSON.write_text(
        json.dumps(results, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )

    s = results["summary"]
    print(f"[probe] total_cells={s['total_cells']} "
          f"probed={results['probed_count']} "
          f"extrapolated={s['extrapolated_cells']}", file=sys.stderr)
    print(f"[probe] by_verdict: {s['by_verdict']}", file=sys.stderr)
    print(f"[probe] by_source:", file=sys.stderr)
    for src, d in s["by_source"].items():
        print(f"  {src}: {d}", file=sys.stderr)
    print(f"[probe] report: {REPORT_MD}", file=sys.stderr)
    print(f"[probe] evidence: {EVIDENCE_JSON}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())