# /public-extracts 行筛选 — 缩刀任务书

- 编号：`397-stage2-public-extracts-row-filter-tasking-20260826`
- 前置：`396` PASS；首页文案已对齐；用户：**继续自行决定往下走**
- 用户裁定：**C** + **D**；Cursor 代判

## SCHEMA / 裁定

| 决策点 | 裁定 |
|---|---|
| 本刀做 | (1) `/public-extracts` 各数据表上方（或一览条下）增加**轻量行筛选**：单输入框，按单元格文本包含匹配过滤当前可见表（四轨各自独立或共用一个 filter 作用于当前滚动分节——优先**每轨独立 input**，实现简单）；(2) 纯客户端，不改 fixture 字节；(3) ≥2 pytest/smoke 针（input 在位 + 过滤逻辑或 data-testid）；(4) 回执 **`398`**（`-cc-`）|
| 本刀不做 | 新源；改 SHA；Gate/O1 PASS；重型表格库 |
| 禁止 | 谎称筛选结果=权威库；破坏 demo 标注 |

## NOW

1. 行筛选 UI + 测
2. pack → 回执 **`398`**
3. `./scripts/cc_gate_watch.sh --pull` → **`84` POLL**

## 红线

不 Gate/O1 PASS；不碰 extract JSON 字节。
