-- Migration 012 — S2.5-lite: inference_record + claim_evidence_link additive columns
--
-- Per docs/40 §2 (Stage 2 / S2.5 规划) + Cursor tasking 226 §SCHEMA.
-- 用户裁定 D (缩刀节奏) — 与 S2.1-lite (008) / S2.2-lite (009) / S2.3-lite (010) /
-- S2.4-lite (011) 同构.
--
-- 全部 ADD COLUMN IF NOT EXISTS — 无 FK 启用、无 EXCLUDE、无 DROP/RENAME、
-- 不动既有 inference_record / claim_evidence_link 表 (01-core.sql §915-928 +
-- §956-966)、不动 information_layer ENUM (4 态: FACT/DERIVED/INFERENCE/JUDGMENT,
-- per 01-core.sql §25-30)、不动 polarity CHECK 约束 (SUPPORTS/CONTRADICTS 双显锁定,
-- per docs/04 §3.9 防确认偏差)、不动 inference_layer_not_fact + inference_confidence_range
-- CHECK 约束、不动现有触发器 / observation_no_delete / source_document_no_delete。
--
-- 新增列总计: inference_record +8 / claim_evidence_link +5.
-- 评分/排名/总分字段 (score/rating/rank/total_score/confidence_score/credibility_score)
-- 红线: 一律不引入.
--
-- Per docs/33 §3.2 sentinel: lineage JSONB 是 is_demo 唯一落点;
-- 全 is_demo=true 时 lineage.is_demo = "true".
-- Per R3-E provenance: lineage 形状 = {chain_id, source_file_sha256,
-- source_file_url, extractor_version, is_demo}.
-- Per R12-A de-dupe: inference_hash_canonical / claim_evidence_hash_canonical 跨修订共享.
--
-- 反例守门 (per docs/40 §3.4 + docs/04 §3.9):
--   polarity_summary = SUPPORTED | CONTRADICTED | MIXED | UNCONTESTED
--   canonical_polarity 投影 SUPPORTS | CONTRADICTS (不动 schema CHECK)
--   评审层 + mart_claim_evidence_polarity_balance 守门 NO_CONTRADICTING_EVIDENCE

SET search_path = cegr, public;

-- ---------------------------------------------------------------------------
-- 1. inference_record (+ 8 cols)
-- ---------------------------------------------------------------------------

ALTER TABLE inference_record
    ADD COLUMN IF NOT EXISTS canonical_statement TEXT,
    ADD COLUMN IF NOT EXISTS canonical_layer TEXT,
    ADD COLUMN IF NOT EXISTS inference_method TEXT,
    ADD COLUMN IF NOT EXISTS inference_year INTEGER,
    ADD COLUMN IF NOT EXISTS lineage JSONB,
    ADD COLUMN IF NOT EXISTS inference_hash_canonical TEXT,
    ADD COLUMN IF NOT EXISTS polarity_summary TEXT,
    ADD COLUMN IF NOT EXISTS geo_entity_id UUID;

COMMENT ON COLUMN inference_record.canonical_statement IS
    '归一化陈述 (去"可能"/"或许"/"据估计"漂移); nullable TEXT';
COMMENT ON COLUMN inference_record.canonical_layer IS
    'enum-style 投影: INFERENCE | DERIVED | JUDGMENT (不动 schema information_layer ENUM, per docs/04 §3.1); nullable TEXT';
COMMENT ON COLUMN inference_record.inference_method IS
    'enum-style: L1_TREND | L2_PEER | L3_CONDITIONAL | L4_PANEL_FE | L5_EVENT | L6_DID | L7_SYNTHETIC | OTHER (per docs/06 §4 L1-L7); nullable TEXT';
COMMENT ON COLUMN inference_record.inference_year IS
    '推断适用年份 (avoid JOIN date_part); nullable INTEGER';
COMMENT ON COLUMN inference_record.lineage IS
    'per-row R3-E provenance: {chain_id, source_file_sha256, source_file_url, extractor_version, is_demo}; is_demo sentinel per docs/33 §3.2';
COMMENT ON COLUMN inference_record.inference_hash_canonical IS
    '同一推断跨修订 stable SHA (per R12-A de-dupe); nullable TEXT';
COMMENT ON COLUMN inference_record.polarity_summary IS
    'enum-style: SUPPORTED | CONTRADICTED | MIXED | UNCONTESTED; nullable TEXT; 反例守门投影';
COMMENT ON COLUMN inference_record.geo_entity_id IS
    '推断适用范围 (per RegionCard 默认显示); nullable UUID; FK → geo_entity(id) 启用推迟';

-- ---------------------------------------------------------------------------
-- 2. claim_evidence_link (+ 5 cols)
-- ---------------------------------------------------------------------------

ALTER TABLE claim_evidence_link
    ADD COLUMN IF NOT EXISTS canonical_polarity TEXT,
    ADD COLUMN IF NOT EXISTS evidence_strength TEXT,
    ADD COLUMN IF NOT EXISTS lineage JSONB,
    ADD COLUMN IF NOT EXISTS claim_evidence_hash_canonical TEXT,
    ADD COLUMN IF NOT EXISTS geo_entity_id UUID;

COMMENT ON COLUMN claim_evidence_link.canonical_polarity IS
    'enum-style 投影: SUPPORTS | CONTRADICTS (不动 schema polarity CHECK, per docs/04 §3.9 双显锁定); nullable TEXT';
COMMENT ON COLUMN claim_evidence_link.evidence_strength IS
    'enum-style: STRONG | MODERATE | WEAK | UNRATED; 不数值化 (per docs/06 §6.6 红线); nullable TEXT';
COMMENT ON COLUMN claim_evidence_link.lineage IS
    'per-row R3-E provenance: {chain_id, source_file_sha256, source_file_url, extractor_version, is_demo}';
COMMENT ON COLUMN claim_evidence_link.claim_evidence_hash_canonical IS
    '同一关联跨修订 stable SHA (per R12-A de-dupe); nullable TEXT';
COMMENT ON COLUMN claim_evidence_link.geo_entity_id IS
    '关联适用范围 (UI 按区域过滤); nullable UUID; FK → geo_entity(id) 启用推迟';

-- ---------------------------------------------------------------------------
-- 3. Indexes (per docs/40 §3.1 + S2.4-lite 011 平行)
-- ---------------------------------------------------------------------------

CREATE INDEX IF NOT EXISTS idx_inference_canonical_layer
    ON inference_record (canonical_layer)
    WHERE canonical_layer IS NOT NULL;

CREATE INDEX IF NOT EXISTS idx_inference_method
    ON inference_record (inference_method)
    WHERE inference_method IS NOT NULL;

CREATE INDEX IF NOT EXISTS idx_inference_hash_canonical
    ON inference_record (inference_hash_canonical)
    WHERE inference_hash_canonical IS NOT NULL;

CREATE INDEX IF NOT EXISTS idx_inference_lineage_gin
    ON inference_record USING gin (lineage jsonb_path_ops)
    WHERE lineage IS NOT NULL;

CREATE INDEX IF NOT EXISTS idx_claim_evidence_canonical_polarity
    ON claim_evidence_link (canonical_polarity)
    WHERE canonical_polarity IS NOT NULL;

CREATE INDEX IF NOT EXISTS idx_claim_evidence_hash_canonical
    ON claim_evidence_link (claim_evidence_hash_canonical)
    WHERE claim_evidence_hash_canonical IS NOT NULL;

CREATE INDEX IF NOT EXISTS idx_claim_evidence_lineage_gin
    ON claim_evidence_link USING gin (lineage jsonb_path_ops)
    WHERE lineage IS NOT NULL;

RESET search_path;

-- End of migration 012.