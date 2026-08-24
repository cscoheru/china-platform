# Agent bootstrap（CC / Claude Code 必读）

**每次会话第一条命令（强制）：**

```bash
git fetch origin && git pull --ff-only origin main
grep -E '^(## META|phase|queue_rev|\| \*\*phase\*\*)' reviews/stage0-gate0-rework-2026-08-23/00-CC-CURRENT.md
cat reviews/stage0-gate0-rework-2026-08-23/00-CC-CURRENT.md
```

然后：

- §META **`phase=CC_ACTION_REQUIRED`** → 执行 **§NOW**（禁止 IDLE，禁止问用户「下一步」）
- 否则 → **`40-stage0-cc-cursor-deadlock-fix-20260824.md` §POLL**（3 分钟 pull；禁止等 Cursor 聊天）

**交卷后不得 STOP idle：** push 回执 → §POLL 直到 `queue_rev` 变化。

- 任务书：`reviews/stage0-gate0-rework-2026-08-23/` 最新 Cursor 文件
- 轮询协议：`40`（主）+ `21-stage0-cc-proactive-poll-standing-order-20260824.md`
- 双推：`git push origin HEAD && git push github HEAD`

Cursor 协调；用户仅裁定 §BLOCKED 代号。
