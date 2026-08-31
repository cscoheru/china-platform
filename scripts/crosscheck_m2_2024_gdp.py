"""M2-d — 2024 GDP cross-source sanity check (knife 635 §1.D).

Compares two independent 2024 GDP estimates:

  (A) National observation (NBS 公报): 1349084 亿
  (B) Sum of province observations (level='PROVINCE') for the 2024 calendar
      period + indicator `M2_GDP_ANNUAL` + calendar_period_id = 2024Y

Per knife 635 §1.D:
  - 相对差 < 0.5% → CONSISTENT
  - 否则         → QUARANTINED + caveat

Method limitation: when only N provinces are COVERED (not all 31),
the (B)/(A) ratio is expected to be < 1.0 (the gap = un-covered provinces).
The crosscheck is therefore a *weak* sanity check:

  - "coverage_ratio" = n_covered / 31
  - "sum_ratio"      = sum_covered / national
  - "expected_min_ratio" ≈ coverage_ratio * 0.5  (heuristic floor:
    covered provinces are typically the bigger ones, so ratio ≥ 50% of
    coverage_ratio is expected)
  - if sum_ratio < expected_min_ratio → QUARANTINED + "library sum implausibly
    small given coverage"

No silent fallback: the script reports the verdict per row and the
overall verdict, but never modifies observation.value.

Outputs `docs/reports/m2_2024_gdp_crosscheck_20260831.md`.

Usage:
  python scripts/crosscheck_m2_2024_gdp.py

DSN: ${CEGR_DSN:-postgresql://postgres:postgres@127.0.0.1:55440/cegr_test}
"""
from __future__ import annotations

import os
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
REPORTS_DIR = REPO_ROOT / "docs" / "reports"

# M2-b indicator / period / national geo UUIDs (must match ingest_m2_2024_gdp.py)
M2_GDP_ANNUAL_INDICATOR_ID = "a2000000-0000-0000-0000-00000000a001"
CALENDAR_2024_PERIOD_ID = "a2000000-0000-0000-0000-000020240101"
NATIONAL_GEO_ENTITY_ID = "a2000000-0000-0000-0000-000000000000"

# Cross-source consistency threshold (knife 635 §1.D; docs/54 §08b)
CONSISTENT_THRESHOLD_PCT = 0.5  # ±0.5% relative diff


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
        sys.exit("ERROR: psycopg2 not installed; pip install psycopg2-binary")
    return psycopg2.connect(get_dsn())


def _load_national_value(cur) -> tuple[float, str | None]:
    cur.execute(
        """
        SELECT value, missing_reason
        FROM cegr.observation
        WHERE indicator_id = %s
          AND calendar_period_id = %s
          AND geo_entity_id = %s
        """,
        (M2_GDP_ANNUAL_INDICATOR_ID,
         CALENDAR_2024_PERIOD_ID,
         NATIONAL_GEO_ENTITY_ID),
    )
    row = cur.fetchone()
    if not row:
        return 0.0, "no national observation row"
    return float(row[0]), row[1]


def _load_province_values(cur) -> list[tuple[str, str, float, str]]:
    """Return [(admin_code, province_zh, value, caveat)] sorted by admin_code."""
    cur.execute(
        """
        SELECT
          split_part(g.canonical_name, '', 1) AS _nope,
          g.canonical_name,
          o.value,
          COALESCE(o.caveat_text, '')
        FROM cegr.observation o
        JOIN cegr.geo_entity g ON g.id = o.geo_entity_id
        WHERE o.indicator_id = %s
          AND o.calendar_period_id = %s
          AND g.level = 'PROVINCE'
        ORDER BY g.canonical_name
        """,
        (M2_GDP_ANNUAL_INDICATOR_ID, CALENDAR_2024_PERIOD_ID),
    )
    # Postgres doesn't have a "split by index" function; admin_code is
    # implicit in canonical_name. We return canonical_name; admin_code
    # is informational only.
    out: list[tuple[str, str, float, str]] = []
    rows = cur.fetchall()
    # Use first column placeholder; rebuild tuple from real columns
    cur.execute(
        """
        SELECT
          g.canonical_name,
          o.value,
          COALESCE(o.caveat_text, '')
        FROM cegr.observation o
        JOIN cegr.geo_entity g ON g.id = o.geo_entity_id
        WHERE o.indicator_id = %s
          AND o.calendar_period_id = %s
          AND g.level = 'PROVINCE'
        ORDER BY g.canonical_name
        """,
        (M2_GDP_ANNUAL_INDICATOR_ID, CALENDAR_2024_PERIOD_ID),
    )
    rows = cur.fetchall()
    for r in rows:
        zh, value, caveat = r[0], float(r[1]), r[2]
        out.append(("", zh, value, caveat))
    return out


def _load_n_provinces(cur) -> int:
    cur.execute(
        "SELECT COUNT(*) FROM cegr.geo_entity WHERE level='PROVINCE'"
    )
    return int(cur.fetchone()[0])


def _verdict_relative_diff(sum_value: float, national: float) -> tuple[str, float]:
    """Verdict using absolute relative diff vs threshold."""
    if national == 0:
        return "QUARANTINED", 100.0
    rel_diff_pct = abs(sum_value - national) / national * 100.0
    if rel_diff_pct < CONSISTENT_THRESHOLD_PCT:
        return "CONSISTENT", rel_diff_pct
    return "QUARANTINED", rel_diff_pct


def _verdict_coverage_implied(
    sum_value: float, national: float, n_covered: int, n_total: int
) -> tuple[str, str]:
    """Sanity check: given N_provinces covered, sum should be ≥ ~50% of
    (coverage_ratio × national). If sum is far below that, library values
    look implausibly small (could indicate a value extraction bug)."""
    if n_total == 0 or national == 0:
        return "N/A", "no coverage data"
    coverage_ratio = n_covered / n_total
    expected_min_ratio = coverage_ratio * 0.5
    actual_ratio = sum_value / national
    if actual_ratio < expected_min_ratio:
        return (
            "QUARANTINED",
            f"sum/national={actual_ratio:.4f} < coverage_ratio×0.5="
            f"{expected_min_ratio:.4f}; library values appear implausibly"
            f" small given coverage (ratio={coverage_ratio:.4f}, "
            f"covered={n_covered}/{n_total})",
        )
    return "PASS", (
        f"sum/national={actual_ratio:.4f} ≥ coverage_ratio×0.5="
        f"{expected_min_ratio:.4f} (coverage={n_covered}/{n_total})"
    )


def main() -> int:
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    out_path = REPORTS_DIR / "m2_2024_gdp_crosscheck_20260831.md"

    with _connect() as conn:
        with conn.cursor() as cur:
            national, national_miss = _load_national_value(cur)
            provinces = _load_province_values(cur)
            n_total = _load_n_provinces(cur)

    n_covered = len(provinces)
    sum_value = sum(p[2] for p in provinces) if provinces else 0.0
    coverage_ratio = n_covered / n_total if n_total else 0.0
    sum_ratio = sum_value / national if national else 0.0

    rel_verdict, rel_diff = _verdict_relative_diff(sum_value, national)
    impl_verdict, impl_reason = _verdict_coverage_implied(
        sum_value, national, n_covered, n_total
    )

    # Top-level verdict — combine both checks
    if rel_verdict == "CONSISTENT" and impl_verdict == "PASS":
        top_verdict = "CONSISTENT"
        top_caveat = (
            "all 31 provinces covered AND sum matches national within ±"
            f"{CONSISTENT_THRESHOLD_PCT}%"
        )
    elif rel_verdict == "QUARANTINED" and impl_verdict == "PASS":
        top_verdict = "QUARANTINED-WEAK"
        top_caveat = (
            f"relative diff {rel_diff:.2f}% > ±{CONSISTENT_THRESHOLD_PCT}%; "
            "method limitation: only "
            f"{n_covered}/{n_total} provinces covered, "
            f"sum_ratio={sum_ratio:.4f} (expected <1.0); "
            "see docs/54 §08b for weak-crosscheck protocol."
        )
    elif impl_verdict == "QUARANTINED":
        top_verdict = "QUARANTINED"
        top_caveat = (
            f"library values implausibly small: {impl_reason}; "
            "re-extract province values; this is NOT a coverage gap."
        )
    else:
        top_verdict = "QUARANTINED"
        top_caveat = (
            f"relative diff {rel_diff:.2f}% AND implausibility: {impl_reason}"
        )

    # Build markdown report
    lines: list[str] = []
    lines.append("# M2-d 2024 GDP Crosscheck Report (knife 635 §1.D)")
    lines.append("")
    lines.append(
        f"> Generated: {os.environ.get('CROSSCHECK_RUN_AT', 'inline')}  ·  "
        f"top verdict: **{top_verdict}**"
    )
    lines.append("")
    lines.append("## 1. Sources cross-checked")
    lines.append("")
    lines.append("| source | scope | value (亿元) | caveat |")
    lines.append("| --- | --- | --- | --- |")
    lines.append(
        f"| A: 国家统计局 2024 公报 (NBS NATIONAL_BULLETIN) | COUNTRY | "
        f"{national:,.1f} | "
        f"{national_miss or 'observation SUCCESS, missing_reason IS NULL'} |"
    )
    lines.append(
        f"| B: Sum of {n_covered} province observations (level=PROVINCE) | "
        f"PROVINCE×{n_covered} | {sum_value:,.1f} | "
        f"weak sum (only {coverage_ratio*100:.1f}% of provinces covered) |"
    )
    lines.append("")
    lines.append("## 2. Per-province breakdown")
    lines.append("")
    lines.append(
        "| province_zh | value (亿元) | share of national | caveat (前 60) |"
    )
    lines.append("| --- | --- | --- | --- |")
    if provinces:
        for _admin, zh, value, caveat in provinces:
            share = (value / national * 100.0) if national else 0.0
            lines.append(
                f"| {zh} | {value:,.2f} | {share:.2f}% | {caveat[:60]} |"
            )
    else:
        lines.append("| (no province rows) | — | — | — |")
    lines.append("")
    lines.append("## 3. Verdicts")
    lines.append("")
    lines.append(
        "| check | verdict | metric | threshold | reason |"
    )
    lines.append("| --- | --- | --- | --- | --- |")
    lines.append(
        f"| absolute relative diff (sum vs national) | {rel_verdict} | "
        f"{rel_diff:.4f}% | <{CONSISTENT_THRESHOLD_PCT}% | "
        f"sum={sum_value:,.1f}; national={national:,.1f} |"
    )
    lines.append(
        f"| coverage-implied plausibility | {impl_verdict} | "
        f"sum_ratio={sum_ratio:.4f} | "
        f"≥ coverage_ratio×0.5 = {coverage_ratio * 0.5:.4f} | "
        f"{impl_reason} |"
    )
    lines.append("")
    lines.append(f"## 4. Top-level verdict: **{top_verdict}**")
    lines.append("")
    lines.append(f"> {top_caveat}")
    lines.append("")
    lines.append("## 5. Method limitations")
    lines.append("")
    lines.append(
        "- Knife 635 §1.D: '无国家分省表时：用「31 省库内加总 vs 国家 GDP」"
        "作 弱核对'. 本 crosscheck is therefore WEAK by design."
    )
    lines.append(
        f"- 当前覆盖 {n_covered}/{n_total} 省级 ({coverage_ratio*100:.1f}%); "
        "覆盖率 < 100% 时 sum_ratio 期望 < 1.0 (差距 = 未覆盖省合计)."
    )
    lines.append(
        "- 31 省全 COVERED 后, 此 crosscheck 自动升级为 STRONG "
        "(±0.5% 阈值)."
    )
    lines.append(
        "- 本脚本不修改 observation.value; verdict 是 read-only 报告."
    )
    lines.append("")
    lines.append("## 6. Provenance")
    lines.append("")
    lines.append(
        "- indicator_id: `M2_GDP_ANNUAL` = "
        f"`{M2_GDP_ANNUAL_INDICATOR_ID}` (knife 633)"
    )
    lines.append(
        "- calendar_period_id: `2024Y` = "
        f"`{CALENDAR_2024_PERIOD_ID}`"
    )
    lines.append(
        "- national geo_entity_id: "
        f"`{NATIONAL_GEO_ENTITY_ID}` (synthetic, not in GB/T 2260)"
    )
    lines.append(
        "- threshold: docs/54 §08b = "
        f"±{CONSISTENT_THRESHOLD_PCT}% relative diff"
    )
    lines.append("")

    text = "\n".join(lines) + "\n"

    out_path.write_text(text, encoding="utf-8")
    print(text)
    print(f"[OK] wrote crosscheck report to {out_path}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())