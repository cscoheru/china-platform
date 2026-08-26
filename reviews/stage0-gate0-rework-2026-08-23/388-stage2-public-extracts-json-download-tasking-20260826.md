# 四轨 extract JSON 静态下载 — 缩刀任务书

- 编号：`388-stage2-public-extracts-json-download-tasking-20260826`
- 前置：`387` PASS；预览已有四轨 + 一览；用户：**继续自行决定往下走**
- 用户裁定：**C** + **D**；Cursor 代判

## SCHEMA / 裁定

| 决策点 | 裁定 |
|---|---|
| 本刀做 | (1) 将 4 个 frontend fixture **字节一致**拷到 `frontend/public/public-extracts/`（`nbs.json` / `nbs-live-candidate.json` / `sz.json` / `hubei.json`）；(2) 一览表或各分节加「下载 JSON」链（`/public-extracts/*.json`，`download` 属性可选）；(3) ≥2 pytest（public 文件 sha/字节 == fixture）+ smoke 针；(4) 回执 **`389`**（`-cc-`）|
| 本刀不做 | 改 extract 逻辑；Gate/O1 PASS；加新源 |
| 禁止 | 改写 fixture 内容；谎称 live/O1 |

## NOW

1. public 拷贝 + 下载链 + 测
2. pack → 回执 **`389`**
3. `./scripts/cc_gate_watch.sh --pull` → **`84` POLL**

## 红线

不 Gate/O1 PASS；public 与 `lib/public_extract_*.json` 必须字节一致。
