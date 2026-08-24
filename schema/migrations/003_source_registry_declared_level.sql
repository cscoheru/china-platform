-- ============================================================================
-- Migration 003 — source_registry.declared_source_level + CSV-side metadata
-- ============================================================================
-- Adds the per-registry `declared_source_level` column (mirrors CSV
-- source_registry/registry.csv::declared_source_level) and optional CSV-side
-- metadata columns (local_sample_path / file_hash_sha256 / file_size_bytes /
-- purpose_note / source_level) so that source_registry/registry.csv → DB
-- UPSERT preserves I-05 declared-vs-effective split at the registry layer.
--
-- Per docs/03 §9.5 and reviews/30-stage1-s13-registry-tasking-20260824 §0.1:
--   * `declared_source_level` is uploader's claim (CSV col 17)
--   * `source_level` is the platform-effective level (CSV col 13)
--   * Both NULL-able for backward compatibility with the existing 6 rows.
--
-- This is additive only — no CHECK constraints change, no columns removed,
-- no semantics touched. Stage 0 39 schema_negative + 21 source_governance
-- tests must still pass.
-- ============================================================================

SET search_path = cegr, public;

ALTER TABLE source_registry
    ADD COLUMN IF NOT EXISTS source_level            source_level,
    ADD COLUMN IF NOT EXISTS declared_source_level   source_level,
    ADD COLUMN IF NOT EXISTS local_sample_path       TEXT,
    ADD COLUMN IF NOT EXISTS file_hash_sha256        TEXT,
    ADD COLUMN IF NOT EXISTS file_size_bytes         BIGINT,
    ADD COLUMN IF NOT EXISTS purpose_note            TEXT;

COMMENT ON COLUMN source_registry.source_level IS
    '平台 effective 来源等级（per I-05 §9；CSV col 13）。NULL = 尚未评估。';

COMMENT ON COLUMN source_registry.declared_source_level IS
    '上传者/CSV 声明的来源等级（per I-05 §9；CSV col 17）。可能与 source_level 不同。';

COMMENT ON COLUMN source_registry.local_sample_path IS
    'CSV col 14: 仓库内已下载样本相对路径（用于 evidence_pack 校验）';

COMMENT ON COLUMN source_registry.file_hash_sha256 IS
    'CSV col 15: 样本 SHA-256（hex, 64 chars）';

COMMENT ON COLUMN source_registry.file_size_bytes IS
    'CSV col 16: 样本字节数（>0）';

COMMENT ON COLUMN source_registry.purpose_note IS
    'CSV col 18: 用途说明（research / representative / pressure 等）';

-- Per source_document source_doc_hash_format convention; registry layer is
-- more lenient (NULL allowed for registry rows whose sample is not yet
-- present on disk).
ALTER TABLE source_registry
    ADD CONSTRAINT source_registry_hash_format
        CHECK (file_hash_sha256 IS NULL OR file_hash_sha256 ~ '^[a-f0-9]{64}$')
        NOT VALID;

-- NOT VALID lets the constraint apply to new rows without re-scanning the
-- (currently empty) source_registry table; future rows must satisfy it.
ALTER TABLE source_registry VALIDATE CONSTRAINT source_registry_hash_format;