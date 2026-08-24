-- ============================================================================
-- Migration 002 — I-05 来源等级治理 (Stage 0 Gate 0 R4)
--
-- 目的：分离 "uploader-declared" vs "platform-verified effective" 来源等级，
--       强制 S0 必须经过平台核验，并保留完整审计轨迹。
--
-- 增量：
--   1. source_document.declared_source_level    (新列)  上传者声明的等级
--   2. source_document 的 S0+UNVERIFIED CHECK   (新约束) 反 "未核验冒充 S0"
--   3. source_document_verification_event      (新表)  append-only 审计日志
--   4. 触发器：每次 verification_status UPDATE   写一条事件（含审核人、时间、证据）
--
-- 反向语义：source_document 不可变（除 caveat_text + verification_status），
--           source_document_verification_event 同样 append-only。
-- ============================================================================

SET search_path = cegr, public;

-- 1. 新增 declared_source_level 列；uploader 上传时可声明等级，平台核验后才能
--    升为 effective S0。允许 NULL（兼容历史行）。
ALTER TABLE source_document
    ADD COLUMN IF NOT EXISTS declared_source_level source_level;

COMMENT ON COLUMN source_document.declared_source_level IS
    '上传者声明的来源等级（informational；effective level 在 source_level）';

-- 2. CHECK 约束：effective S0 必须已经过平台核验。
--    S1/S2/S3/S4 不要求 verification（它们本身可信度按层级递减，
--    允许 UNVERIFIED 是设计意图）。
ALTER TABLE source_document
    ADD CONSTRAINT source_level_s0_requires_verified
    CHECK (
        source_level <> 'S0' OR verification_status = 'VERIFIED'
    );

COMMENT ON CONSTRAINT source_level_s0_requires_verified ON source_document IS
    'I-05：effective S0 必须是平台已核验；未核验上传者声明只能停留在 S1-S4';

-- 3. 核验事件审计表（append-only；DELETE/UPDATE 由 trigger 拦截）
CREATE TABLE source_document_verification_event (
    id                       UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    source_document_id       UUID NOT NULL REFERENCES source_document(id) ON DELETE RESTRICT,
    from_status              source_verification_status,
    to_status                source_verification_status NOT NULL,
    from_declared_level      source_level,
    from_effective_level     source_level,
    to_declared_level        source_level,
    to_effective_level       source_level,
    verifier_id              TEXT NOT NULL,            -- 平台核验人/角色
    evidence_note            TEXT,                     -- 核验依据（链接/SHA/公告）
    decided_at               TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_src_verify_event_doc
    ON source_document_verification_event (source_document_id, decided_at DESC);

COMMENT ON TABLE source_document_verification_event IS
    '核验状态迁移审计日志（append-only）。每次 source_document.verification_status'
    ' 变更都触发一条事件，含前后状态、变更人、时间、证据。';

-- 4. 触发器：仅允许 verification_status + caveat_text 变更；
--    任何 verification_status 变更 → 写事件
CREATE OR REPLACE FUNCTION source_document_log_verification()
RETURNS TRIGGER AS $$
BEGIN
    IF OLD.verification_status IS DISTINCT FROM NEW.verification_status THEN
        INSERT INTO source_document_verification_event (
            source_document_id,
            from_status, to_status,
            from_declared_level, from_effective_level,
            to_declared_level, to_effective_level,
            verifier_id, evidence_note
        ) VALUES (
            NEW.id,
            OLD.verification_status, NEW.verification_status,
            OLD.declared_source_level, OLD.source_level,
            NEW.declared_source_level, NEW.source_level,
            COALESCE(current_setting('app.verifier_id', true), 'system'),
            'source_document_verification_status transition'
        );
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER source_document_log_verification
    AFTER UPDATE OF verification_status ON source_document
    FOR EACH ROW EXECUTE FUNCTION source_document_log_verification();

-- 5. 审计表本身 append-only（防回溯篡改）
CREATE OR REPLACE FUNCTION source_document_verification_event_immutable()
RETURNS TRIGGER AS $$
BEGIN
    RAISE EXCEPTION 'source_document_verification_event is append-only; '
                    'UPDATE/DELETE forbidden on %', OLD.id;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER source_document_verification_event_no_update
    BEFORE UPDATE ON source_document_verification_event
    FOR EACH ROW EXECUTE FUNCTION source_document_verification_event_immutable();

CREATE TRIGGER source_document_verification_event_no_delete
    BEFORE DELETE ON source_document_verification_event
    FOR EACH ROW EXECUTE FUNCTION source_document_verification_event_immutable();

RESET search_path;
