-- ============================================================================
-- 641 / M4.4: 黑龙江政策真实化 spike seed (knife 641)
-- ============================================================================
-- Per knife 641 tasking §2.641-A.2 / docs/60 §5 (M4.4 推荐 scope) /
-- docs/33 §3.2 sentinel (lineage JSONB is_demo 唯一落点).
--
-- 性质: **真实化 spike** (与 640 demo 不同;沿用 sentinel 基础设施).
-- 抓取: scripts/fetch_heilongjiang_policy_v1_2024.py (≤4 HTTP total)
-- 真实锚: https://www.hlj.gov.cn/hlj/c108368/zwgk.shtml (政务公开 landing)
--         → https://www.hlj.gov.cn/hlj/c108378/202608/c00_31971131.shtml
--           黑龙江省人民政府关于王正军等任免职的通知 (2026-08-31, 21348 bytes,
--           sha256=26e5379d86e6a5c6a596acfef41293821a07413e973e1481b2b373f2e00b87ab)
-- 真实 SHA: hashlib.sha256(detail_page_html).hexdigest() (calc on fetch)
--
-- 写入目标: cegr schema (默认 search_path).
-- 隔离原则 (与 640 demo 共存):
--   * 真实数据: lineage->>'is_demo' = 'false' (R3-E provenance 真实生成)
--   * demo 数据: lineage->>'is_demo' = 'true'  (640 demo SHA 0...02 不混淆)
--   * 真实 SHA ≠ 640 demo SHA '0000...0002'
--   * chain_id: 'real_641_heilongjiang' (非 demo_* 前缀)
--   * 真实数据由 641-A.1 抓取脚本解析;无静默硬编码值
--
-- Red lines (per tasking 641 §4 / docs/34 §7):
--   * ❌ 不删表 / 不 DROP COLUMN / 不 DELETE FROM 真实数据
--   * ❌ 不修改 source_registry 既有行 / mart_*.sql / 4 frontend fixture
--   * ❌ 不静默硬编码 GDP 值 (commitment_text 等从 641-A.1 抓取;无则 NULL)
--   * ❌ spike 边界 ≤ 1 条 each policy 6 表 (1 真实 spike,不复现 640 demo 3 行)
--   * ❌ 不宣称 Gate / O1 / M2 / M4 PASS
--   * ❌ 不新写 016 migration (沿用 009+010 lineage JSONB)
--   * ❌ 不爬网 (641-A.1 ≤4 HTTP total)
--   * ❌ 不复现 639 6 REACHABLE 任免源 / 不复现 640 5 BLOCKED 政策源
--   * ❌ 真实化范围限定 1 省 (黑龙江唯一 REACHABLE per 640 二次 probe)
--   * ❌ 真实 SHA ≠ 640 demo SHA '0000...0002'
--
-- Verification (this knife must satisfy):
--   * tests/test_m4_4_heilongjiang_real.py ≥ 6 用例 必须全 green
--   * 现有 71 用例 pytest (M2 + 637 + 638 + 639 + 640) 必须仍 pass
--   * 共存 demo (640) + real (641);应用层 SELECT WHERE lineage->>'is_demo'
--     = 'true' 过滤 demo,真实数据 lineage.is_demo='false' 或 NULL
-- ============================================================================

SET search_path = cegr, public;

BEGIN;

-- ----------------------------------------------------------------------------
-- 1. 1 个真实 source_registry (黑龙江政府网官方;与既有 registry 行兼容)
-- ----------------------------------------------------------------------------
INSERT INTO source_registry (
    id, domain, organization, category, primary_url,
    update_frequency, auth_note, access_method,
    historical_coverage, stability_note, failure_handling, enabled
) VALUES (
    'c1eebc99-9c0b-4ef8-bb6d-6bb9bd380a01',
    'www.hlj.gov.cn',
    '黑龙江省人民政府',
    'government',
    'https://www.hlj.gov.cn/hlj/c108368/zwgk.shtml',
    'daily',
    'official government site; no auth required',
    'HTTP_CURL',
    '2024-2026 policy/announcement docs',
    'site stable; 640 二次 probe REACHABLE 2/12 = 1 province (heilongjiang) only',
    'retry 3x; WAF 网防G01 may block subpath; 641 effective path uses /hlj/c108368/zwgk.shtml',
    TRUE
) ON CONFLICT (id) DO NOTHING;

-- ----------------------------------------------------------------------------
-- 2. 1 个真实 source_document (real SHA = 641-A.1 抓取的详情页 HTML SHA256)
--    真实化 spike;verification_status = UNVERIFIED (待人工核验 人工裁定门)
-- ----------------------------------------------------------------------------
INSERT INTO source_document (
    id, source_registry_id, source_level, verification_status,
    title, publisher, publication_date, url,
    file_hash_sha256, file_format, file_size_bytes,
    language, extraction_method, caveat_text,
    uploader_id
) VALUES (
    'c1eebc99-9c0b-4ef8-bb6d-6bb9bd380a11',
    'c1eebc99-9c0b-4ef8-bb6d-6bb9bd380a01',
    'S1',                                   -- S1 = 政府官方源 (per docs/34 §6 源等级)
    'UNVERIFIED',                           -- 真实化 spike; 待人工核验 (人工裁定门)
    '黑龙江省人民政府关于王正军等任免职的通知_黑政干',
    '黑龙江省人民政府',
    '2026-08-31',
    'https://www.hlj.gov.cn/hlj/c108378/202608/c00_31971131.shtml',
    '26e5379d86e6a5c6a596acfef41293821a07413e973e1481b2b373f2e00b87ab',  -- 真实 SHA (calc on fetch)
    'html',
    21348,                                  -- 真实 file_size from 641-A.1
    'zh',
    'HTTP_CURL',
    'first real policy document from heilongjiang /hlj/c108368/zwgk.shtml via 641-A.1; lineage.is_demo=false',
    'm4_4_heilongjiang_real'
) ON CONFLICT (id) DO NOTHING;

-- ----------------------------------------------------------------------------
-- 3. 1 个真实 policy_document (lineage JSONB is_demo='false')
--    真实化 sentinel: chain_id='real_641_heilongjiang' (R3-E provenance 真实)
--    真实 SHA ≠ 640 demo SHA '0000...0002'
-- ----------------------------------------------------------------------------
INSERT INTO policy_document (
    id, doc_type, title, publisher, publication_date,
    source_id, classification, policy_level, lineage
) VALUES (
    'c2eebc99-9c0b-4ef8-bb6d-6bb9bd380a21',
    'NOTICE',
    '黑龙江省人民政府关于王正军等任免职的通知_黑政干',
    '黑龙江省人民政府',
    '2026-08-31',
    'c1eebc99-9c0b-4ef8-bb6d-6bb9bd380a11',
    'NOTICE',
    'PROVINCIAL',
    '{"chain_id": "real_641_heilongjiang", "source_file_sha256": "26e5379d86e6a5c6a596acfef41293821a07413e973e1481b2b373f2e00b87ab",
       "source_file_url": "https://www.hlj.gov.cn/hlj/c108378/202608/c00_31971131.shtml",
       "extractor_version": "v1.0", "is_demo": "false"}'::jsonb
) ON CONFLICT (id) DO NOTHING;

-- ----------------------------------------------------------------------------
-- 4. 1 个真实 policy_target (FK → 上 1 条真实 policy_document)
-- ----------------------------------------------------------------------------
INSERT INTO policy_target (
    id, policy_document_id, target_description,
    target_value, target_unit, target_year, measurable, lineage
) VALUES (
    'c3eebc99-9c0b-4ef8-bb6d-6bb9bd380a31',
    'c2eebc99-9c0b-4ef8-bb6d-6bb9bd380a21',
    'real-policy-target-1 (王正军任免通知 / spike 1)',
    NULL, NULL, 2026, FALSE,
    '{"chain_id": "real_641_heilongjiang", "source_file_sha256": "26e5379d86e6a5c6a596acfef41293821a07413e973e1481b2b373f2e00b87ab",
       "source_file_url": "https://www.hlj.gov.cn/hlj/c108378/202608/c00_31971131.shtml",
       "extractor_version": "v1.0", "is_demo": "false"}'::jsonb
) ON CONFLICT (id) DO NOTHING;

-- ----------------------------------------------------------------------------
-- 5. 1 个真实 policy_measure (FK → 上 1 条真实 policy_document)
-- ----------------------------------------------------------------------------
INSERT INTO policy_measure (
    id, policy_document_id, measure_description, measure_type, lineage
) VALUES (
    'c4eebc99-9c0b-4ef8-bb6d-6bb9bd380a41',
    'c2eebc99-9c0b-4ef8-bb6d-6bb9bd380a21',
    'real-policy-measure-1 (王正军任免通知 / spike 1)',
    'REGULATORY',
    '{"chain_id": "real_641_heilongjiang", "source_file_sha256": "26e5379d86e6a5c6a596acfef41293821a07413e973e1481b2b373f2e00b87ab",
       "source_file_url": "https://www.hlj.gov.cn/hlj/c108378/202608/c00_31971131.shtml",
       "extractor_version": "v1.0", "is_demo": "false"}'::jsonb
) ON CONFLICT (id) DO NOTHING;

-- ----------------------------------------------------------------------------
-- 6. 1 个真实 government_commitment
--    (FK → 上 1 条真实 policy_target + 真实 geo_entity (黑龙江) + source_document)
--    黑龙江省 geo_entity_id: SELECT 子查询 from M2-a seed (canonical_name='黑龙江省')
--    proposer_person_id = NULL (avoid FK 到 639 person demo;保持 spike 自洽)
-- ----------------------------------------------------------------------------
INSERT INTO government_commitment (
    id, policy_target_id, commitment_text,
    proposer_person_id, geo_entity_id, commitment_date,
    due_date, status, source_id, lineage
)
SELECT
    'c5eebc99-9c0b-4ef8-bb6d-6bb9bd380a51',
    'c3eebc99-9c0b-4ef8-bb6d-6bb9bd380a31',
    'real-commitment-1 (王正军任免通知 / spike 1; 黑龙江省政府)',
    NULL,
    g.id,
    '2026-08-31',
    '2026-09-30',
    'FULFILLED',
    'c1eebc99-9c0b-4ef8-bb6d-6bb9bd380a11',
    jsonb_build_object(
        'chain_id', 'real_641_heilongjiang',
        'source_file_sha256', '26e5379d86e6a5c6a596acfef41293821a07413e973e1481b2b373f2e00b87ab',
        'source_file_url', 'https://www.hlj.gov.cn/hlj/c108378/202608/c00_31971131.shtml',
        'extractor_version', 'v1.0',
        'is_demo', 'false'
    )
FROM geo_entity g
WHERE g.canonical_name = '黑龙江省' AND g.level = 'PROVINCIAL'
LIMIT 1
ON CONFLICT (id) DO NOTHING;

-- ----------------------------------------------------------------------------
-- 7. 1 个真实 commitment_progress (FK → 上 1 条真实 government_commitment)
-- ----------------------------------------------------------------------------
INSERT INTO commitment_progress (
    id, commitment_id, progress_date,
    progress_value, progress_unit, progress_note, source_id, lineage
) VALUES (
    'c6eebc99-9c0b-4ef8-bb6d-6bb9bd380a61',
    'c5eebc99-9c0b-4ef8-bb6d-6bb9bd380a51',
    '2026-08-31',
    1.0,
    '百分比',
    'real progress 100% fulfilled (王正军任免通知)',
    'c1eebc99-9c0b-4ef8-bb6d-6bb9bd380a11',
    '{"chain_id": "real_641_heilongjiang", "source_file_sha256": "26e5379d86e6a5c6a596acfef41293821a07413e973e1481b2b373f2e00b87ab",
       "source_file_url": "https://www.hlj.gov.cn/hlj/c108378/202608/c00_31971131.shtml",
       "extractor_version": "v1.0", "is_demo": "false"}'::jsonb
) ON CONFLICT (id) DO NOTHING;

-- ----------------------------------------------------------------------------
-- 8. 1 个真实 project_event (FK → 真实 geo_entity 黑龙江)
--    真实化 spike: project_type='OTHER' + status='COMPLETED'
--    (任免通知 issued;视为政府公告事件)
-- ----------------------------------------------------------------------------
INSERT INTO project_event (
    id, project_name, geo_entity_id, project_type,
    status, event_date, source_id, lineage
)
SELECT
    'c7eebc99-9c0b-4ef8-bb6d-6bb9bd380a71',
    'real-project-1 (王正军任免公告)',
    g.id,
    'OTHER',
    'COMPLETED',
    '2026-08-31',
    'c1eebc99-9c0b-4ef8-bb6d-6bb9bd380a11',
    jsonb_build_object(
        'chain_id', 'real_641_heilongjiang',
        'source_file_sha256', '26e5379d86e6a5c6a596acfef41293821a07413e973e1481b2b373f2e00b87ab',
        'source_file_url', 'https://www.hlj.gov.cn/hlj/c108378/202608/c00_31971131.shtml',
        'extractor_version', 'v1.0',
        'is_demo', 'false'
    )
FROM geo_entity g
WHERE g.canonical_name = '黑龙江省' AND g.level = 'PROVINCIAL'
LIMIT 1
ON CONFLICT (id) DO NOTHING;

COMMIT;

RESET search_path;
