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
