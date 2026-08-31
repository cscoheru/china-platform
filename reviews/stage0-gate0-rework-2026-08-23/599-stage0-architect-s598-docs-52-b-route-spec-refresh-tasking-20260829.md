# 599-stage0-architect-s598-docs-52-b-route-spec-refresh-tasking-20260829

> **任务书类型**: 架构师签发 → 执行端实施（per ARCH-PULSE step 3 verbatim 583/585/587/589/591/593/594/595/596/597/598 平行模式）
> **触发依据**: 598 audit §L 推荐 #1（采纳 597 audit §L 推荐 #1 候选）= docs/52 B 路 spec 落定刀
> **前置**: 597 PASS（584 §5.2.4 CLOSED per 597）· 598 audit PASS（O3 §5.2.4 CLOSED 候选 per 588 + 590 + 597 三重声明）
> **签发时间**: 2026-08-29
> **作者**: CC-arch（架构师；按 ARCH-PULSE step 3 verbatim 不写实现/不 commit/不 push）

---

## §0.1 本刀做

| 项 | 落地 |
|---|---|
| (A) docs/52 B 路 spec selective refresh（如有 stale `--confirm-*` 表述）| per 593 + 589 + 591 平行模式：grep `docs/52-stage2-official-open-source-auto-ingest-plan-20260826.md` 命中 `--confirm-*` 字面（如有）；append supersede blockquote（~6-12 行 markdown blockquote 含 `[superseded per 599（2026-08-29）]` 显式标识 + 链接到 587 tasking + 587 receipt + 588 audit + 589 tasking + 590 audit + 591 tasking + 592 audit + 593 tasking + 593 receipt + 594 tasking + 594 receipt + 595 tasking + 595 audit + 596 tasking + 596 audit + 597 tasking + 597 receipt + 598 audit 19 个文件 + 2026-08-29 治理铁律明文「零 `--confirm-*` 字面」+ 原文不删 + 不改原文 + 不调用 user-action 路径）|
| (B) 补 grep `执行端自取预 vetted 公开源走完整 e2e 流水线` 命中 docs/52 line Y | per docs-only refresh 房规：grep `执行端自取预 vetted 公开源走完整 e2e 流水线` 命中 docs/52 line Y 区域 ≥ 1 occurrence；如未命中则 append 该语句到 docs/52 收口段（line 100 之后任何合适位置）；不得触碰 B 路 11 + 主路径 8 既有 grep 命中数|
| (C) docs/47 + docs/48 stale user-action 表述 selective refresh（如有）| grep `docs/4[78]*.md` 命中 `--confirm-*` 字面（如有 stale user-action 表述与 2026-08-29 治理铁律冲突）；append supersede blockquote（per 589 + 591 + 593 + 595 + 596 + 597 平行模式）|
| (D) 写 docs/49 §5.2 + docs/50 §5.1 状态行 append（如 597 + 598 双重 CLOSED 声明）| per docs-only refresh 房规：append docs/49 §5.2 row 5.2.4 状态行 append（5.2.4 CLOSED per 597 + 598 audit 落 标注 共存）+ docs/50 §5.1 O3 状态行 append（5.2.4 CLOSED per 597 + 598 audit 落 标注 共存）|
| (E) manifest bump K → 944+K（K 仅在 docs/X 实际触碰 + 599 receipt + 可选 bump 脚本时累加）| per docs 房规 docs/X 命中行 supersede append NOT-IN-MANIFEST（不增计数，与 589 + 591 + 593 + 595 + 596 + 597 平行模式一致）；enumeration 即权威 per 583 §F；INVARIANT 944+K == 944+K == 944+K ✓|
| (F) 599 receipt 写回执 | 含 (A)(B)(C)(D)(E)(F) 六段交付 + 双推 + cc_head backfill + manifest INVARIANT 验证 + 13 受保护文件零漂移 + 30+ 红线 100% 兑现 + ⚠ disclosures（如有）|

---

## §0.2 本刀不做（执行端零擅自做）

| 禁止 | 守门 |
|---|---|
| ❌ Stage 0/Gate 1/2 PASS / O1 PASS / O3 PASS | ✅ 599 仅 docs-only refresh；O3 整体保持 CLOSED 候选 per 588+590+597 三重声明；O1 整体保持 WAITING_FILE |
| ❌ 2020-2025 batch work | ✅ 零批量 |
| ❌ HTTP source crawl | ✅ 零爬网 |
| ❌ OCR threshold lowering | ✅ 零阈值调整 |
| ❌ 1909-as-China | ✅ 零历史边界触碰 |
| ❌ --force | ✅ git push 走普通路径 |
| ❌ PAT request | ✅ 零 PAT |
| ❌ gate_thresholds.json edit | ✅ 3709 bytes / mtime Aug 23 不变 |
| ❌ 重新宣告 O3 整体 CLOSED | ✅ O3 状态保持 CLOSED 候选（仍待 588 + 590 + 597 三重声明 + 后续架构师 OK 后宣布）|
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
| ❌ 修改 docs/45 / docs/49 / docs/50 / docs/53 既有 OPEN 行原文 | ✅ 599 仅 selective refresh（per docs-only refresh 房规）；既有 OPEN 行零删减 |
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

## §1. 599 tasking 详情

### 1.1 (A) docs/52 B 路 spec selective refresh

**触发条件**: `grep -n "\-\-confirm-\|用户裁定\|用户线下渠道\|用户提供\|用户亲验\|用户提供真实 PDF\|\-\-user-\*" docs/52-stage2-official-open-source-auto-ingest-plan-20260826.md` 命中 ≥ 1 行且与 2026-08-29 治理铁律冲突。

**落地**: append supersede blockquote per 589 + 591 + 593 + 595 + 596 + 597 平行模式。

**grep 验证**: `grep "superseded per 599" docs/52-stage2-official-open-source-auto-ingest-plan-20260826.md` 命中 ≥ 1 occurrence。

### 1.2 (B) B 路保持主路径 grep 验证

**触发条件**: `grep "执行端自取预 vetted 公开源走完整 e2e 流水线" docs/52-stage2-official-open-source-auto-ingest-plan-20260826.md` 命中 ≥ 1 occurrence。

**落地**: 如未命中则 append 该语句到 docs/52 收口段；不得触碰 B 路 11 + 主路径 8 既有 grep 命中数。

### 1.3 (C) docs/47 + docs/48 stale user-action selective refresh

**触发条件**: `grep -n "\-\-confirm-\|用户裁定\|用户线下渠道\|用户提供\|用户亲验\|用户提供真实 PDF\|\-\-user-\*" docs/47*.md docs/48*.md` 命中 ≥ 1 行且与 2026-08-29 治理铁律冲突。

**落地**: append supersede blockquote per 589 + 591 + 593 + 595 + 596 + 597 平行模式。

**grep 验证**: `grep "superseded per 599" docs/47*.md docs/48*.md` 命中 ≥ 1 occurrence。

### 1.4 (D) docs/49 §5.2 + docs/50 §5.1 状态行 append

**落地**:
- docs/49 §5.2 row 5.2.4 状态行 append（5.2.4 CLOSED per 597 + 598 audit 落 标注 共存；不删 BLOCKED-DEFERRED 旧版）
- docs/50 §5.1 O3 状态行 append（5.2.4 CLOSED per 597 + 598 audit 落 标注 共存）

**grep 验证**: `grep "598 audit 落" docs/49*.md docs/50*.md` 命中 ≥ 2 occurrences（每 doc ≥ 1 occurrence）。

### 1.5 (E) manifest bump

**落地**:
- `scripts/_knife599_manifest_bump.py` NEW spike_helper +1
- 598 audit 文件入库随 599 commit per docs 房规 documentation +1
- 599 receipt NEW documentation +1
- K = 3 基础（如 docs/X 实际触碰时累加；enumeration 即权威 per 583 §F）

**INVARIANT**: 944+K == 944+K == 944+K ✓

### 1.6 (F) 599 receipt 写回执

**落地**:
- (A)(B)(C)(D)(E)(F) 六段交付
- 双推 + cc_head backfill
- manifest INVARIANT 验证
- 13 受保护文件零漂移
- 30+ 红线 100% 兑现
- ⚠ disclosures（如有）

---

## §2. 验收清单

| # | 验证项 | 预期 |
|---|---|---|
| 1 | docs/52 B 路 spec selective refresh（如命中）| ✅ 1+ 处 superseded per 599 |
| 2 | docs/52 B 路保持主路径 grep | ✅ 执行端自取预 vetted 公开源走完整 e2e 流水线 命中 ≥ 1 |
| 3 | docs/47 + docs/48 selective refresh（如命中）| ✅ 1+ 处 superseded per 599 |
| 4 | docs/49 §5.2 + docs/50 §5.1 状态行 append | ✅ 598 audit 落 标注 命中 ≥ 2 occurrences |
| 5 | manifest INVARIANT | ✅ 944+K == 944+K == 944+K |
| 6 | 13 受保护文件零漂移 | ✅ 全部 SHA + bytes 不变 |
| 7 | 30+ 红线 100% 兑现 | ✅ 全部 PASS |
| 8 | 双推 + cc_head backfill | ✅ 100% 收敛 |
| 9 | docs 房规 NOT-IN-MANIFEST | ✅ docs/X 命中行 supersede append 不增计数 |
| 10 | 既有 OPEN 行零删减 | ✅ 全部保留 |

---

## §3. 与前置刀的衔接

| 刀 | 闭合项 | 状态 |
|---|---|---|
| 583 PASS | §5.2.2 validate_ocr_input() + §5.2.3 doc_kind migration | CLOSED |
| 584 BLOCKED-DEFERRED → CLOSED per 597 | §5.2.4 paddle-ocr deps + Dockerfile | CLOSED |
| 585 PASS | §5.2.5 端到端 pytest + §584 audit ⚠1 docs sync patch | CLOSED |
| 587 PASS | §5.2.6 真实 PDF e2e + O3 整体 CLOSED 候选 | CLOSED 候选 |
| 589/591/593/595/596 PASS | docs/45/49/50/53 三层 supersede 平行模式 + BLOCKER 5→0 闭环 | CLOSED |
| 597 PASS（per 598 audit）| paddle-ocr 引擎依赖实施 + 584 docs sync 收口 | CLOSED |
| **599（本刀）**| docs/52 B 路 spec 落定 + docs/47 + docs/48 stale refresh + docs/49/50 状态行 append | docs-only refresh |

---

## §4. 关联文件清单

- 597 tasking：`reviews/stage0-gate0-rework-2026-08-23/597-stage0-architect-s596-584-reack-impl-tasking-20260829.md`（NOT-IN-MANIFEST per docs 房规）
- 597 receipt：`reviews/stage0-gate0-rework-2026-08-23/597-stage0-cc-584-reack-impl-tasking-20260829-receipt.md`（25960B, sha=`08ef2da1`）
- 598 audit：`reviews/stage0-gate0-rework-2026-08-23/598-stage0-architect-s597-584-impl-tasking-20260829-audit-PASS-20260829.md`
- 599 tasking 本文件：`reviews/stage0-gate0-rework-2026-08-23/599-stage0-architect-s598-docs-52-b-route-spec-refresh-tasking-20260829.md`
- docs/52：`docs/52-stage2-official-open-source-auto-ingest-plan-20260826.md`
- docs/47：`docs/47-stage2-s210-o1-real-pdf-pilot-user-action-stale-20260826.md`
- docs/48：`docs/48-stage2-s210-o1-real-pdf-pilot-user-action-stale-20260826.md`
- queue：`reviews/stage0-gate0-rework-2026-08-23/00-EXEC-QUEUE.md`（rev 16）

---

— End of `599-stage0-architect-s598-docs-52-b-route-spec-refresh-tasking-20260829.md` —
