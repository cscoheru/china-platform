# S1.11 — CC 实现回执

- 编号：`87-stage0-cc-s11-impl-receipt-20260825`
- 前置：`86` 实现任务书；`docs/25` 规划；`83` 规划回执；`85` 规划审计
- 提交：`052081b`
- Pack：478 artifacts (role_count +1 vs 458；新角色 `data_contract_suite` × 20)
- 双推：origin ✅ (88f7fe4..052081b) / github ✅ (32a4485..052081b)

## 交付物

| 类别 | 文件 | 说明 |
|---|---|---|
| Suites | `ge/expectations/d1_source_registry_suite.json` | 10 expectations — schema drift + PK not-null + uniqueness + source_level enum + category enum + enabled [0,1] + domain regex + updated_at ≥ created_at (Cursor 85 §1, mostly=0.99) |
| Suites | `ge/expectations/d2_source_document_suite.json` | 10 expectations — SHA-256 regex `^[a-f0-9]{64}$` (R-08 校验链) + verification_status enum + publication_date [1900, 2100] |
| Suites | `ge/expectations/d3_ingestion_run_suite.json` | 10 expectations — status enum (RUNNING/SUCCESS/PARTIAL/FAILED) + records_extracted/inserted 非负 + records_inserted ≤ records_extracted (mostly=0.99) + insertion_pct [0,100] + is_stale boolean |
| Suites | `ge/expectations/d4_observation_suite.json` | 12 expectations — 22-column schema drift + observation_id PK + indicator_id/geo_entity_id/source_id FKs (mostly=0.99) + value_type enum + extraction_method enum (8 values from `cegr.extraction_method`) + confidence [0,1] (mostly=0.80) + period_end ≥ period_start (Migration 004 invariant) |
| Suites | `ge/expectations/d5_indicator_timeseries_suite.json` | 10 expectations — 16-column schema drift + value NOT NULL (int view filter) + value [-1e15, 1e15] sanity bound + source_level enum S1-S5 + verification_status enum + confidence [0,1] (mostly=0.80) + period_end ≥ period_start |
| Config | `ge/great_expectations.yml` | config_version 4.0 + DSN chain `${CEGR_GE_DSN}` → SqlAlchemyExecutionEngine + InferredAssetSqlDataConnector (schema_name=cegr_staging) + EmptyTableHandler plugin |
| Checkpoint | `ge/checkpoints/ci_checkpoint.yml` | 5 validations × 1 batch each, index=-1 (latest snapshot) — StoreValidationResultAction + StoreEvaluationParametersAction + UpdateDataDocsAction |
| Checkpoint | `ge/checkpoints/dev_checkpoint.yml` | single D4 suite for single-suite dev loop |
| Plugin | `ge/plugins/custom_data_docs/empty_table_handler.py` | reclassifies FAIL → PASS_WITH_WARN when `metrics.table_row_count <= 1` AND all failing expectations have `mostly < 1.0`; preserves strict mostly=1.0 as a 红色（空表也失败） |
| Plugin | `ge/plugins/__init__.py` + `ge/plugins/custom_data_docs/__init__.py` | package markers |
| Runner | `ge/scripts/ge_run.sh` | DSN-chain wrapper, venv resolution (`/tmp/ge_venv/bin/python` preferred), subcommands: `check` / `--suite <name>` / `--docs` |
| Tests | `ge/tests/__init__.py` + `conftest.py` | sys.path → ge/ + `ge_dir` fixture + `dsn` fixture |
| Tests | `ge/tests/test_ge_suites_loadable.py` | **7 tests** — files exist, JSON parse, ≥10 expectations, type/kwargs structure, **NO mostly=1.0** (红色), ≥40% mostly coverage, yml DSN+datasource+plugin, GE 0.18 ExpectationSuite round-trip via ExpectationConfiguration |
| Tests | `ge/tests/test_empty_table_strategy.py` | **6 tests** — PASS-through, reclassification on empty, no-touch on non-empty, strict mostly=1.0 still fails, threshold constant=1, kwargs graceful |
| Tests | `ge/tests/test_checkpoints_loadable.py` | **6 tests** — both checkpoints exist, ci_checkpoint 5 validations, dev_checkpoint D4, batch_request data_asset matches cegr_staging.{view}, ge_run.sh executable |
| Build | `Makefile` | `ge-check` / `ge-docs` / `ge-suite-%` / `ge-test` / `ge-list` |
| CI | `.github/workflows/ge-check.yml` | 2 jobs: loadable (pytest ge/tests/) + contract (suite JSON + checkpoint YAML structure) |
| Manifest | `evidence_pack/manifest.json` | +20 ge/ artifacts under new `data_contract_suite` role; 458 → 478 (artifact_count); 17 → 18 (role_count); role_count sum 478 == artifact_count 478 |
| Builder | `scripts/build_evidence_pack.py` | +ge/ patterns in collect_artifacts() + classify() rule `data_contract_suite` for `ge/`, `.github/workflows/`, `Makefile` |
| Ignore | `.gitignore` | +ge/gx/, ge/uncommitted/, ge/data_docs/ (GE 0.18 runtime artifacts; never source-controlled) |

**Tests: 19/19 passed in 3.98s** (`/tmp/ge_venv/bin/python -m pytest ge/tests/`).

## 设计要点

### 1. Empty-table 三态（docs/25 §5）

| row_count | mostly < 1.0 | mostly = 1.0 |
|---|---|---|
| ≤ 1 (空) | FAIL → PASS_WITH_WARN | FAIL（红色保留） |
| > 1 (非空) | FAIL（数据真问题） | FAIL |

阈值常量 `EMPTY_TABLE_ROW_COUNT = 1`，命名导出便于单测 + 文档同源。

### 2. mostly 策略（Cursor 85 §1）

| 场景 | 阈值 | 适用 |
|---|---|---|
| PK/FK 不为空 | **0.99** | `expect_column_values_to_not_be_null` on `source_id` / `run_id` / `observation_id` 等 |
| 列对不变量 | **0.99** | `expect_column_pair_values_a_to_be_greater_than_b` |
| 枚举/正则 | **0.80** | source_level / category / SHA-256 / extraction_method |
| 计数范围 | **0.99** | records_extracted / records_inserted / insertion_pct |
| Schema drift guard | **无**（结构断言） | `expect_table_columns_to_match_ordered_list` / `expect_column_values_to_be_unique` |

**无任何 expectation 使用 mostly=1.0**（`test_no_expectation_uses_strict_mostly_one` 强制）。

### 3. DSN chain（与 S1.10 一致）

`CEGR_GE_DSN` → `CEGR_API_DSN` → `CEGR_DSN` → `DATABASE_URL` → `postgresql://postgres:postgres@127.0.0.1:55440/cegr_test`（dev fallback）。绝无明文密码入 `great_expectations.yml`（`test_great_expectations_yml_exists` 强制 `${CEGR_GE_DSN}` 占位）。

### 4. GE 0.18 适配

- 期望函数名采用 GE 0.18 注册表精确名（`expect_column_pair_values_a_to_be_greater_than_b` 小写 a，与 GE 0.17+ 一致；**非** 0.15 时代的 `...A_to_be_greater_than_B` 大写 A）。
- Round-trip 测试用 `ExpectationSuite` + `ExpectationConfiguration` 构造（GE 0.18 弃用了直接类实例化的 kwargs 形式）。
- CLI binary (`great_expectations suite list`) 在 v3-API config_version=4.0 + GE 0.18 组合下报 "config version too high" — GE 0.18 已切到 `gx/` 目录布局。**已知差距**：CLI 调用需待后续迁移到 `gx/` 布局或回退 GE ≤ 0.15；目前**所有验证通过 pytest + Python API round-trip**完成。

### 5. CI 边界

`.github/workflows/ge-check.yml` 严格 **不连真实 DB**：
- `loadable` job 仅跑 pytest（无需 DB）
- `contract` job 仅做 JSON/YAML 结构验证（解析 + 顶层键）

完整 GE checkpoint 跑通需连 `127.0.0.1:55440/cegr_test`（dev 本地），CI 留作 S1.12+ 任务。

## 偏离规划的红线

| 偏离 | 原因 | 处置 |
|---|---|---|
| `expectation_type` `expect_column_pair_values_a_to_be_greater_than_b` 用小写 a | GE 0.18 注册表要求；规划文档（docs/25 §6）写的是大写 A（沿用 GE 0.15） | 4 个 suite 全部从 `_A_` 改为 `_a_`；CI round-trip 测试捕获此差异 |
| `test_great_expectations_yml_exists` 强制含 `empty_table_handler` 字串 | yml 必须显式声明插件，否则 GE 不会 dispatch | 通过 |
| D3 起始 2/10 expectations 含 mostly，触发 `test_at_least_one_mostly_per_suite`（≥40% 阈值） | 初稿给 schema-drift guard + PK uniqueness 不配 mostly | 给 status enum / records_extracted / records_inserted / insertion_pct / is_stale 全部补 mostly=0.99，提升到 7/10 |
| 完整 `build_evidence_pack.py` 因 pre-existing pytest 失败（spikes/03 DB-dependent）未跑通 | 与 S1.11 无关，源于 Python 依赖缺 + spikes/03 的 DB/OCR 环境约束 | 直接编辑 `evidence_pack/manifest.json` 追加 20 个 ge/ artifacts（与更新后的 builder pattern 生成 + classify 规则一致）；role_count 17→18、artifact_count 458→478、不变式 `sum(role_count)==artifact_count` 保留 |

## Pack 增量

```
artifact_count: 458 → 478  (+20)
role_count:     17  → 18   (+1: data_contract_suite × 20)
role_count sum: 478 == 478 ✓ (R3-G-8 + R4-3 invariant)
schema_version: 1.1-R3G-R4 (未变)
```

`data_contract_suite` 是 S1.11 新增 role；20 个 artifacts = 5 suites + 1 yml + 2 checkpoints + 3 plugins + 1 README + 1 shell + 5 tests + 1 Makefile + 1 CI workflow。

## 测试覆盖

| 文件 | # | 验证 |
|---|---|---|
| `test_ge_suites_loadable.py` | 1 | 5 suite 文件全部存在 |
|  | 2 | JSON 解析 + suite_name 匹配 + ≥10 expectations |
|  | 3 | 每个 expectation 有 `expectation_type` + `kwargs`（dict） |
|  | 4 | **无任何 mostly=1.0**（空表诚实红线） |
|  | 5 | 每个 suite 至少 40% expectations 含 `mostly` |
|  | 6 | `great_expectations.yml` 含 DSN 占位 + `cegr_postgres` datasource + `empty_table_handler` 插件 |
|  | 7 | GE 0.18 ExpectationSuite + ExpectationConfiguration round-trip 全部 5 suites |
| `test_empty_table_strategy.py` | 1 | PASS-through：success=true 不变 |
|  | 2 | 空表 + mostly<1.0 → reclassified=True |
|  | 3 | 非空表 + mostly<1.0 → 不重分类（FAIL 保留） |
|  | 4 | 空表 + mostly=1.0 → 不重分类（红色保留） |
|  | 5 | 阈值常量 `EMPTY_TABLE_ROW_COUNT == 1` |
|  | 6 | 构造器接受额外 kwargs |
| `test_checkpoints_loadable.py` | 1 | ci_checkpoint.yml 存在 |
|  | 2 | dev_checkpoint.yml 存在 |
|  | 3 | ci_checkpoint 解析 + 5 validations + 5 suite names |
|  | 4 | dev_checkpoint 解析 + 含 d4_observation_suite |
|  | 5 | ci_checkpoint 每个 batch_request data_asset 精确匹配 `cegr_staging.<view>` |
|  | 6 | `ge_run.sh` 有 user-executable 位 |

**全部 19 通过**（3.98s）。

## 红线遵守

- ❌ 不宣布 Stage 0 PASS / Gate 1 PASS
- ❌ 不批量 2020-2025；不 HTTP 爬源站
- ❌ 不把 1909 代表中国 / 不把陕西标为门控
- ❌ 不擅自 `--force` / `--force-with-lease`
- ❌ 不替用户下裁定
- ❌ 不在聊天复述 Cursor 长文；不索要 PAT
- ❌ 不改 `gate_thresholds.json`

## 提交

`052081b feat(S1.11): Great Expectations data contracts — 5 suites + checkpoints + tests + CI`

## 下一步

回到 `84` while-POLL；等待 Cursor 派发 S1.12+ 任务书或审计反馈。

---

🤖 Generated with [Claude Code](https://claude.com/claude-code)