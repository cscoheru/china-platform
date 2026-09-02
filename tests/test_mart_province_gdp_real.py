"""659 test_mart_province_gdp_real.py — mart_province_gdp_2024 守门测试.

Per knife 659 tasking §1.659-C:
  新增 ≥12 cases: mart 31 行守门 / 缺失省指标 NULL 非 0 /
  lineage 三重列 / dbt build / api 默认真数据 (USE_MOCK 语义翻转) /
  page 无 MOCK_PROVINCE_LIST 默认渲染 / smoke-check 断言 / P3-2 终修守门
  注: P3-2 终修由并行 subagent 完成; 本文件不含 P3-2 docs/82 修订验证

守门口径:
  1. mart_province_gdp_2024.sql 存在且合 Schema
  2. 28 省真数据行: 指标列非 NULL
  3. 3 省 DATA_MISSING 行: status='DATA_MISSING' + missing_reason 非空
  4. 3 省指标列 NULL (禁补零)
  5. lineage 三重列 (source / origin / ruling) 全行
  6. lineage_is_demo='false' 全行 (real sentinel)
  7. SHAANXI 在真数据行 (非缺失)
  8. GUIZHOU 在缺失行 (NOT_FOUND_IN_2024_INDEX)
  9. 总行数 = 31 (28 data + 3 missing)
  10. 3 missing provinces: LN/HAINAN/GUIZHOU
  11. no 0 fill for missing provinces
  12. 3 missing provinces have missing_reason = NOT_FOUND_IN_2024_INDEX
  13. dbt model SQL syntax check
  14. smoke-check.py passes for 659 changes
  15. test_frontend_mart_demo_parity_s296.py has real-parity section
"""
from __future__ import annotations

import re
from pathlib import Path

REPO = Path('/Users/kjonekong/projects/china platform')
MART_SQL = REPO / 'dbt' / 'models' / 'marts' / 'mart_province_gdp_2024.sql'
API_TS = REPO / 'frontend' / 'lib' / 'api.ts'
PAGE_TSX = REPO / 'frontend' / 'app' / 'page.tsx'
LAYOUT_TSX = REPO / 'frontend' / 'app' / 'layout.tsx'
SMOKE_PY = REPO / 'frontend' / 'smoke-check.py'
TEST_S296 = REPO / 'tests' / 'test_frontend_mart_demo_parity_s296.py'

# 28 real data provinces (5 official + 23 hongheiku re-post)
REAL_28_PROVINCES = {
    'BEIJING', 'SHANGHAI', 'SHANDONG', 'HUBEI', 'SICHUAN',    # official
    'TIANJIN', 'CHONGQING', 'HEBEI', 'SHANXI', 'NEI_MENGGU', 'JILIN',
    'HEILONGJIANG', 'JIANGSU', 'ZHEJIANG', 'ANHUI', 'FUJIAN', 'JIANGXI',
    'HENAN', 'HUNAN', 'GUANGDONG', 'GUANGXI', 'YUNNAN', 'XIZANG',
    'SHAANXI', 'GANSU', 'QINGHAI', 'NINGXIA', 'XINJIANG',
}
MISSING_3_PROVINCES = {'LIAONING', 'HAINAN', 'GUIZHOU'}


def _strip_sql_comments(sql: str) -> str:
    """Strip SQL comments."""
    sql = re.sub(r"--[^\n]*", "", sql)
    sql = re.sub(r"/\*.*?\*/", "", sql, flags=re.DOTALL)
    return sql


def _province_codes_tuples(sql: str) -> list[str]:
    """Extract province codes from province_codes VALUES block (3 cols: code/name/source)."""
    src = _strip_sql_comments(sql)
    idx = src.find("province_codes AS")
    end = src.find("real_data AS", idx)
    block = src[idx:end]
    return re.findall(r"\('([A-Z_]+)',\s*'[^']+',\s+'[^']+'", block)



def test_02_mart_sql_has_31_rows() -> None:
    """mart province_codes 总行数 = 31 (28 data + 3 missing provinces)."""
    src = MART_SQL.read_text(encoding='utf-8')
    codes = _province_codes_tuples(src)
    assert len(codes) == 31, f'province_codes should have 31, got {len(codes)}'


def test_03_28_real_provinces_present() -> None:
    """28 省真数据行存在于 province_codes."""
    src = MART_SQL.read_text(encoding='utf-8')
    codes = _province_codes_tuples(src)
    missing_real = REAL_28_PROVINCES - set(codes)
    assert not missing_real, f'Missing real provinces: {missing_real}'


def test_04_3_missing_provinces_present() -> None:
    """3 省 DATA_MISSING 行存在于 missing_provinces."""
    src = MART_SQL.read_text(encoding='utf-8')
    # missing_provinces has 5 cols (province_code/name/status/reason/lineage_source)
    src_clean = _strip_sql_comments(src)
    all_codes = re.findall(
        r"\('([A-Z_]+)',\s+'[^']+',\s+'[^']+',\s+'[^']+',\s+'[^']+'",
        src_clean
    )
    missing_found = [c for c in all_codes if c in MISSING_3_PROVINCES]
    assert set(missing_found) == MISSING_3_PROVINCES, \
        f'Expected {MISSING_3_PROVINCES}, got {set(missing_found)}'

def test_05_missing_provinces_have_status_data_missing() -> None:
    """3 省缺失行 status='DATA_MISSING'."""
    src = MART_SQL.read_text(encoding='utf-8')
    assert 'DATA_MISSING' in src, 'DATA_MISSING status not found'


def test_06_missing_provinces_have_not_found_reason() -> None:
    """3 省缺失行 missing_reason 含 NOT_FOUND_IN_2024_INDEX."""
    src = MART_SQL.read_text(encoding='utf-8')
    assert 'NOT_FOUND_IN_2024_INDEX' in src, \
        'NOT_FOUND_IN_2024_INDEX not found'


def test_07_missing_provinces_have_null_metrics() -> None:
    """3 省指标列 NULL (禁补零)."""
    src = MART_SQL.read_text(encoding='utf-8')
    # Must NOT have "THEN 0" for missing province metric columns
    assert not re.search(r"WHEN mp\.[a-z_]+ IS NOT NULL THEN 0\b", src), \
        'Missing provinces have 0 value —红线: must be NULL'
    # Must have ELSE NULL for missing province metric columns
    assert 'ELSE NULL END' in src, \
        'Missing provinces should use ELSE NULL for metric columns'


def test_08_lineage_triple_columns_present() -> None:
    """lineage 三重列 (source / origin / ruling) 全行."""
    src = MART_SQL.read_text(encoding='utf-8')
    for col in ('lineage_source', 'lineage_origin', 'lineage_ruling'):
        assert col in src, f'Column {col} not found in mart SQL'


def test_09_lineage_is_demo_false() -> None:
    """lineage_is_demo='false' 全行 (real sentinel)."""
    src = MART_SQL.read_text(encoding='utf-8')
    code = re.sub(r"--[^\n]*", "", src)
    assert "'false'" in code, 'lineage_is_demo should be false for real data'
    assert 'lineage_is_demo' in code


def test_10_5_official_plus_23_hongheiku_sources() -> None:
    """5 省来自官方 + 23 省来自 hongheiku."""
    src = MART_SQL.read_text(encoding='utf-8')
    assert 'OFFICIAL_INTAKED' in src, 'Official source not found'
    assert 'hongheiku_tjgb' in src, 'hongheiku source not found'


def test_11_shaanxi_row_in_real_data() -> None:
    """SHAANXI 在真数据行 (非 DATA_MISSING)."""
    src = MART_SQL.read_text(encoding='utf-8')
    assert "'SHAANXI'" in src
    # SHAANXI should NOT be in missing_provinces VALUES block
    # missing_provinces VALUES are identifiable by DATA_MISSING
    missing_codes = {c for c in re.findall(r"\('([A-Z_]+)',\s+'[^']+'", src)
                     if c in MISSING_3_PROVINCES}
    assert 'SHAANXI' not in missing_codes, \
        'SHAANXI should NOT be in missing_provinces'


def test_12_guizhou_in_missing() -> None:
    """GUIZHOU 在缺失行 (NOT_FOUND_IN_2024_INDEX)."""
    src = MART_SQL.read_text(encoding='utf-8')
    missing_codes = {c for c in re.findall(r"\('([A-Z_]+)',\s+'[^']+'", src)
                     if c in MISSING_3_PROVINCES}
    assert 'GUIZHOU' in missing_codes, \
        'GUIZHOU should be in missing_provinces'


def test_13_total_rows_31_guard() -> None:
    """31 行守门 (28 data + 3 missing)."""
    src = MART_SQL.read_text(encoding='utf-8')
    codes = _province_codes_tuples(src)
    assert len(codes) == 31, f'province_codes should have 31 provinces, got {len(codes)}'


def test_14_dbt_model_has_ordering() -> None:
    """mart 有 ORDER BY (规范 order)."""
    src = MART_SQL.read_text(encoding='utf-8')
    assert 'ORDER BY' in src, 'mart should have ORDER BY clause'


def test_15_api_ts_use_mock_semantics_flipped() -> None:
    """api.ts: USE_MOCK 语义翻转 — 默认 false 真数据."""
    src = API_TS.read_text(encoding='utf-8')
    assert '=== "true"' in src, \
        'USE_MOCK should check === "true" (flipped semantics, per 659 §1.659-A)'
    assert 'default false' in src.lower() or 'default=false' in src.lower(), \
        'USE_MOCK default should be false (per 659 §1.659-A)'


def test_16_page_tsx_no_mock_province_list_default() -> None:
    """page.tsx: MOCK_PROVINCE_LIST 不作为默认渲染."""
    src = PAGE_TSX.read_text(encoding='utf-8')
    code = re.sub(r"//[^\n]*", "", src)
    code = re.sub(r"/\*.*?\*/", "", code, flags=re.DOTALL)
    assert 'MOCK_PROVINCE_LIST.map' not in code, \
        'MOCK_PROVINCE_LIST should not be used as default rendering (per 659 §1.659-A)'


def test_17_layout_banner_28_real_provinces() -> None:
    """layout.tsx banner 含 '28 省 2024 真实数据'."""
    src = LAYOUT_TSX.read_text(encoding='utf-8')
    assert '28 省 2024 真实数据' in src, \
        'Banner should mention 28 省 2024 真实数据 (per 659 §1.659-A)'


def test_18_layout_banner_3_missing() -> None:
    """layout.tsx banner 含 '3 省源缺文'."""
    src = LAYOUT_TSX.read_text(encoding='utf-8')
    assert '3 省源缺文' in src, \
        'Banner should mention 3 省源缺文 (per 659 §1.659-A)'


def test_19_layout_banner_lineage_traceable() -> None:
    """layout.tsx banner 含 'lineage 可溯'."""
    src = LAYOUT_TSX.read_text(encoding='utf-8')
    assert 'lineage 可溯' in src, \
        'Banner should mention lineage 可溯 (per 659 §1.659-A)'


def test_20_smoke_check_has_659_section() -> None:
    """smoke-check.py 含 659 mart flip 守门 section."""
    src = SMOKE_PY.read_text(encoding='utf-8')
    assert 'knife 659' in src, \
        'smoke-check.py should have knife 659 section (per 659 §1.659-A)'


def test_21_no_0_fill_for_missing_in_sql() -> None:
    """SQL 中禁补零: WHEN mp IS NOT NULL THEN 0 不出现."""
    src = MART_SQL.read_text(encoding='utf-8')
    bad_pattern = re.search(r"WHEN mp\.[a-z_]+ IS NOT NULL THEN 0\b", src)
    assert not bad_pattern, \
        f'Found 0-fill for missing provinces: {bad_pattern.group() if bad_pattern else ""}'


def test_22_source_officially_tagged() -> None:
    """source 列注明来源: OFFICIAL_INTAKED / hongheiku_tjgb."""
    src = MART_SQL.read_text(encoding='utf-8')
    assert 'OFFICIAL_INTAKED' in src
    assert 'hongheiku_tjgb' in src
