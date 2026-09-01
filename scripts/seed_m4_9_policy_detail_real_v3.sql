-- ----------------------------------------------------------------------------
-- 646-A.1 — M4.9 政策详情 v3 真实化 seed SQL (knife 646 M4.9 side)
--   12 INSERT (政策表) = 2 样本 (fujian + guangdong) × 6 政策表
--     + 2 source_registry + 2 source_document = 16 INSERT total
--   lineage JSONB `is demo='false'` 真实化 sentinel
--   chain_id='real_646_m4_9_policy_detail_v3' (v3 标记 = fujian + gd 第 5/6 样本; ≠ 645 chain_id)
--   2 新 SHA 全 distinct ≠ 645/644/643/642/641/640/639 demo/real SHA
--     - fujian     `fceb8c0ac80c5d3c...` (/zwgk/ — 全新)
--     - guangdong  `49eed23efcb2954e...` (/zwgk/ — 全新; preferred cell 0, no fallback)
--   UUID prefix e 段 (e02-e62) ≠ 645 d 段 (d21-d94) ≠ 644 c 段 (c41-c93)
--   不新写 016 migration (沿用 009+010+014+015 lineage JSONB)
--   不修改 source_registry 既有 638/640/641/642/643/644/645 行 / mart / 4 fixture
-- ----------------------------------------------------------------------------

-- ----------------------------------------------------------------------------
-- 0. 2 个真实 source_registry (lineage JSONB is_demo='false')
--    chain_id='real_646_m4_9_policy_detail_v3'
--    UUID prefix e02/e03 (≠ 645 d21/d22/d23/d24)
-- ----------------------------------------------------------------------------
INSERT INTO source_registry (
    id, source_url, source_name, source_type,
    country, province, enabled, lineage
) VALUES
    ('e0eebc99-9c0b-4ef8-bb6d-6bb9bd380e02',
     'https://www.fujian.gov.cn/zwgk/',
     '福建省人民政府 政务公开 landing',
     'PROVINCIAL_BULLETIN',
     'CN', 'FUJIAN', TRUE,
     '{"chain_id": "real_646_m4_9_policy_detail_v3",
       "source_file_sha256": "fceb8c0ac80c5d3c55115a5716414fbc6ee000d7dbb325bf38585c8b88e01709",
       "source_file_url": "https://www.fujian.gov.cn/zwgk/",
       "extractor_version": "v1.0", "is_demo": "false"}'::jsonb),
    ('e0eebc99-9c0b-4ef8-bb6d-6bb9bd380e03',
     'https://www.gd.gov.cn/zwgk/',
     '广东省人民政府 政务公开 landing',
     'PROVINCIAL_BULLETIN',
     'CN', 'GUANGDONG', TRUE,
     '{"chain_id": "real_646_m4_9_policy_detail_v3",
       "source_file_sha256": "49eed23efcb2954e54dbaf8bbf8f664b38dc187b604bf0f6f5a9a502a3f7d5db",
       "source_file_url": "https://www.gd.gov.cn/zwgk/",
       "extractor_version": "v1.0", "is_demo": "false"}'::jsonb)
ON CONFLICT (id) DO NOTHING;

-- ----------------------------------------------------------------------------
-- 0b. 2 个真实 source_document (lineage JSONB is_demo='false')
--     UUID prefix e04/e05
-- ----------------------------------------------------------------------------
INSERT INTO source_document (
    id, source_id, title, doc_kind, content_url,
    captured_at, file_hash_sha256, file_size_bytes, lineage
) VALUES
    ('e0eebc99-9c0b-4ef8-bb6d-6bb9bd380e04',
     'e0eebc99-9c0b-4ef8-bb6d-6bb9bd380e02',
     '福建省人民政府 政务公开 landing',
     'POLICY_DETAIL_LIST',
     'https://www.fujian.gov.cn/zwgk/',
     '2026-09-01',
     'fceb8c0ac80c5d3c55115a5716414fbc6ee000d7dbb325bf38585c8b88e01709',
     682079,
     '{"chain_id": "real_646_m4_9_policy_detail_v3",
       "source_file_sha256": "fceb8c0ac80c5d3c55115a5716414fbc6ee000d7dbb325bf38585c8b88e01709",
       "source_file_url": "https://www.fujian.gov.cn/zwgk/",
       "extractor_version": "v1.0", "is_demo": "false"}'::jsonb),
    ('e0eebc99-9c0b-4ef8-bb6d-6bb9bd380e05',
     'e0eebc99-9c0b-4ef8-bb6d-6bb9bd380e03',
     '广东省人民政府 政务公开 landing',
     'PROVINCIAL_BULLETIN',
     'https://www.gd.gov.cn/zwgk/',
     '2026-09-01',
     '49eed23efcb2954e54dbaf8bbf8f664b38dc187b604bf0f6f5a9a502a3f7d5db',
     73836,
     '{"chain_id": "real_646_m4_9_policy_detail_v3",
       "source_file_sha256": "49eed23efcb2954e54dbaf8bbf8f664b38dc187b604bf0f6f5a9a502a3f7d5db",
       "source_file_url": "https://www.gd.gov.cn/zwgk/",
       "extractor_version": "v1.0", "is_demo": "false"}'::jsonb)
ON CONFLICT (id) DO NOTHING;

-- ----------------------------------------------------------------------------
-- 1. 2 个真实 policy_document (lineage JSONB is_demo='false')
--    chain_id='real_646_m4_9_policy_detail_v3'
--    UUID prefix e11/e12 (≠ 645 d41/d42/d43/d44 ≠ 644 c41/c42/c43)
-- ----------------------------------------------------------------------------
INSERT INTO policy_document (
    id, doc_type, title, publisher, publication_date,
    source_id, classification, policy_level, lineage
) VALUES
    ('e1eebc99-9c0b-4ef8-bb6d-6bb9bd380e11',
     'POLICY_DETAIL',
     '省政府政策详情 v3（福建政务公开 landing）',
     '福建省人民政府',
     '2026-09-01',
     'e0eebc99-9c0b-4ef8-bb6d-6bb9bd380e04',
     'BULLETIN', 'PROVINCIAL',
     '{"chain_id": "real_646_m4_9_policy_detail_v3",
       "source_file_sha256": "fceb8c0ac80c5d3c55115a5716414fbc6ee000d7dbb325bf38585c8b88e01709",
       "source_file_url": "https://www.fujian.gov.cn/zwgk/",
       "extractor_version": "v1.0", "is_demo": "false"}'::jsonb),
    ('e1eebc99-9c0b-4ef8-bb6d-6bb9bd380e12',
     'POLICY_DETAIL',
     '省政府政策详情 v3（广东政务公开 landing）',
     '广东省人民政府',
     '2026-09-01',
     'e0eebc99-9c0b-4ef8-bb6d-6bb9bd380e05',
     'BULLETIN', 'PROVINCIAL',
     '{"chain_id": "real_646_m4_9_policy_detail_v3",
       "source_file_sha256": "49eed23efcb2954e54dbaf8bbf8f664b38dc187b604bf0f6f5a9a502a3f7d5db",
       "source_file_url": "https://www.gd.gov.cn/zwgk/",
       "extractor_version": "v1.0", "is_demo": "false"}'::jsonb)
ON CONFLICT (id) DO NOTHING;

-- ----------------------------------------------------------------------------
-- 2. 2 个真实 policy_target (FK → 上 2 条真实 policy_document)
--    UUID prefix e21/e22 (≠ 645 d51/d52/d53/d54 ≠ 644 c51/c52/c53)
-- ----------------------------------------------------------------------------
INSERT INTO policy_target (
    id, policy_document_id, target_description,
    target_value, target_unit, target_year, measurable, lineage
) VALUES
    ('e2eebc99-9c0b-4ef8-bb6d-6bb9bd380e21',
     'e1eebc99-9c0b-4ef8-bb6d-6bb9bd380e11',
     'real-policy-target-fujian-v3 (政策详情 v3 第 5 样本)', NULL, NULL, 2026, FALSE,
     '{"chain_id": "real_646_m4_9_policy_detail_v3",
       "source_file_sha256": "fceb8c0ac80c5d3c55115a5716414fbc6ee000d7dbb325bf38585c8b88e01709",
       "source_file_url": "https://www.fujian.gov.cn/zwgk/",
       "extractor_version": "v1.0", "is_demo": "false"}'::jsonb),
    ('e2eebc99-9c0b-4ef8-bb6d-6bb9bd380e22',
     'e1eebc99-9c0b-4ef8-bb6d-6bb9bd380e12',
     'real-policy-target-guangdong-v3 (政策详情 v3 第 6 样本)', NULL, NULL, 2026, FALSE,
     '{"chain_id": "real_646_m4_9_policy_detail_v3",
       "source_file_sha256": "49eed23efcb2954e54dbaf8bbf8f664b38dc187b604bf0f6f5a9a502a3f7d5db",
       "source_file_url": "https://www.gd.gov.cn/zwgk/",
       "extractor_version": "v1.0", "is_demo": "false"}'::jsonb)
ON CONFLICT (id) DO NOTHING;

-- ----------------------------------------------------------------------------
-- 3. 2 个真实 policy_measure (FK → 上 2 条真实 policy_document)
--    UUID prefix e31/e32 (≠ 645 d61/d62/d63/d64 ≠ 644 c61/c62/c63)
-- ----------------------------------------------------------------------------
INSERT INTO policy_measure (
    id, policy_document_id, measure_description, measure_type, lineage
) VALUES
    ('e3eebc99-9c0b-4ef8-bb6d-6bb9bd380e31',
     'e1eebc99-9c0b-4ef8-bb6d-6bb9bd380e11',
     'real-policy-measure-fujian-v3 (政策详情 v3 第 5 样本)', 'REGULATORY',
     '{"chain_id": "real_646_m4_9_policy_detail_v3",
       "source_file_sha256": "fceb8c0ac80c5d3c55115a5716414fbc6ee000d7dbb325bf38585c8b88e01709",
       "source_file_url": "https://www.fujian.gov.cn/zwgk/",
       "extractor_version": "v1.0", "is_demo": "false"}'::jsonb),
    ('e3eebc99-9c0b-4ef8-bb6d-6bb9bd380e32',
     'e1eebc99-9c0b-4ef8-bb6d-6bb9bd380e12',
     'real-policy-measure-guangdong-v3 (政策详情 v3 第 6 样本)', 'REGULATORY',
     '{"chain_id": "real_646_m4_9_policy_detail_v3",
       "source_file_sha256": "49eed23efcb2954e54dbaf8bbf8f664b38dc187b604bf0f6f5a9a502a3f7d5db",
       "source_file_url": "https://www.gd.gov.cn/zwgk/",
       "extractor_version": "v1.0", "is_demo": "false"}'::jsonb)
ON CONFLICT (id) DO NOTHING;

-- ----------------------------------------------------------------------------
-- 4. 2 个真实 government_commitment (FK → policy_target + 真实 geo_entity + source_document)
--    福建 / 广东 geo_entity_id: SELECT 子查询
--    proposer_person_id = NULL (避免 FK 到 639 person demo;保持 spike 自洽)
--    UUID prefix e41/e42 (≠ 645 d71/d72/d73/d74 ≠ 644 c71/c72/c73)
-- ----------------------------------------------------------------------------
INSERT INTO government_commitment (
    id, policy_target_id, commitment_text,
    proposer_person_id, geo_entity_id, commitment_date,
    due_date, status, source_id, lineage
)
SELECT
    'e4eebc99-9c0b-4ef8-bb6d-6bb9bd380e41',
    'e2eebc99-9c0b-4ef8-bb6d-6bb9bd380e21',
    'real-commitment-fujian-v3 (政策详情 v3 第 5 样本; 福建省政府)',
    NULL,
    g.id,
    '2026-09-01',
    '2026-12-31',
    'IN_PROGRESS',
    'e0eebc99-9c0b-4ef8-bb6d-6bb9bd380e04',
    jsonb_build_object(
        'chain_id', 'real_646_m4_9_policy_detail_v3',
        'source_file_sha256', 'fceb8c0ac80c5d3c55115a5716414fbc6ee000d7dbb325bf38585c8b88e01709',
        'source_file_url', 'https://www.fujian.gov.cn/zwgk/',
        'extractor_version', 'v1.0',
        'is_demo', 'false'
    )
FROM geo_entity g
WHERE g.canonical_name = '福建省' AND g.level = 'PROVINCIAL'
LIMIT 1
ON CONFLICT (id) DO NOTHING;

INSERT INTO government_commitment (
    id, policy_target_id, commitment_text,
    proposer_person_id, geo_entity_id, commitment_date,
    due_date, status, source_id, lineage
)
SELECT
    'e4eebc99-9c0b-4ef8-bb6d-6bb9bd380e42',
    'e2eebc99-9c0b-4ef8-bb6d-6bb9bd380e22',
    'real-commitment-guangdong-v3 (政策详情 v3 第 6 样本; 广东省政府)',
    NULL,
    g.id,
    '2026-09-01',
    '2026-12-31',
    'IN_PROGRESS',
    'e0eebc99-9c0b-4ef8-bb6d-6bb9bd380e05',
    jsonb_build_object(
        'chain_id', 'real_646_m4_9_policy_detail_v3',
        'source_file_sha256', '49eed23efcb2954e54dbaf8bbf8f664b38dc187b604bf0f6f5a9a502a3f7d5db',
        'source_file_url', 'https://www.gd.gov.cn/zwgk/',
        'extractor_version', 'v1.0',
        'is_demo', 'false'
    )
FROM geo_entity g
WHERE g.canonical_name = '广东省' AND g.level = 'PROVINCIAL'
LIMIT 1
ON CONFLICT (id) DO NOTHING;

-- ----------------------------------------------------------------------------
-- 5. 2 个真实 commitment_progress (FK → 上 2 条真实 government_commitment)
--    UUID prefix e51/e52 (≠ 645 d81/d82/d83/d84 ≠ 644 c81/c82/c83)
-- ----------------------------------------------------------------------------
INSERT INTO commitment_progress (
    id, government_commitment_id, progress_value, progress_unit,
    reported_date, reporting_org, lineage
) VALUES
    ('e5eebc99-9c0b-4ef8-bb6d-6bb9bd380e51',
     'e4eebc99-9c0b-4ef8-bb6d-6bb9bd380e41',
     0.5, 'PERCENT', '2026-09-01', '福建省人民政府',
     '{"chain_id": "real_646_m4_9_policy_detail_v3",
       "source_file_sha256": "fceb8c0ac80c5d3c55115a5716414fbc6ee000d7dbb325bf38585c8b88e01709",
       "source_file_url": "https://www.fujian.gov.cn/zwgk/",
       "extractor_version": "v1.0", "is_demo": "false"}'::jsonb),
    ('e5eebc99-9c0b-4ef8-bb6d-6bb9bd380e52',
     'e4eebc99-9c0b-4ef8-bb6d-6bb9bd380e42',
     0.5, 'PERCENT', '2026-09-01', '广东省人民政府',
     '{"chain_id": "real_646_m4_9_policy_detail_v3",
       "source_file_sha256": "49eed23efcb2954e54dbaf8bbf8f664b38dc187b604bf0f6f5a9a502a3f7d5db",
       "source_file_url": "https://www.gd.gov.cn/zwgk/",
       "extractor_version": "v1.0", "is_demo": "false"}'::jsonb)
ON CONFLICT (id) DO NOTHING;

-- ----------------------------------------------------------------------------
-- 6. 2 个真实 project_event (FK → 真实 geo_entity via SELECT 子查询)
--    UUID prefix e61/e62 (≠ 645 d91/d92/d93/d94 ≠ 644 c91/c92/c93)
-- ----------------------------------------------------------------------------
INSERT INTO project_event (
    id, event_type, event_date, title, description,
    geo_entity_id, source_id, lineage
)
SELECT
    'e6eebc99-9c0b-4ef8-bb6d-6bb9bd380e61',
    'POLICY_DETAIL_RELEASE',
    '2026-09-01',
    'real-project-fujian-v3 (政策详情 v3 第 5 样本)',
    '福建省政府政策详情页落地; from /zwgk/ landing (全新 SHA fceb8c0a...)',
    g.id,
    'e0eebc99-9c0b-4ef8-bb6d-6bb9bd380e04',
    jsonb_build_object(
        'chain_id', 'real_646_m4_9_policy_detail_v3',
        'source_file_sha256', 'fceb8c0ac80c5d3c55115a5716414fbc6ee000d7dbb325bf38585c8b88e01709',
        'source_file_url', 'https://www.fujian.gov.cn/zwgk/',
        'extractor_version', 'v1.0',
        'is_demo', 'false'
    )
FROM geo_entity g
WHERE g.canonical_name = '福建省' AND g.level = 'PROVINCIAL'
LIMIT 1
ON CONFLICT (id) DO NOTHING;

INSERT INTO project_event (
    id, event_type, event_date, title, description,
    geo_entity_id, source_id, lineage
)
SELECT
    'e6eebc99-9c0b-4ef8-bb6d-6bb9bd380e62',
    'POLICY_DETAIL_RELEASE',
    '2026-09-01',
    'real-project-guangdong-v3 (政策详情 v3 第 6 样本)',
    '广东省政府政策详情页落地; from /zwgk/ landing (preferred cell 0, no fallback; 全新 SHA 49eed23e...)',
    g.id,
    'e0eebc99-9c0b-4ef8-bb6d-6bb9bd380e05',
    jsonb_build_object(
        'chain_id', 'real_646_m4_9_policy_detail_v3',
        'source_file_sha256', '49eed23efcb2954e54dbaf8bbf8f664b38dc187b604bf0f6f5a9a502a3f7d5db',
        'source_file_url', 'https://www.gd.gov.cn/zwgk/',
        'extractor_version', 'v1.0',
        'is_demo', 'false'
    )
FROM geo_entity g
WHERE g.canonical_name = '广东省' AND g.level = 'PROVINCIAL'
LIMIT 1
ON CONFLICT (id) DO NOTHING;

-- ----------------------------------------------------------------------------
-- 646-A.1 spike 边界小结:
--   6 政策表 × 2 真实样本 = 12 INSERT planned
--   + 2 source_registry (e02/e03) + 2 source_document (e04/e05) = 16 INSERT total
--   chain_id='real_646_m4_9_policy_detail_v3' (≠ 645 chain_id '_v2' ≠ 644 '_policy_detail')
--   UUID prefix e 段 (e02-e62) ≠ 645 d 段 (d21-d94) ≠ 644 c 段 (c41-c93)
--   2 新 SHA (fceb8c0a / 49eed23e) ≠ 645 SHA (6237cd48 / dfa38998 / bd4c4c51 / f33eba53)
--   lineage JSONB is_demo='false' 真实化 sentinel
-- ----------------------------------------------------------------------------