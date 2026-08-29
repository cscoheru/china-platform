-- Migration 014 — O3 OCR 生产路径：source_document.doc_kind 列
--
-- Per docs/49 §3.2 Step 7 output spec + §5.2.3 (实装位置) + 583 任务书 §B。
-- 前置：582 审计 PASS；581 修复刀完成。
-- 性质：流程刀落地（最小）；单列增量 + CHECK + index；零数据迁移（DEFAULT 'NORMAL'）。
--
-- 闭合 docs/49 §5.2.3；O3 引擎依赖（paddle-ocr / 5.2.4 / 5.2.5 / 5.2.6）后续刀。
--
-- 列选择 deviation 论证：
--   docs/49 §3.2 Step 7 列 spec = {source_file_sha256, doc_kind, language, page_count,
--                                    upload_user_id, uploaded_at, lineage}
--   source_document 既有列（schema/01-core.sql L312–334）已含：
--     file_hash_sha256 ↔ source_file_sha256 ✓（既有，零新增）
--     language ✓（既有，DEFAULT 'zh'）
--     uploader_id (TEXT) ↔ upload_user_id 语义映射 ✓（既有，零新增）
--     created_at (TIMESTAMPTZ) ↔ uploaded_at 语义映射 ✓（既有，零新增）
--     file_format (TEXT) 内隐式表达 page_count（OCR 工具元数据提取，非 schema 列）
--   → migration 014 **仅新增 doc_kind 列**；其余语义映射走既有列，避免列冗余。
--
-- 评分/排名/总分字段 (score/rating/rank/total_score/confidence_score/credibility_score)
-- 红线: 一律不引入.
--
-- 线 lineage JSONB（如需）：迁移本期不新增；如 O3 流水线后续需独立 lineage 列（区别
--   source_document.file_hash_sha256 上游链），后续刀 §5.2.7+ 单独议。

BEGIN;

ALTER TABLE source_document
    ADD COLUMN doc_kind TEXT NOT NULL DEFAULT 'NORMAL';

ALTER TABLE source_document
    ADD CONSTRAINT source_document_doc_kind_check
        CHECK (doc_kind IN ('NORMAL', 'OCR_SCAN'));

CREATE INDEX idx_source_doc_doc_kind ON source_document (doc_kind);

COMMENT ON COLUMN source_document.doc_kind IS
    '来源文档类型：NORMAL = 普通文件上传（默认值，向后兼容既有行）；OCR_SCAN = 扫描件 OCR 录入（per docs/49 §3.2 Step 7 + 583 任务书 §B）';

COMMIT;
