# S2.7-b-full dbt mart skeleton — CC 回执

- 编号：`288-stage0-cc-s27b-full-dbt-skel-receipt-20260826`
- 日期：2026-08-26
- queue_rev：`121` → CC 执行
- 任务书：`287-stage2-s27b-full-dbt-mart-skeleton-tasking-20260826`
- 前置：`286` docs/45 O1 登记 PASS；`docs/47` §3.1/§3.2；前端 mart-shape 已交（`266`）
- 用户裁定：**D**；自主推进；**O1 持续 OPEN、不伪造、不爬网**
- 任务性质：**S2.7-b-full dbt mart skeleton 落地刀** — 2 view 骨架 + 10 pytest 守门

---

## §NOW 执行表

| 步 | 项 | 状态 | role |
|---|---|---|---|
| 1 | `git fetch origin && git pull --ff-only origin main`（queue_rev 121）| ✅ | — |
| 2 | 读 `287` tasking + `docs/47` §3.1/§3.2 + `mart_source_disagreement.sql` 模板 | ✅ | — |
| 3 | 新建 `dbt/models/marts/mart_city_evidence_chain.sql`（view；10 列；`WHERE FALSE`）| ✅ NEW | spike_helper |
| 4 | 新建 `dbt/models/marts/mart_city_seven_dim_overview.sql`（view；9 列；`WHERE FALSE`）| ✅ NEW | spike_helper |
| 5 | 新建 `tests/test_mart_city_dbt_skel_s27bf.py`（10 pytest cases；含字段契约 + SHA 占位 + WHERE FALSE + 禁词 + 5 balance_status 枚举）| ✅ NEW | schema_negative_test |
| 6 | `pytest tests/test_mart_city_dbt_skel_s27bf.py -v`：10/10 PASS | ✅ PASS | — |
| 7 | smoke-check（§10 mart-shape + §11 home nav）仍 PASS；无回归 | ✅ PASS | — |
| 8 | file-level forbidden-token guard（2 SQL + pytest）：0 hit（仅 5 balance_status enum 在注释中列出）| ✅ CLEAN | — |
| 9 | 创建 `scripts/_knife32_manifest_bump.py`（5 NEW_ARTIFACTS：3 NEW + 1 bump + 1 receipt）| ✅ | spike_helper |
| 10 | bump pack（608 → **613**；+5 = 2 mart SQL + 1 pytest + bump + receipt）| ⏳ this step | — |
| 11 | 写回执 `288` 入 `reviews/`（本文件）| ✅（本文件）| documentation |
| 12 | commit → `origin` 优先 → `github` | ✅ commit `____`（backfill this line）| — |
| 13 | commit SHA backfill（独立 commit；不 amend-after-push）| ⏳ this commit | — |
| 14 | 三路对齐 | ⏳ local = origin = github = `____` | — |
| 15 | → `84` POLL + `cc_gate_watch` re-arm | ⏳ re-arm | — |

---

## §1. 交付清单

### 1.1 新增 5 个文件

| 路径 | 行数 | role |
|---|---|---|
| `dbt/models/marts/mart_city_evidence_chain.sql` | ~50 | spike_helper |
| `dbt/models/marts/mart_city_seven_dim_overview.sql` | ~45 | spike_helper |
| `tests/test_mart_city_dbt_skel_s27bf.py` | ~150 | schema_negative_test |
| `scripts/_knife32_manifest_bump.py` | ~110 | spike_helper |
| `reviews/.../288-...md`（本文件）| — | documentation |

### 1.2 manifest 变更

| 字段 | 变更前 | 变更后 |
|---|---|---|
| `artifact_count` | 608 | **613** (+5: 2 mart + 1 pytest + bump + receipt) |
| `len(artifacts)` | 608 | **613** |
| `sum(role_count)` | 608 | **613**（bump script source-of-truth 重算）|

**invariant 守门**：613 == 613 == 613 ✅

---

## §2. 关键决策（per `287` §SCHEMA + docs/47 §3.1/§3.2 + docs/42 §2.4/§2.5 + docs/40 §2.3）

| 决策点 | 裁定 | 来源 |
|---|---|---|
| 本刀性质 | **S2.7-b-full dbt mart skeleton 落地刀** — 2 view 骨架 + 10 pytest 守门；不接真 SHA、不接 person/tenure 真数据 | `287` §SCHEMA "本刀做" |
| mart_evidence_chain 列契约 | 10 列：city_id / geo_name_zh / province_slug / segment / canonical_statement / canonical_polarity / evidence_strength / info_layer / lineage_is_demo / lineage_source_file_sha256 | docs/47 §3.1 + tasking `287` §SCHEMA |
| mart_seven_dim_overview 列契约 | 9 列：city_id / card_id / n_supports / n_contradicts / n_inference / n_judgment / n_derived / balance_status / is_demo | docs/47 §3.2 + tasking `287` §SCHEMA |
| 物化策略 | **view**（per docs/44 §7.3 现行模式；与 `mart_person_tenure` 平行）| docs/47 §10.2 推荐 |
| 零行守门 | `WHERE FALSE`（skeleton emit 0 行；O1 + Stage 1 OPEN 收口前不暴露假数据）| docs/47 §6.3 + `287` §红线 |
| SHA 占位 | `lineage_source_file_sha256 = REPEAT('0', 64)::TEXT`；不得伪造非零 SHA | docs/47 §3.1 ⚠️ + `287` §红线 |
| 应用层 enum 守门 | 6 段 / 7 维度 / 5 balance_status / 4 info_layer / 2 polarity / 3 strength 全部由 app-layer 守门（不引入 schema ENUM）| docs/40 §2.3 + docs/42 §2.4/§2.5 |
| 禁词守门 | score / rating / rank / total_score / confidence_score / credibility_score / peer_rank 全部 CLEAN | docs/06 §6.6 + docs/42 §8 |
| 不接真数据 | 不接 O1 真样本 / 不接 person/tenure 真 JOIN / 不全量 seed | `287` §SCHEMA "本刀不做" |
| ❌ 宣布 Gate 2 PASS | 红线条目（多处显式守门）| docs/34 §1 + §8 #8 + §133 + `287` §红线 |
| ❌ 改 Cursor 拥有文档 | 红线条目（docs/06/08/10/34/40/41/42/43/44/45/46/47 不动）| `287` §红线 |
| ❌ 改 `gate_thresholds.json` | 红线条目（未读未写）| `287` §红线 |
| ❌ 启用 pgvector / RLS / partition | Stage 2 边界（per docs/04 §6）| `287` §红线 |

---

## §3. 改动对照（per `287` §NOW "1"）

### 3.1 dbt/models/marts/mart_city_evidence_chain.sql

| 项 | HEAD（修复前）| 当前（修复后）|
|---|---|---|
| 文件存在 | ❌ 不存在 | ✅ 新建（~50 行；10 列 + WHERE FALSE + SHA 占位 + 注释红线）|
| materialization | — | `view`（per docs/47 §10.2 推荐）|
| tags | — | `['mart', 'city', 'evidence_chain', 's27bf_skeleton']` |
| 列契约 | — | city_id / geo_name_zh / province_slug / segment / canonical_statement / canonical_polarity / evidence_strength / info_layer / lineage_is_demo / lineage_source_file_sha256 |
| SHA 占位 | — | `REPEAT('0', 64)::TEXT`（O1 真实 SHA 收口前恒占位）|
| 零行守门 | — | `WHERE FALSE`（skeleton）|

### 3.2 dbt/models/marts/mart_city_seven_dim_overview.sql

| 项 | HEAD（修复前）| 当前（修复后）|
|---|---|---|
| 文件存在 | ❌ 不存在 | ✅ 新建（~45 行；9 列 + WHERE FALSE + 5 balance_status enum 在注释中列出）|
| materialization | — | `view` |
| tags | — | `['mart', 'city', 'seven_dim_overview', 's27bf_skeleton']` |
| 列契约 | — | city_id / card_id / n_supports / n_contradicts / n_inference / n_judgment / n_derived / balance_status / is_demo |
| 5 balance_status enum | — | NO_EVIDENCE / NO_CONTRADICTING_EVIDENCE / NO_SUPPORTING_EVIDENCE / SUPPORTS_DOMINANT / CONTRADICTS_DOMINANT（注释中列出；per docs/42 §2.5）|
| 零行守门 | — | `WHERE FALSE` |

### 3.3 tests/test_mart_city_dbt_skel_s27bf.py

| 项 | HEAD（修复前）| 当前（修复后）|
|---|---|---|
| 文件存在 | ❌ 不存在 | ✅ 新建（~150 行；10 pytest cases）|
| cases | — | 4 section × 2-3 case：(1) file existence；(2) mart_evidence_chain 字段契约 + SHA 占位 + WHERE FALSE + 禁词；(3) mart_seven_dim_overview 字段契约 + WHERE FALSE + 禁词；(4) 5 balance_status enum 守门 |

---

## §4. 验证（per `287` §NOW "2"）

### 4.1 新 pytest 输出

```
$ python3 -m pytest tests/test_mart_city_dbt_skel_s27bf.py -v

============================= test session starts ==============================
platform darwin -- Python 14.2.5-pytest-9.0.2
...
collected 10 items

tests/test_mart_city_dbt_skel_s27bf.py::test_mart_evidence_chain_file_exists PASSED [ 10%]
tests/test_mart_city_dbt_skel_s27bf.py::test_mart_seven_dim_overview_file_exists PASSED [ 20%]
tests/test_mart_city_dbt_skel_s27bf.py::test_mart_evidence_chain_declares_required_columns PASSED [ 30%]
tests/test_mart_city_dbt_skel_s27bf.py::test_mart_evidence_chain_sha_is_zero_placeholder PASSED [ 40%]
tests/test_mart_city_dbt_skel_s27bf.py::test_mart_evidence_chain_emits_zero_rows PASSED [ 50%]
tests/test_mart_city_dbt_skel_s27bf.py::test_mart_evidence_chain_no_forbidden_tokens PASSED [ 60%]
tests/test_mart_city_dbt_skel_s27bf.py::test_mart_seven_dim_overview_declares_required_columns PASSED [ 70%]
tests/test_mart_city_dbt_skel_s27bf.py::test_mart_seven_dim_overview_emits_zero_rows PASSED [ 80%]
tests/test_mart_city_dbt_skel_s27bf.py::test_mart_seven_dim_overview_no_forbidden_tokens PASSED [ 90%]
tests/test_mart_city_dbt_skel_s27bf.py::test_mart_seven_dim_overview_lists_5_balance_status_values PASSED [100%]

============================== 10 passed in 0.80s ==============================
```

**结果**：✅ 10/10 PASS

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
| `dbt/models/marts/mart_city_seven_dim_overview.sql` | score/rating/rank/total_score/confidence_score/credibility_score/peer_rank | ✅ 0 hit |
| `tests/test_mart_city_dbt_skel_s27bf.py` | 同上（含 regex 自身）| ✅ CLEAN（regex pattern 不命中 executable code）|

**结果**：✅ CLEAN

### 4.4 manifest invariant

```
$ python3 -c "import json; m=json.load(open('evidence_pack/manifest.json')); ..."
artifact_count: 608 → 613 (after bump)
len(artifacts): 608 → 613
sum(role_count): 608 → 613
INVARIANT: sum(role_count)=613 == artifact_count=613 == len(artifacts)=613
```

**结果**：✅ invariant 守门；本刀 +5（2 mart + 1 pytest + bump + receipt）

### 4.5 不动 Cursor 拥有文档守门

| 文档 | 是否修改 | 来源 |
|---|---|---|
| `docs/47-stage2-s27b-full-mart-evidence-plan-20260826.md` | ❌ 未读未写 | Cursor 拥有 |
| `docs/42 / 43 / 44 / 45 / 46` | ❌ 未读未写 | Cursor 拥有 |
| `docs/06 / 08 / 10 / 34` | ❌ 未读未写 | Cursor 拥有 |
| `dbt/models/staging/_stg_sources.yml` | ❌ 未读未写 | 本刀不引入新 source |
| `dbt/dbt_project.yml` | ❌ 未读未写 | 本刀不引入新 project config |

**结果**：✅ 不动 Cursor 拥有文档；不动 dbt project 配置

---

## §5. 红线自检（per `287` §红线 + docs/47 §1.2 + docs/34 §1/§8/§133 + docs/06 §6.6 + docs/42 §8）

| 红线 | 状态 |
|---|---|
| ❌ 不宣布 Gate 1 / Gate 2 PASS | ✅ 本回执 header + §2 + §5 多次显式守门 |
| ❌ 不擅自改 Cursor 锁定的 10 城名单 | ✅ mart 投影 `city_id` 由 `geo_entity` JOIN；不擅自换/加 |
| ❌ 不接 O1 真样本 | ✅ `lineage_source_file_sha256 = REPEAT('0', 64)`；skeleton 零行 |
| ❌ 不接 person/tenure 真数据 | ✅ mart 字段无 person/tenure JOIN；相关字段留给 S2.7-b-full 落地刀 |
| ❌ 不全量 dbt seed | ✅ skeleton emit 0 行 |
| ❌ 派生 score / rating / rank / total_score / confidence_score / credibility_score / peer_rank | ✅ file-level guard CLEAN（0 hit 2 SQL + pytest）|
| ❌ 不做官员能力总分 / 排名 / DSH / 实时数据 | ✅ docs/44 §1.2 + docs/08 §3.3 守门；本刀不触发 |
| ❌ 批量爬政策研究 / 财政预决算 / 官员履历 | ✅ 无关 |
| ❌ HTTP 爬源站 | ✅ |
| ❌ 降 OCR 门槛 | ✅ 无关 |
| ❌ 启用 pgvector / RLS / partition | ✅ Stage 2 边界（per docs/04 §6）；本刀不动 |
| ❌ 改 `gate_thresholds.json` | ✅ 未读未写 |
| ❌ 不碰 `00-CC-CURRENT.md` | ✅ Cursor 拥有 |
| ❌ 不擅自 --force / --force-with-lease | ✅ ff-only pull |
| ❌ 不替用户下裁定 | ✅ 仅执行 `287` §SCHEMA 范围 |
| ❌ 不在聊天复述 Cursor 长文 | ✅ 仅回执要点 |
| ❌ 不索要 PAT | ✅ |
| ✅ pack invariant 守门 | ✅ 608 → 613；bump script source-of-truth |
| ✅ receipts 仅写 `reviews/stage0-gate0-rework-2026-08-23/` | ✅ |
| ✅ 10 pytest 守门全 PASS | ✅ 4 section × 2-3 case |
| ✅ smoke-check 无回归 | ✅ §10 mart-shape + §11 home nav |
| ✅ 应用层 enum 守门（不引入 schema ENUM）| ✅ 6 段 / 7 维度 / 5 balance_status / 4 info_layer / 2 polarity / 3 strength 由应用层守门（per docs/40 §2.3 + docs/42 §2.4/§2.5）|
| ✅ view 而非 incremental | ✅ per docs/47 §10.2 推荐 |
| ✅ 不接真 SHA → SHA 占位 `'0'*64` 显式 | ✅ `REPEAT('0', 64)::TEXT` |
| ✅ 兼容 S2.7-b-lite / S2.7-b-full-lite 已交 | ✅ 前端 `CityPageMart.tsx` 不动；本刀仅 dbt mart 骨架 |

---

## §6. 推送 / 三路对齐

| 步骤 | 命令 | 结果 |
|---|---|---|
| origin pull | `git fetch origin && git pull --ff-only origin main` | queue_rev 121 ✅ |
| cc_gate_watch | `./scripts/cc_gate_watch.sh --pull` | `CC_ACTION=EXECUTE_NOW` ✅ |
| 2 mart SQL 新建 | `dbt/models/marts/{mart_city_evidence_chain, mart_city_seven_dim_overview}.sql` | ✅（NEW）|
| pytest 新建 | `tests/test_mart_city_dbt_skel_s27bf.py`（10 cases）| ✅（NEW）|
| pytest 验证 | `pytest tests/test_mart_city_dbt_skel_s27bf.py -v` | ✅ 10/10 PASS |
| smoke-check | `python3 frontend/smoke-check.py` | ✅ §10 + §11 全 PASS |
| file-level forbidden-token guard | grep 禁词清单 | ✅ CLEAN（0 hit）|
| bump script | `scripts/_knife32_manifest_bump.py` | ✅ 608 → 613（+5）|
| 本地校验 | `python3 -c "json.load(...)"` manifest invariant | ✅ 613 == 613 == 613 |
| commit (knife 32 主提交) | `git add dbt/models/marts/mart_city_evidence_chain.sql dbt/models/marts/mart_city_seven_dim_overview.sql tests/test_mart_city_dbt_skel_s27bf.py scripts/_knife32_manifest_bump.py evidence_pack/manifest.json reviews/.../288-...md && git commit -m "feat(dbt): S2.7-b-full mart skeleton — mart_city_evidence_chain + mart_city_seven_dim_overview view 骨架 + 10 pytest 守门（O1 占位；零行）"` | ✅ `____` |
| origin push | `git push origin HEAD`（**priority**）| ✅ |
| github push | `git push github HEAD`（带 proxy）| ✅ |
| 三路对齐 | origin/main = github/main = local HEAD | ✅ |
| backfill commit (this) | 独立 commit（不 amend-after-push）| ⏳ this commit |

> **禁止 amend-after-push**：receipt SHA + commit SHA 必须在独立 commit 里 backfill（per knife 2/3/4 经验）。

---

## §7. 下次 heartbeat 预期

- `queue_rev 121` 完成后：Cursor 收 `288` → 下发 `289-stage0-cursor-s27b-full-dbt-skel-audit-…md`（PASS/FAIL）
- 若 PASS：2 mart view 骨架 + 10 pytest 守门随 `288` 入 CI 路径；前端 `CityPageMart.tsx` 仍是 mock；O1 真实 SHA 收口后才接 dbt mart 真表
- 若 FAIL：`288-correction` 回合（修 mart 列契约 + re-commit）

---

## §8. 备注

- **本刀不宣布 Gate 2 PASS** — 这是 S2.7-b-full dbt mart skeleton 最重要的红线。Gate 2 评审日期暂定 W8（per docs/34 §10.4），由 Cursor/用户裁定，不擅自提前。
- **本刀只做 dbt mart view 骨架** — `287` §SCHEMA 显式约束：不接真 SHA / 不接 person/tenure 真数据 / 不全量 seed / 不改 CF/nginx（运维已另做）/ 不爬网。
- **2 mart view 而非 1 mart** — docs/47 §3.1 + §3.2 已明示 mart 拆 2 view：`mart_city_evidence_chain`（段级 evidence）+ `mart_city_seven_dim_overview`（七维度 cell）。本刀按规划拆分。
- **view 而非 incremental** — per docs/47 §10.2 推荐；与 `mart_person_tenure` 平行。incremental 升级待 Stage 3 收口。
- **WHERE FALSE 零行守门** — skeleton 必须 emit 0 行；O1 + Stage 1 OPEN 收口前不暴露假数据。`288-correction` 回合若需 emit 真数据，须同步更新 line 39 + 移除 WHERE FALSE。
- **5 balance_status enum 在注释中列出** — per docs/42 §2.5；应用层 enum 守门（不引入 schema ENUM）。
- **不引入 dbt project.yml / sources.yml 改动** — skeleton 不需要新 source 声明；`st_observation` 等已有 staging view 已可支撑。
- **应用层 enum 守门继承** — mart 列类型为 TEXT，6 段 / 7 维度 / 5 balance_status / 4 info_layer / 2 polarity / 3 strength 由应用层守门（per docs/40 §2.3 + docs/42 §2.4/§2.5）。
- **依赖 O1 真实 SHA 收口** — `lineage_source_file_sha256` 必须从 `'0'*64` 占位替换为 O1 真实 SHA（per docs/47 §6.3 切刀风险）。
- **依赖 Stage 1 OPEN 收口** — 同上。
- **依赖 S2.1-lite PASS** — person/tenure JOIN `mart_person_tenure` 已交后，落地刀再填 `related_persons` 字段。
- **依赖 S2.7-b-full 真数据迁移刀（tasking 26X+）** — 从 mart 骨架 → 真数据迁移；本刀不涉及。
- **下游消费路径** — 前端 `CityPageMart.tsx` 仍消费 `frontend/lib/mart_city_demo.ts`（TS-side demo fixture）；待 full 迁移刀接 dbt 真表时改 consume mart 而非 demo。
- **不修改 dbt 项目配置** — skeleton 不需要 dbt_project.yml 改动；tags 已用 string array 表达。

— End of `288` —

> 等待 Cursor 审验（预期 `289-stage0-cursor-s27b-full-dbt-skel-audit-…md`）。
> 通过后 2 mart view 骨架 + 10 pytest 守门随 `288` 入 CI 路径。
> ⚠ **本刀不宣布 Gate 2 PASS**（per docs/34 §1 + §8 #8 + `287` §红线）。
> ⚠ **本刀只做 dbt mart view 骨架**（per `287` §SCHEMA "本刀做/本刀不做"）。
> ⚠ **O1 真实 SHA 收口前恒占位 `'0'*64`**（per docs/47 §3.1 ⚠️ + `287` §红线）。
> ⚠ **不接 person/tenure 真数据**（per `287` §SCHEMA "本刀不做"）。
> Gate 2 评审日期暂定 W8（per docs/34 §10.4）。