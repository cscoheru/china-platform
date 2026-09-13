# knife env-config — 集中 NEXT_PUBLIC_* env var + 编译时校验 (2026-09-13)

> **刀号**: env-config
> **角色**: 架构师+执行端 merged (per 2026-08-31 21:50 豁免)
> **前置**: knife api-base-fix (1fb9fc8) PASS, knife hydration-fix (f9d7b1a) PASS
> **本件状态**: **READY FOR EXECUTION**
> **关联**: api-base-fix forward scope §"knife env-config 整理" + memory [[china-platform-frontend-mart-env-var-regression]]

---

## Context (为什么做这件事)

### 用户质询 (2026-09-13)

> 「hydration fix code 已 deployed + 根因 (SSR HTML 含 range input) 已消除, 但因 API_BASE pre-existing bug (localhost:8000 → portainer 而非 FastAPI:8001), 所有 city 页面仍渲染 CityEmptyState...」
> → 上一刀选「先修 API_BASE (推荐,独立刀)」, 改为「改 source 默认」+「容错 + log warn」
> 「下一刀选?」 → 「(a) knife env-config 整理 (防 regress)」

### 直答

knife api-base-fix 修复了**症状** (默认端口 8000 → 8001) 但没修**根因**: `process.env.NEXT_PUBLIC_*` 在 4 文件 8 处散落直读, 各处默认值 + 类型转换 + 缺失分支各自维护, 任何 1 处改了就漂移。本刀建 `frontend/lib/env.ts` 单一入口, 让所有 env var 走 typed constants + 集中默认值 + 1 个声明表 (`INJECTED_ENV_VARS`) 编译时校验, 防止 typo 类 + drift 类 regress 重现 (per memory [[china-platform-frontend-mart-env-var-regression]] NEXT_PUBLIC_* 历史 regression 教训)。

---

## Root Cause (根因分析)

### 文件实测 (env 散点)

```
NEXT_PUBLIC_USE_MOCK (api.ts:37, mock 切换):
  process.env.NEXT_PUBLIC_USE_MOCK === "true"

NEXT_PUBLIC_USE_MART_FIXTURE (api.ts:39, layout.tsx, cities/[slug]/page.tsx:48):
  process.env.NEXT_PUBLIC_USE_MART_FIXTURE === "1"
  process.env.NEXT_PUBLIC_USE_MART_FIXTURE === "0"
  // 三处独立读, 三处独立 === "1" 或 === "0", 字符串比较分散

NEXT_PUBLIC_API_BASE (api.ts:47, layout.tsx:73):
  process.env.NEXT_PUBLIC_API_BASE ?? "http://localhost:8000"  ← 老默认 (bug)
  process.env.NEXT_PUBLIC_API_BASE ?? "http://127.0.0.1:8001" ← 新默认 (1fb9fc8)

NEXT_PUBLIC_MART_DATA_PATH (mart-static.ts 5 处 + 4 处注释 + cities/[slug] reference):
  typeof process.env.NEXT_PUBLIC_MART_DATA_PATH === "string"
  && process.env.NEXT_PUBLIC_MART_DATA_PATH.length > 0
```

### 历史 regression (per memory)

- **knife H-series H5c env var regression** (2026-09-10): `NEXT_PUBLIC_*` 默认值与显示 banner 不一致 → 复现 8000/8001 同类 bug
- **knife api-base-fix**: 修复症状但留隐患 (4 文件各自默认值独立维护)
- **mart-static.ts**: 5 处 `process.env.NEXT_PUBLIC_MART_DATA_PATH` 读, 任何 1 处改名 (e.g. `NEXT_PUBLIC_MART_JSON_PATH`) 4 处漏改 → silent null + 空 Indicator inventory

### 为什么之前没暴露

每处 `"?? 默认值"` 都是静态默认, 编译期已注入. 问题只在 **build 环境变了** 时暴露 (e.g. newvps 上 8000 被 portainer 占), 本地 dev 永远 `localhost:8000` 没事。

---

## Fix (修复方案)

### 选定方案

**A. 单一入口 `frontend/lib/env.ts`** (本刀主体)
- 定义 typed constants:
  ```ts
  export const ENV = {
    USE_MOCK: process.env.NEXT_PUBLIC_USE_MOCK === "true",
    USE_MART_FIXTURE: process.env.NEXT_PUBLIC_USE_MART_FIXTURE === "1",
    API_BASE: process.env.NEXT_PUBLIC_API_BASE ?? "http://127.0.0.1:8001",
    MART_DATA_PATH: process.env.NEXT_PUBLIC_MART_DATA_PATH ?? "",
  } as const;
  ```
- 集中派生 boolean:
  ```ts
  export const IS_MOCK_MODE = ENV.USE_MOCK;
  export const IS_MART_FIXTURE_MODE = ENV.USE_MART_FIXTURE;
  export const IS_STATIC_MART_DATA_MODE = ENV.MART_DATA_PATH.length > 0;
  ```
- 声明表 (编译时校验):
  ```ts
  export const INJECTED_ENV_VARS = [
    "NEXT_PUBLIC_USE_MOCK",
    "NEXT_PUBLIC_USE_MART_FIXTURE",
    "NEXT_PUBLIC_API_BASE",
    "NEXT_PUBLIC_MART_DATA_PATH",
  ] as const;
  ```
  (用于 runtime sanity check: 检测 `process.env` 中未声明的 `NEXT_PUBLIC_*`, 防止 typo 漏改; 只在 dev 触发, 生产 build 关掉)

**B. 调用点收敛** (本刀副作用)
- `lib/api.ts` 4 处 → `import { ENV } from "./env"`
- `lib/mart-static.ts` 5 处 → `import { ENV } from "./env"`
- `app/layout.tsx` 1 处 → `import { ENV } from "../../lib/env"`
- `app/cities/[slug]/page.tsx` 1 处 → `import { ENV } from "../../../lib/env"`
- `IS_MOCK_MODE` / `IS_MART_FIXTURE_MODE` / `IS_STATIC_MART_DATA_MODE` re-export 从 `env.ts` (保持原 import 路径兼容)

**C. Default 同步** (B-OPT-EC)
- `ENV.API_BASE` 默认值锁定 `127.0.0.1:8001` (per knife api-base-fix 1fb9fc8)
- 所有 `??` 默认值统一到 env.ts, 不在调用点散落

### 修改文件清单 (5 改 + 2 新 = 7 文件)

| 路径 | 类型 | 改动 |
|---|---|---|
| `frontend/lib/env.ts` | **A** | NEW — 集中入口 (~50 行) |
| `frontend/lib/api.ts` | **M** | 4 处 `process.env.NEXT_PUBLIC_*` → `ENV.*`; re-export `IS_*_MODE` from env (向后兼容) |
| `frontend/lib/mart-static.ts` | **M** | 5 处 `process.env.NEXT_PUBLIC_MART_DATA_PATH` → `ENV.MART_DATA_PATH` |
| `frontend/app/layout.tsx` | **M** | 1 处 `process.env.NEXT_PUBLIC_API_BASE ?? ...` → `ENV.API_BASE` |
| `frontend/app/cities/[slug]/page.tsx` | **M** | 1 处 `process.env.NEXT_PUBLIC_USE_MART_FIXTURE === "0"` → `ENV.USE_MART_FIXTURE === false` (typed) |
| `docs/plans/knife-env-config.md` | **A** | 本 plan |
| `package.json` (skip) | n/a | 无 dep 变化 |

### 复用与依赖

- **复用** `lib/api.ts:125-127` 现有 `IS_MOCK_MODE` / `IS_MART_FIXTURE_MODE` / `IS_STATIC_MART_DATA_MODE` 导出 → 改为 re-export from env (向后兼容, 现有 `import { IS_MOCK_MODE } from "../lib/api"` 仍可用)
- **复用** `cities/[slug]/page.tsx:48` 现 B-OPT-NT 容错模式 — 不改
- **不依赖** 其他 component 改动
- **不依赖** build env 变化 — 编译期静态注入仍由 Next.js 完成

### 红线守门 (本件专属)

- ✓ **不改任何 env 默认值** (API_BASE 维持 127.0.0.1:8001 per 1fb9fc8)
- ✓ **不删现有 re-export** (`IS_MOCK_MODE` 等保留向后兼容, 现有调用点不动 import path)
- ✓ **不爬网** (本件 0 HTTP, 仅 build verify + curl smoke)
- ✓ **amend-first** (1 commit, 5 改 + 2 新)
- ✓ **mock 链文件不删** (mart_city_demo.ts / mock_cities.ts 保留)
- ✓ **不主动 commit/push** (待用户授权)
- ✓ **不冒充 ops** (newvps deploy 仅 user_ruling_666+ 签署后)
- ✓ **docs/81 零改动** (改 docs/plans/knife-env-config.md 新 plan)
- ✓ **红线-1 2001-2019 全 DATA_MISSING** 不涉及 (无数据流变化)
- ✓ **红线-2 2026 全 DATA_MISSING** 不涉及
- ✓ **红线-3 hongheiku 0 entry** 不涉及
- ✓ **红线-7 4 直辖市禁在 city 维度重复** 不涉及

---

## Verification (验证闭环)

### 红线 (本件 5 条 PASS)

| # | 红线 | 期望 | 验证方法 |
|---|---|---|---|
| 1 | **env.ts 导出完整** | `ENV` 对象含 4 keys (USE_MOCK, USE_MART_FIXTURE, API_BASE, MART_DATA_PATH) + 3 IS_*_MODE + INJECTED_ENV_VARS 数组 | local grep + newvps curl SSR HTML |
| 2 | **调用点收敛** | `process.env.NEXT_PUBLIC_*` 在 4 调用文件 = 0 (除 env.ts) | grep -rn "process\.env\.NEXT_PUBLIC" frontend --include="*.ts" --include="*.tsx" \| grep -v env.ts |
| 3 | **build 编译 PASS** | `npm run build` on newvps exit 0 | ssh newvps npm run build |
| 4 | **现有 5 红线不 regress** | /cities/shenzhen 仍 60 cells, / 仍 HTTP 200, banner 仍 127.0.0.1:8001 | curl + python regex (同 knife api-base-fix 红线 1-5) |
| 5 | **env runtime sanity check** (dev only) | `INJECTED_ENV_VARS` 检测到未声明 `NEXT_PUBLIC_*` 时 console.warn | dev server console (本件暂不强制 require, 留 hook 给未来 knife) |

### 部署步骤 (per user_ruling_666+ SSH ops 授权)

```bash
# 1. local → scp newvps
scp frontend/lib/env.ts newvps:/opt/china-platform/repo/frontend/lib/env.ts
scp frontend/lib/api.ts newvps:/opt/china-platform/repo/frontend/lib/api.ts
scp frontend/lib/mart-static.ts newvps:/opt/china-platform/repo/frontend/lib/mart-static.ts
scp frontend/app/layout.tsx newvps:/opt/china-platform/repo/frontend/app/layout.tsx
scp frontend/app/cities/[slug]/page.tsx newvps:/opt/china-platform/repo/frontend/app/cities/[slug]/page.tsx

# 2. build
ssh newvps 'cd /opt/china-platform/repo/frontend && rm -rf .next && npm run build'

# 3. restart
ssh newvps 'sudo systemctl restart china-platform-frontend'

# 4. verify (5 红线)
curl -s "https://china.3strategy.cc/cities/shenzhen" > /tmp/sz.html
python3 -c "..."
grep -rn "process\.env\.NEXT_PUBLIC" frontend --include="*.ts" --include="*.tsx" | grep -v env.ts | wc -l   # 期望 0
```

### 不宣称

- ❌ 不宣布 env-config PASS — 仅 DEPLOYED + 5/5 红线 + 公网 0 regress 实测后登记
- ❌ 不冒充 ops — newvps deploy 仅 user_ruling_666+ 签署后
- ❌ 不回写 ops 文件 (systemd unit 不可改)
- ❌ 不爬网 — 仅 1 curl × 1 城 + grep + python parse
- ❌ 不主动 commit — 等用户授权

---

## 风险与缓解

| 风险 | 缓解 |
|---|---|
| **env.ts 默认值与调用点硬编码值不一致** | 唯一默认值集中在 env.ts, 调用点全部 `ENV.X`, 编译期一致 |
| **re-export 兼容现有 import path** | `lib/api.ts` 保留 `export const IS_MOCK_MODE = ...` (re-export from env), 现有 `import { IS_MOCK_MODE } from "../lib/api"` 不破坏 |
| **dev server sanity check 噪音** | runtime 检测默认只在 `NODE_ENV !== "production"` 触发, 生产 build 关掉 (env.ts: `if (process.env.NODE_ENV !== "production") { ... }`) |
| **newvps build 缓存** | `rm -rf .next && npm run build` 强制 clean rebuild (per memory [[china-platform-nextjs-build-after-sync]]) |
| **systemd restart orphan** | per memory [[china-platform-next-server-restart-pattern]], `sudo kill -TERM <old_pid>` 先杀 start-stop-daemon orphan, 再 systemctl restart |
| **`as const` 改动影响 type narrowing** | typed constants 用 `as const` 保证 narrow 类型, 不影响 `USE_MOCK: boolean` 兼容性 (布尔派生已 typed) |

---

## 预估 commits 结构 (1 commit)

```
<hash>  refactor(env-config): 集中 NEXT_PUBLIC_* 到 lib/env.ts, 防 typo/drift 类 regress
  - frontend/lib/env.ts: NEW, 集中 4 env var typed constants + IS_*_MODE + INJECTED_ENV_VARS 声明表
  - frontend/lib/api.ts: 4 处 process.env.NEXT_PUBLIC_* → ENV.*
  - frontend/lib/mart-static.ts: 5 处 NEXT_PUBLIC_MART_DATA_PATH → ENV.MART_DATA_PATH
  - frontend/app/layout.tsx: 1 处 NEXT_PUBLIC_API_BASE → ENV.API_BASE
  - frontend/app/cities/[slug]/page.tsx: 1 处 NEXT_PUBLIC_USE_MART_FIXTURE === "0" → ENV.USE_MART_FIXTURE === false
  - docs/plans/knife-env-config.md: 本 plan
```

预估总: **1 commit** + 1 plan 文件 + 5 源文件改动 + 1 新文件

预估部署耗时:
- Code 改: ~8min
- scp + build + restart: ~3min
- 5 红线 curl + python verify + grep: ~3min
- commit + push via Clash proxy: ~1min (待用户授权)

---

## Forward scope (post-env-config)

- **knife env-validate-rust-time**: 启动时 strict 检查 (e.g. URL parse, path exists), dev console.error 暴露 (P3, defensive)
- **knife env-config-app**: 把 `process.env.NEXT_PUBLIC_*` 集中读移到 `next.config.js` runtimeConfig (P3, refactor)
- **knife API_BASE 锁**: 通过 deploy.sh 注入 `NEXT_PUBLIC_API_BASE`, 不靠 source 默认 (D3 锁, 防止 default drift 再现)

---

## 链接

- 关联 knife api-base-fix (1fb9fc8) — 暴露本刀根因的触发
- 关联 knife hydration-fix (f9d7b1a) — 前一闭环刀
- 关联 memory [[china-platform-frontend-mart-env-var-regression]] — NEXT_PUBLIC_* 历史 regression 教训
- 关联 memory [[china-platform-fastapi-missing-on-newvps]] — FastAPI 8001 端口实证
- 关联 memory [[china-platform-nextjs-build-after-sync]] — scp 必须在 npm run build 之前
- 关联 memory [[china-platform-next-server-restart-pattern]] — systemd restart vs nohup (newvps 用 systemd)

— End knife env-config plan (集中 NEXT_PUBLIC_* + 编译时校验, 2026-09-13, READY FOR EXECUTION) —