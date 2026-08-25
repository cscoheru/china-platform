"""Stage 1 / S1.12 — Demo seed loader for Gate 1 §1.5.

Inserts the Jiangsu GDP 5-year hand-crafted seed (data/seeds/jiangsu_gdp_2020_2024.json)
into cegr_test so that the API `/api/indicator/{id}/series` endpoint can answer
"近 5 年江苏 GDP 增长趋势".

Per tasking 92 §1.1: 演示数据 允许 受控 seed / 已有样本入库 (不批量爬 2020-2025；不 HTTP 爬源站).
Per R4 用户裁定 (Stage 0): never claim 1909 US Abstract as Chinese-representative.

Usage:
  python scripts/seed_jiangsu_gdp_demo.py --load
  python scripts/seed_jiangsu_gdp_demo.py --status
  python scripts/seed_jiangsu_gdp_demo.py --unload

Idempotent: all INSERTs use ON CONFLICT DO NOTHING with stable UUIDs.

DSN: ${CEGR_DSN:-${STAGE0_DSN:-postgresql://postgres:postgres@127.0.0.1:55440/cegr_test}}
"""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
import uuid
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
SEED_FILE = REPO_ROOT / "data" / "seeds" / "jiangsu_gdp_2020_2024.json"
DBT_DIR = REPO_ROOT / "dbt"
DBT_VENV = Path("/tmp/dbt_venv/bin/dbt")

# Stable UUIDs for the demo seed (deterministic — re-runnable).
# All in UUID v4 hex-only form (a0000000-0000-0000-0000-NNNNNNNNNNNN).
JIANGSU_PROVINCE_ID = uuid.UUID("a0000000-0000-0000-0000-000000000032")
JIANGSU_GDP_INDICATOR_ID = uuid.UUID("a0000000-0000-0000-0000-000000000001")
JIANGSU_INDICATOR_MV_ID = uuid.UUID("a0000000-0000-0000-0000-000000000002")
JIANGSU_SOURCE_REGISTRY_ID = uuid.UUID("a0000000-0000-0000-0000-000000000003")
JIANGSU_SOURCE_DOC_ID = uuid.UUID("a0000000-0000-0000-0000-000000000004")
JIANGSU_SOURCE_LOC_ID = uuid.UUID("a0000000-0000-0000-0000-000000000005")
JIANGSU_INGESTION_RUN_ID = uuid.UUID("a0000000-0000-0000-0000-000000000006")
JIANGSU_GEO_CODE_VERSION_ID = uuid.UUID("a0000000-0000-0000-0000-000000000007")


def _period_id(year: int) -> uuid.UUID:
    """Stable UUID per calendar year (5xx prefix → 5 UUIDs namespace)."""
    return uuid.UUID(f"a0000000-0000-0000-0000-{year:04x}00000000")


def _obs_id(year: int) -> uuid.UUID:
    return uuid.UUID(f"a0000000-0000-0000-0000-{year:04x}10000000")


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
        import psycopg2.extras  # type: ignore
    except ImportError:
        sys.exit("ERROR: psycopg2 not installed. Run: pip install psycopg2-binary")

    psycopg2.extras.register_uuid()
    return psycopg2.connect(get_dsn())


def load_seed(verbose: bool = True) -> None:
    """Insert Jiangsu GDP 5-year seed into cegr_test (idempotent)."""
    if not SEED_FILE.exists():
        sys.exit(f"ERROR: seed file not found: {SEED_FILE}")

    with open(SEED_FILE, "r", encoding="utf-8") as f:
        seed = json.load(f)

    meta = seed["metadata"]
    lineage = seed["lineage"]
    obs_rows = seed["observations"]

    if verbose:
        print(f"[seed] loading {len(obs_rows)} observations of {meta['indicator_zh']} "
              f"({meta['province_zh']}) into cegr_test")

    with _connect() as conn:
        with conn.cursor() as cur:
            # Source registry (declared_source_level=S0; source_level=S1 until
            # verification_status becomes VERIFIED. The constraint
            # source_level_s0_requires_verified blocks S0 unless VERIFIED.)
            cur.execute(
                """
                INSERT INTO cegr.source_registry
                    (id, domain, organization, category, primary_url,
                     access_method, source_level, declared_source_level,
                     update_frequency, enabled, auth_note, purpose_note)
                VALUES (%s, %s, %s, %s, %s,
                        %s, %s, %s,
                        %s, TRUE, %s, %s)
                ON CONFLICT (id) DO NOTHING
                """,
                (
                    str(JIANGSU_SOURCE_REGISTRY_ID),
                    "tj.jiangsu.gov.cn",
                    meta["source_agency"],
                    "PROVINCIAL_BULLETIN",
                    meta["source_url"],
                    "HTML_PARSE",
                    "S1",
                    "S0",
                    "ANNUAL",
                    "公开；无需授权（DEMO_SEED 仅用于 Gate 1 §1.5 真实研究问题演示）",
                    "DEMO_SEED_HANDCRAFTED: 手工 seed，非批量爬取；per tasking 92 §1.1; "
                    "source_level=S1 (declared S0) until verification_status=VERIFIED",
                ),
            )

            # Source document (one row, demo placeholder SHA-256)
            # verification_status is enum UNVERIFIED/PENDING/VERIFIED/REJECTED —
            # use UNVERIFIED + caveat_text to mark as DEMO per R08.
            cur.execute(
                """
                INSERT INTO cegr.source_document
                    (id, source_registry_id, source_level, verification_status,
                     title, publisher, file_hash_sha256,
                     url, file_size_bytes, caveat_text)
                VALUES (%s, %s, 'S1', 'UNVERIFIED',
                        '江苏省年度国民经济统计公报 (DEMO_SEED)',
                        %s, %s,
                        %s, NULL, %s)
                ON CONFLICT (id) DO NOTHING
                """,
                (
                    str(JIANGSU_SOURCE_DOC_ID),
                    str(JIANGSU_SOURCE_REGISTRY_ID),
                    meta["source_agency"],
                    lineage["source_file_sha256"],
                    lineage["source_file_url"],
                    "DEMO_SEED_HANDCRAFTED: 手工 seed，非批量爬取；per tasking 92 §1.1; "
                    "verification_status=UNVERIFIED because no live SHA-256 file",
                ),
            )

            # Source location
            cur.execute(
                """
                INSERT INTO cegr.source_location
                    (id, source_document_id, sheet_name, page_number,
                     cell_range)
                VALUES (%s, %s, 'N/A', 0, 'DEMO_SEED')
                ON CONFLICT (id) DO NOTHING
                """,
                (str(JIANGSU_SOURCE_LOC_ID), str(JIANGSU_SOURCE_DOC_ID)),
            )

            # Geo entity (江苏省)
            cur.execute(
                """
                INSERT INTO cegr.geo_entity
                    (id, canonical_name, canonical_name_en, level, parent_id)
                VALUES (%s, %s, %s, 'PROVINCE', NULL)
                ON CONFLICT (id) DO NOTHING
                """,
                (str(JIANGSU_PROVINCE_ID), meta["province_zh"], meta["province_pinyin"]),
            )

            # Geo code version (ISO code JS / GB/T 2260 = 32)
            cur.execute(
                """
                INSERT INTO cegr.geo_code_version
                    (id, geo_entity_id, iso_code, valid_from, source_id)
                VALUES (%s, %s, %s, '2020-01-01'::date, %s)
                ON CONFLICT (id) DO NOTHING
                """,
                (
                    str(JIANGSU_GEO_CODE_VERSION_ID),
                    str(JIANGSU_PROVINCE_ID),
                    meta["province_code_gb2260"],
                    str(JIANGSU_SOURCE_DOC_ID),
                ),
            )

            # Indicator definition
            cur.execute(
                """
                INSERT INTO cegr.indicator_definition
                    (id, canonical_name, canonical_name_en, unit_canonical,
                     frequency, geo_scope_default)
                VALUES (%s, %s, %s, %s,
                        'ANNUAL', 'PROVINCE')
                ON CONFLICT (id) DO NOTHING
                """,
                (
                    str(JIANGSU_GDP_INDICATOR_ID),
                    meta["indicator_zh"],
                    meta["indicator_canonical"],
                    meta["unit"],
                ),
            )

            # Indicator methodology version
            cur.execute(
                """
                INSERT INTO cegr.indicator_methodology_version
                    (id, indicator_id, version_label, valid_from, valid_to,
                     change_summary, source_id)
                VALUES (%s, %s, 'v1.0-demo', '2020-01-01'::date, NULL,
                            'DEMO_SEED — hand-crafted; not a live extraction',
                            %s)
                ON CONFLICT (id) DO NOTHING
                """,
                (
                    str(JIANGSU_INDICATOR_MV_ID),
                    str(JIANGSU_GDP_INDICATOR_ID),
                    str(JIANGSU_SOURCE_DOC_ID),
                ),
            )

            # Ingestion run (one DEMO row covering all 5 years)
            cur.execute(
                """
                INSERT INTO cegr.ingestion_run
                    (id, source_registry_id, status, started_at, finished_at,
                     records_extracted, records_inserted, records_updated,
                     triggered_by)
                VALUES (%s, %s, 'SUCCESS', NOW() - INTERVAL '1 hour',
                        NOW() - INTERVAL '50 minutes', %s, %s, 0, 'DEMO_SEED')
                ON CONFLICT (id) DO NOTHING
                """,
                (
                    str(JIANGSU_INGESTION_RUN_ID),
                    str(JIANGSU_SOURCE_REGISTRY_ID),
                    len(obs_rows),
                    len(obs_rows),
                ),
            )

            # Calendar periods (one per year) + observations
            for row in obs_rows:
                year = int(row["period_label"])
                period_id = _period_id(year)
                obs_id = _obs_id(year)

                cur.execute(
                    """
                    INSERT INTO cegr.calendar_period
                        (id, start_date, end_date, period_type, period_label,
                         fy_label, raw_label, period_basis)
                    VALUES (%s, %s, %s, 'ANNUAL', %s,
                            %s, %s, 'INSTANTANEOUS')
                    ON CONFLICT (id) DO NOTHING
                    """,
                    (
                        str(period_id),
                        row["period_start"],
                        row["period_end"],
                        f"{row['period_label']}-JS-DEMO",
                        f"FY{year}",
                        row["period_label"],
                    ),
                )

                cur.execute(
                    """
                    INSERT INTO cegr.observation
                        (id, indicator_id, indicator_methodology_version_id,
                         geo_entity_id, geo_code_version_id, calendar_period_id,
                         value, raw_value, unit, is_imputed, missing_reason,
                         value_type, status, comparison_basis, source_id,
                         source_location_id, ingestion_run_id, extraction_method,
                         confidence, period_start, period_end, period_label,
                         period_type, lineage, caveat_text, extracted_at)
                    VALUES
                        (%s, %s, %s, %s, %s, %s,
                         %s, %s, %s, FALSE, NULL,
                         'FACT', 'FINAL', %s, %s,
                         %s, %s, 'MANUAL_UPLOAD',
                         0.85, %s, %s, %s,
                         %s, %s::jsonb, %s, NOW())
                    ON CONFLICT (id) DO NOTHING
                    """,
                    (
                        str(obs_id),
                        str(JIANGSU_GDP_INDICATOR_ID),
                        str(JIANGSU_INDICATOR_MV_ID),
                        str(JIANGSU_PROVINCE_ID),
                        str(JIANGSU_GEO_CODE_VERSION_ID),
                        str(period_id),
                        row["value"],
                        str(row["value"]),
                        row["unit"],
                        row["comparison_basis"],
                        str(JIANGSU_SOURCE_DOC_ID),
                        str(JIANGSU_SOURCE_LOC_ID),
                        str(JIANGSU_INGESTION_RUN_ID),
                        row["period_start"],
                        row["period_end"],
                        row["period_label"],
                        row["period_type"],
                        json.dumps({
                            "chain_id": lineage["chain_id"],
                            "source_file_sha256": lineage["source_file_sha256"],
                            "growth_rate_yoy_pct": row["growth_rate_yoy_pct"],
                            "indicator_zh": row["indicator_zh"],
                            "demo_note": "S1.12 hand-crafted seed (per tasking 92 §1.1)",
                        }, ensure_ascii=False, sort_keys=True),
                        row.get("caveat"),
                    ),
                )

        conn.commit()
    if verbose:
        print(f"[seed] inserted {len(obs_rows)} observations into cegr_test")

    # Rebuild dbt staging views so API can read cegr_staging.stg_observation.
    if DBT_VENV.exists() and DBT_DIR.is_dir():
        if verbose:
            print("[seed] rebuilding dbt staging views...")
        result = subprocess.run(
            [str(DBT_VENV), "run", "--select", "staging+",
             "--profiles-dir", str(DBT_DIR)],
            cwd=str(DBT_DIR),
            capture_output=True, text=True, timeout=120,
        )
        if verbose:
            if result.returncode == 0:
                print("[seed] dbt staging views rebuilt OK")
            else:
                print(f"[seed] dbt run warning (returncode={result.returncode}); "
                      "API may serve stale views but cegr.observation is authoritative",
                      file=sys.stderr)
                if result.stderr:
                    print(result.stderr[-500:], file=sys.stderr)


def status(verbose: bool = True) -> None:
    """Print whether the demo seed rows exist."""
    try:
        with _connect() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    SELECT COUNT(*) FROM cegr.observation
                    WHERE source_id = %s
                    """,
                    (str(JIANGSU_SOURCE_DOC_ID),),
                )
                n_obs = cur.fetchone()[0]
                cur.execute(
                    """
                    SELECT COUNT(*) FROM cegr.indicator_definition
                    WHERE id = %s
                    """,
                    (str(JIANGSU_GDP_INDICATOR_ID),),
                )
                n_ind = cur.fetchone()[0]
        print(f"[status] observations={n_obs} indicator_definitions={n_ind}")
        print(f"  indicator_id = {JIANGSU_GDP_INDICATOR_ID}")
        print(f"  province_id  = {JIANGSU_PROVINCE_ID}")
    except Exception as e:
        print(f"[status] ERROR: {e}", file=sys.stderr)
        sys.exit(1)


def unload(verbose: bool = True) -> None:
    """Remove the demo seed rows (cascade to observations)."""
    with _connect() as conn:
        with conn.cursor() as cur:
            cur.execute(
                "DELETE FROM cegr.observation WHERE source_id = %s",
                (str(JIANGSU_SOURCE_DOC_ID),),
            )
            n_obs = cur.rowcount
            cur.execute(
                "DELETE FROM cegr.source_location WHERE id = %s",
                (str(JIANGSU_SOURCE_LOC_ID),),
            )
            cur.execute(
                "DELETE FROM cegr.source_document WHERE id = %s",
                (str(JIANGSU_SOURCE_DOC_ID),),
            )
            cur.execute(
                "DELETE FROM cegr.source_registry WHERE id = %s",
                (str(JIANGSU_SOURCE_REGISTRY_ID),),
            )
            cur.execute(
                "DELETE FROM cegr.indicator_methodology_version WHERE id = %s",
                (str(JIANGSU_INDICATOR_MV_ID),),
            )
            cur.execute(
                "DELETE FROM cegr.indicator_definition WHERE id = %s",
                (str(JIANGSU_GDP_INDICATOR_ID),),
            )
            cur.execute(
                "DELETE FROM cegr.geo_code_version WHERE id = %s",
                (str(JIANGSU_GEO_CODE_VERSION_ID),),
            )
            cur.execute(
                "DELETE FROM cegr.geo_entity WHERE id = %s",
                (str(JIANGSU_PROVINCE_ID),),
            )
            cur.execute(
                "DELETE FROM cegr.ingestion_run WHERE id = %s",
                (str(JIANGSU_INGESTION_RUN_ID),),
            )
            cur.execute(
                "DELETE FROM cegr.calendar_period WHERE id IN (%s, %s, %s, %s, %s)",
                (
                    str(_period_id(2020)), str(_period_id(2021)),
                    str(_period_id(2022)), str(_period_id(2023)),
                    str(_period_id(2024)),
                ),
            )
        conn.commit()
    print(f"[unload] removed {n_obs} demo observations + dependencies")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    parser.add_argument("--load", action="store_true", help="Insert demo seed (idempotent)")
    parser.add_argument("--status", action="store_true", help="Show seed presence")
    parser.add_argument("--unload", action="store_true", help="Remove demo seed rows")
    args = parser.parse_args()

    if args.load:
        load_seed()
    elif args.status:
        status()
    elif args.unload:
        unload()
    else:
        parser.print_help()


if __name__ == "__main__":
    main()