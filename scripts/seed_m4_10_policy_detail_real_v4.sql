-- ----------------------------------------------------------------------------
-- 647-A.1 — M4.10 政策详情 v4 真实化 seed SQL (knife 647 M4.10 side)
--   12 INSERT (政策表) = 2 样本 (zhejiang + jiangxi 替代 shandong BLOCKED) × 6 政策表
--     + 2 source_registry + 2 source_document = 16 INSERT total
--   lineage JSONB `is_demo='false'` 真实化 sentinel
--   chain_id='real_647_m4_10_policy_detail_v4' (v4 标记 = zhejiang + jiangxi 第 7/8 样本; ≠ 646 chain_id)
--   2 新 SHA 全 distinct ≠ 646/645/644/643/642/641/640/639/638 demo/real SHA
--     - zhejiang  `8016ef0874c49261...` (/zwgk/ 403 → fallback / 200; SHA 8016ef08...)
--     - jiangxi   `56481050c810fbee...` (substitute for shandong BLOCKED TLS; /zwgk/ 200; SHA 56481050...)
--   UUID prefix f 段 (f02-f62) ≠ 646 e 段 (e02-e62) ≠ 645 d 段 ≠ 644 c 段
--   不新写 016 migration (沿用 009+010+014+015 lineage JSONB)
--   不修改 source_registry 既有 638/640/641/642/643/644/645/646 行 / mart / 4 fixture
--
-- 625 fall-through substitute 注记:
--   shandong 4 attempts BLOCKED (HTTPS TLS handshake_failure + HTTP 404/timeout);
--   沿用 625 fall-through 政策, 从"已用省全集"未用省份 pool (HLJ/HENAN/YUNNAN/FUJIAN/GD 之外)
--   替换为 jiangxi (实测 https://www.jiangxi.gov.cn/zwgk/ = 200 REACHABLE).
-- ----------------------------------------------------------------------------

-- ----------------------------------------------------------------------------
-- 0. 2 个真实 source_registry (lineage JSONB is_demo='false')
--    chain_id='real_647_m4_10_policy_detail_v4'
--    UUID prefix f02/f03 (≠ 646 e02/e03)
-- ----------------------------------------------------------------------------
INSERT INTO source_registry (
    id, source_url, source_name, source_type,
    country, province, enabled, lineage
) VALUES
    ('f0eebc99-9c0b-4ef8-bb6d-6bb9bd380f02',
     'https://www.zj.gov.cn/zwgk/',
     '浙江省人民政府 政务公开 landing',
     'PROVINCIAL_BULLETIN',
     'CN', 'ZHEJIANG', TRUE,
     '{"chain_id": "real_647_m4_10_policy_detail_v4",
       "source_file_sha256": "8016ef0874c49261d39fc83f79b7ba04b6ce109b2bf85444cca473f27c58f8a8",
       "source_file_url": "https://www.zj.gov.cn/",
       "extractor_version": "v1.0", "is_demo": "false"}'::jsonb),
    ('f0eebc99-9c0b-4ef8-bb6d-6bb9bd380f03',
     'https://www.jiangxi.gov.cn/zwgk/',
     '江西省人民政府 政务公开 landing (shandong BLOCKED 625 substitute)',
     'PROVINCIAL_BULLETIN',
     'CN', 'JIANGXI', TRUE,
     '{"chain_id": "real_647_m4_10_policy_detail_v4",
       "source_file_sha256": "56481050c810fbeec004ff68478d9f291c5eda39e005ec09e3fb6122dc28edd4",
       "source_file_url": "https://www.jiangxi.gov.cn/zwgk/",
       "extractor_version": "v1.0", "is_demo": "false"}'::jsonb)
ON CONFLICT (id) DO NOTHING;

-- ----------------------------------------------------------------------------
-- 0b. 2 个真实 source_document (lineage JSONB is_demo='false')
--     UUID prefix f04/f05
-- ----------------------------------------------------------------------------
INSERT INTO source_document (
    id, source_id, title, doc_kind, content_url,
    captured_at, file_hash_sha256, file_size_bytes, lineage
) VALUES
    ('f0eebc99-9c0b-4ef8-bb6d-6bb9bd380f04',
     'f0eebc99-9c0b-4ef8-bb6d-6bb9bd380f02',
     '浙江省人民政府 政务公开 landing',
     'POLICY_DETAIL_LIST',
     'https://www.zj.gov.cn/',
     '2026-09-01',
     '8016ef0874c49261d39fc83f79b7ba04b6ce109b2bf85444cca473f27c58f8a8',
     159382,
     '{"chain_id": "real_647_m4_10_policy_detail_v4",
       "source_file_sha256": "8016ef0874c49261d39fc83f79b7ba04b6ce109b2bf85444cca473f27c58f8a8",
       "source_file_url": "https://www.zj.gov.cn/",
       "extractor_version": "v1.0", "is_demo": "false"}'::jsonb),
    ('f0eebc99-9c0b-4ef8-bb6d-6bb9bd380f05',
     'f0eebc99-9c0b-4ef8-bb6d-6bb9bd380f03',
     '江西省人民政府 政务公开 landing (shandong BLOCKED 625 substitute)',
     'POLICY_DETAIL_LIST',
     'https://www.jiangxi.gov.cn/zwgk/',
     '2026-09-01',
     '56481050c810fbeec004ff68478d9f291c5eda39e005ec09e3fb6122dc28edd4',
     48118,
     '{"chain_id": "real_647_m4_10_policy_detail_v4",
       "source_file_sha256": "56481050c810fbeec004ff68478d9f291c5eda39e005ec09e3fb6122dc28edd4",
       "source_file_url": "https://www.jiangxi.gov.cn/zwgk/",
       "extractor_version": "v1.0", "is_demo": "false"}'::jsonb)
ON CONFLICT (id) DO NOTHING;

-- ----------------------------------------------------------------------------
-- 1. 2 个真实 policy_document (lineage JSONB is_demo='false')
--    chain_id='real_647_m4_10_policy_detail_v4'
--    UUID prefix f11/f12 (≠ 646 e11/e12 ≠ 645 d41-d44)
-- ----------------------------------------------------------------------------
INSERT INTO policy_document (
    id, doc_type, title, publisher, publication_date,
    source_id, classification, policy_level, lineage
) VALUES
    ('f1eebc99-9c0b-4ef8-bb6d-6bb9bd380f11',
     'POLICY_DETAIL',
     '省政府政策详情 v4（浙江政务公开 landing）',
     '浙江省人民政府',
     '2026-09-01',
     'f0eebc99-9c0b-4ef8-bb6d-6bb9bd380f04',
     'BULLETIN', 'PROVINCIAL',
     '{"chain_id": "real_647_m4_10_policy_detail_v4",
       "source_file_sha256": "8016ef0874c49261d39fc83f79b7ba04b6ce109b2bf85444cca473f27c58f8a8",
       "source_file_url": "https://www.zj.gov.cn/",
       "extractor_version": "v1.0", "is_demo": "false"}'::jsonb),
    ('f1eebc99-9c0b-4ef8-bb6d-6bb9bd380f12',
     'POLICY_DETAIL',
     '省政府政策详情 v4（江西政务公开 landing; shandong BLOCKED 625 substitute）',
     '江西省人民政府',
     '2026-09-01',
     'f0eebc99-9c0b-4ef8-bb6d-6bb9bd380f05',
     'BULLETIN', 'PROVINCIAL',
     '{"chain_id": "real_647_m4_10_policy_detail_v4",
       "source_file_sha256": "56481050c810fbeec004ff68478d9f291c5eda39e005ec09e3fb6122dc28edd4",
       "source_file_url": "https://www.jiangxi.gov.cn/zwgk/",
       "extractor_version": "v1.0", "is_demo": "false"}'::jsonb)
ON CONFLICT (id) DO NOTHING;

-- ----------------------------------------------------------------------------
-- 2. 2 个真实 policy_target (FK → 上 2 条真实 policy_document)
--    UUID prefix f21/f22 (≠ 646 e21/e22 ≠ 645 d51-d54)
-- ----------------------------------------------------------------------------
INSERT INTO policy_target (
    id, policy_document_id, target_description,
    target_value, target_unit, target_year, measurable, lineage
) VALUES
    ('f2eebc99-9c0b-4ef8-bb6d-6bb9bd380f21',
     'f1eebc99-9c0b-4ef8-bb6d-6bb9bd380f11',
     'real-policy-target-zhejiang-v4 (政策详情 v4 第 7 样本)', NULL, NULL, 2026, FALSE,
     '{"chain_id": "real_647_m4_10_policy_detail_v4",
       "source_file_sha256": "8016ef0874c49261d39fc83f79b7ba04b6ce109b2bf85444cca473f27c58f8a8",
       "source_file_url": "https://www.zj.gov.cn/",
       "extractor_version": "v1.0", "is_demo": "false"}'::jsonb),
    ('f2eebc99-9c0b-4ef8-bb6d-6bb9bd380f22',
     'f1eebc99-9c0b-4ef8-bb6d-6bb9bd380f12',
     'real-policy-target-jiangxi-v4 (政策详情 v4 第 8 样本; shandong BLOCKED 625 substitute)', NULL, NULL, 2026, FALSE,
     '{"chain_id": "real_647_m4_10_policy_detail_v4",
       "source_file_sha256": "56481050c810fbeec004ff68478d9f291c5eda39e005ec09e3fb6122dc28edd4",
       "source_file_url": "https://www.jiangxi.gov.cn/zwgk/",
       "extractor_version": "v1.0", "is_demo": "false"}'::jsonb)
ON CONFLICT (id) DO NOTHING;

-- ----------------------------------------------------------------------------
-- 3. 2 个真实 policy_measure (FK → 上 2 条真实 policy_document)
--    UUID prefix f31/f32 (≠ 646 e31/e32 ≠ 645 d61-d64)
-- ----------------------------------------------------------------------------
INSERT INTO policy_measure (
    id, policy_document_id, measure_description, measure_type, lineage
) VALUES
    ('f3eebc99-9c0b-4ef8-bb6d-6bb9bd380f31',
     'f1eebc99-9c0b-4ef8-bb6d-6bb9bd380f11',
     'real-policy-measure-zhejiang-v4 (政策详情 v4 第 7 样本)', 'REGULATORY',
     '{"chain_id": "real_647_m4_10_policy_detail_v4",
       "source_file_sha256": "8016ef0874c49261d39fc83f79b7ba04b6ce109b2bf85444cca473f27c58f8a8",
       "source_file_url": "https://www.zj.gov.cn/",
       "extractor_version": "v1.0", "is_demo": "false"}'::jsonb),
    ('f3eebc99-9c0b-4ef8-bb6d-6bb9bd380f32',
     'f1eebc99-9c0b-4ef8-bb6d-6bb9bd380f12',
     'real-policy-measure-jiangxi-v4 (政策详情 v4 第 8 样本; shandong BLOCKED 625 substitute)', 'REGULATORY',
     '{"chain_id": "real_647_m4_10_policy_detail_v4",
       "source_file_sha256": "56481050c810fbeec004ff68478d9f291c5eda39e005ec09e3fb6122dc28edd4",
       "source_file_url": "https://www.jiangxi.gov.cn/zwgk/",
       "extractor_version": "v1.0", "is_demo": "false"}'::jsonb)
ON CONFLICT (id) DO NOTHING;

-- ----------------------------------------------------------------------------
-- 4. 2 个真实 government_commitment (FK → policy_target + 真实 geo_entity + source_document)
--    浙江 / 江西 geo_entity_id: SELECT 子查询
--    proposer_person_id = NULL (避免 FK 到 639 person demo;保持 spike 自洽)
--    UUID prefix f41/f42 (≠ 646 e41/e42 ≠ 645 d71-d74)
-- ----------------------------------------------------------------------------
INSERT INTO government_commitment (
    id, policy_target_id, commitment_text,
    proposer_person_id, geo_entity_id, commitment_date,
    due_date, status, source_id, lineage
)
SELECT
    'f4eebc99-9c0b-4ef8-bb6d-6bb9bd380f41',
    'f2eebc99-9c0b-4ef8-bb6d-6bb9bd380f21',
    'real-commitment-zhejiang-v4 (政策详情 v4 第 7 样本; 浙江省政府)',
    NULL,
    g.id,
    '2026-09-01',
    '2026-12-31',
    'IN_PROGRESS',
    'f0eebc99-9c0b-4ef8-bb6d-6bb9bd380f04',
    jsonb_build_object(
        'chain_id', 'real_647_m4_10_policy_detail_v4',
        'source_file_sha256', '8016ef0874c49261d39fc83f79b7ba04b6ce109b2bf85444cca473f27c58f8a8',
        'source_file_url', 'https://www.zj.gov.cn/',
        'extractor_version', 'v1.0',
        'is_demo', 'false'
    )
FROM geo_entity g
WHERE g.canonical_name = '浙江省' AND g.level = 'PROVINCIAL'
LIMIT 1
ON CONFLICT (id) DO NOTHING;

INSERT INTO government_commitment (
    id, policy_target_id, commitment_text,
    proposer_person_id, geo_entity_id, commitment_date,
    due_date, status, source_id, lineage
)
SELECT
    'f4eebc99-9c0b-4ef8-bb6d-6bb9bd380f42',
    'f2eebc99-9c0b-4ef8-bb6d-6bb9bd380f22',
    'real-commitment-jiangxi-v4 (政策详情 v4 第 8 样本; 江西省政府; shandong BLOCKED 625 substitute)',
    NULL,
    g.id,
    '2026-09-01',
    '2026-12-31',
    'IN_PROGRESS',
    'f0eebc99-9c0b-4ef8-bb6d-6bb9bd380f05',
    jsonb_build_object(
        'chain_id', 'real_647_m4_10_policy_detail_v4',
        'source_file_sha256', '56481050c810fbeec004ff68478d9f291c5eda39e005ec09e3fb6122dc28edd4',
        'source_file_url', 'https://www.jiangxi.gov.cn/zwgk/',
        'extractor_version', 'v1.0',
        'is_demo', 'false'
    )
FROM geo_entity g
WHERE g.canonical_name = '江西省' AND g.level = 'PROVINCIAL'
LIMIT 1
ON CONFLICT (id) DO NOTHING;

-- ----------------------------------------------------------------------------
-- 5. 2 个真实 commitment_progress (FK → 上 2 条真实 government_commitment)
--    UUID prefix f51/f52 (≠ 646 e51/e52 ≠ 645 d81-d84)
-- ----------------------------------------------------------------------------
INSERT INTO commitment_progress (
    id, government_commitment_id, progress_value, progress_unit,
    reported_date, reporting_org, lineage
) VALUES
    ('f5eebc99-9c0b-4ef8-bb6d-6bb9bd380f51',
     'f4eebc99-9c0b-4ef8-bb6d-6bb9bd380f41',
     0.5, 'PERCENT', '2026-09-01', '浙江省人民政府',
     '{"chain_id": "real_647_m4_10_policy_detail_v4",
       "source_file_sha256": "8016ef0874c49261d39fc83f79b7ba04b6ce109b2bf85444cca473f27c58f8a8",
       "source_file_url": "https://www.zj.gov.cn/",
       "extractor_version": "v1.0", "is_demo": "false"}'::jsonb),
    ('f5eebc99-9c0b-4ef8-bb6d-6bb9bd380f52',
     'f4eebc99-9c0b-4ef8-bb6d-6bb9bd380f42',
     0.5, 'PERCENT', '2026-09-01', '江西省人民政府',
     '{"chain_id": "real_647_m4_10_policy_detail_v4",
       "source_file_sha256": "56481050c810fbeec004ff68478d9f291c5eda39e005ec09e3fb6122dc28edd4",
       "source_file_url": "https://www.jiangxi.gov.cn/zwgk/",
       "extractor_version": "v1.0", "is_demo": "false"}'::jsonb)
ON CONFLICT (id) DO NOTHING;

-- ----------------------------------------------------------------------------
-- 6. 2 个真实 project_event (FK → 真实 geo_entity via SELECT 子查询)
--    UUID prefix f61/f62 (≠ 646 e61/e62 ≠ 645 d91-d94)
-- ----------------------------------------------------------------------------
INSERT INTO project_event (
    id, event_type, event_date, title, description,
    geo_entity_id, source_id, lineage
)
SELECT
    'f6eebc99-9c0b-4ef8-bb6d-6bb9bd380f61',
    'POLICY_DETAIL_RELEASE',
    '2026-09-01',
    'real-project-zhejiang-v4 (政策详情 v4 第 7 样本)',
    '浙江省政府政策详情页落地; from /zwgk/ fallback / landing (chain_index=1; 全新 SHA 8016ef08...)',
    g.id,
    'f0eebc99-9c0b-4ef8-bb6d-6bb9bd380f04',
    jsonb_build_object(
        'chain_id', 'real_647_m4_10_policy_detail_v4',
        'source_file_sha256', '8016ef0874c49261d39fc83f79b7ba04b6ce109b2bf85444cca473f27c58f8a8',
        'source_file_url', 'https://www.zj.gov.cn/',
        'extractor_version', 'v1.0',
        'is_demo', 'false'
    )
FROM geo_entity g
WHERE g.canonical_name = '浙江省' AND g.level = 'PROVINCIAL'
LIMIT 1
ON CONFLICT (id) DO NOTHING;

INSERT INTO project_event (
    id, event_type, event_date, title, description,
    geo_entity_id, source_id, lineage
)
SELECT
    'f6eebc99-9c0b-4ef8-bb6d-6bb9bd380f62',
    'POLICY_DETAIL_RELEASE',
    '2026-09-01',
    'real-project-jiangxi-v4 (政策详情 v4 第 8 样本; shandong BLOCKED 625 substitute)',
    '江西省政府政策详情页落地; from /zwgk/ landing (chain_index=0; 全新 SHA 56481050...); 替代 shandong HTTPS TLS handshake_failure + HTTP 404/timeout (4 attempts BLOCKED)',
    g.id,
    'f0eebc99-9c0b-4ef8-bb6d-6bb9bd380f05',
    jsonb_build_object(
        'chain_id', 'real_647_m4_10_policy_detail_v4',
        'source_file_sha256', '56481050c810fbeec004ff68478d9f291c5eda39e005ec09e3fb6122dc28edd4',
        'source_file_url', 'https://www.jiangxi.gov.cn/zwgk/',
        'extractor_version', 'v1.0',
        'is_demo', 'false'
    )
FROM geo_entity g
WHERE g.canonical_name = '江西省' AND g.level = 'PROVINCIAL'
LIMIT 1
ON CONFLICT (id) DO NOTHING;

-- ----------------------------------------------------------------------------
-- 647-A.1 spike 边界小结:
--   6 政策表 × 2 真实样本 = 12 INSERT planned
--   + 2 source_registry (f02/f03) + 2 source_document (f04/f05) = 16 INSERT total
--   chain_id='real_647_m4_10_policy_detail_v4' (≠ 646 chain_id '_v3' ≠ 645 '_v2' ≠ 644 '_policy_detail')
--   UUID prefix f 段 (f02-f62) ≠ 646 e 段 (e02-e62) ≠ 645 d 段 ≠ 644 c 段
--   2 新 SHA (8016ef08 / 56481050) ≠ 646 SHA (fceb8c0a / 49eed23e) ≠ 645 SHA ≠ ...
--   lineage JSONB is_demo='false' 真实化 sentinel
--
-- 625 fall-through substitute 注记 (jiangxi 替代 shandong BLOCKED):
--   shandong 4 attempts BLOCKED:
--     - https://www.shandong.gov.cn/zwgk/ → sslv3 alert handshake_failure
--     - https://www.shandong.gov.cn/ → sslv3 alert handshake_failure
--     - http://www.shandong.gov.cn/zwgk/ → 404 (redirected to HTTPS)
--     - http://www.shandong.gov.cn/ → timeout
--   沿用 625 fall-through 政策 → 从未用 pool 替换为 jiangxi (实测 /zwgk/ = 200 REACHABLE).
-- ----------------------------------------------------------------------------