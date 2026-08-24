"""
I-05 来源等级治理测试 (Stage 0 Gate 0 R4)

覆盖：
  1. S0 + UNVERIFIED  → CheckViolation (新 CHECK 约束)
  2. S0 + PENDING     → CheckViolation (同样要求 VERIFIED)
  3. S0 + REJECTED    → CheckViolation (不能以 REJECTED 状态声称 S0)
  4. S0 + VERIFIED    → ok (正向)
  5. S1/S2/S3/S4 + UNVERIFIED → ok (S1-S4 不强制核验)
  6. declared_source_level 可独立于 effective level 写入
  7. verification_status UNVERIFIED → PENDING → VERIFIED
     各阶段触发 source_document_verification_event 审计
  8. 审计表本身 append-only (UPDATE/DELETE 均被拒)
  9. source_document 不可变性依然成立 (除 caveat_text + verification_status)
"""
from __future__ import annotations

import os
import uuid
from datetime import date

import pytest

try:
    import psycopg
except ImportError:
    try:
        import psycopg2 as psycopg
    except ImportError:
        psycopg = None

DSN = os.environ.get(
    "STAGE0_DSN",
    "host=127.0.0.1 port=55440 user=postgres dbname=cegr_test",
)


def _conn():
    if psycopg is None:
        pytest.fail("psycopg/psycopg2 未安装 — 测试无法运行")
    try:
        return psycopg.connect(DSN)
    except Exception as e:
        pytest.fail(
            f"PostgreSQL 未运行或不可连 (DSN={DSN}): {e}"
        )


@pytest.fixture(scope="module")
def conn():
    c = _conn()
    yield c
    c.close()


@pytest.fixture
def tx(conn):
    conn.autocommit = False
    cur = conn.cursor()
    yield cur
    conn.rollback()


def _seed_registry(cur) -> str:
    rid = str(uuid.uuid4())
    cur.execute(
        "INSERT INTO source_registry (id, domain, organization, category, primary_url)"
        " VALUES (%s, %s, %s, %s, %s)",
        (rid, f"i05-{rid[:8]}.example", "TEST", "OTHER",
         f"https://{rid[:8]}.example/"),
    )
    return rid


def _insert_source_doc(cur, *, rid: str, level: str,
                       verification: str = "UNVERIFIED",
                       declared: str | None = None) -> str:
    sid = str(uuid.uuid4())
    cur.execute(
        "INSERT INTO source_document"
        " (id, source_registry_id, source_level, verification_status,"
        "  declared_source_level, title, publisher, file_hash_sha256,"
        "  file_size_bytes, extraction_method)"
        " VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)",
        (sid, rid, level, verification, declared,
         f"I05_DOC_{sid[:8]}", "test",
         uuid.uuid4().hex + uuid.uuid4().hex, 1024, "EXCEL_PARSE"),
    )
    return sid


# ============================================================================
# 1. S0 + UNVERIFIED 被拒 (R4-4 negative)
# ============================================================================

def test_s0_unverified_rejected(tx):
    """I-05 / R4-4: S0 + UNVERIFIED → CheckViolation.

    effective S0 必须经过平台核验；上传者声明 S0 但未核验不能写入。
    """
    tx.execute("SET search_path = cegr, public")
    rid = _seed_registry(tx)
    with pytest.raises(psycopg.errors.CheckViolation):
        _insert_source_doc(tx, rid=rid, level="S0",
                           verification="UNVERIFIED")


def test_s0_pending_rejected(tx):
    """S0 + PENDING 也被拒 — 等待核验期间不能对外表现为 S0。"""
    tx.execute("SET search_path = cegr, public")
    rid = _seed_registry(tx)
    with pytest.raises(psycopg.errors.CheckViolation):
        _insert_source_doc(tx, rid=rid, level="S0",
                           verification="PENDING")


def test_s0_rejected_rejected(tx):
    """S0 + REJECTED 也被拒 — 拒绝本身就是拒绝冒充 S0。"""
    tx.execute("SET search_path = cegr, public")
    rid = _seed_registry(tx)
    with pytest.raises(psycopg.errors.CheckViolation):
        _insert_source_doc(tx, rid=rid, level="S0",
                           verification="REJECTED")


# ============================================================================
# 2. S0 + VERIFIED 正向 (R4-4 positive)
# ============================================================================

def test_s0_verified_accepted(tx):
    """I-05 / R4-4: S0 + VERIFIED → ok。"""
    tx.execute("SET search_path = cegr, public")
    rid = _seed_registry(tx)
    sid = _insert_source_doc(tx, rid=rid, level="S0",
                             verification="VERIFIED")
    row = tx.execute(
        "SELECT source_level, verification_status FROM source_document"
        " WHERE id = %s", (sid,)).fetchone()
    assert row[0] == "S0"
    assert row[1] == "VERIFIED"


def test_s0_verified_with_declared_level(tx):
    """S0 + VERIFIED 同时记录 declared_source_level。"""
    tx.execute("SET search_path = cegr, public")
    rid = _seed_registry(tx)
    sid = _insert_source_doc(tx, rid=rid, level="S0",
                             verification="VERIFIED",
                             declared="S0")
    row = tx.execute(
        "SELECT declared_source_level, source_level FROM source_document"
        " WHERE id = %s", (sid,)).fetchone()
    assert row[0] == "S0"
    assert row[1] == "S0"


# ============================================================================
# 3. S1/S2/S3/S4 + UNVERIFIED 正向 (S1-S4 不要求核验)
# ============================================================================

@pytest.mark.parametrize("level", ["S1", "S2", "S3", "S4"])
def test_s1_to_s4_unverified_accepted(tx, level):
    """S1-S4 允许 UNVERIFIED — 这些等级本身可信度按层级递减，
    设计上不要求平台核验。"""
    tx.execute("SET search_path = cegr, public")
    rid = _seed_registry(tx)
    sid = _insert_source_doc(tx, rid=rid, level=level,
                             verification="UNVERIFIED")
    row = tx.execute(
        "SELECT source_level, verification_status FROM source_document"
        " WHERE id = %s", (sid,)).fetchone()
    assert row[0] == level
    assert row[1] == "UNVERIFIED"


# ============================================================================
# 4. declared_source_level 与 effective level 独立
# ============================================================================

def test_declared_level_can_differ_from_effective(tx):
    """上传者声明 S0 但平台核验后只给 S1 — 两列分别记录。"""
    tx.execute("SET search_path = cegr, public")
    rid = _seed_registry(tx)
    sid = _insert_source_doc(tx, rid=rid, level="S1",
                             verification="VERIFIED",
                             declared="S0")
    row = tx.execute(
        "SELECT declared_source_level, source_level FROM source_document"
        " WHERE id = %s", (sid,)).fetchone()
    assert row[0] == "S0"   # uploader 声称
    assert row[1] == "S1"   # platform effective


def test_declared_level_nullable(tx):
    """declared_source_level 允许 NULL — 历史行兼容。"""
    tx.execute("SET search_path = cegr, public")
    rid = _seed_registry(tx)
    sid = _insert_source_doc(tx, rid=rid, level="S2",
                             verification="UNVERIFIED",
                             declared=None)
    row = tx.execute(
        "SELECT declared_source_level FROM source_document"
        " WHERE id = %s", (sid,)).fetchone()
    assert row[0] is None


# ============================================================================
# 5. verification_status 迁移写审计 (核心 R4-4 不变量)
# ============================================================================

def _audit_count(tx, sid: str) -> int:
    return tx.execute(
        "SELECT count(*) FROM source_document_verification_event"
        " WHERE source_document_id = %s", (sid,)).fetchone()[0]


def test_verification_transition_writes_audit_event(tx):
    """UNVERIFIED → PENDING → VERIFIED → 2 条事件被记录。"""
    tx.execute("SET search_path = cegr, public")
    rid = _seed_registry(tx)
    sid = _insert_source_doc(tx, rid=rid, level="S1",
                             verification="UNVERIFIED")
    assert _audit_count(tx, sid) == 0, "初始状态不应有事件"

    # UNVERIFIED → PENDING
    tx.execute(
        "UPDATE source_document SET verification_status = 'PENDING'"
        " WHERE id = %s", (sid,))
    assert _audit_count(tx, sid) == 1

    # PENDING → VERIFIED
    tx.execute(
        "UPDATE source_document SET verification_status = 'VERIFIED'"
        " WHERE id = %s", (sid,))
    assert _audit_count(tx, sid) == 2

    events = tx.execute(
        "SELECT from_status, to_status FROM source_document_verification_event"
        " WHERE source_document_id = %s ORDER BY decided_at", (sid,)).fetchall()
    assert events[0] == ("UNVERIFIED", "PENDING")
    assert events[1] == ("PENDING", "VERIFIED")


def test_audit_event_captures_verifier_id(tx):
    """审计事件记录 verifier_id — 通过 SET LOCAL app.verifier_id。"""
    tx.execute("SET search_path = cegr, public")
    rid = _seed_registry(tx)
    sid = _insert_source_doc(tx, rid=rid, level="S1",
                             verification="UNVERIFIED")
    tx.execute("SET LOCAL app.verifier_id = 'ops_review_alice'")
    tx.execute(
        "UPDATE source_document SET verification_status = 'VERIFIED'"
        " WHERE id = %s", (sid,))
    verifier = tx.execute(
        "SELECT verifier_id FROM source_document_verification_event"
        " WHERE source_document_id = %s", (sid,)).fetchone()[0]
    assert verifier == "ops_review_alice"


def test_audit_event_captures_declared_and_effective_levels(tx):
    """事件同时记录 declared 和 effective 前后状态。
    effective source_level 不可 UPDATE（immutable），
    所以对比通过不同 source_document 行（declared=S0/effective=S1 → 升 S0）。"""
    tx.execute("SET search_path = cegr, public")
    rid = _seed_registry(tx)

    # 上传者声明 S0，但平台核验通过前 effective 是 S1（合理：等待审核）
    sid = _insert_source_doc(tx, rid=rid, level="S1",
                             verification="UNVERIFIED",
                             declared="S0")
    # 触发一次 verification_status 变更 → 写审计
    tx.execute(
        "UPDATE source_document SET verification_status = 'PENDING'"
        " WHERE id = %s", (sid,))
    ev = tx.execute(
        "SELECT from_status, to_status,"
        " from_declared_level, from_effective_level,"
        " to_declared_level, to_effective_level"
        " FROM source_document_verification_event"
        " WHERE source_document_id = %s", (sid,)).fetchone()
    assert ev[0] == "UNVERIFIED" and ev[1] == "PENDING"
    assert ev[2] == "S0" and ev[3] == "S1"   # 变更前：declared=S0, effective=S1
    assert ev[4] == "S0" and ev[5] == "S1"   # 变更后：effective 仍 S1（immutable）


# ============================================================================
# 6. 审计表 append-only
# ============================================================================

def test_audit_event_update_rejected(tx):
    """source_document_verification_event 行不可 UPDATE。"""
    tx.execute("SET search_path = cegr, public")
    rid = _seed_registry(tx)
    sid = _insert_source_doc(tx, rid=rid, level="S1",
                             verification="UNVERIFIED")
    tx.execute(
        "UPDATE source_document SET verification_status = 'VERIFIED'"
        " WHERE id = %s", (sid,))
    eid = tx.execute(
        "SELECT id FROM source_document_verification_event"
        " WHERE source_document_id = %s LIMIT 1", (sid,)).fetchone()[0]
    with pytest.raises(psycopg.errors.RaiseException):
        tx.execute(
            "UPDATE source_document_verification_event"
            " SET evidence_note = 'tampered' WHERE id = %s", (eid,))


def test_audit_event_delete_rejected(tx):
    """source_document_verification_event 行不可 DELETE。"""
    tx.execute("SET search_path = cegr, public")
    rid = _seed_registry(tx)
    sid = _insert_source_doc(tx, rid=rid, level="S1",
                             verification="UNVERIFIED")
    tx.execute(
        "UPDATE source_document SET verification_status = 'VERIFIED'"
        " WHERE id = %s", (sid,))
    eid = tx.execute(
        "SELECT id FROM source_document_verification_event"
        " WHERE source_document_id = %s LIMIT 1", (sid,)).fetchone()[0]
    with pytest.raises(psycopg.errors.RaiseException):
        tx.execute(
            "DELETE FROM source_document_verification_event"
            " WHERE id = %s", (eid,))


# ============================================================================
# 7. source_document 原不可变性不被破坏
# ============================================================================

def test_source_document_immutable_other_fields_still_rejected(tx):
    """新触发器只允许 verification_status 变更；
    其他字段 (title/hash 等) UPDATE 仍然被 source_document_immutable 拒。"""
    tx.execute("SET search_path = cegr, public")
    rid = _seed_registry(tx)
    sid = _insert_source_doc(tx, rid=rid, level="S0",
                             verification="VERIFIED")
    with pytest.raises(psycopg.errors.RaiseException):
        tx.execute(
            "UPDATE source_document SET title = 'tampered' WHERE id = %s",
            (sid,))


def test_source_document_source_level_change_via_update_still_rejected(tx):
    """即使 verification_status=VERIFIED，source_level 仍不能通过 UPDATE 改。
    source_document_immutable trigger 把 source_level 列在不可变字段中。
    """
    tx.execute("SET search_path = cegr, public")
    rid = _seed_registry(tx)
    sid = _insert_source_doc(tx, rid=rid, level="S1",
                             verification="VERIFIED")
    with pytest.raises(psycopg.errors.RaiseException):
        tx.execute(
            "UPDATE source_document SET source_level = 'S0'"
            " WHERE id = %s", (sid,))


def test_source_document_no_delete(tx):
    """source_document 不可 DELETE（继承原有 no_delete trigger）。"""
    tx.execute("SET search_path = cegr, public")
    rid = _seed_registry(tx)
    sid = _insert_source_doc(tx, rid=rid, level="S0",
                             verification="VERIFIED")
    with pytest.raises(psycopg.errors.RaiseException):
        tx.execute("DELETE FROM source_document WHERE id = %s", (sid,))


# ============================================================================
# 8. caveat_text 仍允许 UPDATE（与既有约定一致）
# ============================================================================

def test_caveat_text_update_allowed(tx):
    """caveat_text 是 source_document_immutable 唯一允许的字段，
    verification_status 变更不应阻断它。"""
    tx.execute("SET search_path = cegr, public")
    rid = _seed_registry(tx)
    sid = _insert_source_doc(tx, rid=rid, level="S0",
                             verification="VERIFIED")
    tx.execute(
        "UPDATE source_document SET caveat_text = 'new caveat'"
        " WHERE id = %s", (sid,))
    assert _audit_count(tx, sid) == 0, (
        "caveat_text 不应触发 verification_event (verification_status 未变)"
    )


# ============================================================================
# 9. 同一 source_document 可被多次核验（审计完整）
# ============================================================================

def test_multiple_verification_cycles_audit_completeness(tx):
    """同一 source 经历 完整周期：UNVERIFIED → PENDING → REJECTED →
    UNVERIFIED → VERIFIED，应有 4 条审计事件。"""
    tx.execute("SET search_path = cegr, public")
    rid = _seed_registry(tx)
    sid = _insert_source_doc(tx, rid=rid, level="S1",
                             verification="UNVERIFIED")
    transitions = ["PENDING", "REJECTED", "UNVERIFIED", "VERIFIED"]
    for s in transitions:
        tx.execute(
            "UPDATE source_document SET verification_status = %s"
            " WHERE id = %s", (s, sid))
    assert _audit_count(tx, sid) == 4
