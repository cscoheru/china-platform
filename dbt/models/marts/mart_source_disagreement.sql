{{
    config(
        materialized='incremental',
        unique_key=['indicator_id', 'geo_entity_id', 'calendar_period_id', 'source_a_id', 'source_b_id', 'detected_at'],
        tags=['mart', 'source_disagreement']
    )
}}

-- Mart model for source_disagreement (docs/29 §2.2).
-- Classifies each candidate pair into severity tier and persists only
-- RECORDED (2-5%) and NEEDS_REVIEW (>5%) rows.
-- WITHIN_TOLERANCE (<2%) is filtered out by WHERE clause.

WITH classified AS (
  SELECT
    indicator_id, geo_entity_id, calendar_period_id,
    source_a_id, source_a_observation_id, source_a_value, source_a_level, source_a_basis,
    source_b_id, source_b_observation_id, source_b_value, source_b_level, source_b_basis,
    diff_abs, diff_pct, diff_sign,
    CASE
      WHEN diff_pct IS NULL THEN 'WITHIN_TOLERANCE'
      WHEN diff_pct < 2.0 THEN 'WITHIN_TOLERANCE'
      WHEN diff_pct < 5.0 THEN 'RECORDED'
      ELSE 'NEEDS_REVIEW'
    END                                                                  AS severity,
    COALESCE(diff_pct, 0)                                                 AS severity_threshold_pct,
    NOW()                                                                 AS detected_at
  FROM {{ ref('stg_source_disagreement_candidate') }}
)

SELECT
  {{ dbt_utils.generate_surrogate_key([
      'indicator_id','geo_entity_id','calendar_period_id',
      'source_a_id','source_b_id','detected_at'
  ]) }}                                                                  AS id,
  indicator_id, geo_entity_id, calendar_period_id,
  source_a_id, source_a_observation_id, source_a_value, source_a_level, source_a_basis,
  source_b_id, source_b_observation_id, source_b_value, source_b_level, source_b_basis,
  diff_abs, diff_pct, diff_sign,
  severity, severity_threshold_pct,
  'PENDING'                                                              AS resolution,
  NULL                                                                   AS resolution_note,
  NULL                                                                   AS resolved_by,
  NULL                                                                   AS resolved_at,
  detected_at,
  'dbt_mart_source_disagreement'                                         AS detected_by,
  '{{ invocation_id }}'::UUID                                             AS run_id
FROM classified
WHERE severity IN ('RECORDED', 'NEEDS_REVIEW')