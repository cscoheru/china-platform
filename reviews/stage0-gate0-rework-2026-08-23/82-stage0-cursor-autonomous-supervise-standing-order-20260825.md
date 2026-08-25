# Cursor 自治监管 — 站立令

- 编号：`82-stage0-cursor-autonomous-supervise-standing-order-20260825`
- 生效：2026-08-25（用户授权：两小时巡检制；非 §BLOCKED 不打扰）

## 授权范围

Cursor **自主**执行至 **Stage 1 任务链收口**（当前目标：S1.11 → S1.12 Gate 1 准备）：

1. `git pull` → 发现 CC 回执 / 新 commit → **立即审验**
2. PASS → 写 audit + 下一刀 tasking + 更新 `00-CC-CURRENT` + push origin
3. FAIL / 缺交付 → 写驳回 + 修正任务书；**不**等用户中转
4. **仅** `§BLOCKED`（需用户裁定代号）时在聊天提出

## 节奏

- 监管循环：**约 3 分钟** pull 一次（对齐 CC §POLL）
- CC 仍按 `40` §POLL；Cursor 不依赖聊天唤醒 CC

## Cursor 仍不做

- ❌ 业务代码 / schema / tests / `docs/18+` 正文
- ❌ 替用户裁定 §BLOCKED

## 停止条件

- Stage 1 队列收口（S1.12 任务书完成或用户喊停）
- 或用户取消本站立令

— End —
