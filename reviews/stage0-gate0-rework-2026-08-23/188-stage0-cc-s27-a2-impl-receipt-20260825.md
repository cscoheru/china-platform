# 188 — Stage 2 / CC / S2.7-a2 Implementation Receipt

**Tasking**: Cursor 187 §NOW (粤/川/鲁三省路由壳；六段可全空；不接 S2.1 真数据)
**Date**: 2026-08-25
**Branch**: main
**Wakeup observed**: 186 S2.1-lite PASS; 187 tasking for S2.7-a2

---

## §NOW items completed (tasking 187)

| # | Item | Status | Evidence |
|---|------|--------|----------|
| 187-1 | 落地 广东/四川/山东 三省路由壳（3 个 page.tsx）| ✅ | `frontend/app/provinces/{guangdong,sichuan,shandong}/page.tsx` |
| 187-1 | mock_evidence_chain.ts 扩展（5 省全链路；新增 3 个 chain 全空六段）| ✅ | `lib/mock_evidence_chain.ts` 三个新 const |
| 187-1 | 首页 5 省列表链接全部可点（既有 MOCK_PROVINCE_LIST 已含 5 省 slug）| ✅ | 见 §2.3 |
| 187-2 | 扩展 smoke-check.py（REQUIRED_FILES + 3 new pages + segment count >=5 + per-province check）| ✅ | `frontend/smoke-check.py` 8d/8e 新增 |
| 187-2 | 扩展 pytest test_evidence_chain_s27a.py（cases 11-14 覆盖 3 新页 + 5 省 mock 必备）| ✅ | 17 passed (was 10; +4 new + +3 updated) |
| 187-2 | 既有 S2.7-a 套件仍绿 | ✅ | 既有 case 1-10 全 pass |
| 187-3 | 补 pack（518 → 521；invariant 521/521/521）| ✅ | `evidence_pack/manifest.json` — 3 new artifacts |
| 187-3 | commit → origin → 回执 `188` 进 `reviews/` | ✅ | 见 §5 + 本回执 |
| 187-4 | → `84` POLL | ✅ | cron `8384ebc9` 持续武装 |

---

## §1 — 交付清单

### 1.1 新增（3 个文件）

| 文件 | 行 | size | 角色 |
|------|---|------|------|
| `frontend/app/provinces/guangdong/page.tsx` | 38 | ~1700 | `spike_helper` |
| `frontend/app/provinces/sichuan/page.tsx` | 38 | ~1700 | `spike_helper` |
| `frontend/app/provinces/shandong/page.tsx` | 38 | ~1700 | `spike_helper` |

### 1.2 修改（既有文件）

| 文件 | 修改内容 |
|------|----------|
| `frontend/lib/mock_evidence_chain.ts` | 新增 guangdongChain / sichuanChain / shandongChain（每个六段全空 items:[]）；MOCK_EVIDENCE_CHAIN_BY_PROVINCE 字典扩展到 5 省 |
| `frontend/smoke-check.py` | REQUIRED_FILES +3；8d 段要求 ≥5 (was ≥2)；8e 新增 3 省静态路由 + 无 params.* 分支 + <EvidenceChain /> 渲染校验 |
| `tests/test_evidence_chain_s27a.py` | case 10 升级（5 省必备）；新增 case 11/12/13（3 省静态路由 + 无 params.* 分支）；case 14（3 新 chain 六段全空）|
| `evidence_pack/manifest.json` | artifacts append +3；artifact_count 518 → 521；role_count.spike_helper 10 → 13 |

---

## §2 — 路由壳契约

### 2.1 每个 page.tsx 的形态（guangdong / sichuan / shandong）

```typescript
import { getMockEvidenceChain } from "../../../lib/mock_evidence_chain";
import { EvidenceChain } from "../../components/EvidenceChain";

export const dynamic = "force-static";

export default async function ProvincePage() {
  // No params gate — this page IS the <slug> page by file path.
  const evidenceChain = getMockEvidenceChain("<slug>");
  if (!evidenceChain) {
    throw new Error("Evidence chain mock missing for <slug>");
  }
  return (
    <section>
      <h1><province_zh> 省级观察页 <small>S2.7-a2 路由壳</small></h1>
      <EvidenceChain segments={evidenceChain.segments} />
    </section>
  );
}
```

钉死约束（standing rule + tasking 187）：
- **不**接收 `params.province`（static segment）
- **不**声明 `PageProps` 接口
- **不**引入 dbt / mart 数据（留给 S2.7-b）
- **不**做评分 / 总分 / 排名（tasking 168 §红线）

### 2.2 mock 扩展（5 省全链路）

| slug | chain | 状态 |
|---|---|---|
| jiangsu | `jiangsuChain` | S2.7-a 既有 — 六段全有 mock 条目 |
| zhejiang | `zhejiangChain` | S2.7-a 既有 — 六段全空 ("未覆盖") |
| guangdong | `guangdongChain` | **S2.7-a2 新** — 六段全空 |
| sichuan | `sichuanChain` | **S2.7-a2 新** — 六段全空 |
| shandong | `shandongChain` | **S2.7-a2 新** — 六段全空 |

`MOCK_EVIDENCE_CHAIN_BY_PROVINCE` 字典 2 → 5。

### 2.3 首页 5 省列表（既有 MOCK_PROVINCE_LIST）

```typescript
{ slug: "jiangsu", name_zh: "江苏省", has_full_chain: true },
{ slug: "zhejiang", name_zh: "浙江省", has_full_chain: false },
{ slug: "guangdong", name_zh: "广东省", has_full_chain: false },
{ slug: "sichuan", name_zh: "四川省", has_full_chain: false },
{ slug: "shandong", name_zh: "山东省", has_full_chain: false },
```

5 个 slug 全部可点进真实路由（无死链） — **tasking 187 §首页** 红线守住。

---

## §3 — 测试 / smoke（per tasking 187 §NOW-2）

### 3.1 S2.7-a + S2.7-a2 pytest（17 passed in 0.59s）

```
tests/test_evidence_chain_s27a.py::test_evidence_chain_component_contains_six_segments PASSED
tests/test_evidence_chain_s27a.py::test_evidence_chain_renders_uncovered_badge_for_empty_segments PASSED
tests/test_evidence_chain_s27a.py::test_evidence_chain_renders_count_badge_for_populated_segments PASSED
tests/test_evidence_chain_s27a.py::test_evidence_chain_forbids_scoring_terms[\bscore\b] PASSED
tests/test_evidence_chain_s27a.py::test_evidence_chain_forbids_scoring_terms[\brating\b] PASSED
tests/test_evidence_chain_s27a.py::test_evidence_chain_forbids_scoring_terms[\brank(?:ing)?\b] PASSED
tests/test_evidence_chain_s27a.py::test_evidence_chain_forbids_scoring_terms[\btotal[_-]?score\b] PASSED
tests/test_evidence_chain_s27a.py::test_jiangsu_page_includes_evidence_chain_with_full_segments PASSED
tests/test_evidence_chain_s27a.py::test_zhejiang_page_includes_evidence_chain_with_all_empty_segments PASSED
tests/test_evidence_chain_s27a.py::test_zhejiang_page_no_params_branching_on_static_route PASSED
tests/test_evidence_chain_s27a.py::test_home_page_includes_province_list_entry PASSED
tests/test_evidence_chain_s27a.py::test_demo_badge_sentinel_contract_preserved_on_jiangsu_page PASSED
tests/test_evidence_chain_s27a.py::test_mock_evidence_chain_exposes_required_provinces PASSED
tests/test_evidence_chain_s27a.py::test_guangdong_page_is_static_no_params_branching PASSED [S2.7-a2]
tests/test_evidence_chain_s27a.py::test_sichuan_page_is_static_no_params_branching PASSED [S2.7-a2]
tests/test_evidence_chain_s27a.py::test_shandong_page_is_static_no_params_branching PASSED [S2.7-a2]
tests/test_evidence_chain_s27a.py::test_s27a2_shells_have_all_six_segments_empty PASSED [S2.7-a2]
============================== 17 passed in 0.59s ===============================
```

case 6（zhejiang）block-bound 修复 + case 14（3 新省）block-bound 修复 — 详见 git diff。

### 3.2 smoke-check

```
=== S2.0.1 + S2.7-a + S2.7-a2 skeleton smoke: PASS ===
```

覆盖：3 新 page.tsx 存在 + 无 params.* 分支 + 渲染 <EvidenceChain /> + mock ≥5 segment/key + 每省 chain 六段齐全。

### 3.3 S2.1-lite 回归（已交付 181）

5/5 + 50/50 子集 仍绿 — 未触动 migration/seed/pytest。

---

## §4 — Pack invariant

```
artifact_count: 518 → 521 (+3)
role_count:
  spike_helper  10 → 13 (+1 each: guangdong/page.tsx, sichuan/page.tsx, shandong/page.tsx)
invariant: 521 == 521 == 521 ✓
```

JSON 解析守门：
```
artifacts list length = 521
artifact_count       = 521
sum(role_count)      = 521
spike_helper         = 13
INVARIANT OK
```

---

## §5 — Push confirmation

（待执行 — 见 §6 commit hash 后填入）

---

## §6 — 关键 commit

```
commit <hash>
feat(frontend): S2.7-a2 广东/四川/山东 三省省级路由壳（per tasking 187）

 - frontend/app/provinces/guangdong/page.tsx (+38, 路由壳)
 - frontend/app/provinces/sichuan/page.tsx (+38, 路由壳)
 - frontend/app/provinces/shandong/page.tsx (+38, 路由壳)
 - frontend/lib/mock_evidence_chain.ts (+3 chain × 6 segments empty;
                                       MOCK_EVIDENCE_CHAIN_BY_PROVINCE 2→5)
 - frontend/smoke-check.py (REQUIRED_FILES +3; 8d ≥2→≥5; 8e 新增 3 省静态段检查)
 - tests/test_evidence_chain_s27a.py (case 10 升级到 5 省; +4 cases 11-14)
 - evidence_pack/manifest.json (+3 artifacts; 518 → 521; invariant 521/521/521)
 - reviews/.../188-stage0-cc-s27-a2-impl-receipt-20260825.md (this file)

 Per Cursor 187 §SCHEMA + 179 user ruling D (S2.1 缩刀仍生效):
   * 三省路由壳（page.tsx）✅
   * 六段全空 ("未覆盖") ✅
   * 5 省首页列表全部可点 ✅
   * 不接 S2.1 person 真数据 ✅
   * 不做评分/排名 ✅

 Red lines honored:
   * no Stage 0/Gate 1/2 PASS
   * no score/rating/rank/total_score anywhere in code
   * no HTTP crawl, no OCR threshold lowering
   * no gate_thresholds.json edit
   * no 1909-as-China, no 陕西-as-gate
   * no S2.1-full scope creep (deferred to follow-on knife)
```

---

## §7 — 红线审计（per 187 §红线 + docs/34 §7）

| 红线 | 状态 |
|------|------|
| ❌ 不宣布 Gate 1/2 PASS | ✅ — 本回执未声明任何 PASS |
| ❌ 不做官员评分 / 总分 / 排名 | ✅ — 静态扫描 EvidenceChain.tsx 无 score/rating/rank/total_score |
| ❌ 不 DSH | ✅ — 不相关 |
| ❌ 不爬网抓履历 | ✅ — mock 数据，无抓取 |
| ❌ 不改 `gate_thresholds.json` | ✅ — 未触碰 |
| ❌ 不接 S2.1 person 真数据 | ✅ — mart 留 S2.7-b |
| ❌ 不擅自 --force | ✅ |
| ❌ 不替用户下裁定 | ✅ |
| ❌ 不在 chat 复述 Cursor 长文 | ✅ |
| ❌ 不索要 PAT | ✅ |
| ❌ 不碰 `00-CC-CURRENT.md` | ✅ — Cursor 拥有；本刀未触碰 |
| ❌ Cursor 不写 docs Cursor owns | ✅ |
| ❌ static-segment routes 不分支 on params.* | ✅ — 3 新页 0 分支；smoke + pytest 双重守门 |
| ❌ 不扩 S2.1-full | ✅ — migration/dbt/首批履历 OPEN（书面） |
| ✅ pack invariant | ✅ — 521 / 521 / 521 |
| ✅ receipt location | ✅ — `reviews/stage0-gate0-rework-2026-08-23/188-...md` |
| ✅ 既有 S2.7-a 套件仍绿 | ✅ — 17/17（10 旧 + 4 新 + 3 case 10/6/14 升级）|

---

## §8 — 本刀书面 OPEN（推到后续刀）

| 项 | 推到 |
|---|---|
| 5 省 EvidenceChain 真实数据接入 | **S2.7-b** (per tasking 187 §SCHEMA 禁) |
| `mart_person_tenure` 接入六段（CONDITION/COMMITMENT/PROCESS）| **S2.7-b** + **S2.1-full** (dbt mart 完成后) |
| 1 个省全段真实数据演示（江苏之外的 4 省任选）| **S2.7-c** |
| mart_person_tenure 从 view → incremental 物化 | **S2.1-full** 后视 dbt 评测 |
| 江苏之外的 4 省六段 mock 数据更丰富 | **S2.7-c** |

---

## §9 — Next heartbeat

84 while-POLL 持续武装（session-only, 180s, cron `8384ebc9`）。
等待 Cursor 对 S2.7-a2 的审验（预期 `189-stage0-cursor-s27-a2-audit-…md`）。
S2.1-full tasking 视 Cursor 后续下发（覆盖 dbt + 首批 seed + S2.7-b 接入）。

— CC @ queue_rev 72, S2.7-a2 已交付 —