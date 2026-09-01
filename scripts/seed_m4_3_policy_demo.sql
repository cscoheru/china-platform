-- ============================================================================
-- 640 / M4.3: 政策项目 demo seed (knife 640)
-- ============================================================================
-- Per knife 640 tasking §2.640-A.2 / docs/59 §5 (M4.3 推荐 scope) /
-- docs/33 §3.2 sentinel (lineage JSONB is_demo 唯一落点).
--
-- 性质: 纯 demo / 隔离 seed. 全部 demo 行:
--   * policy_document.lineage->>'is_demo' = 'true'
--   * policy_target.lineage->>'is_demo'    = 'true'
--   * policy_measure.lineage->>'is_demo'   = 'true'
--   * government_commitment.lineage->>'is_demo' = 'true'
--   * commitment_progress.lineage->>'is_demo'  = 'true'
--   * project_event.lineage->>'is_demo'    = 'true'
--   * source_document.file_hash_sha256     = deterministic demo SHA '0...02'
--     (与 639 demo SHA '0...01' 区分,避免 demo 污染混淆)
--
-- 写入目标: cegr schema (默认 search_path).
-- 隔离原则: 应用层 SELECT 必须 WHERE lineage->>'is_demo' = 'true' 过滤;
--   真实数据 INSERT 必须 lineage->>'is_demo' = 'false' 或 NULL
--   (009+010 已建 idx_*_lineage_gin GIN 索引).
--
-- Red lines (per docs/34 §7 + tasking 640 §红线):
--   * ❌ 不删表 / 不 DROP COLUMN / 不 DELETE FROM 真实数据
--   * ❌ 不修改 source_registry 既有行 / mart_*.sql / 4 frontend fixture
--   * ❌ 不写 cegr.observation 真实行
--   * ❌ 不静默硬编码 GDP 值 (demo 表无 GDP 字段)
--   * ❌ demo ≤ 3 条 each policy 6 表
--   * ❌ 不宣称 Gate / O1 / M2 / M4 PASS
--   * ❌ 不新写 016 migration (沿用 009+010 lineage JSONB)
--
-- Verification (this knife must satisfy):
--   * tests/test_m4_3_policy_demo.py ≥ 6 用例 必须全 green
--   * 现有 64 用例 pytest (M2 + 637 + 638 + 639) 必须仍 pass
--   * 不动 015 已加列 (person.is_demo / appointment_event.is_demo)
--   * 不动 009 lineage JSONB on 5 政策表 / 010 lineage JSONB on project_event
--   * demo 数据与 639 receipt §8 (cc_head `1fca08e` + receipt `11778db`)
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
    'b0eebc99-9c0b-4ef8-bb6d-6bb9bd380a01',
    'demo.placeholder',
    'M4.3 demo (synthetic)',
    'demo',
    'https://demo.placeholder/m4_3',
    'never',
    'demo source; no auth required; used only for demo isolation',
    'MANUAL_UPLOAD',
    'demo coverage',
    'demo SHA deterministic (0...02)',
    'demo no retry',
    FALSE
) ON CONFLICT (id) DO NOTHING;

-- ----------------------------------------------------------------------------
-- 2. 1 个 demo source_document (deterministic SHA 0...02;UNVERIFIED 状态)
-- ----------------------------------------------------------------------------
INSERT INTO source_document (
    id, source_registry_id, source_level, verification_status,
    title, publisher, publication_date, url,
    file_hash_sha256, file_format, file_size_bytes,
    language, extraction_method, caveat_text,
    uploader_id
) VALUES (
    'b0eebc99-9c0b-4ef8-bb6d-6bb9bd380a11',
    'b0eebc99-9c0b-4ef8-bb6d-6bb9bd380a01',
    'S4',                                   -- demo (synthetic);S4 = 社交/自媒体最低级
    'UNVERIFIED',
    'M4.3 demo placeholder document',
    'M4.3 demo (synthetic)',
    '2024-01-01',
    'https://demo.placeholder/m4_3/policy',
    '0000000000000000000000000000000000000000000000000000000000000002',  -- demo SHA 0...02 (与 639 SHA 0...01 区分)
    'sql',
    4096,
    'zh',
    'MANUAL_UPLOAD',
    'demo only; NOT real policy data; lineage.is_demo=true isolation required for all downstream rows',
    'm4_3_demo'
) ON CONFLICT (id) DO NOTHING;

-- ----------------------------------------------------------------------------
-- 3. 3 个 demo geo_entity (synthetic PROVINCE;government_commitment / project_event 需要)
--    不绑定具体省份名 (因 640 probe 仅 2 REACHABLE 黑龙江省政策源,1 省不足以做省-政策 映射 demo).
--    与 639 demo-person-1..5 同模式:合成数据 + lineage JSONB 隔离.
-- ----------------------------------------------------------------------------
INSERT INTO geo_entity (id, canonical_name, canonical_name_en, level, notes)
VALUES
    ('f1eebc99-9c0b-4ef8-bb6d-6bb9bd380c01', 'M4.3 demo province 1', 'M4.3 demo province 1',
     'PROVINCE', 'M4.3 demo synthetic geo; not bound to real province; lineage JSONB isolates'),
    ('f2eebc99-9c0b-4ef8-bb6d-6bb9bd380c02', 'M4.3 demo province 2', 'M4.3 demo province 2',
     'PROVINCE', 'M4.3 demo synthetic geo; not bound to real province; lineage JSONB isolates'),
    ('f3eebc99-9c0b-4ef8-bb6d-6bb9bd380c03', 'M4.3 demo province 3', 'M4.3 demo synthetic province 3',
     'PROVINCE', 'M4.3 demo synthetic geo; not bound to real province; lineage JSONB isolates')
ON CONFLICT (id) DO NOTHING;

-- ----------------------------------------------------------------------------
-- 4. 3 个 demo policy_document (全部 lineage JSONB is_demo='true')
-- ----------------------------------------------------------------------------
INSERT INTO policy_document (
    id, doc_type, title, publisher, publication_date,
    source_id, classification, policy_level, lineage
) VALUES
    ('c1eebc99-9c0b-4ef8-bb6d-6bb9bd380a31', 'REGULATION',
     'demo-policy-document-1', 'M4.3 demo (synthetic)', '2024-01-01',
     'b0eebc99-9c0b-4ef8-bb6d-6bb9bd380a11',
     'REGULATION', 'PROVINCIAL',
     '{"chain_id": "demo_640", "source_file_sha256": "0000000000000000000000000000000000000000000000000000000000000002",
       "source_file_url": "https://demo.placeholder/m4_3",
       "extractor_version": "demo_v1", "is_demo": "true"}'::jsonb),
    ('c1eebc99-9c0b-4ef8-bb6d-6bb9bd380a32', 'NOTICE',
     'demo-policy-document-2', 'M4.3 demo (synthetic)', '2024-02-01',
     'b0eebc99-9c0b-4ef8-bb6d-6bb9bd380a11',
     'NOTICE', 'PROVINCIAL',
     '{"chain_id": "demo_640", "source_file_sha256": "0000000000000000000000000000000000000000000000000000000000000002",
       "source_file_url": "https://demo.placeholder/m4_3",
       "extractor_version": "demo_v1", "is_demo": "true"}'::jsonb),
    ('c1eebc99-9c0b-4ef8-bb6d-6bb9bd380a33', 'PLAN',
     'demo-policy-document-3', 'M4.3 demo (synthetic)', '2024-03-01',
     'b0eebc99-9c0b-4ef8-bb6d-6bb9bd380a11',
     'PLAN', 'PROVINCIAL',
     '{"chain_id": "demo_640", "source_file_sha256": "0000000000000000000000000000000000000000000000000000000000000002",
       "source_file_url": "https://demo.placeholder/m4_3",
       "extractor_version": "demo_v1", "is_demo": "true"}'::jsonb)
ON CONFLICT (id) DO NOTHING;

-- ----------------------------------------------------------------------------
-- 5. 3 个 demo policy_target (FK → 上 3 条 demo policy_document)
-- ----------------------------------------------------------------------------
INSERT INTO policy_target (
    id, policy_document_id, target_description,
    target_value, target_unit, target_year, measurable, lineage
) VALUES
    ('d1eebc99-9c0b-4ef8-bb6d-6bb9bd380a41',
     'c1eebc99-9c0b-4ef8-bb6d-6bb9bd380a31',
     'demo-policy-target-1', 1.0, '百分比', 2024, TRUE,
     '{"chain_id": "demo_640", "source_file_sha256": "0000000000000000000000000000000000000000000000000000000000000002",
       "source_file_url": "https://demo.placeholder/m4_3",
       "extractor_version": "demo_v1", "is_demo": "true"}'::jsonb),
    ('d1eebc99-9c0b-4ef8-bb6d-6bb9bd380a42',
     'c1eebc99-9c0b-4ef8-bb6d-6bb9bd380a32',
     'demo-policy-target-2', 2.0, '百分比', 2025, TRUE,
     '{"chain_id": "demo_640", "source_file_sha256": "0000000000000000000000000000000000000000000000000000000000000002",
       "source_file_url": "https://demo.placeholder/m4_3",
       "extractor_version": "demo_v1", "is_demo": "true"}'::jsonb),
    ('d1eebc99-9c0b-4ef8-bb6d-6bb9bd380a43',
     'c1eebc99-9c0b-4ef8-bb6d-6bb9bd380a33',
     'demo-policy-target-3', 3.0, '百分比', 2026, TRUE,
     '{"chain_id": "demo_640", "source_file_sha256": "0000000000000000000000000000000000000000000000000000000000000002",
       "source_file_url": "https://demo.placeholder/m4_3",
       "extractor_version": "demo_v1", "is_demo": "true"}'::jsonb)
ON CONFLICT (id) DO NOTHING;

-- ----------------------------------------------------------------------------
-- 6. 3 个 demo policy_measure (FK → 上 3 条 demo policy_document)
-- ----------------------------------------------------------------------------
INSERT INTO policy_measure (
    id, policy_document_id, measure_description, measure_type, lineage
) VALUES
    ('d2eebc99-9c0b-4ef8-bb6d-6bb9bd380a51',
     'c1eebc99-9c0b-4ef8-bb6d-6bb9bd380a31',
     'demo-policy-measure-1', 'INCENTIVE',
     '{"chain_id": "demo_640", "source_file_sha256": "0000000000000000000000000000000000000000000000000000000000000002",
       "source_file_url": "https://demo.placeholder/m4_3",
       "extractor_version": "demo_v1", "is_demo": "true"}'::jsonb),
    ('d2eebc99-9c0b-4ef8-bb6d-6bb9bd380a52',
     'c1eebc99-9c0b-4ef8-bb6d-6bb9bd380a32',
     'demo-policy-measure-2', 'REGULATORY',
     '{"chain_id": "demo_640", "source_file_sha256": "0000000000000000000000000000000000000000000000000000000000000002",
       "source_file_url": "https://demo.placeholder/m4_3",
       "extractor_version": "demo_v1", "is_demo": "true"}'::jsonb),
    ('d2eebc99-9c0b-4ef8-bb6d-6bb9bd380a53',
     'c1eebc99-9c0b-4ef8-bb6d-6bb9bd380a33',
     'demo-policy-measure-3', 'INVESTMENT',
     '{"chain_id": "demo_640", "source_file_sha256": "0000000000000000000000000000000000000000000000000000000000000002",
       "source_file_url": "https://demo.placeholder/m4_3",
       "extractor_version": "demo_v1", "is_demo": "true"}'::jsonb)
ON CONFLICT (id) DO NOTHING;

-- ----------------------------------------------------------------------------
-- 7. 3 个 demo government_commitment
--    (FK → 上 3 条 demo policy_target + 上 3 个 demo geo_entity)
--    proposer_person_id = NULL (避免 FK 到 639 person demo;保持 6 表 demo 自洽)
-- ----------------------------------------------------------------------------
INSERT INTO government_commitment (
    id, policy_target_id, commitment_text,
    proposer_person_id, geo_entity_id, commitment_date,
    due_date, status, source_id, lineage
) VALUES
    ('e1eebc99-9c0b-4ef8-bb6d-6bb9bd380a61',
     'd1eebc99-9c0b-4ef8-bb6d-6bb9bd380a41',
     'demo-commitment-1', NULL,
     'f1eebc99-9c0b-4ef8-bb6d-6bb9bd380c01',
     '2024-01-15', '2024-12-31', 'PROPOSED',
     'b0eebc99-9c0b-4ef8-bb6d-6bb9bd380a11',
     '{"chain_id": "demo_640", "source_file_sha256": "0000000000000000000000000000000000000000000000000000000000000002",
       "source_file_url": "https://demo.placeholder/m4_3",
       "extractor_version": "demo_v1", "is_demo": "true"}'::jsonb),
    ('e1eebc99-9c0b-4ef8-bb6d-6bb9bd380a62',
     'd1eebc99-9c0b-4ef8-bb6d-6bb9bd380a42',
     'demo-commitment-2', NULL,
     'f2eebc99-9c0b-4ef8-bb6d-6bb9bd380c02',
     '2024-02-15', '2024-12-31', 'IN_PROGRESS',
     'b0eebc99-9c0b-4ef8-bb6d-6bb9bd380a11',
     '{"chain_id": "demo_640", "source_file_sha256": "0000000000000000000000000000000000000000000000000000000000000002",
       "source_file_url": "https://demo.placeholder/m4_3",
       "extractor_version": "demo_v1", "is_demo": "true"}'::jsonb),
    ('e1eebc99-9c0b-4ef8-bb6d-6bb9bd380a63',
     'd1eebc99-9c0b-4ef8-bb6d-6bb9bd380a43',
     'demo-commitment-3', NULL,
     'f3eebc99-9c0b-4ef8-bb6d-6bb9bd380c03',
     '2024-03-15', '2024-12-31', 'FULFILLED',
     'b0eebc99-9c0b-4ef8-bb6d-6bb9bd380a11',
     '{"chain_id": "demo_640", "source_file_sha256": "0000000000000000000000000000000000000000000000000000000000000002",
       "source_file_url": "https://demo.placeholder/m4_3",
       "extractor_version": "demo_v1", "is_demo": "true"}'::jsonb)
ON CONFLICT (id) DO NOTHING;

-- ----------------------------------------------------------------------------
-- 8. 3 个 demo commitment_progress (FK → 上 3 条 demo government_commitment)
-- ----------------------------------------------------------------------------
INSERT INTO commitment_progress (
    id, commitment_id, progress_date,
    progress_value, progress_unit, progress_note, source_id, lineage
) VALUES
    ('e2eebc99-9c0b-4ef8-bb6d-6bb9bd380a71',
     'e1eebc99-9c0b-4ef8-bb6d-6bb9bd380a61',
     '2024-06-30', 0.5, '百分比', 'demo progress 50%',
     'b0eebc99-9c0b-4ef8-bb6d-6bb9bd380a11',
     '{"chain_id": "demo_640", "source_file_sha256": "0000000000000000000000000000000000000000000000000000000000000002",
       "source_file_url": "https://demo.placeholder/m4_3",
       "extractor_version": "demo_v1", "is_demo": "true"}'::jsonb),
    ('e2eebc99-9c0b-4ef8-bb6d-6bb9bd380a72',
     'e1eebc99-9c0b-4ef8-bb6d-6bb9bd380a62',
     '2024-06-30', 1.0, '百分比', 'demo progress 50% (mid-year)',
     'b0eebc99-9c0b-4ef8-bb6d-6bb9bd380a11',
     '{"chain_id": "demo_640", "source_file_sha256": "0000000000000000000000000000000000000000000000000000000000000002",
       "source_file_url": "https://demo.placeholder/m4_3",
       "extractor_version": "demo_v1", "is_demo": "true"}'::jsonb),
    ('e2eebc99-9c0b-4ef8-bb6d-6bb9bd380a73',
     'e1eebc99-9c0b-4ef8-bb6d-6bb9bd380a63',
     '2024-09-30', 3.0, '百分比', 'demo progress 100% fulfilled',
     'b0eebc99-9c0b-4ef8-bb6d-6bb9bd380a11',
     '{"chain_id": "demo_640", "source_file_sha256": "0000000000000000000000000000000000000000000000000000000000000002",
       "source_file_url": "https://demo.placeholder/m4_3",
       "extractor_version": "demo_v1", "is_demo": "true"}'::jsonb)
ON CONFLICT (id) DO NOTHING;

-- ----------------------------------------------------------------------------
-- 9. 3 个 demo project_event (FK → 上 3 个 demo geo_entity)
-- ----------------------------------------------------------------------------
INSERT INTO project_event (
    id, project_name, geo_entity_id, project_type,
    status, event_date, source_id, lineage
) VALUES
    ('f0eebc99-9c0b-4ef8-bb6d-6bb9bd380a81',
     'demo-project-1', 'f1eebc99-9c0b-4ef8-bb6d-6bb9bd380c01',
     'INFRASTRUCTURE', 'ANNOUNCED', '2024-04-01',
     'b0eebc99-9c0b-4ef8-bb6d-6bb9bd380a11',
     '{"chain_id": "demo_640", "source_file_sha256": "0000000000000000000000000000000000000000000000000000000000000002",
       "source_file_url": "https://demo.placeholder/m4_3",
       "extractor_version": "demo_v1", "is_demo": "true"}'::jsonb),
    ('f0eebc99-9c0b-4ef8-bb6d-6bb9bd380a82',
     'demo-project-2', 'f2eebc99-9c0b-4ef8-bb6d-6bb9bd380c02',
     'ENERGY', 'IN_PROGRESS', '2024-05-01',
     'b0eebc99-9c0b-4ef8-bb6d-6bb9bd380a11',
     '{"chain_id": "demo_640", "source_file_sha256": "0000000000000000000000000000000000000000000000000000000000000002",
       "source_file_url": "https://demo.placeholder/m4_3",
       "extractor_version": "demo_v1", "is_demo": "true"}'::jsonb),
    ('f0eebc99-9c0b-4ef8-bb6d-6bb9bd380a83',
     'demo-project-3', 'f3eebc99-9c0b-4ef8-bb6d-6bb9bd380c03',
     'MANUFACTURING', 'COMPLETED', '2024-06-01',
     'b0eebc99-9c0b-4ef8-bb6d-6bb9bd380a11',
     '{"chain_id": "demo_640", "source_file_sha256": "0000000000000000000000000000000000000000000000000000000000000002",
       "source_file_url": "https://demo.placeholder/m4_3",
       "extractor_version": "demo_v1", "is_demo": "true"}'::jsonb)
ON CONFLICT (id) DO NOTHING;

COMMIT;

RESET search_path;
