"""M1 T1 — reference data seed (per docs/55 §T1 · 2026-08-31).

Idempotent upsert of the 5 FK entities required by the M1 first series
(`hubei_2026_06.xlsx` → GDP, Hubei Province, 2026 H1 period):

  1. geo_entity               — 湖北省 (PROVINCE)
  2. geo_code_version         — admin_code 42 / ISO CN-HB, valid 2026-01-01..
  3. indicator_definition     — 地区生产总值 (短码 GDP, unit  亿元)
  4. indicator_methodology_version — hubei-2026-06-bulletin-caveat
  5. calendar_period          — 2026H1 上半年（提取器实际可得期间）

Per docs/55 §T1 完成条件：5 类 FK 全部存在；同名不同口径不合并
(GDP 半年累计 vs 年度 vs 单季分三条 methodology / indicator，本刀只用
一条并写 caveat)。

Per docs/55 §T1 验收：脚本 exit 0 两次结果稳定；不 INSERT observation
（T2 才接 observation）。

Usage:
  python scripts/seed_m1_reference_data.py --load
  python scripts/seed_m1_reference_data.py --status
  python scripts/seed_m1_reference_data.py --unload

DSN: ${CEGR_DSN:-postgresql://postgres:postgres@127.0.0.1:55440/cegr_test}
"""
from __future__ import annotations

import argparse
import os
import sys
import uuid
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
DESIGNATED_XLSX = (
    REPO_ROOT / "spikes" / "02-provincial-yearbook" / "hubei_2026_06.xlsx"
)
DESIGNATED_SHA = (
    "c5cf5abeb4fdf97af52567f0640470d631bc9ac329dcc98f14e5d40bf6a5cac7"
)
DESIGNATED_SIZE = 11261  # bytes per registry row + sha256 verified

# Stable UUIDs — M1 T1 namespace `a1000000-0000-0000-0000-…`
HUBEI_PROVINCE_ID = uuid.UUID("a1000000-0000-0000-0000-000000000001")
HUBEI_GEO_CODE_VERSION_ID = uuid.UUID(
    "a1000000-0000-0000-0000-000000000002"
)
HUBEI_GDP_INDICATOR_ID = uuid.UUID(
    "a1000000-0000-0000-0000-000000000010"
)
HUBEI_GDP_MV_ID = uuid.UUID("a1000000-0000-0000-0000-000000000011")
HUBEI_IAV_INDICATOR_ID = uuid.UUID(
    "a1000000-0000-0000-0000-000000000020"
)
HUBEI_IAV_MV_ID = uuid.UUID("a1000000-0000-0000-0000-000000000021")
HUBEI_2026_H1_PERIOD_ID = uuid.UUID(
    "a1000000-0000-0000-0000-000020260601"
)
HUBEI_SOURCE_DOC_ID = uuid.UUID(
    "a1000000-0000-0000-0000-000000000030"
)


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


def _resolve_hubei_registry_id(cur) -> uuid.UUID:
    """Look up the source_registry.id for tjj.hubei.gov.cn / PROVINCIAL_BULLETIN.

    This row is inserted by scripts/import_registry_csv.py from registry.csv.
    We rely on that having run (it is the test fixture's responsibility).
    """
    cur.execute(
        """
        SELECT id FROM cegr.source_registry
        WHERE domain = 'tjj.hubei.gov.cn' AND category = 'PROVINCIAL_BULLETIN'
        LIMIT 1
        """
    )
    row = cur.fetchone()
    if row is None:
        sys.exit(
            "ERROR: source_registry row tjj.hubei.gov.cn/PROVINCIAL_BULLETIN "
            "missing; run scripts/import_registry_csv.py first"
        )
    return row[0]


def load_seed(verbose: bool = True) -> None:
    """Insert M1 first-series reference data into cegr_test (idempotent)."""
    # Sanity: file exists & SHA matches registry — see docs/55 §1.1
    if not DESIGNATED_XLSX.exists():
        sys.exit(f"ERROR: designated xlsx missing: {DESIGNATED_XLSX}")
    actual_sha = DESIGNATED_XLSX.read_bytes()
    import hashlib
    if hashlib.sha256(actual_sha).hexdigest() != DESIGNATED_SHA:
        sys.exit(
            f"ERROR: designated xlsx SHA drift: "
            f"expected={DESIGNATED_SHA[:12]} actual file hash mismatch"
        )
    if len(actual_sha) != DESIGNATED_SIZE:
        sys.exit(
            f"ERROR: designated xlsx size drift: "
            f"expected={DESIGNATED_SIZE} actual={len(actual_sha)}"
        )

    with _connect() as conn:
        with conn.cursor() as cur:
            sr_id = _resolve_hubei_registry_id(cur)

            # 1. Source document (the spike 02 xlsx, with caveat)
            cur.execute(
                """
                INSERT INTO cegr.source_document
                    (id, source_registry_id, source_level, verification_status,
                     title, publisher, file_hash_sha256, file_size_bytes,
                     file_path, file_format, language, extraction_method,
                     url, caveat_text)
                VALUES (%s, %s, 'S0', 'VERIFIED',
                        %s, %s, %s, %s,
                        %s, 'XLSX', 'zh', 'EXCEL_PARSE',
                        %s, %s)
                ON CONFLICT (id) DO NOTHING
                """,
                (
                    str(HUBEI_SOURCE_DOC_ID),
                    str(sr_id),
                    "湖北省统计局 2026 年 6 月份统计公报 (xlsx)",
                    "湖北省统计局",
                    DESIGNATED_SHA,
                    DESIGNATED_SIZE,
                    str(DESIGNATED_XLSX.relative_to(REPO_ROOT)),
                    "https://tjj.hubei.gov.cn/tjsj/sjkscx/tjyb/",
                    "GDP 字段为季度数（半年累计）；写入 observation 时 "
                    "caveat_text 必填，不得改写成无条件「半年累计」（per docs/55 §1.1）",
                ),
            )

            # 2. geo_entity: 湖北省 (PROVINCE)
            cur.execute(
                """
                INSERT INTO cegr.geo_entity
                    (id, canonical_name, canonical_name_en, level)
                VALUES (%s, '湖北省', 'Hubei', 'PROVINCE')
                ON CONFLICT (id) DO NOTHING
                """,
                (str(HUBEI_PROVINCE_ID),),
            )

            # 3. geo_code_version: 湖北 GB/T 2260 = 42, ISO CN-HB
            cur.execute(
                """
                INSERT INTO cegr.geo_code_version
                    (id, geo_entity_id, admin_code, iso_code,
                     valid_from, source_id)
                VALUES (%s, %s, '42', 'CN-HB',
                        '2026-01-01'::date, %s)
                ON CONFLICT (id) DO NOTHING
                """,
                (
                    str(HUBEI_GEO_CODE_VERSION_ID),
                    str(HUBEI_PROVINCE_ID),
                    str(HUBEI_SOURCE_DOC_ID),
                ),
            )

            # 4. indicator_definition: 地区生产总值 / GDP
            cur.execute(
                """
                INSERT INTO cegr.indicator_definition
                    (id, canonical_name, canonical_name_en, short_code,
                     description, unit_canonical, unit_category,
                     frequency, is_cumulative, geo_scope_default)
                VALUES (%s, '地区生产总值', 'Gross Regional Product', 'GDP',
                        '地区生产总值（半年累计；季度口径 per 湖北统计局公报脚注）',
                        '亿元', 'CURRENCY',
                        'HALF_YEARLY', TRUE, 'PROVINCE')
                ON CONFLICT (id) DO NOTHING
                """,
                (str(HUBEI_GDP_INDICATOR_ID),),
            )

            # 5. indicator_methodology_version: GDP hubei-2026-06-bulletin-caveat
            cur.execute(
                """
                INSERT INTO cegr.indicator_methodology_version
                    (id, indicator_id, version_label, valid_from,
                     change_summary, impact_note, source_id)
                VALUES (%s, %s, 'hubei-2026-06-bulletin-caveat', '2026-01-01'::date,
                            'GDP 为季度数；不得改写为无条件「半年累计」',
                            '解析 spike 02 时写入 caveat_text',
                            %s)
                ON CONFLICT (id) DO NOTHING
                """,
                (
                    str(HUBEI_GDP_MV_ID),
                    str(HUBEI_GDP_INDICATOR_ID),
                    str(HUBEI_SOURCE_DOC_ID),
                ),
            )

            # 6. (parallel) indicator_definition: 工业增加值 / IAV
            #     用以验证「GDP 与工业增加值不共用 methodology」（T1 §验收）
            cur.execute(
                """
                INSERT INTO cegr.indicator_definition
                    (id, canonical_name, canonical_name_en, short_code,
                     description, unit_canonical, unit_category,
                     frequency, geo_scope_default)
                VALUES (%s, '规模以上工业增加值', 'Industrial Value Added', 'IAV',
                        '规模以上工业增加值（月度/累计；与 GDP 同源不同口径）',
                        '亿元', 'CURRENCY',
                        'MONTHLY', 'PROVINCE')
                ON CONFLICT (id) DO NOTHING
                """,
                (str(HUBEI_IAV_INDICATOR_ID),),
            )

            # 7. (parallel) indicator_methodology_version for IAV
            cur.execute(
                """
                INSERT INTO cegr.indicator_methodology_version
                    (id, indicator_id, version_label, valid_from,
                     change_summary, source_id)
                VALUES (%s, %s, 'hubei-2026-06-bulletin-iav', '2026-01-01'::date,
                            '规模以上工业增加值与 GDP 同源不同口径；不共用 methodology',
                            %s)
                ON CONFLICT (id) DO NOTHING
                """,
                (
                    str(HUBEI_IAV_MV_ID),
                    str(HUBEI_IAV_INDICATOR_ID),
                    str(HUBEI_SOURCE_DOC_ID),
                ),
            )

            # 8. calendar_period: 2026 上半年 (period_label '2026H1')
            cur.execute(
                """
                INSERT INTO cegr.calendar_period
                    (id, period_label, period_type, start_date, end_date,
                     fy_label, raw_label, period_basis)
                VALUES (%s, '2026H1', 'HALF_YEARLY',
                        '2026-01-01'::date, '2026-06-30'::date,
                        'FY2026H1', '1—6月（湖北统计局公报口径）',
                        'INSTANTANEOUS')
                ON CONFLICT (id) DO NOTHING
                """,
                (str(HUBEI_2026_H1_PERIOD_ID),),
            )

        conn.commit()

    if verbose:
        print(
            f"[seed] M1 first-series reference data loaded — "
            f"province={HUBEI_PROVINCE_ID} indicator={HUBEI_GDP_INDICATOR_ID} "
            f"period={HUBEI_2026_H1_PERIOD_ID} src_doc={HUBEI_SOURCE_DOC_ID}"
        )


def status(verbose: bool = True) -> None:
    """Print M1 reference-data presence (5 FK entities)."""
    with _connect() as conn:
        with conn.cursor() as cur:
            cur.execute(
                "SELECT COUNT(*) FROM cegr.geo_entity WHERE id = %s",
                (str(HUBEI_PROVINCE_ID),),
            )
            n_geo = cur.fetchone()[0]
            cur.execute(
                "SELECT COUNT(*) FROM cegr.geo_code_version WHERE id = %s",
                (str(HUBEI_GEO_CODE_VERSION_ID),),
            )
            n_gcv = cur.fetchone()[0]
            cur.execute(
                "SELECT COUNT(*) FROM cegr.indicator_definition "
                "WHERE id IN (%s, %s)",
                (str(HUBEI_GDP_INDICATOR_ID), str(HUBEI_IAV_INDICATOR_ID)),
            )
            n_ind = cur.fetchone()[0]
            cur.execute(
                "SELECT COUNT(*) FROM cegr.indicator_methodology_version "
                "WHERE id IN (%s, %s)",
                (str(HUBEI_GDP_MV_ID), str(HUBEI_IAV_MV_ID)),
            )
            n_mv = cur.fetchone()[0]
            cur.execute(
                "SELECT COUNT(*) FROM cegr.calendar_period WHERE id = %s",
                (str(HUBEI_2026_H1_PERIOD_ID),),
            )
            n_period = cur.fetchone()[0]
    print(
        f"[status] geo_entity={n_geo}/1 geo_code_version={n_gcv}/1 "
        f"indicator_definition={n_ind}/2 indicator_methodology_version={n_mv}/2 "
        f"calendar_period={n_period}/1"
    )


def unload(verbose: bool = True) -> None:
    """Remove M1 first-series reference data (TRUNCATE CASCADE).

    Per schema/01-core.sql: source_document has a BEFORE DELETE row
    trigger that raises an exception. TRUNCATE on source_document only
    fires statement-level triggers, not row-level BEFORE DELETE, so
    TRUNCATE ... CASCADE is the supported cleanup path and respects FK
    chains into geo_code_version / indicator_methodology_version /
    observation.
    """
    with _connect() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                TRUNCATE TABLE
                    cegr.source_document,
                    cegr.indicator_methodology_version,
                    cegr.indicator_definition,
                    cegr.calendar_period,
                    cegr.geo_code_version,
                    cegr.geo_entity
                CASCADE
                """
            )
        conn.commit()
    print("[unload] M1 reference data removed (TRUNCATE CASCADE)")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    parser.add_argument("--load", action="store_true",
                        help="Insert M1 reference data (idempotent)")
    parser.add_argument("--status", action="store_true",
                        help="Show M1 reference-data presence")
    parser.add_argument("--unload", action="store_true",
                        help="Remove M1 reference-data rows")
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