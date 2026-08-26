# JS-shell 误判收紧 + NBS live 再探 — 缩刀任务书

- 编号：`355-stage2-js-shell-heuristic-nbs-live-tasking-20260826`
- 前置：`354` PASS；NBS live 曾因大页含 `window.location`/`<script>` 被 rc=7；Cursor `341` 代判
- 用户裁定：**D**

## SCHEMA / 裁定

| 决策点 | 裁定 |
|---|---|
| 本刀做 | (1) 收紧 `is_js_only_shell`：**仅当** `len(blob) < threshold` **且**（含 `<script` 或 `window.location`）→ 真壳；大页（≥threshold）即使有 script **不**因启发式单独 tech-block；(2) 大页无 deeplink 且无 `<table>` 时可另报「空内容」tech-blocked（非 JS 壳）；(3) ≥4 pytest（小壳仍拦 / 大页+script 放行 / 回归 Hubei 71B）；(4) **一次** NBS `--live`：成功则 deep-link/归档/按 `341` 可 pin；仍失败如实报告；(5) 回执 **`356`**（`-cc-` 名）|
| 本刀不做 | headless；HTTP pin 深圳；Gate/O1 伪 PASS |
| 禁止 | 执行 JS；把 71B 壳放行；伪造 O1 |

## NOW

1. 收紧启发式 + 测 + NBS live
2. 补 pack → 回执 **`356`**
3. `./scripts/cc_gate_watch.sh --pull` → **`84` POLL**

## 红线

不 Gate PASS；不 headless；不绕 AUTH；小壳仍拦。
