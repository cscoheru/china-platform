# docs/45 三轨公开提取刷新 — 缩刀任务书

- 编号：`373-stage2-docs45-three-track-extracts-refresh-tasking-20260826`
- 前置：`372` PASS；`/public-extracts` 已部署三轨（NBS sample 63 / NBS live 60 / 深圳 sample 71）
- 用户裁定：**D** + Stage 2 **C**；空闲 POLL → 续刀

## SCHEMA / 裁定

| 决策点 | 裁定 |
|---|---|
| 本刀做 | (1) 刷新 `docs/45`：登记公开提取**三轨**（原双轨 + 深圳 REGISTRY_SAMPLE 散文 71 行 / `d5e2c731…` / fixture `public_extract_sz.json` / 回执链 `368`→`371`）；更新 §1 公开提取段 + §6.2 相关索引行；(2) 显式写清：三轨皆 demo/candidate，**非** O1/Gate PASS；(3) ≥1 轻测或 docs 自检（按既有 docs45 refresh 惯例即可）；(4) 回执 **`374`**（`-cc-`）|
| 本刀不做 | 改前端；深圳 HTTPS live；改 NBS fixture；Gate/O1 PASS 宣告 |
| 禁止 | 谎称三轨=O1；覆盖/删减既有 OPEN 清单 |

## NOW

1. 只改 `docs/45`（必要时顺带 `docs/53` 一句指向三轨；非必须）
2. pack → 回执 **`374`**
3. `./scripts/cc_gate_watch.sh --pull` → **`84` POLL**

## 红线

不 Gate/O1 PASS；不改业务代码；不碰 extract/fixture 字节。
