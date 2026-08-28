{{
    config(
        materialized='view',
        tags=['staging', 'person']
    )
}}

-- Staging model for person_name_alias (S2.1-full, per docs/36 §2.2).
-- 同名异人通过 alias 关联（不直接合并）；歧义未消前不入 mart 层.

SELECT
    a.id                        AS alias_id,
    a.person_id,
    a.alias,
    a.alias_type,
    a.valid_from,
    a.valid_to
FROM {{ source('cegr', 'person_name_alias') }} a
