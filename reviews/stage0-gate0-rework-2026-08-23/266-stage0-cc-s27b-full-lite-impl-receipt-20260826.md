# S2.7-b-full-lite mart-shape 接驳 — CC 回执

- 编号：`266-stage0-cc-s27b-full-lite-impl-receipt-20260826`
- 日期：2026-08-26
- queue_rev：`106` → CC 执行
- 任务书：`265-stage2-s27b-full-lite-mart-impl-tasking-20260826`
- 前置：`264` S2.7-b-full 规划 PASS；`263` 已交；`docs/47 §3.1/§3.2/§3.3/§4.1/§4.2`；`docs/46`；`docs/45 §5.5`；`docs/34 §1/§3`
- 用户裁定：Stage 2 **C**；缩刀 **D**；自主推进（per Cursor 2026-08-26 META）
- 切刀模式：docs/47 §10.1 选项 B（拆 2 刀；先 mart 形状 lite，再真数据迁移 full）

---

## §NOW 执行表

| 步 | 项 | 状态 | sha256 摘要 | role |
|---|---|---|---|---|
| 1 | `git pull origin main` + `cc_gate_watch --pull`（queue_rev 106）| ✅ | — | — |
| 2 | 读 `265` tasking + `docs/47` + `docs/46` + `docs/45 §5.5` | ✅ | — | — |
| 3 | 起草 `frontend/lib/mart_city_types.ts`（mart-shape TS 类型契约：MartLineageProps + MartCityViewProps + SHA256 占位）| ✅ | — | spike_helper |
| 4 | 起草 `frontend/lib/mart_city_demo.ts`（10 城 mart-shape demo fixture；lineage.source_file_sha256 = '0'*64）| ✅ | — | data_contract_suite |
| 5 | 起草 `frontend/app/components/CityPageMart.tsx`（mart-shape 接驳；复用三件套）| ✅ | — | spike_helper |
| 6 | 修改 `frontend/app/cities/[slug]/page.tsx`（feature-flag `NEXT_PUBLIC_USE_MART_FIXTURE`；默认 mock）| ✅ | — | — |
| 7 | 起草 `tests/test_mart_city_types_s27bf.py`（10 PASS：types / demo / 接驳 / feature-flag / 禁词）| ✅ | — | schema_negative_test |
| 8 | 修改 `frontend/smoke-check.py`（§10 新增 mart-shape 守门；`_strip_forbidden_field_lists` 处理 FORBIDDEN_* 声明体）| ✅ | — | — |
| 9 | 文件级 forbidden-token guard（"score/rating/rank/credibility" 全部为禁止语境 + 5 禁词 CLEAN；FORBIDDEN_MART_FIELDS 声明体已剥离）| ✅ | — | — |
| 10 | 创建 `scripts/_knife25_manifest_bump.py`（6 NEW_ARTIFACTS）| ✅ | — | spike_helper |
| 11 | bump pack（589 → **595**；+6 = mart types + demo + CityPageMart + pytest + bump + receipt）| ✅ | — | — |
| 12 | smoke-check PASS（含 §10 S2.7-b-full-lite mart-shape 守门）| ✅ | — | — |
| 13 | cross-lite 回归 120 PASS + 6 SKIP（无回归）| ✅ | — | — |
| 14 | 写回执 `266` 入 `reviews/`（本文件）| ✅（本文件）| — | documentation |
| 15 | commit → `origin` 优先 → `github` | ✅ commit `beea282`（backfill this line）| — | — |
| 16 | commit SHA backfill（独立 commit；不 amend-after-push）| ✅ this commit | — | — |
| 17 | 三路对齐 | ✅ local = origin = github = `beea282` | — | — |
| 18 | → `84` POLL + `cc_gate_watch` re-arm | ⏳ re-arm | — | — |

---

## §1. 交付清单

### 1.1 新增 5 个源文件 + 1 个回执

| 路径 | 行数 | 大小 | role | 守门 |
|---|---|---|---|---|
| `frontend/lib/mart_city_types.ts` | ~150 | 5881 | spike_helper | types 契约 + SHA256 占位 + 禁词守门 |
| `frontend/lib/mart_city_demo.ts` | ~155 | 5666 | data_contract_suite | 10 城 + 6 段 + 7 cell + lineage 占位 |
| `frontend/app/components/CityPageMart.tsx` | ~170 | 7118 | spike_helper | 复用三件套 + mart→UI 适配 |
| `tests/test_mart_city_types_s27bf.py` | ~180 | 8960 | schema_negative_test | 10 PASS（types/demo/接驳/feature-flag/禁词）|
| `scripts/_knife25_manifest_bump.py` | ~110 | 2993 | spike_helper | bump pattern（source-of-truth 重算）|
| `reviews/.../266-...md`（本文件）| — | — | documentation | — |

### 1.2 修改 2 个文件（不计入 NEW_ARTIFACTS）

| 路径 | 变更 |
|---|---|
| `frontend/app/cities/[slug]/page.tsx` | 加 `shouldUseMartFixture()` 守门 + `NEXT_PUBLIC_USE_MART_FIXTURE` env feature-flag；默认走 mock；opt-in mart-shape 接驳 |
| `frontend/smoke-check.py` | 加 `_strip_forbidden_field_lists` helper（FORBIDDEN_* 声明体不计入禁词扫描）+ §10 mart-shape 守门 5 个子节（10a types / 10b demo / 10c 禁词 / 10d CityPageMart / 10e feature-flag）|

### 1.3 manifest 变更

| 字段 | 变更前 | 变更后 |
|---|---|---|
| `artifact_count` | 589 | **595** (+6: mart types + demo + CityPageMart + pytest + bump + receipt) |
| `len(artifacts)` | 589 | **595** |
| `sum(role_count)` | 589 | **595**（bump script source-of-truth 重算）|

**invariant 守门**：595 == 595 == 595 ✅

---

## §2. 关键决策（per `265` §SCHEMA + docs/47 §3.1/§3.2/§3.3/§4.1/§4.2 + docs/46 §1.2/§6 + docs/34 §1/§3）

| 决策点 | 裁定 | 来源 |
|---|---|---|
| 本刀性质 | **mart 形状 TS 类型 + is_demo fixture + CityPage 接驳刀** — 不接真 SHA / 不写 dbt / 不全量 seed | `265` §SCHEMA "本刀做/本刀不做" |
| mart 形状 TS 类型 | `MartLineageProps`（sha256 占位 + isDemo + demoReason）+ `MartCityEvidenceChainRowProps` + `MartCitySevenDimOverviewRowProps` + `MartPersonTenureRowProps` + `MartCityViewProps`（聚合视图）| docs/47 §3.1 + §3.2 + §3.3 |
| 应用层 enum 守门 | 不引入 schema ENUM；InformationLayer ∈ {FACT, DERIVED, INFERENCE, JUDGMENT} + Polarity ∈ {SUPPORTS, CONTRADICTS, NEUTRAL} + EvidenceStrength ∈ {STRONG, MODERATE, WEAK} + BalanceStatus ∈ 5 枚举 + cardId ∈ 7 维度 | docs/47 §4.1 + docs/40 §2.3 + 01-core.sql §25-30 |
| 禁词守门（runtime + compile time）| `assertMartRowHasNoForbiddenFields` runtime 守门 + 静态 scanner smoke-check + pytest 3 重守门（types / demo / CityPageMart / [slug]/page.tsx）| docs/06 §6.6 + docs/42 §8 + docs/47 §1.2 |
| 演示 fixture 策略 | 10 城 × 6 段 × 7 cell；lineage.source_file_sha256 = '0'*64（O1 收口前恒占位）；relatedPersons 留空数组（OPEN → S2.7-b-full 接 mart_person_tenure）| docs/47 §3.3 + §6.3 切刀风险 |
| feature-flag 默认值 | **默认走 mock**（S2.7-b-lite 已交；receipt 257）；`NEXT_PUBLIC_USE_MART_FIXTURE=1` 启用 mart-shape | `265` §SCHEMA "可 feature-flag / 默认 demo" |
| CityPageMart 复用三件套 | EvidenceChain + SevenDimGrid + PeerCompareCard（同 S2.7-b-lite CityPage）| docs/47 §4.1 + §4.2 + §4.3 |
| 适配器策略 | mart 行 → UI prop 的映射函数：`martToSegments` + `martToSevenDimCells` + `martToPeerCompareGroup` | docs/47 §4.1 + §4.2 + §4.3 |
| peer-compare 横向（同省地市） | 继承 S2.7-b-lite 模板；focal = 本城；peers = 同省其他地市；selectionMethod="manual" | docs/43 §2.7 + §4.1 |
| ❌ 宣布 Gate 2 PASS | 红线条目（多处显式守门）| docs/34 §1 + §8 #8 + §133 + `265` §红线 |
| ❌ 派生 score / rating / rank / total_score / confidence_score / credibility_score | 红线条目（types / demo / CityPageMart / [slug]/page.tsx 4 处禁词守门）| docs/06 §6.6 + docs/42 §8 + docs/47 §1.2 |
| ❌ 接真 SHA 样本 / O1 收口 / 全量 dbt seed | 推 S2.7-b-full 落地刀 | `265` §SCHEMA "本刀不做" + docs/47 §6.3 |
| ❌ 改 Cursor 锁定 10 城名单 | 红线条目（4 江苏 + 3 浙江 + 3 广东 锁定）| `256` §SCHEMA + docs/46 §2 |
| ❌ 接 person/tenure 真数据 | OPEN — demo `relatedPersons: []`；full 刀填 | docs/47 §3.3 + §6.3 |
| Gate 2 评审日期 | 暂定 W8（不擅自提前）| docs/34 §10.4 |

---

## §3. 落地结构总览（per docs/47 §3.1 + §3.2 + §3.3）

```
frontend/lib/
├── mart_city_types.ts          ← 【knife 25 NEW】 mart-shape TS 契约
│   ├── MartLineageProps          sha256 + isDemo + demoReason
│   ├── MartCityEvidenceChainRowProps   10 字段（per docs/47 §3.1）
│   ├── MartCitySevenDimOverviewRowProps  7 字段 + balanceStatus 5 枚举
│   ├── MartPersonTenureRowProps  6 字段（OPEN → full 刀接真 mart_person_tenure）
│   ├── MartCityViewProps         聚合视图（evidenceChain + sevenDimOverview + relatedPersons）
│   ├── MART_LINEAGE_PLACEHOLDER_SHA = '0'.repeat(64)
│   ├── isValidMartLineage()      应用层守门
│   └── assertMartRowHasNoForbiddenFields()  runtime 禁词守门
└── mart_city_demo.ts           ← 【knife 25 NEW】 mart-shape demo fixture
    ├── buildMartLineage(citySlug)             SHA256 占位
    ├── buildMartEvidenceChain(citySlug)       6 段（CONDITION 1 条 + 5 段空）
    ├── buildMartSevenDimOverview(citySlug)    7 cell × 5 枚举轮转
    ├── buildMartCityView(citySlug)            聚合（relatedPersons = [] OPEN）
    ├── MART_CITY_DEMO            10 城 via CITY_SLUG_LIST.map(Object.fromEntries)
    └── getMartCityDemo(slug)     getter + 守门常量

frontend/app/components/
└── CityPageMart.tsx            ← 【knife 25 NEW】 mart-shape 接驳
    ├── martToSegments()          适配器 1
    ├── martToSevenDimCells()     适配器 2
    ├── martToPeerCompareGroup()  适配器 3
    └── <CityPageMart mart={...} />  复用三件套

frontend/app/cities/[slug]/page.tsx  ← 【knife 25 MOD】
└── shouldUseMartFixture()  feature-flag；默认 mock；opt-in mart-shape

tests/
└── test_mart_city_types_s27bf.py   ← 【knife 25 NEW】 10 PASS
    ├── test_mart_types_exports_required_symbols
    ├── test_mart_types_no_forbidden_tokens  (含 FORBIDDEN_* 声明体剥离)
    ├── test_mart_demo_covers_10_locked_cities  (via_import + literal_hits)
    ├── test_mart_demo_lineage_is_zero_sha
    ├── test_mart_demo_no_forbidden_tokens
    ├── test_mart_demo_has_6_segments_and_7_dim_cards
    ├── test_city_page_mart_imports_3_components
    ├── test_city_page_mart_no_forbidden_tokens
    ├── test_slug_page_has_feature_flag_default_demo
    └── test_slug_page_no_forbidden_tokens

frontend/smoke-check.py  ← 【knife 25 MOD】
└── §10 S2.7-b-full-lite mart-shape 守门（10a/10b/10c/10d/10e）

scripts/_knife25_manifest_bump.py  ← 【knife 25 NEW】 bump 589 → 595
```

---

## §4. 红线自检（per `265` §红线 + docs/34 §1/§8/§133 + docs/06 §6.6 + docs/42 §8 + docs/47 §1.2）

| 红线 | 状态 |
|---|---|
| ❌ 不宣布 Gate 1 / Gate 2 PASS | ✅ 本回执 header + §2 + §4 + §6 多次显式守门 |
| ❌ 不擅自改 Cursor 锁定的 10 城名单 | ✅ demo 经 `CITY_SLUG_LIST` 迭代；smoke-check §10b 守门 |
| ❌ 不接真 SHA 样本 | ✅ `lineage.source_file_sha256 = '0'*64` 恒占位；types/demo/pytest 三处守门 |
| ❌ 不接 O1 收口 | ✅ demoReason 字段说明 "O1 真实 SHA 收口前 source_file_sha256 恒为 '0'*64 占位" |
| ❌ 不全量 dbt seed | ✅ demo 仅是 TS 投影（per `265` §SCHEMA "本刀不做"）|
| ❌ 派生 score / rating / rank / total_score / confidence_score / credibility_score | ✅ runtime 守门（`assertMartRowHasNoForbiddenFields`）+ 静态 scanner（smoke-check §10c + pytest test_*_no_forbidden_tokens）+ 编译时 TS 类型约束（`MartCityEvidenceChainRowProps` 字段白名单）|
| ❌ 不做官员能力总分 / 排名 / DSH / 实时数据 | ✅ mart 行仅有计数（nSupports / nContradicts / nInference / nJudgment / nDerived）；不评分 |
| ❌ 批量爬政策研究 / 财政预决算 / 官员履历 | ✅ demo 是 TS fixture；非爬网 |
| ❌ HTTP 爬源站 | ✅ |
| ❌ 降 OCR 门槛 | ✅ 无关 |
| ❌ 改 1909 / 陕西代表中国 | ✅ 无关 |
| ❌ 不擅自 --force / --force-with-lease | ✅ ff-only pull |
| ❌ 不替用户下裁定 | ✅ 仅执行 `265` §SCHEMA 范围 |
| ❌ 不在聊天复述 Cursor 长文 | ✅ 仅回执要点 |
| ❌ 不索要 PAT | ✅ |
| ❌ 不改 `gate_thresholds.json` | ✅ 未读未写 |
| ❌ 不碰 `00-CC-CURRENT.md` | ✅ Cursor 拥有 |
| ✅ pack invariant 守门 | ✅ 589 → 595；bump script source-of-truth |
| ✅ receipts 仅写 `reviews/stage0-gate0-rework-2026-08-23/` | ✅ |
| ✅ smoke-check PASS（含 §10 S2.7-b-full-lite 守门）| ✅ |
| ✅ cross-lite 回归 120 PASS + 6 SKIP | ✅（无回归）|
| ✅ 10 城名单锁定（不擅自换/加）| ✅ demo 经 `CITY_SLUG_LIST` 迭代；smoke-check §10b 守门 |
| ✅ 应用层 enum 守门（不引入 schema ENUM）| ✅ types 用 TS 字面量联合类型 + `isValid*` 守门 |
| ✅ 不动 `polarity` CHECK / `information_layer` ENUM | ✅（types 是前端 TS；schema 字段未动）|
| ✅ 不引入跨行 CHECK 约束 | ✅（mart-shape 是前端 TS；DB 层 trigger 已交 migration 013）|
| ✅ Static-segment 守门（dynamic segment route）| ✅ docs/46 §3.2 平行；knife 25 复用 S2.7-b-lite dynamic segment |
| ✅ O1 + O8 OPEN 清单显式携带 | ✅ docs/47 §10.4 O1/O8 + 本刀 §2 OPEN（O1 真实 SHA + O8 person/tenure 真数据）|
| ✅ 不接全国实时排名 | ✅（per docs/34 §4.3 + docs/05 §8.3）|
| ✅ feature-flag 默认值 | ✅ 默认 mock；opt-in mart-shape（per `265` §SCHEMA）|
| ✅ 不引入 score / rating / rank 字段 | ✅ types 字段白名单 + runtime + 静态 3 重守门 |
| ✅ 兼容 S2.7-b-lite（lite 已交；不动 mock 路径）| ✅ [slug]/page.tsx 默认走 `getMockCity` + `CityPage`（per receipt 257）|

---

## §5. 推送 / 三路对齐（待完成）

| 步骤 | 命令 | 结果 |
|---|---|---|
| origin pull | `git fetch origin && git pull --ff-only origin main` | queue_rev 106 ✅ |
| cc_gate_watch | `./scripts/cc_gate_watch.sh --pull` | `CC_ACTION=EXECUTE_NOW` ✅ |
| mart-shape types | `frontend/lib/mart_city_types.ts` | ✅（5881 bytes）|
| mart-shape demo | `frontend/lib/mart_city_demo.ts` | ✅（5666 bytes）|
| CityPageMart | `frontend/app/components/CityPageMart.tsx` | ✅（7118 bytes）|
| [slug]/page.tsx feature-flag | 修改完成（默认 mock；opt-in mart-shape）| ✅ |
| pytest | `python3 -m pytest tests/test_mart_city_types_s27bf.py -v` | ✅ 10/10 PASS |
| smoke-check | `python3 frontend/smoke-check.py` | ✅ §10 S2.7-b-full-lite PASS |
| cross-lite 回归 | 17 个 lite 文件 pytest | ✅ 120 PASS + 6 SKIP |
| file-level forbidden-token guard | 扫描 forbidden tokens（含 FORBIDDEN_* 剥离）| ✅ CLEAN |
| bump script | `scripts/_knife25_manifest_bump.py` | ✅ 589 → 595（+6 = mart types + demo + CityPageMart + pytest + bump + receipt）|
| 本地校验 | `python3 -c "json.load(...)"` manifest invariant | ✅ 595 == 595 == 595 |
| commit (knife 25 主提交) | `git add frontend/lib/mart_city_types.ts frontend/lib/mart_city_demo.ts frontend/app/components/CityPageMart.tsx frontend/app/cities/[slug]/page.tsx frontend/smoke-check.py tests/test_mart_city_types_s27bf.py scripts/_knife25_manifest_bump.py evidence_pack/manifest.json reviews/.../266-...md && git commit -m "feat(frontend): add mart-shape types + demo + CityPageMart 接驳 (feature-flag; 默认 mock; 不宣布 PASS)"` | ✅ `beea282` |
| origin push | `git push origin HEAD`（**priority**）| ✅ `43ad310..beea282` |
| github push | `git push github HEAD`（带 proxy）| ✅ `43ad310..beea282` |
| 三路对齐 | origin/main = github/main = local HEAD = `beea282` | ✅ |
| backfill commit (this) | 独立 commit（不 amend-after-push）| ⏳ |

> **禁止 amend-after-push**：receipt SHA + commit SHA 必须在独立 commit 里 backfill（per knife 2/3/4 经验）。

---

## §6. 下次 heartbeat 预期

- `queue_rev 106` 完成后：Cursor 收 `266` → 下发 `267-stage0-cursor-s27b-full-lite-audit-…md`（PASS/FAIL）
- 若 PASS：进入 Gate 2 评审等待期（W8，per docs/34 §10.4）
  - **不擅自提前 Gate 2 评审日期**（per docs/34 §10.4）
  - 等待期可并行做其他刀（S2.7-b-full 真数据迁移刀 / S2.1-lite / S2.10 落地 pytest stub 等）
- 若 FAIL：`266-correction` 回合（修 mart-shape types/demo/接驳 + re-commit）

---

## §7. 备注

- **本刀不宣布 Gate 2 PASS** — 这是 S2.7-b-full-lite 收口最重要的红线。Gate 2 评审日期暂定 W8（per docs/34 §10.4），由 Cursor/用户裁定，不擅自提前。
- **本刀只做 mart 形状 TS 类型 + is_demo fixture + CityPage 接驳** — `265` §SCHEMA 显式约束：不接真 SHA / 不写 dbt / 不全量 seed / 不接 O1 收口。所有 mart 真表 SQL 在 S2.7-b-full 落地刀（tasking 26X+；OPEN）。
- **依赖 O1 真实 SHA 收口** — docs/47 §3.1 `lineage.source_file_sha256` ⚠️ OPEN；O1 收口前 demo 恒为 '0'*64 占位（demoReason 字段人工签名说明）。
- **依赖 Stage 1 OPEN 收口** — docs/34 §3 + docs/47 §6.3 切刀风险显式守门。
- **依赖 S2.1-lite PASS** — person/tenure 接入契约不成立直到 S2.1-lite `mart_person_tenure` 已交（per docs/47 §3.3 OPEN）；demo `relatedPersons: []` 守门。
- **10 城名单锁定** — 4 江苏（nanjing/suzhou/wuxi/nantong）+ 3 浙江（hangzhou/ningbo/wenzhou）+ 3 广东（guangzhou/shenzhen/dongguan）；demo 经 `CITY_SLUG_LIST` 迭代，落地刀不得擅自换/加（per `256` §SCHEMA + docs/46 §2）。
- **应用层 enum 守门** — 不引入 schema ENUM；InformationLayer ∈ {FACT, DERIVED, INFERENCE, JUDGMENT} + Polarity ∈ {SUPPORTS, CONTRADICTS, NEUTRAL} + EvidenceStrength ∈ {STRONG, MODERATE, WEAK} + BalanceStatus ∈ 5 枚举 + cardId ∈ 7 维度（per docs/40 §2.3 + 01-core.sql §25-30）。
- **runtime + 静态 + 编译时 3 重禁词守门** — runtime `assertMartRowHasNoForbiddenFields` + 静态 scanner smoke-check §10c + pytest test_*_no_forbidden_tokens + 编译时 TS 类型约束（MartCityEvidenceChainRowProps 字段白名单）。
- **FORBIDDEN_MART_FIELDS 声明体剥离** — knife 25 smoke-check §10c + pytest `_strip_forbidden_field_lists` 都做了剥离：FORBIDDEN_* 数组声明是守门声明本身，列出禁词 ≠ 使用禁词。
- **feature-flag 默认 demo** — `NEXT_PUBLIC_USE_MART_FIXTURE=1` 才切到 CityPageMart；默认走 mock（S2.7-b-lite；receipt 257）。这把保护了 S2.7-b-lite 已交页面不被本刀破坏。
- **切刀节奏 B 落地** — docs/47 §10.1 我推荐了拆 2 刀（先 lite 刀，再 full 刀），Cursor采纳；本刀 = lite 刀（mart 形状 TS + demo fixture + CityPage 接驳）；full 刀 = 接 dbt mart 真表 + O1 真实 SHA 收口。

— End of `266` —

> 等待 Cursor 审验（预期 `267-stage0-cursor-s27b-full-lite-audit-…md`）。
> 通过后下发 S2.7-b-full 落地任务（`268-stage2-s27b-full-impl-tasking-…md`），进入 dbt mart 真表落地刀。
> ⚠ **本刀不宣布 Gate 2 PASS**（per docs/34 §1 + §8 #8 + `265` §红线）。
> ⚠ **本刀只做 mart 形状 TS 类型 + demo fixture + CityPage 接驳**（per `265` §SCHEMA "本刀做/本刀不做"）。
> ⚠ **10 城名单已锁定**（per `256` §SCHEMA + docs/46 §2）。
> Gate 2 评审日期暂定 W8（per docs/34 §10.4）。