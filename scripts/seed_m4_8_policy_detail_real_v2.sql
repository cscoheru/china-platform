-- ----------------------------------------------------------------------------
-- 645-A.3 — M4.8 政策详情 v2 真实化 seed SQL (knife 645 M4.8 side)
--   24 INSERT = 4 样本 (heilongjiang/henan-zfgb/henan-zwgk/yunnan) × 1 detail each × 6 政策表
--   + 4 source_registry + 4 source_document = 32 INSERT total
--   lineage JSONB `is demo='false'` 真实化 sentinel
--   chain_id='real_645_m4_8_policy_detail_v2' (v2 标记 = 第 4 样本纳入; ≠ 644 chain_id)
--   4 新 SHA 全 distinct ≠ 644/643/642/641/640/639 demo/real SHA
--     - hlj     `6237cd48afc60c06...` (c107884/list.shtml — 644 bad8be51 → 645 drift 6237cd48)
--     - henan-z `dfa38998c3e7e892...` (/zwgk/zfgb/ — 沿用 644 SHA)
--     - henan-r `bd4c4c51b8f371e2...` (/zwgk/ — NEW 第 4 样本, 644 留作扩展)
--     - yunnan  `f33eba53a1e5e961...` (/zwgk/zfxxgk/zfgzbg/ — 沿用 644 SHA)
--   UUID prefix d 段 (d21-d94) ≠ 644 c 段 (c41-c93)
--   不新写 016 migration (沿用 009+010 lineage JSONB)
--   不修改 source_registry 既有 638/640/641/642/643 行 / mart / 4 fixture
-- ----------------------------------------------------------------------------

-- ----------------------------------------------------------------------------
-- 0. 4 个真实 source_registry (lineage JSONB is_demo='false')
--    chain_id='real_645_m4_8_policy_detail_v2'
--    UUID prefix d21/d22/d23/d24 (≠ 644 b31/b32/b33 (643 沿用))
-- ----------------------------------------------------------------------------
INSERT INTO source_registry (
    id, source_url, source_name, source_type,
    country, province, enabled, lineage
) VALUES
    ('d0eebc99-9c0b-4ef8-bb6d-6bb9bd380d21',
     'https://www.hlj.gov.cn/hlj/c107884/list.shtml',
     '黑龙江省人民政府 政策详情列表',
     'PROVINCIAL_BULLETIN',
     'CN', 'HEILONGJIANG', TRUE,
     '{"chain_id": "real_645_m4_8_policy_detail_v2",
       "source_file_sha256": "6237cd48afc60c0641bb7b558ecdbf5e04e36b6e06c0839947b925b50fe5200a",
       "source_file_url": "https://www.hlj.gov.cn/hlj/c107884/list.shtml",
       "extractor_version": "v1.0", "is_demo": "false"}'::jsonb),
    ('d0eebc99-9c0b-4ef8-bb6d-6bb9bd380d22',
     'https://www.henan.gov.cn/zwgk/zfgb/',
     '河南省人民政府 政策文件列表',
     'PROVINCIAL_BULLETIN',
     'CN', 'HENAN', TRUE,
     '{"chain_id": "real_645_m4_8_policy_detail_v2",
       "source_file_sha256": "dfa38998c3e7e8924612991eebe1366ab2485553767d3e1124b7ae8f144119ae",
       "source_file_url": "https://www.henan.gov.cn/zwgk/zfgb/",
       "extractor_version": "v1.0", "is_demo": "false"}'::jsonb),
    ('d0eebc99-9c0b-4ef8-bb6d-6bb9bd380d23',
     'https://www.henan.gov.cn/zwgk/',
     '河南省人民政府 政务公开 root',
     'PROVINCIAL_BULLETIN',
     'CN', 'HENAN', TRUE,
     '{"chain_id": "real_645_m4_8_policy_detail_v2",
       "source_file_sha256": "bd4c4c51b8f371e2f1b3fb8acb2b3bf3441a27213b4464e39fdb99b56270d0b9",
       "source_file_url": "https://www.henan.gov.cn/zwgk/",
       "extractor_version": "v1.0", "is_demo": "false"}'::jsonb),
    ('d0eebc99-9c0b-4ef8-bb6d-6bb9bd380d24',
     'https://www.yn.gov.cn/zwgk/zfxxgk/zfgzbg/',
     '云南省人民政府 政府工作报告',
     'PROVINCIAL_BULLETIN',
     'CN', 'YUNNAN', TRUE,
     '{"chain_id": "real_645_m4_8_policy_detail_v2",
       "source_file_sha256": "f33eba53a1e5e9614d50f3fb3e5e0fc646196585ad74a9b32feb3a9c8cc4e7ea",
       "source_file_url": "https://www.yn.gov.cn/zwgk/zfxxgk/zfgzbg/",
       "extractor_version": "v1.0", "is_demo": "false"}'::jsonb)
ON CONFLICT (id) DO NOTHING;

-- ----------------------------------------------------------------------------
-- 0b. 4 个真实 source_document (lineage JSONB is_demo='false')
--     UUID prefix d31/d32/d33/d34
-- ----------------------------------------------------------------------------
INSERT INTO source_document (
    id, source_id, title, doc_kind, content_url,
    captured_at, file_hash_sha256, file_size_bytes, lineage
) VALUES
    ('d0eebc99-9c0b-4ef8-bb6d-6bb9bd380d31',
     'd0eebc99-9c0b-4ef8-bb6d-6bb9bd380d21',
     '黑龙江省人民政府 政策详情列表 landing',
     'POLICY_DETAIL_LIST',
     'https://www.hlj.gov.cn/hlj/c107884/list.shtml',
     '2026-09-01',
     '6237cd48afc60c0641bb7b558ecdbf5e04e36b6e06c0839947b925b50fe5200a',
     148507,
     '{"chain_id": "real_645_m4_8_policy_detail_v2",
       "source_file_sha256": "6237cd48afc60c0641bb7b558ecdbf5e04e36b6e06c0839947b925b50fe5200a",
       "source_file_url": "https://www.hlj.gov.cn/hlj/c107884/list.shtml",
       "extractor_version": "v1.0", "is_demo": "false"}'::jsonb),
    ('d0eebc99-9c0b-4ef8-bb6d-6bb9bd380d32',
     'd0eebc99-9c0b-4ef8-bb6d-6bb9bd380d22',
     '河南省人民政府 政策文件列表 landing',
     'POLICY_DETAIL_LIST',
     'https://www.henan.gov.cn/zwgk/zfgb/',
     '2026-09-01',
     'dfa38998c3e7e8924612991eebe1366ab2485553767d3e1124b7ae8f144119ae',
     8959,
     '{"chain_id": "real_645_m4_8_policy_detail_v2",
       "source_file_sha256": "dfa38998c3e7e8924612991eebe1366ab2485553767d3e1124b7ae8f144119ae",
       "source_file_url": "https://www.henan.gov.cn/zwgk/zfgb/",
       "extractor_version": "v1.0", "is_demo": "false"}'::jsonb),
    ('d0eebc99-9c0b-4ef8-bb6d-6bb9bd380d33',
     'd0eebc99-9c0b-4ef8-bb6d-6bb9bd380d23',
     '河南省人民政府 政务公开 root landing',
     'PROVINCIAL_BULLETIN',
     'https://www.henan.gov.cn/zwgk/',
     '2026-09-01',
     'bd4c4c51b8f371e2f1b3fb8acb2b3bf3441a27213b4464e39fdb99b56270d0b9',
     158029,
     '{"chain_id": "real_645_m4_8_policy_detail_v2",
       "source_file_sha256": "bd4c4c51b8f371e2f1b3fb8acb2b3bf3441a27213b4464e39fdb99b56270d0b9",
       "source_file_url": "https://www.henan.gov.cn/zwgk/",
       "extractor_version": "v1.0", "is_demo": "false"}'::jsonb),
    ('d0eebc99-9c0b-4ef8-bb6d-6bb9bd380d34',
     'd0eebc99-9c0b-4ef8-bb6d-6bb9bd380d24',
     '云南省人民政府 政府工作报告列表',
     'PROVINCIAL_BULLETIN',
     'https://www.yn.gov.cn/zwgk/zfxxgk/zfgzbg/',
     '2026-09-01',
     'f33eba53a1e5e9614d50f3fb3e5e0fc646196585ad74a9b32feb3a9c8cc4e7ea',
     94310,
     '{"chain_id": "real_645_m4_8_policy_detail_v2",
       "source_file_sha256": "f33eba53a1e5e9614d50f3fb3e5e0fc646196585ad74a9b32feb3a9c8cc4e7ea",
       "source_file_url": "https://www.yn.gov.cn/zwgk/zfxxgk/zfgzbg/",
       "extractor_version": "v1.0", "is_demo": "false"}'::jsonb)
ON CONFLICT (id) DO NOTHING;

-- ----------------------------------------------------------------------------
-- 1. 4 个真实 policy_document (lineage JSONB is_demo='false')
--    chain_id='real_645_m4_8_policy_detail_v2'
--    UUID prefix d41/d42/d43/d44 (≠ 644 c41/c42/c43)
-- ----------------------------------------------------------------------------
INSERT INTO policy_document (
    id, doc_type, title, publisher, publication_date,
    source_id, classification, policy_level, lineage
) VALUES
    ('d1eebc99-9c0b-4ef8-bb6d-6bb9bd380d41',
     'POLICY_DETAIL',
     '省政府政策详情 v2',
     '黑龙江省人民政府',
     '2026-08-15',
     'd0eebc99-9c0b-4ef8-bb6d-6bb9bd380d31',
     'BULLETIN', 'PROVINCIAL',
     '{"chain_id": "real_645_m4_8_policy_detail_v2",
       "source_file_sha256": "6237cd48afc60c0641bb7b558ecdbf5e04e36b6e06c0839947b925b50fe5200a",
       "source_file_url": "https://www.hlj.gov.cn/hlj/c107884/list.shtml",
       "extractor_version": "v1.0", "is_demo": "false"}'::jsonb),
    ('d1eebc99-9c0b-4ef8-bb6d-6bb9bd380d42',
     'POLICY_DETAIL',
     '省政府政策详情（zcfg 列表 v2）',
     '河南省人民政府',
     '2026-07-29',
     'd0eebc99-9c0b-4ef8-bb6d-6bb9bd380d32',
     'BULLETIN', 'PROVINCIAL',
     '{"chain_id": "real_645_m4_8_policy_detail_v2",
       "source_file_sha256": "dfa38998c3e7e8924612991eebe1366ab2485553767d3e1124b7ae8f144119ae",
       "source_file_url": "https://www.henan.gov.cn/zwgk/zfgb/",
       "extractor_version": "v1.0", "is_demo": "false"}'::jsonb),
    ('d1eebc99-9c0b-4ef8-bb6d-6bb9bd380d43',
     'POLICY_DETAIL',
     '省政府政策详情（zwgk root v2）',
     '河南省人民政府',
     '2026-08-30',
     'd0eebc99-9c0b-4ef8-bb6d-6bb9bd380d33',
     'BULLETIN', 'PROVINCIAL',
     '{"chain_id": "real_645_m4_8_policy_detail_v2",
       "source_file_sha256": "bd4c4c51b8f371e2f1b3fb8acb2b3bf3441a27213b4464e39fdb99b56270d0b9",
       "source_file_url": "https://www.henan.gov.cn/zwgk/",
       "extractor_version": "v1.0", "is_demo": "false"}'::jsonb),
    ('d1eebc99-9c0b-4ef8-bb6d-6bb9bd380d44',
     'POLICY_DETAIL',
     '云南省人民政府工作报告 v2',
     '云南省人民政府',
     '2026-02-03',
     'd0eebc99-9c0b-4ef8-bb6d-6bb9bd380d34',
     'BULLETIN', 'PROVINCIAL',
     '{"chain_id": "real_645_m4_8_policy_detail_v2",
       "source_file_sha256": "f33eba53a1e5e9614d50f3fb3e5e0fc646196585ad74a9b32feb3a9c8cc4e7ea",
       "source_file_url": "https://www.yn.gov.cn/zwgk/zfxxgk/zfgzbg/",
       "extractor_version": "v1.0", "is_demo": "false"}'::jsonb)
ON CONFLICT (id) DO NOTHING;

-- ----------------------------------------------------------------------------
-- 2. 4 个真实 policy_target (FK → 上 4 条真实 policy_document)
--    UUID prefix d51/d52/d53/d54 (≠ 644 c51/c52/c53)
-- ----------------------------------------------------------------------------
INSERT INTO policy_target (
    id, policy_document_id, target_description,
    target_value, target_unit, target_year, measurable, lineage
) VALUES
    ('d2eebc99-9c0b-4ef8-bb6d-6bb9bd380d51',
     'd1eebc99-9c0b-4ef8-bb6d-6bb9bd380d41',
     'real-policy-target-heilongjiang-v2 (政策详情 v2)', NULL, NULL, 2026, FALSE,
     '{"chain_id": "real_645_m4_8_policy_detail_v2",
       "source_file_sha256": "6237cd48afc60c0641bb7b558ecdbf5e04e36b6e06c0839947b925b50fe5200a",
       "source_file_url": "https://www.hlj.gov.cn/hlj/c107884/list.shtml",
       "extractor_version": "v1.0", "is_demo": "false"}'::jsonb),
    ('d2eebc99-9c0b-4ef8-bb6d-6bb9bd380d52',
     'd1eebc99-9c0b-4ef8-bb6d-6bb9bd380d42',
     'real-policy-target-henan-zfgb-v2 (政策详情 v2)', NULL, NULL, 2026, FALSE,
     '{"chain_id": "real_645_m4_8_policy_detail_v2",
       "source_file_sha256": "dfa38998c3e7e8924612991eebe1366ab2485553767d3e1124b7ae8f144119ae",
       "source_file_url": "https://www.henan.gov.cn/zwgk/zfgb/",
       "extractor_version": "v1.0", "is_demo": "false"}'::jsonb),
    ('d2eebc99-9c0b-4ef8-bb6d-6bb9bd380d53',
     'd1eebc99-9c0b-4ef8-bb6d-6bb9bd380d43',
     'real-policy-target-henan-zwgk-v2 (政策详情 v2 / 第 4 样本)', NULL, NULL, 2026, FALSE,
     '{"chain_id": "real_645_m4_8_policy_detail_v2",
       "source_file_sha256": "bd4c4c51b8f371e2f1b3fb8acb2b3bf3441a27213b4464e39fdb99b56270d0b9",
       "source_file_url": "https://www.henan.gov.cn/zwgk/",
       "extractor_version": "v1.0", "is_demo": "false"}'::jsonb),
    ('d2eebc99-9c0b-4ef8-bb6d-6bb9bd380d54',
     'd1eebc99-9c0b-4ef8-bb6d-6bb9bd380d44',
     'real-policy-target-yunnan-v2 (政策详情 v2)', NULL, NULL, 2026, FALSE,
     '{"chain_id": "real_645_m4_8_policy_detail_v2",
       "source_file_sha256": "f33eba53a1e5e9614d50f3fb3e5e0fc646196585ad74a9b32feb3a9c8cc4e7ea",
       "source_file_url": "https://www.yn.gov.cn/zwgk/zfxxgk/zfgzbg/",
       "extractor_version": "v1.0", "is_demo": "false"}'::jsonb)
ON CONFLICT (id) DO NOTHING;

-- ----------------------------------------------------------------------------
-- 3. 4 个真实 policy_measure (FK → 上 4 条真实 policy_document)
--    UUID prefix d61/d62/d63/d64 (≠ 644 c61/c62/c63)
-- ----------------------------------------------------------------------------
INSERT INTO policy_measure (
    id, policy_document_id, measure_description, measure_type, lineage
) VALUES
    ('d3eebc99-9c0b-4ef8-bb6d-6bb9bd380d61',
     'd1eebc99-9c0b-4ef8-bb6d-6bb9bd380d41',
     'real-policy-measure-heilongjiang-v2 (政策详情 v2)', 'REGULATORY',
     '{"chain_id": "real_645_m4_8_policy_detail_v2",
       "source_file_sha256": "6237cd48afc60c0641bb7b558ecdbf5e04e36b6e06c0839947b925b50fe5200a",
       "source_file_url": "https://www.hlj.gov.cn/hlj/c107884/list.shtml",
       "extractor_version": "v1.0", "is_demo": "false"}'::jsonb),
    ('d3eebc99-9c0b-4ef8-bb6d-6bb9bd380d62',
     'd1eebc99-9c0b-4ef8-bb6d-6bb9bd380d42',
     'real-policy-measure-henan-zfgb-v2 (政策详情 v2)', 'REGULATORY',
     '{"chain_id": "real_645_m4_8_policy_detail_v2",
       "source_file_sha256": "dfa38998c3e7e8924612991eebe1366ab2485553767d3e1124b7ae8f144119ae",
       "source_file_url": "https://www.henan.gov.cn/zwgk/zfgb/",
       "extractor_version": "v1.0", "is_demo": "false"}'::jsonb),
    ('d3eebc99-9c0b-4ef8-bb6d-6bb9bd380d63',
     'd1eebc99-9c0b-4ef8-bb6d-6bb9bd380d43',
     'real-policy-measure-henan-zwgk-v2 (政策详情 v2 / 第 4 样本)', 'REGULATORY',
     '{"chain_id": "real_645_m4_8_policy_detail_v2",
       "source_file_sha256": "bd4c4c51b8f371e2f1b3fb8acb2b3bf3441a27213b4464e39fdb99b56270d0b9",
       "source_file_url": "https://www.henan.gov.cn/zwgk/",
       "extractor_version": "v1.0", "is_demo": "false"}'::jsonb),
    ('d3eebc99-9c0b-4ef8-bb6d-6bb9bd380d64',
     'd1eebc99-9c0b-4ef8-bb6d-6bb9bd380d44',
     'real-policy-measure-yunnan-v2 (政策详情 v2)', 'REGULATORY',
     '{"chain_id": "real_645_m4_8_policy_detail_v2",
       "source_file_sha256": "f33eba53a1e5e9614d50f3fb3e5e0fc646196585ad74a9b32feb3a9c8cc4e7ea",
       "source_file_url": "https://www.yn.gov.cn/zwgk/zfxxgk/zfgzbg/",
       "extractor_version": "v1.0", "is_demo": "false"}'::jsonb)
ON CONFLICT (id) DO NOTHING;

-- ----------------------------------------------------------------------------
-- 4. 4 个真实 government_commitment (FK → policy_target + 真实 geo_entity + source_document)
--    黑龙江 / 河南 / 云南 geo_entity_id: SELECT 子查询 from M2-a seed
--    proposer_person_id = NULL (避免 FK 到 639 person demo;保持 spike 自洽)
--    UUID prefix d71/d72/d73/d74 (≠ 644 c71/c72/c73)
-- ----------------------------------------------------------------------------
INSERT INTO government_commitment (
    id, policy_target_id, commitment_text,
    proposer_person_id, geo_entity_id, commitment_date,
    due_date, status, source_id, lineage
)
SELECT
    'd4eebc99-9c0b-4ef8-bb6d-6bb9bd380d71',
    'd2eebc99-9c0b-4ef8-bb6d-6bb9bd380d51',
    'real-commitment-heilongjiang-v2 (政策详情 v2; 黑龙江省政府)',
    NULL,
    g.id,
    '2026-08-15',
    '2026-12-31',
    'IN_PROGRESS',
    'd0eebc99-9c0b-4ef8-bb6d-6bb9bd380d31',
    jsonb_build_object(
        'chain_id', 'real_645_m4_8_policy_detail_v2',
        'source_file_sha256', '6237cd48afc60c0641bb7b558ecdbf5e04e36b6e06c0839947b925b50fe5200a',
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
    'd4eebc99-9c0b-4ef8-bb6d-6bb9bd380d72',
    'd2eebc99-9c0b-4ef8-bb6d-6bb9bd380d52',
    'real-commitment-henan-zfgb-v2 (政策详情 v2; 河南省政府)',
    NULL,
    g.id,
    '2026-07-29',
    '2026-12-31',
    'IN_PROGRESS',
    'd0eebc99-9c0b-4ef8-bb6d-6bb9bd380d32',
    jsonb_build_object(
        'chain_id', 'real_645_m4_8_policy_detail_v2',
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
    'd4eebc99-9c0b-4ef8-bb6d-6bb9bd380d73',
    'd2eebc99-9c0b-4ef8-bb6d-6bb9bd380d53',
    'real-commitment-henan-zwgk-v2 (政策详情 v2 / 第 4 样本; 河南省政府)',
    NULL,
    g.id,
    '2026-08-30',
    '2026-12-31',
    'IN_PROGRESS',
    'd0eebc99-9c0b-4ef8-bb6d-6bb9bd380d33',
    jsonb_build_object(
        'chain_id', 'real_645_m4_8_policy_detail_v2',
        'source_file_sha256', 'bd4c4c51b8f371e2f1b3fb8acb2b3bf3441a27213b4464e39fdb99b56270d0b9',
        'source_file_url', 'https://www.henan.gov.cn/zwgk/',
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
    'd4eebc99-9c0b-4ef8-bb6d-6bb9bd380d74',
    'd2eebc99-9c0b-4ef8-bb6d-6bb9bd380d54',
    'real-commitment-yunnan-v2 (政策详情 v2; 云南省政府)',
    NULL,
    g.id,
    '2026-02-03',
    '2026-12-31',
    'IN_PROGRESS',
    'd0eebc99-9c0b-4ef8-bb6d-6bb9bd380d34',
    jsonb_build_object(
        'chain_id', 'real_645_m4_8_policy_detail_v2',
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
-- 5. 4 个真实 commitment_progress (FK → 上 4 条真实 government_commitment)
--    UUID prefix d81/d82/d83/d84 (≠ 644 c81/c82/c83)
-- ----------------------------------------------------------------------------
INSERT INTO commitment_progress (
    id, government_commitment_id, progress_value, progress_unit,
    reported_date, reporting_org, lineage
) VALUES
    ('d5eebc99-9c0b-4ef8-bb6d-6bb9bd380d81',
     'd4eebc99-9c0b-4ef8-bb6d-6bb9bd380d71',
     0.5, 'PERCENT', '2026-08-15', '黑龙江省人民政府',
     '{"chain_id": "real_645_m4_8_policy_detail_v2",
       "source_file_sha256": "6237cd48afc60c0641bb7b558ecdbf5e04e36b6e06c0839947b925b50fe5200a",
       "source_file_url": "https://www.hlj.gov.cn/hlj/c107884/list.shtml",
       "extractor_version": "v1.0", "is_demo": "false"}'::jsonb),
    ('d5eebc99-9c0b-4ef8-bb6d-6bb9bd380d82',
     'd4eebc99-9c0b-4ef8-bb6d-6bb9bd380d72',
     0.5, 'PERCENT', '2026-07-29', '河南省人民政府',
     '{"chain_id": "real_645_m4_8_policy_detail_v2",
       "source_file_sha256": "dfa38998c3e7e8924612991eebe1366ab2485553767d3e1124b7ae8f144119ae",
       "source_file_url": "https://www.henan.gov.cn/zwgk/zfgb/",
       "extractor_version": "v1.0", "is_demo": "false"}'::jsonb),
    ('d5eebc99-9c0b-4ef8-bb6d-6bb9bd380d83',
     'd4eebc99-9c0b-4ef8-bb6d-6bb9bd380d73',
     0.5, 'PERCENT', '2026-08-30', '河南省人民政府',
     '{"chain_id": "real_645_m4_8_policy_detail_v2",
       "source_file_sha256": "bd4c4c51b8f371e2f1b3fb8acb2b3bf3441a27213b4464e39fdb99b56270d0b9",
       "source_file_url": "https://www.henan.gov.cn/zwgk/",
       "extractor_version": "v1.0", "is_demo": "false"}'::jsonb),
    ('d5eebc99-9c0b-4ef8-bb6d-6bb9bd380d84',
     'd4eebc99-9c0b-4ef8-bb6d-6bb9bd380d74',
     0.5, 'PERCENT', '2026-02-03', '云南省人民政府',
     '{"chain_id": "real_645_m4_8_policy_detail_v2",
       "source_file_sha256": "f33eba53a1e5e9614d50f3fb3e5e0fc646196585ad74a9b32feb3a9c8cc4e7ea",
       "source_file_url": "https://www.yn.gov.cn/zwgk/zfxxgk/zfgzbg/",
       "extractor_version": "v1.0", "is_demo": "false"}'::jsonb)
ON CONFLICT (id) DO NOTHING;

-- ----------------------------------------------------------------------------
-- 6. 4 个真实 project_event (FK → 真实 geo_entity via SELECT 子查询)
--    UUID prefix d91/d92/d93/d94 (≠ 644 c91/c92/c93)
-- ----------------------------------------------------------------------------
INSERT INTO project_event (
    id, event_type, event_date, title, description,
    geo_entity_id, source_id, lineage
)
SELECT
    'd6eebc99-9c0b-4ef8-bb6d-6bb9bd380d91',
    'POLICY_DETAIL_RELEASE',
    '2026-08-15',
    'real-project-heilongjiang-v2 (政策详情 v2)',
    '黑龙江省政府政策详情页落地; from c107884 列表 (drift 6237cd48)',
    g.id,
    'd0eebc99-9c0b-4ef8-bb6d-6bb9bd380d31',
    jsonb_build_object(
        'chain_id', 'real_645_m4_8_policy_detail_v2',
        'source_file_sha256', '6237cd48afc60c0641bb7b558ecdbf5e04e36b6e06c0839947b925b50fe5200a',
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
    'd6eebc99-9c0b-4ef8-bb6d-6bb9bd380d92',
    'POLICY_DETAIL_RELEASE',
    '2026-07-29',
    'real-project-henan-zfgb-v2 (政策详情 v2)',
    '河南省政府政策详情页落地; from /zwgk/zfgb/ 列表',
    g.id,
    'd0eebc99-9c0b-4ef8-bb6d-6bb9bd380d32',
    jsonb_build_object(
        'chain_id', 'real_645_m4_8_policy_detail_v2',
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
    'd6eebc99-9c0b-4ef8-bb6d-6bb9bd380d93',
    'POLICY_DETAIL_RELEASE',
    '2026-08-30',
    'real-project-henan-zwgk-v2 (政策详情 v2 / 第 4 样本)',
    '河南省政府政务公开 root 落地; from /zwgk/ landing (NEW 645 第 4 样本)',
    g.id,
    'd0eebc99-9c0b-4ef8-bb6d-6bb9bd380d33',
    jsonb_build_object(
        'chain_id', 'real_645_m4_8_policy_detail_v2',
        'source_file_sha256', 'bd4c4c51b8f371e2f1b3fb8acb2b3bf3441a27213b4464e39fdb99b56270d0b9',
        'source_file_url', 'https://www.henan.gov.cn/zwgk/',
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
    'd6eebc99-9c0b-4ef8-bb6d-6bb9bd380d94',
    'POLICY_DETAIL_RELEASE',
    '2026-02-03',
    'real-project-yunnan-v2 (政策详情 v2)',
    '云南省政府政策详情页落地; from /zwgk/zfxxgk/zfgzbg/ 政府工作报告',
    g.id,
    'd0eebc99-9c0b-4ef8-bb6d-6bb9bd380d34',
    jsonb_build_object(
        'chain_id', 'real_645_m4_8_policy_detail_v2',
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
-- 645-A.3 spike 边界小结:
--   6 政策表 × 4 真实样本 = 24 INSERT planned
--   + 4 source_registry (d21-d24) + 4 source_document (d31-d34) = 32 INSERT total
--   chain_id='real_645_m4_8_policy_detail_v2' (≠ 644 chain_id)
--   UUID prefix d 段 (d21-d94) ≠ 644 c 段 (c41-c93)
--   4 新 SHA (6237cd48 / dfa38998 / bd4c4c51 / f33eba53) ≠ 644 SHA (bad8be51 漂移到 6237cd48)
--   lineage JSONB is_demo='false' 真实化 sentinel
-- ----------------------------------------------------------------------------
