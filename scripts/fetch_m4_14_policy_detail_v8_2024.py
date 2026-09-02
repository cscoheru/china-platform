"""M4.14 政策详情 v8 真实化 spike fetch (knife 651 §A.1, 2026-09-02).

Per knife 651 tasking §1.651-A.1:
- 2 真实样本: shaanxi + sichuan (第 15/16 样本; 递补池收官转正)
- shaanxi 首选: https://www.shaanxi.gov.cn/zwgk/ ; fallback #1: https://www.shaanxi.gov.cn/
- sichuan 首选: https://www.sc.gov.cn/zwgk/ ; fallback #1: https://www.sc.gov.cn/
- 两级均 BLOCKED → **无池可递补 → BLOCKED 留痕** (per 红线 14 增补: 递补池正式耗尽, 不代换)
- chain_id = 'real_651_m4_14_policy_detail_v8' (末段 `_v8` ≠ 650 `_v7` ≠ 649 `_v6`)
- UUID j 段 (j0eebc99-j6eebc99) ≠ 650 i 段 ≠ 649 h 段 ≠ 648 g 段
- 已用省全集 (不得重复, 按 actual_province 口径): HLJ/HENAN/YUNNAN/FUJIAN/GD/ZJ/JX/HUN/AH/LN/JL/GUIZHOU/JIANGSU; 651 增量 = SHAANXI/SICHUAN → 16 省全集
- 2 NEW SHA 全 distinct ≠ 638-650 全部 SHA
- lineage 全 is_demo='false' 真实化 sentinel (per docs/33 §3.2)
- 16 INSERT total = 12 政策表 + 2 source_registry + 2 source_document
- ≤12 HTTP total (per 651 §A.1 总预算; 全刀预期 2-10)
- 零 cegr.* mutation; 零爬网; 仅 1-2 HTTP per cell

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
SHAANXI_FALLBACK_CHAIN: list[tuple[str, str]] = [
    ("https://www.shaanxi.gov.cn/zwgk/", "zwgk_root"),
    ("https://www.shaanxi.gov.cn/", "province_root"),
]
SICHUAN_FALLBACK_CHAIN: list[tuple[str, str]] = [
    ("https://www.sc.gov.cn/zwgk/", "zwgk_root"),
    ("https://www.sc.gov.cn/", "province_root"),
]
# 递补池 (per 651 §0.14 红线 14 增补: 递补池正式耗尽 [EXHAUSTED]; 651 后任
#   何样本槽两级 fallback 全失败 → BLOCKED 留痕, 不再跨省代换)
SUBSTITUTE_POOL: list[tuple[str, list[tuple[str, str]], str]] = []
SUBSTITUTE_POOL_STATUS = "EXHAUSTED"  # per 红线 14 增补; 651 后池耗尽条款

# 总预算
HTTP_LIMIT = 12
TIMEOUT = 15

# 锚点正则
ANCHOR_RE_PROVINCIAL_GENERIC = (
    r"人民政府|省政府|省政府办公厅|省人民政府办公厅|政务公开|政府公报|政府文件"
)
WAF_BLOCK_RE = r"403 Forbidden|WAF|网防G01|eventID"


def _curl(url: str, timeout: int = TIMEOUT) -> tuple[int, str, str]:
    """Single curl fetch. Returns (http_code, reason, body)."""
    try:
        proc = subprocess.run(
            ["curl", "-sS", "-L", "--max-time", str(timeout),
             "-o", "/tmp/_651_fetch_body", "-w", "%{http_code}|%{errormsg}",
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
        body = Path("/tmp/_651_fetch_body").read_bytes()
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

    Per 红线 14: 递补池耗尽; 两级 fallback 全失败 → BLOCKED 留痕, 不跨省代换。

    Returns cell with:
    - province: original requested province
    - actual_province: where data was actually fetched from (= province since no substitute)
    - file_hash_sha256: from actual_province content (or empty if BLOCKED)
    - substitute_used: bool (always False since pool exhausted per 红线 14)
    - blocked_reason: human-readable explanation if BLOCKED_NO_POOL
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
        # 200 + WAF marker → BLOCKED_WAF (try next)
        if code == 200 and waf_present:
            continue  # try next fallback
    # 全部 fallback chain 失败 → BLOCKED 留痕 (per 红线 14 增补; 无池可代换)
    cell_log_summary = "; ".join(
        f"{e['label']}={e['http_code']}" for e in cell_log
    )
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
        "verdict": "BLOCKED_NO_POOL",
        "substitute_used": False,
        "blocked_reason": (
            f"原试点省 {province} 两级 fallback 均未 REACHABLE ({cell_log_summary}); "
            f"per 651 §0.14 红线 14 增补: 递补池正式耗尽 [EXHAUSTED], 无池可代换, 留痕不代换"
        ),
    }


def main() -> int:
    http_used: list[int] = []

    # Cell 1: shaanxi
    cell_shaanxi = fetch_cell("shaanxi", SHAANXI_FALLBACK_CHAIN, http_used)
    # Cell 2: sichuan
    cell_sichuan = fetch_cell("sichuan", SICHUAN_FALLBACK_CHAIN, http_used)

    cells = [cell_shaanxi, cell_sichuan]
    fetched_count = sum(1 for c in cells if c["file_hash_sha256"])
    fetch_status = (
        "REAL_FETCHED" if fetched_count == 2
        else "PARTIAL" if fetched_count == 1
        else "ALL_BLOCKED_NO_POOL"
    )

    # 合并 fetch_log (保留每条 entry 的 attempt_province)
    fetch_log: list[dict[str, Any]] = []
    for c in cells:
        for entry in c["fetch_log"]:
            fetch_log.append(entry)  # attempt_province 已在 entry 内

    output = {
        "knife": "651-A.1",
        "purpose": "M4.14 政策详情 v8 真实化 spike (shaanxi + sichuan 第 15/16 样本; 递补池收官转正 + 红线 14 增补耗尽条款)",
        "chain_id": "real_651_m4_14_policy_detail_v8",
        "uuid_prefix": "j",
        "uuid_prefixes": {
            "source_registry": "j0eebc99",
            "source_document": "j0eebc99",
            "policy_document": "j1eebc99",
            "policy_target": "j2eebc99",
            "policy_measure": "j3eebc99",
            "government_commitment": "j4eebc99",
            "commitment_progress": "j5eebc99",
            "project_event": "j6eebc99",
        },
        "summary": {
            "fetch_status": fetch_status,
            "fetched_count": fetched_count,
            "http_count": sum(http_used),
            "http_limit": HTTP_LIMIT,
            "substitute_used_count": 0,  # 红线 14: 池耗尽, 不可能 > 0
            "substitute_pool_status": SUBSTITUTE_POOL_STATUS,
            "blocked_no_pool_count": sum(
                1 for c in cells if c.get("verdict") == "BLOCKED_NO_POOL"
            ),
            "distinct_shas": sorted({
                c["file_hash_sha256"] for c in cells if c["file_hash_sha256"]
            }),
        },
        "cells": cells,
        "fetch_log": fetch_log,
        "methodology": (
            "v8 spike fetch: 2 cells (shaanxi + sichuan), each with primary /zwgk/ + "
            "fallback #1 (省府根 /). "
            "递补池 (SUBSTITUTE_POOL) 显式标记 [EXHAUSTED] (per 651 §0.14 红线 14 增补); "
            "两级 fallback 全失败 → BLOCKED_NO_POOL 留痕, 不跨省代换. "
            "每 cell ≤2 attempts, 总预算 ≤12 HTTP. "
            "Per 650 §0.13: 附属复验/验证产物允许独立文件, 但主 evidence methodology 必须含指针. "
            "代换行 source_registry province/source_name 一律用 actual_province (per 649 P3-1). "
            "Per 651 §0.14: BLOCKED_NO_POOL 留痕不代换."
        ),
    }

    out_path = Path("evidence_pack/m4_14_policy_detail_real_v8_20260902.json")
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(
        json.dumps(output, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    print(json.dumps(output, ensure_ascii=False, indent=2))
    print(f"[OK] wrote fetch evidence to {out_path}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())