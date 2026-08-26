# /public-extracts 四轨一览条 — 缩刀任务书

- 编号：`382-stage2-public-extracts-overview-strip-tasking-20260826`
- 前置：`381` PASS；四轨数据已齐；用户：**继续自行决定往下走**
- 用户裁定：**C** + **D**；Cursor 代判

## SCHEMA / 裁定

| 决策点 | 裁定 |
|---|---|
| 本刀做 | (1) `/public-extracts` 页首增**四轨一览**（非 card 堆砌：一表或一行摘要）：域名 / 类别 / 行数 / SHA 前 8 / demo\|candidate 标注 / 锚点链到分节；(2) 数据只读自既有 4 fixture，不重算；(3) ≥2 pytest + smoke 针；(4) 回执 **`383`**（`-cc-`）|
| 本刀不做 | 新源抽取；改 fixture 字节；Gate/O1 PASS；炫技图表库 |
| 禁止 | 谎称 live/O1；破坏四分节正文 |

## NOW

1. 页首一览 + 测
2. pack → 回执 **`383`**
3. `./scripts/cc_gate_watch.sh --pull` → **`84` POLL**

## 红线

不 Gate/O1 PASS；不碰 extract JSON 字节。
