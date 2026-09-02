-- ----------------------------------------------------------------------------
-- 652-A.1 — M4.15 政策详情 v9 真实化 seed SQL (knife 652 M4.15 side, 2026-09-02)
--   12 INSERT (政策表) = 2 样本 (xinjiang + nei_menggu 第 17/18 样本) × 6 政策表
--     + 2 source_registry + 2 source_document = 16 INSERT total
--   lineage JSONB `is_demo='false'` 真实化 sentinel
--   chain_id='real_652_m4_15_policy_detail_v9' (v9 标记 = xinjiang/nei_menggu 第 17/18 样本; ≠ 651 chain_id)
--   2 新 SHA 全 distinct ≠ 651/650/649/648/647/646/645/644/643/642/641/640/639/638 demo/real SHA
--     - xinjiang (fallback #1)   `21c8211bf7bf8b41569174e5ae2ae127f8e11439a04a5501209a63506ddca472` (/zwgk/ 403 WAF → / 200; SHA 21c8211b...)
--     - nei_menggu (zwgk/ 直)   `da1d4104db87c47809ef40f12bd8847d98c432bf990b0d7056f0042e6fd0533b` (/zwgk/ 200; SHA da1d4104...)
--   UUID prefix k 段 (k02-k62) ≠ 651 j 段 (j02-j62) ≠ 650 i 段 ≠ 649 h 段 ≠ 648 g 段 ≠ 647 f 段 ≠ 646 e 段 ≠ 645 d 段 ≠ 644 c 段
--   不新写 016 migration (沿用 009+010+014+015 lineage JSONB)
--   不修改 source_registry 既有 638-651 行 / mart / 4 fixture
--   substitute_used_count = 0 (xinjiang fallback #1 REACHABLE; nei_menggu 首选 REACHABLE; 递补池已耗尽 per 红线 14 沿用 651)
--   HTTP total = 3/12 (25% usage; xinjiang 2 + nei_menggu 1)
--   blocked_no_pool_count = 0 (本次双样本均 REACHABLE; BLOCKED_NO_POOL 分支代码存在并可达, e2e 守门见 tests/)
--
-- 652 红线 14 沿用 (per 651 §0.14 增补):
--   递补池 (SUBSTITUTE_POOL) 显式 [EXHAUSTED]; 任一样本槽两级 fallback 全失败 → BLOCKED_NO_POOL 留痕,
--   不再跨省代换 (per 651 §0.14 增补; 649 激活 liaoning + 650 备而未触发 + 651 转正 shaanxi/sichuan → 池耗尽)
--   本次双样本均 REACHABLE, 触发 verdict=REACHABLE, substitute_used=false, blocked_reason='' (空)
--   BLOCKED_NO_POOL 分支代码强制存在并可达 (per 652 §0.14 强制 e2e 验证; 即使本次未触发)
--
-- 652 红线 13 沿用:
--   不宣称 Gate / O1 / O2 / O3 / M2 / M4.x / M5.x / M6 PASS (沿用红线 1)
--   代换行标注规范 (per 649 审计 P3-1): source_registry province/source_name 一律用 actual_province (URL 归属省), original_province 仅存 lineage JSONB
--   已用省全集 (不得重复, 按 actual_province 口径, 16 省): HLJ / HENAN / YUNNAN / FUJIAN / GD / ZJ / JX / HUN / AH / LN / JL / GUIZHOU / JIANGSU / SHAANXI / SICHUAN; 652 增量 = XINJIANG / NEI MENGGU → 18 省
--   附属复验/验证产物允许独立文件, 但主 evidence summary.methodology 必须含指针
--   本次首选 xinjiang + nei_menggu: xinjiang /zwgk/ 403 WAF → / 200 REACHABLE; nei_menggu /zwgk/ 200 REACHABLE; 递补池 [EXHAUSTED] 备而永不触发
-- ----------------------------------------------------------------------------

-- ----------------------------------------------------------------------------
-- 0. 2 个真实 source_registry (lineage JSONB is_demo='false')
--    chain_id='real_652_m4_15_policy_detail_v9'
--    UUID prefix k02/k03 (≠ 651 j02/j03 ≠ 650 i02/i03 ≠ 649 h02/h03)
--    注: 本次 2 样本均无 substitute 触发 (actual_province = province); 行内字段以 actual_province 口径为准 (per 649 P3-1 规范)
-- ----------------------------------------------------------------------------
INSERT INTO source_registry (
    id, source_url, source_name, source_type,
    country, province, enabled, lineage
) VALUES
    ('k0eebc99-9c0b-4ef8-bb6d-6bb9bd380k02',
     'https://www.xinjiang.gov.cn/',
     '新疆维吾尔自治区人民政府 政务公开 landing (xinjiang /zwgk/ 403 WAF → / 200 REACHABLE)',
     'PROVINCIAL_BULLETIN',
     'CN', 'XINJIANG', TRUE,
     '{"chain_id": "real_652_m4_15_policy_detail_v9",
       "source_file_sha256": "21c8211bf7bf8b41569174e5ae2ae127f8e11439a04a5501209a63506ddca472",
       "source_file_url": "https://www.xinjiang.gov.cn/",
       "extractor_version": "v1.0",
       "is_demo": "false",
       "original_province": "xinjiang",
       "actual_province": "xinjiang",
       "substitute_used": false,
       "red_line_14_status": "EXHAUSTED",
       "substitute_pool_note": "per 651 §0.14 红线 14 增补 (沿用): 递补池正式耗尽; 本次未触发 substitute (xinjiang fallback #1 REACHABLE; nei_menggu 首选 REACHABLE)"}'::jsonb),
    ('k0eebc99-9c0b-4ef8-bb6d-6bb9bd380k03',
     'https://www.nmg.gov.cn/zwgk/',
     '内蒙古自治区人民政府 政务公开 (nei_menggu /zwgk/ 200 REACHABLE 首选直命中)',
     'PROVINCIAL_BULLETIN',
     'CN', 'NEI MENGGU', TRUE,
     '{"chain_id": "real_652_m4_15_policy_detail_v9",
       "source_file_sha256": "da1d4104db87c47809ef40f12bd8847d98c432bf990b0d7056f0042e6fd0533b",
       "source_file_url": "https://www.nmg.gov.cn/zwgk/",
       "extractor_version": "v1.0",
       "is_demo": "false",
       "original_province": "nei_menggu",
       "actual_province": "nei_menggu",
       "substitute_used": false,
       "red_line_14_status": "EXHAUSTED",
       "substitute_pool_note": "per 651 §0.14 红线 14 增补 (沿用): 递补池正式耗尽; 本次未触发 substitute (nei_menggu 首选 REACHABLE)"}'::jsonb)
ON CONFLICT (id) DO NOTHING;

-- ----------------------------------------------------------------------------
-- 0b. 2 个真实 source_document (lineage JSONB is_demo='false')
--     UUID prefix k04/k05
-- ----------------------------------------------------------------------------
INSERT INTO source_document (
    id, source_id, title, doc_kind, content_url,
    captured_at, file_hash_sha256, file_size_bytes, lineage
) VALUES
    ('k0eebc99-9c0b-4ef8-bb6d-6bb9bd380k04',
     'k0eebc99-9c0b-4ef8-bb6d-6bb9bd380k02',
     '新疆维吾尔自治区人民政府 政务公开 landing',
     'POLICY_DETAIL_LIST',
     'https://www.xinjiang.gov.cn/',
     '2026-09-02',
     '21c8211bf7bf8b41569174e5ae2ae127f8e11439a04a5501209a63506ddca472',
     108841,
     '{"chain_id": "real_652_m4_15_policy_detail_v9",
       "source_file_sha256": "21c8211bf7bf8b41569174e5ae2ae127f8e11439a04a5501209a63506ddca472",
       "source_file_url": "https://www.xinjiang.gov.cn/",
       "extractor_version": "v1.0",
       "is_demo": "false",
       "original_province": "xinjiang",
       "actual_province": "xinjiang",
       "substitute_used": false,
       "red_line_14_status": "EXHAUSTED"}'::jsonb),
    ('k0eebc99-9c0b-4ef8-bb6d-6bb9bd380k05',
     'k0eebc99-9c0b-4ef8-bb6d-6bb9bd380k03',
     '内蒙古自治区人民政府 政务公开',
     'POLICY_DETAIL_LIST',
     'https://www.nmg.gov.cn/zwgk/',
     '2026-09-02',
     'da1d4104db87c47809ef40f12bd8847d98c432bf990b0d7056f0042e6fd0533b',
     137602,
     '{"chain_id": "real_652_m4_15_policy_detail_v9",
       "source_file_sha256": "da1d4104db87c47809ef40f12bd8847d98c432bf990b0d7056f0042e6fd0533b",
       "source_file_url": "https://www.nmg.gov.cn/zwgk/",
       "extractor_version": "v1.0",
       "is_demo": "false",
       "original_province": "nei_menggu",
       "actual_province": "nei_menggu",
       "substitute_used": false,
       "red_line_14_status": "EXHAUSTED"}'::jsonb)
ON CONFLICT (id) DO NOTHING;

-- ----------------------------------------------------------------------------
-- 1. 2 个真实 policy_document (lineage JSONB is_demo='false')
--    chain_id='real_652_m4_15_policy_detail_v9'
--    UUID prefix k11/k12 (≠ 651 j11/j12 ≠ 650 i11/i12 ≠ 649 h11/h12)
-- ----------------------------------------------------------------------------
INSERT INTO policy_document (
    id, doc_type, title, publisher, publication_date,
    source_id, classification, policy_level, lineage
) VALUES
    ('k1eebc99-9c0b-4ef8-bb6d-6bb9bd380k11',
     'POLICY_DETAIL',
     '省政府政策详情 v9（新疆维吾尔自治区政务公开 landing）',
     '新疆维吾尔自治区人民政府',
     '2026-09-02',
     'k0eebc99-9c0b-4ef8-bb6d-6bb9bd380k04',
     'BULLETIN', 'PROVINCIAL',
     '{"chain_id": "real_652_m4_15_policy_detail_v9",
       "source_file_sha256": "21c8211bf7bf8b41569174e5ae2ae127f8e11439a04a5501209a63506ddca472",
       "source_file_url": "https://www.xinjiang.gov.cn/",
       "extractor_version": "v1.0",
       "is_demo": "false",
       "original_province": "xinjiang",
       "actual_province": "xinjiang",
       "substitute_used": false,
       "red_line_14_status": "EXHAUSTED"}'::jsonb),
    ('k1eebc99-9c0b-4ef8-bb6d-6bb9bd380k12',
     'POLICY_DETAIL',
     '省政府政策详情 v9（内蒙古自治区政务公开）',
     '内蒙古自治区人民政府',
     '2026-09-02',
     'k0eebc99-9c0b-4ef8-bb6d-6bb9bd380k05',
     'BULLETIN', 'PROVINCIAL',
     '{"chain_id": "real_652_m4_15_policy_detail_v9",
       "source_file_sha256": "da1d4104db87c47809ef40f12bd8847d98c432bf990b0d7056f0042e6fd0533b",
       "source_file_url": "https://www.nmg.gov.cn/zwgk/",
       "extractor_version": "v1.0",
       "is_demo": "false",
       "original_province": "nei_menggu",
       "actual_province": "nei_menggu",
       "substitute_used": false,
       "red_line_14_status": "EXHAUSTED"}'::jsonb)
ON CONFLICT (id) DO NOTHING;

-- ----------------------------------------------------------------------------
-- 2. 2 个真实 policy_target (FK → 上 2 条真实 policy_document)
--    UUID prefix k21/k22 (≠ 651 j21/j22 ≠ 650 i21/i22 ≠ 649 h21/h22)
-- ----------------------------------------------------------------------------
INSERT INTO policy_target (
    id, policy_document_id, target_description,
    target_value, target_unit, target_year, measurable, lineage
) VALUES
    ('k2eebc99-9c0b-4ef8-bb6d-6bb9bd380k21',
     'k1eebc99-9c0b-4ef8-bb6d-6bb9bd380k11',
     'real-policy-target-xinjiang-v9 (政策详情 v9 第 17 样本)', NULL, NULL, 2026, FALSE,
     '{"chain_id": "real_652_m4_15_policy_detail_v9",
       "source_file_sha256": "21c8211bf7bf8b41569174e5ae2ae127f8e11439a04a5501209a63506ddca472",
       "source_file_url": "https://www.xinjiang.gov.cn/",
       "extractor_version": "v1.0",
       "is_demo": "false",
       "substitute_used": false,
       "red_line_14_status": "EXHAUSTED"}'::jsonb),
    ('k2eebc99-9c0b-4ef8-bb6d-6bb9bd380k22',
     'k1eebc99-9c0b-4ef8-bb6d-6bb9bd380k12',
     'real-policy-target-nei_menggu-v9 (政策详情 v9 第 18 样本)', NULL, NULL, 2026, FALSE,
     '{"chain_id": "real_652_m4_15_policy_detail_v9",
       "source_file_sha256": "da1d4104db87c47809ef40f12bd8847d98c432bf990b0d7056f0042e6fd0533b",
       "source_file_url": "https://www.nmg.gov.cn/zwgk/",
       "extractor_version": "v1.0",
       "is_demo": "false",
       "substitute_used": false,
       "red_line_14_status": "EXHAUSTED"}'::jsonb)
ON CONFLICT (id) DO NOTHING;

-- ----------------------------------------------------------------------------
-- 3. 2 个真实 policy_measure (FK → 上 2 条真实 policy_document)
--    UUID prefix k31/k32 (≠ 651 j31/j32 ≠ 650 i31/i32 ≠ 649 h31/h32)
-- ----------------------------------------------------------------------------
INSERT INTO policy_measure (
    id, policy_document_id, measure_description, measure_type, lineage
) VALUES
    ('k3eebc99-9c0b-4ef8-bb6d-6bb9bd380k31',
     'k1eebc99-9c0b-4ef8-bb6d-6bb9bd380k11',
     'real-policy-measure-xinjiang-v9 (政策详情 v9 第 17 样本)', 'REGULATORY',
     '{"chain_id": "real_652_m4_15_policy_detail_v9",
       "source_file_sha256": "21c8211bf7bf8b41569174e5ae2ae127f8e11439a04a5501209a63506ddca472",
       "source_file_url": "https://www.xinjiang.gov.cn/",
       "extractor_version": "v1.0",
       "is_demo": "false",
       "substitute_used": false,
       "red_line_14_status": "EXHAUSTED"}'::jsonb),
    ('k3eebc99-9c0b-4ef8-bb6d-6bb9bd380k32',
     'k1eebc99-9c0b-4ef8-bb6d-6bb9bd380k12',
     'real-policy-measure-nei_menggu-v9 (政策详情 v9 第 18 样本)', 'REGULATORY',
     '{"chain_id": "real_652_m4_15_policy_detail_v9",
       "source_file_sha256": "da1d4104db87c47809ef40f12bd8847d98c432bf990b0d7056f0042e6fd0533b",
       "source_file_url": "https://www.nmg.gov.cn/zwgk/",
       "extractor_version": "v1.0",
       "is_demo": "false",
       "substitute_used": false,
       "red_line_14_status": "EXHAUSTED"}'::jsonb)
ON CONFLICT (id) DO NOTHING;

-- ----------------------------------------------------------------------------
-- 4. 2 个真实 government_commitment (FK → policy_target + 真实 geo_entity + source_document)
--    新疆 / 内蒙古 geo_entity_id: SELECT 子查询
--    proposer_person_id = NULL (避免 FK 到 639 person demo;保持 spike 自洽)
--    UUID prefix k41/k42 (≠ 651 j41/j42 ≠ 650 i41/i42 ≠ 649 h41/h42)
-- ----------------------------------------------------------------------------
INSERT INTO government_commitment (
    id, policy_target_id, commitment_text,
    proposer_person_id, geo_entity_id, commitment_date,
    due_date, status, source_id, lineage
)
SELECT
    'k4eebc99-9c0b-4ef8-bb6d-6bb9bd380k41',
    'k2eebc99-9c0b-4ef8-bb6d-6bb9bd380k21',
    'real-commitment-xinjiang-v9 (政策详情 v9 第 17 样本; 新疆维吾尔自治区政府)',
    NULL,
    g.id,
    '2026-09-02',
    '2026-12-31',
    'IN_PROGRESS',
    'k0eebc99-9c0b-4ef8-bb6d-6bb9bd380k04',
    jsonb_build_object(
        'chain_id', 'real_652_m4_15_policy_detail_v9',
        'source_file_sha256', '21c8211bf7bf8b41569174e5ae2ae127f8e11439a04a5501209a63506ddca472',
        'source_file_url', 'https://www.xinjiang.gov.cn/',
        'extractor_version', 'v1.0',
        'is_demo', 'false',
        'original_province', 'xinjiang',
        'actual_province', 'xinjiang',
        'substitute_used', false,
        'red_line_14_status', 'EXHAUSTED'
    )
FROM geo_entity g
WHERE g.canonical_name = '新疆维吾尔自治区' AND g.level = 'PROVINCIAL'
LIMIT 1
ON CONFLICT (id) DO NOTHING;

INSERT INTO government_commitment (
    id, policy_target_id, commitment_text,
    proposer_person_id, geo_entity_id, commitment_date,
    due_date, status, source_id, lineage
)
SELECT
    'k4eebc99-9c0b-4ef8-bb6d-6bb9bd380k42',
    'k2eebc99-9c0b-4ef8-bb6d-6bb9bd380k22',
    'real-commitment-nei_menggu-v9 (政策详情 v9 第 18 样本; 内蒙古自治区政府)',
    NULL,
    g.id,
    '2026-09-02',
    '2026-12-31',
    'IN_PROGRESS',
    'k0eebc99-9c0b-4ef8-bb6d-6bb9bd380k05',
    jsonb_build_object(
        'chain_id', 'real_652_m4_15_policy_detail_v9',
        'source_file_sha256', 'da1d4104db87c47809ef40f12bd8847d98c432bf990b0d7056f0042e6fd0533b',
        'source_file_url', 'https://www.nmg.gov.cn/zwgk/',
        'extractor_version', 'v1.0',
        'is_demo', 'false',
        'original_province', 'nei_menggu',
        'actual_province', 'nei_menggu',
        'substitute_used', false,
        'red_line_14_status', 'EXHAUSTED'
    )
FROM geo_entity g
WHERE g.canonical_name = '内蒙古自治区' AND g.level = 'PROVINCIAL'
LIMIT 1
ON CONFLICT (id) DO NOTHING;

-- ----------------------------------------------------------------------------
-- 5. 2 个真实 commitment_progress (FK → 上 2 条真实 government_commitment)
--    UUID prefix k51/k52 (≠ 651 j51/j52 ≠ 650 i51/i52 ≠ 649 h51/h52)
-- ----------------------------------------------------------------------------
INSERT INTO commitment_progress (
    id, government_commitment_id, progress_value, progress_unit,
    reported_date, reporting_org, lineage
) VALUES
    ('k5eebc99-9c0b-4ef8-bb6d-6bb9bd380k51',
     'k4eebc99-9c0b-4ef8-bb6d-6bb9bd380k41',
     0.5, 'PERCENT', '2026-09-02', '新疆维吾尔自治区人民政府',
     '{"chain_id": "real_652_m4_15_policy_detail_v9",
       "source_file_sha256": "21c8211bf7bf8b41569174e5ae2ae127f8e11439a04a5501209a63506ddca472",
       "source_file_url": "https://www.xinjiang.gov.cn/",
       "extractor_version": "v1.0",
       "is_demo": "false",
       "substitute_used": false,
       "red_line_14_status": "EXHAUSTED"}'::jsonb),
    ('k5eebc99-9c0b-4ef8-bb6d-6bb9bd380k52',
     'k4eebc99-9c0b-4ef8-bb6d-6bb9bd380k42',
     0.5, 'PERCENT', '2026-09-02', '内蒙古自治区人民政府',
     '{"chain_id": "real_652_m4_15_policy_detail_v9",
       "source_file_sha256": "da1d4104db87c47809ef40f12bd8847d98c432bf990b0d7056f0042e6fd0533b",
       "source_file_url": "https://www.nmg.gov.cn/zwgk/",
       "extractor_version": "v1.0",
       "is_demo": "false",
       "substitute_used": false,
       "red_line_14_status": "EXHAUSTED"}'::jsonb)
ON CONFLICT (id) DO NOTHING;

-- ----------------------------------------------------------------------------
-- 6. 2 个真实 project_event (FK → 真实 geo_entity via SELECT 子查询)
--    UUID prefix k61/k62 (≠ 651 j61/j62 ≠ 650 i61/i62 ≠ 649 h61/h62)
-- ----------------------------------------------------------------------------
INSERT INTO project_event (
    id, event_type, event_date, title, description,
    geo_entity_id, source_id, lineage
)
SELECT
    'k6eebc99-9c0b-4ef8-bb6d-6bb9bd380k61',
    'POLICY_DETAIL_RELEASE',
    '2026-09-02',
    'real-project-xinjiang-v9 (政策详情 v9 第 17 样本)',
    '新疆维吾尔自治区政府政策详情页落地; xinjiang /zwgk/ 403 WAF → fallback / 200 REACHABLE (全新 SHA 21c8211b...)',
    g.id,
    'k0eebc99-9c0b-4ef8-bb6d-6bb9bd380k04',
    jsonb_build_object(
        'chain_id', 'real_652_m4_15_policy_detail_v9',
        'source_file_sha256', '21c8211bf7bf8b41569174e5ae2ae127f8e11439a04a5501209a63506ddca472',
        'source_file_url', 'https://www.xinjiang.gov.cn/',
        'extractor_version', 'v1.0',
        'is_demo', 'false',
        'original_province', 'xinjiang',
        'actual_province', 'xinjiang',
        'substitute_used', false,
        'red_line_14_status', 'EXHAUSTED'
    )
FROM geo_entity g
WHERE g.canonical_name = '新疆维吾尔自治区' AND g.level = 'PROVINCIAL'
LIMIT 1
ON CONFLICT (id) DO NOTHING;

INSERT INTO project_event (
    id, event_type, event_date, title, description,
    geo_entity_id, source_id, lineage
)
SELECT
    'k6eebc99-9c0b-4ef8-bb6d-6bb9bd380k62',
    'POLICY_DETAIL_RELEASE',
    '2026-09-02',
    'real-project-nei_menggu-v9 (政策详情 v9 第 18 样本)',
    '内蒙古自治区政府政策详情页落地; nei_menggu /zwgk/ 200 REACHABLE (全新 SHA da1d4104...)',
    g.id,
    'k0eebc99-9c0b-4ef8-bb6d-6bb9bd380k05',
    jsonb_build_object(
        'chain_id', 'real_652_m4_15_policy_detail_v9',
        'source_file_sha256', 'da1d4104db87c47809ef40f12bd8847d98c432bf990b0d7056f0042e6fd0533b',
        'source_file_url', 'https://www.nmg.gov.cn/zwgk/',
        'extractor_version', 'v1.0',
        'is_demo', 'false',
        'original_province', 'nei_menggu',
        'actual_province', 'nei_menggu',
        'substitute_used', false,
        'red_line_14_status', 'EXHAUSTED'
    )
FROM geo_entity g
WHERE g.canonical_name = '内蒙古自治区' AND g.level = 'PROVINCIAL'
LIMIT 1
ON CONFLICT (id) DO NOTHING;

-- ----------------------------------------------------------------------------
-- End 652-A.1 seed SQL
-- 16 INSERT total = 12 政策表 + 2 source_registry + 2 source_document
-- chain_id=real_652_m4_15_policy_detail_v9
-- UUID k 段 (k02-k62) ≠ 651 j 段 ≠ 650 i 段 ≠ 649 h 段 ≠ 648 g 段 ≠ 647 f 段
-- 2 NEW SHA: 21c8211b (xinjiang fallback #1 REACHABLE) + da1d4104 (nei_menggu 首选 REACHABLE)
-- substitute_used_count = 0 (双样本均 REACHABLE; 递补池 [EXHAUSTED] per 红线 14 沿用 651)
-- blocked_no_pool_count = 0 (本次未触发 BLOCKED; 分支代码存在并可达, e2e 守门见 tests/test_m4_15_policy_detail_real_v9.py)
-- HTTP total = 3/12 (25% usage; xinjiang 2 + nei_menggu 1)
-- 代换行标注规范: 本次 2 样本均无 substitute, 行内字段以 actual_province 口径为准 (与 province 一致); 红线 13 增补条款 (per 649 P3-1) 同时落地: 若后续触发 substitute, source_registry province/source_name 一律用 actual_province, original_province 仅存 lineage JSONB
-- 红线 14 增补落地 (沿用 651): lineage JSONB 含 red_line_14_status='EXHAUSTED' + substitute_pool_note 显式登记递补池耗尽状态; 任一样本槽两级 fallback 全失败 → BLOCKED_NO_POOL 留痕, 不代换
-- 652 §0.14 强制 e2e 验证: BLOCKED_NO_POOL 分支代码存在并可达 (本次未触发, 但分支可触发)
-- ----------------------------------------------------------------------------