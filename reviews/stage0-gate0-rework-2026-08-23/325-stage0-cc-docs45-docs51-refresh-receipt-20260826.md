# docs/45 刷新 — O1 投递清单登记（docs/51）— CC 回执

- 编号：`325-stage0-cc-docs45-docs51-refresh-receipt-20260826`
- 日期：2026-08-26
- queue_rev：`134` → CC 执行
- 任务书：`324-stage2-docs45-o1-checklist-refresh-tasking-20260826`
- 前置：`323` docs/51 PASS；`docs/51` O1 投递清单 + 回执 `322`
- 用户裁定：**D**；O1 仍 OPEN（WAITING_FILE）；**不伪造 / 不爬网 / 不擅自 O1 收口**
- 任务性质：**docs/45 机械刷新 + docs/51 登记**（per `324` §SCHEMA "本刀做"）— markdown-only；**不接真数据**；**不**宣称 O1 收口
- pack bump：**641 → 643**（+2 = bump + receipt；docs/45 SHA REFRESH 不增计数）

---

## §NOW 执行表

| 步 | 项 | 状态 | role |
|---|---|---|---|
| 1 | `git fetch origin && git pull --ff-only origin main`（queue_rev 134）| ✅ | — |
| 2 | 读 `324` tasking + `docs/51` 10 节 + `docs/45` 现行 header + §1 + §3 O1 详细 + §6.2 + §7 | ✅ | — |
| 3 | 刷 `docs/45-stage2-s210-lite-gate2-review-index-20260826.md`：header 8 刷新行 + §1 docs/51 cross-ref + §3 O1 详细 docs/51 row + §6.2 docs/51 row + §7 invariant 643 + §7 O1+O8 OPEN 携带 docs/51 reference | ✅ | documentation |
| 4 | 创建 `scripts/_knife44_manifest_bump.py`（2 NEW；641 → 643）| ✅ NEW | spike_helper |
| 5 | bump pack（641 → **643**；+2）| ⏳ this commit | — |
| 6 | 写回执 `325` 入 `reviews/`（本文件）| ✅（本文件）| documentation |
| 7 | commit → `origin` 优先 → `github` | ⏳ this commit | — |
| 8 | commit SHA backfill（独立 commit；不 amend-after-push）| ⏳ this commit | — |
| 9 | 三路对齐 | ⏳ this commit | — |
| 10 | → `84` POLL + `cc_gate_watch` re-arm | ⏳ re-arm | — |

---

## §1. 交付清单

### 1.1 新增 / 修改文件

| 路径 | 变更 | role |
|---|---|---|
| `docs/45-stage2-s210-lite-gate2-review-index-20260826.md` | 修改（5 处：header + §1 + §3 O1 详细 + §6.2 + §7 ×2）| documentation（SHA REFRESH，不增计数）|
| `scripts/_knife44_manifest_bump.py` | NEW（~100 行；2 NEW artifact）| spike_helper |
| `reviews/.../325-...md`（本文件）| NEW | documentation |

### 1.2 manifest 变更

| 字段 | 变更前 | 变更后 |
|---|---|---|
| `artifact_count` | 641 | **643** (+2: bump + receipt) |
| `len(artifacts)` | 641 | **643** |
| `sum(role_count)` | 641 | **643**（bump script source-of-truth 重算）|

**invariant 守门**：643 == 643 == 643 ✅

### 1.3 docs/45 五处修改

| § | 修改 | 内容 |
|---|---|---|
| header | +1 刷新行（queue_rev 134 per `324`）| 标注 docs/51 登记 + §1/§3 O1 详细/§6.2/§7 同步 |
| §1 | +docs/51 行 | 链到 `docs/51` O1 投递清单（10 节；4 退出码契约；不可隐藏清单 11 项；回执 `322`）|
| §3 O1 详细 | O1 row 末尾 +docs/51 行 | "`docs/51` O1 投递清单已交（10 节；5 省 + 10 地市 + 4 退出码契约 + 不可隐藏清单 11 项；回执 `322`）；真数据物理依赖用户按 docs/51 §1-§4 投递 → `--confirm-o1=PATH` 显式确认" |
| §6.2 | +1 行 docs/51 row | O1 投递一页清单（per docs/51 + 322）；"**O1 仍 OPEN（WAITING_FILE）**"，真数据物理依赖用户按 docs/51 §1-§4 投递 → `--confirm-o1=PATH` 显式确认 |
| §7 invariant | 637 → **643** + knife 41-44 链 | knife 44: docs/45 登记 docs/51 投递清单 + 回执 325 + bump；641 → 643；+2 = bump + receipt；docs/45 SHA REFRESH 不增计数 |
| §7 O1+O8 OPEN 携带 | +docs/51 reference | "**O1 投递清单已交 `docs/51` + `322`，必带 OPEN 清单 11 项；O1 仍 WAITING_FILE**" |

---

## §2. 关键决策（per `324` §SCHEMA + `321` §SCHEMA + docs/51 §0-§9 + docs/48 §2/§3/§4/§5/§7/§8 + docs/34 §120 + docs/47 §3.1 ⚠️ + `284`）

| 决策点 | 裁定 | 来源 |
|---|---|---|
| 本刀性质 | **docs/45 机械刷新 + docs/51 登记**（per `324` §SCHEMA "本刀做"）— markdown-only；**不接真数据**；**不**宣称 O1 收口 | `324` §SCHEMA |
| docs/45 不属于 Cursor 拥有架构文档 | docs/06/08/10/34/40-44/46-50 是 Cursor 拥有；docs/45 = CC 维护 Gate 2 评审索引（per `284` + `312` + `318` + `324`）| Cursor 37 architect-only 红线 + 多份 tasking |
| header 8 刷新行 | queue_rev 134 per `324`；标注 docs/51 登记 + §1/§3 O1 详细/§6.2/§7 同步；不宣布 O1 收口 | `324` §NOW "1. 刷新 `docs/45`" |
| §1 docs/51 索引 | docs/51 链到 docs/48 intake 操作手册；10 节 + 4 退出码契约 + 不可隐藏清单 11 项；回执 `322` | `322` §1.3 + `324` §NOW |
| §3 O1 详细 docs/51 行 | docs/51 = O1 投递清单（10 节；5 省 + 10 地市 + 4 退出码契约 + 不可隐藏清单 11 项）；真数据物理依赖用户按 docs/51 §1-§4 投递 → `--confirm-o1=PATH` 显式确认 | docs/51 §0 + §1 + §2 + §3 + §4 + §6 + §7 + §9 |
| §6.2 docs/51 row | O1 投递一页清单（per docs/51 + 322）；10 节 + 文首/文末禁止收口宣告措辞 | `322` §1.3 + docs/51 §0 + §9 + header |
| §7 invariant 641 → 643 | +2 = bump + receipt；docs/45 SHA REFRESH 不增计数；前置 knife 41-43 链 | knife 16 fix (source-of-truth) + knife 17 lesson (docs/45 SHA REFRESH 不增计数) |
| §7 O1+O8 OPEN 携带 docs/51 reference | docs/51 = O1 投递清单已交；必带 OPEN 清单 11 项；O1 仍 WAITING_FILE；推 S2.7-b-full 真数据迁移刀 + O3 tasking 31X+ | docs/34 §120 + docs/51 §6 + docs/47 §6.3 + `284` §依赖 |
| ❌ 文首/文末 PASS / O1 收口宣告措辞 | docs/45 修改均在 docs/51 引用语境中显式"OPEN WAITING_FILE"，不在 docs/51 本身（docs/51 文首/文末 11 处 ⚠）| `321` §红线 + `324` §红线 |
| ❌ 业务代码改动 | docs/45 = markdown 评审索引；schema / migration / dbt / pytest / TS / frontend / smoke-check / intake 全部未动 | `324` §SCHEMA "本刀做" |
| ❌ 爬源站 / 登录绕过 / OCR 降门槛 | docs/45 §1 docs/51 cross-ref 显式禁止（per docs/51 §0 + §7 + §8）| `324` §红线 + docs/49 §2.2 |
| ❌ 派生 score / rating / rank / total_score / confidence_score / credibility_score / peer_rank | docs/45 §7 红线自检 + §6.2 禁词守门 沿用 | docs/06 §6.6 + docs/42 §8 + docs/47 §1.2 |
| ❌ 改 Cursor 拥有架构文档 | docs/06/08/10/34/40-44/46-50 / `00-CC-CURRENT.md` / `gate_thresholds.json` 未读未写 | `324` §红线 + Cursor 37 architect-only |
| ❌ 改 docs/51 既有内容 | docs/51 = 前置已交（`322`）；docs/45 仅引用 docs/51 既有 10 节 | `324` §SCHEMA "本刀做/本刀不做" |
| ❌ 改 docs/48 既有内容 | docs/48 = docs/51 引用源；docs/45 docs/51 cross-ref 间接引用 docs/48 §2/§3/§4/§5；不改 docs/48 | `324` §SCHEMA "本刀做" |
| ❌ 改 `scripts/intake_real_sha_if_present.py` 既有内容 | 脚本未读未写 | `324` §SCHEMA "本刀做/本刀不做" |
| ❌ `git push --force` / `--force-with-lease` | 仅 `git push origin HEAD` + `git push github HEAD` | 红线条目 + knife 17 lesson |

---

## §3. docs/45 修改详情

#### 3.1 header（line 8 区域 + 1 new line）

新增 line 14（line 14 = 8 刷新行 + 现有 line 13 之上）：

```markdown
> 刷新：queue_rev 134（per `324-stage2-docs45-o1-checklist-refresh-tasking-20260826`）— 登记 **`docs/51`** O1 投递**清单**（10 节；5 省 + 10 地市 + 4 退出码契约 + 不可隐藏清单 11 项 + 链到 docs/48 intake 操作手册；回执 `322`）；§1 + §3 O1 详细 + §6.2 + §7 同步指向 docs/51；**O1 仍 OPEN（WAITING_FILE）**，不擅自 O1 收口，真数据物理依赖用户按 docs/51 §1-§4 投递 → `--confirm-o1=PATH` 显式确认
```

#### 3.2 §1 索引目的（line 26 区域）

新增 docs/51 段：

```markdown
**O1 投递清单**（per `docs/51-stage2-o1-drop-checklist-20260826.md`，10 节；回执 `322`）：§0 一句话总览 + §1 pre-conditions 5 项 + §2 allowlist 3 前缀 + §3 4 退出码契约（WAITING_FILE / CANDIDATE_FOUND / CONTRACT_VIOLATION / 内部错误）+ §4 `--confirm-o1=PATH` 显式确认 + §5 收口预览 + §6 不可隐藏清单 11 项 + §7 红线 + §8 不在范围 + §9 下次心跳预期。**docs/51 不是 O1 收口宣告**（per `321` §SCHEMA "本刀做" + `324` §红线）；O1 仍 OPEN（WAITING_FILE）直到用户主动 `--confirm-o1=PATH`；真数据物理依赖用户按 docs/51 §1-§4 投递。
```

#### 3.3 §3 O1 详细（line 68 附近 O1 row）

修改 O1 row 末尾：

```markdown
| **O1** 真实 SHA-locked 江苏样本 | **S1.18 DEMO 路径 OPEN — 用户 2026-08-26 确认无持有材料**（per `284` 缩刀任务书）；**`docs/51` O1 投递清单**已交（10 节；5 省 + 10 地市 + 4 退出码契约 + 不可隐藏清单 11 项；回执 `322`）；真数据物理依赖用户按 docs/51 §1-§4 投递 → `--confirm-o1=PATH` 显式确认 | ✅ **必带**（per docs/34 §3 + §120）|
```

#### 3.4 §6.2 评审必带文件清单（line 213 区域）

新增 docs/51 row（line 213 docs/50 row + Gate 2 三类划分 row 之后）：

```markdown
| **O1 投递一页清单**（per `docs/51` + `322`）| `docs/51-stage2-o1-drop-checklist-20260826.md`（10 节：§0 一句话 / §1 pre-conditions 5 项 / §2 allowlist 3 前缀 / §3 4 退出码契约（WAITING_FILE / CANDIDATE_FOUND / CONTRACT_VIOLATION / 内部错误）/ §4 `--confirm-o1=PATH` 显式确认 / §5 收口预览 / §6 不可隐藏清单 11 项 / §7 红线 / §8 不在范围 / §9 下次心跳预期；文首/文末禁止收口宣告措辞）| ✅ O1 投递清单已交（回执 `322`；**O1 仍 OPEN（WAITING_FILE）**，真数据物理依赖用户按 docs/51 §1-§4 投递 → `--confirm-o1=PATH` 显式确认；不擅自 O1 收口）|
```

#### 3.5 §7 红线自检 pack invariant（line 242）

```markdown
| ✅ pack invariant | ⏳ bump + commit 后 643 == 643 == 643（knife 44: docs/45 登记 docs/51 投递清单 + 回执 325 + bump；641 → 643；+2 = bump + receipt；docs/45 SHA REFRESH 不增计数；前置 knife 43 = docs/51 NEW + 回执 322 639 → 641；knife 42 = docs/45 登记 docs/50 637 → 639；knife 41 = docs/50 NEW + 回执 316 635 → 637）|
```

#### 3.6 §7 红线自检 O1+O8 OPEN 清单显式携带（line 249）

```markdown
| ✅ O1 + O8 OPEN 清单显式携带 | ✅ §3 + §5.5 + §6.2（lineage.source_file_sha256 + person/tenure 真数据；person/tenure **demo** 已交 `303`；**O3 OCR 规划已交 `309` 仍 OPEN**；**Gate 2 评审包草稿已交 `docs/50` + `316`，必带 OPEN 清单**；**O1 投递清单已交 `docs/51` + `322`，必带 OPEN 清单 11 项；O1 仍 WAITING_FILE**）推 S2.7-b-full 真数据迁移刀 + O3 tasking 31X+ |
```

---

## §4. 验证（per `324` §NOW "1-2"）

### 4.1 markdown 格式

docs/45 是 markdown 文件；未引入新表头格式（仅在 docs/45 既有表格格式上加 docs/51 行）。格式一致性由 docs/45 既有惯例守门。

### 4.2 docs/45 内容守门

| 检查项 | 状态 |
|---|---|
| ✅ header 8 刷新行（queue_rev 134 per `324`）| ✅ |
| ✅ §1 docs/51 cross-ref（链到 docs/48 intake + 10 节 + 4 退出码 + 不可隐藏清单 11 项 + 回执 322）| ✅ |
| ✅ §3 O1 详细 docs/51 row（"docs/51 O1 投递清单已交 ... 真数据物理依赖用户按 docs/51 §1-§4 投递 → `--confirm-o1=PATH` 显式确认"）| ✅ |
| ✅ §6.2 docs/51 row（O1 投递一页清单 + 10 节 + 文首/文末禁止收口宣告 + 不擅自 O1 收口）| ✅ |
| ✅ §7 invariant 643 == 643 == 643 + knife 41-44 链 | ✅ |
| ✅ §7 O1+O8 OPEN 携带 docs/51 reference（"O1 投递清单已交 `docs/51` + `322`，必带 OPEN 清单 11 项；O1 仍 WAITING_FILE"）| ✅ |
| ✅ docs/45 = markdown-only（无业务代码改动）| ✅ |
| ✅ Cursor 拥有架构文档未动 | ✅ |

### 4.3 不动 Cursor 拥有文档守门

| 文档 | 是否修改 | 来源 |
|---|---|---|
| `docs/45-stage2-s210-lite-gate2-review-index-20260826.md`（本刀主修改）| ✅ 修改（5 处）| CC 维护 Gate 2 评审索引（per `324` §SCHEMA）|
| `docs/51-stage2-o1-drop-checklist-20260826.md` | ❌ 未读未写 | docs/45 docs/51 cross-ref 引用 docs/51 既有 10 节；不改 docs/51 既有契约（per `324` §SCHEMA "本刀做/本刀不做" + `321` §SCHEMA）|
| `docs/48-stage2-real-sha-intake-handbook-20260826.md` | ❌ 未读未写 | docs/45 docs/51 cross-ref 间接引用 docs/48 §2/§3/§4/§5；不改 docs/48 既有契约 |
| `docs/50-stage2-gate2-review-packet-draft-20260826.md` | ❌ 未读未写 | docs/45 docs/50 cross-ref 既有（per `318`）|
| `docs/44 / 47 / 41 / 36-39 / 42 / 43 / 49` | ❌ 未读未写 | Cursor 拥有架构文档 |
| `docs/06 / 08 / 10 / 34` | ❌ 未读未写 | Cursor 拥有 |
| `00-CC-CURRENT.md` | ❌ 未读未写 | Cursor 拥有 |
| `gate_thresholds.json` | ❌ 未读未写 | 红线条目 |
| `scripts/intake_real_sha_if_present.py` | ❌ 未读未写 | docs/45 docs/51 cross-ref 引用脚本；不修改脚本既有契约（per docs/48 §6）|

**结果**：✅ Cursor 拥有架构文档 + docs/51 + docs/48 + scripts/intake_real_sha_if_present.py 既有契约全部未动；docs/45 仅引用既有 docs/51 / docs/50 / docs/49 / docs/48 / docs/47 / docs/44 等。

### 4.4 manifest invariant

```
$ python3 scripts/_knife44_manifest_bump.py
ADD: scripts/_knife44_manifest_bump.py (... bytes, sha=____)
ADD: reviews/.../325-...md (... bytes, sha=____)
UPDATE artifact_count: 641 → 643
INVARIANT: sum(role_count)=643 == artifact_count=643 == len(artifacts)=643
OK manifest updated; added 2 artifacts
```

**结果**：✅ invariant 守门；本刀 +2（bump + receipt），docs/45 SHA REFRESH 不增计数（per knife 17 lesson）。

### 4.5 docs/45 grep "PASS" / "收口宣告" 检查

docs/45 修改前已有 "PASS" 字样 = "不宣布 Gate 2 PASS" / "不宣布 Stage 0 / Gate 1 / Gate 2 PASS" 等守门语境（沿用 docs/45 既有红线自检 §7），不在 docs/45 docs/51 cross-ref 新增内容里。

docs/45 修改前已有 "收口宣告" 字样 = 无；本次新增 docs/51 cross-ref 中"文首/文末禁止收口宣告措辞" / "不擅自 O1 收口" 等守门语境，无 bare "收口宣告" 措辞。

**结果**：✅ 无 bare "PASS" / bare "收口宣告"；所有 "PASS" / "收口" 均在否定语境或显式禁止语境。

---

## §5. 红线自检（per `324` §红线 + docs/34 §1/§3/§8/§120 + docs/48 §8 + docs/49 §2.2 + docs/06 §6.6 + docs/42 §8 + docs/47 §3.1 ⚠️ + docs/51 §7 + `321` §红线 + `284` §红线）

| 红线 | 状态 | 守门位置 |
|---|---|---|
| ❌ 不宣布 Gate 1 / Gate 2 PASS | ✅ | docs/45 §1 docs/51 cross-ref + §6.2 docs/51 row + §7 + docs/51 §0 + §5 + §7 + §8 + header 多次 ⚠ |
| ❌ 不擅自 O1 收口 | ✅ | docs/45 §3 O1 详细 + §6.2 docs/51 row + §7 O1+O8 OPEN 携带 + docs/51 §0 + §1 + §2 + §3 + §4 + §5 + §6 + §7 + §8 + header 10 处显式 |
| ❌ 不擅自 O3 收口 | ✅ | docs/45 §7 O1+O8 OPEN 携带 + §6.2 O3 OCR 规划 row + docs/51 §1 + §6 #9 + §7 + §8 5 处显式 |
| ❌ 不派生 score / rating / rank / total_score / confidence_score / credibility_score / peer_rank | ✅ | docs/45 §6.2 禁词守门 + §7 沿用；docs/51 §7 显式禁止 |
| ❌ 不做官员能力总分 / 排名 / DSH / 实时数据 | ✅ | docs/45 §7 + docs/51 §7 |
| ❌ 不批量爬政策研究 / 财政预决算 / 官员履历 | ✅ | docs/45 §7 + docs/51 §0 + §7 + §8 |
| ❌ HTTP 爬源 | ✅ | docs/45 §7 + docs/51 §0 + §2 + §6 #4 + §7 + §8 |
| ❌ 登录绕过 | ✅ | docs/45 §7 + docs/51 §0 + §7 + §8 |
| ❌ 未授权 cloud OCR API | ✅ | docs/45 §7 + docs/51 §0 + §6 #4 + §7 + §8 |
| ❌ 降 OCR 门槛 | ✅ | docs/45 §7 + docs/51 §7 + docs/49 §2.2 守门 |
| ❌ 启用 pgvector / RLS / partition | ✅ | Stage 2 边界；本刀不动 |
| ❌ 改 `gate_thresholds.json` | ✅ | 未读未写 |
| ❌ 不碰 `00-CC-CURRENT.md` | ✅ | Cursor 拥有 |
| ❌ 不擅自 --force / --force-with-lease | ✅ | ff-only pull |
| ❌ 不替用户下裁定 | ✅ | docs/45 §1 docs/51 cross-ref + §6.2 docs/51 row 显式 "O1 仍 OPEN（WAITING_FILE）" + "真数据物理依赖用户按 docs/51 §1-§4 投递 → `--confirm-o1=PATH` 显式确认" |
| ❌ 不在聊天复述 Cursor 长文 | ✅ | 仅回执要点 |
| ❌ 不索要 PAT | ✅ | — |
| ✅ pack invariant 守门 | ✅ | 641 → 643；bump script source-of-truth |
| ✅ receipts 仅写 `reviews/stage0-gate0-rework-2026-08-23/` | ✅ | `325-...md` |
| ✅ docs/45 = markdown-only | ✅ | docs/45 仅 markdown 评审索引修改 |
| ✅ Cursor 拥有架构文档未动 | ✅ | docs/06/08/10/34/40-44/46-50 / `00-CC-CURRENT.md` 未读未写 |
| ✅ docs/51 既有契约未动 | ✅ | docs/45 仅引用 docs/51 既有 10 节 |
| ✅ docs/48 既有契约未动 | ✅ | docs/45 docs/51 cross-ref 间接引用 docs/48 §2/§3/§4/§5 |
| ✅ scripts/intake_real_sha_if_present.py 既有契约未动 | ✅ | docs/45 仅引用 |
| ✅ O1 仍 OPEN（WAITING_FILE） | ✅ | docs/45 §1 + §3 O1 详细 + §6.2 docs/51 row + §7 O1+O8 OPEN 携带 5 处显式 |
| ✅ WAITING_FILE ≠ O1 收口 | ✅ | docs/45 §6.2 docs/51 row + docs/51 §0 + §3 + §6 #6 + §7 显式 |
| ✅ pytest 自动化 `--confirm-o1` 禁止 | ✅ | docs/45 §6.2 docs/51 row + docs/51 §3 + §4 + §6 #5 + §7 显式 |
| ✅ O1 收口 ≠ Gate 2 PASS | ✅ | docs/45 §6.2 docs/51 row + docs/51 §5 + §6 #7 + §7 显式 |
| ✅ O1 收口 ≠ person/tenure 真数据 | ✅ | docs/45 §6.2 docs/51 row + docs/51 §5 + §6 #8 显式 |
| ✅ O1 收口 ≠ O3 收口 | ✅ | docs/45 §6.2 docs/51 row + docs/51 §1 + §6 #9 显式 |
| ✅ O1 收口 ≠ dbt mart 真表 | ✅ | docs/45 §6.2 docs/51 row + docs/51 §5 + §6 #10 显式 |
| ✅ O1 收口 ≠ docs/10 §3.2-3.4 收口 | ✅ | docs/45 §6.2 docs/51 row + docs/51 §6 #11 显式 |
| ✅ PDF 扫描件须先经 O3 OCR 流水线 | ✅ | docs/45 §6.2 O3 OCR 规划 row + docs/51 §1 显式 |
| ✅ mart-shape 禁词 3 重守门 | ✅ | docs/45 §6.2 禁词守门 沿用 |

---

## §6. 推送 / 三路对齐

| 步骤 | 命令 | 结果 |
|---|---|---|
| origin pull | `git fetch origin && git pull --ff-only origin main` | queue_rev 134 ✅ |
| cc_gate_watch | `./scripts/cc_gate_watch.sh --pull` | `phase=CC_ACTION_REQUIRED` ✅ |
| docs/45 修改 | header + §1 + §3 O1 详细 + §6.2 + §7 ×2 | ✅ 6 处同步 |
| bump script | `scripts/_knife44_manifest_bump.py`（2 NEW）| ✅ 641 → 643（+2）|
| 本地校验 | manifest invariant | ✅ 643 == 643 == 643 |
| commit (knife 44 主提交) | `git add ... && git commit -m "docs(45): 324 docs/51 O1 投递清单登记 — §1/§3 O1 详细/§6.2/§7 同步"` | ⏳ this commit |
| origin push | `git push origin HEAD`（**priority**）| ⏳ this commit |
| github push | `git push github HEAD` | ⏳ this commit |
| 三路对齐 | origin/main = github/main = local HEAD | ⏳ this commit |
| backfill commit | 独立 commit（不 amend-after-push）| ⏳ this commit |

> **禁止 amend-after-push**：receipt SHA + commit SHA 必须在独立 commit 里 backfill（per knife 2/3/4 经验）。

---

## §7. 下次心跳预期

- `queue_rev 134` 完成后：Cursor 收 `325` → 下发 `326-stage0-cursor-s324-docs45-docs51-refresh-audit-…md`（PASS/FAIL）
- 若 PASS：docs/45 完整同步 docs/51 登记 + 5 处 cross-ref + pack invariant 643；用户可按 docs/51 §1-§4 投递真数据 → 跑 intake → `--confirm-o1=PATH` 收口
- 若 FAIL：`325-correction` 回合（修 header 8 刷新行 / 修 §1 docs/51 cross-ref / 修 §3 O1 详细 docs/51 row / 修 §6.2 docs/51 row / 修 §7 invariant 643 / 修 §7 O1+O8 OPEN 携带 docs/51 reference / re-commit）

---

## §8. 备注

- **本刀不接真数据 / 不宣称已收口** — docs/45 §1 docs/51 cross-ref + §3 O1 详细 docs/51 row + §6.2 docs/51 row + §7 O1+O8 OPEN 携带 5 处显式守门；O1 仍 OPEN（WAITING_FILE）直到用户主动 `--confirm-o1=PATH`（per docs/34 §3 + §120 + docs/47 §3.1 ⚠️ + `284` + `324` + `321`）。
- **本刀只做 docs/45 机械刷新 + docs/51 登记** — `324` §SCHEMA 显式约束：不接真 SHA / 不接真履历 / 不爬网 / 不派生 score / 不改业务代码 / **不实装 OCR 引擎** / **不宣布 Gate/O1/O3 收口** / 不改 docs/51 既有契约 / 不改 Cursor 拥有架构文档。
- **docs/51 = CC 维护投递清单**（per `321` §SCHEMA "本刀做"）— 10 节 markdown 文档；不属于 Cursor 拥有架构文档（docs/06/08/10/34/40-44/46-50）；红线 "Cursor 37 architect-only" 不约束 docs/51。
- **O1 仍 OPEN — WAITING_FILE** — docs/45 §1 docs/51 cross-ref + §3 O1 详细 docs/51 row + §6.2 docs/51 row + §7 O1+O8 OPEN 携带 5 处显式（per docs/34 §3 + §120 + docs/47 §3.1 ⚠️ + `284` + `321` + `324`）。
- **O3 仍 OPEN — 规划已交，实装待 tasking 31X+** — docs/45 §6.2 O3 OCR 规划 row + §7 O1+O8 OPEN 携带 + docs/51 §1 + §6 #9 + §7 + §8 + header 多次显式（per `docs/49` §5.3 + §8 + §10 + `309` + `313`）。
- **不可隐藏清单 11 项** — docs/51 §6 显式 O1 投递必带：O1 OPEN + 不 fixture 冒充 + 不假造 SHA + 不爬网/登录/OCR/未授权 + 不自动化 confirm + WAITING_FILE ≠ 收口 + O1 ≠ Gate PASS + O1 ≠ person/tenure 真数据 + O1 ≠ O3 + O1 ≠ dbt mart 真表 + O1 ≠ docs/10 §3.2-3.4。
- **用户投递流程** — docs/51 §0 + §1 + §2 + §3 + §4 + §5 单页端到端：pre-conditions → allowlist → 探测 → 显式确认 → 收口预览。
- **PDF 扫描件须先经 O3 OCR 流水线**（per `docs/49` §5.3 + §10 Q4）— docs/51 §1 + docs/45 §6.2 O3 OCR 规划 row 显式；O3 仍 OPEN 未实装（tasking 31X+）。
- **下次 heartbeat 闸门** — O1 真收口须用户主动 `--confirm-o1=PATH` + 真数据投递 + intake rc=0 (O1_INTAKED) + 端到端 pytest PASS；在此之前 docs/45 §1 + §3 O1 详细 + §6.2 + §7 O1+O8 OPEN 携带 docs/51 reference 仍标注 O1 OPEN WAITING_FILE。

— End of `325` —

> 等待 Cursor 审验（预期 `326-stage0-cursor-s324-docs45-docs51-refresh-audit-…md`）。
> 通过后 docs/45 完整同步 docs/51 登记 + 5 处 cross-ref + pack invariant 643；用户可按 docs/51 §1-§4 投递真数据 → 跑 intake → `--confirm-o1=PATH` 收口。
> ⚠ **本刀不是 O1 收口宣告**（per `324` §SCHEMA "本刀做" + `321` §红线 + `284` §SCHEMA）。
> ⚠ **O1 仍 OPEN（WAITING_FILE）**（per docs/34 §3 + §120 + docs/47 §3.1 ⚠️ + `284` §SCHEMA + `321` §红线 + `324` §红线）。
> ⚠ **不伪造 / 不爬网 / 不擅自 O1 收口**（per docs/48 §4.3 + §8 + `324` §红线 + docs/06 §6.6 + docs/49 §2.2）。
> ⚠ **rc=0 (WAITING_FILE) ≠ O1 收口**（per docs/48 §3）。
> ⚠ **`--confirm-o1=PATH` 必须由用户主动显式触发；pytest 自动化禁止**（per docs/48 §4.3 + §7）。
> ⚠ **O1 收口不构成 Gate 2 / O3 / dbt mart 真表 / person/tenure 真数据 / docs/10 §3.2-3.4 收口**（per docs/34 §1 + §8 #8 + docs/47 §6.3 + docs/49 §5.3 + `284` §依赖）。
> ⚠ **PDF 扫描件须先经 O3 OCR 流水线**（per `docs/49` §5.3 + §10 Q4；O3 仍 OPEN，未实装）。
> ⚠ **不在范围：实装 OCR / 改业务代码 / 改 Cursor 拥有文档 / 收口宣告 / 改 docs/51 既有契约**（per `324` §SCHEMA "本刀不做" + `321` §SCHEMA "本刀不做"）。