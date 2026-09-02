# mart_flip_frontend_20260902.md — 659 mart flip + 前端切源 报告

> **刀号**: 659 (mart flip + 前端切源 = 页面 GDP 真实化收官刀)
> **日期**: 2026-09-02
> **关联**: docs/84 + 658 audit PASS（完全通过） + 659 tasking signed off（rev103）+ U6 ruling

## 1. 数字验收

| 项 | 值 | 阈值 | verdict |
|---|---:|---|---|
| mart 行数 | 31 (28 数据 + 3 missing) | 31 | **PASS** |
| 真实数据 (官方 5 + 转载 23) | 28 | 28 | **PASS** |
| DATA_MISSING (LN/HAINAN/GUIZHOU) | 3 | 3 | **PASS** |
| 缺失省指标列 NULL 禁补零 | 3/3 NULL | 0 插值 | **PASS** |
| lineage 三重列 | 全行 | 全行 | **PASS** |
| lineage_is_demo | 'false' 全行 | real sentinel | **PASS** |
| USE_MOCK 默认 | false 真数据 | false | **PASS** |
| USE_MOCK env 显式 | `=== "true"` | 翻转后 | **PASS** |
| MOCK_PROVINCE_LIST 默认渲染 | 移除 | 移除 | **PASS** |
| mock 模块文件 | 保留 | 保留 (S1.18) | **PASS** |
| layout banner 文案 | 4 守门点齐 | 4 守门点 | **PASS** |
| docs/81 零改动 | ✓ | 零改动 | **PASS** |
| 既有 registry SHA 零漂移 | ✓ | 零漂移 | **PASS** |
| fixture 4 锁值零触碰 | ✓ | 零触碰 | **PASS** |

## 2. 产物清单 (per 659 §C)

```
dbt/models/marts/mart_province_gdp_2024.sql     (mart model, 152 行)
frontend/lib/api.ts                              (USE_MOCK 语义翻转)
frontend/app/page.tsx                            (去 MOCK_PROVINCE_LIST 默认渲染)
frontend/app/layout.tsx                          (banner 文案更新)
frontend/smoke-check.py                          (§15 knife 659 mart flip 守门)
tests/test_mart_province_gdp_real.py             (新, 22 cases)
tests/test_frontend_mart_demo_parity_s296.py     (§8 扩展, 11 新 cases real-parity 28 省)
evidence_pack/mart_province_gdp_2024_flip_20260902.json  (mart flip evidence)
docs/84-mart-flip-frontend-real-20260902.md       (架构师级审查)
docs/reports/mart_flip_frontend_20260902.md      (本报告)
reviews/.../659-stage0-cc-mart-flip-frontend-real-receipt-20260902.md  (13 节回执)
```

## 3. 关键 knife 节点

- **658-A.2 P3-1**: docs/82 §1.2 31 行全对账 (25 R + 4 B + 2 M2-only)
- **658-P3-2 终修**: docs/82 rows 12-19 刀号按链 SHA 实证逐一更正（`936640d`/`fce3153`/`d13b3229`/`04721b7`/`52a1ad7`/`c3387f0`/`86314f9c`） + §3 归属列对齐 docs/80 §5.1 + 循环自证全删
- **659-§1.659**: mart flip 31 行守门 (28 数据 + 3 DATA_MISSING)
- **659-§1.659-A**: 前端 USE_MOCK 语义翻转 + page.tsx 去 mock 默认渲染 + layout banner 文案更新 + smoke §15 守门

## 4. 红线 14 + U6 §5 附加五条

| # | 红线 | 状态 |
|---:|---|---|
| 1 | 不补零 | ✓ (3 missing 指标列 NULL) |
| 2 | 不静默硬编码 | ✓ (UI 显式 LIVE MODE) |
| 3 | 不爬网 | ✓ (0 HTTP, 纯前端切源) |
| 4 | 不改既有 docs | ✓ (docs/82 仅 §1.2 行内 P3-2; docs/81/83 零改动) |
| 5 | SHA 全等 | ✓ (registry SHA 零漂移) |
| 6 | 数据源 (U6 + 金丝雀 5/5) | ✓ (28 数据 = 5 官方 + 23 hongheiku U6) |
| 7 | lineage 三重标注 | ✓ (mart 四列全行) |
| 8 | 本地 | ✓ |
| 9 | 三重留痕 | ✓ |
| 10 | 回执 13 节 | ✓ |
| 11 | spike 蓝本不入库 | ✓ (mart flip 不动 spike; lineage_is_demo='false' 区分) |
| 12 | m2 零 diff | ✓ |
| 13 | 不自动宣布 | ✓ (24 里程碑不宣布) |
| 14 | BLOCKED 留痕 | ✓ (3 missing status + reason) |
| U6 §5-1 | SHA 锁转载字节 | ✓ (28 SHA 全锁 per 658) |
| U6 §5-2 | lineage 三重 | ✓ |
| U6 §5-3 | 不绕反爬 | ✓ (无 HTTP) |
| U6 §5-4 | docs/81 零改动 | ✓ |
| U6 §5-5 | CANARY_FAIL 禁部分采信 | ✓ (金丝雀 5/5 PASS) |

## 5. 落定收官

**659 = 页面 GDP 真实化收官刀** (mart flip + 前端切源):
- mart 31 行守门 ✓
- 前端 USE_MOCK 语义翻转 ✓
- 3 缺失省 UI "数据暂缺" 状态 ✓
- 22 + 11 新 test cases PASS ✓
- 19 文件集回归 0 失败 ✓
- 红线 14 + U6 §5 附加五条全 ✓

**收官叙事** (per 657 审计"页面真实化倒数第二刀"预叙): 659 = 收官; 660 = next 待签发。

— End mart_flip_frontend 报告 20260902 —
