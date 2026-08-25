"""Stage 1 / S1.15 — docs/10 §2.7–2.9 acceptance e2e tests.

Per docs/30 §4 (14 planned cases) + tasking 115 §NOW-1 (≥10 minimum).

Strategy (mirrors test_source_disagreement_s141.py):
  - Direct psycopg2 SQL against the conftest-bootstrapped schema chain.
  - Module fixture seeds the FK chain once (stable UUIDs, prefix e2000000-).
  - Function fixture wipes only this file's observation/queue rows between tests.
  - The ingest router for §2.8 is implemented as a helper mirroring docs/30 §2.3;
    the DB CHECK (observation_ocr_confidence_floor) is the non-bypassable gate.

Coverage (docs/10 definitions):
  §2.7 行政区划有效期 — detection query: geo_code_version window must cover
      calendar_period; 巢湖-style split fixture (valid 2000→2011-07).
  §2.8 OCR 置信度 — confidence < 0.70 routes to cegr.ocr_review_queue, never
      into observation (CHECK floor 0.70; exactly 0.70 passes).
  §2.9 缺失值不补零 — value/missing_reason exclusivity (existing CHECK in
      01-core.sql) + zero-with-missing-marker detection query.
"""

from __future__ import annotations

import os
import sys
import uuid
from decimal import Decimal
from pathlib import Path

import psycopg2
import psycopg2.extras
import pytest

# Ensure backend/src is on sys.path (consistency with sibling test modules)
_BACKEND_SRC = Path(__file__).resolve().parents[1] / "backend" / "src"
if str(_BACKEND_SRC) not in sys.path:
    sys.path.insert(0, str(_BACKEND_SRC))

psycopg2.extras.register_uuid()

DSN = os.environ.get(
    "STAGE0_DSN",
    "postgresql://postgres:postgres@127.0.0.1:55440/cegr_test",
)

# OCR confidence floor — docs/10 §2.8 constant (0-1 scale).
# NOTE: gate_thresholds.json is a DIFFERENT artifact (spike-04 eval, 0-100
# scale) and is read-only; do not conflate.
CONF_FLOOR = Decimal("0.70")

# Stable fixture UUIDs (prefix e2000000-; observations use ...c% prefix)
IND          = uuid.UUID("e2000000-0000-0000-0000-000000000001")
GEO_CHAOLU   = uuid.UUID("e2000000-0000-0000-0000-000000000002")  # 2011 拆分式
GEO_OPEN     = uuid.UUID("e2000000-0000-0000-0000-000000000003")  # 开放式版本
PERIOD_2010  = uuid.UUID("e2000000-0000-0000-0000-000000000004")
PERIOD_2012  = uuid.UUID("e2000000-0000-0000-0000-000000000005")
PERIOD_2015  = uuid.UUID("e2000000-0000-0000-0000-000000000006")
SRC_REG      = uuid.UUID("e2000000-0000-0000-0000-00000000a001")
DOC          = uuid.UUID("e2000000-0000-0000-0000-00000000b001")
IND_METH     = uuid.UUID("e2000000-0000-0000-0000-00000000d001")
GEO_VER_CHL  = uuid.UUID("e2000000-0000-0000-0000-00000000d002")  # 2000→2011-07-31
GEO_VER_OPEN = uuid.UUID("e2000000-0000-0000-0000-00000000d003")  # 1999→NULL
SRC_LOC      = uuid.UUID("e2000000-0000-0000-0000-00000000e001")

# Observation ID pool (...c% prefix — wiped between tests)
OBS_POOL = {f"c{i:03d}": uuid.UUID(f"e2000000-0000-0000-0000-00000000c{i:03d}") for i in range(1, 16)}


def _connect():
    return psycopg2.connect(DSN)


@pytest.fixture(scope="module", autouse=True)
def _ensure_fixtures():
    """Seed the FK chain once (docs/30 §1/§2 fixture design)."""
    try:
        with _connect() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    INSERT INTO cegr.indicator_definition
                        (id, canonical_name, unit_canonical, frequency)
                    VALUES (%s, 'TEST_INDICATOR_S15', 'CNY', 'YEARLY')
                    ON CONFLICT (id) DO NOTHING
                    """,
                    (str(IND),),
                )
                for gid, name in [(GEO_CHAOLU, "TEST_GEO_S15_CHAOLU"),
                                  (GEO_OPEN, "TEST_GEO_S15_OPEN")]:
                    cur.execute(
                        """
                        INSERT INTO cegr.geo_entity (id, canonical_name, level)
                        VALUES (%s, %s, 'PROVINCE')
                        ON CONFLICT (id) DO NOTHING
                        """,
                        (str(gid), name),
                    )
                for pid, label, start, end in [
                    (PERIOD_2010, "2010-S15", "2010-01-01", "2010-12-31"),
                    (PERIOD_2012, "2012-S15", "2012-01-01", "2012-12-31"),
                    (PERIOD_2015, "2015-S15", "2015-01-01", "2015-12-31"),
                ]:
                    cur.execute(
                        """
                        INSERT INTO cegr.calendar_period
                            (id, period_label, start_date, end_date, period_type)
                        VALUES (%s, %s, %s, %s, 'CALENDAR_YEAR')
                        ON CONFLICT (id) DO NOTHING
                        """,
                        (str(pid), label, start, end),
                    )
                cur.execute(
                    """
                    INSERT INTO cegr.source_registry
                        (id, domain, organization, category, primary_url,
                         access_method, source_level, declared_source_level,
                         update_frequency, enabled, auth_note)
                    VALUES (%s, 'test.local', 'TEST_SRC_S15', 'TEST',
                            'http://test.local/s15-a', 'API', 'S0', 'S0',
                            'AD_HOC', TRUE, 'test')
                    ON CONFLICT (id) DO NOTHING
                    """,
                    (str(SRC_REG),),
                )
                cur.execute(
                    """
                    INSERT INTO cegr.source_document
                        (id, source_registry_id, source_level, verification_status,
                         title, publisher, url, file_path, file_hash_sha256,
                         file_format, extraction_method, copyright_note, uploader_id)
                    VALUES (%s, %s, 'S1', 'UNVERIFIED',
                            'fixture S15 scanned pdf', 'TEST_SRC_S15', 'http://test/s15',
                            '/tmp/s15', repeat('e', 64), 'pdf', 'PDF_OCR',
                            '公开 / 《著作权法》第五条 / fixture', 'test-fixture')
                    ON CONFLICT (id) DO NOTHING
                    """,
                    (str(DOC), str(SRC_REG)),
                )
                cur.execute(
                    """
                    INSERT INTO cegr.indicator_methodology_version
                        (id, indicator_id, version_label, valid_from,
                         change_summary, source_id)
                    VALUES (%s, %s, 'v1-s15', '2020-01-01', 'test methodology', %s)
                    ON CONFLICT (id) DO NOTHING
                    """,
                    (str(IND_METH), str(IND), str(DOC)),
                )
                # 巢湖式: 2000-01-01 → 2011-07-31 (2011 拆分)
                cur.execute(
                    """
                    INSERT INTO cegr.geo_code_version
                        (id, geo_entity_id, admin_code, valid_from, valid_to, source_id)
                    VALUES (%s, %s, 'TEST-S15-CHL', '2000-01-01', '2011-07-31', %s)
                    ON CONFLICT (id) DO NOTHING
                    """,
                    (str(GEO_VER_CHL), str(GEO_CHAOLU), str(DOC)),
                )
                # 开放式: 1999-01-01 → NULL
                cur.execute(
                    """
                    INSERT INTO cegr.geo_code_version
                        (id, geo_entity_id, admin_code, valid_from, valid_to, source_id)
                    VALUES (%s, %s, 'TEST-S15-OPEN', '1999-01-01', NULL, %s)
                    ON CONFLICT (id) DO NOTHING
                    """,
                    (str(GEO_VER_OPEN), str(GEO_OPEN), str(DOC)),
                )
                cur.execute(
                    """
                    INSERT INTO cegr.source_location (id, source_document_id, sheet_name)
                    VALUES (%s, %s, 'page-24') ON CONFLICT (id) DO NOTHING
                    """,
                    (str(SRC_LOC), str(DOC)),
                )
            conn.commit()
    except Exception as e:
        pytest.skip(f"Fixture seed failed: {e}", allow_module_level=True)


@pytest.fixture(autouse=True)
def _wipe():
    """Per-test clean slate.

    observation is append-only in production (observation_no_delete row
    trigger forbids DELETE); per-test isolation therefore uses TRUNCATE
    CASCADE, which bypasses row triggers and auto-truncates referencing
    tables (observation_revision, source_disagreement,
    observation_quality_flag, ...). This matches the conftest regime (the
    whole cegr schema is dropped/re-applied each pytest session anyway).
    """
    with _connect() as conn:
        with conn.cursor() as cur:
            cur.execute("TRUNCATE cegr.observation CASCADE")
            cur.execute(
                "DELETE FROM cegr.ocr_review_queue WHERE source_document_id = %s",
                (str(DOC),),
            )
        conn.commit()
    yield


# ---------------------------------------------------------------------------
# helpers
# ---------------------------------------------------------------------------

def _route_ocr_cell(cur, obs_id, *, confidence, geo=GEO_CHAOLU,
                    geo_ver=GEO_VER_CHL, period=PERIOD_2010,
                    raw="123.4", value=Decimal("123.4")):
    """Ingest router per docs/30 §2.3.

    OCR cell with confidence < 0.70 → cegr.ocr_review_queue (NOT observation);
    confidence >= 0.70 → observation. The DB CHECK is the non-bypassable gate
    (proven separately by test_ocr_floor_check_rejects).
    """
    if confidence < CONF_FLOOR:
        cur.execute(
            """
            INSERT INTO cegr.ocr_review_queue
                (source_document_id, raw_ocr_text, parsed_value,
                 confidence, locator_page)
            VALUES (%s, %s, %s, %s, 24)
            """,
            (str(DOC), raw, value, confidence),
        )
    else:
        cur.execute(
            """
            INSERT INTO cegr.observation
                (id, indicator_id, indicator_methodology_version_id,
                 geo_entity_id, geo_code_version_id, calendar_period_id,
                 value, unit, comparison_basis, value_type, status,
                 source_id, source_location_id, extraction_method,
                 confidence, period_label, period_type)
            VALUES (%s, %s, %s, %s, %s, %s, %s, 'CNY', 'NOMINAL', 'FACT', 'FINAL',
                    %s, %s, 'PDF_OCR', %s, '2010-S15', 'CALENDAR_YEAR')
            """,
            (str(obs_id), str(IND), str(IND_METH), str(geo), str(geo_ver),
             str(period), value, str(DOC), str(SRC_LOC), confidence),
        )


_GEO_VIOLATIONS = """
    SELECT o.id, gcv.geo_entity_id
    FROM cegr.observation o
    JOIN cegr.geo_code_version gcv ON gcv.id = o.geo_code_version_id
    JOIN cegr.calendar_period cp ON cp.id = o.calendar_period_id
    WHERE o.id::text LIKE 'e2000000-0000-0000-0000-00000000c%'
      AND NOT (
          cp.start_date >= gcv.valid_from
          AND (gcv.valid_to IS NULL OR cp.end_date <= gcv.valid_to)
      )
"""


def _geo_violations():
    with _connect() as conn:
        with conn.cursor() as cur:
            cur.execute(_GEO_VIOLATIONS)
            return cur.fetchall()


# ---------------------------------------------------------------------------
# §2.7 行政区划有效期 (docs/10 §2.7 / docs/30 §1)
# ---------------------------------------------------------------------------

def test_valid_version_covers_period():
    """2010 巢湖观察引用 2000→2011-07 版本 → 检出查询 0 违规 (docs/10 §2.7 例)"""
    with _connect() as conn:
        with conn.cursor() as cur:
            _route_ocr_cell(cur, OBS_POOL["c001"], confidence=Decimal("0.90"))
        conn.commit()
    assert _geo_violations() == []


def test_expired_version_detected():
    """2012 观察仍引用拆分前版本 → 检出查询命中 1 条且指向该实体"""
    with _connect() as conn:
        with conn.cursor() as cur:
            _route_ocr_cell(cur, OBS_POOL["c002"], confidence=Decimal("0.90"),
                            period=PERIOD_2012)
        conn.commit()
    rows = _geo_violations()
    assert len(rows) == 1
    assert rows[0][0] == OBS_POOL["c002"]
    assert rows[0][1] == GEO_CHAOLU


def test_overlapping_versions_rejected():
    """同实体重叠区间版本 → EXCLUDE gist 拒绝 (01-core.sql:173)"""
    with pytest.raises(psycopg2.errors.ExclusionViolation):
        with _connect() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    INSERT INTO cegr.geo_code_version
                        (id, geo_entity_id, admin_code, valid_from, valid_to, source_id)
                    VALUES ('e2000000-0000-0000-0000-00000000d099',
                            %s, 'TEST-S15-OVL', '2005-01-01', '2020-12-31', %s)
                    """,
                    (str(GEO_CHAOLU), str(DOC)),
                )
            conn.commit()


def test_open_ended_version_always_valid():
    """valid_to NULL 的开放式版本覆盖任意后期 period → 0 违规"""
    with _connect() as conn:
        with conn.cursor() as cur:
            _route_ocr_cell(cur, OBS_POOL["c004"], confidence=Decimal("0.90"),
                            geo=GEO_OPEN, geo_ver=GEO_VER_OPEN, period=PERIOD_2015)
        conn.commit()
    assert _geo_violations() == []


# ---------------------------------------------------------------------------
# §2.8 OCR 置信度分流 (docs/10 §2.8 / docs/30 §2)
# ---------------------------------------------------------------------------

def test_queue_schema_applied():
    """migration 007: 表 + 关键列 + 2 索引 + observation 硬门约束存在"""
    with _connect() as conn:
        with conn.cursor() as cur:
            cur.execute(
                "SELECT to_regclass('cegr.ocr_review_queue') IS NOT NULL")
            assert cur.fetchone()[0] is True
            cur.execute(
                """
                SELECT column_name FROM information_schema.columns
                WHERE table_schema = 'cegr' AND table_name = 'ocr_review_queue'
                """)
            cols = {r[0] for r in cur.fetchall()}
            for c in ("confidence", "review_status", "raw_ocr_text",
                      "parsed_value", "locator_page", "locator_bbox",
                      "source_document_id", "reviewed_at"):
                assert c in cols, f"missing column {c}"
            cur.execute(
                """
                SELECT indexname FROM pg_indexes
                WHERE schemaname = 'cegr' AND tablename = 'ocr_review_queue'
                """)
            idx = {r[0] for r in cur.fetchall()}
            assert "idx_ocr_review_queue_status" in idx
            assert "idx_ocr_review_queue_doc" in idx
            cur.execute(
                """
                SELECT 1 FROM pg_constraint
                WHERE conname = 'observation_ocr_confidence_floor'
                  AND conrelid = 'cegr.observation'::regclass
                """)
            assert cur.fetchone() is not None


def test_low_confidence_routed_to_queue():
    """conf=0.65 → queue 1 行 / observation 0 行 (docs/10: 不入正式表)"""
    with _connect() as conn:
        with conn.cursor() as cur:
            _route_ocr_cell(cur, OBS_POOL["c005"], confidence=Decimal("0.65"))
            cur.execute(
                "SELECT confidence, review_status FROM cegr.ocr_review_queue "
                "WHERE source_document_id = %s", (str(DOC),))
            q = cur.fetchall()
            cur.execute(
                "SELECT COUNT(*) FROM cegr.observation "
                "WHERE id::text LIKE 'e2000000-0000-0000-0000-00000000c%'")
            n_obs = cur.fetchone()[0]
        conn.commit()
    assert len(q) == 1
    assert q[0][0] == Decimal("0.65")
    assert q[0][1] == "PENDING"
    assert n_obs == 0


def test_high_confidence_passes():
    """conf=0.85 → observation 1 行 / queue 0 行"""
    with _connect() as conn:
        with conn.cursor() as cur:
            _route_ocr_cell(cur, OBS_POOL["c006"], confidence=Decimal("0.85"))
            cur.execute(
                "SELECT confidence FROM cegr.observation WHERE id = %s",
                (str(OBS_POOL["c006"]),))
            o = cur.fetchall()
            cur.execute(
                "SELECT COUNT(*) FROM cegr.ocr_review_queue "
                "WHERE source_document_id = %s", (str(DOC),))
            n_q = cur.fetchone()[0]
        conn.commit()
    assert len(o) == 1
    assert o[0][0] == Decimal("0.85")
    assert n_q == 0


def test_boundary_070_passes():
    """恰好 0.70 通过 (docs/10 定义 <0.7 才分流)"""
    with _connect() as conn:
        with conn.cursor() as cur:
            _route_ocr_cell(cur, OBS_POOL["c007"], confidence=CONF_FLOOR)
            cur.execute(
                "SELECT confidence FROM cegr.observation WHERE id = %s",
                (str(OBS_POOL["c007"]),))
            o = cur.fetchall()
            cur.execute(
                "SELECT COUNT(*) FROM cegr.ocr_review_queue "
                "WHERE source_document_id = %s", (str(DOC),))
            n_q = cur.fetchone()[0]
        conn.commit()
    assert len(o) == 1
    assert n_q == 0


def test_ocr_floor_check_rejects():
    """绕过路由直插 OCR conf=0.65 行 → CHECK 在 INSERT 时拒绝 (DB 级不可绕过)"""
    with pytest.raises(psycopg2.errors.CheckViolation):
        with _connect() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    INSERT INTO cegr.observation
                        (id, indicator_id, indicator_methodology_version_id,
                         geo_entity_id, geo_code_version_id, calendar_period_id,
                         value, unit, comparison_basis, value_type, status,
                         source_id, source_location_id, extraction_method,
                         confidence, period_label, period_type)
                    VALUES (%s, %s, %s, %s, %s, %s, 65.0, 'CNY', 'NOMINAL',
                            'FACT', 'FINAL', %s, %s, 'PDF_OCR', 0.65,
                            '2010-S15', 'CALENDAR_YEAR')
                    """,
                    (str(OBS_POOL["c008"]), str(IND), str(IND_METH),
                     str(GEO_CHAOLU), str(GEO_VER_CHL), str(PERIOD_2010),
                     str(DOC), str(SRC_LOC)),
                )
            conn.commit()
    # 确认行未落库
    with _connect() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT COUNT(*) FROM cegr.observation WHERE id = %s",
                        (str(OBS_POOL["c008"]),))
            assert cur.fetchone()[0] == 0


def test_non_ocr_unaffected():
    """EXCEL_PARSE + confidence NULL → 硬门不适用, 正常插入"""
    with _connect() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                INSERT INTO cegr.observation
                    (id, indicator_id, indicator_methodology_version_id,
                     geo_entity_id, geo_code_version_id, calendar_period_id,
                     value, unit, comparison_basis, value_type, status,
                     source_id, source_location_id, extraction_method,
                     period_label, period_type)
                VALUES (%s, %s, %s, %s, %s, %s, 42.0, 'CNY', 'NOMINAL',
                        'FACT', 'FINAL', %s, %s, 'EXCEL_PARSE',
                        '2010-S15', 'CALENDAR_YEAR')
                """,
                (str(OBS_POOL["c009"]), str(IND), str(IND_METH),
                 str(GEO_CHAOLU), str(GEO_VER_CHL), str(PERIOD_2010),
                 str(DOC), str(SRC_LOC)),
            )
        conn.commit()


# ---------------------------------------------------------------------------
# §2.9 缺失值不补零 (docs/10 §2.9 / docs/30 §3)
# ---------------------------------------------------------------------------

def _insert_full(cur, obs_id, *, period, value, raw, missing_reason,
                 is_imputed=False):
    """Full INSERT including value/raw_value/missing_reason/is_imputed so the
    observation_missing_consistency CHECK evaluates at INSERT time."""
    cur.execute(
        """
        INSERT INTO cegr.observation
            (id, indicator_id, indicator_methodology_version_id,
             geo_entity_id, geo_code_version_id, calendar_period_id,
             value, raw_value, missing_reason, is_imputed, unit,
             comparison_basis, value_type, status,
             source_id, source_location_id, extraction_method,
             period_label, period_type)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s,
                'NOMINAL', 'FACT', 'FINAL', %s, %s, 'PDF_OCR',
                '2010-S15', 'CALENDAR_YEAR')
        """,
        (str(obs_id), str(IND), str(IND_METH), str(GEO_CHAOLU),
         str(GEO_VER_CHL), str(period), value, raw, missing_reason,
         is_imputed, None if value is None else "CNY",
         str(DOC), str(SRC_LOC)),
    )


def test_missing_row_persists_null():
    """value NULL + missing_reason + is_imputed FALSE → 插入成功且读回保持 NULL"""
    with _connect() as conn:
        with conn.cursor() as cur:
            _insert_full(cur, OBS_POOL["c010"], period=PERIOD_2010,
                         value=None, raw="…", missing_reason="NOT_PUBLISHED")
        conn.commit()
    with _connect() as conn:
        with conn.cursor() as cur:
            cur.execute(
                "SELECT value, missing_reason, is_imputed, unit "
                "FROM cegr.observation WHERE id = %s", (str(OBS_POOL["c010"]),))
            row = cur.fetchone()
    assert row[0] is None
    assert row[1] == "NOT_PUBLISHED"
    assert row[2] is False
    assert row[3] is None


def test_zero_with_reason_rejected():
    """value=0 + missing_reason → CheckViolation (缺失不得写 0)"""
    with pytest.raises(psycopg2.errors.CheckViolation):
        with _connect() as conn:
            with conn.cursor() as cur:
                _insert_full(cur, OBS_POOL["c011"], period=PERIOD_2010,
                             value=Decimal("0"), raw="…",
                             missing_reason="NOT_PUBLISHED")
            conn.commit()


def test_value_with_reason_rejected():
    """value=123 + missing_reason → CheckViolation (有值不得挂缺失因)"""
    with pytest.raises(psycopg2.errors.CheckViolation):
        with _connect() as conn:
            with conn.cursor() as cur:
                _insert_full(cur, OBS_POOL["c012"], period=PERIOD_2010,
                             value=Decimal("123"), raw="123",
                             missing_reason="SUPPRESSED")
            conn.commit()


def test_zero_marker_detection():
    """value=0 且 raw_value 为缺失占位符 → 检出查询命中; 真 0 (raw='0') 不命中"""
    with _connect() as conn:
        with conn.cursor() as cur:
            # 补零污染行: 占位符 … 却被写成 0 — 无 reason 时 CHECK 拦不住,
            # 只能靠检出查询 (docs/30 §3.2-4)
            cur.execute(
                """
                INSERT INTO cegr.observation
                    (id, indicator_id, indicator_methodology_version_id,
                     geo_entity_id, geo_code_version_id, calendar_period_id,
                     value, raw_value, unit, comparison_basis, value_type, status,
                     source_id, source_location_id, extraction_method,
                     period_label, period_type)
                VALUES (%s, %s, %s, %s, %s, %s, 0, '…', 'CNY', 'NOMINAL',
                        'FACT', 'FINAL', %s, %s, 'PDF_OCR',
                        '2010-S15', 'CALENDAR_YEAR')
                """,
                (str(OBS_POOL["c013"]), str(IND), str(IND_METH),
                 str(GEO_CHAOLU), str(GEO_VER_CHL), str(PERIOD_2010),
                 str(DOC), str(SRC_LOC)),
            )
            # 真 0 行
            cur.execute(
                """
                INSERT INTO cegr.observation
                    (id, indicator_id, indicator_methodology_version_id,
                     geo_entity_id, geo_code_version_id, calendar_period_id,
                     value, raw_value, unit, comparison_basis, value_type, status,
                     source_id, source_location_id, extraction_method,
                     period_label, period_type)
                VALUES (%s, %s, %s, %s, %s, %s, 0, '0', 'CNY', 'NOMINAL',
                        'FACT', 'FINAL', %s, %s, 'PDF_OCR',
                        '2012-S15', 'CALENDAR_YEAR')
                """,
                (str(OBS_POOL["c014"]), str(IND), str(IND_METH),
                 str(GEO_CHAOLU), str(GEO_VER_CHL), str(PERIOD_2012),
                 str(DOC), str(SRC_LOC)),
            )
        conn.commit()
    with _connect() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT id FROM cegr.observation
                WHERE id::text LIKE 'e2000000-0000-0000-0000-00000000c%'
                  AND value = 0
                  AND raw_value IN ('…', '—', '')
                """)
            hits = [r[0] for r in cur.fetchall()]
    assert hits == [OBS_POOL["c013"]]
