"""Stage 1 / S1.16 — R03 / docs/10 §2.4 dbt 阈值测试 自动化入口.

Per docs/31 §3.2 + tasking 121 §NOW-2:
  - 缺 .venv-dbt 环境 → skip (不 fail; 缺环境≠逻辑错)
  - 干净 → dbt test PASS
  - PENDING NEEDS_REVIEW → FAIL (断言 >5% 冲突未闭环)
  - RESOLVED (resolution≠PENDING) → PASS (已有人工核查结论放行)
  - S0↔S1 8% PENDING → PASS (docs/10 §2.4 分层: 记录不阻塞)

每个用例: TRUNCATE observation CASCADE + 清 dbt mart (--full-refresh) → 装 fixture → dbt run → dbt test → 断言 rc 与 mart 状态.
"""

from __future__ import annotations

import os
import shutil
import subprocess
import sys
import uuid
from decimal import Decimal
from pathlib import Path

import psycopg2
import psycopg2.extras
import pytest

psycopg2.extras.register_uuid()

DSN = os.environ.get(
    "STAGE0_DSN",
    "postgresql://postgres:postgres@127.0.0.1:55440/cegr_test",
)

DBT_DIR    = Path(__file__).resolve().parents[1] / "dbt"
VENV_BIN   = Path(__file__).resolve().parents[1] / ".venv-dbt" / "bin" / "dbt"
PROJ       = str(DBT_DIR)
DBT_SELECT = "+mart_source_disagreement"
TEST_SELECT = "test_cross_source_consistency_threshold"


def _venv_dbt() -> str | None:
    """Return vbt CLI path if .venv-dbt/bin/dbt exists, else None.

    Robust against pytest's sys.path manipulation: try __file__-relative first,
    then walk up parents searching for .venv-dbt/bin/dbt. dbt 1.12 dropped
    `python -m dbt` (dbt is now a package), so the venv's CLI entrypoint is
    .venv-dbt/bin/dbt.
    """
    candidates = [Path(__file__).resolve().parents[1] / ".venv-dbt" / "bin" / "dbt"]
    for parent in Path(__file__).resolve().parents:
        candidates.append(parent / ".venv-dbt" / "bin" / "dbt")
    for c in candidates:
        if c.exists():
            return str(c)
    return None


def _connect():
    return psycopg2.connect(DSN)


def _wipe_obs():
    with _connect() as conn:
        with conn.cursor() as cur:
            cur.execute("TRUNCATE cegr.observation CASCADE")
        conn.commit()


def _dbt(venv, *args):
    return subprocess.run(
        [venv, *args],
        cwd=PROJ, capture_output=True, text=True, timeout=180,
    )


# Stable fixture UUIDs (prefix f3000000-; obs IDs use ...c% scoped)
IND      = uuid.UUID("f3000000-0000-0000-0000-000000000001")
GEO      = uuid.UUID("f3000000-0000-0000-0000-000000000002")
PERIOD   = uuid.UUID("f3000000-0000-0000-0000-000000000003")
SRC_A    = uuid.UUID("f3000000-0000-0000-0000-00000000a001")
SRC_B    = uuid.UUID("f3000000-0000-0000-0000-00000000a002")
SRC_C    = uuid.UUID("f3000000-0000-0000-0000-00000000a003")
DOC_A    = uuid.UUID("f3000000-0000-0000-0000-00000000b001")
DOC_B    = uuid.UUID("f3000000-0000-0000-0000-00000000b002")
DOC_C    = uuid.UUID("f3000000-0000-0000-0000-00000000b003")
IND_METH = uuid.UUID("f3000000-0000-0000-0000-00000000d001")
GEO_VER  = uuid.UUID("f3000000-0000-0000-0000-00000000d002")
LOC_A    = uuid.UUID("f3000000-0000-0000-0000-00000000e001")
LOC_B    = uuid.UUID("f3000000-0000-0000-0000-00000000e002")
LOC_C    = uuid.UUID("f3000000-0000-0000-0000-00000000e003")
OBS_A    = uuid.UUID("f3000000-0000-0000-0000-00000000c001")
OBS_B    = uuid.UUID("f3000000-0000-0000-0000-00000000c002")


@pytest.fixture(scope="module", autouse=True)
def _fixtures():
    """FK chain (no observations) seeded once; observations added per test."""
    try:
        with _connect() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    "INSERT INTO cegr.indicator_definition "
                    "(id, canonical_name, unit_canonical, frequency) "
                    "VALUES (%s, 'TEST_IND_R03', 'CNY', 'YEARLY') "
                    "ON CONFLICT (id) DO NOTHING", (str(IND),))
                cur.execute(
                    "INSERT INTO cegr.geo_entity (id, canonical_name, level) "
                    "VALUES (%s, 'TEST_GEO_R03', 'PROVINCE') "
                    "ON CONFLICT (id) DO NOTHING", (str(GEO),))
                cur.execute(
                    "INSERT INTO cegr.calendar_period "
                    "(id, period_label, start_date, end_date, period_type) "
                    "VALUES (%s, '2099-R03', '2099-01-01', '2099-12-31', 'CALENDAR_YEAR') "
                    "ON CONFLICT (id) DO NOTHING", (str(PERIOD),))
                for sid, org, url, decl_lvl in [
                    (SRC_A, 'TEST_A', 'http://test.local/r03-a', 'S0'),
                    (SRC_B, 'TEST_B', 'http://test.local/r03-b', 'S0'),
                    (SRC_C, 'TEST_C', 'http://test.local/r03-c', 'S1'),
                ]:
                    cur.execute(
                        "INSERT INTO cegr.source_registry "
                        "(id, domain, organization, category, primary_url, "
                        " access_method, source_level, declared_source_level, "
                        " update_frequency, enabled, auth_note) "
                        "VALUES (%s, 'test.local', %s, 'TEST', %s, "
                        " 'API', 'S0', %s, 'AD_HOC', TRUE, 'test') "
                        "ON CONFLICT (id) DO NOTHING",
                        (str(sid), org, url, decl_lvl))
                for did, sid, lvl, h in [
                    (DOC_A, SRC_A, 'S0', 'a'),
                    (DOC_B, SRC_B, 'S0', 'b'),
                    (DOC_C, SRC_C, 'S1', 'c'),
                ]:
                    cur.execute(
                        "INSERT INTO cegr.source_document "
                        "(id, source_registry_id, source_level, verification_status, "
                        " title, publisher, url, file_path, file_hash_sha256, "
                        " file_format, extraction_method, copyright_note, uploader_id) "
                        "VALUES (%s, %s, %s, 'VERIFIED', 'fixture r03', 'TEST', "
                        " 'http://test/r03', '/tmp/r03', repeat(%s, 64), 'csv', "
                        " 'CSV_PARSE', '公开 / 著作权法第五条 / fixture', 'test-fixture') "
                        "ON CONFLICT (id) DO NOTHING",
                        (str(did), str(sid), lvl, h))
                cur.execute(
                    "INSERT INTO cegr.indicator_methodology_version "
                    "(id, indicator_id, version_label, valid_from, "
                    " change_summary, source_id) "
                    "VALUES (%s, %s, 'v1-r03', '2020-01-01', 'test', %s) "
                    "ON CONFLICT (id) DO NOTHING",
                    (str(IND_METH), str(IND), str(DOC_A)))
                cur.execute(
                    "INSERT INTO cegr.geo_code_version "
                    "(id, geo_entity_id, admin_code, valid_from, source_id) "
                    "VALUES (%s, %s, 'TEST-R03', '2020-01-01', %s) "
                    "ON CONFLICT (id) DO NOTHING",
                    (str(GEO_VER), str(GEO), str(DOC_A)))
                for lid, did in [(LOC_A, DOC_A), (LOC_B, DOC_B), (LOC_C, DOC_C)]:
                    cur.execute(
                        "INSERT INTO cegr.source_location "
                        "(id, source_document_id, sheet_name) "
                        "VALUES (%s, %s, 'sheet') "
                        "ON CONFLICT (id) DO NOTHING",
                        (str(lid), str(did)))
            conn.commit()
    except Exception as e:
        pytest.skip(f"Fixture seed failed: {e}", allow_module_level=True)


@pytest.fixture(autouse=True)
def _wipe_between_tests():
    _wipe_obs()
    yield
    _wipe_obs()


def _insert_pair(value_a: Decimal, value_b: Decimal,
                 doc_b: uuid.UUID = DOC_B, loc_b: uuid.UUID = LOC_B):
    """Seed a pair of observations under the same (indicator, geo, period)
    with different sources. doc_b/loc_b parameterize the B side so S0↔S0
    (default DOC_B) and S0↔S1 (DOC_C, source_level='S1' from fixture) can
    be exercised without UPDATE — blocked by source_document_immutable().
    """
    with _connect() as conn:
        with conn.cursor() as cur:
            cur.execute(
                "INSERT INTO cegr.observation "
                "(id, indicator_id, indicator_methodology_version_id, "
                " geo_entity_id, geo_code_version_id, calendar_period_id, "
                " value, unit, comparison_basis, value_type, status, "
                " source_id, source_location_id, extraction_method, "
                " period_label, period_type) "
                "VALUES (%s, %s, %s, %s, %s, %s, %s, 'CNY', 'NOMINAL', "
                " 'FACT', 'FINAL', %s, %s, 'CSV_PARSE', '2099-R03', 'CALENDAR_YEAR') "
                "ON CONFLICT (id) DO NOTHING",
                (str(OBS_A), str(IND), str(IND_METH), str(GEO), str(GEO_VER),
                 str(PERIOD), value_a, str(DOC_A), str(LOC_A)))
            cur.execute(
                "INSERT INTO cegr.observation "
                "(id, indicator_id, indicator_methodology_version_id, "
                " geo_entity_id, geo_code_version_id, calendar_period_id, "
                " value, unit, comparison_basis, value_type, status, "
                " source_id, source_location_id, extraction_method, "
                " period_label, period_type) "
                "VALUES (%s, %s, %s, %s, %s, %s, %s, 'CNY', 'NOMINAL', "
                " 'FACT', 'FINAL', %s, %s, 'CSV_PARSE', '2099-R03', 'CALENDAR_YEAR') "
                "ON CONFLICT (id) DO NOTHING",
                (str(OBS_B), str(IND), str(IND_METH), str(GEO), str(GEO_VER),
                 str(PERIOD), value_b, str(doc_b), str(loc_b)))
        conn.commit()


def _mart_rows():
    with _connect() as conn:
        with conn.cursor() as cur:
            cur.execute(
                "SELECT severity, resolution, source_a_level, source_b_level "
                "FROM cegr_staging.mart_source_disagreement "
                "WHERE indicator_id = %s",
                (str(IND),))
            return cur.fetchall()


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------

def test_dbt_env_available():
    """缺 .venv-dbt 跳过 (docs/31 §3.2); 在场则 --version 可执行."""
    venv = _venv_dbt()
    if venv is None:
        pytest.skip(".venv-dbt not built; run: python3.11 -m venv .venv-dbt "
                    "&& .venv-dbt/bin/pip install -r requirements-dbt.txt")
    r = _dbt(venv, "--version")
    assert r.returncode == 0
    # dbt 1.12 输出格式: "Core:\n  - installed: 1.12.3\n..."
    assert ("Core:" in r.stdout and "installed:" in r.stdout) or \
           ("dbt-core" in r.stdout or "dbt-core" in r.stderr)


def test_dbt_run_then_test_clean():
    """干净态: 1% + 3.5% 两对 → 1% 不落 mart, 3.5% RECORDED 不触发断言 → PASS."""
    venv = _venv_dbt() or pytest.skip("dbt env missing")
    # Two distinct periods for the two pairs (avoid natural-key collision)
    # — value_a/value_b parametrize via separate period ids. Simplest: just
    # the 3.5% pair (RECORDED but not asserted) — RECORDED rows exist in mart
    # but aren't PENDING NEEDS_REVIEW so test PASSes.
    _insert_pair(Decimal("100"), Decimal("103.5"))  # 3.5% diff → RECORDED
    assert _dbt(venv, "run", "--select", DBT_SELECT,
                "--full-refresh", "--profiles-dir", ".").returncode == 0
    r = _dbt(venv, "test", "--select", TEST_SELECT, "--profiles-dir", ".")
    assert r.returncode == 0
    rows = _mart_rows()
    assert any(r[0] == "RECORDED" for r in rows)
    assert not any(r[0] == "NEEDS_REVIEW" and r[1] == "PENDING" for r in rows)


def test_dbt_test_fails_on_pending_needs_review():
    """8% S0↔S0 PENDING → mart 落 NEEDS_REVIEW+resolution='PENDING' → test FAIL."""
    venv = _venv_dbt() or pytest.skip("dbt env missing")
    _insert_pair(Decimal("100"), Decimal("108"))  # 8% → NEEDS_REVIEW
    assert _dbt(venv, "run", "--select", DBT_SELECT,
                "--full-refresh", "--profiles-dir", ".").returncode == 0
    rows = _mart_rows()
    pending = [r for r in rows if r[0] == "NEEDS_REVIEW" and r[1] == "PENDING"]
    assert len(pending) == 1
    assert pending[0][2] == "S0" and pending[0][3] == "S0"
    r = _dbt(venv, "test", "--select", TEST_SELECT, "--profiles-dir", ".")
    assert r.returncode != 0
    assert TEST_SELECT in (r.stdout + r.stderr)


def test_dbt_test_passes_when_resolved():
    """8% S0↔S0 但 resolution='PARSE' → mart 仍 NEEDS_REVIEW 但 PENDING=False → PASS."""
    venv = _venv_dbt() or pytest.skip("dbt env missing")
    _insert_pair(Decimal("100"), Decimal("108"))
    assert _dbt(venv, "run", "--select", DBT_SELECT,
                "--full-refresh", "--profiles-dir", ".").returncode == 0
    # Simulate human resolution on the mart row
    with _connect() as conn:
        with conn.cursor() as cur:
            cur.execute(
                "UPDATE cegr_staging.mart_source_disagreement "
                "SET resolution = 'PARSE', resolution_note = 'fake test' "
                "WHERE indicator_id = %s", (str(IND),))
        conn.commit()
    r = _dbt(venv, "test", "--select", TEST_SELECT, "--profiles-dir", ".")
    assert r.returncode == 0


def test_s0_s1_pair_not_asserted():
    """8% S0↔S1 PENDING → mart 行存在 (NEEDS_REVIEW) 但 singular test 限 S0↔S0 → PASS."""
    venv = _venv_dbt() or pytest.skip("dbt env missing")
    _insert_pair(Decimal("100"), Decimal("108"), doc_b=DOC_C, loc_b=LOC_C)
    assert _dbt(venv, "run", "--select", DBT_SELECT,
                "--full-refresh", "--profiles-dir", ".").returncode == 0
    rows = _mart_rows()
    nr = [r for r in rows if r[0] == "NEEDS_REVIEW"]
    assert len(nr) == 1
    # Pair should be (S0, S1) — candidate's "lower level wins as A"
    levels = sorted([nr[0][2], nr[0][3]])
    assert levels == ["S0", "S1"], f"expected (S0,S1), got {levels}"
    r = _dbt(venv, "test", "--select", TEST_SELECT, "--profiles-dir", ".")
    assert r.returncode == 0