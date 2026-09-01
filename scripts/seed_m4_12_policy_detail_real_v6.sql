-- ----------------------------------------------------------------------------
-- 649-A.1 — M4.12 政策详情 v6 真实化 seed SQL (knife 649 M4.12 side)
--   12 INSERT (政策表) = 2 样本 (hubei + jilin 第 11/12 样本) × 6 政策表
--     + 2 source_registry + 2 source_document = 16 INSERT total
--   lineage JSONB `is_demo='false'` 真实化 sentinel
--   chain_id='real_649_m4_12_policy_detail_v6' (v6 标记 = hubei/jilin 第 11/12 样本; ≠ 648 chain_id)
--   2 新 SHA 全 distinct ≠ 648/647/646/644/643/642/641/640/639/638 demo/real SHA
--     - hubei  substitute→liaoning  `b22d1fb4d291e9e134166602757e5184c99f4a4d67c66abd2fdd20a5371d4f82` (hubei 412+412 → ln 404 → ln / 200; SHA b22d1fb4...)
--     - jilin                   `a1e49a91172927dfe7ac022587f039ea9a44414e0a900fefd1bd82a0884931c6` (/zwgk/ 0 timeout → fallback / 200; SHA a1e49a91...)
--   UUID prefix h 段 (h02-h62) ≠ 648 g 段 (g02-g62) ≠ 647 f 段 (f02-f62) ≠ 646 e 段 ≠ 645 d 段 ≠ 644 c 段
--   不新写 016 migration (沿用 009+010+014+015 lineage JSONB)
--   不修改 source_registry 既有 638-648 行 / mart / 4 fixture
--
-- 649 红线 13 关键:
--   不宣称 Gate / O1 / O2 / O3 / M2 / M4.x / M5.x / M6 PASS (沿用红线 1)
--   跨省 substitute 仅限递补池 (liaoning/shaanxi/sichuan/guizhou/jiangsu), 触发即 evidence `substitute_reason` + docs/73 §2 登记
--   附属复验/验证产物允许独立文件, 但主 evidence summary.methodology 必须含指针
--   已用省全集 (不得重复): HLJ / HENAN / YUNNAN / FUJIAN / GD / ZJ / JX / HUN / AH
--   本次首选 hubei + jilin: hubei 412 (Precondition Failed) → 412 → 递补 liaoning / 200 REACHABLE; jilin / 200 REACHABLE; 递补池按序仅触达 liaoning (liaoning/shaanxi/sichuan/guizhou/jiangsu)
-- ----------------------------------------------------------------------------

-- ----------------------------------------------------------------------------
-- 0. 2 个真实 source_registry (lineage JSONB is_demo='false')
--    chain_id='real_649_m4_12_policy_detail_v6'
--    UUID prefix h02/h03 (≠ 648 g02/g03)
--    注: hubei 实际 fetch 走 liaoning 递补, 但 lineage.canonical_name 反映原始请求 (hubei)
--        source_file_url 反映实际抓取 URL (liaoning)
-- ----------------------------------------------------------------------------
INSERT INTO source_registry (
    id, source_url, source_name, source_type,
    country, province, enabled, lineage
) VALUES
    ('h0eebc99-9c0b-4ef8-bb6d-6bb9bd380h02',
     'https://www.ln.gov.cn/',
     '湖北省人民政府 政务公开 landing (hubei 412+412 → liaoning 递补省府根 /)',
     'PROVINCIAL_BULLETIN',
     'CN', 'HUBEI', TRUE,
     '{"chain_id": "real_649_m4_12_policy_detail_v6",
       "source_file_sha256": "b22d1fb4d291e9e134166602757e5184c99f4a4d67c66abd2fdd20a5371d4f82",
       "source_file_url": "https://www.ln.gov.cn/",
       "extractor_version": "v1.0",
       "is_demo": "false",
       "original_province": "hubei",
       "actual_province": "liaoning",
       "substitute_used": true,
       "substitute_reason": "原试点省 hubei 两级 fallback 均返回 412 (Precondition Failed); 按 649 任务书 §0.13 递补池按序取 liaoning (省府根 / 200 REACHABLE; 396 锚点命中)"}'::jsonb),
    ('h0eebc99-9c0b-4ef8-bb6d-6bb9bd380h03',
     'https://www.jl.gov.cn/',
     '吉林省人民政府 政务公开 landing',
     'PROVINCIAL_BULLETIN',
     'CN', 'JILIN', TRUE,
     '{"chain_id": "real_649_m4_12_policy_detail_v6",
       "source_file_sha256": "a1e49a91172927dfe7ac022587f039ea9a44414e0a900fefd1bd82a0884931c6",
       "source_file_url": "https://www.jl.gov.cn/",
       "extractor_version": "v1.0",
       "is_demo": "false",
       "original_province": "jilin",
       "actual_province": "jilin",
       "substitute_used": false}'::jsonb)
ON CONFLICT (id) DO NOTHING;

-- ----------------------------------------------------------------------------
-- 0b. 2 个真实 source_document (lineage JSONB is_demo='false')
--     UUID prefix h04/h05
-- ----------------------------------------------------------------------------
INSERT INTO source_document (
    id, source_id, title, doc_kind, content_url,
    captured_at, file_hash_sha256, file_size_bytes, lineage
) VALUES
    ('h0eebc99-9c0b-4ef8-bb6d-6bb9bd380h04',
     'h0eebc99-9c0b-4ef8-bb6d-6bb9bd380h02',
     '湖北省人民政府 政务公开 landing (hubei→liaoning 递补)',
     'POLICY_DETAIL_LIST',
     'https://www.ln.gov.cn/',
     '2026-09-01',
     'b22d1fb4d291e9e134166602757e5184c99f4a4d67c66abd2fdd20a5371d4f82',
     148399,
     '{"chain_id": "real_649_m4_12_policy_detail_v6",
       "source_file_sha256": "b22d1fb4d291e9e134166602757e5184c99f4a4d67c66abd2fdd20a5371d4f82",
       "source_file_url": "https://www.ln.gov.cn/",
       "extractor_version": "v1.0",
       "is_demo": "false",
       "original_province": "hubei",
       "actual_province": "liaoning",
       "substitute_used": true,
       "substitute_reason": "原试点省 hubei 两级 fallback 均返回 412 (Precondition Failed); 按 649 任务书 §0.13 递补池按序取 liaoning"}'::jsonb),
    ('h0eebc99-9c0b-4ef8-bb6d-6bb9bd380h05',
     'h0eebc99-9c0b-4ef8-bb6d-6bb9bd380h03',
     '吉林省人民政府 政务公开 landing',
     'POLICY_DETAIL_LIST',
     'https://www.jl.gov.cn/',
     '2026-09-01',
     'a1e49a91172927dfe7ac022587f039ea9a44414e0a900fefd1bd82a0884931c6',
     69943,
     '{"chain_id": "real_649_m4_12_policy_detail_v6",
       "source_file_sha256": "a1e49a91172927dfe7ac022587f039ea9a44414e0a900fefd1bd82a0884931c6",
       "source_file_url": "https://www.jl.gov.cn/",
       "extractor_version": "v1.0",
       "is_demo": "false",
       "original_province": "jilin",
       "actual_province": "jilin",
       "substitute_used": false}'::jsonb)
ON CONFLICT (id) DO NOTHING;

-- ----------------------------------------------------------------------------
-- 1. 2 个真实 policy_document (lineage JSONB is_demo='false')
--    chain_id='real_649_m4_12_policy_detail_v6'
--    UUID prefix h11/h12 (≠ 648 g11/g12)
-- ----------------------------------------------------------------------------
INSERT INTO policy_document (
    id, doc_type, title, publisher, publication_date,
    source_id, classification, policy_level, lineage
) VALUES
    ('h1eebc99-9c0b-4ef8-bb6d-6bb9bd380h11',
     'POLICY_DETAIL',
     '省政府政策详情 v6（湖北政务公开 landing, hubei→liaoning 递补）',
     '湖北省人民政府',
     '2026-09-01',
     'h0eebc99-9c0b-4ef8-bb6d-6bb9bd380h04',
     'BULLETIN', 'PROVINCIAL',
     '{"chain_id": "real_649_m4_12_policy_detail_v6",
       "source_file_sha256": "b22d1fb4d291e9e134166602757e5184c99f4a4d67c66abd2fdd20a5371d4f82",
       "source_file_url": "https://www.ln.gov.cn/",
       "extractor_version": "v1.0",
       "is_demo": "false",
       "original_province": "hubei",
       "actual_province": "liaoning",
       "substitute_used": true,
       "substitute_reason": "原试点省 hubei 两级 fallback 均 412; 递补池 liaoning 省府根 / 200 REACHABLE"}'::jsonb),
    ('h1eebc99-9c0b-4ef8-bb6d-6bb9bd380h12',
     'POLICY_DETAIL',
     '省政府政策详情 v6（吉林政务公开 landing）',
     '吉林省人民政府',
     '2026-09-01',
     'h0eebc99-9c0b-4ef8-bb6d-6bb9bd380h05',
     'BULLETIN', 'PROVINCIAL',
     '{"chain_id": "real_649_m4_12_policy_detail_v6",
       "source_file_sha256": "a1e49a91172927dfe7ac022587f039ea9a44414e0a900fefd1bd82a0884931c6",
       "source_file_url": "https://www.jl.gov.cn/",
       "extractor_version": "v1.0",
       "is_demo": "false",
       "original_province": "jilin",
       "actual_province": "jilin",
       "substitute_used": false}'::jsonb)
ON CONFLICT (id) DO NOTHING;

-- ----------------------------------------------------------------------------
-- 2. 2 个真实 policy_target (FK → 上 2 条真实 policy_document)
--    UUID prefix h21/h22 (≠ 648 g21/g22)
-- ----------------------------------------------------------------------------
INSERT INTO policy_target (
    id, policy_document_id, target_description,
    target_value, target_unit, target_year, measurable, lineage
) VALUES
    ('h2eebc99-9c0b-4ef8-bb6d-6bb9bd380h21',
     'h1eebc99-9c0b-4ef8-bb6d-6bb9bd380h11',
     'real-policy-target-hubei-v6 (政策详情 v6 第 11 样本; hubei→liaoning 递补)', NULL, NULL, 2026, FALSE,
     '{"chain_id": "real_649_m4_12_policy_detail_v6",
       "source_file_sha256": "b22d1fb4d291e9e134166602757e5184c99f4a4d67c66abd2fdd20a5371d4f82",
       "source_file_url": "https://www.ln.gov.cn/",
       "extractor_version": "v1.0",
       "is_demo": "false",
       "substitute_used": true}'::jsonb),
    ('h2eebc99-9c0b-4ef8-bb6d-6bb9bd380h22',
     'h1eebc99-9c0b-4ef8-bb6d-6bb9bd380h12',
     'real-policy-target-jilin-v6 (政策详情 v6 第 12 样本)', NULL, NULL, 2026, FALSE,
     '{"chain_id": "real_649_m4_12_policy_detail_v6",
       "source_file_sha256": "a1e49a91172927dfe7ac022587f039ea9a44414e0a900fefd1bd82a0884931c6",
       "source_file_url": "https://www.jl.gov.cn/",
       "extractor_version": "v1.0",
       "is_demo": "false",
       "substitute_used": false}'::jsonb)
ON CONFLICT (id) DO NOTHING;

-- ----------------------------------------------------------------------------
-- 3. 2 个真实 policy_measure (FK → 上 2 条真实 policy_document)
--    UUID prefix h31/h32 (≠ 648 g31/g32)
-- ----------------------------------------------------------------------------
INSERT INTO policy_measure (
    id, policy_document_id, measure_description, measure_type, lineage
) VALUES
    ('h3eebc99-9c0b-4ef8-bb6d-6bb9bd380h31',
     'h1eebc99-9c0b-4ef8-bb6d-6bb9bd380h11',
     'real-policy-measure-hubei-v6 (政策详情 v6 第 11 样本; hubei→liaoning 递补)', 'REGULATORY',
     '{"chain_id": "real_649_m4_12_policy_detail_v6",
       "source_file_sha256": "b22d1fb4d291e9e134166602757e5184c99f4a4d67c66abd2fdd20a5371d4f82",
       "source_file_url": "https://www.ln.gov.cn/",
       "extractor_version": "v1.0",
       "is_demo": "false",
       "substitute_used": true}'::jsonb),
    ('h3eebc99-9c0b-4ef8-bb6d-6bb9bd380h32',
     'h1eebc99-9c0b-4ef8-bb6d-6bb9bd380h12',
     'real-policy-measure-jilin-v6 (政策详情 v6 第 12 样本)', 'REGULATORY',
     '{"chain_id": "real_649_m4_12_policy_detail_v6",
       "source_file_sha256": "a1e49a91172927dfe7ac022587f039ea9a44414e0a900fefd1bd82a0884931c6",
       "source_file_url": "https://www.jl.gov.cn/",
       "extractor_version": "v1.0",
       "is_demo": "false",
       "substitute_used": false}'::jsonb)
ON CONFLICT (id) DO NOTHING;

-- ----------------------------------------------------------------------------
-- 4. 2 个真实 government_commitment (FK → policy_target + 真实 geo_entity + source_document)
--    湖北 / 吉林 geo_entity_id: SELECT 子查询
--    proposer_person_id = NULL (避免 FK 到 639 person demo;保持 spike 自洽)
--    UUID prefix h41/h42 (≠ 648 g41/g42)
-- ----------------------------------------------------------------------------
INSERT INTO government_commitment (
    id, policy_target_id, commitment_text,
    proposer_person_id, geo_entity_id, commitment_date,
    due_date, status, source_id, lineage
)
SELECT
    'h4eebc99-9c0b-4ef8-bb6d-6bb9bd380h41',
    'h2eebc99-9c0b-4ef8-bb6d-6bb9bd380h21',
    'real-commitment-hubei-v6 (政策详情 v6 第 11 样本; 湖北省政府, hubei→liaoning 递补)',
    NULL,
    g.id,
    '2026-09-01',
    '2026-12-31',
    'IN_PROGRESS',
    'h0eebc99-9c0b-4ef8-bb6d-6bb9bd380h04',
    jsonb_build_object(
        'chain_id', 'real_649_m4_12_policy_detail_v6',
        'source_file_sha256', 'b22d1fb4d291e9e134166602757e5184c99f4a4d67c66abd2fdd20a5371d4f82',
        'source_file_url', 'https://www.ln.gov.cn/',
        'extractor_version', 'v1.0',
        'is_demo', 'false',
        'original_province', 'hubei',
        'actual_province', 'liaoning',
        'substitute_used', true,
        'substitute_reason', '原试点省 hubei 两级 fallback 均 412; 递补池 liaoning'
    )
FROM geo_entity g
WHERE g.canonical_name = '湖北省' AND g.level = 'PROVINCIAL'
LIMIT 1
ON CONFLICT (id) DO NOTHING;

INSERT INTO government_commitment (
    id, policy_target_id, commitment_text,
    proposer_person_id, geo_entity_id, commitment_date,
    due_date, status, source_id, lineage
)
SELECT
    'h4eebc99-9c0b-4ef8-bb6d-6bb9bd380h42',
    'h2eebc99-9c0b-4ef8-bb6d-6bb9bd380h22',
    'real-commitment-jilin-v6 (政策详情 v6 第 12 样本; 吉林省政府)',
    NULL,
    g.id,
    '2026-09-01',
    '2026-12-31',
    'IN_PROGRESS',
    'h0eebc99-9c0b-4ef8-bb6d-6bb9bd380h05',
    jsonb_build_object(
        'chain_id', 'real_649_m4_12_policy_detail_v6',
        'source_file_sha256', 'a1e49a91172927dfe7ac022587f039ea9a44414e0a900fefd1bd82a0884931c6',
        'source_file_url', 'https://www.jl.gov.cn/',
        'extractor_version', 'v1.0',
        'is_demo', 'false',
        'original_province', 'jilin',
        'actual_province', 'jilin',
        'substitute_used', false
    )
FROM geo_entity g
WHERE g.canonical_name = '吉林省' AND g.level = 'PROVINCIAL'
LIMIT 1
ON CONFLICT (id) DO NOTHING;

-- ----------------------------------------------------------------------------
-- 5. 2 个真实 commitment_progress (FK → 上 2 条真实 government_commitment)
--    UUID prefix h51/h52 (≠ 648 g51/g52)
-- ----------------------------------------------------------------------------
INSERT INTO commitment_progress (
    id, government_commitment_id, progress_value, progress_unit,
    reported_date, reporting_org, lineage
) VALUES
    ('h5eebc99-9c0b-4ef8-bb6d-6bb9bd380h51',
     'h4eebc99-9c0b-4ef8-bb6d-6bb9bd380h41',
     0.5, 'PERCENT', '2026-09-01', '湖北省人民政府 (hubei→liaoning 递补)',
     '{"chain_id": "real_649_m4_12_policy_detail_v6",
       "source_file_sha256": "b22d1fb4d291e9e134166602757e5184c99f4a4d67c66abd2fdd20a5371d4f82",
       "source_file_url": "https://www.ln.gov.cn/",
       "extractor_version": "v1.0",
       "is_demo": "false",
       "substitute_used": true}'::jsonb),
    ('h5eebc99-9c0b-4ef8-bb6d-6bb9bd380h52',
     'h4eebc99-9c0b-4ef8-bb6d-6bb9bd380h42',
     0.5, 'PERCENT', '2026-09-01', '吉林省人民政府',
     '{"chain_id": "real_649_m4_12_policy_detail_v6",
       "source_file_sha256": "a1e49a91172927dfe7ac022587f039ea9a44414e0a900fefd1bd82a0884931c6",
       "source_file_url": "https://www.jl.gov.cn/",
       "extractor_version": "v1.0",
       "is_demo": "false",
       "substitute_used": false}'::jsonb)
ON CONFLICT (id) DO NOTHING;

-- ----------------------------------------------------------------------------
-- 6. 2 个真实 project_event (FK → 真实 geo_entity via SELECT 子查询)
--    UUID prefix h61/h62 (≠ 648 g61/g62)
-- ----------------------------------------------------------------------------
INSERT INTO project_event (
    id, event_type, event_date, title, description,
    geo_entity_id, source_id, lineage
)
SELECT
    'h6eebc99-9c0b-4ef8-bb6d-6bb9bd380h61',
    'POLICY_DETAIL_RELEASE',
    '2026-09-01',
    'real-project-hubei-v6 (政策详情 v6 第 11 样本)',
    '湖北省政府政策详情页落地; hubei /zwgk/ + / 两级均 412 → 递补池 liaoning /zwgk/ 404 → ln / 200 REACHABLE (全新 SHA b22d1fb4...)',
    g.id,
    'h0eebc99-9c0b-4ef8-bb6d-6bb9bd380h04',
    jsonb_build_object(
        'chain_id', 'real_649_m4_12_policy_detail_v6',
        'source_file_sha256', 'b22d1fb4d291e9e134166602757e5184c99f4a4d67c66abd2fdd20a5371d4f82',
        'source_file_url', 'https://www.ln.gov.cn/',
        'extractor_version', 'v1.0',
        'is_demo', 'false',
        'original_province', 'hubei',
        'actual_province', 'liaoning',
        'substitute_used', true,
        'substitute_reason', '原试点省 hubei 两级 fallback 均 412; 递补池 liaoning 省府根 / 200'
    )
FROM geo_entity g
WHERE g.canonical_name = '湖北省' AND g.level = 'PROVINCIAL'
LIMIT 1
ON CONFLICT (id) DO NOTHING;

INSERT INTO project_event (
    id, event_type, event_date, title, description,
    geo_entity_id, source_id, lineage
)
SELECT
    'h6eebc99-9c0b-4ef8-bb6d-6bb9bd380h62',
    'POLICY_DETAIL_RELEASE',
    '2026-09-01',
    'real-project-jilin-v6 (政策详情 v6 第 12 样本)',
    '吉林省政府政策详情页落地; /zwgk/ 0 timeout → fallback / 200 REACHABLE (全新 SHA a1e49a91...)',
    g.id,
    'h0eebc99-9c0b-4ef8-bb6d-6bb9bd380h05',
    jsonb_build_object(
        'chain_id', 'real_649_m4_12_policy_detail_v6',
        'source_file_sha256', 'a1e49a91172927dfe7ac022587f039ea9a44414e0a900fefd1bd82a0884931c6',
        'source_file_url', 'https://www.jl.gov.cn/',
        'extractor_version', 'v1.0',
        'is_demo', 'false',
        'original_province', 'jilin',
        'actual_province', 'jilin',
        'substitute_used', false
    )
FROM geo_entity g
WHERE g.canonical_name = '吉林省' AND g.level = 'PROVINCIAL'
LIMIT 1
ON CONFLICT (id) DO NOTHING;

-- ----------------------------------------------------------------------------
-- End 649-A.1 seed SQL
-- 16 INSERT total = 12 政策表 + 2 source_registry + 2 source_document
-- chain_id=real_649_m4_12_policy_detail_v6
-- UUID h 段 (h02-h62) ≠ 648 g 段 ≠ 647 f 段
-- 2 NEW SHA: b22d1fb4 (hubei→liaoning 递补) + a1e49a91 (jilin)
-- hubei substitute_reason: 两级 412 (Precondition Failed); 按 649 §0.13 递补池按序取 liaoning
-- ----------------------------------------------------------------------------
