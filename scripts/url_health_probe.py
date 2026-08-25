"""Stage 1 / S1.17 — URL 健康探针 CLI (R12).

Per docs/32-stage1-s17-r12-url-health-plan-20260825.md §2.1–§2.3 + tasking 127.

Probe every `source_registry.enabled = TRUE` row's `primary_url` (and
`backup_urls[]` when present) with HEAD (default) or GET-Range-bytes-0-1023
fallback. Classify each response per §2.2 → write one synthetic
`cegr.ingestion_run` row per URL (triggered_by='url_health_probe'). Aggregate
exit code per §2.3.

CLI:
  python3 scripts/url_health_probe.py [--dsn DSN] [--max-runtime 60]
                                      [--url URL ...] [--quiet]

If `--url` is given, probe those URLs against a registry id (one URL only
allowed for synthetic runs); default mode scans `source_registry`.

Constraints (钉死 per docs/32 §2.1 + Cursor 127 §红线):
  * HEAD 默认；GET Range bytes=0-1023 仅在 HEAD 不支持 / 失败时降级
  * 每源 ≤1 req/s；总表 ≤60s
  * 不绕验证码 / 付费墙 / 登录（特征字符串 → PARTIAL）
  * 不写 source_document / observation（per IngestMonitor §只读原则）

Read-only on the rest of `source_registry`; writes only to `ingestion_run`.
"""
from __future__ import annotations

import argparse
import os
import re
import sys
import time
import uuid
from typing import Iterable

import psycopg2
import requests

CAPTCHA_PATTERNS = (
    re.compile(r"captcha", re.IGNORECASE),
    re.compile(r"paywall", re.IGNORECASE),
    re.compile(r"login\s+required", re.IGNORECASE),
)


def _dsn(arg_dsn: str | None) -> str:
    """Resolve DSN: --dsn > CEGR_DSN > DATABASE_URL > local test default."""
    return (
        arg_dsn
        or os.environ.get("CEGR_DSN")
        or os.environ.get("DATABASE_URL")
        or "postgresql://postgres:postgres@127.0.0.1:55440/cegr_test"
    )


def _is_captcha_or_paywall(body: str) -> bool:
    """Detect captcha / paywall / login-required in response body.

    Triggers on first match. Body should be ≤1KB (per docs/32 §2.1 GET Range).
    """
    if not body:
        return False
    for pat in CAPTCHA_PATTERNS:
        if pat.search(body):
            return True
    return False


def _probe_url(session: requests.Session, url: str,
               timeout_total: float = 15.0) -> tuple[str, str | None]:
    """Probe a single URL. Returns (status, error_log).

    status ∈ {'SUCCESS', 'FAILED', 'PARTIAL'}. error_log = first 200 chars
    on FAILED, 'captcha_or_paywall_detected' on PARTIAL, else None.

    Probe order (per docs/32 §2.1):
      1. HEAD (default)
      2. GET Range: bytes=0-1023 (only if HEAD returned 4xx 'method not
         supported'-style code; **not** on network errors — if HEAD DNS
         fails, GET would also DNS-fail, so we short-circuit to FAILED).
    """
    try:
        r = session.head(url, timeout=(5, 10), allow_redirects=True)
    except requests.RequestException as e:
        # Network/DNS/SSL error → do not try GET (would also fail)
        return "FAILED", f"HEAD: {type(e).__name__}: {str(e)[:120]}"

    code = r.status_code
    if 200 <= code < 400:
        return "SUCCESS", None

    # HEAD responded but with non-2xx; only fall back to GET when the
    # response indicates HEAD unsupported (405 / 501). Other 4xx/5xx → FAILED.
    if code not in (405, 501):
        return "FAILED", f"HEAD: HTTP {code}"

    # Fallback: GET Range bytes=0-1023
    try:
        r = session.get(
            url, timeout=(5, 10), allow_redirects=True,
            headers={"Range": "bytes=0-1023"},
        )
        body = (r.content or b"")[:1024].decode("utf-8", errors="ignore")
        if _is_captcha_or_paywall(body):
            return "PARTIAL", "captcha_or_paywall_detected"
        gcode = r.status_code
        if 200 <= gcode < 400:
            return "SUCCESS", None
        return "FAILED", f"GET_Range: HTTP {gcode}"
    except requests.RequestException as e:
        return "FAILED", f"GET_Range: {type(e).__name__}: {str(e)[:120]}"


def _iter_registry_urls(conn) -> Iterable[tuple[uuid.UUID, str, str]]:
    """Yield (source_registry_id, role, url) for every enabled source.

    role ∈ {'primary', 'backup'}. Each URL gets its own ingestion_run row.
    """
    with conn.cursor() as cur:
        cur.execute("""
            SELECT id, primary_url, backup_urls
            FROM cegr.source_registry
            WHERE enabled = TRUE
            ORDER BY id
        """)
        for reg_id, primary, backups in cur.fetchall():
            yield reg_id, "primary", primary
            for url in (backups or []):
                yield reg_id, "backup", url


def _write_run(conn, source_registry_id: uuid.UUID, status: str,
               error_log: str | None, triggered_by: str = "url_health_probe"
               ) -> None:
    """Insert one synthetic ingestion_run row.

    Per docs/32 §2.2: started_at = finished_at (synthetic, no work duration).
    """
    with conn.cursor() as cur:
        cur.execute(
            """
            INSERT INTO cegr.ingestion_run
                (id, source_registry_id, started_at, finished_at, status,
                 records_extracted, records_inserted, error_log, triggered_by)
            VALUES (%s, %s, NOW(), NOW(), %s, 0, 0, %s, %s)
            """,
            (
                uuid.uuid4(),
                str(source_registry_id),
                status,
                (error_log[:200] if error_log else None),
                triggered_by,
            ),
        )


def probe_all(dsn: str, max_runtime: float = 60.0,
              quiet: bool = False) -> int:
    """Probe every enabled source_registry URL. Returns aggregate exit code."""
    started = time.monotonic()
    deadline = started + max_runtime
    counts = {"SUCCESS": 0, "FAILED": 0, "PARTIAL": 0}
    with requests.Session() as session, psycopg2.connect(dsn) as conn:
        for reg_id, role, url in _iter_registry_urls(conn):
            if time.monotonic() >= deadline:
                if not quiet:
                    print(f"[url_health] hit runtime cap {max_runtime}s; stopping",
                          file=sys.stderr)
                break
            status, error_log = _probe_url(session, url)
            counts[status] += 1
            _write_run(conn, reg_id, status, error_log)
            if not quiet:
                print(f"[url_health] {status} {role} {url} "
                      f"{('err=' + error_log) if error_log else ''}")
            # Per-source throttle ≤1 req/s (per docs/32 §2.1)
            time.sleep(1.0)
        conn.commit()

    failed = counts["FAILED"]
    partial = counts["PARTIAL"]
    success = counts["SUCCESS"]
    if failed and partial:
        exit_code = 3
    elif failed:
        exit_code = 1
    elif partial:
        exit_code = 2
    else:
        exit_code = 0
    if not quiet:
        print(f"[url_health] done: success={success} failed={failed} "
              f"partial={partial} exit={exit_code}")
    return exit_code


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description="S1.17 URL 健康探针 (R12)")
    p.add_argument("--dsn", default=None,
                   help="Postgres DSN (default: CEGR_DSN / DATABASE_URL / test DB)")
    p.add_argument("--max-runtime", type=float, default=60.0,
                   help="Total runtime cap in seconds (default: 60)")
    p.add_argument("--url", default=None,
                   help="(test hook) single URL override; not used in prod scan")
    p.add_argument("--quiet", action="store_true",
                   help="Suppress per-URL stdout lines")
    args = p.parse_args(argv)
    dsn = _dsn(args.dsn)
    if args.url:
        # Test hook: probe one URL against a sentinel registry id; used by
        # pytest wrapper to verify classification logic without DB scan.
        with requests.Session() as session:
            status, err = _probe_url(session, args.url)
        print(f"[url_health] single {status} {args.url} "
              f"{('err=' + err) if err else ''}")
        return {"SUCCESS": 0, "FAILED": 1, "PARTIAL": 2}[status]
    return probe_all(dsn, max_runtime=args.max_runtime, quiet=args.quiet)


if __name__ == "__main__":
    sys.exit(main())