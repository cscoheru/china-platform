{{
    config(
        materialized='view',
        tags=['mart', 'province', 'gdp', '2024', 'real']
    )
}}

-- Mart model: mart_province_gdp_2024
-- Per knife 659 tasking §1.659 (mart flip).
-- Source: observation table 28 provinces with real 2024 GDP data
--   (5 official [BEIJING/SHANGHAI/SHANDONG/HUBEI/SICHUAN] + 23 hongheiku re-posts [658 batch])
--   + 3 provinces with DATA_MISSING status (LN/HAINAN/GUIZHOU = NOT_FOUND_IN_2024_INDEX, 禁补零)
-- lineage_is_demo = 'false' for all real data rows (real sentinel per mart_city_evidence_chain.sql pattern).
--
-- Red lines:
--   - 3 missing provinces: status='DATA_MISSING', missing_reason set, ALL metric columns NULL
--   - No 0 / interpolation / silent default for missing provinces
--   - lineage JSONB triple annotation: source / origin / ruling

WITH province_codes AS (
    SELECT * FROM (VALUES
        ('BEIJING',     '北京',     'Official portal (M2-c)'),
        ('SHANGHAI',    '上海',     'Official portal (M2-d)'),
        ('SHANDONG',    '山东',     'Official portal (M2-e)'),
        ('HUBEI',       '湖北',     'Official portal (M2-e)'),
        ('SICHUAN',     '四川',     'Official portal (M2-e)'),
        ('TIANJIN',     '天津',     'hongheiku re-post (U6 2026-09-02)'),
        ('CHONGQING',   '重庆',     'hongheiku re-post (U6 2026-09-02)'),
        ('HEBEI',       '河北',     'hongheiku re-post (U6 2026-09-02)'),
        ('SHANXI',      '山西',     'hongheiku re-post (U6 2026-09-02)'),
        ('NEI_MENGGU',  '内蒙古',   'hongheiku re-post (U6 2026-09-02)'),
        ('JILIN',       '吉林',     'hongheiku re-post (U6 2026-09-02)'),
        ('HEILONGJIANG','黑龙江',   'hongheiku re-post (U6 2026-09-02)'),
        ('JIANGSU',     '江苏',     'hongheiku re-post (U6 2026-09-02)'),
        ('ZHEJIANG',    '浙江',     'hongheiku re-post (U6 2026-09-02)'),
        ('ANHUI',       '安徽',     'hongheiku re-post (U6 2026-09-02)'),
        ('FUJIAN',      '福建',     'hongheiku re-post (U6 2026-09-02)'),
        ('JIANGXI',     '江西',     'hongheiku re-post (U6 2026-09-02)'),
        ('HENAN',       '河南',     'hongheiku re-post (U6 2026-09-02)'),
        ('HUNAN',       '湖南',     'hongheiku re-post (U6 2026-09-02)'),
        ('GUANGDONG',   '广东',     'hongheiku re-post (U6 2026-09-02)'),
        ('GUANGXI',     '广西',     'hongheiku re-post (U6 2026-09-02)'),
        ('YUNNAN',      '云南',     'hongheiku re-post (U6 2026-09-02)'),
        ('XIZANG',      '西藏',     'hongheiku re-post (U6 2026-09-02)'),
        ('SHAANXI',     '陕西',     'hongheiku re-post (U6 2026-09-02)'),
        ('GANSU',       '甘肃',     'hongheiku re-post (U6 2026-09-02)'),
        ('QINGHAI',     '青海',     'hongheiku re-post (U6 2026-09-02)'),
        ('NINGXIA',     '宁夏',     'hongheiku re-post (U6 2026-09-02)'),
        ('XINJIANG',    '新疆',     'hongheiku re-post (U6 2026-09-02)'),
        ('LIAONING',    '辽宁',     'hongheiku re-post (U6 2026-09-02)'),
        ('HAINAN',      '海南',     'hongheiku re-post (U6 2026-09-02)'),
        ('GUIZHOU',     '贵州',     'hongheiku re-post (U6 2026-09-02)')
    ) AS t(province_code, province_name, source)
),
real_data AS (
    SELECT * FROM (VALUES
        ('BEIJING',     '北京',     49843.1,  NULL,       101.6,   4806.3,  19046.7,  25790.2,  'OFFICIAL_INTAKED',  'beijing_tjj',   '北京市统计局'),
        ('SHANGHAI',    '上海',     53926.71, NULL,       115.56,  9590.5,  19034.93, 34721.66, 'OFFICIAL_INTAKED',  'shanghai_tjj',  '上海市统计局'),
        ('SHANDONG',    '山东',     98565.8,  NULL,       5120.2,  39677.2, 53768.4,  NULL,     'OFFICIAL_INTAKED',  'shandong_tjj',  '山东省统计局'),
        ('HUBEI',       '湖北',     60012.97, NULL,       5082.9,  21300.0, 33630.07, NULL,     'OFFICIAL_INTAKED',  'hubei_tjj',     '湖北省统计局'),
        ('SICHUAN',     '四川',     64697.0,  NULL,       6560.0,  20957.0, 37180.0,  NULL,     'OFFICIAL_INTAKED',  'sichuan_tjj',   '四川省统计局'),
        ('TIANJIN',     '天津',     18024.32, 5.1,       284.28,  6214.27, 11525.77, NULL,     'hongheiku_tjgb',   'tjgb.hongheiku', '天津市统计局'),
        ('CHONGQING',   '重庆',     32193.15, 5.7,       2135.82, 11690.68, 18366.65, NULL,     'hongheiku_tjgb',   'tjgb.hongheiku', '重庆市统计局'),
        ('HEBEI',       '河北',     47526.9,  5.4,       4522.3,  17470.5, 25534.1,  NULL,     'hongheiku_tjgb',   'tjgb.hongheiku', '河北省统计局'),
        ('SHANXI',      '山西',     25494.69, 2.3,       1392.48, 11021.46, 13080.74, NULL,     'hongheiku_tjgb',   'tjgb.hongheiku', '山西省统计局'),
        ('NEI_MENGGU',  '内蒙古',   26314.6,  5.8,       2872.6,  11604.4, 11837.6,  NULL,     'hongheiku_tjgb',   'tjgb.hongheiku', '内蒙古自治区统计局'),
        ('JILIN',       '吉林',     14361.22, 4.3,       1589.8,  4577.64, 8193.79,  NULL,     'hongheiku_tjgb',   'tjgb.hongheiku', '吉林省统计局'),
        ('HEILONGJIANG','黑龙江',   16476.9,  3.2,       3203.3,  4147.3,  9126.2,   NULL,     'hongheiku_tjgb',   'tjgb.hongheiku', '黑龙江省统计局'),
        ('JIANGSU',     '江苏',     137008.0, 5.8,       5245.2,  59180.1, 72582.8,  NULL,     'hongheiku_tjgb',   'tjgb.hongheiku', '江苏省统计局'),
        ('ZHEJIANG',    '浙江',     90131.0,  5.5,       2586.0,  34783.0, 52762.0,  NULL,     'hongheiku_tjgb',   'tjgb.hongheiku', '浙江省统计局'),
        ('ANHUI',       '安徽',     50625.0,  5.8,       3566.0,  19607.0, 27452.0,  NULL,     'hongheiku_tjgb',   'tjgb.hongheiku', '安徽省统计局'),
        ('FUJIAN',      '福建',     57761.02, 5.5,       3287.67, 24713.16, 29760.19, NULL,     'hongheiku_tjgb',   'tjgb.hongheiku', '福建省统计局'),
        ('JIANGXI',     '江西',     34202.5,  5.1,       2605.1,  13688.6, 17908.8,  NULL,     'hongheiku_tjgb',   'tjgb.hongheiku', '江西省统计局'),
        ('HENAN',       '河南',     63589.99, 5.1,       5491.4,  24346.17, 33752.42, NULL,     'hongheiku_tjgb',   'tjgb.hongheiku', '河南省统计局'),
        ('HUNAN',       '湖南',     53231.0,  4.8,       4899.7,  19534.6, 28796.7,  NULL,     'hongheiku_tjgb',   'tjgb.hongheiku', '湖南省统计局'),
        ('GUANGDONG',   '广东',     141633.81, 3.5,      5837.03, 54365.47, 81431.31, NULL,     'hongheiku_tjgb',   'tjgb.hongheiku', '广东省统计局'),
        ('GUANGXI',     '广西',     28649.4,  4.2,       4751.54, 9300.99, 14596.87, NULL,     'hongheiku_tjgb',   'tjgb.hongheiku', '广西壮族自治区统计局'),
        ('YUNNAN',      '云南',     31534.1,  3.3,       4193.0,  10330.0, 17011.0,  NULL,     'hongheiku_tjgb',   'tjgb.hongheiku', '云南省统计局'),
        ('XIZANG',      '西藏',     2764.94,  6.3,       247.52,  1016.07, 1501.35,  NULL,     'hongheiku_tjgb',   'tjgb.hongheiku', '西藏自治区统计局'),
        ('SHAANXI',     '陕西',     35538.77, 5.3,       2621.96, 14518.97, 18397.84, NULL,     'hongheiku_tjgb',   'tjgb.hongheiku', '陕西省统计局'),
        ('GANSU',       '甘肃',     13002.9,  5.8,       1621.7,  4436.4,  6944.8,   NULL,     'hongheiku_tjgb',   'tjgb.hongheiku', '甘肃省统计局'),
        ('QINGHAI',     '青海',     3950.79,  2.7,       359.07,  1662.39, 1929.33,  NULL,     'hongheiku_tjgb',   'tjgb.hongheiku', '青海省统计局'),
        ('NINGXIA',     '宁夏',     5502.76,  5.4,       451.24,  2335.36, 2716.16,  NULL,     'hongheiku_tjgb',   'tjgb.hongheiku', '宁夏回族自治区统计局'),
        ('XINJIANG',    '新疆',     20534.08, 6.1,       2571.98, 8135.87, 9826.23,  NULL,     'hongheiku_tjgb',   'tjgb.hongheiku', '新疆维吾尔自治区统计局')
    ) AS t(province_code, province_name, gdp_total, gdp_growth,
           primary, secondary, tertiary, growth_note,
           source, source_domain, origin)
),
missing_provinces AS (
    SELECT * FROM (VALUES
        ('LIAONING',    '辽宁',     'DATA_MISSING', 'hongheiku 2024 索引缺文 NOT_FOUND_IN_2024_INDEX', 'hongheiku_tjgb'),
        ('HAINAN',      '海南',     'DATA_MISSING', 'hongheiku 2024 索引缺文 NOT_FOUND_IN_2024_INDEX', 'hongheiku_tjgb'),
        ('GUIZHOU',     '贵州',     'DATA_MISSING', 'hongheiku 2024 索引缺文 NOT_FOUND_IN_2024_INDEX', 'hongheiku_tjgb')
    ) AS t(province_code, province_name, status, missing_reason, lineage_source)
)
SELECT
    -- Identity
    pc.province_code,
    pc.province_name,
    -- Real data rows
    CASE WHEN rd.province_code IS NOT NULL THEN rd.gdp_total   ELSE NULL END AS gdp_total,
    CASE WHEN rd.province_code IS NOT NULL THEN rd.gdp_growth  ELSE NULL END AS gdp_growth,
    CASE WHEN rd.province_code IS NOT NULL THEN rd.primary      ELSE NULL END AS primary_gdp,
    CASE WHEN rd.province_code IS NOT NULL THEN rd.secondary    ELSE NULL END AS secondary_gdp,
    CASE WHEN rd.province_code IS NOT NULL THEN rd.tertiary     ELSE NULL END AS tertiary_gdp,
    -- Missing province rows (指标列 NULL per 红线 659)
    CASE WHEN mp.province_code IS NOT NULL THEN mp.status         ELSE NULL END AS status,
    CASE WHEN mp.province_code IS NOT NULL THEN mp.missing_reason ELSE NULL END AS missing_reason,
    -- Source metadata
    COALESCE(rd.source,    mp.lineage_source) AS lineage_source,
    COALESCE(rd.origin,    'hongheiku_tjgb') AS lineage_origin,
    'U6 2026-09-02'                            AS lineage_ruling,
    -- is_demo sentinel (real data = false; consistent with mart_city_evidence_chain.sql pattern)
    'false'                                    AS lineage_is_demo
FROM province_codes pc
LEFT JOIN real_data        rd ON rd.province_code = pc.province_code
LEFT JOIN missing_provinces mp ON mp.province_code = pc.province_code
ORDER BY
    CASE pc.province_code
        WHEN 'BEIJING'       THEN  1
        WHEN 'SHANGHAI'     THEN  2
        WHEN 'TIANJIN'      THEN  3
        WHEN 'CHONGQING'    THEN  4
        WHEN 'HEBEI'        THEN  5
        WHEN 'SHANXI'       THEN  6
        WHEN 'NEI_MENGGU'   THEN  7
        WHEN 'LIAONING'     THEN  8
        WHEN 'JILIN'        THEN  9
        WHEN 'HEILONGJIANG' THEN 10
        WHEN 'SHANDONG'     THEN 11
        WHEN 'JIANGSU'      THEN 12
        WHEN 'ANHUI'        THEN 13
        WHEN 'ZHEJIANG'     THEN 14
        WHEN 'FUJIAN'       THEN 15
        WHEN 'JIANGXI'      THEN 16
        WHEN 'HENAN'        THEN 17
        WHEN 'HUBEI'        THEN 18
        WHEN 'HUNAN'        THEN 19
        WHEN 'GUANGDONG'    THEN 20
        WHEN 'GUANGXI'      THEN 21
        WHEN 'HAINAN'       THEN 22
        WHEN 'YUNNAN'      THEN 23
        WHEN 'GUIZHOU'      THEN 24
        WHEN 'SHAANXI'      THEN 25
        WHEN 'GANSU'        THEN 26
        WHEN 'QINGHAI'      THEN 27
        WHEN 'NINGXIA'      THEN 28
        WHEN 'XIZANG'       THEN 29
        WHEN 'XINJIANG'     THEN 30
        WHEN 'SICHUAN'      THEN 31
    END
