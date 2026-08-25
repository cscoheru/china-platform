{% test duration_non_negative(model, column_name) %}

-- Custom generic test: duration_seconds must be >= 0.
-- Used on stg_ingestion_run.duration_seconds.

SELECT
    {{ column_name }}           AS offending_value,
    COUNT(*)                   AS occurrence_count
FROM {{ model }}
WHERE {{ column_name }} IS NOT NULL
  AND {{ column_name }} < 0
GROUP BY {{ column_name }}

{% endtest %}