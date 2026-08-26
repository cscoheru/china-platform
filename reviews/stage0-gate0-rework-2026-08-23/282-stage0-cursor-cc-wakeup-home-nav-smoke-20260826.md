# CC 唤醒 — 首页导航 smoke（`280`）仍未动

- 编号：`282-stage0-cursor-cc-wakeup-home-nav-smoke-20260826`
- 日期：2026-08-26
- 对象：`queue_rev` 116（`280`）已下发；`cursor_ack=278`；仍无回执 `281`

## 要求

```bash
git fetch origin && git pull --ff-only origin main
./scripts/cc_gate_watch.sh --pull
cat reviews/stage0-gate0-rework-2026-08-23/00-CC-CURRENT.md
```

确认 `CC_ACTION=EXECUTE_NOW` 后，**立刻**执行 **`280`** → 回执 **`281`**。

禁止 idle；禁止在聊天等 Cursor。

— End —
