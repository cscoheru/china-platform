"""Stage 2 / S2.7-b-full frontend mart-shape demo parity guard test.

Per docs/47 §3.1 + §3.2 + tasking 296 (frontend mart demo parity).

Locks in the contract alignment between:
  - frontend/lib/mart_city_demo.ts          (TS demo fixture, 10 cities × 6+7 rows)
  - dbt/models/marts/mart_city_evidence_chain.sql   (60 demo rows)
  - dbt/models/marts/mart_city_seven_dim_overview.sql (70 demo rows)

Both sides must agree on:
  - 10 cities (per docs/46 §2 江苏 4 + 浙江 3 + 广东 3):
      nanjing / suzhou / wuxi / nantong / hangzhou / ningbo / wenzhou /
      guangzhou / shenzhen / dongguan
  - 6 segments (per docs/06 §2):
      CONDITION / COMMITMENT / INPUT / PROCESS / OUTPUT / OUTCOME_RISK
  - 7 dimensions (per docs/42 §2.4):
      POLICY_DELIVERY / FISCAL_EXECUTION / PROJECT_DELIVERY /
      ECONOMIC_ADAPTATION / PUBLIC_SERVICES / RISK_MANAGEMENT /
      GOAL_CONSISTENCY
  - 5 balance_status enum (per docs/42 §2.5):
      NO_EVIDENCE / NO_CONTRADICTING_EVIDENCE / NO_SUPPORTING_EVIDENCE /
      SUPPORTS_DOMINANT / CONTRADICTS_DOMINANT
  - lineage.isDemo = true + SHA = '0'.repeat(64)
  - no forbidden fields (score / rating / rank / total_score /
    confidence_score / credibility_score / peer_rank)
  - NEXT_PUBLIC_USE_MART_FIXTURE feature flag declared in
    app/cities/[slug]/page.tsx

Red lines (per tasking 296 §红线 + docs/47 §1.2 + docs/34 §1 + docs/06 §6.6):
  - No real SHA (lineage.source_file_sha256 = '0'.repeat(64) ONLY)
  - No Gate 1/2 PASS
  - No forbidden scoring columns
  - No peer_rank derivation
"""
from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
FRONTEND = ROOT / "frontend"
DBT_MARTS = ROOT / "dbt" / "models" / "marts"

MART_DEMO_TS = FRONTEND / "lib" / "mart_city_demo.ts"
MART_TYPES_TS = FRONTEND / "lib" / "mart_city_types.ts"
CITY_SLUG_MAP_TS = FRONTEND / "lib" / "city_slug_map.ts"
TYPES_SEVEN_DIM_TS = FRONTEND / "lib" / "types_seven_dim.ts"
SLUG_PAGE_TSX = FRONTEND / "app" / "cities" / "[slug]" / "page.tsx"
CITYPAGE_MART_TSX = FRONTEND / "app" / "components" / "CityPageMart.tsx"

DBT_EVIDENCE_CHAIN_SQL = DBT_MARTS / "mart_city_evidence_chain.sql"
DBT_SEVEN_DIM_SQL = DBT_MARTS / "mart_city_seven_dim_overview.sql"

# TS demo contract surface = the 4 source-of-truth files mart_city_demo.ts
# imports its enums/sentinels from. Per docs/47 §3.1 + §3.2 + `265` §SCHEMA.
TS_DEMO_CONTRACT_FILES = (
    MART_DEMO_TS,
    MART_TYPES_TS,
    CITY_SLUG_MAP_TS,
    TYPES_SEVEN_DIM_TS,
)

FORBIDDEN_TOKENS = [
    "score",
    "rating",
    "rank",
    "total_score",
    "confidence_score",
    "credibility_score",
    "peer_rank",
]

EXPECTED_10_CITIES = [
    "nanjing",
    "suzhou",
    "wuxi",
    "nantong",
    "hangzhou",
    "ningbo",
    "wenzhou",
    "guangzhou",
    "shenzhen",
    "dongguan",
]

EXPECTED_6_SEGMENTS = [
    "CONDITION",
    "COMMITMENT",
    "INPUT",
    "PROCESS",
    "OUTPUT",
    "OUTCOME_RISK",
]

EXPECTED_7_DIMENSIONS = [
    "POLICY_DELIVERY",
    "FISCAL_EXECUTION",
    "PROJECT_DELIVERY",
    "ECONOMIC_ADAPTATION",
    "PUBLIC_SERVICES",
    "RISK_MANAGEMENT",
    "GOAL_CONSISTENCY",
]

EXPECTED_5_BALANCE_STATUS = [
    "NO_EVIDENCE",
    "NO_CONTRADICTING_EVIDENCE",
    "NO_SUPPORTING_EVIDENCE",
    "SUPPORTS_DOMINANT",
    "CONTRADICTS_DOMINANT",
]


def _strip_ts_comments(src: str) -> str:
    """Strip TS line + block comments per AGENTS.md 守门."""
    # Block comments /* ... */
    src = re.sub(r"/\*[\s\S]*?\*/", "", src)
    out_lines: list[str] = []
    for line in src.splitlines():
        # // line comments (not inside strings)
        idx = line.find("//")
        if idx >= 0:
            line = line[:idx]
        if line.strip():
            out_lines.append(line)
    return "\n".join(out_lines)


def _strip_sql_comments(src: str) -> str:
    """Strip SQL line + block comments."""
    src = re.sub(r"/\*[\s\S]*?\*/", "", src)
    out_lines: list[str] = []
    for line in src.splitlines():
        idx = line.find("--")
        if idx >= 0:
            line = line[:idx]
        if line.strip():
            out_lines.append(line)
    return "\n".join(out_lines)


def _assert_no_forbidden_tokens(clean: str, file_label: str) -> None:
    """Strip-quotes-safe scan for forbidden scoring tokens."""
    for tok in FORBIDDEN_TOKENS:
        pat = re.compile(rf"(?<![A-Za-z0-9_]){re.escape(tok)}(?![A-Za-z0-9_])")
        if pat.search(clean):
            raise AssertionError(
                f"FORBIDDEN: {file_label} 含禁词 '{tok}' "
                f"(per docs/06 §6.6 + docs/42 §8 + docs/47 §1.2 红线)"
            )


# ===== 1. mart_city_demo.ts file existence =====

def test_mart_city_demo_ts_exists() -> None:
    assert MART_DEMO_TS.is_file(), f"missing: {MART_DEMO_TS}"


def test_mart_city_types_ts_exists() -> None:
    assert MART_TYPES_TS.is_file(), f"missing: {MART_TYPES_TS}"


# ===== 2. mart demo 契约对齐（TS demo imports from 4-file contract surface）=====

def test_mart_demo_ts_enumerates_10_cities() -> None:
    """Per docs/46 §2 + 任务书 296 §SCHEMA '10 城'。

    TS demo imports CITY_SLUG_LIST from city_slug_map.ts (single source of
    truth for the locked 10-city list per docs/46 §2 + Cursor ruling).
    """
    src = CITY_SLUG_MAP_TS.read_text(encoding="utf-8")
    clean = _strip_ts_comments(src)
    for slug in EXPECTED_10_CITIES:
        assert f'"{slug}"' in clean or f"'{slug}'" in clean, (
            f"city_slug_map.ts: 10 城清单缺 '{slug}' "
            f"(per docs/46 §2 + 296 §SCHEMA)"
        )


def test_mart_demo_ts_enumerates_6_segments() -> None:
    """Per docs/06 §2 — segments listed inline in mart_city_demo.ts."""
    src = MART_DEMO_TS.read_text(encoding="utf-8")
    for seg in EXPECTED_6_SEGMENTS:
        assert f'"{seg}"' in src or f"'{seg}'" in src, (
            f"mart_city_demo.ts: 6 段清单缺 '{seg}' "
            f"(per docs/06 §2)"
        )


def test_mart_demo_ts_enumerates_7_dimensions() -> None:
    """Per docs/42 §2.4 — dims imported from types_seven_dim.ts."""
    src = TYPES_SEVEN_DIM_TS.read_text(encoding="utf-8")
    for card in EXPECTED_7_DIMENSIONS:
        assert f'"{card}"' in src or f"'{card}'" in src, (
            f"types_seven_dim.ts: 7 维度清单缺 '{card}' "
            f"(per docs/42 §2.4)"
        )


def test_mart_demo_ts_enumerates_5_balance_status() -> None:
    """Per docs/42 §2.5 — BALANCE_STATUS imported from types_seven_dim.ts."""
    src = TYPES_SEVEN_DIM_TS.read_text(encoding="utf-8")
    for status in EXPECTED_5_BALANCE_STATUS:
        assert f'"{status}"' in src or f"'{status}'" in src, (
            f"types_seven_dim.ts: 5 balance_status 缺 '{status}' "
            f"(per docs/42 §2.5)"
        )


def test_mart_demo_ts_sha_is_zero_placeholder() -> None:
    """lineage.source_file_sha256 = '0'.repeat(64) 占位（from mart_city_types.ts）."""
    src = MART_TYPES_TS.read_text(encoding="utf-8")
    assert '"0".repeat(64)' in src, (
        "mart_city_types.ts: MART_LINEAGE_PLACEHOLDER_SHA 必须 = '0'.repeat(64) "
        "(per docs/47 §3.1 ⚠️ OPEN + 296 §红线)"
    )


def test_mart_demo_ts_is_demo_true() -> None:
    """lineage.isDemo = true（per S1.18 sentinel）."""
    src = MART_DEMO_TS.read_text(encoding="utf-8")
    assert 'isDemo: true' in src, (
        "mart_city_demo.ts: lineage.isDemo 必须 = true（演示 sentinel）"
    )


def test_mart_demo_ts_no_forbidden_tokens() -> None:
    src = MART_DEMO_TS.read_text(encoding="utf-8")
    clean = _strip_ts_comments(src)
    _assert_no_forbidden_tokens(clean, "mart_city_demo.ts")


# ===== 3. mart_city_types.ts 契约对齐 =====

def test_mart_types_ts_sha_constant_is_zero_64() -> None:
    """MART_LINEAGE_PLACEHOLDER_SHA = '0'.repeat(64)."""
    src = MART_TYPES_TS.read_text(encoding="utf-8")
    assert '"0".repeat(64)' in src, (
        "mart_city_types.ts: MART_LINEAGE_PLACEHOLDER_SHA 必须 = '0'.repeat(64) "
        "(per docs/47 §3.1 ⚠️)"
    )


def test_mart_types_ts_is_demo_string_sentinel() -> None:
    """MART_IS_DEMO = 'true' string sentinel (per S1.18)."""
    src = MART_TYPES_TS.read_text(encoding="utf-8")
    assert '"true"' in src and "MART_IS_DEMO" in src, (
        "mart_city_types.ts: MART_IS_DEMO 必须 = 'true' string sentinel"
    )


def test_mart_types_ts_no_forbidden_tokens() -> None:
    src = MART_TYPES_TS.read_text(encoding="utf-8")
    clean = _strip_ts_comments(src)
    # NOTE: this file legitimately enumerates FORBIDDEN_MART_FIELDS in the
    # assertion helper; do NOT count those occurrences as violations.
    FORBIDDEN_LIST_BLOCK_RE = re.compile(
        r"FORBIDDEN_MART_FIELDS\s*=\s*\[[^\]]+\]",
        re.DOTALL,
    )
    clean_no_list = FORBIDDEN_LIST_BLOCK_RE.sub("", clean)
    _assert_no_forbidden_tokens(clean_no_list, "mart_city_types.ts")


# ===== 4. 城市页 feature-flag 守门 =====

def test_slug_page_declares_mart_fixture_flag() -> None:
    """[slug]/page.tsx 必须声明 NEXT_PUBLIC_USE_MART_FIXTURE feature-flag."""
    src = SLUG_PAGE_TSX.read_text(encoding="utf-8")
    clean = _strip_ts_comments(src)
    assert "NEXT_PUBLIC_USE_MART_FIXTURE" in clean, (
        "app/cities/[slug]/page.tsx: 缺 NEXT_PUBLIC_USE_MART_FIXTURE feature-flag "
        "(per 265 §NOW-1 + 296 §SCHEMA)"
    )
    assert "shouldUseMartFixture" in clean, (
        "app/cities/[slug]/page.tsx: 缺 shouldUseMartFixture() helper"
    )


def test_slug_page_branches_default_vs_mart() -> None:
    """Default: getMockCity; opt-in: getMartCityDemo + CityPageMart."""
    src = SLUG_PAGE_TSX.read_text(encoding="utf-8")
    clean = _strip_ts_comments(src)
    assert "getMockCity" in clean, "缺默认 mock 路径 (getMockCity)"
    assert "getMartCityDemo" in clean, "缺 mart-shape 路径 (getMartCityDemo)"
    assert "CityPageMart" in clean, "缺 CityPageMart 导入"


# ===== 5. UI 显式 demo 标识守门 =====

def test_city_page_mart_shows_demo_marker_in_ui() -> None:
    """CityPageMart.tsx UI 必须显式标注 is_demo + sha256 占位."""
    src = CITYPAGE_MART_TSX.read_text(encoding="utf-8")
    clean = _strip_ts_comments(src)
    assert "is_demo=true" in clean or "is_demo={String" in clean, (
        "CityPageMart.tsx: UI 必须显式标注 is_demo=true "
        "(per 296 §红线 'UI 必须可区分 demo（不得伪装已收口 O1）')"
    )
    assert "data-is-demo" in src, (
        "CityPageMart.tsx: 缺 data-is-demo attribute（testid 守门）"
    )


# ===== 6. dbt mart ↔ TS demo 联合守门（per `296` §NOW-1 契约对齐） =====

def _read_ts_contract_surface() -> str:
    """Concatenate the 4-file TS demo contract surface after comment strip."""
    chunks: list[str] = []
    for p in TS_DEMO_CONTRACT_FILES:
        if p.is_file():
            chunks.append(_strip_ts_comments(p.read_text(encoding="utf-8")))
    return "\n".join(chunks)


def test_dbt_and_ts_demo_share_10_cities() -> None:
    """dbt mart demo-join 与 TS demo 都必须枚举 10 城（per `296` 契约对齐）."""
    ts_contract = _read_ts_contract_surface()
    dbt_ec_src = _strip_sql_comments(DBT_EVIDENCE_CHAIN_SQL.read_text(encoding="utf-8"))
    dbt_sd_src = _strip_sql_comments(DBT_SEVEN_DIM_SQL.read_text(encoding="utf-8"))

    for slug in EXPECTED_10_CITIES:
        # TS contract surface: city_slug_map.ts declares the slug literals
        ts_ok = f'"{slug}"' in ts_contract or f"'{slug}'" in ts_contract
        # dbt: as SQL string literal in VALUES
        dbt_ec_ok = f"'{slug}'" in dbt_ec_src
        dbt_sd_ok = f"'{slug}'" in dbt_sd_src
        assert ts_ok, f"TS demo contract 缺 '{slug}' (city_slug_map.ts)"
        assert dbt_ec_ok, f"dbt mart_city_evidence_chain 缺 '{slug}'"
        assert dbt_sd_ok, f"dbt mart_city_seven_dim_overview 缺 '{slug}'"


def test_dbt_and_ts_demo_share_segment_and_dimension_enums() -> None:
    """dbt mart ↔ TS demo 共享 6 段 + 7 维度 enum."""
    ts_contract = _read_ts_contract_surface()
    dbt_ec_src = _strip_sql_comments(DBT_EVIDENCE_CHAIN_SQL.read_text(encoding="utf-8"))
    dbt_sd_src = _strip_sql_comments(DBT_SEVEN_DIM_SQL.read_text(encoding="utf-8"))

    for seg in EXPECTED_6_SEGMENTS:
        ts_ok = f'"{seg}"' in ts_contract or f"'{seg}'" in ts_contract
        dbt_ok = f"'{seg}'" in dbt_ec_src
        assert ts_ok, f"TS demo contract 缺段 '{seg}'"
        assert dbt_ok, f"dbt evidence_chain 缺段 '{seg}'"

    for card in EXPECTED_7_DIMENSIONS:
        ts_ok = f'"{card}"' in ts_contract or f"'{card}'" in ts_contract
        dbt_ok = f"'{card}'" in dbt_sd_src
        assert ts_ok, f"TS demo contract 缺维度 '{card}'"
        assert dbt_ok, f"dbt seven_dim_overview 缺维度 '{card}'"


def test_dbt_and_ts_demo_share_sha_placeholder() -> None:
    """Both sides must use '0'.repeat(64) / REPEAT('0', 64) as SHA placeholder.

    Per docs/47 §3.1/§3.2 mart-shape contract:
      - mart_city_evidence_chain carries lineage_source_file_sha256 (row-level)
      - mart_city_seven_dim_overview is an aggregate overview; only carries
        is_demo sentinel (per S1.18) — no row-level SHA needed.
    """
    ts_contract = _read_ts_contract_surface()
    dbt_ec_src = _strip_sql_comments(DBT_EVIDENCE_CHAIN_SQL.read_text(encoding="utf-8"))
    dbt_sd_src = _strip_sql_comments(DBT_SEVEN_DIM_SQL.read_text(encoding="utf-8"))

    # TS side: mart_city_types.ts exports the constant
    assert '"0".repeat(64)' in ts_contract, (
        "TS demo contract (mart_city_types.ts) 缺 '0'.repeat(64) 占位"
    )
    # dbt evidence_chain (row-level lineage): must carry SHA placeholder
    assert "REPEAT('0', 64)" in dbt_ec_src, "dbt evidence_chain 缺 REPEAT('0', 64) 占位"
    # dbt seven_dim_overview: must declare is_demo sentinel (no SHA needed;
    # aggregate overview). Verify sentinel instead.
    assert "'true'" in dbt_sd_src and "is_demo" in dbt_sd_src, (
        "dbt seven_dim_overview is_demo sentinel 必须 = 'true' "
        "(per docs/47 §3.2 aggregate overview shape)"
    )


def test_dbt_and_ts_demo_share_is_demo_true() -> None:
    """Both sides must declare is_demo = 'true' / true (demo sentinel)."""
    ts_contract = _read_ts_contract_surface()
    dbt_ec_src = _strip_sql_comments(DBT_EVIDENCE_CHAIN_SQL.read_text(encoding="utf-8"))
    dbt_sd_src = _strip_sql_comments(DBT_SEVEN_DIM_SQL.read_text(encoding="utf-8"))

    # TS demo: mart_city_types.ts exports MART_IS_DEMO = "true"
    assert "MART_IS_DEMO" in ts_contract and '"true"' in ts_contract, (
        "TS demo contract MART_IS_DEMO 必须 = 'true' string sentinel"
    )
    # dbt: lineage_is_demo 'true' literal
    assert "'true'" in dbt_ec_src and "lineage_is_demo" in dbt_ec_src, (
        "dbt evidence_chain lineage_is_demo 必须 = 'true'"
    )
    assert "'true'" in dbt_sd_src and "is_demo" in dbt_sd_src, (
        "dbt seven_dim_overview is_demo 必须 = 'true'"
    )


# ===== 7. cross-file forbidden token guard =====

def test_no_forbidden_tokens_across_frontend_and_dbt() -> None:
    """联合守门: 禁词在 frontend TS + dbt SQL 任何位置均不得命中。"""
    files = [
        (MART_DEMO_TS, _strip_ts_comments),
        (MART_TYPES_TS, _strip_ts_comments),
        (CITY_SLUG_MAP_TS, _strip_ts_comments),
        (TYPES_SEVEN_DIM_TS, _strip_ts_comments),
        (SLUG_PAGE_TSX, _strip_ts_comments),
        (CITYPAGE_MART_TSX, _strip_ts_comments),
        (DBT_EVIDENCE_CHAIN_SQL, _strip_sql_comments),
        (DBT_SEVEN_DIM_SQL, _strip_sql_comments),
    ]
    for path, strip in files:
        clean = strip(path.read_text(encoding="utf-8"))
        for tok in FORBIDDEN_TOKENS:
            # NOTE: types file legitimately enumerates tokens in FORBIDDEN_MART_FIELDS
            if path == MART_TYPES_TS:
                # strip the literal list before scanning
                clean_no_list = re.sub(
                    r"FORBIDDEN_MART_FIELDS\s*=\s*\[[^\]]+\]",
                    "",
                    clean,
                    flags=re.DOTALL,
                )
                scan_target = clean_no_list
            else:
                scan_target = clean
            pat = re.compile(rf"(?<![A-Za-z0-9_]){re.escape(tok)}(?![A-Za-z0-9_])")
            assert not pat.search(scan_target), (
                f"FORBIDDEN: {path.name} 含禁词 '{tok}' "
                f"(per docs/06 §6.6 + docs/42 §8)"
            )


# ===== 8. knife 659 — mart_province_gdp_2024 real-parity (per 659 tasking §1.659-C) =====

MART_GDP_2024 = DBT_MARTS / "mart_province_gdp_2024.sql"

# 28 real data provinces (5 official + 23 hongheiku re-post)
REAL_28_PROVINCES = {
    'BEIJING', 'SHANGHAI', 'SHANDONG', 'HUBEI', 'SICHUAN',    # official
    'TIANJIN', 'CHONGQING', 'HEBEI', 'SHANXI', 'NEI_MENGGU', 'JILIN',
    'HEILONGJIANG', 'JIANGSU', 'ZHEJIANG', 'ANHUI', 'FUJIAN', 'JIANGXI',
    'HENAN', 'HUNAN', 'GUANGDONG', 'GUANGXI', 'YUNNAN', 'XIZANG',
    'SHAANXI', 'GANSU', 'QINGHAI', 'NINGXIA', 'XINJIANG',
}
MISSING_3 = {'LIAONING', 'HAINAN', 'GUIZHOU'}


def test_mart_gdp_2024_exists() -> None:
    """mart_province_gdp_2024.sql 在位."""
    assert MART_GDP_2024.exists(), f"missing: {MART_GDP_2024}"


def test_mart_gdp_2024_has_31_rows() -> None:
    """Total rows = 31 (28 data + 3 missing)."""
    src = MART_GDP_2024.read_text(encoding='utf-8')
    # province_codes block has 31 provinces (incl LN/HAINAN/GUIZHOU)
    idx = src.find("province_codes AS")
    end = src.find("real_data AS", idx)
    block = src[idx:end]
    tuples = re.findall(r"\('([A-Z_]+)', *'[^']+', *'[^']+'", block)
    assert len(tuples) == 31, f"Expected 31, got {len(tuples)}"

def test_mart_gdp_2024_28_real_provinces() -> None:
    """28 provinces in real data block."""
    src = MART_GDP_2024.read_text(encoding='utf-8')
    real_idx = src.find("real_data AS")
    end = src.find("missing_provinces AS", real_idx)
    block = src[real_idx:end]
    tuples = re.findall(r"\('([A-Z_]+)', *'[^']+'", block)
    assert len(tuples) == 28, f"Expected 28 real provinces, got {len(tuples)}"

def test_mart_gdp_2024_3_missing_provinces() -> None:
    """3 省 DATA_MISSING 行存在 (LN/HAINAN/GUIZHOU)."""
    src = MART_GDP_2024.read_text(encoding='utf-8')
    missing_match = re.search(
        r"missing_provinces AS \(\s+SELECT \* FROM \(VALUES(.*?)\)\s+AS t",
        src, re.DOTALL
    )
    assert missing_match, 'missing_provinces block not found'
    vals_block = missing_match.group(1)
    missing_codes = re.findall(r"\('([A-Z_]+)',\s*'[^']+'", vals_block)
    assert set(missing_codes) == MISSING_3, \
        f'Expected {MISSING_3}, got {set(missing_codes)}'
    assert 'DATA_MISSING' in vals_block


def test_mart_gdp_2024_missing_have_null_metrics() -> None:
    """3 缺失省指标列 NULL (红线: 禁补零)."""
    src = MART_GDP_2024.read_text(encoding='utf-8')
    # Check: no "THEN 0" for missing provinces
    assert not re.search(r"WHEN mp\.[a-z_]+ IS NOT NULL THEN 0\b", src), \
        'Missing provinces have 0 —红线: must be NULL'


def test_mart_gdp_2024_missing_reason_not_found() -> None:
    """3 缺失省 missing_reason = NOT_FOUND_IN_2024_INDEX."""
    src = MART_GDP_2024.read_text(encoding='utf-8')
    assert 'NOT_FOUND_IN_2024_INDEX' in src


def test_mart_gdp_2024_lineage_triple() -> None:
    """lineage 三重列: source / origin / ruling 全行."""
    src = MART_GDP_2024.read_text(encoding='utf-8')
    for col in ('lineage_source', 'lineage_origin', 'lineage_ruling'):
        assert col in src, f'{col} not in mart SQL'


def test_mart_gdp_2024_is_demo_false() -> None:
    """lineage_is_demo='false' 全行 (real sentinel)."""
    src = MART_GDP_2024.read_text(encoding='utf-8')
    code = re.sub(r"--[^\n]*", "", src)
    assert "'false'" in code and 'lineage_is_demo' in code


def test_mart_gdp_2024_official_plus_hongheiku() -> None:
    """5 官方 + 23 hongheiku 双源标注."""
    src = MART_GDP_2024.read_text(encoding='utf-8')
    assert 'OFFICIAL_INTAKED' in src, 'Official source not found'
    assert 'hongheiku_tjgb' in src, 'hongheiku source not found'


def test_mart_gdp_2024_shaanxi_real_data() -> None:
    """SHAANXI 在真数据行 (非 DATA_MISSING)."""
    src = MART_GDP_2024.read_text(encoding='utf-8')
    missing_match = re.search(
        r"missing_provinces AS \(\s+SELECT \* FROM \(VALUES(.*?)\)\s+AS t",
        src, re.DOTALL
    )
    assert missing_match
    assert "'SHAANXI'" not in missing_match.group(1), \
        'SHAANXI should NOT be missing'


def test_mart_gdp_2024_guizhou_missing() -> None:
    """GUIZHOU 在缺失行."""
    src = MART_GDP_2024.read_text(encoding='utf-8')
    missing_match = re.search(
        r"missing_provinces AS \(\s+SELECT \* FROM \(VALUES(.*?)\)\s+AS t",
        src, re.DOTALL
    )
    assert missing_match
    assert "'GUIZHOU'" in missing_match.group(1), \
        'GUIZHOU should be in missing_provinces'


def test_mart_gdp_2024_has_ordering() -> None:
    """mart 有 ORDER BY (规范 order)."""
    src = MART_GDP_2024.read_text(encoding='utf-8')
    assert 'ORDER BY' in src, 'mart should have ORDER BY clause'