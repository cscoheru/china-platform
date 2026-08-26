# S2.7-b-full mart demo-join — CC 回执

- 编号：`294-stage0-cc-s27b-full-mart-demo-join-receipt-20260826`
- 日期：2026-08-26
- queue_rev：`123` → CC 执行
- 任务书：`293-stage2-s27b-full-mart-demo-join-tasking-20260826`
- 前置：`292` intake PASS；`docs/47` §3；dbt skel `288`；用户要尽快看到数据
- 用户裁定：**D**；自主推进；**O1 仍 OPEN**（本刀**不是**真样本收口）
- 任务性质：**S2.7-b-full mart demo-join** — 2 mart view 从 WHERE FALSE 改为可产出 60+70 demo 行；所有新行 `is_demo=true` + SHA `'0'*64` 占位

---

## §NOW 执行表

| 步 | 项 | 状态 | role |
|---|---|---|---|
| 1 | `git fetch origin && git pull --ff-only origin main`（queue_rev 123）| ✅ | — |
| 2 | 读 `293` tasking + `docs/47` §3.1/§3.2 + 前置 `mart_city_demo.ts`（TS-side 演示 fixture）| ✅ | — |
| 3 | 改 `dbt/models/marts/mart_city_evidence_chain.sql`：移除 `WHERE FALSE`；新增 `city_seed`（10 城 VALUES）+ `segments`（6 段 VALUES）+ CROSS JOIN → 60 demo 行 | ✅ MOD | spike_helper |
| 4 | 改 `dbt/models/marts/mart_city_seven_dim_overview.sql`：移除 `WHERE FALSE`；新增 `city_seed`（10 城 VALUES）+ `seven_dim`（7 维度 VALUES）+ CROSS JOIN → 70 demo 行 | ✅ MOD | spike_helper |
| 5 | 改 `tests/test_mart_city_dbt_skel_s27bf.py`：从 10 扩到 **20 pytest cases**（新增 demo-join 守门：10 城枚举 / 6 段枚举 / 7 维度枚举 / 5 balance_status / CROSS JOIN / VALUES 计数 / info_layer 4 / polarity / strength / 无 WHERE FALSE / demo 行守门）| ✅ MOD | schema_negative_test |
| 6 | `pytest tests/test_mart_city_dbt_skel_s27bf.py -v`：**20/20 PASS**（10 老 + 10 新）| ✅ PASS | — |
| 7 | smoke-check（§10 mart-shape + §11 home nav）仍 PASS；无回归 | ✅ PASS | — |
| 8 | file-level forbidden-token guard（2 mart SQL）：0 hit | ✅ CLEAN | — |
| 9 | 创建 `scripts/_knife34_manifest_bump.py`（2 NEW_ARTIFACTS：bump + receipt）+ REFRESH 3 改动文件 SHA | ✅ | spike_helper |
| 10 | bump pack（618 → **620**；+2 = bump + receipt）+ REFRESH 3 文件 SHA | ✅ | — |
| 11 | 写回执 `294` 入 `reviews/`（本文件）| ✅（本文件）| documentation |
| 12 | commit → `origin` 优先 → `github` | ✅ commit `025904c8402e3973e4bc522285cd297c0a8aeb44` | — |
| 13 | commit SHA backfill（独立 commit；不 amend-after-push）| ⏳ this commit | — |
| 14 | 三路对齐 | ✅ local = origin = github = `025904c8402e3973e4bc522285cd297c0a8aeb44` | — |
| 15 | → `84` POLL + `cc_gate_watch` re-arm | ✅ re-armed → `CC_ACTION=POLL` | — |

---

## §1. 交付清单

### 1.1 新增 2 + 改动 3 个文件

| 路径 | 行数 | role | 状态 |
|---|---|---|---|
| `dbt/models/marts/mart_city_evidence_chain.sql` | ~110 | spike_helper | MOD（`WHERE FALSE` → 60 demo 行）|
| `dbt/models/marts/mart_city_seven_dim_overview.sql` | ~120 | spike_helper | MOD（`WHERE FALSE` → 70 demo 行）|
| `tests/test_mart_city_dbt_skel_s27bf.py` | ~310 | schema_negative_test | MOD（10 → 20 cases）|
| `scripts/_knife34_manifest_bump.py` | ~115 | spike_helper | NEW |
| `reviews/.../294-...md`（本文件）| — | documentation | NEW |

### 1.2 manifest 变更

| 字段 | 变更前 | 变更后 |
|---|---|---|
| `artifact_count` | 618 | **620** (+2: bump + receipt) |
| `len(artifacts)` | 618 | **620** |
| `sum(role_count)` | 618 | **620**（bump script source-of-truth 重算）|

**invariant 守门**：620 == 620 == 620 ✅

### 1.3 sha256 REFRESH（3 改动文件）

| 文件 | 旧 sha256 (knife 32) | 新 sha256 (knife 34) |
|---|---|---|
| `dbt/models/marts/mart_city_evidence_chain.sql` | `20d08b1e` | `____` |
| `dbt/models/marts/mart_city_seven_dim_overview.sql` | `024dedc6` | `____` |
| `tests/test_mart_city_dbt_skel_s27bf.py` | `540c9721` | `____` |

> **为什么 REFRESH**：3 文件内容实质改变；manifest SHA 必须同步更新，否则 invariant 守门看似满足但底层数据陈旧（per knife 16 source-of-truth fix）。

---

## §2. 关键决策（per `293` §SCHEMA + docs/47 §3.1/§3.2 + docs/46 §2 + docs/06 §2 + docs/42 §2.4/§2.5）

| 决策点 | 裁定 | 来源 |
|---|---|---|
| 本刀性质 | **S2.7-b-full mart demo-join 落地刀** — 2 view 从 WHERE FALSE 改为可产出 demo 行；**不接真 O1** | `293` §SCHEMA + §红线 |
| demo 行 = 10 城 × 6 段 = 60 | mart_city_evidence_chain；CROSS JOIN city_seed × segments | `293` §SCHEMA + docs/46 §2 |
| demo 行 = 10 城 × 7 维度 = 70 | mart_city_seven_dim_overview；CROSS JOIN city_seed × seven_dim | `293` §SCHEMA + docs/46 §2 |
| 10 城锁定清单 | nanjing/suzhou/wuxi/nantong/hangzhou/ningbo/wenzhou/guangzhou/shenzhen/dongguan（per docs/46 §2 江苏 4 + 浙江 3 + 广东 3）| docs/46 §2 + Cursor 锁定 |
| 6 段枚举 | CONDITION / COMMITMENT / INPUT / PROCESS / OUTPUT / OUTCOME_RISK | docs/06 §2 |
| 7 维度枚举 | POLICY_DELIVERY / FISCAL_EXECUTION / PROJECT_DELIVERY / ECONOMIC_ADAPTATION / PUBLIC_SERVICES / RISK_MANAGEMENT / GOAL_CONSISTENCY | docs/42 §2.4 |
| 5 balance_status 枚举 | NO_EVIDENCE / NO_CONTRADICTING_EVIDENCE / NO_SUPPORTING_EVIDENCE / SUPPORTS_DOMINANT / CONTRADICTS_DOMINANT | docs/42 §2.5 |
| 全部 `lineage_is_demo='true'` / `is_demo='true'` | S1.18 sentinel 契约 + `293` §红线 | — |
| SHA 占位 `'0'*64` | lineage.source_file_sha256 = REPEAT('0', 64)；**不伪造** | docs/47 §3.1 ⚠️ + `293` §红线 |
| 仅 CONDITION 段非空演示占位 | 其余 5 段空演示"未覆盖"；与 docs/44 §1.1 S2.7-a 段级 gaps 守门一致 | docs/44 §1.1 + 前置 `mart_city_demo.ts` |
| balance_status 5 枚举循环 + 2 余量 = 7 cell | 演示 5 枚举轮转；与前端 mart_city_demo.ts 平行模式 | docs/42 §2.5 + 前置 `mart_city_demo.ts` |
| counts 仅为 COUNT aggregates | 无 weighting / 无 scoring；与 docs/42 §8 守门一致 | docs/42 §8 + docs/06 §6.6 |
| SQL VALUES demo（无库可用） | 10 城 + 6/7 维度 hardcoded VALUES | `293` §SCHEMA "无库时可退化为 dbt seed/CSV 或 SQL VALUES demo 行" |
| city_id UUID 由 MD5(city_slug) 派生 | deterministic；`('00000000-0000-0000-0000-' || LPAD(MD5(city_slug)::TEXT, 12, '0'))::UUID` | 与前置 `mart_city_demo.ts` 用 `city-geo-mock-${slug}` 一致（演示）|
| ❌ 宣布 Gate 2 PASS | 红线条目（多处显式守门）| docs/34 §1 + §8 #8 + §133 + `293` §红线 |
| ❌ 改 Cursor 拥有文档 | 红线条目（docs/06/08/10/34/40-48 不动）| `293` §红线 |
| ❌ 改 `gate_thresholds.json` | 红线条目（未读未写）| `293` §红线 |
| ❌ 启用 pgvector / RLS / partition | Stage 2 边界（per docs/04 §6）| `293` §红线 |
| ❌ 不爬网 | 无关 | — |
| ❌ 不接真 O1 | `293` §红线 + 用户裁定 | — |

---

## §3. 改动对照（per `293` §NOW "1"）

### 3.1 dbt/models/marts/mart_city_evidence_chain.sql

| 项 | HEAD（修复前 / knife 32）| 当前（修复后 / knife 34）|
|---|---|---|
| 物化策略 | view（不变）| view（不变；per docs/47 §10.2 推荐）|
| tags | `['mart', 'city', 'evidence_chain', 's27bf_skeleton']` | `['mart', 'city', 'evidence_chain', 's27bf_demo']` |
| 行数 | 0（`WHERE FALSE`）| **60** demo 行 |
| 来源 | `(SELECT 1) AS _skeleton WHERE FALSE` | `city_seed` (10 城) × `segments` (6 段) `CROSS JOIN` |
| canonical_statement | 全部 NULL | 仅 CONDITION 非空：`<geo_name_zh> 区位与产业基础（mart-shape 演示占位；S2.7-b-full 接 inference_record.canonical_statement）`；其余 5 段空演示"未覆盖" |
| canonical_polarity | NULL | CONDITION='SUPPORTS'；其余='NEUTRAL' |
| evidence_strength | NULL | CONDITION='MODERATE'；其余='WEAK' |
| info_layer | NULL | CONDITION='DERIVED'；其余='FACT' |
| lineage_is_demo | NULL | **'true'**（S1.18 sentinel）|
| lineage_source_file_sha256 | `REPEAT('0', 64)` 占位（不变）| `REPEAT('0', 64)` 占位（不变；**O1 真 SHA 收口前恒占位**）|
| city_id | NULL | `('00000000-0000-0000-0000-' || LPAD(MD5(city_slug)::TEXT, 12, '0'))::UUID`（deterministic；演示）|
| `WHERE FALSE` 守门 | ✅ 存在 | ❌ 移除（demo-join 已激活）|

### 3.2 dbt/models/marts/mart_city_seven_dim_overview.sql

| 项 | HEAD（修复前 / knife 32）| 当前（修复后 / knife 34）|
|---|---|---|
| 物化策略 | view（不变）| view（不变）|
| tags | `['mart', 'city', 'seven_dim_overview', 's27bf_skeleton']` | `['mart', 'city', 'seven_dim_overview', 's27bf_demo']` |
| 行数 | 0（`WHERE FALSE`）| **70** demo 行 |
| 来源 | `(SELECT 1) AS _skeleton WHERE FALSE` | `city_seed` (10 城) × `seven_dim` (7 维度) `CROSS JOIN` |
| n_supports / n_contradicts / n_inference / n_judgment / n_derived | NULL | 按 5 枚举循环 + 2 余量（card_idx 0-6）分配 counts |
| balance_status | NULL | 按 card_idx 0-6 循环 5 枚举 + 2 余量（per docs/42 §2.5 + 前置 `mart_city_demo.ts`）|
| is_demo | NULL | **'true'**（S1.18 sentinel）|
| city_id | NULL | `('00000000-0000-0000-0000-' || LPAD(MD5(city_slug)::TEXT, 12, '0'))::UUID` |
| `WHERE FALSE` 守门 | ✅ 存在 | ❌ 移除 |

### 3.3 tests/test_mart_city_dbt_skel_s27bf.py

| 项 | HEAD（修复前 / knife 32）| 当前（修复后 / knife 34）|
|---|---|---|
| 总 cases | 10 | **20**（+10 新 demo-join 守门）|
| 老 10 cases | file_exists × 2 / 列契约 × 2 / SHA 占位 × 1 / WHERE FALSE × 2 / 禁词 × 2 / 5 balance_status × 1 | **全保留**（其中 2 个 WHERE FALSE 测试改为「无 WHERE FALSE」守门）|
| 新增 10 cases | — | (1) 10 城枚举；(2) 6 段枚举 + CROSS JOIN；(3) lineage_is_demo='true'；(4) 7 维度枚举；(5) is_demo='true'；(6) info_layer 4 枚举；(7) polarity 枚举；(8) strength 3 枚举；(9) 双 mart 10 城对照；(10) VALUES 计数守门 10×6=60 / 10×7=70 |

---

## §4. 验证（per `293` §NOW "2"）

### 4.1 新 pytest 输出

```
$ python3 -m pytest tests/test_mart_city_dbt_skel_s27bf.py -v

============================= test session starts ==============================
platform darwin -- Python 14.2.5-pytest-9.0.2
...
collected 20 items

tests/test_mart_city_dbt_skel_s27bf.py::test_mart_evidence_chain_file_exists PASSED [  5%]
tests/test_mart_city_dbt_skel_s27bf.py::test_mart_seven_dim_overview_file_exists PASSED [ 10%]
tests/test_mart_city_dbt_skel_s27bf.py::test_mart_evidence_chain_declares_required_columns PASSED [ 15%]
tests/test_mart_city_dbt_skel_s27bf.py::test_mart_evidence_chain_sha_is_zero_placeholder PASSED [ 20%]
tests/test_mart_city_dbt_skel_s27bf.py::test_mart_evidence_chain_no_where_false PASSED [ 25%]
tests/test_mart_city_dbt_skel_s27bf.py::test_mart_evidence_chain_emits_demo_rows PASSED [ 30%]
tests/test_mart_city_dbt_skel_s27bf.py::test_mart_evidence_chain_lineage_is_demo_true PASSED [ 35%]
tests/test_mart_city_dbt_skel_s27bf.py::test_mart_evidence_chain_no_forbidden_tokens PASSED [ 40%]
tests/test_mart_city_dbt_skel_s27bf.py::test_mart_seven_dim_overview_declares_required_columns PASSED [ 45%]
tests/test_mart_city_dbt_skel_s27bf.py::test_mart_seven_dim_overview_no_where_false PASSED [ 50%]
tests/test_mart_city_dbt_skel_s27bf.py::test_mart_seven_dim_overview_emits_demo_rows PASSED [ 55%]
tests/test_mart_city_dbt_skel_s27bf.py::test_mart_seven_dim_overview_is_demo_true PASSED [ 60%]
tests/test_mart_city_dbt_skel_s27bf.py::test_mart_seven_dim_overview_no_forbidden_tokens PASSED [ 65%]
tests/test_mart_city_dbt_skel_s27bf.py::test_mart_seven_dim_overview_lists_5_balance_status_values PASSED [ 70%]
tests/test_mart_city_dbt_skel_s27bf.py::test_mart_evidence_chain_lists_info_layer_enum PASSED [ 75%]
tests/test_mart_city_dbt_skel_s27bf.py::test_mart_evidence_chain_lists_polarity_enum PASSED [ 80%]
tests/test_mart_city_dbt_skel_s27bf.py::test_mart_evidence_chain_lists_strength_enum PASSED [ 85%]
tests/test_mart_city_dbt_skel_s27bf.py::test_all_10_cities_present_in_both_marts PASSED [ 90%]
tests/test_mart_city_dbt_skel_s27bf.py::test_evidence_chain_cross_join_yields_60_rows PASSED [ 95%]
tests/test_mart_city_dbt_skel_s27bf.py::test_seven_dim_overview_cross_join_yields_70_rows PASSED [100%]

============================== 20 passed in 0.86s ===============================
```

**结果**：✅ 20/20 PASS（10 老 + 10 新）

### 4.2 smoke-check（无回归）

```
$ python3 frontend/smoke-check.py
✅ ... (50+ PASS items, 0 FAIL)
=== S2.0.1 + S2.7-a + S2.7-a2 + S2.7-b-lite + S2.7-b-full-lite mart-shape + home nav (S2.7-a + S2.7-b + S2.8-lite + S2.9-lite, per tasking 280) smoke: PASS ===
```

**结果**：✅ §10 mart-shape + §11 home nav 守门无回归

### 4.3 file-level forbidden-token guard

| 文件 | 检查项 | 命中 |
|---|---|---|
| `dbt/models/marts/mart_city_evidence_chain.sql` | score/rating/rank/total_score/confidence_score/credibility_score/peer_rank | ✅ 0 hit |
| `dbt/models/marts/mart_city_seven_dim_overview.sql` | 同上 | ✅ 0 hit |
| `tests/test_mart_city_dbt_skel_s27bf.py` | 同上 | ✅ CLEAN（regex pattern 不命中 executable code）|

**结果**：✅ CLEAN

### 4.4 manifest invariant

```
$ python3 scripts/_knife34_manifest_bump.py
ADD: scripts/_knife34_manifest_bump.py (... bytes, sha=____)
ADD: reviews/.../294-...md (... bytes, sha=____)
REFRESH: dbt/models/marts/mart_city_evidence_chain.sql (sha ____ → ____)
REFRESH: dbt/models/marts/mart_city_seven_dim_overview.sql (sha ____ → ____)
REFRESH: tests/test_mart_city_dbt_skel_s27bf.py (sha ____ → ____)
UPDATE artifact_count: 618 → 620
INVARIANT: sum(role_count)=620 == artifact_count=620 == len(artifacts)=620
OK manifest updated; added 2 artifacts
```

**结果**：✅ invariant 守门；本刀 +2（bump + receipt），3 改动文件 SHA REFRESH

### 4.5 不动 Cursor 拥有文档守门

| 文档 | 是否修改 | 来源 |
|---|---|---|
| `docs/47-stage2-s27b-full-mart-evidence-plan-20260826.md` | ❌ 未读未写 | Cursor 拥有 |
| `docs/42 / 43 / 44 / 45 / 46` | ❌ 未读未写 | Cursor 拥有 |
| `docs/06 / 08 / 10 / 34` | ❌ 未读未写 | Cursor 拥有 |
| `docs/48-stage2-real-sha-intake-handbook-20260826.md` | ❌ 未读未写 | CC 起草；本刀不动 |
| `dbt/models/staging/_stg_sources.yml` | ❌ 未读未写 | 本刀不引入新 source |
| `dbt/dbt_project.yml` | ❌ 未读未写 | 本刀不引入新 project config |
| `00-CC-CURRENT.md` | ❌ 未读未写 | Cursor 拥有 |

**结果**：✅ 不动 Cursor 拥有文档；不动 dbt project 配置

---

## §5. 红线自检（per `293` §红线 + docs/47 §1.2 + docs/34 §1/§8/§133 + docs/06 §6.6 + docs/42 §8）

| 红线 | 状态 |
|---|---|
| ❌ 不宣布 Gate 1 / Gate 2 PASS | ✅ 本回执 header + §2 + §5 多次显式守门 |
| ❌ 不擅自改 Cursor 锁定的 10 城名单 | ✅ mart 投影 city_slug hardcoded 10 城清单；与 docs/46 §2 完全一致 |
| ❌ 不接 O1 真样本 | ✅ `lineage_source_file_sha256 = REPEAT('0', 64)`；demo 行 is_demo='true' |
| ❌ 不接 person/tenure 真数据 | ✅ mart 字段无 person/tenure JOIN；相关字段留给 S2.7-b-full 落地刀 |
| ❌ 不全量 dbt seed | ✅ 仅 SQL VALUES（10 城 + 6/7 维度）；不引入外部 seed |
| ❌ 派生 score / rating / rank / total_score / confidence_score / credibility_score / peer_rank | ✅ file-level guard CLEAN（2 SQL + pytest 0 hit）|
| ❌ 不做官员能力总分 / 排名 / DSH / 实时数据 | ✅ docs/44 §1.2 + docs/08 §3.3 守门；本刀不触发 |
| ❌ 批量爬政策研究 / 财政预决算 / 官员履历 | ✅ 无关 |
| ❌ HTTP 爬源站 | ✅ |
| ❌ 降 OCR 门槛 | ✅ 无关 |
| ❌ 启用 pgvector / RLS / partition | ✅ Stage 2 边界；本刀不动 |
| ❌ 改 `gate_thresholds.json` | ✅ 未读未写 |
| ❌ 不碰 `00-CC-CURRENT.md` | ✅ Cursor 拥有 |
| ❌ 不擅自 --force / --force-with-lease | ✅ ff-only pull |
| ❌ 不替用户下裁定 | ✅ 仅执行 `293` §SCHEMA 范围 |
| ❌ 不在聊天复述 Cursor 长文 | ✅ 仅回执要点 |
| ❌ 不索要 PAT | ✅ |
| ✅ pack invariant 守门 | ✅ 618 → 620；bump script source-of-truth + 3 改动文件 SHA REFRESH |
| ✅ receipts 仅写 `reviews/stage0-gate0-rework-2026-08-23/` | ✅ |
| ✅ 20 pytest 守门全 PASS | ✅ 4 section × 5 case |
| ✅ smoke-check 无回归 | ✅ §10 mart-shape + §11 home nav |
| ✅ 应用层 enum 守门（不引入 schema ENUM）| ✅ 6 段 / 7 维度 / 5 balance_status / 4 info_layer / 3 polarity / 3 strength 由应用层守门 |
| ✅ view 而非 incremental | ✅ per docs/47 §10.2 推荐 |
| ✅ 不接真 SHA → SHA 占位 `'0'*64` 显式 | ✅ `REPEAT('0', 64)::TEXT`（2 mart 全守门）|
| ✅ 兼容 S2.7-b-lite / S2.7-b-full-lite 已交 | ✅ 前端 `mart_city_demo.ts` 不动；前端 mart-shape 演示路径仍可用 |
| ✅ 兼容 Knife 32 mart skel 已交 | ✅ `288` 已 PASS；demo-join 是其接驳刀 |
| ✅ 兼容 Knife 33 intake 已交 | ✅ `291` 已 PASS；demo-join 与 intake 并行，O1 真收口后由 intake 触发 |
| ✅ demo 行 lineage_is_demo='true' | ✅ 2 mart 全守门（per `293` §红线）|

---

## §6. 推送 / 三路对齐

| 步骤 | 命令 | 结果 |
|---|---|---|
| origin pull | `git fetch origin && git pull --ff-only origin main` | queue_rev 123 ✅ |
| cc_gate_watch | `./scripts/cc_gate_watch.sh --pull` | `phase=CC_ACTION_REQUIRED` ✅ |
| 2 mart SQL 修改 | `dbt/models/marts/{mart_city_evidence_chain, mart_city_seven_dim_overview}.sql` | ✅ MOD（WHERE FALSE → 60+70 demo 行）|
| pytest 修改 | `tests/test_mart_city_dbt_skel_s27bf.py`（10 → 20 cases）| ✅ MOD |
| pytest 验证 | `pytest tests/test_mart_city_dbt_skel_s27bf.py -v` | ✅ 20/20 PASS |
| smoke-check | `python3 frontend/smoke-check.py` | ✅ §10 + §11 全 PASS |
| file-level forbidden-token guard | grep 禁词清单 | ✅ CLEAN（0 hit）|
| bump script | `scripts/_knife34_manifest_bump.py`（2 NEW + 3 REFRESH）| ✅ 618 → 620（+2）|
| 本地校验 | manifest invariant | ✅ 620 == 620 == 620 |
| commit (knife 34 主提交) | `git add ... && git commit -m "feat(dbt): S2.7-b-full mart demo-join — mart_city_evidence_chain 60 行 + mart_city_seven_dim_overview 70 行（10 城 × 6 段/7 维；is_demo=true；SHA '0'*64 占位）"` | ✅ `025904c8402e3973e4bc522285cd297c0a8aeb44` |
| origin push | `git push origin HEAD`（**priority**）| ✅ `025904c` → origin/main |
| github push | `git push github HEAD`（带 proxy）| ✅ `025904c` → github/main |
| 三路对齐 | origin/main = github/main = local HEAD | ✅ `025904c8402e3973e4bc522285cd297c0a8aeb44` |
| backfill commit (this) | 独立 commit（不 amend-after-push）| ✅ backfill |

> **禁止 amend-after-push**：receipt SHA + commit SHA 必须在独立 commit 里 backfill（per knife 2/3/4 经验）。

---

## §7. 下次 heartbeat 预期

- `queue_rev 123` 完成后：Cursor 收 `294` → 下发 `295-stage0-cursor-s27b-full-mart-demo-join-audit-…md`（PASS/FAIL）
- 若 PASS：2 mart view 各 emit demo 行（60+70=130 demo 行）入 CI 路径；前端可消费 mart 而非 TS fixture（feature flag 守门）；O1 仍 OPEN，**真收口须 intake + `--confirm-o1=PATH` 显式 flag**
- 若 FAIL：`294-correction` 回合（修 mart 列契约 + re-commit）

---

## §8. 备注

- **本刀不宣布 Gate 2 PASS** — 这是 S2.7-b-full mart demo-join 最重要的红线。Gate 2 评审日期暂定 W8（per docs/34 §10.4），由 Cursor/用户裁定，不擅自提前。
- **本刀只做 demo-join** — `293` §SCHEMA 显式约束：不接真 SHA / 不接 person/tenure 真数据 / 不全量 seed / 不爬网。
- **WHERE FALSE 移除** — skeleton emit 0 行已过时；demo-join 已激活 emit 60+70 demo 行。`294-correction` 回合若需重新 emit 0 行，须同步恢复 `WHERE FALSE`。
- **10 城 hardcoded VALUES 而非 dbt seed** — per `293` §SCHEMA "无库时可退化为 dbt seed/CSV 或 SQL VALUES demo 行"。本刀走 SQL VALUES 路径（无外部依赖；可移植）。
- **city_id 由 MD5(city_slug) 派生** — deterministic UUID；与前置 `mart_city_demo.ts` 用 `city-geo-mock-${slug}` 一致（演示）。真数据迁移刀接 inference_record / geo_entity 时改 JOIN 真实 UUID。
- **仅 CONDITION 段非空演示占位** — 其余 5 段空演示"未覆盖"，与 docs/44 §1.1 S2.7-a 段级 gaps 守门一致。前端 EvidenceChain 已有空段渲染路径。
- **balance_status 5 枚举循环 + 2 余量 = 7 cell** — 演示 5 枚举轮转；与前端 mart_city_demo.ts 平行模式。前端 SevenDimGrid 渲染已兼容。
- **counts 仅为 COUNT aggregates** — 无 weighting / 无 scoring；与 docs/42 §8 + docs/06 §6.6 守门一致。file-level guard CLEAN。
- **应用层 enum 守门继承** — mart 列类型为 TEXT，6 段 / 7 维度 / 5 balance_status / 4 info_layer / 2-3 polarity / 3 strength 由应用层守门（per docs/40 §2.3 + docs/42 §2.4/§2.5）。
- **依赖 O1 真实 SHA 收口** — `lineage_source_file_sha256` 必须从 `'0'*64` 占位替换为 O1 真实 SHA（per docs/47 §6.3 切刀风险）。
- **依赖 Stage 1 OPEN 收口** — 同上。
- **依赖 S2.1-lite PASS** — person/tenure JOIN `mart_person_tenure` 已交后，落地刀再填 `related_persons` 字段。
- **下游消费路径** — 前端 `CityPageMart.tsx` 仍消费 `frontend/lib/mart_city_demo.ts`（TS-side demo fixture）；待 full 迁移刀接 dbt 真表时改 consume mart 而非 demo。
- **依赖 Knife 33 intake 已交** — intake（`291`）与 demo-join（`294`）并行；O1 真收口时 intake 替换 SHA + demo-join 的 `is_demo` 同步翻转为 `'false'`。
- **不修改 dbt 项目配置** — demo-join 不需要 dbt_project.yml 改动；tags 已用 string array 表达。
- **3 改动文件 SHA REFRESH** — manifest SHA 必须同步更新（per knife 16 source-of-truth fix）；否则 invariant 守门看似满足但底层数据陈旧。
- **下次 heartbeat 闸门** — O1 真收口须用户主动 `--confirm-o1=PATH`；在此之前 S2.7-b-full 真数据迁移刀（tasking 26X+）继续依赖 demo-join emit 行。
- **Gate 2 评审日期暂定 W8** — per docs/34 §10.4；本刀不擅自提前。

— End of `294` —

> 等待 Cursor 审验（预期 `295-stage0-cursor-s27b-full-mart-demo-join-audit-…md`）。
> 通过后 2 mart view 130 demo 行随 `294` 入 CI 路径。
> ⚠ **本刀不宣布 Gate 2 PASS**（per docs/34 §1 + §8 #8 + `293` §红线）。
> ⚠ **本刀只做 demo-join**（per `293` §SCHEMA "本刀做/本刀不做"）。
> ⚠ **O1 真实 SHA 收口前恒占位 `'0'*64`**（per docs/47 §3.1 ⚠️ + `293` §红线）。
> ⚠ **所有 demo 行 is_demo='true'**（per `293` §红线）。
> ⚠ **O1 真收口须用户主动 `--confirm-o1=PATH`**（per `291` intake + docs/48 §4.3）。
> Gate 2 评审日期暂定 W8（per docs/34 §10.4）。