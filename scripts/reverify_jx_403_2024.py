"""648-A.0 — jiangxi "403" 复验 (1×HTTP re-fetch + SHA 对比 + 内容锚点).

Per knife 648 §1.648-A.0 (647 审计 P3-1 处置):
- 1×HTTP re-fetch https://www.jiangxi.gov.cn/zwgk/
- SHA 对比 vs 原值 `56481050c810fbeec004ff68478d9f291c5eda39e005ec09e3fb6122dc28edd4`
  (来自 647 fetch_log)
- 内容锚点: <title> + DATE_RE + 关键 body 标识 (江西/jiangxi/政务公开/zfgb 等)
- 一致=CONTENT_CONFIRMED 注记 (append, 不删行)
- 不一致=docs/52 (a) drift 登记 + 评估换样

不消耗 648-A.1 M4.11 side HTTP quota (≤12); 仅 1×HTTP for reverify。

OUTPUT:
  evidence_pack/m4_10_reverify_jx_20260901.json
"""
from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path

from _probe_http_helpers import fetch, now_utc_iso

REPO_ROOT = Path(__file__).resolve().parent.parent
EVIDENCE_JSON = REPO_ROOT / "evidence_pack" / "m4_10_reverify_jx_20260901.json"

# 647 fetch 实际 SHA (per evidence_pack/m4_10_policy_detail_real_v4_20260901.json cell 2)
ORIGINAL_SHA = "56481050c810fbeec004ff68478d9f291c5eda39e005ec09e3fb6122dc28edd4"
URL = "https://www.jiangxi.gov.cn/zwgk/"
DATE_RE = re.compile(r"(20\d{2}[-年]\d{1,2}[-月]\d{1,2})", re.IGNORECASE)
# 内容锚点正则: 检测页面是否仍为江西政务公开目录
ANCHOR_RE = re.compile(
    r"江西|jiangxi|政务公开|政府公报|政府文件|政策法规|公开目录|领导信息",
    re.IGNORECASE,
)
WAF_BLOCK_RE = re.compile(r"403 Forbidden|WAF|网防G01|eventID", re.IGNORECASE)


def parse_anchors(html: bytes) -> dict:
    text = html.decode("utf-8", errors="replace")
    title = ""
    tm = re.search(r"<title[^>]*>([^<]{2,200}?)</title>", text, re.IGNORECASE)
    if tm:
        title = tm.group(1).strip()
        title = re.sub(r"\s*[|\-_—－]\s*[^|\-_—－]*$", "", title).strip()
    pub_date = ""
    pm = DATE_RE.search(text)
    if pm:
        pub_date = pm.group(1).replace("年", "-").replace("月", "-")
    anchor_hits = ANCHOR_RE.findall(text)
    waf_hit = bool(WAF_BLOCK_RE.search(text))
    return {
        "title": title,
        "publication_date": pub_date,
        "file_size_bytes": len(html),
        "anchor_hits_count": len(anchor_hits),
        "anchor_hits_sample": anchor_hits[:5],
        "waf_marker_present": waf_hit,
        "body_char_count": len(text),
    }


def run_reverify() -> dict:
    # 1×HTTP re-fetch
    code, reason, body = fetch(URL, timeout=15)
    fetched_at = now_utc_iso()
    sha = hashlib.sha256(body).hexdigest()
    anchors = parse_anchors(body)
    sha_match = sha == ORIGINAL_SHA
    # CONTENT_CONFIRMED 判定条件: sha 一致 + (title 包含江西或 anchor 命中 ≥1)
    is_content_anchored = (
        "江西" in anchors["title"] or anchors["anchor_hits_count"] >= 1
    )
    content_confirmed = sha_match and is_content_anchored
    if content_confirmed:
        verdict = "CONTENT_CONFIRMED"
    elif not sha_match:
        verdict = "DRIFT_SHA_MISMATCH"
    elif not is_content_anchored:
        verdict = "DRIFT_CONTENT_ANCHOR_LOST"
    else:
        verdict = "AMBIGUOUS"
    return {
        "generated_at": fetched_at,
        "knife": "648-A.0",
        "purpose": "jiangxi '403' 复验 per 647 审计 P3-1 处置",
        "url": URL,
        "original_sha256": ORIGINAL_SHA,
        "fetch": {
            "http_code": code,
            "reason": reason,
            "fetched_at": fetched_at,
        },
        "new_sha256": sha,
        "sha_match": sha_match,
        "anchors": anchors,
        "is_content_anchored": is_content_anchored,
        "verdict": verdict,
    }


def write_outputs(results: dict) -> None:
    EVIDENCE_JSON.parent.mkdir(parents=True, exist_ok=True)
    EVIDENCE_JSON.write_text(
        json.dumps(results, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )


def main() -> int:
    results = run_reverify()
    write_outputs(results)
    print(
        f"648-A.0 jiangxi reverify: verdict={results['verdict']} "
        f"sha_match={results['sha_match']} "
        f"http_code={results['fetch']['http_code']} "
        f"size={results['anchors']['file_size_bytes']}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())