-- Mart model: mart_city_timeseries (P2 / knife 669a-2020)
-- ============================================================================
-- Cross product: 4 cities × 10 indicators × 7 years (2020-2026) = 280 rows.
--
-- Per 新增红线-7 (docs/87 §3.2 P2 数据扩展): mart schema 保持 province/city 分离
-- (不合并), 4 直辖市 (北京/上海/天津/重庆) 禁在 city 维度重复 (已在 province mart)。
--
-- Per 新增红线-3 (docs/05 §8 禁手填): city 数据只准来自 hongheiku 城市维度
-- 采集; 缺失年/缺失 city 禁补零。
--
-- 669a-2020 范围 (zero-harvest knife):
--   - 4 priority city (深圳市/广州市/杭州市/南京市)
--   - year 2020 only (实证: hongheiku 城市 cat index 仅 2021-2025, 2020 缺文)
--   - 所有 40 cells = DATA_MISSING, 验证 zero-handling 路径 (不补零/不手填/不编造)
--   - 0 HTTP budget (no harvest — 仅建 schema + 实证 hongheiku 城市 2020 缺文)
--
-- 669a 后续 sub-knives:
--   - 669a-2021 / 2022 / 2023 / 2024 / 2025 (5 sub-knives)
--   - 每刀 ADD 4 city × 10 indicator × 1 year = 40 cells (real data from hongheiku 城市 cat)
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
-- Red lines (669a-2020 enforced):
--   - 4 直辖市禁在 city 维度重复 (新增红线-7; 已在 mart_province_timeseries)
--   - 城市数据禁手填 (新增红线-3; hongheiku 缺文 → DATA_MISSING)
--   - city_code 命名: {PROVINCE_CODE}_{CITY_SLUG} (大写英文 + 下划线)

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
-- 669a-2020 zero-harvest: 无 real_data CTE (hongheiku 城市 2020 缺文)
-- 669a-2021+ sub-knives 将添加 real_data_2021/2022/2023/2024/2025 CTE
missing_city_year AS (
    -- 永久缺 city (4 直辖市禁重复; 港/澳/台 不在 city mart)
    -- 669a-2020 范围内无永久缺 city (4 直辖市之外的 4 priority city 都有 cat tag)
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
    NULL::numeric AS value,
    CASE
        WHEN cp.year < 2020  THEN 'DATA_MISSING'
        WHEN cp.year = 2026  THEN 'DATA_MISSING'
        WHEN cp.year = 2020  THEN 'DATA_MISSING'  -- hongheiku 城市 2020 缺文
        ELSE 'DATA_MISSING'  -- 2021-2025 待 669a-2021+ sub-knives harvest
    END AS status,
    CASE
        WHEN cp.year < 2020  THEN '新增红线-1: 2001-2019 禁编造历史数据 (hongheiku 城市 probe 待补; 红线通用)'
        WHEN cp.year = 2026  THEN '新增红线-2: 2026 待 2027 官方发布'
        WHEN cp.year = 2020  THEN 'hongheiku 城市维度 2020 缺文 (cat index 仅 2021-2025; knife 669 待拓展其他来源)'
        ELSE 'knife 669a-2021/2022/2023/2024/2025 待 harvest (本刀 669a-2020 仅建 schema)'
    END AS missing_reason,
    'DATA_MISSING' AS lineage_source_type,
    'none'          AS lineage_origin,
    'K669a-2020-2026-09-04' AS lineage_ruling,
    'false'         AS lineage_is_demo
FROM cross_product cp;
