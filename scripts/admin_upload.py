"""Stage 1 / S1.13.1 — CLI /admin/upload (对称 REST 能力).

Per docs/28 §1.2 + Cursor 100 §NOW-2.

Usage:
  python3 scripts/admin_upload.py \\
    --source-id <uuid> \\
    --file /path/to/file.pdf \\
    --declared-url <url> \\
    --copyright-note "<≥20 chars>" \\
    --uploader-id <id> \\
    [--period-label "2024-H1"] \\
    [--purpose-note "..."] \\
    [--force-replace]

DSN: ${CEGR_DSN:-${STAGE0_DSN}}
Output: stdout JSON envelope (mirror REST response)
Exit code: 0 success, 1 on failure
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import sys
import uuid
from datetime import datetime, timezone
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent

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


def _dsn() -> str:
    return os.environ.get(
        "CEGR_DSN",
        os.environ.get("STAGE0_DSN", "postgresql://postgres:postgres@127.0.0.1:55440/cegr_test"),
    )


def _ext_for_filename(name: str) -> str | None:
    if "." not in name:
        return None
    ext = name.rsplit(".", 1)[1].lower()
    return ext if ext in ALLOWED_FILE_FORMATS else None


def _compute_sha256(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            h.update(chunk)
    return h.hexdigest()


def _audit(
    uploader_id: str,
    source_id_str: str | None,
    status_: str,
    error_code: str | None,
    file_hash: str | None,
    file_size: int | None,
    file_format: str | None,
    declared_url: str | None,
    purpose_note: str | None,
) -> None:
    try:
        import psycopg2  # type: ignore
        import psycopg2.extras  # type: ignore
        psycopg2.extras.register_uuid()
        source_uuid = None
        if source_id_str:
            try:
                source_uuid = uuid.UUID(source_id_str)
            except ValueError:
                source_uuid = None
        with psycopg2.connect(_dsn()) as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    INSERT INTO public.admin_upload_audit
                        (uploader_id, source_id, file_hash_sha256, file_size_bytes,
                         file_format, client_ip, auth_method, status, error_code,
                         purpose_note, declared_url)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    """,
                    (uploader_id, source_uuid, file_hash, file_size, file_format,
                     None, "CLI", status_, error_code, purpose_note, declared_url),
                )
            conn.commit()
    except Exception as e:
        sys.stderr.write(f"[warn] audit write failed: {e}\n")


def upload(
    file_path: Path,
    source_id: str,
    declared_url: str,
    copyright_note: str,
    uploader_id: str,
    period_label: str | None = None,
    purpose_note: str | None = None,
    force_replace: bool = False,
    uploads_dir: str = "/tmp/cegr_uploads_cli",
) -> dict:
    """Mirror REST POST /admin/upload. Returns dict with response fields."""
    # ----- Validate -----
    if not file_path.exists():
        _audit(uploader_id, source_id, "FAILED", "FILE_NOT_FOUND",
               None, None, None, declared_url, purpose_note)
        raise SystemExit(f"ERROR: file not found: {file_path}")
    if len(copyright_note.strip()) < COPYRIGHT_NOTE_MIN_LEN:
        _audit(uploader_id, source_id, "FAILED", "MISSING_AUTH_DECLARATION",
               None, None, None, declared_url, purpose_note)
        raise SystemExit(f"ERROR: copyright_note must be ≥ {COPYRIGHT_NOTE_MIN_LEN} chars")
    try:
        source_uuid = uuid.UUID(source_id)
    except ValueError:
        _audit(uploader_id, source_id, "FAILED", "INVALID_SOURCE_ID",
               None, None, None, declared_url, purpose_note)
        raise SystemExit(f"ERROR: source_id is not a UUID: {source_id}")

    ext = _ext_for_filename(file_path.name)
    if ext is None:
        _audit(uploader_id, source_id, "FAILED", "INVALID_FILE_TYPE",
               None, None, None, declared_url, purpose_note)
        raise SystemExit(
            f"ERROR: file extension must be one of {sorted(ALLOWED_FILE_FORMATS)}"
        )

    # ----- Compute SHA + write to canonical path -----
    sha256 = _compute_sha256(file_path)
    file_size = file_path.stat().st_size

    now = datetime.now(timezone.utc)
    yyyy = now.strftime("%Y")
    mm = now.strftime("%m")
    canonical_dir = Path(uploads_dir) / str(source_uuid) / yyyy / mm / sha256[:2]
    canonical_dir.mkdir(parents=True, exist_ok=True)
    final_path = canonical_dir / f"{sha256}.{ext}"

    if final_path.exists() and not force_replace:
        _audit(uploader_id, source_id, "FAILED", "SHA_COLLISION",
               sha256, file_size, ext, declared_url, purpose_note)
        raise SystemExit(
            f"ERROR: SHA_COLLISION — file already uploaded at {final_path}"
        )

    # ----- DB -----
    import psycopg2  # type: ignore
    import psycopg2.extras  # type: ignore
    psycopg2.extras.register_uuid()
    try:
        with psycopg2.connect(_dsn()) as conn:
            with conn.cursor() as cur:
                cur.execute(
                    "SELECT organization, source_level, declared_source_level FROM cegr.source_registry WHERE id = %s",
                    (str(source_uuid),),
                )
                row = cur.fetchone()
                if row is None:
                    _audit(uploader_id, source_id, "FAILED", "SOURCE_NOT_FOUND",
                           sha256, file_size, ext, declared_url, purpose_note)
                    raise SystemExit(f"ERROR: source_id={source_uuid} not in source_registry")
                organization, registry_level, declared_level = row

                cur.execute(
                    "SELECT id FROM cegr.source_document WHERE file_hash_sha256 = %s",
                    (sha256,),
                )
                existing = cur.fetchone()
                if existing and not force_replace:
                    _audit(uploader_id, source_id, "FAILED", "SHA_COLLISION",
                           sha256, file_size, ext, declared_url, purpose_note)
                    raise SystemExit(
                        f"ERROR: SHA_COLLISION — SHA-256 already in source_document (id={existing[0]})"
                    )

                doc_id = uuid.uuid4()
                extraction_method = ALLOWED_EXTRACTION_METHODS[ext]

                # Copy file to canonical path
                import shutil
                shutil.copy2(file_path, final_path)

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
                        declared_level if declared_level == registry_level else registry_level,
                        f"{organization} - {file_path.name} ({now.isoformat()})",
                        organization,
                        declared_url if declared_url else None,
                        str(final_path),
                        sha256,
                        ext,
                        file_size,
                        extraction_method,
                        copyright_note,
                        f"UPLOADED_VIA_CLI; verification_status=UNVERIFIED; period_label={period_label}",
                        uploader_id,
                    ),
                )
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
                        None, "CLI", "SUCCESS", purpose_note, declared_url,
                    ),
                )
            conn.commit()
    except SystemExit:
        raise
    except Exception as e:
        _audit(uploader_id, source_id, "FAILED", "DB_WRITE_FAILED",
               sha256, file_size, ext, declared_url, purpose_note)
        raise SystemExit(f"ERROR: DB write failed: {e}")

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


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    parser.add_argument("--source-id", required=True, help="UUID of source_registry entry")
    parser.add_argument("--file", required=True, type=Path, help="Path to file")
    parser.add_argument("--declared-url", required=True, help="Declared source URL (can be empty string)")
    parser.add_argument("--copyright-note", required=True, help=f"Auth declaration ≥ {COPYRIGHT_NOTE_MIN_LEN} chars")
    parser.add_argument("--uploader-id", required=True, help="Uploader identifier")
    parser.add_argument("--period-label", default=None)
    parser.add_argument("--purpose-note", default=None)
    parser.add_argument("--force-replace", action="store_true")
    parser.add_argument("--uploads-dir", default="/tmp/cegr_uploads_cli")
    args = parser.parse_args()

    result = upload(
        file_path=args.file,
        source_id=args.source_id,
        declared_url=args.declared_url,
        copyright_note=args.copyright_note,
        uploader_id=args.uploader_id,
        period_label=args.period_label,
        purpose_note=args.purpose_note,
        force_replace=args.force_replace,
        uploads_dir=args.uploads_dir,
    )
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()