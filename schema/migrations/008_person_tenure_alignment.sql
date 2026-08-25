-- ============================================================================
-- Migration 008 — person / tenure / position additive alignment (S2.1-lite)
-- ============================================================================
-- Per Cursor 180 §SCHEMA (S2.1-lite tasking, user ruling D shrink).
-- Per docs/36 §2 (Stage 2 "人" dimension table contracts).
-- Per Cursor 179 (user ruling D accepted 2026-08-25).
--
-- Brings the 6 existing person/tenure tables (created in 01-core.sql lines
-- 635-705) up to the docs/36 §2 field contract by ADDING nullable columns.
-- NO DROP / NO RENAME / NO NOT NULL / NO FK / NO EXCLUDE in this migration:
--   * No FK: keeps 008 purely additive; existing rows keep working with NULL
--     back-references. FKs land in 009 when mart integrity demands them.
--   * No EXCLUDE on tenure: docs/36 §2.4 + tasking 180 §红线钉死 — overlapping
--     tenures are LEGAL (the same person can hold two roles simultaneously,
--     or one person can succeed themselves across reorganizations).
--   * No NOT NULL: existing rows pre-migration would all fail the constraint.
--   * No DROP/RENAME: legacy column `claim` on person_source_evidence is
--     kept; new column `excerpt` is added additively. Data backfill is a
--     separate knife (deferred).
--
-- Why additive-only:
--   * Stage 1 prior migrations (004, 005, 006, 007) all follow the additive
--     pattern. Migration 008 inherits the convention.
--   * Existing 0 rows in person/tenure (no pilot data ever inserted), but
--     41 negative tests in test_schema_negative.py touch these tables and
--     must continue passing.
--   * docs/36 §2.0 prohibits altering existing field names — only additive
--     columns are allowed at this knife.
--
-- Columns added:
--   person:
--     + canonical_name_pinyin   TEXT NULL  -- docs/36 §2.1; for search/sort
--   person_name_alias:
--     + valid_from              DATE NULL  -- docs/36 §2.2; alias validity range
--     + valid_to                DATE NULL
--   position:
--     + canonical_title         TEXT NULL  -- docs/36 §2.3; normalized title
--     + title_en                TEXT NULL  -- docs/36 §2.3; English rendering
--     + rank_level              TEXT NULL  -- docs/36 §2.3; enum-style; NOT
--                                              a capability score; pure filter
--     + is_standing_committee   BOOLEAN NULL DEFAULT FALSE
--   tenure:
--     + geo_entity_id           UUID NULL  -- docs/36 §2.4; NULL = central or
--                                              pre-existing row
--     + is_current              BOOLEAN NULL  -- docs/36 §2.4; computed
--                                                 flag, end_date IS NULL
--     + departure_event_id      UUID NULL  -- docs/36 §2.4; FK to appointment
--                                              event when tenure closes
--   appointment_event:
--     + person_id               UUID NULL  -- docs/36 §2.5; nullable for
--                                              departure-only events where
--                                              tenure_id suffices
--     + position_id             UUID NULL  -- docs/36 §2.5
--     + geo_entity_id           UUID NULL  -- docs/36 §2.5
--     + announcement_doc_id     UUID NULL  -- docs/36 §2.5; FK to source_document
--   person_source_evidence:
--     + excerpt                 TEXT NULL  -- docs/36 §2.6; new canonical name
--                                              for what was previously `claim`.
--                                              Old `claim` column preserved for
--                                              back-compat (this knife).
--     + evidence_type           TEXT NULL  -- docs/36 §2.6; CV / ANNOUNCEMENT
--                                              / BIOGRAPHY / etc.
--
-- Red lines (per docs/34 §7 + tasking 180 §红线):
--   * ❌ 不加 EXCLUDE 约束 — overlap legal
--   * ❌ 不加 FK 约束 — deferred to 009
--   * ❌ 不 DROP / 不 RENAME 既有列 — additive only
--   * ❌ 不动 gate_thresholds.json (spike-04 评测构件，只读)
--   * ❌ 不做官员能力分 / 总分 / 排名 — rank_level 是 enum-style TEXT 检索过滤
--   * ❌ 不写 dbt mart/stg — 本刀 S2.1-lite 仅 DDL
--   * ❌ 不灌首批 ≤30 person 真实/演示履历 — 本刀 0 行业务数据
--   * ❌ 不爬网抓履历 — seed 骨架仅
--
-- Schema verification after this migration:
--   * stage0 38 schema_negative tests must still pass (no CHECK/UNIQUE changed)
--   * tests/test_person_tenure_s21lite.py (this knife) must pass all 3 cases
-- ============================================================================

SET search_path = cegr, public;

-- ----- person -----
ALTER TABLE person
    ADD COLUMN IF NOT EXISTS canonical_name_pinyin TEXT;

COMMENT ON COLUMN person.canonical_name_pinyin IS
    'docs/36 §2.1: pinyin rendering of canonical_name for sort/search; NULL OK';

-- ----- person_name_alias -----
ALTER TABLE person_name_alias
    ADD COLUMN IF NOT EXISTS valid_from DATE,
    ADD COLUMN IF NOT EXISTS valid_to   DATE;

COMMENT ON COLUMN person_name_alias.valid_from IS
    'docs/36 §2.2: alias validity start; NULL for "all-time" aliases';
COMMENT ON COLUMN person_name_alias.valid_to IS
    'docs/36 §2.2: alias validity end; NULL = currently in use';

-- ----- position -----
ALTER TABLE position
    ADD COLUMN IF NOT EXISTS canonical_title       TEXT,
    ADD COLUMN IF NOT EXISTS title_en              TEXT,
    ADD COLUMN IF NOT EXISTS rank_level            TEXT,
    ADD COLUMN IF NOT EXISTS is_standing_committee BOOLEAN;

COMMENT ON COLUMN position.canonical_title IS
    'docs/36 §2.3: normalized title (post-de-dup); NULL OK; legacy rows
     keep raw `title` as ground truth';
COMMENT ON COLUMN position.title_en IS
    'docs/36 §2.3: English rendering for international cross-reference';
COMMENT ON COLUMN position.rank_level IS
    'docs/36 §2.3: enum-style rank (e.g. PROVINCIAL_MINISTER / DEPUTY_MINISTER
     / BUREAU_DIRECTOR / etc.). Application-level validation; stored as TEXT
     to allow adding new values without migration churn. NOT a capability
     score / NOT a total / NOT a ranking metric — purely a filter dimension.';
COMMENT ON COLUMN position.is_standing_committee IS
    'docs/36 §2.3: TRUE if position sits on the provincial standing committee';

-- ----- tenure -----
ALTER TABLE tenure
    ADD COLUMN IF NOT EXISTS geo_entity_id      UUID,
    ADD COLUMN IF NOT EXISTS is_current         BOOLEAN,
    ADD COLUMN IF NOT EXISTS departure_event_id UUID;

COMMENT ON COLUMN tenure.geo_entity_id IS
    'docs/36 §2.4: redundant with position.geo_entity_id but stored here for
     fast filtering without JOIN. NULL for central-level tenures or legacy
     rows pre-migration-008.';
COMMENT ON COLUMN tenure.is_current IS
    'docs/36 §2.4: end_date IS NULL derived flag; application-maintained';
COMMENT ON COLUMN tenure.departure_event_id IS
    'docs/36 §2.4: FK to appointment_event (when tenure closes); NULL for
     open tenures. FK constraint deferred to migration 009.';

-- ----- appointment_event -----
ALTER TABLE appointment_event
    ADD COLUMN IF NOT EXISTS person_id           UUID,
    ADD COLUMN IF NOT EXISTS position_id         UUID,
    ADD COLUMN IF NOT EXISTS geo_entity_id       UUID,
    ADD COLUMN IF NOT EXISTS announcement_doc_id UUID;

COMMENT ON COLUMN appointment_event.person_id IS
    'docs/36 §2.5: redundant with tenure.person_id; nullable for departure-
     only events where tenure_id suffices';
COMMENT ON COLUMN appointment_event.position_id IS
    'docs/36 §2.5: redundant with tenure.position_id';
COMMENT ON COLUMN appointment_event.geo_entity_id IS
    'docs/36 §2.5: redundant with tenure.geo_entity_id';
COMMENT ON COLUMN appointment_event.announcement_doc_id IS
    'docs/36 §2.5: FK to source_document hosting the original announcement
     (e.g. 决定 / 通知). FK constraint deferred to migration 009.';

-- ----- person_source_evidence -----
ALTER TABLE person_source_evidence
    ADD COLUMN IF NOT EXISTS excerpt       TEXT,
    ADD COLUMN IF NOT EXISTS evidence_type TEXT;

-- Backfill: copy existing `claim` into `excerpt` so any rows written before
-- migration 008 still satisfy downstream queries that read `excerpt`.
UPDATE person_source_evidence
SET excerpt = claim
WHERE excerpt IS NULL AND claim IS NOT NULL;

COMMENT ON COLUMN person_source_evidence.excerpt IS
    'docs/36 §2.6: canonical name for what was previously `claim`. Old
     `claim` column preserved for back-compat (this knife); future knife
     will rename `claim` → `excerpt` after a 2-version deprecation cycle.';
COMMENT ON COLUMN person_source_evidence.evidence_type IS
    'docs/36 §2.6: CV / ANNOUNCEMENT / BIOGRAPHY / etc.; application-validated';

-- ----- light indexes (post-load only; CONCURRENTLY deferred to ops knife) -----
-- These are intentionally bare CREATE INDEX (not CONCURRENTLY) because they
-- only run on the empty test schema during migration apply.
CREATE INDEX IF NOT EXISTS idx_tenure_geo_entity          ON tenure (geo_entity_id);
CREATE INDEX IF NOT EXISTS idx_tenure_is_current         ON tenure (is_current);
CREATE INDEX IF NOT EXISTS idx_appointment_event_person  ON appointment_event (person_id);
CREATE INDEX IF NOT EXISTS idx_appointment_event_position ON appointment_event (position_id);
CREATE INDEX IF NOT EXISTS idx_appointment_event_geo     ON appointment_event (geo_entity_id);
CREATE INDEX IF NOT EXISTS idx_position_rank_level       ON position (rank_level);
CREATE INDEX IF NOT EXISTS idx_position_is_standing      ON position (is_standing_committee);
CREATE INDEX IF NOT EXISTS idx_pse_evidence_type         ON person_source_evidence (evidence_type);

-- Reset search_path so later migrations don't inherit cegr implicit.
RESET search_path;