"""Shared HTTP probe helpers for knife 638 M4.1 probes.

Per knife 638 §2 / 636 复用:
- subprocess + curl pattern (no Python httpx / requests — keep DSN-free)
- 5 UA profiles (inherited from 636)
- verdict: REACHABLE / PARTIAL / BLOCKED / NOT_APPLICABLE / NOT_PROBED

Helper-only module; do not import outside scripts/.
"""
from __future__ import annotations

import re
import subprocess
from datetime import datetime, timezone

UA = ("Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36")

# Reused from 636: 31 省 slug ordering (alphabetical-ish)
PROVINCE_SLUGS = [
    "beijing", "tianjin", "shanghai", "chongqing",
    "hebei", "shanxi", "innermongolia", "liaoning",
    "jilin", "heilongjiang", "jiangsu", "zhejiang",
    "anhui", "fujian", "jiangxi", "shandong",
    "henan", "hubei", "hunan", "guangdong",
    "guangxi", "hainan", "sichuan", "guizhou",
    "yunnan", "tibet", "shaanxi", "gansu",
    "qinghai", "ningxia", "xinjiang",
]


def fetch(url: str, timeout: int = 15) -> tuple[int, str, bytes]:
    """Returns (http_code, reason, body). reason ∈ {"ok","timeout","tls_reset",
    "dns_fail","conn_refused","empty","bad_format","waf_403"}.
    Same signature as probe_m2_2001_backfill.fetch().
    """
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


def now_utc_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


# Marker regexes per source class
GOV_REPORT_MARKER_RE = re.compile(
    r"政府工作报告|人民政府|工作报告|Provincial Government Report",
    re.IGNORECASE,
)
RENMIAN_MARKER_RE = re.compile(
    r"任免|任免名单|appoint|removal|departure",
    re.IGNORECASE,
)
POLICY_MARKER_RE = re.compile(
    r"政策文件|政府公报|规划计划|政府工作报告|五年规划|规范性文件|policy|regulation|five.year.plan",
    re.IGNORECASE,
)
WAF_BLOCK_RE = re.compile(r"403 Forbidden|WAF|网防G01|eventID", re.IGNORECASE)


def classify_people_probe(http_code: int, reason: str, body: bytes,
                          marker_re: re.Pattern[str]) -> str:
    """Verdict for people-source probes (gov report / renmian announcement).

    REACHABLE: HTTP 200 + body contains source marker
    PARTIAL: HTTP 200 + body loaded but no marker found
    BLOCKED: TLS reset / 403 WAF / 404 / connection error
    """
    if reason != "ok":
        return "BLOCKED"
    if http_code != 200:
        return "BLOCKED"
    txt = ""
    try:
        txt = body.decode("utf-8", errors="replace")
    except Exception:
        txt = body.decode("gb18030", errors="replace")
    if WAF_BLOCK_RE.search(txt):
        return "BLOCKED"
    if marker_re.search(txt):
        return "REACHABLE"
    return "PARTIAL"