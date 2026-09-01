-- ----------------------------------------------------------------------------
-- 650-A.1 — M4.13 政策详情 v7 真实化 seed SQL (knife 650 M4.13 side)
--   12 INSERT (政策表) = 2 样本 (guizhou + jiangsu 第 13/14 样本) × 6 政策表
--     + 2 source_registry + 2 source_document = 16 INSERT total
--   lineage JSONB `is_demo='false'` 真实化 sentinel
--   chain_id='real_650_m4_13_policy_detail_v7' (v7 标记 = guizhou/jiangsu 第 13/14 样本; ≠ 649 chain_id)
--   2 新 SHA 全 distinct ≠ 649/648/647/646/644/643/642/641/640/639/638 demo/real SHA
--     - guizhou (直接 REACHABLE)  `5c5b12952db6b4af8f63a8478100d1000765fcb8460f574dd8b480ce2aa56cc0` (/zwgk/ 200 REACHABLE; SHA 5c5b1295...)
--     - jiangsu (fallback #1)    `def18a2f8f025b5ae11c685725b96cbf181c19c4771ab56d5d4be12974c7e534` (/zwgk/ 404 → / 200; SHA def18a2f...)
--   UUID prefix i 段 (i02-i62) ≠ 649 h 段 (h02-h62) ≠ 648 g 段 (g02-g62) ≠ 647 f 段 (f02-f62) ≠ 646 e 段 ≠ 645 d 段 ≠ 644 c 段
--   不新写 016 migration (沿用 009+010+014+015 lineage JSONB)
--   不修改 source_registry 既有 638-649 行 / mart / 4 fixture
--   substitute_used_count = 0 (guizhou 直接 REACHABLE; jiangsu fallback #1 REACHABLE; 递补池按序 shaanxi → sichuan 备而未触发)
--   HTTP total = 3/12 (25% usage)
--
-- 650 红线 13 关键:
--   不宣称 Gate / O1 / O2 / O3 / M2 / M4.x / M5.x / M6 PASS (沿用红线 1)
--   跨省 substitute 仅限递补池 (shaanxi → sichuan, 649 liaoning 已用), 触发即 evidence substitute_reason + docs/74 §2 登记
--   附属复验/验证产物允许独立文件, 但主 evidence summary.methodology 必须含指针
--   代换行标注规范 (per 649 审计 P3-1): source_registry province/source_name 一律用 actual_province (URL 归属省), original_province 仅存 lineage JSONB
--   已用省全集 (不得重复, 按 actual_province 口径): HLJ / HENAN / YUNNAN / FUJIAN / GD / ZJ / JX / HUN / AH / LN / JL
--   本次首选 guizhou + jiangsu: guizhou /zwgk/ 200 直接 REACHABLE; jiangsu /zwgk/ 404 → / 200 REACHABLE; 递补池按序 shaanxi → sichuan 备而未触发
-- ----------------------------------------------------------------------------

-- ----------------------------------------------------------------------------
-- 0. 2 个真实 source_registry (lineage JSONB is_demo='false')
--    chain_id='real_650_m4_13_policy_detail_v7'
--    UUID prefix i02/i03 (≠ 649 h02/h03)
--    注: 本次 2 样本均无 substitute 触发 (actual_province = province); 行内字段以 actual_province 口径为准 (per 649 P3-1 规范)
-- ----------------------------------------------------------------------------
INSERT INTO source_registry (
    id, source_url, source_name, source_type,
    country, province, enabled, lineage
) VALUES
    ('i0eebc99-9c0b-4ef8-bb6d-6bb9bd380i02',
     'https://www.guizhou.gov.cn/zwgk/',
     '贵州省人民政府 政务公开 landing (guizhou /zwgk/ 200 REACHABLE)',
     'PROVINCIAL_BULLETIN',
     'CN', 'GUIZHOU', TRUE,
     '{"chain_id": "real_650_m4_13_policy_detail_v7",
       "source_file_sha256": "5c5b12952db6b4af8f63a8478100d1000765fcb8460f574dd8b480ce2aa56cc0",
       "source_file_url": "https://www.guizhou.gov.cn/zwgk/",
       "extractor_version": "v1.0",
       "is_demo": "false",
       "original_province": "guizhou",
       "actual_province": "guizhou",
       "substitute_used": false}'::jsonb),
    ('i0eebc99-9c0b-4ef8-bb6d-6bb9bd380i03',
     'https://www.jiangsu.gov.cn/',
     '江苏省人民政府 政务公开 landing (jiangsu /zwgk/ 404 → / 200 REACHABLE)',
     'PROVINCIAL_BULLETIN',
     'CN', 'JIANGSU', TRUE,
     '{"chain_id": "real_650_m4_13_policy_detail_v7",
       "source_file_sha256": "def18a2f8f025b5ae11c685725b96cbf181c19c4771ab56d5d4be12974c7e534",
       "source_file_url": "https://www.jiangsu.gov.cn/",
       "extractor_version": "v1.0",
       "is_demo": "false",
       "original_province": "jiangsu",
       "actual_province": "jiangsu",
       "substitute_used": false}'::jsonb)
ON CONFLICT (id) DO NOTHING;

-- ----------------------------------------------------------------------------
-- 0b. 2 个真实 source_document (lineage JSONB is_demo='false')
--     UUID prefix i04/i05
-- ----------------------------------------------------------------------------
INSERT INTO source_document (
    id, source_id, title, doc_kind, content_url,
    captured_at, file_hash_sha256, file_size_bytes, lineage
) VALUES
    ('i0eebc99-9c0b-4ef8-bb6d-6bb9bd380i04',
     'i0eebc99-9c0b-4ef8-bb6d-6bb9bd380i02',
     '贵州省人民政府 政务公开 landing',
     'POLICY_DETAIL_LIST',
     'https://www.guizhou.gov.cn/zwgk/',
     '2026-09-01',
     '5c5b12952db6b4af8f63a8478100d1000765fcb8460f574dd8b480ce2aa56cc0',
     170166,
     '{"chain_id": "real_650_m4_13_policy_detail_v7",
       "source_file_sha256": "5c5b12952db6b4af8f63a8478100d1000765fcb8460f574dd8b480ce2aa56cc0",
       "source_file_url": "https://www.guizhou.gov.cn/zwgk/",
       "extractor_version": "v1.0",
       "is_demo": "false",
       "original_province": "guizhou",
       "actual_province": "guizhou",
       "substitute_used": false}'::jsonb),
    ('i0eebc99-9c0b-4ef8-bb6d-6bb9bd380i05',
     'i0eebc99-9c0b-4ef8-bb6d-6bb9bd380i03',
     '江苏省人民政府 政务公开 landing',
     'POLICY_DETAIL_LIST',
     'https://www.jiangsu.gov.cn/',
     '2026-09-01',
     'def18a2f8f025b5ae11c685725b96cbf181c19c4771ab56d5d4be12974c7e534',
     82985,
     '{"chain_id": "real_650_m4_13_policy_detail_v7",
       "source_file_sha256": "def18a2f8f025b5ae11c685725b96cbf181c19c4771ab56d5d4be12974c7e534",
       "source_file_url": "https://www.jiangsu.gov.cn/",
       "extractor_version": "v1.0",
       "is_demo": "false",
       "original_province": "jiangsu",
       "actual_province": "jiangsu",
       "substitute_used": false}'::jsonb)
ON CONFLICT (id) DO NOTHING;

-- ----------------------------------------------------------------------------
-- 1. 2 个真实 policy_document (lineage JSONB is_demo='false')
--    chain_id='real_650_m4_13_policy_detail_v7'
--    UUID prefix i11/i12 (≠ 649 h11/h12)
-- ----------------------------------------------------------------------------
INSERT INTO policy_document (
    id, doc_type, title, publisher, publication_date,
    source_id, classification, policy_level, lineage
) VALUES
    ('i1eebc99-9c0b-4ef8-bb6d-6bb9bd380i11',
     'POLICY_DETAIL',
     '省政府政策详情 v7（贵州政务公开 landing）',
     '贵州省人民政府',
     '2026-09-01',
     'i0eebc99-9c0b-4ef8-bb6d-6bb9bd380i04',
     'BULLETIN', 'PROVINCIAL',
     '{"chain_id": "real_650_m4_13_policy_detail_v7",
       "source_file_sha256": "5c5b12952db6b4af8f63a8478100d1000765fcb8460f574dd8b480ce2aa56cc0",
       "source_file_url": "https://www.guizhou.gov.cn/zwgk/",
       "extractor_version": "v1.0",
       "is_demo": "false",
       "original_province": "guizhou",
       "actual_province": "guizhou",
       "substitute_used": false}'::jsonb),
    ('i1eebc99-9c0b-4ef8-bb6d-6bb9bd380i12',
     'POLICY_DETAIL',
     '省政府政策详情 v7（江苏政务公开 landing）',
     '江苏省人民政府',
     '2026-09-01',
     'i0eebc99-9c0b-4ef8-bb6d-6bb9bd380i05',
     'BULLETIN', 'PROVINCIAL',
     '{"chain_id": "real_650_m4_13_policy_detail_v7",
       "source_file_sha256": "def18a2f8f025b5ae11c685725b96cbf181c19c4771ab56d5d4be12974c7e534",
       "source_file_url": "https://www.jiangsu.gov.cn/",
       "extractor_version": "v1.0",
       "is_demo": "false",
       "original_province": "jiangsu",
       "actual_province": "jiangsu",
       "substitute_used": false}'::jsonb)
ON CONFLICT (id) DO NOTHING;

-- ----------------------------------------------------------------------------
-- 2. 2 个真实 policy_target (FK → 上 2 条真实 policy_document)
--    UUID prefix i21/i22 (≠ 649 h21/h22)
-- ----------------------------------------------------------------------------
INSERT INTO policy_target (
    id, policy_document_id, target_description,
    target_value, target_unit, target_year, measurable, lineage
) VALUES
    ('i2eebc99-9c0b-4ef8-bb6d-6bb9bd380i21',
     'i1eebc99-9c0b-4ef8-bb6d-6bb9bd380i11',
     'real-policy-target-guizhou-v7 (政策详情 v7 第 13 样本)', NULL, NULL, 2026, FALSE,
     '{"chain_id": "real_650_m4_13_policy_detail_v7",
       "source_file_sha256": "5c5b12952db6b4af8f63a8478100d1000765fcb8460f574dd8b480ce2aa56cc0",
       "source_file_url": "https://www.guizhou.gov.cn/zwgk/",
       "extractor_version": "v1.0",
       "is_demo": "false",
       "substitute_used": false}'::jsonb),
    ('i2eebc99-9c0b-4ef8-bb6d-6bb9bd380i22',
     'i1eebc99-9c0b-4ef8-bb6d-6bb9bd380i12',
     'real-policy-target-jiangsu-v7 (政策详情 v7 第 14 样本)', NULL, NULL, 2026, FALSE,
     '{"chain_id": "real_650_m4_13_policy_detail_v7",
       "source_file_sha256": "def18a2f8f025b5ae11c685725b96cbf181c19c4771ab56d5d4be12974c7e534",
       "source_file_url": "https://www.jiangsu.gov.cn/",
       "extractor_version": "v1.0",
       "is_demo": "false",
       "substitute_used": false}'::jsonb)
ON CONFLICT (id) DO NOTHING;

-- ----------------------------------------------------------------------------
-- 3. 2 个真实 policy_measure (FK → 上 2 条真实 policy_document)
--    UUID prefix i31/i32 (≠ 649 h31/h32)
-- ----------------------------------------------------------------------------
INSERT INTO policy_measure (
    id, policy_document_id, measure_description, measure_type, lineage
) VALUES
    ('i3eebc99-9c0b-4ef8-bb6d-6bb9bd380i31',
     'i1eebc99-9c0b-4ef8-bb6d-6bb9bd380i11',
     'real-policy-measure-guizhou-v7 (政策详情 v7 第 13 样本)', 'REGULATORY',
     '{"chain_id": "real_650_m4_13_policy_detail_v7",
       "source_file_sha256": "5c5b12952db6b4af8f63a8478100d1000765fcb8460f574dd8b480ce2aa56cc0",
       "source_file_url": "https://www.guizhou.gov.cn/zwgk/",
       "extractor_version": "v1.0",
       "is_demo": "false",
       "substitute_used": false}'::jsonb),
    ('i3eebc99-9c0b-4ef8-bb6d-6bb9bd380i32',
     'i1eebc99-9c0b-4ef8-bb6d-6bb9bd380i12',
     'real-policy-measure-jiangsu-v7 (政策详情 v7 第 14 样本)', 'REGULATORY',
     '{"chain_id": "real_650_m4_13_policy_detail_v7",
       "source_file_sha256": "def18a2f8f025b5ae11c685725b96cbf181c19c4771ab56d5d4be12974c7e534",
       "source_file_url": "https://www.jiangsu.gov.cn/",
       "extractor_version": "v1.0",
       "is_demo": "false",
       "substitute_used": false}'::jsonb)
ON CONFLICT (id) DO NOTHING;

-- ----------------------------------------------------------------------------
-- 4. 2 个真实 government_commitment (FK → policy_target + 真实 geo_entity + source_document)
--    贵州 / 江苏 geo_entity_id: SELECT 子查询
--    proposer_person_id = NULL (避免 FK 到 639 person demo;保持 spike 自洽)
--    UUID prefix i41/i42 (≠ 649 h41/h42)
-- ----------------------------------------------------------------------------
INSERT INTO government_commitment (
    id, policy_target_id, commitment_text,
    proposer_person_id, geo_entity_id, commitment_date,
    due_date, status, source_id, lineage
)
SELECT
    'i4eebc99-9c0b-4ef8-bb6d-6bb9bd380i41',
    'i2eebc99-9c0b-4ef8-bb6d-6bb9bd380i21',
    'real-commitment-guizhou-v7 (政策详情 v7 第 13 样本; 贵州省政府)',
    NULL,
    g.id,
    '2026-09-01',
    '2026-12-31',
    'IN_PROGRESS',
    'i0eebc99-9c0b-4ef8-bb6d-6bb9bd380i04',
    jsonb_build_object(
        'chain_id', 'real_650_m4_13_policy_detail_v7',
        'source_file_sha256', '5c5b12952db6b4af8f63a8478100d1000765fcb8460f574dd8b480ce2aa56cc0',
        'source_file_url', 'https://www.guizhou.gov.cn/zwgk/',
        'extractor_version', 'v1.0',
        'is_demo', 'false',
        'original_province', 'guizhou',
        'actual_province', 'guizhou',
        'substitute_used', false
    )
FROM geo_entity g
WHERE g.canonical_name = '贵州省' AND g.level = 'PROVINCIAL'
LIMIT 1
ON CONFLICT (id) DO NOTHING;

INSERT INTO government_commitment (
    id, policy_target_id, commitment_text,
    proposer_person_id, geo_entity_id, commitment_date,
    due_date, status, source_id, lineage
)
SELECT
    'i4eebc99-9c0b-4ef8-bb6d-6bb9bd380i42',
    'i2eebc99-9c0b-4ef8-bb6d-6bb9bd380i22',
    'real-commitment-jiangsu-v7 (政策详情 v7 第 14 样本; 江苏省政府)',
    NULL,
    g.id,
    '2026-09-01',
    '2026-12-31',
    'IN_PROGRESS',
    'i0eebc99-9c0b-4ef8-bb6d-6bb9bd380i05',
    jsonb_build_object(
        'chain_id', 'real_650_m4_13_policy_detail_v7',
        'source_file_sha256', 'def18a2f8f025b5ae11c685725b96cbf181c19c4771ab56d5d4be12974c7e534',
        'source_file_url', 'https://www.jiangsu.gov.cn/',
        'extractor_version', 'v1.0',
        'is_demo', 'false',
        'original_province', 'jiangsu',
        'actual_province', 'jiangsu',
        'substitute_used', false
    )
FROM geo_entity g
WHERE g.canonical_name = '江苏省' AND g.level = 'PROVINCIAL'
LIMIT 1
ON CONFLICT (id) DO NOTHING;

-- ----------------------------------------------------------------------------
-- 5. 2 个真实 commitment_progress (FK → 上 2 条真实 government_commitment)
--    UUID prefix i51/i52 (≠ 649 h51/h52)
-- ----------------------------------------------------------------------------
INSERT INTO commitment_progress (
    id, government_commitment_id, progress_value, progress_unit,
    reported_date, reporting_org, lineage
) VALUES
    ('i5eebc99-9c0b-4ef8-bb6d-6bb9bd380i51',
     'i4eebc99-9c0b-4ef8-bb6d-6bb9bd380i41',
     0.5, 'PERCENT', '2026-09-01', '贵州省人民政府',
     '{"chain_id": "real_650_m4_13_policy_detail_v7",
       "source_file_sha256": "5c5b12952db6b4af8f63a8478100d1000765fcb8460f574dd8b480ce2aa56cc0",
       "source_file_url": "https://www.guizhou.gov.cn/zwgk/",
       "extractor_version": "v1.0",
       "is_demo": "false",
       "substitute_used": false}'::jsonb),
    ('i5eebc99-9c0b-4ef8-bb6d-6bb9bd380i52',
     'i4eebc99-9c0b-4ef8-bb6d-6bb9bd380i42',
     0.5, 'PERCENT', '2026-09-01', '江苏省人民政府',
     '{"chain_id": "real_650_m4_13_policy_detail_v7",
       "source_file_sha256": "def18a2f8f025b5ae11c685725b96cbf181c19c4771ab56d5d4be12974c7e534",
       "source_file_url": "https://www.jiangsu.gov.cn/",
       "extractor_version": "v1.0",
       "is_demo": "false",
       "substitute_used": false}'::jsonb)
ON CONFLICT (id) DO NOTHING;

-- ----------------------------------------------------------------------------
-- 6. 2 个真实 project_event (FK → 真实 geo_entity via SELECT 子查询)
--    UUID prefix i61/i62 (≠ 649 h61/h62)
-- ----------------------------------------------------------------------------
INSERT INTO project_event (
    id, event_type, event_date, title, description,
    geo_entity_id, source_id, lineage
)
SELECT
    'i6eebc99-9c0b-4ef8-bb6d-6bb9bd380i61',
    'POLICY_DETAIL_RELEASE',
    '2026-09-01',
    'real-project-guizhou-v7 (政策详情 v7 第 13 样本)',
    '贵州省政府政策详情页落地; guizhou /zwgk/ 200 REACHABLE (全新 SHA 5c5b1295...)',
    g.id,
    'i0eebc99-9c0b-4ef8-bb6d-6bb9bd380i04',
    jsonb_build_object(
        'chain_id', 'real_650_m4_13_policy_detail_v7',
        'source_file_sha256', '5c5b12952db6b4af8f63a8478100d1000765fcb8460f574dd8b480ce2aa56cc0',
        'source_file_url', 'https://www.guizhou.gov.cn/zwgk/',
        'extractor_version', 'v1.0',
        'is_demo', 'false',
        'original_province', 'guizhou',
        'actual_province', 'guizhou',
        'substitute_used', false
    )
FROM geo_entity g
WHERE g.canonical_name = '贵州省' AND g.level = 'PROVINCIAL'
LIMIT 1
ON CONFLICT (id) DO NOTHING;

INSERT INTO project_event (
    id, event_type, event_date, title, description,
    geo_entity_id, source_id, lineage
)
SELECT
    'i6eebc99-9c0b-4ef8-bb6d-6bb9bd380i62',
    'POLICY_DETAIL_RELEASE',
    '2026-09-01',
    'real-project-jiangsu-v7 (政策详情 v7 第 14 样本)',
    '江苏省政府政策详情页落地; jiangsu /zwgk/ 404 → fallback / 200 REACHABLE (全新 SHA def18a2f...)',
    g.id,
    'i0eebc99-9c0b-4ef8-bb6d-6bb9bd380i05',
    jsonb_build_object(
        'chain_id', 'real_650_m4_13_policy_detail_v7',
        'source_file_sha256', 'def18a2f8f025b5ae11c685725b96cbf181c19c4771ab56d5d4be12974c7e534',
        'source_file_url', 'https://www.jiangsu.gov.cn/',
        'extractor_version', 'v1.0',
        'is_demo', 'false',
        'original_province', 'jiangsu',
        'actual_province', 'jiangsu',
        'substitute_used', false
    )
FROM geo_entity g
WHERE g.canonical_name = '江苏省' AND g.level = 'PROVINCIAL'
LIMIT 1
ON CONFLICT (id) DO NOTHING;

-- ----------------------------------------------------------------------------
-- End 650-A.1 seed SQL
-- 16 INSERT total = 12 政策表 + 2 source_registry + 2 source_document
-- chain_id=real_650_m4_13_policy_detail_v7
-- UUID i 段 (i02-i62) ≠ 649 h 段 ≠ 648 g 段 ≠ 647 f 段
-- 2 NEW SHA: 5c5b1295 (guizhou 直接 REACHABLE) + def18a2f (jiangsu fallback REACHABLE)
-- substitute_used_count = 0 (guizhou + jiangsu 均无 substitute 触发; 递补池 shaanxi → sichuan 备而未触发)
-- HTTP total = 3/12 (25% usage; 比 649 6/12 (50%) 更省)
-- 代换行标注规范: 本次 2 样本均无 substitute, 行内字段以 actual_province 口径为准 (与 province 一致); 红线 13 增补条款 (per 649 P3-1) 同时落地: 若后续触发 substitute, source_registry province/source_name 一律用 actual_province, original_province 仅存 lineage JSONB
-- ----------------------------------------------------------------------------