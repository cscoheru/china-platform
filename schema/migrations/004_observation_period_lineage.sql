-- ============================================================================
-- Migration 004 — observation per-row period metadata + lineage JSONB
-- ============================================================================
-- Per Cursor 50 §SCHEMA (Stage 1 / S1.6 省级年鉴连接器实现任务书).
-- Implements B-06 (per-indicator period metadata) + R3-E (per-row lineage chain)
-- by adding additive, NULL-able columns to cegr.observation. This is the
-- schema contract that ProvincialYearbookConnector (S1.6) writes to.
--
-- Why additive-only:
--   * Existing 0 observations in observation (S1.4/S1.5 pilot inserted none
--     because reference data FK cannot be resolved). Adding NOT NULL columns
--     is unnecessary and would force a backfill that has no semantics yet.
--   * Existing CHECK constraints (observation_missing_consistency,
--     observation_unit_required, observation_confidence_range) do NOT touch
--     the new columns — they remain valid.
--   * UNIQUE NULLS NOT DISTINCT on natural keys still works because period_*
--     columns are not part of the natural key (natural key is indicator +
--     methodology_version + geo + period + source, where "period" is the
--     calendar_period_id FK).
--
-- Columns added:
--   period_start   DATE  NULL  — per B-06; e.g. 2026-01-01 for cumulative H1
--   period_end     DATE  NULL  — per B-06; e.g. 2026-06-30 (or 2026-05-31 for
--                                5-month, 2026-06-30 for period-end-of-month)
--   period_label   TEXT  NULL  — Chinese label per source sheet; e.g.
--                                "2026年1-6月" / "2026年6月末"
--   period_type    TEXT  NULL  — per-row enum string. Allowed values are
--                                governed by docs/20 §1.2 — NOT collapsed to
--                                a single CUMULATIVE_HALF_YEAR. Examples:
--                                CUMULATIVE_HALF_YEAR / CUMULATIVE_5MONTH /
--                                PERIOD_END_OF_MONTH / INDEX_YOY.
--                                (Stored as TEXT rather than ENUM to permit
--                                adding new period_type values without
--                                migration churn; integrity is enforced by
--                                application-level validation in docs/20 §1.2
--                                + the connector's PERIOD_METADATA_MAP.)
--   lineage        JSONB NULL  — per-row R3-E provenance:
--                                {
--                                  "chain_id":         "<stable id>",
--                                  "source_file_sha256": "<hex>",
--                                  "source_file_url":  "<canonical URL>",
--                                  "extractor_version":"<semver>"
--                                }
--   caveat_text    TEXT  NULL  — per-row caveat (R3-E). For Hubei H1 2026:
--                                GDP/居民收入行 quarterly_data_verified=False
--                                carries a "GDP为季度数被标为半年累计；权威
--                                口径待核验" caveat. The connector writes this
--                                string from PERIOD_METADATA_MAP[indicator_zh]
--                                .caveat; it is NOT the same as observation.
--                                notes (which is operator-authored).
--
-- Red lines (per docs/20 §6):
--   * ❌ 不漂移 CUMULATIVE_HALF_YEAR — period_type stays TEXT; no DEFAULT
--     forcing a single value. Per-indicator period_type is canonical in
--     PERIOD_METADATA_MAP (spike 02) and connector reads from there.
--   * ❌ 不在此处塞中文 — period_label is Chinese (matches source sheet) but
--     indicator_canonical (in application layer, not DB) is snake_case
--     English; indicator_zh never lands in observation.
--   * ❌ 不在 fixture 临时建表 — this migration is the only schema authority.
--
-- Schema verification after this migration:
--   * stage0 39 schema_negative tests must still pass (no enum/CHECK changed)
--   * stage0 21 source_governance tests must still pass
--   * pytest tests/test_provincial_yearbook_connector.py asserts the new
--     columns are populated by the connector end-to-end
-- ============================================================================

SET search_path = cegr, public;

ALTER TABLE observation
    ADD COLUMN IF NOT EXISTS period_start   DATE,
    ADD COLUMN IF NOT EXISTS period_end     DATE,
    ADD COLUMN IF NOT EXISTS period_label   TEXT,
    ADD COLUMN IF NOT EXISTS period_type    TEXT,
    ADD COLUMN IF NOT EXISTS lineage        JSONB,
    ADD COLUMN IF NOT EXISTS caveat_text    TEXT;

-- Lightweight sanity CHECK on date ordering — both NULL allowed (additive);
-- if both present, period_end must be ≥ period_start.
ALTER TABLE observation
    ADD CONSTRAINT observation_period_range
        CHECK (period_start IS NULL OR period_end IS NULL
               OR period_end >= period_start)
        NOT VALID;

ALTER TABLE observation VALIDATE CONSTRAINT observation_period_range;

-- lineage is JSONB; an empty JSON object `{}` is allowed (write of "no
-- lineage known yet" is honest); NULL is also allowed (legacy rows).
-- No CHECK on JSONB shape — application owns the schema (R3-E lineage
-- contract documented in docs/20 §2).

COMMENT ON COLUMN observation.period_start IS
    'B-06 per-indicator period start (DATE); NULL for legacy rows';

COMMENT ON COLUMN observation.period_end IS
    'B-06 per-indicator period end (DATE); NULL for legacy rows';

COMMENT ON COLUMN observation.period_label IS
    'B-06 per-indicator period label (Chinese source-sheet text); NULL OK';

COMMENT ON COLUMN observation.period_type IS
    'B-06 per-indicator period type (TEXT, application-validated). Examples:
     CUMULATIVE_HALF_YEAR / CUMULATIVE_5MONTH / PERIOD_END_OF_MONTH /
     INDEX_YOY. NOT collapsed to a single value; connector reads from
     PERIOD_METADATA_MAP. Allowed values documented in docs/20 §1.2.';

COMMENT ON COLUMN observation.lineage IS
    'R3-E per-row provenance (JSONB). Shape:
     {chain_id, source_file_sha256, source_file_url, extractor_version}.
     chain_id is stable across re-extractions of the same SHA-256 input.';

COMMENT ON COLUMN observation.caveat_text IS
    'R3-E per-row caveat (TEXT). Distinct from observation.notes
     (operator-authored). Filled by connector from PERIOD_METADATA_MAP
     for indicators awaiting authoritative methodology verification
     (e.g. quarterly GDP mis-classified as cumulative H1).';

-- Index on period_start/end supports downstream per-period queries
-- (Gate 1 analytical queries against time windows). Created CONCURRENTLY
-- is preferred in production, but tests run on a small dataset so plain
-- CREATE INDEX is acceptable here.
CREATE INDEX IF NOT EXISTS idx_observation_period_range
    ON observation (period_start, period_end);

CREATE INDEX IF NOT EXISTS idx_observation_period_type
    ON observation (period_type);

-- GIN index on lineage JSONB — speeds up "find all rows from chain X" queries.
CREATE INDEX IF NOT EXISTS idx_observation_lineage_gin
    ON observation USING GIN (lineage);