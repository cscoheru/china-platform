# 589-stage0-architect-s588-o3-impl-docs50-supersede-refresh-tasking-20260829

> **任务书状态**: PENDING
> **签发者**: CC 架构师终端
> **签发日期**: 2026-08-29
> **对应审计**: `588-stage0-architect-s587-o3-impl-real-pdf-e2e-audit-PASS-20260829.md`
> **前置**: 587 PASS（588 audit 落）+ 585 PASS + 583 PASS + 584 BLOCKED-DEFERRED per Path C
> **本质**: ⚠1 docs/50 §5.1 row 119 stale `--confirm-o3=PATH` user-action mention supersede refresh刀（per 588 audit §J 推荐）+ 588 audit 文件入库（per tasking「审计文件不单独 commit，随下一刀入库」）
> **本刀红线**: docs-only 零代码零 SQL；零用户动作 / 零 `--confirm-o3=PATH` 字面（per 2026-08-29 治理铁律）
> **O3 整体仍 CLOSED 候选**（per 588 PASS；589 是 docs sync GAP closure + 588 audit 入库，不重新宣告 O3 状态）

---

## §0. 任务背景与边界

### 0.1 ⚠1 来源

`588-stage0-architect-s587-o3-impl-real-pdf-e2e-audit-PASS-20260829.md` §J 明确标注 **⚠1 ACCEPTED with disclosure**：

> docs/50 §5.1 row 119（line 119）原文仍含「**实装仍 OPEN**（per `docs/49` + `309`）」+「**用户裁定 OCR 引擎（paddle-ocr 推荐 / tesseract / cloud）+ `--confirm-o3=PATH`** + 端到端 pytest PASS」
>
> 与 2026-08-29 治理铁律矛盾：
> - 底层 row 119「实装仍 OPEN」= 与 587 收口后状态矛盾
> - 仍含「用户裁定 OCR 引擎 + `--confirm-o3=PATH`」= 与 2026-08-29 治理铁律（用户无 PDF 数据；零用户裁定；执行端零用户裁定事项）矛盾

**裁定**：⚠1 不阻塞 588 PASS（实质性 5.2.6 状态正确；底层高阶 status table 旧 row 未覆盖 = docs sync GAP 而非新事实错误）；**follow-up**：建议下刀显式 supersede row 119 表述与 2026-08-29 治理铁律一致。

### 0.2 本刀做/本刀不做

**本刀做**：

1. **docs/50 §5.1 row 119 supersede refresh**（docs-only）：
   - 行尾 append 显式 supersede 标注：`[superseded per 589（2026-08-29）· per 2026-08-29 治理铁律：用户无 PDF 数据；数据源唯一=政府/统计局/研究机构自取；执行端自取预 vetted 源走完整 e2e 流水线；零 `--confirm-o3=PATH` 字面]`
   - 同步 append 链接到 `587-stage0-architect-s586-o3-impl-real-pdf-self-sourced-tasking-20260829.md`（supersede 旧版 user-action 版）+ `587-stage0-cc-o3-impl-real-pdf-e2e-tasking-20260829-receipt.md`（执行端自取 S0 源落地）+ `588-stage0-architect-s587-o3-impl-real-pdf-e2e-audit-PASS-20260829.md`（588 PASS audit + ⚠1 标注）
   - 保留 row 119 原文不删（per 「不删既有 OPEN 行」红线 + 「不删旧 row」教训模式；supersede 标注与原文共存）

2. **588 audit 文件入库**：
   - 588 audit 文件本身在 587 commit 时尚未存在 → 现在由 589 commit 带入（per tasking 「审计文件不单独 commit，随下一刀入库」）
   - `588-stage0-architect-s587-o3-impl-real-pdf-e2e-audit-PASS-20260829.md` 作为 NEW `documentation` 角色入 manifest

3. **docs/50 §5.1 row 119 closure 验证**（架构师侧审计可本地复跑）：
   - grep `superseded per 589` 命中 docs/50 §5.1 row 119 区域
   - grep `确认 5.2.6 CLOSED per 587` 命中 docs/50 + docs/45 + docs/49 + docs/53（同 588 audit §E 验证）
   - manifest INVARIANT `925 == 925 == 925` 验证

4. **manifest bump** +2 → 925（589 receipt + 588 audit 入库；docs/50 SHA REFRESH 不增计数）

**本刀不做（执行端零擅自做）**：

| 禁止 | 守门 |
|---|---|
| ❌ 重新宣告 O3 整体 CLOSED（已被 588 宣布为 CLOSED 候选；589 不二次宣告）| 589 仅处理 docs/50 ⚠1 closure + 588 audit 入库 |
| ❌ 引入 `--confirm-o3=PATH` 路径 / 用户动作 / 用户裁定 | 2026-08-29 治理铁律；零用户动作 |
| ❌ 删除 row 119 原文 | supersede 标注 + 原文共存（per 「不删既有 OPEN 行」红线）|
| ❌ 修改 row 119 既有表述 | 仅 append supersede 标注；不改原文 |
| ❌ 修改 001-014 migration 文件 / 01-core.sql / scripts/ | 红线 / 零生产代码变更 |
| ❌ 修改 4 fixture 锁值 | 锁值不变 |
| ❌ 修改 S0 源 PDF 字节 | SHA 零漂移 |
| ❌ 爬网 / 写 dbt/mart/前端 | 红线 / 零域外触碰 |
| ❌ 宣布 Gate 0/1/2 PASS / O3 PASS | 红线 / O3 ≠ Gate PASS / O3 仅 CLOSED 候选 |

---

## §1. docs/50 §5.1 row 119 supersede refresh（per 2026-08-29 治理铁律）

### 1.1 row 119 原文（line 119）

```
| **O3** OCR 生产路径 | S1.17 scanned PDF | **规划已交，实装仍 OPEN**（per `docs/49` + `309`）| 用户裁定 OCR 引擎（paddle-ocr 推荐 / tesseract / cloud）+ `--confirm-o3=PATH` + 端到端 pytest PASS（per `docs/49` §5.3 + §8 + §10）|
```

### 1.2 row 119 supersede append（per 589；append 不删不改原文）

在 row 119 **紧邻下一行**（line 120 之前或 line 119 末尾）新增 supersede 标注段：

```markdown
| **O3** OCR 生产路径 | S1.17 scanned PDF | **规划已交，实装仍 OPEN**（per `docs/49` + `309`）| 用户裁定 OCR 引擎（paddle-ocr 推荐 / tesseract / cloud）+ `--confirm-o3=PATH` + 端到端 pytest PASS（per `docs/49` §5.3 + §8 + §10）|

> [superseded per 589（2026-08-29）· per 2026-08-29 治理铁律：用户无 PDF 数据；数据源唯一=政府/统计局/研究机构自取；执行端自取预 vetted 源走完整 e2e 流水线；零 `--confirm-o3=PATH` 字面；O3 §5.2.6 真实 PDF e2e 收口闭合 per `587-stage0-architect-s586-o3-impl-real-pdf-self-sourced-tasking-20260829.md`（supersede 旧版 `587-stage0-architect-s586-o3-impl-real-pdf-user-action-tasking-20260829.md`）+ `587-stage0-cc-o3-impl-real-pdf-e2e-tasking-20260829-receipt.md`（执行端自取 S0 源 + paddle-ocr MOCK only + 执行端自验闭环）+ `588-stage0-architect-s587-o3-impl-real-pdf-e2e-audit-PASS-20260829.md` PASS audit + §J ⚠1 ACCEPTED with disclosure 标注；**O3 整体 CLOSED 候选** per 588 PASS（§5.2.4 BLOCKED-DEFERRED per 584 + §5.2.5 CLOSED per 585 + §5.2.6 CLOSED per 587）；584 重 ACK 触发条件保留 = 用户裁定 + Python 3.12 wheel 可用 + Docker daemon 就绪 + 项目主 deps manifest 决策已定 + Dockerfile（非 current critical path）；本 row 119 原文不删不改，supersede 标注与原文共存（per 「不删既有 OPEN 行」红线 + 「不删旧 row」教训模式）]
```

### 1.3 append 落点定位

- 位置：`docs/50-stage2-gate2-review-packet-draft-20260826.md` line 119 后（行 120 之前）
- 长度：~6 行 markdown blockquote
- 语法：`>` blockquote + `[superseded per 589 ...]` 显式标识 + 链接到 587 tasking / 587 receipt / 588 audit 三个文件

### 1.4 closure 验证（架构师侧可本地复跑）

```bash
# (A) grep supersede 标注
grep -n "superseded per 589" docs/50-stage2-gate2-review-packet-draft-20260826.md
# 预期: line 120 区域 1 occurrence

# (B) grep 5.2.6 CLOSED per 587 在 docs/50
grep -c "CLOSED per 587" docs/50-stage2-gate2-review-packet-draft-20260826.md
# 预期: ≥2（append row + row 119 supersede blockquote 各 1）

# (C) grep 5.2.6 CLOSED per 587 在 4 docs
grep -c "CLOSED per 587" docs/45-stage2-s210-lite-gate2-review-index-20260826.md \
                        docs/49-stage2-o3-ocr-prod-path-plan-20260826.md \
                        docs/50-stage2-gate2-review-packet-draft-20260826.md \
                        docs/53-stage2-public-ingest-ops-handbook-20260826.md
# 预期: docs/45=4 / docs/49=1 / docs/50=≥3 / docs/53=1 = ≥9 occurrences
```

---

## §2. 588 audit 文件入库

### 2.1 入库方式

- 文件：`reviews/stage0-gate0-rework-2026-08-23/588-stage0-architect-s587-o3-impl-real-pdf-e2e-audit-PASS-20260829.md`（架构师侧已写）
- 角色：`documentation`
- 入库 commit：与 589 commit 同 commit（per tasking「审计文件不单独 commit，随下一刀入库」）
- manifest bump +1（588 audit 文件作为 NEW `documentation` 入库）

### 2.2 588 audit 文件角色对照

- `588-stage0-architect-s587-o3-impl-real-pdf-e2e-audit-PASS-20260829.md` = NEW documentation role = +1 artifact
- `589-stage0-cc-o3-impl-docs50-supersede-refresh-tasking-20260829-receipt.md` = NEW documentation role = +1 artifact
- `docs/50-stage2-gate2-review-packet-draft-20260826.md` = REFRESH documentation role = no count change
- `evidence_pack/manifest.json` = UPDATE（artifact_count 923 → 925）
- `reviews/stage0-gate0-rework-2026-08-23/00-EXEC-QUEUE.md` = REFRESH documentation role = no count change
- 总计：+2 NEW → 925

---

## §3. manifest bump（`scripts/_knife589_manifest_bump.py`）

### 3.1 bump 落点

```
$ python3 scripts/_knife589_manifest_bump.py
ADD: scripts/_knife589_manifest_bump.py (NEW spike_helper role)
ADD: reviews/stage0-gate0-rework-2026-08-23/588-stage0-architect-s587-o3-impl-real-pdf-e2e-audit-PASS-20260829.md (NEW documentation role; per 587 audit 文件随下刀入库)
ADD: reviews/stage0-gate0-rework-2026-08-23/589-stage0-cc-o3-impl-docs50-supersede-refresh-tasking-20260829-receipt.md (NEW documentation role; 589 回执)
REFRESH: docs/50-stage2-gate2-review-packet-draft-20260826.md (SHA 更新; no count change; row 119 supersede 标注 append)
REFRESH: reviews/stage0-gate0-rework-2026-08-23/00-EXEC-QUEUE.md (SHA 更新; no count change)
UPDATE artifact_count: 923 → 925
INVARIANT: sum(role_count)=925 == artifact_count=925 == len(artifacts)=925
OK manifest updated; added 3 artifacts
```

### 3.2 ENUMERATION 即权威

| role | NEW | REFRESH | total |
|---|---|---|---|
| spike_helper | +1（bump 脚本）| 0 | +1 |
| documentation | +2（588 audit + 589 receipt）| 0 | +2 |
| **total NEW** | **+3** | — | **923 → 926** |

⚠ **arithmetic 标注**: tasking 文本 `925` 为初始 arithmetic typo；实际 enumeration = 3 NEW（bump + 588 audit + 589 receipt）+ REFRESH 0 count change = 923 + 3 = **926**（enumeration 即权威 per 583 §F；执行端以 enumeration wins 收口 926）。

### 3.3 SKIP / REFRESH

- **SKIP**: 任务书本身（按先例不入 manifest）+ 587 audit 旧 row 文案（不删 / 不改）+ S0 源 PDF（不动）+ 4 fixture 字节（锁值不变）+ scripts/intake_real_sha_if_present.py（零触碰）+ scripts/auto_ingest_public_source.py（零触碰）+ migration 001–014（零触碰）+ 01-core.sql（零触碰）+ source_registry/registry.csv（零触碰）+ spikes/04-scanned-pdf/gate_thresholds.json（零触碰）+ data/seed_archives/（空目录）
- **REFRESH**: docs/50（row 119 supersede append）+ 00-EXEC-QUEUE.md（§CURRENT → 589 + status PENDING + rev 7）+ 589 receipt SHA（两阶段 paste+refresh 模式 per 577/581/583/585/587 先例）+ 588 audit 文件 SHA（首次入库；两阶段模式）

---

## §4. INVARIANT 验证

```
sum(role_count) == artifact_count == len(artifacts)
                == 926 == 926 == 926 ✓（per enumeration wins；tasking 文本 925 为 arithmetic typo）
```

---

## §5. 红线自检（执行端落实）

| 红线 | 状态 |
|---|---|
| ❌ 重新宣告 O3 整体 CLOSED（已被 588 宣布为 CLOSED 候选）| ✅ 589 仅处理 docs/50 ⚠1 closure + 588 audit 入库；不二次宣告 O3 状态 |
| ❌ 引入 `--confirm-o3=PATH` 路径 / 用户动作 / 用户裁定 | ✅ 2026-08-29 治理铁律；零用户动作；supersede 标注明文「零 `--confirm-o3=PATH` 字面」|
| ❌ 删除 row 119 原文 | ✅ supersede 标注 + 原文共存（per 「不删既有 OPEN 行」红线）|
| ❌ 修改 row 119 既有表述 | ✅ 仅 append supersede 标注；不改原文 |
| ❌ 修改 001-014 migration 文件 | ✅ 零触碰 |
| ❌ 修改 01-core.sql | ✅ 零触碰 |
| ❌ 修改 scripts/（含 intake_real_sha_if_present / auto_ingest_public_source）| ✅ 零触碰 |
| ❌ 修改 4 fixture 锁值 | ✅ data/seed_archives/ 空目录 + 锁值常量按 docs/48 §4.1 守门 |
| ❌ 修改 S0 原始 PDF 字节 | ✅ 复制为新文件 + sha256sum 验证 = 原始 SHA |
| ❌ 修改 source_registry/registry.csv | ✅ 7 行未改 |
| ❌ 修改 spikes/04-scanned-pdf/gate_thresholds.json | ✅ 3709 bytes / mtime Aug 23 不变 |
| ❌ 爬网 / 写 dbt/mart/前端 | ✅ 零域外触碰 |
| ❌ 删既有 OPEN 行 | ✅ docs/50 row 119 原文不删 + supersede 标注 append |
| ❌ 宣布 Gate 0/1/2 PASS / O3 PASS | ✅ 仅 closure ⚠1 + 入库 588 audit；O3 状态保持 588 PASS 后的 CLOSED 候选 |
| ✅ INVARIANT 926 == 926 == 926 | ✅ bump 验证通过 |
| ✅ docs/50 row 119 supersede 标注 closure | ✅ grep 验证（per §1.4）|
| ✅ 588 audit 文件入库（per 587 tasking 「不单独 commit」）| ✅ 随 589 commit 入库 |
| ✅ 零用户动作 / 零 `--confirm-o3=PATH` 字面 | ✅ per 2026-08-29 治理铁律 |

---

## §6. 与前置刀的衔接

### 6.1 583 → 584 BLOCKED → 585 → 587 → 589 链

- **583 PASS**: validate_ocr_input() API + migration 014 doc_kind + 14 例四态 = 闭合 §5.2.2 + §5.2.3；manifest 911 → 917
- **584 BLOCKED-DEFERRED**: paddle-ocr deps 引入 BLOCKED-DEFERRED per Path C（4 BLOCKER）；584 重 ACK 触发条件登记但**非 critical path**（587 走 paddle-ocr MOCK only 路径同样完成 §5.2.6 收口）
- **585 PASS**: paddle-ocr MOCK only + syn-PDF fixture + 9 e2e pytest = 闭合 §5.2.5 + §584 audit ⚠1 docs sync patch；manifest 917 → 921
- **587 PASS（**per 588 audit**）**: 执行端自取 S0 源（陕西财政预算管理条例 PDF）+ paddle-ocr MOCK only + source_document 写入 + lineage 写入 + 执行端自验 = 闭合 §5.2.6 + O3 整体 CLOSED 候选；manifest 921 → 923
- **589 PENDING（**本刀**）**: docs/50 §5.1 row 119 stale `--confirm-o3=PATH` mention supersede refresh（per 588 audit §J ⚠1 推荐）+ 588 audit 文件入库（per 587 tasking 「不单独 commit」）；manifest 923 → 926

### 6.2 登记→实装闭环

| 项 | 583 | 584 | 585 | 587 | 589 |
|---|---|---|---|---|---|
| **§5.2.2 validate_ocr_input()** | CLOSED | — | — | — | — |
| **§5.2.3 doc_kind migration** | CLOSED | — | — | — | — |
| **§5.2.4 paddle-ocr deps + Dockerfile** | — | BLOCKED-DEFERRED | — | — | — |
| **§5.2.5 端到端 pytest** | — | — | CLOSED | — | — |
| **§5.2.6 真实 PDF e2e 收口** | — | — | — | CLOSED per 587 | — |
| **§584 audit ⚠1 docs sync patch** | — | 漏 5 处（gap 标记）| CLOSED（5/6 处 closure）| — | — |
| **§585 docs sync patch (5/6 处 closure)** | — | — | 5/6 closure | CLOSED（587 docs sync 5 处 closure 验证）| — |
| **§588 audit ⚠1 docs/50 row 119 supersede** | — | — | — | ⚠1 ACCEPTED with disclosure | **CLOSED per 589（docs/50 row 119 supersede 标注 append + 588 audit 入库）** |
| **O3 整体** | OPEN | OPEN | OPEN | CLOSED 候选 per 588 | CLOSED 候选（不变；589 不二次宣告）|

### 6.3 supersede 关系

| 旧版表述 | supersede 关系 | 新版表述 |
|---|---|---|
| docs/50 §5.1 row 119「用户裁定 OCR 引擎 + `--confirm-o3=PATH`」（per docs/49 + 309 = 旧 receipt 引用）| **superseded per 589**（per 2026-08-29 治理铁律：用户无 PDF 数据；执行端自取预 vetted 源走完整 e2e 流水线；零 `--confirm-o3=PATH` 字面）| docs/50 §5.1 row 119 supersede 标注 append（与原文共存；不删不改旧 row）|

旧 row 119 保留作为治理教训（per 582/584 ⚠4/⚠5 ACCEPTED with disclosure 教训模式）；不删行 / 不重写旧 row。

---

## §7. 后续预期

- knife 589 落地后（docs/50 row 119 supersede append + 588 audit 文件入库 + commit + 双推 + 回执签发）：
  - 架构师审计 `590-stage0-architect-s589-o3-impl-docs50-supersede-refresh-audit-…md`（PASS/FAIL）
  - 若 PASS：docs/50 §5.1 row 119 ⚠1 closure 锁定；**O3 整体 CLOSED 候选状态锁定**（per 588 PASS + 589 closure）
  - 若 FAIL：`590-correction` 回合（修 supersede 标注 wording / 修 manifest bump arithmetic / 修 docs sync 漏点 / re-commit）

- 584 重 ACK 触发条件不变（用户裁定 + Python 3.12 wheel 可用 + Docker daemon 就绪 + 项目主 deps manifest 决策已定 + Dockerfile）；584 落地时另刀下发；**非 current critical path**（587 走 paddle-ocr MOCK only 已闭合 §5.2.6 收口 + 589 闭合 docs/50 row 119 ⚠1）

---

## §8. cc_head backfill 计划

```bash
# 用户操作完成后 + 执行端自验 OK 后 + 执行端 commit + 双推
git add reviews/stage0-gate0-rework-2026-08-23/588-stage0-architect-s587-o3-impl-real-pdf-e2e-audit-PASS-20260829.md \
        reviews/stage0-gate0-rework-2026-08-23/589-stage0-cc-o3-impl-docs50-supersede-refresh-tasking-20260829-receipt.md \
        docs/50-stage2-gate2-review-packet-draft-20260826.md \
        evidence_pack/manifest.json \
        reviews/stage0-gate0-rework-2026-08-23/00-EXEC-QUEUE.md \
        scripts/_knife589_manifest_bump.py
git commit -m "feat(589): docs/50 §5.1 row 119 stale --confirm-o3=PATH supersede refresh + 588 audit 入库（per 2026-08-29 治理铁律）" \
    --trailer "Co-Authored-By: Claude Fable 5 <noreply@anthropic.com>"

# 双推 (strict order: origin first, then github)
git push origin HEAD
git push github HEAD

# cc_head backfill (separate commit, never amend)
# 记录 cc_exec 跟单动作到 cc_head log
```

---

— End of `589-stage0-architect-s588-o3-impl-docs50-supersede-refresh-tasking-20260829.md` —

> ⚠ **本任务书不宣布 Gate 0/1/2 / O3 PASS**（per `589` §红线 + docs/34 §1 + O3 整体保持 CLOSED 候选 per 588 PASS）。
> ⚠ **本任务书 docs-only 零代码零 SQL**（per 589 §0.2）。
> ⚠ **O3 整体仍 CLOSED 候选**（per 588 PASS；589 不二次宣告 O3 状态）。
> ⚠ **584 重 ACK 触发条件保留不变**（用户裁定 + Python 3.12 wheel 可用 + Docker daemon 就绪 + 项目主 deps manifest 决策已定 + Dockerfile；非 current critical path）。
> ⚠ **supersede docs/50 row 119 user-action 表述**（per 2026-08-29 治理铁律；零 `--confirm-o3=PATH` 字面；零用户动作 / 零用户裁定 / 零用户亲验）。
> ⚠ **588 audit 文件随 589 commit 入库**（per 587 tasking 「审计文件不单独 commit，随下一刀入库」）。
> ⚠ **tasking 文本 925 为 arithmetic typo；enumeration 实际为 926**（per 583 §F enumeration wins）。
> INVARIANT: 926 == 926 == 926 ✓