# 01 — 当前架构图（Current Architecture）

> Stage 0 交付物 #01；对应 PRD 第 15 章第 5 项。
> 状态：**空仓库，无既存架构**。

## 1. 总览

仓库创建于 2026-08-23，**此前不存在任何代码、数据、文档、CI/CD、部署**。
本 Stage 0 之前的状态可视为**完全空**。

## 2. 当前仓库结构

```
china platform/
├── china-economy-governance-research-platform-prd-v0.1.md   ← 唯一已有文件（PRD）
└── .git/                                                    ← 本次 init
```

## 3. 当前架构图

```
        ┌────────────────────────────────────────────┐
        │                   (空)                      │
        │   无前端、无后端、无数据库、无抓取、无部署  │
        └────────────────────────────────────────────┘
```

## 4. 不存在的组件（用于与目标架构对比）

| 层 | 当前 | 目标（见 doc 02） |
|---|---|---|
| 原始资料层 | ❌ | S3/对象存储 |
| 标准化数据层 | ❌ | PostgreSQL + PostGIS + DuckDB |
| 分析语义层 | ❌ | 计算引擎（Python/Polars/SQL） |
| 文档检索层 | ❌ | pgvector / OpenSearch |
| API 层 | ❌ | FastAPI |
| 产品层 | ❌ | Next.js（暂缓，Stage 1 仅 CLI/Notebook） |
| Agent 层 | ❌ | 可选 DSH（doc 07 决策矩阵） |
| 调度层 | ❌ | Prefect（Stage 2+） |
| 可观测层 | ❌ | 结构化日志 + OpenTelemetry（Stage 2+） |
| 测试层 | ❌ | pytest + dbt tests（Stage 1+） |
| CI/CD | ❌ | GitHub Actions（Stage 1+） |
| 部署 | ❌ | Docker + 主机（Stage 1+） |

## 5. 决策

- **不需要"迁移"计划**——因为没有存量系统
- Stage 1 起按 doc 02 的目标架构自下而上建设
- 任何"假设已有的旧架构"在此项目都不成立；如有 PRD 误读，将在评审时修订

## 6. 与 PRD 15.2 的关系

PRD 15.2 要求"使用 `rg --files`、`rg` 和项目已有文档盘点前端、后端、数据库、任务调度、AI、部署和测试结构"。本次盘点结论：

```
$ rg --files | head -5
china-economy-governance-research-platform-prd-v0.1.md

$ rg --type py | wc -l
0    # 无 Python
$ rg --type ts | wc -l
0    # 无 TS
$ rg --type sql | wc -l
0    # 无 SQL
$ rg --type-add 'yaml:*.{yml,yaml}' --type yaml | wc -l
0    # 无 YAML
```

**结论**：仓库盘点完毕，结构清晰可见（空）。Stage 1 起按 doc 02 自底向上建设。
