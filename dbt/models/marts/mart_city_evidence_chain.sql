{{
    config(
        materialized='view',
        tags=['mart', 'city', 'evidence_chain', 's27bf_demo']
    )
}}

-- Mart model: mart_city_evidence_chain (demo rows)
-- Per docs/47 §3.1 + tasking 293 (S2.7-b-full mart demo-join).
--
-- Purpose: city-scoped 6-segment evidence chain view for /cities/{slug}
--          (CONDITION / COMMITMENT / INPUT / PROCESS / OUTPUT / OUTCOME_RISK).
--          Used by EvidenceChain.tsx in CityPageMart.
--
-- Demo-join status (per `293` §SCHEMA + §红线 + docs/47 §3.1):
--   - 10 cities × 6 segments = 60 rows (per docs/46 §2 10 城锁定清单).
--   - lineage.is_demo = 'true' (per S1.18 sentinel).
--   - lineage.source_file_sha256 = REPEAT('0', 64)::TEXT 占位
--     (per docs/47 §3.1 ⚠️ OPEN；O1 真实 SHA 收口前恒占位).
--   - canonical_statement 仅 CONDITION 段非空演示占位
--     （其余 5 段空演示"未覆盖"，与 docs/44 §1.1 S2.7-a 段级 gaps 守门一致）.
--
-- Red lines (per docs/47 §1.2 + docs/34 §1 + docs/06 §6.6 + docs/42 §8):
--   - No fake SHA — lineage.source_file_sha256 is always '0'*64 placeholder.
--   - No score / rating / rank / total_score / confidence_score columns.
--   - No real person/tenure JOIN data (related_persons filled by S2.7-b-full
--     landing knife after S2.1-lite mart_person_tenure PASS).
--
-- Real-data migration path (OPEN, not this knife):
--   - O1 SHA-locked Jiangsu sample (per docs/34 §3 + docs/47 §6.3).
--   - Stage 1 OPEN closure (per docs/34 §3).
--   - S2.1-lite mart_person_tenure PASS (per docs/47 §3.3).

WITH city_seed AS (
    -- 10 城锁定清单（per docs/46 §2 江苏 4 + 浙江 3 + 广东 3）
    SELECT * FROM (VALUES
        ('nanjing',   '南京市', 'jiangsu'),
        ('suzhou',    '苏州市', 'jiangsu'),
        ('wuxi',      '无锡市', 'jiangsu'),
        ('nantong',   '南通市', 'jiangsu'),
        ('hangzhou',  '杭州市', 'zhejiang'),
        ('ningbo',    '宁波市', 'zhejiang'),
        ('wenzhou',   '温州市', 'zhejiang'),
        ('guangzhou', '广州市', 'guangdong'),
        ('shenzhen',  '深圳市', 'guangdong'),
        ('dongguan',  '东莞市', 'guangdong')
    ) AS t(city_slug, geo_name_zh, province_slug)
),
segments AS (
    -- 6 段锁定清单（per docs/06 §2 evidence chain）
    SELECT * FROM (VALUES
        ('CONDITION'),
        ('COMMITMENT'),
        ('INPUT'),
        ('PROCESS'),
        ('OUTPUT'),
        ('OUTCOME_RISK')
    ) AS t(segment)
),
cross_60 AS (
    -- 10 × 6 = 60 demo 行（demo-join；per `293` §SCHEMA）
    SELECT
        c.city_slug,
        c.geo_name_zh,
        c.province_slug,
        s.segment
    FROM city_seed c
    CROSS JOIN segments s
)
SELECT
    -- city / geography
    ('00000000-0000-0000-0000-' ||
        LPAD(MD5(c.city_slug)::TEXT, 12, '0')
    )::UUID                                                                  AS city_id,
    c.geo_name_zh,
    c.province_slug,
    -- evidence segment (6 fixed segments; enum-style guard at app layer)
    c.segment,
    -- canonical statement / polarity / strength
    -- 仅 CONDITION 段非空演示占位；其余 5 段空演示"未覆盖"
    CASE
        WHEN c.segment = 'CONDITION' THEN
            c.geo_name_zh || ' 区位与产业基础（mart-shape 演示占位；S2.7-b-full 接 inference_record.canonical_statement）'
        ELSE ''
    END                                                                      AS canonical_statement,
    CASE
        WHEN c.segment = 'CONDITION' THEN 'SUPPORTS'
        ELSE 'NEUTRAL'
    END                                                                      AS canonical_polarity,  -- SUPPORTS / CONTRADICTS / NEUTRAL
    CASE
        WHEN c.segment = 'CONDITION' THEN 'MODERATE'
        ELSE 'WEAK'
    END                                                                      AS evidence_strength,   -- STRONG / MODERATE / WEAK
    -- info layer (4 enum; per docs/40 §2.3 app-layer guard)
    CASE
        WHEN c.segment = 'CONDITION' THEN 'DERIVED'
        ELSE 'FACT'
    END                                                                      AS info_layer,          -- FACT / DERIVED / INFERENCE / JUDGMENT
    -- lineage — ALWAYS placeholder until O1 SHA closes (per docs/47 §3.1 ⚠️ OPEN)
    'true'                                                                   AS lineage_is_demo,     -- 'true' / 'false'
    REPEAT('0', 64)::TEXT                                                    AS lineage_source_file_sha256  -- ⚠️ placeholder
FROM cross_60 c