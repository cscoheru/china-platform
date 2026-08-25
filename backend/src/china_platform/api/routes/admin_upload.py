"""Stage 1 / S1.13.1 — /admin/upload 人工上传入口 (REST).

Per docs/28 §1.1 + Cursor 100 §SCHEMA / 裁定.

约束 (R08 措施 4/7):
  * Bearer ADMIN_UPLOAD_TOKEN 鉴权
  * copyright_note ≥ 20 chars (强制授权声明)
  * ≤100 MB 文件 (configurable)
  * 文件白名单扩展: pdf/xlsx/xls/csv/html
  * SHA-256 唯一约束 (已有 → 409)
  * source_id 必须存在 (422)
  * 全部成功 / 失败 写 admin_upload_audit (append-only)
  * UNVERIFIED source_document 登记 (verification_status 升 S0 待 ops 手动)

注意: 走独立 psycopg2 连接 (绕过 Database pool 的 SET TRANSACTION READ ONLY);
Database pool 是 S1.10 read-only API 专用, upload 写操作需独立连接。
"""

from __future__ import annotations

import hashlib
import logging
import os
import re
import uuid
from datetime import datetime, timezone
from pathlib import Path

import psycopg2
import psycopg2.extras
from fastapi import APIRouter, Depends, File, Form, Header, HTTPException, Request, UploadFile, status

from china_platform.api.config import ApiSettings, get_settings

log = logging.getLogger(__name__)

router = APIRouter(prefix="/admin", tags=["admin"])

ALLOWED_FILE_FORMATS = {"pdf", "xlsx", "xls", "csv", "html"}
ALLOWED_EXTRACTION_METHODS = {
    "pdf": "PDF_OCR",
    "xlsx": "EXCEL_PARSE",
    "xls": "EXCEL_PARSE",
    "csv": "CSV_PARSE",
    "html": "HTML_PARSE",
}
COPYRIGHT_NOTE_MIN_LEN = 20
SHA256_RE = re.compile(r"^[a-f0-9]{64}$")


def _write_db_factory():
    """Factory for non-pooled write connections.

    The Database pool (S1.10) enforces SET TRANSACTION READ ONLY.
    /admin/upload writes to cegr.source_document + admin_upload_audit, so
    we need a separate connection that can write.
    """
    settings = get_settings()
    return psycopg2.connect(settings.resolved_dsn())


def _compute_sha256(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            h.update(chunk)
    return h.hexdigest()


def _ext_for_filename(name: str) -> str | None:
    if "." not in name:
        return None
    ext = name.rsplit(".", 1)[1].lower()
    return ext if ext in ALLOWED_FILE_FORMATS else None


def _audit_failure(
    uploader_id: str | None,
    source_id_str: str | None,
    error_code: str,
    request: Request,
    settings: ApiSettings,
    file_hash: str | None = None,
    file_size: int | None = None,
    file_format: str | None = None,
    declared_url: str | None = None,
    purpose_note: str | None = None,
) -> None:
    """Best-effort failure audit. Never raises (failure path must not crash)."""
    try:
        psycopg2.extras.register_uuid()
        with _write_db_factory() as conn:
            with conn.cursor() as cur:
                source_uuid = None
                if source_id_str:
                    try:
                        source_uuid = uuid.UUID(source_id_str)
                    except ValueError:
                        source_uuid = None
                cur.execute(
                    """
                    INSERT INTO public.admin_upload_audit
                        (uploader_id, source_id, file_hash_sha256, file_size_bytes,
                         file_format, client_ip, auth_method, status, error_code,
                         purpose_note, declared_url)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    """,
                    (
                        uploader_id or "<unknown>",
                        source_uuid,
                        file_hash,
                        file_size,
                        file_format,
                        (request.client.host if request.client else None),
                        "BEARER_TOKEN",
                        "FAILED",
                        error_code,
                        purpose_note,
                        declared_url,
                    ),
                )
            conn.commit()
    except Exception as audit_err:
        log.warning("audit_failure best-effort insert failed: %s", audit_err)


@router.post(
    "/upload",
    status_code=status.HTTP_200_OK,
    summary="人工上传受扫码 PDF / 受限源文件 (R08 措施 4/7)",
    responses={
        200: {"description": "Upload accepted + registered"},
        400: {"description": "INVALID_FILE_TYPE / MISSING_AUTH_DECLARATION / INVALID_SOURCE_ID"},
        401: {"description": "INVALID_TOKEN"},
        409: {"description": "SHA_COLLISION"},
        413: {"description": "FILE_TOO_LARGE"},
        422: {"description": "SOURCE_NOT_FOUND"},
        503: {"description": "ADMIN_UPLOAD_DISABLED (token not configured)"},
    },
)
async def admin_upload(
    request: Request,
    file: UploadFile = File(...),
    source_id: str = Form(...),
    declared_url: str = Form(...),
    copyright_note: str = Form(...),
    uploader_id: str = Form(...),
    period_label: str | None = Form(default=None),
    purpose_note: str | None = Form(default=None),
    force_replace: bool = Form(default=False),
    authorization: str | None = Header(default=None),
    settings: ApiSettings = Depends(get_settings),
) -> dict:
    """上传 + 登记 + 审计. 详见 docs/28 §1.1."""
    # ----- Auth -----
    if not settings.admin_upload_token:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail={"error_code": "ADMIN_UPLOAD_DISABLED",
                    "message": "ADMIN_UPLOAD_TOKEN not configured on server"},
        )
    expected_header = f"Bearer {settings.admin_upload_token}"
    if authorization != expected_header:
        await _write_audit_async(
            uploader_id=uploader_id, source_id_str=source_id,
            error_code="INVALID_TOKEN", request=request, settings=settings,
        )
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={"error_code": "INVALID_TOKEN",
                    "message": "Missing or invalid Authorization header"},
            headers={"WWW-Authenticate": "Bearer"},
        )

    # ----- Validate -----
    if len(copyright_note.strip()) < COPYRIGHT_NOTE_MIN_LEN:
        await _write_audit_async(
            uploader_id=uploader_id, source_id_str=source_id,
            error_code="MISSING_AUTH_DECLARATION", request=request, settings=settings,
            copyright_note=copyright_note,
            declared_url=declared_url,
        )
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"error_code": "MISSING_AUTH_DECLARATION",
                    "message": f"copyright_note must be ≥ {COPYRIGHT_NOTE_MIN_LEN} chars"},
        )

    try:
        source_uuid = uuid.UUID(source_id)
    except ValueError:
        await _write_audit_async(
            uploader_id=uploader_id, source_id_str=source_id,
            error_code="INVALID_SOURCE_ID", request=request, settings=settings,
            copyright_note=copyright_note, declared_url=declared_url,
        )
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"error_code": "INVALID_SOURCE_ID",
                    "message": "source_id must be a UUID"},
        )

    filename = file.filename or "unnamed"
    ext = _ext_for_filename(filename)
    if ext is None:
        await _write_audit_async(
            uploader_id=uploader_id, source_id=source_uuid,
            error_code="INVALID_FILE_TYPE", request=request, settings=settings,
            copyright_note=copyright_note, declared_url=declared_url,
        )
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"error_code": "INVALID_FILE_TYPE",
                    "message": f"filename must end in one of {sorted(ALLOWED_FILE_FORMATS)}",
                    "filename": filename},
        )

    # ----- Stream to disk + size guard -----
    settings_uploads = Path(settings.uploads_dir)
    settings_uploads.mkdir(parents=True, exist_ok=True)

    tmp_path = settings_uploads / f".upload-{uuid.uuid4().hex}.tmp"
    file_size = 0
    try:
        with open(tmp_path, "wb") as f:
            while True:
                chunk = await file.read(8192)
                if not chunk:
                    break
                file_size += len(chunk)
                if file_size > settings.max_upload_size_bytes:
                    f.close()
                    tmp_path.unlink(missing_ok=True)
                    await _write_audit_async(
                        uploader_id=uploader_id, source_id=source_uuid,
                        error_code="FILE_TOO_LARGE", request=request,
                        settings=settings,
                        file_size=file_size, file_format=ext,
                        copyright_note=copyright_note,
                        declared_url=declared_url,
                    )
                    raise HTTPException(
                        status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                        detail={"error_code": "FILE_TOO_LARGE",
                                "message": f"file exceeds {settings.max_upload_size_bytes} bytes"},
                    )
                f.write(chunk)
    finally:
        await file.close()

    sha256 = _compute_sha256(tmp_path)

    # ----- Move to canonical path (content-addressed) -----
    now = datetime.now(timezone.utc)
    yyyy = now.strftime("%Y")
    mm = now.strftime("%m")
    canonical_dir = (
        settings_uploads / str(source_uuid) / yyyy / mm / sha256[:2]
    )
    canonical_dir.mkdir(parents=True, exist_ok=True)
    final_path = canonical_dir / f"{sha256}.{ext}"
    if final_path.exists() and not force_replace:
        # Already on disk; treat as SHA_COLLISION (only if different source_document)
        tmp_path.unlink(missing_ok=True)
        await _write_audit_async(
            uploader_id=uploader_id, source_id=source_uuid,
            error_code="SHA_COLLISION", request=request, settings=settings,
            file_hash=sha256, file_size=file_size, file_format=ext,
            copyright_note=copyright_note, declared_url=declared_url,
        )
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail={"error_code": "SHA_COLLISION",
                    "message": f"file_hash_sha256={sha256[:16]}... already uploaded"},
        )
    tmp_path.rename(final_path)

    # ----- DB: verify source_registry exists, then INSERT source_document + audit -----
    psycopg2.extras.register_uuid()
    try:
        with _write_db_factory() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    "SELECT organization, source_level, declared_source_level FROM cegr.source_registry WHERE id = %s",
                    (str(source_uuid),),
                )
                row = cur.fetchone()
                if row is None:
                    final_path.unlink(missing_ok=True)
                    await _write_audit_async(
                        uploader_id=uploader_id, source_id=source_uuid,
                        error_code="SOURCE_NOT_FOUND", request=request,
                        settings=settings,
                        file_hash=sha256, file_size=file_size, file_format=ext,
                        copyright_note=copyright_note,
                        declared_url=declared_url,
                    )
                    raise HTTPException(
                        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                        detail={"error_code": "SOURCE_NOT_FOUND",
                                "message": f"source_id={source_uuid} not in source_registry"},
                    )
                organization, registry_level, declared_level = row

                # SHA collision across different source_documents
                cur.execute(
                    "SELECT id FROM cegr.source_document WHERE file_hash_sha256 = %s",
                    (sha256,),
                )
                existing = cur.fetchone()
                if existing and not force_replace:
                    final_path.unlink(missing_ok=True)
                    raise HTTPException(
                        status_code=status.HTTP_409_CONFLICT,
                        detail={"error_code": "SHA_COLLISION",
                                "message": f"SHA-256 already in source_document (id={existing[0]})"},
                    )

                doc_id = uuid.uuid4()
                extraction_method = ALLOWED_EXTRACTION_METHODS[ext]
                cur.execute(
                    """
                    INSERT INTO cegr.source_document
                        (id, source_registry_id, source_level, verification_status,
                         title, publisher, url, file_path, file_hash_sha256,
                         file_format, file_size_bytes, extraction_method,
                         copyright_note, caveat_text, uploader_id)
                    VALUES (%s, %s, %s, 'UNVERIFIED',
                            %s, %s, %s, %s, %s,
                            %s, %s, %s,
                            %s, %s, %s)
                    """,
                    (
                        str(doc_id), str(source_uuid),
                        # Use declared_level until VERIFIED; mirror schema constraint
                        declared_level if declared_level == registry_level else registry_level,
                        f"{organization} - {filename} ({now.isoformat()})",
                        organization,
                        declared_url if declared_url else None,
                        str(final_path),
                        sha256,
                        ext,
                        file_size,
                        extraction_method,
                        copyright_note,
                        f"UPLOADED_VIA_ADMIN; verification_status=UNVERIFIED; period_label={period_label}",
                        uploader_id,
                    ),
                )

                # Audit row (success)
                cur.execute(
                    """
                    INSERT INTO public.admin_upload_audit
                        (uploader_id, source_id, file_hash_sha256, file_size_bytes,
                         file_format, client_ip, auth_method, status, purpose_note,
                         declared_url)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    """,
                    (
                        uploader_id, str(source_uuid), sha256, file_size, ext,
                        request.client.host if request.client else None,
                        "BEARER_TOKEN", "SUCCESS",
                        purpose_note, declared_url,
                    ),
                )
            conn.commit()
    except HTTPException:
        raise
    except Exception as e:
        log.exception("upload DB write failed")
        final_path.unlink(missing_ok=True)
        await _write_audit_async(
            uploader_id=uploader_id, source_id=source_uuid,
            error_code="DB_WRITE_FAILED", request=request, settings=settings,
            file_hash=sha256, file_size=file_size, file_format=ext,
            copyright_note=copyright_note, declared_url=declared_url,
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"error_code": "DB_WRITE_FAILED",
                    "message": str(e)},
        )

    return {
        "source_document_id": str(doc_id),
        "file_hash_sha256": sha256,
        "file_size_bytes": file_size,
        "stored_path": str(final_path),
        "extraction_trigger": (
            "OCR_QUEUED" if extraction_method == "PDF_OCR" else "MANUAL_PIPELINE_NEEDED"
        ),
        "verification_status": "UNVERIFIED",
        "next_steps": [
            "review observation_quality_flag (R04 措施 4)",
            "rerun GE checkpoint d2_source_document_suite",
            "manual verification_status flip to VERIFIED when ready",
        ],
    }


async def _write_audit_async(**kwargs) -> None:
    """Synchronous shim (psycopg2 in threadpool would be ideal; KISS for Stage 1)."""
    _audit_failure(
        uploader_id=kwargs.get("uploader_id"),
        source_id_str=kwargs.get("source_id_str") or str(kwargs["source_id"]) if kwargs.get("source_id") else kwargs.get("source_id_str"),
        error_code=kwargs["error_code"],
        request=kwargs["request"],
        settings=kwargs["settings"],
        file_hash=kwargs.get("file_hash"),
        file_size=kwargs.get("file_size"),
        file_format=kwargs.get("file_format"),
        declared_url=kwargs.get("declared_url"),
        purpose_note=kwargs.get("purpose_note"),
    )