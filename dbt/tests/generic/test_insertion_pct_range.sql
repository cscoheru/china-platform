{% test insertion_pct_range(model, column_name) %}

-- Custom generic test: insertion_pct must be in [0.0, 100.0].
-- Used on stg_ingestion_run.insertion_pct.

SELECT
    {{ column_name }}           AS offending_value,
    COUNT(*)                   AS occurrence_count
FROM {{ model }}
WHERE {{ column_name }} IS NOT NULL
  AND ({{ column_name }} < 0.0 OR {{ column_name }} > 100.0)
GROUP BY {{ column_name }}

{% endtest %}