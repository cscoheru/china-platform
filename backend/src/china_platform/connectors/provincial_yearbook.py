"""Stage 1 / S1.6 — 湖北省级统计年鉴 xlsx 连接器.

Per docs/20-stage1-s16-provincial-yearbook-plan-20260824.md.

Reuses `spikes/02-provincial-yearbook/extract_02_provincial_yearbook.py` for
per-indicator period metadata (B-06), canonical indicator mapping (no Chinese
in DB), and per-row lineage chain (R3-E). Same source of truth used by Stage 0
spike tests.

Single-sample pilot: reads `spikes/02-provincial-yearbook/hubei_2026_06.xlsx`
by default. **No HTTP.** Production multi-period (2020-2025) ingestion is out
of scope for S1.6.

DB ingest flow:
  1. Resolve source_registry row by
     (domain='tjj.hubei.gov.cn', category='PROVINCIAL_YEARBOOK')
  2. INSERT ingestion_run (status='RUNNING')
  3. Compute file SHA-256; INSERT source_document (S0, VERIFIED — pre-existing
     spike sample; avoids I-05 §9.1 source_level_s0_requires_verified CHECK)
  4. extract() → N observation dicts in memory (21 data rows for hubei_2026_06)
  5. Attempt INSERT observations (FK resolution is deferred to S1.7+ — same as
     S1.4/S1.5; expected to fail FK, status falls to PARTIAL/FAILED).
     When FK resolution lands, the connector writes the new migration-004
     columns (period_start/end/label/type, lineage JSONB, caveat_text).
  6. UPDATE ingestion_run with final status + counts

Exit / status semantics (mirrors S1.4/S1.5):
  SUCCESS — source_document persisted; extract succeeded; ≥1 row written
  PARTIAL — source_document persisted; some obs FK failed
  FAILED  — extract failed OR source_document INSERT failed
  Special: 0 obs is treated as SUCCESS per docs/19 §5 (spike 02 returns 21
  rows for the sample, but the connector doesn't crash on empty extract).

Per-indicator period metadata (B-06) — stored via migration 004 columns:
  * observation.period_start  / period_end    — DATE
  * observation.period_label                 — TEXT (Chinese source label)
  * observation.period_type                  — TEXT
    (CUMULATIVE_HALF_YEAR / CUMULATIVE_5MONTH / PERIOD_END_OF_MONTH / INDEX_YOY;
     **NOT** collapsed to a single value — connector reads from
     spike 02 PERIOD_METADATA_MAP)
  * observation.lineage (JSONB) — {chain_id, source_file_sha256,
    source_file_url, extractor_version}
  * observation.caveat_text (TEXT) — per-row caveat for indicators awaiting
    authoritative methodology verification (e.g. GDP 季度数被标为半年累计).

Red lines (docs/20 §6):
  * ❌ 不漂移 CUMULATIVE_HALF_YEAR — period_type stays TEXT; per-indicator
  * ❌ 中文 indicator_zh 不进 DB — only period_label and caveat_text carry
    Chinese; indicator_canonical is snake-case English
  * ❌ 不在 fixture 临时建表 — migration 004 owns schema
"""
from __future__ import annotations

import json
import sys
import uuid
from pathlib import Path

import openpyxl
import psycopg2
import psycopg2.errors

# Path shim so we can import the spike module without copying the parser
REPO_ROOT = Path(__file__).resolve().parents[4]
SPIKE_02_DIR = REPO_ROOT / "spikes" / "02-provincial-yearbook"
if str(SPIKE_02_DIR) not in sys.path:
    sys.path.insert(0, str(SPIKE_02_DIR))

from extract_02_provincial_yearbook import (  # noqa: E402  (sys.path manipulation above)
    COMPARISON_BASIS_MAP,
    INDICATOR_CANONICAL_MAP,
    PERIOD_METADATA_MAP,
    PROVINCE_CODE_GB2260,
    PROVINCE_ZH,
    SOURCE_AGENCY,
    SOURCE_URL,
    build_lineage_chain,
    compute_sha256 as _spike_compute_sha256,
    derive_period_metadata,
    extract_rows as _spike_extract_rows,
)


class ProvincialYearbookConnector:
    """Stage 1 / S1.6 — 湖北省级统计年鉴 xlsx 连接器."""

    DEFAULT_SAMPLE = SPIKE_02_DIR / "hubei_2026_06.xlsx"
    DEFAULT_REGISTRY_DOMAIN = "tjj.hubei.gov.cn"
    # Category must match the registry row in source_registry/registry.csv
    # (per Cursor 50 §NOW + registry CSV inspection). The connector class is
    # named "ProvincialYearbookConnector" for its technical role (xlsx yearbook
    # parsing); the administrative category is PROVINCIAL_BULLETIN.
    DEFAULT_REGISTRY_CATEGORY = "PROVINCIAL_BULLETIN"
    DEFAULT_SAMPLE_TITLE = (
        "湖北省2026年1-6月主要经济指标"
    )
    DEFAULT_SAMPLE_PUBLISHER = SOURCE_AGENCY
    DEFAULT_SAMPLE_URL = SOURCE_URL
    DEFAULT_PROVINCE_ZH = PROVINCE_ZH
    DEFAULT_PROVINCE_CODE_GB2260 = PROVINCE_CODE_GB2260
    DEFAULT_EXTRACTOR_VERSION = "2.0"

    # ---- pure-file helpers ----

    def compute_sha256(self, file_path: Path) -> str:
        """SHA-256 hex digest of `file_path` bytes."""
        if not file_path.exists():
            raise FileNotFoundError(f"Sample xlsx missing: {file_path}")
        return _spike_compute_sha256(file_path)

    def extract(self, file_path: Path) -> dict:
        """Parse xlsx; return dict with sha256 + observations + metadata.

        Pure file operation, no side effects on the DB.

        The returned `observations` list contains one dict per data row from
        spike 02's `extract_rows()`; each dict carries B-06 period metadata
        (period_start/end/label/type) and `lineage` (chain_id +
        source_file_sha256 + source_file_url + extractor_version) — these are
        what gets written to migration-004 columns when FK resolution lands.

        `indicator_zh` is preserved per row for evidence_pack traceability but
        is NEVER written to observation.* columns; only period_label and
        caveat_text may carry Chinese (they mirror source-sheet strings).
        """
        if not file_path.exists():
            raise FileNotFoundError(f"Sample xlsx missing: {file_path}")

        sha = _spike_compute_sha256(file_path)
        wb = openpyxl.load_workbook(file_path, data_only=True)
        ws = wb.active

        # Title row (row 1)
        title = None
        for cell in ws.iter_rows(min_row=1, max_row=1, values_only=True):
            title = cell[0]

        # Column headers (row 2)
        col_headers: list[str] = []
        for cell in ws.iter_rows(min_row=2, max_row=2, values_only=True):
            col_headers = [str(c).strip() if c else "" for c in cell]

        # Data rows (row 3+) — spike 02 extract_rows returns (rows, footnotes)
        rows, footnotes = _spike_extract_rows(ws)

        # Inject lineage into each row (B-06 + R3-E)
        lineage = build_lineage_chain(sha)
        per_row_lineage = {
            "chain_id": lineage["chain_id"],
            "source_file_sha256": sha,
            "source_file_url": SOURCE_URL,
            "extractor_version": lineage["extractor_version"],
        }
        for r in rows:
            r["lineage"] = per_row_lineage

        return {
            "sha256": sha,
            "observations": rows,
            "lineage": lineage,
            "metadata": {
                "source_url": SOURCE_URL,
                "province_zh": PROVINCE_ZH,
                "province_code_gb2260": PROVINCE_CODE_GB2260,
                "table_title": str(title).strip() if title else "",
                "column_headers": col_headers,
                "footnote_text": footnotes,
                "extraction_method": (
                    "openpyxl (data_only=True) + spike 02 lineage v2.0"
                ),
                "extractor_version": lineage["extractor_version"],
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
        # extraction_method='EXCEL_PARSE' — already in schema/01-core.sql enum
        # (per Cursor 49 §1 备注). No schema change required.
        with conn.cursor() as cur:
            cur.execute(
                """
                INSERT INTO cegr.source_document
                    (source_registry_id, source_level, verification_status,
                     title, publisher, url, file_hash_sha256, file_size_bytes,
                     language, extraction_method)
                VALUES (%s, 'S0', 'VERIFIED',
                        %s, %s, %s, %s, %s,
                        'zh', 'EXCEL_PARSE')
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
        """Stub for S1.6 pilot. Real FK resolution belongs to S1.7+ when
        reference data (indicator_definition / geo_entity / calendar_period /
        indicator_methodology_version / geo_code_version / source_location)
        is seeded. Mirrors S1.4/S1.5 pattern.

        When FK is satisfied, this INSERT would also populate migration-004
        columns: period_start/end/label/type, lineage JSONB, caveat_text.
        For the pilot, those columns are left NULL because the INSERT itself
        fails FK; the dict values still carry the canonical metadata for
        downstream verification (asserted by tests on `extract()` output).
        """
        try:
            with conn.cursor() as cur:
                # Build a defensive JSON string for the lineage JSONB. If the
                # observation doesn't carry a lineage dict, emit '{}' so the
                # column gets an empty JSON object (still valid JSONB).
                lineage = observation.get("lineage") or {}
                lineage_sql = json.dumps(lineage, ensure_ascii=False, sort_keys=True)

                cur.execute(
                    """
                    INSERT INTO cegr.observation
                        (indicator_id, geo_entity_id, geo_code_version_id,
                         calendar_period_id, source_id, source_location_id,
                         ingestion_run_id, value, raw_value, unit,
                         comparison_basis, value_type, status, extraction_method,
                         confidence,
                         period_start, period_end, period_label, period_type,
                         lineage, caveat_text)
                    VALUES (
                        %s, %s, %s, %s, %s, %s, %s,
                        %s, %s, %s,
                        %s, 'FACT', 'PRELIMINARY', 'EXCEL_PARSE',
                        %s,
                        %s, %s, %s, %s,
                        %s::jsonb, %s
                    )
                    """,
                    (
                        # Placeholder UUIDs — replaced with real lookups when
                        # S1.7+ seeds reference data. Deliberately fail FK so
                        # PARTIAL/FAILED is the honest status in the pilot.
                        uuid.UUID(int=0),  # indicator_id
                        uuid.UUID(int=0),  # geo_entity_id
                        uuid.UUID(int=0),  # geo_code_version_id
                        uuid.UUID(int=0),  # calendar_period_id
                        uuid.UUID(int=0),  # source_id
                        uuid.UUID(int=0),  # source_location_id
                        str(run_id),
                        observation.get("value"),
                        str(observation.get("value"))
                        if observation.get("value") is not None else None,
                        observation.get("unit") or None,
                        observation.get("comparison_basis") or "NEEDS_VERIFICATION",
                        # confidence: spike 02 doesn't compute confidence yet;
                        # NULL is allowed (no observation_confidence_range fail).
                        None,
                        # Migration-004 columns:
                        observation.get("period_start") or None,
                        observation.get("period_end") or None,
                        observation.get("period_label") or None,
                        observation.get("period_type") or None,
                        lineage_sql,
                        observation.get("caveat") or None,
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
        triggered_by: str = "provincial_yearbook_connector",
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
                "source_registry row for tjj.hubei.gov.cn / PROVINCIAL_YEARBOOK "
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

        # Status semantics — mirror S1.4/S1.5:
        #   0 obs        → SUCCESS (legitimate empty extract)
        #   all inserted → SUCCESS
        #   none inserted→ FAILED
        #   partial      → PARTIAL
        if n_extracted == 0:
            status = "SUCCESS"
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