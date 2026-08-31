"""M2-a — 2024 GDP coverage empty matrix report (per docs/56 / knife 631 §1.C).

For 31 省级行政区 (per `cegr.geo_entity` where level='PROVINCE') and the year 2024,
print the coverage status of the official GDP table source (per
`source_registry/m2_2024_gdp_inventory.csv`):

  - province_zh
  - geo_code
  - inventory_status (PENDING | BLOCKED | MISSING | FETCHED)
  - inventory_url    (candidate_url, 锁定 raw 表级 URL)
  - observation_rows (count of cegr.observation with this geo + 2024; 0 in M2-a)
  - missing_reason   (if any)
  - verdict          (COVERED | BLOCKED | PENDING | EMPTY)

M2-a allows 全 0 有值 (empty matrix); exit 0 always.

Usage:
  python scripts/report_m2_gdp_coverage.py [--out path/to/coverage.md]

DSN: ${CEGR_DSN:-postgresql://postgres:postgres@127.0.0.1:55440/cegr_test}
"""
from __future__ import annotations

import argparse
import csv
import os
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
INVENTORY_CSV = REPO_ROOT / "source_registry" / "m2_2024_gdp_inventory.csv"
YEAR = 2024


def get_dsn() -> str:
    return os.environ.get(
        "CEGR_DSN",
        os.environ.get(
            "STAGE0_DSN",
            "postgresql://postgres:postgres@127.0.0.1:55440/cegr_test",
        ),
    )


def _connect():
    try:
        import psycopg2  # type: ignore
    except ImportError:
        sys.exit("ERROR: psycopg2 not installed. Run: pip install psycopg2-binary")
    return psycopg2.connect(get_dsn())


def _load_inventory() -> dict[str, dict[str, str]]:
    """Load the M2 2024 GDP inventory CSV, keyed by geo_code."""
    out: dict[str, dict[str, str]] = {}
    with INVENTORY_CSV.open("r", encoding="utf-8") as fh:
        reader = csv.DictReader(fh)
        for row in reader:
            code = (row.get("geo_code") or "").strip()
            if code:
                out[code] = row
    return out


def _obs_count_by_geo(cur) -> dict[str, int]:
    """Return a dict {geo_entity_id: count} of observation rows for 2024 GDP.

    Joins geo_entity (PROVINCE) -> observation rows where
    observation.period_start falls in 2024 (calendar year).
    Returns 0 if no rows.
    """
    cur.execute(
        """
        SELECT g.id::text, COUNT(o.id)
        FROM cegr.geo_entity g
        LEFT JOIN cegr.observation o
            ON o.geo_entity_id = g.id
            AND o.period_start >= %s::date
            AND o.period_start <  %s::date
        WHERE g.level = 'PROVINCE'
        GROUP BY g.id
        """,
        (f"{YEAR}-01-01", f"{YEAR + 1}-01-01"),
    )
    return dict(cur.fetchall())


def main() -> int:
    p = argparse.ArgumentParser(
        description="M2-a 2024 GDP coverage report (knife 631 §1.C)"
    )
    p.add_argument(
        "--out",
        type=Path,
        default=None,
        help="Optional markdown output path",
    )
    args = p.parse_args()

    inventory = _load_inventory()

    with _connect() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT id::text, canonical_name, canonical_name_en
                FROM cegr.geo_entity
                WHERE level = 'PROVINCE'
                ORDER BY canonical_name
                """
            )
            provinces = cur.fetchall()  # list of (id, zh, en)
            obs_count = _obs_count_by_geo(cur)

    # Build the report rows
    lines: list[str] = []
    lines.append(f"# M2-a 2024 GDP coverage matrix ({len(provinces)} 省级)")
    lines.append("")
    lines.append(
        "| province_zh | geo_code | inventory_status | inventory_url | "
        "observation_rows | missing_reason | verdict |"
    )
    lines.append(
        "| --- | --- | --- | --- | --- | --- | --- |"
    )

    summary = {"COVERED": 0, "BLOCKED": 0, "PENDING": 0, "EMPTY": 0}

    # Build a map geo_code (per inventory) -> admin_code from M1 seed
    # We don't have direct mapping in this script; use inventory row directly.
    inv_by_name: dict[str, dict[str, str]] = {
        r.get("province_zh", ""): r for r in inventory.values()
    }

    for geo_id, zh, _en in provinces:
        inv = inv_by_name.get(zh) or {}
        inv_status = (inv.get("status") or "MISSING").strip()
        inv_url = inv.get("candidate_url", "") or ""
        missing = (inv.get("missing_reason") or "").strip()
        n_obs = obs_count.get(geo_id, 0)

        if n_obs > 0:
            verdict = "COVERED"
        elif inv_status == "BLOCKED":
            verdict = "BLOCKED"
        elif inv_status == "MISSING":
            verdict = "EMPTY"
        else:
            verdict = "PENDING"

        summary[verdict] += 1
        lines.append(
            f"| {zh} | {inv.get('geo_code', '')} | {inv_status} | "
            f"{inv_url} | {n_obs} | {missing} | {verdict} |"
        )

    lines.append("")
    lines.append("## Summary")
    lines.append("")
    lines.append(f"- Total 省级 rows: **{len(provinces)}**")
    lines.append(f"- COVERED (real observation 2024 GDP): **{summary['COVERED']}**")
    lines.append(f"- BLOCKED (inventory status=BLOCKED): **{summary['BLOCKED']}**")
    lines.append(f"- PENDING (inventory status=PENDING): **{summary['PENDING']}**")
    lines.append(f"- EMPTY (no inventory row): **{summary['EMPTY']}**")
    lines.append("")
    lines.append(
        f"KPI (per knife 631 §2): geo×indicator×year=2024 覆盖率 = "
        f"**{summary['COVERED']}/{len(provinces)}** = "
        f"{(summary['COVERED'] / max(len(provinces), 1)) * 100:.1f}%"
    )
    lines.append("")
    lines.append(
        "M2-a allows 全 0 有值 (empty matrix); 此报告仅记录基线状态。"
    )

    text = "\n".join(lines) + "\n"

    # Always print to stdout
    print(text)

    # Optionally write to file
    if args.out is not None:
        args.out.write_text(text, encoding="utf-8")
        print(f"[OK] wrote coverage report to {args.out}", file=sys.stderr)

    # exit 0 always (per knife 631 §1.C)
    return 0


if __name__ == "__main__":
    sys.exit(main())