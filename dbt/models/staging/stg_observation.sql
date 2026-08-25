{{
    config(
        materialized='view',
        tags=['staging', 'observation']
    )
}}

-- Staging model for observation.
-- Filters to value_type = 'FACT' only.
-- DERIVED / INFERENCE / JUDGMENT left for intermediate layer (S1.10+).
-- Period columns from migration 004 are passed through.

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
FROM {{ source('cegr', 'observation') }} o
WHERE o.value_type = 'FACT'