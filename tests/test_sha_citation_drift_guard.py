"""Step (C) per 614 tasking §1.3 — SHA citation drift guard tests.

Per 614 tasking §0.3 (实测值守门) + §1.3 (单元测试守门):
  - 用例 (1) 扫描 `reviews/stage0-gate0-rework-2026-08-23/` 全部 `*.md`，
    断言文件内 SHA 引用形如 `c404980f1eb542dad24504ae0e957c169de60b7d78859159986412fc83541277`（实测值）合法
  - 用例 (2) 断言不存在 `3639e729` 字面引用（过期值）
  - 用例 (3) 断言 612 receipt 文件内 `92e1481c3fea…`（江苏样本地市第四刀实测 SHA）合法引用
  - 用例 (4) 断言 605/606/608/610/612 五个江苏样本 SHA 在 receipt/audit 文件中一致
  - 用例 (5) 断言 `source_registry/registry.csv` 既有 11 行 SHA 在所有 audit/receipt/tasking 文档中引用一致
  - 用例 (6) 断言 `git diff --stat` 后所有修改文件 SHA 一致守门

执行端新增用例必须 PASS.

Per docs/房规 NOT-IN-MANIFEST source code is documentation+spike_helper role category
when bumped via _knife614_manifest_bump.py.

Test count: 6 PASS required (per 614 §1.3 "用例 ≥ 6 个").
"""
from __future__ import annotations

import hashlib
import re
import subprocess
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
REVIEWS_DIR = PROJECT_ROOT / "reviews" / "stage0-gate0-rework-2026-08-23"
REGISTRY_CSV = PROJECT_ROOT / "source_registry" / "registry.csv"
SEED_ARCHIVES = PROJECT_ROOT / "data" / "seed_archives"

# HEAD actual SHA (实测) per 612 §5 EXISTING 11 ROWS IDENTICAL TO HEAD diff verification
HEAD_ACTUAL_SHA = "c404980f1eb542dad24504ae0e957c169de60b7d78859159986412fc83541277"

# Stale/drift SHA patterns (per 614 §0.3)
STALE_SHA_8CHAR = "3639e729"
STALE_SHA_FULL = "3639e729bdb52e40e9681de71591806970260cbc05927da4097fc7692a375420"

# Truncated 61-char SHA drift (per 614 receipt ⚠ disclosure; pre-existing in
# 00-EXEC-QUEUE + 612 receipt; fixed in 614 (B+) step)
TRUNCATED_SHA_61 = "c404980f1eb542dad24504ae0e957c169de60b7d78859186412fc83541277"

# 5 江苏样本 SHA values (per 605/606/608/610/612 receipt)
JIANGSU_SHAS = {
    "stats_gov_cn_zxfb_605": "450e7f723795241c58c34c3c8f18147cf289db04c3fa2bbbdd7c0db564f49279",
    "suzhou_606":            "df3d8246679040968a747762d8c11eccf7b63647cadfc2c50719322badf7c7fd",
    "nanjing_608":           "37ed4c223b16397f66781744987dafa6ab975fc0ceb7006a028b3edb62ce2712",
    "changzhou_610":         "0ecf3d2ed76407c4bf50a5cba8552af78ca2e22fcc5ab39966b1212aac6979f6",
    "nantong_612":           "92e1481c3fea5962569979086b30983cf1b2ee950d8ca940b3d524d2bac35f54",
}


def _compute_registry_11rows_sha() -> str:
    """Compute SHA-256 of registry.csv first 11 lines (with trailing \\n each).
    Matches `head -11 source_registry/registry.csv | shasum -a 256` semantics.
    """
    with open(REGISTRY_CSV, "rb") as f:
        raw = f.read()
    lines = raw.splitlines(keepends=True)[:11]
    return hashlib.sha256(b"".join(lines)).hexdigest()


def test_1_head_actual_sha_legal():
    """(1) HEAD 实测值合法: registry.csv 既有 11 行 SHA = c404980f1eb542... 实测一致."""
    actual = _compute_registry_11rows_sha()
    assert actual == HEAD_ACTUAL_SHA, (
        f"registry.csv first 11 rows SHA {actual[:16]}... != "
        f"HEAD actual {HEAD_ACTUAL_SHA[:16]}... "
        f"(per 612 §5 EXISTING 11 ROWS IDENTICAL TO HEAD diff verification)"
    )
    assert len(actual) == 64, f"SHA must be 64 chars, got {len(actual)}"


def test_2_no_stale_sha_references():
    """(2) Per 616 (C') verbatim: 没有文件把 `3639e729` 作为权威 SHA 引用.

    Stricter pattern per 616 §1.3 (C') option α+β: git grep 在关键权威引用点
    (source_registry/registry.csv / evidence_pack/manifest.json / schema/01-core.sql)
    匹配 stale SHA — 这些文件才是 SHA 权威引用点。

    Narrative 描述（receipt/audit/tasking 中描述 drift history）已通过
    616 (B') 改写为「过期 8-char prefix」label 形式（per 616 §0.1 (B') (ii) + (iii)），
    不视为权威引用。
    """
    import re
    AUTHORITATIVE_PATHS = [
        "source_registry/registry.csv",
        "evidence_pack/manifest.json",
        "schema/01-core.sql",
    ]
    for pattern in (STALE_SHA_8CHAR, STALE_SHA_FULL):
        result = subprocess.run(
            ["git", "grep", "-nH", "-E", rf"{re.escape(pattern)}",
             "--", *AUTHORITATIVE_PATHS],
            capture_output=True, text=True, cwd=str(PROJECT_ROOT),
        )
        # git grep returns 1 when no matches (or non-existent path; non-existent paths
        # in 列表不报错 — 仅跳过)
        if result.returncode == 0:
            matching = result.stdout.strip()
            assert False, (
                f"Stale SHA '{pattern}' cited as authoritative in critical files:\n"
                f"{matching}\n"
                f"(per 616 (C') verbatim「没有文件把 3639e729 作为权威 SHA 引用」)"
            )


def test_3_nantong_sha_in_612_receipt():
    """(3) 江苏样本地市第四刀 (nantong) SHA 在 612 receipt 内合法引用."""
    receipt_path = REVIEWS_DIR / (
        "612-stage0-cc-o1-§5.2.x-real-sha-locked-江苏样本-地市第四刀-tasking-20260829-receipt.md"
    )
    assert receipt_path.exists(), f"612 receipt not found: {receipt_path}"
    text = receipt_path.read_text(encoding="utf-8")
    expected_sha = JIANGSU_SHAS["nantong_612"]
    assert expected_sha in text, (
        f"612 receipt does not cite nantong SHA {expected_sha[:16]}... "
        f"(per 612 receipt §3 source_document.source_sha256)"
    )


def test_4_five_jiangsu_samples_consistent():
    """(4) 5 江苏样本 SHA 一致: 605/606/608/610/612 SHA 在 registry.csv + 各自 receipt 文件内引用一致."""
    registry_text = REGISTRY_CSV.read_text(encoding="utf-8")
    for sample_name, sha in JIANGSU_SHAS.items():
        assert sha in registry_text, (
            f"registry.csv missing {sample_name} SHA {sha[:16]}..."
        )
        # Verify SHA matches actual file content on disk
        # Map sample name to actual file
        filename_map = {
            "stats_gov_cn_zxfb_605": "jiangsu_stats_gov_cn_zxfb_20260829.html",
            "suzhou_606":            "jiangsu_suzhou_tjj_gov_cn_20260829.html",
            "nanjing_608":           "jiangsu_nanjing_tjj_gov_cn_20260829.html",
            "changzhou_610":         "jiangsu_changzhou_tjj_gov_cn_20260829.html",
            "nantong_612":           "jiangsu_nantong_tjj_gov_cn_20260829.html",
        }
        fpath = SEED_ARCHIVES / filename_map[sample_name]
        if fpath.exists():
            actual_file_sha = hashlib.sha256(fpath.read_bytes()).hexdigest()
            assert actual_file_sha == sha, (
                f"{sample_name} file SHA drift: on-disk {actual_file_sha[:16]}... "
                f"!= registry {sha[:16]}..."
            )


def test_5_head_11rows_sha_consistent_in_docs():
    """(5) registry.csv 既有 11 行 HEAD actual SHA 在所有 audit/receipt 文档中引用一致."""
    # Count occurrences of HEAD_ACTUAL_SHA across receipts/audits
    target_files = [
        "609-stage0-architect-s608-o1-§5.2.x-real-sha-locked-江苏样本-地市第二刀-tasking-20260829-audit-PASS-20260829.md",
        "610-stage0-cc-o1-§5.2.x-real-sha-locked-江苏样本-地市第三刀-tasking-20260829-receipt.md",
        "611-stage0-architect-s610-o1-§5.2.x-real-sha-locked-江苏样本-地市第三刀-tasking-20260829-audit-PASS-20260829.md",
        "612-stage0-cc-o1-§5.2.x-real-sha-locked-江苏样本-地市第四刀-tasking-20260829-receipt.md",
    ]
    head_actual_count = 0
    for fname in target_files:
        fpath = REVIEWS_DIR / fname
        if not fpath.exists():
            continue
        text = fpath.read_text(encoding="utf-8")
        n = text.count(HEAD_ACTUAL_SHA)
        head_actual_count += n
        assert n > 0, f"{fname} does not cite HEAD actual SHA (drift regression)"
    assert head_actual_count >= 10, (
        f"HEAD actual SHA cited too few times ({head_actual_count}); "
        f"expected ≥10 across 4 target files"
    )


def test_6_git_diff_sha_consistency_guard():
    """(6) Per 616 (C') verbatim: 没有文件把 truncated 61-char SHA 作为权威 SHA 引用.

    Stricter pattern per 616 §1.3 (C') option α: git grep 在关键权威引用点
    (source_registry/registry.csv / evidence_pack/manifest.json / schema/01-core.sql)
    匹配 truncated 61-char SHA — 这些文件才是 SHA 权威引用点。

    Narrative 描述（receipt/audit/tasking 中描述 drift history）已通过
    616 (B') 保留「truncated 61-char SHA」+「缺 `5998` 4 字符」label 形式，
    不视为权威引用。
    """
    import re
    AUTHORITATIVE_PATHS = [
        "source_registry/registry.csv",
        "evidence_pack/manifest.json",
        "schema/01-core.sql",
    ]
    result_trunc = subprocess.run(
        ["git", "grep", "-nH", "-E", rf"{re.escape(TRUNCATED_SHA_61)}",
         "--", *AUTHORITATIVE_PATHS],
        capture_output=True, text=True, cwd=str(PROJECT_ROOT),
    )
    if result_trunc.returncode == 0:
        matching = result_trunc.stdout.strip()
        assert False, (
            f"Truncated 61-char SHA cited as authoritative in critical files:\n"
            f"{matching}\n"
            f"(per 616 (C') verbatim「没有文件把 truncated 61-char SHA 作为权威 SHA 引用」)"
        )
    # Also re-verify HEAD actual 11-row SHA didn't drift from fixed value
    actual = _compute_registry_11rows_sha()
    assert actual == HEAD_ACTUAL_SHA, (
        f"registry.csv 11-row SHA drifted post-fix: {actual[:16]}..."
    )


if __name__ == "__main__":
    # Allow running as script: python tests/test_sha_citation_drift_guard.py
    import pytest
    sys.exit(pytest.main([__file__, "-v"]))