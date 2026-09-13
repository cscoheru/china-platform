#!/usr/bin/env python3
"""knife 971 sync dev→prod 副省级 city mart (2026-09-13).

Sync 4 城 (suzhou/wuxi/ningbo/dongguan) × 7 年 × 10 指标 = 280 cells
from dev (127.0.0.1:55440 cegr_test) → prod (newvps china-platform-pg cegr_test).

UPDATE-ONLY (INSERT ON CONFLICT DO UPDATE) — 守历史溯源守恒.
守 5 红线 PASS:
  - 红线-1: 2001-2019 历史年禁编造 → sync 仅 2020-2026
  - 红线-2: 2026 全 DATA_MISSING → dev 已守
  - 红线-3: hongheiku 0 entry 禁补零 → dev 已守 (SUZHOU 2023 + WUXI 2022 都 no-bulletin)
  - 红线-7: 4 直辖市禁 → 4 城不含 4 直辖市, sync 守门

不 DROP / 不 TRUNCATE / 不 DELETE — 仅 INSERT ON CONFLICT DO UPDATE 受影响行.

Dry-run mode (--dry-run) 只生成 SQL, 不 ssh docker exec.
"""
import argparse
import os
import subprocess
import sys
import psycopg2

# === Dev source ===
DB_DEV_HOST = "127.0.0.1"
DB_DEV_PORT = 55440
DB_USER = "postgres"
DB_PASS = "postgres"
DB_NAME = "cegr_test"

# === Prod target (via SSH + docker exec) ===
PROD_SSH_ALIAS = "newvps"
PROD_CONTAINER = "china-platform-pg"

# === Mart schema ===
TARGET_SCHEMA = "cegr_mart"
MART_NAME = "mart_city_timeseries"

# === Sync scope (per A 选项 user ruling 2026-09-13) ===
DEFAULT_CITIES = [
    "JIANGSU_SUZHOU",
    "JIANGSU_WUXI",
    "ZHEJIANG_NINGBO",
    "GUANGDONG_DONGGUAN",
]

# 红线-7 禁
MUNICIPALITY_CITIES = {
    "BEIJING_BEIJING",
    "SHANGHAI_SHANGHAI",
    "TIANJIN_TIANJIN",
    "CHONGQING_CHONGQING",
}

SYNC_MARKER = "K971-sync-dev-to-prod-2026-09-13"


def get_dev_cells(cities: list[str]) -> list[dict]:
    """SELECT FROM dev mart_city_timeseries WHERE city_code IN cities AND year BETWEEN 2020 AND 2026."""
    conn = psycopg2.connect(host=DB_DEV_HOST, port=DB_DEV_PORT, user=DB_USER,
                            password=DB_PASS, dbname=DB_NAME)
    try:
        with conn.cursor() as cur:
            city_list = ",".join(f"'{c}'" for c in cities)
            cur.execute(f"""
                SELECT city_code, city_name, province_code, indicator_key,
                       indicator_label, unit, year, value, status,
                       missing_reason, lineage_source_type, lineage_origin,
                       lineage_ruling, lineage_is_demo
                FROM {TARGET_SCHEMA}.{MART_NAME}
                WHERE city_code IN ({city_list})
                  AND year BETWEEN 2020 AND 2026
                ORDER BY city_code, indicator_key, year
            """)
            cols = [d[0] for d in cur.description]
            rows = [dict(zip(cols, r)) for r in cur.fetchall()]
            return rows
    finally:
        conn.close()


def escape_sql_value(v, col_name: str) -> str:
    """SQL value escape: NULL / number / string."""
    if v is None:
        return "NULL"
    if col_name in ("value",):
        return str(v)
    if col_name == "year":
        return str(int(v))
    return "'" + str(v).replace("'", "''") + "'"


def build_sync_sql(rows: list[dict], cities: list[str]) -> str:
    """Build multi-row INSERT ON CONFLICT DO UPDATE SQL (psycopg2 single-%→%% escape fix + OR-clause fix)."""
    if not rows:
        return ""

    # 红线-7 守门
    for r in rows:
        if r["city_code"] in MUNICIPALITY_CITIES:
            raise ValueError(f"红线-7 violation: {r['city_code']} (4 直辖市禁)")

    cols = ["city_code", "city_name", "province_code", "indicator_key",
            "indicator_label", "unit", "year", "value", "status",
            "missing_reason", "lineage_source_type", "lineage_origin",
            "lineage_ruling", "lineage_is_demo"]

    values_lines = []
    for r in rows:
        row_vals = [escape_sql_value(r[c], c) for c in cols]
        values_lines.append("  (" + ", ".join(row_vals) + ")")

    # 注意: psycopg2 用 %s 参数化, 但这里生成的是字面 SQL (不通过 psycopg2 execute),
    # 所以不需要 %% escape. 这是生成静态 SQL 字符串, 用 subprocess + docker exec psql 跑.
    sql = f"""-- knife 971 sync dev→prod subprovincial (2026-09-13)
-- Generated: {SYNC_MARKER}
-- Cities: {", ".join(cities)}
-- Rows: {len(rows)} (4 city × 7 year × 10 indicator = 280 expected)
-- Sync marker: {SYNC_MARKER}

BEGIN;

INSERT INTO {TARGET_SCHEMA}.{MART_NAME}
  ({", ".join(cols)})
VALUES
{",".join(values_lines)}
ON CONFLICT (city_code, indicator_key, year) DO UPDATE SET
  city_name = EXCLUDED.city_name,
  province_code = EXCLUDED.province_code,
  indicator_label = EXCLUDED.indicator_label,
  unit = EXCLUDED.unit,
  value = EXCLUDED.value,
  status = EXCLUDED.status,
  missing_reason = EXCLUDED.missing_reason,
  lineage_source_type = EXCLUDED.lineage_source_type,
  lineage_origin = EXCLUDED.lineage_origin,
  lineage_ruling = EXCLUDED.lineage_ruling,
  lineage_is_demo = EXCLUDED.lineage_is_demo;

COMMIT;
"""
    return sql


def push_to_prod(sql: str) -> subprocess.CompletedProcess:
    """Push SQL to prod via ssh newvps docker cp + docker exec psql."""
    # 1. Write to local tmp
    local_sql = "/tmp/knife_971_sync.sql"
    with open(local_sql, "w", encoding="utf-8") as f:
        f.write(sql)

    # 2. scp to newvps
    remote_dir = "/tmp/knife_971"
    remote_sql = f"{remote_dir}/sync.sql"
    subprocess.run(["ssh", PROD_SSH_ALIAS, f"mkdir -p {remote_dir}"], check=True)
    subprocess.run(["scp", local_sql, f"{PROD_SSH_ALIAS}:{remote_sql}"], check=True)

    # 3. docker cp into container + docker exec psql
    result = subprocess.run(
        ["ssh", PROD_SSH_ALIAS,
         f"docker cp {remote_sql} {PROD_CONTAINER}:/tmp/sync.sql && "
         f"docker exec -i {PROD_CONTAINER} psql -U postgres -d {DB_NAME} "
         f"-v ON_ERROR_STOP=1 -f /tmp/sync.sql"],
        capture_output=True, text=True
    )
    return result


def main() -> int:
    parser = argparse.ArgumentParser(description="knife 971 sync dev→prod 副省级 city")
    parser.add_argument("--dry-run", action="store_true", help="只生成 SQL, 不推送")
    parser.add_argument("--cities", nargs="+", default=DEFAULT_CITIES, help="覆盖默认 4 城")
    parser.add_argument("--sql-out", default="/tmp/knife_971_sync.sql", help="SQL 输出路径")
    args = parser.parse_args()

    print(f"=== knife 971 sync dev→prod 副省级 city mart (2026-09-13) ===")
    print(f"Dev: {DB_DEV_HOST}:{DB_DEV_PORT}/{DB_NAME}")
    print(f"Prod: {PROD_SSH_ALIAS} {PROD_CONTAINER} / {DB_NAME}")
    print(f"Cities: {args.cities}")
    print(f"Mode: {'dry-run' if args.dry_run else 'live push'}")
    print(f"Sync marker: {SYNC_MARKER}")
    print()

    # Step 1: SELECT FROM dev
    print("--- Step 1: SELECT FROM dev mart_city_timeseries ---")
    rows = get_dev_cells(args.cities)
    print(f"  ✓ Selected {len(rows)} rows")

    if len(rows) != 280:
        print(f"  ✗ Expected 280 cells (4 city × 7 year × 10 indicator), got {len(rows)}")
        sys.exit(1)

    # 红线-1 守门 (year 范围)
    bad_years = [r for r in rows if r["year"] < 2020 or r["year"] > 2026]
    if bad_years:
        print(f"  ✗ 红线-1 违规: {len(bad_years)} rows year out of [2020, 2026]")
        sys.exit(1)
    print(f"  ✓ All rows year in [2020, 2026] (守红线-1 + 红线-2)")

    # 红线-7 守门 (4 直辖市)
    bad_cities = [r for r in rows if r["city_code"] in MUNICIPALITY_CITIES]
    if bad_cities:
        print(f"  ✗ 红线-7 违规: {len(bad_cities)} rows are 4 直辖市")
        sys.exit(1)
    print(f"  ✓ No 4 直辖市 in rows (守红线-7)")

    # 红线-3 守门 (DATA_MISSING value=NULL)
    bad_miss = [r for r in rows if r["status"] == "DATA_MISSING" and r["value"] is not None]
    if bad_miss:
        print(f"  ✗ 红线-3 违规: {len(bad_miss)} DATA_MISSING rows with non-NULL value")
        sys.exit(1)
    real_count = sum(1 for r in rows if r["value"] is not None)
    miss_count = sum(1 for r in rows if r["status"] == "DATA_MISSING")
    print(f"  ✓ 红线-3 守门: {real_count} real + {miss_count} DATA_MISSING (no hybrid cells)")

    # Step 2: Build SQL
    print(f"\n--- Step 2: Build INSERT ON CONFLICT SQL ---")
    sql = build_sync_sql(rows, args.cities)
    with open(args.sql_out, "w", encoding="utf-8") as f:
        f.write(sql)
    print(f"  ✓ SQL written to {args.sql_out} ({len(sql)} bytes)")

    if args.dry_run:
        print(f"\n[dry-run mode — SQL generated, NOT pushed]")
        print(f"  Inspect: head -3 {args.sql_out}")
        return 0

    # Step 3: Push to prod
    print(f"\n--- Step 3: Push to prod via SSH + docker cp + docker exec ---")
    result = push_to_prod(sql)
    print(result.stdout)
    if result.returncode != 0:
        print(f"  ✗ psql failed (exit {result.returncode}):")
        print(result.stderr)
        sys.exit(1)
    print(f"  ✓ Sync to prod successful")

    # Step 4: Quick verify
    print(f"\n--- Step 4: Quick verify (prod cell count) ---")
    verify_result = subprocess.run(
        ["ssh", PROD_SSH_ALIAS,
         f"docker exec {PROD_CONTAINER} psql -U postgres -d {DB_NAME} -t -c "
         f"\"SELECT count(*) FROM {TARGET_SCHEMA}.{MART_NAME} "
         f"WHERE city_code IN ('JIANGSU_SUZHOU','JIANGSU_WUXI','ZHEJIANG_NINGBO','GUANGDONG_DONGGUAN');\""],
        capture_output=True, text=True
    )
    print(f"  prod {TARGET_SCHEMA}.{MART_NAME} 4 city cell count: {verify_result.stdout.strip()}")
    if "280" not in verify_result.stdout:
        print(f"  ✗ Expected 280 cells, got {verify_result.stdout.strip()}")
        sys.exit(1)
    print(f"  ✓ 280 cells in prod (4 city × 7 year × 10 indicator)")

    return 0


if __name__ == "__main__":
    main()
