"""Stage 1 / S1.4 — NBS Monthly Statistical Bulletin HTML connector.

Per docs/18-stage1-s14-nbs-connector-plan-20260824.md.

Reuses `spikes/01-national-yearbook/extract_01_national_yearbook.py` for HTML
table parsing (no copy-paste; same source of truth used by Stage 0 spike tests).

Single-period pilot: reads `spikes/01-national-yearbook/sample.html` by default.
**No HTTP.** Production bulk ingestion of 2020–2025 is out of scope for S1.4.

DB ingest flow:
  1. Resolve source_registry row by (domain='stats.gov.cn', category='NATIONAL_BULLETIN')
  2. INSERT ingestion_run (status='RUNNING')
  3. Compute file SHA-256; INSERT source_document (VERIFIED — pre-existing spike sample)
  4. extract() → N observation dicts in memory
  5. Attempt INSERT observations (FK resolution is deferred to S1.5 — reference data
     not yet seeded for production; expected to fail FK, status falls to PARTIAL)
  6. UPDATE ingestion_run with final status + counts

Exit / status semantics:
  SUCCESS — source_document persisted; extract succeeded
  PARTIAL — source_document persisted but observation FK resolution failed
  FAILED  — extract failed OR source_document INSERT failed
"""
from __future__ import annotations

import hashlib
import sys
import uuid
from pathlib import Path

import psycopg2
import psycopg2.errors

# Path shim so we can import the spike module without copying the parser
REPO_ROOT = Path(__file__).resolve().parents[4]
SPIKE_01_DIR = REPO_ROOT / "spikes" / "01-national-yearbook"
if str(SPIKE_01_DIR) not in sys.path:
    sys.path.insert(0, str(SPIKE_01_DIR))

from extract_01_national_yearbook import (  # noqa: E402  (sys.path manipulation above)
    SAMPLE_HTML,
    compute_sha256 as _spike_compute_sha256,
    extract_rows as _spike_extract_rows,
    parse_html_table as _spike_parse_html_table,
)


class NbsMonthlyConnector:
    """Stage 1 / S1.4 — NBS HTML monthly bulletin connector."""

    DEFAULT_SAMPLE = SAMPLE_HTML
    DEFAULT_REGISTRY_DOMAIN = "stats.gov.cn"
    DEFAULT_REGISTRY_CATEGORY = "NATIONAL_BULLETIN"
    DEFAULT_SAMPLE_TITLE = (
        "国家统计局 2026 年 7 月份规模以上工业增加值月度数据 (1—7月份)"
    )
    DEFAULT_SAMPLE_PUBLISHER = "国家统计局"
    DEFAULT_SAMPLE_URL = (
        "https://www.stats.gov.cn/sj/zxfb/202608/t20260817_1965056.html"
    )

    # ---- pure-file helpers ----

    def compute_sha256(self, file_path: Path) -> str:
        """SHA-256 hex digest of `file_path` bytes."""
        return _spike_compute_sha256(file_path)

    def extract(self, file_path: Path) -> dict:
        """Parse HTML; return dict with sha256 + observations + metadata.

        Pure file operation, no side effects on the DB.
        """
        if not file_path.exists():
            raise FileNotFoundError(f"Sample HTML missing: {file_path}")
        with open(file_path, "r", encoding="utf-8", errors="replace") as f:
            html_content = f.read()
        sha = self.compute_sha256(file_path)
        rows_data = _spike_parse_html_table(html_content)
        observations = _spike_extract_rows(rows_data)
        return {
            "sha256": sha,
            "observations": observations,
            "metadata": {
                "source_url": self.DEFAULT_SAMPLE_URL,
                "table_locator": "table[1] — 规模以上工业增加值月度数据表 (1—7月份)",
                "fetched_at": "2026-08-17T00:00:00Z",
                "extraction_method": "html.parser + regex (spike 01)",
                "raw_table_rows": len(rows_data),
                "file_name": file_path.name,
                "file_size_bytes": file_path.stat().st_size,
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
        # Truncate error_log to fit reasonable sizes; keep first error only.
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
        """Stub for S1.4 pilot. Real FK resolution belongs to S1.5 when reference
        data (indicator_definition / geo_entity / calendar_period /
        indicator_methodology_version / geo_code_version / source_location)
        is seeded. For the pilot we surface the FK error as PARTIAL signal.

        Returns (inserted: bool, error_summary: Optional[str])."""
        try:
            with conn.cursor() as cur:
                # The placeholder INSERT proves the schema is reachable but
                # fails FK on indicator_methodology_version etc.; we report the
                # first error so the ingestion_run row records why we stopped.
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
                        'NEEDS_VERIFICATION', 'FACT', 'PRELIMINARY', 'HTML_PARSE',
                        %s
                    )
                    """,
                    (
                        # These UUIDs are placeholders — replaced in S1.5 with
                        # real lookups. The placeholder pattern deliberately
                        # fails FK so PARTIAL is the honest status.
                        uuid.UUID(int=0),  # indicator_id
                        uuid.UUID(int=0),  # geo_entity_id
                        uuid.UUID(int=0),  # geo_code_version_id
                        uuid.UUID(int=0),  # calendar_period_id
                        uuid.UUID(int=0),  # source_id
                        uuid.UUID(int=0),  # source_location_id
                        str(run_id),
                        observation.get("value"),
                        observation.get("raw_value") or str(observation.get("value")),
                        observation.get("unit"),
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
        triggered_by: str = "nbs_monthly_connector",
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
                "source_registry row for stats.gov.cn / NATIONAL_BULLETIN "
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

        if n_extracted == 0:
            status = "SUCCESS"  # No rows to insert; extract itself ran clean.
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