"""Tests for knife 643 M4.6 政府工作报告真实化 spike (≥8 cases).

Per tasking 643 §B.2:
- fetch 报告存在 + 顶层裁定 REAL_FETCHED
- evidence JSON parses + 3 真实样本 + http_count ≤ 12
- seed SQL 8 表 × 3 真实 each = 24 行
- seed SQL lineage is_demo='false' 隔离
- seed SQL 3 真实 SHA ≠ 640/641/642/639 demo/real SHA + chain_id='real_643_m4_6_govreport'
- docs/65 六段 + 不宣称 PASS
- seed SQL has SELECT subquery for geo_entity (government_commitment + project_event)

All tests are read-only (no DB / no network).
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))

DOC_65 = REPO_ROOT / "docs" / "65-m4-6-govreport-real-20260901.md"
REPORT_MD = REPO_ROOT / "docs" / "reports" / "m4_6_govreport_real_20260901.md"
EVIDENCE_JSON = REPO_ROOT / "evidence_pack" / "m4_6_govreport_real_20260901.json"
SEED_SQL = REPO_ROOT / "scripts" / "seed_m4_6_govreport_real.sql"
FETCH_SCRIPT = REPO_ROOT / "scripts" / "fetch_m4_6_govreport_v1_2024.py"

# 3 新真实 SHA from 643-A.2 真实抓取 (hlj/henan/yunnan 政府公报)
REAL_SHA_HEILONGJIANG = (
    "e68099df39fa09bad9c63201e5fab80af66302bce5c1deeea62fc2bda68ea1c3"
)
REAL_SHA_HENAN = (
    "631094910323dc63e59483af5048cd70b2fe9dfaedf1265f215ce159c5d80bf1"
)
REAL_SHA_YUNNAN = (
    "93fe23b32d083581456cc17be66361a36ca13caa28d25f63e9466d0c1cb8c6b0"
)
# 642 真实 SHA (任免) — 撞 ⇒ 排除
REAL_SHA_642_HENAN = (
    "cd6aff30260779ef84d2e83da724334387e3d6ae776633be3de772adbcc0f746"
)
REAL_SHA_642_GUANGDONG = (
    "4349ee0ff814d38abb41ea397bd89a774b607763b88e3677312fdae8931e6894"
)
REAL_SHA_642_GUIZHOU = (
    "fede03baaeecd8f6c2d6f646904bb64662d74bd70d2f25c3588ef1f9569dcd39"
)
# 641 真实 SHA (王正军任免) — 撞 ⇒ 排除
REAL_SHA_641_HEILONGJIANG = (
    "26e5379d86e6a5c6a596acfef41293821a07413e973e1481b2b373f2e00b87ab"
)
# 640 demo SHA '0…02'
DEMO_SHA_640 = "0000000000000000000000000000000000000000000000000000000000000002"
# 639 demo SHA '0…01'
DEMO_SHA_639 = "0000000000000000000000000000000000000000000000000000000000000001"


def _strip_sql_comments(s: str) -> str:
    """Strip SQL line (--) and block (/* */) comments before keyword scan."""
    s = re.sub(r"--[^\n]*", "", s)
    s = re.sub(r"/\*.*?\*/", "", s, flags=re.DOTALL)
    return s


def test_m4_6_govreport_fetch_report_exists_and_has_top_verdict():
    """643-A.2 fetch 报告存在 + 顶层裁定 REAL_FETCHED."""
    assert REPORT_MD.exists(), f"M4.6 fetch markdown missing: {REPORT_MD}"
    text = REPORT_MD.read_text(encoding="utf-8")
    assert "## 0. 顶层裁定" in text
    assert "REAL_FETCHED" in text, (
        "M4.6 fetch report missing REAL_FETCHED top verdict"
    )
    assert "总抓取" in text or "样本" in text
    # 真实抓取源 URL 必出现 (3 试点省)
    assert "hlj.gov.cn" in text
    assert "henan.gov.cn" in text
    assert "yn.gov.cn" in text
    # 政府工作报告关键词
    assert "政府工作" in text or "政府公报" in text


def test_m4_6_govreport_evidence_json_parses_and_http_count():
    """643-A.2 evidence JSON parses + fetched_count + http_count ≤ 12."""
    assert EVIDENCE_JSON.exists(), f"M4.6 evidence JSON missing: {EVIDENCE_JSON}"
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
    会让 `[^)]*` 提前中断;但 per-row UUID prefix 是确定 key.
    """
    return sum(1 for u in uuids if u in sql_text)


# 3 试点省 × 8 表 各 3 行 UUID (lineage JSONB 已统一 chain_id;
# per-row UUID prefix 唯一, 按表命名)
TABLE_UUIDS = {
    "source_registry": [
        "d0eebc99-9c0b-4ef8-bb6d-6bb9bd380b21",
        "d0eebc99-9c0b-4ef8-bb6d-6bb9bd380b22",
        "d0eebc99-9c0b-4ef8-bb6d-6bb9bd380b23",
    ],
    "source_document": [
        "d0eebc99-9c0b-4ef8-bb6d-6bb9bd380b31",
        "d0eebc99-9c0b-4ef8-bb6d-6bb9bd380b32",
        "d0eebc99-9c0b-4ef8-bb6d-6bb9bd380b33",
    ],
    "policy_document": [
        "d1eebc99-9c0b-4ef8-bb6d-6bb9bd380b41",
        "d1eebc99-9c0b-4ef8-bb6d-6bb9bd380b42",
        "d1eebc99-9c0b-4ef8-bb6d-6bb9bd380b43",
    ],
    "policy_target": [
        "d2eebc99-9c0b-4ef8-bb6d-6bb9bd380b51",
        "d2eebc99-9c0b-4ef8-bb6d-6bb9bd380b52",
        "d2eebc99-9c0b-4ef8-bb6d-6bb9bd380b53",
    ],
    "policy_measure": [
        "d3eebc99-9c0b-4ef8-bb6d-6bb9bd380b61",
        "d3eebc99-9c0b-4ef8-bb6d-6bb9bd380b62",
        "d3eebc99-9c0b-4ef8-bb6d-6bb9bd380b63",
    ],
    "government_commitment": [
        "d4eebc99-9c0b-4ef8-bb6d-6bb9bd380b71",
        "d4eebc99-9c0b-4ef8-bb6d-6bb9bd380b72",
        "d4eebc99-9c0b-4ef8-bb6d-6bb9bd380b73",
    ],
    "commitment_progress": [
        "d5eebc99-9c0b-4ef8-bb6d-6bb9bd380b81",
        "d5eebc99-9c0b-4ef8-bb6d-6bb9bd380b82",
        "d5eebc99-9c0b-4ef8-bb6d-6bb9bd380b83",
    ],
    "project_event": [
        "d6eebc99-9c0b-4ef8-bb6d-6bb9bd380b91",
        "d6eebc99-9c0b-4ef8-bb6d-6bb9bd380b92",
        "d6eebc99-9c0b-4ef8-bb6d-6bb9bd380b93",
    ],
}


def test_seed_m4_6_sql_exists_and_has_real_data():
    """643-A.3 seed SQL 存在 + 8 表 × 3 真实 each = 24 行 (per-table UUID 验证)."""
    assert SEED_SQL.exists(), f"seed_m4_6_govreport_real.sql missing: {SEED_SQL}"
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
            f"seed_m4_6_govreport_real.sql (after comment strip) "
            f"contains forbidden DML/DDL: {f!r}"
        )


def test_seed_m4_6_sql_lineage_is_demo_false_isolation():
    """643-A.3 seed SQL 所有 6 政策表 × 3 行 lineage JSONB is_demo='false'."""
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
        "seed_m4_6_govreport_real.sql must not contain lineage is_demo='true' "
        "(real seed only; demo is_demo=true belongs to 640 seed only)"
    )
    # JSON boolean false (必须是字符串 "false" per sentinel)
    bad_bool = re.search(r'"is_demo"\s*:\s*false\b(?!")', text_compact)
    assert not bad_bool, (
        "seed SQL must not contain JSON boolean false for is_demo "
        "(must be string 'false' per docs/33 §3.2 sentinel)"
    )


def test_seed_m4_6_sql_real_sha_distinct_from_prior_shas():
    """643-A.3 3 真实 SHA (hlj/henan/yunnan) ≠ 640/641/642/639 demo/real SHA."""
    assert SEED_SQL.exists()
    text_raw = SEED_SQL.read_text(encoding="utf-8")
    # 去掉 SQL 注释,只扫可执行 SQL
    text = _strip_sql_comments(text_raw)
    # 3 新真实 SHA 必须出现
    for sha in (REAL_SHA_HEILONGJIANG, REAL_SHA_HENAN, REAL_SHA_YUNNAN):
        assert sha in text, (
            f"seed_m4_6_govreport_real.sql missing real SHA {sha}"
        )
    # 3 新 SHA 不应是 demo SHA (排除 0…02 / 0…01 模式)
    for sha in (REAL_SHA_HEILONGJIANG, REAL_SHA_HENAN, REAL_SHA_YUNNAN):
        assert sha != DEMO_SHA_640
        assert sha != DEMO_SHA_639
        assert sha != REAL_SHA_641_HEILONGJIANG, (
            f"643 real SHA {sha} must differ from 641 real SHA "
            f"{REAL_SHA_641_HEILONGJIANG} (avoid SHA collision)"
        )
        assert sha != REAL_SHA_642_HENAN, (
            f"643 real SHA {sha} must differ from 642 real SHA"
        )
        assert sha != REAL_SHA_642_GUANGDONG, (
            f"643 real SHA {sha} must differ from 642 real SHA"
        )
        assert sha != REAL_SHA_642_GUIZHOU, (
            f"643 real SHA {sha} must differ from 642 real SHA"
        )
    # 643 seed 不含 642 真实 SHA (任免 endpoint)
    for sha in (REAL_SHA_642_HENAN, REAL_SHA_642_GUANGDONG, REAL_SHA_642_GUIZHOU):
        assert sha not in text, (
            f"seed_m4_6_govreport_real.sql must not contain 642 real SHA "
            f"{sha} (endpoint ≠ 政府工作报告 endpoint)"
        )
    # 643 seed 不含 641 真实 SHA (王正军任免);heilongjiang 643 是政府公报 SHA, 不同
    assert REAL_SHA_641_HEILONGJIANG not in text, (
        f"seed_m4_6_govreport_real.sql must not contain 641 real SHA "
        f"{REAL_SHA_641_HEILONGJIANG} (王正军任免;SHA 不撞)"
    )
    # 643 seed 不含 640 demo SHA 0…02 / 639 demo SHA 0…01
    assert DEMO_SHA_640 not in text, (
        f"seed_m4_6_govreport_real.sql must not contain 640 demo SHA "
        f"{DEMO_SHA_640} (real SHA must be distinct)"
    )
    assert DEMO_SHA_639 not in text, (
        f"seed_m4_6_govreport_real.sql must not contain 639 demo SHA "
        f"{DEMO_SHA_639} (real SHA must be distinct)"
    )
    # 真实 URL 必须出现 (3 试点省)
    real_urls = [
        "https://www.hlj.gov.cn/hlj/c107882/redirect_firstChannel.shtml",
        "https://www.henan.gov.cn/2026/07-29/3380417.html",
        "https://www.yn.gov.cn/zwgk/zfgb/",
    ]
    for url in real_urls:
        assert url in text, f"seed_m4_6_govreport_real.sql missing real URL {url}"
    # R3-E provenance chain_id='real_643_m4_6_govreport' 必须出现
    assert "real_643_m4_6_govreport" in text, (
        "seed SQL missing R3-E provenance chain_id='real_643_m4_6_govreport'"
    )
    # 643 seed 不含 641/642 chain_id (避免 chain_id 撞)
    assert "real_641_heilongjiang" not in text, (
        "seed_m4_6_govreport_real.sql must not contain 641 chain_id "
        "(chain_id 'real_643_m4_6_govreport' is distinct)"
    )
    assert "real_642_m4_5_renmian" not in text, (
        "seed_m4_6_govreport_real.sql must not contain 642 chain_id "
        "(chain_id 'real_643_m4_6_govreport' is distinct)"
    )


def test_doc_65_has_six_sections():
    """643-A.4 docs/65 含 ## 1.-## 6. 六段 + 标头属性."""
    assert DOC_65.exists(), f"docs/65 missing: {DOC_65}"
    text = DOC_65.read_text(encoding="utf-8")
    for n in ("## 1.", "## 2.", "## 3.", "## 4.", "## 5.", "## 6."):
        assert n in text, f"docs/65 missing section {n}"
    # 标头属性
    assert "65" in text[:200]
    assert "2026-09-01" in text
    assert "643" in text
    # M4.6 关键要素
    assert "real_643_m4_6_govreport" in text
    assert "is_demo='false'" in text or '"is_demo": "false"' in text
    assert "643 tasking" in text or "spike" in text


def test_doc_65_no_pass_announcement():
    """643-A.4 docs/65 不宣称 M2/M4/Gate PASS (智能排除 disclaimer 否定句)."""
    assert DOC_65.exists()
    text = DOC_65.read_text(encoding="utf-8")
    sec6 = text[text.index("## 6."):]
    for keyword in ("M4 PASS", "M4.6 PASS", "Gate PASS", "M2 PASS"):
        positive_lines = [
            line for line in sec6.splitlines()
            if keyword in line and "不宣布" not in line
            and "不声称" not in line and "不宣称" not in line
            and "不宣告" not in line
        ]
        assert not positive_lines, (
            f"docs/65 §6 contains positive {keyword} claim: "
            f"{positive_lines!r}"
        )


def test_seed_m4_6_sql_has_select_subquery_for_geo_entity():
    """643-A.3 government_commitment + project_event 用 SELECT 子查询 geo_entity_id."""
    assert SEED_SQL.exists()
    text = SEED_SQL.read_text(encoding="utf-8")
    # government_commitment 必须含 SELECT FROM geo_entity g
    blocks_gc = re.findall(
        r"INSERT INTO government_commitment.*?FROM geo_entity g.*?ON CONFLICT",
        text, re.DOTALL,
    )
    assert len(blocks_gc) >= 3, (
        f"government_commitment SELECT 子查询 blocks = {len(blocks_gc)}, "
        f"expected ≥ 3 (hlj/henan/yunnan)"
    )
    for block in blocks_gc:
        assert "SELECT" in block and "FROM geo_entity g" in block
        assert "canonical_name = '黑龙江省'" in block or \
            "canonical_name = '河南省'" in block or \
            "canonical_name = '云南省'" in block
        assert "level = 'PROVINCIAL'" in block
        assert "LIMIT 1" in block
    # project_event 必须含 SELECT FROM geo_entity g
    blocks_pe = re.findall(
        r"INSERT INTO project_event.*?FROM geo_entity g.*?ON CONFLICT",
        text, re.DOTALL,
    )
    assert len(blocks_pe) >= 3, (
        f"project_event SELECT 子查询 blocks = {len(blocks_pe)}, "
        f"expected ≥ 3 (hlj/henan/yunnan)"
    )
    for block in blocks_pe:
        assert "SELECT" in block and "FROM geo_entity g" in block
        assert "LIMIT 1" in block