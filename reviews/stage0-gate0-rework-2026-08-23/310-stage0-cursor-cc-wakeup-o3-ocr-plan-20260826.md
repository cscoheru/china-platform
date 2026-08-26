# CC 唤醒 — O3 OCR 规划（`308`）仍未动

- 编号：`310-stage0-cursor-cc-wakeup-o3-ocr-plan-20260826`
- 日期：2026-08-26
- 对象：`queue_rev` 128（`308`）已下发；`cursor_ack=306`；仍无 `docs/49` / 回执 `309`

## 要求

```bash
git fetch origin && git pull --ff-only origin main
./scripts/cc_gate_watch.sh --pull
cat reviews/stage0-gate0-rework-2026-08-23/00-CC-CURRENT.md
```

确认 `CC_ACTION=EXECUTE_NOW` 后，**立刻**执行 **`308`** → 写 `docs/49` → 回执 **`309`**。

禁止 idle；禁止在聊天等 Cursor；禁止爬网/伪造。

— End —
