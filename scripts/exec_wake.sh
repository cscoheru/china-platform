#!/usr/bin/env bash
# exec_wake.sh — 架构师签发任务书/新要求后，唤醒执行终端
# 用法: bash scripts/exec_wake.sh ["自定义提示语"]   （默认提示语取自 00-EXEC-QUEUE.md §CURRENT）
# 通道（按序尝试，全部只读仓库文件、不 commit）:
#   1) tmux send-keys 直注执行端 pane（若存在且非本会话）
#   2) macOS 通知 + 声音（兜底，提示用户切到执行终端说"跟单"）
#   3) Sound alert (afplay /System/Library/Sounds/Glass.aiff)
#   4) Terminal / iTerm2 title flash via ANSI OSC 0/2 sequence
set -o pipefail

# 确保 UTF-8（emoji 🔔 在 C locale 下被截断）
export LANG="${LANG:-en_US.UTF-8}"
export LC_ALL="${LC_ALL:-en_US.UTF-8}"

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
QUEUE="$REPO_ROOT/reviews/stage0-gate0-rework-2026-08-23/00-EXEC-QUEUE.md"
DEFAULT_MSG="EXEC-PULSE 触发：读 00-EXEC-QUEUE.md §CURRENT，PENDING 则 ACK 并执行"
MSG="${1:-$DEFAULT_MSG}"

# 0) 解析任务书文件名（如 595-stage0-architect-s594-blocker-relief-dockerfile-deps-tasking-20260829.md）
TASK="见队列"
if [ -f "$QUEUE" ]; then
  TASK=$(grep -m1 '^\- tasking:' "$QUEUE" 2>/dev/null \
    | grep -oE '[0-9]+-[a-z0-9-]+-tasking-[0-9]+\.md' \
    | head -1 || echo "")
  TASK="${TASK:-见队列}"
fi
TITLE_MSG="🔔 EXEC-PULSE: $TASK"

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
  osascript -e "display notification \"新任务：$TASK\" with title \"架构师已下发（china-platform）\" subtitle \"$MSG\" sound name \"Glass\"" \
    && echo "WAKE: macOS 通知已发（切到执行终端说：跟单）" \
    || echo "WAKE: 通知失败 — 请手动切到执行终端说：跟单"
else
  echo "WAKE: 无可用通道 — 请手动切到执行终端说：跟单"
fi

# 3) Sound alert enhancement (per 595 tasking §4.2; macOS system sound)
if command -v afplay >/dev/null 2>&1; then
  afplay /System/Library/Sounds/Glass.aiff 2>/dev/null \
    && echo "WAKE: 声音提示 Glass.aiff 已播" \
    || echo "WAKE: afplay 失败（系统声音文件不存在？）"
fi

# 4) Terminal / iTerm2 title flash via ANSI OSC sequence (per 595 tasking §4.2)
# 序列: OSC 0/2 ; 改 window title + icon title; 还原在 3 秒后
# 先在父 shell 完整打印 echo（避免 subshell 干扰变量）
# 注: echo 内置对 🔔 多字节 emoji 处理异常；用 printf
printf 'WAKE: Terminal/iTerm2 标题已 flash → %s（3 秒后还原）\n' "$TITLE_MSG"
printf '\033]0;%s\007' "$TITLE_MSG" 2>/dev/null || true
printf '\033]2;%s\007' "$TITLE_MSG" 2>/dev/null || true
(
  sleep 3
  RESTORE_TITLE="china-platform"
  printf '\033]0;%s\007' "$RESTORE_TITLE" 2>/dev/null || true
  printf '\033]2;%s\007' "$RESTORE_TITLE" 2>/dev/null || true
) >/dev/null 2>&1 &