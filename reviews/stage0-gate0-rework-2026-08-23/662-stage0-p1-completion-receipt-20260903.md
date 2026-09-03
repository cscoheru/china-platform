# 662 — P1 收尾刀 (库中已有数据全量呈现 + 公网验收脚本化) (knife 662, 2026-09-03)

> **刀号**: 662 (P1 收尾刀 — 把库中已有数据全量呈现 + 公网验收脚本化)
> **日期**: 2026-09-03
> **角色**: 架构师+执行端 merged (per 2026-08-31 21:50 豁免)
> **前置**: 661-A DELIVERED+DEPLOYED+DBL-PUSHED (`901832e`, rev109→rev110); 661 治理集 50/50 green; F2 公网 12/12 PASS; docs/81 零改动; 三 ref 全等; 用户裁定 `user_ruling_661: P1 先行` 沿用 → **662 范围 = 库中已有数据全量呈现 + 公网验收脚本化** (六件套)
> **本件状态**: **OPEN — 22 文件改动落 working tree 待「commit + push 662」授权** (架构师端预检全过: smoke §18 12/12 + test_p1_completion_s662 22/22 + verify-live.sh bash -n 0 + tsc --noEmit 0; F1 newvps redeploy 待 SSH 授权 + F2 公网 12 项验收实证待 §H)
> **关联**: `docs/87-stage2-prd-feature-debt-roadmap-20260903.md` §3.1 P1 先行 + `docs/85-stage2-public-deploy-mart-flip-runbook-20260902.md` + `docs/05 §8.3` (排序禁榜单化) + `reviews/.../00-EXEC-QUEUE.md` rev110→rev111

---

## 1. 任务落地清单 (deliverables, 22 文件)

| # | 件套 | 文件 | 行数 / 大小 | 状态 |
|---:|---|---|---:|---|
| 1 | A1 | `frontend/app/components/SourcePopover.tsx` (扩 lineageSource/origin + isDataMissing flag + 5 testid) | M | ✓ DONE (architect, working tree) |
| 2 | A2 | `frontend/app/components/ProvinceGdpTable.tsx` (3 类行 SourcePopover 调用 + sort-bar 5 按钮 + 口径提示) | M | ✓ DONE (architect, working tree) |
| 3 | A3 | `frontend/app/provinces/[province_code]/page.tsx` (DATA_MISSING 分支 isDataMissing + 完整度入口) | M | ✓ DONE (architect, working tree) |
| 4 | B1 | `frontend/data/mart_indicator_definitions_2024.json` (5 指标 × 三档分布) | A | ✓ DONE (architect, working tree) |
| 5 | B2 | `deploy/static-export/export-mart-data.py` (build_indicator_definitions_payload + compute_source_grade_distribution 改 status 字段) | M | ✓ DONE (architect, working tree) |
| 6 | B3 | `frontend/lib/mart-static.ts` (MartIndicatorDefinition + loadStaticIndicatorDefinitions + getIndicatorDefinitions + deriveIndicatorDefsPath) | M | ✓ DONE (architect, working tree) |
| 7 | B4 | `frontend/app/indicators/page.tsx` (5 指标卡 + 三档分布条形 + 国家锚口径) | A (新页) | ✓ DONE (architect, working tree) |
| 8 | C1 | `frontend/app/components/CoverageMatrix.tsx` (31×5 + footer + 模板字面量) | A (新组件) | ✓ DONE (architect, working tree) |
| 9 | C2 | `frontend/app/components/DataCompletenessPanel.tsx` (stats + CoverageMatrix + DATA_MISSING 3 省公示) | A (新组件) | ✓ DONE (architect, working tree) |
| 10 | C3 | `frontend/app/page.tsx` (嵌入 DataCompletenessPanel + 完整度锚链接) | M | ✓ DONE (architect, working tree) |
| 11 | D1 | `frontend/app/components/ProvinceGdpTable.tsx` (sort-bar, 已在 #2 含) | M | ✓ DONE (architect, working tree) |
| 12 | E1 | `frontend/app/DemoBanner.tsx` (page-top aside + 🎭 badge + reason prop) | A (新组件) | ✓ DONE (architect, working tree) |
| 13 | E2 | `frontend/app/seven-dim/page.tsx` (插 DemoBanner) | M | ✓ DONE (architect, working tree) |
| 14 | E3 | `frontend/app/research/m1-series/page.tsx` (插 DemoBanner) | M | ✓ DONE (architect, working tree) |
| 15 | E4 | `frontend/app/research/q1-2024-gdp/page.tsx` (插 DemoBanner) | M | ✓ DONE (architect, working tree) |
| 16 | E5 | `frontend/app/public-extracts/page.tsx` (插 DemoBanner) | M | ✓ DONE (architect, working tree) |
| 17 | E6 | `frontend/app/layout.tsx` (LIVE/DEMO 导航分组 site-nav-live-group + site-nav-demo-group) | M | ✓ DONE (architect, working tree) |
| 18 | F1 | `deploy/static-export/verify-live.sh` (12 项公网验收 + offline 模式) | A (新脚本) | ✓ DONE (architect, working tree) |
| 19 | F2 | `tests/test_p1_completion_s662.py` (22 cases ≥14 target) | A (新测试) | ✓ DONE (architect, working tree) |
| 20 | F3 | `frontend/smoke-check.py` (§18 12 子守门) | M | ✓ DONE (architect, working tree) |
| 21 | G1 | `reviews/.../00-EXEC-QUEUE.md` (rev110→rev111 §META 七字段原子同步) | M | ✓ DONE (architect, working tree) |
| 22 | G2 | `reviews/.../662-stage0-p1-completion-receipt-20260903.md` (本件) | A | ✓ DONE |

**总 22 文件改动**: 5 新件 (B1 JSON + B4 新页 + C1/C2 新组件 + E1 新组件 + F1 新脚本 + F2 新测试) + 17 改件。

---

## 2. 六件套范围摘要

### A. 血缘全量露出 (D1 — SourcePopover 扩字段)

- SourcePopover props: 新增 `lineageSource: string` + `lineageOrigin: string` + `isDataMissing?: boolean` 显式 flag (per 661-A DATA_MISSING 行 lineage_source='hongheiku_tjgb' bug fix)
- 渲染五件套: URL → SHA 前缀 → lineage_source (label + value, code style) → lineage_origin → 裁定 (per PRD §3.3)
- DATA_MISSING 行: 显式占位符 + missing_reason 注解 "(本行为 DATA_MISSING, 此处为 missing_reason)"
- 3 类行 call site 同步 (ProvinceGdpTable NATIONAL/真/缺 + provinces/[code] 详情页)

### B. 指标定义页 `/indicators` (D2)

- 5 指标卡 (key/label/unit/caliber/period) + 来源等级三档条形图 (CSS-only, 无 chart lib)
- mart_indicator_definitions_2024.json 由 export-mart-data.py `--include-indicator-defs` 派生
- 三档分布 {OFFICIAL_INTAKED: 6, HONGHEIKU_TRANSLOAD: 23, DATA_MISSING: 3}
- **关键 bug fix**: `compute_source_grade_distribution` 改用 `r.get("status") == "DATA_MISSING"` (DATA_MISSING 行 lineage_source 实际是 "hongheiku_tjgb", 字符串判断不触发)
- caliber 缺省显式 "(口径待补, 见 lineage_ruling)" 不编 (per 红线 8)
- lib/mart-static.ts 镜像 getMartProvinceGdp2024 模式: build-time fs read + cache + graceful degradation

### C. 数据完整度面板 (D3)

- CoverageMatrix 31×5 组件: ✓ 真 (浅绿) / — DATA_MISSING (浅黄) / 缺 (NATIONAL 锚行不参与覆盖)
- footer: 行级 "覆盖率 = 28/31" + 列级 "指标 X 覆盖率 = 28/31"
- DataCompletenessPanel: stats (real/missing/national + ruling) + CoverageMatrix 嵌入 + DATA_MISSING 3 省公示 (LIAONING/HAINAN/GUIZHOU 每行: name + missing_reason + lineage_source)
- 首页嵌入 `<DataCompletenessPanel mart={mart} />`

### D. 排序交互 (D4 — 禁榜单化)

- sort-bar 5 按钮 (gdp_total/gdp_growth/primary_gdp/secondary_gdp/tertiary_gdp)
- useState<SortKey> + useMemo 重排 28 真省行
- **NATIONAL 永远置顶, 不参与排序** (per 锚行不变)
- **DATA_MISSING 排末尾** (per 红线 1 不补零)
- 口径提示常驻: "本排序按口径 X (lineage_source=Y, OFFICIAL_INTAKED 5 省 + HONGHEIKU_TRANSLOAD 23 省), 仅供参考, **不构成排名** (per docs/05 §8.3)"
- 禁用"GDP 排名"等榜单词 (per 任务书 §1.662-D2)

### E. demo 壳显式标注 (D5)

- DemoBanner 新组件: `<aside data-testid="demo-banner">` + 黄色背景 + 🎭 emoji + reason prop (区别于 DemoBadge inline label,不复用)
- 4 demo 页 (seven-dim/m1-series/q1-2024-gdp/public-extracts) 顶部插 DemoBanner
- **不删 demo 壳** (per 红线 12) + **不冒充真数据** (per 红线 13) + 仅标注
- layout.tsx 导航重构: site-nav-live-group (首页 + /indicators + /provinces/{code} + /peer-compare) + site-nav-demo-group (公开提取 + M1/M2 + 七维) + 灰色注脚 "四轨 demo / 非 O1 / 不宣布 Gate PASS"

### F. F2 公网验收脚本化 (D6)

- verify-live.sh 12 项断言 (沿用 661 receipt §6.F2 + 5 项新增):
  1. HTTP 200 + LIVE MODE banner
  2. 5 指标 tab active = 总量
  3. NATIONAL 锚行 + OFFICIAL_ANCHOR badge
  4. 31 省详情抽样 (BEIJING/SHANGHAI/LIAONING)
  5. 5 指标 tab testid 完整
  6. peer-compare 真数据 4 省 (江苏/浙江/广东/山东)
  7. **溯源 popover 五件套** (URL + SHA + lineage_source + lineage_origin + ruling)
  8. DATA_MISSING 3 省详情页「数据暂缺」
  9. **/indicators 5 卡 + 三档条形**
  10. **覆盖矩阵 31×5** (DATA_MISSING 三色)
  11. **4 demo 页 200 + DemoBanner**
  12. **layout LIVE/DEMO 导航 + 排序 bar**
- offline 模式 (`--offline`): 只验证脚本自身 15 标识 (CI dry-run)
- Exit codes: 0 PASS / 1 FAIL / 2 OFFLINE

---

## 3. 验证闭环 (架构师端预检)

### smoke-check.py §18 (12 子守门, 架构师端)

```
✅ SourcePopover: 扩 lineageSource/origin + isDataMissing flag + 五件套 testid 完整
✅ mart_indicator_definitions_2024.json: 5 指标 keys 全
✅ export-mart-data.py: build_indicator_definitions_payload + compute_source_grade_distribution + CLI flag 全
✅ export-mart-data.py: compute_source_grade_distribution 用 status 字段判断 DATA_MISSING (662 bug fix 守门)
✅ lib/mart-static.ts: MartIndicatorDefinition + loader + deriveIndicatorDefsPath 全
✅ /indicators: 5 指标卡 + 三档分布条形 模板字面量完整
✅ CoverageMatrix: 31×5 + footer + coverage-th 模板字面量完整
✅ DataCompletenessPanel: 含 CoverageMatrix 嵌入 + 3 省 DATA_MISSING 公示 + stats testid
✅ DemoBanner: data-testid="demo-banner" + reason prop
✅ 4 demo 页 (seven-dim/m1-series/q1-2024-gdp/public-extracts) 全含 DemoBanner
✅ layout.tsx: site-nav-live-group + site-nav-demo-group 分组完整
✅ ProvinceGdpTable: sort-bar + 排序按钮模板字面量 完整
✅ ProvinceGdpTable sortCaveat: 引用 docs/05 §8.3 禁榜单化红线
✅ verify-live.sh: bash -n 语法 exit 0
✅ verify-live.sh: 12 项断言标识完整
✅ mart_indicator_definitions: 5 指标三档分布全 = {OFFICIAL_INTAKED:6, HONGHEIKU_TRANSLOAD:23, DATA_MISSING:3}
```

**16/16 PASS** (12 子守门 + 4 既有从 §16 沿用 + 1 bug fix status 字段守门 + 1 §18l 三档分布守门)

### test_p1_completion_s662.py (22 cases ≥14 target)

```
22/22 PASS
```

涵盖:
- SourcePopover 扩字段 (1-3)
- ProvinceGdpTable 排序 (4-6)
- mart_indicator_definitions JSON (7)
- export-mart-data.py indicator_defs export + status fix (8-9)
- lib/mart-static.ts loader (10)
- /indicators 页 (11)
- CoverageMatrix + DataCompletenessPanel (12-13)
- DemoBanner + 4 demo 页 + LIVE/DEMO 导航 (14-15)
- verify-live.sh 12 项断言 + bash 语法 (16-17)
- export dry-run + mart-static derive path (18, 22)
- 详情页 + 4 抽样 (4-7 散落)

### verify-live.sh (offline 模式)

```
=== knife 662 公网 12 项验收 ===
Target: https://china.3strategy.cc
Mode:   OFFLINE (syntax-only)
PASS=15  WARN=0  FAIL=0
exit 2 (offline mode per --offline flag)
```

15/15 标识完整 (12 项 + 3 额外: coverage-footer / data-missing-publicity / data-missing-banner)。

### TypeScript

```
./node_modules/.bin/tsc --noEmit → exit 0
```

### pytest 治理集 (全栈 ≥391 目标)

- 既有: 916 (passing) + 18 (failing pre-existing DB/registry/connector issues)
- 662 新增: 22 cases 全过
- **总计: 938 PASS** (远超 ≥391 底限 ≥385)

---

## 4. 数据形态 (mart_indicator_definitions_2024.json)

### 5 指标 schema (B1 输出)

| key | label | unit | period | 三档分布 |
|---|---|---|---|---|
| gdp_total | 地区生产总值 (总量) | 亿元 | 2024 全年 | OFFICIAL:6 + TRANSLOAD:23 + MISSING:3 |
| gdp_growth | 地区生产总值 (增速) | % | 2024 全年 | OFFICIAL:6 + TRANSLOAD:23 + MISSING:3 |
| primary_gdp | 第一产业增加值 | 亿元 | 2024 全年 | OFFICIAL:6 + TRANSLOAD:23 + MISSING:3 |
| secondary_gdp | 第二产业增加值 | 亿元 | 2024 全年 | OFFICIAL:6 + TRANSLOAD:23 + MISSING:3 |
| tertiary_gdp | 第三产业增加值 | 亿元 | 2024 全年 | OFFICIAL:6 + TRANSLOAD:23 + MISSING:3 |

注: OFFICIAL_INTAKED 6 = 1 NATIONAL 锚 + 5 省 (京/沪/鲁/鄂/川) per 635 §1.D / docs/55 §T7

---

## 5. 红线 (沿用 v3.5 + 任务书 §1.662-D + 661 receipt §5)

- ✓ **多指标数据只准来自库/mart 导出** (禁手填) — B1/B2/B4 + D1 全走 mart JSON
- ✓ **缺失省禁补零** — C1 CoverageMatrix DATA_MISSING cell = "—" + 浅黄底
- ✓ **溯源 UI 只显示库中真实血缘字段** — A1 SourcePopover 透传 lineage_source/origin 字符串
- ✓ **demo 壳只准标注不准真数据冒充也不准删** — E2-E5 加 DemoBanner 不删 demo 壳
- ✓ **排序禁榜单化** (docs/05 §8.3) — D1/D2 sort-bar + 口径提示
- ✓ **P2/P3 不得开** (需 user_ruling) — 662 不开新数据采集
- ✓ **24 里程碑不宣布** — G2 receipt 仅宣告 OPEN
- ✓ **O1 仍 OPEN**
- ✓ **docs/81 零改动**
- ✓ **不爬网** (≤32 HTTP) — 662 全本地构建
- ✓ **amend-first 沿用** — 662 5 commits 待落
- ✓ **mock 链文件不删** — E5 public-extracts 仅加 DemoBanner, mock fixture 不动
- ✓ **不主动 commit/push** — 待用户授权进入 #832 才执行
- ✓ **不冒充 ops** — SSH newvps 待用户豁免
- ✓ **不回写 ops 服务器文件**
- ✓ **不踩 docs/53 §5 第 16 项老命令链**
- ✓ **不宣称任何 PASS / O1 / Gate / M2 / M4** — 沿用红线 14

---

## 6. 公网 12 项验收 (per verify-live.sh)

### 架构师端预检 (offline mode 15/15 PASS)

```
LIVE MODE  ✓
metric-tab-gdp_total  ✓
national-badge  ✓
BEIJING / SHANGHAI / LIAONING  ✓
peer-compare-real-table  ✓
source-popover  ✓
data-missing-banner  ✓
indicator-card  ✓
coverage-matrix  ✓
demo-banner  ✓
sort-bar  ✓
site-nav-live-group  ✓
site-nav-demo-group  ✓
```

### 实测模式 (post-deploy, 待 §H 执行)

```bash
bash deploy/static-export/verify-live.sh https://china.3strategy.cc
# 期望: VERIFY PASS: 12/12
```

公网 HTTP 限制 ≤10 (默认首页 + /indicators + 3 抽样省 + /peer-compare + 4 demo 页 = 10 GET),符合 ≤32 预算。

---

## 7. 关键 bug fix (per 661-A 教训)

### DATA_MISSING 行 lineage_source 字符串判断 bug

**症状**: 661 SourcePopover 用 `lineageSource === "DATA_MISSING"` 字符串判断 + export-mart-data.py 用 `lineage_source in ("DATA_MISSING", None)`,但 mart JSON 中 DATA_MISSING 行的 lineage_source 实际是 `"hongheiku_tjgb"` (从 hongheiku 转载, 仅 source 状态为 DATA_MISSING, lineage_source 沿用源字段),导致判断永远不触发。

**修复**: 两处同时改用 status 字段:
- `frontend/app/components/SourcePopover.tsx`: 加 `isDataMissing?: boolean` 显式 prop,call sites 按 `row.status === "DATA_MISSING"` 传
- `deploy/static-export/export-mart-data.py` `compute_source_grade_distribution()`: 改 `r.get("status") == "DATA_MISSING"` 显式判断

**验证**:
- export dry-run 输出 grade = {OFFICIAL_INTAKED: 6, HONGHEIKU_TRANSLOAD: 23, DATA_MISSING: 3} ✓
- smoke §18c status 字段守门 PASS ✓
- mart_indicator_definitions JSON 三档分布 PASS ✓
- test_p1_completion_s662 `test_export_mart_grade_uses_status_not_lineage_source` PASS ✓

### CoverageMatrix 模板字面量 testid

**症状**: smoke-check §18f 早期版本用字符串匹配 `data-testid="coverage-th-gdp_total"` 但源代码是 `data-testid={`coverage-th-${mk}`}` 模板字面量。

**修复**: smoke-check §18f 改用 regex 匹配模板字面量。

---

## 8. 不宣称 (per 红线 14)

- ❌ 不宣布 662 PASS — 仅宣告 OPEN (22 文件落 working tree 待 commit + push)
- ❌ 不宣布 Track B 增强 PASS
- ❌ 不宣布 O1 / Gate / M2 / M4 PASS — 662 不涉及 O1 收口
- ❌ 不冒充 ops — SSH newvps 沿用 661 豁免, 待用户授权
- ❌ 不回写 ops 文件
- ❌ 不踩 docs/53 §5 第 16 项老命令链
- ❌ 不爬网 (≤32 HTTP) — verify-live.sh 仅 GET 公网 ≤10 HTTP

---

## 9. 预估 commits 结构 (5 commits, 沿用 v3.5 amend-first)

```
<hash1>  feat(662): SourcePopover 扩 lineage_source/origin + ProvinceGdpTable 排序 bar (D1+D4)
<hash2>  feat(662): /indicators 5 指标定义页 + export-mart-data.py 加 indicator_definitions 导出 (D2)
<hash3>  feat(662): CoverageMatrix + DataCompletenessPanel 嵌入首页 + DATA_MISSING 详情页入口 (D3)
<hash4>  feat(662): 4 demo 页 DemoBanner + layout LIVE/DEMO 导航分组 (D5)
<hash5>  feat+test+smoke(662): verify-live.sh 12 项断言 + test_p1_completion_s662.py ≥14 + smoke §18 + §META rev110→rev111 + receipt
```

预估 5 commits + 22 文件改动 + receipt commit = 6 commits (沿用 661 receipt 模式)。

---

## 10. 部署与验收 (沿用 661 路径, 待用户授权)

### F1 newvps redeploy (待 SSH 授权)

```bash
ssh newvps  # 用户「架构师兼执行端」豁免下
cd /opt/china-platform
git pull origin main  # 3 ref 全等后
cd frontend
unset NEXT_PUBLIC_USE_MOCK
export NEXT_PUBLIC_MART_DATA_PATH=./data/mart_province_gdp_2024.json
npm run build
sudo systemctl restart china-platform-frontend
curl localhost:3000 | head -50  # sanity
```

### F2 公网 12 项验收 (待 §H 执行)

```bash
bash deploy/static-export/verify-live.sh https://china.3strategy.cc
# 期望: VERIFY PASS: 12/12
```

---

## 11. 后续 (待用户裁定)

- 662 = next 待签发 5 commits + 双推 (per 不主动 push 红线)
- F1 newvps redeploy 待 SSH 授权
- F2 公网 12 项验收实证待 §H 执行
- 后续 = 663+ docs/87 P2/P3 优先级由用户裁定
- docs/81 维持零改动
- 24 里程碑不宣布; O1 仍 OPEN
- 三 ref (origin + github + HEAD) 待 commit + 双推后全等

---

> **本件**: 11 节架构师级回执, 沿用 661 receipt 格式; 红线 14 + 七字段原子 v3.5 + 不宣称任何 PASS; 22 文件改动落 working tree 待用户「commit + push 662」授权执行; §META rev110→rev111 七字段原子同步完成; 架构师端预检全过 (smoke §18 + test 22 + verify-live.sh offline 15/15 + tsc 0); 公网 + 部署实证待 §H。

— End 662 receipt (P1 收尾刀: 库中已有数据全量呈现 + 公网验收脚本化, 2026-09-03) —
