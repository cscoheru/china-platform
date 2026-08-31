# 591-stage0-architect-s590-o3-impl-docs50-o1-row117-supersede-refresh-tasking-20260829

> **任务书状态**: PENDING
> **签发者**: CC 架构师终端
> **签发日期**: 2026-08-29
> **对应审计**: `590-stage0-architect-s589-o3-impl-docs50-supersede-refresh-audit-PASS-20260829.md`（PASS）
> **前置**: 590 PASS（591 audit 落）+ 589 PASS（590 audit 落）+ 588 PASS + 587 PASS + 585 PASS + 583 PASS + 584 BLOCKED-DEFERRED per Path C
> **本质**: ⚠1 docs/50 §5.1 row 117 stale `--confirm-o1=PATH` user-action mention supersede refresh刀（per 590 audit §L 推荐 + 2026-08-29 治理铁律对称应用 = O3 row 119 supersede 已 per 589 闭合 + O1 row 117 supersede 待 per 591 闭合）+ 590 audit 文件入库（per tasking「审计文件不单独 commit，随下一刀入库」）
> **本刀红线**: docs-only 零代码零 SQL；零用户动作 / 零 `--confirm-o1=PATH` 字面（per 2026-08-29 治理铁律）；B 路（公开源自动获取）= 主路径保持；A 路（用户线下渠道）= 保留为 fallback 标注，不删除
> **O3 整体仍 CLOSED 候选**（per 588 PASS + 590 PASS 双重声明；591 是 O1 row 117 supersede refresh 平行刀，不重新宣告 O3 状态，不涉及 O1 整体收口）

---

## §0. 任务背景与边界

### 0.1 ⚠1 来源

`590-stage0-architect-s589-o3-impl-docs50-supersede-refresh-audit-PASS-20260829.md` §L 推荐：「下一刀待架构师签发」候选 = 584 deps 引入重 ACK 触发条件评估刀 / docs-only docs sync 全量巡检刀 / **O1 真实 SHA-locked 江苏样本刀** / 其它治理推进刀 — 任一由架构师定夺。

**架构师裁定**：本刀（591）= **docs-only docs/50 §5.1 row 117 stale `--confirm-o1=PATH` user-action mention supersede refresh刀**（per 589 平行模式 + 2026-08-29 治理铁律对称应用 = O3 row 119 supersede 已 per 589 闭合 + O1 row 117 supersede 待 per 591 闭合）。

**O1 row 117 stale 表述发现**：

docs/50 §5.1 row 117（line 117）原文仍含「**A 路 = 用户线下渠道（政府文件 PDF/扫描件原件）+ `--confirm-o1=PATH` 显式 flag（仅限 A 路出口）+ intake 4 退出码契约（per `291` + docs/48 §4.3），仍可用但非唯一**」

**与 2026-08-29 治理铁律矛盾**：
- 「**A 路 = 用户线下渠道（政府文件 PDF/扫描件原件）**」= 与 2026-08-29 治理铁律「数据源唯一=政府/统计局/研究机构自取」+「用户无 PDF 数据；用户零裁定」矛盾（用户 2026-08-26 已确认本机/仓库未持有江苏真实 SHA-locked 样本；用户 2026-08-29 进一步明确「我没有任何数据PDF文件」）
- 「**`--confirm-o1=PATH` 显式 flag**」= 与 2026-08-29 治理铁律「执行端零用户裁定事项」+「零用户提供 PDF」矛盾
- 「**（仅限 A 路出口）**」= 出口码契约仍依赖用户裁定动作（与 docs/48 §4.3 intake 4 退出码契约耦合 = 用户操作动作嵌入契约）
- 「**仍可用但非唯一**」= 隐含允许用户继续走 A 路（与铁律矛盾）

**row 117 主路径部分（与铁律一致，保留）**：
- 「**WAITING_FILE**（= intake 出口码 / mart 真 SHA 未入仓技术状态语义，非「等用户投喂才可继续」per `484`/`486`/`488`/`490` 对齐；用户 2026-08-26 确认本机/仓库**未持有**江苏真实 SHA-locked 样本；`lineage.source_file_sha256` 恒为 `'0'*64` 占位 per docs/47 §3.1 ⚠️）」= **2026-08-26 用户披露已落 row 117 主体**，WAITING_FILE 技术状态语义保留
- 「**主路径 = docs/52 B 路（公开源自动获取，试点轴 `NATIONAL_BULLETIN` per `480`/`482`）**」= **B 路已与铁律一致**（公开源自动获取 = 政府/统计局/研究机构自取），保留

**裁定**：row 117 主体（WAITING_FILE 状态 + 用户披露 + B 路主路径）保留；仅 A 路 `--confirm-o1=PATH` user-action flag 表述需 supersede refresh（per 589 平行模式）。

**594 重 ACK / docs 全量巡检 / O1 整体收口**留待后续刀（per 590 audit §L）；591 仅处理 row 117 A 路 supersede。

### 0.2 本刀做/本刀不做

**本刀做**：

1. **docs/50 §5.1 row 117 A 路 supersede refresh**（docs-only）：
   - 行尾 append 显式 supersede 标注：`[superseded per 591（2026-08-29）· per 2026-08-29 治理铁律：用户无 PDF 数据；数据源唯一=政府/统计局/研究机构自取；执行端自取预 vetted 源走完整 e2e 流水线；零 `--confirm-o1=PATH` 字面；A 路（用户线下渠道）保留为 fallback 标注（不删除、不调用），仅当 B 路（公开源自动获取）无法取得样本时方由架构师夜间授权下自主评估是否启动；O1 §5.2.x 真实 SHA-locked 江苏样本刀待 docs/52 B 路落定后另刀下发]`
   - 同步 append 链接到 `589-stage0-architect-s588-o3-impl-docs50-supersede-refresh-tasking-20260829.md`（O3 row 119 supersede 平行模式先例）+ `590-stage0-architect-s589-o3-impl-docs50-supersede-refresh-audit-PASS-20260829.md`（590 PASS audit + ⚠1 ACCEPTED with disclosure 标注）+ `docs/47 §3.1`（O1 用户披露行）+ `docs/52`（B 路公开源自动获取路径）+ 2026-08-29 治理铁律明文
   - 保留 row 117 原文不删（per 「不删既有 OPEN 行」红线 + 「不删旧 row」教训模式；supersede 标注与原文共存）

2. **590 audit 文件入库**：
   - 590 audit 文件本身在 589 commit 时尚未存在 → 现在由 591 commit 带入（per tasking「审计文件不单独 commit，随下一刀入库」）
   - `590-stage0-architect-s589-o3-impl-docs50-supersede-refresh-audit-PASS-20260829.md` 作为 NEW `documentation` 角色入 manifest

3. **docs/50 §5.1 row 117 closure 验证**（架构师侧审计可本地复跑）：
   - grep `superseded per 591` 命中 docs/50 §5.1 row 117 区域
   - grep `WAITING_FILE per 591` 命中 docs/50（row 117 supersede blockquote 内含）
   - grep `B 路（公开源自动获取）` 命中 docs/50（row 117 B 路主路径保持标注）
   - manifest INVARIANT `929 == 929 == 929` 验证

4. **manifest bump** +3 → 929（591 bump 脚本 `spike_helper` +1 + 590 audit `documentation` +1 + 591 receipt `documentation` +1；enumeration 即权威 per 583 §F）

**本刀不做（执行端零擅自做）**：

| 禁止 | 守门 |
|---|---|
| ❌ 重新宣告 O3 整体 CLOSED（已被 588 + 590 PASS 双重声明）| 591 仅处理 docs/50 row 117 A 路 ⚠1 closure + 590 audit 入库；不重新宣告任何 O3 状态 |
| ❌ 重新宣告 O1 整体收口（O1 §5.2.x 待 docs/52 B 路落定后另刀）| 591 仅处理 row 117 A 路 supersede；O1 整体仍 WAITING_FILE 状态（row 117 主体保持）|
| ❌ 启动 O1 A 路（用户线下渠道）实跑 | 2026-08-29 治理铁律；用户无 PDF 数据；B 路优先；A 路仅 fallback 标注 |
| ❌ 引入 `--confirm-o1=PATH` 路径 / 用户动作 / 用户裁定 | 2026-08-29 治理铁律；零用户动作；supersede 标注明文「零 `--confirm-o1=PATH` 字面」|
| ❌ 删除 row 117 原文 | supersede 标注 + 原文共存（per 「不删既有 OPEN 行」红线 + 「不删旧 row」教训模式）|
| ❌ 修改 row 117 WAITING_FILE 状态 / B 路主路径标注 | row 117 主体保持；仅 append A 路 supersede 标注 |
| ❌ 修改 001-014 migration 文件 / 01-core.sql / scripts/ | 红线 / 零生产代码变更 |
| ❌ 修改 4 fixture 锁值 | 锁值不变 |
| ❌ 修改 S0 源 PDF 字节 | SHA 零漂移 |
| ❌ 爬网 / 写 dbt/mart/前端 | 红线 / 零域外触碰 |
| ❌ 宣布 Gate 0/1/2 PASS / O1 PASS / O3 PASS | 红线 / 仅 closure A 路 ⚠1 + 入库 590 audit |

---

## §1. docs/50 §5.1 row 117 A 路 supersede refresh（per 2026-08-29 治理铁律）

### 1.1 row 117 原文（line 117）

```
| **O1** 真实 SHA-locked 江苏样本 | S1.18 DEMO 路径 | **WAITING_FILE**（= intake 出口码 / mart 真 SHA 未入仓技术状态语义，非「等用户投喂才可继续」per `484`/`486`/`488`/`490` 对齐；用户 2026-08-26 确认本机/仓库**未持有**江苏真实 SHA-locked 样本；`lineage.source_file_sha256` 恒为 `'0'*64` 占位 per docs/47 §3.1 ⚠️）| 主路径 = docs/52 B 路（公开源自动获取，试点轴 `NATIONAL_BULLETIN` per `480`/`482`）；A 路 = 用户线下渠道（政府文件 PDF/扫描件原件）+ `--confirm-o1=PATH` 显式 flag（仅限 A 路出口）+ intake 4 退出码契约（per `291` + docs/48 §4.3），仍可用但非唯一 |
```

### 1.2 row 117 A 路 supersede append（per 591；append 不删不改原文）

在 row 117 **紧邻下一行**（line 118 之前或 line 117 末尾）新增 supersede 标注段：

```markdown
| **O1** 真实 SHA-locked 江苏样本 | S1.18 DEMO 路径 | **WAITING_FILE**（= intake 出口码 / mart 真 SHA 未入仓技术状态语义，非「等用户投喂才可继续」per `484`/`486`/`488`/`490` 对齐；用户 2026-08-26 确认本机/仓库**未持有**江苏真实 SHA-locked 样本；`lineage.source_file_sha256` 恒为 `'0'*64` 占位 per docs/47 §3.1 ⚠️）| 主路径 = docs/52 B 路（公开源自动获取，试点轴 `NATIONAL_BULLETIN` per `480`/`482`）；A 路 = 用户线下渠道（政府文件 PDF/扫描件原件）+ `--confirm-o1=PATH` 显式 flag（仅限 A 路出口）+ intake 4 退出码契约（per `291` + docs/48 §4.3），仍可用但非唯一 |

> [superseded per 591（2026-08-29）· per 2026-08-29 治理铁律：用户无 PDF 数据；数据源唯一=政府/统计局/研究机构自取；执行端自取预 vetted 源走完整 e2e 流水线；零 `--confirm-o1=PATH` 字面；A 路（用户线下渠道）保留为 fallback 标注（不删除、不调用），仅当 B 路（公开源自动获取）无法取得样本时方由架构师夜间授权下自主评估是否启动；O1 §5.2.x 真实 SHA-locked 江苏样本刀待 docs/52 B 路落定后另刀下发；O3 §5.2.6 真实 PDF e2e 收口闭合 per `587-stage0-architect-s586-o3-impl-real-pdf-self-sourced-tasking-20260829.md`（supersede 旧版 `587-stage0-architect-s586-o3-impl-real-pdf-user-action-tasking-20260829.md`）+ `587-stage0-cc-o3-impl-real-pdf-e2e-tasking-20260829-receipt.md`（执行端自取 S0 源 + paddle-ocr MOCK only + 执行端自验闭环）+ `588-stage0-architect-s587-o3-impl-real-pdf-e2e-audit-PASS-20260829.md` PASS audit + §J ⚠1 ACCEPTED with disclosure 标注 + `589-stage0-architect-s588-o3-impl-docs50-supersede-refresh-tasking-20260829.md` O3 row 119 supersede 平行模式 + `590-stage0-architect-s589-o3-impl-docs50-supersede-refresh-audit-PASS-20260829.md` PASS audit + ⚠1 line 121 vs 120 ACCEPTED with disclosure 标注；**O3 整体 CLOSED 候选** per 588 PASS + 590 PASS 双重声明；**O1 整体仍 WAITING_FILE**（per docs/47 §3.1 + 用户 2026-08-26 披露 + 2026-08-29 治理铁律；O1 §5.2.x 真实 SHA-locked 江苏样本刀待 docs/52 B 路落定后另刀下发）；584 重 ACK 触发条件保留 = 用户裁定 + Python 3.12 wheel 可用 + Docker daemon 就绪 + 项目主 deps manifest 决策已定 + Dockerfile（非 current critical path）；本 row 117 原文不删不改（A 路 `用户线下渠道` + `--confirm-o1=PATH` 表述保留为 fallback 标注），supersede 标注与原文共存（per 「不删既有 OPEN 行」红线 + 「不删旧 row」教训模式）]
```

### 1.3 append 落点定位

- 位置：`docs/50-stage2-gate2-review-packet-draft-20260826.md` line 117 后（行 118 之前）
- 长度：~10-12 行 markdown blockquote（较 589 row 119 supersede 略长，因 row 117 内容更多 + A 路 fallback 标注需说明 + O3 平行模式链接 + O1 整体状态保持标注）
- 语法：`>` blockquote + `[superseded per 591 ...]` 显式标识 + 链接到 589 tasking + 590 audit + docs/47 §3.1 + docs/52 四个文件 + 2026-08-29 治理铁律明文

### 1.4 closure 验证（架构师侧可本地复跑）

```bash
# (A) grep supersede 标注
grep -n "superseded per 591" docs/50-stage2-gate2-review-packet-draft-20260826.md
# 预期: line 119 区域 1 occurrence（line 117 表格行 + 空行 118 + blockquote 119 = 与 589 row 119→121 平行模式；可能有 1-line offset due to blank separator）

# (B) grep WAITING_FILE per 591
grep -c "WAITING_FILE per 591" docs/50-stage2-gate2-review-packet-draft-20260826.md
# 预期: ≥ 1（row 117 supersede blockquote 内含）

# (C) grep B 路主路径保持
grep -c "B 路（公开源自动获取）" docs/50-stage2-gate2-review-packet-draft-20260826.md
# 预期: ≥ 1（row 117 B 路主路径标注保留；可能 row 117 主体也有 1 occurrence；supersede blockquote 引用至少 1 处）

# (D) grep 590 PASS audit 引用
grep -c "590-stage0-architect-s589-o3-impl-docs50-supersede-refresh-audit-PASS-20260829" docs/50-stage2-gate2-review-packet-draft-20260826.md
# 预期: ≥ 1（supersede blockquote 链接）

# (E) grep O3 row 119 supersede 平行先例
grep -c "589-stage0-architect-s588-o3-impl-docs50-supersede-refresh-tasking-20260829" docs/50-stage2-gate2-review-packet-draft-20260829.md
# 预期: ≥ 1（supersede blockquote 链接）
```

---

## §2. 590 audit 文件入库

### 2.1 入库方式

- 文件：`reviews/stage0-gate0-rework-2026-08-23/590-stage0-architect-s589-o3-impl-docs50-supersede-refresh-audit-PASS-20260829.md`（架构师侧已写）
- 角色：`documentation`
- 入库 commit：与 591 commit 同 commit（per tasking「审计文件不单独 commit，随下一刀入库」）
- manifest bump +1（590 audit 文件作为 NEW `documentation` 入库）

### 2.2 590 audit 文件角色对照

- `590-stage0-architect-s589-o3-impl-docs50-supersede-refresh-audit-PASS-20260829.md` = NEW documentation role = +1 artifact
- `591-stage0-cc-o1-impl-docs50-o1-row117-supersede-refresh-tasking-20260829-receipt.md` = NEW documentation role = +1 artifact
- `docs/50-stage2-gate2-review-packet-draft-20260826.md` = REFRESH documentation role = no count change
- `evidence_pack/manifest.json` = UPDATE（artifact_count 926 → 929）
- `reviews/stage0-gate0-rework-2026-08-23/00-EXEC-QUEUE.md` = REFRESH documentation role = no count change
- 总计：+2 NEW → 929

### 2.3 590 audit 关键结论（per 590 §0 + §A + §D + §E + §J）

- 双推收敛 `7d8637b` 三侧 100% 一致 ✓
- 9 e2e pytest 9 passed / 0.82s 复跑通过 ✓
- S0 源 SHA `f34b2e57…` 双侧 1007943 bytes 零漂移 ✓
- docs sync 4 件 5+1 处 closure 完整 ✓
- 588 audit 入库 + 589 receipt 入库 + bump 脚本入库 + manifest INVARIANT 926 == 926 == 926 ✓
- 红线 100% 兑现 ✓
- ⚠1 line 121 vs 120 ACCEPTED with disclosure ✓

---

## §3. manifest bump（`scripts/_knife591_manifest_bump.py`）

### 3.1 bump 落点

```
$ python3 scripts/_knife591_manifest_bump.py
ADD: scripts/_knife591_manifest_bump.py (NEW spike_helper role)
ADD: reviews/stage0-gate0-rework-2026-08-23/590-stage0-architect-s589-o3-impl-docs50-supersede-refresh-audit-PASS-20260829.md (NEW documentation role; per 589 audit 文件随下刀入库)
ADD: reviews/stage0-gate0-rework-2026-08-23/591-stage0-cc-o1-impl-docs50-o1-row117-supersede-refresh-tasking-20260829-receipt.md (NEW documentation role; 591 回执)
REFRESH: docs/50-stage2-gate2-review-packet-draft-20260826.md (SHA 更新; no count change; row 117 A 路 supersede 标注 append)
REFRESH: reviews/stage0-gate0-rework-2026-08-23/00-EXEC-QUEUE.md (SHA 更新; no count change)
UPDATE artifact_count: 926 → 929
INVARIANT: sum(role_count)=929 == artifact_count=929 == len(artifacts)=929
OK manifest updated; added 3 artifacts
```

### 3.2 ENUMERATION 即权威

| role | NEW | REFRESH | total |
|---|---|---|---|
| spike_helper | +1（bump 脚本）| 0 | +1 |
| documentation | +2（590 audit + 591 receipt）| 0 | +2 |
| **total NEW** | **+3** | — | **926 → 929** |

### 3.3 SKIP / REFRESH

- **SKIP**: 任务书本身（按先例不入 manifest）+ 591 audit 旧 row 文案（不删 / 不改）+ S0 源 PDF（不动）+ 4 fixture 字节（锁值不变）+ scripts/intake_real_sha_if_present.py（零触碰）+ scripts/auto_ingest_public_source.py（零触碰）+ migration 001–014（零触碰）+ 01-core.sql（零触碰）+ source_registry/registry.csv（零触碰）+ spikes/04-scanned-pdf/gate_thresholds.json（零触碰）+ data/seed_archives/（空目录）
- **REFRESH**: docs/50（row 117 A 路 supersede append）+ 00-EXEC-QUEUE.md（§CURRENT → 591 + status PENDING + rev 8）+ 591 receipt SHA（两阶段 paste+refresh 模式 per 577/581/583/585/587/589 先例）+ 590 audit 文件 SHA（首次入库；两阶段模式）

---

## §4. INVARIANT 验证

```
sum(role_count) == artifact_count == len(artifacts)
                == 929 == 929 == 929 ✓（per enumeration wins；docs/50 row 117 REFRESH 不增计数）
```

---

## §5. 红线自检（执行端落实）

| 红线 | 状态 |
|---|---|
| ❌ 重新宣告 O3 整体 CLOSED | ✅ 591 仅处理 docs/50 row 117 A 路 ⚠1 closure + 590 audit 入库；不重新宣告 O3 状态（O3 保持 CLOSED 候选 per 588 PASS + 590 PASS 双重声明）|
| ❌ 重新宣告 O1 整体收口 | ✅ 591 仅处理 row 117 A 路 supersede；O1 整体仍 WAITING_FILE（row 117 主体保持）|
| ❌ 启动 O1 A 路（用户线下渠道）实跑 | ✅ A 路保留为 fallback 标注；不启动实跑；B 路优先 |
| ❌ 引入 `--confirm-o1=PATH` 路径 / 用户动作 / 用户裁定 | ✅ 2026-08-29 治理铁律；零用户动作；supersede 标注明文「零 `--confirm-o1=PATH` 字面」|
| ❌ 删除 row 117 原文 | ✅ supersede 标注 + 原文共存（per 「不删既有 OPEN 行」红线）|
| ❌ 修改 row 117 WAITING_FILE 状态 / B 路主路径标注 | ✅ row 117 主体保持；仅 append A 路 supersede 标注 |
| ❌ 修改 001-014 migration 文件 | ✅ 零触碰 |
| ❌ 修改 01-core.sql | ✅ 零触碰 |
| ❌ 修改 scripts/（含 intake_real_sha_if_present / auto_ingest_public_source）| ✅ 零触碰 |
| ❌ 修改 4 fixture 锁值 | ✅ data/seed_archives/ 空目录 + 锁值常量按 docs/48 §4.1 守门 |
| ❌ 修改 S0 原始 PDF 字节 | ✅ 复制为新文件 + sha256sum 验证 = 原始 SHA |
| ❌ 修改 source_registry/registry.csv | ✅ 7 行未改 |
| ❌ 修改 spikes/04-scanned-pdf/gate_thresholds.json | ✅ 3709 bytes / mtime Aug 23 不变 |
| ❌ 爬网 / 写 dbt/mart/前端 | ✅ 零域外触碰 |
| ❌ 删既有 OPEN 行 | ✅ docs/50 row 117 原文不删 + A 路 supersede 标注 append |
| ❌ 宣布 Gate 0/1/2 PASS / O1 PASS / O3 PASS | ✅ 仅 closure A 路 ⚠1 + 入库 590 audit；O3 状态保持 590 PASS 后的 CLOSED 候选；O1 状态保持 WAITING_FILE |
| ✅ INVARIANT 929 == 929 == 929 | ✅ bump 验证通过 |
| ✅ docs/50 row 117 A 路 supersede 标注 closure | ✅ grep 验证（per §1.4）|
| ✅ 590 audit 文件入库（per 589 tasking 「不单独 commit」）| ✅ 随 591 commit 入库 |
| ✅ 零用户动作 / 零 `--confirm-o1=PATH` 字面 | ✅ per 2026-08-29 治理铁律 |

---

## §6. 与前置刀的衔接

### 6.1 583 → 584 BLOCKED → 585 → 587 → 589 → 591 链

- **583 PASS**: validate_ocr_input() API + migration 014 doc_kind + 14 例四态 = 闭合 §5.2.2 + §5.2.3；manifest 911 → 917
- **584 BLOCKED-DEFERRED**: paddle-ocr deps 引入 BLOCKED-DEFERRED per Path C（4 BLOCKER）；584 重 ACK 触发条件登记但**非 critical path**（587 走 paddle-ocr MOCK only 路径同样完成 §5.2.6 收口）
- **585 PASS**: paddle-ocr MOCK only + syn-PDF fixture + 9 e2e pytest = 闭合 §5.2.5 + §584 audit ⚠1 docs sync patch；manifest 917 → 921
- **587 PASS（**per 588 audit**）**: 执行端自取 S0 源 + paddle-ocr MOCK only + source_document 写入 + lineage 写入 + 执行端自验 = 闭合 §5.2.6 + O3 整体 CLOSED 候选；manifest 921 → 923
- **589 PASS（**per 590 audit**）**: docs/50 §5.1 row 119 stale `--confirm-o3=PATH` mention supersede refresh + 588 audit 文件入库 + docs sync 4 件 5+1 处 closure + manifest 923 → 926
- **591 PENDING（**本刀**）**: docs/50 §5.1 row 117 A 路 stale `--confirm-o1=PATH` mention supersede refresh（per 590 audit §L 推荐 + 2026-08-29 治理铁律对称应用）+ 590 audit 文件入库 + docs sync 5+1 处 closure（O3 row 119 + O1 row 117 双 supersede 标注）+ manifest 926 → 929

### 6.2 登记→实装闭环

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

### 6.3 supersede 关系

| 旧版表述 | supersede 关系 | 新版表述 |
|---|---|---|
| docs/50 §5.1 row 117「A 路 = 用户线下渠道（政府文件 PDF/扫描件原件）+ `--confirm-o1=PATH` 显式 flag（仅限 A 路出口）+ intake 4 退出码契约（per `291` + docs/48 §4.3），仍可用但非唯一」（per docs/47 §3.1 ⚠️ + 用户 2026-08-26 披露 + 291 + docs/48 §4.3 = 旧 A 路出口码契约）| **A 路 `--confirm-o1=PATH` 表述 superseded per 591**（per 2026-08-29 治理铁律：用户无 PDF 数据；执行端自取预 vetted 源走完整 e2e 流水线；零 `--confirm-o1=PATH` 字面；A 路保留为 fallback 标注，不删除、不调用）| docs/50 §5.1 row 117 A 路 supersede 标注 append（与原文共存；不删不改旧 row；row 117 主体 WAITING_FILE 状态 + B 路主路径保持）|

旧 row 117 保留作为治理教训（per 582/584/588 ⚠4/⚠5/⚠1 ACCEPTED with disclosure + 589 row 119 supersede 平行模式教训模式）；不删行 / 不重写旧 row。

---

## §7. 后续预期

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

## §8. cc_head backfill 计划

```bash
# 用户操作完成后 + 执行端自验 OK 后 + 执行端 commit + 双推
git add reviews/stage0-gate0-rework-2026-08-23/590-stage0-architect-s589-o3-impl-docs50-supersede-refresh-audit-PASS-20260829.md \
        reviews/stage0-gate0-rework-2026-08-23/591-stage0-cc-o1-impl-docs50-o1-row117-supersede-refresh-tasking-20260829-receipt.md \
        docs/50-stage2-gate2-review-packet-draft-20260826.md \
        evidence_pack/manifest.json \
        reviews/stage0-gate0-rework-2026-08-23/00-EXEC-QUEUE.md \
        scripts/_knife591_manifest_bump.py
git commit -m "feat(591): docs/50 §5.1 row 117 A 路 stale --confirm-o1=PATH supersede refresh + 590 audit 入库（per 2026-08-29 治理铁律对称应用）" \
    --trailer "Co-Authored-By: Claude Fable 5 <noreply@anthropic.com>"

# 双推 (strict order: origin first, then github)
git push origin HEAD
git push github HEAD

# cc_head backfill (separate commit, never amend)
# 记录 cc_exec 跟单动作到 cc_head log
```

---

— End of `591-stage0-architect-s590-o3-impl-docs50-o1-row117-supersede-refresh-tasking-20260829.md` —

> ⚠ **本任务书不宣布 Gate 0/1/2 / O1 PASS / O3 PASS**（per `591` §红线 + docs/34 §1 + O3 整体保持 CLOSED 候选 per 588 PASS + 590 PASS 双重声明 + O1 整体保持 WAITING_FILE per docs/47 §3.1 + 用户 2026-08-26 披露 + 2026-08-29 治理铁律）。
> ⚠ **本任务书 docs-only 零代码零 SQL**（per 591 §0.2）。
> ⚠ **O3 整体仍 CLOSED 候选**（per 588 PASS + 590 PASS 双重声明；591 不二次宣告 O3 状态）。
> ⚠ **O1 整体仍 WAITING_FILE**（per docs/47 §3.1 + 用户 2026-08-26 披露 + 2026-08-29 治理铁律；O1 §5.2.x 真实 SHA-locked 江苏样本刀待 docs/52 B 路落定后另刀下发）。
> ⚠ **584 重 ACK 触发条件保留不变**（用户裁定 + Python 3.12 wheel 可用 + Docker daemon 就绪 + 项目主 deps manifest 决策已定 + Dockerfile；非 current critical path）。
> ⚠ **supersede docs/50 row 117 A 路 `--confirm-o1=PATH` user-action 表述**（per 2026-08-29 治理铁律；零 `--confirm-o1=PATH` 字面；零用户动作 / 零用户裁定 / 零用户亲验；A 路保留为 fallback 标注，不删除、不调用）。
> ⚠ **B 路（公开源自动获取）保持主路径**（per docs/52 B 路 = 主路径标注 + 2026-08-29 治理铁律「数据源唯一=政府/统计局/研究机构自取」）。
> ⚠ **row 117 WAITING_FILE 状态保持**（不修改 row 117 主体；仅 append A 路 supersede 标注）。
> ⚠ **590 audit 文件随 591 commit 入库**（per 589 tasking 「审计文件不单独 commit，随下一刀入库」）。
> ⚠ **589 row 119 supersede 平行模式先例**（per 589-stage0-architect-s588-o3-impl-docs50-supersede-refresh-tasking-20260829.md O3 row 119 supersede 闭合 + 590 audit PASS）。
> INVARIANT: 929 == 929 == 929 ✓
