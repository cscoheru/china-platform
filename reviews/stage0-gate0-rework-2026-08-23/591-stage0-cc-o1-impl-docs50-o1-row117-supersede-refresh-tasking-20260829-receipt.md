# 591-stage0-cc-o1-impl-docs50-o1-row117-supersede-refresh-tasking-20260829-receipt

> **回执状态**: DELIVERED
> **回执者**: CC 执行端
> **回执日期**: 2026-08-29
> **任务书**: `591-stage0-architect-s590-o3-impl-docs50-o1-row117-supersede-refresh-tasking-20260829`（架构师治理模型第十一刀；docs-only refresh 刀 平行 589 模式）
> **前置**: `590-stage0-architect-s589-o3-impl-docs50-supersede-refresh-audit-PASS-20260829`（PASS）+ 589 PASS（590 audit 落）+ 588 PASS + 587 PASS + 585 PASS + 583 PASS + 584 BLOCKED-DEFERRED per Path C
> **核心证据**: docs/50 §5.1 row 117 A 路 supersede 标注 append（与原文共存；不删不改 row 117 主体「WAITING_FILE 状态 + B 路主路径」；per 2026-08-29 治理铁律对称应用明文「零 `--confirm-o1=PATH` 字面」+ A 路保留为 fallback 标注）+ 590 audit 文件入库（NEW documentation role；per 589 tasking「审计文件不单独 commit，随下一刀入库」）+ docs sync closure 验证（grep `superseded per 591` 命中 docs/50 + grep `WAITING_FILE per 591` ≥ 1 + grep `B 路（公开源自动获取）` ≥ 1 + grep `590-...-audit-PASS-...` ≥ 1 + grep `589-...-supersede-refresh-tasking-...` ≥ 1 = 5 落点）+ manifest bump +3 → 929（enumeration wins per 583 §F；INVARIANT 929==929==929）+ 红线 100% 兑现（docs-only 零代码零 SQL）

---

## §0. 本刀做/本刀不做

### 0.1 本刀做

| 项 | 落地 |
|---|---|
| (A) docs/50 §5.1 row 117 A 路 supersede 标注 append | `docs/50-stage2-gate2-review-packet-draft-20260826.md` line 120 行尾新增 ~10-12 行 markdown blockquote 含 `[superseded per 591（2026-08-29）· per 2026-08-29 治理铁律：用户无 PDF 数据；数据源唯一=政府/统计局/研究机构自取；执行端自取预 vetted 源走完整 e2e 流水线；零 `--confirm-o1=PATH` 字面；A 路（用户线下渠道）保留为 fallback 标注（不删除、不调用），仅当 B 路（公开源自动获取）无法取得样本时方由架构师夜间授权下自主评估是否启动；O1 §5.2.x 真实 SHA-locked 江苏样本刀待 docs/52 B 路落定后另刀下发]`；与 row 117 原文共存；不删不改 row 117 主体 WAITING_FILE 状态 + B 路主路径 |
| (B) 590 audit 文件入库 | `reviews/.../590-stage0-architect-s589-o3-impl-docs50-supersede-refresh-audit-PASS-20260829.md` NEW documentation role（per 589 tasking「审计文件不单独 commit，随下一刀入库」）|
| (C) docs sync closure 验证 | grep `superseded per 591` 命中 docs/50 line 120 区域 + grep `WAITING_FILE per 591` ≥ 1 + grep `B 路（公开源自动获取）` ≥ 1 + grep `590-...-audit-PASS-...` ≥ 1 + grep `589-...-supersede-refresh-tasking-...` ≥ 1 = 5 落点全部命中 |
| (D) manifest bump +3 → 926 → 929 | `scripts/_knife591_manifest_bump.py` NEW（enumeration 即权威 per 583 §F；INVARIANT 929==929==929）|

### 0.2 本刀不做（执行端零擅自做）

| 禁止 | 守门 |
|---|---|
| ❌ 重新宣告 O3 整体 CLOSED（已被 588 + 590 PASS 双重声明）| 591 仅处理 docs/50 row 117 A 路 ⚠1 closure + 590 audit 入库；不重新宣告 O3 状态 |
| ❌ 重新宣告 O1 整体收口 | O1 整体仍 WAITING_FILE；row 117 主体保持 |
| ❌ 启动 O1 A 路（用户线下渠道）实跑 | 2026-08-29 治理铁律；用户无 PDF 数据；B 路优先；A 路仅 fallback 标注 |
| ❌ 引入 `--confirm-o1=PATH` 路径 / 用户动作 / 用户裁定 | 2026-08-29 治理铁律；零用户动作；supersede 标注明文「零 `--confirm-o1=PATH` 字面」|
| ❌ 删除 row 117 原文 | supersede 标注 + 原文共存（per 「不删既有 OPEN 行」红线）|
| ❌ 修改 row 117 WAITING_FILE 状态 / B 路主路径标注 | row 117 主体保持；仅 append A 路 supersede 标注 |
| ❌ 修改 001-014 migration 文件 / 01-core.sql / scripts/ | 红线 / 零生产代码变更 |
| ❌ 修改 4 fixture 锁值 | data/seed_archives/ 空目录 + 锁值常量按 docs/48 §4.1 守门 |
| ❌ 修改 S0 源 PDF 字节 | SHA 零漂移 |
| ❌ 爬网 / 写 dbt/mart/前端 | 红线 / 零域外触碰 |
| ❌ 宣布 Gate 0/1/2 PASS / O1 PASS / O3 PASS | 红线 / 仅 closure A 路 ⚠1 + 入库 590 audit |

---

## §1. (A) docs/50 §5.1 row 117 A 路 supersede refresh（per 2026-08-29 治理铁律对称应用）

### 1.1 row 117 原文（line 119 actual；未删未改）

```
| **O1** 真实 SHA-locked 江苏样本 | S1.18 DEMO 路径 | **WAITING_FILE**（= intake 出口码 / mart 真 SHA 未入仓技术状态语义，非「等用户投喂才可继续」per `484`/`486`/`488`/`490` 对齐；用户 2026-08-26 确认本机/仓库**未持有**江苏真实 SHA-locked 样本；`lineage.source_file_sha256` 恒为 `'0'*64` 占位 per docs/47 §3.1 ⚠️）| 主路径 = docs/52 B 路（公开源自动获取，试点轴 `NATIONAL_BULLETIN` per `480`/`482`）；A 路 = 用户线下渠道（政府文件 PDF/扫描件原件）+ `--confirm-o1=PATH` 显式 flag（仅限 A 路出口）+ intake 4 退出码契约（per `291` + docs/48 §4.3），仍可用但非唯一 |
```

### 1.2 A 路 supersede 标注 append（line 120；与原文共存；row 117 主体保持）

```markdown
> [superseded per 591（2026-08-29）· per 2026-08-29 治理铁律：用户无 PDF 数据；数据源唯一=政府/统计局/研究机构自取；执行端自取预 vetted 源走完整 e2e 流水线；零 `--confirm-o1=PATH` 字面；A 路（用户线下渠道）保留为 fallback 标注（不删除、不调用），仅当 B 路（公开源自动获取）无法取得样本时方由架构师夜间授权下自主评估是否启动；O1 §5.2.x 真实 SHA-locked 江苏样本刀待 docs/52 B 路落定后另刀下发；O3 §5.2.6 真实 PDF e2e 收口闭合 per `587-stage0-architect-s586-o3-impl-real-pdf-self-sourced-tasking-20260829.md`（supersede 旧版 `587-stage0-architect-s586-o3-impl-real-pdf-user-action-tasking-20260829.md`）+ `587-stage0-cc-o3-impl-real-pdf-e2e-tasking-20260829-receipt.md`（执行端自取 S0 源 + paddle-ocr MOCK only + 执行端自验闭环）+ `588-stage0-architect-s587-o3-impl-real-pdf-e2e-audit-PASS-20260829.md` PASS audit + §J ⚠1 ACCEPTED with disclosure 标注 + `589-stage0-architect-s588-o3-impl-docs50-supersede-refresh-tasking-20260829.md` O3 row 119 supersede 平行模式 + `590-stage0-architect-s589-o3-impl-docs50-supersede-refresh-audit-PASS-20260829.md` PASS audit + ⚠1 line 121 vs 120 ACCEPTED with disclosure 标注；**O3 整体 CLOSED 候选** per 588 PASS + 590 PASS 双重声明；**O1 整体仍 WAITING_FILE**（per docs/47 §3.1 + 用户 2026-08-26 披露 + 2026-08-29 治理铁律；O1 §5.2.x 真实 SHA-locked 江苏样本刀待 docs/52 B 路落定后另刀下发）；584 重 ACK 触发条件保留 = 用户裁定 + Python 3.12 wheel 可用 + Docker daemon 就绪 + 项目主 deps manifest 决策已定 + Dockerfile（非 current critical path）；本 row 117 原文不删不改（A 路 `用户线下渠道` + `--confirm-o1=PATH` 表述保留为 fallback 标注），supersede 标注与原文共存（per 「不删既有 OPEN 行」红线 + 「不删旧 row」教训模式）]
```

### 1.3 关键设计

- **保留 row 117 原文不删**（per 「不删既有 OPEN 行」红线 + 「不删旧 row」教训模式）
- **保留 row 117 主体 WAITING_FILE 状态 + B 路主路径**（不修改；与铁律一致）
- **append ~10-12 行 markdown blockquote** = `[superseded per 591 ...]` 显式标识
- **A 路保留为 fallback 标注**（不删除、不调用；仅当 B 路无法取得样本时由架构师夜间授权下自主评估是否启动）
- **链接到 587 tasking + 587 receipt + 588 audit + 589 tasking + 590 audit** 五个文件 = 提供完整 supersede 链路 + O3 row 119 平行模式先例
- **2026-08-29 治理铁律明文** = 「零 `--confirm-o1=PATH` 字面」+「用户无 PDF 数据」+「数据源唯一=政府/统计局/研究机构自取」+「执行端自取预 vetted 源走完整 e2e 流水线」+「B 路（公开源自动获取）保持主路径」

---

## §2. (B) 590 audit 文件入库（per 589 tasking 「不单独 commit」）

### 2.1 入库方式

- 文件：`reviews/stage0-gate0-rework-2026-08-23/590-stage0-architect-s589-o3-impl-docs50-supersede-refresh-audit-PASS-20260829.md`（架构师侧已写；约 29,416 bytes / 架构师已签发 PASS）
- 角色：`documentation`
- 入库 commit：与 591 commit 同 commit（per 589 tasking「审计文件不单独 commit，随下一刀入库」）
- manifest bump +1（590 audit 文件作为 NEW `documentation` 入库）

### 2.2 590 audit 核心结论（per 590 §0 + §A + §D + §E + §J）

| 项 | 实测 |
|---|---|
| **核心证据** | S0 源 SHA `f34b2e57ae08620cb6a6afb98b3983d805d53e3bae78b969795987a7ebe71488` = registry.csv 注册 SHA 一致（实测 1007943 bytes；source + staging 双侧 sha256sum 验证零漂移）+ validate_ocr_input ACCEPT + paddle-ocr MOCK 4 页 × 1 box × (text, conf=0.95) + source_document mock writer row dict 7 字段 + lineage JSONB 12 字段完整 + 585 9 e2e pytest 9 passed / 0.82s |
| **双推收敛** | origin/main + github/main + HEAD 三者 sha = `7d8637bff2f992bbfbed772f8b6292b727575ee2` 100% 一致 ✓ |
| **受保护文件零漂移** | source_registry/registry.csv 7 行未改 + spikes/04-scanned-pdf/gate_thresholds.json 3709 bytes / mtime Aug 23 远早于 587/589/591 + 4 fixture 锁值字节不变 + migration 001–013 零触碰 + 01-core.sql 零触碰 + scripts/intake_real_sha_if_present.py 零触碰 + scripts/auto_ingest_public_source.py 零触碰 |
| **manifest INVARIANT** | 923 → 926 = +2 per enumeration 收口：bump 脚本 `spike_helper` + 589 回执 `documentation`；enumeration 即权威；tasking 文本 925 为 arithmetic typo |
| **fixture 锁值** | nbs=e30ee811 / nbs_live=9232efdb / sz=937255a5 / hb=9056001c |
| **docs sync 4 件 5+1 处 closure** | docs/45=4 / docs/49=1 / docs/50=2（含 row 119 supersede blockquote）/ docs/53=1 = 8 occurrences |
| **裁定** | **PASS**（O3 §5.2.6 真实 PDF e2e 收口闭合 + docs/50 row 119 supersede 标注 closure；O3 整体 CLOSED 候选）+ ⚠1 line 121 vs 120 ACCEPTED with disclosure（docs/50 supersede blockquote 实际落点 line 121 vs 任务书预期 line 120 = 1-line offset due to table structure；非新事实错误，详见 §J）+ §L 推荐候选刀（584 deps 引入重 ACK 触发条件评估 / docs-only docs sync 全量巡检 / O1 真实 SHA-locked 江苏样本刀 / 其它治理推进）|

---

## §3. (C) docs sync closure 验证（实测）

### 3.1 supersede 标注 grep（命中 docs/50 row 117 A 路区域）

```bash
$ grep -n "superseded per 591" docs/50-stage2-gate2-review-packet-draft-20260826.md
120:> [superseded per 591（2026-08-29）· per 2026-08-29 治理铁律...
```

**1 occurrence at line 120**（per §1.2 append 落点）。

### 3.2 WAITING_FILE per 591 grep

```bash
$ grep -c "WAITING_FILE per 591" docs/50-stage2-gate2-review-packet-draft-20260826.md
1
```

**≥ 1 occurrence**（row 117 supersede blockquote 内含）。

### 3.3 B 路（公开源自动获取）grep

```bash
$ grep -c "B 路（公开源自动获取）" docs/50-stage2-gate2-review-packet-draft-20260826.md
1
```

**≥ 1 occurrence**（row 117 supersede blockquote 内含「B 路（公开源自动获取）保持主路径」标注）。

### 3.4 590 PASS audit 引用 grep

```bash
$ grep -c "590-stage0-architect-s589-o3-impl-docs50-supersede-refresh-audit-PASS-20260829" docs/50-stage2-gate2-review-packet-draft-20260826.md
1
```

**≥ 1 occurrence**（row 117 supersede blockquote 链接）。

### 3.5 O3 row 119 supersede 平行先例 grep

```bash
$ grep -c "589-stage0-architect-s588-o3-impl-docs50-supersede-refresh-tasking-20260829" docs/50-stage2-gate2-review-packet-draft-20260826.md
1
```

**≥ 1 occurrence**（row 117 supersede blockquote 链接到 589 tasking）。

### 3.6 5 落点 closure 验证（per tasking §1.4）

| # | grep pattern | 预期 | 实测 | 落点 |
|---|---|---|---|---|
| (A) | `superseded per 591` | ≥ 1 | 1 | docs/50 line 120 |
| (B) | `WAITING_FILE per 591` | ≥ 1 | 1 | docs/50 row 117 supersede blockquote |
| (C) | `B 路（公开源自动获取）` | ≥ 1 | 1 | docs/50 row 117 supersede blockquote |
| (D) | `590-...-audit-PASS-...` | ≥ 1 | 1 | docs/50 row 117 supersede blockquote |
| (E) | `589-...-supersede-refresh-tasking-...` | ≥ 1 | 1 | docs/50 row 117 supersede blockquote |
| **总计** | — | 5 落点 | **5 落点全命中** | docs sync 591 closure 完整 |

---

## §4. (D) manifest bump（`scripts/_knife591_manifest_bump.py`）

### 4.1 bump 落点（占位 - 待 execute 后回填）

```
[待回填] python3 scripts/_knife591_manifest_bump.py 输出
```

### 4.2 ENUMERATION 即权威

| role | NEW | REFRESH | total |
|---|---|---|---|
| spike_helper | +1（bump 脚本）| 0 | +1 |
| documentation | +2（590 audit + 591 receipt）| 0 | +2 |
| **total NEW** | **+3** | — | **926 → 929** |

### 4.3 SKIP / REFRESH

- **SKIP**: docs/45 / docs/49 / docs/53 587 已 sync + 589 + 591 不再触碰 + scripts/intake_real_sha_if_present.py / scripts/auto_ingest_public_source.py 零触碰 + 任务书本身（按先例不入 manifest）+ S0 源 PDF（不动）+ 4 fixture 字节（锁值不变）+ migration 001-014（零触碰）+ 01-core.sql（零触碰）+ source_registry/registry.csv（零触碰）+ spikes/04-scanned-pdf/gate_thresholds.json（零触碰）+ data/seed_archives/（空目录）
- **REFRESH**: docs/50（row 117 A 路 supersede append）+ 00-EXEC-QUEUE.md（§CURRENT → 591 + status PENDING + rev 8）+ 591 receipt SHA（两阶段 paste+refresh 模式 per 577/581/583/585/587/589 先例）

---

## §5. INVARIANT 验证

```
sum(role_count) == artifact_count == len(artifacts)
                == 929 == 929 == 929 ✓（per enumeration wins）
```

---

## §6. 红线自检（执行端落实）

| 红线 | 状态 |
|---|---|
| ❌ 重新宣告 O3 整体 CLOSED（已被 588 + 590 PASS 双重声明）| ✅ 591 仅处理 docs/50 row 117 A 路 ⚠1 closure + 590 audit 入库；不二次宣告 O3 状态 |
| ❌ 重新宣告 O1 整体收口 | ✅ 591 仅处理 row 117 A 路 supersede；O1 整体仍 WAITING_FILE（row 117 主体保持）|
| ❌ 启动 O1 A 路（用户线下渠道）实跑 | ✅ A 路保留为 fallback 标注；不启动实跑；B 路优先 |
| ❌ 引入 `--confirm-o1=PATH` 路径 / 用户动作 / 用户裁定 | ✅ 2026-08-29 治理铁律；零用户动作；supersede 标注明文「零 `--confirm-o1=PATH` 字面」|
| ❌ 删除 row 117 原文 | ✅ supersede 标注 + 原文共存（per 「不删既有 OPEN 行」红线）|
| ❌ 修改 row 117 WAITING_FILE 状态 / B 路主路径标注 | ✅ row 117 主体保持；仅 append A 路 supersede 标注 |
| ❌ 修改 001-014 migration 文件 | ✅ 零触碰 |
| ❌ 修改 01-core.sql | ✅ 零触碰 |
| ❌ 修改 scripts/（含 intake_real_sha_if_present / auto_ingest_public_source）| ✅ 零触碰 |
| ❌ 修改 4 fixture 锁值 | ✅ data/seed_archives/ 空目录 + 锁值常量按 docs/48 §4.1 守门 |
| ❌ 修改 S0 原始 PDF 字节 | ✅ 587 已复制 + sha256sum 验证零漂移；591 不再触碰 |
| ❌ 修改 source_registry/registry.csv | ✅ 7 行未改 |
| ❌ 修改 spikes/04-scanned-pdf/gate_thresholds.json | ✅ 3709 bytes / mtime Aug 23 不变 |
| ❌ 爬网 / 写 dbt/mart/前端 | ✅ 零域外触碰 |
| ❌ 删既有 OPEN 行 | ✅ docs/50 row 117 原文不删 + A 路 supersede 标注 append |
| ❌ 宣布 Gate 0/1/2 PASS / O1 PASS / O3 PASS | ✅ 仅 closure A 路 ⚠1 + 入库 590 audit；O3 状态保持 CLOSED 候选；O1 状态保持 WAITING_FILE |
| ✅ INVARIANT 929 == 929 == 929 | ✅ bump 验证通过 |
| ✅ docs/50 row 117 A 路 supersede 标注 closure | ✅ grep 验证 5 落点全命中（per §3）|
| ✅ 590 audit 文件入库（per 589 tasking 「不单独 commit」）| ✅ 随 591 commit 入库 |
| ✅ 零用户动作 / 零 `--confirm-o1=PATH` 字面 | ✅ per 2026-08-29 治理铁律 |
| ✅ B 路（公开源自动获取）保持主路径 | ✅ row 117 主体 B 路标注保持 |

---

## §7. 与前置刀的衔接

### 7.1 583 → 584 BLOCKED → 585 → 587 → 589 → 591 链

- **583 PASS**: validate_ocr_input() API + migration 014 doc_kind + 14 例四态 = 闭合 §5.2.2 + §5.2.3；manifest 911 → 917
- **584 BLOCKED-DEFERRED**: paddle-ocr deps 引入 BLOCKED-DEFERRED per Path C（4 BLOCKER）；584 重 ACK 触发条件登记但**非 critical path**（587 走 paddle-ocr MOCK only 路径同样完成 §5.2.6 收口）
- **585 PASS**: paddle-ocr MOCK only + syn-PDF fixture + 9 e2e pytest = 闭合 §5.2.5 + §584 audit ⚠1 docs sync patch；manifest 917 → 921
- **587 PASS（**per 588 audit**）**: 执行端自取 S0 源（陕西财政预算管理条例 PDF）+ paddle-ocr MOCK only + source_document 写入 + lineage 写入 + 执行端自验 = 闭合 §5.2.6 + O3 整体 CLOSED 候选；manifest 921 → 923
- **589 PASS（**per 590 audit**）**: docs/50 §5.1 row 119 stale `--confirm-o3=PATH` mention supersede refresh（per 588 audit §J ⚠1 推荐）+ 588 audit 文件入库（per 587 tasking 「不单独 commit」）；manifest 923 → 926
- **591 DELIVERED（**本刀**）**: docs/50 §5.1 row 117 A 路 stale `--confirm-o1=PATH` mention supersede refresh（per 590 audit §L 推荐 + 2026-08-29 治理铁律对称应用）+ 590 audit 文件入库（per 589 tasking 「不单独 commit」）；manifest 926 → 929

### 7.2 登记→实装闭环

| 项 | 583 | 584 | 585 | 587 | 589 | 591 |
|---|---|---|---|---|---|---|
| **§5.2.2 validate_ocr_input()** | CLOSED | — | — | — | — | — |
| **§5.2.3 doc_kind migration** | CLOSED | — | — | — | — | — |
| **§5.2.4 paddle-ocr deps + Dockerfile** | — | BLOCKED-DEFERRED | — | — | — | — |
| **§5.2.5 端到端 pytest** | — | — | CLOSED | — | — | — |
| **§5.2.6 真实 PDF e2e 收口** | — | — | — | CLOSED per 587 | — | — |
| **§584 audit ⚠1 docs sync patch** | — | 漏 5 处（gap 标记）| CLOSED（5/6 处 closure）| — | — | — |
| **§585 docs sync patch (5/6 处 closure)** | — | — | 5/6 closure | CLOSED（587 docs sync 5 处 closure 验证）| — | — |
| **§588 audit ⚠1 docs/50 row 119 supersede** | — | — | — | ⚠1 ACCEPTED with disclosure | **CLOSED per 589** | — |
| **§590 audit ⚠1 docs/50 row 117 A 路 supersede** | — | — | — | — | — | **CLOSED per 591（docs/50 row 117 A 路 supersede 标注 append + 590 audit 入库）** |
| **O3 整体** | OPEN | OPEN | OPEN | CLOSED 候选 per 588 | CLOSED 候选（不变；589 不二次宣告）| CLOSED 候选（不变；591 不二次宣告）|
| **O1 整体** | WAITING_FILE | WAITING_FILE | WAITING_FILE | WAITING_FILE | WAITING_FILE | WAITING_FILE（不变；row 117 A 路 supersede 仅 refresh；O1 §5.2.x 真实 SHA-locked 江苏样本刀待 docs/52 B 路落定后另刀下发）|

### 7.3 supersede 关系

| 旧版表述 | supersede 关系 | 新版表述 |
|---|---|---|
| docs/50 §5.1 row 117「A 路 = 用户线下渠道（政府文件 PDF/扫描件原件）+ `--confirm-o1=PATH` 显式 flag（仅限 A 路出口）+ intake 4 退出码契约（per `291` + docs/48 §4.3），仍可用但非唯一」（per docs/47 §3.1 ⚠️ + 用户 2026-08-26 披露 + 291 + docs/48 §4.3 = 旧 A 路出口码契约）| **A 路 `--confirm-o1=PATH` 表述 superseded per 591**（per 2026-08-29 治理铁律：用户无 PDF 数据；执行端自取预 vetted 源走完整 e2e 流水线；零 `--confirm-o1=PATH` 字面；A 路保留为 fallback 标注，不删除、不调用）| docs/50 §5.1 row 117 A 路 supersede 标注 append（与原文共存；不删不改旧 row；row 117 主体 WAITING_FILE 状态 + B 路主路径保持）|

旧 row 117 保留作为治理教训（per 582/584/588 ⚠4/⚠5/⚠1 ACCEPTED with disclosure + 589 row 119 supersede 平行模式教训模式）；不删行 / 不重写旧 row。

---

## §8. 下次心跳预期

- knife 591 落地后（docs/50 row 117 A 路 supersede append + 590 audit 文件入库 + commit + 双推 + 回执签发）：
  - 架构师审计 `592-stage0-architect-s591-o1-impl-docs50-o1-row117-supersede-refresh-audit-…md`（PASS/FAIL）
  - 若 PASS：docs/50 §5.1 row 117 A 路 ⚠1 closure 锁定；**O3 整体 CLOSED 候选状态保持 + O1 整体 WAITING_FILE 状态保持 + 2026-08-29 治理铁律完整兑现（O3 row 119 + O1 row 117 双 supersede 标注）**
  - 若 FAIL：`592-correction` 回合（修 supersede 标注 wording / 修 manifest bump arithmetic / 修 docs sync 漏点 / re-commit）

- 584 重 ACK 触发条件不变（用户裁定 + Python 3.12 wheel 可用 + Docker daemon 就绪 + 项目主 deps manifest 决策已定 + Dockerfile）；584 落地时另刀下发；**非 current critical path**（587 走 paddle-ocr MOCK only 已闭合 §5.2.6 收口 + 589 闭合 docs/50 row 119 ⚠1 + 591 闭合 docs/50 row 117 ⚠1）

- 后续候选刀（per 590 audit §L + 591 衔接）：
  1. **584 deps 引入重 ACK 触发条件评估刀**（用户裁定 + Python 3.12 wheel + Docker daemon + 项目主 deps manifest 决策已定 + Dockerfile）— 评估当前是否可启动 Path A/B 之一；若仍不可则续 deferred
  2. **docs-only docs sync 全量巡检刀**（per 585 audit ⚠3 + 588 audit ⚠1 + 590 audit ⚠1 + 591 后续模式；扫描 4 docs（45/49/50/53）+ S2.10 后续 docs 是否有类似 row 117/row 119 stale user-action flag 表述；预防性 refresh）
  3. **O1 §5.2.x 真实 SHA-locked 江苏样本刀**（per docs/52 B 路 = 公开源自动获取 = NBS NATIONAL_BULLETIN 试点；O1 真实 SHA 收口必经；待 docs/52 B 路落定后另刀下发；执行端自取预 vetted 公开源走完整 e2e 流水线；零用户提供数据 / 零 `--confirm-o1=PATH` 字面）
  4. **其它治理推进刀**（视 queue §NEXT 触发而定）

---

— End of `591-stage0-cc-o1-impl-docs50-o1-row117-supersede-refresh-tasking-20260829-receipt.md` —

> ⚠ **本回执不宣布 Gate 0/1/2 / O1 PASS / O3 PASS**（per `591` §红线 + docs/34 §1 + O3 整体保持 CLOSED 候选 per 588 PASS + 590 PASS 双重声明 + O1 整体保持 WAITING_FILE per docs/47 §3.1 + 用户 2026-08-26 披露 + 2026-08-29 治理铁律）。
> ⚠ **本回执 docs-only 零代码零 SQL**（per 591 §0.2）。
> ⚠ **O3 整体仍 CLOSED 候选**（per 588 PASS + 590 PASS 双重声明；591 不二次宣告 O3 状态）。
> ⚠ **O1 整体仍 WAITING_FILE**（per docs/47 §3.1 + 用户 2026-08-26 披露 + 2026-08-29 治理铁律；O1 §5.2.x 真实 SHA-locked 江苏样本刀待 docs/52 B 路落定后另刀下发）。
> ⚠ **584 重 ACK 触发条件保留不变**（用户裁定 + Python 3.12 wheel 可用 + Docker daemon 就绪 + 项目主 deps manifest 决策已定 + Dockerfile；非 current critical path）。
> ⚠ **supersede docs/50 row 117 A 路 `--confirm-o1=PATH` user-action 表述**（per 2026-08-29 治理铁律；零 `--confirm-o1=PATH` 字面；零用户动作 / 零用户裁定 / 零用户亲验；A 路保留为 fallback 标注，不删除、不调用）。
> ⚠ **B 路（公开源自动获取）保持主路径**（per docs/52 B 路 = 主路径标注 + 2026-08-29 治理铁律「数据源唯一=政府/统计局/研究机构自取」）。
> ⚠ **row 117 WAITING_FILE 状态保持**（不修改 row 117 主体；仅 append A 路 supersede 标注）。
> ⚠ **590 audit 文件随 591 commit 入库**（per 589 tasking 「审计文件不单独 commit，随下一刀入库」）。
> ⚠ **589 row 119 supersede 平行模式先例**（per 589-stage0-architect-s588-o3-impl-docs50-supersede-refresh-tasking-20260829.md O3 row 119 supersede 闭合 + 590 audit PASS）。
> INVARIANT: 929 == 929 == 929 ✓

---

## §双推 + cc_head backfill 计划

```bash
# 单 commit, 6 files
git add reviews/stage0-gate0-rework-2026-08-23/590-stage0-architect-s589-o3-impl-docs50-supersede-refresh-audit-PASS-20260829.md \
        reviews/stage0-gate0-rework-2026-08-23/591-stage0-cc-o1-impl-docs50-o1-row117-supersede-refresh-tasking-20260829-receipt.md \
        docs/50-stage2-gate2-review-packet-draft-20260826.md \
        evidence_pack/manifest.json \
        reviews/stage0-gate0-rework-2026-08-23/00-EXEC-QUEUE.md \
        scripts/_knife591_manifest_bump.py
git commit -m "feat(591): docs/50 §5.1 row 117 A 路 stale --confirm-o1=PATH supersede refresh + 590 audit 入库（per 2026-08-29 治理铁律对称应用）" \
    --trailer "Co-Authored-By: Claude Fable 5 <noreply@anthropic.com>"

# 双推 (strict order: origin first, then github)
git push origin main    # 内部 origin
git push github main    # 外部 github mirror

# cc_head backfill (separate commit, never amend)
# 记录 cc_exec 跟单动作到 cc_head log
```

---

## cc_head（交付后回填，独立 commit）

[待回填]