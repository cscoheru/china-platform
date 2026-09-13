-- Migration 001: Add UNIQUE constraint on mart_city_timeseries for UPSERT
-- Knife: 669b-i batch4 (2026-09-13)
-- Purpose: Enable INSERT ... ON CONFLICT (city_code, indicator_key, year) DO UPDATE
--          pattern in apply_mart_city_669b_i_batch4.py (and future 669b-i batches).
--          Before this constraint, 669b-i batches could only UPDATE existing rows,
--          blocking first-time city INSERT (WENZHOU/SHAOXING/JIAXING/HUZHOU).
-- Reversible: ALTER TABLE cegr_mart.mart_city_timeseries DROP CONSTRAINT uq_mart_city_timeseries_city_ind_year;
-- Verified:   knife 669b-i batch4 apply ran clean (UPSERT 163 real + 67 miss = 230 cells)

ALTER TABLE cegr_mart.mart_city_timeseries
ADD CONSTRAINT uq_mart_city_timeseries_city_ind_year
UNIQUE (city_code, indicator_key, year);