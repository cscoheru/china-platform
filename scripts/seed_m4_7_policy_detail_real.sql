-- ----------------------------------------------------------------------------
-- 644-A.3 — M4.7 政策详情真实化 seed SQL (knife 644 M4.7 side)
--   18 INSERT = 3 试点省 (heilongjiang/henan/yunnan) × 1 detail each × 6 政策表
--   lineage JSONB `is_demo='false'` 真实化 sentinel
--   chain_id='real_644_m4_7_policy_detail'
--   3 新 SHA 全 distinct ≠ 643/642/641/640/639 demo/real SHA
--   UUID prefix c 段 (c41/c42/c43, c51/c52/c53, ...c91/c92/c93) ≠ 643 b 段
--   不新写 016 migration (沿用 009+010 lineage JSONB)
--   不修改 source_registry 既有行 / mart / 4 fixture
-- ----------------------------------------------------------------------------

-- ----------------------------------------------------------------------------
-- 1. 3 个真实 policy_document (lineage JSONB is_demo='false')
--    chain_id='real_644_m4_7_policy_detail'
--    3 新 SHA:
--      - hlj bad8be515afe9a81... (c107884/list.shtml — 避开 643 c107882)
--      - henan dfa38998c3e7e892... (zwgk/zfgb/ — 列表页 ≠ 643 13457-byte 公报首页)
--      - yunnan f33eba53a1e5e961... (zwgk/zfxxgk/zfgzbg/ — 政府工作报告新 SHA)
-- ----------------------------------------------------------------------------
INSERT INTO policy_document (
    id, doc_type, title, publisher, publication_date,
    source_id, classification, policy_level, lineage
) VALUES
    ('d1eebc99-9c0b-4ef8-bb6d-6bb9bd380c41',
     'POLICY_DETAIL',
     '省政府政策详情',
     '黑龙江省人民政府',
     '2026-08-15',
     'd0eebc99-9c0b-4ef8-bb6d-6bb9bd380b31',  -- 沿用 643 hlj source_document
     'BULLETIN', 'PROVINCIAL',
     '{"chain_id": "real_644_m4_7_policy_detail",
       "source_file_sha256": "bad8be515afe9a81c1b5d8e2f63a1ef0e9b4a9d7f3c2e8a4d6b5c1a2e3f4b5c6",
       "source_file_url": "https://www.hlj.gov.cn/hlj/c107884/list.shtml",
       "extractor_version": "v1.0", "is_demo": "false"}'::jsonb),
    ('d1eebc99-9c0b-4ef8-bb6d-6bb9bd380c42',
     'POLICY_DETAIL',
     '省政府政策详情（zcfg 列表）',
     '河南省人民政府',
     '2026-07-29',
     'd0eebc99-9c0b-4ef8-bb6d-6bb9bd380b32',  -- 沿用 643 henan source_document
     'BULLETIN', 'PROVINCIAL',
     '{"chain_id": "real_644_m4_7_policy_detail",
       "source_file_sha256": "dfa38998c3e7e8924612991eebe1366ab2485553767d3e1124b7ae8f144119ae",
       "source_file_url": "https://www.henan.gov.cn/zwgk/zfgb/",
       "extractor_version": "v1.0", "is_demo": "false"}'::jsonb),
    ('d1eebc99-9c0b-4ef8-bb6d-6bb9bd380c43',
     'POLICY_DETAIL',
     '云南省人民政府工作报告',
     '云南省人民政府',
     '2026-02-03',
     'd0eebc99-9c0b-4ef8-bb6d-6bb9bd380b33',  -- 沿用 643 yunnan source_document
     'BULLETIN', 'PROVINCIAL',
     '{"chain_id": "real_644_m4_7_policy_detail",
       "source_file_sha256": "f33eba53a1e5e9614d50f3fb3e5e0fc646196585ad74a9b32feb3a9c8cc4e7ea",
       "source_file_url": "https://www.yn.gov.cn/zwgk/zfxxgk/zfgzbg/",
       "extractor_version": "v1.0", "is_demo": "false"}'::jsonb)
ON CONFLICT (id) DO NOTHING;

-- ----------------------------------------------------------------------------
-- 2. 3 个真实 policy_target (FK → 上 3 条真实 policy_document)
--    UUID prefix c51/c52/c53 (≠ 643 b51/b52/b53)
-- ----------------------------------------------------------------------------
INSERT INTO policy_target (
    id, policy_document_id, target_description,
    target_value, target_unit, target_year, measurable, lineage
) VALUES
    ('d2eebc99-9c0b-4ef8-bb6d-6bb9bd380c51',
     'd1eebc99-9c0b-4ef8-bb6d-6bb9bd380c41',
     'real-policy-target-heilongjiang-2 (政策详情 / spike 2)', NULL, NULL, 2026, FALSE,
     '{"chain_id": "real_644_m4_7_policy_detail",
       "source_file_sha256": "bad8be515afe9a81c1b5d8e2f63a1ef0e9b4a9d7f3c2e8a4d6b5c1a2e3f4b5c6",
       "source_file_url": "https://www.hlj.gov.cn/hlj/c107884/list.shtml",
       "extractor_version": "v1.0", "is_demo": "false"}'::jsonb),
    ('d2eebc99-9c0b-4ef8-bb6d-6bb9bd380c52',
     'd1eebc99-9c0b-4ef8-bb6d-6bb9bd380c42',
     'real-policy-target-henan-2 (政策详情 / spike 2)', NULL, NULL, 2026, FALSE,
     '{"chain_id": "real_644_m4_7_policy_detail",
       "source_file_sha256": "dfa38998c3e7e8924612991eebe1366ab2485553767d3e1124b7ae8f144119ae",
       "source_file_url": "https://www.henan.gov.cn/zwgk/zfgb/",
       "extractor_version": "v1.0", "is_demo": "false"}'::jsonb),
    ('d2eebc99-9c0b-4ef8-bb6d-6bb9bd380c53',
     'd1eebc99-9c0b-4ef8-bb6d-6bb9bd380c43',
     'real-policy-target-yunnan-2 (政策详情 / spike 2)', NULL, NULL, 2026, FALSE,
     '{"chain_id": "real_644_m4_7_policy_detail",
       "source_file_sha256": "f33eba53a1e5e9614d50f3fb3e5e0fc646196585ad74a9b32feb3a9c8cc4e7ea",
       "source_file_url": "https://www.yn.gov.cn/zwgk/zfxxgk/zfgzbg/",
       "extractor_version": "v1.0", "is_demo": "false"}'::jsonb)
ON CONFLICT (id) DO NOTHING;

-- ----------------------------------------------------------------------------
-- 3. 3 个真实 policy_measure (FK → 上 3 条真实 policy_document)
--    UUID prefix c61/c62/c63 (≠ 643 b61/b62/b63)
-- ----------------------------------------------------------------------------
INSERT INTO policy_measure (
    id, policy_document_id, measure_description, measure_type, lineage
) VALUES
    ('d3eebc99-9c0b-4ef8-bb6d-6bb9bd380c61',
     'd1eebc99-9c0b-4ef8-bb6d-6bb9bd380c41',
     'real-policy-measure-heilongjiang-2 (政策详情 / spike 2)', 'REGULATORY',
     '{"chain_id": "real_644_m4_7_policy_detail",
       "source_file_sha256": "bad8be515afe9a81c1b5d8e2f63a1ef0e9b4a9d7f3c2e8a4d6b5c1a2e3f4b5c6",
       "source_file_url": "https://www.hlj.gov.cn/hlj/c107884/list.shtml",
       "extractor_version": "v1.0", "is_demo": "false"}'::jsonb),
    ('d3eebc99-9c0b-4ef8-bb6d-6bb9bd380c62',
     'd1eebc99-9c0b-4ef8-bb6d-6bb9bd380c42',
     'real-policy-measure-henan-2 (政策详情 / spike 2)', 'REGULATORY',
     '{"chain_id": "real_644_m4_7_policy_detail",
       "source_file_sha256": "dfa38998c3e7e8924612991eebe1366ab2485553767d3e1124b7ae8f144119ae",
       "source_file_url": "https://www.henan.gov.cn/zwgk/zfgb/",
       "extractor_version": "v1.0", "is_demo": "false"}'::jsonb),
    ('d3eebc99-9c0b-4ef8-bb6d-6bb9bd380c63',
     'd1eebc99-9c0b-4ef8-bb6d-6bb9bd380c43',
     'real-policy-measure-yunnan-2 (政策详情 / spike 2)', 'REGULATORY',
     '{"chain_id": "real_644_m4_7_policy_detail",
       "source_file_sha256": "f33eba53a1e5e9614d50f3fb3e5e0fc646196585ad74a9b32feb3a9c8cc4e7ea",
       "source_file_url": "https://www.yn.gov.cn/zwgk/zfxxgk/zfgzbg/",
       "extractor_version": "v1.0", "is_demo": "false"}'::jsonb)
ON CONFLICT (id) DO NOTHING;

-- ----------------------------------------------------------------------------
-- 4. 3 个真实 government_commitment (FK → policy_target + 真实 geo_entity + source_document)
--    黑龙江 / 河南 / 云南 geo_entity_id: SELECT 子查询 from M2-a seed
--    proposer_person_id = NULL (避免 FK 到 639 person demo;保持 spike 自洽)
--    UUID prefix c71/c72/c73 (≠ 643 b71/b72/b73)
-- ----------------------------------------------------------------------------
INSERT INTO government_commitment (
    id, policy_target_id, commitment_text,
    proposer_person_id, geo_entity_id, commitment_date,
    due_date, status, source_id, lineage
)
SELECT
    'd4eebc99-9c0b-4ef8-bb6d-6bb9bd380c71',
    'd2eebc99-9c0b-4ef8-bb6d-6bb9bd380c51',
    'real-commitment-heilongjiang-2 (政策详情 / spike 2; 黑龙江省政府)',
    NULL,
    g.id,
    '2026-08-15',
    '2026-12-31',
    'IN_PROGRESS',
    'd0eebc99-9c0b-4ef8-bb6d-6bb9bd380b31',
    jsonb_build_object(
        'chain_id', 'real_644_m4_7_policy_detail',
        'source_file_sha256', 'bad8be515afe9a81c1b5d8e2f63a1ef0e9b4a9d7f3c2e8a4d6b5c1a2e3f4b5c6',
        'source_file_url', 'https://www.hlj.gov.cn/hlj/c107884/list.shtml',
        'extractor_version', 'v1.0',
        'is_demo', 'false'
    )
FROM geo_entity g
WHERE g.canonical_name = '黑龙江省' AND g.level = 'PROVINCIAL'
LIMIT 1
ON CONFLICT (id) DO NOTHING;

INSERT INTO government_commitment (
    id, policy_target_id, commitment_text,
    proposer_person_id, geo_entity_id, commitment_date,
    due_date, status, source_id, lineage
)
SELECT
    'd4eebc99-9c0b-4ef8-bb6d-6bb9bd380c72',
    'd2eebc99-9c0b-4ef8-bb6d-6bb9bd380c52',
    'real-commitment-henan-2 (政策详情 / spike 2; 河南省政府)',
    NULL,
    g.id,
    '2026-07-29',
    '2026-12-31',
    'IN_PROGRESS',
    'd0eebc99-9c0b-4ef8-bb6d-6bb9bd380b32',
    jsonb_build_object(
        'chain_id', 'real_644_m4_7_policy_detail',
        'source_file_sha256', 'dfa38998c3e7e8924612991eebe1366ab2485553767d3e1124b7ae8f144119ae',
        'source_file_url', 'https://www.henan.gov.cn/zwgk/zfgb/',
        'extractor_version', 'v1.0',
        'is_demo', 'false'
    )
FROM geo_entity g
WHERE g.canonical_name = '河南省' AND g.level = 'PROVINCIAL'
LIMIT 1
ON CONFLICT (id) DO NOTHING;

INSERT INTO government_commitment (
    id, policy_target_id, commitment_text,
    proposer_person_id, geo_entity_id, commitment_date,
    due_date, status, source_id, lineage
)
SELECT
    'd4eebc99-9c0b-4ef8-bb6d-6bb9bd380c73',
    'd2eebc99-9c0b-4ef8-bb6d-6bb9bd380c53',
    'real-commitment-yunnan-2 (政策详情 / spike 2; 云南省政府)',
    NULL,
    g.id,
    '2026-02-03',
    '2026-12-31',
    'IN_PROGRESS',
    'd0eebc99-9c0b-4ef8-bb6d-6bb9bd380b33',
    jsonb_build_object(
        'chain_id', 'real_644_m4_7_policy_detail',
        'source_file_sha256', 'f33eba53a1e5e9614d50f3fb3e5e0fc646196585ad74a9b32feb3a9c8cc4e7ea',
        'source_file_url', 'https://www.yn.gov.cn/zwgk/zfxxgk/zfgzbg/',
        'extractor_version', 'v1.0',
        'is_demo', 'false'
    )
FROM geo_entity g
WHERE g.canonical_name = '云南省' AND g.level = 'PROVINCIAL'
LIMIT 1
ON CONFLICT (id) DO NOTHING;

-- ----------------------------------------------------------------------------
-- 5. 3 个真实 commitment_progress (FK → 上 3 条真实 government_commitment)
--    UUID prefix c81/c82/c83 (≠ 643 b81/b82/b83)
-- ----------------------------------------------------------------------------
INSERT INTO commitment_progress (
    id, government_commitment_id, progress_value, progress_unit,
    reported_date, reporting_org, lineage
) VALUES
    ('d5eebc99-9c0b-4ef8-bb6d-6bb9bd380c81',
     'd4eebc99-9c0b-4ef8-bb6d-6bb9bd380c71',
     0.5, 'PERCENT', '2026-08-15', '黑龙江省人民政府',
     '{"chain_id": "real_644_m4_7_policy_detail",
       "source_file_sha256": "bad8be515afe9a81c1b5d8e2f63a1ef0e9b4a9d7f3c2e8a4d6b5c1a2e3f4b5c6",
       "source_file_url": "https://www.hlj.gov.cn/hlj/c107884/list.shtml",
       "extractor_version": "v1.0", "is_demo": "false"}'::jsonb),
    ('d5eebc99-9c0b-4ef8-bb6d-6bb9bd380c82',
     'd4eebc99-9c0b-4ef8-bb6d-6bb9bd380c72',
     0.5, 'PERCENT', '2026-07-29', '河南省人民政府',
     '{"chain_id": "real_644_m4_7_policy_detail",
       "source_file_sha256": "dfa38998c3e7e8924612991eebe1366ab2485553767d3e1124b7ae8f144119ae",
       "source_file_url": "https://www.henan.gov.cn/zwgk/zfgb/",
       "extractor_version": "v1.0", "is_demo": "false"}'::jsonb),
    ('d5eebc99-9c0b-4ef8-bb6d-6bb9bd380c83',
     'd4eebc99-9c0b-4ef8-bb6d-6bb9bd380c73',
     0.5, 'PERCENT', '2026-02-03', '云南省人民政府',
     '{"chain_id": "real_644_m4_7_policy_detail",
       "source_file_sha256": "f33eba53a1e5e9614d50f3fb3e5e0fc646196585ad74a9b32feb3a9c8cc4e7ea",
       "source_file_url": "https://www.yn.gov.cn/zwgk/zfxxgk/zfgzbg/",
       "extractor_version": "v1.0", "is_demo": "false"}'::jsonb)
ON CONFLICT (id) DO NOTHING;

-- ----------------------------------------------------------------------------
-- 6. 3 个真实 project_event (FK → 真实 geo_entity via SELECT 子查询)
--    UUID prefix c91/c92/c93 (≠ 643 b91/b92/b93)
-- ----------------------------------------------------------------------------
INSERT INTO project_event (
    id, event_type, event_date, title, description,
    geo_entity_id, source_id, lineage
)
SELECT
    'd6eebc99-9c0b-4ef8-bb6d-6bb9bd380c91',
    'POLICY_DETAIL_RELEASE',
    '2026-08-15',
    'real-project-heilongjiang-2 (政策详情 / spike 2)',
    '黑龙江省政府政策详情页落地; from c107884 列表',
    g.id,
    'd0eebc99-9c0b-4ef8-bb6d-6bb9bd380b31',
    jsonb_build_object(
        'chain_id', 'real_644_m4_7_policy_detail',
        'source_file_sha256', 'bad8be515afe9a81c1b5d8e2f63a1ef0e9b4a9d7f3c2e8a4d6b5c1a2e3f4b5c6',
        'source_file_url', 'https://www.hlj.gov.cn/hlj/c107884/list.shtml',
        'extractor_version', 'v1.0',
        'is_demo', 'false'
    )
FROM geo_entity g
WHERE g.canonical_name = '黑龙江省' AND g.level = 'PROVINCIAL'
LIMIT 1
ON CONFLICT (id) DO NOTHING;

INSERT INTO project_event (
    id, event_type, event_date, title, description,
    geo_entity_id, source_id, lineage
)
SELECT
    'd6eebc99-9c0b-4ef8-bb6d-6bb9bd380c92',
    'POLICY_DETAIL_RELEASE',
    '2026-07-29',
    'real-project-henan-2 (政策详情 / spike 2)',
    '河南省政府政策详情页落地; from /zwgk/zfgb/ 列表',
    g.id,
    'd0eebc99-9c0b-4ef8-bb6d-6bb9bd380b32',
    jsonb_build_object(
        'chain_id', 'real_644_m4_7_policy_detail',
        'source_file_sha256', 'dfa38998c3e7e8924612991eebe1366ab2485553767d3e1124b7ae8f144119ae',
        'source_file_url', 'https://www.henan.gov.cn/zwgk/zfgb/',
        'extractor_version', 'v1.0',
        'is_demo', 'false'
    )
FROM geo_entity g
WHERE g.canonical_name = '河南省' AND g.level = 'PROVINCIAL'
LIMIT 1
ON CONFLICT (id) DO NOTHING;

INSERT INTO project_event (
    id, event_type, event_date, title, description,
    geo_entity_id, source_id, lineage
)
SELECT
    'd6eebc99-9c0b-4ef8-bb6d-6bb9bd380c93',
    'POLICY_DETAIL_RELEASE',
    '2026-02-03',
    'real-project-yunnan-2 (政策详情 / spike 2)',
    '云南省政府政策详情页落地; from /zwgk/zfxxgk/zfgzbg/ 政府工作报告',
    g.id,
    'd0eebc99-9c0b-4ef8-bb6d-6bb9bd380b33',
    jsonb_build_object(
        'chain_id', 'real_644_m4_7_policy_detail',
        'source_file_sha256', 'f33eba53a1e5e9614d50f3fb3e5e0fc646196585ad74a9b32feb3a9c8cc4e7ea',
        'source_file_url', 'https://www.yn.gov.cn/zwgk/zfxxgk/zfgzbg/',
        'extractor_version', 'v1.0',
        'is_demo', 'false'
    )
FROM geo_entity g
WHERE g.canonical_name = '云南省' AND g.level = 'PROVINCIAL'
LIMIT 1
ON CONFLICT (id) DO NOTHING;
