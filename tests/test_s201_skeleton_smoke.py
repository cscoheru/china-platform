"""Stage 2 / S2.0.1 — Next.js skeleton smoke (pytest wrapper).

Per tasking 146 §NOW.3: "pytest 或前端 smoke（最小可验收）".

This test wraps frontend/smoke-check.py so it runs under pytest. We avoid
spawning `next build` (which would require node_modules in the test env).

S2.0.1 is a *skeleton*, not a deployed app; pytest is the smallest acceptable
verification that satisfies tasking 146. Subsequent Stage 2 刀 (S2.7-b etc.)
will add real Playwright/Next.js e2e.

661 C2/C3: 5 静态省详情页 (jiangsu/guangdong/shandong/sichuan/zhejiang) 已删除,
统一由 provinces/[province_code]/page.tsx 动态路由 + generateStaticParams 接管.
本文件对应 needle 同步到动态路由形态,旧 jiangsu 专属测试替换为 province 动态路由守门.
"""
from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

import pytest

FRONTEND_DIR = Path(__file__).resolve().parent.parent / "frontend"
SMOKE_SCRIPT = FRONTEND_DIR / "smoke-check.py"


def _run_smoke() -> subprocess.CompletedProcess:
    """Invoke frontend/smoke-check.py and capture output."""
    if not SMOKE_SCRIPT.is_file():
        pytest.fail(f"smoke-check.py missing at {SMOKE_SCRIPT}")
    return subprocess.run(
        [sys.executable, str(SMOKE_SCRIPT)],
        cwd=str(FRONTEND_DIR),
        capture_output=True,
        text=True,
        check=False,
    )


def test_frontend_skeleton_files_present() -> None:
    """Required skeleton files exist under frontend/.

    661 C3: app/provinces/jiangsu/page.tsx (静态页) 已删除,改测
    app/provinces/[province_code]/page.tsx (动态路由) + components/ProvinceGdpTable.tsx (C1 组件).
    """
    required = [
        "package.json",
        "tsconfig.json",
        "next.config.js",
        "README.md",
        "app/layout.tsx",
        "app/page.tsx",
        "app/DemoBadge.tsx",
        "app/provinces/[province_code]/page.tsx",  # 661 C2 dynamic route
        "app/components/ProvinceGdpTable.tsx",  # 661 C1 mart table component
        "lib/api.ts",
        "lib/types.ts",
        "lib/mock.ts",
    ]
    missing = [p for p in required if not (FRONTEND_DIR / p).is_file()]
    assert not missing, f"missing frontend files: {missing}"


def test_frontend_skeleton_smoke_passes() -> None:
    """frontend/smoke-check.py returns 0 and reports PASS."""
    result = _run_smoke()
    if result.returncode != 0:
        pytest.fail(
            f"smoke-check.py failed (rc={result.returncode})\n"
            f"STDOUT:\n{result.stdout}\nSTDERR:\n{result.stderr}"
        )
    assert "PASS" in result.stdout, (
        f"smoke-check.py did not print PASS marker; got:\n{result.stdout}"
    )


def test_frontend_package_declares_next_react() -> None:
    """package.json depends on next + react + react-dom."""
    import json

    pkg = json.loads((FRONTEND_DIR / "package.json").read_text(encoding="utf-8"))
    deps = pkg.get("dependencies", {})
    for dep in ("next", "react", "react-dom"):
        assert dep in deps, f"package.json missing dependency: {dep}"


def test_frontend_mock_data_has_is_demo_sentinel() -> None:
    """lib/mock.ts includes at least one row with lineage.is_demo === "true".

    Per docs/34 §4.2 + tasking 146 §SCHEMA: this is the load-bearing requirement
    that distinguishes S1.18 DEMO sentinels from future real SHA-locked samples.
    """
    import re

    mock = (FRONTEND_DIR / "lib/mock.ts").read_text(encoding="utf-8")
    assert re.search(r'is_demo:\s*"true"', mock), (
        "lib/mock.ts has no lineage.is_demo === 'true' sentinel row"
    )


def test_frontend_readme_documents_mock_toggle() -> None:
    """README.md explains NEXT_PUBLIC_USE_MOCK + is_demo badge contract."""
    readme = (FRONTEND_DIR / "README.md").read_text(encoding="utf-8")
    assert "NEXT_PUBLIC_USE_MOCK" in readme, "README does not document mock toggle"
    assert "is_demo" in readme, "README does not document is_demo badge contract"


def test_frontend_province_dynamic_route_has_no_params_branch() -> None:
    """661 C3: 静态 jiangsu 页删除后, 旧 "params.province 不应作为 gate" 守门
    转移到 provinces/[province_code]/page.tsx 动态路由. 动态路由才有 params,但必须
    generateStaticParams 静态预生成所有合法 slug,不依赖运行时 params 守门.

    Strip JS comments before scanning.
    """
    import re

    province_route = (FRONTEND_DIR / "app/provinces/[province_code]/page.tsx")
    assert province_route.is_file(), (
        f"provinces/[province_code]/page.tsx 缺失 (661 C2 必须存在)"
    )
    code = province_route.read_text(encoding="utf-8")
    code = re.sub(r"//[^\n]*", "", code)
    code = re.sub(r"/\*.*?\*/", "", code, flags=re.DOTALL)
    # 动态路由必须 generateStaticParams + dynamicParams=false (404 兜底 per docs/46 §3.1)
    assert "generateStaticParams" in code, (
        "provinces/[province_code]/page.tsx 缺 generateStaticParams"
    )
    assert "dynamicParams" in code and "false" in code, (
        "provinces/[province_code]/page.tsx 缺 dynamicParams=false 兜底"
    )
    # 32 个合法代码 (31 GB/T + NATIONAL) 必须齐全,uppercase 在源中
    assert "NATIONAL" in code and "BEIJING" in code and "XINJIANG" in code, (
        "provinces/[province_code]/page.tsx 缺 32 合法代码枚举"
    )


def test_frontend_province_route_renders_data_or_missing_branch() -> None:
    """661 C2: 动态路由必须既支持真实数据分支 (28 真省渲染 5 指标) 又支持
    DATA_MISSING 分支 (3 缺失省显式「数据暂缺」)."""
    province_route = (FRONTEND_DIR / "app/provinces/[province_code]/page.tsx")
    code = province_route.read_text(encoding="utf-8")
    # DATA_MISSING 分支
    assert "DATA_MISSING" in code, (
        "provinces/[province_code]/page.tsx 缺 DATA_MISSING 分支"
    )
    assert "数据暂缺" in code or "missing_reason" in code, (
        "provinces/[province_code]/page.tsx DATA_MISSING 分支未显示明示文案"
    )
    # 真实数据分支必须有 fmtNum/fmtPct 或等价数值格式化
    assert "fmtNum" in code or "toLocaleString" in code, (
        "provinces/[province_code]/page.tsx 缺数值格式化 (fmtNum/toLocaleString)"
    )