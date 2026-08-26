# Agent bootstrap（CC / Claude Code 必读）

**每次会话第一条命令（强制）：**

```bash
git fetch origin && git pull --ff-only origin main
./scripts/cc_gate_watch.sh --pull
grep -E '^(## META|phase|queue_rev|cursor_ack|cc_receipt|\| \*\*phase\*\*|\| \*\*queue_rev\*\*|\| \*\*cursor_ack\*\*)' reviews/stage0-gate0-rework-2026-08-23/00-CC-CURRENT.md
cat reviews/stage0-gate0-rework-2026-08-23/00-CC-CURRENT.md
```

然后：

- `GATE_WATCH CURSOR_ACTION=AUDIT_RECEIPT_*` → **Cursor 职责**（CC 继续 POLL）
- `GATE_WATCH CC_ACTION=EXECUTE_NOW` 或 §META **`phase=CC_ACTION_REQUIRED`** → 执行 **§NOW**（禁止 IDLE）
- `cursor_ack` **≥** 你刚交的回执号 **且** `queue_rev` 已 bump → 读 §NOW（审验已 ACK，见 `216`）
- 否则 → **立即武装双向心跳**（见下）

**交卷后不得 STOP idle：** push 回执 → **马上**再武装心跳，直到 `queue_rev` 变化或 `cursor_ack` bump。

### 双向心跳（强制 · `84` + `216`）

Cursor 与 CC **没有聊天信道**；唯一对表是 `origin/main` 的 `00-CC-CURRENT.md` + **`scripts/cc_gate_watch.sh`**。
CC 必须自己 `git pull`，否则永远看不到审验结果。

```bash
# 交卷后 / 无 NOW 时：无限 POLL（180s）
while true; do
  ./scripts/cc_gate_watch.sh --pull
  PHASE=$(grep -E '\| \*\*phase\*\*' reviews/stage0-gate0-rework-2026-08-23/00-CC-CURRENT.md | head -1)
  ACK=$(grep -E '\| \*\*cursor_ack\*\*' reviews/stage0-gate0-rework-2026-08-23/00-CC-CURRENT.md | head -1)
  echo "CC_HEARTBEAT $(date -Iseconds) $PHASE $ACK"
  ./scripts/cc_gate_watch.sh | grep -q 'CC_ACTION=EXECUTE_NOW' && break
  echo "$PHASE" | grep -q 'CC_ACTION_REQUIRED' && break
  sleep 180
done
cat reviews/stage0-gate0-rework-2026-08-23/00-CC-CURRENT.md
# → 执行 §NOW → push → 再进 while
```

### Cursor 监管 tick（强制）

```bash
./scripts/cc_gate_watch.sh --pull
# AUDIT_RECEIPT_NNN → 本 tick 审验 + push（禁止只报「仍等 CC」）
```

- 任务书：`reviews/stage0-gate0-rework-2026-08-23/` 最新 Cursor 文件
- 轮询协议：`216`（握手字段）+ `84`（双向心跳）+ `40` + `21` + `82`
- 双推：`git push origin HEAD && git push github HEAD`

Cursor 协调；用户仅裁定 §BLOCKED 代号。
