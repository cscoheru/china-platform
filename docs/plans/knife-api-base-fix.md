# knife api-base-fix — 修 API_BASE 默认端口 + 首页容错 (2026-09-13)

> **刀号**: api-base-fix
> **角色**: 架构师+执行端 merged (per 2026-08-31 21:50 豁免)
> **前置**: knife H-series (commits 8d1e399/dc32d28/24b3ac2/b6eba49) H1+H2+H3 已 deployed, knife H3-verify (d0943a4) PASS, knife hydration-fix (deployed, not yet committed) 卡在 SSR fetch 命中 portainer
> **本件状态**: **READY FOR EXECUTION** — user 2026-09-13 选定「先修 API_BASE (推荐,独立刀)」+ 「改 source 默认」+ 「容错 + log warn」
> **关联**: knife H-series plan + B-OPT-NT (b6eba49) + H3-verify (d0943a4) + knife hydration-fix (deployed, pending verify)

---

## Context (为什么做这件事)

### 用户质询 (2026-09-13)

> 「hydration fix code 已 deployed + 根因 (SSR HTML 含 range input) 已消除, 但因 API_BASE pre-existing bug (localhost:8000 → portainer 而非 FastAPI:8001), 所有 city 页面仍渲染 CityEmptyState, 无法端到端验证 0 warning. 下一刀?」
> 「先修 API_BASE (推荐,独立刀)」

### 直答

knife hydration-fix 代码 + 部署均完成, 但**所有 city 页面** (`/cities/{slug}`) **都渲染 CityEmptyState** 而非 CityTimeseriesLive, **首页** (`/`) **HTTP 500**。根因: `frontend/lib/api.ts:43` `API_BASE` 默认 `http://localhost:8000`, 但 newvps 上 8000 端口被 portainer 占用 (返 404), FastAPI 实际在 `127.0.0.1:8001` (docker-proxy 映射 china-platform-api 容器 8000→host 8001)。此 bug 在 H-series 部署后 (SSR fetch 才实际触发) 才暴露, 之前一直隐藏。

修这条: 默认端口翻到 8001 (匹配现实) + 首页加 try/catch 容错, 让 H3 + hydration 验证能跑通。

---

## Root Cause (根因分析)

### 文件实测

1. `frontend/lib/api.ts:43`:
   ```ts
   const API_BASE = process.env.NEXT_PUBLIC_API_BASE ?? "http://localhost:8000";
   ```
   默认端口 = **8000**。next-server SSR fetch 命中 `localhost:8000` → portainer 返 404 → 抛错。

2. `frontend/app/layout.tsx:73`:
   ```tsx
   FastAPI at {process.env.NEXT_PUBLIC_API_BASE ?? "http://localhost:8000"}.
   ```
   client banner 显示同一默认 — 改 source 需同步。

3. `frontend/app/page.tsx:33`:
   ```ts
   const data = await listIndicators();
   ```
   无 try/catch。listIndicators() throws on non-2xx → Next.js server component 抛错 → `/` HTTP 500。

4. `frontend/app/cities/[slug]/page.tsx:74-118` (对照参考): **已有 B-OPT-NT try/catch** — 404 走 EmptyState, 其他失败 fallback mart_city_demo fixture。首页缺这一层。

### 端口实证 (newvps 2026-09-13)

```
localhost:8000 → portainer (portainer/portainer-ce, HTTP 404 "Not found")
                  ↑ API_BASE 默认命中
127.0.0.1:8001 → china-platform-api (FastAPI, HTTP 200, 60 cells SHENZHEN 2020-2025)
                  ↑ 实际 FastAPI 端口
```

`/api/city-timeseries/GUANGDONG_SHENZHEN?year_start=2020&year_end=2025`:
- 8000: HTTP 404 9b "Not found"
- 8001: HTTP 200 26944b 60 points

### `listCityDataCompleteness` 已容错

`frontend/lib/api.ts:282-318` 用 `Promise.allSettled`, 单城失败 → error row, 不阻断整表。**不需要改**。修复后 9/10 城应真实计数 (nantong 守红线-3 仍 0/60)。

### 为什么之前没暴露

H-series 之前: SSR 只调 `getProvinceTimeSeries` (S1.18 mock + H1 之前没 SSR city)。knife H-series 部署后 SSR 调 `getCityTimeSeries` + `listIndicators` + `listCityDataCompleteness`, 全都过 `API_BASE` → 第一次暴露。

公网 curl `https://china.3strategy.cc/cities/shenzhen` 不暴露因为 nginx `/api/*` → `127.0.0.1:8001` 直连 FastAPI, 绕过 next-server 内部 fetch。

---

## Fix (修复方案)

### 选定方案

**A. Source 默认翻 8000 → 8001** (per user 选定)
- `api.ts:43` 默认从 `http://localhost:8000` 改为 `http://127.0.0.1:8001`
- `layout.tsx:73` 默认同步翻, 保证 client banner 与实际 fetch URL 一致
- 不动 deploy.sh / systemd unit (现有 build 流程无需改 env var)
- local dev: 仍可设 `NEXT_PUBLIC_API_BASE=...` 覆盖

**B. 首页容错** (per user 选定)
- `page.tsx:33` 包裹 try/catch, 仿 `cities/[slug]/page.tsx:74-118` B-OPT-NT 模式
- catch 块: `console.warn` + 返空 `{ indicators: [] }`, 不 throw
- mart section (`getMartProvinceGdp2024` 走 static JSON, 不 fetch) 不需改
- city completeness (`listCityDataCompleteness` 内部 allSettled) 不需改

### 修改文件清单 (3 文件改 + 1 plan 新 = 4 文件)

| 路径 | 类型 | 改动 |
|---|---|---|
| `frontend/lib/api.ts` | **M** (1 行) | `API_BASE` 默认 `localhost:8000` → `127.0.0.1:8001` |
| `frontend/app/layout.tsx` | **M** (1 行) | client banner 默认同步翻 |
| `frontend/app/page.tsx` | **M** (8-12 行) | `await listIndicators()` 包裹 try/catch, 错误时 console.warn + 空 indicators |
| `docs/plans/knife-api-base-fix.md` | **A** | 本文件 |

### 复用与依赖

- 复用 `cities/[slug]/page.tsx:74-118` B-OPT-NT try/catch 模式 (consistency)
- 复用 `listCityDataCompleteness` 的 allSettled 行为 (无需改)
- 复用 `getMartProvinceGdp2024` static JSON 路径 (next-server 不需要 FastAPI 也能渲染 mart section)
- 不依赖其他 component 改动

### 红线守门 (本件专属)

- ✓ **不擅自增减 10 城名单** (page.tsx `CITY_SLUG_LIST` 不动)
- ✓ **DATA_MISSING 显式「数据缺失」** (`listCityDataCompleteness` already 容错, 修后 nantong 仍守红线-3 显示 "—")
- ✓ **不爬网** (本件 0 HTTP, 修复后 1 curl + python regex 验 5 红线)
- ✓ **amend-first** (1 commit, 3 改 + 1 新)
- ✓ **mock 链文件不删** (mart_city_demo.ts / mock_cities.ts 保留)
- ✓ **不主动 commit/push** (待用户授权 "commit + push")
- ✓ **不冒充 ops** (newvps deploy 仅 user_ruling_666+ 签署后)
- ✓ **docs/81 零改动** (改 docs/plans/knife-api-base-fix.md 新 plan)

---

## Verification (验证闭环)

### 5 红线 PASS (公网 https://china.3strategy.cc 2026-09-13 curl 实测, post-deploy)

| # | 红线 | 期望 | 验证方法 |
|---|---|---|---|
| 1 | **城市页改走 live mart** | `/cities/shenzhen` HTTP 200 + `data-testid="city-timeseries-live"` 命中 + 60 cell-* testids | curl + python regex |
| 2 | **971 sync 后 4 副省级活** | `/cities/suzhou` / `/cities/wuxi` / `/cities/ningbo` / `/cities/dongguan` 全部 `city-timeseries-live` testid 命中 | curl + python regex |
| 3 | **首页 HTTP 200 (不 500)** | `/` HTTP 200 + 11 home-city-completeness-* testids (1 header + 10 cities) | curl + python regex |
| 4 | **首页 H3 真实计数** | suzhou 35, wuxi 35, ningbo 44, dongguan 47; nantong "—" 守红线-3; 8 城 real+miss=480=8×60 | curl + python regex |
| 5 | **client banner 默认正确** | public HTML 中 `FastAPI at http://127.0.0.1:8001` (or 实际值) | curl + grep |

### Hydration fix 端到端验证 (附加, post-deploy)

| 验证项 | 期望 | 方法 |
|---|---|---|
| SSR HTML 无 `<input type="range">` | count = 0 | python regex |
| 4 月份滑块 post-mount testid 命中 | 0 (server-side 仅 render skeleton) | python regex |
| `data-hydration-state="pending"` SSR 命中 | count = 1 | python regex |
| `data-hydration-state="mounted"` CSR 命中 (dev only) | 人工 DevTools | n/a (无法 curl) |

### 部署步骤 (per user_ruling_666+ SSH ops 授权)

```bash
# 1. local → scp newvps
scp frontend/lib/api.ts newvps:/opt/china-platform/repo/frontend/lib/api.ts
scp frontend/app/layout.tsx newvps:/opt/china-platform/repo/frontend/app/layout.tsx
scp frontend/app/page.tsx newvps:/opt/china-platform/repo/frontend/app/page.tsx

# 2. build
ssh newvps 'cd /opt/china-platform/repo/frontend && rm -rf .next && npm run build'

# 3. restart
ssh newvps 'sudo systemctl restart china-platform-frontend'

# 4. verify (5 红线)
curl -s "https://china.3strategy.cc/cities/shenzhen" > /tmp/sz.html
python3 -c "
import re
with open('/tmp/sz.html') as f: html = f.read()
print('city-timeseries-live:', len(re.findall(r'data-testid=\"city-timeseries-live\"', html)))
print('city-empty-state:', len(re.findall(r'data-testid=\"city-empty-state\"', html)))
print('cell-*:', len(re.findall(r'data-testid=\"cell-[a-z_]+-[0-9]{4}\"', html)))
"
```

### 不宣称

- ❌ 不宣布 api-base-fix PASS — 仅 DEPLOYED + 5/5 红线 + 公网 0 hydration warning 实测后登记
- ❌ 不冒充 ops — newvps deploy 仅 user_ruling_666+ 签署后
- ❌ 不回写 ops 文件 (systemd unit 不可改)
- ❌ 不爬网 — 仅 1 curl × 5 城 + 1 home + python parse
- ❌ 不主动 commit — 等用户授权

---

## 风险与缓解

| 风险 | 缓解 |
|---|---|
| **改 source 默认影响 local dev** | local dev 设 `NEXT_PUBLIC_API_BASE=...` env var 覆盖, 不破坏 dev workflow |
| **client banner 显示 ≠ 实际 fetch URL** | api.ts + layout.tsx 同步翻, build 后两者一致 |
| **首页容错后 mart section 也空 (因 listIndicators 失败是 fetch 错误, getMartProvinceGdp2024 走 static JSON 仍正常)** | 独立 fetch 路径, 不相互影响. mart section 仍显示 28+3 行. |
| **公网 / 显示空 Indicator inventory** | 顶部 banner 「LIVE MODE」仍标 FastAPI 地址, 修复后 listIndicators 应成功, inventory 不空 |
| **`/cities/nantong` 仍 CityEmptyState** | 期望行为 — 守红线-3 hongheiku 0 entry, 修复后不变 |
| **newvps 8001 端口被 firewall 限** | 实证已 accessible (curl localhost:8001 → 200, 60 cells), 不存在 |

---

## 预估 commits 结构 (1 commit)

```
<hash>  fix(api-base): 默认端口 8000 → 8001 + 首页容错, 修 H-series 后 city 页空白 + home 500
  - frontend/lib/api.ts: API_BASE 默认 localhost:8000 → 127.0.0.1:8001
  - frontend/app/layout.tsx: client banner 默认同步翻
  - frontend/app/page.tsx: listIndicators() 包裹 try/catch, 错误时 console.warn + 空 indicators
  - docs/plans/knife-api-base-fix.md: 本 plan
```

预估总: **1 commit** + 1 plan 文件 + 3 源文件改动

预估部署耗时:
- Code 改: ~5min
- scp + build + restart: ~3min
- 5 红线 curl + python verify: ~3min
- commit + push via Clash proxy: ~1min (待用户授权)

---

## Forward scope (post-api-base-fix)

- **knife hydration fix 收口**: API_BASE 修后, /cities/shenzhen 走 live, DevTools 0 warning 实测, commit + push knife hydration-fix (deferred per #1152)
- **knife env-config 整理**: 把所有 `process.env.NEXT_PUBLIC_*` 集中到 `frontend/lib/env.ts`, 编译时验证 (P3, cosmetic)
- **knife home-page UX**: Indicator inventory 空时显示 "数据加载中" placeholder (P3, cosmetic)
- **knife client-banner config**: 把 banner 移到 env-config 集中读, 避免 layout.tsx 直读 (P3, refactor)

---

## 链接

- 关联 knife H-series (commits 8d1e399/dc32d28/24b3ac2/b6eba49) — 暴露此 bug 的前置
- 关联 knife H3-verify (d0943a4) — 5/5 PASS, 验证 4 副省级 sync 后 H3 真实计数
- 关联 knife hydration-fix (deployed, pending commit) — 等待本件完成后端到端验证
- 关联 memory [[china-platform-fastapi-missing-on-newvps]] — FastAPI container 8001 端口实证
- 关联 memory [[china-platform-frontend-mart-env-var-regression]] — NEXT_PUBLIC_* 历史 regression 教训
- 关联 memory [[china-platform-nextjs-build-after-sync]] — scp 必须在 npm run build 之前
- 关联 memory [[china-platform-next-server-restart-pattern]] — systemd restart vs nohup (newvps 用 systemd)

— End knife api-base-fix plan (修 API_BASE 默认 + 首页容错, 2026-09-13, READY FOR EXECUTION) —
