# 43 — Stage 2 / S2.9 / 同类地区对比 规划

> 起草：CC · 2026-08-26 · queue_rev 94
> 前置：`240` S2.8-lite PASS；`docs/34` §4 序 12；`docs/05` §8（同类地区匹配）；
> `docs/06` §4（分析等级 L1-L7）；`docs/08` §S2.9（5 省 × 3 个对比地区）；
> `docs/10` §133（peer_selection_justified）；`docs/41` §10.8（同类区间位）
> 本刀**仅规划**；不写生产 migration（per `241` §SCHEMA + 用户裁定 **D** 缩刀模式）

---

## 1. 目标

S2.9 是 Stage 2 **同类地区对比**维度的**契约/UI 刀** — 落地刀将提供：

- 手工选择 3-5 个可比地区的能力（per `docs/05 §8.2`）
- 匹配依据可解释（per `docs/10 §133`）：人口/产业/区位
- 不允许"仅按 GDP top N"（per `docs/05 §8.3` 红线）
- 与 S2.7 EvidenceChain + S2.8 七维度观察卡的**接驳**：
  - RegionCard 顶部可点开"同类地区对比"
  - 对比卡展示本地区 × 3-5 同类的 **EvidenceChain 段级对比**
  - 对比卡展示本地区 × 同类的 **七维度 cell 对比**（per S2.8）
  - 对比**只读**（不评分、不排名、不算贡献）

**S2.9 与 S2.7 / S2.8 的边界**（per `241` §SCHEMA 钉死）：

| S2.7 关注 | S2.8 关注 | S2.9 关注 |
|---|---|---|
| 六段 EvidenceChain UI（已交）| 七维度观察卡 UI（已交）| 同类地区对比 UI |
| 段级 evidence gaps 显示 | 维度级 balance_status 显示 | 地区级 comparison_group 显示 |
| mart_evidence_chain 段级投影 | mart_seven_dim_overview 维度级投影 | mart_peer_region_compare 地区级投影 |
| 单地区观察 | 单地区多维度观察 | 多地区同口径观察 |

**S2.9 红线**（per `241` §SCHEMA + docs/34 §4.3 + docs/05 §8.3）：

- ❌ 不接全国实时排名（Stage 3 边界）
- ❌ 不按 GDP 总量取 top N
- ❌ 不做 Mahalanobis 距离自动匹配（Stage 3 范围）
- ❌ 不做倾向得分（Stage 3 范围）
- ❌ 不做官员评分 / 不做总分 / 不做排名
- ❌ 同一观察不可同时被分到多组（重叠即不可解释）

---

## 2. 契约（同类地区对比 + EvidenceChain 接驳 + 七维度接驳）

### 2.0 范围声明

| 包含 | 不包含（推后续刀）|
|---|---|
| `comparison_group` 表 schema（手工选择版）| Mahalanobis 距离自动匹配（Stage 3）|
| `comparison_group_member` 中间表 schema | 倾向得分匹配（Stage 3）|
| 匹配依据 4 维度（人口/区位/产业/发展阶段）| 时变匹配（动态调整）|
| 5 省 × 3 同类 = 15 行的首批 seed（手工）| 全国 31 省自动匹配 |
| 与 S2.7 EvidenceChain 段级对比 | 与 S2.10 Gate 2 评审包集成 |
| 与 S2.8 七维度 cell 对比 | 与 S2.10 Gate 2 评审包集成 |
| 应用层 enum-style 守门（4 维度枚举）| schema ENUM（per docs/40 §2.3 平行）|
| `lineage.is_demo` 流转守门 | 任何 production data 写入 |

### 2.1 `comparison_group` 表（手工选择版）

```sql
-- comparison_group (per docs/05 §8.1)
CREATE TABLE IF NOT EXISTS cegr.comparison_group (
    comparison_group_id    UUID PRIMARY KEY,
    canonical_name_zh      TEXT NOT NULL,
    canonical_name_en      TEXT NOT NULL,
    description            TEXT,                         -- 为什么这群可比
    population_tier        TEXT,                         -- <500万 / 500-1000万 / 1000-2000万 / >2000万
    location_type          TEXT,                         -- coastal / inland / border
    industry_base           TEXT,                         -- resource / manufacturing / service / mixed
    development_stage      TEXT,                         -- high / middle / low
    selection_method       TEXT NOT NULL,                -- manual / mahalanobis / propensity（仅 manual 落地）
    selection_justification TEXT NOT NULL,               -- 可解释依据（per docs/10 §133）
    lineage                JSONB NOT NULL DEFAULT '{}',  -- is_demo / source_file_sha256 / source_file_url
    created_at             TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at             TIMESTAMPTZ NOT NULL DEFAULT now(),
    CHECK (selection_method IN ('manual', 'mahalanobis', 'propensity'))
);

CREATE INDEX IF NOT EXISTS idx_comparison_group_method
    ON cegr.comparison_group (selection_method)
    WHERE selection_method = 'manual';
```

### 2.2 `comparison_group_member` 中间表

```sql
-- comparison_group_member (per docs/05 §8.1)
CREATE TABLE IF NOT EXISTS cegr.comparison_group_member (
    comparison_group_id    UUID NOT NULL REFERENCES cegr.comparison_group(comparison_group_id) ON DELETE CASCADE,
    geo_entity_id          UUID NOT NULL REFERENCES cegr.geo_entity(geo_entity_id) ON DELETE CASCADE,
    role_in_group          TEXT NOT NULL,                -- focal / peer
    selection_reason       TEXT NOT NULL,                -- 为什么这个地区被选入
    lineage                JSONB NOT NULL DEFAULT '{}',
    created_at             TIMESTAMPTZ NOT NULL DEFAULT now(),
    PRIMARY KEY (comparison_group_id, geo_entity_id),
    CHECK (role_in_group IN ('focal', 'peer')),
    CHECK (selection_reason <> '')                       -- 不能空选
);

CREATE INDEX IF NOT EXISTS idx_member_geo
    ON cegr.comparison_group_member (geo_entity_id);
```

### 2.3 4 维度匹配依据守门（per docs/05 §8.1）

```yaml
# 应用层 enum-style 守门（per docs/40 §2.3 平行；不引入 schema ENUM）
POPULATION_TIER = ["<500万", "500-1000万", "1000-2000万", ">2000万"]
LOCATION_TYPE = ["coastal", "inland", "border"]
INDUSTRY_BASE = ["resource", "manufacturing", "service", "mixed"]
DEVELOPMENT_STAGE = ["high", "middle", "low"]

# 守门：每 group 至少 1 个 focal + 3-5 peer（per docs/08 §S2.9）
# 守门：每 peer 必须 selection_reason 非空（per docs/10 §133）
```

### 2.4 `mart_peer_region_compare` 视图（每 comparison_group × 段/维度一行）

```sql
-- mart_peer_region_compare
{{ config(materialized='view', tags=['mart', 'peer_region']) }}

WITH group_evidence_balance AS (
    SELECT
        cgm.comparison_group_id,
        cg.canonical_name_zh AS group_name_zh,
        cgm.geo_entity_id,
        cgm.role_in_group,
        -- EvidenceChain 段级聚合
        COUNT(*) FILTER (WHERE ec.information_layer = 'OBSERVATION')  AS n_observation,
        COUNT(*) FILTER (WHERE ec.information_layer = 'INFERENCE')    AS n_inference,
        COUNT(*) FILTER (WHERE ec.information_layer = 'JUDGMENT')     AS n_judgment,
        COUNT(*) FILTER (WHERE ec.information_layer = 'DERIVED')      AS n_derived,
        COUNT(*) FILTER (WHERE cel.canonical_polarity = 'SUPPORTS')   AS n_supports,
        COUNT(*) FILTER (WHERE cel.canonical_polarity = 'CONTRADICTS') AS n_contradicts
    FROM cegr.comparison_group_member cgm
    JOIN cegr.comparison_group cg
        ON cg.comparison_group_id = cgm.comparison_group_id
    LEFT JOIN cegr.evidence_chain ec
        ON ec.geo_entity_id = cgm.geo_entity_id
    LEFT JOIN cegr.claim_evidence_link cel
        ON cel.geo_entity_id = cgm.geo_entity_id
    GROUP BY cgm.comparison_group_id, cg.canonical_name_zh,
             cgm.geo_entity_id, cgm.role_in_group
),
seven_dim_per_region AS (
    SELECT
        geo_entity_id,
        COUNT(*) FILTER (WHERE balance_status = 'NO_CONTRADICTING_EVIDENCE') AS cells_no_contradicts,
        COUNT(*) FILTER (WHERE balance_status = 'SUPPORTS_DOMINANT')          AS cells_supports_dominant,
        COUNT(*) FILTER (WHERE balance_status = 'CONTRADICTS_DOMINANT')       AS cells_contradicts_dominant,
        COUNT(*)                                                              AS total_cells
    FROM cegr_staging.mart_seven_dim_overview
    GROUP BY geo_entity_id
)
SELECT
    geb.comparison_group_id,
    geb.group_name_zh,
    geb.role_in_group,
    geb.geo_entity_id,
    ge.canonical_name AS geo_name_zh,
    -- 段级
    geb.n_observation,
    geb.n_inference,
    geb.n_judgment,
    geb.n_derived,
    geb.n_supports,
    geb.n_contradicts,
    -- 七维度级（来自 S2.8 mart）
    COALESCE(sdr.cells_no_contradicts, 0)     AS cells_no_contradicts,
    COALESCE(sdr.cells_supports_dominant, 0)  AS cells_supports_dominant,
    COALESCE(sdr.cells_contradicts_dominant, 0) AS cells_contradicts_dominant,
    COALESCE(sdr.total_cells, 0)              AS total_seven_dim_cells,
    -- lineage
    COALESCE(cgm.lineage->>'is_demo', 'true') AS is_demo
FROM group_evidence_balance geb
JOIN cegr.comparison_group_member cgm
    ON cgm.comparison_group_id = geb.comparison_group_id
    AND cgm.geo_entity_id = geb.geo_entity_id
JOIN cegr.geo_entity ge
    ON ge.geo_entity_id = geb.geo_entity_id
LEFT JOIN seven_dim_per_region sdr
    ON sdr.geo_entity_id = geb.geo_entity_id
```

**不评分**：仅计数 + 枚举状态；不派生"地区排名""综合得分"（per docs/06 §6.6 红线）。

### 2.5 与 S2.7 EvidenceChain 接驳（段级对比）

| segment | `mart_peer_region_compare.n_observation` 等列 |
|---|---|
| `CONDITION` | (无 n_observation 列；S2.7 内部) |
| `COMMITMENT` | (无 n_observation 列；S2.7 内部) |
| `PROCESS` | (无 n_observation 列；S2.7 内部) |
| `OUTPUT` | `n_observation`（聚合 OBSERVATION layer）|
| `OUTCOME` | `n_inference` + `n_judgment`（聚合 INFERENCE/JUDGMENT layer）|
| `FEEDBACK` | `n_derived`（聚合 DERIVED layer）|

> **注**：mart_peer_region_compare 输出 n_observation 等 4 列聚合，UI 落地刀可按段映射显示。

### 2.6 与 S2.8 七维度 cell 接驳

| seven_dim_card | `mart_peer_region_compare` 列 |
|---|---|
| `POLICY_DELIVERY` | (按 region 聚合；不做 card 级别列拆分) |
| `FISCAL_EXECUTION` | (按 region 聚合) |
| `PROJECT_DELIVERY` | (按 region 聚合) |
| `ECONOMIC_ADAPTATION` | (按 region 聚合) |
| `PUBLIC_SERVICES` | (按 region 聚合) |
| `RISK_MANAGEMENT` | (按 region 聚合) |
| `GOAL_CONSISTENCY` | (按 region 聚合) |

> **简化**：UI 落地刀仅展示 region-level 聚合（cells_no_contradicts 等），不做 card-level 横向对比（避免引入"地区×维度排名"）。

### 2.7 `mart_peer_region_compare` 应用层守门

```python
# 应用层 enum-style 守门 (per docs/40 §2.3 + docs/41 §2.3 平行)
SELECTION_METHOD = ["manual", "mahalanobis", "propensity"]
ROLE_IN_GROUP = ["focal", "peer"]
POPULATION_TIER = ["<500万", "500-1000万", "1000-2000万", ">2000万"]
LOCATION_TYPE = ["coastal", "inland", "border"]
INDUSTRY_BASE = ["resource", "manufacturing", "service", "mixed"]
DEVELOPMENT_STAGE = ["high", "middle", "low"]

# ❌ 不引入 schema ENUM
# ❌ 不引入 score / rating / total_score / rank / peer_rank 字段
# ✅ dbt model WHERE selection_method = 'manual' 守门（仅手工）
# ✅ pytest 显式断言所有 enum 守门
```

---

## 3. UI 形态（同类地区对比 + 与 EvidenceChain / 七维度接驳）

### 3.1 同类地区对比入口（RegionCard 顶部）

```
┌──────────────────────────────────────────────────────────────────┐
│  RegionCard — 江苏 (mock)                                         │
├──────────────────────────────────────────────────────────────────┤
│  [展开 ▼] [EvidenceChain 六段] [七维度观察卡] [同类地区对比]      │  ← 新增 tab
└──────────────────────────────────────────────────────────────────┘
```

### 3.2 同类地区对比卡（折叠态）

```
┌──────────────────────────────────────────────────────────────────────┐
│  同类地区对比 (江苏 mock, comparison_group_id = XXXX)                  │
├──────────────────────────────────────────────────────────────────────┤
│  匹配依据 (per docs/10 §133):                                         │
│    人口: 1000-2000万 / 区位: coastal / 产业: mixed / 阶段: high      │
│                                                                      │
│  focal: 江苏 (focal)                                                  │
│  peers:                                                                │
│    • 浙江 (peer; 沿海+制造+高收入)                                    │
│    • 广东 (peer; 沿海+服务+高收入)                                    │
│    • 山东 (peer; 沿海+制造+中等)                                      │
│                                                                      │
│  [展开 ▼]                                                             │
└──────────────────────────────────────────────────────────────────────┘
```

### 3.3 同类地区对比卡（展开态 — EvidenceChain 段级对比）

```
┌──────────────────────────────────────────────────────────────────────┐
│  EvidenceChain 段级对比 (per S2.7 接驳)                                │
├──────────────────────────────────────────────────────────────────────┤
│  段         江苏 (focal)  浙江 (peer)  广东 (peer)  山东 (peer)         │
│  OUTPUT     142 n_obs     138          156          121                 │
│  OUTCOME    38 n_inf      35           42           29                  │
│             12 n_jud      14           16           9                   │
│  FEEDBACK   4 n_der       3            5            2                   │
│                                                                      │
│  反例守门 (per S2.6 接驳):                                              │
│    江苏: 47 n_contradicts                                                │
│    浙江: 45 n_contradicts                                                │
│    ...                                                                 │
│                                                                      │
│  ⚠ 仅展示计数；不排名；不算分                                          │
└──────────────────────────────────────────────────────────────────────┘
```

### 3.4 同类地区对比卡（展开态 — 七维度 cell 对比 per S2.8 接驳）

```
┌──────────────────────────────────────────────────────────────────────┐
│  七维度 cell 对比 (per S2.8 接驳)                                     │
├──────────────────────────────────────────────────────────────────────┤
│  维度               江苏 (focal)  浙江  广东  山东                     │
│  POL_DEL            🔴 0 反       🔴 0   🟠 2   🟢 4                   │
│  FIS_EXEC           🟢 5 / 1      🟢 4   🟢 6   🟡 0 / 3                │
│  PROJ_DEL           🟡 0 / 2      🟠 1   🟢 3   🟢 4                   │
│  ECON_ADP           🟢 4 / 1      🟢 5   🟢 6   🟠 1                   │
│  PUB_SVC            🟠 1 / 2      🟢 3   🟢 4   🟡 0 / 2                │
│  RISK_MGT           🔴 2 / 0      🔴 1   🟢 3   🟢 5                   │
│  GOAL_CON           ⚪ 空          🟢 2   🟢 3   🟡 0 / 1                │
│                                                                      │
│  ⚠ 仅展示 balance_status 计数；不评分；不排名；不派生地区得分            │
└──────────────────────────────────────────────────────────────────────┘
```

### 3.5 React 组件最小形态（落地刀产出）

```tsx
// frontend/components/peer-compare/PeerCompareCard.tsx — 落地刀产出
interface PeerCompareProps {
    groupId: string;
    groupNameZh: string;
    populationTier: PopulationTier;
    locationType: LocationType;
    industryBase: IndustryBase;
    developmentStage: DevelopmentStage;
    selectionMethod: "manual";                    // 仅 manual
    selectionJustification: string;               // 非空
    members: Array<{
        geoEntityId: string;
        geoNameZh: string;
        roleInGroup: "focal" | "peer";
        selectionReason: string;                  // 非空
    }>;
    // mart_peer_region_compare 输出
    evidenceBalanceByMember?: Array<{
        geoEntityId: string;
        nObservation: number;
        nInference: number;
        nJudgment: number;
        nDerived: number;
        nSupports: number;
        nContradicts: number;
    }>;
    sevenDimByMember?: Array<{
        geoEntityId: string;
        cellsNoContradicts: number;
        cellsSupportsDominant: number;
        cellsContradictsDominant: number;
        totalSevenDimCells: number;
    }>;
    isDemo: boolean;
    expanded?: boolean;
}

// 折叠态: 匹配依据 + focal/peers 列表
// 展开态: + EvidenceChain 段级对比 + 七维度 cell 对比
// ⚠ 仅展示计数；不评分；不排名；不派生地区得分
```

### 3.6 与 S2.7 / S2.8 路由接驳（落地刀）

```
RegionCard
  ↓ click "同类地区对比" tab
PeerCompareCard (S2.9 既有)
  ├── click "EvidenceChain 段级对比"
  │     → EvidenceChain (S2.7 既有) — 但只读；不算分
  ├── click "七维度 cell 对比"
  │     → SevenDimCard (S2.8 既有) — 但只读；不算分
  └── click "返回 RegionCard"
        → RegionCard
```

---

## 4. 首批入库策略

> **本刀仅规划**；落地刀 (tasking 244+) 视 Cursor 审验再下发。

### 4.1 草拟：5 省 × 3 同类 = 15 行 seed

| focal (江苏) | peer | peer | peer | 匹配依据 |
|---|---|---|---|---|
| 江苏 (mock) | 浙江 | 广东 | 山东 | coastal + mixed + high |
| 浙江 (mock) | 江苏 | 上海 | 福建 | coastal + mixed + high |
| 广东 (mock) | 江苏 | 浙江 | 山东 | coastal + mixed + high |
| 山东 (mock) | 江苏 | 浙江 | 河南 | coastal + mixed + middle |
| 四川 (mock) | 河南 | 湖北 | 安徽 | inland + mixed + middle |

| focal | peer | peer | peer | 匹配依据 |
|---|---|---|---|---|
| 江苏 | 浙江 | 广东 | 山东 | coastal + mixed + high |
| 浙江 | 江苏 | 上海 | 福建 | coastal + mixed + high |
| 广东 | 江苏 | 浙江 | 山东 | coastal + mixed + high |
| 山东 | 江苏 | 浙江 | 河南 | coastal + mixed + middle |
| 四川 | 河南 | 湖北 | 安徽 | inland + mixed + middle |

> **总计**：5 focal × 3 peer = 20 member 行（5 group + 15 peer + 5 focal）
> **is_demo**: `true`（per docs/33 §3.2 sentinel + 用户裁定 D 缩刀）
> **严禁爬网**：selection_justification 由 CC 手工填入，不从网络抓取

### 4.2 mart 行数守门

| mart | 行数上限 | 理由 |
|---|---|---|
| `mart_peer_region_compare` | ≤20 行（5 group × 4 member）| 演示守门 |
| 每 group focal count | = 1 | 守门 |
| 每 group peer count | ∈ [3, 5] | docs/05 §8.2 |

### 4.3 `is_demo` 流转（per docs/33 §3.2 sentinel + docs/41 §4.3 平行）

| 阶段 | `comparison_group.lineage.is_demo` | `comparison_group_member.lineage.is_demo` |
|---|---|---|
| DRAFT | `"true"` | `"true"` |
| 公开登记后 | `"false"` | `"false"` |

### 4.4 稳定标识（per S1.12 + docs/40 §4.4 平行）

| 表 | UUID 家族 |
|---|---|
| `comparison_group` | `b0000000-0000-0000-0000-000000000XXX` |
| `comparison_group_member` | `b1000000-0000-0000-0000-000000000XXX` |
| mart_peer_region_compare | 无 UUID；`(comparison_group_id, geo_entity_id)` 复合主键 |

---

## 5. 与 S2.7 / S2.8 / S2.10 接驳

### 5.1 与 S2.7 EvidenceChain 接驳（段级对比）

| 段 | S2.9 mart 列 |
|---|---|
| `OUTPUT` | `n_observation` (聚合 OBSERVATION layer) |
| `OUTCOME` | `n_inference` + `n_judgment` (聚合 INFERENCE/JUDGMENT layer) |
| `FEEDBACK` | `n_derived` (聚合 DERIVED layer) |
| `CONDITION` / `COMMITMENT` / `PROCESS` | (S2.9 不展开；属 S2.7 内部) |

### 5.2 与 S2.8 七维度 cell 接驳

S2.9 mart 仅展示 region-level 聚合（`cells_no_contradicts` 等），不做 card-level 横向对比（避免引入"地区×维度排名"红线）。

### 5.3 与 S2.6 反例守门接驳（per docs/41 §5.1）

S2.9 mart 复用 `n_contradicts` 列；红色 banner 触发逻辑与 S2.6 平行（`n_contradicts = 0` → 红 banner）；S2.9 不重新触发 `assert_min_one_contradicts()` trigger（DB 已守门）。

### 5.4 不接 S2.10 Gate 2 评审包（per `241` §SCHEMA 红线）

S2.10 评审包集成属后续刀；本刀 S2.9 仅规划 comparison_group/mart_peer_region_compare + UI 落地。

### 5.5 验证（落地刀）

```bash
# 1. comparison_group 行数 ≤ 5（演示守门）
psql -c "SELECT COUNT(*) FROM cegr.comparison_group;"

# 2. comparison_group_member 行数 ≤ 20（每 group 1 focal + 3 peer）
psql -c "SELECT comparison_group_id, role_in_group, COUNT(*)
         FROM cegr.comparison_group_member
         GROUP BY 1, 2;"

# 3. selection_justification 非空
psql -c "SELECT COUNT(*) FROM cegr.comparison_group WHERE selection_justification = '' OR selection_justification IS NULL;"
# 预期: 0

# 4. selection_method = 'manual' 守门（落地刀仅 manual）
psql -c "SELECT COUNT(*) FROM cegr.comparison_group WHERE selection_method <> 'manual';"
# 预期: 0

# 5. 每 group focal = 1, peer ∈ [3, 5]
psql -c "SELECT comparison_group_id,
         COUNT(*) FILTER (WHERE role_in_group = 'focal') AS n_focal,
         COUNT(*) FILTER (WHERE role_in_group = 'peer')  AS n_peer
         FROM cegr.comparison_group_member
         GROUP BY comparison_group_id;"

# 6. mart_peer_region_compare 视图可 query
psql -c "SELECT COUNT(*) FROM cegr_staging.mart_peer_region_compare;"
# 预期: 20

# 7. mart 列 8 枚举守门
psql -c "SELECT DISTINCT role_in_group FROM cegr_staging.mart_peer_region_compare;"
# 预期: focal, peer
```

---

## 6. 验收清单

| # | 项 | 落地刀验证方式 |
|---|---|---|
| 1 | `comparison_group` 表 schema 含 4 维度匹配依据列（per §2.1）| `\d cegr.comparison_group` |
| 2 | `comparison_group_member` 表含 `role_in_group` + `selection_reason` 列（per §2.2）| `\d cegr.comparison_group_member` |
| 3 | selection_method CHECK 含 `manual` / `mahalanobis` / `propensity`（per §2.1）| `\d+ cegr.comparison_group` |
| 4 | 每 group 1 focal + 3-5 peer 守门（per §4.2）| SQL COUNT GROUP BY |
| 5 | `selection_justification` 非空守门（per docs/10 §133）| SQL COUNT WHERE = '' |
| 6 | `mart_peer_region_compare` 视图可 query；行数 ≤ 20 | dbt run + SQL COUNT |
| 7 | mart 列 8 枚举守门（4 元数据 enum + 2 role enum + selection_method）| SQL DISTINCT |
| 8 | 与 S2.7 EvidenceChain 段级对比接驳（per §5.1）| React 路由 E2E |
| 9 | 与 S2.8 七维度 cell 对比接驳（per §5.2）| React 路由 E2E |
| 10 | 与 S2.6 反例红色 banner 接驳（per §5.3）| React 路由 E2E |
| 11 | RegionCard 顶部新增"同类地区对比" tab（per §3.1）| frontend browser E2E |
| 12 | 折叠态：匹配依据 + focal/peers 列表（per §3.2）| frontend browser E2E |
| 13 | 展开态：EvidenceChain 段级对比 + 七维度 cell 对比（per §3.3 + §3.4）| frontend browser E2E |
| 14 | `lineage.is_demo` 流转：含 is_demo | SQL COUNT |
| 15 | 不引入 schema ENUM（应用层 enum-style 守门）| grep "CREATE TYPE" schema/migrations/ |
| 16 | 不引入 score / rating / total_score / peer_rank 字段 | grep |
| 17 | 不接 S2.10 Gate 2 评审包（per `241` §SCHEMA 红线）| code review |
| 18 | 不接全国实时排名（per `241` §SCHEMA 红线）| code review |
| 19 | 不按 GDP 总量取 top N（per docs/05 §8.3 红线）| selection_justification 守门 |
| 20 | 新增 pytest `tests/test_peer_region_compare_s29.py` ≥5 cases 全过 | pytest -v |
| 21 | pack invariant 559 → 559+N | JSON 解析守门 |
| 22 | smoke-check 仍 PASS（无 frontend 改动）| python3 frontend/smoke-check.py |
| 23 | 既有 s21lite..s26lite 套件仍绿 | pytest tests/test_*_s*lite.py -q |

---

## 7. 关键风险与回滚

| 风险 | 触发条件 | 回滚策略 |
|---|---|---|
| `selection_justification` 空值 | migration 未加 NOT NULL CHECK | pytest case 显式断言；migration 加 `CHECK (selection_justification <> '')` |
| 每 group peer < 3 或 > 5 | seed 配比错 | pytest case 显式断言 peer 范围；seed 脚本 dry-run |
| `selection_method` 引入 `mahalanobis` / `propensity`（越界到 Stage 3）| migration 误扩枚举 | pytest case 显式断言 `WHERE selection_method = 'manual'` |
| S2.9 接全国实时排名（越界）| mart 视图扩到省级全集 | code review；§8 红线 |
| 评分字段被引入（"peer_rank" "peer_score" "comparison_score"）| docs/06 §6.6 红线被绕过 | pytest FORBIDDEN_COLUMN_PATTERNS 守门；grep 双层守门 |
| S2.9 接 S2.10 评审包（越界）| Gate 2 评审被意外引入 | code review；§5.4 红线 |
| S2.9 接 S2.7 EvidenceChain 段级修改（越界）| S2.7 UI 改动 | code review；§5.1 红线（仅消费 n_observation 等列）|
| S2.9 接 S2.8 七维度 cell 修改（越界）| S2.8 UI 改动 | code review；§5.2 红线（仅消费 region-level 聚合）|
| `is_demo` 流转被绕过（admin 直接 UPDATE）| DB 写权限 | 既有 trigger 守门（per docs/33 §3.2）|

---

## 8. 不做什么（本刀 S2.9 边界；推后续刀）

| ❌ | 推到 |
|---|---|
| ❌ 写生产 migration（**仅规划**）| S2.9 落地刀（tasking 244+）|
| ❌ dbt `mart_peer_region_compare` 视图 + source yml | S2.9 落地刀 |
| ❌ 首批 ≤20 行 seed（5 group × 4 member）| S2.9 落地刀（**严禁爬网**）|
| ❌ React PeerCompareCard 组件 + RegionCard tab | S2.9 落地刀 |
| ❌ Mahalanobis 距离自动匹配 | Stage 3 |
| ❌ 倾向得分匹配 | Stage 3 |
| ❌ 全国实时排名 | Stage 3 红线 |
| ❌ 按 GDP 总量取 top N | 红线（per docs/05 §8.3）|
| ❌ 改 docs/05 §8 内容（Cursor 拥有）| — |
| ❌ 改 docs/06 §4 内容（Cursor 拥有）| — |
| ❌ S2.7 六段 EvidenceChain UI 改动 | S2.7 |
| ❌ S2.8 七维度观察卡 UI 改动 | S2.8 |
| ❌ S2.6 反例登记 UI 改动 | S2.6 |
| ❌ S2.10 Gate 2 评审包集成 | S2.10 |
| ❌ `score` / `rating` / `rank` / `peer_rank` / `total_score` / `confidence_score` 任一字段 | **红线**（per docs/06 §6.6 + docs/41 §10.8）|
| ❌ schema-level ENUM（per docs/40 §2.3 + docs/41 §2.3 平行）| — |
| ❌ 修改 `gate_thresholds.json` | spike-04 评测构件，只读 |
| ❌ 批量爬政策研究 / 财政预决算 / 官员履历 | 红线 |
| ❌ 启用 pgvector / RLS / partition | Stage 2 边界（per docs/04 §6）|
| ❌ 修改 `00-CC-CURRENT.md` | Cursor 拥有 |
| ❌ 跨行 CHECK 约束 | 用 trigger + 应用层守门 |

---

## 9. 与现有文档的关系

| 引用 | 用途 |
|---|---|
| `docs/05-indicator-methodology.md` §8.1 | 匹配特征（人口/区位/产业/发展阶段）|
| `docs/05-indicator-methodology.md` §8.2 | 匹配方法（手动 / Mahalanobis / 倾向得分）|
| `docs/05-indicator-methodology.md` §8.3 | 不允许的匹配（按 GDP top N / 无依据 / 重叠）|
| `docs/06-governance-observation-method.md` §4 | 分析等级 L1-L7（L2 同类比较）|
| `docs/06-governance-observation-method.md` §6.6 | 综合指数纪律（**红线**：不评分；不排名）|
| `docs/04-data-model.md` §6 | Stage 0 边界（不扩 pgvector / RLS / partition）|
| `docs/08-mvp-plan.md` §S2.9 | 5 省 × 3 个对比地区 |
| `docs/08-mvp-plan.md` §4 Stage 3 | 比较分析与同类地区（Stage 3 范围）|
| `docs/10-acceptance-tests.md` §133 | peer_selection_justified（可解释依据）|
| `docs/33 §3.2` | `lineage.is_demo` sentinel |
| `docs/34-stage2-s20-kickoff-plan-20260825.md` §1 | "六段证据链 + 七维度观察卡 + 同类地区对比" |
| `docs/34-stage2-s20-kickoff-plan-20260825.md` §4 序 12 | S2.9 范围 |
| `docs/34-stage2-s20-kickoff-plan-20260825.md` §4.3 | 全国实时排名红线条目 |
| `docs/40-stage2-s25-inference-plan-20260826.md` §5.1 | INFERENCE/JUDGMENT 角标接驳 |
| `docs/41-stage2-s26-counterexample-plan-20260826.md` §5.1 | 反例红色 banner 接驳 |
| `docs/41-stage2-s26-counterexample-plan-20260826.md` §10.8 | 同类区间位红线 |
| `docs/42-stage2-s28-seven-dim-plan-20260826.md` §5.3 | S2.8 不接 S2.9 全量 |
| `docs/42-stage2-s28-seven-dim-plan-20260826.md` §10.8 | S2.9 同类区间显示位 |
| `schema/01-core.sql` | 既有 `geo_entity` 表（comparison_group_member FK）|

---

## 10. CC 建议（供 Cursor 审阅 / 用户裁定）

### 10.1 `comparison_group` schema 形态

| 选项 | 描述 | 选 |
|---|---|---|
| A | 独立表 + FK 到 geo_entity（per §2.1 + §2.2）| **推荐**（per docs/05 §8.1）|
| B | JSONB 字段存成员 | 简单；但难 JOIN；违反 docs/04 §3.4 行级守门原则 |

### 10.2 `selection_method` 是否含 `mahalanobis` / `propensity`

| 选项 | 描述 | 选 |
|---|---|---|
| A | CHECK 含全部 3 种（但落地刀仅 manual）| **推荐**（per §2.1；保留扩展性，但 pytest 守门仅 manual）|
| B | CHECK 仅含 manual | 简单；但 Stage 3 需 ALTER TYPE 扩枚举 |

### 10.3 `selection_justification` 守门

| 选项 | 描述 | 选 |
|---|---|---|
| A | `NOT NULL TEXT` + `CHECK (selection_justification <> '')`（per §7 风险）| **推荐**（per docs/10 §133）|
| B | 仅 NOT NULL | 空字符串可通过；pytest 守门补足 |

### 10.4 与 S2.7 EvidenceChain 接驳粒度

| 选项 | 描述 | 选 |
|---|---|---|
| A | S2.9 mart 仅展示 n_observation 等聚合列（per §5.1）| **推荐**（per `241` §SCHEMA 红线 — 不接 S2.7 UI 改动）|
| B | S2.9 mart 拆 6 段为 6 列 | 加固；需扩展 S2.7 mart |

### 10.5 与 S2.8 七维度接驳粒度

| 选项 | 描述 | 选 |
|---|---|---|
| A | S2.9 mart 仅展示 region-level 聚合（per §5.2）| **推荐**（per docs/06 §6.6 红线 — 不引入"地区×维度排名"）|
| B | S2.9 mart 拆 7 card 为 7 列 | 加固；可能引入地区×维度排名越界 |

### 10.6 评分字段（红线）

| 选项 | 描述 | 选 |
|---|---|---|
| A | 不引入评分字段（per docs/06 §6.6）| **推荐** |
| B | 引入"peer_rank"等数值 | ❌ 红线 |

### 10.7 `comparison_group_member.role_in_group` 枚举

| 选项 | 描述 | 选 |
|---|---|---|
| A | `focal` / `peer` 双值（per §2.2）| **推荐**（per docs/05 §8.2 + docs/08 §S2.9）|
| B | 不区分 focal/peer，统一为 `member` | 简单；但难 UI 区分对比基准 |

### 10.8 同类地区匹配依据维度数

| 选项 | 描述 | 选 |
|---|---|---|
| A | 4 维度（人口/区位/产业/发展阶段）（per §2.3）| **推荐**（per docs/05 §8.1）|
| B | 简化为 2 维度（人口/区位）| 简化；丢失 docs/05 §8.1 信息 |

---

— End of `docs/43` —

> 等待 Cursor 审验（预期 `243-stage0-cursor-s29-plan-audit-…md`）。
> 通过后下发落地任务（`244-stage2-s29-peer-compare-impl-tasking-…md`），进入 S2.9 实施。
> S2.9 落地可与 S2.1-full 与 S2.2-dbt/seed 与 S2.3/4/5 落地可**并行**（不同 schema 域）；等 Cursor 裁定。