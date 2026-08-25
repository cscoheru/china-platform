{{
    config(
        materialized='view',
        tags=['intermediate', 'coverage']
    )
}}

-- Intermediate model: source-level coverage and quality aggregation.
-- Aggregates ingestion_run + observation_quality per source.
-- Used by S1.11 Great Expectations for data contracts baseline.

SELECT
    sr.source_id,
    sr.domain,
    sr.category,
    sr.source_level,
    sr.enabled,
    -- Ingestion run statistics
    COUNT(DISTINCT ir.run_id)   AS total_runs,
    COUNT(DISTINCT ir.run_id) FILTER (WHERE ir.status = 'SUCCESS')
                                AS success_runs,
    COUNT(DISTINCT ir.run_id) FILTER (WHERE ir.status IN ('PARTIAL', 'FAILED'))
                                AS failure_runs,
    CASE
        WHEN COUNT(DISTINCT ir.run_id) > 0
        THEN ROUND(
            COUNT(DISTINCT ir.run_id) FILTER (WHERE ir.status IN ('PARTIAL', 'FAILED'))::numeric
            / COUNT(DISTINCT ir.run_id),
            3
        )
        ELSE 0.0
    END                         AS failure_rate,
    SUM(ir.records_extracted)   AS total_extracted,
    SUM(ir.records_inserted)    AS total_inserted,
    CASE
        WHEN SUM(ir.records_extracted) > 0
        THEN ROUND(
            (SUM(ir.records_inserted)::numeric / SUM(ir.records_extracted)) * 100,
            1
        )
        ELSE NULL
    END                         AS overall_insertion_pct,
    -- Quality statistics (from subquery)
    oq.avg_quality_score,
    oq.low_confidence_count,
    oq.missing_with_reason_count,
    oq.total_observations,
    -- Freshness
    MAX(ir.started_at)          AS last_run_at
FROM {{ ref('stg_source_registry') }} sr
LEFT JOIN {{ ref('stg_ingestion_run') }} ir
    ON sr.source_id = ir.source_id
LEFT JOIN (
    SELECT
        source_id,
        AVG(quality_score)                              AS avg_quality_score,
        COUNT(*) FILTER (WHERE is_low_confidence)       AS low_confidence_count,
        COUNT(*) FILTER (WHERE is_missing_with_reason)   AS missing_with_reason_count,
        COUNT(*)                                        AS total_observations
    FROM {{ ref('stg_observation_quality') }}
    GROUP BY source_id
) oq ON sr.source_id = oq.source_id
GROUP BY
    sr.source_id,
    sr.domain,
    sr.category,
    sr.source_level,
    sr.enabled,
    oq.avg_quality_score,
    oq.low_confidence_count,
    oq.missing_with_reason_count,
    oq.total_observations