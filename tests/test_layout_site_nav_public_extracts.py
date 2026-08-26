# Knife 72 (tasking 409) — 全站顶栏 /public-extracts 常驻链 测试.
#
# Per 409 §SCHEMA:
#   (1) layout.tsx 顶栏增全站常驻链 /public-extracts (四轨 demo / 非 O1)
#   (2) banner 补一句主演示入口 (nav 旁注)
#   (3) ≥1 smoke/pytest (本文件)
#   (4) 回执 410
#
# 红线 (per 409 §红线): 不 Gate/O1 PASS; 不分支 params.* (AGENTS.md standing
# red line — static-segment Next.js routes must NOT branch on params.*).
from __future__ import annotations

import re
from pathlib import Path

import pytest

PROJECT_ROOT = Path(__file__).resolve().parent.parent
LAYOUT = PROJECT_ROOT / "frontend" / "app" / "layout.tsx"


def _strip_comments(src: str) -> str:
    code = re.sub(r"//[^\n]*", "", src)
    code = re.sub(r"/\*.*?\*/", "", code, flags=re.DOTALL)
    return code


def test_layout_has_site_nav_container() -> None:
    """Per 409 §SCHEMA-1: layout.tsx 必须含 <nav data-testid="site-nav">
    作为顶栏常驻链的容器（带 testId 供 smoke + 测试复用)."""
    assert LAYOUT.is_file(), f"missing layout: {LAYOUT}"
    src = LAYOUT.read_text(encoding="utf-8")
    code = _strip_comments(src)
    assert 'data-testid="site-nav"' in code, (
        "layout.tsx 必须含 <nav data-testid=\"site-nav\"> 顶栏常驻链容器 "
        "(per 409 §SCHEMA-1)"
    )


def test_layout_site_nav_links_public_extracts() -> None:
    """Per 409 §SCHEMA-1: site-nav 内必须含 href="/public-extracts" 链 +
    渲染 testId；使用 <a> 锚链 (不引入 Next.js Link 避免 dynamic params)."""
    src = LAYOUT.read_text(encoding="utf-8")
    code = _strip_comments(src)
    assert 'href="/public-extracts"' in code, (
        "layout.tsx site-nav 缺少 href=\"/public-extracts\" 全站常驻链 "
        "(per 409 §SCHEMA-1)"
    )
    assert 'data-testid="site-nav-public-extracts"' in code, (
        "layout.tsx site-nav 链缺少 data-testid (供 smoke + 测试定位)"
    )


def test_layout_site_nav_disclaimer_and_no_o1_or_gate_pass_claim() -> None:
    """Per 409 §SCHEMA + §红线: site-nav 必须显式非 O1 / 不宣布 Gate PASS
    （四轨 demo / 非 O1 / 不 Gate PASS 三句必含)."""
    src = LAYOUT.read_text(encoding="utf-8")
    code = _strip_comments(src)
    for needle, label in (
        ("四轨 demo", "四轨 demo 标注"),
        ("非 O1", "非 O1 守门"),
        ("不宣布 Gate PASS", "不宣布 Gate PASS 守门"),
    ):
        assert needle in code, f"layout.tsx site-nav 缺少 {label} (per 409 §红线)"


def test_layout_does_not_branch_on_params() -> None:
    """Per AGENTS.md standing red line: static-segment Next.js routes must
    NOT branch on params.* (always undefined). layout.tsx 是 root layout
    (静态)，绝对不允许 params.* 分支."""
    src = LAYOUT.read_text(encoding="utf-8")
    code = _strip_comments(src)
    # 任意 params. / .params 都禁手 — 静态 layout 永远拿不到 params
    assert not re.search(r"params\s*\.", code), (
        "layout.tsx 出现 params.* 分支 — 静态 root layout 不允许 "
        "(per AGENTS.md standing red line)"
    )
    assert ".params" not in code, (
        "layout.tsx 出现 .params 引用 — 静态 root layout 不允许 "
        "(per AGENTS.md standing red line)"
    )


def test_layout_site_nav_uses_anchor_not_nextjs_link() -> None:
    """Per 409 §SCHEMA: site-nav 用纯 <a href> 锚链；不引入 Next.js <Link>
    避免 dynamic params 推断；保留 ○ Static build 特征."""
    src = LAYOUT.read_text(encoding="utf-8")
    code = _strip_comments(src)
    # 必须出现 <a href="/public-extracts"> 形式（不是 Link href）
    assert "<a" in code and 'href="/public-extracts"' in code, (
        "layout.tsx site-nav 须用 <a href> 锚链 (per 409 §SCHEMA)"
    )
    # 不引入 next/link 避免 dynamic params 副作用
    assert "from \"next/link\"" not in code, (
        "layout.tsx 不应 import next/link (静态锚链, per 409 §SCHEMA)"
    )