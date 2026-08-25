{{
    config(
        materialized='view',
        tags=['staging', 'ingestion_run']
    )
}}

-- Staging model for ingestion_run.
-- Calculates duration_seconds, insertion_pct, and is_stale flag.
-- Joins source_registry for domain/category metadata.

SELECT
    ir.id                       AS run_id,
    ir.source_registry_id       AS source_id,
    sr.domain,
    sr.category,
    ir.status,
    ir.started_at,
    ir.finished_at,
    CASE
        WHEN ir.finished_at IS NOT NULL
        THEN EXTRACT(EPOCH FROM (ir.finished_at - ir.started_at))
        ELSE NULL
    END                         AS duration_seconds,
    ir.records_extracted,
    ir.records_inserted,
    ir.records_updated,
    CASE
        WHEN ir.records_extracted > 0
        THEN ROUND((ir.records_inserted::numeric / ir.records_extracted) * 100, 1)
        ELSE NULL
    END                         AS insertion_pct,
    ir.error_log,
    ir.triggered_by,
    CASE
        WHEN ir.status = 'RUNNING'
             AND ir.finished_at IS NULL
             AND ir.started_at < NOW() - INTERVAL '6 hours'
        THEN TRUE
        ELSE FALSE
    END                         AS is_stale
FROM {{ source('cegr', 'ingestion_run') }} ir
JOIN {{ source('cegr', 'source_registry') }} sr
    ON ir.source_registry_id = sr.id