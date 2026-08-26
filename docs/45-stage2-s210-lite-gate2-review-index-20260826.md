# 45 — Stage 2 / S2.10-lite / Gate 2 评审索引（缩刀落地）

> 起草：CC · 2026-08-26 · queue_rev 97
> 前置：`249` docs/44 规划 PASS；`docs/08` §3.2（Gate 2 七条）；`docs/34` §2/§3；`docs/10` §3.1-3.5
> 用户裁定：**D**（缩刀节奏）+ Stage 2 **C**
> 任务书：`250-stage2-s210-lite-gate2-index-tasking-20260826`
> 刷新：queue_rev 103（per `259-stage2-gate2-index-s27b-refresh-tasking-20260826`）— §2 #1 + §5.5 + §6.1 反映 S2.7-b-lite 收口（回执 `257` + commit `c8ee2b9`/`cd936ab`）
> 刷新：queue_rev 108（per `268-stage2-gate2-index-s27bf-refresh-tasking-20260826`）— §2 #1 + §5.6 + §6.2 反映 S2.7-b-full-lite 收口（回执 `266` + commit `beea282`/`0e0a6cf`）— mart-shape TS 类型 + demo fixture + CityPage 接驳（feature-flag；默认 demo）
> 刷新：queue_rev 119（per `284-stage2-docs45-o1-no-sample-tasking-20260826`）— §3 O1 登记用户 2026-08-26 无材料裁定（演示继续 mock；Gate 2 必带 OPEN 清单）— 不得伪造样本/不得爬网/不擅自 O1 收口
>
> ⚠ **本文件是 Gate 2 评审索引；不宣布 Gate 2 PASS**（per `docs/34 §1` + §8 #8 + §133 + `247` §红线 + `250` §红线）

---

## 1. 索引目的

把 Gate 2 评审所需的 **7 条验收 ↔ 证据路径** 装订到一页 markdown，供 Cursor 评审 + 用户裁定使用。本文件**只是索引**，不补 dbt、不补 UI、不补 pytest case（per tasking `250` §SCHEMA "本刀不做"）。

**Gate 2 评审日期**：暂定 W8（per `docs/34 §10.4`；不擅自提前）。

---

## 2. Gate 2 七条 ↔ 证据路径（per docs/08 §3.2 + docs/44 §2）

| # | 验收项 | 阶段来源 | 证据路径 | OPEN |
|---|---|---|---|---|
| **1** | 5 省 + 10 地市观察页面上线 | S2.7 | 5 省 lite：`frontend/app/provinces/{jiangsu,zhejiang,guangdong,shandong,sichuan}/page.tsx`；10 地市 lite：`frontend/app/cities/[slug]/page.tsx`（`generateStaticParams` 预生成 10 slug；`dynamicParams = false` 404 兜底）| ✅ S2.7-b-lite 已交（mock 壳）— 回执 `257`；mart-shape 接驳（feature-flag；默认 demo）— 回执 `266`；dbt mart 真表 / person/tenure 真数据仍 OPEN → S2.7-b-full 真数据迁移刀 |
| **2** | 六段证据链完整可点击 | S2.6 + S2.7 | `frontend/app/components/EvidenceChain.tsx` + 反例 trigger `schema/migrations/013_counterexample_gate.sql` | ✅ 不可降级 — 已守（lite UI + migration 013）|
| **3** | 七维度观察卡可展开 | S2.8 | `frontend/app/components/SevenDimGrid.tsx` + `frontend/lib/types_seven_dim.ts` + `frontend/lib/mock_seven_dim.ts` | ✅ 演示级可过 |
| **4** | 没有「官员能力总分」 | PRD 红线 + docs/08 §3.3 | `frontend/smoke-check.py` + file-level forbidden-token guard（每次新文件 CLEAN） | ✅ 已守门 |
| **5** | 每条 governance 观察标注 INFERENCE/JUDGMENT | S2.5 + S2.7 | `schema/migrations/012_inference_alignment.sql` + `frontend/lib/types_seven_dim.ts` §2.5 | ✅ 已交 |
| **6** | 至少 1 个反例被显式登记并展示 | S2.6 | `schema/migrations/013_counterexample_gate.sql` + `docs/41-stage2-s26-counterexample-plan-20260826.md` | ✅ 已交（trigger + 规划）|
| **7** | docs/10 测试 §3.1-3.5 全过 | Stage 2 收口 | 跨 lite 回归：`tests/test_*_s*lite.py`（当前 42/42 PASS）| ⚠️ 3.1 + 3.5 已交 schema/types；3.2-3.4 待 S2.10 落地刀（tasking 251+）|

---

## 3. Stage 1 OPEN 显式携带（per docs/34 §3 + docs/44 §4）

| OPEN | 状态 | Gate 2 必带？|
|---|---|---|
| **O1** 真实 SHA-locked 江苏样本 | **S1.18 DEMO 路径 OPEN — 用户 2026-08-26 确认无持有材料**（per `284` 缩刀任务书）| ✅ **必带**（per docs/34 §3 + §120）|
| **O2** cron / 通知 / 真实联外探针 | Stage 1 运维 OPEN | ⚠️ 演示级可过 |
| **O3** OCR 生产路径 | S1.17 scanned PDF OPEN | ⚠️ NBS 数字演示可过；建议 Gate 2 前补 1 条生产路径 |
| O4 `is_demo` 机制 | ✅ 已交（S1.18）| — |
| O5 docs/10 测试 | 部分已交（3.1/3.5）| ⚠️ 3.2-3.4 留 stub（Stage 3 收口）|
| O6 FastAPI 只读服务 | ✅ 已交（S1.10）| — |
| O7 dbt staging candidate | ✅ 已交（S1.19）| — |

**O1 详细状态（per `284` §SCHEMA + 用户 2026-08-26 裁定）**：
- **用户 2026-08-26 确认**：本机/仓库**未持有**江苏真实 SHA-locked 样本；无 OCR 后入库的江苏政府文件。
- **演示路径**：继续走 `lib/mart_city_demo.ts` 的 S1.18 DEMO sentinel；`lineage.source_file_sha256` 恒为 `'0'*64` 占位（per docs/47 §3.1 ⚠️）。
- **不伪造**：禁止假造江苏政府文件 SHA；禁止拿 mock fixture 冒充真实样本；禁止拿 cursor-demo 等替代物冒充（per `284` §SCHEMA "本刀不做" + docs/06 §6.6 红线）。
- **不爬网**：不 HTTP 抓政府站；不调用第三方 API 抓江苏 GDP / 财政 / 履历（per `284` §SCHEMA "本刀不做" + `284` §红线）。
- **Gate 2 评审必带 OPEN**：Gate 2 评审包必须显式携带 O1 OPEN 清单（per docs/34 §3 + §120）；不擅自宣布 O1 收口。
- **收口路径**：O1 真实 SHA 由用户后续提供（线下渠道：政府文件 PDF/扫描件原件）；收口前 demo 恒占位（per docs/47 §6.3 切刀风险 + `284` §SCHEMA）。
- **依赖**：S2.7-b-full 真数据迁移刀（tasking 26X+ OPEN）依赖 O1 真实 SHA 收口（per docs/45 §5.5 OPEN + docs/47 §6.3）。

---

## 4. docs/10 §3.1-3.5 方法层测试当前覆盖度（per docs/44 §3）

| 测试 | 当前覆盖度 | pytest 文件 | Gate 2 要求 |
|---|---|---|---|
| §3.1 同类比较匹配依据 | ✅ schema + types 已交 | （待 S2.10 落地刀）| ✅ 必过 |
| §3.2 回归模型参数 | ⚠️ Stage 3 收口 | xfail stub | stub 即可 |
| §3.3 缺失值处理 | ⚠️ Stage 3 收口 | xfail stub | stub 即可 |
| §3.4 因果设计假设 | ⚠️ Stage 3 收口 | xfail stub | stub 即可 |
| §3.5 归因措辞 | ✅ schema + types 已交 | （待 S2.10 落地刀）| ✅ 必过 |

**守门**：Gate 2 评审需 §3.1 + §3.5 pytest 通过；§3.2-3.4 留 xfail 占位 + 标 "Stage 3 收口"。

---

## 5. Gate 2 演示场景验证清单（per docs/44 §5）

### 5.1 5 省 lite 页面（验收项 #1）

| 省 | 路径 | 状态 |
|---|---|---|
| 江苏 (focal) | `frontend/app/provinces/jiangsu/page.tsx` | ✅ S2.7-a2 已交 |
| 浙江 (peer) | `frontend/app/provinces/zhejiang/page.tsx` | ✅ S2.7-a 已交 |
| 广东 (peer) | `frontend/app/provinces/guangdong/page.tsx` | ✅ S2.7-a 已交 |
| 山东 (peer) | `frontend/app/provinces/shandong/page.tsx` | ✅ S2.7-a 已交 |
| 四川 (peer) | `frontend/app/provinces/sichuan/page.tsx` | ✅ S2.7-a 已交 |

### 5.2 六段证据链可点击（验收项 #2）

| 段 | UI 渲染 | 反例登记 |
|---|---|---|
| `CONDITION` | ✅ EvidenceChain.tsx | — |
| `COMMITMENT` | ✅ EvidenceChain.tsx | — |
| `PROCESS` | ✅ EvidenceChain.tsx | — |
| `OUTPUT` | ✅ EvidenceChain.tsx | ✅ migration 013 trigger |
| `OUTCOME` | ✅ EvidenceChain.tsx | — |
| `FEEDBACK` | ✅ EvidenceChain.tsx | — |

### 5.3 七维度观察卡（验收项 #3）

| 维度 | UI 渲染 | 折叠/展开 |
|---|---|---|
| `POLICY_DELIVERY` | ✅ SevenDimGrid.tsx | ✅ |
| `FISCAL_EXECUTION` | ✅ SevenDimGrid.tsx | ✅ |
| `PROJECT_DELIVERY` | ✅ SevenDimGrid.tsx | ✅ |
| `ECONOMIC_ADAPTATION` | ✅ SevenDimGrid.tsx | ✅ |
| `PUBLIC_SERVICES` | ✅ SevenDimGrid.tsx | ✅ |
| `RISK_MANAGEMENT` | ✅ SevenDimGrid.tsx | ✅ |
| `GOAL_CONSISTENCY` | ✅ SevenDimGrid.tsx | ✅ |

### 5.4 同类地区对比（验收项 #1 配套）

| 组件 | 状态 |
|---|---|
| `frontend/app/components/PeerCompareCard.tsx` | ✅ S2.9-lite 已交 |
| `frontend/lib/types_peer_compare.ts`（8 enum + 5 isValid*）| ✅ |
| `frontend/lib/mock_peer_compare.ts`（江苏 + 浙粤鲁 4 维度匹配）| ✅ |

### 5.5 10 地市 lite 页面（S2.7-b-lite 收口 — 回执 `257`）

| 地市 | slug | 省份 | 路由 | 状态 |
|---|---|---|---|---|
| 南京 | `nanjing` | 江苏 | `/cities/nanjing` | ✅ S2.7-b-lite 已交（mock） |
| 苏州 | `suzhou` | 江苏 | `/cities/suzhou` | ✅ S2.7-b-lite 已交（mock） |
| 无锡 | `wuxi` | 江苏 | `/cities/wuxi` | ✅ S2.7-b-lite 已交（mock） |
| 南通 | `nantong` | 江苏 | `/cities/nantong` | ✅ S2.7-b-lite 已交（mock） |
| 杭州 | `hangzhou` | 浙江 | `/cities/hangzhou` | ✅ S2.7-b-lite 已交（mock） |
| 宁波 | `ningbo` | 浙江 | `/cities/ningbo` | ✅ S2.7-b-lite 已交（mock） |
| 温州 | `wenzhou` | 浙江 | `/cities/wenzhou` | ✅ S2.7-b-lite 已交（mock） |
| 广州 | `guangzhou` | 广东 | `/cities/guangzhou` | ✅ S2.7-b-lite 已交（mock） |
| 深圳 | `shenzhen` | 广东 | `/cities/shenzhen` | ✅ S2.7-b-lite 已交（mock） |
| 东莞 | `dongguan` | 广东 | `/cities/dongguan` | ✅ S2.7-b-lite 已交（mock） |

**OPEN（推 S2.7-b-full 真数据迁移刀）**：
- `dbt/models/marts/mart_city_evidence_chain.sql` + `mart_city_seven_dim_overview.sql`（per docs/47 §3.1/§3.2）
- person/tenure 真数据接入契约（per docs/47 §3.3 OPEN）
- 依赖：**O1 真实 SHA 收口 + Stage 1 OPEN 收口 + S2.1-lite `mart_person_tenure` PASS**（per docs/34 §3 + docs/47 §6.3 切刀风险）
- 路线图：S2.7-b-full 真数据迁移刀（tasking 26X+；OPEN）= 接 dbt mart 真表 + 接 person/tenure 真数据（`relatedPersons` 数组填充）+ lineage.source_file_sha256 从占位 `'0'*64` 替换为 O1 真实 SHA

---

## 6. 不可降级 / 演示级 / OPEN 守门汇总（per docs/44 §6）

| 类别 | 项 | 当前状态 |
|---|---|---|
| **不可降级** | 验收项 #2（六段证据链 UI）| ✅ S2.7 + S2.6-lite 已交 |
| **演示级可过** | 验收项 #1（5 省页面）/ #3（七维度观察卡）/ #1 配套（peer-compare）| ✅ 全部 lite 已交 |
| **已守门** | 验收项 #4（无官员能力总分）| ✅ smoke-check + file-level guard |
| **已交** | 验收项 #5（INFERENCE/JUDGMENT 角标）/ #6（反例 trigger）| ✅ |
| **部分已交** | 验收项 #7（docs/10 §3.1-3.5）| ✅ §3.1/§3.5 schema；§3.2-§3.4 stub |
| **OPEN** | O1 真实 SHA + O3 OCR | ⚠️ Gate 2 评审包必带 OPEN 清单 |
| **OPEN** | 10 地市（S2.7-b）| ✅ S2.7-b-lite（mock 壳）已交 — 回执 `257`；S2.7-b-full-lite（mart-shape 接驳）已交 — 回执 `266`；S2.7-b-full 真数据迁移刀（dbt mart 真表 + person/tenure 真数据）OPEN（tasking 26X+）|

### 6.1 S2.7-b 落地回执登记

| 回执 | 范围 | commit | 状态 |
|---|---|---|---|
| `257-stage0-cc-s27b-lite-impl-receipt-20260826` | S2.7-b-lite（10 地市 mock 壳）| `c8ee2b9` / `cd936ab` | ✅ 已交 |
| `266-stage0-cc-s27b-full-lite-impl-receipt-20260826` | S2.7-b-full-lite（mart-shape TS 类型 + demo fixture + CityPage 接驳；feature-flag；默认 mock）| `beea282` / `0e0a6cf` | ✅ 已交 |

### 6.2 S2.7-b-full-lite mart-shape 接驳路径（回执 `266`）

| 元素 | 路径 | 状态 |
|---|---|---|
| mart-shape TS 类型契约 | `frontend/lib/mart_city_types.ts` | ✅ S2.7-b-full-lite 已交 |
| mart-shape demo fixture（10 城 × 6 段 × 7 cell）| `frontend/lib/mart_city_demo.ts` | ✅ S2.7-b-full-lite 已交 |
| mart-shape 接驳组件（复用三件套）| `frontend/app/components/CityPageMart.tsx` | ✅ S2.7-b-full-lite 已交 |
| Dynamic segment route feature-flag | `frontend/app/cities/[slug]/page.tsx`（`NEXT_PUBLIC_USE_MART_FIXTURE`；默认 mock）| ✅ S2.7-b-full-lite 已交 |
| mart-shape 守门 pytest（10 PASS）| `tests/test_mart_city_types_s27bf.py` | ✅ S2.7-b-full-lite 已交 |
| smoke-check §10 mart-shape 守门 | `frontend/smoke-check.py` §10a–§10e | ✅ S2.7-b-full-lite 已交 |
| lineage.source_file_sha256 占位 | `'0'*64`（O1 真实 SHA 收口前恒占位）| ⚠️ OPEN — 推 S2.7-b-full 真数据迁移刀 |
| person/tenure 真数据接入（`relatedPersons`）| demo 当前 = `[]`（OPEN → S2.7-b-full 接 `mart_person_tenure`）| ⚠️ OPEN — 推 S2.7-b-full 真数据迁移刀 |
| 应用层 enum 守门（runtime + 静态 + 编译时 3 重）| `assertMartRowHasNoForbiddenFields` + smoke-check §10c + pytest `test_*_no_forbidden_tokens` | ✅ 已守门 |

**禁词守门（per docs/06 §6.6 + docs/42 §8 + docs/47 §1.2）**:
- ❌ 不派生 `score` / `rating` / `rank` / `total_score` / `confidence_score` / `credibility_score`
- ❌ 不做"地区得分" / 不做"地区排名" / 不做 `peer_rank`
- ✅ runtime 守门 + 静态 scanner + TS 类型约束（`MartCityEvidenceChainRowProps` 字段白名单）

---

## 7. 红线自检（per `250` §红线）

| 红线 | 状态 |
|---|---|
| ❌ 宣布 Gate 2 PASS | ✅ §1 + §6 + §7 多次显式守门 |
| ❌ 伪造 SHA / 伪造证据 | ✅ 仅索引 + 已交付证据 |
| ❌ 官员能力总分 / 排名 / DSH / 实时数据 | ✅ docs/44 §1.2 + docs/08 §3.3 守门 |
| ❌ 批量爬政策研究 / 财政预决算 / 官员履历 | ✅ 无关 |
| ❌ HTTP 爬源站 | ✅ |
| ❌ 降 OCR 门槛 | ✅ |
| ❌ 改 `gate_thresholds.json` | ✅ |
| ❌ 改 `00-CC-CURRENT.md` | ✅ Cursor 拥有 |
| ❌ --force / --force-with-lease | ✅ ff-only pull |
| ❌ 索要 PAT | ✅ |
| ✅ pack invariant | ⏳ bump + commit 后 597 == 597 == 597（knife 26: docs/45 刷新 + 回执 269 + bump；595 → 597；+2 = bump + receipt）|
| ✅ receipts 仅写 `reviews/stage0-gate0-rework-2026-08-23/` | ✅ |
| ✅ 不改 docs/06 / docs/08 / docs/10 / docs/34 内容（Cursor 拥有）| ✅ |
| ✅ 不擅自提前 Gate 2 评审日期 | ✅ W8（per docs/34 §10.4）|
| ✅ mart-shape 禁词 3 重守门 | ✅ runtime `assertMartRowHasNoForbiddenFields` + 静态 scanner smoke-check §10c + pytest `test_*_no_forbidden_tokens` + 编译时 TS 字段白名单 |
| ✅ mart-shape feature-flag 默认值 | ✅ `NEXT_PUBLIC_USE_MART_FIXTURE !== "1"` 默认走 mock（S2.7-b-lite；保护已交页面） |
| ✅ 兼容 S2.7-b-lite 已交路径 | ✅ [slug]/page.tsx 默认 `getMockCity` + `CityPage`（per receipt 257）；mart-shape opt-in（per receipt 266）|
| ✅ O1 + O8 OPEN 清单显式携带 | ✅ §3 + §5.5 + §6.2（lineage.source_file_sha256 + relatedPersons）推 S2.7-b-full 真数据迁移刀 |

---

## 8. 与 docs/44 的关系

| docs/44 § | docs/45 镜像 |
|---|---|
| §2 七条 ↔ Stage 2 各刀映射 | §2 本文件 |
| §3 docs/10 §3.1-3.5 映射 | §4 本文件 |
| §4 Stage 1 OPEN 继承清单 | §3 本文件 |
| §5 Gate 2 演示场景 | §5 本文件 |
| §6 演示级 vs 不可降级 vs OPEN | §6 本文件 |
| §7 Gate 2 评审脚本清单 | （pytest 落 S2.10 落地刀 tasking 251+）|
| §8-§11 红线/不做/文档关系/CC 建议 | §7 本文件 + `docs/44` 全文 |

---

## 9. CC 建议（供 Cursor 审阅 / 用户裁定）

| 决策点 | 推荐 | 备选 |
|---|---|---|
| Gate 2 评审日期 | W8（per docs/34 §10.4）| 提前到 W6-W7（不推荐）|
| 演示数据策略 | 仅 mock（per docs/34 §141）| 部分真实 SHA（强依赖 O1 收口）|
| docs/10 §3.2-3.4 | xfail stub + "Stage 3 收口"标 | skip（pytest 报告弱）|
| Stage 1 OPEN 必带 | O1 + O3 | 仅 O1 |
| Gate 2 PASS 守门 | receipt/索引严禁 PASS 字样 + Cursor 审验 | 仅红线自检表 |

---

— End of `docs/45` —

> 等待 Cursor 审验（预期 `252-stage0-cursor-s210-lite-index-audit-…md`）。
> 通过后下发 pytest 落地任务（`253-stage2-s210-impl-tasking-…md`），进入 S2.10 实施 pytest case + stub。
> ⚠ **本文件不宣布 Gate 2 PASS**。
> Gate 2 评审日期暂定 W8（per docs/34 §10.4）。