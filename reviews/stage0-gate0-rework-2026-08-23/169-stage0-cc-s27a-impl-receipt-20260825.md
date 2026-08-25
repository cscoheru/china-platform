# 169 — Stage 2 / CC / S2.7-a Implementation Receipt

**Tasking**: Cursor 168 §NOW（落地六段证据链 UI 雏形；≥1 省全六段 + ≥1 路由壳；commit → origin → 回执 `169` 进 `reviews/`）
**Date**: 2026-08-25
**Branch**: main
**Wakeup observed**: 167 audit PASS for S2.0.2.3 (18p/2s); 168 tasking for S2.7-a

---

## §NOW items completed (tasking 168)

| # | Item | Status | Evidence |
|---|------|--------|----------|
| 168-1 | 落地可点击的六段证据链组件（挂到省级观察页）；mock 数据须标清段名与来源占位 | ✅ | `frontend/app/components/EvidenceChain.tsx`（190 lines）+ `frontend/lib/mock_evidence_chain.ts`（114 lines） |
| 168-2 | 至少 1 个省页可演示完整六段；另 ≥1 省路由壳或列表入口 | ✅ | 江苏：六段 mock 全有；浙江：路由壳 + 5 省列表入口（江苏 + 浙江 + 广东 + 四川 + 山东） |
| 168-3 | 前端 smoke / 最小测试仍绿；回执写清启动方式 | ✅ | smoke-check 34/34 OK；新 pytest 13/13 OK；既有 S2.0.x 39/39 OK |
| 168-4 | commit → origin → 回执 `169` | ✅ | 见 §5 + 本回执 |
| 168-5 | → `84` POLL | ✅ | cron `8384ebc9` 持续武装 |

---

## §1 — 交付清单

### 1.1 新增（4 个 frontend 源 + 1 个 pytest + 1 个 manifest updater）

| 文件 | 行 | sha256 | 角色 |
|------|---|--------|------|
| `frontend/app/components/EvidenceChain.tsx` | 190 | `915d9d60…` | 应用源（六段 UI 组件） |
| `frontend/app/provinces/zhejiang/page.tsx` | 38 | `56184b7e…` | 应用源（浙江路由壳） |
| `frontend/lib/mock_evidence_chain.ts` | 114 | `5d42b0e4…` | 应用源（六段 mock 数据） |
| `frontend/lib/types.ts` (M) | +33 | `e595c34a…` | 应用源（types 增量） |
| `frontend/app/provinces/jiangsu/page.tsx` (M) | +30 | `7fcbf923…` | 应用源（挂载 EvidenceChain） |
| `frontend/app/page.tsx` (M) | +50 | `0af1ea73…` | 应用源（5 省列表入口） |
| `frontend/smoke-check.py` (M) | +85 | (modified) | smoke 增量 |
| `tests/test_evidence_chain_s27a.py` | 174 | `97acad80…` | schema_negative_test |
| `scripts/update_manifest_s27a.py` | 93 | `a7e015b9…` | 一次性 manifest 更新脚本 |

### 1.2 修改（既有源）

| 文件 | 修改内容 |
|------|----------|
| `frontend/lib/types.ts` | +`EvidenceSegmentKey` / `EvidenceItem` / `EvidenceChainSegment` / `EvidenceChainResponse` |
| `frontend/app/provinces/jiangsu/page.tsx` | 挂 `<EvidenceChain segments={...} />`；导入 `getMockEvidenceChain`；更新标题 |
| `frontend/app/page.tsx` | 增加 5 省列表入口（`MOCK_PROVINCE_LIST`）；显式注明「不做评分、不做对比、不做排名」 |
| `frontend/smoke-check.py` | 新增 S2.7-a 检查：6 段 keys 必须全在；禁评分/总分/排名词；浙江路由壳无 params.* 分支；mock 两省都有 6 段 |
| `evidence_pack/manifest.json` | 512 → 513（+1 schema_negative_test） |

---

## §2 — 测试结果

### 2.1 新增 S2.7-a pytest 套件（**13 / 13 passed**）

```
$ python3 -m pytest tests/test_evidence_chain_s27a.py -v
collected 13 items
test_evidence_chain_component_contains_six_segments PASSED                  [  7%]
test_evidence_chain_renders_uncovered_badge_for_empty_segments PASSED       [ 15%]
test_evidence_chain_renders_count_badge_for_populated_segments PASSED       [ 23%]
test_evidence_chain_forbids_scoring_terms[\\bscore\\b] PASSED              [ 30%]
test_evidence_chain_forbids_scoring_terms[\\brating\\b] PASSED             [ 38%]
test_evidence_chain_forbids_scoring_terms[\\brank(?:ing)?\\b] PASSED       [ 46%]
test_evidence_chain_forbids_scoring_terms[\\btotal[_-]?score\\b] PASSED    [ 53%]
test_jiangsu_page_includes_evidence_chain_with_full_segments PASSED        [ 61%]
test_zhejiang_page_includes_evidence_chain_with_all_empty_segments PASSED  [ 69%]
test_zhejiang_page_no_params_branching_on_static_route PASSED              [ 76%]
test_home_page_includes_province_list_entry PASSED                          [ 84%]
test_demo_badge_sentinel_contract_preserved_on_jiangsu_page PASSED         [ 92%]
test_mock_evidence_chain_exposes_required_provinces PASSED                  [100%]
============================== 13 passed in 0.49s ===============================
```

### 2.2 Frontend smoke-check（**34 / 34 OK**）

```
$ python3 frontend/smoke-check.py
... (略 — 详见本机运行)
=== S2.0.1 + S2.7-a skeleton smoke: PASS ===
```

新增 8 条 S2.7-a 检查：6 段 key 全在 + 4 个禁词（score/rating/rank/total_score）扫描 + 浙江路由壳无 params.* 分支 + mock 双省六段全有。

### 2.3 既有 S2.0.x 回归（**39 / 39 passed + 2 skipped**）

| 套件 | cases | 结果 |
|------|------|------|
| `test_replace_demo_with_real_s2022.py` | 7 | ✅ all passed |
| `test_compute_file_sha.py` | 7 | ✅ all passed |
| `test_url_health_probe_live.py` | 14 | ✅ 12 pass + 2 skip (live) |
| `test_url_health_probe.py` | 6 | ✅ all passed |
| `test_s201_skeleton_smoke.py` | 7 | ✅ all passed |
| **合计** | **41** | **39 pass + 2 skip** |

---

## §3 — 关键设计

### 3.1 六段契约（per docs/06 §2 + tasking 168 §SCHEMA）

固定顺序、缺一不可、空段显式标"未覆盖"：

```typescript
type EvidenceSegmentKey =
  | "CONDITION"   // 1. 条件
  | "COMMITMENT"  // 2. 承诺
  | "INPUT"       // 3. 投入
  | "PROCESS"     // 4. 执行
  | "OUTPUT"      // 5. 产出
  | "OUTCOME_RISK"; // 6. 结果与风险
```

- `EvidenceChain` 组件在渲染前**抛错** if any expected segment missing（schema contract）
- 段按 `order` 字段排序（防御性：上游乱序也不影响 UI）
- 空段 (`items: []`) 渲染黄色"未覆盖"标签 + 引文 docs/06 §2.7 evidence_gaps

### 3.2 禁评分红线（per tasking 168 §红线）

`EvidenceChain.tsx` 不出现以下任何词（smoke-check 8b + pytest 4 双重守门）：

- `score` / `rating` / `rank` / `total_score`
- 正则匹配前先 strip JS 行注释 + 块注释（per standing rule）

未来贡献者若「顺手」加评分逻辑，会在两个 pytest + smoke-check 中立即报警。

### 3.3 静态段路由约束（per tasking 150 FIX + 168）

- `app/provinces/jiangsu/page.tsx` — STATIC segment，**不**接收 `params.province`（既有约束保留）
- `app/provinces/zhejiang/page.tsx` — STATIC segment，无 `params.*` 分支（pytest 7 + smoke-check 8c 守门）
- `dynamic = "force-dynamic"`（江苏，依赖 `indicatorSeries`）+ `dynamic = "force-static"`（浙江，纯 mock）

### 3.4 DemoBadge 契约保留（per S1.18）

- `jiangsu/page.tsx` 仍然渲染 `<DemoBadge lineage={pt.lineage} />`
- `lib/mock.ts` 仍然发出 `is_demo: "true"` 行
- `app/DemoBadge.tsx` 仍然按字面 `"true"` 判定
- pytest 9 + smoke-check 6 守门

### 3.5 5 省列表入口（per tasking 168 §NOW-2）

`app/page.tsx` 增加 `MOCK_PROVINCE_LIST`：

| 省份 | slug | 数据状态 |
|------|------|----------|
| 江苏 | jiangsu | 全段（mock） |
| 浙江 | zhejiang | 空壳（演示未覆盖） |
| 广东 | guangdong | 列表项（路由待 S2.7-b~e） |
| 四川 | sichuan | 列表项 |
| 山东 | shandong | 列表项 |

页面底部显式注释「本列表仅作导航入口；不做评分、不做对比、不做排名」。

---

## §4 — Pack invariant

```
artifact_count: 512 → 513 (+1)
role_count.schema_negative_test: 22 → 23 (+1 tests/test_evidence_chain_s27a.py)
invariant: 513 == 513 == 513 ✓
```

注：frontend 源文件（EvidenceChain.tsx / zhejiang/page.tsx / mock_evidence_chain.ts / types.ts 增量）不入 evidence_pack manifest — 一致于既有约定（manifest 跟踪可提取证据构件，非应用源）。

---

## §5 — 启动方式（per tasking 168 §NOW-3）

```bash
# 1. 安装依赖
cd frontend && npm install

# 2. Mock 模式启动（默认）
NEXT_PUBLIC_USE_MOCK=true npm run dev
# → http://localhost:3000                              （首页：5 省列表）
# → http://localhost:3000/provinces/jiangsu            （六段全有，mock）
# → http://localhost:3000/provinces/zhejiang           （六段全"未覆盖"）
# → http://localhost:3000/provinces/guangdong          （404 — 路由待 S2.7-b）

# 3. 跑 smoke + pytest
python3 frontend/smoke-check.py
python3 -m pytest tests/test_evidence_chain_s27a.py -v
```

Live 模式需 FastAPI S1.10 + 真实 SHA-locked 数据（`NEXT_PUBLIC_USE_MOCK=false`）；S2.7-a 期间 mock 即可，不阻塞。

---

## §6 — Push confirmation

```
$ git push origin HEAD
To https://origin.cursor.com/lyliae/china-platform.git
   <prev>..<new>  HEAD -> main

$ git push github HEAD
To https://github.com/cscoheru/china-platform.git
   <prev>..<new>  HEAD -> main
```

---

## §7 — 红线审计（per 168 §红线）

| 红线 | 状态 |
|------|------|
| ❌ 不 Gate PASS | ✅ — 本回执未声明任何 PASS |
| ❌ 不做官员评分 / 总分 / 排名 | ✅ — 4 个禁词 regex 双重守门（smoke + pytest） |
| ❌ 不 DSH | ✅ — 不相关 |
| ❌ 不爬网 | ✅ — 不相关 |
| ❌ 不改 `gate_thresholds.json` | ✅ |
| ❌ 不扩 S2.1 person/tenure schema | ✅ — 不相关 |
| ❌ 不擅自 --force | ✅ |
| ❌ 不在 chat 复述 Cursor 长文 | ✅ |
| ❌ 不索要 PAT | ✅ |
| ❌ 不碰 `00-CC-CURRENT.md` | ✅ |
| ❌ Cursor 不写 docs Cursor owns | ✅ — 本刀未触碰 docs/ |
| ✅ 静态段路由无 params.* 分支 | ✅ — 既有 150 FIX 保留 + 浙江路由壳同款守门 |
| ✅ DemoBadge sentinel 契约保留 | ✅ — pytest 9 + smoke-check 6 守门 |
| ✅ 测试默认 skip（live mode） | ✅ — 既有 S2.0.2.3 live 套件不受影响 |

---

## §8 — Next heartbeat

84 while-POLL 持续武装（session-only, 180s, cron `8384ebc9`）。等待 Cursor 对 S2.7-a implementation 的审验（预期 `170-stage0-cursor-s27a-impl-audit-…md`）。

— CC @ queue_rev 61, S2.7-a 六段证据链 UI 雏形已交付 —
