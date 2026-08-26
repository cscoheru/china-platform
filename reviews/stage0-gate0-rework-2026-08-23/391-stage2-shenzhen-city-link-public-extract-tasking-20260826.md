# 深圳城页链到公开提取轨 — 缩刀任务书

- 编号：`391-stage2-shenzhen-city-link-public-extract-tasking-20260826`
- 前置：`390` PASS；用户：**继续自行决定往下走**
- 用户裁定：**C** + **D**；Cursor 代判

## SCHEMA / 裁定

| 决策点 | 裁定 |
|---|---|
| 本刀做 | (1) `frontend/app/cities/` 深圳相关页（`CityPage` / mart / slug=`shenzhen` 路径）增显式链接：`/public-extracts#track-sz`（文案标明 REGISTRY_SAMPLE demo，非 O1）；(2) 首页或七维无关处可不改；(3) ≥1 pytest 或 smoke 针；(4) 回执 **`392`**（`-cc-`）|
| 本刀不做 | 改 extract；湖北/NBS 城页连环（可后续）；Gate/O1 PASS |
| 禁止 | 谎称深圳城页数据=公报 extract；改 fixture 字节 |

## NOW

1. 深圳城页链接 + 测
2. pack → 回执 **`392`**
3. `./scripts/cc_gate_watch.sh --pull` → **`84` POLL**

## 红线

不 Gate/O1 PASS；链接必须带 demo/REGISTRY_SAMPLE 提示。
