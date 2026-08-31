# 01 — 当前架构图（Current Architecture）

> Stage 0 交付物 #01；对应 PRD 第 15 章第 5 项。
> **2026-08-30 刷新**（M0.2 / `docs/54` U5）。原文「空仓库」仅描述 2026-08-23 开库瞬间，不得再当现状。
> 对照目标：`docs/02-target-architecture.md`。里程碑：`docs/54-milestone-replan-20260830.md`。
> 不宣布 Gate / O1 PASS。

## 1. 总览

仓库已从 greenfield 长成 **monorepo + 演示前端 + 只读 API + schema/dbt 骨架 + 公开源 SHA 归档**。数据面仍停在连接器 PARTIAL / mock 默认；产品面已有 Gate 2 **演示壳**（PRD 16.1 的采集质量 Gate 2 未过）。

HEAD 快照：`9efac2d`（刷新日）。evidence pack `artifact_count=1004`。

## 2. 当前仓库结构（摘要）

```
china platform/
├── docs/                    PRD + Stage 0–2 计划/索引（00–54…）
├── schema/                  01-core.sql + migrations 001–014
├── source_registry/         registry.csv（18 数据行；NATIONAL_BULLETIN_SPIKE 拆行 per M1 T0 · 2026-08-31）
├── backend/src/china_platform/
│   ├── api/                 FastAPI 只读（indicator series / observation / source）
│   ├── connectors/          nbs_monthly, provincial_yearbook, sz bulletin, scanned_pdf_ocr
│   └── monitoring/
├── dbt/models/              staging + marts（18 SQL）
├── frontend/                Next.js：首页、5 省、10 城、public-extracts、七维、peer-compare
├── spikes/00–04/            Stage 0 四类提取验证
├── data/seed_archives/      11 份统计局首页 HTML（L0 线索，非 observation）
├── tests/                   53 个项目 test_*.py
├── infra/docker-compose.yml PostgreSQL 16 + PostGIS（仅 db，无 MinIO/Prefect）
└── reviews/…/00-EXEC-QUEUE.md  调度源（rev 47 起压缩；历史见 archive）
```

## 3. 七层现状（对照 docs/02）

```
L7  产品     Next.js 10 路由 + 公网预览 china.3strategy.cc
             默认 NEXT_PUBLIC_USE_MOCK=true；MART_FIXTURE 可选
                    ▲ 已接真 series：`/research/m1-series`（湖北 GDP 1 行真 observation）
L6  Agent    无（正确延后至 M5）
L5  API      FastAPI GET /api/indicator/{id}/series 等；测在 cegr_test
L4  检索     无 pgvector
L3  分析     dbt mart；1 行真 SHA pilot（nanjing CONDITION = a7e4029d）
             其余 demo / '0'*64
L2  标准库   schema 齐；M1 指定表已 SUCCESS（湖北 2026 H1 GDP observation 真行入 cegr_staging.int_indicator_timeseries；详见 docs/55 §5 + 629 回执）
L1  原始     seed_archives + spikes；无 MinIO WORM
L0  外部源   registry 18 行（NATIONAL_BULLETIN live + NATIONAL_BULLETIN_SPIKE 本地样本 拆行）；首页 HTML 与可解析统计表 URL 混用
```

### 3.1 L0 / L1 SHA 双真相（**M0.3 已拆行** per M1 T0 · 2026-08-31）

| 对象 | SHA-256 前 8 | 字节含义 |
|---|---|---|
| `spikes/01-national-yearbook/sample.html` | `dea13b8a` | 本地 spike；388238 B；NBS 连接器单测锁此文件 |
| registry `stats.gov.cn` / `NATIONAL_BULLETIN` `file_hash_sha256` | `a7e4029d` | 2026-08-27 live 公报（180165 B）；**live-only，无本地样本** |
| registry `stats.gov.cn` / `NATIONAL_BULLETIN_SPIKE` `file_hash_sha256` | `dea13b8a` | sample.html 本地样本行；388238 B；与文件字节一致 |
| mart pilot `lineage_source_file_sha256` | `a7e4029d` | 绑 live 哈希，仓内无对应 WORM 文件路径保证 |

拆行落地（per `docs/55` §T0 · 2026-08-31）：NATIONAL_BULLETIN 行清空 `local_sample_path`，新增 NATIONAL_BULLETIN_SPIKE 行承载本地样本；NbsMonthlyConnector 默认指向 SPIKE 行。**前 11 行 SHA 不变**刀锁已破，回执 ACCEPTED disclosure（U5/M0.3 授权）。

### 3.2 与 docs/02 部署形态的差距

| docs/02 Stage 1 目标 | 现状 |
|---|---|
| Compose：Postgres + PostGIS + MinIO + FastAPI | 仅 PostGIS `infra/docker-compose.yml` |
| 每日 pg_dump + MinIO 版本化 | 无 |
| GitHub Actions lint + pytest + dbt | `ge-check.yml` 等；非完整 Stage 1 CI |
| Prefect + Grafana（原写 Stage 2 / docs/08 误放 S1.8） | 无；按 `docs/54` 挪到 M3 |

## 4. 已有 vs 没有

| 层 | 当前 | 目标（docs/02） |
|---|---|---|
| 原始资料层 | 目录归档，非对象存储 | MinIO / OSS WORM |
| 标准化数据层 | schema + 测试库；生产序列未入 | observation SUCCESS 可查询 |
| 分析语义层 | dbt 形状 + demo mart | 派生指标 + model_spec |
| 文档检索层 | ❌ | pgvector（M5 后） |
| API 层 | ✅ 只读骨架 | 接真 vintage/source |
| 产品层 | ✅ 演示壳 | 关 mock 读 L5 |
| Agent 层 | ❌ | 只读 sidecar（M5 评估） |
| 调度 | 刀链文档，非 Prefect | M3 |
| 测试 | pytest 53 文件 | 保持；禁止为全绿放宽 SHA 闸 |

## 5. 决策（2026-08-30）

- **需要「纠偏」而不是「从空开始」**：L7 已提前引入（偏离 docs/02「Next.js Stage 4+」）；后续 L7 只消费 L5。
- 首页 HTML SHA-lock **降为 L0 线索**，停止作为里程碑（U1）。
- 现行路线：`docs/54` M1 单表闭环 → M2 31 省 GDP（08b）。

## 6. 与 PRD 15.2 的关系

PRD 要求盘点前端、后端、数据库、调度、AI、部署和测试。2026-08-30 盘点结论：上述组件**均已出现骨架**；缺口是 **L1 不可变归档与 L2 真 observation**，不是「仓库为空」。
