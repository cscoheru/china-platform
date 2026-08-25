# CEGR Frontend — Stage 2 / S2.0.1 Skeleton

> **Status**: skeleton only. No real SHA-locked data; mock-driven per `docs/34` §4.1 序 1 + tasking `146` §SCHEMA.

## What this is

Next.js 14 (App Router) skeleton that:

1. **Consumes the existing FastAPI read-only service** (S1.10) — no new write API.
2. **Has a mock switch** (`NEXT_PUBLIC_USE_MOCK=true`) so pages render without a DB.
3. **Distinguishes DEMO vs future real SHA** at the render layer (`is_demo` badge on every observation row).
4. Ships **two pages**: home + one provincial observation page (`/provinces/jiangsu`).

The skeleton deliberately stops at "1 省级观察页壳" per tasking `146` §NOW.2. S2.1-S2.6 schema work and 5-province rollout come later.

## Run

```bash
# 1. install (no build needed for smoke check)
cd frontend
npm install

# 2. dev (mock mode — no FastAPI / Postgres required)
NEXT_PUBLIC_USE_MOCK=true npm run dev
# → http://localhost:3000

# 3. dev (real FastAPI)
NEXT_PUBLIC_USE_MOCK=false \
NEXT_PUBLIC_API_BASE=http://localhost:8000 \
npm run dev

# 4. smoke (no Node required — pure file inspection)
npm run smoke    # → exits 0 if skeleton is structurally intact
```

## Mock vs real

| env var | default | meaning |
|---|---|---|
| `NEXT_PUBLIC_USE_MOCK` | `true` | When `true`, frontend returns hard-coded mock data. When `false`, fetches from `${NEXT_PUBLIC_API_BASE}/api/...`. |
| `NEXT_PUBLIC_API_BASE` | `http://localhost:8000` | FastAPI root. Default matches `backend/src/china_platform/api/main.py` (uvicorn on 8000). CORS already permits `http://localhost:3000` (`backend/src/china_platform/api/config.py`). |

## is_demo vs real SHA

Every observation row carries `lineage.is_demo` (from S1.18 sentinel pattern). The frontend renders an explicit `<DemoBadge />` next to any row where `lineage.is_demo === true`. This satisfies tasking `146` §SCHEMA requirement: "须能区分/展示 `is_demo` vs 未来真实 SHA（文案/角标即可）".

When S2.0.2 lands a real SHA-locked Jiangsu sample, the same `DemoBadge` component will automatically hide itself (because real rows have `is_demo: false`). No frontend code changes needed.

## What is NOT in this skeleton

- ❌ No S2.1 person/tenure/position schema — out of scope per docs/34 §4.2 (parallel, not on critical path)
- ❌ No S2.2-S2.6 entity tables — same
- ❌ No 七维度观察卡 UI (S2.8) — comes after S2.1-S2.6 land
- ❌ No 同类地区对比 (S2.9) — comes after 5 省级页面 ship
- ❌ No DSH / pgvector / 官员评分 / OCR production — red lines per docs/08 §3.3 + PRD

## Smoke check

`smoke-check.py` is a Python script (run via `npm run smoke` — uses system `python3`). It validates:

- All required files exist
- `package.json` declares `next` and `react`
- `tsconfig.json` enables App Router conventions (`"jsx": "preserve"`)
- `app/layout.tsx` exists with the demo banner
- `app/provinces/jiangsu/page.tsx` imports `<DemoBadge />`
- `lib/mock.ts` includes `is_demo: true` in at least one row
- `lib/api.ts` honours `NEXT_PUBLIC_USE_MOCK` switch

It does NOT execute `next build` (avoids needing `node_modules` in the smoke env).

## File map

```
frontend/
├── package.json
├── tsconfig.json
├── next.config.js
├── .gitignore
├── README.md                  ← you are here
├── smoke-check.py             ← run via `npm run smoke`
├── app/
│   ├── layout.tsx             ← root layout, top banner
│   ├── page.tsx               ← home (indicator list, mock or real)
│   └── provinces/
│       └── jiangsu/
│           └── page.tsx       ← 省级观察页壳
└── lib/
    ├── api.ts                 ← typed fetcher w/ NEXT_PUBLIC_USE_MOCK switch
    ├── types.ts               ← IndicatorSeriesResponse / IndicatorSeriesPoint shapes
    └── mock.ts                ← demo data, including is_demo=true Jiangsu GDP sample
```

— End —