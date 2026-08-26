# 45 — Stage 2 / S2.10-lite / Gate 2 评审索引（缩刀落地）

> 起草：CC · 2026-08-26 · queue_rev 97
> 前置：`249` docs/44 规划 PASS；`docs/08` §3.2（Gate 2 七条）；`docs/34` §2/§3；`docs/10` §3.1-3.5
> 用户裁定：**D**（缩刀节奏）+ Stage 2 **C**
> 任务书：`250-stage2-s210-lite-gate2-index-tasking-20260826`
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
| **1** | 5 省 + 10 地市观察页面上线 | S2.7 | 5 省 lite：`frontend/app/provinces/{jiangsu,zhejiang,guangdong,shandong,sichuan}/page.tsx` | ⚠️ 10 地市 OPEN（S2.7-b tasking 待发）|
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
| **O1** 真实 SHA-locked 江苏样本 | S1.18 DEMO 路径 OPEN | ✅ **必带**（per docs/34 §3 + §120）|
| **O2** cron / 通知 / 真实联外探针 | Stage 1 运维 OPEN | ⚠️ 演示级可过 |
| **O3** OCR 生产路径 | S1.17 scanned PDF OPEN | ⚠️ NBS 数字演示可过；建议 Gate 2 前补 1 条生产路径 |
| O4 `is_demo` 机制 | ✅ 已交（S1.18）| — |
| O5 docs/10 测试 | 部分已交（3.1/3.5）| ⚠️ 3.2-3.4 留 stub（Stage 3 收口）|
| O6 FastAPI 只读服务 | ✅ 已交（S1.10）| — |
| O7 dbt staging candidate | ✅ 已交（S1.19）| — |

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
| **OPEN** | 10 地市（S2.7-b）| ⚠️ S2.7-b tasking 待发 |

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
| ✅ pack invariant | ⏳ bump + commit 后 570 == 570 == 570 |
| ✅ receipts 仅写 `reviews/stage0-gate0-rework-2026-08-23/` | ✅ |
| ✅ 不改 docs/06 / docs/08 / docs/10 / docs/34 内容（Cursor 拥有）| ✅ |
| ✅ 不擅自提前 Gate 2 评审日期 | ✅ W8（per docs/34 §10.4）|

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