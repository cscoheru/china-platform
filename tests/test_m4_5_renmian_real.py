"""Tests for knife 642 M4.5 任免真实化 spike (≥6 cases).

Per tasking 642 §B:
- fetch 报告存在 + 顶层裁定 REAL_FETCHED
- evidence JSON parses + 4 source SHAs (3 新 + 1 重复撞 641) + http_count ≤ 12
- seed SQL 6 表 × 1 real each × 3 source = 18 INSERT (heilongjiang SHA 撞 641 ⇒ 排除)
- seed lineage is_demo='false' 隔离 (vs 640 demo is_demo='true')
- seed 3 真实 SHA ≠ 640 demo SHA 0…02 ≠ 641 real SHA 0…26e5 ≠ 639 demo SHA 0…01
- docs/63 六段 + 不宣称 PASS

All tests are read-only (no DB / no network).
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))

DOC_63 = REPO_ROOT / "docs" / "63-m4-5-renmian-real-20260901.md"
REPORT_MD = REPO_ROOT / "docs" / "reports" / "m4_5_renmian_real_20260901.md"
EVIDENCE_JSON = REPO_ROOT / "evidence_pack" / "m4_5_renmian_real_20260901.json"
SEED_SQL = REPO_ROOT / "scripts" / "seed_m4_5_renmian_real.sql"
FETCH_SCRIPT = REPO_ROOT / "scripts" / "fetch_m4_5_renmian_v1_2024.py"

# 3 新真实 SHA from 642-A.2 真实抓取 (henan/guangdong/guizhou)
REAL_SHA_HENAN = "cd6aff30260779ef84d2e83da724334387e3d6ae776633be3de772adbcc0f746"
REAL_SHA_GUANGDONG = "4349ee0ff814d38abb41ea397bd89a774b607763b88e3677312fdae8931e6894"
REAL_SHA_GUIZHOU = "fede03baaeecd8f6c2d6f646904bb64662d74bd70d2f25c3588ef1f9569dcd39"
# 641 真实 SHA (王正军任免 detail page) — 撞 ⇒ 排除
REAL_SHA_641_HEILONGJIANG = "26e5379d86e6a5c6a596acfef41293821a07413e973e1481b2b373f2e00b87ab"
# 640 demo SHA '0…02'
DEMO_SHA_640 = "0000000000000000000000000000000000000000000000000000000000000002"
# 639 demo SHA '0…01'
DEMO_SHA_639 = "0000000000000000000000000000000000000000000000000000000000000001"


def _strip_sql_comments(s: str) -> str:
    """Strip SQL line (--) and block (/* */) comments before keyword scan."""
    s = re.sub(r"--[^\n]*", "", s)
    s = re.sub(r"/\*.*?\*/", "", s, flags=re.DOTALL)
    return s


def test_m4_5_renmian_fetch_report_exists_and_has_top_verdict():
    """642-A.2 fetch 报告存在 + 顶层裁定 REAL_FETCHED."""
    assert REPORT_MD.exists(), f"M4.5 fetch markdown missing: {REPORT_MD}"
    text = REPORT_MD.read_text(encoding="utf-8")
    assert "## 0. 顶层裁定" in text
    assert "REAL_FETCHED" in text, (
        "M4.5 fetch report missing REAL_FETCHED top verdict"
    )
    assert "总抓取" in text or "样本" in text
    # 真实抓取源 URL 必出现
    assert "henan.gov.cn" in text
    assert "gd.gov.cn" in text
    assert "guizhou.gov.cn" in text


def test_m4_5_renmian_evidence_json_parses_and_http_count():
    """642-A.2 evidence JSON parses + fetched_count + http_count ≤ 12."""
    assert EVIDENCE_JSON.exists(), f"M4.5 evidence JSON missing: {EVIDENCE_JSON}"
    data = json.loads(EVIDENCE_JSON.read_text(encoding="utf-8"))
    assert "summary" in data
    assert "cells" in data
    assert "fetch_log" in data
    sv = data["summary"]
    assert sv["fetch_status"] == "REAL_FETCHED", (
        f"fetch_status = {sv['fetch_status']}, expected REAL_FETCHED"
    )
    assert sv["fetched_count"] >= 1, (
        f"fetched_count = {sv['fetched_count']}, expected ≥ 1"
    )
    # ≤12 HTTP total 红线
    assert sv["http_count"] <= 12, (
        f"http_count = {sv['http_count']}, exceeds ≤ 12 红线"
    )
    # 真实 SHA 64 hex chars
    for cell in data["cells"]:
        sha = cell.get("file_hash_sha256", "")
        assert re.match(r"^[0-9a-f]{64}$", sha), (
            f"cell sha not 64 hex: {sha}"
        )


def _count_uuids(sql_text: str, uuids: list[str]) -> int:
    """Count how many of the expected per-row UUIDs appear in the SQL.

    比 VALUES-tuple regex 更可靠: string literal 含 ASCII 括号
    (`(狄绯任免 / spike 1)`) 会让 `[^)]*` 提前中断;但 per-row UUID
    prefix 是确定 key.
    """
    return sum(1 for u in uuids if u in sql_text)


# 3 试点省 × 6 政策表 各 3 行 UUID (lineage JSONB 已统一 chain_id;
# per-row UUID prefix 唯一, 按表命名)
TABLE_UUIDS = {
    "source_registry": [
        "d0eebc99-9c0b-4ef8-bb6d-6bb9bd380a01",
        "d0eebc99-9c0b-4ef8-bb6d-6bb9bd380a02",
        "d0eebc99-9c0b-4ef8-bb6d-6bb9bd380a03",
    ],
    "source_document": [
        "d0eebc99-9c0b-4ef8-bb6d-6bb9bd380a11",
        "d0eebc99-9c0b-4ef8-bb6d-6bb9bd380a12",
        "d0eebc99-9c0b-4ef8-bb6d-6bb9bd380a13",
    ],
    "policy_document": [
        "d1eebc99-9c0b-4ef8-bb6d-6bb9bd380a21",
        "d1eebc99-9c0b-4ef8-bb6d-6bb9bd380a22",
        "d1eebc99-9c0b-4ef8-bb6d-6bb9bd380a23",
    ],
    "policy_target": [
        "d2eebc99-9c0b-4ef8-bb6d-6bb9bd380a31",
        "d2eebc99-9c0b-4ef8-bb6d-6bb9bd380a32",
        "d2eebc99-9c0b-4ef8-bb6d-6bb9bd380a33",
    ],
    "policy_measure": [
        "d3eebc99-9c0b-4ef8-bb6d-6bb9bd380a41",
        "d3eebc99-9c0b-4ef8-bb6d-6bb9bd380a42",
        "d3eebc99-9c0b-4ef8-bb6d-6bb9bd380a43",
    ],
    "government_commitment": [
        "d4eebc99-9c0b-4ef8-bb6d-6bb9bd380a51",
        "d4eebc99-9c0b-4ef8-bb6d-6bb9bd380a52",
        "d4eebc99-9c0b-4ef8-bb6d-6bb9bd380a53",
    ],
    "commitment_progress": [
        "d5eebc99-9c0b-4ef8-bb6d-6bb9bd380a61",
        "d5eebc99-9c0b-4ef8-bb6d-6bb9bd380a62",
        "d5eebc99-9c0b-4ef8-bb6d-6bb9bd380a63",
    ],
    "project_event": [
        "d6eebc99-9c0b-4ef8-bb6d-6bb9bd380a71",
        "d6eebc99-9c0b-4ef8-bb6d-6bb9bd380a72",
        "d6eebc99-9c0b-4ef8-bb6d-6bb9bd380a73",
    ],
}


def test_seed_m4_5_sql_exists_and_has_real_data():
    """642-A.2 seed SQL 存在 + 8 表 × 3 真实 each = 24 行 (per-table UUID 验证)."""
    assert SEED_SQL.exists(), f"seed_m4_5_renmian_real.sql missing: {SEED_SQL}"
    text = SEED_SQL.read_text(encoding="utf-8")
    # 8 表 各 3 行 (3 试点省; UUID 唯一性保证无重复)
    expected_per_table = 3
    for tbl, uuids in TABLE_UUIDS.items():
        rows = _count_uuids(text, uuids)
        assert rows == expected_per_table, (
            f"{tbl} per-row UUID count = {rows}, expected {expected_per_table}"
        )
    # 红线: 不删表 / 不 DROP COLUMN / 不 DELETE FROM 真实数据
    text_no_comments = _strip_sql_comments(text)
    forbidden = [
        "DROP TABLE", "DROP COLUMN", "DROP INDEX",
        "DELETE FROM", "TRUNCATE",
    ]
    for f in forbidden:
        assert f not in text_no_comments, (
            f"seed_m4_5_renmian_real.sql (after comment strip) "
            f"contains forbidden DML/DDL: {f!r}"
        )


def test_seed_m4_5_sql_lineage_is_demo_false_isolation():
    """642-A.2 seed SQL 所有 6 政策表 × 3 行 lineage JSONB is_demo='false'."""
    assert SEED_SQL.exists()
    text = SEED_SQL.read_text(encoding="utf-8")
    # 6 政策表均需有 is_demo='false' (或 "is_demo": "false")
    policy_tables = [
        "policy_document", "policy_target", "policy_measure",
        "government_commitment", "commitment_progress", "project_event",
    ]
    for tbl in policy_tables:
        # 抓所有 INSERT block (粗正则)
        blocks = re.findall(
            rf"INSERT INTO {tbl}.*?ON CONFLICT",
            text, re.DOTALL,
        )
        assert blocks, f"seed SQL missing INSERT INTO {tbl} ... ON CONFLICT block"
        for block in blocks:
            # 含 is_demo='false' (SQL string) 或 "is_demo": "false" (JSON literal)
            # 或 jsonb_build_object 'is_demo', 'false' (SELECT-style)
            is_false = (
                "is_demo" in block
                and (
                    "'false'" in block
                    or "'false'," in block
                    or '"is_demo": "false"' in block
                    or "'is_demo', 'false'" in block
                )
            )
            assert is_false, f"{tbl} block missing is_demo='false' (real sentinel)"
    # 红线: 真实化 seed 不含 is_demo='true' (避免与 640 demo 混淆)
    text_compact = text.replace(" ", "").replace("\n", "").replace("\t", "")
    assert '"is_demo":"true"' not in text_compact, (
        "seed_m4_5_renmian_real.sql must not contain lineage is_demo='true' "
        "(real seed only; demo is_demo=true belongs to 640 seed only)"
    )
    # JSON boolean false (必须是字符串 "false" per sentinel)
    bad_bool = re.search(r'"is_demo"\s*:\s*false\b(?!")', text_compact)
    assert not bad_bool, (
        "seed SQL must not contain JSON boolean false for is_demo "
        "(must be string 'false' per docs/33 §3.2 sentinel)"
    )


def test_seed_m4_5_sql_real_sha_distinct_from_prior_shas():
    """642-A.2 3 真实 SHA (henan/guangdong/guizhou) ≠ 640 demo / ≠ 641 real / ≠ 639 demo."""
    assert SEED_SQL.exists()
    text_raw = SEED_SQL.read_text(encoding="utf-8")
    # 去掉 SQL 注释,只扫可执行 SQL
    text = _strip_sql_comments(text_raw)
    # 3 新真实 SHA 必须出现
    for sha in (REAL_SHA_HENAN, REAL_SHA_GUANGDONG, REAL_SHA_GUIZHOU):
        assert sha in text, (
            f"seed_m4_5_renmian_real.sql missing real SHA {sha}"
        )
    # 3 新 SHA 不应是 demo SHA (排除 0…02 / 0…01 模式)
    for sha in (REAL_SHA_HENAN, REAL_SHA_GUANGDONG, REAL_SHA_GUIZHOU):
        assert sha != DEMO_SHA_640
        assert sha != DEMO_SHA_639
        assert sha != REAL_SHA_641_HEILONGJIANG, (
            f"642 real SHA {sha} must differ from 641 real SHA "
            f"{REAL_SHA_641_HEILONGJIANG} (avoid SHA collision)"
        )
    # 642 seed 不含 641 real SHA (王正军任免);heilongjiang 因 SHA 撞 641 已被排除
    assert REAL_SHA_641_HEILONGJIANG not in text, (
        f"seed_m4_5_renmian_real.sql must not contain 641 real SHA "
        f"{REAL_SHA_641_HEILONGJIANG} (heilongjiang SHA collision — excluded)"
    )
    # 642 seed 不含 640 demo SHA 0…02 / 639 demo SHA 0…01
    assert DEMO_SHA_640 not in text, (
        f"seed_m4_5_renmian_real.sql must not contain 640 demo SHA "
        f"{DEMO_SHA_640} (real SHA must be distinct)"
    )
    assert DEMO_SHA_639 not in text, (
        f"seed_m4_5_renmian_real.sql must not contain 639 demo SHA "
        f"{DEMO_SHA_639} (real SHA must be distinct)"
    )
    # 真实 URL 必须出现
    real_urls = [
        "https://www.henan.gov.cn/2026/08-21/3401380.html",
        "https://www.gd.gov.cn/zwgk/rsxx/content/post_4917420.html",
        "https://www.guizhou.gov.cn/zwgk/zcfg/szfwj/qfr/202608/t20260828_90796146.html",
    ]
    for url in real_urls:
        assert url in text, f"seed_m4_5_renmian_real.sql missing real URL {url}"
    # R3-E provenance chain_id='real_642_m4_5_renmian' 必须出现
    assert "real_642_m4_5_renmian" in text, (
        "seed SQL missing R3-E provenance chain_id='real_642_m4_5_renmian'"
    )
    # 642 seed 不含 641 chain_id (避免 chain_id 撞)
    assert "real_641_heilongjiang" not in text, (
        "seed_m4_5_renmian_real.sql must not contain 641 chain_id "
        "(chain_id 'real_642_m4_5_renmian' is distinct)"
    )


def test_doc_63_has_six_sections():
    """docs/63 含 ## 1.-## 6. 六段 + 标头属性."""
    assert DOC_63.exists(), f"docs/63 missing: {DOC_63}"
    text = DOC_63.read_text(encoding="utf-8")
    for n in ("## 1.", "## 2.", "## 3.", "## 4.", "## 5.", "## 6."):
        assert n in text, f"docs/63 missing section {n}"
    # 标头属性
    assert "63" in text[:200]
    assert "2026-09-01" in text
    assert "642" in text
    # M4.5 关键要素
    assert "real_642_m4_5_renmian" in text
    assert "is_demo='false'" in text or '"is_demo": "false"' in text
    assert "642 tasking" in text or "spike" in text


def test_doc_63_no_pass_announcement():
    """docs/63 不宣称 M2/M4/Gate PASS (智能排除 disclaimer 否定句)."""
    assert DOC_63.exists()
    text = DOC_63.read_text(encoding="utf-8")
    sec6 = text[text.index("## 6."):]
    for keyword in ("M4 PASS", "Gate PASS", "M2 PASS"):
        positive_lines = [
            line for line in sec6.splitlines()
            if keyword in line and "不宣布" not in line
            and "不声称" not in line and "不宣称" not in line
            and "不宣告" not in line
        ]
        assert not positive_lines, (
            f"docs/63 §6 contains positive {keyword} claim: "
            f"{positive_lines!r}"
        )


def test_seed_m4_5_sql_has_select_subquery_for_geo_entity():
    """642-A.2 government_commitment + project_event 用 SELECT 子查询 geo_entity_id."""
    assert SEED_SQL.exists()
    text = SEED_SQL.read_text(encoding="utf-8")
    # government_commitment 块含 FROM geo_entity g
    gc_blocks = re.findall(
        r"INSERT INTO government_commitment.*?ON CONFLICT",
        text, re.DOTALL,
    )
    assert gc_blocks
    for b in gc_blocks:
        assert "FROM geo_entity g" in b, (
            "government_commitment block must use SELECT subquery "
            "from geo_entity for real geo_entity_id (per 641 sentinel)"
        )
        assert "LIMIT 1" in b, (
            "government_commitment block must use LIMIT 1 "
            "(avoid multi-row subquery)"
        )
    # project_event 块含 FROM geo_entity g
    proj_blocks = re.findall(
        r"INSERT INTO project_event.*?ON CONFLICT",
        text, re.DOTALL,
    )
    assert proj_blocks
    for b in proj_blocks:
        assert "FROM geo_entity g" in b, (
            "project_event block must use SELECT subquery "
            "from geo_entity for real geo_entity_id"
        )
        assert "LIMIT 1" in b, (
            "project_event block must use LIMIT 1"
        )