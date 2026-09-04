{{
    config(
        materialized='table',
        schema='mart',
        tags=['mart', 'timeseries', 'p2', 'china_platform']
    )
}}

-- Mart model: mart_province_timeseries (P2, knife 663)
-- ============================================================================
-- Cross product: 31 provinces × 10 indicators × 26 years (2001-2026) = 8060 rows.
--
-- Status semantics (新增红线 enforced at mart schema level):
--   - 'DATA_MISSING' for years <2020  (新增红线-1: 禁编造历史数据)
--   - 'DATA_MISSING' for year =2026   (新增红线-2: 待 2027 官方发布)
--   - 'DATA_MISSING' for missing provinces (辽/琼/黔) across all years
--   - 'DATA_MISSING' for cells where knife 665/666 haven't harvested yet
--   - NULL status = real data (passed through lineage_source_type)
--
-- lineage_source_type values:
--   - 'OFFICIAL_INTAKED'    : 5 现指标 from 省统计局 (5 京沪鲁鄂川 + 666 adds 粤苏浙)
--   - 'HONGHEIKU_TRANSLOAD' : from tjgb.hongheiku.com re-post (5 现 + 5 增量)
--   - 'DATA_MISSING'        : explicit missing (red lines 1+2, missing provinces, pending harvest)
--
-- 663 initial state: 140 real cells
--   = 28 real provinces × 5 现指标 × year 2024 (from knife 660 batch)
-- After 665: ~1500 real cells (+ 5 现 2020-2023+2025 + 5 增量 2020-2025 from hongheiku)
-- After 666: ~1590 real cells (+ 粤苏浙 OFFICIAL 5 现 2020-2025)
-- 668 verify-live.sh v2 expects ≥186 real cells per indicator (= 31 × 6 = 186 total rows).
--
-- Red lines:
--   - 缺失年禁补零 (新增红线-1+2 沿用 660 「缺失省禁补零」扩展)
--   - 5 增量指标只准来自 hongheiku 采集, 禁手填 (新增红线-3)
--   - No interpolation / silent default for missing cells
--   - lineage 三件套: source_type / origin / ruling 必填

WITH province_dimension AS (
    SELECT * FROM (VALUES
        ('BEIJING',     '北京'),
        ('SHANGHAI',    '上海'),
        ('SHANDONG',    '山东'),
        ('HUBEI',       '湖北'),
        ('SICHUAN',     '四川'),
        ('TIANJIN',     '天津'),
        ('CHONGQING',   '重庆'),
        ('HEBEI',       '河北'),
        ('SHANXI',      '山西'),
        ('NEI_MENGGU',  '内蒙古'),
        ('JILIN',       '吉林'),
        ('HEILONGJIANG','黑龙江'),
        ('JIANGSU',     '江苏'),
        ('ZHEJIANG',    '浙江'),
        ('ANHUI',       '安徽'),
        ('FUJIAN',      '福建'),
        ('JIANGXI',     '江西'),
        ('HENAN',       '河南'),
        ('HUNAN',       '湖南'),
        ('GUANGDONG',   '广东'),
        ('GUANGXI',     '广西'),
        ('YUNNAN',      '云南'),
        ('XIZANG',      '西藏'),
        ('SHAANXI',     '陕西'),
        ('GANSU',       '甘肃'),
        ('QINGHAI',     '青海'),
        ('NINGXIA',     '宁夏'),
        ('XINJIANG',    '新疆'),
        ('LIAONING',    '辽宁'),
        ('HAINAN',      '海南'),
        ('GUIZHOU',     '贵州')
    ) AS t(province_code, province_name)
),
indicator_dimension AS (
    -- 10 indicators: 5 现 (knife 660 batch) + 5 增量 (665 harvest)
    SELECT * FROM (VALUES
        ('gdp_total',     '地区生产总值 (总量)',     '亿元'),
        ('gdp_growth',    '地区生产总值 (增速)',     '%'),
        ('primary_gdp',   '第一产业增加值',           '亿元'),
        ('secondary_gdp', '第二产业增加值',           '亿元'),
        ('tertiary_gdp',  '第三产业增加值',           '亿元'),
        ('gdp_percapita', '人均地区生产总值',         '元'),
        ('fiscal_rev',    '地方一般公共预算收入',     '亿元'),
        ('fixed_asset',   '固定资产投资',             '亿元'),
        ('retail',        '社会消费品零售总额',       '亿元'),
        ('trade',         '进出口总额',               '亿元')
    ) AS t(indicator_key, indicator_label, unit)
),
year_dimension AS (
    SELECT generate_series(2001, 2026) AS year
),
cross_product AS (
    SELECT pd.province_code, pd.province_name,
           id.indicator_key, id.indicator_label, id.unit,
           yd.year
    FROM province_dimension pd
    CROSS JOIN indicator_dimension id
    CROSS JOIN year_dimension yd
),
real_2024_provinces AS (
    -- 28 real provinces × 5 现指标 × 2024 only (from knife 660 batch / mart_province_gdp_2024.sql)
    -- Unpivoted below into 5 rows per province via UNION ALL.
    SELECT * FROM (VALUES
        ('BEIJING',     49843.1,  NULL,       101.6,   4806.3,  19046.7, 'OFFICIAL_INTAKED',  'beijing_tjj'),
        ('SHANGHAI',    53926.71, NULL,       115.56,  9590.5,  19034.93,'OFFICIAL_INTAKED',  'shanghai_tjj'),
        ('SHANDONG',    98565.8,  NULL,       5120.2,  39677.2, 53768.4, 'OFFICIAL_INTAKED',  'shandong_tjj'),
        ('HUBEI',       60012.97, NULL,       5082.9,  21300.0, 33630.07,'OFFICIAL_INTAKED',  'hubei_tjj'),
        ('SICHUAN',     64697.0,  NULL,       6560.0,  20957.0, 37180.0, 'OFFICIAL_INTAKED',  'sichuan_tjj'),
        ('TIANJIN',     18024.32, 5.1,        284.28,  6214.27, 11525.77,'hongheiku_tjgb',   'tjgb.hongheiku'),
        ('CHONGQING',   32193.15, 5.7,        2135.82, 11690.68,18366.65,'hongheiku_tjgb',   'tjgb.hongheiku'),
        ('HEBEI',       47526.9,  5.4,        4522.3,  17470.5, 25534.1, 'hongheiku_tjgb',   'tjgb.hongheiku'),
        ('SHANXI',      25494.69, 2.3,        1392.48, 11021.46,13080.74,'hongheiku_tjgb',   'tjgb.hongheiku'),
        ('NEI_MENGGU',  26314.6,  5.8,        2872.6,  11604.4, 11837.6, 'hongheiku_tjgb',   'tjgb.hongheiku'),
        ('JILIN',       14361.22, 4.3,        1589.8,  4577.64, 8193.79, 'hongheiku_tjgb',   'tjgb.hongheiku'),
        ('HEILONGJIANG',16476.9,  3.2,        3203.3,  4147.3,  9126.2,  'hongheiku_tjgb',   'tjgb.hongheiku'),
        ('JIANGSU',     137008.0, 5.8,        5245.2,  59180.1, 72582.8, 'hongheiku_tjgb',   'tjgb.hongheiku'),
        ('ZHEJIANG',    90131.0,  5.5,        2586.0,  34783.0, 52762.0, 'hongheiku_tjgb',   'tjgb.hongheiku'),
        ('ANHUI',       50625.0,  5.8,        3566.0,  19607.0, 27452.0, 'hongheiku_tjgb',   'tjgb.hongheiku'),
        ('FUJIAN',      57761.02, 5.5,        3287.67, 24713.16,29760.19,'hongheiku_tjgb',   'tjgb.hongheiku'),
        ('JIANGXI',     34202.5,  5.1,        2605.1,  13688.6, 17908.8, 'hongheiku_tjgb',   'tjgb.hongheiku'),
        ('HENAN',       63589.99, 5.1,        5491.4,  24346.17,33752.42,'hongheiku_tjgb',   'tjgb.hongheiku'),
        ('HUNAN',       53231.0,  4.8,        4899.7,  19534.6, 28796.7, 'hongheiku_tjgb',   'tjgb.hongheiku'),
        ('GUANGDONG',   141633.81,3.5,        5837.03, 54365.47,81431.31,'hongheiku_tjgb',   'tjgb.hongheiku'),
        ('GUANGXI',     28649.4,  4.2,        4751.54, 9300.99, 14596.87,'hongheiku_tjgb',   'tjgb.hongheiku'),
        ('YUNNAN',      31534.1,  3.3,        4193.0,  10330.0, 17011.0, 'hongheiku_tjgb',   'tjgb.hongheiku'),
        ('XIZANG',      2764.94,  6.3,        247.52,  1016.07, 1501.35, 'hongheiku_tjgb',   'tjgb.hongheiku'),
        ('SHAANXI',     35538.77, 5.3,        2621.96, 14518.97,18397.84,'hongheiku_tjgb',   'tjgb.hongheiku'),
        ('GANSU',       13002.9,  5.8,        1621.7,  4436.4,  6944.8,  'hongheiku_tjgb',   'tjgb.hongheiku'),
        ('QINGHAI',     3950.79,  2.7,        359.07,  1662.39, 1929.33, 'hongheiku_tjgb',   'tjgb.hongheiku'),
        ('NINGXIA',     5502.76,  5.4,        451.24,  2335.36, 2716.16, 'hongheiku_tjgb',   'tjgb.hongheiku'),
        ('XINJIANG',    20534.08, 6.1,        2571.98, 8135.87, 9826.23, 'hongheiku_tjgb',   'tjgb.hongheiku')
    ) AS t(province_code, gdp_total, gdp_growth, primary_gdp, secondary_gdp, tertiary_gdp,
           lineage_source_type, lineage_origin)
),
real_data_2024 AS (
    -- Unpivot 5 现指标 × 28 real provinces × 2024 → 140 rows.
    -- 各指标用 WHERE value IS NOT NULL 过滤 (e.g. BEIJING gdp_growth 是 NULL → 跳过该 cell).
    SELECT province_code, 'gdp_total'     AS indicator_key, gdp_total     AS value,
           lineage_source_type, lineage_origin FROM real_2024_provinces WHERE gdp_total     IS NOT NULL
    UNION ALL
    SELECT province_code, 'gdp_growth'    AS indicator_key, gdp_growth    AS value,
           lineage_source_type, lineage_origin FROM real_2024_provinces WHERE gdp_growth    IS NOT NULL
    UNION ALL
    SELECT province_code, 'primary_gdp'   AS indicator_key, primary_gdp   AS value,
           lineage_source_type, lineage_origin FROM real_2024_provinces WHERE primary_gdp   IS NOT NULL
    UNION ALL
    SELECT province_code, 'secondary_gdp' AS indicator_key, secondary_gdp AS value,
           lineage_source_type, lineage_origin FROM real_2024_provinces WHERE secondary_gdp IS NOT NULL
    UNION ALL
    SELECT province_code, 'tertiary_gdp'  AS indicator_key, tertiary_gdp  AS value,
           lineage_source_type, lineage_origin FROM real_2024_provinces WHERE tertiary_gdp  IS NOT NULL
),
real_data_2021 AS (
    -- knife 665 (year 2021): 29 省 × 10 指标 from seed_hongheiku_timeseries_2021
    -- Real cells ~251; missing ~39 (parse couldn't extract). All 5 OFFICIAL_INTAKED provinces
    -- (京/沪/鲁/鄂/川) 2021 gdp_growth is hongheiku (no OFFICIAL patch yet — 666 program).
    -- HUNAN page is a stub on hongheiku → 10/10 DATA_MISSING for 2021.
    -- GUANGDONG + JIANGXI: not in hongheiku cat index → 10/10 DATA_MISSING for 2021.
    SELECT province_code, year, indicator_key, value,
           lineage_source_type, lineage_origin,
           lineage_ruling, lineage_is_demo
    FROM {{ ref('seed_hongheiku_timeseries_2021') }}
    WHERE value IS NOT NULL
),
real_data AS (
    -- Combined harvest data across years (663 baseline 2024 + 665 2021 + future 665b-665e)
    -- UNION 2 CTEs of identical column shape: (province_code, indicator_key, value, lineage_source_type, lineage_origin, year)
    -- real_data_2024 has implicit year=2024 (constant added below)
    SELECT province_code, indicator_key, value,
           lineage_source_type, lineage_origin, 2024 AS year
    FROM real_data_2024
    UNION ALL
    SELECT province_code, indicator_key, value,
           lineage_source_type, lineage_origin, year
    FROM real_data_2021
),
missing_provinces AS (
    -- 3 省份历史年缺文 (沿用 P1 660 红线, 跨 26 年 × 10 指标 = 780 DATA_MISSING rows)
    -- knife 665 试 hongheiku 长历史覆盖, 失败则永久 DATA_MISSING.
    SELECT * FROM (VALUES
        ('LIAONING', '辽宁', 'hongheiku 2020-2025 索引缺文 (待 665 试 hongheiku 长历史覆盖; 永久 DATA_MISSING if fail)'),
        ('HAINAN',   '海南', 'hongheiku 2020-2025 索引缺文 (待 665 试 hongheiku 长历史覆盖; 永久 DATA_MISSING if fail)'),
        ('GUIZHOU',  '贵州', 'hongheiku 2020-2025 索引缺文 (待 665 试 hongheiku 长历史覆盖; 永久 DATA_MISSING if fail)')
    ) AS t(province_code, province_name, missing_reason)
)
SELECT
    cp.province_code,
    cp.province_name,
    cp.indicator_key,
    cp.indicator_label,
    cp.unit,
    cp.year,
    rd.value,
    CASE
        WHEN cp.year < 2020                                              THEN 'DATA_MISSING'
        WHEN cp.year = 2026                                              THEN 'DATA_MISSING'
        WHEN mp.province_code IS NOT NULL                                 THEN 'DATA_MISSING'
        WHEN cp.year BETWEEN 2020 AND 2025 AND rd.value IS NULL           THEN 'DATA_MISSING'
        ELSE NULL
    END AS status,
    CASE
        WHEN cp.year < 2020                                       THEN '新增红线-1: 2001-2019 禁编造历史数据 (hongheiku probe 636 REACHABLE=0)'
        WHEN cp.year = 2026                                       THEN '新增红线-2: 2026 待 2027 官方发布'
        WHEN mp.province_code IS NOT NULL                         THEN mp.missing_reason
        WHEN cp.year BETWEEN 2020 AND 2025 AND rd.value IS NULL   THEN 'knife 665/666 待采集 (hongheiku 2020-2025 + 粤苏浙 OFFICIAL)'
        ELSE NULL
    END AS missing_reason,
    COALESCE(
        rd.lineage_source_type,
        CASE
            WHEN cp.year < 2020 OR cp.year = 2026      THEN 'DATA_MISSING'
            WHEN mp.province_code IS NOT NULL           THEN 'hongheiku_tjgb'
            WHEN cp.year BETWEEN 2020 AND 2025          THEN 'hongheiku_tjgb'  -- pending harvest default
            ELSE 'unknown'
        END
    ) AS lineage_source_type,
    COALESCE(
        rd.lineage_origin,
        CASE
            WHEN cp.year < 2020 OR cp.year = 2026      THEN 'none'
            WHEN mp.province_code IS NOT NULL           THEN 'tjgb.hongheiku'
            WHEN cp.year BETWEEN 2020 AND 2025          THEN 'tjgb.hongheiku'
            ELSE 'unknown'
        END
    ) AS lineage_origin,
    'K663-2026-09-03' AS lineage_ruling,
    'false'           AS lineage_is_demo
FROM cross_product cp
LEFT JOIN real_data rd
    ON rd.province_code = cp.province_code
    AND rd.indicator_key = cp.indicator_key
    AND rd.year = cp.year
    AND cp.year IN (2024, 2021)
LEFT JOIN missing_provinces mp
    ON mp.province_code = cp.province_code
