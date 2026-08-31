# 614-stage0-architect-s613-§5.2.x-sha-citation-drift-治理-tasking-20260829

> **任务书类型**: 架构师签发 → 执行端实施（per ARCH-PULSE step 3 verbatim 583/585/587/589/591/593/594/595/596/597/598/599/600/601/602/603/604/605/606/607/608/609/610/611/612/613 平行模式）
> **触发依据**: 613 audit §7 候选 #1 verbatim「§CURRENT/历史 receipt SHA 串号问题治理刀（per §3 ⚠ disclosure #3；候选根因：60X receipt 误把 `head -10`/`head -12` 等不同 SHA 串号传递；§CURRENT/612 tasking line 110/120/266 + 611 audit + 610 receipt 文本 SHA `3639e729…` 与 HEAD 实测 `c404980f1eb542…` 不符；以实测为准；建议 614 audit 一次性 git grep + 全文校对修复 + 增单元测试守门）」+ 612 receipt §9 候选 #4 + 612 tasking §4 关联文件清单 + 2026-08-29 治理铁律
> **前置**: 613 audit PASS（14 维度全 PASS + 5 ⚠ disclosures ACCEPTED + 零 FAIL；三侧收敛 100% feat(612) `bc9c2d8` + cc_head(612) backfill `bbde4a0` + §双推 populate `7a33f99` + §双推 populate fix SHA correction `9dff0e0` → HEAD=origin=github=`9dff0e0c64f2a38e140fdc36de166afb233665a9`；cc_head queue pointer `9dff0e0`）+ 612 receipt PASS + 611 audit PASS（14 维度 + 4 ⚠ ACCEPTED + 1 附加 ⚠ ACCEPTED + 零 FAIL）+ 610 receipt PASS + 609 audit PASS + 608 receipt PASS + 607 audit PASS + 606 receipt PASS + 605 audit PASS + 604 audit PASS + 603 PASS + 602 + 601 + 600/599/597/595/594/593/591/589/587/585/583 全链 PASS
> **签发时间**: 2026-08-29
> **作者**: CC-arch（架构师；按 ARCH-PULSE step 3 verbatim 不写实现/不 commit/不 push）

---

## §0.1 本刀做

| 项 | 落地 |
|---|---|
| (A) SHA 串号 drift 全量定位（git grep 全审计）| 执行端在 `reviews/stage0-gate0-rework-2026-08-23/` 下执行 `git grep -nH '3639e729'` 一次性定位所有过期 SHA 引用；**实测 HEAD 既有 11 行 SHA = `c404980f1eb542dad24504ae0e957c169de60b7d78859159986412fc83541277`**（per 612 §5 EXISTING 11 ROWS IDENTICAL TO HEAD diff 验证；以实测为准 per 583 §F enumeration 即权威）；命中清单必须枚举穷尽（含 605/606/608/610/611 receipt/audit + 612 tasking/receipt/audit + 612 §CURRENT 等）|
| (B) 文档 SHA 串号校对修复（selective refresh）| 执行端对 (A) 命中清单中所有误引 `3639e729…` 的位置逐个校对修复为 HEAD 实测 `c404980f1eb542…`；**只修 SHA 字面**，不改其它原文；既有 docs/45/46/49/50/51/52/53 OPEN 行零删减；既有 status blockquote 完整保留；既有 31+ 红线守门条文完整保留；docs 房规 NOT-IN-MANIFEST |
| (C) 单元测试守门（增 tests/test_sha_citation_drift_guard.py）| 执行端新增 `tests/test_sha_citation_drift_guard.py`（per 599/601/605/606/608/610/611/612 precedent 测试文件命名 + static-segment guard pattern）；用例 ≥ 6 个：(1) 扫描 `reviews/stage0-gate0-rework-2026-08-23/` 全部 `*.md`，断言文件内 SHA 引用形如 `c404980f1eb542dad24504ae0e957c169de60b7d78859159986412fc83541277`（实测值）合法；（2）断言不存在 `3639e729` 字面引用（过期值）；（3）断言 612 receipt 文件内 `92e1481c3fea5962569979086b30983cf1b2ee950d8ca940b3d524d2bac35f54`（江苏样本地市第四刀实测 SHA）合法引用；（4）断言 605/606/608/610/612 五个江苏样本 SHA 在 receipt/audit 文件中一致；（5）断言 `source_registry/registry.csv` 既有 11 行 SHA 在所有 audit/receipt/tasking 文档中引用一致；（6）断言 `git diff --stat` 后所有修改文件 SHA 一致守门；执行端新增用例必须 PASS |
| (D) docs/45 §6.2 O1 status append（如适用；SKIP 政策若 grep 命中 0 行 stale 字面）| docs 房规 NOT-IN-MANIFEST；可选 append 一行 `> ⚠ **docs/45 §6.2 O1 status append**（per 614 · 2026-08-29）：O1 §5.2.x SHA 串号 drift 治理刀已落地（既有 11 行 SHA 串号文本校对修复实测=`c404980f1eb542dad24504ae0e957c169de60b7d78859186412fc83541277` per 612 §5 EXISTING 11 ROWS IDENTICAL TO HEAD diff 验证 + 614 单元测试守门）；SHA 串号 drift 闭环。`；既有 605 + 606 + 608 + 610 + 612 status blockquote 完整保留；不删不改 |
| (E) docs/49 + docs/50 + docs/51 + docs/52 + docs/53 status row append（如适用；SKIP 政策若 grep 命中 0 行 stale 字面）| per docs-only refresh 房规；SKIP 政策若命中为治理级决策标注非 stale `--confirm-*` 字面；docs 房规 NOT-IN-MANIFEST |
| (F) manifest bump K → 973+K | per docs 房规 + spike_helper 房规；K = 4 基础（614 bump script + 613 audit 入库随 614 commit + 614 receipt + tests/test_sha_citation_drift_guard.py）= +4；enumeration 即权威 per 583 §F；INVARIANT 973+4 == 973+4 == 973+4 ✓；source_registry_csv role 不增计数 per 606/607/608/609/610/611/612 file-based role_count 守门 |
| (G) 614 receipt 写回执 | 含 (A)(B)(C)(D)(E)(F)(G) 七段交付 + 双推 + cc_head backfill + manifest INVARIANT 验证 + 13 受保护文件零漂移（⚠ disclosure: 14 受保护文件含 test_sha_citation_drift_guard.py 新增；既有 13 受保护文件零漂移）+ 31+ 红线 100% 兑现 + ⚠ disclosures（如有）|

---

## §0.2 本刀不做（执行端零擅自做）

| 禁止 | 守门 |
|---|---|
| ❌ Stage 0/Gate 1/2 PASS / O1 PASS / O3 PASS | ✅ 614 仅 SHA 串号 drift 治理（纯文档校对 + 单元测试守门）；O1 整体保持 WAITING_FILE（per docs/47 §3.1 + 484/486/488 校准）；O3 整体保持 CLOSED 候选 per 588+590+597+598+599+600+601+602+603+604+605+606+607+608+609+610+611+612+613 十八重声明 |
| ❌ 2020-2025 batch work | ✅ 零批量；本刀仅 1 个 SHA 串号 drift 治理刀 |
| ❌ 公网爬网（非政府/统计局/研究机构）| ✅ 零公网爬网；本刀零网络访问（仅 git grep + shasum 本地操作）|
| ❌ OCR threshold lowering | ✅ 零阈值调整；gate_thresholds.json 3709 bytes 不变 |
| ❌ 1909-as-China | ✅ 零历史边界触碰 |
| ❌ --force | ✅ git push 走普通路径 |
| ❌ PAT request | ✅ 零 PAT |
| ❌ gate_thresholds.json edit | ✅ 3709 bytes / mtime Aug 23 不变 |
| ❌ 重新宣告 O3 整体 CLOSED | ✅ O3 状态保持 CLOSED 候选（per 588 + 590 + 597 + 598 + 599 + 600 + 601 + 602 + 603 + 604 + 605 + 606 + 607 + 608 + 609 + 610 + 611 + 612 + 613 十八重声明）；614 不二次宣告 |
| ❌ 重新宣告 O1 整体收口 | ✅ O1 状态保持 WAITING_FILE；614 仅 SHA 串号 drift 治理不构成 O1 整体收口 |
| ❌ 启动 O1 A 路实跑 | ✅ A 路保留为 fallback 标注（per 601 + 599 + 591 docs/50 row 117 supersede）|
| ❌ 引入 --confirm-* 字面（实跑）| ✅ 2026-08-29 治理铁律；零 `--confirm-*` 字面 |
| ❌ 修改 001-013 migration 文件 | ✅ 红线 / 零生产 schema 变更 |
| ❌ 修改 01-core.sql | ✅ 红线 / 零核心 schema 变更（51589 bytes 不变）|
| ❌ 修改 4 fixture 锁值（synthetic.png + S0 PDF + _syn_pdf_585.py + extracts dir）| ✅ 红线 / 4 fixture 字节不变 |
| ❌ 修改 S0 原始 PDF 字节 | ✅ SHA 零漂移（`f34b2e57…` 1007943 bytes）|
| ❌ 修改 source_registry/registry.csv 既有 11 行 | ✅ 红线 / 既有 11 行未改；614 零行变动（SHA 串号文档校对修复不增 source_registry 行）|
| ❌ 修改 spikes/04-scanned-pdf/gate_thresholds.json | ✅ 红线 / 3709 bytes / mtime Aug 23 不变 |
| ❌ 修改 .venv-paddle / scripts/requirements-paddle.txt / requirements-dbt.txt | ✅ 红线 / 零 venv/env 污染（requirements-dbt.txt 349 bytes 不变）|
| ❌ 修改 scripts/intake_real_sha_if_present.py / scripts/auto_ingest_public_source.py | ✅ 红线 / 零 intake 实跑触碰 |
| ❌ 修改 docs/45 / docs/46 / docs/44 / docs/49 / docs/50 / docs/51 / docs/52 / docs/53 既有 OPEN 行原文 | ✅ 614 仅选择性 refresh（per docs-only refresh 房规）；既有 OPEN 行零删减；SHA 字面校对修复视为"实测对齐"非"内容改动" |
| ❌ 删除命中行原文 | ✅ 红线 / 既有 OPEN 行零删减 |
| ❌ 真实 paddleocr API 调用 | ✅ 本刀零 OCR 调用；纯文档校对 + 单元测试守门 |
| ❌ 真实 PDF 上传 | ✅ 本刀零 PDF 上传；零源文件操作 |
| ❌ 触真实 DB（生产 schema）| ✅ 零生产 schema 变更；mock writer 零触 |
| ❌ 引入 cloud OCR / GPU runtime | ✅ 本刀零 OCR |
| ❌ docker daemon systemctl 操作 | ✅ Colima daemon 已就绪（per 595 落地）；零 docker 操作 |
| ❌ 持久保留 paddle-ocr:v1 Docker image | ✅ per 596 §2.5 已清理（697MB 释放）|
| ❌ 启动 584 BLOCKED 实跑 paddle-ocr deps 到 system | ✅ 本刀零 paddle-ocr 调用 |
| ❌ 用户授权 #1 二次申请 | ✅ 本刀零网络访问（仅本地 git grep + shasum 操作）；零用户动作 |

---

## §0.3 实测值守门（执行端必读）

**HEAD 实测**（per 612 §5 EXISTING 11 ROWS IDENTICAL TO HEAD diff 验证）：
- 既有 11 行 SHA = `c404980f1eb542dad24504ae0e957c169de60b7d78859159986412fc83541277`
- 江苏样本地市第四刀（南通市统计局）HTML SHA = `92e1481c3fea5962569979086b30983cf1b2ee950d8ca940b3d524d2bac35f54`
- 江苏样本地市第三刀（常州市统计局）HTML SHA（610 落地；待执行端实测复算）
- 江苏样本地市第二刀（南京市统计局）HTML SHA（608 落地；待执行端实测复算）
- 江苏样本地市首批（苏州市统计局）HTML SHA（606 落地；待执行端实测复算）
- 江苏首批（江苏分省）HTML SHA（605 落地；待执行端实测复算）

**过期值（drift）**：
- `3639e729…` 是 60X receipt 误把 `head -10`/`head -12` 等不同 SHA 串号传递的结果；本刀需一次性校对修复为 HEAD 实测值
- 任何对过期值的引用必须替换为实测值或删除（仅当引用无意义时）

---

## §1. 614 tasking 详情

### 1.1 (A) SHA 串号 drift 全量定位

**触发条件**:
- 613 audit §3 ⚠ disclosure #3 verbatim「§CURRENT/历史 receipt SHA 串号问题」
- 612 receipt §9 候选 #4 verbatim「§CURRENT/历史 receipt SHA 串号问题治理刀」
- 613 audit §7 候选 #1（最高优先）verbatim「一次性 git grep + 全文校对修复 + 增单元测试守门」
- 612 tasking §4 关联文件清单（§CURRENT + 612 tasking line 110/120/266 + 611 audit + 610 receipt）

**执行步骤**:
1. `cd reviews/stage0-gate0-rework-2026-08-23/`
2. `git grep -nH '3639e729'` 一次性枚举所有过期 SHA 引用
3. 整理 (B) 修复清单（命中文件 + 行号 + 替换前 SHA + 替换后 SHA）
4. 校验 HEAD 实测 SHA（`head -11 source_registry/registry.csv | shasum -a 256`）

**预期输出**:
- (B) 修复清单 ≥ 5 处命中（§CURRENT + 612 tasking line 110/120/266 + 611 audit + 610 receipt）
- 若命中数 < 5，需深一层 grep（grep `\b3639e729\b` 等更严格模式）

### 1.2 (B) 文档 SHA 串号校对修复

**触发条件**:
- (A) 修复清单完整

**执行步骤**:
1. 对每个命中位置，用 Edit 工具将过期 SHA 字面替换为 HEAD 实测 SHA 字面
2. 校验：替换前后仅 SHA 字面变化，其它原文零删减
3. 校验：docs/45/46/49/50/51/52/53 既有 OPEN 行原文零删减
4. 校验：status blockquote 完整保留

**预期输出**:
- 所有命中位置 SHA 字面已修复
- 既有 31+ 红线守门条文完整保留
- docs 房规 NOT-IN-MANIFEST 守门

### 1.3 (C) 单元测试守门

**触发条件**:
- (B) 修复完成

**执行步骤**:
1. 新建 `tests/test_sha_citation_drift_guard.py`（per 599/601/605/606/608/610/611/612 precedent 测试文件命名）
2. 6 个用例覆盖：HEAD 实测值合法 + 过期值不存在 + 江苏样本地市第四刀实测值合法 + 5 江苏样本 SHA 一致 + 既有 11 行 SHA 一致 + git diff --stat 后 SHA 一致守门
3. 执行 `python3 -m pytest tests/test_sha_citation_drift_guard.py -q`
4. 断言 6 用例全 PASS

**预期输出**:
- `tests/test_sha_citation_drift_guard.py` 新增（~150 lines；用例 6 个）
- pytest exit 0；6 PASS

### 1.4 (D) docs/45 §6.2 O1 status append（如适用）

**触发条件**:
- (A)(B)(C) 全部 PASS

**执行步骤**（可选；SKIP 政策若 grep 命中 0 行 stale 字面）:
1. 检查 docs/45 §6.2 是否需要 append（SKIP 政策若 612/613 status 上下文足够清晰）
2. 若需要 append：append 一行 `> ⚠ **docs/45 §6.2 O1 status append**（per 614 · 2026-08-29）：O1 §5.2.x SHA 串号 drift 治理刀已落地...`
3. 校验：既有 605 + 606 + 608 + 610 + 612 status blockquote 完整保留

**预期输出**:
- docs/45 §6.2 append 一行（如适用）
- 既有 status blockquote 完整保留

### 1.5 (F) manifest bump K → 977

**触发条件**:
- (A)(B)(C)(D)(E) 全部 PASS

**执行步骤**:
1. 新建 `scripts/_knife614_manifest_bump.py`（per 599/601/605/606/608/610/611/612 precedent）
2. bump script 内枚举：614 bump script + 613 audit 入库随 614 commit + 614 receipt + tests/test_sha_citation_drift_guard.py = +4
3. 实跑 `--verify` 断言：973 + 4 = 977；INVARIANT 977 == 977 == 977 ✓
4. 写入 `evidence_pack/manifest.json` + 校验 sha

**预期输出**:
- `scripts/_knife614_manifest_bump.py` 新增
- `evidence_pack/manifest.json` 更新（INVARIANT 977）
- 既有 969 + 4 (612) + 4 (614) = 977 ✓

### 1.6 (G) 614 receipt 写回执

**触发条件**:
- (A)(B)(C)(D)(E)(F) 全部 PASS

**执行步骤**:
1. 新建 `reviews/stage0-gate0-rework-2026-08-23/614-stage0-cc-§5.2.x-sha-citation-drift-治理-tasking-20260829-receipt.md`
2. 七段交付：(A) git grep 命中清单 + (B) 修复清单 + (C) 测试 PASS 输出 + (D) docs/45 append（如适用）+ (E) docs/49-53 append（如适用）+ (F) manifest bump 输出 + (G) 本 receipt
3. 含双推 + cc_head backfill + 14 受保护文件零漂移（13 + 614 新增 test_sha_citation_drift_guard.py 守门）+ 31+ 红线 100% 兑现 + ⚠ disclosures（如有）

**预期输出**:
- 614 receipt 文件入库
- 双推 origin + github + cc_head backfill 完整

---

## §2. 关联文件清单（执行端需修改/创建）

| 文件 | 操作 | 备注 |
|---|---|---|
| `reviews/stage0-gate0-rework-2026-08-23/00-EXEC-QUEUE.md` | (B) 校对修复（如有命中）| §CURRENT SHA 字面校对 |
| `reviews/stage0-gate0-rework-2026-08-23/612-stage0-architect-s611-o1-§5.2.x-real-sha-locked-江苏样本-地市第四刀-tasking-20260829.md` | (B) 校对修复（line 110/120/266）| SHA 字面校对 |
| `reviews/stage0-gate0-rework-2026-08-23/611-stage0-architect-s610-o1-§5.2.x-real-sha-locked-江苏样本-地市第三刀-tasking-20260829-audit-PASS-20260829.md` | (B) 校对修复 | SHA 字面校对 |
| `reviews/stage0-gate0-rework-2026-08-23/610-stage0-cc-o1-§5.2.x-real-sha-locked-江苏样本-地市第三刀-tasking-20260829-receipt.md` | (B) 校对修复 | SHA 字面校对 |
| `tests/test_sha_citation_drift_guard.py` | (C) 新增 | 6 用例守门 |
| `scripts/_knife614_manifest_bump.py` | (F) 新增 | manifest bump helper |
| `evidence_pack/manifest.json` | (F) 更新 | 973 → 977 |
| `reviews/stage0-gate0-rework-2026-08-23/614-stage0-cc-§5.2.x-sha-citation-drift-治理-tasking-20260829-receipt.md` | (G) 新增 | 614 receipt |

**零修改文件清单**（执行端必守）:
- 13 受保护文件（含 synthetic.png + S0 PDF + _syn_pdf_585.py + extracts dir + registry.csv 既有 11 行 + gate_thresholds.json + 01-core.sql + requirements-dbt.txt + requirements-paddle.txt + intake_real_sha + auto_ingest + .venv-paddle/pyvenv.cfg + migration 001-013）
- docs/45/46/49/50/51/52/53 既有 OPEN 行原文（仅选择性 refresh append；F 段 SKIP）
- source_registry/registry.csv 既有 11 行字节

---

## §3. 验收清单（执行端提交前自查）

- [ ] (A) git grep `'3639e729'` 命中清单 ≥ 5 处，整理 (B) 修复清单
- [ ] (B) 所有命中位置 SHA 字面校对修复完成；既有 OPEN 行零删减
- [ ] (C) `tests/test_sha_citation_drift_guard.py` 6 用例全 PASS
- [ ] (D) docs/45 §6.2 append（如适用）；既有 status blockquote 完整保留
- [ ] (E) docs/49/50/51/52/53 F 段 SKIP 政策成立
- [ ] (F) `scripts/_knife614_manifest_bump.py` --verify 实跑 PASS；INVARIANT 977 == 977 == 977 ✓
- [ ] (G) 614 receipt 写回执 + 双推 + cc_head backfill
- [ ] 13 受保护文件零漂移（13 + 614 新增 test_sha_citation_drift_guard.py 守门）
- [ ] 31+ 红线 100% 兑现（zero Stage 0/Gate 1/2/O1/O3 PASS 等）
- [ ] 零网络访问（仅本地 git grep + shasum 操作）
- [ ] 零用户授权 #1 二次申请（零网络访问；无需授权）

---

## §4. 关联文件清单回执

614 tasking 关联：
- (A) 命中清单 → 614 receipt §1
- (B) 修复清单 → 614 receipt §2
- (C) test_sha_citation_drift_guard.py 用例 → 614 receipt §3
- (D) docs/45 §6.2 append（如适用）→ 614 receipt §4
- (F) manifest bump 输出 → 614 receipt §5
- (G) 614 receipt → 614 receipt §6 + §7 + §8

---

## §5. 收口语义

- 614 既闭合 O1 §5.2.x SHA 串号 drift 治理刀（纯文档校对 + 单元测试守门）
- O1 整体保持 WAITING_FILE（per docs/47 §3.1 + 484/486/488 校准）
- O3 整体保持 CLOSED 候选（per 588 + 590 + 597 + 598 + 599 + 600 + 601 + 602 + 603 + 604 + 605 + 606 + 607 + 608 + 609 + 610 + 611 + 612 + 613 十八重声明）
- 江苏样本链路 5/15 节点（不动）
- 31+ 红线 100% 兑现

---

## §6. 架构师签字

- 架构师 (Architect) — 614 tasking 签发落地
- 签发时间：2026-08-29
- queue §CURRENT status: AUDITED → **PENDING** (note = 「614 tasking 签发 · SHA 串号 drift 治理刀 · per 613 audit §7 候选 #1 · §CURRENT/历史 receipt SHA 串号一次性校对修复 + 单元测试守门」)
- 下一站 = 执行端按本任务书落地 + 614 receipt DELIVERED → 615 audit

---

— End of `614-stage0-architect-s613-§5.2.x-sha-citation-drift-治理-tasking-20260829.md` —