{{
    config(
        materialized='view',
        tags=['mart', 'city', 'seven_dim_overview', 's27bf_demo']
    )
}}

-- Mart model: mart_city_seven_dim_overview (demo rows)
-- Per docs/47 §3.2 + tasking 293 (S2.7-b-full mart demo-join).
--
-- Purpose: city × 7-dimension overview projection for /cities/{slug}
--          (SevenDimGrid.tsx in CityPageMart).
--          Per docs/42 §2.4 / §2.5, 7 cards: POLICY_DELIVERY / FISCAL_EXECUTION
--          / PROJECT_DELIVERY / ECONOMIC_ADAPTATION / PUBLIC_SERVICES /
--          RISK_MANESSMENT / GOAL_CONSISTENCY.
--
-- Demo-join status (per `293` §SCHEMA + §红线 + docs/47 §3.2):
--   - 10 cities × 7 cards = 70 rows (per docs/46 §2 10 城锁定清单).
--   - is_demo = 'true' (per S1.18 sentinel).
--   - balance_status 5 枚举循环 + 2 余量（per docs/42 §2.5 + frontend 平行模式）
--     [NO_EVIDENCE, NO_CONTRADICTING_EVIDENCE, NO_SUPPORTING_EVIDENCE,
--      SUPPORTS_DOMINANT, CONTRADICTS_DOMINANT, SUPPORTS_DOMINANT, NO_EVIDENCE]
--   - n_supports / n_contradicts / n_inference / n_judgment / n_derived 仅为
--     COUNT aggregates（无 weighting / 无 scoring），与 docs/44 §1.1 S2.7-a 段级
--     gaps 守门一致。
--
-- Red lines (per docs/47 §1.2 + docs/34 §1 + docs/06 §6.6 + docs/42 §8):
--   - No score / rating / rank / total_score / confidence_score / peer_rank.
--   - balance_status ∈ {NO_EVIDENCE, NO_CONTRADICTING_EVIDENCE,
--     NO_SUPPORTING_EVIDENCE, SUPPORTS_DOMINANT, CONTRADICTS_DOMINANT}
--     (5 enum; app-layer guard per docs/42 §2.5).
--
-- Real-data migration path (OPEN, not this knife):
--   - O1 SHA-locked Jiangsu sample (per docs/34 §3 + docs/47 §6.3).
--   - Stage 1 OPEN closure (per docs/34 §3).

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
seven_dim AS (
    -- 7 维度锁定清单（per docs/42 §2.4）
    SELECT * FROM (VALUES
        ('POLICY_DELIVERY',     0),
        ('FISCAL_EXECUTION',    1),
        ('PROJECT_DELIVERY',    2),
        ('ECONOMIC_ADAPTATION', 3),
        ('PUBLIC_SERVICES',     4),
        ('RISK_MANAGEMENT',     5),
        ('GOAL_CONSISTENCY',    6)
    ) AS t(card_id, card_idx)
),
cross_70 AS (
    -- 10 × 7 = 70 demo 行（demo-join；per `293` §SCHEMA）
    SELECT
        c.city_slug,
        c.geo_name_zh,
        c.province_slug,
        d.card_id,
        d.card_idx
    FROM city_seed c
    CROSS JOIN seven_dim d
)
SELECT
    -- city / card keys
    ('00000000-0000-0000-0000-' ||
        LPAD(MD5(c.city_slug)::TEXT, 12, '0')
    )::UUID                                                                  AS city_id,
    c.card_id,                                                                -- 7 enum (POLICY_DELIVERY / ... / GOAL_CONSISTENCY)
    -- counts only — NO weighting, NO scoring (per docs/42 §8 + docs/06 §6.6)
    -- balance_status 5 枚举循环 + 2 余量 = 7 card（per docs/42 §2.5）
    CASE c.card_idx
        WHEN 0 THEN 2   -- NO_EVIDENCE → n_supports=2 (no contradiction either)
        WHEN 1 THEN 2   -- NO_CONTRADICTING_EVIDENCE → n_supports=2
        WHEN 2 THEN 2   -- NO_SUPPORTING_EVIDENCE → n_supports=2 (矛盾多于支持)
        WHEN 3 THEN 4   -- SUPPORTS_DOMINANT → n_supports=4
        WHEN 4 THEN 1   -- CONTRADICTS_DOMINANT → n_supports=1
        WHEN 5 THEN 4   -- SUPPORTS_DOMINANT (2nd) → n_supports=4
        ELSE 2          -- NO_EVIDENCE (2nd) → n_supports=2
    END                                                                      AS n_supports,
    CASE c.card_idx
        WHEN 0 THEN 0   -- NO_EVIDENCE
        WHEN 1 THEN 0   -- NO_CONTRADICTING_EVIDENCE
        WHEN 2 THEN 2   -- NO_SUPPORTING_EVIDENCE → 矛盾 2
        WHEN 3 THEN 0   -- SUPPORTS_DOMINANT
        WHEN 4 THEN 3   -- CONTRADICTS_DOMINANT → 矛盾 3
        WHEN 5 THEN 0   -- SUPPORTS_DOMINANT
        ELSE 0          -- NO_EVIDENCE
    END                                                                      AS n_contradicts,
    1                                                                        AS n_inference,
    0                                                                        AS n_judgment,
    0                                                                        AS n_derived,
    -- 5 enum balance status (app-layer guard; per docs/42 §2.5)
    CASE c.card_idx
        WHEN 0 THEN 'NO_EVIDENCE'
        WHEN 1 THEN 'NO_CONTRADICTING_EVIDENCE'
        WHEN 2 THEN 'NO_SUPPORTING_EVIDENCE'
        WHEN 3 THEN 'SUPPORTS_DOMINANT'
        WHEN 4 THEN 'CONTRADICTS_DOMINANT'
        WHEN 5 THEN 'SUPPORTS_DOMINANT'
        ELSE 'NO_EVIDENCE'
    END                                                                      AS balance_status,    -- 5 enum (NO_EVIDENCE / ... / CONTRADICTS_DOMINANT)
    -- demo sentinel
    'true'                                                                   AS is_demo
FROM cross_70 c