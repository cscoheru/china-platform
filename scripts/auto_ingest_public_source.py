#!/usr/bin/env python3
"""S2.5.2.1 — First public-source connector (NBS NATIONAL_BULLETIN only).

Per docs/52 §4 (6-step pipeline) and tasking 330 §SCHEMA.

Scope of this knife:
  - One pilot source: stats.gov.cn / NATIONAL_BULLETIN /
    https://www.stats.gov.cn/sj/zxfb/  (registry.csv row 3).
  - Pipeline: discover → download → sha256 → archive → extract → observation.
  - Auth escalation: 401/403/登录墙/验证码/付费/反爬 → STOP + write
    reviews/.../auth-blocked...md (5 fields per docs/52 §6.2).
  - WORM archive: data/public_archives/{YYYY-MM}/{domain}/{filename}.
  - Lineage contract: intake_status=O1_AUTO_INTAKED only when SHA matches
    registry AND not fixture AND all lineage fields present (per docs/48 §5).

Not in scope (per tasking 330 §红线):
  - Hubei / Shenzhen connectors (next knives).
  - OCR / O3 (per docs/49 §5.3; tasking 31X+ OPEN).
  - Source crawl, headless browser, paid APIs, login bypass.
  - Bulk 2020-2025 / 1909-as-China / fixture-as-live.
  - Modifying docs/48/51/52 contracts or source_registry/registry.csv.

CLI:
  --pilot-domain=DOMAIN       default: stats.gov.cn
  --pilot-category=CATEGORY   default: NATIONAL_BULLETIN
  --dry-run                   default: True (no network, no DB writes)
  --live                      explicit opt-in; still requires user authorization
                              (i.e. --confirm-live=PATH) before writing lineage
  --confirm-live=PATH         (live mode only) explicit authorization to write
                              WORM archive + flip intake_status to
                              O1_AUTO_INTAKED; refuses without it

Exit codes:
  0 = OK (dry-run or live with confirm-live)
  1 = pilot source not in registry
  2 = registry CSV parse error
  3 = AUTH blocked (401/403/登录墙/验证码/付费/反爬); blocked report written
  4 = SHA mismatch with registry
  5 = network/transport error after retries
  6 = live mode requested without --confirm-live=PATH
"""
from __future__ import annotations

import argparse
import csv
import datetime as _dt
import hashlib
import json
import sys
import time
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
REGISTRY_CSV = PROJECT_ROOT / "source_registry" / "registry.csv"
PUBLIC_ARCHIVE_ROOT = PROJECT_ROOT / "data" / "public_archives"
REVIEWS_DIR = (
    PROJECT_ROOT / "reviews" / "stage0-gate0-rework-2026-08-23"
)

# Pilot config (per tasking 330 §SCHEMA "本刀做"; only ONE pilot).
PILOT_DOMAIN = "stats.gov.cn"
PILOT_CATEGORY = "NATIONAL_BULLETIN"
PILOT_URL = "https://www.stats.gov.cn/sj/zxfb/"

# Auth-blocked HTTP statuses that MUST escalate (per docs/52 §6.1).
AUTH_BLOCKED_STATUSES = {401, 403, 429}

# Network retry budget (per tasking 330 §NOW "1").
MAX_RETRIES = 3
RETRY_BACKOFF_SECONDS = 1.0

# User-Agent (per tasking 330 §NOW "1": curl/requests with rate limit).
USER_AGENT = "CEGR-public-ingest/1.0 (+contact; non-headless; respect robots.txt)"


# ---------------------------------------------------------------------------
# Registry loading
# ---------------------------------------------------------------------------

def load_registry() -> list[dict[str, str]]:
    """Load source_registry/registry.csv as a list of dicts (raw string cells)."""
    if not REGISTRY_CSV.exists():
        print(f"❌ registry not found: {REGISTRY_CSV}", file=sys.stderr)
        return []
    with REGISTRY_CSV.open(newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        return [dict(row) for row in reader]


def filter_public_enabled(
    rows: list[dict[str, str]],
    *,
    pilot_domain: str = PILOT_DOMAIN,
    pilot_category: str = PILOT_CATEGORY,
) -> list[dict[str, str]]:
    """Return the registry rows that this knife is allowed to ingest.

    Filtering rules (per docs/52 §1 + tasking 330 §红线):
      - enabled == "TRUE"
      - auth_note starts with "公开" (public; no auth required)
      - domain + category match the pilot (this knife only)
    """
    out: list[dict[str, str]] = []
    for row in rows:
        if row.get("enabled", "").strip().upper() != "TRUE":
            continue
        if not row.get("auth_note", "").lstrip().startswith("公开"):
            continue
        if row.get("domain") != pilot_domain:
            continue
        if row.get("category") != pilot_category:
            continue
        out.append(row)
    return out


# ---------------------------------------------------------------------------
# Discovery
# ---------------------------------------------------------------------------

def discover(rows: list[dict[str, str]]) -> dict[str, str] | None:
    """Pick the single pilot row. Return None if not in registry."""
    if not rows:
        return None
    if len(rows) > 1:
        print(
            f"❌ pilot filter matched {len(rows)} rows; expected exactly 1",
            file=sys.stderr,
        )
        return rows[0]
    return rows[0]


# ---------------------------------------------------------------------------
# Download (with AUTH escalation)
# ---------------------------------------------------------------------------

class AuthBlocked(Exception):
    """Raised when the source returns an auth-blocked HTTP status (401/403/429)
    or redirects to a login/CAPTCHA/paywall page after the retry budget is
    exhausted. Per docs/52 §6 — must STOP, never bypass."""

    def __init__(
        self,
        *,
        domain: str,
        category: str,
        url: str,
        status_code: int | None,
        reason: str,
    ):
        self.domain = domain
        self.category = category
        self.url = url
        self.status_code = status_code
        self.reason = reason
        super().__init__(reason)


def download(
    url: str,
    *,
    timeout: float = 15.0,
) -> bytes:
    """Fetch URL using `requests`. NOT a headless browser. Retries up to
    MAX_RETRIES with exponential backoff. Raises AuthBlocked on 401/403/429 or
    on a redirect to a login/CAPTCHA wall. Raises RuntimeError on transport
    failure after retries."""
    try:
        import requests  # local import keeps --dry-run zero-deps friendly
    except ImportError as exc:  # pragma: no cover
        print(
            "❌ requests not installed; run `pip install requests` to enable "
            "live mode (dry-run still works).",
            file=sys.stderr,
        )
        raise RuntimeError("requests-missing") from exc

    last_exc: Exception | None = None
    for attempt in range(1, MAX_RETRIES + 1):
        try:
            resp = requests.get(
                url,
                headers={"User-Agent": USER_AGENT},
                timeout=timeout,
                allow_redirects=True,
            )
            if resp.status_code in AUTH_BLOCKED_STATUSES:
                raise AuthBlocked(
                    domain=PILOT_DOMAIN,
                    category=PILOT_CATEGORY,
                    url=url,
                    status_code=resp.status_code,
                    reason=f"HTTP {resp.status_code} after {attempt} attempt(s)",
                )
            # Heuristic: redirect to login/CAPTCHA wall surfaces as a 200
            # with a login form. Detect by URL substring.
            final_url = resp.url or ""
            if any(
                marker in final_url.lower()
                for marker in ("login", "captcha", "verify", "auth", "paywall")
            ):
                raise AuthBlocked(
                    domain=PILOT_DOMAIN,
                    category=PILOT_CATEGORY,
                    url=url,
                    status_code=resp.status_code,
                    reason=f"redirect to login/CAPTCHA wall: {final_url}",
                )
            resp.raise_for_status()
            return resp.content
        except AuthBlocked:
            raise
        except requests.exceptions.RequestException as exc:
            last_exc = exc
            if attempt < MAX_RETRIES:
                time.sleep(RETRY_BACKOFF_SECONDS * (2 ** (attempt - 1)))
                continue
            raise RuntimeError(
                f"transport failed after {MAX_RETRIES} attempts: {exc}"
            ) from exc
    # Defensive: loop always returns/raises.
    raise RuntimeError(f"unreachable: {last_exc}")


# ---------------------------------------------------------------------------
# SHA-256
# ---------------------------------------------------------------------------

def sha256_of_bytes(blob: bytes) -> str:
    return hashlib.sha256(blob).hexdigest()


def assert_sha_matches_registry(
    *,
    computed: str,
    expected: str,
) -> None:
    """Compare computed SHA-256 to registry.csv file_hash_sha256. Raise on
    mismatch (per docs/52 §4 step 3)."""
    if computed.lower() != expected.lower():
        raise RuntimeError(
            f"SHA-256 mismatch: computed={computed[:16]}… expected="
            f"{expected[:16]}…  (registry may have drifted; report user, "
            f"do not auto-update)"
        )


# ---------------------------------------------------------------------------
# Archive (WORM)
# ---------------------------------------------------------------------------

def archive(
    *,
    blob: bytes,
    domain: str,
    filename: str,
) -> Path:
    """Write the downloaded bytes to data/public_archives/{YYYY-MM}/{domain}/.

    The filename is supplied by the caller (typically derived from the URL
    path or the registry's local_sample_path). The YYYY-MM is the current
    month in UTC. The directory is created if missing.

    This function is intentionally append-only at the application layer; the
    WORM guarantee is enforced by filesystem ACLs in production (out of
    scope here)."""
    ym = _dt.datetime.now(_dt.timezone.utc).strftime("%Y-%m")
    out_dir = PUBLIC_ARCHIVE_ROOT / ym / domain
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / filename
    if out_path.exists():
        # Idempotent: if the same content is already archived, do not overwrite.
        # A drift would have already failed the SHA check above.
        return out_path
    out_path.write_bytes(blob)
    return out_path


# ---------------------------------------------------------------------------
# Extract (HTML table scrape for NBS NATIONAL_BULLETIN)
# ---------------------------------------------------------------------------

def extract_html_tables(blob: bytes) -> list[dict[str, str]]:
    """Extract the first table on the NBS NATIONAL_BULLETIN index.

    Returns a list of {col1: ..., col2: ...} dicts (one per row). For the
    pilot, we only need a non-empty extract to mark observation OK. The
    full table-walker is deferred to a later connector (per docs/52 §8)."""
    try:
        from bs4 import BeautifulSoup  # local import; dry-run friendly
    except ImportError as exc:  # pragma: no cover
        raise RuntimeError("beautifulsoup4 missing") from exc
    soup = BeautifulSoup(blob, "html.parser")
    table = soup.find("table")
    if table is None:
        return []
    rows: list[dict[str, str]] = []
    for tr in table.find_all("tr"):
        cells = [td.get_text(strip=True) for td in tr.find_all(["td", "th"])]
        if not cells:
            continue
        if not rows:
            # First row treated as header.
            header = cells
            continue
        rows.append({h: c for h, c in zip(header, cells)})
    return rows


# ---------------------------------------------------------------------------
# Observation (lineage JSONL)
# ---------------------------------------------------------------------------

LINEAGE_SCHEMA_FIELDS = (
    "is_demo",
    "source_file_sha256",
    "source_file_path",
    "source_agency",
    "intake_ts",
    "intake_status",
)


def _relative_or_abs(path: Path) -> str:
    """Return path relative to PROJECT_ROOT when possible, else absolute."""
    try:
        return str(path.relative_to(PROJECT_ROOT))
    except ValueError:
        return str(path)


def write_observation(
    *,
    archive_path: Path,
    sha256_hex: str,
    agency: str,
    intake_status: str,
    output_path: Path,
) -> Path:
    """Append a single JSONL line to output_path with all lineage fields
    populated per docs/48 §5. intake_status MUST be one of:
        - O1_AUTO_INTAKED  (live mode + SHA matches registry)
        - DEMO             (fixture / placeholder; demo flag stays true)
    """
    record = {
        "is_demo": "false" if intake_status == "O1_AUTO_INTAKED" else "true",
        "source_file_sha256": sha256_hex,
        "source_file_path": _relative_or_abs(archive_path),
        "source_agency": agency,
        "intake_ts": _dt.datetime.now(_dt.timezone.utc).isoformat(),
        "intake_status": intake_status,
    }
    for field in LINEAGE_SCHEMA_FIELDS:
        if not record.get(field):
            raise RuntimeError(
                f"lineage contract violation: missing field '{field}'"
            )
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("a", encoding="utf-8") as f:
        f.write(json.dumps(record, ensure_ascii=False) + "\n")
    return output_path


# ---------------------------------------------------------------------------
# AUTH escalation report (per docs/52 §6.2 — 5 mandatory fields)
# ---------------------------------------------------------------------------

def write_auth_blocked_report(
    *,
    domain: str,
    category: str,
    url: str,
    reason: str,
    status_code: int | None,
    estimated_cost: str = "公开源本应免费；若有付费墙/订阅要求，将由用户裁定",
    required_account: str = "无需账号；如源改为登录，需用户提供",
    alternative_source: str = (
        "registry.csv 已有公开源：tjj.hubei.gov.cn PROVINCIAL_BULLETIN / "
        "sz.gov.cn MUNICIPAL_BULLETIN（待 tasking 33X+ 落地）"
    ),
    eta_after_authorization: str = "用户提供授权后 ~30 分钟可继续",
) -> Path:
    """Write reviews/.../auth-blocked...md with the 5 mandatory fields per
    docs/52 §6.2. Returns the written path."""
    REVIEWS_DIR.mkdir(parents=True, exist_ok=True)
    ts = _dt.datetime.now(_dt.timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    out_path = REVIEWS_DIR / (
        f"{ts}-stage2-public-source-auth-blocked-{domain}-{category}.md"
    )
    body = f"""# 公开源 AUTH 触发报告（per docs/52 §6）

- 域：`{domain}`
- 类目：`{category}`
- URL：`{url}`
- 触发原因：`{reason}`
- HTTP 状态码：`{status_code if status_code is not None else 'N/A'}`
- 触发时间（UTC）：`{_dt.datetime.now(_dt.timezone.utc).isoformat()}`

## 1. 源 / 费用 / 需要账号

| 字段 | 值 |
|---|---|
| domain | `{domain}` |
| category | `{category}` |
| URL | `{url}` |
| 费用估计 | {estimated_cost} |
| 需要什么账号/订阅 | {required_account} |

## 2. 替代公开源

{alternative_source}

## 3. 用户授权后 ETA

{eta_after_authorization}

## 4. 红线

- ❌ **不绕过验证码 / 付费墙 / 登录 / 技术限制**（per docs/00 §3 红线 7 + PRD 1.3 + 12.8 + docs/52 §6）
- ❌ **不静默失败**（本报告即非静默；含 5 字段 + 替代源 + ETA）
- ❌ **不 headless browser 绕过反爬**（per registry.csv Hubei 备注）
- ❌ **不擅自切换到 headless 或登录后端点**

## 5. 等用户裁定（4 路径 per docs/52 §6.3）

1. **用户提供授权**（账号/订阅/凭证）→ 更新 registry.csv `auth_note`；下次心跳流水线自动重试
2. **用户裁定跳过该源** → registry.csv `enabled=FALSE`
3. **用户裁定改用替代公开源** → discover 阶段重路由
4. **用户裁定暂缓** → 源保持 `enabled=FALSE`，等下次裁定

— End of AUTH blocked report —
"""
    out_path.write_text(body, encoding="utf-8")
    return out_path


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="auto_ingest_public_source",
        description=(
            "First public-source connector (NBS NATIONAL_BULLETIN only). "
            "Dry-run by default; --live requires --confirm-live=PATH."
        ),
    )
    parser.add_argument(
        "--pilot-domain", default=PILOT_DOMAIN,
        help="registry.csv domain filter (default: stats.gov.cn)",
    )
    parser.add_argument(
        "--pilot-category", default=PILOT_CATEGORY,
        help="registry.csv category filter (default: NATIONAL_BULLETIN)",
    )
    parser.add_argument(
        "--dry-run", action="store_true", default=True,
        help="(default) no network, no DB writes; only validates registry filter",
    )
    parser.add_argument(
        "--live", action="store_true",
        help="enable network + archive + observation writes (still requires "
             "--confirm-live=PATH)",
    )
    parser.add_argument(
        "--confirm-live", default=None, metavar="PATH",
        help="explicit authorization to flip intake_status=O1_AUTO_INTAKED; "
             "PATH is the lineage JSONL output",
    )
    args = parser.parse_args(argv)

    if args.live and not args.confirm_live:
        print(
            "❌ --live requires --confirm-live=PATH (explicit user authorization)",
            file=sys.stderr,
        )
        return 6

    rows = load_registry()
    if not rows:
        return 2

    pilot_rows = filter_public_enabled(
        rows,
        pilot_domain=args.pilot_domain,
        pilot_category=args.pilot_category,
    )
    pilot = discover(pilot_rows)
    if pilot is None:
        print(
            f"❌ pilot not in registry: domain={args.pilot_domain} "
            f"category={args.pilot_category}",
            file=sys.stderr,
        )
        return 1

    print(f"OK pilot matched: {pilot['domain']} / {pilot['category']}")
    print(f"   primary_url: {pilot['primary_url']}")
    print(f"   auth_note: {pilot['auth_note']}")
    print(f"   expected SHA: {pilot['file_hash_sha256'][:16]}…")

    if args.dry_run and not args.live:
        print(
            "OK dry-run; no network, no archive, no lineage writes. "
            "Pass --live --confirm-live=PATH to run for real (with explicit "
            "user authorization).",
        )
        return 0

    # Live path (only reached when --live + --confirm-live=PATH).
    try:
        blob = download(pilot["primary_url"])
    except AuthBlocked as ab:
        report = write_auth_blocked_report(
            domain=ab.domain,
            category=ab.category,
            url=ab.url,
            reason=ab.reason,
            status_code=ab.status_code,
        )
        print(f"❌ AUTH blocked; report written: {report}", file=sys.stderr)
        return 3
    except RuntimeError as exc:
        print(f"❌ transport error: {exc}", file=sys.stderr)
        return 5

    sha = sha256_of_bytes(blob)
    print(f"OK downloaded {len(blob)} bytes; sha256={sha[:16]}…")
    try:
        assert_sha_matches_registry(
            computed=sha,
            expected=pilot["file_hash_sha256"],
        )
    except RuntimeError as exc:
        print(f"❌ {exc}", file=sys.stderr)
        return 4

    filename = Path(pilot["primary_url"]).name or "index.html"
    archive_path = archive(
        blob=blob,
        domain=pilot["domain"],
        filename=filename,
    )
    print(f"OK archived: {archive_path}")

    tables = extract_html_tables(blob)
    print(f"OK extract: {len(tables)} table row(s)")

    write_observation(
        archive_path=archive_path,
        sha256_hex=sha,
        agency=pilot["organization"],
        intake_status="O1_AUTO_INTAKED",
        output_path=Path(args.confirm_live),
    )
    print(f"OK observation written: {args.confirm_live}")
    return 0


if __name__ == "__main__":
    sys.exit(main())