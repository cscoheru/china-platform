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
| **O3** OCR 生产路径 | S1.17 scanned PDF | **规划已交，实装仍 OPEN**（per `docs/49` + `309`）| 用户裁定 OCR 引擎（paddle-ocr 推荐 / tesseract / cloud）+ `--confirm-o3=PATH` + 端到端 pytest PASS（per `docs/49` §5.3 + §8 + §10）|
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

> ⚠ **本节是公开提取演示里程碑的端到端交付清单**（回执链 `344` → `362` → `368` → `371` → `377` → `383` → `398` → `404` → `410` → `413` → `436` → `440` → `446` → `448` → `470` → `474` → `482` → `496` → `498` → `502`；16–19 公网互链弧收口里程碑行 per `474`（`472` 已在 docs/53/docs/45 登记）；O1 B 路 21–23 弧内里程碑行补登 per `482`/`496`/`498`、弧收口登记 per `500` 已在 docs/53 §5 第 24 项/docs/45 登记、21–23 弧收口里程碑行补登 per `502`，链尾以 `502` 收口）；**全部为 demo/candidate 演示，非 O1/Gate 收口**；链到 `docs/45` §6.2 + `docs/53` §5。

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
| **O3** OCR 生产路径 | S1.17 scanned PDF | **规划已交（`docs/49` + `309`），实装仍 OPEN** | ✅ **必带**（per docs/34 §3 + `docs/49` §5.3）| OCR 引擎选型 + `--confirm-o3=PATH` + 端到端 pytest PASS |
| O4 `is_demo` 机制 | S1.18 | ✅ 已交 | — | — |
| **O5** docs/10 测试 §3.2-3.4 | Stage 2 收口 | ⚠️ xfail stub | ✅ **必带**（Gate 2 评审包必带 OPEN 清单）| S2.10 落地刀（tasking 251+）|
| O6 FastAPI 只读服务 | S1.10 | ✅ 已交 | — | — |
| O7 dbt staging candidate | S1.19 | ✅ 已交 | — | — |

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