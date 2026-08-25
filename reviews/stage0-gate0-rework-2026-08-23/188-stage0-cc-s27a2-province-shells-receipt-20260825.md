# 188 — Stage 2 / CC / S2.7-a2 补齐三省省级路由壳 Implementation Receipt

**Tasking**: Cursor `187` §NOW（广东 / 四川 / 山东路由壳 + smoke/pytest 扩展）
**Date**: 2026-08-25
**Branch**: `cursor/s27a2-province-shells-7145`（**非 main** — 见 §6 交付说明）
**Predecessor**: `186` S2.1-lite 审验 PASS；`168`/`170` S2.7-a（江苏满段 + 浙江壳 + 5 省列表）
**User ruling**: `D`（S2.1 缩刀仍有效）；Stage 2 前进承 `C`

---

## §NOW items completed (tasking 187)

| # | Item | Status | Evidence |
|---|------|--------|----------|
| 187-1 | 落地广东 / 四川 / 山东三省页壳 + mock（六段全空） | ✅ | `frontend/app/provinces/{guangdong,sichuan,shandong}/page.tsx`；`frontend/lib/mock_evidence_chain.ts` |
| 187-2 | 扩展 smoke / pytest；既有 S2.7-a 套件仍绿 | ✅ | `frontend/smoke-check.py` PASS；`tests/test_province_shells_s27a2.py` 新增；三套件 **54 passed** |
| 187-3 | commit → origin → 回执 `188` 进 `reviews/` | ✅ | 见 §5 + 本回执 |
| 187-4 | → `84` POLL | ⏳ | 见 §8 |

---

## §1 — 交付清单

### 1.1 新增（4 个文件）

| 文件 | 行 | 角色 |
|------|---|------|
| `frontend/app/provinces/guangdong/page.tsx` | 37 | 省级路由壳 |
| `frontend/app/provinces/sichuan/page.tsx` | 37 | 省级路由壳 |
| `frontend/app/provinces/shandong/page.tsx` | 37 | 省级路由壳 |
| `tests/test_province_shells_s27a2.py` | 176 | `schema_negative_test`（入 pack） |

### 1.2 修改（3 个文件）

| 文件 | 修改内容 |
|------|----------|
| `frontend/lib/mock_evidence_chain.ts` | 新增 `guangdongChain` / `sichuanChain` / `shandongChain`（各六段 `items: []`）；三者注册进 `MOCK_EVIDENCE_CHAIN_BY_PROVINCE` |
| `frontend/smoke-check.py` | 三省页文件必需项；三省 params 门 / `<EvidenceChain />` / 自身 slug 解析检查；段键计数阈值 2 → 5；新增 8e「首页 5 省列表无死链」 |
| `evidence_pack/manifest.json` | artifacts append (+1)；artifact_count 518 → 519；`schema_negative_test` 24 → 25 |

**未新建任何 docs**；未触碰 `00-CC-CURRENT.md`。

---

## §2 — 声明顺序约束（本刀唯一非显然点）

`tests/test_evidence_chain_s27a.py` case 5/6 用 `const jiangsuChain` / `const zhejiangChain`
两个变量声明做**源码切片锚点**，浙江段一路切到文件尾并断言「恰好 6 个空段」。
三省新链若插在锚点之后，浙江切片会数到 24 段 → 既有套件红。

处理：三省链声明放在江苏 / 浙江**之前**，并在源码就地留注释说明该约束；
另加 pytest case 9 (`test_s27a_slice_anchors_still_isolate_jiangsu_and_zhejiang`)
把这条约束固化成断言，防止后续刀（S2.7-b 起）再踩。

**既有 `tests/test_evidence_chain_s27a.py` 一字未改。**

---

## §3 — 测试 / smoke

### 3.1 S2.7-a2 + S2.7-a + S2.0.1 三套件

```
tests/test_province_shells_s27a2.py  (34)
tests/test_evidence_chain_s27a.py    (13, 既有未改)
tests/test_s201_skeleton_smoke.py    ( 7, 既有未改)
54 passed in 0.06s
```

### 3.2 frontend smoke-check

```
$ python3 frontend/smoke-check.py
...
✅ guangdong/page.tsx has no params.* gate
✅ guangdong/page.tsx renders <EvidenceChain />
✅ guangdong/page.tsx resolves its own mock chain
✅ sichuan/page.tsx  … ×3
✅ shandong/page.tsx … ×3
✅ mock_evidence_chain.ts has ≥5 of each of 6 segment keys
✅ province list entry 'jiangsu'   resolves to a real route + mock chain
✅ province list entry 'zhejiang'  resolves to a real route + mock chain
✅ province list entry 'guangdong' resolves to a real route + mock chain
✅ province list entry 'sichuan'   resolves to a real route + mock chain
✅ province list entry 'shandong'  resolves to a real route + mock chain

=== S2.0.1 + S2.7-a + S2.7-a2 skeleton smoke: PASS ===
```

首页 5 省列表 **0 死链**（tasking 187 §SCHEMA 第 4 行验收点）。

### 3.3 全量 `tests/ -q` — 环境受限，**书面 OPEN**

本 VM 无 `psycopg2` / 无 Postgres，15 个 DB 依赖套件 collection error，
另有 13 个 pre-existing FAILED（`test_cleanliness` 2 + `test_url_health_probe_live` 11）。

**已独立验证这 13 红与本刀无关**：`git stash -u` 清空工作区后复跑，
同样 `13 failed, 10 passed, 2 skipped` — 数量与用例名完全一致。

| 项 | 状态 |
|---|---|
| `test_cleanliness::test_data_dir_has_only_gitkeep_or_known_subdirs` | pre-existing（`data/seeds`、`data/seed_archives` 未列入白名单） |
| `test_cleanliness::test_suite_leaves_no_worktree_trace_h2` | pre-existing（子进程 collection rc=2，源于缺 psycopg2） |
| `test_url_health_probe_live` ×11 | pre-existing（缺 psycopg2） |
| 15 × collection ERROR | 环境缺 psycopg2 / Postgres |

本刀纯前端 + 纯文件扫描 pytest，不触 DB 路径。

---

## §4 — Pack invariant

```
artifact_count: 518 → 519 (+1)
role_count:
  schema_negative_test  24 → 25  (+1 tests/test_province_shells_s27a2.py)
invariant: 519 == 519 == 519 ✓
```

JSON 解析守门：
```
artifacts list length = 519
artifact_count       = 519
sum(role_count)      = 519
schema_negative_test = 25
INVARIANT OK
```

前端 `.tsx` 不入 pack — 沿用 S2.7-a 先例（`168`/`170` 亦仅收 `tests/test_evidence_chain_s27a.py`）。

---

## §5 — Push confirmation

见 PR / 分支 `cursor/s27a2-province-shells-7145`（§6）。

---

## §6 — 交付路径偏离（**需 Cursor 知悉**）

本刀由 **Cursor Cloud Agent** 执行，其运行时策略强制「feature 分支 + PR」，
禁止直接推 `main`、禁止自行 merge。因此本刀**未按 `AGENTS.md` 双推 main**，
而是落在 `cursor/s27a2-province-shells-7145` 并开 PR。

**后果**：`origin/main` 上暂时看不到本回执，`84` 双向心跳的对表点不会自动更新。
**需要的动作**：由 Cursor / 用户 merge 该 PR 到 `main`，心跳链路即恢复。

未做任何 `--force`、未 amend、未改写历史。

---

## §7 — 红线审计（per 187 §红线 + docs/34 §7）

| 红线 | 状态 |
|------|------|
| ❌ 不 Gate PASS | ✅ — 本回执未声明任何 Gate PASS |
| ❌ 不做官员评分 / 总分 / 排名 | ✅ — 三省页 pytest case 8 静态扫 `score`/`rating`/`rank`/`total_score`，全无 |
| ❌ 不 DSH | ✅ — 不相关 |
| ❌ 不爬网 | ✅ — 纯 mock，0 次 HTTP |
| ❌ 不改 `gate_thresholds.json` | ✅ — 未触碰 |
| ❌ 不接 S2.1 person 真数据 | ✅ — pytest case 7 断言三省页无 `mart_person_tenure`/`person_tenure`/`appointment_event` 引用；留 S2.7-b |
| ❌ 不扩 S2.1-full | ✅ — 未碰 schema / dbt / seed |
| ❌ 不擅自 `--force` | ✅ |
| ❌ 不替用户下裁定 | ✅ |
| ❌ 不碰 `00-CC-CURRENT.md` | ✅ — Cursor 拥有 |
| ❌ Cursor-owned docs 不写 | ✅ — 仅改 CC 起草文件（frontend/test/manifest/receipt） |
| ✅ 六段缺一不可 | ✅ — 三省各六段，全空并显式「未覆盖」 |
| ✅ 静态段路由不吃 params | ✅ — pytest case 3 ×3 省 |
| ✅ 既有 S2.7-a 套件仍绿 | ✅ — 未改一字，13/13 绿 |
| ✅ pack invariant | ✅ — 519 / 519 / 519 |
| ✅ receipt location | ✅ — `reviews/stage0-gate0-rework-2026-08-23/188-...md` |

---

## §8 — 本刀书面 OPEN

| 项 | 推到 |
|---|---|
| 三省接真实证据（S2.1 person/tenure、policy_document 等） | **S2.7-b** |
| 全量 `tests/ -q` 绿（需 psycopg2 + Postgres） | 环境侧；本刀无法在 Cloud Agent VM 复现 |
| `data/seeds`、`data/seed_archives` 未列入 `test_cleanliness` 白名单 | pre-existing，待单独小刀 |
| 前端 `.tsx` 是否应入 pack | 待 Cursor 裁定（当前沿用 S2.7-a 先例：不入） |
| 本 PR 合入 `main` 以恢复 `84` 心跳 | **Cursor / 用户** |

---

## §9 — Next heartbeat

`84` POLL 待 PR 合入 `main` 后恢复对表（Cloud Agent 运行时无常驻 cron；
本回执一旦落到 `origin/main`，`queue_rev` 即可由 Cursor 推进）。

— CC @ queue_rev 72, S2.7-a2 已交付 —
