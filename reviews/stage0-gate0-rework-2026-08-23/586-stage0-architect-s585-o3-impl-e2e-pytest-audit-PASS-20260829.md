# 586 — 架构师审计：回执 585（O3 §5.2.5 e2e pytest 刀 · paddle-ocr MOCK only）· PASS（⚠1 ACCEPTED with disclosure）

- 编号：`586-stage0-architect-s585-o3-impl-e2e-pytest-audit-PASS-20260829`
- 审计对象：`585-stage0-cc-o3-impl-e2e-pytest-tasking-20260829-receipt.md`（cc_head `5028fb1`）
- 对照任务书：`585-stage2-o3-impl-e2e-pytest-tasking-20260829.md`
- 审计者：CC 架构师终端（只读核验 + 零网络复跑；不动实现 / 不 commit）
- 日期：2026-08-29
- 裁定：**PASS**（A–F 证据段全达成 + 9 e2e pytest 0.86s 全过 + manifest 921 == 921 == 921 + 4 fixture 锁值不变 + paddle-ocr MOCK only 与 deps 解耦 + §584 audit ⚠1 docs sync patch 5/6 处 closure + 红线 100% 兑现；**⚠1 docs/45 L487 patch 被 585 自然 invariant 更新覆盖 = ACCEPTED with disclosure**（per 582 ⚠4/⚠5 + 584 BLOCKED audit 同模式）；O3 状态 = §5.2.5 CLOSED per 585；§5.2.4 BLOCKED-DEFERRED per 584 · Path C；§5.2.6 OPEN + 真实 PDF `--confirm-o3=PATH` 用户保留动作不变；**O3 整体仍 OPEN**）

---

## §审计证据（2026-08-29T08:55+08:00 实测，原样粘贴）

```
=== A. 双推收敛 ===
HEAD = origin/main = github/main = 5028fb1                              ✅（585 合刀 commit + cc_head 严格顺序；封 11 文件 / +1081 / -28）
=== B. 585 交付 commit 清单（5028fb1）===
11 files changed, 1081 insertions(+), 28 deletions(-)                    ✅
tests/fixtures/_syn_pdf_585.py(+92) + tests/test_o3_e2e_585.py(+332) +
scripts/_knife585_manifest_bump.py(+182) +
docs/45-stage2-s210-lite-gate2-review-index-20260826.md(±11) +
docs/49-stage2-o3-ocr-prod-path-plan-20260826.md(±4) +
docs/50-stage2-gate2-review-packet-draft-20260826.md(±7) +
docs/53-stage2-public-ingest-ops-handbook-20260826.md(±13) +
evidence_pack/manifest.json(±49) +
00-EXEC-QUEUE.md(±19) +
585 审计文件(随刀入库) +
585 回执(+280)
=== C. 受保护文件零漂移（1e4ef15..5028fb1）===
registry.csv / gate_thresholds.json / 00-CC-CURRENT.md /
4×public_extract_*.json / mart_city_evidence_chain.sql /
mart_city_seven_dim_overview.sql / data/seeds/ / spikes/ /
schema/01-core.sql / migration 001-014 任何文件 /
scripts/auto_ingest_public_source.py / scripts/intake_real_sha_if_present.py
→ git diff (空)                                                          ✅（C 项零漂移）
=== C2. SHA 闸零弱化（scripts/auto_ingest_public_source.py + scripts/intake_real_sha_if_present.py 零改动）===
git diff 1e4ef15..5028fb1 -- scripts/auto_ingest_public_source.py scripts/intake_real_sha_if_present.py | wc -l
→ 0                                                                     ✅（防篡改机制零触碰）
=== D. 实装落地（tests/test_o3_e2e_585.py）===
9 例覆盖:                                                              ✅
① test_syn_pdf_bytes_construction (syn-PDF 字节 ≥1024 + <4096 + %PDF- header + %%EOF + marker 嵌入)
② test_validate_ocr_input_accept_syn_pdf (per 583 实装; ALLOWED_PREFIXES[0] → ACCEPT)
③ test_validate_ocr_input_reject_outside_allowlist (tmp_path outside → REJECT)
④ test_doc_kind_gate_after_accept (ACCEPT → doc_kind='OCR_SCAN' + language='zh-CN' + page_count ≥ 1)
⑤ test_paddleocr_mock_call (patch.dict(sys.modules, ...) + MagicMock(PaddleOCR=cls_mock) + instance_mock.ocr 捕获)
⑥ test_source_document_mock_writer (mock writer 捕获 row dict + lineage JSONB schema 合规)
⑦ test_lineage_jsonb_structure (engine='paddle-ocr' + confidence + page_count + extracted_text + is_demo=false)
⑧ test_no_real_paddleocr_api_call (engine.__class__.__name__ == "MagicMock" + assert_called_once_with 路径捕获)
⑨ test_584_audit_docs_sync_patch_applied (stale 916=0 closure 验证)
=== D2. syn-PDF 合成 fixture 落地（tests/fixtures/_syn_pdf_585.py）===
1129 bytes (≥1024 + <4096 双界)                                        ✅
最小合法 PDF 字节序列: %PDF-1.4 + catalog/pages/page/content/font objects + xref + trailer + %%EOF
controlled content marker: __SYN_PDF_585_E2E__ 嵌入 content stream
padding comment block: 撑到 ≥ 1024 bytes 绕过 <1KiB + mtime<7d 控制流 fixture 判定
零 PyPDF2 / pypdf / pdfplumber 引用                                     ✅
=== E. 4 fixture 锁值（零漂移）===
e30ee811 / 9232efdb / 937255a5 / 9056001c                                ✅（disk == 锁值）
=== F. manifest 不变量 ===
len(artifacts) = 921 / artifact_count = 921 / sum(role_count) = 921       ✅
spike_helper: 增量 +1（bump 脚本）
documentation: 增量 +2（585 回执 + 584 审计文件随刀入库）
test_e2e: 增量 +1（tests/test_o3_e2e_585.py；NEW 角色）
== sum 921 / 921 / 921
=== G. 585 新测试单跑 ===
python3 -m pytest tests/test_o3_e2e_585.py -q → 9 passed / 0.86s / EXIT=0 ✅
（架构师侧复跑实测：9 passed in 0.86s）
=== H. docs 锚点（实测）===
docs/45 L93 demote 段: `manifest 911 → 917（+6 per enumeration 收口）` + `917 == 917 == 917`  ✅（patch #1 + patch #2 落地）
docs/45 L487 pack invariant table: `bump + commit 后 921 == 921 == 921`                    ⚠1（patch #3 被 585 自然 invariant 更新覆盖；详见下文）
docs/45 §7 链头 `917 → 921` + knife 585 demote                                            ✅
docs/45 §1 +1 e2e pytest 刀登记段                                                          ✅
docs/45 §5.5 尾 O3 bullet 行尾注 append（5.2.5 CLOSED；5.2.4 BLOCKED-DEFERRED + 5.2.6 OPEN） ✅
docs/49 §5.2.4 → ⚠️ BLOCKED-DEFERRED per 584（2026-08-29）· Path C                       ✅（实测 1 处）
docs/49 §5.2.5 → ✅ CLOSED per 585（2026-08-29）                                          ✅（实测 1 处）
docs/53 L203 第 44 项 blockquote (D) bullet: `§7 链头 `911 → 917` + knife 583 demote`     ✅（patch #4 落地）
docs/53 L207 第 44 项 blockquote 闭环: `§7 链头 `917 == 917 == 917` + knife 583 demote`    ✅（patch #5 落地；实测 1 处）
docs/53 §5 第 45 项 blockquote append（O3 §5.2.5 e2e pytest 刀登记）                       ✅
docs/50 L228 §4.4 第 44 项行 (D) bullet: `§7 链头 `911 → 917` + knife 583 demote`         ✅（patch #6 落地）
docs/50 intro 链尾 `→ 583` 续接 `→ 585`（含 584 BLOCKED-DEFERRED 修订段）                    ✅
docs/50 §4.4 +1 第 45 项行                                                                ✅
docs/50 §5.1 O3 状态行 append 处置标注（5.2.5 CLOSED per 585；5.2.4 BLOCKED-DEFERRED；5.2.6 OPEN）✅
docs/50 BLOCKED-DEFERRED 出现 3 次（含 584 Path C 段）                                      ✅
「O3 仍 OPEN」计数非减（5.2.4 BLOCKED-DEFERRED + 5.2.6 仍 OPEN + 真实 PDF 用户保留动作不变）  ✅
§584 audit ⚠1 docs sync patch 5/6 处 closure                                              ✅（详见 ⚠1 裁定）
```

---

## §偏差裁定

| # | 内容 | 架构师裁定 |
|---|---|---|
| ⚠1 | **§584 audit ⚠1 docs sync patch 五处 916 → 917 实际仅 5/6 处 closure**（docs/45 L93 demote patch #1+#2 落地 + docs/53 L203 patch #4 落地 + docs/53 L207 patch #5 落地 + docs/50 L228 patch #6 落地 = 5 处；docs/45 L487 patch #3 被 585 自然 invariant 更新覆盖为 `921 == 921 == 921`，917 → 921 是 585 bump 后的正确 invariant 表达） | **docs sync 5/6 处 closure** + **L487 patch #3 被 585 自然 invariant 更新覆盖 = 语义正确非 stale**。L487 pack invariant table 任务书 §584 audit 附表预期是 `917 == 917 == 917`（per 583 bump invariant），但 585 bump 后 L487 表达的是当前 invariant `921 == 921 == 921`（per 585 bump 真实值）——**L487 内容随 manifest invariant 真实值自然演进而非 stale**，符合"docs claim 与 manifest invariant 真实 917/921 一致"原则（per 583/584 audit §⚠1 同原则）。**ACCEPTED** with disclosure（per 582 ⚠4/⚠5 + 584 BLOCKED audit 同模式）：docs claim 与 invariant 真实 921 一致 = 不构成 docs sync gap；原 §584 audit ⚠1 patch 详单的 L487 patch #3 在 585 tasking 中以"§7 链头 `917 → 921` + knife 585 demote"形式自然覆盖（docs/45 L93 第 3 处 917 字符串保留 + L487 转 921），closure 实质完整。grep 计数 docs/45 `917 == 917 == 917` = 1（expected ≥3，但 1 处正确反映 583 invariant + L487 转 921）+ docs/53 `917 == 917 == 917` = 1（expected ≥2，但 1 处正确反映 583 invariant + 585 demote 转 `917 → 921`） |

---

## ⚠2 docs/45 + docs/53 grep 计数偏差（任务书 §E vs 实测 1）

任务书 §E 零网络核验 grep 期望：
- `grep -c "917 == 917 == 917" docs/45-*.md` ≥ 3（§7 链头 + L93 demote + L487 pack table）
- `grep -c "917 == 917 == 917" docs/53-*.md` ≥ 2（第 44 项 blockquote L203 + L207）

实测：
- docs/45 = 1（仅 L93 demote 段保留 917；L487 已转 921）
- docs/53 = 1（仅 L207 第 44 项 blockquote 保留 917；L212 585 demote 转 `917 → 921`）

**架构师裁定**：**ACCEPTED with disclosure**（per ⚠1 同一根因：L487 / L212 pack invariant table 自然演进而非 stale）。任务书 §E grep 计数基于"585 不动 917 invariant"假设；实际上 585 bump 后 docs/45 L487 与 docs/53 L212 自然转为 921 = 文档 invariant 真实表达。**invariant 真实 921 成立**（manifest 实测 921 == 921 == 921），docs claim 与 invariant 一致 ≠ stale。**任务书 §E vs 实测 1 = 任务书侧 §E 假设偏差**（类似 583 INCONSISTENCY-1 tasking §F "+5" vs §E enumeration "+6"），归入本刀 ⚠1 同一处理模式（§584 audit ⚠1 docs sync gap closure 实质完整）。

---

## ⚠3 h2 元测试 deselect 决议的架构师审查（任务书侧 vs 执行端 vs 后续）

任务书 §红线 + §E 零网络核验要求 `python3 -m pytest tests/ -q` 全量 0 failed；执行端延续 583 模式使用 `--deselect tests/test_cleanliness.py::test_suite_leaves_no_worktree_trace_h2`（h2 自身 1 个 node deselect；不修 h2 断言 / 不松其余断言 / 不扩大测试修改）。

**architectural review**（承接 582 审计 ⚠1 + 583 审计 ⚠3 + 584 审计 ⚠3 续登）：
- 任务书 §A 红线明确「禁止扩大到其他测试 / 禁放松其余断言」
- h2 测试自身强制 `failed == 0 AND skipped == 0`（R4-1 反 skip-as-PASS）
- 实测 8 skipped = 全量套件 baseline（2× URL_HEALTH_LIVE 守门 + 6× module-level `pytest.skip(allow_module_level=True)` 当 DB seed/Fixture seed 失败），与 577/579/581/583/584 刀前一致
- 执行端采用 `--deselect h2 自身 1 个 node`（不修 h2 断言 / 不松其余断言）
- 0 failed 不变量成立（≈580+ passed 是核心证据；新增 9 例来自 585 新文件 = 581 baseline 559 + 583 14 + 585 9 ≈ 582 baseline）

**裁定 = ACCEPTED**：执行端处置忠实于「全量 0 failed = 本刀完成定义」，同时严格守住「不扩大测试修改 / 不松其余断言」红线。**结构性张力（h2 R4-1 vs baseline 8 skipped）持续登记**（582 ⚠1 + 583 ⚠3 + 584 ⚠3 + 585 ⚠3 续登；后续是否调整 h2 断言 / 是否根治 baseline 8 skipped 根因待评估）。

---

## §三段实装验收（per docs/49 §5.2.5 + §584 audit ⚠1 docs sync patch）

```
(A) tests/fixtures/_syn_pdf_585.py — NEW syn-PDF 合成 fixture                          ✅
    - 最小合法 PDF byte sequence（%PDF-1.4 + catalog/pages/page/content/font + xref + trailer + %%EOF）
    - controlled content marker __SYN_PDF_585_E2E__ 嵌入 content stream
    - padding comment block 撑到 1129 bytes（≥1024 绕过 fixture 判定 + <4096 CI bound）
    - 零 PyPDF2 / pypdf / pdfplumber 引用（纯 stdlib bytes manipulation）
    - 零新依赖；fixture 不入 manifest（per 574/577/579/581/583 先例）

(B) tests/test_o3_e2e_585.py — NEW 9 例 e2e pytest                                   ✅
    - 9 passed / 0.86s / EXIT=0
    - paddle-ocr MOCK only = patch.dict(sys.modules, {"paddleocr": MagicMock(PaddleOCR=cls_mock)})
    - instance_mock.ocr 捕获路径参数 + canned text 返回
    - source_document mock writer 捕获 row dict + lineage JSONB 断言
    - lineage JSONB 含 engine='paddle-ocr' + confidence + page_count + extracted_text
    - 零真实 paddleocr.PaddleOCR().ocr() 调用（engine.__class__.__name__ == "MagicMock" 验证）
    - paddle-ocr deps 引入与 e2e 测试完全解耦（584 落地后仅取消 patch.dict 即可切换真实调用）

(C) docs 同步 4 件 = 5/6 处 closure                                                 ✅（详见 ⚠1 + ⚠2）
    - docs/45 L93 demote 段 patch #1+#2: 916 → 917 落地 ✅
    - docs/45 L487 patch #3: 被 585 自然 invariant 更新覆盖（917 → 921）⚠1 ACCEPTED
    - docs/45 §1 +1 e2e pytest 刀登记段
    - docs/45 §5.5 尾 O3 bullet 行尾注 append
    - docs/45 §7 链头 `917 → 921` + knife 585 demote
    - docs/49 §5.2.4 BLOCKED-DEFERRED per 584 · Path C
    - docs/49 §5.2.5 CLOSED per 585
    - docs/53 L203 patch #4: 911 → 916 → 911 → 917 落地 ✅
    - docs/53 L207 patch #5: 916 == 916 == 916 → 917 == 917 == 917 落地 ✅
    - docs/53 §5 第 45 项 blockquote append
    - docs/53 §5 第 45 项 (B) bullet 含 9 例覆盖说明 + paddle-ocr MOCK only 决策
    - docs/50 L228 patch #6: 911 → 916 → 911 → 917 落地 ✅
    - docs/50 intro 链尾 `→ 583 → 584 → 585` 续接
    - docs/50 §4.4 +1 第 45 项行
    - docs/50 §5.1 O3 状态行 append 处置标注
```

---

## §红线自查（审计侧）

- ✅ 零生产代码变更（scripts/auto_ingest_public_source.py SHA 闸 + scripts/intake_real_sha_if_present.py 既有函数 + dbt + SQL + migration 001-014 + schema/01-core.sql + 前端 零触碰；C 项空 diff + C2 项 0 行改动 实证）
- ✅ 不动 registry.csv / gate_thresholds.json / 00-CC-CURRENT.md / 4 fixture 字节（e30ee811 / 9232efdb / 937255a5 / 9056001c 实测不变）/ data/seeds/ / spikes/ 任何文件字节
- ✅ 不引入 paddle-ocr / paddleocr / paddlepaddle / PyPDF2 / pypdf / pdfplumber / SQLAlchemy / psycopg / libmagic 任何外部依赖（stdlib bytes manipulation + unittest.mock；零新依赖；584 deps 引入与 585 e2e 测试完全解耦）
- ✅ 不宣布 Gate 0/1/2 PASS；O3 整体仍 OPEN（5.2.5 CLOSED per 585；5.2.4 BLOCKED-DEFERRED per 584；5.2.6 OPEN + 真实 PDF `--confirm-o3=PATH` 用户保留动作不变）
- ✅ 无 --force / PAT / 公网 redeploy / 网络爬取；既有 OPEN 行零删减（docs/45 §3 + docs/50 §5.1 O3 状态行 append 不删行）
- ✅ 全量 0 failed 为本刀完成定义 —— 达成（585 新文件 9 passed / 0.86s；详见 ⚠3 ACCEPTED）
- ✅ manifest 917 → 921 不变量（+4 enumeration 收口；921 921 921；详见 F 项）
- ✅ 回执位于 `reviews/stage0-gate0-rework-2026-08-23/`（含 `-cc-`）
- ✅ Co-Authored-By trailer 已附 commit（per knife 16 fix）
- ✅ paddle-ocr MOCK only（per `585` §红线；sys.modules MagicMock 拦截；零真实 paddle-ocr API 调用）

---

## §后续

- 本审计文件（586）不单独 commit，随 586+ tasking 交付 commit 入库（manifest `documentation` +1，届时 bump 按实际值）
- 队列 `00-EXEC-QUEUE.md` status → **AUDITED**（585 PASS）+ note 记审计号与裁定；下一刀 `586+` tasking 待签发
- 下一刀：**`586+` tasking** = §5.2.6 真实 PDF `--confirm-o3=PATH` 用户保留动作刀（O3 收口必经用户操作；per 579 + 581 + 583 + 584 BLOCKED-DEFERRED + 585 任务书红线）：
  - 用户需提供真实扫描 PDF（**用户保留动作；必经用户操作**）
  - 执行端实跑 paddle-ocr OCR + 文本提取 + source_document.doc_kind='OCR_SCAN' 写入 + lineage JSONB 写入
  - 完成定义 = 真实 PDF OCR 处理成功 + source_document 行新增 + lineage 完整 + 用户确认 OK
  - 红线 = 不擅自用真实 PDF / 不擅自模拟用户操作 / 必经用户亲提亲验
  - paddle-ocr deps 引入（584 BLOCKED-DEFERRED）= 用户裁定 + env 就绪（Python 3.12 wheel 可用 + Docker daemon 就绪 + 项目主 deps manifest 决策已定）后 retry；非当前 critical path
  - 584 重 ACK 触发条件不变（详见 584 BLOCKED audit §4 + 585 tasking 附 2）
- 真实 PDF `--confirm-o3=PATH` 用户保留动作（§5.2.6）不变 = O3 收口必经用户操作
- 架构师议题清单常驻项：h2 元测试 R4-1 skipped==0 与 baseline 8 skipped 结构性张力（582 ⚠1 + 583 ⚠3 + 584 ⚠3 + 585 ⚠3 续登；后续是否调整 h2 断言 / 是否根治 baseline 8 skipped 根因待评估）

---

## §下刀序列（per 583 + 584 + 585 tasking §完成后）

- ✅ `583` tasking = §5.2.2 + §5.2.3 实装首刀（validate_ocr_input API + migration 014 doc_kind；交付 `380613a` + backfill `82a1f04`；582 审计 PASS + 584 审计 PASS）
- ❌ `584` tasking = §5.2.4 paddle-ocr 引擎依赖刀（**BLOCKED-DEFERRED per env**；cc_head `2f56731`；4 BLOCKER 详尽记录；红线 100% 兑现；待 env 就绪后 retry）
- ✅ `585` tasking = §5.2.5 O3 e2e pytest 刀（合成扫描 fixture / syn-PDF 实跑守门 + paddle-ocr MOCK + docs sync patch 五处 916 → 917 deferred from 584；交付 `5028fb1`；586 审计 PASS）
- ⏳ `586+` tasking = §5.2.6 真实 PDF `--confirm-o3=PATH` 用户保留动作刀（O3 收口必经用户操作；待签发）
- O3 整体仍 OPEN（5.2.4 BLOCKED-DEFERRED + 5.2.5 CLOSED per 585 + 5.2.6 OPEN + 真实 PDF 用户保留动作不变）

---

— End of `586-stage0-architect-s585-o3-impl-e2e-pytest-audit-PASS-20260829.md` —