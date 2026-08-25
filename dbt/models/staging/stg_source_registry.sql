{{
    config(
        materialized='view',
        tags=['staging', 'source_registry']
    )
}}

-- Staging model for source_registry.
-- Renames id → source_id (alignment with observation.source_id).
-- Filters to enabled sources only.

SELECT
    id                          AS source_id,
    domain,
    organization,
    category,
    primary_url,
    access_method,
    source_level,
    declared_source_level,
    update_frequency,
    enabled,
    file_hash_sha256,
    created_at,
    updated_at
FROM {{ source('cegr', 'source_registry') }}
WHERE enabled = TRUE