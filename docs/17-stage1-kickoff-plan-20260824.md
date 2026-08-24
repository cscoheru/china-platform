# Stage 1 — Kickoff Plan (CC 起草,待 Cursor S1.1 审验)

> 文件编号：`docs/17-stage1-kickoff-plan-20260824.md`
> 起草方：CC（Claude Code）
> 起草日期：2026-08-24
> 授权依据：`reviews/23-stage1-kickoff-20260824.md` §2 S1-K1 + 用户 U-4=A
> 范围：**仅规划**；不动生产库；不改 `gate_thresholds.json`；不批量爬取

---

## §0. TL;DR

| 项 | 值 |
|---|---|
| Gate 0 | CLOSED（2026-08-24,per U-4=A） |
| Stage 1 范围 | S1.1–S1.12（数据底座,4-6 周,见 `docs/08` §2） |
| 本计划覆盖 | **仅 W1**（S1.1–S1.3 分解）；S1.4+ 等 Cursor 审验 W1 后另下 |
| 试点 | 非全国市县全量（per PRD 红线 + `docs/08` §2.4） |
| 红线 | 不全国抓取；不官员评分；不 DSH；不降 OCR 门槛；1909 不代表中国 |

---

## §1. W1 范围：S1.1–S1.3 分解

### S1.1 — PostgreSQL 16 + PostGIS 部署（W1）

| 维度 | 内容 |
|---|---|
| 目标 | 数据库可连接；`schema/01-core.sql` 在生产路径上跑通 |
| 路径 | **本任务禁止**：不在 CC 本任务内启动 Docker 部署生产 PG；本计划仅交付 *连接模板 + 应用 apply 链契约* |
| 应用链契约 | 与 Stage 0 同：`tests/conftest.py` autouse session fixture + `scripts/build_evidence_pack.py` `run_db_apply()` 均 DROP+链式 apply `schema/01-core.sql` + `schema/migrations/*.sql` |
| 退出标准 | 应用链在目标 PG 实例上 exit 0；`tests/test_schema_negative.py` 39 + `tests/test_source_governance.py` 21 全过 |
| 不做 | ❌ Docker compose 拉起新容器；❌ 改 connection string；❌ 暴露公网端口 |

### S1.2 — schema/migrations + Alembic 初始化（W1）

| 维度 | 内容 |
|---|---|
| 现状 | `schema/01-core.sql` + `schema/migrations/001_create_core.sql/log` + `002_source_governance.sql/log`（手工 SQL 文件 + 自定义 apply 链） |
| 关系策略 | **并存而非替换**：手工 SQL 文件作为「canonical」源（已通过 Stage 0 39+21 测试）；Alembic 仅作「migration 调度器」,初始 `alembic init` 目录 + `env.py` 指向同一 PG schema（`cegr`） |
| 版本映射 | `alembic_version` 表手工播种为 `002`（HEAD），未来 migration 003+ 走 Alembic 模板 |
| 退出标准 | `alembic current` = `002`；`alembic history` 含 001/002 两节点；`alembic upgrade head` no-op |
| 拒绝 | ❌ 用 Alembic 重写 001/002；❌ 删除现有手工 SQL |

### S1.3 — source_registry + source_document + URL 健康监控（W1-W2）

| 维度 | 内容 |
|---|---|
| 现状 | 表已存在（39 schema 负例 + 21 governance 测试覆盖）；registry CSV 6 条来源 + 1 条陕西研究轨 |
| W1 任务 | (a) 把 CSV 6 条（4 spike 已验证 + 1909 + 陕西）批量导入 `source_registry` 表；(b) 增 `source_document_verification_event` 触发器回归测试（已有 schema/migration 002） |
| W1-W2 任务 | URL 健康监控：基于 `registry.csv::update_frequency` + `failure_handling` 字段，写 `health_check.py` 周期脚本（**仅做监控不发爬取请求**） |
| 退出标准 | 6 条来源全部入表且 `declared_source_level` 与 CSV 一致；`source_level_s0_requires_verified` CHECK 约束无违例；URL 监控脚本 exit 0（dry-run 模式） |
| 不做 | ❌ 真发 HTTP 请求到源站；❌ 自动 ingest；❌ 改 S0/S3 等级（per `docs/03 §9` I-05） |

---

## §2. 与现有 schema 的关系（Alembic vs 手工 SQL 策略）

```
schema/
├── 01-core.sql                # canonical DDL;Stage 0 已验证
└── migrations/
    ├── 001_create_core.sql    # 同 01-core 的增量视图（含 PostGIS）
    ├── 001_create_core.log    # PG16 apply log（2026-08-23 留档）
    ├── 002_source_governance.sql  # I-05 治理增量
    └── 002_source_governance.log  # PG17 apply log
```

**决策**：**手工 SQL 文件保留为 canonical**；Alembic 只承担「未来 003+ 的 migration 调度」。

| 现有文件 | 在 Stage 1 中的角色 |
|---|---|
| `schema/01-core.sql` | canonical DDL；Stage 1 不得修改其内容（除非用户红线改动触发新 migration） |
| `schema/migrations/001_create_core.sql` | 同 01-core 的 PostGIS 增量视图；保留 |
| `schema/migrations/002_source_governance.sql` | I-05 治理；保留 |
| **新增（CC 不在本任务动手）** | `alembic/` 目录、`alembic.ini`、`alembic_version` 表手工播种为 `002` |

**与 Stage 0 apply 链契约的兼容性**：`tests/conftest.py` 的 autouse session fixture 与 `scripts/build_evidence_pack.py` 的 `run_db_apply()` 仍直接 `psql -f schema/01-core.sql + migrations/*.sql`,绕开 Alembic。Stage 1 W1 阶段不破坏这条链。

---

## §3. 首批 5 来源登记清单

来源：`source_registry/registry.csv`（6 行数据 + 1 表头 = 7 行 × 18 列）。

| # | domain | category | declared_source_level | role | Stage 1 试点范围 |
|---|---|---|---|---|---|
| 1 | stats.gov.cn | NATIONAL_YEARBOOK | S0 | spike 00 已验证；OCR（JPG 扫描） | W2-W3：S1.4（NBS-MONTHLY）父源 |
| 2 | stats.gov.cn | NATIONAL_BULLETIN | S0 | spike 01 已验证；HTML 表格 | W2-W3：S1.4 数据源 |
| 3 | tjj.hubei.gov.cn | PROVINCIAL_BULLETIN | S0 | spike 02 已验证；EXCEL | W2-W3：试点省级 |
| 4 | sz.gov.cn | MUNICIPAL_BULLETIN | S0 | spike 03 已验证；HTML | W2-W3：试点市级 |
| 5 | **archive.org（1909）** | SCANNED_PDF_UPLOAD | **S3** | spike 04 已验证；**仅 OCR 管线压力** | W3-W4：S1.7 测试样本（**不代表中国**） |
| 6（研究轨） | wb.flk.npc.gov.cn | SCANNED_PDF_RESEARCH | S0（研究轨） | 陕西四页（per U-1/U-2/U-3） | W3-W4：S1.7 中文 OCR 研究（**非门控**,per U-3） |

**4 spike 已验证 + 1 待定 = 5 个生产范围来源**：
- 已选 5：spike 00/01/02/03/04（archive.org）
- **第 5 个待定**：候选 = (a) spike 02 的另一省份（如广东/江苏）；(b) spike 03 的另一地市（如杭州/广州）；(c) 中央部委新源（财政部/审计署月报）。**Cursor 审验 S1-K1 后另下选定依据**。

**声明（per P-2 / U-3）**：
- ❌ 1909 archive.org 不代表中国（仅 OCR 管线压力）
- ❌ 陕西 NPC 不参与 Gate（仅研究轨）

---

## §4. 已知 Stage 0 遗留质量债

Stage 1 必须诚实延续记录，不得用「Stage 1 启动」掩盖：

| 债 | 来源 | Stage 1 中的诚实口径 |
|---|---|---|
| **spike 00 needs_review 56%** | `data/extracts/00-national-yearbook-table/per_column_accuracy.json` | `overall_verdict=BLOCKED`；超过 `docs/08b` 50% 回滚线；S1.4 真实入库需重新评估 |
| **1909 eval FAILED** | `spikes/04-scanned-pdf/eval_report.json` + `gate_thresholds.json::spike04_current_eval` | numeric 0.0% / digit-char 3.7% / needs_review 450/450；S1.7 仅作 OCR 管线回归测试 |
| **陕西 research-only** | `spikes/04-scanned-pdf/shaanxi_text_eval_report.json` + `docs/16` | Han 93.93% 满足适用研究阈值；numeric N/A；**不参与 Gate 1** |
| **I-05 治理** | `schema/migrations/002_source_governance.sql` + 21 测试 | 已闭环；S1.3 入表时强制应用 |
| **code review 工具阻塞** | `docs/16 §6.2` BLOCKED_BY_TOOLING | 持续记录；Stage 1 任何 ≥5 文件修改仍需尝试 `/review` |
| **evidence pack 自漂移** | `reviews/11 §1.1` | 每次 S1 docs 更新后必须 rebuild pack → pack_errors=0 再 commit |

---

## §5. Gate 1 退出标准对照表（来自 `docs/08` §2.3）

| 标准 | 当前状态（Stage 0 末） | Stage 1 W6 目标 | 阻塞 / 风险 |
|---|---|---|---|
| 5 来源登记 + 4 类数据入库 | 6 行 CSV 已存在；4 spike 已验证管线；0 行入库 | 5 行入表（4 spike 已验证 + 1 待定）+ 4 类全部入库至少 1 期 | spike 00 needs_review 56% 可能让 NBS-MONTHLY 入库延后 |
| 每个 observation 1 跳回 source_document + SHA-256 | schema 已支持（39 负例验证） | 全表强制应用；CI 测试覆盖 | I-05 触发器必须在 ingest 路径上 |
| `docs/10` 测试 2.1-2.6 全过 | 2.1-2.6 在 Stage 0 spike 套件中已部分覆盖 | 全过；2.7-2.9 部分过 | 需要扩展现有 spike 测试而非新写 |
| R03（缺失）/R08（授权）/R12（URL 漂移）兜底 | R03/R08 在 Stage 0 schema 已有兜底；R12 仅 registry 字段 | 兜底逻辑 + 测试 | 需逐条查 `docs/09` |
| 至少 1 个真实研究问题可回答 | 未演示 | W6 演示（如「近 5 年江苏 GDP 增长趋势」） | spike 02 仅有湖北；需扩江苏 |

**Gate 1 不等于 Stage 1 整体 PASS**（per `reviews/23` §5）：仅启动 Stage 1 工作,Gate 1 评审由 Cursor 在 W6 末下发新任务书。

---

## §6. S1-K1 本任务交付清单（本文件 = 全部）

- [x] 本文件 `docs/17-stage1-kickoff-plan-20260824.md`（CC 起草）
- [ ] Cursor S1.1 技术方案审验（Cursor 将在审验本文件后更新 `00-CC-CURRENT` §NOW = S1.1）
- [ ] 之后才动 PostgreSQL 部署（per Cursor §3；本任务内不动）

**S1-K1 内未做（红线遵守）**：
- ❌ Docker 部署生产 PG
- ❌ 批量爬取
- ❌ 改 `gate_thresholds.json`
- ❌ 写 Alembic `env.py`（在 S1.1 任务书下发后才写）
- ❌ 入表任何 source_registry 行（CSV 仍为真源）
- ❌ 改 PRD
- ❌ 改 Stage 0 已闭环的 R4-1..R4-6 / R5-A..R5-I / R6-A..R6-E 任何文档

---

## §7. 下一刀（Cursor 审验后）

Cursor 审验本文件后,`00-CC-CURRENT.md` §NOW 预计更新为 **S1.1**（PostgreSQL 部署）。届时 CC：
1. `git pull origin main`
2. 读新 §NOW + 新任务书
3. 按 21 §1 触发器执行

— End of Stage 1 kickoff plan —