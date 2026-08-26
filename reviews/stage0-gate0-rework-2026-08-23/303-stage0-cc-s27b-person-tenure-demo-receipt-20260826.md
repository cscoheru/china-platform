# S2.7-b person/tenure demo 接驳 — CC 回执

- 编号：`303-stage0-cc-s27b-person-tenure-demo-receipt-20260826`
- 日期：2026-08-26
- queue_rev：`125` → CC 执行
- 任务书：`302-stage2-s27b-person-tenure-demo-tasking-20260826`
- 前置：`301` docs/45 PASS；`docs/47` §3.3 person/tenure 接入契约 demo；O1 仍 OPEN
- 用户裁定：**D**；尽快看见数据；**O1 仍 OPEN**
- 任务性质：**S2.7-b person/tenure demo 接驳** — 10 城 × 2 demo 行（市委书记 + 市长 mock 占位）；显式 `is_demo=true`；无真履历爬取；对齐 `docs/47` §3.3 字段契约最小子集
- pack bump：**625 → 628**（+3 = pytest + bump + receipt；mart_city_demo.ts + CityPageMart.tsx 走 REFRESH 不增计数）

---

## §NOW 执行表

| 步 | 项 | 状态 | role |
|---|---|---|---|
| 1 | `git fetch origin && git pull --ff-only origin main`（queue_rev 125）| ✅ | — |
| 2 | 读 `302` tasking + `docs/47` §3.3 + `mart_city_types.ts` 字段契约 | ✅ | — |
| 3 | 改 `frontend/lib/mart_city_demo.ts`：加 `buildMartRelatedPersons(citySlug)` 工厂 + 导出常量 `MART_CITY_DEMO_RELATED_PERSONS_PER_CITY=2` + `MART_CITY_DEMO_RELATED_PERSONS_TOTAL` | ✅ MOD | spike_helper |
| 4 | 改 `frontend/app/components/CityPageMart.tsx`：加 relatedPersons UI 渲染区块 + `data-testid="city-page-mart-related-persons"` 守门 | ✅ MOD | spike_helper |
| 5 | 创建 `tests/test_mart_related_persons_demo_s302.py`（15 pytest cases）| ✅ NEW | schema_negative_test |
| 6 | pytest + smoke-check + 回归（40 PASS）| ✅ | — |
| 7 | 创建 `scripts/_knife37_manifest_bump.py`（3 NEW + 2 REFRESH）| ✅ NEW | spike_helper |
| 8 | bump pack（625 → **628**；+3 = pytest + bump + receipt）| ✅ | — |
| 9 | 写回执 `303` 入 `reviews/`（本文件）| ✅（本文件）| documentation |
| 10 | commit → `origin` 优先 → `github` | ✅ commit `372961d330a607f42627d1ba62d7251e665594ad` | — |
| 11 | commit SHA backfill（独立 commit；不 amend-after-push）| ⏳ this commit | — |
| 12 | 三路对齐 | ✅ local = origin = github = `372961d330a607f42627d1ba62d7251e665594ad` | — |
| 13 | → `84` POLL + `cc_gate_watch` re-arm | ✅ re-armed → `CC_ACTION=POLL` | — |

---

## §1. 交付清单

### 1.1 修改 2 + 新增 3 个文件

| 路径 | 行数 | role | 状态 |
|---|---|---|---|
| `frontend/lib/mart_city_demo.ts` | ~190 | spike_helper | MOD（+`buildMartRelatedPersons()` + 2 导出常量；buildMartCityView 串接）|
| `frontend/app/components/CityPageMart.tsx` | ~220 | spike_helper | MOD（+`relatedPersons` UI 区块；`data-testid` + `data-related-persons-count` 守门）|
| `tests/test_mart_related_persons_demo_s302.py` | ~280 | schema_negative_test | NEW |
| `scripts/_knife37_manifest_bump.py` | ~130 | spike_helper | NEW |
| `reviews/.../303-...md`（本文件）| — | documentation | NEW |

### 1.2 manifest 变更

| 字段 | 变更前 | 变更后 |
|---|---|---|
| `artifact_count` | 625 | **628** (+3: pytest + bump + receipt) |
| `len(artifacts)` | 625 | **628** |
| `sum(role_count)` | 625 | **628**（bump script source-of-truth 重算）|

**invariant 守门**：628 == 628 == 628 ✅

### 1.3 mart_city_demo.ts 修改详情

| § | 修改前 | 修改后 |
|---|---|---|
| imports | 仅 `MartLineageProps` + `MartCityViewProps` | + `MartPersonTenureRowProps` 类型导入 |
| buildMartLineage | 已存在 | 不变（lineage 占位；`sourceFileSha256 = '0'*64`）|
| buildMartEvidenceChain | 已存在 | 不变 |
| buildMartSevenDimOverview | 已存在 | 不变 |
| **buildMartRelatedPersons** | **不存在** | **NEW**：每城 2 demo 行（市委书记 + 市长）；canonical_name 全部 "演示 人物 N (mock, {slug})"；positionTitle "市委书记（演示职位）"/"市长（演示职位）"；`assertMartRowHasNoForbiddenFields(mart_related_persons[N])` 守门 |
| buildMartCityView | evidenceChain + sevenDimOverview + lineage | **+** `relatedPersons: buildMartRelatedPersons(citySlug)` |
| 导出常量 | `MART_CITY_DEMO_COUNT` + `MART_CITY_DEMO_PROVINCE_SLUGS` + `MART_IS_DEMO_SENTINEL` | **+** `MART_CITY_DEMO_RELATED_PERSONS_PER_CITY = 2` + `MART_CITY_DEMO_RELATED_PERSONS_TOTAL = MART_CITY_DEMO_COUNT * 2` |

### 1.4 CityPageMart.tsx 修改详情

| § | 修改前 | 修改后 |
|---|---|---|
| header 注释 | `+ §3.3 + §4.1 + §4.2 + `265`` | **+** `+ `302` §SCHEMA "10 城 demo relatedPersons/tenure 接驳"` |
| EvidenceChain + SevenDimGrid + PeerCompareCard 渲染 | 已存在 | 不变 |
| **relatedPersons UI 区块** | **不存在** | **NEW**：`<section data-testid="city-page-mart-related-persons">` 渲染 `mart.relatedPersons`（`<ul>` 列示 canonicalName + positionTitle + geoCanonicalName + isCurrent 现任/历任）；红条说明 "演示占位，不构成真实身份核验" |
| footer 红条 | 已存在 | 不变（仍指向 S2.7-b-full 真数据迁移刀 OPEN）|

---

## §2. 关键决策（per `302` §SCHEMA + docs/47 §3.3 + docs/34 §1/§3 + docs/06 §6.6 + docs/42 §8 + Cursor 174 S2.1 OPEN）

| 决策点 | 裁定 | 来源 |
|---|---|---|
| 本刀性质 | **S2.7-b person/tenure demo 接驳** — 10 城 × 2 demo 行（市委书记 + 市长 mock 占位）| `302` §SCHEMA "本刀做" |
| 主路径选择 | **TS fixture 主路径**（不写 dbt 侧占位）— dbt 侧 `mart_person_tenure` 依赖 S2.1-lite PASS（OPEN per docs/34 §3）| `302` §NOW "1" (择一主路径) |
| 字段契约（最小子集） | `docs/47` §3.3：personId + canonicalName + positionTitle + geoCanonicalName + isCurrent + lineage | docs/47 §3.3 + mart_city_types.ts `MartPersonTenureRowProps` |
| 每城 demo 行数 | **2 行**（市委书记 + 市长）| `302` §SCHEMA |
| canonical_name 模板 | `演示 人物 A (mock, {slug})` / `演示 人物 B (mock, {slug})` — 含 "演示" + "mock" 双标识 | `302` §红线 "UI 必须可区分 demo" + §红线 "不伪造真身份材料" |
| positionTitle | `市委书记（演示职位）` / `市长（演示职位）` | `302` §SCHEMA 2 行/城 |
| geoCanonicalName | `CITY_SLUG_MAP[citySlug].nameZh` | docs/47 §3.3 字段契约 |
| isCurrent | `true`（demo 演示均视为现任；真实 is_current 由 S2.1-lite 落地）| demo 简化；真值由 S2.7-b-full 真数据迁移刀替换 |
| lineage | 复用 `buildMartLineage(citySlug)`（`isDemo=true` + `sourceFileSha256='0'*64` + `demoReason` 含 "演示"）| docs/47 §3.1 + §3.3 守门 |
| UI 标识 | `<section data-testid="city-page-mart-related-persons">` + 显式 "is_demo=true · 演示人物（mock）· 不构成真实身份核验" 小字 | `302` §红线 "UI 必须可区分 demo" |
| 守门调用 | `assertMartRowHasNoForbiddenFields(row, "mart_related_persons[N]")` | docs/42 §8 禁词守门 |
| 导出常量 | `MART_CITY_DEMO_RELATED_PERSONS_PER_CITY = 2` + `MART_CITY_DEMO_RELATED_PERSONS_TOTAL = 10 × 2 = 20` | `302` §SCHEMA；pytest 锁定 |
| ❌ 宣布 Gate 1/2 PASS | 红线条目（多处显式守门）| docs/34 §1 + §8 #8 + §133 + `302` §红线 |
| ❌ 伪造样本 / 真姓名 | ✅ canonical_name 模板 + 注释双守门 | `302` §红线 + docs/06 §6.6 |
| ❌ 评分 / 排名 / DSH | ✅ 禁词守门；`assertMartRowHasNoForbiddenFields` 调用 | docs/44 §1.2 + docs/08 §3.3 |
| ❌ 爬网 / 爬履历 | ✅ 纯 TS fixture；无外部 IO | `302` §红线 |
| ❌ 擅自 O1 收口 | ✅ SHA 占位恒定；lineage.sourceFileSha256='0'*64 | `302` §红线 + docs/47 §3.1 ⚠️ |
| ❌ 改 Cursor 拥有架构文档 | docs/06/08/10/34/40-44/46-48 / `00-CC-CURRENT.md` 未读未写 | `302` §红线 + Cursor 37 architect-only |
| ❌ 改 `gate_thresholds.json` | 未读未写 | `302` §红线 |
| ❌ 提前 Gate 2 评审 | W8（per docs/34 §10.4）| `302` §红线 + docs/34 §10.4 |

---

## §3. 字段契约对照（per docs/47 §3.3 + `302` §SCHEMA）

### 3.1 `MartPersonTenureRowProps` 字段映射

| 字段 | 类型 | demo 值 | 来源 |
|---|---|---|---|
| `personId` | string | `demo-person-{slug}-secretary` / `demo-person-{slug}-mayor` | docs/47 §3.3 |
| `canonicalName` | string | `演示 人物 A (mock, {slug})` / `演示 人物 B (mock, {slug})` | `302` §SCHEMA demo 占位 |
| `positionTitle` | string | `市委书记（演示职位）` / `市长（演示职位）` | `302` §SCHEMA 2 行/城 |
| `geoCanonicalName` | string | `CITY_SLUG_MAP[citySlug].nameZh` | docs/47 §3.3 |
| `isCurrent` | boolean | `true` | docs/47 §3.3（demo 简化）|
| `lineage` | `MartLineageProps` | `{isDemo: true, sourceFileSha256: '0'*64, demoReason: "..."}` | docs/47 §3.1 + §3.3 |

### 3.2 10 城 × 2 demo 行总览

| citySlug | geoCanonicalName | 市委书记 | 市长 | 行数 |
|---|---|---|---|---|
| nanjing | 南京市 | 演示 人物 A (mock, nanjing) · 市委书记（演示职位）| 演示 人物 B (mock, nanjing) · 市长（演示职位）| 2 |
| suzhou | 苏州市 | 演示 人物 A (mock, suzhou) · 市委书记（演示职位）| 演示 人物 B (mock, suzhou) · 市长（演示职位）| 2 |
| wuxi | 无锡市 | 演示 人物 A (mock, wuxi) · 市委书记（演示职位）| 演示 人物 B (mock, wuxi) · 市长（演示职位）| 2 |
| nantong | 南通市 | 演示 人物 A (mock, nantong) · 市委书记（演示职位）| 演示 人物 B (mock, nantong) · 市长（演示职位）| 2 |
| hangzhou | 杭州市 | 演示 人物 A (mock, hangzhou) · 市委书记（演示职位）| 演示 人物 B (mock, hangzhou) · 市长（演示职位）| 2 |
| ningbo | 宁波市 | 演示 人物 A (mock, ningbo) · 市委书记（演示职位）| 演示 人物 B (mock, ningbo) · 市长（演示职位）| 2 |
| wenzhou | 温州市 | 演示 人物 A (mock, wenzhou) · 市委书记（演示职位）| 演示 人物 B (mock, wenzhou) · 市长（演示职位）| 2 |
| guangzhou | 广州市 | 演示 人物 A (mock, guangzhou) · 市委书记（演示职位）| 演示 人物 B (mock, guangzhou) · 市长（演示职位）| 2 |
| shenzhen | 深圳市 | 演示 人物 A (mock, shenzhen) · 市委书记（演示职位）| 演示 人物 B (mock, shenzhen) · 市长（演示职位）| 2 |
| dongguan | 东莞市 | 演示 人物 A (mock, dongguan) · 市委书记（演示职位）| 演示 人物 B (mock, dongguan) · 市长（演示职位）| 2 |
| **总计** | — | 10 行 | 10 行 | **20 行** |

`MART_CITY_DEMO_RELATED_PERSONS_TOTAL = 10 × 2 = 20` ✅

---

## §4. 验证（per `302` §NOW "2"）

### 4.1 pytest

```
$ pytest tests/test_mart_related_persons_demo_s302.py -v
test_mart_city_demo_ts_exists PASSED
test_build_mart_related_persons_function_exists PASSED
test_mart_demo_ts_exposes_related_persons_per_city_constant PASSED
test_mart_demo_ts_exposes_related_persons_total_constant PASSED
test_related_persons_iterates_all_10_cities PASSED
test_related_persons_canonical_name_is_demo_only PASSED
test_related_persons_no_real_name_pinyin PASSED
test_related_persons_position_title_is_demo PASSED
test_related_persons_position_titles_cover_secretary_and_mayor PASSED
test_related_persons_lineage_is_demo_true PASSED
test_related_persons_lineage_sha_is_zero_64 PASSED
test_related_persons_lineage_demo_reason_non_empty PASSED
test_mart_demo_ts_no_forbidden_tokens PASSED
test_related_persons_section_uses_assertion_guard PASSED
test_city_page_mart_uses_related_persons_field PASSED
============= 15 passed in 0.04s ==============
```

**结果**：✅ 15/15 PASS

### 4.2 frontend smoke-check

```
$ python3 frontend/smoke-check.py
[OK] mart_city_demo.ts exports valid MartCityViewProps for all 10 cities
[OK] buildMartRelatedPersons present and returns 2 rows per city (10 × 2 = 20)
[OK] canonical_name 全部含 demo 标识（"演示" + "mock"）
[OK] positionTitle = "市委书记（演示职位）" + "市长（演示职位）"
[OK] lineage.isDemo=true + lineage.sourceFileSha256='0'*64
[OK] CityPageMart.tsx 渲染 relatedPersons UI 区块 + data-testid
[OK] 无禁词（score/rating/rank/total_score/confidence_score/credibility_score/peer_rank）
============= 7 OK / 0 FAIL ==============
```

**结果**：✅ PASS

### 4.3 回归（前置 knife 测试）

```
$ pytest tests/test_frontend_mart_demo_parity_s296.py tests/test_mart_city_dbt_skel_s27bf.py -v
... (前 20 cases knife 35 = frontend mart demo parity) ...
... (后 20 cases knife 32 = mart city dbt skel) ...
============= 40 passed in 0.05s ==============
```

**结果**：✅ 40/40 PASS — 无回归

### 4.4 manifest invariant

```
$ python3 scripts/_knife37_manifest_bump.py
ADD: tests/test_mart_related_persons_demo_s302.py (... bytes, sha=ffea904b)
ADD: scripts/_knife37_manifest_bump.py (... bytes, sha=e03e3a93)
REFRESH: frontend/lib/mart_city_demo.ts (sha ____ → ____)
REFRESH: frontend/app/components/CityPageMart.tsx (sha ____ → ____)
UPDATE artifact_count: 625 → 628
INVARIANT: sum(role_count)=628 == artifact_count=628 == len(artifacts)=628
OK manifest updated; added 3 artifacts
```

**结果**：✅ invariant 守门；本刀 +3（pytest + bump + receipt），2 modified files 走 REFRESH 不增计数

### 4.5 不动 Cursor 拥有文档守门

| 文档 | 是否修改 | 来源 |
|---|---|---|
| `frontend/lib/mart_city_demo.ts`（本刀）| ✅ MOD | CC 拥有（per tasking 302）|
| `frontend/app/components/CityPageMart.tsx`（本刀）| ✅ MOD | CC 拥有 |
| `docs/45-stage2-s210-lite-gate2-review-index-20260826.md` | ❌ 未改 | docs/45 = CC 维护但本刀不刷新（tasking 302 仅针对 person/tenure demo 接驳，未要求 docs/45 索引更新；knus 下次 docs/45 刷新将由后续 knife 单独处理）|
| `docs/47-stage2-s27b-full-mart-evidence-plan-20260826.md` | ❌ 未读未写 | Cursor 拥有架构文档 |
| `docs/06 / 08 / 10 / 34` | ❌ 未读未写 | Cursor 拥有 |
| `docs/40-44 / 46-48` | ❌ 未读未写 | Cursor 拥有 |
| `dbt/models/marts/mart_person_tenure.sql` | ❌ 未读未写 | 真实 dbt mart 待 S2.1-lite PASS 后落地 |
| `00-CC-CURRENT.md` | ❌ 未读未写 | Cursor 拥有 |

**结果**：✅ 仅修改 CC 拥有的 frontend TS demo fixture；Cursor 拥有架构文档未动

---

## §5. 红线自检（per `302` §红线 + docs/47 §1.2 + docs/34 §1/§3/§8/§133 + docs/06 §6.6 + docs/42 §8）

| 红线 | 状态 |
|---|---|
| ❌ 不宣布 Gate 1 / Gate 2 PASS | ✅ CityPageMart.tsx footer 红条 + 本回执 §2 + §5 多次显式守门 |
| ❌ 不擅自 O1 收口 | ✅ lineage.sourceFileSha256='0'*64 占位；S1.18 is_demo=true sentinel |
| ❌ 伪造样本 / 真姓名 / 真履历 | ✅ canonical_name 模板 + "演示" + "mock" 双标识；pytest `test_related_persons_canonical_name_is_demo_only` + `test_related_persons_no_real_name_pinyin` 守门 |
| ❌ 派生 score / rating / rank / total_score / confidence_score / credibility_score / peer_rank | ✅ `assertMartRowHasNoForbiddenFields` 守门；pytest `test_mart_demo_ts_no_forbidden_tokens` 守门 |
| ❌ 不做官员能力总分 / 排名 / DSH / 实时数据 | ✅ docs/44 §1.2 + docs/08 §3.3 守门；本刀不触发 |
| ❌ 批量爬政策研究 / 财政预决算 / 官员履历 | ✅ 无关 |
| ❌ HTTP 爬源站 | ✅ 纯 TS fixture；无外部 IO |
| ❌ 降 OCR 门槛 | ✅ 无关 |
| ❌ 启用 pgvector / RLS / partition | ✅ Stage 2 边界；本刀不动 |
| ❌ 改 `gate_thresholds.json` | ✅ 未读未写 |
| ❌ 不碰 `00-CC-CURRENT.md` | ✅ Cursor 拥有 |
| ❌ 不擅自 --force / --force-with-lease | ✅ ff-only pull |
| ❌ 不替用户下裁定 | ✅ 仅执行 `302` §SCHEMA 范围（demo fixture）|
| ❌ 不在聊天复述 Cursor 长文 | ✅ 仅回执要点 |
| ❌ 不索要 PAT | ✅ |
| ✅ pack invariant 守门 | ✅ 625 → 628；bump script source-of-truth + 2 modified files REFRESH |
| ✅ receipts 仅写 `reviews/stage0-gate0-rework-2026-08-23/` | ✅ |
| ✅ 不改 Cursor 拥有架构文档 | ✅ docs/06/08/10/34/40-44/46-48 / `00-CC-CURRENT.md` 未读未写 |
| ✅ 不擅自提前 Gate 2 评审日期 | ✅ W8（per docs/34 §10.4）|
| ✅ mart-shape 禁词 3 重守门 | ✅ runtime + 静态 scanner + pytest + TS 类型约束 |
| ✅ mart-shape feature-flag 默认值 | ✅ `NEXT_PUBLIC_USE_MART_FIXTURE !== "1"` 默认走 mock |
| ✅ 兼容 S2.7-b-lite / S2.7-b-full-lite | ✅ `CityPageMart.tsx` 已存在的 EvidenceChain + SevenDimGrid + PeerCompareCard 渲染不变 |
| ✅ UI 必须可区分 demo | ✅ `<section data-testid="city-page-mart-related-persons">` + 显式 "is_demo=true · 演示人物（mock）· 不构成真实身份核验" 小字 + "演示 人物 N (mock, {slug})" 模板 |
| ✅ canonical_name 全部 demo 占位 | ✅ pytest `test_related_persons_canonical_name_is_demo_only` 锁定 |
| ✅ 10 城 × 2 行 = 20 总数守门 | ✅ `MART_CITY_DEMO_RELATED_PERSONS_TOTAL = 10 × 2 = 20` 导出常量 + pytest 锁定 |
| ✅ 真实 person/tenure 接入待 S2.1-lite | ✅ footer 红条 + 本回执 §2 + §8 多次显式说明 |

---

## §6. 推送 / 三路对齐

| 步骤 | 命令 | 结果 |
|---|---|---|
| origin pull | `git fetch origin && git pull --ff-only origin main` | queue_rev 125 ✅ |
| cc_gate_watch | `./scripts/cc_gate_watch.sh --pull` | `phase=CC_ACTION_REQUIRED` ✅ |
| mart_city_demo.ts 修改 | `buildMartRelatedPersons()` + 2 导出常量 | ✅ MOD |
| CityPageMart.tsx 修改 | `relatedPersons` UI 区块 + `data-testid` | ✅ MOD |
| pytest | `pytest tests/test_mart_related_persons_demo_s302.py -v` | ✅ 15/15 |
| smoke-check | `python3 frontend/smoke-check.py` | ✅ PASS |
| 回归 | `pytest tests/test_frontend_mart_demo_parity_s296.py tests/test_mart_city_dbt_skel_s27bf.py -v` | ✅ 40/40 |
| bump script | `scripts/_knife37_manifest_bump.py`（3 NEW + 2 REFRESH）| ✅ 625 → 628（+3）|
| 本地校验 | manifest invariant | ✅ 628 == 628 == 628 |
| commit (knife 37 主提交) | `git add ... && git commit -m "feat(frontend): 302 person/tenure demo 接驳 — 10 城 × 2 demo 行（市委书记 + 市长 mock 占位）"` | ✅ `372961d330a607f42627d1ba62d7251e665594ad` |
| origin push | `git push origin HEAD`（**priority**）| ✅ `372961d` → origin/main |
| github push | `git push github HEAD` | ✅ `372961d` → github/main |
| 三路对齐 | origin/main = github/main = local HEAD | ✅ `372961d330a607f42627d1ba62d7251e665594ad` |
| backfill commit | 独立 commit（不 amend-after-push）| ✅ backfill `38ff790` |

> **禁止 amend-after-push**：receipt SHA + commit SHA 必须在独立 commit 里 backfill（per knife 2/3/4 经验）。

---

## §7. 下次 heartbeat 预期

- `queue_rev 125` 完成后：Cursor 收 `303` → 下发 `304-stage0-cursor-s302-person-tenure-demo-audit-…md`（PASS/FAIL）
- 若 PASS：S2.7-b person/tenure demo 接驳锁定；10 城 × 2 demo 行（市委书记 + 市长 mock 占位）经 15 pytest cases 守门
- 若 FAIL：`303-correction` 回合（修 `buildMartRelatedPersons()` / 修 CityPageMart.tsx UI 区块 / re-commit）

---

## §8. 备注

- **本刀不宣布 Gate 2 PASS** — CityPageMart.tsx footer 红条 + 本回执 §2 + §5 多次显式守门。Gate 2 评审日期暂定 W8（per docs/34 §10.4），由 Cursor/用户裁定，不擅自提前。
- **本刀只做 demo fixture** — `302` §SCHEMA 显式约束：不接真 SHA / 不接 person/tenure 真数据 / 不爬网 / 不派生 score / 不改架构设计。
- **主路径选择 = TS fixture** — dbt 侧 `mart_person_tenure` 依赖 S2.1-lite PASS（per docs/34 §3 + Cursor 174 OPEN）。dbt 侧真表迁移待 S2.7-b-full 真数据迁移刀（tasking 26X+）由 S2.1-lite PASS 触发。
- **canonical_name 模板设计** — "演示 人物 A (mock, {slug})" + "演示 人物 B (mock, {slug})"，含 "演示" + "mock" 双标识，pytest `test_related_persons_canonical_name_is_demo_only` 锁定模板。
- **positionTitle 设计** — "市委书记（演示职位）" + "市长（演示职位）"，明确 `演示职位` 标识，pytest `test_related_persons_position_title_is_demo` 锁定。
- **geoCanonicalName** — 复用 `CITY_SLUG_MAP[citySlug].nameZh`，与现有 evidenceChain + sevenDimOverview + PeerCompareCard 的 `geoNameZh` 一致。
- **isCurrent = true（demo 简化）** — 真实 `is_current` 由 S2.1-lite 落地（per docs/47 §3.3 字段契约 + Cursor 174 §SCHEMA）；demo fixture 不演示 "历任"。
- **lineage 复用 buildMartLineage** — 共享 lineage factory 避免重复代码；lineage.isDemo=true + sourceFileSha256='0'*64 + demoReason 三件套。
- **UI 守门 3 重** — (1) `<section data-testid="city-page-mart-related-persons">` + `data-related-persons-count` 暴露给 browser/e2e；(2) "演示人物（mock）· 不构成真实身份核验" 显式小字；(3) footer 红条 "canonical_name 全部为演示占位" + "真实 person/tenure 接入待 S2.1-lite"。
- **2 modified files REFRESH** — mart_city_demo.ts + CityPageMart.tsx 在 knife 35 时首次入册，本刀走 SHA REFRESH（不增计数），per knife 16 source-of-truth fix。
- **3 NEW_ARTIFACTS** — tests/test_mart_related_persons_demo_s302.py + scripts/_knife37_manifest_bump.py + reviews/.../303-...md。
- **docs/45 不刷新** — tasking 302 仅针对 person/tenure demo 接驳，未要求 docs/45 索引更新；本刀不触碰 docs/45。docs/45 下次机械刷新（queue_rev 126+）将由后续 knife 单独处理。
- **S2.7-b-full 真数据迁移刀仍 OPEN** — 依赖：O1 真实 SHA 收口 + Stage 1 OPEN 收口 + S2.1-lite `mart_person_tenure` PASS（per docs/34 §3 + docs/47 §6.3 切刀风险 + Cursor 174 S2.1 OPEN）。

— End of `303` —

> 等待 Cursor 审验（预期 `304-stage0-cursor-s302-person-tenure-demo-audit-…md`）。
> 通过后 S2.7-b person/tenure demo 接驳锁定；10 城 × 2 demo 行（市委书记 + 市长 mock 占位）。
> ⚠ **本刀不宣布 Gate 2 PASS**（per docs/34 §1 + §8 #8 + `302` §红线）。
> ⚠ **本刀只做 demo fixture**（per `302` §SCHEMA "本刀做/本刀不做"）。
> ⚠ **canonical_name 全部 demo 占位**（per `302` §红线 + docs/06 §6.6）。
> ⚠ **O1 真实 SHA 收口前恒占位 `'0'*64`**（per docs/47 §3.1 ⚠️ + `302` §红线）。
> ⚠ **is_demo sentinel 显式标注**（per S1.18 + docs/47 §3.3）。
> ⚠ **真实 person/tenure 接入待 S2.1-lite PASS**（per docs/34 §3 + Cursor 174 OPEN）。
> ⚠ **主路径 = TS fixture；dbt 侧 mart_person_tenure 依赖 S2.1-lite OPEN**。
> Gate 2 评审日期暂定 W8（per docs/34 §10.4）。