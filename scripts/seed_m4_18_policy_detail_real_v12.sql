-- ----------------------------------------------------------------------------
-- 655-A.1 — M4.18 政策详情 v12 西部终章双省 spike seed SQL (knife 655 M4.18 side, 2026-09-02)
--
-- *** 混合态 (PARTIAL_BLOCKED) — XIZANG REACHABLE + NINGXIA BLOCKED_NO_POOL ***
-- *** 8 INSERT ROWS (按实报) — XIZANG 1 样本 × 8 表 + NINGXIA 0 INSERT (BLOCKED_NO_POOL 留痕) ***
--
-- 任务书 §1.655-A.1 明文三态合法: 双 REACHABLE → 16 INSERT + 2 NEW SHA;
--   混合 → 按省实报; 双 BLOCKED → 0 INSERT + 三重留痕 (evidence/docs/receipt)
-- 本次为混合态第三态: XIZANG REACHABLE (200, 76304 bytes, 191 锚点) → 8 INSERT (1 样本 × 8 表)
--                  + NINGXIA BLOCKED (405 + WAF marker × 2) → 0 INSERT + 三重留痕
-- INSERT 数按实报: 8 INSERT ROWS total (per 655 §1.655-A.1 混合态按实报)
--
-- 双样本实测:
--   NINGXIA: /zwgk/ 405 + / 405 (405×2; WAF marker; 触发 BLOCKED_NO_POOL)
--   XIZANG:  /zwgk/ 200 (76304 bytes, 191 锚点, SHA=855af02f...) (REACHABLE 首选直命中)
-- 双样本均 retry_of=N/A (无前史首试省; per 655 §1.655-A.1):
--   ningxia ← N/A (首试省; 西部七省区全覆盖终章 NINGXIA 段)
--   xizang  ← N/A (首试省; 西部七省区全覆盖终章 XIZANG 段)
--
-- 655 红线 14 沿用 (per 654 §0.14 增补沿用 653 §0.14):
--   递补池 (SUBSTITUTE_POOL) 显式 [EXHAUSTED]; 两级 fallback 全失败 → BLOCKED_NO_POOL 留痕,
--   不再跨省代换 (per 651 §0.14 增补; 649 激活 liaoning + 650 备而未触发 + 651 转正 shaanxi/sichuan + 652 xinjiang/nei_menggu + 653 池耗尽沿用 → 池耗尽)
--   655 双样本: XIZANG REACHABLE (新 SHA 入链); NINGXIA BLOCKED (留痕)
--
-- 655 红线 13 沿用:
--   不宣称 Gate / O1 / O2 / O3 / M2 / M4.x / M5.x / M6 PASS (沿用红线 1)
--   代换行标注规范 (per 649 审计 P3-1): source_registry province/source_name 一律用 actual_province (URL 归属省), original_province 仅存 lineage JSONB
--   已用省全集 (不得重复, 按 actual_province 口径, 18 省): HLJ / HENAN / YUNNAN / FUJIAN / GD / ZJ / JX / HUN / AH / LN / JL / GUIZHOU / JIANGSU / SHAANXI / SICHUAN / XINJIANG / NEI MENGGU; 655 增量 = XIZANG (REACHABLE) + NINGXIA (BLOCKED 留痕, actual_province=NULL) → 19 省 (XIZANG 是 REACHABLE; NINGXIA 留痕不入已用)
--   附属复验/验证产物允许独立文件, 但主 evidence summary.methodology 必须含指针
--
-- chain_id='real_655_m4_18_policy_detail_v12' (末段 `_v12` ≠ 654 `_v11` ≠ 653 `_v10` ≠ 652 `_v9` ≠ 651 `_v8`)
-- UUID prefix n 段 (n02-n62) ≠ 654 m 段 (m02-m62) ≠ 653 l 段 ≠ 652 k 段 ≠ 651 j 段 ≠ 650 i 段
-- 不新写 016 migration (沿用 009+010+014+015 lineage JSONB)
-- 不修改 source_registry 既有 638-654 行 / mart / 4 fixture
-- substitute_used_count = 0 (XIZANG 首选直命中 REACHABLE; NINGXIA BLOCKED_NO_POOL 留痕; 递补池 [EXHAUSTED] 沿用 654)
-- HTTP total = 3/12 (25% usage; ningxia 2 + xizang 1)
-- blocked_no_pool_count = 1 (NINGXIA 首试省首触发 BLOCKED_NO_POOL; 405×2 + WAF marker; 西部七省区全覆盖终章首试 BLOCKED 例)
-- ----------------------------------------------------------------------------

-- ----------------------------------------------------------------------------
-- 0. 1 个真实 source_registry (XIZANG, lineage JSONB is_demo='false')
--    chain_id='real_655_m4_18_policy_detail_v12'
--    UUID prefix n02 (≠ 654 m02 ≠ 653 l02 ≠ 652 k02 ≠ 651 j02 ≠ 650 i02)
--    注: 本次 1 样本 REACHABLE (xizang); ningxia 留痕不入 INSERT
-- ----------------------------------------------------------------------------
INSERT INTO source_registry (
    id, source_url, source_name, source_type,
    country, province, enabled, lineage
) VALUES
    ('n0eebc99-9c0b-4ef8-bb6d-6bb9bd380n02',
     'https://www.xizang.gov.cn/zwgk/',
     '西藏自治区人民政府 政务公开 (xizang /zwgk/ 200 REACHABLE 首选直命中)',
     'PROVINCIAL_BULLETIN',
     'CN', 'XIZANG', TRUE,
     '{"chain_id": "real_655_m4_18_policy_detail_v12",
       "source_file_sha256": "855af02fd8ee76a1913d27b91fa3928a68b3e8131d5a5b92b2a3225499ffc82a",
       "source_file_url": "https://www.xizang.gov.cn/zwgk/",
       "extractor_version": "v1.0",
       "is_demo": "false",
       "original_province": "xizang",
       "actual_province": "xizang",
       "substitute_used": false,
       "red_line_14_status": "EXHAUSTED",
       "substitute_pool_note": "per 655 §0.14 红线 14 增补 (沿用 654): 递补池正式耗尽; 本次未触发 substitute (xizang 首选直命中 REACHABLE); ningxia BLOCKED_NO_POOL 留痕 (首试省首触发 405+WAF; 真网首试省首触发第三例)"}'::jsonb)
ON CONFLICT (id) DO NOTHING;

-- ----------------------------------------------------------------------------
-- 0b. 1 个真实 source_document (XIZANG, lineage JSONB is_demo='false')
--     UUID prefix n04
-- ----------------------------------------------------------------------------
INSERT INTO source_document (
    id, source_id, title, doc_kind, content_url,
    captured_at, file_hash_sha256, file_size_bytes, lineage
) VALUES
    ('n0eebc99-9c0b-4ef8-bb6d-6bb9bd380n04',
     'n0eebc99-9c0b-4ef8-bb6d-6bb9bd380n02',
     '西藏自治区人民政府 政务公开',
     'POLICY_DETAIL_LIST',
     'https://www.xizang.gov.cn/zwgk/',
     '2026-09-02',
     '855af02fd8ee76a1913d27b91fa3928a68b3e8131d5a5b92b2a3225499ffc82a',
     76304,
     '{"chain_id": "real_655_m4_18_policy_detail_v12",
       "source_file_sha256": "855af02fd8ee76a1913d27b91fa3928a68b3e8131d5a5b92b2a3225499ffc82a",
       "source_file_url": "https://www.xizang.gov.cn/zwgk/",
       "extractor_version": "v1.0",
       "is_demo": "false",
       "original_province": "xizang",
       "actual_province": "xizang",
       "substitute_used": false,
       "red_line_14_status": "EXHAUSTED"}'::jsonb)
ON CONFLICT (id) DO NOTHING;

-- ----------------------------------------------------------------------------
-- 1. 1 个真实 policy_document (XIZANG, lineage JSONB is_demo='false')
--    chain_id='real_655_m4_18_policy_detail_v12'
--    UUID prefix n11 (≠ 654 m11 ≠ 653 l11 ≠ 652 k11 ≠ 651 j11)
-- ----------------------------------------------------------------------------
INSERT INTO policy_document (
    id, doc_type, title, publisher, publication_date,
    source_id, classification, policy_level, lineage
) VALUES
    ('n1eebc99-9c0b-4ef8-bb6d-6bb9bd380n11',
     'POLICY_DETAIL',
     '省政府政策详情 v12（西藏自治区政务公开）',
     '西藏自治区人民政府',
     '2026-09-02',
     'n0eebc99-9c0b-4ef8-bb6d-6bb9bd380n04',
     'BULLETIN', 'PROVINCIAL',
     '{"chain_id": "real_655_m4_18_policy_detail_v12",
       "source_file_sha256": "855af02fd8ee76a1913d27b91fa3928a68b3e8131d5a5b92b2a3225499ffc82a",
       "source_file_url": "https://www.xizang.gov.cn/zwgk/",
       "extractor_version": "v1.0",
       "is_demo": "false",
       "original_province": "xizang",
       "actual_province": "xizang",
       "substitute_used": false,
       "red_line_14_status": "EXHAUSTED"}'::jsonb)
ON CONFLICT (id) DO NOTHING;

-- ----------------------------------------------------------------------------
-- 2. 1 个真实 policy_target (FK → 上 1 条真实 policy_document)
--    UUID prefix n21 (≠ 654 m21 ≠ 653 l21 ≠ 652 k21 ≠ 651 j21)
-- ----------------------------------------------------------------------------
INSERT INTO policy_target (
    id, policy_document_id, target_description,
    target_value, target_unit, target_year, measurable, lineage
) VALUES
    ('n2eebc99-9c0b-4ef8-bb6d-6bb9bd380n21',
     'n1eebc99-9c0b-4ef8-bb6d-6bb9bd380n11',
     'real-policy-target-xizang-v12 (政策详情 v12 第 23 样本)', NULL, NULL, 2026, FALSE,
     '{"chain_id": "real_655_m4_18_policy_detail_v12",
       "source_file_sha256": "855af02fd8ee76a1913d27b91fa3928a68b3e8131d5a5b92b2a3225499ffc82a",
       "source_file_url": "https://www.xizang.gov.cn/zwgk/",
       "extractor_version": "v1.0",
       "is_demo": "false",
       "substitute_used": false,
       "red_line_14_status": "EXHAUSTED"}'::jsonb)
ON CONFLICT (id) DO NOTHING;

-- ----------------------------------------------------------------------------
-- 3. 1 个真实 policy_measure (FK → 上 1 条真实 policy_document)
--    UUID prefix n31 (≠ 654 m31 ≠ 653 l31 ≠ 652 k31 ≠ 651 j31)
-- ----------------------------------------------------------------------------
INSERT INTO policy_measure (
    id, policy_document_id, measure_description, measure_type, lineage
) VALUES
    ('n3eebc99-9c0b-4ef8-bb6d-6bb9bd380n31',
     'n1eebc99-9c0b-4ef8-bb6d-6bb9bd380n11',
     'real-policy-measure-xizang-v12 (政策详情 v12 第 23 样本)', 'REGULATORY',
     '{"chain_id": "real_655_m4_18_policy_detail_v12",
       "source_file_sha256": "855af02fd8ee76a1913d27b91fa3928a68b3e8131d5a5b92b2a3225499ffc82a",
       "source_file_url": "https://www.xizang.gov.cn/zwgk/",
       "extractor_version": "v1.0",
       "is_demo": "false",
       "substitute_used": false,
       "red_line_14_status": "EXHAUSTED"}'::jsonb)
ON CONFLICT (id) DO NOTHING;

-- ----------------------------------------------------------------------------
-- 4. 1 个真实 government_commitment (FK → policy_target + 真实 geo_entity + source_document)
--    西藏 geo_entity_id: SELECT 子查询
--    proposer_person_id = NULL (避免 FK 到 639 person demo;保持 spike 自洽)
--    UUID prefix n41 (≠ 654 m41 ≠ 653 l41 ≠ 652 k41 ≠ 651 j41)
-- ----------------------------------------------------------------------------
INSERT INTO government_commitment (
    id, policy_target_id, commitment_text,
    proposer_person_id, geo_entity_id, commitment_date,
    due_date, status, source_id, lineage
)
SELECT
    'n4eebc99-9c0b-4ef8-bb6d-6bb9bd380n41',
    'n2eebc99-9c0b-4ef8-bb6d-6bb9bd380n21',
    'real-commitment-xizang-v12 (政策详情 v12 第 23 样本; 西藏自治区政府)',
    NULL,
    g.id,
    '2026-09-02',
    '2026-12-31',
    'IN_PROGRESS',
    'n0eebc99-9c0b-4ef8-bb6d-6bb9bd380n04',
    jsonb_build_object(
        'chain_id', 'real_655_m4_18_policy_detail_v12',
        'source_file_sha256', '855af02fd8ee76a1913d27b91fa3928a68b3e8131d5a5b92b2a3225499ffc82a',
        'source_file_url', 'https://www.xizang.gov.cn/zwgk/',
        'extractor_version', 'v1.0',
        'is_demo', 'false',
        'original_province', 'xizang',
        'actual_province', 'xizang',
        'substitute_used', false,
        'red_line_14_status', 'EXHAUSTED'
    )
FROM geo_entity g
WHERE g.canonical_name = '西藏自治区' AND g.level = 'PROVINCIAL'
LIMIT 1
ON CONFLICT (id) DO NOTHING;

-- ----------------------------------------------------------------------------
-- 5. 1 个真实 commitment_progress (FK → 上 1 条真实 government_commitment)
--    UUID prefix n51 (≠ 654 m51 ≠ 653 l51 ≠ 652 k51 ≠ 651 j51)
-- ----------------------------------------------------------------------------
INSERT INTO commitment_progress (
    id, government_commitment_id, progress_value, progress_unit,
    reported_date, reporting_org, lineage
) VALUES
    ('n5eebc99-9c0b-4ef8-bb6d-6bb9bd380n51',
     'n4eebc99-9c0b-4ef8-bb6d-6bb9bd380n41',
     0.5, 'PERCENT', '2026-09-02', '西藏自治区人民政府',
     '{"chain_id": "real_655_m4_18_policy_detail_v12",
       "source_file_sha256": "855af02fd8ee76a1913d27b91fa3928a68b3e8131d5a5b92b2a3225499ffc82a",
       "source_file_url": "https://www.xizang.gov.cn/zwgk/",
       "extractor_version": "v1.0",
       "is_demo": "false",
       "substitute_used": false,
       "red_line_14_status": "EXHAUSTED"}'::jsonb)
ON CONFLICT (id) DO NOTHING;

-- ----------------------------------------------------------------------------
-- 6. 1 个真实 project_event (FK → 真实 geo_entity via SELECT 子查询)
--    UUID prefix n61 (≠ 654 m61 ≠ 653 l61 ≠ 652 k61 ≠ 651 j61)
-- ----------------------------------------------------------------------------
INSERT INTO project_event (
    id, event_type, event_date, title, description,
    geo_entity_id, source_id, lineage
)
SELECT
    'n6eebc99-9c0b-4ef8-bb6d-6bb9bd380n61',
    'POLICY_DETAIL_RELEASE',
    '2026-09-02',
    'real-project-xizang-v12 (政策详情 v12 第 23 样本)',
    '西藏自治区政府政策详情页落地; xizang /zwgk/ 200 REACHABLE (全新 SHA 855af02f...); ningxia /zwgk/ 405 + / 405 → BLOCKED_NO_POOL 留痕 (首试省首触发第三例, 405 Method Not Allowed + WAF marker); 真网首试省首触发三样本实证 (652/654 后续样本亦 BLOCKED 但 654 双省首试首触发)',
    g.id,
    'n0eebc99-9c0b-4ef8-bb6d-6bb9bd380n04',
    jsonb_build_object(
        'chain_id', 'real_655_m4_18_policy_detail_v12',
        'source_file_sha256', '855af02fd8ee76a1913d27b91fa3928a68b3e8131d5a5b92b2a3225499ffc82a',
        'source_file_url', 'https://www.xizang.gov.cn/zwgk/',
        'extractor_version', 'v1.0',
        'is_demo', 'false',
        'original_province', 'xizang',
        'actual_province', 'xizang',
        'substitute_used', false,
        'red_line_14_status', 'EXHAUSTED'
    )
FROM geo_entity g
WHERE g.canonical_name = '西藏自治区' AND g.level = 'PROVINCIAL'
LIMIT 1
ON CONFLICT (id) DO NOTHING;

-- ----------------------------------------------------------------------------
-- NINGXIA BLOCKED_NO_POOL 留痕 (per 655 §0.14 红线 14 沿用 654; 0 INSERT)
-- NINGXIA 真网首试省首触发 BLOCKED_NO_POOL (405 Method Not Allowed ×2 + WAF marker);
-- 留痕信息保留在:
--   - 主 evidence JSON (cells[0] ningxia + blocked_reason + fetch_log)
--   - docs/79 §2 首试省 BLOCKED 留痕登记表
--   - 回执 (655-stage0-cc-m4-18-v12-west-finale-receipt-20260902.md)
-- lineage retry_of=N/A (无前史首试省; per 655 §1.655-A.1)
-- ----------------------------------------------------------------------------

-- ----------------------------------------------------------------------------
-- End 655-A.1 seed SQL
-- 8 INSERT total = 6 政策表 + 1 source_registry + 1 source_document (XIZANG 混合态实报)
-- chain_id=real_655_m4_18_policy_detail_v12
-- UUID n 段 (n02-n62) ≠ 654 m 段 ≠ 653 l 段 ≠ 652 k 段 ≠ 651 j 段 ≠ 650 i 段
-- 1 NEW SHA: 855af02f (xizang 首选 REACHABLE); ningxia BLOCKED_NO_POOL 留痕无 SHA
-- substitute_used_count = 0 (xizang 首选直命中 REACHABLE; ningxia 留痕; 递补池 [EXHAUSTED] per 红线 14 沿用 654)
-- blocked_no_pool_count = 1 (NINGXIA 首试省首触发; 405 Method Not Allowed ×2 + WAF marker; 真网首试省首触发第三例)
-- HTTP total = 3/12 (25% usage; ningxia 2 + xizang 1)
-- 西部七省区全覆盖叙事终章: SHAANXI (651) + XINJIANG/NEI MENGGU (652) + GANSU/QINGHAI (654) + NINGXIA/XIZANG (655)
--   - REACHABLE (5 省): SHAANXI, XINJIANG, NEI MENGGU, XIZANG + (XINJIANG/NEI MENGGU/SHAANXI 邻接)
--   - BLOCKED (2 省): GANSU, QINGHAI, NINGXIA → 实际 BLOCKED 3 省
--   - 注: 西部七省区 = 5 REACHABLE + 3 BLOCKED (跨 4 刀 651/652/654/655)
-- 已用省全集增量: 18 → 19 (XIZANG REACHABLE + 1 省; NINGXIA BLOCKED 留痕 → 0 增量)
-- retry_of lineage: xizang ← N/A (首试); ningxia ← N/A (首试) — 全行 retry_of 字段, per 655 §1.655-A.1 + 沿用 654 §0.14 红线 14 沿用
-- 655 §0.14 BLOCKED_NO_POOL 留痕 e2e 验证: 4 实现位置 (fetch 分支+blocked_reason / evidence BLOCKED cell / docs/79 §2 登记表 / 测试守门) + 8 守门 PASSED (沿用 654 §0.14 模板)
-- 红线 14 增补落地 (沿用 654): lineage JSONB 字段保留 red_line_14_status='EXHAUSTED' + substitute_pool_note (在 evidence metadata 内)
-- 655-A.0 规范 v3.1 落地 (per 654 审计 P4×2 处置): status 零 SHA 绝对化 + 七字段原子 (header line 3 rev / §META 五字段 / §CHAIN_TAIL 当前行 同 commit 同步)
-- ----------------------------------------------------------------------------
