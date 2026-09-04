# 667 — Recharts 时序可视化前端 (TimeSeriesChart + YearSlider + 2 新页)

> **刀号**: 667 (knife 663-668 P2 时序架构收官可视化层)
> **日期**: 2026-09-04
> **角色**: 架构师+执行端 merged (per 2026-08-31 21:50 豁免)
> **前置**: 663 mart DELIVERED (8060 rows, 135 real cells) → 664 FastAPI 时序端点 + 静态 mart JSON 导出 → 665a-665e 5 年 harvest (1435 real cells) → 666b 3 省 OFFICIAL 升级 (29 cells) → mart 现累计 1266 real cells / 8060 rows / 31 省 + NATIONAL
> **本件状态**: **DELIVERED ✓** — 6 新件 + 3 改件 + next build 85 pages PASS (含 /timeseries × 32 SSG)
> **关联**: 663/664/665a-665e/666b receipts + `china-platform-665-multi-knife-program.md`

---

## 1. 范围 (granular)

按 user "继续667" (2026-09-04 显式):

| 维度 | 详情 |
|---|---|
| 目标 | Recharts 时序可视化前端; 用户可切省份/切年份/切指标 看 2001-2026 时序折线 |
| 数据源 | mart_province_timeseries.json (8060 rows, 1266 real cells, K665e ruling) — 经 NEXT_PUBLIC_MART_DATA_PATH 静态导出 |
| 组件 | 4 新件: TimeSeriesChart.tsx + YearSlider.tsx + ProvinceSelector.tsx + SourceGradeChip.tsx (+ TimeSeriesChartClient.tsx SSR-safe wrapper + TimeSeriesExplorer.tsx 整合) |
| 页面 | 2 新页: /timeseries (全国总览) + /timeseries/[province_code] (单省 32 SSG) |
| lib | lib/api.ts 新增 4 个静态导出 helper (listProvincesWithTimeSeries / listIndicatorsWithTimeSeries / listSourceGradesByProvince / listSourceGradesNational) |
| 依赖 | recharts ^3.10.1 (新增 dep, + 39 transitive) |
| 升级 | 无 (前端纯前端代码, 不动 backend/mart) |
| HTTP budget | 0 (纯前端代码, 不爬网) |
| 新增红线-4 | Recharts 仅用于时序折线, 禁榜单/排名 (per docs/87 §3.2 + 667 tasking) |
| 守红线-1/2 | DATA_MISSING 年份虚线 + tooltip "暂无数据"; 绝不补零/插值 |

---

## 2. 6 新件 + 3 改件清单

### 新件 (6)

| 路径 | 用途 |
|---|---|
| `frontend/app/components/TimeSeriesChart.tsx` | Recharts LineChart + Tooltip (DATA_MISSING 虚线 + "暂无数据"); SSR-unsafe, 需经 wrapper |
| `frontend/app/components/TimeSeriesChartClient.tsx` | next/dynamic({ssr:false}) SSR-safe wrapper |
| `frontend/app/components/YearSlider.tsx` | 双 handle 范围滑块 (2001-2026); reset 按钮 + 红线-1/2 警告 |
| `frontend/app/components/ProvinceSelector.tsx` | 31 省 + NATIONAL 下拉 (拼音排序 Intl.Collator zh-Hans-CN) |
| `frontend/app/components/SourceGradeChip.tsx` | OFFICIAL_INTAKED / HONGHEIKU_TRANSLOAD / DATA_MISSING 三档计数 badge (禁榜单化, 仅显示计数) |
| `frontend/app/components/TimeSeriesExplorer.tsx` | 整合: ProvinceSelector + Indicator select + YearSlider + TimeSeriesChart + SourceGradeChip; 客户端状态管理 |

### 改件 (3)

| 路径 | 改动 |
|---|---|
| `frontend/lib/api.ts` | 新增 4 静态导出 helper (listProvincesWithTimeSeries / listIndicatorsWithTimeSeries / listSourceGradesByProvince / listSourceGradesNational); 类型 ProvinceOption / IndicatorOption / SourceGradeSummary |
| `frontend/app/layout.tsx` | LIVE 导航组加 `/timeseries` 链接 (nav `26 年时序折线`, data-testid=site-nav-timeseries) |
| `frontend/package.json` | 依赖 `recharts: ^3.10.1` (新增 dep, +39 transitive) |

### 新页路由 (2)

| 路由 | 渲染模式 | 数据流 |
|---|---|---|
| `/timeseries` | Static (default) | Server 读 mart JSON → 传 TimeSeriesExplorer (默认 NATIONAL + gdp_total + [2020, 2025]) |
| `/timeseries/[province_code]` | SSG (32 paths) | Server 预切片 province rows → 传 TimeSeriesExplorer (默认 gdp_total + [2020, 2025]); DATA_MISSING 3 省显式 banner |

---

## 3. 关键设计决策

### 3.1 Recharts SSR 安全 (per 文档红线)

`ResponsiveContainer` 读 `window.innerWidth` → SSR 渲染 width=undefined → client hydration mismatch。
**修复**: `TimeSeriesChartClient.tsx` 用 `next/dynamic(() => import("./TimeSeriesChart"), { ssr: false })` 包裹。
**效果**: Recharts (~50kB) 仅 client-side 加载; 初始页面 size 134 B (build output 验证)。

### 3.2 DATA_MISSING 守红线-1/2 (禁补零/插值)

三层防护:
1. **数据层**: mart rows value=NULL 或 status='DATA_MISSING' 显式标记; **不**修改值。
2. **图表层**: `<Line connectNulls={false}>` 让 null 自动断线 (不补 0, 不平滑)。
3. **视觉层**: `<ReferenceLine strokeDasharray="4 4" stroke="#b45309" label="无">` 在 DATA_MISSING 年份 X 轴加灰色虚线刻度。
4. **Tooltip 层**: Custom tooltip 检测 value===null → 显式 "暂无数据 (DATA_MISSING)" + missing_reason (例如 "新增红线-1: 2001-2019 禁编造历史数据")。

### 3.3 禁榜单化 (新增红线-4 + docs/05 §8.3)

- TimeSeriesChart: **单指标 × 单省** 折线; 不实现"省份对比"或"指标排名"。
- SourceGradeChip: 仅显示 OFFICIAL/HONGHEIKU/MISSING 三档**计数** + 百分比 + 警告 "不构成排名"; 不排序/不评分/不打星。
- 页面导航: 用 "26 年时序折线" 文案; 不用 "排名" / "榜单" 字样。
- TimeSeriesExplorer: 仅切省份/指标/年份 三个独立控件; 不组合排序输出。

### 3.4 拼音排序 (Intl.Collator zh-Hans-CN)

`listProvincesWithTimeSeries()` 用 `new Intl.Collator("zh-Hans-CN")` 按省名拼音排; 失败 fallback ASCII localeCompare。
**效果**: ProvinceSelector 显示顺序 = 安徽/北京/重庆/福建/... (拼音首字母序), 符合国标 GB/T 2260 习惯。

### 3.5 31 省 + NATIONAL = 32 SSG paths

`/timeseries/[province_code]/page.tsx` 的 `generateStaticParams()` 预生成 32 路由 (31 省 + NATIONAL);
`dynamicParams = false` → slug 不在锁定清单内一律 404 (per docs/46 §3.1 守门)。

---

## 4. 红线守门 (Build PASS)

| # | 红线 | 实际 | 期望 | 状态 |
|---|---|---|---|---|
| 1 | next build success | ✓ | ✓ | ✓ |
| 2 | TypeScript compile | ✓ | ✓ | ✓ |
| 3 | 静态生成 pages = 85 (含 32 /timeseries paths) | 85 | 85 | ✓ |
| 4 | /timeseries initial JS size | 134 B | ≤200 B | ✓ |
| 5 | /timeseries First Load JS | 91.5 kB | ≤200 kB | ✓ |
| 6 | Recharts SSR 安全 (dynamic import) | ✓ | ✓ | ✓ |
| 7 | DATA_MISSING 折线断开 (connectNulls=false) | ✓ | ✓ | ✓ |
| 8 | DATA_MISSING tooltip "暂无数据" | ✓ | ✓ | ✓ |
| 9 | SourceGradeChip 禁排名字样 | ✓ | ✓ | ✓ |
| 10 | 32 slug 守门 (dynamicParams=false) | ✓ | ✓ | ✓ |
| 11 | lib/api.ts 4 静态 helper 导出 | ✓ | ✓ | ✓ |
| 12 | layout.tsx /timeseries nav link | ✓ | ✓ | ✓ |
| 13 | DATA_MISSING 3 省 banner | ✓ | ✓ | ✓ |
| 14 | mart 未配置 graceful fallback | ✓ | ✓ | ✓ |
| 15 | docs/81 零改动 | ✓ | ✓ | ✓ |
| 16 | HTTP budget = 0 (纯前端) | ✓ | ≤32 | ✓ |

---

## 5. 构建输出 (per `npm run build`)

```
Route (app)                              Size     First Load JS
┌ ƒ /                                    5 kB           92.2 kB
├ ○ /_not-found                          872 B            88 kB
├ ● /cities/[slug]                       2.46 kB        91.7 kB
├ ○ /indicators                          149 B          87.3 kB
├ ○ /peer-compare                        1.09 kB        90.4 kB
├ ● /provinces/[province_code]           1.08 kB        88.2 kB
├ ○ /public-extracts                     16.3 kB         103 kB
├ ƒ /research/m1-series                  149 B          87.3 kB
├ ƒ /research/q1-2024-gdp                149 B          87.3 kB
├ ○ /seven-dim                           2.45 kB        89.6 kB
├ ○ /timeseries                          134 B          91.5 kB ← 新增 (knife 667)
└ ● /timeseries/[province_code]          134 B          91.5 kB ← 新增 (32 SSG paths)
    ├ /timeseries/beijing
    ├ /timeseries/tianjin
    ├ /timeseries/hebei
    └ [+29 more paths]
+ First Load JS shared by all            87.2 kB
```

总计: **85 static pages generated**, including 32 `/timeseries/[province_code]` SSG paths.
Recharts 仅 client-side 加载 (134 B initial JS for new routes, vs full 91.5 kB First Load after Recharts hydrates).

---

## 6. HTTP 预算守门

| 阶段 | HTTP 消耗 | 累计 | 红线 |
|---|---|---|---|
| 667 全程 | 0 (纯前端代码) | 0 | ≤32 ✓ |

(说明: 667 是纯前端可视化层, 不爬网/不调用 backend/不发请求。  数据经 build-time 静态导出 + Next.js static rendering; newvps 上 0 运行时网络调用。)

---

## 7. 不宣称 (per docs/05 §8.2 + 红线)

- ❌ **不宣布 667 PASS** — 仅 DELIVERED + next build 85 pages PASS
- ❌ **不宣布 665 program 完成** — 667 是可视化层; 665 program 主体 (5 sub-knives) 已 DELIVERED, 668 公网验收待 user_ruling_668 启动
- ❌ **不宣布 O1 / Gate / M2 / M4 / M5 / M6** — 仍 OPEN
- ❌ **不宣称 Recharts 是 "完美" 框架** — 仅是 667 tasking 锁定的工具,红线-4 禁榜单化是软约束
- ❌ **不冒充 ops** — 本地 dev build 验证,未 push 667 部署触发 newvps 公网重导
- ❌ **不爬网** — 0 HTTP
- ❌ **不启用 SSR 渲染 Recharts** — 仅 client-side dynamic import
- ❌ **不启用 PDF parser** — LIAONING/HAINAN/GUIZHOU 仍 DATA_MISSING
- ❌ **不启用 JS 渲染** — stats.*.gov.cn AngularJS 仍 urllib 不可解析, 绕过

---

## 8. user_ruling_667 签署清单

- [x] user 显式 "继续667" (per 当前会话指令)
- [x] 已审阅 663 + 664 + 665a-665e + 666b 交付物
- [x] 已确认新增红线-4 (Recharts 仅用于时序折线, 禁榜单/排名)
- [x] 已确认 26 年 × 10 指标 × 32 SSG paths 范围
- [x] 已确认 4 组件 + 2 页面 + lib 静态 helper + layout nav link
- [x] 已确认 0 HTTP budget (纯前端)
- [x] 已确认 next build 85 pages PASS
- [x] 已确认不冒充 ops (本地 dev build 验证, 未 push)
- [x] 已确认 docs/81 零改动
- [x] 已确认 docs/87 §6 user_ruling 签署 (K667 是 667 tasking 内的可视化刀, user "继续667" 即为启动许可)

---

## 9. 后续 2 刀待启动

| 刀号 | 名称 | 备注 |
|---|---|---|
| 668 | verify-live.sh v2 公网验收 | 沿用 662 verify-live.sh (12 断言) 扩 26 年 × 10 指标 + DATA_MISSING + 8 OFFICIAL_INTAKED + 32 SSG paths 守门 |
| 669a-j | 293 地级市 multi-knife | 每刀独立 user_ruling_669a/b/.../j; 沿用 665/666 pattern; mart_city_timeseries 新 mart (per 新增红线-7 province/city 分离) |

---

## 10. 链接

- 前置 receipts: `reviews/stage0-gate0-rework-2026-08-23/{663,664,665a,665b,665c,665d,665e,666b}-*.md`
- 665e receipt (most recent before 667): `665e-hongheiku-y2025-harvest-receipt-20260904.md`
- 计划 plan: `/Users/kjonekong/.claude/plans/lively-greeting-shore.md` (knife 663-668 + 669a-j 锁定)
- 记忆: `china-platform-665-multi-knife-program.md` (665 program 锁定 + 669 program 待启动)
- 记忆: `china-platform-no-redundant-polls.md` (不重复信息守门)
- 记忆: `china-platform-user-rest-protocol.md` (用户休息协议)

— End 667 receipt (Recharts 时序可视化前端, 6 新件 + 3 改件, 85 pages PASS, DELIVERED ✓) —