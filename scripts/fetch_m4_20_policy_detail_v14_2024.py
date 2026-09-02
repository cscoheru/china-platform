"""M4.20 政策详情 v14 HEBEI+SHANXI 全国 31 省收官 spike fetch (knife 657 §1.657, 2026-09-02).

Per knife 657 tasking §1.657:
- 2 真实样本: HEBEI + SHANXI (第 27/28 样本; 全国 31 省收官刀; 双首试省无前史 → retry_of=N/A)
- HEBEI 首选: https://www.hebei.gov.cn/zwgk/ ; fallback #1: https://www.hebei.gov.cn/
- SHANXI 首选: https://www.shanxi.gov.cn/zwgk/ ; fallback #1: https://www.shanxi.gov.cn/
- 双首试省无前史 (per 656 §0.14 + 657 §0.14) → retry_of 不适用 (留空); 若 BLOCKED → 纯 BLOCKED_NO_POOL 留痕
- 三态合法: 双 REACHABLE / 混合 / 双 BLOCKED
- chain_id = 'real_657_m4_20_policy_detail_v14' (末段 `_v14` ≠ 656 `_v13` ≠ 655 `_v12` ≠ 654 `_v11` ≠ 653 `_v10` ≠ 652 `_v9` ≠ 651 `_v8`)
- UUID p 段 (p0eebc99-p6eebc99) ≠ 656 o 段 ≠ 655 n 段 ≠ 654 m 段 ≠ 653 l 段 ≠ 652 k 段 ≠ 651 j 段
- 已用省全集 (不得重复, 按 actual_province 口径, 21 省 after 656):
  HLJ/HENAN/YUNNAN/FUJIAN/GD/ZJ/JX/HUN/AH/LN/JL/GUIZHOU/JIANGSU/SHAANXI/SICHUAN/XINJIANG/NEI MENGGU/XIZANG/GUANGXI/HAINAN
  657 增量后 = 21/23 省 (双 REACHABLE → 23 省; 留 8 省给 658)
  注: 657 全国 31 省收官刀 = 27/28 样本; 收官后留 3 省 (TBD, 待 658+ 切)
- 2 NEW SHA 全 distinct ≠ 638-656 全部 SHA (or BLOCKED cell 留 blocked_reason 无 SHA)
- lineage 全 is_demo='false' 真实化 sentinel (per docs/33 §3.2)
- ≤12 HTTP total (per 657 §0.3 红线 3)
- 零 cegr.* mutation; 零爬网; 仅 1-2 HTTP per cell

数据源唯一 = 政府/统计局/研究机构自取; 用户零裁定 (per 2026-08-29 铁律)。
"""
from __future__ import annotations

import hashlib
import json
import subprocess
import sys
from pathlib import Path
from typing import Any

# 首选 + fallback 1 (省府根)
HEBEI_FALLBACK_CHAIN: list[tuple[str, str]] = [
    ("https://www.hebei.gov.cn/zwgk/", "zwgk_root"),
    ("https://www.hebei.gov.cn/", "province_root"),
]
SHANXI_FALLBACK_CHAIN: list[tuple[str, str]] = [
    ("https://www.shanxi.gov.cn/zwgk/", "zwgk_root"),
    ("https://www.shanxi.gov.cn/", "province_root"),
]
# 递补池 (per 657 §0.14 红线 14 沿用 654-656 耗尽态)
SUBSTITUTE_POOL: list[tuple[str, list[tuple[str, str]], str]] = []
SUBSTITUTE_POOL_STATUS = "EXHAUSTED"  # per 红线 14 增补; 657 沿用 656 耗尽态

# 首试省 lineage 注解 (per 657 §0.14 红线 14 + 657 tasking §1.657)
# 无前史 → retry_of 不适用 (留空); 若 BLOCKED → 纯 BLOCKED_NO_POOL 留痕
RETRY_OF_NOTES: dict[str, str] = {
    "hebei": "retry_of=N/A (无前史首试; per 657 §0.14)",
    "shanxi": "retry_of=N/A (无前史首试; per 657 §0.14)",
}

# 总预算
HTTP_LIMIT = 12
TIMEOUT = 15

# 锚点正则
ANCHOR_RE_PROVINCIAL_GENERIC = (
    r"人民政府|省政府|省政府办公厅|省人民政府办公厅|政务公开|政府公报|政府文件"
)
WAF_BLOCK_RE = r"403 Forbidden|WAF|网防G01|eventID"


def _curl(url: str, timeout: int = TIMEOUT) -> tuple[int, str, str]:
    """Single curl fetch. Returns (http_code, reason, body).

    Robust to SSL/network errors: when curl fails before writing body file,
    falls back to proc.stderr / curl errormsg from -w template.
    """
    body_path = Path(f"/tmp/_657_fetch_{abs(hash(url)) % 100000}")
    try:
        proc = subprocess.run(
            ["curl", "-sS", "-L", "--max-time", str(timeout),
             "-o", str(body_path), "-w", "%{http_code}|%{errormsg}",
             url],
            capture_output=True, text=True, timeout=timeout + 5,
        )
        out = (proc.stdout or "").strip()
        err = (proc.stderr or "").strip()
        parts = out.split("|", 1)
        code_str = parts[0]
        curl_reason = parts[1] if len(parts) > 1 else ""
        try:
            code = int(code_str)
        except ValueError:
            code = 0
        if body_path.exists():
            body_bytes = body_path.read_bytes()
            try:
                body = body_bytes.decode("utf-8", errors="replace")
            except Exception:
                body = ""
            reason = curl_reason or err.split("\n", 1)[-1] or "ok"
        else:
            body = ""
            reason = curl_reason or err or "no_body_file"
        return code, reason, body
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
        "hebei": ["河北", "hebei", "冀"],
        "shanxi": ["山西", "shanxi", "晋"],
    }
    keywords = prov_keywords.get(province, [province])
    text = body
    hits = 0
    for kw in keywords:
        hits += len(re.findall(re.escape(kw), text))
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

    Per 红线 14 沿用 654-656: 递补池耗尽; 两级 fallback 全失败 → BLOCKED 留痕, 不跨省代换。
    657 §0.14 首试省: 该分支代码必须存在并可达, 无论 REACHABLE 还是 BLOCKED;
    三态均合法 (双 REACHABLE → 16 INSERT + 2 NEW SHA; 混合 → 按省实报; 双 BLOCKED → 0 INSERT + 三重留痕)。
    HEBEI/SHANXI 无前史 → retry_of 不适用 (首试省; lineage 留空留痕)。
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
        if code == 200 and size > 1000 and anchor_hits >= 1 and not waf_present:
            return {
                "province": province,
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
                "retry_of": RETRY_OF_NOTES.get(province, ""),
            }
        if code == 200 and waf_present:
            continue
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
            f"首试省 {province} 两级 fallback 均未 REACHABLE ({cell_log_summary}); "
            f"per 657 §0.14 红线 14 增补 (沿用 654-656): 递补池正式耗尽 [EXHAUSTED], "
            f"无池可代换, 留痕不代换 (BLOCKED_NO_POOL 留痕首试省真网触发, per 657 §0.14). "
            f"lineage retry_of=N/A (无前史首试省; per 657 §1.657)."
        ),
        "retry_of": RETRY_OF_NOTES.get(province, ""),
    }


def main() -> int:
    http_used: list[int] = []

    cell_hebei = fetch_cell("hebei", HEBEI_FALLBACK_CHAIN, http_used)
    cell_shanxi = fetch_cell("shanxi", SHANXI_FALLBACK_CHAIN, http_used)

    cells = [cell_hebei, cell_shanxi]
    fetched_count = sum(1 for c in cells if c["file_hash_sha256"])
    blocked_count = sum(1 for c in cells if c.get("verdict") == "BLOCKED_NO_POOL")
    if fetched_count == 2:
        fetch_status = "REAL_FETCHED"
    elif fetched_count == 1:
        fetch_status = "PARTIAL_BLOCKED"
    elif blocked_count == 2:
        fetch_status = "ALL_BLOCKED_NO_POOL"
    else:
        fetch_status = "ALL_BLOCKED_NO_POOL"

    fetch_log: list[dict[str, Any]] = []
    for c in cells:
        for entry in c["fetch_log"]:
            fetch_log.append(entry)

    output = {
        "knife": "657",
        "purpose": (
            "M4.20 政策详情 v14 HEBEI+SHANXI 全国 31 省收官 spike (第 27/28 样本; "
            "双首试省 per 657 §0.14 沿用 656 §0.14; "
            "真网首试 BLOCKED_NO_POOL 留痕概率; lineage 全 retry_of=N/A)"
        ),
        "chain_id": "real_657_m4_20_policy_detail_v14",
        "uuid_prefix": "p",
        "uuid_prefixes": {
            "source_registry": "p0eebc99",
            "source_document": "p0eebc99",
            "policy_document": "p1eebc99",
            "policy_target": "p2eebc99",
            "policy_measure": "p3eebc99",
            "government_commitment": "p4eebc99",
            "commitment_progress": "p5eebc99",
            "project_event": "p6eebc99",
        },
        "summary": {
            "fetch_status": fetch_status,
            "fetched_count": fetched_count,
            "blocked_no_pool_count": blocked_count,
            "http_count": sum(http_used),
            "http_limit": HTTP_LIMIT,
            "substitute_used_count": 0,
            "substitute_pool_status": SUBSTITUTE_POOL_STATUS,
            "distinct_shas": sorted({
                c["file_hash_sha256"] for c in cells if c["file_hash_sha256"]
            }),
            "retry_of_annotation": RETRY_OF_NOTES,
        },
        "cells": cells,
        "fetch_log": fetch_log,
        "methodology": (
            "v14 HEBEI+SHANXI 全国 31 省收官 spike fetch: 2 cells (hebei + shanxi 第 27/28 样本; "
            "双首试省 per 657 §0.14 沿用 656 §0.14). "
            "HEBEI 首选 https://www.hebei.gov.cn/zwgk/ + fallback #1 https://www.hebei.gov.cn/; "
            "SHANXI 首选 https://www.shanxi.gov.cn/zwgk/ + fallback #1 https://www.shanxi.gov.cn/. "
            "递补池 (SUBSTITUTE_POOL) 显式 [EXHAUSTED] (per 657 §0.14 红线 14 增补沿用 656 §0.14); "
            "两级 fallback 全失败 → BLOCKED_NO_POOL 留痕, 不跨省代换. "
            "每 cell ≤2 attempts, 总预算 ≤12 HTTP. "
            "lineage retry_of=N/A (双省无前史首试; per 657 §1.657). "
            "三态均合法 (任务书明文): 双 REACHABLE → 16 INSERT ROWS 正常落 + 2 NEW SHA; 混合 → 按省实报; 双 BLOCKED → 0 INSERT + 三重留痕 (evidence/docs/receipt). "
            "Per 650 §0.13: 附属复验/验证产物允许独立文件, 但主 evidence methodology 必须含指针. "
            "代换行 source_registry province/source_name 一律用 actual_province (per 649 P3-1). "
            "Per 657 §0.14: 首试省 BLOCKED_NO_POOL 留痕 e2e 验证 (沿用 656 §0.14 模板). "
            "递补池 [EXHAUSTED] 沿用 656. "
            "全国 31 省收官刀: HEBEI + SHANXI (留 3 省 TBD 给 658+). "
            f"本次双样本结果: REACHABLE×{fetched_count} / BLOCKED_NO_POOL×{blocked_count}."
        ),
    }

    out_path = Path("evidence_pack/m4_20_policy_detail_real_v14_20260902.json")
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(
        json.dumps(output, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    print(json.dumps(output, ensure_ascii=False, indent=2))
    print(f"[OK] wrote fetch evidence to {out_path}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
