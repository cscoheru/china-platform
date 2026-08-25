{% test quality_score_range(model, column_name) %}

-- Custom generic test: quality_score must be in [0.0, 1.0].
-- Used on stg_observation_quality.quality_score.

SELECT
    {{ column_name }}           AS offending_value,
    COUNT(*)                   AS occurrence_count
FROM {{ model }}
WHERE {{ column_name }} IS NOT NULL
  AND ({{ column_name }} < 0.0 OR {{ column_name }} > 1.0)
GROUP BY {{ column_name }}

{% endtest %}