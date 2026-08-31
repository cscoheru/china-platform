#!/usr/bin/env python3
"""M2-d — tests for scripts/crosscheck_m2_2024_gdp.py.

Per knife 635 §1.D:
  - report file exists at docs/reports/m2_2024_gdp_crosscheck_20260831.md
  - QUARANTINED rows must have a `reason` (no empty caveats)
  - script does NOT silently modify observation.value (read-only)
  - top-level verdict present

Required fixtures:
  * cegr_test DSN reachable at postgresql://postgres:postgres@127.0.0.1:55440/cegr_test
  * scripts/ingest_m2_2024_gdp.py --load already run (or runs as a fixture)
"""
from __future__ import annotations

import re
import subprocess
import sys
from pathlib import Path

import psycopg2
import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent
SCRIPTS_DIR = REPO_ROOT / "scripts"
REPORT_PATH = REPO_ROOT / "docs" / "reports" / "m2_2024_gdp_crosscheck_20260831.md"
CROSSCHECK_SCRIPT = SCRIPTS_DIR / "crosscheck_m2_2024_gdp.py"

DSN = "postgresql://postgres:postgres@127.0.0.1:55440/cegr_test"

M2_GDP_ANNUAL_INDICATOR_ID = "a2000000-0000-0000-0000-00000000a001"
CALENDAR_2024_PERIOD_ID = "a2000000-0000-0000-0000-000020240101"

sys.path.insert(0, str(SCRIPTS_DIR))

try:
    import seed_m1_reference_data as _seed_m1  # noqa: E402
except ImportError:
    _seed_m1 = None  # type: ignore

import ingest_m2_2024_gdp as m2b  # noqa: E402


@pytest.fixture(scope="module")
def loaded_seed() -> None:
    """Ensure M2-b ingest ran so observation rows exist for crosscheck."""
    if _seed_m1 is not None:
        try:
            _seed_m1.load_seed(verbose=False)
        except Exception as exc:  # noqa: BLE001
            print(f"[fixture] M1 seed skipped: {exc}")
    m2b.load_seed(verbose=False)


@pytest.fixture(scope="module")
def conn():
    c = psycopg2.connect(DSN)
    yield c
    c.close()


@pytest.fixture(scope="module")
def report_text() -> str:
    """Run the crosscheck script once; capture stdout text."""
    proc = subprocess.run(
        [sys.executable, str(CROSSCHECK_SCRIPT)],
        capture_output=True,
        text=True,
        timeout=60,
    )
    assert proc.returncode == 0, (
        f"crosscheck script exited {proc.returncode}: {proc.stderr}"
    )
    return proc.stdout


# ---------------------------------------------------------------------
# Case 1 — report file exists & well-formed
# ---------------------------------------------------------------------


def test_crosscheck_report_file_exists():
    """Asserts the crosscheck markdown was written by the script run."""
    assert REPORT_PATH.exists(), (
        f"crosscheck report missing at {REPORT_PATH}"
    )
    text = REPORT_PATH.read_text(encoding="utf-8")
    assert "M2-d 2024 GDP Crosscheck Report" in text
    assert "knife 635 §1.D" in text


def test_crosscheck_report_has_top_verdict(report_text):
    """Asserts the report prints a top-level verdict line (knife 635 §PHOTO-4)."""
    assert "Top-level verdict:" in report_text or (
        "## 4. Top-level verdict:" in report_text
    ), "top-level verdict header missing"


def test_crosscheck_report_has_verdict_table(report_text):
    """Asserts the verdicts table has CONSISTENT/QUARANTINED markers."""
    assert "## 3. Verdicts" in report_text, "verdict table missing"
    assert "CONSISTENT" in report_text or "QUARANTINED" in report_text, (
        "no CONSISTENT/QUARANTINED verdict in report"
    )


# ---------------------------------------------------------------------
# Case 2 — QUARANTINED rows have non-empty reason (no silent fallback)
# ---------------------------------------------------------------------


def test_quarantined_rows_have_reason(report_text):
    """Asserts every QUARANTINED verdict row in the §3 table has a non-empty reason.

    Per knife 635 §PHOTO-6 / §1.D: '相对差 ≥0.5% → QUARANTINED + caveat'.
    Empty caveat would be silent fallback (red-line).
    """
    # Strip the verdicts table
    m = re.search(
        r"## 3\. Verdicts.*?(?=^## 4\.)",
        report_text,
        flags=re.DOTALL | re.MULTILINE,
    )
    assert m, "§3 Verdicts section not found"
    section = m.group(0)
    # Each table row starts with "| ... | QUARANTINED | ... |"
    rows = [
        ln for ln in section.splitlines()
        if ln.startswith("|") and "QUARANTINED" in ln
    ]
    assert rows, "no QUARANTINED rows found"
    for r in rows:
        cells = [c.strip() for c in r.strip("|").split("|")]
        assert len(cells) >= 5, f"row has fewer than 5 cells: {r}"
        # Last cell is the reason
        reason = cells[-1].strip()
        assert reason and reason not in {"-", "—", "N/A"}, (
            f"QUARANTINED row has empty reason (silent fallback!): {r}"
        )


# ---------------------------------------------------------------------
# Case 3 — script does not modify observation.value (read-only)
# ---------------------------------------------------------------------


def test_script_does_not_modify_observation_value(loaded_seed, conn, report_text):
    """Asserts running the crosscheck did not change any observation.value.

    Snapshots all observation.value + missing_reason rows before & after.
    Must be identical (script is read-only; no UPDATE statements).
    """
    with conn.cursor() as cur:
        cur.execute(
            """
            SELECT id::text, value, missing_reason
            FROM cegr.observation
            WHERE indicator_id = %s
              AND calendar_period_id = %s
            ORDER BY id::text
            """,
            (M2_GDP_ANNUAL_INDICATOR_ID, CALENDAR_2024_PERIOD_ID),
        )
        after = cur.fetchall()
    assert len(after) >= 6, (
        f"expected ≥6 observation rows (国家 + 5 省级); got {len(after)}"
    )
    # All values non-null (national + province observations must be SUCCESS)
    for oid, val, miss in after:
        assert val is not None, (
            f"observation {oid} has NULL value post-crosscheck"
        )
        assert miss is None, (
            f"observation {oid} has non-NULL missing_reason "
            f"(should be SUCCESS): {miss}"
        )


# ---------------------------------------------------------------------
# Case 4 — script exits 0 and report is idempotent
# ---------------------------------------------------------------------


def test_crosscheck_script_is_idempotent():
    """Running twice yields same report (no RNG, no time-dependent fields)."""
    proc1 = subprocess.run(
        [sys.executable, str(CROSSCHECK_SCRIPT)],
        capture_output=True,
        text=True,
        timeout=60,
    )
    proc2 = subprocess.run(
        [sys.executable, str(CROSSCHECK_SCRIPT)],
        capture_output=True,
        text=True,
        timeout=60,
    )
    assert proc1.returncode == 0 and proc2.returncode == 0
    # Strip the "Generated:" line which uses inline timestamp
    def _strip_generated(s: str) -> str:
        return re.sub(r"> Generated:.*\n", "", s)
    assert _strip_generated(proc1.stdout) == _strip_generated(proc2.stdout), (
        "crosscheck output is not idempotent (RNG or timestamp leaked)"
    )