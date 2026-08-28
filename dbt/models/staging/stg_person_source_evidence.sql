{{
    config(
        materialized='view',
        tags=['staging', 'person']
    )
}}

-- Staging model for person_source_evidence (S2.1-full, per docs/36 §2.6).
-- 每条 person 至少 1 条 evidence（无源 = 不入 mart）。

SELECT
    e.id                        AS evidence_id,
    e.person_id,
    e.source_id,
    e.claim,
    e.excerpt,
    e.evidence_type,
    e.source_location_id,
    e.created_at
FROM {{ source('cegr', 'person_source_evidence') }} e
