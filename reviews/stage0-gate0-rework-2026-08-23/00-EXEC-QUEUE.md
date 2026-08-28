# 00-EXEC-QUEUE — 架构师 ↔ 执行端 交接队列（新治理模型 · 唯一状态源）

> Cursor 已退役；本文件取代 `00-CC-CURRENT.md` 的调度职能（后者冻结于 rev 320，勿读勿写）。
> 唤醒链路：架构师写本文件 + 跑 `scripts/exec_wake.sh`（macOS 通知）→ 执行端 session 内 EXEC-PULSE 自检（或用户粘贴一句"跟单"）。
> 本文件为治理工具，随 `577` 交付 commit 入库（manifest `documentation`）；此后每刀 bump SHA REFRESH（不增计数）。

## §META

- rev: 1
- updated: 2026-08-28
- architect: CC 架构师终端（本仓库唯一任务书/审计签发方；不写实现、不 commit）
- executor: CC 执行终端（本仓库目录内运行；按任务书执行、自验、回执、commit、双推）
- ruling: 用户（O1 / O3 / Gate 2 / 抽查）

## §CURRENT

- tasking: `reviews/stage0-gate0-rework-2026-08-23/577-stage2-o1-close-person-tenure-full-tasking-20260828.md`
- status: **DELIVERED**       <!-- PENDING → ACK → DELIVERED → AUDITED；只改本行 -->
- issued: 2026-08-28
- note: O1 裁定登记 + S2.1-full（需本地 DB，Phase 0 起库 55440）；manifest 889→903（含本文件 + exec_wake.sh，+14）→ 回执 `577-stage0-cc-o1-close-person-tenure-full-receipt-20260828`（A–H 合刀单 commit + 双推完成）；实际 NEW 15 项 per §A「按 bump 实际值」→ **904 == 904 == 904**（任务书 §F 标注 +14→903 与实列 15 项不符，回执文首 ⚠1 显著披露）

## §ACK

- 2026-08-28T21:30+08:00 / CC-exec（Claude Code 执行终端，574 同 session） / 开始执行

## §STATE 规则

| status | 含义 | 谁写 |
|---|---|---|
| PENDING | 任务书已签发，待执行端认领 | 架构师 |
| ACK | 执行端已认领开工 | 执行端（+§ACK 一行） |
| DELIVERED | 回执落盘 + 双推完成，待审计 | 执行端（回执号写进 note） |
| AUDITED | 架构师审计出档（PASS/FAIL 写 note） | 架构师 |
