# Cursor 自主推进计划 — 2026-08-28 下午

> 用户离席裁定：Cursor 自主推进 **26X→O1** 序列（合刀 **C**）；CC 卡住则调整方案唤醒；**不宣布 Gate/O1 PASS**。

## 已完成

| 刀 | 状态 |
|---|---|
| 566 | 26X kickoff — audit 567 PASS |
| 568 | 26X build — audit 569 PASS |
| 570 | O1 kickoff — **EXECUTE_NOW** |

## 待执行队列（Cursor 自主下发）

| 序 | 刀 | 主题 | 触发 |
|---|---|---|---|
| 1 | 570 | O1 kickoff + mart SHA 下一轴登记 | 进行中 |
| 2 | 571 | audit 570 PASS | 570 回执到 |
| 3 | 572 | mart 真 SHA 入仓 impl 合刀（dbt mart 占位→`a7e4029d…` 首行；pytest 守门） | 571 后 |
| 4 | 573 | audit 572 | 572 回执到 |
| 5 | 574 | O1 mart SHA 证据 docs 弧收口合刀（docs/53 38–39 + docs/45/50） | 573 后 |
| 6 | 575+ | 视 572 结果：person/tenure 真数据仍 defer；或 O1 收口条件文档化 | 链式 |

## CC 卡住唤醒策略

1. **Stale-token**：`queue_rev` bump + `cursor_ack` 对齐后再发 §NOW
2. **EXECUTE_NOW 超时**（>15min 无回执）：检查 origin/main 是否有 cc 提交；无则简化 tasking（docs-only 降级刀）重发
3. **build/pytest 失败**：tasking 允许偏差报告 + 拆 fix 刀，不 PASS 虚假回执
4. **AUTH/网络阻**：登记 BLOCKED 代号 + 文档节点，不绕过

## 红线（不变）

- 合刀单槽单回执
- O1 仍 OPEN 直至用户/Cursor 显式另裁
- 不动 4 fixture 字节
- 不 force push main
