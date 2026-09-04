-- Mart model: mart_city_timeseries (P2 / knife 669a-2020 / 669a-2021)
-- ============================================================================
-- Cross product: 4 cities × 10 indicators × 7 years (2020-2026) = 280 rows.
--
-- Per 新增红线-7 (docs/87 §3.2 P2 数据扩展): mart schema 保持 province/city 分离
-- (不合并), 4 直辖市 (北京/上海/天津/重庆) 禁在 city 维度重复 (已在 province mart)。
--
-- Per 新增红线-3 (docs/05 §8 禁手填): city 数据只准来自 hongheiku 城市维度
-- 采集; 缺失年/缺失 city 禁补零。
--
-- 669a-2020 (zero-harvest knife, DELIVERED):
--   - 实证: hongheiku 城市 cat index 仅 2021-2025, 2020 缺文
--   - 所有 40 cells (4 city × 10 indicator × 2020) = DATA_MISSING
--   - lineage_ruling = 'K669a-2020-2026-09-04'
--
-- 669a-2021 (real-data harvest knife, current):
--   - 4 city × 10 indicator × 2021 = 40 cells (26 real + 14 DATA_MISSING)
--   - 26 real: gdp_total/gdp_growth/三产/gdp_percapita/fiscal_rev/retail/trade 等 (per city)
--   - 14 DATA_MISSING: 公报非典型结构 (广州) + fixed_asset 普遍缺 (2021 城市公报少列)
--   - 守新增红线-3: regex miss → DATA_MISSING, 禁手填/禁编造
--   - lineage_ruling = 'K669a-2021-2026-09-04'
--   - HTTP budget: 8 (1 shenzhen tag + 3 other tags + 4 city 2021 bulletins)
--
-- 669a 后续 sub-knives (3 把: 2022/2023/2024/2025):
--   - 每刀 ADD 4 city × 10 indicator × 1 year (real data from hongheiku 城市 cat)
--   - mart rerun 累积到 280 rows by 669a-2025 (4 × 10 × 7)
--
-- 后续 669b-j 批次:
--   - 8 batches × 6 years × ~32 city = 48 sub-knives (max 32 HTTP per sub-knife)
--   - 每 sub-knife 独立 user_ruling (per docs/87 §6)
--
-- lineage_source_type values:
--   - 'OFFICIAL_INTAKED'    : from city 统计局 (未启用; 669 program 沿用 hongheiku 转载)
--   - 'HONGHEIKU_TRANSLOAD' : from tjgb.hongheiku.com 城市 cat (per-city year URL)
--   - 'DATA_MISSING'        : explicit missing (per 新增红线-1/2/3, hongheiku 缺文)
--
-- Status semantics (新增红线 enforced at mart schema level):
--   - 'DATA_MISSING' for year < 2020   (新增红线-1: 禁编造历史数据)
--   - 'DATA_MISSING' for year = 2026   (新增红线-2: 待 2027 官方发布)
--   - 'DATA_MISSING' for city × year not yet harvested (per-knife 提交)
--   - NULL status = real data (passed through lineage_source_type)
--
-- Red lines (669a-2021 enforced):
--   - 4 直辖市禁在 city 维度重复 (新增红线-7; 已在 mart_province_timeseries)
--   - 城市数据禁手填 (新增红线-3; hongheiku 缺文 → DATA_MISSING)
--   - city_code 命名: {PROVINCE_CODE}_{CITY_SLUG} (大写英文 + 下划线)
--   - 2020 全 DATA_MISSING (实证 hongheiku 城市 cat index 仅 2021-2025)

WITH city_dimension AS (
    -- 669a 批次: 4 优先 city (深/穗/杭/宁)
    -- city_code 命名规范: {PROVINCE_CODE}_{CITY_SLUG} (大写英文)
    SELECT * FROM (VALUES
        ('GUANGDONG_SHENZHEN',  '深圳市', 'GUANGDONG'),
        ('GUANGDONG_GUANGZHOU', '广州市', 'GUANGDONG'),
        ('ZHEJIANG_HANGZHOU',   '杭州市', 'ZHEJIANG'),
        ('JIANGSU_NANJING',     '南京市', 'JIANGSU')
    ) AS t(city_code, city_name, province_code)
),
indicator_dimension AS (
    -- 10 indicators (mirror mart_province_timeseries indicator_dimension)
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
    -- 城市维度 year 窗口: 2020-2026 (7 年)
    -- 实证: hongheiku 城市 cat index 仅 2021-2025 (5 年), 2020 缺文
    -- (year index 实证: 2025=68085 / 2024=57063 / 2023=45926 / 2022=35003 / 2021=23939;
    --  无 2020 year index URL — cat page /2020中国 → 全国普查非 city)
    SELECT generate_series(2020, 2026) AS year
),
cross_product AS (
    SELECT cd.city_code, cd.city_name, cd.province_code,
           id.indicator_key, id.indicator_label, id.unit,
           yd.year
    FROM city_dimension cd
    CROSS JOIN indicator_dimension id
    CROSS JOIN year_dimension yd
),
-- 669a-2021 real_data (4 city × 10 indicator = 40 cells expected, 26 actual real + 14 DATA_MISSING)
-- 来源: hongheiku /djs/{id}.html (深圳 26979 / 广州 27931 / 杭州 25516 / 南京 27791)
-- missing cells: 广州公报非典型结构 (强调战略性新兴产业而非传统 gdp_total/三产分项) +
--                fixed_asset 2021 城市公报普遍未列 (守新增红线-3 不手填)
real_data_2021 AS (
    SELECT * FROM (VALUES
        -- GUANGDONG_SHENZHEN (深圳 2021, 9/10 real cells)
        ('GUANGDONG_SHENZHEN', 'gdp_total',     30664.85::numeric),
        ('GUANGDONG_SHENZHEN', 'gdp_growth',    6.7::numeric),
        ('GUANGDONG_SHENZHEN', 'primary_gdp',   26.59::numeric),
        ('GUANGDONG_SHENZHEN', 'secondary_gdp', 11338.59::numeric),
        ('GUANGDONG_SHENZHEN', 'tertiary_gdp',  19299.67::numeric),
        ('GUANGDONG_SHENZHEN', 'gdp_percapita', 173663::numeric),
        ('GUANGDONG_SHENZHEN', 'fiscal_rev',    4257.76::numeric),
        -- ('GUANGDONG_SHENZHEN', 'fixed_asset',  NULL)  -- 2021 公报未列
        ('GUANGDONG_SHENZHEN', 'retail',        9498.12::numeric),
        ('GUANGDONG_SHENZHEN', 'trade',         35435.57::numeric),
        -- GUANGDONG_GUANGZHOU (广州 2021, 3/10 real cells — 公报非典型结构)
        -- ('GUANGDONG_GUANGZHOU', 'gdp_total', NULL)  -- 公报用「战略性新兴产业合计」非「地区生产总值」表述
        ('GUANGDONG_GUANGZHOU', 'gdp_growth',  8.2::numeric),
        -- ('GUANGDONG_GUANGZHOU', 'primary_gdp', NULL)  -- 公报未列
        -- ('GUANGDONG_GUANGZHOU', 'secondary_gdp', NULL)  -- 公报未列
        -- ('GUANGDONG_GUANGZHOU', 'tertiary_gdp', NULL)  -- 公报未列
        -- ('GUANGDONG_GUANGZHOU', 'gdp_percapita', NULL)  -- 公报未列
        ('GUANGDONG_GUANGZHOU', 'fiscal_rev',  1883.18::numeric),
        -- ('GUANGDONG_GUANGZHOU', 'fixed_asset', NULL)  -- 公报未列
        ('GUANGDONG_GUANGZHOU', 'retail',      10122.56::numeric),
        -- ('GUANGDONG_GUANGZHOU', 'trade', NULL)  -- 公报未列
        -- ZHEJIANG_HANGZHOU (杭州 2021, 5/10 real cells)
        ('ZHEJIANG_HANGZHOU', 'gdp_total',     18109::numeric),
        ('ZHEJIANG_HANGZHOU', 'gdp_growth',    8.5::numeric),
        -- ('ZHEJIANG_HANGZHOU', 'primary_gdp', NULL)  -- 公报未列
        -- ('ZHEJIANG_HANGZHOU', 'secondary_gdp', NULL)  -- 公报未列
        -- ('ZHEJIANG_HANGZHOU', 'tertiary_gdp', NULL)  -- 公报未列
        -- ('ZHEJIANG_HANGZHOU', 'gdp_percapita', NULL)  -- 公报未列
        ('ZHEJIANG_HANGZHOU', 'fiscal_rev',    2386.6::numeric),
        -- ('ZHEJIANG_HANGZHOU', 'fixed_asset', NULL)  -- 公报未列
        ('ZHEJIANG_HANGZHOU', 'retail',        6744::numeric),
        ('ZHEJIANG_HANGZHOU', 'trade',         7369::numeric),
        -- JIANGSU_NANJING (南京 2021, 9/10 real cells)
        -- ('JIANGSU_NANJING', 'gdp_total', NULL)  -- 公报未直接列, 仅含三产分项
        ('JIANGSU_NANJING', 'gdp_growth',    7.5::numeric),
        ('JIANGSU_NANJING', 'primary_gdp',   303.94::numeric),
        ('JIANGSU_NANJING', 'secondary_gdp', 5902.65::numeric),
        ('JIANGSU_NANJING', 'tertiary_gdp',  10148.73::numeric),
        ('JIANGSU_NANJING', 'gdp_percapita', 174520::numeric),
        ('JIANGSU_NANJING', 'fiscal_rev',    1729.52::numeric),
        ('JIANGSU_NANJING', 'fixed_asset',   5675.24::numeric),
        ('JIANGSU_NANJING', 'retail',        7899.41::numeric),
        ('JIANGSU_NANJING', 'trade',         6366.83::numeric)
    ) AS t(city_code, indicator_key, value)
),
-- 669a-2020 zero-harvest: 无 real_data CTE (hongheiku 城市 2020 缺文)
-- 669a-2021+ sub-knives 将添加 real_data_2021/2022/2023/2024/2025 CTE
missing_city_year AS (
    -- 永久缺 city (4 直辖市禁重复; 港/澳/台 不在 city mart)
    -- 669a-2021 范围内无永久缺 city (4 直辖市之外的 4 priority city 都有 cat tag)
    SELECT NULL::text AS city_code WHERE FALSE
)
SELECT
    cp.city_code,
    cp.city_name,
    cp.province_code,
    cp.indicator_key,
    cp.indicator_label,
    cp.unit,
    cp.year,
    rd.value,
    CASE
        WHEN cp.year < 2020  THEN 'DATA_MISSING'
        WHEN cp.year = 2026  THEN 'DATA_MISSING'
        WHEN cp.year = 2020  THEN 'DATA_MISSING'  -- hongheiku 城市 2020 缺文
        WHEN cp.year = 2021  AND rd.value IS NOT NULL THEN NULL  -- real cell, status=NULL
        WHEN cp.year = 2021  AND rd.value IS NULL     THEN 'DATA_MISSING'
        ELSE 'DATA_MISSING'  -- 2022-2025 待 669a-2022+ sub-knives harvest
    END AS status,
    CASE
        WHEN cp.year < 2020  THEN '新增红线-1: 2001-2019 禁编造历史数据 (hongheiku 城市 probe 待补; 红线通用)'
        WHEN cp.year = 2026  THEN '新增红线-2: 2026 待 2027 官方发布'
        WHEN cp.year = 2020  THEN 'hongheiku 城市维度 2020 缺文 (cat index 仅 2021-2025; knife 669 待拓展其他来源)'
        WHEN cp.year = 2021  AND rd.value IS NOT NULL THEN NULL  -- real cell, no missing_reason
        WHEN cp.year = 2021  AND rd.value IS NULL     THEN 'knife 669a-2021 公报未列/正则 miss (守新增红线-3 不手填; 后续 sub-knife 可补采)'
        ELSE 'knife 669a-2022/2023/2024/2025 待 harvest (本刀 669a-2020+2021 已 DELIVERED)'
    END AS missing_reason,
    CASE
        WHEN cp.year = 2021  AND rd.value IS NOT NULL THEN 'HONGHEIKU_TRANSLOAD'
        ELSE 'DATA_MISSING'
    END AS lineage_source_type,
    CASE
        WHEN cp.year = 2021  AND rd.value IS NOT NULL THEN 'tjgb.hongheiku.com/djs/' || cp.city_name
        ELSE 'none'
    END AS lineage_origin,
    CASE
        WHEN cp.year = 2020  THEN 'K669a-2020-2026-09-04'
        WHEN cp.year = 2021  THEN 'K669a-2021-2026-09-04'
        ELSE 'pending'
    END AS lineage_ruling,
    'false'         AS lineage_is_demo
FROM cross_product cp
LEFT JOIN real_data_2021 rd
    ON cp.city_code = rd.city_code
    AND cp.indicator_key = rd.indicator_key
    AND cp.year = 2021;
