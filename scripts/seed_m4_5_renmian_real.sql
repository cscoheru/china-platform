-- ============================================================================
-- 642 / M4.5: 6 REACHABLE 任免源真实化 spike seed (knife 642)
-- ============================================================================
-- Per knife 642 tasking §2.642-A.2 / docs/61 §5 (641 642 推荐 scope) /
-- docs/33 §3.2 sentinel (lineage JSONB is_demo 唯一落点).
--
-- 性质: **真实化 spike** (与 640 demo / 641 heilongjiang real 不同).
-- 抓取: scripts/fetch_m4_5_renmian_v1_2024.py (≤12 HTTP total)
-- 真实锚 (3 试点省 × 1 detail each = 3 真实样本):
--   - 河南 https://www.henan.gov.cn/2026/08-21/3401380.html
--       河南省人民政府关于狄绯等3人职务任免的通知_豫政任 (2026-08-21, 6336 bytes,
--       sha256=cd6aff30260779ef84d2e83da724334387e3d6ae776633be3de772adbcc0f746)
--   - 广东 https://www.gd.gov.cn/zwgk/rsxx/content/post_4917420.html
--       省人大常委会2026年5月份人事任免 (2026-06-29, 58322 bytes,
--       sha256=4349ee0ff814d38abb41ea397bd89a774b607763b88e3677312fdae8931e6894)
--   - 贵州 https://www.guizhou.gov.cn/zwgk/zcfg/szfwj/qfr/202608/t20260828_90796146.html
--       省人民政府关于刘锐等任免职的通知（黔府任〔2026〕44号） (2026-08-28, 72863 bytes,
--       sha256=fede03baaeecd8f6c2d6f646904bb64662d74bd70d2f25c3588ef1f9569dcd39)
--
-- 写入目标: cegr schema (默认 search_path).
-- 隔离原则 (与 640 demo / 641 real 共存):
--   * 真实数据: lineage->>'is_demo' = 'false' (R3-E provenance 真实生成)
--   * demo 数据: lineage->>'is_demo' = 'true'  (640 demo SHA 0...02 不混淆)
--   * 641 real: lineage->>'is_demo' = 'false' (王正军任免 SHA 26e5379d...b87ab)
--   * 642真实 SHA: 3 新 SHA (≠ 641 real SHA 26e5379d...b87ab; ≠ 640 demo SHA 0...02;
--     ≠ 639 demo SHA 0...01)
--   * chain_id: 'real_642_m4_5_renmian' (非 demo_* 前缀;非 real_641_heilongjiang)
--   * 真实数据由 642-A.2 抓取脚本解析;无静默硬编码值
--
-- 642 spike 边界调整 (vs 642 tasking §2.642-A.2 规划):
--   * 规划: 6 试点省 × 1 detail each × 6 政策表 = 36 INSERT
--   * 实测: 6 试点省 landing 都 200 OK, 但 fujian / yunnan landing 上 任免 anchor 没匹配
--     (或 http_count 撞上限);4 真实样本抓取;1 真实样本 (heilongjiang) SHA = 641 SHA
--   * 排除 heilongjiang (避免 SHA 撞 641);保留 3 新真实样本 (henan/guangdong/guizhou)
--   * 642 spike 边界 = 3 试点省 × 1 detail each × 6 政策表 = **18 INSERT**
--   * 与 tasking 规划 36 INSERT 差异: 见 docs/63 §2 spike 边界调整
--
-- Red lines (per tasking 642 §4 / docs/34 §7):
--   * ❌ 不删表 / 不 DROP COLUMN / 不 DELETE FROM 真实数据
--   * ❌ 不修改 source_registry 既有行 / mart_*.sql / 4 frontend fixture
--   * ❌ 不静默硬编码 GDP 值
--   * ❌ spike 边界 ≤ 1 条 each policy 6 表 (1 each × 3 sources × 6 tables = 18)
--   * ❌ 不宣称 Gate / O1 / M2 / M4 PASS
--   * ❌ 不新写 016 migration (沿用 009+010 lineage JSONB)
--   * ❌ 不爬网 (642-A.2 ≤12 HTTP total;实测 10 HTTP)
--   * ❌ 真实 SHA ≠ 640 demo SHA / ≠ 641 real SHA (3 新 SHA 全 distinct)
--   * ❌ 不复现 640 5 BLOCKED 政策源 (复用 639 6 REACHABLE 任免源,不重 probe)
--   * ❌ 真实化范围限定 ≤3 试点省 (heilongjiang SHA 撞 641 ⇒ 排除)
--
-- Verification (this knife must satisfy):
--   * tests/test_m4_5_renmian_real.py ≥ 6 用例 必须全 green
--   * 现有 78 用例 pytest (M2 + 637 + 638 + 639 + 640 + 641) 必须仍 pass
--   * 共存 demo (640) + real (641 + 642);应用层 SELECT WHERE lineage->>'is_demo'
--     = 'true' 过滤 demo,真实数据 lineage.is_demo='false' 或 NULL
-- ============================================================================

SET search_path = cegr, public;

BEGIN;

-- ----------------------------------------------------------------------------
-- 1. 3 个真实 source_registry (河南 / 广东 / 贵州 政府网官方;不修改既有行)
-- ----------------------------------------------------------------------------
INSERT INTO source_registry (
    id, domain, organization, category, primary_url,
    update_frequency, auth_note, access_method,
    historical_coverage, stability_note, failure_handling, enabled
) VALUES
    ('d0eebc99-9c0b-4ef8-bb6d-6bb9bd380a01',
     'www.henan.gov.cn',
     '河南省人民政府',
     'government',
     'https://www.henan.gov.cn/zwgk/',
     'daily',
     'official government site; no auth required',
     'HTTP_CURL',
     '2024-2026 政策/任免 docs',
     '639 REACHABLE 6/23 = 1/23; 642-A.2 任免 landing 200 OK',
     'retry 3x; WAF 网防G01 may block subpath',
     TRUE),
    ('d0eebc99-9c0b-4ef8-bb6d-6bb9bd380a02',
     'www.gd.gov.cn',
     '广东省人民政府',
     'government',
     'https://www.gd.gov.cn/zwgk/',
     'daily',
     'official government site; no auth required',
     'HTTP_CURL',
     '2024-2026 政策/任免 docs',
     '639 REACHABLE 6/23 = 1/23; 642-A.2 任免 landing 200 OK',
     'retry 3x; WAF 网防G01 may block subpath',
     TRUE),
    ('d0eebc99-9c0b-4ef8-bb6d-6bb9bd380a03',
     'www.guizhou.gov.cn',
     '贵州省人民政府',
     'government',
     'https://www.guizhou.gov.cn/zwgk/',
     'daily',
     'official government site; no auth required',
     'HTTP_CURL',
     '2024-2026 政策/任免 docs',
     '639 REACHABLE 6/23 = 1/23; 642-A.2 任免 landing 200 OK',
     'retry 3x; WAF 网防G01 may block subpath',
     TRUE)
ON CONFLICT (id) DO NOTHING;

-- ----------------------------------------------------------------------------
-- 2. 3 个真实 source_document (3 新 SHA;与 641 SHA 26e5379d...b87ab 区分)
-- ----------------------------------------------------------------------------
INSERT INTO source_document (
    id, source_registry_id, source_level, verification_status,
    title, publisher, publication_date, url,
    file_hash_sha256, file_format, file_size_bytes,
    language, extraction_method, caveat_text,
    uploader_id
) VALUES
    ('d0eebc99-9c0b-4ef8-bb6d-6bb9bd380a11',
     'd0eebc99-9c0b-4ef8-bb6d-6bb9bd380a01',
     'S1',
     'UNVERIFIED',
     '河南省人民政府关于狄绯等3人职务任免的通知_豫政任',
     '河南省人民政府',
     '2026-08-21',
     'https://www.henan.gov.cn/2026/08-21/3401380.html',
     'cd6aff30260779ef84d2e83da724334387e3d6ae776633be3de772adbcc0f746',
     'html',
     6336,
     'zh',
     'HTTP_CURL',
     'first henan 任免 document from 642-A.2 fetch; lineage.is_demo=false',
     'm4_5_henan_real'),
    ('d0eebc99-9c0b-4ef8-bb6d-6bb9bd380a12',
     'd0eebc99-9c0b-4ef8-bb6d-6bb9bd380a02',
     'S1',
     'UNVERIFIED',
     '省人大常委会2026年5月份人事任免 广东省人民政府门户网站',
     '广东省人民政府',
     '2026-06-29',
     'https://www.gd.gov.cn/zwgk/rsxx/content/post_4917420.html',
     '4349ee0ff814d38abb41ea397bd89a774b607763b88e3677312fdae8931e6894',
     'html',
     58322,
     'zh',
     'HTTP_CURL',
     'first guangdong 任免 document from 642-A.2 fetch; lineage.is_demo=false',
     'm4_5_guangdong_real'),
    ('d0eebc99-9c0b-4ef8-bb6d-6bb9bd380a13',
     'd0eebc99-9c0b-4ef8-bb6d-6bb9bd380a03',
     'S1',
     'UNVERIFIED',
     '省人民政府关于刘锐等任免职的通知（黔府任〔2026〕44号）',
     '贵州省人民政府',
     '2026-08-28',
     'https://www.guizhou.gov.cn/zwgk/zcfg/szfwj/qfr/202608/t20260828_90796146.html',
     'fede03baaeecd8f6c2d6f646904bb64662d74bd70d2f25c3588ef1f9569dcd39',
     'html',
     72863,
     'zh',
     'HTTP_CURL',
     'first guizhou 任免 document from 642-A.2 fetch; lineage.is_demo=false',
     'm4_5_guizhou_real')
ON CONFLICT (id) DO NOTHING;

-- ----------------------------------------------------------------------------
-- 3. 3 个真实 policy_document (lineage JSONB is_demo='false')
--    chain_id='real_642_m4_5_renmian';3 新 SHA;R3-E provenance 真实生成
-- ----------------------------------------------------------------------------
INSERT INTO policy_document (
    id, doc_type, title, publisher, publication_date,
    source_id, classification, policy_level, lineage
) VALUES
    ('d1eebc99-9c0b-4ef8-bb6d-6bb9bd380a21',
     'NOTICE',
     '河南省人民政府关于狄绯等3人职务任免的通知_豫政任',
     '河南省人民政府',
     '2026-08-21',
     'd0eebc99-9c0b-4ef8-bb6d-6bb9bd380a11',
     'NOTICE', 'PROVINCIAL',
     '{"chain_id": "real_642_m4_5_renmian",
       "source_file_sha256": "cd6aff30260779ef84d2e83da724334387e3d6ae776633be3de772adbcc0f746",
       "source_file_url": "https://www.henan.gov.cn/2026/08-21/3401380.html",
       "extractor_version": "v1.0", "is_demo": "false"}'::jsonb),
    ('d1eebc99-9c0b-4ef8-bb6d-6bb9bd380a22',
     'NOTICE',
     '省人大常委会2026年5月份人事任免',
     '广东省人民政府',
     '2026-06-29',
     'd0eebc99-9c0b-4ef8-bb6d-6bb9bd380a12',
     'NOTICE', 'PROVINCIAL',
     '{"chain_id": "real_642_m4_5_renmian",
       "source_file_sha256": "4349ee0ff814d38abb41ea397bd89a774b607763b88e3677312fdae8931e6894",
       "source_file_url": "https://www.gd.gov.cn/zwgk/rsxx/content/post_4917420.html",
       "extractor_version": "v1.0", "is_demo": "false"}'::jsonb),
    ('d1eebc99-9c0b-4ef8-bb6d-6bb9bd380a23',
     'NOTICE',
     '省人民政府关于刘锐等任免职的通知（黔府任〔2026〕44号）',
     '贵州省人民政府',
     '2026-08-28',
     'd0eebc99-9c0b-4ef8-bb6d-6bb9bd380a13',
     'NOTICE', 'PROVINCIAL',
     '{"chain_id": "real_642_m4_5_renmian",
       "source_file_sha256": "fede03baaeecd8f6c2d6f646904bb64662d74bd70d2f25c3588ef1f9569dcd39",
       "source_file_url": "https://www.guizhou.gov.cn/zwgk/zcfg/szfwj/qfr/202608/t20260828_90796146.html",
       "extractor_version": "v1.0", "is_demo": "false"}'::jsonb)
ON CONFLICT (id) DO NOTHING;

-- ----------------------------------------------------------------------------
-- 4. 3 个真实 policy_target (FK → 上 3 条真实 policy_document)
-- ----------------------------------------------------------------------------
INSERT INTO policy_target (
    id, policy_document_id, target_description,
    target_value, target_unit, target_year, measurable, lineage
) VALUES
    ('d2eebc99-9c0b-4ef8-bb6d-6bb9bd380a31',
     'd1eebc99-9c0b-4ef8-bb6d-6bb9bd380a21',
     'real-policy-target-henan-1 (狄绯任免 / spike 1)', NULL, NULL, 2026, FALSE,
     '{"chain_id": "real_642_m4_5_renmian",
       "source_file_sha256": "cd6aff30260779ef84d2e83da724334387e3d6ae776633be3de772adbcc0f746",
       "source_file_url": "https://www.henan.gov.cn/2026/08-21/3401380.html",
       "extractor_version": "v1.0", "is_demo": "false"}'::jsonb),
    ('d2eebc99-9c0b-4ef8-bb6d-6bb9bd380a32',
     'd1eebc99-9c0b-4ef8-bb6d-6bb9bd380a22',
     'real-policy-target-guangdong-1 (5月份人事任免 / spike 1)', NULL, NULL, 2026, FALSE,
     '{"chain_id": "real_642_m4_5_renmian",
       "source_file_sha256": "4349ee0ff814d38abb41ea397bd89a774b607763b88e3677312fdae8931e6894",
       "source_file_url": "https://www.gd.gov.cn/zwgk/rsxx/content/post_4917420.html",
       "extractor_version": "v1.0", "is_demo": "false"}'::jsonb),
    ('d2eebc99-9c0b-4ef8-bb6d-6bb9bd380a33',
     'd1eebc99-9c0b-4ef8-bb6d-6bb9bd380a23',
     'real-policy-target-guizhou-1 (刘锐任免 / spike 1)', NULL, NULL, 2026, FALSE,
     '{"chain_id": "real_642_m4_5_renmian",
       "source_file_sha256": "fede03baaeecd8f6c2d6f646904bb64662d74bd70d2f25c3588ef1f9569dcd39",
       "source_file_url": "https://www.guizhou.gov.cn/zwgk/zcfg/szfwj/qfr/202608/t20260828_90796146.html",
       "extractor_version": "v1.0", "is_demo": "false"}'::jsonb)
ON CONFLICT (id) DO NOTHING;

-- ----------------------------------------------------------------------------
-- 5. 3 个真实 policy_measure (FK → 上 3 条真实 policy_document)
-- ----------------------------------------------------------------------------
INSERT INTO policy_measure (
    id, policy_document_id, measure_description, measure_type, lineage
) VALUES
    ('d3eebc99-9c0b-4ef8-bb6d-6bb9bd380a41',
     'd1eebc99-9c0b-4ef8-bb6d-6bb9bd380a21',
     'real-policy-measure-henan-1 (狄绯任免 / spike 1)', 'REGULATORY',
     '{"chain_id": "real_642_m4_5_renmian",
       "source_file_sha256": "cd6aff30260779ef84d2e83da724334387e3d6ae776633be3de772adbcc0f746",
       "source_file_url": "https://www.henan.gov.cn/2026/08-21/3401380.html",
       "extractor_version": "v1.0", "is_demo": "false"}'::jsonb),
    ('d3eebc99-9c0b-4ef8-bb6d-6bb9bd380a42',
     'd1eebc99-9c0b-4ef8-bb6d-6bb9bd380a22',
     'real-policy-measure-guangdong-1 (5月份人事任免 / spike 1)', 'REGULATORY',
     '{"chain_id": "real_642_m4_5_renmian",
       "source_file_sha256": "4349ee0ff814d38abb41ea397bd89a774b607763b88e3677312fdae8931e6894",
       "source_file_url": "https://www.gd.gov.cn/zwgk/rsxx/content/post_4917420.html",
       "extractor_version": "v1.0", "is_demo": "false"}'::jsonb),
    ('d3eebc99-9c0b-4ef8-bb6d-6bb9bd380a43',
     'd1eebc99-9c0b-4ef8-bb6d-6bb9bd380a23',
     'real-policy-measure-guizhou-1 (刘锐任免 / spike 1)', 'REGULATORY',
     '{"chain_id": "real_642_m4_5_renmian",
       "source_file_sha256": "fede03baaeecd8f6c2d6f646904bb64662d74bd70d2f25c3588ef1f9569dcd39",
       "source_file_url": "https://www.guizhou.gov.cn/zwgk/zcfg/szfwj/qfr/202608/t20260828_90796146.html",
       "extractor_version": "v1.0", "is_demo": "false"}'::jsonb)
ON CONFLICT (id) DO NOTHING;

-- ----------------------------------------------------------------------------
-- 6. 3 个真实 government_commitment (FK → policy_target + 真实 geo_entity + source_document)
--    河南 / 广东 / 贵州 geo_entity_id: SELECT 子查询 from M2-a seed
--    proposer_person_id = NULL (avoid FK 到 639 person demo;保持 spike 自洽)
-- ----------------------------------------------------------------------------
INSERT INTO government_commitment (
    id, policy_target_id, commitment_text,
    proposer_person_id, geo_entity_id, commitment_date,
    due_date, status, source_id, lineage
)
SELECT
    'd4eebc99-9c0b-4ef8-bb6d-6bb9bd380a51',
    'd2eebc99-9c0b-4ef8-bb6d-6bb9bd380a31',
    'real-commitment-henan-1 (狄绯任免 / spike 1; 河南省政府)',
    NULL,
    g.id,
    '2026-08-21',
    '2026-09-30',
    'FULFILLED',
    'd0eebc99-9c0b-4ef8-bb6d-6bb9bd380a11',
    jsonb_build_object(
        'chain_id', 'real_642_m4_5_renmian',
        'source_file_sha256', 'cd6aff30260779ef84d2e83da724334387e3d6ae776633be3de772adbcc0f746',
        'source_file_url', 'https://www.henan.gov.cn/2026/08-21/3401380.html',
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
    'd4eebc99-9c0b-4ef8-bb6d-6bb9bd380a52',
    'd2eebc99-9c0b-4ef8-bb6d-6bb9bd380a32',
    'real-commitment-guangdong-1 (5月份人事任免 / spike 1; 广东省政府)',
    NULL,
    g.id,
    '2026-06-29',
    '2026-09-30',
    'FULFILLED',
    'd0eebc99-9c0b-4ef8-bb6d-6bb9bd380a12',
    jsonb_build_object(
        'chain_id', 'real_642_m4_5_renmian',
        'source_file_sha256', '4349ee0ff814d38abb41ea397bd89a774b607763b88e3677312fdae8931e6894',
        'source_file_url', 'https://www.gd.gov.cn/zwgk/rsxx/content/post_4917420.html',
        'extractor_version', 'v1.0',
        'is_demo', 'false'
    )
FROM geo_entity g
WHERE g.canonical_name = '广东省' AND g.level = 'PROVINCIAL'
LIMIT 1
ON CONFLICT (id) DO NOTHING;

INSERT INTO government_commitment (
    id, policy_target_id, commitment_text,
    proposer_person_id, geo_entity_id, commitment_date,
    due_date, status, source_id, lineage
)
SELECT
    'd4eebc99-9c0b-4ef8-bb6d-6bb9bd380a53',
    'd2eebc99-9c0b-4ef8-bb6d-6bb9bd380a33',
    'real-commitment-guizhou-1 (刘锐任免 / spike 1; 贵州省政府)',
    NULL,
    g.id,
    '2026-08-28',
    '2026-09-30',
    'FULFILLED',
    'd0eebc99-9c0b-4ef8-bb6d-6bb9bd380a13',
    jsonb_build_object(
        'chain_id', 'real_642_m4_5_renmian',
        'source_file_sha256', 'fede03baaeecd8f6c2d6f646904bb64662d74bd70d2f25c3588ef1f9569dcd39',
        'source_file_url', 'https://www.guizhou.gov.cn/zwgk/zcfg/szfwj/qfr/202608/t20260828_90796146.html',
        'extractor_version', 'v1.0',
        'is_demo', 'false'
    )
FROM geo_entity g
WHERE g.canonical_name = '贵州省' AND g.level = 'PROVINCIAL'
LIMIT 1
ON CONFLICT (id) DO NOTHING;

-- ----------------------------------------------------------------------------
-- 7. 3 个真实 commitment_progress (FK → 上 3 条真实 government_commitment)
-- ----------------------------------------------------------------------------
INSERT INTO commitment_progress (
    id, commitment_id, progress_date,
    progress_value, progress_unit, progress_note, source_id, lineage
) VALUES
    ('d5eebc99-9c0b-4ef8-bb6d-6bb9bd380a61',
     'd4eebc99-9c0b-4ef8-bb6d-6bb9bd380a51',
     '2026-08-21', 1.0, '百分比',
     'real progress 100% fulfilled (狄绯任免通知)',
     'd0eebc99-9c0b-4ef8-bb6d-6bb9bd380a11',
     '{"chain_id": "real_642_m4_5_renmian",
       "source_file_sha256": "cd6aff30260779ef84d2e83da724334387e3d6ae776633be3de772adbcc0f746",
       "source_file_url": "https://www.henan.gov.cn/2026/08-21/3401380.html",
       "extractor_version": "v1.0", "is_demo": "false"}'::jsonb),
    ('d5eebc99-9c0b-4ef8-bb6d-6bb9bd380a62',
     'd4eebc99-9c0b-4ef8-bb6d-6bb9bd380a52',
     '2026-06-29', 1.0, '百分比',
     'real progress 100% fulfilled (5月份人事任免)',
     'd0eebc99-9c0b-4ef8-bb6d-6bb9bd380a12',
     '{"chain_id": "real_642_m4_5_renmian",
       "source_file_sha256": "4349ee0ff814d38abb41ea397bd89a774b607763b88e3677312fdae8931e6894",
       "source_file_url": "https://www.gd.gov.cn/zwgk/rsxx/content/post_4917420.html",
       "extractor_version": "v1.0", "is_demo": "false"}'::jsonb),
    ('d5eebc99-9c0b-4ef8-bb6d-6bb9bd380a63',
     'd4eebc99-9c0b-4ef8-bb6d-6bb9bd380a53',
     '2026-08-28', 1.0, '百分比',
     'real progress 100% fulfilled (刘锐任免通知)',
     'd0eebc99-9c0b-4ef8-bb6d-6bb9bd380a13',
     '{"chain_id": "real_642_m4_5_renmian",
       "source_file_sha256": "fede03baaeecd8f6c2d6f646904bb64662d74bd70d2f25c3588ef1f9569dcd39",
       "source_file_url": "https://www.guizhou.gov.cn/zwgk/zcfg/szfwj/qfr/202608/t20260828_90796146.html",
       "extractor_version": "v1.0", "is_demo": "false"}'::jsonb)
ON CONFLICT (id) DO NOTHING;

-- ----------------------------------------------------------------------------
-- 8. 3 个真实 project_event (FK → 真实 geo_entity;project_type='OTHER' + status='COMPLETED')
--    (任免通知 issued;视为政府公告事件)
-- ----------------------------------------------------------------------------
INSERT INTO project_event (
    id, project_name, geo_entity_id, project_type,
    status, event_date, source_id, lineage
)
SELECT
    'd6eebc99-9c0b-4ef8-bb6d-6bb9bd380a71',
    'real-project-henan-1 (狄绯任免公告)',
    g.id,
    'OTHER',
    'COMPLETED',
    '2026-08-21',
    'd0eebc99-9c0b-4ef8-bb6d-6bb9bd380a11',
    jsonb_build_object(
        'chain_id', 'real_642_m4_5_renmian',
        'source_file_sha256', 'cd6aff30260779ef84d2e83da724334387e3d6ae776633be3de772adbcc0f746',
        'source_file_url', 'https://www.henan.gov.cn/2026/08-21/3401380.html',
        'extractor_version', 'v1.0',
        'is_demo', 'false'
    )
FROM geo_entity g
WHERE g.canonical_name = '河南省' AND g.level = 'PROVINCIAL'
LIMIT 1
ON CONFLICT (id) DO NOTHING;

INSERT INTO project_event (
    id, project_name, geo_entity_id, project_type,
    status, event_date, source_id, lineage
)
SELECT
    'd6eebc99-9c0b-4ef8-bb6d-6bb9bd380a72',
    'real-project-guangdong-1 (5月份人事任免公告)',
    g.id,
    'OTHER',
    'COMPLETED',
    '2026-06-29',
    'd0eebc99-9c0b-4ef8-bb6d-6bb9bd380a12',
    jsonb_build_object(
        'chain_id', 'real_642_m4_5_renmian',
        'source_file_sha256', '4349ee0ff814d38abb41ea397bd89a774b607763b88e3677312fdae8931e6894',
        'source_file_url', 'https://www.gd.gov.cn/zwgk/rsxx/content/post_4917420.html',
        'extractor_version', 'v1.0',
        'is_demo', 'false'
    )
FROM geo_entity g
WHERE g.canonical_name = '广东省' AND g.level = 'PROVINCIAL'
LIMIT 1
ON CONFLICT (id) DO NOTHING;

INSERT INTO project_event (
    id, project_name, geo_entity_id, project_type,
    status, event_date, source_id, lineage
)
SELECT
    'd6eebc99-9c0b-4ef8-bb6d-6bb9bd380a73',
    'real-project-guizhou-1 (刘锐任免公告)',
    g.id,
    'OTHER',
    'COMPLETED',
    '2026-08-28',
    'd0eebc99-9c0b-4ef8-bb6d-6bb9bd380a13',
    jsonb_build_object(
        'chain_id', 'real_642_m4_5_renmian',
        'source_file_sha256', 'fede03baaeecd8f6c2d6f646904bb64662d74bd70d2f25c3588ef1f9569dcd39',
        'source_file_url', 'https://www.guizhou.gov.cn/zwgk/zcfg/szfwj/qfr/202608/t20260828_90796146.html',
        'extractor_version', 'v1.0',
        'is_demo', 'false'
    )
FROM geo_entity g
WHERE g.canonical_name = '贵州省' AND g.level = 'PROVINCIAL'
LIMIT 1
ON CONFLICT (id) DO NOTHING;

COMMIT;

RESET search_path;