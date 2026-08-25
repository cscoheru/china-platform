"""Stage 1 / S1.7 — 扫描 PDF OCR 连接器（研究轨；非 Gate 1 代表性）.

Per docs/21-stage1-s17-scanned-pdf-ocr-plan-20260825.md + Cursor 56 §SCHEMA/语义裁定.

Reuses `spikes/04-scanned-pdf/extract_04_shaanxi_text.py` (Chinese-text research
track) and `spikes/04-scanned-pdf/extract_04_scanned_pdf.py` (1909 numeric-table
fallback — code branch retained per Cursor 56 §SCHEMA 决策 6, but **default
tests only run 陕西**).

Single-sample pilot. **No HTTP. No batch historical scanning.**

DB ingest flow (mirrors S1.4/S1.5/S1.6):
  1. Resolve source_registry row by
     (domain='wb.flk.npc.gov.cn', category='SCANNED_PDF_RESEARCH')
  2. INSERT ingestion_run (status='RUNNING')
  3. Compute file SHA-256; verify against spike 04 provenance.json;
     INSERT source_document (S0, VERIFIED — provenance-validated origin;
     extraction_method='PDF_OCR', already in schema/01-core.sql enum line 55)
  4. extract() → N observation dicts in memory (per-page granularity;
     4 obs for Shaanxi PDF)
  5. Attempt INSERT observations (FK placeholder UUIDs → PARTIAL/FAILED in pilot;
     when FK resolution lands, the connector populates observation.notes JSON +
     observation.caveat_text + observation.lineage JSONB extension keys)
  6. UPDATE ingestion_run final status + counts

Per Cursor 56 §SCHEMA 语义裁定 (硬约束):
  * Shaanxi obs granularity = **per-page** (1 obs per PDF page; raw_value =
    OCR text of that page)
  * observation.value_type = **'FACT'** (enum has no DEFINITION; 禁止 new
    migration 改 enum)
  * observation.value = NULL; missing_reason = 'NOT_NUMERIC_SOURCE'
  * observation.notes JSON = {"research_track": true, "not_statistical_table":
    true, "han_agreement_pending_evaluation": true, ...}
  * observation.period_* (start/end/label/type) = NULL (法规 != 数据周期)
  * observation.lineage JSONB = {chain_id, source_file_sha256, source_file_url,
    extractor_version: "spike04-shanxi/1.1", render_dpi, ocr_language, psm,
    embedded_text_layer_used: false}
  * **不做 migration 005** (extraction_metadata JSONB 列被否决; bbox/dpi 入
    lineage JSONB 扩展键)

Missing toolchain (tesseract / pdftoppm / pdfinfo / chi_sim) → **fail 透传**;
不 skip-as-PASS. Connector reuses `extract_04_shaanxi_text.require_tools()`
which raises RuntimeError, propagated to ingest() and surfaced in error_log +
status=FAILED.

1909 fallback (numeric-table track) — code branch retained (DEFAULT_TRACK
override);禁止宣布 1909 PASS; 禁止改 gate_thresholds.json.
"""
from __future__ import annotations

import json
import sys
import uuid
from pathlib import Path

import psycopg2
import psycopg2.errors

# Path shim so we can import spike 04 modules without copying
REPO_ROOT = Path(__file__).resolve().parents[4]
SPIKE_04_DIR = REPO_ROOT / "spikes" / "04-scanned-pdf"
if str(SPIKE_04_DIR) not in sys.path:
    sys.path.insert(0, str(SPIKE_04_DIR))

from extract_04_shaanxi_text import (  # noqa: E402  (sys.path manipulation above)
    DEFAULT_PDF as _spike_04_shaanxi_DEFAULT_PDF,
    DPI as _spike_04_shaanxi_DPI,
    LANGUAGE as _spike_04_shaanxi_LANG,
    PSM as _spike_04_shaanxi_PSM,
    PROVENANCE as _spike_04_PROVENANCE,
    SAMPLE_KEY as _spike_04_SAMPLE_KEY,
    extract as _spike_04_shaanxi_extract,
    sha256_file as _spike_04_shaanxi_sha256,
)
from extract_04_scanned_pdf import (  # noqa: E402
    DEFAULT_PDF as _spike_04_1909_DEFAULT_PDF,
)


class ScannedPdfOcrConnector:
    """Stage 1 / S1.7 — 扫描 PDF OCR 连接器（研究轨；非 Gate 1 代表性）."""

    DEFAULT_SAMPLE = _spike_04_shaanxi_DEFAULT_PDF  # 陕西研究轨 (U-1·U-2·U-3)
    DEFAULT_REGISTRY_DOMAIN = "wb.flk.npc.gov.cn"
    DEFAULT_REGISTRY_CATEGORY = "SCANNED_PDF_RESEARCH"
    DEFAULT_SAMPLE_TITLE = "陕西省财政预算管理条例"
    DEFAULT_SAMPLE_PUBLISHER = "陕西省人民代表大会常务委员会"
    DEFAULT_SAMPLE_URL = (
        "https://wb.flk.npc.gov.cn/dfxfg/PDF/d31411b562fc4226a7465f1c875afe67.pdf"
    )
    DEFAULT_TRACK = "shaanxi_chinese_text"  # per Cursor 56 §SCHEMA 决策 6
    DEFAULT_RENDER_DPI = _spike_04_shaanxi_DPI
    DEFAULT_OCR_LANGUAGE = _spike_04_shaanxi_LANG
    DEFAULT_PSM = _spike_04_shaanxi_PSM
    DEFAULT_EXTRACTOR_VERSION = "spike04-shanxi/1.1"
    # Page-level needs_review heuristic threshold (mirror spike 04 numeric-track
    # conf<60 rule). NOT a replacement for Han agreement evaluation (which
    # requires ground truth); flagged via notes.han_agreement_pending_evaluation.
    DEFAULT_NEEDS_REVIEW_CONFIDENCE_THRESHOLD = 60.0

    # ---- pure-file helpers ----

    def compute_sha256(self, file_path: Path) -> str:
        """SHA-256 hex digest of `file_path` bytes (uses spike 04 helper)."""
        if not file_path.exists():
            raise FileNotFoundError(f"Sample PDF missing: {file_path}")
        return _spike_04_shaanxi_sha256(file_path)

    def _verify_against_provenance(self, file_path: Path) -> dict:
        """Verify SHA-256 matches spike 04 provenance.json — local origin guard.

        Per spike 04 README: "PDF SHA-256: f34b2e57…71488" is the
        machine-readable source of truth. Connector refuses to ingest if the
        bytes don't match — protects against silent re-download / re-fetch.
        """
        if not _spike_04_PROVENANCE.exists():
            raise RuntimeError(
                f"provenance.json missing: {_spike_04_PROVENANCE}"
            )
        prov = json.loads(_spike_04_PROVENANCE.read_text(encoding="utf-8"))
        sample = prov["research_samples"][_spike_04_SAMPLE_KEY]
        actual = self.compute_sha256(file_path)
        if actual != sample["file_hash_sha256"]:
            raise RuntimeError(
                f"sha256 mismatch for {file_path.name}: "
                f"expected {sample['file_hash_sha256']}, got {actual}"
            )
        return prov

    def extract(self, file_path: Path) -> dict:
        """Parse scanned PDF; return dict with sha256 + observations + metadata.

        Pure file operation, no side effects on the DB. Branch by track:
          * "shaanxi_chinese_text" (DEFAULT) — call _spike_04_shaanxi_extract;
            one obs per page; period_* NULL; lineage JSONB has render_dpi + lang
            + psm + embedded_text_layer_used=false
          * "numeric_table_1909" (fallback, **not default-tested**) — call
            spike 04 numeric extractor; per-cell obs; period_* filled;
            禁止宣布 PASS (per Cursor 56 §SCHEMA 决策 6).

        Per Cursor 56 §SCHEMA:
          observation.value = NULL + missing_reason = 'NOT_NUMERIC_SOURCE'
          observation.value_type = 'FACT' (enum has no DEFINITION)
          observation.notes = JSON {research_track: true,
                                     not_statistical_table: true,
                                     han_agreement_pending_evaluation: true,
                                     mean_word_confidence: float|None,
                                     word_count: int,
                                     page_pdf_1indexed: int,
                                     needs_review: bool,
                                     needs_review_reason: str|None}
          observation.caveat_text = human-readable summary
        """
        if not file_path.exists():
            raise FileNotFoundError(f"Sample PDF missing: {file_path}")

        sha = self.compute_sha256(file_path)
        prov = self._verify_against_provenance(file_path)
        sample = prov["research_samples"][_spike_04_SAMPLE_KEY]

        if self.DEFAULT_TRACK == "shaanxi_chinese_text":
            # spike 04 raises RuntimeError if tesseract / pdftoppm / chi_sim
            # are absent — we let it propagate (no silent skip)
            ocr_out = _spike_04_shaanxi_extract(file_path)
            observations = []
            for page in ocr_out["pages"]:
                obs = self._build_shanxi_observation(
                    page=page,
                    sha=sha,
                    provenance=prov,
                    sample=sample,
                    extraction=ocr_out["extraction"],
                )
                observations.append(obs)
            return {
                "sha256": sha,
                "observations": observations,
                "lineage": {
                    "chain_id": f"shaanxi-flk-2026-{sha[:12]}",
                    "source_file_sha256": sha,
                    "source_file_url": sample["source_url"],
                    "extractor_version": self.DEFAULT_EXTRACTOR_VERSION,
                    "render_dpi": self.DEFAULT_RENDER_DPI,
                    "ocr_language": self.DEFAULT_OCR_LANGUAGE,
                    "ocr_psm": self.DEFAULT_PSM,
                    "embedded_text_layer_used": False,
                },
                "metadata": {
                    "source_url": sample["source_url"],
                    "track": "shaanxi_chinese_text",
                    "role": sample.get("role", ""),
                    "extraction_method": (
                        f"pdftoppm {self.DEFAULT_RENDER_DPI}dpi + "
                        f"tesseract {self.DEFAULT_OCR_LANGUAGE} psm{self.DEFAULT_PSM} "
                        "+ layout-aware two-column (spike 04 v1.1)"
                    ),
                    "file_name": file_path.name,
                    "file_size_bytes": file_path.stat().st_size,
                    "pdf_pages_total": sample["pdf_pages_total"],
                    "page_observations": len(observations),
                    "extraction_metadata": ocr_out["extraction"],
                },
            }
        # 1909 fallback (code path retained but **not** default-tested per
        # Cursor 56 §SCHEMA 决策 6)
        raise NotImplementedError(
            "1909 numeric-table track is fallback-only per Cursor 56 §SCHEMA "
            "决策 6; default tests only run 陕西. Implement only if future "
            "tasking explicitly approves 1909 PASS — 禁止改 gate_thresholds.json."
        )

    def _build_shanxi_observation(
        self,
        page: dict,
        sha: str,
        provenance: dict,
        sample: dict,
        extraction: dict,
    ) -> dict:
        """Build one per-page observation dict for Shaanxi track.

        Per Cursor 56 §SCHEMA 语义裁定: per-page granularity, value_type='FACT',
        value=NULL + missing_reason='NOT_NUMERIC_SOURCE', period_* NULL,
        lineage JSONB extension keys for render_dpi + lang + psm +
        embedded_text_layer_used.
        """
        page_idx = page["page_pdf_1indexed"]
        word_count = page.get("word_count", 0)
        mean_conf = page.get("mean_word_confidence")
        needs_review = (
            mean_conf is not None
            and mean_conf < self.DEFAULT_NEEDS_REVIEW_CONFIDENCE_THRESHOLD
        )

        # Concatenate left/right region canonical_lines as raw_value (page text)
        raw_text_parts: list[str] = []
        for region in page.get("regions", []):
            region_lines = region.get("canonical_lines", [])
            if region_lines:
                raw_text_parts.append(
                    f"[{region['name']}]\n" + "\n".join(region_lines)
                )
        raw_value_text = "\n\n".join(raw_text_parts)

        # notes JSON — explicit per Cursor 56 §SCHEMA 决策 3
        notes_payload = {
            "research_track": True,
            "not_statistical_table": True,
            "han_agreement_pending_evaluation": True,
            "page_pdf_1indexed": page_idx,
            "word_count": word_count,
            "mean_word_confidence": mean_conf,
            "needs_review": needs_review,
            "needs_review_reason": (
                "low_mean_word_confidence" if needs_review else None
            ),
            "render_dpi": extraction.get("render_dpi"),
            "ocr_language": extraction.get("tesseract_language"),
            "ocr_psm": extraction.get("page_segmentation_mode"),
            "embedded_text_layer_used": extraction.get(
                "embedded_text_layer_used", False
            ),
            "layout": page.get("layout", {}),
        }
        notes_json = json.dumps(
            notes_payload, ensure_ascii=False, sort_keys=True
        )

        # caveat_text — human-readable
        caveat_parts = [
            "Shaanxi research track; NOT a statistical-table representative "
            "sample (per Cursor 56 §SCHEMA 决策 6 + spike 04 README 红线 8)",
            f"page={page_idx}",
            f"word_count={word_count}",
            f"mean_word_confidence={mean_conf}",
            "han_agreement_pending_evaluation=true",
        ]
        caveat_text = "; ".join(caveat_parts)

        return {
            "page_pdf_1indexed": page_idx,
            "value": None,
            "raw_value": raw_value_text,
            "unit": None,
            "comparison_basis": "NEEDS_VERIFICATION",
            "value_type": "FACT",  # enum has no DEFINITION (Cursor 55 §1 备注)
            "missing_reason": "NOT_NUMERIC_SOURCE",
            "confidence": (
                round(mean_conf / 100.0, 3) if mean_conf is not None else None
            ),
            "period_start": None,
            "period_end": None,
            "period_label": None,
            "period_type": None,
            "notes": notes_json,
            "caveat_text": caveat_text,
            "lineage": {
                "chain_id": f"shaanxi-flk-2026-page{page_idx}-{sha[:12]}",
                "source_file_sha256": sha,
                "source_file_url": sample["source_url"],
                "extractor_version": self.DEFAULT_EXTRACTOR_VERSION,
                "render_dpi": extraction.get("render_dpi"),
                "ocr_language": extraction.get("tesseract_language"),
                "ocr_psm": extraction.get("page_segmentation_mode"),
                "embedded_text_layer_used": False,
                "page_pdf_1indexed": page_idx,
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
        # extraction_method='PDF_OCR' (already in schema/01-core.sql enum line 55;
        # Cursor 49 §1 备注)
        with conn.cursor() as cur:
            cur.execute(
                """
                INSERT INTO cegr.source_document
                    (source_registry_id, source_level, verification_status,
                     title, publisher, url, file_hash_sha256, file_size_bytes,
                     language, extraction_method)
                VALUES (%s, 'S0', 'VERIFIED',
                        %s, %s, %s, %s, %s,
                        'zh', 'PDF_OCR')
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
        """Insert one observation. FK placeholder UUIDs → PARTIAL/FAILED in pilot.

        Per Cursor 56 §SCHEMA: missing_reason='NOT_NUMERIC_SOURCE' is REQUIRED
        when value IS NULL (per observation_missing_consistency CHECK on
        schema/01-core.sql line 488–491). lineage::jsonb + caveat_text +
        notes populate migration-004 columns.
        """
        try:
            with conn.cursor() as cur:
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
                         lineage, caveat_text, missing_reason, notes)
                    VALUES (
                        %s, %s, %s, %s, %s, %s, %s,
                        %s, %s, %s,
                        %s, %s, 'PRELIMINARY', 'PDF_OCR',
                        %s,
                        %s, %s, %s, %s,
                        %s::jsonb, %s, %s, %s
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
                        observation.get("value"),  # NULL for Shaanxi
                        observation.get("raw_value"),  # page OCR text
                        observation.get("unit"),  # NULL for Shaanxi
                        observation.get("comparison_basis") or "NEEDS_VERIFICATION",
                        observation.get("value_type") or "FACT",
                        observation.get("confidence"),
                        # Migration-004 period_* — all NULL for Shaanxi
                        observation.get("period_start") or None,
                        observation.get("period_end") or None,
                        observation.get("period_label") or None,
                        observation.get("period_type") or None,
                        lineage_sql,
                        observation.get("caveat_text") or None,
                        observation.get("missing_reason") or None,
                        observation.get("notes") or None,
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
        triggered_by: str = "scanned_pdf_ocr_connector",
        title: str | None = None,
        publisher: str | None = None,
        url: str | None = None,
    ) -> dict:
        """End-to-end ingest: extract → ingestion_run → source_document →
        observations (best-effort) → ingestion_run final status.

        Returns a summary dict (suitable for assertions in tests).

        缺 tesseract / pdftoppm / chi_sim → fail 透传（per Cursor 56 §NOW step 3）;
        status=FAILED + error_log 含具体缺失工具名.
        """
        title = title or self.DEFAULT_SAMPLE_TITLE
        publisher = publisher or self.DEFAULT_SAMPLE_PUBLISHER
        url = url or self.DEFAULT_SAMPLE_URL

        sr_id = self._resolve_source_registry(conn)
        if sr_id is None:
            raise RuntimeError(
                "source_registry row for wb.flk.npc.gov.cn / SCANNED_PDF_RESEARCH "
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
        except RuntimeError as exc:
            # spike 04 raises RuntimeError for missing tesseract / chi_sim /
            # pdftoppm / sha256 mismatch — fail 透传 per Cursor 56 §NOW step 3
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

        # Status semantics (mirror S1.4/S1.5/S1.6):
        if n_extracted == 0:
            status = "SUCCESS"  # extract ran clean (rare for OCR)
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