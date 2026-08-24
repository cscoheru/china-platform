"""
Spike 00 — 国家统计年鉴表 提取器 测试（重写 per 返工指令 §三 + R3-C）

测试覆盖：
  B-03: 完整 22 列 multi-level schema，无 "其他指标" fallback
  B-04: missing_reason 永不为 None（needs_review=True 时有具体根因）
  B-05: per-column 已知 NBS 真值核对（不允许全表都查同一个指标）
  B-06: per-column 准确率报告（sample_count, matched_count, accuracy）
  B-08: bbox / confidence / source hash / page locator 完整
  I-02: 禁止硬编码 /Users 路径
  R3-C: 31×22=682 槽位完整网格 + 缺格显式建模（value=None + 具体 reason）
        + 列边界映射（right-edge k-means）在中间缺格时不左移后续列
        + 每列硬门槛（PER_COLUMN_MIN_ACCURACY 全部 1.0）
"""
from __future__ import annotations

import hashlib
import json
import subprocess
import sys
from pathlib import Path

import pytest

from extract_00_national_yearbook_table import (
    COLUMN_REFERENCE,
    COLUMN_SCHEMA,
    EXPECTED_NUMERIC_COLS,
    KNOWN_PROVINCES,
    OCR_TOLERANCE,
    PER_COLUMN_MIN_ACCURACY,
    _row_to_column_slots,
    assign_column_provenance,
    assign_right_edge_to_column,
    build_column_boundaries,
    detect_province,
    extract,
    extract_numeric_token,
    group_into_rows,
    ocr_text,
    require_tesseract,
    sha256_file,
)

ROOT = Path(__file__).resolve().parent
SAMPLE = ROOT / "data" / "c0309.jpg"
EXPECTED_HASH = "9576529a881b83beac4718594f3a26d2e1949947a65c7e375b4a5f1c6a69688e"


def _tess_ok() -> bool:
    try:
        require_tesseract(); return True
    except RuntimeError:
        return False


@pytest.fixture(scope="module")
def result():
    if not SAMPLE.exists():
        pytest.fail(f"必需样本缺失: {SAMPLE}（R4-1：不得 skip-as-PASS）")
    if not _tess_ok():
        pytest.fail("tesseract/chi_sim 不可用（R4-1：不得 skip-as-PASS）")
    return extract(SAMPLE)


# ---------------------------------------------------------- 基础存在性

def test_sample_exists():
    assert SAMPLE.exists(), f"样本缺失: {SAMPLE}"


def test_sample_hash_matches_locked():
    """B-08: 输入文件 SHA-256 必须与样本登记一致。"""
    assert sha256_file(SAMPLE) == EXPECTED_HASH


def test_tesseract_chinese_available():
    bin_path, lang = require_tesseract()
    assert bin_path and lang == "chi_sim"


# ---------------------------------------------------------- B-03 完整 schema

def test_column_schema_has_full_22_numeric_columns():
    """三-1: 22 列 multi-level 完整定义；不存在 fallback 兜底。"""
    numeric_cols = [c for c in COLUMN_SCHEMA if not c.get("is_label")]
    assert len(numeric_cols) == 22, f"numeric 列数异常: {len(numeric_cols)}"
    for c in numeric_cols:
        assert c["indicator"], f"列 {c['key']} 缺少 indicator"
        assert c["unit"] in {"亿元", "元", "%"}, f"列 {c['key']} 单位异常: {c['unit']}"
    keys = [c["key"] for c in numeric_cols]
    expected_prefixes = {
        "gdp_total", "ind_", "brk_", "per_capita",
        "share_", "growth_",
    }
    matched = sum(1 for k in keys
                  if any(k.startswith(p) for p in expected_prefixes))
    assert matched == 22


def test_no_other_indicator_fallback():
    """三-3: 严禁 "其他指标/col_N/亿元" fallback。"""
    for c in COLUMN_SCHEMA:
        assert "其他指标" not in c["indicator"], f"fallback 仍存在: {c}"
    # 验证 assign_column_provenance 在越界时抛错（不再静默兜底）
    with pytest.raises(ValueError):
        assign_column_provenance(EXPECTED_NUMERIC_COLS + 5)


def test_schema_groups_complete():
    """三-1: 每个数据列 group_l1/group_l2/leaf 三层元数据齐全。"""
    for c in COLUMN_SCHEMA:
        if c.get("is_label"):
            continue
        # 列名指示器至少在 group_l2 或 leaf 之一有内容（per_capita 这种
        # 三级结构单子节点是合法的）
        assert c["leaf"], f"列 {c['key']} 缺 leaf"


# ---------------------------------------------------------- B-04 missing_reason

def test_missing_reason_never_none_when_flagged(result):
    """三-4: needs_review=True 时 missing_reason 字段必须给出具体原因。
    之前缺 missing_reason=None 时被静默放过 — 现在任何被标 needs_review
    的 observation 必带原因字符串。"""
    bad = [
        o for o in result["observations"]
        if o["needs_review"] and not o["needs_review_reasons"]
    ]
    assert not bad, f"{len(bad)} 个 needs_review=True 的 obs 缺原因"


def test_needs_review_triggers_consistent(result):
    """三-4: needs_review 触发条件互斥且完整（R3-C 扩展 reason 集）。"""
    allowed = {
        "row_cell_count_mismatch",
        "low_ocr_confidence",
        "not_published",
        "empty_ocr",
        "ocr_unreadable",
        # R3-C：缺格显式建模的缺格原因（行/列级）+ 边界映射折叠信号
        "cell_not_detected",
        "row_not_detected",
        "duplicate_column_tokens",
    }
    for o in result["observations"]:
        for r in o["needs_review_reasons"]:
            assert r in allowed, f"非允许 reason: {r} ({o['geo_canonical']}/{o['column_key']})"


# ---------------------------------------------------------- B-05 per-column 真值

def test_per_column_truth_keys_present():
    """三-5: 每个有真值的列必须出现在 COLUMN_REFERENCE 中。"""
    keys = {c["key"] for c in COLUMN_SCHEMA if not c.get("is_label")}
    for col_key in COLUMN_REFERENCE:
        assert col_key in keys, f"COLUMN_REFERENCE 含未知列 {col_key}"


def test_per_column_hard_gate_met(result):
    """三-5 + R3-C：每列硬门槛（PER_COLUMN_MIN_ACCURACY 全部 1.0）。

    官方公布、且 OCR 损伤低的高信噪比参考样本，每个都必须在 OCR_TOLERANCE 内
    命中（硬门槛 = 全部命中，允许零遗漏）。若参考被污染、或出现系统性列错位，
    门槛即被打破。"""
    by_colprov: dict[tuple[str, str], dict] = {}
    for o in result["observations"]:
        by_colprov[(o["column_key"], o["geo_canonical"])] = o

    fails: list[str] = []
    for col_key, prov_truth in COLUMN_REFERENCE.items():
        tol = OCR_TOLERANCE[col_key]
        n_ref = len(prov_truth)
        matched = 0
        for prov, expected_value in prov_truth.items():
            obs = by_colprov.get((col_key, prov))
            if obs is None or obs["value"] is None:
                continue
            if abs(obs["value"] - expected_value) <= tol:
                matched += 1
        accuracy = matched / n_ref if n_ref else 1.0
        min_acc = PER_COLUMN_MIN_ACCURACY[col_key]
        if accuracy < min_acc:
            fails.append(
                f"{col_key}: acc={accuracy:.2f} ({matched}/{n_ref}) "
                f"need>={min_acc} (tol={tol})"
            )
    assert not fails, "硬门槛未达标:\n  " + "\n  ".join(fails)
    # 参考样本总数下限（确保不是全表都查同一个指标）
    total_ref = sum(len(v) for v in COLUMN_REFERENCE.values())
    assert total_ref >= 30, f"per-column 真值样本数过少: {total_ref}"


# ---------------------------------------------------------- B-06 per-column 准确率

def test_per_column_accuracy_report_writable(result, tmp_path):
    """三-6: 评估器必须能产出 per-column 准确率报告。"""
    by_col: dict[str, list[dict]] = {}
    for o in result["observations"]:
        by_col.setdefault(o["column_key"], []).append(o)
    report: dict = {"per_column": {}}
    for col_key, obs_list in by_col.items():
        truth_map = COLUMN_REFERENCE.get(col_key, {})
        tol = OCR_TOLERANCE.get(col_key, 5.0)
        matched = 0
        for o in obs_list:
            expected = truth_map.get(o["geo_canonical"])
            if expected is None or o["value"] is None:
                continue
            if abs(o["value"] - expected) <= tol:
                matched += 1
        n_truth = len(truth_map)
        accuracy = round(100.0 * matched / n_truth, 1) if n_truth else None
        report["per_column"][col_key] = {
            "sample_count": n_truth,
            "matched_count": matched,
            "accuracy_pct": accuracy,
            "ocr_observations_for_col": len(obs_list),
        }
    report_path = tmp_path / "per_column_accuracy.json"
    report_path.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    payload = json.loads(report_path.read_text(encoding="utf-8"))
    for col_key in COLUMN_REFERENCE:
        assert col_key in payload["per_column"], f"报告缺 {col_key}"


# ---------------------------------------------------------- R3-C 列边界映射

def _make_token(text, right_edge, conf=90):
    """构造一个 _row_to_column_slots 消费的 token 字典。"""
    v, raw, reason = extract_numeric_token(text)
    return {
        "word": {"text": text, "conf": conf, "left": right_edge - 50,
                 "top": 0, "width": 50, "height": 10, "word_num": 0},
        "value": v, "raw_value": raw,
        "missing_reason": None if reason == "OK" else reason,
        "has_value": reason == "OK", "right_edge": right_edge,
    }


def test_column_boundary_mapping_no_shift_on_missing_middle():
    """R3-C 负例：中间某列缺格时，后续列不得整体左移（位置式计数会错位一位）。

    位置式计数把第 i 个数值 cell 硬塞给第 i 列；一旦第 5 列缺失，第 6 列的值
    会被放进第 5 列，之后全部错位。right-edge 边界映射则按 x 归属列，缺格只
    让第 5 列为空，第 6..21 列原封不动。"""
    width = 91.0
    centers = [100.0 + (i + 1) * width for i in range(22)]
    _centers, boundaries, _intervals = build_column_boundaries(centers, k=22)
    grid_interval = (centers[0] - width / 2, centers[-1] + width / 2)

    # 缺第 5 列（center[5]），其余 21 列各有 token
    row_tokens = [_make_token(str(i), centers[i]) for i in range(22) if i != 5]
    slots, dups = _row_to_column_slots(row_tokens, boundaries, grid_interval)

    assert 5 not in slots, "缺格列 5 不应有 token（应显式建模为缺失）"
    # 第 6 列的值仍是原第 6 列，未左移到第 5 列
    assert slots[6]["word"]["text"] == "6", (
        f"列 6 被左移：got {slots[6]['word']['text']} want 6"
    )
    # 末列（列 21）也未左移
    assert slots[21]["word"]["text"] == "21", (
        f"列 21 被左移：got {slots[21]['word']['text']} want 21"
    )
    # 每列最多一个最佳 token；其余列（0..21 除 5 外）都在
    for i in range(22):
        if i != 5:
            assert i in slots, f"列 {i} 缺 token"
    assert 1 not in dups  # 每列单 token → 无 duplicate


def test_column_boundary_duplicate_detection():
    """R3-C：一列收到两个 token（边界映射折叠两列）→ 报 duplicate_column_tokens。"""
    width = 91.0
    centers = [100.0 + (i + 1) * width for i in range(22)]
    _centers, boundaries, _intervals = build_column_boundaries(centers, k=22)
    grid_interval = (centers[0] - width / 2, centers[-1] + width / 2)
    # 列 3 放两个 token
    row_tokens = [_make_token(str(i), centers[i]) for i in range(6)]
    row_tokens.append(_make_token("dup", centers[3] + 20))
    slots, dups = _row_to_column_slots(row_tokens, boundaries, grid_interval)
    assert 3 in dups, "列 3 收到 2 token 应计 duplicate"


def test_column_boundary_assign_matches_schema():
    """R3-C：assign_right_edge_to_column 越界返回最右/最左，不越 schema。"""
    width = 91.0
    centers = [100.0 + (i + 1) * width for i in range(22)]
    _centers, boundaries, _intervals = build_column_boundaries(centers, k=22)
    # 最左 token 归列 0
    assert assign_right_edge_to_column(centers[0] - 5, boundaries) == 0
    # 最右 token 归列 21
    assert assign_right_edge_to_column(centers[-1] + 5, boundaries) == 21
    # 每列 center 恰好归该列
    for i, c in enumerate(centers):
        assert assign_right_edge_to_column(c, boundaries) == i, f"center {i} 归错列"


# ---------------------------------------------------------- 既有契约

def test_full_31x22_grid_exact(result):
    """R3-C: 31 省 × 22 列 = 682 槽位，每省恰好 22 条，一个不多一个不少。"""
    md = result["metadata"]
    n = md["n_observations"]
    assert n == 682, f"观测数必须精确为 31×22=682，实际 {n}"
    provinces = sorted(set(o["geo_canonical"] for o in result["observations"]))
    assert provinces == sorted(KNOWN_PROVINCES), (
        f"省份缺失={set(KNOWN_PROVINCES) - set(provinces)} "
        f"多余={set(provinces) - set(KNOWN_PROVINCES)}"
    )
    from collections import Counter
    per_prov = Counter(o["geo_canonical"] for o in result["observations"])
    assert all(v == EXPECTED_NUMERIC_COLS for v in per_prov.values()), (
        f"每省槽位数必须=22，实际: "
        f"{ {p: c for p, c in per_prov.items() if c != EXPECTED_NUMERIC_COLS} }"
    )
    col_keys = [c["key"] for c in COLUMN_SCHEMA if not c.get("is_label")]
    per_col = Counter(o["column_key"] for o in result["observations"])
    assert all(per_col[k] == len(KNOWN_PROVINCES) for k in col_keys), (
        f"每列必须覆盖全部 31 省，实际: "
        f"{ {k: per_col.get(k, 0) for k in col_keys if per_col.get(k, 0) != len(KNOWN_PROVINCES)} }"
    )


def test_missing_cells_modeled_explicitly(result):
    """R3-C: 缺格以 value=None + 具体 missing_reason 显式建模，绝不静默省略。
    每个 value=None 的槽位必须仍作为 observation 存在（is_missing=True）。"""
    md = result["metadata"]
    missing = [o for o in result["observations"] if o["value"] is None]
    assert len(missing) == md["n_missing"]
    for o in missing:
        assert o["is_missing"] is True
        assert o["missing_reason"] is not None
        assert o["needs_review"] is True
        assert o["needs_review_reasons"], (
            f"缺格 obs 缺原因: {o['geo_canonical']}/{o['column_key']}"
        )
        assert len(o["needs_review_reasons"]) >= 1
    # 缺格原因必须落在已登记集合内（missing_reason 用大写，与全库一致）
    allowed_missing = {"CELL_NOT_DETECTED", "ROW_NOT_DETECTED",
                       "OCR_UNREADABLE", "NOT_PUBLISHED"}
    for o in missing:
        assert o["missing_reason"] in allowed_missing, (
            f"未登记的缺格原因: {o['missing_reason']} "
            f"({o['geo_canonical']}/{o['column_key']})"
        )


def test_every_observation_has_ocr_lineage(result):
    for o in result["observations"]:
        sd = o["source_document"]
        assert sd["file_hash_sha256"] == EXPECTED_HASH
        assert sd["ocr_engine"] == "tesseract"
        sl = o["source_location"]
        assert sl["page_number"] == 1
        assert sl["column_boundary_method"] == "kmeans_right_edge"
        # 缺格（无 token）没有物理 cell_bbox → None；有值时才校验 bbox 正尺寸
        bbox = sl["cell_bbox"]
        if bbox is not None:
            assert bbox["width"] > 0 and bbox["height"] > 0
        assert 0.0 <= o["confidence"] <= 1.0


def test_methodology_caveat_extracted(result):
    sample = result["observations"][0]
    assert "当年价格" in sample["methodology_caveat"]
    assert "初步核算" in sample["methodology_caveat"]


def test_metadata_not_called_truth(result):
    """三-7: metadata 不再叫 'OCR 真值' / 'truth'；只是 'OCR 提取产物'。

    允许显式否定 "NOT human-verified truth"（声明本身不是真值）。"""
    md = result["metadata"]
    flat = json.dumps(md, ensure_ascii=False).lower()
    # 禁止在字段名 / 表头自居为真值；允许否定式免责声明
    import re
    truth_hits = [m.group(0) for m in re.finditer(r"\btruth\b", flat)]
    for hit in truth_hits:
        # 上下文窗口
        idx = flat.find(hit)
        ctx = flat[max(0, idx - 30): idx + len(hit) + 30]
        assert "not" in ctx or "non-" in ctx or "非" in ctx, (
            f"metadata 出现非否定 truth 出现: ...{ctx}..."
        )


def test_extract_numeric_token_handles_missing():
    assert extract_numeric_token("…") == (None, "…", "NOT_PUBLISHED")
    assert extract_numeric_token("—") == (None, "—", "NOT_PUBLISHED")
    v, raw, reason = extract_numeric_token("49843.1")
    assert v == 49843.1 and reason == "OK" and raw == "49843.1"


def test_extract_numeric_token_ocr_garbage():
    v, raw, reason = extract_numeric_token("abc")
    assert v is None and reason == "OCR_UNREADABLE" and raw == "abc"


def test_group_into_rows_respects_y():
    fake = [
        {"text": "A", "conf": 90, "left": 0, "top": 100, "width": 10, "height": 10},
        {"text": "B", "conf": 90, "left": 20, "top": 105, "width": 10, "height": 10},
        {"text": "C", "conf": 90, "left": 0, "top": 200, "width": 10, "height": 10},
    ]
    rows = group_into_rows(fake, y_tolerance=20)
    assert [w["text"] for w in rows[0]] == ["A", "B"]
    assert [w["text"] for w in rows[1]] == ["C"]


def test_no_path_hardcoding():
    src = (ROOT / "extract_00_national_yearbook_table.py").read_text(encoding="utf-8")
    assert "/Users/" not in src
    assert "/Users/kjonekong" not in src


def test_extract_writes_real_output(tmp_path, capsys):
    from extract_00_national_yearbook_table import main as _main
    output = tmp_path / "extracted.json"
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
    assert "31" in captured.out
    payload = json.loads(output.read_text(encoding="utf-8"))
    assert payload["metadata"]["n_observations"] >= 600
    # schema 元数据已写入
    assert len(payload["metadata"]["column_schema"]) == 22


# ---------------------------------------------------------- R4-1 负例：缺失样本/工具必须非 0

def _run_cli(argv: list[str]) -> int:
    """调用 extractor main()。未捕获异常视为 rc=1（Python 进程默认行为）。

    R4-1：缺样本/缺工具必须非 0；进程崩溃（异常）即非 0，无需 main() 显式捕获。
    """
    from extract_00_national_yearbook_table import main as _main
    old_argv = sys.argv
    sys.argv = ["extract.py", *argv]
    try:
        return _main()
    except SystemExit as e:
        return int(e.code) if isinstance(e.code, int) else 1
    except BaseException:
        return 1
    finally:
        sys.argv = old_argv


def test_extractor_fails_when_sample_missing(tmp_path):
    """R4-1: 必需样本缺失必须 failed 非 0（不得 skip）。"""
    rc = _run_cli([
        "--input", str(tmp_path / "missing.jpg"),
        "--output", str(tmp_path / "out.json"),
    ])
    assert rc != 0, f"样本缺失时 extractor 不应 rc=0；got rc={rc}"


def test_extractor_fails_when_tesseract_missing(tmp_path, monkeypatch):
    """R4-1: OCR 工具缺失必须 failed 非 0（不得 skip）。"""
    (tmp_path / "empty_bin").mkdir()
    monkeypatch.setenv("PATH", str(tmp_path / "empty_bin"))
    rc = _run_cli(["--output", str(tmp_path / "out.json")])
    assert rc != 0, f"tesseract 缺失时 extractor 不应 rc=0；got rc={rc}"


# ---------------------------------------------------------- R4-2 全国年鉴证据一致性

REPO = Path(__file__).resolve().parent.parent.parent
EXTRACTED_JSON = (REPO / "data" / "extracts" / "00-national-yearbook-table" /
                  "extracted.json")
PER_COL_JSON = (REPO / "data" / "extracts" / "00-national-yearbook-table" /
                "per_column_accuracy.json")


def _load_extracted() -> dict:
    return json.loads(EXTRACTED_JSON.read_text(encoding="utf-8"))


def _load_per_column() -> dict:
    return json.loads(PER_COL_JSON.read_text(encoding="utf-8"))


def test_per_column_accuracy_covers_all_22_columns():
    """R4-2: 准确率报告必须覆盖全部 22 列（不得挑选 OCR 无损单元）。"""
    r = _load_per_column()
    assert "per_column" in r
    assert "summary" in r
    assert "header" in r
    assert len(r["per_column"]) == 22, (
        f"per_column 应有 22 列，实际 {len(r['per_column'])}"
    )
    for col_key, info in r["per_column"].items():
        for k in ("sample_count", "coverage_pct", "matched_count",
                  "accuracy_pct", "threshold_pct", "verdict"):
            assert k in info, f"列 {col_key} 缺字段 {k}"


def test_per_column_accuracy_header_matches_extracted():
    """R4-2: header 必须与 extracted.json 共享 extractor / hash / 观测数 / 列数。

    任何漂移（668/682、hash 变、列数变、版本变）即 per_column_accuracy.json
    已陈旧，本测试失败。
    """
    ext = _load_extracted()
    pc = _load_per_column()
    md = ext["metadata"]
    h = pc["header"]
    assert h["extractor"] == md["extractor"], (
        f"header.extractor={h['extractor']!r} ≠ metadata.extractor={md['extractor']!r}"
    )
    assert h["input_hash_sha256"] == md["file_hash_sha256"], (
        "input hash 漂移 ⇒ per_column_accuracy.json 已陈旧"
    )
    assert h["n_observations"] == 682 == md["n_observations"], (
        f"观测数漂移: header={h['n_observations']} metadata={md['n_observations']}"
    )
    assert h["n_columns"] == 22, f"列数={h['n_columns']} ≠ 22"
    assert h["expected_n_observations"] == 682
    assert h["expected_n_columns"] == 22


def test_per_column_accuracy_is_byte_reproducible(tmp_path):
    """R4-2: 重新生成 per_column_accuracy.json 必须字节一致（B-07 / I-01）。"""
    # 同一份 extracted.json 输入 → 脚本产出应与 committed 字节一致
    out = tmp_path / "per_column_accuracy.json"
    rc = subprocess.run(
        [sys.executable,
         str(Path(__file__).parent / "build_per_column_accuracy.py"),
         "--input", str(EXTRACTED_JSON),
         "--output", str(out)],
        cwd=str(REPO), capture_output=True, text=True, timeout=120,
    )
    assert rc.returncode == 0, f"regenerate failed: {rc.stderr}\n{rc.stdout}"
    regen_bytes = out.read_bytes()
    committed_bytes = PER_COL_JSON.read_bytes()
    assert regen_bytes == committed_bytes, (
        f"per_column_accuracy.json 不是字节可重现的：\n"
        f"  committed_sha={hashlib.sha256(committed_bytes).hexdigest()[:16]}\n"
        f"  regen_sha=    {hashlib.sha256(regen_bytes).hexdigest()[:16]}"
    )


def test_per_column_overall_verdict_blocked_when_quality_below_threshold():
    """R4-2: needs_review > 50% 或 任一列 0%/低于门槛 → overall_verdict=BLOCKED。

    当前 needs_review=385/682=56.45% > 50% → 必然 BLOCKED。
    """
    pc = _load_per_column()
    s = pc["summary"]
    # 引用 extracted.json 的真实 needs_review 数（而非仅 per_column）
    ext = _load_extracted()
    real_nr = ext["metadata"]["n_needs_review"]
    real_n_obs = ext["metadata"]["n_observations"]
    real_nr_pct = round(100.0 * real_nr / real_n_obs, 2)
    assert s["needs_review_total"] == real_nr, (
        f"per_column needs_review={s['needs_review_total']} "
        f"≠ extracted n_needs_review={real_nr}"
    )
    assert s["needs_review_pct"] == real_nr_pct, (
        f"per_column needs_review_pct={s['needs_review_pct']} "
        f"≠ 直接计算 {real_nr_pct}"
    )
    if real_nr_pct > 50.0:
        assert s["overall_verdict"] == "BLOCKED", (
            f"needs_review_pct={real_nr_pct} > 50% 但 overall_verdict="
            f"{s['overall_verdict']}（违反 docs/08b 50% 回滚线）"
        )
    # 任一列 0%/低于门槛也必须 BLOCKED
    cols_below = s["columns_below_threshold_count"]
    cols_zero = s["columns_at_zero_count"]
    if cols_below or cols_zero:
        assert s["overall_verdict"] == "BLOCKED"


def test_per_column_no_cherry_picking():
    """R4-2: overall_accuracy_pct 必须是全部 22 列 accuracy_pct 的算术平均，
    不得只挑选 OCR 无损单元格再求平均。
    """
    pc = _load_per_column()
    s = pc["summary"]
    pcts = [
        info["accuracy_pct"] for info in pc["per_column"].values()
        if info["accuracy_pct"] is not None
    ]
    expected = round(sum(pcts) / len(pcts), 2) if pcts else None
    assert s["overall_accuracy_pct"] == expected, (
        f"overall_accuracy_pct={s['overall_accuracy_pct']} ≠ 22 列平均 {expected}"
    )