#!/usr/bin/env python3
"""
Knife 934b deploy — generate unified SQL to load seeds + apply marts on newvps postgres
=============================================================================

Pattern (per newvps 部署约束, see memory china-platform-fastapi-missing-on-newvps):
- newvps prod compose has NO host port mapping for postgres (only puer-net internal 5432)
- newvps has NO dbt CLI installed
- dbt CLI 与 Python 3.14 不兼容 (per 663 Gap 1)
- Solution: substitute jinja refs locally + docker exec -i psql pipe

Generates: /tmp/934b/deploy_batch_934b.sql
- DROP + CREATE 5 seed tables (cegr_staging)
- COPY 5 seed CSVs
- DROP + CREATE TABLE AS mart_province_timeseries (with jinja refs substituted)
- DROP + CREATE TABLE AS mart_city_timeseries (no jinja)

Then upload + apply on newvps.
"""
import re
from pathlib import Path

PROJECT_ROOT = Path("/Users/kjonekong/projects/china platform")
MART_PROVINCE_SQL = PROJECT_ROOT / "dbt/models/marts/mart_province_timeseries.sql"
MART_CITY_SQL = PROJECT_ROOT / "dbt/models/marts/mart_city_timeseries.sql"
SEED_DIR = PROJECT_ROOT / "dbt/seeds"
OUT_DIR = Path("/tmp/934b")
OUT_DIR.mkdir(parents=True, exist_ok=True)
OUT_FILE = OUT_DIR / "deploy_batch_934b.sql"

# Seed CSVs (5 years) — column types match dbt seed schema (13 cols)
SEED_YEARS = [2021, 2022, 2023, 2024, 2025]
SEED_COLS = [
    ("province_code", "text"),
    ("province_name_cn", "text"),
    ("year", "integer"),
    ("value", "numeric"),
    ("unit", "text"),
    ("indicator_key", "text"),
    ("indicator_label_cn", "text"),
    ("status", "text"),
    ("missing_reason", "text"),
    ("lineage_source_type", "text"),
    ("lineage_origin", "text"),
    ("lineage_ruling", "text"),
    ("lineage_is_demo", "text"),
]


def read_file(p: Path) -> str:
    return p.read_text(encoding="utf-8")


def strip_dbt_config_block(sql: str) -> str:
    """Strip leading {{ config(...) }} jinja block (lines 1-7 typically)."""
    # Match opening {{ on its own line + config(...) + closing }}
    pattern = re.compile(r"^\{\{\s*\n\s*config\([^)]*\)\s*\n\}\}\s*\n", re.MULTILINE)
    return pattern.sub("", sql, count=1)


def substitute_jinja_refs(sql: str, ref_map: dict) -> str:
    """Replace {{ ref('xxx') }} with target string."""
    for ref_name, replacement in ref_map.items():
        # Match {{ ref('ref_name') }} with optional whitespace
        sql = re.sub(
            r"\{\{\s*ref\(\s*['\"]" + re.escape(ref_name) + r"['\"]\s*\)\s*\}\}",
            replacement,
            sql,
        )
    return sql


def build_seed_section() -> str:
    """Build DROP + CREATE TABLE + COPY for 5 seed CSVs."""
    sections = []
    sections.append("-- =================================================================")
    sections.append("-- SECTION 1: 5 seed CSVs → cegr_staging.seed_hongheiku_timeseries_202X")
    sections.append("-- =================================================================")

    cols_ddl = ",\n    ".join(f"{name} {dtype}" for name, dtype in SEED_COLS)

    for year in SEED_YEARS:
        csv_path = SEED_DIR / f"seed_hongheiku_timeseries_{year}.csv"
        if not csv_path.exists():
            raise FileNotFoundError(f"Seed CSV missing: {csv_path}")

        sections.append(f"\n-- Seed year {year}: {csv_path.name} ({csv_path.stat().st_size} bytes)")
        sections.append(f"DROP TABLE IF EXISTS cegr_staging.seed_hongheiku_timeseries_{year} CASCADE;")
        sections.append(f"CREATE TABLE cegr_staging.seed_hongheiku_timeseries_{year} (\n    {cols_ddl}\n);")

        # SQL COPY (server-side, reads from container path /tmp/934b_seeds/)
        # CSVs are docker cp'd to container BEFORE running this SQL
        sections.append(rf"COPY cegr_staging.seed_hongheiku_timeseries_{year} FROM '/tmp/934b_seeds/seed_hongheiku_timeseries_{year}.csv' WITH (FORMAT csv, HEADER true, ENCODING 'UTF8');")

    return "\n".join(sections)


def _ensure_semicolon(sql: str) -> str:
    """Ensure SQL ends with exactly one semicolon (CRITICAL for CREATE TABLE AS)."""
    return sql.rstrip().rstrip(";").rstrip() + ";\n"


def build_mart_province_section() -> str:
    """Build DROP + CREATE TABLE AS for mart_province_timeseries (with jinja substituted)."""
    raw = read_file(MART_PROVINCE_SQL)
    stripped = strip_dbt_config_block(raw)
    ref_map = {f"seed_hongheiku_timeseries_{y}": f"cegr_staging.seed_hongheiku_timeseries_{y}" for y in SEED_YEARS}
    rendered = substitute_jinja_refs(stripped, ref_map)

    # Verify no jinja remains
    if "{{" in rendered or "}}" in rendered:
        leftover = re.findall(r"\{\{[^}]+\}\}", rendered)
        raise ValueError(f"Leftover jinja refs in mart_province: {leftover}")

    sections = []
    sections.append("\n-- =================================================================")
    sections.append("-- SECTION 2: mart_province_timeseries (DROP + CREATE TABLE AS)")
    sections.append(f"-- Source: {MART_PROVINCE_SQL.name} ({len(raw)} chars, jinja refs substituted)")
    sections.append("-- =================================================================")
    sections.append("DROP TABLE IF EXISTS cegr_mart.mart_province_timeseries CASCADE;")
    sections.append("CREATE TABLE cegr_mart.mart_province_timeseries AS")
    sections.append(_ensure_semicolon(rendered))

    return "\n".join(sections)


def _strip_trailing_commas_in_values(body: str) -> str:
    """Strip trailing comma from the LAST VALUES tuple (whichever is last).

    PostgreSQL VALUES syntax: comma BETWEEN tuples (separator), NO trailing comma
    before `) AS t(...)`. The heredoc body has trailing commas on every tuple
    (CSV-style); the very last tuple — whether or not it had a trailing comma —
    must end without one. All earlier tuples keep their commas (separators).

    Worked example (2024 body — last tuple already had no comma):
      BEFORE: ...retail', '1232.31'::numeric),\\n  trade', '801.05'::numeric)
      AFTER:  ...retail', '1232.31'::numeric),\\n  trade', '801.05'::numeric)
      (no change; last tuple already correct)

    Worked example (2022/2023 body — last tuple had trailing comma):
      BEFORE: ...trade', 513.57::numeric)\\n  ) AS t(...)
      AFTER:  ...trade', 513.57::numeric\\n  ) AS t(...)
      (stripped from last tuple only)
    """
    lines = body.split("\n")
    # Find the last VALUES tuple line (any line with `(...)::numeric` style content)
    last_tuple_idx = -1
    for i in range(len(lines) - 1, -1, -1):
        stripped = lines[i].rstrip()
        if "(" in stripped and "::" in stripped and ")" in stripped:
            last_tuple_idx = i
            break
    if last_tuple_idx >= 0:
        lines[last_tuple_idx] = lines[last_tuple_idx].rstrip().rstrip(",")
    return "\n".join(lines)


def substitute_heredoc_bodies(sql: str) -> str:
    """Replace $(cat /tmp/.../cte_YYYY_body.txt) bash heredoc placeholders with file contents.

    Pattern from knife 669fix-b-2020/2022/2023/2024 apply workflow — bodies are stored in
    /tmp/669b/ for traceability, and the SQL file references them via $(cat ...) for
    in-place shell substitution. Since we're piping via docker exec -i psql (no shell),
    we substitute Python-side here.
    """
    pattern = re.compile(r"\$\(cat\s+([^\)]+)\)")
    matches = pattern.findall(sql)
    for path_str in matches:
        path = Path(path_str.strip())
        if not path.exists():
            raise FileNotFoundError(f"Heredoc body missing: {path}")
        body = path.read_text(encoding="utf-8")
        # Strip trailing commas in VALUES (postgres disallows; see _strip_trailing_commas_in_values)
        body = _strip_trailing_commas_in_values(body)
        sql = sql.replace(f"$(cat {path_str})", body)
    if matches:
        print(f"    substituted {len(matches)} heredoc bodies: {[Path(m.strip()).name for m in matches]}")
    return sql


def build_mart_city_section() -> str:
    """Build DROP + CREATE TABLE AS for mart_city_timeseries (no jinja)."""
    raw = read_file(MART_CITY_SQL)

    # Verify no jinja in mart_city
    if "{{" in raw or "}}" in raw:
        leftover = re.findall(r"\{\{[^}]+\}\}", raw)
        raise ValueError(f"Unexpected jinja in mart_city: {leftover}")

    # Substitute bash heredoc bodies (knife 669fix pattern)
    rendered = substitute_heredoc_bodies(raw)

    sections = []
    sections.append("\n-- =================================================================")
    sections.append("-- SECTION 3: mart_city_timeseries (DROP + CREATE TABLE AS)")
    sections.append(f"-- Source: {MART_CITY_SQL.name} ({len(raw)} chars, no jinja)")
    sections.append("-- =================================================================")
    sections.append("DROP TABLE IF EXISTS cegr_mart.mart_city_timeseries CASCADE;")
    sections.append("CREATE TABLE cegr_mart.mart_city_timeseries AS")
    sections.append(_ensure_semicolon(rendered))

    return "\n".join(sections)


def main():
    print("=== knife 934b deploy SQL generator ===")
    print(f"OUT: {OUT_FILE}")

    seed_section = build_seed_section()
    print(f"  seed section: {len(seed_section)} chars")

    province_section = build_mart_province_section()
    print(f"  mart_province section: {len(province_section)} chars")

    city_section = build_mart_city_section()
    print(f"  mart_city section: {len(city_section)} chars")

    header = [
        "-- knife 934b unified deploy SQL (newvps prod postgres)",
        "-- Generated by scripts/deploy_batch_934b.py",
        f"-- Seeds: {len(SEED_YEARS)} years × cegr_staging.seed_hongheiku_timeseries_YYYY",
        "-- Marts: cegr_mart.mart_province_timeseries + cegr_mart.mart_city_timeseries",
        "-- Apply via: docker exec -i china-platform-pg psql -U postgres -d cegr_test < this file",
        "",
    ]

    OUT_FILE.write_text("\n".join(header) + "\n" + seed_section + "\n" + province_section + "\n" + city_section + "\n", encoding="utf-8")
    print(f"\n  wrote {OUT_FILE} ({OUT_FILE.stat().st_size} bytes)")
    print(f"  preview (first 20 lines):")
    print("\n".join(f"    {line}" for line in OUT_FILE.read_text().splitlines()[:20]))


if __name__ == "__main__":
    main()
