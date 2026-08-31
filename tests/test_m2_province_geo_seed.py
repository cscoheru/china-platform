#!/usr/bin/env python3
"""M2-a — tests for scripts/seed_m2_province_geo.py + coverage script.

Per knife 631 §1.D (4 cases):
  1. 31 省 geo_entity 存在 (level=PROVINCE)
  2. 湖北 M1 行未重复 (geo_code_version 不冲突)
  3. inventory CSV ≥31 行 + 无「仅根首页」FETCHED
  4. coverage 脚本 exit 0 且打印 KPI 行

Required fixtures:
  * cegr_test DSN reachable at postgresql://postgres:postgres@127.0.0.1:55440/cegr_test
  * scripts/seed_m2_province_geo.py --load already run (or runs as a fixture)
  * source_registry/m2_2024_gdp_inventory.csv present with 32 lines
"""
from __future__ import annotations

import csv
import importlib
import subprocess
import sys
from pathlib import Path

import psycopg2
import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent
SCRIPTS_DIR = REPO_ROOT / "scripts"
INVENTORY_CSV = REPO_ROOT / "source_registry" / "m2_2024_gdp_inventory.csv"
COVERAGE_SCRIPT = SCRIPTS_DIR / "report_m2_gdp_coverage.py"

DSN = "postgresql://postgres:postgres@127.0.0.1:55440/cegr_test"

HUBEI_PROVINCE_ID = "a1000000-0000-0000-0000-000000000001"

# Make scripts importable
sys.path.insert(0, str(SCRIPTS_DIR))
# Stub seed_m1 for the case where M1 seed module is unavailable
try:
    import seed_m1_reference_data as _seed_m1  # noqa: E402
except ImportError:
    _seed_m1 = None  # type: ignore

import seed_m2_province_geo as seed  # noqa: E402


@pytest.fixture(scope="module")
def loaded_seed() -> None:
    """Ensure both M1 (Hubei baseline) and M2-a seeds are loaded.

    pytest's conftest drops+re-applies the schema at session start, which
    wipes all data; we therefore re-run M1 first (so Hubei geo_code_version
    exists) then M2-a (which skips Hubei geo_code_version to avoid
    daterange EXCLUDE conflict).
    """
    # M1 seed (Hubei geo_entity + geo_code_version + indicator + observation)
    if _seed_m1 is not None:
        try:
            _seed_m1.load_seed(verbose=False)
        except Exception as exc:  # noqa: BLE001
            # If M1 seed fails (e.g. registry not imported yet), skip — the
            # Hubei geo_code_version test will then correctly assert 0 (no M1).
            print(f"[fixture] M1 seed skipped: {exc}")

    # M2-a seed (31 provinces + 30 code versions + 1 CODE_REFERENCE row)
    seed.load_seed(verbose=False)


@pytest.fixture(scope="module")
def conn():
    c = psycopg2.connect(DSN)
    yield c
    c.close()


# ---------------------------------------------------------------------
# Case 1 — 31 省 geo_entity 存在
# ---------------------------------------------------------------------


def test_31_province_geo_entities_exist(loaded_seed, conn):
    """Asserts cegr.geo_entity has 31 rows at level='PROVINCE'."""
    with conn.cursor() as cur:
        cur.execute(
            """
            SELECT COUNT(*) FROM cegr.geo_entity
            WHERE level = 'PROVINCE'
            """
        )
        count = cur.fetchone()[0]
    assert count == 31, f"expected 31 PROVINCE rows; got {count}"


def test_provinces_include_hubei_and_30_m2_namespaces(loaded_seed, conn):
    """Asserts Hubei uses M1 namespace + 30 provinces use M2 namespace a2000000-."""
    with conn.cursor() as cur:
        cur.execute(
            """
            SELECT id::text, canonical_name FROM cegr.geo_entity
            WHERE level = 'PROVINCE'
            ORDER BY canonical_name
            """
        )
        rows = cur.fetchall()

    by_name = {name: gid for gid, name in rows}
    # Hubei present (M1 namespace)
    assert by_name.get("湖北省") == HUBEI_PROVINCE_ID, (
        f"Hubei not on M1 UUID: got {by_name.get('湖北省')}"
    )
    # 30 non-Hubei provinces on M2 namespace
    m2_count = sum(1 for gid in by_name.values() if gid.startswith("a2000000-"))
    assert m2_count == 30, f"expected 30 M2-namespace provinces; got {m2_count}"


# ---------------------------------------------------------------------
# Case 2 — 湖北 M1 行未重复冲突
# ---------------------------------------------------------------------


def test_hubei_geo_code_version_not_duplicated(loaded_seed, conn):
    """Asserts geo_code_version has at most one row per Hubei daterange period.

    M1 seeded Hubei at valid_from='2026-01-01'.
    M2-a skips Hubei in geo_code_version (knife 631 §1.A) — daterange EXCLUDE
    constraint must not conflict.
    """
    with conn.cursor() as cur:
        cur.execute(
            """
            SELECT COUNT(*) FROM cegr.geo_code_version
            WHERE geo_entity_id = %s
            """,
            (HUBEI_PROVINCE_ID,),
        )
        count = cur.fetchone()[0]
    # M1 only — M2-a explicitly skips Hubei to avoid daterange conflict
    assert count == 1, (
        f"expected exactly 1 geo_code_version for Hubei (M1); got {count}"
    )


def test_30_m2_geo_code_versions_at_2024(loaded_seed, conn):
    """Asserts 30 M2-namespace provinces have a geo_code_version at valid_from='2024-01-01'."""
    with conn.cursor() as cur:
        cur.execute(
            """
            SELECT COUNT(*) FROM cegr.geo_code_version gcv
            JOIN cegr.geo_entity g ON g.id = gcv.geo_entity_id
            WHERE g.id::text LIKE 'a2000000-%'
              AND gcv.valid_from = '2024-01-01'
            """
        )
        count = cur.fetchone()[0]
    assert count == 30, f"expected 30 M2-namespace code versions; got {count}"


# ---------------------------------------------------------------------
# Case 3 — inventory CSV ≥31 行 + 无「仅根首页」FETCHED
# ---------------------------------------------------------------------


def test_inventory_has_at_least_31_rows():
    """Asserts the inventory CSV has at least 32 lines (1 header + 31 data)."""
    with INVENTORY_CSV.open("r", encoding="utf-8") as fh:
        lines = [ln for ln in fh if ln.strip()]
    assert len(lines) >= 32, (
        f"expected ≥32 lines (header + 31); got {len(lines)}"
    )


def test_inventory_status_distribution():
    """Asserts the inventory CSV has 30 PENDING + 1 BLOCKED for 31 rows."""
    pending = 0
    blocked = 0
    fetched = 0
    fetched_root_only = 0
    with INVENTORY_CSV.open("r", encoding="utf-8") as fh:
        reader = csv.DictReader(fh)
        for row in reader:
            status = (row.get("status") or "").strip()
            if status == "PENDING":
                pending += 1
            elif status == "BLOCKED":
                blocked += 1
            elif status == "FETCHED":
                fetched += 1
                url = (row.get("candidate_url") or "").rstrip("/")
                # Root homepage only (e.g. https://tjj.beijing.gov.cn/)
                # vs. deeper path like .../tjsj/sjcx/tjgb/
                # Block-level URLs that go directly to statistics
                # section/category pages are OK.
                last = url.rsplit("/", 1)[-1]
                if last == "":
                    fetched_root_only += 1
    assert pending >= 30, f"expected ≥30 PENDING rows; got {pending}"
    assert blocked >= 1, f"expected ≥1 BLOCKED row; got {blocked}"
    # Knife 631 §1.B: 不锁省统计局首页当表源
    assert fetched == 0, (
        f"per knife 631 §1.B, no row may be FETCHED in M2-a; got {fetched}"
    )
    assert fetched_root_only == 0, (
        f"per knife 631 §1.B, no root-homepage FETCHED allowed; got {fetched_root_only}"
    )


# ---------------------------------------------------------------------
# Case 4 — coverage 脚本 exit 0 且打印 KPI 行
# ---------------------------------------------------------------------


def test_coverage_script_exits_zero():
    """Asserts report_m2_gdp_coverage.py exits 0 and prints KPI line."""
    proc = subprocess.run(
        [sys.executable, str(COVERAGE_SCRIPT)],
        capture_output=True,
        text=True,
        timeout=60,
    )
    assert proc.returncode == 0, (
        f"coverage script exited {proc.returncode}: {proc.stderr}"
    )
    # KPI line is required output
    assert "KPI (per knife 631 §2)" in proc.stdout, (
        f"KPI line missing from coverage output:\n{proc.stdout[:1000]}"
    )
    # 31 省级 rows mentioned
    assert "31 省级" in proc.stdout, "31 省级 header missing"


def test_coverage_script_includes_hubei_blocked():
    """Asserts Hubei shows BLOCKED verdict (M1 sample is 2026H1, not 2024 annual)."""
    proc = subprocess.run(
        [sys.executable, str(COVERAGE_SCRIPT)],
        capture_output=True,
        text=True,
        timeout=60,
    )
    assert proc.returncode == 0
    # Hubei row should appear with BLOCKED verdict
    hubei_lines = [l for l in proc.stdout.splitlines() if "湖北省" in l]
    assert hubei_lines, "Hubei row missing from coverage output"
    assert any("BLOCKED" in ln for ln in hubei_lines), (
        f"Hubei should be BLOCKED, got: {hubei_lines}"
    )