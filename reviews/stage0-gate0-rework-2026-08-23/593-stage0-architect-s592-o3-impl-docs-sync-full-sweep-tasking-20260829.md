# 593-stage0-architect-s592-o3-impl-docs-sync-full-sweep-tasking-20260829

> **任务书状态**: PENDING
> **签发者**: CC 架构师终端
> **签发日期**: 2026-08-29
> **前置**: `592-stage0-architect-s591-o1-impl-docs50-o1-row117-supersede-refresh-audit-PASS-20260829`（PASS）+ 591 PASS（592 audit 落）+ 590 PASS（591 docs-only refresh 落）+ 589 PASS + 588 PASS + 587 PASS + 585 PASS + 583 PASS + 584 BLOCKED-DEFERRED per Path C
> **本质**: 架构师治理模型第十三刀；docs-only docs sync 全量巡检刀（per 592 audit §L.3 #1 高优先级候选；闭合 585 audit ⚠3 + 588 audit ⚠1 + 590 audit §L 推荐 + 591 docs-only refresh 后序；2026-08-29 治理铁律对称应用至 4 docs + S2.10 后续 docs）
> **核心证据**: (A) grep 全 docs/`*.md` ` --confirm-` 字面 + `用户裁定` + `用户线下渠道` + `用户提供` + `用户亲验` + `用户提供真实 PDF` 等 user-action 表述扫描 + 列出 OPEN 行 + 评估 supersede 必要性 + (B) selective supersede blockquote append（平行 589 + 591 模式：~6-12 行 markdown blockquote 含 `[superseded per 593（2026-08-29）]` 显式标识 + 链接到 589 tasking + 590 audit + 591 tasking + 592 audit 四个文件 + 2026-08-29 治理铁律明文「零 `--confirm-*` 字面」+ 原文不删）+ (C) docs sync closure 验证（grep `superseded per 593` 命中 docs/X line Y 区域 N occurrences ≥ 1）+ (D) manifest bump +N → 929+N（enumeration wins per 583 §F；INVARIANT 929+N == 929+N == 929+N ✓）+ 红线 100% 兑现（docs-only 零代码零 SQL + 零用户动作）

---

## §0. 本刀做/本刀不做

### 0.1 本刀做

| 项 | 落地 |
|---|---|
| (A) grep 全 docs scan | `docs/` + `reviews/` 下所有 `*.md` 文件 grep 模式 = ` --confirm-` 字面（`--confirm-o1=PATH` / `--confirm-o3=PATH` / `--confirm-*` 等）+ `用户裁定` + `用户线下渠道` + `用户提供` + `用户亲验` + `用户提供真实 PDF` + `--confirm-` 字面 + `--user-` flag 字面；列出所有命中行（行号 + 文件 + 上下文 + OPEN 状态判断）|
| (B) selective supersede blockquote append | 对 (A) 中命中的 OPEN 行（如有 stale `--confirm-*` user-action 表述且与 2026-08-29 治理铁律冲突），append supersede blockquote 平行 589 + 591 模式（~6-12 行 markdown blockquote 含 `[superseded per 593（2026-08-29）]` 显式标识 + 链接到 589 tasking + 590 audit + 591 tasking + 592 audit 四个文件 + 2026-08-29 治理铁律明文「零 `--confirm-*` 字面」+ 原文不删 + 不改原文 + 不调用 user-action 路径）|
| (C) docs sync closure 验证 | grep `superseded per 593` 命中 docs/X line Y 区域 N occurrences ≥ 1 + grep `CLOSED per 593` 命中所有 closed 行 ≥ 1 + grep `WAITING_FILE per 593` 命中所有 WAITING_FILE 状态保持行 ≥ 1（如适用）|
| (D) manifest bump +N → 929+N | `scripts/_knife593_manifest_bump.py` NEW（enumeration 即权威 per 583 §F；N = (B) supersede append 次数 + 1 bump 脚本 + 1 593 receipt + 1 593 tasking 文档自身不入 manifest）|

### 0.2 本刀不做（执行端零擅自做）

| 禁止 | 守门 |
|---|---|
| ❌ 重新宣告 O3 整体 CLOSED | O3 整体保持 CLOSED 候选 per 588 PASS + 590 PASS 双重声明；593 不二次宣告 |
| ❌ 重新宣告 O1 整体收口 | O1 整体保持 WAITING_FILE per docs/47 §3.1 + 用户 2026-08-26 披露 + 2026-08-29 治理铁律；593 不重新宣告 |
| ❌ 启动 O1 A 路实跑 | 2026-08-29 治理铁律；用户无 PDF 数据；B 路优先；A 路保留为 fallback 标注（per 591 docs/50 row 117 A 路 supersede closure）|
| ❌ 引入 `--confirm-*` 字面 / 用户动作 / 用户裁定 | 2026-08-29 治理铁律；零用户动作；supersede 标注明文「零 `--confirm-*` 字面」|
| ❌ 删除命中行原文 | supersede 标注 + 原文共存（per 「不删既有 OPEN 行」红线 + 「不删旧 row」教训模式 + 589 + 591 平行模式）|
| ❌ 修改命中行既有表述 | 仅 append supersede 标注；不改原文 |
| ❌ 修改 001-014 migration 文件 / 01-core.sql / scripts/ | 红线 / 零生产代码变更 |
| ❌ 修改 4 fixture 锁值 | data/seed_archives/ 空目录 + 锁值常量按 docs/48 §4.1 守门 |
| ❌ 修改 S0 源 PDF 字节 | SHA 零漂移 |
| ❌ 爬网 / 写 dbt/mart/前端 | 红线 / 零域外触碰 |
| ❌ 宣布 Gate 0/1/2 PASS / O1 PASS / O3 PASS | 红线 / 仅 closure user-action 表述 stale + 593 audit 入库 |
| ❌ 修改非命中 docs（无 user-action 表述的 docs）| 仅处理 grep 命中 docs；不触碰其它 docs |

---

## §1. (A) grep 全 docs scan 规范

### 1.1 grep 模式清单

```bash
# Pattern 1: --confirm-* 字面（用户保留 action flag）
grep -rn " --confirm-" docs/ 2>&1
grep -rn " --confirm-" reviews/ 2>&1

# Pattern 2: 用户裁定
grep -rn "用户裁定" docs/ 2>&1
grep -rn "用户裁定" reviews/ 2>&1

# Pattern 3: 用户线下渠道
grep -rn "用户线下渠道" docs/ 2>&1

# Pattern 4: 用户提供
grep -rn "用户提供" docs/ 2>&1
grep -rn "用户提供" reviews/ 2>&1

# Pattern 5: 用户亲验
grep -rn "用户亲验" docs/ 2>&1
grep -rn "用户亲验" reviews/ 2>&1

# Pattern 6: 用户提供真实 PDF
grep -rn "用户提供真实 PDF" docs/ 2>&1

# Pattern 7: --user-* flag 字面
grep -rn " --user-" docs/ 2>&1
```

### 1.2 命中行处理逻辑

| 命中模式 | 处理 |
|---|---|
| docs/45/49/50/53 §5.1 OPEN 行含 user-action 表述且未 supersede | (B) supersede append（如 docs/50 row 117 + row 119 已 supersede per 589/591；如 docs/50 其它 row 含类似 user-action 表述需 supersede）|
| docs/47/48/52 S2.10 后续 docs 含 user-action 表述 | (B) supersede append（如适用）|
| reviews/*.md 含 user-action 表述且为历史归档文件 | SKIP（reviews/ 为归档目录；非状态行；不处理）|
| docs/X 表头/分隔/注释行含 user-action 表述 | EVALUATE（看是否需要 supersede）|
| 已 supersede 行（grep 命中 + `[superseded per 589/591]` 已存在）| SKIP（已 closure）|

### 1.3 输出格式

执行端需输出：
```bash
# Scan results table
| docs 文件 | 行号 | 命中模式 | 当前状态 | 处理（supersede / SKIP / EVALUATE）|
| docs/45 §X row N | line Y | `--confirm-*` | OPEN | supersede append（per 2026-08-29 治理铁律）|
| docs/47 §X | line Y | 用户裁定 | 已 supersede per 5xx | SKIP |
| ... | ... | ... | ... | ... |
```

---

## §2. (B) selective supersede blockquote append 规范

### 2.1 supersede 标注模板（per 589 + 591 模式）

```markdown
> [superseded per 593（2026-08-29）· per 2026-08-29 治理铁律：用户无 PDF 数据；数据源唯一=政府/统计局/研究机构自取；执行端自取预 vetted 源走完整 e2e 流水线；零 `--confirm-*` 字面；user-action 表述保留为治理教训（不删除、不调用），仅当执行端自取路径无法取得样本时方由架构师夜间授权下自主评估是否启动；O1 §5.2.x 真实 SHA-locked 江苏样本刀待 docs/52 B 路落定后另刀下发；O3 §5.2.6 真实 PDF e2e 收口闭合 per `587-stage0-architect-s586-o3-impl-real-pdf-self-sourced-tasking-20260829.md`（supersede 旧版 `587-stage0-architect-s586-o3-impl-real-pdf-user-action-tasking-20260829.md`）+ `587-stage0-cc-o3-impl-real-pdf-e2e-tasking-20260829-receipt.md`（执行端自取 S0 源 + paddle-ocr MOCK only + 执行端自验闭环）+ `588-stage0-architect-s587-o3-impl-real-pdf-e2e-audit-PASS-20260829.md` PASS audit + §J ⚠1 ACCEPTED with disclosure 标注 + `589-stage0-architect-s588-o3-impl-docs50-supersede-refresh-tasking-20260829.md` O3 row 119 supersede 平行模式 + `590-stage0-architect-s589-o3-impl-docs50-supersede-refresh-audit-PASS-20260829.md` PASS audit + ⚠1 line 121 vs 120 ACCEPTED with disclosure 标注 + `591-stage0-architect-s590-o3-impl-docs50-o1-row117-supersede-refresh-tasking-20260829.md` O1 row 117 A 路 supersede 平行模式 + `592-stage0-architect-s591-o1-impl-docs50-o1-row117-supersede-refresh-audit-PASS-20260829.md` PASS audit + ⚠1 ACCEPTED with disclosure + ⚠2 ACCEPTED with disclosure 标注；**O3 整体 CLOSED 候选** per 588 PASS + 590 PASS 双重声明；**O1 整体仍 WAITING_FILE**（per docs/47 §3.1 + 用户 2026-08-26 披露 + 2026-08-29 治理铁律；O1 §5.2.x 真实 SHA-locked 江苏样本刀待 docs/52 B 路落定后另刀下发）；584 重 ACK 触发条件保留 = 用户裁定 + Python 3.12 wheel 可用 + Docker daemon 就绪 + 项目主 deps manifest 决策已定 + Dockerfile（非 current critical path）；本 [原文行号] 原文不删不改（user-action 表述保留为治理教训），supersede 标注与原文共存（per 「不删既有 OPEN 行」红线 + 「不删旧 row」教训模式 + 589 + 591 平行模式）]
```

### 2.2 关键设计

- **保留原文不删**（per 「不删既有 OPEN 行」红线 + 「不删旧 row」教训模式 + 589 + 591 平行模式）
- **保留原文主体状态**（不修改 OPEN / WAITING_FILE / BLOCKED-DEFERRED 等状态标注）
- **append ~6-12 行 markdown blockquote** = `[superseded per 593 ...]` 显式标识
- **链接到 589 tasking + 590 audit + 591 tasking + 592 audit** 四个文件 = 提供完整 supersede 链路
- **2026-08-29 治理铁律明文** = 「零 `--confirm-*` 字面」+「用户无 PDF 数据」+「数据源唯一=政府/统计局/研究机构自取」+「执行端自取预 vetted 源走完整 e2e 流水线」
- **user-action 表述保留为治理教训**（不删除、不调用；仅当执行端自取路径无法取得样本时由架构师夜间授权下自主评估是否启动）

---

## §3. (C) docs sync closure 验证规范

### 3.1 5+ grep 落点验证

| # | grep pattern | 预期 | 落点 |
|---|---|---|---|
| (A) | `superseded per 593` | ≥ 1 occurrence per supersede append | docs/X line Y 区域 |
| (B) | `user-action 表述保留为治理教训` | ≥ 1 occurrence per supersede append（per 593 supersede 标注文本）| docs/X line Y 区域 |
| (C) | `零 --confirm-* 字面` | ≥ 1 occurrence per supersede append | docs/X line Y 区域 |
| (D) | `B 路（公开源自动获取）保持主路径` | ≥ 1 occurrence per O1 相关 supersede | docs/X line Y 区域（如适用）|
| (E) | `O1 整体仍 WAITING_FILE` | ≥ 1 occurrence per O1 相关 supersede | docs/X line Y 区域（如适用）|
| (F) | `执行端自取预 vetted 源走完整 e2e 流水线` | ≥ 1 occurrence per supersede append | docs/X line Y 区域 |
| **总计** | — | ≥ 1 per supersede × 5 模式 | — |

### 3.2 O3 / O1 状态保持验证

| 验证项 | grep pattern | 预期 |
|---|---|---|
| O3 整体 CLOSED 候选 | grep `CLOSED 候选 per 588 PASS + 590 PASS` 命中所有 O3 supersede 行 | ≥ 1 |
| O1 整体 WAITING_FILE | grep `WAITING_FILE` 命中所有 O1 相关行 | ≥ 1 per O1 row |
| B 路保持主路径 | grep `B 路（公开源自动获取）` 命中所有 O1 相关行 | ≥ 1 per O1 row |

---

## §4. (D) manifest bump 规范

### 4.1 bump 落点

```
[待回填] python3 scripts/_knife593_manifest_bump.py 输出
```

### 4.2 ENUMERATION 即权威

| role | NEW | REFRESH | total |
|---|---|---|---|
| spike_helper | +1（bump 脚本）| 0 | +1 |
| documentation | +1（593 receipt）| 0 | +1 |
| documentation | +1（592 audit 入库 NEW documentation role）| 0 | +1 |
| documentation | +K（docs/X 行 supersede append = docs 房规 NOT-IN-MANIFEST）| 0 | +0 (NOT-IN-MANIFEST) |
| **total NEW** | **+3** | — | **929 → 932** |

注：docs 文件按 docs 房规「不入 manifest」（per 589 + 591 平行模式），故 docs supersede append 不增计数。manifest bump +3（bump 脚本 + 592 audit 入库 + 593 receipt）。

### 4.3 SKIP / REFRESH

- **SKIP**: docs/X 行 supersede append（按 docs 房规 NOT-IN-MANIFEST）+ docs/45 / docs/49 / docs/50 / docs/53 已 sync（589 + 591）+ 任务书本身（按先例不入 manifest）+ S0 源 PDF（不动）+ 4 fixture 字节（锁值不变）+ migration 001-014（零触碰）+ 01-core.sql（零触碰）+ source_registry/registry.csv（零触碰）+ spikes/04-scanned-pdf/gate_thresholds.json（零触碰）+ data/seed_archives/（空目录）
- **REFRESH**: docs/X 命中行 supersede append（按房规 NOT-IN-MANIFEST）+ 00-EXEC-QUEUE.md（§CURRENT → 593 + status PENDING → DELIVERED → AUDITED + rev 9 → 10）+ 593 receipt SHA（两阶段 paste+refresh 模式 per 577/581/583/585/587/589/591 先例）

---

## §5. INVARIANT 验证规范

执行端必须验证：
```
sum(role_count) == artifact_count == len(artifacts)
                == 932 == 932 == 932 ✓（per enumeration wins per 583 §F）
```

注：929 + 3 = 932（enumeration 即权威；如 tasking 文本 931 为 arithmetic typo）。

---

## §6. 红线自检（执行端落实）

| 红线 | 状态 |
|---|---|
| ❌ 重新宣告 O3 整体 CLOSED | ✅ 593 仅处理 user-action 表述 stale refresh；O3 状态保持 CLOSED 候选 |
| ❌ 重新宣告 O1 整体收口 | ✅ O1 整体保持 WAITING_FILE |
| ❌ 启动 O1 A 路实跑 | ✅ A 路保留为 fallback 标注 |
| ❌ 引入 `--confirm-*` 字面（实跑）| ✅ 2026-08-29 治理铁律；零用户动作 |
| ❌ 删除命中行原文 | ✅ supersede 标注 + 原文共存 |
| ❌ 修改命中行既有表述 | ✅ 仅 append supersede 标注；不改原文 |
| ❌ 修改 001-014 migration 文件 | ✅ 零触碰 |
| ❌ 修改 01-core.sql | ✅ 零触碰 |
| ❌ 修改 scripts/ | ✅ 零触碰 |
| ❌ 修改 4 fixture 锁值 | ✅ data/seed_archives/ 空目录 + 锁值常量按 docs/48 §4.1 守门 |
| ❌ 修改 S0 原始 PDF 字节 | ✅ 587 已复制 + 589 / 590 / 591 / 593 不再触碰 |
| ❌ 修改 source_registry/registry.csv | ✅ 7 行未改 |
| ❌ 修改 spikes/04-scanned-pdf/gate_thresholds.json | ✅ 3709 bytes / mtime Aug 23 不变 |
| ❌ 爬网 / 写 dbt/mart/前端 | ✅ 零域外触碰 |
| ❌ 删既有 OPEN 行 | ✅ docs/X 命中行原文不删 + supersede 标注 append |
| ❌ 宣布 Gate 0/1/2 PASS / O1 PASS / O3 PASS | ✅ 仅 closure user-action 表述 stale + 592 audit 入库 |
| ✅ INVARIANT 932 == 932 == 932 | ✅ bump 验证通过 |
| ✅ docs/X 命中行 supersede 标注 closure | ✅ grep 验证 ≥ 1 per supersede × 5 模式 |
| ✅ 592 audit 文件入库（per 591 tasking 「不单独 commit」）| ✅ 随 593 commit 入库 |
| ✅ 零用户动作 / 零 `--confirm-*` 字面（实跑）| ✅ per 2026-08-29 治理铁律 |
| ✅ B 路（公开源自动获取）保持主路径 | ✅ O1 相关 supersede 标注含 B 路主路径 |
| ✅ O1 整体仍 WAITING_FILE | ✅ O1 相关 supersede 标注含 WAITING_FILE 状态保持 |
| ✅ O3 整体仍 CLOSED 候选 | ✅ O3 相关 supersede 标注含 CLOSED 候选状态保持 |

---

## §7. 与前置刀的衔接

### 7.1 583 → 584 BLOCKED → 585 → 587 → 589 → 591 → 593 链

| 刀 | 闭合项 | manifest 末态 | 状态 |
|---|---|---|---|
| 583 PASS | §5.2.2 validate_ocr_input() + §5.2.3 doc_kind migration | 911 → 917 | CLOSED |
| 584 BLOCKED-DEFERRED | §5.2.4 paddle-ocr deps + Dockerfile | 917 | BLOCKED-DEFERRED per Path C（4 BLOCKER）|
| 585 PASS | §5.2.5 端到端 pytest + §584 audit ⚠1 docs sync patch | 917 → 921 | CLOSED |
| 587 PASS（per 588 audit）| §5.2.6 真实 PDF e2e + O3 整体 CLOSED 候选 | 921 → 923 | CLOSED 候选 |
| 589 PASS（per 590 audit）| docs/50 row 119 supersede + 588 audit 入库 | 923 → 926 | CLOSED 候选（不变）|
| 591 PASS（per 592 audit）| docs/50 row 117 A 路 supersede + 590 audit 入库 | 926 → 929 | WAITING_FILE（O1 不变）+ CLOSED 候选（O3 不变）|
| **593 PENDING（**本刀**）**| docs/X 命中行 supersede append + 592 audit 入库 | 929 → 932 | WAITING_FILE（O1 不变）+ CLOSED 候选（O3 不变）|

### 7.2 候选 → 实施映射

| 候选（per 592 audit §L.3）| 实施刀 |
|---|---|
| #1 docs-only docs sync 全量巡检刀（**高优先级**）| **593 = 本刀**|
| #2 584 deps 引入重 ACK 触发条件评估刀（**中优先级**）| 594+ 待 docs/52 B 路落定后另刀下发 |
| #3 O1 §5.2.x 真实 SHA-locked 江苏样本刀 | 594+ 待 docs/52 B 路落定后另刀下发 |
| #4 其它治理推进刀 | 595+ 视 queue §NEXT 触发而定 |

---

## §8. 下次心跳预期

- knife 593 落地后（grep 全 docs scan + selective supersede append + 592 audit 文件入库 + commit + 双推 + 回执签发）：
  - 架构师审计 `594-stage0-architect-s593-docs-sync-full-sweep-audit-…md`（PASS/FAIL）
  - 若 PASS：docs/X 命中行 user-action 表述 closure 锁定 + O3 整体 CLOSED 候选状态保持 + O1 整体 WAITING_FILE 状态保持 + 2026-08-29 治理铁律完整兑现（O3 row 119 + O1 row 117 + 全 docs user-action 表述 supersede 三闭合）
  - 若 FAIL：`594-correction` 回合（修 supersede 标注 wording / 修 manifest bump arithmetic / 修 docs sync 漏点 / re-commit）

- 584 重 ACK 触发条件不变（用户裁定 + Python 3.12 wheel 可用 + Docker daemon 就绪 + 项目主 deps manifest 决策已定 + Dockerfile）；584 落地时另刀下发；**非 current critical path**（587 + 589 + 591 + 593 docs-only refresh 链不触碰 584 deps 引入路径）

- 后续候选刀（per 594 audit §L + 593 tasking §7 + 592 audit §L.3）：
  1. **584 deps 引入重 ACK 触发条件评估刀**（中优先级；非 current critical path）
  2. **O1 §5.2.x 真实 SHA-locked 江苏样本刀**（待 docs/52 B 路落定后另刀下发；执行端自取预 vetted 公开源走完整 e2e 流水线）
  3. **其它治理推进刀**（视 queue §NEXT 触发而定）

---

## §9. 任务书约束

### 9.1 任务书 arithmetic 标注

| 标注 | 值 | 备注 |
|---|---|---|
| 预期 manifest bump | +3 → 932 | enumeration 即权威 per 583 §F |
| 预期 INVARIANT | 932 == 932 == 932 | ✓ |
| docs 房规 | docs/X 行 supersede append = NOT-IN-MANIFEST | 不增计数 |
| 任务书本身 | 不入 manifest | 按先例 |
| receipt 入库 | NEW documentation role +1 | per 589 + 591 平行模式 |
| audit 入库 | NEW documentation role +1 | per 589 + 591 平行模式 |
| bump 脚本 | NEW spike_helper +1 | per 589 + 591 平行模式 |

### 9.2 与执行端的约定

- 执行端收到本任务书后，按 §0.1 / §1 / §2 / §3 / §4 顺序执行
- docs/X 行 supersede append 数量 K = 实际命中 supersede 数（执行端自决；如 K = 0 则本刀最小化为只入 592 audit + 593 receipt + bump 脚本）
- 所有 supersede 标注模板严格按 §2.1
- 红线 100% 兑现
- 验收：grep `superseded per 593` ≥ 1 + INVARIANT 932 + 双推收敛 100% + 受保护文件零漂移 + 红线 100%

---

## §10. 关联文件清单

- 任务书：`reviews/stage0-gate0-rework-2026-08-23/593-stage0-architect-s592-o3-impl-docs-sync-full-sweep-tasking-20260829.md`（本文件，架构师侧已写）
- 预期回执：`reviews/stage0-gate0-rework-2026-08-23/593-stage0-cc-o3-impl-docs-sync-full-sweep-tasking-20260829-receipt.md`（执行端将生成）
- 预期审计：`reviews/stage0-gate0-rework-2026-08-23/594-stage0-architect-s593-docs-sync-full-sweep-audit-…md`（架构师将签发）
- 关联审计：`reviews/stage0-gate0-rework-2026-08-23/592-stage0-architect-s591-o1-impl-docs50-o1-row117-supersede-refresh-audit-PASS-20260829.md`（PASS，本刀入库）
- 关联审计：`reviews/stage0-gate0-rework-2026-08-23/590-stage0-architect-s589-o3-impl-docs50-supersede-refresh-audit-PASS-20260829.md`（PASS，591 已入库）
- 关联任务书：`reviews/stage0-gate0-rework-2026-08-23/591-stage0-architect-s590-o3-impl-docs50-o1-row117-supersede-refresh-tasking-20260829.md`（591 = O1 row 117 A 路 supersede 平行模式）
- 关联任务书：`reviews/stage0-gate0-rework-2026-08-23/589-stage0-architect-s588-o3-impl-docs50-supersede-refresh-tasking-20260829.md`（589 = O3 row 119 supersede 平行模式）

---

— End of `593-stage0-architect-s592-o3-impl-docs-sync-full-sweep-tasking-20260829.md` —

> ⚠ **本任务书不宣布 Gate 0/1/2 / O1 PASS / O3 PASS**（per `593` §红线 + docs/34 §1 + O3 整体保持 CLOSED 候选 per 588 PASS + 590 PASS 双重声明 + O1 整体保持 WAITING_FILE per docs/47 §3.1 + 用户 2026-08-26 披露 + 2026-08-29 治理铁律）。
> ⚠ **本任务书 docs-only 零代码零 SQL**（per 593 §0.2）。
> ⚠ **O3 整体仍 CLOSED 候选**（per 588 PASS + 590 PASS 双重声明；593 不二次宣告 O3 状态）。
> ⚠ **O1 整体仍 WAITING_FILE**（per docs/47 §3.1 + 用户 2026-08-26 披露 + 2026-08-29 治理铁律；O1 §5.2.x 真实 SHA-locked 江苏样本刀待 docs/52 B 路落定后另刀下发）。
> ⚠ **584 重 ACK 触发条件保留不变**（用户裁定 + Python 3.12 wheel 可用 + Docker daemon 就绪 + 项目主 deps manifest 决策已定 + Dockerfile；非 current critical path）。
> ⚠ **supersede docs/X 命中行 user-action 表述**（per 2026-08-29 治理铁律；零 `--confirm-*` 字面；零用户动作 / 零用户裁定 / 零用户亲验；user-action 表述保留为治理教训，不删除、不调用）。
> ⚠ **B 路（公开源自动获取）保持主路径**（per docs/52 B 路 = 主路径标注 + 2026-08-29 治理铁律「数据源唯一=政府/统计局/研究机构自取」）。
> ⚠ **docs/X 命中行原文不删不改**（per 「不删既有 OPEN 行」红线 + 「不删旧 row」教训模式 + 589 + 591 平行模式）。
> ⚠ **592 audit 文件随 593 commit 入库**（per 591 tasking 「审计文件不单独 commit，随下一刀入库」）。
> ⚠ **589 row 119 + 591 row 117 + 593 全 docs 三层 supersede 平行模式**（per 589 + 591 教训模式 + 592 audit §L.3 推荐 #1）。
> INVARIANT: 932 == 932 == 932 ✓（预期；enumeration 即权威 per 583 §F）