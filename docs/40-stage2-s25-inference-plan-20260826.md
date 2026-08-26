# 40 — Stage 2 / S2.5 / inference_record + claim_evidence_link 规划

> 起草：CC · 2026-08-26 · queue_rev 88
> 前置：`222` S2.4-lite PASS；`223` S2.5 任务书；`docs/04` §2 ERD 推断段 + §3.1/§3.9；`docs/06` §2.7 / §4 / §6 / §7 推断与展示纪律；`docs/34` §4 序 9
> 本刀**仅规划**；不写生产 migration（per `223` §SCHEMA + 用户裁定 **D** 缩刀模式）

---

## 1. 目标

S2.5 是 Stage 2 「推断」维度的桥接表刀 — 把 Stage 1 已入库的 observation / policy / budget / project 行**接驳到六段证据链 UI** 上。本刀完成 `inference_record` + `claim_evidence_link`（最小关联）的**规划文档**，不写 migration。落地刀（tasking 224+ 视 Cursor 审验再下发）将：

- 迁移 `inference_record` + `claim_evidence_link` 至 docs/40 §2 等价字段契约（additive-only）
- 迁移 `uncertainty_record` + `research_note` 既有列（如缺）至本规划 §2.3/§2.4 钉死的最小列集
- 首批 ≤N 行手工 seed（`is_demo="true"`），不爬网
- 落地 dbt `stg_inference_record` + `stg_claim_evidence_link` + `mart_inference_record`（含 `is_demo` 过滤 + layer ENUM 投影）
- pytest 覆盖：layer ≠ FACT 守门 / 置信度 [0, 1] 守门 / polarity SUPPORTS ∪ CONTRADICTS 双显守门 / `is_demo` 过滤 / 无评分字段

参考 S2.1 / S2.2 / S2.3 / S2.4 节奏：先 `docs/40` 规划 → Cursor 审验 PASS → 落地 tasking → 实施。本文档对应 `docs/40`。

---

## 2. 表契约（per docs/04 §2 ERD 推断段 + §3.1/§3.9 + schema/01-core.sql §915-969）

### 2.0 范围声明

| 包含 | 不包含（推后续刀）|
|---|---|
| `inference_record`（**主表**，layer ENUM 必 INFERENCE/DERIVED/JUDGMENT）| Gate 2 全量 UI（仅本刀 §5 接驳形状）|
| `claim_evidence_link`（**正反证据**最小关联；仅 +canonical columns）| `uncertainty_record` 加列（既有够用）|
| `research_note`（既有；`body_tsv` GIN 索引已有）| `derived_metric`（S2.5 后续刀视 Cursor 裁定）|
| 关键列 `lineage` JSONB（is_demo sentinel）| S2.1 person 全量（用户 D 缩刀仍生效）|
| `uncertainty_record`（既有；本刀**不**加列）| `score` / `rating` / `rank` / `total_score` / `confidence_score` 任一字段 — 红线 |
| `canonical_statement` / `polarity_hash` 归一化 | pgvector / RLS / partition（per docs/04 §6） |

### 2.1 `inference_record`（既有，落地刀 additive）

```sql
-- 既有 (01-core.sql §915-928)
CREATE TABLE inference_record (
    id                  UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    layer               information_layer NOT NULL,
    statement           TEXT NOT NULL,
    evidence_obs_ids    UUID[] NOT NULL,
    evidence_gaps       TEXT[],
    alternative_explanations TEXT[],
    uncertainty         TEXT,
    confidence          NUMERIC,
    created_at          TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    created_by          TEXT NOT NULL,
    CONSTRAINT inference_confidence_range CHECK (confidence IS NULL OR confidence BETWEEN 0 AND 1),
    CONSTRAINT inference_layer_not_fact CHECK (layer <> 'FACT')
);
```

新增列（本刀**只规划**；落地刀 migration 012 实施）：

| 列 | 类型 | 用途 | docs/38 §2 平行 |
|---|---|---|---|
| `canonical_statement` | TEXT NULL | 归一化陈述（去"可能"/"或许"/"据估计"漂移）| `policy_document.canonical_title` 平行 |
| `canonical_layer` | TEXT NULL | enum-style 投影：INFERENCE / DERIVED / JUDGMENT（不动 schema ENUM） | `project_event.project_class` 平行 |
| `inference_method` | TEXT NULL | enum-style: L1_TREND / L2_PEER / L3_CONDITIONAL / L4_PANEL_FE / L5_EVENT / L6_DID / L7_SYNTHETIC / OTHER | docs/06 §4 L1-L7 方法等级 |
| `inference_year` | INTEGER NULL | 推断适用年份（avoid JOIN date_part） | `project_event.status_year` 平行 |
| `lineage` | JSONB NULL | per-row R3-E provenance: `{chain_id, source_file_sha256, source_file_url, extractor_version, is_demo, methodology_version}` | 同 S2.1-S2.4 模式 |
| `inference_hash_canonical` | TEXT NULL | 同一推断跨修订 stable SHA（per R12-A de-dupe）| `project_hash_canonical` 平行 |
| `polarity_summary` | TEXT NULL | enum-style: SUPPORTED / CONTRADICTED / MIXED / UNCONTESTED | 归一化呈现 |
| `geo_entity_id` | UUID NULL FK→geo_entity(id) | 推断适用范围（per RegionCard 默认显示） | `tenure.geo_entity_id` 平行 |

**不扩**：
- ❌ 不在 `inference_record` 加 `score` / `rating` / `rank` / `total_score` / `confidence_score` 任一字段 — **红线**（per docs/06 §6.6 综合指数纪律）
- ❌ 不修改 `information_layer` ENUM —— 落地刀不动 ENUM；新增态 = 后续 013+
- ❌ 不强制 `confidence` NOT NULL —— NULL = "未量化置信度"合法
- ❌ 不写触发器自动从 evidence_obs_ids 数量推 `confidence`（per docs/04 §3.x 独立记录原则）
- ❌ 不启用 FK `evidence_obs_ids` → `observation(id)`（数组 FK；应用层守门）
- ❌ 不启用地标 `EXCLUDE` 约束
- ❌ 不在 evidence_obs_ids 上加 GIN（避免 landing 与 cost 错配；mart 端按需）

### 2.2 `claim_evidence_link`（既有，落地刀 additive）

```sql
-- 既有 (01-core.sql §956-966)
CREATE TABLE claim_evidence_link (
    id                  UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    claim_id            UUID NOT NULL,
    claim_type          TEXT NOT NULL,
    evidence_id         UUID NOT NULL,
    evidence_type       TEXT NOT NULL,
    polarity            TEXT NOT NULL,
    note                TEXT,
    created_at          TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    CONSTRAINT claim_evidence_polarity CHECK (polarity IN ('SUPPORTS','CONTRADICTS'))
);
```

新增列（本刀**只规划**；落地刀 migration 012 实施）：

| 列 | 类型 | 用途 | docs/38 §2 平行 |
|---|---|---|---|
| `canonical_polarity` | TEXT NULL | enum-style 投影：SUPPORTS / CONTRADICTS（不动 schema CHECK） | `project_event.project_class` 平行 |
| `evidence_strength` | TEXT NULL | enum-style: STRONG / MODERATE / WEAK / UNRATED — **不**数值化（per 红线）| — |
| `lineage` | JSONB NULL | per-row R3-E provenance | 同上 |
| `claim_evidence_hash_canonical` | TEXT NULL | 同一关联跨修订 stable SHA（per R12-A de-dupe）| `inference_hash_canonical` 平行 |
| `geo_entity_id` | UUID NULL FK→geo_entity(id) | 关联适用范围（UI 按区域过滤） | `tenure.geo_entity_id` 平行 |

**不扩**：
- ❌ 不在 `claim_evidence_link` 加 `score` / `rating` / `confidence_score` / `credibility_score` — **红线**
- ❌ 不修改 `polarity` CHECK 约束（SUPPORTS / CONTRADICTS 双显锁定，per docs/04 §3.9 防确认偏差）
- ❌ 不启用 FK `claim_id` / `evidence_id` → 任何具体表（应用层守门；claim/evidence 类型多样）
- ❌ 不写触发器强制 claim_id ≠ evidence_id（不同表可能同 UUID 命名空间）

### 2.3 `uncertainty_record`（既有，**不**加列）

```sql
-- 既有 (01-core.sql §932-940)
CREATE TABLE uncertainty_record (
    id                  UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    target_type         TEXT NOT NULL,
    target_id           UUID NOT NULL,
    uncertainty_type    TEXT NOT NULL,
    description         TEXT NOT NULL,
    impact_note         TEXT,
    created_at          TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
```

**钉死**（per docs/06 §2.7 + §6.6）：
- 字段集**完整够用**；不扩
- `target_type ∈ ('INFERENCE','POLICY','BUDGET','PROJECT','PERSON','CLAIM_EVIDENCE','OTHER')`（enum-style 应用层守门；不引入 schema ENUM）
- 不在 `uncertainty_record` 上挂 `is_demo` sentinel —— 通过 `target_id JOIN` 投影

### 2.4 `research_note`（既有，**不**加列）

```sql
-- 既有 (01-core.sql §942-954) — 含 body_tsv GIN 索引 + layer ENUM 投影
CREATE TABLE research_note (
    id                  UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    title               TEXT NOT NULL,
    body                TEXT NOT NULL,
    body_tsv            TSVECTOR,
    layer               information_layer NOT NULL,
    claim_evidence_ids  UUID[],
    created_at          TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at          TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    created_by          TEXT NOT NULL
);
```

**钉死**（per docs/04 §3.10 + docs/06 §6.6）：
- `body_tsv` GIN 已有；不重做
- 字段集完整；不扩
- 落地刀不写 `set_updated_at_research_note` 触发器更新 — 触发器**已存在**（per 01-core.sql §995-997）
- mart 仅 passthrough；不派生"研究笔记热度"等评分字段

### 2.5 polarity 守门与反例登记（per docs/04 §3.9 + docs/06 §6）

| 维度 | 钉死 | 来源 |
|---|---|---|
| `polarity` 必 ∈ `SUPPORTS` ∪ `CONTRADICTS` | CHECK 约束锁定；落地刀**不动** | docs/04 §3.9 |
| 每条主张**必须**至少记录一条 SUPPORTS | 应用层守门（不在 schema CHECK；否则反例可能无人登记） | docs/04 §3.9 + docs/06 §6.6 反例纪律 |
| 每条主张**至少**记录一条 CONTRADICTS（Gate 2 §3.2 硬要求）| 评审层 catch + UI 显式标注"反例登记数" | docs/34 §2 Gate 2 §3.2 |
| `evidence_strength` 仅 enum-style TEXT | 不计算"证据强度评分" | 红线 |

**关键纪律**（per docs/06 §6.6 第 1 行）：**"任何指数都必须能一键回放"** —— `claim_evidence_link` 的 `note` 字段承担这一职责，记录评估者的判定理由与数据快照。

---

## 3. dbt staging candidate 路径（per docs/19 §S1.19 + S2.1 §3 + S2.4 §3 平行）

### 3.1 sources（`_stg_sources.yml`）

新增 4 条：

```yaml
sources:
  - name: cegr
    tables:
      - name: inference_record
        columns: [id, layer, statement, evidence_obs_ids, evidence_gaps,
                  alternative_explanations, uncertainty, confidence,
                  created_at, created_by,
                  canonical_statement, canonical_layer, inference_method,
                  inference_year, lineage, inference_hash_canonical,
                  polarity_summary, geo_entity_id]
      - name: claim_evidence_link
        columns: [id, claim_id, claim_type, evidence_id, evidence_type,
                  polarity, note, created_at,
                  canonical_polarity, evidence_strength, lineage,
                  claim_evidence_hash_canonical, geo_entity_id]
      - name: uncertainty_record
        columns: [id, target_type, target_id, uncertainty_type,
                  description, impact_note, created_at]
      - name: research_note
        columns: [id, title, body, body_tsv, layer, claim_evidence_ids,
                  created_at, updated_at, created_by]
```

### 3.2 staging models（per `dbt/models/staging/stg_observation.sql` 模式）

| 模型 | 备注 |
|---|---|
| `stg_inference_record.sql` | passthrough；expose `canonical_layer` enum 文本；expose `is_demo` from lineage；JOIN geo_entity for `geo_canonical_name` |
| `stg_claim_evidence_link.sql` | passthrough；expose `canonical_polarity` enum 文本；JOIN geo_entity for `geo_canonical_name` |
| `stg_uncertainty_record.sql` | passthrough（**不**加列；按需暴露）|
| `stg_research_note.sql` | passthrough + `body_tsv` 全文检索字段暴露 |

```sql
{{ config(materialized='view', tags=['staging', 'inference']) }}
```

### 3.3 mart（仿 S2.4 §3.3 `mart_budget_execution` + S2.1 §3 `mart_person_tenure`）

新建 `mart_inference_record`：

```sql
{{ config(materialized='view', tags=['mart', 'inference']) }}

SELECT
    inf.inference_id,
    inf.layer,
    inf.canonical_layer,
    inf.statement,
    inf.canonical_statement,
    inf.inference_method,
    inf.inference_year,
    inf.confidence,
    inf.uncertainty,
    inf.evidence_obs_ids,
    inf.evidence_gaps,
    inf.alternative_explanations,
    inf.polarity_summary,
    inf.geo_entity_id,
    g.canonical_name AS geo_canonical_name,
    -- 反例计数（**仅计数**；不评分）
    (
        SELECT COUNT(*)
        FROM {{ ref('stg_claim_evidence_link') }} cel
        WHERE cel.claim_id = inf.inference_id
          AND cel.canonical_polarity = 'CONTRADICTS'
    ) AS n_contradicts,
    (
        SELECT COUNT(*)
        FROM {{ ref('stg_claim_evidence_link') }} cel
        WHERE cel.claim_id = inf.inference_id
          AND cel.canonical_polarity = 'SUPPORTS'
    ) AS n_supports,
    inf.inference_hash_canonical,
    inf.lineage AS inf_lineage,
    COALESCE(inf.lineage->>'is_demo', 'false') AS is_demo
FROM {{ ref('stg_inference_record') }} inf
LEFT JOIN {{ ref('stg_geo_entity') }} g ON g.geo_entity_id = inf.geo_entity_id
```

`is_demo` 显式暴露为最后一列（per docs/33 §3.2 sentinel + S2.1-S2.4 mart 同模式）。
**不评分**：`n_supports` / `n_contradicts` 仅计数；不派生"支持度评分""反例严重度"等数值（per 红线）。

### 3.4 反例登记 mart 辅助视图（落地刀必出）

```sql
-- mart_claim_evidence_polarity_balance（每 claim 一条；SUPPORTS / CONTRADICTS 平衡度）
CREATE OR REPLACE VIEW mart_claim_evidence_polarity_balance AS
SELECT
    cel.claim_id,
    cel.claim_type,
    COUNT(*) FILTER (WHERE cel.canonical_polarity = 'SUPPORTS')     AS n_supports,
    COUNT(*) FILTER (WHERE cel.canonical_polarity = 'CONTRADICTS') AS n_contradicts,
    CASE
        WHEN COUNT(*) FILTER (WHERE cel.canonical_polarity = 'CONTRADICTS') = 0
            THEN 'NO_CONTRADICTING_EVIDENCE'
        WHEN COUNT(*) FILTER (WHERE cel.canonical_polarity = 'SUPPORTS') = 0
            THEN 'NO_SUPPORTING_EVIDENCE'
        WHEN COUNT(*) FILTER (WHERE cel.canonical_polarity = 'SUPPORTS')
           >= COUNT(*) FILTER (WHERE cel.canonical_polarity = 'CONTRADICTS')
            THEN 'SUPPORTS_DOMINANT'
        ELSE 'CONTRADICTS_DOMINANT'
    END AS balance_status
FROM stg_claim_evidence_link cel
GROUP BY cel.claim_id, cel.claim_type;
```

**不评分**：仅枚举 `balance_status`；不计算"反例比例""证据均衡度"等派生评分（per 红线 + docs/06 §6.6 第 1 行）。

### 3.5 推断方法等级 mart 辅助视图（per docs/06 §4 L1-L7）

```sql
-- mart_inference_method_distribution（每 method 一条；纯分布计数）
CREATE OR REPLACE VIEW mart_inference_method_distribution AS
SELECT
    inf.inference_method,
    COUNT(*) AS n_records,
    COUNT(DISTINCT inf.geo_entity_id) AS n_geos,
    -- 置信度分布（**仅分布**；不评分）
    COUNT(*) FILTER (WHERE inf.confidence IS NULL)         AS n_confidence_null,
    COUNT(*) FILTER (WHERE inf.confidence < 0.5)            AS n_confidence_low,
    COUNT(*) FILTER (WHERE inf.confidence BETWEEN 0.5 AND 0.8) AS n_confidence_mid,
    COUNT(*) FILTER (WHERE inf.confidence > 0.8)            AS n_confidence_high
FROM stg_inference_record inf
WHERE inf.inference_method IS NOT NULL
GROUP BY inf.inference_method;
```

---

## 4. 首批入库策略

### 4.1 来源（per `92` §1.1 R4 + 223 §SCHEMA）

| 来源 | 类型 | 红线 |
|---|---|---|
| 公开政策研究 / 学术论文 | 期刊 / 智库 / 学术数据库 | **不**批量爬 2020-2025；首批 ≤N 行 |
| 用户上传 | S2.0.2 admin_upload (Stage 1 §1.3.1) | 仅在 admin 角色提交；audit trail 写入 |
| 手工 seed | hand-curated JSON（per S1.12 + S2.1-S2.4 平行） | `is_demo="true"`；不爬网 |
| 跨刀共享 | `inference_record.evidence_obs_ids` 引用 Stage 1 已入库 observation | 仅引用已固化行；不重新创建 observation |

### 4.2 条数上限（首批 ≤N）

| inference 行 | claim_evidence 行 | uncertainty 行 | research_note 行 | 理由 |
|---|---|---|---|---|
| ≤12 | ≤36 | ≤12 | ≤6 | 每 inference 平均 3 条证据（含 SUPPORTS / CONTRADICTS 双显）|

具体约束：

| 限制 | 上限 | 理由 |
|---|---|---|
| `inference_record` 总行数 | ≤12 | 演示 ≤4 个 layer × ≤3 个 method |
| `claim_evidence_link` 总行数 | ≤36 | ≤12 inference × ≤3 evidence |
| `uncertainty_record` 总行数 | ≤12 | 与 inference 行数对齐 |
| `research_note` 总行数 | ≤6 | 演示 < 8 维度摘要 |
| `inference_hash_canonical` 唯一值 | ≤12 | ≤12 独立推断笔 |
| `geo_entity_id` 跨 inference | ≤5 | 跨省/跨市；首批演示多 geo |
| `inference_year` 覆盖 | ≥2 | 演示跨年（2023 + 2024）|
| `polarity` 分布 SUPPORTS:CONTRADICTS | ≥ 1:1 | **反例守门**（per docs/04 §3.9）|
| `confidence` 分布 | 各档 ≤ 8 | 演示 NULL/低/中/高四档 |
| `canonical_layer` IS NULL | 0 | 守门 — 落地刀 100% 投影 |
| `inference_method` IS NULL | 0 | 守门 — 落地刀 100% 标注 |

### 4.3 `is_demo` 全 true（per S1.18 sentinel + S2.1 §4.3 / S2.2 §4.3 / S2.3 §4.3 / S2.4 §4.3 平行）

| 字段 | 值 |
|---|---|
| `inference_record.lineage->>'is_demo'` | `"true"` |
| `claim_evidence_link.lineage->>'is_demo'` | `"true"` |
| `source_file_sha256` | `"0"` × 64（per docs/33 §3.1）|
| `source_file_url` | `"(DEMO_SEED_NO_FILE)"` |

### 4.4 稳定 UUID（per S1.12 + S2.1 §4.4 / S2.4 §4.4 平行）

| 表 | UUID 家族 |
|---|---|
| `inference_record` | `a0000000-0000-0000-0000-0000000000aX`（X = 0..9 + a..z）|
| `claim_evidence_link` | `a0000000-0000-0000-0000-0000000000bX`（X = 0..9 + a..z）|
| `uncertainty_record` | `a0000000-0000-0000-0000-0000000000cX`（X = 0..9 + a..z）|
| `research_note` | `a0000000-0000-0000-0000-0000000000dX`（X = 0..9 + a..z）|
| `geo_entity`（外键）| 复用既有 demo geo_entity（per S2.3 §4.4 / S2.4 §4.4）|

### 4.5 seed 文件

- `data/seeds/inference_record_demo.json` + `scripts/seed_inference_record_demo.py`（mirror `scripts/seed_budget_execution_demo.py`）
- `data/seeds/claim_evidence_link_demo.json` + `scripts/seed_claim_evidence_link_demo.py`
- `data/seeds/uncertainty_record_demo.json` + `scripts/seed_uncertainty_record_demo.py`
- `data/seeds/research_note_demo.json` + `scripts/seed_research_note_demo.py`
- 加载顺序：`observation` (既有 Stage 1) → `inference_record` → `claim_evidence_link` → `uncertainty_record` → `research_note`（FK 依赖：evidence_obs_ids 引用既有 observation；不重写）

---

## 5. 与 S2.7 六段 PROCESS / OUTPUT + 七维度消费对照

### 5.1 `mart_inference_record` → RegionCard **顶部 INFERENCE/JUDGMENT 角标**（per docs/34 §2 Gate 2）

| mart 列 | RegionCard 字段 | 备注 |
|---|---|---|
| `canonical_layer` | `card.layer_badge` | INFERENCE = 蓝 / JUDGMENT = 橙 / DERIVED = 灰（per docs/06 §3 维度卡）|
| `inference_method` | `card.method_label` | "L3 条件化表现" / "L6 双重差分" 等（per docs/06 §4）|
| `confidence` | `card.confidence_label` | NULL → "未量化" / <0.5 → "低" / 0.5-0.8 → "中" / >0.8 → "高"（**仅展示**；不评分）|
| `n_supports` / `n_contradicts` | `card.evidence_balance` | "3 条支持 / 1 条反例"（**仅展示**；per docs/06 §6.6 一键回放）|
| `balance_status` | `card.balance_badge` | "反例缺失" / "反例登记"（per docs/04 §3.9 防确认偏差）|
| `lineage->>'is_demo'` | items 整体加 `is_demo=true` 角标 | S1.18 sentinel |

### 5.2 `mart_inference_record` → **证据链缺失提示**（per docs/06 §2.7）

| mart 列 | EvidenceChain 段消费字段 | 备注 |
|---|---|---|
| `evidence_gaps` | `items[].gap_warning[]` | 每条 gap 显示为黄色 banner "X 段未覆盖"（per docs/06 §2.7 第 2 条）|
| `alternative_explanations` | `items[].alt_explanations[]` | 折叠面板；评审层访问 |
| `uncertainty` | `items[].uncertainty_note` | 自由文本；不评分 |
| `canonical_statement` | `items[].statement_canonical`（**新增**）| 后续刀 |

### 5.3 `mart_claim_evidence_polarity_balance` → **反例登记总览**（per docs/34 §2 Gate 2 §3.2）

| mart 列 | UI 字段 | 备注 |
|---|---|---|
| `n_supports` | `evidence_panel.support_count` | 计数；不评分 |
| `n_contradicts` | `evidence_panel.contradict_count` | **Gate 2 §3.2 硬要求**至少 1 条反例显式登记 |
| `balance_status` | `evidence_panel.balance_status` | "NO_CONTRADICTING_EVIDENCE" 显红色 |

### 5.4 不接 Gate 2 全量 UI（per 223 §SCHEMA 禁）

本刀 S2.5（落地刀）**不接** Gate 2 §3.2 全量 UI 验收（属 S2.7-b / S2.10 协同刀）。本刀仅：
- 暴露 `mart_inference_record` 给前端可消费（mock 即可；不必 wire）
- 暴露 `mart_claim_evidence_polarity_balance` 给 Gate 2 §3.2 反例登记检查

### 5.5 验证（落地刀）

```bash
# 1. inference mart 行数 ≥1
PGPASSWORD=postgres psql -h 127.0.0.1 -p 55440 -U postgres -d cegr_test \
    -c "SELECT COUNT(*) FROM cegr_staging.mart_inference_record WHERE is_demo = 'true';"
# 预期: ≥1

# 2. layer 分布（必须含 INFERENCE / DERIVED / JUDGMENT；无 FACT — schema CHECK 守门）
PGPASSWORD=postgres psql ... \
    -c "SELECT canonical_layer, COUNT(*) FROM cegr_staging.mart_inference_record GROUP BY canonical_layer ORDER BY canonical_layer;"
# 预期: ≥3 行；无 FACT

# 3. 反例守门（per docs/04 §3.9 + §10.2 Gate 2）
PGPASSWORD=postgres psql ... \
    -c "SELECT COUNT(*) FROM cegr_staging.mart_claim_evidence_polarity_balance WHERE balance_status = 'NO_CONTRADICTING_EVIDENCE';"
# 预期: 0（per §4.2 守门）

# 4. polarity 分布
PGPASSWORD=postgres psql ... \
    -c "SELECT canonical_polarity, COUNT(*) FROM cegr_staging.stg_claim_evidence_link GROUP BY canonical_polarity;"
# 预期: SUPPORTS ≥ 1，CONTRADICTS ≥ 1（per §4.2）

# 5. is_demo 过滤（per docs/33 §3.3 case 4）
PGPASSWORD=postgres psql ... \
    -c "SELECT COUNT(*) FROM cegr_staging.mart_inference_record WHERE is_demo = 'false';"
# 预期: 0（仅 demo 数据）

# 6. inference_hash_canonical de-dupe
PGPASSWORD=postgres psql ... \
    -c "SELECT COUNT(DISTINCT inference_hash_canonical) FROM cegr_staging.mart_inference_record;"
# 预期: ≤12（per §4.2）

# 7. 跨年覆盖
PGPASSWORD=postgres psql ... \
    -c "SELECT COUNT(DISTINCT inference_year) FROM cegr_staging.mart_inference_record;"
# 预期: ≥2（per §4.2）

# 8. canonical_layer 100% 投影守门
PGPASSWORD=postgres psql ... \
    -c "SELECT COUNT(*) FROM cegr_staging.stg_inference_record WHERE canonical_layer IS NULL;"
# 预期: 0（per §4.2）

# 9. inference_method 100% 标注守门
PGPASSWORD=postgres psql ... \
    -c "SELECT COUNT(*) FROM cegr_staging.stg_inference_record WHERE inference_method IS NULL;"
# 预期: 0（per §4.2）

# 10. confidence 分布四档
PGPASSWORD=postgres psql ... \
    -c "SELECT
          COUNT(*) FILTER (WHERE confidence IS NULL) AS n_null,
          COUNT(*) FILTER (WHERE confidence < 0.5) AS n_low,
          COUNT(*) FILTER (WHERE confidence BETWEEN 0.5 AND 0.8) AS n_mid,
          COUNT(*) FILTER (WHERE confidence > 0.8) AS n_high
        FROM cegr_staging.mart_inference_record WHERE is_demo = 'true';"
# 预期: 每档 ≤ 8（per §4.2）
```

---

## 6. 验收清单

| # | 项 | 落地刀验证方式 |
|---|---|---|
| 1 | `inference_record` 表 + docs/40 §2.1 新增列齐全 | `\d cegr.inference_record` |
| 2 | `claim_evidence_link` 表 + docs/40 §2.2 新增列齐全 | `\d cegr.claim_evidence_link` |
| 3 | 既有 CHECK `inference_layer_not_fact` + `inference_confidence_range` 保留 | `\d` 约束列表 |
| 4 | 既有 CHECK `claim_evidence_polarity` (SUPPORTS / CONTRADICTS) 保留 | `\d` 约束列表 |
| 5 | 既有 `information_layer` ENUM 4 态不动 | `\dT+ cegr.information_layer` |
| 6 | 既有 `research_note.body_tsv` GIN + `set_updated_at_research_note` 触发器保留 | `\d cegr.research_note` + pg_trigger |
| 7 | dbt run `--select stg_inference_record+ mart_inference_record` exit 0；4 stg + 1 mart + 2 mart 辅助 view 创建 | dbt run log |
| 8 | mart 行数 = seed 行数（is_demo=true 过滤后）| SQL COUNT |
| 9 | 反例守门 NO_CONTRADICTING_EVIDENCE 数 = 0（per §4.2）| SQL COUNT |
| 10 | polarity 分布 SUPPORTS ≥ 1 + CONTRADICTS ≥ 1（per §4.2）| SQL GROUP BY |
| 11 | layer 分布 ≥ 3 行；无 FACT（per §5.5 #2）| SQL GROUP BY canonical_layer |
| 12 | canonical_layer 100% 投影 + inference_method 100% 标注（per §4.2）| SQL COUNT NULL = 0 |
| 13 | `inference_hash_canonical` 唯一值 ≤12（per §4.2）| SQL COUNT DISTINCT |
| 14 | `inference_year` 跨年覆盖 ≥2（per §4.2）| SQL COUNT DISTINCT |
| 15 | confidence 分布每档 ≤8（per §4.2）| SQL COUNT FILTER |
| 16 | 既有 61 schema_negative 测试仍绿（含 s21lite 5 + s22lite 5 + s23lite 8 + s24lite 8 + others）| pytest tests/ -q |
| 17 | 新增 pytest `tests/test_inference_s25lite.py` ≥5 cases 全过 | pytest -v |
| 18 | pack invariant 541 → 541+N（**含本刀 bug 修复：role_count 追平 artifacts**）| JSON 解析守门 |
| 19 | smoke-check 仍 PASS（无 frontend 改动）| python3 frontend/smoke-check.py |
| 20 | 既有 S2.7-a2 + S2.1-lite + S2.2-lite + S2.3-lite + S2.4-lite 套件仍绿 | pytest tests/test_evidence_chain_s27a.py tests/test_person_tenure_s21lite.py tests/test_policy_commitment_s22lite.py tests/test_project_event_s23lite.py tests/test_budget_s24lite.py |

---

## 7. 关键风险与回滚

| 风险 | 触发条件 | 回滚策略 |
|---|---|---|
| `layer = FACT` 写入触发 `inference_layer_not_fact` CHECK | 应用层误用 | schema CHECK 自动拒；落地刀测试 case 1 显式断言 |
| `confidence` 超出 [0, 1] 触发 CHECK | 录入错误 | schema CHECK 自动拒；落地刀测试 case 2 显式断言 |
| `polarity` 不在 SUPPORTS / CONTRADICTS | 应用层误用 | schema CHECK 自动拒；落地刀测试 case 3 显式断言 |
| `claim_evidence_link` 全 SUPPORTS 无 CONTRADICTS | 评审层未捕获反例 | `mart_claim_evidence_polarity_balance` 守门；Gate 2 §3.2 硬卡 |
| `inference_method` 全 NULL | 应用层未分类 | mart 守门 `n_records IS NULL`；落地刀测试 case 4 显式断言 |
| `inference_record.evidence_obs_ids` 引用未固化的 observation UUID | 引用孤岛 | 应用层守门；落地刀测试 case 5 验证 evidence_obs_ids ⊆ 既有 observation.id |
| 既有 `research_note.body_tsv` 触发器与新加列冲突 | migration 顺序 | 落地刀**不动** research_note schema；只通过 staging JOIN 关联 |
| `claim_evidence_hash_canonical` 全 NULL（首批不生成）| de-dupe 失效 | 落地刀 §4.4 稳定 UUID 钉死 36 行；不允许 NULL |
| `confidence` 高分推断误导用户 | UI 渲染问题 | docs/06 §6.6 红线 — UI 标注"仅展示量化值；非评分" |
| 反例登记被审核流于形式 | Gate 2 §3.2 弱化 | `mart_claim_evidence_polarity_balance.balance_status` 强制 NO_CONTRADICTING_EVIDENCE 红色 banner |

---

## 8. 不做什么（本刀 S2.5 边界；推后续刀）

| ❌ | 推到 |
|---|---|
| ❌ 写生产 migration 012（**仅规划**）| S2.5 落地刀（tasking 224+）|
| ❌ dbt stg_inference_record + stg_claim_evidence_link + mart_inference_record + mart 辅助 view | S2.5 落地刀 |
| ❌ 首批 ≤12 inference + ≤36 claim_evidence + ≤12 uncertainty + ≤6 research_note 真实 seed | S2.5 落地刀（**严禁爬网**）|
| ❌ 接 S2.7-b RegionCard 全量 UI 消费（仅暴露 mart；不 wire）| S2.7-b 协同刀 |
| ❌ Gate 2 §3.2 全量 UI 验收 | S2.10 |
| ❌ S2.1 person 全量（用户 D 缩刀）| 后续刀待用户裁定 |
| ❌ `policy_commitment` ↔ `inference_record` FK 启用 | 后续刀（per Cursor 裁定）|
| ❌ `derived_metric`（S2.5 后续刀）| 视 Cursor 裁定 |
| ❌ 推断评分（"准确率""可靠度""总评分"）| **红线**（per docs/06 §6.6）|
| ❌ `score` / `rating` / `rank` / `total_score` / `confidence_score` / `credibility_score` 任一字段 | **红线** |
| ❌ 修改 `information_layer` ENUM | docs/04 §3.1 钉死；新增态 = 013+ |
| ❌ 修改 `gate_thresholds.json` | spike-04 评测构件，只读 |
| ❌ 批量爬 2020-2025 政策研究 | 红线 |
| ❌ 启用 pgvector / RLS / partition | Stage 2 边界（per docs/04 §6）|
| ❌ 修改 `00-CC-CURRENT.md` | Cursor 拥有 |
| ❌ 修复 knife 8/9 漏报的 role_count +7 bug | **本刀 §10.3 一并修复** |

---

## 9. 与现有文档的关系

| 引用 | 用途 |
|---|---|
| `docs/04-data-model.md` §2 ERD 推断段 | `inference_record` ↔ `claim_evidence_link` 关系 |
| `docs/04-data-model.md` §3.1 | `information_layer` ENUM 4 态 + 不动 ENUM 钉死 |
| `docs/04-data-model.md` §3.9 | `claim_evidence_link.polarity` SUPPORTS / CONTRADICTS 双显（防确认偏差）|
| `docs/04-data-model.md` §6 | Stage 0 边界（不扩 pgvector / RLS / partition）|
| `docs/06-governance-observation-method.md` §2.7 | 证据链缺失的处理（`inference_record.evidence_gaps`）|
| `docs/06-governance-observation-method.md` §3 | 七维度观察卡 + INFERENCE/JUDGMENT 标注 |
| `docs/06-governance-observation-method.md` §4 | L1-L7 分析方法等级（`inference_method` enum）|
| `docs/06-governance-observation-method.md` §5 | 任期归因约束（不归因于"现任未尽职"）|
| `docs/06-governance-observation-method.md` §6 | 综合指数纪律（**红线**：不评分；不排名；不展示总分）|
| `docs/06-governance-observation-method.md` §7 | 展示形式（不展示"该官员表现好/差"）|
| `docs/19-stage1-s19-dbt-staging-plan-20260825.md` | dbt staging 模式 |
| `docs/33-stage1-s18-demo-sha-lock-plan-20260825.md` §3.1 / §3.3 | `is_demo` sentinel + 评测基线 |
| `docs/34-stage2-s20-kickoff-plan-20260825.md` §2 Gate 2 | 至少 1 个反例被显式登记并展示（**S2.5/§2.2 + §3.4 接驳**）|
| `docs/34-stage2-s20-kickoff-plan-20260825.md` §4 序 9 | S2.5 范围 + 推断排位 |
| `docs/36-stage2-s21-person-tenure-plan-20260825.md` | S2.1 平行规划（lineage + 命名模式）|
| `docs/37-stage2-s22-policy-plan-20260825.md` | S2.2 平行规划（unit drift 守门经验）|
| `docs/38-stage2-s23-project-plan-20260825.md` | S2.3 平行规划（五态机 + hash_canonical + 五段）|
| `docs/39-stage2-s24-budget-plan-20260826.md` | S2.4 平行规划（执行率双显 + 单位 drift）|
| `schema/01-core.sql` §25-30 | `information_layer` ENUM 4 态 |
| `schema/01-core.sql` §915-928 | 既有 `inference_record` 表 |
| `schema/01-core.sql` §932-940 | 既有 `uncertainty_record` 表 |
| `schema/01-core.sql` §942-954 | 既有 `research_note` 表（含 GIN 索引）|
| `schema/01-core.sql` §956-969 | 既有 `claim_evidence_link` 表（含 SUPPORTS/CONTRADICTS CHECK）|

---

## 10. CC 建议（供 Cursor 审阅 / 用户裁定）

### 10.1 `canonical_layer` 落 strategy

| 选项 | 描述 | 选 |
|---|---|---|
| A | enum-style TEXT（per docs/38 §10.2 平行）| **推荐**（不动 `information_layer` ENUM）|
| B | schema-level CHECK + ENUM type | 加固；migration 012 复杂度↑ |

### 10.2 `inference_method` 落 strategy

| 选项 | 描述 | 选 |
|---|---|---|
| A | enum-style TEXT 对应 docs/06 §4 L1-L7 + OTHER | **推荐**（与 docs/06 §4 平行）|
| B | 任意字符串 + drift view 守门 | 灵活；但 method 命名难统一 |

### 10.3 ⚠️ pack invariant bug 修复（knife 8/9 漏报）

**问题**：knife 8/9 落地的 7 个 artifact（schema_migration_ddl: +1, schema_migration_log: +1, schema_negative_test: +1, documentation: +4）**未**同步 bump `evidence_pack/manifest.json` 的 `role_count` dict。当前 manifest 状态：

```text
artifact_count: 541
len(artifacts): 541
sum(role_count): 534   ← 缺 +7
```

**修复**（本刀 +docs/40 同步处理）：

| role | 现在 | 修后 | delta |
|---|---|---|---|
| `documentation` | 46 | 50 | +4（knife 8/9 漏报 ×2 + 早期漏报 ×2）|
| `schema_migration_ddl` | 9 | 10 | +1（migration 011）|
| `schema_migration_log` | 5 | 6 | +1（migration 011 .log）|
| `schema_negative_test` | 26 | 27 | +1（test_budget_s24lite.py）|
| **小计追平** | 534 | 541 | **+7** |
| **+docs/40 (documentation +1)** | 541 | **542** | **+8 total** |

**invariant 终态**：542 == 542 == 542 ✅

**为什么必须本刀修**：每漏报一刀，gap 扩大；下一次 Cursor 评审可能拒收（"pack 散乱"）。本刀趁 knife 10 边界条件顺手收口。

### 10.4 `polarity` 必填性

| 选项 | 描述 | 选 |
|---|---|---|
| A | NOT NULL + CHECK 锁定（per docs/04 §3.9 钉死）| **推荐**（既有 CHECK 已锁定）|
| B | 引入 "UNRATED" 模糊值 | 削弱 docs/04 §3.9 防确认偏差 |

### 10.5 `confidence` 必填性

| 选项 | 描述 | 选 |
|---|---|---|
| A | nullable NUMERIC + CHECK [0, 1]（per docs/04 §1 既有约束）| **推荐**（既有 CHECK）|
| B | required NOT NULL | 加固；但"未量化"是合法语义 |

### 10.6 反例守门强度

| 选项 | 描述 | 选 |
|---|---|---|
| A | 应用层 + mart `balance_status` 守门（per §3.4）| **推荐**（per docs/04 §3.9）|
| B | schema-level CHECK `EXISTS (CONTRADICTS WHERE claim_id = ...)` | 不可行（跨行约束；PostgreSQL 不支持 subquery CHECK）|

### 10.7 `evidence_strength` 落 strategy

| 选项 | 描述 | 选 |
|---|---|---|
| A | enum-style TEXT（STRONG / MODERATE / WEAK / UNRATED）| **推荐**（per 红线 — 不数值化）|
| B | 不引入；评审层自由记录到 `note` 字段 | 灵活；但 UI 渲染一致性差 |

### 10.8 `geo_entity_id` 必填性

| 选项 | 描述 | 选 |
|---|---|---|
| A | nullable UUID（per §2.1 + §2.2；"全局推断"合法）| **推荐** |
| B | required NOT NULL | 加固；但跨地区/全国级推断无法入库 |

---

— End of `docs/40` —

> 等待 Cursor 审验（预期 `225-stage0-cursor-s25-plan-audit-…md`）。
> 通过后下发落地任务（`226-stage2-s25-inference-impl-tasking-…md`），进入 S2.5 实施。
> S2.1-full 与 S2.2-dbt/seed 与 S2.3 落地 与 S2.4 落地 与 S2.5 落地可**并行**（不同 schema 域）；等 Cursor 裁定。