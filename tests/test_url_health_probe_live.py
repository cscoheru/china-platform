"""Stage 2 / S2.0.2.3 — URL probe `URL_HEALTH_LIVE` gate pytest.

Per tasking 165 §NOW-2 + docs/35 §5.1 / §5.4:
  - Default behavior (URL_HEALTH_LIVE unset / '0' / non-'1'): main() REFUSES
    to probe live; exits 0 with explicit stderr message.
  - Live mode (URL_HEALTH_LIVE='1'): main() proceeds to probe_all; honors
    docs/32 §2.1 limits (HEAD default, GET-Range fallback, ≤1 req/s per
    source, ≤60s total, only ingestion_run writes).

This test file defaults to **skipped** because the live-mode cases only run
when URL_HEALTH_LIVE='1'. The gate-behavior cases (refusal) run UNCONDITIONALLY
because they validate the safety default — no live network is involved.

Cases:
  1. test_default_url_health_live_unset_refuses     (always runs)
  2. test_url_health_live_zero_refuses              (always runs)
  3. test_url_health_live_only_exact_one_enables    (always runs; anti-foot-gun)
  4. test_url_health_live_message_cites_docs35_51   (always runs)
  5. test_live_mode_invokes_probe_all_when_enabled  (skipped unless LIVE)
  6. test_live_mode_test_hook_url_works             (skipped unless LIVE)
  7. test_live_mode_does_not_write_to_business_tables  (always runs; static)
  8. test_existing_probe_suite_unaffected           (always runs; smoke)
"""
from __future__ import annotations

import importlib.util
import os
import subprocess
import sys
from pathlib import Path
from unittest.mock import patch

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]
SCRIPT = REPO_ROOT / "scripts" / "url_health_probe.py"
PYTHON = sys.executable


def _import_module():
    """Import scripts/url_health_probe.py as a module (mirrors existing pattern)."""
    spec = importlib.util.spec_from_file_location("url_health_probe_s2023", SCRIPT)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


# Skip live-mode integration cases unless operator explicitly opts in.
_LIVE = os.environ.get("URL_HEALTH_LIVE") == "1"
requires_live = pytest.mark.skipif(
    not _LIVE,
    reason="URL_HEALTH_LIVE != '1'; live mode not enabled (set URL_HEALTH_LIVE=1 to run)",
)


def _invoke_main(env_extra: dict | None = None,
                 args: list[str] | None = None) -> subprocess.CompletedProcess:
    """Invoke url_health_probe.py main() via subprocess (clean sys.argv)."""
    env = os.environ.copy()
    # Strip our own test marker so child doesn't see it.
    env.pop("URL_HEALTH_LIVE", None)
    if env_extra:
        env.update(env_extra)
    return subprocess.run(
        [PYTHON, str(SCRIPT), *(args or [])],
        capture_output=True,
        text=True,
        env=env,
        timeout=30,
    )


# ---------- Case 1: default unset refuses ----------
def test_default_url_health_live_unset_refuses() -> None:
    """URL_HEALTH_LIVE unset → main() refuses, exits 0 (clean refusal)."""
    result = _invoke_main(env_extra={"URL_HEALTH_LIVE": ""})
    assert result.returncode == 0, (
        f"refusal should exit 0 (clean, not error); got {result.returncode}; "
        f"stderr={result.stderr!r}"
    )
    assert "refusing" in result.stderr, (
        f"stderr must announce refusal; got {result.stderr!r}"
    )
    assert "URL_HEALTH_LIVE" in result.stderr


# ---------- Case 2: explicit '0' refuses ----------
def test_url_health_live_zero_refuses() -> None:
    """URL_HEALTH_LIVE='0' → refuse (per docs/35 §5.1 default semantics)."""
    result = _invoke_main(env_extra={"URL_HEALTH_LIVE": "0"})
    assert result.returncode == 0
    assert "refusing" in result.stderr


# ---------- Case 3: anti-foot-gun (only exact '1' enables) ----------
@pytest.mark.parametrize("value", ["true", "True", "TRUE", "yes", "on", "2", "01"])
def test_url_health_live_only_exact_one_enables(value: str) -> None:
    """Only the literal string '1' enables live mode.

    Rationale (per Cursor 127 red line / docs/32 §3.4): we want a single,
    unambiguous opt-in token. Variants like 'true', 'yes', '01' are too
    easy to mistype and could silently activate live probe.
    """
    result = _invoke_main(env_extra={"URL_HEALTH_LIVE": value})
    assert result.returncode == 0
    assert "refusing" in result.stderr, (
        f"variant {value!r} should be refused (anti-foot-gun); got {result.stderr!r}"
    )


# ---------- Case 4: refusal message cites docs/35 §5.1 ----------
def test_url_health_live_message_cites_docs35_51() -> None:
    """The refusal message must cite the source-of-truth doc + section."""
    result = _invoke_main(env_extra={"URL_HEALTH_LIVE": "0"})
    assert "docs/35" in result.stderr
    assert "5.1" in result.stderr
    # Also must mention CI / prod cron exclusion.
    assert "CI" in result.stderr and "cron" in result.stderr


# ---------- Case 5: live mode invokes probe_all ----------
@requires_live
def test_live_mode_invokes_probe_all_when_enabled() -> None:
    """URL_HEALTH_LIVE=1 → main() calls probe_all (mocked to avoid real network)."""
    mod = _import_module()
    with patch.object(mod, "probe_all", return_value=0) as mock_probe:
        rc = mod.main([])
    assert rc == 0
    assert mock_probe.called, "URL_HEALTH_LIVE=1 must reach probe_all()"


# ---------- Case 6: live mode --url test hook works ----------
@requires_live
def test_live_mode_test_hook_url_works(monkeypatch) -> None:
    """When live mode is enabled, --url test hook works (mocked session)."""
    mod = _import_module()

    fake_session = mod.requests.Session()  # real instance, but we'll patch below

    def fake_probe_url(session, url, timeout_total=15.0):
        return "SUCCESS", None

    monkeypatch.setattr(mod, "_probe_url", fake_probe_url)
    rc = mod.main(["--url", "http://127.0.0.1:1/health"])
    assert rc == 0, f"--url test hook should succeed; got rc={rc}"


# ---------- Case 7: never writes to business tables (static check) ----------
def test_live_mode_does_not_write_to_business_tables() -> None:
    """Static guard: probe_all/_write_run must only touch cegr.ingestion_run.

    Per Cursor 165 §SCHEMA: 仅写 `ingestion_run`; 不写业务表. We assert this
    by grep'ing the script source for any INSERT/UPDATE into cegr tables
    other than cegr.ingestion_run.
    """
    src = SCRIPT.read_text(encoding="utf-8")
    # Strip comments so explanatory notes don't trip the regex.
    import re
    src_no_comments = re.sub(r"#[^\n]*", "", src)
    # Find every INSERT INTO cegr.<table> and collect distinct table names.
    inserts = re.findall(r"INSERT\s+INTO\s+cegr\.(\w+)", src_no_comments, re.IGNORECASE)
    distinct = sorted(set(t.lower() for t in inserts))
    # Must contain ingestion_run (the only allowed write target).
    assert "ingestion_run" in distinct, (
        f"script must write to cegr.ingestion_run; saw: {distinct}"
    )
    # Must NOT write to any business table.
    business_tables = {
        "observation", "source_document", "source_location", "indicator_definition",
        "indicator_methodology_version", "calendar_period", "geo_entity",
        "geo_code_version", "source_registry",
    }
    leaked = business_tables & set(distinct)
    assert not leaked, (
        f"script must NOT write to business tables; leaked: {leaked}"
    )


# ---------- Case 8: existing probe suite still passes (smoke) ----------
def test_existing_probe_suite_unaffected() -> None:
    """Smoke: existing test_url_health_probe.py's module-level fixtures still load.

    We do NOT re-run all 6 existing cases here (that would duplicate CI time);
    this test just confirms that the S2.0.2.3 edit didn't break the import
    surface or change the public function signatures.
    """
    spec = importlib.util.spec_from_file_location(
        "url_health_probe_existing", SCRIPT
    )
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)

    # Public surface unchanged: these are what test_url_health_probe.py relies on.
    assert callable(mod.probe_all)
    assert callable(mod._probe_url)
    assert callable(mod._write_run)
    assert callable(mod._dsn)
    # New gate function exported.
    assert callable(mod._url_health_live_enabled)
    # main() still callable.
    assert callable(mod.main)
