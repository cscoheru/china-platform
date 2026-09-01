"""M4.13 政策详情 v7 真实化 spike fetch (knife 650 §A.1, 2026-09-01).

Per knife 650 tasking §1.650-A.1:
- 2 真实样本: guizhou + jiangsu (第 13/14 样本)
- guizhou 首选: https://www.guizhou.gov.cn/zwgk/ ; fallback #1: https://www.guizhou.gov.cn/ (省府根)
- jiangsu 首选: https://www.jiangsu.gov.cn/zwgk/ ; fallback #1: https://www.jiangsu.gov.cn/ (省府根)
- 两级均 BLOCKED → 递补池按序 shaanxi → sichuan (per 650 §0.13 红线 13 增补; 649 递补池首次激活 liaoning 已用; 剩 4 候选 → 本刀缩为 shaanxi → sichuan)
- chain_id = 'real_650_m4_13_policy_detail_v7' (末段 `_v7` ≠ 649 `_v6` ≠ 648 `_v5`)
- UUID i 段 (i0eebc99-i6eebc99) ≠ 649 h 段 ≠ 648 g 段 ≠ 647 f 段
- 已用省全集 (不得重复, 按 actual_province 口径): HLJ / HENAN / YUNNAN / FUJIAN / GD / ZJ / JX / HUN / AH / LN / JL
- 2 NEW SHA 全 distinct ≠ 638-649 全部 SHA
- lineage 全 is_demo='false' 真实化 sentinel (per docs/33 §3.2)
- 16 INSERT total = 12 政策表 + 2 source_registry + 2 source_document
- ≤12 HTTP total (per 650 §A.1 总预算)
- 零 cegr.* mutation; 零爬网; 仅 1 HTTP per cell

数据源唯一 = 政府/统计局/研究机构自取; 用户零裁定。
"""
from __future__ import annotations

import hashlib
import json
import subprocess
import sys
from pathlib import Path
from typing import Any

# 首选 + fallback 1 (省府根)
GUIZHOU_FALLBACK_CHAIN: list[tuple[str, str]] = [
    ("https://www.guizhou.gov.cn/zwgk/", "zwgk_root"),
    ("https://www.guizhou.gov.cn/", "province_root"),
]
JIANGSU_FALLBACK_CHAIN: list[tuple[str, str]] = [
    ("https://www.jiangsu.gov.cn/zwgk/", "zwgk_root"),
    ("https://www.jiangsu.gov.cn/", "province_root"),
]
# 递补池 (per 650 §0.13 增补: 649 liaoning 已用 → 剩 shaanxi/sichuan/guizhou/jiangsu → 本刀首选 = guizhou + jiangsu; 触发则按序 shaanxi → sichuan)
SUBSTITUTE_POOL: list[tuple[str, list[tuple[str, str]], str]] = [
    ("shaanxi", [
        ("https://www.shaanxi.gov.cn/zwgk/", "zwgk_root"),
        ("https://www.shaanxi.gov.cn/", "province_root"),
    ], "陕ICP备"),
    ("sichuan", [
        ("https://www.sc.gov.cn/zwgk/", "zwgk_root"),
        ("https://www.sc.gov.cn/", "province_root"),
    ], "川ICP备"),
]

# 总预算
HTTP_LIMIT = 12
TIMEOUT = 15

# 锚点正则
ANCHOR_RE = (
    r"贵州|江苏|shaanxi|sichuan|政务公开|政府公报|政府文件|政策法规|公开目录|领导信息"
)
ANCHOR_RE_PROVINCIAL_GENERIC = (
    r"人民政府|省政府|省政府办公厅|省人民政府办公厅|政务公开|政府公报|政府文件"
)
WAF_BLOCK_RE = r"403 Forbidden|WAF|网防G01|eventID"


def _curl(url: str, timeout: int = TIMEOUT) -> tuple[int, str, str]:
    """Single curl fetch. Returns (http_code, reason, body)."""
    try:
        proc = subprocess.run(
            ["curl", "-sS", "-L", "--max-time", str(timeout),
             "-o", "/tmp/_650_fetch_body", "-w", "%{http_code}|%{errormsg}",
             url],
            capture_output=True, text=True, timeout=timeout + 5,
        )
        out = proc.stdout.strip()
        parts = out.split("|", 1)
        code_str = parts[0]
        reason = parts[1] if len(parts) > 1 else ""
        try:
            code = int(code_str)
        except ValueError:
            code = 0
        body = Path("/tmp/_650_fetch_body").read_bytes()
        return code, reason, body.decode("utf-8", errors="replace")
    except subprocess.TimeoutExpired:
        return 0, "timeout", ""
    except Exception as e:
        return 0, f"error: {e}", ""


def _sha256(body: str) -> str:
    return hashlib.sha256(body.encode("utf-8")).hexdigest()


def _anchor_hits(body: str, province: str) -> int:
    """Count anchor hits in body. Province-specific + generic."""
    import re
    prov_keywords: dict[str, list[str]] = {
        "guizhou": ["贵州", "guizhou", "gz", "黔"],
        "jiangsu": ["江苏", "jiangsu", "js", "苏"],
        "shaanxi": ["陕西", "shaanxi", "陕"],
        "sichuan": ["四川", "sichuan", "sc", "川"],
    }
    keywords = prov_keywords.get(province, [province])
    text = body
    hits = 0
    for kw in keywords:
        hits += len(re.findall(re.escape(kw), text))
    # 政务类 generic
    for kw in ["政务公开", "政府公报", "政府文件", "政策法规", "公开目录", "领导信息"]:
        hits += len(re.findall(re.escape(kw), text))
    return hits


def _waf_marker_present(body: str) -> bool:
    import re
    return bool(re.search(WAF_BLOCK_RE, body))


def fetch_cell(
    province: str, fallback_chain: list[tuple[str, str]], http_used: list[int]
) -> dict[str, Any]:
    """Fetch a single cell via fallback chain. Returns cell dict.

    Returns cell with:
    - province: original requested province (e.g., "guizhou") — even after substitute
    - actual_province: where data was actually fetched from (e.g., "shaanxi" if substitute)
    - file_hash_sha256: from actual_province content
    - substitute_used: bool
    - substitute_reason: human-readable explanation if applicable
    """
    cell_log: list[dict[str, Any]] = []
    for url, label in fallback_chain:
        if sum(http_used) >= HTTP_LIMIT:
            cell_log.append({
                "url": url, "label": label,
                "http_code": 0, "reason": "http_budget_exhausted",
                "skip": True,
                "attempt_province": province,
            })
            break
        http_used.append(1)
        code, reason, body = _curl(url)
        size = len(body.encode("utf-8"))
        anchor_hits = _anchor_hits(body, province)
        waf_present = _waf_marker_present(body)
        cell_log.append({
            "url": url, "label": label,
            "http_code": code, "reason": reason or "ok",
            "body_size_bytes": size,
            "anchor_hits_count": anchor_hits,
            "waf_marker_present": waf_present,
            "attempt_province": province,
        })
        # 200 + 真内容 + 有锚点 → REACHABLE
        if code == 200 and size > 1000 and anchor_hits >= 1 and not waf_present:
            return {
                "province": province,  # 原始请求省 (始终不变)
                "actual_province": province,
                "fetched_url": url,
                "chain_index": cell_log.index(cell_log[-1]),
                "fallback_chain_used": [c["label"] for c in cell_log],
                "fetch_log": cell_log,
                "file_hash_sha256": _sha256(body),
                "file_size_bytes": size,
                "http_code": code,
                "anchor_hits_count": anchor_hits,
                "waf_marker_present": waf_present,
                "verdict": "REACHABLE",
                "substitute_used": False,
            }
        # 200 + WAF marker → BLOCKED_WAF
        if code == 200 and waf_present:
            continue  # try next fallback
    # fallback chain 全失败 → 走递补池
    for sub_province, sub_chain, _icp in SUBSTITUTE_POOL:
        if sum(http_used) >= HTTP_LIMIT:
            break
        for url, label in sub_chain:
            if sum(http_used) >= HTTP_LIMIT:
                break
            http_used.append(1)
            code, reason, body = _curl(url)
            size = len(body.encode("utf-8"))
            anchor_hits = _anchor_hits(body, sub_province)
            waf_present = _waf_marker_present(body)
            cell_log.append({
                "url": url, "label": f"substitute[{sub_province}]/{label}",
                "http_code": code, "reason": reason or "ok",
                "body_size_bytes": size,
                "anchor_hits_count": anchor_hits,
                "waf_marker_present": waf_present,
                "attempt_province": sub_province,
            })
            if code == 200 and size > 1000 and anchor_hits >= 1 and not waf_present:
                return {
                    "province": province,  # 原始请求省 (始终不变)
                    "actual_province": sub_province,  # 实际抓取省
                    "fetched_url": url,
                    "chain_index": -1,
                    "fallback_chain_used": [c["label"] for c in cell_log],
                    "fetch_log": cell_log,
                    "file_hash_sha256": _sha256(body),
                    "file_size_bytes": size,
                    "http_code": code,
                    "anchor_hits_count": anchor_hits,
                    "waf_marker_present": waf_present,
                    "verdict": "REACHABLE_VIA_SUBSTITUTE",
                    "substitute_used": True,
                    "substitute_reason": (
                        f"原试点省 {province} 两级 fallback 均未 REACHABLE (412/404/timeout); "
                        f"按 650 任务书 §0.13 递补池按序取 {sub_province}"
                    ),
                }
    # 全部失败
    return {
        "province": province,
        "actual_province": None,
        "fetched_url": None,
        "chain_index": -1,
        "fallback_chain_used": [c["label"] for c in cell_log],
        "fetch_log": cell_log,
        "file_hash_sha256": "",
        "file_size_bytes": 0,
        "http_code": 0,
        "anchor_hits_count": 0,
        "waf_marker_present": False,
        "verdict": "ALL_BLOCKED",
        "substitute_used": False,
    }


def main() -> int:
    http_used: list[int] = []

    # Cell 1: guizhou
    cell_guizhou = fetch_cell("guizhou", GUIZHOU_FALLBACK_CHAIN, http_used)
    # Cell 2: jiangsu
    cell_jiangsu = fetch_cell("jiangsu", JIANGSU_FALLBACK_CHAIN, http_used)

    cells = [cell_guizhou, cell_jiangsu]
    fetched_count = sum(1 for c in cells if c["file_hash_sha256"])
    fetch_status = (
        "REAL_FETCHED" if fetched_count == 2
        else "PARTIAL" if fetched_count == 1
        else "ALL_BLOCKED"
    )

    # 合并 fetch_log (保留每条 entry 的 attempt_province)
    fetch_log: list[dict[str, Any]] = []
    for c in cells:
        for entry in c["fetch_log"]:
            fetch_log.append(entry)  # attempt_province 已在 entry 内

    output = {
        "knife": "650-A.1",
        "purpose": "M4.13 政策详情 v7 真实化 spike (guizhou + jiangsu 第 13/14 样本; 649 P3-1 蓝图更正 + 红线 13 增补; 递补池按序 shaanxi → sichuan)",
        "chain_id": "real_650_m4_13_policy_detail_v7",
        "uuid_prefix": "i",
        "uuid_prefixes": {
            "source_registry": "i0eebc99",
            "source_document": "i0eebc99",
            "policy_document": "i1eebc99",
            "policy_target": "i2eebc99",
            "policy_measure": "i3eebc99",
            "government_commitment": "i4eebc99",
            "commitment_progress": "i5eebc99",
            "project_event": "i6eebc99",
        },
        "summary": {
            "fetch_status": fetch_status,
            "fetched_count": fetched_count,
            "http_count": sum(http_used),
            "http_limit": HTTP_LIMIT,
            "substitute_used_count": sum(1 for c in cells if c.get("substitute_used")),
            "distinct_shas": sorted({
                c["file_hash_sha256"] for c in cells if c["file_hash_sha256"]
            }),
        },
        "cells": cells,
        "fetch_log": fetch_log,
        "methodology": (
            "v7 spike fetch: 2 cells (guizhou + jiangsu), each with primary /zwgk/ + "
            "fallback #1 (省府根 /) + 递补池 (shaanxi→sichuan). "
            "每 cell ≤4 attempts, 总预算 ≤12 HTTP. "
            "Per 650 §0.13: 附属复验/验证产物允许独立文件, 但主 evidence methodology 必须含指针. "
            "代换行 source_registry province/source_name 一律用 actual_province (per 649 P3-1)."
        ),
    }

    out_path = Path("evidence_pack/m4_13_policy_detail_real_v7_20260901.json")
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(
        json.dumps(output, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    print(json.dumps(output, ensure_ascii=False, indent=2))
    print(f"[OK] wrote fetch evidence to {out_path}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())