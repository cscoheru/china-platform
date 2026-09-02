"""M4.18 政策详情 v12 西部终章双省 spike fetch (knife 655 §A.1, 2026-09-02).

Per knife 655 tasking §1.655-A.1:
- 2 真实样本: NINGXIA + XIZANG (第 23/24 样本; 西部七省区全覆盖终章: SHAANXI/GANSU/QINGHAI/XINJIANG/NEIMENGGU + 本刀二省区)
- NINGXIA 首选: https://www.nx.gov.cn/zwgk/ ; fallback #1: https://www.nx.gov.cn/
- XIZANG 首选: https://www.xizang.gov.cn/zwgk/ ; fallback #1: https://www.xizang.gov.cn/
- 两省无前史首试 (vs 654 双首试) → retry_of 不适用 (首试省); 若 BLOCKED → 纯 BLOCKED_NO_POOL 留痕
- 三态合法: 双 REACHABLE / 混合 / 双 BLOCKED
- chain_id = 'real_655_m4_18_policy_detail_v12' (末段 `_v12` ≠ 654 `_v11` ≠ 653 `_v10` ≠ 652 `_v9` ≠ 651 `_v8`)
- UUID n 段 (n0eebc99-n6eebc99) ≠ 654 m 段 ≠ 653 l 段 ≠ 652 k 段 ≠ 651 j 段 ≠ 650 i 段
- 已用省全集 (不得重复, 按 actual_province 口径, 18 省):
  HLJ/HENAN/YUNNAN/FUJIAN/GD/ZJ/JX/HUN/AH/LN/JL/GUIZHOU/JIANGSU/SHAANXI/SICHUAN/XINJIANG/NEI MENGGU
  655 增量后 = 19/20 省 (若任一 REACHABLE)
  注: 西部五省区 651+652+654 已用 (SHAANXI/GANSU/QINGHAI/XINJIANG/NEIMENGGU);
  → 655 双省 NINGXIA/XIZANG (西部七省区全覆盖终章: 651+652+654+655 收官)
- 2 NEW SHA 全 distinct ≠ 638-654 全部 SHA (或 BLOCKED cell 留 blocked_reason 无 SHA)
- lineage 全 is_demo='false' 真实化 sentinel (per docs/33 §3.2)
- ≤12 HTTP total (per 655 §0.3 红线 3 + 全刀预期 4-8)
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
NINGXIA_FALLBACK_CHAIN: list[tuple[str, str]] = [
    ("https://www.nx.gov.cn/zwgk/", "zwgk_root"),
    ("https://www.nx.gov.cn/", "province_root"),
]
XIZANG_FALLBACK_CHAIN: list[tuple[str, str]] = [
    ("https://www.xizang.gov.cn/zwgk/", "zwgk_root"),
    ("https://www.xizang.gov.cn/", "province_root"),
]
# 递补池 (per 655 §0.14 红线 14 沿用 654 耗尽态; 655 首试省若两级 fallback 全失败 → BLOCKED_NO_POOL 留痕)
SUBSTITUTE_POOL: list[tuple[str, list[tuple[str, str]], str]] = []
SUBSTITUTE_POOL_STATUS = "EXHAUSTED"  # per 红线 14 增补; 655 沿用 654 耗尽态

# 首试省 lineage 注解 (per 655 §0.14 红线 14 + 655 tasking §1.655-A.1)
# 无前史 → retry_of 不适用 (留空); 若 BLOCKED → 纯 BLOCKED_NO_POOL 留痕
RETRY_OF_NOTES: dict[str, str] = {
    "ningxia": "retry_of=N/A (无前史首试; per 655 §0.14)",
    "xizang": "retry_of=N/A (无前史首试; per 655 §0.14)",
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
    """Single curl fetch. Returns (http_code, reason, body)."""
    try:
        proc = subprocess.run(
            ["curl", "-sS", "-L", "--max-time", str(timeout),
             "-o", "/tmp/_655_fetch_body", "-w", "%{http_code}|%{errormsg}",
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
        body = Path("/tmp/_655_fetch_body").read_bytes()
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
        "ningxia": ["宁夏", "ningxia", "宁"],
        "xizang": ["西藏", "xizang", "藏"],
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

    Per 红线 14 沿用 654: 递补池耗尽; 两级 fallback 全失败 → BLOCKED 留痕, 不跨省代换。
    655 §0.14 首试省: 该分支代码必须存在并可达, 无论 REACHABLE 还是 BLOCKED;
    三态均合法 (双 REACHABLE → 16 INSERT + 2 NEW SHA; 混合 → 按省实报; 双 BLOCKED → 0 INSERT + 三重留痕)。
    NINGXIA/XIZANG 无前史 → retry_of 不适用 (首试省; lineage 留空留痕)。
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
                "retry_of": RETRY_OF_NOTES.get(province, ""),
            }
        # 200 + WAF marker → BLOCKED_WAF (try next)
        if code == 200 and waf_present:
            continue  # try next fallback
    # 全部 fallback chain 失败 → BLOCKED 留痕 (per 红线 14 增补; 无池可代换)
    # 真网首试省 BLOCKED_NO_POOL 留痕 (per 655 §0.14 红线 14 沿用 654; 655 双省无前史 → retry_of 不适用)
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
            f"per 655 §0.14 红线 14 增补 (沿用 654): 递补池正式耗尽 [EXHAUSTED], "
            f"无池可代换, 留痕不代换 (BLOCKED_NO_POOL 留痕首试省真网触发, per 655 §0.14). "
            f"lineage retry_of=N/A (无前史首试省; per 655 §1.655-A.1)."
        ),
        "retry_of": RETRY_OF_NOTES.get(province, ""),
    }


def main() -> int:
    http_used: list[int] = []

    # Cell 1: ningxia (首试; 无前史)
    cell_ningxia = fetch_cell("ningxia", NINGXIA_FALLBACK_CHAIN, http_used)
    # Cell 2: xizang (首试; 无前史)
    cell_xizang = fetch_cell("xizang", XIZANG_FALLBACK_CHAIN, http_used)

    cells = [cell_ningxia, cell_xizang]
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

    # 合并 fetch_log (保留每条 entry 的 attempt_province)
    fetch_log: list[dict[str, Any]] = []
    for c in cells:
        for entry in c["fetch_log"]:
            fetch_log.append(entry)  # attempt_province 已在 entry 内

    output = {
        "knife": "655-A.1",
        "purpose": (
            "M4.18 政策详情 v12 西部终章双省 spike (ningxia + xizang 第 23/24 样本; "
            "双首试省 per 655 §0.14 沿用 654 §0.14; "
            "真网首试 BLOCKED_NO_POOL 留痕概率; lineage 全 retry_of=N/A)"
        ),
        "chain_id": "real_655_m4_18_policy_detail_v12",
        "uuid_prefix": "n",
        "uuid_prefixes": {
            "source_registry": "n0eebc99",
            "source_document": "n0eebc99",
            "policy_document": "n1eebc99",
            "policy_target": "n2eebc99",
            "policy_measure": "n3eebc99",
            "government_commitment": "n4eebc99",
            "commitment_progress": "n5eebc99",
            "project_event": "n6eebc99",
        },
        "summary": {
            "fetch_status": fetch_status,
            "fetched_count": fetched_count,
            "blocked_no_pool_count": blocked_count,
            "http_count": sum(http_used),
            "http_limit": HTTP_LIMIT,
            "substitute_used_count": 0,  # 红线 14: 池耗尽, 不可能 > 0
            "substitute_pool_status": SUBSTITUTE_POOL_STATUS,
            "distinct_shas": sorted({
                c["file_hash_sha256"] for c in cells if c["file_hash_sha256"]
            }),
            "retry_of_annotation": RETRY_OF_NOTES,
        },
        "cells": cells,
        "fetch_log": fetch_log,
        "methodology": (
            "v12 西部终章双省 spike fetch: 2 cells (ningxia + xizang 第 23/24 样本; "
            "双首试省 per 655 §0.14 沿用 654 §0.14). "
            "NINGXIA 首选 https://www.nx.gov.cn/zwgk/ + fallback #1 https://www.nx.gov.cn/; "
            "XIZANG 首选 https://www.xizang.gov.cn/zwgk/ + fallback #1 https://www.xizang.gov.cn/. "
            "递补池 (SUBSTITUTE_POOL) 显式 [EXHAUSTED] (per 655 §0.14 红线 14 增补沿用 654 §0.14); "
            "两级 fallback 全失败 → BLOCKED_NO_POOL 留痕, 不跨省代换. "
            "每 cell ≤2 attempts, 总预算 ≤12 HTTP. "
            "lineage retry_of=N/A (双省无前史首试; per 655 §1.655-A.1). "
            "三态均合法 (任务书明文): 双 REACHABLE → 16 INSERT ROWS 正常落 + 2 NEW SHA; 混合 → 按省实报; 双 BLOCKED → 0 INSERT + 三重留痕 (evidence/docs/receipt). "
            "Per 650 §0.13: 附属复验/验证产物允许独立文件, 但主 evidence methodology 必须含指针. "
            "代换行 source_registry province/source_name 一律用 actual_province (per 649 P3-1). "
            "Per 655 §0.14: 首试省 BLOCKED_NO_POOL 留痕 e2e 验证 (沿用 654 §0.14 模板, docs/78 §5.2 + 655 §0.14 复试). "
            "递补池 [EXHAUSTED] 沿用 654. "
            "西部七省区全覆盖叙事终章: SHAANXI (651) + XINJIANG/NEI MENGGU (652) + GANSU/QINGHAI (654) + NINGXIA/XIZANG (655) — 651+652+654+655 四刀收官. "
            f"本次双样本结果: REACHABLE×{fetched_count} / BLOCKED_NO_POOL×{blocked_count}."
        ),
    }

    out_path = Path("evidence_pack/m4_18_policy_detail_real_v12_20260902.json")
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(
        json.dumps(output, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    print(json.dumps(output, ensure_ascii=False, indent=2))
    print(f"[OK] wrote fetch evidence to {out_path}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
