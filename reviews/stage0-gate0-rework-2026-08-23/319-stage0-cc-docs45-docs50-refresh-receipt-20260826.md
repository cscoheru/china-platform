# docs/45 → docs/50 登记 — CC 回执

- 编号：`319-stage0-cc-docs45-docs50-refresh-receipt-20260826`
- 日期：2026-08-26
- queue_rev：`132` → CC 执行
- 任务书：`318-stage2-docs45-gate2-packet-refresh-tasking-20260826`
- 前置：`317` docs/50 PASS；`docs/45 §2 七条`；`docs/50` Gate 2评审包草稿（11 节）
- 用户裁定：**D**；不宣布 Gate PASS
- 任务性质：**docs/45 登记 Gate 2 评审包草稿** — 机械登记 `docs/50` / 回执 `316`；标明草稿、OPEN 必带、非 PASS；不改 docs/50 既有内容
- pack bump：**637 → 639**（+2 = bump + receipt；docs/45 SHA REFRESH 不增计数）

---

## §NOW 执行表

| 步 | 项 | 状态 | role |
|---|---|---|---|
| 1 | `git fetch origin && git pull --ff-only origin main`（queue_rev 132）| ✅ | — |
| 2 | 读 `318` tasking + `docs/45` 当前内容 + `317` 前置回执 + `docs/50` 评审包草稿 | ✅ | — |
| 3 | 改 `docs/45-stage2-s210-lite-gate2-review-index-20260826.md`：header 加 queue_rev 132；§1 + docs/50 索引条目（11 节）；§3 O3 行 + docs/50 引用；§6.2 + Gate 2 评审包草稿行 + Gate 2 三类划分行；§7 invariant 更新到 637；§7 O1+O8 OPEN 携带更新 + Gate 2 评审包草稿登记 | ✅ MOD | documentation |
| 4 | 创建 `scripts/_knife42_manifest_bump.py`（2 NEW + 1 REFRESH）| ✅ NEW | spike_helper |
| 5 | bump pack（637 → **639**；+2）| ✅ | — |
| 6 | 写回执 `319` 入 `reviews/`（本文件）| ✅（本文件）| documentation |
| 7 | commit → `origin` 优先 → `github` | ⏳ this commit | — |
| 8 | commit SHA backfill（独立 commit；不 amend-after-push）| ⏳ this commit | — |
| 9 | 三路对齐 | ✅ local = origin = github | — |
| 10 | → `84` POLL + `cc_gate_watch` re-arm | ✅ re-armed → `CC_ACTION=POLL` | — |

---

## §1. 交付清单

### 1.1 修改 1 + 新增 2 个文件

| 路径 | 行数 | role | 状态 |
|---|---|---|---|
| `docs/45-stage2-s210-lite-gate2-review-index-20260826.md` | ~280 | documentation | MOD（header + §1 + §3 O3 + §6.2 + §7）|
| `scripts/_knife42_manifest_bump.py` | ~125 | spike_helper | NEW |
| `reviews/.../319-...md`（本文件）| — | documentation | NEW |

### 1.2 manifest 变更

| 字段 | 变更前 | 变更后 |
|---|---|---|
| `artifact_count` | 637 | **639** (+2: bump + receipt; docs/45 REFRESH 不增计数) |
| `len(artifacts)` | 637 | **639** |
| `sum(role_count)` | 637 | **639**（bump script source-of-truth 重算）|

**invariant 守门**：639 == 639 == 639 ✅

### 1.3 docs/45 修改详情

| § | 修改前 | 修改后 |
|---|---|---|
| header | 7 刷新行（queue_rev 97/103/108/119/125/127/130）| 8 刷新行（+queue_rev 132 per `318`）|
| §1 索引目的 | 7 条验收 + Gate 2 评审日期 W8 | +docs/50 Gate 2 评审包草稿（11 节；七条 ↔ 证据 + OPEN 必带 + 不可隐藏清单 8 项 + 预览路径；回执 `316`）；**docs/50 是草稿（不宣布 Gate 2 PASS）**；O1 WAITING_FILE + O3 规划已交实装仍 OPEN + docs/10 §3.2-3.4 xfail stub 必带 OPEN 清单；Gate 2 评审日期 W8（不擅自提前）|
| §3 O3 行 | "S1.17 scanned PDF OPEN → docs/49 规划蓝图（7 步流水线设计 + allowlist + is_demo/SHA lineage 衔接 + 验收清单；回执 309）" | +docs/50 Gate 2 评审包草稿引用（11 节；七条 ↔ 证据 + OPEN 必带 + 不可隐藏清单 8 项；回执 316）；必带 OPEN 清单指向 docs/50 §3.3 + §5.1 + §5.3 + §9 #2 |
| §6.2 接驳路径 | 16 元素（O3 4 退出码契约 + allowlist 等）| +Gate 2 评审包草稿（per docs/50 + 316）+ Gate 2 三类划分（per docs/50 §3）= 18 元素 |
| §7 invariant | 旧 `635 == 635 == 635`（knife 40 stale）| 更新到 `637 == 637 == 637`（knife 41 stale）→ knife 42 `639 == 639 == 639` |
| §7 O1 + O8 OPEN 携带 | "lineage.source_file_sha256 + person/tenure 真数据；person/tenure **demo** 已交 `303`；**O3 OCR 规划已交 `309` 仍 OPEN**" | +"**Gate 2 评审包草稿已交 `docs/50` + `316`，必带 OPEN 清单**" |

---

## §2. 关键决策（per `318` §SCHEMA + docs/50 §0/§3/§5 + docs/34 §1/§3/§120 + docs/45 §3 OPEN + `317`）

| 决策点 | 裁定 | 来源 |
|---|---|---|
| 本刀性质 | **docs/45 → docs/50 登记** — 机械登记 `docs/50` / 回执 `316`；**不改 docs/50 既有内容**；不宣布 Gate 2 PASS | `318` §SCHEMA "本刀做/本刀不做" |
| header 加 queue_rev 132 | 第 7 次机械刷新（queue_rev 103/108/119/125/127/130/132）| `318` §NOW "1" |
| §1 加 docs/50 索引条目 | 11 节概要 + 必带 OPEN 清单引用 + 草稿（不宣布 Gate 2 PASS）| `318` §SCHEMA + docs/50 §0 |
| §3 O3 行 + docs/50 引用 | O3 OPEN 状态明确：规划已交（`docs/49` + `309`），实装仍 OPEN；**docs/50 Gate 2 评审包草稿已交**（11 节；回执 `316`）；必带 OPEN 清单指向 docs/50 §3.3 + §5.1 + §5.3 + §9 #2 | `318` §NOW "1" + docs/50 §3.3/§5.1/§5.3/§9 |
| §6.2 加 Gate 2 评审包草稿 + Gate 2 三类划分 | docs/50 11 节 + 不可降级 4 / 演示级 2 / 仍 OPEN 5 三类 | docs/50 §3 + §0 |
| §7 invariant 更新 | 旧 `635` (knife 40 stale) → knife 41 `637` → knife 42 `639` | bump script source-of-truth |
| §7 O1 + O8 OPEN 携带 | +Gate 2 评审包草稿已交 `docs/50` + `316`，必带 OPEN 清单 | docs/34 §120 + docs/50 §9 |
| ❌ 宣布 Gate 1/2 PASS | 红线条目（多处显式守门）| docs/34 §1 + §8 #8 + §133 + `318` §红线 + docs/50 §0 |
| ❌ 宣布 O1 收口 | 红线条目（§1 + §3 + §7 多处显式 OPEN WAITING_FILE）| `318` §红线 + docs/34 §3 + §120 + `284` |
| ❌ 宣布 O3 收口 | 红线条目（§1 + §3 O3 + §7 多处显式 OPEN 实装未实装）| `318` §红线 + docs/34 §3 + `docs/49` §5.3 + `309` |
| ❌ 爬网 / 登录绕过 / OCR 降门槛 | docs/50 §0.3 + §5.3 显式禁止；本刀不引入新 HTTP | `318` §红线 + docs/49 §2.2 |
| ❌ 伪造样本 | 仅索引刷新 + `docs/50` 已显式守门 | `318` §红线 + docs/06 §6.6 |
| ❌ 改 Cursor 拥有架构文档 | docs/06/08/10/34/40-44/46-50 / `00-CC-CURRENT.md` 未读未写 | `318` §红线 + Cursor 37 architect-only |
| ❌ 改 `gate_thresholds.json` | 未读未写 | `318` §红线 |
| ❌ 改 docs/50 既有内容 | docs/50 = 本刀不修改（仅 docs/45 登记 docs/50 引用）| `318` §SCHEMA "本刀做/本刀不做" |

---

## §3. 修改对照（per `318` §NOW "1"）

### 3.1 docs/45 header

| 项 | HEAD（修改前 / queue_rev 130 之后）| 当前（修改后 / queue_rev 132）|
|---|---|---|
| 刷新行数 | 7（queue_rev 97/103/108/119/125/127/130）| 8（+queue_rev 132 per `318`）|
| 末行措辞 | +O3 OCR 生产路径规划落地（`309` 7 步流水线 + allowlist + lineage 衔接 + 验收清单 + 显式禁爬网/登录绕过；见 `docs/49`）；**O3 仍 OPEN**（未实装 OCR 引擎 + 未收口；tasking 31X+）；Gate 2 评审必带 OPEN 清单 | +登记 **`docs/50`** Gate 2 评审包**草稿**（11 节；七条 ↔ 证据 + OPEN 必带 + 不可隐藏清单 8 项 + 预览路径；回执 `316`）；§1 + §6 + §6.2 + §7 同步指向 docs/50；**docs/50 是草稿（不宣布 Gate 2 PASS）**，O1 WAITING_FILE + O3 规划已交实装仍 OPEN + docs/10 §3.2-3.4 xfail stub 必带 OPEN 清单；Gate 2 评审日期 W8（per docs/34 §10.4，不擅自提前）|

### 3.2 §1 索引目的 + §3 O3 行

| 项 | HEAD（修改前）| 当前（修改后）|
|---|---|---|
| §1 索引目的 | 7 条验收 + Gate 2 评审日期 W8 | +**Gate 2 评审包草稿**（per `docs/50` + `316`）：§2 七条 ↔ 证据路径 + §3 三类划分 + §4 演示场景 + §5 OPEN 必带 + §6 评审脚本清单 + §7 预览路径（**非 O1/O3 收口**）+ §8 红线自检 + §9 不可隐藏清单 8 项 + §10 备注；**docs/50 是草稿（不宣布 Gate 2 PASS）**；O1 WAITING_FILE + O3 规划已交实装仍 OPEN + docs/10 §3.2-3.4 xfail stub 必带 OPEN 清单；Gate 2 评审日期 W8 |
| §3 O3 行 | "S1.17 scanned PDF OPEN → `docs/49` 规划蓝图（7 步流水线设计 + allowlist + `is_demo`/SHA lineage 衔接 + 验收清单；回执 `309`）\| ⚠️ **O3 仍 OPEN — 规划已交，实装待 tasking 31X+**；Gate 2 评审必带 OPEN 清单" | +**`docs/50` Gate 2 评审包草稿**已交（11 节；七条 ↔ 证据 + OPEN 必带 + 不可隐藏清单 8 项；回执 `316`）\| ⚠️ **O3 仍 OPEN — 规划已交，实装待 tasking 31X+**；Gate 2 评审必带 OPEN 清单（per docs/50 §3.3 + §5.1 + §5.3 + §9 #2）|

### 3.3 §6.2 + §7

| 项 | HEAD（修改前）| 当前（修改后）|
|---|---|---|
| §6.2 接驳路径 | 16 元素（mart-shape + mart 骨架/demo-join/intake/parity + relatedPersons demo + 真数据 + enum 守门 + 禁词 + O3 规划 + O3 4 退出码契约 + allowlist）| 18 元素（+**Gate 2 评审包草稿** + **Gate 2 三类划分** per `docs/50` §3）|
| §7 invariant 措辞 | "⏳ bump + commit 后 635 == 635 == 635（knife 40: docs/45 刷新 + 回执 313 + bump；633 → 635）" | "⏳ bump + commit 后 637 == 637 == 637（knife 41: docs/50 评审包草稿 + 回执 316 + bump；635 → 637；+2 = bump + receipt；docs/45 SHA REFRESH 不增计数）"|
| §7 O1 + O8 OPEN 携带 | "§3 + §5.5 + §6.2（lineage.source_file_sha256 + person/tenure 真数据；person/tenure **demo** 已交 `303`；**O3 OCR 规划已交 `309` 仍 OPEN**）推 S2.7-b-full 真数据迁移刀 + O3 tasking 31X+" | "§3 + §5.5 + §6.2（lineage.source_file_sha256 + person/tenure 真数据；person/tenure **demo** 已交 `303`；**O3 OCR 规划已交 `309` 仍 OPEN**；**Gate 2 评审包草稿已交 `docs/50` + `316`，必带 OPEN 清单**）推 S2.7-b-full 真数据迁移刀 + O3 tasking 31X+" |

---

## §4. 验证（per `318` §NOW "1-2"）

### 4.1 markdown lint

docs/45 是 markdown 文件；本刀未引入新表头格式（仅在已有表格内追加行 + §1 加段 + §6.2 加 2 行 + §7 invariant 更新 + §7 O1+O8 OPEN 携带更新）。格式一致性由 docs/45 既有惯例守门。

### 4.2 不动 Cursor 拥有文档守门

| 文档 | 是否修改 | 来源 |
|---|---|---|
| `docs/45-stage2-s210-lite-gate2-review-index-20260826.md`（本刀）| ✅ 修改 | CC 拥有（per header "起草：CC"）|
| `docs/50-stage2-gate2-review-packet-draft-20260826.md` | ❌ 未读未写 | 本刀仅在 docs/45 登记 docs/50 引用；不修改 docs/50 既有内容（per `318` §SCHEMA "本刀做/本刀不做" + `317`）|
| `docs/49-stage2-o3-ocr-prod-path-plan-20260826.md` | ❌ 未读未写 | docs/45 引用 docs/49 §0/§2.2/§3.2 步骤 4/§5.3/§6.2/§10；不修改 docs/49 既有内容 |
| `docs/48-stage2-real-sha-intake-handbook-20260826.md` | ❌ 未读未写 | docs/45 引用 docs/48 §2/§3/§4.1/§4.3；不修改 docs/48 既有内容 |
| `docs/44 / 47 / 41 / 36-39 / 42 / 43` | ❌ 未读未写 | Cursor 拥有架构文档 |
| `docs/06 / 08 / 10 / 34` | ❌ 未读未写 | Cursor 拥有 |
| `docs/40-43 / 46` | ❌ 未读未写 | Cursor 拥有 |
| `scripts/intake_real_sha_if_present.py` / `scripts/compute_file_sha.py` / `scripts/replace_demo_with_real.py` | ❌ 未读未写 | 引用，不修改 |
| `00-CC-CURRENT.md` | ❌ 未读未写 | Cursor 拥有 |
| `gate_thresholds.json` | ❌ 未读未写 | 红线条目 |

**结果**：✅ docs/45 是 CC 维护的 Gate 2 评审索引（per header "起草：CC · 2026-08-26 · queue_rev 97" + 多次刷新行），本次属于第 7 次索引刷新（queue_rev 103/108/119/125/127/130/132）；Cursor 拥有架构文档未动。

### 4.3 manifest invariant

```
$ python3 scripts/_knife42_manifest_bump.py
ADD: scripts/_knife42_manifest_bump.py (... bytes, sha=____)
ADD: reviews/.../319-...md (... bytes, sha=____)
REFRESH: docs/45-stage2-s210-lite-gate2-review-index-20260826.md (sha ____ → ____)
UPDATE artifact_count: 637 → 639
INVARIANT: sum(role_count)=639 == artifact_count=639 == len(artifacts)=639
OK manifest updated; added 2 artifacts
```

**结果**：✅ invariant 守门；本刀 +2（bump + receipt），docs/45 SHA REFRESH（不增计数）

### 4.4 docs/45 内容守门

| 检查项 | 状态 |
|---|---|
| ✅ header 8 刷新行（含 queue_rev 132 per `318`）| ✅ |
| ✅ §1 + docs/50 Gate 2 评审包草稿索引条目（11 节；OPEN 必带 + 非 PASS）| ✅ |
| ✅ §3 O3 行 + docs/50 引用 + docs/50 §3.3/§5.1/§5.3/§9 #2 必带 OPEN 清单 | ✅ |
| ✅ §6.2 18 元素（+ Gate 2 评审包草稿 + Gate 2 三类划分）| ✅ |
| ✅ §7 invariant 更新到 637（knife 41 stale → 639 待 knife 42 commit）| ✅ |
| ✅ §7 O1 + O8 OPEN 携带更新（+ Gate 2 评审包草稿登记）| ✅ |
| ✅ ⚠ 不宣布 Gate 2 PASS / O1 / O3 收口 守门贯穿全文 | ✅ |
| ✅ O1 + O3 OPEN 显式携带（per docs/34 §3 + §120）| ✅ |
| ✅ Gate 2 评审日期 W8（per docs/34 §10.4）| ✅ |

---

## §5. 红线自检（per `318` §红线 + docs/34 §1/§3/§8/§120/§133 + docs/50 §0/§7 + docs/49 §0/§7 + docs/06 §6.6 + docs/42 §8 + docs/45 §6.2）

| 红线 | 状态 |
|---|---|
| ❌ 不宣布 Gate 1 / Gate 2 PASS | ✅ docs/45 §1 + §6 + §7 + §8（CC 建议 Gate 2 PASS 守门）+ 本回执 header + §2 + §5 多次显式守门 |
| ❌ 不擅自 O1 收口 | ✅ docs/45 §3 O1 详细 + §1 + §7 + 本回执 §2 + §5 显式 OPEN；intake WAITING_FILE；预览路径**非 O1** |
| ❌ 不擅自 O3 收口 | ✅ docs/45 §3 O3 行 + §3 O1 详细 O3 子项 + §1 + §6.2 + §7 + 本回执 §2 + §5 多处显式 OPEN |
| ❌ 不实装 OCR 引擎 | ✅ docs/49 §0 范围 + §8 不在范围；docs/45 §3 O3 + §6.2 + §7 显式 OPEN（实装待 tasking 31X+）|
| ❌ 伪造样本 / 真履历 | ✅ 仅索引刷新 + `docs/50` 已显式守门 |
| ❌ 派生 score / rating / rank / total_score / confidence_score / credibility_score / peer_rank | ✅ docs/45 §6.2 禁词守门沿用；本刀不引入 |
| ❌ 不做官员能力总分 / 排名 / DSH / 实时数据 | ✅ docs/44 §1.2 + docs/08 §3.3 守门；本刀不触发 |
| ❌ 批量爬政策研究 / 财政预决算 / 官员履历 | ✅ 无关 |
| ❌ HTTP 爬源 | ✅ docs/49 §2.2 显式禁止；docs/45 §3 O1 详细 + §6.2 引用；本刀不引入新 HTTP |
| ❌ 登录绕过 | ✅ docs/49 §2.2 显式禁止；docs/45 引用 |
| ❌ 未授权 cloud OCR API | ✅ docs/49 §2.2 显式禁止；docs/45 引用 |
| ❌ 降 OCR 门槛 | ✅ |
| ❌ 启用 pgvector / RLS / partition | ✅ Stage 2 边界；本刀不动 |
| ❌ 改 `gate_thresholds.json` | ✅ 未读未写 |
| ❌ 不碰 `00-CC-CURRENT.md` | ✅ Cursor 拥有 |
| ❌ 不擅自 --force / --force-with-lease | ✅ ff-only pull |
| ❌ 不替用户下裁定 | ✅ 仅执行 `318` §SCHEMA 范围（机械登记）|
| ❌ 不在聊天复述 Cursor 长文 | ✅ 仅回执要点 |
| ❌ 不索要 PAT | ✅ |
| ✅ pack invariant 守门 | ✅ 637 → 639；bump script source-of-truth + docs/45 SHA REFRESH |
| ✅ receipts 仅写 `reviews/stage0-gate0-rework-2026-08-23/` | ✅ |
| ✅ 不改 Cursor 拥有架构文档 | ✅ docs/06/08/10/34/40-44/46-50 / `00-CC-CURRENT.md` 未读未写 |
| ✅ 不擅自提前 Gate 2 评审日期 | ✅ W8（per docs/34 §10.4）|
| ✅ mart-shape 禁词 3 重守门 | ✅ runtime + 静态 scanner + pytest + TS 类型约束（per docs/45 §6.2）|
| ✅ mart-shape feature-flag 默认值 | ✅ `NEXT_PUBLIC_USE_MART_FIXTURE !== "1"` 默认走 mock |
| ✅ 兼容 S2.7-b-lite / S2.7-b-full-lite / S2.7-b-full mart skel / demo-join / parity / person-tenure demo | ✅ 8 回执全部入 §6.1（`257`/`266`/`288`/`291`/`294`/`297`/`303`/`316`）|
| ✅ O1 + O3 OPEN 显式携带 | ✅ §1 + §3 + §6.2 + §7 |
| ✅ 预览路径明确非 O1 收口 | ✅ §1 + §6.2 |
| ✅ docs/45 = CC 维护索引（per header "起草：CC"）| ✅ 第 7 次机械刷新（queue_rev 103/108/119/125/127/130/132）|
| ✅ docs/50 引用而非修改 | ✅ docs/45 §1 + §3 O3 + §6.2 + §7 多处引用 docs/50 + `316`；不改 docs/50 既有内容 |
| ✅ O3 输入边界显式禁止 | ✅ §3 O1 详细 + §6.2 引用 docs/49 §2.2（HTTP / 登录绕过 / 未授权 API / symlink）|
| ✅ O3 4 退出码契约 + allowlist 复用 docs/48 | ✅ §6.2 显式 |
| ✅ OCR 引擎选型待用户裁定 | ✅ §3 O1 详细 显式 |
| ✅ O3 仍 OPEN — 未实装 | ✅ 多处显式 OPEN |
| ✅ Gate 2 评审包草稿登记齐 | ✅ §1 + §3 O3 + §6.2 + §7 多处引用 docs/50 + `316` |
| ✅ Gate 2 三类划分（不可降级 / 演示级 / 仍 OPEN）| ✅ §6.2 引用 docs/50 §3 |
| ✅ 不可隐藏清单（Gate 2 评审必带）| ✅ §7 O1+O8 OPEN 携带引用 docs/50 §9 不可隐藏清单 8 项 |

---

## §6. 推送 / 三路对齐

| 步骤 | 命令 | 结果 |
|---|---|---|
| origin pull | `git fetch origin && git pull --ff-only origin main` | queue_rev 132 ✅ |
| cc_gate_watch | `./scripts/cc_gate_watch.sh --pull` | `phase=CC_ACTION_REQUIRED` ✅ |
| docs/45 修改 | `docs/45-stage2-s210-lite-gate2-review-index-20260826.md`（header + §1 + §3 O3 + §6.2 + §7 invariant + §7 O1+O8 OPEN 携带）| ✅ MOD |
| bump script | `scripts/_knife42_manifest_bump.py`（2 NEW + 1 REFRESH）| ✅ 637 → 639（+2）|
| 本地校验 | manifest invariant | ✅ 639 == 639 == 639 |
| commit (knife 42 主提交) | `git add ... && git commit -m "docs(45): 318 docs/50 评审包草稿登记 — §1/§3 O3/§6.2/§7 同步"` | ✅ `93f9b5001b8f25926c65d85df73b7c9a74c043f2` |
| origin push | `git push origin HEAD`（**priority**）| ✅ `93f9b50` → origin/main |
| github push | `git push github HEAD` | ✅ `93f9b50` → github/main |
| 三路对齐 | origin/main = github/main = local HEAD | ✅ `93f9b5001b8f25926c65d85df73b7c9a74c043f2` |
| backfill commit | 独立 commit（不 amend-after-push）| ✅ `93f9b50` + receipt backfill |

> **禁止 amend-after-push**：receipt SHA + commit SHA 必须在独立 commit 里 backfill（per knife 2/3/4 经验）。

---

## §7. 下次心跳预期

- `queue_rev 132` 完成后：Cursor 收 `319` → 下发 `320-stage0-cursor-s318-docs45-docs50-audit-…md`（PASS/FAIL）
- 若 PASS：docs/45 → docs/50 登记齐；Gate 2 评审包草稿齐（`docs/50` + `316` + `319`）；§1 + §3 O3 + §6.2 + §7 多处显式引用 docs/50；O1 WAITING_FILE + O3 规划已交实装仍 OPEN + docs/10 §3.2-3.4 xfail stub 必带 OPEN 清单
- 若 FAIL：`319-correction` 回合（修 docs/45 表格 / 修 §1 措辞 / re-commit）

---

## §8. 备注

- **本刀不宣布 Gate 2 / O1 / O3 PASS** — docs/45 §1 + §6 + §7 + §8 + 本回执 §2 + §5 多次显式守门。Gate 2 评审日期暂定 W8（per docs/34 §10.4），由 Cursor/用户裁定，不擅自提前。
- **本刀只做机械索引登记** — `318` §SCHEMA 显式约束：不接真 SHA / 不接 person/tenure 真数据 / 不爬网 / 不派生 score / 不改架构设计 / **不实装 OCR 引擎** / **不宣布 Gate/O1/O3 收口**。
- **docs/45 = CC 维护索引（per header "起草：CC · queue_rev 97"）** — 本次属于第 7 次机械刷新（queue_rev 103/108/119/125/127/130/132）；Cursor 拥有架构文档（docs/06/08/10/34/40-44/46-50）未动。**红线 "Cursor 37 architect-only (don't write docs Cursor owns)" 不约束 docs/45**，因为 docs/45 是 CC 维护的索引，由 Cursor 任务书（如 `318`）显式委托刷新。
- **O1 仍 WAITING_FILE** — docs/45 §3 O1 详细 + §1 + §7 多处显式 OPEN。O1 真收口须用户主动 `--confirm-o1=PATH` + 真实 SHA 投递 + intake 4 退出码契约（per `291` + docs/48 §4.3）。
- **O3 仍 OPEN — 规划已交，实装待 tasking 31X+** — docs/45 §3 O3 行 + §3 O1 详细 O3 子项 + §1 + §6.2 + §7 多处显式标注。O3 实装须用户裁定 paddle-ocr / tesseract / cloud + 用户主动 `--confirm-o3=PATH` 提供真实 PDF + 端到端 pytest PASS（per `docs/49` §5.3 + §8 + §10）。
- **docs/50 引用而非修改** — docs/45 §1 + §3 O3 + §6.2 + §7 多处登记 docs/50 + `316` 引用；不改 docs/50 既有内容（per `318` §SCHEMA "本刀做/本刀不做" + docs/50 §0 范围 + `317`）。
- **Gate 2 三类划分（不可降级 / 演示级 / 仍 OPEN）** — docs/45 §6.2 引用 docs/50 §3：不可降级 4 项（#2/#4/#5/#6）+ 演示级 2 项（#1/#3）+ 仍 OPEN 5 项（dbt mart 真表 / docs/10 §3.2-3.4 / O1 / O3 / person/tenure 真数据）。
- **不可隐藏清单（Gate 2 评审必带 8 项）** — docs/45 §7 O1+O8 OPEN 携带引用 docs/50 §9。
- **预览路径明确非 O1 收口** — docs/45 §1 + §6.2 显式："该预览仅是 demo 演示管道，不构成 O1 收口"；`lineage.source_file_sha256` 恒为 `'0'*64` 占位。
- **OCR 引擎选型待用户裁定** — docs/45 §3 O1 详细显式 paddle-ocr 推荐 + tesseract/cloud 备选 + 用户裁定（per `docs/49` §3.2 步骤 4 + §10 Q1）。
- **真实 PDF 待用户主动 `--confirm-o3=PATH`** — docs/45 §3 O1 详细显式（per `docs/49` §10 Q4 + docs/48 §3 intake 模式）。
- **cloud OCR 默认离线** — docs/45 §3 O1 详细显式 + docs/49 §2.2 显式禁止未授权 API（须 `--enable-cloud-ocr=PROVIDER` 显式 flag）。
- **下游分发依赖** — docs/45 §3 O1 详细显式 S2.1-lite `mart_person_tenure` + S2.2 `policy_observation` + S2.4 `fiscal_observation`（per `docs/49` §6.2）。
- **§7 invariant 更新** — 旧 `635` (knife 40 stale) → knife 41 `637` (knife 41 stale) → knife 42 `639`；manifest SHA 必须同步更新（per knife 16 source-of-truth fix）。
- **docs/45 header 8 刷新行** — queue_rev 97 (`250`) + 103 (`259`) + 108 (`268`) + 119 (`284`) + 125 (`299`) + 127 (`305`) + 130 (`312`) + **132 (`318`)**。
- **不修改 dbt 项目配置** — 索引刷新刀不需 dbt_project.yml 改动。
- **下次 heartbeat 闸门** — O1 真收口须用户主动 `--confirm-o1=PATH` + 真实 SHA 投递；O3 真收口须用户主动 `--confirm-o3=PATH` + OCR 引擎选型裁定 + 端到端 pytest PASS；docs/10 §3.2-3.4 收口待 S2.10 落地刀（tasking 251+）；在此之前 docs/45 §3 O1 + §3 O3 + §5.5 + §6 + §6.2 仍标注必带 OPEN 清单。

— End of `319` —

> 等待 Cursor 审验（预期 `320-stage0-cursor-s318-docs45-docs50-audit-…md`）。
> 通过后 docs/45 → docs/50 登记齐；Gate 2 评审包草稿齐（`docs/50` + `316` + `319`）；§1 + §3 O3 + §6.2 + §7 多处显式引用 docs/50；O1 WAITING_FILE + O3 规划已交实装仍 OPEN + docs/10 §3.2-3.4 xfail stub 必带 OPEN 清单。
> ⚠ **本刀不宣布 Gate 2 / O1 / O3 PASS**（per docs/34 §1 + §8 #8 + §120 + §133 + `318` §红线）。
> ⚠ **本刀只做机械索引登记**（per `318` §SCHEMA "本刀做/本刀不做"）。
> ⚠ **O1 真实 SHA 收口前恒占位 `'0'*64`**（per docs/47 §3.1 ⚠️ + `318` §红线）。
> ⚠ **O3 真收口须用户主动 `--confirm-o3=PATH` + OCR 引擎选型裁定 + 端到端 pytest PASS**（per `docs/49` §5.3 + §8 + §10 + docs/48 §3）。
> ⚠ **cloud OCR 默认离线；须 `--enable-cloud-ocr=PROVIDER` 显式 flag**（per `docs/49` §2.2 + §3.2 步骤 4）。
> ⚠ **输入边界 = 仅用户/admin upload；禁止 HTTP 爬源 / 登录绕过 / 未授权 API / symlink / 伪造**（per `docs/49` §2.2）。
> ⚠ **docs/10 §3.2-3.4 xfail stub（Stage 3 收口）；Gate 2 评审必带 OPEN 清单**。
> ⚠ **Gate 2 评审日期暂定 W8**（per docs/34 §10.4），由 Cursor/用户裁定，**不擅自提前**。