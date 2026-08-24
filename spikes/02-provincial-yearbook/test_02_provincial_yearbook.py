"""
test_extract.py — Spike 02: Provincial Statistical Yearbook Extraction Tests
(reworked per 返工指令 §四 + B-06 + I-02)

测试覆盖：
  * 文件完整性 / SHA-256 锁定
  * 新 schema 字段：metadata / observations / lineage
  * 每行 period_start / period_end / period_label / period_type 齐全
  * 每行 comparison_basis 必填且非 UNKNOWN（除特殊行）
  * 每行 lineage.chain_id + lineage.source_file_sha256 齐全
  * 确定性重建：两次运行输出 SHA-256 必一致
  * 不可硬编码绝对家目录路径（per I-02）
"""
from __future__ import annotations

import hashlib
import json
import os
import subprocess
import sys
from pathlib import Path

import pytest

HERE = Path(__file__).parent
REPO = HERE.parent.parent
RAW_FILE = HERE / "hubei_2026_06.xlsx"
EXTRACTOR = HERE / "extract_02_provincial_yearbook.py"
EXTRACTED_FILE = REPO / "data" / "extracts" / "02-provincial-yearbook" / "extracted.json"


def _run(cmd: list[str], **kw) -> subprocess.CompletedProcess:
    return subprocess.run([sys.executable, *cmd], cwd=str(REPO),
                          capture_output=True, text=True,
                          env={**os.environ, "PYTHONDONTWRITEBYTECODE": "1"},
                          **kw)


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture(scope="module")
def raw_hash():
    return hashlib.sha256(RAW_FILE.read_bytes()).hexdigest()


@pytest.fixture(scope="module")
def extracted():
    return json.loads(EXTRACTED_FILE.read_text(encoding="utf-8"))


@pytest.fixture(scope="module")
def observations(extracted):
    return extracted["observations"]


# ---------------------------------------------------------------------------
# File integrity
# ---------------------------------------------------------------------------

class TestFileIntegrity:
    def test_raw_file_exists(self):
        assert RAW_FILE.exists()

    def test_extracted_json_exists(self):
        assert EXTRACTED_FILE.exists()

    def test_sha256_matches(self, extracted, raw_hash):
        assert extracted["metadata"]["file_hash_sha256"] == raw_hash

    def test_extractor_exists(self):
        assert EXTRACTOR.exists()


# ---------------------------------------------------------------------------
# 新 schema 字段
# ---------------------------------------------------------------------------

class TestNewSchemaFields:
    def test_metadata_wrapper(self, extracted):
        assert "metadata" in extracted
        md = extracted["metadata"]
        for k in ("spike", "province_zh", "province_code_gb2260",
                  "period_start", "period_end", "period_label", "period_type",
                  "source_agency", "source_url", "table_title",
                  "column_headers", "file_name", "file_size_bytes",
                  "file_hash_sha256", "extractor_version"):
            assert k in md, f"metadata 缺 {k}"

    def test_province_metadata(self, extracted):
        md = extracted["metadata"]
        assert md["province_zh"] == "湖北"
        assert md["province_code_gb2260"] == "42"
        assert md["province_pinyin"] == "Hubei"

    def test_period_metadata(self, extracted):
        md = extracted["metadata"]
        assert md["period_start"] == "2026-01-01"
        assert md["period_end"] == "2026-06-30"
        assert md["period_type"] == "CUMULATIVE_HALF_YEAR"

    def test_lineage_chain_exists(self, extracted):
        assert "lineage" in extracted
        lg = extracted["lineage"]
        for k in ("chain_id", "source_publisher", "source_publisher_url",
                  "source_file_url", "source_file_sha256",
                  "extractor", "extractor_version", "stages"):
            assert k in lg, f"lineage 缺 {k}"
        assert lg["stages"], "lineage.stages 至少要有一个 stage"

    def test_extractor_version_recorded(self, extracted):
        assert extracted["metadata"]["extractor_version"].startswith("2.")


# ---------------------------------------------------------------------------
# Per-row 血缘 (per directive 四-2/3)
# ---------------------------------------------------------------------------

class TestPerRowLineage:
    def test_every_row_has_period(self, observations):
        for r in observations:
            assert "period_start" in r, f"row 缺 period_start: {r.get('indicator_zh')}"
            assert "period_end" in r
            assert "period_label" in r
            assert "period_type" in r

    def test_every_row_has_comparison_basis(self, observations):
        unknown_rows = [r for r in observations if r.get("comparison_basis") == "UNKNOWN"]
        assert len(unknown_rows) == 0, (
            f"{len(unknown_rows)} 行 comparison_basis=UNKNOWN: "
            f"{[r['indicator_zh'] for r in unknown_rows]}"
        )

    def test_every_row_has_lineage(self, observations):
        for r in observations:
            assert "lineage" in r, f"row 缺 lineage: {r.get('indicator_zh')}"
            lg = r["lineage"]
            for k in ("chain_id", "source_file_sha256", "source_file_url",
                      "extractor_version"):
                assert k in lg, f"row lineage 缺 {k}: {r.get('indicator_zh')}"

    def test_lineage_sha_matches_file(self, observations, raw_hash):
        """per-row lineage.source_file_sha256 必须等于 file_hash_sha256"""
        for r in observations:
            assert r["lineage"]["source_file_sha256"] == raw_hash

    def test_chain_id_consistent_across_rows(self, observations):
        ids = {r["lineage"]["chain_id"] for r in observations}
        assert len(ids) == 1, f"lineage chain_id 不一致: {ids}"


# ---------------------------------------------------------------------------
# Per-row indicator_canonical (B-08: 标准化)
# ---------------------------------------------------------------------------

class TestIndicatorCanonical:
    def test_canonical_present(self, observations):
        for r in observations:
            assert "indicator_canonical" in r
            assert r["indicator_canonical"], f"canonical 为空: {r.get('indicator_zh')}"

    def test_canonical_no_chinese(self, observations):
        """中文别名不应作为 indicator_canonical 进 DB（per B-08）。"""
        import re
        cjk = re.compile(r"[一-鿿]")
        for r in observations:
            assert not cjk.search(r["indicator_canonical"]), (
                f"indicator_canonical 含中文: {r['indicator_canonical']}"
            )

    def test_no_unknown_indicators(self, observations):
        bad = [r for r in observations if r["indicator_canonical"].startswith("unknown__")]
        assert len(bad) == 0, (
            f"{len(bad)} 行未映射: {[(r['indicator_zh'], r['indicator_canonical']) for r in bad]}"
        )


# ---------------------------------------------------------------------------
# Deterministic rebuild (per directive 四-1)
# ---------------------------------------------------------------------------

class TestDeterministicRebuild:
    def test_verify_determinism_subprocess(self):
        """脚本支持 --verify-determinism 自检两次输出哈希一致。"""
        rc = _run([str(EXTRACTOR), "--verify-determinism"])
        assert rc.returncode == 0, f"determinism 失败: {rc.stderr}\n{rc.stdout}"
        assert "byte-identical" in rc.stdout

    def test_two_runs_produce_same_hash(self, tmp_path):
        out_a = tmp_path / "a.json"
        out_b = tmp_path / "b.json"
        rc1 = _run([str(EXTRACTOR), "--output", str(out_a)])
        rc2 = _run([str(EXTRACTOR), "--output", str(out_b)])
        assert rc1.returncode == 0 and rc2.returncode == 0
        assert out_a.read_bytes() == out_b.read_bytes()

    def test_extracted_at_locked(self, extracted):
        """extracted_at 必须固定，不允许 datetime.now() 漂移。"""
        lg = extracted["lineage"]
        assert "T" in lg["extracted_at"]
        # 不允许微秒精度漂移
        assert lg["extracted_at"].endswith("Z") or "+00:00" in lg["extracted_at"]


# ---------------------------------------------------------------------------
# 数据契约
# ---------------------------------------------------------------------------

class TestDataContract:
    def test_row_count(self, observations):
        assert len(observations) == 19, f"期望 19 数据行，实际 {len(observations)}"

    def test_gdp_row_has_value(self, observations):
        gdp = [r for r in observations if "地区生产总值" in r["indicator_zh"]]
        assert gdp and gdp[0]["value"] is not None
        assert gdp[0]["value"] == 31336.72

    def test_needs_review_consistent(self, observations):
        for r in observations:
            if r["needs_review"]:
                assert r["needs_review_reasons"], f"needs_review=True 但无原因: {r}"
                assert r["missing_reason"], f"needs_review=True 但缺 missing_reason: {r}"

    def test_comparison_basis_known_values(self, observations):
        allowed = {
            "CUMULATIVE_YOY", "CUMULATIVE_YOY_5MONTH",
            "PERIOD_END_YOY", "INDEX_YOY", "UNKNOWN",
        }
        for r in observations:
            assert r["comparison_basis"] in allowed, (
                f"未知 comparison_basis: {r['comparison_basis']}"
            )


# ---------------------------------------------------------------------------
# R3-E: per-indicator period metadata（不得强制单一半年累计）
# ---------------------------------------------------------------------------

class TestR3PeriodMetadata:
    """R3-E：按指标真实周期建模，而非强制单一半年累计口径。"""

    def test_1_5_month_indicator_uses_5month_period(self, observations):
        """指标名含 '1-5月' → period_end=2026-05-31，type=CUMULATIVE_5MONTH。"""
        fdi = [r for r in observations if "1-5月" in r["indicator_zh"]]
        assert len(fdi) >= 1, "样本必须包含至少一个 1-5月 指标"
        for r in fdi:
            assert r["period_end"] == "2026-05-31", (
                f"{r['indicator_zh']} period_end 应为 2026-05-31, 实际 {r['period_end']}"
            )
            assert r["period_type"] == "CUMULATIVE_5MONTH", (
                f"{r['indicator_zh']} period_type 应为 CUMULATIVE_5MONTH"
            )

    def test_eom_indicator_uses_period_end_type(self, observations):
        """指标名含 '月末' → period_start=period_end=2026-06-30，type=PERIOD_END_OF_MONTH。"""
        eom = [r for r in observations if "月末" in r["indicator_zh"]]
        assert len(eom) >= 2, "样本必须包含至少两个月末指标"
        for r in eom:
            assert r["period_start"] == "2026-06-30", (
                f"{r['indicator_zh']} period_start 应为 2026-06-30"
            )
            assert r["period_end"] == "2026-06-30", (
                f"{r['indicator_zh']} period_end 应为 2026-06-30"
            )
            assert r["period_type"] == "PERIOD_END_OF_MONTH", (
                f"{r['indicator_zh']} period_type 应为 PERIOD_END_OF_MONTH"
            )

    def test_gdp_and_income_have_pending_verification_caveat(self, observations):
        """GDP/居民收入 → caveat 标记待核验 + quarterly_data_verified=False。"""
        gdp = [r for r in observations if "生产总值" in r["indicator_zh"]]
        income = [r for r in observations if "居民收入" in r["indicator_zh"]
                  or "可支配收入" in r["indicator_zh"]]
        assert len(gdp) >= 1, "样本必须包含 GDP"
        assert len(income) >= 1, "样本必须包含居民收入"
        for r in gdp + income:
            assert r.get("caveat"), (
                f"{r['indicator_zh']} 必须带 caveat 标记（R3-E）"
            )
            assert "季度" in r["caveat"] or "待核验" in r["caveat"], (
                f"{r['indicator_zh']} caveat 必须明确标注季度口径: {r['caveat']}"
            )
            assert r.get("quarterly_data_verified") is False, (
                f"{r['indicator_zh']} quarterly_data_verified 必须为 False（待核验）"
            )

    def test_other_indicators_default_half_year(self, observations):
        """未在 PERIOD_METADATA_MAP 中的指标 → 默认 2026年1-6月 CUMULATIVE_HALF_YEAR，无 caveat。

        排除特殊类目：GDP/居民收入/1-5月/月末/指数（CPI/PPI 各自有专属 caveat）。
        """
        special = lambda r: (
            "生产总值" in r["indicator_zh"]
            or "居民收入" in r["indicator_zh"]
            or "可支配收入" in r["indicator_zh"]
            or "1-5月" in r["indicator_zh"]
            or "月末" in r["indicator_zh"]
            or "指数" in r["indicator_zh"]  # CPI/PPI 有专属 caveat
        )
        non_mapped = [r for r in observations if not special(r)]
        assert len(non_mapped) >= 5, "样本必须包含若干常规指标"
        for r in non_mapped:
            assert r["period_type"] == "CUMULATIVE_HALF_YEAR"
            assert r["period_label"] == "2026年1-6月"
            assert r.get("caveat") is None or r.get("caveat") == "", (
                f"{r['indicator_zh']} 不应带 caveat: {r.get('caveat')}"
            )


# ---------------------------------------------------------------------------
# No hardcoded paths (per I-02)
# ---------------------------------------------------------------------------

class TestNoPathHardcoding:
    def test_no_users_path_in_extractor(self):
        src = EXTRACTOR.read_text(encoding="utf-8")
        # 构造搜索串以避免自匹配
        slash = chr(47)
        users_pat = slash + "Users" + slash
        user_pat = users_pat + chr(107) + chr(106) + chr(111) + chr(110) + chr(101) + chr(107) + chr(111) + chr(110) + chr(103)
        assert users_pat not in src
        assert user_pat not in src

    def test_no_users_path_in_test(self):
        src = Path(__file__).read_text(encoding="utf-8")
        slash = chr(47)
        users_pat = slash + "Users" + slash
        user_pat = users_pat + chr(107) + chr(106) + chr(111) + chr(110) + chr(101) + chr(107) + chr(111) + chr(110) + chr(103)
        # sentinel 也由 chr() 拼出，避免自身字面量被自匹配
        sentinel = chr(88) + "USERS" + chr(88)
        cleaned = src.replace(users_pat, sentinel)
        assert sentinel not in cleaned, f"硬编码绝对家目录路径"
        assert user_pat not in cleaned, f"硬编码用户名"


if __name__ == "__main__":
    sys.exit(pytest.main([__file__, "-v", "--tb=short"]))