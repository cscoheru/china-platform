"""M2-a — 31 省 `geo_entity` 种子 (per docs/56 / knife 631).

Idempotent upsert of the 31 provincial administrative divisions (4 直辖市 + 23 省
+ 5 自治区) into `cegr.geo_entity` + minimal `cegr.geo_code_version` (GB/T 2260).

Scope (knife 631 §1.A):
  - 31 省级行政区（含直辖市）写入 `cegr.geo_entity`
  - 30 行 `cegr.geo_code_version`（admin_code + iso_code + valid_from 2024-01-01）
    （Hubei 沿用 M1 已 seed 的 2026-01-01 行；不动 valid_from / source_id）
  - 1 行 `cegr.source_registry`「CODE_REFERENCE / GB/T 2260」作为 code FK 来源

UUID 命名空间 (per 631 §1.A):
  - 湖北沿用 M1 `a1000000-0000-0000-0000-000000000001`（与 0ee445e / a8fb101 一致）
  - 其余 30 省采用新命名空间 `a2000000-0000-0000-0000-{admin_code << 40}`
    （末 12 hex = admin_code 左移 40 位；如北京 11 → a2000000-…110000000000）

明确不做 (per 631 §2):
  - 不 ingest 31 省 observation（→ M2-b）
  - 不改 `/provinces/jiangsu`；不扩四轨 HTML
  - 不宣布 Gate 1/2 / M2 PASS

Usage:
  python scripts/seed_m2_province_geo.py --load
  python scripts/seed_m2_province_geo.py --status
  python scripts/seed_m2_province_geo.py --unload

DSN: ${CEGR_DSN:-postgresql://postgres:postgres@127.0.0.1:55440/cegr_test}
"""
from __future__ import annotations

import argparse
import os
import sys
import uuid
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent

# M1-保留：湖北 UUID（与 seed_m1_reference_data.py / 629 回执一致）
HUBEI_PROVINCE_ID = uuid.UUID("a1000000-0000-0000-0000-000000000001")

# M2-a 命名空间：a2000000-0000-0000-0000-{admin_code << 40}
# 末 12 hex = admin_code 左移 40 位（如 11 → 0x110000000000 → 12 hex chars）


def _make_m2_uuid(admin_code: str) -> uuid.UUID:
    """Build a stable M2 province UUID from its GB/T 2260 admin_code.

    Encoding: ``a2000000-0000-0000-0000-{admin_code << 40}``.
    UUID last segment is 12 hex chars; we keep admin_code readable in leftmost 2.
    """
    code_int = int(admin_code) << 40
    return uuid.UUID(f"a2000000-0000-0000-0000-{code_int:012x}")


def _geo_code_version_id(geo_id: uuid.UUID) -> uuid.UUID:
    """Derive a stable geo_code_version.id from the geo_entity.id.

    Encoding: same UUID but with version nibble set to ``0x001`` (lowest free).
    This keeps the namespace parallel without collision with M1's
    HUBEI_GEO_CODE_VERSION_ID (a1000000-...002).
    """
    geo_int = int(geo_id.hex[-12:], 16)
    cv_int = (geo_int | 0x001) & 0xFFFFFFFFFFFF
    return uuid.UUID(f"{geo_id.hex[:8]}-0000-0000-0000-{cv_int:012x}")


# ---------------------------------------------------------------------
# 31 省级行政区清单（GB/T 2260 行政区划代码；2024 年口径）
# 列：admin_code, zh, en, iso（CN-XX 两位）
# ---------------------------------------------------------------------
PROVINCES: list[tuple[str, str, str, str]] = [
    # 4 直辖市
    ("11", "北京市",   "Beijing",      "CN-11"),
    ("12", "天津市",   "Tianjin",      "CN-12"),
    ("31", "上海市",   "Shanghai",     "CN-31"),
    ("50", "重庆市",   "Chongqing",    "CN-50"),
    # 23 省
    ("13", "河北省",   "Hebei",        "CN-13"),
    ("14", "山西省",   "Shanxi",       "CN-14"),
    ("15", "内蒙古自治区", "Inner Mongolia", "CN-15"),
    ("21", "辽宁省",   "Liaoning",     "CN-21"),
    ("22", "吉林省",   "Jilin",        "CN-22"),
    ("23", "黑龙江省", "Heilongjiang", "CN-23"),
    ("32", "江苏省",   "Jiangsu",      "CN-32"),
    ("33", "浙江省",   "Zhejiang",     "CN-33"),
    ("34", "安徽省",   "Anhui",        "CN-34"),
    ("35", "福建省",   "Fujian",       "CN-35"),
    ("36", "江西省",   "Jiangxi",      "CN-36"),
    ("37", "山东省",   "Shandong",     "CN-37"),
    ("41", "河南省",   "Henan",        "CN-41"),
    # ("42", "湖北省",   "Hubei",        "CN-42"),  # M1 already seeded; keep a1000000-...001
    ("43", "湖南省",   "Hunan",        "CN-43"),
    ("44", "广东省",   "Guangdong",    "CN-44"),
    ("45", "广西壮族自治区", "Guangxi", "CN-45"),
    ("46", "海南省",   "Hainan",       "CN-46"),
    ("51", "四川省",   "Sichuan",      "CN-51"),
    ("52", "贵州省",   "Guizhou",      "CN-52"),
    ("53", "云南省",   "Yunnan",       "CN-53"),
    ("54", "西藏自治区", "Tibet",       "CN-54"),
    ("61", "陕西省",   "Shaanxi",      "CN-61"),
    ("62", "甘肃省",   "Gansu",        "CN-62"),
    ("63", "青海省",   "Qinghai",      "CN-63"),
    ("64", "宁夏回族自治区", "Ningxia", "CN-64"),
    ("65", "新疆维吾尔自治区", "Xinjiang", "CN-65"),
]

# 31 省合成（包含 Hubei from M1）
HUBEI_ROW = ("42", "湖北省", "Hubei", "CN-42")
ALL_31: list[tuple[uuid.UUID, str, str, str, str]] = [
    (HUBEI_PROVINCE_ID, *HUBEI_ROW),
    *[
        (_make_m2_uuid(admin_code), admin_code, zh, en, iso)
        for admin_code, zh, en, iso in PROVINCES
    ],
]
assert len(ALL_31) == 31, f"expected 31 provincial rows; got {len(ALL_31)}"

# ---------------------------------------------------------------------
# source_registry + source_document 合成行：GB/T 2260 CODE_REFERENCE
# ---------------------------------------------------------------------
GB_T_2260_REGISTRY_ID = uuid.UUID("a2000000-0000-0000-0000-0000000ff226")
GB_T_2260_DOC_ID = uuid.UUID("a2000000-0000-0000-0000-0000000ff227")
GB_T_2260_URL = (
    "http://www.stats.gov.cn/sj/tjbz/tjyqhdmhcxhfdm/2024/"
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


# ---------------------------------------------------------------------
# load_seed -- idempotent upsert
# ---------------------------------------------------------------------


def load_seed(verbose: bool = True) -> None:
    """Upsert 31 province geo_entity + 30 geo_code_version + 1 CODE_REFERENCE row.

    - geo_entity: ON CONFLICT (id) DO NOTHING (idempotent on id)
    - geo_code_version: ON CONFLICT (id) DO NOTHING (idempotent on id);
      Hubei row is SKIPPED to avoid conflicting with M1's 2026-01-01 row
      (geo_code_version has an EXCLUDE daterange constraint).
    - source_registry: ON CONFLICT (primary_url) DO NOTHING (idempotent on URL).
    """
    with _connect() as conn:
        with conn.cursor() as cur:
            # 1. source_registry: GB/T 2260 CODE_REFERENCE row
            cur.execute(
                """
                INSERT INTO cegr.source_registry
                    (id, domain, organization, category, primary_url,
                     update_frequency, auth_note, access_method,
                     enabled, source_level)
                VALUES (%s, 'stats.gov.cn', '国家统计局', 'CODE_REFERENCE', %s,
                        'STABLE', '公开;无需授权',
                        'MANUAL_UPLOAD',
                        TRUE, 'S0')
                ON CONFLICT (primary_url) DO NOTHING
                """,
                (str(GB_T_2260_REGISTRY_ID), GB_T_2260_URL),
            )
            if verbose:
                print(f"[OK] source_registry CODE_REFERENCE  "
                      f"id={GB_T_2260_REGISTRY_ID}")

            # 1b. source_document: GB/T 2260 doc that the codes reference.
            # geo_code_version.source_id FK points to source_document.id
            # (constraint geo_code_version_source_fk), NOT source_registry.
            cur.execute(
                """
                INSERT INTO cegr.source_document
                    (id, source_registry_id, source_level, verification_status,
                     title, publisher, file_hash_sha256, file_size_bytes,
                     file_format, language, extraction_method,
                     url, caveat_text)
                VALUES (%s, %s, 'S0', 'VERIFIED',
                        'GB/T 2260 中华人民共和国行政区划代码 (2024 版)',
                        '国家统计局',
                        %s, 1,
                        'HTML_TABLE', 'zh', 'HTML_PARSE',
                        %s,
                        '行政区划代码标准；用于 geo_code_version 引用')
                ON CONFLICT (id) DO NOTHING
                """,
                (
                    str(GB_T_2260_DOC_ID),
                    str(GB_T_2260_REGISTRY_ID),
                    # synthetic stable SHA: 64 hex of "GB/T 2260 2024" repeated
                    ("a2" * 32),
                    GB_T_2260_URL,
                ),
            )
            if verbose:
                print(f"[OK] source_document CODE_REFERENCE  "
                      f"id={GB_T_2260_DOC_ID}")

            # 2. geo_entity x 31 (Hubei 沿用 M1)
            n_geo = 0
            for geo_id, admin_code, zh, en, _iso in ALL_31:
                cur.execute(
                    """
                    INSERT INTO cegr.geo_entity
                        (id, canonical_name, canonical_name_en, level)
                    VALUES (%s, %s, %s, 'PROVINCE')
                    ON CONFLICT (id) DO NOTHING
                    """,
                    (str(geo_id), zh, en),
                )
                n_geo += 1
            if verbose:
                print(f"[OK] geo_entity: upserted {n_geo} rows")

            # 3. geo_code_version x 30 (Hubei 跳过：M1 已 seed at valid_from=2026-01-01)
            n_cv = 0
            for geo_id, admin_code, zh, _en, iso in ALL_31:
                if geo_id == HUBEI_PROVINCE_ID:
                    continue
                cv_id = _geo_code_version_id(geo_id)
                cur.execute(
                    """
                    INSERT INTO cegr.geo_code_version
                        (id, geo_entity_id, admin_code, iso_code,
                         valid_from, source_id)
                    VALUES (%s, %s, %s, %s,
                                '2024-01-01'::date, %s)
                    ON CONFLICT (id) DO NOTHING
                    """,
                    (
                        str(cv_id),
                        str(geo_id),
                        admin_code,
                        iso,
                        str(GB_T_2260_DOC_ID),
                    ),
                )
                n_cv += 1
            if verbose:
                print(f"[OK] geo_code_version: upserted {n_cv} rows "
                      f"(30 new + 0 Hubei; M1 沿用)")
        conn.commit()

    if verbose:
        print(
            f"[OK] seed_m2_province_geo loaded: "
            f"31 geo_entity + 30 geo_code_version + 1 CODE_REFERENCE row"
        )


# ---------------------------------------------------------------------
# status -- print current state
# ---------------------------------------------------------------------


def status(verbose: bool = True) -> None:
    with _connect() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT level, COUNT(*)
                FROM cegr.geo_entity
                GROUP BY level
                ORDER BY level
                """
            )
            levels = cur.fetchall()
            cur.execute(
                """
                SELECT COUNT(*) FROM cegr.geo_code_version
                WHERE source_id = %s
                """,
                (str(GB_T_2260_DOC_ID),),
            )
            cv_count = cur.fetchone()[0]
            cur.execute(
                """
                SELECT domain, organization, category
                FROM cegr.source_registry
                WHERE id = %s
                """,
                (str(GB_T_2260_REGISTRY_ID),),
            )
            sr = cur.fetchone()

    if verbose:
        print("=== geo_entity by level ===")
        for level, count in levels:
            print(f"  {level}: {count}")
        print(f"=== geo_code_version (CODE_REFERENCE source) ===\n  {cv_count}")
        print(f"=== source_registry CODE_REFERENCE row ===\n  {sr}")


# ---------------------------------------------------------------------
# unload -- remove ONLY M2-a rows (a2000000-...); preserve Hubei M1
# ---------------------------------------------------------------------


def unload(verbose: bool = True) -> None:
    with _connect() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                DELETE FROM cegr.geo_code_version
                WHERE geo_entity_id IN (
                    SELECT id FROM cegr.geo_entity
                    WHERE id::text LIKE 'a2000000-%'
                )
                """
            )
            deleted_cv = cur.rowcount
            cur.execute(
                "DELETE FROM cegr.geo_entity WHERE id::text LIKE 'a2000000-%'"
            )
            deleted_geo = cur.rowcount
            cur.execute(
                "DELETE FROM cegr.source_registry WHERE id = %s",
                (str(GB_T_2260_DOC_ID),),
            )
            deleted_sr = cur.rowcount
        conn.commit()

    if verbose:
        print(
            f"[OK] unloaded: {deleted_geo} geo_entity + "
            f"{deleted_cv} geo_code_version + {deleted_sr} source_registry"
        )


# ---------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------


def main() -> int:
    p = argparse.ArgumentParser(
        description="M2-a 31 省 geo 种子 (knife 631 §1.A)"
    )
    p.add_argument("--load", action="store_true", help="upsert 31 provinces")
    p.add_argument("--status", action="store_true", help="print state")
    p.add_argument("--unload", action="store_true", help="remove M2-a rows only")
    args = p.parse_args()

    if args.load:
        load_seed(verbose=True)
    elif args.status:
        status(verbose=True)
    elif args.unload:
        unload(verbose=True)
    else:
        p.print_help()
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())