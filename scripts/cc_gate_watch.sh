#!/usr/bin/env bash
# cc_gate_watch.sh — CC↔Cursor 对表探针（协议 84 + 216）
# 用法：./scripts/cc_gate_watch.sh [--pull]
# 输出：key=value 行；监管环 / bootstrap 解析 CURSOR_ACTION / CC_ACTION
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$REPO_ROOT"

CURRENT="reviews/stage0-gate0-rework-2026-08-23/00-CC-CURRENT.md"
REVIEWS="reviews/stage0-gate0-rework-2026-08-23"

DO_PULL=0
[[ "${1:-}" == "--pull" ]] && DO_PULL=1

git fetch origin 2>/dev/null || true

LOCAL_HEAD="$(git rev-parse HEAD)"
ORIGIN_HEAD="$(git rev-parse origin/main 2>/dev/null || echo "$LOCAL_HEAD")"
BEHIND=0
if [[ "$LOCAL_HEAD" != "$ORIGIN_HEAD" ]] && git merge-base --is-ancestor "$LOCAL_HEAD" "$ORIGIN_HEAD" 2>/dev/null; then
  BEHIND=1
fi

if [[ "$DO_PULL" -eq 1 && "$BEHIND" -eq 1 ]]; then
  git pull --ff-only origin main
  LOCAL_HEAD="$(git rev-parse HEAD)"
  BEHIND=0
fi

meta_field() {
  local key="$1"
  grep -E "\\| \\*\\*${key}\\*\\*" "$CURRENT" 2>/dev/null | head -1 \
    | sed -E 's/.*\| `([^`]+)`.*/\1/' \
    | sed -E 's/（.*//' | sed -E 's/；.*//' | tr -d ' ' || true
}

PHASE="$(meta_field phase)"
QUEUE_REV="$(meta_field queue_rev)"
CURSOR_ACK="$(meta_field cursor_ack)"
CC_RECEIPT_META="$(meta_field cc_receipt)"
ORIGIN_HEAD_META="$(meta_field origin_head)"
CC_HEAD_META="$(meta_field cc_head | cut -d'；' -f1)"

# 仅以 origin/main 已跟踪回执为准（忽略本地未 push 的 WIP）
LATEST_RECEIPT="$(
  git ls-tree -r --name-only origin/main -- "$REVIEWS" 2>/dev/null \
    | grep -E '/[0-9]+-.*-cc-.*-receipt-.*\.md$' \
    | sed -n 's|.*/\([0-9][0-9]*\)-.*|\1|p' | sort -n | tail -1
)"
LATEST_RECEIPT="${LATEST_RECEIPT:-0}"
CURSOR_ACK_N="${CURSOR_ACK:-0}"
CURSOR_ACK_N="${CURSOR_ACK_N//[^0-9]/}"
CURSOR_ACK_N="${CURSOR_ACK_N:-0}"

echo "GATE_WATCH ts=$(date -Iseconds)"
echo "GATE_WATCH local_head=$LOCAL_HEAD"
echo "GATE_WATCH origin_head=$ORIGIN_HEAD"
echo "GATE_WATCH behind=$BEHIND"
echo "GATE_WATCH phase=$PHASE"
echo "GATE_WATCH queue_rev=$QUEUE_REV"
echo "GATE_WATCH latest_cc_receipt=$LATEST_RECEIPT"
echo "GATE_WATCH cursor_ack=$CURSOR_ACK_N"
echo "GATE_WATCH cc_receipt_meta=${CC_RECEIPT_META:-}"
echo "GATE_WATCH origin_head_meta=${ORIGIN_HEAD_META:-}"

CURSOR_ACTION="POLL"
CC_ACTION="POLL"

if [[ "$BEHIND" -eq 1 ]]; then
  CURSOR_ACTION="PULL_REQUIRED"
  CC_ACTION="PULL_REQUIRED"
fi

if [[ "$LATEST_RECEIPT" =~ ^[0-9]+$ && "$CURSOR_ACK_N" =~ ^[0-9]+$ && "$LATEST_RECEIPT" -gt "$CURSOR_ACK_N" ]]; then
  CURSOR_ACTION="AUDIT_RECEIPT_${LATEST_RECEIPT}"
fi

if [[ "$PHASE" == "CC_ACTION_REQUIRED" && "$CURSOR_ACTION" == "POLL" ]]; then
  CC_ACTION="EXECUTE_NOW"
fi

if [[ "$PHASE" == "BLOCKED" ]]; then
  CC_ACTION="BLOCKED_POLL"
  CURSOR_ACTION="BLOCKED_POLL"
fi

echo "GATE_WATCH CURSOR_ACTION=$CURSOR_ACTION"
echo "GATE_WATCH CC_ACTION=$CC_ACTION"
