-- ============================================================================
-- Migration 007 — ocr_review_queue + observation OCR confidence floor (S1.15)
-- ============================================================================
-- Per docs/30 §2 (plan, audited by Cursor 114/115 §SCHEMA):
--   * docs/10 §2.8: OCR 置信度 < 0.70 必须入复核队列、不入正式表
--   * 阈值来源: docs/10 §2.8 验收常量 (0-1 标度, observation.confidence CHECK 0-1)
--   * spikes/04-scanned-pdf/gate_thresholds.json 是 spike-04 OCR 质量评测 gate
--     (0-100 标度), 属不同构件 — 只读不写, 本迁移不引用
--
-- 设计:
--   * cegr.ocr_review_queue — 单元格级停车场; 复核 ACCEPT 后走 MANUAL_UPLOAD
--     重新提取入 observation (不改 confidence 粉饰), 见 docs/30 §2.3
--   * observation CHECK 硬门 — DB 级不可绕过 (docs/10「不入正式表」):
--     extraction_method ∈ {PDF_OCR, IMAGE_OCR} 时 confidence 须 >= 0.70
--     (恰好 0.70 通过 — docs/10 定义是 <0.7 才分流)
--   * 幂等: 表/索引用 IF NOT EXISTS; ADD CONSTRAINT 无 IF NOT EXISTS 语法,
--     用 DO 块查 pg_constraint 守卫 (S1.14 FAIL 教训: 见 005 头注)
--   * 全部落 cegr schema, 随 conftest DROP SCHEMA cegr CASCADE 自然清理
-- ============================================================================

CREATE TABLE IF NOT EXISTS cegr.ocr_review_queue (
    id                  UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    source_document_id  UUID NOT NULL REFERENCES cegr.source_document(id) ON DELETE RESTRICT,
    ingestion_run_id    UUID REFERENCES cegr.ingestion_run(id),
    indicator_id        UUID REFERENCES cegr.indicator_definition(id),  -- 复核确认映射前可空
    geo_entity_id       UUID REFERENCES cegr.geo_entity(id),
    calendar_period_id  UUID REFERENCES cegr.calendar_period(id),
    raw_ocr_text        TEXT,                       -- 原始单元格文本(含不可解析)
    parsed_value        NUMERIC,                    -- 复核前解析值(可能是错的)
    confidence          NUMERIC NOT NULL CHECK (confidence >= 0 AND confidence < 0.70),
    locator_page        INTEGER,
    locator_bbox        JSONB,
    review_status       TEXT NOT NULL DEFAULT 'PENDING'
                        CHECK (review_status IN ('PENDING','ACCEPTED','REJECTED','REEXTRACT')),
    resolution_note     TEXT,
    reviewed_by         TEXT,
    reviewed_at         TIMESTAMPTZ,
    created_at          TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_ocr_review_queue_status
    ON cegr.ocr_review_queue (review_status);
CREATE INDEX IF NOT EXISTS idx_ocr_review_queue_doc
    ON cegr.ocr_review_queue (source_document_id);

COMMENT ON TABLE cegr.ocr_review_queue IS
    'Stage 1 / S1.15 — OCR 低置信度单元格复核队列 (docs/10 §2.8). '
    'confidence < 0.70 的 OCR 单元格不入 observation, 落此表待人工复核; '
    'ACCEPT 后以 MANUAL_UPLOAD 重新提取';

-- 观测表硬门: OCR 提取路径置信度下限 0.70 (docs/10 §2.8)
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM pg_constraint
        WHERE conname = 'observation_ocr_confidence_floor'
          AND conrelid = 'cegr.observation'::regclass
    ) THEN
        ALTER TABLE cegr.observation ADD CONSTRAINT observation_ocr_confidence_floor CHECK (
            extraction_method NOT IN ('PDF_OCR','IMAGE_OCR')
            OR confidence IS NULL        -- 非 OCR 语义路径不受限
            OR confidence >= 0.70
        );
    END IF;
END $$;

-- ============================================================================
-- 验证
-- ============================================================================
-- SELECT to_regclass('cegr.ocr_review_queue');
-- SELECT conname FROM pg_constraint
--   WHERE conname = 'observation_ocr_confidence_floor';
-- 直插低置信 OCR 行应被拒:
--   INSERT INTO cegr.observation (... extraction_method='PDF_OCR', confidence=0.65 ...)
--   → 违反 observation_ocr_confidence_floor
