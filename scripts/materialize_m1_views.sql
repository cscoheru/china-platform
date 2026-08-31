-- M1 T4 — Materialize cegr_staging views from dbt model definitions.
--
-- Per docs/55 §T4 (knife 629 §2 T4) + dbt/models/staging/stg_observation.sql
-- + dbt/models/staging/stg_source_document.sql
-- + dbt/models/intermediate/int_indicator_timeseries.sql.
--
-- Approach B (knife 629 §2 T4 fallback): create the views directly via
-- plain SQL when dbt run is unavailable. The view bodies are kept
-- **identical in semantics** to the dbt Jinja originals (only the Jinja
-- refs {{ source(...) }} / {{ ref(...) }} are resolved to literal
-- `schema.table` references; no column or WHERE-clause drift).
--
-- Run via:
--   PGPASSWORD=postgres psql -h 127.0.0.1 -p 55440 -U postgres -d cegr_test \
--       -v ON_ERROR_STOP=1 -f scripts/materialize_m1_views.sql
--
-- Idempotent: DROP+CREATE handles column-list changes (CREATE OR REPLACE
-- preserves original column names when the SELECT list differs).

DROP VIEW IF EXISTS cegr_staging.int_indicator_timeseries;
DROP VIEW IF EXISTS cegr_staging.stg_observation;
DROP VIEW IF EXISTS cegr_staging.stg_source_document;

SET search_path = cegr, cegr_staging, public;

-- ---------------------------------------------------------------------
-- 1. cegr_staging.stg_observation (mirrors dbt/models/staging/stg_observation.sql)
-- ---------------------------------------------------------------------

CREATE VIEW cegr_staging.stg_observation AS
SELECT
    o.id                        AS observation_id,
    o.indicator_id,
    o.geo_entity_id,
    o.calendar_period_id,
    o.value,
    o.raw_value,
    o.unit,
    o.is_imputed,
    o.missing_reason,
    o.value_type,
    o.status,
    o.comparison_basis,
    o.source_id,
    o.ingestion_run_id,
    o.extraction_method,
    o.confidence,
    -- Migration 004 period columns
    o.period_start,
    o.period_end,
    o.period_label,
    o.period_type,
    o.lineage,
    o.caveat_text,
    -- Period alignment (simplified for this round; expansion in S1.10+)
    o.period_start              AS effective_period_start,
    o.extracted_at
FROM cegr.observation o
WHERE o.value_type = 'FACT';

-- ---------------------------------------------------------------------
-- 2. cegr_staging.stg_source_document (mirrors dbt/models/staging/stg_source_document.sql)
-- ---------------------------------------------------------------------

CREATE VIEW cegr_staging.stg_source_document AS
SELECT
    sd.id                       AS document_id,
    sd.source_registry_id       AS source_id,
    sr.domain,
    sr.category,
    sd.source_level,
    sd.declared_source_level,
    sd.verification_status,
    sd.title,
    sd.publisher,
    sd.publication_date,
    sd.url,
    sd.file_path,
    sd.file_hash_sha256,
    sd.file_format,
    sd.file_size_bytes,
    sd.language,
    sd.extraction_method,
    sd.caveat_text,
    sd.created_at
FROM cegr.source_document sd
JOIN cegr.source_registry sr
    ON sd.source_registry_id = sr.id;

-- ---------------------------------------------------------------------
-- 3. cegr_staging.int_indicator_timeseries (mirrors dbt/models/intermediate/int_indicator_timeseries.sql)
-- ---------------------------------------------------------------------

CREATE VIEW cegr_staging.int_indicator_timeseries AS
SELECT
    o.indicator_id,
    o.geo_entity_id,
    o.period_start,
    o.period_end,
    o.period_type,
    o.value,
    o.unit,
    o.status,
    o.comparison_basis,
    sd.domain                   AS source_domain,
    sd.category                 AS source_category,
    sd.source_level,
    sd.verification_status,
    o.extraction_method,
    o.confidence,
    o.caveat_text,
    LEFT(sd.file_hash_sha256, 8) AS source_hash_prefix,
    o.extracted_at
FROM cegr_staging.stg_observation o
JOIN cegr_staging.stg_source_document sd
    ON o.source_id = sd.document_id
WHERE o.value IS NOT NULL;

RESET search_path;
