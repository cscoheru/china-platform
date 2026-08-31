# 08 — MVP 计划与里程碑（Roadmap & MVP Plan）

> Stage 0 交付物 #08；对应 PRD 第 15 章第 8 项 + 第 16 章。
> 5 个 Stage × Gate 评审，把"研究问题"前置（per R05 防范围失控）。

## 1. 时间总览

| Stage | 主题 | 周数 | Gate 评审 |
|---|---|---|---|
| **Stage 1** | 数据底座 | 4-6 周 | Gate 1: 首批数据可查询、可回溯 |
| **Stage 2** | 治理观察页面 | 6-8 周 | Gate 2: 首批 5 个省/10 个地市页面可演示 |
| **Stage 3** | 比较分析与同类地区 | 4-6 周 | Gate 3: 首批 3 个研究问题闭环 |
| **Stage 4** | 研究 Agent 评估 | 4-6 周 | Gate 4: DSH 决策落地（按 doc 07） |
| **Stage 5** | 优化与运维 | 4-6 周 | Gate 5: 公测上线 |
| **合计** | – | 22-32 周（约 5-7 月） |

**注**：不含前置准备（团队组建、基础设施）；PRD 16.1 给的是"自项目启动起"。

## 2. Stage 1 — 数据底座（4-6 周）

### 2.1 任务清单

| 任务 | 周 | 依赖 | 验收 |
|---|---|---|---|
| **S1.1** 部署 PostgreSQL 16 + PostGIS | W1 | – | 数据库可连接；schema 01-core.sql 跑通 |
| **S1.2** 建立 schema/migrations 目录，写 Alembic 初始化 | W1 | S1.1 | migration 001_create_core 可执行可回滚 |
| **S1.3** 实施 source_registry + source_document 表 + URL 健康监控 | W1-W2 | S1.1 | 首批 5 个来源登记（含 spike 验证过的 4 个） |
| **S1.4** 实现 NBS-MONTHLY 连接器（基于 Spike 1） | W2-W3 | S1.1, S1.3 | 2020-2025 月度数据入库；通过 doc 10 测试 2.1-2.6 |
| **S1.5** 实现 SHENZHEN-BULLETIN 连接器（基于 Spike 3） | W2-W3 | S1.1 | 2020-2024 年公报入库；通过 doc 10 测试 2.1-2.5 |
| **S1.6** 实现省级年鉴连接器（基于 Spike 2） | W3-W4 | S1.1 | 3 省 × 5 年入库；通过 schema 差异测试 |
| **S1.7** 实现扫描 PDF OCR 连接器（基于 Spike 4） | W3-W4 | S1.1 | 历史扫描 PDF 抽样入库；OCR confidence 测试通过 |
| **S1.8** 实施 ingest_run 监控 + 失败告警 | W4 | S1.4-1.7 | Grafana dashboard 上线；失败率告警 |
| **S1.9** dbt 模型层（基础清洁度） | W4-W5 | S1.4-1.7 | dbt test 全过；5 张 staging view |
| **S1.10** FastAPI 基础服务（仅查询接口） | W5 | S1.9 | `/api/indicator/{id}/series` 可调用 |
| **S1.11** 数据契约文档（great_expections） | W5-W6 | S1.9 | 5 个核心数据集 contract |
| **S1.12** Stage 1 Gate 评审准备 | W6 | – | Gate 1 包（数据快照 + 测试报告 + 演示） |

### 2.2 关键时间估算依据（spike 实测）

| 阶段 | Spike 实测 | Stage 1 估算 |
|---|---|---|
| 取样 + 哈希 | 1-2 分钟 | – |
| 解析脚本开发 | 15-20 分钟（一个文件） | 1-2 周（生产化：retry、错误处理、监控） |
| 测试用例 | 14-20 条（<1 分钟） | 1 周（覆盖率提升到 50+ 条/源） |
| 数据入库 | 1 个样本 | 1-2 周（5 年 × 12 月 = 60 期） |

**说明**：spike 是"打通管线"的最小验证；生产化还需 10x 时间。

### 2.3 Gate 1 评审标准

- [ ] 5 个来源登记 + 4 类数据入库（国家月度、省级年鉴、地市公报、扫描 PDF）
- [ ] 每个 observation 可 1 跳回 source_document + SHA-256
- [ ] doc 10 测试 2.1-2.6 全过；测试 2.7-2.9 部分过
- [ ] R03（缺失）/R08（授权）/R12（URL 漂移）有兜底
- [ ] 至少 1 个真实研究问题可回答（如"近 5 年江苏 GDP 增长趋势"）

### 2.4 Stage 1 不做什么

- ❌ 不抓取全国市县数据（per PRD 红线；Stage 1 仅试点）
- ❌ 不建立官员评分
- ❌ 不启用 DSH
- ❌ 不做 pgvector embedding

## 3. Stage 2 — 治理观察页面（6-8 周）

### 3.1 任务清单

| 任务 | 周 | 依赖 | 验收 |
|---|---|---|---|
| **S2.1** 实施 person/tenure/position 表 | W1 | S1.x | 公开发布的人事任免数据入库 |
| **S2.2** 实施 policy_document/policy_target/government_commitment 表 | W1-W2 | S1.x | 首批政策文件入库（中央 + 5 省） |
| **S2.3** 实施 project_event 表 + 五态机 UI | W2 | S1.x | 5 省 2020+ 重大项目入库 |
| **S2.4** 实施 budget_allocation/execution 表 | W2-W3 | S1.x | 5 省 2020+ 预算数据入库 |
| **S2.5** 实现 inference_record 表 + 推断 API | W3 | S2.1-2.4 | 推断登记 + UI 可见 |
| **S2.6** 实现 claim_evidence_link + 反例登记流程 | W3-W4 | S2.5 | 反例可入库 + UI 展示 |
| **S2.7** Next.js 前端 — 治理观察页面 | W4-W6 | S2.1-2.6 | 5 个省级页面可演示；六段证据链 UI |
| **S2.8** 七维度观察卡 UI | W5-W7 | S2.7 | 7 维度卡可点击展开 |
| **S2.9** 同类地区对比（初版：手工选择） | W6-W7 | S2.7 | 5 省 × 3 个对比地区 |
| **S2.10** Stage 2 Gate 评审准备 | W8 | – | Gate 2 包 |

### 3.2 Gate 2 评审标准

- [ ] 5 个省/10 个地市观察页面上线
- [ ] 六段证据链完整可点击
- [ ] 七维度观察卡可展开
- [ ] 没有"官员能力总分"（per PRD 红线）
- [ ] 每条 governance 观察标注 INFERENCE/JUDGMENT
- [ ] 至少 1 个反例被显式登记并展示
- [ ] doc 10 测试 3.1-3.5 全过

### 3.3 Stage 2 不做什么

- ❌ 不做官员能力评分（红线）
- ❌ 不做隐性指数
- ❌ 不启用 DSH
- ❌ 不做实时数据（仅月度/年度更新）

## 4. Stage 3 — 比较分析与同类地区（4-6 周）

### 4.1 任务清单

| 任务 | 周 | 依赖 | 验收 |
|---|---|---|---|
| **S3.1** 实现 comparison_group 自动匹配（Mahalanobis） | W1-W2 | S1.x | 5 省 × 5 指标匹配依据可解释 |
| **S3.2** 实现 L4-L5 分析（面板 FE / 事件研究） | W2-W3 | S3.1 | 3 个研究问题跑通 |
| **S3.3** 实施 model_specification 强制登记 | W3 | S3.2 | 所有 L4+ 分析入库 spec |
| **S3.4** DiD/合成控制 UI（L6-L7） | W3-W4 | S3.2 | 1 个研究问题用 DiD 闭环 |
| **S3.5** 不确定性可视化 | W4 | S3.2 | 每个结果有置信区间 + 替代解释 |
| **S3.6** Stage 3 Gate 评审准备 | W5-W6 | – | Gate 3 包 |

### 4.2 Gate 3 评审标准

- [ ] 3 个研究问题完整闭环（含反例）
- [ ] 每条结论标注 evidence_strength
- [ ] model_specification 全部入库
- [ ] doc 10 测试 3.2-3.4 全过
- [ ] doc 10 测试 4.1-4.6 部分过（幻觉检测前置）

### 4.3 Stage 3 不做什么

- ❌ 不启用 DSH
- ❌ 不做全国实时排名
- ❌ 不引入新数据源（除非 R05 触发）

## 5. Stage 4 — 研究 Agent 评估（4-6 周）

### 5.1 任务清单

| 任务 | 周 | 依赖 | 验收 |
|---|---|---|---|
| **S4.1** 写 ADR-0001-dsh-sidecar-decision.md | W1 | Stage 3 Gate 通过 | ADR 通过评审 |
| **S4.2** 实施 11 个只读工具（per doc 07 第 4 节） | W1-W3 | S4.1 | 工具通过安全审计 |
| **S4.3** Agent 容器部署（只读 DB 角色） | W3 | S4.2 | Agent 进程权限边界测试通过 |
| **S4.4** 100 个研究问题评估集 | W2-W4 | – | 评估集上线 |
| **S4.5** 幻觉率 / 可追溯率 / 成本评估 | W4-W5 | S4.4 | 评估报告 |
| **S4.6** 决策：B 启用 / 降级到 A | W6 | S4.5 | doc 07 第 6.3 触发回滚检查 |

### 5.2 Gate 4 评审标准（按 doc 07 第 5.3）

- [ ] 幻觉率 <2%（或降级到 A）
- [ ] 可追溯率 ≥98%
- [ ] 权限违反 = 0
- [ ] doc 10 测试 4.1-4.6 全过

### 5.3 Stage 4 决策矩阵（per doc 07 第 6 节）

```
Stage 4 末决策：
  ├─ B 满足门槛 → 启用 Sidecar
  ├─ B 不满足 → 降级到 A（永不启用 DSH）
  └─ C 任何时候不考虑（ROI 偏低）
```

### 5.4 Stage 4 不做什么

- ❌ 不让 DSH 写库
- ❌ 不让 DSH 自由生成 SQL
- ❌ 不让 DSH 跳过 API 层
- ❌ 不启用 pgvector embedding（如不必要）

## 6. Stage 5 — 优化与运维（4-6 周）

### 6.1 任务清单

| 任务 | 周 | 依赖 | 验收 |
|---|---|---|---|
| **S5.1** 性能优化（查询缓存、precomputed view） | W1-W2 | S4.x | P95 <500ms |
| **S5.2** 备份 + 灾备演练 | W2 | – | RPO ≤1h, RTO ≤4h |
| **S5.3** 可观测性（metrics/log/tracing） | W2-W3 | S4.x | Grafana + Prometheus + Loki |
| **S5.4** 用户文档 + API 文档 | W3 | S5.3 | docs.cegr.example.com 上线 |
| **S5.5** 安全审计 + 渗透测试 | W4 | S5.3 | 无高危漏洞 |
| **S5.6** 公测 + 用户反馈 | W4-W5 | S5.4 | 20+ 真实用户 |
| **S5.7** Stage 5 Gate 评审 + 上线 | W6 | – | 上线 |

### 6.2 Gate 5 评审标准

- [ ] doc 10 全部测试通过
- [ ] PRD 14 全部验收项通过
- [ ] R01-R12 全部进入"已缓解"状态
- [ ] 运维手册完整
- [ ] 安全审计通过

## 7. 不做什么（红线 per PRD 1.3 / 12.10）

无论哪个 Stage：

- ❌ **不建立"官员能力总排名"**（per PRD 6.6）
- ❌ **不收集私人社交账号、泄露资料或非公开个人信息**
- ❌ **不把新闻报道数量、会议次数、招商签约额直接当绩效**
- ❌ **不让大模型直接改写原始统计数据**
- ❌ **不以抓取网页数作为完成标准**
- ❌ **不绕过验证码、付费墙或网站技术限制**
- ❌ **不把 DSH / 任何 Agent 框架作为核心数据仓库或统计计算引擎**
- ❌ **不修改 observation 表的 value 字段（修订走 revision 表）**

## 8. 与其他文档的关系

- Schema：`schema/01-core.sql`
- 风险登记：`docs/09-risk-register.md`（R05 范围失控、R06 错误归因、R09 AI 幻觉）
- 治理观察：`docs/06-governance-observation-method.md`
- DSH 决策：`docs/07-dsh-decision.md`
- 验收测试：`docs/10-acceptance-tests.md`（每 Stage Gate 必过项）
- **现行里程碑（2026-08-30 起）：`docs/54-milestone-replan-20260830.md`** — 覆盖本文 §2–§6 剩余排序；本文 Gate 2 七条降级为产品壳评审

## 9. Stage 状态（2026-08-30 对齐 docs/54）

- [x] Stage 0：仓库审计与技术验证 — Gate 0 CLOSED 2026-08-24 per U-4=A
- [x] Stage 1：**已启动未完成**（连接器骨架 + API；无 31 省 GDP 生产入库）— 剩余工作 = docs/54 **M1–M2**
- [~] Stage 2：**lite UI 已提前交付**；PRD 阶段 2（试点监测/采集质量）= docs/54 **M3**，未开始
- [ ] Stage 3：未启动 → docs/54 **M4**
- [ ] Stage 4：未启动 → docs/54 **M5**
- [ ] Stage 5：未启动（全国地级/区县，不设一次性完成日）

**不宣布 Stage / Gate / O1 PASS。** 禁止用江苏样本 11/15 或首页 HTML 数当作本文进度。