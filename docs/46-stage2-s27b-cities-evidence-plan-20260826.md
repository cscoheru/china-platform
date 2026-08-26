# 46 — Stage 2 / S2.7-b / 10 地市观察页 + 证据链接入 规划

> 起草：CC · 2026-08-26 · queue_rev 99
> 前置：`252` S2.10-lite PASS；`docs/45` §2 #1 OPEN；`docs/44` §5.1.2-§5.1.3；`docs/34` §4 序 5
> 用户裁定：Stage 2 **C**；缩刀节奏 **D**（本刀**只规划**）；**自主推进**（仅功能测试 / §BLOCKED 再找用户）
> 任务书：`253-stage2-s27b-cities-plan-tasking-20260826`
>
> ⚠ **本刀不宣布 Gate 2 PASS**（per `docs/34 §1` + §8 #8 + §133 + `253` §红线）
> ⚠ **10 城名单已锁定**（Cursor 裁定；不得擅自更改）

---

## 1. 目标

S2.7-b 是 Stage 2 **5 省 + 10 地市** 全量页面的**规划刀** — 落地刀（S2.7-b-lite / S2.7-b-full tasking 待 Cursor 下发）将：

- 落实 Gate 2 验收项 #1 **5 省 + 10 地市** 全 15 页面（per docs/08 §3.2 #1）
- 落实 docs/45 §2 #1 OPEN（10 地市待 tasking 253+）
- 落实 docs/44 §5.1.2（10 地市 OPEN）+ §5.1.3（候选清单）
- 复用 S2.7-a 5 省 lite 模板（per docs/44 §5.1.1）+ EvidenceChain UI（per docs/44 §5.2）
- person/tenure 真数据接入契约（OPEN；本规划刀不强制接满 mart）
- 切刀边界：S2.7-b-lite（mock 壳）vs S2.7-b-full（接 mart 真数据）

**本刀只规划**（per `253` §SCHEMA + 用户 D）；不写 migration / 不全量 UI / 不接真 mart。

### 1.1 S2.7-b 与前置刀的关系

| S2.7-b 关注 | S2.7-a 关注 | S2.10-lite 关注 |
|---|---|---|
| 10 地市观察页 | 5 省观察页（mock 已交）| Gate 2 评审索引 |
| `/cities/{slug}` 路由 + slug 约定 | `/provinces/{slug}` 路由 | 七条验收 ↔ 证据路径 |
| EvidenceChain 复用 + city 段级适配 | EvidenceChain 段级渲染 | 演示场景验证清单 |
| person/tenure mart 接入契约（OPEN）| 5 省 mock 数据 | O1 真实 SHA OPEN |
| 切刀：lite mock vs full mart | 仅 mock | 仅 mock |

### 1.2 S2.7-b 红线（per docs/08 §3.2 + docs/34 §1 + §8 + `253` §红线）

- ❌ 不宣布 Gate 2 PASS
- ❌ 不做官员能力总分（PRD 红线 + docs/08 §3.3 红线 1）
- ❌ 不做隐性指数（docs/08 §3.3 红线）
- ❌ 不启用 DSH（docs/08 §3.3 红线）
- ❌ 不做实时数据（docs/08 §3.3 红线；月度/年度更新）
- ❌ 不伪造 SHA / 不伪造证据（`253` §红线）
- ❌ 不批量爬政策研究 / 财政预决算 / 官员履历（standing 红线）
- ❌ 不擅自改 Cursor 锁定的 10 城名单（per `253` §SCHEMA "10 地市锁定"）
- ❌ 不擅自提前 Gate 2 评审日期（per docs/34 §10.4）

---

## 2. 10 地市锁定清单（Cursor 裁定；不得擅改）

> 来源：`253` §SCHEMA "10 地市锁定（Cursor 裁定，勿另挑）"
> per docs/05 §8.1（4 维度匹配依据）+ docs/43 §4.1（江苏 focal 候选）

| focal 省 | 地市 | slug | 候选理由（per docs/05 §8.1 + docs/43 §4.1）|
|---|---|---|---|
| **江苏** | 南京 | `nanjing` | 省会；副省级；都市圈核心 |
| **江苏** | 苏州 | `suzhou` | 经济强市（全国 GDP 前 10）；苏南模式 |
| **江苏** | 无锡 | `wuxi` | 经济强市（人均 GDP 高）；苏南模式 |
| **江苏** | 南通 | `nantong` | 沿海；上海都市圈；江苏新增长极 |
| **浙江** | 杭州 | `hangzhou` | 省会；数字经济（互联网+）；都市圈核心 |
| **浙江** | 宁波 | `ningbo` | 计划单列市；港口经济；制造业 |
| **浙江** | 温州 | `wenzhou` | 民营经济典型；商贸 |
| **广东** | 广州 | `guangzhou` | 省会；一线；商贸+先进制造 |
| **广东** | 深圳 | `shenzhen` | 计划单列市；一线；科技创新 |
| **广东** | 东莞 | `dongguan` | 制造业（电子信息集群）；深圳都市圈 |

**总计**：10 地市 = 江苏 4 + 浙江 3 + 广东 3（per docs/44 §5.1.3 候选地市映射；**缩减版** — 候选每省 4 个，Cursor 锁版减少到 10）

**守门**：落地刀不得擅自换/加城市；如需调整须经 Cursor 重发 tasking + 改 `253` §SCHEMA "10 地市锁定" 表。

---

## 3. Slug 约定 + 路由

### 3.1 Slug 约定（per `253` §SCHEMA "路由建议"）

| 字段 | 约定 |
|---|---|
| slug 字符集 | `[a-z0-9-]+` |
| slug 来源 | 中文地名 pinyin 去声调（南京→nanjing；苏州→suzhou；...）|
| slug 唯一性 | 全局唯一（与省 slug 不冲突：province 已用 `jiangsu/zhejiang/guangdong`）|
| slug 守门 | `frontend/lib/city_slug_map.ts`（lite 落地刀新建）+ 单元测试 |

### 3.2 路由建议（per `253` §SCHEMA "路由建议"）

| 选项 | 描述 | 评估 |
|---|---|---|
| **A** | `/cities/{slug}`（顶层）| ✅ **推荐** — 简单；Gate 2 评审易点名 |
| B | `/provinces/{province_slug}/cities/{city_slug}`（挂省下）| ⚠️ 嵌套；URL 长；评审点名麻烦 |

**裁定**：A — 顶层 `/cities/{slug}`。理由：
- 5 省 + 10 地市 = 15 页面；独立路由评审易点名
- 与 docs/44 §5.1.1 "5 省 + 10 地市 = 15 页面" 一致
- 与 docs/45 §2 #1 "5 省 + 10 地市观察页面上线" 一致
- 与 docs/08 §3.2 #1 "5 个省/10 个地市观察页面上线" 一致

**Static-segment 守门**（per AGENTS.md "Static-segment Next.js routes must NOT branch on params.*"）：
- `/cities/[slug]` 必须用 dynamic segment route（`generateStaticParams` + `params.slug`）
- 不能用 static segment + params.* 分支（`/cities/jiangsu` 之类的写法会失败）
- 落地刀须明示此约定

### 3.3 文件路径约定

| 资源 | 路径 | 备注 |
|---|---|---|
| 路由 | `frontend/app/cities/[slug]/page.tsx` | dynamic segment |
| 组件 | `frontend/app/components/CityPage.tsx` | 复用 S2.7-a 5 省模板 |
| 数据 | `frontend/lib/mock_cities.ts` | 10 地市 mock 数据 |
| slug 映射 | `frontend/lib/city_slug_map.ts` | `nanjing` → 南京市 等 |
| 类型 | `frontend/lib/types_cities.ts` | CityProps 接口 |
| pytest | `tests/test_city_slug_map_s27b.py` | slug 唯一性 + 字符集守门 |

---

## 4. UI 复用 S2.7-a 5 省模板

> per docs/44 §5.1.1 "5 省 lite 已交（mock）"+ `253` §SCHEMA "缩刀落地预期：S2.7-b-lite 10 城 mock 壳 + EvidenceChain 复用"

### 4.1 复用边界

| 元素 | S2.7-a 来源 | S2.7-b 复用 |
|---|---|---|
| 5 段证据链 UI | `frontend/app/components/EvidenceChain.tsx` | ✅ **直接复用**（段级渲染 city 段级 evidence）|
| 城市选择器 | 无 | ❌ 新增（CityPage 顶部下拉）|
| 七维度观察卡 | `frontend/app/components/SevenDimGrid.tsx` | ✅ **直接复用**（lite mock + 7 cell）|
| 同类地区对比 | `frontend/app/components/PeerCompareCard.tsx` | ✅ **直接复用**（江苏地市横向 / 浙江地市横向 / 广东地市横向）|
| 官员履历 | 无（5 省 lite 无）| ⚠️ **OPEN** — person/tenure 真数据接入契约 |

### 4.2 落地刀复用清单（S2.7-b-lite）

```tsx
// frontend/app/cities/[slug]/page.tsx (sketch — 落地刀实做)
import { CityPage } from '../../components/CityPage';
import { MOCK_CITIES } from '../../../lib/mock_cities';
import { CITY_SLUG_MAP } from '../../../lib/city_slug_map';

export function generateStaticParams() {
  return Object.keys(CITY_SLUG_MAP).map(slug => ({ slug }));
}

export default function Page({ params }: { params: { slug: string } }) {
  const city = MOCK_CITIES[params.slug];
  if (!city) return <NotFound />;
  return <CityPage city={city} />;
}
```

---

## 5. EvidenceChain 接入边界

> per docs/44 §5.2 "六段证据链完整可点击" + docs/45 §2 #2 不可降级

### 5.1 段级适配（per docs/40 §2 + docs/41 §3）

| 段 | S2.7-a 5 省适配 | S2.7-b 10 城适配 | 来源 |
|---|---|---|---|
| `CONDITION` | ✅ 省情基础 | ✅ **市情基础**（地市经济/人口/区位）| docs/40 §2.5 |
| `COMMITMENT` | ✅ 省五年规划 | ⚠️ **市五年规划 / 重点工作**（per docs/41 §3.2；lite 阶段用 mock）| docs/41 §3.2 |
| `PROCESS` | ✅ 省政策落实过程 | ⚠️ **市政策执行过程**（per docs/41 §3.3；lite 阶段用 mock）| docs/41 §3.3 |
| `OUTPUT` | ✅ 省产出（GDP/财政/项目）| ⚠️ **市产出**（per docs/41 §3.4；lite 阶段用 mock）| docs/41 §3.4 |
| `OUTCOME` | ✅ 省结果（民生/生态）| ⚠️ **市结果**（lite 阶段用 mock）| docs/41 §3.4 |
| `FEEDBACK` | ✅ 省反馈 | ⚠️ **市反馈**（lite 阶段用 mock）| docs/41 §3.4 |

**守门**：6 段全部 UI 渲染（per docs/45 §2 #2 不可降级）+ 反例登记 trigger（per migration 013）。

### 5.2 地市段级数据契约（OPEN — 落地刀填）

```ts
// 落地刀 (S2.7-b-full 或 S2.7-b-lite) 须填充：
interface CityEvidenceBySegment {
  city_id: string;
  segment: 'CONDITION' | 'COMMITMENT' | 'PROCESS' | 'OUTPUT' | 'OUTCOME' | 'FEEDBACK';
  canonical_statement: string;
  canonical_polarity: 'SUPPORTS' | 'CONTRADICTS' | 'NEUTRAL';
  evidence_strength: 'STRONG' | 'MODERATE' | 'WEAK';
  info_layer: 'OBSERVATION' | 'EVALUATION' | 'INTERPRETATION' | 'CRITIQUE';
  lineage: { is_demo: boolean; source_file_sha256: string; ... };
}
```

---

## 6. 切刀边界：S2.7-b-lite vs S2.7-b-full

### 6.1 S2.7-b-lite（首落刀 — tasking 254+ 预期）

| 范围 | 包含 |
|---|---|
| 路由 | `/cities/[slug]` 落地 |
| 10 地市 mock 数据 | `frontend/lib/mock_cities.ts`（10 × 6 段 × mock）|
| EvidenceChain 复用 | ✅ S2.7-a 复用 |
| 七维度观察卡复用 | ✅ S2.8-lite 复用 |
| 同类地区对比复用 | ✅ S2.9-lite 复用（同省地市横向）|
| 不可降级验收项 #2 | ✅ 六段 UI 渲染 + 反例 trigger（per docs/45 §2 #2）|
| person/tenure 真数据 | ❌ mock 占位（per `253` §SCHEMA "本规划刀与 lite 不强制接满 mart"）|
| dbt mart 接入 | ❌ 仍 mock |
| smoke-check | ✅ 通过 |
| pytest | `tests/test_city_slug_map_s27b.py`（slug 守门）+ 跨 lite 回归不破 |

### 6.2 S2.7-b-full（次落刀 — tasking 25X+ 预期；OPEN）

| 范围 | 包含 |
|---|---|
| dbt mart | `mart_city_evidence_chain`（新增）+ `mart_city_seven_dim_overview`（新增）|
| person/tenure 真数据接入 | `mart_person_tenure` JOIN `comparison_group` 横向 |
| 10 地市 mock → 真数据迁移 | 仅在 O1 真实 SHA + Stage 1 OPEN 收口后做 |
| 演示数据策略 | per docs/34 §11.2 "A 仅 mock"；full 切换需 O1 收口 |

---

## 7. 验收清单（per docs/08 §3.2 #1 + docs/44 §5.1.2 + `253` §SCHEMA）

### 7.1 S2.7-b-lite 验收（首落刀）

| # | 项 | 来源 |
|---|---|---|
| 1 | 10 地市页面（南京/苏州/无锡/南通/杭州/宁波/温州/广州/深圳/东莞）上线 | docs/08 §3.2 #1 |
| 2 | 路由 `/cities/{slug}` 可点；slug 唯一；字符集 `[a-z0-9-]+` | docs/45 §5.1 + §3.1 |
| 3 | EvidenceChain 6 段可点击（CONDITION/COMMITMENT/PROCESS/OUTPUT/OUTCOME/FEEDBACK）| docs/45 §2 #2 不可降级 |
| 4 | 七维度观察卡 7 cell 渲染 + 折叠/展开 | docs/45 §2 #3 演示级可过 |
| 5 | 同类地区对比（同省地市横向）| docs/43 §4.1 |
| 6 | `is_demo` sentinel（per docs/33 §3.2）| docs/45 §5.4 |
| 7 | smoke-check PASS（5 省模板复用 + 10 城新 page）| AGENTS.md |
| 8 | 跨 lite 回归不破（s21lite..s26lite + s210 = 42+12 = 54 PASS）| docs/45 §4 |
| 9 | pytest `test_city_slug_map_s27b.py` ≥3 case PASS | docs/45 §4 |
| 10 | 反例登记 trigger（per migration 013）| docs/45 §2 #6 已交 |

### 7.2 S2.7-b-full 验收（次落刀；OPEN）

| # | 项 | 来源 |
|---|---|---|
| 11 | dbt mart `mart_city_evidence_chain` + `mart_city_seven_dim_overview` 落地 | docs/44 §7.3 |
| 12 | 10 地市 mock → 真数据迁移（仅 O1 + Stage 1 OPEN 收口后）| docs/34 §11.2 |
| 13 | person/tenure 接入契约 + mart JOIN 通过 | docs/44 §7.3 |
| 14 | 七维度 card 5 枚举守门（`balance_status` ∈ {NO_EVIDENCE, NO_CONTRADICTING_EVIDENCE, NO_SUPPORTING_EVIDENCE, SUPPORTS_DOMINANT, CONTRADICTS_DOMINANT}）| docs/42 §2.5 |
| 15 | 段级 evidence gaps 显示（per docs/44 §1.1 S2.7-a 段级证据链接驳）| docs/44 §1.1 |

---

## 8. 红线自检（per `253` §红线 + docs/34 §1/§8/§133）

| 红线 | 状态 |
|---|---|
| ❌ 宣布 Gate 2 PASS | ✅ §1.2 + §6 + §7 + §9 多次显式守门 |
| ❌ 改 Cursor 锁定 10 城名单 | ✅ §2 锁定清单；不得擅自换/加 |
| ❌ 伪造 SHA / 伪造证据 | ✅ 仅规划；无 SHA 操作 |
| ❌ 官员能力总分 / 排名 / DSH / 实时数据 | ✅ docs/45 §2 #4 守门 |
| ❌ 批量爬政策研究 / 财政预决算 / 官员履历 | ✅ |
| ❌ HTTP 爬源站 | ✅ |
| ❌ 降 OCR 门槛 | ✅ |
| ❌ 改 `gate_thresholds.json` | ✅ |
| ❌ 改 `00-CC-CURRENT.md` | ✅ Cursor 拥有 |
| ❌ --force / --force-with-lease | ✅ |
| ❌ 索要 PAT | ✅ |
| ✅ pack invariant 守门 | ⏳ bump + commit 后 578 == 578 == 578 |
| ✅ receipts 仅写 `reviews/stage0-gate0-rework-2026-08-23/` | ✅ |
| ✅ 不写 dbt mart | ✅（本刀仅规划）|
| ✅ 不写 migration | ✅ |
| ✅ 不擅自提前 Gate 2 评审日期 | ✅ W8（per docs/34 §10.4）|
| ✅ 不接全国实时排名 | ✅（per docs/34 §4.3）|
| ✅ 不引入 score / rating / rank 字段 | ✅ §9 红线条目 |
| ✅ 不引入 schema ENUM | ✅ 应用层 enum-style 守门 |
| ✅ Static-segment 守门（dynamic segment route）| ✅ §3.2 |

---

## 9. 不做什么（本刀 S2.7-b 规划边界；推后续刀）

| ❌ | 推到 |
|---|---|
| ❌ 宣布 Gate 2 PASS | Gate 2 评审日（暂定 W8，per docs/34 §10.4）|
| ❌ 伪造 SHA / 伪造证据 | 红线 |
| ❌ 改 10 城名单 | 红线（per `253` §SCHEMA）|
| ❌ 10 地市页面落地 | S2.7-b-lite（tasking 254+）|
| ❌ dbt mart 落地 | S2.7-b-full（tasking 25X+；OPEN）|
| ❌ person/tenure 真数据接入 | S2.7-b-full + O1 真实 SHA 收口后 |
| ❌ 5 省 + 10 地市全 15 页面同时上线 | S2.7-b-lite 优先 10 城；S2.7-a 已交 5 省 |
| ❌ 改 docs/06 / docs/08 / docs/10 / docs/34 / docs/40 / docs/41 / docs/42 / docs/43 / docs/44 / docs/45 内容 | Cursor 拥有 |
| ❌ 改 `gate_thresholds.json` | spike-04 评测构件，只读 |
| ❌ 启用 pgvector / RLS / partition | Stage 2 边界（per docs/04 §6）|

---

## 10. 与现有文档的关系

| 引用 | 用途 |
|---|---|
| `docs/05-data-spec.md` §8.1 | 4 维度匹配依据（人口/区位/产业/发展阶段）|
| `docs/06-governance-observation-method.md` §6.6 | 综合指数纪律（**红线**：不评分；不排名）|
| `docs/08-mvp-plan.md` §3.1 | Stage 2 任务清单（13 刀）|
| `docs/08-mvp-plan.md` §3.2 #1 | Gate 2 验收项 #1（5 省 + 10 地市）|
| `docs/08-mvp-plan.md` §3.3 | Stage 2 红线 4 条 |
| `docs/33-data-lineage.md` §3.2 | `is_demo` sentinel |
| `docs/34-stage2-s20-kickoff-plan-20260825.md` §1 | 状态："草案；不宣布 Gate 1/2 PASS" |
| `docs/34-stage2-s20-kickoff-plan-20260825.md` §4 序 5 | S2.7-b = 10 地市观察页 |
| `docs/34-stage2-s20-kickoff-plan-20260825.md` §8 #8 | 不宣布 Gate 2 PASS |
| `docs/34-stage2-s20-kickoff-plan-20260825.md` §10.4 | Gate 2 评审日期 W8 |
| `docs/34-stage2-s20-kickoff-plan-20260825.md` §11.2 | 演示数据策略（仅 mock）|
| `docs/34-stage2-s20-kickoff-plan-20260825.md` §11.6 | 10 地市选择（建议由 Cursor/用户裁定）|
| `docs/40-stage2-s25-inference-plan-20260826.md` §5 | INFERENCE/JUDGMENT 角标 |
| `docs/41-stage2-s26-counterexample-plan-20260826.md` §3 | 段级 evidence |
| `docs/42-stage2-s28-seven-dim-plan-20260826.md` §2.5 | 七维度 cell 5 枚举 |
| `docs/43-stage2-s29-peer-compare-plan-20260826.md` §4.1 | 江苏 focal 候选 |
| `docs/44-stage2-s210-gate2-package-plan-20260826.md` §5.1.2-§5.1.3 | 10 地市 OPEN + 候选清单 |
| `docs/45-stage2-s210-lite-gate2-review-index-20260826.md` §2 #1 | 10 地市 OPEN 必带 |
| `frontend/app/provinces/{jiangsu,zhejiang,guangdong,shandong,sichuan}/page.tsx` | 5 省 lite 模板 |
| `frontend/app/components/EvidenceChain.tsx` | 六段证据链 UI |
| `frontend/app/components/SevenDimGrid.tsx` | 七维度观察卡 |
| `frontend/app/components/PeerCompareCard.tsx` | 同类地区对比 |
| `schema/migrations/013_counterexample_gate.sql` | 反例 trigger |

---

## 11. CC 建议（供 Cursor 审阅 / 用户裁定）

### 11.1 路由方案

| 选项 | 描述 | 选 |
|---|---|---|
| A | `/cities/{slug}`（顶层）| ✅ **推荐**（per §3.2）|
| B | `/provinces/{province_slug}/cities/{city_slug}`（挂省下）| 嵌套；URL 长 |

### 11.2 落地刀节奏

| 选项 | 描述 | 选 |
|---|---|---|
| A | S2.7-b-lite（10 城 mock 壳）→ S2.7-b-full（接 mart）分两刀 | ✅ **推荐**（per `253` §SCHEMA + §6）|
| B | 单刀同时上线 10 城 + 接 mart | 越界（O1 OPEN 未收口）|

### 11.3 不可降级验收项

| 项 | 状态 |
|---|---|
| 六段证据链 UI（验收项 #2）| ✅ **不可降级**（per docs/45 §2 #2）|
| 10 城路由 + slug 守门（验收项 #1 配套）| ✅ 演示级可过 |
| 七维度观察卡（验收项 #3）| ✅ 演示级可过 |

### 11.4 段级 evidence 接入

| 选项 | 描述 | 选 |
|---|---|---|
| A | lite 阶段用 6 段 mock；full 阶段接 `mart_city_evidence_chain` | ✅ **推荐** |
| B | lite 阶段接 `mart_province_evidence_chain` 横向（复用 5 省）| 强依赖 S2.7-a full 落地 |

### 11.5 同类地区对比

| 选项 | 描述 | 选 |
|---|---|---|
| A | 同省地市横向（南京↔苏州↔无锡↔南通；杭州↔宁波↔温州；广州↔深圳↔东莞）| ✅ **推荐**（per docs/43 §4.1 + S2.9-lite）|
| B | 跨省地市对比（深圳↔苏州）| ⚠️ 越界（per docs/34 §4.3）|

---

— End of `docs/46` —

> 等待 Cursor 审验（预期 `255-stage0-cursor-s27b-plan-audit-…md`）。
> 通过后下发 S2.7-b-lite 落地任务（`256-stage2-s27b-lite-cities-impl-tasking-…md`），进入 10 城 mock 壳落地。
> ⚠ **本刀不宣布 Gate 2 PASS**（per docs/34 §1 + §8 #8 + `253` §红线）。
> ⚠ **10 城名单已锁定**（per `253` §SCHEMA；不得擅自更改）。
> Gate 2 评审日期暂定 W8（per docs/34 §10.4）。