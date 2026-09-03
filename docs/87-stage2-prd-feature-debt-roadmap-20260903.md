# 87 — Stage 2 PRD §7 产品功能差距重排路线图（2026-09-03, knife 661 任务书 §1.661 首交付件）

> **依据**: `china-economy-governance-research-platform-prd-v0.1.md` §7.1-§7.7 七大产品功能; `docs/54-milestone-replan-20260830.md` §5 M0-M6 24 里程碑; 660 receipt (`reviews/.../660-stage0-cc-track-b-static-export-receipt-20260902.md`) — 用户质询「660 刀下来才一个 28 省表格, 与 PRD 初衷差十万八千里」; 661 tasking (`660-audit-661-tasking-consolidated-20260903.md` PART 2); `user_ruling_661: P1 先行` (rev108 §CURRENT, 2026-09-03 用户裁定).
> **地位**: PRD §7 产品差距对照 + 三期路线提案; **优先级由用户裁定, 执行端不得自行开 P3 深水区刀**.
> **不宣布 Gate / O1 / M2 / M4 / M5 / M6 PASS**; M0-M6 全部沿用 docs/54 §5 OPEN 表述.
> HEAD 快照: `93bc4f3` (661 user_ruling) → 661 commit 链尾 (本刀).

---

## 0. 为什么要重排

660 闭环后, 生产站虽然显示了 28 省真数据, 但用户视觉上**只看见一张 GDP 表** (28 行 × 5 列 + 3 数据暂缺 badge). PRD §7 定义七大产品功能 (全国总览/地区画像 15 项/地区比较/历史脉络/监测预警/官员政策项目页/研究工作台), 当前生产 = **1 个指标 × 1 年 × 省级 × 1 张表**.

**用户质询 (2026-09-03)**:
> 「660 刀下来才一个 28 省表格, 与 PRD 设计初衷相差十万八千里?」

**直答 (per 661 tasking PART 2 §0)**:
属实. PRD §7 七大产品功能当前交付 **0 个** (除 660 Track B 静态导出=仅 §7.2 地区画像的一个指标子集). 三层原因:

1. **659+ 刀几乎全部花在 PRD §3 证据规则 (血缘/不可变/红线) 的治理地基** —— 必要但零产品产出 (rev105-108 共 4 轮红线补齐).
2. **MVP 被越切越窄** (`docs/54` 首期定义「国家-31 省-试点城市闭环」, 实际只做省级 GDP 角落; 国家锚在库未上页, M3 城市 U6 放宽, O1 时序仍 OPEN).
3. **呈现层从未规划** (660 前无部署管线; 公网 demo 仅 mock).

**修正路径 = 本刀**: PRD §7 逐项 × 现状 × 数据就绪度 × 依赖 × 刀次路线, 重排主计划, **交用户裁定优先级**.

---

## 1. PRD §7 七大产品功能差距对照

> 表头约定: **现状** 列只标 live / demo 壳 / 无; **数据就绪度** 列按 (全在库 / 部分在库 / 需新数据刀 / 需 PRD 深水区模型) 四档; **依赖** 列按 (前端 only / 需新数据刀 / 需 PRD 深水区 / 需部署管线) 四档; **建议刀次** 列按 (661+ / 662-665 / 666-680 / 681+) 四档. P1/P2/P3 裁定权属用户.

### §7.1 全国总览

| 子项 | 现状 | 数据就绪度 | 依赖 | 建议刀次 |
|---|---|---|---|---|
| 加入 WTO 以来的关键经济阶段时间线 | demo (timeline 元素未上页) | 无 | 需 PRD §5.4 时序模型 + 新数据刀 | P3 681+ |
| 年度/季度/月度主要指标 | demo (仅 1 指标 × 1 年) | 部分 (115 obs × 5 维度, 全部 2024 年) | 需时序回填 (2001 起) | P2 666-680 |
| 产业/需求/财政/金融/人口/外贸结构 | 无 | 部分 (3 次产业在库; 5 其余缺) | 需新数据刀 (NBS + 部委) | P2 666-680 |
| 增长动力/约束/风险清单 | demo (七维壳) | 部分 (mock 七维) | 需 PRD §6 治理效能观察模型 | P3 681+ |
| 中央政策/财政/货币政策时间线 | demo (timeline 元素) | 部分 (policy_document 在库) | 需 PRD §5.4 政策承诺模型 | P3 681+ |
| 图表来源/口径/版本/修订 | ** 660 Track B 静态导出已上** (lineage_source + lineage_ruling) | live | 661 加 source_url + source_hash_prefix (UI 强化) | P1 661 |
| **§7.1 现状小结** | **6 子项: 1 live / 4 demo / 1 部分 live** | | | |

### §7.2 地区画像 (per PRD §7.2 「每个地区至少 8 维度」)

| 子项 | 现状 | 数据就绪度 | 依赖 | 建议刀次 |
|---|---|---|---|---|
| 基础禀赋 | demo (5 详情页 mock) | 部分 (5 详情页有 mock 六段链) | 661 flip 5 静态 → 31 动态 + 真数据 | P1 661 |
| 历史发展路径 | demo | 无 | 需时序数据 (2001 起) | P2 666-680 |
| 当前经济运行 | **660 Track B 已上** (28 省 5 列 GDP) | live (1 指标) | 661 加国家锚 + 5 指标 tab + 溯源 | P1 661 |
| 产业结构与产业链 | partial (3 次产业在库) | 部分 | 661 flip 五维度 tab | P1 661 |
| 人口与人才 | 无 | 无 | 需新数据刀 (统计年鉴) | P3 681+ |
| 财政与债务 | 无 | 无 | 需新数据刀 (财政部) | P3 681+ |
| 资源与环境 | 无 | 无 | 需新数据刀 (生态环境部) | P3 681+ |
| 15 项子能力 (per PRD §7.2) | demo (六段链壳) | 部分 | 需 PRD §5 模型扩展 | P2 666-680 |
| **§7.2 现状小结** | **8 子项: 1 live / 4 demo / 3 无** (5 详情页 mock 已 flip = 1 live in 661) | | | |

### §7.3 地区比较

| 子项 | 现状 | 数据就绪度 | 依赖 | 建议刀次 |
|---|---|---|---|---|
| 任意选择多个地区和时间范围 | demo (peer-compare mock) | 部分 (4 省数据在库) | 661 flip peer-compare mock → 真数据 | P1 661 |
| 名义值/实际增速/人均值/占比/指数化序列 | demo | 部分 (5 指标在库, 无指数化) | 需新指标刀 + 索引逻辑 | P2 666-680 |
| 同类地区自动建议 + 选择依据 | demo (mock) | 部分 (mock 4 维度匹配) | 需 PRD §6.4 同类地区模型 | P3 681+ |
| 不可比指标警告 | 无 | 无 | 需 PRD §5.3 比较组定义 | P3 681+ |
| 生成图表/表格/摘要/咨询报告草稿 | 无 | 无 | 需 PRD §7.7 研究工作台 | P3 681+ |
| **§7.3 现状小结** | **5 子项: 1 demo (661 flip 后 live) / 2 部分 / 2 无** | | | |

### §7.4 历史脉络

| 子项 | 现状 | 数据就绪度 | 依赖 | 建议刀次 |
|---|---|---|---|---|
| 经济指标共用时间轴 | demo (timeline 元素) | 部分 (1 指标 × 1 年) | 需时序回填 (2001 起) | P2 666-680 |
| 行政区划共用时间轴 | 无 | 部分 (geo_entity 在库) | 需时序数据 | P3 681+ |
| 官员任期共用时间轴 | 无 | 部分 (mart_person_tenure demo) | 需 PRD §5.3 任期模型 + 真数据 | P3 681+ |
| 政策/项目共用时间轴 | 无 | 部分 (policy_document 在库) | 需 PRD §5.4 政策承诺模型 | P3 681+ |
| 外部冲击共用时间轴 | 无 | 无 | 需新数据刀 | P3 681+ |
| 按主题筛选事件 | 无 | 无 | 需前端 + 标签体系 | P3 681+ |
| 任一结论回到原始数据和文件 | **660 Track B 已上** (lineage_source) | live | 661 加 source_url + UI 强化 | P1 661 |
| **§7.4 现状小结** | **7 子项: 1 live / 1 demo / 3 部分 / 2 无** | | | |

### §7.5 当前监测与预警

| 子项 | 现状 | 数据就绪度 | 依赖 | 建议刀次 |
|---|---|---|---|---|
| 根据官方发布时间表检查新数据 | 无 | 部分 (registry enabled 在库) | 需 Prefect/cron (L3 调度) | P2 666-680 |
| 识别最新数据/修订数据/缺失发布 | 无 | 部分 (missing_reason 在库) | 需前端 UI | P2 666-680 |
| 监测增速拐点/异常偏离/财政压力/房地产变化/人口变化/政策信号 | demo (七维壳) | 无 | 需 PRD §6 治理效能观察 + 新数据刀 | P3 681+ |
| 预警必须显示规则/比较基线/证据 | 无 | 部分 (lineage 在库) | 需 PRD §6.5 预警规则 | P3 681+ |
| **§7.5 现状小结** | **4 子项: 1 demo / 3 部分 / 0 live** | | | |

### §7.6 官员/政策/项目页面

| 子项 | 现状 | 数据就绪度 | 依赖 | 建议刀次 |
|---|---|---|---|---|
| 官员公开履历和任期时间线 | demo (mart_person_tenure, 5×6 cross-product, is_demo=true) | 部分 (demo 数据) | 需 PRD §5.3 任期模型 + 真数据 | P3 681+ |
| 任期内政策/预算/项目/经济社会指标 | demo (六段链壳) | 部分 (六段链 mock) | 需 PRD §5.3 任期 + §5.4 政策 | P3 681+ |
| 政府工作报告目标抽取与兑现跟踪 | 无 | 部分 (policy_document 在库) | 需新数据刀 (全文 OCR) | P3 681+ |
| 项目从宣布到交付的状态迁移 | demo (project_event 五态机) | 部分 (schema 在库) | 需新数据刀 | P3 681+ |
| 政策文件主题/工具/对象/期限/上级关联 | demo | 部分 (policy_document 在库) | 需新数据刀 | P3 681+ |
| **§7.6 现状小结** | **5 子项: 5 demo (0 live)** | | | |

### §7.7 研究工作台

| 子项 | 现状 | 数据就绪度 | 依赖 | 建议刀次 |
|---|---|---|---|---|
| 自然语言提问和结构化筛选 | 无 | 无 | 需 L6 只读 Agent + pgvector | P3 681+ |
| 查询数据序列/政策原文/任期/项目 | 部分 (sequence 在库, 原文缺) | 部分 | 需 PRD §5 模型 + Agent | P3 681+ |
| 保存研究问题/筛选条件/图表/笔记 | demo (`/research/q1-2024-gdp` 页面) | 部分 | 需前端 + DB | P2 666-680 |
| 生成带引文的报告草稿 | 无 | 无 | 需 Agent + 报告模板 | P3 681+ |
| 导出 CSV/Markdown/图片/Word/PDF | demo (`/public-extracts` 四轨) | 部分 | 需前端 + 导出工具 | P2 666-680 |
| **§7.7 现状小结** | **5 子项: 2 demo / 2 部分 / 1 无** | | | |

### §7 总览 (按子项统计)

| 段 | 子项总数 | live | demo | 部分 | 无 |
|---|---:|---:|---:|---:|---:|
| §7.1 全国总览 | 6 | 1 (660) | 0 | 4 | 1 |
| §7.2 地区画像 | 8 | 1 (660) | 0 | 4 | 3 |
| §7.3 地区比较 | 5 | 0 | 1 | 2 | 2 |
| §7.4 历史脉络 | 7 | 1 (660) | 0 | 3 | 3 |
| §7.5 当前监测 | 4 | 0 | 1 | 3 | 0 |
| §7.6 官员政策项目 | 5 | 0 | 5 | 0 | 0 |
| §7.7 研究工作台 | 5 | 0 | 2 | 2 | 1 |
| **合计 7 段 40 子项** | **40** | **3 (7.5%)** | **9 (22.5%)** | **18 (45%)** | **10 (25%)** |

**注**: 「live」严格按公网静态导出或 FastAPI 路由可访问且带真实血缘;「demo」= 有 UI 壳但数据为 mock / is_demo=true;「部分」= 数据在 DB 但未上页或部分上页;「无」= 库空.

---

## 2. 已在库未上页盘点 (per 661 tasking §1.661 §1)

| 项 | 数量 | 位置 | 661 处理 |
|---|---:|---|---|
| observation 行 | 115 | `dbt/models/staging/stg_observation.sql` (全部 2024, FACT value_type) | 661 flip 首页 5 指标 tab |
| 国家锚行 (NBS 2024 GDP) | 1 (库未上页) | 待 export-mart-data.py 扩展 | 661 加 NATIONAL 锚行 |
| 五维度指标 | 5 (gdp_total/gdp_growth/primary_gdp/secondary_gdp/tertiary_gdp) | mart_province_gdp_2024.sql | 661 flip 首页 tab 切换 |
| 血缘字段 | source_url/source_hash_prefix/lineage_source/lineage_origin/lineage_ruling | 库 in source_document/observation.lineage | 661 加 2 字段 + 溯源 popover |
| 5 静态详情页 (mock) | 5 (guangdong/jiangsu/shandong/sichuan/zhejiang) | `frontend/app/provinces/[5]/page.tsx` | 661 flip → 31 动态路由 |
| 4 维 mock 比较 | 1 (江苏+浙江+广东+山东) | `frontend/lib/mock_peer_compare.ts` | 661 flip 真数据 |
| 七维/六段链 demo 壳 | 2 | `frontend/lib/mock_seven_dim.ts` + `mock_evidence_chain.ts` | 661 不动 (留 662-680) |
| mart_person_tenure (demo 5×6) | 30 行 is_demo=true | `dbt/models/marts/mart_person_tenure.sql` | 661 不动 (P3 深水区) |

---

## 3. 三期路线提案 (用户裁定)

### §3.1 P1 先行 — 库中已有数据全部露出 (user_ruling_661 locked)

**范围**: 首页 5 指标 tab + 国家锚行 + 溯源 popover + 31 省详情动态路由真数据化 + peer-compare 真数据化.

**数据源**: 全部已在库 / mart (`mart_province_gdp_2024.sql` 28 真 + 3 缺失 + NBS 2024 国家锚).

**依赖**: 前端 only + 静态导出扩展 (B1 export-mart-data.py +3 字段) + 部署管线 (沿用 660 deploy.sh).

**刀次**: **661** (本刀完整切, 不拆 662-663).

**交付价值**: 用户视觉上从「1 个 28 省表格」升级到「全国总览 + 31 省详情 + 地区比较 三大产品页, 全部真数据」= **PRD §7.1 + §7.2 + §7.3 三段从 1 live/1 demo 升级到 3 live** (live 占比从 7.5% 升到 ~15%).

**不涉及**: 时序回填 / 新指标数据刀 / 人物政策项目 / 治理效能观察 / Agent 工作台 — 全部归 P2/P3.

### §3.2 P2 数据扩展 (用户待裁定)

**范围**: 时序回填 2001 起 GDP (per 636 feasibility probe, REACHABLE 0 / PARTIAL 770 / BLOCKED 771 — 需用户提供政府源镜像 / 商业年鉴库授权 per U4 重审) + 多指标扩展 (人口/财政/消费/投资/外贸 5 类) + M3 试点城市 U6 重启条件触发 + 研究工作台导出增强.

**数据源**: 多源 (NBS + 31 省 tjj + 商业年鉴库) — 需用户授权 U4 重审.

**依赖**: 新数据刀 + L3 调度 (Prefect) + L4 pgvector (per docs/02 §8) + 部分 PRD 深水区.

**刀次**: 666-680 估算 (~14 刀, 12 周).

**交付价值**: §7.1/§7.2/§7.3/§7.4/§7.5/§7.7 部分子项从 demo/部分 升级到 live; **不涉及** §7.6 官员政策项目 (P3).

### §3.3 P3 深水区 (用户待裁定, **执行端禁开**)

**范围**: PRD §5.3 人物任期 + §5.4 政策承诺 + §6 治理效能观察 + §7.6 官员政策项目 + §7.7 Agent 工作台 + §7.5 预警规则.

**数据源**: 政府工作报告全文 OCR (per 583 O3-impl) + 任免公告 + 政策文件全文 + pgvector 向量化.

**依赖**: PRD §5/§6 模型深水区 (per docs/00-project-assessment.md 红线 5 「不以抓取网页数作为完成标准」) + L4 pgvector + L6 Agent + 9-18 个月级.

**刀次**: 681+ 估算 (~24-36 刀, 6-12 个月).

**交付价值**: PRD §7 七段全量 (40 子项从 7.5% live 提升到 50%+ live).

---

## 4. P1 优先级由用户裁定 (locked)

> Per 661 tasking §1.661-D 红线: **docs/87 路线为提案, 优先级由用户裁定, 执行端不得自行开 P3 深水区刀**.

**user_ruling_661 已签发** (2026-09-03, rev108 §CURRENT):
> **`user_ruling_661: P1 先行`** — 库中已有数据全部露出 (多指标 + 31 省详情 + 溯源 + 比较), 最快见效; P2/P3 在 P1 之后; docs/87 PRD 对齐路线图; 660 这把刀本身没失败; 七大产品功能交付了 0 个; 用户完全看不见.

P2/P3 路线**待用户另行裁定**,**;** 执行端**不得自行开刀**进入 P2/P3. 任何 P2/P3 刀次**必须先有 user_ruling_6XX** 才能开始.

---

## 5. 661 任务书对应 (本刀)

Per 661 tasking `660-audit-661-tasking-consolidated-20260903.md` PART 2 §1.661:

1. **docs/87 本件** (架构师级 PRD 对齐重排) — **本件完成 ✓**
2. **首个产品化切片 (P1 之一)** — 661 同刀落地:
   - 首页表**多指标切换** (5 指标 tab/下拉)
   - **国家锚行** (全国 2024 GDP 锚值置顶, 标 OFFICIAL_ANCHOR)
   - 每行**溯源链接** (点开显示 source_url + source_hash_prefix + lineage_ruling)
   - 31 省详情动态路由真数据化 (5 静态 → 32 slug 动态)
   - peer-compare 真数据化 (mock → 真)

> 注: 661 tasking §1.661 「首个产品化切片」 = 本 docs/87 §3.1 P1 先行 的**完整一刀切** (用户「P1 范围」裁定 = 首页 + 31 省详情 + 比较页), 不拆 662/663. 后续 P1 增强 (e.g. 时序 tab, 31 省 × 5 指标组合视图) 归 662+ 范畴.

---

## 6. 执行端禁开 (深水区红线)

> Per 661 tasking §1.661-D 第 8 条: **docs/87 路线为提案, 优先级由用户裁定, 执行端不得自行开 P3 深水区刀**.

执行端在本刀及后续任何刀中, **不得自行**:
- 启动 P2 数据扩展刀 (时序回填 / 多指标新数据刀 / 商业年鉴库授权 / M3 城市重启)
- 启动 P3 深水区刀 (PRD §5.3 任期 / §5.4 政策 / §6 治理效能 / §7.6 官员政策项目 / §7.7 Agent)
- 越过用户裁定擅自决定 P1/P2/P3 优先级

任何 P2/P3 刀必须:
1. 先有 `user_ruling_6XX` 单独签署 (rev 6XX §CURRENT 登记)
2. 在 00-EXEC-QUEUE.md §META cc_head 加入新 commit 链
3. 红线 14 「不宣称 PASS」沿用, **不宣布 Gate / O1 / M2 / M4 / M5 / M6 PASS**

---

## 7. 链接

- 关联 661 tasking: `reviews/stage0-gate0-rework-2026-08-23/660-audit-661-tasking-consolidated-20260903.md` PART 2
- 关联 660 receipt: `reviews/stage0-gate0-rework-2026-08-23/660-stage0-cc-track-b-static-export-receipt-20260902.md`
- 关联 runbook: `docs/85-stage2-public-deploy-mart-flip-runbook-20260902.md`
- 关联 24 里程碑基线: `docs/54-milestone-replan-20260830.md` §5 M0-M6
- 关联 PRD 全文: `docs/china-economy-governance-research-platform-prd-v0.1.md` §7
- 关联 U4 数据源重审: `docs/55-m1-first-series-task-breakdown-20260831.md` / `docs/57-m3-launch-conditions-review-20260901.md`
- 关联 memory: [[china-platform-661-p1-ruling]] [[china-platform-exec-mechanism]] [[china-platform-user-rest-protocol]]
- 关联 00-EXEC-QUEUE: `reviews/stage0-gate0-rework-2026-08-23/00-EXEC-QUEUE.md` (rev108 → 661 commit 链尾 rev109)

— End docs/87 (PRD §7 七大产品功能差距对照 + 三期路线提案, 2026-09-03) —