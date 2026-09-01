"""O1 live-candidate probe (knife 646 Block A.2, O1 B路 main-path registration).

Per knife 646 §3.646-A.2:
- ≥1 live-candidate 政府/统计局源 做候选登记 (markdown-only)
- 不启用、不改生产 connector、不写 cegr.*
- O1 仍 OPEN (B路 主路径 仅登记, 不切换)
- HTTP probe only (single landing cell, no e2e)

HARD LIMITS:
- ≤1 HTTP total (1 candidate × 1 HTTP)
- 不爬网 (no recursion; no follow pagination)
- 仅抓 landing (curl only, no JS / no headless browser)
- 不写 cegr.* 表 (read-only on production)
- 不改 source_registry/registry.csv (registry 零改动)
- 不启用 connector (enabled=FALSE 登记 markdown-only)

1 candidate:
- data.stats.gov.cn (国家统计局 国家数据; NOT in registry.csv 当前 16 行;
  与 stats.gov.cn/sj/zxfb/ (NATIONAL_BULLETIN) / sj/ndsj/ (NATIONAL_YEARBOOK)
  / NATIONAL_BULLETIN_SPIKE 全部不同 sub-domain)

OUTPUT:
* docs/reports/o1_live_candidate_probe_20260901.md
* evidence_pack/o1_live_candidate_probe_20260901.json
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

from _probe_http_helpers import fetch, now_utc_iso

REPO_ROOT = Path(__file__).resolve().parent.parent
REPORT_MD = REPO_ROOT / "docs" / "reports" / "o1_live_candidate_probe_20260901.md"
EVIDENCE_JSON = REPO_ROOT / "evidence_pack" / "o1_live_candidate_probe_20260901.json"

CANDIDATE = {
    "domain": "data.stats.gov.cn",
    "organization": "国家统计局 国家数据 (National Bureau of Statistics - National Data)",
    "category": "NATIONAL_DATA_API",
    "primary_url": "https://data.stats.gov.cn/",
    "purpose_note": (
        "O1 B路 live-candidate 探测登记; 与现有 stats.gov.cn/sj/zxfb/ "
        "(NATIONAL_BULLETIN) + sj/ndsj/ (NATIONAL_YEARBOOK) 不同 sub-domain; "
        "data.stats.gov.cn 提供月度/季度/年度指标 API + HTML 视图; "
        "646 仅登记不启用; O1 仍 OPEN 等用户/架构师裁定启用时机"
    ),
    "auth_note": "公开;无需授权",
    "access_method": "HTML + JSON API",
    "historical_coverage": "国家数据库月度/季度/年度指标 (1949-至今)",
    "stability_note": "URL 格式稳定; sub-domain 与现有 rows 不同, 不会冲突",
    "failure_handling": "重试 3 次 → archive.org 备份 → 人工上传入口",
    "update_frequency": "MONTHLY/QUARTERLY/YEARLY (按指标不同)",
}

TIMEOUT = 15
HTTP_LIMIT = 1


def run_probe() -> dict:
    cells = []
    fetch_log = []
    http_count = 0
    if http_count < HTTP_LIMIT:
        url = CANDIDATE["primary_url"]
        code, reason, body = fetch(url, timeout=TIMEOUT)
        http_count += 1
        fetch_log.append({
            "url": url, "domain": CANDIDATE["domain"],
            "phase": "candidate_probe",
            "http_code": code, "reason": reason,
            "http_attempt": http_count, "fetched_at": now_utc_iso(),
        })
        if reason == "ok" and code == 200:
            sha = hashlib.sha256(body).hexdigest()
            cell = {
                "domain": CANDIDATE["domain"],
                "organization": CANDIDATE["organization"],
                "primary_url": url,
                "file_hash_sha256": sha,
                "file_size_bytes": len(body),
                "registration_status": "PENDING_CANDIDATE_ONLY",
                "enabled_in_registry": False,
                "notes": "646 markdown-only registration; O1 仍 OPEN; no cegr.* mutation; no registry.csv mutation",
            }
            cells.append(cell)

    return {
        "generated_at": now_utc_iso(),
        "summary": {
            "candidate_count": len(cells),
            "http_count": http_count,
            "probe_status": "REAL_PROBED" if cells else "CANDIDATE_BLOCKED",
            "o1_status": "OPEN",
            "registration_scope": "markdown-only",
            "registry_csv_mutation": "NONE",
            "cegr_star_mutation": "NONE",
            "connector_enabled": False,
            "candidate_methodology": (
                f"O1 B路 live-candidate 探测登记; 1 candidate (data.stats.gov.cn) × 1 HTTP each = "
                f"{len(cells)} real probe; ≤{HTTP_LIMIT} HTTP total; curl only; "
                f"markdown-only registration; O1 仍 OPEN"
            ),
        },
        "fetch_log": fetch_log,
        "cells": cells,
        "candidate_spec": CANDIDATE,
    }


def write_outputs(results: dict) -> None:
    EVIDENCE_JSON.parent.mkdir(parents=True, exist_ok=True)
    REPORT_MD.parent.mkdir(parents=True, exist_ok=True)
    EVIDENCE_JSON.write_text(
        json.dumps(results, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    sv = results["summary"]
    cs = results["candidate_spec"]
    top = sv.get("probe_status", "NOT_PROBED")
    lines = [
        "# O1 B 路 live-candidate 探测登记（2026-09-01，knife 646 O1 side）",
        "",
        "> **类型**: 646-A.2 O1 B路 live-candidate markdown-only 探测登记",
        "> **作用域**: 仅登记 (registration only); 不启用; 不写 cegr.*; 不改 registry.csv",
        "> **O1 状态**: **仍 OPEN** (B路 主路径 仅登记 candidate, 不切换/启用)",
        "> **前置**: 645 DELIVERED + 审计 PASS (`645-stage0-cursor-s645-m6-m4-8-audit-PASS-20260901.md`)",
        "> **架构师依据**: 646-A.2 spec; per docs/52 §13 B路 主路径 (per 599/601) + 用户零裁定铁律 2026-08-29",
        "",
        "## 0. 顶层裁定",
        "",
        f"**{top}** — 适用 {sv.get('http_count', 0)} HTTP, 实测 "
        f"{sv.get('candidate_count', 0)} candidate。",
        "",
        f"O1 状态: **{sv.get('o1_status', 'OPEN')}** (主路径 B路 live-candidate 仅登记, 不切换)",
        f"注册作用域: **{sv.get('registration_scope', 'markdown-only')}**",
        f"registry.csv 变更: **{sv.get('registry_csv_mutation', 'NONE')}**",
        f"cegr.* 表变更: **{sv.get('cegr_star_mutation', 'NONE')}**",
        f"connector enabled: **{sv.get('connector_enabled', False)}**",
        "",
        "## 1. Live-candidate 实体逐项",
        "",
        "| 序号 | domain | organization | primary_url | sha256 (前 16) | file_size | registration_status |",
        "|---|---|---|---|---|---|---|",
    ]
    for i, c in enumerate(results["cells"], start=1):
        sha_short = c.get("file_hash_sha256", "")[:16]
        lines.append(
            f"| {i} | {c.get('domain', '')} | {c.get('organization', '')[:30]} | "
            f"{c.get('primary_url', '')} | {sha_short} | {c.get('file_size_bytes', 0)} | "
            f"{c.get('registration_status', '')} |"
        )
    lines += [
        "",
        "## 2. Candidate spec 详情",
        "",
        "| 字段 | 值 |",
        "|---|---|",
        f"| domain | {cs['domain']} |",
        f"| organization | {cs['organization']} |",
        f"| category | {cs['category']} |",
        f"| primary_url | {cs['primary_url']} |",
        f"| auth_note | {cs['auth_note']} |",
        f"| access_method | {cs['access_method']} |",
        f"| historical_coverage | {cs['historical_coverage']} |",
        f"| stability_note | {cs['stability_note']} |",
        f"| failure_handling | {cs['failure_handling']} |",
        f"| update_frequency | {cs['update_frequency']} |",
        f"| purpose_note | {cs['purpose_note']} |",
        "",
        "## 3. HTTP 抓取日志",
        "",
        "| URL | domain | phase | http_code | reason | 抓取时刻 |",
        "|---|---|---|---|---|---|",
    ]
    for fl in results["fetch_log"]:
        lines.append(
            f"| {fl['url']} | {fl['domain']} | {fl['phase']} | "
            f"{fl['http_code']} | {fl['reason']} | {fl['fetched_at']} |"
        )
    lines += [
        "",
        "## 4. 启用前置条件 (等用户/架构师裁定)",
        "",
        "- [ ] M2 Gate 决策结果 (当前 O1 仍 OPEN)",
        "- [ ] 用户/架构师对 data.stats.gov.cn connector 的明确启用授权",
        "- [ ] connector 实现 + 端端 e2e 验证 (现有 B路 公开源自动获取六步流水线已就绪 per docs/52 §13)",
        "- [ ] 单元测试 + 集成测试覆盖 (e.g. fetch 200 / SHA 校验 / 错误重试)",
        "",
        "## 5. 红线遵守",
        "",
        "- ✓ ≤1 HTTP total (硬性上限)",
        "- ✓ 不爬网 (no follow pagination; no recursion)",
        "- ✓ 不写 cegr.* 表 (read-only on production)",
        "- ✓ 不改 registry.csv (registry 零改动)",
        "- ✓ 不启用 connector (enabled=FALSE)",
        "- ✓ O1 仍 OPEN (B路 主路径 仅登记, 不切换)",
        "- ✓ 不静默硬编码 value (从抓取解析 SHA)",
        "- ✓ 脚本幂等 (no time.sleep / no random; sha256 deterministic)",
        "- ✓ 数据源唯一 = 政府/统计局/研究机构自取 (data.stats.gov.cn = 国家统计局 国家数据, 满足)",
        "- ✓ 不宣称 Gate / O1 / O2 / O3 / M2 / M4.x / M5.x / M6 / O1 B路 live-candidate PASS",
        "",
    ]
    REPORT_MD.write_text("\n".join(lines), encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description="646-A.2 O1 B路 live-candidate 探测登记")
    args = parser.parse_args()
    results = run_probe()
    write_outputs(results)
    print(
        f"646-A.2 O1 live-candidate: http_count={results['summary']['http_count']}, "
        f"candidate_count={results['summary']['candidate_count']}, "
        f"status={results['summary']['probe_status']}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())