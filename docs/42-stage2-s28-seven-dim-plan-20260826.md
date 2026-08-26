# 42 — Stage 2 / S2.8 / 七维度观察卡 规划

> 起草：CC · 2026-08-26 · queue_rev 92
> 前置：`234` S2.6-lite PASS；`docs/34` §4 序 11；`docs/06` §3 七维度定义；`docs/40` §5.1-5.3 INFERENCE 角标接驳；`docs/41` §5.1 反例红色 banner 接驳
> 本刀**仅规划**；不写生产 migration（per `235` §SCHEMA + 用户裁定 **D** 缩刀模式）

---

## 1. 目标

S2.8 是 Stage 2 **七维度观察卡**维度的**契约/UI 刀** — 无新表（per docs/06 §3 七维度是「证据链映射的观察维度」，不增新 schema），本刀完成**七维度卡契约 + 与六段 EvidenceChain 接驳 + 折叠/展开 UI 形态 + 评审 + 红线**的规划。落地刀（tasking 237+ 视 Cursor 审验再下发）将：

- 落地 7 张观察卡的 React 组件（每张卡 = 1 个维度）
- 落地 `mart_seven_dim_overview` dbt 模型（聚合七维度计数 + 反例守门 + evidence gaps）
- 落地 RegionCard → EvidenceChain → 七维度卡的**三段路由**
- pytest 覆盖：维度卡字段守门 / 反例红色 banner 守门 / lineage is_demo 流转守门 / 无评分字段
- docs/06 §3 七维度定义的**应用层枚举守门**（新增 `seven_dim_card` 枚举守门）

**S2.8 与 S2.5 / S2.6 / S2.7 的边界**（per `235` §SCHEMA 钉死 + docs/34 §4 序 11）：

| S2.5 关注 | S2.6 关注 | S2.7 关注 | S2.8 关注 |
|---|---|---|---|
| `inference_record` schema 形态（已交）| 反例登记 workflow（已交）| 六段 EvidenceChain UI 接驳 | 七维度卡 UI 接驳 + 折叠/展开 |
| `polarity` CHECK 守门（已交）| 反例登记最少 1 条 CONTRADICTS 守门（已交 trigger）| 段级 evidence_gaps 显示（黄 banner）| 维度级 balance_status 显示（红/黄/绿/橙 banner）|
| `mart_claim_evidence_polarity_balance` 规划（已交）| mart 应用层 + UI 最小接驳 | mart_evidence_chain 段级投影 | mart_seven_dim_overview 维度级投影 |
| `canonical_layer` 投影（已交）| `canonical_polarity` 投影（已交）| evidence gaps 投影（既有 S2.7）| 七维度 cell × claim_evidence_link JOIN 投影 |

**S2.8 不接 S2.9 对比全量**（per `235` §SCHEMA 红线）— S2.9 同类地区对比卡属 S2.9 范围。

---

## 2. 契约（七维度卡 + EvidenceChain 接驳）

### 2.0 范围声明

| 包含 | 不包含（推后续刀）|
|---|---|
| 七维度卡契约（per docs/06 §3 七维）+ UI 形态（折叠/展开）| S2.9 同类地区对比卡 |
| `mart_seven_dim_overview` 维度级投影（聚合 7 维度 × claim_evidence_link）| 新增 `seven_dim_cell` 表（lineage + cell 字段够用）|
| 与 S2.7 EvidenceChain 接驳（段级 evidence → 维度级 evidence）| S2.7 六段 UI 改动 |
| 与 S2.6 反例红色 banner 接驳（维度级 balance_status）| S2.6 反例登记 UI 改动 |
| 与 S2.5 inference 角标接驳（每维度 INFERENCE/JUDGMENT 角标）| S2.5 inference_card UI 改动 |
| 应用层 enum-style 守门（7 维度枚举 + 反例守门 + lineage is_demo）| schema ENUM（per docs/40 §2.3 平行；不引入 schema ENUM）|
| docs/06 §3 7 维度的**精确映射表**（PRD 8 项 → 框架 7 项）| 改 docs/06 §3 内容（Cursor 拥有）|

### 2.1 七维度卡契约（per docs/06 §3 + §113-119）

```yaml
# 七维度卡 schema (前端 TypeScript + 后端 mart 列对齐)
seven_dim_cards:
  - card_id: "POLICY_DELIVERY"        # 政策兑现与政务透明
    canonical_name_zh: "政策兑现与政务透明"
    canonical_name_en: "Policy Delivery & Transparency"
    primary_evidence_sources:
      - "政府工作报告"
      - "五年规划"
      - "预算报告"
      - "信息公开年报"
      - "回应率"
      - "统计修订说明"
    risk_notes:
      - "抽象承诺"
      - "目标漂移"
      - "公开 ≠ 易读"
    prd_6_3_mapping: ["政策兑现", "政务透明"]   # 合并两 PRD 项
    links_to_s27_segments: ["COMMITMENT", "PROCESS", "OUTPUT"]
  - card_id: "FISCAL_EXECUTION"        # 财政执行
    canonical_name_zh: "财政执行"
    canonical_name_en: "Fiscal Execution"
    primary_evidence_sources:
      - "决算"
      - "预算执行通报"
      - "绩效自评"
      - "审计报告"
    risk_notes:
      - "调整预算"
      - "决算时滞"
    prd_6_3_mapping: ["财政执行"]
    links_to_s27_segments: ["COMMITMENT", "PROCESS", "OUTPUT"]
  - card_id: "PROJECT_DELIVERY"        # 项目交付
    canonical_name_zh: "项目交付"
    canonical_name_en: "Project Delivery"
    primary_evidence_sources:
      - "审批平台"
      - "招投标"
      - "公共资源交易"
    risk_notes:
      - "签约注水"
      - "烂尾"
    prd_6_3_mapping: ["项目交付"]
    links_to_s27_segments: ["PROCESS", "OUTPUT"]
  - card_id: "ECONOMIC_ADAPTATION"     # 经济适应
    canonical_name_zh: "经济适应"
    canonical_name_en: "Economic Adaptation"
    primary_evidence_sources:
      - "统计公报"
      - "税收"
      - "产业用电"
      - "专利"
    risk_notes:
      - "短期波动 vs 长期趋势"
    prd_6_3_mapping: ["经济适应"]
    links_to_s27_segments: ["OUTPUT", "OUTCOME"]
  - card_id: "PUBLIC_SERVICES"         # 公共服务
    canonical_name_zh: "公共服务"
    canonical_name_en: "Public Services"
    primary_evidence_sources:
      - "教育/医疗/养老统计公报"
      - "12345"
    risk_notes:
      - "满意度抽样代表性"
    prd_6_3_mapping: ["公共服务"]
    links_to_s27_segments: ["OUTPUT", "OUTCOME"]
  - card_id: "RISK_MANAGEMENT"         # 风险管理
    canonical_name_zh: "风险管理"
    canonical_name_en: "Risk Management"
    primary_evidence_sources:
      - "债务限额"
      - "土地出让金"
      - "房地产销售"
      - "生态公报"
    risk_notes:
      - "隐性债务"
      - "报表美化"
    prd_6_3_mapping: ["风险管理"]
    links_to_s27_segments: ["INPUT", "OUTPUT"]
  - card_id: "GOAL_CONSISTENCY"        # 目标一致性
    canonical_name_zh: "目标一致性"
    canonical_name_en: "Goal Consistency"
    primary_evidence_sources:
      - "工作报告 vs 实际数据"
      - "第三方评估"
    risk_notes:
      - "因果 vs 相关"
    prd_6_3_mapping: ["目标一致性"]
    links_to_s27_segments: ["CONDITION", "COMMITMENT", "OUTPUT"]
```

### 2.2 `mart_seven_dim_overview`（每 claim × 每维度一行）

```sql
-- mart_seven_dim_overview (每 claim × 每 seven_dim_card 一行)
{{ config(materialized='view', tags=['mart', 'seven_dim']) }}

WITH claim_seven_dim AS (
    -- 1. 列出所有 claim × 7 维度笛卡尔积
    SELECT c.claim_id, c.claim_type, sd.card_id
    FROM (
        SELECT DISTINCT claim_id, claim_type
        FROM {{ ref('stg_claim_evidence_link') }}
    ) c
    CROSS JOIN (
        SELECT unnest(ARRAY[
            'POLICY_DELIVERY', 'FISCAL_EXECUTION', 'PROJECT_DELIVERY',
            'ECONOMIC_ADAPTATION', 'PUBLIC_SERVICES',
            'RISK_MANAGEMENT', 'GOAL_CONSISTENCY'
        ]) AS card_id
    ) sd
),
polarity_per_card AS (
    -- 2. 计算每 claim × 每维度 的 polarity 计数
    SELECT
        csd.claim_id,
        csd.card_id,
        COUNT(*) FILTER (WHERE cel.canonical_polarity = 'CONTRADICTS') AS n_contradicts,
        COUNT(*) FILTER (WHERE cel.canonical_polarity = 'SUPPORTS')     AS n_supports,
        COUNT(*)                                                       AS n_total
    FROM claim_seven_dim csd
    LEFT JOIN {{ ref('stg_claim_evidence_link') }} cel
        ON cel.claim_id = csd.claim_id
        -- 七维度 cell 与 claim_evidence_link 关联: 通过 geo_entity_id + observation_type
        AND cel.geo_entity_id IS NOT NULL
    GROUP BY csd.claim_id, csd.card_id
),
inference_per_card AS (
    -- 3. 计算每 claim × 每维度 的 INFERENCE / JUDGMENT 计数
    SELECT
        csd.claim_id,
        csd.card_id,
        COUNT(*) FILTER (WHERE inf.canonical_layer = 'INFERENCE')  AS n_inference,
        COUNT(*) FILTER (WHERE inf.canonical_layer = 'JUDGMENT')   AS n_judgment,
        COUNT(*) FILTER (WHERE inf.canonical_layer = 'DERIVED')    AS n_derived
    FROM claim_seven_dim csd
    LEFT JOIN {{ ref('stg_inference_record') }} inf
        ON inf.geo_entity_id IN (SELECT geo_entity_id FROM {{ ref('stg_claim_evidence_link') }} WHERE claim_id = csd.claim_id)
    GROUP BY csd.claim_id, csd.card_id
)
SELECT
    ppc.claim_id,
    ppc.card_id,
    ppc.n_contradicts,
    ppc.n_supports,
    ppc.n_total,
    CASE
        WHEN ppc.n_total = 0 THEN 'NO_EVIDENCE'
        WHEN ppc.n_contradicts = 0 THEN 'NO_CONTRADICTING_EVIDENCE'
        WHEN ppc.n_supports = 0 THEN 'NO_SUPPORTING_EVIDENCE'
        WHEN ppc.n_supports >= ppc.n_contradicts THEN 'SUPPORTS_DOMINANT'
        ELSE 'CONTRADICTS_DOMINANT'
    END AS balance_status,
    ipc.n_inference,
    ipc.n_judgment,
    ipc.n_derived,
    COALESCE(ppc.is_demo, 'true') AS is_demo
FROM polarity_per_card ppc
LEFT JOIN inference_per_card ipc
    ON ipc.claim_id = ppc.claim_id AND ipc.card_id = ppc.card_id
```

**不评分**：仅计数 + 枚举状态；不派生"维度严重度""可信度"（per docs/06 §6.6 红线 + docs/41 §10.8 红线）。

### 2.3 七维度 cell 与 S2.7 EvidenceChain 段接驳（per docs/06 §3 + docs/40 §5.1）

| seven_dim_card | S2.7 EvidenceChain 段消费 | 数据来源 |
|---|---|---|
| `POLICY_DELIVERY` | `COMMITMENT` + `PROCESS` + `OUTPUT` | policy_measure + claim_evidence_link |
| `FISCAL_EXECUTION` | `COMMITMENT` + `PROCESS` + `OUTPUT` | budget_execution + claim_evidence_link |
| `PROJECT_DELIVERY` | `PROCESS` + `OUTPUT` | project_event + claim_evidence_link |
| `ECONOMIC_ADAPTATION` | `OUTPUT` + `OUTCOME` | observation + claim_evidence_link |
| `PUBLIC_SERVICES` | `OUTPUT` + `OUTCOME` | observation + claim_evidence_link |
| `RISK_MANAGEMENT` | `INPUT` + `OUTPUT` | source_document + claim_evidence_link |
| `GOAL_CONSISTENCY` | `CONDITION` + `COMMITMENT` + `OUTPUT` | inference_record + claim_evidence_link |

### 2.4 七维度 cell 与 S2.6 反例守门接驳（per docs/41 §5.1）

| balance_status | UI 渲染 | 接驳 |
|---|---|---|
| `NO_EVIDENCE` | 灰色 "无证据" | docs/06 §2.7 evidence_gaps 处理（黄 banner）|
| `NO_CONTRADICTING_EVIDENCE` | 🔴 红色 banner "反例未登记" | docs/41 §5.1 + Gate 2 §3.2 硬卡 |
| `NO_SUPPORTING_EVIDENCE` | 🟡 黄色 banner "支持证据缺失" | 评审层 catch |
| `SUPPORTS_DOMINANT` | 🟢 绿色 "支持证据占优" | docs/41 §2.4 |
| `CONTRADICTS_DOMINANT` | 🟠 橙色 "反例占优" | docs/41 §2.4 — 不评分 |

### 2.5 七维度 cell 与 S2.5 inference 角标接驳（per docs/40 §5.1）

| 角标 | 显示 | 接驳 |
|---|---|---|
| INFERENCE | 蓝 | docs/40 §5.1 `canonical_layer = 'INFERENCE'` |
| JUDGMENT | 橙 | docs/40 §5.1 `canonical_layer = 'JUDGMENT'` |
| DERIVED | 灰 | docs/40 §5.1 `canonical_layer = 'DERIVED'` |
| **多角标聚合** | "2 INFERENCE / 1 JUDGMENT" | 计数显示；不评分 |

### 2.6 应用层守门（per docs/06 §3 + docs/04 §3.9 + docs/41 §2.4）

```python
# 应用层 enum-style 守门 (per docs/40 §2.3 + docs/41 §2.3 平行)
SEVEN_DIM_CARDS = {
    "POLICY_DELIVERY", "FISCAL_EXECUTION", "PROJECT_DELIVERY",
    "ECONOMIC_ADAPTATION", "PUBLIC_SERVICES",
    "RISK_MANAGEMENT", "GOAL_CONSISTENCY",
}

BALANCE_STATUS = {
    "NO_EVIDENCE", "NO_CONTRADICTING_EVIDENCE",
    "NO_SUPPORTING_EVIDENCE", "SUPPORTS_DOMINANT",
    "CONTRADICTS_DOMINANT",
}

# ❌ 不引入 schema ENUM
# ❌ 不引入 score / rating / total_score 字段
# ✅ dbt model WHERE card_id IN SEVEN_DIM_CARDS 守门
# ✅ pytest 显式断言 SEVEN_DIM_CARDS / BALANCE_STATUS
```

---

## 3. UI 形态（七维度卡折叠/展开 + 与六段接驳）

### 3.1 七维度卡网格（折叠态）

```
┌─────────────────────────────────────────────────────────────────┐
│  RegionCard 顶部: [反例缺失 🔴] / [INFERENCE ×2 蓝] / [JUDGMENT ×1 橙] │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐         │
│  │ 政策兑现与政务 │  │ 财政执行    │  │ 项目交付    │         │
│  │ 🔴 反例未登记 │  │ 🟢 支持占优 │  │ 🟡 支持缺失 │         │
│  │ 3 支持 / 0 反 │  │ 5 支持 / 1 反│  │ 0 支持 / 2 反│         │
│  │ 2 INFERENCE  │  │ 1 INFERENCE │  │ 1 JUDGMENT  │         │
│  │ [展开 ▼]     │  │ [展开 ▼]    │  │ [展开 ▼]    │         │
│  └──────────────┘  └──────────────┘  └──────────────┘         │
│                                                                 │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐         │
│  │ 经济适应    │  │ 公共服务    │  │ 风险管理    │         │
│  │ 🟢 支持占优 │  │ 🟡 支持缺失 │  │ 🔴 反例未登记│         │
│  │ ...         │  │ ...          │  │ ...         │         │
│  └──────────────┘  └──────────────┘  └──────────────┘         │
│                                                                 │
│  ┌──────────────┐                                                │
│  │ 目标一致性  │                                                │
│  │ 🟢 支持占优 │                                                │
│  └──────────────┘                                                │
└─────────────────────────────────────────────────────────────────┘
```

### 3.2 七维度卡展开态

```
┌──────────────────────────────────────────────────────────────────┐
│ [政策兑现与政务透明 (Policy Delivery & Transparency)]      [收起 ▲]│
├──────────────────────────────────────────────────────────────────┤
│ 主要证据来源: 政府工作报告 / 五年规划 / 预算报告 / 信息公开年报 │
│ 风险提示: 抽象承诺 / 目标漂移 / 公开 ≠ 易读                     │
│                                                                  │
│ 反例守门: 🔴 反例未登记 (per Gate 2 §3.2 硬要求)               │
│   → "至少 1 个反例被显式登记" (per docs/34 §2)                  │
│   → 跳转反例登记 [admin] / [reviewer] 角色                       │
│                                                                  │
│ evidence gaps: 3 段未覆盖 (per docs/06 §2.7)                    │
│   → CONDITION 段: ✓ / COMMITMENT 段: ✗ / PROCESS 段: ✗          │
│   → OUTPUT 段: ✗ / OUTCOME 段: ✓ / FEEDBACK 段: ✗              │
│                                                                  │
│ INFERENCE 角标: 2 INFERENCE (蓝) + 1 JUDGMENT (橙)              │
│   → [跳转到该 dimension 的 inference 列表]                      │
│                                                                  │
│ EvidenceChain 接驳: COMMITMENT 段 / OUTPUT 段                    │
│   → [展开六段证据链 ▼]                                          │
│                                                                  │
│ 同类区间: (S2.9 范围; 此刀不接)                                  │
│                                                                  │
│ is_demo: true / false (per docs/33 §3.2 sentinel)               │
└──────────────────────────────────────────────────────────────────┘
```

### 3.3 React 组件最小形态（落地刀产出）

```tsx
// frontend/components/seven-dim/SevenDimGrid.tsx — 落地刀产出
interface SevenDimCardProps {
    claimId: string;
    cardId: SevenDimCardId;          // 7 枚举
    nSupports: number;
    nContradicts: number;
    nInference: number;
    nJudgment: number;
    nDerived: number;
    balanceStatus: BalanceStatus;    // 5 枚举
    isDemo: boolean;
    expanded?: boolean;
}

// 折叠态: card + balance_status badge + counter
// 展开态: card + 主要证据来源 + 风险提示 + 反例红色 banner +
//        evidence gaps 黄 banner + INFERENCE 角标 + EvidenceChain 接驳链接
```

### 3.4 与 S2.7 EvidenceChain 路由接驳（落地刀）

```
RegionCard
  ↓ click 七维度卡
SevenDimCard (展开)
  ↓ click "EvidenceChain 接驳"
EvidenceChain (S2.7 既有)
  ↓ click 单段
SegmentDetail
  ↓ click "关联 claim"
ClaimDetail (per docs/04 §3.4)
  ↓ click "反例登记"
CounterexampleRegistration (S2.6 既有 — docs/41 §3.3)
```

---

## 4. 首批入库策略

> **本刀仅规划**；落地刀 (tasking 237+) 视 Cursor 审验再下发。

### 4.1 草拟：首批 ≤N 行 claim × 维度 cell

| 范围 | 数量 | 数据来源 | 红线 |
|---|---|---|---|
| INFERENCE claim (per S2.5) | ≤6 × 7 = 42 cell | 引用 S2.5 `inference_record` | 不爬网 |
| POLICY claim (per S2.2) | ≤4 × 7 = 28 cell | 引用 S2.2 `policy_measure` | 不爬网 |
| BUDGET claim (per S2.4) | ≤4 × 7 = 28 cell | 引用 S2.4 `budget_execution` | 不爬网 |
| PROJECT claim (per S2.3) | ≤3 × 7 = 21 cell | 引用 S2.3 `project_event` | 不爬网 |
| PERSON claim (per S2.1) | ≤3 × 7 = 21 cell | 引用 S2.1 `person` / `tenure` | 不爬网 |
| **合计** | ≤20 claim × 7 维度 = **140 cell** | | **不爬网** |

### 4.2 polarity 守门（per docs/06 §6 + docs/41 §2.4 + Gate 2 §3.2）

| 限制 | 上限 | 理由 |
|---|---|---|
| 每 claim × 维度 cell CONTRADICTS | ≥1（**全局每 claim ≥1** — 由 trigger 守门，per migration 013）| Gate 2 §3.2 |
| 每 claim × 维度 cell SUPPORTS | ≥1 | docs/41 §4.2 + docs/06 §6.6 演示守门 |
| 维度 cell SUPPORTS : CONTRADICTS | 建议 2:1 ~ 3:1 | 演示守门非形式化 |

### 4.3 `is_demo` 流转（per docs/33 §3.2 sentinel + docs/41 §4.3 平行）

| 阶段 | mart 七维度 cell `is_demo` |
|---|---|
| DRAFT | `"true"` |
| 公开登记后 | `"false"` |

> 注：mart_seven_dim_overview 输出列名 `is_demo`，源自 `claim_evidence_link.lineage->>'is_demo'` 聚合。

### 4.4 稳定 cell 标识（per S1.12 + docs/40 §4.4 平行）

| mart cell | UUID 家族 |
|---|---|
| `mart_seven_dim_overview` cell | 无 UUID；用 `(claim_id, card_id)` 复合主键 |
| `seven_dim_card` 枚举映射 | 静态 7 项；不存表 |

---

## 5. 与 S2.7 / S2.9 接驳

### 5.1 与 S2.7 EvidenceChain 段接驳（per §3.4 + docs/40 §5.1）

| 段 | 七维度 cell 消费 |
|---|---|
| `CONDITION` | GOAL_CONSISTENCY |
| `COMMITMENT` | POLICY_DELIVERY + FISCAL_EXECUTION + GOAL_CONSISTENCY |
| `PROCESS` | POLICY_DELIVERY + FISCAL_EXECUTION + PROJECT_DELIVERY |
| `OUTPUT` | POLICY_DELIVERY + FISCAL_EXECUTION + PROJECT_DELIVERY + ECONOMIC_ADAPTATION + PUBLIC_SERVICES + RISK_MANAGEMENT + GOAL_CONSISTENCY |
| `OUTCOME` | ECONOMIC_ADAPTATION + PUBLIC_SERVICES |
| `FEEDBACK` | (无七维度 cell 消费；属 S2.7 内部反馈环) |

### 5.2 与 S2.6 反例守门接驳（per docs/41 §5.1）

```sql
-- mart_seven_dim_overview 已聚合每 cell 的 n_contradicts;
-- mart_claim_evidence_polarity_balance 已聚合每 claim 的 n_contradicts;
-- 七维度 cell 红色 banner 复用 docs/41 §2.4 / §5.1
-- ❌ 不重新触发 assert_min_one_contradicts() trigger (DB 已守门)
-- ✅ mart 视图层投影 balance_status 5 枚举
```

### 5.3 不接 S2.9 对比全量（per `235` §SCHEMA 钉死红线）

**S2.9 同类地区对比卡**属 S2.9 范围；本刀 S2.8 仅规划七维度卡本体；不接"同类区间"显示（per §3.2 "同类区间: (S2.9 范围; 此刀不接)"）。

### 5.4 验证（落地刀）

```bash
# 1. mart 行数 = seed cell 数 (per §4.1 ≤ 140)
PGPASSWORD=postgres psql -h 127.0.0.1 -p 55440 -U postgres -d cegr_test \
    -c "SELECT COUNT(*) FROM cegr_staging.mart_seven_dim_overview;"
# 预期: 140

# 2. card_id 分布 (per §2.1 7 枚举)
PGPASSWORD=postgres psql ... \
    -c "SELECT card_id, COUNT(*) FROM cegr_staging.mart_seven_dim_overview GROUP BY card_id;"
# 预期: 7 行 × 20 cell = 140

# 3. balance_status 守门 (per §2.4 + Gate 2 §3.2)
PGPASSWORD=postgres psql ... \
    -c "SELECT balance_status, COUNT(*) FROM cegr_staging.mart_seven_dim_overview GROUP BY balance_status;"
# 预期: NO_CONTRADICTING_EVIDENCE = 0 (全局每 claim ≥1 由 trigger 守门)

# 4. INFERENCE / JUDGMENT 角标 (per §2.5)
PGPASSWORD=postgres psql ... \
    -c "SELECT card_id, SUM(n_inference), SUM(n_judgment), SUM(n_derived)
        FROM cegr_staging.mart_seven_dim_overview
        GROUP BY card_id;"

# 5. is_demo 流转 (per §4.3)
PGPASSWORD=postgres psql ... \
    -c "SELECT
          COUNT(*) FILTER (WHERE is_demo = 'true') AS n_is_demo_true,
          COUNT(*) FILTER (WHERE is_demo = 'false') AS n_is_demo_false
        FROM cegr_staging.mart_seven_dim_overview;"

# 6. 七维度 cell 红色 banner 触发器 (per docs/41 §5.1 + §2.5)
PGPASSWORD=postgres psql ... \
    -c "DELETE FROM cegr.claim_evidence_link
        WHERE canonical_polarity = 'CONTRADICTS'
          AND claim_id = (SELECT claim_id FROM cegr.claim_evidence_link
                          WHERE canonical_polarity = 'CONTRADICTS'
                          ORDER BY created_at LIMIT 1)
          AND id = (SELECT id FROM cegr.claim_evidence_link
                    WHERE canonical_polarity = 'CONTRADICTS'
                    ORDER BY created_at LIMIT 1);"
# 预期: RAISE EXCEPTION (per migration 013 + docs/41 §2.5)
```

---

## 6. 验收清单

| # | 项 | 落地刀验证方式 |
|---|---|---|
| 1 | docs/06 §3 七维度 7 项 + PRD 8 项映射表（per §2.1）| markdown 文本守门 |
| 2 | `mart_seven_dim_overview` 视图可 query；card_id ∈ 7 枚举守门 | dbt run + SQL DISTINCT |
| 3 | balance_status ∈ 5 枚举守门（NO_EVIDENCE/NO_CONTRADICTING_EVIDENCE/NO_SUPPORTING_EVIDENCE/SUPPORTS_DOMINANT/CONTRADICTS_DOMINANT）| SQL DISTINCT |
| 4 | 七维度 cell 红色 banner（NO_CONTRADICTING_EVIDENCE = 0）| SQL COUNT |
| 5 | 与 S2.7 EvidenceChain 段接驳（per §5.1 表）| React 路由 E2E |
| 6 | 与 S2.6 反例红色 banner 接驳（per §5.2）| React 路由 E2E |
| 7 | 与 S2.5 INFERENCE/JUDGMENT 角标接驳（per §5 + §2.5）| SQL + UI |
| 8 | 折叠态：card + balance_status badge + counter | frontend browser E2E |
| 9 | 展开态：card + 主要证据来源 + 风险提示 + 反例红色 banner + evidence gaps 黄 banner + INFERENCE 角标 + EvidenceChain 接驳链接 | frontend browser E2E |
| 10 | `lineage.is_demo` 流转：cell mart 输出列含 is_demo | SQL COUNT |
| 11 | 不引入 schema ENUM（应用层 enum-style 守门）| grep "CREATE TYPE" schema/migrations/ |
| 12 | 不引入 score / rating / total_score / rank 列 | grep |
| 13 | 不接 S2.9 同类对比全量（per `235` §SCHEMA 红线）| code review |
| 14 | 不接 S2.7 六段 UI 改动（per `235` §SCHEMA 红线）| code review |
| 15 | 新增 pytest `tests/test_seven_dim_s28lite.py` ≥5 cases 全过 | pytest -v |
| 16 | pack invariant 552 → 552+N | JSON 解析守门 |
| 17 | smoke-check 仍 PASS（无 frontend 改动）| python3 frontend/smoke-check.py |
| 18 | 既有 s21lite..s26lite 套件仍绿 | pytest tests/test_*_s*lite.py -q |
| 19 | 触发器守门：删最后 CONTRADICTS 行抛异常（per docs/41 §5.4 + migration 013）| psql DELETE 验证 |

---

## 7. 关键风险与回滚

| 风险 | 触发条件 | 回滚策略 |
|---|---|---|
| 七维度 cell `NO_CONTRADICTING_EVIDENCE` 数 ≠ 0 | migration 013 trigger 未部署；或 claim_id 无 CONTRADICTS 行 | pytest case 4 显式断言；触发器部署到 `BEFORE DELETE` 而非 `AFTER`；记录 audit log |
| 七维度 cell SUPPORTS : CONTRADICTS 失衡 | seed 数据未按 2:1 配比 | pytest case 显式断言分布；seed 脚本先 dry-run |
| `card_id` 越界（PRD 8 项 vs 框架 7 项）| 应用层 enum-style 守门缺失 | pytest case 显式断言 `card_id ∈ 7 枚举`；dbt WHERE 守门 |
| `balance_status` 越界（5 枚举）| CASE 表达式缺 ELSE | pytest case 显式断言；CASE END AS balance_status NOT NULL |
| 七维度卡 evidence_gaps 与六段 EvidenceChain 不对齐 | 段级 evidence gaps 与维度级 evidence 不同源 | §5.1 映射表硬钉；pytest case 显式断言 |
| 评分字段被引入（"维度严重度""维度可信度"）| docs/06 §6.6 红线被绕过 | pytest FORBIDDEN_COLUMN_PATTERNS 守门；grep 双层守门 |
| S2.8 接 S2.9 全量对比（越界）| S2.9 同类区间被意外引入 | code review；§5.3 红线 |
| `is_demo` 流转被绕过（admin 直接 UPDATE）| DB 写权限 | 既有 trigger 守门（per docs/33 §3.2）|

---

## 8. 不做什么（本刀 S2.8 边界；推后续刀）

| ❌ | 推到 |
|---|---|
| ❌ 写生产 migration（**仅规划**）| S2.8 落地刀（tasking 237+）|
| ❌ dbt `mart_seven_dim_overview` + 7 dbt source yml | S2.8 落地刀 |
| ❌ 首批 ≤140 cell seed | S2.8 落地刀（**严禁爬网**）|
| ❌ React SevenDimGrid + 七维度卡组件 + EvidenceChain 接驳路由 | S2.8 落地刀 |
| ❌ S2.9 同类地区对比卡（**仅 §3.2 同类区间位保留**）| S2.9 |
| ❌ 改 docs/06 §3 内容（Cursor 拥有）| — |
| ❌ 改七维度定义（合并/拆分 PRD 6.3 8 项）| — |
| ❌ S2.7 六段 EvidenceChain UI 改动 | S2.7 |
| ❌ S2.5 inference_card UI 改动 | S2.5 |
| ❌ S2.6 反例登记 UI 改动 | S2.6 |
| ❌ `score` / `rating` / `rank` / `total_score` / `confidence_score` / `credibility_score` 任一字段 | **红线**（per docs/06 §6.6 + docs/41 §10.8）|
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
| `docs/06-governance-observation-method.md` §3 | 七维度观察卡定义（7 维度 + PRD 8 项映射表）|
| `docs/06-governance-observation-method.md` §2.7 | evidence_gaps 处理（黄 banner）|
| `docs/06-governance-observation-method.md` §4 L1-L7 | inference_method 角标 |
| `docs/06-governance-observation-method.md` §6.6 | 综合指数纪律（**红线**：不评分；不排名）|
| `docs/04-data-model.md` §3.4 | observation_revision append-only 平行 |
| `docs/04-data-model.md` §3.9 | `claim_evidence_link.polarity` SUPPORTS / CONTRADICTS 双显（防确认偏差）|
| `docs/04-data-model.md` §6 | Stage 0 边界（不扩 pgvector / RLS / partition）|
| `docs/08-mvp-plan.md` §77 序 11 | S2.8 七维度观察卡 UI (W5-W7) |
| `docs/08-mvp-plan.md` §85 | 验收："七维度观察卡可展开" |
| `docs/33 §3.2` | `lineage.is_demo` sentinel |
| `docs/34-stage2-s20-kickoff-plan-20260825.md` §1 | "六段证据链 + 七维度观察卡" |
| `docs/34-stage2-s20-kickoff-plan-20260825.md` §4 序 11 | S2.8 范围 |
| `docs/40-stage2-s25-inference-plan-20260826.md` §5.1 | INFERENCE/JUDGMENT 角标接驳 |
| `docs/41-stage2-s26-counterexample-plan-20260826.md` §5.1 | 反例红色 banner 接驳 |
| `schema/01-core.sql` §932-940 | 既有 `uncertainty_record` 表（S2.6 平行）|
| `schema/01-core.sql` §956-966 | 既有 `claim_evidence_link` 表（S2.6 + 012 + 013 已加列 + trigger）|
| `schema/migrations/012_inference_alignment.sql` | `claim_evidence_link` +5 列（S2.5 已交）|
| `schema/migrations/013_counterexample_gate.sql` | 反例守门触发器（S2.6-lite 已交）|

---

## 10. CC 建议（供 Cursor 审阅 / 用户裁定）

### 10.1 七维度 cell 投影策略

| 选项 | 描述 | 选 |
|---|---|---|
| A | 笛卡尔积：每 claim × 7 维度 = 7 cell；空 cell 显示 NO_EVIDENCE | **推荐**（per §2.2 CTE）|
| B | 仅投影有 evidence 的 cell（稀疏表）| cell 数 ≤ 7 × claim 数；UI 折叠态需特殊处理"未覆盖维度" |

### 10.2 card_id 与 claim_evidence_link 关联键

| 选项 | 描述 | 选 |
|---|---|---|
| A | `cel.geo_entity_id` 关联（per §2.2 CTE LEFT JOIN）| **推荐**（简单）|
| B | 通过 `observation_type`/`policy_type`/`budget_type`/`project_type` 显式枚举关联 | 加固；需扩展 Stage 2 schema |

### 10.3 INFERENCE / JUDGMENT 角标聚合显示

| 选项 | 描述 | 选 |
|---|---|---|
| A | 单角标（取主要 layer）| 简化；丢失多角度信息 |
| B | 多角标聚合 "2 INFERENCE / 1 JUDGMENT" | **推荐**（per §3.1 + §2.5）|

### 10.4 balance_status 5 枚举是否含 NO_EVIDENCE

| 选项 | 描述 | 选 |
|---|---|---|
| A | 含 NO_EVIDENCE（空 cell 显式标注）| **推荐**（per §2.4）|
| B | 不含 NO_EVIDENCE（空 cell 不进 mart）| UI 折叠态难处理 |

### 10.5 七维度卡 evidence_gaps 显示来源

| 选项 | 描述 | 选 |
|---|---|---|
| A | 复用 S2.7 evidence_gaps 段级（per §3.2）| **推荐**（per §5.1）|
| B | 维度级独立 evidence_gaps（更细粒度）| 加固；需扩展 mart |

### 10.6 评分字段（红线）

| 选项 | 描述 | 选 |
|---|---|---|
| A | 不引入评分字段（per docs/06 §6.6）| **推荐** |
| B | 引入"维度严重度"等数值 | ❌ 红线 |

### 10.7 `card_id` 落地形态

| 选项 | 描述 | 选 |
|---|---|---|
| A | 应用层 enum-style 守门（per §2.6）| **推荐**（per docs/40 §2.3 + docs/41 §2.3 平行；不引入 schema ENUM）|
| B | schema-level CHECK + ENUM type | 加固；migration 复杂度↑ |

### 10.8 同类区间显示位（per `235` §SCHEMA 红线）

| 选项 | 描述 | 选 |
|---|---|---|
| A | 同类区间位保留占位 + 注 "(S2.9 范围; 此刀不接)" | **推荐**（per §3.2）|
| B | 直接隐藏同类区间位 | S2.9 接驳时再显示 |

---

— End of `docs/42` —

> 等待 Cursor 审验（预期 `237-stage0-cursor-s28-plan-audit-…md`）。
> 通过后下发落地任务（`238-stage2-s28-seven-dim-impl-tasking-…md`），进入 S2.8 实施。
> S2.8 落地可与 S2.1-full 与 S2.2-dbt/seed 与 S2.3/4/5 落地可**并行**（不同 schema 域）；等 Cursor 裁定。