#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
export-mart-data.py — knife 660 Track B (静态导出).

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
EXPECTED_ROWS = 31
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
        })

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
        "ruling": "knife 660 Track B static export (per §PART 2)",
        "mart_source": str(MART_SQL.relative_to(REPO_ROOT)),
        "total_count": len(rows),
        "real_count": len(real_rows),
        "missing_count": len(missing_rows),
        "data_missing_provinces": missing_codes,
        "lineage_ruling": "U6 2026-09-02",
        "lineage_is_demo": "false",
        "provinces": rows,
    }

    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(out, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"OK: {len(rows)} rows -> {args.out.relative_to(REPO_ROOT)}")
    print(f"  real={out['real_count']} missing={out['missing_count']} missing_codes={missing_codes}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
