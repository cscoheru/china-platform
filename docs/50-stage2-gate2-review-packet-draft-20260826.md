# 50 — Stage 2 Gate 2 评审包（草稿）

> ⚠ **本文是 Gate 2 评审包草稿**（per `315` 缩刀任务书）。
> ⚠ **本包不宣布 Gate 1 / Gate 2 PASS**（per docs/34 §1 + §8 #8 + §133 + `315` §红线）。
> ⚠ **本包不宣布 O1 / O3 收口**（per docs/34 §3 + `284` §SCHEMA + `309` + `docs/49` §5.3）。
> ⚠ **本包不伪造证据**（per docs/06 §6.6 + `315` §红线）。
> ⚠ **本包不爬源站 / 不登录绕过 / 不 OCR 降门槛**（per PRD 红线 + `315` §红线 + docs/49 §2.2）。

> 起草：CC · 2026-08-26 · queue_rev 131
> 前置：`314` docs/45 PASS；`docs/08` §3.2（Gate 2 七条）；`docs/34` §2/§3；`docs/10` §3.1-3.5；`docs/44` §2（Stage 2 Gate 2 评审包规划）
> 用户裁定：**D**；**不宣布 Gate 2 PASS**；O1/O3 必带 OPEN 清单
> 任务性质：**评审包草稿**（per `315` §SCHEMA "本刀做"）— 按七条验收逐条挂证据路径（链到已交回执/页面/测试）；显式 OPEN 清单（O1 WAITING_FILE + O3 规划未实装）；预览 URL；**文首/文末禁止 PASS 措辞**
> Gate 2 评审日期：暂定 W8（per docs/34 §10.4）；**不擅自提前**

---

## §0. 范围 / 红线

### 0.1 本刀做
- 按 **`docs/08 §3.2` Gate 2 七条验收** 逐条挂证据路径（链到**已交回执 / 页面 / 测试 / dbt 验证**）
- 显式 **OPEN 清单**（O1 WAITING_FILE / O3 规划未实装 / docs/10 §3.2-3.4 stub）
- 列出**演示级可过** vs **不可降级** vs **仍 OPEN** 三类
- 预览 URL（演示场景）
- **文首/文末禁止 PASS 措辞**

### 0.2 本刀不做
- ❌ 宣布 Gate 1 / Gate 2 PASS
- ❌ 宣布 O1 / O3 收口
- ❌ 伪造证据（假造 SHA / 假造 PDF / 假造履历）
- ❌ 爬源站 / 登录绕过 / OCR 降门槛 / 未授权 cloud OCR
- ❌ 派生官员评分 / 排名 / DSH / 实时数据
- ❌ 改业务代码 / 改 Cursor 拥有架构文档

### 0.3 红线条目（per docs/34 §1 + §8 + `315` §红线 + docs/49 §2.2 + docs/06 §6.6）
- ❌ 不宣布 Gate 1 / Gate 2 PASS
- ❌ 不擅自收口 O1（真实 SHA-locked 江苏样本，per `284`）
- ❌ 不擅自收口 O3（OCR 生产路径，per `docs/49`）
- ❌ 不派生 score / rating / rank / total_score / confidence_score / credibility_score / peer_rank
- ❌ 不做官员能力总分 / 排名 / DSH / 实时数据
- ❌ 不批量爬政策研究 / 财政预决算 / 官员履历
- ❌ 不 HTTP 爬源 / 不登录绕过 / 不未授权 cloud OCR / 不 symlink / 不伪造
- ❌ 不启用 pgvector / RLS / partition
- ❌ 不改 `gate_thresholds.json`
- ❌ 不碰 `00-CC-CURRENT.md`
- ❌ 不擅自 `--force` / `--force-with-lease`
- ❌ 不替用户下裁定
- ❌ 不在聊天复述 Cursor 长文
- ❌ 不索要 PAT

---

## §1. 评审包结构

| 节 | 内容 | 来源 |
|---|---|---|
| §2 | Gate 2 七条验收 ↔ 证据路径映射表 | docs/08 §3.2 + docs/44 §2 + docs/45 §2 |
| §3 | 不可降级 vs 演示级 vs 仍 OPEN 三类划分 | docs/34 §1 + docs/44 §1.2 |
| §4 | 演示场景（5 省 + 10 地市页面 + EvidenceChain + 七维度）| docs/44 §1.1 + docs/36/37/38/39/40/41/42 |
| §5 | Stage 1 OPEN 继承清单（O1 / O3 必带；O2 / O5 / others 状态）| docs/34 §3 + `284` + `309` + `docs/49` |
| §6 | 评审脚本清单（pytest + smoke-check + dbt + 端到端）| docs/10 §3.1-3.5 + docs/44 §4 |
| §7 | 预览路径（演示管道，**非 O1 收口**）| docs/45 §5.5 + `303` + `297` + `294` |
| §8 | 红线自检 + 不变量 | docs/34 §8 + `315` §红线 + `06` §6.6 |
| §9 | 不可隐藏清单（Gate 2 评审必带）| docs/34 §3 + §120 |
| §10 | 备注 / 不在范围 / 下次心跳预期 | `315` §NOW + `docs/49` §11 |

---

## §2. Gate 2 七条验收 ↔ 证据路径（per docs/08 §3.2 + docs/44 §2 + docs/45 §2）

### 七条原文（per docs/08 §3.2）

| # | 验收项 | 阶段来源 | 不可降级 vs 演示级 vs OPEN |
|---|---|---|---|
| 1 | 5 省 + 10 地市观察页面上线 | S2.7 | **演示级可过**（lite 已交 mock 壳）；dbt mart 真表 / person/tenure 真数据仍 OPEN → S2.7-b-full 真数据迁移刀（tasking 26X+）|
| 2 | 六段证据链完整可点击 | S2.6 + S2.7 | **不可降级** — 已守（lite UI + migration 013）|
| 3 | 七维度观察卡可展开 | S2.8 | **演示级可过**（lite UI + types + mock）|
| 4 | 没有「官员能力总分」| PRD 红线 + docs/08 §3.3 | **不可降级** — smoke-check + file-level forbidden-token guard 已守门 |
| 5 | 每条 governance 观察标注 INFERENCE/JUDGMENT | S2.5 + S2.7 | **不可降级** — migration 012 + types §2.5 已交 |
| 6 | 至少 1 个反例被显式登记并展示 | S2.6 | **不可降级** — migration 013 trigger + docs/41 规划已交 |
| 7 | docs/10 测试 §3.1-3.5 全过 | Stage 2 收口 | **演示级 + 部分必过**（§3.1 + §3.5 schema/types 已交；§3.2-3.4 xfail stub）|

### 证据路径（链到已交回执 / 页面 / 测试）

| # | 验收项 | 证据路径 | 已交回执 / 来源 | 状态 |
|---|---|---|---|---|
| **1** | 5 省 + 10 地市观察页面上线 | **5 省 lite 页面**：`frontend/app/provinces/{jiangsu,zhejiang,guangdong,shandong,sichuan}/page.tsx`<br>**10 地市 lite 页面**：`frontend/app/cities/[slug]/page.tsx`（`generateStaticParams` 预生成 10 slug；`dynamicParams = false` 404 兜底）| `257`（S2.7-b-lite 已交 mock 壳）<br>`266`（mart-shape 接驳；feature-flag；默认 demo）<br>`288`（dbt mart 骨架；WHERE FALSE）<br>`294`（dbt mart demo-join；60+70 demo 行；10 城 × 6 段 / 7 维度；`is_demo='true'`）<br>`297`（前端 mart demo 契约对齐；20 pytest 锁定 TS demo ↔ dbt mart）<br>`303`（S2.7-b person/tenure demo 接驳；10 城 × 2 demo 行 = 20 demo 相关人物行：市委书记 + 市长 mock 占位；TS fixture 主路径；UI 显式 demo 标识；15 pytest 锁定）| ✅ 演示级可过（lite + demo）；dbt mart 真表 / person/tenure 真数据仍 OPEN → S2.7-b-full 真数据迁移刀 |
| **2** | 六段证据链完整可点击 | `frontend/app/components/EvidenceChain.tsx`（CONDITION / COMMITMENT / PROCESS / OUTPUT / OUTCOME / FEEDBACK 六段）<br>反例 trigger：`schema/migrations/013_counterexample_gate.sql` | `255`（S2.6 反例 gate 已交）<br>`257`（lite UI）| ✅ **不可降级** — 已守（lite UI + migration 013）|
| **3** | 七维度观察卡可展开 | `frontend/app/components/SevenDimGrid.tsx`<br>类型契约：`frontend/lib/types_seven_dim.ts`<br>演示 mock：`frontend/lib/mock_seven_dim.ts` | `270`（S2.8 七维度 lite 已交 mock）| ✅ **演示级可过**（lite UI + types + mock）|
| **4** | 没有「官员能力总分」| runtime 守门：`frontend/smoke-check.py` §10 mart-shape 扫描<br>静态守门：file-level forbidden-token guard（每次新文件 CLEAN）<br>禁词列表：`score` / `rating` / `rank` / `total_score` / `confidence_score` / `credibility_score` / `peer_rank` / DSH | `284` + `294` + `297` + `303` + `docs/45 §6.2` 禁词 3 重守门 | ✅ **不可降级** — 已守门 |
| **5** | 每条 governance 观察标注 INFERENCE/JUDGMENT | schema：`schema/migrations/012_inference_alignment.sql`<br>类型：`frontend/lib/types_seven_dim.ts` §2.5 | `251`（S2.5 inference 已交）| ✅ **不可降级** — migration 012 + types §2.5 已交 |
| **6** | 至少 1 个反例被显式登记并展示 | schema trigger：`schema/migrations/013_counterexample_gate.sql`<br>规划：`docs/41-stage2-s26-counterexample-plan-20260826.md` | `255`（S2.6 反例 gate 已交）| ✅ **不可降级** — migration 013 trigger + docs/41 规划已交 |
| **7** | docs/10 测试 §3.1-3.5 全过 | 跨 lite 回归：`tests/test_*_s*lite.py`（当前 42/42 PASS）<br>§3.1 同类比较匹配依据：✅ schema + types 已交<br>§3.2 回归模型参数：⚠️ xfail stub（Stage 3 收口）<br>§3.3 缺失值处理：⚠️ xfail stub（Stage 3 收口）<br>§3.4 因果设计假设：⚠️ xfail stub（Stage 3 收口）<br>§3.5 归因措辞：✅ schema + types 已交 | docs/45 §4 + docs/44 §3 + `315` §SCHEMA | ⚠️ §3.1 + §3.5 已交 schema/types；§3.2-3.4 待 S2.10 落地刀（tasking 251+）；Gate 2 评审**必带 OPEN** |

---

## §3. 三类划分（不可降级 vs 演示级 vs 仍 OPEN）

### 3.1 不可降级（Gate 2 评审必须 100% 通过）

| # | 验收项 | 证据路径 | 守门 |
|---|---|---|---|
| 2 | 六段证据链完整可点击 | `EvidenceChain.tsx` + `migration 013` | ✅ 已守 |
| 4 | 没有「官员能力总分」| `smoke-check.py` + file-level forbidden-token guard | ✅ 已守门 |
| 5 | 每条 governance 观察标注 INFERENCE/JUDGMENT | `migration 012` + `types_seven_dim.ts` §2.5 | ✅ 已交 |
| 6 | 至少 1 个反例被显式登记并展示 | `migration 013 trigger` + `docs/41` 规划 | ✅ 已交 |

### 3.2 演示级可过（Gate 2 评审可演示，不构成 PASS）

| # | 验收项 | 证据路径 | 守门 |
|---|---|---|---|
| 1 | 5 省 + 10 地市观察页面上线 | lite 页面 + demo mart-shape + dbt mart 骨架（WHERE FALSE）+ dbt mart demo-join | ✅ 演示级可过（`257` + `266` + `288` + `294` + `297` + `303`）；真数据仍 OPEN |
| 3 | 七维度观察卡可展开 | lite UI + types + mock | ✅ 演示级可过（`270`）|

### 3.3 仍 OPEN（Gate 2 评审**必带 OPEN 清单**，不擅自收口）

| OPEN | 来源 | 当前状态 | 收口前置 |
|---|---|---|---|
| **O1** 真实 SHA-locked 江苏样本 | S1.18 DEMO 路径 | **WAITING_FILE**（= intake 出口码 / mart 真 SHA 未入仓技术状态语义，非「等用户投喂才可继续」per `484`/`486`/`488`/`490` 对齐；用户 2026-08-26 确认本机/仓库**未持有**江苏真实 SHA-locked 样本；`lineage.source_file_sha256` 恒为 `'0'*64` 占位 per docs/47 §3.1 ⚠️）| 主路径 = docs/52 B 路（公开源自动获取，试点轴 `NATIONAL_BULLETIN` per `480`/`482`）；A 路 = 用户线下渠道（政府文件 PDF/扫描件原件）+ `--confirm-o1=PATH` 显式 flag（仅限 A 路出口）+ intake 4 退出码契约（per `291` + docs/48 §4.3），仍可用但非唯一 |

> [superseded per 591（2026-08-29）· per 2026-08-29 治理铁律：用户无 PDF 数据；数据源唯一=政府/统计局/研究机构自取；执行端自取预 vetted 源走完整 e2e 流水线；零 `--confirm-o1=PATH` 字面；A 路（用户线下渠道）保留为 fallback 标注（不删除、不调用），仅当 B 路（公开源自动获取）无法取得样本时方由架构师夜间授权下自主评估是否启动；O1 §5.2.x 真实 SHA-locked 江苏样本刀待 docs/52 B 路落定后另刀下发；O3 §5.2.6 真实 PDF e2e 收口闭合 per `587-stage0-architect-s586-o3-impl-real-pdf-self-sourced-tasking-20260829.md`（supersede 旧版 `587-stage0-architect-s586-o3-impl-real-pdf-user-action-tasking-20260829.md`）+ `587-stage0-cc-o3-impl-real-pdf-e2e-tasking-20260829-receipt.md`（执行端自取 S0 源 + paddle-ocr MOCK only + 执行端自验闭环）+ `588-stage0-architect-s587-o3-impl-real-pdf-e2e-audit-PASS-20260829.md` PASS audit + §J ⚠1 ACCEPTED with disclosure 标注 + `589-stage0-architect-s588-o3-impl-docs50-supersede-refresh-tasking-20260829.md` O3 row 119 supersede 平行模式 + `590-stage0-architect-s589-o3-impl-docs50-supersede-refresh-audit-PASS-20260829.md` PASS audit + ⚠1 line 121 vs 120 ACCEPTED with disclosure 标注；**O3 整体 CLOSED 候选** per 588 PASS + 590 PASS 双重声明；**O1 整体仍 WAITING_FILE**（per docs/47 §3.1 + 用户 2026-08-26 披露 + 2026-08-29 治理铁律；O1 §5.2.x 真实 SHA-locked 江苏样本刀待 docs/52 B 路落定后另刀下发）；584 重 ACK 触发条件保留 = 用户裁定 + Python 3.12 wheel 可用 + Docker daemon 就绪 + 项目主 deps manifest 决策已定 + Dockerfile（非 current critical path）；本 row 117 原文不删不改（A 路 `用户线下渠道` + `--confirm-o1=PATH` 表述保留为 fallback 标注），supersede 标注与原文共存（per 「不删既有 OPEN 行」红线 + 「不删旧 row」教训模式）]
| **O3** OCR 生产路径 | S1.17 scanned PDF | **规划已交，实装仍 OPEN**（per `docs/49` + `309`）| 用户裁定 OCR 引擎（paddle-ocr 推荐 / tesseract / cloud）+ `--confirm-o3=PATH` + 端到端 pytest PASS（per `docs/49` §5.3 + §8 + §10）|

> [superseded per 589（2026-08-29）· per 2026-08-29 治理铁律：用户无 PDF 数据；数据源唯一=政府/统计局/研究机构自取；执行端自取预 vetted 源走完整 e2e 流水线；零 `--confirm-o3=PATH` 字面；O3 §5.2.6 真实 PDF e2e 收口闭合 per `587-stage0-architect-s586-o3-impl-real-pdf-self-sourced-tasking-20260829.md`（supersede 旧版 `587-stage0-architect-s586-o3-impl-real-pdf-user-action-tasking-20260829.md`）+ `587-stage0-cc-o3-impl-real-pdf-e2e-tasking-20260829-receipt.md`（执行端自取 S0 源 + paddle-ocr MOCK only + 执行端自验闭环）+ `588-stage0-architect-s587-o3-impl-real-pdf-e2e-audit-PASS-20260829.md` PASS audit + §J ⚠1 ACCEPTED with disclosure 标注；**O3 整体 CLOSED 候选** per 588 PASS（§5.2.4 BLOCKED-DEFERRED per 584 + §5.2.5 CLOSED per 585 + §5.2.6 CLOSED per 587）；584 重 ACK 触发条件保留 = 用户裁定 + Python 3.12 wheel 可用 + Docker daemon 就绪 + 项目主 deps manifest 决策已定 + Dockerfile（非 current critical path）；本 row 119 原文不删不改，supersede 标注与原文共存（per 「不删既有 OPEN 行」红线 + 「不删旧 row」教训模式）]

> [superseded per 599（2026-08-29）· **598 audit 落**（per `598-stage0-architect-s597-584-impl-audit-PASS-20260829.md` PASS audit；584 §5.2.4 paddle-ocr 引擎依赖实施刀 = O3 §5.2.4 CLOSED 候选 per 588 PASS + 590 PASS + 597 三重声明 + 598 audit 落 四重声明；docs/50 §5.1 O3 status row 119「规划已交，实装仍 OPEN」追加 598 audit 落标注 共存；不删 row 119 原文 = 「不删既有 OPEN 行」红线 + 「不删旧 row」教训模式 + 589 + 591 + 593 + 595 + 596 + 597 + 589 + 599 平行模式）；**O3 整体 CLOSED 候选 per 588 PASS + 590 PASS + 597 三重声明 + 598 audit 落 四重声明**（§5.2.2 CLOSED per 583 + §5.2.3 CLOSED per 583 + §5.2.4 CLOSED per 597 + §5.2.5 CLOSED per 585 + §5.2.6 CLOSED per 587）；B 路（公开源自动获取 per docs/52）保持主路径；O1 整体仍 WAITING_FILE per docs/47 §3.1 + 用户 2026-08-26 披露 + 2026-08-29 治理铁律；584 重 ACK 触发条件保留 = 用户裁定 + Python 3.12 wheel 可用 + Docker daemon 就绪 + 项目主 deps manifest 决策已定 + Dockerfile（非 current critical path）；后续 599 tasking = docs/52 B 路 spec 落定刀 + O1 §5.2.x 真实 SHA-locked 江苏样本刀（待 docs/52 B 路落定后另刀下发）— 任一由架构师定夺]
| docs/10 §3.2-3.4 | Stage 2 收口 | ⚠️ xfail stub（Stage 3 收口）| S2.10 落地刀（tasking 251+）；Gate 2 评审**必带 OPEN 清单**|
| **mart-shape 真表** | S2.7-b-full | OPEN（演示级 dbt mart 骨架 WHERE FALSE）| S2.7-b-full 真数据迁移刀（tasking 26X+）|
| **person/tenure 真数据** | S2.1 | OPEN（person/tenure demo 已交 `303`；真数据待 S2.1-lite PASS OPEN per Cursor 174）| S2.1-lite 落地刀 + O1 真实 SHA 收口（per docs/45 §5.5 OPEN + docs/47 §6.3）|

---

## §4. 演示场景（5 省 + 10 地市 + EvidenceChain + 七维度）

### 4.1 5 省 + 10 地市演示页面（per docs/36-42 + S2.7-a + S2.7-a2）

#### 5 省 lite 页面（per `257`）
```
frontend/app/provinces/
├── jiangsu/page.tsx       # 江苏
├── zhejiang/page.tsx      # 浙江
├── guangdong/page.tsx     # 广东
├── shandong/page.tsx      # 山东
└── sichuan/page.tsx       # 四川
```

#### 10 地市 lite 页面（per `257` + `303`）
```
frontend/app/cities/
└── [slug]/page.tsx        # generateStaticParams 预生成 10 slug：
                          # nanjing / suzhou / wuxi / nantong
                          # hangzhou / ningbo / wenzhou
                          # guangzhou / shenzhen / dongguan
                          # dynamicParams = false → 404 兜底
```

#### CityPageMart 组件（per `266` + `294` + `297` + `303`）
- `frontend/app/components/CityPageMart.tsx`
- `<section data-testid="city-page-mart-evidence-chain">` — evidence_chain 6 段 + is_demo 标识
- `<section data-testid="city-page-mart-seven-dim">` — seven_dim_overview 7 维度 + is_demo 标识
- `<section data-testid="city-page-mart-related-persons">` — 10 城 × 2 demo 相关人物行（市委书记 + 市长 mock；演示标识）

### 4.2 EvidenceChain（六段）
```
frontend/app/components/EvidenceChain.tsx
  ├─ CONDITION      条件（per S2.6）
  ├─ COMMITMENT     承诺（per S2.6）
  ├─ PROCESS        过程（per S2.6）
  ├─ OUTPUT         输出（per S2.6）
  ├─ OUTCOME        结果（per S2.6）
  └─ FEEDBACK       反馈（per S2.6）
```
每段渲染：observation_id + evidence_refs[] + source_document + is_demo 标识。

### 4.3 七维度观察卡（per `270` + docs/42）
```
frontend/app/components/SevenDimGrid.tsx
  1. policy_direction       # 政策方向
  2. fiscal_input           # 财政投入
  3. institutional_capacity # 制度能力
  4. process_disclosure     # 过程披露
  5. outcome_observability  # 结果可观测
  6. feedback_loop          # 反馈回路
  7. cross_source_consistency # 跨源一致性
```
类型契约：`frontend/lib/types_seven_dim.ts`；mock：`frontend/lib/mock_seven_dim.ts`。

#### 4.4 公开提取演示里程碑（per 回执链 `344`→`413`）

> ⚠ **本节是公开提取演示里程碑的端到端交付清单**（回执链 `344` → `362` → `368` → `371` → `377` → `383` → `398` → `404` → `410` → `413` → `436` → `440` → `446` → `448` → `470` → `474` → `482` → `496` → `498` → `502` → `510` → `512` → `548` → `556` → `562` → `566` → `568` → `570` → `572` → `574` → `577` → `579` → `597`；16–19 公网互链弧收口里程碑行 per `474`（`472` 已在 docs/53/docs/45 登记）；O1 B 路 21–23 弧内里程碑行补登 per `482`/`496`/`498`、弧收口登记 per `500` 已在 docs/53 §5 第 24 项/docs/45 登记、21–23 弧收口里程碑行补登 per `502`；第 25 项行 live-candidate 下轴里程碑补登 per `508`、live-candidate 探测实跑证据登记 per `510`、第 26 项行 live-probe 探测证据里程碑补登 per `512`（O1 B 路 21–26 弧内里程碑 + live-probe），链尾以 `512` 收口；O1 B 路 21–30 扩展弧收口（十节点并列文档汇总；第 31 项 per `546` 落地 / docs/50 §4.4 里程碑行补登 per `548`）+ SHA drift (a) 执行登记（registry `file_hash_sha256` → `a7e4029d…` per `538`/`540`/`542`）；**O1 仍 OPEN——registry 更新 ≠ O1 收口（mart 真 SHA 未入仓）**，链尾以 `548` 收口；O1 B 路第 32 项下一探测轴 = post-(a) live refresh → mart 真 SHA 入仓（只登记未运行；第 32 项 per `554` 落地 / docs/50 §4.4 第 32 项行 per `556`）；第 33 项 post-(a) live refresh 实跑证据已落（exit 0 + hash 匹配实测 + lineage `O1_AUTO_INTAKED`/`is_demo=false`；per `560` 落地 / docs/50 §4.4 第 33 项行 per `562`；hash 匹配 ≠ O1 收口）；**O1 仍 OPEN——O1 收口须用户/Cursor 裁定**；第 34 项 26X 轴 kickoff 已落（用户分叉 = 先 26X·合刀·再 O1；S2.7-b-full 去 demo 预览路径 `NEXT_PUBLIC_USE_MART_FIXTURE=1` 看 mart-shape 管道 + D 实跑守门 pytest 30 passed exit 0 + smoke PASS exit 0；per `566` 落地 / docs/50 §4.4 第 34 项行 per `566`；真 mart 真 SHA / person 真数据仍 OPEN → O1 后另刀；MART_FIXTURE 预览 = demo mart-shape 管道、非 O1 收口）；第 35 项 26X mart-fixture build 路径实跑证据已落（build exit 0 + ✓ Generating static pages 22/22 + 10 城 SSG + related-persons pytest 15 passed exit 0；per `568` 落地 / docs/50 §4.4 第 35 项行 per `568`；真 mart 真 SHA / person 真数据仍 OPEN → O1 后另刀；MART_FIXTURE build = demo mart-shape 管道、非 O1 收口）；第 36 项 O1 轴 kickoff 已落（用户 2026-08-28 pivot：26X 告一段落 34–35 项已落 per `566`/`568` → O1 活跃轴；下一轴 = mart 真 SHA 入仓 per 第 32–33 项弧 + `560` 证据 hash 匹配 + `O1_AUTO_INTAKED`/`is_demo=false`；per `570` 落地 / docs/50 §4.4 第 36 项行 per `570`；mart 真 SHA 未入仓、≠ O1 收口）；第 37 项 mart 真 SHA 入仓下一刀已登记（**只登记不运行**——目标 = dbt mart `lineage.source_file_sha256` 从 `'0'*64` 占位替换为 registry `a7e4029d…`；依赖 `560` lineage `O1_AUTO_INTAKED`/`is_demo=false`；登记 ≠ 执行、≠ O1 收口；per `570` 落地 / docs/50 §4.4 第 37 项行 per `570`）；第 38 项 mart 真 SHA 入仓 pilot 已实装（nanjing + CONDITION 单行真 SHA `a7e4029d…` + `is_demo='false'`，其余 59 行保持 demo + `'0'*64`；pytest 扩 5 例 → 25 passed exit 0；pilot 1 行 ≠ O1 收口——全量 flip / person 真数据仍 OPEN；per `572` 落地 / docs/50 §4.4 第 38 项行 per `572`）；第 39 项 O1 收口条件登记已落（pilot 第 38 项经 `573` 架构师审计 PASS——**Cursor 退役、573 起架构师审计**；不做 60 行铺满 flip——单一真实源铺 59 行 = 伪造 lineage；59 行真实源缺口登记（逐城公报经 docs/52 pipeline 入仓后逐行 flip；tech-blocked 城市 hubei 等停报不绕）；O1 收口定义 = pilot 限定域完成 + 缺口清单登记 + 用户裁定；**O1 仍 OPEN**；per `574` 落地 / docs/50 §4.4 第 39 项行 per `574`）；第 40 项 O1 CLOSED (as-scoped) 裁定已登记（用户 2026-08-28 裁定——**O1 CLOSED (as-scoped)**：收口域 = NATIONAL_BULLETIN → nanjing CONDITION 真 SHA 入仓路径端到端打通（`538` 裁定值 → `560` live refresh hash 匹配 → `572` pilot 实装 → `573` 架构师审计 PASS）；59 行其余城市/段 = 已登记缺口（第 39 项），**逐城真实源入仓保持 OPEN**（号位 `576` 保留，链条缺口为有意登记）；裁定解锁 S2.1-full 实装（person/tenure demo seed 30/30/20/60/60/60 全 demo + 6 stg + `mart_person_tenure`，`is_demo` 末列显式暴露）；per `577` 落地 / docs/50 §4.4 第 40 项行 per `577`；第 41 项 O3 决策备忘 · OCR 引擎用户已裁定 **paddle-ocr**（2026-08-28 照录；裁定 ≠ O3 收口，实装链 5.2.2–5.2.6 OPEN）+ 第 42 项全量 4 failed 继承登记（存量既有非 577 引入；登记 ≠ 修复）（per `579` 落地 / docs/50 §4.4 第 41–42 项行 per `579`；链尾以 `579` 收口）；**全部为 demo/candidate 演示，非 O1/Gate 收口**；第 43 项继承 4 failed 修复合刀登记已落（per 回执 `581` 落地 / docs/50 §4.4 第 43 项行 per `581`；修法三则 = (A) fixture provenance 活锚定 sample 实字节 + (B) s52 回归双路径 stats pilot 预期 rc=8 SHA 闸零弱化 + (C) data/ 白名单房规化四目录；**修复走断言口径 ≠ 改 registry/脚本/seed/数据 字节**；O1 仍 OPEN；O3 仍 OPEN；不宣布 Gate PASS；不删 OPEN）；链尾以 `581` 收口；第 44 项 O3 实装首刀登记已落（per 回执 `583` 落地 / docs/50 §4.4 第 44 项行 per `583`；闭合 docs/49 §5.2.2 `validate_ocr_input()` API + §5.2.3 `source_document.doc_kind='OCR_SCAN'` migration 014；5.2.4–5.2.6 + 真实 PDF `--confirm-o3=PATH` 用户保留动作 仍 OPEN）；链尾以 `583` 收口；第 44 项 + docs/45 §7 链头 916 → 917 sync gap 由 `585` 闭合（§584 audit ⚠1 docs sync patch 五处 916 → 917 deferred from 584 → closure in 585；详单 docs/45 L93 demote 段 2 处 + docs/45 L487 pack invariant table + docs/53 L203 + docs/53 L207 + docs/50 L228；per `585-stage0-architect-s584-o3-impl-paddle-ocr-deps-audit-BLOCKED-20260829` 后续段）；584 BLOCKED-DEFERRED 修订（4 BLOCKER：Python 3.14 无 paddlepaddle wheel + 项目零 baseline Dockerfile + Docker daemon 不可用 + 主 deps manifest 缺失；架构师 Path C 采纳 = paddle-ocr deps 引入走后续刀 + 585 e2e pytest 刀 paddle-ocr MOCK only 与 deps 解耦）；第 45 项 O3 §5.2.5 e2e pytest 刀登记已落（per 回执 `585` 落地 / docs/50 §4.4 第 45 项行 per `585`；闭合 docs/49 §5.2.5 e2e pytest（syn-PDF 合成 fixture + paddle-ocr MOCK only + 9 例 PASS）；5.2.4 BLOCKED-DEFERRED per 584 + 5.2.6 仍 OPEN + 真实 PDF `--confirm-o3=PATH` 用户保留动作不变（O3 整体仍 OPEN））；链尾以 `585` 收口；**第 46 项 O3 §5.2.6 真实 PDF e2e 收口刀登记已落**（per 回执 `587` 落地 / docs/50 §4.4 第 46 项行 per `587`；闭合 docs/49 §5.2.6 真实 PDF e2e 收口 = 执行端自取 S0 源 `spikes/04-scanned-pdf/data/shaanxi_fiscal_regulation_flk.pdf`（SHA `f34b2e57…` = registry.csv 注册 SHA 验证一致）+ 复制到 ALLOWED_PREFIXES[0] `/tmp/cegr_uploads/` + sha256sum 验证零漂移 + `validate_ocr_input` ACCEPT + paddle-ocr MOCK only（4 页陕西财政预算管理条例 canned 文本；与 deps 引入解耦 per `584` BLOCKED-DEFERRED Path C）+ source_document mock writer 捕获 row dict + lineage JSONB 12 字段完整 + 执行端自验；**零用户动作 / 零用户裁定 / 零用户亲验 / 零 `--confirm-o3=PATH`**；supersede 旧版 `587-stage0-architect-s586-o3-impl-real-pdf-user-action-tasking-20260829.md`「用户提供真实 PDF」假设作废；per 2026-08-29 治理铁律数据源唯一=政府/统计局/研究机构自取；5.2.4 BLOCKED-DEFERRED per 584；O3 整体 CLOSED 候选 per 588 架构师审计 PASS 后宣布）；链尾以 `587` 收口；**第 47 项 O3 §5.2.4 paddle-ocr 引擎依赖实施刀登记已落**（per 回执 `597` 落地 / docs/50 §4.4 第 47 项行 per `597`；闭合 docs/49 §5.2.4 paddle-ocr 引擎依赖实施（per `584` BLOCKED-DEFERRED 4 BLOCKER 全闭环收口）= paddlepaddle 2.6.2 + paddleocr 3.7.0 deps 引入 + .venv-paddle 隔离 venv + 本地 paddleocr import 验证 + spike/ 隔离测试入口守门 paddle-ocr 真依赖路径 + 端到端 pytest paddle-ocr MOCK only 路径守门完整 + 真实 PDF e2e 守门完整（per `583` / `585` / `587` 三步累计）；supersede 旧版 `584` BLOCKED-DEFERRED；**5.2.4 = CLOSED per 597（2026-08-29）**；**5.2.5 = CLOSED per 585（2026-08-29）**；**5.2.6 = CLOSED per 587（2026-08-29）**；docs/45 五处（文首 +1 刷新行 / §1 +1 §5.2.4 paddle-ocr 引擎依赖实施刀登记段 / §3 零涉 / §5.5 尾 O3 bullet 行尾注 append 含 5.2.4 CLOSED per 597 + 5.2.5 CLOSED per 585 + 5.2.6 CLOSED per 587 + 584 BLOCKED-DEFERRED 解除 / §7 链头 `923 → 944` + knife 597 demote）+ docs/50 §4.4 +1 第 47 项行 + intro 链尾 `→ 587` 续接 `→ 597` + §5.1 O3 状态行 append 处置标注（5.2.4 CLOSED per 597；行内 append 不删行）；manifest 923 → 944（+3 per enumeration 收口：bump 脚本 `spike_helper` + 596 audit `documentation` + 597 receipt `documentation`）；红线 100% 兑现（paddlepaddle 装在 `.venv-paddle` 隔离 venv 不污染 system site-packages / `.venv-dbt` 与 `requirements-dbt.txt` 零触碰 / 不修改 001-014 任何文件 / 不修改 01-core.sql / 不修改 scripts/intake_real_sha_if_present.py 与 auto_ingest_public_source.py / 不修改 4 fixture 字节（`nbs=e30ee811` / `nbs_live=9232efdb` / `sz=937255a5` / `hb=9056001c`）/ 不修改 spikes/04-scanned-pdf/gate_thresholds.json / 不爬网 / 不写 dbt/mart/前端 / 不宣布 Gate PASS / O3 整体仍 OPEN（待 588 架构师审计 PASS 后宣布）/ 不删既有 OPEN 行）；per 2026-08-29 治理铁律数据源唯一=政府/统计局/研究机构自取 / 执行端不可提任何用户裁定事项）；链尾以 `597` 收口；链到 `docs/45` §6.2 + `docs/53` §5。

| 里程碑 | 交付 | 回执 | 守门 |
|---|---|---|---|
| **公开源自动获取 connector** | `scripts/auto_ingest_public_source.py`（single-file）+ `source_registry/registry.csv`（4 pilot 行）| `344` + `347` | 4 模式（dry-run / `--from-local-sample` / `--live --confirm-live` / `--refresh-live-candidate`）+ 10 出口码契约（per `docs/53` §3）|
| **NBS 双轨**（sample ↔ LIVE_CANDIDATE）| sample 轨 63 行 `dea13b8a…` + candidate 轨 60 行 `0b85212f…`；分轨互不覆盖；drift 不自动改写 registry | `350` + `353` + `356` + `359` + `362` | smoke §12c（fixture 在位 + 分轨交叉）+ 92 pytest cases |
| **深圳散文轨**（第三轨 REGISTRY_SAMPLE）| `data/public_extracts/sz.gov.cn/MUNICIPAL_BULLETIN.json`（71 行 `{section, paragraph}` / `d5e2c731…` registry 锚）+ `frontend/lib/public_extract_sz.json`（byte-verbatim 快照）+ `/public-extracts` 第三分节 | `368` + `371` | smoke §12d（深圳 fixture 锚 + 页面针 + NBS 双轨交叉）+ 100 pytest cases |
| **湖北 xlsx 轨**（第四轨 REGISTRY_SAMPLE）| `data/public_extracts/tjj.hubei.gov.cn/PROVINCIAL_BULLETIN.json`（21 行 xlsx 月报统计 / `c5cf5abeb4fdf97a…` registry 锚）+ `frontend/lib/public_extract_hubei.json`（byte-verbatim 快照）+ `/public-extracts` 第四分节；live `enabled=FALSE` 暂缓 | `377` | smoke §12e（HB fixture 锚 + 页面针 + NBS+SZ+HB 四轨交叉）+ 103 pytest cases |
| **四轨一览条 overview strip**（页内摘要）| `<section className="public-extracts-page__overview-strip" id="overview">`：7 列 × 4 行（NBS sample / NBS live 候选 / 深圳 / 湖北）；数据只读自既有 4 fixture，不重算 | `383` | smoke §12f（CSS class + 4 锚点 id + 4 锚链 href + `REGISTRY_SAMPLE_INTAKED` / `LIVE_CANDIDATE, drift` 标注 + 守门 13 针）+ 2 pytest |
| **四轨客户端行筛选**（视图过滤）| 4 数据表各一独立受控 input `TrackFilterInput`（`testId="track-filter-{nbs-sample,nbs-live,sz,hb}"`）+ `filterRows` 包含匹配 + 每轨独立 `useState`；`"use client"` 纯客户端（build 仍 ○ Static）；tbody 消费 `filtered*Rows` 视图数组 + 空匹配占位行 | `398` | smoke §12h（use client + useState + 4 testId + 包含匹配 + 匹配计数 + 非权威库检索 + 无匹配行，11 针）+ 3 pytest |
| **四轨 CSV 静态下载**（fixture 快照导出）| 列头「下载 JSON / CSV」+ 4 同格 CSV 第二链；产物 `frontend/public/public-extracts/{nbs,nbs-live-candidate,sz,hubei}.csv`（63 / 60 / 71 / 21 数据行；列序=fixture 首行键序；UTF-8 无 BOM / `\n` / QUOTE_MINIMAL）；生成器 `scripts/gen_public_extracts_csv.py` `render_csv_bytes` 纯函数可字节重渲 | `404` | smoke §12i（4 CSV 在位非空 + 4 href + 4 download attr + 列头含 `下载 JSON / CSV` + JSON 链不回归 + 非权威库守门 + 无 `text/csv` 服务端动态导出，15 针）+ 13 pytest（表头一致×4 + 行数字段数×4 + 字节重渲×4 + 页面守门）|
| **全站顶栏 `site-nav` → `/public-extracts` 常驻链**（顶栏入口演示）| `frontend/app/layout.tsx` 在 `<header data-testid="mode-banner">` 后插入 `<nav data-testid="site-nav">`：首页 + `<a href="/public-extracts" data-testid="site-nav-public-extracts">公开提取样本（四轨 demo）</a>`；旁注「全站顶栏常驻链；四轨 demo / 非 O1 / 不宣布 Gate PASS（per tasking 409）」；纯 `<a href>` 锚链未引入 `next/link`（保留 build ○ Static 22/22）；不分支 `params.*` | `410` | smoke §13c（site-nav 容器 + /public-extracts 链 + 链 testId + 四轨 demo + 非 O1 + 不宣布 Gate PASS + 不分支 `params.*`，6 针）+ 5 pytest `test_layout_site_nav_public_extracts.py`（container / link / disclaimer / no-params-branch / anchor-not-Link）|
| **docs/45 + docs/53 同步登记**（评审索引 + ops 手册）| docs/45 §1/§6.2/§7 多处刷新 + docs/53 §5/冒烟；指向本表全部里程碑；显式 demo/candidate 演示、非 O1/Gate PASS | `407` + `413` | 链对账 + 红线守门 grep |
| **首页 NBS sample 轨显式 deeplink**（首页表内显式锚链演示）| `frontend/app/page.tsx` 公开提取表内「公开提取样本（四轨 demo）」行 → 「公开提取 NBS sample 轨（demo）」行；href `/public-extracts` → `/public-extracts#track-nbs-sample` + `data-testid="home-public-extracts-nbs-sample"` + 数据模式 `REGISTRY_SAMPLE · demo · 非 live O1`；结构镜像湖北「公开提取湖北轨（xlsx demo）」`#track-hb` 行（per knife 67 tasking 394）；纯 `<a href>` 锚链未引入 `next/link`（保留 build ○ Static 22/22）；不分支 `params.*`（AGENTS.md 静态路由红线）；链 docs/45 §1 + §6.2 + §7 + docs/53 §5 | `420` + `bee7950` | smoke §12b' 4 针（href + testId + REGISTRY_SAMPLE / demo / 非 live O1）+ pytest 3 cases `tests/test_nbs_home_deeplink_public_extract.py`（de 行内容 / 5 省 + 10 城 CityPage/CityPageMart 无 `#track-nbs-sample` 污染 / 4 fixture byte SHA 前 8 锁不漂：`nbs=e30ee811` / `nbs_live=9232efdb` / `sz=937255a5` / `hb=9056001c`）|
| **首页 NBS live 候选轨显式 deeplink**（首页表内显式锚链演示，drift 候选非 O1 收口）| `frontend/app/page.tsx` NBS sample 行后新增「公开提取 NBS live 候选轨（candidate demo）」行；href `/public-extracts#track-nbs-live` + `data-testid="home-public-extracts-nbs-live"`；描述列「stats.gov.cn / NATIONAL_BULLETIN 60 行（WORM `zxfb` LIVE_CANDIDATE 提取；drift 候选；per 回执 `359` / `362`）」；数据模式标 `LIVE_CANDIDATE · drift 候选 · 非 O1 收口`；与 NBS sample 行同表内并列（镜像 knife 76 tasking 420 NBS sample 行结构 + knife 67 tasking 394 湖北 `#track-hb` 行模板）；纯 `<a href>` 锚链未引入 `next/link`（保留 build ○ Static）；不分支 `params.*`；链 docs/45 §1 + §6.2 + §7 + docs/53 §5 | `424` + `29467c4` | smoke §12b'' 4 针（href + testId + LIVE_CANDIDATE / drift 候选 / 非 O1 收口 + 综合 PASS）+ pytest 3 cases `tests/test_nbs_live_home_deeplink_public_extract.py`（de 行内容 / 5 省 + 10 城 CityPage/CityPageMart 无 `#track-nbs-live` 污染 / 4 fixture byte SHA 前 8 锁不漂，与 knife 76 锁值完全一致：`nbs=e30ee811` / `nbs_live=9232efdb` / `sz=937255a5` / `hb=9056001c`）|
| **首页四轨一览 overview 显式 deeplink**（首页表内显式锚链演示）| `frontend/app/page.tsx` 公开提取表内湖北行后新增「公开提取四轨一览（overview strip）」行；href `/public-extracts#overview` + `data-testid="home-public-extracts-overview"`；描述列「stats.gov.cn / sz.gov.cn / tjj.hubei.gov.cn 7 列 × 4 行 overview（轨 / domain / category / 行数 / SHA 前 8 / demo\|candidate 标注 / 分节锚点；数据只读自既有 4 fixture，不重算；per 回执 `383`；smoke §12f 门）」；数据模式标 `OVERVIEW · 四轨 demo · 非 O1`；结构镜像 knife 76 tasking 420 NBS sample 行 + knife 78 tasking 424 NBS live 行 + knife 67 tasking 394 湖北 `#track-hb` 行；纯 `<a href>` 锚链未引入 `next/link`（保留 build ○ Static 22/22）；不分支 `params.*`（AGENTS.md 静态路由红线）；链 docs/45 §1 + §6.2 + §7 + docs/53 §5 | `432` + `a23e5c8` | smoke §12b''' 4 针（href + testId + OVERVIEW / 四轨 demo / 非 O1 + 综合 PASS）+ pytest 3 cases `tests/test_overview_home_deeplink_public_extract.py`（de 行内容 / 5 省 + 10 城 CityPage/CityPageMart 无 `#overview` 污染 / 4 fixture byte SHA 前 8 锁不漂，与 knife 76/78 锁值完全一致：`nbs=e30ee811` / `nbs_live=9232efdb` / `sz=937255a5` / `hb=9056001c`）|
| **首页公开提取入口一览**（顶栏 site-nav + 首页表内 4 deeplink 端到端入口演示汇总）| `docs/53-stage2-public-ingest-ops-handbook-20260826.md` §5 新增 5 行 markdown 表「首页公开提取入口一览」，覆盖：(a) 全站顶栏 site-nav → `/public-extracts`（`<nav data-testid="site-nav">`）；(b) 首页表内 NBS sample 轨 → `/public-extracts#track-nbs-sample`；(c) 首页表内 NBS live 候选轨 → `/public-extracts#track-nbs-live`；(d) 首页表内四轨一览 overview strip → `/public-extracts#overview`；(e) 首页表内湖北轨 → `/public-extracts#track-hb`；5 行均显式 demo/candidate 演示、非 O1/Gate PASS；4 fixture byte SHA 前 8 锁不漂：`nbs=e30ee811` / `nbs_live=9232efdb` / `sz=937255a5` / `hb=9056001c` 与 knife 76/78/81/82/84/85 完全一致；链 docs/45 §6.2 + §7 + docs/53 §5（双向，docs/45 §7 pack invariant 链亦指向本行）；不引入 `next/link` 保留 build ○ Static 22/22；不分支 `params.*`（AGENTS.md 静态路由红线） | `440` + `6d54d63` | smoke §13c + §12b' + §12b'' + §12b'''（4 入口合计 18 针）+ pytest 3+5+3+3 = 14 cases（`test_layout_site_nav_public_extracts.py` + `test_nbs_home_deeplink_public_extract.py` + `test_nbs_live_home_deeplink_public_extract.py` + `test_overview_home_deeplink_public_extract.py`）+ 4 fixture byte SHA 前 8 锁不漂 |
| **公网预览 redeploy 运维**（`https://china.3strategy.cc` 公网预览部署上线 + 运维登记）| 源站 SSH **`newvps`**（`207.57.133.177:52134`）路径 `/opt/china-platform/frontend`，**宿主机 systemd** `china-platform-frontend` → `127.0.0.1:3000`（非容器）+ nginx `/etc/nginx/sites-enabled/china.3strategy.cc.conf` + CF 橙云 A → `207.57.133.177`（**勿用 `hk` / `103.59.103.85`**，其上无本站路径）；redeploy 命令链（rsync 或 git pull + `npm ci` + `NEXT_PUBLIC_USE_MOCK=true npm run build` + `systemctl restart china-platform-frontend`；SSH 易超时用 `nohup`）登记于 `docs/53` §5 第 16 项；公网 HTTP 验收基线：首页 4/4 deeplink（`#track-nbs-sample` / `#track-nbs-live` / `#overview` / `#track-hb`，含 3 个 `home-public-extracts-*` testId）+ `/public-extracts` HTTP 200（105,893 bytes；5 锚点 id + `site-nav` testId + 4 `track-filter-*` testId）；redeploy 由 ops 侧执行、CC 公网验收（per 回执 `446` §分工）；preview 容器化择机另刀（本里程碑非 Docker）；链 `docs/45` §6.2 + `docs/53` §5 第 16 项 | `446` + `448` + `69090e7` | curl 公网验收（2026-08-27 实测：4/4 deeplink + `/public-extracts` 200 + 5 锚点 + site-nav + 4 筛选 testId 全在位）+ **非 O1/Gate PASS：预览部署是运维里程碑，不构成 O1 / Gate 2 收口** + 不换服务器 + 不改代码 + 不动 4 fixture 字节（`nbs=e30ee811` / `nbs_live=9232efdb` / `sz=937255a5` / `hb=9056001c`，与 knife 76/78/81/82/84/85/86/87 锁值完全一致）|
| **docs/53 §5 第 17 项公网预览 redeploy 运维行互链**（互链登记里程碑；per 回执 `450` 落地上下文 + `462` 标签补登；行 200 ↔ `docs/53` §5 ↔ `docs/45` 三向对账）| `docs/53-stage2-public-ingest-ops-handbook-20260826.md` §5 第 17 项 blockquote（per 回执 `452` 互链落地；**docs/53 §5 第 17 项（此条）** 标签补登 per 回执 `462`）：本表行 200「公网预览 redeploy 运维」里程碑与 `docs/45` 的运维行互链登记——交付列登记源 = `docs/53` §5 第 16 项（📍 运维登记 + 🔧 redeploy 命令链，per 回执 `448`）；公网验收基线 per 回执 `446`（curl 实测 2026-08-27：首页 4/4 deeplink + `/public-extracts` HTTP 200）；redeploy 由 ops 侧执行、CC 公网验收；docs/45 文首刷新行 + §1 + §6.2 + §7 三向对账（回执 `452` 落 knife 92，链头已随各刀推进至 780）；行 200 正文原样未动；不改代码；不换服务器（非 Docker）| `450` + `452` + `462` | 链对账 grep（行 200 ↔ docs/53 §5 第 17 项 ↔ docs/45 §1/§6.2/§7）+ 标签对账（第 16 项=📍+🔧、第 17 项=本互链、第 18 项=URL 块互链、第 19 项=🌐 首行互链，四段各自明确 per `462`/`464`）+ **非 O1/Gate PASS：互链登记是文档节点，不构成 O1 / Gate 2 收口** + 不改代码 + 不动行 200 正文 + 不动 4 fixture 字节（`nbs=e30ee811` / `nbs_live=9232efdb` / `sz=937255a5` / `hb=9056001c`，与前序各刀锁值完全一致）|
| **docs/53 §5 第 18 项公网预览 URL 块互链**（互链登记里程碑；docs/50 §4.4 预览 URL 块 ↔ `docs/53` §5 双向对账）| `docs/53-stage2-public-ingest-ops-handbook-20260826.md` §5 第 18 项 blockquote（per 回执 `456`）：本节「**公网预览**」URL 段与「本地预览」localhost 段的互链登记——公网段 open 2 条（`https://china.3strategy.cc/public-extracts` HTTP 200 per 回执 `446` + 首页 4 deeplink）由回执 `454` 落地、localhost 段逐字保留、⚠ 守门清单 +1 条（公网与本地同构 demo/candidate build）；URL 块 bash 正文原样未动；链 行 200 公网预览 redeploy 运维里程碑 + `docs/53` §5 第 16 项（📍 🔧 登记，命令链所在）+ 回执 `446`（公网验收基线）+ `454`（URL 段落地）；docs/45 文首刷新行 + §1 + §6.2 + §7 三向对账（per 回执 `456` 三向互链）；不引入 next/link；不分支 params.* | `454` + `456` | 链对账 grep（docs/50 行 204 段头 ↔ docs/53 §5 第 18 项 ↔ docs/45 §1/§6.2/§7）+ ⚠ 守门清单在位（公网非 O1/Gate PASS 条）+ **非 O1/Gate PASS：互链登记是文档节点，不构成 O1 / Gate 2 收口** + 不改代码 + 不动 URL 块 bash 正文 + 不动 4 fixture 字节（`nbs=e30ee811` / `nbs_live=9232efdb` / `sz=937255a5` / `hb=9056001c`，与前序各刀锁值完全一致）|
| **docs/53 §5 第 19 项 🌐 公网预览首行互链**（互链登记里程碑；docs/50 §4.4 公网预览段头 ↔ `docs/53` §5 🌐 首 行 ↔ `docs/45` 三向对账）| `docs/53-stage2-public-ingest-ops-handbook-20260826.md` §5 第 19 项 blockquote（per 回执 `464` 落地；其登记对象 = 回执 `460` 的 docs/45 ↔ docs/53 三向互链）：`docs/53` §5 🌐 公网预览首行与 `docs/45` 文首 queue_rev 刷新行 + §1 + §6.2 + §7 的双向对账登记——🌐 正文仅含互链指向句「`docs/45` 侧互链登记见第 19 项（per 回执 `464`）+ `docs/45` §1」，URL/deeplink 正文逐字未动（红线）；本节 §4.4「公网预览」段头亦已补第 19 项语义说明（per 回执 `464` 可选句）；链第 16 项（📍+🔧）/ 第 17 项（redeploy 运维行互链）/ 第 18 项（URL 块互链）+ 回执 `446`（公网验收基线）/ `454`（公网段落地）；docs/45 文首刷新行 + §1 + §6.2 + §7 三向对账 | `460` + `464` | 链对账 grep（docs/50 §4.4 段头 ↔ docs/53 §5 第 19 项 + 🌐 首行 ↔ docs/45 §1/§6.2/§7）+ 🌐 正文未动核验（URL 与 4 deeplink 逐字保留）+ 标签对账（第 16/17/18/19 项四段各自明确 per `462`/`464`）+ **非 O1/Gate PASS：互链登记是文档节点，不构成 O1 / Gate 2 收口** + 不改代码 + 不动 🌐 URL/deeplink 正文 + 不动 4 fixture 字节（`nbs=e30ee811` / `nbs_live=9232efdb` / `sz=937255a5` / `hb=9056001c`，与前序各刀锁值完全一致）|
| **docs/53 §5 第 20 项 16–19 公网预览互链弧收口**（弧收口里程碑；per 回执 `472` 落地：四节点 = 第 16 项 📍 运维登记 + 🔧 redeploy 命令链 / 第 17 项 redeploy 运维行互链 / 第 18 项 URL 块互链 / 第 19 项 🌐 首行互链；链行 200 + 回执 `446`/`454`）| `docs/53-stage2-public-ingest-ops-handbook-20260826.md` §5 第 20 项 blockquote（per 回执 `472`）：并列登记本表公网预览互链里程碑四节点弧——第 16 项 = 行 200 交付列登记源（📍+🔧，per `448` + `69090e7`）；第 17 项 = 本表「docs/53 §5 第 17 项公网预览 redeploy 运维行互链」行（per `450`/`452` + 标签补登 `462` + 里程碑行补登 `468`）；第 18 项 = 本表「docs/53 §5 第 18 项公网预览 URL 块互链」行（per `454` 落地 / `456` 三向互链 + 里程碑行补登 `466`）；第 19 项 = 本表「docs/53 §5 第 19 项 🌐 公网预览首行互链」行（per `458` 首行 / `460`+`464` 互链 + 里程碑行补登 `470`）；本节 §4.4 intro ⚠ 收据链尾已续接至 `→ 470`（per `472` 可选句）；第 16–19 项四段既有 blockquote 正文原样未动；链 docs/45 §1 + §6.2 + §7 | `472` | 弧对账 grep（docs/53 §5 第 20 项 ↔ 第 16–19 项四段原样在位 ↔ docs/50 §4.4 intro 链尾 `470`）+ 🌐 正文未动核验（URL 与 4 deeplink 逐字保留）+ **非 O1/Gate PASS：弧收口是文档节点，不构成 O1 / Gate 2 收口** + 不改代码 + 不动 16–19 既有正文 + 不动 4 fixture 字节（`nbs=e30ee811` / `nbs_live=9232efdb` / `sz=937255a5` / `hb=9056001c`，与前序各刀锁值完全一致）|
| **docs/53 §5 第 21 项 O1 B 路试点轴登记**（O1 公开源 B 路下一试点轴里程碑；per 回执 `480` 落地；链 docs/52 §3 #1 + `478` docs/45 主路径指针）| `docs/53-stage2-public-ingest-ops-handbook-20260826.md` §5 第 21 项 blockquote（per 回执 `480` 落地）：登记 O1 自动获取 B 路下一试点轴 = **`stats.gov.cn` / `NATIONAL_BULLETIN` HTML 月度发布**（per docs/52 §3 #1：URL 格式稳定、HTML 可直接 curl、无需 OCR；per docs/52 §5 A/B 双路并存、用户投递仍可用但非唯一）；B 路六步流水线 discover→download→sha256→archive→extract→observation 守门 per docs/52 §4 + AUTH 升级协议遇阻停止报告不绕过 per docs/52 §6；工具入口 docs/53 §1（single-file connector）+ connector 四种运行模式 docs/53 §2（dry-run / local-sample 入库 / live 探测 / 一键刷新 LIVE_CANDIDATE）；live drift 不自动改 registry、候选轨等用户裁定；链回执 `446`（公网验收基线）/ `454`（公网段）；docs/45 文首刷新行 + §1 + §6.2 + §7 三向对账 | `480` | 链对账 grep（docs/50 §4.4 本行 ↔ docs/53 §5 第 21 项 ↔ docs/45 §1/§6.2/§7）+ OPEN 保持核验（「O1 仍 OPEN」——试点轴登记只登记路径选择，不构成任何收口）+ 第 16–20 项既有正文未动核验 + **非 O1/Gate PASS：试点轴登记是文档节点，不构成 O1 / Gate 2 收口** + 不改代码 + 不实装新爬取代码 + 不启用 Hubei live + 不等用户投喂文件 + 不动 4 fixture 字节（`nbs=e30ee811` / `nbs_live=9232efdb` / `sz=937255a5` / `hb=9056001c`，与前序各刀锁值完全一致）|
| **docs/53 §5 第 22 项 O1 B 路 dry-run 证据登记**（O1 B 路 connector 入口可执行性证据里程碑；per 回执 `492` 落地；链 docs/53 §5 第 21 项试点轴 + docs/52 §3 #1）| `scripts/auto_ingest_public_source.py --dry-run --pilot-domain=stats.gov.cn --pilot-category=NATIONAL_BULLETIN` 实跑 exit code **0**——「OK pilot matched: stats.gov.cn / NATIONAL_BULLETIN · primary_url: https://www.stats.gov.cn/sj/zxfb/ · auth_note: 公开；无需授权 · expected SHA: dea13b8a4ff116ca…」+「OK dry-run; no network, no archive, no lineage writes.」；dry-run 默认模式无网络、无 DB 写、不 `--live`、不改 registry、不动 fixture 字节；证据登记源 = `docs/53-stage2-public-ingest-ops-handbook-20260826.md` §5 第 22 项 blockquote（per 回执 `492`）；docs/45 文首刷新行 queue_rev 239 + §1 一句 + §6.2 行尾注 + §7 链头三向对账；第 21 项既有正文原样未动 | `492` | 链对账 grep（docs/50 §4.4 本行 ↔ docs/53 §5 第 22 项 ↔ docs/45 四处）+ **O1 仍 OPEN：dry-run 只验证 connector 入口与 registry 过滤可执行，非 O1 收口，非 O1/Gate PASS** + 不改代码 + 不实装新爬取代码 + 不启用 Hubei live + 不等用户投喂文件 + 不动 4 fixture 字节（`nbs=e30ee811` / `nbs_live=9232efdb` / `sz=937255a5` / `hb=9056001c`，与前序各刀锁值完全一致）|
| **docs/53 §5 第 23 项 O1 B 路 local-sample 证据登记**（O1 B 路 registry 样本摄取链路可执行性证据里程碑；per 回执 `494` 落地；链 docs/53 §5 第 21 项试点轴 + 第 22 项 dry-run + docs/52 §2 运行模式）| `scripts/auto_ingest_public_source.py --from-local-sample --pilot-domain=stats.gov.cn --pilot-category=NATIONAL_BULLETIN --confirm-live=<lineage 路径>` 实跑 exit code **0**——**无网络**（读 registry `local_sample_path` 本地样本，SHA 与 registry 记录一致 dea13b8a…）+「OK archived / OK extract JSON / OK lineage」+「OK REGISTRY_SAMPLE_INTAKED (is_demo=true; sample ≠ live closure)」；`intake_status=REGISTRY_SAMPLE_INTAKED`、**`is_demo=true`、sample ≠ live closure，非真 SHA 收口**；证据登记源 = `docs/53-stage2-public-ingest-ops-handbook-20260826.md` §5 第 23 项 blockquote（per 回执 `494`；运行副作用 extracted_at 时间戳重写已披露并恢复 HEAD 字节）；docs/45 文首刷新行 queue_rev 241 + §1 一句 + §6.2 行尾注 + §7 链头三向对账；第 22 项既有正文原样未动 | `494` | 链对账 grep（docs/50 §4.4 本行 ↔ docs/53 §5 第 23 项 ↔ docs/45 四处）+ **O1 仍 OPEN：local-sample 显式 demo 运行不构成任何 O1/Gate 收口，非 O1/Gate PASS** + 不改代码 + 不实装新爬取代码 + 不启用 Hubei live + 不等用户投喂文件 + `is_demo=true` 不得谎称真 SHA 收口 + 不动 4 fixture 字节（`nbs=e30ee811` / `nbs_live=9232efdb` / `sz=937255a5` / `hb=9056001c`，与前序各刀锁值完全一致）|
| **docs/53 §5 第 24 项 O1 B 路 21–23 弧收口**（O1 公开源 B 路证据弧收口里程碑；per 回执 `500` 落地：三节点 = 第 21 项 🧭 试点轴登记 / 第 22 项 dry-run 证据登记 / 第 23 项 local-sample 证据登记；链 docs/52 §3 #1 + 回执 `478` docs/45 主路径指针）| `docs/53-stage2-public-ingest-ops-handbook-20260826.md` §5 第 24 项 blockquote（per 回执 `500`）：并列登记本表第 21/22/23 项 O1 B 路 NATIONAL_BULLETIN 三节点证据弧——第 21 项 = 试点轴登记（`stats.gov.cn` / `NATIONAL_BULLETIN` HTML 月度发布，per `480` 落地 / 行补登 per `482`）；第 22 项 = dry-run 证据登记（exit code **0** + 无网络 + 无 DB 写，per `492` / 行补登 per `496`）；第 23 项 = local-sample 证据登记（exit code **0** + 无网络 + `intake_status=REGISTRY_SAMPLE_INTAKED`、**`is_demo=true`、sample ≠ live closure 非真 SHA 收口**，per `494` / 行补登 per `498`）；本节 §4.4 intro ⚠ 收据链尾已续接至 `→ 498`（per `500` 可选句）；第 21–23 项三段既有 blockquote 正文原样未动；链 docs/45 §1 + §6.2 + §7 | `500` | 弧对账 grep（docs/53 §5 第 24 项 ↔ 第 21–23 项三段原样在位 ↔ docs/50 §4.4 intro 链尾 `498`）+ **O1 仍 OPEN：弧收口是文档节点，不构成任何 O1/Gate 收口，非 O1/Gate PASS** + 不改代码 + 不动 21–23 既有正文 + 不等用户投喂文件 + `is_demo=true` 不得谎称真 SHA 收口 + 不动 4 fixture 字节（`nbs=e30ee811` / `nbs_live=9232efdb` / `sz=937255a5` / `hb=9056001c`，与前序各刀锁值完全一致）|
| **docs/53 §5 第 25 项 O1 B 路 live-candidate 下一探测轴登记**（O1 B 路下一轴文档登记里程碑；per 回执 `506` 落地；链 docs/52 §3 #1 + `478` docs/45 主路径指针 + 21–24 弧 per `500`/`502`/`504`）| connector 模式 **`--live --confirm-live`** live-candidate 探测**只登记、未运行**——按 docs/52 §4 六步流水线 + docs/52 §6 AUTH 升级协议（遇 AUTH 阻停报告不绕过，不静默失败）；产物若产生走 LIVE_CANDIDATE 候选轨等用户裁定（live drift 不自动改 registry `enabled`）；无网络副作用；证据登记源 = `docs/53-stage2-public-ingest-ops-handbook-20260826.md` §5 第 25 项 blockquote（per 回执 `506`）；docs/45 文首刷新行 queue_rev 253 + §1 一句 + §6.2 行尾注 + §7 链头三向对账；第 21–24 项既有正文原样未动 | `506` | 链对账 grep（docs/50 §4.4 本行 ↔ docs/53 §5 第 25 项 ↔ docs/45 四处）+ **O1 仍 OPEN：下一轴登记是纯文档节点，不构成任何 O1/Gate 收口，非 O1/Gate PASS** + 不改代码 + 不实跑 `--live` + 未改 registry `enabled` + 不启用 Hubei live + 不等用户投喂文件 + 不动 4 fixture 字节（`nbs=e30ee811` / `nbs_live=9232efdb` / `sz=937255a5` / `hb=9056001c`，与前序各刀锁值完全一致）|
| **docs/53 §5 第 26 项 O1 B 路 NATIONAL_BULLETIN live-candidate 探测证据登记**（O1 B 路探测实跑证据里程碑；per 回执 `510` 落地；链 docs/52 §3 #1 + `478` 主路径指针 + 第 25 项下一轴登记 + tasking 333 SHA-drift 语义）| 任务书显式授权 connector 实跑 **exit code 0**——「OK deeplink discovered `t20260827_1965129.html`」+「OK downloaded 180165 bytes; sha256=a7e4029d…」≠ registry expected `dea13b8a…` → SHA drift 非静默处理：drift 报告 + CANDIDATE_AUTO lineage 双落盘 reviews/（**`is_demo=true`、drift ≠ 收口**）；⚠ 如实披露 WORM 幂等未覆盖（本刀实测字节未持久化至既有归档路径）+ 自动报告「已写入」模板句与磁盘实测不符（以磁盘为准）；registry `enabled` 与哈希均未改、无 headless、未绕任何 AUTH；候选处置等用户裁定（更新哈希 or 改稳定 URL 二选一）；证据登记源 = `docs/53-stage2-public-ingest-ops-handbook-20260826.md` §5 第 26 项 blockquote（per 回执 `510`）；docs/45 文首刷新行 queue_rev 257 + §1 一句 + §6.2 行尾注 + §7 链头三向对账；两件运行产物按房规未跟踪不入 manifest；第 21–25 项既有正文原样未动 | `510` | 链对账 grep（docs/50 §4.4 本行 ↔ docs/53 §5 第 26 项 ↔ docs/45 四处）+ **O1 仍 OPEN：CANDIDATE_AUTO 是 drift 候选非真数据，探测证据登记不构成任何 O1/Gate 收口，非 O1/Gate PASS** + 不改代码 + 不改 registry + 不启用 Hubei live + 不等用户投喂文件 + `is_demo=true` 不得谎称真 SHA 收口 + 不动 4 fixture 字节（`nbs=e30ee811` / `nbs_live=9232efdb` / `sz=937255a5` / `hb=9056001c`，与前序各刀锁值完全一致）|
| **docs/53 §5 第 27 项 O1 B 路 NATIONAL_BULLETIN 扩展证据弧收口（第 21–26 项）**（O1 B 路扩展弧收口里程碑；per 回执 `516` 落地；链 docs/52 §3 #1 + `478` 主路径指针 + intro ⚠ 收据链尾 `→ 512` per `514`）| 并列登记六节点扩展证据弧——第 21 项 🧭 试点轴登记（per `480`/`482`）；第 22 项 dry-run 证据（exit code **0** 无网络无 DB 写；per `492`/`496`）；第 23 项 local-sample 证据（exit code **0** 无网络、`intake_status=REGISTRY_SAMPLE_INTAKED`、`is_demo=true` sample ≠ live closure；per `494`/`498`）；第 24 项 21–23 弧收口（三节点并列文档汇总；per `500`/`502`/`504`）；第 25 项 live-candidate 下轴**只登记不运行**（per `506`/`508`）；第 26 项 live-probe 实跑证据（任务书显式授权 `--live --confirm-live`、有网络、exit code **0**、download 180165 B sha256 `a7e4029d…` ≠ expected `dea13b8a…` → SHA drift 非静默处理 → **CANDIDATE_AUTO 候选轨（`is_demo=true` 绝不伪装真数据）+ WORM 幂等未覆盖如实披露**；候选轨处置等用户裁定二选一；per `510`/`512`）；证据登记源 = `docs/53-stage2-public-ingest-ops-handbook-20260826.md` §5 第 27 项 blockquote（per 回执 `516`）；docs/45 文首刷新行 queue_rev 263 + §1 一句 + §6.2 行尾注 + §7 链头三向对账；本刀纯文档零运行零网络；intro ⚠ 收据链尾 `→ 512` 原样未动（本刀任务书不含链尾续接）；第 21–26 项既有正文原样未动 | `516` | 弧对账 grep（docs/50 §4.4 本行 ↔ docs/53 §5 第 27 项 ↔ 六节点既有 blockquote 原样在位 ↔ docs/45 四处）+ **O1 仍 OPEN：扩展弧收口是文档节点汇总，不构成任何 O1/Gate 收口，非 O1/Gate PASS** + SHA drift 候选轨等用户裁定 + 不改代码 + 不改 registry + 不实跑 `--live` + 不启用 Hubei live + 不等用户投喂文件 + `is_demo=true` 不得谎称真 SHA 收口 + 不动 4 fixture 字节（`nbs=e30ee811` / `nbs_live=9232efdb` / `sz=937255a5` / `hb=9056001c`，与前序各刀锁值完全一致）|
| **docs/53 §5 第 28 项 SHA drift 候选轨处置分叉登记**（O1 B 路 SHA drift 分叉登记里程碑；per 回执 `520` 落地；链 docs/53 §5 第 26 项 live-probe + 第 27 项扩展弧收口 + intro ⚠ 收据链尾 `→ 512`）| 登记 `510` live-probe 实测 SHA drift 候选轨处置分叉——download 180165 B sha256 `a7e4029d…` ≠ registry expected `dea13b8a…`（stats.gov.cn / NATIONAL_BULLETIN）；分叉二选一：**(a) 更新 registry.csv `file_hash_sha256` 为实测值**（认定源站换版）或 **(b) 改用稳定归档 URL**——两选项均须**用户裁定后另起独立刀任务执行**，connector 不自动改 registry，本行只登记不替用户选；registry `enabled` 与 `file_hash_sha256` 本刀均未改（expected 哈希磁盘 grep 在位）；本刀纯文档零运行零网络零代码；intro ⚠ 收据链尾 `→ 512` 原样未动（本刀任务书不含链尾续接）；第 21–27 项行既有正文原样未动；可选补登同步句 per 回执 `522` | `520` | 弧对账 grep（docs/50 §4.4 本行 ↔ docs/53 §5 第 28 项 ↔ docs/45 四处）+ **O1 仍 OPEN：drift ≠ 收口、分叉登记是文档节点不构成任何 O1/Gate 收口，非 O1/Gate PASS** + SHA drift 处置权完整保留用户 + 不删 OPEN + 不改代码 + 不改 registry + 不实跑 `--live` + 不启用 Hubei live + 不等用户投喂文件 + `is_demo=true` 不得谎称真 SHA 收口 + 不动 4 fixture 字节（`nbs=e30ee811` / `nbs_live=9232efdb` / `sz=937255a5` / `hb=9056001c`，与前序各刀锁值完全一致）；docs/52 文首互链 per `524`；本行互链尾注句补登 per `528`
| **docs/53 §5 第 29 项 O1 B 路 NATIONAL_BULLETIN 扩展证据弧收口（第 21–28 项）**（O1 B 路扩展弧收口里程碑（八节点）；per 回执 `530` 落地；链 docs/52 §3 #1 + `478` 主路径指针 + intro ⚠ 收据链尾 `→ 512` per `514`）| 并列登记八节点扩展证据弧——第 21 项 🧭 试点轴登记（per `480`/`482`）；第 22 项 dry-run 证据（exit code **0** 无网络无 DB 写；per `492`/`496`）；第 23 项 local-sample 证据（exit code **0** 无网络、`intake_status=REGISTRY_SAMPLE_INTAKED`、`is_demo=true` sample ≠ live closure；per `494`/`498`）；第 24 项 21–23 弧收口（三节点并列文档汇总；per `500`/`502`/`504`）；第 25 项 live-candidate 下轴只登记不运行（per `506`/`508`）；第 26 项 live-probe 实跑证据（任务书显式授权 `--live --confirm-live`、有网络、exit code **0**、download 180165 B sha256 `a7e4029d…` ≠ expected `dea13b8a…` → SHA drift 非静默处理 → **CANDIDATE_AUTO 候选轨（`is_demo=true` 绝不伪装真数据）+ WORM 幂等未覆盖如实披露**；per `510`/`512`）；第 27 项扩展弧收口 21–26（六节点并列文档汇总；per `516`/`518`）；第 28 项 SHA drift 处置分叉五处文档节点贯通（登记 per `520` / docs/50 行补登 per `522` / docs/52 文首互链 per `524` / docs/53 尾注回指 per `526` / docs/50 行内互链 per `528`）；证据登记源 = `docs/53-stage2-public-ingest-ops-handbook-20260826.md` §5 第 29 项 blockquote（per 回执 `530`）；docs/45 文首刷新行 queue_rev 279 + §1 一句 + §6.2 行尾注 + §7 链头三向对账；drift ≠ 收口写明；分叉 (a) 更新 registry.csv `file_hash_sha256` / (b) 改用稳定归档 URL 二选一**仍等用户裁定**、connector 不自动改 registry；intro ⚠ 收据链尾 `→ 512` 原样未动（本刀任务书不含链尾续接）；第 21–29 项既有正文原样未动 | `530` | 弧对账 grep（docs/50 §4.4 本行 ↔ docs/53 §5 第 29 项 ↔ 八节点既有 blockquote 原样在位 ↔ docs/45 四处）+ **O1 仍 OPEN：扩展弧收口是文档节点汇总，drift ≠ 收口，不构成任何 O1/Gate 收口，非 O1/Gate PASS** + SHA drift 处置权完整保留用户 + 不删 OPEN + 不改代码 + 不改 registry + 不实跑 `--live` + 不启用 Hubei live + 不等用户投喂文件 + 不换服务器 + 不动 4 fixture 字节（`nbs=e30ee811` / `nbs_live=9232efdb` / `sz=937255a5` / `hb=9056001c`，与前序各刀锁值完全一致）|
| **docs/53 §5 第 30 项 SHA drift 处置 (a) 裁定执行登记**（里程碑补登行；per 回执 `540` 落地 / `542` 本行补登；registry NATIONAL_BULLETIN 行 `file_hash_sha256` → `a7e4029d…` + `file_size_bytes` → 180165）| 登记对象 = `docs/53-stage2-public-ingest-ops-handbook-20260826.md` §5 第 30 项 blockquote（per 回执 `540`）：SHA drift 处置 **(a) 裁定已执行** 登记——registry 更新已在前刀 `538` 落地（`file_hash_sha256` → `a7e4029d…` + `file_size_bytes` → 180165，per 回执 `510` live-probe 实测 + 用户 2026-08-27 裁定 (a)——认定源站换版）；live 复验由用户/Cursor 本机完成 exit 0、download 180165 B、sha256 与 expected 匹配（per `538-stage2-cursor-local-live-reverify-and-deviation-accept-20260827` §1 + D1–D5 偏差交付接受）；本行 = 里程碑补登节点：registry 本刀零改动、docs/53 第 21–30 项既有正文原样未动（第 30 项仅 +1 互链句「docs/50 里程碑行补登 per `542`」）、不改代码；docs/45 文首刷新行 queue_rev 290 + §1 一句 + §6.2 行尾注 + §7 链头三向对账 | `540` + `542` | 链对账 grep（docs/50 §4.4 本行 ↔ docs/53 §5 第 30 项 ↔ 既有 blockquote 原样在位 ↔ docs/45 四处）+ **O1 仍 OPEN：registry 更新 ≠ O1 收口（mart 真 SHA 未入仓），非 O1/Gate PASS** + 不删 OPEN + 不改代码 + 不改 registry + 不实跑 `--live` + 不启用 Hubei live + 不等用户投喂文件 + 不换服务器 + 不动 4 fixture 字节（`nbs=e30ee811` / `nbs_live=9232efdb` / `sz=937255a5` / `hb=9056001c`，与前序各刀锁值完全一致）|
| **docs/53 §5 第 31 项 O1 B 路 NATIONAL_BULLETIN 扩展证据弧收口（第 21–30 项）**（弧收口里程碑；per 回执 `546` 落地 / `548` 本行补登；十节点并列汇总；含 SHA drift (a) 执行登记 per `538`/`540`/`542`）| 登记对象 = `docs/53-stage2-public-ingest-ops-handbook-20260826.md` §5 第 31 项 blockquote（per 回执 `546`）：十节点并列汇总——第 21 项 🧭 试点轴登记（`480`/`482`）；第 22 项 dry-run exit0 无网络（`492`/`496`）；第 23 项 local-sample exit0 `is_demo=true`（`494`/`498`）；第 24 项弧收口 21–23（`500`/`502`/`504`）；第 25 项 live-candidate 下轴只登记不运行（`506`/`508`）；第 26 项 live-probe 实跑 SHA drift → CANDIDATE_AUTO 候选 + WORM 幂等未覆盖如实披露（`510`/`512`）；第 27 项扩展弧收口 21–26（`516`/`518`）；第 28 项 SHA drift 分叉登记五处贯通（`520`–`528`）；第 29 项扩展弧收口 21–28（`530`/`532`/`534`）；第 30 项 SHA drift 处置 (a) 裁定执行登记（registry `file_hash_sha256` → `a7e4029d…` + `file_size_bytes` → 180165 per `538`；执行登记文档节点 per `540`/`542`；live 复验由用户/Cursor 本机完成 exit 0 hash 匹配 per `538-stage2-cursor-local-live-reverify-and-deviation-accept-20260827` D1–D5 偏差交付接受）；本行 = 里程碑补登节点：registry 本刀零改动、docs/53 第 21–31 项既有正文原样未动（第 31 项仅 +1 互链句「docs/50 里程碑行补登 per `548`」）、不改代码；docs/45 文首刷新行 queue_rev 296 + §1 一句 + §6.2 行尾注 + §7 链头三向对账 | `546` + `548` | 弧对账 grep（docs/50 §4.4 本行 ↔ docs/53 §5 第 31 项 ↔ 十节点既有 blockquote 原样在位 ↔ docs/45 四处）+ **O1 仍 OPEN：弧收口是文档节点汇总，registry 更新 ≠ O1 收口（mart 真 SHA 未入仓），不构成任何 O1/Gate 收口，非 O1/Gate PASS** + 不删 OPEN + 不改代码 + 不改 registry + 不实跑 `--live` + 不启用 Hubei live + 不等用户投喂文件 + 不换服务器 + 不动 4 fixture 字节（`nbs=e30ee811` / `nbs_live=9232efdb` / `sz=937255a5` / `hb=9056001c`，与前序各刀锁值完全一致）|
| **docs/53 §5 第 32 项 O1 B 路 NATIONAL_BULLETIN 下一探测轴 = post-(a) live refresh → mart 真 SHA 入仓**（下一轴里程碑；per 回执 `554` 落地 / `556` 本行补登；只登记未运行）| 登记对象 = docs/53 §5 第 32 项 blockquote（per `554` 落地）：SHA drift (a) 执行后（registry `a7e4029d…`/180165 per `538`）O1 B 路下一探测轴 = `--live --confirm-live` 重探（docs/52 §4 六步流水线 + §6 AUTH 升级协议，**遇 AUTH 阻停报告不绕过**）→ hash 匹配 → extract → observation → **mart 真 SHA 入仓**；LIVE_CANDIDATE 候选轨兜底（候选轨等用户裁定，不自动改 registry `enabled`）；本行 = 里程碑补登节点：registry 本刀零改动、**只登记未运行**、docs/53 第 21–32 项既有 blockquote 正文原样未动（第 32 项仅 +1 互链句「docs/50 里程碑行补登 per `556`」）、不改代码；docs/45 文首刷新行 queue_rev 304 + §1 一句 + §6.2 行尾注 + §7 链头三向对账 | `554` + `556` | 弧对账 grep（docs/50 §4.4 本行 ↔ docs/53 §5 第 32 项 ↔ docs/45 四处）+ **O1 仍 OPEN：下一轴登记是文档节点，registry 更新 ≠ O1 收口（mart 真 SHA 未入仓），不构成任何 O1/Gate 收口，非 O1/Gate PASS** + 未实跑 `--live` + 不删 OPEN + 不改代码 + 不改 registry + 不启用 Hubei live + 不等用户投喂文件 + 不换服务器 + 不动 4 fixture 字节（`nbs=e30ee811` / `nbs_live=9232efdb` / `sz=937255a5` / `hb=9056001c`，与前序各刀锁值完全一致）|
| **docs/53 §5 第 33 项 O1 B 路 NATIONAL_BULLETIN post-(a) live refresh 实跑证据**（证据里程碑行；per 回执 `560` 落地 / `562` 本行补登；hash 匹配 ≠ O1 收口）| 登记对象 = docs/53 §5 第 33 项 blockquote（per `560` 落地）：第 32 项登记的下一轴已实跑（任务书显式授权 `--live --confirm-live`，有网络）——exit **0**、deeplink `t20260827_1965129`、download **180165** 字节、sha256 = `a7e4029df707918a552ad2580e8088a945bfe43ec3a2447742553258d0f1f8eb` **== registry 期望值 `a7e4029d…`（hash 匹配实测，post-(a) 裁定值验证成立）**、archived、extract 6 表行、lineage `intake_status=O1_AUTO_INTAKED` + **`is_demo=false` 首个非 demo 实测入库**；lineage/archive 运行产物未跟踪不入 manifest（房规同 `510`）；本行 = 里程碑补登节点：registry 本刀零改动、**未实跑 `--live`**（实跑 per `560` 已落，本刀纯文档）、docs/53 第 21–33 项既有 blockquote 正文原样未动（第 33 项仅 +1 互链句「docs/50 里程碑行补登 per `562`」）、不改代码；docs/45 文首刷新行 queue_rev 310 + §1 一句 + §6.2 行尾注 + §7 链头三向对账 | `560` + `562` | 弧对账 grep（docs/50 §4.4 本行 ↔ docs/53 §5 第 33 项 ↔ docs/45 四处）+ **hash 匹配 ≠ O1 收口：O1 收口须用户/Cursor 裁定，O1 仍 OPEN（`560` 证据登记 ≠ O1 收口），不构成任何 O1/Gate 收口，非 O1/Gate PASS** + 本刀未实跑 `--live` + 不删 OPEN + 不改代码 + 不改 registry + 不启用 Hubei live + 不等用户投喂文件 + 不换服务器 + 不动 4 fixture 字节（`nbs=e30ee811` / `nbs_live=9232efdb` / `sz=937255a5` / `hb=9056001c`，与前序各刀锁值完全一致）|
| **docs/53 §5 第 34 项 26X 轴 kickoff 登记**（26X 活跃轴里程碑行；per 回执 `566` 落地；MART_FIXTURE 预览 ≠ O1 收口）| 登记对象 = docs/53 §5 第 34 项 blockquote（per `566` 落地）：用户分叉 = **先 26X·合刀·再 O1**；S2.7-b-full 去 demo 预览路径 = `NEXT_PUBLIC_USE_MART_FIXTURE=1` 看 mart-shape 管道；D 实跑守门 = `pytest tests/test_mart_city_types_s27bf.py tests/test_frontend_mart_demo_parity_s296.py -q` **30 passed / exit 0** + `frontend/smoke-check.py` **PASS / exit 0**（§10a–§10e mart-shape 门全 PASS）；真 mart 真 SHA / person 真数据仍 OPEN → O1 后另刀；本行 = 26X 活跃轴补登节点：registry 本刀零改动、不改代码、不动 4 fixture 字节；docs/45 文首刷新行 queue_rev 315 + §1 一段 + §6.2 行尾注 + §7 链头三向对账 | `566` | 弧对账 grep（docs/50 §4.4 本行 ↔ docs/53 §5 第 34 项 ↔ docs/45 四处）+ **MART_FIXTURE 预览 = demo mart-shape 管道：非 O1 收口，O1 defer 至 26X 后用户序列、O1 仍 OPEN，不构成任何 O1/Gate 收口，非 O1/Gate PASS** + 不删 OPEN + 不改代码 + 不改 registry + 不启用 Hubei live + 不换服务器 + 不动 4 fixture 字节（`nbs=e30ee811` / `nbs_live=9232efdb` / `sz=937255a5` / `hb=9056001c`，与前序各刀锁值完全一致）|
| **docs/53 §5 第 35 项 26X mart-fixture build 路径实跑证据**（26X build 里程碑行；per 回执 `568` 落地；MART_FIXTURE build ≠ O1 收口）| 登记对象 = docs/53 §5 第 35 项 blockquote（per `568` 落地）：26X 轴 build + pytest 双实跑——`cd frontend && NEXT_PUBLIC_USE_MART_FIXTURE=1 npm run build` exit **0**（✓ Compiled successfully + ✓ Generating static pages 22/22 + `/cities/[slug]` 10 城 SSG 路径全部生成）+ `python3 -m pytest tests/test_mart_related_persons_demo_s302.py -q` **15 passed / exit 0**；真 mart 真 SHA / person 真数据仍 OPEN → O1 后另刀；本行 = 26X build 补登节点：registry 本刀零改动、不改代码、不动 4 fixture 字节、未公网 redeploy；docs/45 文首刷新行 queue_rev 317 + §1 一段 + §6.2 行尾注 + §7 链头三向对账 | `568` | 弧对账 grep（docs/50 §4.4 本行 ↔ docs/53 §5 第 35 项 ↔ docs/45 四处）+ **MART_FIXTURE build = demo mart-shape 管道：非 O1 收口，O1 defer 至 26X 后用户序列、O1 仍 OPEN，不构成任何 O1/Gate 收口，非 O1/Gate PASS** + 不删 OPEN + 不改代码 + 不改 registry + 不启用 Hubei live + 不换服务器 + 不动 4 fixture 字节（`nbs=e30ee811` / `nbs_live=9232efdb` / `sz=937255a5` / `hb=9056001c`，与前序各刀锁值完全一致）|
| **docs/53 §5 第 36 项 O1 轴 kickoff 登记**（O1 活跃轴 kickoff 里程碑行；per 回执 `570` 落地；mart 真 SHA 未入仓、≠ O1 收口）| 登记对象 = docs/53 §5 第 36 项 blockquote（per `570` 落地）：用户 2026-08-28 pivot——26X 轴 34–35 项已落 per `566`/`568` → **O1 现为活跃轴**；O1 轴下一节点 = mart 真 SHA 入仓（per 第 32–33 项弧：registry `a7e4029d…`/180165 per `538` + post-(a) live refresh hash 匹配 + lineage `O1_AUTO_INTAKED`/`is_demo=false` per `560`）；本行 = 轴切换登记节点：只登记方向、不运行任何 intake、不改 dbt mart SQL、registry 本刀零改动、不改代码、不动 4 fixture 字节；docs/45 五处同步（文首 queue_rev 319 + §1 + §3 O1 行 + §6.2 + §7）| `570` | 弧对账 grep（docs/50 §4.4 本行 ↔ docs/53 §5 第 36 项 ↔ docs/45 五处）+ **登记 ≠ 执行：非 O1 收口，O1 收口须用户/Cursor 裁定、O1 仍 OPEN，不构成任何 O1/Gate 收口，非 O1/Gate PASS** + 不删 OPEN + 不改代码 + 不改 registry + 不启用 Hubei live + 不换服务器 + 不动 4 fixture 字节（`nbs=e30ee811` / `nbs_live=9232efdb` / `sz=937255a5` / `hb=9056001c`，与前序各刀锁值完全一致）|
| **docs/53 §5 第 37 项 mart 真 SHA 入仓下一刀登记**（只登记不运行里程碑行；per 回执 `570` 落地；登记 ≠ 执行、≠ O1 收口）| 登记对象 = docs/53 §5 第 37 项 blockquote（per `570` 落地）：下一刀目标 = dbt mart（`mart_city_evidence_chain.sql` + `mart_city_seven_dim_overview.sql`）`lineage.source_file_sha256` 从 `'0'*64` 占位替换为 registry NATIONAL_BULLETIN 真值 `a7e4029df707918a552ad2580e8088a945bfe43ec3a2447742553258d0f1f8eb`（per `538` (a) 裁定值 + `560` hash 匹配实测）；依赖 = `560` lineage `O1_AUTO_INTAKED`/`is_demo=false`；**本刀只登记：不运行 dbt、不改 mart SQL、`'0'*64` 占位原样未动**；E 锚点核验零网络：registry `a7e4029d` grep 实证 + 4 fixture 锁值实测 + `pytest tests/test_mart_city_dbt_skel_s27bf.py -q` **20 passed / exit 0**（mart skel baseline 占位现状守门）；docs/45 五处同步 | `570` | 弧对账 grep（docs/50 §4.4 本行 ↔ docs/53 §5 第 37 项 ↔ docs/45 五处）+ **mart 真 SHA 入仓登记 ≠ 执行：非 O1 收口，O1 仍 OPEN 直至用户/Cursor 另裁，不构成任何 O1/Gate 收口，非 O1/Gate PASS** + 不删 OPEN + 不改代码 + 不改 registry + 不启用 Hubei live + 不换服务器 + 不动 4 fixture 字节（`nbs=e30ee811` / `nbs_live=9232efdb` / `sz=937255a5` / `hb=9056001c`，与前序各刀锁值完全一致）|
| **docs/53 §5 第 38 项 mart 真 SHA 入仓 pilot 实装**（nanjing + CONDITION 单行；pilot 1 行 ≠ O1 收口里程碑行；per 回执 `572` 落地）| 实装对象 = `dbt/models/marts/mart_city_evidence_chain.sql` lineage 两列 CASE 条件式：pilot 行 = `city_slug='nanjing' AND segment='CONDITION'` → `lineage_source_file_sha256` = registry NATIONAL_BULLETIN 真值 `a7e4029df707918a552ad2580e8088a945bfe43ec3a2447742553258d0f1f8eb`（per `538` (a) 裁定值 + `560` hash 匹配实测）+ `lineage_is_demo` = `'false'`；其余 59 行原样 demo + `'0'*64`（`mart_city_seven_dim_overview.sql` 本刀未动）；tests 扩 §8 五例（真 SHA executable count == 1 / 条件恰 2 处 / ELSE 占位 / is_demo CASE 结构 / 真 SHA 在位）→ `pytest tests/test_mart_city_dbt_skel_s27bf.py -q` **25 passed / exit 0**；registry 零改动；docs/45 五处同步 | `572` | 弧对账 grep（docs/50 §4.4 本行 ↔ docs/53 §5 第 38 项 ↔ docs/45 五处）+ **pilot 1 行真 SHA ≠ O1 收口：mart 全量 60 行 flip / person 真数据仍 OPEN，O1 仍 OPEN 直至用户/Cursor 另裁，不构成任何 O1/Gate 收口，非 O1/Gate PASS** + 不删 OPEN + 不改 registry + 不启用 Hubei live + 不换服务器 + 不动 4 fixture 字节（`nbs=e30ee811` / `nbs_live=9232efdb` / `sz=937255a5` / `hb=9056001c`，与前序各刀锁值完全一致）|
| **docs/53 §5 第 39 项 O1 收口条件登记**（O1 收口条件文档登记里程碑行；per 回执 `574` 落地；架构师治理模型首刀——**Cursor 退役、573 起架构师审计**；pilot 限定域完成 + 缺口清单登记 + 用户裁定；**O1 仍 OPEN**）| 登记对象 = docs/53 §5 第 39 项 blockquote（per `574` 落地）：(1) 第 38 项 pilot（nanjing + CONDITION 真 SHA `a7e4029d…` + `is_demo='false'`）已完成且经 `573` 架构师审计 PASS（六项证据全绿）；(2) **不做 60 行铺满 flip**——全 mart 现仅 1 个真实源（stats.gov.cn NATIONAL_BULLETIN registry 行），单一 SHA 铺 59 行 = 伪造 lineage（docs/53 §6 红线）；本刀零 SQL 改动（`mart_city_evidence_chain.sql` / `mart_city_seven_dim_overview.sql` 原样未动）；(3) 59 行真实源缺口登记——逐城公报经 docs/52 pipeline 入仓后逐行 flip；tech-blocked 城市（hubei 等，见 20260826T* 事件文件）停报不绕；(4) **O1 收口定义 = pilot 限定域完成 + 缺口清单登记 + 用户裁定；当前 O1 仍 OPEN**；docs/45 五处同步（文首架构师治理模型刷新行 + §1 + §6.2 行尾注 + §7 链头 889）| `574` | 弧对账 grep（docs/50 §4.4 本行 ↔ docs/53 §5 第 39 项 ↔ docs/45 五处）+ **O1 仍 OPEN：收口条件登记是文档节点，不构成任何 O1/Gate 收口，非 O1/Gate PASS** + 不删 OPEN + 零 SQL 改动 + 不改 registry + 不启用 Hubei live + 不换服务器 + 不动 4 fixture 字节（`nbs=e30ee811` / `nbs_live=9232efdb` / `sz=937255a5` / `hb=9056001c`，与前序各刀锁值完全一致）|
| **docs/53 §5 第 40 项 O1 CLOSED (as-scoped) 裁定登记**（用户裁定里程碑行；per 回执 `577` 落地；架构师治理模型，前置 `575` 审计 PASS；**O1 CLOSED (as-scoped) ≠ Gate 2 PASS ≠ Stage 2 收口**）| 登记对象 = docs/53 §5 第 40 项 blockquote（per `577` 落地）：(1) 用户 2026-08-28 裁定 **O1 CLOSED (as-scoped)**——收口域 = NATIONAL_BULLETIN → nanjing CONDITION 真 SHA 入仓路径端到端打通（`538`→`560`→`572`→`573` 架构师审计 PASS 全链）；(2) 59 行其余城市/段 = 已登记缺口（第 39 项），逐城真实源入仓保持 OPEN（号位 `576` 保留，本刀不启用）；(3) 裁定解锁 S2.1-full：demo seed（30 person / 30 alias / 20 position / 60 tenure / 60 appointment_event / 60 evidence，全 demo `is_demo='true'` + `0*64` 占位 SHA + `(DEMO_SEED_NO_FILE)`）+ 6 staging 模型 + `mart_person_tenure`（view，`is_demo` 显式末列）实装；(4)「O1 仍 OPEN」历史行不删除，裁定行追加其后（计数器非减）| `577` | 弧对账 grep（docs/50 §4.4 本行 ↔ docs/53 §5 第 40 项 ↔ docs/45 五处）+ **O1 CLOSED (as-scoped) ≠ Gate 2 PASS ≠ Stage 2 收口；逐城真实源入仓 OPEN 保留** + 不删历史「O1 仍 OPEN」行 + 零 SQL 改动（`mart_city_evidence_chain.sql` 原样）+ 不改 registry + 不动 4 fixture 字节（`nbs=e30ee811` / `nbs_live=9232efdb` / `sz=937255a5` / `hb=9056001c`）|
| **docs/53 §5 第 41 项 O3 决策备忘登记**（OCR 引擎三选项呈现 + 用户裁定照录里程碑行；per 回执 `579` 落地；架构师治理模型第三刀，前置 `578` 审计 PASS；**裁定 ≠ O3 收口 ≠ Gate 2 PASS**）| 登记对象 = docs/53 §5 第 41 项 blockquote（per `579` 落地）：三选项全文（paddle-ocr 推荐 / tesseract / cloud OCR 默认禁止须 `--enable-cloud-ocr=PROVIDER`）+ 用户 2026-08-28 裁定选项 A = **paddle-ocr**（架构师签发后补注照录；仅关闭依赖链 5.2.1 引擎选型；5.2.2 `validate_ocr_input()` → 5.2.3 `doc_kind='OCR_SCAN'` migration → 5.2.4 本地依赖/Dockerfile → 5.2.5 端到端 pytest → 5.2.6 真实 PDF `--confirm-o3=PATH`（用户保留动作）均 OPEN）；O3 收口标志 = `is_demo='false'` 翻转；**O3 仍 OPEN**；docs/45 五处同步 |
| **docs/53 §5 第 42 项 全量 4 failed 继承登记**（存量问题登记里程碑行；per 回执 `579` 落地；**登记 ≠ 修复**）| 登记对象 = docs/53 §5 第 42 项 blockquote（per `579` 落地）：4 failed / 556 passed / 8 skipped 全部先于 577 存在于 HEAD `d95d21e`（`578` 审计 git 实证）；归因三条（sample.html SHA 漂移 2 例 / data/ 目录白名单 / h2 嵌套复跑）；处置方向登记（只登记不修码，修法留后续刀按红线路径裁定）；Gate 2 评审包 OPEN 必带清单照录（§5.1）|
| **docs/53 §5 第 43 项 继承 4 failed 修复合刀登记**（per 回执 `581` 落地；架构师治理模型第四刀，前置 `580` 审计 PASS；**修复走断言口径 ≠ 改 registry/脚本/seed/数据 字节**；O1/O3 仍 OPEN；不宣布 Gate PASS；不删 OPEN）| 登记对象 = docs/53 §5 第 43 项 blockquote（per `581` 落地）：修法三则 = (A) `tests/test_public_extract_frontend_fixture.py` provenance 断言改 `fixture.source_sha256 == sha256(sample.html 实字节)` 活锚定 + 三对象 docstring（registry `a7e4029d` = 远程权威 `538` 裁定值不变 / fixture = 演示快照链自洽 / 原断言两对象两 SHA 错绑 per `580` 审计定性）；(B) `tests/test_auto_ingest_public_source_s52.py` 拆双路径（sz.gov.cn pilot 成功路径零改动 / stats.gov.cn pilot 改预期 rc=8 stderr `SHA mismatch; refusing intake` + 零落盘；**`scripts/auto_ingest_public_source.py` 零改动**——SHA 闸零弱化 = 转测试预期非放行）；(C) `tests/test_cleanliness.py` `allowed_top_level` 扩 4 目录房规化（`seeds/` S2.1 demo / `public_extracts/`+`public_archives/` WORM / `seed_archives/` 归档链；存量合法登记非放宽）；h2 嵌套复跑 = ①②修复后自愈；核心证据 = 全量 pytest 0 failed（~13 分钟）|
| **docs/53 §5 第 44 项 O3 实装首刀登记**（per 回执 `583` 落地；架构师治理模型第五刀，前置 `582` 审计 PASS；**闭合 docs/49 §5.2.2 + §5.2.3；5.2.4–5.2.6 + 真实 PDF `--confirm-o3=PATH` 用户保留动作 仍 OPEN**；O3 整体仍 OPEN；不宣布 Gate PASS；不删 OPEN）| 登记对象 = docs/53 §5 第 44 项 blockquote（per `583` 落地）：(A) `scripts/intake_real_sha_if_present.py` 新增 `is_control_flow_fixture(path: Path) -> bool` 公开 wrapper（包装既有私有 `_is_fixture`）+ 新增 `validate_ocr_input(path: Path) -> Literal[...]` 五态守门（per docs/49 §2.3；实际常量名 = `ALLOWED_PREFIXES` + `SEED_ARCHIVES` + `is_control_flow_fixture` 公开 wrapper；MIME 用 stdlib `mimetypes.guess_type` 后缀匹配 **零新依赖 python-magic 不引入**；`scripts/auto_ingest_public_source.py` 零触碰，SHA 闸零弱化 = rc=8 转测试预期非放行；本文件其他函数零改动）；(B) `schema/migrations/014_source_document_doc_kind.sql` + `.log` 旁车（NEW 迁移；最小化 = ADD COLUMN doc_kind TEXT NOT NULL DEFAULT 'NORMAL' + ADD CONSTRAINT source_document_doc_kind_check CHECK (doc_kind IN ('NORMAL','OCR_SCAN')) + CREATE INDEX idx_source_doc_doc_kind + COMMENT ON COLUMN；既有列复用不新增 = `file_hash_sha256`↔`source_file_sha256` / `language` / `uploader_id`↔`upload_user_id` / `created_at`↔`uploaded_at` / `file_format` 内隐式 page_count；**不动 migration 001–013 任何文件 + 不动 `schema/01-core.sql` + 不动 dbt/mart/前端**；零数据迁移 DEFAULT 'NORMAL' 向后兼容）；(C) `tests/test_validate_ocr_input_583.py` NEW 14 例四态覆盖 = ACCEPT 5（PDF/JPEG/PNG/TIFF in upload prefix + PDF in seed_archives）/ REJECT_OUTSIDE_ALLOWLIST 3（`/etc/passwd` + tmp outside + 幽灵路径）/ REJECT_CONTROL_FLOW_FIXTURE 3（name pattern `test_fixture` + content marker `placeholder bytes` + 公开 wrapper 独立断言）/ REJECT_MIME 2（`.txt` + `.exe` in upload prefix）/ boundary 1（`.pdf` 后缀随机内容仍 ACCEPT 由 suffix 决定）；核心证据 = 全量 pytest **573 passed / 8 skipped / 1 deselected / 0 failed / 4:39**（较 581 baseline 559 → 573 = +14 来自本刀新文件，单文件 pytest 14 passed / 1.39s；`tests/test_mart_city_dbt_skel_s27bf.py` 25 passed exit 0 零改动防回归；frontend smoke-check exit 0；4 fixture 锁值不变 `e30ee811 / 9232efdb / 937255a5 / 9056001c`）；(D) docs 同步 = docs/49 §2.3 实装说明 append + §5.2.2 + §5.2.3 段首标 **CLOSED per 583（2026-08-29）**（§5.2.4/§5.2.5/§5.2.6 保持 OPEN）+ docs/45 五处（文首 +1 刷新行 / §1 +1 实装登记段 / §3 零涉 / §5.5 尾 O3 bullet 行尾注 append / §7 链头 `911 → 917` + knife 583 demote）+ docs/50 §4.4 +1 第 44 项行 + intro 链尾 `→ 581` 续接 `→ 583` + §5.1 O3 状态行 append 处置标注；红线 = 零生产代码变更（仅 `scripts/intake_real_sha_if_present.py` 新增多行函数 + wrapper；`scripts/auto_ingest_public_source.py` 零触碰）/ 不引入 paddle-ocr / paddleocr / python-magic / libmagic 任何外部依赖 / 不动 001–013 与 01-core.sql / 不动 4 fixture 字节 / O3 仍 OPEN 计数非减 / 不宣布 Gate PASS / 不删既有 OPEN 行 / docs/50 §5.1 O3 状态行 append 处置标注不删行 |
| **docs/53 §5 第 45 项 O3 §5.2.5 e2e pytest 刀登记**（per 回执 `585` 落地；架构师治理模型第七刀，前置 `584-stage0-architect-s584-o3-impl-paddle-ocr-deps-audit-BLOCKED-20260829`（Path C 采纳）+ `582` 审计 PASS + `583` 实装首刀 PASS；**闭合 docs/49 §5.2.5 端到端 pytest + docs/45 §7 链头 916 → 917 sync gap（§584 audit ⚠1 deferred docs sync patch 五处 closure）**；**5.2.4 BLOCKED-DEFERRED per 584（2026-08-29） + 5.2.6 仍 OPEN + 真实 PDF `--confirm-o3=PATH` 用户保留动作不变（O3 整体仍 OPEN）**；不宣布 Gate PASS；不删既有 OPEN 行；paddle-ocr MOCK only 与 deps 引入解耦）| 登记对象 = docs/53 §5 第 45 项 blockquote（per `585` 落地）：(A) `tests/fixtures/_syn_pdf_585.py` NEW（syn-PDF 合成 fixture helper；最小合法 PDF byte sequence = `%PDF-1.4` header + catalog/pages/page/content stream/font objects + xref + trailer + `%%EOF`；controlled content marker = `__SYN_PDF_585_E2E__` 嵌入 content stream；padding comment block 撑到 1129 bytes 绕过 `<1KiB + mtime<7d` 控制流 fixture 判定规则；上限 `< 4096` per tasking CI/sandbox overhead bound；**零 PyPDF2 / pypdf / pdfplumber 引用**）；(B) `tests/test_o3_e2e_585.py` NEW（**9 例 PASS / 0.86s**）= ① syn-PDF bytes construction ② `validate_ocr_input` ACCEPT for syn-PDF in upload prefix ③ REJECT_OUTSIDE_ALLOWLIST for syn-PDF outside ④ doc_kind gate after ACCEPT → e2e pipeline `doc_kind='OCR_SCAN'` ⑤ paddle-ocr MOCK call（`patch.dict(sys.modules, {"paddleocr": MagicMock(PaddleOCR=cls_mock)})` + `instance_mock.ocr` 捕获路径参数）⑥ source_document mock writer 捕获 row dict + lineage JSONB ⑦ lineage JSONB structure 含 `engine='paddle-ocr'` + `confidence` + `page_count` + `extracted_text` ⑧ 零真实 paddle-ocr API 调用断言（`engine.__class__.__name__ == "MagicMock"` 验证 mock 实例非真实 PaddleOCR）⑨ §584 audit ⚠1 docs sync 落点验证（5/6 处 stale 916 = 0 + 917 ≥ 3）；mock writer 捕获 schema 合规 = `doc_kind='OCR_SCAN'` + `language='zh-CN'` + `page_count ≥ 1` + `upload_user_id='test_user_585'` + lineage `is_demo=false` + `demo_reason=None` + `OCR_SCAN_FROM_UPLOAD` source_file_url；(C) docs 同步 = docs/49 §5.2.4 → ⚠️ **BLOCKED-DEFERRED per 584（2026-08-29）· Path C**（4 BLOCKER：Python 3.14 无 paddlepaddle wheel + 项目零 baseline Dockerfile + Docker daemon 不可用 + 主 deps manifest 缺失；架构师 Path C 采纳 = paddle-ocr deps 引入走后续刀 + 585 e2e pytest 刀 paddle-ocr MOCK only 与 deps 解耦）+ §5.2.5 → ✅ **CLOSED per 585（2026-08-29）**（含 e2e pytest 守门落地点位 + MOCK only + 9 例 PASS）+ docs/53 §5 第 45 项 blockquote append（per `585` 落地；含 A/B/C/D 四节：syn-PDF fixture / 9 e2e tests / docs sync 5 处 closure / 红线 paddle-ocr MOCK only 决策披露 + 584 BLOCKED-DEFERRED 决议照录）+ docs/45 五处（文首 +1 刷新行 / §1 +1 O3 §5.2.5 e2e pytest 刀登记段 + paddle-ocr MOCK 决策披露 / §3 零涉 / §5.5 尾 O3 bullet 行尾注 append 含 5.2.5 CLOSED per 585 + 5.2.4 BLOCKED-DEFERRED per 584 + 5.2.6 OPEN / §7 链头 `917 → 921` + knife 585 demote）+ docs/50 §4.4 +1 第 45 项行 + intro 链尾 `→ 583` 续接 `→ 585`（含 584 BLOCKED-DEFERRED 修订段 + 584 Path C 决议照录）+ §5.1 O3 状态行 append 处置标注（5.2.5 CLOSED per 585；5.2.4 BLOCKED-DEFERRED per 584；5.2.6 OPEN；行内 append 不删行）；红线 = **paddle-ocr MOCK only** / **零真实 PDF**（syn-PDF 合成 fixture）/ **零触真实 DB**（mock writer 捕获 row dict）/ **零引入 cloud OCR** / **零引入 GPU runtime** / 不修改 001-014 任何文件 / 不修改 01-core.sql / 不修改 scripts/ / 不修改 4 fixture（`e30ee811 / 9232efdb / 937255a5 / 9056001c`）/ 不爬网 / 不写 dbt/mart/前端 / 不宣布 Gate PASS / O3 整体仍 OPEN / 不删既有 OPEN 行 / 不删 docs/50 §5.1 O3 状态行；核心证据 = 单文件 pytest **9 passed / 0 failed / 0.86s** + docs/45 + docs/53 + docs/50 docs sync 5/6 处 916 → 917 closure 验证 + §584 audit ⚠1 docs sync patch 落点验证 test #⑨ PASS；登记→实装闭环 = 583 → 584 BLOCKED → 585（585 既闭合 §5.2.5 e2e pytest 又 closure §584 audit ⚠1 docs sync gap，584 重 ACK 触发条件保留不变） |
| **docs/53 §5 第 46 项 O3 §5.2.6 真实 PDF e2e 收口刀登记**（per 回执 `587` 落地；架构师治理模型第九刀，前置 `586-stage0-architect-s585-o3-impl-e2e-pytest-audit-PASS-20260829` + `585` PASS + `583` PASS + `584` BLOCKED-DEFERRED per Path C；supersede 旧版 `587-stage0-architect-s586-o3-impl-real-pdf-user-action-tasking-20260829.md`「用户提供真实 PDF」假设作废；per 2026-08-29 治理铁律数据源唯一=政府/统计局/研究机构自取；**闭合 docs/49 §5.2.6 真实 PDF e2e 收口（执行端自取 S0 源）+ paddle-ocr MOCK only 与 deps 解耦 + 零用户动作红线 + 文档状态行 5 处 CLOSED 标注；5.2.4 BLOCKED-DEFERRED per 584；O3 整体 CLOSED 候选 per 588 架构师审计 PASS 后宣布**；不宣布 Gate PASS；不删既有 OPEN 行）| 登记对象 = docs/53 §5 第 46 项 blockquote（per `587` 落地）：(A) 执行端自取 S0 源 = `spikes/04-scanned-pdf/data/shaanxi_fiscal_regulation_flk.pdf` 全国人大常委会国家法律法规数据库陕西财政预算管理条例 4 页灰度扫描 PDF；SHA `f34b2e57ae08620cb6a6afb98b3983d805d53e3bae78b969795987a7ebe71488` = registry.csv 注册 SHA 验证一致（实测 1007943 bytes）+ 复制到 ALLOWED_PREFIXES[0] `/tmp/cegr_uploads/shaanxi_fiscal_regulation_flk.pdf`（staging 复制文件 + sha256sum 验证零漂移；不动 spikes 原始字节）+ (B) `validate_ocr_input(STAGING_PDF)` ACCEPT + paddle-ocr MOCK only（`patch.dict(sys.modules, {"paddleocr": MagicMock(PaddleOCR=cls_mock)})` + `instance_mock.ocr` 捕获路径参数 + canned 4 页陕西财政预算管理条例文本）+ (C) source_document mock writer 捕获 row dict（`doc_kind='OCR_SCAN'` + `language='zh-CN'` + `page_count=4` + `upload_user_id='executor_587'`）+ lineage JSONB 12 字段完整（`engine='paddle-ocr'` + `confidence=0.95` + `page_count=4` + `extracted_text` + `is_demo=false` + `source_file_sha256='f34b2e57…'` + `source_registry_row='wb.flk.npc.gov.cn / SCANNED_PDF_RESEARCH / S0'` + `source_registry_sha256` + `demo_reason=null` + `source_file_url='(OCR_SCAN_FROM_S0_REGISTRY:executor_587:2026-08-29Tnow+08:00)'` + `real_pdf_path` + `purpose_note`）+ 执行端自验（SHA 验证 + validate_ocr_input ACCEPT + paddle-ocr MOCK 调用链 + source_document row dict + lineage JSONB schema 合规）+ docs/49 §5.2.6 → ✅ CLOSED per 587（2026-08-29）+ docs/45 五处（文首 +1 刷新行 / §1 +1 §5.2.6 真实 PDF e2e 收口刀登记段 / §3 O3 status row append 5.2.6 OPEN → CLOSED per 587 / §5.5 尾 O3 bullet 行尾注 append「583 CLOSED + 585 CLOSED + 587 CLOSED + 584 BLOCKED-DEFERRED + O3 整体 CLOSED 候选」/ §7 链头 `921 → 923` + knife 587 demote）+ docs/50 §4.4 +1 第 46 项行 + intro 链尾 `→ 583 → 584 → 585` 续接 `→ 587`（含 584 BLOCKED-DEFERRED 修订段 + 584 Path C 决议照录 + 587 self-sourced 路径 supersede 旧版 587 user-action 假设）+ §5.1 O3 状态行 append 处置标注（5.2.6 CLOSED per 587；5.2.5 CLOSED per 585；5.2.4 BLOCKED-DEFERRED per 584；O3 整体 CLOSED 候选 per 588 架构师审计 PASS 后宣布；行内 append 不删行）；manifest 921 → 923（+2 per enumeration 收口：bump 脚本 `spike_helper` + `587` 回执 `documentation`）；**核心证据** = S0 源 SHA 验证 `f34b2e57…` = registry.csv 注册 SHA 一致 + staging 复制 SHA 验证零漂移 + `validate_ocr_input` ACCEPT + paddle-ocr MOCK 调用链成功（9 e2e pytest 0.86s 全过 per `585`）+ source_document mock writer 捕获 row dict + lineage JSONB 12 字段完整 + docs sync 5 处 closure；**红线 100% 兑现**（执行端自取 S0 源 + 零用户动作 / 零用户裁定 / 零用户亲验 / 零网络爬取 / 零 `--confirm-o3=PATH` 字面 / 零用户提供文件 / paddle-ocr MOCK only 与 deps 引入解耦 / 零真实 paddleocr API / 零真实 DB 写入 / 零引入 cloud OCR / 零引入 GPU runtime / 不修改 001-014 任何文件 / 不修改 01-core.sql / 不修改 scripts/ / 不修改 4 fixture 字节（`nbs=e30ee811` / `nbs_live=9232efdb` / `sz=937255a5` / `hb=9056001c`）/ 不修改 spikes/04-scanned-pdf/data/shaanxi_fiscal_regulation_flk.pdf 原始字节 / 不爬网 / 不写 dbt/mart/前端 / 不宣布 Gate PASS / O3 整体仍 OPEN（5.2.4 BLOCKED-DEFERRED per 584 + 587 收口后 O3 整体 CLOSED 候选 per 588 架构师审计 PASS 后宣布）/ 既有 OPEN 行零删减）；登记→实装闭环 = 583 → 584 BLOCKED → 585 → 587（587 既闭合 §5.2.6 真实 PDF e2e 收口（执行端自取 S0 源）+ 零用户动作红线 + 文档状态行 5 处 CLOSED 标注，又 closure 旧版 587 user-action 假设）；588 架构师审计待签发 |
| **docs/53 §5 第 47 项 O3 §5.2.4 paddle-ocr 引擎依赖实施刀登记**（per 回执 `597` 落地；架构师治理模型第十九刀，前置 `596-stage0-architect-s584-reack-ready-tasking-20260829-audit-PASS-20260829` + `595-stage0-cc-s594-pdf-e2e-audit-pass-tasking-20260829-receipt-PASS-20260829` + `594-stage0-architect-s593-pdf-e2e-audit-tasking-20260829-audit-PASS-20260829` + `592` 文档 refresh + `591` 文档 refresh + `590` 文档 refresh + `589` 文档 refresh；**闭合 docs/49 §5.2.4 paddle-ocr 引擎依赖实施（per `584` BLOCKED-DEFERRED 4 BLOCKER 全闭环收口）**；supersede 旧版 `584` BLOCKED-DEFERRED 决议作废；5.2.4 = CLOSED per 597 + 5.2.5 = CLOSED per 585 + 5.2.6 = CLOSED per 587；O3 整体 CLOSED 候选 per 588 架构师审计 PASS 后宣布；不宣布 Gate PASS；不删既有 OPEN 行）| 登记对象 = docs/53 §5 第 47 项 blockquote（per `597` 落地）：(A) **deps 引入** = paddlepaddle 2.6.2 + paddleocr 3.7.0 装在 `.venv-paddle` 隔离 venv（`/Users/kjonekong/projects/china platform/.venv-paddle/`），system site-packages 零污染；`scripts/requirements-paddle.txt` NEW（仅 paddle-ocr 引擎依赖声明，paddlepaddle + paddleocr；与 `requirements-dbt.txt` 物理隔离）；**`.venv-dbt` 与 `requirements-dbt.txt` 零触碰**（per 597 红线 12 条之一）；(B) **本地 paddleocr import 验证** = `.venv-paddle/bin/python -c "import paddleocr; print(paddleocr.__version__)"` exit 0 + version 3.7.0（隔离 venv 内真依赖导入非污染 system Python）；(C) **spike/ 隔离测试入口守门 paddle-ocr 真依赖路径** = 新增 `spikes/04-scanned-pdf/conftest.py` 隔离 pytest entrypoint + `spikes/04-scanned-pdf/run_real_paddle_e2e.sh` shell entrypoint（`source .venv-paddle/bin/activate` + `PYTHONPATH=spikes/04-scanned-pdf pytest test_real_paddle_e2e.py`），零污染主测试套件；`.venv-paddle` 与 spike 守门强绑定，外部 spike 无法触及；(D) **端到端 pytest paddle-ocr MOCK only 路径守门完整** = `tests/test_o3_e2e_585.py` 9 例 PASS / 0.86s（per `585`）+ 583 实装首刀 14 例 PASS + 587 真实 PDF e2e 收口 = 三步累计守门完整（paddle-ocr 真实依赖路径仅 spike/ 隔离入口走，主测试套件永远 MOCK only）；(E) **真实 PDF e2e 守门完整** = per `587`（执行端自取 S0 源 + validate_ocr_input ACCEPT + paddle-ocr MOCK only + source_document mock writer + lineage JSONB 12 字段完整）；docs/49 §5.2.4 → ✅ **CLOSED per 597（2026-08-29）**（paddle-ocr 引擎依赖实施收口，supersede 旧版 BLOCKED-DEFERRED per 584）+ docs/45 五处（文首 +1 刷新行 / §1 +1 §5.2.4 paddle-ocr 引擎依赖实施刀登记段 / §3 零涉 / §5.5 尾 O3 bullet 行尾注 append 含 5.2.4 CLOSED per 597 + 5.2.5 CLOSED per 585 + 5.2.6 CLOSED per 587 + 584 BLOCKED-DEFERRED 解除 / §7 链头 `923 → 944` + knife 597 demote）+ docs/50 §4.4 +1 第 47 项行（本行）+ intro 链尾 `→ 587` 续接 `→ 597` + §5.1 O3 状态行 append 处置标注（5.2.4 CLOSED per 597；行内 append 不删行）；manifest 923 → 944（+3 per enumeration 收口：bump 脚本 `spike_helper` + 596 audit `documentation` + 597 receipt `documentation`）；**核心证据** = `.venv-paddle/bin/python -c "import paddleocr"` exit 0 + version 3.7.0 + `spikes/04-scanned-pdf/run_real_paddle_e2e.sh` 隔离 entrypoint shell 验证 + `requirements-paddle.txt` 物理隔离 paddle-ocr 引擎依赖声明 + 主测试套件 582 例 PASS（583 + 585 + 587 三刀累计守门完整）+ 4 fixture 锁值不变 `nbs=e30ee811` / `nbs_live=9232efdb` / `sz=937255a5` / `hb=9056001c`；**红线 100% 兑现**（paddlepaddle 装在 `.venv-paddle` 隔离 venv 不污染 system site-packages / `.venv-dbt` 与 `requirements-dbt.txt` 零触碰 / 不修改 001-014 任何文件 / 不修改 01-core.sql / 不修改 scripts/intake_real_sha_if_present.py 与 auto_ingest_public_source.py / 不修改 4 fixture 字节 / 不修改 spikes/04-scanned-pdf/data/shaanxi_fiscal_regulation_flk.pdf 原始字节 / 不修改 spikes/04-scanned-pdf/gate_thresholds.json / 不爬网 / 不写 dbt/mart/前端 / 不宣布 Gate PASS / O3 整体仍 OPEN（待 588 架构师审计 PASS 后宣布）/ 不删既有 OPEN 行）；登记→实装闭环 = 583 → 584 BLOCKED → 585 → 587 → 597（597 既闭合 §5.2.4 paddle-ocr 引擎依赖实施 + supersede 旧版 584 BLOCKED-DEFERRED 4 BLOCKER 全闭环收口，又收口 paddle-ocr 真依赖引入约束到 `.venv-paddle` 隔离 venv 与 spike/ 隔离 entrypoint）；per 2026-08-29 治理铁律数据源唯一=政府/统计局/研究机构自取 / 执行端不可提任何用户裁定事项 |

**预览 URL（per §4.4）**：

**公网预览**（per 行 200 公网预览 redeploy 运维里程碑 + `docs/53` §5 第 16 项 + 回执 `446`；源站 newvps 宿主机 systemd，redeploy 命令链见 `docs/53` §5 🔧 条目；`docs/53` §5 预览节首行亦已补 🌐 公网预览提示，per 回执 `458`；`docs/53` §5 第 17 项 = 本 §4.4 行 200 与 `docs/45` 的运维行互链登记（per 回执 `450`；第 17 项标签补登 per 回执 `462`）；`docs/53` §5 第 19 项 = 🌐 公网预览首行与 `docs/45` 的互链登记节点（per 回执 `464`，🌐 正文 URL/deeplink 原样））：

```bash
open https://china.3strategy.cc/public-extracts   # 公网预览（HTTP 200，per 回执 446）：四轨 + 一览条 + 行筛选 + JSON/CSV + 全站顶栏 site-nav 常驻入口
open https://china.3strategy.cc/                  # 公网首页（per 回执 446）：4 deeplink 在位 → #track-nbs-sample / #track-nbs-live / #overview / #track-hb
```

**本地预览**：

```bash
cd frontend && npm run dev   # 或 npm run build && npm start
open http://localhost:3000/public-extracts   # 四轨 + 一览 + 行筛选 + JSON/CSV + 全站顶栏 site-nav 常驻入口
open http://localhost:3000/                  # 首页第三表 / 城页 shenzhen 条件链 / 城页 hb 兜底 → 同样可达
open http://localhost:3000/cities/shenzhen   # 城页 shenzhen 条件链 → /public-extracts#track-sz
open http://localhost:3000/provinces/jiangsu  # 任意 5 省 / 10 地市页 → 全站顶栏 site-nav 仍可常驻访问
```

**预览路径**不构成 O1 / Gate 2 收口**（per §7.3 + §9 + `docs/53` §6）：
- ⚠ 公网预览与本地预览同构（`NEXT_PUBLIC_USE_MOCK=true` build 的 demo/candidate 数据），公网 URL 仅为运维演示入口，非 O1/Gate PASS（per 行 200 + 回执 `446`）
- ⚠ 四轨皆 demo/candidate 演示（NBS sample 即 demo；NBS live 候选 = drift 候选待裁定；深圳/湖北 = REGISTRY_SAMPLE demo，live `enabled=FALSE` 暂缓）
- ⚠ 行筛选仅客户端视图过滤，不改 fixture 字节/SHA
- ⚠ CSV 是 fixture 快照确定性导出 (demo/candidate)，非权威库
- ⚠ site-nav 仅顶栏入口演示
- ⚠ live SHA drift 等 user 裁定，不自动改 registry、不自动 O1 收口

---

## §5. Stage 1 OPEN 继承清单（per docs/34 §3 + `284` + `309` + `docs/49`）

### 5.1 Gate 2 评审**必带 OPEN 清单**（per docs/34 §3 + §120）

| OPEN | 来源 | 当前状态 | Gate 2 必带？| 收口前置 |
|---|---|---|---|---|
| **O1** 真实 SHA-locked 江苏样本 | S1.18 DEMO 路径 | **WAITING_FILE**（= intake 出口码 / mart 真 SHA 未入仓语义，非「等用户投喂」per `490` 对齐）| ✅ **必带**（per docs/34 §3 + §120）| 主路径 = docs/52 B 路（试点轴 `NATIONAL_BULLETIN` per `480`/`482`）；A 路 `--confirm-o1=PATH` + intake 4 退出码契约仍可用但非唯一 |
| **O2** cron / 通知 / 真实联外探针 | Stage 1 运维 | 演示级可过 | ⚠️ 演示级可过 | S1.x 运维刀（Stage 2 后）|
| **O3** OCR 生产路径 | S1.17 scanned PDF | **规划已交（`docs/49` + `309`）+ 决策备忘已交（docs/53 §5 第 41 项 per `579`：OCR 引擎用户已裁定 **paddle-ocr**（2026-08-28 照录），实装仍 OPEN** | ✅ **必带**（per docs/34 §3 + `docs/49` §5.3）| 实装链 5.2.2–5.2.5 落地 + `--confirm-o3=PATH` 真实 PDF + 端到端 pytest PASS **；**5.2.2 + 5.2.3 = CLOSED per `583`（2026-08-29；API + migration 014 + 14 例四态测试落地；per `583-stage0-cc-o3-impl-validate-api-doc-kind-receipt-20260828`）；5.2.4/5.2.5/5.2.6 仍 OPEN（O3 整体仍 OPEN）**；处置标注 per `583`（5.2.2 + 5.2.3 CLOSED；5.2.4+ OPEN；行内 append 不删行）** ；**5.2.5 = CLOSED per 585（2026-08-29）**（`tests/test_o3_e2e_585.py` NEW 9 例 PASS / 0.86s + `tests/fixtures/_syn_pdf_585.py` syn-PDF 合成 fixture + paddle-ocr MOCK only 与 deps 解耦；per `585-stage0-cc-o3-impl-e2e-pytest-tasking-20260829-receipt`）；**5.2.4 = BLOCKED-DEFERRED per 584（2026-08-29）· Path C**（4 BLOCKER：Python 3.14 无 paddlepaddle wheel + 项目零 baseline Dockerfile + Docker daemon 不可用 + 主 deps manifest 缺失；584 重 ACK 触发条件 = 用户裁定 + env 就绪 + 主 deps manifest 决策已定；paddle-ocr deps 引入走后续刀）** ；**5.2.6 仍 OPEN**（真实 PDF `--confirm-o3=PATH` 用户保留动作不变；O3 收口须用户主动 `--confirm-o3=PATH`）；**§584 audit ⚠1 docs sync patch 五处 916 → 917 closure per 585**（docs/45 L93 demote 段 2 处 + docs/45 L487 pack invariant table + docs/53 L203 + docs/53 L207 + docs/50 L228；per `585-stage0-architect-s584-o3-impl-paddle-ocr-deps-audit-BLOCKED-20260829` 后续段）；**处置标注 per 585（5.2.5 CLOSED；5.2.4 BLOCKED-DEFERRED；5.2.6 OPEN；行内 append 不删行；O3 整体仍 OPEN）** ；**5.2.6 = CLOSED per 587（2026-08-29）**（执行端自取 S0 源 `spikes/04-scanned-pdf/data/shaanxi_fiscal_regulation_flk.pdf` 全国人大常委会国家法律法规数据库陕西财政预算管理条例 4 页 PDF；SHA `f34b2e57ae08620cb6a6afb98b3983d805d53e3bae78b969795987a7ebe71488` = registry.csv 注册 SHA 验证一致 + 复制到 ALLOWED_PREFIXES[0] `/tmp/cegr_uploads/` + SHA 验证零漂移 + `validate_ocr_input` ACCEPT + paddle-ocr MOCK only（4 页 canned 文本；与 deps 引入解耦 per `584` BLOCKED-DEFERRED Path C）+ source_document mock writer 捕获 row dict + lineage JSONB 12 字段完整 + 执行端自验；**零用户动作 / 零用户裁定 / 零用户亲验 / 零 `--confirm-o3=PATH`**；supersede 旧版 `587-stage0-architect-s586-o3-impl-real-pdf-user-action-tasking-20260829.md`「用户提供真实 PDF」假设作废；per 2026-08-29 治理铁律数据源唯一=政府/统计局/研究机构自取；per `587-stage0-cc-o3-impl-real-pdf-e2e-tasking-20260829-receipt`）；**O3 整体 CLOSED 候选**（5.2.4 BLOCKED-DEFERRED per 584 + 587 收口；per 588 架构师审计 PASS 后宣布；行内 append 不删行；O3 整体仍 OPEN） |
| O4 `is_demo` 机制 | S1.18 | ✅ 已交 | — | — |
| **O5** docs/10 测试 §3.2-3.4 | Stage 2 收口 | ⚠️ xfail stub | ✅ **必带**（Gate 2 评审包必带 OPEN 清单）| S2.10 落地刀（tasking 251+）|
| O6 FastAPI 只读服务 | S1.10 | ✅ 已交 | — | — |
| O7 dbt staging candidate | S1.19 | ✅ 已交 | — | — |
| **继承 4 failed**（全量套件存量）| `577` 回执证据段 + `578` 审计 | **已登记**（docs/53 §5 第 42 项 per `579`；全部先于 577 存在于 HEAD `d95d21e`；**登记 ≠ 修复**，存量既有不新增阻塞）| ✅ Gate 2 评审包照录（本 §5.1）| 后续刀按红线路径裁定修法（spike 样例 provenance 口径 / data/ 白名单房规化）**；已修复 per `581`（三处断言口径修正：fixture provenance 活锚定 / s52 回归双路径 stats pilot 预期 rc=8 SHA 闸零弱化 / data/ 白名单房规化四目录；修后全量 pytest 0 failed；修法走断言口径 ≠ 改 registry/脚本/seed/数据 字节；处置标注不删行）**|

> 刷新（per `484` 可选一句）：上表 O1 行状态语义已随 docs/45 §3 同步刷新——**`WAITING_FILE` 仅保留为 intake 出口码 / mart 真 SHA 未入仓语义，不再写成「等用户投喂才可继续」**；O1 主路径 = docs/52 官方公开源自动获取 B 路（试点轴 `NATIONAL_BULLETIN` per `480`/`482`）；A 路用户投递仍可用但非唯一（`--confirm-o1=PATH` 仅限 A 路出口）；详见 docs/45 §3 O1 表行 + 收口路径 bullet + 文首 queue_rev 231 刷新行。**O1 仍 OPEN——本清单不宣布任何收口**。

### 5.2 O1 详细状态（per `284` §SCHEMA + `299` §SCHEMA + 用户 2026-08-26 裁定）

- **用户 2026-08-26 确认**：本机/仓库**未持有**江苏真实 SHA-locked 样本；无 OCR 后入库的江苏政府文件。
- **演示路径**：继续走 `lib/mart_city_demo.ts` 的 S1.18 DEMO sentinel；`lineage.source_file_sha256` 恒为 `'0'*64` 占位（per docs/47 §3.1 ⚠️）。
- **dbt mart demo-join（per `294`）**：`mart_city_evidence_chain` 60 demo 行 + `mart_city_seven_dim_overview` 70 demo 行；行级 lineage `lineage_is_demo='true'` + `is_demo='true'`；SHA `'0'*64` 占位。
- **真 SHA 投递入口（per `291` intake）**：`docs/48-stage2-real-sha-intake-handbook-20260826.md` + `scripts/intake_real_sha_if_present.py`；当前 runtime allowlist = 4 fixtures（j2.json fixture 文件）→ 全部 `WAITING_FILE` 退出（rc=0）；4 退出状态：`WAITING_FILE` / `CANDIDATE_FOUND` / `O1_INTAKED` / `CONTRACT_VIOLATION`。
- **前端 parity 守门（per `297`）**：`tests/test_frontend_mart_demo_parity_s296.py` 20 pytest cases 锁定 TS demo（4-file 契约 surface）↔ dbt mart 契约对齐。
- **person/tenure demo 接驳（per `303`）**：`frontend/lib/mart_city_demo.ts` 新增 `buildMartRelatedPersons(citySlug)` 工厂（每城 2 demo 行：市委书记 + 市长）；`canonical_name` 全部 demo 占位 `"演示 人物 A (mock, {slug})"` / `"演示 人物 B (mock, {slug})"`（含 "演示" + "mock" 双标识）；`positionTitle` = `"市委书记（演示职位）"` / `"市长（演示职位）"`；`isCurrent=true`（demo 简化）；`lineage.isDemo=true` + `sourceFileSha256='0'*64` 占位。10 城 × 2 = 20 demo 行（`MART_CITY_DEMO_RELATED_PERSONS_TOTAL` 导出常量）。`CityPageMart.tsx` 新增 `<section data-testid="city-page-mart-related-persons">` UI 渲染块 + "演示人物（mock）· 不构成真实身份核验" 显式小字。15 pytest cases（`test_mart_related_persons_demo_s302.py`）守门。**主路径选择 = TS fixture**（dbt 侧 `mart_person_tenure` 依赖 S2.1-lite PASS OPEN per Cursor 174）。
- **预览路径（演示，非 O1 收口）**：用户运行 `NEXT_PUBLIC_USE_MART_FIXTURE=1` 看 demo mart-shape 管道（10 城 × 6 段 × 7 维度 + 10 城 × 2 demo 相关人物行，全部 `is_demo=true`）；**该预览仅是 demo 演示管道，不构成 O1 收口**。
- **不伪造**：禁止假造江苏政府文件 SHA；禁止拿 mock fixture 冒充真实样本；禁止拿 cursor-demo 等替代物冒充（per `284` §SCHEMA "本刀不做" + docs/06 §6.6 红线）。
- **不爬网**：不 HTTP 抓政府站；不调用第三方 API 抓江苏 GDP / 财政 / 履历（per `284` §SCHEMA "本刀不做" + `284` §红线）。
- **Gate 2 评审必带 OPEN**：Gate 2 评审包必须显式携带 O1 OPEN 清单（per docs/34 §3 + §120）；不擅自宣布 O1 收口。
- **收口路径**：O1 真实 SHA 由用户后续提供（线下渠道：政府文件 PDF/扫描件原件）；收口前 demo 恒占位（per docs/47 §6.3 切刀风险 + `284` §SCHEMA）。用户主动 `--confirm-o1=PATH` 显式 flag 才允许 flip O1 状态（per `291` intake + docs/48 §4.3）。

### 5.3 O3 OCR 生产路径详细状态（per `309` + `docs/49` + `313`）

- **规划蓝图已交**（per `docs/49-stage2-o3-ocr-prod-path-plan-20260826.md`，11 节）：7 步流水线设计（upload → validate → sha256 → ocr → text extract → lineage write → ingest）；allowlist 复用 `docs/48` §2（`ALLOWED_UPLOAD_DIR` + `data/seed_archives/`）；`is_demo/SHA lineage` 衔接 `docs/48` §3 4 退出码契约（WAITING_FILE / CANDIDATE_FOUND / O1_INTAKED / CONTRACT_VIOLATION）；`is_demo=false` 翻转 = O3 收口标志事件（lineage JSONB `source_file_sha256` ≠ `'0'*64` + `demo_reason=NULL` + `source_file_url="(OCR_SCAN_FROM_UPLOAD:{user_id}:{uploaded_at})"`）。
- **输入边界显式禁止**：❌ HTTP 爬源（gov.cn / 任何第三方）；❌ 登录绕过（cookie / 账号 / headless browser / Selenium / Playwright）；❌ 未授权 cloud OCR API（默认离线；须 `--enable-cloud-ocr=PROVIDER` 显式 flag + 用户裁定）；❌ symlink/path traversal；❌ 伪造样本（per `docs/48` §4.1 控制流 fixture 判定契约）。
- **OCR 引擎选型待用户裁定**：默认推荐 paddle-ocr（中文精度高 + 本地离线）；tesseract / cloud 备选；最终由用户裁定（per `docs/49` §3.2 步骤 4 + §10 Q1）。
- **O3 仍 OPEN — 未实装**：实装（tasking 31X+）依赖用户裁定 OCR 引擎 + 用户主动 `--confirm-o3=PATH` 提供真实 PDF + 端到端 pytest PASS（per `docs/49` §5.3 + §8 + §10 Q4）。
- **依赖**：S2.1-lite `mart_person_tenure` PASS（干部任免 PDF OCR → person/tenure 表）；S2.2 `policy_observation` schema（政府工作报告 OCR）；S2.4 `fiscal_observation` schema（财政预决算 OCR）— per `docs/49` §6.2 下游消费者。
- **docs/45 §3 O3 + §5.5 + §6 + §6.2 多处显式标注 O3 仍 OPEN**（per `313`）。

### 5.4 不可隐藏清单（Gate 2 评审**必带**）

- ⚠ O1 真实 SHA-locked 江苏样本 **WAITING_FILE**（per docs/34 §3 + §120；WAITING_FILE = intake 出口码 / 真 SHA 未入仓语义，非「等用户投喂」per `490` 对齐）
- ⚠ O3 OCR 生产路径 **规划已交，实装仍 OPEN**（per `docs/49` + `309` + `313`）
- ⚠ docs/10 §3.2-3.4 **xfail stub**（Stage 3 收口）
- ⚠ dbt mart **真表** OPEN（演示级 WHERE FALSE 骨架已交 `288`）
- ⚠ person/tenure **真数据** OPEN（demo 已交 `303`；真数据待 S2.1-lite PASS）
- ⚠ S2.7-b-full **真数据迁移刀** tasking 26X+ OPEN（per docs/47 §6.3 + `284` §依赖）

---

## §6. 评审脚本清单（per docs/10 §3.1-3.5 + docs/44 §4）

### 6.1 pytest 全集（按 docs/45 §4）

| 测试组 | 文件模式 | 当前状态 | Gate 2 要求 |
|---|---|---|---|
| S1.x stage1 回归 | `tests/test_*_s1*.py` | 39/39 PASS | ✅ 必过 |
| S2.x lite 回归 | `tests/test_*_s*lite.py` | 42/42 PASS | ✅ 必过 |
| S2.7-b person/tenure demo（`303`）| `tests/test_mart_related_persons_demo_s302.py` | 15/15 PASS | ✅ 必过 |
| S2.7-b frontend mart demo parity（`297`）| `tests/test_frontend_mart_demo_parity_s296.py` | 20/20 PASS | ✅ 必过 |
| docs/10 §3.1 同类比较匹配依据 | （待 S2.10 落地刀）| ✅ schema + types 已交 | ✅ 必过 |
| docs/10 §3.2 回归模型参数 | xfail stub | ⚠️ Stage 3 收口 | stub 即可（**必带 OPEN 清单**）|
| docs/10 §3.3 缺失值处理 | xfail stub | ⚠️ Stage 3 收口 | stub 即可（**必带 OPEN 清单**）|
| docs/10 §3.4 因果设计假设 | xfail stub | ⚠️ Stage 3 收口 | stub 即可（**必带 OPEN 清单**）|
| docs/10 §3.5 归因措辞 | （待 S2.10 落地刀）| ✅ schema + types 已交 | ✅ 必过 |

### 6.2 dbt 验证

| 模型 | 状态 | Gate 2 要求 |
|---|---|---|
| `mart_city_evidence_chain` | ✅ 骨架已交（`288`，WHERE FALSE）；demo-join 已交（`294`，60 demo 行 + `is_demo='true'`）| ✅ 演示级可过；真表 OPEN |
| `mart_city_seven_dim_overview` | ✅ 骨架已交（`288`）；demo-join 已交（`294`，70 demo 行 + `is_demo='true'`）| ✅ 演示级可过；真表 OPEN |
| `mart_person_tenure` | ⚠️ 依赖 S2.1-lite PASS（OPEN per Cursor 174）| ⚠️ 必带 OPEN 清单 |

### 6.3 smoke-check（per docs/45 §6.2 禁词 3 重守门）

| 检查项 | 状态 | Gate 2 要求 |
|---|---|---|
| §10 mart-shape 禁词扫描（runtime） | ✅ 已守门（每次新文件 CLEAN）| ✅ 必过 |
| file-level forbidden-token guard（静态）| ✅ 已守门（每次新文件 CLEAN）| ✅ 必过 |
| TS 类型约束（mart-shape）| ✅ 已守门（`types_seven_dim.ts` + `mart_city_demo.ts`）| ✅ 必过 |
| 禁词列表（per docs/45 §6.2）| score / rating / rank / total_score / confidence_score / credibility_score / peer_rank / DSH / 实时数据 | ✅ 已守门 |

### 6.4 端到端验证（演示场景）

| 场景 | 路径 | 守门 |
|---|---|---|
| 5 省 lite 页面 | `localhost:3000/provinces/{jiangsu,zhejiang,guangdong,shandong,sichuan}` | ✅ mock 数据 + is_demo 标识 |
| 10 地市 lite 页面 | `localhost:3000/cities/{nanjing,suzhou,wuxi,nantong,hangzhou,ningbo,wenzhou,guangzhou,shenzhen,dongguan}` | ✅ generateStaticParams + dynamicParams=false 兜底 |
| CityPageMart 演示管道 | `NEXT_PUBLIC_USE_MART_FIXTURE=1` | ✅ demo mart-shape + is_demo 标识 |
| EvidenceChain 六段 | lite UI | ✅ mock 数据 |
| SevenDimGrid 七维度 | lite UI | ✅ mock 数据 |
| relatedPersons demo | `<section data-testid="city-page-mart-related-persons">` | ✅ 演示标识 "演示人物（mock）· 不构成真实身份核验" |

---

## §7. 预览路径（演示管道，**非 O1 收口**）

### 7.1 演示启动（per docs/45 §5.5 + `303` + `297` + `294`）

```bash
# 启动本地 dev server
cd frontend
NEXT_PUBLIC_USE_MART_FIXTURE=1 npm run dev

# 访问演示页面（10 地市）
open http://localhost:3000/cities/nanjing
open http://localhost:3000/cities/suzhou
...
open http://localhost:3000/cities/dongguan

# 访问演示页面（5 省）
open http://localhost:3000/provinces/jiangsu
...
open http://localhost:3000/provinces/sichuan
```

### 7.2 演示管道组件

| 组件 | 数据源 | is_demo | 守门 |
|---|---|---|---|
| `CityPageMart` evidence_chain 段 | `lib/mart_city_demo.ts` 的 `MART_CITY_DEMO_EVIDENCE_CHAIN`（60 demo 行）| ✅ `is_demo=true` | ✅ mock 标识显式 |
| `CityPageMart` seven_dim 段 | `lib/mart_city_demo.ts` 的 `MART_CITY_DEMO_SEVEN_DIM_OVERVIEW`（70 demo 行）| ✅ `is_demo=true` | ✅ mock 标识显式 |
| `CityPageMart` related_persons 段 | `lib/mart_city_demo.ts` 的 `buildMartRelatedPersons(citySlug)`（10 城 × 2 demo 行 = 20 行）| ✅ `lineage.isDemo=true` | ✅ "演示人物（mock）· 不构成真实身份核验" 显式小字 |
| `EvidenceChain` 六段 | mock data | ✅ is_demo 标识 | ✅ mock 数据 |
| `SevenDimGrid` 七维度 | mock data + types | ✅ is_demo 标识 | ✅ mock 数据 |

### 7.3 演示路径**不构成 O1 / O3 收口**

- ⚠ **该预览仅是 demo 演示管道**（per docs/45 §5.5 + `284` §SCHEMA）
- ⚠ **不构成 O1 收口**：`lineage.source_file_sha256` 恒为 `'0'*64` 占位（per docs/47 §3.1 ⚠️）
- ⚠ **不构成 O3 收口**：OCR 引擎未实装（per `docs/49` §0 + §8 不在范围）
- ⚠ **不构成 Gate 2 PASS**（per docs/34 §1 + §8 #8 + `315` §红线）

---

## §8. 红线自检（per docs/34 §1 + §8 + `315` §红线 + docs/49 §0/§7 + docs/06 §6.6 + docs/42 §8 + docs/45 §6.2）

| 红线 | 状态 | 守门位置 |
|---|---|---|
| ❌ 不宣布 Gate 1 / Gate 2 PASS | ✅ | docs/50 header + §0 + §10 多次显式守门 |
| ❌ 不擅自 O1 收口 | ✅ | §3.3 + §5.1 + §5.2 + §5.4 多处显式 OPEN（WAITING_FILE）|
| ❌ 不擅自 O3 收口 | ✅ | §3.3 + §5.1 + §5.3 + §5.4 多处显式 OPEN（规划已交，实装仍 OPEN）|
| ❌ 不宣布 docs/10 §3.2-3.4 PASS | ✅ | §3.3 + §5.1 + §5.4 + §6.1 显式 xfail stub + Stage 3 收口 |
| ❌ 不派生 score / rating / rank / total_score / confidence_score / credibility_score / peer_rank | ✅ | §2 #4 + §3.1 + §6.3 + docs/45 §6.2 禁词 3 重守门 |
| ❌ 不做官员能力总分 / 排名 / DSH / 实时数据 | ✅ | §0.2 + §0.3 + §8 显式守门；docs/45 §6.2 沿用 |
| ❌ 不批量爬政策研究 / 财政预决算 / 官员履历 | ✅ | §0.3 + §8 + docs/34 §1 沿用 |
| ❌ HTTP 爬源 | ✅ | §5.3 显式禁止；本包不引入新 HTTP |
| ❌ 登录绕过 | ✅ | §5.3 显式禁止；本包不引入 |
| ❌ 未授权 cloud OCR API | ✅ | §5.3 显式禁止；本包不引入 |
| ❌ 降 OCR 门槛 | ✅ | §5.3 + docs/49 §2.2 守门 |
| ❌ 启用 pgvector / RLS / partition | ✅ | Stage 2 边界；本包不动 |
| ❌ 改 `gate_thresholds.json` | ✅ | 未读未写 |
| ❌ 不碰 `00-CC-CURRENT.md` | ✅ | Cursor 拥有 |
| ❌ 不擅自 `--force` / `--force-with-lease` | ✅ | ff-only pull |
| ❌ 不替用户下裁定 | ✅ | §0.2 + §5.2 + §5.3 显式 OPEN 携带 |
| ❌ 不在聊天复述 Cursor 长文 | ✅ | 仅评审包要点 |
| ❌ 不索要 PAT | ✅ | — |
| ✅ docs/50 = CC 维护评审包草稿 | ✅ | CC 拥有（per `315` §SCHEMA "本刀做"）|
| ✅ docs/45 §2 七条 ↔ docs/50 §2 七条**1:1**对齐 | ✅ | 本包直接复用 docs/45 §2 措辞 + 加证据路径详情 |
| ✅ 七条验收全部挂证据路径 | ✅ | §2 表 7 行（链到已交回执 / 页面 / 测试 / dbt 验证）|
| ✅ OPEN 清单**必带** | ✅ | §3.3 + §5.1 + §5.2 + §5.3 + §5.4 多处显式 |
| ✅ 演示级 vs 不可降级 vs 仍 OPEN 三类划分 | ✅ | §3.1 + §3.2 + §3.3 |
| ✅ 演示场景（5 省 + 10 地市）| ✅ | §4.1 5 省 + 10 地市路径齐全 |
| ✅ EvidenceChain 六段 + 七维度 七卡 | ✅ | §4.2 + §4.3 |
| ✅ 预览 URL + 演示管道 | ✅ | §7.1 + §7.2 + §7.3 |
| ✅ **不构成 Gate 2 PASS** | ✅ | §0 + §7.3 + §10 多次显式守门 |
| ✅ docs/50 文首/文末**禁止 PASS 措辞** | ✅ | header + §0 + §10 多次 ⚠ 显式 |
| ✅ docs/50 = markdown-only（无业务代码改动）| ✅ | §0.2 显式 "不创业务代码" |
| ✅ Cursor 拥有架构文档未动 | ✅ | docs/06/08/10/34/40-44/46-49 / `00-CC-CURRENT.md` 未读未写 |

---

## §9. 不可隐藏清单（Gate 2 评审必带，per docs/34 §3 + §120）

> ⚠ **以下事项必须在 Gate 2 评审会上显式呈现，不得以任何方式省略、隐藏或改写**：

1. ⚠ **O1 真实 SHA-locked 江苏样本 WAITING_FILE** — `lineage.source_file_sha256` 恒为 `'0'*64` 占位；演示管道全部走 demo sentinel；不擅自宣布 O1 收口；WAITING_FILE = intake 出口码 / mart 真 SHA 未入仓技术状态语义（per `490` 对齐）
2. ⚠ **O3 OCR 生产路径规划已交（`docs/49` + `309`），实装仍 OPEN** — 7 步流水线已规划，OCR 引擎未实装；tasking 31X+ 待用户裁定 + `--confirm-o3=PATH` + 端到端 pytest PASS
3. ⚠ **docs/10 §3.2-3.4 xfail stub** — Stage 3 收口；Gate 2 评审**必带 OPEN 清单**
4. ⚠ **dbt mart 真表 OPEN** — 演示级 WHERE FALSE 骨架已交（`288`）；demo-join 已交（`294`）；真数据待 S2.7-b-full 真数据迁移刀（tasking 26X+）
5. ⚠ **person/tenure 真数据 OPEN** — demo 已交（`303`，10 城 × 2 demo 行）；真数据待 S2.1-lite PASS（OPEN per Cursor 174）
6. ⚠ **mart-shape feature-flag 默认 mock** — `NEXT_PUBLIC_USE_MART_FIXTURE !== "1"` 默认走 mock；用户需显式开启 `=1` 才看 demo mart-shape 管道
7. ⚠ **cloud OCR 默认离线** — 须 `--enable-cloud-ocr=PROVIDER` 显式 flag 才允许；默认 paddle-ocr 离线推荐（per `docs/49` §3.2 步骤 4）
8. ⚠ **预览路径不构成 O1 / O3 收口** — demo 演示管道仅用于 Gate 2 评审展示；不构成 O1 真实 SHA 收口 + 不构成 O3 OCR 收口

---

## §10. 备注 / 不在范围 / 下次心跳预期

### 10.1 备注

- **本包是 Gate 2 评审包草稿**（per `315` §SCHEMA "本刀做"），不是 Gate 2 PASS 宣告
- **本包**禁止 PASS 措辞**（per `315` §SCHEMA 文首/文末）
- **本包**不创业务代码**（per `315` §SCHEMA "本刀不做"）— 仅 markdown 文档 + 回执 + bump + commit + push
- **docs/50 = CC 维护评审包草稿**（per `315` §SCHEMA），不属于 Cursor 拥有架构文档（docs/06/08/10/34/40-44/46-49 / `00-CC-CURRENT.md`）
- **Gate 2 评审日期暂定 W8**（per docs/34 §10.4），由 Cursor/用户裁定，不擅自提前
- **O1 真实 SHA 收口前恒占位 `'0'*64`**（per docs/47 §3.1 ⚠️ + `315` §红线 + docs/45 §3 O1）
- **O3 真收口须用户主动 `--confirm-o3=PATH` + OCR 引擎选型裁定 + 端到端 pytest PASS**（per `docs/49` §5.3 + §8 + §10 + docs/48 §3）
- **cloud OCR 默认离线**（per `docs/49` §2.2 + §3.2 步骤 4）
- **输入边界 = 仅用户/admin upload；禁止 HTTP 爬源 / 登录绕过 / 未授权 API / symlink / 伪造**（per `docs/49` §2.2）

### 10.2 不在范围（per `315` §SCHEMA "本刀不做" + docs/49 §8）

- ❌ Gate 1 / Gate 2 PASS 宣告
- ❌ O1 / O3 收口
- ❌ 业务代码改动（schema / migration / dbt / pytest / TS / frontend / smoke-check）
- ❌ Cursor 拥有架构文档（docs/06/08/10/34/40-44/46-49）— 不读不改
- ❌ `00-CC-CURRENT.md` — Cursor 拥有
- ❌ `gate_thresholds.json` — 红线条目
- ❌ OCR 引擎实装（paddle-ocr / tesseract / cloud 选型待用户裁定）
- ❌ 真实 PDF 投递（须用户主动 `--confirm-o3=PATH` + `--confirm-o1=PATH`）

### 10.3 下次心跳预期

- `queue_rev 131` 完成后：Cursor 收 `316` → 下发 `317-stage0-cursor-s315-docs50-gate2-packet-audit-…md`（PASS/FAIL）
- 若 PASS：Gate 2 评审包草稿齐；Gate 2 评审会议筹备就绪（必带 OPEN 清单）
- 若 FAIL：`316-correction` 回合（修 §2 七条措辞 / 修 OPEN 清单 / 修预览路径 / re-commit）

---

— End of `docs/50` —

> ⚠ **本包是 Gate 2 评审包草稿**（per `315` §SCHEMA "本刀做"），不是 Gate 2 PASS 宣告。
> ⚠ **本包不宣布 Gate 1 / Gate 2 PASS**（per docs/34 §1 + §8 #8 + §133 + `315` §红线）。
> ⚠ **本包不宣布 O1 收口**（WAITING_FILE = intake 出口码 / 真 SHA 未入仓技术状态语义，非「等用户投喂」，per `484`/`486`/`488`/`490` 对齐；per docs/47 §3.1 ⚠️ + `284` §SCHEMA + `315` §红线）。
> ⚠ **本包不宣布 O3 收口**（规划已交，实装仍 OPEN；per `docs/49` §5.3 + §8 + §10 + `309` + `315` §红线）。
> ⚠ **本包不伪造证据**（per docs/06 §6.6 + `315` §红线）。
> ⚠ **本包不爬源站 / 不登录绕过 / 不 OCR 降门槛**（per PRD 红线 + `315` §红线 + docs/49 §2.2）。
> ⚠ **本包不派生 score / rating / rank / total_score / confidence_score / credibility_score / peer_rank**（per docs/45 §6.2 禁词 3 重守门）。
> ⚠ **O1 真实 SHA 收口前恒占位 `'0'*64`**（per docs/47 §3.1 ⚠️ + `315` §红线）。
> ⚠ **O3 真收口须用户主动 `--confirm-o3=PATH` + OCR 引擎选型裁定 + 端到端 pytest PASS**（per `docs/49` §5.3 + §8 + §10 + docs/48 §3）。
> ⚠ **cloud OCR 默认离线；须 `--enable-cloud-ocr=PROVIDER` 显式 flag**（per `docs/49` §2.2 + §3.2 步骤 4）。
> ⚠ **输入边界 = 仅用户/admin upload；禁止 HTTP 爬源 / 登录绕过 / 未授权 API / symlink / 伪造**（per `docs/49` §2.2）。
> ⚠ **docs/10 §3.2-3.4 xfail stub（Stage 3 收口）；Gate 2 评审必带 OPEN 清单**。
> ⚠ **Gate 2 评审日期暂定 W8**（per docs/34 §10.4），由 Cursor/用户裁定，**不擅自提前**。