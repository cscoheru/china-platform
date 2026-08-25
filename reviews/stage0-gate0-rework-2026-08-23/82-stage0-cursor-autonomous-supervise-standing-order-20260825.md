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
- **双向心跳升级见 `84`**：CC 必须自武装 while-POLL；Cursor 不依赖聊天唤醒 CC
- 唯一信道：`origin/main` 的 `queue_rev` / §NOW

## 禁止擅自停环

- Cursor **不得**因「怕打扰用户点 Run」而关掉 supervise loop
- 审批弹窗由用户在 **Agents → Approvals & Execution → Run Everything**（或 allowlist）一次解决
- 仅用户明确喊停 / Stage 1 收口 / §BLOCKED 才停环

## Cursor 仍不做

- ❌ 业务代码 / schema / tests / `docs/18+` 正文
- ❌ 替用户裁定 §BLOCKED

## 停止条件

- Stage 1 队列收口（S1.12 实现收口或用户喊停）
- 或用户取消本站立令

— End —（补丁：与 `84` 联读；2026-08-25 禁擅自停环）
