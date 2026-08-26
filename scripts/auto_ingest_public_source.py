#!/usr/bin/env python3
"""S2.5.2.1 — First public-source connector (NBS NATIONAL_BULLETIN only).

Per docs/52 §4 (6-step pipeline) and tasking 330 §SCHEMA.

Scope of this knife:
  - Two pilots supported (per tasking 330 + tasking 336):
    - stats.gov.cn / NATIONAL_BULLETIN (HTML index)
    - tjj.hubei.gov.cn / PROVINCIAL_BULLETIN (XLSX 直链)
  - Pipeline: discover → download → sha256 → archive → extract → observation.
    extract is dispatched by category (HTML for NBS, XLSX for Hubei).
  - Auth escalation: 401/403/登录墙/验证码/付费/反爬 → STOP + write
    reviews/.../auth-blocked...md (5 fields per docs/52 §6.2).
  - SHA-drift handling (per tasking 333 §SCHEMA): live SHA ≠ registry → **NOT**
    a hard fail. Still WORM-archive the bytes, set
    `intake_status=CANDIDATE_AUTO` + `is_demo=true`, and write
    reviews/.../sha-drift-...md (5 fields per tasking 333 §SCHEMA).
  - WORM archive: data/public_archives/{YYYY-MM}/{domain}/{filename}.
  - Lineage contract: intake_status=O1_AUTO_INTAKED only when SHA matches
    registry AND not fixture AND all lineage fields present (per docs/48 §5).
  - 禁止 headless browser (per registry.csv Hubei row: "禁止 headless browser,
    被 ERR_CONNECTION_RESET 拒绝").

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
  0 = OK (dry-run / live with confirm-live / --from-local-sample intake)
  1 = pilot source not in registry, OR local-sample refused (disabled row
      without --allow-disabled-local-sample)
  2 = registry CSV parse error
  3 = AUTH blocked (401/403/登录墙/验证码/付费/反爬); blocked report written
  4 = SHA mismatch with registry → drift path (NOT a hard fail); CANDIDATE_AUTO
      archived + sha-drift report written; rc=4 signals "drift handled, not O1"
  5 = network/transport error after retries
  6 = live or --from-local-sample mode requested without --confirm-live=PATH
  7 = tech-blocked (JS-only shell / 0 deeplinks / same-domain filter excludes all);
      tech-blocked report written; STOP, do NOT bypass with headless
  8 = local-sample SHA does NOT match registry file_hash_sha256; hard fail
      (do NOT auto-update registry, do NOT intake)
  9 = local-sample file missing at local_sample_path
"""
from __future__ import annotations

import argparse
import csv
import datetime as _dt
import hashlib
import json
import os
import sys
import time
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
REGISTRY_CSV = PROJECT_ROOT / "source_registry" / "registry.csv"
PUBLIC_ARCHIVE_ROOT = PROJECT_ROOT / "data" / "public_archives"
PUBLIC_EXTRACTS_ROOT = PROJECT_ROOT / "data" / "public_extracts"


def get_archive_root() -> Path:
    """Resolve the WORM archive root at CALL time (per tasking 352 §SCHEMA).

    Precedence: CEGR_ARCHIVE_ROOT env (also set by --archive-root) >
    module default PUBLIC_ARCHIVE_ROOT (monkeypatchable in-process).
    Resolving per-call is what lets pytest — including subprocess tests,
    which inherit the parent env — redirect writes to tmp dirs so the
    committed data/public_extracts tree is never dirtied (cf. 7f04237 /
    95a8569, both of which restored extracts a test had clobbered)."""
    env = os.environ.get("CEGR_ARCHIVE_ROOT")
    if env:
        return Path(env)
    return PUBLIC_ARCHIVE_ROOT


def get_extracts_root() -> Path:
    """Resolve the structured-extracts root at CALL time (per tasking 352).

    Precedence: CEGR_EXTRACT_ROOT env (also set by --extract-root) >
    module default PUBLIC_EXTRACTS_ROOT."""
    env = os.environ.get("CEGR_EXTRACT_ROOT")
    if env:
        return Path(env)
    return PUBLIC_EXTRACTS_ROOT


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
    mismatch (per docs/52 §4 step 3).

    Per tasking 333 §SCHEMA: callers in the live path are expected to catch
    this RuntimeError and route to the SHA-drift handler (WORM archive +
    intake_status=CANDIDATE_AUTO + drift report). assert_sha_matches_registry
    itself stays loud because other callers (e.g. unit tests) should treat a
    registry drift as a contract violation, not a silent auto-update.
    """
    if computed.lower() != expected.lower():
        raise RuntimeError(
            f"SHA-256 mismatch: computed={computed[:16]}… expected="
            f"{expected[:16]}…  (registry may have drifted; report user, "
            f"do not auto-update)"
        )


class ShaDrift(Exception):
    """Raised by main() when the live SHA differs from registry and the
    drift path was taken (WORM archive + drift report). Carries all 5
    fields required by tasking 333 §SCHEMA so the report writer doesn't
    need to re-derive them."""

    def __init__(
        self,
        *,
        domain: str,
        category: str,
        url: str,
        computed_sha256: str,
        expected_sha256: str,
    ):
        self.domain = domain
        self.category = category
        self.url = url
        self.computed_sha256 = computed_sha256
        self.expected_sha256 = expected_sha256
        super().__init__(
            f"SHA drift: computed={computed_sha256[:16]}… "
            f"expected={expected_sha256[:16]}…"
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
    out_dir = get_archive_root() / ym / domain
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / filename
    if out_path.exists():
        # Idempotent: if the same content is already archived, do not overwrite.
        # A drift would have already failed the SHA check above.
        return out_path
    out_path.write_bytes(blob)
    return out_path


# ---------------------------------------------------------------------------
# Local-sample intake (per tasking 346 §SCHEMA)
# ---------------------------------------------------------------------------

class LocalSampleMismatch(Exception):
    """Raised when the local sample's SHA does NOT match the registry's
    `file_hash_sha256`. Per tasking 346 §SCHEMA: SHA mismatch is a hard fail
    (do NOT silently fix the registry; do NOT auto-intake)."""

    def __init__(
        self,
        *,
        domain: str,
        category: str,
        path: Path,
        computed_sha256: str,
        expected_sha256: str,
    ):
        self.domain = domain
        self.category = category
        self.path = path
        self.computed_sha256 = computed_sha256
        self.expected_sha256 = expected_sha256
        super().__init__(
            f"local sample SHA mismatch at {path}: "
            f"computed={computed_sha256[:16]}… "
            f"expected={expected_sha256[:16]}…"
        )


def intake_from_local_sample(
    *,
    pilot_row: dict[str, str],
    allow_disabled: bool = False,
) -> tuple[Path, Path, Path]:
    """Run the 5-step pipeline (read → SHA → archive → extract → observation)
    against the pilot's `local_sample_path` instead of a live download.

    Per tasking 346 §SCHEMA:
      1. Read the local file at `local_sample_path`.
      2. SHA MUST equal `file_hash_sha256`; mismatch → LocalSampleMismatch.
      3. WORM-archive the bytes (same archive() helper as live path).
      4. extract_tables(blob, category=pilot.category).
      5. write_extract_json(...) → data/public_extracts/{domain}/{category}.json.
      6. write_observation(... intake_status=REGISTRY_SAMPLE_INTAKED,
         is_demo=true).

    If the registry row is `enabled=FALSE` and `allow_disabled=False`,
    raises RuntimeError (red line: do NOT silently intake disabled rows).
    The Hubei-specific path requires `allow_disabled=True` (per tasking 346
    §SCHEMA "(3) 湖北允许 `--allow-disabled-local-sample`").

    Returns (archive_path, extract_json_path, lineage_path).
    """
    enabled = pilot_row.get("enabled", "").strip().upper()
    if enabled != "TRUE" and not allow_disabled:
        raise RuntimeError(
            f"registry row enabled={enabled!r} (not TRUE); refusing local-sample "
            f"intake for {pilot_row['domain']} / {pilot_row['category']}. "
            f"Pass --allow-disabled-local-sample to override (per tasking 346 "
            f"§SCHEMA \"(3) 湖北允许\")."
        )

    sample_rel = pilot_row.get("local_sample_path", "").strip()
    if not sample_rel:
        raise RuntimeError(
            f"registry row {pilot_row['domain']} / {pilot_row['category']} "
            f"has empty local_sample_path; cannot run --from-local-sample"
        )
    sample_path = Path(sample_rel)
    if not sample_path.is_absolute():
        sample_path = (PROJECT_ROOT / sample_rel).resolve()
    if not sample_path.exists():
        raise FileNotFoundError(f"local sample missing: {sample_path}")

    blob = sample_path.read_bytes()
    sha = sha256_of_bytes(blob)
    expected_sha = pilot_row["file_hash_sha256"].strip().lower()
    if sha.lower() != expected_sha:
        raise LocalSampleMismatch(
            domain=pilot_row["domain"],
            category=pilot_row["category"],
            path=sample_path,
            computed_sha256=sha,
            expected_sha256=pilot_row["file_hash_sha256"],
        )

    # Use the sample's basename as archive filename so WORM path is stable
    # and self-describing.
    archive_path = archive(
        blob=blob,
        domain=pilot_row["domain"],
        filename=sample_path.name,
    )

    tables = extract_tables(blob, category=pilot_row["category"])
    extract_json_path = write_extract_json(
        domain=pilot_row["domain"],
        category=pilot_row["category"],
        tables=tables,
        archive_path=archive_path,
        sha256_hex=sha,
        source_sample_path=sample_rel,
    )

    # Lineage row lives at the same path used for live mode lineage.
    # is_demo=true is automatic (REGISTRY_SAMPLE_INTAKED ≠ O1_AUTO_INTAKED).
    lineage_path = Path(pilot_row.get("__lineage_output__", "/tmp/_local_sample_lineage.jsonl"))
    write_observation(
        archive_path=archive_path,
        sha256_hex=sha,
        agency=pilot_row["organization"],
        intake_status=REGISTRY_SAMPLE_INTAKE_STATUS,
        output_path=lineage_path,
    )
    return archive_path, extract_json_path, lineage_path


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
    header: list[str] | None = None
    for tr in table.find_all("tr"):
        cells = [td.get_text(strip=True) for td in tr.find_all(["td", "th"])]
        if not cells:
            continue
        if header is None:
            # First non-empty row treated as header.
            header = cells
            continue
        rows.append({h: c for h, c in zip(header, cells)})
    return rows


# ---------------------------------------------------------------------------
# Extract (XLSX table scrape for Hubei PROVINCIAL_BULLETIN)
# ---------------------------------------------------------------------------

def extract_xlsx_tables(blob: bytes) -> list[dict[str, str]]:
    """Extract the first sheet of an .xlsx file as a list of dicts.

    Per tasking 336 §SCHEMA + registry.csv Hubei row (access_method:
    'curl 直下（禁止 headless browser，被 ERR_CONNECTION_RESET 拒绝）').
    First row is treated as header; subsequent rows become dicts keyed by
    the header cells (with str coercion for non-string cell values).

    openpyxl is used (locally imported; raises RuntimeError if missing).
    The Hubei file is small (~11 KB) so loading the whole workbook is fine.
    """
    try:
        import openpyxl  # local import; dry-run friendly
    except ImportError as exc:  # pragma: no cover
        raise RuntimeError("openpyxl missing") from exc
    import io

    wb = openpyxl.load_workbook(io.BytesIO(blob), read_only=True, data_only=True)
    try:
        ws = wb.worksheets[0]
        rows_iter = ws.iter_rows(values_only=True)
        header: list[str] | None = None
        rows: list[dict[str, str]] = []
        for raw in rows_iter:
            cells = ["" if v is None else str(v) for v in raw]
            if not any(c.strip() for c in cells):
                continue
            if header is None:
                header = cells
                continue
            rows.append({h: c for h, c in zip(header, cells)})
        return rows
    finally:
        wb.close()


def extract_tables(blob: bytes, *, category: str) -> list[dict[str, str]]:
    """Dispatcher: pick the right extractor based on registry.csv category.

    Per tasking 336 §SCHEMA "extract(xlsx)" + tasking 343 §SCHEMA — routes by category:
      - NATIONAL_BULLETIN   → HTML (NBS zxfb index)
      - PROVINCIAL_BULLETIN → XLSX (Hubei 月度统计)
      - MUNICIPAL_BULLETIN  → HTML (Shenzhen sz.gov.cn 公报散文 + 嵌入表格)
    Unknown categories raise ValueError (red line: do not silently
    downgrade to HTML for an EXCEL source or vice versa)."""
    if category == "NATIONAL_BULLETIN":
        return extract_html_tables(blob)
    if category == "PROVINCIAL_BULLETIN":
        return extract_xlsx_tables(blob)
    if category == "MUNICIPAL_BULLETIN":
        return extract_html_tables(blob)
    raise ValueError(
        f"unknown category '{category}'; no extractor registered "
        f"(supported: NATIONAL_BULLETIN, PROVINCIAL_BULLETIN, MUNICIPAL_BULLETIN)"
    )


# ---------------------------------------------------------------------------
# Structured extract → JSON (per tasking 346 §SCHEMA)
# ---------------------------------------------------------------------------

def write_extract_json(
    *,
    domain: str,
    category: str,
    tables: list[dict[str, str]],
    archive_path: Path,
    sha256_hex: str,
    source_sample_path: str,
    output_root: Path | None = None,
) -> Path:
    """Write structured extract JSON to {extracts_root}/{domain}/{category}.json.

    Per tasking 346 §SCHEMA: stores REGISTRY_SAMPLE_INTAKED row's extracted
    table rows alongside provenance (archive path, source sample path, SHA).
    is_demo is implicit (caller decides via lineage row, not via this JSON).

    `output_root` resolves at CALL time via get_extracts_root() when not
    supplied (per tasking 352: a module-constant DEFAULT ARG would bind at
    import and ignore both monkeypatching and CEGR_EXTRACT_ROOT, which is
    exactly how pytest runs clobbered the committed extracts).

    Returns the written path. Caller is responsible for ensuring tables is
    the result of extract_tables(blob, category=pilot.category)."""
    root = output_root if output_root is not None else get_extracts_root()
    out_dir = root / domain
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / f"{category}.json"
    record = {
        "domain": domain,
        "category": category,
        "source_sample_path": source_sample_path,
        "source_archive_path": _relative_or_abs(archive_path),
        "source_sha256": sha256_hex,
        "row_count": len(tables),
        "rows": tables,
        "extracted_at": _dt.datetime.now(_dt.timezone.utc).isoformat(),
    }
    out_path.write_text(
        json.dumps(record, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    return out_path


# ---------------------------------------------------------------------------
# Deeplink discovery (per tasking 339 §SCHEMA — no headless, no JS exec)
# ---------------------------------------------------------------------------

JS_SHELL_SIZE_THRESHOLD = 2048  # bytes; below this, suspect JS-only shell


def is_js_only_shell(blob: bytes, *, threshold: int = JS_SHELL_SIZE_THRESHOLD) -> bool:
    """Heuristic: return True if the blob looks like a JS-only shell (e.g.
    Hubei's 71-byte ``<script>window.location=...</script>``).

    Triggers on either:
      - size <= threshold AND content contains a `<script>` tag, OR
      - content contains the literal `window.location` redirect marker.
    The connector does NOT execute JS (per tasking 339 §红线 '不执行页面 JS');
    this check only inspects the bytes statically.
    """
    if not blob:
        return True
    text = blob.decode("utf-8", errors="replace")
    has_script = "<script" in text.lower()
    has_redirect = "window.location" in text or "location.replace" in text
    if has_redirect:
        return True
    return has_script and len(blob) < threshold


def discover_deeplinks(
    blob: bytes,
    *,
    base_url: str,
    extensions: tuple[str, ...] = (".xlsx", ".xls"),
) -> list[str]:
    """Find same-domain deep links to attachment files in an index page.

    Per tasking 339 §SCHEMA 'deeplink discover': parse the index HTML with
    BeautifulSoup, collect `<a href="...">` whose path ends with one of
    `extensions`, resolve relative URLs against `base_url`, and keep only
    links whose host matches `base_url`'s host. NO headless browser, NO
    JS execution.

    Returns a list of absolute URLs (in document order). An empty list
    means "no deeplinks discoverable from initial HTML" — caller should
    escalate via write_tech_blocked_report rather than try to follow JS.
    """
    try:
        from bs4 import BeautifulSoup
        from urllib.parse import urljoin, urlparse
    except ImportError as exc:  # pragma: no cover
        raise RuntimeError("beautifulsoup4 missing") from exc

    base_host = (urlparse(base_url).hostname or "").lower()
    soup = BeautifulSoup(blob, "html.parser")
    found: list[str] = []
    seen: set[str] = set()
    for a in soup.find_all("a"):
        href = a.get("href")
        if not href or not isinstance(href, str):
            continue
        href_lower = href.lower()
        if not any(href_lower.endswith(ext) for ext in extensions):
            continue
        abs_url = urljoin(base_url, href)
        host = (urlparse(abs_url).hostname or "").lower()
        # Same-domain only (per tasking 339 §红线 '不盲爬外域').
        if base_host and host and host != base_host:
            continue
        if abs_url in seen:
            continue
        seen.add(abs_url)
        found.append(abs_url)
    return found


# ---------------------------------------------------------------------------
# Tech-blocked report (per tasking 339 §SCHEMA — 5 mandatory fields)
# ---------------------------------------------------------------------------

def write_tech_blocked_report(
    *,
    domain: str,
    category: str,
    url: str,
    phenomenon: str,
    required_to_proceed: str = (
        "用户需提供稳定的直链 URL（registry.csv primary_url 改为直链）或 "
        "在 headless-free 的可达页面（HTML 含完整附件 href 列表）"
    ),
    alternative_source: str = (
        "registry.csv 已有公开源：stats.gov.cn NATIONAL_BULLETIN(已落 drift 等用户)/ "
        "wb.flk.npc.gov.cn SCANNED_PDF_RESEARCH / archive.org SCANNED_PDF_UPLOAD "
        "（待 tasking 33X+ 落地）"
    ),
) -> Path:
    """Write reviews/.../tech-blocked...md with the 5 mandatory fields per
    tasking 339 §SCHEMA: 源 / URL / 现象 / 需要什么 / 替代. Used when
    deeplink discovery finds 0 candidates OR the page is a JS-only shell
    (e.g. Hubei 71-byte redirect)."""
    REVIEWS_DIR.mkdir(parents=True, exist_ok=True)
    ts = _dt.datetime.now(_dt.timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    out_path = REVIEWS_DIR / (
        f"{ts}-stage2-public-source-tech-blocked-{domain}-{category}.md"
    )
    body = f"""# 公开源技术阻断报告（per tasking 339 §SCHEMA）

- 域：`{domain}`
- 类目：`{category}`
- 触发时间（UTC）：`{_dt.datetime.now(_dt.timezone.utc).isoformat()}`

## 1. 源 / URL

| 字段 | 值 |
|---|---|
| domain | `{domain}` |
| category | `{category}` |
| URL | `{url}` |

## 2. 现象

{ phenomenon}

## 3. 需要什么（用户裁定 / 提供）

{ required_to_proceed}

## 4. 替代公开源

{ alternative_source}

## 5. 红线

- ❌ **不执行页面 JS**（per tasking 339 §红线 '不执行页面 JS';connector 静态解析 HTML）
- ❌ **不切 headless browser 跟随 JS 重定向**（per registry.csv Hubei access_method）
- ❌ **不盲爬外域**（deeplink 已用 urlparse 比 host,跨域一律过滤）
- ❌ **不把 JS 壳静默当 O1_AUTO_INTAKED**（本报告即非静默）
- ❌ **不静默失败**（5 字段 + 替代源 + 等用户裁定）
- ✅ **等用户裁定**：(a) 提供稳定直链 / (b) 换镜像 / (c) 暂缓

— End of tech-blocked report —
"""
    out_path.write_text(body, encoding="utf-8")
    return out_path


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

# Per tasking 346 §SCHEMA: REGISTRY_SAMPLE_INTAKED is the honest marker for
# a local-sample intake (sample ≠ live closure; is_demo=true is automatic).
REGISTRY_SAMPLE_INTAKE_STATUS = "REGISTRY_SAMPLE_INTAKED"


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
        - O1_AUTO_INTAKED    (live mode + SHA matches registry)
        - CANDIDATE_AUTO     (live mode + SHA drift; per tasking 333; is_demo=true)
        - DEMO               (fixture / placeholder; demo flag stays true)
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
# SHA-drift report (per tasking 333 §SCHEMA — 5 mandatory fields)
# ---------------------------------------------------------------------------


# ---------------------------------------------------------------------------
# SHA-drift report (per tasking 333 §SCHEMA — 5 mandatory fields)
# ---------------------------------------------------------------------------

def write_sha_drift_report(
    *,
    domain: str,
    category: str,
    url: str,
    computed_sha256: str,
    expected_sha256: str,
    recommendation: str = (
        "用户确认后二选一：(a) 更新 registry.csv file_hash_sha256 为实测 "
        "computed_sha256（如认定是源站换版/换路径）；(b) 改用稳定的归档 URL "
        "（如 Wayback Machine 快照或稳定 PDF/EXCEL 直链）。本 connector "
        "不会自动改 registry。"
    ),
) -> Path:
    """Write reviews/.../sha-drift-...md with the 5 mandatory fields per
    tasking 333 §SCHEMA: 源 / URL / computed SHA / expected SHA / 建议.
    Returns the written path. The WORM archive of the drifted bytes is
    already on disk by the time this report runs (callers must archive
    BEFORE invoking write_sha_drift_report so the report can reference
    the archive path)."""
    REVIEWS_DIR.mkdir(parents=True, exist_ok=True)
    ts = _dt.datetime.now(_dt.timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    out_path = REVIEWS_DIR / (
        f"{ts}-stage2-public-source-sha-drift-{domain}-{category}.md"
    )
    # Locate the most-recent archive for this domain+category so the
    # report can reference the WORM-stored bytes. Honor root overrides so
    # test-run reports reference the redirected archive, not the repo one.
    ym = _dt.datetime.now(_dt.timezone.utc).strftime("%Y-%m")
    archive_dir = get_archive_root() / ym / domain
    archive_ref = "(not yet archived)"
    if archive_dir.exists():
        candidates = sorted(archive_dir.iterdir(), key=lambda p: p.stat().st_mtime, reverse=True)
        if candidates:
            archive_ref = _relative_or_abs(candidates[0])
    body = f"""# 公开源 SHA 漂移报告（per tasking 333 §SCHEMA）

- 域：`{domain}`
- 类目：`{category}`
- 触发时间（UTC）：`{_dt.datetime.now(_dt.timezone.utc).isoformat()}`
- WORM 归档：`{archive_ref}`

## 1. 源 / URL

| 字段 | 值 |
|---|---|
| domain | `{domain}` |
| category | `{category}` |
| URL | `{url}` |

## 2. computed SHA-256（实测下载字节）

```
{computed_sha256}
```

## 3. expected SHA-256（registry.csv file_hash_sha256）

```
{expected_sha256}
```

## 4. 状态

- `intake_status = CANDIDATE_AUTO`（非 O1_AUTO_INTAKED；drift ≠ 收口）
- `is_demo = true`（drift 候选绝不能伪装成真数据）
- WORM 归档实测字节：已写入 `{archive_ref}`
- registry.csv **未**被修改（connector 不自动改 registry）

## 5. 建议

{recommendation}

## 6. 红线

- ❌ **不自动改 registry.csv file_hash_sha256**（per tasking 333 §SCHEMA "不伪造、不自动改 registry"）
- ❌ **不把 drift 标成 O1_AUTO_INTAKED**（drift ≠ 收口）
- ❌ **不静默吞掉 drift**（本报告即非静默；含 5 字段 + WORM 归档位置）
- ❌ **不 headless / 不绕过反爬**获取"应该匹配的"内容
- ✅ **等用户裁定**：(a) 更新 registry 哈希 或 (b) 改用稳定 URL

— End of SHA drift report —
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
            "Dry-run by default; --live requires --confirm-live=PATH. "
            "--from-local-sample ingests the pilot's local_sample_path "
            "instead of a live download (per tasking 346 §SCHEMA)."
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
        "--from-local-sample", action="store_true",
        help="ingest pilot's local_sample_path (per tasking 346 §SCHEMA); "
             "no network; SHA must match registry file_hash_sha256; "
             "requires --confirm-live=PATH for lineage writes; "
             "emits intake_status=REGISTRY_SAMPLE_INTAKED, is_demo=true",
    )
    parser.add_argument(
        "--allow-disabled-local-sample", action="store_true",
        help="allow --from-local-sample on registry rows where enabled=FALSE "
             "(currently only Hubei, per tasking 346 §SCHEMA)",
    )
    parser.add_argument(
        "--confirm-live", default=None, metavar="PATH",
        help="explicit authorization to flip intake_status=O1_AUTO_INTAKED "
             "(live mode) OR write REGISTRY_SAMPLE_INTAKED lineage "
             "(--from-local-sample mode); PATH is the lineage JSONL output",
    )
    parser.add_argument(
        "--archive-root", default=None, metavar="DIR",
        help="override the WORM archive root (default: data/public_archives "
             "under the repo). Equivalent to CEGR_ARCHIVE_ROOT (per tasking "
             "352 §SCHEMA; pytest MUST point this at a tmp dir)",
    )
    parser.add_argument(
        "--extract-root", default=None, metavar="DIR",
        help="override the structured-extracts root (default: "
             "data/public_extracts under the repo). Equivalent to "
             "CEGR_EXTRACT_ROOT (per tasking 352 §SCHEMA)",
    )
    args = parser.parse_args(argv)

    # Root overrides resolve BEFORE any write path can run (per tasking 352:
    # both the CLI flag and the env var funnel into the same call-time
    # resolution in get_archive_root()/get_extracts_root()).
    if args.archive_root:
        os.environ["CEGR_ARCHIVE_ROOT"] = args.archive_root
    if args.extract_root:
        os.environ["CEGR_EXTRACT_ROOT"] = args.extract_root

    if args.live and not args.confirm_live:
        print(
            "❌ --live requires --confirm-live=PATH (explicit user authorization)",
            file=sys.stderr,
        )
        return 6

    if args.from_local_sample and not args.confirm_live:
        print(
            "❌ --from-local-sample requires --confirm-live=PATH (lineage "
            "writes still require explicit authorization)",
            file=sys.stderr,
        )
        return 6

    rows = load_registry()
    if not rows:
        return 2

    # Local-sample path: do NOT call filter_public_enabled (which would
    # reject disabled rows like Hubei). Instead, find the row by
    # domain+category regardless of `enabled`, then let
    # intake_from_local_sample() enforce the enabled gate.
    if args.from_local_sample:
        pilot = None
        for r in rows:
            if r.get("domain") == args.pilot_domain and r.get("category") == args.pilot_category:
                pilot = r
                break
        if pilot is None:
            print(
                f"❌ pilot not in registry: domain={args.pilot_domain} "
                f"category={args.pilot_category}",
                file=sys.stderr,
            )
            return 1
        print(
            f"OK local-sample pilot matched: {pilot['domain']} / "
            f"{pilot['category']} (enabled={pilot['enabled']})"
        )
        print(f"   local_sample_path: {pilot['local_sample_path']}")
        print(f"   expected SHA: {pilot['file_hash_sha256'][:16]}…")
        try:
            pilot["__lineage_output__"] = args.confirm_live
            archive_path, extract_json_path, lineage_path = intake_from_local_sample(
                pilot_row=pilot,
                allow_disabled=args.allow_disabled_local_sample,
            )
        except LocalSampleMismatch as exc:
            print(
                f"❌ local-sample SHA mismatch; refusing intake. "
                f"computed={exc.computed_sha256[:16]}… "
                f"expected={exc.expected_sha256[:16]}… "
                f"path={exc.path}",
                file=sys.stderr,
            )
            return 8  # new exit code: local-sample SHA mismatch
        except FileNotFoundError as exc:
            print(f"❌ local sample not found: {exc}", file=sys.stderr)
            return 9  # new exit code: local sample missing
        except RuntimeError as exc:
            print(f"❌ local-sample intake refused: {exc}", file=sys.stderr)
            return 1  # disabled row without --allow-disabled-local-sample
        print(f"OK archived: {archive_path}")
        print(f"OK extract JSON: {extract_json_path}")
        print(f"OK lineage: {lineage_path}")
        print(
            "OK REGISTRY_SAMPLE_INTAKED (is_demo=true; sample ≠ live closure). "
            "rc=0 = sample intake successful."
        )
        return 0

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
            "user authorization). Pass --from-local-sample --confirm-live=PATH "
            "to ingest the registry's local sample.",
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

    # Per tasking 339 §SCHEMA: deeplink discover + JS-shell detection.
    # If the page is a JS-only shell OR has no same-domain attachment href,
    # STOP and report user (do NOT bypass with headless). Otherwise resolve
    # the first deeplink and re-download that as the real source bytes.
    if is_js_only_shell(blob):
        report = write_tech_blocked_report(
            domain=pilot["domain"],
            category=pilot["category"],
            url=pilot["primary_url"],
            phenomenon=(
                f"下载字节仅 {len(blob)} bytes,且包含 `<script>` 或 "
                f"`window.location` 重定向标记。判定为 JS-only shell "
                f"(per tasking 339 §SCHEMA)。connector **不执行 JS**,也"
                f"**不切 headless browser** 跟随;等用户提供稳定直链或暂缓。"
            ),
        )
        print(f"❌ JS-only shell; tech-blocked report: {report}", file=sys.stderr)
        return 7

    extensions: tuple[str, ...]
    if pilot["category"] == "PROVINCIAL_BULLETIN":
        extensions = (".xlsx", ".xls")
    elif pilot["category"] == "NATIONAL_BULLETIN":
        extensions = (".html", ".htm")  # article pages
    elif pilot["category"] == "MUNICIPAL_BULLETIN":
        # Shenzhen sz.gov.cn 公报：散文形式 + 嵌入表格；本页 HTML 即可，
        # 不强求附件 deeplink。若后续 tasking 要求附件直链再加 extensions。
        extensions = (".html", ".htm", ".pdf")
    else:
        extensions = (".xlsx", ".xls", ".html", ".htm", ".pdf")

    deeplinks = discover_deeplinks(
        blob,
        base_url=pilot["primary_url"],
        extensions=extensions,
    )
    if not deeplinks:
        report = write_tech_blocked_report(
            domain=pilot["domain"],
            category=pilot["category"],
            url=pilot["primary_url"],
            phenomenon=(
                f"已下载 {len(blob)} bytes 但 HTML 中未发现任何同域附件 "
                f"href(扩展名: {', '.join(extensions)})。可能是 JS 渲染页面、"
                f"iframe 内嵌、或附件链接通过 JS 动态生成。connector 静态解析"
                f"不到 → 0 deeplink → tech-blocked,等用户提供稳定直链。"
            ),
        )
        print(f"❌ 0 deeplinks; tech-blocked report: {report}", file=sys.stderr)
        return 7

    # Use the first deeplink (deterministic, document order). A future
    # connector could sort by URL date token (e.g. /2026-06/) for "freshest"
    # selection. Knife 49 keeps it simple.
    chosen_url = deeplinks[0]
    print(f"OK deeplink discovered: {chosen_url}")
    if chosen_url != pilot["primary_url"]:
        try:
            blob = download(chosen_url)
        except AuthBlocked as ab:
            report = write_auth_blocked_report(
                domain=ab.domain,
                category=ab.category,
                url=ab.url,
                reason=ab.reason,
                status_code=ab.status_code,
            )
            print(f"❌ AUTH blocked (deeplink); {report}", file=sys.stderr)
            return 3
        except RuntimeError as exc:
            print(f"❌ deeplink transport error: {exc}", file=sys.stderr)
            return 5

    sha = sha256_of_bytes(blob)
    print(f"OK downloaded {len(blob)} bytes; sha256={sha[:16]}…")

    filename = Path(pilot["primary_url"]).name or "index.html"

    # SHA path: match → O1_AUTO_INTAKED; mismatch → drift (NOT hard fail).
    # Per tasking 333 §SCHEMA: drift does NOT auto-update registry; we still
    # WORM-archive the bytes, write a sha-drift report, and emit a
    # CANDIDATE_AUTO lineage row with is_demo=true.
    sha_matched = (
        sha.lower() == pilot["file_hash_sha256"].strip().lower()
    )

    if not sha_matched:
        # Always WORM-archive the drifted bytes BEFORE the report runs so
        # the report can point at them.
        archive_path = archive(
            blob=blob,
            domain=pilot["domain"],
            filename=filename,
        )
        print(f"⚠ SHA drift; archived drifted bytes: {archive_path}")
        drift_report = write_sha_drift_report(
            domain=pilot["domain"],
            category=pilot["category"],
            url=pilot["primary_url"],
            computed_sha256=sha,
            expected_sha256=pilot["file_hash_sha256"],
        )
        print(f"⚠ drift report written: {drift_report}", file=sys.stderr)
        # Emit CANDIDATE_AUTO lineage (is_demo=true via write_observation).
        write_observation(
            archive_path=archive_path,
            sha256_hex=sha,
            agency=pilot["organization"],
            intake_status="CANDIDATE_AUTO",
            output_path=Path(args.confirm_live),
        )
        print(
            "⚠ CANDIDATE_AUTO lineage emitted; rc=4 means drift handled, "
            "NOT O1 收口。等用户裁定。",
            file=sys.stderr,
        )
        return 4

    # SHA matches → O1_AUTO_INTAKED path (unchanged from knife 46).
    archive_path = archive(
        blob=blob,
        domain=pilot["domain"],
        filename=filename,
    )
    print(f"OK archived: {archive_path}")

    tables = extract_tables(blob, category=pilot["category"])
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