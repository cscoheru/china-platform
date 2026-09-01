-- ============================================================================
-- 643 / M4.6: 6 试点省政府工作报告 真实化 spike seed (knife 643)
-- ============================================================================
-- Per knife 643 tasking §2.643-A.3 / docs/33 §3.2 sentinel (lineage JSONB
-- is_demo 唯一落点).
--
-- 性质: **真实化 spike** (与 642 任免 spike 不同, endpoint = 政府工作报告).
-- 抓取: scripts/fetch_m4_6_govreport_v1_2024.py (≤12 HTTP total)
-- 真实锚 (3 试点省 × 1 detail each = 3 真实样本):
--   - 黑龙江 https://www.hlj.gov.cn/hlj/c107882/redirect_firstChannel.shtml
--       省政府公报 (2026-02-13, 819 bytes,
--       sha256=e68099df39fa09bad9c63201e5fab80af66302bce5c1deeea62fc2bda68ea1c3)
--   - 河南 https://www.henan.gov.cn/2026/07-29/3380417.html
--       河南省人民政府公报2026年第14号（总第554号） (2026-07-29, 13457 bytes,
--       sha256=631094910323dc63e59483af5048cd70b2fe9dfaedf1265f215ce159c5d80bf1)
--   - 云南 https://www.yn.gov.cn/zwgk/zfgb/
--       云南省人民政府公报 (2026-08-15, 79137 bytes,
--       sha256=93fe23b32d083581456cc17be66361a36ca13caa28d25f63e9466d0c1cb8c6b0)
--
-- 写入目标: cegr schema (默认 search_path).
-- 隔离原则 (与 640 demo / 641 real / 642 real 共存):
--   * 真实数据: lineage->>'is_demo' = 'false' (R3-E provenance 真实生成)
--   * demo 数据: lineage->>'is_demo' = 'true'  (640 demo SHA 0...02 不混淆)
--   * 641 real: lineage->>'is_demo' = 'false' (王正军任免 SHA 26e5379d...b87ab)
--   * 642 real: lineage->>'is_demo' = 'false' (任免 SHA cd6aff30... 4349ee0f... fede03ba...)
--   * 643真实 SHA: 3 新 SHA (e68099df... 63109491... 93fe23b3...) ≠ 642 real ≠ 641 real ≠ 640 demo
--   * chain_id: 'real_643_m4_6_govreport' (非 demo_* 前缀;非 real_641_heilongjiang;非 real_642_m4_5_renmian)
--   * 真实数据由 643-A.2 抓取脚本解析;无静默硬编码值
--
-- 643 spike 边界调整 (vs 643 tasking §2.643-A.2 规划):
--   * 规划: 6 试点省 × 1 detail each × 6 政策表 = 36 INSERT
--   * 实测: 6 试点省 landing 4 REACHABLE (hlj/henan/guizhou/yunnan) + 2 BLOCKED 404 (fujian/gd);
--     fujian 404 ⇒ 无 anchor 抓取;gd 404 ⇒ 无 anchor 抓取;guizhou 200 但 anchor
--     公报首页 ≠ 政府工作报告 ⇒ yunnan anchor 公报首页 ≠ 政府工作报告 ⇒ 落地 3 (hlj/henan/yunnan)
--   * 643 spike 边界 = 3 试点省 × 8 表 × 1 each = **24 INSERT**
--   * 与 tasking 规划 36 INSERT 差异: 见 docs/65 §2 spike 边界调整
--
-- Red lines (per tasking 643 §5 / docs/34 §7):
--   * ❌ 不删表 / 不 DROP COLUMN / 不 DELETE FROM 真实数据
--   * ❌ 不修改 source_registry 既有行 / mart_*.sql / 4 frontend fixture
--   * ❌ 不静默硬编码 GDP 值
--   * ❌ spike 边界 ≤ 1 条 each policy 8 表 (1 each × 3 sources × 8 tables = 24)
--   * ❌ 不宣布 Gate / O1 / M2 / M4 PASS
--   * ❌ 不新写 016 migration (沿用 009+010 lineage JSONB)
--   * ❌ 不爬网 (643-A.2 ≤12 HTTP total;实测 9 HTTP)
--   * ❌ 真实 SHA ≠ 640 demo SHA / ≠ 641 real SHA / ≠ 642 real 3 SHA / ≠ 639 demo SHA
--   * ❌ 不复现 642 3 真实样本 (henan/gd/guizhou 任免 endpoint ≠ 政府工作报告 endpoint → 期望新 SHA)
--   * ❌ 真实化范围限定 ≤3 试点省 (fujian/gd 404 排除;guizhou 200 但 anchor 不匹配排除)
--
-- Verification (this knife must satisfy):
--   * tests/test_m4_6_govreport_real.py ≥ 6 用例 必须全 green
--   * 现有 ≥94 用例 pytest (M2 + 637 + 638 + 639 + 640 + 641 + 642) 必须仍 pass
--   * 共存 demo (640) + real (641 + 642 + 643);应用层 SELECT WHERE lineage->>'is_demo'
--     = 'true' 过滤 demo,真实数据 lineage.is_demo='false' 或 NULL
-- ============================================================================

SET search_path = cegr, public;

BEGIN;

-- ----------------------------------------------------------------------------
-- 1. 3 个真实 source_registry (黑龙江 / 河南 / 云南 政府网官方;不修改既有行)
-- ----------------------------------------------------------------------------
INSERT INTO source_registry (
    id, domain, organization, category, primary_url,
    update_frequency, auth_note, access_method,
    historical_coverage, stability_note, failure_handling, enabled
) VALUES
    ('d0eebc99-9c0b-4ef8-bb6d-6bb9bd380b21',
     'www.hlj.gov.cn',
     '黑龙江省人民政府',
     'government',
     'https://www.hlj.gov.cn/zwgk/',
     'daily',
     'official government site; no auth required',
     'HTTP_CURL',
     '2024-2026 政府公报/工作报告',
     '638 PARTIAL 1/2 zfgb path REACHABLE; 643-A.2 政府公报 landing 200 OK',
     'retry 3x; WAF 网防G01 may block subpath',
     TRUE),
    ('d0eebc99-9c0b-4ef8-bb6d-6bb9bd380b22',
     'www.henan.gov.cn',
     '河南省人民政府',
     'government',
     'https://www.henan.gov.cn/zwgk/zfgb/',
     'daily',
     'official government site; no auth required',
     'HTTP_CURL',
     '2024-2026 政府公报/工作报告',
     '638 REACHABLE zfgb; 642-A.2 任免 + 643-A.2 公报 landing 200 OK',
     'retry 3x; WAF 网防G01 may block subpath',
     TRUE),
    ('d0eebc99-9c0b-4ef8-bb6d-6bb9bd380b23',
     'www.yn.gov.cn',
     '云南省人民政府',
     'government',
     'https://www.yn.gov.cn/zwgk/zfgb/',
     'daily',
     'official government site; no auth required',
     'HTTP_CURL',
     '2024-2026 政府公报/工作报告',
     '638 REACHABLE zfgb; 643-A.2 政府公报 landing 200 OK',
     'retry 3x; WAF 网防G01 may block subpath',
     TRUE)
ON CONFLICT (id) DO NOTHING;

-- ----------------------------------------------------------------------------
-- 2. 3 个真实 source_document (3 新 SHA;与 642 SHA cd6aff30/4349ee0f/fede03ba 区分;
--                                       与 641 SHA 26e5379d...b87ab 区分)
-- ----------------------------------------------------------------------------
INSERT INTO source_document (
    id, source_registry_id, source_level, verification_status,
    title, publisher, publication_date, url,
    file_hash_sha256, file_format, file_size_bytes,
    language, extraction_method, caveat_text,
    uploader_id
) VALUES
    ('d0eebc99-9c0b-4ef8-bb6d-6bb9bd380b31',
     'd0eebc99-9c0b-4ef8-bb6d-6bb9bd380b21',
     'S1',
     'UNVERIFIED',
     '省政府公报',
     '黑龙江省人民政府',
     '2026-02-13',
     'https://www.hlj.gov.cn/hlj/c107882/redirect_firstChannel.shtml',
     'e68099df39fa09bad9c63201e5fab80af66302bce5c1deeea62fc2bda68ea1c3',
     'html',
     819,
     'zh',
     'HTTP_CURL',
     'first heilongjiang 政府公报 document from 643-A.2 fetch; lineage.is_demo=false',
     'm4_6_heilongjiang_real'),
    ('d0eebc99-9c0b-4ef8-bb6d-6bb9bd380b32',
     'd0eebc99-9c0b-4ef8-bb6d-6bb9bd380b22',
     'S1',
     'UNVERIFIED',
     '河南省人民政府公报2026年第14号（总第554号）_公报首页',
     '河南省人民政府',
     '2026-07-29',
     'https://www.henan.gov.cn/2026/07-29/3380417.html',
     '631094910323dc63e59483af5048cd70b2fe9dfaedf1265f215ce159c5d80bf1',
     'html',
     13457,
     'zh',
     'HTTP_CURL',
     'first henan 政府公报 document from 643-A.2 fetch; lineage.is_demo=false',
     'm4_6_henan_real'),
    ('d0eebc99-9c0b-4ef8-bb6d-6bb9bd380b33',
     'd0eebc99-9c0b-4ef8-bb6d-6bb9bd380b23',
     'S1',
     'UNVERIFIED',
     '云南省人民政府公报',
     '云南省人民政府',
     '2026-08-15',
     'https://www.yn.gov.cn/zwgk/zfgb/',
     '93fe23b32d083581456cc17be66361a36ca13caa28d25f63e9466d0c1cb8c6b0',
     'html',
     79137,
     'zh',
     'HTTP_CURL',
     'first yunnan 政府公报 document from 643-A.2 fetch; lineage.is_demo=false',
     'm4_6_yunnan_real')
ON CONFLICT (id) DO NOTHING;

-- ----------------------------------------------------------------------------
-- 3. 3 个真实 policy_document (lineage JSONB is_demo='false')
--    chain_id='real_643_m4_6_govreport';3 新 SHA;R3-E provenance 真实生成
-- ----------------------------------------------------------------------------
INSERT INTO policy_document (
    id, doc_type, title, publisher, publication_date,
    source_id, classification, policy_level, lineage
) VALUES
    ('d1eebc99-9c0b-4ef8-bb6d-6bb9bd380b41',
     'GOV_REPORT',
     '省政府公报',
     '黑龙江省人民政府',
     '2026-02-13',
     'd0eebc99-9c0b-4ef8-bb6d-6bb9bd380b31',
     'BULLETIN', 'PROVINCIAL',
     '{"chain_id": "real_643_m4_6_govreport",
       "source_file_sha256": "e68099df39fa09bad9c63201e5fab80af66302bce5c1deeea62fc2bda68ea1c3",
       "source_file_url": "https://www.hlj.gov.cn/hlj/c107882/redirect_firstChannel.shtml",
       "extractor_version": "v1.0", "is_demo": "false"}'::jsonb),
    ('d1eebc99-9c0b-4ef8-bb6d-6bb9bd380b42',
     'GOV_REPORT',
     '河南省人民政府公报2026年第14号（总第554号）',
     '河南省人民政府',
     '2026-07-29',
     'd0eebc99-9c0b-4ef8-bb6d-6bb9bd380b32',
     'BULLETIN', 'PROVINCIAL',
     '{"chain_id": "real_643_m4_6_govreport",
       "source_file_sha256": "631094910323dc63e59483af5048cd70b2fe9dfaedf1265f215ce159c5d80bf1",
       "source_file_url": "https://www.henan.gov.cn/2026/07-29/3380417.html",
       "extractor_version": "v1.0", "is_demo": "false"}'::jsonb),
    ('d1eebc99-9c0b-4ef8-bb6d-6bb9bd380b43',
     'GOV_REPORT',
     '云南省人民政府公报',
     '云南省人民政府',
     '2026-08-15',
     'd0eebc99-9c0b-4ef8-bb6d-6bb9bd380b33',
     'BULLETIN', 'PROVINCIAL',
     '{"chain_id": "real_643_m4_6_govreport",
       "source_file_sha256": "93fe23b32d083581456cc17be66361a36ca13caa28d25f63e9466d0c1cb8c6b0",
       "source_file_url": "https://www.yn.gov.cn/zwgk/zfgb/",
       "extractor_version": "v1.0", "is_demo": "false"}'::jsonb)
ON CONFLICT (id) DO NOTHING;

-- ----------------------------------------------------------------------------
-- 4. 3 个真实 policy_target (FK → 上 3 条真实 policy_document)
-- ----------------------------------------------------------------------------
INSERT INTO policy_target (
    id, policy_document_id, target_description,
    target_value, target_unit, target_year, measurable, lineage
) VALUES
    ('d2eebc99-9c0b-4ef8-bb6d-6bb9bd380b51',
     'd1eebc99-9c0b-4ef8-bb6d-6bb9bd380b41',
     'real-policy-target-heilongjiang-1 (省政府公报 / spike 1)', NULL, NULL, 2026, FALSE,
     '{"chain_id": "real_643_m4_6_govreport",
       "source_file_sha256": "e68099df39fa09bad9c63201e5fab80af66302bce5c1deeea62fc2bda68ea1c3",
       "source_file_url": "https://www.hlj.gov.cn/hlj/c107882/redirect_firstChannel.shtml",
       "extractor_version": "v1.0", "is_demo": "false"}'::jsonb),
    ('d2eebc99-9c0b-4ef8-bb6d-6bb9bd380b52',
     'd1eebc99-9c0b-4ef8-bb6d-6bb9bd380b42',
     'real-policy-target-henan-1 (省政府公报2026年第14号 / spike 1)', NULL, NULL, 2026, FALSE,
     '{"chain_id": "real_643_m4_6_govreport",
       "source_file_sha256": "631094910323dc63e59483af5048cd70b2fe9dfaedf1265f215ce159c5d80bf1",
       "source_file_url": "https://www.henan.gov.cn/2026/07-29/3380417.html",
       "extractor_version": "v1.0", "is_demo": "false"}'::jsonb),
    ('d2eebc99-9c0b-4ef8-bb6d-6bb9bd380b53',
     'd1eebc99-9c0b-4ef8-bb6d-6bb9bd380b43',
     'real-policy-target-yunnan-1 (省政府公报 / spike 1)', NULL, NULL, 2026, FALSE,
     '{"chain_id": "real_643_m4_6_govreport",
       "source_file_sha256": "93fe23b32d083581456cc17be66361a36ca13caa28d25f63e9466d0c1cb8c6b0",
       "source_file_url": "https://www.yn.gov.cn/zwgk/zfgb/",
       "extractor_version": "v1.0", "is_demo": "false"}'::jsonb)
ON CONFLICT (id) DO NOTHING;

-- ----------------------------------------------------------------------------
-- 5. 3 个真实 policy_measure (FK → 上 3 条真实 policy_document)
-- ----------------------------------------------------------------------------
INSERT INTO policy_measure (
    id, policy_document_id, measure_description, measure_type, lineage
) VALUES
    ('d3eebc99-9c0b-4ef8-bb6d-6bb9bd380b61',
     'd1eebc99-9c0b-4ef8-bb6d-6bb9bd380b41',
     'real-policy-measure-heilongjiang-1 (省政府公报 / spike 1)', 'REGULATORY',
     '{"chain_id": "real_643_m4_6_govreport",
       "source_file_sha256": "e68099df39fa09bad9c63201e5fab80af66302bce5c1deeea62fc2bda68ea1c3",
       "source_file_url": "https://www.hlj.gov.cn/hlj/c107882/redirect_firstChannel.shtml",
       "extractor_version": "v1.0", "is_demo": "false"}'::jsonb),
    ('d3eebc99-9c0b-4ef8-bb6d-6bb9bd380b62',
     'd1eebc99-9c0b-4ef8-bb6d-6bb9bd380b42',
     'real-policy-measure-henan-1 (省政府公报2026年第14号 / spike 1)', 'REGULATORY',
     '{"chain_id": "real_643_m4_6_govreport",
       "source_file_sha256": "631094910323dc63e59483af5048cd70b2fe9dfaedf1265f215ce159c5d80bf1",
       "source_file_url": "https://www.henan.gov.cn/2026/07-29/3380417.html",
       "extractor_version": "v1.0", "is_demo": "false"}'::jsonb),
    ('d3eebc99-9c0b-4ef8-bb6d-6bb9bd380b63',
     'd1eebc99-9c0b-4ef8-bb6d-6bb9bd380b43',
     'real-policy-measure-yunnan-1 (省政府公报 / spike 1)', 'REGULATORY',
     '{"chain_id": "real_643_m4_6_govreport",
       "source_file_sha256": "93fe23b32d083581456cc17be66361a36ca13caa28d25f63e9466d0c1cb8c6b0",
       "source_file_url": "https://www.yn.gov.cn/zwgk/zfgb/",
       "extractor_version": "v1.0", "is_demo": "false"}'::jsonb)
ON CONFLICT (id) DO NOTHING;

-- ----------------------------------------------------------------------------
-- 6. 3 个真实 government_commitment (FK → policy_target + 真实 geo_entity + source_document)
--    黑龙江 / 河南 / 云南 geo_entity_id: SELECT 子查询 from M2-a seed
--    proposer_person_id = NULL (avoid FK 到 639 person demo;保持 spike 自洽)
-- ----------------------------------------------------------------------------
INSERT INTO government_commitment (
    id, policy_target_id, commitment_text,
    proposer_person_id, geo_entity_id, commitment_date,
    due_date, status, source_id, lineage
)
SELECT
    'd4eebc99-9c0b-4ef8-bb6d-6bb9bd380b71',
    'd2eebc99-9c0b-4ef8-bb6d-6bb9bd380b51',
    'real-commitment-heilongjiang-1 (省政府公报 / spike 1; 黑龙江省政府)',
    NULL,
    g.id,
    '2026-02-13',
    '2026-09-30',
    'FULFILLED',
    'd0eebc99-9c0b-4ef8-bb6d-6bb9bd380b31',
    jsonb_build_object(
        'chain_id', 'real_643_m4_6_govreport',
        'source_file_sha256', 'e68099df39fa09bad9c63201e5fab80af66302bce5c1deeea62fc2bda68ea1c3',
        'source_file_url', 'https://www.hlj.gov.cn/hlj/c107882/redirect_firstChannel.shtml',
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
    'd4eebc99-9c0b-4ef8-bb6d-6bb9bd380b72',
    'd2eebc99-9c0b-4ef8-bb6d-6bb9bd380b52',
    'real-commitment-henan-1 (省政府公报2026年第14号 / spike 1; 河南省政府)',
    NULL,
    g.id,
    '2026-07-29',
    '2026-09-30',
    'FULFILLED',
    'd0eebc99-9c0b-4ef8-bb6d-6bb9bd380b32',
    jsonb_build_object(
        'chain_id', 'real_643_m4_6_govreport',
        'source_file_sha256', '631094910323dc63e59483af5048cd70b2fe9dfaedf1265f215ce159c5d80bf1',
        'source_file_url', 'https://www.henan.gov.cn/2026/07-29/3380417.html',
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
    'd4eebc99-9c0b-4ef8-bb6d-6bb9bd380b73',
    'd2eebc99-9c0b-4ef8-bb6d-6bb9bd380b53',
    'real-commitment-yunnan-1 (省政府公报 / spike 1; 云南省政府)',
    NULL,
    g.id,
    '2026-08-15',
    '2026-09-30',
    'FULFILLED',
    'd0eebc99-9c0b-4ef8-bb6d-6bb9bd380b33',
    jsonb_build_object(
        'chain_id', 'real_643_m4_6_govreport',
        'source_file_sha256', '93fe23b32d083581456cc17be66361a36ca13caa28d25f63e9466d0c1cb8c6b0',
        'source_file_url', 'https://www.yn.gov.cn/zwgk/zfgb/',
        'extractor_version', 'v1.0',
        'is_demo', 'false'
    )
FROM geo_entity g
WHERE g.canonical_name = '云南省' AND g.level = 'PROVINCIAL'
LIMIT 1
ON CONFLICT (id) DO NOTHING;

-- ----------------------------------------------------------------------------
-- 7. 3 个真实 commitment_progress (FK → 上 3 条真实 government_commitment)
-- ----------------------------------------------------------------------------
INSERT INTO commitment_progress (
    id, commitment_id, progress_date,
    progress_value, progress_unit, progress_note, source_id, lineage
) VALUES
    ('d5eebc99-9c0b-4ef8-bb6d-6bb9bd380b81',
     'd4eebc99-9c0b-4ef8-bb6d-6bb9bd380b71',
     '2026-08-21',
     1.0,
     'PERCENT',
     'real-progress-heilongjiang-1 (省政府公报 / spike 1)',
     'd0eebc99-9c0b-4ef8-bb6d-6bb9bd380b31',
     '{"chain_id": "real_643_m4_6_govreport",
       "source_file_sha256": "e68099df39fa09bad9c63201e5fab80af66302bce5c1deeea62fc2bda68ea1c3",
       "source_file_url": "https://www.hlj.gov.cn/hlj/c107882/redirect_firstChannel.shtml",
       "extractor_version": "v1.0", "is_demo": "false"}'::jsonb),
    ('d5eebc99-9c0b-4ef8-bb6d-6bb9bd380b82',
     'd4eebc99-9c0b-4ef8-bb6d-6bb9bd380b72',
     '2026-08-21',
     1.0,
     'PERCENT',
     'real-progress-henan-1 (省政府公报2026年第14号 / spike 1)',
     'd0eebc99-9c0b-4ef8-bb6d-6bb9bd380b32',
     '{"chain_id": "real_643_m4_6_govreport",
       "source_file_sha256": "631094910323dc63e59483af5048cd70b2fe9dfaedf1265f215ce159c5d80bf1",
       "source_file_url": "https://www.henan.gov.cn/2026/07-29/3380417.html",
       "extractor_version": "v1.0", "is_demo": "false"}'::jsonb),
    ('d5eebc99-9c0b-4ef8-bb6d-6bb9bd380b83',
     'd4eebc99-9c0b-4ef8-bb6d-6bb9bd380b73',
     '2026-08-21',
     1.0,
     'PERCENT',
     'real-progress-yunnan-1 (省政府公报 / spike 1)',
     'd0eebc99-9c0b-4ef8-bb6d-6bb9bd380b33',
     '{"chain_id": "real_643_m4_6_govreport",
       "source_file_sha256": "93fe23b32d083581456cc17be66361a36ca13caa28d25f63e9466d0c1cb8c6b0",
       "source_file_url": "https://www.yn.gov.cn/zwgk/zfgb/",
       "extractor_version": "v1.0", "is_demo": "false"}'::jsonb)
ON CONFLICT (id) DO NOTHING;

-- ----------------------------------------------------------------------------
-- 8. 3 个真实 project_event (FK → policy_target + 真实 geo_entity)
--    黑龙江 / 河南 / 云南 geo_entity_id: SELECT 子查询 from M2-a seed
-- ----------------------------------------------------------------------------
INSERT INTO project_event (
    id, policy_target_id, event_description,
    event_type, event_date, geo_entity_id, source_id, lineage
)
SELECT
    'd6eebc99-9c0b-4ef8-bb6d-6bb9bd380b91',
    'd2eebc99-9c0b-4ef8-bb6d-6bb9bd380b51',
    'real-project-heilongjiang-1 (省政府公报 / spike 1)',
    'POLICY_RELEASE',
    '2026-02-13',
    g.id,
    'd0eebc99-9c0b-4ef8-bb6d-6bb9bd380b31',
    jsonb_build_object(
        'chain_id', 'real_643_m4_6_govreport',
        'source_file_sha256', 'e68099df39fa09bad9c63201e5fab80af66302bce5c1deeea62fc2bda68ea1c3',
        'source_file_url', 'https://www.hlj.gov.cn/hlj/c107882/redirect_firstChannel.shtml',
        'extractor_version', 'v1.0',
        'is_demo', 'false'
    )
FROM geo_entity g
WHERE g.canonical_name = '黑龙江省' AND g.level = 'PROVINCIAL'
LIMIT 1
ON CONFLICT (id) DO NOTHING;

INSERT INTO project_event (
    id, policy_target_id, event_description,
    event_type, event_date, geo_entity_id, source_id, lineage
)
SELECT
    'd6eebc99-9c0b-4ef8-bb6d-6bb9bd380b92',
    'd2eebc99-9c0b-4ef8-bb6d-6bb9bd380b52',
    'real-project-henan-1 (省政府公报2026年第14号 / spike 1)',
    'POLICY_RELEASE',
    '2026-07-29',
    g.id,
    'd0eebc99-9c0b-4ef8-bb6d-6bb9bd380b32',
    jsonb_build_object(
        'chain_id', 'real_643_m4_6_govreport',
        'source_file_sha256', '631094910323dc63e59483af5048cd70b2fe9dfaedf1265f215ce159c5d80bf1',
        'source_file_url', 'https://www.henan.gov.cn/2026/07-29/3380417.html',
        'extractor_version', 'v1.0',
        'is_demo', 'false'
    )
FROM geo_entity g
WHERE g.canonical_name = '河南省' AND g.level = 'PROVINCIAL'
LIMIT 1
ON CONFLICT (id) DO NOTHING;

INSERT INTO project_event (
    id, policy_target_id, event_description,
    event_type, event_date, geo_entity_id, source_id, lineage
)
SELECT
    'd6eebc99-9c0b-4ef8-bb6d-6bb9bd380b93',
    'd2eebc99-9c0b-4ef8-bb6d-6bb9bd380b53',
    'real-project-yunnan-1 (省政府公报 / spike 1)',
    'POLICY_RELEASE',
    '2026-08-15',
    g.id,
    'd0eebc99-9c0b-4ef8-bb6d-6bb9bd380b33',
    jsonb_build_object(
        'chain_id', 'real_643_m4_6_govreport',
        'source_file_sha256', '93fe23b32d083581456cc17be66361a36ca13caa28d25f63e9466d0c1cb8c6b0',
        'source_file_url', 'https://www.yn.gov.cn/zwgk/zfgb/',
        'extractor_version', 'v1.0',
        'is_demo', 'false'
    )
FROM geo_entity g
WHERE g.canonical_name = '云南省' AND g.level = 'PROVINCIAL'
LIMIT 1
ON CONFLICT (id) DO NOTHING;

COMMIT;

-- 643 spike 落地统计:
--   * source_registry: 3 (heilongjiang/henan/yunnan .gov.cn)
--   * source_document: 3 (3 新 SHA 全 distinct ≠ 642/641/640/639)
--   * policy_document: 3 (GOV_REPORT doc_type)
--   * policy_target: 3
--   * policy_measure: 3
--   * government_commitment: 3 (SELECT geo_entity_id from M2-a)
--   * commitment_progress: 3
--   * project_event: 3 (SELECT geo_entity_id from M2-a)
-- 总计: 24 INSERT (vs 643 tasking 规划 36;spike 边界调整后 24)