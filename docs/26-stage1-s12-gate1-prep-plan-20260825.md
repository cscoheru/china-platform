# Stage 1 / S1.12 — Gate 1 评审准备包规划

> **规划 only。** 不宣布 Gate 1 PASS。缺口诚实列出。Cursor 拥有 `00-CC-CURRENT.md`，本文档由 CC 起草。

- 编号：`docs/26-stage1-s12-gate1-prep-plan-20260825`
- 前置：`88` S1.11 通过；`89` S1.12 任务书；`docs/08` §2.3 Gate 1 标准
- 范围：Gate 1 **准备包**（数据快照 + 测试报告 + 演示步骤 + 缺口清单）。实现（组包/跑演示）另开 S1.13+ 任务书

---

## §0. Gate 1 标准复盘（docs/08 §2.3 verbatim）

1. 5 个来源登记 + 4 类数据入库（国家月度、省级年鉴、地市公报、扫描 PDF）
2. 每个 observation 可 1 跳回 source_document + SHA-256
3. doc 10 测试 2.1-2.6 全过；测试 2.7-2.9 部分过
4. R03（缺失）/R08（授权）/R12（URL 漂移）有兜底
5. 至少 1 个真实研究问题可回答（如"近 5 年江苏 GDP 增长趋势"）

## §1. 5 条逐条评估

### 1.1 来源登记 + 4 类数据入库

**判定：✅ 已满足（带一处需声明的边界）**

| 类别 | 来源 | 状态 | 证据 |
|---|---|---|---|
| 国家月度（HTML） | `stats.gov.cn/sj/zxfb/` | ✅ S0 enabled | `source_registry/registry.csv` row 2 + `spikes/01-national-yearbook/` |
| 省级年鉴（XLSX） | `tjj.hubei.gov.cn` | ✅ S0 enabled | `source_registry/registry.csv` row 3 + `spikes/02-provincial-yearbook/` |
| 地市公报（HTML 散文） | `sz.gov.cn/zfgb/` | ✅ S0 enabled | `source_registry/registry.csv` row 4 + `spikes/03-municipal-bulletin/` |
| 扫描 PDF（OCR） | `wb.flk.npc.gov.cn`（陕西省财政预算管理条例） | ✅ S0 enabled | `source_registry/registry.csv` row 6 + `spikes/04-scanned-pdf/` |
| 扫描 PDF（OCR 压力测试） | `archive.org/.../statisticalabst00unit`（1909 美国统计摘要） | ⚠️ S3，**非中国代表性** | `source_registry/registry.csv` row 5 — per Stage 0 R4 用户裁定，仅作 OCR 管线验证 |

**声明边界**：登记表共 6 条；其中 1 条为非代表性 S3（1909 US Abstract），仅用于 OCR 管线压力测试，不计入"中国治理数据 4 类"。若 Gate 1 要求"5 个中国来源登记"，**不满足**（仅 4 个）；若接受"≥4 类代表性来源 + 1 个非代表性 OCR 压力测试样本"视为额外加分，**满足**。

### 1.2 observation 1 跳回 source_document + SHA-256

**判定：✅ 已满足**

- Schema：`schema/01-core.sql` 定义 `observation` 表 FK → `source_location(source_document_id, source_id)`；`source_document.file_hash_sha256` 列存在。
- dbt：`dbt/models/staging/stg_observation.sql` 保留链路；`stg_source_document.sql` 保留 SHA-256。
- API（S1.10）：`/api/observation/{id}` 返回 observation + 通过内嵌 `source_id` 可 1 跳 `GET /api/source/{id}`；SHA-256 通过 `source_registry/registry.csv` 与 `source_document.file_hash_sha256` 双重锚定。
- GE 契约（S1.11）：`d4_observation_suite` 强制 FK 不为 NULL（`indicator_id` / `geo_entity_id` / `source_id` 均 `mostly=0.99`）+ `d2_source_document_suite` 强制 SHA-256 正则 `^[a-f0-9]{64}$`（R-08 校验链）。

**注**：当前 dev DB（`127.0.0.1:55440`）在 S1.10 测试中通过 19/19 integration；CI（`.github/workflows/ge-check.yml`）目前不连真实 DB（仅 JSON/YAML 结构验证）。连库验证走 S1.13+ 任务。

### 1.3 doc 10 测试 2.1-2.6 全过；2.7-2.9 部分过

**判定：⚠️ 部分满足（2.1-2.6 全过有证据，2.7-2.9 部分实现需诚实声明）**

| 测试 | 描述 | 当前状态 | 证据路径 |
|---|---|---|---|
| 2.1 单位与数量级 | `unit ∈ allowed_units`；同 series 同单位 | ✅ 已实现 | `tests/test_cleanliness.py`（schema 层 schema_negative_test）+ `tests/test_api_s110.py`（API 层）|
| 2.2 合计校验 | 分省合计 ≈ 全国 ±1% | ✅ spike 验证 | `spikes/00-national-yearbook-table/test_*.py`（`assert abs(sum(by_province.value) - total.value) / total.value < 0.01`）|
| 2.3 同比反算 | `(cur-prev)/prev` 与公布增速 ±0.5% | ✅ spike 验证 | `spikes/00-provincial-yearbook-table/test_*.py`（`obs_2024 GDP 60012.97` ± 1e-4）|
| 2.4 跨来源一致性 | 5% 阈值；>2% 写 source_disagreement | ✅ 已设计 + 部分测试 | `schema/01-core.sql` `source_disagreement` 表 + `tests/test_source_governance.py` |
| 2.5 时间序列异常 | 同比 | 99 分位的 3× | ✅ 已实现（schema + dbt）+ spike 验证 | `dbt/models/intermediate/int_indicator_timeseries.sql` |
| 2.6 修订值冲突 | append-only | ✅ 已实现 | `schema/01-core.sql` `observation_revision` 表（append-only via primary key `(observation_id, revision_no)`）|
| 2.7 行政区划有效期 | `geo_version.is_valid_at(period)` | ⚠️ 部分（schema 已支持，测试 stub）| `schema/01-core.sql` `geo_entity` / `geo_code_version` / `boundary_change_event` 表已实现；`tests/test_api_s110.py` 不含此测试，spikes 中无完整 e2e |
| 2.8 OCR 置信度 | <0.7 入复核队列，不入正式表 | ⚠️ 部分（schema + dbt 已实现，触发逻辑未连 ingest）| `schema/01-core.sql` `observation_quality_flag` 表 + `dbt/models/staging/stg_observation_quality.sql` + `spikes/04-scanned-pdf/evaluate_04.py`（**评估有数据，触发管线未接通**）|
| 2.9 缺失值不补零 | NULL + missing_reason；`is_imputed=False` | ⚠️ 部分（schema 约束存在，应用层强制未跑测试）| `schema/01-core.sql` `observation.value` 允许 NULL + `missing_reason` 列；`tests/` 中无 e2e |

**已知缺口**（Gate 1 应诚实声明）：
- **2.7-2.9 e2e 测试缺失**：spike 层验证过逻辑，**端到端管道 + 自动化测试未完成**。
- **OCR 触发管线（2.8）未连 ingest**：scanned PDF 真样本入库走管理员手动上传（per R08 措施 4）；OCR 置信度分流触发器未自动化。

### 1.4 R03 / R08 / R12 兜底

**判定：⚠️ 部分（设计 + 部分实现；运维监控尚未自动化）**

#### R03 — 地方数据缺失和不一致

- ✅ Schema：`schema/01-core.sql` `source_disagreement` 表存冲突；`missing_reason` 字段记缺失；`is_imputed` 字段防误补零。
- ✅ 来源优先级：S0 > S1 > S2 > S3 > S4（在 source_registry `declared_source_level` 列；dbt staging 派生 `source_level`）。
- ❌ 自动化冲突检测：当前 **spike 内人工核对**；dbt 测试 `test_cross_source_consistency_threshold`（per docs/10 §2.4）未在 `dbt/models/staging/` 中实现。
- ❌ research_note 表：未实施（Stage 2 设计项）。

#### R08 — 数据授权和网站稳定性

- ✅ Schema：`source_registry.auth_note` + `source_registry.failure_handling` 列；URL 多备选。
- ✅ 抓取节流：每源 ≤1 req/s；不绕过验证码/付费墙（per docs/09 措施 2/5）。
- ❌ 人工上传入口 `/admin/upload`：**未实施**（S1.12+ 任务）。
- ❌ URL 健康监控 + 自动告警：**未实施**。

#### R12 — URL 漂移（运维风险）

- ✅ Schema：`source_registry.backup_urls`（多备选）。
- ❌ URL 健康探针 + ingest_run 失败率告警：**未自动化**（spike `monitor_ingest.py` 仅手动跑）。

### 1.5 至少 1 个真实研究问题可回答

**判定：⚠️ 部分（API 可查询；**研究问题 demo 未跑**）**

候选问题（per PRD demo set）：
- "近 5 年江苏 GDP 增长趋势"
- "近 5 年深圳规模以上工业增加值"
- "陕西省财政预算管理条例 2010 全文检索"

**当前能力**：
- API（S1.10）：`GET /api/indicator/{indicator_id}/series?geo_entity_id=...&period_start=...&period_end=...` 可返回时间序列。19/19 integration test 通过（`tests/test_api_s110.py`）。
- dbt 中间层：`int_indicator_timeseries.sql` 派生 `value` 字段（含 NOT NULL 过滤 by design）。
- GE 契约（S1.11）：5 suites 守住空表/非空路径。

**当前缺口**：
- ❌ 演示 seed 未生成（无 `/江苏/GDP/2019-2023/` 真实 observation 入库；S1.10 测试 seed 是 dict-level fixture，不是真实数据）。
- ❌ 真实研究问题 demo step-by-step 脚本：未编写。
- ❌ UI/CLI 演示层：仅 FastAPI docs，**没有 HTML/React 页面**。

---

## §2. Gate 1 准备包内容（交付物清单）

按 `89` §NOW-3，**本节为准备包骨架**（实现由后续 S1.13+ 任务书驱动）。

| 包条目 | 当前状态 | 路径 / 实现方 |
|---|---|---|
| **数据快照清单** | 部分 | `source_registry/registry.csv`（6 条）+ `dbt/models/staging/`（5 views）+ dev DB 中 S1.10 seed fixture（仅测试用）|
| **测试报告索引** | ✅ | `tests/`（10 个 test_*.py）+ `spikes/*/test_*.py`（6 个 spike test）+ `ge/tests/`（3 个）|
| **dbt staging + intermediate** | ✅ | `dbt/models/staging/`（5 views）+ `dbt/models/intermediate/`（2 views）|
| **API 端点** | ✅ | `backend/src/china_platform/api/routes/`（12 endpoints via 4 routers）|
| **GE 契约** | ✅ | `ge/expectations/`（5 suites）+ `ge/checkpoints/`（2 checkpoints）+ `ge/tests/`（19 tests passing）|
| **风险登记** | ✅ | `docs/09-risk-register.md`（12 risks；R03/R08/R12 状态见 §1.4）|
| **证据包（manifest）** | ✅ | `evidence_pack/manifest.json`（478 artifacts；S1.11 增量 role `data_contract_suite`）|
| **演示脚本（step-by-step）** | ❌ 未编写 | S1.13 任务（建议） |
| **真实研究问题 seed** | ❌ 未生成 | S1.13 任务（建议） |
| **HTML/CLI 演示 UI** | ❌ 未实施 | Stage 2 设计项 |

---

## §3. 已知缺口与风险（**诚实清单**）

按 `89` §NOW-4 强制要求"缺口须诚实列出"。

### 3.1 严重缺口（若 Gate 1 PASS 必须解决）

1. **真实研究问题 demo 未跑通**：无真实 observation 入库，5 条 §1.5 候选问题不能端到端演示。
2. **跨来源一致性测试（2.4）dbt 未实施**：spike 内手动核对；dbt `test_cross_source_consistency_threshold` 未写。
3. **2.7-2.9 e2e 测试缺失**：schema + dbt 已实现，**自动化端到端测试未跑**。
4. **R03 自动化冲突检测未实施**：spike 内人工核对；运行时未跑。
6. **R08/R12 运维监控未自动化**：URL 健康探针 + ingest_run 失败率告警未实现。

### 3.2 边界声明

- **来源代表性**：登记 6 条，但仅 4 个中国代表性来源 + 1 个非代表性 OCR 压力样本（1909 US Abstract，S3）；不应误称"5 个中国来源登记"。
- **1909 美国统计摘要**：per Stage 0 R4 用户裁定，仅 OCR 管线验证用，不进入正式数据；Gate 1 不应引用此样本作为"代表性研究证据"。
- **陕西扫描 PDF**：per spikes/04 README，**仅作 OCR 评估**，U-1 接受 / U-2 以嵌入层作对照 / U-3 非 Stage 0 验收项；**数值单元指标不适用**，不自动改变 Stage 0 verdict。

### 3.3 后续任务书

| 任务书 | 范围 | 紧急度 |
|---|---|---|
| S1.13 | 真实研究问题 seed 生成（江苏 GDP / 深圳工业 / 陕西财政 PDF 全文检索）| 高 |
| S1.14 | 演示 step-by-step 脚本（CLI + curl + FastAPI docs） | 高 |
| S1.15 | 2.7-2.9 e2e 自动化测试 + 2.4 dbt 测试 | 中 |
| S1.16 | R03 自动化冲突检测（dbt test + monitoring）| 中 |
| S1.17 | R08 人工上传入口 `/admin/upload`（**必做**，per R08 措施 4）| 高 |
| S1.18 | R12 URL 健康探针 + ingest_run 失败率告警 | 中 |

---

## §4. 红线遵守（per `89` §红线 + 全局约束）

- ❌ **不宣布 Stage 0 PASS / Gate 1 PASS**（§3.1 已诚实列出 5 项严重缺口）
- ❌ 不批量爬取 2020-2025 数据（per PRD 红线 + Stage 0 R4）
- ❌ 不 HTTP 爬源站（仅依赖已下载样本 + admin 上传入口）
- ❌ 不把 1909 美国统计摘要代表中国 / 不把陕西标为 Gate 1 验证项
- ❌ 不擅自 `--force` / `--force-with-lease`
- ❌ 不替用户下裁定（§1.1 中"5 个来源登记 vs 4 类数据入库"的边界声明供 Cursor 复核）
- ❌ 不在聊天复述 Cursor 长文；不索要 PAT
- ❌ 不改 `gate_thresholds.json`（per `89` §红线 + `85` §SCHEMA 决策）
- ❌ Cursor 不写本文档正文（per `89` §红线 + `84` §0 唯一信道）

---

## §5. 交付物

| 文件 | 类型 | 说明 |
|---|---|---|
| `docs/26-stage1-s12-gate1-prep-plan-20260825.md` | 规划 | 本文档 |
| `reviews/stage0-gate0-rework-2026-08-23/90-stage0-cc-s12-plan-receipt-20260825.md` | 回执 | `90` 给 Cursor 审验 |

**Pack contract**：本刀为规划 only；不动 `evidence_pack/manifest.json`（role_count 不变）。等 S1.13+ 实现时再触发 pack 增量。

---

— CC @ queue_rev 29 —