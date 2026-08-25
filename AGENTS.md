# Agent bootstrap（CC / Claude Code 必读）

**每次会话第一条命令（强制）：**

```bash
git fetch origin && git pull --ff-only origin main
grep -E '^(## META|phase|queue_rev|\| \*\*phase\*\*|\| \*\*queue_rev\*\*)' reviews/stage0-gate0-rework-2026-08-23/00-CC-CURRENT.md
cat reviews/stage0-gate0-rework-2026-08-23/00-CC-CURRENT.md
```

然后：

- §META **`phase=CC_ACTION_REQUIRED`** → 执行 **§NOW**（禁止 IDLE，禁止问用户「下一步」）
- 否则 → **立即武装双向心跳**（见下）

**交卷后不得 STOP idle：** push 回执 → **马上**再武装心跳，直到 `queue_rev` 变化。

### 双向心跳（强制 · `84`）

Cursor 与 CC **没有聊天信道**；唯一对表是 `origin/main` 的 `00-CC-CURRENT.md`。
CC 必须自己 `git pull`，否则永远看不到审验结果。

```bash
# 交卷后 / 无 NOW 时：无限 POLL（180s），废除「1h 后停」
while true; do
  git fetch origin && git pull --ff-only origin main
  PHASE=$(grep -E '\| \*\*phase\*\*' reviews/stage0-gate0-rework-2026-08-23/00-CC-CURRENT.md | head -1)
  echo "CC_HEARTBEAT $(date -Iseconds) $PHASE"
  echo "$PHASE" | grep -q 'CC_ACTION_REQUIRED' && break
  sleep 180
done
cat reviews/stage0-gate0-rework-2026-08-23/00-CC-CURRENT.md
# → 执行 §NOW → push → 再进 while
```

- 任务书：`reviews/stage0-gate0-rework-2026-08-23/` 最新 Cursor 文件
- 轮询协议：`84`（双向心跳，主）+ `40` + `21` + `82`（Cursor 自治）
- 双推：`git push origin HEAD && git push github HEAD`

Cursor 协调；用户仅裁定 §BLOCKED 代号。
