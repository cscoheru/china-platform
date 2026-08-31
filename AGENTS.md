# Agent bootstrap（CC / Claude Code 必读）

**每次会话 / `/compact` 后第一条命令（强制）：**

```bash
git fetch origin && git pull --ff-only origin main
./scripts/dual_poll_status.sh --pull || ./scripts/cc_gate_watch.sh --pull
# 热记忆：只读罗盘（≤80 行）。禁止 cat 00-CC-CURRENT / docs/45 / docs/54 / docs/55 全文。
wc -l -c docs/00-COMPASS.md
test "$(wc -l < docs/00-COMPASS.md)" -le 80
cat docs/00-COMPASS.md
```

深读规则：只打开 `docs/00-COMPASS.md` §POINTERS 里**当前 NOW 需要的一个文件**。调度只 `sed -n '/^## §CURRENT/,/^## §CHAIN/p'` 读 `00-EXEC-QUEUE.md`。

协议全文：`reviews/stage0-gate0-rework-2026-08-23/00-DUAL-POLL-PROTOCOL-20260831.md`

然后：

- `CURSOR_ACTION=AUDIT_NOW` → **Cursor 审验**（CC 做 5m POLL）
- `CC_ACTION=EXECUTE_NOW` → **立即执行 §NOW**（禁止 IDLE）
- 否则：见下「交卷后 5m POLL」

### 交卷门闩（强制）

交付 = 回执已写 + **commit** + **双推成功**。  
**未 commit/push → 禁止轮询**（专心实现）。

### 交卷后 5m POLL（取代旧 180s）

```bash
# 仅在双推成功后进入
while true; do
  git fetch origin && git pull --ff-only origin main
  ./scripts/dual_poll_status.sh
  grep -q 'CC_ACTION=EXECUTE_NOW' <<<"$(./scripts/dual_poll_status.sh)" && break
  echo "CC_HEARTBEAT $(date -Iseconds) waiting audit/next"
  sleep 300
done
# → 读最新 *-audit-* + EXEC-QUEUE §NOW 任务书 → 执行 → push → 再进 while
```

### Cursor 30m 监管（本会话 loop）

见 `00-DUAL-POLL-PROTOCOL`：每 30 分钟 `dual_poll_status`；`AUDIT_NOW` 则审验+签发下一单。

双推：`git push origin HEAD && git push github HEAD`  
用户仅裁定 §BLOCKED / Gate / 有限通过。
