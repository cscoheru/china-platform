# Agent bootstrap（CC / Claude Code 必读）

**每次会话第一条命令（强制）：**

```bash
git fetch origin && git pull --ff-only origin main
cat reviews/stage0-gate0-rework-2026-08-23/00-CC-CURRENT.md
```

然后执行 `00-CC-CURRENT.md` 的 **§NOW**。未完成 §NOW 前 **禁止 IDLE**，禁止问用户「下一步」。

- 任务书：`reviews/stage0-gate0-rework-2026-08-23/` 最新 Cursor 文件
- 轮询协议：`21-stage0-cc-proactive-poll-standing-order-20260824.md`
- 双推：`git push origin HEAD && git push github HEAD`

Cursor 协调；用户仅裁定 §BLOCKED 代号。
