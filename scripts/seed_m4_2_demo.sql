-- ============================================================================
-- 639 / M4.2: 人物政策 demo seed (knife 639)
-- ============================================================================
-- Per knife 639 tasking §2.639-A.2 / docs/58 §5 (M4.2 推荐 scope) /
-- docs/59 §3 (架构师级审查,本 SQL 是 demo 数据的事实源).
--
-- 性质: 纯 demo / 隔离 seed. 全部 demo 行:
--   * person.is_demo = TRUE
--   * appointment_event.is_demo = TRUE
--   * tenure.source_id = demo source_document (synthetic SHA)
--   * appointment_event.source_id = demo source_document
--   * source_document.file_hash_sha256 = deterministic demo SHA '0...01'
--     (用于一跳回 SHA 标识 demo 隔离,不走真实 source_registry).
--
-- 写入目标: cegr schema (默认 search_path).
-- 隔离原则: 应用层 SELECT 必须 WHERE is_demo=true 过滤;真实数据 INSERT
--   必须 is_demo=false + source_id NOT NULL (016+ 引入 CHECK 约束).
--
-- Red lines (per docs/34 §7 + tasking 639 §红线):
--   * ❌ 不删表 / 不 DROP COLUMN / 不 DELETE FROM 真实数据
--   * ❌ 不修改 source_registry 既有行 / mart_*.sql / 4 frontend fixture
--   * ❌ 不写 cegr.observation 真实行
--   * ❌ 不静默硬编码 GDP 值 (demo 无 GDP 字段)
--   * ❌ demo ≤ 5 person / tenure / appointment_event
--   * ❌ 不宣称 Gate / O1 / M2 / M4 PASS
--
-- Verification (this knife must satisfy):
--   * tests/test_m4_2_renmian_demo.py ≥ 6 用例 必须全 green
--   * 现有 49+8+6 ≥ 63 pytest 必须仍 pass
--   * 039-A 不动 015 已加列 (person.is_demo / appointment_event.is_demo /
--     person.last_verified_at + 3 索引)
--   * demo 数据与 638 receipt §8 (cc_head `f1fdad5` + receipt `ee86977`)
--     链路一致;不冲突
-- ============================================================================

SET search_path = cegr, public;

BEGIN;

-- ----------------------------------------------------------------------------
-- 1. 1 个 demo source_registry (synthetic;不修改既有 registry 行)
-- ----------------------------------------------------------------------------
INSERT INTO source_registry (
    id, domain, organization, category, primary_url,
    update_frequency, auth_note, access_method,
    historical_coverage, stability_note, failure_handling, enabled
) VALUES (
    'a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a01',
    'demo.placeholder',
    'M4.2 demo (synthetic)',
    'demo',
    'https://demo.placeholder/m4_2',
    'never',
    'demo source; no auth required; used only for demo isolation',
    'MANUAL_UPLOAD',
    'demo coverage',
    'demo SHA deterministic (0...01)',
    'demo no retry',
    FALSE
) ON CONFLICT (id) DO NOTHING;

-- ----------------------------------------------------------------------------
-- 2. 1 个 demo source_document (deterministic SHA 0...01;UNVERIFIED 状态)
-- ----------------------------------------------------------------------------
INSERT INTO source_document (
    id, source_registry_id, source_level, verification_status,
    title, publisher, publication_date, url,
    file_hash_sha256, file_format, file_size_bytes,
    language, extraction_method, caveat_text,
    uploader_id
) VALUES (
    'a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a11',
    'a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a01',
    'S4',                                   -- demo (synthetic);S4 = 社交/自媒体最低级
    'UNVERIFIED',
    'M4.2 demo placeholder document',
    'M4.2 demo (synthetic)',
    '2024-01-01',
    'https://demo.placeholder/m4_2/person',
    '0000000000000000000000000000000000000000000000000000000000000001',  -- demo SHA
    'sql',
    4096,
    'zh',
    'MANUAL_UPLOAD',
    'demo only; NOT real 任免 data; is_demo=true isolation required for all downstream rows',
    'm4_2_demo'
) ON CONFLICT (id) DO NOTHING;

-- ----------------------------------------------------------------------------
-- 3. 5 个 demo position (synthetic;无 geo_entity_id;title NOT NULL)
--    注: schema 当前 position 表无 is_demo 列 (015 仅 person/appointment_event 加);
--    demo position 由下游应用层按 source_document.is_demo (本 seed 单条 S4 demo) 关联过滤.
-- ----------------------------------------------------------------------------
INSERT INTO position (id, title, level, is_key)
VALUES
    ('b0eebc99-9c0b-4ef8-bb6d-6bb9bd380a21', 'demo-position-1', 'central', FALSE),
    ('b0eebc99-9c0b-4ef8-bb6d-6bb9bd380a22', 'demo-position-2', 'central', FALSE),
    ('b0eebc99-9c0b-4ef8-bb6d-6bb9bd380a23', 'demo-position-3', 'central', FALSE),
    ('b0eebc99-9c0b-4ef8-bb6d-6bb9bd380a24', 'demo-position-4', 'central', FALSE),
    ('b0eebc99-9c0b-4ef8-bb6d-6bb9bd380a25', 'demo-position-5', 'central', FALSE)
ON CONFLICT (id) DO NOTHING;

-- ----------------------------------------------------------------------------
-- 4. 5 个 demo person (全部 is_demo=TRUE;last_verified_at=NOW())
-- ----------------------------------------------------------------------------
INSERT INTO person (id, canonical_name, gender, notes, is_demo, last_verified_at)
VALUES
    ('c0eebc99-9c0b-4ef8-bb6d-6bb9bd380a31', 'demo-person-1', NULL,
     'M4.2 demo row 1/5; isolated by is_demo=true; no real 任免 data',
     TRUE, NOW()),
    ('c0eebc99-9c0b-4ef8-bb6d-6bb9bd380a32', 'demo-person-2', NULL,
     'M4.2 demo row 2/5; isolated by is_demo=true; no real 任免 data',
     TRUE, NOW()),
    ('c0eebc99-9c0b-4ef8-bb6d-6bb9bd380a33', 'demo-person-3', NULL,
     'M4.2 demo row 3/5; isolated by is_demo=true; no real 任免 data',
     TRUE, NOW()),
    ('c0eebc99-9c0b-4ef8-bb6d-6bb9bd380a34', 'demo-person-4', NULL,
     'M4.2 demo row 4/5; isolated by is_demo=true; no real 任免 data',
     TRUE, NOW()),
    ('c0eebc99-9c0b-4ef8-bb6d-6bb9bd380a35', 'demo-person-5', NULL,
     'M4.2 demo row 5/5; isolated by is_demo=true; no real 任免 data',
     TRUE, NOW())
ON CONFLICT (id) DO NOTHING;

-- ----------------------------------------------------------------------------
-- 5. 5 个 demo tenure (全部 source_id = demo source_document;
--    start_date <= end_date OR end_date IS NULL)
-- ----------------------------------------------------------------------------
INSERT INTO tenure (id, person_id, position_id, start_date, end_date,
                    source_id, departure_reason)
VALUES
    ('d0eebc99-9c0b-4ef8-bb6d-6bb9bd380a41',
     'c0eebc99-9c0b-4ef8-bb6d-6bb9bd380a31',
     'b0eebc99-9c0b-4ef8-bb6d-6bb9bd380a21',
     '2024-01-01', NULL,
     'a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a11',
     'M4.2 demo tenure 1; current'),
    ('d0eebc99-9c0b-4ef8-bb6d-6bb9bd380a42',
     'c0eebc99-9c0b-4ef8-bb6d-6bb9bd380a32',
     'b0eebc99-9c0b-4ef8-bb6d-6bb9bd380a22',
     '2024-01-01', NULL,
     'a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a11',
     'M4.2 demo tenure 2; current'),
    ('d0eebc99-9c0b-4ef8-bb6d-6bb9bd380a43',
     'c0eebc99-9c0b-4ef8-bb6d-6bb9bd380a33',
     'b0eebc99-9c0b-4ef8-bb6d-6bb9bd380a23',
     '2024-01-01', '2024-12-31',
     'a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a11',
     'M4.2 demo tenure 3; ended'),
    ('d0eebc99-9c0b-4ef8-bb6d-6bb9bd380a44',
     'c0eebc99-9c0b-4ef8-bb6d-6bb9bd380a34',
     'b0eebc99-9c0b-4ef8-bb6d-6bb9bd380a24',
     '2024-01-01', NULL,
     'a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a11',
     'M4.2 demo tenure 4; current'),
    ('d0eebc99-9c0b-4ef8-bb6d-6bb9bd380a45',
     'c0eebc99-9c0b-4ef8-bb6d-6bb9bd380a35',
     'b0eebc99-9c0b-4ef8-bb6d-6bb9bd380a25',
     '2024-01-01', NULL,
     'a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a11',
     'M4.2 demo tenure 5; current')
ON CONFLICT (id) DO NOTHING;

-- ----------------------------------------------------------------------------
-- 6. 5 个 demo appointment_event (全部 is_demo=TRUE;
--    tenure_id FK 到上 5 条 demo tenure; source_id = demo source_document)
-- ----------------------------------------------------------------------------
INSERT INTO appointment_event (id, tenure_id, event_type, event_date,
                               document_url, source_id, is_demo)
VALUES
    ('e0eebc99-9c0b-4ef8-bb6d-6bb9bd380a51',
     'd0eebc99-9c0b-4ef8-bb6d-6bb9bd380a41',
     'appointment', '2024-01-01',
     'https://demo.placeholder/m4_2/person/1',
     'a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a11', TRUE),
    ('e0eebc99-9c0b-4ef8-bb6d-6bb9bd380a52',
     'd0eebc99-9c0b-4ef8-bb6d-6bb9bd380a42',
     'appointment', '2024-01-01',
     'https://demo.placeholder/m4_2/person/2',
     'a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a11', TRUE),
    ('e0eebc99-9c0b-4ef8-bb6d-6bb9bd380a53',
     'd0eebc99-9c0b-4ef8-bb6d-6bb9bd380a43',
     'appointment', '2024-01-01',
     'https://demo.placeholder/m4_2/person/3',
     'a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a11', TRUE),
    ('e0eebc99-9c0b-4ef8-bb6d-6bb9bd380a54',
     'd0eebc99-9c0b-4ef8-bb6d-6bb9bd380a44',
     'appointment', '2024-01-01',
     'https://demo.placeholder/m4_2/person/4',
     'a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a11', TRUE),
    ('e0eebc99-9c0b-4ef8-bb6d-6bb9bd380a55',
     'd0eebc99-9c0b-4ef8-bb6d-6bb9bd380a45',
     'removal',    '2024-12-31',
     'https://demo.placeholder/m4_2/person/5',
     'a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a11', TRUE)
ON CONFLICT (id) DO NOTHING;

COMMIT;

RESET search_path;
