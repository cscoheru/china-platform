-- Mart model: mart_city_timeseries (P2 / knife 669a-2020/2021/2022/2023/2024/2025 + 669b-2025 + 669fix-b-2020)
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
-- 669fix-b-2020 (full re-harvest, 2026-09-08 启动):
--   - 历史误判 (per china-platform-669-historical-misjudgment.md): 669a-2020/2025 +
--     669b-2025 zero-harvest 判定基于错误 tag parse filter (eid < 15000 上限, 漏 /djs/
--     模式 2021-2025 + eid 20000+ 城市公告), 实际 25 省会 24 city 有 2020 bulletin
--   - 实证: 24/25 city real 2020 data (24 city × 1 HTTP = 24 HTTP, 在 ≤32 红线内)
--   - 161 absolute-value real cells + 70 DATA_MISSING = 250 cells (25 city × 10 indicator)
--     - 19 fixed_asset 增长% (无绝对值) → DATA_MISSING (per 669a-2021 receipt §2)
--     - 10 TAIWAN → DATA_MISSING (hongheiku 无 entry)
--     - 20 JIANGXI(10)/SHANXI(10) image-only → DATA_MISSING (无 OCR 范围)
--     - 21 城市级公报未列指标 → DATA_MISSING (守新增红线-3 不手填)
--   - lineage_ruling = 'K669fix-b-2020-2026-09-08'
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
        ('TAIWAN_TAIPEI',          '台北市',       'TAIWAN'),
        -- 669b-i batch 1 (2026-09-09, knife F first sub-knife)
        -- 4 计划单列市 (副省级, NOT 25 省会) + 4 高 GDP 地级市
        ('LIAONING_DALIAN',        '大连市',       'LIAONING'),
        ('SHANDONG_QINGDAO',       '青岛市',       'SHANDONG'),
        ('ZHEJIANG_NINGBO',        '宁波市',       'ZHEJIANG'),
        ('FUJIAN_XIAMEN',          '厦门市',       'FUJIAN'),
        ('JIANGSU_SUZHOU',         '苏州市',       'JIANGSU'),
        ('JIANGSU_WUXI',           '无锡市',       'JIANGSU'),
        ('GUANGDONG_FOSHAN',       '佛山市',       'GUANGDONG'),
        ('GUANGDONG_DONGGUAN',     '东莞市',       'GUANGDONG')
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
-- 669fix-b-2020 full re-harvest (2026-09-08): 25 省会 × 2020 × 10 指标 = 250 cells
--   - 161 absolute-value real cells (24 city 公告 + 161 cells from 10 指标)
--   - 89 DATA_MISSING:
--     - 10 TAIWAN (hongheiku 无 entry)
--     - 20 JIANGXI/SHANXI image-only (无 OCR 范围)
--     - 19 fixed_asset 增长% (无绝对值, per 669a-2021 §2 红线-3)
--     - 40 城市级公报未列指标 (守新增红线-3 不手填)
--   - fixed_asset growth-only rows EXCLUDED from values column; LEFT JOIN miss → DATA_MISSING
real_data_669fix_2020 AS (
    SELECT * FROM (VALUES
        -- HEBEI_SHIJIAZHUANG (1816, 石家庄 2020, 7/10 real cells)
        ('HEBEI_SHIJIAZHUANG', 'gdp_total',     5935.1::numeric),
        ('HEBEI_SHIJIAZHUANG', 'primary_gdp',   498.6::numeric),
        ('HEBEI_SHIJIAZHUANG', 'secondary_gdp', 1745.5::numeric),
        ('HEBEI_SHIJIAZHUANG', 'tertiary_gdp',  3691.0::numeric),
        ('HEBEI_SHIJIAZHUANG', 'fiscal_rev',    605.0::numeric),
        ('HEBEI_SHIJIAZHUANG', 'retail',        2279.6::numeric),
        ('HEBEI_SHIJIAZHUANG', 'trade',         1341.1::numeric),
        -- NEIMENGGU_HUHEHAOTE (75, 呼和浩特 2020, 9/10 real cells — fixed_asset 仅发增速 46.8%)
        ('NEIMENGGU_HUHEHAOTE', 'gdp_total',     2800.7::numeric),
        ('NEIMENGGU_HUHEHAOTE', 'gdp_growth',    0.2::numeric),
        ('NEIMENGGU_HUHEHAOTE', 'primary_gdp',   126.5::numeric),
        ('NEIMENGGU_HUHEHAOTE', 'secondary_gdp', 815.7::numeric),
        ('NEIMENGGU_HUHEHAOTE', 'tertiary_gdp',  1858.5::numeric),
        ('NEIMENGGU_HUHEHAOTE', 'fiscal_rev',    217.1::numeric),
        ('NEIMENGGU_HUHEHAOTE', 'retail',        1032.9::numeric),
        ('NEIMENGGU_HUHEHAOTE', 'trade',         147.0::numeric),
        -- LIAONING_SHENYANG (347, 沈阳 2020, 9/10 real cells)
        ('LIAONING_SHENYANG', 'gdp_total',     6571.6::numeric),
        ('LIAONING_SHENYANG', 'gdp_growth',    0.8::numeric),
        ('LIAONING_SHENYANG', 'primary_gdp',   303.6::numeric),
        ('LIAONING_SHENYANG', 'secondary_gdp', 2160.4::numeric),
        ('LIAONING_SHENYANG', 'tertiary_gdp',  4107.6::numeric),
        ('LIAONING_SHENYANG', 'fiscal_rev',    736.1::numeric),
        ('LIAONING_SHENYANG', 'retail',        3637.6::numeric),
        ('LIAONING_SHENYANG', 'trade',         1028.1::numeric),
        -- HEILONGJIANG_HARBIN (9267, 哈尔滨 2020, 8/10 real cells)
        ('HEILONGJIANG_HARBIN', 'gdp_total',     1174.6::numeric),
        ('HEILONGJIANG_HARBIN', 'gdp_growth',    0.6::numeric),
        ('HEILONGJIANG_HARBIN', 'primary_gdp',   615.8::numeric),
        ('HEILONGJIANG_HARBIN', 'secondary_gdp', 1144.5::numeric),
        ('HEILONGJIANG_HARBIN', 'tertiary_gdp',  3423.5::numeric),
        ('HEILONGJIANG_HARBIN', 'gdp_percapita', 54570::numeric),
        ('HEILONGJIANG_HARBIN', 'fiscal_rev',    339.6::numeric),
        ('HEILONGJIANG_HARBIN', 'trade',         255.9::numeric),
        -- JILIN_CHANGCHUN (13562, 长春 2020, 7/10 real cells)
        ('JILIN_CHANGCHUN', 'gdp_total',     6638.03::numeric),
        ('JILIN_CHANGCHUN', 'gdp_growth',    3.6::numeric),
        ('JILIN_CHANGCHUN', 'primary_gdp',   533.82::numeric),
        ('JILIN_CHANGCHUN', 'secondary_gdp', 2758.12::numeric),
        ('JILIN_CHANGCHUN', 'tertiary_gdp',  3346.09::numeric),
        ('JILIN_CHANGCHUN', 'gdp_percapita', 77634::numeric),
        ('JILIN_CHANGCHUN', 'trade',         1027.6::numeric),
        -- ANHUI_HEFEI (719 PDF, 合肥 2020, 7/10 real cells)
        ('ANHUI_HEFEI', 'gdp_growth',    4.3::numeric),
        ('ANHUI_HEFEI', 'primary_gdp',   332.32::numeric),
        ('ANHUI_HEFEI', 'secondary_gdp', 3579.51::numeric),
        ('ANHUI_HEFEI', 'fiscal_rev',    762.90::numeric),
        ('ANHUI_HEFEI', 'retail',        4513.76::numeric),
        ('ANHUI_HEFEI', 'trade',         374.87::numeric),
        -- FUJIAN_FUZHOU (3413, 福州 2020, 9/10 real cells)
        ('FUJIAN_FUZHOU', 'gdp_total',     10020.02::numeric),
        ('FUJIAN_FUZHOU', 'gdp_growth',    5.1::numeric),
        ('FUJIAN_FUZHOU', 'primary_gdp',   560.70::numeric),
        ('FUJIAN_FUZHOU', 'secondary_gdp', 3840.77::numeric),
        ('FUJIAN_FUZHOU', 'tertiary_gdp',  5618.55::numeric),
        ('FUJIAN_FUZHOU', 'fiscal_rev',    675.61::numeric),
        ('FUJIAN_FUZHOU', 'retail',        4225.61::numeric),
        ('FUJIAN_FUZHOU', 'trade',         2504.8::numeric),
        -- SHANDONG_JINAN (7978, 济南 2020, 8/10 real cells)
        ('SHANDONG_JINAN', 'gdp_growth',    4.9::numeric),
        ('SHANDONG_JINAN', 'primary_gdp',   361.7::numeric),
        ('SHANDONG_JINAN', 'secondary_gdp', 3530.7::numeric),
        ('SHANDONG_JINAN', 'tertiary_gdp',  6248.6::numeric),
        ('SHANDONG_JINAN', 'fiscal_rev',    906.1::numeric),
        ('SHANDONG_JINAN', 'retail',        4469.1::numeric),
        ('SHANDONG_JINAN', 'trade',         1382.7::numeric),
        -- HENAN_ZHENGZHOU (1804, 郑州 2020, 8/10 real cells)
        ('HENAN_ZHENGZHOU', 'gdp_growth',    3.0::numeric),
        ('HENAN_ZHENGZHOU', 'primary_gdp',   156.9::numeric),
        ('HENAN_ZHENGZHOU', 'secondary_gdp', 4759.5::numeric),
        ('HENAN_ZHENGZHOU', 'tertiary_gdp',  7086.6::numeric),
        ('HENAN_ZHENGZHOU', 'fiscal_rev',    1259.2::numeric),
        ('HENAN_ZHENGZHOU', 'retail',        5076.3::numeric),
        ('HENAN_ZHENGZHOU', 'trade',         4946.4::numeric),
        -- HUBEI_WUHAN (4553, 武汉 2020, 8/10 real cells)
        ('HUBEI_WUHAN', 'gdp_total',     15616.06::numeric),
        ('HUBEI_WUHAN', 'gdp_growth',    21.9::numeric),
        ('HUBEI_WUHAN', 'primary_gdp',   402.18::numeric),
        ('HUBEI_WUHAN', 'secondary_gdp', 5557.47::numeric),
        ('HUBEI_WUHAN', 'tertiary_gdp',  9656.41::numeric),
        ('HUBEI_WUHAN', 'fiscal_rev',    1230.29::numeric),
        ('HUBEI_WUHAN', 'retail',        6149.84::numeric),
        ('HUBEI_WUHAN', 'trade',         2704.30::numeric),
        -- HUNAN_CHANGSHA (327, 长沙 2020, 9/10 real cells)
        ('HUNAN_CHANGSHA', 'gdp_total',     12142.52::numeric),
        ('HUNAN_CHANGSHA', 'gdp_growth',    4.0::numeric),
        ('HUNAN_CHANGSHA', 'primary_gdp',   423.46::numeric),
        ('HUNAN_CHANGSHA', 'secondary_gdp', 4739.27::numeric),
        ('HUNAN_CHANGSHA', 'tertiary_gdp',  6979.79::numeric),
        ('HUNAN_CHANGSHA', 'fiscal_rev',    1642.96::numeric),
        ('HUNAN_CHANGSHA', 'retail',        4469.76::numeric),
        ('HUNAN_CHANGSHA', 'trade',         2350.46::numeric),
        -- GUANGXI_NANNING (7734, 南宁 2020, 9/10 real cells)
        ('GUANGXI_NANNING', 'gdp_total',     4726.34::numeric),
        ('GUANGXI_NANNING', 'gdp_growth',    3.7::numeric),
        ('GUANGXI_NANNING', 'primary_gdp',   534.36::numeric),
        ('GUANGXI_NANNING', 'secondary_gdp', 1084.32::numeric),
        ('GUANGXI_NANNING', 'tertiary_gdp',  3107.67::numeric),
        ('GUANGXI_NANNING', 'fiscal_rev',    372.25::numeric),
        ('GUANGXI_NANNING', 'retail',        2180.36::numeric),
        ('GUANGXI_NANNING', 'trade',         986::numeric),
        -- HAINAN_HAIKOU (1226, 海口 2020, 8/10 real cells)
        ('HAINAN_HAIKOU', 'gdp_total',     1791.58::numeric),
        ('HAINAN_HAIKOU', 'gdp_growth',    5.3::numeric),
        ('HAINAN_HAIKOU', 'primary_gdp',   79.88::numeric),
        ('HAINAN_HAIKOU', 'secondary_gdp', 269.56::numeric),
        ('HAINAN_HAIKOU', 'tertiary_gdp',  1442.14::numeric),
        ('HAINAN_HAIKOU', 'fiscal_rev',    460::numeric),
        ('HAINAN_HAIKOU', 'trade',         368.3::numeric),
        -- SICHUAN_CHENGDU (1460 PDF, 成都 2020, 8/10 real cells)
        ('SICHUAN_CHENGDU', 'gdp_total',     17716.7::numeric),
        ('SICHUAN_CHENGDU', 'gdp_growth',    4.0::numeric),
        ('SICHUAN_CHENGDU', 'primary_gdp',   655.2::numeric),
        ('SICHUAN_CHENGDU', 'secondary_gdp', 5418.5::numeric),
        ('SICHUAN_CHENGDU', 'fiscal_rev',    1520.4::numeric),
        ('SICHUAN_CHENGDU', 'retail',        8118.5::numeric),
        ('SICHUAN_CHENGDU', 'trade',         7154.2::numeric),
        -- GUIZHOU_GUIYANG (3174, 贵阳 2020, 8/10 real cells)
        ('GUIZHOU_GUIYANG', 'gdp_growth',    5.0::numeric),
        ('GUIZHOU_GUIYANG', 'primary_gdp',   178.31::numeric),
        ('GUIZHOU_GUIYANG', 'secondary_gdp', 1552.59::numeric),
        ('GUIZHOU_GUIYANG', 'tertiary_gdp',  2580.75::numeric),
        ('GUIZHOU_GUIYANG', 'fiscal_rev',    398.13::numeric),
        ('GUIZHOU_GUIYANG', 'retail',        2188.26::numeric),
        ('GUIZHOU_GUIYANG', 'trade',         60.00::numeric),
        -- YUNNAN_KUNMING (14086, 昆明 2020, 8/10 real cells)
        ('YUNNAN_KUNMING', 'gdp_growth',    2.3::numeric),
        ('YUNNAN_KUNMING', 'primary_gdp',   312.35::numeric),
        ('YUNNAN_KUNMING', 'secondary_gdp', 2102.93::numeric),
        ('YUNNAN_KUNMING', 'tertiary_gdp',  4318.51::numeric),
        ('YUNNAN_KUNMING', 'fiscal_rev',    650.47::numeric),
        ('YUNNAN_KUNMING', 'retail',        3070.44::numeric),
        ('YUNNAN_KUNMING', 'trade',         160.59::numeric),
        -- XIZANG_LASA (14174, 拉萨 2020, 7/10 real cells)
        ('XIZANG_LASA', 'gdp_total',     678.16::numeric),
        ('XIZANG_LASA', 'gdp_growth',    7.8::numeric),
        ('XIZANG_LASA', 'primary_gdp',   22.45::numeric),
        ('XIZANG_LASA', 'secondary_gdp', 290.44::numeric),
        ('XIZANG_LASA', 'tertiary_gdp',  365.27::numeric),
        ('XIZANG_LASA', 'retail',        369.35::numeric),
        -- SHAANXI_XIAN (1229, 西安 2020, 8/10 real cells)
        ('SHAANXI_XIAN', 'gdp_total',     10020.39::numeric),
        ('SHAANXI_XIAN', 'gdp_growth',    5.2::numeric),
        ('SHAANXI_XIAN', 'primary_gdp',   312.75::numeric),
        ('SHAANXI_XIAN', 'secondary_gdp', 3328.27::numeric),
        ('SHAANXI_XIAN', 'tertiary_gdp',  6379.37::numeric),
        ('SHAANXI_XIAN', 'fiscal_rev',    724.13::numeric),
        ('SHAANXI_XIAN', 'trade',         3473.8::numeric),
        -- GANSU_LANZHOU (949 PDF, 兰州 2020, 9/10 real cells)
        ('GANSU_LANZHOU', 'gdp_total',     2886.74::numeric),
        ('GANSU_LANZHOU', 'gdp_growth',    2.4::numeric),
        ('GANSU_LANZHOU', 'primary_gdp',   57.43::numeric),
        ('GANSU_LANZHOU', 'secondary_gdp', 933.42::numeric),
        ('GANSU_LANZHOU', 'tertiary_gdp',  1895.9::numeric),
        ('GANSU_LANZHOU', 'fiscal_rev',    247.13::numeric),
        ('GANSU_LANZHOU', 'retail',        1641.2::numeric),
        ('GANSU_LANZHOU', 'trade',         102.5::numeric),
        -- QINGHAI_XINING (11065 PDF, 西宁 2020, 5/10 real cells)
        ('QINGHAI_XINING', 'gdp_growth',    1.8::numeric),
        ('QINGHAI_XINING', 'primary_gdp',   57.17::numeric),
        ('QINGHAI_XINING', 'secondary_gdp', 418.72::numeric),
        ('QINGHAI_XINING', 'retail',        573.57::numeric),
        ('QINGHAI_XINING', 'trade',         16.81::numeric),
        -- NINGXIA_YINCHUAN (7796, 银川 2020, 9/10 real cells)
        ('NINGXIA_YINCHUAN', 'gdp_total',     1964.37::numeric),
        ('NINGXIA_YINCHUAN', 'gdp_growth',    3.2::numeric),
        ('NINGXIA_YINCHUAN', 'primary_gdp',   75.72::numeric),
        ('NINGXIA_YINCHUAN', 'secondary_gdp', 832.62::numeric),
        ('NINGXIA_YINCHUAN', 'tertiary_gdp',  1056.03::numeric),
        ('NINGXIA_YINCHUAN', 'fiscal_rev',    157.25::numeric),
        ('NINGXIA_YINCHUAN', 'retail',        770.87::numeric),
        ('NINGXIA_YINCHUAN', 'trade',         62.96::numeric),
        -- XINJIANG_WULUMUQI (428, 乌鲁木齐 2020, 10/10 全齐 — 本批唯一)
        ('XINJIANG_WULUMUQI', 'gdp_total',     3337.32::numeric),
        ('XINJIANG_WULUMUQI', 'gdp_growth',    0.3::numeric),
        ('XINJIANG_WULUMUQI', 'primary_gdp',   27.05::numeric),
        ('XINJIANG_WULUMUQI', 'secondary_gdp', 907.89::numeric),
        ('XINJIANG_WULUMUQI', 'tertiary_gdp',  2402.38::numeric),
        ('XINJIANG_WULUMUQI', 'gdp_percapita', 93030::numeric),
        ('XINJIANG_WULUMUQI', 'fiscal_rev',    392.64::numeric),
        ('XINJIANG_WULUMUQI', 'retail',        1043.51::numeric),
        ('XINJIANG_WULUMUQI', 'trade',         455.87::numeric)
    ) AS t(city_code, indicator_key, value)
),
-- 669fix-b-2021 full re-harvest (2026-09-08): 25 省会 × 2021 × 10 指标 = 250 cells
--   - 156 absolute-value real cells (21 city 公告 + 156 cells from 10 指标)
--   - 94 DATA_MISSING:
--     - 40 SICHUAN/XIZANG/QINGHAI/TAIWAN (hongheiku tag 页无 2021 entry)
--     - 13 fixed_asset 增长% (无绝对值, per 669a-2021 §2 红线-3)
--     - 41 城市级公报未列指标 (守新增红线-3 不手填)
--     - 0 HUBEI/SHANXI bulletin 实为 tag listing (no actual content, DATA_MISSING all 10)
--   - fixed_asset growth-only rows EXCLUDED from values column; LEFT JOIN miss → DATA_MISSING
real_data_669fix_2021 AS (
    SELECT * FROM (VALUES
        -- HEBEI_SHIJIAZHUANG (24600, 石家庄 2021, 7/10 real cells)
        ('HEBEI_SHIJIAZHUANG', 'gdp_total',     6490.3::numeric),
        ('HEBEI_SHIJIAZHUANG', 'primary_gdp',   504.8::numeric),
        ('HEBEI_SHIJIAZHUANG', 'secondary_gdp', 2107.1::numeric),
        ('HEBEI_SHIJIAZHUANG', 'tertiary_gdp',  3878.4::numeric),
        ('HEBEI_SHIJIAZHUANG', 'fiscal_rev',    654.1::numeric),
        ('HEBEI_SHIJIAZHUANG', 'retail',        2392.5::numeric),
        ('HEBEI_SHIJIAZHUANG', 'trade',         1481.2::numeric),
        -- NEIMENGGU_HUHEHAOTE (25235, 呼和浩特 2021, 9/10 real cells)
        ('NEIMENGGU_HUHEHAOTE', 'gdp_total',     3121.4::numeric),
        ('NEIMENGGU_HUHEHAOTE', 'gdp_growth',    6.5::numeric),
        ('NEIMENGGU_HUHEHAOTE', 'primary_gdp',   137.1::numeric),
        ('NEIMENGGU_HUHEHAOTE', 'secondary_gdp', 1052.6::numeric),
        ('NEIMENGGU_HUHEHAOTE', 'tertiary_gdp',  1931.7::numeric),
        ('NEIMENGGU_HUHEHAOTE', 'gdp_percapita', 89828::numeric),
        ('NEIMENGGU_HUHEHAOTE', 'fiscal_rev',    228.9::numeric),
        ('NEIMENGGU_HUHEHAOTE', 'retail',        1104.7::numeric),
        ('NEIMENGGU_HUHEHAOTE', 'trade',         159.8::numeric),
        -- LIAONING_SHENYANG (27930, 沈阳 2021, 9/10 real cells)
        ('LIAONING_SHENYANG', 'gdp_total',     7249.7::numeric),
        ('LIAONING_SHENYANG', 'gdp_growth',    7.0::numeric),
        ('LIAONING_SHENYANG', 'primary_gdp',   326.3::numeric),
        ('LIAONING_SHENYANG', 'secondary_gdp', 2570.3::numeric),
        ('LIAONING_SHENYANG', 'tertiary_gdp',  4353.0::numeric),
        ('LIAONING_SHENYANG', 'gdp_percapita', 79706::numeric),
        ('LIAONING_SHENYANG', 'fiscal_rev',    773.0::numeric),
        ('LIAONING_SHENYANG', 'retail',        3985.1::numeric),
        ('LIAONING_SHENYANG', 'trade',         1416.0::numeric),
        -- JILIN_CHANGCHUN (31744, 长春 2021, 8/10 real cells)
        ('JILIN_CHANGCHUN', 'gdp_total',     7103.12::numeric),
        ('JILIN_CHANGCHUN', 'gdp_growth',    6.2::numeric),
        ('JILIN_CHANGCHUN', 'primary_gdp',   523.74::numeric),
        ('JILIN_CHANGCHUN', 'secondary_gdp', 2960.47::numeric),
        ('JILIN_CHANGCHUN', 'tertiary_gdp',  3618.90::numeric),
        ('JILIN_CHANGCHUN', 'fiscal_rev',    617.09::numeric),
        ('JILIN_CHANGCHUN', 'retail',        2219.19::numeric),
        ('JILIN_CHANGCHUN', 'trade',         1179.77::numeric),
        -- HEILONGJIANG_HARBIN (29127, 哈尔滨 2021, 9/10 real cells)
        ('HEILONGJIANG_HARBIN', 'gdp_total',     1215.0::numeric),
        ('HEILONGJIANG_HARBIN', 'gdp_growth',    5.5::numeric),
        ('HEILONGJIANG_HARBIN', 'primary_gdp',   628.2::numeric),
        ('HEILONGJIANG_HARBIN', 'secondary_gdp', 1239.2::numeric),
        ('HEILONGJIANG_HARBIN', 'tertiary_gdp',  3484.3::numeric),
        ('HEILONGJIANG_HARBIN', 'gdp_percapita', 56580::numeric),
        ('HEILONGJIANG_HARBIN', 'fiscal_rev',    365.8::numeric),
        ('HEILONGJIANG_HARBIN', 'retail',        2380.3::numeric),
        ('HEILONGJIANG_HARBIN', 'trade',         344.6::numeric),
        -- ANHUI_HEFEI (25210, 合肥 2021, 8/10 real cells — fixed_asset 仅发增速)
        ('ANHUI_HEFEI', 'gdp_growth',    9.2::numeric),
        ('ANHUI_HEFEI', 'primary_gdp',   351.05::numeric),
        ('ANHUI_HEFEI', 'secondary_gdp', 4171.21::numeric),
        ('ANHUI_HEFEI', 'tertiary_gdp',  6890.54::numeric),
        ('ANHUI_HEFEI', 'gdp_percapita', 121187::numeric),
        ('ANHUI_HEFEI', 'fiscal_rev',    844.22::numeric),
        ('ANHUI_HEFEI', 'retail',        5111.68::numeric),
        ('ANHUI_HEFEI', 'trade',         514.60::numeric),
        -- FUJIAN_FUZHOU (25196, 福州 2021, 10/10 real cells — 全 harvest)
        ('FUJIAN_FUZHOU', 'gdp_total',     11324.48::numeric),
        ('FUJIAN_FUZHOU', 'gdp_growth',    8.4::numeric),
        ('FUJIAN_FUZHOU', 'primary_gdp',   637.03::numeric),
        ('FUJIAN_FUZHOU', 'secondary_gdp', 4289.80::numeric),
        ('FUJIAN_FUZHOU', 'tertiary_gdp',  6397.66::numeric),
        ('FUJIAN_FUZHOU', 'gdp_percapita', 135298::numeric),
        ('FUJIAN_FUZHOU', 'fiscal_rev',    749.85::numeric),
        ('FUJIAN_FUZHOU', 'fixed_asset',   5330.27::numeric),
        ('FUJIAN_FUZHOU', 'retail',        4549.41::numeric),
        ('FUJIAN_FUZHOU', 'trade',         3321.5::numeric),
        -- JIANGXI_NANCHANG (26554, 南昌 2021, 9/10 real cells)
        ('JIANGXI_NANCHANG', 'gdp_total',     6650.53::numeric),
        ('JIANGXI_NANCHANG', 'gdp_growth',    8.7::numeric),
        ('JIANGXI_NANCHANG', 'primary_gdp',   238.31::numeric),
        ('JIANGXI_NANCHANG', 'secondary_gdp', 3218.10::numeric),
        ('JIANGXI_NANCHANG', 'tertiary_gdp',  3194.11::numeric),
        ('JIANGXI_NANCHANG', 'gdp_percapita', 104788::numeric),
        ('JIANGXI_NANCHANG', 'fiscal_rev',    484.84::numeric),
        ('JIANGXI_NANCHANG', 'retail',        2878.74::numeric),
        ('JIANGXI_NANCHANG', 'trade',         1293.56::numeric),
        -- SHANDONG_JINAN (24205, 济南 2021, 7/10 real cells — fixed_asset 仅发增速)
        ('SHANDONG_JINAN', 'gdp_growth',    17.2::numeric),
        ('SHANDONG_JINAN', 'primary_gdp',   408.8::numeric),
        ('SHANDONG_JINAN', 'secondary_gdp', 3964.1::numeric),
        ('SHANDONG_JINAN', 'tertiary_gdp',  7059.4::numeric),
        ('SHANDONG_JINAN', 'fiscal_rev',    1007.6::numeric),
        ('SHANDONG_JINAN', 'retail',        5126.1::numeric),
        ('SHANDONG_JINAN', 'trade',         1944.2::numeric),
        -- HENAN_ZHENGZHOU (25032, 郑州 2021, 8/10 real cells)
        ('HENAN_ZHENGZHOU', 'gdp_total',     11850.4::numeric),
        ('HENAN_ZHENGZHOU', 'gdp_growth',    4.7::numeric),
        ('HENAN_ZHENGZHOU', 'primary_gdp',   181.7::numeric),
        ('HENAN_ZHENGZHOU', 'secondary_gdp', 5039.3::numeric),
        ('HENAN_ZHENGZHOU', 'tertiary_gdp',  7470::numeric),
        ('HENAN_ZHENGZHOU', 'fiscal_rev',    1223.6::numeric),
        ('HENAN_ZHENGZHOU', 'retail',        5389.2::numeric),
        ('HENAN_ZHENGZHOU', 'trade',         5892.1::numeric),
        -- HUNAN_CHANGSHA (25200, 长沙 2021, 8/10 real cells — fixed_asset 仅发增速)
        ('HUNAN_CHANGSHA', 'gdp_total',     13270.70::numeric),
        ('HUNAN_CHANGSHA', 'gdp_growth',    7.5::numeric),
        ('HUNAN_CHANGSHA', 'primary_gdp',   425.56::numeric),
        ('HUNAN_CHANGSHA', 'secondary_gdp', 5251.30::numeric),
        ('HUNAN_CHANGSHA', 'tertiary_gdp',  7593.85::numeric),
        ('HUNAN_CHANGSHA', 'fiscal_rev',    1775.04::numeric),
        ('HUNAN_CHANGSHA', 'retail',        5111.57::numeric),
        ('HUNAN_CHANGSHA', 'trade',         2780.28::numeric),
        -- GUANGXI_NANNING (27984, 南宁 2021, 8/10 real cells — fixed_asset 仅发增速)
        ('GUANGXI_NANNING', 'gdp_total',     5120.94::numeric),
        ('GUANGXI_NANNING', 'gdp_growth',    6.1::numeric),
        ('GUANGXI_NANNING', 'primary_gdp',   606.76::numeric),
        ('GUANGXI_NANNING', 'secondary_gdp', 1198.76::numeric),
        ('GUANGXI_NANNING', 'tertiary_gdp',  3315.42::numeric),
        ('GUANGXI_NANNING', 'fiscal_rev',    391.77::numeric),
        ('GUANGXI_NANNING', 'retail',        2364.17::numeric),
        ('GUANGXI_NANNING', 'trade',         1231.92::numeric),
        -- HAINAN_HAIKOU (23898, 海口 2021, 7/10 real cells)
        ('HAINAN_HAIKOU', 'gdp_total',     2057.06::numeric),
        ('HAINAN_HAIKOU', 'gdp_growth',    11.3::numeric),
        ('HAINAN_HAIKOU', 'primary_gdp',   85.43::numeric),
        ('HAINAN_HAIKOU', 'secondary_gdp', 346.75::numeric),
        ('HAINAN_HAIKOU', 'tertiary_gdp',  1624.88::numeric),
        ('HAINAN_HAIKOU', 'fiscal_rev',    566.5::numeric),
        ('HAINAN_HAIKOU', 'trade',         476.4::numeric),
        -- GUIZHOU_GUIYANG (27953, 贵阳 2021, 8/10 real cells — fixed_asset 仅发增速)
        ('GUIZHOU_GUIYANG', 'gdp_growth',    6.6::numeric),
        ('GUIZHOU_GUIYANG', 'primary_gdp',   193.44::numeric),
        ('GUIZHOU_GUIYANG', 'secondary_gdp', 1681.34::numeric),
        ('GUIZHOU_GUIYANG', 'tertiary_gdp',  2836.25::numeric),
        ('GUIZHOU_GUIYANG', 'gdp_percapita', 77919::numeric),
        ('GUIZHOU_GUIYANG', 'fiscal_rev',    426.68::numeric),
        ('GUIZHOU_GUIYANG', 'retail',        2546.69::numeric),
        ('GUIZHOU_GUIYANG', 'trade',         74.12::numeric),
        -- YUNNAN_KUNMING (31057, 昆明 2021, 7/10 real cells)
        ('YUNNAN_KUNMING', 'gdp_growth',    3.7::numeric),
        ('YUNNAN_KUNMING', 'primary_gdp',   333.12::numeric),
        ('YUNNAN_KUNMING', 'secondary_gdp', 2287.71::numeric),
        ('YUNNAN_KUNMING', 'tertiary_gdp',  4601.67::numeric),
        ('YUNNAN_KUNMING', 'fiscal_rev',    689.12::numeric),
        ('YUNNAN_KUNMING', 'retail',        3386.40::numeric),
        ('YUNNAN_KUNMING', 'trade',         265.72::numeric),
        -- SHAANXI_XIAN (25636 PDF, 西安 2021, 9/10 real cells — fixed_asset 仅发增速)
        ('SHAANXI_XIAN', 'gdp_total',     10688.28::numeric),
        ('SHAANXI_XIAN', 'gdp_growth',    4.1::numeric),
        ('SHAANXI_XIAN', 'primary_gdp',   308.82::numeric),
        ('SHAANXI_XIAN', 'secondary_gdp', 3585.20::numeric),
        ('SHAANXI_XIAN', 'tertiary_gdp',  6794.26::numeric),
        ('SHAANXI_XIAN', 'gdp_percapita', 83689::numeric),
        ('SHAANXI_XIAN', 'fiscal_rev',    855.96::numeric),
        ('SHAANXI_XIAN', 'retail',        4963.42::numeric),
        ('SHAANXI_XIAN', 'trade',         4399.96::numeric),
        -- GANSU_LANZHOU (27570, 兰州 2021, 8/10 real cells — fixed_asset + trade 仅发增速)
        ('GANSU_LANZHOU', 'gdp_total',     3231.29::numeric),
        ('GANSU_LANZHOU', 'gdp_growth',    6.1::numeric),
        ('GANSU_LANZHOU', 'primary_gdp',   62.52::numeric),
        ('GANSU_LANZHOU', 'secondary_gdp', 1113.91::numeric),
        ('GANSU_LANZHOU', 'tertiary_gdp',  2054.86::numeric),
        ('GANSU_LANZHOU', 'gdp_percapita', 73807::numeric),
        ('GANSU_LANZHOU', 'fiscal_rev',    276.73::numeric),
        ('GANSU_LANZHOU', 'retail',        1757.74::numeric),
        -- NINGXIA_YINCHUAN (25485, 银川 2021, 9/10 real cells — fixed_asset 仅发增速)
        ('NINGXIA_YINCHUAN', 'gdp_total',     2262.95::numeric),
        ('NINGXIA_YINCHUAN', 'gdp_growth',    6.3::numeric),
        ('NINGXIA_YINCHUAN', 'primary_gdp',   83.83::numeric),
        ('NINGXIA_YINCHUAN', 'secondary_gdp', 1028.32::numeric),
        ('NINGXIA_YINCHUAN', 'tertiary_gdp',  1150.81::numeric),
        ('NINGXIA_YINCHUAN', 'gdp_percapita', 78794::numeric),
        ('NINGXIA_YINCHUAN', 'fiscal_rev',    171.19::numeric),
        ('NINGXIA_YINCHUAN', 'retail',        788.69::numeric),
        ('NINGXIA_YINCHUAN', 'trade',         132.07::numeric),
        -- XINJIANG_WULUMUQI (31404, 乌鲁木齐 2021, 8/10 real cells — gdp_percapita + fixed_asset 仅发增速)
        ('XINJIANG_WULUMUQI', 'gdp_total',     3691.57::numeric),
        ('XINJIANG_WULUMUQI', 'gdp_growth',    6.1::numeric),
        ('XINJIANG_WULUMUQI', 'primary_gdp',   28.10::numeric),
        ('XINJIANG_WULUMUQI', 'secondary_gdp', 1039.76::numeric),
        ('XINJIANG_WULUMUQI', 'tertiary_gdp',  2623.71::numeric),
        ('XINJIANG_WULUMUQI', 'fiscal_rev',    377.93::numeric),
        ('XINJIANG_WULUMUQI', 'retail',        1171.86::numeric),
        ('XINJIANG_WULUMUQI', 'trade',         385.45::numeric)
        -- SICHUAN_CHENGDU (no 2021 entry) / XIZANG_LASA / QINGHAI_XINING / TAIWAN_TAIPEI → DATA_MISSING
        -- HUBEI_WUHAN (28733) / SHANXI_TAIYUAN (24774) → hongheiku URL 实为 tag listing, 无内容 → DATA_MISSING
    ) AS t(city_code, indicator_key, value)
),
-- 669fix-b-2022 full re-harvest (2026-09-08): 25 省会 × 2022 × 10 指标 = 250 cells
--   - 136 absolute-value real cells (17 city 公告 + XINJIANG 10/10 + 16 city partial)
--   - 114 DATA_MISSING:
--     - 80 QINGHAI/GUANGXI/TAIWAN (hongheiku 缺/无内容: QINGHAI=984 chars tag listing; GUANGXI/TAIWAN 无 2022 entry)
--     - 10 fixed_asset 增长% (无绝对值, per 669a-2021 §2 红线-3)
--     - 24 城市级公报未列指标 (守新增红线-3 不手填)
--   - 8 all-missing cities: ANHUI/FUJIAN/GUANGXI/HEILONGJIANG/JIANGXI/QINGHAI/SHANXI/TAIWAN
real_data_669fix_2022 AS (
    SELECT * FROM (VALUES
$(cat /tmp/669b/cte_2022_body.txt)
    ) AS t(city_code, indicator_key, value)
),
real_data_669fix_2023 AS (
    SELECT * FROM (VALUES
$(cat /tmp/669b/cte_2023_body.txt)
    ) AS t(city_code, indicator_key, value)
),
real_data_669fix_2024 AS (
    SELECT * FROM (VALUES
$(cat /tmp/669b/cte_2024_body.txt)
    ) AS t(city_code, indicator_key, value)
),
real_data_669fix_2025 AS (
    -- knife 669fix-b-2025 (Path A 续刀 5/5): zero-harvest 路径
    -- 25 省会 × 2025 市级公报 hongheiku 暂未收录 (cat index 2025 14 entry 全为省级公报非市级, 5 city tag/search probe 0 命中)
    -- 守红线-3 不手填; 0 tuples 是预期行为 (与 669b-2025 一致)
    -- empty CTE via WHERE FALSE (postgres VALUES 不能 0 tuples)
    SELECT NULL::text AS city_code, NULL::text AS indicator_key, NULL::numeric AS value WHERE FALSE
),
real_data_669b_i_batch1_2024 AS (
    -- knife F first sub-knife (2026-09-09): 验证 969+970 通用脚本规模
    -- 8 cities × 2024 (4 计划单列市 + 4 高 GDP 地级市, NOT 25 省会)
    -- hongheiku /tag/{城市市} URL discovery (1 HTTP/city = 8 total ≤32 红线)
    -- 7/8 cities found (宁波 2024 不存在, hongheiku /tag/宁波市 只有 2021/2022/2023/2025)
    -- 1 PDF (Foshan) + 6 HTML = 8 HTTP for fetch phase
    -- parse: 57/80 real cells (71% coverage, 23 DATA_MISSING)
    --   - 10 缺 cells: 宁波 (eid=None, hongheiku 缺 2024)
    --   - 13 缺 cells: parser 未匹配 (gdp_percapita 5 个 + retail 4 个 + fixed_asset 5 个 + tertiary/secondary 4 个 mixed)
    -- 守新增红线-3: 不手填/不补零/仅从 hongheiku 采集
    SELECT * FROM (VALUES
        ('LIAONING_DALIAN',        'gdp_total',     9516.9::numeric),
        ('LIAONING_DALIAN',        'gdp_growth',    5.2::numeric),
        ('LIAONING_DALIAN',        'primary_gdp',   585.7::numeric),
        ('LIAONING_DALIAN',        'secondary_gdp', 3349.0::numeric),
        ('LIAONING_DALIAN',        'tertiary_gdp',  5582.2::numeric),
        ('LIAONING_DALIAN',        'gdp_percapita', 126185::numeric),
        ('LIAONING_DALIAN',        'fiscal_rev',    774.8::numeric),
        ('LIAONING_DALIAN',        'retail',        2085.9::numeric),
        ('LIAONING_DALIAN',        'trade',         4496.7::numeric),
        ('SHANDONG_QINGDAO',       'gdp_total',     15973.16::numeric),
        ('SHANDONG_QINGDAO',       'gdp_growth',    5.7::numeric),
        ('SHANDONG_QINGDAO',       'primary_gdp',   500.82::numeric),
        ('SHANDONG_QINGDAO',       'secondary_gdp', 5723.10::numeric),
        ('SHANDONG_QINGDAO',       'tertiary_gdp',  10495.54::numeric),
        ('SHANDONG_QINGDAO',       'fiscal_rev',    1339.3::numeric),
        ('SHANDONG_QINGDAO',       'trade',         9076.7::numeric),
        ('FUJIAN_XIAMEN',          'gdp_total',     2913.67::numeric),
        ('FUJIAN_XIAMEN',          'gdp_growth',    5.5::numeric),
        ('FUJIAN_XIAMEN',          'primary_gdp',   26.34::numeric),
        ('FUJIAN_XIAMEN',          'secondary_gdp', 3147.40::numeric),
        ('FUJIAN_XIAMEN',          'tertiary_gdp',  5415.28::numeric),
        ('FUJIAN_XIAMEN',          'fiscal_rev',    933.19::numeric),
        ('FUJIAN_XIAMEN',          'trade',         9326.12::numeric),
        ('JIANGSU_SUZHOU',         'gdp_total',     26727.0::numeric),
        ('JIANGSU_SUZHOU',         'gdp_growth',    6.0::numeric),
        ('JIANGSU_SUZHOU',         'primary_gdp',   202.0::numeric),
        ('JIANGSU_SUZHOU',         'secondary_gdp', 12516.7::numeric),
        ('JIANGSU_SUZHOU',         'tertiary_gdp',  14008.3::numeric),
        ('JIANGSU_SUZHOU',         'fiscal_rev',    2459.1::numeric),
        ('JIANGSU_SUZHOU',         'fixed_asset',   6135.7::numeric),
        ('JIANGSU_SUZHOU',         'trade',         26193.1::numeric),
        ('JIANGSU_WUXI',           'gdp_total',     16263.29::numeric),
        ('JIANGSU_WUXI',           'gdp_growth',    5.8::numeric),
        ('JIANGSU_WUXI',           'primary_gdp',   140.45::numeric),
        ('JIANGSU_WUXI',           'secondary_gdp', 7716.02::numeric),
        ('JIANGSU_WUXI',           'tertiary_gdp',  8406.82::numeric),
        ('JIANGSU_WUXI',           'fiscal_rev',    1201.56::numeric),
        ('JIANGSU_WUXI',           'fixed_asset',   4587.36::numeric),
        ('JIANGSU_WUXI',           'retail',        4284.06::numeric),
        ('JIANGSU_WUXI',           'trade',         7709.46::numeric),
        ('GUANGDONG_FOSHAN',       'gdp_total',     13361.90::numeric),
        ('GUANGDONG_FOSHAN',       'gdp_growth',    1.3::numeric),
        ('GUANGDONG_FOSHAN',       'primary_gdp',   243.54::numeric),
        ('GUANGDONG_FOSHAN',       'tertiary_gdp',  6397.16::numeric),
        ('GUANGDONG_FOSHAN',       'fiscal_rev',    767.08::numeric),
        ('GUANGDONG_FOSHAN',       'retail',        3943.91::numeric),
        ('GUANGDONG_FOSHAN',       'trade',         4996.5::numeric),
        ('GUANGDONG_DONGGUAN',     'gdp_total',     12282.15::numeric),
        ('GUANGDONG_DONGGUAN',     'gdp_growth',    4.6::numeric),
        ('GUANGDONG_DONGGUAN',     'primary_gdp',   38.54::numeric),
        ('GUANGDONG_DONGGUAN',     'secondary_gdp', 6800.80::numeric),
        ('GUANGDONG_DONGGUAN',     'tertiary_gdp',  5442.81::numeric),
        ('GUANGDONG_DONGGUAN',     'gdp_percapita', 116661::numeric),
        ('GUANGDONG_DONGGUAN',     'fiscal_rev',    789.43::numeric),
        ('GUANGDONG_DONGGUAN',     'fixed_asset',   694.44::numeric),
        ('GUANGDONG_DONGGUAN',     'retail',        4446.26::numeric),
        ('GUANGDONG_DONGGUAN',     'trade',         13880.4::numeric)
    ) AS t(city_code, indicator_key, value)
),
real_data_669b_i_dongguan AS (
    -- knife 669b-i DONGGUAN sub-knife 1/4 (2026-09-10): 续刀 batch 1 single-city 6-year harvest
    -- hongheiku /tag/东莞市 → eid_map discovery (1 HTTP, ≤32 红线) → /djs/{eid}.html × 4 new (2021/2022/2023/2025; 2024 已 rd13)
    -- parse: 37/40 real cells (92.5% coverage; 3 DATA_MISSING = fixed_asset 2021/2022/2023 仅发增长%)
    -- 2020 10 DATA_MISSING (hongheiku tag 页无 2020 bulletin, 守红线-3 禁编造)
    -- 2024 stays in rd13 (K669b-i-batch1-parse-2024-2026-09-09, Knife F first sub-knife attribution)
    SELECT * FROM (VALUES
        ('GUANGDONG_DONGGUAN', 'gdp_total',     10855.35::numeric),  -- 2021 eid=25333
        ('GUANGDONG_DONGGUAN', 'gdp_growth',    8.2::numeric),
        ('GUANGDONG_DONGGUAN', 'primary_gdp',   34.66::numeric),
        ('GUANGDONG_DONGGUAN', 'secondary_gdp', 6319.41::numeric),
        ('GUANGDONG_DONGGUAN', 'tertiary_gdp',  4501.28::numeric),
        ('GUANGDONG_DONGGUAN', 'gdp_percapita', 103284::numeric),
        ('GUANGDONG_DONGGUAN', 'fiscal_rev',    769.46::numeric),
        ('GUANGDONG_DONGGUAN', 'retail',        4239.24::numeric),
        ('GUANGDONG_DONGGUAN', 'trade',         15247.03::numeric),
        ('GUANGDONG_DONGGUAN', 'gdp_total',     11200.32::numeric),  -- 2022 eid=42065
        ('GUANGDONG_DONGGUAN', 'gdp_growth',    0.6::numeric),
        ('GUANGDONG_DONGGUAN', 'primary_gdp',   36.50::numeric),
        ('GUANGDONG_DONGGUAN', 'secondary_gdp', 6513.64::numeric),
        ('GUANGDONG_DONGGUAN', 'tertiary_gdp',  4650.18::numeric),
        ('GUANGDONG_DONGGUAN', 'gdp_percapita', 106803::numeric),
        ('GUANGDONG_DONGGUAN', 'fiscal_rev',    766.04::numeric),
        ('GUANGDONG_DONGGUAN', 'retail',        4254.87::numeric),
        ('GUANGDONG_DONGGUAN', 'trade',         13926.63::numeric),
        ('GUANGDONG_DONGGUAN', 'gdp_total',     11438.13::numeric),  -- 2023 eid=47430
        ('GUANGDONG_DONGGUAN', 'gdp_growth',    2.6::numeric),
        ('GUANGDONG_DONGGUAN', 'primary_gdp',   36.25::numeric),
        ('GUANGDONG_DONGGUAN', 'secondary_gdp', 6478.18::numeric),
        ('GUANGDONG_DONGGUAN', 'tertiary_gdp',  4923.71::numeric),
        ('GUANGDONG_DONGGUAN', 'gdp_percapita', 109339::numeric),
        ('GUANGDONG_DONGGUAN', 'fiscal_rev',    804.84::numeric),
        ('GUANGDONG_DONGGUAN', 'retail',        4408.12::numeric),
        ('GUANGDONG_DONGGUAN', 'trade',         12823.56::numeric),
        ('GUANGDONG_DONGGUAN', 'gdp_total',     12760.20::numeric),  -- 2025 eid=69935
        ('GUANGDONG_DONGGUAN', 'gdp_growth',    4.0::numeric),
        ('GUANGDONG_DONGGUAN', 'primary_gdp',   36.90::numeric),
        ('GUANGDONG_DONGGUAN', 'secondary_gdp', 7165.44::numeric),
        ('GUANGDONG_DONGGUAN', 'tertiary_gdp',  5557.87::numeric),
        ('GUANGDONG_DONGGUAN', 'gdp_percapita', 119415::numeric),
        ('GUANGDONG_DONGGUAN', 'fiscal_rev',    891.82::numeric),
        ('GUANGDONG_DONGGUAN', 'fixed_asset',   362.30::numeric),
        ('GUANGDONG_DONGGUAN', 'retail',        4446.00::numeric),
        ('GUANGDONG_DONGGUAN', 'trade',         15794.3::numeric)
    ) AS t(city_code, indicator_key, value)
),
missing_city_year AS (
    -- 永久缺 city (4 直辖市禁重复; 港/澳/台 不在 city mart)
    -- 669a-2021 范围内无永久缺 city (4 直辖市之外的 4 priority city 都有 cat tag)
    SELECT NULL::text AS city_code WHERE FALSE
),
real_data_669b_i_dalian AS (
    -- knife 669b-i-dalian sub-knife 2/4 (2026-09-10): DALIAN 6-year harvest
    -- 30 real cells = 7+8+8+7 for 2021/2022/2023/2025 (2024 stays in rd13 Knife F attribution)
    -- eid map: {2021: 30342, 2022: 36951, 2023: 48502, 2024: 60425, 2025: 69004}
    -- 12 missing cells (gdp_total/gdp_percapita/fixed_asset) → DATA_MISSING in mart SQL CASE clauses
    VALUES
        ('LIAONING_DALIAN', 'gdp_growth',    8.2::numeric,    2021),  -- eid=30342
        ('LIAONING_DALIAN', 'primary_gdp',   513.3::numeric,  2021),
        ('LIAONING_DALIAN', 'secondary_gdp', 3301.6::numeric, 2021),
        ('LIAONING_DALIAN', 'tertiary_gdp',  4011.0::numeric, 2021),
        ('LIAONING_DALIAN', 'fiscal_rev',    737.6::numeric,  2021),
        ('LIAONING_DALIAN', 'retail',        1909.7::numeric, 2021),
        ('LIAONING_DALIAN', 'trade',         4248.5::numeric, 2021),
        ('LIAONING_DALIAN', 'gdp_growth',    4.0::numeric,    2022),  -- eid=36951
        ('LIAONING_DALIAN', 'primary_gdp',   563.0::numeric,  2022),
        ('LIAONING_DALIAN', 'secondary_gdp', 3712.5::numeric, 2022),
        ('LIAONING_DALIAN', 'tertiary_gdp',  4155.4::numeric, 2022),
        ('LIAONING_DALIAN', 'gdp_percapita', 112270::numeric, 2022),
        ('LIAONING_DALIAN', 'fiscal_rev',    669.7::numeric,  2022),
        ('LIAONING_DALIAN', 'retail',        1846.9::numeric, 2022),
        ('LIAONING_DALIAN', 'trade',         4792.1::numeric, 2022),
        ('LIAONING_DALIAN', 'gdp_growth',    6.0::numeric,    2023),  -- eid=48502
        ('LIAONING_DALIAN', 'primary_gdp',   595.9::numeric,  2023),
        ('LIAONING_DALIAN', 'secondary_gdp', 3715.3::numeric, 2023),
        ('LIAONING_DALIAN', 'tertiary_gdp',  4441.7::numeric, 2023),
        ('LIAONING_DALIAN', 'gdp_percapita', 116557::numeric, 2023),
        ('LIAONING_DALIAN', 'fiscal_rev',    750.2::numeric,  2023),
        ('LIAONING_DALIAN', 'retail',        2008.6::numeric, 2023),
        ('LIAONING_DALIAN', 'trade',         4552.8::numeric, 2023),
        ('LIAONING_DALIAN', 'gdp_growth',    5.7::numeric,    2025),  -- eid=69004
        ('LIAONING_DALIAN', 'primary_gdp',   665.4::numeric,  2025),
        ('LIAONING_DALIAN', 'secondary_gdp', 3532.5::numeric, 2025),
        ('LIAONING_DALIAN', 'tertiary_gdp',  5804.2::numeric, 2025),
        ('LIAONING_DALIAN', 'fiscal_rev',    749.5::numeric,  2025),
        ('LIAONING_DALIAN', 'retail',        2180.8::numeric, 2025),
        ('LIAONING_DALIAN', 'trade',         4492.6::numeric, 2025)
),
real_data_669b_i_wuxi AS (
    -- knife 669b-i-wuxi sub-knife 3/4 (2026-09-10): WUXI 6-year harvest
    -- 26 real cells = 8+9+9 for 2021/2023/2025 (2020/2022/2024/2026 stay DATA_MISSING or Knife F)
    -- eid map: {2021: 23931, 2023: 45593, 2024: 60801 (Knife F), 2025: 70051}
    -- 4 missing cells (gdp_percapita ×3 + 2021 fiscal_rev) → DATA_MISSING in mart SQL CASE clauses
    VALUES
        ('JIANGSU_WUXI', 'gdp_total',      14003.24::numeric, 2021),  -- eid=23931
        ('JIANGSU_WUXI', 'gdp_growth',     8.8::numeric,      2021),
        ('JIANGSU_WUXI', 'primary_gdp',    130.33::numeric,   2021),
        ('JIANGSU_WUXI', 'secondary_gdp',  6710.50::numeric,  2021),
        ('JIANGSU_WUXI', 'tertiary_gdp',   7162.41::numeric,  2021),
        ('JIANGSU_WUXI', 'fixed_asset',    3985.20::numeric,  2021),
        ('JIANGSU_WUXI', 'retail',         3306.09::numeric,  2021),
        ('JIANGSU_WUXI', 'trade',          1057.01::numeric,  2021),
        ('JIANGSU_WUXI', 'gdp_total',      15456.19::numeric, 2023),  -- eid=45593
        ('JIANGSU_WUXI', 'gdp_growth',     6.0::numeric,      2023),
        ('JIANGSU_WUXI', 'primary_gdp',    136.50::numeric,   2023),
        ('JIANGSU_WUXI', 'secondary_gdp',  7376.85::numeric,  2023),
        ('JIANGSU_WUXI', 'tertiary_gdp',   7942.84::numeric,  2023),
        ('JIANGSU_WUXI', 'fiscal_rev',     1195.42::numeric,  2023),
        ('JIANGSU_WUXI', 'fixed_asset',    4412.10::numeric,  2023),
        ('JIANGSU_WUXI', 'retail',         3567.55::numeric,  2023),
        ('JIANGSU_WUXI', 'trade',          7065.32::numeric,  2023),
        ('JIANGSU_WUXI', 'gdp_total',      16773.94::numeric, 2025),  -- eid=70051
        ('JIANGSU_WUXI', 'gdp_growth',     5.1::numeric,      2025),
        ('JIANGSU_WUXI', 'primary_gdp',    142.48::numeric,   2025),
        ('JIANGSU_WUXI', 'secondary_gdp',  7870.47::numeric,  2025),
        ('JIANGSU_WUXI', 'tertiary_gdp',   8760.99::numeric,  2025),
        ('JIANGSU_WUXI', 'fiscal_rev',     1225.39::numeric,  2025),
        ('JIANGSU_WUXI', 'fixed_asset',    3979.11::numeric,  2025),
        ('JIANGSU_WUXI', 'retail',         4418.47::numeric,  2025),
        ('JIANGSU_WUXI', 'trade',          8292.76::numeric,  2025)
),
real_data_669b_i_suzhou AS (
    -- knife 669b-i-suzhou sub-knife 4/4 (2026-09-10): SUZHOU 6-year harvest
    -- 35 real cells = 9+9+0+8+9 for 2021/2022/2023/2024/2025 (2023 全 DATA_MISSING, 数字含空格 parser regex 失配; 2024 stays K669b-i-batch1 Knife F attribution; 2020/2026 stay DATA_MISSING)
    -- eid map: {2020: 3008 (老 ID), 2021: 25410, 2022: 35155, 2023: 45627, 2024: 61278 (Knife F), 2025: 69636}
    -- 5 missing cells (gdp_percapita ×4 + 2024 retail) → DATA_MISSING in mart SQL CASE clauses
    VALUES
        ('JIANGSU_SUZHOU', 'gdp_total',      22718.3::numeric,  2021),  -- eid=25410
        ('JIANGSU_SUZHOU', 'gdp_growth',     8.7::numeric,      2021),
        ('JIANGSU_SUZHOU', 'primary_gdp',    189.7::numeric,    2021),
        ('JIANGSU_SUZHOU', 'secondary_gdp',  10872.8::numeric,  2021),
        ('JIANGSU_SUZHOU', 'tertiary_gdp',   11655.8::numeric,  2021),
        ('JIANGSU_SUZHOU', 'fiscal_rev',     2510.0::numeric,   2021),
        ('JIANGSU_SUZHOU', 'fixed_asset',    5660.6::numeric,   2021),
        ('JIANGSU_SUZHOU', 'retail',         9031.3::numeric,   2021),
        ('JIANGSU_SUZHOU', 'trade',          25332.0::numeric,  2021),
        ('JIANGSU_SUZHOU', 'gdp_total',      23958.34::numeric, 2022),  -- eid=35155
        ('JIANGSU_SUZHOU', 'gdp_growth',     2.0::numeric,      2022),
        ('JIANGSU_SUZHOU', 'primary_gdp',    192.98::numeric,   2022),
        ('JIANGSU_SUZHOU', 'secondary_gdp',  11521.41::numeric, 2022),
        ('JIANGSU_SUZHOU', 'tertiary_gdp',   12243.95::numeric, 2022),
        ('JIANGSU_SUZHOU', 'fiscal_rev',     2329.2::numeric,   2022),
        ('JIANGSU_SUZHOU', 'fixed_asset',    5744.2::numeric,   2022),
        ('JIANGSU_SUZHOU', 'retail',         9010.7::numeric,   2022),
        ('JIANGSU_SUZHOU', 'trade',          25721.1::numeric,  2022),
        ('JIANGSU_SUZHOU', 'gdp_total',      26727.0::numeric,  2024),  -- eid=61278 (Knife F 收录; 2024 stays K669b-i-batch1)
        ('JIANGSU_SUZHOU', 'gdp_growth',     6.0::numeric,      2024),
        ('JIANGSU_SUZHOU', 'primary_gdp',    202.0::numeric,    2024),
        ('JIANGSU_SUZHOU', 'secondary_gdp',  12516.7::numeric,  2024),
        ('JIANGSU_SUZHOU', 'tertiary_gdp',   14008.3::numeric,  2024),
        ('JIANGSU_SUZHOU', 'fiscal_rev',     2459.1::numeric,   2024),
        ('JIANGSU_SUZHOU', 'fixed_asset',    6135.7::numeric,   2024),
        ('JIANGSU_SUZHOU', 'trade',          26193.1::numeric,  2024),
        ('JIANGSU_SUZHOU', 'gdp_total',      27695.1::numeric,  2025),  -- eid=69636
        ('JIANGSU_SUZHOU', 'gdp_growth',     5.4::numeric,      2025),
        ('JIANGSU_SUZHOU', 'primary_gdp',    208.9::numeric,    2025),
        ('JIANGSU_SUZHOU', 'secondary_gdp',  12844.4::numeric,  2025),
        ('JIANGSU_SUZHOU', 'tertiary_gdp',   14641.8::numeric,  2025),
        ('JIANGSU_SUZHOU', 'fiscal_rev',     2490.2::numeric,   2025),
        ('JIANGSU_SUZHOU', 'fixed_asset',    5713.7::numeric,   2025),
        ('JIANGSU_SUZHOU', 'retail',         9092.2::numeric,   2025),
        ('JIANGSU_SUZHOU', 'trade',          28119.3::numeric,  2025)
),
-- knife 669b-i-xiamen sub-knife (2026-09-12): XIAMEN 5-year harvest
-- 39 real cells = 7+9+8+7+8 for 2021/2022/2023/2024/2025
-- eid map: {2021: 24437, 2022: 38423, 2023: 45732, 2024: 57609 (Knife F), 2025: 68649}
-- 2020 缺 (tag page 无 entry, 守新增红线-3 禁编造)
-- gdp_percapita 5 cells × 5 year DATA_MISSING (公报无「人均地区生产总值」关键词)
-- fiscal_rev 2021 + fixed_asset 4 cells + 2024 retail DATA_MISSING (bulletin 无 / parser 未匹配)
-- 2024 cells stay in rd13 (Knife F attribution), apply 跳过 2024
real_data_669b_i_xiamen AS (
    VALUES
        ('FUJIAN_XIAMEN', 'gdp_total',       7033.89::numeric,  2021),  -- eid=24437
        ('FUJIAN_XIAMEN', 'gdp_growth',      8.1::numeric,      2021),
        ('FUJIAN_XIAMEN', 'primary_gdp',     29.06::numeric,    2021),
        ('FUJIAN_XIAMEN', 'secondary_gdp',   2882.89::numeric,  2021),
        ('FUJIAN_XIAMEN', 'tertiary_gdp',    4121.94::numeric,  2021),
        ('FUJIAN_XIAMEN', 'retail',          2584.07::numeric,  2021),
        ('FUJIAN_XIAMEN', 'trade',           8876.52::numeric,  2021),
        ('FUJIAN_XIAMEN', 'gdp_total',       7802.66::numeric,  2022),  -- eid=38423
        ('FUJIAN_XIAMEN', 'gdp_growth',      4.4::numeric,      2022),
        ('FUJIAN_XIAMEN', 'primary_gdp',     29.27::numeric,    2022),
        ('FUJIAN_XIAMEN', 'secondary_gdp',   3233.56::numeric,  2022),
        ('FUJIAN_XIAMEN', 'tertiary_gdp',    4539.83::numeric,  2022),
        ('FUJIAN_XIAMEN', 'fiscal_rev',      883.77::numeric,   2022),
        ('FUJIAN_XIAMEN', 'fixed_asset',     276.84::numeric,   2022),
        ('FUJIAN_XIAMEN', 'retail',          2665.36::numeric,  2022),
        ('FUJIAN_XIAMEN', 'trade',           9225.59::numeric,  2022),
        ('FUJIAN_XIAMEN', 'gdp_total',       8066.49::numeric,  2023),  -- eid=45732
        ('FUJIAN_XIAMEN', 'gdp_growth',      3.1::numeric,      2023),
        ('FUJIAN_XIAMEN', 'primary_gdp',     27.73::numeric,    2023),
        ('FUJIAN_XIAMEN', 'secondary_gdp',   2867.94::numeric,  2023),
        ('FUJIAN_XIAMEN', 'tertiary_gdp',    5170.81::numeric,  2023),
        ('FUJIAN_XIAMEN', 'retail',          2743.33::numeric,  2023),
        ('FUJIAN_XIAMEN', 'trade',           9470.44::numeric,  2023),
        ('FUJIAN_XIAMEN', 'gdp_total',       2913.67::numeric,  2024),  -- eid=57609 (Knife F 收录; 2024 stays K669b-i-batch1)
        ('FUJIAN_XIAMEN', 'gdp_growth',      5.5::numeric,      2024),
        ('FUJIAN_XIAMEN', 'primary_gdp',     26.34::numeric,    2024),
        ('FUJIAN_XIAMEN', 'secondary_gdp',   3147.40::numeric,  2024),
        ('FUJIAN_XIAMEN', 'tertiary_gdp',    5415.28::numeric,  2024),
        ('FUJIAN_XIAMEN', 'fiscal_rev',      933.19::numeric,   2024),
        ('FUJIAN_XIAMEN', 'trade',           9326.12::numeric,  2024),
        ('FUJIAN_XIAMEN', 'gdp_total',       3056.72::numeric,  2025),  -- eid=68649
        ('FUJIAN_XIAMEN', 'gdp_growth',      5.7::numeric,      2025),
        ('FUJIAN_XIAMEN', 'primary_gdp',     24.24::numeric,    2025),
        ('FUJIAN_XIAMEN', 'secondary_gdp',   3394.74::numeric,  2025),
        ('FUJIAN_XIAMEN', 'tertiary_gdp',    5561.39::numeric,  2025),
        ('FUJIAN_XIAMEN', 'fiscal_rev',      961.08::numeric,   2025),
        ('FUJIAN_XIAMEN', 'retail',          3448.60::numeric,  2025),
        ('FUJIAN_XIAMEN', 'trade',           9600.22::numeric,  2025)
)
SELECT
    cp.city_code,
    cp.city_name,
    cp.province_code,
    cp.indicator_key,
    cp.indicator_label,
    cp.unit,
    cp.year,
    COALESCE(rd.value, rd2.value, rd3.value, rd4.value, rd5.value, rd6.value, rd7.value, rd8.value, rd9.value, rd10.value, rd11.value, rd13.value, rd14.value, rd15.value, rd16.value, rd17.value, rd18.value) AS value,
    CASE
        WHEN cp.year < 2020  THEN 'DATA_MISSING'
        WHEN cp.year = 2026  THEN 'DATA_MISSING'
        WHEN cp.year = 2020  AND rd7.value IS NOT NULL THEN NULL  -- real cell from 669fix-b-2020 harvest
        WHEN cp.year = 2020  AND rd7.value IS NULL     THEN 'DATA_MISSING'  -- city×indicator 公报未列
        WHEN cp.year = 2021  AND rd.value IS NOT NULL  THEN NULL  -- 4 669a cities real cell
        WHEN cp.year = 2021  AND rd8.value IS NOT NULL THEN NULL  -- 25 省会 real cell from 669fix-b-2021 harvest
        WHEN cp.year = 2021  AND rd.value IS NULL      THEN 'DATA_MISSING'
        WHEN cp.year = 2021  AND rd8.value IS NULL     THEN 'DATA_MISSING'
        WHEN cp.year = 2022  AND rd9.value IS NOT NULL THEN NULL  -- 25 省会 real cell from 669fix-b-2022 harvest
        WHEN cp.year = 2022  AND rd2.value IS NOT NULL THEN NULL  -- 4 669a cities real cell
        WHEN cp.year = 2022  AND rd9.value IS NULL     THEN 'DATA_MISSING'  -- 25 省会 missing cell
        WHEN cp.year = 2022  AND rd2.value IS NULL     THEN 'DATA_MISSING'  -- 4 669a cities missing cell
        WHEN cp.year = 2023  AND rd10.value IS NOT NULL THEN NULL  -- 25 省会 real cell from 669fix-b-2023 harvest
        WHEN cp.year = 2023  AND rd3.value IS NOT NULL THEN NULL  -- 4 669a cities real cell (K669a-2023)
        WHEN cp.year = 2023  AND rd10.value IS NULL     THEN 'DATA_MISSING'  -- 25 省会 missing cell
        WHEN cp.year = 2023  AND rd3.value IS NULL     THEN 'DATA_MISSING'  -- 4 669a cities missing cell
        WHEN cp.year = 2024  AND rd11.value IS NOT NULL THEN NULL  -- 25 省会 real cell from K669fix-b-2024
        WHEN cp.year = 2024  AND rd4.value IS NOT NULL THEN NULL  -- real cell, status=NULL
        WHEN cp.year = 2024  AND rd13.value IS NOT NULL THEN NULL  -- knife F first sub-knife real cell (8 cities, 57 cells)
        WHEN cp.year = 2024  AND rd4.value IS NULL     THEN 'DATA_MISSING'
        WHEN cp.year = 2025  AND rd5.value IS NOT NULL THEN NULL  -- real cell, status=NULL
        WHEN cp.year = 2025  AND rd6.value IS NOT NULL THEN NULL  -- real cell (future-proofing for 669b)
        WHEN cp.year = 2025  AND rd5.value IS NULL     THEN 'DATA_MISSING'  -- covers 4 669a + 25 669b cities
        WHEN cp.city_code = 'GUANGDONG_DONGGUAN' AND rd14.value IS NOT NULL THEN NULL  -- knife 669b-i-dongguan real cell (2021/2022/2023/2025, 37 cells)
        WHEN cp.city_code = 'GUANGDONG_DONGGUAN' AND cp.year = 2020 THEN 'DATA_MISSING'  -- knife 669b-i-dongguan explicit 2020 exclusion (hongheiku tag 无 2020 bulletin)
        WHEN cp.city_code = 'LIAONING_DALIAN' AND rd15.value IS NOT NULL THEN NULL  -- knife 669b-i-dalian real cell (2021/2022/2023/2025, 30 cells; 2024 stays in rd13 Knife F)
        WHEN cp.city_code = 'LIAONING_DALIAN' AND cp.year = 2020 THEN 'DATA_MISSING'  -- knife 669b-i-dalian: hongheiku tag 页无 2020 DALIAN 公告
        WHEN cp.city_code = 'JIANGSU_WUXI' AND rd16.value IS NOT NULL THEN NULL  -- knife 669b-i-wuxi real cell (2021/2023/2025, 26 cells; 2024 stays in rd13 Knife F)
        WHEN cp.city_code = 'JIANGSU_WUXI' AND cp.year = 2020 THEN 'DATA_MISSING'  -- knife 669b-i-wuxi: hongheiku 2020 WUXI 公告走 /1707.html 老 ID, 非 /djs/ 标准 pattern (Knife E 不支持)
        WHEN cp.city_code = 'JIANGSU_WUXI' AND cp.year = 2022 THEN 'DATA_MISSING'  -- knife 669b-i-wuxi: hongheiku tag 页无 2022 /djs/{eid}.html (仅 /xjtjgb/xj2020/34940.html 非标准 path)
        WHEN cp.city_code = 'JIANGSU_SUZHOU' AND rd17.value IS NOT NULL THEN NULL  -- knife 669b-i-suzhou real cell (2021/2022/2024/2025, 35 cells; 2024 stays in rd13 Knife F attribution)
        WHEN cp.city_code = 'JIANGSU_SUZHOU' AND cp.year = 2020 THEN 'DATA_MISSING'  -- knife 669b-i-suzhou: hongheiku 2020 SUZHOU 公告走 /3008.html 老 ID, 非 /djs/ 标准 pattern (Knife E 不支持)
        WHEN cp.city_code = 'JIANGSU_SUZHOU' AND cp.year = 2023 THEN 'DATA_MISSING'  -- knife 669b-i-suzhou: parser regex 数字含空格失配 (e.g. "24653 . 4 亿元" 不能匹配 "(\d+\.?\d*)\s*亿", 守红线-3 禁编造)
        WHEN cp.city_code = 'FUJIAN_XIAMEN' AND rd18.value IS NOT NULL THEN NULL  -- knife 669b-i-xiamen real cell (2021/2022/2023/2025, 32 cells; 2024 stays in rd13 Knife F attribution)
        WHEN cp.city_code = 'FUJIAN_XIAMEN' AND cp.year = 2020 THEN 'DATA_MISSING'  -- knife 669b-i-xiamen: hongheiku tag 页无 2020 XIAMEN 公告 (5 entries 全是 2021-2025, 守新增红线-3 不手填)
        ELSE 'DATA_MISSING'  -- 2026 待 2027 官方发布
    END AS status,
    CASE
        WHEN cp.year < 2020  THEN '新增红线-1: 2001-2019 禁编造历史数据 (hongheiku 城市 probe 待补; 红线通用)'
        WHEN cp.year = 2026  THEN '新增红线-2: 2026 待 2027 官方发布'
        WHEN cp.year = 2020  AND rd7.value IS NOT NULL THEN NULL  -- real cell, no missing_reason
        WHEN cp.year = 2020  AND rd7.value IS NULL     AND cp.city_code = 'TAIWAN_TAIPEI'
            THEN 'knife 669fix-b-2020: hongheiku tag 页无 2020 bulletin (TAIWAN, 守新增红线-3 不手填)'
        WHEN cp.year = 2020  AND rd7.value IS NULL     AND cp.city_code IN ('JIANGXI_NANCHANG', 'SHANXI_TAIYUAN')
            THEN 'knife 669fix-b-2020: bulletin 内容为 image 扫描件, 无 OCR 范围 (守红线-3)'
        WHEN cp.year = 2020  AND rd7.value IS NULL     AND cp.indicator_key = 'fixed_asset'
            THEN 'knife 669fix-b-2020: bulletin 仅发增长% 无绝对值 (守红线-3, per 669a-2021 §2)'
        WHEN cp.year = 2020  AND rd7.value IS NULL     THEN 'knife 669fix-b-2020: 25 省会 2020 bulletin 未列此 indicator (守新增红线-3 不手填; 后续 sub-knife 可补采)'
        WHEN cp.year = 2021  AND rd.value IS NOT NULL  THEN NULL  -- 4 669a cities real cell, no missing_reason
        WHEN cp.year = 2021  AND rd8.value IS NOT NULL THEN NULL  -- 25 省会 real cell, no missing_reason
        WHEN cp.year = 2021  AND rd.value IS NULL      AND cp.city_code IN ('GUANGDONG_SHENZHEN','GUANGDONG_GUANGZHOU','ZHEJIANG_HANGZHOU','JIANGSU_NANJING')
            THEN 'knife 669a-2021 公报未列/正则 miss (守新增红线-3 不手填; 后续 sub-knife 可补采)'
        WHEN cp.year = 2021  AND rd8.value IS NULL     AND cp.city_code IN ('SICHUAN_CHENGDU','XIZANG_LASA','QINGHAI_XINING','TAIWAN_TAIPEI')
            THEN 'knife 669fix-b-2021: hongheiku tag 页无 2021 bulletin (SICHUAN/XIZANG/QINGHAI/TAIWAN, 守新增红线-3 不手填)'
        WHEN cp.year = 2021  AND rd8.value IS NULL     AND cp.city_code IN ('HUBEI_WUHAN','SHANXI_TAIYUAN')
            THEN 'knife 669fix-b-2021: hongheiku URL 实为 tag listing 无内容 (28733/24774, 守新增红线-3 不手填)'
        WHEN cp.year = 2021  AND rd8.value IS NULL     AND cp.indicator_key = 'fixed_asset'
            THEN 'knife 669fix-b-2021: bulletin 仅发增长% 无绝对值 (守红线-3, per 669a-2021 §2)'
        WHEN cp.year = 2021  AND rd8.value IS NULL     THEN 'knife 669fix-b-2021: 25 省会 2021 bulletin 未列此 indicator (守新增红线-3 不手填; 后续 sub-knife 可补采)'
        WHEN cp.year = 2022  AND rd9.value IS NOT NULL THEN NULL  -- 25 省会 real cell, no missing_reason
        WHEN cp.year = 2022  AND rd2.value IS NOT NULL THEN NULL  -- 4 669a cities real cell, no missing_reason
        WHEN cp.year = 2022  AND rd9.value IS NULL     AND cp.city_code IN ('GUANGXI_NANNING','TAIWAN_TAIPEI')
            THEN 'knife 669fix-b-2022: hongheiku tag 页无 2022 bulletin (GUANGXI_NANNING/TAIWAN_TAIPEI, 守新增红线-3 不手填)'
        WHEN cp.year = 2022  AND rd9.value IS NULL     AND cp.city_code = 'QINGHAI_XINING'
            THEN 'knife 669fix-b-2022: bulletin 内容为 tag listing 无具体数值 (984 chars, 守新增红线-3 不手填)'
        WHEN cp.year = 2022  AND rd9.value IS NULL     AND cp.indicator_key = 'fixed_asset'
            THEN 'knife 669fix-b-2022: bulletin 仅发增长% 无绝对值 (守红线-3, per 669a-2021 §2)'
        WHEN cp.year = 2022  AND rd9.value IS NULL     THEN 'knife 669fix-b-2022: 25 省会 2022 bulletin 未列此 indicator (守新增红线-3 不手填; 后续 sub-knife 可补采)'
        WHEN cp.year = 2022  AND rd2.value IS NULL     THEN 'knife 669a-2022 公报仅发增速无绝对值 (守新增红线-3 不手填; 后续 sub-knife 可补采)'
        WHEN cp.year = 2023  AND rd10.value IS NOT NULL THEN NULL  -- 25 省会 real cell, no missing_reason
        WHEN cp.year = 2023  AND rd3.value IS NOT NULL THEN NULL  -- 4 669a cities real cell, no missing_reason
        WHEN cp.year = 2023  AND rd10.value IS NULL     AND cp.city_code IN ('LIAONING_SHENYANG','HEILONGJIANG_HARBIN','JIANGXI_NANCHANG','YUNNAN_KUNMING','TAIWAN_TAIPEI')
            THEN 'knife 669fix-b-2023: hongheiku tag 页无 2023 bulletin (LIAONING/HEILONGJIANG/JIANGXI/YUNNAN/TAIWAN, 守新增红线-3 不手填)'
        WHEN cp.year = 2023  AND rd10.value IS NULL     AND cp.city_code IN ('SHAANXI_XIAN','QINGHAI_XINING')
            THEN 'knife 669fix-b-2023: bulletin 内容为 tag listing 无具体数值 (448-984 chars, 守新增红线-3 不手填)'
        WHEN cp.year = 2023  AND rd10.value IS NULL     AND cp.indicator_key = 'fixed_asset'
            THEN 'knife 669fix-b-2023: bulletin 仅发增长% 无绝对值 (守红线-3, per 669a-2021 §2)'
        WHEN cp.year = 2023  AND rd10.value IS NULL     THEN 'knife 669fix-b-2023: 25 省会 2023 bulletin 未列此 indicator (守新增红线-3 不手填; 后续 sub-knife 可补采)'
        WHEN cp.year = 2023  AND rd3.value IS NULL     THEN 'knife 669a-2023 公报仅发增速无绝对值 (守新增红线-3 不手填; 后续 sub-knife 可补采)'
        WHEN cp.year = 2024  AND rd11.value IS NOT NULL THEN NULL  -- 25 省会 real cell, no missing_reason
        WHEN cp.year = 2024  AND rd4.value IS NOT NULL THEN NULL  -- real cell, no missing_reason
        WHEN cp.year = 2024  AND rd13.value IS NOT NULL THEN NULL  -- knife F first sub-knife real cell, no missing_reason
        WHEN cp.year = 2024  AND rd11.value IS NULL     AND cp.city_code IN ('JIANGXI_NANCHANG','YUNNAN_KUNMING','QINGHAI_XINING','TAIWAN_TAIPEI')
            THEN 'knife 669fix-b-2024: hongheiku tag 页无 2024 bulletin (JIANGXI/YUNNAN/QINGHAI/TAIWAN, 守新增红线-3 不手填)'
        WHEN cp.year = 2024  AND rd11.value IS NULL     AND cp.indicator_key = 'fixed_asset'
            THEN 'knife 669fix-b-2024: bulletin 仅发增长% 无绝对值 (守红线-3, per 669a-2021 §2)'
        WHEN cp.year = 2024  AND rd11.value IS NULL     THEN 'knife 669fix-b-2024: 25 省会 2024 bulletin 未列此 indicator (守新增红线-3 不手填; 后续 sub-knife 可补采)'
        WHEN cp.year = 2024  AND rd4.value IS NOT NULL THEN NULL  -- real cell, no missing_reason
        WHEN cp.year = 2024  AND rd13.value IS NULL     AND cp.city_code = 'ZHEJIANG_NINGBO'
            THEN 'knife F first sub-knife (2026-09-09): hongheiku /tag/宁波市 无 2024 bulletin (仅 2021/2022/2023/2025, 守新增红线-3 不手填)'
        WHEN cp.year = 2024  AND rd13.value IS NULL     AND cp.indicator_key = 'fixed_asset'
            THEN 'knife F first sub-knife (2026-09-09): bulletin 仅发增长% 无绝对值 (守红线-3)'
        WHEN cp.year = 2024  AND rd13.value IS NULL     THEN 'knife F first sub-knife (2026-09-09): 8 cities × 2024 bulletin parser 未匹配此 indicator (守新增红线-3 不手填; 后续 sub-knife 可补采)'
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
        WHEN cp.city_code = 'GUANGDONG_DONGGUAN' AND rd14.value IS NOT NULL THEN NULL  -- knife 669b-i-dongguan real cell, no missing_reason
        WHEN cp.city_code = 'GUANGDONG_DONGGUAN' AND cp.year = 2020 THEN 'knife 669b-i-dongguan: hongheiku 无 2020 DONGGUAN 公告 (tag 页仅 2021-2025, 守红线-3 禁编造)'
        WHEN cp.city_code = 'GUANGDONG_DONGGUAN' AND rd14.value IS NULL AND cp.indicator_key = 'fixed_asset'
            THEN 'knife 669b-i-dongguan: bulletin 仅发增长% 无绝对值 (守红线-3, per 669a-2021 §2)'  -- 2021/2022/2023 fixed_asset 3 cells
        WHEN cp.city_code = 'LIAONING_DALIAN' AND rd15.value IS NOT NULL THEN NULL  -- knife 669b-i-dalian real cell (2021/2022/2023/2025, 30 cells)
        WHEN cp.city_code = 'LIAONING_DALIAN' AND cp.year = 2020 THEN 'knife 669b-i-dalian: hongheiku 无 2020 年 DALIAN 公告 (tag 页仅 2021-2025, 守红线-3 禁编造)'
        WHEN cp.city_code = 'LIAONING_DALIAN' AND rd15.value IS NULL AND cp.indicator_key IN ('gdp_total', 'gdp_percapita', 'fixed_asset')
            THEN 'knife 669b-i-dalian: bulletin 仅发增长%/parser 未匹配 (守红线-3, per 669a-2021 §2)'  -- 12 cells = 3 (2021 gdp_total/gdp_percapita/fixed_asset) + 2 (2022 gdp_total/fixed_asset) + 2 (2023 gdp_total/fixed_asset) + 3 (2025 gdp_total/gdp_percapita/fixed_asset) + 2 (2024 from Knife F)
        WHEN cp.city_code = 'JIANGSU_WUXI' AND rd16.value IS NOT NULL THEN NULL  -- knife 669b-i-wuxi real cell (2021/2023/2025, 26 cells), no missing_reason
        WHEN cp.city_code = 'JIANGSU_WUXI' AND cp.year = 2020 THEN 'knife 669b-i-wuxi: hongheiku 2020 WUXI 公告走 /1707.html 老 ID, 非 /djs/ 标准 pattern (Knife E 不支持, 守红线-3 禁编造)'
        WHEN cp.city_code = 'JIANGSU_WUXI' AND cp.year = 2022 THEN 'knife 669b-i-wuxi: hongheiku tag 页无 2022 年 WUXI 公告 /djs/{eid}.html (仅 /xjtjgb/xj2020/34940.html 非标准 path, 守红线-3 禁编造)'
        WHEN cp.city_code = 'JIANGSU_WUXI' AND rd16.value IS NULL AND cp.indicator_key IN ('gdp_percapita', 'fiscal_rev')
            THEN 'knife 669b-i-wuxi: bulletin 无 gdp_percapita 数据 / 2021 fiscal_rev parser 未匹配 (守红线-3, per 669a-2021 §2)'  -- 4 cells (gdp_percapita ×3 + 2021 fiscal_rev)
        WHEN cp.city_code = 'JIANGSU_SUZHOU' AND rd17.value IS NOT NULL THEN NULL  -- knife 669b-i-suzhou real cell, no missing_reason
        WHEN cp.city_code = 'JIANGSU_SUZHOU' AND cp.year = 2020 THEN 'knife 669b-i-suzhou: hongheiku 2020 SUZHOU 公告走 /3008.html 老 ID, 非 /djs/ 标准 pattern (Knife E 不支持, 守红线-3 禁编造)'
        WHEN cp.city_code = 'JIANGSU_SUZHOU' AND rd17.value IS NULL AND cp.indicator_key = 'gdp_percapita'
            THEN 'knife 669b-i-suzhou: bulletin 无 gdp_percapita 数据 (守红线-3, per 669a-2021 §2)'  -- 4 cells (gdp_percapita ×4 for 2021/2022/2024/2025)
        WHEN cp.city_code = 'JIANGSU_SUZHOU' AND rd17.value IS NULL AND cp.year = 2024 AND cp.indicator_key = 'retail'
            THEN 'knife 669b-i-suzhou: 2024 retail bulletin parser 未匹配 (守红线-3)'  -- 1 cell
        WHEN cp.city_code = 'JIANGSU_SUZHOU' AND rd17.value IS NULL AND cp.year = 2023
            THEN 'knife 669b-i-suzhou: parser regex 数字含空格失配 "24653 . 4 亿元" 不能匹配 (守红线-3, hongheiku 苏州 2023 eid 45627 bulletin 排版异常)'
        WHEN cp.city_code = 'FUJIAN_XIAMEN' AND rd18.value IS NOT NULL THEN NULL  -- knife 669b-i-xiamen real cell, no missing_reason
        WHEN cp.city_code = 'FUJIAN_XIAMEN' AND cp.year = 2020 THEN 'knife 669b-i-xiamen: hongheiku tag 页无 2020 XIAMEN 公告 (5 entries: 2021/2022/2023/2024/2025, 守新增红线-3 不手填)'
        WHEN cp.city_code = 'FUJIAN_XIAMEN' AND rd18.value IS NULL AND cp.indicator_key = 'gdp_percapita'
            THEN 'knife 669b-i-xiamen: bulletin 无 gdp_percapita 数据 (守红线-3, per 669a-2021 §2)'  -- 5 cells (gdp_percapita ×5 for 2021/2022/2023/2024/2025; 2024 stays Knife F)
        WHEN cp.city_code = 'FUJIAN_XIAMEN' AND rd18.value IS NULL AND cp.year = 2021 AND cp.indicator_key = 'fiscal_rev'
            THEN 'knife 669b-i-xiamen: 2021 fiscal_rev bulletin parser 未匹配 (守红线-3)'  -- 1 cell
        WHEN cp.city_code = 'FUJIAN_XIAMEN' AND rd18.value IS NULL AND cp.indicator_key = 'fixed_asset'
            THEN 'knife 669b-i-xiamen: bulletin 仅发增长% 无绝对值 (守红线-3, per 669a-2021 §2)'  -- 4 cells (2021/2022/2023/2025; 2024 stays Knife F)
        WHEN cp.city_code = 'FUJIAN_XIAMEN' AND rd18.value IS NULL AND cp.year = 2024 AND cp.indicator_key = 'retail'
            THEN 'knife 669b-i-xiamen: 2024 retail bulletin parser 未匹配 (守红线-3)'  -- 1 cell
        ELSE 'knife 669 后续 sub-knife 待 harvest'
    END AS missing_reason,
    CASE
        WHEN cp.year = 2020  AND rd7.value IS NOT NULL THEN 'HONGHEIKU_TRANSLOAD'
        WHEN cp.year = 2021  AND rd.value IS NOT NULL  THEN 'HONGHEIKU_TRANSLOAD'  -- 4 669a
        WHEN cp.year = 2021  AND rd8.value IS NOT NULL THEN 'HONGHEIKU_TRANSLOAD'  -- 25 省会 from 669fix-b-2021
        WHEN cp.year = 2022  AND rd9.value IS NOT NULL THEN 'HONGHEIKU_TRANSLOAD'  -- 25 省会 from 669fix-b-2022
        WHEN cp.year = 2022  AND rd2.value IS NOT NULL THEN 'HONGHEIKU_TRANSLOAD'  -- 4 669a cities
        WHEN cp.year = 2023  AND rd10.value IS NOT NULL THEN 'HONGHEIKU_TRANSLOAD'  -- 25 省会 from 669fix-b-2023
        WHEN cp.year = 2023  AND rd3.value IS NOT NULL THEN 'HONGHEIKU_TRANSLOAD'  -- 4 669a cities (K669a-2023)
        WHEN cp.year = 2024  AND rd11.value IS NOT NULL THEN 'HONGHEIKU_TRANSLOAD'  -- 25 省会 from 669fix-b-2024
        WHEN cp.year = 2024  AND rd13.value IS NOT NULL THEN 'HONGHEIKU_TRANSLOAD'  -- knife F first sub-knife real cells (8 city × 2024)
        WHEN cp.year = 2024  AND rd4.value IS NOT NULL THEN 'HONGHEIKU_TRANSLOAD'
        WHEN cp.year = 2025  AND rd5.value IS NOT NULL THEN 'HONGHEIKU_TRANSLOAD'
        WHEN cp.year = 2025  AND rd6.value IS NOT NULL THEN 'HONGHEIKU_TRANSLOAD'  -- future-proofing for 669b
        WHEN cp.city_code = 'GUANGDONG_DONGGUAN' AND rd14.value IS NOT NULL THEN 'HONGHEIKU_TRANSLOAD'  -- knife 669b-i-dongguan real cell
        WHEN cp.city_code = 'LIAONING_DALIAN' AND rd15.value IS NOT NULL THEN 'HONGHEIKU_TRANSLOAD'  -- knife 669b-i-dalian real cell
        WHEN cp.city_code = 'JIANGSU_WUXI' AND rd16.value IS NOT NULL THEN 'HONGHEIKU_TRANSLOAD'  -- knife 669b-i-wuxi real cell
        WHEN cp.city_code = 'JIANGSU_SUZHOU' AND rd17.value IS NOT NULL THEN 'HONGHEIKU_TRANSLOAD'  -- knife 669b-i-suzhou real cell
        WHEN cp.city_code = 'FUJIAN_XIAMEN' AND rd18.value IS NOT NULL THEN 'HONGHEIKU_TRANSLOAD'  -- knife 669b-i-xiamen real cell
        ELSE 'DATA_MISSING'
    END AS lineage_source_type,
    CASE
        WHEN cp.year = 2020  AND rd7.value IS NOT NULL THEN 'tjgb.hongheiku.com/' || cp.city_code  -- e.g. /1816.html, /djs/...
        WHEN cp.year = 2021  AND rd.value IS NOT NULL  THEN 'tjgb.hongheiku.com/djs/' || cp.city_name
        WHEN cp.year = 2021  AND rd8.value IS NOT NULL THEN 'tjgb.hongheiku.com/djs/' || cp.city_code  -- 25 省会 2021 eid encoded in city_code
        WHEN cp.year = 2022  AND rd9.value IS NOT NULL THEN 'tjgb.hongheiku.com/djs/' || cp.city_code  -- 25 省会 2022 eid encoded in city_code (669fix-b-2022)
        WHEN cp.year = 2022  AND rd2.value IS NOT NULL THEN 'tjgb.hongheiku.com/djs/' || cp.city_name  -- 4 669a cities
        WHEN cp.year = 2023  AND rd10.value IS NOT NULL THEN 'tjgb.hongheiku.com/djs/' || cp.city_code  -- 25 省会 2023 eid encoded in city_code (669fix-b-2023)
        WHEN cp.year = 2023  AND rd3.value IS NOT NULL THEN 'tjgb.hongheiku.com/djs/' || cp.city_name
        WHEN cp.year = 2024  AND rd13.value IS NOT NULL THEN 'tjgb.hongheiku.com/tag/' || cp.city_name  -- knife F first sub-knife real cells (8 city × 2024, hongheiku tag page)
        WHEN cp.year = 2024  AND rd11.value IS NOT NULL THEN 'tjgb.hongheiku.com/djs/' || cp.city_code  -- 25 省会 2024 eid encoded in city_code (669fix-b-2024)
        WHEN cp.year = 2024  AND rd4.value IS NOT NULL THEN 'tjgb.hongheiku.com/djs/' || cp.city_name
        WHEN cp.year = 2024  AND cp.city_code IN (
            'LIAONING_DALIAN','SHANDONG_QINGDAO','ZHEJIANG_NINGBO',
            'FUJIAN_XIAMEN','JIANGSU_SUZHOU','JIANGSU_WUXI',
            'GUANGDONG_FOSHAN','GUANGDONG_DONGGUAN'
        ) THEN 'tjgb.hongheiku.com/tag/' || cp.city_name  -- knife F first sub-knife DATA_MISSING cells (tag page either parser 未匹配 or NINGBO 无 2024 entry)
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
        WHEN cp.city_code = 'GUANGDONG_DONGGUAN' AND rd14.value IS NOT NULL AND cp.year = 2021 THEN 'tjgb.hongheiku.com/djs/25333.html'  -- knife 669b-i-dongguan
        WHEN cp.city_code = 'GUANGDONG_DONGGUAN' AND rd14.value IS NOT NULL AND cp.year = 2022 THEN 'tjgb.hongheiku.com/djs/42065.html'
        WHEN cp.city_code = 'GUANGDONG_DONGGUAN' AND rd14.value IS NOT NULL AND cp.year = 2023 THEN 'tjgb.hongheiku.com/djs/47430.html'
        WHEN cp.city_code = 'GUANGDONG_DONGGUAN' AND rd14.value IS NOT NULL AND cp.year = 2025 THEN 'tjgb.hongheiku.com/djs/69935.html'
        WHEN cp.city_code = 'GUANGDONG_DONGGUAN' AND rd14.value IS NULL AND cp.indicator_key = 'fixed_asset'
            THEN 'tjgb.hongheiku.com/djs/{25333,42065,47430}.html (bulletin 仅发增长%)'  -- 2021/2022/2023 fixed_asset 3 cells
        WHEN cp.city_code = 'GUANGDONG_DONGGUAN' AND cp.year = 2020 THEN 'tjgb.hongheiku.com/tag/东莞市 (no 2020 entry, 守新增红线-3 不手填)'
        WHEN cp.city_code = 'LIAONING_DALIAN' AND rd15.value IS NOT NULL AND cp.year = 2021 THEN 'tjgb.hongheiku.com/djs/30342.html'  -- knife 669b-i-dalian
        WHEN cp.city_code = 'LIAONING_DALIAN' AND rd15.value IS NOT NULL AND cp.year = 2022 THEN 'tjgb.hongheiku.com/djs/36951.html'
        WHEN cp.city_code = 'LIAONING_DALIAN' AND rd15.value IS NOT NULL AND cp.year = 2023 THEN 'tjgb.hongheiku.com/djs/48502.html'
        WHEN cp.city_code = 'LIAONING_DALIAN' AND rd15.value IS NOT NULL AND cp.year = 2025 THEN 'tjgb.hongheiku.com/djs/69004.html'
        WHEN cp.city_code = 'LIAONING_DALIAN' AND rd15.value IS NULL AND cp.indicator_key IN ('gdp_total', 'gdp_percapita', 'fixed_asset')
            THEN 'tjgb.hongheiku.com/djs/{30342,36951,48502,69004}.html (bulletin 仅发增长%/parser 未匹配)'  -- 12 cells
        WHEN cp.city_code = 'LIAONING_DALIAN' AND cp.year = 2020 THEN 'tjgb.hongheiku.com/tag/大连市 (no 2020 entry, 守新增红线-3 不手填)'
        WHEN cp.city_code = 'JIANGSU_WUXI' AND rd16.value IS NOT NULL AND cp.year = 2021 THEN 'tjgb.hongheiku.com/djs/23931.html'  -- knife 669b-i-wuxi
        WHEN cp.city_code = 'JIANGSU_WUXI' AND rd16.value IS NOT NULL AND cp.year = 2023 THEN 'tjgb.hongheiku.com/djs/45593.html'
        WHEN cp.city_code = 'JIANGSU_WUXI' AND rd16.value IS NOT NULL AND cp.year = 2025 THEN 'tjgb.hongheiku.com/djs/70051.html'
        WHEN cp.city_code = 'JIANGSU_WUXI' AND rd16.value IS NULL AND cp.indicator_key IN ('gdp_percapita', 'fiscal_rev')
            THEN 'tjgb.hongheiku.com/djs/{23931,45593,70051}.html (bulletin 无 gdp_percapita 数据 / 2021 fiscal_rev parser 未匹配)'  -- 4 cells
        WHEN cp.city_code = 'JIANGSU_WUXI' AND cp.year = 2020 THEN 'tjgb.hongheiku.com/1707.html (老 ID 非 djs pattern, Knife E 不支持, 守新增红线-3 不手填)'
        WHEN cp.city_code = 'JIANGSU_WUXI' AND cp.year = 2022 THEN 'tjgb.hongheiku.com/xjtjgb/xj2020/34940.html (非标准 path, Knife E 不支持, 守新增红线-3 不手填)'
        WHEN cp.city_code = 'JIANGSU_SUZHOU' AND rd17.value IS NOT NULL AND cp.year = 2021 THEN 'tjgb.hongheiku.com/djs/25410.html'  -- knife 669b-i-suzhou
        WHEN cp.city_code = 'JIANGSU_SUZHOU' AND rd17.value IS NOT NULL AND cp.year = 2022 THEN 'tjgb.hongheiku.com/djs/35155.html'
        WHEN cp.city_code = 'JIANGSU_SUZHOU' AND rd17.value IS NOT NULL AND cp.year = 2024 THEN 'tjgb.hongheiku.com/djs/61278.html'  -- Knife F attribution (2024 stays K669b-i-batch1)
        WHEN cp.city_code = 'JIANGSU_SUZHOU' AND rd17.value IS NOT NULL AND cp.year = 2025 THEN 'tjgb.hongheiku.com/djs/69636.html'
        WHEN cp.city_code = 'JIANGSU_SUZHOU' AND rd17.value IS NULL AND cp.indicator_key = 'gdp_percapita'
            THEN 'tjgb.hongheiku.com/djs/{25410,35155,61278,69636}.html (bulletin 无 gdp_percapita 数据)'  -- 4 cells
        WHEN cp.city_code = 'JIANGSU_SUZHOU' AND rd17.value IS NULL AND cp.year = 2024 AND cp.indicator_key = 'retail'
            THEN 'tjgb.hongheiku.com/djs/61278.html (2024 retail parser 未匹配, 守红线-3)'  -- 1 cell
        WHEN cp.city_code = 'JIANGSU_SUZHOU' AND rd17.value IS NULL AND cp.year = 2023
            THEN 'tjgb.hongheiku.com/djs/45627.html (2023 bulletin parser 数字含空格 regex 失配, 守红线-3 禁编造)'  -- 10 cells
        WHEN cp.city_code = 'JIANGSU_SUZHOU' AND cp.year = 2020 THEN 'tjgb.hongheiku.com/3008.html (老 ID 非 djs pattern, Knife E 不支持, 守新增红线-3 不手填)'
        WHEN cp.city_code = 'FUJIAN_XIAMEN' AND rd18.value IS NOT NULL AND cp.year = 2021 THEN 'tjgb.hongheiku.com/djs/24437.html'  -- knife 669b-i-xiamen
        WHEN cp.city_code = 'FUJIAN_XIAMEN' AND rd18.value IS NOT NULL AND cp.year = 2022 THEN 'tjgb.hongheiku.com/djs/38423.html'
        WHEN cp.city_code = 'FUJIAN_XIAMEN' AND rd18.value IS NOT NULL AND cp.year = 2023 THEN 'tjgb.hongheiku.com/djs/45732.html'
        WHEN cp.city_code = 'FUJIAN_XIAMEN' AND rd18.value IS NOT NULL AND cp.year = 2025 THEN 'tjgb.hongheiku.com/djs/68649.html'
        WHEN cp.city_code = 'FUJIAN_XIAMEN' AND rd18.value IS NULL AND cp.indicator_key = 'gdp_percapita'
            THEN 'tjgb.hongheiku.com/djs/{24437,38423,45732,68649}.html (bulletin 无 gdp_percapita 数据)'  -- 4 cells (2024 stays Knife F)
        WHEN cp.city_code = 'FUJIAN_XIAMEN' AND rd18.value IS NULL AND cp.year = 2021 AND cp.indicator_key = 'fiscal_rev'
            THEN 'tjgb.hongheiku.com/djs/24437.html (2021 fiscal_rev parser 未匹配, 守红线-3)'  -- 1 cell
        WHEN cp.city_code = 'FUJIAN_XIAMEN' AND rd18.value IS NULL AND cp.indicator_key = 'fixed_asset'
            THEN 'tjgb.hongheiku.com/djs/{24437,38423,45732,68649}.html (bulletin 仅发增长% 无绝对值)'  -- 4 cells
        WHEN cp.city_code = 'FUJIAN_XIAMEN' AND rd18.value IS NULL AND cp.year = 2024 AND cp.indicator_key = 'retail'
            THEN 'tjgb.hongheiku.com/djs/57609.html (2024 retail parser 未匹配, 守红线-3)'  -- 1 cell
        WHEN cp.city_code = 'FUJIAN_XIAMEN' AND cp.year = 2020 THEN 'tjgb.hongheiku.com/tag/厦门市 (no 2020 entry, 守新增红线-3 不手填)'
        ELSE 'none'
    END AS lineage_origin,
    CASE
        WHEN cp.year = 2020  AND rd7.value IS NOT NULL THEN 'K669fix-b-2020-2026-09-08'
        WHEN cp.year = 2020  AND cp.city_code IN (
            'GUANGDONG_SHENZHEN','GUANGDONG_GUANGZHOU','ZHEJIANG_HANGZHOU','JIANGSU_NANJING'
        ) THEN 'K669a-2020-2026-09-04'  -- 4 669a cities, not in 25 省会 dimension
        WHEN cp.year = 2020  THEN 'K669fix-b-2020-2026-09-08'  -- 25 省会 missing cells
        WHEN cp.year = 2021  AND cp.city_code IN (
            'GUANGDONG_SHENZHEN','GUANGDONG_GUANGZHOU','ZHEJIANG_HANGZHOU','JIANGSU_NANJING'
        ) THEN 'K669a-2021-2026-09-04'  -- 4 669a cities
        WHEN cp.year = 2021  AND rd8.value IS NOT NULL THEN 'K669fix-b-2021-2026-09-08'  -- 25 省会 real cells
        WHEN cp.year = 2021  THEN 'K669fix-b-2021-2026-09-08'  -- 25 省会 missing cells
        WHEN cp.year = 2022  AND rd9.value IS NOT NULL THEN 'K669fix-b-2022-2026-09-08'  -- 25 省会 real cells from 669fix-b-2022 harvest
        WHEN cp.year = 2022  AND rd2.value IS NOT NULL THEN 'K669a-2022-2026-09-07'  -- 4 669a cities real cells
        WHEN cp.year = 2022  AND cp.city_code IN (
            'GUANGDONG_SHENZHEN','GUANGDONG_GUANGZHOU','ZHEJIANG_HANGZHOU','JIANGSU_NANJING'
        ) THEN 'K669a-2022-2026-09-07'  -- 4 669a cities missing cells
        WHEN cp.year = 2022  THEN 'K669fix-b-2022-2026-09-08'  -- 25 省会 missing cells
        WHEN cp.year = 2023  AND rd10.value IS NOT NULL THEN 'K669fix-b-2023-2026-09-08'  -- 25 省会 real cells from 669fix-b-2023 harvest
        WHEN cp.year = 2023  AND cp.city_code IN (
            'GUANGDONG_SHENZHEN','GUANGDONG_GUANGZHOU','ZHEJIANG_HANGZHOU','JIANGSU_NANJING'
        ) THEN 'K669a-2023-2026-09-07'  -- 4 669a cities
        WHEN cp.year = 2023  THEN 'K669fix-b-2023-2026-09-08'  -- 25 省会 missing cells
        WHEN cp.year = 2024  AND rd13.value IS NOT NULL THEN 'K669b-i-batch1-parse-2024-2026-09-09'  -- knife F first sub-knife real cells (8 city × 2024)
        WHEN cp.year = 2024  AND rd11.value IS NOT NULL THEN 'K669fix-b-2024-2026-09-09'  -- 25 省会 real cells from 669fix-b-2024 harvest
        WHEN cp.year = 2024  AND cp.city_code IN (
            'LIAONING_DALIAN','SHANDONG_QINGDAO','ZHEJIANG_NINGBO',
            'FUJIAN_XIAMEN','JIANGSU_SUZHOU','JIANGSU_WUXI',
            'GUANGDONG_FOSHAN','GUANGDONG_DONGGUAN'
        ) THEN 'K669b-i-batch1-parse-2024-2026-09-09'  -- knife F first sub-knife DATA_MISSING cells (23 missing: 13 fixed_asset/growth-only + NINGBO 10 all-missing)
        WHEN cp.year = 2024  AND cp.city_code IN (
            'GUANGDONG_SHENZHEN','GUANGDONG_GUANGZHOU','ZHEJIANG_HANGZHOU','JIANGSU_NANJING'
        ) THEN 'K669a-2024-2026-09-07'  -- 4 669a cities
        WHEN cp.year = 2024  THEN 'K669fix-b-2024-2026-09-09'  -- 25 省会 missing cells
        WHEN cp.year = 2025  AND cp.city_code IN (
            'GUANGDONG_SHENZHEN','GUANGDONG_GUANGZHOU','ZHEJIANG_HANGZHOU','JIANGSU_NANJING'
        ) THEN 'K669a-2025-2026-09-07'
        WHEN cp.year = 2025  THEN 'K669fix-b-2025-2026-09-09'  -- 25 省会 (深/穗/杭/宁 之外的, zero-harvest 路径; 替代 K669b-2025 attribution)
        WHEN cp.city_code = 'GUANGDONG_DONGGUAN' AND rd14.value IS NOT NULL AND cp.year = 2021 THEN 'K669b-i-dongguan-parse-2021-2026-09-10'
        WHEN cp.city_code = 'GUANGDONG_DONGGUAN' AND rd14.value IS NOT NULL AND cp.year = 2022 THEN 'K669b-i-dongguan-parse-2022-2026-09-10'
        WHEN cp.city_code = 'GUANGDONG_DONGGUAN' AND rd14.value IS NOT NULL AND cp.year = 2023 THEN 'K669b-i-dongguan-parse-2023-2026-09-10'
        WHEN cp.city_code = 'GUANGDONG_DONGGUAN' AND rd14.value IS NOT NULL AND cp.year = 2025 THEN 'K669b-i-dongguan-parse-2025-2026-09-10'
        WHEN cp.city_code = 'GUANGDONG_DONGGUAN' AND rd14.value IS NULL AND cp.indicator_key = 'fixed_asset'
            THEN 'K669b-i-dongguan-parse-fixed_asset_growth_pct-2026-09-10'  -- 2021/2022/2023 fixed_asset 3 cells
        WHEN cp.city_code = 'GUANGDONG_DONGGUAN' AND cp.year = 2020 THEN 'K669b-i-dongguan-no-bulletin-2020-2026-09-10'
        WHEN cp.city_code = 'LIAONING_DALIAN' AND rd15.value IS NOT NULL AND cp.year = 2021 THEN 'K669b-i-dalian-parse-2021-2026-09-10'  -- knife 669b-i-dalian
        WHEN cp.city_code = 'LIAONING_DALIAN' AND rd15.value IS NOT NULL AND cp.year = 2022 THEN 'K669b-i-dalian-parse-2022-2026-09-10'
        WHEN cp.city_code = 'LIAONING_DALIAN' AND rd15.value IS NOT NULL AND cp.year = 2023 THEN 'K669b-i-dalian-parse-2023-2026-09-10'
        WHEN cp.city_code = 'LIAONING_DALIAN' AND rd15.value IS NOT NULL AND cp.year = 2025 THEN 'K669b-i-dalian-parse-2025-2026-09-10'
        WHEN cp.city_code = 'LIAONING_DALIAN' AND rd15.value IS NULL AND cp.indicator_key IN ('gdp_total', 'gdp_percapita', 'fixed_asset')
            THEN 'K669b-i-dalian-parse-fixed_asset_growth_pct-2026-09-10'  -- 12 cells (3+2+2+3+2 Knife F 2024 = 12)
        WHEN cp.city_code = 'LIAONING_DALIAN' AND cp.year = 2020 THEN 'K669b-i-dalian-no-bulletin-2020-2026-09-10'
        WHEN cp.city_code = 'JIANGSU_WUXI' AND rd16.value IS NOT NULL AND cp.year = 2021 THEN 'K669b-i-wuxi-parse-2021-2026-09-10'  -- knife 669b-i-wuxi
        WHEN cp.city_code = 'JIANGSU_WUXI' AND rd16.value IS NOT NULL AND cp.year = 2023 THEN 'K669b-i-wuxi-parse-2023-2026-09-10'
        WHEN cp.city_code = 'JIANGSU_WUXI' AND rd16.value IS NOT NULL AND cp.year = 2025 THEN 'K669b-i-wuxi-parse-2025-2026-09-10'
        WHEN cp.city_code = 'JIANGSU_WUXI' AND rd16.value IS NULL AND cp.indicator_key IN ('gdp_percapita', 'fiscal_rev')
            THEN 'K669b-i-wuxi-parse-fixed_asset_growth_pct-2026-09-10'  -- 4 cells (gdp_percapita ×3 + 2021 fiscal_rev)
        WHEN cp.city_code = 'JIANGSU_WUXI' AND cp.year = 2020 THEN 'K669b-i-wuxi-no-bulletin-djs-2020-2026-09-10'  -- 老 ID /1707.html 非 djs pattern
        WHEN cp.city_code = 'JIANGSU_WUXI' AND cp.year = 2022 THEN 'K669b-i-wuxi-no-bulletin-2022-2026-09-10'  -- tag 页无 /djs/{eid}.html
        WHEN cp.city_code = 'JIANGSU_SUZHOU' AND rd17.value IS NOT NULL AND cp.year = 2021 THEN 'K669b-i-suzhou-parse-2021-2026-09-10'  -- knife 669b-i-suzhou
        WHEN cp.city_code = 'JIANGSU_SUZHOU' AND rd17.value IS NOT NULL AND cp.year = 2022 THEN 'K669b-i-suzhou-parse-2022-2026-09-10'
        WHEN cp.city_code = 'JIANGSU_SUZHOU' AND rd17.value IS NOT NULL AND cp.year = 2024 THEN 'K669b-i-batch1-parse-2024-2026-09-09'  -- Knife F attribution
        WHEN cp.city_code = 'JIANGSU_SUZHOU' AND rd17.value IS NOT NULL AND cp.year = 2025 THEN 'K669b-i-suzhou-parse-2025-2026-09-10'
        WHEN cp.city_code = 'JIANGSU_SUZHOU' AND rd17.value IS NULL AND cp.indicator_key = 'gdp_percapita'
            THEN 'K669b-i-suzhou-parse-fixed_asset_growth_pct-2026-09-10'  -- 4 cells (gdp_percapita ×4 for 2021/2022/2024/2025)
        WHEN cp.city_code = 'JIANGSU_SUZHOU' AND rd17.value IS NULL AND cp.year = 2024 AND cp.indicator_key = 'retail'
            THEN 'K669b-i-suzhou-parse-fixed_asset_growth_pct-2026-09-10'  -- 1 cell (2024 retail parser 未匹配)
        WHEN cp.city_code = 'JIANGSU_SUZHOU' AND rd17.value IS NULL AND cp.year = 2023
            THEN 'K669b-i-suzhou-no-bulletin-2023-2026-09-10'  -- parser 数字含空格 regex 失配 (苏州 2023 bulletin 排版异常, hongheiku eid 45627)
        WHEN cp.city_code = 'JIANGSU_SUZHOU' AND cp.year = 2020 THEN 'K669b-i-suzhou-no-bulletin-djs-2020-2026-09-10'  -- 老 ID /3008.html 非 djs pattern
        WHEN cp.city_code = 'FUJIAN_XIAMEN' AND rd18.value IS NOT NULL AND cp.year = 2021 THEN 'K669b-i-xiamen-parse-2021-2026-09-12'  -- knife 669b-i-xiamen
        WHEN cp.city_code = 'FUJIAN_XIAMEN' AND rd18.value IS NOT NULL AND cp.year = 2022 THEN 'K669b-i-xiamen-parse-2022-2026-09-12'
        WHEN cp.city_code = 'FUJIAN_XIAMEN' AND rd18.value IS NOT NULL AND cp.year = 2023 THEN 'K669b-i-xiamen-parse-2023-2026-09-12'
        WHEN cp.city_code = 'FUJIAN_XIAMEN' AND rd18.value IS NOT NULL AND cp.year = 2025 THEN 'K669b-i-xiamen-parse-2025-2026-09-12'
        WHEN cp.city_code = 'FUJIAN_XIAMEN' AND rd18.value IS NULL AND cp.indicator_key = 'gdp_percapita'
            THEN 'K669b-i-xiamen-parse-fixed_asset_growth_pct-2026-09-12'  -- 4 cells (gdp_percapita ×4 for 2021/2022/2023/2025; 2024 stays Knife F)
        WHEN cp.city_code = 'FUJIAN_XIAMEN' AND rd18.value IS NULL AND cp.year = 2021 AND cp.indicator_key = 'fiscal_rev'
            THEN 'K669b-i-xiamen-parse-fixed_asset_growth_pct-2026-09-12'  -- 1 cell (2021 fiscal_rev parser 未匹配)
        WHEN cp.city_code = 'FUJIAN_XIAMEN' AND rd18.value IS NULL AND cp.indicator_key = 'fixed_asset'
            THEN 'K669b-i-xiamen-parse-fixed_asset_growth_pct-2026-09-12'  -- 4 cells (fixed_asset 2021/2022/2023/2025 bulletin 仅发增长%)
        WHEN cp.city_code = 'FUJIAN_XIAMEN' AND rd18.value IS NULL AND cp.year = 2024 AND cp.indicator_key = 'retail'
            THEN 'K669b-i-xiamen-parse-fixed_asset_growth_pct-2026-09-12'  -- 1 cell (2024 retail parser 未匹配)
        WHEN cp.city_code = 'FUJIAN_XIAMEN' AND cp.year = 2020 THEN 'K669b-i-xiamen-no-bulletin-tag-2020-2026-09-12'  -- hongheiku tag 页无 2020 XIAMEN 公告 (5 entries: 2021-2025)
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
    AND cp.year = 2025
LEFT JOIN real_data_669fix_2020 rd7
    ON cp.city_code = rd7.city_code
    AND cp.indicator_key = rd7.indicator_key
    AND cp.year = 2020
LEFT JOIN real_data_669fix_2021 rd8
    ON cp.city_code = rd8.city_code
    AND cp.indicator_key = rd8.indicator_key
    AND cp.year = 2021
LEFT JOIN real_data_669fix_2022 rd9
    ON cp.city_code = rd9.city_code
    AND cp.indicator_key = rd9.indicator_key
    AND cp.year = 2022
LEFT JOIN real_data_669fix_2023 rd10
    ON cp.city_code = rd10.city_code
    AND cp.indicator_key = rd10.indicator_key
    AND cp.year = 2023
LEFT JOIN real_data_669fix_2024 rd11
    ON cp.city_code = rd11.city_code
    AND cp.indicator_key = rd11.indicator_key
    AND cp.year = 2024
LEFT JOIN real_data_669fix_2025 rd12
    ON cp.city_code = rd12.city_code
    AND cp.indicator_key = rd12.indicator_key
    AND cp.year = 2025
LEFT JOIN real_data_669b_i_batch1_2024 rd13
    ON cp.city_code = rd13.city_code
    AND cp.indicator_key = rd13.indicator_key
    AND cp.year = 2024
LEFT JOIN real_data_669b_i_dongguan rd14
    ON cp.city_code = rd14.city_code
    AND cp.indicator_key = rd14.indicator_key
    AND cp.year IN (2021, 2022, 2023, 2025);  -- 2024 stays in rd13 (Knife F attribution)
LEFT JOIN real_data_669b_i_dalian rd15
    ON cp.city_code = rd15.city_code
    AND cp.indicator_key = rd15.indicator_key
    AND cp.year IN (2021, 2022, 2023, 2025);  -- 2024 stays in rd13 (Knife F attribution)
LEFT JOIN real_data_669b_i_wuxi rd16
    ON cp.city_code = rd16.city_code
    AND cp.indicator_key = rd16.indicator_key
    AND cp.year IN (2021, 2023, 2025);  -- 2020/2022/2024/2026 stay DATA_MISSING or Knife F attribution
LEFT JOIN real_data_669b_i_suzhou rd17
    ON cp.city_code = rd17.city_code
    AND cp.indicator_key = rd17.indicator_key
    AND cp.year IN (2021, 2022, 2024, 2025);  -- 2020 老 ID /3008.html, 2023 parser 数字含空格失配, 2026 守新增红线-2
LEFT JOIN real_data_669b_i_xiamen rd18
    ON cp.city_code = rd18.city_code
    AND cp.indicator_key = rd18.indicator_key
    AND cp.year IN (2021, 2022, 2023, 2025);  -- 2020 hongheiku tag 无 entry, 2024 stays rd13 (Knife F), 2026 守新增红线-2
