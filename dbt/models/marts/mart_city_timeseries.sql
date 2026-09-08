-- Mart model: mart_city_timeseries (P2 / knife 669a-2020/2021/2022/2023/2024/2025 + 669b-2025)
-- ============================================================================
-- Cross product: 29 cities × 10 indicators × 7 years (2020-2026) = 2030 rows.
--   - 669a 4 cities (深/穗/杭/宁)
--   - 669b 25 cities (28 省会 - 3 已在 669a - 4 直辖市禁)
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
    -- 669b 批次: 25 省会 city (除 4 直辖市禁 city dim + 3 已在 669a: 穗/杭/宁)
    -- city_code 命名规范: {PROVINCE_CODE}_{CITY_SLUG} (大写英文)
    SELECT * FROM (VALUES
        ('GUANGDONG_SHENZHEN',  '深圳市', 'GUANGDONG'),
        ('GUANGDONG_GUANGZHOU', '广州市', 'GUANGDONG'),
        ('ZHEJIANG_HANGZHOU',   '杭州市', 'ZHEJIANG'),
        ('JIANGSU_NANJING',     '南京市', 'JIANGSU'),
        -- 669b 25 省会 (新增)
        ('HEBEI_SHIJIAZHUANG',     '石家庄市',     'HEBEI'),
        ('SHANXI_TAIYUAN',         '太原市',       'SHANXI'),
        ('NEIMENGGU_HUHEHAOTE',    '呼和浩特市',   'NEIMENGGU'),
        ('LIAONING_SHENYANG',      '沈阳市',       'LIAONING'),
        ('JILIN_CHANGCHUN',        '长春市',       'JILIN'),
        ('HEILONGJIANG_HARBIN',    '哈尔滨市',     'HEILONGJIANG'),
        ('ANHUI_HEFEI',            '合肥市',       'ANHUI'),
        ('FUJIAN_FUZHOU',          '福州市',       'FUJIAN'),
        ('JIANGXI_NANCHANG',       '南昌市',       'JIANGXI'),
        ('SHANDONG_JINAN',         '济南市',       'SHANDONG'),
        ('HENAN_ZHENGZHOU',        '郑州市',       'HENAN'),
        ('HUBEI_WUHAN',            '武汉市',       'HUBEI'),
        ('HUNAN_CHANGSHA',         '长沙市',       'HUNAN'),
        ('GUANGXI_NANNING',        '南宁市',       'GUANGXI'),
        ('HAINAN_HAIKOU',          '海口市',       'HAINAN'),
        ('SICHUAN_CHENGDU',        '成都市',       'SICHUAN'),
        ('GUIZHOU_GUIYANG',        '贵阳市',       'GUIZHOU'),
        ('YUNNAN_KUNMING',         '昆明市',       'YUNNAN'),
        ('XIZANG_LASA',            '拉萨市',       'XIZANG'),
        ('SHAANXI_XIAN',           '西安市',       'SHAANXI'),
        ('GANSU_LANZHOU',          '兰州市',       'GANSU'),
        ('QINGHAI_XINING',         '西宁市',       'QINGHAI'),
        ('NINGXIA_YINCHUAN',       '银川市',       'NINGXIA'),
        ('XINJIANG_WULUMUQI',      '乌鲁木齐市',   'XINJIANG'),
        ('TAIWAN_TAIPEI',          '台北市',       'TAIWAN')
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
-- 669a-2022 real_data (4 city × 10 indicator = 40 cells, 37 real + 3 DATA_MISSING)
-- 来源: hongheiku /djs/{id}.html (深圳 38197 / 广州 38118 / 杭州 37237 / 南京 38005)
-- URL discovery: 4 city tag pages cached from 669a-2021 (0 HTTP)
-- 2022 公报表述变体 (实证):
--   gdp_total: 「2022年深圳地区生产总值32387.68亿元」(城名前缀) /
--              「实现地区生产总值（初步核算数）28839.00亿元」(穗括号注) /
--              「实现地区生产总值[2]18753亿元」(杭/宁脚注标记)
--   gdp_percapita: 加「达到/为」修饰 (穗/杭)
--   trade: 穗用「商品进出口总值」(同一商品/货物口径, 合法采集非手填)
-- 3 DATA_MISSING: 深圳/广州/杭州 fixed_asset (2022 公报仅发增速 8.4%/-2.1%/6.0% 无绝对值,
--   守新增红线-3 不手填不换算); 南京 10/10 全齐
real_data_2022 AS (
    SELECT * FROM (VALUES
        -- GUANGDONG_SHENZHEN (深圳 2022, 9/10 real cells)
        ('GUANGDONG_SHENZHEN', 'gdp_total',     32387.68::numeric),
        ('GUANGDONG_SHENZHEN', 'gdp_growth',    3.3::numeric),
        ('GUANGDONG_SHENZHEN', 'primary_gdp',   25.64::numeric),
        ('GUANGDONG_SHENZHEN', 'secondary_gdp', 12405.88::numeric),
        ('GUANGDONG_SHENZHEN', 'tertiary_gdp',  19956.16::numeric),
        ('GUANGDONG_SHENZHEN', 'gdp_percapita', 183274::numeric),
        ('GUANGDONG_SHENZHEN', 'fiscal_rev',    4012.27::numeric),
        -- ('GUANGDONG_SHENZHEN', 'fixed_asset', NULL)  -- 公报仅发增速 8.4% 无绝对值
        ('GUANGDONG_SHENZHEN', 'retail',        9708.28::numeric),
        ('GUANGDONG_SHENZHEN', 'trade',         36737.52::numeric),
        -- GUANGDONG_GUANGZHOU (广州 2022, 9/10 real cells)
        ('GUANGDONG_GUANGZHOU', 'gdp_total',     28839.00::numeric),
        ('GUANGDONG_GUANGZHOU', 'gdp_growth',    1.0::numeric),
        ('GUANGDONG_GUANGZHOU', 'primary_gdp',   318.31::numeric),
        ('GUANGDONG_GUANGZHOU', 'secondary_gdp', 7909.29::numeric),
        ('GUANGDONG_GUANGZHOU', 'tertiary_gdp',  20611.40::numeric),
        ('GUANGDONG_GUANGZHOU', 'gdp_percapita', 153625::numeric),
        ('GUANGDONG_GUANGZHOU', 'fiscal_rev',    1854.73::numeric),
        -- ('GUANGDONG_GUANGZHOU', 'fixed_asset', NULL)  -- 公报仅发增速 -2.1% 无绝对值
        ('GUANGDONG_GUANGZHOU', 'retail',        10298.15::numeric),
        ('GUANGDONG_GUANGZHOU', 'trade',         10948.40::numeric),  -- 商品进出口总值口径
        -- ZHEJIANG_HANGZHOU (杭州 2022, 9/10 real cells)
        ('ZHEJIANG_HANGZHOU', 'gdp_total',     18753::numeric),
        ('ZHEJIANG_HANGZHOU', 'gdp_growth',    1.5::numeric),
        ('ZHEJIANG_HANGZHOU', 'primary_gdp',   346::numeric),
        ('ZHEJIANG_HANGZHOU', 'secondary_gdp', 5620::numeric),
        ('ZHEJIANG_HANGZHOU', 'tertiary_gdp',  12787::numeric),
        ('ZHEJIANG_HANGZHOU', 'gdp_percapita', 152588::numeric),
        ('ZHEJIANG_HANGZHOU', 'fiscal_rev',    2451::numeric),
        -- ('ZHEJIANG_HANGZHOU', 'fixed_asset', NULL)  -- 公报仅发增速 6.0% 无绝对值
        ('ZHEJIANG_HANGZHOU', 'retail',        7294::numeric),
        ('ZHEJIANG_HANGZHOU', 'trade',         7565::numeric),
        -- JIANGSU_NANJING (南京 2022, 10/10 real cells — 本批唯一全齐)
        ('JIANGSU_NANJING', 'gdp_total',     16907.85::numeric),
        ('JIANGSU_NANJING', 'gdp_growth',    2.1::numeric),
        ('JIANGSU_NANJING', 'primary_gdp',   315.56::numeric),
        ('JIANGSU_NANJING', 'secondary_gdp', 6069.64::numeric),
        ('JIANGSU_NANJING', 'tertiary_gdp',  10522.65::numeric),
        ('JIANGSU_NANJING', 'gdp_percapita', 178781::numeric),
        ('JIANGSU_NANJING', 'fiscal_rev',    1558.2::numeric),
        ('JIANGSU_NANJING', 'fixed_asset',   5874.92::numeric),
        ('JIANGSU_NANJING', 'retail',        7832.41::numeric),
        ('JIANGSU_NANJING', 'trade',         6292.13::numeric)
    ) AS t(city_code, indicator_key, value)
),
-- 669a-2023 real_data (4 city × 10 indicator = 40 cells, 37 real + 3 DATA_MISSING)
-- 来源: hongheiku /djs/{id}.html (深圳 49092 / 广州 47985 / 杭州 45617 / 南京 46614)
-- URL discovery: 4 city tag pages cached from 669a-2021 (0 HTTP)
-- 2023 公报表述变体 (实证):
--   gdp_percapita: 南京用缩写「人均GDP达183015元」+ 广州单字「达」+ 杭州「为」
--     (同一人均 GDP 口径, 采集自公报原文非手填)
--   fixed_asset: 南京「完成固定资产投资5763.64亿元」(完成前缀);
--     深/穗/杭 仅发增速 11.0%/3.6%/2.8% 无绝对值 → DATA_MISSING (守红线-3 不换算)
real_data_2023 AS (
    SELECT * FROM (VALUES
        -- GUANGDONG_SHENZHEN (深圳 2023, 9/10 real cells)
        ('GUANGDONG_SHENZHEN', 'gdp_total',     34606.40::numeric),
        ('GUANGDONG_SHENZHEN', 'gdp_growth',    6.0::numeric),
        ('GUANGDONG_SHENZHEN', 'primary_gdp',   24.71::numeric),
        ('GUANGDONG_SHENZHEN', 'secondary_gdp', 13015.32::numeric),
        ('GUANGDONG_SHENZHEN', 'tertiary_gdp',  21566.38::numeric),
        ('GUANGDONG_SHENZHEN', 'gdp_percapita', 195230.17::numeric),
        ('GUANGDONG_SHENZHEN', 'fiscal_rev',    4112.78::numeric),
        -- ('GUANGDONG_SHENZHEN', 'fixed_asset', NULL)  -- 公报仅发增速 11.0% 无绝对值
        ('GUANGDONG_SHENZHEN', 'retail',        10486.19::numeric),
        ('GUANGDONG_SHENZHEN', 'trade',         38710.70::numeric),
        -- GUANGDONG_GUANGZHOU (广州 2023, 9/10 real cells)
        ('GUANGDONG_GUANGZHOU', 'gdp_total',     30355.73::numeric),
        ('GUANGDONG_GUANGZHOU', 'gdp_growth',    4.6::numeric),
        ('GUANGDONG_GUANGZHOU', 'primary_gdp',   317.78::numeric),
        ('GUANGDONG_GUANGZHOU', 'secondary_gdp', 7775.71::numeric),
        ('GUANGDONG_GUANGZHOU', 'tertiary_gdp',  22262.24::numeric),
        ('GUANGDONG_GUANGZHOU', 'gdp_percapita', 161634::numeric),
        ('GUANGDONG_GUANGZHOU', 'fiscal_rev',    1944.15::numeric),
        -- ('GUANGDONG_GUANGZHOU', 'fixed_asset', NULL)  -- 公报仅发增速 3.6% 无绝对值
        ('GUANGDONG_GUANGZHOU', 'retail',        11012.62::numeric),
        ('GUANGDONG_GUANGZHOU', 'trade',         10914.28::numeric),
        -- ZHEJIANG_HANGZHOU (杭州 2023, 9/10 real cells)
        ('ZHEJIANG_HANGZHOU', 'gdp_total',     20059::numeric),
        ('ZHEJIANG_HANGZHOU', 'gdp_growth',    5.6::numeric),
        ('ZHEJIANG_HANGZHOU', 'primary_gdp',   347::numeric),
        ('ZHEJIANG_HANGZHOU', 'secondary_gdp', 5667::numeric),
        ('ZHEJIANG_HANGZHOU', 'tertiary_gdp',  14045::numeric),
        ('ZHEJIANG_HANGZHOU', 'gdp_percapita', 161129::numeric),
        ('ZHEJIANG_HANGZHOU', 'fiscal_rev',    2617::numeric),
        -- ('ZHEJIANG_HANGZHOU', 'fixed_asset', NULL)  -- 公报仅发增速 2.8% 无绝对值
        ('ZHEJIANG_HANGZHOU', 'retail',        7671::numeric),
        ('ZHEJIANG_HANGZHOU', 'trade',         8030::numeric),
        -- JIANGSU_NANJING (南京 2023, 10/10 real cells — 本批唯一全齐)
        ('JIANGSU_NANJING', 'gdp_total',     17421.40::numeric),
        ('JIANGSU_NANJING', 'gdp_growth',    4.6::numeric),
        ('JIANGSU_NANJING', 'primary_gdp',   317.75::numeric),
        ('JIANGSU_NANJING', 'secondary_gdp', 5929.00::numeric),
        ('JIANGSU_NANJING', 'tertiary_gdp',  11174.65::numeric),
        ('JIANGSU_NANJING', 'gdp_percapita', 183015::numeric),
        ('JIANGSU_NANJING', 'fiscal_rev',    1620::numeric),
        ('JIANGSU_NANJING', 'fixed_asset',   5763.64::numeric),
        ('JIANGSU_NANJING', 'retail',        8201.07::numeric),
        ('JIANGSU_NANJING', 'trade',         5659.9::numeric)
    ) AS t(city_code, indicator_key, value)
),
-- 669a-2024 real_data (4 city × 10 indicator = 40 cells, 36 real + 4 DATA_MISSING)
-- 来源: hongheiku /djs/{id}.html (深圳 62867 / 广州 58648 / 杭州 57316 / 南京 57850)
-- URL discovery: 4 city tag pages cached from 669a-2021 (0 HTTP)
-- 2024 公报表述变体 (实证, 首跑 34/40 修 2 处 regex 后 36/40):
--   gdp_total: 南京脚注 [2] 前有换行「地区生产总值⏎[2]⏎18500.81亿元」
--     (2022 为同行空格) → regex 加 \s* 在脚注组前
--   retail: 杭州脚注 [4] 「社会消费品零售总额[4]9151亿元」 → 同加脚注容错
--   fixed_asset: 南京有绝对值 4777.29亿元; 深/穗/杭 仅发增速 (2.4%/0.2%/-2.9%)
--   南京 retail 仅发增速 4.3% 无绝对值 → DATA_MISSING (守红线-3)
-- 4 DATA_MISSING: 3× fixed_asset (深/穗/杭) + 1× 南京 retail
real_data_2024 AS (
    SELECT * FROM (VALUES
        -- GUANGDONG_SHENZHEN (深圳 2024, 9/10 real cells)
        ('GUANGDONG_SHENZHEN', 'gdp_total',     36801.87::numeric),
        ('GUANGDONG_SHENZHEN', 'gdp_growth',    5.8::numeric),
        ('GUANGDONG_SHENZHEN', 'primary_gdp',   26.37::numeric),
        ('GUANGDONG_SHENZHEN', 'secondary_gdp', 13909.28::numeric),
        ('GUANGDONG_SHENZHEN', 'tertiary_gdp',  22866.22::numeric),
        ('GUANGDONG_SHENZHEN', 'gdp_percapita', 205714::numeric),
        ('GUANGDONG_SHENZHEN', 'fiscal_rev',    3914.18::numeric),
        -- ('GUANGDONG_SHENZHEN', 'fixed_asset', NULL)  -- 公报仅发增速 2.4% 无绝对值
        ('GUANGDONG_SHENZHEN', 'retail',        10637.70::numeric),
        ('GUANGDONG_SHENZHEN', 'trade',         45048.24::numeric),
        -- GUANGDONG_GUANGZHOU (广州 2024, 9/10 real cells)
        ('GUANGDONG_GUANGZHOU', 'gdp_total',     31032.50::numeric),
        ('GUANGDONG_GUANGZHOU', 'gdp_growth',    2.1::numeric),
        ('GUANGDONG_GUANGZHOU', 'primary_gdp',   334.47::numeric),
        ('GUANGDONG_GUANGZHOU', 'secondary_gdp', 7839.45::numeric),
        ('GUANGDONG_GUANGZHOU', 'tertiary_gdp',  22858.58::numeric),
        ('GUANGDONG_GUANGZHOU', 'gdp_percapita', 164171::numeric),
        ('GUANGDONG_GUANGZHOU', 'fiscal_rev',    1954.74::numeric),
        -- ('GUANGDONG_GUANGZHOU', 'fixed_asset', NULL)  -- 公报仅发增速 0.2% 无绝对值
        ('GUANGDONG_GUANGZHOU', 'retail',        11055.77::numeric),
        ('GUANGDONG_GUANGZHOU', 'trade',         11238.38::numeric),  -- 商品进出口总值口径
        -- ZHEJIANG_HANGZHOU (杭州 2024, 9/10 real cells)
        ('ZHEJIANG_HANGZHOU', 'gdp_total',     21860::numeric),
        ('ZHEJIANG_HANGZHOU', 'gdp_growth',    4.7::numeric),
        ('ZHEJIANG_HANGZHOU', 'primary_gdp',   369::numeric),
        ('ZHEJIANG_HANGZHOU', 'secondary_gdp', 5529::numeric),
        ('ZHEJIANG_HANGZHOU', 'tertiary_gdp',  15962::numeric),
        ('ZHEJIANG_HANGZHOU', 'gdp_percapita', 173867::numeric),
        ('ZHEJIANG_HANGZHOU', 'fiscal_rev',    2640::numeric),
        -- ('ZHEJIANG_HANGZHOU', 'fixed_asset', NULL)  -- 公报仅发增速 -2.9% 无绝对值
        ('ZHEJIANG_HANGZHOU', 'retail',        9151::numeric),  -- 脚注[4]容错采集
        ('ZHEJIANG_HANGZHOU', 'trade',         8549::numeric),
        -- JIANGSU_NANJING (南京 2024, 9/10 real cells — retail 公报仅发增速)
        ('JIANGSU_NANJING', 'gdp_total',     18500.81::numeric),  -- 脚注[2]换行容错采集
        ('JIANGSU_NANJING', 'gdp_growth',    4.5::numeric),
        ('JIANGSU_NANJING', 'primary_gdp',   331.00::numeric),
        ('JIANGSU_NANJING', 'secondary_gdp', 5831.06::numeric),
        ('JIANGSU_NANJING', 'tertiary_gdp',  12338.75::numeric),
        ('JIANGSU_NANJING', 'gdp_percapita', 193483::numeric),
        ('JIANGSU_NANJING', 'fiscal_rev',    1596.02::numeric),
        ('JIANGSU_NANJING', 'fixed_asset',   4777.29::numeric),
        -- ('JIANGSU_NANJING', 'retail', NULL)  -- 公报仅发增速 4.3% 无绝对值
        ('JIANGSU_NANJING', 'trade',         5459.2::numeric)
    ) AS t(city_code, indicator_key, value)
),
-- 669a-2025 real_data (4 city × 10 indicator = 40 cells, 18 real + 22 DATA_MISSING)
-- 来源: hongheiku /djs/{id}.html (广州 69954, 发布 2026-05-12 / 杭州 69708, 发布 2026-04-30)
-- URL discovery: 6 HTTP total (2 tag fetches sz/nj + 2 bulletins gz/hz + 1 cat index + 1 search sz + 1 search nj)
-- 2025 harvest 实测 (probe 实证):
--   hongheiku 2025 entry AVAILABLE for GUANGZHOU + HANGZHOU
--   hongheiku 2025 entry ABSENT for SHENZHEN + NANJING (tag 页只列 2021-2024, 站内搜索无结果)
--   → SZ/NJ 2025 全部 10 cells DATA_MISSING (守红线-3 不手填, 公报未发布/未收录)
-- 2025 公报表述变体 (empirical probe):
--   GDP: 广州括号注「(初步核算数)」 → 沿用 2024 括号容错; 杭州脚注 [2] 23011亿元 → 沿用 s* 脚注容错
--   人均: 全称「人均地区生产总值」+ 无缩写 (2025 公报口径规范化)
--   固投: 仅发增速 (穗-6.7% / 杭占比) → DATA_MISSING (守红线-3 增速≠绝对值)
real_data_2025 AS (
    SELECT * FROM (VALUES
        -- GUANGDONG_SHENZHEN (深圳 2025, 0/10 — hongheiku 无 2025 entry)
        -- GUANGDONG_GUANGZHOU (广州 2025, 9/10 real cells — fixed_asset 仅发增速 -6.7%)
        ('GUANGDONG_GUANGZHOU', 'gdp_total',     32039.46::numeric),
        ('GUANGDONG_GUANGZHOU', 'gdp_growth',    4.0::numeric),
        ('GUANGDONG_GUANGZHOU', 'primary_gdp',   317.02::numeric),
        ('GUANGDONG_GUANGZHOU', 'secondary_gdp', 7710.27::numeric),
        ('GUANGDONG_GUANGZHOU', 'tertiary_gdp',  24012.17::numeric),
        ('GUANGDONG_GUANGZHOU', 'gdp_percapita', 168279::numeric),
        ('GUANGDONG_GUANGZHOU', 'fiscal_rev',    2184.82::numeric),
        -- ('GUANGDONG_GUANGZHOU', 'fixed_asset', NULL)  -- 公报仅发增速 -6.7% 无绝对值
        ('GUANGDONG_GUANGZHOU', 'retail',        11032.38::numeric),
        ('GUANGDONG_GUANGZHOU', 'trade',         12407.24::numeric),
        -- ZHEJIANG_HANGZHOU (杭州 2025, 9/10 real cells — fixed_asset 仅发占比)
        ('ZHEJIANG_HANGZHOU', 'gdp_total',     23011::numeric),  -- 脚注[2]容错采集
        ('ZHEJIANG_HANGZHOU', 'gdp_growth',    5.2::numeric),
        ('ZHEJIANG_HANGZHOU', 'primary_gdp',   383::numeric),
        ('ZHEJIANG_HANGZHOU', 'secondary_gdp', 5631::numeric),
        ('ZHEJIANG_HANGZHOU', 'tertiary_gdp',  16997::numeric),
        ('ZHEJIANG_HANGZHOU', 'gdp_percapita', 181732::numeric),
        ('ZHEJIANG_HANGZHOU', 'fiscal_rev',    2693::numeric),
        -- ('ZHEJIANG_HANGZHOU', 'fixed_asset', NULL)  -- 公报仅发占比「民间投资占46.0%」, 无绝对值
        ('ZHEJIANG_HANGZHOU', 'retail',        9499::numeric),
        ('ZHEJIANG_HANGZHOU', 'trade',         9072::numeric)
        -- JIANGSU_NANJING (南京 2025, 0/10 — hongheiku 无 2025 entry)
    ) AS t(city_code, indicator_key, value)
),
-- 669b-2025 real_data (25 city × 10 indicator = 250 cells, 0 real + 250 DATA_MISSING)
-- 来源: hongheiku /tag/{city_name} (无 2025 city bulletin)
-- URL discovery: 25 tag pages × 1 = 25 HTTP (per knife 669b-2025 budget, ≤32 红线)
-- 实证 (3 probe methods, 全部 0 命中):
--   1. tag 页 × 25 city — 全部仅含 2020 年公报 + 人口普查公报 (无 2021-2025)
--   2. cat index /category/sjtjgb 2025 — 1 entry (national 68085), 0 city
--   3. 站搜 ?s={city}2025 × 5 代表性 city (武汉/成都/长沙/杭州/广州) — 全部 '未找到', 0 results
-- 决策: 25 city × 2025 = 全 DATA_MISSING (守新增红线-3 不手填, 公报未发布/未收录)
-- lineage_ruling = 'K669b-2025-2026-09-08'
real_data_669b_2025 AS (
    -- Empty CTE: 25 省会 × 2025 = all DATA_MISSING (hongheiku 无 2025 city bulletin)
    SELECT NULL::text AS city_code, NULL::text AS indicator_key, NULL::numeric AS value
    WHERE FALSE
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
    COALESCE(rd.value, rd2.value, rd3.value, rd4.value, rd5.value, rd6.value) AS value,
    CASE
        WHEN cp.year < 2020  THEN 'DATA_MISSING'
        WHEN cp.year = 2026  THEN 'DATA_MISSING'
        WHEN cp.year = 2020  THEN 'DATA_MISSING'  -- hongheiku 城市 2020 缺文
        WHEN cp.year = 2021  AND rd.value IS NOT NULL THEN NULL  -- real cell, status=NULL
        WHEN cp.year = 2021  AND rd.value IS NULL     THEN 'DATA_MISSING'
        WHEN cp.year = 2022  AND rd2.value IS NOT NULL THEN NULL  -- real cell, status=NULL
        WHEN cp.year = 2022  AND rd2.value IS NULL     THEN 'DATA_MISSING'
        WHEN cp.year = 2023  AND rd3.value IS NOT NULL THEN NULL  -- real cell, status=NULL
        WHEN cp.year = 2023  AND rd3.value IS NULL     THEN 'DATA_MISSING'
        WHEN cp.year = 2024  AND rd4.value IS NOT NULL THEN NULL  -- real cell, status=NULL
        WHEN cp.year = 2024  AND rd4.value IS NULL     THEN 'DATA_MISSING'
        WHEN cp.year = 2025  AND rd5.value IS NOT NULL THEN NULL  -- real cell, status=NULL
        WHEN cp.year = 2025  AND rd6.value IS NOT NULL THEN NULL  -- real cell (future-proofing for 669b)
        WHEN cp.year = 2025  AND rd5.value IS NULL     THEN 'DATA_MISSING'  -- covers 4 669a + 25 669b cities
        ELSE 'DATA_MISSING'  -- 2026 待 2027 官方发布
    END AS status,
    CASE
        WHEN cp.year < 2020  THEN '新增红线-1: 2001-2019 禁编造历史数据 (hongheiku 城市 probe 待补; 红线通用)'
        WHEN cp.year = 2026  THEN '新增红线-2: 2026 待 2027 官方发布'
        WHEN cp.year = 2020  THEN 'hongheiku 城市维度 2020 缺文 (cat index 仅 2021-2025; knife 669 待拓展其他来源)'
        WHEN cp.year = 2021  AND rd.value IS NOT NULL THEN NULL  -- real cell, no missing_reason
        WHEN cp.year = 2021  AND rd.value IS NULL     THEN 'knife 669a-2021 公报未列/正则 miss (守新增红线-3 不手填; 后续 sub-knife 可补采)'
        WHEN cp.year = 2022  AND rd2.value IS NOT NULL THEN NULL  -- real cell, no missing_reason
        WHEN cp.year = 2022  AND rd2.value IS NULL     THEN 'knife 669a-2022 公报仅发增速无绝对值 (守新增红线-3 不手填; 后续 sub-knife 可补采)'
        WHEN cp.year = 2023  AND rd3.value IS NOT NULL THEN NULL  -- real cell, no missing_reason
        WHEN cp.year = 2023  AND rd3.value IS NULL     THEN 'knife 669a-2023 公报仅发增速无绝对值 (守新增红线-3 不手填; 后续 sub-knife 可补采)'
        WHEN cp.year = 2024  AND rd4.value IS NOT NULL THEN NULL  -- real cell, no missing_reason
        WHEN cp.year = 2024  AND rd4.value IS NULL     THEN 'knife 669a-2024 公报仅发增速无绝对值 (守新增红线-3 不手填; 后续 sub-knife 可补采)'
        WHEN cp.year = 2025  AND rd5.value IS NOT NULL THEN NULL  -- real cell, no missing_reason
        WHEN cp.year = 2025  AND rd6.value IS NOT NULL THEN NULL  -- real cell, no missing_reason (future-proofing for 669b)
        WHEN cp.year = 2025  AND cp.city_code IN (
            'HEBEI_SHIJIAZHUANG','SHANXI_TAIYUAN','NEIMENGGU_HUHEHAOTE','LIAONING_SHENYANG',
            'JILIN_CHANGCHUN','HEILONGJIANG_HARBIN','ANHUI_HEFEI','FUJIAN_FUZHOU',
            'JIANGXI_NANCHANG','SHANDONG_JINAN','HENAN_ZHENGZHOU','HUBEI_WUHAN',
            'HUNAN_CHANGSHA','GUANGXI_NANNING','HAINAN_HAIKOU','SICHUAN_CHENGDU',
            'GUIZHOU_GUIYANG','YUNNAN_KUNMING','XIZANG_LASA','SHAANXI_XIAN',
            'GANSU_LANZHOU','QINGHAI_XINING','NINGXIA_YINCHUAN','XINJIANG_WULUMUQI',
            'TAIWAN_TAIPEI'
        ) THEN 'knife 669b-2025 hongheiku 无 2025 city bulletin (3 probe methods 全部 0 命中, tag 页仅含 2020 年公报 + 人口普查公报; 守新增红线-3 不手填)'
        WHEN cp.year = 2025  AND rd5.value IS NULL     THEN 'knife 669a-2025 hongheiku 无 2025 entry / 公报仅发增速 (守红线-3 不手填; 后续 sub-knife 可补采)'
        ELSE 'knife 669 后续 sub-knife 待 harvest'
    END AS missing_reason,
    CASE
        WHEN cp.year = 2021  AND rd.value IS NOT NULL THEN 'HONGHEIKU_TRANSLOAD'
        WHEN cp.year = 2022  AND rd2.value IS NOT NULL THEN 'HONGHEIKU_TRANSLOAD'
        WHEN cp.year = 2023  AND rd3.value IS NOT NULL THEN 'HONGHEIKU_TRANSLOAD'
        WHEN cp.year = 2024  AND rd4.value IS NOT NULL THEN 'HONGHEIKU_TRANSLOAD'
        WHEN cp.year = 2025  AND rd5.value IS NOT NULL THEN 'HONGHEIKU_TRANSLOAD'
        WHEN cp.year = 2025  AND rd6.value IS NOT NULL THEN 'HONGHEIKU_TRANSLOAD'  -- future-proofing for 669b
        ELSE 'DATA_MISSING'
    END AS lineage_source_type,
    CASE
        WHEN cp.year = 2021  AND rd.value IS NOT NULL THEN 'tjgb.hongheiku.com/djs/' || cp.city_name
        WHEN cp.year = 2022  AND rd2.value IS NOT NULL THEN 'tjgb.hongheiku.com/djs/' || cp.city_name
        WHEN cp.year = 2023  AND rd3.value IS NOT NULL THEN 'tjgb.hongheiku.com/djs/' || cp.city_name
        WHEN cp.year = 2024  AND rd4.value IS NOT NULL THEN 'tjgb.hongheiku.com/djs/' || cp.city_name
        WHEN cp.year = 2025  AND rd5.value IS NOT NULL THEN 'tjgb.hongheiku.com/djs/' || cp.city_name
        WHEN cp.year = 2025  AND rd6.value IS NOT NULL THEN 'tjgb.hongheiku.com/djs/' || cp.city_name
        WHEN cp.year = 2025  AND cp.city_code IN (
            'HEBEI_SHIJIAZHUANG','SHANXI_TAIYUAN','NEIMENGGU_HUHEHAOTE','LIAONING_SHENYANG',
            'JILIN_CHANGCHUN','HEILONGJIANG_HARBIN','ANHUI_HEFEI','FUJIAN_FUZHOU',
            'JIANGXI_NANCHANG','SHANDONG_JINAN','HENAN_ZHENGZHOU','HUBEI_WUHAN',
            'HUNAN_CHANGSHA','GUANGXI_NANNING','HAINAN_HAIKOU','SICHUAN_CHENGDU',
            'GUIZHOU_GUIYANG','YUNNAN_KUNMING','XIZANG_LASA','SHAANXI_XIAN',
            'GANSU_LANZHOU','QINGHAI_XINING','NINGXIA_YINCHUAN','XINJIANG_WULUMUQI',
            'TAIWAN_TAIPEI'
        ) THEN 'tjgb.hongheiku.com/tag/' || cp.city_name || ' (no 2025 entry, 3 probes 0 命中)'
        ELSE 'none'
    END AS lineage_origin,
    CASE
        WHEN cp.year = 2020  THEN 'K669a-2020-2026-09-04'
        WHEN cp.year = 2021  THEN 'K669a-2021-2026-09-04'
        WHEN cp.year = 2022  THEN 'K669a-2022-2026-09-07'
        WHEN cp.year = 2023  THEN 'K669a-2023-2026-09-07'
        WHEN cp.year = 2024  THEN 'K669a-2024-2026-09-07'
        WHEN cp.year = 2025  AND cp.city_code IN (
            'GUANGDONG_SHENZHEN','GUANGDONG_GUANGZHOU','ZHEJIANG_HANGZHOU','JIANGSU_NANJING'
        ) THEN 'K669a-2025-2026-09-07'
        WHEN cp.year = 2025  THEN 'K669b-2025-2026-09-08'  -- 25 省会 (深/穗/杭/宁 之外的)
        ELSE 'pending'
    END AS lineage_ruling,
    'false'         AS lineage_is_demo
FROM cross_product cp
LEFT JOIN real_data_2021 rd
    ON cp.city_code = rd.city_code
    AND cp.indicator_key = rd.indicator_key
    AND cp.year = 2021
LEFT JOIN real_data_2022 rd2
    ON cp.city_code = rd2.city_code
    AND cp.indicator_key = rd2.indicator_key
    AND cp.year = 2022
LEFT JOIN real_data_2023 rd3
    ON cp.city_code = rd3.city_code
    AND cp.indicator_key = rd3.indicator_key
    AND cp.year = 2023
LEFT JOIN real_data_2024 rd4
    ON cp.city_code = rd4.city_code
    AND cp.indicator_key = rd4.indicator_key
    AND cp.year = 2024
LEFT JOIN real_data_2025 rd5
    ON cp.city_code = rd5.city_code
    AND cp.indicator_key = rd5.indicator_key
    AND cp.year = 2025
LEFT JOIN real_data_669b_2025 rd6
    ON cp.city_code = rd6.city_code
    AND cp.indicator_key = rd6.indicator_key
    AND cp.year = 2025;
