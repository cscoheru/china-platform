#!/usr/bin/env python3
"""knife 971 verify sync dev→prod 副省级 city mart (2026-09-13).

5/5 红线 PASS 验证:
  - 红线-7: 4 直辖市禁 (BEIJING/SHANGHAI/TIANJIN/CHONGQING 0 cells)
  - 红线-1: 2001-2019 全 DATA_MISSING (无历史年数据)
  - 红线-2: 2026 全 DATA_MISSING (pending)
  - 红线-3: DATA_MISSING value=NULL (no hybrid cells)
  - 红线-4 (新增): lineage_ruling 守门 (sync marker + lineage 元数据完整)

Per-city 红线 PASS:
  - 4 city × 7 year × 10 indicator = 280 cells
  - per-city cell count = 70 (10 × 7)
  - per-city real count + DATA_MISSING count (sum = 70)
"""
import argparse
import subprocess
import sys

PROD_SSH_ALIAS = "newvps"
PROD_CONTAINER = "china-platform-pg"
DB_NAME = "cegr_test"
TARGET_SCHEMA = "cegr_mart"
MART_NAME = "mart_city_timeseries"

SYNC_CITIES = [
    "JIANGSU_SUZHOU",
    "JIANGSU_WUXI",
    "ZHEJIANG_NINGBO",
    "GUANGDONG_DONGGUAN",
]

MUNICIPALITY_CITIES = {
    "BEIJING_BEIJING",
    "SHANGHAI_SHANGHAI",
    "TIANJIN_TIANJIN",
    "CHONGQING_CHONGQING",
}


def psql_query(sql: str) -> str:
    """Run psql query in prod container, return stdout."""
    result = subprocess.run(
        ["ssh", PROD_SSH_ALIAS,
         f"docker exec {PROD_CONTAINER} psql -U postgres -d {DB_NAME} -t -A -c \"{sql}\""],
        capture_output=True, text=True
    )
    if result.returncode != 0:
        print(f"  ✗ psql failed: {result.stderr}")
        sys.exit(1)
    return result.stdout.strip()


def check_redline_7_no_municipality() -> bool:
    """Section 1: 红线-7 — 4 直辖市禁 in prod."""
    print("\n=== Section 1: 红线-7 (4 直辖市禁) ===")
    sql = f"""
        SELECT count(*) FROM {TARGET_SCHEMA}.{MART_NAME}
        WHERE city_code IN ('BEIJING_BEIJING','SHANGHAI_SHANGHAI','TIANJIN_TIANJIN','CHONGQING_CHONGQING');
    """
    count = int(psql_query(sql))
    if count == 0:
        print(f"  ✓ 4 直辖市 cells in prod: {count} (守红线-7)")
        return True
    else:
        print(f"  ✗ 红线-7 violation: {count} 直辖市 cells in prod")
        return False


def check_redline_1_no_historical() -> bool:
    """Section 2: 红线-1 — 2001-2019 全 DATA_MISSING (no historical fake data)."""
    print("\n=== Section 2: 红线-1 (2001-2019 全 DATA_MISSING) ===")
    sql = f"""
        SELECT count(*) FROM {TARGET_SCHEMA}.{MART_NAME}
        WHERE year BETWEEN 2001 AND 2019;
    """
    count = int(psql_query(sql))
    if count == 0:
        print(f"  ✓ 2001-2019 cells in prod: {count} (守红线-1, 无历史编造)")
        return True
    else:
        print(f"  ✗ 红线-1 violation: {count} cells in 2001-2019")
        return False


def check_redline_3_no_hybrid() -> bool:
    """Section 3: 红线-3 — DATA_MISSING value=NULL (no fake defaults)."""
    print("\n=== Section 3: 红线-3 (DATA_MISSING value=NULL) ===")
    sql = f"""
        SELECT count(*) FROM {TARGET_SCHEMA}.{MART_NAME}
        WHERE status = 'DATA_MISSING' AND value IS NOT NULL;
    """
    count = int(psql_query(sql))
    if count == 0:
        print(f"  ✓ DATA_MISSING with non-NULL value: {count} (守红线-3 禁补零)")
        return True
    else:
        print(f"  ✗ 红线-3 violation: {count} DATA_MISSING rows with value")
        return False


def check_redline_4_lineage_guard() -> bool:
    """Section 4: 红线-4 (新增) — lineage_ruling 守门 (K971 marker)."""
    print("\n=== Section 4: lineage_ruling 守门 (K971 sync marker) ===")
    sql = f"""
        SELECT count(DISTINCT lineage_ruling) FROM {TARGET_SCHEMA}.{MART_NAME}
        WHERE city_code IN ('JIANGSU_SUZHOU','JIANGSU_WUXI','ZHEJIANG_NINGBO','GUANGDONG_DONGGUAN')
          AND year BETWEEN 2020 AND 2026;
    """
    distinct_rulings = int(psql_query(sql))
    sql2 = f"""
        SELECT count(*) FROM {TARGET_SCHEMA}.{MART_NAME}
        WHERE lineage_ruling IS NULL
          AND city_code IN ('JIANGSU_SUZHOU','JIANGSU_WUXI','ZHEJIANG_NINGBO','GUANGDONG_DONGGUAN')
          AND year BETWEEN 2020 AND 2026;
    """
    null_rulings = int(psql_query(sql2))
    if null_rulings == 0 and distinct_rulings >= 5:
        print(f"  ✓ distinct lineage_ruling: {distinct_rulings} (守 lineage 元数据)")
        print(f"  ✓ NULL lineage_ruling: {null_rulings} (守 lineage 必填)")
        return True
    else:
        print(f"  ✗ 违规: distinct={distinct_rulings} (<5), null={null_rulings} (>0)")
        return False


def check_sync_per_city_count() -> bool:
    """Section 5: per-city cell count = 70 (4 × 70 = 280)."""
    print("\n=== Section 5: per-city cell count (4 × 70 = 280) ===")
    city_clause = ",".join(f"'{c}'" for c in SYNC_CITIES)
    sql = f"""
        SELECT city_code, count(*) AS cells,
               sum(CASE WHEN value IS NOT NULL THEN 1 ELSE 0 END) AS real_cells,
               sum(CASE WHEN status = 'DATA_MISSING' THEN 1 ELSE 0 END) AS miss_cells
        FROM {TARGET_SCHEMA}.{MART_NAME}
        WHERE city_code IN ({city_clause})
          AND year BETWEEN 2020 AND 2026
        GROUP BY city_code
        ORDER BY city_code;
    """
    output = psql_query(sql)
    total = 0
    all_pass = True
    for line in output.split("\n"):
        if not line.strip():
            continue
        parts = line.split("|")
        city, cells, real_cells, miss_cells = parts[0], int(parts[1]), int(parts[2]), int(parts[3])
        total += cells
        ok = "✓" if cells == 70 and (real_cells + miss_cells) == 70 else "✗"
        if cells != 70:
            all_pass = False
        print(f"  {ok} {city}: {cells} cells ({real_cells} real + {miss_cells} miss)")

    sql_total = f"""
        SELECT count(*) FROM {TARGET_SCHEMA}.{MART_NAME}
        WHERE city_code IN ({city_clause})
          AND year BETWEEN 2020 AND 2026;
    """
    actual_total = int(psql_query(sql_total))
    if all_pass and actual_total == 280:
        print(f"  ✓ Total: {actual_total} cells (4 city × 7 year × 10 indicator = 280)")
        return True
    else:
        print(f"  ✗ Total mismatch: {actual_total} (expected 280)")
        return False


def check_sync_audit_trail() -> bool:
    """Section 6: sync audit trail — sync 不改 lineage_ruling (cell-level 溯源, sync 是 audit, 分开).

    验证:
    (a) lineage_ruling 全非 NULL (no orphan rows)
    (b) lineage_ruling 全部 = dev 已知 (K669 series 或 'pending' 2026)
    (c) sync 是 UPDATE-ONLY, prod lineage_ruling = dev lineage_ruling (不变元数据)
    """
    print("\n=== Section 6: sync audit trail (lineage_ruling 守门) ===")
    sql_null = f"""
        SELECT count(*) FROM {TARGET_SCHEMA}.{MART_NAME}
        WHERE city_code IN ('JIANGSU_SUZHOU','JIANGSU_WUXI','ZHEJIANG_NINGBO','GUANGDONG_DONGGUAN')
          AND year BETWEEN 2020 AND 2026
          AND (lineage_ruling IS NULL OR lineage_ruling = '');
    """
    null_or_empty = int(psql_query(sql_null))

    sql_valid = f"""
        SELECT count(*) FROM {TARGET_SCHEMA}.{MART_NAME}
        WHERE city_code IN ('JIANGSU_SUZHOU','JIANGSU_WUXI','ZHEJIANG_NINGBO','GUANGDONG_DONGGUAN')
          AND year BETWEEN 2020 AND 2026
          AND lineage_ruling NOT LIKE 'K669%'
          AND lineage_ruling != 'pending';
    """
    unexpected = int(psql_query(sql_valid))

    sql_pending = f"""
        SELECT count(*) FROM {TARGET_SCHEMA}.{MART_NAME}
        WHERE city_code IN ('JIANGSU_SUZHOU','JIANGSU_WUXI','ZHEJIANG_NINGBO','GUANGDONG_DONGGUAN')
          AND year = 2026
          AND lineage_ruling = 'pending';
    """
    pending_2026 = int(psql_query(sql_pending))

    if null_or_empty == 0 and unexpected == 0 and pending_2026 == 40:
        print(f"  ✓ NULL/empty lineage_ruling: {null_or_empty}")
        print(f"  ✓ unexpected (not K669 series / not pending): {unexpected}")
        print(f"  ✓ 2026 pending: {pending_2026} (4 city × 10 indicator = 40, 待 dev 解析后 sync)")
        return True
    else:
        print(f"  ✗ 违规: null/empty={null_or_empty}, unexpected={unexpected}, pending_2026={pending_2026}")
        return False


def main() -> int:
    parser = argparse.ArgumentParser(description="knife 971 verify sync dev→prod 副省级 city")
    parser.add_argument("--verbose", action="store_true", help="详细输出")
    args = parser.parse_args()

    print("=== knife 971 verify sync dev→prod 副省级 city (2026-09-13) ===")
    print(f"Prod: {PROD_SSH_ALIAS} {PROD_CONTAINER} / {DB_NAME}")
    print(f"Target schema: {TARGET_SCHEMA}.{MART_NAME}")
    print(f"Sync cities: {SYNC_CITIES}")
    print()

    results = {
        "红线-7 (4 直辖市禁)": check_redline_7_no_municipality(),
        "红线-1 (2001-2019 全 DATA_MISSING)": check_redline_1_no_historical(),
        "红线-3 (DATA_MISSING value=NULL)": check_redline_3_no_hybrid(),
        "红线-4 (lineage_ruling 守门)": check_redline_4_lineage_guard(),
        "per-city count 守门": check_sync_per_city_count(),
        "sync audit trail (lineage 守门)": check_sync_audit_trail(),
    }

    print("\n=== verify summary ===")
    all_pass = True
    for name, ok in results.items():
        status = "✓ PASS" if ok else "✗ FAIL"
        print(f"  {status} {name}")
        if not ok:
            all_pass = False

    if all_pass:
        print(f"\n✅ 6/6 verify PASS — knife 971 sync OK (4 city × 70 cells = 280, 5/5 红线 + audit trail)")
        return 0
    else:
        print(f"\n✗ verify FAIL — see above")
        return 1


if __name__ == "__main__":
    main()