{{
    config(
        materialized='view',
        tags=['intermediate', 'timeseries']
    )
}}

-- Intermediate model: indicator × geo × period time series.
-- Joins stg_observation with stg_source_document for provenance metadata.
-- Excludes NULL values (missing rows handled separately via stg_observation_quality).
-- Used by S1.10 FastAPI to answer Gate 1 research questions.

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
    o.extracted_at
FROM {{ ref('stg_observation') }} o
JOIN {{ ref('stg_source_document') }} sd
    ON o.source_id = sd.document_id
WHERE o.value IS NOT NULL