{{
    config(
        materialized='view',
        tags=['staging', 'source_document']
    )
}}

-- Staging model for source_document.
-- Joins source_registry for domain/category metadata.
-- Preserves immutability semantics: all fields except caveat_text are
-- set once at insert time.

SELECT
    sd.id                       AS document_id,
    sd.source_registry_id       AS source_id,
    sr.domain,
    sr.category,
    sd.source_level,
    sd.declared_source_level,
    sd.verification_status,
    sd.title,
    sd.publisher,
    sd.publication_date,
    sd.url,
    sd.file_path,
    sd.file_hash_sha256,
    sd.file_format,
    sd.file_size_bytes,
    sd.language,
    sd.extraction_method,
    sd.caveat_text,
    sd.created_at
FROM {{ source('cegr', 'source_document') }} sd
JOIN {{ source('cegr', 'source_registry') }} sr
    ON sd.source_registry_id = sr.id