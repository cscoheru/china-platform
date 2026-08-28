{{
    config(
        materialized='view',
        tags=['mart', 'person_tenure']
    )
}}

-- Mart model for person tenure (S2.1-full; docs/36 §3 + tasking 577 §D).
-- Grain: one row per tenure. JOIN person + position; LEFT JOIN geo_entity
-- and appointment_event.
--
-- is_demo derivation: the tenure table has no row-level JSONB lineage
-- column (01-core) and migrations 001-013 are frozen per tasking 577 red
-- lines, so the demo flag is derived from the tenure's source_document
-- markers (caveat_text LIKE '%DEMO_SEED%' OR url sentinel) — the same
-- rule scripts/seed_person_tenure_demo.py --status applies. Per docs/33
-- §3.2 the value is the 'true'/'false' string sentinel; per docs/36 §3 it
-- is exposed explicitly as the LAST column so downstream consumers can
-- filter (WHERE is_demo != 'true').

SELECT
    t.tenure_id,
    t.person_id,
    p.canonical_name,
    p.canonical_name_pinyin,
    p.gender,
    t.position_id,
    pos.title                       AS position_title,
    pos.canonical_title,
    pos.title_en,
    pos.level                       AS position_level,
    pos.is_standing_committee,
    t.geo_entity_id,
    g.canonical_name                AS geo_name,
    t.start_date,
    t.end_date,
    t.is_current,
    t.departure_reason,
    ae.event_id                     AS appointment_event_id,
    ae.event_type,
    ae.event_date,
    t.source_id,
    CASE
        WHEN sd.caveat_text LIKE '%DEMO_SEED%'
            OR sd.url = '(DEMO_SEED_NO_FILE)'
        THEN 'true'
        ELSE 'false'
    END                             AS is_demo
FROM {{ ref('stg_tenure') }} t
JOIN {{ ref('stg_person') }} p          ON p.person_id = t.person_id
JOIN {{ ref('stg_position') }} pos      ON pos.position_id = t.position_id
LEFT JOIN {{ source('cegr', 'geo_entity') }} g
                                        ON g.id = t.geo_entity_id
LEFT JOIN {{ ref('stg_appointment_event') }} ae
                                        ON ae.event_id = t.appointment_event_id
LEFT JOIN {{ source('cegr', 'source_document') }} sd
                                        ON sd.id = t.source_id
