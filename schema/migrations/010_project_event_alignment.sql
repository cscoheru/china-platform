-- Migration 010 — S2.3-lite: project_event additive columns
--
-- Per docs/38 §2.1 (Stage 2 / S2.3 规划) + Cursor tasking 204 §SCHEMA.
-- 用户裁定 D (缩刀节奏) — 与 S2.1-lite (008) / S2.2-lite (009) 同构.
--
-- 全部 ADD COLUMN IF NOT EXISTS — 无 FK 启用、无 EXCLUDE、无 DROP/RENAME、
-- 不动既有 project_status 五态机 ENUM (per docs/04 §3.8)、不动现有触发器.
-- 与既有 project_event 表 (01-core.sql §785-798) 严格对齐.
--
-- 新增列总计: 11 列.
-- 评分/排名/总分字段 (score/rating/rank/total_score) 红线: 一律不引入.
--
-- Per docs/33 §3.2 sentinel: lineage JSONB 是 is_demo 唯一落点;
-- 全 is_demo=true 时 lineage.is_demo = "true".
-- Per R3-E provenance: lineage 形状 = {chain_id, source_file_sha256,
-- source_file_url, extractor_version, is_demo}.
-- Per R12-A de-dupe: project_hash_canonical 跨事件共享 (同一项目 N 个 event).

SET search_path = cegr, public;

-- ---------------------------------------------------------------------------
-- 1. project_event (+ 11 cols)
-- ---------------------------------------------------------------------------

ALTER TABLE project_event
    ADD COLUMN IF NOT EXISTS canonical_project_name TEXT,
    ADD COLUMN IF NOT EXISTS project_name_en TEXT,
    ADD COLUMN IF NOT EXISTS project_class TEXT,
    ADD COLUMN IF NOT EXISTS status_year INTEGER,
    ADD COLUMN IF NOT EXISTS lineage JSONB,
    ADD COLUMN IF NOT EXISTS project_hash_canonical TEXT,
    ADD COLUMN IF NOT EXISTS investment_currency_canonical TEXT,
    ADD COLUMN IF NOT EXISTS expected_output_text TEXT,
    ADD COLUMN IF NOT EXISTS delay_reason TEXT,
    ADD COLUMN IF NOT EXISTS completion_year_planned INTEGER,
    ADD COLUMN IF NOT EXISTS completion_year_actual INTEGER;

COMMENT ON COLUMN project_event.canonical_project_name IS
    '归一化项目名 (去批文号/版本后缀); 与 policy_document.canonical_title 同模式';
COMMENT ON COLUMN project_event.project_name_en IS
    '英文渲染 (国际 cross-ref); nullable TEXT';
COMMENT ON COLUMN project_event.project_class IS
    'enum-style: MANUFACTURING | INFRASTRUCTURE | REAL_ESTATE | TECH | ENERGY | AGRICULTURE | OTHER; 不引入 schema ENUM (per docs/38 §10.2)';
COMMENT ON COLUMN project_event.status_year IS
    '从 event_date 提取 (avoid JOIN to date_part)';
COMMENT ON COLUMN project_event.lineage IS
    'per-row R3-E provenance: {chain_id, source_file_sha256, source_file_url, extractor_version, is_demo}; is_demo sentinel per docs/33 §3.2';
COMMENT ON COLUMN project_event.project_hash_canonical IS
    '同一项目跨 event 共享的 stable SHA (per R12-A de-dupe); nullable TEXT';
COMMENT ON COLUMN project_event.investment_currency_canonical IS
    '归一化币种 (avoid "亿元" vs "亿元(本币)" vs "RMB" drift); nullable TEXT';
COMMENT ON COLUMN project_event.expected_output_text IS
    '期望产出 (自然语言; 不评分); nullable TEXT';
COMMENT ON COLUMN project_event.delay_reason IS
    '延期原因 (仅延期 event 填; 其余 NULL); nullable TEXT';
COMMENT ON COLUMN project_event.completion_year_planned IS
    '计划达产年 (nullable INTEGER)';
COMMENT ON COLUMN project_event.completion_year_actual IS
    '实际达产年 (per AT_CAPACITY event; nullable INTEGER)';

-- ---------------------------------------------------------------------------
-- 2. Indexes (per docs/38 §3.1 sources 形态)
-- ---------------------------------------------------------------------------

CREATE INDEX IF NOT EXISTS idx_project_event_hash_canonical
    ON project_event (project_hash_canonical)
    WHERE project_hash_canonical IS NOT NULL;

CREATE INDEX IF NOT EXISTS idx_project_event_lineage_gin
    ON project_event USING gin (lineage jsonb_path_ops)
    WHERE lineage IS NOT NULL;

CREATE INDEX IF NOT EXISTS idx_project_event_class
    ON project_event (project_class)
    WHERE project_class IS NOT NULL;

CREATE INDEX IF NOT EXISTS idx_project_event_status_year
    ON project_event (status_year)
    WHERE status_year IS NOT NULL;

RESET search_path;

-- End of migration 010.