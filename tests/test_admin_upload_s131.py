"""Stage 1 / S1.13.1 — /admin/upload tests.

Per docs/28 §4 + Cursor 100 §NOW-4 (≥7 tests).

Strategy:
  - Session-scoped autouse fixture seeds minimal data (source_registry entry).
  - Tests use FastAPI TestClient against the lifespan-managed app.
  - ADMIN_UPLOAD_TOKEN is set via env var CEGR_API_ADMIN_UPLOAD_TOKEN
    (ApiSettings reads CEGR_API_* prefix).

Tests:
  1. test_upload_happy_path — auth + valid inputs → 200 + source_document registered
  2. test_upload_auth_missing — no Authorization header → 401 INVALID_TOKEN
  3. test_upload_auth_wrong_token — wrong Bearer token → 401
  4. test_upload_copyright_too_short — copyright_note < 20 chars → 400 MISSING_AUTH_DECLARATION
  5. test_upload_invalid_file_type — .exe extension → 400 INVALID_FILE_TYPE
  6. test_upload_invalid_source_id_format — non-UUID source_id → 400 INVALID_SOURCE_ID
  7. test_upload_source_not_found — UUID not in source_registry → 422 SOURCE_NOT_FOUND
  8. test_upload_sha_collision — second upload with same content → 409 SHA_COLLISION
  9. test_upload_audit_log_written — failed upload writes audit row with status=FAILED
"""

from __future__ import annotations

import io
import os
import sys
import tempfile
import uuid
from pathlib import Path

# Ensure backend/src is on sys.path.
_BACKEND_SRC = Path(__file__).resolve().parents[1] / "backend" / "src"
if str(_BACKEND_SRC) not in sys.path:
    sys.path.insert(0, str(_BACKEND_SRC))

import pytest
from fastapi.testclient import TestClient

# Set token BEFORE importing app (settings reads env at import)
TEST_TOKEN = "test-admin-upload-token-abc123"
os.environ["CEGR_API_ADMIN_UPLOAD_TOKEN"] = TEST_TOKEN
os.environ["CEGR_API_UPLOADS_DIR"] = tempfile.mkdtemp(prefix="cegr_test_uploads_")

import psycopg2  # noqa: E402
import psycopg2.extras  # noqa: E402

from china_platform.api.main import app  # noqa: E402

DSN = os.environ.get(
    "STAGE0_DSN",
    "postgresql://postgres:postgres@127.0.0.1:55440/cegr_test",
)

# Stable UUIDs for the demo source_registry entry.
TEST_SOURCE_ID = uuid.UUID("c1000000-0000-0000-0000-000000000001")


def _connect():
    psycopg2.extras.register_uuid()
    return psycopg2.connect(DSN)


def _seed_source_registry() -> None:
    """Insert a single source_registry entry for testing uploads against."""
    with _connect() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                INSERT INTO cegr.source_registry
                    (id, domain, organization, category, primary_url,
                     access_method, source_level, declared_source_level,
                     update_frequency, enabled, auth_note, purpose_note)
                VALUES (%s, 'test.local', 'TEST_UPLOAD_ORG', 'TEST',
                        'http://test.local/sample.pdf',
                        'MANUAL_UPLOAD', 'S1', 'S0',
                        'AD_HOC', TRUE, 'test', 'test source for /admin/upload tests')
                ON CONFLICT (id) DO NOTHING
                """,
                (str(TEST_SOURCE_ID),),
            )
        conn.commit()


def _purge_audit_for_test_source() -> None:
    """Best-effort: clean audit rows from previous runs (idempotent)."""
    with _connect() as conn:
        with conn.cursor() as cur:
            cur.execute(
                "DELETE FROM public.admin_upload_audit WHERE uploader_id = %s",
                ("test-uploader",),
            )
            cur.execute(
                "DELETE FROM cegr.source_document WHERE source_registry_id = %s",
                (str(TEST_SOURCE_ID),),
            )
        conn.commit()


@pytest.fixture(scope="session", autouse=True)
def _seed() -> None:
    try:
        _purge_audit_for_test_source()
        _seed_source_registry()
    except Exception as e:
        pytest.skip(f"DB seed failed (is cegr_test reachable?): {e}", allow_module_level=True)


@pytest.fixture()
def client_() -> "TestClient":
    with TestClient(app) as c:
        yield c


def _pdf_bytes(content: bytes = b"%PDF-1.4\n%fake pdf for upload test\n") -> bytes:
    return content


def _make_upload_payload(
    *,
    source_id: str | None = None,
    filename: str = "test.pdf",
    content: bytes | None = None,
    copyright_note: str = "公开 / 《著作权法》第五条 / 研究+审核",
    declared_url: str = "http://test.local/sample.pdf",
    uploader_id: str = "test-uploader",
    token: str | None = TEST_TOKEN,
):
    sid = source_id or str(TEST_SOURCE_ID)
    body = content if content is not None else _pdf_bytes()
    return {
        "file": (filename, io.BytesIO(body), "application/pdf"),
        "source_id": (None, sid),
        "declared_url": (None, declared_url),
        "copyright_note": (None, copyright_note),
        "uploader_id": (None, uploader_id),
    }, token


def _post(client: TestClient, files, form, token: str | None) -> "requests.Response":
    headers = {"Authorization": f"Bearer {token}"} if token else {}
    return client.post("/admin/upload", files=files, data=form, headers=headers)


def test_upload_happy_path(client_: TestClient) -> None:
    """Auth + valid → 200 + source_document registered."""
    payload, token = _make_upload_payload(content=_pdf_bytes(b"%PDF-1.4\nunique-happy-path\n"))
    files, form = payload, {k: v[1] for k, v in payload.items() if k != "file"}
    files = {**files, "file": payload["file"]}
    headers = {"Authorization": f"Bearer {token}"}

    r = client_.post("/admin/upload", files=files, data=form, headers=headers)
    assert r.status_code == 200, r.text
    body = r.json()
    assert "source_document_id" in body
    assert "file_hash_sha256" in body
    assert len(body["file_hash_sha256"]) == 64
    assert body["verification_status"] == "UNVERIFIED"
    assert body["extraction_trigger"] in ("OCR_QUEUED", "MANUAL_PIPELINE_NEEDED")

    # Verify source_document in DB
    with _connect() as conn:
        with conn.cursor() as cur:
            cur.execute(
                "SELECT file_hash_sha256, verification_status, copyright_note "
                "FROM cegr.source_document WHERE id = %s",
                (body["source_document_id"],),
            )
            row = cur.fetchone()
    assert row is not None
    assert row[0] == body["file_hash_sha256"]
    assert row[1] == "UNVERIFIED"
    assert "公开" in row[2]


def test_upload_auth_missing(client_: TestClient) -> None:
    """No Authorization header → 401 INVALID_TOKEN."""
    payload, _ = _make_upload_payload(content=_pdf_bytes(b"%PDF-1.4\nunique-auth-missing\n"))
    files, form = payload, {k: v[1] for k, v in payload.items() if k != "file"}
    files = {**files, "file": payload["file"]}

    r = client_.post("/admin/upload", files=files, data=form)  # no headers
    assert r.status_code == 401, r.text
    body = r.json()
    assert body["detail"]["error_code"] == "INVALID_TOKEN"


def test_upload_auth_wrong_token(client_: TestClient) -> None:
    """Wrong Bearer token → 401."""
    payload, _ = _make_upload_payload(content=_pdf_bytes(b"%PDF-1.4\nunique-auth-wrong\n"))
    files, form = payload, {k: v[1] for k, v in payload.items() if k != "file"}
    files = {**files, "file": payload["file"]}

    r = client_.post("/admin/upload", files=files, data=form,
                     headers={"Authorization": "Bearer wrong-token-xyz"})
    assert r.status_code == 401
    assert r.json()["detail"]["error_code"] == "INVALID_TOKEN"


def test_upload_copyright_too_short(client_: TestClient) -> None:
    """copyright_note < 20 chars → 400 MISSING_AUTH_DECLARATION."""
    payload, token = _make_upload_payload(
        content=_pdf_bytes(b"%PDF-1.4\nunique-copyright-short\n"),
        copyright_note="too short",
    )
    files, form = payload, {k: v[1] for k, v in payload.items() if k != "file"}
    files = {**files, "file": payload["file"]}
    r = client_.post("/admin/upload", files=files, data=form,
                     headers={"Authorization": f"Bearer {token}"})
    assert r.status_code == 400
    assert r.json()["detail"]["error_code"] == "MISSING_AUTH_DECLARATION"


def test_upload_invalid_file_type(client_: TestClient) -> None:
    """File with .exe extension → 400 INVALID_FILE_TYPE."""
    payload, token = _make_upload_payload(
        content=b"MZ" + b"\x00" * 100,
        filename="malware.exe",
    )
    files = {**payload, "file": (payload["file"][0], io.BytesIO(b"MZ" + b"\x00" * 100), "application/octet-stream")}
    form = {k: v[1] for k, v in payload.items() if k != "file"}
    r = client_.post("/admin/upload", files=files, data=form,
                     headers={"Authorization": f"Bearer {token}"})
    assert r.status_code == 400
    assert r.json()["detail"]["error_code"] == "INVALID_FILE_TYPE"


def test_upload_invalid_source_id_format(client_: TestClient) -> None:
    """source_id not a UUID → 400 INVALID_SOURCE_ID."""
    payload, token = _make_upload_payload(
        content=_pdf_bytes(b"%PDF-1.4\nunique-bad-source\n"),
        source_id="not-a-uuid",
    )
    files = payload
    form = {k: v[1] for k, v in payload.items() if k != "file"}
    r = client_.post("/admin/upload", files=files, data=form,
                     headers={"Authorization": f"Bearer {token}"})
    assert r.status_code == 400
    assert r.json()["detail"]["error_code"] == "INVALID_SOURCE_ID"


def test_upload_source_not_found(client_: TestClient) -> None:
    """Valid UUID but not in source_registry → 422 SOURCE_NOT_FOUND."""
    bogus_id = str(uuid.UUID("c1c2c3c4-0000-0000-0000-000000000000"))
    payload, token = _make_upload_payload(
        content=_pdf_bytes(b"%PDF-1.4\nunique-source-not-found\n"),
        source_id=bogus_id,
    )
    files = payload
    form = {k: v[1] for k, v in payload.items() if k != "file"}
    r = client_.post("/admin/upload", files=files, data=form,
                     headers={"Authorization": f"Bearer {token}"})
    assert r.status_code == 422
    assert r.json()["detail"]["error_code"] == "SOURCE_NOT_FOUND"


def test_upload_sha_collision(client_: TestClient) -> None:
    """Same content uploaded twice → 409 SHA_COLLISION."""
    content = _pdf_bytes(b"%PDF-1.4\nunique-sha-collision\n")
    payload, token = _make_upload_payload(content=content)
    files = payload
    form = {k: v[1] for k, v in payload.items() if k != "file"}

    # First upload: should succeed
    r1 = client_.post("/admin/upload", files=files, data=form,
                      headers={"Authorization": f"Bearer {token}"})
    assert r1.status_code == 200, r1.text

    # Second upload with same content: should fail SHA_COLLISION
    payload2, token2 = _make_upload_payload(content=content)
    files2 = payload2
    form2 = {k: v[1] for k, v in payload2.items() if k != "file"}
    r2 = client_.post("/admin/upload", files=files2, data=form2,
                      headers={"Authorization": f"Bearer {token2}"})
    assert r2.status_code == 409
    assert r2.json()["detail"]["error_code"] == "SHA_COLLISION"


def test_upload_audit_log_written(client_: TestClient) -> None:
    """Failed upload (missing token) writes audit row with status=FAILED."""
    # Use unique content so happy-path SHA doesn't pollute
    payload, _ = _make_upload_payload(content=_pdf_bytes(b"%PDF-1.4\nunique-audit-fail\n"))
    files = payload
    form = {k: v[1] for k, v in payload.items() if k != "file"}
    # No auth → must trigger INVALID_TOKEN + audit row
    r = client_.post("/admin/upload", files=files, data=form)
    assert r.status_code == 401

    # Audit row should exist with status=FAILED, error_code=INVALID_TOKEN
    with _connect() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT status, error_code, auth_method
                FROM public.admin_upload_audit
                WHERE uploader_id = 'test-uploader'
                ORDER BY timestamp_utc DESC
                LIMIT 1
                """,
            )
            row = cur.fetchone()
    assert row is not None, "audit row missing for failed auth"
    assert row[0] == "FAILED"
    assert row[1] == "INVALID_TOKEN"
    assert row[2] == "BEARER_TOKEN"