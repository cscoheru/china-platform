-- ============================================================================
-- 中国经济与区域治理研究平台 — Stage 0 核心 Schema
-- Database: PostgreSQL 16 + PostGIS 3.4
-- Schema:   cegr (China Economy & Governance Research)
-- 文档依据: PRD 第 5 章 + 评审 B-02/B-03 修正
-- 已验证: 在全新 PostgreSQL 16 + PostGIS 3.4 实例上可执行
-- ============================================================================

-- 扩展（按依赖顺序）
CREATE EXTENSION IF NOT EXISTS postgis;       -- PostGIS 几何
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";   -- UUID 生成
CREATE EXTENSION IF NOT EXISTS pg_trgm;       -- 模糊匹配
CREATE EXTENSION IF NOT EXISTS btree_gist;    -- 关键：GiST 排他约束需要此扩展
-- CREATE EXTENSION IF NOT EXISTS vector;     -- pgvector，Stage 4 再启用

-- Schema 命名空间
CREATE SCHEMA IF NOT EXISTS cegr;
SET search_path = cegr, public;

-- ============================================================================
-- 0. 通用枚举与类型
-- ============================================================================

-- 四层信息模型 (per PRD 3.1)
CREATE TYPE information_layer AS ENUM (
    'FACT',        -- 来源直接披露的事实/数值
    'DERIVED',     -- 公开公式计算
    'INFERENCE',   -- 模型/同类比较/事件研究推断
    'JUDGMENT'     -- 研究者基于证据的判断
);

-- 来源等级 (per PRD 3.2)
CREATE TYPE source_level AS ENUM (
    'S0',  -- 法定或一手官方（已平台核验）
    'S1',  -- 国际组织/学术
    'S2',  -- 商业数据库
    'S3',  -- 主流媒体/公开报告
    'S4'   -- 社交/自媒体（仅线索）
);

-- 上传者声明的来源等级（必须经平台核验才升为 S0；默认 'UNVERIFIED'）
CREATE TYPE source_verification_status AS ENUM (
    'UNVERIFIED',  -- 上传者声明，未核验
    'PENDING',     -- 等待平台核验
    'VERIFIED',    -- 已核验，可标 S0
    'REJECTED'     -- 核验拒绝
);

-- 提取方式 (per PRD 3.3 / 9.3)
CREATE TYPE extraction_method AS ENUM (
    'API',
    'HTML_PARSE',
    'EXCEL_PARSE',
    'PDF_TEXT',
    'PDF_OCR',
    'IMAGE_OCR',     -- 扫描图像（JPG/PNG/TIFF）
    'CSV_PARSE',
    'MANUAL_UPLOAD'  -- 用户上传
);

-- 观测值修订状态
CREATE TYPE observation_status AS ENUM (
    'PRELIMINARY',  -- 初值
    'REVISED',      -- 修订值
    'FINAL'         -- 终值
);

-- 行政区划层级
CREATE TYPE geo_level AS ENUM (
    'COUNTRY',
    'PROVINCE',
    'PREFECTURE',     -- 地级市/地区/自治州/盟
    'COUNTY',
    'TOWNSHIP'
);

-- 行政区划变化类型
CREATE TYPE boundary_change_type AS ENUM (
    'CREATED', 'MERGED', 'SPLIT', 'ABOLISHED',
    'RENAMED', 'UPGRADED', 'DOWNGRADED', 'REASSIGNED'
);

-- 地域关系类型（per PRD 5.1）
CREATE TYPE geo_relation_type AS ENUM (
    'PART_OF',          -- 从属（如市属于省）
    'CONTAINS',         -- 包含
    'BORDERS',          -- 接壤
    'MERGED_INTO',      -- 合并入
    'SPLIT_FROM',       -- 拆分自
    'ECONOMIC_REGION'   -- 经济区归属
);

-- 比较基础
-- R3-E: 移除 'Q2_ONLY' — 不再以"仅 Q2 单季"作为强制口径；
-- GDP/居民收入 等季度数据被标为半年累计时，通过 caveat 字段 + period metadata
-- 显式建模，而非用 enum 值强制约束。
CREATE TYPE comparison_basis AS ENUM (
    'NOMINAL',                -- 当年价
    'REAL',                   -- 不变价
    'CHAIN',                  -- 链式
    'H1_ACCUMULATED',         -- 真半年累计
    'CUMULATIVE',             -- 累计口径
    'INSTANTANEOUS',          -- 时点
    'NEEDS_VERIFICATION'      -- 待核验（不能自动判定）
);

-- 政策文件类型
CREATE TYPE policy_doc_type AS ENUM (
    'GOVERNMENT_WORK_REPORT',
    'FIVE_YEAR_PLAN',
    'BUDGET_REPORT',
    'FINAL_ACCOUNT',
    'POLICY_DOCUMENT',
    'MEETING_MINUTES',
    'INSPECTION_REPORT',
    'AUDIT_REPORT',
    'INFORMATION_DISCLOSURE',
    'OTHER'
);

-- 承诺状态
CREATE TYPE commitment_status AS ENUM (
    'PROPOSED', 'UNDER_WAY', 'PARTIALLY_DONE',
    'FULFILLED', 'BROKEN', 'CANCELLED'
);

-- 项目状态 (五态机)
CREATE TYPE project_status AS ENUM (
    'ANNOUNCED', 'SIGNED', 'STARTED', 'PRODUCING', 'AT_CAPACITY'
);

-- 分析方法
CREATE TYPE analysis_method AS ENUM (
    'TREND', 'PEER_COMPARE', 'CONDITIONAL',
    'PANEL_FE', 'EVENT_STUDY', 'DID', 'SYNTHETIC_CTRL'
);

-- ============================================================================
-- 1. 地理与时间 (per PRD 5.1)
-- ============================================================================

CREATE TABLE geo_entity (
    id                  UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    canonical_name      TEXT NOT NULL,
    canonical_name_en   TEXT,
    level               geo_level NOT NULL,
    parent_id           UUID REFERENCES geo_entity(id),
    created_at          TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at          TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    notes               TEXT,
    CONSTRAINT geo_entity_name_level_unique UNIQUE (canonical_name, level)
);

CREATE INDEX idx_geo_entity_canonical ON geo_entity (canonical_name);
CREATE INDEX idx_geo_entity_parent    ON geo_entity (parent_id);
CREATE INDEX idx_geo_entity_level     ON geo_entity (level);

COMMENT ON TABLE geo_entity IS '逻辑地理实体；不同时期代码见 geo_code_version';

CREATE TABLE geo_code_version (
    id                  UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    geo_entity_id       UUID NOT NULL REFERENCES geo_entity(id) ON DELETE RESTRICT,
    admin_code          TEXT,
    stat_code           TEXT,
    iso_code            TEXT,
    valid_from          DATE NOT NULL,
    valid_to            DATE,
    source_id           UUID NOT NULL,  -- FK 由后置 ALTER 添加；评审六-7 强制来源
    boundary_status     TEXT DEFAULT 'CURRENT_BOUNDARY',
    geometry            GEOMETRY(MultiPolygon, 4326),
    created_at          TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    CONSTRAINT geo_code_version_dates_valid CHECK (valid_from <= valid_to OR valid_to IS NULL),
    EXCLUDE USING gist (
        geo_entity_id WITH =,
        daterange(valid_from, COALESCE(valid_to, '9999-12-31'::date), '[]') WITH &&
    )
);

CREATE INDEX idx_geo_code_version_entity  ON geo_code_version (geo_entity_id);
CREATE INDEX idx_geo_code_version_admin   ON geo_code_version (admin_code);
CREATE INDEX idx_geo_code_version_stat    ON geo_code_version (stat_code);
CREATE INDEX idx_geo_code_version_valid   ON geo_code_version (valid_from, valid_to);

COMMENT ON TABLE geo_code_version IS '行政区划代码版本（时变）；每段时期一个版本';

-- 新增：地域时变关系 (per PRD 5.1 / 评审 B-03)
CREATE TABLE geo_relation (
    id                  UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    geo_entity_id       UUID NOT NULL REFERENCES geo_entity(id) ON DELETE RESTRICT,
    related_entity_id   UUID NOT NULL REFERENCES geo_entity(id) ON DELETE RESTRICT,
    relation_type       geo_relation_type NOT NULL,
    valid_from          DATE NOT NULL,
    valid_to            DATE,
    source_id           UUID NOT NULL,  -- FK 由后置 ALTER 添加（source_document 晚于本表创建）
    created_at          TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    CONSTRAINT geo_relation_dates_valid CHECK (valid_from <= valid_to OR valid_to IS NULL),
    CONSTRAINT geo_relation_not_self CHECK (geo_entity_id <> related_entity_id),
    -- 评审六-8：允许同期不同 relation_type 并存（如同时 PART_OF 湖北省 + 位于长江经济带）
    -- PART_OF 单独保证"同一时期单一父级、期间不重叠"（部分排他约束）
    CONSTRAINT geo_relation_partof_single_parent EXCLUDE USING gist (
        geo_entity_id WITH =,
        daterange(valid_from, COALESCE(valid_to, '9999-12-31'::date), '[]') WITH &&
    ) WHERE (relation_type = 'PART_OF'),
    -- 精确重复行仍被拒绝（自然键）
    CONSTRAINT geo_relation_natural_key UNIQUE (geo_entity_id, related_entity_id, relation_type, valid_from)
);

CREATE INDEX idx_geo_relation_entity    ON geo_relation (geo_entity_id);
CREATE INDEX idx_geo_relation_related   ON geo_relation (related_entity_id);

COMMENT ON TABLE geo_relation IS '地域时变关系（从属/接壤/合并入/拆分自/经济区）；用于 PRD 5.1';

CREATE TABLE boundary_change_event (
    id                  UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    event_date          DATE NOT NULL,
    change_type         boundary_change_type NOT NULL,
    affected_entity_ids UUID[] NOT NULL,
    predecessor_ids     UUID[],
    successor_ids       UUID[],
    description         TEXT NOT NULL,
    source_id           UUID NOT NULL,  -- FK 由后置 ALTER 添加；评审六-7 强制来源
    created_at          TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    CONSTRAINT boundary_change_has_affected CHECK (array_length(affected_entity_ids, 1) >= 1)
);

CREATE INDEX idx_boundary_change_date  ON boundary_change_event (event_date);

CREATE TABLE calendar_period (
    id                  UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    period_label        TEXT NOT NULL UNIQUE,
    period_type         TEXT NOT NULL,
    start_date          DATE NOT NULL,
    end_date            DATE NOT NULL,
    fy_label            TEXT,
    raw_label           TEXT,        -- 原始来源文本（如 "1-6月"/"上半年"）
    period_basis        comparison_basis DEFAULT 'INSTANTANEOUS',
    CONSTRAINT period_dates_valid CHECK (start_date <= end_date)
);

CREATE INDEX idx_calendar_period_dates ON calendar_period (start_date, end_date);

COMMENT ON TABLE calendar_period IS '标准日历期；区分统计期、原始来源文本与口径';

-- ============================================================================
-- 2. 指标与观测 (per PRD 5.2)
-- ============================================================================

CREATE TABLE indicator_definition (
    id                       UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    canonical_name           TEXT NOT NULL,
    canonical_name_en        TEXT,
    short_code               TEXT UNIQUE,
    description              TEXT,
    unit_canonical           TEXT NOT NULL,             -- "亿元"/"%" / "%ppt"
    unit_category            TEXT,                      -- 'CURRENCY'/'PERCENT'/'PERCENTAGE_POINT'/'COUNT'/'INDEX'
    frequency                TEXT NOT NULL,
    price_basis              comparison_basis,
    seasonally_adjusted      BOOLEAN DEFAULT FALSE,
    is_cumulative            BOOLEAN DEFAULT FALSE,
    aggregation_method       TEXT,
    additivity               TEXT,
    comparability_note       TEXT,
    classification_version   TEXT,
    formula                  TEXT,
    -- PRD 评审 B-03 增补：地域范围
    geo_scope_default        geo_level,                 -- 指标默认层级
    min_geo_id               UUID REFERENCES geo_entity(id),  -- 最小适用地域
    max_geo_id               UUID REFERENCES geo_entity(id),  -- 最大适用地域
    created_at               TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at               TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_indicator_canonical ON indicator_definition (canonical_name);

COMMENT ON TABLE indicator_definition IS '指标定义（含地域范围）；历史口径走 indicator_methodology_version';

CREATE TABLE indicator_alias (
    id                  UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    indicator_id        UUID NOT NULL REFERENCES indicator_definition(id) ON DELETE RESTRICT,
    alias               TEXT NOT NULL,
    source_id           UUID,  -- 之后 ALTER TABLE 加 FK；不同源的别名单独登记
    language            TEXT DEFAULT 'zh',
    UNIQUE (indicator_id, alias, source_id)
);

CREATE INDEX idx_indicator_alias_alias ON indicator_alias (alias);

CREATE TABLE indicator_methodology_version (
    id                  UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    indicator_id        UUID NOT NULL REFERENCES indicator_definition(id) ON DELETE RESTRICT,
    version_label       TEXT NOT NULL,
    valid_from          DATE NOT NULL,
    valid_to            DATE,
    change_summary      TEXT NOT NULL,
    impact_note         TEXT,
    source_id           UUID NOT NULL,  -- FK 由后置 ALTER 添加；评审六-7 强制来源
    created_at          TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    CONSTRAINT indicator_mv_dates_valid CHECK (valid_from <= valid_to OR valid_to IS NULL),
    -- 评审六-5：为 observation 的复合外键 (methodology_version_id, indicator_id) 提供目标键
    CONSTRAINT indicator_mv_id_indicator_unique UNIQUE (id, indicator_id),
    EXCLUDE USING gist (
        indicator_id WITH =,
        daterange(valid_from, COALESCE(valid_to, '9999-12-31'::date), '[]') WITH &&
    )
);

CREATE INDEX idx_indicator_mv_indicator ON indicator_methodology_version (indicator_id);

COMMENT ON TABLE indicator_methodology_version IS '指标方法版本（口径时变）';

-- 来源文档（必须先建；外键引用）
CREATE TABLE source_document (
    id                       UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    source_registry_id       UUID NOT NULL,   -- per F-2: 每份来源文档必须回源到 source_registry
    source_level             source_level NOT NULL,
    verification_status      source_verification_status NOT NULL DEFAULT 'UNVERIFIED',
    title                    TEXT NOT NULL,
    publisher                TEXT NOT NULL,
    publication_date         DATE,
    url                      TEXT,
    file_path                TEXT,
    file_hash_sha256         TEXT NOT NULL,
    file_format              TEXT,
    file_size_bytes          BIGINT,
    language                 TEXT DEFAULT 'zh',
    extraction_method        extraction_method,
    caveat_text              TEXT,
    copyright_note           TEXT,
    uploader_id              TEXT,                 -- 若为上传，登记上传者
    created_at               TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    CONSTRAINT source_doc_has_hash CHECK (file_hash_sha256 IS NOT NULL),
    CONSTRAINT source_doc_hash_format CHECK (file_hash_sha256 ~ '^[a-f0-9]{64}$'),
    CONSTRAINT source_doc_size_positive CHECK (file_size_bytes IS NULL OR file_size_bytes > 0)
);

CREATE INDEX idx_source_doc_publisher ON source_document (publisher);
CREATE INDEX idx_source_doc_level     ON source_document (source_level);
CREATE INDEX idx_source_doc_pubdate   ON source_document (publication_date);
CREATE INDEX idx_source_doc_hash      ON source_document (file_hash_sha256);
CREATE INDEX idx_source_doc_verification ON source_document (verification_status);

COMMENT ON TABLE source_document IS '来源文档（原始不可变）；caveat_text 记录标题/数据不一致等关键解析说明';

-- 来源登记（必须先建）
CREATE TABLE source_registry (
    id                  UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    domain              TEXT NOT NULL,
    organization        TEXT NOT NULL,
    category            TEXT NOT NULL,
    primary_url         TEXT NOT NULL,
    backup_urls         TEXT[],
    update_frequency    TEXT,
    auth_note           TEXT,
    access_method       extraction_method,
    historical_coverage TEXT,
    stability_note      TEXT,
    failure_handling    TEXT,
    enabled             BOOLEAN DEFAULT TRUE,
    created_at          TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at          TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_source_registry_domain   ON source_registry (domain);
CREATE INDEX idx_source_registry_enabled ON source_registry (enabled);
CREATE UNIQUE INDEX idx_source_registry_url ON source_registry (primary_url);

-- 来源定位（多形态）
CREATE TABLE source_location (
    id                  UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    source_document_id  UUID NOT NULL REFERENCES source_document(id) ON DELETE RESTRICT,
    sheet_name          TEXT,
    page_number         INTEGER,
    table_index         INTEGER,
    cell_range          TEXT,
    bbox                JSONB,
    section_heading     TEXT,
    paragraph_index     INTEGER,
    context_quote       TEXT,
    row_locator         TEXT,
    created_at          TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    -- 评审六-9：cell_range-only 与 bbox-only 也是有效定位
    CONSTRAINT source_loc_has_locator CHECK (
        sheet_name IS NOT NULL OR page_number IS NOT NULL OR
        table_index IS NOT NULL OR paragraph_index IS NOT NULL OR
        section_heading IS NOT NULL OR row_locator IS NOT NULL OR
        cell_range IS NOT NULL OR bbox IS NOT NULL
    ),
    -- 评审六-6：为 observation/revision 的复合外键 (source_location_id, source_id) 提供目标键
    CONSTRAINT source_loc_id_doc_unique UNIQUE (id, source_document_id),
    CONSTRAINT source_loc_context_length CHECK (
        context_quote IS NULL OR (length(context_quote) BETWEEN 5 AND 500)
    )
);

CREATE INDEX idx_source_loc_doc ON source_location (source_document_id);

COMMENT ON TABLE source_location IS '来源定位（多形态：sheet/page/cell/段落/章节）';

-- 抓取运行
CREATE TABLE ingestion_run (
    id                  UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    source_registry_id  UUID NOT NULL REFERENCES source_registry(id) ON DELETE RESTRICT,
    started_at          TIMESTAMPTZ NOT NULL,
    finished_at         TIMESTAMPTZ,
    status              TEXT NOT NULL,
    records_extracted   INTEGER,
    records_inserted    INTEGER,
    records_updated     INTEGER,
    error_log           TEXT,
    triggered_by        TEXT,
    created_at          TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    CONSTRAINT ingestion_run_status_valid CHECK (status IN ('RUNNING','SUCCESS','PARTIAL','FAILED')),
    CONSTRAINT ingestion_run_counts_valid CHECK (
        records_extracted IS NULL OR records_extracted >= 0
    )
);

CREATE INDEX idx_ingestion_run_source  ON ingestion_run (source_registry_id);
CREATE INDEX idx_ingestion_run_status  ON ingestion_run (status);
CREATE INDEX idx_ingestion_run_started ON ingestion_run (started_at);

-- 现在补全 source_document / source_location / geo_code_version / indicator_methodology_version 等的外键
ALTER TABLE source_document
    ADD CONSTRAINT source_document_registry_fk
    FOREIGN KEY (source_registry_id) REFERENCES source_registry(id) ON DELETE RESTRICT;

ALTER TABLE geo_code_version
    ADD CONSTRAINT geo_code_version_source_fk
    FOREIGN KEY (source_id) REFERENCES source_document(id) ON DELETE RESTRICT;

ALTER TABLE geo_relation
    ADD CONSTRAINT geo_relation_source_fk
    FOREIGN KEY (source_id) REFERENCES source_document(id) ON DELETE RESTRICT;

ALTER TABLE boundary_change_event
    ADD CONSTRAINT boundary_change_source_fk
    FOREIGN KEY (source_id) REFERENCES source_document(id) ON DELETE RESTRICT;

ALTER TABLE indicator_alias
    ADD CONSTRAINT indicator_alias_source_fk
    FOREIGN KEY (source_id) REFERENCES source_document(id) ON DELETE RESTRICT;

ALTER TABLE indicator_methodology_version
    ADD CONSTRAINT indicator_mv_source_fk
    FOREIGN KEY (source_id) REFERENCES source_document(id) ON DELETE RESTRICT;

-- 观测值（核心事实）
CREATE TABLE observation (
    id                       UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    indicator_id             UUID NOT NULL REFERENCES indicator_definition(id) ON DELETE RESTRICT,
    indicator_methodology_version_id UUID REFERENCES indicator_methodology_version(id) ON DELETE RESTRICT,
    geo_entity_id            UUID NOT NULL REFERENCES geo_entity(id) ON DELETE RESTRICT,
    geo_code_version_id      UUID NOT NULL REFERENCES geo_code_version(id) ON DELETE RESTRICT,
    calendar_period_id       UUID NOT NULL REFERENCES calendar_period(id) ON DELETE RESTRICT,
    value                    NUMERIC,
    raw_value                TEXT,                       -- 原始单元格文本（含 … — 等）
    is_imputed               BOOLEAN DEFAULT FALSE,
    missing_reason           TEXT,                       -- NOT_PUBLISHED / SUPPRESSED / SECTION_SKIPPED / OCR_FAILED ...
    unit                     TEXT,                       -- 可空：rate-only 行允许 NULL
    comparison_basis         comparison_basis DEFAULT 'NEEDS_VERIFICATION',
    value_type               information_layer NOT NULL DEFAULT 'FACT',
    status                   observation_status NOT NULL DEFAULT 'PRELIMINARY',
    source_id                UUID NOT NULL REFERENCES source_document(id) ON DELETE RESTRICT,
    source_location_id       UUID NOT NULL REFERENCES source_location(id) ON DELETE RESTRICT,  -- 评审 B-03 必填
    ingestion_run_id         UUID REFERENCES ingestion_run(id) ON DELETE RESTRICT,
    extracted_at             TIMESTAMPTZ,
    extraction_method        extraction_method,
    confidence               NUMERIC,                    -- 0-1
    notes                    TEXT,
    created_at               TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    created_by               TEXT,
    -- 自然键：indicator + methodology_version + geo + period + source（status 不参与）
    -- 评审 R3-F：状态变更只能走 observation_revision（append-only），禁止"修改 status 列
    --             就替换为不同指标/地区/时期的观测"。status 必须从自然键剔除。
    UNIQUE NULLS NOT DISTINCT (indicator_id, indicator_methodology_version_id, geo_entity_id,
            calendar_period_id, source_id),
    -- 评审六-6：source_id 必须与 source_location 所属 source_document 一致（复合外键）
    CONSTRAINT observation_loc_source_match
        FOREIGN KEY (source_location_id, source_id)
        REFERENCES source_location (id, source_document_id)
        ON DELETE RESTRICT,
    -- 评审六-5：methodology version 必须属于 observation 的 indicator（复合外键）
    CONSTRAINT observation_methodology_indicator_match
        FOREIGN KEY (indicator_methodology_version_id, indicator_id)
        REFERENCES indicator_methodology_version (id, indicator_id)
        ON DELETE RESTRICT,
    CONSTRAINT observation_confidence_range CHECK (confidence IS NULL OR confidence BETWEEN 0 AND 1),
    CONSTRAINT observation_missing_consistency CHECK (
        (value IS NULL AND missing_reason IS NOT NULL) OR
        (value IS NOT NULL AND missing_reason IS NULL) OR
        (value IS NULL AND is_imputed = TRUE)  -- 填补允许 NULL
    ),
    CONSTRAINT observation_unit_required CHECK (
        unit IS NOT NULL OR value IS NULL OR is_imputed = TRUE
    )
);

CREATE INDEX idx_observation_indicator     ON observation (indicator_id);
CREATE INDEX idx_observation_indicator_mv  ON observation (indicator_methodology_version_id);
CREATE INDEX idx_observation_geo           ON observation (geo_entity_id);
CREATE INDEX idx_observation_period        ON observation (calendar_period_id);
CREATE INDEX idx_observation_source        ON observation (source_id);
CREATE INDEX idx_observation_status        ON observation (status);
CREATE INDEX idx_observation_source_loc    ON observation (source_location_id);

COMMENT ON TABLE observation IS '观测值：包含 methodology_version + source 的自然键；source_location 必填';

-- 观测值修订（append-only）
CREATE TABLE observation_revision (
    id                  UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    observation_id      UUID NOT NULL REFERENCES observation(id) ON DELETE RESTRICT,
    revision_no         INTEGER NOT NULL CHECK (revision_no > 0),
    value               NUMERIC,
    raw_value           TEXT,
    unit                TEXT,
    missing_reason      TEXT,                       -- 评审六-4：修订可声明缺失
    status              observation_status NOT NULL,
    revision_date       DATE NOT NULL,
    revision_reason     TEXT,
    source_id           UUID NOT NULL REFERENCES source_document(id) ON DELETE RESTRICT,
    -- 评审六-4/六-6：修订自带定位；source_id 必须与该定位所属文档一致
    source_location_id  UUID NOT NULL REFERENCES source_location(id) ON DELETE RESTRICT,
    confidence          NUMERIC,                    -- 评审六-4：修订自带置信度
    created_at          TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    UNIQUE (observation_id, revision_no),
    CONSTRAINT observation_revision_loc_source_match
        FOREIGN KEY (source_location_id, source_id)
        REFERENCES source_location (id, source_document_id)
        ON DELETE RESTRICT,
    CONSTRAINT observation_revision_confidence_range
        CHECK (confidence IS NULL OR confidence BETWEEN 0 AND 1)
);

CREATE INDEX idx_observation_revision_obs ON observation_revision (observation_id);

COMMENT ON TABLE observation_revision IS '修订历史：append-only；删除 observation 不会清除修订';

-- 观测值质量标记
CREATE TABLE observation_quality_flag (
    id                  UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    observation_id      UUID NOT NULL REFERENCES observation(id) ON DELETE RESTRICT,
    flag_type           TEXT NOT NULL,
    severity            TEXT NOT NULL CHECK (severity IN ('INFO','WARN','BLOCK')),
    description         TEXT NOT NULL,
    resolved            BOOLEAN DEFAULT FALSE,
    resolved_by         TEXT,
    resolved_at         TIMESTAMPTZ,
    created_at          TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_obs_quality_obs           ON observation_quality_flag (observation_id);
CREATE INDEX idx_obs_quality_flag_type     ON observation_quality_flag (flag_type);
CREATE INDEX idx_obs_quality_unresolved    ON observation_quality_flag (resolved) WHERE resolved = FALSE;

-- ============================================================================
-- 3. 当前观测值视图（含 latest revision）— 评审 B-03 强制 + 返工六-4 重做
--    语义：
--      * 无任何 revision → 直接取 observation 字段；
--      * 存在 revision   → 值/单位/缺失原因/置信度/状态/来源/定位全部取自同一条
--                          最新 revision（value 为 NULL 就是 NULL，禁止回退旧值）。
-- ============================================================================

CREATE OR REPLACE VIEW v_current_observation AS
SELECT
    o.id,
    o.indicator_id,
    o.indicator_methodology_version_id,
    o.geo_entity_id,
    o.geo_code_version_id,
    o.calendar_period_id,
    CASE WHEN rev.id IS NULL THEN o.value ELSE rev.value END
                                                    AS current_value,
    CASE WHEN rev.id IS NULL THEN o.unit  ELSE rev.unit  END
                                                    AS current_unit,
    CASE WHEN rev.id IS NULL THEN o.status ELSE rev.status END
                                                    AS current_status,
    CASE WHEN rev.id IS NULL THEN o.missing_reason ELSE rev.missing_reason END
                                                    AS current_missing_reason,
    CASE WHEN rev.id IS NULL THEN o.confidence   ELSE rev.confidence END
                                                    AS current_confidence,
    CASE WHEN rev.id IS NULL THEN o.source_id   ELSE rev.source_id END
                                                    AS current_source_id,
    CASE WHEN rev.id IS NULL THEN o.source_location_id ELSE rev.source_location_id END
                                                    AS current_source_location_id,
    rev.revision_no                                 AS current_revision_no
FROM observation o
LEFT JOIN LATERAL (
    SELECT r.*
    FROM observation_revision r
    WHERE r.observation_id = o.id
    ORDER BY r.revision_no DESC
    LIMIT 1
) rev ON TRUE;

COMMENT ON VIEW v_current_observation IS '当前观测值：最新 revision 的全部字段整体生效（NULL 即 NULL，不回退）；无 revision 时回退 observation 本身';

CREATE OR REPLACE VIEW v_observation_with_evidence AS
SELECT
    cur.id,
    i.canonical_name        AS indicator,
    g.canonical_name        AS geo,
    gv.admin_code           AS admin_code,
    cp.period_label         AS period,
    cp.raw_label            AS period_raw_label,
    cur.current_value       AS value,
    cur.current_unit        AS unit,
    cur.current_status      AS status,
    o.value_type,
    o.comparison_basis,
    cur.current_missing_reason AS missing_reason,
    s.title                 AS source_title,
    s.url                   AS source_url,
    s.file_hash_sha256      AS source_hash,
    sl.sheet_name           AS sheet_name,
    sl.page_number          AS page_number,
    sl.row_locator          AS row_locator,
    sl.cell_range           AS cell_range,
    cur.current_confidence  AS confidence,
    o.is_imputed
FROM v_current_observation cur
JOIN observation o            ON o.id = cur.id
JOIN indicator_definition i  ON i.id = cur.indicator_id
JOIN geo_entity g            ON g.id = cur.geo_entity_id
JOIN geo_code_version gv     ON gv.id = cur.geo_code_version_id
JOIN calendar_period cp      ON cp.id = cur.calendar_period_id
JOIN source_document s       ON s.id = cur.current_source_id
JOIN source_location sl      ON sl.id = cur.current_source_location_id;

COMMENT ON VIEW v_observation_with_evidence IS '观测值+证据+最新修订视图；值/单位/来源/定位全部来自同一条最新 revision 或原 observation';

-- ============================================================================
-- 4. 人物与任期 (per PRD 5.3)
-- ============================================================================

CREATE TABLE person (
    id                  UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    canonical_name      TEXT NOT NULL,
    gender              TEXT,
    birth_year          INTEGER,
    ethnicity           TEXT,
    education_summary   TEXT,
    notes               TEXT,
    created_at          TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_person_canonical ON person (canonical_name);
CREATE INDEX idx_person_name_trgm ON person USING gin (canonical_name gin_trgm_ops);

COMMENT ON TABLE person IS '人物：仅收集公开履历；不收集家庭/联系方式/住址';

CREATE TABLE person_name_alias (
    id                  UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    person_id           UUID NOT NULL REFERENCES person(id) ON DELETE RESTRICT,
    alias               TEXT NOT NULL,
    alias_type          TEXT,
    UNIQUE (person_id, alias)
);

CREATE TABLE position (
    id                  UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    title               TEXT NOT NULL,
    geo_entity_id       UUID REFERENCES geo_entity(id) ON DELETE RESTRICT,
    level               TEXT,
    parent_position_id  UUID REFERENCES position(id) ON DELETE RESTRICT,
    is_key              BOOLEAN DEFAULT FALSE,
    notes               TEXT
);

CREATE INDEX idx_position_geo ON position (geo_entity_id);

CREATE TABLE tenure (
    id                  UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    person_id           UUID NOT NULL REFERENCES person(id) ON DELETE RESTRICT,
    position_id         UUID NOT NULL REFERENCES position(id) ON DELETE RESTRICT,
    start_date          DATE NOT NULL,
    end_date            DATE,
    appointment_event_id UUID,
    departure_reason    TEXT,
    source_id           UUID NOT NULL REFERENCES source_document(id) ON DELETE RESTRICT,
    created_at          TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    CONSTRAINT tenure_dates_valid CHECK (start_date <= end_date OR end_date IS NULL)
);

CREATE INDEX idx_tenure_person    ON tenure (person_id);
CREATE INDEX idx_tenure_position  ON tenure (position_id);
CREATE INDEX idx_tenure_dates     ON tenure (start_date, end_date);

CREATE TABLE appointment_event (
    id                  UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    tenure_id           UUID NOT NULL REFERENCES tenure(id) ON DELETE RESTRICT,
    event_type          TEXT NOT NULL,
    event_date          DATE NOT NULL,
    document_url        TEXT,
    source_id           UUID NOT NULL REFERENCES source_document(id) ON DELETE RESTRICT,
    created_at          TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE person_source_evidence (
    id                  UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    person_id           UUID NOT NULL REFERENCES person(id) ON DELETE RESTRICT,
    source_id           UUID NOT NULL REFERENCES source_document(id) ON DELETE RESTRICT,
    claim               TEXT NOT NULL,
    source_location_id  UUID REFERENCES source_location(id) ON DELETE RESTRICT,
    created_at          TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- ============================================================================
-- 5. 政策、承诺与项目 (per PRD 5.4)
-- ============================================================================

CREATE TABLE policy_document (
    id                  UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    doc_type            policy_doc_type NOT NULL,
    title               TEXT NOT NULL,
    publisher           TEXT NOT NULL,
    publication_date    DATE NOT NULL,
    effective_date      DATE,
    expiry_date         DATE,
    document_url        TEXT,
    full_text           TEXT,
    full_text_tsv       TSVECTOR,
    summary             TEXT,
    geo_entity_ids      UUID[],
    parent_policy_id    UUID REFERENCES policy_document(id) ON DELETE RESTRICT,
    source_id           UUID NOT NULL REFERENCES source_document(id) ON DELETE RESTRICT,
    created_at          TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_policy_doc_type     ON policy_document (doc_type);
CREATE INDEX idx_policy_doc_pubdate  ON policy_document (publication_date);
CREATE INDEX idx_policy_doc_publisher ON policy_document (publisher);
CREATE INDEX idx_policy_doc_fts      ON policy_document USING gin (full_text_tsv);

CREATE TABLE policy_target (
    id                  UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    policy_document_id  UUID NOT NULL REFERENCES policy_document(id) ON DELETE RESTRICT,
    target_description  TEXT NOT NULL,
    target_indicator_id UUID REFERENCES indicator_definition(id) ON DELETE RESTRICT,
    target_value        NUMERIC,
    target_unit         TEXT,
    target_year         INTEGER,
    measurable          BOOLEAN DEFAULT TRUE,
    source_location_id  UUID REFERENCES source_location(id) ON DELETE RESTRICT,
    created_at          TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE policy_measure (
    id                  UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    policy_document_id  UUID NOT NULL REFERENCES policy_document(id) ON DELETE RESTRICT,
    measure_description TEXT NOT NULL,
    measure_type        TEXT,
    target_audience     TEXT,
    source_location_id  UUID REFERENCES source_location(id) ON DELETE RESTRICT,
    created_at          TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE government_commitment (
    id                  UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    policy_target_id    UUID REFERENCES policy_target(id) ON DELETE RESTRICT,
    commitment_text     TEXT NOT NULL,
    proposer_person_id  UUID REFERENCES person(id) ON DELETE RESTRICT,
    geo_entity_id       UUID NOT NULL REFERENCES geo_entity(id) ON DELETE RESTRICT,
    commitment_date     DATE NOT NULL,
    due_date            DATE,
    status              commitment_status NOT NULL DEFAULT 'PROPOSED',
    source_id           UUID NOT NULL REFERENCES source_document(id) ON DELETE RESTRICT,
    created_at          TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_commitment_geo    ON government_commitment (geo_entity_id);
CREATE INDEX idx_commitment_status ON government_commitment (status);
CREATE INDEX idx_commitment_due    ON government_commitment (due_date);

CREATE TABLE commitment_progress (
    id                  UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    commitment_id       UUID NOT NULL REFERENCES government_commitment(id) ON DELETE RESTRICT,
    progress_date       DATE NOT NULL,
    progress_value      NUMERIC,
    progress_unit       TEXT,
    progress_note       TEXT,
    source_id           UUID NOT NULL REFERENCES source_document(id) ON DELETE RESTRICT,
    created_at          TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE project_event (
    id                  UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    project_name        TEXT NOT NULL,
    geo_entity_id       UUID NOT NULL REFERENCES geo_entity(id) ON DELETE RESTRICT,
    project_type        TEXT,
    status              project_status NOT NULL,
    event_date          DATE NOT NULL,
    investment_amount   NUMERIC,
    investment_unit     TEXT,
    parties             TEXT[],
    description         TEXT,
    source_id           UUID NOT NULL REFERENCES source_document(id) ON DELETE RESTRICT,
    created_at          TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_project_event_geo    ON project_event (geo_entity_id);
CREATE INDEX idx_project_event_status ON project_event (status);
CREATE INDEX idx_project_event_date   ON project_event (event_date);

CREATE TABLE budget_allocation (
    id                  UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    geo_entity_id       UUID NOT NULL REFERENCES geo_entity(id) ON DELETE RESTRICT,
    fiscal_year         INTEGER NOT NULL,
    budget_type         TEXT,
    category            TEXT,
    allocated_amount    NUMERIC NOT NULL,
    unit                TEXT NOT NULL,
    source_id           UUID NOT NULL REFERENCES source_document(id) ON DELETE RESTRICT,
    created_at          TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_budget_alloc_geo  ON budget_allocation (geo_entity_id);
CREATE INDEX idx_budget_alloc_year ON budget_allocation (fiscal_year);

CREATE TABLE budget_execution (
    id                  UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    budget_allocation_id UUID REFERENCES budget_allocation(id) ON DELETE RESTRICT,
    execution_period_id UUID NOT NULL REFERENCES calendar_period(id) ON DELETE RESTRICT,
    executed_amount     NUMERIC NOT NULL,
    unit                TEXT NOT NULL,
    execution_rate      NUMERIC,
    source_id           UUID NOT NULL REFERENCES source_document(id) ON DELETE RESTRICT,
    created_at          TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE public_response_evidence (
    id                  UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    policy_document_id  UUID REFERENCES policy_document(id) ON DELETE RESTRICT,
    commitment_id       UUID REFERENCES government_commitment(id) ON DELETE RESTRICT,
    response_type       TEXT,
    response_summary    TEXT,
    response_date       DATE,
    response_count      INTEGER,
    source_id           UUID NOT NULL REFERENCES source_document(id) ON DELETE RESTRICT,
    created_at          TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- ============================================================================
-- 6. 研究与推断 (per PRD 5.5)
-- ============================================================================

CREATE TABLE research_question (
    id                  UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    question_text       TEXT NOT NULL,
    scope_geo_ids       UUID[],
    scope_indicator_ids UUID[],
    scope_period_ids    UUID[],
    registered_by       TEXT NOT NULL,
    registered_at       TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    notes               TEXT
);

-- 模型规格（必须先建，供 analysis_run 引用）
CREATE TABLE model_specification (
    id                  UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    spec_name           TEXT NOT NULL UNIQUE,
    model_type          TEXT NOT NULL,
    formula             TEXT NOT NULL,
    variables           JSONB NOT NULL,
    standard_errors     TEXT,
    notes               TEXT,
    created_at          TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

COMMENT ON TABLE model_specification IS '模型规格：保存公式、变量、SE 形式，保证可复现';

-- 比较组（必须先建）
CREATE TABLE comparison_group (
    id                  UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    group_name          TEXT NOT NULL,
    geo_entity_ids      UUID[] NOT NULL,
    matching_features   JSONB NOT NULL,
    matching_method     TEXT NOT NULL,
    notes               TEXT,
    created_at          TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    CONSTRAINT comparison_group_has_geos CHECK (array_length(geo_entity_ids, 1) >= 1)
);

COMMENT ON TABLE comparison_group IS '比较组；同类地区匹配依据必须可解释';

CREATE TABLE analysis_run (
    id                  UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    research_question_id UUID REFERENCES research_question(id) ON DELETE RESTRICT,
    method              analysis_method NOT NULL,
    started_at          TIMESTAMPTZ NOT NULL,
    finished_at         TIMESTAMPTZ,
    code_version        TEXT NOT NULL,
    input_data_vintage  TEXT NOT NULL,
    parameters          JSONB NOT NULL,
    comparison_group_id UUID REFERENCES comparison_group(id) ON DELETE RESTRICT,
    model_spec_id       UUID REFERENCES model_specification(id) ON DELETE RESTRICT,
    result_payload      JSONB,
    status              TEXT NOT NULL,
    created_by          TEXT NOT NULL,
    CONSTRAINT analysis_run_status_valid CHECK (status IN ('RUNNING','SUCCESS','FAILED'))
);

CREATE INDEX idx_analysis_run_question ON analysis_run (research_question_id);
CREATE INDEX idx_analysis_run_method   ON analysis_run (method);

CREATE TABLE derived_metric (
    id                  UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    metric_name         TEXT NOT NULL,
    based_on_indicator_ids UUID[] NOT NULL,
    formula             TEXT NOT NULL,
    unit                TEXT,
    notes               TEXT,
    created_at          TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE inference_record (
    id                  UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    layer               information_layer NOT NULL,
    statement           TEXT NOT NULL,
    evidence_obs_ids    UUID[] NOT NULL,
    evidence_gaps       TEXT[],
    alternative_explanations TEXT[],
    uncertainty         TEXT,
    confidence          NUMERIC,
    created_at          TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    created_by          TEXT NOT NULL,
    CONSTRAINT inference_confidence_range CHECK (confidence IS NULL OR confidence BETWEEN 0 AND 1),
    CONSTRAINT inference_layer_not_fact CHECK (layer <> 'FACT')
);

CREATE INDEX idx_inference_layer ON inference_record (layer);

CREATE TABLE uncertainty_record (
    id                  UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    target_type         TEXT NOT NULL,
    target_id           UUID NOT NULL,
    uncertainty_type    TEXT NOT NULL,
    description         TEXT NOT NULL,
    impact_note         TEXT,
    created_at          TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE research_note (
    id                  UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    title               TEXT NOT NULL,
    body                TEXT NOT NULL,
    body_tsv            TSVECTOR,
    layer               information_layer NOT NULL,
    claim_evidence_ids  UUID[],
    created_at          TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at          TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    created_by          TEXT NOT NULL
);

CREATE INDEX idx_research_note_fts ON research_note USING gin (body_tsv);

CREATE TABLE claim_evidence_link (
    id                  UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    claim_id            UUID NOT NULL,
    claim_type          TEXT NOT NULL,
    evidence_id         UUID NOT NULL,
    evidence_type       TEXT NOT NULL,
    polarity            TEXT NOT NULL,
    note                TEXT,
    created_at          TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    CONSTRAINT claim_evidence_polarity CHECK (polarity IN ('SUPPORTS','CONTRADICTS'))
);

CREATE INDEX idx_claim_evidence_claim    ON claim_evidence_link (claim_id);
CREATE INDEX idx_claim_evidence_polarity ON claim_evidence_link (polarity);

-- ============================================================================
-- 7. 触发器：updated_at 维护
-- ============================================================================

CREATE OR REPLACE FUNCTION trg_set_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER set_updated_at_geo_entity
    BEFORE UPDATE ON geo_entity
    FOR EACH ROW EXECUTE FUNCTION trg_set_updated_at();

CREATE TRIGGER set_updated_at_indicator_definition
    BEFORE UPDATE ON indicator_definition
    FOR EACH ROW EXECUTE FUNCTION trg_set_updated_at();

CREATE TRIGGER set_updated_at_source_registry
    BEFORE UPDATE ON source_registry
    FOR EACH ROW EXECUTE FUNCTION trg_set_updated_at();

CREATE TRIGGER set_updated_at_research_note
    BEFORE UPDATE ON research_note
    FOR EACH ROW EXECUTE FUNCTION trg_set_updated_at();

-- tsvector 全文索引维护
CREATE OR REPLACE FUNCTION policy_doc_tsv_update()
RETURNS TRIGGER AS $$
BEGIN
    NEW.full_text_tsv = to_tsvector('simple', COALESCE(NEW.full_text, '') || ' ' || COALESCE(NEW.title, ''));
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER policy_doc_tsv
    BEFORE INSERT OR UPDATE ON policy_document
    FOR EACH ROW EXECUTE FUNCTION policy_doc_tsv_update();

CREATE OR REPLACE FUNCTION research_note_tsv_update()
RETURNS TRIGGER AS $$
BEGIN
    NEW.body_tsv = to_tsvector('simple', COALESCE(NEW.body, '') || ' ' || COALESCE(NEW.title, ''));
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER research_note_tsv
    BEFORE INSERT OR UPDATE ON research_note
    FOR EACH ROW EXECUTE FUNCTION research_note_tsv_update();

-- ============================================================================
-- 8. 不可变性（append-only）触发器：observation/source_document/revision
--    返工六-2/六-3：全部改用 IS DISTINCT FROM（NULL 安全），
--    保护全部不可变字段，并一律拒绝 DELETE。
-- ============================================================================

-- source_document 不可 UPDATE（除 caveat_text 与 verification_status 外）
-- verification_status 允许变更：UNVERIFIED → 平台核验后提升（评审七-7）
CREATE OR REPLACE FUNCTION source_document_immutable()
RETURNS TRIGGER AS $$
BEGIN
    IF OLD.id                  IS DISTINCT FROM NEW.id
       OR OLD.source_registry_id IS DISTINCT FROM NEW.source_registry_id
       OR OLD.source_level       IS DISTINCT FROM NEW.source_level
       OR OLD.title              IS DISTINCT FROM NEW.title
       OR OLD.publisher          IS DISTINCT FROM NEW.publisher
       OR OLD.publication_date   IS DISTINCT FROM NEW.publication_date
       OR OLD.url                IS DISTINCT FROM NEW.url
       OR OLD.file_path          IS DISTINCT FROM NEW.file_path
       OR OLD.file_hash_sha256   IS DISTINCT FROM NEW.file_hash_sha256
       OR OLD.file_format        IS DISTINCT FROM NEW.file_format
       OR OLD.file_size_bytes    IS DISTINCT FROM NEW.file_size_bytes
       OR OLD.language           IS DISTINCT FROM NEW.language
       OR OLD.extraction_method  IS DISTINCT FROM NEW.extraction_method
       OR OLD.copyright_note     IS DISTINCT FROM NEW.copyright_note
       OR OLD.uploader_id        IS DISTINCT FROM NEW.uploader_id
    THEN
        RAISE EXCEPTION 'source_document is immutable; create new document instead of modifying %', OLD.id;
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER source_document_immutable
    BEFORE UPDATE ON source_document
    FOR EACH ROW EXECUTE FUNCTION source_document_immutable();

CREATE OR REPLACE FUNCTION source_document_no_delete()
RETURNS TRIGGER AS $$
BEGIN
    RAISE EXCEPTION 'source_document cannot be deleted (audit/lineage anchor); id=%', OLD.id;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER source_document_no_delete
    BEFORE DELETE ON source_document
    FOR EACH ROW EXECUTE FUNCTION source_document_no_delete();

-- observation: 事实、口径、地域版本及血缘字段全部不可 UPDATE（必须走 revision）
CREATE OR REPLACE FUNCTION observation_immutable()
RETURNS TRIGGER AS $$
BEGIN
    IF OLD.value                              IS DISTINCT FROM NEW.value
       OR OLD.unit                            IS DISTINCT FROM NEW.unit
       OR OLD.raw_value                       IS DISTINCT FROM NEW.raw_value
       OR OLD.missing_reason                  IS DISTINCT FROM NEW.missing_reason
       OR OLD.is_imputed                      IS DISTINCT FROM NEW.is_imputed
       OR OLD.status                          IS DISTINCT FROM NEW.status
       OR OLD.value_type                      IS DISTINCT FROM NEW.value_type
       OR OLD.comparison_basis                IS DISTINCT FROM NEW.comparison_basis
       OR OLD.confidence                      IS DISTINCT FROM NEW.confidence
       OR OLD.indicator_id                    IS DISTINCT FROM NEW.indicator_id
       OR OLD.indicator_methodology_version_id IS DISTINCT FROM NEW.indicator_methodology_version_id
       OR OLD.geo_entity_id                   IS DISTINCT FROM NEW.geo_entity_id
       OR OLD.geo_code_version_id             IS DISTINCT FROM NEW.geo_code_version_id
       OR OLD.calendar_period_id              IS DISTINCT FROM NEW.calendar_period_id
       OR OLD.source_id                       IS DISTINCT FROM NEW.source_id
       OR OLD.source_location_id              IS DISTINCT FROM NEW.source_location_id
       OR OLD.ingestion_run_id                IS DISTINCT FROM NEW.ingestion_run_id
       OR OLD.extraction_method               IS DISTINCT FROM NEW.extraction_method
       OR OLD.extracted_at                    IS DISTINCT FROM NEW.extracted_at
    THEN
        RAISE EXCEPTION 'observation facts are immutable; use observation_revision instead for %', OLD.id;
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER observation_immutable
    BEFORE UPDATE ON observation
    FOR EACH ROW EXECUTE FUNCTION observation_immutable();

-- 返工六-3：observation 无论有无 revision 一律拒绝 DELETE
CREATE OR REPLACE FUNCTION observation_no_delete()
RETURNS TRIGGER AS $$
BEGIN
    RAISE EXCEPTION 'observation cannot be deleted; supersede via observation_revision (id=%)', OLD.id;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER observation_no_delete
    BEFORE DELETE ON observation
    FOR EACH ROW EXECUTE FUNCTION observation_no_delete();

-- observation_revision: append-only
CREATE OR REPLACE FUNCTION observation_revision_immutable()
RETURNS TRIGGER AS $$
BEGIN
    RAISE EXCEPTION 'observation_revision is append-only; id=%', OLD.id;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER observation_revision_no_update
    BEFORE UPDATE ON observation_revision
    FOR EACH ROW EXECUTE FUNCTION observation_revision_immutable();

CREATE TRIGGER observation_revision_no_delete
    BEFORE DELETE ON observation_revision
    FOR EACH ROW EXECUTE FUNCTION observation_revision_immutable();

-- ============================================================================
-- 9. 注释：本 Schema 的边界
-- ============================================================================

-- Stage 0 已验证：
--   1. psql -v ON_ERROR_STOP=1 -f schema/01-core.sql 在 PostgreSQL 16.14 + PostGIS 上跑通；
--   2. 见 schema/migrations/001_create_core.log 作为执行证据。

-- Stage 1 实施时需要：
--   1. 启用 pgvector 扩展（line 14 取消注释）；
--   2. Alembic 迁移管理；
--   3. RLS（行级安全）按角色隔离；
--   4. 按 calendar_period 分区（partition）大表；
--   5. 备份策略 + WAL archiving；
--   6. 监控（pg_stat_statements + auto_explain）。