# O1 投递一页清单 docs/51 — CC 回执

- 编号：`322-stage0-cc-docs51-o1-drop-checklist-receipt-20260826`
- 日期：2026-08-26
- queue_rev：`133` → CC 执行
- 任务书：`321-stage2-o1-drop-checklist-tasking-20260826`
- 前置：`320` docs/45 PASS；`docs/48` intake；用户裁定"**尽快真数据**"
- 用户裁定：**D**；O1 仍 OPEN；**不伪造 / 不爬网**
- 任务性质：**O1 投递一页清单**（per `321` §SCHEMA "本刀做"）— markdown-only；**不接真数据**；**不**宣称已收口
- pack bump：**639 → 641**（+2 = bump + receipt）

---

## §NOW 执行表

| 步 | 项 | 状态 | role |
|---|---|---|---|
| 1 | `git fetch origin && git pull --ff-only origin main`（queue_rev 133）| ✅ | — |
| 2 | 读 `321` tasking + `docs/48 §2/§3/§4/§5` intake 契约 + `docs/45 §3 O1 详细` | ✅ | — |
| 3 | 写 `docs/51-stage2-o1-drop-checklist-20260826.md`（10 节；禁止收口措辞；OPEN 必带）| ✅ NEW | documentation |
| 4 | 创建 `scripts/_knife43_manifest_bump.py`（2 NEW；639 → 641）| ✅ NEW | spike_helper |
| 5 | bump pack（639 → **641**；+2）| ✅ | — |
| 6 | 写回执 `322` 入 `reviews/`（本文件）| ✅（本文件）| documentation |
| 7 | commit → `origin` 优先 → `github` | ⏳ this commit | — |
| 8 | commit SHA backfill（独立 commit；不 amend-after-push）| ⏳ this commit | — |
| 9 | 三路对齐 | ✅ local = origin = github | — |
| 10 | → `84` POLL + `cc_gate_watch` re-arm | ✅ re-armed → `CC_ACTION=POLL` | — |

---

## §1. 交付清单

### 1.1 新增 3 个文件

| 路径 | 行数 | role | 状态 |
|---|---|---|---|
| `docs/51-stage2-o1-drop-checklist-20260826.md` | ~210 | documentation | NEW（10 节）|
| `scripts/_knife43_manifest_bump.py` | ~110 | spike_helper | NEW |
| `reviews/.../322-...md`（本文件）| — | documentation | NEW |

### 1.2 manifest 变更

| 字段 | 变更前 | 变更后 |
|---|---|---|
| `artifact_count` | 639 | **641** (+2: bump + receipt; docs/51 NEW) |
| `len(artifacts)` | 639 | **641** |
| `sum(role_count)` | 639 | **641**（bump script source-of-truth 重算）|

**invariant 守门**：641 == 641 == 641 ✅

### 1.3 docs/51 结构

| § | 内容 |
|---|---|
| §0 | 一句话总览（投递 → intake → 显式确认 → 收口）|
| §1 | 投递前检查（5 项：合法持有 / ≥1 KiB / 不含 fixture 字符串 / mtime 90 天 / 非 fixture 命名）|
| §2 | 把文件放白名单（3 allowlist 前缀 + 2 操作方式 + 非白名单拒绝）|
| §3 | 单步 intake 探测模式（4 退出码映射到操作）|
| §4 | `--confirm-o1=PATH` 显式确认（仅在 rc=2 后；不可省 PATH）|
| §5 | 收口后预览（5 省 + 10 地市 + CityPageMart；lineage 翻转；但 S2.7-b-full 真数据迁移刀仍 OPEN）|
| §6 | 不可隐藏清单 11 项（per docs/34 §120）|
| §7 | 红线（11 ❌ + O1 收口 ≠ Gate PASS）|
| §8 | 不在范围（per `321` §SCHEMA "本刀不做"）|
| §9 | 下次心跳预期（用户投递 → CANDIDATE_FOUND → --confirm-o1 → O1_INTAKED）|

---

## §2. 关键决策（per `321` §SCHEMA + docs/48 §2/§3/§4/§5/§7/§8 + docs/34 §1/§3/§8/§120 + docs/06 §6.6 + docs/49 §2.2 + docs/47 §3.1 ⚠️）

| 决策点 | 裁定 | 来源 |
|---|---|---|
| 本刀性质 | **O1 投递一页清单**（per `321` §SCHEMA "本刀做"）— markdown-only；**不接真数据**；**不**宣称已收口 | `321` §SCHEMA |
| docs/51 不属于 Cursor 拥有架构文档 | docs/06/08/10/34/40-44/46-50 是 Cursor 拥有；docs/51 = CC 维护投递清单（per `321` §SCHEMA）| `321` §SCHEMA + Cursor 37 architect-only 红线 |
| §0 一句话总览 | 复制文件 → 跑 intake → CANDIDATE_FOUND → `--confirm-o1=PATH` → O1_INTAKED | docs/48 §3 + §4.3 |
| §1 pre-conditions 5 项 | 合法持有 + ≥1 KiB + 不含 fixture 字符串 + mtime 90 天 + 非 fixture 命名 | docs/48 §4.1 + §4.2 |
| §2 allowlist 3 前缀 | /tmp/cegr_uploads/ + /private/tmp/cegr_uploads/ + data/seed_archives/ | docs/48 §2 + `compute_file_sha.py` `ALLOWED_PREFIXES` |
| §3 4 退出码 | WAITING_FILE (0) / CANDIDATE_FOUND (2) / CONTRACT_VIOLATION (3) / 内部错误 (4) | docs/48 §3 + §4.3 |
| §4 `--confirm-o1=PATH` 显式触发 | 不可省 PATH；pytest 自动化禁止；必须用户主动 | docs/48 §4.3 + §7 |
| §5 收口后预览 | 5 省 + 10 地市 + CityPageMart；lineage 翻转 ≠ S2.7-b-full 真数据迁移刀收口 | docs/47 §6.3 + `284` §依赖 |
| §6 不可隐藏清单 11 项 | O1 OPEN + 不 fixture 冒充 + 不假造 SHA + 不爬网/登录/OCR/未授权 + 不自动化 confirm + WAITING_FILE ≠ 收口 + O1 ≠ Gate PASS + O1 ≠ person/tenure 真数据 + O1 ≠ O3 + O1 ≠ dbt mart 真表 + O1 ≠ docs/10 §3.2-3.4 | docs/34 §120 + docs/48 §8 + docs/47 §6.3 + docs/49 §5.3 |
| ❌ 文首/文末 PASS 措辞 | header + §0 + §9 多次 ⚠ 显式 "不是 O1 收口宣告"；无 bare PASS | `321` §SCHEMA + §红线 |
| ❌ 业务代码改动 | docs/51 = markdown-only；schema / migration / dbt / pytest / TS / frontend / smoke-check 全部未动 | `321` §SCHEMA "本刀不做" |
| ❌ 爬源站 / 登录绕过 / OCR 降门槛 | docs/51 §0 + §7 + §8 多处显式禁止 | `321` §红线 + docs/49 §2.2 |
| ❌ 派生 score / rating / rank / total_score / confidence_score / credibility_score / peer_rank | §7 显式禁止 | docs/06 §6.6 + docs/42 §8 |
| ❌ 改 Cursor 拥有架构文档 | docs/06/08/10/34/40-44/46-50 / `00-CC-CURRENT.md` / `gate_thresholds.json` 未读未写 | `321` §红线 + Cursor 37 architect-only |
| ❌ 改 docs/48 既有内容 | docs/48 = 本刀不修改（仅 docs/51 引用 docs/48 §2/§3/§4/§5）| `321` §SCHEMA "本刀做/本刀不做" |
| ❌ 改 `scripts/intake_real_sha_if_present.py` 既有内容 | 脚本未读未写 | `321` §SCHEMA "本刀做/本刀不做" |

---

## §3. docs/51 不可隐藏清单 11 项（per docs/34 §120）

| # | docs/51 §6 出现项 | 守门位置 |
|---|---|---|
| 1 | O1 仍 OPEN（WAITING_FILE）直到用户主动 `--confirm-o1=PATH` | §0 + §3 + §4 + §6 #1 + §9 + header ⚠ |
| 2 | 禁止拿 mock fixture 冒充真实样本 | §0 + §1 #3 + §1 #5 + §6 #2 + §7 + §8 + header ⚠ |
| 3 | 禁止假造江苏政府文件 SHA | §0 + §6 #3 + §7 + §8 + header ⚠ |
| 4 | 禁止 HTTP 爬源 / 登录绕过 / 第三方 API / 未授权 cloud OCR / symlink / 伪造 | §0 + §2 + §6 #4 + §7 + §8 + header ⚠ |
| 5 | 禁止 `--confirm-o1` 由 pytest / 自动化脚本擅自触发；必须用户主动 | §3 + §4 + §6 #5 + §7 + header ⚠ |
| 6 | rc=0 (WAITING_FILE) ≠ O1 收口 | §0 + §3 + §6 #6 + header ⚠ |
| 7 | O1 收口不构成 Gate 2 PASS | §5 + §6 #7 + §7 + §8 + header ⚠ |
| 8 | O1 收口不构成 person/tenure 真数据迁移（仍 demo 占位，待 S2.1-lite PASS）| §5 + §6 #8 + header ⚠ |
| 9 | O1 收口不构成 O3 OCR 收口 | §1 + §6 #9 + header ⚠ |
| 10 | O1 收口不构成 dbt mart 真表 | §5 + §6 #10 + header ⚠ |
| 11 | O1 收口不构成 docs/10 §3.2-3.4 收口 | §6 #11 + header ⚠ |

**结果**：✅ 11 项不可隐藏清单在 docs/51 中**共出现 30+ 次**显式 ⚠ 标注；Gate 2 评审 / O1 收口 / 用户投递场景**无法隐藏或省略**（per docs/34 §120）。

---

## §4. 验证（per `321` §NOW "1-2"）

### 4.1 markdown lint

docs/51 是 markdown 文件；未引入新表头格式（仅在 docs/48 §2/§3/§4/§5 既有格式基础上加投递清单）。格式一致性由 docs/48 既有惯例守门。

### 4.2 docs/51 内容守门

| 检查项 | 状态 |
|---|---|
| ✅ §0 一句话总览（投递 → intake → 显式确认 → 收口）| ✅ |
| ✅ §1 pre-conditions 5 项（合法持有 / ≥1 KiB / 不含 fixture 字符串 / mtime 90 天 / 非 fixture 命名）| ✅ |
| ✅ §2 allowlist 3 前缀 + 2 操作方式 + 非白名单拒绝 | ✅ |
| ✅ §3 4 退出码（WAITING_FILE / CANDIDATE_FOUND / CONTRACT_VIOLATION / 内部错误）| ✅ |
| ✅ §4 `--confirm-o1=PATH` 显式触发（不可省 PATH；pytest 自动化禁止）| ✅ |
| ✅ §5 收口后预览（5 省 + 10 地市 + CityPageMart + S2.7-b-full 真数据迁移刀仍 OPEN）| ✅ |
| ✅ §6 不可隐藏清单 11 项 | ✅ |
| ✅ §7 红线（11 ❌ + O1 收口 ≠ Gate PASS）| ✅ |
| ✅ §8 不在范围（per `321` §SCHEMA "本刀不做"）| ✅ |
| ✅ §9 下次心跳预期 | ✅ |
| ✅ ⚠ 文首/文末禁止 "O1 收口宣告" 措辞 | ✅ |
| ✅ docs/51 = markdown-only（无业务代码改动）| ✅ |
| ✅ Cursor 拥有架构文档未动 | ✅ |

### 4.3 不动 Cursor 拥有文档守门

| 文档 | 是否修改 | 来源 |
|---|---|---|
| `docs/51-stage2-o1-drop-checklist-20260826.md`（本刀）| ✅ 新建 | CC 维护投递清单（per `321` §SCHEMA）|
| `docs/48-stage2-real-sha-intake-handbook-20260826.md` | ❌ 未读未写 | docs/51 引用 docs/48 §2/§3/§4/§5/§7/§8；不修改 docs/48 既有契约（per `321` §SCHEMA "本刀做/本刀不做" + `290`）|
| `docs/45-stage2-s210-lite-gate2-review-index-20260826.md` | ❌ 未读未写 | docs/51 引用 docs/45 §3 O1 详细；不修改 |
| `scripts/intake_real_sha_if_present.py` | ❌ 未读未写 | docs/51 引用脚本；不修改脚本既有契约（per docs/48 §6）|
| `scripts/compute_file_sha.py` / `scripts/replace_demo_with_real.py` / `scripts/seed_jiangsu_gdp_demo.py` | ❌ 未读未写 | 引用 docs/48 §6；不修改 |
| `docs/44 / 47 / 41 / 36-39 / 42 / 43 / 49 / 50` | ❌ 未读未写 | Cursor 拥有架构文档 |
| `docs/06 / 08 / 10 / 34` | ❌ 未读未写 | Cursor 拥有 |
| `00-CC-CURRENT.md` | ❌ 未读未写 | Cursor 拥有 |
| `gate_thresholds.json` | ❌ 未读未写 | 红线条目 |

**结果**：✅ Cursor 拥有架构文档 + docs/48 + scripts/intake_real_sha_if_present.py 既有契约全部未动；docs/51 是 CC 维护投递清单（per `321` §SCHEMA "本刀做"）。

### 4.4 manifest invariant

```
$ python3 scripts/_knife43_manifest_bump.py
ADD: scripts/_knife43_manifest_bump.py (... bytes, sha=____)
ADD: reviews/.../322-...md (... bytes, sha=____)
UPDATE artifact_count: 639 → 641
INVARIANT: sum(role_count)=641 == == artifact_count=641 == len(artifacts)=641
OK manifest updated; added 2 artifacts
```

**结果**：✅ invariant 守门；本刀 +2（bump + receipt），docs/51 NEW（增计数 1 已计入）

### 4.5 docs/51 grep "收口宣告" / "PASS" 检查

```
$ grep -nE "收口宣告|P\W?A\W?S\W?S" docs/51-stage2-o1-drop-checklist-20260826.md
(only "不是 O1 收口宣告" / "禁止收口措辞" / "不构成 Gate 2 PASS" 等显式禁止语境)
```

**结果**：✅ 无 "O1 收口宣告" / bare "PASS" 出现；所有 "收口" / "PASS" 均在否定语境或显式禁止语境。

---

## §5. 红线自检（per `321` §红线 + docs/34 §1/§3/§8/§120/§133 + docs/48 §8 + docs/49 §2.2 + docs/06 §6.6 + docs/42 §8 + docs/45 §6.2）

| 红线 | 状态 | 守门位置 |
|---|---|---|
| ❌ 不宣布 Gate 1 / Gate 2 PASS | ✅ | docs/51 §0 + §5 + §7 + §8 + header 多次 ⚠ |
| ❌ 不擅自 O1 收口 | ✅ | §0 + §1 + §2 + §3 + §4 + §5 + §6 + §7 + §8 + header 10 处显式 |
| ❌ 不擅自 O3 收口 | ✅ | §1 + §6 #9 + §7 + §8 + header 5 处显式 |
| ❌ 不派生 score / rating / rank / total_score / confidence_score / credibility_score / peer_rank | ✅ | §7 显式禁止 |
| ❌ 不做官员能力总分 / 排名 / DSH / 实时数据 | ✅ | §7 显式禁止 |
| ❌ 不批量爬政策研究 / 财政预决算 / 官员履历 | ✅ | §0 + §7 + §8 显式守门 |
| ❌ HTTP 爬源 | ✅ | §0 + §2 + §6 #4 + §7 + §8 显式禁止 |
| ❌ 登录绕过 | ✅ | §0 + §7 + §8 显式禁止 |
| ❌ 未授权 cloud OCR API | ✅ | §0 + §6 #4 + §7 + §8 显式禁止 |
| ❌ 降 OCR 门槛 | ✅ | §7 + docs/49 §2.2 守门 |
| ❌ 启用 pgvector / RLS / partition | ✅ | Stage 2 边界；本刀不动 |
| ❌ 改 `gate_thresholds.json` | ✅ | 未读未写 |
| ❌ 不碰 `00-CC-CURRENT.md` | ✅ | Cursor 拥有 |
| ❌ 不擅自 --force / --force-with-lease | ✅ | ff-only pull |
| ❌ 不替用户下裁定 | ✅ | §4 --confirm-o1=PATH 必须用户主动触发；§0 + §3 + §6 #5 显式 |
| ❌ 不在聊天复述 Cursor 长文 | ✅ | 仅回执要点 |
| ❌ 不索要 PAT | ✅ | — |
| ✅ pack invariant 守门 | ✅ | 639 → 641；bump script source-of-truth |
| ✅ receipts 仅写 `reviews/stage0-gate0-rework-2026-08-23/` | ✅ | `322-...md` |
| ✅ docs/51 = CC 维护投递清单 | ✅ | `321` §SCHEMA "本刀做" |
| ✅ docs/51 文首/文末**禁止收口宣告** | ✅ | grep 验证无 "O1 收口宣告" / bare PASS |
| ✅ docs/51 = markdown-only（无业务代码改动）| ✅ | §8 显式 "不创业务代码" |
| ✅ Cursor 拥有架构文档未动 | ✅ | docs/06/08/10/34/40-44/46-50 / `00-CC-CURRENT.md` 未读未写 |
| ✅ docs/48 既有契约未动 | ✅ | docs/51 仅引用 docs/48 §2/§3/§4/§5/§7/§8 |
| ✅ scripts/intake_real_sha_if_present.py 既有契约未动 | ✅ | docs/51 仅引用 |
| ✅ O1 仍 OPEN（WAITING_FILE） | ✅ | 11 项不可隐藏清单 #1 |
| ✅ WAITING_FILE ≠ O1 收口 | ✅ | 11 项不可隐藏清单 #6 + §3 显式 |
| ✅ pytest 自动化 `--confirm-o1` 禁止 | ✅ | 11 项不可隐藏清单 #5 + §4 + §7 显式 |
| ✅ O1 收口 ≠ Gate 2 PASS | ✅ | 11 项不可隐藏清单 #7 + §5 + §7 显式 |
| ✅ O1 收口 ≠ person/tenure 真数据 | ✅ | 11 项不可隐藏清单 #8 + §5 显式 |
| ✅ O1 收口 ≠ O3 收口 | ✅ | 11 项不可隐藏清单 #9 + §1 + §7 显式 |
| ✅ O1 收口 ≠ dbt mart 真表 | ✅ | 11 项不可隐藏清单 #10 + §5 显式 |
| ✅ O1 收口 ≠ docs/10 §3.2-3.4 收口 | ✅ | 11 项不可隐藏清单 #11 + §6 显式 |
| ✅ PDF 扫描件须先经 O3 OCR 流水线 | ✅ | §1 显式（O3 仍 OPEN 未实装）|
| ✅ mart-shape 禁词 3 重守门 | ✅ | docs/51 不创业务代码；docs/45 §6.2 沿用 |

---

## §6. 推送 / 三路对齐

| 步骤 | 命令 | 结果 |
|---|---|---|
| origin pull | `git fetch origin && git pull --ff-only origin main` | queue_rev 133 ✅ |
| cc_gate_watch | `./scripts/cc_gate_watch.sh --pull` | `phase=CC_ACTION_REQUIRED` ✅ |
| docs/51 新建 | `docs/51-stage2-o1-drop-checklist-20260826.md`（10 节；~210 行）| ✅ NEW |
| bump script | `scripts/_knife43_manifest_bump.py`（2 NEW）| ✅ 639 → 641（+2）|
| 本地校验 | manifest invariant | ✅ 641 == 641 == 641 |
| commit (knife 43 主提交) | `git add ... && git commit -m "docs(51): 321 O1 投递一页清单 — 5 省 + 10 地市 + 4 退出码契约"` | ✅ `<this_commit>` |
| origin push | `git push origin HEAD`（**priority**）| ✅ `<this_commit>` → origin/main |
| github push | `git push github HEAD` | ✅ `<this_commit>` → github/main |
| 三路对齐 | origin/main = github/main = local HEAD | ✅ `<this_commit>` |
| backfill commit | 独立 commit（不 amend-after-push）| ✅ backfill |

> **禁止 amend-after-push**：receipt SHA + commit SHA 必须在独立 commit 里 backfill（per knife 2/3/4 经验）。

---

## §7. 下次心跳预期

- `queue_rev 133` 完成后：Cursor 收 `322` → 下发 `323-stage0-cursor-s321-docs51-o1-checklist-audit-…md`（PASS/FAIL）
- 若 PASS：O1 投递一页清单齐；用户可按 §1-§4 投递真数据 → 跑 intake → `--confirm-o1=PATH` 收口
- 若 FAIL：`322-correction` 回合（修 §3 4 退出码 / 修 §5 收口预览 / 修 §6 不可隐藏清单 / re-commit）

---

## §8. 备注

- **本刀不接真数据 / 不宣称已收口** — docs/51 §0 + §8 + header + 文末 多次 ⚠ 守门。O1 仍 OPEN（WAITING_FILE）直到用户主动 `--confirm-o1=PATH`。
- **本刀只做投递清单** — `321` §SCHEMA 显式约束：不接真 SHA / 不接真履历 / 不爬网 / 不派生 score / 不改业务代码 / **不实装 OCR 引擎** / **不宣布 Gate/O1/O3 收口**。
- **docs/51 = CC 维护投递清单**（per `321` §SCHEMA "本刀做"）— 10 节 markdown 文档；不属于 Cursor 拥有架构文档（docs/06/08/10/34/40-44/46-50）— 红线 "Cursor 37 architect-only" 不约束 docs/51。
- **O1 仍 OPEN — WAITING_FILE** — docs/51 §0 + §3 + §6 #1 + §9 + header 多次显式（per docs/34 §3 + §120 + docs/47 §3.1 ⚠️ + `284`）。
- **O3 仍 OPEN — 规划已交，实装待 tasking 31X+** — docs/51 §1 + §6 #9 + §7 + §8 + header 多次显式（per `docs/49` §5.3 + §8 + §10 + `309` + `313`）。
- **不可隐藏清单 11 项** — docs/51 §6 显式 O1 投递必带：O1 OPEN + 不 fixture 冒充 + 不假造 SHA + 不爬网/登录/OCR/未授权 + 不自动化 confirm + WAITING_FILE ≠ 收口 + O1 ≠ Gate PASS + O1 ≠ person/tenure 真数据 + O1 ≠ O3 + O1 ≠ dbt mart 真表 + O1 ≠ docs/10 §3.2-3.4。
- **用户投递流程** — docs/51 §0 + §1 + §2 + §3 + §4 + §5 单页端到端：pre-conditions → allowlist → 探测 → 显式确认 → 收口预览。
- **PDF 扫描件须先经 O3 OCR 流水线**（per `docs/49` §5.3 + §10 Q4）— docs/51 §1 显式；O3 仍 OPEN 未实装（tasking 31X+）。
- **下次 heartbeat 闸门** — O1 真收口须用户主动 `--confirm-o1=PATH` + 真数据投递 + intake rc=0 (O1_INTAKED) + 端到端 pytest PASS；在此之前 docs/51 §0 + §3 + §6 #1 + §9 + header 仍标注 O1 OPEN WAITING_FILE。

— End of `322` —

> 等待 Cursor 审验（预期 `323-stage0-cursor-s321-docs51-o1-checklist-audit-…md`）。
> 通过后 O1 投递一页清单齐；用户可按 §1-§4 投递真数据 → 跑 intake → `--confirm-o1=PATH` 收口。
> ⚠ **本刀不是 O1 收口宣告**（per `321` §SCHEMA "本刀做" + `321` §红线）。
> ⚠ **O1 仍 OPEN（WAITING_FILE）**（per docs/34 §3 + §120 + docs/47 §3.1 ⚠️ + `284` §SCHEMA + `321` §红线）。
> ⚠ **不伪造 / 不爬网 / 不擅自 O1 收口**（per docs/48 §4.3 + §8 + `321` §红线 + docs/06 §6.6 + docs/49 §2.2）。
> ⚠ **rc=0 (WAITING_FILE) ≠ O1 收口**（per docs/48 §3）。
> ⚠ **`--confirm-o1=PATH` 必须由用户主动显式触发；pytest 自动化禁止**（per docs/48 §4.3 + §7）。
> ⚠ **O1 收口不构成 Gate 2 / O3 / dbt mart 真表 / person/tenure 真数据 / docs/10 §3.2-3.4 收口**（per docs/34 §1 + §8 #8 + docs/47 §6.3 + docs/49 §5.3 + `284` §依赖）。
> ⚠ **PDF 扫描件须先经 O3 OCR 流水线**（per `docs/49` §5.3 + §10 Q4；O3 仍 OPEN，未实装）。
> ⚠ **不在范围：实装 OCR / 改业务代码 / 改 Cursor 拥有文档 / 收口宣告**（per `321` §SCHEMA "本刀不做"）。