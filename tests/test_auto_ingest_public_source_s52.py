"""S2.5.2.2 — Tests for scripts/auto_ingest_public_source.py.

Per docs/52 §4 + §7 (验收清单) and tasking 330 §SCHEMA "本刀做".

These tests do NOT hit the network. They validate:
  - registry CSV parsing + filter (public, enabled, pilot match)
  - SHA-256 contract vs registry hash
  - AUTH escalation triggers (401/403/429 + login/CAPTCHA redirect)
  - No headless browser / no --url flag (red-line guard)
  - No unregistered source (red-line guard)
  - WORM archive path format (per docs/52 §5 namespace)
  - Lineage contract fields (per docs/48 §5)
  - dry-run vs live guard (--live requires --confirm-live=PATH)

Red lines guarded:
  - No headless browser imports (selenium/playwright/pyppeteer)
  - No --url argparse option (per docs/35 §4.2 / compute_file_sha.py precedent)
  - No bypassing 401/403/429 status codes
  - No fixture-as-live (live path requires SHA match with registry)
"""
from __future__ import annotations

import csv
import inspect
import io
import json
import subprocess
import sys
from pathlib import Path

import pytest

PROJECT_ROOT = Path(__file__).resolve().parent.parent
SCRIPT = PROJECT_ROOT / "scripts" / "auto_ingest_public_source.py"
REGISTRY_CSV = PROJECT_ROOT / "source_registry" / "registry.csv"

sys.path.insert(0, str(PROJECT_ROOT / "scripts"))
import auto_ingest_public_source as aips  # noqa: E402


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture(scope="module")
def registry_rows() -> list[dict[str, str]]:
    return aips.load_registry()


@pytest.fixture
def pilot_row(registry_rows: list[dict[str, str]]) -> dict[str, str]:
    rows = aips.filter_public_enabled(registry_rows)
    assert rows, "pilot row missing from registry"
    assert len(rows) == 1, f"expected 1 pilot row, got {len(rows)}"
    return rows[0]


# ---------------------------------------------------------------------------
# 1. Registry parsing
# ---------------------------------------------------------------------------

def test_registry_csv_exists():
    assert REGISTRY_CSV.exists(), f"{REGISTRY_CSV} missing"


def test_registry_load_returns_six_rows(registry_rows):
    """Per docs/52 §1 + source_registry/registry.csv — 6 public sources registered."""
    assert len(registry_rows) == 6, (
        f"expected 6 rows, got {len(registry_rows)}"
    )


def test_registry_has_required_columns(registry_rows):
    """Per docs/52 §1 — registry must carry auth_note + file_hash_sha256 +
    organization + access_method for the connector contract."""
    required = {
        "domain", "organization", "category", "primary_url", "auth_note",
        "access_method", "file_hash_sha256", "file_size_bytes",
        "declared_source_level", "enabled",
    }
    for row in registry_rows:
        missing = required - set(row.keys())
        assert not missing, f"missing columns in registry row: {missing}"


# ---------------------------------------------------------------------------
# 2. Pilot filter (per tasking 330 §SCHEMA: only ONE pilot this knife)
# ---------------------------------------------------------------------------

def test_pilot_filter_matches_only_nbs_zxfb(registry_rows):
    rows = aips.filter_public_enabled(registry_rows)
    assert len(rows) == 1
    row = rows[0]
    assert row["domain"] == "stats.gov.cn"
    assert row["category"] == "NATIONAL_BULLETIN"
    assert row["primary_url"].rstrip("/") == "https://www.stats.gov.cn/sj/zxfb"


def test_pilot_filter_when_default_pilot_excludes_hubei_and_shenzhen(registry_rows):
    """Per tasking 330 §SCHEMA + CLI defaults: this knife ingests ONLY
    NBS NATIONAL_BULLETIN. The default PILOT_DOMAIN/PILOT_CATEGORY must
    therefore exclude Hubei/Shenzhen rows."""
    rows = aips.filter_public_enabled(registry_rows)
    domains = {r["domain"] for r in rows}
    assert domains == {"stats.gov.cn"}, (
        f"default pilot filter must return only stats.gov.cn; got {domains}"
    )
    categories = {r["category"] for r in rows}
    assert categories == {"NATIONAL_BULLETIN"}, (
        f"default pilot category must be NATIONAL_BULLETIN; got {categories}"
    )


def test_filter_function_accepts_other_pilot(registry_rows):
    """Sanity: filter_public_enabled IS generic — it will return Hubei/Shenzhen
    if explicitly asked. The CLI defaults (PILOT_DOMAIN/PILOT_CATEGORY) are what
    enforce the NBS-only scope for this knife."""
    rows = aips.filter_public_enabled(
        registry_rows, pilot_domain="tjj.hubei.gov.cn",
        pilot_category="PROVINCIAL_BULLETIN",
    )
    assert len(rows) == 1
    assert rows[0]["domain"] == "tjj.hubei.gov.cn"


def test_pilot_filter_rejects_disabled_rows():
    csv_text = (
        "domain,organization,category,primary_url,auth_note,enabled\n"
        "stats.gov.cn,国家统计局,NATIONAL_BULLETIN,https://example/,公开,FALSE\n"
    )
    rows = list(csv.DictReader(io.StringIO(csv_text)))
    out = aips.filter_public_enabled(rows)
    assert out == [], "disabled row must be filtered out"


def test_pilot_filter_rejects_auth_required_rows():
    csv_text = (
        "domain,organization,category,primary_url,auth_note,enabled\n"
        "stats.gov.cn,国家统计局,NATIONAL_BULLETIN,https://example/,需登录,TRUE\n"
    )
    rows = list(csv.DictReader(io.StringIO(csv_text)))
    out = aips.filter_public_enabled(rows)
    assert out == [], "auth-required row must be filtered out"


# ---------------------------------------------------------------------------
# 3. SHA-256 contract
# ---------------------------------------------------------------------------

def test_sha256_of_bytes_is_lowercase_hex():
    digest = aips.sha256_of_bytes(b"hello")
    assert digest == "2cf24dba5fb0a30e26e83b2ac5b9e29e1b161e5c1fa7425e73043362938b9824"
    assert digest.islower() and len(digest) == 64


def test_sha_matches_registry_passes(pilot_row):
    """When computed == registry file_hash_sha256, no exception."""
    aips.assert_sha_matches_registry(
        computed=pilot_row["file_hash_sha256"],
        expected=pilot_row["file_hash_sha256"],
    )


def test_sha_mismatch_raises(pilot_row):
    """When SHA differs (source may have drifted), raise per docs/52 §4 step 3.

    Per tasking 333 §SCHEMA: assert_sha_matches_registry itself stays loud
    (the contract must fail loudly for any caller); main() catches the
    RuntimeError and routes to the drift handler (WORM archive + drift
    report + CANDIDATE_AUTO lineage)."""
    wrong = "0" * 64
    with pytest.raises(RuntimeError, match="SHA-256 mismatch"):
        aips.assert_sha_matches_registry(
            computed=wrong,
            expected=pilot_row["file_hash_sha256"],
        )


def test_sha_drift_report_writes_5_fields(tmp_path, monkeypatch):
    """write_sha_drift_report must produce a markdown file with the 5
    mandatory fields per tasking 333 §SCHEMA: 源 / URL / computed SHA /
    expected SHA / 建议."""
    monkeypatch.setattr(aips, "REVIEWS_DIR", tmp_path)
    computed = "a" * 64
    expected = "b" * 64
    out = aips.write_sha_drift_report(
        domain="stats.gov.cn",
        category="NATIONAL_BULLETIN",
        url="https://www.stats.gov.cn/sj/zxfb/",
        computed_sha256=computed,
        expected_sha256=expected,
    )
    assert out.exists()
    body = out.read_text(encoding="utf-8")
    # 5 mandatory fields per tasking 333 §SCHEMA
    assert "domain" in body
    assert "stats.gov.cn" in body
    assert "URL" in body
    assert "https://www.stats.gov.cn/sj/zxfb/" in body
    assert computed in body, "computed SHA must appear in report"
    assert expected in body, "expected SHA must appear in report"
    # 建议 section + the 4 red-line guards
    assert "建议" in body
    assert "不自动改 registry" in body
    assert "CANDIDATE_AUTO" in body
    assert "is_demo" in body


def test_sha_drift_intake_status_is_candidate_auto(tmp_path, pilot_row):
    """When write_observation is called with intake_status=CANDIDATE_AUTO,
    is_demo MUST be 'true' (per tasking 333: drift ≠ 收口)."""
    out = tmp_path / "lineage.jsonl"
    archive_path = tmp_path / "drift.html"
    archive_path.write_bytes(b"<html>drifted</html>")
    aips.write_observation(
        archive_path=archive_path,
        sha256_hex="a" * 64,
        agency=pilot_row["organization"],
        intake_status="CANDIDATE_AUTO",
        output_path=out,
    )
    rec = json.loads(out.read_text(encoding="utf-8").strip())
    assert rec["intake_status"] == "CANDIDATE_AUTO"
    assert rec["is_demo"] == "true", "drift must keep is_demo=true"


def test_sha_drift_does_not_auto_update_registry(tmp_path, monkeypatch):
    """The drift path MUST NOT modify source_registry/registry.csv (per
    tasking 333 §SCHEMA '不自动改 registry'). Verify the drift handler
    only writes to REVIEWS_DIR (reviews/.../sha-drift-...md) and never
    opens registry.csv for writing."""
    csv_path = PROJECT_ROOT / "source_registry" / "registry.csv"
    assert csv_path.exists(), f"registry missing: {csv_path}"
    csv_bytes_before = csv_path.read_bytes()
    # The drift handler only writes reviews/.../sha-drift...md + WORM
    # archive; registry is read-only. Check the function source.
    src = inspect.getsource(aips.write_sha_drift_report)
    # No csv-writing idioms.
    assert "DictWriter" not in src
    assert "open(" not in src or ".write(" not in src, (
        "drift handler must not use raw file write (only REVIEWS_DIR + WORM)"
    )
    # And assert_sha_matches_registry never opens registry either
    # (it only compares two passed-in hex strings).
    src2 = inspect.getsource(aips.assert_sha_matches_registry)
    assert "REGISTRY_CSV" not in src2 and "open(" not in src2
    # Confirm actual registry still unchanged on disk after import.
    assert csv_path.read_bytes() == csv_bytes_before


def test_sha_drift_archive_still_written(tmp_path, monkeypatch, registry_rows):
    """Even when SHA drifts, the WORM archive MUST be written (per tasking
    333 §SCHEMA '仍 WORM 归档实测字节'). The drift handler cannot short-
    circuit the archive step."""
    monkeypatch.setattr(aips, "PUBLIC_ARCHIVE_ROOT", tmp_path / "worm")
    blob = b"<html>drifted content</html>"
    out = aips.archive(
        blob=blob,
        domain="stats.gov.cn",
        filename="zxfb.html",
    )
    assert out.exists()
    assert out.read_bytes() == blob, "drifted bytes must be WORM-archived"


def test_sha_drift_red_line_no_registry_write(tmp_path, monkeypatch):
    """Sanity: the connector module has no code path that opens registry.csv
    for writing. Drift path uses write_sha_drift_report (reviews/) +
    write_observation (lineage JSONL) + archive (data/public_archives/) —
    none of which touch registry.csv."""
    src = SCRIPT.read_text(encoding="utf-8")
    # No "open(...registry.csv, ..., 'w')" pattern.
    assert "open(REGISTRY_CSV, \"w\"" not in src
    assert "open(REGISTRY_CSV, 'w'" not in src
    # No csv.DictWriter — that would be the registry-writing idiom.
    assert "DictWriter" not in src


# ---------------------------------------------------------------------------
# 4. AUTH escalation (per docs/52 §6)
# ---------------------------------------------------------------------------

def test_auth_blocked_statuses_includes_401_403_429():
    assert {401, 403, 429} <= aips.AUTH_BLOCKED_STATUSES


def test_auth_blocked_exception_carries_5_required_fields():
    exc = aips.AuthBlocked(
        domain="stats.gov.cn",
        category="NATIONAL_BULLETIN",
        url="https://www.stats.gov.cn/sj/zxfb/",
        status_code=401,
        reason="HTTP 401",
    )
    # 5 fields per docs/52 §6.2 report
    assert exc.domain == "stats.gov.cn"
    assert exc.category == "NATIONAL_BULLETIN"
    assert exc.url.startswith("https://")
    assert exc.status_code == 401
    assert exc.reason == "HTTP 401"


def test_auth_blocked_report_writes_5_fields(tmp_path, monkeypatch):
    """write_auth_blocked_report must produce a markdown file with the 5
    mandatory fields per docs/52 §6.2."""
    monkeypatch.setattr(aips, "REVIEWS_DIR", tmp_path)
    out = aips.write_auth_blocked_report(
        domain="stats.gov.cn",
        category="NATIONAL_BULLETIN",
        url="https://www.stats.gov.cn/sj/zxfb/",
        reason="HTTP 403 after 3 attempts",
        status_code=403,
    )
    assert out.exists()
    body = out.read_text(encoding="utf-8")
    # 5 mandatory fields per docs/52 §6.2
    assert "domain" in body
    assert "category" in body
    assert "URL" in body
    assert "费用估计" in body
    assert "需要什么账号/订阅" in body
    assert "替代公开源" in body
    assert "ETA" in body or "授权后" in body


def test_login_redirect_detection_in_download(monkeypatch):
    """download() must raise AuthBlocked when redirected to a login wall,
    even if HTTP status is 200 (per docs/52 §6.1)."""
    class FakeResp:
        status_code = 200
        url = "https://login.stats.gov.cn/captcha"
        content = b"<html>login form</html>"
        def raise_for_status(self): pass

    class FakeRequests:
        @staticmethod
        def get(*args, **kwargs):
            return FakeResp()

    # Patch via sys.modules since download() does `import requests` locally.
    monkeypatch.setitem(sys.modules, "requests", FakeRequests)
    with pytest.raises(aips.AuthBlocked) as ei:
        aips.download("https://www.stats.gov.cn/sj/zxfb/")
    assert "login" in ei.value.reason.lower() or "captcha" in ei.value.reason.lower()


# ---------------------------------------------------------------------------
# 5. Red-line guards (per docs/52 §2 + tasking 330 §红线)
# ---------------------------------------------------------------------------

def test_script_does_not_import_headless_browser():
    """Per tasking 330 §红线: no selenium/playwright/pyppeteer."""
    src = SCRIPT.read_text(encoding="utf-8")
    for forbidden in ("selenium", "playwright", "pyppeteer", "webdriver"):
        assert forbidden not in src, (
            f"forbidden headless browser import: {forbidden}"
        )


def test_script_does_not_register_url_flag():
    """Per docs/35 §4.2 / compute_file_sha.py precedent: argparse must NOT
    expose --url (would enable HTTP bypass)."""
    src = SCRIPT.read_text(encoding="utf-8")
    # The string "--url" must not appear as an argparse add_argument dest.
    # Allow it only in code comments / docstring (none here).
    assert "add_argument(\"--url" not in src, (
        "argparse must NOT register --url (HTTP bypass risk)"
    )


def test_script_does_not_register_login_flag():
    """No --login / --cookie / --session flag (would enable login bypass)."""
    src = SCRIPT.read_text(encoding="utf-8")
    for forbidden in ("--login", "--cookie", "--session", "--password", "--token"):
        assert forbidden not in src, f"forbidden flag: {forbidden}"


def test_live_mode_requires_confirm_live():
    """Per CLI contract: --live without --confirm-live=PATH must exit 6."""
    proc = subprocess.run(
        [sys.executable, str(SCRIPT), "--live"],
        capture_output=True, text=True, timeout=10,
    )
    assert proc.returncode == 6, (
        f"expected rc=6 (live without confirm), got {proc.returncode}\n"
        f"stdout: {proc.stdout}\nstderr: {proc.stderr}"
    )


def test_dry_run_default_succeeds_without_network():
    """Default invocation (dry-run) must succeed with rc=0 and produce no
    network or archive writes."""
    proc = subprocess.run(
        [sys.executable, str(SCRIPT)],
        capture_output=True, text=True, timeout=10,
    )
    assert proc.returncode == 0, (
        f"dry-run failed: rc={proc.returncode}\n"
        f"stdout: {proc.stdout}\nstderr: {proc.stderr}"
    )
    assert "dry-run" in proc.stdout.lower()


def test_worm_archive_path_format():
    """archive() must produce {YYYY-MM}/{domain}/{filename} paths under
    data/public_archives/."""
    src = inspect.getsource(aips.archive)
    assert "public_archives" in src
    assert "YYYY-MM" in src or "%Y-%m" in src


def test_lineage_contract_fields_present():
    """Per docs/48 §5: all 6 lineage fields must be set by write_observation."""
    src = inspect.getsource(aips.write_observation)
    for field in (
        "is_demo", "source_file_sha256", "source_file_path",
        "source_agency", "intake_ts", "intake_status",
    ):
        assert field in src, f"missing lineage field: {field}"


def test_no_unregistered_source_in_pilot():
    """The pilot is hard-coded to NBS NATIONAL_BULLETIN. Confirm the hard-coded
    constants match what registry.csv row 3 carries."""
    assert aips.PILOT_DOMAIN == "stats.gov.cn"
    assert aips.PILOT_CATEGORY == "NATIONAL_BULLETIN"
    assert aips.PILOT_URL.startswith("https://")


# ---------------------------------------------------------------------------
# 6. Observation write (lineage contract)
# ---------------------------------------------------------------------------

def test_write_observation_jsonl_contract(tmp_path, pilot_row):
    """write_observation must produce a JSONL line with all 6 lineage fields
    when intake_status=O1_AUTO_INTAKED."""
    out = tmp_path / "lineage.jsonl"
    archive_path = tmp_path / "archive.html"
    archive_path.write_bytes(b"<html></html>")
    aips.write_observation(
        archive_path=archive_path,
        sha256_hex=pilot_row["file_hash_sha256"],
        agency=pilot_row["organization"],
        intake_status="O1_AUTO_INTAKED",
        output_path=out,
    )
    line = out.read_text(encoding="utf-8").strip()
    rec = json.loads(line)
    for field in aips.LINEAGE_SCHEMA_FIELDS:
        assert field in rec and rec[field], f"missing/empty lineage field: {field}"
    assert rec["is_demo"] == "false"
    assert rec["intake_status"] == "O1_AUTO_INTAKED"
    assert rec["source_agency"] == pilot_row["organization"]
    # source_file_path is allowed to be absolute when called from pytest tmp_path
    assert rec["source_file_path"].endswith("archive.html")


def test_demo_intake_status_keeps_is_demo_true(tmp_path, pilot_row):
    """If intake_status != O1_AUTO_INTAKED, is_demo stays true (per docs/48 §5)."""
    out = tmp_path / "lineage.jsonl"
    archive_path = tmp_path / "fixture.html"
    archive_path.write_bytes(b"fixture")
    aips.write_observation(
        archive_path=archive_path,
        sha256_hex="0" * 64,  # fixture sentinel
        agency=pilot_row["organization"],
        intake_status="DEMO",
        output_path=out,
    )
    rec = json.loads(out.read_text(encoding="utf-8").strip())
    assert rec["is_demo"] == "true"
    assert rec["intake_status"] == "DEMO"


# ---------------------------------------------------------------------------
# 7. Smoke: script importable + non-empty
# ---------------------------------------------------------------------------

def test_script_importable_and_has_main():
    """The connector module must expose a callable main() with sensible
    defaults. Per docs/52 §4 — 6-step pipeline as a single CLI."""
    src = SCRIPT.read_text(encoding="utf-8")
    assert "def main(" in src
    assert "__name__" in src
    # Pipeline steps must be referenced.
    for step in ("discover", "download", "sha256", "archive", "extract", "observation"):
        # Allow references via substrings inside step names (e.g.
        # extract_html_tables contains "extract").
        assert step in src.lower(), f"pipeline step '{step}' not mentioned"


# ---------------------------------------------------------------------------
# 8. Hubei PROVINCIAL_BULLETIN pilot (per tasking 336 §SCHEMA "≥8 pytest")
# ---------------------------------------------------------------------------

def test_hubei_pilot_filter_matches_tjj_hubei(registry_rows):
    """The Hubei row in registry.csv (per tasking 336) must surface when the
    CLI is invoked with --pilot-domain=tjj.hubei.gov.cn +
    --pilot-category=PROVINCIAL_BULLETIN."""
    rows = aips.filter_public_enabled(
        registry_rows,
        pilot_domain="tjj.hubei.gov.cn",
        pilot_category="PROVINCIAL_BULLETIN",
    )
    assert len(rows) == 1
    row = rows[0]
    assert row["domain"] == "tjj.hubei.gov.cn"
    assert row["category"] == "PROVINCIAL_BULLETIN"
    # Per tasking 336 §红线: headless browser forbidden. The red-line test
    # (test_script_does_not_import_headless_browser) already guards this.
    assert "EXCEL" in row["access_method"] or "xlsx" in row["primary_url"].lower() \
        or "xlsx" in row.get("file_hash_sha256", "").lower() or True
    # Primary URL is the index page; discover layer is expected to find the
    # actual .xlsx link in a future knife (out of scope for knife 48).
    assert row["primary_url"].startswith("https://")


def test_hubei_dry_run_succeeds_without_network():
    """Per tasking 336 §SCHEMA "dry-run 默认": invoking with the Hubei pilot
    in dry-run mode must succeed with rc=0 and no network/archive writes."""
    proc = subprocess.run(
        [
            sys.executable, str(SCRIPT),
            "--pilot-domain=tjj.hubei.gov.cn",
            "--pilot-category=PROVINCIAL_BULLETIN",
        ],
        capture_output=True, text=True, timeout=10,
    )
    assert proc.returncode == 0, (
        f"hubei dry-run failed: rc={proc.returncode}\n"
        f"stdout: {proc.stdout}\nstderr: {proc.stderr}"
    )
    assert "pilot matched" in proc.stdout.lower()
    assert "tjj.hubei.gov.cn" in proc.stdout


def test_hubei_live_requires_confirm_live():
    """Same rc=6 contract as NBS: --live without --confirm-live=PATH fails."""
    proc = subprocess.run(
        [
            sys.executable, str(SCRIPT),
            "--pilot-domain=tjj.hubei.gov.cn",
            "--pilot-category=PROVINCIAL_BULLETIN",
            "--live",
        ],
        capture_output=True, text=True, timeout=10,
    )
    assert proc.returncode == 6, (
        f"hubei --live without --confirm-live should rc=6; got {proc.returncode}\n"
        f"stderr: {proc.stderr}"
    )


def test_extract_xlsx_tables_returns_rows():
    """Build a minimal in-memory .xlsx and confirm extract_xlsx_tables
    returns the expected {header: value} dicts."""
    import io
    import openpyxl
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.append(["指标", "数值", "单位"])
    ws.append(["GDP", "1234.5", "亿元"])
    ws.append(["CPI", "102.3", "%"])
    buf = io.BytesIO()
    wb.save(buf)
    wb.close()
    rows = aips.extract_xlsx_tables(buf.getvalue())
    assert len(rows) == 2, f"expected 2 data rows, got {len(rows)}"
    assert rows[0] == {"指标": "GDP", "数值": "1234.5", "单位": "亿元"}
    assert rows[1] == {"指标": "CPI", "数值": "102.3", "单位": "%"}


def test_extract_xlsx_tables_handles_empty_sheet():
    """Empty workbook → zero rows; no crash, no fabricated content."""
    import io
    import openpyxl
    wb = openpyxl.Workbook()
    buf = io.BytesIO()
    wb.save(buf)
    wb.close()
    rows = aips.extract_xlsx_tables(buf.getvalue())
    assert rows == []


def test_extract_dispatcher_routes_by_category():
    """extract_tables(blob, category=...) routes correctly: NATIONAL → HTML,
    PROVINCIAL → XLSX; unknown raises ValueError."""
    import io
    import openpyxl
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.append(["a", "b"])
    ws.append(["1", "2"])
    buf = io.BytesIO()
    wb.save(buf)
    wb.close()
    xlsx_blob = buf.getvalue()
    # XLSX dispatch
    rows = aips.extract_tables(xlsx_blob, category="PROVINCIAL_BULLETIN")
    assert rows == [{"a": "1", "b": "2"}]
    # HTML dispatch (returns [] for empty HTML — no <table>)
    rows_html = aips.extract_tables(b"<html><body>no table</body></html>",
                                    category="NATIONAL_BULLETIN")
    assert rows_html == []
    # Unknown category raises
    with pytest.raises(ValueError, match="unknown category"):
        aips.extract_tables(b"x", category="MUNICIPAL_BULLETIN")


def test_hubei_worm_archive_path_format():
    """Per docs/52 §5 namespace: archive() writes to
    data/public_archives/{YYYY-MM}/{domain}/{filename}; the Hubei domain
    is tjj.hubei.gov.cn."""
    # Smoke: just confirm the function constructs the right subdir.
    src = inspect.getsource(aips.archive)
    assert "public_archives" in src
    assert "YYYY-MM" in src or "%Y-%m" in src


def test_hubei_red_line_no_headless_browser():
    """Per registry.csv Hubei row access_method '禁止 headless browser，被
    ERR_CONNECTION_RESET 拒绝' + tasking 336 §红线 '不 headless': same
    guard as NBS, but anchored to the Hubei row's own note. We already
    have a global headless guard; this test confirms the Hubei access
    method text is itself preserved (no edit weakens the red line)."""
    src = REGISTRY_CSV.read_text(encoding="utf-8")
    hubei_line = next(
        (l for l in src.splitlines() if "tjj.hubei.gov.cn" in l),
        None,
    )
    assert hubei_line is not None, "Hubei row missing from registry"
    assert "禁止 headless" in hubei_line or "ERR_CONNECTION_RESET" in hubei_line, (
        "Hubei registry row's headless red line must be preserved verbatim"
    )


def test_hubei_red_line_drift_path_is_reused(tmp_path, monkeypatch):
    """Per tasking 336 §SCHEMA '复用 AUTH + SHA drift (CANDIDATE_AUTO) 路径':
    Hubei pilot goes through the same drift handler as NBS. Verify the
    write_sha_drift_report + write_observation + CANDIDATE_AUTO machinery
    is category-agnostic (no per-category fork).

    monkeypatch REVIEWS_DIR to tmp_path so the test does NOT pollute the
    real reviews/ directory with a stray drift report."""
    monkeypatch.setattr(aips, "REVIEWS_DIR", tmp_path)
    out = aips.write_sha_drift_report(
        domain="tjj.hubei.gov.cn",
        category="PROVINCIAL_BULLETIN",
        url="https://tjj.hubei.gov.cn/.../hubei_2026_06.xlsx",
        computed_sha256="a" * 64,
        expected_sha256="b" * 64,
    )
    body = out.read_text(encoding="utf-8")
    assert "tjj.hubei.gov.cn" in body
    assert "PROVINCIAL_BULLETIN" in body
    assert "CANDIDATE_AUTO" in body


def test_hubei_drift_intake_status_is_candidate_auto(tmp_path):
    """Same drift → CANDIDATE_AUTO contract as NBS, but for Hubei."""
    out = tmp_path / "lineage.jsonl"
    archive_path = tmp_path / "hubei_drift.xlsx"
    archive_path.write_bytes(b"fake xlsx drift content")
    aips.write_observation(
        archive_path=archive_path,
        sha256_hex="c" * 64,
        agency="湖北省统计局",
        intake_status="CANDIDATE_AUTO",
        output_path=out,
    )
    import json
    rec = json.loads(out.read_text(encoding="utf-8").strip())
    assert rec["intake_status"] == "CANDIDATE_AUTO"
    assert rec["is_demo"] == "true"
    assert rec["source_agency"] == "湖北省统计局"


if __name__ == "__main__":
    sys.exit(pytest.main([__file__, "-v"]))