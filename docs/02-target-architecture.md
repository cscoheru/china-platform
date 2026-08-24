# 02 — 目标架构图（Target Architecture）

> Stage 0 交付物 #02；对应 PRD 第 15 章第 5 项 + 第 8 章。
> 设计原则：分层、只读、可追溯、不依赖 DSH。

## 1. 设计原则（per PRD 8.1）

1. **原始资料不可变**——每次获取保存 raw + 哈希；上游变则新版本，不覆盖
2. **分层语义清晰**——原始 → 标准化 → 分析 → 检索 → API → 产品 → Agent
3. **核心 ETL 路径无 LLM**——Python + SQL + DuckDB 即可完成 90% 工作
4. **Agent 只在产品层做只读研究编排**——不进 ETL、不写库、不改原始数据
5. **配置驱动而非代码驱动**——新增地区/指标尽量配置化

## 2. 七层目标架构图

```
┌─────────────────────────────────────────────────────────────────────┐
│  L7 产品层（Product）         Next.js 研究工作台 + 静态报告         │
│     - 全国/省级/地级页面、时间轴、比较、治理效能观察、研究工作台     │
│     - 导出 CSV / Markdown / PNG；后续 Word/PDF                      │
└─────────────────────────────────────────────────────────────────────┘
                            ▲  仅读
┌─────────────────────────────────────────────────────────────────────┐
│  L6 Agent 层（Optional）      DSH / Claude Agent SDK                │
│     - 只读工具集（11 个）：get_indicator_series 等                   │
│     - 强制 evidence_id 引用；禁直接 SQL；禁写库                      │
│     - Stage 4 评估启用（doc 07）                                     │
└─────────────────────────────────────────────────────────────────────┘
                            ▲  仅读
┌─────────────────────────────────────────────────────────────────────┐
│  L5 API 层（Read-only API）   FastAPI（+ Uvicorn + Nginx）          │
│     - GET /indicators /observations /sources /policies /persons    │
│     - 所有响应带 source_id, vintage, confidence                     │
└─────────────────────────────────────────────────────────────────────┘
                            ▲
┌─────────────────────────────────────────────────────────────────────┐
│  L4 文档检索层                pgvector + tsvector（PostgreSQL）     │
│     - 政策原文 / 政府报告 / 项目文件 / 历史解释                     │
│     - 段落级 embedding + 关键词                                     │
└─────────────────────────────────────────────────────────────────────┘
                            ▲
┌─────────────────────────────────────────────────────────────────────┐
│  L3 分析语义层                Python（Polars / Pandas）+ DuckDB    │
│     - 派生指标、同类比较、条件化表现、面板固定效应、事件研究          │
│     - 回归/合成控制仅在数据条件可信时使用                             │
│     - 所有 model_spec / comparison_group 入库                        │
└─────────────────────────────────────────────────────────────────────┘
                            ▲
┌─────────────────────────────────────────────────────────────────────┐
│  L2 标准化数据层              PostgreSQL 16 + PostGIS 3.4           │
│     - geo_entity / geo_code_version / boundary_change_event         │
│     - indicator_definition / observation (+_revision /_quality)    │
│     - source_document / source_location / ingestion_run             │
│     - person / position / tenure / appointment_event                │
│     - policy_document / policy_target / policy_measure              │
│     - government_commitment / commitment_progress                   │
│     - project_event / budget_allocation / budget_execution          │
│     - research_question / analysis_run / model_specification        │
│     - derived_metric / inference_record / uncertainty_record        │
└─────────────────────────────────────────────────────────────────────┘
                            ▲
┌─────────────────────────────────────────────────────────────────────┐
│  L1 原始资料层                S3 兼容对象存储（MinIO / OSS / S3）    │
│     - 原始 HTML / PDF / Excel / CSV / 图片 + 元数据 JSON             │
│     - 命名：source_id / sha256 / fetched_at / version              │
│     - 不可变（WORM）；写一次读多次                                   │
└─────────────────────────────────────────────────────────────────────┘
                            ▲
        ┌─────────────────────────────────────────┐
        │  L0 外部源（per source_registry/）      │
        │     国家统计局 / 部委 / 省级 / 地市级     │
        │     海关 / 人民银行 / 财政部 / 审计署等  │
        └─────────────────────────────────────────┘
```

## 3. 横切关注点

### 3.1 可观测性（Stage 2+）
- 结构化日志（JSON Schema）：每条 ingestion_run / analysis_run / API request
- OpenTelemetry traces：跨层追踪
- 指标：抓取成功率、提取置信度分布、模型评分漂移

### 3.2 安全（per PRD 11.5）
- 密钥：Vault / 1Password CLI / env（绝不进仓库）
- 网络：DB / S3 不暴露公网；仅内部 docker network
- 权限：Agent 进程对 DB 只读；写操作仅 ETL 容器

### 3.3 调度（Stage 2+）
- Prefect（推荐）：DAG + retry + alert；轻量；不强依赖 K8s
- 替代：Dagster（如果团队更熟）；自建 cron（不推荐）

### 3.4 数据质量（per PRD 9.4）
- 单位和数量级校验
- 同表合计校验
- 同比/增速反算
- 跨来源一致性
- 时间序列异常
- 修订值冲突检查
- 行政区划有效期
- OCR 置信度 → 人工复核队列
- 缺失值不补零（写 NULL + 原因）

### 3.5 测试（per PRD 14 + doc 10）
- 数据层：单位/合计/同比/边界/OCR
- 方法层：同类比较匹配依据/模型参数/缺失值处理
- AI 层：来源覆盖/引用准确/幻觉检测

## 4. 部署形态（Stage 1+）

### Stage 1（数据底座 + API）
- 单机 Docker Compose：PostgreSQL + PostGIS + MinIO + FastAPI
- 备份：每日 pg_dump + MinIO 版本化
- CI：GitHub Actions（lint + pytest + dbt build）

### Stage 2（监测 + 调度）
- 加 Prefect worker + 监控（Prometheus + Grafana）
- 仍单机；规模不足再考虑 K8s

### Stage 3+（产品 + Agent）
- 加 Next.js（产品层）
- 加 DSH 容器（如果 doc 07 决策启用）
- 仍保持分层容器化，不强上 K8s

## 5. 数据流（典型路径）

```
L0 源发布
    │
    ▼  L1 抓取器（Python，按 source_registry 路由）
       • 限速（每源 ≤1 req/sec 或按 robots.txt）
       • 保存 raw + sha256 + fetched_at
       • 写 ingestion_run 记录（成功/失败/异常）
    │
    ▼  L1 → L2 解析与标准化
       • Excel → openpyxl；HTML → beautifulsoup；PDF → pdfplumber/tesseract
       • 指标名 → indicator_definition（带 alias）
       • 单位/口径/版本从 schema 表读
       • observation 入库 + observation_revision 写初值
    │
    ▼  L2 → L3 分析
       • 派生：占比/增速/指数
       • 同类：基于 geo + indicator + period 的 join
       • 模型：regression / DiD / synthetic control → inference_record
    │
    ▼  L3 → L4 索引
       • 政策原文 / 报告段落 → chunk + embedding → pgvector
    │
    ▼  L4 → L5 API
       • Read-only endpoint；响应带 source_id + vintage
    │
    ▼  L5 → L6 Agent (可选)
       • 11 个只读工具（per doc 07 决策）
       • 每个工具强制带 source_evidence 返回
    │
    ▼  L5/L6 → L7 产品
       • Next.js SSG/ISR
       • 报告导出 Markdown
```

## 6. 不可达路径（per PRD 1.3）

明确**不允许**的路径：

```
❌ L6 Agent 直接 L2 写库
❌ L6 Agent 直接执行任意 SQL
❌ L3 用 LLM 改写 observation.value
❌ L1 抓取时绕过访问限制（per PRD 12.8）
❌ 任何路径产生"官员能力总分"（per PRD 6.6）
❌ L7 直接渲染 INFERENCE/JUDGMENT 为"FACT"（无标签）
```

## 7. 与已有项目的复用

- obsidian-mcp（vault 写入）→ 用于研究笔记落盘
- crawler（既有）→ 仅作源发现线索，不作权威源（PR S3 媒体层）
- puer-hub（Next.js 经验）→ 复用 Next.js 16 / Tailwind v4 / Auth 思路
- classics-spectrum（光谱可视化）→ 复用光谱组件思路（若有"区域—时间"图）

## 8. 演进路线

| 阶段 | 重点层 | 新增能力 |
|---|---|---|
| Stage 1 | L1, L2, L5 | 国家+省级数据底座 + API |
| Stage 2 | L0-L4 全部 | 调度 + 监测 + 试点地市 |
| Stage 3 | L1-L2（人物/政策/项目子域）| 任免、政策、项目、承诺跟踪 |
| Stage 4 | L3（分析）+ L6（Agent）| 同类比较 + 条件化 + Agent 评估 |
| Stage 5 | 全平台横向扩展 | 地级市+区县，按价值排期 |

## 9. 关键取舍（决策记录）

| 决策 | 选项 | 选定 | 理由 |
|---|---|---|---|
| 主 OLTP/OLAP DB | PostgreSQL+PostGIS vs ClickHouse vs DuckDB | **Postgres+PostGIS** | 一库多用、pgvector 整合、地理分析、运维简单 |
| 历史批处理 | Postgres vs DuckDB vs Parquet+Spark | **DuckDB + Parquet** | 单机分析性能优、不依赖集群、Stage 4 再评估 ClickHouse |
| 向量库 | pgvector vs Qdrant vs Milvus | **pgvector**（起步）| 减少组件；规模不足再独立 |
| 后端 | FastAPI vs Django vs Flask | **FastAPI** | 异步、Pydantic 校验、OpenAPI 自动 |
| 前端 | Next.js vs Vite+React vs Svelte | **Next.js**（Stage 4+ 引入）| 与用户现有项目栈一致 |
| 调度 | Prefect vs Dagster vs Airflow | **Prefect**（Stage 2+）| 轻量、DAG-as-code、Python 原生 |
| 对象存储 | MinIO vs S3 vs OSS | **MinIO**（本地）+ **OSS**（生产）| 开发友好、生产可平迁 |
| 模型转换 | dbt vs SQLMesh vs 裸 SQL | **dbt**（Stage 2+ 引入）| 测试 + 血缘 + 文档化 |
| OCR | tesseract vs paddleocr | **tesseract**（起步）| 部署简单；中文精度不足时再升级 paddleocr |

任何决策变更需更新本表 + 写 ADR（`docs/adr/`）。
