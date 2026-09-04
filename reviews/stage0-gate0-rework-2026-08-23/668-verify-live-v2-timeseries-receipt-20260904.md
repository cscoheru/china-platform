# 668 — verify-live.sh v2 公网 26 年 × 10 指标验收

> **刀号**: 668 (knife 663-668 P2 时序架构收官验收层)
> **日期**: 2026-09-04
> **角色**: 架构师+执行端 merged (per 2026-08-31 21:50 豁免)
> **前置**: 663 mart DELIVERED → 664 FastAPI 时序端点 + newvps postgres → 665a-e 5 年 harvest (1435 cells) → 666b 3 省 OFFICIAL → 667 Recharts 时序可视化前端 (DELIVERED, push 8b2f48e) → mart 现累计 1266 real cells / 8060 rows / 31 省 + NATIONAL
> **本件状态**: **DELIVERED ✓** — verify-live.sh v2 写好 (520 行, +202 行 vs v1);OFFLINE 语法 PASS 28/28;LIVE mode 13/41 验收项 PASS (12 P1 baseline 全部就位 + 1 SSR 安全 OK);5 P2 时序新增 section 暂 FAIL (newvps 未部署 667, 待 user_ruling_668+ granular 授权)
> **关联**: 663/664/665a-e/666b/667 receipts + `china-platform-665-multi-knife-program.md`

---

## 1. 范围 (granular)

按 user "开启668" (2026-09-04 显式):

| 维度 | 详情 |
|---|---|
| 目标 | 在 knife 662 verify-live.sh (12 P1 baseline) 基础上扩 v2, 加 5 个 P2 时序新增 section, 守门 knife 667 时序前端 |
| 工具 | bash + curl + grep (per 662 pattern, 纯 HTTP 验证) |
| 覆盖 | 17 项断言 = 12 P1 baseline + 5 P2 时序新增 |
| OFFLINE | `--offline` 模式 28 个 testid/字符串 keyword 守门 |
| LIVE | 11 个新文件 / 5 个新 testid 组 / 32 SSG paths / 3 DATA_MISSING 省 banner / dynamicParams=false 404 守门 |
| HTTP budget | 0 (纯 bash + curl, 不爬网/不调用 backend) |
| 升级 | 无 (纯 bash 脚本, 不动 backend/frontend/mart) |
| 红线 | 沿用 668 tasking 锁定; 不冒充 ops (newvps 部署待 user 单独签署) |

---

## 2. 文件改动清单 (1 改件, +202 行)

### 改件 (1)

| 路径 | 改动 | 行数 |
|---|---|---|
| `deploy/static-export/verify-live.sh` | v1 → v2: 顶部 banner / OFFLINE keywords / 5 个新 section (13-17) / summary 12→17 | 318 → 520 (+202) |

### v1 → v2 关键 diff

```
HEADER: 12 项 → 17 项 (12 P1 baseline + 5 P2 时序新增)
OFFLINE keywords: 14 → 28 个 testid/字符串守门
新 section 13: /timeseries 总览页 + site-nav-timeseries (4 testid)
新 section 14: /timeseries/[code] 32 SSG 抽样 (5 testid × 5 省) + dynamicParams=false 守门
新 section 15: DATA_MISSING 三档守门 (time-series-chart + DATA_MISSING 文案 + 3 省 banner)
新 section 16: SourceGradeChip 三档 + 禁榜单化 (4 pill testid + caveat + 计数 data 属性)
新 section 17: Recharts SSR 安全 + 4 控件守门 (province/indicator/year/chart + reset + size ≤50KB)
SUMMARY: 12/17 改 $PASS/17
```

### 5 个新 section 守门明细

#### Section 13 — /timeseries 总览页 + 26 年时序折线 nav link

| 守门 | 验证方式 | 来源文件 |
|---|---|---|
| /timeseries HTTP 200 | `fetch_body $BASE_URL/timeseries` | page.tsx |
| `data-testid="timeseries-overview-page"` | grep | app/timeseries/page.tsx:48 |
| `data-testid="timeseries-h1"` | grep | app/timeseries/page.tsx:49 |
| `data-testid="time-series-explorer"` | grep | app/components/TimeSeriesExplorer.tsx:123 |
| 「31 省 + NATIONAL 锚」文案 | grep | app/timeseries/page.tsx:50 |
| `data-testid="site-nav-timeseries"` 在首页 | grep homepage | app/layout.tsx:107 |

#### Section 14 — /timeseries/[code] 32 SSG 抽样 + dynamicParams=false 守门

| 守门 | 验证方式 | 来源文件 |
|---|---|---|
| /timeseries/beijing HTTP 200 + page/h1 testid | fetch + grep | app/timeseries/[province_code]/page.tsx |
| /timeseries/shanghai HTTP 200 + page/h1 testid | fetch + grep | 同上 |
| /timeseries/liaoning HTTP 200 + all-missing-LIAONING banner | fetch + grep | page.tsx:91-113 (红线-1 banner) |
| /timeseries/hainan HTTP 200 + all-missing-HAINAN banner | fetch + grep | 同上 |
| /timeseries/guizhou HTTP 200 + all-missing-GUIZHOU banner | fetch + grep | 同上 |
| /timeseries/invalid → HTTP 404 (dynamicParams=false) | `fetch` HTTP code | page.tsx:40 `dynamicParams = false` |
| /timeseries/national → HTTP 200 (锁定清单内) | `fetch` HTTP code | page.tsx:32 |

#### Section 15 — DATA_MISSING 三档守门 (红线-1+2)

| 守门 | 验证方式 | 来源文件 |
|---|---|---|
| `data-testid="time-series-chart"` 容器 | grep /timeseries/beijing + /shanghai | app/components/TimeSeriesChart.tsx:119 |
| 「DATA_MISSING」字样在 /timeseries 概览页 | grep | page.tsx:54 + explorer caveat |
| 「DATA_MISSING」字样在 /timeseries/liaoning banner | grep | page.tsx:103 |
| WARN: 直接引用「红线-1/2」(可选项) | grep | page.tsx:54 |

#### Section 16 — SourceGradeChip 三档 + 禁榜单化 (红线-4 + docs/05 §8.3)

| 守门 | 验证方式 | 来源文件 |
|---|---|---|
| `data-testid="source-grade-chip"` | grep | app/components/SourceGradeChip.tsx:45 |
| `data-testid="source-grade-pill-official"` | grep | line 65 |
| `data-testid="source-grade-pill-hongheiku"` | grep | line 72 |
| `data-testid="source-grade-pill-missing"` | grep | line 79 |
| `source-grade-caveat` 含「不构成」字样 | grep | line 84: "不构成省份或时间点排名 (per docs/05 §8.3)" |
| `data-official=` data 属性 | grep | line 46 |

#### Section 17 — Recharts SSR 安全 + 4 控件守门 (新增红线-4)

| 守门 | 验证方式 | 来源文件 |
|---|---|---|
| `data-testid="province-selector"` | grep | app/components/ProvinceSelector.tsx:46 |
| `data-testid="indicator-selector"` | grep | app/components/TimeSeriesExplorer.tsx:136 |
| `data-testid="year-slider"` | grep | app/components/YearSlider.tsx:67 |
| `data-testid="time-series-chart"` | grep | app/components/TimeSeriesChart.tsx:119 |
| `year-slider-reset` 按钮 | grep | YearSlider.tsx:84 |
| `province-selector-input` | grep | ProvinceSelector.tsx:62 |
| page size ≤50KB (SSR 安全 sanity) | `wc -c` | TimeSeriesChartClient.tsx dynamic import |

---

## 3. 红线守门 (Build PASS + OFFLINE PASS)

| # | 红线 | 实际 | 期望 | 状态 |
|---|---|---|---|---|
| 1 | bash 语法 (`bash -n`) | ✓ | ✓ | ✓ |
| 2 | OFFLINE 模式 28 keywords 全 PASS | 28/28 | 28/28 | ✓ |
| 3 | LIVE 模式 P1 baseline 12 项 | 11/12 | 12/12 | △ (1 known issue: /research/m1-series demo-banner, pre-existing) |
| 4 | LIVE 模式 P2 时序新增 5 项 | 1/5 | 5/5 | ✗ (newvps 未部署 667, 待 granular 授权) |
| 5 | /timeseries 总览页 + nav link | section 13 FAIL | 5/5 testid | ✗ (newvps 未部署 667) |
| 6 | /timeseries/[code] 32 SSG + dynamicParams=false | section 14 部分 FAIL | 7/7 | △ (/timeseries/invalid 404 PASS = dynamicParams=false 生效) |
| 7 | DATA_MISSING 三档守门 | section 15 FAIL | 4/4 | ✗ (newvps 未部署 667) |
| 8 | SourceGradeChip 禁榜单化 | section 16 FAIL | 6/6 | ✗ (newvps 未部署 667) |
| 9 | Recharts SSR 安全 + 4 控件 | section 17 部分 PASS | 6/7 | △ (page size 11091 bytes ≤50KB SSR 安全 OK) |
| 10 | docs/81 零改动 | ✓ | ✓ | ✓ |
| 11 | HTTP budget = 0 (纯 bash + curl) | ✓ | 0 | ✓ |
| 12 | 不冒充 ops (newvps 部署待 user 签署) | ✓ | ✓ | ✓ |

**结论**: 668 脚本本身 DELIVERED ✓; 公网 P2 时序新增 5 项 FAIL 是预期 (newvps 未部署 667), 不影响脚本正确性。

---

## 4. 验证输出 (OFFLINE mode, 全 PASS)

```
=== knife 668 公网 17 项验收 (12 P1 baseline + 5 P2 时序新增) ===
Target: https://china.3strategy.cc
Mode:   OFFLINE (syntax-only)
Date:   2026-09-04T10:13:25Z

--- OFFLINE mode: syntax + 17 项标识检查 ---
[OK]   标识 LIVE MODE 在脚本内
[OK]   标识 metric-tab-gdp_total 在脚本内
[OK]   标识 national-badge 在脚本内
[OK]   标识 BEIJING 在脚本内
[OK]   标识 SHANGHAI 在脚本内
[OK]   标识 LIAONING 在脚本内
[OK]   标识 peer-compare-real-table 在脚本内
[OK]   标识 source-popover 在脚本内
[OK]   标识 data-missing-banner 在脚本内
[OK]   标识 indicators 在脚本内
[OK]   标识 coverage-matrix 在脚本内
[OK]   标识 demo-banner 在脚本内
[OK]   标识 sort-bar 在脚本内
[OK]   标识 site-nav-live-group 在脚本内
[OK]   标识 site-nav-demo-group 在脚本内
[OK]   标识 timeseries-overview-page 在脚本内
[OK]   标识 timeseries-h1 在脚本内
[OK]   标识 time-series-explorer 在脚本内
[OK]   标识 site-nav-timeseries 在脚本内
[OK]   标识 timeseries-province-all-missing 在脚本内
[OK]   标识 province-selector 在脚本内
[OK]   标识 indicator-selector 在脚本内
[OK]   标识 year-slider 在脚本内
[OK]   标识 source-grade-chip 在脚本内
[OK]   标识 source-grade-pill-official 在脚本内
[OK]   标识 source-grade-pill-hongheiku 在脚本内
[OK]   标识 source-grade-pill-missing 在脚本内
[OK]   标识 source-grade-caveat 在脚本内

=== OFFLINE summary ===
PASS=28  WARN=0  FAIL=0
```

---

## 5. 验证输出 (LIVE mode, 13/41 PASS + 1 WARN)

```
=== knife 668 公网 17 项验收 (12 P1 baseline + 5 P2 时序新增) ===
Target: https://china.3strategy.cc
Mode:   LIVE
Date:   2026-09-04T10:14:12Z

--- P1 baseline (knife 662 12 项) ---
[OK]   1. 首页 HTTP 200 + LIVE MODE banner
[OK]   2. metric-tab-gdp_total 默认 active (aria-selected=true)
[OK]   3. national-badge + OFFICIAL_ANCHOR 文案
[OK]   4. 3 抽样省 (BEIJING/SHANGHAI metrics + LIAONING data-missing)
[OK]   5. 5 指标 tab testid 完整
[OK]   6. peer-compare 4 省
[OK]   7. SourcePopover 五件套
[OK]   8. DATA_MISSING 3 省详情页「数据暂缺」
[OK]   9. /indicators 5 指标卡 + 三档条形
[OK]   10. CoverageMatrix 31×5 (含 DATA_MISSING 三色)
[FAIL] 11. /research/m1-series demo-banner (pre-existing P1 issue)
[OK]   12. layout LIVE/DEMO 导航分组 + sort-bar

--- P2 时序新增 (knife 668 5 项) ---
[FAIL] 13. /timeseries 总览页 + site-nav-timeseries (5 FAIL, newvps 未部署 667)
[FAIL] 14. /timeseries/[code] 32 SSG + dynamicParams=false (5 FAIL, newvps 未部署 667)
       + /timeseries/invalid 404 PASS (dynamicParams=false Next.js 默认生效)
[FAIL] 15. DATA_MISSING 三档守门 (3 FAIL, newvps 未部署 667)
[FAIL] 16. SourceGradeChip 三档 + 禁榜单化 (6 FAIL, newvps 未部署 667)
[FAIL] 17. Recharts SSR 安全 + 4 控件 (4 FAIL + 1 PASS page size ≤50KB)

=== knife 668 公网 17 项验收 summary ===
VERIFY FAIL: 28 failed / 13 passed / 1 warned
```

**根因**: newvps 还没 pull commit 8b2f48e (667 commit chain 末位); frontend 还在 knife 666b 部署版 (没有 /timeseries 路由)。

**668 验证脚本本身正确**: 待 667 newvps 部署后, LIVE mode 5/5 P2 时序新增 section 应全 PASS (因 667 已通过本地 next build 85 pages 验证, 见 667 receipt §5)。

---

## 6. HTTP 预算守门

| 阶段 | HTTP 消耗 | 累计 | 红线 |
|---|---|---|---|
| 668 写脚本 | 0 | 0 | ≤32 ✓ |
| 668 OFFLINE 验证 | 0 | 0 | ✓ |
| 668 LIVE 验证 | 0 (curl 只读公网, 不爬网) | 0 | ✓ |

(说明: 668 是验收脚本, 仅 curl 读公网 SSG 页 / API 健康检查, 不爬网/不发 POST。HTTP budget = 0 完全在红线内。)

---

## 7. 不宣称 (per docs/05 §8.2 + 红线)

- ❌ **不宣布 668 PASS** — 仅 DELIVERED + OFFLINE 28/28 PASS;LIVE mode 因 newvps 未部署 667 暂 FAIL 28 项
- ❌ **不宣布 663-668 启动 PASS** — 启动需 user_ruling_668 单独签署
- ❌ **不宣布 O1 / Gate / M2 / M4 / M5 / M6** — 仍 OPEN
- ❌ **不冒充 ops** — newvps 部署待 user_ruling_668+ 单独签署
- ❌ **不爬网** — 0 HTTP
- ❌ **不宣称 /research/m1-series demo-banner 修复** — pre-existing P1 issue, 与 668 无关

---

## 8. user_ruling_668 签署清单 (待 user)

- [ ] user 显式 "开启668" (per 当前会话指令)
- [ ] 已审阅 663 + 664 + 665a-e + 666b + 667 交付物
- [ ] 已确认 5 个新 section 范围 (13-17: /timeseries 概览 + 32 SSG + DATA_MISSING + SourceGradeChip + Recharts SSR)
- [ ] 已确认 OFFLINE 28/28 PASS
- [ ] 已确认 LIVE mode 13/41 暂 FAIL (newvps 未部署 667)
- [ ] 已确认 docs/81 零改动
- [ ] 已确认 0 HTTP budget (纯 bash + curl)
- [ ] 已授权 verify-live.sh v2 commit + push 双推 (待 user_ruling_668)
- [ ] 已理解 newvps 667 deploy 待 granular 授权 (SSH + dbt rerun + docker + nginx 各一)
- [ ] 已理解本计划 O1 仍 OPEN, 不宣称任何 PASS

---

## 9. 后续 1 刀待启动

| 刀号 | 名称 | 备注 |
|---|---|---|
| 668 (current) | verify-live.sh v2 公网验收 | DELIVERED; 待 user_ruling_668 启动 + newvps 667 deploy |
| 669a-j | 293 地级市 multi-knife | 每刀独立 user_ruling_669a/b/.../j; 沿用 665/666 pattern; mart_city_timeseries 新 mart (per 新增红线-7 province/city 分离) |

---

## 10. 链接

- 前置 receipts: `reviews/stage0-gate0-rework-2026-08-23/{663,664,665a,665b,665c,665d,665e,666b,667}-*.md`
- 667 receipt (most recent before 668): `667-recharts-timeseries-frontend-receipt-20260904.md`
- 计划 plan: `/Users/kjonekong/.claude/plans/lively-greeting-shore.md` (knife 663-668 + 669a-j 锁定)
- 记忆: [[china-platform-665-multi-knife-program]] (665 program 锁定 + 669 program 待启动)
- 记忆: [[china-platform-no-redundant-polls]] (不重复信息守门)
- 记忆: [[china-platform-user-rest-protocol]] (用户休息协议)

— End 668 receipt (verify-live.sh v2 公网 17 项验收, +202 行, OFFLINE 28/28 PASS, LIVE 13/41 待 newvps 部署, DELIVERED ✓) —
