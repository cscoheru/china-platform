# 47 — Stage 2 / S2.7-b-full / 10 地市 mart / person 真数据接入 规划

> 起草：CC · 2026-08-26 · queue_rev 105
> 前置：`261` docs/45 刷新 PASS；`260` S2.7-b-lite `257`；`docs/46`；`docs/44` §5.1.2/§5.1.3；`docs/34` §3
> 用户裁定：Stage 2 **C**；缩刀 **D**（本刀**只规划**）；自主推进
> 任务书：`262-stage2-s27b-full-mart-plan-tasking-20260826`
>
> ⚠ **本刀不宣布 Gate 2 PASS**（per `docs/34 §1` + §8 #8 + §133 + `262` §红线）
> ⚠ **本刀不接真 mart / 不伪造 SHA**（per `262` §SCHEMA "本刀只规划"）
> ⚠ **10 城名单已锁定**（per `256` §SCHEMA + docs/46 §2）

---

## 1. 目标

S2.7-b-full 是 S2.7-b-lite 的**接驳刀** — 把 10 地市 mock 替换为 `mart_city_evidence_chain` + person/tenure 真数据接入，同时保留 lite 已交付的 UI 三件套（EvidenceChain + SevenDimGrid + PeerCompareCard）。本刀是**规划刀**（per `262` §SCHEMA "本刀只规划"），落地刀（tasking 26X+）须依赖：

- **O1** 真实 SHA-locked 江苏样本（per docs/34 §3）
- **Stage 1 OPEN 收口**（per docs/34 §3）
- 现行 dbt mart 体系扩展（per docs/44 §7.3）

### 1.1 与前置刀的关系

| S2.7-b-full 关注 | S2.7-b-lite 已交 | docs/46 规划 |
|---|---|---|
| 10 城 EvidenceChain 接 mart | 10 城 6 段 mock | §6.2 S2.7-b-full 范围 |
| person/tenure 真数据接入契约 | 仅 mock 占位（person/tenure 缺失）| §5.2 OPEN |
| 七维度 cell 接 `mart_city_seven_dim_overview` | 7 cell mock | §6.2 + docs/42 §3 |
| 段级 evidence gaps 显示 | "未覆盖" mock 演示 | docs/44 §1.1 |
| 不可降级验收项 #2 持续守门 | ✅ 六段 UI 渲染 | docs/45 §2 #2 |

### 1.2 S2.7-b-full 红线（per docs/46 §1.2 + `262` §红线 + docs/34 §1/§8/§133）

- ❌ 不宣布 Gate 1 / Gate 2 PASS
- ❌ 不做官员能力总分（PRD 红线 + docs/08 §3.3 红线 1）
- ❌ 不做隐性指数（docs/08 §3.3 红线）
- ❌ 不启用 DSH（docs/08 §3.3 红线）
- ❌ 不做实时数据（docs/08 §3.3 红线；月度/年度更新）
- ❌ 不伪造 SHA / 不伪造证据（`262` §红线）
- ❌ 不批量爬政策研究 / 财政预决算 / 官员履历（standing 红线）
- ❌ 不擅自改 Cursor 锁定的 10 城名单（per `256` §SCHEMA）
- ❌ 不擅自提前 Gate 2 评审日期（per docs/34 §10.4）

---

## 2. S2.7-b-full 范围（per docs/46 §6.2 + `262` §SCHEMA）

### 2.1 落地范围（OPEN — tasking 26X+ 预期）

| 元素 | 来源 / mart | 落地状态 |
|---|---|---|
| dbt mart `mart_city_evidence_chain` | 新建（per docs/46 §6.2）| OPEN — S2.7-b-full 落地刀 |
| dbt mart `mart_city_seven_dim_overview` | 新建（per docs/44 §7.3 + docs/42 §2.2 投影）| OPEN — S2.7-b-full 落地刀 |
| person/tenure 真数据接入契约 | `mart_person_tenure` JOIN `comparison_group` 横向 | OPEN — 依赖 O1 真实 SHA |
| 10 地市 mock → 真数据迁移 | MOCK_CITIES → mart_city_* | OPEN — 依赖 Stage 1 OPEN 收口 |
| 演示数据策略 | per docs/34 §11.2 "A 仅 mock"；full 切换需 O1 收口 | OPEN — user_ruling |
| 七维度 cell 5 枚举守门 | `balance_status` ∈ {NO_EVIDENCE, NO_CONTRADICTING_EVIDENCE, NO_SUPPORTING_EVIDENCE, SUPPORTS_DOMINANT, CONTRADICTS_DOMINANT} | OPEN — 接 docs/42 §2.5 mart 投影 |
| 段级 evidence gaps 显示 | per docs/44 §1.1 S2.7-a 段级证据链接驳 | OPEN — 接 mart + UI |
| 不可降级验收项 #2 | ✅ 六段 UI + 反例 trigger（per docs/45 §2 #2）| ✅ lite 已交；full 持续守门 |

### 2.2 不在范围（per docs/46 §9 + `262` §SCHEMA）

- ❌ 宣布 Gate 2 PASS（红线条目）
- ❌ 10 城 mock → 真数据 全量迁移（O1 + Stage 1 OPEN 收口后做）
- ❌ 改 docs/06 / docs/08 / docs/10 / docs/34 / docs/40 / docs/41 / docs/42 / docs/43 / docs/44 / docs/45 / docs/46 内容（Cursor 拥有）
- ❌ 改 `gate_thresholds.json`（spike-04 评测构件，只读）
- ❌ 启用 pgvector / RLS / partition（Stage 2 边界；per docs/04 §6）

---

## 3. mart 映射（per docs/46 §6.2 + docs/44 §7.3）

### 3.1 `mart_city_evidence_chain`（新建 — S2.7-b-full 落地刀）

| 字段 | 类型 | 来源 | 守门 |
|---|---|---|---|
| `city_id` | UUID | `geo_entity.geo_entity_id`（10 城；focal 锁定 4 江苏 + 3 浙江 + 3 广东）| JOIN `geo_entity` |
| `geo_name_zh` | TEXT | `geo_entity.geo_name_zh` | JOIN |
| `province_slug` | TEXT | `geo_entity.lineage->>'province_slug'` | 应用层守门 |
| `segment` | TEXT | `evidence_segment.segment`（6 段：CONDITION/COMMITMENT/INPUT/PROCESS/OUTPUT/OUTCOME/FEEDBACK）| 应用层 enum 守门（per docs/40 §2.3）|
| `canonical_statement` | TEXT | `inference_record.canonical_statement`（per migration 012）| NOT NULL |
| `canonical_polarity` | TEXT | `inference_record.canonical_polarity`（SUPPORTS/CONTRADICTS）| 应用层 enum 守门 |
| `evidence_strength` | TEXT | `inference_record.evidence_strength`（STRONG/MODERATE/WEAK）| 应用层 enum 守门 |
| `info_layer` | TEXT | `inference_record.canonical_layer`（FACT/DERIVED/INFERENCE/JUDGMENT）| 应用层 enum 守门（per 01-core.sql §25-30）|
| `lineage.is_demo` | TEXT | `inference_record.lineage->>'is_demo'` | demo sentinel（per docs/33 §3.2）|
| `lineage.source_file_sha256` | TEXT | `inference_record.lineage->>'source_file_sha256'` | ⚠️ **OPEN**（O1 真实 SHA 收口前均为占位）|

**物化策略**：先 `view`（与 `mart_person_tenure` 平行），Stage 3 收口增量。

### 3.2 `mart_city_seven_dim_overview`（新建 — S2.7-b-full 落地刀）

| 字段 | 类型 | 来源 | 守门 |
|---|---|---|---|
| `city_id` | UUID | `geo_entity.geo_entity_id` | JOIN |
| `card_id` | TEXT | `inference_record.card_id`（7 维度：POLICY_DELIVERY/FISCAL_EXECUTION/PROJECT_DELIVERY/ECONOMIC_ADAPTATION/PUBLIC_SERVICES/RISK_MANAGEMENT/GOAL_CONSISTENCY）| 应用层 enum 守门（per docs/42 §2.4 + §2.5）|
| `n_supports` | INTEGER | 聚合 `claim_evidence_link` WHERE polarity='SUPPORTS' | 仅计数 |
| `n_contradicts` | INTEGER | 聚合 `claim_evidence_link` WHERE polarity='CONTRADICTS' | 仅计数 |
| `n_inference` | INTEGER | 聚合 `inference_record` WHERE canonical_layer='INFERENCE' | 仅计数 |
| `n_judgment` | INTEGER | 聚合 `inference_record` WHERE canonical_layer='JUDGMENT' | 仅计数 |
| `n_derived` | INTEGER | 聚合 `inference_record` WHERE canonical_layer='DERIVED' | 仅计数 |
| `balance_status` | TEXT | 派生 5 枚举（NO_EVIDENCE / NO_CONTRADICTING_EVIDENCE / NO_SUPPORTING_EVIDENCE / SUPPORTS_DOMINANT / CONTRADICTS_DOMINANT）| 应用层 enum 守门（per docs/42 §2.4）|
| `is_demo` | TEXT | `inference_record.lineage->>'is_demo'` | demo sentinel |

**红线守门**：
- ❌ 不派生 `score` / `rating` / `total_score` / `confidence_score` / `credibility_score`（per docs/42 §8 + docs/06 §6.6）
- ❌ 不做"地区得分" / 不做"地区排名" / 不做"peer_rank"
- 仅展示 `balance_status` 计数；不评分；不排名

### 3.3 person/tenure 接入契约（per docs/46 §5.2 OPEN + S2.1-lite `mart_person_tenure`）

| mart_person_tenure 字段 | 接入方式 | 守门 |
|---|---|---|
| `person_id` | JOIN `tenure.person_id` | 应用层守门 |
| `canonical_name` | JOIN `person.canonical_name` | — |
| `position_title` | JOIN `position.title` | — |
| `geo_canonical_name` | JOIN `geo_entity.canonical_name`（与 city JOIN）| — |
| `is_current` | JOIN `tenure.is_current` | 应用层 enum 守门 |
| `is_demo` | `tenure.lineage->>'is_demo'` | demo sentinel |

**OPEN**：
- 段级 evidence 与 person/tenure 关联（COMMITMENT/INPUT/PROCESS 段）— 落地刀填
- 履历卡 UI（per S2.7-a 已预留，无数据接入）— 落地刀填

---

## 4. 段级字段契约（per docs/46 §5.1 + docs/40 §2 + docs/41 §3）

### 4.1 city 段级 evidence 字段契约（落地刀填 OPEN）

```ts
interface CitySegmentEvidenceProps {
  cityId: string;             // JOIN mart_city_evidence_chain.city_id
  segment: 'CONDITION' | 'COMMITMENT' | 'INPUT' | 'PROCESS' | 'OUTPUT' | 'OUTCOME' | 'FEEDBACK';
  canonicalStatement: string; // JOIN mart_city_evidence_chain.canonical_statement
  canonicalPolarity: 'SUPPORTS' | 'CONTRADICTS' | 'NEUTRAL';
  evidenceStrength: 'STRONG' | 'MODERATE' | 'WEAK';
  infoLayer: 'FACT' | 'DERIVED' | 'INFERENCE' | 'JUDGMENT';
  lineage: {
    isDemo: boolean;          // mart.lineage.is_demo
    sourceFileSha256: string; // ⚠️ OPEN — 占位为 '0'*64 直到 O1 真实 SHA 收口
  };
}
```

**应用层 enum-style 守门**（不引入 schema ENUM；per docs/40 §2.3 平行）：
- `InformationLayer` ∈ {FACT, DERIVED, INFERENCE, JUDGMENT}（per 01-core.sql §25-30）
- `Polarity` ∈ {SUPPORTS, CONTRADICTS, NEUTRAL}
- `EvidenceStrength` ∈ {STRONG, MODERATE, WEAK}

### 4.2 city 七维度 cell 字段契约（落地刀填 OPEN）

```ts
interface CitySevenDimCellProps {
  cityId: string;             // JOIN mart_city_seven_dim_overview.city_id
  cardId: SevenDimCardId;     // 7 维度（per docs/42 §2.4 + §2.5）
  nSupports: number;          // JOIN mart_city_seven_dim_overview.n_supports
  nContradicts: number;       // JOIN mart_city_seven_dim_overview.n_contradicts
  nInference: number;
  nJudgment: number;
  nDerived: number;
  balanceStatus: BalanceStatus; // 5 枚举
  isDemo: boolean;
}
```

### 4.3 city peer-compare 横向契约（同省地市）

```ts
interface CityPeerCompareProps {
  groupId: string;            // mart_peer_region_compare JOIN（per docs/43 §2.4）
  focalCityId: string;        // 本城（focal）
  peerCityIds: string[];      // 同省其他地市（peer；lite mock 已是同省横向）
  selectionJustification: string; // per docs/10 §133 + docs/43 §2.2 NOT NULL CHECK
}
```

---

## 5. 验收清单（per docs/46 §7.2 + docs/08 §3.2 + docs/44 §5.1.2）

### 5.1 S2.7-b-full 验收（次落刀 — OPEN）

| # | 项 | 来源 |
|---|---|---|
| 1 | dbt mart `mart_city_evidence_chain` 落地 | docs/46 §6.2 + 本刀 §3.1 |
| 2 | dbt mart `mart_city_seven_dim_overview` 落地 | docs/44 §7.3 + 本刀 §3.2 |
| 3 | person/tenure 接入契约 + mart JOIN 通过 | docs/46 §5.2 + 本刀 §3.3 |
| 4 | 10 地市 mock → 真数据迁移（O1 真实 SHA + Stage 1 OPEN 收口后做）| docs/46 §6.2 + docs/34 §3 |
| 5 | 七维度 card 5 枚举守门（`balance_status` ∈ 5 态）| docs/42 §2.5 |
| 6 | 段级 evidence gaps 显示（per docs/44 §1.1 S2.7-a 段级证据链接驳）| docs/44 §1.1 |
| 7 | 不可降级验收项 #2 持续守门（六段 UI + 反例 trigger）| docs/45 §2 #2 |
| 8 | 红线守门（不评分 / 不排名 / 不派生 `score`）| docs/06 §6.6 + docs/42 §8 |
| 9 | 跨 lite 回归 + full 回归 PASS | docs/45 §4 |
| 10 | smoke-check PASS（含 S2.7-b-full mart 守门）| AGENTS.md |
| 11 | 10 城名单锁定（不擅自换/加）| `256` §SCHEMA + docs/46 §2 |
| 12 | 应用层 enum 守门（不引入 schema ENUM）| docs/40 §2.3 |

### 5.2 S2.7-b-full 不在验收范围（OPEN — 推后续刀）

- ❌ Gate 2 PASS 宣布（红线条目；评审日 W8 由 Cursor/用户裁定）
- ❌ 跨省地市对比（per docs/46 §11.5 B 选项 — 越界 docs/34 §4.3）
- ❌ 官员能力总分 / 排名 / DSH / 实时数据（PRD 红线）
- ❌ 批量爬政策研究 / 财政预决算 / 官员履历

---

## 6. lite → full 切刀边界（per docs/46 §6 + `262` §SCHEMA）

### 6.1 已交（lite — tasking 256 + 回执 257）

| 元素 | 状态 |
|---|---|
| `/cities/[slug]` 路由 + `generateStaticParams` | ✅ S2.7-b-lite 已交 |
| 10 城 mock 数据 | ✅ S2.7-b-lite 已交 |
| 复用 EvidenceChain + SevenDimGrid + PeerCompareCard | ✅ S2.7-b-lite 已交 |
| `test_city_slug_map_s27b.py` 6 PASS | ✅ S2.7-b-lite 已交 |
| smoke-check 9 节守门 | ✅ S2.7-b-lite 已交 |

### 6.2 OPEN（full — tasking 26X+ 预期）

| 元素 | 依赖 | 触发条件 |
|---|---|---|
| `mart_city_evidence_chain` | O1 真实 SHA 收口 | docs/34 §3 + Stage 1 OPEN 收口 |
| `mart_city_seven_dim_overview` | O1 + 上游 mart | 同上 |
| person/tenure 真数据接入 | S2.1-lite `mart_person_tenure` 已交 + docs/46 §5.2 契约 | S2.1-lite PASS（OPEN）|
| 10 城 mock → 真数据迁移 | 上述 mart 落地 + 演示策略 user_ruling | docs/34 §11.2 切换 |
| 段级 evidence gaps 显示 | mart + UI 联动 | 同上 |

### 6.3 切刀风险（per `262` §红线）

- **O1 真实 SHA 未收口** → 不得落地 full（否则伪造证据）
- **Stage 1 OPEN 未收口** → 不得落地 full（per docs/34 §3）
- **S2.1-lite 未交** → person/tenure 接入契约不成立
- **Gate 2 评审日期提前** → 不得擅自提前（per docs/34 §10.4）
- **本刀不擅自换/加 10 城** → 落地刀不得擅自改 Cursor 锁定清单

---

## 7. 红线自检（per `262` §红线 + docs/34 §1/§8/§133）

| 红线 | 状态 |
|---|---|
| ❌ 宣布 Gate 1 / Gate 2 PASS | ✅ §1.2 + §6 + §7 + §9 多次显式守门 |
| ❌ 改 Cursor 锁定 10 城名单 | ✅ §2 + §6 锁定清单；落地刀不得擅自换/加 |
| ❌ 伪造 SHA / 伪造证据 | ✅ §6.3 切刀风险显式守门；O1 收口前不得落地 full |
| ❌ 官员能力总分 / 排名 / DSH / 实时数据 | ✅ §3.2 + §5.2 守门 |
| ❌ 批量爬政策研究 / 财政预决算 / 官员履历 | ✅ |
| ❌ HTTP 爬源站 | ✅ |
| ❌ 降 OCR 门槛 | ✅ 无关 |
| ❌ 改 `gate_thresholds.json` | ✅ |
| ❌ 改 `00-CC-CURRENT.md` | ✅ Cursor 拥有 |
| ❌ --force / --force-with-lease | ✅ |
| ❌ 索要 PAT | ✅ |
| ✅ pack invariant 守门 | ⏳ bump + commit 后 587 == 587 == 587 |
| ✅ receipts 仅写 `reviews/stage0-gate0-rework-2026-08-23/` | ✅ |
| ✅ 不写 dbt mart | ✅（per `262` §SCHEMA "本刀只规划"）|
| ✅ 不写 migration | ✅（per `262` §SCHEMA）|
| ✅ 不擅自提前 Gate 2 评审日期 | ✅ W8（per docs/34 §10.4）|
| ✅ 不接全国实时排名 | ✅（per docs/34 §4.3 + docs/05 §8.3）|
| ✅ 不引入 score / rating / rank 字段 | ✅ §3.2 红线 |
| ✅ 不引入 schema ENUM | ✅ 应用层 enum-style 守门（per docs/40 §2.3）|
| ✅ Static-segment 守门（dynamic segment route）| ✅ docs/46 §3.2 平行 |
| ✅ O1 + O3 OPEN 清单显式携带 | ✅ §6.3 切刀风险 + §3.1 lineage.source_file_sha256 ⚠️ OPEN |

---

## 8. 不做什么（per docs/46 §9 + `262` §SCHEMA）

| ❌ | 推到 |
|---|---|
| ❌ 宣布 Gate 2 PASS | Gate 2 评审日（暂定 W8，per docs/34 §10.4）|
| ❌ 伪造 SHA / 伪造证据 | 红线（per docs/34 §1）|
| ❌ 改 10 城名单 | 红线（per `256` §SCHEMA）|
| ❌ 10 地市 mart 落地 | S2.7-b-full 落地刀（tasking 26X+；OPEN）|
| ❌ person/tenure 真数据接入 | S2.7-b-full + O1 真实 SHA 收口后 |
| ❌ 改 docs/06 / docs/08 / docs/10 / docs/34 / docs/40 / docs/41 / docs/42 / docs/43 / docs/44 / docs/45 / docs/46 内容 | Cursor 拥有 |
| ❌ 改 `gate_thresholds.json` | spike-04 评测构件，只读 |
| ❌ 启用 pgvector / RLS / partition | Stage 2 边界（per docs/04 §6）|

---

## 9. 与现有文档的关系

| 引用 | 用途 |
|---|---|
| `docs/34-stage2-s20-kickoff-plan-20260825.md` §1/§3/§8/§133/§10.4 | 红线 + Stage 1 OPEN + 评审日期 |
| `docs/34-stage2-s20-kickoff-plan-20260825.md` §11.2 | 演示数据策略（仅 mock）|
| `docs/40-stage2-s25-inference-plan-20260826.md` §2.3 | 应用层 enum-style 守门（不引入 schema ENUM）|
| `docs/41-stage2-s26-counterexample-plan-20260826.md` §3 | 段级 evidence |
| `docs/42-stage2-s28-seven-dim-plan-20260826.md` §2.4/§2.5 | 七维度 cell 5 枚举 + INFERENCE/JUDGMENT 角标 |
| `docs/43-stage2-s29-peer-compare-plan-20260826.md` §4.1 | 江苏 focal 候选 + 同省地市横向 |
| `docs/44-stage2-s210-gate2-package-plan-20260826.md` §5.1.2/§5.1.3/§7.3 | 10 地市 OPEN + 候选清单 + mart 接入 |
| `docs/45-stage2-s210-lite-gate2-review-index-20260826.md` §2 #1 + §5.5 + §6.1 | 10 地市 lite 落地状态 + 回执 257 登记 |
| `docs/46-stage2-s27b-cities-evidence-plan-20260826.md` §2/§3.1/§3.2/§5.2/§6/§7.2 | 10 城锁定 + 路由 + 段级契约 + 切刀 + 验收 |
| `schema/migrations/012_inference_alignment.sql` | inference_record + claim_evidence_link +8/+5 列 |
| `schema/migrations/013_counterexample_gate.sql` | 反例 trigger |
| `dbt/models/marts/mart_source_disagreement.sql` | 现行 mart 模板（per docs/44 §7.3）|
| `frontend/lib/mock_cities.ts` | 10 城 mock（lite 已交；full 替换源）|
| `frontend/app/cities/[slug]/page.tsx` | dynamic segment route（lite 已交；full 复用）|
| `frontend/app/components/{EvidenceChain,SevenDimGrid,PeerCompareCard,CityPage}.tsx` | UI 三件套（lite 已交；full 复用）|
| `tests/test_city_slug_map_s27b.py` | 6 PASS（lite 已交；full 守门）|

---

## 10. CC 建议（供 Cursor 审阅 / 用户裁定）

### 10.1 切刀节奏

| 选项 | 描述 | 选 |
|---|---|---|
| A | S2.7-b-full 单刀（接 mart + person/tenure + 10 城迁移）| ⚠️ 强依赖 O1 + Stage 1 OPEN 收口 |
| B | S2.7-b-full 拆 2 刀（先 mart 落地，再真数据迁移）| ✅ **推荐**（降依赖） |
| C | 推迟至 O1 收口后做 | ✅ 最安全；评审等待期可并行做其他刀 |

### 10.2 mart 物化策略

| 选项 | 描述 | 选 |
|---|---|---|
| A | view（与 mart_person_tenure 平行）| ✅ **推荐**（per docs/44 §7.3 现行模式）|
| B | 增量物化 | Stage 3 收口后再升 |

### 10.3 不可降级验收项（与 lite 平行）

| 项 | 状态 |
|---|---|
| 六段证据链 UI（验收项 #2）| ✅ 不可降级（lite 已守；full 持续守门）|
| 七维度观察卡 5 枚举守门（验收项 #3）| ✅ 演示级可过；full 接 mart 投影 |
| person/tenure 履历卡 UI | ⚠️ S2.7-a 已预留；full 落地刀填 |

### 10.4 OPEN 清单显式携带（与 docs/45 §3 平行）

| OPEN | 来源 | full 触发条件 |
|---|---|---|
| **O1** 真实 SHA-locked 江苏样本 | docs/34 §3 | ✅ 必带 |
| O2 cron / 通知 / 真实联外探针 | docs/34 §3 | ⚠️ 演示级可过 |
| **O3** OCR 生产路径 | docs/34 §3 | ⚠️ NBS 数字演示可过 |
| **O8** person/tenure 真数据 | docs/46 §5.2 OPEN | ✅ 必带（full 落地）|
| **O9** mart_city_evidence_chain | docs/46 §6.2 OPEN + 本刀 §3.1 | ✅ 必带（full 落地）|
| **O10** mart_city_seven_dim_overview | docs/46 §6.2 OPEN + 本刀 §3.2 | ✅ 必带（full 落地）|

---

— End of `docs/47` —

> 等待 Cursor 审验（预期 `264-stage0-cursor-s27b-full-audit-…md`）。
> 通过后下发 S2.7-b-full 落地任务（`265-stage2-s27b-full-impl-tasking-…md`），进入 mart 落地刀。
> ⚠ **本刀不宣布 Gate 2 PASS**（per docs/34 §1 + §8 #8 + `262` §红线）。
> ⚠ **本刀不接真 mart / 不伪造 SHA**（per `262` §SCHEMA "本刀只规划"）。
> ⚠ **10 城名单已锁定**（per `256` §SCHEMA + docs/46 §2）。
> Gate 2 评审日期暂定 W8（per docs/34 §10.4）。