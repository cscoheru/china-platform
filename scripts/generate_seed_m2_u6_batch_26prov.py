#!/usr/bin/env python3
"""658 generate_seed_sql.py — Generate seed_m2_u6_batch_26prov.sql from evidence_pack.

Reads:  evidence_pack/u6_batch_26prov_fetch_20260902.json (23 REACHABLE cells)
Writes: scripts/seed_m2_u6_batch_26prov.sql (full INSERT bundle)

Schema constraints (per schema/01-core.sql + 657 ingest_m2_2024_gdp.py patterns):
  source_registry columns:   id, domain, organization, category, primary_url,
                             update_frequency, auth_note, access_method,
                             historical_coverage, stability_note, failure_handling,
                             enabled, source_level, lineage
  source_document columns:   id, source_id, file_path, file_size_bytes,
                             file_hash_sha256, mime_type, retrieval_method,
                             retrieval_at, raw_content_ref
  source_location columns:   id, source_id, location_type, url, http_code,
                             accessed_at, content_hash, notes
  ingestion_run columns:     id, source_id, started_at, finished_at,
                             records_inserted, records_updated, records_skipped,
                             status, error_message, run_kind
  observation columns:       id, indicator_id, indicator_methodology_version_id,
                             geo_entity_id, geo_code_version_id, calendar_period_id,
                             value, raw_value, is_imputed, missing_reason,
                             unit, comparison_basis, value_type, status,
                             source_id, source_location_id, ingestion_run_id,
                             extracted_at, extraction_method, confidence, notes

UUID scheme (per 658 tasking "UUID q 段 (q0eebc99-q6eebc99)"):
  q0eebc99-{idx:08x}-...-{idx:012x}  = source_registry (q0)
  q1eebc99-{idx:08x}-...-{idx:012x}  = source_document (q1)
  q2eebc99-{idx:08x}-...-{idx:012x}  = source_location (q2)
  q6eebc99-{idx:08x}-...-{idx:012x}  = observation (q6)
  q7eebc99-{idx:08x}-...-{idx:012x}  = ingestion_run (q7)

  Where {idx} = 0..22 for the 23 REACHABLE provinces, in evidence_pack order.

Indicator IDs (a-prefix, 657 M2 namespace):
  a2000000-0000-0000-0000-00000000a001 = GDP_ANNUAL
  a2000000-0000-0000-0000-00000000a003 = GDP_GROWTH
  a2000000-0000-0000-0000-00000000a004 = GVA_PRIMARY
  a2000000-0000-0000-0000-00000000a005 = GVA_SECONDARY
  a2000000-0000-0000-0000-00000000a006 = GVA_TERTIARY

Methodology version IDs (a-prefix):
  a2000000-0000-0000-0000-00000000a002 = M2-b 2024 GDP MV
  a2000000-0000-0000-0000-00000000a007 = M2-b 2024 GDP_GROWTH MV
  a2000000-0000-0000-0000-00000000a008 = M2-b 2024 GVA_PRIMARY MV
  a2000000-0000-0000-0000-00000000a009 = M2-b 2024 GVA_SECONDARY MV
  a2000000-0000-0000-0000-00000000a010 = M2-b 2024 GVA_TERTIARY MV

Geo entity UUIDs (from 657 M2 family pattern; per-province admin_code 12-65):
  a2000000-0000-0000-0000-{admin_code:012d}

Calendar period (2024):
  a2000000-0000-0000-0000-000020240101 (existing 657 fixture)

GB/T 2260 doc (existing fixture):
  a2000000-0000-0000-0000-0000000ff227

Province admin codes (GB/T 2260):
  tianjin=12, chongqing=50, hebei=13, shanxi=14, neimenggu=15,
  jilin=22, heilongjiang=23, jiangsu=32, zhejiang=33, anhui=34,
  fujian=35, jiangxi=36, henan=41, hunan=43, guangdong=44,
  guangxi=45, yunnan=53, xizang=54, shaanxi=61, gansu=62,
  qinghai=63, ningxia=64, xinjiang=65

Lineage 三重标注 (per U6 ruling):
  source = "hongheiku_tjgb" (reprint source domain)
  origin = "XX省统计局" (provincial bureau origin)
  ruling = "U6 2026-09-02" (user ruling)
"""
import json
import sys
from pathlib import Path

REPO = Path('/Users/kjonekong/projects/china platform')

# Province -> (chinese_name, admin_code)
PROVINCE_INFO = {
    'tianjin':      ('天津市', 12),
    'chongqing':    ('重庆市', 50),
    'hebei':        ('河北省', 13),
    'shanxi':       ('山西省', 14),
    'neimenggu':    ('内蒙古自治区', 15),
    'jilin':        ('吉林省', 22),
    'heilongjiang': ('黑龙江省', 23),
    'jiangsu':      ('江苏省', 32),
    'zhejiang':     ('浙江省', 33),
    'anhui':        ('安徽省', 34),
    'fujian':       ('福建省', 35),
    'jiangxi':      ('江西省', 36),
    'henan':        ('河南省', 41),
    'hunan':        ('湖南省', 43),
    'guangdong':    ('广东省', 44),
    'guangxi':      ('广西壮族自治区', 45),
    'yunnan':       ('云南省', 53),
    'xizang':       ('西藏自治区', 54),
    'shaanxi':      ('陕西省', 61),
    'gansu':        ('甘肃省', 62),
    'qinghai':      ('青海省', 63),
    'ningxia':      ('宁夏回族自治区', 64),
    'xinjiang':     ('新疆维吾尔自治区', 65),
}

# Indicator short_code -> (id, mv_id, label)
INDICATORS = {
    'gdp_total': ('a2000000-0000-0000-0000-00000000a001',
                  'a2000000-0000-0000-0000-00000000a002',
                  'GDP_ANNUAL', '亿元'),
    'growth':    ('a2000000-0000-0000-0000-00000000a003',
                  'a2000000-0000-0000-0000-00000000a007',
                  'GDP_GROWTH', '%'),
    'primary':   ('a2000000-0000-0000-0000-00000000a004',
                  'a2000000-0000-0000-0000-00000000a008',
                  'GVA_PRIMARY', '亿元'),
    'secondary': ('a2000000-0000-0000-0000-00000000a005',
                  'a2000000-0000-0000-0000-00000000a009',
                  'GVA_SECONDARY', '亿元'),
    'tertiary':  ('a2000000-0000-0000-0000-00000000a006',
                  'a2000000-0000-0000-0000-00000000a010',
                  'GVA_TERTIARY', '亿元'),
}

CALENDAR_PERIOD_2024 = 'a2000000-0000-0000-0000-000020240101'
GB_T2260_DOC_ID = 'a2000000-0000-0000-0000-0000000ff227'

def q_uuid(prefix: int, idx: int, suffix: int) -> str:
    """Build a q-prefix UUID in q{prefix}eebc99-XXXX-XXXX-XXXX-{suffix:012d} form."""
    return f'q{prefix}eebc99-{idx:04x}-4000-8000-{suffix:012d}'

def geo_entity_uuid(admin_code: int) -> str:
    return f'a2000000-0000-0000-0000-{admin_code:012d}'

def geo_cv_uuid(admin_code: int) -> str:
    return f'a2000000-0000-0000-0000-{admin_code:012d}01'


def main() -> int:
    evidence_path = REPO / 'evidence_pack' / 'u6_batch_26prov_fetch_20260902.json'
    evidence = json.loads(evidence_path.read_text(encoding='utf-8'))

    reachable = [c for c in evidence['cells'] if c['verdict'] == 'REACHABLE']
    blocked = evidence['blocked_provinces']
    if len(reachable) != 23:
        print(f'FATAL: expected 23 REACHABLE cells, got {len(reachable)}')
        return 1

    out_lines = []
    out_lines.append("""-- ============================================================================
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
     '""" + GB_T2260_DOC_ID + """'),
    ('a2000000-0000-0000-0000-00000000a007',
     'a2000000-0000-0000-0000-00000000a003',
     'M2-b 2024 年度 GDP 增长率', '2024-01-01'::date,
     'M2-b 2024 年度 GDP 同比增长率',
     '2024 年同比增长率；不变价计算',
     '""" + GB_T2260_DOC_ID + """'),
    ('a2000000-0000-0000-0000-00000000a008',
     'a2000000-0000-0000-0000-00000000a004',
     'M2-b 2024 年度 第一产业增加值', '2024-01-01'::date,
     'M2-b 2024 年度 第一产业增加值初步核算口径',
     '2024 年初步核算',
     '""" + GB_T2260_DOC_ID + """'),
    ('a2000000-0000-0000-0000-00000000a009',
     'a2000000-0000-0000-0000-00000000a005',
     'M2-b 2024 年度 第二产业增加值', '2024-01-01'::date,
     'M2-b 2024 年度 第二产业增加值初步核算口径',
     '2024 年初步核算',
     '""" + GB_T2260_DOC_ID + """'),
    ('a2000000-0000-0000-0000-00000000a010',
     'a2000000-0000-0000-0000-00000000a006',
     'M2-b 2024 年度 第三产业增加值', '2024-01-01'::date,
     'M2-b 2024 年度 第三产业增加值初步核算口径',
     '2024 年初步核算',
     '""" + GB_T2260_DOC_ID + """')
ON CONFLICT (id) DO NOTHING;
""")

    # ---- Per-province INSERT bundle ----
    out_lines.append("""
-- ----------------------------------------------------------------------------
-- 1-23. 23 REACHABLE province (per-province: registry + document + location +
--                                ingestion_run + 5 observations)
--    UUID q 段 (q0eebc99/q1eebc99/q2eebc99/q6eebc99/q7eebc99) ≠ 657 p 段
--    5 指标 × 23 省 = 115 observation rows
-- ----------------------------------------------------------------------------
""")

    for idx, cell in enumerate(reachable):
        prov_en = cell['province']
        prov_zh, admin_code = PROVINCE_INFO[prov_en]
        url = cell['url']
        sha256 = cell['sha256']
        size_bytes = cell['bytes']
        extracted = cell['extracted']

        registry_id = q_uuid(0, idx, idx)
        doc_id      = q_uuid(1, idx, idx)
        loc_id      = q_uuid(2, idx, idx)
        run_id      = q_uuid(7, idx, idx)
        obs_gdp_id      = q_uuid(6, idx, idx * 5 + 0)
        obs_growth_id   = q_uuid(6, idx, idx * 5 + 1)
        obs_primary_id  = q_uuid(6, idx, idx * 5 + 2)
        obs_secondary_id = q_uuid(6, idx, idx * 5 + 3)
        obs_tertiary_id  = q_uuid(6, idx, idx * 5 + 4)

        geo_entity = geo_entity_uuid(admin_code)
        geo_cv = geo_cv_uuid(admin_code)

        out_lines.append(f"""-- Province {idx+1:02d}: {prov_en} ({prov_zh}, admin_code={admin_code}, idx={idx:02d})
DO $$
DECLARE
    v_registry_id UUID := '{registry_id}';
    v_doc_id UUID := '{doc_id}';
    v_loc_id UUID := '{loc_id}';
    v_run_id UUID := '{run_id}';
    v_geo_entity_id UUID := '{geo_entity}';
    v_geo_cv_id UUID := '{geo_cv}';
BEGIN
    -- 1) source_registry (hongheiku_tjgb, origin={prov_zh}统计局)
    INSERT INTO cegr.source_registry
        (id, domain, organization, category, primary_url,
         update_frequency, auth_note, access_method,
         historical_coverage, stability_note, failure_handling,
         enabled, source_level,
         lineage)
    VALUES
        (v_registry_id, 'tjgb.hongheiku.com',
         'hongheiku 转载 (origin: {prov_zh}统计局)', 'PROVINCIAL_BULLETIN_REPRINT',
         '{url}', 'ANNUAL',
         '公开转载;hongheiku 红黑统计公报库;U6 用户裁定接受',
         'HTTP_CURL', '2024 年度公报',
         'U6 金丝雀 5/5 PASS (京/沪/鲁/鄂/川 delta=0 全等)',
         'BLOCKED_NO_POOL 留痕不代换 (红线 14)',
         TRUE, 'S2_REPRINT',
         jsonb_build_object(
             'chain_id', 'real_658_m2_u6_batch_v1'::text,
             'knife', '658',
             'source', 'hongheiku_tjgb',
             'origin', '{prov_zh}统计局',
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
         '/tmp/_658_{prov_en}.html',
         {size_bytes},
         '{sha256}',
         'text/html', 'HTTP_CURL',
         '2026-09-02'::timestamp,
         'evidence_pack/u6_batch_26prov_fetch_20260902.json#{prov_en}')
    ON CONFLICT (id) DO NOTHING;

    -- 3) source_location (URL + http_code 200)
    INSERT INTO cegr.source_location
        (id, source_id, location_type, url, http_code,
         accessed_at, content_hash, notes)
    VALUES
        (v_loc_id, v_registry_id, 'PRIMARY_URL',
         '{url}', 200,
         '2026-09-02'::timestamp,
         '{sha256}',
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
""")

        # 5) 5 observation rows (GDP/growth/primary/sec/tert)
        obs_pairs = [
            ('gdp_total', obs_gdp_id, 'GDP_ANNUAL', '亿元', 'REAL'),
            ('growth',    obs_growth_id, 'GDP_GROWTH', '%',  'REAL'),
            ('primary',   obs_primary_id, 'GVA_PRIMARY', '亿元', 'REAL'),
            ('secondary', obs_secondary_id, 'GVA_SECONDARY', '亿元', 'REAL'),
            ('tertiary',  obs_tertiary_id, 'GVA_TERTIARY', '亿元', 'REAL'),
        ]
        for key, obs_id, short_code, unit, val_type in obs_pairs:
            if key not in extracted:
                out_lines.append(f"""    -- observation {short_code}: missing → NULL + missing_reason (禁补零)
    INSERT INTO cegr.observation
        (id, indicator_id, indicator_methodology_version_id,
         geo_entity_id, geo_code_version_id, calendar_period_id,
         value, raw_value, is_imputed, missing_reason,
         unit, comparison_basis, value_type, status,
         source_id, source_location_id, ingestion_run_id,
         extracted_at, extraction_method, confidence, notes)
    VALUES
        ('{obs_id}',
         '{INDICATORS[key][0]}', '{INDICATORS[key][1]}',
         v_geo_entity_id, v_geo_cv_id, '{CALENDAR_PERIOD_2024}',
         NULL, NULL, FALSE, 'NOT_FOUND_IN_2024_INDEX',
         '{unit}', 'YEAR_OVER_YEAR', '{val_type}', 'MISSING',
         v_registry_id, v_loc_id, v_run_id,
         '2026-09-02'::timestamp, 'REGEX_ANCHORED', 0.0,
         '{prov_en} {short_code} 缺值 (U6 hongheiku 转载页未抓到该指标)')
    ON CONFLICT (id) DO NOTHING;
""")
            else:
                v = extracted[key]
                ind_id, mv_id, _, _ = INDICATORS[key]
                out_lines.append(f"""    -- observation {short_code}: {v} {unit}
    INSERT INTO cegr.observation
        (id, indicator_id, indicator_methodology_version_id,
         geo_entity_id, geo_code_version_id, calendar_period_id,
         value, raw_value, is_imputed, missing_reason,
         unit, comparison_basis, value_type, status,
         source_id, source_location_id, ingestion_run_id,
         extracted_at, extraction_method, confidence, notes)
    VALUES
        ('{obs_id}',
         '{ind_id}', '{mv_id}',
         v_geo_entity_id, v_geo_cv_id, '{CALENDAR_PERIOD_2024}',
         {v}, '{v}', FALSE, NULL,
         '{unit}', 'YEAR_OVER_YEAR', '{val_type}', 'PUBLISHED',
         v_registry_id, v_loc_id, v_run_id,
         '2026-09-02'::timestamp, 'REGEX_ANCHORED', 1.0,
         '{prov_en} {short_code} {v} {unit};hongheiku 转载;U6 裁定;lineage 三重标注')
    ON CONFLICT (id) DO NOTHING;
""")

        out_lines.append("END $$;\n\n")

    out_lines.append("""
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
""")

    out_path = REPO / 'scripts' / 'seed_m2_u6_batch_26prov.sql'
    out_path.write_text(''.join(out_lines), encoding='utf-8')

    # Verification
    registry_count = out_lines.count('-- 1) source_registry')
    doc_count = out_lines.count('-- 2) source_document')
    loc_count = out_lines.count('-- 3) source_location')
    run_count = out_lines.count('-- 4) ingestion_run')
    obs_real_count = sum(
        1 for line in out_lines
        if line.startswith('    -- observation')
        and '禁补零' not in line
    )
    obs_missing_count = sum(
        1 for line in out_lines
        if line.startswith('    -- observation')
        and '禁补零' in line
    )

    print(f'wrote {out_path}')
    print(f'  source_registry rows:  {registry_count} (expect 23)')
    print(f'  source_document rows:  {doc_count} (expect 23)')
    print(f'  source_location rows:  {loc_count} (expect 23)')
    print(f'  ingestion_run rows:    {run_count} (expect 23)')
    print(f'  observation rows:      {obs_real_count} real + {obs_missing_count} missing (expect 115 + 0)')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
