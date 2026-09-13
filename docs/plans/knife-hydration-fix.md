# knife hydration-fix — /cities/shenzhen React #418/#423 hydration warnings (2026-09-13)

> **刀号**: hydration-fix
> **角色**: 架构师+执行端 merged (per 2026-08-31 21:50 豁免)
> **前置**: knife H-series H1+H2+H3 (commits 8d1e399/dc32d28/24b3ac2/b6eba49) 已 deployed 4 副省级 city live mart
> **本件状态**: **READY FOR EXECUTION** — user 2026-09-13 选定 "修 hydration warning"
> **关联**: H-series plan + B-OPT-NT (b6eba49) + H3-verify (d0943a4)

---

## Context (为什么做这件事)

### 用户质询 (2026-09-13)

> 「继续下一刀」→ 选定「修 hydration warning (推荐)」

### 直答

knife H-series B-OPT-NT (b6eba49) + H3-verify (d0943a4) 完成 4 副省级 live mart 接驳, 公网 9/10 city 页面走 live mart. 但前端 dev 打开 /cities/shenzhen 控制台报 8 条 React #418/#423 hydration warning.

QA report: "Pre-existing React #418/#423 hydration warnings on /cities/shenzhen are from YearSlider/Recharts SSR/CSR mismatch".

---

## Root Cause (根因分析)

### 文件实测

1. `frontend/app/components/YearSlider.tsx` (6115 bytes, 'use client'):
   - `<input type="range" min={2001} max={2026} value={yearStart} />` (line 94-104)
   - `<input type="range" min={2001} max={2026} value={yearEnd} />` (line 107-118)
   - `value={number}` → React 19 hydration 检查 number vs string 的 DOM attribute 时触发 mismatch

2. `frontend/app/components/CityTimeseriesLive.tsx` (12935 bytes, 'use client'):
   - 渲染 YearSlider + SourceGradeChip + table (10 indicator × 6 year)
   - `useState(initialResponse.year_range[0])` 来自 server-fetched 数据
   - table 内容确定 (SSR = CSR), 唯一可疑 mismatch 源 = YearSlider inputs

3. `frontend/app/components/TimeSeriesChart.tsx` (10046 bytes) + `TimeSeriesChartClient.tsx` (1854 bytes):
   - Recharts ResponsiveContainer 读 window.innerWidth; 已用 `dynamic({ ssr: false })` 包装 (TimeSeriesChartClient)
   - /cities/shenzhen 路径不渲染 TimeSeriesExplorer (只用 CityTimeseriesLive), 故 Recharts 非本件 source

4. `frontend/app/cities/[slug]/page.tsx`:
   - server component → 调 `getCityTimeSeries()` → render `<CityTimeseriesLive>`
   - server-fetched 数据 via RSC 序列化传入 client component
   - server 与 client 接收同一 prop, useState 初始化一致

### SSR HTML 实测 (公网 2026-09-13)

```
<input type="range" min="2001" max="2026" step="1" aria-label="年份起点" 
  data-testid="year-slider-start" style="width:100%;accent-color:#0969da" 
  value="2020"/>
```

server emits `value="2020"` (string from attribute). client React prop `value={2020}` (number). React 19 hydration 对 controlled range input 检查更严 — 数字 vs 字符串 mismatch 触发 #418.

8 条 warning = 2 inputs × cascading children mismatch (YearSlider header text "(<!-- -->6<!-- --> 年)" 与 reset button "重置 (<!-- -->2020<!-- -->–<!-- -->2025<!-- -->)" 都有 `<!-- -->` 边界, parent mismatch 触发 children re-render warning).

---

## Fix (修复方案)

### 选定方案: useEffect setMounted guard (per-input)

**理由**:
- TimeSeriesChartClient 已用 `dynamic({ssr: false})` 解决 Recharts 同类问题 (commit knife 667); 本件沿用同 pattern 但作用域限于 YearSlider (避免整页客户端化)
- `suppressHydrationWarning` 仅压制 1 层 attribute 警告, 不压制 children 级 cascade → 8 warning 仍残留
- `dynamic({ssr: false})` 整页 → SEO 退化 (table content 不在 initial HTML) → 不推荐
- `defaultValue` 替代 `value` → 后续 setYearStart 不会更新 input.value → 不推荐

**方案**: 在 YearSlider 加 `useEffect(() => setMounted(true), [])`. 未 mount 时渲染 SSR-friendly 静态文本 (header + 数字回显, 无 inputs). mount 后渲染完整版本 (含 inputs).

```
SSR HTML:    <div data-testid="year-slider">
                <span>年份范围:</span>
                <span><strong>2020</strong>—<strong>2025</strong></span>
                <span>(6 年)</span>
              </div>
              [无 inputs]

CSR mount:  useEffect fires → setMounted(true) → re-render
              <div data-testid="year-slider">
                <span>年份范围:</span>
                <span><strong>2020</strong>—<strong>2025</strong></span>
                <span>(6 年)</span>
                <button>重置 (2020–2025)</button>
                <label><input type="range" value="2020"/></label>
                <label><input type="range" value="2025"/></label>
              </div>
```

SSR HTML 简化为 text-only skeleton, CSR mount 后再填 inputs. Hydration 完全匹配 (both render same initial state). 之后 useEffect 触发 client-side re-render, 期间无 hydration warning (post-hydration mismatch 不警告).

### 修改文件清单 (1 文件改, 1 plan 新)

| 路径 | 类型 | 改动 |
|---|---|---|
| `frontend/app/components/YearSlider.tsx` | **M** | 加 `useEffect` setMounted + 静态分支 (无 inputs) + 完整分支 (有 inputs) |
| `docs/plans/knife-hydration-fix.md` | **A** | 本文件 |

### 复用与依赖

- 复用现有 YearSlider 所有 CSS variables (containerStyle / headerStyle / rangeStyle / countStyle / labelStyle 等)
- 复用现有 props interface (yearStart / yearEnd / onChange / min / max / defaultRange)
- 不依赖其他组件改动 (CityTimeseriesLive 不动)

### 红线守门 (本件专属)

- ✓ **不擅自增减 10 城名单** (YearSlider 改动不影响 city_slug_map.ts)
- ✓ **DATA_MISSING 显式「数据缺失」** (CityTimeseriesLive 不动, 此约束保留)
- ✓ **不爬网** (本件 0 HTTP, 仅 fetch 公网 /cities/shenzhen 验 hydration markers)
- ✓ **amend-first** (1 commit, 1 文件改 + 1 plan 新)
- ✓ **mock 链文件不删** (mart_city_demo.ts / mock_cities.ts 保留)
- ✓ **不主动 commit/push** (待用户授权 "commit + push")

---

## Verification (验证闭环)

### 公网 HTML 实测 (after deploy)

```bash
# 1. SSR HTML 不再含 input type="range"
curl -s "https://china.3strategy.cc/cities/shenzhen" > /tmp/shenzhen_after.html
python3 << 'EOF'
import re
with open('/tmp/shenzhen_after.html') as f:
    html = f.read()
m = re.findall(r'<input[^>]*type="range"', html)
print(f"SSR <input type='range'> count: {len(m)} (期望 0, 因为 inputs 在 CSR mount 后才渲染)")
m2 = re.findall(r'data-testid="year-slider"', html)
print(f"year-slider testid count: {len(m2)} (期望 1)")
EOF
```

### 5 红线 PASS verification

| # | 红线 | 验证 |
|---|---|---|
| 1 | SSR HTML 无 `<input type="range">` | python regex count = 0 (inputs 仅 client mount 后出现) |
| 2 | year-slider testid SSR 命中 | count = 1 (静态文本分支渲染) |
| 3 | data-year-start/data-year-end SSR 命中 | count = 1/1 (静态分支从 props 渲染) |
| 4 | city-timeseries-live testid 命中 | count = 1 (CityTimeseriesLive 主容器不变) |
| 5 | table content (10×6 cell testids) 命中 | count = 60 (table 不变, 仍 SSR) |

### DevTools console (人工, 不在本件脚本化)

期望: 0 React #418/#423 hydration warning (从 8 → 0)

### 不宣称

- ❌ 不宣布 hydration-fix PASS — 仅在 DEPLOYED + 5/5 红线 PASS + 公网 0 warning 实测后登记
- ❌ 不冒充 ops — newvps deploy 仅 user_ruling_666+ 签署后
- ❌ 不回写 ops 文件
- ❌ 不爬网 — 仅 curl 1 次公网验
- ❌ 不主动 commit — 等用户授权

---

## 风险与缓解

| 风险 | 缓解 |
|---|---|
| **YearSlider SSR 简化 → 初始 paint 缺 slider 控件** | skeleton 仍展示年份范围 + count, 用户感知仅 slider 控件延迟 ~16ms (client mount 后立即出现). 视觉无显著退化 |
| **useEffect setMounted 触发 re-render → layout shift** | skeleton 与完整版结构一致 (same div + same text + same width), 仅 inputs 后插入, layout shift 极小 |
| **Accessibility: slider 在 mount 前未在 a11y tree** | skeleton 含 text-only "年份范围: 2020—2025 (6 年)" + button "重置", 屏幕阅读器仍可获取关键信息 |
| **其他 client component 也有同样 input 模式** | 仅 YearSlider 用 `<input type="range">`, 其他 client component (SourceGradeChip, CityEmptyState 等) 无 range input → 无需扩大 fix scope |

---

## 预估 commits 结构 (1 commit)

```
<hash>  fix(hydration): YearSlider setMounted guard 消除 /cities/shenzhen 8 条 React #418/#423 warning
  - frontend/app/components/YearSlider.tsx: useEffect setMounted + 静态分支 (SSR) / 完整分支 (CSR mount)
  - docs/plans/knife-hydration-fix.md: 本 plan
```

预估总: **1 commit** + 1 plan 文件 + 1 文件改动

预估部署耗时:
- Code 改 + 本地 build: ~3min
- scp newvps + npm run build + start-stop-daemon restart: ~3min
- 公网 curl 验: ~1min
- commit + push via Clash proxy: ~1min

---

## Forward scope (post-hydration-fix)

- **knife H-series B-OPT-NT+**: 同 fix pattern 推广到其他 client component (如有 range input / Date.now() / localStorage)
- **knife hydration-strict-mode**: 启用 React strict mode in dev, 提前发现未来 hydration mismatch
- **knife YearSlider UX**: 把 skeleton 与完整版用 CSS transition 渐入, 避免 layout shift 感知

---

## 链接

- 关联 knife H-series (commits 8d1e399/dc32d28/24b3ac2/b6eba49)
- 关联 knife 971 sync (HEAD 24a1e11) — 4 副省级 live mart
- 关联 knife H3-verify (HEAD d0943a4) — H3 列 5/5 PASS
- 关联记忆 [[china-platform-fastapi-missing-on-newvps]] (FastAPI 在 newvps 实证)
- 关联记忆 [[china-platform-nextjs-build-after-sync]] (scp 必须在 npm run build 之前)
- 关联记忆 [[china-platform-next-server-restart-pattern]] (start-stop-daemon 才能 detach)

— End knife hydration-fix plan (YearSlider setMounted guard, 2026-09-13, READY FOR EXECUTION) —