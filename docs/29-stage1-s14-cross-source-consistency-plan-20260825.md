# S1.14 — 跨来源一致性（Cross-source Consistency）规划

> **规划 only**（不实现）。**CC 拥有**本文（per Cursor tasking 103 红线）。
> 前置：`102` S1.13.1 通过；`docs/27` §4.1 剩余严重缺口 #2；用户裁定 A（继续缺口）。
> 日期：2026-08-25

---

## §0. 目标

实现 **跨来源差异检测 + 记录**（per docs/05 §3.3 + docs/10 §2.4）：

- **5% 阈值**：任意两个 S0/S1 源对同一 `(indicator, geo, period)` 给出 >5% 差异 → 触发人工核查（GE 失败 + `inference_record` 标记）
- **2% 记录阈值**：>2% 但 ≤5% → 自动写 `source_disagreement` 表（**不阻塞**，仅记录）
- **<2%**：视为可接受修订差异（如 spike 1 启示：公报 zxfb 与年鉴修订差 0.3-1.5%），不记录

**核心原则**（per docs/09 R05 措施 2）：
- 冲突**并存**而非覆盖；S0 优先用于显示，但 S1+ 数据保留 + 标记
- 缺失 = NULL + `missing_reason`（per docs/05 §5）
- 阈值参数不写死到代码（待 Stage 2 / Cursor 提议配置化）

---

## §1. Schema 设计

**当前状态**：docs/05 §3.3 已定义 `source_disagreement` 表，但数据库**未创建**。本次需创建：

```sql
-- schema/migrations/006_source_disagreement.sql (CC 起草)

CREATE TABLE cegr.source_disagreement (
    id              UUID PRIMARY KEY DEFAULT uuid_generate_v4(),

    -- 标识三元组
    indicator_id           UUID NOT NULL REFERENCES cegr.indicator_definition(id),
    geo_entity_id          UUID NOT NULL REFERENCES cegr.geo_entity(id),
    calendar_period_id     UUID NOT NULL REFERENCES cegr.calendar_period(id),

    -- 来源 A（按优先级排）
    source_a_id            UUID NOT NULL REFERENCES cegr.source_registry(id),
    source_a_observation_id UUID REFERENCES cegr.observation(id),
    source_a_value         NUMERIC NOT NULL,
    source_a_level         cegr.source_level NOT NULL,
    source_a_basis         cegr.comparison_basis NOT NULL,

    -- 来源 B（质疑方）
    source_b_id            UUID NOT NULL REFERENCES cegr.source_registry(id),
    source_b_observation_id UUID REFERENCES cegr.observation(id),
    source_b_value         NUMERIC NOT NULL,
    source_b_level         cegr.source_level NOT NULL,
    source_b_basis         cegr.comparison_basis NOT NULL,

    -- 差异量化
    diff_abs               NUMERIC GENERATED ALWAYS AS (ABS(source_a_value - source_b_value)) STORED,
    diff_pct               NUMERIC GENERATED ALWAYS AS (
                              CASE WHEN source_a_value = 0 THEN NULL
                                   ELSE ABS(source_a_value - source_b_value) / ABS(source_a_value) * 100
                              END
                            ) STORED,
    diff_sign              TEXT NOT NULL CHECK (diff_sign IN ('A_GT_B', 'B_GT_A', 'EQUAL')),

    -- 分级 + 处理
    severity               TEXT NOT NULL CHECK (severity IN ('WITHIN_TOLERANCE', 'RECORDED', 'NEEDS_REVIEW')),
    severity_threshold_pct NUMERIC NOT NULL,  -- 触发本行的阈值（2.0 / 5.0 / 100.0）
    resolution             TEXT NOT NULL DEFAULT 'PENDING'
                  CHECK (resolution IN ('USE_A', 'USE_B', 'PARSE', 'PARALLEL', 'PENDING')),
    resolution_note        TEXT,
    resolved_by            TEXT,
    resolved_at            TIMESTAMPTZ,

    -- 元数据
    detected_at            TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    detected_by            TEXT NOT NULL DEFAULT 'dbt_test_cross_source_consistency',
    run_id                 UUID,  -- 关联 cegr.ingestion_run（无 FK 因为是 dbt 侧）
    UNIQUE (indicator_id, geo_entity_id, calendar_period_id, source_a_id, source_b_id, detected_at)
);

CREATE INDEX idx_source_disagreement_severity ON cegr.source_disagreement (severity, detected_at DESC);
CREATE INDEX idx_source_disagreement_unresolved ON cegr.source_disagreement (resolved_at) WHERE resolved_at IS NULL;
CREATE INDEX idx_source_disagreement_triplet ON cegr.source_disagreement (indicator_id, geo_entity_id, calendar_period_id);
```

**关键设计决策**：
- `diff_abs` / `diff_pct` 用 `GENERATED ALWAYS AS ... STORED`：避免 dbt 重算 + 保证一致性
- `severity` 三档映射阈值：`<2% → WITHIN_TOLERANCE`（不写表，由 dbt 直接过滤）；`2-5% → RECORDED`；`>5% → NEEDS_REVIEW`
- `UNIQUE (..., detected_at)`：允许同一三元组多次检测（不同 run）但每次都保留
- **不写硬 FK 到 `dbt_run`**：避免与 dbt 元数据耦合；`run_id` 仅为 UUID 引用

---

## §2. dbt 模型形状

### 2.1 `stg_source_disagreement_candidate` (staging)

读取每个 `(indicator_id, geo_entity_id, calendar_period_id)` 上**至少 2 个** `observation`，构造候选对比对：

```sql
-- dbt/models/staging/stg_source_disagreement_candidate.sql

WITH obs AS (
  SELECT
    indicator_id, geo_entity_id, calendar_period_id,
    source_registry_id, value, source_level, comparison_basis,
    observation_id
  FROM {{ ref('stg_observation') }}
  WHERE value IS NOT NULL
    AND source_level IN ('S0', 'S1')   -- 仅 S0/S1 进入跨源对比
),
pairs AS (
  SELECT
    a.indicator_id, a.geo_entity_id, a.calendar_period_id,
    LEAST(a.source_registry_id, b.source_registry_id) AS source_a_id,
    GREATEST(a.source_registry_id, b.source_registry_id) AS source_b_id,
    -- 选择高优先级为 A
    CASE WHEN a.source_level < b.source_level THEN a
         WHEN b.source_level < a.source_level THEN b
         ELSE a END AS pick_a,
    CASE WHEN a.source_level < b.source_level THEN b
         WHEN b.source_level < a.source_level THEN a
         ELSE b END AS pick_b
  FROM obs a
  JOIN obs b
    ON a.indicator_id = b.indicator_id
   AND a.geo_entity_id = b.geo_entity_id
   AND a.calendar_period_id = b.calendar_period_id
   AND a.source_registry_id < b.source_registry_id
   AND a.comparison_basis = b.comparison_basis  -- 基础必须一致
)
SELECT
  indicator_id, geo_entity_id, calendar_period_id,
  pick_a.source_registry_id AS source_a_id, pick_a.observation_id AS source_a_observation_id,
  pick_a.value AS source_a_value, pick_a.source_level AS source_a_level, pick_a.comparison_basis AS source_a_basis,
  pick_b.source_registry_id AS source_b_id, pick_b.observation_id AS source_b_observation_id,
  pick_b.value AS source_b_value, pick_b.source_level AS source_b_level, pick_b.comparison_basis AS source_b_basis,
  CASE WHEN pick_a.value > pick_b.value THEN 'A_GT_B' WHEN pick_a.value < pick_b.value THEN 'B_GT_A' ELSE 'EQUAL' END AS diff_sign
FROM pairs
```

### 2.2 `mart_source_disagreement` (mart) — 主入口

应用 5% / 2% 阈值分级，写入 `cegr.source_disagreement`：

```sql
-- dbt/models/marts/mart_source_disagreement.sql

{{ config(materialized='incremental', unique_key=['indicator_id','geo_entity_id','calendar_period_id','source_a_id','source_b_id','detected_at']) }}

WITH candidates AS (
  SELECT *,
    CASE
      WHEN source_a_value = 0 THEN NULL
      ELSE ABS(source_a_value - source_b_value) / ABS(source_a_value) * 100
    END AS diff_pct_computed
  FROM {{ ref('stg_source_disagreement_candidate') }}
),

classified AS (
  SELECT *,
    CASE
      WHEN diff_pct_computed IS NULL THEN 'WITHIN_TOLERANCE'
      WHEN diff_pct_computed < 2.0 THEN 'WITHIN_TOLERANCE'
      WHEN diff_pct_computed < 5.0 THEN 'RECORDED'
      ELSE 'NEEDS_REVIEW'
    END AS severity_computed,
    COALESCE(diff_pct_computed, 0) AS severity_threshold_pct
  FROM candidates
)

SELECT
  {{ dbt_utils.generate_surrogate_key(['indicator_id','geo_entity_id','calendar_period_id','source_a_id','source_b_id','detected_at']) }} AS id,
  indicator_id, geo_entity_id, calendar_period_id,
  source_a_id, source_a_observation_id, source_a_value, source_a_level, source_a_basis,
  source_b_id, source_b_observation_id, source_b_value, source_b_level, source_b_basis,
  diff_abs, diff_pct AS diff_pct,  -- DB 列优先（如果 GENERATED 已生效）；否则用 computed
  diff_sign, severity_computed AS severity,
  severity_threshold_pct,
  'PENDING' AS resolution, NULL AS resolution_note, NULL AS resolved_by, NULL AS resolved_at,
  NOW() AS detected_at,
  'dbt_test_cross_source_consistency' AS detected_by,
  '{{ invocation_id }}'::UUID AS run_id
FROM classified
WHERE severity_computed IN ('RECORDED', 'NEEDS_REVIEW')  -- WITHIN_TOLERANCE 不写表
```

**注**：`diff_pct` 列若 DB 侧已 GENERATED，则 dbt 不重算；否则用 `diff_pct_computed`。本规划先实现 dbt 计算，DB 列最终改为 GENERATED。

### 2.3 dbt tests（GE checkpoint）

```yaml
# dbt/models/marts/_mart_models.yml
models:
  - name: mart_source_disagreement
    tests:
      - dbt_utils.unique_combination_of_columns:
          combination_of_columns:
            - indicator_id
            - geo_entity_id
            - calendar_period_id
            - source_a_id
            - source_b_id
            - detected_at
      - not_null:
          column_name: severity
    columns:
      - name: diff_pct
        tests:
          - not_null
          - dbt_utils.accepted_range:
              min_value: 0
              max_value: 1000   # 1000% 视为占位异常
```

### 2.4 新增 GE suite `d3_source_disagreement_suite.json`

参照既有 `d1_source_registry_suite.json` 模板，新建 GE suite 检查：
- `source_disagreement` 表行数 ≥0（空表允许，honest）
- `severity='NEEDS_REVIEW'` 行必须 `resolution != 'PENDING'`
- `diff_pct IS NULL` 的行必须有 NULL-tolerant 标记

---

## §3. 现有 source_disagreement 衔接（空表诚实）

**当前 DB 状态**：`cegr.source_disagreement` **不存在**（查询 `information_schema.tables` 已确认）；docs/05 §3.3 是设计文档。

**实施时**：
1. 应用 migration `006_source_disagreement.sql` 到 cegr_test（**不**入 docs/26 Gate1 plan，因为它属于 S1.14 而非 Gate 1）
2. dbt staging view `stg_source_disagreement_candidate` 首次运行 → 由于 S1.12 江苏 seed + 历史 spike 数据**可能**产生 0 行（当前 S0/S1 唯一数据是 jiangsu_gdp_demo 的单一来源，不会触发跨源对比）
3. **空表诚实声明**：`mart_source_disagreement` 0 行 ≠ 通过；GE 期望空表时显式输出 `EXPECTED_EMPTY: source_disagreement table is empty (no S0/S1 cross-source pairs in seed data)`
4. 真正的 NEEDS_REVIEW 数据要等到 Stage 2 引入第二 S0 源（IMF / World Bank GDP）后才可能产生

---

## §4. API / GE 边界

### 4.1 新增 API endpoint（**S1.14.1 impl 阶段**，本规划仅声明）

```
GET /disagreements?severity=NEEDS_REVIEW&limit=50
GET /disagreements/{indicator_id}/{geo_id}/{period_id}
```

实现位于 `backend/src/china_platform/api/routes/disagreements.py`，沿用 S1.10 read-only pool；查询 `cegr.source_disagreement` JOIN `indicator_definition` + `geo_entity` + `calendar_period`。

### 4.2 GE / DB / API 三层职责

| 层 | 职责 | 不做 |
|---|---|---|
| **DB** (`source_disagreement`) | 持久化差异行 + 阈值分级 | 不计算（用 GENERATED 列） |
| **dbt** (mart) | 候选对比对生成 + 增量 upsert | 不写历史（每次 detected_at 新行） |
| **GE** | 空表诚实 + NEEDS_REVIEW 必有 resolution | 不阻塞（仅 fail 信号） |
| **API** (`/disagreements`) | 暴露给前端 + ops 人工核查 UI | 不修数据（只读） |

---

## §5. 测试策略

按 S1.13.1 模式（≥7 pytest）：

| # | 测试 | 断言 |
|---|------|------|
| 1 | `test_schema_applied` | `source_disagreement` 表存在 + 列名匹配 |
| 2 | `test_insert_within_tolerance_not_recorded` | <2% 差 → 表无新增行 |
| 3 | `test_insert_recorded` | 2-5% 差 → severity=RECORDED 行写入 |
| 4 | `test_insert_needs_review` | >5% 差 → severity=NEEDS_REVIEW 行写入 |
| 5 | `test_diff_pct_computed_correctly` | 手算 (a-b)/a*100 与 GENERATED 列一致 |
| 6 | `test_diff_sign_correct` | A>B → A_GT_B；相等 → EQUAL |
| 7 | `test_comparison_basis_mismatch_excluded` | 不同 basis 的 obs 不进入 pairs |
| 8 | `test_unique_constraint` | 同三元组 + 同 source pair 重复 INSERT 抛错 |
| 9 | `test_dbt_mart_runs_empty` | 空数据时 mart 0 行 + 不抛错 |

总计 ≥9（per S1.13.1 9 模式；与任务书 ≥7 一致）。

---

## §6. 红线（per tasking 103）

- ❌ 不宣布 Stage 0 PASS / Gate 1 PASS
- ❌ 不批量 2020-2025 历史数据爬取
- ❌ 不 HTTP 爬源站
- ❌ 不降 OCR 门槛
- ❌ 不把任何省份标为「门控」
- ❌ 不擅自 --force / --force-with-lease
- ❌ 不替用户下裁定
- ❌ 不在聊天复述 Cursor 长文；不索要 PAT
- ❌ 不改 gate_thresholds.json（阈值 2% / 5% 是常量，非 gate 阈值）
- ❌ 不爬网（仅本地 fixture + dbt 在已有 staging 上）
- ❌ Cursor 不写 `docs/29` 正文（CC 拥有）

---

## §7. 缺口与未决（honest gap list）

| Gap | 备注 |
|-----|------|
| **空表状态** | 当前 DB 0 行 `source_disagreement`（表本身也不存在）。dbt 运行产出 0 行 ≠ 通过 → GE 显式声明 `EXPECTED_EMPTY` |
| **第二 S0 源** | 真正的 NEEDS_REVIEW 数据要等 Stage 2 引入 IMF / World Bank。当前无法 E2E 演示 NEEDS_REVIEW 路径，仅能演示 RECORDED（通过 test fixture 注入） |
| **阈值参数化** | 2% / 5% 写死在 dbt SQL CASE WHEN。Stage 2 提议 dbt var / config 化 |
| **resolution 工作流** | API 暴露 `/disagreements` 但 UI 不在 Stage 1 范围；ops 通过 psql 手动改 resolution |
| **跨 schema 命名** | `public.admin_upload_audit` vs `cegr.*` — `source_disagreement` 选用 `cegr.*`（与已有 observation / observation_quality_flag 一致） |

---

## §8. 后续 tasking 预告

- **tasking 105 (S1.14.1 impl)**：migration 006 + dbt model + GE suite + ≥7 pytest + API `/disagreements` route
- **tasking 106 (S1.14.2)**（Stage 2 起）：引入 IMF / World Bank GDP 第二 S0 源，验证 NEEDS_REVIEW 路径

— CC @ queue_rev 34, S1.14 plan draft —