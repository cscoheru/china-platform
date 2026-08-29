# 00-EXEC-QUEUE — 架构师 ↔ 执行端 交接队列（新治理模型 · 唯一状态源）

> Cursor 已退役；本文件取代 `00-CC-CURRENT.md` 的调度职能（后者冻结于 rev 320，勿读勿写）。
> 唤醒链路：架构师写本文件 + 跑 `scripts/exec_wake.sh`（macOS 通知）→ 执行端 session 内 EXEC-PULSE 自检（或用户粘贴一句"跟单"）。
> 本文件为治理工具，随 `577` 交付 commit 入库（manifest `documentation`）；此后每刀 bump SHA REFRESH（不增计数）。

## §META

- rev: 4
- updated: 2026-08-29
- architect: CC 架构师终端（本仓库唯一任务书/审计签发方；不写实现、不 commit）
- executor: CC 执行终端（本仓库目录内运行；按任务书执行、自验、回执、commit、双推）
- ruling: 用户（O1 / O3 / Gate 2 / 抽查）；**常设授权（2026-08-28 夜起生效）：需用户裁定项一律按架构师推荐自动执行**；例外 = 必须用户亲自操作项（注册/登录/付费/UI 人工验收/提供真实文件如 O3 的 `--confirm-o3=PATH` PDF）；仓库常备红线不因授权失效（不宣布 Gate PASS、不 --force、不公网 redeploy 等仍按红线）

## §CURRENT

- tasking: `reviews/stage0-gate0-rework-2026-08-23/583-stage2-o3-impl-validate-api-doc-kind-tasking-20260828.md`
- status: **DELIVERED**             <!-- PENDING → ACK → DELIVERED → AUDITED；只改本行 -->
- issued: 2026-08-29
- note: **O3 实装首刀**（per docs/49 §2.3 + §5.2.2 + §5.2.3；引擎 paddle-ocr per 2026-08-28 裁定 / §5.2.1 已关闭）= (A) `validate_ocr_input(path: Path) -> Literal["ACCEPT", "REJECT_OUTSIDE_ALLOWLIST", "REJECT_CONTROL_FLOW_FIXTURE", "REJECT_MIME"]` API 实装（per docs/49 §2.3 形态；本刀采用 stdlib `mimetypes` 零新依赖；实际常量名 = `ALLOWED_PREFIXES` + `SEED_ARCHIVES` + `is_control_flow_fixture()` 公开 wrapper）+ (B) `source_document.doc_kind='OCR_SCAN'` schema migration **014**（NEW 迁移；红线仅锁 001–013；最小化 = 单列增量 + CHECK + index；既有语义映射列如 `uploader_id`/`created_at` 复用不新增）+ (C) 引擎接 paddle-ocr = §5.2.4 单独刀（本刀不引入 paddle-ocr 依赖）；**完成定义** = 全量 pytest 0 failed + migration 014 上线 + validate API 四态单测覆盖 + e2e 合成扫描 fixture 通过；**O3 收口保留** = 真实 PDF `--confirm-o3=PATH` 用户保留动作（5.2.6）；**前置 582 审计 PASS**：581 修复刀（继承 4 failed 三处断言口径修正 + 全量 0 failed + manifest 911）已审计 PASS（fd483d1 + 36aea26）；**583 交付** = 回执 `583-stage0-cc-o3-impl-validate-api-doc-kind-receipt-20260828.md`（manifest bump 911 → 917 / 14 例新测 PASS / 1.39s / INCONSISTENT-1 任务书 §F "+5" vs §E 枚举 "+6" 闭合以 enumeration 为准 917 per 013.log 独立文件双 ADD）→ 待架构师审计

## §DELIVERED（583 待审计）

- 2026-08-29 / CC-exec（Claude Code 执行终端，582 同 session） / 回执 `583-stage0-cc-o3-impl-validate-api-doc-kind-receipt-20260828.md`（manifest 911 → 917 / 14 例新测 PASS / INCONSISTENT-1 tasking §F "+5" vs §E enumeration "+6" 闭合以 enumeration 为准 917 / 双推 + cc_head backfill 待执行） → 待架构师审计

## §AUDITED（582 PASS）

- 2026-08-29T00:0x+08:00 / CC-arch（架构师审计终端） / 581 receipt PASS（`582-stage0-architect-s581-inherited-fix-audit-PASS-20260828`；9 证据段 A–I + ⚠4/⚠5 ACCEPTED with disclosure + ⚠6 四刀零 ⚠ 计数偏差复发；manifest 911 不变量成立；红线零违反）→ 583 签发（O3 实装首刀）

## §ACK

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
