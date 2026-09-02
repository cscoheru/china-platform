-- ============================================================================
-- 658 / M2-b: U6 hongheiku 26 省 × 5 指标 batch seed (knife 658)
-- ============================================================================
-- Per knife 658 tasking §1.658 / 658-A.1 / 658-A.2 / docs/81 U6 ruling /
-- U6 金丝雀 CANARY_PASS 5/5 (5 省 × 5 字段 delta=0 全等).
--
-- 性质: hongheiku 转载页 batch (与 657 M4.20 spike 不同; U6 数据源用户裁定)
-- 抓取: scripts/fetch_m2_u6_batch_26prov_2024.py (≤32 HTTP; 23 REACHABLE + 3 BLOCKED)
-- 数据源: hongheiku 红黑统计公报库 (https://tjgb.hongheiku.com/)
--         —— U6 2026-09-02 用户裁定 + docs/81 ruling (含 lineage 三重标注)
--         source='hongheiku_tjgb' / origin='XX省统计局' / ruling='U6 2026-09-02'
--
-- INSERT 拓扑:
--   5 indicator_definition + 5 indicator_methodology_version (a-prefix)
--   23 REACHABLE 省 × (source_registry + source_document + source_location +
--                       ingestion_run + 5 observation)
--   = 5 + 5 + (23 + 23 + 23 + 23 + 23*5) = 232 INSERT ROWS
--   3 BLOCKED 省 (liaoning/hainan/guizhou) → 留痕不代换 (红线 14)
--
-- Red lines (per tasking 658 §D / docs/81 §5 / 654-657 沿用):
--   ❌ 不删表 / 不新写 016 migration (沿用 009+010+014+015 lineage JSONB)
--   ❌ 不修改 source_registry 既有行 (4 fixture + 5 canary 锁值)
--   ❌ 不静默硬编码 value (each value from fetch_*.py extraction)
--   ❌ 不爬网 (≤32 HTTP; category-first URL discovery)
--   ❌ 不补零 / 不跳缺 (整省 BLOCKED 或单值 NULL+missing_reason)
--   ❌ spike 边界: 23 REACHABLE provinces only (3 BLOCKED excluded)
--   ❌ 不宣称 Gate / O1 / M2 / M4 PASS
--   ❌ 不宣称 M2 PASS (M2.3 跨源升级评估只读)
-- ============================================================================

SET search_path = cegr, public;

BEGIN;

-- ----------------------------------------------------------------------------
-- 0. indicator_definition + indicator_methodology_version (5 个指标)
--    沿用 657 M2-b 既有 GDP_ANNUAL; 新增 4 个三次产业 + 1 个增长率
--    short_code: GDP_ANNUAL / GDP_GROWTH / GVA_PRIMARY / GVA_SECONDARY / GVA_TERTIARY
--    UUID a 段 (a2000000-0000-0000-0000-00000000a001-a010) — 沿用 657 namespace
-- ----------------------------------------------------------------------------
INSERT INTO cegr.indicator_definition
    (id, canonical_name, canonical_name_en, short_code,
     description, unit_canonical, unit_category,
     frequency, is_cumulative, geo_scope_default)
VALUES
    ('a2000000-0000-0000-0000-00000000a001', '地区生产总值(年度)',
     'Gross Regional Product (Annual)', 'GDP_ANNUAL',
     '年度地区生产总值；初步核算口径（区别于 M1 GDP 半年累计）',
     '亿元', 'CURRENCY', 'YEARLY', TRUE, 'PROVINCE'),
    ('a2000000-0000-0000-0000-00000000a003', '地区生产总值增长率(年度)',
     'Gross Regional Product Growth Rate (Annual)', 'GDP_GROWTH',
     '年度地区生产总值同比增长率；不变价计算',
     '%', 'PERCENTAGE', 'YEARLY', FALSE, 'PROVINCE'),
    ('a2000000-0000-0000-0000-00000000a004', '第一产业增加值(年度)',
     'Primary Industry Value Added (Annual)', 'GVA_PRIMARY',
     '年度第一产业增加值；初步核算口径',
     '亿元', 'CURRENCY', 'YEARLY', TRUE, 'PROVINCE'),
    ('a2000000-0000-0000-0000-00000000a005', '第二产业增加值(年度)',
     'Secondary Industry Value Added (Annual)', 'GVA_SECONDARY',
     '年度第二产业增加值；初步核算口径',
     '亿元', 'CURRENCY', 'YEARLY', TRUE, 'PROVINCE'),
    ('a2000000-0000-0000-0000-00000000a006', '第三产业增加值(年度)',
     'Tertiary Industry Value Added (Annual)', 'GVA_TERTIARY',
     '年度第三产业增加值；初步核算口径',
     '亿元', 'CURRENCY', 'YEARLY', TRUE, 'PROVINCE')
ON CONFLICT (id) DO NOTHING;


INSERT INTO cegr.indicator_methodology_version
    (id, indicator_id, version_label,
     valid_from, change_summary, impact_note,
     source_id)
VALUES
    ('a2000000-0000-0000-0000-00000000a002',
     'a2000000-0000-0000-0000-00000000a001',
     'M2-b 2024 年度 GDP 初步核算', '2024-01-01'::date,
     'M2-b 2024 年度 GDP 初步核算口径',
     '2024 年初步核算；最终核实以国家统计局核定为准',
     'a2000000-0000-0000-0000-0000000ff227'),
    ('a2000000-0000-0000-0000-00000000a007',
     'a2000000-0000-0000-0000-00000000a003',
     'M2-b 2024 年度 GDP 增长率', '2024-01-01'::date,
     'M2-b 2024 年度 GDP 同比增长率',
     '2024 年同比增长率；不变价计算',
     'a2000000-0000-0000-0000-0000000ff227'),
    ('a2000000-0000-0000-0000-00000000a008',
     'a2000000-0000-0000-0000-00000000a004',
     'M2-b 2024 年度 第一产业增加值', '2024-01-01'::date,
     'M2-b 2024 年度 第一产业增加值初步核算口径',
     '2024 年初步核算',
     'a2000000-0000-0000-0000-0000000ff227'),
    ('a2000000-0000-0000-0000-00000000a009',
     'a2000000-0000-0000-0000-00000000a005',
     'M2-b 2024 年度 第二产业增加值', '2024-01-01'::date,
     'M2-b 2024 年度 第二产业增加值初步核算口径',
     '2024 年初步核算',
     'a2000000-0000-0000-0000-0000000ff227'),
    ('a2000000-0000-0000-0000-00000000a010',
     'a2000000-0000-0000-0000-00000000a006',
     'M2-b 2024 年度 第三产业增加值', '2024-01-01'::date,
     'M2-b 2024 年度 第三产业增加值初步核算口径',
     '2024 年初步核算',
     'a2000000-0000-0000-0000-0000000ff227')
ON CONFLICT (id) DO NOTHING;

-- ----------------------------------------------------------------------------
-- 1-23. 23 REACHABLE province (per-province: registry + document + location +
--                                ingestion_run + 5 observations)
--    UUID q 段 (q0eebc99/q1eebc99/q2eebc99/q6eebc99/q7eebc99) ≠ 657 p 段
--    5 指标 × 23 省 = 115 observation rows
-- ----------------------------------------------------------------------------
-- Province 01: tianjin (天津市, admin_code=12, idx=00)
DO $$
DECLARE
    v_registry_id UUID := 'q0eebc99-0000-4000-8000-000000000000';
    v_doc_id UUID := 'q1eebc99-0000-4000-8000-000000000000';
    v_loc_id UUID := 'q2eebc99-0000-4000-8000-000000000000';
    v_run_id UUID := 'q7eebc99-0000-4000-8000-000000000000';
    v_geo_entity_id UUID := 'a2000000-0000-0000-0000-000000000012';
    v_geo_cv_id UUID := 'a2000000-0000-0000-0000-00000000001201';
BEGIN
    -- 1) source_registry (hongheiku_tjgb, origin=天津市统计局)
    INSERT INTO cegr.source_registry
        (id, domain, organization, category, primary_url,
         update_frequency, auth_note, access_method,
         historical_coverage, stability_note, failure_handling,
         enabled, source_level,
         lineage)
    VALUES
        (v_registry_id, 'tjgb.hongheiku.com',
         'hongheiku 转载 (origin: 天津市统计局)', 'PROVINCIAL_BULLETIN_REPRINT',
         'https://tjgb.hongheiku.com/sjtjgb/57426.html', 'ANNUAL',
         '公开转载;hongheiku 红黑统计公报库;U6 用户裁定接受',
         'HTTP_CURL', '2024 年度公报',
         'U6 金丝雀 5/5 PASS (京/沪/鲁/鄂/川 delta=0 全等)',
         'BLOCKED_NO_POOL 留痕不代换 (红线 14)',
         TRUE, 'S2_REPRINT',
         jsonb_build_object(
             'chain_id', 'real_658_m2_u6_batch_v1'::text,
             'knife', '658',
             'source', 'hongheiku_tjgb',
             'origin', '天津市统计局',
             'ruling', 'U6 2026-09-02',
             'cross_reference', '金丝雀 5/5 全等 (京/沪/鲁/鄂/川)',
             'reprint', TRUE,
             'extraction_method', 'category_first_url_discovery'
         ))
    ON CONFLICT (id) DO NOTHING;

    -- 2) source_document (file SHA 锁转载字节)
    INSERT INTO cegr.source_document
        (id, source_id, file_path, file_size_bytes, file_hash_sha256,
         mime_type, retrieval_method, retrieval_at, raw_content_ref)
    VALUES
        (v_doc_id, v_registry_id,
         '/tmp/_658_tianjin.html',
         65462,
         'a7f8254ed5f4e42624f43775b80a749c32b1a3e1e1340fc736c24344c7cc8fcf',
         'text/html', 'HTTP_CURL',
         '2026-09-02'::timestamp,
         'evidence_pack/u6_batch_26prov_fetch_20260902.json#tianjin')
    ON CONFLICT (id) DO NOTHING;

    -- 3) source_location (URL + http_code 200)
    INSERT INTO cegr.source_location
        (id, source_id, location_type, url, http_code,
         accessed_at, content_hash, notes)
    VALUES
        (v_loc_id, v_registry_id, 'PRIMARY_URL',
         'https://tjgb.hongheiku.com/sjtjgb/57426.html', 200,
         '2026-09-02'::timestamp,
         'a7f8254ed5f4e42624f43775b80a749c32b1a3e1e1340fc736c24344c7cc8fcf',
         'hongheiku 转载页; 2024 年度公报; 1 HTTP (cache hit post-1st)')
    ON CONFLICT (id) DO NOTHING;

    -- 4) ingestion_run (status=SUCCESS, records_inserted=5)
    INSERT INTO cegr.ingestion_run
        (id, source_id, started_at, finished_at,
         records_inserted, records_updated, records_skipped,
         status, error_message, run_kind)
    VALUES
        (v_run_id, v_registry_id,
         '2026-09-02'::timestamp, '2026-09-02'::timestamp,
         5, 0, 0,
         'SUCCESS', NULL,
         'U6_HONGHEIKU_REPRINT_BATCH')
    ON CONFLICT (id) DO NOTHING;
    -- observation GDP_ANNUAL: 18024.32 亿元
    INSERT INTO cegr.observation
        (id, indicator_id, indicator_methodology_version_id,
         geo_entity_id, geo_code_version_id, calendar_period_id,
         value, raw_value, is_imputed, missing_reason,
         unit, comparison_basis, value_type, status,
         source_id, source_location_id, ingestion_run_id,
         extracted_at, extraction_method, confidence, notes)
    VALUES
        ('q6eebc99-0000-4000-8000-000000000000',
         'a2000000-0000-0000-0000-00000000a001', 'a2000000-0000-0000-0000-00000000a002',
         v_geo_entity_id, v_geo_cv_id, 'a2000000-0000-0000-0000-000020240101',
         18024.32, '18024.32', FALSE, NULL,
         '亿元', 'YEAR_OVER_YEAR', 'REAL', 'PUBLISHED',
         v_registry_id, v_loc_id, v_run_id,
         '2026-09-02'::timestamp, 'REGEX_ANCHORED', 1.0,
         'tianjin GDP_ANNUAL 18024.32 亿元;hongheiku 转载;U6 裁定;lineage 三重标注')
    ON CONFLICT (id) DO NOTHING;
    -- observation GDP_GROWTH: 5.1 %
    INSERT INTO cegr.observation
        (id, indicator_id, indicator_methodology_version_id,
         geo_entity_id, geo_code_version_id, calendar_period_id,
         value, raw_value, is_imputed, missing_reason,
         unit, comparison_basis, value_type, status,
         source_id, source_location_id, ingestion_run_id,
         extracted_at, extraction_method, confidence, notes)
    VALUES
        ('q6eebc99-0000-4000-8000-000000000001',
         'a2000000-0000-0000-0000-00000000a003', 'a2000000-0000-0000-0000-00000000a007',
         v_geo_entity_id, v_geo_cv_id, 'a2000000-0000-0000-0000-000020240101',
         5.1, '5.1', FALSE, NULL,
         '%', 'YEAR_OVER_YEAR', 'REAL', 'PUBLISHED',
         v_registry_id, v_loc_id, v_run_id,
         '2026-09-02'::timestamp, 'REGEX_ANCHORED', 1.0,
         'tianjin GDP_GROWTH 5.1 %;hongheiku 转载;U6 裁定;lineage 三重标注')
    ON CONFLICT (id) DO NOTHING;
    -- observation GVA_PRIMARY: 284.28 亿元
    INSERT INTO cegr.observation
        (id, indicator_id, indicator_methodology_version_id,
         geo_entity_id, geo_code_version_id, calendar_period_id,
         value, raw_value, is_imputed, missing_reason,
         unit, comparison_basis, value_type, status,
         source_id, source_location_id, ingestion_run_id,
         extracted_at, extraction_method, confidence, notes)
    VALUES
        ('q6eebc99-0000-4000-8000-000000000002',
         'a2000000-0000-0000-0000-00000000a004', 'a2000000-0000-0000-0000-00000000a008',
         v_geo_entity_id, v_geo_cv_id, 'a2000000-0000-0000-0000-000020240101',
         284.28, '284.28', FALSE, NULL,
         '亿元', 'YEAR_OVER_YEAR', 'REAL', 'PUBLISHED',
         v_registry_id, v_loc_id, v_run_id,
         '2026-09-02'::timestamp, 'REGEX_ANCHORED', 1.0,
         'tianjin GVA_PRIMARY 284.28 亿元;hongheiku 转载;U6 裁定;lineage 三重标注')
    ON CONFLICT (id) DO NOTHING;
    -- observation GVA_SECONDARY: 6214.27 亿元
    INSERT INTO cegr.observation
        (id, indicator_id, indicator_methodology_version_id,
         geo_entity_id, geo_code_version_id, calendar_period_id,
         value, raw_value, is_imputed, missing_reason,
         unit, comparison_basis, value_type, status,
         source_id, source_location_id, ingestion_run_id,
         extracted_at, extraction_method, confidence, notes)
    VALUES
        ('q6eebc99-0000-4000-8000-000000000003',
         'a2000000-0000-0000-0000-00000000a005', 'a2000000-0000-0000-0000-00000000a009',
         v_geo_entity_id, v_geo_cv_id, 'a2000000-0000-0000-0000-000020240101',
         6214.27, '6214.27', FALSE, NULL,
         '亿元', 'YEAR_OVER_YEAR', 'REAL', 'PUBLISHED',
         v_registry_id, v_loc_id, v_run_id,
         '2026-09-02'::timestamp, 'REGEX_ANCHORED', 1.0,
         'tianjin GVA_SECONDARY 6214.27 亿元;hongheiku 转载;U6 裁定;lineage 三重标注')
    ON CONFLICT (id) DO NOTHING;
    -- observation GVA_TERTIARY: 11525.77 亿元
    INSERT INTO cegr.observation
        (id, indicator_id, indicator_methodology_version_id,
         geo_entity_id, geo_code_version_id, calendar_period_id,
         value, raw_value, is_imputed, missing_reason,
         unit, comparison_basis, value_type, status,
         source_id, source_location_id, ingestion_run_id,
         extracted_at, extraction_method, confidence, notes)
    VALUES
        ('q6eebc99-0000-4000-8000-000000000004',
         'a2000000-0000-0000-0000-00000000a006', 'a2000000-0000-0000-0000-00000000a010',
         v_geo_entity_id, v_geo_cv_id, 'a2000000-0000-0000-0000-000020240101',
         11525.77, '11525.77', FALSE, NULL,
         '亿元', 'YEAR_OVER_YEAR', 'REAL', 'PUBLISHED',
         v_registry_id, v_loc_id, v_run_id,
         '2026-09-02'::timestamp, 'REGEX_ANCHORED', 1.0,
         'tianjin GVA_TERTIARY 11525.77 亿元;hongheiku 转载;U6 裁定;lineage 三重标注')
    ON CONFLICT (id) DO NOTHING;
END $$;

-- Province 02: chongqing (重庆市, admin_code=50, idx=01)
DO $$
DECLARE
    v_registry_id UUID := 'q0eebc99-0001-4000-8000-000000000001';
    v_doc_id UUID := 'q1eebc99-0001-4000-8000-000000000001';
    v_loc_id UUID := 'q2eebc99-0001-4000-8000-000000000001';
    v_run_id UUID := 'q7eebc99-0001-4000-8000-000000000001';
    v_geo_entity_id UUID := 'a2000000-0000-0000-0000-000000000050';
    v_geo_cv_id UUID := 'a2000000-0000-0000-0000-00000000005001';
BEGIN
    -- 1) source_registry (hongheiku_tjgb, origin=重庆市统计局)
    INSERT INTO cegr.source_registry
        (id, domain, organization, category, primary_url,
         update_frequency, auth_note, access_method,
         historical_coverage, stability_note, failure_handling,
         enabled, source_level,
         lineage)
    VALUES
        (v_registry_id, 'tjgb.hongheiku.com',
         'hongheiku 转载 (origin: 重庆市统计局)', 'PROVINCIAL_BULLETIN_REPRINT',
         'https://tjgb.hongheiku.com/sjtjgb/57604.html', 'ANNUAL',
         '公开转载;hongheiku 红黑统计公报库;U6 用户裁定接受',
         'HTTP_CURL', '2024 年度公报',
         'U6 金丝雀 5/5 PASS (京/沪/鲁/鄂/川 delta=0 全等)',
         'BLOCKED_NO_POOL 留痕不代换 (红线 14)',
         TRUE, 'S2_REPRINT',
         jsonb_build_object(
             'chain_id', 'real_658_m2_u6_batch_v1'::text,
             'knife', '658',
             'source', 'hongheiku_tjgb',
             'origin', '重庆市统计局',
             'ruling', 'U6 2026-09-02',
             'cross_reference', '金丝雀 5/5 全等 (京/沪/鲁/鄂/川)',
             'reprint', TRUE,
             'extraction_method', 'category_first_url_discovery'
         ))
    ON CONFLICT (id) DO NOTHING;

    -- 2) source_document (file SHA 锁转载字节)
    INSERT INTO cegr.source_document
        (id, source_id, file_path, file_size_bytes, file_hash_sha256,
         mime_type, retrieval_method, retrieval_at, raw_content_ref)
    VALUES
        (v_doc_id, v_registry_id,
         '/tmp/_658_chongqing.html',
         76457,
         '00c674b09af35351590ddf976342ea6768245ce52380b9c629e3b88313d60ea3',
         'text/html', 'HTTP_CURL',
         '2026-09-02'::timestamp,
         'evidence_pack/u6_batch_26prov_fetch_20260902.json#chongqing')
    ON CONFLICT (id) DO NOTHING;

    -- 3) source_location (URL + http_code 200)
    INSERT INTO cegr.source_location
        (id, source_id, location_type, url, http_code,
         accessed_at, content_hash, notes)
    VALUES
        (v_loc_id, v_registry_id, 'PRIMARY_URL',
         'https://tjgb.hongheiku.com/sjtjgb/57604.html', 200,
         '2026-09-02'::timestamp,
         '00c674b09af35351590ddf976342ea6768245ce52380b9c629e3b88313d60ea3',
         'hongheiku 转载页; 2024 年度公报; 1 HTTP (cache hit post-1st)')
    ON CONFLICT (id) DO NOTHING;

    -- 4) ingestion_run (status=SUCCESS, records_inserted=5)
    INSERT INTO cegr.ingestion_run
        (id, source_id, started_at, finished_at,
         records_inserted, records_updated, records_skipped,
         status, error_message, run_kind)
    VALUES
        (v_run_id, v_registry_id,
         '2026-09-02'::timestamp, '2026-09-02'::timestamp,
         5, 0, 0,
         'SUCCESS', NULL,
         'U6_HONGHEIKU_REPRINT_BATCH')
    ON CONFLICT (id) DO NOTHING;
    -- observation GDP_ANNUAL: 32193.15 亿元
    INSERT INTO cegr.observation
        (id, indicator_id, indicator_methodology_version_id,
         geo_entity_id, geo_code_version_id, calendar_period_id,
         value, raw_value, is_imputed, missing_reason,
         unit, comparison_basis, value_type, status,
         source_id, source_location_id, ingestion_run_id,
         extracted_at, extraction_method, confidence, notes)
    VALUES
        ('q6eebc99-0001-4000-8000-000000000005',
         'a2000000-0000-0000-0000-00000000a001', 'a2000000-0000-0000-0000-00000000a002',
         v_geo_entity_id, v_geo_cv_id, 'a2000000-0000-0000-0000-000020240101',
         32193.15, '32193.15', FALSE, NULL,
         '亿元', 'YEAR_OVER_YEAR', 'REAL', 'PUBLISHED',
         v_registry_id, v_loc_id, v_run_id,
         '2026-09-02'::timestamp, 'REGEX_ANCHORED', 1.0,
         'chongqing GDP_ANNUAL 32193.15 亿元;hongheiku 转载;U6 裁定;lineage 三重标注')
    ON CONFLICT (id) DO NOTHING;
    -- observation GDP_GROWTH: 5.7 %
    INSERT INTO cegr.observation
        (id, indicator_id, indicator_methodology_version_id,
         geo_entity_id, geo_code_version_id, calendar_period_id,
         value, raw_value, is_imputed, missing_reason,
         unit, comparison_basis, value_type, status,
         source_id, source_location_id, ingestion_run_id,
         extracted_at, extraction_method, confidence, notes)
    VALUES
        ('q6eebc99-0001-4000-8000-000000000006',
         'a2000000-0000-0000-0000-00000000a003', 'a2000000-0000-0000-0000-00000000a007',
         v_geo_entity_id, v_geo_cv_id, 'a2000000-0000-0000-0000-000020240101',
         5.7, '5.7', FALSE, NULL,
         '%', 'YEAR_OVER_YEAR', 'REAL', 'PUBLISHED',
         v_registry_id, v_loc_id, v_run_id,
         '2026-09-02'::timestamp, 'REGEX_ANCHORED', 1.0,
         'chongqing GDP_GROWTH 5.7 %;hongheiku 转载;U6 裁定;lineage 三重标注')
    ON CONFLICT (id) DO NOTHING;
    -- observation GVA_PRIMARY: 2135.82 亿元
    INSERT INTO cegr.observation
        (id, indicator_id, indicator_methodology_version_id,
         geo_entity_id, geo_code_version_id, calendar_period_id,
         value, raw_value, is_imputed, missing_reason,
         unit, comparison_basis, value_type, status,
         source_id, source_location_id, ingestion_run_id,
         extracted_at, extraction_method, confidence, notes)
    VALUES
        ('q6eebc99-0001-4000-8000-000000000007',
         'a2000000-0000-0000-0000-00000000a004', 'a2000000-0000-0000-0000-00000000a008',
         v_geo_entity_id, v_geo_cv_id, 'a2000000-0000-0000-0000-000020240101',
         2135.82, '2135.82', FALSE, NULL,
         '亿元', 'YEAR_OVER_YEAR', 'REAL', 'PUBLISHED',
         v_registry_id, v_loc_id, v_run_id,
         '2026-09-02'::timestamp, 'REGEX_ANCHORED', 1.0,
         'chongqing GVA_PRIMARY 2135.82 亿元;hongheiku 转载;U6 裁定;lineage 三重标注')
    ON CONFLICT (id) DO NOTHING;
    -- observation GVA_SECONDARY: 11690.68 亿元
    INSERT INTO cegr.observation
        (id, indicator_id, indicator_methodology_version_id,
         geo_entity_id, geo_code_version_id, calendar_period_id,
         value, raw_value, is_imputed, missing_reason,
         unit, comparison_basis, value_type, status,
         source_id, source_location_id, ingestion_run_id,
         extracted_at, extraction_method, confidence, notes)
    VALUES
        ('q6eebc99-0001-4000-8000-000000000008',
         'a2000000-0000-0000-0000-00000000a005', 'a2000000-0000-0000-0000-00000000a009',
         v_geo_entity_id, v_geo_cv_id, 'a2000000-0000-0000-0000-000020240101',
         11690.68, '11690.68', FALSE, NULL,
         '亿元', 'YEAR_OVER_YEAR', 'REAL', 'PUBLISHED',
         v_registry_id, v_loc_id, v_run_id,
         '2026-09-02'::timestamp, 'REGEX_ANCHORED', 1.0,
         'chongqing GVA_SECONDARY 11690.68 亿元;hongheiku 转载;U6 裁定;lineage 三重标注')
    ON CONFLICT (id) DO NOTHING;
    -- observation GVA_TERTIARY: 18366.65 亿元
    INSERT INTO cegr.observation
        (id, indicator_id, indicator_methodology_version_id,
         geo_entity_id, geo_code_version_id, calendar_period_id,
         value, raw_value, is_imputed, missing_reason,
         unit, comparison_basis, value_type, status,
         source_id, source_location_id, ingestion_run_id,
         extracted_at, extraction_method, confidence, notes)
    VALUES
        ('q6eebc99-0001-4000-8000-000000000009',
         'a2000000-0000-0000-0000-00000000a006', 'a2000000-0000-0000-0000-00000000a010',
         v_geo_entity_id, v_geo_cv_id, 'a2000000-0000-0000-0000-000020240101',
         18366.65, '18366.65', FALSE, NULL,
         '亿元', 'YEAR_OVER_YEAR', 'REAL', 'PUBLISHED',
         v_registry_id, v_loc_id, v_run_id,
         '2026-09-02'::timestamp, 'REGEX_ANCHORED', 1.0,
         'chongqing GVA_TERTIARY 18366.65 亿元;hongheiku 转载;U6 裁定;lineage 三重标注')
    ON CONFLICT (id) DO NOTHING;
END $$;

-- Province 03: hebei (河北省, admin_code=13, idx=02)
DO $$
DECLARE
    v_registry_id UUID := 'q0eebc99-0002-4000-8000-000000000002';
    v_doc_id UUID := 'q1eebc99-0002-4000-8000-000000000002';
    v_loc_id UUID := 'q2eebc99-0002-4000-8000-000000000002';
    v_run_id UUID := 'q7eebc99-0002-4000-8000-000000000002';
    v_geo_entity_id UUID := 'a2000000-0000-0000-0000-000000000013';
    v_geo_cv_id UUID := 'a2000000-0000-0000-0000-00000000001301';
BEGIN
    -- 1) source_registry (hongheiku_tjgb, origin=河北省统计局)
    INSERT INTO cegr.source_registry
        (id, domain, organization, category, primary_url,
         update_frequency, auth_note, access_method,
         historical_coverage, stability_note, failure_handling,
         enabled, source_level,
         lineage)
    VALUES
        (v_registry_id, 'tjgb.hongheiku.com',
         'hongheiku 转载 (origin: 河北省统计局)', 'PROVINCIAL_BULLETIN_REPRINT',
         'https://tjgb.hongheiku.com/sjtjgb/59037.html', 'ANNUAL',
         '公开转载;hongheiku 红黑统计公报库;U6 用户裁定接受',
         'HTTP_CURL', '2024 年度公报',
         'U6 金丝雀 5/5 PASS (京/沪/鲁/鄂/川 delta=0 全等)',
         'BLOCKED_NO_POOL 留痕不代换 (红线 14)',
         TRUE, 'S2_REPRINT',
         jsonb_build_object(
             'chain_id', 'real_658_m2_u6_batch_v1'::text,
             'knife', '658',
             'source', 'hongheiku_tjgb',
             'origin', '河北省统计局',
             'ruling', 'U6 2026-09-02',
             'cross_reference', '金丝雀 5/5 全等 (京/沪/鲁/鄂/川)',
             'reprint', TRUE,
             'extraction_method', 'category_first_url_discovery'
         ))
    ON CONFLICT (id) DO NOTHING;

    -- 2) source_document (file SHA 锁转载字节)
    INSERT INTO cegr.source_document
        (id, source_id, file_path, file_size_bytes, file_hash_sha256,
         mime_type, retrieval_method, retrieval_at, raw_content_ref)
    VALUES
        (v_doc_id, v_registry_id,
         '/tmp/_658_hebei.html',
         70033,
         '3975966399dce6165ade6c66e56a43f7fc6fe8047b8c80cac95bcf5d87041ea4',
         'text/html', 'HTTP_CURL',
         '2026-09-02'::timestamp,
         'evidence_pack/u6_batch_26prov_fetch_20260902.json#hebei')
    ON CONFLICT (id) DO NOTHING;

    -- 3) source_location (URL + http_code 200)
    INSERT INTO cegr.source_location
        (id, source_id, location_type, url, http_code,
         accessed_at, content_hash, notes)
    VALUES
        (v_loc_id, v_registry_id, 'PRIMARY_URL',
         'https://tjgb.hongheiku.com/sjtjgb/59037.html', 200,
         '2026-09-02'::timestamp,
         '3975966399dce6165ade6c66e56a43f7fc6fe8047b8c80cac95bcf5d87041ea4',
         'hongheiku 转载页; 2024 年度公报; 1 HTTP (cache hit post-1st)')
    ON CONFLICT (id) DO NOTHING;

    -- 4) ingestion_run (status=SUCCESS, records_inserted=5)
    INSERT INTO cegr.ingestion_run
        (id, source_id, started_at, finished_at,
         records_inserted, records_updated, records_skipped,
         status, error_message, run_kind)
    VALUES
        (v_run_id, v_registry_id,
         '2026-09-02'::timestamp, '2026-09-02'::timestamp,
         5, 0, 0,
         'SUCCESS', NULL,
         'U6_HONGHEIKU_REPRINT_BATCH')
    ON CONFLICT (id) DO NOTHING;
    -- observation GDP_ANNUAL: 47526.9 亿元
    INSERT INTO cegr.observation
        (id, indicator_id, indicator_methodology_version_id,
         geo_entity_id, geo_code_version_id, calendar_period_id,
         value, raw_value, is_imputed, missing_reason,
         unit, comparison_basis, value_type, status,
         source_id, source_location_id, ingestion_run_id,
         extracted_at, extraction_method, confidence, notes)
    VALUES
        ('q6eebc99-0002-4000-8000-000000000010',
         'a2000000-0000-0000-0000-00000000a001', 'a2000000-0000-0000-0000-00000000a002',
         v_geo_entity_id, v_geo_cv_id, 'a2000000-0000-0000-0000-000020240101',
         47526.9, '47526.9', FALSE, NULL,
         '亿元', 'YEAR_OVER_YEAR', 'REAL', 'PUBLISHED',
         v_registry_id, v_loc_id, v_run_id,
         '2026-09-02'::timestamp, 'REGEX_ANCHORED', 1.0,
         'hebei GDP_ANNUAL 47526.9 亿元;hongheiku 转载;U6 裁定;lineage 三重标注')
    ON CONFLICT (id) DO NOTHING;
    -- observation GDP_GROWTH: 5.4 %
    INSERT INTO cegr.observation
        (id, indicator_id, indicator_methodology_version_id,
         geo_entity_id, geo_code_version_id, calendar_period_id,
         value, raw_value, is_imputed, missing_reason,
         unit, comparison_basis, value_type, status,
         source_id, source_location_id, ingestion_run_id,
         extracted_at, extraction_method, confidence, notes)
    VALUES
        ('q6eebc99-0002-4000-8000-000000000011',
         'a2000000-0000-0000-0000-00000000a003', 'a2000000-0000-0000-0000-00000000a007',
         v_geo_entity_id, v_geo_cv_id, 'a2000000-0000-0000-0000-000020240101',
         5.4, '5.4', FALSE, NULL,
         '%', 'YEAR_OVER_YEAR', 'REAL', 'PUBLISHED',
         v_registry_id, v_loc_id, v_run_id,
         '2026-09-02'::timestamp, 'REGEX_ANCHORED', 1.0,
         'hebei GDP_GROWTH 5.4 %;hongheiku 转载;U6 裁定;lineage 三重标注')
    ON CONFLICT (id) DO NOTHING;
    -- observation GVA_PRIMARY: 4522.3 亿元
    INSERT INTO cegr.observation
        (id, indicator_id, indicator_methodology_version_id,
         geo_entity_id, geo_code_version_id, calendar_period_id,
         value, raw_value, is_imputed, missing_reason,
         unit, comparison_basis, value_type, status,
         source_id, source_location_id, ingestion_run_id,
         extracted_at, extraction_method, confidence, notes)
    VALUES
        ('q6eebc99-0002-4000-8000-000000000012',
         'a2000000-0000-0000-0000-00000000a004', 'a2000000-0000-0000-0000-00000000a008',
         v_geo_entity_id, v_geo_cv_id, 'a2000000-0000-0000-0000-000020240101',
         4522.3, '4522.3', FALSE, NULL,
         '亿元', 'YEAR_OVER_YEAR', 'REAL', 'PUBLISHED',
         v_registry_id, v_loc_id, v_run_id,
         '2026-09-02'::timestamp, 'REGEX_ANCHORED', 1.0,
         'hebei GVA_PRIMARY 4522.3 亿元;hongheiku 转载;U6 裁定;lineage 三重标注')
    ON CONFLICT (id) DO NOTHING;
    -- observation GVA_SECONDARY: 17470.5 亿元
    INSERT INTO cegr.observation
        (id, indicator_id, indicator_methodology_version_id,
         geo_entity_id, geo_code_version_id, calendar_period_id,
         value, raw_value, is_imputed, missing_reason,
         unit, comparison_basis, value_type, status,
         source_id, source_location_id, ingestion_run_id,
         extracted_at, extraction_method, confidence, notes)
    VALUES
        ('q6eebc99-0002-4000-8000-000000000013',
         'a2000000-0000-0000-0000-00000000a005', 'a2000000-0000-0000-0000-00000000a009',
         v_geo_entity_id, v_geo_cv_id, 'a2000000-0000-0000-0000-000020240101',
         17470.5, '17470.5', FALSE, NULL,
         '亿元', 'YEAR_OVER_YEAR', 'REAL', 'PUBLISHED',
         v_registry_id, v_loc_id, v_run_id,
         '2026-09-02'::timestamp, 'REGEX_ANCHORED', 1.0,
         'hebei GVA_SECONDARY 17470.5 亿元;hongheiku 转载;U6 裁定;lineage 三重标注')
    ON CONFLICT (id) DO NOTHING;
    -- observation GVA_TERTIARY: 25534.1 亿元
    INSERT INTO cegr.observation
        (id, indicator_id, indicator_methodology_version_id,
         geo_entity_id, geo_code_version_id, calendar_period_id,
         value, raw_value, is_imputed, missing_reason,
         unit, comparison_basis, value_type, status,
         source_id, source_location_id, ingestion_run_id,
         extracted_at, extraction_method, confidence, notes)
    VALUES
        ('q6eebc99-0002-4000-8000-000000000014',
         'a2000000-0000-0000-0000-00000000a006', 'a2000000-0000-0000-0000-00000000a010',
         v_geo_entity_id, v_geo_cv_id, 'a2000000-0000-0000-0000-000020240101',
         25534.1, '25534.1', FALSE, NULL,
         '亿元', 'YEAR_OVER_YEAR', 'REAL', 'PUBLISHED',
         v_registry_id, v_loc_id, v_run_id,
         '2026-09-02'::timestamp, 'REGEX_ANCHORED', 1.0,
         'hebei GVA_TERTIARY 25534.1 亿元;hongheiku 转载;U6 裁定;lineage 三重标注')
    ON CONFLICT (id) DO NOTHING;
END $$;

-- Province 04: shanxi (山西省, admin_code=14, idx=03)
DO $$
DECLARE
    v_registry_id UUID := 'q0eebc99-0003-4000-8000-000000000003';
    v_doc_id UUID := 'q1eebc99-0003-4000-8000-000000000003';
    v_loc_id UUID := 'q2eebc99-0003-4000-8000-000000000003';
    v_run_id UUID := 'q7eebc99-0003-4000-8000-000000000003';
    v_geo_entity_id UUID := 'a2000000-0000-0000-0000-000000000014';
    v_geo_cv_id UUID := 'a2000000-0000-0000-0000-00000000001401';
BEGIN
    -- 1) source_registry (hongheiku_tjgb, origin=山西省统计局)
    INSERT INTO cegr.source_registry
        (id, domain, organization, category, primary_url,
         update_frequency, auth_note, access_method,
         historical_coverage, stability_note, failure_handling,
         enabled, source_level,
         lineage)
    VALUES
        (v_registry_id, 'tjgb.hongheiku.com',
         'hongheiku 转载 (origin: 山西省统计局)', 'PROVINCIAL_BULLETIN_REPRINT',
         'https://tjgb.hongheiku.com/sjtjgb/58259.html', 'ANNUAL',
         '公开转载;hongheiku 红黑统计公报库;U6 用户裁定接受',
         'HTTP_CURL', '2024 年度公报',
         'U6 金丝雀 5/5 PASS (京/沪/鲁/鄂/川 delta=0 全等)',
         'BLOCKED_NO_POOL 留痕不代换 (红线 14)',
         TRUE, 'S2_REPRINT',
         jsonb_build_object(
             'chain_id', 'real_658_m2_u6_batch_v1'::text,
             'knife', '658',
             'source', 'hongheiku_tjgb',
             'origin', '山西省统计局',
             'ruling', 'U6 2026-09-02',
             'cross_reference', '金丝雀 5/5 全等 (京/沪/鲁/鄂/川)',
             'reprint', TRUE,
             'extraction_method', 'category_first_url_discovery'
         ))
    ON CONFLICT (id) DO NOTHING;

    -- 2) source_document (file SHA 锁转载字节)
    INSERT INTO cegr.source_document
        (id, source_id, file_path, file_size_bytes, file_hash_sha256,
         mime_type, retrieval_method, retrieval_at, raw_content_ref)
    VALUES
        (v_doc_id, v_registry_id,
         '/tmp/_658_shanxi.html',
         52537,
         'e2cf59b413f19f7a0581d02ac65c924e91775a726334559bf29d7763ae013108',
         'text/html', 'HTTP_CURL',
         '2026-09-02'::timestamp,
         'evidence_pack/u6_batch_26prov_fetch_20260902.json#shanxi')
    ON CONFLICT (id) DO NOTHING;

    -- 3) source_location (URL + http_code 200)
    INSERT INTO cegr.source_location
        (id, source_id, location_type, url, http_code,
         accessed_at, content_hash, notes)
    VALUES
        (v_loc_id, v_registry_id, 'PRIMARY_URL',
         'https://tjgb.hongheiku.com/sjtjgb/58259.html', 200,
         '2026-09-02'::timestamp,
         'e2cf59b413f19f7a0581d02ac65c924e91775a726334559bf29d7763ae013108',
         'hongheiku 转载页; 2024 年度公报; 1 HTTP (cache hit post-1st)')
    ON CONFLICT (id) DO NOTHING;

    -- 4) ingestion_run (status=SUCCESS, records_inserted=5)
    INSERT INTO cegr.ingestion_run
        (id, source_id, started_at, finished_at,
         records_inserted, records_updated, records_skipped,
         status, error_message, run_kind)
    VALUES
        (v_run_id, v_registry_id,
         '2026-09-02'::timestamp, '2026-09-02'::timestamp,
         5, 0, 0,
         'SUCCESS', NULL,
         'U6_HONGHEIKU_REPRINT_BATCH')
    ON CONFLICT (id) DO NOTHING;
    -- observation GDP_ANNUAL: 25494.69 亿元
    INSERT INTO cegr.observation
        (id, indicator_id, indicator_methodology_version_id,
         geo_entity_id, geo_code_version_id, calendar_period_id,
         value, raw_value, is_imputed, missing_reason,
         unit, comparison_basis, value_type, status,
         source_id, source_location_id, ingestion_run_id,
         extracted_at, extraction_method, confidence, notes)
    VALUES
        ('q6eebc99-0003-4000-8000-000000000015',
         'a2000000-0000-0000-0000-00000000a001', 'a2000000-0000-0000-0000-00000000a002',
         v_geo_entity_id, v_geo_cv_id, 'a2000000-0000-0000-0000-000020240101',
         25494.69, '25494.69', FALSE, NULL,
         '亿元', 'YEAR_OVER_YEAR', 'REAL', 'PUBLISHED',
         v_registry_id, v_loc_id, v_run_id,
         '2026-09-02'::timestamp, 'REGEX_ANCHORED', 1.0,
         'shanxi GDP_ANNUAL 25494.69 亿元;hongheiku 转载;U6 裁定;lineage 三重标注')
    ON CONFLICT (id) DO NOTHING;
    -- observation GDP_GROWTH: 2.3 %
    INSERT INTO cegr.observation
        (id, indicator_id, indicator_methodology_version_id,
         geo_entity_id, geo_code_version_id, calendar_period_id,
         value, raw_value, is_imputed, missing_reason,
         unit, comparison_basis, value_type, status,
         source_id, source_location_id, ingestion_run_id,
         extracted_at, extraction_method, confidence, notes)
    VALUES
        ('q6eebc99-0003-4000-8000-000000000016',
         'a2000000-0000-0000-0000-00000000a003', 'a2000000-0000-0000-0000-00000000a007',
         v_geo_entity_id, v_geo_cv_id, 'a2000000-0000-0000-0000-000020240101',
         2.3, '2.3', FALSE, NULL,
         '%', 'YEAR_OVER_YEAR', 'REAL', 'PUBLISHED',
         v_registry_id, v_loc_id, v_run_id,
         '2026-09-02'::timestamp, 'REGEX_ANCHORED', 1.0,
         'shanxi GDP_GROWTH 2.3 %;hongheiku 转载;U6 裁定;lineage 三重标注')
    ON CONFLICT (id) DO NOTHING;
    -- observation GVA_PRIMARY: 1392.48 亿元
    INSERT INTO cegr.observation
        (id, indicator_id, indicator_methodology_version_id,
         geo_entity_id, geo_code_version_id, calendar_period_id,
         value, raw_value, is_imputed, missing_reason,
         unit, comparison_basis, value_type, status,
         source_id, source_location_id, ingestion_run_id,
         extracted_at, extraction_method, confidence, notes)
    VALUES
        ('q6eebc99-0003-4000-8000-000000000017',
         'a2000000-0000-0000-0000-00000000a004', 'a2000000-0000-0000-0000-00000000a008',
         v_geo_entity_id, v_geo_cv_id, 'a2000000-0000-0000-0000-000020240101',
         1392.48, '1392.48', FALSE, NULL,
         '亿元', 'YEAR_OVER_YEAR', 'REAL', 'PUBLISHED',
         v_registry_id, v_loc_id, v_run_id,
         '2026-09-02'::timestamp, 'REGEX_ANCHORED', 1.0,
         'shanxi GVA_PRIMARY 1392.48 亿元;hongheiku 转载;U6 裁定;lineage 三重标注')
    ON CONFLICT (id) DO NOTHING;
    -- observation GVA_SECONDARY: 11021.46 亿元
    INSERT INTO cegr.observation
        (id, indicator_id, indicator_methodology_version_id,
         geo_entity_id, geo_code_version_id, calendar_period_id,
         value, raw_value, is_imputed, missing_reason,
         unit, comparison_basis, value_type, status,
         source_id, source_location_id, ingestion_run_id,
         extracted_at, extraction_method, confidence, notes)
    VALUES
        ('q6eebc99-0003-4000-8000-000000000018',
         'a2000000-0000-0000-0000-00000000a005', 'a2000000-0000-0000-0000-00000000a009',
         v_geo_entity_id, v_geo_cv_id, 'a2000000-0000-0000-0000-000020240101',
         11021.46, '11021.46', FALSE, NULL,
         '亿元', 'YEAR_OVER_YEAR', 'REAL', 'PUBLISHED',
         v_registry_id, v_loc_id, v_run_id,
         '2026-09-02'::timestamp, 'REGEX_ANCHORED', 1.0,
         'shanxi GVA_SECONDARY 11021.46 亿元;hongheiku 转载;U6 裁定;lineage 三重标注')
    ON CONFLICT (id) DO NOTHING;
    -- observation GVA_TERTIARY: 13080.74 亿元
    INSERT INTO cegr.observation
        (id, indicator_id, indicator_methodology_version_id,
         geo_entity_id, geo_code_version_id, calendar_period_id,
         value, raw_value, is_imputed, missing_reason,
         unit, comparison_basis, value_type, status,
         source_id, source_location_id, ingestion_run_id,
         extracted_at, extraction_method, confidence, notes)
    VALUES
        ('q6eebc99-0003-4000-8000-000000000019',
         'a2000000-0000-0000-0000-00000000a006', 'a2000000-0000-0000-0000-00000000a010',
         v_geo_entity_id, v_geo_cv_id, 'a2000000-0000-0000-0000-000020240101',
         13080.74, '13080.74', FALSE, NULL,
         '亿元', 'YEAR_OVER_YEAR', 'REAL', 'PUBLISHED',
         v_registry_id, v_loc_id, v_run_id,
         '2026-09-02'::timestamp, 'REGEX_ANCHORED', 1.0,
         'shanxi GVA_TERTIARY 13080.74 亿元;hongheiku 转载;U6 裁定;lineage 三重标注')
    ON CONFLICT (id) DO NOTHING;
END $$;

-- Province 05: neimenggu (内蒙古自治区, admin_code=15, idx=04)
DO $$
DECLARE
    v_registry_id UUID := 'q0eebc99-0004-4000-8000-000000000004';
    v_doc_id UUID := 'q1eebc99-0004-4000-8000-000000000004';
    v_loc_id UUID := 'q2eebc99-0004-4000-8000-000000000004';
    v_run_id UUID := 'q7eebc99-0004-4000-8000-000000000004';
    v_geo_entity_id UUID := 'a2000000-0000-0000-0000-000000000015';
    v_geo_cv_id UUID := 'a2000000-0000-0000-0000-00000000001501';
BEGIN
    -- 1) source_registry (hongheiku_tjgb, origin=内蒙古自治区统计局)
    INSERT INTO cegr.source_registry
        (id, domain, organization, category, primary_url,
         update_frequency, auth_note, access_method,
         historical_coverage, stability_note, failure_handling,
         enabled, source_level,
         lineage)
    VALUES
        (v_registry_id, 'tjgb.hongheiku.com',
         'hongheiku 转载 (origin: 内蒙古自治区统计局)', 'PROVINCIAL_BULLETIN_REPRINT',
         'https://tjgb.hongheiku.com/sjtjgb/58092.html', 'ANNUAL',
         '公开转载;hongheiku 红黑统计公报库;U6 用户裁定接受',
         'HTTP_CURL', '2024 年度公报',
         'U6 金丝雀 5/5 PASS (京/沪/鲁/鄂/川 delta=0 全等)',
         'BLOCKED_NO_POOL 留痕不代换 (红线 14)',
         TRUE, 'S2_REPRINT',
         jsonb_build_object(
             'chain_id', 'real_658_m2_u6_batch_v1'::text,
             'knife', '658',
             'source', 'hongheiku_tjgb',
             'origin', '内蒙古自治区统计局',
             'ruling', 'U6 2026-09-02',
             'cross_reference', '金丝雀 5/5 全等 (京/沪/鲁/鄂/川)',
             'reprint', TRUE,
             'extraction_method', 'category_first_url_discovery'
         ))
    ON CONFLICT (id) DO NOTHING;

    -- 2) source_document (file SHA 锁转载字节)
    INSERT INTO cegr.source_document
        (id, source_id, file_path, file_size_bytes, file_hash_sha256,
         mime_type, retrieval_method, retrieval_at, raw_content_ref)
    VALUES
        (v_doc_id, v_registry_id,
         '/tmp/_658_neimenggu.html',
         77530,
         '247d186af392a6093e44f586b07ea2f002f3543fba0e60f342c8e06c41773d96',
         'text/html', 'HTTP_CURL',
         '2026-09-02'::timestamp,
         'evidence_pack/u6_batch_26prov_fetch_20260902.json#neimenggu')
    ON CONFLICT (id) DO NOTHING;

    -- 3) source_location (URL + http_code 200)
    INSERT INTO cegr.source_location
        (id, source_id, location_type, url, http_code,
         accessed_at, content_hash, notes)
    VALUES
        (v_loc_id, v_registry_id, 'PRIMARY_URL',
         'https://tjgb.hongheiku.com/sjtjgb/58092.html', 200,
         '2026-09-02'::timestamp,
         '247d186af392a6093e44f586b07ea2f002f3543fba0e60f342c8e06c41773d96',
         'hongheiku 转载页; 2024 年度公报; 1 HTTP (cache hit post-1st)')
    ON CONFLICT (id) DO NOTHING;

    -- 4) ingestion_run (status=SUCCESS, records_inserted=5)
    INSERT INTO cegr.ingestion_run
        (id, source_id, started_at, finished_at,
         records_inserted, records_updated, records_skipped,
         status, error_message, run_kind)
    VALUES
        (v_run_id, v_registry_id,
         '2026-09-02'::timestamp, '2026-09-02'::timestamp,
         5, 0, 0,
         'SUCCESS', NULL,
         'U6_HONGHEIKU_REPRINT_BATCH')
    ON CONFLICT (id) DO NOTHING;
    -- observation GDP_ANNUAL: 26314.6 亿元
    INSERT INTO cegr.observation
        (id, indicator_id, indicator_methodology_version_id,
         geo_entity_id, geo_code_version_id, calendar_period_id,
         value, raw_value, is_imputed, missing_reason,
         unit, comparison_basis, value_type, status,
         source_id, source_location_id, ingestion_run_id,
         extracted_at, extraction_method, confidence, notes)
    VALUES
        ('q6eebc99-0004-4000-8000-000000000020',
         'a2000000-0000-0000-0000-00000000a001', 'a2000000-0000-0000-0000-00000000a002',
         v_geo_entity_id, v_geo_cv_id, 'a2000000-0000-0000-0000-000020240101',
         26314.6, '26314.6', FALSE, NULL,
         '亿元', 'YEAR_OVER_YEAR', 'REAL', 'PUBLISHED',
         v_registry_id, v_loc_id, v_run_id,
         '2026-09-02'::timestamp, 'REGEX_ANCHORED', 1.0,
         'neimenggu GDP_ANNUAL 26314.6 亿元;hongheiku 转载;U6 裁定;lineage 三重标注')
    ON CONFLICT (id) DO NOTHING;
    -- observation GDP_GROWTH: 5.8 %
    INSERT INTO cegr.observation
        (id, indicator_id, indicator_methodology_version_id,
         geo_entity_id, geo_code_version_id, calendar_period_id,
         value, raw_value, is_imputed, missing_reason,
         unit, comparison_basis, value_type, status,
         source_id, source_location_id, ingestion_run_id,
         extracted_at, extraction_method, confidence, notes)
    VALUES
        ('q6eebc99-0004-4000-8000-000000000021',
         'a2000000-0000-0000-0000-00000000a003', 'a2000000-0000-0000-0000-00000000a007',
         v_geo_entity_id, v_geo_cv_id, 'a2000000-0000-0000-0000-000020240101',
         5.8, '5.8', FALSE, NULL,
         '%', 'YEAR_OVER_YEAR', 'REAL', 'PUBLISHED',
         v_registry_id, v_loc_id, v_run_id,
         '2026-09-02'::timestamp, 'REGEX_ANCHORED', 1.0,
         'neimenggu GDP_GROWTH 5.8 %;hongheiku 转载;U6 裁定;lineage 三重标注')
    ON CONFLICT (id) DO NOTHING;
    -- observation GVA_PRIMARY: 2872.6 亿元
    INSERT INTO cegr.observation
        (id, indicator_id, indicator_methodology_version_id,
         geo_entity_id, geo_code_version_id, calendar_period_id,
         value, raw_value, is_imputed, missing_reason,
         unit, comparison_basis, value_type, status,
         source_id, source_location_id, ingestion_run_id,
         extracted_at, extraction_method, confidence, notes)
    VALUES
        ('q6eebc99-0004-4000-8000-000000000022',
         'a2000000-0000-0000-0000-00000000a004', 'a2000000-0000-0000-0000-00000000a008',
         v_geo_entity_id, v_geo_cv_id, 'a2000000-0000-0000-0000-000020240101',
         2872.6, '2872.6', FALSE, NULL,
         '亿元', 'YEAR_OVER_YEAR', 'REAL', 'PUBLISHED',
         v_registry_id, v_loc_id, v_run_id,
         '2026-09-02'::timestamp, 'REGEX_ANCHORED', 1.0,
         'neimenggu GVA_PRIMARY 2872.6 亿元;hongheiku 转载;U6 裁定;lineage 三重标注')
    ON CONFLICT (id) DO NOTHING;
    -- observation GVA_SECONDARY: 11604.4 亿元
    INSERT INTO cegr.observation
        (id, indicator_id, indicator_methodology_version_id,
         geo_entity_id, geo_code_version_id, calendar_period_id,
         value, raw_value, is_imputed, missing_reason,
         unit, comparison_basis, value_type, status,
         source_id, source_location_id, ingestion_run_id,
         extracted_at, extraction_method, confidence, notes)
    VALUES
        ('q6eebc99-0004-4000-8000-000000000023',
         'a2000000-0000-0000-0000-00000000a005', 'a2000000-0000-0000-0000-00000000a009',
         v_geo_entity_id, v_geo_cv_id, 'a2000000-0000-0000-0000-000020240101',
         11604.4, '11604.4', FALSE, NULL,
         '亿元', 'YEAR_OVER_YEAR', 'REAL', 'PUBLISHED',
         v_registry_id, v_loc_id, v_run_id,
         '2026-09-02'::timestamp, 'REGEX_ANCHORED', 1.0,
         'neimenggu GVA_SECONDARY 11604.4 亿元;hongheiku 转载;U6 裁定;lineage 三重标注')
    ON CONFLICT (id) DO NOTHING;
    -- observation GVA_TERTIARY: 11837.6 亿元
    INSERT INTO cegr.observation
        (id, indicator_id, indicator_methodology_version_id,
         geo_entity_id, geo_code_version_id, calendar_period_id,
         value, raw_value, is_imputed, missing_reason,
         unit, comparison_basis, value_type, status,
         source_id, source_location_id, ingestion_run_id,
         extracted_at, extraction_method, confidence, notes)
    VALUES
        ('q6eebc99-0004-4000-8000-000000000024',
         'a2000000-0000-0000-0000-00000000a006', 'a2000000-0000-0000-0000-00000000a010',
         v_geo_entity_id, v_geo_cv_id, 'a2000000-0000-0000-0000-000020240101',
         11837.6, '11837.6', FALSE, NULL,
         '亿元', 'YEAR_OVER_YEAR', 'REAL', 'PUBLISHED',
         v_registry_id, v_loc_id, v_run_id,
         '2026-09-02'::timestamp, 'REGEX_ANCHORED', 1.0,
         'neimenggu GVA_TERTIARY 11837.6 亿元;hongheiku 转载;U6 裁定;lineage 三重标注')
    ON CONFLICT (id) DO NOTHING;
END $$;

-- Province 06: jilin (吉林省, admin_code=22, idx=05)
DO $$
DECLARE
    v_registry_id UUID := 'q0eebc99-0005-4000-8000-000000000005';
    v_doc_id UUID := 'q1eebc99-0005-4000-8000-000000000005';
    v_loc_id UUID := 'q2eebc99-0005-4000-8000-000000000005';
    v_run_id UUID := 'q7eebc99-0005-4000-8000-000000000005';
    v_geo_entity_id UUID := 'a2000000-0000-0000-0000-000000000022';
    v_geo_cv_id UUID := 'a2000000-0000-0000-0000-00000000002201';
BEGIN
    -- 1) source_registry (hongheiku_tjgb, origin=吉林省统计局)
    INSERT INTO cegr.source_registry
        (id, domain, organization, category, primary_url,
         update_frequency, auth_note, access_method,
         historical_coverage, stability_note, failure_handling,
         enabled, source_level,
         lineage)
    VALUES
        (v_registry_id, 'tjgb.hongheiku.com',
         'hongheiku 转载 (origin: 吉林省统计局)', 'PROVINCIAL_BULLETIN_REPRINT',
         'https://tjgb.hongheiku.com/sjtjgb/57522.html', 'ANNUAL',
         '公开转载;hongheiku 红黑统计公报库;U6 用户裁定接受',
         'HTTP_CURL', '2024 年度公报',
         'U6 金丝雀 5/5 PASS (京/沪/鲁/鄂/川 delta=0 全等)',
         'BLOCKED_NO_POOL 留痕不代换 (红线 14)',
         TRUE, 'S2_REPRINT',
         jsonb_build_object(
             'chain_id', 'real_658_m2_u6_batch_v1'::text,
             'knife', '658',
             'source', 'hongheiku_tjgb',
             'origin', '吉林省统计局',
             'ruling', 'U6 2026-09-02',
             'cross_reference', '金丝雀 5/5 全等 (京/沪/鲁/鄂/川)',
             'reprint', TRUE,
             'extraction_method', 'category_first_url_discovery'
         ))
    ON CONFLICT (id) DO NOTHING;

    -- 2) source_document (file SHA 锁转载字节)
    INSERT INTO cegr.source_document
        (id, source_id, file_path, file_size_bytes, file_hash_sha256,
         mime_type, retrieval_method, retrieval_at, raw_content_ref)
    VALUES
        (v_doc_id, v_registry_id,
         '/tmp/_658_jilin.html',
         74298,
         'b07493e2e6a409f32033289f0f6ea5274be34595042c51311fef9d046d80d205',
         'text/html', 'HTTP_CURL',
         '2026-09-02'::timestamp,
         'evidence_pack/u6_batch_26prov_fetch_20260902.json#jilin')
    ON CONFLICT (id) DO NOTHING;

    -- 3) source_location (URL + http_code 200)
    INSERT INTO cegr.source_location
        (id, source_id, location_type, url, http_code,
         accessed_at, content_hash, notes)
    VALUES
        (v_loc_id, v_registry_id, 'PRIMARY_URL',
         'https://tjgb.hongheiku.com/sjtjgb/57522.html', 200,
         '2026-09-02'::timestamp,
         'b07493e2e6a409f32033289f0f6ea5274be34595042c51311fef9d046d80d205',
         'hongheiku 转载页; 2024 年度公报; 1 HTTP (cache hit post-1st)')
    ON CONFLICT (id) DO NOTHING;

    -- 4) ingestion_run (status=SUCCESS, records_inserted=5)
    INSERT INTO cegr.ingestion_run
        (id, source_id, started_at, finished_at,
         records_inserted, records_updated, records_skipped,
         status, error_message, run_kind)
    VALUES
        (v_run_id, v_registry_id,
         '2026-09-02'::timestamp, '2026-09-02'::timestamp,
         5, 0, 0,
         'SUCCESS', NULL,
         'U6_HONGHEIKU_REPRINT_BATCH')
    ON CONFLICT (id) DO NOTHING;
    -- observation GDP_ANNUAL: 14361.22 亿元
    INSERT INTO cegr.observation
        (id, indicator_id, indicator_methodology_version_id,
         geo_entity_id, geo_code_version_id, calendar_period_id,
         value, raw_value, is_imputed, missing_reason,
         unit, comparison_basis, value_type, status,
         source_id, source_location_id, ingestion_run_id,
         extracted_at, extraction_method, confidence, notes)
    VALUES
        ('q6eebc99-0005-4000-8000-000000000025',
         'a2000000-0000-0000-0000-00000000a001', 'a2000000-0000-0000-0000-00000000a002',
         v_geo_entity_id, v_geo_cv_id, 'a2000000-0000-0000-0000-000020240101',
         14361.22, '14361.22', FALSE, NULL,
         '亿元', 'YEAR_OVER_YEAR', 'REAL', 'PUBLISHED',
         v_registry_id, v_loc_id, v_run_id,
         '2026-09-02'::timestamp, 'REGEX_ANCHORED', 1.0,
         'jilin GDP_ANNUAL 14361.22 亿元;hongheiku 转载;U6 裁定;lineage 三重标注')
    ON CONFLICT (id) DO NOTHING;
    -- observation GDP_GROWTH: 4.3 %
    INSERT INTO cegr.observation
        (id, indicator_id, indicator_methodology_version_id,
         geo_entity_id, geo_code_version_id, calendar_period_id,
         value, raw_value, is_imputed, missing_reason,
         unit, comparison_basis, value_type, status,
         source_id, source_location_id, ingestion_run_id,
         extracted_at, extraction_method, confidence, notes)
    VALUES
        ('q6eebc99-0005-4000-8000-000000000026',
         'a2000000-0000-0000-0000-00000000a003', 'a2000000-0000-0000-0000-00000000a007',
         v_geo_entity_id, v_geo_cv_id, 'a2000000-0000-0000-0000-000020240101',
         4.3, '4.3', FALSE, NULL,
         '%', 'YEAR_OVER_YEAR', 'REAL', 'PUBLISHED',
         v_registry_id, v_loc_id, v_run_id,
         '2026-09-02'::timestamp, 'REGEX_ANCHORED', 1.0,
         'jilin GDP_GROWTH 4.3 %;hongheiku 转载;U6 裁定;lineage 三重标注')
    ON CONFLICT (id) DO NOTHING;
    -- observation GVA_PRIMARY: 1589.8 亿元
    INSERT INTO cegr.observation
        (id, indicator_id, indicator_methodology_version_id,
         geo_entity_id, geo_code_version_id, calendar_period_id,
         value, raw_value, is_imputed, missing_reason,
         unit, comparison_basis, value_type, status,
         source_id, source_location_id, ingestion_run_id,
         extracted_at, extraction_method, confidence, notes)
    VALUES
        ('q6eebc99-0005-4000-8000-000000000027',
         'a2000000-0000-0000-0000-00000000a004', 'a2000000-0000-0000-0000-00000000a008',
         v_geo_entity_id, v_geo_cv_id, 'a2000000-0000-0000-0000-000020240101',
         1589.8, '1589.8', FALSE, NULL,
         '亿元', 'YEAR_OVER_YEAR', 'REAL', 'PUBLISHED',
         v_registry_id, v_loc_id, v_run_id,
         '2026-09-02'::timestamp, 'REGEX_ANCHORED', 1.0,
         'jilin GVA_PRIMARY 1589.8 亿元;hongheiku 转载;U6 裁定;lineage 三重标注')
    ON CONFLICT (id) DO NOTHING;
    -- observation GVA_SECONDARY: 4577.64 亿元
    INSERT INTO cegr.observation
        (id, indicator_id, indicator_methodology_version_id,
         geo_entity_id, geo_code_version_id, calendar_period_id,
         value, raw_value, is_imputed, missing_reason,
         unit, comparison_basis, value_type, status,
         source_id, source_location_id, ingestion_run_id,
         extracted_at, extraction_method, confidence, notes)
    VALUES
        ('q6eebc99-0005-4000-8000-000000000028',
         'a2000000-0000-0000-0000-00000000a005', 'a2000000-0000-0000-0000-00000000a009',
         v_geo_entity_id, v_geo_cv_id, 'a2000000-0000-0000-0000-000020240101',
         4577.64, '4577.64', FALSE, NULL,
         '亿元', 'YEAR_OVER_YEAR', 'REAL', 'PUBLISHED',
         v_registry_id, v_loc_id, v_run_id,
         '2026-09-02'::timestamp, 'REGEX_ANCHORED', 1.0,
         'jilin GVA_SECONDARY 4577.64 亿元;hongheiku 转载;U6 裁定;lineage 三重标注')
    ON CONFLICT (id) DO NOTHING;
    -- observation GVA_TERTIARY: 8193.79 亿元
    INSERT INTO cegr.observation
        (id, indicator_id, indicator_methodology_version_id,
         geo_entity_id, geo_code_version_id, calendar_period_id,
         value, raw_value, is_imputed, missing_reason,
         unit, comparison_basis, value_type, status,
         source_id, source_location_id, ingestion_run_id,
         extracted_at, extraction_method, confidence, notes)
    VALUES
        ('q6eebc99-0005-4000-8000-000000000029',
         'a2000000-0000-0000-0000-00000000a006', 'a2000000-0000-0000-0000-00000000a010',
         v_geo_entity_id, v_geo_cv_id, 'a2000000-0000-0000-0000-000020240101',
         8193.79, '8193.79', FALSE, NULL,
         '亿元', 'YEAR_OVER_YEAR', 'REAL', 'PUBLISHED',
         v_registry_id, v_loc_id, v_run_id,
         '2026-09-02'::timestamp, 'REGEX_ANCHORED', 1.0,
         'jilin GVA_TERTIARY 8193.79 亿元;hongheiku 转载;U6 裁定;lineage 三重标注')
    ON CONFLICT (id) DO NOTHING;
END $$;

-- Province 07: heilongjiang (黑龙江省, admin_code=23, idx=06)
DO $$
DECLARE
    v_registry_id UUID := 'q0eebc99-0006-4000-8000-000000000006';
    v_doc_id UUID := 'q1eebc99-0006-4000-8000-000000000006';
    v_loc_id UUID := 'q2eebc99-0006-4000-8000-000000000006';
    v_run_id UUID := 'q7eebc99-0006-4000-8000-000000000006';
    v_geo_entity_id UUID := 'a2000000-0000-0000-0000-000000000023';
    v_geo_cv_id UUID := 'a2000000-0000-0000-0000-00000000002301';
BEGIN
    -- 1) source_registry (hongheiku_tjgb, origin=黑龙江省统计局)
    INSERT INTO cegr.source_registry
        (id, domain, organization, category, primary_url,
         update_frequency, auth_note, access_method,
         historical_coverage, stability_note, failure_handling,
         enabled, source_level,
         lineage)
    VALUES
        (v_registry_id, 'tjgb.hongheiku.com',
         'hongheiku 转载 (origin: 黑龙江省统计局)', 'PROVINCIAL_BULLETIN_REPRINT',
         'https://tjgb.hongheiku.com/sjtjgb/59289.html', 'ANNUAL',
         '公开转载;hongheiku 红黑统计公报库;U6 用户裁定接受',
         'HTTP_CURL', '2024 年度公报',
         'U6 金丝雀 5/5 PASS (京/沪/鲁/鄂/川 delta=0 全等)',
         'BLOCKED_NO_POOL 留痕不代换 (红线 14)',
         TRUE, 'S2_REPRINT',
         jsonb_build_object(
             'chain_id', 'real_658_m2_u6_batch_v1'::text,
             'knife', '658',
             'source', 'hongheiku_tjgb',
             'origin', '黑龙江省统计局',
             'ruling', 'U6 2026-09-02',
             'cross_reference', '金丝雀 5/5 全等 (京/沪/鲁/鄂/川)',
             'reprint', TRUE,
             'extraction_method', 'category_first_url_discovery'
         ))
    ON CONFLICT (id) DO NOTHING;

    -- 2) source_document (file SHA 锁转载字节)
    INSERT INTO cegr.source_document
        (id, source_id, file_path, file_size_bytes, file_hash_sha256,
         mime_type, retrieval_method, retrieval_at, raw_content_ref)
    VALUES
        (v_doc_id, v_registry_id,
         '/tmp/_658_heilongjiang.html',
         63010,
         '14cd553dbfa2d2fe2e59132e4e3ea4f0e2dfc40923888edb656256b0a7003b0f',
         'text/html', 'HTTP_CURL',
         '2026-09-02'::timestamp,
         'evidence_pack/u6_batch_26prov_fetch_20260902.json#heilongjiang')
    ON CONFLICT (id) DO NOTHING;

    -- 3) source_location (URL + http_code 200)
    INSERT INTO cegr.source_location
        (id, source_id, location_type, url, http_code,
         accessed_at, content_hash, notes)
    VALUES
        (v_loc_id, v_registry_id, 'PRIMARY_URL',
         'https://tjgb.hongheiku.com/sjtjgb/59289.html', 200,
         '2026-09-02'::timestamp,
         '14cd553dbfa2d2fe2e59132e4e3ea4f0e2dfc40923888edb656256b0a7003b0f',
         'hongheiku 转载页; 2024 年度公报; 1 HTTP (cache hit post-1st)')
    ON CONFLICT (id) DO NOTHING;

    -- 4) ingestion_run (status=SUCCESS, records_inserted=5)
    INSERT INTO cegr.ingestion_run
        (id, source_id, started_at, finished_at,
         records_inserted, records_updated, records_skipped,
         status, error_message, run_kind)
    VALUES
        (v_run_id, v_registry_id,
         '2026-09-02'::timestamp, '2026-09-02'::timestamp,
         5, 0, 0,
         'SUCCESS', NULL,
         'U6_HONGHEIKU_REPRINT_BATCH')
    ON CONFLICT (id) DO NOTHING;
    -- observation GDP_ANNUAL: 16476.9 亿元
    INSERT INTO cegr.observation
        (id, indicator_id, indicator_methodology_version_id,
         geo_entity_id, geo_code_version_id, calendar_period_id,
         value, raw_value, is_imputed, missing_reason,
         unit, comparison_basis, value_type, status,
         source_id, source_location_id, ingestion_run_id,
         extracted_at, extraction_method, confidence, notes)
    VALUES
        ('q6eebc99-0006-4000-8000-000000000030',
         'a2000000-0000-0000-0000-00000000a001', 'a2000000-0000-0000-0000-00000000a002',
         v_geo_entity_id, v_geo_cv_id, 'a2000000-0000-0000-0000-000020240101',
         16476.9, '16476.9', FALSE, NULL,
         '亿元', 'YEAR_OVER_YEAR', 'REAL', 'PUBLISHED',
         v_registry_id, v_loc_id, v_run_id,
         '2026-09-02'::timestamp, 'REGEX_ANCHORED', 1.0,
         'heilongjiang GDP_ANNUAL 16476.9 亿元;hongheiku 转载;U6 裁定;lineage 三重标注')
    ON CONFLICT (id) DO NOTHING;
    -- observation GDP_GROWTH: 3.2 %
    INSERT INTO cegr.observation
        (id, indicator_id, indicator_methodology_version_id,
         geo_entity_id, geo_code_version_id, calendar_period_id,
         value, raw_value, is_imputed, missing_reason,
         unit, comparison_basis, value_type, status,
         source_id, source_location_id, ingestion_run_id,
         extracted_at, extraction_method, confidence, notes)
    VALUES
        ('q6eebc99-0006-4000-8000-000000000031',
         'a2000000-0000-0000-0000-00000000a003', 'a2000000-0000-0000-0000-00000000a007',
         v_geo_entity_id, v_geo_cv_id, 'a2000000-0000-0000-0000-000020240101',
         3.2, '3.2', FALSE, NULL,
         '%', 'YEAR_OVER_YEAR', 'REAL', 'PUBLISHED',
         v_registry_id, v_loc_id, v_run_id,
         '2026-09-02'::timestamp, 'REGEX_ANCHORED', 1.0,
         'heilongjiang GDP_GROWTH 3.2 %;hongheiku 转载;U6 裁定;lineage 三重标注')
    ON CONFLICT (id) DO NOTHING;
    -- observation GVA_PRIMARY: 3203.3 亿元
    INSERT INTO cegr.observation
        (id, indicator_id, indicator_methodology_version_id,
         geo_entity_id, geo_code_version_id, calendar_period_id,
         value, raw_value, is_imputed, missing_reason,
         unit, comparison_basis, value_type, status,
         source_id, source_location_id, ingestion_run_id,
         extracted_at, extraction_method, confidence, notes)
    VALUES
        ('q6eebc99-0006-4000-8000-000000000032',
         'a2000000-0000-0000-0000-00000000a004', 'a2000000-0000-0000-0000-00000000a008',
         v_geo_entity_id, v_geo_cv_id, 'a2000000-0000-0000-0000-000020240101',
         3203.3, '3203.3', FALSE, NULL,
         '亿元', 'YEAR_OVER_YEAR', 'REAL', 'PUBLISHED',
         v_registry_id, v_loc_id, v_run_id,
         '2026-09-02'::timestamp, 'REGEX_ANCHORED', 1.0,
         'heilongjiang GVA_PRIMARY 3203.3 亿元;hongheiku 转载;U6 裁定;lineage 三重标注')
    ON CONFLICT (id) DO NOTHING;
    -- observation GVA_SECONDARY: 4147.3 亿元
    INSERT INTO cegr.observation
        (id, indicator_id, indicator_methodology_version_id,
         geo_entity_id, geo_code_version_id, calendar_period_id,
         value, raw_value, is_imputed, missing_reason,
         unit, comparison_basis, value_type, status,
         source_id, source_location_id, ingestion_run_id,
         extracted_at, extraction_method, confidence, notes)
    VALUES
        ('q6eebc99-0006-4000-8000-000000000033',
         'a2000000-0000-0000-0000-00000000a005', 'a2000000-0000-0000-0000-00000000a009',
         v_geo_entity_id, v_geo_cv_id, 'a2000000-0000-0000-0000-000020240101',
         4147.3, '4147.3', FALSE, NULL,
         '亿元', 'YEAR_OVER_YEAR', 'REAL', 'PUBLISHED',
         v_registry_id, v_loc_id, v_run_id,
         '2026-09-02'::timestamp, 'REGEX_ANCHORED', 1.0,
         'heilongjiang GVA_SECONDARY 4147.3 亿元;hongheiku 转载;U6 裁定;lineage 三重标注')
    ON CONFLICT (id) DO NOTHING;
    -- observation GVA_TERTIARY: 9126.2 亿元
    INSERT INTO cegr.observation
        (id, indicator_id, indicator_methodology_version_id,
         geo_entity_id, geo_code_version_id, calendar_period_id,
         value, raw_value, is_imputed, missing_reason,
         unit, comparison_basis, value_type, status,
         source_id, source_location_id, ingestion_run_id,
         extracted_at, extraction_method, confidence, notes)
    VALUES
        ('q6eebc99-0006-4000-8000-000000000034',
         'a2000000-0000-0000-0000-00000000a006', 'a2000000-0000-0000-0000-00000000a010',
         v_geo_entity_id, v_geo_cv_id, 'a2000000-0000-0000-0000-000020240101',
         9126.2, '9126.2', FALSE, NULL,
         '亿元', 'YEAR_OVER_YEAR', 'REAL', 'PUBLISHED',
         v_registry_id, v_loc_id, v_run_id,
         '2026-09-02'::timestamp, 'REGEX_ANCHORED', 1.0,
         'heilongjiang GVA_TERTIARY 9126.2 亿元;hongheiku 转载;U6 裁定;lineage 三重标注')
    ON CONFLICT (id) DO NOTHING;
END $$;

-- Province 08: jiangsu (江苏省, admin_code=32, idx=07)
DO $$
DECLARE
    v_registry_id UUID := 'q0eebc99-0007-4000-8000-000000000007';
    v_doc_id UUID := 'q1eebc99-0007-4000-8000-000000000007';
    v_loc_id UUID := 'q2eebc99-0007-4000-8000-000000000007';
    v_run_id UUID := 'q7eebc99-0007-4000-8000-000000000007';
    v_geo_entity_id UUID := 'a2000000-0000-0000-0000-000000000032';
    v_geo_cv_id UUID := 'a2000000-0000-0000-0000-00000000003201';
BEGIN
    -- 1) source_registry (hongheiku_tjgb, origin=江苏省统计局)
    INSERT INTO cegr.source_registry
        (id, domain, organization, category, primary_url,
         update_frequency, auth_note, access_method,
         historical_coverage, stability_note, failure_handling,
         enabled, source_level,
         lineage)
    VALUES
        (v_registry_id, 'tjgb.hongheiku.com',
         'hongheiku 转载 (origin: 江苏省统计局)', 'PROVINCIAL_BULLETIN_REPRINT',
         'https://tjgb.hongheiku.com/sjtjgb/57215.html', 'ANNUAL',
         '公开转载;hongheiku 红黑统计公报库;U6 用户裁定接受',
         'HTTP_CURL', '2024 年度公报',
         'U6 金丝雀 5/5 PASS (京/沪/鲁/鄂/川 delta=0 全等)',
         'BLOCKED_NO_POOL 留痕不代换 (红线 14)',
         TRUE, 'S2_REPRINT',
         jsonb_build_object(
             'chain_id', 'real_658_m2_u6_batch_v1'::text,
             'knife', '658',
             'source', 'hongheiku_tjgb',
             'origin', '江苏省统计局',
             'ruling', 'U6 2026-09-02',
             'cross_reference', '金丝雀 5/5 全等 (京/沪/鲁/鄂/川)',
             'reprint', TRUE,
             'extraction_method', 'category_first_url_discovery'
         ))
    ON CONFLICT (id) DO NOTHING;

    -- 2) source_document (file SHA 锁转载字节)
    INSERT INTO cegr.source_document
        (id, source_id, file_path, file_size_bytes, file_hash_sha256,
         mime_type, retrieval_method, retrieval_at, raw_content_ref)
    VALUES
        (v_doc_id, v_registry_id,
         '/tmp/_658_jiangsu.html',
         54990,
         '9cc5dc427701b650a9874ea5e1aa1af9367e527b788c791cd53eea336a4d9d48',
         'text/html', 'HTTP_CURL',
         '2026-09-02'::timestamp,
         'evidence_pack/u6_batch_26prov_fetch_20260902.json#jiangsu')
    ON CONFLICT (id) DO NOTHING;

    -- 3) source_location (URL + http_code 200)
    INSERT INTO cegr.source_location
        (id, source_id, location_type, url, http_code,
         accessed_at, content_hash, notes)
    VALUES
        (v_loc_id, v_registry_id, 'PRIMARY_URL',
         'https://tjgb.hongheiku.com/sjtjgb/57215.html', 200,
         '2026-09-02'::timestamp,
         '9cc5dc427701b650a9874ea5e1aa1af9367e527b788c791cd53eea336a4d9d48',
         'hongheiku 转载页; 2024 年度公报; 1 HTTP (cache hit post-1st)')
    ON CONFLICT (id) DO NOTHING;

    -- 4) ingestion_run (status=SUCCESS, records_inserted=5)
    INSERT INTO cegr.ingestion_run
        (id, source_id, started_at, finished_at,
         records_inserted, records_updated, records_skipped,
         status, error_message, run_kind)
    VALUES
        (v_run_id, v_registry_id,
         '2026-09-02'::timestamp, '2026-09-02'::timestamp,
         5, 0, 0,
         'SUCCESS', NULL,
         'U6_HONGHEIKU_REPRINT_BATCH')
    ON CONFLICT (id) DO NOTHING;
    -- observation GDP_ANNUAL: 137008.0 亿元
    INSERT INTO cegr.observation
        (id, indicator_id, indicator_methodology_version_id,
         geo_entity_id, geo_code_version_id, calendar_period_id,
         value, raw_value, is_imputed, missing_reason,
         unit, comparison_basis, value_type, status,
         source_id, source_location_id, ingestion_run_id,
         extracted_at, extraction_method, confidence, notes)
    VALUES
        ('q6eebc99-0007-4000-8000-000000000035',
         'a2000000-0000-0000-0000-00000000a001', 'a2000000-0000-0000-0000-00000000a002',
         v_geo_entity_id, v_geo_cv_id, 'a2000000-0000-0000-0000-000020240101',
         137008.0, '137008.0', FALSE, NULL,
         '亿元', 'YEAR_OVER_YEAR', 'REAL', 'PUBLISHED',
         v_registry_id, v_loc_id, v_run_id,
         '2026-09-02'::timestamp, 'REGEX_ANCHORED', 1.0,
         'jiangsu GDP_ANNUAL 137008.0 亿元;hongheiku 转载;U6 裁定;lineage 三重标注')
    ON CONFLICT (id) DO NOTHING;
    -- observation GDP_GROWTH: 5.8 %
    INSERT INTO cegr.observation
        (id, indicator_id, indicator_methodology_version_id,
         geo_entity_id, geo_code_version_id, calendar_period_id,
         value, raw_value, is_imputed, missing_reason,
         unit, comparison_basis, value_type, status,
         source_id, source_location_id, ingestion_run_id,
         extracted_at, extraction_method, confidence, notes)
    VALUES
        ('q6eebc99-0007-4000-8000-000000000036',
         'a2000000-0000-0000-0000-00000000a003', 'a2000000-0000-0000-0000-00000000a007',
         v_geo_entity_id, v_geo_cv_id, 'a2000000-0000-0000-0000-000020240101',
         5.8, '5.8', FALSE, NULL,
         '%', 'YEAR_OVER_YEAR', 'REAL', 'PUBLISHED',
         v_registry_id, v_loc_id, v_run_id,
         '2026-09-02'::timestamp, 'REGEX_ANCHORED', 1.0,
         'jiangsu GDP_GROWTH 5.8 %;hongheiku 转载;U6 裁定;lineage 三重标注')
    ON CONFLICT (id) DO NOTHING;
    -- observation GVA_PRIMARY: 5245.2 亿元
    INSERT INTO cegr.observation
        (id, indicator_id, indicator_methodology_version_id,
         geo_entity_id, geo_code_version_id, calendar_period_id,
         value, raw_value, is_imputed, missing_reason,
         unit, comparison_basis, value_type, status,
         source_id, source_location_id, ingestion_run_id,
         extracted_at, extraction_method, confidence, notes)
    VALUES
        ('q6eebc99-0007-4000-8000-000000000037',
         'a2000000-0000-0000-0000-00000000a004', 'a2000000-0000-0000-0000-00000000a008',
         v_geo_entity_id, v_geo_cv_id, 'a2000000-0000-0000-0000-000020240101',
         5245.2, '5245.2', FALSE, NULL,
         '亿元', 'YEAR_OVER_YEAR', 'REAL', 'PUBLISHED',
         v_registry_id, v_loc_id, v_run_id,
         '2026-09-02'::timestamp, 'REGEX_ANCHORED', 1.0,
         'jiangsu GVA_PRIMARY 5245.2 亿元;hongheiku 转载;U6 裁定;lineage 三重标注')
    ON CONFLICT (id) DO NOTHING;
    -- observation GVA_SECONDARY: 59180.1 亿元
    INSERT INTO cegr.observation
        (id, indicator_id, indicator_methodology_version_id,
         geo_entity_id, geo_code_version_id, calendar_period_id,
         value, raw_value, is_imputed, missing_reason,
         unit, comparison_basis, value_type, status,
         source_id, source_location_id, ingestion_run_id,
         extracted_at, extraction_method, confidence, notes)
    VALUES
        ('q6eebc99-0007-4000-8000-000000000038',
         'a2000000-0000-0000-0000-00000000a005', 'a2000000-0000-0000-0000-00000000a009',
         v_geo_entity_id, v_geo_cv_id, 'a2000000-0000-0000-0000-000020240101',
         59180.1, '59180.1', FALSE, NULL,
         '亿元', 'YEAR_OVER_YEAR', 'REAL', 'PUBLISHED',
         v_registry_id, v_loc_id, v_run_id,
         '2026-09-02'::timestamp, 'REGEX_ANCHORED', 1.0,
         'jiangsu GVA_SECONDARY 59180.1 亿元;hongheiku 转载;U6 裁定;lineage 三重标注')
    ON CONFLICT (id) DO NOTHING;
    -- observation GVA_TERTIARY: 72582.8 亿元
    INSERT INTO cegr.observation
        (id, indicator_id, indicator_methodology_version_id,
         geo_entity_id, geo_code_version_id, calendar_period_id,
         value, raw_value, is_imputed, missing_reason,
         unit, comparison_basis, value_type, status,
         source_id, source_location_id, ingestion_run_id,
         extracted_at, extraction_method, confidence, notes)
    VALUES
        ('q6eebc99-0007-4000-8000-000000000039',
         'a2000000-0000-0000-0000-00000000a006', 'a2000000-0000-0000-0000-00000000a010',
         v_geo_entity_id, v_geo_cv_id, 'a2000000-0000-0000-0000-000020240101',
         72582.8, '72582.8', FALSE, NULL,
         '亿元', 'YEAR_OVER_YEAR', 'REAL', 'PUBLISHED',
         v_registry_id, v_loc_id, v_run_id,
         '2026-09-02'::timestamp, 'REGEX_ANCHORED', 1.0,
         'jiangsu GVA_TERTIARY 72582.8 亿元;hongheiku 转载;U6 裁定;lineage 三重标注')
    ON CONFLICT (id) DO NOTHING;
END $$;

-- Province 09: zhejiang (浙江省, admin_code=33, idx=08)
DO $$
DECLARE
    v_registry_id UUID := 'q0eebc99-0008-4000-8000-000000000008';
    v_doc_id UUID := 'q1eebc99-0008-4000-8000-000000000008';
    v_loc_id UUID := 'q2eebc99-0008-4000-8000-000000000008';
    v_run_id UUID := 'q7eebc99-0008-4000-8000-000000000008';
    v_geo_entity_id UUID := 'a2000000-0000-0000-0000-000000000033';
    v_geo_cv_id UUID := 'a2000000-0000-0000-0000-00000000003301';
BEGIN
    -- 1) source_registry (hongheiku_tjgb, origin=浙江省统计局)
    INSERT INTO cegr.source_registry
        (id, domain, organization, category, primary_url,
         update_frequency, auth_note, access_method,
         historical_coverage, stability_note, failure_handling,
         enabled, source_level,
         lineage)
    VALUES
        (v_registry_id, 'tjgb.hongheiku.com',
         'hongheiku 转载 (origin: 浙江省统计局)', 'PROVINCIAL_BULLETIN_REPRINT',
         'https://tjgb.hongheiku.com/sjtjgb/57047.html', 'ANNUAL',
         '公开转载;hongheiku 红黑统计公报库;U6 用户裁定接受',
         'HTTP_CURL', '2024 年度公报',
         'U6 金丝雀 5/5 PASS (京/沪/鲁/鄂/川 delta=0 全等)',
         'BLOCKED_NO_POOL 留痕不代换 (红线 14)',
         TRUE, 'S2_REPRINT',
         jsonb_build_object(
             'chain_id', 'real_658_m2_u6_batch_v1'::text,
             'knife', '658',
             'source', 'hongheiku_tjgb',
             'origin', '浙江省统计局',
             'ruling', 'U6 2026-09-02',
             'cross_reference', '金丝雀 5/5 全等 (京/沪/鲁/鄂/川)',
             'reprint', TRUE,
             'extraction_method', 'category_first_url_discovery'
         ))
    ON CONFLICT (id) DO NOTHING;

    -- 2) source_document (file SHA 锁转载字节)
    INSERT INTO cegr.source_document
        (id, source_id, file_path, file_size_bytes, file_hash_sha256,
         mime_type, retrieval_method, retrieval_at, raw_content_ref)
    VALUES
        (v_doc_id, v_registry_id,
         '/tmp/_658_zhejiang.html',
         54771,
         '4c22d82a526aa3e1c7cc6e146b6376e62effa5ec6747c0e85717c951049952b8',
         'text/html', 'HTTP_CURL',
         '2026-09-02'::timestamp,
         'evidence_pack/u6_batch_26prov_fetch_20260902.json#zhejiang')
    ON CONFLICT (id) DO NOTHING;

    -- 3) source_location (URL + http_code 200)
    INSERT INTO cegr.source_location
        (id, source_id, location_type, url, http_code,
         accessed_at, content_hash, notes)
    VALUES
        (v_loc_id, v_registry_id, 'PRIMARY_URL',
         'https://tjgb.hongheiku.com/sjtjgb/57047.html', 200,
         '2026-09-02'::timestamp,
         '4c22d82a526aa3e1c7cc6e146b6376e62effa5ec6747c0e85717c951049952b8',
         'hongheiku 转载页; 2024 年度公报; 1 HTTP (cache hit post-1st)')
    ON CONFLICT (id) DO NOTHING;

    -- 4) ingestion_run (status=SUCCESS, records_inserted=5)
    INSERT INTO cegr.ingestion_run
        (id, source_id, started_at, finished_at,
         records_inserted, records_updated, records_skipped,
         status, error_message, run_kind)
    VALUES
        (v_run_id, v_registry_id,
         '2026-09-02'::timestamp, '2026-09-02'::timestamp,
         5, 0, 0,
         'SUCCESS', NULL,
         'U6_HONGHEIKU_REPRINT_BATCH')
    ON CONFLICT (id) DO NOTHING;
    -- observation GDP_ANNUAL: 90131.0 亿元
    INSERT INTO cegr.observation
        (id, indicator_id, indicator_methodology_version_id,
         geo_entity_id, geo_code_version_id, calendar_period_id,
         value, raw_value, is_imputed, missing_reason,
         unit, comparison_basis, value_type, status,
         source_id, source_location_id, ingestion_run_id,
         extracted_at, extraction_method, confidence, notes)
    VALUES
        ('q6eebc99-0008-4000-8000-000000000040',
         'a2000000-0000-0000-0000-00000000a001', 'a2000000-0000-0000-0000-00000000a002',
         v_geo_entity_id, v_geo_cv_id, 'a2000000-0000-0000-0000-000020240101',
         90131.0, '90131.0', FALSE, NULL,
         '亿元', 'YEAR_OVER_YEAR', 'REAL', 'PUBLISHED',
         v_registry_id, v_loc_id, v_run_id,
         '2026-09-02'::timestamp, 'REGEX_ANCHORED', 1.0,
         'zhejiang GDP_ANNUAL 90131.0 亿元;hongheiku 转载;U6 裁定;lineage 三重标注')
    ON CONFLICT (id) DO NOTHING;
    -- observation GDP_GROWTH: 5.5 %
    INSERT INTO cegr.observation
        (id, indicator_id, indicator_methodology_version_id,
         geo_entity_id, geo_code_version_id, calendar_period_id,
         value, raw_value, is_imputed, missing_reason,
         unit, comparison_basis, value_type, status,
         source_id, source_location_id, ingestion_run_id,
         extracted_at, extraction_method, confidence, notes)
    VALUES
        ('q6eebc99-0008-4000-8000-000000000041',
         'a2000000-0000-0000-0000-00000000a003', 'a2000000-0000-0000-0000-00000000a007',
         v_geo_entity_id, v_geo_cv_id, 'a2000000-0000-0000-0000-000020240101',
         5.5, '5.5', FALSE, NULL,
         '%', 'YEAR_OVER_YEAR', 'REAL', 'PUBLISHED',
         v_registry_id, v_loc_id, v_run_id,
         '2026-09-02'::timestamp, 'REGEX_ANCHORED', 1.0,
         'zhejiang GDP_GROWTH 5.5 %;hongheiku 转载;U6 裁定;lineage 三重标注')
    ON CONFLICT (id) DO NOTHING;
    -- observation GVA_PRIMARY: 2586.0 亿元
    INSERT INTO cegr.observation
        (id, indicator_id, indicator_methodology_version_id,
         geo_entity_id, geo_code_version_id, calendar_period_id,
         value, raw_value, is_imputed, missing_reason,
         unit, comparison_basis, value_type, status,
         source_id, source_location_id, ingestion_run_id,
         extracted_at, extraction_method, confidence, notes)
    VALUES
        ('q6eebc99-0008-4000-8000-000000000042',
         'a2000000-0000-0000-0000-00000000a004', 'a2000000-0000-0000-0000-00000000a008',
         v_geo_entity_id, v_geo_cv_id, 'a2000000-0000-0000-0000-000020240101',
         2586.0, '2586.0', FALSE, NULL,
         '亿元', 'YEAR_OVER_YEAR', 'REAL', 'PUBLISHED',
         v_registry_id, v_loc_id, v_run_id,
         '2026-09-02'::timestamp, 'REGEX_ANCHORED', 1.0,
         'zhejiang GVA_PRIMARY 2586.0 亿元;hongheiku 转载;U6 裁定;lineage 三重标注')
    ON CONFLICT (id) DO NOTHING;
    -- observation GVA_SECONDARY: 34783.0 亿元
    INSERT INTO cegr.observation
        (id, indicator_id, indicator_methodology_version_id,
         geo_entity_id, geo_code_version_id, calendar_period_id,
         value, raw_value, is_imputed, missing_reason,
         unit, comparison_basis, value_type, status,
         source_id, source_location_id, ingestion_run_id,
         extracted_at, extraction_method, confidence, notes)
    VALUES
        ('q6eebc99-0008-4000-8000-000000000043',
         'a2000000-0000-0000-0000-00000000a005', 'a2000000-0000-0000-0000-00000000a009',
         v_geo_entity_id, v_geo_cv_id, 'a2000000-0000-0000-0000-000020240101',
         34783.0, '34783.0', FALSE, NULL,
         '亿元', 'YEAR_OVER_YEAR', 'REAL', 'PUBLISHED',
         v_registry_id, v_loc_id, v_run_id,
         '2026-09-02'::timestamp, 'REGEX_ANCHORED', 1.0,
         'zhejiang GVA_SECONDARY 34783.0 亿元;hongheiku 转载;U6 裁定;lineage 三重标注')
    ON CONFLICT (id) DO NOTHING;
    -- observation GVA_TERTIARY: 52762.0 亿元
    INSERT INTO cegr.observation
        (id, indicator_id, indicator_methodology_version_id,
         geo_entity_id, geo_code_version_id, calendar_period_id,
         value, raw_value, is_imputed, missing_reason,
         unit, comparison_basis, value_type, status,
         source_id, source_location_id, ingestion_run_id,
         extracted_at, extraction_method, confidence, notes)
    VALUES
        ('q6eebc99-0008-4000-8000-000000000044',
         'a2000000-0000-0000-0000-00000000a006', 'a2000000-0000-0000-0000-00000000a010',
         v_geo_entity_id, v_geo_cv_id, 'a2000000-0000-0000-0000-000020240101',
         52762.0, '52762.0', FALSE, NULL,
         '亿元', 'YEAR_OVER_YEAR', 'REAL', 'PUBLISHED',
         v_registry_id, v_loc_id, v_run_id,
         '2026-09-02'::timestamp, 'REGEX_ANCHORED', 1.0,
         'zhejiang GVA_TERTIARY 52762.0 亿元;hongheiku 转载;U6 裁定;lineage 三重标注')
    ON CONFLICT (id) DO NOTHING;
END $$;

-- Province 10: anhui (安徽省, admin_code=34, idx=09)
DO $$
DECLARE
    v_registry_id UUID := 'q0eebc99-0009-4000-8000-000000000009';
    v_doc_id UUID := 'q1eebc99-0009-4000-8000-000000000009';
    v_loc_id UUID := 'q2eebc99-0009-4000-8000-000000000009';
    v_run_id UUID := 'q7eebc99-0009-4000-8000-000000000009';
    v_geo_entity_id UUID := 'a2000000-0000-0000-0000-000000000034';
    v_geo_cv_id UUID := 'a2000000-0000-0000-0000-00000000003401';
BEGIN
    -- 1) source_registry (hongheiku_tjgb, origin=安徽省统计局)
    INSERT INTO cegr.source_registry
        (id, domain, organization, category, primary_url,
         update_frequency, auth_note, access_method,
         historical_coverage, stability_note, failure_handling,
         enabled, source_level,
         lineage)
    VALUES
        (v_registry_id, 'tjgb.hongheiku.com',
         'hongheiku 转载 (origin: 安徽省统计局)', 'PROVINCIAL_BULLETIN_REPRINT',
         'https://tjgb.hongheiku.com/sjtjgb/57296.html', 'ANNUAL',
         '公开转载;hongheiku 红黑统计公报库;U6 用户裁定接受',
         'HTTP_CURL', '2024 年度公报',
         'U6 金丝雀 5/5 PASS (京/沪/鲁/鄂/川 delta=0 全等)',
         'BLOCKED_NO_POOL 留痕不代换 (红线 14)',
         TRUE, 'S2_REPRINT',
         jsonb_build_object(
             'chain_id', 'real_658_m2_u6_batch_v1'::text,
             'knife', '658',
             'source', 'hongheiku_tjgb',
             'origin', '安徽省统计局',
             'ruling', 'U6 2026-09-02',
             'cross_reference', '金丝雀 5/5 全等 (京/沪/鲁/鄂/川)',
             'reprint', TRUE,
             'extraction_method', 'category_first_url_discovery'
         ))
    ON CONFLICT (id) DO NOTHING;

    -- 2) source_document (file SHA 锁转载字节)
    INSERT INTO cegr.source_document
        (id, source_id, file_path, file_size_bytes, file_hash_sha256,
         mime_type, retrieval_method, retrieval_at, raw_content_ref)
    VALUES
        (v_doc_id, v_registry_id,
         '/tmp/_658_anhui.html',
         55063,
         '62299ace2df0ea80b0578d54c83e8f302cc6d326c54abdbbeff9149a0e47907f',
         'text/html', 'HTTP_CURL',
         '2026-09-02'::timestamp,
         'evidence_pack/u6_batch_26prov_fetch_20260902.json#anhui')
    ON CONFLICT (id) DO NOTHING;

    -- 3) source_location (URL + http_code 200)
    INSERT INTO cegr.source_location
        (id, source_id, location_type, url, http_code,
         accessed_at, content_hash, notes)
    VALUES
        (v_loc_id, v_registry_id, 'PRIMARY_URL',
         'https://tjgb.hongheiku.com/sjtjgb/57296.html', 200,
         '2026-09-02'::timestamp,
         '62299ace2df0ea80b0578d54c83e8f302cc6d326c54abdbbeff9149a0e47907f',
         'hongheiku 转载页; 2024 年度公报; 1 HTTP (cache hit post-1st)')
    ON CONFLICT (id) DO NOTHING;

    -- 4) ingestion_run (status=SUCCESS, records_inserted=5)
    INSERT INTO cegr.ingestion_run
        (id, source_id, started_at, finished_at,
         records_inserted, records_updated, records_skipped,
         status, error_message, run_kind)
    VALUES
        (v_run_id, v_registry_id,
         '2026-09-02'::timestamp, '2026-09-02'::timestamp,
         5, 0, 0,
         'SUCCESS', NULL,
         'U6_HONGHEIKU_REPRINT_BATCH')
    ON CONFLICT (id) DO NOTHING;
    -- observation GDP_ANNUAL: 50625.0 亿元
    INSERT INTO cegr.observation
        (id, indicator_id, indicator_methodology_version_id,
         geo_entity_id, geo_code_version_id, calendar_period_id,
         value, raw_value, is_imputed, missing_reason,
         unit, comparison_basis, value_type, status,
         source_id, source_location_id, ingestion_run_id,
         extracted_at, extraction_method, confidence, notes)
    VALUES
        ('q6eebc99-0009-4000-8000-000000000045',
         'a2000000-0000-0000-0000-00000000a001', 'a2000000-0000-0000-0000-00000000a002',
         v_geo_entity_id, v_geo_cv_id, 'a2000000-0000-0000-0000-000020240101',
         50625.0, '50625.0', FALSE, NULL,
         '亿元', 'YEAR_OVER_YEAR', 'REAL', 'PUBLISHED',
         v_registry_id, v_loc_id, v_run_id,
         '2026-09-02'::timestamp, 'REGEX_ANCHORED', 1.0,
         'anhui GDP_ANNUAL 50625.0 亿元;hongheiku 转载;U6 裁定;lineage 三重标注')
    ON CONFLICT (id) DO NOTHING;
    -- observation GDP_GROWTH: 5.8 %
    INSERT INTO cegr.observation
        (id, indicator_id, indicator_methodology_version_id,
         geo_entity_id, geo_code_version_id, calendar_period_id,
         value, raw_value, is_imputed, missing_reason,
         unit, comparison_basis, value_type, status,
         source_id, source_location_id, ingestion_run_id,
         extracted_at, extraction_method, confidence, notes)
    VALUES
        ('q6eebc99-0009-4000-8000-000000000046',
         'a2000000-0000-0000-0000-00000000a003', 'a2000000-0000-0000-0000-00000000a007',
         v_geo_entity_id, v_geo_cv_id, 'a2000000-0000-0000-0000-000020240101',
         5.8, '5.8', FALSE, NULL,
         '%', 'YEAR_OVER_YEAR', 'REAL', 'PUBLISHED',
         v_registry_id, v_loc_id, v_run_id,
         '2026-09-02'::timestamp, 'REGEX_ANCHORED', 1.0,
         'anhui GDP_GROWTH 5.8 %;hongheiku 转载;U6 裁定;lineage 三重标注')
    ON CONFLICT (id) DO NOTHING;
    -- observation GVA_PRIMARY: 3566.0 亿元
    INSERT INTO cegr.observation
        (id, indicator_id, indicator_methodology_version_id,
         geo_entity_id, geo_code_version_id, calendar_period_id,
         value, raw_value, is_imputed, missing_reason,
         unit, comparison_basis, value_type, status,
         source_id, source_location_id, ingestion_run_id,
         extracted_at, extraction_method, confidence, notes)
    VALUES
        ('q6eebc99-0009-4000-8000-000000000047',
         'a2000000-0000-0000-0000-00000000a004', 'a2000000-0000-0000-0000-00000000a008',
         v_geo_entity_id, v_geo_cv_id, 'a2000000-0000-0000-0000-000020240101',
         3566.0, '3566.0', FALSE, NULL,
         '亿元', 'YEAR_OVER_YEAR', 'REAL', 'PUBLISHED',
         v_registry_id, v_loc_id, v_run_id,
         '2026-09-02'::timestamp, 'REGEX_ANCHORED', 1.0,
         'anhui GVA_PRIMARY 3566.0 亿元;hongheiku 转载;U6 裁定;lineage 三重标注')
    ON CONFLICT (id) DO NOTHING;
    -- observation GVA_SECONDARY: 19607.0 亿元
    INSERT INTO cegr.observation
        (id, indicator_id, indicator_methodology_version_id,
         geo_entity_id, geo_code_version_id, calendar_period_id,
         value, raw_value, is_imputed, missing_reason,
         unit, comparison_basis, value_type, status,
         source_id, source_location_id, ingestion_run_id,
         extracted_at, extraction_method, confidence, notes)
    VALUES
        ('q6eebc99-0009-4000-8000-000000000048',
         'a2000000-0000-0000-0000-00000000a005', 'a2000000-0000-0000-0000-00000000a009',
         v_geo_entity_id, v_geo_cv_id, 'a2000000-0000-0000-0000-000020240101',
         19607.0, '19607.0', FALSE, NULL,
         '亿元', 'YEAR_OVER_YEAR', 'REAL', 'PUBLISHED',
         v_registry_id, v_loc_id, v_run_id,
         '2026-09-02'::timestamp, 'REGEX_ANCHORED', 1.0,
         'anhui GVA_SECONDARY 19607.0 亿元;hongheiku 转载;U6 裁定;lineage 三重标注')
    ON CONFLICT (id) DO NOTHING;
    -- observation GVA_TERTIARY: 27452.0 亿元
    INSERT INTO cegr.observation
        (id, indicator_id, indicator_methodology_version_id,
         geo_entity_id, geo_code_version_id, calendar_period_id,
         value, raw_value, is_imputed, missing_reason,
         unit, comparison_basis, value_type, status,
         source_id, source_location_id, ingestion_run_id,
         extracted_at, extraction_method, confidence, notes)
    VALUES
        ('q6eebc99-0009-4000-8000-000000000049',
         'a2000000-0000-0000-0000-00000000a006', 'a2000000-0000-0000-0000-00000000a010',
         v_geo_entity_id, v_geo_cv_id, 'a2000000-0000-0000-0000-000020240101',
         27452.0, '27452.0', FALSE, NULL,
         '亿元', 'YEAR_OVER_YEAR', 'REAL', 'PUBLISHED',
         v_registry_id, v_loc_id, v_run_id,
         '2026-09-02'::timestamp, 'REGEX_ANCHORED', 1.0,
         'anhui GVA_TERTIARY 27452.0 亿元;hongheiku 转载;U6 裁定;lineage 三重标注')
    ON CONFLICT (id) DO NOTHING;
END $$;

-- Province 11: fujian (福建省, admin_code=35, idx=10)
DO $$
DECLARE
    v_registry_id UUID := 'q0eebc99-000a-4000-8000-000000000010';
    v_doc_id UUID := 'q1eebc99-000a-4000-8000-000000000010';
    v_loc_id UUID := 'q2eebc99-000a-4000-8000-000000000010';
    v_run_id UUID := 'q7eebc99-000a-4000-8000-000000000010';
    v_geo_entity_id UUID := 'a2000000-0000-0000-0000-000000000035';
    v_geo_cv_id UUID := 'a2000000-0000-0000-0000-00000000003501';
BEGIN
    -- 1) source_registry (hongheiku_tjgb, origin=福建省统计局)
    INSERT INTO cegr.source_registry
        (id, domain, organization, category, primary_url,
         update_frequency, auth_note, access_method,
         historical_coverage, stability_note, failure_handling,
         enabled, source_level,
         lineage)
    VALUES
        (v_registry_id, 'tjgb.hongheiku.com',
         'hongheiku 转载 (origin: 福建省统计局)', 'PROVINCIAL_BULLETIN_REPRINT',
         'https://tjgb.hongheiku.com/sjtjgb/57209.html', 'ANNUAL',
         '公开转载;hongheiku 红黑统计公报库;U6 用户裁定接受',
         'HTTP_CURL', '2024 年度公报',
         'U6 金丝雀 5/5 PASS (京/沪/鲁/鄂/川 delta=0 全等)',
         'BLOCKED_NO_POOL 留痕不代换 (红线 14)',
         TRUE, 'S2_REPRINT',
         jsonb_build_object(
             'chain_id', 'real_658_m2_u6_batch_v1'::text,
             'knife', '658',
             'source', 'hongheiku_tjgb',
             'origin', '福建省统计局',
             'ruling', 'U6 2026-09-02',
             'cross_reference', '金丝雀 5/5 全等 (京/沪/鲁/鄂/川)',
             'reprint', TRUE,
             'extraction_method', 'category_first_url_discovery'
         ))
    ON CONFLICT (id) DO NOTHING;

    -- 2) source_document (file SHA 锁转载字节)
    INSERT INTO cegr.source_document
        (id, source_id, file_path, file_size_bytes, file_hash_sha256,
         mime_type, retrieval_method, retrieval_at, raw_content_ref)
    VALUES
        (v_doc_id, v_registry_id,
         '/tmp/_658_fujian.html',
         67267,
         '8f58be0f606af9f8d91237387ea27340763d4f9a25e896f3d708444cab0964b5',
         'text/html', 'HTTP_CURL',
         '2026-09-02'::timestamp,
         'evidence_pack/u6_batch_26prov_fetch_20260902.json#fujian')
    ON CONFLICT (id) DO NOTHING;

    -- 3) source_location (URL + http_code 200)
    INSERT INTO cegr.source_location
        (id, source_id, location_type, url, http_code,
         accessed_at, content_hash, notes)
    VALUES
        (v_loc_id, v_registry_id, 'PRIMARY_URL',
         'https://tjgb.hongheiku.com/sjtjgb/57209.html', 200,
         '2026-09-02'::timestamp,
         '8f58be0f606af9f8d91237387ea27340763d4f9a25e896f3d708444cab0964b5',
         'hongheiku 转载页; 2024 年度公报; 1 HTTP (cache hit post-1st)')
    ON CONFLICT (id) DO NOTHING;

    -- 4) ingestion_run (status=SUCCESS, records_inserted=5)
    INSERT INTO cegr.ingestion_run
        (id, source_id, started_at, finished_at,
         records_inserted, records_updated, records_skipped,
         status, error_message, run_kind)
    VALUES
        (v_run_id, v_registry_id,
         '2026-09-02'::timestamp, '2026-09-02'::timestamp,
         5, 0, 0,
         'SUCCESS', NULL,
         'U6_HONGHEIKU_REPRINT_BATCH')
    ON CONFLICT (id) DO NOTHING;
    -- observation GDP_ANNUAL: 57761.02 亿元
    INSERT INTO cegr.observation
        (id, indicator_id, indicator_methodology_version_id,
         geo_entity_id, geo_code_version_id, calendar_period_id,
         value, raw_value, is_imputed, missing_reason,
         unit, comparison_basis, value_type, status,
         source_id, source_location_id, ingestion_run_id,
         extracted_at, extraction_method, confidence, notes)
    VALUES
        ('q6eebc99-000a-4000-8000-000000000050',
         'a2000000-0000-0000-0000-00000000a001', 'a2000000-0000-0000-0000-00000000a002',
         v_geo_entity_id, v_geo_cv_id, 'a2000000-0000-0000-0000-000020240101',
         57761.02, '57761.02', FALSE, NULL,
         '亿元', 'YEAR_OVER_YEAR', 'REAL', 'PUBLISHED',
         v_registry_id, v_loc_id, v_run_id,
         '2026-09-02'::timestamp, 'REGEX_ANCHORED', 1.0,
         'fujian GDP_ANNUAL 57761.02 亿元;hongheiku 转载;U6 裁定;lineage 三重标注')
    ON CONFLICT (id) DO NOTHING;
    -- observation GDP_GROWTH: 5.5 %
    INSERT INTO cegr.observation
        (id, indicator_id, indicator_methodology_version_id,
         geo_entity_id, geo_code_version_id, calendar_period_id,
         value, raw_value, is_imputed, missing_reason,
         unit, comparison_basis, value_type, status,
         source_id, source_location_id, ingestion_run_id,
         extracted_at, extraction_method, confidence, notes)
    VALUES
        ('q6eebc99-000a-4000-8000-000000000051',
         'a2000000-0000-0000-0000-00000000a003', 'a2000000-0000-0000-0000-00000000a007',
         v_geo_entity_id, v_geo_cv_id, 'a2000000-0000-0000-0000-000020240101',
         5.5, '5.5', FALSE, NULL,
         '%', 'YEAR_OVER_YEAR', 'REAL', 'PUBLISHED',
         v_registry_id, v_loc_id, v_run_id,
         '2026-09-02'::timestamp, 'REGEX_ANCHORED', 1.0,
         'fujian GDP_GROWTH 5.5 %;hongheiku 转载;U6 裁定;lineage 三重标注')
    ON CONFLICT (id) DO NOTHING;
    -- observation GVA_PRIMARY: 3287.67 亿元
    INSERT INTO cegr.observation
        (id, indicator_id, indicator_methodology_version_id,
         geo_entity_id, geo_code_version_id, calendar_period_id,
         value, raw_value, is_imputed, missing_reason,
         unit, comparison_basis, value_type, status,
         source_id, source_location_id, ingestion_run_id,
         extracted_at, extraction_method, confidence, notes)
    VALUES
        ('q6eebc99-000a-4000-8000-000000000052',
         'a2000000-0000-0000-0000-00000000a004', 'a2000000-0000-0000-0000-00000000a008',
         v_geo_entity_id, v_geo_cv_id, 'a2000000-0000-0000-0000-000020240101',
         3287.67, '3287.67', FALSE, NULL,
         '亿元', 'YEAR_OVER_YEAR', 'REAL', 'PUBLISHED',
         v_registry_id, v_loc_id, v_run_id,
         '2026-09-02'::timestamp, 'REGEX_ANCHORED', 1.0,
         'fujian GVA_PRIMARY 3287.67 亿元;hongheiku 转载;U6 裁定;lineage 三重标注')
    ON CONFLICT (id) DO NOTHING;
    -- observation GVA_SECONDARY: 24713.16 亿元
    INSERT INTO cegr.observation
        (id, indicator_id, indicator_methodology_version_id,
         geo_entity_id, geo_code_version_id, calendar_period_id,
         value, raw_value, is_imputed, missing_reason,
         unit, comparison_basis, value_type, status,
         source_id, source_location_id, ingestion_run_id,
         extracted_at, extraction_method, confidence, notes)
    VALUES
        ('q6eebc99-000a-4000-8000-000000000053',
         'a2000000-0000-0000-0000-00000000a005', 'a2000000-0000-0000-0000-00000000a009',
         v_geo_entity_id, v_geo_cv_id, 'a2000000-0000-0000-0000-000020240101',
         24713.16, '24713.16', FALSE, NULL,
         '亿元', 'YEAR_OVER_YEAR', 'REAL', 'PUBLISHED',
         v_registry_id, v_loc_id, v_run_id,
         '2026-09-02'::timestamp, 'REGEX_ANCHORED', 1.0,
         'fujian GVA_SECONDARY 24713.16 亿元;hongheiku 转载;U6 裁定;lineage 三重标注')
    ON CONFLICT (id) DO NOTHING;
    -- observation GVA_TERTIARY: 29760.19 亿元
    INSERT INTO cegr.observation
        (id, indicator_id, indicator_methodology_version_id,
         geo_entity_id, geo_code_version_id, calendar_period_id,
         value, raw_value, is_imputed, missing_reason,
         unit, comparison_basis, value_type, status,
         source_id, source_location_id, ingestion_run_id,
         extracted_at, extraction_method, confidence, notes)
    VALUES
        ('q6eebc99-000a-4000-8000-000000000054',
         'a2000000-0000-0000-0000-00000000a006', 'a2000000-0000-0000-0000-00000000a010',
         v_geo_entity_id, v_geo_cv_id, 'a2000000-0000-0000-0000-000020240101',
         29760.19, '29760.19', FALSE, NULL,
         '亿元', 'YEAR_OVER_YEAR', 'REAL', 'PUBLISHED',
         v_registry_id, v_loc_id, v_run_id,
         '2026-09-02'::timestamp, 'REGEX_ANCHORED', 1.0,
         'fujian GVA_TERTIARY 29760.19 亿元;hongheiku 转载;U6 裁定;lineage 三重标注')
    ON CONFLICT (id) DO NOTHING;
END $$;

-- Province 12: jiangxi (江西省, admin_code=36, idx=11)
DO $$
DECLARE
    v_registry_id UUID := 'q0eebc99-000b-4000-8000-000000000011';
    v_doc_id UUID := 'q1eebc99-000b-4000-8000-000000000011';
    v_loc_id UUID := 'q2eebc99-000b-4000-8000-000000000011';
    v_run_id UUID := 'q7eebc99-000b-4000-8000-000000000011';
    v_geo_entity_id UUID := 'a2000000-0000-0000-0000-000000000036';
    v_geo_cv_id UUID := 'a2000000-0000-0000-0000-00000000003601';
BEGIN
    -- 1) source_registry (hongheiku_tjgb, origin=江西省统计局)
    INSERT INTO cegr.source_registry
        (id, domain, organization, category, primary_url,
         update_frequency, auth_note, access_method,
         historical_coverage, stability_note, failure_handling,
         enabled, source_level,
         lineage)
    VALUES
        (v_registry_id, 'tjgb.hongheiku.com',
         'hongheiku 转载 (origin: 江西省统计局)', 'PROVINCIAL_BULLETIN_REPRINT',
         'https://tjgb.hongheiku.com/sjtjgb/57884.html', 'ANNUAL',
         '公开转载;hongheiku 红黑统计公报库;U6 用户裁定接受',
         'HTTP_CURL', '2024 年度公报',
         'U6 金丝雀 5/5 PASS (京/沪/鲁/鄂/川 delta=0 全等)',
         'BLOCKED_NO_POOL 留痕不代换 (红线 14)',
         TRUE, 'S2_REPRINT',
         jsonb_build_object(
             'chain_id', 'real_658_m2_u6_batch_v1'::text,
             'knife', '658',
             'source', 'hongheiku_tjgb',
             'origin', '江西省统计局',
             'ruling', 'U6 2026-09-02',
             'cross_reference', '金丝雀 5/5 全等 (京/沪/鲁/鄂/川)',
             'reprint', TRUE,
             'extraction_method', 'category_first_url_discovery'
         ))
    ON CONFLICT (id) DO NOTHING;

    -- 2) source_document (file SHA 锁转载字节)
    INSERT INTO cegr.source_document
        (id, source_id, file_path, file_size_bytes, file_hash_sha256,
         mime_type, retrieval_method, retrieval_at, raw_content_ref)
    VALUES
        (v_doc_id, v_registry_id,
         '/tmp/_658_jiangxi.html',
         71973,
         '52dfccded22918d3e97a3433288e76a3b89e3e16c1c82d22416b2b16dda7b869',
         'text/html', 'HTTP_CURL',
         '2026-09-02'::timestamp,
         'evidence_pack/u6_batch_26prov_fetch_20260902.json#jiangxi')
    ON CONFLICT (id) DO NOTHING;

    -- 3) source_location (URL + http_code 200)
    INSERT INTO cegr.source_location
        (id, source_id, location_type, url, http_code,
         accessed_at, content_hash, notes)
    VALUES
        (v_loc_id, v_registry_id, 'PRIMARY_URL',
         'https://tjgb.hongheiku.com/sjtjgb/57884.html', 200,
         '2026-09-02'::timestamp,
         '52dfccded22918d3e97a3433288e76a3b89e3e16c1c82d22416b2b16dda7b869',
         'hongheiku 转载页; 2024 年度公报; 1 HTTP (cache hit post-1st)')
    ON CONFLICT (id) DO NOTHING;

    -- 4) ingestion_run (status=SUCCESS, records_inserted=5)
    INSERT INTO cegr.ingestion_run
        (id, source_id, started_at, finished_at,
         records_inserted, records_updated, records_skipped,
         status, error_message, run_kind)
    VALUES
        (v_run_id, v_registry_id,
         '2026-09-02'::timestamp, '2026-09-02'::timestamp,
         5, 0, 0,
         'SUCCESS', NULL,
         'U6_HONGHEIKU_REPRINT_BATCH')
    ON CONFLICT (id) DO NOTHING;
    -- observation GDP_ANNUAL: 34202.5 亿元
    INSERT INTO cegr.observation
        (id, indicator_id, indicator_methodology_version_id,
         geo_entity_id, geo_code_version_id, calendar_period_id,
         value, raw_value, is_imputed, missing_reason,
         unit, comparison_basis, value_type, status,
         source_id, source_location_id, ingestion_run_id,
         extracted_at, extraction_method, confidence, notes)
    VALUES
        ('q6eebc99-000b-4000-8000-000000000055',
         'a2000000-0000-0000-0000-00000000a001', 'a2000000-0000-0000-0000-00000000a002',
         v_geo_entity_id, v_geo_cv_id, 'a2000000-0000-0000-0000-000020240101',
         34202.5, '34202.5', FALSE, NULL,
         '亿元', 'YEAR_OVER_YEAR', 'REAL', 'PUBLISHED',
         v_registry_id, v_loc_id, v_run_id,
         '2026-09-02'::timestamp, 'REGEX_ANCHORED', 1.0,
         'jiangxi GDP_ANNUAL 34202.5 亿元;hongheiku 转载;U6 裁定;lineage 三重标注')
    ON CONFLICT (id) DO NOTHING;
    -- observation GDP_GROWTH: 5.1 %
    INSERT INTO cegr.observation
        (id, indicator_id, indicator_methodology_version_id,
         geo_entity_id, geo_code_version_id, calendar_period_id,
         value, raw_value, is_imputed, missing_reason,
         unit, comparison_basis, value_type, status,
         source_id, source_location_id, ingestion_run_id,
         extracted_at, extraction_method, confidence, notes)
    VALUES
        ('q6eebc99-000b-4000-8000-000000000056',
         'a2000000-0000-0000-0000-00000000a003', 'a2000000-0000-0000-0000-00000000a007',
         v_geo_entity_id, v_geo_cv_id, 'a2000000-0000-0000-0000-000020240101',
         5.1, '5.1', FALSE, NULL,
         '%', 'YEAR_OVER_YEAR', 'REAL', 'PUBLISHED',
         v_registry_id, v_loc_id, v_run_id,
         '2026-09-02'::timestamp, 'REGEX_ANCHORED', 1.0,
         'jiangxi GDP_GROWTH 5.1 %;hongheiku 转载;U6 裁定;lineage 三重标注')
    ON CONFLICT (id) DO NOTHING;
    -- observation GVA_PRIMARY: 2605.1 亿元
    INSERT INTO cegr.observation
        (id, indicator_id, indicator_methodology_version_id,
         geo_entity_id, geo_code_version_id, calendar_period_id,
         value, raw_value, is_imputed, missing_reason,
         unit, comparison_basis, value_type, status,
         source_id, source_location_id, ingestion_run_id,
         extracted_at, extraction_method, confidence, notes)
    VALUES
        ('q6eebc99-000b-4000-8000-000000000057',
         'a2000000-0000-0000-0000-00000000a004', 'a2000000-0000-0000-0000-00000000a008',
         v_geo_entity_id, v_geo_cv_id, 'a2000000-0000-0000-0000-000020240101',
         2605.1, '2605.1', FALSE, NULL,
         '亿元', 'YEAR_OVER_YEAR', 'REAL', 'PUBLISHED',
         v_registry_id, v_loc_id, v_run_id,
         '2026-09-02'::timestamp, 'REGEX_ANCHORED', 1.0,
         'jiangxi GVA_PRIMARY 2605.1 亿元;hongheiku 转载;U6 裁定;lineage 三重标注')
    ON CONFLICT (id) DO NOTHING;
    -- observation GVA_SECONDARY: 13688.6 亿元
    INSERT INTO cegr.observation
        (id, indicator_id, indicator_methodology_version_id,
         geo_entity_id, geo_code_version_id, calendar_period_id,
         value, raw_value, is_imputed, missing_reason,
         unit, comparison_basis, value_type, status,
         source_id, source_location_id, ingestion_run_id,
         extracted_at, extraction_method, confidence, notes)
    VALUES
        ('q6eebc99-000b-4000-8000-000000000058',
         'a2000000-0000-0000-0000-00000000a005', 'a2000000-0000-0000-0000-00000000a009',
         v_geo_entity_id, v_geo_cv_id, 'a2000000-0000-0000-0000-000020240101',
         13688.6, '13688.6', FALSE, NULL,
         '亿元', 'YEAR_OVER_YEAR', 'REAL', 'PUBLISHED',
         v_registry_id, v_loc_id, v_run_id,
         '2026-09-02'::timestamp, 'REGEX_ANCHORED', 1.0,
         'jiangxi GVA_SECONDARY 13688.6 亿元;hongheiku 转载;U6 裁定;lineage 三重标注')
    ON CONFLICT (id) DO NOTHING;
    -- observation GVA_TERTIARY: 17908.8 亿元
    INSERT INTO cegr.observation
        (id, indicator_id, indicator_methodology_version_id,
         geo_entity_id, geo_code_version_id, calendar_period_id,
         value, raw_value, is_imputed, missing_reason,
         unit, comparison_basis, value_type, status,
         source_id, source_location_id, ingestion_run_id,
         extracted_at, extraction_method, confidence, notes)
    VALUES
        ('q6eebc99-000b-4000-8000-000000000059',
         'a2000000-0000-0000-0000-00000000a006', 'a2000000-0000-0000-0000-00000000a010',
         v_geo_entity_id, v_geo_cv_id, 'a2000000-0000-0000-0000-000020240101',
         17908.8, '17908.8', FALSE, NULL,
         '亿元', 'YEAR_OVER_YEAR', 'REAL', 'PUBLISHED',
         v_registry_id, v_loc_id, v_run_id,
         '2026-09-02'::timestamp, 'REGEX_ANCHORED', 1.0,
         'jiangxi GVA_TERTIARY 17908.8 亿元;hongheiku 转载;U6 裁定;lineage 三重标注')
    ON CONFLICT (id) DO NOTHING;
END $$;

-- Province 13: henan (河南省, admin_code=41, idx=12)
DO $$
DECLARE
    v_registry_id UUID := 'q0eebc99-000c-4000-8000-000000000012';
    v_doc_id UUID := 'q1eebc99-000c-4000-8000-000000000012';
    v_loc_id UUID := 'q2eebc99-000c-4000-8000-000000000012';
    v_run_id UUID := 'q7eebc99-000c-4000-8000-000000000012';
    v_geo_entity_id UUID := 'a2000000-0000-0000-0000-000000000041';
    v_geo_cv_id UUID := 'a2000000-0000-0000-0000-00000000004101';
BEGIN
    -- 1) source_registry (hongheiku_tjgb, origin=河南省统计局)
    INSERT INTO cegr.source_registry
        (id, domain, organization, category, primary_url,
         update_frequency, auth_note, access_method,
         historical_coverage, stability_note, failure_handling,
         enabled, source_level,
         lineage)
    VALUES
        (v_registry_id, 'tjgb.hongheiku.com',
         'hongheiku 转载 (origin: 河南省统计局)', 'PROVINCIAL_BULLETIN_REPRINT',
         'https://tjgb.hongheiku.com/sjtjgb/58132.html', 'ANNUAL',
         '公开转载;hongheiku 红黑统计公报库;U6 用户裁定接受',
         'HTTP_CURL', '2024 年度公报',
         'U6 金丝雀 5/5 PASS (京/沪/鲁/鄂/川 delta=0 全等)',
         'BLOCKED_NO_POOL 留痕不代换 (红线 14)',
         TRUE, 'S2_REPRINT',
         jsonb_build_object(
             'chain_id', 'real_658_m2_u6_batch_v1'::text,
             'knife', '658',
             'source', 'hongheiku_tjgb',
             'origin', '河南省统计局',
             'ruling', 'U6 2026-09-02',
             'cross_reference', '金丝雀 5/5 全等 (京/沪/鲁/鄂/川)',
             'reprint', TRUE,
             'extraction_method', 'category_first_url_discovery'
         ))
    ON CONFLICT (id) DO NOTHING;

    -- 2) source_document (file SHA 锁转载字节)
    INSERT INTO cegr.source_document
        (id, source_id, file_path, file_size_bytes, file_hash_sha256,
         mime_type, retrieval_method, retrieval_at, raw_content_ref)
    VALUES
        (v_doc_id, v_registry_id,
         '/tmp/_658_henan.html',
         52550,
         'b0388e69dee5ea342f57162ec2c7fb2c974308fddfc6211485ebd3a5e15bcf15',
         'text/html', 'HTTP_CURL',
         '2026-09-02'::timestamp,
         'evidence_pack/u6_batch_26prov_fetch_20260902.json#henan')
    ON CONFLICT (id) DO NOTHING;

    -- 3) source_location (URL + http_code 200)
    INSERT INTO cegr.source_location
        (id, source_id, location_type, url, http_code,
         accessed_at, content_hash, notes)
    VALUES
        (v_loc_id, v_registry_id, 'PRIMARY_URL',
         'https://tjgb.hongheiku.com/sjtjgb/58132.html', 200,
         '2026-09-02'::timestamp,
         'b0388e69dee5ea342f57162ec2c7fb2c974308fddfc6211485ebd3a5e15bcf15',
         'hongheiku 转载页; 2024 年度公报; 1 HTTP (cache hit post-1st)')
    ON CONFLICT (id) DO NOTHING;

    -- 4) ingestion_run (status=SUCCESS, records_inserted=5)
    INSERT INTO cegr.ingestion_run
        (id, source_id, started_at, finished_at,
         records_inserted, records_updated, records_skipped,
         status, error_message, run_kind)
    VALUES
        (v_run_id, v_registry_id,
         '2026-09-02'::timestamp, '2026-09-02'::timestamp,
         5, 0, 0,
         'SUCCESS', NULL,
         'U6_HONGHEIKU_REPRINT_BATCH')
    ON CONFLICT (id) DO NOTHING;
    -- observation GDP_ANNUAL: 63589.99 亿元
    INSERT INTO cegr.observation
        (id, indicator_id, indicator_methodology_version_id,
         geo_entity_id, geo_code_version_id, calendar_period_id,
         value, raw_value, is_imputed, missing_reason,
         unit, comparison_basis, value_type, status,
         source_id, source_location_id, ingestion_run_id,
         extracted_at, extraction_method, confidence, notes)
    VALUES
        ('q6eebc99-000c-4000-8000-000000000060',
         'a2000000-0000-0000-0000-00000000a001', 'a2000000-0000-0000-0000-00000000a002',
         v_geo_entity_id, v_geo_cv_id, 'a2000000-0000-0000-0000-000020240101',
         63589.99, '63589.99', FALSE, NULL,
         '亿元', 'YEAR_OVER_YEAR', 'REAL', 'PUBLISHED',
         v_registry_id, v_loc_id, v_run_id,
         '2026-09-02'::timestamp, 'REGEX_ANCHORED', 1.0,
         'henan GDP_ANNUAL 63589.99 亿元;hongheiku 转载;U6 裁定;lineage 三重标注')
    ON CONFLICT (id) DO NOTHING;
    -- observation GDP_GROWTH: 5.1 %
    INSERT INTO cegr.observation
        (id, indicator_id, indicator_methodology_version_id,
         geo_entity_id, geo_code_version_id, calendar_period_id,
         value, raw_value, is_imputed, missing_reason,
         unit, comparison_basis, value_type, status,
         source_id, source_location_id, ingestion_run_id,
         extracted_at, extraction_method, confidence, notes)
    VALUES
        ('q6eebc99-000c-4000-8000-000000000061',
         'a2000000-0000-0000-0000-00000000a003', 'a2000000-0000-0000-0000-00000000a007',
         v_geo_entity_id, v_geo_cv_id, 'a2000000-0000-0000-0000-000020240101',
         5.1, '5.1', FALSE, NULL,
         '%', 'YEAR_OVER_YEAR', 'REAL', 'PUBLISHED',
         v_registry_id, v_loc_id, v_run_id,
         '2026-09-02'::timestamp, 'REGEX_ANCHORED', 1.0,
         'henan GDP_GROWTH 5.1 %;hongheiku 转载;U6 裁定;lineage 三重标注')
    ON CONFLICT (id) DO NOTHING;
    -- observation GVA_PRIMARY: 5491.4 亿元
    INSERT INTO cegr.observation
        (id, indicator_id, indicator_methodology_version_id,
         geo_entity_id, geo_code_version_id, calendar_period_id,
         value, raw_value, is_imputed, missing_reason,
         unit, comparison_basis, value_type, status,
         source_id, source_location_id, ingestion_run_id,
         extracted_at, extraction_method, confidence, notes)
    VALUES
        ('q6eebc99-000c-4000-8000-000000000062',
         'a2000000-0000-0000-0000-00000000a004', 'a2000000-0000-0000-0000-00000000a008',
         v_geo_entity_id, v_geo_cv_id, 'a2000000-0000-0000-0000-000020240101',
         5491.4, '5491.4', FALSE, NULL,
         '亿元', 'YEAR_OVER_YEAR', 'REAL', 'PUBLISHED',
         v_registry_id, v_loc_id, v_run_id,
         '2026-09-02'::timestamp, 'REGEX_ANCHORED', 1.0,
         'henan GVA_PRIMARY 5491.4 亿元;hongheiku 转载;U6 裁定;lineage 三重标注')
    ON CONFLICT (id) DO NOTHING;
    -- observation GVA_SECONDARY: 24346.17 亿元
    INSERT INTO cegr.observation
        (id, indicator_id, indicator_methodology_version_id,
         geo_entity_id, geo_code_version_id, calendar_period_id,
         value, raw_value, is_imputed, missing_reason,
         unit, comparison_basis, value_type, status,
         source_id, source_location_id, ingestion_run_id,
         extracted_at, extraction_method, confidence, notes)
    VALUES
        ('q6eebc99-000c-4000-8000-000000000063',
         'a2000000-0000-0000-0000-00000000a005', 'a2000000-0000-0000-0000-00000000a009',
         v_geo_entity_id, v_geo_cv_id, 'a2000000-0000-0000-0000-000020240101',
         24346.17, '24346.17', FALSE, NULL,
         '亿元', 'YEAR_OVER_YEAR', 'REAL', 'PUBLISHED',
         v_registry_id, v_loc_id, v_run_id,
         '2026-09-02'::timestamp, 'REGEX_ANCHORED', 1.0,
         'henan GVA_SECONDARY 24346.17 亿元;hongheiku 转载;U6 裁定;lineage 三重标注')
    ON CONFLICT (id) DO NOTHING;
    -- observation GVA_TERTIARY: 33752.42 亿元
    INSERT INTO cegr.observation
        (id, indicator_id, indicator_methodology_version_id,
         geo_entity_id, geo_code_version_id, calendar_period_id,
         value, raw_value, is_imputed, missing_reason,
         unit, comparison_basis, value_type, status,
         source_id, source_location_id, ingestion_run_id,
         extracted_at, extraction_method, confidence, notes)
    VALUES
        ('q6eebc99-000c-4000-8000-000000000064',
         'a2000000-0000-0000-0000-00000000a006', 'a2000000-0000-0000-0000-00000000a010',
         v_geo_entity_id, v_geo_cv_id, 'a2000000-0000-0000-0000-000020240101',
         33752.42, '33752.42', FALSE, NULL,
         '亿元', 'YEAR_OVER_YEAR', 'REAL', 'PUBLISHED',
         v_registry_id, v_loc_id, v_run_id,
         '2026-09-02'::timestamp, 'REGEX_ANCHORED', 1.0,
         'henan GVA_TERTIARY 33752.42 亿元;hongheiku 转载;U6 裁定;lineage 三重标注')
    ON CONFLICT (id) DO NOTHING;
END $$;

-- Province 14: hunan (湖南省, admin_code=43, idx=13)
DO $$
DECLARE
    v_registry_id UUID := 'q0eebc99-000d-4000-8000-000000000013';
    v_doc_id UUID := 'q1eebc99-000d-4000-8000-000000000013';
    v_loc_id UUID := 'q2eebc99-000d-4000-8000-000000000013';
    v_run_id UUID := 'q7eebc99-000d-4000-8000-000000000013';
    v_geo_entity_id UUID := 'a2000000-0000-0000-0000-000000000043';
    v_geo_cv_id UUID := 'a2000000-0000-0000-0000-00000000004301';
BEGIN
    -- 1) source_registry (hongheiku_tjgb, origin=湖南省统计局)
    INSERT INTO cegr.source_registry
        (id, domain, organization, category, primary_url,
         update_frequency, auth_note, access_method,
         historical_coverage, stability_note, failure_handling,
         enabled, source_level,
         lineage)
    VALUES
        (v_registry_id, 'tjgb.hongheiku.com',
         'hongheiku 转载 (origin: 湖南省统计局)', 'PROVINCIAL_BULLETIN_REPRINT',
         'https://tjgb.hongheiku.com/sjtjgb/57486.html', 'ANNUAL',
         '公开转载;hongheiku 红黑统计公报库;U6 用户裁定接受',
         'HTTP_CURL', '2024 年度公报',
         'U6 金丝雀 5/5 PASS (京/沪/鲁/鄂/川 delta=0 全等)',
         'BLOCKED_NO_POOL 留痕不代换 (红线 14)',
         TRUE, 'S2_REPRINT',
         jsonb_build_object(
             'chain_id', 'real_658_m2_u6_batch_v1'::text,
             'knife', '658',
             'source', 'hongheiku_tjgb',
             'origin', '湖南省统计局',
             'ruling', 'U6 2026-09-02',
             'cross_reference', '金丝雀 5/5 全等 (京/沪/鲁/鄂/川)',
             'reprint', TRUE,
             'extraction_method', 'category_first_url_discovery'
         ))
    ON CONFLICT (id) DO NOTHING;

    -- 2) source_document (file SHA 锁转载字节)
    INSERT INTO cegr.source_document
        (id, source_id, file_path, file_size_bytes, file_hash_sha256,
         mime_type, retrieval_method, retrieval_at, raw_content_ref)
    VALUES
        (v_doc_id, v_registry_id,
         '/tmp/_658_hunan.html',
         58502,
         '73d93ec5493171a14cc822512e24036879d86947e9137dcc0e240d23800851fa',
         'text/html', 'HTTP_CURL',
         '2026-09-02'::timestamp,
         'evidence_pack/u6_batch_26prov_fetch_20260902.json#hunan')
    ON CONFLICT (id) DO NOTHING;

    -- 3) source_location (URL + http_code 200)
    INSERT INTO cegr.source_location
        (id, source_id, location_type, url, http_code,
         accessed_at, content_hash, notes)
    VALUES
        (v_loc_id, v_registry_id, 'PRIMARY_URL',
         'https://tjgb.hongheiku.com/sjtjgb/57486.html', 200,
         '2026-09-02'::timestamp,
         '73d93ec5493171a14cc822512e24036879d86947e9137dcc0e240d23800851fa',
         'hongheiku 转载页; 2024 年度公报; 1 HTTP (cache hit post-1st)')
    ON CONFLICT (id) DO NOTHING;

    -- 4) ingestion_run (status=SUCCESS, records_inserted=5)
    INSERT INTO cegr.ingestion_run
        (id, source_id, started_at, finished_at,
         records_inserted, records_updated, records_skipped,
         status, error_message, run_kind)
    VALUES
        (v_run_id, v_registry_id,
         '2026-09-02'::timestamp, '2026-09-02'::timestamp,
         5, 0, 0,
         'SUCCESS', NULL,
         'U6_HONGHEIKU_REPRINT_BATCH')
    ON CONFLICT (id) DO NOTHING;
    -- observation GDP_ANNUAL: 53231.0 亿元
    INSERT INTO cegr.observation
        (id, indicator_id, indicator_methodology_version_id,
         geo_entity_id, geo_code_version_id, calendar_period_id,
         value, raw_value, is_imputed, missing_reason,
         unit, comparison_basis, value_type, status,
         source_id, source_location_id, ingestion_run_id,
         extracted_at, extraction_method, confidence, notes)
    VALUES
        ('q6eebc99-000d-4000-8000-000000000065',
         'a2000000-0000-0000-0000-00000000a001', 'a2000000-0000-0000-0000-00000000a002',
         v_geo_entity_id, v_geo_cv_id, 'a2000000-0000-0000-0000-000020240101',
         53231.0, '53231.0', FALSE, NULL,
         '亿元', 'YEAR_OVER_YEAR', 'REAL', 'PUBLISHED',
         v_registry_id, v_loc_id, v_run_id,
         '2026-09-02'::timestamp, 'REGEX_ANCHORED', 1.0,
         'hunan GDP_ANNUAL 53231.0 亿元;hongheiku 转载;U6 裁定;lineage 三重标注')
    ON CONFLICT (id) DO NOTHING;
    -- observation GDP_GROWTH: 4.8 %
    INSERT INTO cegr.observation
        (id, indicator_id, indicator_methodology_version_id,
         geo_entity_id, geo_code_version_id, calendar_period_id,
         value, raw_value, is_imputed, missing_reason,
         unit, comparison_basis, value_type, status,
         source_id, source_location_id, ingestion_run_id,
         extracted_at, extraction_method, confidence, notes)
    VALUES
        ('q6eebc99-000d-4000-8000-000000000066',
         'a2000000-0000-0000-0000-00000000a003', 'a2000000-0000-0000-0000-00000000a007',
         v_geo_entity_id, v_geo_cv_id, 'a2000000-0000-0000-0000-000020240101',
         4.8, '4.8', FALSE, NULL,
         '%', 'YEAR_OVER_YEAR', 'REAL', 'PUBLISHED',
         v_registry_id, v_loc_id, v_run_id,
         '2026-09-02'::timestamp, 'REGEX_ANCHORED', 1.0,
         'hunan GDP_GROWTH 4.8 %;hongheiku 转载;U6 裁定;lineage 三重标注')
    ON CONFLICT (id) DO NOTHING;
    -- observation GVA_PRIMARY: 4899.7 亿元
    INSERT INTO cegr.observation
        (id, indicator_id, indicator_methodology_version_id,
         geo_entity_id, geo_code_version_id, calendar_period_id,
         value, raw_value, is_imputed, missing_reason,
         unit, comparison_basis, value_type, status,
         source_id, source_location_id, ingestion_run_id,
         extracted_at, extraction_method, confidence, notes)
    VALUES
        ('q6eebc99-000d-4000-8000-000000000067',
         'a2000000-0000-0000-0000-00000000a004', 'a2000000-0000-0000-0000-00000000a008',
         v_geo_entity_id, v_geo_cv_id, 'a2000000-0000-0000-0000-000020240101',
         4899.7, '4899.7', FALSE, NULL,
         '亿元', 'YEAR_OVER_YEAR', 'REAL', 'PUBLISHED',
         v_registry_id, v_loc_id, v_run_id,
         '2026-09-02'::timestamp, 'REGEX_ANCHORED', 1.0,
         'hunan GVA_PRIMARY 4899.7 亿元;hongheiku 转载;U6 裁定;lineage 三重标注')
    ON CONFLICT (id) DO NOTHING;
    -- observation GVA_SECONDARY: 19534.6 亿元
    INSERT INTO cegr.observation
        (id, indicator_id, indicator_methodology_version_id,
         geo_entity_id, geo_code_version_id, calendar_period_id,
         value, raw_value, is_imputed, missing_reason,
         unit, comparison_basis, value_type, status,
         source_id, source_location_id, ingestion_run_id,
         extracted_at, extraction_method, confidence, notes)
    VALUES
        ('q6eebc99-000d-4000-8000-000000000068',
         'a2000000-0000-0000-0000-00000000a005', 'a2000000-0000-0000-0000-00000000a009',
         v_geo_entity_id, v_geo_cv_id, 'a2000000-0000-0000-0000-000020240101',
         19534.6, '19534.6', FALSE, NULL,
         '亿元', 'YEAR_OVER_YEAR', 'REAL', 'PUBLISHED',
         v_registry_id, v_loc_id, v_run_id,
         '2026-09-02'::timestamp, 'REGEX_ANCHORED', 1.0,
         'hunan GVA_SECONDARY 19534.6 亿元;hongheiku 转载;U6 裁定;lineage 三重标注')
    ON CONFLICT (id) DO NOTHING;
    -- observation GVA_TERTIARY: 28796.7 亿元
    INSERT INTO cegr.observation
        (id, indicator_id, indicator_methodology_version_id,
         geo_entity_id, geo_code_version_id, calendar_period_id,
         value, raw_value, is_imputed, missing_reason,
         unit, comparison_basis, value_type, status,
         source_id, source_location_id, ingestion_run_id,
         extracted_at, extraction_method, confidence, notes)
    VALUES
        ('q6eebc99-000d-4000-8000-000000000069',
         'a2000000-0000-0000-0000-00000000a006', 'a2000000-0000-0000-0000-00000000a010',
         v_geo_entity_id, v_geo_cv_id, 'a2000000-0000-0000-0000-000020240101',
         28796.7, '28796.7', FALSE, NULL,
         '亿元', 'YEAR_OVER_YEAR', 'REAL', 'PUBLISHED',
         v_registry_id, v_loc_id, v_run_id,
         '2026-09-02'::timestamp, 'REGEX_ANCHORED', 1.0,
         'hunan GVA_TERTIARY 28796.7 亿元;hongheiku 转载;U6 裁定;lineage 三重标注')
    ON CONFLICT (id) DO NOTHING;
END $$;

-- Province 15: guangdong (广东省, admin_code=44, idx=14)
DO $$
DECLARE
    v_registry_id UUID := 'q0eebc99-000e-4000-8000-000000000014';
    v_doc_id UUID := 'q1eebc99-000e-4000-8000-000000000014';
    v_loc_id UUID := 'q2eebc99-000e-4000-8000-000000000014';
    v_run_id UUID := 'q7eebc99-000e-4000-8000-000000000014';
    v_geo_entity_id UUID := 'a2000000-0000-0000-0000-000000000044';
    v_geo_cv_id UUID := 'a2000000-0000-0000-0000-00000000004401';
BEGIN
    -- 1) source_registry (hongheiku_tjgb, origin=广东省统计局)
    INSERT INTO cegr.source_registry
        (id, domain, organization, category, primary_url,
         update_frequency, auth_note, access_method,
         historical_coverage, stability_note, failure_handling,
         enabled, source_level,
         lineage)
    VALUES
        (v_registry_id, 'tjgb.hongheiku.com',
         'hongheiku 转载 (origin: 广东省统计局)', 'PROVINCIAL_BULLETIN_REPRINT',
         'https://tjgb.hongheiku.com/sjtjgb/57657.html', 'ANNUAL',
         '公开转载;hongheiku 红黑统计公报库;U6 用户裁定接受',
         'HTTP_CURL', '2024 年度公报',
         'U6 金丝雀 5/5 PASS (京/沪/鲁/鄂/川 delta=0 全等)',
         'BLOCKED_NO_POOL 留痕不代换 (红线 14)',
         TRUE, 'S2_REPRINT',
         jsonb_build_object(
             'chain_id', 'real_658_m2_u6_batch_v1'::text,
             'knife', '658',
             'source', 'hongheiku_tjgb',
             'origin', '广东省统计局',
             'ruling', 'U6 2026-09-02',
             'cross_reference', '金丝雀 5/5 全等 (京/沪/鲁/鄂/川)',
             'reprint', TRUE,
             'extraction_method', 'category_first_url_discovery'
         ))
    ON CONFLICT (id) DO NOTHING;

    -- 2) source_document (file SHA 锁转载字节)
    INSERT INTO cegr.source_document
        (id, source_id, file_path, file_size_bytes, file_hash_sha256,
         mime_type, retrieval_method, retrieval_at, raw_content_ref)
    VALUES
        (v_doc_id, v_registry_id,
         '/tmp/_658_guangdong.html',
         62776,
         '656aa9adf8cc14bacb08bf799892e6dc0d00ada03ab985229b8f36de11f3eb4f',
         'text/html', 'HTTP_CURL',
         '2026-09-02'::timestamp,
         'evidence_pack/u6_batch_26prov_fetch_20260902.json#guangdong')
    ON CONFLICT (id) DO NOTHING;

    -- 3) source_location (URL + http_code 200)
    INSERT INTO cegr.source_location
        (id, source_id, location_type, url, http_code,
         accessed_at, content_hash, notes)
    VALUES
        (v_loc_id, v_registry_id, 'PRIMARY_URL',
         'https://tjgb.hongheiku.com/sjtjgb/57657.html', 200,
         '2026-09-02'::timestamp,
         '656aa9adf8cc14bacb08bf799892e6dc0d00ada03ab985229b8f36de11f3eb4f',
         'hongheiku 转载页; 2024 年度公报; 1 HTTP (cache hit post-1st)')
    ON CONFLICT (id) DO NOTHING;

    -- 4) ingestion_run (status=SUCCESS, records_inserted=5)
    INSERT INTO cegr.ingestion_run
        (id, source_id, started_at, finished_at,
         records_inserted, records_updated, records_skipped,
         status, error_message, run_kind)
    VALUES
        (v_run_id, v_registry_id,
         '2026-09-02'::timestamp, '2026-09-02'::timestamp,
         5, 0, 0,
         'SUCCESS', NULL,
         'U6_HONGHEIKU_REPRINT_BATCH')
    ON CONFLICT (id) DO NOTHING;
    -- observation GDP_ANNUAL: 141633.81 亿元
    INSERT INTO cegr.observation
        (id, indicator_id, indicator_methodology_version_id,
         geo_entity_id, geo_code_version_id, calendar_period_id,
         value, raw_value, is_imputed, missing_reason,
         unit, comparison_basis, value_type, status,
         source_id, source_location_id, ingestion_run_id,
         extracted_at, extraction_method, confidence, notes)
    VALUES
        ('q6eebc99-000e-4000-8000-000000000070',
         'a2000000-0000-0000-0000-00000000a001', 'a2000000-0000-0000-0000-00000000a002',
         v_geo_entity_id, v_geo_cv_id, 'a2000000-0000-0000-0000-000020240101',
         141633.81, '141633.81', FALSE, NULL,
         '亿元', 'YEAR_OVER_YEAR', 'REAL', 'PUBLISHED',
         v_registry_id, v_loc_id, v_run_id,
         '2026-09-02'::timestamp, 'REGEX_ANCHORED', 1.0,
         'guangdong GDP_ANNUAL 141633.81 亿元;hongheiku 转载;U6 裁定;lineage 三重标注')
    ON CONFLICT (id) DO NOTHING;
    -- observation GDP_GROWTH: 3.5 %
    INSERT INTO cegr.observation
        (id, indicator_id, indicator_methodology_version_id,
         geo_entity_id, geo_code_version_id, calendar_period_id,
         value, raw_value, is_imputed, missing_reason,
         unit, comparison_basis, value_type, status,
         source_id, source_location_id, ingestion_run_id,
         extracted_at, extraction_method, confidence, notes)
    VALUES
        ('q6eebc99-000e-4000-8000-000000000071',
         'a2000000-0000-0000-0000-00000000a003', 'a2000000-0000-0000-0000-00000000a007',
         v_geo_entity_id, v_geo_cv_id, 'a2000000-0000-0000-0000-000020240101',
         3.5, '3.5', FALSE, NULL,
         '%', 'YEAR_OVER_YEAR', 'REAL', 'PUBLISHED',
         v_registry_id, v_loc_id, v_run_id,
         '2026-09-02'::timestamp, 'REGEX_ANCHORED', 1.0,
         'guangdong GDP_GROWTH 3.5 %;hongheiku 转载;U6 裁定;lineage 三重标注')
    ON CONFLICT (id) DO NOTHING;
    -- observation GVA_PRIMARY: 5837.03 亿元
    INSERT INTO cegr.observation
        (id, indicator_id, indicator_methodology_version_id,
         geo_entity_id, geo_code_version_id, calendar_period_id,
         value, raw_value, is_imputed, missing_reason,
         unit, comparison_basis, value_type, status,
         source_id, source_location_id, ingestion_run_id,
         extracted_at, extraction_method, confidence, notes)
    VALUES
        ('q6eebc99-000e-4000-8000-000000000072',
         'a2000000-0000-0000-0000-00000000a004', 'a2000000-0000-0000-0000-00000000a008',
         v_geo_entity_id, v_geo_cv_id, 'a2000000-0000-0000-0000-000020240101',
         5837.03, '5837.03', FALSE, NULL,
         '亿元', 'YEAR_OVER_YEAR', 'REAL', 'PUBLISHED',
         v_registry_id, v_loc_id, v_run_id,
         '2026-09-02'::timestamp, 'REGEX_ANCHORED', 1.0,
         'guangdong GVA_PRIMARY 5837.03 亿元;hongheiku 转载;U6 裁定;lineage 三重标注')
    ON CONFLICT (id) DO NOTHING;
    -- observation GVA_SECONDARY: 54365.47 亿元
    INSERT INTO cegr.observation
        (id, indicator_id, indicator_methodology_version_id,
         geo_entity_id, geo_code_version_id, calendar_period_id,
         value, raw_value, is_imputed, missing_reason,
         unit, comparison_basis, value_type, status,
         source_id, source_location_id, ingestion_run_id,
         extracted_at, extraction_method, confidence, notes)
    VALUES
        ('q6eebc99-000e-4000-8000-000000000073',
         'a2000000-0000-0000-0000-00000000a005', 'a2000000-0000-0000-0000-00000000a009',
         v_geo_entity_id, v_geo_cv_id, 'a2000000-0000-0000-0000-000020240101',
         54365.47, '54365.47', FALSE, NULL,
         '亿元', 'YEAR_OVER_YEAR', 'REAL', 'PUBLISHED',
         v_registry_id, v_loc_id, v_run_id,
         '2026-09-02'::timestamp, 'REGEX_ANCHORED', 1.0,
         'guangdong GVA_SECONDARY 54365.47 亿元;hongheiku 转载;U6 裁定;lineage 三重标注')
    ON CONFLICT (id) DO NOTHING;
    -- observation GVA_TERTIARY: 81431.31 亿元
    INSERT INTO cegr.observation
        (id, indicator_id, indicator_methodology_version_id,
         geo_entity_id, geo_code_version_id, calendar_period_id,
         value, raw_value, is_imputed, missing_reason,
         unit, comparison_basis, value_type, status,
         source_id, source_location_id, ingestion_run_id,
         extracted_at, extraction_method, confidence, notes)
    VALUES
        ('q6eebc99-000e-4000-8000-000000000074',
         'a2000000-0000-0000-0000-00000000a006', 'a2000000-0000-0000-0000-00000000a010',
         v_geo_entity_id, v_geo_cv_id, 'a2000000-0000-0000-0000-000020240101',
         81431.31, '81431.31', FALSE, NULL,
         '亿元', 'YEAR_OVER_YEAR', 'REAL', 'PUBLISHED',
         v_registry_id, v_loc_id, v_run_id,
         '2026-09-02'::timestamp, 'REGEX_ANCHORED', 1.0,
         'guangdong GVA_TERTIARY 81431.31 亿元;hongheiku 转载;U6 裁定;lineage 三重标注')
    ON CONFLICT (id) DO NOTHING;
END $$;

-- Province 16: guangxi (广西壮族自治区, admin_code=45, idx=15)
DO $$
DECLARE
    v_registry_id UUID := 'q0eebc99-000f-4000-8000-000000000015';
    v_doc_id UUID := 'q1eebc99-000f-4000-8000-000000000015';
    v_loc_id UUID := 'q2eebc99-000f-4000-8000-000000000015';
    v_run_id UUID := 'q7eebc99-000f-4000-8000-000000000015';
    v_geo_entity_id UUID := 'a2000000-0000-0000-0000-000000000045';
    v_geo_cv_id UUID := 'a2000000-0000-0000-0000-00000000004501';
BEGIN
    -- 1) source_registry (hongheiku_tjgb, origin=广西壮族自治区统计局)
    INSERT INTO cegr.source_registry
        (id, domain, organization, category, primary_url,
         update_frequency, auth_note, access_method,
         historical_coverage, stability_note, failure_handling,
         enabled, source_level,
         lineage)
    VALUES
        (v_registry_id, 'tjgb.hongheiku.com',
         'hongheiku 转载 (origin: 广西壮族自治区统计局)', 'PROVINCIAL_BULLETIN_REPRINT',
         'https://tjgb.hongheiku.com/sjtjgb/58355.html', 'ANNUAL',
         '公开转载;hongheiku 红黑统计公报库;U6 用户裁定接受',
         'HTTP_CURL', '2024 年度公报',
         'U6 金丝雀 5/5 PASS (京/沪/鲁/鄂/川 delta=0 全等)',
         'BLOCKED_NO_POOL 留痕不代换 (红线 14)',
         TRUE, 'S2_REPRINT',
         jsonb_build_object(
             'chain_id', 'real_658_m2_u6_batch_v1'::text,
             'knife', '658',
             'source', 'hongheiku_tjgb',
             'origin', '广西壮族自治区统计局',
             'ruling', 'U6 2026-09-02',
             'cross_reference', '金丝雀 5/5 全等 (京/沪/鲁/鄂/川)',
             'reprint', TRUE,
             'extraction_method', 'category_first_url_discovery'
         ))
    ON CONFLICT (id) DO NOTHING;

    -- 2) source_document (file SHA 锁转载字节)
    INSERT INTO cegr.source_document
        (id, source_id, file_path, file_size_bytes, file_hash_sha256,
         mime_type, retrieval_method, retrieval_at, raw_content_ref)
    VALUES
        (v_doc_id, v_registry_id,
         '/tmp/_658_guangxi.html',
         102996,
         '8a56e74e971f213098dae71b6d9e12705326eca65de45faea3fb4e95c62fdbf3',
         'text/html', 'HTTP_CURL',
         '2026-09-02'::timestamp,
         'evidence_pack/u6_batch_26prov_fetch_20260902.json#guangxi')
    ON CONFLICT (id) DO NOTHING;

    -- 3) source_location (URL + http_code 200)
    INSERT INTO cegr.source_location
        (id, source_id, location_type, url, http_code,
         accessed_at, content_hash, notes)
    VALUES
        (v_loc_id, v_registry_id, 'PRIMARY_URL',
         'https://tjgb.hongheiku.com/sjtjgb/58355.html', 200,
         '2026-09-02'::timestamp,
         '8a56e74e971f213098dae71b6d9e12705326eca65de45faea3fb4e95c62fdbf3',
         'hongheiku 转载页; 2024 年度公报; 1 HTTP (cache hit post-1st)')
    ON CONFLICT (id) DO NOTHING;

    -- 4) ingestion_run (status=SUCCESS, records_inserted=5)
    INSERT INTO cegr.ingestion_run
        (id, source_id, started_at, finished_at,
         records_inserted, records_updated, records_skipped,
         status, error_message, run_kind)
    VALUES
        (v_run_id, v_registry_id,
         '2026-09-02'::timestamp, '2026-09-02'::timestamp,
         5, 0, 0,
         'SUCCESS', NULL,
         'U6_HONGHEIKU_REPRINT_BATCH')
    ON CONFLICT (id) DO NOTHING;
    -- observation GDP_ANNUAL: 28649.4 亿元
    INSERT INTO cegr.observation
        (id, indicator_id, indicator_methodology_version_id,
         geo_entity_id, geo_code_version_id, calendar_period_id,
         value, raw_value, is_imputed, missing_reason,
         unit, comparison_basis, value_type, status,
         source_id, source_location_id, ingestion_run_id,
         extracted_at, extraction_method, confidence, notes)
    VALUES
        ('q6eebc99-000f-4000-8000-000000000075',
         'a2000000-0000-0000-0000-00000000a001', 'a2000000-0000-0000-0000-00000000a002',
         v_geo_entity_id, v_geo_cv_id, 'a2000000-0000-0000-0000-000020240101',
         28649.4, '28649.4', FALSE, NULL,
         '亿元', 'YEAR_OVER_YEAR', 'REAL', 'PUBLISHED',
         v_registry_id, v_loc_id, v_run_id,
         '2026-09-02'::timestamp, 'REGEX_ANCHORED', 1.0,
         'guangxi GDP_ANNUAL 28649.4 亿元;hongheiku 转载;U6 裁定;lineage 三重标注')
    ON CONFLICT (id) DO NOTHING;
    -- observation GDP_GROWTH: 4.2 %
    INSERT INTO cegr.observation
        (id, indicator_id, indicator_methodology_version_id,
         geo_entity_id, geo_code_version_id, calendar_period_id,
         value, raw_value, is_imputed, missing_reason,
         unit, comparison_basis, value_type, status,
         source_id, source_location_id, ingestion_run_id,
         extracted_at, extraction_method, confidence, notes)
    VALUES
        ('q6eebc99-000f-4000-8000-000000000076',
         'a2000000-0000-0000-0000-00000000a003', 'a2000000-0000-0000-0000-00000000a007',
         v_geo_entity_id, v_geo_cv_id, 'a2000000-0000-0000-0000-000020240101',
         4.2, '4.2', FALSE, NULL,
         '%', 'YEAR_OVER_YEAR', 'REAL', 'PUBLISHED',
         v_registry_id, v_loc_id, v_run_id,
         '2026-09-02'::timestamp, 'REGEX_ANCHORED', 1.0,
         'guangxi GDP_GROWTH 4.2 %;hongheiku 转载;U6 裁定;lineage 三重标注')
    ON CONFLICT (id) DO NOTHING;
    -- observation GVA_PRIMARY: 4751.54 亿元
    INSERT INTO cegr.observation
        (id, indicator_id, indicator_methodology_version_id,
         geo_entity_id, geo_code_version_id, calendar_period_id,
         value, raw_value, is_imputed, missing_reason,
         unit, comparison_basis, value_type, status,
         source_id, source_location_id, ingestion_run_id,
         extracted_at, extraction_method, confidence, notes)
    VALUES
        ('q6eebc99-000f-4000-8000-000000000077',
         'a2000000-0000-0000-0000-00000000a004', 'a2000000-0000-0000-0000-00000000a008',
         v_geo_entity_id, v_geo_cv_id, 'a2000000-0000-0000-0000-000020240101',
         4751.54, '4751.54', FALSE, NULL,
         '亿元', 'YEAR_OVER_YEAR', 'REAL', 'PUBLISHED',
         v_registry_id, v_loc_id, v_run_id,
         '2026-09-02'::timestamp, 'REGEX_ANCHORED', 1.0,
         'guangxi GVA_PRIMARY 4751.54 亿元;hongheiku 转载;U6 裁定;lineage 三重标注')
    ON CONFLICT (id) DO NOTHING;
    -- observation GVA_SECONDARY: 9300.99 亿元
    INSERT INTO cegr.observation
        (id, indicator_id, indicator_methodology_version_id,
         geo_entity_id, geo_code_version_id, calendar_period_id,
         value, raw_value, is_imputed, missing_reason,
         unit, comparison_basis, value_type, status,
         source_id, source_location_id, ingestion_run_id,
         extracted_at, extraction_method, confidence, notes)
    VALUES
        ('q6eebc99-000f-4000-8000-000000000078',
         'a2000000-0000-0000-0000-00000000a005', 'a2000000-0000-0000-0000-00000000a009',
         v_geo_entity_id, v_geo_cv_id, 'a2000000-0000-0000-0000-000020240101',
         9300.99, '9300.99', FALSE, NULL,
         '亿元', 'YEAR_OVER_YEAR', 'REAL', 'PUBLISHED',
         v_registry_id, v_loc_id, v_run_id,
         '2026-09-02'::timestamp, 'REGEX_ANCHORED', 1.0,
         'guangxi GVA_SECONDARY 9300.99 亿元;hongheiku 转载;U6 裁定;lineage 三重标注')
    ON CONFLICT (id) DO NOTHING;
    -- observation GVA_TERTIARY: 14596.87 亿元
    INSERT INTO cegr.observation
        (id, indicator_id, indicator_methodology_version_id,
         geo_entity_id, geo_code_version_id, calendar_period_id,
         value, raw_value, is_imputed, missing_reason,
         unit, comparison_basis, value_type, status,
         source_id, source_location_id, ingestion_run_id,
         extracted_at, extraction_method, confidence, notes)
    VALUES
        ('q6eebc99-000f-4000-8000-000000000079',
         'a2000000-0000-0000-0000-00000000a006', 'a2000000-0000-0000-0000-00000000a010',
         v_geo_entity_id, v_geo_cv_id, 'a2000000-0000-0000-0000-000020240101',
         14596.87, '14596.87', FALSE, NULL,
         '亿元', 'YEAR_OVER_YEAR', 'REAL', 'PUBLISHED',
         v_registry_id, v_loc_id, v_run_id,
         '2026-09-02'::timestamp, 'REGEX_ANCHORED', 1.0,
         'guangxi GVA_TERTIARY 14596.87 亿元;hongheiku 转载;U6 裁定;lineage 三重标注')
    ON CONFLICT (id) DO NOTHING;
END $$;

-- Province 17: yunnan (云南省, admin_code=53, idx=16)
DO $$
DECLARE
    v_registry_id UUID := 'q0eebc99-0010-4000-8000-000000000016';
    v_doc_id UUID := 'q1eebc99-0010-4000-8000-000000000016';
    v_loc_id UUID := 'q2eebc99-0010-4000-8000-000000000016';
    v_run_id UUID := 'q7eebc99-0010-4000-8000-000000000016';
    v_geo_entity_id UUID := 'a2000000-0000-0000-0000-000000000053';
    v_geo_cv_id UUID := 'a2000000-0000-0000-0000-00000000005301';
BEGIN
    -- 1) source_registry (hongheiku_tjgb, origin=云南省统计局)
    INSERT INTO cegr.source_registry
        (id, domain, organization, category, primary_url,
         update_frequency, auth_note, access_method,
         historical_coverage, stability_note, failure_handling,
         enabled, source_level,
         lineage)
    VALUES
        (v_registry_id, 'tjgb.hongheiku.com',
         'hongheiku 转载 (origin: 云南省统计局)', 'PROVINCIAL_BULLETIN_REPRINT',
         'https://tjgb.hongheiku.com/sjtjgb/58560.html', 'ANNUAL',
         '公开转载;hongheiku 红黑统计公报库;U6 用户裁定接受',
         'HTTP_CURL', '2024 年度公报',
         'U6 金丝雀 5/5 PASS (京/沪/鲁/鄂/川 delta=0 全等)',
         'BLOCKED_NO_POOL 留痕不代换 (红线 14)',
         TRUE, 'S2_REPRINT',
         jsonb_build_object(
             'chain_id', 'real_658_m2_u6_batch_v1'::text,
             'knife', '658',
             'source', 'hongheiku_tjgb',
             'origin', '云南省统计局',
             'ruling', 'U6 2026-09-02',
             'cross_reference', '金丝雀 5/5 全等 (京/沪/鲁/鄂/川)',
             'reprint', TRUE,
             'extraction_method', 'category_first_url_discovery'
         ))
    ON CONFLICT (id) DO NOTHING;

    -- 2) source_document (file SHA 锁转载字节)
    INSERT INTO cegr.source_document
        (id, source_id, file_path, file_size_bytes, file_hash_sha256,
         mime_type, retrieval_method, retrieval_at, raw_content_ref)
    VALUES
        (v_doc_id, v_registry_id,
         '/tmp/_658_yunnan.html',
         67609,
         'c7617a63042d17aa3ccd8d2359e461628d09cd4ee13ae2065c138feedbccd8a8',
         'text/html', 'HTTP_CURL',
         '2026-09-02'::timestamp,
         'evidence_pack/u6_batch_26prov_fetch_20260902.json#yunnan')
    ON CONFLICT (id) DO NOTHING;

    -- 3) source_location (URL + http_code 200)
    INSERT INTO cegr.source_location
        (id, source_id, location_type, url, http_code,
         accessed_at, content_hash, notes)
    VALUES
        (v_loc_id, v_registry_id, 'PRIMARY_URL',
         'https://tjgb.hongheiku.com/sjtjgb/58560.html', 200,
         '2026-09-02'::timestamp,
         'c7617a63042d17aa3ccd8d2359e461628d09cd4ee13ae2065c138feedbccd8a8',
         'hongheiku 转载页; 2024 年度公报; 1 HTTP (cache hit post-1st)')
    ON CONFLICT (id) DO NOTHING;

    -- 4) ingestion_run (status=SUCCESS, records_inserted=5)
    INSERT INTO cegr.ingestion_run
        (id, source_id, started_at, finished_at,
         records_inserted, records_updated, records_skipped,
         status, error_message, run_kind)
    VALUES
        (v_run_id, v_registry_id,
         '2026-09-02'::timestamp, '2026-09-02'::timestamp,
         5, 0, 0,
         'SUCCESS', NULL,
         'U6_HONGHEIKU_REPRINT_BATCH')
    ON CONFLICT (id) DO NOTHING;
    -- observation GDP_ANNUAL: 31534.1 亿元
    INSERT INTO cegr.observation
        (id, indicator_id, indicator_methodology_version_id,
         geo_entity_id, geo_code_version_id, calendar_period_id,
         value, raw_value, is_imputed, missing_reason,
         unit, comparison_basis, value_type, status,
         source_id, source_location_id, ingestion_run_id,
         extracted_at, extraction_method, confidence, notes)
    VALUES
        ('q6eebc99-0010-4000-8000-000000000080',
         'a2000000-0000-0000-0000-00000000a001', 'a2000000-0000-0000-0000-00000000a002',
         v_geo_entity_id, v_geo_cv_id, 'a2000000-0000-0000-0000-000020240101',
         31534.1, '31534.1', FALSE, NULL,
         '亿元', 'YEAR_OVER_YEAR', 'REAL', 'PUBLISHED',
         v_registry_id, v_loc_id, v_run_id,
         '2026-09-02'::timestamp, 'REGEX_ANCHORED', 1.0,
         'yunnan GDP_ANNUAL 31534.1 亿元;hongheiku 转载;U6 裁定;lineage 三重标注')
    ON CONFLICT (id) DO NOTHING;
    -- observation GDP_GROWTH: 3.3 %
    INSERT INTO cegr.observation
        (id, indicator_id, indicator_methodology_version_id,
         geo_entity_id, geo_code_version_id, calendar_period_id,
         value, raw_value, is_imputed, missing_reason,
         unit, comparison_basis, value_type, status,
         source_id, source_location_id, ingestion_run_id,
         extracted_at, extraction_method, confidence, notes)
    VALUES
        ('q6eebc99-0010-4000-8000-000000000081',
         'a2000000-0000-0000-0000-00000000a003', 'a2000000-0000-0000-0000-00000000a007',
         v_geo_entity_id, v_geo_cv_id, 'a2000000-0000-0000-0000-000020240101',
         3.3, '3.3', FALSE, NULL,
         '%', 'YEAR_OVER_YEAR', 'REAL', 'PUBLISHED',
         v_registry_id, v_loc_id, v_run_id,
         '2026-09-02'::timestamp, 'REGEX_ANCHORED', 1.0,
         'yunnan GDP_GROWTH 3.3 %;hongheiku 转载;U6 裁定;lineage 三重标注')
    ON CONFLICT (id) DO NOTHING;
    -- observation GVA_PRIMARY: 4193.0 亿元
    INSERT INTO cegr.observation
        (id, indicator_id, indicator_methodology_version_id,
         geo_entity_id, geo_code_version_id, calendar_period_id,
         value, raw_value, is_imputed, missing_reason,
         unit, comparison_basis, value_type, status,
         source_id, source_location_id, ingestion_run_id,
         extracted_at, extraction_method, confidence, notes)
    VALUES
        ('q6eebc99-0010-4000-8000-000000000082',
         'a2000000-0000-0000-0000-00000000a004', 'a2000000-0000-0000-0000-00000000a008',
         v_geo_entity_id, v_geo_cv_id, 'a2000000-0000-0000-0000-000020240101',
         4193.0, '4193.0', FALSE, NULL,
         '亿元', 'YEAR_OVER_YEAR', 'REAL', 'PUBLISHED',
         v_registry_id, v_loc_id, v_run_id,
         '2026-09-02'::timestamp, 'REGEX_ANCHORED', 1.0,
         'yunnan GVA_PRIMARY 4193.0 亿元;hongheiku 转载;U6 裁定;lineage 三重标注')
    ON CONFLICT (id) DO NOTHING;
    -- observation GVA_SECONDARY: 10330.0 亿元
    INSERT INTO cegr.observation
        (id, indicator_id, indicator_methodology_version_id,
         geo_entity_id, geo_code_version_id, calendar_period_id,
         value, raw_value, is_imputed, missing_reason,
         unit, comparison_basis, value_type, status,
         source_id, source_location_id, ingestion_run_id,
         extracted_at, extraction_method, confidence, notes)
    VALUES
        ('q6eebc99-0010-4000-8000-000000000083',
         'a2000000-0000-0000-0000-00000000a005', 'a2000000-0000-0000-0000-00000000a009',
         v_geo_entity_id, v_geo_cv_id, 'a2000000-0000-0000-0000-000020240101',
         10330.0, '10330.0', FALSE, NULL,
         '亿元', 'YEAR_OVER_YEAR', 'REAL', 'PUBLISHED',
         v_registry_id, v_loc_id, v_run_id,
         '2026-09-02'::timestamp, 'REGEX_ANCHORED', 1.0,
         'yunnan GVA_SECONDARY 10330.0 亿元;hongheiku 转载;U6 裁定;lineage 三重标注')
    ON CONFLICT (id) DO NOTHING;
    -- observation GVA_TERTIARY: 17011.0 亿元
    INSERT INTO cegr.observation
        (id, indicator_id, indicator_methodology_version_id,
         geo_entity_id, geo_code_version_id, calendar_period_id,
         value, raw_value, is_imputed, missing_reason,
         unit, comparison_basis, value_type, status,
         source_id, source_location_id, ingestion_run_id,
         extracted_at, extraction_method, confidence, notes)
    VALUES
        ('q6eebc99-0010-4000-8000-000000000084',
         'a2000000-0000-0000-0000-00000000a006', 'a2000000-0000-0000-0000-00000000a010',
         v_geo_entity_id, v_geo_cv_id, 'a2000000-0000-0000-0000-000020240101',
         17011.0, '17011.0', FALSE, NULL,
         '亿元', 'YEAR_OVER_YEAR', 'REAL', 'PUBLISHED',
         v_registry_id, v_loc_id, v_run_id,
         '2026-09-02'::timestamp, 'REGEX_ANCHORED', 1.0,
         'yunnan GVA_TERTIARY 17011.0 亿元;hongheiku 转载;U6 裁定;lineage 三重标注')
    ON CONFLICT (id) DO NOTHING;
END $$;

-- Province 18: xizang (西藏自治区, admin_code=54, idx=17)
DO $$
DECLARE
    v_registry_id UUID := 'q0eebc99-0011-4000-8000-000000000017';
    v_doc_id UUID := 'q1eebc99-0011-4000-8000-000000000017';
    v_loc_id UUID := 'q2eebc99-0011-4000-8000-000000000017';
    v_run_id UUID := 'q7eebc99-0011-4000-8000-000000000017';
    v_geo_entity_id UUID := 'a2000000-0000-0000-0000-000000000054';
    v_geo_cv_id UUID := 'a2000000-0000-0000-0000-00000000005401';
BEGIN
    -- 1) source_registry (hongheiku_tjgb, origin=西藏自治区统计局)
    INSERT INTO cegr.source_registry
        (id, domain, organization, category, primary_url,
         update_frequency, auth_note, access_method,
         historical_coverage, stability_note, failure_handling,
         enabled, source_level,
         lineage)
    VALUES
        (v_registry_id, 'tjgb.hongheiku.com',
         'hongheiku 转载 (origin: 西藏自治区统计局)', 'PROVINCIAL_BULLETIN_REPRINT',
         'https://tjgb.hongheiku.com/sjtjgb/58383.html', 'ANNUAL',
         '公开转载;hongheiku 红黑统计公报库;U6 用户裁定接受',
         'HTTP_CURL', '2024 年度公报',
         'U6 金丝雀 5/5 PASS (京/沪/鲁/鄂/川 delta=0 全等)',
         'BLOCKED_NO_POOL 留痕不代换 (红线 14)',
         TRUE, 'S2_REPRINT',
         jsonb_build_object(
             'chain_id', 'real_658_m2_u6_batch_v1'::text,
             'knife', '658',
             'source', 'hongheiku_tjgb',
             'origin', '西藏自治区统计局',
             'ruling', 'U6 2026-09-02',
             'cross_reference', '金丝雀 5/5 全等 (京/沪/鲁/鄂/川)',
             'reprint', TRUE,
             'extraction_method', 'category_first_url_discovery'
         ))
    ON CONFLICT (id) DO NOTHING;

    -- 2) source_document (file SHA 锁转载字节)
    INSERT INTO cegr.source_document
        (id, source_id, file_path, file_size_bytes, file_hash_sha256,
         mime_type, retrieval_method, retrieval_at, raw_content_ref)
    VALUES
        (v_doc_id, v_registry_id,
         '/tmp/_658_xizang.html',
         46448,
         '0025e560f3740e04af8be671ce82564617528d202b3dba1da19f987ffe2e1430',
         'text/html', 'HTTP_CURL',
         '2026-09-02'::timestamp,
         'evidence_pack/u6_batch_26prov_fetch_20260902.json#xizang')
    ON CONFLICT (id) DO NOTHING;

    -- 3) source_location (URL + http_code 200)
    INSERT INTO cegr.source_location
        (id, source_id, location_type, url, http_code,
         accessed_at, content_hash, notes)
    VALUES
        (v_loc_id, v_registry_id, 'PRIMARY_URL',
         'https://tjgb.hongheiku.com/sjtjgb/58383.html', 200,
         '2026-09-02'::timestamp,
         '0025e560f3740e04af8be671ce82564617528d202b3dba1da19f987ffe2e1430',
         'hongheiku 转载页; 2024 年度公报; 1 HTTP (cache hit post-1st)')
    ON CONFLICT (id) DO NOTHING;

    -- 4) ingestion_run (status=SUCCESS, records_inserted=5)
    INSERT INTO cegr.ingestion_run
        (id, source_id, started_at, finished_at,
         records_inserted, records_updated, records_skipped,
         status, error_message, run_kind)
    VALUES
        (v_run_id, v_registry_id,
         '2026-09-02'::timestamp, '2026-09-02'::timestamp,
         5, 0, 0,
         'SUCCESS', NULL,
         'U6_HONGHEIKU_REPRINT_BATCH')
    ON CONFLICT (id) DO NOTHING;
    -- observation GDP_ANNUAL: 2764.94 亿元
    INSERT INTO cegr.observation
        (id, indicator_id, indicator_methodology_version_id,
         geo_entity_id, geo_code_version_id, calendar_period_id,
         value, raw_value, is_imputed, missing_reason,
         unit, comparison_basis, value_type, status,
         source_id, source_location_id, ingestion_run_id,
         extracted_at, extraction_method, confidence, notes)
    VALUES
        ('q6eebc99-0011-4000-8000-000000000085',
         'a2000000-0000-0000-0000-00000000a001', 'a2000000-0000-0000-0000-00000000a002',
         v_geo_entity_id, v_geo_cv_id, 'a2000000-0000-0000-0000-000020240101',
         2764.94, '2764.94', FALSE, NULL,
         '亿元', 'YEAR_OVER_YEAR', 'REAL', 'PUBLISHED',
         v_registry_id, v_loc_id, v_run_id,
         '2026-09-02'::timestamp, 'REGEX_ANCHORED', 1.0,
         'xizang GDP_ANNUAL 2764.94 亿元;hongheiku 转载;U6 裁定;lineage 三重标注')
    ON CONFLICT (id) DO NOTHING;
    -- observation GDP_GROWTH: 6.3 %
    INSERT INTO cegr.observation
        (id, indicator_id, indicator_methodology_version_id,
         geo_entity_id, geo_code_version_id, calendar_period_id,
         value, raw_value, is_imputed, missing_reason,
         unit, comparison_basis, value_type, status,
         source_id, source_location_id, ingestion_run_id,
         extracted_at, extraction_method, confidence, notes)
    VALUES
        ('q6eebc99-0011-4000-8000-000000000086',
         'a2000000-0000-0000-0000-00000000a003', 'a2000000-0000-0000-0000-00000000a007',
         v_geo_entity_id, v_geo_cv_id, 'a2000000-0000-0000-0000-000020240101',
         6.3, '6.3', FALSE, NULL,
         '%', 'YEAR_OVER_YEAR', 'REAL', 'PUBLISHED',
         v_registry_id, v_loc_id, v_run_id,
         '2026-09-02'::timestamp, 'REGEX_ANCHORED', 1.0,
         'xizang GDP_GROWTH 6.3 %;hongheiku 转载;U6 裁定;lineage 三重标注')
    ON CONFLICT (id) DO NOTHING;
    -- observation GVA_PRIMARY: 247.52 亿元
    INSERT INTO cegr.observation
        (id, indicator_id, indicator_methodology_version_id,
         geo_entity_id, geo_code_version_id, calendar_period_id,
         value, raw_value, is_imputed, missing_reason,
         unit, comparison_basis, value_type, status,
         source_id, source_location_id, ingestion_run_id,
         extracted_at, extraction_method, confidence, notes)
    VALUES
        ('q6eebc99-0011-4000-8000-000000000087',
         'a2000000-0000-0000-0000-00000000a004', 'a2000000-0000-0000-0000-00000000a008',
         v_geo_entity_id, v_geo_cv_id, 'a2000000-0000-0000-0000-000020240101',
         247.52, '247.52', FALSE, NULL,
         '亿元', 'YEAR_OVER_YEAR', 'REAL', 'PUBLISHED',
         v_registry_id, v_loc_id, v_run_id,
         '2026-09-02'::timestamp, 'REGEX_ANCHORED', 1.0,
         'xizang GVA_PRIMARY 247.52 亿元;hongheiku 转载;U6 裁定;lineage 三重标注')
    ON CONFLICT (id) DO NOTHING;
    -- observation GVA_SECONDARY: 1016.07 亿元
    INSERT INTO cegr.observation
        (id, indicator_id, indicator_methodology_version_id,
         geo_entity_id, geo_code_version_id, calendar_period_id,
         value, raw_value, is_imputed, missing_reason,
         unit, comparison_basis, value_type, status,
         source_id, source_location_id, ingestion_run_id,
         extracted_at, extraction_method, confidence, notes)
    VALUES
        ('q6eebc99-0011-4000-8000-000000000088',
         'a2000000-0000-0000-0000-00000000a005', 'a2000000-0000-0000-0000-00000000a009',
         v_geo_entity_id, v_geo_cv_id, 'a2000000-0000-0000-0000-000020240101',
         1016.07, '1016.07', FALSE, NULL,
         '亿元', 'YEAR_OVER_YEAR', 'REAL', 'PUBLISHED',
         v_registry_id, v_loc_id, v_run_id,
         '2026-09-02'::timestamp, 'REGEX_ANCHORED', 1.0,
         'xizang GVA_SECONDARY 1016.07 亿元;hongheiku 转载;U6 裁定;lineage 三重标注')
    ON CONFLICT (id) DO NOTHING;
    -- observation GVA_TERTIARY: 1501.35 亿元
    INSERT INTO cegr.observation
        (id, indicator_id, indicator_methodology_version_id,
         geo_entity_id, geo_code_version_id, calendar_period_id,
         value, raw_value, is_imputed, missing_reason,
         unit, comparison_basis, value_type, status,
         source_id, source_location_id, ingestion_run_id,
         extracted_at, extraction_method, confidence, notes)
    VALUES
        ('q6eebc99-0011-4000-8000-000000000089',
         'a2000000-0000-0000-0000-00000000a006', 'a2000000-0000-0000-0000-00000000a010',
         v_geo_entity_id, v_geo_cv_id, 'a2000000-0000-0000-0000-000020240101',
         1501.35, '1501.35', FALSE, NULL,
         '亿元', 'YEAR_OVER_YEAR', 'REAL', 'PUBLISHED',
         v_registry_id, v_loc_id, v_run_id,
         '2026-09-02'::timestamp, 'REGEX_ANCHORED', 1.0,
         'xizang GVA_TERTIARY 1501.35 亿元;hongheiku 转载;U6 裁定;lineage 三重标注')
    ON CONFLICT (id) DO NOTHING;
END $$;

-- Province 19: shaanxi (陕西省, admin_code=61, idx=18)
DO $$
DECLARE
    v_registry_id UUID := 'q0eebc99-0012-4000-8000-000000000018';
    v_doc_id UUID := 'q1eebc99-0012-4000-8000-000000000018';
    v_loc_id UUID := 'q2eebc99-0012-4000-8000-000000000018';
    v_run_id UUID := 'q7eebc99-0012-4000-8000-000000000018';
    v_geo_entity_id UUID := 'a2000000-0000-0000-0000-000000000061';
    v_geo_cv_id UUID := 'a2000000-0000-0000-0000-00000000006101';
BEGIN
    -- 1) source_registry (hongheiku_tjgb, origin=陕西省统计局)
    INSERT INTO cegr.source_registry
        (id, domain, organization, category, primary_url,
         update_frequency, auth_note, access_method,
         historical_coverage, stability_note, failure_handling,
         enabled, source_level,
         lineage)
    VALUES
        (v_registry_id, 'tjgb.hongheiku.com',
         'hongheiku 转载 (origin: 陕西省统计局)', 'PROVINCIAL_BULLETIN_REPRINT',
         'https://tjgb.hongheiku.com/sjtjgb/57236.html', 'ANNUAL',
         '公开转载;hongheiku 红黑统计公报库;U6 用户裁定接受',
         'HTTP_CURL', '2024 年度公报',
         'U6 金丝雀 5/5 PASS (京/沪/鲁/鄂/川 delta=0 全等)',
         'BLOCKED_NO_POOL 留痕不代换 (红线 14)',
         TRUE, 'S2_REPRINT',
         jsonb_build_object(
             'chain_id', 'real_658_m2_u6_batch_v1'::text,
             'knife', '658',
             'source', 'hongheiku_tjgb',
             'origin', '陕西省统计局',
             'ruling', 'U6 2026-09-02',
             'cross_reference', '金丝雀 5/5 全等 (京/沪/鲁/鄂/川)',
             'reprint', TRUE,
             'extraction_method', 'category_first_url_discovery'
         ))
    ON CONFLICT (id) DO NOTHING;

    -- 2) source_document (file SHA 锁转载字节)
    INSERT INTO cegr.source_document
        (id, source_id, file_path, file_size_bytes, file_hash_sha256,
         mime_type, retrieval_method, retrieval_at, raw_content_ref)
    VALUES
        (v_doc_id, v_registry_id,
         '/tmp/_658_shaanxi.html',
         45463,
         '40a2f5600092c316cff527ab8d3596f34eaae73ef8fa643a9a9c9d80f11581c7',
         'text/html', 'HTTP_CURL',
         '2026-09-02'::timestamp,
         'evidence_pack/u6_batch_26prov_fetch_20260902.json#shaanxi')
    ON CONFLICT (id) DO NOTHING;

    -- 3) source_location (URL + http_code 200)
    INSERT INTO cegr.source_location
        (id, source_id, location_type, url, http_code,
         accessed_at, content_hash, notes)
    VALUES
        (v_loc_id, v_registry_id, 'PRIMARY_URL',
         'https://tjgb.hongheiku.com/sjtjgb/57236.html', 200,
         '2026-09-02'::timestamp,
         '40a2f5600092c316cff527ab8d3596f34eaae73ef8fa643a9a9c9d80f11581c7',
         'hongheiku 转载页; 2024 年度公报; 1 HTTP (cache hit post-1st)')
    ON CONFLICT (id) DO NOTHING;

    -- 4) ingestion_run (status=SUCCESS, records_inserted=5)
    INSERT INTO cegr.ingestion_run
        (id, source_id, started_at, finished_at,
         records_inserted, records_updated, records_skipped,
         status, error_message, run_kind)
    VALUES
        (v_run_id, v_registry_id,
         '2026-09-02'::timestamp, '2026-09-02'::timestamp,
         5, 0, 0,
         'SUCCESS', NULL,
         'U6_HONGHEIKU_REPRINT_BATCH')
    ON CONFLICT (id) DO NOTHING;
    -- observation GDP_ANNUAL: 35538.77 亿元
    INSERT INTO cegr.observation
        (id, indicator_id, indicator_methodology_version_id,
         geo_entity_id, geo_code_version_id, calendar_period_id,
         value, raw_value, is_imputed, missing_reason,
         unit, comparison_basis, value_type, status,
         source_id, source_location_id, ingestion_run_id,
         extracted_at, extraction_method, confidence, notes)
    VALUES
        ('q6eebc99-0012-4000-8000-000000000090',
         'a2000000-0000-0000-0000-00000000a001', 'a2000000-0000-0000-0000-00000000a002',
         v_geo_entity_id, v_geo_cv_id, 'a2000000-0000-0000-0000-000020240101',
         35538.77, '35538.77', FALSE, NULL,
         '亿元', 'YEAR_OVER_YEAR', 'REAL', 'PUBLISHED',
         v_registry_id, v_loc_id, v_run_id,
         '2026-09-02'::timestamp, 'REGEX_ANCHORED', 1.0,
         'shaanxi GDP_ANNUAL 35538.77 亿元;hongheiku 转载;U6 裁定;lineage 三重标注')
    ON CONFLICT (id) DO NOTHING;
    -- observation GDP_GROWTH: 5.3 %
    INSERT INTO cegr.observation
        (id, indicator_id, indicator_methodology_version_id,
         geo_entity_id, geo_code_version_id, calendar_period_id,
         value, raw_value, is_imputed, missing_reason,
         unit, comparison_basis, value_type, status,
         source_id, source_location_id, ingestion_run_id,
         extracted_at, extraction_method, confidence, notes)
    VALUES
        ('q6eebc99-0012-4000-8000-000000000091',
         'a2000000-0000-0000-0000-00000000a003', 'a2000000-0000-0000-0000-00000000a007',
         v_geo_entity_id, v_geo_cv_id, 'a2000000-0000-0000-0000-000020240101',
         5.3, '5.3', FALSE, NULL,
         '%', 'YEAR_OVER_YEAR', 'REAL', 'PUBLISHED',
         v_registry_id, v_loc_id, v_run_id,
         '2026-09-02'::timestamp, 'REGEX_ANCHORED', 1.0,
         'shaanxi GDP_GROWTH 5.3 %;hongheiku 转载;U6 裁定;lineage 三重标注')
    ON CONFLICT (id) DO NOTHING;
    -- observation GVA_PRIMARY: 2621.96 亿元
    INSERT INTO cegr.observation
        (id, indicator_id, indicator_methodology_version_id,
         geo_entity_id, geo_code_version_id, calendar_period_id,
         value, raw_value, is_imputed, missing_reason,
         unit, comparison_basis, value_type, status,
         source_id, source_location_id, ingestion_run_id,
         extracted_at, extraction_method, confidence, notes)
    VALUES
        ('q6eebc99-0012-4000-8000-000000000092',
         'a2000000-0000-0000-0000-00000000a004', 'a2000000-0000-0000-0000-00000000a008',
         v_geo_entity_id, v_geo_cv_id, 'a2000000-0000-0000-0000-000020240101',
         2621.96, '2621.96', FALSE, NULL,
         '亿元', 'YEAR_OVER_YEAR', 'REAL', 'PUBLISHED',
         v_registry_id, v_loc_id, v_run_id,
         '2026-09-02'::timestamp, 'REGEX_ANCHORED', 1.0,
         'shaanxi GVA_PRIMARY 2621.96 亿元;hongheiku 转载;U6 裁定;lineage 三重标注')
    ON CONFLICT (id) DO NOTHING;
    -- observation GVA_SECONDARY: 14518.97 亿元
    INSERT INTO cegr.observation
        (id, indicator_id, indicator_methodology_version_id,
         geo_entity_id, geo_code_version_id, calendar_period_id,
         value, raw_value, is_imputed, missing_reason,
         unit, comparison_basis, value_type, status,
         source_id, source_location_id, ingestion_run_id,
         extracted_at, extraction_method, confidence, notes)
    VALUES
        ('q6eebc99-0012-4000-8000-000000000093',
         'a2000000-0000-0000-0000-00000000a005', 'a2000000-0000-0000-0000-00000000a009',
         v_geo_entity_id, v_geo_cv_id, 'a2000000-0000-0000-0000-000020240101',
         14518.97, '14518.97', FALSE, NULL,
         '亿元', 'YEAR_OVER_YEAR', 'REAL', 'PUBLISHED',
         v_registry_id, v_loc_id, v_run_id,
         '2026-09-02'::timestamp, 'REGEX_ANCHORED', 1.0,
         'shaanxi GVA_SECONDARY 14518.97 亿元;hongheiku 转载;U6 裁定;lineage 三重标注')
    ON CONFLICT (id) DO NOTHING;
    -- observation GVA_TERTIARY: 18397.84 亿元
    INSERT INTO cegr.observation
        (id, indicator_id, indicator_methodology_version_id,
         geo_entity_id, geo_code_version_id, calendar_period_id,
         value, raw_value, is_imputed, missing_reason,
         unit, comparison_basis, value_type, status,
         source_id, source_location_id, ingestion_run_id,
         extracted_at, extraction_method, confidence, notes)
    VALUES
        ('q6eebc99-0012-4000-8000-000000000094',
         'a2000000-0000-0000-0000-00000000a006', 'a2000000-0000-0000-0000-00000000a010',
         v_geo_entity_id, v_geo_cv_id, 'a2000000-0000-0000-0000-000020240101',
         18397.84, '18397.84', FALSE, NULL,
         '亿元', 'YEAR_OVER_YEAR', 'REAL', 'PUBLISHED',
         v_registry_id, v_loc_id, v_run_id,
         '2026-09-02'::timestamp, 'REGEX_ANCHORED', 1.0,
         'shaanxi GVA_TERTIARY 18397.84 亿元;hongheiku 转载;U6 裁定;lineage 三重标注')
    ON CONFLICT (id) DO NOTHING;
END $$;

-- Province 20: gansu (甘肃省, admin_code=62, idx=19)
DO $$
DECLARE
    v_registry_id UUID := 'q0eebc99-0013-4000-8000-000000000019';
    v_doc_id UUID := 'q1eebc99-0013-4000-8000-000000000019';
    v_loc_id UUID := 'q2eebc99-0013-4000-8000-000000000019';
    v_run_id UUID := 'q7eebc99-0013-4000-8000-000000000019';
    v_geo_entity_id UUID := 'a2000000-0000-0000-0000-000000000062';
    v_geo_cv_id UUID := 'a2000000-0000-0000-0000-00000000006201';
BEGIN
    -- 1) source_registry (hongheiku_tjgb, origin=甘肃省统计局)
    INSERT INTO cegr.source_registry
        (id, domain, organization, category, primary_url,
         update_frequency, auth_note, access_method,
         historical_coverage, stability_note, failure_handling,
         enabled, source_level,
         lineage)
    VALUES
        (v_registry_id, 'tjgb.hongheiku.com',
         'hongheiku 转载 (origin: 甘肃省统计局)', 'PROVINCIAL_BULLETIN_REPRINT',
         'https://tjgb.hongheiku.com/sjtjgb/57196.html', 'ANNUAL',
         '公开转载;hongheiku 红黑统计公报库;U6 用户裁定接受',
         'HTTP_CURL', '2024 年度公报',
         'U6 金丝雀 5/5 PASS (京/沪/鲁/鄂/川 delta=0 全等)',
         'BLOCKED_NO_POOL 留痕不代换 (红线 14)',
         TRUE, 'S2_REPRINT',
         jsonb_build_object(
             'chain_id', 'real_658_m2_u6_batch_v1'::text,
             'knife', '658',
             'source', 'hongheiku_tjgb',
             'origin', '甘肃省统计局',
             'ruling', 'U6 2026-09-02',
             'cross_reference', '金丝雀 5/5 全等 (京/沪/鲁/鄂/川)',
             'reprint', TRUE,
             'extraction_method', 'category_first_url_discovery'
         ))
    ON CONFLICT (id) DO NOTHING;

    -- 2) source_document (file SHA 锁转载字节)
    INSERT INTO cegr.source_document
        (id, source_id, file_path, file_size_bytes, file_hash_sha256,
         mime_type, retrieval_method, retrieval_at, raw_content_ref)
    VALUES
        (v_doc_id, v_registry_id,
         '/tmp/_658_gansu.html',
         50440,
         'e4e1187309e5c5c491a51f33d5ef06cc5c590abcfd08bae84cad07f2cd70889f',
         'text/html', 'HTTP_CURL',
         '2026-09-02'::timestamp,
         'evidence_pack/u6_batch_26prov_fetch_20260902.json#gansu')
    ON CONFLICT (id) DO NOTHING;

    -- 3) source_location (URL + http_code 200)
    INSERT INTO cegr.source_location
        (id, source_id, location_type, url, http_code,
         accessed_at, content_hash, notes)
    VALUES
        (v_loc_id, v_registry_id, 'PRIMARY_URL',
         'https://tjgb.hongheiku.com/sjtjgb/57196.html', 200,
         '2026-09-02'::timestamp,
         'e4e1187309e5c5c491a51f33d5ef06cc5c590abcfd08bae84cad07f2cd70889f',
         'hongheiku 转载页; 2024 年度公报; 1 HTTP (cache hit post-1st)')
    ON CONFLICT (id) DO NOTHING;

    -- 4) ingestion_run (status=SUCCESS, records_inserted=5)
    INSERT INTO cegr.ingestion_run
        (id, source_id, started_at, finished_at,
         records_inserted, records_updated, records_skipped,
         status, error_message, run_kind)
    VALUES
        (v_run_id, v_registry_id,
         '2026-09-02'::timestamp, '2026-09-02'::timestamp,
         5, 0, 0,
         'SUCCESS', NULL,
         'U6_HONGHEIKU_REPRINT_BATCH')
    ON CONFLICT (id) DO NOTHING;
    -- observation GDP_ANNUAL: 13002.9 亿元
    INSERT INTO cegr.observation
        (id, indicator_id, indicator_methodology_version_id,
         geo_entity_id, geo_code_version_id, calendar_period_id,
         value, raw_value, is_imputed, missing_reason,
         unit, comparison_basis, value_type, status,
         source_id, source_location_id, ingestion_run_id,
         extracted_at, extraction_method, confidence, notes)
    VALUES
        ('q6eebc99-0013-4000-8000-000000000095',
         'a2000000-0000-0000-0000-00000000a001', 'a2000000-0000-0000-0000-00000000a002',
         v_geo_entity_id, v_geo_cv_id, 'a2000000-0000-0000-0000-000020240101',
         13002.9, '13002.9', FALSE, NULL,
         '亿元', 'YEAR_OVER_YEAR', 'REAL', 'PUBLISHED',
         v_registry_id, v_loc_id, v_run_id,
         '2026-09-02'::timestamp, 'REGEX_ANCHORED', 1.0,
         'gansu GDP_ANNUAL 13002.9 亿元;hongheiku 转载;U6 裁定;lineage 三重标注')
    ON CONFLICT (id) DO NOTHING;
    -- observation GDP_GROWTH: 5.8 %
    INSERT INTO cegr.observation
        (id, indicator_id, indicator_methodology_version_id,
         geo_entity_id, geo_code_version_id, calendar_period_id,
         value, raw_value, is_imputed, missing_reason,
         unit, comparison_basis, value_type, status,
         source_id, source_location_id, ingestion_run_id,
         extracted_at, extraction_method, confidence, notes)
    VALUES
        ('q6eebc99-0013-4000-8000-000000000096',
         'a2000000-0000-0000-0000-00000000a003', 'a2000000-0000-0000-0000-00000000a007',
         v_geo_entity_id, v_geo_cv_id, 'a2000000-0000-0000-0000-000020240101',
         5.8, '5.8', FALSE, NULL,
         '%', 'YEAR_OVER_YEAR', 'REAL', 'PUBLISHED',
         v_registry_id, v_loc_id, v_run_id,
         '2026-09-02'::timestamp, 'REGEX_ANCHORED', 1.0,
         'gansu GDP_GROWTH 5.8 %;hongheiku 转载;U6 裁定;lineage 三重标注')
    ON CONFLICT (id) DO NOTHING;
    -- observation GVA_PRIMARY: 1621.7 亿元
    INSERT INTO cegr.observation
        (id, indicator_id, indicator_methodology_version_id,
         geo_entity_id, geo_code_version_id, calendar_period_id,
         value, raw_value, is_imputed, missing_reason,
         unit, comparison_basis, value_type, status,
         source_id, source_location_id, ingestion_run_id,
         extracted_at, extraction_method, confidence, notes)
    VALUES
        ('q6eebc99-0013-4000-8000-000000000097',
         'a2000000-0000-0000-0000-00000000a004', 'a2000000-0000-0000-0000-00000000a008',
         v_geo_entity_id, v_geo_cv_id, 'a2000000-0000-0000-0000-000020240101',
         1621.7, '1621.7', FALSE, NULL,
         '亿元', 'YEAR_OVER_YEAR', 'REAL', 'PUBLISHED',
         v_registry_id, v_loc_id, v_run_id,
         '2026-09-02'::timestamp, 'REGEX_ANCHORED', 1.0,
         'gansu GVA_PRIMARY 1621.7 亿元;hongheiku 转载;U6 裁定;lineage 三重标注')
    ON CONFLICT (id) DO NOTHING;
    -- observation GVA_SECONDARY: 4436.4 亿元
    INSERT INTO cegr.observation
        (id, indicator_id, indicator_methodology_version_id,
         geo_entity_id, geo_code_version_id, calendar_period_id,
         value, raw_value, is_imputed, missing_reason,
         unit, comparison_basis, value_type, status,
         source_id, source_location_id, ingestion_run_id,
         extracted_at, extraction_method, confidence, notes)
    VALUES
        ('q6eebc99-0013-4000-8000-000000000098',
         'a2000000-0000-0000-0000-00000000a005', 'a2000000-0000-0000-0000-00000000a009',
         v_geo_entity_id, v_geo_cv_id, 'a2000000-0000-0000-0000-000020240101',
         4436.4, '4436.4', FALSE, NULL,
         '亿元', 'YEAR_OVER_YEAR', 'REAL', 'PUBLISHED',
         v_registry_id, v_loc_id, v_run_id,
         '2026-09-02'::timestamp, 'REGEX_ANCHORED', 1.0,
         'gansu GVA_SECONDARY 4436.4 亿元;hongheiku 转载;U6 裁定;lineage 三重标注')
    ON CONFLICT (id) DO NOTHING;
    -- observation GVA_TERTIARY: 6944.8 亿元
    INSERT INTO cegr.observation
        (id, indicator_id, indicator_methodology_version_id,
         geo_entity_id, geo_code_version_id, calendar_period_id,
         value, raw_value, is_imputed, missing_reason,
         unit, comparison_basis, value_type, status,
         source_id, source_location_id, ingestion_run_id,
         extracted_at, extraction_method, confidence, notes)
    VALUES
        ('q6eebc99-0013-4000-8000-000000000099',
         'a2000000-0000-0000-0000-00000000a006', 'a2000000-0000-0000-0000-00000000a010',
         v_geo_entity_id, v_geo_cv_id, 'a2000000-0000-0000-0000-000020240101',
         6944.8, '6944.8', FALSE, NULL,
         '亿元', 'YEAR_OVER_YEAR', 'REAL', 'PUBLISHED',
         v_registry_id, v_loc_id, v_run_id,
         '2026-09-02'::timestamp, 'REGEX_ANCHORED', 1.0,
         'gansu GVA_TERTIARY 6944.8 亿元;hongheiku 转载;U6 裁定;lineage 三重标注')
    ON CONFLICT (id) DO NOTHING;
END $$;

-- Province 21: qinghai (青海省, admin_code=63, idx=20)
DO $$
DECLARE
    v_registry_id UUID := 'q0eebc99-0014-4000-8000-000000000020';
    v_doc_id UUID := 'q1eebc99-0014-4000-8000-000000000020';
    v_loc_id UUID := 'q2eebc99-0014-4000-8000-000000000020';
    v_run_id UUID := 'q7eebc99-0014-4000-8000-000000000020';
    v_geo_entity_id UUID := 'a2000000-0000-0000-0000-000000000063';
    v_geo_cv_id UUID := 'a2000000-0000-0000-0000-00000000006301';
BEGIN
    -- 1) source_registry (hongheiku_tjgb, origin=青海省统计局)
    INSERT INTO cegr.source_registry
        (id, domain, organization, category, primary_url,
         update_frequency, auth_note, access_method,
         historical_coverage, stability_note, failure_handling,
         enabled, source_level,
         lineage)
    VALUES
        (v_registry_id, 'tjgb.hongheiku.com',
         'hongheiku 转载 (origin: 青海省统计局)', 'PROVINCIAL_BULLETIN_REPRINT',
         'https://tjgb.hongheiku.com/sjtjgb/57094.html', 'ANNUAL',
         '公开转载;hongheiku 红黑统计公报库;U6 用户裁定接受',
         'HTTP_CURL', '2024 年度公报',
         'U6 金丝雀 5/5 PASS (京/沪/鲁/鄂/川 delta=0 全等)',
         'BLOCKED_NO_POOL 留痕不代换 (红线 14)',
         TRUE, 'S2_REPRINT',
         jsonb_build_object(
             'chain_id', 'real_658_m2_u6_batch_v1'::text,
             'knife', '658',
             'source', 'hongheiku_tjgb',
             'origin', '青海省统计局',
             'ruling', 'U6 2026-09-02',
             'cross_reference', '金丝雀 5/5 全等 (京/沪/鲁/鄂/川)',
             'reprint', TRUE,
             'extraction_method', 'category_first_url_discovery'
         ))
    ON CONFLICT (id) DO NOTHING;

    -- 2) source_document (file SHA 锁转载字节)
    INSERT INTO cegr.source_document
        (id, source_id, file_path, file_size_bytes, file_hash_sha256,
         mime_type, retrieval_method, retrieval_at, raw_content_ref)
    VALUES
        (v_doc_id, v_registry_id,
         '/tmp/_658_qinghai.html',
         71365,
         'efa2694dc196ac2a7a4aff8c111da8b22fae58ce47e67882766a1b42050423d1',
         'text/html', 'HTTP_CURL',
         '2026-09-02'::timestamp,
         'evidence_pack/u6_batch_26prov_fetch_20260902.json#qinghai')
    ON CONFLICT (id) DO NOTHING;

    -- 3) source_location (URL + http_code 200)
    INSERT INTO cegr.source_location
        (id, source_id, location_type, url, http_code,
         accessed_at, content_hash, notes)
    VALUES
        (v_loc_id, v_registry_id, 'PRIMARY_URL',
         'https://tjgb.hongheiku.com/sjtjgb/57094.html', 200,
         '2026-09-02'::timestamp,
         'efa2694dc196ac2a7a4aff8c111da8b22fae58ce47e67882766a1b42050423d1',
         'hongheiku 转载页; 2024 年度公报; 1 HTTP (cache hit post-1st)')
    ON CONFLICT (id) DO NOTHING;

    -- 4) ingestion_run (status=SUCCESS, records_inserted=5)
    INSERT INTO cegr.ingestion_run
        (id, source_id, started_at, finished_at,
         records_inserted, records_updated, records_skipped,
         status, error_message, run_kind)
    VALUES
        (v_run_id, v_registry_id,
         '2026-09-02'::timestamp, '2026-09-02'::timestamp,
         5, 0, 0,
         'SUCCESS', NULL,
         'U6_HONGHEIKU_REPRINT_BATCH')
    ON CONFLICT (id) DO NOTHING;
    -- observation GDP_ANNUAL: 3950.79 亿元
    INSERT INTO cegr.observation
        (id, indicator_id, indicator_methodology_version_id,
         geo_entity_id, geo_code_version_id, calendar_period_id,
         value, raw_value, is_imputed, missing_reason,
         unit, comparison_basis, value_type, status,
         source_id, source_location_id, ingestion_run_id,
         extracted_at, extraction_method, confidence, notes)
    VALUES
        ('q6eebc99-0014-4000-8000-000000000100',
         'a2000000-0000-0000-0000-00000000a001', 'a2000000-0000-0000-0000-00000000a002',
         v_geo_entity_id, v_geo_cv_id, 'a2000000-0000-0000-0000-000020240101',
         3950.79, '3950.79', FALSE, NULL,
         '亿元', 'YEAR_OVER_YEAR', 'REAL', 'PUBLISHED',
         v_registry_id, v_loc_id, v_run_id,
         '2026-09-02'::timestamp, 'REGEX_ANCHORED', 1.0,
         'qinghai GDP_ANNUAL 3950.79 亿元;hongheiku 转载;U6 裁定;lineage 三重标注')
    ON CONFLICT (id) DO NOTHING;
    -- observation GDP_GROWTH: 2.7 %
    INSERT INTO cegr.observation
        (id, indicator_id, indicator_methodology_version_id,
         geo_entity_id, geo_code_version_id, calendar_period_id,
         value, raw_value, is_imputed, missing_reason,
         unit, comparison_basis, value_type, status,
         source_id, source_location_id, ingestion_run_id,
         extracted_at, extraction_method, confidence, notes)
    VALUES
        ('q6eebc99-0014-4000-8000-000000000101',
         'a2000000-0000-0000-0000-00000000a003', 'a2000000-0000-0000-0000-00000000a007',
         v_geo_entity_id, v_geo_cv_id, 'a2000000-0000-0000-0000-000020240101',
         2.7, '2.7', FALSE, NULL,
         '%', 'YEAR_OVER_YEAR', 'REAL', 'PUBLISHED',
         v_registry_id, v_loc_id, v_run_id,
         '2026-09-02'::timestamp, 'REGEX_ANCHORED', 1.0,
         'qinghai GDP_GROWTH 2.7 %;hongheiku 转载;U6 裁定;lineage 三重标注')
    ON CONFLICT (id) DO NOTHING;
    -- observation GVA_PRIMARY: 359.07 亿元
    INSERT INTO cegr.observation
        (id, indicator_id, indicator_methodology_version_id,
         geo_entity_id, geo_code_version_id, calendar_period_id,
         value, raw_value, is_imputed, missing_reason,
         unit, comparison_basis, value_type, status,
         source_id, source_location_id, ingestion_run_id,
         extracted_at, extraction_method, confidence, notes)
    VALUES
        ('q6eebc99-0014-4000-8000-000000000102',
         'a2000000-0000-0000-0000-00000000a004', 'a2000000-0000-0000-0000-00000000a008',
         v_geo_entity_id, v_geo_cv_id, 'a2000000-0000-0000-0000-000020240101',
         359.07, '359.07', FALSE, NULL,
         '亿元', 'YEAR_OVER_YEAR', 'REAL', 'PUBLISHED',
         v_registry_id, v_loc_id, v_run_id,
         '2026-09-02'::timestamp, 'REGEX_ANCHORED', 1.0,
         'qinghai GVA_PRIMARY 359.07 亿元;hongheiku 转载;U6 裁定;lineage 三重标注')
    ON CONFLICT (id) DO NOTHING;
    -- observation GVA_SECONDARY: 1662.39 亿元
    INSERT INTO cegr.observation
        (id, indicator_id, indicator_methodology_version_id,
         geo_entity_id, geo_code_version_id, calendar_period_id,
         value, raw_value, is_imputed, missing_reason,
         unit, comparison_basis, value_type, status,
         source_id, source_location_id, ingestion_run_id,
         extracted_at, extraction_method, confidence, notes)
    VALUES
        ('q6eebc99-0014-4000-8000-000000000103',
         'a2000000-0000-0000-0000-00000000a005', 'a2000000-0000-0000-0000-00000000a009',
         v_geo_entity_id, v_geo_cv_id, 'a2000000-0000-0000-0000-000020240101',
         1662.39, '1662.39', FALSE, NULL,
         '亿元', 'YEAR_OVER_YEAR', 'REAL', 'PUBLISHED',
         v_registry_id, v_loc_id, v_run_id,
         '2026-09-02'::timestamp, 'REGEX_ANCHORED', 1.0,
         'qinghai GVA_SECONDARY 1662.39 亿元;hongheiku 转载;U6 裁定;lineage 三重标注')
    ON CONFLICT (id) DO NOTHING;
    -- observation GVA_TERTIARY: 1929.33 亿元
    INSERT INTO cegr.observation
        (id, indicator_id, indicator_methodology_version_id,
         geo_entity_id, geo_code_version_id, calendar_period_id,
         value, raw_value, is_imputed, missing_reason,
         unit, comparison_basis, value_type, status,
         source_id, source_location_id, ingestion_run_id,
         extracted_at, extraction_method, confidence, notes)
    VALUES
        ('q6eebc99-0014-4000-8000-000000000104',
         'a2000000-0000-0000-0000-00000000a006', 'a2000000-0000-0000-0000-00000000a010',
         v_geo_entity_id, v_geo_cv_id, 'a2000000-0000-0000-0000-000020240101',
         1929.33, '1929.33', FALSE, NULL,
         '亿元', 'YEAR_OVER_YEAR', 'REAL', 'PUBLISHED',
         v_registry_id, v_loc_id, v_run_id,
         '2026-09-02'::timestamp, 'REGEX_ANCHORED', 1.0,
         'qinghai GVA_TERTIARY 1929.33 亿元;hongheiku 转载;U6 裁定;lineage 三重标注')
    ON CONFLICT (id) DO NOTHING;
END $$;

-- Province 22: ningxia (宁夏回族自治区, admin_code=64, idx=21)
DO $$
DECLARE
    v_registry_id UUID := 'q0eebc99-0015-4000-8000-000000000021';
    v_doc_id UUID := 'q1eebc99-0015-4000-8000-000000000021';
    v_loc_id UUID := 'q2eebc99-0015-4000-8000-000000000021';
    v_run_id UUID := 'q7eebc99-0015-4000-8000-000000000021';
    v_geo_entity_id UUID := 'a2000000-0000-0000-0000-000000000064';
    v_geo_cv_id UUID := 'a2000000-0000-0000-0000-00000000006401';
BEGIN
    -- 1) source_registry (hongheiku_tjgb, origin=宁夏回族自治区统计局)
    INSERT INTO cegr.source_registry
        (id, domain, organization, category, primary_url,
         update_frequency, auth_note, access_method,
         historical_coverage, stability_note, failure_handling,
         enabled, source_level,
         lineage)
    VALUES
        (v_registry_id, 'tjgb.hongheiku.com',
         'hongheiku 转载 (origin: 宁夏回族自治区统计局)', 'PROVINCIAL_BULLETIN_REPRINT',
         'https://tjgb.hongheiku.com/sjtjgb/60392.html', 'ANNUAL',
         '公开转载;hongheiku 红黑统计公报库;U6 用户裁定接受',
         'HTTP_CURL', '2024 年度公报',
         'U6 金丝雀 5/5 PASS (京/沪/鲁/鄂/川 delta=0 全等)',
         'BLOCKED_NO_POOL 留痕不代换 (红线 14)',
         TRUE, 'S2_REPRINT',
         jsonb_build_object(
             'chain_id', 'real_658_m2_u6_batch_v1'::text,
             'knife', '658',
             'source', 'hongheiku_tjgb',
             'origin', '宁夏回族自治区统计局',
             'ruling', 'U6 2026-09-02',
             'cross_reference', '金丝雀 5/5 全等 (京/沪/鲁/鄂/川)',
             'reprint', TRUE,
             'extraction_method', 'category_first_url_discovery'
         ))
    ON CONFLICT (id) DO NOTHING;

    -- 2) source_document (file SHA 锁转载字节)
    INSERT INTO cegr.source_document
        (id, source_id, file_path, file_size_bytes, file_hash_sha256,
         mime_type, retrieval_method, retrieval_at, raw_content_ref)
    VALUES
        (v_doc_id, v_registry_id,
         '/tmp/_658_ningxia.html',
         58273,
         'db558552db9878b9e182b4a84e613aada5fdb1afb7a359f3367b234d122101ab',
         'text/html', 'HTTP_CURL',
         '2026-09-02'::timestamp,
         'evidence_pack/u6_batch_26prov_fetch_20260902.json#ningxia')
    ON CONFLICT (id) DO NOTHING;

    -- 3) source_location (URL + http_code 200)
    INSERT INTO cegr.source_location
        (id, source_id, location_type, url, http_code,
         accessed_at, content_hash, notes)
    VALUES
        (v_loc_id, v_registry_id, 'PRIMARY_URL',
         'https://tjgb.hongheiku.com/sjtjgb/60392.html', 200,
         '2026-09-02'::timestamp,
         'db558552db9878b9e182b4a84e613aada5fdb1afb7a359f3367b234d122101ab',
         'hongheiku 转载页; 2024 年度公报; 1 HTTP (cache hit post-1st)')
    ON CONFLICT (id) DO NOTHING;

    -- 4) ingestion_run (status=SUCCESS, records_inserted=5)
    INSERT INTO cegr.ingestion_run
        (id, source_id, started_at, finished_at,
         records_inserted, records_updated, records_skipped,
         status, error_message, run_kind)
    VALUES
        (v_run_id, v_registry_id,
         '2026-09-02'::timestamp, '2026-09-02'::timestamp,
         5, 0, 0,
         'SUCCESS', NULL,
         'U6_HONGHEIKU_REPRINT_BATCH')
    ON CONFLICT (id) DO NOTHING;
    -- observation GDP_ANNUAL: 5502.76 亿元
    INSERT INTO cegr.observation
        (id, indicator_id, indicator_methodology_version_id,
         geo_entity_id, geo_code_version_id, calendar_period_id,
         value, raw_value, is_imputed, missing_reason,
         unit, comparison_basis, value_type, status,
         source_id, source_location_id, ingestion_run_id,
         extracted_at, extraction_method, confidence, notes)
    VALUES
        ('q6eebc99-0015-4000-8000-000000000105',
         'a2000000-0000-0000-0000-00000000a001', 'a2000000-0000-0000-0000-00000000a002',
         v_geo_entity_id, v_geo_cv_id, 'a2000000-0000-0000-0000-000020240101',
         5502.76, '5502.76', FALSE, NULL,
         '亿元', 'YEAR_OVER_YEAR', 'REAL', 'PUBLISHED',
         v_registry_id, v_loc_id, v_run_id,
         '2026-09-02'::timestamp, 'REGEX_ANCHORED', 1.0,
         'ningxia GDP_ANNUAL 5502.76 亿元;hongheiku 转载;U6 裁定;lineage 三重标注')
    ON CONFLICT (id) DO NOTHING;
    -- observation GDP_GROWTH: 5.4 %
    INSERT INTO cegr.observation
        (id, indicator_id, indicator_methodology_version_id,
         geo_entity_id, geo_code_version_id, calendar_period_id,
         value, raw_value, is_imputed, missing_reason,
         unit, comparison_basis, value_type, status,
         source_id, source_location_id, ingestion_run_id,
         extracted_at, extraction_method, confidence, notes)
    VALUES
        ('q6eebc99-0015-4000-8000-000000000106',
         'a2000000-0000-0000-0000-00000000a003', 'a2000000-0000-0000-0000-00000000a007',
         v_geo_entity_id, v_geo_cv_id, 'a2000000-0000-0000-0000-000020240101',
         5.4, '5.4', FALSE, NULL,
         '%', 'YEAR_OVER_YEAR', 'REAL', 'PUBLISHED',
         v_registry_id, v_loc_id, v_run_id,
         '2026-09-02'::timestamp, 'REGEX_ANCHORED', 1.0,
         'ningxia GDP_GROWTH 5.4 %;hongheiku 转载;U6 裁定;lineage 三重标注')
    ON CONFLICT (id) DO NOTHING;
    -- observation GVA_PRIMARY: 451.24 亿元
    INSERT INTO cegr.observation
        (id, indicator_id, indicator_methodology_version_id,
         geo_entity_id, geo_code_version_id, calendar_period_id,
         value, raw_value, is_imputed, missing_reason,
         unit, comparison_basis, value_type, status,
         source_id, source_location_id, ingestion_run_id,
         extracted_at, extraction_method, confidence, notes)
    VALUES
        ('q6eebc99-0015-4000-8000-000000000107',
         'a2000000-0000-0000-0000-00000000a004', 'a2000000-0000-0000-0000-00000000a008',
         v_geo_entity_id, v_geo_cv_id, 'a2000000-0000-0000-0000-000020240101',
         451.24, '451.24', FALSE, NULL,
         '亿元', 'YEAR_OVER_YEAR', 'REAL', 'PUBLISHED',
         v_registry_id, v_loc_id, v_run_id,
         '2026-09-02'::timestamp, 'REGEX_ANCHORED', 1.0,
         'ningxia GVA_PRIMARY 451.24 亿元;hongheiku 转载;U6 裁定;lineage 三重标注')
    ON CONFLICT (id) DO NOTHING;
    -- observation GVA_SECONDARY: 2335.36 亿元
    INSERT INTO cegr.observation
        (id, indicator_id, indicator_methodology_version_id,
         geo_entity_id, geo_code_version_id, calendar_period_id,
         value, raw_value, is_imputed, missing_reason,
         unit, comparison_basis, value_type, status,
         source_id, source_location_id, ingestion_run_id,
         extracted_at, extraction_method, confidence, notes)
    VALUES
        ('q6eebc99-0015-4000-8000-000000000108',
         'a2000000-0000-0000-0000-00000000a005', 'a2000000-0000-0000-0000-00000000a009',
         v_geo_entity_id, v_geo_cv_id, 'a2000000-0000-0000-0000-000020240101',
         2335.36, '2335.36', FALSE, NULL,
         '亿元', 'YEAR_OVER_YEAR', 'REAL', 'PUBLISHED',
         v_registry_id, v_loc_id, v_run_id,
         '2026-09-02'::timestamp, 'REGEX_ANCHORED', 1.0,
         'ningxia GVA_SECONDARY 2335.36 亿元;hongheiku 转载;U6 裁定;lineage 三重标注')
    ON CONFLICT (id) DO NOTHING;
    -- observation GVA_TERTIARY: 2716.16 亿元
    INSERT INTO cegr.observation
        (id, indicator_id, indicator_methodology_version_id,
         geo_entity_id, geo_code_version_id, calendar_period_id,
         value, raw_value, is_imputed, missing_reason,
         unit, comparison_basis, value_type, status,
         source_id, source_location_id, ingestion_run_id,
         extracted_at, extraction_method, confidence, notes)
    VALUES
        ('q6eebc99-0015-4000-8000-000000000109',
         'a2000000-0000-0000-0000-00000000a006', 'a2000000-0000-0000-0000-00000000a010',
         v_geo_entity_id, v_geo_cv_id, 'a2000000-0000-0000-0000-000020240101',
         2716.16, '2716.16', FALSE, NULL,
         '亿元', 'YEAR_OVER_YEAR', 'REAL', 'PUBLISHED',
         v_registry_id, v_loc_id, v_run_id,
         '2026-09-02'::timestamp, 'REGEX_ANCHORED', 1.0,
         'ningxia GVA_TERTIARY 2716.16 亿元;hongheiku 转载;U6 裁定;lineage 三重标注')
    ON CONFLICT (id) DO NOTHING;
END $$;

-- Province 23: xinjiang (新疆维吾尔自治区, admin_code=65, idx=22)
DO $$
DECLARE
    v_registry_id UUID := 'q0eebc99-0016-4000-8000-000000000022';
    v_doc_id UUID := 'q1eebc99-0016-4000-8000-000000000022';
    v_loc_id UUID := 'q2eebc99-0016-4000-8000-000000000022';
    v_run_id UUID := 'q7eebc99-0016-4000-8000-000000000022';
    v_geo_entity_id UUID := 'a2000000-0000-0000-0000-000000000065';
    v_geo_cv_id UUID := 'a2000000-0000-0000-0000-00000000006501';
BEGIN
    -- 1) source_registry (hongheiku_tjgb, origin=新疆维吾尔自治区统计局)
    INSERT INTO cegr.source_registry
        (id, domain, organization, category, primary_url,
         update_frequency, auth_note, access_method,
         historical_coverage, stability_note, failure_handling,
         enabled, source_level,
         lineage)
    VALUES
        (v_registry_id, 'tjgb.hongheiku.com',
         'hongheiku 转载 (origin: 新疆维吾尔自治区统计局)', 'PROVINCIAL_BULLETIN_REPRINT',
         'https://tjgb.hongheiku.com/sjtjgb/57625.html', 'ANNUAL',
         '公开转载;hongheiku 红黑统计公报库;U6 用户裁定接受',
         'HTTP_CURL', '2024 年度公报',
         'U6 金丝雀 5/5 PASS (京/沪/鲁/鄂/川 delta=0 全等)',
         'BLOCKED_NO_POOL 留痕不代换 (红线 14)',
         TRUE, 'S2_REPRINT',
         jsonb_build_object(
             'chain_id', 'real_658_m2_u6_batch_v1'::text,
             'knife', '658',
             'source', 'hongheiku_tjgb',
             'origin', '新疆维吾尔自治区统计局',
             'ruling', 'U6 2026-09-02',
             'cross_reference', '金丝雀 5/5 全等 (京/沪/鲁/鄂/川)',
             'reprint', TRUE,
             'extraction_method', 'category_first_url_discovery'
         ))
    ON CONFLICT (id) DO NOTHING;

    -- 2) source_document (file SHA 锁转载字节)
    INSERT INTO cegr.source_document
        (id, source_id, file_path, file_size_bytes, file_hash_sha256,
         mime_type, retrieval_method, retrieval_at, raw_content_ref)
    VALUES
        (v_doc_id, v_registry_id,
         '/tmp/_658_xinjiang.html',
         65886,
         '0d5cbbcbae4fea8faed60af84c327a7f79b60bb5fd0b125d37063f50c498657c',
         'text/html', 'HTTP_CURL',
         '2026-09-02'::timestamp,
         'evidence_pack/u6_batch_26prov_fetch_20260902.json#xinjiang')
    ON CONFLICT (id) DO NOTHING;

    -- 3) source_location (URL + http_code 200)
    INSERT INTO cegr.source_location
        (id, source_id, location_type, url, http_code,
         accessed_at, content_hash, notes)
    VALUES
        (v_loc_id, v_registry_id, 'PRIMARY_URL',
         'https://tjgb.hongheiku.com/sjtjgb/57625.html', 200,
         '2026-09-02'::timestamp,
         '0d5cbbcbae4fea8faed60af84c327a7f79b60bb5fd0b125d37063f50c498657c',
         'hongheiku 转载页; 2024 年度公报; 1 HTTP (cache hit post-1st)')
    ON CONFLICT (id) DO NOTHING;

    -- 4) ingestion_run (status=SUCCESS, records_inserted=5)
    INSERT INTO cegr.ingestion_run
        (id, source_id, started_at, finished_at,
         records_inserted, records_updated, records_skipped,
         status, error_message, run_kind)
    VALUES
        (v_run_id, v_registry_id,
         '2026-09-02'::timestamp, '2026-09-02'::timestamp,
         5, 0, 0,
         'SUCCESS', NULL,
         'U6_HONGHEIKU_REPRINT_BATCH')
    ON CONFLICT (id) DO NOTHING;
    -- observation GDP_ANNUAL: 20534.08 亿元
    INSERT INTO cegr.observation
        (id, indicator_id, indicator_methodology_version_id,
         geo_entity_id, geo_code_version_id, calendar_period_id,
         value, raw_value, is_imputed, missing_reason,
         unit, comparison_basis, value_type, status,
         source_id, source_location_id, ingestion_run_id,
         extracted_at, extraction_method, confidence, notes)
    VALUES
        ('q6eebc99-0016-4000-8000-000000000110',
         'a2000000-0000-0000-0000-00000000a001', 'a2000000-0000-0000-0000-00000000a002',
         v_geo_entity_id, v_geo_cv_id, 'a2000000-0000-0000-0000-000020240101',
         20534.08, '20534.08', FALSE, NULL,
         '亿元', 'YEAR_OVER_YEAR', 'REAL', 'PUBLISHED',
         v_registry_id, v_loc_id, v_run_id,
         '2026-09-02'::timestamp, 'REGEX_ANCHORED', 1.0,
         'xinjiang GDP_ANNUAL 20534.08 亿元;hongheiku 转载;U6 裁定;lineage 三重标注')
    ON CONFLICT (id) DO NOTHING;
    -- observation GDP_GROWTH: 6.1 %
    INSERT INTO cegr.observation
        (id, indicator_id, indicator_methodology_version_id,
         geo_entity_id, geo_code_version_id, calendar_period_id,
         value, raw_value, is_imputed, missing_reason,
         unit, comparison_basis, value_type, status,
         source_id, source_location_id, ingestion_run_id,
         extracted_at, extraction_method, confidence, notes)
    VALUES
        ('q6eebc99-0016-4000-8000-000000000111',
         'a2000000-0000-0000-0000-00000000a003', 'a2000000-0000-0000-0000-00000000a007',
         v_geo_entity_id, v_geo_cv_id, 'a2000000-0000-0000-0000-000020240101',
         6.1, '6.1', FALSE, NULL,
         '%', 'YEAR_OVER_YEAR', 'REAL', 'PUBLISHED',
         v_registry_id, v_loc_id, v_run_id,
         '2026-09-02'::timestamp, 'REGEX_ANCHORED', 1.0,
         'xinjiang GDP_GROWTH 6.1 %;hongheiku 转载;U6 裁定;lineage 三重标注')
    ON CONFLICT (id) DO NOTHING;
    -- observation GVA_PRIMARY: 2571.98 亿元
    INSERT INTO cegr.observation
        (id, indicator_id, indicator_methodology_version_id,
         geo_entity_id, geo_code_version_id, calendar_period_id,
         value, raw_value, is_imputed, missing_reason,
         unit, comparison_basis, value_type, status,
         source_id, source_location_id, ingestion_run_id,
         extracted_at, extraction_method, confidence, notes)
    VALUES
        ('q6eebc99-0016-4000-8000-000000000112',
         'a2000000-0000-0000-0000-00000000a004', 'a2000000-0000-0000-0000-00000000a008',
         v_geo_entity_id, v_geo_cv_id, 'a2000000-0000-0000-0000-000020240101',
         2571.98, '2571.98', FALSE, NULL,
         '亿元', 'YEAR_OVER_YEAR', 'REAL', 'PUBLISHED',
         v_registry_id, v_loc_id, v_run_id,
         '2026-09-02'::timestamp, 'REGEX_ANCHORED', 1.0,
         'xinjiang GVA_PRIMARY 2571.98 亿元;hongheiku 转载;U6 裁定;lineage 三重标注')
    ON CONFLICT (id) DO NOTHING;
    -- observation GVA_SECONDARY: 8135.87 亿元
    INSERT INTO cegr.observation
        (id, indicator_id, indicator_methodology_version_id,
         geo_entity_id, geo_code_version_id, calendar_period_id,
         value, raw_value, is_imputed, missing_reason,
         unit, comparison_basis, value_type, status,
         source_id, source_location_id, ingestion_run_id,
         extracted_at, extraction_method, confidence, notes)
    VALUES
        ('q6eebc99-0016-4000-8000-000000000113',
         'a2000000-0000-0000-0000-00000000a005', 'a2000000-0000-0000-0000-00000000a009',
         v_geo_entity_id, v_geo_cv_id, 'a2000000-0000-0000-0000-000020240101',
         8135.87, '8135.87', FALSE, NULL,
         '亿元', 'YEAR_OVER_YEAR', 'REAL', 'PUBLISHED',
         v_registry_id, v_loc_id, v_run_id,
         '2026-09-02'::timestamp, 'REGEX_ANCHORED', 1.0,
         'xinjiang GVA_SECONDARY 8135.87 亿元;hongheiku 转载;U6 裁定;lineage 三重标注')
    ON CONFLICT (id) DO NOTHING;
    -- observation GVA_TERTIARY: 9826.23 亿元
    INSERT INTO cegr.observation
        (id, indicator_id, indicator_methodology_version_id,
         geo_entity_id, geo_code_version_id, calendar_period_id,
         value, raw_value, is_imputed, missing_reason,
         unit, comparison_basis, value_type, status,
         source_id, source_location_id, ingestion_run_id,
         extracted_at, extraction_method, confidence, notes)
    VALUES
        ('q6eebc99-0016-4000-8000-000000000114',
         'a2000000-0000-0000-0000-00000000a006', 'a2000000-0000-0000-0000-00000000a010',
         v_geo_entity_id, v_geo_cv_id, 'a2000000-0000-0000-0000-000020240101',
         9826.23, '9826.23', FALSE, NULL,
         '亿元', 'YEAR_OVER_YEAR', 'REAL', 'PUBLISHED',
         v_registry_id, v_loc_id, v_run_id,
         '2026-09-02'::timestamp, 'REGEX_ANCHORED', 1.0,
         'xinjiang GVA_TERTIARY 9826.23 亿元;hongheiku 转载;U6 裁定;lineage 三重标注')
    ON CONFLICT (id) DO NOTHING;
END $$;


-- ----------------------------------------------------------------------------
-- 3 BLOCKED 省 (liaoning/hainan/guizhou) 留痕不代换
-- 红线 14: 缺省禁部分采信 → 整省 BLOCKED (单行留痕, 不入库 observation)
-- ----------------------------------------------------------------------------
DO $$
DECLARE
    v_blocked_note TEXT;
BEGIN
    -- 留痕写 project_event (kafka-style)
    v_blocked_note := '658 BLOCKED: liaoning/hainan/guizhou 未在 2024 公报索引页 /category/sjtjgb 出现 (NOT_FOUND_IN_2024_INDEX)';
    INSERT INTO cegr.project_event
        (id, chain_id, knife, event_type, severity, message,
             actor, occurred_at, related_artifact, metadata)
    VALUES
        (gen_random_uuid(), 'real_658_m2_u6_batch_v1', 658,
             'BLOCKED_NO_POOL', 'WARNING',
             v_blocked_note, 'arch-exec-merged',
             '2026-09-02'::timestamp,
             'evidence_pack/u6_batch_26prov_fetch_20260902.json',
             jsonb_build_object(
                 'blocked', '["liaoning","hainan","guizhou"]'::jsonb,
                 'ruling', 'U6 2026-09-02',
                 'note', '整省 BLOCKED, 不入库 observation (红线 14)'
             ))
    ON CONFLICT DO NOTHING;
END $$;

COMMIT;

RESET search_path;
