{{
    config(
        materialized='view',
        tags=['staging', 'source_disagreement']
    )
}}

-- Staging model for cross-source disagreement candidate pairs (docs/29 §2.1).
-- Generates ordered (source_a < source_b) pairs of S0/S1 observations
-- on the same (indicator, geo, period) sharing the same comparison_basis.

WITH obs AS (
  SELECT
    o.id                        AS observation_id,
    o.indicator_id,
    o.geo_entity_id,
    o.calendar_period_id,
    o.value,
    o.comparison_basis,
    o.source_id,                 -- FK to source_document
    sd.source_registry_id,
    sd.source_level
  FROM {{ source('cegr', 'observation') }} o
  JOIN {{ source('cegr', 'source_document') }} sd
    ON sd.id = o.source_id
  WHERE o.value_type = 'FACT'
    AND o.value IS NOT NULL
    AND sd.source_level IN ('S0', 'S1')
),

pairs AS (
  SELECT
    a.indicator_id,
    a.geo_entity_id,
    a.calendar_period_id,
    -- Source A = higher priority (lower source_level wins)
    CASE WHEN a.source_level < b.source_level THEN a.source_registry_id
         WHEN b.source_level < a.source_level THEN b.source_registry_id
         ELSE LEAST(a.source_registry_id, b.source_registry_id) END        AS source_a_id,
    CASE WHEN a.source_level < b.source_level THEN a.observation_id
         WHEN b.source_level < a.source_level THEN b.observation_id
         ELSE LEAST(a.observation_id, b.observation_id) END               AS source_a_observation_id,
    CASE WHEN a.source_level < b.source_level THEN a.value
         WHEN b.source_level < a.source_level THEN b.value
         ELSE LEAST(a.value, b.value) END                                 AS source_a_value,
    CASE WHEN a.source_level < b.source_level THEN a.source_level
         WHEN b.source_level < a.source_level THEN b.source_level
         ELSE a.source_level END                                          AS source_a_level,
    CASE WHEN a.source_level < b.source_level THEN a.comparison_basis
         WHEN b.source_level < a.source_level THEN b.comparison_basis
         ELSE a.comparison_basis END                                      AS source_a_basis,

    CASE WHEN a.source_level < b.source_level THEN b.source_registry_id
         WHEN b.source_level < a.source_level THEN a.source_registry_id
         ELSE GREATEST(a.source_registry_id, b.source_registry_id) END   AS source_b_id,
    CASE WHEN a.source_level < b.source_level THEN b.observation_id
         WHEN b.source_level < a.source_level THEN a.observation_id
         ELSE GREATEST(a.observation_id, b.observation_id) END           AS source_b_observation_id,
    CASE WHEN a.source_level < b.source_level THEN b.value
         WHEN b.source_level < a.source_level THEN a.value
         ELSE GREATEST(a.value, b.value) END                             AS source_b_value,
    CASE WHEN a.source_level < b.source_level THEN b.source_level
         WHEN b.source_level < a.source_level THEN a.source_level
         ELSE a.source_level END                                          AS source_b_level,
    CASE WHEN a.source_level < b.source_level THEN b.comparison_basis
         WHEN b.source_level < a.source_level THEN a.comparison_basis
         ELSE b.comparison_basis END                                      AS source_b_basis
  FROM obs a
  JOIN obs b
    ON a.indicator_id     = b.indicator_id
   AND a.geo_entity_id    = b.geo_entity_id
   AND a.calendar_period_id = b.calendar_period_id
   AND a.source_registry_id < b.source_registry_id
   AND a.comparison_basis  = b.comparison_basis
)

SELECT
  indicator_id, geo_entity_id, calendar_period_id,
  source_a_id, source_a_observation_id, source_a_value, source_a_level, source_a_basis,
  source_b_id, source_b_observation_id, source_b_value, source_b_level, source_b_basis,
  ABS(source_a_value - source_b_value)                                    AS diff_abs,
  CASE WHEN source_a_value = 0 THEN NULL
       ELSE ABS(source_a_value - source_b_value) / ABS(source_a_value) * 100
  END                                                                    AS diff_pct,
  CASE WHEN source_a_value > source_b_value THEN 'A_GT_B'
       WHEN source_a_value < source_b_value THEN 'B_GT_A'
       ELSE 'EQUAL' END                                                   AS diff_sign
FROM pairs