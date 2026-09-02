"""M4.16 政策详情 v10 双复试 spike fetch (knife 653 §A.1, 2026-09-02).

Per knife 653 tasking §1.653-A.1:
- 2 真实样本: SHANDONG + HUBEI (第 19/20 样本; 双 BLOCKED 史省复试)
- SHANDONG 首选: https://www.shandong.gov.cn/zwgk/ ; fallback #1: https://www.shandong.gov.cn/
- HUBEI 首选: https://www.hubei.gov.cn/zwgk/ ; fallback #1: https://www.hubei.gov.cn/
- 复试缘起: 647 shandong 4 连 BLOCKED 史 (域名错配+403); 649 hubei 412×2 史 (槽被代换 actual=LIAONING)
- 双样本两级均 BLOCKED → **真网首次 BLOCKED_NO_POOL 留痕** (per 红线 14 沿用 652; 653 §0.14 复试)
  - 注: 任一 REACHABLE 也属合法 (REACHABLE 落 evidence, 不强求 BLOCKED)
  - 两态均收官价值高: 真触发 = 首次真网 BLOCKED 留痕; REACHABLE = SHANDONG/HUBEI 以 actual 入集 (消 647/649 槽名遗留, 已用省 18→20)
- lineage 全 retry_of 字段: shandong ← 647 BLOCKED×4; hubei ← 649 substituted actual=LIAONING
- chain_id = 'real_653_m4_16_policy_detail_v10' (末段 `_v10` ≠ 652 `_v9` ≠ 651 `_v8`)
- UUID l 段 (l0eebc99-l6eebc99) ≠ 652 k 段 ≠ 651 j 段 ≠ 650 i 段
- 已用省全集 (不得重复, 按 actual_province 口径, 18 省):
  HLJ/HENAN/YUNNAN/FUJIAN/GD/ZJ/JX/HUN/AH/LN/JL/GUIZHOU/JIANGSU/SHAANXI/SICHUAN/XINJIANG/NEI MENGGU
  653 增量后 = 19/20 省 (若双样本均 REACHABLE)
- 2 NEW SHA 全 distinct ≠ 638-652 全部 SHA (或 BLOCKED cell 留 blocked_reason 无 SHA)
- lineage 全 is_demo='false' 真实化 sentinel + 全行 retry_of (per docs/33 §3.2)
- ≤12 HTTP total (per 653 §0.3 红线 3 + 全刀预期 4-8)
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
SHANDONG_FALLBACK_CHAIN: list[tuple[str, str]] = [
    ("https://www.shandong.gov.cn/zwgk/", "zwgk_root"),
    ("https://www.shandong.gov.cn/", "province_root"),
]
HUBEI_FALLBACK_CHAIN: list[tuple[str, str]] = [
    ("https://www.hubei.gov.cn/zwgk/", "zwgk_root"),
    ("https://www.hubei.gov.cn/", "province_root"),
]
# 递补池 (per 653 §0.14 红线 14 沿用 652 耗尽态; 653 复试若两级 fallback 全失败 → 真网首次 BLOCKED_NO_POOL 留痕)
SUBSTITUTE_POOL: list[tuple[str, list[tuple[str, str]], str]] = []
SUBSTITUTE_POOL_STATUS = "EXHAUSTED"  # per 红线 14 增补; 653 沿用 652 耗尽态

# 复试 lineage 注解 (per 653 §0.14 红线 14 沿用 + 653 tasking §1.653-A.1)
RETRY_OF_NOTES: dict[str, str] = {
    "shandong": "retry_of=647 (BLOCKED×4: 域名错配+403)",
    "hubei": "retry_of=649 (412×2 史, 槽被代换 actual=LIAONING)",
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
             "-o", "/tmp/_653_fetch_body", "-w", "%{http_code}|%{errormsg}",
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
        body = Path("/tmp/_653_fetch_body").read_bytes()
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
        "shandong": ["山东", "shandong", "鲁"],
        "hubei": ["湖北", "hubei", "鄂"],
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

    Per 红线 14 沿用 652: 递补池耗尽; 两级 fallback 全失败 → BLOCKED 留痕, 不跨省代换。
    653 §0.14 复试: 该分支代码必须存在并可达, 无论 REACHABLE 还是 BLOCKED;
    两态均合法, lineage 全行 retry_of 字段。

    Returns cell with:
    - province: original requested province
    - actual_province: where data was actually fetched from (= province since no substitute)
    - retry_of: per RED_LINE_14 lineage annotation
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
                "retry_of": RETRY_OF_NOTES.get(province, ""),
            }
        # 200 + WAF marker → BLOCKED_WAF (try next)
        if code == 200 and waf_present:
            continue  # try next fallback
    # 全部 fallback chain 失败 → BLOCKED 留痕 (per 红线 14 增补; 无池可代换)
    # 真网首次 BLOCKED_NO_POOL 留痕 (per 653 §0.14 复试 + 沿用 652 §0.14 红线 14 沿用)
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
            f"per 653 §0.14 红线 14 增补 (沿用 652): 递补池正式耗尽 [EXHAUSTED], "
            f"无池可代换, 留痕不代换 (BLOCKED_NO_POOL 留痕真网首次触发, per 653 §0.14 复试)"
        ),
        "retry_of": RETRY_OF_NOTES.get(province, ""),
    }


def main() -> int:
    http_used: list[int] = []

    # Cell 1: shandong (复试; 647 4 连 BLOCKED 史)
    cell_shandong = fetch_cell("shandong", SHANDONG_FALLBACK_CHAIN, http_used)
    # Cell 2: hubei (复试; 649 412×2 史, 槽被代换 actual=LIAONING)
    cell_hubei = fetch_cell("hubei", HUBEI_FALLBACK_CHAIN, http_used)

    cells = [cell_shandong, cell_hubei]
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
        "knife": "653-A.1",
        "purpose": (
            "M4.16 政策详情 v10 双复试 spike (shandong + hubei 第 19/20 样本; "
            "双 BLOCKED 史省复试 per 653 §0.14 沿用 652 §0.14; "
            "真网 BLOCKED_NO_POOL 首触发最佳概率; lineage 全 retry_of)"
        ),
        "chain_id": "real_653_m4_16_policy_detail_v10",
        "uuid_prefix": "l",
        "uuid_prefixes": {
            "source_registry": "l0eebc99",
            "source_document": "l0eebc99",
            "policy_document": "l1eebc99",
            "policy_target": "l2eebc99",
            "policy_measure": "l3eebc99",
            "government_commitment": "l4eebc99",
            "commitment_progress": "l5eebc99",
            "project_event": "l6eebc99",
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
            "v10 双复试 spike fetch: 2 cells (shandong + hubei 第 19/20 样本; "
            "双 BLOCKED 史省复试). "
            "SHANDONG 首选 https://www.shandong.gov.cn/zwgk/ + fallback #1 https://www.shandong.gov.cn/ (复试 647 4 连 BLOCKED 史: 域名错配+403); "
            "HUBEI 首选 https://www.hubei.gov.cn/zwgk/ + fallback #1 https://www.hubei.gov.cn/ (复试 649 412×2 史: 槽被代换 actual=LIAONING). "
            "递补池 (SUBSTITUTE_POOL) 显式 [EXHAUSTED] (per 653 §0.14 红线 14 增补沿用 652 §0.14); "
            "两级 fallback 全失败 → BLOCKED_NO_POOL 留痕, 不跨省代换. "
            "每 cell ≤2 attempts, 总预算 ≤12 HTTP. "
            "lineage 全 retry_of 字段: shandong ← 647 BLOCKED×4; hubei ← 649 substituted actual=LIAONING. "
            "两态均合法 (任务书明文): 双 REACHABLE → 16 INSERT ROWS 正常落; 任一 BLOCKED → 该省 0 INSERT + cell 占位 + blocked_reason + 另一省正常落. "
            "Per 650 §0.13: 附属复验/验证产物允许独立文件, 但主 evidence methodology 必须含指针. "
            "代换行 source_registry province/source_name 一律用 actual_province (per 649 P3-1). "
            "Per 653 §0.14: 复试 BLOCKED_NO_POOL 留痕 e2e 验证 (沿用 652 §0.14 模板, docs/76 §5.2). "
            "递补池 [EXHAUSTED] 沿用 652. "
            f"本次双样本结果: REACHABLE×{fetched_count} / BLOCKED_NO_POOL×{blocked_count}."
        ),
    }

    out_path = Path("evidence_pack/m4_16_policy_detail_real_v10_20260902.json")
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(
        json.dumps(output, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    print(json.dumps(output, ensure_ascii=False, indent=2))
    print(f"[OK] wrote fetch evidence to {out_path}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
