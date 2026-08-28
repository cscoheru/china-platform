{{
    config(
        materialized='view',
        tags=['staging', 'person']
    )
}}

-- Staging model for person (S2.1-full, per docs/36 §2.1).
-- 1:1 passthrough + id → person_id rename (per S1.19 staging convention).

SELECT
    p.id                        AS person_id,
    p.canonical_name,
    p.canonical_name_pinyin,
    p.gender,
    p.birth_year,
    p.ethnicity,
    p.education_summary,
    p.notes,
    p.created_at
FROM {{ source('cegr', 'person') }} p
