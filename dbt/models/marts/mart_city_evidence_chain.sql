{{
    config(
        materialized='view',
        tags=['mart', 'city', 'evidence_chain', 's27bf_skeleton']
    )
}}

-- Mart model: mart_city_evidence_chain
-- Per docs/47 §3.1 + tasking 287 (S2.7-b-full dbt mart skeleton).
--
-- Purpose: city-scoped 6-segment evidence chain view for /cities/{slug}
--          (CONDITION / COMMITMENT / INPUT / PROCESS / OUTPUT / OUTCOME_RISK).
--          Used by EvidenceChain.tsx in CityPageMart.
--
-- Skeleton status: column contract declared (per docs/47 §3.1 table);
--                  zero rows emitted (WHERE FALSE) because O1 real SHA + Stage 1
--                  OPEN not yet closed (per docs/47 §6.3 切刀风险).
--
-- Red lines (per docs/47 §1.2 + docs/34 §1 + docs/06 §6.6 + docs/42 §8):
--   - No fake SHA — lineage.source_file_sha256 is always '0'*64 placeholder.
--   - No score / rating / rank / total_score / confidence_score columns.
--   - No real person/tenure JOIN data (related_persons filled by S2.7-b-full
--     landing knife after S2.1-lite mart_person_tenure PASS).
--
-- Real-data migration path (OPEN, not this knife):
--   - O1 SHA-locked Jiangsu sample (per docs/34 §3 + docs/47 §6.3).
--   - Stage 1 OPEN closure (per docs/34 §3).
--   - S2.1-lite mart_person_tenure PASS (per docs/47 §3.3).

SELECT
  -- city / geography
  NULL::UUID                                                              AS city_id,
  NULL::TEXT                                                              AS geo_name_zh,
  NULL::TEXT                                                              AS province_slug,
  -- evidence segment (6 fixed segments; enum-style guard at app layer)
  NULL::TEXT                                                              AS segment,
  -- canonical statement / polarity / strength
  NULL::TEXT                                                              AS canonical_statement,
  NULL::TEXT                                                              AS canonical_polarity,  -- SUPPORTS / CONTRADICTS / NEUTRAL
  NULL::TEXT                                                              AS evidence_strength,   -- STRONG / MODERATE / WEAK
  -- info layer (4 enum; per docs/40 §2.3 app-layer guard)
  NULL::TEXT                                                              AS info_layer,          -- FACT / DERIVED / INFERENCE / JUDGMENT
  -- lineage — ALWAYS placeholder until O1 SHA closes (per docs/47 §3.1 ⚠️ OPEN)
  NULL::TEXT                                                              AS lineage_is_demo,     -- 'true' / 'false'
  REPEAT('0', 64)::TEXT                                                   AS lineage_source_file_sha256  -- ⚠️ placeholder
FROM (SELECT 1) AS _skeleton
WHERE FALSE                                                               -- skeleton: zero rows