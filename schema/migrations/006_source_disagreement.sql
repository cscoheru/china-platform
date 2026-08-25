-- Migration 006 — cegr.source_disagreement table
-- Per docs/29 §1 (S1.14 cross-source consistency).
-- Captures cross-source discrepancies >2% (RECORDED) or >5% (NEEDS_REVIEW).

BEGIN;

CREATE TABLE IF NOT EXISTS cegr.source_disagreement (
    id                          UUID PRIMARY KEY DEFAULT uuid_generate_v4(),

    -- Identification triplet
    indicator_id                UUID NOT NULL REFERENCES cegr.indicator_definition(id),
    geo_entity_id               UUID NOT NULL REFERENCES cegr.geo_entity(id),
    calendar_period_id          UUID NOT NULL REFERENCES cegr.calendar_period(id),

    -- Source A (higher-priority / S0 by default)
    source_a_id                 UUID NOT NULL REFERENCES cegr.source_registry(id),
    source_a_observation_id     UUID REFERENCES cegr.observation(id),
    source_a_value              NUMERIC NOT NULL,
    source_a_level              cegr.source_level NOT NULL,
    source_a_basis              cegr.comparison_basis NOT NULL,

    -- Source B (challenger)
    source_b_id                 UUID NOT NULL REFERENCES cegr.source_registry(id),
    source_b_observation_id     UUID REFERENCES cegr.observation(id),
    source_b_value              NUMERIC NOT NULL,
    source_b_level              cegr.source_level NOT NULL,
    source_b_basis              cegr.comparison_basis NOT NULL,

    -- Computed diff columns (computed in dbt, kept here for query speed)
    diff_abs                    NUMERIC NOT NULL,
    diff_pct                    NUMERIC NOT NULL,
    diff_sign                   TEXT NOT NULL CHECK (diff_sign IN ('A_GT_B', 'B_GT_A', 'EQUAL')),

    -- Severity classification (per docs/10 §2.4 + docs/29 §0)
    severity                    TEXT NOT NULL CHECK (severity IN ('WITHIN_TOLERANCE', 'RECORDED', 'NEEDS_REVIEW')),
    severity_threshold_pct      NUMERIC NOT NULL,

    -- Resolution state
    resolution                  TEXT NOT NULL DEFAULT 'PENDING'
                                CHECK (resolution IN ('USE_A', 'USE_B', 'PARSE', 'PARALLEL', 'PENDING')),
    resolution_note             TEXT,
    resolved_by                 TEXT,
    resolved_at                 TIMESTAMPTZ,

    -- Detection metadata
    detected_at                 TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    detected_by                 TEXT NOT NULL DEFAULT 'dbt_test_cross_source_consistency',
    run_id                      UUID,

    CONSTRAINT source_disagreement_unique UNIQUE (
        indicator_id, geo_entity_id, calendar_period_id,
        source_a_id, source_b_id, detected_at
    )
);

CREATE INDEX IF NOT EXISTS idx_source_disagreement_severity
    ON cegr.source_disagreement (severity, detected_at DESC);

CREATE INDEX IF NOT EXISTS idx_source_disagreement_unresolved
    ON cegr.source_disagreement (resolved_at)
    WHERE resolved_at IS NULL;

CREATE INDEX IF NOT EXISTS idx_source_disagreement_triplet
    ON cegr.source_disagreement (indicator_id, geo_entity_id, calendar_period_id);

COMMENT ON TABLE cegr.source_disagreement IS
    'Per docs/29 §1 — cross-source consistency detection (S1.14.1 impl). '
    'Holds RECORDED (2-5%) and NEEDS_REVIEW (>5%) rows; WITHIN_TOLERANCE (<2%) never lands here.';

COMMIT;