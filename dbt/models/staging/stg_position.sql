{{
    config(
        materialized='view',
        tags=['staging', 'person']
    )
}}

-- Staging model for position (S2.1-full, per docs/36 §2.3).
-- rank_level is an enum-style filter dimension (docs/36 §2.3) — NOT a
-- capability metric; score-family tokens are banned at the mart layer.

SELECT
    pos.id                      AS position_id,
    pos.title,
    pos.canonical_title,
    pos.title_en,
    pos.rank_level,
    pos.is_standing_committee,
    pos.level,
    pos.geo_entity_id,
    pos.parent_position_id,
    pos.is_key,
    pos.notes
FROM {{ source('cegr', 'position') }} pos
