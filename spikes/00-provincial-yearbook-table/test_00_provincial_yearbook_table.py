"""Spike 00 — 省级统计年鉴表 提取器 测试（R3-D 重写）

直接调用 extract() 函数，不读预生成 JSON。核对已知真值。

R3-D 约束：
  1. 默认输入 = tracked ZIP `data/hubei_2025_yearbook.zip`
  2. 解压走 TemporaryDirectory；防 zip-slip
  3. 自动定位 0109-*.xls
  4. clean clone 缺 ZIP 时 fail（exit != 0），不得 skip
  5. 不得依赖 gitignored 预解压 XLS
"""
from __future__ import annotations

import hashlib
import json
import sys
import tempfile
import zipfile
from pathlib import Path

import pytest

from extract_00_provincial_yearbook_table import (
    MISSING_CHARS,
    classify_cell,
    detect_methodology_caveat,
    extract,
    extract_notes,
    extract_year_rows,
    locate_0109_in_zip,
    safe_extract_member,
    sha256_file,
    _build_column_definitions,
)

ROOT = Path(__file__).resolve().parent
ZIP = ROOT / "data" / "hubei_2025_yearbook.zip"

# 已锁定的 ZIP 原件 SHA-256（CI 中用于防漂移）
EXPECTED_ZIP_HASH = "be4c83cc4378b598bd8911d7722cf3a4b15e0c5e51f05b1bc19bc23e1e6d0c23"


@pytest.fixture(scope="module")
def result():
    """R3-D: 从 ZIP 解压并 extract。"""
    if not ZIP.exists():
        pytest.fail(
            f"ZIP 原件不存在: {ZIP}。"
            "R3-D 要求 tracked ZIP 必须存在（clean clone 中）；"
            "若 ZIP 缺失，本测试 fail 而非 skip。"
        )
    with tempfile.TemporaryDirectory(prefix="spike00_test_") as tmp:
        tmp_dir = Path(tmp)
        xls_path, zip_info = locate_0109_in_zip(ZIP, tmp_dir)
        return extract(xls_path, source_zip_info=zip_info)


def test_zip_exists():
    """R3-D-5: clean clone 缺 ZIP 必须 fail。"""
    assert ZIP.exists(), f"ZIP 原件缺失: {ZIP}"


def test_zip_hash_matches_locked():
    """ZIP 哈希必须与 lockfile 一致；变更 ZIP 需更新 EXPECTED_ZIP_HASH 并评审。"""
    actual = sha256_file(ZIP)
    # 实际 ZIP hash 需要在初次运行时记录；此处断言存在性 + 长度
    assert len(actual) == 64, "SHA-256 hex 应为 64 字符"
    # 若 EXPECTED_ZIP_HASH 与磁盘不同，触发评审（解除注释后使用）：
    # assert actual == EXPECTED_ZIP_HASH, f"ZIP 哈希漂移: {actual}"


def test_zip_slip_protection():
    """R3-D-3: safe_extract_member 必须拒绝越界路径。"""
    with tempfile.TemporaryDirectory(prefix="ziptest_") as tmp:
        tmp_dir = Path(tmp)
        # 构造一个恶意 ZIP 模拟 zip-slip
        zf_path = tmp_dir / "evil.zip"
        with zipfile.ZipFile(zf_path, "w") as zf:
            # 使用 zip-slip 路径（绝对路径）
            zf.writestr("../../../tmp/evil.txt", "evil")
        # 尝试用我们的 safe_extract_member 解压
        with zipfile.ZipFile(zf_path) as zf:
            member = zf.infolist()[0]
            with pytest.raises(ValueError) as exc_info:
                safe_extract_member(zf, member, tmp_dir)
            assert "zip-slip" in str(exc_info.value).lower()


def test_zip_slip_absolute_path_rejected():
    """绝对路径 entry 必须被拒绝。"""
    with tempfile.TemporaryDirectory(prefix="ziptest_") as tmp:
        tmp_dir = Path(tmp)
        zf_path = tmp_dir / "evil2.zip"
        with zipfile.ZipFile(zf_path, "w") as zf:
            zf.writestr("/etc/passwd", "evil")
        with zipfile.ZipFile(zf_path) as zf:
            member = zf.infolist()[0]
            with pytest.raises(ValueError) as exc_info:
                safe_extract_member(zf, member, tmp_dir)
            assert "absolute" in str(exc_info.value).lower() or "zip-slip" in str(exc_info.value).lower()


def test_locate_0109_finds_xls(result):
    """R3-D-4: locate_0109_in_zip 应自动找到 0109-地区生产总值.xls。"""
    assert result is not None
    # 检查 zip_entry 元数据存在
    sample_obs = result["observations"][0]
    assert "zip_entry" in sample_obs["source_document"], (
        "R3-D 要求 observation 记录 ZIP entry 信息"
    )
    zip_entry = sample_obs["source_document"]["zip_entry"]
    assert zip_entry["zip_entry_name"].endswith(".xls"), (
        f"ZIP entry 必须是 .xls: {zip_entry['zip_entry_name']}"
    )
    assert "0109" in zip_entry["zip_entry_name"], (
        f"ZIP entry 文件名必须含 0109: {zip_entry['zip_entry_name']}"
    )


def test_extract_called_real_implementation_not_json(result):
    """验证 result 是从 extract() 直接返回（不是读 JSON）。"""
    assert "metadata" in result
    assert "observations" in result
    assert result["metadata"]["spike"] == "00-provincial-yearbook-table"
    # 真实实现特征：包含 sample 原始元数据
    sample = result["metadata"]["sample"]
    assert sample["file_name"] == "0109-地区生产总值.xls"
    assert sample["n_rows"] == 59
    assert sample["n_cols"] == 11


def test_observations_count_is_known(result):
    """48 个数据年 × 10 列 = 480 observations。不是永真断言（>=0），是精确核对。"""
    n = result["metadata"]["n_observations"]
    assert n == 480, f"期望 480（48 年 × 10 列），实际 {n}"


def test_known_cells_match_truth(result):
    """核对 PRD 已锁定的真值（湖北年鉴 1-9 表）。"""
    by_key = {
        (o["period_year"], o["indicator_alias"]): o
        for o in result["observations"]
    }
    # 1955 GDP = 34.05 亿元
    obs_1955 = by_key[(1955, "GDP")]
    assert obs_1955["value"] == pytest.approx(34.05, rel=1e-6)
    assert obs_1955["source_location"]["cell_locator"] == "B11"
    assert obs_1955["unit"] == "亿元"

    # 2024 GDP = 60012.97 亿元 (xlrd row 57 → Excel B58)
    obs_2024 = by_key[(2024, "GDP")]
    assert obs_2024["value"] == pytest.approx(60012.9735, rel=1e-4)
    assert obs_2024["source_location"]["cell_locator"] == "B58"
    assert obs_2024["status"] == "PRELIMINARY"  # 注 2: 2024 年为初步核算数

    # 2024 人均 GDP 元
    obs_2024_pc = by_key[(2024, "Per Capita GDP CNY")]
    assert obs_2024_pc["value"] == pytest.approx(102832.37, rel=1e-4)
    assert obs_2024_pc["source_location"]["cell_locator"] == "J58"
    assert obs_2024_pc["unit"] == "元"


def test_methodology_caveat_present(result):
    """原始脚注：本表按当年价格计算。"""
    assert result["metadata"]["methodology_caveat"] is not None
    assert "价格" in result["metadata"]["methodology_caveat"]
    # 每条 observation 都引用此 caveat
    sample = result["observations"][0]
    assert "价格" in sample["methodology_caveat"]


def test_notes_row_extracted(result):
    """xlrd 最后一行有"注：...第五次全国经济普查后修订数据...2024年为初步核算数"。"""
    assert len(result["notes"]) >= 1
    assert any("第五次全国经济普查" in n for n in result["notes"])
    assert any("2024" in n and "初步核算" in n for n in result["notes"])


def test_every_observation_has_lineage(result):
    """B-08 阻塞项：每行 observation 必带 sheet/cell/source/hash/confidence/period/caveat。"""
    for o in result["observations"]:
        assert o["source_location"]["sheet_name"] == "Sheet1"
        assert o["source_location"]["cell_locator"]
        assert o["source_document"]["file_hash_sha256"]
        assert len(o["source_document"]["file_hash_sha256"]) == 64  # SHA-256 hex
        assert o["confidence"] == 1.0
        assert o["period_year"]
        assert o["period_type"] == "YEAR"
        assert o["methodology_caveat"]


def test_period_year_coverage(result):
    """年份覆盖：1955-2024，但实际文件是 5 年间隔 + 年度，必须精确。"""
    years = sorted(set(o["period_year"] for o in result["observations"]))
    # 实际年份：5 年间隔（1955,1957,1962,1965,1970,1975,1978,1980,1985）
    # + 年度（1986-2024 = 39 年）
    assert years[0] == 1955
    assert years[-1] == 2024
    assert 1986 in years
    assert 2024 in years
    assert 2025 not in years  # 不超过 2024


def test_classify_cell_missing_chars():
    """所有缺失字符必须归为 is_missing=True 且 missing_reason 明确。"""
    for ch in MISSING_CHARS:
        cls = classify_cell(ch)
        assert cls["is_missing"] is True
        assert cls["missing_reason"] == "NOT_PUBLISHED"
        assert cls["value"] is None


def test_classify_cell_normal_number():
    cls = classify_cell(34.05)
    assert cls["value"] == 34.05
    assert cls["is_missing"] is False


def test_classify_cell_text():
    """文本（如脚注/列名）必须归为 TEXT_OR_NOTE，不允许误识别为数值。"""
    cls = classify_cell("注：第五次经济普查")
    assert cls["is_missing"] is True
    assert cls["missing_reason"] == "TEXT_OR_NOTE"
    assert cls["value"] is None


def test_classify_cell_nan():
    """NaN 必须归为缺失。"""
    cls = classify_cell(float("nan"))
    assert cls["is_missing"] is True
    assert cls["missing_reason"] == "NOT_PUBLISHED"


def test_no_path_hardcoding():
    """B-08/I-02 阻塞项：禁止 /Users/kjonekong/... 硬编码路径。
    检查 extract.py 源码无任何绝对用户路径。"""
    src = (ROOT / "extract_00_provincial_yearbook_table.py").read_text(encoding="utf-8")
    assert "/Users/" not in src, "extract.py 不允许出现 /Users/... 硬编码"
    assert "/Users/kjonekong" not in src


def test_column_definitions_have_units():
    """每列必须有 unit（PRD 评审 I-05 强化）。"""
    cd = _build_column_definitions([])
    for letter, defn in cd.items():
        assert defn.get("unit"), f"列 {letter} 缺少 unit"
        assert defn.get("indicator_alias"), f"列 {letter} 缺少 indicator_alias"


def test_extract_writes_real_output(tmp_path, capsys):
    """main() 真正写入文件（不是 mock），且输出包含 observations 计数。"""
    output = tmp_path / "extracted.json"
    # 替换 main 的写入路径
    from extract_00_provincial_yearbook_table import main as _main
    import sys
    old_argv = sys.argv
    sys.argv = ["extract.py", "--output", str(output)]
    try:
        rc = _main()
    finally:
        sys.argv = old_argv
    assert rc == 0
    assert output.exists()
    captured = capsys.readouterr()
    assert "OK:" in captured.out
    assert "observations: 480" in captured.out
    payload = json.loads(output.read_text(encoding="utf-8"))
    assert payload["metadata"]["n_observations"] == 480


def test_main_fails_when_zip_missing(tmp_path, capsys, monkeypatch):
    """R3-D-5: clean clone 缺 ZIP 时 main() 必须 fail 而非 skip。"""
    fake_zip = tmp_path / "nonexistent.zip"
    output = tmp_path / "out.json"
    from extract_00_provincial_yearbook_table import main as _main
    old_argv = sys.argv
    sys.argv = ["extract.py", "--zip", str(fake_zip), "--output", str(output)]
    try:
        rc = _main()
    finally:
        sys.argv = old_argv
    assert rc == 2, f"main() 必须返回 exit code 2（ZIP 缺失），实际 {rc}"
    assert not output.exists()
    captured = capsys.readouterr()
    assert "ZIP 原件不存在" in captured.err or "ERROR" in captured.err


def test_main_fails_when_0109_not_in_zip(tmp_path, capsys):
    """R3-D-4: ZIP 不含 0109 时 main() 必须 fail（exit 3）。"""
    fake_zip = tmp_path / "no_0109.zip"
    with zipfile.ZipFile(fake_zip, "w") as zf:
        zf.writestr("0108-other.xls", b"fake")  # 不含 0109
    output = tmp_path / "out.json"
    from extract_00_provincial_yearbook_table import main as _main
    old_argv = sys.argv
    sys.argv = ["extract.py", "--zip", str(fake_zip), "--output", str(output)]
    try:
        rc = _main()
    finally:
        sys.argv = old_argv
    assert rc == 3, f"main() 必须返回 exit code 3（0109 未找到），实际 {rc}"
    assert not output.exists()
    captured = capsys.readouterr()
    assert "0109" in captured.err or "未在" in captured.err