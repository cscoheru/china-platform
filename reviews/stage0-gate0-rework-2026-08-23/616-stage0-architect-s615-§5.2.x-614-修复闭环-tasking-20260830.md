# 616-stage0-architect-s615-§5.2.x-614-修复闭环-tasking-20260830

> **任务书类型**: 架构师签发 → 执行端实施（per ARCH-PULSE step 3 verbatim 583/585/587/589/591/593/594/595/596/597/598/599/600/601/602/603/604/605/606/607/608/609/610/611/612/613/614/615 平行模式）
> **触发依据**: 615 audit §7.1 优先级 1 verbatim「**615 tasking = 614 修复闭环刀**（per FAIL #1 + FAIL #3 处置）」+ 615 audit §4 FAIL items #1（(A) scope miss — 613 audit 4 处 bare `3639e729` 未修）+ #2（(B) v3 fix log "post-fix [empty]" 失实）+ #3（(C) 单元测试 2/6 FAIL — test_2 + test_6 结构性悖论 + 613 audit scope miss 联动）+ 614 tasking §3 验收清单 verbatim + 614 receipt §9 + 2026-08-29 治理铁律
> **前置**: 615 audit FAIL 落地（14 维度 11 PASS + 3 FAIL + 4 ⚠ disclosures ACCEPTED + 零额外 FAIL；三侧收敛 100% feat(614) `106f9c6` + cc_head(614) backfill `0ed1359` + §双推 populate `eba8882` → HEAD=origin=github=`eba8882d32456304707e782b838ca46bd5982d57`；cc_head queue pointer `eba8882d`）+ 614 receipt DELIVERED + 614 receipt 包含 (A)(B)(D)(E)(F)(G) 6/7 段 PASS + (C) 单元测试 4/6 PASS（test_2 + test_6 FAIL） + 613 audit PASS（14 维度全 PASS + 5 ⚠ ACCEPTED + 零 FAIL）+ 612 receipt PASS + 611 audit PASS + 610 receipt PASS + 609 audit PASS + 608 receipt PASS + 607 audit PASS + 606 receipt PASS + 605 audit PASS + 604 audit PASS + 603 + 602 + 601 + 600/599/597/595/594/593/591/589/587/585/583 全链 PASS
> **签发时间**: 2026-08-30
> **作者**: CC-arch（架构师；按 ARCH-PULSE step 3 verbatim 不写实现/不 commit/不 push）

---

## §0.1 本刀做

| 项 | 落地 |
|---|---|
| (A') **scope 扩展**（grep 全量定位 scope 扩展）| 执行端在 `reviews/stage0-gate0-rework-2026-08-23/` 下执行 `git grep -nH '3639e729'` 一次性枚举**所有**过期 SHA 引用（**scope 必须显式包含 architect-authored audit / receipt / tasking 文件**——per 615 audit FAIL #1 root cause；614 遗漏 613 audit 4 处）；实测应枚举 ≥ 7 文件 ≥ 31 行 ≥ 35 处 occurrences（per 614 receipt §1 实测 7 文件 31 行 35 处）|
| (B') **修复清单扩展**（per FAIL #1 修复清单 miss）| 修复清单必须显式列出：(i) **613 audit 4 处** bare `3639e729` 字面（line 170 ⚠ #3 disclosure + line 225 §7 候选 #1）；(ii) **00-EXEC-QUEUE.md §CURRENT/§DELIVERED 中 7 处** `3639e729` 字面（**改写叙事措辞**为「`3639e729<…>` 过期 8-char prefix」+ 反引号包裹；保留为合法叙事但避免 bare 字面作为权威 SHA 形式）；(iii) **614 receipt 中 9 处** bare `3639e729` 字面（同上改写叙事措辞）；(iv) 既有 5 文件 27 行 SHA 字面校对修复（per 614 receipt §2 已落地，**仅 SHA 字面替换不改其他原文**；既有 docs/45/46/49/50/51/52/53 OPEN 行零删减；status blockquote 完整保留；31+ 红线守门条文完整保留；docs 房规 NOT-IN-MANIFEST）|
| (C') **测试重写**（per FAIL #3 结构性悖论）| 执行端**编辑（in-place）** `tests/test_sha_citation_drift_guard.py`（保留现有 4 个 PASS 用例：test_1 + test_3 + test_4 + test_5；**重写** test_2 + test_6）：新断言语义 = 「**没有文件把 `3639e729` 作为权威 SHA 引用**」；实现方法 = (α) 从 grep 范围排除 `*-receipt.md` + `*-audit-*.md` + `*-tasking-*.md` 的 narrative content；或 (β) 用更严格 pattern（如 `git grep -nH -E '(registry\.csv|manifest\.json|01-core\.sql).*3639e729'` 等关键引用点匹配）；pytest exit 0；**6 用例全 PASS**（per 615 audit §7.1 priority 1 (C') verbatim）|
| (D') docs/45 §6.2 O1 status append（per 615 · 2026-08-30）| append 一行 `> ⚠ **docs/45 §6.2 O1 status append**（per 615 · 2026-08-30）：O1 §5.2.x SHA 串号 drift 治理刀（部分落地 + 修复闭环 + 单元测试守门 6 用例全 PASS）已闭合；既有 11 行 SHA 串号文本校对修复实测=`c404980f1eb542dad24504ae0e957c169de60b7d78859159986412fc83541277` per 614 §0.3 实测值守门；615 audit FAIL 修复闭环；613 audit + 614 receipt + 00-EXEC-QUEUE.md narrative `3639e729<…>` 改写完成；测试重写完成。`；既有 605 + 606 + 608 + 610 + 612 + 614 status blockquote 完整保留；既 Gate 2 PASS / W8 评审日期完整保留；不删不改；docs 房规 NOT-IN-MANIFEST|
| (E') docs/49 + docs/50 + docs/51 + docs/52 + docs/53 status row append（如适用；SKIP 政策若 grep 命中 0 行 stale 字面）| per docs-only refresh 房规；SKIP 政策若命中为治理级决策标注非 stale `--confirm-*` 字面；docs 房规 NOT-IN-MANIFEST|
| (F') manifest bump K = 3 → 977 → 980 | per docs 房规 + spike_helper 房规；K = 3 基础：(1) `scripts/_knife616_manifest_bump.py` NEW spike_helper +1；(2) **615 audit 入库随 616 commit** NEW documentation +1；(3) **616 receipt** NEW documentation +1；enumeration 即权威 per 583 §F；INVARIANT 980 == 980 == 980 ✓；source_registry_csv role 不增计数 per 606/607/608/609/610/611/612 file-based role_count 守门；test_sha_citation_drift_guard.py in-place edit 不增计数 per 615 audit §7.1 (C') priority 1 verbatim「保留 test_1 + test_3 + test_4 + test_5 四个 PASS 用例」|
| (G') 616 receipt 写回执 | 含 (A')(B')(C')(D')(E')(F')(G') 七段交付 + 双推 + cc_head backfill + manifest INVARIANT 验证 + 14 受保护文件零漂移（13 既有 + 615 audit 入库随 616 commit + 616 receipt 自身 + test_sha_citation_drift_guard.py in-place edit 不变）+ 31+ 红线 100% 兑现 + ⚠ disclosures ACCEPTED|

---

## §0.2 本刀不做（执行端零擅自做）

| 禁止 | 守门 |
|---|---|
| ❌ Stage 0/Gate 1/2 PASS / O1 PASS / O3 PASS | ✅ 616 仅 614 修复闭环（scope 扩展 + 修复 + 测试重写 + docs/45 append + manifest bump + receipt）；O1 整体保持 WAITING_FILE（per docs/47 §3.1 + 484/486/488 校准）；O3 整体保持 CLOSED 候选 per 588+590+597+598+599+600+601+602+603+604+605+606+607+608+609+610+611+612+613 十九重声明 + 615 续接 = 二十重声明 |
| ❌ 2020-2025 batch work | ✅ 零批量；本刀仅 1 个 SHA 串号 drift 修复闭环刀 |
| ❌ 公网爬网（非政府/统计局/研究机构）| ✅ 零公网爬网；本刀零网络访问（仅本地 git grep + shasum + pytest 操作）|
| ❌ OCR threshold lowering | ✅ 零阈值调整；gate_thresholds.json 3709 bytes 不变 |
| ❌ 1909-as-China | ✅ 零历史边界触碰 |
| ❌ --force | ✅ git push 走普通路径 |
| ❌ PAT request | ✅ 零 PAT |
| ❌ gate_thresholds.json edit | ✅ 3709 bytes / mtime Aug 23 不变 |
| ❌ 重新宣告 O3 整体 CLOSED | ✅ O3 状态保持 CLOSED 候选（per 588+590+597+598+599+600+601+602+603+604+605+606+607+608+609+610+611+612+613 十九重声明 + 615 续接 = 二十重声明）；616 不二次宣告 |
| ❌ 重新宣告 O1 整体收口 | ✅ O1 状态保持 WAITING_FILE；616 仅 SHA 串号 drift 修复闭环不构成 O1 整体收口 |
| ❌ 启动 O1 A 路实跑 | ✅ A 路保留为 fallback 标注（per 601 + 599 + 591 docs/50 row 117 supersede）|
| ❌ 引入 --confirm-* 字面（实跑）| ✅ 2026-08-29 治理铁律；零 `--confirm-*` 字面 |
| ❌ 修改 001-013 migration 文件 | ✅ 红线 / 零生产 schema 变更 |
| ❌ 修改 01-core.sql | ✅ 红线 / 零核心 schema 变更（51589 bytes 不变）|
| ❌ 修改 4 fixture 锁值（synthetic.png + S0 PDF + _syn_pdf_585.py + extracts dir）| ✅ 红线 / 4 fixture 字节不变 |
| ❌ 修改 S0 原始 PDF 字节 | ✅ SHA 零漂移（`f34b2e57…` 1007943 bytes）|
| ❌ 修改 source_registry/registry.csv 既有 11 行 | ✅ 红线 / 既有 11 行未改；616 零行变动（SHA 串号修复不增 source_registry 行）|
| ❌ 修改 spikes/04-scanned-pdf/gate_thresholds.json | ✅ 红线 / 3709 bytes / mtime Aug 23 不变 |
| ❌ 修改 .venv-paddle / scripts/requirements-paddle.txt / requirements-dbt.txt | ✅ 红线 / 零 venv/env 污染（requirements-dbt.txt 349 bytes 不变）|
| ❌ 修改 scripts/intake_real_sha_if_present.py / scripts/auto_ingest_public_source.py | ✅ 红线 / 零 intake 实跑触碰 |
| ❌ 修改 docs/45 / docs/46 / docs/44 / docs/49 / docs/50 / docs/51 / docs/52 / docs/53 既有 OPEN 行原文 | ✅ 616 仅选择性 refresh append（per docs-only refresh 房规）；既有 OPEN 行零删减；SHA 字面校对修复视为"实测对齐"非"内容改动"；narrative 措辞改写保留为合法叙事但避免 bare `3639e729` 字面作为权威 SHA 形式 |
| ❌ 删除命中行原文 | ✅ 红线 / 既有 OPEN 行零删减；narrative 改写仅修字面包装形式（`3639e729<…>` vs bare `3639e729`），不改原文措辞语义 |
| ❌ 真实 paddleocr API 调用 | ✅ 本刀零 OCR 调用；纯文档校对 + 单元测试守门 + docs append |
| ❌ 真实 PDF 上传 | ✅ 本刀零 PDF 上传；零源文件操作 |
| ❌ 触真实 DB（生产 schema）| ✅ 零生产 schema 变更；mock writer 零触 |
| ❌ 引入 cloud OCR / GPU runtime | ✅ 本刀零 OCR |
| ❌ docker daemon systemctl 操作 | ✅ Colima daemon 已就绪（per 595 落地）；零 docker 操作 |
| ❌ 持久保留 paddle-ocr:v1 Docker image | ✅ per 596 §2.5 已清理（697MB 释放）|
| ❌ 启动 584 BLOCKED 实跑 paddle-ocr deps 到 system | ✅ 本刀零 paddle-ocr 调用 |
| ❌ 用户授权 #1 二次申请 | ✅ 本刀零网络访问（仅本地 git grep + shasum + pytest 操作）；零用户动作 |
| ❌ 修改 614 receipt 掩盖 FAIL | ✅ 614 receipt 已落地（含 FAIL #3 自我披露）— 616 仅改 narrative 措辞包裹形式，不删不改 614 receipt 实质内容 |
| ❌ 修改 615 audit 文件 | ✅ 615 audit 由架构师自签；执行端零修改；615 audit 仅随 616 commit 入库（per docs 房规「审计文件不单独 commit 随下一刀入库」）|
| ❌ 新建 tests/test_sha_citation_drift_guard_v2.py | ✅ per 615 audit §7.1 priority 1 (C') verbatim「保留 test_1 + test_3 + test_4 + test_5 四个 PASS 用例」；in-place edit 既有文件，不创建 v2 新文件 |

---

## §0.3 实测值守门（执行端必读）

**HEAD 实测**（per 612 §5 EXISTING 11 ROWS IDENTICAL TO HEAD diff 验证 + 614 §0.3 沿用）：
- 既有 11 行 SHA = `c404980f1eb542dad24504ae0e957c169de60b7d78859159986412fc83541277`（实测 `head -11 source_registry/registry.csv | shasum -a 256`）
- 江苏样本地市第四刀（南通市统计局）HTML SHA = `92e1481c3fea5962569979086b30983cf1b2ee950d8ca940b3d524d2bac35f54`
- 江苏样本地市第三刀（常州市统计局）HTML SHA = `0ecf3d2ed76407c4bf50a5cba8552af78ca2e22fcc5ab39966b1212aac6979f6`
- 江苏样本地市第二刀（南京市统计局）HTML SHA = `37ed4c223b16397f66781744987dafa6ab975fc0ceb7006a028b3edb62ce2712`
- 江苏样本地市首批（苏州市统计局）HTML SHA = `df3d8246679040968a747762d8c11eccf7b63647cadfc2c50719322badf7c7fd`
- 江苏首批（江苏分省）HTML SHA = `450e7f723795241c58c34c3c8f18147cf289db04c3fa2bbbdd7c0db564f49279`

**过期值（drift）**（per 615 audit FAIL #1 + FAIL #2 + FAIL #3 处置）：
- `3639e729<…>` 是 60X receipt 误把 `head -10`/`head -12` 等不同 SHA 串号传递的结果；本刀需一次性校对修复为 HEAD 实测值或改写叙事措辞为「`3639e729<…>` 过期 8-char prefix」+ 反引号包裹（避免 bare `3639e729` 字面作为权威 SHA 形式）
- truncated 61-char SHA `c404980f1eb542dad24504ae0e957c169de60b7d78859186412fc83541277`（缺 `5998` 4 字符）同样需要「truncated 61-char SHA」+ 反引号包裹
- 任何对过期值的引用必须替换为实测值或**改写为过期 8-char prefix 形式**

---

## §1. 616 tasking 详情

### 1.1 (A') SHA 串号 drift 全量定位 scope 扩展

**触发条件**:
- 615 audit §4 FAIL #1 verbatim「(A) SHA 串号 drift 全量定位 — **scope miss FAIL**」
- 615 audit §7.7 verbatim「**(B) 修复范围** = 35 处 SHA 字面替换（31 处 `3639e729…` + 4 处 truncated 61-char SHA）落地于 5 文件（00-EXEC-QUEUE.md + 609 audit + 610 receipt + 611 audit + 612 receipt）；**(B) 遗漏** = 613 audit 4 处 bare `3639e729` 字面未在 scope 内；615-tasking 续接时纳入修复」

**执行步骤**:
1. `cd reviews/stage0-gate0-rework-2026-08-23/`
2. `git grep -nH '3639e729'` 一次性枚举**所有**过期 SHA 引用（**scope 必须显式包含 architect-authored audit / receipt / tasking 文件**——per 615 audit FAIL #1 root cause；614 遗漏 613 audit 4 处）
3. 整理 (B') 修复清单（命中文件 + 行号 + 替换前 SHA + 替换后 SHA + 处置形式 = 实测替换 OR 改写叙事措辞）
4. 校验 HEAD 实测 SHA（`head -11 source_registry/registry.csv | shasum -a 256`）
5. 同样 `git grep -nH 'c404980f1eb542dad24504ae0e957c169de60b7d78859186412fc83541277'`（truncated 61-char 缺 `5998`）— per 615 audit §维度 4 实测 truncated 1 file 4 occurrences

**预期输出**:
- (B') 修复清单 ≥ 8 文件 ≥ 35 行 ≥ 39 处 occurrences（per 614 receipt §1 实测 7 文件 31 行 35 处 + 615 audit §维度 4 实测 3 文件 20 occurrences post-fix + 1 file 4 occurrences truncated post-fix = 估算 ≥ 8 文件 ≥ 35 行 ≥ 39 处总 occurrences）

### 1.2 (B') 文档 SHA 串号校对修复扩展

**触发条件**:
- (A') 修复清单完整

**执行步骤**:
1. 对每个命中位置，处置 = (i) SHA 字面替换（→ full 64-char HEAD actual `c404980f1eb542dad24504ae0e957c169de60b7d78859159986412fc83541277`）；或 (ii) 改写叙事措辞为「`3639e729<…>` 过期 8-char prefix」+ 反引号包裹（per 615 audit §7.1 priority 1 (B') verbatim）
2. 校验：替换前后仅 SHA 字面或叙事包裹形式变化，其它原文零删减
3. 校验：docs/45/46/49/50/51/52/53 既有 OPEN 行原文零删减
4. 校验：status blockquote 完整保留
5. 校验：31+ 红线守门条文完整保留

**预期输出**:
- 所有命中位置处置完成（实测替换 OR 改写叙事措辞）
- 既有 31+ 红线守门条文完整保留
- docs 房规 NOT-IN-MANIFEST 守门

### 1.3 (C') 单元测试守门重写

**触发条件**:
- (B') 修复完成

**执行步骤**:
1. 编辑（in-place）`tests/test_sha_citation_drift_guard.py`（per 615 audit §7.1 priority 1 (C') verbatim）
2. **保留** 4 个 PASS 用例（不修改）：
   - test_1 HEAD 实测值合法（`c404980f1eb542dad24504ae0e957c169de60b7d78859159986412fc83541277`）
   - test_3 江苏样本地市第四刀实测值合法（`92e1481c3fea5962569979086b30983cf1b2ee950d8ca940b3d524d2bac35f54`）
   - test_4 5 江苏样本 SHA 一致（605 + 606 + 608 + 610 + 612）
   - test_5 既有 11 行 SHA 在所有 audit/receipt/tasking 文档中引用一致
3. **重写** test_2 + test_6（per 615 audit §4 FAIL #3 root cause 处置）：
   - test_2 新断言 = 「**没有文件把 `3639e729` 作为权威 SHA 引用**」（grep 范围排除 `*-receipt.md` + `*-audit-*.md` + `*-tasking-*.md` narrative content；或用更严格 pattern 如 `git grep -nH -E '(registry\.csv|manifest\.json|01-core\.sql).*3639e729'`）
   - test_6 新断言 = 「**没有文件把 truncated 61-char SHA 作为权威 SHA 引用**」（同上 grep 范围排除 + pattern 严格化）
4. 执行 `python3 -m pytest tests/test_sha_citation_drift_guard.py -q`
5. 断言 6 用例全 PASS

**预期输出**:
- `tests/test_sha_citation_drift_guard.py` 编辑（in-place；不创建 v2 新文件）
- pytest exit 0；6 PASS in < 2.5s
- **零 FAIL**（per 615 audit §7.1 priority 1 (C') verbatim「6 用例全 PASS」）

### 1.4 (D') docs/45 §6.2 O1 status append（per 615 · 2026-08-30）

**触发条件**:
- (A')(B')(C') 全部 PASS

**执行步骤**:
1. 检查 docs/45 §6.2 是否需要 append
2. 若需要 append：append 一行 `> ⚠ **docs/45 §6.2 O1 status append**（per 615 · 2026-08-30）：O1 §5.2.x SHA 串号 drift 治理刀（部分落地 + 修复闭环 + 单元测试守门 6 用例全 PASS）已闭合；既有 11 行 SHA 串号文本校对修复实测=...`
3. 校验：既有 605 + 606 + 608 + 610 + 612 + 614 status blockquote 完整保留

**预期输出**:
- docs/45 §6.2 append 一行
- 既有 status blockquote 完整保留

### 1.5 (F') manifest bump K = 3 → 977 → 980

**触发条件**:
- (A')(B')(C')(D')(E') 全部 PASS

**执行步骤**:
1. 新建 `scripts/_knife616_manifest_bump.py`（per 599/601/605/606/608/610/611/612/614 precedent）
2. bump script 内枚举：(1) 616 bump script NEW spike_helper +1；(2) **615 audit 入库随 616 commit** NEW documentation +1；(3) **616 receipt** NEW documentation +1 = K = +3
3. 实跑 `--verify` 断言：977 + 3 = 980；INVARIANT 980 == 980 == 980 ✓
4. 写入 `evidence_pack/manifest.json` + 校验 sha

**预期输出**:
- `scripts/_knife616_manifest_bump.py` 新增
- `evidence_pack/manifest.json` 更新（INVARIANT 980）
- 既有 977 + 3 (616) = 980 ✓

### 1.6 (G') 616 receipt 写回执

**触发条件**:
- (A')(B')(C')(D')(E')(F') 全部 PASS

**执行步骤**:
1. 新建 `reviews/stage0-gate0-rework-2026-08-23/616-stage0-cc-§5.2.x-614-修复闭环-tasking-20260830-receipt.md`
2. 七段交付：(A') scope 扩展 grep 命中清单 + (B') 修复清单（含 613 audit + 00-EXEC-QUEUE.md + 614 receipt narrative 改写）+ (C') 测试 PASS 输出（6 用例全 PASS）+ (D') docs/45 append（如适用）+ (E') docs/49-53 append（如适用）+ (F') manifest bump 输出 + (G') 本 receipt
3. 含双推 + cc_head backfill + 14 受保护文件零漂移（13 + 615 audit 入库随 616 commit + 616 receipt 自身 + test_sha_citation_drift_guard.py in-place edit 不变）+ 31+ 红线 100% 兑现 + ⚠ disclosures ACCEPTED

**预期输出**:
- 616 receipt 文件入库
- 双推 origin + github + cc_head backfill 完整

---

## §2. 关联文件清单（执行端需修改/创建）

| 文件 | 操作 | 备注 |
|---|---|---|
| `reviews/stage0-gate0-rework-2026-08-23/00-EXEC-QUEUE.md` | (B') narrative 改写 | 7 处 bare `3639e729` 字面 → 「`3639e729<…>` 过期 8-char prefix」+ 反引号包裹 |
| `reviews/stage0-gate0-rework-2026-08-23/613-stage0-architect-s612-o1-§5.2.x-real-sha-locked-江苏样本-地市第四刀-tasking-20260829-audit-PASS-20260829.md` | (B') SHA 字面替换 | 4 处 bare `3639e729` 字面（line 170 + 225）→ full 64-char HEAD actual |
| `reviews/stage0-gate0-rework-2026-08-23/614-stage0-cc-§5.2.x-sha-citation-drift-治理-tasking-20260829-receipt.md` | (B') narrative 改写 | 9 处 bare `3639e729` 字面 → 「`3639e729<…>` 过期 8-char prefix」+ 反引号包裹 |
| `tests/test_sha_citation_drift_guard.py` | (C') 编辑 in-place | 重写 test_2 + test_6；保留 test_1 + test_3 + test_4 + test_5 |
| `scripts/_knife616_manifest_bump.py` | (F') 新增 | manifest bump helper |
| `evidence_pack/manifest.json` | (F') 更新 | 977 → 980 |
| `reviews/stage0-gate0-rework-2026-08-23/615-stage0-architect-s614-§5.2.x-sha-citation-drift-治理-tasking-20260830-audit-FAIL-20260830.md` | (G') 入库随 616 commit | NEW documentation +1；per docs 房规「审计文件不单独 commit 随下一刀入库」|
| `reviews/stage0-gate0-rework-2026-08-23/616-stage0-cc-§5.2.x-614-修复闭环-tasking-20260830-receipt.md` | (G') 新增 | 616 receipt |

**零修改文件清单**（执行端必守）:
- 13 受保护文件（含 synthetic.png + S0 PDF + _syn_pdf_585.py + extracts dir + registry.csv 既有 11 行 + gate_thresholds.json + 01-core.sql + requirements-dbt.txt + requirements-paddle.txt + intake_real_sha + auto_ingest + .venv-paddle/pyvenv.cfg + migration 001-013）
- docs/45/46/49/50/51/52/53 既有 OPEN 行原文（仅选择性 refresh append；E 段 SKIP）
- source_registry/registry.csv 既有 11 行字节
- 615 audit 文件（架构师自签；执行端零修改）
- 614 receipt 实质内容（仅 narrative 措辞包裹形式改写）

---

## §3. 验收清单（执行端提交前自查）

- [ ] (A') git grep `'3639e729'` 命中清单 ≥ 8 文件 ≥ 35 行 ≥ 39 处 occurrences（含 613 audit + 00-EXEC-QUEUE.md + 614 receipt 等全部 narrative 文档）
- [ ] (B') 所有命中位置处置完成（实测替换 OR 改写叙事措辞包裹形式 = `3639e729<…>` 或 `truncated 61-char SHA` + 反引号包裹）；既有 OPEN 行零删减；narrative 改写仅修字面包裹形式不改原文措辞语义
- [ ] (C') `tests/test_sha_citation_drift_guard.py` 编辑 in-place（不创建 v2 新文件）；test_1 + test_3 + test_4 + test_5 4 个 PASS 用例保留；test_2 + test_6 重写为「无文件把过期 SHA 作为权威 SHA 引用」新断言；**6 用例全 PASS**（per 615 audit §7.1 priority 1 (C') verbatim「执行端新增用例必须 PASS」）
- [ ] (D') docs/45 §6.2 append（per 615 · 2026-08-30）；既有 605 + 606 + 608 + 610 + 612 + 614 status blockquote 完整保留
- [ ] (E') docs/49/50/51/52/53 F 段 SKIP 政策成立
- [ ] (F') `scripts/_knife616_manifest_bump.py` --verify 实跑 PASS；INVARIANT 980 == 980 == 980 ✓
- [ ] (G') 616 receipt 写回执 + 双推 + cc_head backfill + 615 audit 入库随 616 commit
- [ ] 14 受保护文件零漂移（13 既有 + 615 audit 入库随 616 commit + 616 receipt 自身 + test_sha_citation_drift_guard.py in-place edit 不变）
- [ ] 31+ 红线 100% 兑现（zero Stage 0/Gate 1/2/O1/O3 PASS 等）
- [ ] 零网络访问（仅本地 git grep + shasum + pytest 操作）
- [ ] 零用户授权 #1 二次申请（零网络访问；无需授权）
- [ ] 零修改 615 audit 文件（架构师自签；执行端零修改）
- [ ] 零修改 614 receipt 实质内容（仅 narrative 措辞包裹形式改写）
- [ ] 零新建 tests/test_sha_citation_drift_guard_v2.py（in-place edit）

---

## §4. 关联文件清单回执

616 tasking 关联：
- (A') 命中清单 → 616 receipt §1
- (B') 修复清单 → 616 receipt §2
- (C') test_sha_citation_drift_guard.py 用例 → 616 receipt §3
- (D') docs/45 §6.2 append（如适用）→ 616 receipt §4
- (F') manifest bump 输出 → 616 receipt §5
- (G') 616 receipt → 616 receipt §6 + §7 + §8

---

## §5. 收口语义

- 616 既闭合 O1 §5.2.x SHA 串号 drift 治理刀修复闭环（scope 扩展 + 修复 + 单元测试重写 + docs/45 append + manifest bump + receipt）
- O1 整体保持 WAITING_FILE（per docs/47 §3.1 + 484/486/488 校准）
- O3 整体保持 CLOSED 候选（per 588 + 590 + 597 + 598 + 599 + 600 + 601 + 602 + 603 + 604 + 605 + 606 + 607 + 608 + 609 + 610 + 611 + 612 + 613 十九重声明 + 615 续接 = 二十重声明）
- 江苏样本链路 5/15 节点（不动）
- 31+ 红线 100% 兑现

---

## §6. 架构师签字

- 架构师 (Architect) — 616 tasking 签发落地
- 签发时间：2026-08-30
- queue §CURRENT status: DELIVERED（**保持 DELIVERED + 615 audit FAIL note**）→ **PENDING** (note = 「616 tasking 签发 · O1 §5.2.x 614 修复闭环刀 · per 615 audit §7.1 优先级 1 verbatim · scope 扩展 + 修复 613 audit + 测试重写 + 615 receipt」)
- 下一站 = 执行端按本任务书落地 + 616 receipt DELIVERED → 617 audit

---

— End of `616-stage0-architect-s615-§5.2.x-614-修复闭环-tasking-20260830.md` —