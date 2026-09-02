-- ----------------------------------------------------------------------------
-- 656-A.1 — M4.19 政策详情 v13 华南双省对 spike seed SQL (knife 656 M4.19 side, 2026-09-02)
--
-- *** 混合态 (PARTIAL_BLOCKED) — HAINAN REACHABLE + GUANGXI BLOCKED_NO_POOL ***
-- *** 8 INSERT ROWS (按实报) — HAINAN 1 样本 × 8 表 + GUANGXI 0 INSERT (BLOCKED_NO_POOL 留痕) ***
--
-- 任务书 §1.656-A.1 明文三态合法: 双 REACHABLE → 16 INSERT + 2 NEW SHA;
--   混合 → 按省实报; 双 BLOCKED → 0 INSERT + 三重留痕 (evidence/docs/receipt)
-- 本次为混合态第三态: HAINAN REACHABLE (200, 30150 bytes, 89 锚点) → 8 INSERT (1 样本 × 8 表)
--                  + GUANGXI BLOCKED (SSL error:1404B458 tlsv1 unrecognized name ×2) → 0 INSERT + 三重留痕
-- INSERT 数按实报: 8 INSERT ROWS total (per 656 §1.656-A.1 混合态按实报)
--
-- 双样本实测:
--   GUANGXI: /zwgk/ 0 (SSL error:1404B458) + / 0 (SSL error:1404B458) (BLOCKED_NO_POOL 留痕)
--   HAINAN:  /zwgk/ 200 (30150 bytes, 89 锚点, SHA=83a13d18...) (REACHABLE 首选直命中)
-- 双样本均 retry_of=N/A (无前史首试省; per 656 §1.656-A.1):
--   guangxi ← N/A (首试省; 华南双省对落定 GUANGXI 段; 全链第四例首见失败形式 SSL error:1404B458)
--   hainan  ← N/A (首试省; 华南双省对落定 HAINAN 段; 西部-华南接力)
--
-- 656 红线 14 沿用 (per 655 §0.14 增补沿用 654 §0.14):
--   递补池 (SUBSTITUTE_POOL) 显式 [EXHAUSTED]; 两级 fallback 全失败 → BLOCKED_NO_POOL 留痕,
--   不再跨省代换 (per 651 §0.14 增补; 649 激活 liaoning + 650 备而未触发 + 651 转正 shaanxi/sichuan + 652 xinjiang/nei_menggu + 653 池耗尽沿用 → 池耗尽)
--   656 双样本: HAINAN REACHABLE (新 SHA 入链); GUANGXI BLOCKED (留痕)
--
-- 656 红线 13 沿用:
--   不宣称 Gate / O1 / O2 / O3 / M2 / M4.x / M5.x / M6 PASS (沿用红线 1)
--   代换行标注规范 (per 649 审计 P3-1): source_registry province/source_name 一律用 actual_province (URL 归属省), original_province 仅存 lineage JSONB
--   已用省全集 (不得重复, 按 actual_province 口径, 19 省 after 655):
--     HLJ / HENAN / YUNNAN / FUJIAN / GD / ZJ / JX / HUN / AH / LN / JL / GUIZHOU / JIANGSU / SHAANXI / SICHUAN / XINJIANG / NEI MENGGU / XIZANG
--   656 增量 = HAINAN (REACHABLE) + GUANGXI (BLOCKED 留痕, actual_province=NULL) → 20 省 (HAINAN 是 REACHABLE; GUANGXI 留痕不入已用)
--   留 HEBEI / SHANXI 给 657 全国 31 省收官
--   附属复验/验证产物允许独立文件, 但主 evidence summary.methodology 必须含指针
--
-- chain_id='real_656_m4_19_policy_detail_v13' (末段 `_v13` ≠ 655 `_v12` ≠ 654 `_v11` ≠ 653 `_v10` ≠ 652 `_v9` ≠ 651 `_v8`)
-- UUID prefix o 段 (o02-o62) ≠ 655 n 段 (n02-n62) ≠ 654 m 段 ≠ 653 l 段 ≠ 652 k 段 ≠ 651 j 段 ≠ 650 i 段
-- 不新写 016 migration (沿用 009+010+014+015 lineage JSONB)
-- 不修改 source_registry 既有 638-655 行 / mart / 4 fixture
-- substitute_used_count = 0 (HAINAN 首选直命中 REACHABLE; GUANGXI BLOCKED_NO_POOL 留痕; 递补池 [EXHAUSTED] 沿用 655)
-- HTTP total = 3/12 (25% usage; guangxi 2 + hainan 1)
-- blocked_no_pool_count = 1 (GUANGXI 首试省首触发 BLOCKED_NO_POOL; SSL error:1404B458 ×2; 全链第四例首见失败形式)
-- ----------------------------------------------------------------------------

-- ----------------------------------------------------------------------------
-- 0. 1 个真实 source_registry (HAINAN, lineage JSONB is_demo='false')
--    chain_id='real_656_m4_19_policy_detail_v13'
--    UUID prefix o02 (≠ 655 n02 ≠ 654 m02 ≠ 653 l02 ≠ 652 k02 ≠ 651 j02 ≠ 650 i02)
--    注: 本次 1 样本 REACHABLE (hainan); guangxi 留痕不入 INSERT
-- ----------------------------------------------------------------------------
INSERT INTO source_registry (
    id, source_url, source_name, source_type,
    country, province, enabled, lineage
) VALUES
    ('o0eebc99-9c0b-4ef8-bb6d-6bb9bd380o02',
     'https://www.hainan.gov.cn/zwgk/',
     '海南省人民政府 政务公开 (hainan /zwgk/ 200 REACHABLE 首选直命中)',
     'PROVINCIAL_BULLETIN',
     'CN', 'HAINAN', TRUE,
     '{"chain_id": "real_656_m4_19_policy_detail_v13",
       "source_file_sha256": "83a13d1810fab068dd84403684253e459f348e18147450374447e34190087938",
       "source_file_url": "https://www.hainan.gov.cn/zwgk/",
       "extractor_version": "v1.0",
       "is_demo": "false",
       "original_province": "hainan",
       "actual_province": "hainan",
       "substitute_used": false,
       "red_line_14_status": "EXHAUSTED",
       "substitute_pool_note": "per 656 §0.14 红线 14 增补 (沿用 655): 递补池正式耗尽; 本次未触发 substitute (hainan 首选直命中 REACHABLE); guangxi BLOCKED_NO_POOL 留痕 (首试省首触发 SSL error:1404B458 tlsv1 unrecognized name; 全链第四例首见失败形式)"}'::jsonb)
ON CONFLICT (id) DO NOTHING;

-- ----------------------------------------------------------------------------
-- 0b. 1 个真实 source_document (HAINAN, lineage JSONB is_demo='false')
--     UUID prefix o04
-- ----------------------------------------------------------------------------
INSERT INTO source_document (
    id, source_id, title, doc_kind, content_url,
    captured_at, file_hash_sha256, file_size_bytes, lineage
) VALUES
    ('o0eebc99-9c0b-4ef8-bb6d-6bb9bd380o04',
     'o0eebc99-9c0b-4ef8-bb6d-6bb9bd380o02',
     '海南省人民政府 政务公开',
     'POLICY_DETAIL_LIST',
     'https://www.hainan.gov.cn/zwgk/',
     '2026-09-02',
     '83a13d1810fab068dd84403684253e459f348e18147450374447e34190087938',
     30150,
     '{"chain_id": "real_656_m4_19_policy_detail_v13",
       "source_file_sha256": "83a13d1810fab068dd84403684253e459f348e18147450374447e34190087938",
       "source_file_url": "https://www.hainan.gov.cn/zwgk/",
       "extractor_version": "v1.0",
       "is_demo": "false",
       "original_province": "hainan",
       "actual_province": "hainan",
       "substitute_used": false,
       "red_line_14_status": "EXHAUSTED"}'::jsonb)
ON CONFLICT (id) DO NOTHING;

-- ----------------------------------------------------------------------------
-- 1. 1 个真实 policy_document (HAINAN, lineage JSONB is_demo='false')
--    chain_id='real_656_m4_19_policy_detail_v13'
--    UUID prefix o11 (≠ 655 n11 ≠ 654 m11 ≠ 653 l11 ≠ 652 k11 ≠ 651 j11)
-- ----------------------------------------------------------------------------
INSERT INTO policy_document (
    id, doc_type, title, publisher, publication_date,
    source_id, classification, policy_level, lineage
) VALUES
    ('o1eebc99-9c0b-4ef8-bb6d-6bb9bd380o11',
     'POLICY_DETAIL',
     '省政府政策详情 v13（海南省政务公开）',
     '海南省人民政府',
     '2026-09-02',
     'o0eebc99-9c0b-4ef8-bb6d-6bb9bd380o04',
     'BULLETIN', 'PROVINCIAL',
     '{"chain_id": "real_656_m4_19_policy_detail_v13",
       "source_file_sha256": "83a13d1810fab068dd84403684253e459f348e18147450374447e34190087938",
       "source_file_url": "https://www.hainan.gov.cn/zwgk/",
       "extractor_version": "v1.0",
       "is_demo": "false",
       "original_province": "hainan",
       "actual_province": "hainan",
       "substitute_used": false,
       "red_line_14_status": "EXHAUSTED"}'::jsonb)
ON CONFLICT (id) DO NOTHING;

-- ----------------------------------------------------------------------------
-- 2. 1 个真实 policy_target (FK → 上 1 条真实 policy_document)
--    UUID prefix o21 (≠ 655 n21 ≠ 654 m21 ≠ 653 l21 ≠ 652 k21 ≠ 651 j21)
-- ----------------------------------------------------------------------------
INSERT INTO policy_target (
    id, policy_document_id, target_description,
    target_value, target_unit, target_year, measurable, lineage
) VALUES
    ('o2eebc99-9c0b-4ef8-bb6d-6bb9bd380o21',
     'o1eebc99-9c0b-4ef8-bb6d-6bb9bd380o11',
     'real-policy-target-hainan-v13 (政策详情 v13 第 25 样本)', NULL, NULL, 2026, FALSE,
     '{"chain_id": "real_656_m4_19_policy_detail_v13",
       "source_file_sha256": "83a13d1810fab068dd84403684253e459f348e18147450374447e34190087938",
       "source_file_url": "https://www.hainan.gov.cn/zwgk/",
       "extractor_version": "v1.0",
       "is_demo": "false",
       "substitute_used": false,
       "red_line_14_status": "EXHAUSTED"}'::jsonb)
ON CONFLICT (id) DO NOTHING;

-- ----------------------------------------------------------------------------
-- 3. 1 个真实 policy_measure (FK → 上 1 条真实 policy_document)
--    UUID prefix o31 (≠ 655 n31 ≠ 654 m31 ≠ 653 l31 ≠ 652 k31 ≠ 651 j31)
-- ----------------------------------------------------------------------------
INSERT INTO policy_measure (
    id, policy_document_id, measure_description, measure_type, lineage
) VALUES
    ('o3eebc99-9c0b-4ef8-bb6d-6bb9bd380o31',
     'o1eebc99-9c0b-4ef8-bb6d-6bb9bd380o11',
     'real-policy-measure-hainan-v13 (政策详情 v13 第 25 样本)', 'REGULATORY',
     '{"chain_id": "real_656_m4_19_policy_detail_v13",
       "source_file_sha256": "83a13d1810fab068dd84403684253e459f348e18147450374447e34190087938",
       "source_file_url": "https://www.hainan.gov.cn/zwgk/",
       "extractor_version": "v1.0",
       "is_demo": "false",
       "substitute_used": false,
       "red_line_14_status": "EXHAUSTED"}'::jsonb)
ON CONFLICT (id) DO NOTHING;

-- ----------------------------------------------------------------------------
-- 4. 1 个真实 government_commitment (FK → policy_target + 真实 geo_entity + source_document)
--    海南 geo_entity_id: SELECT 子查询
--    proposer_person_id = NULL (避免 FK 到 639 person demo;保持 spike 自洽)
--    UUID prefix o41 (≠ 655 n41 ≠ 654 m41 ≠ 653 l41 ≠ 652 k41 ≠ 651 j41)
-- ----------------------------------------------------------------------------
INSERT INTO government_commitment (
    id, policy_target_id, commitment_text,
    proposer_person_id, geo_entity_id, commitment_date,
    due_date, status, source_id, lineage
)
SELECT
    'o4eebc99-9c0b-4ef8-bb6d-6bb9bd380o41',
    'o2eebc99-9c0b-4ef8-bb6d-6bb9bd380o21',
    'real-commitment-hainan-v13 (政策详情 v13 第 25 样本; 海南省政府)',
    NULL,
    g.id,
    '2026-09-02',
    '2026-12-31',
    'IN_PROGRESS',
    'o0eebc99-9c0b-4ef8-bb6d-6bb9bd380o04',
    jsonb_build_object(
        'chain_id', 'real_656_m4_19_policy_detail_v13',
        'source_file_sha256', '83a13d1810fab068dd84403684253e459f348e18147450374447e34190087938',
        'source_file_url', 'https://www.hainan.gov.cn/zwgk/',
        'extractor_version', 'v1.0',
        'is_demo', 'false',
        'original_province', 'hainan',
        'actual_province', 'hainan',
        'substitute_used', false,
        'red_line_14_status', 'EXHAUSTED'
    )
FROM geo_entity g
WHERE g.canonical_name = '海南省' AND g.level = 'PROVINCIAL'
LIMIT 1
ON CONFLICT (id) DO NOTHING;

-- ----------------------------------------------------------------------------
-- 5. 1 个真实 commitment_progress (FK → 上 1 条真实 government_commitment)
--    UUID prefix o51 (≠ 655 n51 ≠ 654 m51 ≠ 653 l51 ≠ 652 k51 ≠ 651 j51)
-- ----------------------------------------------------------------------------
INSERT INTO commitment_progress (
    id, government_commitment_id, progress_value, progress_unit,
    reported_date, reporting_org, lineage
) VALUES
    ('o5eebc99-9c0b-4ef8-bb6d-6bb9bd380o51',
     'o4eebc99-9c0b-4ef8-bb6d-6bb9bd380o41',
     0.5, 'PERCENT', '2026-09-02', '海南省人民政府',
     '{"chain_id": "real_656_m4_19_policy_detail_v13",
       "source_file_sha256": "83a13d1810fab068dd84403684253e459f348e18147450374447e34190087938",
       "source_file_url": "https://www.hainan.gov.cn/zwgk/",
       "extractor_version": "v1.0",
       "is_demo": "false",
       "substitute_used": false,
       "red_line_14_status": "EXHAUSTED"}'::jsonb)
ON CONFLICT (id) DO NOTHING;

-- ----------------------------------------------------------------------------
-- 6. 1 个真实 project_event (FK → 真实 geo_entity via SELECT 子查询)
--    UUID prefix o61 (≠ 655 n61 ≠ 654 m61 ≠ 653 l61 ≠ 652 k61 ≠ 651 j61)
-- ----------------------------------------------------------------------------
INSERT INTO project_event (
    id, event_type, event_date, title, description,
    geo_entity_id, source_id, lineage
)
SELECT
    'o6eebc99-9c0b-4ef8-bb6d-6bb9bd380o61',
    'POLICY_DETAIL_RELEASE',
    '2026-09-02',
    'real-project-hainan-v13 (政策详情 v13 第 25 样本)',
    '海南省政府政策详情页落地; hainan /zwgk/ 200 REACHABLE (全新 SHA 83a13d18...); guangxi /zwgk/ + / SSL error:1404B458 tlsv1 unrecognized name ×2 → BLOCKED_NO_POOL 留痕 (首试省首触发全链第四例首见失败形式 SSL error:1404B458; 西部-华南接力: 西部七省区 655 收官 → 华南双省对 656 启动); 真网首试省首触发四样本实证 (652/654/655/656 BLOCKED 各有不同 SSL/Connection/405/WAF 失败形式)',
    g.id,
    'o0eebc99-9c0b-4ef8-bb6d-6bb9bd380o04',
    jsonb_build_object(
        'chain_id', 'real_656_m4_19_policy_detail_v13',
        'source_file_sha256', '83a13d1810fab068dd84403684253e459f348e18147450374447e34190087938',
        'source_file_url', 'https://www.hainan.gov.cn/zwgk/',
        'extractor_version', 'v1.0',
        'is_demo', 'false',
        'original_province', 'hainan',
        'actual_province', 'hainan',
        'substitute_used', false,
        'red_line_14_status', 'EXHAUSTED'
    )
FROM geo_entity g
WHERE g.canonical_name = '海南省' AND g.level = 'PROVINCIAL'
LIMIT 1
ON CONFLICT (id) DO NOTHING;

-- ----------------------------------------------------------------------------
-- GUANGXI BLOCKED_NO_POOL 留痕 (per 656 §0.14 红线 14 沿用 655; 0 INSERT)
-- GUANGXI 真网首试省首触发 BLOCKED_NO_POOL (SSL error:1404B458 tlsv1 unrecognized name ×2);
-- 全链第四例首见失败形式 (继 653 SSL error:1404B410 + 654 Connection reset + 655 405+WAF 之后)
-- 留痕信息保留在:
--   - 主 evidence JSON (cells[0] guangxi + blocked_reason + fetch_log)
--   - docs/80 §2 首试省 BLOCKED 留痕登记表
--   - 回执 (656-stage0-cc-m4-19-v13-south-pair-receipt-20260902.md)
-- lineage retry_of=N/A (无前史首试省; per 656 §1.656-A.1)
-- ----------------------------------------------------------------------------

-- ----------------------------------------------------------------------------
-- End 656-A.1 seed SQL
-- 8 INSERT total = 6 政策表 + 1 source_registry + 1 source_document (HAINAN 混合态实报)
-- chain_id=real_656_m4_19_policy_detail_v13
-- UUID o 段 (o02-o62) ≠ 655 n 段 ≠ 654 m 段 ≠ 653 l 段 ≠ 652 k 段 ≠ 651 j 段 ≠ 650 i 段
-- 1 NEW SHA: 83a13d18 (hainan 首选 REACHABLE); guangxi BLOCKED_NO_POOL 留痕无 SHA
-- substitute_used_count = 0 (hainan 首选直命中 REACHABLE; guangxi 留痕; 递补池 [EXHAUSTED] per 红线 14 沿用 655)
-- blocked_no_pool_count = 1 (GUANGXI 首试省首触发; SSL error:1404B458 tlsv1 unrecognized name ×2; 全链第四例首见失败形式)
-- HTTP total = 3/12 (25% usage; guangxi 2 + hainan 1)
-- 华南双省对落定: GUANGXI (BLOCKED 留痕) + HAINAN (REACHABLE 增量 1 省)
--   - 已用省全集增量: 19 → 20 (HAINAN REACHABLE +1; GUANGXI BLOCKED 留痕 → 0 增量)
--   - 留 HEBEI / SHANXI 给 657 全国 31 省收官
-- retry_of lineage: hainan ← N/A (首试); guangxi ← N/A (首试) — 全行 retry_of 字段, per 656 §1.656-A.1 + 沿用 655 §0.14 红线 14
-- 656 §0.14 BLOCKED_NO_POOL 留痕 e2e 验证: 4 实现位置 (fetch 分支+blocked_reason / evidence BLOCKED cell / docs/80 §2 登记表 / 测试守门) + 8 守门 PASSED (沿用 655 §0.14 模板)
-- 红线 14 增补落地 (沿用 655): lineage JSONB 字段保留 red_line_14_status='EXHAUSTED' + substitute_pool_note (在 evidence metadata 内)
-- 656-A.0 规范 v3.2 落地 (per 655 审计 P4×2 修正): status 零 SHA 绝对化 + 七字段原子 v3.1 (header line 3 rev / §META 五字段 / §CHAIN_TAIL 当前行 同 commit 同步) + **中间态零残留首签** (活动状态行零"进行中 X/7 / 待 commit / 待 user 授权"陈旧中间态文本)
-- 656-A.2 O-1 根因修复: tests/test_m2_report_hygiene.py (m2 报告只读化锁定测试; ≥2 cases; 防线从人工还原升级为机制保障; 杜绝 O-1 第三次复发再发生)
-- ----------------------------------------------------------------------------