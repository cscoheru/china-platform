{{
    config(
        materialized='view',
        tags=['staging', 'observation', 'quality']
    )
}}

-- Staging model for observation quality scoring.
-- Computes 5-factor quality_score (0-1):
--   value non-null       : 0.3
--   confidence >= 0.8    : 0.2  (0.1 if >= 0.5)
--   lineage JSONB present: 0.2
--   source_id not null   : 0.2
--   extraction_method    : 0.1

SELECT
    o.id                        AS observation_id,
    o.source_id,
    o.ingestion_run_id,
    o.value,
    o.missing_reason,
    o.confidence,
    o.extraction_method,
    o.value_type,
    -- Quality flag columns
    CASE
        WHEN o.value IS NULL AND o.missing_reason IS NOT NULL
        THEN TRUE
        ELSE FALSE
    END                         AS is_missing_with_reason,
    CASE
        WHEN o.confidence IS NOT NULL AND o.confidence < 0.5
        THEN TRUE
        ELSE FALSE
    END                         AS is_low_confidence,
    CASE
        WHEN o.is_imputed = TRUE
        THEN TRUE
        ELSE FALSE
    END                         AS is_imputed_flag,
    CASE
        WHEN o.lineage IS NOT NULL
             AND o.lineage ? 'source_file_sha256'
        THEN TRUE
        ELSE FALSE
    END                         AS has_provenance,
    CASE
        WHEN o.caveat_text IS NOT NULL AND o.caveat_text != ''
        THEN TRUE
        ELSE FALSE
    END                         AS has_caveat,
    -- Composite quality score (0-1)
    ROUND(
        (CASE WHEN o.value IS NOT NULL THEN 0.3 ELSE 0 END
         + CASE WHEN o.confidence >= 0.8 THEN 0.2
                WHEN o.confidence >= 0.5 THEN 0.1
                ELSE 0 END
         + CASE WHEN o.lineage IS NOT NULL THEN 0.2 ELSE 0 END
         + CASE WHEN o.source_id IS NOT NULL THEN 0.2 ELSE 0 END
         + CASE WHEN o.extraction_method IS NOT NULL THEN 0.1 ELSE 0 END
        )::numeric, 2
    )                           AS quality_score
FROM {{ source('cegr', 'observation') }} o