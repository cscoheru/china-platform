"""M2-a/b — 2024 GDP coverage report (per docs/56 / knife 631 §1.C, knife 633 §3.D).

For 31 省级行政区 + 1 全国主体 (per `cegr.geo_entity` where level IN
('PROVINCE','COUNTRY')) and the year 2024, print the coverage status of
the official GDP table source (per `source_registry/m2_2024_gdp_inventory.csv`):

  - province_zh (or 国家)
  - geo_code
  - inventory_status (PENDING | BLOCKED | MISSING | FETCHED)
  - inventory_url    (candidate_url, 锁定 raw 表级 URL)
  - observation_rows (count of cegr.observation with this geo + 2024)
  - missing_reason   (if any)
  - verdict          (COVERED | BLOCKED | PENDING | EMPTY)

M2-a allows 全 0 有值 (empty matrix); M2-b KPI is 省级 COVERED ≥5/31,
国家 row tracked separately (per knife 633 §2).

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

    Joins geo_entity (PROVINCE + COUNTRY) -> observation rows where
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
        WHERE g.level IN ('PROVINCE', 'COUNTRY')
        GROUP BY g.id
        """,
        (f"{YEAR}-01-01", f"{YEAR + 1}-01-01"),
    )
    return dict(cur.fetchall())


def main() -> int:
    p = argparse.ArgumentParser(
        description="M2-a/b 2024 GDP coverage report (knife 631 §1.C + "
                    "633 §3.D)"
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
                SELECT id::text, canonical_name, canonical_name_en, level
                FROM cegr.geo_entity
                WHERE level IN ('PROVINCE', 'COUNTRY')
                ORDER BY CASE level WHEN 'COUNTRY' THEN 0 ELSE 1 END,
                         canonical_name
                """
            )
            geos = cur.fetchall()  # list of (id, zh, en, level)
            obs_count = _obs_count_by_geo(cur)

    # Build the report rows
    lines: list[str] = []
    lines.append(
        f"# M2-b 2024 GDP coverage matrix "
        f"({sum(1 for _, _, _, l in geos if l == 'PROVINCE')} 省级 + "
        f"{sum(1 for _, _, _, l in geos if l == 'COUNTRY')} 全国)"
    )
    lines.append("")
    lines.append(
        "| entity_zh | level | geo_code | inventory_status | inventory_url | "
        "observation_rows | missing_reason | verdict |"
    )
    lines.append(
        "| --- | --- | --- | --- | --- | --- | --- | --- |"
    )

    summary = {"COVERED": 0, "BLOCKED": 0, "PENDING": 0, "EMPTY": 0}
    province_covered = 0
    province_total = 0
    national_covered = 0
    national_total = 0

    inv_by_name: dict[str, dict[str, str]] = {
        r.get("province_zh", ""): r for r in inventory.values()
    }

    for geo_id, zh, _en, level in geos:
        inv = inv_by_name.get(zh) or {}
        inv_status = (inv.get("status") or "MISSING").strip()
        inv_url = inv.get("candidate_url", "") or ""
        missing = (inv.get("missing_reason") or "").strip()
        n_obs = obs_count.get(geo_id, 0)
        geo_code = inv.get("geo_code", "") or (
            "00" if level == "COUNTRY" else ""
        )

        if n_obs > 0:
            verdict = "COVERED"
        elif inv_status == "BLOCKED":
            verdict = "BLOCKED"
        elif inv_status == "MISSING":
            verdict = "EMPTY"
        else:
            verdict = "PENDING"

        summary[verdict] += 1
        if level == "PROVINCE":
            province_total += 1
            if verdict == "COVERED":
                province_covered += 1
        elif level == "COUNTRY":
            national_total += 1
            if verdict == "COVERED":
                national_covered += 1
        lines.append(
            f"| {zh} | {level} | {geo_code} | {inv_status} | "
            f"{inv_url} | {n_obs} | {missing} | {verdict} |"
        )

    lines.append("")
    lines.append("## Summary")
    lines.append("")
    lines.append(f"- Total 省级 rows: **{province_total}**")
    lines.append(f"- 省级 COVERED (real observation 2024 GDP): "
                 f"**{province_covered}**")
    lines.append(f"- 省级 BLOCKED (inventory status=BLOCKED): "
                 f"**{summary['BLOCKED']}**")
    lines.append(f"- 省级 PENDING (inventory status=PENDING): "
                 f"**{summary['PENDING']}**")
    lines.append(f"- 省级 EMPTY (no inventory row): **{summary['EMPTY']}**")
    lines.append("")
    lines.append(f"- 全国主体 rows: **{national_total}**")
    lines.append(f"- 全国主体 COVERED: **{national_covered}**")
    lines.append("")
    lines.append(
        f"**KPI (knife 633 §2 + §3.D)**: 省级 COVERED = "
        f"**{province_covered}/{province_total}** = "
        f"{(province_covered / max(province_total, 1)) * 100:.1f}%  "
        f"(M2-b 目标 ≥5/31); 国家行另列, COVERED="
        f"**{national_covered}/{national_total}**。"
    )
    lines.append("")
    lines.append(
        "M2-b 633 §4 明确不做：未扩满 31 省 (→ M2-c)、未跨源核对 (→ M2-d)、"
        "未建 /research/q1-2024-gdp (→ M2-e)。"
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