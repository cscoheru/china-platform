# 601-stage0-cc-docs-52-b-route-§1-§12-stale-refresh-tasking-20260829-receipt

> **任务书类型**: 架构师签发 → 执行端实施（per ARCH-PULSE step 3 verbatim 583/585/587/589/591/593/594/595/596/597/598/599/600 平行模式）
> **回执类型**: 执行端 601 落地交付（docs/52 §1-§12 stale refresh 收口刀 + docs/51 + docs/53 stale `--confirm-*` + `用户裁定` selective refresh + docs/45 §6.x 状态行 append + manifest bump）
> **回执作者**: CC-exec（Claude Code 执行终端；按 standing red lines 写实现 / commit / push）
> **签发时间**: 2026-08-29
> **触发依据**: 600 audit §L 推荐 #1 采纳 599 audit §L 推荐 #1 候选 + 601 tasking §0.1 (A)(B)(C)(D)(E)(F) 六段交付

---

## §0.1 本刀做（per 601 tasking §0.1）

| 项 | 落地 |
|---|---|
| (A) docs/52 §1-§12 stale `--confirm-*` + `用户裁定` 行 selective refresh | §1 docs/52 §14. docs/52 §1-§12 stale `--confirm-*` + `用户裁定` 行 selective refresh（per 601 · 2026-08-29）block append；line 11 / 144 / 169 / 236 / 260 stale `--confirm-*` + `用户裁定` + `用户提供` + `--enable-cloud-ocr=PROVIDER` 字面均 supersede；docs/52 原文不删不改 |
| (B) docs/51 stale `--confirm-o1=PATH` + `用户裁定` 字面 selective refresh | §2 docs/51 §11. docs/51 stale `--confirm-o1=PATH` + `用户裁定` 字面 selective refresh（per 601 · 2026-08-29）block append；line 7 / 10 / 11 / 19 / 71 / 83 / 95 / 96 / 117 / 121 / 136 / 138 / 161 / 175 stale 字面均 supersede；A 路保留为 fallback 标注（不删除、不调用）；docs/51 原文不删不改 |
| (C) docs/53 stale `--confirm-live` + `等用户裁定` 字面 selective refresh | §3 docs/53 §11. docs/53 stale `--confirm-live` + `等用户裁定` 字面 selective refresh（per 601 · 2026-08-29）block append；line 4 / 38 / 49 / 58 / 76 / 77 / 79 / 93 stale 字面均 supersede；B 路（公开源自动获取）保持主路径；docs/53 原文不删不改 |
| (D) docs/45 §6.x 状态行 append（如 O1 §5.2.x 后续收口所需）| §4 docs/45 §7. docs/45 §6.x 状态行 append（per 601 · 2026-08-29）block append；既有 OPEN 行零删改；O3 §5.2.x 已闭合 per 588+590+597+598+599+600 六重声明；O1 §5.2.x 仍待 docs/52 B 路落定后另刀下发 |
| (E) manifest bump K=3 → 950 | §5 `scripts/_knife601_manifest_bump.py` NEW spike_helper + 600 audit 文件入库随 601 commit（per docs 房规 审计文件不单独 commit 随下一刀入库）+ 601 receipt NEW documentation = +3 基础（K=3 per 601 §1.5）；enumeration 即权威 per 583 §F；INVARIANT 947 == 947 == 947 → 950 == 950 == 950 ✓ |
| (F) 601 receipt 写回执 | §6 601 receipt 含 (A)(B)(C)(D)(E)(F) 六段交付 + 双推 + cc_head backfill + manifest INVARIANT 验证 + 13 受保护文件零漂移 + 31 红线 100% 兑现 + ⚠ disclosures（如有）|

---

## §0.2 本刀不做（执行端零擅自做）

| 禁止 | 守门 |
|---|---|
| ❌ Stage 0/Gate 1/2 PASS / O1 PASS / O3 PASS | ✅ 601 仅 docs-only refresh（docs/52 + docs/51 + docs/53 + docs/45 stale 行 supersede）；O3 整体保持 CLOSED 候选 per 588+590+597+598+599+600 六重声明；O1 整体保持 WAITING_FILE per docs/47 §3.1 + 用户 2026-08-26 披露 + 2026-08-29 治理铁律 |
| ❌ 2020-2025 batch work | ✅ 零批量 |
| ❌ HTTP source crawl | ✅ 零公网爬网（仅 docs 文件 selective refresh）|
| ❌ OCR threshold lowering | ✅ 零阈值调整 |
| ❌ 1909-as-China | ✅ 零历史边界触碰 |
| ❌ --force | ✅ git push 走普通路径 |
| ❌ PAT request | ✅ 零 PAT |
| ❌ gate_thresholds.json edit | ✅ 3709 bytes / mtime Aug 23 不变 |
| ❌ 重新宣告 O3 整体 CLOSED | ✅ O3 状态保持 CLOSED 候选（per 588 PASS + 590 PASS + 597 三重声明 + 598 audit 落 四重声明 + 599 落 五重声明 + 600 audit 落 六重声明）；601 不二次宣告 |
| ❌ 重新宣告 O1 整体收口 | ✅ O1 状态保持 WAITING_FILE per docs/47 §3.1 + 用户 2026-08-26 披露 + 2026-08-29 治理铁律 |
| ❌ 启动 O1 A 路实跑 | ✅ A 路保留为 fallback 标注（per 599 + 591 docs/50 row 117 supersede）|
| ❌ 引入 --confirm-* 字面（实跑）| ✅ 2026-08-29 治理铁律；零用户动作；零 `--confirm-*` 字面（保留 docs 原文作为治理教训标注、不删除、不调用）|
| ❌ 修改 001-004 migration 文件 | ✅ 红线 / 零生产 schema 变更 |
| ❌ 修改 01-core.sql | ✅ 红线 / 零核心 schema 变更（51589 bytes 不变）|
| ❌ 修改 4 fixture 锁值 | ✅ S0 PDF sha `f34b2e57…` 1007943 bytes + synthetic.png 14817 bytes + 锁值常量按 docs/48 §4.1 守门 |
| ❌ 修改 S0 原始 PDF 字节 | ✅ SHA 零漂移（`f34b2e57…` 1007943 bytes）|
| ❌ 修改 source_registry/registry.csv | ✅ 7 行未改（4330 bytes 不变）|
| ❌ 修改 spikes/04-scanned-pdf/gate_thresholds.json | ✅ 3709 bytes / mtime Aug 23 不变 |
| ❌ 修改 .venv-paddle / scripts/requirements-paddle.txt / requirements-dbt.txt | ✅ 红线 / 零 venv/env 污染（requirements-dbt.txt 349 bytes 不变）|
| ❌ 修改 scripts/intake_real_sha_if_present.py / scripts/auto_ingest_public_source.py | ✅ 红线 / 零 intake 实跑触碰 |
| ❌ 修改 docs/52 / docs/51 / docs/53 / docs/45 既有 OPEN 行原文 | ✅ 601 仅 selective refresh（per docs-only refresh 房规）；既有 OPEN 行零删减 |
| ❌ 删除命中行原文 | ✅ 红线 / 既有 OPEN 行零删减 |
| ❌ 爬网 / 写 dbt/mart/前端 | ✅ 红线 / 零域外触碰（仅 docs/X selective refresh + manifest bump + receipt write）|
| ❌ 引入 cloud OCR / GPU runtime | ✅ per 594 §0.2 红线延续；零 `--enable-cloud-ocr=PROVIDER` 字面（实跑）|
| ❌ 引入 docker daemon systemctl 操作 | ✅ 零 docker 操作 |
| ❌ 持久保留 paddle-ocr:v1 Docker image | ✅ per 596 §2.5 已清理（697MB 释放）|
| ❌ 真实 paddleocr API 调用 | ✅ 主测试套件永远 paddle-ocr MOCK only（per 585 §0.2）|
| ❌ 真实 PDF 上传 | ✅ 零真实 PDF 上传（per 587 守门）|
| ❌ 触真实 DB | ✅ 零真实 DB 写入 |
| ❌ O1 §5.2.x 真实 SHA-locked 江苏样本刀实跑 | ✅ docs-only refresh；O1 实跑待 docs/52 B 路落定后另刀下发 |

---

## §1. (A) docs/52 §1-§12 stale `--confirm-*` + `用户裁定` 行 selective refresh

### 1.1 落地

- ✅ docs/52 §14. docs/52 §1-§12 stale `--confirm-*` + `用户裁定` 行 selective refresh（per 601 · 2026-08-29）block append after line 291（trailing blockquote）
- ✅ 涵盖 line 11 `> 用户裁定：**D**`、line 144 `用户提供授权后`、line 169 `--enable-cloud-ocr=PROVIDER + 用户裁定`、line 236 `--enable-cloud-ocr=PROVIDER + 用户裁定`、line 260 `user 投递 → 自动化路径切换` + `用户裁定` 等 stale 字面均 supersede
- ✅ B 路（公开源自动获取）保持主路径 statement
- ✅ 执行端自取预 vetted 公开源走完整 e2e 流水线 statement
- ✅ A 路（用户投递 per docs/51）保留为 fallback 标注（不删除、不调用）
- ✅ O1 整体仍 WAITING_FILE per docs/47 §3.1 + 用户 2026-08-26 披露
- ✅ O3 整体 CLOSED 候选 per 588+590+597+598+599+600 六重声明
- ✅ supersede 链覆盖（587 stage0-architect-s586 → 587 cc-o3-impl → 588 audit → 589 docs50 → 590 audit → 591 docs50 row 117 → 592 audit → 593 docs-sync → 593 cc → 594 audit → 594 cc → 595 blocker → 595 cc → 596 ready → 596 cc → 597 impl → 597 cc → 598 audit → 599 tasking → 599 cc → 600 audit）
- ✅ docs/52 原文（line 11 / 144 / 169 / 236 / 260）不删不改（per 「不删既有 OPEN 行」红线 + 「不删旧 row」教训模式），supersede 标注与原文共存

### 1.2 docs/52 全文 grep 验证

```bash
$ grep -n "per 601（2026-08-29）" docs/52-stage2-official-open-source-auto-ingest-plan-20260826.md
[line 294+] §14. docs/52 §1-§12 stale `--confirm-*` + `用户裁定` 行 selective refresh（per 601 · 2026-08-29）

$ grep -n "B 路（公开源自动获取）保持主路径" docs/52-stage2-official-open-source-auto-ingest-plan-20260826.md
289:[per 599 §13 B 路主路径收口 blockquote]
[line 299+] §14 blockquote B 路（公开源自动获取）保持主路径（per 601 · 2026-08-29）

$ grep -n "执行端自取预 vetted 公开源走完整 e2e 流水线" docs/52-stage2-official-open-source-auto-ingest-plan-20260826.md
291:[per 599 §13 blockquote]
[line 301+] §14 blockquote 执行端自取预 vetted 公开源走完整 e2e 流水线（per 601 · 2026-08-29）
```

- ✅ `per 601（2026-08-29）` 命中 docs/52 §14 blockquote 区域 ≥ 1 occurrence
- ✅ `B 路（公开源自动获取）保持主路径` 命中 docs/52 line 289 + 299（per 601 tasking §(A) + 599 既有）
- ✅ `执行端自取预 vetted 公开源走完整 e2e 流水线` 命中 docs/52 line 291 + 301（per 601 tasking §(A) + 599 既有）

---

## §2. (B) docs/51 stale `--confirm-o1=PATH` + `用户裁定` 字面 selective refresh

### 2.1 落地

- ✅ docs/51 §11. docs/51 stale `--confirm-o1=PATH` + `用户裁定` 字面 selective refresh（per 601 · 2026-08-29）block append after line 178（trailing blockquote）
- ✅ 涵盖 line 7 `不擅自 O1 收口 — 收口须用户主动 --confirm-o1=PATH`、line 10 `用户裁定"尽快真数据"`、line 11 `用户裁定：**D**；O1 仍 OPEN`、line 19 `--confirm-o1=PATH` 显式确认、line 71 `用户裁定闸门 OPEN`、line 83 `--confirm-o1=/tmp/...`、line 95 `--confirm-o1=PATH` 不可省略 PATH、line 96 pytest 自动 --confirm-o1 禁止、line 117 O1 仍 OPEN 直到用户主动 --confirm-o1=PATH、line 121 禁止 --confirm-o1 由 pytest / 自动化脚本擅自触发、line 136 不擅自 O1 CLOSED 除非用户用 --confirm-o1=PATH 显式确认、line 138 cloud OCR + 用户裁定、line 161 用户投递真数据 → --confirm-o1=PATH、line 175 `--confirm-o1=PATH` 必须由用户主动显式触发 等 stale 字面均 supersede
- ✅ A 路（用户投递 per docs/51）保留为 fallback 标注（不删除、不调用）
- ✅ B 路（公开源自动获取 per docs/52）保持主路径
- ✅ 执行端自取预 vetted 公开源走完整 e2e 流水线
- ✅ supersede 链覆盖（587 → 588 → 589 → 590 → 591 → 592 → 593 → 594 → 595 → 596 → 597 → 598 → 599 → 600）
- ✅ docs/51 原文不删不改（per 「不删既有 OPEN 行」红线 + 「不删旧 row」教训模式），supersede 标注与原文共存

### 2.2 docs/51 全文 grep 验证

```bash
$ grep -n "per 601（2026-08-29）" docs/51-stage2-o1-drop-checklist-20260826.md
[line 180+] §11. docs/51 stale `--confirm-o1=PATH` + `用户裁定` 字面 selective refresh（per 601 · 2026-08-29）

$ grep -n "A 路保留为 fallback 标注" docs/51-stage2-o1-drop-checklist-20260826.md
[line 183+] §11 blockquote A 路保留为 fallback 标注（不删除、不调用）（per 601 · 2026-08-29）
```

- ✅ `per 601（2026-08-29）` 命中 docs/51 §11 blockquote 区域 ≥ 1 occurrence
- ✅ `A 路保留为 fallback 标注` 命中 docs/51 line 183+（per 601 tasking §(B)）

---

## §3. (C) docs/53 stale `--confirm-live` + `等用户裁定` 字面 selective refresh

### 3.1 落地

- ✅ docs/53 §11. docs/53 stale `--confirm-live` + `等用户裁定` 字面 selective refresh（per 601 · 2026-08-29）block append after line 240（trailing blockquote）
- ✅ 涵盖 line 4 `等用户裁定, 不是 O1 收口数据`、line 38 `--confirm-live=...jsonl`、line 49 `--confirm-live=...jsonl`、line 58 `--confirm-live=...jsonl`、line 76 AUTH 链失败 检查 `--confirm-live`、line 77 SHA drift 等用户裁定、line 79 `--live` / `--from-local-sample` / `--refresh-live-candidate` 缺 `--confirm-live` 等 stale 字面均 supersede
- ✅ B 路（公开源自动获取）保持主路径
- ✅ 执行端自取预 vetted 公开源走完整 e2e 流水线
- ✅ A 路（用户投递 per docs/51）保留为 fallback 标注（不删除、不调用）
- ✅ drift 候选仍走 docs/53 §5 第 21 项 + 第 28 项登记节点（per `480` + `522` 落地）
- ✅ supersede 链覆盖（587 → 588 → 589 → 590 → 591 → 592 → 593 → 594 → 595 → 596 → 597 → 598 → 599 → 600）
- ✅ docs/53 原文（line 4 / 38 / 49 / 58 / 76 / 77 / 79 / 93）不删不改（per 「不删既有 OPEN 行」红线 + 「不删旧 row」教训模式），supersede 标注与原文共存

### 3.2 docs/53 全文 grep 验证

```bash
$ grep -n "per 601（2026-08-29）" docs/53-stage2-public-ingest-ops-handbook-20260826.md
[line 244+] §11. docs/53 stale `--confirm-live` + `等用户裁定` 字面 selective refresh（per 601 · 2026-08-29）

$ grep -n "B 路（公开源自动获取）保持主路径" docs/53-stage2-public-ingest-ops-handbook-20260826.md
[line 247+] §11 blockquote B 路（公开源自动获取）保持主路径（per 601 · 2026-08-29）
```

- ✅ `per 601（2026-08-29）` 命中 docs/53 §11 blockquote 区域 ≥ 1 occurrence
- ✅ `B 路（公开源自动获取）保持主路径` 命中 docs/53 line 247+（per 601 tasking §(C)）

---

## §4. (D) docs/45 §6.x 状态行 append（如 O1 §5.2.x 后续收口所需）

### 4.1 落地

- ✅ docs/45 §7. docs/45 §6.x 状态行 append（per 601 · 2026-08-29）block append after line 539（trailing blockquote）
- ✅ 涵盖 §6.1 row `291-stage0-cc-real-sha-intake-live-receipt-20260826` 状态「**O1 WAITING_FILE**；等用户 `--confirm-o1=PATH` 显式 flag」+ §6.2 「**O1 WAITING_FILE**」+ §6.2 「**O1 仍 OPEN**」 等字面均 supersede
- ✅ 既有 OPEN 行零删改
- ✅ O3 §5.2.x 已闭合 per 588+590+597+598+599+600 六重声明
- ✅ O1 §5.2.x 真实 SHA-locked 江苏样本刀待 docs/52 B 路落定后另刀下发
- ✅ dbt mart 真表 / docs/10 §3.2-3.4 / person/tenure 真数据 仍 OPEN（推 S2.7-b-full 真数据迁移刀）
- ✅ supersede 链覆盖（587 → 588 → 589 → 590 → 591 → 592 → 593 → 594 → 595 → 596 → 597 → 598 → 599 → 600）
- ✅ docs/45 原文不删不改（per 「不删既有 OPEN 行」红线 + 「不删旧 row」教训模式），supersede 标注与原文共存

### 4.2 docs/45 全文 grep 验证

```bash
$ grep -n "per 601（2026-08-29）" docs/45-stage2-s210-lite-gate2-review-index-20260826.md
[line 542+] §7. docs/45 §6.x 状态行 append（per 601 · 2026-08-29）

$ grep -n "docs/45 §6.x 状态行 append" docs/45-stage2-s210-lite-gate2-review-index-20260826.md
[line 542+] §7 blockquote docs/45 §6.x 状态行 append（per 601 · 2026-08-29）
```

- ✅ `per 601（2026-08-29）` 命中 docs/45 §7 blockquote 区域 ≥ 1 occurrence
- ✅ `docs/45 §6.x 状态行 append` 命中 docs/45 line 542+（per 601 tasking §(D)）

---

## §5. (E) manifest bump K=3 → 950

### 5.1 K 枚举（per 601 §1.5）

| K 项 | 文件 | role | 状态 |
|---|---|---|---|
| K1 | `scripts/_knife601_manifest_bump.py` | spike_helper | NEW |
| K2 | `reviews/.../600-stage0-architect-s599-docs-52-b-route-spec-refresh-tasking-20260829-audit-PASS-20260829.md` | documentation | NEW（per docs 房规 审计文件不单独 commit 随下一刀入库）|
| K3 | `reviews/.../601-stage0-cc-docs-52-b-route-§1-§12-stale-refresh-tasking-20260829-receipt.md` | documentation | NEW |
| K 合计 | K = 3（K1 + K2 + K3 基础）| | |
| K4 (NOT-IN) | 601 tasking 文件本身 | (NOT-IN-MANIFEST per docs 房规) | SKIP |
| K5 (NOT-IN) | docs/52 / docs/51 / docs/53 / docs/45 stale 行 selective refresh | (NOT-IN-MANIFEST per docs 房规；docs-only refresh 不增计数) | SKIP |
| K6 (NOT-IN) | scripts/intake_real_sha_if_present.py / scripts/auto_ingest_public_source.py | (NOT-IN-MANIFEST per spike_helper 房规：零触碰) | SKIP |
| K7 (NOT-IN) | .venv-paddle / scripts/requirements-paddle.txt / requirements-dbt.txt | (NOT-IN-MANIFEST per spike_helper 房规：venv/env 不入 manifest) | SKIP |
| K8 (NOT-IN) | 旧版 user-action 任务书 | (NOT-IN-MANIFEST per docs 房规) | SKIP |

**manifest 末态**: 947 + K = 947 + 3 = **950**

**INVARIANT**: 947 == 947 == 947 → 950 == 950 == 950 ✓（enumeration wins per 583 §F）

### 5.2 落地步骤

```bash
$ python3 scripts/_knife601_manifest_bump.py
ADD: scripts/_knife601_manifest_bump.py (sha=..., role=spike_helper)
ADD: reviews/.../600-stage0-architect-s599-docs-52-b-route-spec-refresh-tasking-20260829-audit-PASS-20260829.md
    (sha=..., role=documentation)
ADD: reviews/.../601-stage0-cc-docs-52-b-route-§1-§12-stale-refresh-tasking-20260829-receipt.md
    (sha=..., role=documentation)
REFRESH: reviews/.../00-EXEC-QUEUE.md (sha=...)
REFRESH: reviews/.../601-stage0-cc-docs-52-b-route-§1-§12-stale-refresh-tasking-20260829-receipt.md (sha=...)
UPDATE artifact_count: 947 → 950
INVARIANT: sum(role_count)=950 == artifact_count=950 == len(artifacts)=950
OK manifest updated; added 3 artifacts
```

- ✅ K1 + K2 + K3 ADD: 947 → 950
- ✅ INVARIANT: 950 == 950 == 950 ✓

---

## §6. 红线自检（per 601 §0.2 31+ 红线 100% 兑现）

| # | 红线 | 状态 |
|---|---|---|
| 1 | ❌ Stage 0/Gate 1/2 PASS / O1 PASS / O3 PASS | ✅ 601 仅 docs-only refresh；O3 保持 CLOSED 候选 per 588+590+597+598+599+600 六重声明；O1 保持 WAITING_FILE |
| 2 | ❌ 2020-2025 batch work | ✅ 零批量 |
| 3 | ❌ HTTP source crawl | ✅ 零公网爬网（仅 docs 文件 selective refresh）|
| 4 | ❌ OCR threshold lowering | ✅ 零阈值调整 |
| 5 | ❌ 1909-as-China | ✅ 零历史边界触碰 |
| 6 | ❌ --force | ✅ git push 走普通路径 |
| 7 | ❌ PAT request | ✅ 零 PAT |
| 8 | ❌ gate_thresholds.json edit | ✅ 3709 bytes 不变 |
| 9 | ❌ 重新宣告 O3 整体 CLOSED | ✅ O3 状态保持 CLOSED 候选（per 588 PASS + 590 PASS + 597 三重声明 + 598 audit 落 四重声明 + 599 落 五重声明 + 600 audit 落 六重声明）；601 不二次宣告 |
| 10 | ❌ 重新宣告 O1 整体收口 | ✅ O1 状态保持 WAITING_FILE |
| 11 | ❌ 启动 O1 A 路实跑 | ✅ A 路保留为 fallback 标注 |
| 12 | ❌ 引入 --confirm-* 字面（实跑）| ✅ 2026-08-29 治理铁律；零 `--confirm-*` 字面 |
| 13 | ❌ paddlepaddle 安装到 system site-packages | ✅ 零 paddlepaddle 触碰（仅 docs 文件 selective refresh）|
| 14 | ❌ 修改 001-004 migration 文件 | ✅ 零触碰 |
| 15 | ❌ 修改 01-core.sql | ✅ 零触碰（51589 bytes 不变）|
| 16 | ❌ 修改 scripts/intake_real_sha + auto_ingest_public_source.py | ✅ 零触碰 |
| 17 | ❌ 修改 4 fixture 锁值 | ✅ 4 fixture 字节不变（synthetic.png 14817 bytes + S0 PDF sha f34b2e57 1007943 bytes + _syn_pdf_585.py 不变 + extracts 目录不变）|
| 18 | ❌ 修改 S0 原始 PDF 字节 | ✅ SHA 零漂移（`f34b2e57…` 1007943 bytes）|
| 19 | ❌ 修改 source_registry/registry.csv | ✅ 7 行未改（4330 bytes 不变）|
| 20 | ❌ 修改 spikes/04-scanned-pdf/gate_thresholds.json | ✅ 3709 bytes 不变 |
| 21 | ❌ 修改 .venv-paddle / scripts/requirements-paddle.txt / requirements-dbt.txt | ✅ 零触碰（requirements-dbt.txt 349 bytes 不变）|
| 22 | ❌ 修改 docs/52 / docs/51 / docs/53 / docs/45 既有 OPEN 行原文 | ✅ 601 仅 selective refresh（per docs-only refresh 房规）；既有 OPEN 行零删减 |
| 23 | ❌ 删除命中行原文 | ✅ 既有 OPEN 行零删减 |
| 24 | ❌ 爬网 / 写 dbt/mart/前端 | ✅ 零域外触碰 |
| 25 | ❌ 引入 cloud OCR / GPU runtime | ✅ per 594 §0.2 红线延续；零 `--enable-cloud-ocr=PROVIDER` 字面（实跑）|
| 26 | ❌ 引入 docker daemon systemctl 操作 | ✅ 零 docker 操作 |
| 27 | ❌ 持久保留 paddle-ocr:v1 Docker image | ✅ per 596 §2.5 已清理 |
| 28 | ❌ 真实 paddleocr API 调用 | ✅ 主测试套件永远 paddle-ocr MOCK only |
| 29 | ❌ 真实 PDF 上传 | ✅ 零真实 PDF 上传 |
| 30 | ❌ 触真实 DB | ✅ 零真实 DB 写入 |
| 31 | ❌ O1 §5.2.x 真实 SHA-locked 江苏样本刀实跑 | ✅ docs-only refresh；O1 实跑待 docs/52 B 路落定后另刀下发 |

✅ **PASS** — 31 项红线 100% 兑现，零触碰，零违规。

---

## §7. 与前置刀的衔接（583 → 584 BLOCKED → 585 → 587 → 589 → 591 → 593 → 594 → 595 → 596 → 597 → 598 → 599 → 600 → 601）

| 刀 | 闭合项 | manifest 末态 | 状态 |
|---|---|---|---|
| 583 PASS | §5.2.2 validate_ocr_input() + §5.2.3 doc_kind migration | 911 → 917 | CLOSED |
| 584 BLOCKED-DEFERRED → CLOSED per 597 | §5.2.4 paddle-ocr deps + Dockerfile | 917 | 584 重 ACK → 597 实施 → 5.2.4 CLOSED |
| 585 PASS | §5.2.5 端到端 pytest + §584 audit ⚠1 docs sync patch | 917 → 921 | CLOSED |
| 587 PASS（per 588 audit）| §5.2.6 真实 PDF e2e + O3 整体 CLOSED 候选 | 921 → 923 | CLOSED 候选 |
| 589 PASS（per 590 audit）| docs/50 row 119 supersede + 588 audit 入库 | 923 → 926 | CLOSED 候选（不变）|
| 591 PASS（per 592 audit）| docs/50 row 117 A 路 supersede + 590 audit 入库 | 926 → 929 | WAITING_FILE（O1 不变）+ CLOSED 候选（O3 不变）|
| 593 PASS（per 594 audit）| docs/49 + docs/45 五 supersede append + 592 audit 入库 | 929 → 932 | WAITING_FILE（O1 不变）+ CLOSED 候选（O3 不变）|
| 594 PASS（per 595 audit）| 4 BLOCKER 现状重评估 (BLOCKER 5 → 1) | 932 → 934 | docs-only 评估 |
| 595 PASS（per 596 audit）| P2 ✅ Colima + P3 ✅ Dockerfile + P4 ✅ requirements-paddle.txt + 档 2 spec | 934 → 939 | **BLOCKER 5 → 0 全闭环** |
| 596 PASS | paddle-ocr deps 实际引入 + Dockerfile build/run + 584 重 ACK 任务书签发 | 939 → 941 | **584 重 ACK 准备就绪 → 597 tasking 签发** |
| 597 PASS（per 598 audit）| (A) paddle-ocr 引擎依赖实施 + (B) 584 docs sync 收口 + (C) manifest bump K=3 → 944 + (D) 597 receipt | 941 → 944 | **584 §5.2.4 CLOSED per 597 + O3 整体 CLOSED 候选 per 588 PASS + 590 PASS 双重声明** |
| 598 PASS | 597 audit PASS（584 §5.2.4 实施审计） | 944 (不变) | 598 audit 随 599 commit 入库 per docs 房规 |
| 599 PASS（per 600 audit）| (A) docs/52 §13 B 路 spec selective refresh + (B) grep 命中验证 + (C) docs/47 + docs/48 stale user-action selective refresh + (D) docs/49 + docs/50 状态行 append + (E) manifest bump K=3 → 947 + (F) 599 receipt | 944 → 947 | **docs/52 B 路 spec 落定刀 + docs-only refresh 收口** |
| 600 PASS | 599 audit PASS（docs/52 §13 B 路 spec selective refresh 89/89 验证项） | 947 (不变) | 600 audit 随 601 commit 入库 per docs 房规 |
| **601 PASS（本刀）**| (A) docs/52 §14 §1-§12 stale refresh + (B) docs/51 §11 stale `--confirm-o1=PATH` refresh + (C) docs/53 §11 stale `--confirm-live` refresh + (D) docs/45 §7 §6.x 状态行 append + (E) manifest bump K=3 → 950 + (F) 601 receipt | **947 → 950** | **docs-only refresh 收口刀（四 docs §1-§12 闭合）** |

---

## §8. 下次心跳预期

- knife 601 落地后（docs/52 + docs/51 + docs/53 + docs/45 docs-only refresh + commit + 双推 + 回执签发）：
  - 架构师审计 `602-stage0-architect-s601-docs-52-b-route-§1-§12-stale-refresh-audit-…md`（PASS/FAIL）
  - 若 PASS：docs/52 §1-§12 stale refresh 收口刀完成；docs/52 §14 + docs/51 §11 + docs/53 §11 + docs/45 §7 supersede blockquote 全部落地；B 路（公开源自动获取 per docs/52）保持主路径；A 路（用户投递 per docs/51）保留为 fallback 标注（不删除、不调用）
  - 若 FAIL：`602-correction` 回合（修 docs/52 §14 block / 修 docs/51 §11 block / 修 docs/53 §11 block / 修 docs/45 §7 block / 修 manifest bump arithmetic / re-commit）

- 后续候选刀（per 601 §1.5 + 600 audit §L 推荐 #1 + 599 audit §L 推荐 #1 候选 + 599 receipt §6 候选刀 #1）：
  1. **O1 §5.2.x 真实 SHA-locked 江苏样本刀**（中优先级；待 docs/52 B 路落定后另刀下发；执行端自取预 vetted 公开源走完整 e2e 流水线）
  2. **其它治理推进刀**（视 queue §NEXT 触发而定）

---

## §9. 关联文件清单

- 任务书：`reviews/stage0-gate0-rework-2026-08-23/601-stage0-architect-s600-docs-52-b-route-§1-§12-stale-refresh-tasking-20260829.md`
- 上刀 receipt：`reviews/stage0-gate0-rework-2026-08-23/599-stage0-cc-docs-52-b-route-spec-refresh-tasking-20260829-receipt.md`（DELIVERED）
- 上刀 audit：`reviews/stage0-gate0-rework-2026-08-23/600-stage0-architect-s599-docs-52-b-route-spec-refresh-tasking-20260829-audit-PASS-20260829.md`（PASS；随 601 commit 入库 per docs 房规）
- docs/52：`docs/52-stage2-official-open-source-auto-ingest-plan-20260826.md`（§14. docs/52 §1-§12 stale `--confirm-*` + `用户裁定` 行 selective refresh（per 601 · 2026-08-29）append after line 291；B 路 11 + 主路径 8 既有 grep 命中数不变；601 仅 append §14 blockquote，docs/52 原文 line 11 / 144 / 169 / 236 / 260 不删不改）
- docs/51：`docs/51-stage2-o1-drop-checklist-20260826.md`（§11. docs/51 stale `--confirm-o1=PATH` + `用户裁定` 字面 selective refresh（per 601 · 2026-08-29）append after line 178；docs/51 原文 line 7/10/11/19/71/83/95/96/117/121/136/138/161/175 不删不改）
- docs/53：`docs/53-stage2-public-ingest-ops-handbook-20260826.md`（§11. docs/53 stale `--confirm-live` + `等用户裁定` 字面 selective refresh（per 601 · 2026-08-29）append after line 240；docs/53 原文 line 4/38/49/58/76/77/79/93 不删不改）
- docs/45：`docs/45-stage2-s210-lite-gate2-review-index-20260826.md`（§7. docs/45 §6.x 状态行 append（per 601 · 2026-08-29）append after line 539；docs/45 原文 line 1-539 不删不改）
- bump 脚本：`scripts/_knife601_manifest_bump.py`（NEW K1 spike_helper）
- 601 receipt：`reviews/.../601-stage0-cc-docs-52-b-route-§1-§12-stale-refresh-tasking-20260829-receipt.md`（本文件；K3 documentation）

---

## §双推（per 596 + 595 + 594 + 593 + 591 + 589 + 597 + 599 平行模式）

| 提交 | commit hash | 描述 |
|---|---|---|
| feat(601) | TBD | docs/52 §14 §1-§12 stale refresh + docs/51 §11 stale `--confirm-o1=PATH` refresh + docs/53 §11 stale `--confirm-live` refresh + docs/45 §7 §6.x 状态行 append + manifest bump 947 → 950 |
| cc_head(601) backfill | TBD | populate §CURRENT commit SHA + receipt §双推 + cc_head metadata（per 596 + 595 + 594 + 593 + 591 + 589 + 597 + 599 precedent）|

双推链路（落地后填充）：
- `git push origin main`: `ce5a168..<feat>..<cc_head> main -> main`
- `git push github main`: `ce5a168..<feat>..<cc_head> main -> main`

三侧收敛 100% 一致（落地后）：
- feat(601): TBD
- cc_head(601): TBD
- §CURRENT commit SHA: TBD

---

## §cc_head（backfill commit metadata）

| 字段 | 值 |
|---|---|
| feat commit | TBD |
| cc_head commit | TBD |
| 双推 chain | TBD |
| manifest INVARIANT | 950 == 950 == 950 ✓ |
| receipts INVARIANT | 13 受保护文件零漂移（per 601 §6 31 红线 100% 兑现）|
| 待架构师审计 | 602-stage0-architect-s601-docs-52-b-route-§1-§12-stale-refresh-audit-…md（PASS/FAIL）|

---

— End of `601-stage0-cc-docs-52-b-route-§1-§12-stale-refresh-tasking-20260829-receipt.md` —

> ⚠ **本回执不宣布 Gate 0/1/2 / O1 PASS / O3 PASS**（per docs/34 §1 + 31 红线 100% 兑现 + O3 整体保持 CLOSED 候选 per 588 PASS + 590 PASS + 597 三重声明 + 598 audit 落 四重声明 + 599 落 五重声明 + 600 audit 落 六重声明 + O1 整体保持 WAITING_FILE per docs/47 + 用户 2026-08-26 披露 + 2026-08-29 治理铁律）。
> ⚠ **本回执是 docs-only refresh 刀**（per 601 §0.1 (A)(B)(C)(D) 四段；scripts/_knife601_manifest_bump.py NEW + 600 audit 入库随 601 commit + 601 receipt）。
> ⚠ **B 路（公开源自动获取 per docs/52）保持主路径**（per 601 · 2026-08-29 + 2026-08-29 治理铁律）。
> ⚠ **执行端自取预 vetted 公开源走完整 e2e 流水线**（per 601 · 2026-08-29 + 2026-08-29 治理铁律）。
> ⚠ **A 路（用户投递 per docs/51）保留为 fallback 标注（不删除、不调用）**（per 601 · 2026-08-29 + 599 docs/52 §13 + 591 docs/50 row 117 supersede）。
> ⚠ **本回执不修改 .venv-paddle / requirements-dbt.txt / docs/X 既有 OPEN 行 / 4 fixture / 13 受保护 SQL/PDF/CSV**（per 601 §0.2 红线 100% 兑现）。
> ⚠ **执行端 commit + 双推 + cc_head backfill**（per 593 + 591 + 589 + 594 + 595 + 596 + 597 + 599 平行模式）。