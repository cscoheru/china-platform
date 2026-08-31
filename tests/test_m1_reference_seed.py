#!/usr/bin/env python3
"""M1 T1 — tests for scripts/seed_m1_reference_data.py.

Per docs/55 §T1 (2026-08-31):
  * 5 类 FK 全部存在
  * 脚本 exit 0 两次结果稳定（idempotent）
  * 不 INSERT observation
  * 同名不同口径不合并（GDP 与 IAV 各一条 methodology）

Required fixtures:
  * cegr_test DSN reachable at postgresql://postgres:postgres@127.0.0.1:55440/cegr_test
  * source_registry row tjj.hubei.gov.cn / PROVINCIAL_BULLETIN present
    (run scripts/import_registry_csv.py first)
  * spikes/02-provincial-yearbook/hubei_2026_06.xlsx present
"""
from __future__ import annotations

import hashlib
import importlib
import subprocess
import sys
from pathlib import Path

import psycopg2
import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent

# Make scripts importable
SCRIPTS_DIR = REPO_ROOT / "scripts"
sys.path.insert(0, str(SCRIPTS_DIR))

import seed_m1_reference_data as seed  # noqa: E402

DSN = "postgresql://postgres:postgres@127.0.0.1:55440/cegr_test"

# Stable UUIDs must match those in seed_m1_reference_data.py
HUBEI_PROVINCE_ID = "a1000000-0000-0000-0000-000000000001"
HUBEI_GEO_CODE_VERSION_ID = "a1000000-0000-0000-0000-000000000002"
HUBEI_GDP_INDICATOR_ID = "a1000000-0000-0000-0000-000000000010"
HUBEI_GDP_MV_ID = "a1000000-0000-0000-0000-000000000011"
HUBEI_IAV_INDICATOR_ID = "a1000000-0000-0000-0000-000000000020"
HUBEI_IAV_MV_ID = "a1000000-0000-0000-0000-000000000021"
HUBEI_2026_H1_PERIOD_ID = "a1000000-0000-0000-0000-000020260601"
HUBEI_SOURCE_DOC_ID = "a1000000-0000-0000-0000-000000000030"

EXPECTED_SHA = (
    "c5cf5abeb4fdf97af52567f0640470d631bc9ac329dcc98f14e5d40bf6a5cac7"
)
EXPECTED_SIZE = 11261


# ---------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------


@pytest.fixture(scope="module")
def imported_registry() -> None:
    """Ensure source_registry has tjj.hubei.gov.cn / PROVINCIAL_BULLETIN.

    We don't depend on scripts/import_registry_csv.py — that script has a
    pre-existing data-quality issue with row 14 (tjj.yancheng.gov.cn) whose
    stability_note contains an unescaped comma, breaking the whole CSV
    import. For T1 we only need the Hubei row, so we insert it directly
    (idempotent) and skip the broader re-import.
    """
    import psycopg2

    conn = psycopg2.connect(DSN)
    try:
        with conn.cursor() as cur:
            cur.execute(
                """
                INSERT INTO cegr.source_registry
                    (domain, organization, category, primary_url,
                     update_frequency, auth_note, access_method,
                     enabled, source_level)
                VALUES ('tjj.hubei.gov.cn', '湖北省统计局', 'PROVINCIAL_BULLETIN',
                        'https://tjj.hubei.gov.cn/tjsj/sjkscx/tjyb/',
                        'MONTHLY', '公开；无需授权',
                        'EXCEL_PARSE',
                        TRUE, 'S0')
                ON CONFLICT DO NOTHING
                """
            )
        conn.commit()
    finally:
        conn.close()


@pytest.fixture
def loaded_seed(imported_registry) -> None:
    """Ensure reference data is loaded before each test that needs it."""
    seed.load_seed(verbose=False)


def _conn():
    return psycopg2.connect(DSN)


def _count(conn, sql: str, params: tuple) -> int:
    with conn.cursor() as cur:
        cur.execute(sql, params)
        return cur.fetchone()[0]


# ---------------------------------------------------------------------
# Docs/55 §T1 验收 test 1 — 5 类 FK 全部存在
# ---------------------------------------------------------------------


def test_designated_xlsx_sha_and_size_match_registry() -> None:
    """Per docs/55 §1.1: the designated table is hubei_2026_06.xlsx with
    a specific SHA. This guards drift between the local file and the
    registry claim. SHA=file-bytes is the M0.3 invariant.
    """
    p = REPO_ROOT / "spikes" / "02-provincial-yearbook" / "hubei_2026_06.xlsx"
    if not p.exists():
        pytest.fail(f"mandatory spike xlsx missing: {p}")
    h = hashlib.sha256()
    h.update(p.read_bytes())
    assert h.hexdigest() == EXPECTED_SHA, (
        f"hubei xlsx SHA drift: expected={EXPECTED_SHA[:12]} actual={h.hexdigest()[:12]}"
    )
    assert p.stat().st_size == EXPECTED_SIZE, (
        f"hubei xlsx size drift: expected={EXPECTED_SIZE} actual={p.stat().st_size}"
    )


def test_load_seed_inserts_five_fk_entities(loaded_seed) -> None:
    """docs/55 §T1 验收 #1: 5 类 FK 全部存在.

    Required entities:
      1. geo_entity                (湖北省)
      2. geo_code_version          (admin_code 42 / ISO CN-HB)
      3. indicator_definition      (GDP)
      4. indicator_methodology_version (hubei-2026-06-bulletin-caveat)
      5. calendar_period           (2026H1)

    Plus an explicit IAV indicator + methodology so GDP and IAV do NOT
    share a methodology row (docs/55 §T1 同名不同口径不合并).
    """
    conn = _conn()
    try:
        assert _count(
            conn,
            "SELECT COUNT(*) FROM cegr.geo_entity WHERE id = %s",
            (HUBEI_PROVINCE_ID,),
        ) == 1, "geo_entity 湖北省 missing"

        assert _count(
            conn,
            "SELECT COUNT(*) FROM cegr.geo_code_version WHERE id = %s",
            (HUBEI_GEO_CODE_VERSION_ID,),
        ) == 1, "geo_code_version 湖北 missing"

        assert _count(
            conn,
            "SELECT COUNT(*) FROM cegr.indicator_definition WHERE id = %s",
            (HUBEI_GDP_INDICATOR_ID,),
        ) == 1, "indicator_definition GDP missing"

        assert _count(
            conn,
            """SELECT COUNT(*) FROM cegr.indicator_methodology_version
               WHERE id = %s AND indicator_id = %s""",
            (HUBEI_GDP_MV_ID, HUBEI_GDP_INDICATOR_ID),
        ) == 1, "indicator_methodology_version (GDP) missing or wrong indicator_id"

        assert _count(
            conn,
            "SELECT COUNT(*) FROM cegr.calendar_period WHERE id = %s",
            (HUBEI_2026_H1_PERIOD_ID,),
        ) == 1, "calendar_period 2026H1 missing"

        # Parallel IAV to enforce "不共用 methodology"
        assert _count(
            conn,
            "SELECT COUNT(*) FROM cegr.indicator_definition WHERE id = %s",
            (HUBEI_IAV_INDICATOR_ID,),
        ) == 1, "indicator_definition IAV missing"

        assert _count(
            conn,
            """SELECT COUNT(*) FROM cegr.indicator_methodology_version
               WHERE id = %s AND indicator_id = %s""",
            (HUBEI_IAV_MV_ID, HUBEI_IAV_INDICATOR_ID),
        ) == 1, "indicator_methodology_version (IAV) missing or wrong indicator_id"

        # The two methodology rows must not be cross-linked to the wrong indicator
        assert _count(
            conn,
            """SELECT COUNT(*) FROM cegr.indicator_methodology_version
               WHERE id = %s AND indicator_id = %s""",
            (HUBEI_GDP_MV_ID, HUBEI_IAV_INDICATOR_ID),
        ) == 0, "GDP methodology must not reference IAV indicator"

        assert _count(
            conn,
            """SELECT COUNT(*) FROM cegr.indicator_methodology_version
               WHERE id = %s AND indicator_id = %s""",
            (HUBEI_IAV_MV_ID, HUBEI_GDP_INDICATOR_ID),
        ) == 0, "IAV methodology must not reference GDP indicator"
    finally:
        conn.close()


def test_source_document_links_to_registry_with_correct_hash(loaded_seed) -> None:
    """The seed inserts a source_document for hubei_2026_06.xlsx that must
    back-reference the tjj.hubei.gov.cn / PROVINCIAL_BULLETIN registry row,
    and its hash/size must match the file bytes (M0.3 invariant).
    """
    conn = _conn()
    try:
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT sd.file_hash_sha256, sd.file_size_bytes,
                       sr.domain, sr.category, sd.caveat_text
                FROM cegr.source_document sd
                JOIN cegr.source_registry sr
                  ON sr.id = sd.source_registry_id
                WHERE sd.id = %s
                """,
                (HUBEI_SOURCE_DOC_ID,),
            )
            row = cur.fetchone()
        assert row is not None, "M1 source_document row missing"
        h, sz, dom, cat, caveat = row
        assert h == EXPECTED_SHA, f"source_document hash drift: {h}"
        assert sz == EXPECTED_SIZE, f"source_document size drift: {sz}"
        assert dom == "tjj.hubei.gov.cn", f"source_document domain: {dom}"
        assert cat == "PROVINCIAL_BULLETIN", f"source_document category: {cat}"
        # Caveat must mention 季度数/半年累计 so downstream parser is forced
        # to keep caveat_text verbatim (per docs/55 §T1 / §1.1).
        assert caveat is not None and ("季度数" in caveat or "半年累计" in caveat), (
            f"source_document caveat_text must encode GDP caveat: {caveat!r}"
        )
    finally:
        conn.close()


# ---------------------------------------------------------------------
# Docs/55 §T1 验收 test 2 — 脚本 exit 0 两次结果稳定（idempotent）
# ---------------------------------------------------------------------


def test_seed_script_is_idempotent_double_load(loaded_seed) -> None:
    """Calling --load twice must leave counts unchanged (ON CONFLICT DO NOTHING)."""
    before = _snapshot_counts(_conn())
    # Second load: imported_registry already in scope; this re-INSERTs all rows
    seed.load_seed(verbose=False)
    after = _snapshot_counts(_conn())
    assert before == after, (
        f"second load changed counts: before={before} after={after}"
    )


def test_seed_script_exit_zero_via_subprocess(loaded_seed) -> None:
    """Running the seed script as a subprocess must exit 0 and report stable
    status. Per docs/55 §T1 验收: '脚本 exit 0 两次结果稳定'."""
    proc = subprocess.run(
        [sys.executable, str(seed.REPO_ROOT / "scripts" / "seed_m1_reference_data.py"),
         "--status"],
        capture_output=True,
        text=True,
        timeout=60,
    )
    assert proc.returncode == 0, (
        f"seed script --status failed: rc={proc.returncode} stderr={proc.stderr}"
    )
    # Status output must report 1/1/2/2/1 presence.
    out = proc.stdout
    for needle in ("geo_entity=1/1", "geo_code_version=1/1",
                   "indicator_definition=2/2",
                   "indicator_methodology_version=2/2",
                   "calendar_period=1/1"):
        assert needle in out, (
            f"status output missing {needle!r}: {out!r}"
        )


# ---------------------------------------------------------------------
# Docs/55 §T1 验收 test 3 — 不 INSERT observation
# ---------------------------------------------------------------------


def test_seed_does_not_insert_observation(loaded_seed) -> None:
    """docs/55 §T1: T1 is reference data only. No observation rows are
    allowed. observation insertion is T2's job.

    TRUNCATE observation/source_location/ingestion_run before assertion so
    this test is robust against other test modules that may have run
    first (T2 connector inserts observations).
    """
    conn = _conn()
    try:
        with conn.cursor() as cur:
            # Clear any prior ingestion_run / observation / source_location
            # rows so this assertion is isolated to "what the seed inserts".
            cur.execute(
                "TRUNCATE TABLE cegr.observation, cegr.source_location, "
                "cegr.ingestion_run RESTART IDENTITY CASCADE"
            )
        conn.commit()
        # Re-run the seed to ensure rows are fresh.
        seed.load_seed(verbose=False)
        n = _count(
            conn,
            """
            SELECT COUNT(*) FROM cegr.observation
            WHERE geo_entity_id = %s
               OR indicator_id IN (%s, %s)
               OR calendar_period_id = %s
            """,
            (
                HUBEI_PROVINCE_ID,
                HUBEI_GDP_INDICATOR_ID, HUBEI_IAV_INDICATOR_ID,
                HUBEI_2026_H1_PERIOD_ID,
            ),
        )
        assert n == 0, (
            f"T1 must not insert observation; found {n} referencing T1 FKs"
        )
    finally:
        conn.close()


# ---------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------


def _snapshot_counts(conn) -> dict[str, int]:
    """Stable snapshot of the 5 FK entity counts for idempotency check."""
    with conn.cursor() as cur:
        cur.execute(
            "SELECT COUNT(*) FROM cegr.geo_entity WHERE id = %s",
            (HUBEI_PROVINCE_ID,),
        )
        geo = cur.fetchone()[0]
        cur.execute(
            "SELECT COUNT(*) FROM cegr.geo_code_version WHERE id = %s",
            (HUBEI_GEO_CODE_VERSION_ID,),
        )
        gcv = cur.fetchone()[0]
        cur.execute(
            "SELECT COUNT(*) FROM cegr.indicator_definition WHERE id IN (%s, %s)",
            (HUBEI_GDP_INDICATOR_ID, HUBEI_IAV_INDICATOR_ID),
        )
        ind = cur.fetchone()[0]
        cur.execute(
            "SELECT COUNT(*) FROM cegr.indicator_methodology_version WHERE id IN (%s, %s)",
            (HUBEI_GDP_MV_ID, HUBEI_IAV_MV_ID),
        )
        mv = cur.fetchone()[0]
        cur.execute(
            "SELECT COUNT(*) FROM cegr.calendar_period WHERE id = %s",
            (HUBEI_2026_H1_PERIOD_ID,),
        )
        period = cur.fetchone()[0]
        cur.execute(
            "SELECT COUNT(*) FROM cegr.source_document WHERE id = %s",
            (HUBEI_SOURCE_DOC_ID,),
        )
        sd = cur.fetchone()[0]
    return {
        "geo_entity": geo,
        "geo_code_version": gcv,
        "indicator_definition": ind,
        "indicator_methodology_version": mv,
        "calendar_period": period,
        "source_document": sd,
    }


# ---------------------------------------------------------------------
# Module re-import safety
# ---------------------------------------------------------------------


def test_seed_module_imports_cleanly() -> None:
    """Sanity: the module is importable without raising."""
    mod = importlib.import_module("seed_m1_reference_data")
    assert mod.DESIGNATED_SHA == EXPECTED_SHA
    assert mod.DESIGNATED_SIZE == EXPECTED_SIZE