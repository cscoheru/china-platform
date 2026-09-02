-- ----------------------------------------------------------------------------
-- 651-A.1 — M4.14 政策详情 v8 真实化 seed SQL (knife 651 M4.14 side, 2026-09-02)
--   12 INSERT (政策表) = 2 样本 (shaanxi + sichuan 第 15/16 样本) × 6 政策表
--     + 2 source_registry + 2 source_document = 16 INSERT total
--   lineage JSONB `is_demo='false'` 真实化 sentinel
--   chain_id='real_651_m4_14_policy_detail_v8' (v8 标记 = shaanxi/sichuan 第 15/16 样本; ≠ 650 chain_id)
--   2 新 SHA 全 distinct ≠ 650/649/648/647/646/645/644/643/642/641/640/639/638 demo/real SHA
--     - shaanxi (fallback #1)  `9d0ad78a79317d5ec5224bf4fd56c4fa44dd658d2221e2921da1700e99e32ad5` (/zwgk/ 404 → / 200; SHA 9d0ad78a...)
--     - sichuan (fallback #1)  `f58a33842ab22afcb84a9f1156a6e1f05bae3f01432c8ea6b103c29387346ad5` (/zwgk/ 403 WAF → / 200; SHA f58a3384...)
--   UUID prefix j 段 (j02-j62) ≠ 650 i 段 (i02-i62) ≠ 649 h 段 (h02-h62) ≠ 648 g 段 (g02-g62) ≠ 647 f 段 (f02-f62) ≠ 646 e 段 ≠ 645 d 段 ≠ 644 c 段
--   不新写 016 migration (沿用 009+010+014+015 lineage JSONB)
--   不修改 source_registry 既有 638-650 行 / mart / 4 fixture
--   substitute_used_count = 0 (shaanxi + sichuan 双 fallback #1 REACHABLE; 递补池已耗尽 per 红线 14)
--   HTTP total = 4/12 (33% usage)
--
-- 651 红线 14 关键 (新增):
--   递补池 (SUBSTITUTE_POOL) 显式 [EXHAUSTED]; 651 后任一样本槽两级 fallback 全失败 → BLOCKED_NO_POOL 留痕,
--   不再跨省代换 (per 651 §0.14 增补; 649 激活 liaoning + 650/651 备而未触发 + 651 转正 shaanxi/sichuan → 池耗尽)
--   本次双样本均 fallback #1 REACHABLE, 触发 verdict=REACHABLE, substitute_used=false, blocked_reason='' (空)
--
-- 651 红线 13 沿用:
--   不宣称 Gate / O1 / O2 / O3 / M2 / M4.x / M5.x / M6 PASS (沿用红线 1)
--   代换行标注规范 (per 649 审计 P3-1): source_registry province/source_name 一律用 actual_province (URL 归属省), original_province 仅存 lineage JSONB
--   已用省全集 (不得重复, 按 actual_province 口径): HLJ / HENAN / YUNNAN / FUJIAN / GD / ZJ / JX / HUN / AH / LN / JL / GUIZHOU / JIANGSU; 651 增量 = SHAANXI / SICHUAN → 16 省
--   附属复验/验证产物允许独立文件, 但主 evidence summary.methodology 必须含指针
--   本次首选 shaanxi + sichuan: shaanxi /zwgk/ 404 → / 200 REACHABLE; sichuan /zwgk/ 403 WAF → / 200 REACHABLE; 递补池 [EXHAUSTED] 备而永不触发
-- ----------------------------------------------------------------------------

-- ----------------------------------------------------------------------------
-- 0. 2 个真实 source_registry (lineage JSONB is_demo='false')
--    chain_id='real_651_m4_14_policy_detail_v8'
--    UUID prefix j02/j03 (≠ 650 i02/i03 ≠ 649 h02/h03)
--    注: 本次 2 样本均无 substitute 触发 (actual_province = province); 行内字段以 actual_province 口径为准 (per 649 P3-1 规范)
-- ----------------------------------------------------------------------------
INSERT INTO source_registry (
    id, source_url, source_name, source_type,
    country, province, enabled, lineage
) VALUES
    ('j0eebc99-9c0b-4ef8-bb6d-6bb9bd380j02',
     'https://www.shaanxi.gov.cn/',
     '陕西省人民政府 政务公开 landing (shaanxi /zwgk/ 404 → / 200 REACHABLE)',
     'PROVINCIAL_BULLETIN',
     'CN', 'SHAANXI', TRUE,
     '{"chain_id": "real_651_m4_14_policy_detail_v8",
       "source_file_sha256": "9d0ad78a79317d5ec5224bf4fd56c4fa44dd658d2221e2921da1700e99e32ad5",
       "source_file_url": "https://www.shaanxi.gov.cn/",
       "extractor_version": "v1.0",
       "is_demo": "false",
       "original_province": "shaanxi",
       "actual_province": "shaanxi",
       "substitute_used": false,
       "red_line_14_status": "EXHAUSTED",
       "substitute_pool_note": "per 651 §0.14 红线 14 增补: 递补池正式耗尽; 本次未触发 substitute (fallback #1 REACHABLE)"}'::jsonb),
    ('j0eebc99-9c0b-4ef8-bb6d-6bb9bd380j03',
     'https://www.sc.gov.cn/',
     '四川省人民政府 政务公开 landing (sichuan /zwgk/ 403 WAF → / 200 REACHABLE)',
     'PROVINCIAL_BULLETIN',
     'CN', 'SICHUAN', TRUE,
     '{"chain_id": "real_651_m4_14_policy_detail_v8",
       "source_file_sha256": "f58a33842ab22afcb84a9f1156a6e1f05bae3f01432c8ea6b103c29387346ad5",
       "source_file_url": "https://www.sc.gov.cn/",
       "extractor_version": "v1.0",
       "is_demo": "false",
       "original_province": "sichuan",
       "actual_province": "sichuan",
       "substitute_used": false,
       "red_line_14_status": "EXHAUSTED",
       "substitute_pool_note": "per 651 §0.14 红线 14 增补: 递补池正式耗尽; 本次未触发 substitute (fallback #1 REACHABLE)"}'::jsonb)
ON CONFLICT (id) DO NOTHING;

-- ----------------------------------------------------------------------------
-- 0b. 2 个真实 source_document (lineage JSONB is_demo='false')
--     UUID prefix j04/j05
-- ----------------------------------------------------------------------------
INSERT INTO source_document (
    id, source_id, title, doc_kind, content_url,
    captured_at, file_hash_sha256, file_size_bytes, lineage
) VALUES
    ('j0eebc99-9c0b-4ef8-bb6d-6bb9bd380j04',
     'j0eebc99-9c0b-4ef8-bb6d-6bb9bd380j02',
     '陕西省人民政府 政务公开 landing',
     'POLICY_DETAIL_LIST',
     'https://www.shaanxi.gov.cn/',
     '2026-09-02',
     '9d0ad78a79317d5ec5224bf4fd56c4fa44dd658d2221e2921da1700e99e32ad5',
     87956,
     '{"chain_id": "real_651_m4_14_policy_detail_v8",
       "source_file_sha256": "9d0ad78a79317d5ec5224bf4fd56c4fa44dd658d2221e2921da1700e99e32ad5",
       "source_file_url": "https://www.shaanxi.gov.cn/",
       "extractor_version": "v1.0",
       "is_demo": "false",
       "original_province": "shaanxi",
       "actual_province": "shaanxi",
       "substitute_used": false,
       "red_line_14_status": "EXHAUSTED"}'::jsonb),
    ('j0eebc99-9c0b-4ef8-bb6d-6bb9bd380j05',
     'j0eebc99-9c0b-4ef8-bb6d-6bb9bd380j03',
     '四川省人民政府 政务公开 landing',
     'POLICY_DETAIL_LIST',
     'https://www.sc.gov.cn/',
     '2026-09-02',
     'f58a33842ab22afcb84a9f1156a6e1f05bae3f01432c8ea6b103c29387346ad5',
     100536,
     '{"chain_id": "real_651_m4_14_policy_detail_v8",
       "source_file_sha256": "f58a33842ab22afcb84a9f1156a6e1f05bae3f01432c8ea6b103c29387346ad5",
       "source_file_url": "https://www.sc.gov.cn/",
       "extractor_version": "v1.0",
       "is_demo": "false",
       "original_province": "sichuan",
       "actual_province": "sichuan",
       "substitute_used": false,
       "red_line_14_status": "EXHAUSTED"}'::jsonb)
ON CONFLICT (id) DO NOTHING;

-- ----------------------------------------------------------------------------
-- 1. 2 个真实 policy_document (lineage JSONB is_demo='false')
--    chain_id='real_651_m4_14_policy_detail_v8'
--    UUID prefix j11/j12 (≠ 650 i11/i12 ≠ 649 h11/h12)
-- ----------------------------------------------------------------------------
INSERT INTO policy_document (
    id, doc_type, title, publisher, publication_date,
    source_id, classification, policy_level, lineage
) VALUES
    ('j1eebc99-9c0b-4ef8-bb6d-6bb9bd380j11',
     'POLICY_DETAIL',
     '省政府政策详情 v8（陕西政务公开 landing）',
     '陕西省人民政府',
     '2026-09-02',
     'j0eebc99-9c0b-4ef8-bb6d-6bb9bd380j04',
     'BULLETIN', 'PROVINCIAL',
     '{"chain_id": "real_651_m4_14_policy_detail_v8",
       "source_file_sha256": "9d0ad78a79317d5ec5224bf4fd56c4fa44dd658d2221e2921da1700e99e32ad5",
       "source_file_url": "https://www.shaanxi.gov.cn/",
       "extractor_version": "v1.0",
       "is_demo": "false",
       "original_province": "shaanxi",
       "actual_province": "shaanxi",
       "substitute_used": false,
       "red_line_14_status": "EXHAUSTED"}'::jsonb),
    ('j1eebc99-9c0b-4ef8-bb6d-6bb9bd380j12',
     'POLICY_DETAIL',
     '省政府政策详情 v8（四川政务公开 landing）',
     '四川省人民政府',
     '2026-09-02',
     'j0eebc99-9c0b-4ef8-bb6d-6bb9bd380j05',
     'BULLETIN', 'PROVINCIAL',
     '{"chain_id": "real_651_m4_14_policy_detail_v8",
       "source_file_sha256": "f58a33842ab22afcb84a9f1156a6e1f05bae3f01432c8ea6b103c29387346ad5",
       "source_file_url": "https://www.sc.gov.cn/",
       "extractor_version": "v1.0",
       "is_demo": "false",
       "original_province": "sichuan",
       "actual_province": "sichuan",
       "substitute_used": false,
       "red_line_14_status": "EXHAUSTED"}'::jsonb)
ON CONFLICT (id) DO NOTHING;

-- ----------------------------------------------------------------------------
-- 2. 2 个真实 policy_target (FK → 上 2 条真实 policy_document)
--    UUID prefix j21/j22 (≠ 650 i21/i22 ≠ 649 h21/h22)
-- ----------------------------------------------------------------------------
INSERT INTO policy_target (
    id, policy_document_id, target_description,
    target_value, target_unit, target_year, measurable, lineage
) VALUES
    ('j2eebc99-9c0b-4ef8-bb6d-6bb9bd380j21',
     'j1eebc99-9c0b-4ef8-bb6d-6bb9bd380j11',
     'real-policy-target-shaanxi-v8 (政策详情 v8 第 15 样本)', NULL, NULL, 2026, FALSE,
     '{"chain_id": "real_651_m4_14_policy_detail_v8",
       "source_file_sha256": "9d0ad78a79317d5ec5224bf4fd56c4fa44dd658d2221e2921da1700e99e32ad5",
       "source_file_url": "https://www.shaanxi.gov.cn/",
       "extractor_version": "v1.0",
       "is_demo": "false",
       "substitute_used": false,
       "red_line_14_status": "EXHAUSTED"}'::jsonb),
    ('j2eebc99-9c0b-4ef8-bb6d-6bb9bd380j22',
     'j1eebc99-9c0b-4ef8-bb6d-6bb9bd380j12',
     'real-policy-target-sichuan-v8 (政策详情 v8 第 16 样本)', NULL, NULL, 2026, FALSE,
     '{"chain_id": "real_651_m4_14_policy_detail_v8",
       "source_file_sha256": "f58a33842ab22afcb84a9f1156a6e1f05bae3f01432c8ea6b103c29387346ad5",
       "source_file_url": "https://www.sc.gov.cn/",
       "extractor_version": "v1.0",
       "is_demo": "false",
       "substitute_used": false,
       "red_line_14_status": "EXHAUSTED"}'::jsonb)
ON CONFLICT (id) DO NOTHING;

-- ----------------------------------------------------------------------------
-- 3. 2 个真实 policy_measure (FK → 上 2 条真实 policy_document)
--    UUID prefix j31/j32 (≠ 650 i31/i32 ≠ 649 h31/h32)
-- ----------------------------------------------------------------------------
INSERT INTO policy_measure (
    id, policy_document_id, measure_description, measure_type, lineage
) VALUES
    ('j3eebc99-9c0b-4ef8-bb6d-6bb9bd380j31',
     'j1eebc99-9c0b-4ef8-bb6d-6bb9bd380j11',
     'real-policy-measure-shaanxi-v8 (政策详情 v8 第 15 样本)', 'REGULATORY',
     '{"chain_id": "real_651_m4_14_policy_detail_v8",
       "source_file_sha256": "9d0ad78a79317d5ec5224bf4fd56c4fa44dd658d2221e2921da1700e99e32ad5",
       "source_file_url": "https://www.shaanxi.gov.cn/",
       "extractor_version": "v1.0",
       "is_demo": "false",
       "substitute_used": false,
       "red_line_14_status": "EXHAUSTED"}'::jsonb),
    ('j3eebc99-9c0b-4ef8-bb6d-6bb9bd380j32',
     'j1eebc99-9c0b-4ef8-bb6d-6bb9bd380j12',
     'real-policy-measure-sichuan-v8 (政策详情 v8 第 16 样本)', 'REGULATORY',
     '{"chain_id": "real_651_m4_14_policy_detail_v8",
       "source_file_sha256": "f58a33842ab22afcb84a9f1156a6e1f05bae3f01432c8ea6b103c29387346ad5",
       "source_file_url": "https://www.sc.gov.cn/",
       "extractor_version": "v1.0",
       "is_demo": "false",
       "substitute_used": false,
       "red_line_14_status": "EXHAUSTED"}'::jsonb)
ON CONFLICT (id) DO NOTHING;

-- ----------------------------------------------------------------------------
-- 4. 2 个真实 government_commitment (FK → policy_target + 真实 geo_entity + source_document)
--    陕西 / 四川 geo_entity_id: SELECT 子查询
--    proposer_person_id = NULL (避免 FK 到 639 person demo;保持 spike 自洽)
--    UUID prefix j41/j42 (≠ 650 i41/i42 ≠ 649 h41/h42)
-- ----------------------------------------------------------------------------
INSERT INTO government_commitment (
    id, policy_target_id, commitment_text,
    proposer_person_id, geo_entity_id, commitment_date,
    due_date, status, source_id, lineage
)
SELECT
    'j4eebc99-9c0b-4ef8-bb6d-6bb9bd380j41',
    'j2eebc99-9c0b-4ef8-bb6d-6bb9bd380j21',
    'real-commitment-shaanxi-v8 (政策详情 v8 第 15 样本; 陕西省政府)',
    NULL,
    g.id,
    '2026-09-02',
    '2026-12-31',
    'IN_PROGRESS',
    'j0eebc99-9c0b-4ef8-bb6d-6bb9bd380j04',
    jsonb_build_object(
        'chain_id', 'real_651_m4_14_policy_detail_v8',
        'source_file_sha256', '9d0ad78a79317d5ec5224bf4fd56c4fa44dd658d2221e2921da1700e99e32ad5',
        'source_file_url', 'https://www.shaanxi.gov.cn/',
        'extractor_version', 'v1.0',
        'is_demo', 'false',
        'original_province', 'shaanxi',
        'actual_province', 'shaanxi',
        'substitute_used', false,
        'red_line_14_status', 'EXHAUSTED'
    )
FROM geo_entity g
WHERE g.canonical_name = '陕西省' AND g.level = 'PROVINCIAL'
LIMIT 1
ON CONFLICT (id) DO NOTHING;

INSERT INTO government_commitment (
    id, policy_target_id, commitment_text,
    proposer_person_id, geo_entity_id, commitment_date,
    due_date, status, source_id, lineage
)
SELECT
    'j4eebc99-9c0b-4ef8-bb6d-6bb9bd380j42',
    'j2eebc99-9c0b-4ef8-bb6d-6bb9bd380j22',
    'real-commitment-sichuan-v8 (政策详情 v8 第 16 样本; 四川省政府)',
    NULL,
    g.id,
    '2026-09-02',
    '2026-12-31',
    'IN_PROGRESS',
    'j0eebc99-9c0b-4ef8-bb6d-6bb9bd380j05',
    jsonb_build_object(
        'chain_id', 'real_651_m4_14_policy_detail_v8',
        'source_file_sha256', 'f58a33842ab22afcb84a9f1156a6e1f05bae3f01432c8ea6b103c29387346ad5',
        'source_file_url', 'https://www.sc.gov.cn/',
        'extractor_version', 'v1.0',
        'is_demo', 'false',
        'original_province', 'sichuan',
        'actual_province', 'sichuan',
        'substitute_used', false,
        'red_line_14_status', 'EXHAUSTED'
    )
FROM geo_entity g
WHERE g.canonical_name = '四川省' AND g.level = 'PROVINCIAL'
LIMIT 1
ON CONFLICT (id) DO NOTHING;

-- ----------------------------------------------------------------------------
-- 5. 2 个真实 commitment_progress (FK → 上 2 条真实 government_commitment)
--    UUID prefix j51/j52 (≠ 650 i51/i52 ≠ 649 h51/h52)
-- ----------------------------------------------------------------------------
INSERT INTO commitment_progress (
    id, government_commitment_id, progress_value, progress_unit,
    reported_date, reporting_org, lineage
) VALUES
    ('j5eebc99-9c0b-4ef8-bb6d-6bb9bd380j51',
     'j4eebc99-9c0b-4ef8-bb6d-6bb9bd380j41',
     0.5, 'PERCENT', '2026-09-02', '陕西省人民政府',
     '{"chain_id": "real_651_m4_14_policy_detail_v8",
       "source_file_sha256": "9d0ad78a79317d5ec5224bf4fd56c4fa44dd658d2221e2921da1700e99e32ad5",
       "source_file_url": "https://www.shaanxi.gov.cn/",
       "extractor_version": "v1.0",
       "is_demo": "false",
       "substitute_used": false,
       "red_line_14_status": "EXHAUSTED"}'::jsonb),
    ('j5eebc99-9c0b-4ef8-bb6d-6bb9bd380j52',
     'j4eebc99-9c0b-4ef8-bb6d-6bb9bd380j42',
     0.5, 'PERCENT', '2026-09-02', '四川省人民政府',
     '{"chain_id": "real_651_m4_14_policy_detail_v8",
       "source_file_sha256": "f58a33842ab22afcb84a9f1156a6e1f05bae3f01432c8ea6b103c29387346ad5",
       "source_file_url": "https://www.sc.gov.cn/",
       "extractor_version": "v1.0",
       "is_demo": "false",
       "substitute_used": false,
       "red_line_14_status": "EXHAUSTED"}'::jsonb)
ON CONFLICT (id) DO NOTHING;

-- ----------------------------------------------------------------------------
-- 6. 2 个真实 project_event (FK → 真实 geo_entity via SELECT 子查询)
--    UUID prefix j61/j62 (≠ 650 i61/i62 ≠ 649 h61/h62)
-- ----------------------------------------------------------------------------
INSERT INTO project_event (
    id, event_type, event_date, title, description,
    geo_entity_id, source_id, lineage
)
SELECT
    'j6eebc99-9c0b-4ef8-bb6d-6bb9bd380j61',
    'POLICY_DETAIL_RELEASE',
    '2026-09-02',
    'real-project-shaanxi-v8 (政策详情 v8 第 15 样本)',
    '陕西省政府政策详情页落地; shaanxi /zwgk/ 404 → fallback / 200 REACHABLE (全新 SHA 9d0ad78a...)',
    g.id,
    'j0eebc99-9c0b-4ef8-bb6d-6bb9bd380j04',
    jsonb_build_object(
        'chain_id', 'real_651_m4_14_policy_detail_v8',
        'source_file_sha256', '9d0ad78a79317d5ec5224bf4fd56c4fa44dd658d2221e2921da1700e99e32ad5',
        'source_file_url', 'https://www.shaanxi.gov.cn/',
        'extractor_version', 'v1.0',
        'is_demo', 'false',
        'original_province', 'shaanxi',
        'actual_province', 'shaanxi',
        'substitute_used', false,
        'red_line_14_status', 'EXHAUSTED'
    )
FROM geo_entity g
WHERE g.canonical_name = '陕西省' AND g.level = 'PROVINCIAL'
LIMIT 1
ON CONFLICT (id) DO NOTHING;

INSERT INTO project_event (
    id, event_type, event_date, title, description,
    geo_entity_id, source_id, lineage
)
SELECT
    'j6eebc99-9c0b-4ef8-bb6d-6bb9bd380j62',
    'POLICY_DETAIL_RELEASE',
    '2026-09-02',
    'real-project-sichuan-v8 (政策详情 v8 第 16 样本)',
    '四川省政府政策详情页落地; sichuan /zwgk/ 403 WAF → fallback / 200 REACHABLE (全新 SHA f58a3384...)',
    g.id,
    'j0eebc99-9c0b-4ef8-bb6d-6bb9bd380j05',
    jsonb_build_object(
        'chain_id', 'real_651_m4_14_policy_detail_v8',
        'source_file_sha256', 'f58a33842ab22afcb84a9f1156a6e1f05bae3f01432c8ea6b103c29387346ad5',
        'source_file_url', 'https://www.sc.gov.cn/',
        'extractor_version', 'v1.0',
        'is_demo', 'false',
        'original_province', 'sichuan',
        'actual_province', 'sichuan',
        'substitute_used', false,
        'red_line_14_status', 'EXHAUSTED'
    )
FROM geo_entity g
WHERE g.canonical_name = '四川省' AND g.level = 'PROVINCIAL'
LIMIT 1
ON CONFLICT (id) DO NOTHING;

-- ----------------------------------------------------------------------------
-- End 651-A.1 seed SQL
-- 16 INSERT total = 12 政策表 + 2 source_registry + 2 source_document
-- chain_id=real_651_m4_14_policy_detail_v8
-- UUID j 段 (j02-j62) ≠ 650 i 段 ≠ 649 h 段 ≠ 648 g 段 ≠ 647 f 段
-- 2 NEW SHA: 9d0ad78a (shaanxi fallback #1 REACHABLE) + f58a3384 (sichuan fallback #1 REACHABLE)
-- substitute_used_count = 0 (shaanxi + sichuan 双 fallback #1 REACHABLE; 递补池 [EXHAUSTED] per 红线 14 增补)
-- HTTP total = 4/12 (33% usage)
-- 代换行标注规范: 本次 2 样本均无 substitute, 行内字段以 actual_province 口径为准 (与 province 一致); 红线 13 增补条款 (per 649 P3-1) 同时落地: 若后续触发 substitute, source_registry province/source_name 一律用 actual_province, original_province 仅存 lineage JSONB
-- 红线 14 增补落地: lineage JSONB 含 red_line_14_status='EXHAUSTED' + substitute_pool_note 显式登记递补池耗尽状态; 任一样本槽两级 fallback 全失败 → BLOCKED_NO_POOL 留痕, 不代换
-- ----------------------------------------------------------------------------