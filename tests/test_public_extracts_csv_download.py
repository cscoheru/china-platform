# Knife 70 (tasking 403) — /public-extracts 四轨 CSV 静态下载 测试.
#
# Per 403 §SCHEMA:
#   (1) 由既有 4 fixture 确定性生成 CSV (列序=首行键序, 不重命名) →
#       frontend/public/public-extracts/{nbs,nbs-live-candidate,sz,hubei}.csv
#   (2) overview 表「下载 JSON / CSV」列同格第二链 (JSON 链不破坏)
#   (3) ≥2 pytest (CSV 行数=fixture 行数; 表头一致) + smoke §12i 针
#
# 红线 (per 403 §红线): CSV 必须与 fixture 行数一致; 不改 fixture JSON
# 字节; 无服务端动态导出 (静态文件); 不谎称 CSV=权威库.
from __future__ import annotations

import csv
import importlib.util
import json
import re
from pathlib import Path

import pytest

PROJECT_ROOT = Path(__file__).resolve().parent.parent
PUBLIC_DIR = PROJECT_ROOT / "frontend" / "public" / "public-extracts"
PE_PAGE = PROJECT_ROOT / "frontend" / "app" / "public-extracts" / "page.tsx"
GEN_SCRIPT = PROJECT_ROOT / "scripts" / "gen_public_extracts_csv.py"

# name -> lib fixture path (与 knife 65 public JSON / knife 70 CSV 命名一致)
CSV_FIXTURES = {
    "nbs": PROJECT_ROOT / "frontend" / "lib" / "public_extract_nbs.json",
    "nbs-live-candidate": PROJECT_ROOT
    / "frontend"
    / "lib"
    / "public_extract_nbs_live_candidate.json",
    "sz": PROJECT_ROOT / "frontend" / "lib" / "public_extract_sz.json",
    "hubei": PROJECT_ROOT / "frontend" / "lib" / "public_extract_hubei.json",
}


@pytest.fixture(scope="module")
def gen_module():
    """Import scripts/gen_public_extracts_csv.py as a module (determinism check)."""
    assert GEN_SCRIPT.is_file(), f"missing generator: {GEN_SCRIPT}"
    spec = importlib.util.spec_from_file_location("gen_public_extracts_csv", GEN_SCRIPT)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def _strip_comments(src: str) -> str:
    code = re.sub(r"//[^\n]*", "", src)
    code = re.sub(r"/\*.*?\*/", "", code, flags=re.DOTALL)
    return code


@pytest.mark.parametrize(
    "name,fixture_path", list(CSV_FIXTURES.items()), ids=list(CSV_FIXTURES.keys())
)
def test_csv_header_matches_fixture_first_row_keys(
    name: str, fixture_path: Path
) -> None:
    """Per 403 §SCHEMA-1: CSV 表头 == fixture 首行键序 (不重命名/不重排;
    湖北未命名空列键原样保留)."""
    csv_path = PUBLIC_DIR / f"{name}.csv"
    assert csv_path.is_file(), f"missing CSV: {csv_path}"
    fixture = json.loads(fixture_path.read_text(encoding="utf-8"))
    rows = fixture["rows"]
    with csv_path.open(encoding="utf-8", newline="") as f:
        reader = csv.reader(f)
        header = next(reader)
    assert header == list(rows[0].keys()), (
        f"{name}.csv 表头须 == fixture 首行键序 (不重命名): "
        f"csv={header} vs fixture={list(rows[0].keys())}"
    )


@pytest.mark.parametrize(
    "name,fixture_path", list(CSV_FIXTURES.items()), ids=list(CSV_FIXTURES.keys())
)
def test_csv_row_count_and_field_count_match_fixture(
    name: str, fixture_path: Path
) -> None:
    """Per 403 §红线: CSV 数据行数 == fixture row_count (== len(rows));
    每行字段数 == 表头字段数 (一一对应)."""
    csv_path = PUBLIC_DIR / f"{name}.csv"
    fixture = json.loads(fixture_path.read_text(encoding="utf-8"))
    with csv_path.open(encoding="utf-8", newline="") as f:
        records = list(csv.reader(f))
    header, data = records[0], records[1:]
    assert len(data) == len(fixture["rows"]) == fixture["row_count"], (
        f"{name}.csv 数据行数 ({len(data)}) 须 == fixture row_count "
        f"({fixture['row_count']}) (per 403 §红线 行数一致)"
    )
    for i, rec in enumerate(data):
        assert len(rec) == len(header), (
            f"{name}.csv 第 {i + 2} 行字段数 ({len(rec)}) != 表头 ({len(header)})"
        )


@pytest.mark.parametrize(
    "name,fixture_path", list(CSV_FIXTURES.items()), ids=list(CSV_FIXTURES.keys())
)
def test_csv_bytes_match_deterministic_regeneration(
    name: str, fixture_path: Path, gen_module
) -> None:
    """Per 403 §SCHEMA-1: committed CSV 与生成器重渲字节一致 — 确定性
    (重跑同字节) + 可再生 (产物源自 fixture, 非手编辑)."""
    csv_path = PUBLIC_DIR / f"{name}.csv"
    fixture = json.loads(fixture_path.read_text(encoding="utf-8"))
    regenerated = gen_module.render_csv_bytes(fixture)
    committed = csv_path.read_bytes()
    assert committed == regenerated, (
        f"{name}.csv 与确定性重渲不一致 — 产物须由 gen_public_extracts_csv.py "
        f"从 fixture 生成 (禁止手编辑偏离)"
    )


def test_page_links_csv_and_keeps_json_downloads() -> None:
    """Per 403 §SCHEMA-2 + §禁止: overview「下载 JSON / CSV」列含 4 CSV 链
    (href + download attr); JSON 4 链原样不破坏; 页面无服务端动态导出
    (CSV 为静态 public 文件, 页面无 csv 生成代码); 非权威库守门在位."""
    src = PE_PAGE.read_text(encoding="utf-8")
    code = _strip_comments(src)
    assert "下载 JSON / CSV" in code, "overview 表须含「下载 JSON / CSV」列头"
    for name in CSV_FIXTURES:
        href = f'href="/public-extracts/{name}.csv"'
        dl = f'download="public-extracts-{name}.csv"'
        assert href in code, f"页面须含 CSV 下载链 {href}"
        assert dl in code, f"页面 CSV download attr 须含 {dl}"
        json_href = f'href="/public-extracts/{name}.json"'
        assert json_href in code, (
            f"JSON 下载链不得被 CSV 链破坏: {json_href} (per 403 §禁止)"
        )
    # 非权威库守门 (不谎称 CSV=权威库)
    assert "JSON / CSV 下载皆为 fixture 快照确定性导出" in code
    assert "非权威库" in code
    # 无服务端动态导出: 页面不得出现 CSV 生成/拼接逻辑 (静态文件消费)
    assert "text/csv" not in code, "页面不得有服务端 CSV 动态导出 (per 403 §SCHEMA)"
    assert "application/csv" not in code
    assert "O1_AUTO_INTAKED" not in code
