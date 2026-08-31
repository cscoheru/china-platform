#!/usr/bin/env bash
# dual_poll_status.sh — Cursor↔CC 对表探针（00-DUAL-POLL-PROTOCOL-20260831）
# 用法: ./scripts/dual_poll_status.sh [--pull]
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"
REVIEWS="reviews/stage0-gate0-rework-2026-08-23"
QUEUE="$REVIEWS/00-EXEC-QUEUE.md"

if [[ "${1:-}" == "--pull" ]]; then
  git fetch origin 2>/dev/null || true
  git pull --ff-only origin main 2>/dev/null || true
fi

HEAD="$(git rev-parse --short HEAD 2>/dev/null || echo unknown)"
ORIGIN="$(git rev-parse --short origin/main 2>/dev/null || echo unknown)"

NOW_LINE="$(grep -E '^\| NOW |^- tasking:|§NOW|^\*\*633|\*\*631|M2-b|EXECUTE|DELIVERED' "$QUEUE" 2>/dev/null | head -20 || true)"
TASKING="$(grep -E '^- tasking:' "$QUEUE" | head -1 | sed 's/^- tasking: //' || true)"
STATUS="$(grep -E '^- status:' "$QUEUE" | head -1 || true)"
CC_HEAD="$(grep -E '^- cc_head:' "$QUEUE" | head -1 || true)"
LAST_AUDIT="$(grep -E '^- last_audit:' "$QUEUE" | head -1 || true)"

# Extract knife number from tasking filename if present (e.g. 633-...)
KNIFE="$(echo "$TASKING" | grep -oE '^[0-9]+' || true)"
if [[ -z "$KNIFE" ]]; then
  KNIFE="$(echo "$STATUS" | grep -oE '[0-9]{3}' | head -1 || true)"
fi

RECEIPT=""
AUDIT=""
if [[ -n "$KNIFE" ]]; then
  RECEIPT="$(ls -1 "$REVIEWS/${KNIFE}"-stage0-cc-*-receipt-*.md 2>/dev/null | tail -1 || true)"
  AUDIT="$(ls -1 "$REVIEWS/${KNIFE}"-stage0-*-audit-*.md 2>/dev/null | tail -1 || true)"
  # also cursor audit naming
  if [[ -z "$AUDIT" ]]; then
    AUDIT="$(ls -1 "$REVIEWS"/*-cursor-s${KNIFE}-*-audit-*.md 2>/dev/null | tail -1 || true)"
  fi
fi

CURSOR_ACTION="WAIT"
CC_ACTION="POLL"
REASON="waiting_for_cc_delivery"

# If queue says NOW execute and tasking exists without receipt → CC should execute
if echo "$STATUS" | grep -qiE 'NOW'; then
  if [[ -z "$RECEIPT" ]]; then
    CC_ACTION="EXECUTE_NOW"
    REASON="tasking_pending_no_receipt"
  fi
fi

# Receipt exists, no audit → Cursor audits
if [[ -n "$RECEIPT" && -z "$AUDIT" ]]; then
  # Prefer origin-tracked receipt
  if git ls-files --error-unmatch "$RECEIPT" >/dev/null 2>&1 || \
     git cat-file -e "origin/main:$RECEIPT" 2>/dev/null; then
    CURSOR_ACTION="AUDIT_NOW"
    CC_ACTION="POLL"
    REASON="receipt_awaiting_audit"
  else
    CURSOR_ACTION="WAIT"
    CC_ACTION="POLL"
    REASON="receipt_local_only_not_pushed"
  fi
fi

# Both receipt + audit PASS → CC may have next NOW
if [[ -n "$RECEIPT" && -n "$AUDIT" ]]; then
  if echo "$AUDIT" | grep -qi 'PASS'; then
    if echo "$STATUS" | grep -qiE 'NOW'; then
      # check if tasking knife > audited knife
      NEXT="$(echo "$TASKING" | grep -oE '^[0-9]+' || true)"
      if [[ -n "$NEXT" && "$NEXT" != "$KNIFE" ]]; then
        CC_ACTION="EXECUTE_NOW"
        CURSOR_ACTION="WAIT"
        REASON="next_tasking_ready"
      else
        # same knife audited; if status still NOW for next work
        CC_ACTION="EXECUTE_NOW"
        CURSOR_ACTION="WAIT"
        REASON="audited_check_queue_now"
      fi
    else
      CC_ACTION="POLL"
      CURSOR_ACTION="WAIT"
      REASON="audited_waiting_next_sign"
    fi
  elif echo "$AUDIT" | grep -qi 'FAIL'; then
    CC_ACTION="EXECUTE_NOW"
    CURSOR_ACTION="WAIT"
    REASON="audit_fail_rework"
  fi
fi

echo "DUAL_POLL $(date -Iseconds)"
echo "HEAD=$HEAD ORIGIN=$ORIGIN"
echo "KNIFE=${KNIFE:-none}"
echo "$STATUS"
echo "$CC_HEAD"
echo "$LAST_AUDIT"
echo "tasking=${TASKING:-none}"
echo "receipt=${RECEIPT:-none}"
echo "audit=${AUDIT:-none}"
echo "CURSOR_ACTION=$CURSOR_ACTION"
echo "CC_ACTION=$CC_ACTION"
echo "REASON=$REASON"
