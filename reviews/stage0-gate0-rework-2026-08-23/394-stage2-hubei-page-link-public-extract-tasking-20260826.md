# 湖北观察页链到公开提取轨 — 缩刀任务书

- 编号：`394-stage2-hubei-page-link-public-extract-tasking-20260826`
- 前置：`393` PASS；用户：**继续自行决定往下走**
- 用户裁定：**C** + **D**；Cursor 代判

## SCHEMA / 裁定

| 决策点 | 裁定 |
|---|---|
| 本刀做 | (1) 找到湖北相关前端页（省级 `/provinces/...` 或城页若有）；增显式链 `/public-extracts#track-hb`，文案标明 REGISTRY_SAMPLE / xlsx / live `enabled=FALSE` / 非 O1；(2) ≥1 pytest 或 smoke；(3) 回执 **`395`**（`-cc-`）|
| 若无湖北专用页 | 在首页「公开提取」旁加一行「湖北轨 → #track-hb」亦可（缩刀兜底）|
| 本刀不做 | 启用湖北 live；改 extract；Gate/O1 PASS |
| 禁止 | 无条件污染其它省/城页；谎称 live |

## NOW

1. 链接 + 测
2. pack → 回执 **`395`**
3. `./scripts/cc_gate_watch.sh --pull` → **`84` POLL**

## 红线

不 Gate/O1 PASS；必须 demo / enabled=FALSE 提示。
