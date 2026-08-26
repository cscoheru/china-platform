# Gate 握手 v2 — `cursor_ack` / `cc_gate_watch`（修 autopilot 盲区）

- 编号：`216-stage0-cursor-gate-handshake-v2-20260826`
- 日期：2026-08-26
- 根因：`84` 已写「发现新回执须审验」，但监管 tick **只 grep phase**，未 **pull + 比对 receipt 序号** → CC 已交卷 Cursor 仍报「等 215」

---

## §1. 新增 META 字段（`00-CC-CURRENT.md`）

| 字段 | 写入者 | 含义 |
|---|---|---|
| **`cursor_ack`** | Cursor | 已审验通过的 **CC 回执编号**（如 `215`） |
| **`cc_receipt`** | Cursor（从 origin 观测） | origin 上最新 CC 回执编号（与 `cursor_ack` 对齐时 = 已 ACK） |
| **`origin_head`** | Cursor | 写 CURRENT 时的 `origin/main` SHA（CC 可比对是否落后） |

**CC 退出 POLL 条件（增补）：**

```bash
./scripts/cc_gate_watch.sh --pull
# 当 cursor_ack >= 你刚交的回执号 且 queue_rev 已 bump → 读 §NOW 执行
# 当 phase=CC_ACTION_REQUIRED → 读 §NOW 执行（同 84）
```

**Cursor 监管 tick 强制：**

```bash
./scripts/cc_gate_watch.sh --pull
# CURSOR_ACTION=AUDIT_RECEIPT_NNN → 本 tick 内审验 + push（禁止只报「仍等 CC」）
# CURSOR_ACTION=PULL_REQUIRED → 先 pull 再重跑
```

---

## §2. 脚本

- **`scripts/cc_gate_watch.sh`** — 机器可读 `GATE_WATCH` 行 + `CURSOR_ACTION` / `CC_ACTION`

---

## §3. 与 `84` 关系

- `84` 双环仍有效；本文件 **不新增聊天信道**
- 废除「只看 phase 字符串」作为唯一监管逻辑

— End —
