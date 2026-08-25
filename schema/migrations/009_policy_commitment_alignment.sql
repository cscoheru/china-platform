-- Migration 009 — S2.2-lite: policy DDL additive columns
--
-- Per docs/37 §2 (Stage 2 / S2.2 规划) + Cursor tasking 195 §SCHEMA.
-- 用户裁定 D (缩刀节奏) — 与 S2.1-lite (008) 同构.
--
-- 全部 ADD COLUMN IF NOT EXISTS — 无 FK 启用、无 EXCLUDE、无 DROP/RENAME、
-- 不动 ENUM、不动现有触发器. 与既有 5 张表 (01-core.sql lines 711-783) 严格对齐.
--
-- 新增列总计: 8 (policy_document) + 5 (policy_target) + 2 (policy_measure) +
--            5 (government_commitment) + 3 (commitment_progress) = 23 列.
-- 评分/排名/总分字段 (score/rating/rank/total_score) 红线: 一律不引入.
--
-- Per docs/33 §3.2 sentinel: lineage JSONB 是 is_demo 唯一落点;
-- 全 is_demo=true 时 lineage.is_demo = "true".
-- Per R3-E provenance: lineage 形状 = {chain_id, source_file_sha256,
-- source_file_url, extractor_version, is_demo}.

SET search_path = cegr, public;

-- ---------------------------------------------------------------------------
-- 1. policy_document (+ 8 cols)
-- ---------------------------------------------------------------------------

ALTER TABLE policy_document
    ADD COLUMN IF NOT EXISTS canonical_title TEXT,
    ADD COLUMN IF NOT EXISTS title_en TEXT,
    ADD COLUMN IF NOT EXISTS policy_level TEXT,
    ADD COLUMN IF NOT EXISTS is_standing_committee BOOLEAN,
    ADD COLUMN IF NOT EXISTS classification TEXT,
    ADD COLUMN IF NOT EXISTS effective_year INTEGER,
    ADD COLUMN IF NOT EXISTS lineage JSONB,
    ADD COLUMN IF NOT EXISTS policy_hash_canonical TEXT;

COMMENT ON COLUMN policy_document.canonical_title IS
    '归一化标题 (去版本/编号后缀); 与 person.position.canonical_title 同模式';
COMMENT ON COLUMN policy_document.title_en IS
    '英文渲染 (国际 cross-ref); nullable';
COMMENT ON COLUMN policy_document.policy_level IS
    'enum-style: CENTRAL | PROVINCIAL | MUNICIPAL | COUNTY; 不引入 schema ENUM (per docs/37 §10.5)';
COMMENT ON COLUMN policy_document.is_standing_committee IS
    '是否常委会决议 (极少数); nullable BOOLEAN; per docs/37 §2.1';
COMMENT ON COLUMN policy_document.classification IS
    'enum: PLAN | REGULATION | NOTICE | ANNOUNCEMENT | WORK_REPORT | OP_ED; per docs/37 §2.1 + S2.7 第六段消费';
COMMENT ON COLUMN policy_document.effective_year IS
    '从 effective_date 提取 (避免 JOIN to date_part)';
COMMENT ON COLUMN policy_document.lineage IS
    'per-row R3-E provenance: {chain_id, source_file_sha256, source_file_url, extractor_version, is_demo}; is_demo sentinel per docs/33 §3.2';
COMMENT ON COLUMN policy_document.policy_hash_canonical IS
    '同一篇政策的 stable 跨版本 SHA (per R12-A de-dupe); nullable TEXT';

-- ---------------------------------------------------------------------------
-- 2. policy_target (+ 5 cols)
-- ---------------------------------------------------------------------------

ALTER TABLE policy_target
    ADD COLUMN IF NOT EXISTS target_value_lower NUMERIC,
    ADD COLUMN IF NOT EXISTS target_value_upper NUMERIC,
    ADD COLUMN IF NOT EXISTS target_unit_canonical TEXT,
    ADD COLUMN IF NOT EXISTS verification_method TEXT,
    ADD COLUMN IF NOT EXISTS lineage JSONB;

COMMENT ON COLUMN policy_target.target_value_lower IS
    '区间下限 (e.g. "增长 5-7%" 下界); nullable NUMERIC';
COMMENT ON COLUMN policy_target.target_value_upper IS
    '区间上限; nullable NUMERIC';
COMMENT ON COLUMN policy_target.target_unit_canonical IS
    '归一化单位 (avoid "亿元" vs "亿元(本币)" drift)';
COMMENT ON COLUMN policy_target.verification_method IS
    'enum-style: STATISTICAL_BULLETIN | AUDIT_REPORT | SELF_REPORT | UNKNOWN';
COMMENT ON COLUMN policy_target.lineage IS
    'per-row R3-E provenance; per docs/33 §3.2 sentinel';

-- ---------------------------------------------------------------------------
-- 3. policy_measure (+ 2 cols)
-- ---------------------------------------------------------------------------

ALTER TABLE policy_measure
    ADD COLUMN IF NOT EXISTS expected_outcome_text TEXT,
    ADD COLUMN IF NOT EXISTS lineage JSONB;

COMMENT ON COLUMN policy_measure.expected_outcome_text IS
    '措施期望产出 (自然语言; 不评分); nullable TEXT';
COMMENT ON COLUMN policy_measure.lineage IS
    'per-row R3-E provenance; per docs/33 §3.2 sentinel';

-- ---------------------------------------------------------------------------
-- 4. government_commitment (+ 5 cols)
-- ---------------------------------------------------------------------------

ALTER TABLE government_commitment
    ADD COLUMN IF NOT EXISTS commitment_text_en TEXT,
    ADD COLUMN IF NOT EXISTS proposer_role TEXT,
    ADD COLUMN IF NOT EXISTS is_measurable BOOLEAN,
    ADD COLUMN IF NOT EXISTS measurement_basis TEXT,
    ADD COLUMN IF NOT EXISTS lineage JSONB;

COMMENT ON COLUMN government_commitment.commitment_text_en IS
    '英文承诺 (国际 cross-ref); nullable TEXT per docs/37 §10.3';
COMMENT ON COLUMN government_commitment.proposer_role IS
    '提议者职务 (e.g. "省长"); 冗余 proposer_person_id (avoid JOIN); nullable';
COMMENT ON COLUMN government_commitment.is_measurable IS
    '是否可量化验证 (per docs/04 §3.7 门槛); nullable BOOLEAN';
COMMENT ON COLUMN government_commitment.measurement_basis IS
    'enum-style: INDICATOR_VALUE | PROJECT_COUNT | EVENT_COUNT | SELF_DECLARED';
COMMENT ON COLUMN government_commitment.lineage IS
    'per-row R3-E provenance; per docs/33 §3.2 sentinel';

-- ---------------------------------------------------------------------------
-- 5. commitment_progress (+ 3 cols)
-- ---------------------------------------------------------------------------

ALTER TABLE commitment_progress
    ADD COLUMN IF NOT EXISTS progress_value_lower NUMERIC,
    ADD COLUMN IF NOT EXISTS progress_value_upper NUMERIC,
    ADD COLUMN IF NOT EXISTS lineage JSONB;

COMMENT ON COLUMN commitment_progress.progress_value_lower IS
    '区间下限; nullable NUMERIC';
COMMENT ON COLUMN commitment_progress.progress_value_upper IS
    '区间上限; nullable NUMERIC';
COMMENT ON COLUMN commitment_progress.lineage IS
    'per-row R3-E provenance; per docs/33 §3.2 sentinel';

-- ---------------------------------------------------------------------------
-- 6. Indexes (per docs/37 §3.1 sources 形态)
-- ---------------------------------------------------------------------------

CREATE INDEX IF NOT EXISTS idx_policy_document_hash_canonical
    ON policy_document (policy_hash_canonical)
    WHERE policy_hash_canonical IS NOT NULL;

CREATE INDEX IF NOT EXISTS idx_policy_document_lineage_gin
    ON policy_document USING gin (lineage jsonb_path_ops)
    WHERE lineage IS NOT NULL;

CREATE INDEX IF NOT EXISTS idx_policy_target_lineage_gin
    ON policy_target USING gin (lineage jsonb_path_ops)
    WHERE lineage IS NOT NULL;

CREATE INDEX IF NOT EXISTS idx_policy_measure_lineage_gin
    ON policy_measure USING gin (lineage jsonb_path_ops)
    WHERE lineage IS NOT NULL;

CREATE INDEX IF NOT EXISTS idx_government_commitment_lineage_gin
    ON government_commitment USING gin (lineage jsonb_path_ops)
    WHERE lineage IS NOT NULL;

CREATE INDEX IF NOT EXISTS idx_commitment_progress_lineage_gin
    ON commitment_progress USING gin (lineage jsonb_path_ops)
    WHERE lineage IS NOT NULL;

RESET search_path;

-- End of migration 009.