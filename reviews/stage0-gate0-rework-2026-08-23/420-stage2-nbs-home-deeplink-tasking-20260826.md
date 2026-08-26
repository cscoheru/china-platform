# 首页 NBS sample 轨链 — 缩刀任务书

- 编号：`420-stage2-nbs-home-deeplink-tasking-20260826`
- 前置：`419` PASS；POLL ~9m → 续刀
- 用户裁定：**C** + **D**

## SCHEMA / 裁定

| 决策点 | 裁定 |
|---|---|
| 本刀做 | (1) 首页 `frontend/app/page.tsx` 公开提取表：为 NBS sample 轨加显式链 `/public-extracts#track-nbs-sample`（镜像湖北 `#track-hb` 行；文案标明 REGISTRY_SAMPLE / demo / 非 O1；可改现有「四轨 demo」行 href 或新增一行）；(2) ≥1 smoke 或 pytest 针；(3) 不改 fixture 字节；(4) 回执 **`420`**（`-cc-`）|
| 本刀不做 | live 探测；O1/Gate PASS；改深圳/湖北既有链 |
| 禁止 | 删减 OPEN；谎称 O1 |

## NOW

1. 改 `frontend/app/page.tsx`（+ smoke/pytest）
2. pack → 回执 **`420`**
3. **必须双推** → **`84` POLL**

## 红线

不 Gate/O1 PASS；不改 4 fixture SHA。
