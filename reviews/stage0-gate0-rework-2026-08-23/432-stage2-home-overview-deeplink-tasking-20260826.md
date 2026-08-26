# 首页四轨一览 overview deeplink — 缩刀任务书

- 编号：`432-stage2-home-overview-deeplink-tasking-20260826`
- 前置：`431` PASS；POLL ~9m → 续刀
- 用户裁定：**C** + **D**

## SCHEMA / 裁定

| 决策点 | 裁定 |
|---|---|
| 本刀做 | (1) 首页 `frontend/app/page.tsx` 公开提取表：新增一行「公开提取四轨一览（overview）」→ `/public-extracts#overview`（镜像 NBS/湖北 deeplink 行；文案标明 demo / 非 O1）；(2) ≥1 smoke 或 pytest；(3) 不改 fixture 字节；(4) 回执 **`432`**（`-cc-`）|
| 本刀不做 | live 探测；O1/Gate PASS |
| 禁止 | 删减 OPEN；谎称 O1 |

## NOW

1. 改 `frontend/app/page.tsx`（+ smoke/pytest）
2. pack → 回执 **`432`**
3. **必须双推** → **`84` POLL**

## 红线

不 Gate/O1 PASS；不改 4 fixture SHA。
