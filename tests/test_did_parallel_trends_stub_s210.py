"""S2.10 docs/10 §3.4 — test_did_requires_parallel_trends (xfail stub).

Per docs/10 §163-172 + docs/45 §4 + tasking 250 §3.4 mapping.

本测试为 STUB (xfail)。原因：
  - §3.4 验收要求 DiD + 平行趋势检验（p > 0.1）
  - DiD/合成控制 UI (L6-L7) 属 Stage 3 S3.4 范围（per docs/08 §4 + docs/05 §9）
  - Gate 2 评审仅要求测试**存在**（per docs/08 §3.2 验收项 #7）

pytest.mark.xfail 显式声明，reason 必须含 "Stage 3 收口" 字样。
"""
from __future__ import annotations

import pytest


@pytest.mark.xfail(
    reason="Stage 3 收口 (per docs/10 §163-172 + docs/08 §4 S3.4 + docs/45 §4)",
    strict=False,
)
def test_did_requires_parallel_trends() -> None:
    """Case 1 (xfail stub): DiD 必须验证平行趋势。

    Per docs/10 §165-171 spec:
      result = run_did(treatment="某政策", treatment_geo="浙江", control_geos=["江苏","广东"])
      pre_trends = result.pre_treatment_trends
      p_value = result.parallel_trends_test.p_value
      assert p_value > 0.1, f"平行趋势检验失败 (p={p_value})"

    本刀仅占位；Stage 3 S3.4 收口时实做。
    """
    # Stage 3 收口时实现：
    #   - L4+ analyzer: 实现 run_did(treatment, treatment_geo, control_geos)
    #   - 平行趋势检验 (pre-treatment parallel trends test, p > 0.1)
    #   - dbt mart: mart_did_result 含 pre_trends + parallel_trends_test_p 列
    pytest.skip(
        "xfail stub — Stage 3 收口 (per docs/10 §3.4 + docs/45 §4 + docs/08 §4 S3.4)"
    )


def test_placeholder_presence() -> None:
    """Case 2 (meta): 本测试文件存在性守门。"""
    import pathlib
    test_file = pathlib.Path(__file__)
    assert test_file.exists(), f"self-test missing: {test_file}"
    text = test_file.read_text(encoding="utf-8")
    assert "Stage 3 收口" in text, (
        "xfail reason 必须显式标注 'Stage 3 收口' (per docs/45 §4 + docs/34 §3 O5)"
    )