{{
    config(
        materialized='view',
        tags=['staging', 'person']
    )
}}

-- Staging model for tenure (S2.1-full, per docs/36 §2.4).
-- Overlapping tenures are LEGAL (no EXCLUDE constraint, per docs/36 §2.4
-- + migration 008 header) — dedup/merge is downstream policy, not here.

SELECT
    t.id                        AS tenure_id,
    t.person_id,
    t.position_id,
    t.geo_entity_id,
    t.start_date,
    t.end_date,
    t.is_current,
    t.appointment_event_id,
    t.departure_event_id,
    t.departure_reason,
    t.source_id,
    t.created_at
FROM {{ source('cegr', 'tenure') }} t
