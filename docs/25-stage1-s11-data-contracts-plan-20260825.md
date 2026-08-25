# S1.11 — 数据契约（Great Expectations）规划

- 编号：`25-stage1-s11-data-contracts-plan-20260825`
- 前置：`80` S1.10 通过；`81` 任务书；`docs/08` §2.1 S1.11；`docs/10` §2 / §5.2 / §5.4
- 日期：2026-08-25
- 状态：**规划** — 实现另开任务书

---

## §0 TL;DR

在 S1.9 dbt staging 之上，构建 **Great Expectations 0.18+** 数据契约层，对 `cegr` + `cegr_staging` 的 **5 个核心数据集** 落地 Expectation Suite，覆盖 schema 不变量 / 基数 / 关键业务约束。

**核心验收**：`make ge-check` 在 `cegr_test` 上 PASS，且在空表上**诚实**不爆（per Stage 0 spike 00 教训）。

**本刀不做**：实现 suites/expectations 代码（下一刀）、Next.js 前端、DSH、批量爬取、Gate 1 PASS、改 `gate_thresholds.json`、跑 OCR 全量回归。

---

## §1 目录

| 节 | 内容 |
|---|---|
| §0 | TL;DR |
| §1 | 目录 |
| §2 | 5 个核心数据集清单 |
| §3 | GE 目录结构 |
| §4 | Suite 命名规范 |
| §5 | 空表诚实策略（spike 00 教训） |
| §6 | 期望类型选型 |
| §7 | 与 `docs/10` §2 / §5.2 / §5.4 映射 |
| §8 | CI 与本地跑法 |
| §9 | 红线与边界 |
| §10 | 验收标准 |
| §11 | 与 S1.9 / S1.10 衔接 |

---

## §2 5 个核心数据集

对齐 `docs/08` §2.1 S1.11「5 个核心数据集 contract」。选定如下（**全部依赖 S1.9 dbt staging 落地**）：

| # | 数据集 | 来源表 / View | 行级别预期 | 业务角色 |
|---|---|---|---|---|
| **D1** | 来源目录 | `cegr_staging.stg_source_registry` | 1 行 = 1 个 source | 6 类可入 (S1.3) 来源的稳定总账 |
| **D2** | 文档存证 | `cegr_staging.stg_source_document` | 1 行 = 1 个原始文档/抓取 | SHA-256 存证 + 验证状态 |
| **D3** | 入库运行 | `cegr_staging.stg_ingestion_run` | 1 行 = 1 次 connector 运行 | S1.8 监控数据 |
| **D4** | 观测事实 | `cegr_staging.stg_observation` | 1 行 = 1 个 FACT 观测 | 主事实表；Gate 1 研究问题答案来源 |
| **D5** | 研究级时间序列 | `cegr_staging.int_indicator_timeseries` | 1 行 = (indicator, geo, period, source) | S1.10 API 核心 + 后续可比性 |

**排除**：`int_source_coverage`（S1.11+ 才补；S1.9 已落地但暂不契约——覆盖率是衍生指标，contract 价值低于 5 个核心集）；`stg_observation_quality`（quality flag 衍生，contract 由 `docs/10` §2.7-2.9 测试覆盖）。

---

## §3 GE 目录结构

```
ge/
├── great_expectations.yml              # 0.18+ 配置（postgres + DSN 链 + checkpoints）
├── expectations/
│   ├── d1_source_registry_suite.json
│   ├── d2_source_document_suite.json
│   ├── d3_ingestion_run_suite.json
│   ├── d4_observation_suite.json
│   └── d5_indicator_timeseries_suite.json
├── checkpoints/
│   ├── ci_checkpoint.yml               # CI：所有 5 个 suite 全跑
│   └── dev_checkpoint.yml              # 本地：可单 suite 跑
├── plugins/
│   └── custom_data_docs/
│       └── cegr_renderer.py             # 走项目色板；接 docs/06 视觉语言
├── tests/
│   └── test_ge_suites_loadable.py     # ≥3 测试：suite JSON 可解析；expectation count ≥ N
├── scripts/
│   └── ge_run.sh                      # 包装 great_expectations checkpoint run
└── README.md                          # 跑法 + 如何加新 suite
```

**核心配置点（`great_expectations.yml`）**：
- `datasources.cegr_postgres` 用 `connection_string: ${CEGR_GE_DSN}` env var，**不硬编码密码**
- DSN 链：`CEGR_GE_DSN → CEGR_API_DSN → CEGR_DSN → DATABASE_URL → dev default`
- 默认 `run_id_method: uuid`
- `profiling` 默认 OFF（避免误报）；按需手工触发

---

## §4 Suite 命名规范

**格式**：`{dataset_id}_{table_slug}_suite`

| Suite | 数据源 | Datasource 名 | Batch 名 |
|---|---|---|---|
| `d1_source_registry_suite` | `cegr_staging.stg_source_registry` | `cegr_postgres` | `d1_source_registry_default` |
| `d2_source_document_suite` | `cegr_staging.stg_source_document` | `cegr_postgres` | `d2_source_document_default` |
| `d3_ingestion_run_suite` | `cegr_staging.stg_ingestion_run` | `cegr_postgres` | `d3_ingestion_run_default` |
| `d4_observation_suite` | `cegr_staging.stg_observation` | `cegr_postgres` | `d4_observation_default` |
| `d5_indicator_timeseries_suite` | `cegr_staging.int_indicator_timeseries` | `cegr_postgres` | `d5_indicator_timeseries_default` |

每个 suite 含 **10-20** 个 expectations（不上 50，避免维护负担）。

---

## §5 空表诚实策略（spike 00 教训）

Stage 0 spike 00 OCR 触发：空表上 GE 默认会因 `expect_column_values_to_not_be_null` 报红，触发误判「数据坏了」。本规划明确策略：

### §5.1 规则

1. **永远不在 expect_* 默认参数** 上加 `strict` 模式
2. 涉及非空 / 范围 / 枚举的 expectation **必须** 加 `mostly` 参数：
   - `mostly=0.99` 当 NOT NULL 是事实约束（PK / FK）
   - `mostly=0.80` 当语义约束但允许少量空（如 `caveat_text`）
   - **不**用 `mostly=1.0`（=严格模式，spike 00 已踩坑）
3. **空表容错**：CI 跑前若数据集 row_count=0，**先 emit WARNING 然后跳过 strict-only expectation**；`mostly` 类仍跑
4. **结果分级**：
   - ✅ PASS：所有 expectation PASS
   - ⚠️ PASS_WITH_WARN：空表 + 仅跳过 strict 类
   - ❌ FAIL：违反 `mostly` 阈值或约束

### §5.2 实现

通过 **custom `result_format` + checkpoint `action_list`**：
- `action_list` 含：`store_validation_result` + `update_data_docs` + `custom_empty_table_handler`
- `custom_empty_table_handler` 是 plugin：读 `metrics.table_row_count`，若为 0 则把 strict-only expectation 标记 `skipped` 而非 `failed`
- CI 输出严格遵循 §5.1 三态，不报假阳性

### §5.3 文档承诺

`ge/README.md` 须显式写：**「本套件空表不爆」** + 解释 mostly/empty 策略——避免下一次 Stage 又踩 spike 00 的坑。

---

## §6 期望类型选型

每个数据集选 10-20 个 expectation，覆盖 **3 类**：

### §6.1 Schema 不变量（强约束）

- `expect_table_columns_to_match_ordered_list` — 列名 + 顺序必须一致（catch schema drift）
- `expect_column_values_to_be_of_type` — 关键列类型
- `expect_column_to_exist` — 必要列（PK、FK）

### §6.2 基数与形状（统计）

- `expect_table_row_count_to_be_between` — 行数下限 ≥ 0（永远 PASS）+ 上限（catch 异常爆量）
- `expect_column_unique_value_count_to_be_between` — DISTINCT 计数（如 `source_domain` ≥ 1 当 D1 非空）
- `expect_column_proportion_of_unique_values_to_be_between` — 唯一性比例（如 `stg_observation.observation_id = 1.0`）

### §6.3 业务关键约束

- `expect_column_values_to_match_regex` — code 模式（如 `S1|S2|S3|S4|S5` for `source_level`）
- `expect_column_values_to_be_in_set` — 枚举（`value_type IN ('FACT', 'DERIVED', 'INFERENCE', 'JUDGMENT')`）
- `expect_column_pair_values_A_to_be_greater_than_B` — 派生检查（如 `finished_at >= started_at` 当 finished_at 非空）
- `expect_column_values_to_not_match_regex` — 黑名单（如 `domain NOT MATCH '\\.gov\\.cn$' OR ...` per R-08）

### §6.4 例：d1_source_registry_suite 草样（10 个 expectation）

| # | Expectation | 关键参数 |
|---|---|---|
| 1 | `expect_table_columns_to_match_ordered_list` | `column_list=[source_id, domain, organization, category, primary_url, ..., enabled]` |
| 2 | `expect_column_values_to_not_be_null` `source_id` | `mostly=0.99` |
| 3 | `expect_column_values_to_be_unique` `source_id` | (PK) |
| 4 | `expect_column_values_to_match_regex` `source_level` | `regex='^S[1-5]$'`, `mostly=0.80`（允许未分类） |
| 5 | `expect_column_values_to_be_in_set` `category` | `value_set=['NATIONAL_BULLETIN','PROVINCIAL_YEARBOOK',...]` |
| 6 | `expect_column_values_to_be_between` `enabled` | `min=0, max=1`（boolean 0/1） |
| 7 | `expect_table_row_count_to_be_between` | `min_value=0`（**永远 PASS**）, `max_value=10000` |
| 8 | `expect_column_unique_value_count_to_be_between` `domain` | `min_value=1, mostly=0.50` |
| 9 | `expect_column_values_to_match_regex` `domain` | `regex='^[a-z0-9.-]+\\.[a-z]{2,}$'` |
| 10 | `expect_column_pair_values_A_to_be_greater_than_B` `updated_at >= created_at` | `mostly=1.0`（这一条允许严格——是业务逻辑必然） |

（其余 4 个 suite 类似展开，留给实现刀）

---

## §7 与 `docs/10` §2 / §5.2 / §5.4 映射

### §7.1 docs/10 §2 验收测试

| docs/10 §2 测试 | S1.11 GE suite 覆盖 |
|---|---|
| 2.1 「observation 可回溯到 source_document」 | `d4_observation_suite` exp #3（FK NOT NULL）+ `d2_source_document_suite` exp #2（PK NOT NULL） |
| 2.4 「缺失数据带原因」 | `d4_observation_suite` exp `value_type='MISSING' → missing_reason NOT NULL`，`mostly=0.99` |
| 2.5 「URL 漂移告警」 | `d1_source_registry_suite` exp #9（domain 格式）+ 单独 `d1_primary_url_drift` suite（次刀） |

### §7.2 docs/10 §5.2 自动化框架

S1.11 落地 `great_expectations` 段：
- `pytest tests/` → 数据/方法层单测（已有）
- `dbt build` → 模型层（S1.9 已有）
- `make ge-check` → 数据契约（本刀 + 实现刀）
- `langsmith eval` → Agent 评估（Stage 4+，本刀不引入）

### §7.3 docs/10 §5.4 CI

| 时机 | 触发 |
|---|---|
| **PR** | `lint + pytest + dbt test + ge-check`（前 3 项已存在；`ge-check` 由本刀落 CI 配置） |
| **每日** | 完整 dbt run + GE run（GE 复用 CI 配置） |
| **每阶段末** | Gate 评审包含 GE HTML 报告（per §8.2） |

---

## §8 CI 与本地跑法

### §8.1 本地

```bash
# 第一次：装 GE
pip install great_expectations==0.18.* psycopg2-binary

# 跑全套（5 suite）
make ge-check              # 包装: great_expectations checkpoint run ci_checkpoint

# 跑单 suite（开发用）
great_expectations checkpoint run dev_checkpoint --name d1_source_registry_suite

# 生成 HTML 报告（默认 Data Docs）
great_expectations docs build
# → ./ge/uncommitted/data_docs/local_site/index.html
```

### §8.2 CI（GitHub Actions / equivalent）

新增 `.github/workflows/ge-check.yml`（本地 dev box 无 GH runner；本刀只规划 + 写 YAML，实现刀 push 到 `origin` 后 Cursor 治理 `github` remote）：

```yaml
name: GE data contracts
on: [pull_request]
jobs:
  ge-check:
    runs-on: ubuntu-latest
    services:
      postgres: { ... 镜像同 tests/ ... }
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with: { python-version: '3.11' }
      - run: pip install great_expectations==0.18.* psycopg2-binary
      - name: GE run
        env: { CEGR_GE_DSN: ${{ secrets.CEGR_GE_DSN }} }
        run: great_expectations checkpoint run ci_checkpoint
```

### §8.3 make target

`Makefile` 新增：

```makefile
ge-check:
	cd ge && great_expectations checkpoint run ci_checkpoint

ge-docs:
	cd ge && great_expectations docs build && open uncommitted/data_docs/local_site/index.html

ge-suite-%:
	cd ge && great_expectations checkpoint run dev_checkpoint --name $*
```

---

## §9 红线与边界

| 红线 | 来源 | 本刀态度 |
|---|---|---|
| ❌ 不宣布 Stage 0 PASS / Gate 1 PASS | tasking 78 红线 | 严守；S1.11 是 S1.10 之后的常规刀 |
| ❌ 不批量 2020-2025 入库 | tasking 78 | 不写 connector；不增数据 |
| ❌ 不 HTTP 爬源站 | tasking 78 | 不实现 connector |
| ❌ 不降 OCR 门槛 | tasking 78 + 15 | 不改 `gate_thresholds.json` |
| ❌ 不替用户下裁定 | tasking 78 | 规划 only；§BLOCKED 才请用户 |
| ❌ Cursor 不写 `docs/25` 正文 | tasking 81 红线 | CC 起草；Cursor 仅审计 |
| ❌ 不引入 pgvector / LangSmith / DSH | docs/08 §2.4 | S1.11 仅 GE；其余 Stage 4+ |
| ❌ 不在空表上 FAIL | spike 00 教训 | §5 强制 mostly/empty 策略 |
| ❌ 不硬编码 DSN / 密钥 | 全局红线 | §3 DSN 链强制 env var |

---

## §10 验收标准

S1.11 规划刀（本刀）交付：

| 项 | 标准 |
|---|---|
| `docs/25` 起草 | ✅（本文件） |
| 5 个数据集清单 | ✅ §2 D1-D5 |
| GE 目录结构 | ✅ §3 |
| Suite 命名规范 | ✅ §4 |
| 空表诚实策略 | ✅ §5（spike 00 教训显式化） |
| 期望类型选型 | ✅ §6 + D1 草样 10 个 |
| `docs/10` 映射 | ✅ §7 |
| CI/本地跑法 | ✅ §8 |
| 红线 | ✅ §9 |
| 红线外额外保证 | 「下刀前不读 cegr 原表写契约以外的内容」「不在空表上 FAIL」 |

---

## §11 与 S1.9 / S1.10 衔接

### §11.1 S1.9 dbt staging 衔接

- `stg_*` view 已落地（S1.9 commit `45f16b8` + `1e2dfe5`）；S1.11 GE suite 直接 SELECT from views
- 7 张 staging/intermediate view 全存在（S1.9 dbt run 7/7 PASS）
- 34 个 dbt test PASS（S1.9 commit）— S1.11 是**上一层**契约，不冲突

### §11.2 S1.10 FastAPI 衔接

- S1.10 API 已上线（commit `bcdce45` + receipt `930285b` / `79`）
- S1.10 API 端点返回的 schema 必须与 GE suite 的列约束**对齐**——任何 mismatch 由 GE suite 早暴露
- CI 顺序：`pytest → dbt test → ge-check → curl /api/indicator/{id}/series`（可选 health check）

### §11.3 实现刀（本规划落地后）

任务书 `78`-like 任务书（`reviews/.../83-impl-tasking-...md`）将定义：
- 5 个 suite JSON 的实现（含 D1 草样落地 D2-D5）
- `great_expectations.yml` + checkpoint YAML
- `ge/tests/test_ge_suites_loadable.py` ≥3 tests
- `ge/scripts/ge_run.sh` + Makefile target
- `.github/workflows/ge-check.yml`
- PR commit + dual-push + 回执

**预估**：实现刀 ≈ 4-6 小时（5 suite × 10-15 exp + 配置 + 测试 + CI）。

---

— End of plan — CC @ S1.11 planning @ queue_rev 27 (84 dual heartbeat ARMED) —