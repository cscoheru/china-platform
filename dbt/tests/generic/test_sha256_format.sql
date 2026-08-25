{% test sha256_format(model, column_name) %}

-- Custom generic test: SHA-256 hex digest must match `^[a-f0-9]{64}$`.
-- Used on stg_source_document.file_hash_sha256.

SELECT
    {{ column_name }}           AS offending_value,
    COUNT(*)                   AS occurrence_count
FROM {{ model }}
WHERE {{ column_name }} IS NOT NULL
  AND {{ column_name }} !~ '^[a-f0-9]{64}$'
GROUP BY {{ column_name }}

{% endtest %}