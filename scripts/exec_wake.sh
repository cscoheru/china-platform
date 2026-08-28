#!/usr/bin/env bash
# exec_wake.sh — 架构师签发任务书/新要求后，唤醒执行终端
# 用法: bash scripts/exec_wake.sh ["自定义提示语"]   （默认提示语取自 00-EXEC-QUEUE.md §CURRENT）
# 通道（按序尝试，全部只读仓库文件、不 commit）:
#   1) tmux send-keys 直注执行端 pane（若存在且非本会话）
#   2) macOS 通知 + 声音（兜底，提示用户切到执行终端说"跟单"）
set -uo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
QUEUE="$REPO_ROOT/reviews/stage0-gate0-rework-2026-08-23/00-EXEC-QUEUE.md"
DEFAULT_MSG="EXEC-PULSE 触发：读 00-EXEC-QUEUE.md §CURRENT，PENDING 则 ACK 并执行"
MSG="${1:-$DEFAULT_MSG}"

# 1) tmux 直注（本机当前未装 tmux；保留分支以备将来）
if command -v tmux >/dev/null 2>&1 && tmux info >/dev/null 2>&1; then
  OWN="${TMUX_PANE:-}"
  HIT=0
  while IFS= read -r pane; do
    [ -z "$pane" ] && continue
    [ "$pane" = "$OWN" ] && continue   # 永不注入本会话
    # 只注入跑着 claude 的 pane
    cmd=$(tmux display-message -p -t "$pane" '#{pane_current_command}' 2>/dev/null || true)
    case "$cmd" in
      claude|node)
        tmux send-keys -t "$pane" -l "$MSG"
        tmux send-keys -t "$pane" Enter
        echo "WAKE: tmux 注入 → $pane ($cmd)"
        HIT=1
        ;;
    esac
  done < <(tmux list-panes -a -F '#{pane_id}' 2>/dev/null)
  [ "$HIT" = "1" ] && exit 0
fi

# 2) macOS 通知兜底
if command -v osascript >/dev/null 2>&1; then
  TASK=$(grep -m1 '^\- tasking:' "$QUEUE" 2>/dev/null | sed 's/.*\///; s/`.//g; s/`//g' || echo "见队列")
  osascript -e "display notification \"新任务：${TASK:-见队列}\" with title \"架构师已下发（china-platform）\" subtitle \"$MSG\" sound name \"Glass\"" \
    && echo "WAKE: macOS 通知已发（切到执行终端说：跟单）" \
    || echo "WAKE: 通知失败 — 请手动切到执行终端说：跟单"
else
  echo "WAKE: 无可用通道 — 请手动切到执行终端说：跟单"
fi
