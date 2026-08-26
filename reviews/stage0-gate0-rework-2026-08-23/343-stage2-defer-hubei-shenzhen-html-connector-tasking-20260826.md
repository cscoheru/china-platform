# 暂缓湖北 + 深圳 HTML connector — 缩刀任务书

- 编号：`343-stage2-defer-hubei-shenzhen-html-connector-tasking-20260826`
- 前置：`342` deeplink PASS；Hubei JS 壳 tech-blocked；Cursor `341` 代判
- 用户裁定：**D** + 源工程 Cursor 代判

## SCHEMA / 裁定

| 决策点 | 裁定 |
|---|---|
| 本刀做 | (1) `source_registry/registry.csv`：湖北行 `enabled=FALSE`，`auth_note`/`failure_handling` 注明「2026-08-26 JS-shell tech-blocked；Cursor 暂缓；禁 headless」；(2) 扩展 connector pilot=`sz.gov.cn` / `MUNICIPAL_BULLETIN`（HTML）；复用 AUTH/drift/deeplink/JS-shell；(3) 一次深圳 `--live`；成功深链/正文非壳 → 可 pin registry + `O1_AUTO_INTAKED`（per `341`）；JS 壳/0 链 → tech-blocked；(4) ≥6 pytest；(5) 回执 **`344`** |
| 本刀不做 | headless 跟湖北 JS；擅自 O1 收口 Gate；NBS 列表页 pin |
| 禁止 | 执行 JS；绕 AUTH；把 JS 壳当 O1 |

## NOW

1. 暂缓湖北 + 深圳 pilot + live
2. 补 pack → 回执 **`344`**
3. `./scripts/cc_gate_watch.sh --pull` → **`84` POLL**

## 红线

不 Gate PASS；不 headless；不绕 AUTH；不伪造。
