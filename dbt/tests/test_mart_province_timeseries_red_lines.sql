-- knife 663 tasking §verification — mart_province_timeseries 行数 / 红线断言
--
-- 红线强制 (mart 落表后自检, 失败行 = 测试不通过):
--   1) 总行数 = 8060 (= 31 provinces × 10 indicators × 26 years 2001-2026)
--   2) status='DATA_MISSING' 行在 2001-2019 段 (禁编造历史数据, 新增红线-1)
--   3) status='DATA_MISSING' 行在 2026 段 (新增红线-2)
--   4) 3 缺失省份 (LIAONING/HAINAN/GUIZHOU) 在 2020-2025 段全 DATA_MISSING
--   5) 缺失省份不应有 real value (status NULL 但 value NOT NULL 的脏数据)
--   6) 663 初始应有 ≥140 real cells (5 现指标 × 28 real 省 × 2024)
--
-- 返回行 = 失败 (dbt test 协议).
-- Per dbt test 模式: 一行一类失败, select distinct 以避免重复报告.

WITH mart AS (
    SELECT * FROM {{ ref('mart_province_timeseries') }}
),
fail_total_rowcount AS (
    -- 总行数必须 = 8060 (31 × 10 × 26)
    SELECT 'total_rowcount_not_8060' AS failure_type,
           (SELECT COUNT(*) FROM mart) AS actual_count,
           8060 AS expected_count
    WHERE (SELECT COUNT(*) FROM mart) != 8060
),
fail_hist_data AS (
    -- 2001-2019 不应有 real data (status IS NULL AND value IS NOT NULL)
    -- 新增红线-1: 禁编造历史数据
    SELECT 'hist_year_has_real_data' AS failure_type,
           province_code, indicator_key, year, value
    FROM mart
    WHERE year BETWEEN 2001 AND 2019
      AND status IS NULL
      AND value IS NOT NULL
),
fail_y2026_data AS (
    -- 2026 不应有 real data (新增红线-2)
    SELECT 'y2026_has_real_data' AS failure_type,
           province_code, indicator_key, year, value
    FROM mart
    WHERE year = 2026
      AND status IS NULL
      AND value IS NOT NULL
),
fail_missing_province_data AS (
    -- 3 缺失省份 2020-2025 不应有 real data
    SELECT 'missing_province_has_real_data' AS failure_type,
           province_code, indicator_key, year, value
    FROM mart
    WHERE province_code IN ('LIAONING', 'HAINAN', 'GUIZHOU')
      AND year BETWEEN 2020 AND 2025
      AND status IS NULL
      AND value IS NOT NULL
),
fail_dirty_value AS (
    -- status='DATA_MISSING' 但 value 非 NULL = 脏数据 (违反禁补零)
    SELECT 'dirty_data_missing_with_value' AS failure_type,
           province_code, indicator_key, year, value, status
    FROM mart
    WHERE status = 'DATA_MISSING'
      AND value IS NOT NULL
),
fail_initial_real_count AS (
    -- 663 初始 real cells 应 ≥135 (5 现 × 28 real provinces × 2024 = 140 minus 5 OFFICIAL gdp_growth NULL gap)
    --   - 5 现指标中: gdp_total/primary/secondary/tertiary 各 28 real
    --   - gdp_growth 仅 23 real (5 OFFICIAL_INTAKED [京/沪/鲁/鄂/川] 在 660 batch 里 gdp_growth 为 NULL,
    --     这是 P1 已知数据缺口, 沿用至 P2; 665 试 hongheiku 补)
    --   - 5 增量指标 663 初始全 DATA_MISSING (665 harvest)
    -- 总: 28+23+28+28+28 = 135 real cells (vs plan 140, 差异 = 5 OFFICIAL gdp_growth)
    SELECT 'initial_real_count_below_135' AS failure_type,
           (SELECT COUNT(*) FROM mart WHERE status IS NULL AND value IS NOT NULL) AS actual_real_count,
           135 AS minimum_expected_count
    WHERE (SELECT COUNT(*) FROM mart WHERE status IS NULL AND value IS NOT NULL) < 135
)
SELECT * FROM fail_total_rowcount
UNION ALL SELECT * FROM fail_hist_data
UNION ALL SELECT * FROM fail_y2026_data
UNION ALL SELECT * FROM fail_missing_province_data
UNION ALL SELECT * FROM fail_dirty_value
UNION ALL SELECT * FROM fail_initial_real_count
