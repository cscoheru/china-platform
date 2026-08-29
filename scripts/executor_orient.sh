#!/usr/bin/env bash
# executor_orient.sh — 执行端启动时一行自检
# 用法: bash scripts/executor_orient.sh
# 流程: pull (ff-only) → 解析 §CURRENT → 显示当前刀号 / status / 红线条数 → 提示下一步
# 注意: 不 commit / 不 push / 不改 00-CC-CURRENT.md（只读）
set -o pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$REPO_ROOT"
QUEUE="reviews/stage0-gate0-rework-2026-08-23/00-EXEC-QUEUE.md"
REVIEWS="reviews/stage0-gate0-rework-2026-08-23"

# 1) pull（可选 ff-only；若有 WIP 则提示但不强制）
git fetch origin 2>/dev/null || true
LOCAL=$(git rev-parse HEAD 2>/dev/null || echo "unknown")
ORIGIN=$(git rev-parse origin/main 2>/dev/null || echo "$LOCAL")
if [ "$LOCAL" != "$ORIGIN" ] && git merge-base --is-ancestor "$LOCAL" "$ORIGIN" 2>/dev/null; then
  git pull --ff-only origin main 2>/dev/null \
    && echo "ORIENT: 已 pull（was ${LOCAL:0:8}, now $(git rev-parse --short HEAD)）" \
    || echo "ORIENT: pull 失败（本地有 WIP?）— 继续读队列不阻断"
fi

# 2) 解析 §META
if [ ! -f "$QUEUE" ]; then
  echo "ORIENT: 队列文件不存在: $QUEUE"
  exit 1
fi

META_REV=$(grep -m1 '^- rev:' "$QUEUE" | sed 's/^- rev:[[:space:]]*//')
META_UPDATED=$(grep -m1 '^- updated:' "$QUEUE" | sed 's/^- updated:[[:space:]]*//')
META_TASKING=$(grep -m1 '^- tasking:' "$QUEUE" | sed 's/^- tasking:[[:space:]]*//')
META_STATUS_RAW=$(grep -m1 '^- status:' "$QUEUE" | sed 's/^- status:[[:space:]]*//' | sed 's/[[:space:]]*<!--.*//')

# 提取 tasking 文件路径（如有）
TASKING_FILE=$(echo "$META_TASKING" | grep -oE '[0-9]+-[a-z0-9-]+-tasking-[0-9]+\.md' | head -1)
TASKING_FILE="${TASKING_FILE:-见 00-EXEC-QUEUE.md}"

# 提取刀号
KNIFE_NUM=$(echo "$META_TASKING" | grep -oE '刀号?[[:space:]]*[0-9]+|PENDING[[:space:]]*[0-9]+|^[0-9]+' | grep -oE '[0-9]+' | head -1)
KNIFE_NUM="${KNIFE_NUM:-?}"

# 3) 红线条数（最近 audit 文件 §N 红线表行数）
LATEST_AUDIT=$(ls -t "$REVIEWS"/[0-9]*-stage0-architect-*-audit-*.md 2>/dev/null | head -1)
RED_LINES=0
LATEST_AUDIT_NAME="-"
if [ -n "$LATEST_AUDIT" ]; then
  LATEST_AUDIT_NAME=$(basename "$LATEST_AUDIT")
  # §N 红线表通常格式：| # | 红线 | 状态 |
  RED_LINES=$(awk '/^## §N\. 红线/{flag=1; next} flag && /^## §/{flag=0} flag && /^\| [0-9]+ \|/{c++} END{print c+0}' "$LATEST_AUDIT" 2>/dev/null)
  RED_LINES="${RED_LINES:-0}"
fi

# 4) §AUDITED 行数（审计收口链长度）
AUDITED_COUNT=$(grep -c '^## §AUDITED' "$QUEUE" 2>/dev/null || echo 0)

# 5) 输出
echo "================================================================"
echo "  ORIENT  $(date '+%Y-%m-%d %H:%M:%S %z')  rev=$META_REV  updated=$META_UPDATED"
echo "================================================================"
echo "  HEAD    local=$(git rev-parse --short HEAD 2>/dev/null)  origin=$(git rev-parse --short origin/main 2>/dev/null)"
echo "  KNIFE   $KNIFE_NUM"
echo "  STATUS  $META_STATUS_RAW"
echo "  TASKING $TASKING_FILE"
echo "  RED     $RED_LINES red lines (per $LATEST_AUDIT_NAME)"
echo "  AUDITS  $AUDITED_COUNT 项 §AUDITED 已收口"
echo "----------------------------------------------------------------"
case "$META_STATUS_RAW" in
  *"PENDING"*)
    echo "  → 执行端动作: ACK → 读任务书 → 实施 → 写回执 →"
    echo "    commit → git push origin HEAD → git push github HEAD →"
    echo "    bash scripts/exec_wake.sh"
    ;;
  *"ACK"*)
    echo "  → 你已 ACK；正在实施中。完成后按 PENDING 同流程交付"
    ;;
  *"DELIVERED"*)
    echo "  → 你已交付。等架构师 595 audit 签发；无需动作"
    echo "    （如需提前核对，回执应在 reviews/ 下最新数字文件）"
    ;;
  *"AUDITED"*)
    echo "  → 审计完成。等架构师下一刀任务书签发；无需动作"
    ;;
  *)
    echo "  → 状态字面未识别，请人工核对 00-EXEC-QUEUE.md §CURRENT"
    ;;
esac
echo "================================================================"
