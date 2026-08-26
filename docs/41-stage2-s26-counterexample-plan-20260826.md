# 41 — Stage 2 / S2.6 / 反例登记 (counterexample registration) 规划

> 起草：CC · 2026-08-26 · queue_rev 90
> 前置：`228` S2.5-lite PASS；`docs/34` §2 Gate 2 §3.2 反例硬要求 + §4 序 10；`docs/04` §3.9 正反证据双显；`docs/06` §6.6 综合指数纪律；`docs/40` §2.5/§3.4/§10.6 反例守门；`schema/01-core.sql` §956-969 + §932-940
> 本刀**仅规划**；不写生产 migration（per `229` §SCHEMA + 用户裁定 **D** 缩刀模式）

---

## 1. 目标

S2.6 是 Stage 2 「反例登记」维度的**流程刀** — 表已存在（`claim_evidence_link` 由 migration 012 扩列 + `uncertainty_record` 既有），本刀完成**反例登记 workflow + UI 最小形态 + 评审审核机制**的规划。落地刀（tasking 230+ 视 Cursor 审验再下发）将：

- 落地 S2.6 反例登记 admin UI（S2.0.2 admin_upload 模式延伸；非 admin 角色只能"提议"）
- 落地 `mart_claim_evidence_polarity_balance` dbt 模型（per docs/40 §3.4 平行）
- 落地 `mart_counterexample_overview`（Gate 2 §3.2 硬要求视图）
- 落地 reviewer 审核工作流（`uncertainty_record.uncertainty_type = 'COUNTEREXAMPLE_PENDING_REVIEW'` 中间态）
- pytest 覆盖：反例守门 / reviewer 闭环 / `lineage.is_demo` 守门 / 无评分字段

**S2.6 与 S2.5 的边界**（per `229` §SCHEMA 钉死 + docs/40 §2.0）：

| S2.5 关注 | S2.6 关注 |
|---|---|
| `inference_record` + `claim_evidence_link` schema 形态（已交）| 反例登记 workflow（评审 / admin / 时间窗口）|
| `polarity` CHECK 守门（已交）| 反例登记**最少 1 条 CONTRADICTS** 应用层守门 |
| `mart_claim_evidence_polarity_balance` 规划（已交）| 该 mart 的应用 + UI 红色 banner 接驳 |

---

## 2. 契约（workflow + 消费形态）

### 2.0 范围声明

| 包含 | 不包含（推后续刀）|
|---|---|
| 反例登记 workflow 形态（draft → pending_review → approved / rejected）| S2.8 七维度观察卡全量接驳 |
| `mart_claim_evidence_polarity_balance` 应用层 + UI 最小接驳 | `mart_counterexample_overview` 全量搜索（属 Gate 2 §3.2 评审期）|
| `uncertainty_record` 作为反例审核中间态载体（既有）| 新增 `evidence_audit_trail` 表（推迟；lineage 字段够用）|
| reviewer 审核机制（admin role 闭环）| 公开 API 暴露反例（admin-only）|
| 应用层守门：每条 claim 至少 1 条 CONTRADICTS（per docs/04 §3.9 + docs/40 §3.4）| pgvector / RLS / partition（per docs/04 §6）|

### 2.1 反例登记 workflow（5 阶段）

```
┌──────────┐    ┌──────────────┐    ┌──────────────┐    ┌──────────┐
│ 1.DRAFT  │───▶│2.PENDING_    │───▶│3.APPROVED    │───▶│4.PUBLISHED│
│ 起草    │    │  REVIEW      │    │  (admin)    │    │ (UI 可见)│
└──────────┘    └──────────────┘    └──────────────┘    └──────────┘
     │                  │                  │
     ▼                  ▼                  ▼
┌──────────┐    ┌──────────────┐    ┌──────────┐
│ 0.WITHDRAWN│  │ 5.REJECTED   │    │ 6.ARCHIVED│
│ (作者撤回)│  │ (reviewer 拒)│    │ (过期)    │
└──────────┘    └──────────────┘    └──────────┘
```

**关键约束**（per docs/04 §3.9 + docs/06 §6.6）：

| 阶段 | 必填字段 | 红线 |
|---|---|---|
| **1.DRAFT** | `claim_id` / `claim_type` / `evidence_id` / `evidence_type` / `polarity` / `note` / `lineage.is_demo` | `polarity` 必 ∈ `{SUPPORTS, CONTRADICTS}`（schema CHECK 锁定）|
| **2.PENDING_REVIEW** | DRAFT 全字段 + `uncertainty_record.target_id = claim_evidence_link.id` + `uncertainty_type = 'COUNTEREXAMPLE_PENDING_REVIEW'` | `uncertainty_record.impact_note` 必填 ≥10 字（评审层 catch）|
| **3.APPROVED** | PENDING 全字段 + `reviewer_id` + `review_timestamp` / `uncertainty_record.description` 追加审核意见 | ❌ **不引入** score 字段（per docs/06 §6.6 红线）|
| **4.PUBLISHED** | APPROVED 全字段 + `lineage.is_demo` 在落地时统一 `"false"`（真实登记）| ❌ **不**对 reviewer 暴露 PAT |
| **0.WITHDRAWN / 5.REJECTED / 6.ARCHIVED** | 终态；保留 `lineage` audit trail | ❌ **不**硬删除（append-only per docs/04 §3.4 + §3.9）|

### 2.2 `claim_evidence_link` 反例登记消费形态（per docs/40 §2.2 + migration 012）

```sql
-- 既有 (01-core.sql §956-966) + 012 加 5 列
-- 反例登记核心字段:
--   polarity ENUM(SUPPORTS, CONTRADICTS)   ← schema CHECK 锁定
--   canonical_polarity TEXT NULL            ← 投影 enum-style (migration 012)
--   evidence_strength TEXT NULL             ← STRONG/MODERATE/WEAK/UNRATED (per docs/40 §2.2 红线)
--   lineage JSONB NULL                      ← audit trail (R3-E provenance + audit status)
--   claim_evidence_hash_canonical TEXT NULL ← 跨修订 SHA (R12-A de-dupe)
--   geo_entity_id UUID NULL                 ← 适用范围 (per docs/40 §2.2)
```

**反例登记落地刀**必须满足：

| 约束 | 来源 | 落地刀应对 |
|---|---|---|
| 每条 `claim_id` 至少 1 条 `polarity = CONTRADICTS` | docs/04 §3.9 + Gate 2 §3.2 | 应用层 trigger 函数 `assert_min_one_contradicts()` 在 INSERT/UPDATE 后调用 |
| `polarity` ∈ `{SUPPORTS, CONTRADICTS}` | schema CHECK 锁定 | 既有 CHECK（不动）|
| `canonical_polarity` 与 `polarity` 一致 | docs/40 §2.2 应用层守门 | 落地刀 BEFORE INSERT trigger 函数同步 |
| `evidence_strength` 不数值化 | docs/06 §6.6 红线 | 应用层 enum-style 守门（不引入 score 字段）|
| `lineage.is_demo` 默认 `"true"`；reviewer APPROVED 后 flip 到 `"false"` | docs/33 §3.2 sentinel | 落地刀 APPROVED 触发器 flip；REVOKE 后恢复 audit |

### 2.3 `uncertainty_record` 反例审核中间态（per docs/04 + 01-core.sql §932-940）

```sql
-- 既有 (01-core.sql §932-940); 本刀不扩列
-- 反例审核中间态使用形态:
--   target_type     = 'CLAIM_EVIDENCE_LINK'
--   target_id       = claim_evidence_link.id
--   uncertainty_type = 'COUNTEREXAMPLE_PENDING_REVIEW' | 'COUNTEREXAMPLE_APPROVED' | 'COUNTEREXAMPLE_REJECTED'
--   description     = 审核意见 ≥10 字
--   impact_note     = 反例的关联影响（如"反例驳斥原 claim 在 2023 年 Q2 数据"）
--   created_at      = 自动
```

**新增 `uncertainty_type` 枚举值**（应用层守门，不引入 schema ENUM）：

| 值 | 语义 | docs/40 §2.3 平行 |
|---|---|---|
| `COUNTEREXAMPLE_PENDING_REVIEW` | 反例登记待审 | `OBSERVATION_REVISION_PENDING` 平行 |
| `COUNTEREXAMPLE_APPROVED` | 反例登记已通过 | `OBSERVATION_REVISION_APPROVED` 平行 |
| `COUNTEREXAMPLE_REJECTED` | 反例登记被拒（reviewer 否决）| `OBSERVATION_REVISION_REJECTED` 平行 |
| `COUNTEREXAMPLE_WITHDRAWN` | 反例登记被作者撤回 | — |

### 2.4 反例守门三态（per docs/40 §3.4 + Gate 2 §3.2）

`mart_claim_evidence_polarity_balance.balance_status` 枚举值：

| 值 | 触发条件 | UI 渲染 |
|---|---|---|
| `NO_CONTRADICTING_EVIDENCE` | `COUNT(CONTRADICTS) = 0` | 🔴 红色 banner "反例未登记" — **Gate 2 §3.2 硬卡** |
| `NO_SUPPORTING_EVIDENCE` | `COUNT(SUPPORTS) = 0` | 🟡 黄色 banner "支持证据缺失" — 评审层 catch |
| `SUPPORTS_DOMINANT` | `SUPPORTS >= CONTRADICTS` | 🟢 绿色 "支持证据占优" |
| `CONTRADICTS_DOMINANT` | `CONTRADICTS > SUPPORTS` | 🟠 橙色 "反例占优" — 不评分；仅供评审参考 |

### 2.5 应用层守门函数（落地刀必出）

```sql
-- 触发器函数: assert_min_one_contradicts()
-- 时机: AFTER INSERT OR UPDATE ON claim_evidence_link
-- 动作: 若该 claim_id 删后 COUNT(CONTRADICTS WHERE claim_id = ...) = 0 → RAISE EXCEPTION
CREATE OR REPLACE FUNCTION assert_min_one_contradicts()
RETURNS TRIGGER AS $$
DECLARE
    n_contradicts INTEGER;
    claim_uuid UUID;
BEGIN
    claim_uuid := COALESCE(NEW.claim_id, OLD.claim_id);
    SELECT COUNT(*)
      INTO n_contradicts
      FROM claim_evidence_link
     WHERE claim_id = claim_uuid
       AND canonical_polarity = 'CONTRADICTS';
    IF n_contradicts = 0 THEN
        RAISE EXCEPTION 'gate 2 §3.2 violation: claim % has zero CONTRADICTS rows after this change', claim_uuid;
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;
```

**红线**：
- ❌ 不引入跨行 CHECK 约束（PostgreSQL 不支持 subquery CHECK）
- ✅ 触发器函数 + 触发器 + 应用层 wrapper 三重守门

---

## 3. UI 最小形态（落地刀 mock 即可）

### 3.1 反例登记提交表单（admin_upload 模式延伸）

```tsx
// frontend/app/admin/counterexample/new/page.tsx — 落地刀产出
// 字段:
<form>
  <Field name="claim_id" type="uuid" required />        // 选已有 claim
  <Field name="claim_type" type="enum" required />     // INFERENCE / POLICY / BUDGET / PROJECT / PERSON / OTHER
  <Field name="evidence_id" type="uuid" required />     // 引用既有 observation / policy_measure / budget_execution / project_event
  <Field name="evidence_type" type="enum" required />
  <Field name="polarity" type="enum" required          // SUPPORTS / CONTRADICTS — schema CHECK 锁
          enumOptions={['SUPPORTS', 'CONTRADICTS']} />
  <Field name="canonical_polarity" type="enum" required // 落地刀同步自动填
          defaultValue={polarity} />
  <Field name="evidence_strength" type="enum"          // STRONG / MODERATE / WEAK / UNRATED
          enumOptions={['STRONG', 'MODERATE', 'WEAK', 'UNRATED']} />
  <Field name="note" type="textarea" required minLength={20} />  // ≥20 字
  <Field name="geo_entity_id" type="uuid" optional />  // 适用范围
  <Submit role={['admin', 'reviewer']} />              // 仅 admin / reviewer 角色
</form>
```

### 3.2 反例登记列表 + 红色 banner（Gate 2 §3.2 接驳）

```tsx
// frontend/app/regions/[geo]/counterexamples/page.tsx — 落地刀产出
// 顶部: NO_CONTRADICTING_EVIDENCE 红色 banner (per mart_claim_evidence_polarity_balance)
// 中部: 反例列表 (per claim 维度聚合)
// 底部: 反例登记提交按钮 (admin / reviewer 角色)
```

### 3.3 reviewer 审核界面（落地刀）

```tsx
// frontend/app/admin/counterexample/review/[id]/page.tsx — 落地刀产出
// reviewer 操作:
//   - APPROVE  → uncertainty_record.description 追加审核意见 + flip lineage.is_demo false
//   - REJECT   → uncertainty_record.description 写拒因 + 留 lineage.is_demo true
//   - WITHDRAW → 作者可撤回 (仅 claim_evidence_link.created_by = current_user)
```

---

## 4. 首批入库策略

> **本刀仅规划**；落地刀 (tasking 230+) 视 Cursor 审验再下发。

### 4.1 草拟：首批 ≤N 行反例登记

| claim 类型 | 数量 | 数据来源 | 红线 |
|---|---|---|---|
| INFERENCE (per S2.5 规划) | ≤6 | hand-curated JSON；引用 S2.5 落地刀 `inference_record` 行 | 不爬网 |
| POLICY (per S2.2 规划) | ≤4 | hand-curated JSON；引用 S2.2 落地刀 `policy_measure` 行 | 不爬网 |
| BUDGET (per S2.4 规划) | ≤4 | hand-curated JSON；引用 S2.4 落地刀 `budget_execution` 行 | 不爬网 |
| PROJECT (per S2.3 规划) | ≤3 | hand-curated JSON；引用 S2.3 落地刀 `project_event` 行 | 不爬网 |
| PERSON (per S2.1 规划) | ≤3 | hand-curated JSON；引用 S2.1 落地刀 `person` / `tenure` 行 | 不爬网 |
| **合计** | ≤20 | | **不爬网** |

### 4.2 polarity 守门（per Gate 2 §3.2 + §2.4）

| 限制 | 上限 | 理由 |
|---|---|---|
| 每 claim CONTRADICTS 行数 | ≥1 | **Gate 2 §3.2 硬要求** |
| SUPPORTS : CONTRADICTS 比例 | 建议 2:1 ~ 3:1 | 演示守门非形式化 |
| `canonical_polarity = UNRATED` 行数 | 0 | 守门 — 落地刀 100% 投影 |

### 4.3 `is_demo` 流转（per docs/33 §3.2 sentinel）

| 阶段 | lineage.is_demo | 含义 |
|---|---|---|
| 1.DRAFT | `"true"` | 草拟；未审；不公开 |
| 2.PENDING_REVIEW | `"true"` | 待审；不公开 |
| 3.APPROVED | `"false"` | 审核通过；可公开 |
| 4.PUBLISHED | `"false"` | UI 已展示 |
| 5.REJECTED | `"true"`（保留 audit） | 拒；不公开 |
| 6.ARCHIVED | `"true"`（保留 audit） | 过期；不公开 |

### 4.4 稳定 UUID（per S1.12 + S2.4 §4.4 平行）

| 表 | UUID 家族 |
|---|---|
| `claim_evidence_link`（反例登记） | `a0000000-0000-0000-0000-0000000000eX`（X = 0..9 + a..z）|
| `uncertainty_record`（审核中间态） | 复用 S2.5 §4.4 `cX` 家族 |
| `geo_entity`（外键）| 复用既有 demo geo_entity |

---

## 5. 与 S2.7 / S2.8 接驳

### 5.1 `mart_claim_evidence_polarity_balance` → RegionCard 顶部 **红色 banner**（per Gate 2 §3.2）

| mart 列 | RegionCard 字段 | 备注 |
|---|---|---|
| `n_supports` | `banner.support_count` | 计数；不评分 |
| `n_contradicts` | `banner.contradict_count` | **Gate 2 §3.2 硬要求** ≥1 |
| `balance_status` | `banner.status_badge` | "NO_CONTRADICTING_EVIDENCE" 红色 / 其他 黄/绿/橙 |
| `claim_id` | `banner.claim_link` | 跳转到反例详情页 |

### 5.2 `mart_counterexample_overview` → 反例登记总览页（落地刀新增）

```sql
-- mart_counterexample_overview (每 claim 一行 + 反例计数 + reviewer 状态)
{{ config(materialized='view', tags=['mart', 'counterexample']) }}

WITH polarity_balance AS (
    SELECT
        cel.claim_id,
        cel.claim_type,
        COUNT(*) FILTER (WHERE cel.canonical_polarity = 'CONTRADICTS') AS n_contradicts,
        COUNT(*) FILTER (WHERE cel.canonical_polarity = 'SUPPORTS')     AS n_supports,
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
    FROM {{ ref('stg_claim_evidence_link') }} cel
    GROUP BY cel.claim_id, cel.claim_type
),
review_status AS (
    SELECT
        ur.target_id AS claim_id,
        ur.uncertainty_type,
        ur.created_at,
        ROW_NUMBER() OVER (
            PARTITION BY ur.target_id
            ORDER BY ur.created_at DESC
        ) AS rn
    FROM {{ ref('stg_uncertainty_record') }} ur
    WHERE ur.target_type = 'CLAIM_EVIDENCE_LINK'
)
SELECT
    pb.claim_id,
    pb.claim_type,
    pb.n_contradicts,
    pb.n_supports,
    pb.balance_status,
    rs.uncertainty_type AS latest_review_status,
    rs.created_at AS latest_review_timestamp,
    COALESCE(cel.lineage->>'is_demo', 'true') AS is_demo
FROM polarity_balance pb
LEFT JOIN review_status rs
    ON rs.claim_id = pb.claim_id AND rs.rn = 1
LEFT JOIN {{ ref('stg_claim_evidence_link') }} cel
    ON cel.claim_id = pb.claim_id
```

**不评分**：仅计数 + 枚举状态；不派生"反例严重度""证据强度评分"（per docs/06 §6.6 红线）。

### 5.3 不接 Gate 2 §3.2 全量评审（per `229` §SCHEMA 禁）

本刀 S2.6（落地刀）**不接** Gate 2 §3.2 全量 UI 验收（属 S2.10 Gate 2 评审刀）。本刀仅：
- 暴露 `mart_claim_evidence_polarity_balance` 给前端可消费
- 暴露 `mart_counterexample_overview` 给 Gate 2 §3.2 反例登记检查

### 5.4 验证（落地刀）

```bash
# 1. mart 行数 ≥1
PGPASSWORD=postgres psql -h 127.0.0.1 -p 55440 -U postgres -d cegr_test \
    -c "SELECT COUNT(*) FROM cegr_staging.mart_claim_evidence_polarity_balance;"
# 预期: ≥1

# 2. 反例守门（per Gate 2 §3.2 + docs/40 §3.4）
PGPASSWORD=postgres psql ... \
    -c "SELECT COUNT(*) FROM cegr_staging.mart_claim_evidence_polarity_balance WHERE balance_status = 'NO_CONTRADICTING_EVIDENCE';"
# 预期: 0（per §4.2 守门）

# 3. polarity 分布
PGPASSWORD=postgres psql ... \
    -c "SELECT canonical_polarity, COUNT(*) FROM cegr_staging.stg_claim_evidence_link GROUP BY canonical_polarity;"
# 预期: SUPPORTS ≥ 1, CONTRADICTS ≥ 1（per §4.2）

# 4. 审核中间态流转（仅 PENDING_REVIEW + APPROVED 可见）
PGPASSWORD=postgres psql ... \
    -c "SELECT uncertainty_type, COUNT(*) FROM cegr_staging.stg_uncertainty_record
        WHERE target_type = 'CLAIM_EVIDENCE_LINK'
        GROUP BY uncertainty_type;"
# 预期: 至少含 COUNTEREXAMPLE_PENDING_REVIEW 或 COUNTEREXAMPLE_APPROVED

# 5. lineage is_demo 流转（DRAFT 全部 true；APPROVED 后 false）
PGPASSWORD=postgres psql ... \
    -c "SELECT
          COUNT(*) FILTER (WHERE (lineage->>'is_demo')::boolean = true)  AS n_is_demo_true,
          COUNT(*) FILTER (WHERE (lineage->>'is_demo')::boolean = false) AS n_is_demo_false
        FROM cegr_staging.stg_claim_evidence_link;"
# 预期: 演示 ≥1 true + ≥1 false

# 6. 触发器守门（删最后一条 CONTRADICTS 应抛异常）
PGPASSWORD=postgres psql ... \
    -c "DELETE FROM cegr.claim_evidence_link
        WHERE canonical_polarity = 'CONTRADICTS'
          AND claim_id = (SELECT claim_id FROM cegr.claim_evidence_link
                          WHERE canonical_polarity = 'CONTRADICTS'
                          ORDER BY created_at LIMIT 1)
          AND id = (SELECT id FROM cegr.claim_evidence_link
                    WHERE canonical_polarity = 'CONTRADICTS'
                    ORDER BY created_at LIMIT 1);"
# 预期: RAISE EXCEPTION "gate 2 §3.2 violation: claim % has zero CONTRADICTS rows after this change"
```

---

## 6. 验收清单

| # | 项 | 落地刀验证方式 |
|---|---|---|
| 1 | `claim_evidence_link` 表 + docs/40 §2.2 + migration 012 +5 列齐全 | `\d cegr.claim_evidence_link` |
| 2 | `uncertainty_record` 表既有 6 列不动 | `\d cegr.uncertainty_record` |
| 3 | 既有 `polarity` CHECK (SUPPORTS / CONTRADICTS) 保留 | `\d` 约束列表 |
| 4 | dbt run `--select stg_claim_evidence_link+ mart_claim_evidence_polarity_balance` exit 0；新增 `mart_counterexample_overview` view | dbt run log |
| 5 | mart 行数 = seed 行数（is_demo=true 过滤后）| SQL COUNT |
| 6 | 反例守门 NO_CONTRADICTING_EVIDENCE 数 = 0（per §4.2）| SQL COUNT |
| 7 | polarity 分布 SUPPORTS ≥ 1 + CONTRADICTS ≥ 1（per §4.2）| SQL GROUP BY |
| 8 | 审核中间态流转正确（PENDING_REVIEW → APPROVED/REJECTED）| SQL GROUP BY uncertainty_type |
| 9 | `canonical_polarity` 100% 投影（per §4.2）| SQL COUNT NULL = 0 |
| 10 | 触发器守门：删最后 CONTRADICTS 行抛异常 | psql DELETE 验证 |
| 11 | admin UI 反例登记表单可提交（per §3.1）| frontend browser E2E |
| 12 | reviewer UI 审核闭环可走通（per §3.3）| frontend browser E2E |
| 13 | 既有 61 schema_negative 测试仍绿（含 s21lite 5 + s22lite 5 + s23lite 8 + s24lite 8 + s25lite 8）| pytest tests/ -q |
| 14 | 新增 pytest `tests/test_counterexample_s26lite.py` ≥5 cases 全过 | pytest -v |
| 15 | pack invariant 547 → 547+N | JSON 解析守门 |
| 16 | smoke-check 仍 PASS（无 frontend 改动）| python3 frontend/smoke-check.py |
| 17 | 既有 S2.7-a2 + S2.1-lite + S2.2-lite + S2.3-lite + S2.4-lite + S2.5-lite 套件仍绿 | pytest tests/test_evidence_chain_s27a.py tests/test_person_tenure_s21lite.py tests/test_policy_commitment_s22lite.py tests/test_project_event_s23lite.py tests/test_budget_s24lite.py tests/test_inference_s25lite.py |

---

## 7. 关键风险与回滚

| 风险 | 触发条件 | 回滚策略 |
|---|---|---|
| 反例守门触发器被绕过（admin 直接 SQL DELETE）| DB 写权限 | 触发器部署到 `BEFORE DELETE` 而非 `AFTER`；记录 audit log |
| `uncertainty_record.uncertainty_type` 任意字符串 | 应用层未 enum-style 守门 | 应用层 enum-style 文案；不引入 schema ENUM（per docs/40 §2.3 平行）|
| reviewer 闭环卡死（PENDING_REVIEW 长期未审）| reviewer 缺位 | 加 timeout（如 30 天未审 → auto-reject）；非本刀范围 |
| `lineage.is_demo` 流转被绕过（admin 直接 UPDATE）| DB 写权限 | 触发器部署到 `BEFORE UPDATE`；记录 audit log |
| 反例登记被滥用（malicious reviewer 一键 APPROVED 假反例）| 评审信任 | uncertainty_record.description 必填 ≥10 字；audit trail |
| `mart_counterexample_overview` 性能差（大数据量）| claim 数 > 10K | 落地刀 materialized view + 增量更新；非本刀 |
| `canonical_polarity` 与 `polarity` 不一致（trigger 漏触发）| 触发器未部署 | pytest case 显式断言；部署检查 |

---

## 8. 不做什么（本刀 S2.6 边界；推后续刀）

| ❌ | 推到 |
|---|---|
| ❌ 写生产 migration（**仅规划**）| S2.6 落地刀（tasking 230+）|
| ❌ dbt `mart_claim_evidence_polarity_balance` + `mart_counterexample_overview` | S2.6 落地刀 |
| ❌ 首批 ≤20 反例登记 seed | S2.6 落地刀（**严禁爬网**）|
| ❌ admin UI 反例登记表单 + reviewer 审核界面 | S2.6 落地刀 |
| ❌ 触发器 `assert_min_one_contradicts()` 部署 | S2.6 落地刀 |
| ❌ Gate 2 §3.2 全量 UI 验收 | S2.10 |
| ❌ S2.8 七维度观察卡全量接驳（**仅 §5.1 红色 banner 接驳**）| S2.8 |
| ❌ `evidence_audit_trail` 表新增 | 后续刀视 Cursor 裁定 |
| ❌ 反例评分（"严重度""可信度""反驳力"）| **红线**（per docs/06 §6.6）|
| ❌ `score` / `rating` / `rank` / `total_score` / `confidence_score` / `credibility_score` 任一字段 | **红线** |
| ❌ 修改 `gate_thresholds.json` | spike-04 评测构件，只读 |
| ❌ 批量爬政策研究 / 财政预决算 / 官员履历 | 红线 |
| ❌ 启用 pgvector / RLS / partition | Stage 2 边界（per docs/04 §6）|
| ❌ 修改 `00-CC-CURRENT.md` | Cursor 拥有 |
| ❌ 跨行 CHECK 约束（PostgreSQL 不支持）| 用触发器 + 应用层守门 |

---

## 9. 与现有文档的关系

| 引用 | 用途 |
|---|---|
| `docs/04-data-model.md` §3.4 | observation_revision append-only 平行 |
| `docs/04-data-model.md` §3.9 | `claim_evidence_link.polarity` SUPPORTS / CONTRADICTS 双显（防确认偏差）|
| `docs/04-data-model.md` §6 | Stage 0 边界（不扩 pgvector / RLS / partition）|
| `docs/06-governance-observation-method.md` §6 | 综合指数纪律（**红线**：不评分；不排名）|
| `docs/06-governance-observation-method.md` §6.6 第 1 行 | "任何指数都必须能一键回放" — `claim_evidence_link.note` 字段承担 |
| `docs/34-stage2-s20-kickoff-plan-20260825.md` §2 Gate 2 | 至少 1 个反例被显式登记并展示（**S2.6/§2.4 + §3.2 + §5.1 接驳**）|
| `docs/34-stage2-s20-kickoff-plan-20260825.md` §4 序 10 | S2.6 范围 + 反例排位 |
| `docs/40-stage2-s25-inference-plan-20260826.md` §2.5 | 反例守门三态（SUPPORTS_DOMINANT 等）|
| `docs/40-stage2-s25-inference-plan-20260826.md` §3.4 | `mart_claim_evidence_polarity_balance` 规划（已交）|
| `docs/40-stage2-s25-inference-plan-20260826.md` §10.6 | 反例守门强度（应用层 + mart；不用跨行 CHECK）|
| `schema/01-core.sql` §932-940 | 既有 `uncertainty_record` 表（不加列）|
| `schema/01-core.sql` §956-969 | 既有 `claim_evidence_link` 表（已由 migration 012 扩列）|
| `schema/migrations/012_inference_alignment.sql` | `claim_evidence_link` +5 列（inference 刀已交）|

---

## 10. CC 建议（供 Cursor 审阅 / 用户裁定）

### 10.1 workflow 形态

| 选项 | 描述 | 选 |
|---|---|---|
| A | 5 阶段（DRAFT → PENDING_REVIEW → APPROVED → PUBLISHED + REJECTED/WITHDRAWN/ARCHIVED 终态）| **推荐**（per §2.1）|
| B | 3 阶段简化（DRAFT → APPROVED → PUBLISHED）| 失去 reviewer 闭环；Gate 2 §3.2 弱化 |

### 10.2 reviewer 角色权限

| 选项 | 描述 | 选 |
|---|---|---|
| A | admin role 可独立 APPROVE/REJECT | **推荐**（per §2.1 + 现有 admin_upload 模式）|
| B | 引入 reviewer 角色独立于 admin | 加固；权限模型复杂 |

### 10.3 反例登记最少 CONTRADICTS 数

| 选项 | 描述 | 选 |
|---|---|---|
| A | 每 claim 至少 1 条 CONTRADICTS（per Gate 2 §3.2 硬要求）| **推荐** |
| B | 至少 2 条（更严守门）| 加固；但首批 ≤N 数据难凑 |

### 10.4 `lineage.is_demo` 流转

| 选项 | 描述 | 选 |
|---|---|---|
| A | DRAFT/PENDING/REJECTED/WITHDRAWN → true；APPROVED/PUBLISHED → false | **推荐**（per §4.3）|
| B | APPROVED 后保留 true，PUBLISHED 才 flip | 加固；两阶段审计 |

### 10.5 触发器部署时机

| 选项 | 描述 | 选 |
|---|---|---|
| A | 落地刀部署 `assert_min_one_contradicts()` AFTER INSERT OR UPDATE OR DELETE | **推荐** |
| B | 仅应用层守门（不在 DB 触发器）| 灵活；但 DB 写权限被绕过时失效 |

### 10.6 `uncertainty_record.uncertainty_type` 新增值

| 选项 | 描述 | 选 |
|---|---|---|
| A | 应用层 enum-style 守门（per §2.3）| **推荐**（per docs/40 §2.3 平行；不引入 schema ENUM）|
| B | schema-level CHECK + ENUM type | 加固；migration 复杂度↑ |

### 10.7 reviewer 自动 timeout

| 选项 | 描述 | 选 |
|---|---|---|
| A | 30 天未审 auto-reject（per §7）| **推荐**（非本刀；属 S2.10 Gate 2 评审期）|
| B | 无 timeout；人工 catch | 灵活；但 reviewer 缺位时堆积 |

### 10.8 反例评分（红线）

| 选项 | 描述 | 选 |
|---|---|---|
| A | 不引入评分字段（per docs/06 §6.6）| **推荐** |
| B | 引入"反例严重度"等数值 | ❌ 红线 |

---

— End of `docs/41` —

> 等待 Cursor 审验（预期 `231-stage0-cursor-s26-plan-audit-…md`）。
> 通过后下发落地任务（`232-stage2-s26-counterexample-impl-tasking-…md`），进入 S2.6 实施。
> S2.6 落地可与 S2.1-full 与 S2.2-dbt/seed 与 S2.3/4/5 落地可**并行**（不同 schema 域）；等 Cursor 裁定。