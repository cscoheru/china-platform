# 中国经济与区域治理研究平台 (China Economy & Regional Governance Research Platform)

> 长期数据与研究基础设施；面向中国宏观经济、省级、地级及区县的官方数据，
> 围绕"事实可追溯、计算可复现、归因审慎"的研究原则建设。

## 项目状态

- **当前阶段**: Stage 0 — 仓库审计与技术验证（per `china-economy-governance-research-platform-prd-v0.1.md` 第 15 章）
- **下一阶段**: Stage 0 完成并通过评审后启动；**不得自行进入 Stage 1**

## 文档

| 路径 | 内容 |
|---|---|
| `china-economy-governance-research-platform-prd-v0.1.md` | PRD 首版（需求书） |
| `docs/00-project-assessment.md` | 项目评估（现状、约束、差距） |
| `docs/01-current-architecture.md` | 当前架构图（空仓库 → 无架构） |
| `docs/02-target-architecture.md` | 目标架构图 |
| `docs/03-source-registry.md` | 数据源登记模板 |
| `docs/04-data-model.md` | 实体关系 + 数据字典 |
| `docs/05-indicator-methodology.md` | 指标口径版本化方法 |
| `docs/06-governance-observation-method.md` | 治理效能观察框架（六段证据链） |
| `docs/07-dsh-decision.md` | DSH 三档决策矩阵 |
| `docs/08-mvp-plan.md` | 8-12 周 MVP 任务拆分 |
| `docs/08b-strict-mvp.md` | 严格 8-12 周 MVP 任务拆分（返工新增） |
| `docs/09-risk-register.md` | 风险登记 |
| `docs/10-acceptance-tests.md` | 验收测试设计 |
| `docs/11-stage0-review.md` | Stage 0 评审与返工闭环 |
| `docs/12-stage0-closure-and-report.md` | Stage 0 收口矩阵与最终报告 |

## 目录结构

```
.
├── docs/                          Stage 0 交付文档（PRD 第 15 章）
├── data/
│   ├── raw/                       原始资料（不可变，每次抓取新版本）
│   ├── processed/                 标准化数据
│   └── extracts/                  spike 提取输出
├── schema/                        SQL DDL + Prisma schema
│   └── migrations/
├── backend/                       Python 后端（FastAPI，Stage 1+）
│   └── src/china_platform/
├── spikes/                        Stage 0 技术验证 spike（6 个目录）
│   ├── 00-national-yearbook-table/   国家统计年鉴 JPG 表（OCR 真值对照）
│   ├── 00-provincial-yearbook-table/ 省级年鉴 ZIP（xls 真值对照）
│   ├── 01-national-yearbook/      国家统计年鉴表
│   ├── 02-provincial-yearbook/    省级年鉴表
│   ├── 03-municipal-bulletin/     地市统计公报
│   └── 04-scanned-pdf/            扫描 PDF 表格
├── scripts/                       证据打包（build_evidence_pack）
├── evidence_pack/                 manifest 证据包
├── source_registry/               数据源登记（CSV）
└── tests/                         跨切面测试（数据/方法/AI 三层）
```

## 核心原则

1. **FACT / DERIVED / INFERENCE / JUDGMENT 严格分层**——每个数据点要标类型，AI 不得把推断写成事实。
2. **数据可追溯**——每个数据点带来源、版本、统计期、发布日期、修订状态、提取方式、置信度。
3. **不简单归因**——不把经济增长归因于单一官员或单项政策；建立"条件化相对表现"而非"官员评分"。
4. **先闭环再扩展**——先做国家—省级—样本城市的可用闭环，再扩展到全国地级市和区县。
5. **核心 ETL 不依赖 DSH/Agent**——DSH (DeepSeek Harness) 仅作为可选研究 Agent 编排层，不进确定性计算路径。

## 不做什么

- ❌ 不建立"官员能力总排名"
- ❌ 不收集私人社交账号、泄露资料或非公开个人信息
- ❌ 不把新闻报道数量、会议次数、招商签约额直接当绩效
- ❌ 不让大模型改写原始统计数据
- ❌ 不以抓取网页数作为完成标准
- ❌ 不绕过验证码、付费墙或网站明确设置的技术限制
- ❌ 不在 Stage 0 批量抓取全国市县数据

## 运行

Stage 0 文档全部是 Markdown，无需运行；后续阶段参见 `docs/08-mvp-plan.md`。

## 许可与合规

- 严格遵守来源网站规则、数据授权与引用要求（PRD 11.6）
- 优先官方公开下载；低频率访问；保存原始版本；提供人工上传入口（PRD 12.8）
