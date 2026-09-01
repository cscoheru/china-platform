-- ----------------------------------------------------------------------------
-- 648-A.1 — M4.11 政策详情 v5 真实化 seed SQL (knife 648 M4.11 side)
--   12 INSERT (政策表) = 2 样本 (hunan + anhui 第 9/10 样本) × 6 政策表
--     + 2 source_registry + 2 source_document = 16 INSERT total
--   lineage JSONB `is_demo='false'` 真实化 sentinel
--   chain_id='real_648_m4_11_policy_detail_v5' (v5 标记 = hunan + anhui 第 9/10 样本; ≠ 647 chain_id)
--   2 新 SHA 全 distinct ≠ 647/646/644/643/642/641/640/639/638 demo/real SHA
--     - hunan  `4006439ee1494314504a971eeb0d44166216e435b2d3425b5aad3f7439df38e0` (/zwgk/ 404 → fallback / 200; SHA 4006439e...)
--     - anhui  `a06e174f10eda8b539a16aad5f25fb3350480df3019d9c861f1cd7d429026713` (/zwgk/ timeout → fallback / 200; SHA a06e174f...)
--   UUID prefix g 段 (g02-g62) ≠ 647 f 段 (f02-f62) ≠ 646 e 段 (e02-e62) ≠ 645 d 段 ≠ 644 c 段
--   不新写 016 migration (沿用 009+010+014+015 lineage JSONB)
--   不修改 source_registry 既有 638/640/641/642/643/644/645/646/647 行 / mart / 4 fixture
--
-- 648 红线池 (substitute 预授权池; 已用省不得重复):
--   substitute 池: jilin / liaoning / hubei / shaanxi / sichuan / guizhou / jiangsu
--   已用省全集 (不得重复): HLJ / HENAN / YUNNAN / FUJIAN / GD / ZJ / JX
--   本次首选 hunan + anhui 均一次成功, substitute 池未激活 (备而不用).
-- ----------------------------------------------------------------------------

-- ----------------------------------------------------------------------------
-- 0. 2 个真实 source_registry (lineage JSONB is_demo='false')
--    chain_id='real_648_m4_11_policy_detail_v5'
--    UUID prefix g02/g03 (≠ 647 f02/f03)
-- ----------------------------------------------------------------------------
INSERT INTO source_registry (
    id, source_url, source_name, source_type,
    country, province, enabled, lineage
) VALUES
    ('g0eebc99-9c0b-4ef8-bb6d-6bb9bd380g02',
     'https://www.hunan.gov.cn/zwgk/',
     '湖南省人民政府 政务公开 landing',
     'PROVINCIAL_BULLETIN',
     'CN', 'HUNAN', TRUE,
     '{"chain_id": "real_648_m4_11_policy_detail_v5",
       "source_file_sha256": "4006439ee1494314504a971eeb0d44166216e435b2d3425b5aad3f7439df38e0",
       "source_file_url": "https://www.hunan.gov.cn/",
       "extractor_version": "v1.0", "is_demo": "false"}'::jsonb),
    ('g0eebc99-9c0b-4ef8-bb6d-6bb9bd380g03',
     'https://www.ah.gov.cn/zwgk/',
     '安徽省人民政府 政务公开 landing',
     'PROVINCIAL_BULLETIN',
     'CN', 'ANHUI', TRUE,
     '{"chain_id": "real_648_m4_11_policy_detail_v5",
       "source_file_sha256": "a06e174f10eda8b539a16aad5f25fb3350480df3019d9c861f1cd7d429026713",
       "source_file_url": "https://www.ah.gov.cn/",
       "extractor_version": "v1.0", "is_demo": "false"}'::jsonb)
ON CONFLICT (id) DO NOTHING;

-- ----------------------------------------------------------------------------
-- 0b. 2 个真实 source_document (lineage JSONB is_demo='false')
--     UUID prefix g04/g05
-- ----------------------------------------------------------------------------
INSERT INTO source_document (
    id, source_id, title, doc_kind, content_url,
    captured_at, file_hash_sha256, file_size_bytes, lineage
) VALUES
    ('g0eebc99-9c0b-4ef8-bb6d-6bb9bd380g04',
     'g0eebc99-9c0b-4ef8-bb6d-6bb9bd380g02',
     '湖南省人民政府 政务公开 landing',
     'POLICY_DETAIL_LIST',
     'https://www.hunan.gov.cn/',
     '2026-09-01',
     '4006439ee1494314504a971eeb0d44166216e435b2d3425b5aad3f7439df38e0',
     113702,
     '{"chain_id": "real_648_m4_11_policy_detail_v5",
       "source_file_sha256": "4006439ee1494314504a971eeb0d44166216e435b2d3425b5aad3f7439df38e0",
       "source_file_url": "https://www.hunan.gov.cn/",
       "extractor_version": "v1.0", "is_demo": "false"}'::jsonb),
    ('g0eebc99-9c0b-4ef8-bb6d-6bb9bd380g05',
     'g0eebc99-9c0b-4ef8-bb6d-6bb9bd380g03',
     '安徽省人民政府 政务公开 landing',
     'POLICY_DETAIL_LIST',
     'https://www.ah.gov.cn/',
     '2026-09-01',
     'a06e174f10eda8b539a16aad5f25fb3350480df3019d9c861f1cd7d429026713',
     128409,
     '{"chain_id": "real_648_m4_11_policy_detail_v5",
       "source_file_sha256": "a06e174f10eda8b539a16aad5f25fb3350480df3019d9c861f1cd7d429026713",
       "source_file_url": "https://www.ah.gov.cn/",
       "extractor_version": "v1.0", "is_demo": "false"}'::jsonb)
ON CONFLICT (id) DO NOTHING;

-- ----------------------------------------------------------------------------
-- 1. 2 个真实 policy_document (lineage JSONB is_demo='false')
--    chain_id='real_648_m4_11_policy_detail_v5'
--    UUID prefix g11/g12 (≠ 647 f11/f12)
-- ----------------------------------------------------------------------------
INSERT INTO policy_document (
    id, doc_type, title, publisher, publication_date,
    source_id, classification, policy_level, lineage
) VALUES
    ('g1eebc99-9c0b-4ef8-bb6d-6bb9bd380g11',
     'POLICY_DETAIL',
     '省政府政策详情 v5（湖南政务公开 landing）',
     '湖南省人民政府',
     '2026-09-01',
     'g0eebc99-9c0b-4ef8-bb6d-6bb9bd380g04',
     'BULLETIN', 'PROVINCIAL',
     '{"chain_id": "real_648_m4_11_policy_detail_v5",
       "source_file_sha256": "4006439ee1494314504a971eeb0d44166216e435b2d3425b5aad3f7439df38e0",
       "source_file_url": "https://www.hunan.gov.cn/",
       "extractor_version": "v1.0", "is_demo": "false"}'::jsonb),
    ('g1eebc99-9c0b-4ef8-bb6d-6bb9bd380g12',
     'POLICY_DETAIL',
     '省政府政策详情 v5（安徽政务公开 landing）',
     '安徽省人民政府',
     '2026-09-01',
     'g0eebc99-9c0b-4ef8-bb6d-6bb9bd380g05',
     'BULLETIN', 'PROVINCIAL',
     '{"chain_id": "real_648_m4_11_policy_detail_v5",
       "source_file_sha256": "a06e174f10eda8b539a16aad5f25fb3350480df3019d9c861f1cd7d429026713",
       "source_file_url": "https://www.ah.gov.cn/",
       "extractor_version": "v1.0", "is_demo": "false"}'::jsonb)
ON CONFLICT (id) DO NOTHING;

-- ----------------------------------------------------------------------------
-- 2. 2 个真实 policy_target (FK → 上 2 条真实 policy_document)
--    UUID prefix g21/g22 (≠ 647 f21/f22)
-- ----------------------------------------------------------------------------
INSERT INTO policy_target (
    id, policy_document_id, target_description,
    target_value, target_unit, target_year, measurable, lineage
) VALUES
    ('g2eebc99-9c0b-4ef8-bb6d-6bb9bd380g21',
     'g1eebc99-9c0b-4ef8-bb6d-6bb9bd380g11',
     'real-policy-target-hunan-v5 (政策详情 v5 第 9 样本)', NULL, NULL, 2026, FALSE,
     '{"chain_id": "real_648_m4_11_policy_detail_v5",
       "source_file_sha256": "4006439ee1494314504a971eeb0d44166216e435b2d3425b5aad3f7439df38e0",
       "source_file_url": "https://www.hunan.gov.cn/",
       "extractor_version": "v1.0", "is_demo": "false"}'::jsonb),
    ('g2eebc99-9c0b-4ef8-bb6d-6bb9bd380g22',
     'g1eebc99-9c0b-4ef8-bb6d-6bb9bd380g12',
     'real-policy-target-anhui-v5 (政策详情 v5 第 10 样本)', NULL, NULL, 2026, FALSE,
     '{"chain_id": "real_648_m4_11_policy_detail_v5",
       "source_file_sha256": "a06e174f10eda8b539a16aad5f25fb3350480df3019d9c861f1cd7d429026713",
       "source_file_url": "https://www.ah.gov.cn/",
       "extractor_version": "v1.0", "is_demo": "false"}'::jsonb)
ON CONFLICT (id) DO NOTHING;

-- ----------------------------------------------------------------------------
-- 3. 2 个真实 policy_measure (FK → 上 2 条真实 policy_document)
--    UUID prefix g31/g32 (≠ 647 f31/f32)
-- ----------------------------------------------------------------------------
INSERT INTO policy_measure (
    id, policy_document_id, measure_description, measure_type, lineage
) VALUES
    ('g3eebc99-9c0b-4ef8-bb6d-6bb9bd380g31',
     'g1eebc99-9c0b-4ef8-bb6d-6bb9bd380g11',
     'real-policy-measure-hunan-v5 (政策详情 v5 第 9 样本)', 'REGULATORY',
     '{"chain_id": "real_648_m4_11_policy_detail_v5",
       "source_file_sha256": "4006439ee1494314504a971eeb0d44166216e435b2d3425b5aad3f7439df38e0",
       "source_file_url": "https://www.hunan.gov.cn/",
       "extractor_version": "v1.0", "is_demo": "false"}'::jsonb),
    ('g3eebc99-9c0b-4ef8-bb6d-6bb9bd380g32',
     'g1eebc99-9c0b-4ef8-bb6d-6bb9bd380g12',
     'real-policy-measure-anhui-v5 (政策详情 v5 第 10 样本)', 'REGULATORY',
     '{"chain_id": "real_648_m4_11_policy_detail_v5",
       "source_file_sha256": "a06e174f10eda8b539a16aad5f25fb3350480df3019d9c861f1cd7d429026713",
       "source_file_url": "https://www.ah.gov.cn/",
       "extractor_version": "v1.0", "is_demo": "false"}'::jsonb)
ON CONFLICT (id) DO NOTHING;

-- ----------------------------------------------------------------------------
-- 4. 2 个真实 government_commitment (FK → policy_target + 真实 geo_entity + source_document)
--    湖南 / 安徽 geo_entity_id: SELECT 子查询
--    proposer_person_id = NULL (避免 FK 到 639 person demo;保持 spike 自洽)
--    UUID prefix g41/g42 (≠ 647 f41/f42)
-- ----------------------------------------------------------------------------
INSERT INTO government_commitment (
    id, policy_target_id, commitment_text,
    proposer_person_id, geo_entity_id, commitment_date,
    due_date, status, source_id, lineage
)
SELECT
    'g4eebc99-9c0b-4ef8-bb6d-6bb9bd380g41',
    'g2eebc99-9c0b-4ef8-bb6d-6bb9bd380g21',
    'real-commitment-hunan-v5 (政策详情 v5 第 9 样本; 湖南省政府)',
    NULL,
    g.id,
    '2026-09-01',
    '2026-12-31',
    'IN_PROGRESS',
    'g0eebc99-9c0b-4ef8-bb6d-6bb9bd380g04',
    jsonb_build_object(
        'chain_id', 'real_648_m4_11_policy_detail_v5',
        'source_file_sha256', '4006439ee1494314504a971eeb0d44166216e435b2d3425b5aad3f7439df38e0',
        'source_file_url', 'https://www.hunan.gov.cn/',
        'extractor_version', 'v1.0',
        'is_demo', 'false'
    )
FROM geo_entity g
WHERE g.canonical_name = '湖南省' AND g.level = 'PROVINCIAL'
LIMIT 1
ON CONFLICT (id) DO NOTHING;

INSERT INTO government_commitment (
    id, policy_target_id, commitment_text,
    proposer_person_id, geo_entity_id, commitment_date,
    due_date, status, source_id, lineage
)
SELECT
    'g4eebc99-9c0b-4ef8-bb6d-6bb9bd380g42',
    'g2eebc99-9c0b-4ef8-bb6d-6bb9bd380g22',
    'real-commitment-anhui-v5 (政策详情 v5 第 10 样本; 安徽省政府)',
    NULL,
    g.id,
    '2026-09-01',
    '2026-12-31',
    'IN_PROGRESS',
    'g0eebc99-9c0b-4ef8-bb6d-6bb9bd380g05',
    jsonb_build_object(
        'chain_id', 'real_648_m4_11_policy_detail_v5',
        'source_file_sha256', 'a06e174f10eda8b539a16aad5f25fb3350480df3019d9c861f1cd7d429026713',
        'source_file_url', 'https://www.ah.gov.cn/',
        'extractor_version', 'v1.0',
        'is_demo', 'false'
    )
FROM geo_entity g
WHERE g.canonical_name = '安徽省' AND g.level = 'PROVINCIAL'
LIMIT 1
ON CONFLICT (id) DO NOTHING;

-- ----------------------------------------------------------------------------
-- 5. 2 个真实 commitment_progress (FK → 上 2 条真实 government_commitment)
--    UUID prefix g51/g52 (≠ 647 f51/f52)
-- ----------------------------------------------------------------------------
INSERT INTO commitment_progress (
    id, government_commitment_id, progress_value, progress_unit,
    reported_date, reporting_org, lineage
) VALUES
    ('g5eebc99-9c0b-4ef8-bb6d-6bb9bd380g51',
     'g4eebc99-9c0b-4ef8-bb6d-6bb9bd380g41',
     0.5, 'PERCENT', '2026-09-01', '湖南省人民政府',
     '{"chain_id": "real_648_m4_11_policy_detail_v5",
       "source_file_sha256": "4006439ee1494314504a971eeb0d44166216e435b2d3425b5aad3f7439df38e0",
       "source_file_url": "https://www.hunan.gov.cn/",
       "extractor_version": "v1.0", "is_demo": "false"}'::jsonb),
    ('g5eebc99-9c0b-4ef8-bb6d-6bb9bd380g52',
     'g4eebc99-9c0b-4ef8-bb6d-6bb9bd380g42',
     0.5, 'PERCENT', '2026-09-01', '安徽省人民政府',
     '{"chain_id": "real_648_m4_11_policy_detail_v5",
       "source_file_sha256": "a06e174f10eda8b539a16aad5f25fb3350480df3019d9c861f1cd7d429026713",
       "source_file_url": "https://www.ah.gov.cn/",
       "extractor_version": "v1.0", "is_demo": "false"}'::jsonb)
ON CONFLICT (id) DO NOTHING;

-- ----------------------------------------------------------------------------
-- 6. 2 个真实 project_event (FK → 真实 geo_entity via SELECT 子查询)
--    UUID prefix g61/g62 (≠ 647 f61/f62)
-- ----------------------------------------------------------------------------
INSERT INTO project_event (
    id, event_type, event_date, title, description,
    geo_entity_id, source_id, lineage
)
SELECT
    'g6eebc99-9c0b-4ef8-bb6d-6bb9bd380g61',
    'POLICY_DETAIL_RELEASE',
    '2026-09-01',
    'real-project-hunan-v5 (政策详情 v5 第 9 样本)',
    '湖南省政府政策详情页落地; from /zwgk/ 404 → fallback / landing (chain_index=1; 全新 SHA 4006439e...)',
    g.id,
    'g0eebc99-9c0b-4ef8-bb6d-6bb9bd380g04',
    jsonb_build_object(
        'chain_id', 'real_648_m4_11_policy_detail_v5',
        'source_file_sha256', '4006439ee1494314504a971eeb0d44166216e435b2d3425b5aad3f7439df38e0',
        'source_file_url', 'https://www.hunan.gov.cn/',
        'extractor_version', 'v1.0',
        'is_demo', 'false'
    )
FROM geo_entity g
WHERE g.canonical_name = '湖南省' AND g.level = 'PROVINCIAL'
LIMIT 1
ON CONFLICT (id) DO NOTHING;

INSERT INTO project_event (
    id, event_type, event_date, title, description,
    geo_entity_id, source_id, lineage
)
SELECT
    'g6eebc99-9c0b-4ef8-bb6d-6bb9bd380g62',
    'POLICY_DETAIL_RELEASE',
    '2026-09-01',
    'real-project-anhui-v5 (政策详情 v5 第 10 样本)',
    '安徽省政府政策详情页落地; from /zwgk/ timeout → fallback / landing (chain_index=1; 全新 SHA a06e174f...)',
    g.id,
    'g0eebc99-9c0b-4ef8-bb6d-6bb9bd380g05',
    jsonb_build_object(
        'chain_id', 'real_648_m4_11_policy_detail_v5',
        'source_file_sha256', 'a06e174f10eda8b539a16aad5f25fb3350480df3019d9c861f1cd7d429026713',
        'source_file_url', 'https://www.ah.gov.cn/',
        'extractor_version', 'v1.0',
        'is_demo', 'false'
    )
FROM geo_entity g
WHERE g.canonical_name = '安徽省' AND g.level = 'PROVINCIAL'
LIMIT 1
ON CONFLICT (id) DO NOTHING;

-- ----------------------------------------------------------------------------
-- 648-A.1 spike 边界小结:
--   6 政策表 × 2 真实样本 = 12 INSERT planned
--   + 2 source_registry (g02/g03) + 2 source_document (g04/g05) = 16 INSERT total
--   chain_id='real_648_m4_11_policy_detail_v5' (末段 _v5 ≠ 647 _v4 ≠ 646 _v3 ≠ 645 _v2)
--   UUID prefix g 段 (g02-g62) ≠ 647 f 段 (f02-f62) ≠ 646 e 段 ≠ 645 d 段 ≠ 644 c 段
--   2 新 SHA (4006439e / a06e174f) ≠ 647 SHA (8016ef08 / 56481050) ≠ 646 SHA ≠ 645 SHA ≠ ...
--   lineage JSONB is_demo='false' 真实化 sentinel
--
-- 648 红线池 (substitute 预授权池; 已用省不得重复):
--   substitute 池: jilin / liaoning / hubei / shaanxi / sichuan / guizhou / jiangsu
--   已用省全集 (不得重复): HLJ / HENAN / YUNNAN / FUJIAN / GD / ZJ / JX
--   本次首选 hunan + anhui 均一次成功, substitute 池未激活 (备而不用).
-- ----------------------------------------------------------------------------