# 37 — Stage 2 / S2.2 / policy_document 规划

> 起草：CC · 2026-08-25 · queue_rev 74
> 前置：`190` S2.2 任务书；`189` S2.7-a2 PASS；`docs/04 §3.7/§3.10` policy 位；`docs/34 §3` S2.2 范围
> 本刀**仅规划**；不写生产 migration（per `190` §SCHEMA 决策 + 用户裁定 **D** 缩刀模式）

---

## 1. 目标

S2.2 是 Stage 2 「政策与承诺」维度的基础表刀。本刀完成 `policy_document` + 必要关联表的**规划文档**，不写 migration。落地刀（tasking 193+ 视 Cursor 审验再下发）将：

- 迁移 `policy_document` / `policy_target` / `policy_measure` / `government_commitment` / `commitment_progress` 至 docs/36 §2 等价字段契约
- 首批 ≤N 行手工 seed（`is_demo="true"`），不爬网批量抓政策 PDF
- 落地 dbt `stg_*` + `mart_policy_commitment`（含 `is_demo` 过滤）
- pytest 覆盖：重叠承诺合法 / 无源不入 mart / 条数上限 / `is_demo` 过滤

参考 S2.1 节奏：先 `docs/36` 规划 + Cursor 173 PASS → `174` tasking → `180` 缩刀 → `181` receipt。本文档对应 `docs/37`。

---

## 2. 表契约（per docs/04 §3.7/§3.10 + Stage 2 第六段 COMMITMENT 消费形状）

### 2.0 范围声明

| 包含 | 不包含（推后续刀） |
|---|---|
| `policy_document`（含 `full_text_tsv`）| `project_event`（S2.4）|
| `policy_target` | `budget_allocation`（S2.3）|
| `policy_measure` | `claim_evidence_link`（S2.5 之后）|
| `government_commitment` | `inference_record`（S2.5）|
| `commitment_progress` | S2.1 person 全量（用户 D 缩刀仍生效）|

### 2.1 `policy_document`（per docs/04 §3.10）

```sql
CREATE TABLE policy_document (
    id                  UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    doc_type            policy_doc_type NOT NULL,         -- 7-NPC_PLAN / 7-GOV_WORK_REPORT / ...
    title               TEXT NOT NULL,
    publisher           TEXT NOT NULL,
    publication_date    DATE NOT NULL,
    effective_date      DATE,
    expiry_date         DATE,
    document_url        TEXT,
    full_text           TEXT,
    full_text_tsv       TSVECTOR,
    summary             TEXT,                              -- docs/04 §3.7: 抽象口号在此，**不入 commitment**
    geo_entity_ids      UUID[],
    parent_policy_id    UUID REFERENCES policy_document(id),
    source_id           UUID NOT NULL REFERENCES source_document(id),
    created_at          TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
```

新增列（本刀**只规划**；落地刀 migration 009 实施）：

| 列 | 类型 | 用途 | docs/36 §2 平行 |
|---|---|---|---|
| `canonical_title` | TEXT NULL | 归一化标题（去版本/编号后缀） | person.position 同模式 |
| `title_en` | TEXT NULL | 英文渲染（国际 cross-ref） | person.position 同模式 |
| `policy_level` | TEXT NULL | enum-style: CENTRAL / PROVINCIAL / MUNICIPAL / COUNTY | position.rank_level 平行 |
| `is_standing_committee` | BOOLEAN NULL | 是否常委会决议（极少数） | position.is_standing_committee 平行 |
| `classification` | TEXT NULL | enum: PLAN / REGULATION / NOTICE / ANNOUNCEMENT / WORK_REPORT / OP_ED（per docs/04 §3.10 + 第六段消费） | — |
| `effective_year` | INTEGER NULL | 从 effective_date 提取（avoid JOIN to date_part） | — |
| `lineage` | JSONB NULL | per-row R3-E provenance: `{chain_id, source_file_sha256, source_file_url, extractor_version, is_demo}` | observation.lineage 同模式 |
| `policy_hash_canonical` | TEXT NULL | 同一篇政策的 stable 跨版本 SHA（per R12-A de-dupe） | — |

**不扩**：

- ❌ 不加 `EXCLUDE` on `(publisher, title, publication_date)` —— docs/04 §3.7 钉死不同文件版本共存合法
- ❌ 不加 FK from `policy_target.policy_document_id` 启用 ON DELETE CASCADE —— 已有 ON DELETE RESTRICT
- ❌ 不在 `policy_document` 加 `score` / `rating` / `rank` / `total_score` 任一字段 —— 红线

### 2.2 `policy_target`（per docs/04 §3.7 + §3.10 末段）

```sql
CREATE TABLE policy_target (
    id                      UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    policy_document_id      UUID NOT NULL REFERENCES policy_document(id),
    target_description      TEXT NOT NULL,
    target_indicator_id     UUID REFERENCES indicator_definition(id),
    target_value            NUMERIC,
    target_unit             TEXT,
    target_year             INTEGER,
    measurable              BOOLEAN DEFAULT TRUE,
    source_location_id      UUID REFERENCES source_location(id),
    created_at              TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
```

新增列：

| 列 | 类型 | 用途 |
|---|---|---|
| `target_value_lower` | NUMERIC NULL | 区间下限（"增长 5-7%" 下界） |
| `target_value_upper` | NUMERIC NULL | 区间上限 |
| `target_unit_canonical` | TEXT NULL | 归一化单位（avoid "亿元" vs "亿元(本币)" drift） |
| `verification_method` | TEXT NULL | enum: STATISTICAL_BULLETIN / AUDIT_REPORT / SELF_REPORT / UNKNOWN |
| `lineage` | JSONB NULL | per-row R3-E provenance |

### 2.3 `policy_measure`（per docs/04 §3.7）

```sql
CREATE TABLE policy_measure (
    id                      UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    policy_document_id      UUID NOT NULL REFERENCES policy_document(id),
    measure_description     TEXT NOT NULL,
    measure_type            TEXT,                         -- TAX / SUBSIDY / REGULATION / INVESTMENT / TALENT / ...
    target_audience         TEXT,
    source_location_id      UUID REFERENCES source_location(id),
    created_at              TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
```

新增列：

| 列 | 类型 | 用途 |
|---|---|---|
| `expected_outcome_text` | TEXT NULL | 措施期望产出（自然语言；不评分）|
| `lineage` | JSONB NULL | per-row R3-E provenance |

### 2.4 `government_commitment`（per docs/04 §3.7 可验证门槛）

```sql
CREATE TABLE government_commitment (
    id                      UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    policy_target_id        UUID REFERENCES policy_target(id),
    commitment_text         TEXT NOT NULL,
    proposer_person_id      UUID REFERENCES person(id),    -- 留 NULL: 可能集体承诺
    geo_entity_id           UUID NOT NULL REFERENCES geo_entity(id),
    commitment_date         DATE NOT NULL,
    due_date                DATE,
    status                  commitment_status NOT NULL DEFAULT 'PROPOSED',
    source_id               UUID NOT NULL REFERENCES source_document(id),
    created_at              TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
```

**钉死（per docs/04 §3.7）**：
- `commitment_text` 是**单一可验证承诺**（"三年内引进 100 家规上工业企业"），不是抽象口号
- 抽象口号写在 `policy_document.summary`，**不入 commitment 表**
- `status` 五态机（per 现有 ENUM）：`PROPOSED` → `PROMISED` → `IN_PROGRESS` → `DELIVERED` / `BROKEN` / `WITHDRAWN`
- `due_date` 可空 —— 部分承诺无明确截止

新增列：

| 列 | 类型 | 用途 |
|---|---|---|
| `commitment_text_en` | TEXT NULL | 英文承诺（国际 cross-ref） |
| `proposer_role` | TEXT NULL | 提议者职务（如"省长"）；冗余 person_id（avoid JOIN）|
| `is_measurable` | BOOLEAN NULL | 是否可量化验证（per docs/04 §3.7 门槛）|
| `measurement_basis` | TEXT NULL | enum: INDICATOR_VALUE / PROJECT_COUNT / EVENT_COUNT / SELF_DECLARED |
| `lineage` | JSONB NULL | per-row R3-E provenance |

**不扩**：

- ❌ 不加 FK `proposer_person_id` 启用 —— 当前 ON DELETE RESTRICT 已够；FK 启用 = 后续刀
- ❌ 不加 `score` / `rating` / `rank` 任一字段 —— 红线
- ❌ 不写触发器自动 `status → BROKEN`（per docs/04 §3.7）—— 留应用层 + 评审

### 2.5 `commitment_progress`（per docs/04 §3.7 时间序列）

```sql
CREATE TABLE commitment_progress (
    id                  UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    commitment_id       UUID NOT NULL REFERENCES government_commitment(id),
    progress_date       DATE NOT NULL,
    progress_value      NUMERIC,
    progress_unit       TEXT,
    progress_note       TEXT,
    source_id           UUID NOT NULL REFERENCES source_document(id),
    created_at          TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
```

**钉死（per docs/04 §3.7 + §3.8 末段）**：
- append-only：状态变化需要时序溯源，**不**覆盖历史记录
- `progress_value` 可空 —— 部分承诺仅文字汇报（"已开工"）

新增列：

| 列 | 类型 | 用途 |
|---|---|---|
| `progress_value_lower` | NUMERIC NULL | 区间下限 |
| `progress_value_upper` | NUMERIC NULL | 区间上限 |
| `lineage` | JSONB NULL | per-row R3-E provenance |

---

## 3. dbt staging candidate 路径（per docs/19 §S1.19 + S2.1 §3 平行）

### 3.1 sources（`_stg_sources.yml`）

新增 5 条：

```yaml
sources:
  - name: cegr
    tables:
      - name: policy_document
        columns: [id, doc_type, title, publisher, publication_date, effective_date,
                  expiry_date, document_url, full_text, summary, geo_entity_ids,
                  parent_policy_id, source_id, created_at,
                  canonical_title, title_en, policy_level, is_standing_committee,
                  classification, effective_year, lineage, policy_hash_canonical]
      - name: policy_target
        columns: [... + target_value_lower, target_value_upper,
                  target_unit_canonical, verification_method, lineage]
      - name: policy_measure
        columns: [... + expected_outcome_text, lineage]
      - name: government_commitment
        columns: [... + commitment_text_en, proposer_role, is_measurable,
                  measurement_basis, lineage]
      - name: commitment_progress
        columns: [... + progress_value_lower, progress_value_upper, lineage]
```

### 3.2 staging models（per `dbt/models/staging/stg_observation.sql` 模式）

| 模型 | 备注 |
|---|---|
| `stg_policy_document.sql` | passthrough + JOIN policy_doc_type enum metadata；expose `is_demo` from lineage |
| `stg_policy_target.sql` | passthrough + JOIN indicator_definition for indicator_canonical |
| `stg_policy_measure.sql` | passthrough；expose measure_type |
| `stg_government_commitment.sql` | passthrough + JOIN geo_entity for `geo_canonical_name`；expose `status` |
| `stg_commitment_progress.sql` | passthrough + JOIN government_commitment for `commitment_text` |

全部使用：
```sql
{{ config(materialized='view', tags=['staging', 'policy']) }}
```

### 3.3 mart（不**直接**改既有 mart）

新建 `mart_policy_commitment`（仿 S2.1 §3 mart_person_tenure）：

```sql
{{ config(materialized='view', tags=['mart', 'policy']) }}

SELECT
    gc.commitment_id,
    gc.commitment_text,
    gc.commitment_text_en,
    gc.proposer_person_id,
    gc.proposer_role,
    gc.geo_entity_id,
    g.canonical_name AS geo_canonical_name,
    gc.commitment_date,
    gc.due_date,
    gc.status,
    gc.is_measurable,
    gc.measurement_basis,
    pd.policy_document_id,
    pd.title AS policy_title,
    pd.canonical_title,
    pd.classification,
    pd.policy_level,
    pt.policy_target_id,
    pt.target_description,
    pt.target_value,
    pt.target_value_lower,
    pt.target_value_upper,
    pt.target_unit_canonical,
    pt.target_year,
    pt.verification_method,
    COALESCE(gc.lineage->>'is_demo', 'false') AS is_demo
FROM {{ ref('stg_government_commitment') }} gc
JOIN {{ ref('stg_policy_document') }} pd  ON pd.policy_document_id = gc.policy_document_id  -- via policy_target
LEFT JOIN {{ ref('stg_policy_target') }} pt ON pt.policy_target_id = gc.policy_target_id
LEFT JOIN {{ ref('stg_geo_entity') }} g   ON g.geo_entity_id = gc.geo_entity_id
```

`is_demo` 显式暴露为最后一列（per docs/33 §3.2 sentinel + S2.1 mart 同模式）。

---

## 4. 首批入库策略

### 4.1 来源（per `92` §1.1 R4 + 190 §SCHEMA）

| 来源 | 类型 | 红线 |
|---|---|---|
| 公开政策 PDF | 国务院 / 省委 / 省政府门户 | **不**批量爬 2020-2025；首批 ≤10 政策 |
| 用户上传 | S2.0.2 admin_upload (Stage 1 §1.3.1) | 仅在 admin 角色提交；audit trail 写入 |
| 手工 seed | hand-curated JSON（per S1.12 + S2.1.7-a 平行） | `is_demo="true"`；不爬网 |

### 4.2 条数上限（首批 ≤N）

| 表 | 上限 | 理由 |
|---|---|---|
| `policy_document` | ≤10 | 1 政策 = 1 文件；演示 ≥3 国家级 + ≥3 省级 + ≥1 地方 |
| `policy_target` | ≤30 | 平均每政策 3 个量化目标 |
| `policy_measure` | ≤30 | 平均每政策 3 个具体措施 |
| `government_commitment` | ≤20 | 首批 = 20 条可验证承诺（per docs/04 §3.7 门槛严） |
| `commitment_progress` | ≤40 | 平均每承诺 2 条进度更新 |

### 4.3 `is_demo` 全 true（per S1.18 sentinel + S2.1 §4.3 平行）

| 字段 | 值 |
|---|---|
| `policy_document.lineage->>'is_demo'` | `"true"` |
| `policy_target.lineage->>'is_demo'` | `"true"` |
| `policy_measure.lineage->>'is_demo'` | `"true"` |
| `government_commitment.lineage->>'is_demo'` | `"true"` |
| `commitment_progress.lineage->>'is_demo'` | `"true"` |
| `source_file_sha256` | `"0"` × 64（per docs/33 §3.1） |
| `source_file_url` | `"(DEMO_SEED_NO_FILE)"` |

### 4.4 稳定 UUID（per S1.12 + S2.1 §4.4 平行）

`a0000000-0000-0000-0000-00000000006X` 家族（X = 0..9 + a..z）。

### 4.5 seed 文件

`data/seeds/policy_commitment_demo.json` + `scripts/seed_policy_commitment_demo.py`（mirror `scripts/seed_jiangsu_gdp_demo.py` + `scripts/seed_person_tenure_s21lite.py`）。

---

## 5. 与 S2.7 六段 COMMITMENT 消费对照

### 5.1 `mart_policy_commitment` → `COMMITMENT` 段（per docs/06 §2.7 + S2.7-a mock）

| mart 列 | EvidenceChain 段消费字段 | 备注 |
|---|---|---|
| `commitment_text` | `items[].title` | 短文本直显 |
| `commitment_text_en` | `items[].title_en`（**新增**）| 仅国际 cross-ref 展示 |
| `proposer_role` | `items[].actor_role`（**新增**字段 in EvidenceChain）| 后续刀 |
| `geo_canonical_name` | `items[].geo` | |
| `due_date` | `items[].due_date` | |
| `status` | `items[].status_badge` | 五态映射 |
| `policy_title` | `items[].source_label` | "MOCK · 政策文件标题" |
| `target_value` + `target_unit_canonical` | `items[].target_display` | "增长 5% GDP" |
| `lineage->>'is_demo'` | items 整体加 `is_demo=true` 角标 | S1.18 sentinel |

### 5.2 不接 S2.7-b（per 187 §SCHEMA 禁 + 190 §SCHEMA 禁）

本刀 S2.2-lite（落地刀）**不接** S2.7 COMMITMENT 段。留给 S2.7-b 协同 knife：消费 `mart_policy_commitment`，写入 EvidenceChain。

### 5.3 验证（落地刀）

```bash
# 1. mart 行数 ≥1
PGPASSWORD=postgres psql -h 127.0.0.1 -p 55440 -U postgres -d cegr_test \
    -c "SELECT COUNT(*) FROM cegr_staging.mart_policy_commitment WHERE is_demo = 'true';"
# 预期: ≥1

# 2. mart 暴露 is_demo 列
PGPASSWORD=postgres psql ... \
    -c "SELECT column_name FROM information_schema.columns WHERE table_schema = 'cegr_staging' AND table_name = 'mart_policy_commitment' AND column_name = 'is_demo';"
# 预期: 1 行

# 3. is_demo 过滤（per docs/33 §3.3 case 4）
PGPASSWORD=postgres psql ... \
    -c "SELECT COUNT(*) FROM cegr_staging.mart_policy_commitment WHERE is_demo = 'false';"
# 预期: 0（仅 demo 数据）
```

---

## 6. 验收清单

| # | 项 | 落地刀验证方式 |
|---|---|---|
| 1 | 5 张表 + docs/04 §3.7 字段 + §2 新增列齐全 | `\d cegr.policy_document` 等 |
| 2 | dbt run `--select stg_policy+` exit 0；5 stg + 1 mart 创建 | dbt run log |
| 3 | mart 行数 = seed 行数（is_demo=true 过滤后）| SQL COUNT |
| 4 | 既有 38 schema_negative 测试仍绿 | pytest tests/test_schema_negative.py -q |
| 5 | 新增 pytest tests/test_policy_commitment_s22lite.py ≥8 cases 全过 | pytest -v |
| 6 | pack invariant 521 → 521+N | JSON 解析守门 |
| 7 | smoke-check 仍 PASS（无 frontend 改动）| python3 frontend/smoke-check.py |
| 8 | 既有 S2.7-a2 + S2.1-lite 套件仍绿 | pytest tests/test_evidence_chain_s27a.py tests/test_person_tenure_s21lite.py |

---

## 7. 关键风险与回滚

| 风险 | 触发条件 | 回滚策略 |
|---|---|---|
| 既有 `policy_doc_tsv` 触发器（per docs/04 §3.10）与新列冲突 | trigger 触发 `full_text_tsv` 时新列缺值 | migration 009 仅 ADD COLUMN IF NOT EXISTS；trigger 不动 |
| `policy_target.target_indicator_id` FK NULL 与下游 JOIN 失败 | 历史上目标未关联 indicator | LEFT JOIN in mart；not INNER |
| `government_commitment.proposer_person_id` 启用 FK 后违反 | S2.1 person 未入库 | migration 009 不启用 FK；S2.1-full 之后 010+ 启用 |
| `full_text_tsv` 中文检索 `simple` 配置弱 | 政策全文搜索漏召回 | per docs/04 §3.10 已知；Stage 2 jieba 字典**后**处理 |
| `commitment_status` ENUM 与 docs/04 §3.7 五态不一致 | ENUM 修改必须 ALTER TYPE | 落地刀不动 ENUM；新增态 = 010+ |

---

## 8. 不做什么（本刀 S2.2-lite 边界；推后续刀）

| ❌ | 推到 |
|---|---|
| ❌ 写生产 migration 008 / 009 / 010（**仅规划**）| S2.2 落地刀（tasking 193+）|
| ❌ dbt stg_* + mart_policy_commitment | S2.2 落地刀 |
| ❌ 首批 ≤10 policy_document 真实 seed | S2.2 落地刀（**严禁爬网**）|
| ❌ 接 S2.7-b COMMITMENT 段消费 | S2.7-b 协同刀 |
| ❌ S2.1 person 全量（用户 D 缩刀）| 后续刀待用户裁定 |
| ❌ `claim_evidence_link`（S2.5 末段）| S2.5 |
| ❌ `score` / `rating` / `rank` / `total_score` 任一字段 | 红线 |
| ❌ 触发器自动 `status → BROKEN` | 应用层 + Gate 评审 |
| ❌ 修改 `gate_thresholds.json` | spike-04 评测构件，只读 |
| ❌ 批量爬 2020-2025 政策 PDF | 红线 |
| ❌ 启用 pgvector / RLS / partition | Stage 2 边界（per docs/04 §6）|
| ❌ 修改 `00-CC-CURRENT.md` | Cursor 拥有 |

---

## 9. 与现有文档的关系

| 引用 | 用途 |
|---|---|
| `docs/04-data-model.md` §3.7 | commitment 可验证门槛 |
| `docs/04-data-model.md` §3.8 | 五态机思路（project；commitment 沿用）|
| `docs/04-data-model.md` §3.10 | `policy_document.full_text_tsv` |
| `docs/06-governance-observation-method.md` §2.7 | 六段 COMMITMENT 消费形状 |
| `docs/19-stage1-s19-dbt-staging-plan-20260825.md` | dbt staging 模式 |
| `docs/33-stage1-s18-demo-sha-lock-plan-20260825.md` §3.1 / §3.3 | `is_demo` sentinel + 评测基线 |
| `docs/34-stage2-s20-kickoff-plan-20260825.md` §3 | S2.2 范围 + 阻塞 OCR |
| `docs/36-stage2-s21-person-tenure-plan-20260825.md` | S2.1 平行规划（风格基线）|
| `docs/04` §2 | 6 表命名 `government_commitment` 而非 `commitment`（**命名对齐**）|

---

## 10. CC 建议（供 Cursor 审阅 / 用户裁定）

### 10.1 命名对齐建议（低风险）

`docs/36` §2.2 沿用 `person_name_alias` 而非 `person_alias`（per 186 §1 备注）。本刀 §2.4 钉死 `government_commitment`（保持 docs/04 原命名）；**不**建议改名为 `commitment`。

### 10.2 全 `is_demo` vs 部分 `is_demo`

| 选项 | 描述 | 选 |
|---|---|---|
| A | 首批**全** `is_demo="true"`（per S1.18 / S2.1 §4.3 平行；最简单）| **推荐** |
| B | 首批混合（部分 demo + 部分真实）| 复杂；需两条 ingest 路径 |

### 10.3 `commitment_text_en` 是否必填

| 选项 | 描述 | 选 |
|---|---|---|
| A | nullable TEXT；落到 mart 时 LEFT JOIN 缺失语言 fallback | **推荐** |
| B | required NOT NULL；首批 seed 必须含 EN | 工作量大；首批演示会卡 |

### 10.4 mart 物化策略

| 选项 | 描述 | 选 |
|---|---|---|
| A | view（per S2.1 §3 mart_person_tenure 平行）| **推荐** |
| B | incremental materialization（一旦行数 >10k）| S2.2-lite 不达触发点 |

### 10.5 `policy_level` 落 strategy

| 选项 | 描述 | 选 |
|---|---|---|
| A | enum-style TEXT（CENTRAL / PROVINCIAL / MUNICIPAL / COUNTY）| **推荐** |
| B | schema-level CHECK + ENUM type | 加固；migration 009 复杂度↑ |

---

— End of `docs/37` —

> 等待 Cursor 审验（预期 `194-stage0-cursor-s22-plan-audit-…md`）。
> 通过后下发落地任务（`195-stage2-s22-policy-impl-tasking-…md`），进入 S2.2-lite 实施。
> S2.1-full 与 S2.2 落地可**并行**（不同 schema 域）；等 Cursor 裁定。