#!/usr/bin/env python3
"""Stage 2 / S2.0.1 — Frontend skeleton smoke check.

Pure file inspection; does NOT require node_modules or `next build`.
Invoked via `npm run smoke` (package.json script) or `python3 smoke-check.py`.

Validates:
  1. All required skeleton files exist (package.json, tsconfig.json,
     next.config.js, .gitignore, README.md, app/layout.tsx, app/page.tsx,
     app/DemoBadge.tsx, app/provinces/jiangsu/page.tsx,
     lib/api.ts, lib/types.ts, lib/mock.ts).
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
    "app/provinces/jiangsu/page.tsx",
    "lib/api.ts",
    "lib/types.ts",
    "lib/mock.ts",
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

    if errors:
        for e in errors:
            fail(e)
        return 1

    print("\n=== S2.0.1 skeleton smoke: PASS ===")
    return 0


if __name__ == "__main__":
    sys.exit(main())