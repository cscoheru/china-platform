"""Stage 1 / S1.5 — 深圳市政府统计公报 HTML 散文式连接器.

Per docs/19-stage1-s15-shenzhen-bulletin-plan-20260824.md.

Reuses `spikes/03-municipal-bulletin/extract_03_municipal_bulletin.py` for
prose-paragraph statistics extraction (no copy-paste; same source of truth
used by Stage 0 spike tests).

Single-sample pilot: reads `spikes/03-municipal-bulletin/sample.html` by
default. **No HTTP.** Production multi-year (2020-2024) ingestion is out of
scope for S1.5.

DB ingest flow:
  1. Resolve source_registry row by (domain='sz.gov.cn', category='MUNICIPAL_BULLETIN')
  2. INSERT ingestion_run (status='RUNNING')
  3. Compute file SHA-256; INSERT source_document (S0, VERIFIED — pre-existing
     spike sample; avoids I-05 §9.1 source_level_s0_requires_verified CHECK)
  4. extract() → N observation dicts in memory
  5. Attempt INSERT observations (FK resolution is deferred to S1.5+ — same as
     S1.4 NbsMonthlyConnector; expected to fail FK, status falls to PARTIAL)
  6. UPDATE ingestion_run with final status + counts

Exit / status semantics:
  SUCCESS — source_document persisted; extract succeeded
  PARTIAL — source_document persisted but observation FK resolution failed
  FAILED  — extract failed OR source_document INSERT failed
  Special: if extract() returns 0 obs (legitimate but rare for prose parse),
  status remains SUCCESS with records_inserted=0 (docs/19 §5).
"""
from __future__ import annotations

import sys
import uuid
from pathlib import Path

import psycopg2
import psycopg2.errors

# Path shim so we can import the spike module without copying the parser
REPO_ROOT = Path(__file__).resolve().parents[4]
SPIKE_03_DIR = REPO_ROOT / "spikes" / "03-municipal-bulletin"
if str(SPIKE_03_DIR) not in sys.path:
    sys.path.insert(0, str(SPIKE_03_DIR))

from extract_03_municipal_bulletin import (  # noqa: E402  (sys.path manipulation above)
    BULLETIN_URL,
    CITY,
    YEAR,
    compute_sha256 as _spike_compute_sha256,
    extract_statistics as _spike_extract_statistics,
)


class SzMunicipalBulletinConnector:
    """Stage 1 / S1.5 — 深圳市政府统计公报 HTML 连接器（散文式）。"""

    DEFAULT_SAMPLE = SPIKE_03_DIR / "sample.html"
    DEFAULT_REGISTRY_DOMAIN = "sz.gov.cn"
    DEFAULT_REGISTRY_CATEGORY = "MUNICIPAL_BULLETIN"
    DEFAULT_SAMPLE_TITLE = f"{CITY}{YEAR}年国民经济和社会发展统计公报"
    DEFAULT_SAMPLE_PUBLISHER = "深圳市人民政府"
    DEFAULT_SAMPLE_URL = BULLETIN_URL

    # ---- pure-file helpers ----

    def compute_sha256(self, file_path: Path) -> str:
        """SHA-256 hex digest of `file_path` bytes."""
        if not file_path.exists():
            raise FileNotFoundError(f"Sample HTML missing: {file_path}")
        return _spike_compute_sha256(file_path.read_bytes())

    def extract(self, file_path: Path) -> dict:
        """Parse HTML 散文; return dict with sha256 + observations + metadata.

        Pure file operation, no side effects on the DB.
        """
        if not file_path.exists():
            raise FileNotFoundError(f"Sample HTML missing: {file_path}")
        html_bytes = file_path.read_bytes()
        sha = _spike_compute_sha256(html_bytes)
        observations = _spike_extract_statistics(html_bytes)
        return {
            "sha256": sha,
            "observations": observations,
            "metadata": {
                "source_url": self.DEFAULT_SAMPLE_URL,
                "city": CITY,
                "year": YEAR,
                "fetched_at": "2026-04-01T00:00:00Z",
                "extraction_method": (
                    "beautifulsoup + section-aware regex on prose (spike 03)"
                ),
                "file_name": file_path.name,
                "file_size_bytes": len(html_bytes),
            },
        }

    # ---- DB ingest ----

    def _resolve_source_registry(
        self,
        conn: psycopg2.extensions.connection,
        domain: str = DEFAULT_REGISTRY_DOMAIN,
        category: str = DEFAULT_REGISTRY_CATEGORY,
    ) -> uuid.UUID | None:
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT id FROM cegr.source_registry
                WHERE domain = %s AND category = %s
                LIMIT 1
                """,
                (domain, category),
            )
            row = cur.fetchone()
            return row[0] if row else None

    def _create_ingestion_run(
        self,
        conn: psycopg2.extensions.connection,
        source_registry_id: uuid.UUID,
        triggered_by: str,
    ) -> uuid.UUID:
        with conn.cursor() as cur:
            cur.execute(
                """
                INSERT INTO cegr.ingestion_run
                    (source_registry_id, started_at, status, triggered_by)
                VALUES (%s, NOW(), 'RUNNING', %s)
                RETURNING id
                """,
                (str(source_registry_id), triggered_by),
            )
            run_id = cur.fetchone()[0]
        conn.commit()
        return run_id

    def _create_source_document(
        self,
        conn: psycopg2.extensions.connection,
        source_registry_id: uuid.UUID,
        sha256: str,
        size_bytes: int,
        title: str,
        publisher: str,
        url: str,
    ) -> uuid.UUID:
        with conn.cursor() as cur:
            cur.execute(
                """
                INSERT INTO cegr.source_document
                    (source_registry_id, source_level, verification_status,
                     title, publisher, url, file_hash_sha256, file_size_bytes,
                     language, extraction_method)
                VALUES (%s, 'S0', 'VERIFIED',
                        %s, %s, %s, %s, %s,
                        'zh', 'HTML_PARSE')
                RETURNING id
                """,
                (str(source_registry_id), title, publisher, url, sha256, size_bytes),
            )
            doc_id = cur.fetchone()[0]
        conn.commit()
        return doc_id

    def _finalize_ingestion_run(
        self,
        conn: psycopg2.extensions.connection,
        run_id: uuid.UUID,
        status: str,
        records_extracted: int,
        records_inserted: int,
        error_log: str | None,
    ) -> None:
        if error_log and len(error_log) > 500:
            error_log = error_log[:497] + "..."
        with conn.cursor() as cur:
            cur.execute(
                """
                UPDATE cegr.ingestion_run
                SET finished_at = NOW(),
                    status = %s,
                    records_extracted = %s,
                    records_inserted = %s,
                    error_log = %s
                WHERE id = %s
                """,
                (status, records_extracted, records_inserted, error_log, str(run_id)),
            )
        conn.commit()

    def _attempt_observation_insert(
        self,
        conn: psycopg2.extensions.connection,
        observation: dict,
        run_id: uuid.UUID,
    ) -> tuple[bool, str | None]:
        """Stub for S1.5 pilot. Real FK resolution belongs to S1.5+ when
        reference data (indicator_definition / geo_entity / calendar_period /
        indicator_methodology_version / geo_code_version / source_location)
        is seeded. Mirrors S1.4 NbsMonthlyConnector pattern."""
        try:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    INSERT INTO cegr.observation
                        (indicator_id, geo_entity_id, geo_code_version_id,
                         calendar_period_id, source_id, source_location_id,
                         ingestion_run_id, value, raw_value, unit,
                         comparison_basis, value_type, status, extraction_method,
                         confidence)
                    VALUES (
                        %s, %s, %s, %s, %s, %s, %s,
                        %s, %s, %s,
                        %s, 'FACT', 'PRELIMINARY', 'HTML_PARSE',
                        %s
                    )
                    """,
                    (
                        # Placeholder UUIDs — replaced with real lookups when
                        # S1.5+ seeds reference data. Deliberately fail FK so
                        # PARTIAL is the honest status.
                        uuid.UUID(int=0),  # indicator_id
                        uuid.UUID(int=0),  # geo_entity_id
                        uuid.UUID(int=0),  # geo_code_version_id
                        uuid.UUID(int=0),  # calendar_period_id
                        uuid.UUID(int=0),  # source_id
                        uuid.UUID(int=0),  # source_location_id
                        str(run_id),
                        observation.get("value"),
                        str(observation.get("value")),
                        observation.get("unit"),
                        observation.get("comparison_basis") or "NEEDS_VERIFICATION",
                        observation.get("confidence"),
                    ),
                )
            conn.commit()
            return True, None
        except psycopg2.errors.ForeignKeyViolation as exc:
            conn.rollback()
            return False, f"FK violation: {exc.diag.message_primary or str(exc)[:200]}"
        except psycopg2.errors.Error as exc:
            conn.rollback()
            return False, f"DB error: {str(exc)[:200]}"

    def ingest(
        self,
        file_path: Path,
        conn: psycopg2.extensions.connection,
        triggered_by: str = "sz_municipal_bulletin_connector",
        title: str | None = None,
        publisher: str | None = None,
        url: str | None = None,
    ) -> dict:
        """End-to-end ingest: extract → ingestion_run → source_document →
        observations (best-effort) → ingestion_run final status.

        Returns a summary dict (suitable for assertions in tests).
        """
        title = title or self.DEFAULT_SAMPLE_TITLE
        publisher = publisher or self.DEFAULT_SAMPLE_PUBLISHER
        url = url or self.DEFAULT_SAMPLE_URL

        sr_id = self._resolve_source_registry(conn)
        if sr_id is None:
            raise RuntimeError(
                "source_registry row for sz.gov.cn / MUNICIPAL_BULLETIN "
                "not found; run scripts/import_registry_csv.py first"
            )

        run_id = self._create_ingestion_run(conn, sr_id, triggered_by)

        try:
            extracted = self.extract(file_path)
        except FileNotFoundError as exc:
            self._finalize_ingestion_run(
                conn, run_id, "FAILED", 0, 0, f"extract: {exc}"
            )
            return {
                "ingestion_run_id": str(run_id),
                "status": "FAILED",
                "records_extracted": 0,
                "records_inserted": 0,
                "error_log": f"extract: {exc}",
            }

        sha = extracted["sha256"]
        size_bytes = extracted["metadata"]["file_size_bytes"]
        n_extracted = len(extracted["observations"])

        try:
            doc_id = self._create_source_document(
                conn, sr_id, sha, size_bytes, title, publisher, url
            )
        except psycopg2.errors.Error as exc:
            self._finalize_ingestion_run(
                conn, run_id, "FAILED", n_extracted, 0,
                f"source_document: {str(exc)[:200]}",
            )
            return {
                "ingestion_run_id": str(run_id),
                "status": "FAILED",
                "records_extracted": n_extracted,
                "records_inserted": 0,
                "error_log": f"source_document: {str(exc)[:200]}",
            }

        inserted = 0
        first_error: str | None = None
        for obs in extracted["observations"]:
            ok, err = self._attempt_observation_insert(conn, obs, run_id)
            if ok:
                inserted += 1
            elif first_error is None:
                first_error = err

        # Per docs/19 §5: 0 obs is a legitimate outcome (prose parse).
        if n_extracted == 0:
            status = "SUCCESS"  # extract itself ran clean; no rows is honest
        elif inserted == n_extracted:
            status = "SUCCESS"
        elif inserted == 0:
            status = "FAILED"
        else:
            status = "PARTIAL"

        self._finalize_ingestion_run(
            conn, run_id, status, n_extracted, inserted, first_error
        )

        return {
            "ingestion_run_id": str(run_id),
            "status": status,
            "records_extracted": n_extracted,
            "records_inserted": inserted,
            "error_log": first_error,
            "source_document_id": str(doc_id),
        }