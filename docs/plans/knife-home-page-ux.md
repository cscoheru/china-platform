# knife home-page-ux — Indicator inventory 空 state placeholder (2026-09-13)

> **刀号**: home-page-ux
> **角色**: 架构师+执行端 merged (per 2026-08-31 21:50 豁免)
> **前置**: knife env-config (8a36c43) 双推 PASS, knife api-base-fix (1fb9fc8) PASS
> **本件状态**: **READY FOR EXECUTION**
> **关联**: api-base-fix forward scope §"knife home-page UX" + 本次 API_BASE 500 bug 直接提炼

---

## Context (为什么做这件事)

### 用户质询 (2026-09-13)

> 「不用审验，下一刀」 → 「knife env-config 整理」 → 双推 → 「启动下一刀」
> 「(a) knife home-page UX 空 state placeholder」

### 直答

knife api-base-fix (1fb9fc8) 修复了 `listIndicators()` 抛错 → `/` HTTP 500 的硬错, 但**容错 fallback 是空 tbody**, 用户看到的是**空白表格** — 不告知: (1) 数据为什么空 (2) 怎么修。

本次 API_BASE 500 bug 期间, user 第一次发现是因为首页空白 + 控制台 500 — 没有"为什么空"的提示, 排查耗时。

修这条: 把空 indicators 状态升级成**有信息量的 placeholder**, 显示:
- 当前 mode (MOCK / MART_FIXTURE / LIVE / STATIC_MART_DATA)
- 失败原因 (catch 捕获的 error.message)
- 提示"如何切换 mode" (env var 名)
- 不冒充 ops 修复, 仅告知

---

## Root Cause (根因分析)

### 当前空 state (`page.tsx:40-49, 145-156`)

```tsx
let data: IndicatorListResponse;
try {
  data = await listIndicators();
} catch (err) {
  console.warn(...);
  data = { indicators: [], pagination: {...} };
}
// ...
<tbody>
  {data.indicators.map((it) => <tr>...</tr>)}
</tbody>
```

- 空 indicators → 空白 `<tbody>` (无 `<tr>`)
- catch 错误仅 console.warn, 用户不可见
- mode 切换不告知, 无法自助 debug

### 用户体验问题 (per API_BASE bug 实证)

| 现象 | 用户感知 |
|---|---|
| 首页 200 但 Indicator inventory 空白 | "数据丢了?" |
| Console 看到 `listIndicators: 404` | "server 出问题?" |
| Banner 显示 `LIVE MODE` 但 inventory 空 | "我切错了 mode?" |

### 为什么之前没暴露

api-base-fix 之前是 500, 用户至少知道"页面坏了"; 修后变成"页面正常但内容空", 比 500 更隐蔽 — user 默默接受空数据而不排查。

---

## Fix (修复方案)

### 选定方案

**A. 空 state placeholder 单行** (本刀主体, in-tbody)
- 当 `data.indicators.length === 0` 时, 渲染 1 个 placeholder `<tr>` 跨 4 列 (`<td colSpan={4}>`)
- 内容: mode-aware 提示文本 (LIVE / MOCK / MART_FIXTURE / STATIC_MART_DATA 各自文案)
- 包含: 当前模式 + 失败原因 + "如何切换 mode" 提示

**B. 模式诊断 helper** (新增, in-page.tsx)
- `getEmptyStateMessage()` 函数返回 string, 根据 `IS_MOCK_MODE` / `IS_MART_FIXTURE_MODE` / `IS_STATIC_MART_DATA_MODE` + error.message 派生文案
- 文案 4 模板:
  - LIVE 失败: "Live FastAPI 不可达 (<error>). 请检查 `NEXT_PUBLIC_API_BASE` 或 FastAPI 后端服务。"
  - MOCK + indicators 空: "Mock 模式 sentinel 数据未配置。" (实际不应发生, mock 应总返 1 条)
  - MART_FIXTURE: "Mart demo 模式无 Indicator inventory (Mart 走 Province 表)。"
  - STATIC_MART_DATA: "Static mart 模式, indicators 从 mart_province_gdp_2024.json 构造 (28 省 + 3 缺失)。"

**C. 不替换表格** (保持现有 table 结构, 仅 tbody 改 1 行)
- 不动 table header
- 不动其他 sections (mart / city completeness / public-extracts 等)
- 不动 error 路径 (仍 console.warn, 仅 user-visible 部分升级)

### 修改文件清单 (1 改 + 1 新 = 2 文件)

| 路径 | 类型 | 改动 |
|---|---|---|
| `frontend/app/page.tsx` | **M** (15-25 行) | 加 `getEmptyStateMessage()` 函数 + 空 tbody placeholder + error 状态 |
| `docs/plans/knife-home-page-ux.md` | **A** | 本 plan |

### 复用与依赖

- **复用** `lib/env.ts` `IS_MOCK_MODE` / `IS_MART_FIXTURE_MODE` / `IS_STATIC_MART_DATA_MODE` (per knife env-config 8a36c43)
- **复用** `lib/api.ts` `listIndicators()` error.message (try/catch 已存在)
- **不依赖** 其他 component 改动
- **不依赖** mart section / city completeness section

### 红线守门 (本件专属)

- ✓ **DATA_MISSING 显式「数据缺失」** (本件不涉及, indicators 不属于 mart 数据流)
- ✓ **不爬网** (本件 0 HTTP)
- ✓ **amend-first** (1 commit, 1 改 + 1 新)
- ✓ **mock 链文件不删**
- ✓ **不主动 commit/push** (待用户授权)
- ✓ **不冒充 ops**
- ✓ **docs/81 零改动**
- ✓ **不取代 ops 自助提示** (placeholder 文案不暗示 user 自己重启 FastAPI / 改 deploy.sh)
- ✓ **保持 client-banner 单一来源** (不在 placeholder 重复 banner, 仅引出 context)

---

## Verification (验证闭环)

### 5 红线 PASS (公网 https://china.3strategy.cc 2026-09-13 curl 实测, post-deploy)

| # | 红线 | 期望 | 验证方法 |
|---|---|---|---|
| 1 | **空 state placeholder 出现** | 当 listIndicators() 失败, `/` HTML 含 `data-testid="home-indicator-empty-state"` testid | curl + python regex |
| 2 | **placeholder 文案含 mode 提示** | HTML 含 "Mock mode" / "Mart demo" / "Live FastAPI 不可达" / "Static mart" 之一 | curl + grep |
| 3 | **placeholder 含 error message** | HTML 含 `listIndicators` 错误描述 (e.g. "fetch failed" / "404") | curl + grep |
| 4 | **非空状态不显示 placeholder** | 正常 indicators 渲染时 placeholder testid = 0 | curl + python regex |
| 5 | **不破坏现有 5 红线** | `/cities/shenzhen` 仍 60 cells + hydration markers; `/` mart section + city completeness + 11 testids 仍渲染 | curl + python regex (per knife env-config §4 red lines) |

### 部署步骤 (per user_ruling_666+ SSH ops 授权)

```bash
# 1. local → scp newvps
scp frontend/app/page.tsx newvps:/opt/china-platform/repo/frontend/app/page.tsx

# 2. build
ssh newvps 'cd /opt/china-platform/repo/frontend && rm -rf .next && npm run build'

# 3. restart
ssh newvps 'sudo kill -TERM <old_pid> 2>/dev/null; sudo systemctl restart china-platform-frontend'

# 4. verify (5 红线)
curl -s "https://china.3strategy.cc/" -o /tmp/home_ux.html
python3 -c "
import re
with open('/tmp/home_ux.html') as f: html = f.read()
checks = [
    ('indicator-empty-state testid',  r'data-testid=\"home-indicator-empty-state\"',  0 or 1),
    ('mart row count testid',          r'data-testid=\"mart-row-count\"',             1),
    ('home-city-completeness-*',       r'data-testid=\"home-city-completeness-[a-z_]+\"', 11),
]
print()
"
```

### 不宣称

- ❌ 不宣布 home-page-ux PASS — 仅 DEPLOYED + 5/5 红线 + 公网实测后登记
- ❌ 不冒充 ops
- ❌ 不回写 ops 文件
- ❌ 不爬网
- ❌ 不主动 commit

---

## 风险与缓解

| 风险 | 缓解 |
|---|---|
| **placeholder 误导 user 自己修 ops** | 文案限定 user-facing 提示 (mode 切换, env var 名), 不暗示重启 FastAPI / 改 deploy.sh |
| **placeholder 文案国际化** | 本件中文 (与现有 page.tsx 一致), i18n 留 forward scope |
| **error.message 泄露内部细节** | try/catch 已有 (api-base-fix), placeholder 仅显示 message, 不暴露 stack trace |
| **placeholder 视觉突兀** | 用 `<span style={{ color: "#999" }}>` + italic, 与现有 "—" 占位风格一致 |
| **Mock 模式 sentinel 数据永不空** | 文案说明"Mock sentinel 数据未配置 (预期不会发生)" |

---

## 预估 commits 结构 (1 commit)

```
<hash>  feat(home-page-ux): Indicator inventory 空 state placeholder, 显式 mode + error 提示
  - frontend/app/page.tsx: 加 getEmptyStateMessage() helper + 空 tbody placeholder 行
    (mode-aware 文案: MOCK / MART_FIXTURE / STATIC_MART_DATA / LIVE-failed 各 1 模板)
  - docs/plans/knife-home-page-ux.md: 本 plan
```

预估总: **1 commit** + 1 plan 文件 + 1 源文件改动

预估部署耗时:
- Code 改: ~5min
- scp + build + restart: ~3min
- 5 红线 curl + python verify: ~3min
- commit + push via Clash proxy: ~1min (待用户授权)

---

## Forward scope (post-home-page-ux)

- **knife home-page-stale-data**: 增加 `as_of` 时间戳 (mart 数据更新信号), "数据更新于 ..." 提示 (P3)
- **knife i18n**: placeholder 文案 i18n 化 (per docs/46 i18n 路线图) (P2)
- **knife banner-config-extract**: 把 banner 模式判定逻辑移到 `lib/env.ts` 派生 `BANNER_MODE` 字符串 (per api-base-fix plan forward scope) (P3)
- **knife 669j-1 启动**: 5 卫星城 30 HTTP 数据补完 (D3 lift, user_ruling_669j-1 需签) (P2)

---

## 链接

- 关联 knife api-base-fix (1fb9fc8) — 暴露本件根因 (空状态隐藏 bug)
- 关联 knife env-config (8a36c43) — 提供 `IS_*_MODE` typed boolean (本件用)
- 关联 knife hydration-fix (f9d7b1a) — 前一闭环刀
- 关联 memory [[china-platform-env-config-closure]] — env 集中化
- 关联 memory [[china-platform-fastapi-missing-on-newvps]] — 8001 端口实证

— End knife home-page-ux plan (Indicator inventory 空 state placeholder, 2026-09-13, READY FOR EXECUTION) —