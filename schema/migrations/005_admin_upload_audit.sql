-- ============================================================================
-- Migration 005 — admin_upload_audit (Stage 1 / S1.13.1)
-- ============================================================================
-- Per Cursor 100 §SCHEMA / 裁定:
--   * 接口: POST /admin/upload + scripts/admin_upload.py
--   * 鉴权: ADMIN_UPLOAD_TOKEN (Bearer / header)
--   * 存储: 本地 uploads/...; SHA-256; source_document 登记
--   * audit: 最小 admin_upload_audit 表
--
-- Implements R08 措施 4 / 措施 7 的人工上传入口审计追踪。审计表用于:
--   1. ops 人工检查上传异常 (failed uploads, 异常来源)
--   2. Stage 2 IAM 引入前的最小替代 (单 token + 完整审计行)
--   3. 合规追溯 (谁在何时上传了什么)
--
-- 设计:
--   * append-only (无 UPDATE/DELETE 触发器); 仅 INSERT
--   * 不记文件内容, 仅 SHA-256 引用 (避免审计表膨胀)
--   * 失败请求也记 (status=FAILED + error_code)
--   * client_ip 容忍 NULL (CLI 路径无 HTTP client)
-- ============================================================================

CREATE TABLE admin_upload_audit (
    id                  UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    timestamp_utc       TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    uploader_id         TEXT NOT NULL,
    source_id           UUID,                     -- 上传参数; 上传失败时可为 NULL
    file_hash_sha256    TEXT,                     -- 计算后填; 上传失败时可为 NULL
    file_size_bytes     BIGINT,
    file_format         TEXT,
    client_ip           TEXT,                     -- HTTP 来源; CLI 可为 NULL
    auth_method         TEXT NOT NULL,            -- 'BEARER_TOKEN' || 'CLI'
    status              TEXT NOT NULL,            -- 'SUCCESS' || 'FAILED'
    error_code          TEXT,                     -- 失败时填; 同 docs/28 §1.1 错误码
    purpose_note        TEXT,
    declared_url        TEXT
);

CREATE INDEX idx_admin_upload_audit_timestamp ON admin_upload_audit (timestamp_utc DESC);
CREATE INDEX idx_admin_upload_audit_source    ON admin_upload_audit (source_id) WHERE source_id IS NOT NULL;
CREATE INDEX idx_admin_upload_audit_status    ON admin_upload_audit (status);

COMMENT ON TABLE admin_upload_audit IS
    'Stage 1 / S1.13.1 — /admin/upload 人工上传入口审计追踪. '
    'append-only; 失败请求也记; 不存文件内容, 仅 SHA-256 + 元数据';

-- ============================================================================
-- 验证
-- ============================================================================
-- SELECT COUNT(*) FROM cegr.admin_upload_audit WHERE status = 'FAILED';
-- SELECT uploader_id, COUNT(*) FROM cegr.admin_upload_audit
--   WHERE timestamp_utc > NOW() - INTERVAL '7 days' GROUP BY 1;