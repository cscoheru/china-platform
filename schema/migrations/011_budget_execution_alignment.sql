-- Migration 011 — S2.4-lite: budget_allocation + budget_execution additive columns
--
-- Per docs/39 §2 (Stage 2 / S2.4 规划) + Cursor tasking 218 §SCHEMA.
-- 用户裁定 D (缩刀节奏) — 与 S2.1-lite (008) / S2.2-lite (009) / S2.3-lite (010) 同构.
--
-- 全部 ADD COLUMN IF NOT EXISTS — 无 FK 启用、无 EXCLUDE、无 DROP/RENAME、
-- 不动既有 budget_allocation / budget_execution 表 (01-core.sql §804-828)、
-- 不动现有触发器 / observation_no_delete / source_document_no_delete.
--
-- 新增列总计: budget_allocation +8 / budget_execution +7.
-- 评分/排名/总分字段 (score/rating/rank/total_score/execution_score) 红线: 一律不引入.
--
-- Per docs/33 §3.2 sentinel: lineage JSONB 是 is_demo 唯一落点;
-- 全 is_demo=true 时 lineage.is_demo = "true".
-- Per R3-E provenance: lineage 形状 = {chain_id, source_file_sha256,
-- source_file_url, extractor_version, is_demo}.
-- Per R12-A de-dupe: budget_hash_canonical 跨 execution 共享 (同一 alloc N 个 execution).
--
-- 执行率口径 (per docs/39 §2.4):
--   execution_rate_period   = mart 派生 (executed / allocated)
--   execution_rate_reported = 源站报送 (既有 NUMERIC 列, 不动)
-- 双显由 mart 负责 (per docs/39 §3.3); 本 migration 不加 CHECK 约束 (容许灾年超额执行).

SET search_path = cegr, public;

-- ---------------------------------------------------------------------------
-- 1. budget_allocation (+ 8 cols)
-- ---------------------------------------------------------------------------

ALTER TABLE budget_allocation
    ADD COLUMN IF NOT EXISTS canonical_category TEXT,
    ADD COLUMN IF NOT EXISTS canonical_unit TEXT,
    ADD COLUMN IF NOT EXISTS allocation_currency_canonical TEXT,
    ADD COLUMN IF NOT EXISTS budget_class TEXT,
    ADD COLUMN IF NOT EXISTS fiscal_year_int INTEGER,
    ADD COLUMN IF NOT EXISTS lineage JSONB,
    ADD COLUMN IF NOT EXISTS budget_hash_canonical TEXT,
    ADD COLUMN IF NOT EXISTS progress_note TEXT;

COMMENT ON COLUMN budget_allocation.canonical_category IS
    '归一化类目 (去"教育"/"教育支出"drift); nullable TEXT';
COMMENT ON COLUMN budget_allocation.canonical_unit IS
    '归一化单位 enum-style: CNY_100M | CNY_10K | CNY | OTHER_NOTE; nullable TEXT';
COMMENT ON COLUMN budget_allocation.allocation_currency_canonical IS
    '归一化币种 (CNY / HKD / USD 锚定); nullable TEXT';
COMMENT ON COLUMN budget_allocation.budget_class IS
    'enum-style: GENERAL | SPECIAL | BOND | SOCIAL_SECURITY | TRANSFER | OTHER; 不引入 schema ENUM (per docs/38 §10.2 平行)';
COMMENT ON COLUMN budget_allocation.fiscal_year_int IS
    '从 fiscal_year 投影 (避免 mart SELECT JOIN 年提取)';
COMMENT ON COLUMN budget_allocation.lineage IS
    'per-row R3-E provenance: {chain_id, source_file_sha256, source_file_url, extractor_version, is_demo}; is_demo sentinel per docs/33 §3.2';
COMMENT ON COLUMN budget_allocation.budget_hash_canonical IS
    '同一笔预算跨 execution 共享的 stable SHA (per R12-A de-dupe); nullable TEXT';
COMMENT ON COLUMN budget_allocation.progress_note IS
    '自由文本说明 (不评分); nullable TEXT';

-- ---------------------------------------------------------------------------
-- 2. budget_execution (+ 7 cols)
-- ---------------------------------------------------------------------------

ALTER TABLE budget_execution
    ADD COLUMN IF NOT EXISTS canonical_unit TEXT,
    ADD COLUMN IF NOT EXISTS execution_currency_canonical TEXT,
    ADD COLUMN IF NOT EXISTS execution_date DATE,
    ADD COLUMN IF NOT EXISTS fiscal_year_int INTEGER,
    ADD COLUMN IF NOT EXISTS lineage JSONB,
    ADD COLUMN IF NOT EXISTS execution_hash_canonical TEXT,
    ADD COLUMN IF NOT EXISTS variance_reason TEXT;

COMMENT ON COLUMN budget_execution.canonical_unit IS
    '归一化单位 (与 alloc 同口径; nullable TEXT)';
COMMENT ON COLUMN budget_execution.execution_currency_canonical IS
    '归一化币种 (与 alloc 同口径)';
COMMENT ON COLUMN budget_execution.execution_date IS
    '自由填具体执行日期 (避免每行 JOIN calendar_period); nullable DATE';
COMMENT ON COLUMN budget_execution.fiscal_year_int IS
    '从 execution_period 投影; 用于 mart 过滤';
COMMENT ON COLUMN budget_execution.lineage IS
    'per-row R3-E provenance: {chain_id, source_file_sha256, source_file_url, extractor_version, is_demo}; is_demo sentinel per docs/33 §3.2';
COMMENT ON COLUMN budget_execution.execution_hash_canonical IS
    '同一笔执行的 stable SHA (per R12-A de-dupe); nullable TEXT';
COMMENT ON COLUMN budget_execution.variance_reason IS
    '偏差原因 (仅执行率偏离 [0, 0.8] ∪ [1.2, ∞] 填; 其余 NULL); nullable TEXT';

-- ---------------------------------------------------------------------------
-- 3. Indexes (per docs/39 §3.1 + S2.3 平行)
-- ---------------------------------------------------------------------------

CREATE INDEX IF NOT EXISTS idx_budget_alloc_canonical_category
    ON budget_allocation (canonical_category)
    WHERE canonical_category IS NOT NULL;

CREATE INDEX IF NOT EXISTS idx_budget_alloc_class
    ON budget_allocation (budget_class)
    WHERE budget_class IS NOT NULL;

CREATE INDEX IF NOT EXISTS idx_budget_alloc_hash_canonical
    ON budget_allocation (budget_hash_canonical)
    WHERE budget_hash_canonical IS NOT NULL;

CREATE INDEX IF NOT EXISTS idx_budget_alloc_lineage_gin
    ON budget_allocation USING gin (lineage jsonb_path_ops)
    WHERE lineage IS NOT NULL;

CREATE INDEX IF NOT EXISTS idx_budget_exec_hash_canonical
    ON budget_execution (execution_hash_canonical)
    WHERE execution_hash_canonical IS NOT NULL;

CREATE INDEX IF NOT EXISTS idx_budget_exec_lineage_gin
    ON budget_execution USING gin (lineage jsonb_path_ops)
    WHERE lineage IS NOT NULL;

CREATE INDEX IF NOT EXISTS idx_budget_exec_date
    ON budget_execution (execution_date)
    WHERE execution_date IS NOT NULL;

RESET search_path;

-- End of migration 011.