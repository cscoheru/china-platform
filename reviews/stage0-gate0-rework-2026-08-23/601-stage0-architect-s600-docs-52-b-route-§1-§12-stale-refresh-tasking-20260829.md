# 601-stage0-architect-s600-docs-52-b-route-§1-§12-stale-refresh-tasking-20260829

> **任务书类型**: 架构师签发 → 执行端实施（per ARCH-PULSE step 3 verbatim 583/585/587/589/591/593/594/595/596/597/598/599/600 平行模式）
> **触发依据**: 600 audit §L 推荐 #1 采纳 599 audit §L 推荐 #1 候选 = docs/52 §1-§12 stale `--confirm-*` + `用户裁定` 行 selective refresh 收口刀
> **前置**: 599 PASS（docs/52 §13 B 路主路径收口 blockquote 已 append line 287）· 600 audit PASS（89/89 验证项 + 三侧收敛 `ce5a168`）
> **签发时间**: 2026-08-29
> **作者**: CC-arch（架构师；按 ARCH-PULSE step 3 verbatim 不写实现/不 commit/不 push）

---

## §0.1 本刀做

| 项 | 落地 |
|---|---|
| (A) docs/52 §1-§12 stale `--confirm-*` + `用户裁定` 行 selective refresh（per 599 仅 supersede line 14/21/110/146-152 五处 + §13 block；§1-§12 内其余 stale 行尚未逐处 supersede）| grep `docs/52` 命中 stale `--confirm-*` + `用户裁定` + `用户投递` 字面除 line 14/21/110/146-152 之外（如 line 11 `> 用户裁定：**D**`、line 144 `用户提供授权后`、line 169 `--enable-cloud-ocr=PROVIDER + 用户裁定`、line 236 `--enable-cloud-ocr=PROVIDER + 用户裁定`、line 260 `user 投递 → 自动化路径切换` + `用户裁定`），逐处 append supersede blockquote（per 589 + 591 + 593 + 595 + 596 + 597 + 599 平行模式）|
| (B) docs/51 stale `--confirm-o1=PATH` + `用户裁定` 字面 selective refresh（如有）| grep `docs/51-stage2-o1-drop-checklist-20260826.md` 命中 stale `--confirm-o1=PATH` + `用户裁定` 字面（line 7/10/11/19/71/83/95/96/117/121/136/138/161/175 等），append supersede blockquote（per 589 + 591 + 593 + 595 + 596 + 597 + 599 平行模式）；A 路（用户投递）保留为 fallback 标注（不删除、不调用）；docs/51 原文不删不改|
| (C) docs/53 stale `--confirm-live` + `等用户裁定` 字面 selective refresh（如有）| grep `docs/53-stage2-public-ingest-ops-handbook-20260826.md` 命中 stale `--confirm-live` + `等用户裁定` 字面（line 4/38/49/58/76/77/79/93 等），append supersede blockquote（per 589 + 591 + 593 + 595 + 596 + 597 + 599 平行模式）；B 路（公开源自动获取）保持主路径；docs/53 原文不删不改|
| (D) docs/45 §6.x 状态行 append（如 O1 §5.2.x 后续收口所需）| per docs-only refresh 房规：grep `docs/45-stage2-s210-lite-gate2-review-index-20260826.md` 命中 §6.1 / §6.2 / §6.3 OPEN 表述（如 5.2.4 / 5.2.5 / 5.2.6 后续 O1 §5.2.x 收口所需），append status 行（per 589 + 591 + 593 + 595 + 596 + 597 + 599 平行模式）；docs/45 原文不删不改|
| (E) manifest bump K → 947+K（K 仅在 docs/X 实际触碰 + 601 receipt + 可选 bump 脚本时累加）| per docs 房规 docs/X 命中行 supersede append NOT-IN-MANIFEST（不增计数，与 589 + 591 + 593 + 595 + 596 + 597 + 599 + 600 平行模式一致）；enumeration 即权威 per 583 §F；INVARIANT 947+K == 947+K == 947+K ✓|
| (F) 601 receipt 写回执 | 含 (A)(B)(C)(D)(E)(F) 六段交付 + 双推 + cc_head backfill + manifest INVARIANT 验证 + 13 受保护文件零漂移 + 31+ 红线 100% 兑现 + ⚠ disclosures（如有）|

---

## §0.2 本刀不做（执行端零擅自做）

| 禁止 | 守门 |
|---|---|
| ❌ Stage 0/Gate 1/2 PASS / O1 PASS / O3 PASS | ✅ 601 仅 docs-only refresh；O3 整体保持 CLOSED 候选 per 588+590+597+598+599+600 五重声明；O1 整体保持 WAITING_FILE |
| ❌ 2020-2025 batch work | ✅ 零批量 |
| ❌ HTTP source crawl | ✅ 零爬网 |
| ❌ OCR threshold lowering | ✅ 零阈值调整 |
| ❌ 1909-as-China | ✅ 零历史边界触碰 |
| ❌ --force | ✅ git push 走普通路径 |
| ❌ PAT request | ✅ 零 PAT |
| ❌ gate_thresholds.json edit | ✅ 3709 bytes / mtime Aug 23 不变 |
| ❌ 重新宣告 O3 整体 CLOSED | ✅ O3 状态保持 CLOSED 候选（仍待 588 + 590 + 597 + 598 + 599 + 600 六重声明 + 后续架构师 OK 后宣布）|
| ❌ 重新宣告 O1 整体收口 | ✅ O1 状态保持 WAITING_FILE |
| ❌ 启动 O1 A 路实跑 | ✅ A 路保留为 fallback 标注 |
| ❌ 引入 --confirm-* 字面（实跑）| ✅ 2026-08-29 治理铁律；零用户动作；零 `--confirm-*` 字面 |
| ❌ 修改 001-004 migration 文件 | ✅ 红线 / 零生产 schema 变更 |
| ❌ 修改 01-core.sql | ✅ 红线 / 零核心 schema 变更 |
| ❌ 修改 4 fixture 锁值 | ✅ 红线 / 4 fixture 字节不变 |
| ❌ 修改 S0 原始 PDF 字节 | ✅ 红线 / SHA 零漂移（`f34b2e57…` 1007943 bytes）|
| ❌ 修改 source_registry/registry.csv | ✅ 红线 / 7 行未改 |
| ❌ 修改 spikes/04-scanned-pdf/gate_thresholds.json | ✅ 红线 / 3709 bytes / mtime Aug 23 不变 |
| ❌ 修改 .venv-paddle 或 scripts/requirements-paddle.txt | ✅ 红线 / paddle-ocr 引擎依赖零域外触碰 |
| ❌ 修改 requirements-dbt.txt | ✅ 红线 / 9 行不变 |
| ❌ 修改 scripts/intake_real_sha_if_present.py + auto_ingest_public_source.py | ✅ 红线 / 零 scripts/ 触碰（除 K1 NEW bump 脚本）|
| ❌ 修改 docs/45 / docs/49 / docs/50 / docs/53 既有 OPEN 行原文 | ✅ 601 仅 selective refresh（per docs-only refresh 房规）；既有 OPEN 行零删减 |
| ❌ 删除命中行原文 | ✅ 红线 / 既有 OPEN 行零删减 |
| ❌ 真实 paddleocr API 调用 | ✅ 主测试套件永远 paddle-ocr MOCK only（per 585 §0.2）|
| ❌ 真实 PDF 上传 | ✅ 零真实 PDF 上传（per 587 守门）|
| ❌ 触真实 DB | ✅ 零真实 DB 写入 |
| ❌ 爬网 / 写 dbt/mart/前端 | ✅ 红线 / 零域外触碰（仅 docs/X selective refresh + grep 命中计数）|
| ❌ 引入 cloud OCR / GPU runtime | ✅ per 594 §0.2 红线延续 |
| ❌ docker daemon systemctl 操作 | ✅ Colima daemon 已就绪（595 落地）|
| ❌ 持久保留 paddle-ocr:v1 Docker image | ✅ per 596 §2.5 已清理 |
| ❌ 启动 584 BLOCKED 实跑 paddle-ocr deps 到 system | ✅ 仅 `.venv-paddle` venv |

---

## §1. 601 tasking 详情

### 1.1 (A) docs/52 §1-§12 stale `--confirm-*` + `用户裁定` 行 selective refresh

**触发条件**: `grep -n "\-\-confirm-\|用户裁定\|用户线下渠道\|用户提供\|用户亲验\|用户提供真实 PDF\|\-\-user-\*" docs/52-stage2-official-open-source-auto-ingest-plan-20260826.md` 命中行（除 line 14/21/110/146-152 之外 = 599 §13 blockquote 已覆盖），如 line 11 / 144 / 169 / 236 / 260 等。

**落地**: append supersede blockquote per 589 + 591 + 593 + 595 + 596 + 597 + 599 + 600 平行模式。

**grep 验证**: `grep "per 601（2026-08-29）" docs/52-stage2-official-open-source-auto-ingest-plan-20260826.md` 命中 ≥ 1 occurrence（docs/52 §1-§12 内 stale 行数；如 line 11 / 144 / 169 / 236 / 260）。

### 1.2 (B) docs/51 stale `--confirm-o1=PATH` + `用户裁定` 字面 selective refresh

**触发条件**: `grep -n "\-\-confirm-o1\|用户裁定\|用户线下渠道\|用户提供\|用户亲验\|\-\-user-\*" docs/51-stage2-o1-drop-checklist-20260826.md` 命中 ≥ 1 行且与 2026-08-29 治理铁律冲突。

**落地**: append supersede blockquote per 589 + 591 + 593 + 595 + 596 + 597 + 599 + 600 平行模式。

**grep 验证**: `grep "per 601（2026-08-29）" docs/51-stage2-o1-drop-checklist-20260826.md` 命中 ≥ 1 occurrence。

### 1.3 (C) docs/53 stale `--confirm-live` + `等用户裁定` 字面 selective refresh

**触发条件**: `grep -n "\-\-confirm-live\|等用户裁定\|用户裁定" docs/53-stage2-public-ingest-ops-handbook-20260826.md` 命中 ≥ 1 行且与 2026-08-29 治理铁律冲突。

**落地**: append supersede blockquote per 589 + 591 + 593 + 595 + 596 + 597 + 599 + 600 平行模式。

**grep 验证**: `grep "per 601（2026-08-29）" docs/53-stage2-public-ingest-ops-handbook-20260826.md` 命中 ≥ 1 occurrence。

### 1.4 (D) docs/45 §6.x 状态行 append（如 O1 §5.2.x 后续收口所需）

**触发条件**: `grep -n "## §6" docs/45-stage2-s210-lite-gate2-review-index-20260826.md` 命中 ≥ 1 行 + §6.x 内 OPEN 表述需 status append。

**落地**: append status 行（per 589 + 591 + 593 + 595 + 596 + 597 + 599 + 600 平行模式）；docs/45 原文不删不改。

**grep 验证**: `grep "per 601（2026-08-29）" docs/45-stage2-s210-lite-gate2-review-index-20260826.md` 命中 ≥ 1 occurrence。

### 1.5 (E) manifest bump

**落地**:
- `scripts/_knife601_manifest_bump.py` NEW spike_helper +1
- 600 audit 文件入库随 601 commit per docs 房规 documentation +1
- 601 receipt NEW documentation +1
- K = 3 基础（如 docs/X 实际触碰时累加；enumeration 即权威 per 583 §F）

**INVARIANT**: 947+K == 947+K == 947+K ✓

### 1.6 (F) 601 receipt 写回执

**落地**:
- (A)(B)(C)(D)(E)(F) 六段交付
- 双推 + cc_head backfill
- manifest INVARIANT 验证
- 13 受保护文件零漂移
- 31+ 红线 100% 兑现
- ⚠ disclosures（如有）

---

## §2. 验收清单

| # | 验证项 | 预期 |
|---|---|---|
| 1 | docs/52 §1-§12 stale refresh 落点 closure | ✅ 5+ 处 `per 601（2026-08-29）` 标识（line 11/144/169/236/260 等）|
| 2 | docs/51 stale `--confirm-o1=PATH` + `用户裁定` selective refresh | ✅ 1+ 处 `per 601（2026-08-29）` 标识 |
| 3 | docs/53 stale `--confirm-live` + `等用户裁定` selective refresh | ✅ 1+ 处 `per 601（2026-08-29）` 标识 |
| 4 | docs/45 §6.x 状态行 append（如有）| ✅ 1+ 处 `per 601（2026-08-29）` 标识（如适用）|
| 5 | manifest INVARIANT | ✅ 947+K == 947+K == 947+K |
| 6 | 13 受保护文件零漂移 | ✅ 全部 SHA + bytes 不变 |
| 7 | 31+ 红线 100% 兑现 | ✅ 全部 PASS |
| 8 | 双推 + cc_head backfill | ✅ 100% 收敛 |
| 9 | docs 房规 NOT-IN-MANIFEST | ✅ docs/X 命中行 supersede append 不增计数 |
| 10 | 既有 OPEN 行零删减 | ✅ 全部保留 |
| 11 | A 路保留为 fallback 标注 | ✅ 不删除、不调用 |
| 12 | B 路保持主路径 | ✅ docs/52 + docs/53 内 B 路标注完整 |

---

## §3. 与前置刀的衔接

| 刀 | 闭合项 | 状态 |
|---|---|---|
| 583 PASS | §5.2.2 validate_ocr_input() + §5.2.3 doc_kind migration | CLOSED |
| 584 BLOCKED-DEFERRED → CLOSED per 597 | §5.2.4 paddle-ocr deps + Dockerfile | CLOSED |
| 585 PASS | §5.2.5 端到端 pytest + §584 audit ⚠1 docs sync patch | CLOSED |
| 587 PASS | §5.2.6 真实 PDF e2e + O3 整体 CLOSED 候选 | CLOSED 候选 |
| 589/591/593/595/596/597/599 PASS | docs/45/49/50/51/52/53 六层 supersede 平行模式 + BLOCKER 5→0 闭环 | CLOSED |
| 600 PASS（per 600 audit）| docs/52 §13 B 路主路径收口 blockquote 已 append line 287 | CLOSED |
| **601（本刀）**| docs/52 §1-§12 stale refresh 收口刀 + docs/51 + docs/53 + docs/45 §6.x 状态行 append | docs-only refresh |

---

## §4. 关联文件清单

- 599 tasking：`reviews/stage0-gate0-rework-2026-08-23/599-stage0-architect-s598-docs-52-b-route-spec-refresh-tasking-20260829.md`（NOT-IN-MANIFEST per docs 房规）
- 599 receipt：`reviews/stage0-gate0-rework-2026-08-23/599-stage0-cc-docs-52-b-route-spec-refresh-tasking-20260829-receipt.md`（23,470B, sha=`34359f4e…`）
- 600 audit：`reviews/stage0-gate0-rework-2026-08-23/600-stage0-architect-s599-docs-52-b-route-spec-refresh-tasking-20260829-audit-PASS-20260829.md`
- 601 tasking 本文件：`reviews/stage0-gate0-rework-2026-08-23/601-stage0-architect-s600-docs-52-b-route-§1-§12-stale-refresh-tasking-20260829.md`
- docs/51：`docs/51-stage2-o1-drop-checklist-20260826.md`
- docs/52：`docs/52-stage2-official-open-source-auto-ingest-plan-20260826.md`
- docs/53：`docs/53-stage2-public-ingest-ops-handbook-20260826.md`
- docs/45：`docs/45-stage2-s210-lite-gate2-review-index-20260826.md`
- queue：`reviews/stage0-gate0-rework-2026-08-23/00-EXEC-QUEUE.md`（rev 17 → 18）

---

— End of `601-stage0-architect-s600-docs-52-b-route-§1-§12-stale-refresh-tasking-20260829.md` —
