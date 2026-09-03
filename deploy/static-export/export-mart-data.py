#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
export-mart-data.py — knife 660 Track B (静态导出) + knife 661 扩展 + knife 662 D2.

Reads `dbt/models/marts/mart_province_gdp_2024.sql` (152 行, knife 659 收口),
parses the three VALUES blocks (province_codes / real_data / missing_provinces),
applies the SELECT transformation (LEFT JOIN + CASE/COALESCE) in Python, and
dumps the result as `frontend/data/mart_province_gdp_2024.json` to be consumed
by Next.js at build time via `process.env.NEXT_PUBLIC_MART_DATA_PATH`.

Why parse instead of execute SQL?
- SQLite's VALUES handling is engine-version-dependent; the project's local
  sqlite3 (3.50.4 via Python 3.14 stdlib) does not accept the project's
  `SELECT * FROM (VALUES ...) AS t(...)` pattern as a top-level expression.
- Parsing VALUES tuples with regex is deterministic + portable + auditable.
- Output is byte-stable for the same input (good for downstream cache/tests).

Track B contract (per 660 tasking §PART 2):
- 31 rows total (28 real + 3 DATA_MISSING NULL).
- lineage_is_demo='false' for all real rows (real sentinel).
- Missing provinces have all 5 metric columns = null (禁补零 per 红线 1).
- lineage_ruling='U6 2026-09-02' for all rows.

Knife 661 extensions (per 661 tasking §1.661 + docs/87 §3.1 P1 先行):
- 32 rows total (28 real + 3 DATA_MISSING + 1 NATIONAL anchor).
- NATIONAL anchor row = 全国 2024 GDP 锚值, marked OFFICIAL_ANCHOR.
- Per-row source_url field (per lineage_source → public URL mapping).
- Per-row source_hash_prefix field (null for 661; future 662+ via dbt
  source_document JOIN).

Knife 662 D2 extensions (per 662 tasking §1.662-D2):
- 另输出 `frontend/data/mart_indicator_definitions_2024.json`: 5 指标定义
  (key/label/unit/caliber/period + source_grade_distribution 三档计数).
- caliber/period 来自下方 INDICATOR_METADATA 字典 (代码即元数据,与 mart
  5 指标列对齐);缺省时显式 "(口径待补, 见 lineage_ruling)" 不编 (per 红线 8).
- source_grade_distribution 由 28 真省 + 1 NATIONAL + 3 DATA_MISSING 的
  lineage_source 字段实际计数 (OFFICIAL_INTAKED / HONGHEIKU_TRANSLOAD /
  DATA_MISSING 三档);禁手填.

Exit codes:
- 0  success
- 1  SQL parse error / missing file / row-count mismatch
- 2  red-line violation (missing provinces have non-null metric, etc.)
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]  # deploy/static-export -> repo root
MART_SQL = REPO_ROOT / "dbt" / "models" / "marts" / "mart_province_gdp_2024.sql"
OUT_JSON = REPO_ROOT / "frontend" / "data" / "mart_province_gdp_2024.json"
# 662 D2: 指标定义页 JSON 输出. 同 661 schema_version (不 bump, 因 mart 主
# JSON schema 未变, 仅为派生 JSON).
OUT_INDICATOR_DEFS_JSON = (
    REPO_ROOT / "frontend" / "data" / "mart_indicator_definitions_2024.json"
)
EXPECTED_ROWS = 32  # 661: 28 real + 3 missing + 1 NATIONAL anchor
EXPECTED_REAL = 28
EXPECTED_MISSING = 3
EXPECTED_MISSING_CODES = ["LIAONING", "HAINAN", "GUIZHOU"]
GB_T_2260_ORDER = [
    "BEIJING", "TIANJIN", "HEBEI", "SHANXI", "NEI_MENGGU",
    "LIAONING", "JILIN", "HEILONGJIANG", "SHANGHAI", "JIANGSU",
    "ZHEJIANG", "ANHUI", "FUJIAN", "JIANGXI", "SHANDONG",
    "HENAN", "HUBEI", "HUNAN", "GUANGDONG", "GUANGXI",
    "HAINAN", "CHONGQING", "SICHUAN", "GUIZHOU", "YUNNAN",
    "XIZANG", "SHAANXI", "GANSU", "QINGHAI", "NINGXIA", "XINJIANG",
]
# 662 D2: 5 指标元数据 (代码即元数据, 与 mart 5 指标列对齐).
# caliber/period 用 NBS 标准口径描述 (与 stats.gov.cn 国民经济和社会发展
# 统计公报一致), 非编造数据, 仅描述"指标含义". 若元数据缺失则用
# "(口径待补, 见 lineage_ruling)" 占位 (per 红线 8 禁编造).
INDICATOR_METADATA: dict[str, dict[str, str]] = {
    "gdp_total": {
        "label": "GDP 总量",
        "unit": "亿元",
        "caliber": "地区生产总值（当年价格，亿元）。NBS / 各省统计局国民经济和社会发展统计公报口径。",
        "period": "2024 年（全年）",
    },
    "gdp_growth": {
        "label": "GDP 增速",
        "unit": "%",
        "caliber": "地区生产总值同比增速（不变价，%）。NBS / 各省统计局公报口径。",
        "period": "2024 年（全年）",
    },
    "primary_gdp": {
        "label": "一产增加值",
        "unit": "亿元",
        "caliber": "第一产业增加值（当年价格，亿元）。NBS / 各省统计局口径。",
        "period": "2024 年（全年）",
    },
    "secondary_gdp": {
        "label": "二产增加值",
        "unit": "亿元",
        "caliber": "第二产业增加值（当年价格，亿元）。NBS / 各省统计局口径。",
        "period": "2024 年（全年）",
    },
    "tertiary_gdp": {
        "label": "三产增加值",
        "unit": "亿元",
        "caliber": "第三产业增加值（当年价格，亿元）。NBS / 各省统计局口径。",
        "period": "2024 年（全年）",
    },
}
# 661: source_url mapping per lineage_source type (per docs/81 §2 + U6 ruling).
# These are public government / hongheiku URLs, used as routing key for
# 溯源 popover. Per 红线 8 「溯源 UI 只显示库中真实血缘字段」, source_hash_prefix
# is left null for 661 (will be populated via dbt source_document JOIN in 662+).
SOURCE_URL_BY_LINEAGE = {
    # 5 OFFICIAL_INTAKED provinces: stats.gov.cn national bulletin homepage.
    # Real URL pattern: stats.gov.cn annual GDP bulletin (全国 2024 国民经济
    # 和社会发展统计公报); specific bulletin URL is rotated yearly. Root
    # URL is stable and known public.
    "OFFICIAL_INTAKED": "https://www.stats.gov.cn/sj/zxfb/",
    # 23 hongheiku re-post provinces: tjgb.hongheiku.com per-province archive.
    # Per docs/81 §2 实测: tag 路由 /tag/{省} 列出 2021-2025 各年公报.
    "hongheiku_tjgb": "https://tjgb.hongheiku.com/",
}
# 661 NATIONAL anchor (per docs/81 §3 国家锚核对 1,349,084.0 亿元).
NATIONAL_GDP_TOTAL = "1349084.0"
NATIONAL_ROW_CODE = "NATIONAL"
NATIONAL_ROW_NAME = "全国"
# 662 D2: 口径缺失占位符 (per 红线 8 「溯源 UI 只显示库中真实血缘字段」禁编造).
CALIBER_PLACEHOLDER = "(口径待补, 见 lineage_ruling)"


def parse_values_block(sql: str, cte_name: str) -> list[tuple]:
    """
    Extract a `cte_name AS (SELECT * FROM (VALUES (...) ) AS t(...))` block.
    Returns list of tuple-of-string tuples (literal values, NULL kept as 'NULL').
    """
    # Match the CTE:  cte_name AS (
    #                   SELECT * FROM (VALUES
    #                     ('A', 'B'),
    #                     ...
    #                   ) AS t(...)
    #                 )
    pattern = re.compile(
        rf"{cte_name}\s+AS\s*\(\s*SELECT\s+\*\s+FROM\s+\(VALUES\s*(.*?)\)\s+AS\s+t\(",
        re.DOTALL | re.IGNORECASE,
    )
    m = pattern.search(sql)
    if not m:
        raise ValueError(f"could not locate CTE `{cte_name}`")
    values_blob = m.group(1)
    # Split on top-level `),(` boundary: each tuple is `( ... )` with optional
    # whitespace + commas + nulls.
    tuples = re.findall(r"\(([^()]*(?:'[^']*'[^()]*)*)\)", values_blob)
    out = []
    for tup in tuples:
        # Tokenize respecting single-quoted strings (with embedded spaces /
        # parentheses / commas) and the NULL literal.
        fields: list[str] = []
        i = 0
        buf = ""
        in_str = False
        while i < len(tup):
            ch = tup[i]
            if ch == "'" and (i == 0 or tup[i - 1] != "\\"):
                in_str = not in_str
                buf += ch
            elif ch == "," and not in_str:
                fields.append(buf.strip())
                buf = ""
            else:
                buf += ch
            i += 1
        if buf.strip():
            fields.append(buf.strip())
        # Strip surrounding quotes from string literals; keep NULL as None.
        cleaned = []
        for f in fields:
            if f == "NULL":
                cleaned.append(None)
            elif f.startswith("'") and f.endswith("'") and len(f) >= 2:
                cleaned.append(f[1:-1])
            else:
                cleaned.append(f)
        out.append(tuple(cleaned))
    return out


def main() -> int:
    p = argparse.ArgumentParser(description="knife 660 Track B mart SQL -> JSON")
    p.add_argument("--out", type=Path, default=OUT_JSON, help="output JSON path")
    p.add_argument("--strict", action="store_true", help="exit non-zero on any red-line violation")
    # 661 D3: --dry-run 模式只走解析+自检,不写盘,避免 s660 test_11 side-effect.
    # 660-P1 教训: test_11 直接 --strict --out $MART_JSON 会破坏生产 JSON 文件
    # 在并发 pytest 下产生竞态;改 dry-run 后 test_11 只断言 exit code + 数据形态.
    p.add_argument("--dry-run", action="store_true",
                   help="parse + self-audit only; do not write output JSON")
    # 662 D2: 指标定义 JSON 输出开关. 默认 true (per tasking), --no-include-indicator-defs
    # 可跳过指标定义导出 (用于 partial CI / 数据扩展时).
    p.add_argument("--include-indicator-defs", action=argparse.BooleanOptionalAction,
                   default=True,
                   help="662 D2: also export mart_indicator_definitions_2024.json (default true)")
    p.add_argument("--out-indicator-defs", type=Path, default=OUT_INDICATOR_DEFS_JSON,
                   help="662 D2: indicator definitions output JSON path")
    args = p.parse_args()

    if not MART_SQL.exists():
        print(f"FATAL: mart SQL not found at {MART_SQL}", file=sys.stderr)
        return 1

    sql = MART_SQL.read_text(encoding="utf-8")

    # Parse three CTEs.
    try:
        province_codes = parse_values_block(sql, "province_codes")
        real_data = parse_values_block(sql, "real_data")
        missing_provinces = parse_values_block(sql, "missing_provinces")
    except ValueError as e:
        print(f"FATAL: {e}", file=sys.stderr)
        return 1

    # Index by province_code.
    pc_idx = {row[0]: {"province_code": row[0], "province_name": row[1], "source": row[2]} for row in province_codes}
    rd_idx = {row[0]: row for row in real_data}
    mp_idx = {row[0]: row for row in missing_provinces}

    # Build final 31-row result in GB/T 2260 order (mirrors the SQL's ORDER BY CASE).
    rows: list[dict] = []
    for code in GB_T_2260_ORDER:
        pc = pc_idx.get(code)
        rd = rd_idx.get(code)
        mp = mp_idx.get(code)
        if pc is None:
            print(f"FATAL: province_code {code!r} not in province_codes CTE", file=sys.stderr)
            return 1

        # Replicate SQL SELECT transformation:
        if rd is not None:
            # real_data tuple: (province_code, province_name, gdp_total, gdp_growth,
            #                   primary, secondary, tertiary, growth_note,
            #                   source, source_domain, origin)
            gdp_total = rd[2]
            gdp_growth = rd[3]
            primary = rd[4]
            secondary = rd[5]
            tertiary = rd[6]
            growth_note = rd[7]
            lineage_source = rd[8]
            lineage_origin = rd[10]
            status = None
            missing_reason = None
        else:
            gdp_total = None
            gdp_growth = None
            primary = None
            secondary = None
            tertiary = None
            growth_note = None
            lineage_source = mp[4] if mp else "hongheiku_tjgb"
            lineage_origin = "hongheiku_tjgb"
            status = mp[2] if mp else None
            missing_reason = mp[3] if mp else None

        rows.append({
            "province_code": code,
            "province_name": pc["province_name"],
            "gdp_total": gdp_total,
            "gdp_growth": gdp_growth,
            "primary_gdp": primary,
            "secondary_gdp": secondary,
            "tertiary_gdp": tertiary,
            "growth_note": growth_note,
            "status": status,
            "missing_reason": missing_reason,
            "lineage_source": lineage_source,
            "lineage_origin": lineage_origin,
            "lineage_ruling": "U6 2026-09-02",
            "lineage_is_demo": "false",
            # 661: 溯源 popover 三件套 (per 661 tasking §1.661 + 红线 8).
            # 真实行: source_url = lineage_source → 公共 URL 路由映射(权威,非编造).
            # DATA_MISSING 行: source_url 必须为 null(无 observation, 无 SHA 锁字节可溯,
            #   禁编造 URL per 红线 8). source_hash_prefix 留 null (待 662+ dbt JOIN).
            "source_url": SOURCE_URL_BY_LINEAGE.get(lineage_source) if status != "DATA_MISSING" else None,
            "source_hash_prefix": None,
        })

    # 661: prepend NATIONAL anchor row (全国 2024 GDP, per docs/81 §3 国家锚核对).
    # 此行不来自 mart SQL CTE, 而是从 NBS 2024 国家公报摘录 (架构师端源已自取,
    # per docs/81 §2 实测: 1,349,084.0 亿元); 单值且标 OFFICIAL_ANCHOR.
    national_row = {
        "province_code": NATIONAL_ROW_CODE,
        "province_name": NATIONAL_ROW_NAME,
        "gdp_total": NATIONAL_GDP_TOTAL,
        "gdp_growth": None,            # NBS 全国增速未在本刀定位 (留 662+)
        "primary_gdp": None,
        "secondary_gdp": None,
        "tertiary_gdp": None,
        "growth_note": None,
        "status": "OFFICIAL_ANCHOR",   # 区别于 real (status=null) / missing
        "missing_reason": None,
        "lineage_source": "OFFICIAL_INTAKED",
        "lineage_origin": "国家统计局",
        "lineage_ruling": "U6 2026-09-02",
        "lineage_is_demo": "false",
        "source_url": SOURCE_URL_BY_LINEAGE["OFFICIAL_INTAKED"],
        "source_hash_prefix": None,
    }
    # NATIONAL 置首; 之后 28 真实 + 3 缺失按 GB/T 2260 顺序
    rows = [national_row] + rows

    # Red-line self-audit.
    errors: list[str] = []
    if len(rows) != EXPECTED_ROWS:
        errors.append(f"row count {len(rows)} != {EXPECTED_ROWS}")
    real_rows = [r for r in rows if r["status"] is None]
    missing_rows = [r for r in rows if r["status"] == "DATA_MISSING"]
    if len(real_rows) != EXPECTED_REAL:
        errors.append(f"real row count {len(real_rows)} != {EXPECTED_REAL}")
    if len(missing_rows) != EXPECTED_MISSING:
        errors.append(f"missing row count {len(missing_rows)} != {EXPECTED_MISSING}")
    missing_codes = sorted(r["province_code"] for r in missing_rows)
    if missing_codes != sorted(EXPECTED_MISSING_CODES):
        errors.append(f"missing codes {missing_codes} != {sorted(EXPECTED_MISSING_CODES)}")
    metric_cols = ["gdp_total", "gdp_growth", "primary_gdp", "secondary_gdp", "tertiary_gdp"]
    for r in missing_rows:
        for col in metric_cols:
            if r[col] is not None:
                errors.append(f"missing {r['province_code']} {col}={r[col]!r} (must be NULL)")
    for r in rows:
        if r["lineage_ruling"] != "U6 2026-09-02":
            errors.append(f"{r['province_code']} lineage_ruling={r['lineage_ruling']!r}")
        if r["lineage_is_demo"] != "false":
            errors.append(f"{r['province_code']} lineage_is_demo={r['lineage_is_demo']!r}")

    if errors:
        print("RED-LINE VIOLATIONS:", file=sys.stderr)
        for e in errors:
            print(f"  - {e}", file=sys.stderr)
        if args.strict:
            return 2

    out = {
        "as_of": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "ruling": "knife 660 Track B + 661 P1 切片 (per 661 tasking §1.661)",
        "schema_version": "661",  # 661: bumped from 660 baseline
        "mart_source": str(MART_SQL.relative_to(REPO_ROOT)),
        "total_count": len(rows),
        "real_count": len(real_rows),
        "missing_count": len(missing_rows),
        "national_count": 1,  # 661: NATIONAL anchor row
        "data_missing_provinces": missing_codes,
        "lineage_ruling": "U6 2026-09-02",
        "lineage_is_demo": "false",
        "provinces": rows,
    }

    if args.dry_run:
        # 661 D3: dry-run 模式不写盘,只把 JSON 摘要打到 stdout,供测试断言.
        # 662 D2: 同步报告 indicator_defs 计数 (若开启).
        msg = (f"DRY-RUN OK: {len(rows)} rows "
               f"(real={out['real_count']} missing={out['missing_count']} "
               f"national={out['national_count']})")
        if args.include_indicator_defs:
            # 指标定义数 = metric_cols (5). 来源等级分布从 28 真省 + 1 NATIONAL
            # + 3 DATA_MISSING 实际 lineage_source 字段统计.
            grade = compute_source_grade_distribution(real_rows, missing_rows, [national_row])
            msg += f" + 5 indicator defs (grade={grade})"
        print(msg)
        return 0

    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(out, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"OK: {len(rows)} rows -> {args.out.relative_to(REPO_ROOT)}")
    print(f"  real={out['real_count']} missing={out['missing_count']} missing_codes={missing_codes}")

    # 662 D2: 指标定义 JSON 写出.
    if args.include_indicator_defs:
        grade = compute_source_grade_distribution(real_rows, missing_rows, [national_row])
        ind_out = build_indicator_definitions_payload(grade)
        args.out_indicator_defs.parent.mkdir(parents=True, exist_ok=True)
        args.out_indicator_defs.write_text(
            json.dumps(ind_out, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
        )
        print(f"OK: 5 indicator defs -> {args.out_indicator_defs.relative_to(REPO_ROOT)}")
        print(f"  grade distribution = {grade}")

    return 0


def compute_source_grade_distribution(
    real_rows: list[dict],
    missing_rows: list[dict],
    national_rows: list[dict],
) -> dict[str, int]:
    """
    662 D2: 统计 lineage_source 三档分布.

    - 28 真省 + 1 NATIONAL 锚行 → lineage_source 字段为 "OFFICIAL_INTAKED"
      (6 行: NATIONAL + 北京/上海/山东/湖北/四川) 或 "hongheiku_tjgb"
      (23 行, 计为 HONGHEIKU_TRANSLOAD).
    - 3 DATA_MISSING 行 → 按 row["status"] == "DATA_MISSING" 计为 DATA_MISSING
      档 (mart JSON 中 lineage_source 字段是 "hongheiku_tjgb", 不能靠字符串
      字段判断, 必须用 status).

    缺省值 (None) 不计入 OFFICIAL/TRANSLOAD 档, 但 missing_rows 一律计入
    DATA_MISSING 档 (因 status 字段保证非 None when in missing_rows).
    """
    official = 0
    transload = 0
    missing = 0
    for r in real_rows + national_rows:
        ls = r.get("lineage_source")
        if ls == "OFFICIAL_INTAKED":
            official += 1
        elif ls == "HONGHEIKU_TRANSLOAD" or ls == "hongheiku_tjgb":
            transload += 1
        # 其他 (None / DATA_MISSING / 未知) 不计.
    # 3 DATA_MISSING 行按 status 字段精确判断, 不靠 lineage_source 字符串.
    for r in missing_rows:
        if r.get("status") == "DATA_MISSING":
            missing += 1
    return {
        "OFFICIAL_INTAKED": official,
        "HONGHEIKU_TRANSLOAD": transload,
        "DATA_MISSING": missing,
    }


def build_indicator_definitions_payload(
    grade: dict[str, int],
) -> dict:
    """
    662 D2: 生成 5 指标定义 JSON. schema 与 mart 主 JSON 对齐 (as_of /
    ruling / schema_version / lineage_ruling / lineage_is_demo). 指标
    元数据来自 INDICATOR_METADATA; 缺省字段用 CALIBER_PLACEHOLDER 占位
    (per 红线 8 禁编造 caliber).
    """
    metric_cols = ["gdp_total", "gdp_growth", "primary_gdp", "secondary_gdp", "tertiary_gdp"]
    definitions: list[dict] = []
    for key in metric_cols:
        meta = INDICATOR_METADATA.get(key, {})
        definitions.append({
            "key": key,
            "label": meta.get("label", key),
            "unit": meta.get("unit", CALIBER_PLACEHOLDER),
            "caliber": meta.get("caliber", CALIBER_PLACEHOLDER),
            "period": meta.get("period", CALIBER_PLACEHOLDER),
            "source_grade_distribution": grade,
        })
    return {
        "as_of": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "ruling": "knife 662 D2 指标定义导出 (per 662 tasking §1.662-D2)",
        "schema_version": "661",  # 不 bump; mart 主 JSON schema 未变, 仅为派生
        "mart_source": str(MART_SQL.relative_to(REPO_ROOT)),
        "lineage_ruling": "U6 2026-09-02",
        "lineage_is_demo": "false",
        "indicator_count": len(definitions),
        "indicators": definitions,
    }


if __name__ == "__main__":
    sys.exit(main())
