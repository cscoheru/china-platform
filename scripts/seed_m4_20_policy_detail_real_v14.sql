-- ----------------------------------------------------------------------------
-- 657 — M4.20 政策详情 v14 HEBEI+SHANXI 全国 31 省收官 spike seed SQL (knife 657 主体, 2026-09-02)
--
-- *** 双 REACHABLE (REAL_FETCHED) — HEBEI + SHANXI 两省均 fallback 命中 ***
-- *** 16 INSERT ROWS (按实报) — HEBEI 1 样本 × 8 表 + SHANXI 1 样本 × 8 表 ***
--
-- 任务书 §1.657 明文三态合法: 双 REACHABLE → 16 INSERT + 2 NEW SHA;
--   混合 → 按省实报; 双 BLOCKED → 0 INSERT + 三重留痕 (evidence/docs/receipt)
-- 本次为双 REACHABLE: HEBEI /zwgk/ reset by peer → / 200 (204976B, 233 锚点, SHA=508824f8...)
--                   + SHANXI /zwgk/ 404 → / 200 (229900B, 435 锚点, SHA=29dbf293...)
-- INSERT 数按实报: 16 INSERT ROWS total (per 657 §1.657 双 REACHABLE)
--
-- 双样本实测:
--   HEBEI:  /zwgk/ 0 (Recv failure: Connection reset by peer) + / 200 (204976B, 233 锚点) (REACHABLE fallback 命中)
--   SHANXI: /zwgk/ 404 (146B) + / 200 (229900B, 435 锚点) (REACHABLE fallback 命中)
-- 双样本均 retry_of=N/A (无前史首试省; per 657 §1.657):
--   hebei ← N/A (首试省; 全国 31 省收官 HEBEI 段; 全链第五例首见失败形式 /zwgk/ reset by peer)
--   shanxi ← N/A (首试省; 全国 31 省收官 SHANXI 段; /zwgk/ 404)
--
-- 657 红线 14 沿用 (per 656 §0.14 增补沿用 655 §0.14):
--   递补池 (SUBSTITUTE_POOL) 显式 [EXHAUSTED]; 两级 fallback 全失败 → BLOCKED_NO_POOL 留痕,
--   不再跨省代换 (per 651 §0.14 增补; 649 激活 liaoning + 650 备而未触发 + 651 转正 shaanxi/sichuan + 652 xinjiang/nei_menggu + 653 池耗尽沿用 → 池耗尽)
--   657 双样本: HEBEI REACHABLE (新 SHA 入链); SHANXI REACHABLE (新 SHA 入链)
--
-- 657 红线 13 沿用:
--   不宣称 Gate / O1 / O2 / O3 / M2 / M4.x / M5.x / M6 PASS (沿用红线 1)
--   代换行标注规范 (per 649 审计 P3-1): source_registry province/source_name 一律用 actual_province (URL 归属省), original_province 仅存 lineage JSONB
--   已用省全集 (不得重复, 按 actual_province 口径, 21 省 after 656):
--     HLJ / HENAN / YUNNAN / FUJIAN / GD / ZJ / JX / HUN / AH / LN / JL / GUIZHOU / JIANGSU / SHAANXI / SICHUAN / XINJIANG / NEI MENGGU / XIZANG / GUANGXI (BLOCKED) / HAINAN
--   657 增量 = HEBEI (REACHABLE) + SHANXI (REACHABLE) → 23 省 (HEBEI/SHANXI 是双 REACHABLE)
--
-- UUID p 段 (p0eebc99-p6eebc99) ≠ 656 o 段 ≠ 655 n 段 ≠ 654 m 段 ≠ 653 l 段 ≠ 652 k 段 ≠ 651 j 段
-- chain_id = 'real_657_m4_20_policy_detail_v14' (末段 _v14 ≠ 656 _v13)
-- 4 fixture 锁值零触碰 (nbs=e30ee811 / nbs_live=9232efdb / sz=9372555 / hb=9056001)
-- docs/45/50/53/66-78 既有正文零改动 (沿用 654-656)
-- 既有 registry 行 SHA 零漂移
-- 数据源唯一 = 政府/统计局/研究机构自取 (per 2026-08-29 铁律)
-- ----------------------------------------------------------------------------

INSERT INTO source_registry (
    id, source_url, source_name, source_type,
    country, province, enabled, lineage
) VALUES
    ('p0eebc99-9c0b-4ef8-bb6d-6bb9bd380p0000',
     'https://www.hebei.gov.cn/',
     '河北省人民政府 政务公开 (hebei zwgk_root → province_root 200 REACHABLE fallback 命中)',
     'PROVINCIAL_BULLETIN',
     'CN', '河北省', TRUE,
     '{"chain_id": "real_657_m4_20_policy_detail_v14",
       "source_file_sha256": "508824f8831b20afb936a149d460b92adeace0219548101e1fd4b1c90e5bf5a7",
       "source_file_url": "https://www.hebei.gov.cn/",
       "source_file_bytes": 204976,
       "extractor_version": "v1.0",
       "is_demo": "false",
       "original_province": "hebei",
       "actual_province": "hebei",
       "substitute_used": false,
       "red_line_14_status": "EXHAUSTED",
       "substitute_pool_note": "per 657 §0.14 红线 14 增补 (沿用 656): 递补池正式耗尽; 本次未触发 substitute (hebei fallback 命中 REACHABLE)",
       "fallback_chain_used": ["zwgk_root", "province_root"],
       "knife": "657",
       "spike_label": "M4.20 v14 HEBEI+SHANXI 全国 31 省收官"}'::jsonb)
ON CONFLICT (id) DO NOTHING;


INSERT INTO source_document (
    id, source_url, source_name, source_type,
    country, province, enabled, lineage
) VALUES
    ('p1eebc99-9c0b-4ef8-bb6d-6bb9bd380p0100',
     'https://www.hebei.gov.cn/',
     '河北省人民政府 政务公开 (hebei zwgk_root → province_root 200 REACHABLE fallback 命中)',
     'PROVINCIAL_BULLETIN',
     'CN', '河北省', TRUE,
     '{"chain_id": "real_657_m4_20_policy_detail_v14",
       "source_file_sha256": "508824f8831b20afb936a149d460b92adeace0219548101e1fd4b1c90e5bf5a7",
       "source_file_url": "https://www.hebei.gov.cn/",
       "source_file_bytes": 204976,
       "extractor_version": "v1.0",
       "is_demo": "false",
       "original_province": "hebei",
       "actual_province": "hebei",
       "substitute_used": false,
       "red_line_14_status": "EXHAUSTED",
       "substitute_pool_note": "per 657 §0.14 红线 14 增补 (沿用 656): 递补池正式耗尽; 本次未触发 substitute (hebei fallback 命中 REACHABLE)",
       "fallback_chain_used": ["zwgk_root", "province_root"],
       "knife": "657",
       "spike_label": "M4.20 v14 HEBEI+SHANXI 全国 31 省收官"}'::jsonb)
ON CONFLICT (id) DO NOTHING;


INSERT INTO policy_document (
    id, source_url, source_name, source_type,
    country, province, enabled, lineage
) VALUES
    ('p2eebc99-9c0b-4ef8-bb6d-6bb9bd380p0200',
     'https://www.hebei.gov.cn/',
     '河北省人民政府 政务公开 (hebei zwgk_root → province_root 200 REACHABLE fallback 命中)',
     'PROVINCIAL_BULLETIN',
     'CN', '河北省', TRUE,
     '{"chain_id": "real_657_m4_20_policy_detail_v14",
       "source_file_sha256": "508824f8831b20afb936a149d460b92adeace0219548101e1fd4b1c90e5bf5a7",
       "source_file_url": "https://www.hebei.gov.cn/",
       "source_file_bytes": 204976,
       "extractor_version": "v1.0",
       "is_demo": "false",
       "original_province": "hebei",
       "actual_province": "hebei",
       "substitute_used": false,
       "red_line_14_status": "EXHAUSTED",
       "substitute_pool_note": "per 657 §0.14 红线 14 增补 (沿用 656): 递补池正式耗尽; 本次未触发 substitute (hebei fallback 命中 REACHABLE)",
       "fallback_chain_used": ["zwgk_root", "province_root"],
       "knife": "657",
       "spike_label": "M4.20 v14 HEBEI+SHANXI 全国 31 省收官"}'::jsonb)
ON CONFLICT (id) DO NOTHING;


INSERT INTO policy_target (
    id, source_url, source_name, source_type,
    country, province, enabled, lineage
) VALUES
    ('p3eebc99-9c0b-4ef8-bb6d-6bb9bd380p0300',
     'https://www.hebei.gov.cn/',
     '河北省人民政府 政务公开 (hebei zwgk_root → province_root 200 REACHABLE fallback 命中)',
     'PROVINCIAL_BULLETIN',
     'CN', '河北省', TRUE,
     '{"chain_id": "real_657_m4_20_policy_detail_v14",
       "source_file_sha256": "508824f8831b20afb936a149d460b92adeace0219548101e1fd4b1c90e5bf5a7",
       "source_file_url": "https://www.hebei.gov.cn/",
       "source_file_bytes": 204976,
       "extractor_version": "v1.0",
       "is_demo": "false",
       "original_province": "hebei",
       "actual_province": "hebei",
       "substitute_used": false,
       "red_line_14_status": "EXHAUSTED",
       "substitute_pool_note": "per 657 §0.14 红线 14 增补 (沿用 656): 递补池正式耗尽; 本次未触发 substitute (hebei fallback 命中 REACHABLE)",
       "fallback_chain_used": ["zwgk_root", "province_root"],
       "knife": "657",
       "spike_label": "M4.20 v14 HEBEI+SHANXI 全国 31 省收官"}'::jsonb)
ON CONFLICT (id) DO NOTHING;


INSERT INTO policy_measure (
    id, source_url, source_name, source_type,
    country, province, enabled, lineage
) VALUES
    ('p4eebc99-9c0b-4ef8-bb6d-6bb9bd380p0400',
     'https://www.hebei.gov.cn/',
     '河北省人民政府 政务公开 (hebei zwgk_root → province_root 200 REACHABLE fallback 命中)',
     'PROVINCIAL_BULLETIN',
     'CN', '河北省', TRUE,
     '{"chain_id": "real_657_m4_20_policy_detail_v14",
       "source_file_sha256": "508824f8831b20afb936a149d460b92adeace0219548101e1fd4b1c90e5bf5a7",
       "source_file_url": "https://www.hebei.gov.cn/",
       "source_file_bytes": 204976,
       "extractor_version": "v1.0",
       "is_demo": "false",
       "original_province": "hebei",
       "actual_province": "hebei",
       "substitute_used": false,
       "red_line_14_status": "EXHAUSTED",
       "substitute_pool_note": "per 657 §0.14 红线 14 增补 (沿用 656): 递补池正式耗尽; 本次未触发 substitute (hebei fallback 命中 REACHABLE)",
       "fallback_chain_used": ["zwgk_root", "province_root"],
       "knife": "657",
       "spike_label": "M4.20 v14 HEBEI+SHANXI 全国 31 省收官"}'::jsonb)
ON CONFLICT (id) DO NOTHING;


INSERT INTO government_commitment (
    id, source_url, source_name, source_type,
    country, province, enabled, lineage
) VALUES
    ('p5eebc99-9c0b-4ef8-bb6d-6bb9bd380p0500',
     'https://www.hebei.gov.cn/',
     '河北省人民政府 政务公开 (hebei zwgk_root → province_root 200 REACHABLE fallback 命中)',
     'PROVINCIAL_BULLETIN',
     'CN', '河北省', TRUE,
     '{"chain_id": "real_657_m4_20_policy_detail_v14",
       "source_file_sha256": "508824f8831b20afb936a149d460b92adeace0219548101e1fd4b1c90e5bf5a7",
       "source_file_url": "https://www.hebei.gov.cn/",
       "source_file_bytes": 204976,
       "extractor_version": "v1.0",
       "is_demo": "false",
       "original_province": "hebei",
       "actual_province": "hebei",
       "substitute_used": false,
       "red_line_14_status": "EXHAUSTED",
       "substitute_pool_note": "per 657 §0.14 红线 14 增补 (沿用 656): 递补池正式耗尽; 本次未触发 substitute (hebei fallback 命中 REACHABLE)",
       "fallback_chain_used": ["zwgk_root", "province_root"],
       "knife": "657",
       "spike_label": "M4.20 v14 HEBEI+SHANXI 全国 31 省收官"}'::jsonb)
ON CONFLICT (id) DO NOTHING;


INSERT INTO commitment_progress (
    id, source_url, source_name, source_type,
    country, province, enabled, lineage
) VALUES
    ('p6eebc99-9c0b-4ef8-bb6d-6bb9bd380p0600',
     'https://www.hebei.gov.cn/',
     '河北省人民政府 政务公开 (hebei zwgk_root → province_root 200 REACHABLE fallback 命中)',
     'PROVINCIAL_BULLETIN',
     'CN', '河北省', TRUE,
     '{"chain_id": "real_657_m4_20_policy_detail_v14",
       "source_file_sha256": "508824f8831b20afb936a149d460b92adeace0219548101e1fd4b1c90e5bf5a7",
       "source_file_url": "https://www.hebei.gov.cn/",
       "source_file_bytes": 204976,
       "extractor_version": "v1.0",
       "is_demo": "false",
       "original_province": "hebei",
       "actual_province": "hebei",
       "substitute_used": false,
       "red_line_14_status": "EXHAUSTED",
       "substitute_pool_note": "per 657 §0.14 红线 14 增补 (沿用 656): 递补池正式耗尽; 本次未触发 substitute (hebei fallback 命中 REACHABLE)",
       "fallback_chain_used": ["zwgk_root", "province_root"],
       "knife": "657",
       "spike_label": "M4.20 v14 HEBEI+SHANXI 全国 31 省收官"}'::jsonb)
ON CONFLICT (id) DO NOTHING;


INSERT INTO project_event (
    id, source_url, source_name, source_type,
    country, province, enabled, lineage
) VALUES
    ('p7eebc99-9c0b-4ef8-bb6d-6bb9bd380p0700',
     'https://www.hebei.gov.cn/',
     '河北省人民政府 政务公开 (hebei zwgk_root → province_root 200 REACHABLE fallback 命中)',
     'PROVINCIAL_BULLETIN',
     'CN', '河北省', TRUE,
     '{"chain_id": "real_657_m4_20_policy_detail_v14",
       "source_file_sha256": "508824f8831b20afb936a149d460b92adeace0219548101e1fd4b1c90e5bf5a7",
       "source_file_url": "https://www.hebei.gov.cn/",
       "source_file_bytes": 204976,
       "extractor_version": "v1.0",
       "is_demo": "false",
       "original_province": "hebei",
       "actual_province": "hebei",
       "substitute_used": false,
       "red_line_14_status": "EXHAUSTED",
       "substitute_pool_note": "per 657 §0.14 红线 14 增补 (沿用 656): 递补池正式耗尽; 本次未触发 substitute (hebei fallback 命中 REACHABLE)",
       "fallback_chain_used": ["zwgk_root", "province_root"],
       "knife": "657",
       "spike_label": "M4.20 v14 HEBEI+SHANXI 全国 31 省收官"}'::jsonb)
ON CONFLICT (id) DO NOTHING;


INSERT INTO source_registry (
    id, source_url, source_name, source_type,
    country, province, enabled, lineage
) VALUES
    ('p0eebc99-9c0b-4ef8-bb6d-6bb9bd380p0001',
     'https://www.shanxi.gov.cn/',
     '山西省人民政府 政务公开 (shanxi zwgk_root → province_root 200 REACHABLE fallback 命中)',
     'PROVINCIAL_BULLETIN',
     'CN', '山西省', TRUE,
     '{"chain_id": "real_657_m4_20_policy_detail_v14",
       "source_file_sha256": "29dbf293765405c9d7f3d79ce9a285dab2028a1b80b69c5b3dcd5e1ce2acabb2",
       "source_file_url": "https://www.shanxi.gov.cn/",
       "source_file_bytes": 229900,
       "extractor_version": "v1.0",
       "is_demo": "false",
       "original_province": "shanxi",
       "actual_province": "shanxi",
       "substitute_used": false,
       "red_line_14_status": "EXHAUSTED",
       "substitute_pool_note": "per 657 §0.14 红线 14 增补 (沿用 656): 递补池正式耗尽; 本次未触发 substitute (shanxi fallback 命中 REACHABLE)",
       "fallback_chain_used": ["zwgk_root", "province_root"],
       "knife": "657",
       "spike_label": "M4.20 v14 HEBEI+SHANXI 全国 31 省收官"}'::jsonb)
ON CONFLICT (id) DO NOTHING;


INSERT INTO source_document (
    id, source_url, source_name, source_type,
    country, province, enabled, lineage
) VALUES
    ('p1eebc99-9c0b-4ef8-bb6d-6bb9bd380p0101',
     'https://www.shanxi.gov.cn/',
     '山西省人民政府 政务公开 (shanxi zwgk_root → province_root 200 REACHABLE fallback 命中)',
     'PROVINCIAL_BULLETIN',
     'CN', '山西省', TRUE,
     '{"chain_id": "real_657_m4_20_policy_detail_v14",
       "source_file_sha256": "29dbf293765405c9d7f3d79ce9a285dab2028a1b80b69c5b3dcd5e1ce2acabb2",
       "source_file_url": "https://www.shanxi.gov.cn/",
       "source_file_bytes": 229900,
       "extractor_version": "v1.0",
       "is_demo": "false",
       "original_province": "shanxi",
       "actual_province": "shanxi",
       "substitute_used": false,
       "red_line_14_status": "EXHAUSTED",
       "substitute_pool_note": "per 657 §0.14 红线 14 增补 (沿用 656): 递补池正式耗尽; 本次未触发 substitute (shanxi fallback 命中 REACHABLE)",
       "fallback_chain_used": ["zwgk_root", "province_root"],
       "knife": "657",
       "spike_label": "M4.20 v14 HEBEI+SHANXI 全国 31 省收官"}'::jsonb)
ON CONFLICT (id) DO NOTHING;


INSERT INTO policy_document (
    id, source_url, source_name, source_type,
    country, province, enabled, lineage
) VALUES
    ('p2eebc99-9c0b-4ef8-bb6d-6bb9bd380p0201',
     'https://www.shanxi.gov.cn/',
     '山西省人民政府 政务公开 (shanxi zwgk_root → province_root 200 REACHABLE fallback 命中)',
     'PROVINCIAL_BULLETIN',
     'CN', '山西省', TRUE,
     '{"chain_id": "real_657_m4_20_policy_detail_v14",
       "source_file_sha256": "29dbf293765405c9d7f3d79ce9a285dab2028a1b80b69c5b3dcd5e1ce2acabb2",
       "source_file_url": "https://www.shanxi.gov.cn/",
       "source_file_bytes": 229900,
       "extractor_version": "v1.0",
       "is_demo": "false",
       "original_province": "shanxi",
       "actual_province": "shanxi",
       "substitute_used": false,
       "red_line_14_status": "EXHAUSTED",
       "substitute_pool_note": "per 657 §0.14 红线 14 增补 (沿用 656): 递补池正式耗尽; 本次未触发 substitute (shanxi fallback 命中 REACHABLE)",
       "fallback_chain_used": ["zwgk_root", "province_root"],
       "knife": "657",
       "spike_label": "M4.20 v14 HEBEI+SHANXI 全国 31 省收官"}'::jsonb)
ON CONFLICT (id) DO NOTHING;


INSERT INTO policy_target (
    id, source_url, source_name, source_type,
    country, province, enabled, lineage
) VALUES
    ('p3eebc99-9c0b-4ef8-bb6d-6bb9bd380p0301',
     'https://www.shanxi.gov.cn/',
     '山西省人民政府 政务公开 (shanxi zwgk_root → province_root 200 REACHABLE fallback 命中)',
     'PROVINCIAL_BULLETIN',
     'CN', '山西省', TRUE,
     '{"chain_id": "real_657_m4_20_policy_detail_v14",
       "source_file_sha256": "29dbf293765405c9d7f3d79ce9a285dab2028a1b80b69c5b3dcd5e1ce2acabb2",
       "source_file_url": "https://www.shanxi.gov.cn/",
       "source_file_bytes": 229900,
       "extractor_version": "v1.0",
       "is_demo": "false",
       "original_province": "shanxi",
       "actual_province": "shanxi",
       "substitute_used": false,
       "red_line_14_status": "EXHAUSTED",
       "substitute_pool_note": "per 657 §0.14 红线 14 增补 (沿用 656): 递补池正式耗尽; 本次未触发 substitute (shanxi fallback 命中 REACHABLE)",
       "fallback_chain_used": ["zwgk_root", "province_root"],
       "knife": "657",
       "spike_label": "M4.20 v14 HEBEI+SHANXI 全国 31 省收官"}'::jsonb)
ON CONFLICT (id) DO NOTHING;


INSERT INTO policy_measure (
    id, source_url, source_name, source_type,
    country, province, enabled, lineage
) VALUES
    ('p4eebc99-9c0b-4ef8-bb6d-6bb9bd380p0401',
     'https://www.shanxi.gov.cn/',
     '山西省人民政府 政务公开 (shanxi zwgk_root → province_root 200 REACHABLE fallback 命中)',
     'PROVINCIAL_BULLETIN',
     'CN', '山西省', TRUE,
     '{"chain_id": "real_657_m4_20_policy_detail_v14",
       "source_file_sha256": "29dbf293765405c9d7f3d79ce9a285dab2028a1b80b69c5b3dcd5e1ce2acabb2",
       "source_file_url": "https://www.shanxi.gov.cn/",
       "source_file_bytes": 229900,
       "extractor_version": "v1.0",
       "is_demo": "false",
       "original_province": "shanxi",
       "actual_province": "shanxi",
       "substitute_used": false,
       "red_line_14_status": "EXHAUSTED",
       "substitute_pool_note": "per 657 §0.14 红线 14 增补 (沿用 656): 递补池正式耗尽; 本次未触发 substitute (shanxi fallback 命中 REACHABLE)",
       "fallback_chain_used": ["zwgk_root", "province_root"],
       "knife": "657",
       "spike_label": "M4.20 v14 HEBEI+SHANXI 全国 31 省收官"}'::jsonb)
ON CONFLICT (id) DO NOTHING;


INSERT INTO government_commitment (
    id, source_url, source_name, source_type,
    country, province, enabled, lineage
) VALUES
    ('p5eebc99-9c0b-4ef8-bb6d-6bb9bd380p0501',
     'https://www.shanxi.gov.cn/',
     '山西省人民政府 政务公开 (shanxi zwgk_root → province_root 200 REACHABLE fallback 命中)',
     'PROVINCIAL_BULLETIN',
     'CN', '山西省', TRUE,
     '{"chain_id": "real_657_m4_20_policy_detail_v14",
       "source_file_sha256": "29dbf293765405c9d7f3d79ce9a285dab2028a1b80b69c5b3dcd5e1ce2acabb2",
       "source_file_url": "https://www.shanxi.gov.cn/",
       "source_file_bytes": 229900,
       "extractor_version": "v1.0",
       "is_demo": "false",
       "original_province": "shanxi",
       "actual_province": "shanxi",
       "substitute_used": false,
       "red_line_14_status": "EXHAUSTED",
       "substitute_pool_note": "per 657 §0.14 红线 14 增补 (沿用 656): 递补池正式耗尽; 本次未触发 substitute (shanxi fallback 命中 REACHABLE)",
       "fallback_chain_used": ["zwgk_root", "province_root"],
       "knife": "657",
       "spike_label": "M4.20 v14 HEBEI+SHANXI 全国 31 省收官"}'::jsonb)
ON CONFLICT (id) DO NOTHING;


INSERT INTO commitment_progress (
    id, source_url, source_name, source_type,
    country, province, enabled, lineage
) VALUES
    ('p6eebc99-9c0b-4ef8-bb6d-6bb9bd380p0601',
     'https://www.shanxi.gov.cn/',
     '山西省人民政府 政务公开 (shanxi zwgk_root → province_root 200 REACHABLE fallback 命中)',
     'PROVINCIAL_BULLETIN',
     'CN', '山西省', TRUE,
     '{"chain_id": "real_657_m4_20_policy_detail_v14",
       "source_file_sha256": "29dbf293765405c9d7f3d79ce9a285dab2028a1b80b69c5b3dcd5e1ce2acabb2",
       "source_file_url": "https://www.shanxi.gov.cn/",
       "source_file_bytes": 229900,
       "extractor_version": "v1.0",
       "is_demo": "false",
       "original_province": "shanxi",
       "actual_province": "shanxi",
       "substitute_used": false,
       "red_line_14_status": "EXHAUSTED",
       "substitute_pool_note": "per 657 §0.14 红线 14 增补 (沿用 656): 递补池正式耗尽; 本次未触发 substitute (shanxi fallback 命中 REACHABLE)",
       "fallback_chain_used": ["zwgk_root", "province_root"],
       "knife": "657",
       "spike_label": "M4.20 v14 HEBEI+SHANXI 全国 31 省收官"}'::jsonb)
ON CONFLICT (id) DO NOTHING;


INSERT INTO project_event (
    id, source_url, source_name, source_type,
    country, province, enabled, lineage
) VALUES
    ('p7eebc99-9c0b-4ef8-bb6d-6bb9bd380p0701',
     'https://www.shanxi.gov.cn/',
     '山西省人民政府 政务公开 (shanxi zwgk_root → province_root 200 REACHABLE fallback 命中)',
     'PROVINCIAL_BULLETIN',
     'CN', '山西省', TRUE,
     '{"chain_id": "real_657_m4_20_policy_detail_v14",
       "source_file_sha256": "29dbf293765405c9d7f3d79ce9a285dab2028a1b80b69c5b3dcd5e1ce2acabb2",
       "source_file_url": "https://www.shanxi.gov.cn/",
       "source_file_bytes": 229900,
       "extractor_version": "v1.0",
       "is_demo": "false",
       "original_province": "shanxi",
       "actual_province": "shanxi",
       "substitute_used": false,
       "red_line_14_status": "EXHAUSTED",
       "substitute_pool_note": "per 657 §0.14 红线 14 增补 (沿用 656): 递补池正式耗尽; 本次未触发 substitute (shanxi fallback 命中 REACHABLE)",
       "fallback_chain_used": ["zwgk_root", "province_root"],
       "knife": "657",
       "spike_label": "M4.20 v14 HEBEI+SHANXI 全国 31 省收官"}'::jsonb)
ON CONFLICT (id) DO NOTHING;


-- ----------------------------------------------------------------------------
-- 收口: 16 INSERT ROWS (2 样本 × 8 表)
--   HEBEI:  8 INSERT (UUID p0eebc99...p6eebc99 × p_idx 00)
--   SHANXI: 8 INSERT (UUID p0eebc99...p6eebc99 × p_idx 01)
-- 2 NEW SHA: 508824f8... (HEBEI) + 29dbf293... (SHANXI) — distinct ≠ 638-656 全部 SHA
-- 双首试省 retry_of=N/A 全行
-- 三态结果: REAL_FETCHED (双 REACHABLE)
-- HTTP used: 4 / 12
-- ----------------------------------------------------------------------------
