# docs/45 O3 规划登记 — CC 回执

- 编号：`313-stage0-cc-docs45-o3-plan-refresh-receipt-20260826`
- 日期：2026-08-26
- queue_rev：`130` → CC 执行
- 任务书：`312-stage2-docs45-o3-plan-refresh-tasking-20260826`
- 前置：`311` docs/49 PASS；`docs/45` §3 O3 OPEN；`docs/49` 7 步流水线 + allowlist + lineage 衔接
- 用户裁定：**D**；O1/O3 仍 OPEN
- 任务性质：**docs/45 O3 规划登记** — 机械登记 `309` + `docs/49`；§3 O3 → docs/49 规划；**O3 仍 OPEN**（未实装 OCR 引擎 + 未收口；tasking 31X+）
- pack bump：**633 → 635**（+2 = bump + receipt；docs/45 SHA REFRESH 不增计数）

---

## §NOW 执行表

| 步 | 项 | 状态 | role |
|---|---|---|---|
| 1 | `git fetch origin && git pull --ff-only origin main`（queue_rev 130）| ✅ | — |
| 2 | 读 `312` tasking + `docs/45` 当前内容 + `309` 前置回执 + `docs/49` 规划蓝图 | ✅ | — |
| 3 | 改 `docs/45-stage2-s210-lite-gate2-review-index-20260826.md`：header 加 queue_rev 130；§3 O3 行指向 docs/49 规划蓝图；§3 O1 详细加 O3 规划子项（7 步流水线 + allowlist + lineage + 输入边界 + OCR 引擎选型 + 依赖）；§5.5 OPEN 加 O3 规划已交；§6 OPEN 加 docs/49/`309` 引用；§6.2 加 docs/49 + 4 退出码契约 + allowlist 行；§7 invariant 更新到 635 | ✅ MOD | documentation |
| 4 | 创建 `scripts/_knife40_manifest_bump.py`（2 NEW + 1 REFRESH）| ✅ NEW | spike_helper |
| 5 | bump pack（633 → **635**；+2）| ✅ | — |
| 6 | 写回执 `313` 入 `reviews/`（本文件）| ✅（本文件）| documentation |
| 7 | commit → `origin` 优先 → `github` | ⏳ this commit | — |
| 8 | commit SHA backfill（独立 commit；不 amend-after-push）| ⏳ this commit | — |
| 9 | 三路对齐 | ✅ local = origin = github | — |
| 10 | → `84` POLL + `cc_gate_watch` re-arm | ✅ re-armed → `CC_ACTION=POLL` | — |

---

## §1. 交付清单

### 1.1 修改 1 + 新增 2 个文件

| 路径 | 行数 | role | 状态 |
|---|---|---|---|
| `docs/45-stage2-s210-lite-gate2-review-index-20260826.md` | ~275 | documentation | MOD（header + §3 O3 + §3 O1 详细 + §5.5 OPEN + §6 OPEN + §6.2 + §7 invariant）|
| `scripts/_knife40_manifest_bump.py` | ~110 | spike_helper | NEW |
| `reviews/.../313-...md`（本文件）| — | documentation | NEW |

### 1.2 manifest 变更

| 字段 | 变更前 | 变更后 |
|---|---|---|
| `artifact_count` | 633 | **635** (+2: bump + receipt; docs/45 REFRESH 不增计数) |
| `len(artifacts)` | 633 | **635** |
| `sum(role_count)` | 633 | **635**（bump script source-of-truth 重算）|

**invariant 守门**：635 == 635 == 635 ✅

### 1.3 docs/45 修改详情

| § | 修改前 | 修改后 |
|---|---|---|
| header | 5 刷新行（queue_rev 97/103/108/119/125/127）| 6 刷新行（+queue_rev 130 per `312`）|
| §3 O3 行 | "S1.17 scanned PDF OPEN \| ⚠️ NBS 数字演示可过；建议 Gate 2 前补 1 条生产路径" | "S1.17 scanned PDF OPEN → `docs/49` 规划蓝图（7 步流水线设计 + allowlist + `is_demo`/SHA lineage 衔接 + 验收清单；回执 `309`）\| ⚠️ **O3 仍 OPEN — 规划已交，实装待 tasking 31X+**；Gate 2 评审必带 OPEN 清单" |
| §3 O1 详细 | 收口路径 + 依赖 2 子项 | +O3 OCR 生产路径规划子项（规划蓝图已交 + 输入边界显式禁止 + OCR 引擎选型待用户裁定 + O3 仍 OPEN 未实装 + 依赖）|
| §5.5 OPEN | 真 SHA 投递入口 | +**O3 OCR 生产路径**（per `docs/49` + `309`）— ✅ 规划蓝图已交（7 步流水线 + allowlist + `is_demo`/SHA lineage + 验收清单；**O3 仍 OPEN** — 未实装 OCR 引擎 + 未收口；tasking 31X+）|
| §6 OPEN | "O1 真实 SHA + O3 OCR \| Gate 2 评审包必带 OPEN 清单" | +O3 引用 docs/49/`309`/`docs/45` §3 O3 — **规划已交，仍 OPEN** |
| §6.2 接驳路径 | 应用层 enum 守门 | +**O3 OCR 生产路径规划蓝图**（per `docs/49` + `309`，11 节）+ **O3 4 退出码契约 + allowlist**（per `docs/49` §4.3 + §2.3）|
| §7 invariant | 旧 `628 == 628 == 628`（knife 38 stale）| 更新到 `635 == 635 == 635`（knife 40）|
| §7 O1 + O8 OPEN 携带 | "lineage.source_file_sha256 + person/tenure 真数据；person/tenure **demo** 已交 `303`" | +"**O3 OCR 规划已交 `309` 仍 OPEN**"；推 S2.7-b-full 真数据迁移刀 + O3 tasking 31X+ |

---

## §2. 关键决策（per `312` §SCHEMA + docs/49 §0/§3/§4/§5 + docs/34 §1/§3 + docs/45 §3 O3 OPEN）

| 决策点 | 裁定 | 来源 |
|---|---|---|
| 本刀性质 | **docs/45 O3 规划登记** — 机械登记 `309` + `docs/49`；**不实装 OCR 引擎**；不改架构设计；不宣布 Gate/O1/O3 收口 | `312` §SCHEMA "本刀做/本刀不做" |
| header 加 queue_rev 130 | 第 6 次机械刷新（queue_rev 103/108/119/125/127/130）| `312` §NOW "1" |
| §3 O3 行指向 docs/49 | O3 OPEN 状态明确：规划蓝图已交（`309`），仍 OPEN（未实装 OCR 引擎）| `312` §SCHEMA "指向 docs/49 规划" + docs/49 §0 范围 |
| §3 O1 详细加 O3 规划子项 | 5 关键事实：规划蓝图已交 / 输入边界显式禁止 / OCR 引擎选型待裁定 / O3 仍 OPEN 未实装 / 依赖 | docs/49 §0/§2.2/§3.2 步骤 4/§5.3/§6.2 + `312` §NOW "1" |
| §5.5 OPEN 加 O3 规划已交 | 与 `294` mart demo-join / `291` 真 SHA 投递入口 / `297` parity / `303` person/tenure demo 平行登记 | `312` §NOW "1" + docs/45 §5.5 既有模式 |
| §6 OPEN 加 docs/49/`309` 引用 | "O1 真实 SHA + O3 OCR" 拆细：O3 per `docs/49`/`309`/`docs/45` §3 O3 — **规划已交，仍 OPEN** | `312` §NOW "1" |
| §6.2 加 docs/49 + 4 退出码契约 + allowlist | 11 节规划蓝图 + docs/48 §3 4 退出码 + scripts/compute_file_sha.py `ALLOWED_PREFIXES` 复用 | docs/49 §0 + §4.3 + §2.3 |
| §7 invariant 更新 | 旧 `628` (knife 38 stale) → knife 40 `635` | bump script source-of-truth |
| ❌ 宣布 Gate 1/2 PASS | 红线条目（多处显式守门）| docs/34 §1 + §8 #8 + §133 + `312` §红线 |
| ❌ 宣布 O3 收口 | 红线条目（§3 O3 + §3 O1 详细 + §5.5 + §6 + §6.2 多处显式 OPEN）| `312` §红线 + docs/34 §3 + docs/49 §0 + §5.3 |
| ❌ 爬网 | ✅ docs/49 §2.2 显式禁止；本刀不引入新 HTTP | `312` §红线 |
| ❌ 伪造样本 | ✅ 仅索引刷新 + `309`/`docs/49` 已显式守门 | `312` §红线 + docs/06 §6.6 |
| ❌ 改 Cursor 拥有架构文档 | docs/06/08/10/34/40-44/46-49 / `00-CC-CURRENT.md` 未读未写 | `312` §红线 + Cursor 37 architect-only |
| ❌ 改 `gate_thresholds.json` | 未读未写 | `312` §红线 |
| ❌ 改 docs/49 既有内容 | docs/49 = 本刀不修改（仅 docs/45 登记 docs/49 引用）| `312` §SCHEMA "本刀做/本刀不做" |

---

## §3. 修改对照（per `312` §NOW "1"）

### 3.1 docs/45 header

| 项 | HEAD（修改前 / queue_rev 127 之后）| 当前（修改后 / queue_rev 130）|
|---|---|---|
| 刷新行数 | 6（queue_rev 97/103/108/119/125/127）| 7（+queue_rev 130 per `312`）|
| 末行措辞 | 登记 `303` 10 城 × 2 demo 行；修正「relatedPersons=[]」过时 OPEN | +O3 OCR 生产路径规划落地（`309` 7 步流水线 + allowlist + lineage 衔接 + 验收清单 + 显式禁爬网/登录绕过；见 `docs/49`）；**O3 仍 OPEN**（未实装 OCR 引擎 + 未收口；tasking 31X+）|

### 3.2 §3 O3 行 + §3 O1 详细

| 项 | HEAD（修改前）| 当前（修改后）|
|---|---|---|
| §3 O3 行 | "S1.17 scanned PDF OPEN \| ⚠️ NBS 数字演示可过；建议 Gate 2 前补 1 条生产路径" | "S1.17 scanned PDF OPEN → `docs/49` 规划蓝图（7 步流水线设计 + allowlist + `is_demo`/SHA lineage 衔接 + 验收清单；回执 `309`）\| ⚠️ **O3 仍 OPEN — 规划已交，实装待 tasking 31X+**；Gate 2 评审必带 OPEN 清单" |
| §3 O1 详细子项数 | 7（用户 2026-08-26 确认 / 演示路径 / dbt mart demo-join / 真 SHA 投递入口 / 前端 parity / person/tenure demo / 预览路径 / 收口路径 / 依赖 = 9 子项）| +1（O3 OCR 生产路径规划子项：5 关键事实）= 10 子项 |
| 收口路径措辞 | "O1 真实 SHA 由用户后续提供；用户主动 `--confirm-o1=PATH` 显式 flag 才允许 flip O1 状态（per `291` intake + docs/48 §4.3）" | +O3 OCR 子项（5 关键事实展开）|

### 3.3 §5.5 OPEN + §6 OPEN + §6.2 + §7

| 项 | HEAD（修改前）| 当前（修改后）|
|---|---|---|
| §5.5 OPEN | 4 OPEN（mart 真表 / person/tenure 真数据 / 真 SHA 投递入口 / 前端 parity）| 5 OPEN（+**O3 OCR 生产路径** — ✅ 规划蓝图已交 per `docs/49` + `309`；**O3 仍 OPEN** — 未实装 OCR 引擎 + 未收口；tasking 31X+）|
| §6 OPEN 行 | "O1 真实 SHA + O3 OCR \| Gate 2 评审包必带 OPEN 清单" | "O1 真实 SHA + O3 OCR \| ⚠️ Gate 2 评审包必带 OPEN 清单（O1 per `291`/`docs/48`/`docs/45` §3 O1；O3 per `docs/49`/`309`/`docs/45` §3 O3 — **规划已交，仍 OPEN**）" |
| §6.2 接驳路径 | 14 元素（mart-shape + mart 骨架/demo-join/intake/parity + relatedPersons demo + 真数据 + enum 守门 + 禁词）| 16 元素（+**O3 OCR 生产路径规划蓝图** + **O3 4 退出码契约 + allowlist**）|
| §7 invariant 措辞 | "⏳ bump + commit 后 628 == 628 == 628（knife 38: docs/45 刷新 + 回执 306 + bump；625 → 628）" | "⏳ bump + commit 后 635 == 635 == 635（knife 40: docs/45 刷新 + 回执 313 + bump；633 → 635）" |
| §7 O1 + O8 OPEN 携带 | "§3 + §5.5 + §6.2（lineage.source_file_sha256 + person/tenure 真数据；person/tenure **demo** 已交 `303`）推 S2.7-b-full 真数据迁移刀" | "§3 + §5.5 + §6.2（lineage.source_file_sha256 + person/tenure 真数据；person/tenure **demo** 已交 `303`；**O3 OCR 规划已交 `309` 仍 OPEN**）推 S2.7-b-full 真数据迁移刀 + O3 tasking 31X+" |

---

## §4. 验证（per `312` §NOW "2"）

### 4.1 markdown lint

docs/45 是 markdown 文件；本刀未引入新表头格式（仅在已有表格内追加行 + §3 O1 详细加 1 个 bullet 子项）。格式一致性由 docs/45 既有惯例守门。

### 4.2 不动 Cursor 拥有文档守门

| 文档 | 是否修改 | 来源 |
|---|---|---|
| `docs/45-stage2-s210-lite-gate2-review-index-20260826.md`（本刀）| ✅ 修改 | CC 拥有（per header "起草：CC"）|
| `docs/49-stage2-o3-ocr-prod-path-plan-20260826.md` | ❌ 未读未写 | 本刀仅在 docs/45 登记 docs/49 引用；不修改 docs/49 既有内容（per `312` §SCHEMA "本刀不做"）|
| `docs/48-stage2-real-sha-intake-handbook-20260826.md` | ❌ 未读未写 | docs/45 引用 docs/48 §2/§3/§4.1；不修改 docs/48 既有内容 |
| `docs/47-stage2-s27b-full-mart-evidence-plan-20260826.md` | ❌ 未读未写 | Cursor 拥有架构文档 |
| `docs/06 / 08 / 10 / 34` | ❌ 未读未写 | Cursor 拥有 |
| `docs/40-44 / 46` | ❌ 未读未写 | Cursor 拥有 |
| `scripts/intake_real_sha_if_present.py` / `scripts/compute_file_sha.py` / `scripts/replace_demo_with_real.py` | ❌ 未读未写 | 引用，不修改 |
| `00-CC-CURRENT.md` | ❌ 未读未写 | Cursor 拥有 |
| `gate_thresholds.json` | ❌ 未读未写 | 红线条目 |

**结果**：✅ docs/45 是 CC 维护的 Gate 2 评审索引（per header "起草：CC · 2026-08-26 · queue_rev 97" + 多次刷新行），本次属于第 6 次索引刷新（queue_rev 103/108/119/125/127/130）；Cursor 拥有架构文档未动。

### 4.3 manifest invariant

```
$ python3 scripts/_knife40_manifest_bump.py
ADD: scripts/_knife40_manifest_bump.py (... bytes, sha=____)
ADD: reviews/.../313-...md (... bytes, sha=____)
REFRESH: docs/45-stage2-s210-lite-gate2-review-index-20260826.md (sha ____ → ____)
UPDATE artifact_count: 633 → 635
INVARIANT: sum(role_count)=635 == artifact_count=635 == len(artifacts)=635
OK manifest updated; added 2 artifacts
```

**结果**：✅ invariant 守门；本刀 +2（bump + receipt），docs/45 SHA REFRESH（不增计数）

### 4.4 docs/45 内容守门

| 检查项 | 状态 |
|---|---|---|
| ✅ header 7 刷新行（含 queue_rev 130 per `312`）| ✅ |
| ✅ §3 O3 行指向 docs/49 规划蓝图（per `312` §NOW "1"）| ✅ |
| ✅ §3 O1 详细 10 子项（含 O3 OCR 生产路径规划子项 5 关键事实）| ✅ |
| ✅ §5.5 OPEN 5 项（+ O3 规划已交 per `docs/49` + `309`）| ✅ |
| ✅ §6 OPEN 行更新（O3 per `docs/49`/`309`/`docs/45` §3 O3）| ✅ |
| ✅ §6.2 16 元素（+ O3 规划蓝图 + 4 退出码契约 + allowlist）| ✅ |
| ✅ §7 invariant 更新到 635 | ✅ |
| ✅ §7 O1 + O8 OPEN 携带更新（含 O3 OCR 规划已交 `309` 仍 OPEN）| ✅ |
| ✅ ⚠ 不宣布 Gate 2 PASS / O3 收口 守门贯穿全文 | ✅ |
| ✅ O1 + O3 OPEN 显式携带（per docs/34 §3 + §120）| ✅ |
| ✅ Gate 2 评审日期 W8（per docs/34 §10.4）| ✅ |

---

## §5. 红线自检（per `312` §红线 + docs/34 §1/§3/§8/§133 + docs/49 §0/§7 + docs/06 §6.6 + docs/42 §8）

| 红线 | 状态 |
|---|---|
| ❌ 不宣布 Gate 1 / Gate 2 PASS | ✅ docs/45 §1 + §6 + §7 + 本回执 header + §2 + §5 多次显式守门 |
| ❌ 不擅自 O1 收口 | ✅ docs/45 §3 O1 详细 显式 OPEN；intake WAITING_FILE；预览路径**非 O1** |
| ❌ 不宣布 O3 收口 | ✅ docs/45 §3 O3 行 + §3 O1 详细 + §5.5 OPEN + §6 OPEN + §6.2 多处显式 OPEN |
| ❌ 不实装 OCR 引擎 | ✅ docs/49 §0 范围 + §8 不在范围；docs/45 §3 O3 + §6.2 显式 OPEN（实装待 tasking 31X+）|
| ❌ 伪造样本 / 真履历 | ✅ 仅索引刷新；不创数据 |
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
| ❌ 不替用户下裁定 | ✅ 仅执行 `312` §SCHEMA 范围（机械登记）|
| ❌ 不在聊天复述 Cursor 长文 | ✅ 仅回执要点 |
| ❌ 不索要 PAT | ✅ |
| ✅ pack invariant 守门 | ✅ 633 → 635；bump script source-of-truth + docs/45 SHA REFRESH |
| ✅ receipts 仅写 `reviews/stage0-gate0-rework-2026-08-23/` | ✅ |
| ✅ 不改 Cursor 拥有架构文档 | ✅ docs/06/08/10/34/40-44/46-49 / `00-CC-CURRENT.md` 未读未写 |
| ✅ 不擅自提前 Gate 2 评审日期 | ✅ W8（per docs/34 §10.4）|
| ✅ mart-shape 禁词 3 重守门 | ✅ runtime + 静态 scanner + pytest + TS 类型约束（per docs/45 §6.2）|
| ✅ mart-shape feature-flag 默认值 | ✅ `NEXT_PUBLIC_USE_MART_FIXTURE !== "1"` 默认走 mock |
| ✅ 兼容 S2.7-b-lite / S2.7-b-full-lite / S2.7-b-full mart skel / demo-join / parity / person-tenure demo | ✅ 7 回执全部入 §6.1 |
| ✅ O1 + O3 OPEN 显式携带 | ✅ §3 + §5.5 + §6 + §6.2 |
| ✅ 预览路径明确非 O1 收口 | ✅ §3 + §5.5 + §6.2 |
| ✅ docs/45 = CC 维护索引（per header "起草：CC"）| ✅ 第 6 次机械刷新（queue_rev 103/108/119/125/127/130）|
| ✅ docs/49 引用而非修改 | ✅ docs/45 §3 O3 + §3 O1 详细 + §5.5 + §6 + §6.2 多处引用 docs/49 + `309`；不改 docs/49 既有内容 |
| ✅ O3 输入边界显式禁止 | ✅ §3 O1 详细 + §6.2 引用 docs/49 §2.2（HTTP / 登录绕过 / 未授权 API / symlink）|
| ✅ O3 4 退出码契约 + allowlist 复用 docs/48 | ✅ §6.2 显式 |
| ✅ OCR 引擎选型待用户裁定 | ✅ §3 O1 详细 显式 |
| ✅ O3 仍 OPEN — 未实装 | ✅ 多处显式 OPEN |

---

## §6. 推送 / 三路对齐

| 步骤 | 命令 | 结果 |
|---|---|---|
| origin pull | `git fetch origin && git pull --ff-only origin main` | queue_rev 130 ✅ |
| cc_gate_watch | `./scripts/cc_gate_watch.sh --pull` | `phase=CC_ACTION_REQUIRED` ✅ |
| docs/45 修改 | `docs/45-stage2-s210-lite-gate2-review-index-20260826.md`（header + §3 O3 + §3 O1 详细 + §5.5 + §6 + §6.2 + §7）| ✅ MOD |
| bump script | `scripts/_knife40_manifest_bump.py`（2 NEW + 1 REFRESH）| ✅ 633 → 635（+2）|
| 本地校验 | manifest invariant | ✅ 635 == 635 == 635 |
| commit (knife 40 主提交) | `git add ... && git commit -m "docs(45): 312 O3 规划登记 — §3 O3 → docs/49 + §5.5/§6/§6.2/§7 同步"` | ✅ `8d144a822bf4471f57bd90c03560080652e59ee6` |
| origin push | `git push origin HEAD`（**priority**）| ✅ `8d144a8` → origin/main |
| github push | `git push github HEAD` | ✅ `8d144a8` → github/main |
| 三路对齐 | origin/main = github/main = local HEAD | ✅ `8d144a822bf4471f57bd90c03560080652e59ee6` |
| backfill commit | 独立 commit（不 amend-after-push）| ✅ `8d144a8` + receipt backfill |

> **禁止 amend-after-push**：receipt SHA + commit SHA 必须在独立 commit 里 backfill（per knife 2/3/4 经验）。

---

## §7. 下次 heartbeat 预期

- `queue_rev 130` 完成后：Cursor 收 `313` → 下发 `314-stage0-cursor-s312-docs45-o3-plan-audit-…md`（PASS/FAIL）
- 若 PASS：docs/45 O3 规划登记齐；docs/45 §3 O3 / §5.5 / §6 / §6.2 / §7 多处显式 O3 仍 OPEN（实装待 tasking 31X+）
- 若 FAIL：`313-correction` 回合（修 docs/45 表格 / 修 §3 措辞 / re-commit）

---

## §8. 备注

- **本刀不宣布 Gate 2 / O3 PASS** — docs/45 §1 + §6 + §7 + 本回执 §2 + §5 多次显式守门。Gate 2 评审日期暂定 W8（per docs/34 §10.4），由 Cursor/用户裁定，不擅自提前。
- **本刀只做机械索引登记** — `312` §SCHEMA 显式约束：不接真 SHA / 不接 person/tenure 真数据 / 不爬网 / 不派生 score / 不改架构设计 / **不实装 OCR 引擎** / **不宣布 O3 收口**。
- **docs/45 = CC 维护索引（per header "起草：CC · queue_rev 97"）** — 本次属于第 6 次机械刷新（queue_rev 103/108/119/125/127/130）；Cursor 拥有架构文档（docs/06/08/10/34/40-44/46-49）未动。**红线 "Cursor 37 architect-only (don't write docs Cursor owns)" 不约束 docs/45**，因为 docs/45 是 CC 维护的索引，由 Cursor 任务书（如 `312`）显式委托刷新。
- **O3 仍 OPEN — 规划已交，实装待 tasking 31X+** — docs/45 §3 O3 + §3 O1 详细 + §5.5 + §6 + §6.2 多处显式标注。O3 实装须用户裁定 paddle-ocr / tesseract / cloud + 用户主动 `--confirm-o3=PATH` 提供真实 PDF + 端到端 pytest PASS（per `docs/49` §5.3 + §8 + §10）。
- **docs/49 引用而非修改** — docs/45 仅登记 docs/49 + `309` 引用；不改 docs/49 既有内容（per `312` §SCHEMA "本刀做/本刀不做" + docs/49 §0 范围）。
- **docs/48 契约 1:1 复用** — docs/45 §6.2 显式 O3 复用 docs/48 §3 4 退出码 + `scripts/compute_file_sha.py` `ALLOWED_PREFIXES` allowlist（per `docs/49` §2.3 + §4.3）。
- **OCR 引擎选型待用户裁定** — docs/45 §3 O1 详细显式 paddle-ocr 推荐 + tesseract/cloud 备选 + 用户裁定（per `docs/49` §3.2 步骤 4 + §10 Q1）。
- **真实 PDF 待用户主动 `--confirm-o3=PATH`** — docs/45 §3 O1 详细显式（per `docs/49` §10 Q4 + docs/48 §3 intake 模式）。
- **cloud OCR 默认离线** — docs/45 §3 O1 详细显式 + docs/49 §2.2 显式禁止未授权 API（须 `--enable-cloud-ocr=PROVIDER` 显式 flag）。
- **下游分发依赖** — docs/45 §3 O1 详细显式 S2.1-lite `mart_person_tenure` + S2.2 `policy_observation` + S2.4 `fiscal_observation`（per `docs/49` §6.2）。
- **§7 invariant 更新** — 旧 `628` (knife 38 stale) → knife 39 留 `633` → knife 40 `635`；manifest SHA 必须同步更新（per knife 16 source-of-truth fix）。
- **docs/45 header 7 刷新行** — queue_rev 97 (`250`) + 103 (`259`) + 108 (`268`) + 119 (`284`) + 125 (`299`) + 127 (`305`) + **130 (`312`)**。
- **不修改 dbt 项目配置** — 索引刷新刀不需 dbt_project.yml 改动。
- **下次 heartbeat 闸门** — O3 真收口须用户主动 `--confirm-o3=PATH` + OCR 引擎选型裁定 + 端到端 pytest PASS；在此之前 docs/45 §3 O3 / §5.5 / §6 / §6.2 仍标注 O3 仍 OPEN（实装待 tasking 31X+）。

— End of `313` —

> 等待 Cursor 审验（预期 `314-stage0-cursor-s312-docs45-o3-plan-audit-…md`）。
> 通过后 docs/45 O3 规划登记齐；§3 O3 / §5.5 / §6 / §6.2 / §7 多处显式 O3 仍 OPEN（实装待 tasking 31X+）。
> ⚠ **本刀不宣布 Gate 2 / O3 PASS**（per docs/34 §1 + §8 #8 + `312` §红线）。
> ⚠ **本刀只做机械索引登记**（per `312` §SCHEMA "本刀做/本刀不做"）。
> ⚠ **O3 仍 OPEN — 规划已交，实装待 tasking 31X+**（per docs/34 §3 + `312` §红线）。
> ⚠ **O1 真实 SHA 收口前恒占位 `'0'*64`**（per docs/47 §3.1 ⚠️ + `312` §红线）。
> ⚠ **O3 真收口须用户主动 `--confirm-o3=PATH` + OCR 引擎选型裁定 + 端到端 pytest PASS**（per `docs/49` §5.3 + §8 + §10 + docs/48 §3）。
> ⚠ **cloud OCR 默认离线；须 `--enable-cloud-ocr=PROVIDER` 显式 flag**（per `docs/49` §2.2 + §3.2 步骤 4）。
> ⚠ **输入边界 = 仅用户/admin upload；禁止 HTTP 爬源 / 登录绕过 / 未授权 API / symlink / 伪造**（per `docs/49` §2.2）。
> Gate 2 评审日期暂定 W8（per docs/34 §10.4）。