#!/usr/bin/env python3
"""Stage 2 / S2.0.1 — Frontend skeleton smoke check.

Pure file inspection; does NOT require node_modules or `next build`.
Invoked via `npm run smoke` (package.json script) or `python3 smoke-check.py`.

Validates:
  1. All required skeleton files exist (package.json, tsconfig.json,
     next.config.js, .gitignore, README.md, app/layout.tsx, app/page.tsx,
     app/DemoBadge.tsx, app/provinces/{jiangsu,zhejiang,guangdong,sichuan,
     shandong}/page.tsx, lib/api.ts, lib/types.ts, lib/mock.ts).
  2. package.json declares next + react.
  3. tsconfig.json enables App Router conventions ("jsx": "preserve").
  4. app/layout.tsx renders a top banner keyed off IS_MOCK_MODE
     and reads NEXT_PUBLIC_USE_MOCK / NEXT_PUBLIC_API_BASE env vars.
  5. app/provinces/jiangsu/page.tsx imports DemoBadge from "../../DemoBadge".
  6. lib/mock.ts includes at least one observation row with
     lineage.is_demo === "true" (S1.18 sentinel pattern).
  7. lib/api.ts honours NEXT_PUBLIC_USE_MOCK switch (default true).

Exits 0 on full pass; non-zero on any missing/wrong file.
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent

REQUIRED_FILES = [
    "package.json",
    "tsconfig.json",
    "next.config.js",
    ".gitignore",
    "README.md",
    "app/layout.tsx",
    "app/page.tsx",
    "app/DemoBadge.tsx",
    "app/components/EvidenceChain.tsx",        # S2.7-a
    "app/provinces/jiangsu/page.tsx",
    "app/provinces/zhejiang/page.tsx",          # S2.7-a 路由壳
    "app/provinces/guangdong/page.tsx",         # S2.7-a2 路由壳
    "app/provinces/sichuan/page.tsx",           # S2.7-a2 路由壳
    "app/provinces/shandong/page.tsx",          # S2.7-a2 路由壳
    "lib/api.ts",
    "lib/types.ts",
    "lib/mock.ts",
    "lib/mock_evidence_chain.ts",               # S2.7-a mock
]


def fail(msg: str) -> None:
    print(f"❌ {msg}", file=sys.stderr)


def ok(msg: str) -> None:
    print(f"✅ {msg}")


def main() -> int:
    errors: list[str] = []

    # 1. Required files exist
    for rel in REQUIRED_FILES:
        path = ROOT / rel
        if not path.is_file():
            errors.append(f"missing required file: {rel}")
        else:
            ok(f"present: {rel}")

    if errors:
        for e in errors:
            fail(e)
        return 1

    # 2. package.json declares next + react
    pkg = json.loads((ROOT / "package.json").read_text(encoding="utf-8"))
    deps = pkg.get("dependencies", {})
    for dep in ("next", "react", "react-dom"):
        if dep not in deps:
            errors.append(f"package.json missing dependency: {dep}")
        else:
            ok(f"package.json declares {dep}={deps[dep]}")

    # 3. tsconfig.json enables App Router conventions
    ts = json.loads((ROOT / "tsconfig.json").read_text(encoding="utf-8"))
    compiler = ts.get("compilerOptions", {})
    if compiler.get("jsx") != "preserve":
        errors.append('tsconfig.json compilerOptions.jsx must be "preserve"')
    else:
        ok('tsconfig.json compilerOptions.jsx == "preserve"')

    # 4. app/layout.tsx renders top banner keyed off IS_MOCK_MODE
    layout = (ROOT / "app/layout.tsx").read_text(encoding="utf-8")
    if "IS_MOCK_MODE" not in layout:
        errors.append("app/layout.tsx does not reference IS_MOCK_MODE")
    elif "data-testid=\"mode-banner\"" not in layout:
        errors.append("app/layout.tsx banner is missing data-testid=\"mode-banner\"")
    else:
        ok("app/layout.tsx renders IS_MOCK_MODE banner")

    # 5. jiangsu page imports DemoBadge
    jiangsu = (ROOT / "app/provinces/jiangsu/page.tsx").read_text(encoding="utf-8")
    if 'from "../../DemoBadge"' not in jiangsu:
        errors.append("jiangsu/page.tsx does not import DemoBadge from '../../DemoBadge'")
    else:
        ok("jiangsu/page.tsx imports DemoBadge from '../../DemoBadge'")
    if "DemoBadge" not in jiangsu or "<DemoBadge" not in jiangsu:
        errors.append("jiangsu/page.tsx does not render <DemoBadge />")
    else:
        ok("jiangsu/page.tsx renders <DemoBadge />")

    # 5b. FIX per tasking 150 (Cursor 149 FAIL): reject any source-level
    # constant-failure gate that prevents the series table from rendering.
    # Specifically: static-segment pages must NOT compare `params.province`
    # (always undefined on a static route → always-false gate).
    #
    # Strip JS comments first — explanatory comments may legitimately mention
    # the bad pattern name. We only want to scan executable code.
    code = re.sub(r"//[^\n]*", "", jiangsu)
    code = re.sub(r"/\*.*?\*/", "", code, flags=re.DOTALL)
    if re.search(r"params\.province\s*[!=]==", code):
        errors.append(
            "jiangsu/page.tsx references params.province in executable code — "
            "static-segment route does not receive params; this gate is "
            "always false. Per tasking 150, drop it or move to [province]/ "
            "dynamic route."
        )
    else:
        ok("jiangsu/page.tsx has no params.province gate (FIX per 149/150)")
    if re.search(r"if\s*\(\s*params\.", code):
        errors.append(
            "jiangsu/page.tsx still branches on params.* in executable code — "
            "static-segment params are always undefined."
        )
    # 5c. Static-segment page must not declare PageProps with `params`.
    if re.search(r"interface\s+\w*PageProps\b", code):
        errors.append(
            "jiangsu/page.tsx declares a PageProps interface in executable "
            "code — remove if it still types params (static segment)."
        )
    else:
        ok("jiangsu/page.tsx has no PageProps interface (no stale params typing)")

    # 6. lib/mock.ts has at least one row with lineage.is_demo === "true"
    mock = (ROOT / "lib/mock.ts").read_text(encoding="utf-8")
    if not re.search(r'is_demo:\s*"true"', mock):
        errors.append("lib/mock.ts has no row with lineage.is_demo === 'true'")
    else:
        n = len(re.findall(r'is_demo:\s*"true"', mock))
        ok(f"lib/mock.ts has {n} is_demo=true sentinel rows")

    # 7. lib/api.ts honours NEXT_PUBLIC_USE_MOCK
    api = (ROOT / "lib/api.ts").read_text(encoding="utf-8")
    if "NEXT_PUBLIC_USE_MOCK" not in api:
        errors.append("lib/api.ts does not reference NEXT_PUBLIC_USE_MOCK")
    elif "USE_MOCK" not in api or "if (USE_MOCK)" not in api:
        errors.append("lib/api.ts does not branch on USE_MOCK")
    else:
        ok("lib/api.ts branches on NEXT_PUBLIC_USE_MOCK")

    # 8. S2.7-a — Six-segment evidence chain contract.
    #    Per docs/06 §2: 固定六段 CONDITION → COMMITMENT → INPUT → PROCESS
    #    → OUTPUT → OUTCOME_RISK；缺一不可。
    chain_src = (ROOT / "app/components/EvidenceChain.tsx").read_text(encoding="utf-8")
    expected_segments = [
        "CONDITION", "COMMITMENT", "INPUT", "PROCESS", "OUTPUT", "OUTCOME_RISK",
    ]
    for seg in expected_segments:
        if seg not in chain_src:
            errors.append(f"EvidenceChain.tsx missing segment key: {seg}")
    if not errors or all("EvidenceChain.tsx missing" not in e for e in errors):
        ok(f"EvidenceChain.tsx references all 6 fixed segments ({len(expected_segments)})")

    # 8b. Per tasking 168 §红线: 禁止评分 / 总分 / 排名。静态扫描
    # EvidenceChain.tsx 源码以确保没有数值化或排名化逻辑。
    chain_code = re.sub(r"//[^\n]*", "", chain_src)
    chain_code = re.sub(r"/\*.*?\*/", "", chain_code, flags=re.DOTALL)
    forbidden_patterns = [
        (r"\bscore\b", "score"),
        (r"\brating\b", "rating"),
        (r"\brank(?:ing)?\b", "rank"),
        (r"\btotal[_-]?score\b", "total_score"),
    ]
    for pat, label in forbidden_patterns:
        if re.search(pat, chain_code, re.IGNORECASE):
            errors.append(
                f"EvidenceChain.tsx contains forbidden term {label!r} "
                f"(per tasking 168 §红线: 禁止评分/总分/排名)"
            )
        else:
            ok(f"EvidenceChain.tsx has no forbidden {label!r} term")

    # 8c. Zhejiang route shell — verify it's a static-segment route with no
    # params.* branching (mirror of jiangsu check 5b).
    zhejiang = (ROOT / "app/provinces/zhejiang/page.tsx").read_text(encoding="utf-8")
    zj_code = re.sub(r"//[^\n]*", "", zhejiang)
    zj_code = re.sub(r"/\*.*?\*/", "", zj_code, flags=re.DOTALL)
    if re.search(r"params\.province\s*[!=]==", zj_code):
        errors.append(
            "zhejiang/page.tsx references params.province in executable code — "
            "static-segment route does not receive params."
        )
    else:
        ok("zhejiang/page.tsx has no params.province gate")
    if "EvidenceChain" not in zhejiang:
        errors.append("zhejiang/page.tsx does not render <EvidenceChain />")
    else:
        ok("zhejiang/page.tsx renders <EvidenceChain />")

    # 8c-2. S2.7-a2 — Guangdong / Sichuan / Shandong route shells get the same
    # treatment as Zhejiang: static segment, no params branching, EvidenceChain
    # mounted, and the slug wired to the mock lookup.
    for slug in ("guangdong", "sichuan", "shandong"):
        page = (ROOT / f"app/provinces/{slug}/page.tsx").read_text(encoding="utf-8")
        code = re.sub(r"//[^\n]*", "", page)
        code = re.sub(r"/\*.*?\*/", "", code, flags=re.DOTALL)
        if re.search(r"params\.province\s*[!=]==", code) or re.search(r"if\s*\(\s*params\.", code):
            errors.append(
                f"{slug}/page.tsx branches on params.* in executable code — "
                "static-segment route does not receive params."
            )
        else:
            ok(f"{slug}/page.tsx has no params.* gate")
        if "<EvidenceChain" not in page:
            errors.append(f"{slug}/page.tsx does not render <EvidenceChain />")
        else:
            ok(f"{slug}/page.tsx renders <EvidenceChain />")
        if f'getMockEvidenceChain("{slug}")' not in code:
            errors.append(
                f"{slug}/page.tsx does not call getMockEvidenceChain(\"{slug}\") — "
                "route shell would render another province's chain."
            )
        else:
            ok(f"{slug}/page.tsx resolves its own mock chain")

    # 8d. Mock chain — both Jiangsu (full) and Zhejiang (empty) must provide
    # all 6 segments; this guards against future "we only show 4 segments"
    # regressions.
    mock_chain = (ROOT / "lib/mock_evidence_chain.ts").read_text(encoding="utf-8")
    for province in ["jiangsu", "zhejiang"]:
        # Look for the key within the province's segments array.
        # We accept any order, but every key must appear.
        for seg in expected_segments:
            # Simple heuristic: count occurrences of `key: "SEG"` near the
            # province identifier. To be robust we just check that each segment
            # key appears at least 2 times (jiangsu + zhejiang) in the file.
            pass  # handled by the global count below
    seg_key_count = {seg: len(re.findall(rf'key:\s*"{seg}"', mock_chain)) for seg in expected_segments}
    for seg, n in seg_key_count.items():
        if n < 5:
            errors.append(
                f"mock_evidence_chain.ts: segment {seg} appears {n}x; "
                f"expected ≥5 (jiangsu + zhejiang + guangdong + sichuan + shandong)"
            )
    if all(seg_key_count[s] >= 5 for s in expected_segments):
        ok(f"mock_evidence_chain.ts has ≥5 of each of 6 segment keys")

    # 8e. S2.7-a2 §SCHEMA「首页 5 省列表链接须全部可点进真实路由（非死链）」.
    # Every slug advertised in MOCK_PROVINCE_LIST must resolve to both a mock
    # chain and an on-disk App Router page.
    list_block = mock_chain[mock_chain.index("MOCK_PROVINCE_LIST"):]
    listed_slugs = re.findall(r'slug:\s*"([a-z_]+)"', list_block)
    if len(listed_slugs) < 5:
        errors.append(
            f"MOCK_PROVINCE_LIST advertises {len(listed_slugs)} provinces; expected ≥5"
        )
    registry_block = mock_chain[
        mock_chain.index("MOCK_EVIDENCE_CHAIN_BY_PROVINCE"):
        mock_chain.index("MOCK_PROVINCE_LIST")
    ]
    for slug in listed_slugs:
        if not (ROOT / f"app/provinces/{slug}/page.tsx").is_file():
            errors.append(
                f"MOCK_PROVINCE_LIST lists {slug!r} but app/provinces/{slug}/page.tsx "
                "is missing — dead link on the home page."
            )
        elif f"{slug}:" not in registry_block:
            errors.append(
                f"MOCK_PROVINCE_LIST lists {slug!r} but MOCK_EVIDENCE_CHAIN_BY_PROVINCE "
                "has no entry — the page would throw at render time."
            )
        else:
            ok(f"province list entry {slug!r} resolves to a real route + mock chain")

    if errors:
        for e in errors:
            fail(e)
        return 1

    print("\n=== S2.0.1 + S2.7-a + S2.7-a2 skeleton smoke: PASS ===")
    return 0


if __name__ == "__main__":
    sys.exit(main())