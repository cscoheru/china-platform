# 首页 NBS live 候选轨链 — 缩刀任务书

- 编号：`424-stage2-nbs-live-home-deeplink-tasking-20260826`
- 前置：`423` PASS；POLL ~9m → 续刀
- 用户裁定：**C** + **D**

## SCHEMA / 裁定

| 决策点 | 裁定 |
|---|---|
| 本刀做 | (1) 首页 `frontend/app/page.tsx` 公开提取表：新增一行「公开提取 NBS live 候选轨（candidate demo）」→ `/public-extracts#track-nbs-live`（镜像 NBS sample `#track-nbs-sample` 与湖北 `#track-hb` 行；文案标明 LIVE_CANDIDATE / drift 候选 / 非 O1）；(2) ≥1 smoke 或 pytest；(3) 不改 fixture 字节；(4) 回执 **`424`**（`-cc-`）|
| 本刀不做 | live 探测；改 registry；O1/Gate PASS |
| 禁止 | 删减 OPEN；谎称 O1 |

## NOW

1. 改 `frontend/app/page.tsx`（+ smoke/pytest）
2. pack → 回执 **`424`**
3. **必须双推** → **`84` POLL**

## 红线

不 Gate/O1 PASS；不改 4 fixture SHA；drift 候选非 O1 收口。
