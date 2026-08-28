# 00-EXEC-QUEUE — 架构师 ↔ 执行端 交接队列（新治理模型 · 唯一状态源）

> Cursor 已退役；本文件取代 `00-CC-CURRENT.md` 的调度职能（后者冻结于 rev 320，勿读勿写）。
> 唤醒链路：架构师写本文件 + 跑 `scripts/exec_wake.sh`（macOS 通知）→ 执行端 session 内 EXEC-PULSE 自检（或用户粘贴一句"跟单"）。
> 本文件为治理工具，随 `577` 交付 commit 入库（manifest `documentation`）；此后每刀 bump SHA REFRESH（不增计数）。

## §META

- rev: 2
- updated: 2026-08-28
- architect: CC 架构师终端（本仓库唯一任务书/审计签发方；不写实现、不 commit）
- executor: CC 执行终端（本仓库目录内运行；按任务书执行、自验、回执、commit、双推）
- ruling: 用户（O1 / O3 / Gate 2 / 抽查）；**常设授权（2026-08-28 夜起生效）：需用户裁定项一律按架构师推荐自动执行**；例外 = 必须用户亲自操作项（注册/登录/付费/UI 人工验收/提供真实文件如 O3 的 `--confirm-o3=PATH` PDF）；仓库常备红线不因授权失效（不宣布 Gate PASS、不 --force、不公网 redeploy 等仍按红线）

## §CURRENT

- tasking: `reviews/stage0-gate0-rework-2026-08-23/581-stage2-inherited-4failed-fix-suite-green-tasking-20260828.md`
- status: **DELIVERED**          <!-- PENDING → ACK → DELIVERED → AUDITED；只改本行 -->
- issued: 2026-08-28
- note: **继承 4 failed 修复刀 · 已交付** → 回执 `581-stage0-cc-inherited-4failed-fix-suite-green-receipt-20260828`（A–H 合刀单 commit + 双推完成；本刀三处断言口径修正 + data/ 白名单房规化四目录 + docs 三处同步）；manifest **911 == 911 == 911**（907 → 911，+4 per bump 实际值：bump + 回执 + 580 审计 + s52 测试 ADD）；核心证据 = 全量 pytest **559 passed / 8 skipped / 1 deselected / 0 failed / exit 0 / 4:35**（h2 元测试 deselected，详见回执 ⚠1）；O1 仍 OPEN；O3 仍 OPEN；不宣布 Gate PASS；SHA 闸零弱化 = 转测试预期非放行

## §ACK

- 2026-08-28T22:46+08:00 / CC-exec（Claude Code 执行终端，579 同 session） / 开始执行

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
