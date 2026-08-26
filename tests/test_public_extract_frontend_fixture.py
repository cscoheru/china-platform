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

# Knife 61 / tasking 376 — 湖北 PROVINCIAL_BULLETIN xlsx 提取 fixture
HB_FIXTURE = PROJECT_ROOT / "frontend" / "lib" / "public_extract_hubei.json"
HB_EXTRACT = (
    PROJECT_ROOT
    / "data"
    / "public_extracts"
    / "tjj.hubei.gov.cn"
    / "PROVINCIAL_BULLETIN.json"
)
HB_REGISTRY_SHA_PREFIX = "c5cf5abeb4fdf97a"


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


# ---------------------------------------------------------------------------
# 深圳 REGISTRY_SAMPLE 前端分节 (tasking 370 / knife 59)
# ---------------------------------------------------------------------------

SZ_FIXTURE = PROJECT_ROOT / "frontend" / "lib" / "public_extract_sz.json"
SZ_EXTRACT = (
    PROJECT_ROOT / "data" / "public_extracts" / "sz.gov.cn" / "MUNICIPAL_BULLETIN.json"
)


def test_sz_fixture_mirrors_extract_and_shape() -> None:
    """Per 370 §SCHEMA (1): fixture 快照自深圳 MUNICIPAL extract — dict 全等
    + 形状锚定 (71 行 / section+paragraph / registry SHA d5e2c731…)。"""
    sz = json.loads(SZ_FIXTURE.read_text(encoding="utf-8"))
    data_rec = json.loads(SZ_EXTRACT.read_text(encoding="utf-8"))
    assert sz == data_rec, "fixture 必须与 data 侧提取快照一致"
    assert sz["domain"] == "sz.gov.cn"
    assert sz["category"] == "MUNICIPAL_BULLETIN"
    assert sz["row_count"] == len(sz["rows"]) == 71
    assert set(sz["rows"][0].keys()) == {"section", "paragraph"}
    assert sz["source_sha256"].startswith("d5e2c73196b43cec")
    assert sz["source_sample_path"] == "spikes/03-municipal-bulletin/sample.html"


def test_sz_track_isolated_from_nbs() -> None:
    """Per 370 §红线: 不覆盖 NBS 双轨 — NBS sample 63 行/dea13b8a 锚与
    LIVE_CANDIDATE 锚原样,深圳 SHA/行数独立。"""
    nbs = json.loads(FIXTURE.read_text(encoding="utf-8"))
    live = json.loads(LIVE_EXTRACT.read_text(encoding="utf-8"))
    sz = json.loads(SZ_FIXTURE.read_text(encoding="utf-8"))
    assert nbs["row_count"] == 63
    assert nbs["source_sha256"] == (
        "dea13b8a4ff116ca91403b189cdd60705545b28200f9023c3d56e6db03f3939d"
    )
    assert live["intake_status"] == "LIVE_CANDIDATE"
    assert sz["source_sha256"] not in (nbs["source_sha256"], live["source_sha256"])
    assert sz["row_count"] != nbs["row_count"]


def test_page_renders_sz_registry_sample_track() -> None:
    """Per 370 §SCHEMA (2): /public-extracts 页 import SZ fixture、深圳
    分节标注 MUNICIPAL_BULLETIN、散文抽取说明、非 live 免责 (SSL 暂缓)。"""
    src = PE_PAGE.read_text(encoding="utf-8")
    code = re.sub(r"//[^\n]*", "", src)
    code = re.sub(r"/\*.*?\*/", "", code, flags=re.DOTALL)
    assert "public_extract_sz.json" in code, "page must import the SZ fixture"
    assert "MUNICIPAL_BULLETIN" in code
    assert "散文段落表" in code, "深圳散文分节区块须在"
    assert "SSL 暂缓" in code, "深圳分节须显式非 live 免责 (SSL 暂缓)"
    assert "O1_AUTO_INTAKED" not in code


# ---------------------------------------------------------------------------
# Knife 61 / tasking 376 — 湖北 PROVINCIAL_BULLETIN xlsx 第四分节
# ---------------------------------------------------------------------------


def test_hb_fixture_mirrors_extract_and_shape() -> None:
    """Per 376 §SCHEMA (2): 湖北 fixture 是 extract JSON 的 byte-verbatim
    快照; row_count==len(rows)≥1; source_sha256 与 registry 锚吻合
    (c5cf5abeb4fdf97a…); domain/category 锁死 tjj.hubei.gov.cn /
    PROVINCIAL_BULLETIN。"""
    assert HB_FIXTURE.is_file(), f"missing fixture: {HB_FIXTURE}"
    assert HB_EXTRACT.is_file(), f"missing extract: {HB_EXTRACT}"
    fx = json.loads(HB_FIXTURE.read_text(encoding="utf-8"))
    ex = json.loads(HB_EXTRACT.read_text(encoding="utf-8"))
    # byte-verbatim 快照
    assert fx == ex, "HB fixture must be byte-verbatim snapshot of extract"
    # 形状锚
    assert fx["domain"] == "tjj.hubei.gov.cn"
    assert fx["category"] == "PROVINCIAL_BULLETIN"
    rc = fx["row_count"]
    rows = fx["rows"]
    assert isinstance(rows, list) and len(rows) >= 1
    assert rc == len(rows)
    assert rc == 21, f"任务书 376 期望 ≈21 行; 实际 {rc}"
    # registry 锚
    assert fx["source_sha256"].startswith(HB_REGISTRY_SHA_PREFIX), (
        f"HB source_sha256 必须以 registry 锚 {HB_REGISTRY_SHA_PREFIX} 开头; "
        f"实际 {fx['source_sha256'][:16]}"
    )
    # WORM 尾段
    assert fx["source_archive_path"].startswith("data/public_archives/")


def test_hb_track_isolated_from_nbs_and_sz() -> None:
    """Per 376 §SCHEMA (3): 不覆盖 NBS+SZ 三轨既有 fixture; HB 行数与 sha
    均与三轨不同。"""
    nbs = json.loads(FIXTURE.read_text(encoding="utf-8"))
    sz_fix = PROJECT_ROOT / "frontend" / "lib" / "public_extract_sz.json"
    assert sz_fix.is_file(), "missing SZ fixture (regression?)"
    sz = json.loads(sz_fix.read_text(encoding="utf-8"))
    live_fix = (
        PROJECT_ROOT / "frontend" / "lib" / "public_extract_nbs_live_candidate.json"
    )
    assert live_fix.is_file(), "missing NBS live candidate fixture (regression?)"
    live = json.loads(live_fix.read_text(encoding="utf-8"))
    hb = json.loads(HB_FIXTURE.read_text(encoding="utf-8"))
    # 三轨锚不回归
    assert nbs["row_count"] == 63
    assert nbs["source_sha256"] == (
        "dea13b8a4ff116ca91403b189cdd60705545b28200f9023c3d56e6db03f3939d"
    )
    assert live["intake_status"] == "LIVE_CANDIDATE"
    assert live["source_sha256"].startswith("0b85212f")
    assert sz["source_sha256"].startswith("d5e2c731")
    assert hb["source_sha256"].startswith(HB_REGISTRY_SHA_PREFIX)
    # HB 与三轨互不覆盖
    for other in (nbs, live, sz):
        assert hb["source_sha256"] != other["source_sha256"]
        assert hb["row_count"] != other["row_count"]
    # HB 不冒充 live (live 仍 enabled=FALSE)
    assert "LIVE_CANDIDATE" not in (hb.get("intake_status") or "")
    assert "LIVE" not in (hb.get("intake_status") or "").upper().split("INTAKED")[0]


def test_page_renders_hb_registry_sample_track() -> None:
    """Per 376 §SCHEMA (2): /public-extracts 页 import HB fixture、第四分节
    标注 PROVINCIAL_BULLETIN、xlsx 月报说明、live FALSE 暂缓非 O1。"""
    src = PE_PAGE.read_text(encoding="utf-8")
    code = re.sub(r"//[^\n]*", "", src)
    code = re.sub(r"/\*.*?\*/", "", code, flags=re.DOTALL)
    assert "public_extract_hubei.json" in code, "page must import the HB fixture"
    assert "PROVINCIAL_BULLETIN" in code
    assert "月报统计表" in code, "湖北月报分节区块须在"
    assert "enabled=FALSE" in code, "湖北分节须显式 live FALSE 暂缓"
    assert "O1_AUTO_INTAKED" not in code


def test_page_renders_overview_strip_four_tracks() -> None:
    """Per tasking 382 §SCHEMA (1): /public-extracts 页首增四轨一览条
    overview strip (一表或一行摘要); CSS class + 标题 + 4 行 (sample/live/sz/hb)
    + 锚链到 4 分节 + 守门非 O1/Gate PASS。"""
    src = PE_PAGE.read_text(encoding="utf-8")
    code = re.sub(r"//[^\n]*", "", src)
    code = re.sub(r"/\*.*?\*/", "", code, flags=re.DOTALL)
    assert "public-extracts-page__overview-strip" in code, (
        "overview strip section 须在位 (per 382 §SCHEMA-1)"
    )
    assert "四轨一览 (overview)" in code, "overview strip 标题须在位"
    # 4 分节锚点: 锚 id 命名
    for anchor in ("track-nbs-sample", "track-nbs-live", "track-sz", "track-hb"):
        assert f'id="{anchor}"' in code, f"分节须含 id={anchor}"
    # 4 锚链 (href)
    for href in ("#track-nbs-sample", "#track-nbs-live", "#track-sz", "#track-hb"):
        assert href in code, f"overview strip 须链到 {href}"
    # 守门: 不宣称 O1/Gate PASS
    assert "四轨皆 demo/candidate" in code, "overview strip 须标 demo/candidate 非 O1"
    assert "O1_AUTO_INTAKED" not in code


def test_overview_strip_reads_only_from_existing_fixtures() -> None:
    """Per tasking 382 §SCHEMA (2): overview strip 数据只读自既有 4 fixture,
    不重算 (不允许出现动态构造行数或 SHA 的代码)。"""
    src = PE_PAGE.read_text(encoding="utf-8")
    code = re.sub(r"//[^\n]*", "", src)
    code = re.sub(r"/\*.*?\*/", "", code, flags=re.DOTALL)
    # overview strip 区域须直接读 extract / live / sz / hb 4 const 的字段,
    # 不得出现 sha256 重算或 row_count 重算.
    overview_marker = "public-extracts-page__overview-strip"
    assert overview_marker in code, "overview strip 须在位"
    # 4 fixture 字段都在 strip 区域引用
    for fixture_field in (
        "extract.domain",
        "extract.row_count",
        "extract.source_sha256",
        "live.row_count",
        "sz.row_count",
        "hb.row_count",
    ):
        assert fixture_field in code, (
            f"overview strip 须读 {fixture_field} (per 382 §SCHEMA-2 不重算)"
        )
    # 不允许在 strip 中调用 sha256() 函数或 hashlib (重算)
    # 允许读取 fixture 字段 (.source_sha256, 引用而非计算)
    strip_start = code.find(overview_marker)
    strip_end = code.find("</section>", strip_start)
    assert strip_start > 0 and strip_end > strip_start, "overview strip 须有 </section>"
    strip_slice = code[strip_start:strip_end]
    # 移走 fixture 字段引用 .source_sha256 / source_sha256: (引用, 非计算)
    strip_no_field_ref = strip_slice.replace("source_sha256", "SHA_REF")
    # 现应仅剩 sha256( / hashlib 等计算用法
    sha_compute_re = re.compile(r"\bsha256\s*\(|hashlib", re.IGNORECASE)
    assert not sha_compute_re.search(strip_no_field_ref), (
        "overview strip 不得调用 sha256(...)/hashlib (per 382 §SCHEMA-2 不重算)"
    )
