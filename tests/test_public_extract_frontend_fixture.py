# Knife 52 (tasking 349) — 公开提取 → 前端结构化呈现 的 fixture 溯源测试。
#
# Per 349 §SCHEMA:
#   (1) 前端 fixture 快照自 data/public_extracts/stats.gov.cn/NATIONAL_BULLETIN.json
#   (2) 显式 REGISTRY_SAMPLE / demo 标注, 非 live O1
#   (4) ≥1 测证据 (本文件)
#
# 溯源锚定策略:
#   fixture 的 source_sha256 必须 == source_registry/registry.csv 中
#   stats.gov.cn / NATIONAL_BULLETIN 行的 file_hash_sha256 (registry 锁定)。
#   **不做** fixture 与 live extract 文件的字节对比 — connector pytest
#   (test_auto_ingest_public_source_s52.py 的 main-returning case) 会重写
#   data/public_extracts/ 下的实跑产物 (commit 7f04237 即此因), 字节对比会
#   假性失败。fixture 是快照, registry SHA 才是稳定契约。
#
# 红线: sample ≠ live; 不伪造; 不宣称 O1/Gate PASS。

from __future__ import annotations

import csv
import json
import re
from pathlib import Path

import pytest

PROJECT_ROOT = Path(__file__).resolve().parent.parent
FIXTURE = PROJECT_ROOT / "frontend" / "lib" / "public_extract_nbs.json"
PE_PAGE = PROJECT_ROOT / "frontend" / "app" / "public-extracts" / "page.tsx"
HOME_PAGE = PROJECT_ROOT / "frontend" / "app" / "page.tsx"
REGISTRY = PROJECT_ROOT / "source_registry" / "registry.csv"


@pytest.fixture(scope="module")
def fixture_json() -> dict:
    assert FIXTURE.is_file(), f"missing fixture: {FIXTURE}"
    return json.loads(FIXTURE.read_text(encoding="utf-8"))


@pytest.fixture(scope="module")
def registry_row() -> dict:
    assert REGISTRY.is_file(), f"missing registry: {REGISTRY}"
    with REGISTRY.open(encoding="utf-8") as f:
        rows = list(csv.DictReader(f))
    matches = [
        r
        for r in rows
        if r["domain"] == "stats.gov.cn"
        and r["category"] == "NATIONAL_BULLETIN"
    ]
    assert len(matches) == 1, f"expected exactly 1 NBS row, got {len(matches)}"
    return matches[0]


def test_fixture_row_count_is_63(fixture_json: dict) -> None:
    """63 行 NBS 提取全量入 fixture (per knife 51 receipt 347 §6.3)."""
    assert fixture_json["row_count"] == 63
    assert len(fixture_json["rows"]) == 63


def test_fixture_provenance_sha_matches_registry(
    fixture_json: dict, registry_row: dict
) -> None:
    """fixture.source_sha256 == registry file_hash_sha256 (样本锁定锚点)."""
    assert fixture_json["source_sha256"] == registry_row["file_hash_sha256"]


def test_fixture_source_sample_path_matches_registry(
    fixture_json: dict, registry_row: dict
) -> None:
    """fixture 声明的样本路径 == registry local_sample_path."""
    assert fixture_json["source_sample_path"] == registry_row["local_sample_path"]


def test_fixture_first_row_key_shape(fixture_json: dict) -> None:
    """列序 = spike 提取原样 (两层表头展平后的 3 列); UI 表头依赖此形状."""
    first = fixture_json["rows"][0]
    assert list(first.keys()) == ["指 标", "7月", "1—7月"]


def test_page_imports_fixture_and_labels_registry_sample() -> None:
    """页面: fixture import + REGISTRY_SAMPLE 显式标注 + DemoBadge 复用."""
    src = PE_PAGE.read_text(encoding="utf-8")
    code = re.sub(r"//[^\n]*", "", src)
    code = re.sub(r"/\*.*?\*/", "", code, flags=re.DOTALL)
    assert "public_extract_nbs.json" in code, "page must import the fixture"
    assert "REGISTRY_SAMPLE" in code, "page must label REGISTRY_SAMPLE"
    assert "DemoBadge" in code, "page must reuse DemoBadge"
    assert "source_sha256" in code, "page must expose provenance SHA"


def test_page_does_not_claim_live_o1() -> None:
    """红线: sample ≠ live — 页面不得出现 live O1 收口措辞 (须有否定语)."""
    src = PE_PAGE.read_text(encoding="utf-8")
    assert "非 live O1" in src or "非live O1" in src, (
        "page must carry the '非 live O1' disclaimer (sample ≠ live closure)"
    )
    assert "O1_AUTO_INTAKED" not in src, (
        "page must not claim O1_AUTO_INTAKED (registry sample ≠ live intake)"
    )


def test_home_page_links_public_extracts() -> None:
    """首页导航入口 (per 349 §SCHEMA '首页或专用区块')."""
    src = HOME_PAGE.read_text(encoding="utf-8")
    assert "/public-extracts" in src
    assert "REGISTRY_SAMPLE" in src


# ---------------------------------------------------------------------------
# Knife 55 (tasking 358) — LIVE_CANDIDATE 并列分轨 (live WORM 提取候选)
# ---------------------------------------------------------------------------

LIVE_EXTRACT = (
    PROJECT_ROOT / "data" / "public_extracts" / "stats.gov.cn"
    / "NATIONAL_BULLETIN_LIVE_CANDIDATE.json"
)
LIVE_FIXTURE = (
    PROJECT_ROOT / "frontend" / "lib" / "public_extract_nbs_live_candidate.json"
)
WORM_ARCHIVE = (
    PROJECT_ROOT / "data" / "public_archives" / "2026-08" / "stats.gov.cn"
    / "zxfb"
)


@pytest.fixture(scope="module")
def live_extract_json() -> dict:
    assert LIVE_EXTRACT.is_file(), f"missing live extract: {LIVE_EXTRACT}"
    return json.loads(LIVE_EXTRACT.read_text(encoding="utf-8"))


def test_live_candidate_extract_shape(live_extract_json: dict) -> None:
    """Per 358 §SCHEMA (1): live WORM 提取 JSON 带 sha/path/row_count/rows,
    intake_status 语义 = LIVE_CANDIDATE; SHA 必须锚定 WORM 归档实字节。"""
    rec = live_extract_json
    assert rec["intake_status"] == "LIVE_CANDIDATE"
    assert rec["is_demo"] == "true"  # knife 333 CANDIDATE_AUTO 惯例
    assert rec["domain"] == "stats.gov.cn"
    assert rec["source_archive_path"].endswith("public_archives/2026-08/stats.gov.cn/zxfb")
    assert rec["source_deeplink_url"].startswith("https://www.stats.gov.cn/sj/zxfb/2026")
    assert isinstance(rec["rows"], list) and len(rec["rows"]) >= 1
    assert rec["row_count"] == len(rec["rows"])
    # SHA 锚定:提取记录的 sha == WORM 归档文件实算 sha == knife 54 live 实录
    import hashlib
    h = hashlib.sha256(WORM_ARCHIVE.read_bytes()).hexdigest()
    assert rec["source_sha256"] == h
    assert h == "0b85212f70055c38" + h[16:]  # knife 54 回执实录前缀


def test_live_candidate_fixture_mirrors_extract(
    live_extract_json: dict,
) -> None:
    """Per 358 §SCHEMA (3): 前端 fixture 与 data 侧 live 提取一致
    (knife 55 为一次性快照,数据文件不再被 connector 改写 — 352 已护)。"""
    assert LIVE_FIXTURE.is_file(), f"missing live fixture: {LIVE_FIXTURE}"
    fx = json.loads(LIVE_FIXTURE.read_text(encoding="utf-8"))
    assert fx == live_extract_json, "live fixture must mirror data-side extract"


def test_sample_track_not_overwritten(fixture_json: dict) -> None:
    """Per 358 §红线 'sample 与 live candidate 分轨': 交付后 sample 提取
    (data 侧) 与 sample fixture 仍锁定 registry 锚定 — 未被覆盖。"""
    sample_extract = (
        PROJECT_ROOT / "data" / "public_extracts" / "stats.gov.cn"
        / "NATIONAL_BULLETIN.json"
    )
    data_rec = json.loads(sample_extract.read_text(encoding="utf-8"))
    assert data_rec["row_count"] == 63
    assert data_rec["source_sha256"] == (
        "dea13b8a4ff116ca91403b189cdd60705545b28200f9023c3d56e6db03f3939d"
    )
    assert fixture_json["row_count"] == 63
    assert fixture_json["source_sha256"] == data_rec["source_sha256"]
    # live candidate 的 SHA 必须与 sample 锚定不同 (分轨存在的意义)
    live = json.loads(LIVE_EXTRACT.read_text(encoding="utf-8"))
    assert live["source_sha256"] != data_rec["source_sha256"]


def test_page_renders_live_candidate_track() -> None:
    """Per 358 §SCHEMA (3): /public-extracts 页 import live fixture、标注
    LIVE_CANDIDATE、非 O1 免责、不宣称收口。"""
    src = PE_PAGE.read_text(encoding="utf-8")
    code = re.sub(r"//[^\n]*", "", src)
    code = re.sub(r"/\*.*?\*/", "", code, flags=re.DOTALL)
    assert "public_extract_nbs_live_candidate.json" in code
    assert "LIVE_CANDIDATE" in code
    assert "source_deeplink_url" in code
    assert "非 O1 收口" in code, "live candidate 区块须显式非 O1 免责"
    assert "O1_AUTO_INTAKED" not in code
