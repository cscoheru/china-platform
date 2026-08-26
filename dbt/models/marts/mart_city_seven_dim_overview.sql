{{
    config(
        materialized='view',
        tags=['mart', 'city', 'seven_dim_overview', 's27bf_skeleton']
    )
}}

-- Mart model: mart_city_seven_dim_overview
-- Per docs/47 §3.2 + tasking 287 (S2.7-b-full dbt mart skeleton).
--
-- Purpose: city × 7-dimension overview projection for /cities/{slug}
--          (SevenDimGrid.tsx in CityPageMart).
--          Per docs/42 §2.4 / §2.5, 7 cards: POLICY_DELIVERY / FISCAL_EXECUTION
--          / PROJECT_DELIVERY / ECONOMIC_ADAPTATION / PUBLIC_SERVICES /
--          RISK_MANAGEMENT / GOAL_CONSISTENCY.
--
-- Skeleton status: column contract declared (per docs/47 §3.2 table);
--                  zero rows emitted (WHERE FALSE) because O1 real SHA + Stage 1
--                  OPEN not yet closed (per docs/47 §6.3 切刀风险).
--
-- Red lines (per docs/47 §1.2 + docs/34 §1 + docs/06 §6.6 + docs/42 §8):
--   - No score / rating / rank / total_score / confidence_score / peer_rank.
--   - n_supports / n_contradicts / n_inference / n_judgment / n_derived are
--     COUNT aggregates only (no weighting / no scoring).
--   - balance_status ∈ {NO_EVIDENCE, NO_CONTRADICTING_EVIDENCE,
--     NO_SUPPORTING_EVIDENCE, SUPPORTS_DOMINANT, CONTRADICTS_DOMINANT}
--     (5 enum; app-layer guard per docs/42 §2.5).
--
-- Real-data migration path (OPEN, not this knife):
--   - O1 SHA-locked Jiangsu sample (per docs/34 §3 + docs/47 §6.3).
--   - Stage 1 OPEN closure (per docs/34 §3).
--   - Inference_record + claim_evidence_link from migration 012.

SELECT
  -- city / card keys
  NULL::UUID                                                              AS city_id,
  NULL::TEXT                                                              AS card_id,           -- 7 enum (POLICY_DELIVERY / ... / GOAL_CONSISTENCY)
  -- counts only — NO weighting, NO scoring (per docs/42 §8 + docs/06 §6.6)
  NULL::INTEGER                                                           AS n_supports,
  NULL::INTEGER                                                           AS n_contradicts,
  NULL::INTEGER                                                           AS n_inference,
  NULL::INTEGER                                                           AS n_judgment,
  NULL::INTEGER                                                           AS n_derived,
  -- 5 enum balance status (app-layer guard; per docs/42 §2.5)
  NULL::TEXT                                                              AS balance_status,    -- NO_EVIDENCE / NO_CONTRADICTING_EVIDENCE / NO_SUPPORTING_EVIDENCE / SUPPORTS_DOMINANT / CONTRADICTS_DOMINANT
  -- demo sentinel
  NULL::TEXT                                                              AS is_demo
FROM (SELECT 1) AS _skeleton
WHERE FALSE                                                               -- skeleton: zero rows