# knife banner-config-extract — 集中 banner mode 派生 (2026-09-14)

> **刀号**: banner-config-extract
> **角色**: 架构师+执行端 merged (per 2026-08-31 21:50 豁免)
> **前置**: knife home-page-ux (8ee3223) 双推 PASS, knife env-config (8a36c43) 双推 PASS, knife api-base-fix (1fb9fc8) PASS
> **本件状态**: **READY FOR EXECUTION** (per user_ruling_banner-config-extract + Plan 1 已签, 本 session 2026-09-14)
> **关联**: knife home-page-ux forward scope §"knife banner-config-extract" line 201; knife api-base-fix plan forward scope; knife env-config 8a36c43 (typed env 集中化)

---

## Context (为什么做这件事)

### 用户质询 (本 session 2026-09-14)

> 「knife 669j-sketch memory update 30 → 15 HTTP 修正」 → 「下一刀」 → 「knife banner-config-extract P3 refactor (推荐)」 → 「签 user_ruling + 按 Plan 1 启动 (推荐)」

### 直答

knife home-page-ux (8ee3223) 在 page.tsx 加了 5 mode branches 在 `getIndicatorEmptyStateMessage(loadError)` 函数里 (`live-fetch-failed` / `static-mart` / `mart-fixture` / `mock` / `live-empty`), layout.tsx 也独立判定 `IS_MART_FIXTURE_MODE` / `IS_MOCK_MODE` 选 banner 背景色 + 文案. **mode 判定逻辑散落 2 文件, 不单一 source of truth.**

新 mode (e.g. "i18n 多语言 banner" / "tenant 多租户 banner") 加时需改 2 文件 + 维护 2 套 `IS_*_MODE` 引用链. **本刀把 mode 判定集中到 `lib/env.ts` 派生 `BANNER_MODE` 字符串**, layout.tsx 和 page.tsx 改用 typed string switch.

---

## Root Cause (根因分析)

### 当前 3 个 IS_*_MODE 散点

| 文件 | 引用 |
|---|---|
| `frontend/app/layout.tsx` | `IS_MOCK_MODE` (line 2, 21, 22, 53, 59, 63) + `IS_MART_FIXTURE_MODE` (line 2, 21, 51, 53, 59) — 9 引用 |
| `frontend/app/page.tsx` | `IS_MART_FIXTURE_MODE` (line 21, 67, 78) + `IS_MOCK_MODE` (line 20, 80, 83) + `IS_STATIC_MART_DATA_MODE` (line 22, 67, 78, 443, 453, 462) — 12 引用 |
| `frontend/lib/api.ts` | `IS_MOCK_MODE` + `IS_MART_FIXTURE_MODE` + `IS_STATIC_MART_DATA_MODE` re-export (line 120-122) |

**总计 24 引用 散在 3 文件**, 5 mode (含 `live-fetch-failed` / `live-empty`) 判定逻辑重复:
- layout.tsx: 3 mode (live/mock/mart-fixture), **漏 static-mart** (header banner 无 static-mart 提示)
- page.tsx: 5 mode (live-fetch-failed/static-mart/mart-fixture/mock/live-empty) — 完整

### 用户体验问题 (一致性问题)

| 现象 | 现有 |
|---|---|
| STATIC_MART_DATA 模式 | layout banner 仍按 live 处理 (无 static-mart 提示), page 空 state 提示 static-mart |
| LIVE-fetch-failed 模式 | layout banner 仍按 live 显示 ✅ (但 error 仅 console.warn, user 看不到), page 空 state 显示 error ✅ |

### 为什么之前没暴露

knife home-page-ux 修的是 page.tsx 的 user-facing 部分, layout banner 是 user 顶部 always-visible 的. 当 STATIC_MART 模式下, user 顶部 banner 说 "✅ LIVE MODE" 但 page 提示 "static-mart mode" — 自相矛盾.

---

## Fix (修复方案)

### 选定方案 (per user_ruling_banner-config-extract + Plan 1)

**A. 集中 mode 派生** (`frontend/lib/env.ts`)
- 新增 `BANNER_MODE` 导出, type: `"live" | "mock" | "mart-fixture" | "static-mart" | "live-fetch-failed"`
- 新增 `deriveBannerMode(loadError?: string | null)` 函数, priority order:
  1. `loadError` 存在 → `"live-fetch-failed"` (error context 优先)
  2. `IS_STATIC_MART_DATA_MODE` → `"static-mart"`
  3. `IS_MART_FIXTURE_MODE` → `"mart-fixture"`
  4. `IS_MOCK_MODE` → `"mock"`
  5. (else) → `"live"` (default; "live-empty" 是 page.tsx 内部 sub-state, 不计入 BANNER_MODE)

**B. lib/api.ts 兼容 re-export**
- `export { BANNER_MODE, deriveBannerMode } from "./env";` (与现有 IS_*_MODE re-export 模式一致)
- 保留 `IS_MOCK_MODE` / `IS_MART_FIXTURE_MODE` / `IS_STATIC_MART_DATA_MODE` re-export (向后兼容)

**C. layout.tsx 改用 BANNER_MODE switch**
- `bannerBackground()` 函数: switch on `BANNER_MODE` → color
  - `mart-fixture` → `#cfe2ff` (info blue)
  - `mock` → `#fff3cd` (warning yellow)
  - `static-mart` → `#e2e3e5` (gray, neutral)
  - `live` / `live-fetch-failed` → `#d4edda` (success green)
- JSX banner: switch on `BANNER_MODE` → 4 mode-aware 文案
  - 加 `data-static-mart={BANNER_MODE === "static-mart" ? "1" : "0"}` (与现有 `data-mart-fixture` 对称)
  - `live-fetch-failed` mode: banner 文案加 ⛔ icon + "FastAPI 不可达, 已降级" (但实际 layout 不会传 loadError, 所以 layout 仅显示 4 mode 不含 live-fetch-failed; loadError 仅 page.tsx 知道)

**D. page.tsx 改用 BANNER_MODE switch**
- `getIndicatorEmptyStateMessage(loadError)` 改用 `deriveBannerMode(loadError)` 一次:
  ```ts
  const mode = deriveBannerMode(loadError);
  switch (mode) {
    case "live-fetch-failed": return <LiveFetchFailedBanner error={loadError} />;
    case "static-mart": return <StaticMartBanner />;
    case "mart-fixture": return <MartFixtureBanner />;
    case "mock": return <MockBanner />;
    case "live": return <LiveEmptyBanner />; // includes "live-empty" sub-state
  }
  ```
- 或者保持 inline JSX (per Plan 1 "集成 page.tsx"), 用 switch on mode
- 简化: 5 mode 用 5 个 case in 1 switch

**E. DemoBanner.tsx 不动** (per Plan 1 注解 "接收 mode prop" 可选)
- 现有 4 demo 页 (seven-dim, research/m1-series, research/q1-2024-gdp, public-extracts) 用 `<DemoBanner reason="..." />` 传 reason 字符串
- 不强制加 `mode` prop (per Plan 2 风险), 4 demo 页 不依赖 BANNER_MODE (它们不是 mode-aware)

**F. 不删 `IS_*_MODE` boolean** (向后兼容)
- 保留 3 个 boolean export in lib/api.ts
- 仅 page.tsx + layout.tsx 改用 BANNER_MODE switch, 其他文件 (lib/api.ts consumers) 不动

### 修改文件清单 (4 改 + 1 新 = 5 文件)

| 路径 | 类型 | 改动 |
|---|---|---|
| `frontend/lib/env.ts` | **M** | + `BANNER_MODE` type + `deriveBannerMode()` 函数 (4 mode 判定) |
| `frontend/lib/api.ts` | **M** | + `BANNER_MODE` + `deriveBannerMode` re-export (兼容) |
| `frontend/app/layout.tsx` | **M** | `bannerBackground()` 改 switch on `BANNER_MODE`; JSX banner 文案 改 switch (4 mode) |
| `frontend/app/page.tsx` | **M** | `getIndicatorEmptyStateMessage(loadError)` 改用 `deriveBannerMode(loadError)` + switch (5 mode) |
| `docs/plans/knife-banner-config-extract.md` | **A** | 本 plan |

### 复用与依赖

- **复用** `lib/env.ts` 现有 `ENV.USE_MOCK` / `ENV.USE_MART_FIXTURE` / `ENV.MART_DATA_PATH` (typed boolean)
- **复用** `lib/api.ts` 现有 `IS_STATIC_MART_DATA_MODE` (= `isStaticMartDataEnabled()`)
- **不依赖** 其他 component 改动 (DemoBanner.tsx 不动)
- **不依赖** mart section / city completeness section
- **不依赖** FastAPI backend 改动 (0 backend 改动)

### 红线守门 (本件专属)

- ✓ **不变 user-facing 文案** (mode-aware 文案保持, 仅 switch 化)
- ✓ **不删 `IS_*_MODE` boolean** (向后兼容 24 引用)
- ✓ **不爬网** (本件 0 HTTP)
- ✓ **amend-first** (1 commit, 5 文件)
- ✓ **mock 链文件不删**
- ✓ **不主动 commit/push** (待用户授权)
- ✓ **不冒充 ops**
- ✓ **docs/81 零改动**
- ✓ **不取代 ops 自助提示** (banner 文案不暗示 user 自己重启 FastAPI / 改 deploy.sh)
- ✓ **保持 client-banner 单一来源** (layout banner + page placeholder 都用 BANNER_MODE, 不重复判定)
- ✓ **保持 SSR 兼容** (env 是 build-time injected, BANNER_MODE 是 derived const, server/client 一致)

---

## Verification (验证闭环)

### 5 红线 PASS (公网 https://china.3strategy.cc 2026-09-14 curl 实测, post-deploy)

| # | 红线 | 期望 | 验证方法 |
|---|---|---|---|
| 1 | **layout banner mode-aware** | HTML 含 `data-testid="mode-banner"` + 4 mode 之一 (LIVE/MOCK/MART/STATIC) | curl + python regex |
| 2 | **layout banner background 正确** | `style="background: #d4edda"` (live) 或 `#fff3cd` (mock) 或 `#cfe2ff` (mart-fixture) 或 `#e2e3e5` (static-mart) | curl + regex |
| 3 | **page placeholder mode-aware** | HTML 含 `data-testid="home-indicator-empty-state"` + 5 mode 之一 (live-fetch-failed/static-mart/mart-fixture/mock/live-empty) | curl + python regex |
| 4 | **`data-mart-fixture` + `data-static-mart` 属性正确** | mart-fixture mode: `data-mart-fixture="1" data-static-mart="0"`; static-mart mode: 反之 | curl + regex |
| 5 | **不破坏现有 5 红线** | `/cities/shenzhen` 仍 60 cells + hydration markers; `/` mart section + city completeness + 11 testids 仍渲染 | curl + python regex (per knife env-config §4 red lines) |

### 部署步骤 (per user_ruling_banner-config-extract 已签, 但 deploy 仍 user 授权)

```bash
# 1. local → scp newvps
scp frontend/lib/env.ts newvps:/opt/china-platform/repo/frontend/lib/env.ts
scp frontend/lib/api.ts newvps:/opt/china-platform/repo/frontend/lib/api.ts
scp frontend/app/layout.tsx newvps:/opt/china-platform/repo/frontend/app/layout.tsx
scp frontend/app/page.tsx newvps:/opt/china-platform/repo/frontend/app/page.tsx

# 2. build
ssh newvps 'cd /opt/china-platform/repo/frontend && rm -rf .next && npm run build'

# 3. restart
ssh newvps 'sudo kill -TERM <old_pid> 2>/dev/null; sudo systemctl restart china-platform-frontend'

# 4. verify (5 红线)
curl -s "https://china.3strategy.cc/" -o /tmp/banner.html
python3 -c "
import re
with open('/tmp/banner.html') as f: html = f.read()
checks = [
    ('mode-banner testid', r'data-testid=\"mode-banner\"', 1),
    ('mart-fixture attr', r'data-mart-fixture=\"[01]\"', 1),
    ('static-mart attr', r'data-static-mart=\"[01]\"', 1),
    ('indicator-empty-state testid', r'data-testid=\"home-indicator-empty-state\"', 0 or 1),
    ('mart-row-count', r'data-testid=\"mart-row-count\"', 1),
    ('home-city-completeness-*', r'data-testid=\"home-city-completeness-[a-z_]+\"', 11),
]
"
```

### 不宣称

- ❌ 不宣布 banner-config-extract PASS — 仅 DEPLOYED + 5/5 红线 + 公网实测后登记
- ❌ 不冒充 ops
- ❌ 不回写 ops 文件
- ❌ 不爬网
- ❌ 不主动 commit

---

## 风险与缓解

| 风险 | 缓解 |
|---|---|
| **layout banner 文案改后 UI 差异** | 文案保持 mode-aware, 仅 switch 化, 不改文字 |
| **`deriveBannerMode` SSR 兼容性** | 函数依赖 build-time injected `process.env.NEXT_PUBLIC_*`, SSR/client 一致 |
| **`deriveBannerMode` 调用开销** | 纯函数无 IO, O(1), 每 page render 调 1 次 |
| **`IS_*_MODE` 删除后其他文件 import 失败** | **不删**, 仅加 BANNER_MODE re-export, 3 boolean 保留 |
| **`data-static-mart` 属性加后 e2e test 引用失败** | smoke-check.py 现有 grep `data-testid="mode-banner"` 不依赖 data-static-mart, 加属性向后兼容 |
| **mode priority 变化导致 UX 不一致** | 严格按 Plan: loadError > static-mart > mart-fixture > mock > live (与现有 page.tsx 顺序一致) |

---

## 预估 commits 结构 (1 commit)

```
<hash>  refactor(banner-config-extract): 集中 BANNER_MODE 派生, layout + page switch on typed string
  - frontend/lib/env.ts: + BANNER_MODE type + deriveBannerMode(loadError?) 函数 (4 mode 判定)
  - frontend/lib/api.ts: + BANNER_MODE + deriveBannerMode re-export (兼容 IS_*_MODE)
  - frontend/app/layout.tsx: bannerBackground() + JSX banner 改 switch on BANNER_MODE (4 mode)
  - frontend/app/page.tsx: getIndicatorEmptyStateMessage(loadError) 改用 deriveBannerMode(loadError) + switch (5 mode)
  - docs/plans/knife-banner-config-extract.md: 本 plan
```

预估总: **1 commit** + 1 plan 文件 + 4 源文件改动

预估部署耗时:
- Code 改: ~10min
- scp + build + restart: ~3min
- 5 红线 curl + python verify: ~3min
- commit + push via Clash proxy: ~1min (待用户授权)

---

## Forward scope (post-banner-config-extract)

- **knife banner-i18n**: BANNER_MODE 派生 + i18n 文案 (per docs/46 i18n 路线图) (P2)
- **knife banner-tenant**: 多租户 BANNER_MODE 派生 (per 582 SaaS 方向) (P3)
- **knife 669b-i batch9 拓展**: 继 669b-i batch1~8 拓展 (30/40 city?) (P2, 需查 hongheiku 新 data availability)
- **knife 622-3 红线 校验**: 守红线-3 数据审计脚本 (per 669j program partial cells) (P2)

---

## 链接

- 关联 knife home-page-ux (8ee3223) — page.tsx 5 mode branches 起源, 本刀集中化
- 关联 knife env-config (8a36c43) — typed env 集中化, BANNER_MODE 是其延伸
- 关联 knife api-base-fix (1fb9fc8) — banner-config-extract 计划来源 (per plan forward scope)
- 关联 memory [[china-platform-env-config-closure]] — env 集中化
- 关联 memory [[china-platform-home-page-ux-closure]] — page placeholder 5 mode 起源
- 关联 memory [[china-platform-fastapi-missing-on-newvps]] — 8001 端口实证

— End knife banner-config-extract plan (BANNER_MODE 集中派生 + 5 文件 switch 化, 2026-09-14, READY FOR EXECUTION) —