# 00-EXEC-QUEUE — 架构师 ↔ 执行端 交接队列

> **rev 63 · 2026-09-01。**  
> 热记忆：`docs/00-COMPASS.md`。轮询：`00-DUAL-POLL-PROTOCOL`。  
> **禁止宣布 Gate / O1 / M2 PASS。**

## §META

- rev: 65
- updated: 2026-09-01
- ruling: 639 DELIVERED → 640 M4.3 tasking **OPEN** → 等执行落地

## §CURRENT

- status: **640 tasking OPEN · 等 CC 落地**
- cc_head: `f57712f` (638 tasking) + `f1fdad5` (638 delivery) + `4123fcb` (638 cc_head) + `ee86977` (638 receipt) + `c3968ec` (639 tasking) + `f70ac95` (639 EXEC-QUEUE) + `1fca08e` (639 delivery) + `37aa148` (639 cc_head) + `11778db` (639 receipt)
- last_audit: `634-stage0-cursor-s633-m2-b-audit-PASS-20260831.md`
- tasking: `640-stage0-architect-m4-3-policy-demo-tasking-20260901.md`
- last_delivery: `639-stage0-cc-m4-2-renmian-demo-receipt-20260901.md`
- m4_decision: 640 = M4.3 政策项目 demo (6 表 × 3 demo each, lineage JSONB sentinel is_demo='true' 隔离, demo SHA 0…02 与 639 SHA 0…01 区分;沿用 docs/33 §3.2 sentinel 不新写 016 migration)

## §NOW

CC 落地 640-A (政策 probe + seed SQL + docs/60 + EXEC-QUEUE rev65) + 640-B (≥6 用例) + 640-C (回执 + 双推)。

## §CHAIN_TAIL

| 刀 | 状态 | 一句话 |
|---|---|---|
| 631 | AUDITED | M2-a |
| 633 | **AUDITED** | M2-b 5/31；634 PASS |
| 635 | **AUDITED** | M2-c+d+e：31/31 ≥ 20/31 + QUARANTINED-WEAK 跨源核对 + q1 研究页 |
| 636 | **AUDITED** | M2-f：文档收口 + 2001-onwards probe（适用 cell 1541: REACHABLE 0 / PARTIAL 770 / BLOCKED 771） |
| 637 | **DELIVERED** | M3 启动审查：架构师推荐路径 C（维持现状 + 转向 M4-M5）；详见 docs/57 |
| 638 | **DELIVERED** | M4.1 人物表 schema 收口 + 政府工作报告/任免公告可达性 probe (23/32 REACHABLE)；WAF 假设修正 |
| 639 | **DELIVERED** | M4.2 任免数据 demo: 二次 probe (REACHABLE 6 试点省 + PARTIAL 8 + BLOCKED 15) + 5 demo is_demo=true 隔离 + docs/59 |
| 640 | **tasking OPEN** | M4.3 政策项目 demo (6 表 × 3 demo each, lineage JSONB sentinel is_demo='true' 隔离, demo SHA 0…02 区分) + 二次 probe (6 REACHABLE 试点省政策承载路径 + ccdi/国务院 政策栏目) |

## §ACK

- 2026-09-01 / 用户 / 接收 640 = M4.3 政策项目 demo，签 640 tasking
- 2026-09-01 / CC / 639 DELIVERED — `reviews/stage0-gate0-rework-2026-08-23/639-stage0-cc-m4-2-renmian-demo-receipt-20260901.md`；64/64 pytest green。
- 2026-09-01 / 用户 / 接收 639 scope（ccdi 公告列表 + 23 试点省 + ≤5 条 demo）
- 2026-09-01 / 用户 / 接收 638 → 进入 639 (M4.2)
- 2026-09-01 / CC / 638 DELIVERED — `reviews/stage0-gate0-rework-2026-08-23/638-stage0-cc-m4-1-people-schema-gov-report-probe-receipt-20260901.md`；57/57 pytest green。
- 2026-09-01 / 用户 / 接收 637 路径 C, 进入 638
- 2026-09-01 / CC / 637 DELIVERED — `reviews/stage0-gate0-rework-2026-08-23/637-stage0-cc-m3-launch-conditions-review-receipt-20260901.md`；架构师推荐路径 C。
- 2026-09-01 / CC / 636 DELIVERED — `reviews/stage0-gate0-rework-2026-08-23/636-stage0-cc-m2-f-docs-closure-backfill-feasibility-receipt-20260901.md`；40/40 pytest green。
- 2026-08-31 / CC / 635 DELIVERED — `reviews/stage0-gate0-rework-2026-08-23/635-stage0-cc-m2-cde-coverage-crosscheck-page-receipt-20260831.md`；32/32 pytest green。
- 2026-08-31 / 用户 / 审 633 并签大任务