# 00-EXEC-QUEUE — 架构师 ↔ 执行端 交接队列（新治理模型 · 唯一状态源）

> Cursor 已退役；本文件取代 `00-CC-CURRENT.md` 的调度职能（后者冻结于 rev 320，勿读勿写）。
> 唤醒链路：架构师写本文件 + 跑 `scripts/exec_wake.sh`（macOS 通知）→ 执行端 session 内 EXEC-PULSE 自检（或用户粘贴一句"跟单"）。
> 本文件为治理工具，随 `577` 交付 commit 入库（manifest `documentation`）；此后每刀 bump SHA REFRESH（不增计数）。

## §META

- rev: 5
- updated: 2026-08-29
- architect: CC 架构师终端（本仓库唯一任务书/审计签发方；不写实现、不 commit）
- executor: CC 执行终端（本仓库目录内运行；按任务书执行、自验、回执、commit、双推）
- ruling: 用户（O1 / O3 / Gate 2 / 抽查）；**常设授权（2026-08-28 夜起生效）：需用户裁定项一律按架构师推荐自动执行**；例外 = 必须用户亲自操作项（注册/登录/付费/UI 人工验收/提供真实文件如 O3 的 `--confirm-o3=PATH` PDF）；仓库常备红线不因授权失效（不宣布 Gate PASS、不 --force、不公网 redeploy 等仍按红线）

## §CURRENT

- tasking: `reviews/stage0-gate0-rework-2026-08-23/586-stage0-architect-s585-o3-impl-e2e-pytest-audit-...md`（**待签发**；585 receipt 已 DELIVERED 等审计）
- status: **PENDING**                    <!-- PENDING → ACK → DELIVERED → AUDITED；只改本行 -->
- issued: 2026-08-29
- note: **O3 §5.2.5 e2e pytest 刀 架构师审计**（per `585-stage0-cc-o3-impl-e2e-pytest-tasking-20260829-receipt`；架构师治理模型第七刀审计）。审计要点 = (A) `tests/fixtures/_syn_pdf_585.py` syn-PDF 合成 fixture 满足 ≥ 1024 bytes 绕过 fixture 判定 + 零 PDF 解析库引用 + controlled content marker 嵌入 + (B) `tests/test_o3_e2e_585.py` 9 例 PASS / 0.86s + paddle-ocr MOCK only 与 deps 解耦 + (C) docs sync 4 件 5/6 处 closure（docs/45 五处 + docs/49 两处 + docs/53 两处 + docs/50 三处）+ (D) manifest bump +4 → 921 不变量成立；预期 = ACCEPTED（红线 100% 兑现 + 5/6 处 docs sync 落点验证 + §584 audit ⚠1 docs sync gap closure 完整 + paddle-ocr MOCK only 验证）；**前置 585 DELIVERED**（cc_head 待回填；585 bump #1 + bump #2 完成；单 commit 单回执合刀）

## §DELIVERED（584 BLOCKED）

- 2026-08-29 / CC-exec（Claude Code 执行终端，584 BLOCKED 交付） / 回执 `584-stage0-cc-paddle-ocr-deps-tasking-20260829-receipt.md`（4 BLOCKER：Python 3.14 无 paddlepaddle wheel + 项目零 baseline Dockerfile/requirements.txt + Docker daemon 不可用 + manifest 923 invariant 不可达；架构师修订路径 A/B/C 已附） → 架构师审计 Path C 采纳（584 BLOCKED-DEFERRED per env）

## §DELIVERED（585 PASS）

- 2026-08-29 / CC-exec（Claude Code 执行终端，585 e2e pytest 刀 交付） / 回执 `585-stage0-cc-o3-impl-e2e-pytest-tasking-20260829-receipt.md`（A `tests/fixtures/_syn_pdf_585.py` NEW syn-PDF 合成 fixture = 最小合法 PDF 字节序列 `%PDF-1.4` + catalog/pages/page/content stream/font objects + xref + trailer + `%%EOF` + controlled content marker `__SYN_PDF_585_E2E__` + padding comment 撑到 1129 bytes 绕过 `<1KiB + mtime<7d` 控制流 fixture 判定 + 零 PyPDF2/pypdf/pdfplumber 引用 + B `tests/test_o3_e2e_585.py` NEW **9 例 PASS / 0.86s** = ① syn-PDF bytes construction ② validate_ocr_input ACCEPT for syn-PDF in upload prefix ③ REJECT_OUTSIDE_ALLOWLIST for syn-PDF outside ④ doc_kind gate after ACCEPT → e2e pipeline `doc_kind='OCR_SCAN'` ⑤ paddle-ocr MOCK call（`patch.dict(sys.modules, {"paddleocr": MagicMock(PaddleOCR=cls_mock)})` + `instance_mock.ocr` 捕获路径参数）⑥ source_document mock writer 捕获 row dict + lineage JSONB ⑦ lineage JSONB structure 含 `engine='paddle-ocr'` + `confidence` + `page_count` + `extracted_text` ⑧ 零真实 paddle-ocr API 调用断言（`engine.__class__.__name__ == "MagicMock"` 验证 mock 实例非真实 PaddleOCR）⑨ §584 audit ⚠1 docs sync 落点验证（5/6 处 stale 916 = 0 + 917 ≥ 3）+ C docs 同步 4 件 = docs/45 五处（文首 +1 刷新行 / §1 +1 段 / §3 O3 status row append 处置标注 / §5.5 尾 O3 bullet 行尾注 append / §7 链头 `917 → 921` + knife 585 demote）+ docs/49 §5.2.4 → ⚠️ **BLOCKED-DEFERRED per 584（2026-08-29）· Path C** + §5.2.5 → ✅ **CLOSED per 585（2026-08-29）** + docs/53 §5 第 45 项 blockquote append + docs/50 intro 链尾 `→ 583` 续接 `→ 585`（含 584 BLOCKED-DEFERRED 修订段）+ §4.4 +1 第 45 项行 + §5.1 O3 状态行 append 处置标注（5.2.5 CLOSED per 585；5.2.4 BLOCKED-DEFERRED per 584；5.2.6 OPEN）+ D manifest bump **+4 → 917 → 921**（bump 脚本 + 585 回执 + 584 审计文件 + e2e 测试文件；枚举即权威；INVARIANT 921 == 921 == 921 ✓）；**核心证据** = 单文件 pytest **9 passed / 0 failed / 0.86s** + docs sync 5/6 处 closure 验证 test #⑨ PASS + manifest INVARIANT 921 == 921 == 921；**§584 audit ⚠1 docs sync patch 五处 916 → 917 closure 完整**；**前置 584 BLOCKED disposition ACCEPTED + Path C**（4 BLOCKER = Python 3.14 无 paddlepaddle wheel + 项目零 baseline Dockerfile + Docker daemon 不可用 + 主 deps manifest 缺失；584 重 ACK 触发条件 = 用户裁定 + env 就绪 + 主 deps manifest 决策已定）；**红线 100% 兑现**（paddle-ocr MOCK only / 零真实 PDF / 零触真实 DB / 零引入 cloud OCR / 零引入 GPU runtime / 不修改 migration 001-014 / 不修改 schema/01-core.sql / 不修改 scripts/ / 不修改 4 fixture 字节 / 不爬网 / 不写 dbt/mart/前端 / 不宣布 Gate PASS / 既有 OPEN 行零删减）；**O3 整体仍 OPEN**（5.2.4 BLOCKED-DEFERRED per 584 + 5.2.6 OPEN + 真实 PDF `--confirm-o3=PATH` 用户保留动作不变）；**登记→实装闭环 = 583 → 584 BLOCKED → 585**（585 既闭合 §5.2.5 e2e pytest 又 closure §584 audit ⚠1 docs sync gap）→ 585 审计待签发

## §AUDITED（584 BLOCKED disposition ACCEPTED · Path C）

- 2026-08-29 / CC-arch（架构师审计终端） / 584 BLOCKED receipt ACCEPTED（`585-stage0-architect-s584-o3-impl-paddle-ocr-deps-audit-BLOCKED-20260829`；A–F 证据段全达成 + 4 BLOCKER 详尽记录核验 + 红线 100% 兑现 ACCEPTED；架构师修订路径 Path A/B 拒绝 + Path C 采纳 = 584 BLOCKED-DEFERRED per env + 585 tasking 签发 §5.2.5 e2e pytest 刀 paddle-ocr MOCK only 与 deps 引入解耦；584 重 ACK 触发条件 = 用户裁定 + Python 3.12 wheel 可用 + Docker daemon 就绪 + 项目主 deps manifest 决策已定 任一缺失仍 BLOCKED；manifest 917 不变量保持（无 bump）；§584 audit ⚠1 docs sync patch 五处 916 → 917 deferred 至 585 闭合）→ **585 tasking 已签发 PENDING**

## §AUDITED（584 PASS）

- 2026-08-29 / CC-arch（架构师审计终端） / 583 receipt PASS（`584-stage0-architect-s583-o3-impl-validate-api-doc-kind-audit-PASS-20260829`；A–H 证据段全达成 + ⚠1 docs/45 §7 链头 916 vs actual 917 docs sync gap ACCEPTED with disclosure [不动 commit / 不动 manifest / 仅 docs 文案对齐 actual 917 — 入下刀 patch] + ⚠2 INCONSISTENT-1 enumeration 收口 917 ACCEPTED + ⚠3 h2 deselect 续登 ACCEPTED；manifest 917 不变量成立；红线零违反）→ 584 tasking 签发（O3 §5.2.4 paddle-ocr 引擎依赖刀）

## §AUDITED（582 PASS）

- 2026-08-29T00:0x+08:00 / CC-arch（架构师审计终端） / 581 receipt PASS（`582-stage0-architect-s581-inherited-fix-audit-PASS-20260828`；9 证据段 A–I + ⚠4/⚠5 ACCEPTED with disclosure + ⚠6 四刀零 ⚠ 计数偏差复发；manifest 911 不变量成立；红线零违反）→ 583 签发（O3 实装首刀）

## §ACK

- 2026-08-29 / CC-exec（Claude Code 执行终端，跟单触发「585」） / 开始执行 → 交付 `585-stage0-cc-o3-impl-e2e-pytest-tasking-20260829-receipt.md`（DELIVERED 段已落；待 586 架构师审计签发）
- 2026-08-29 / CC-exec（Claude Code 执行终端，跟单触发 / 跟单 584） / 开始执行 → 交付回执号待回填
- 2026-08-29T00:0x+08:00 / CC-exec（Claude Code 执行终端，跟单触发） / 开始执行 → 交付回执号待回填
- 2026-08-28T22:46+08:00 / CC-exec（Claude Code 执行终端，579 同 session） / 开始执行 → 交付 `fd483d1` + backfill `36aea26` → `582` 审计 PASS

## §ACK（579 刀存档）

- 2026-08-28T22:25+08:00 / CC-exec（Claude Code 执行终端，577 同 session） / 开始执行 → 交付 `6524155` + `81188dc` → `580` 审计 PASS

## §ACK（577 刀存档）

- 2026-08-28T21:30+08:00 / CC-exec（Claude Code 执行终端，574 同 session） / 开始执行 → 交付 `c8e2b9a` + `7c9668e` → `578` 审计 PASS

## §STATE 规则

| status | 含义 | 谁写 |
|---|---|---|
| PENDING | 任务书已签发，待执行端认领 | 架构师 |
| ACK | 执行端已认领开工 | 执行端（+§ACK 一行） |
| DELIVERED | 回执落盘 + 双推完成，待审计 | 执行端（回执号写进 note） |
| AUDITED | 架构师审计出档（PASS/FAIL 写 note） | 架构师 |
