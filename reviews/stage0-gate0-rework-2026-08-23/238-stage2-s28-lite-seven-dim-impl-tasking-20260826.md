# S2.8-lite — 七维卡缩刀实现任务书

- 编号：`238-stage2-s28-lite-seven-dim-impl-tasking-20260826`
- 前置：`237` 规划 PASS；`docs/42`；用户 **D**
- 用户裁定：**D** + Stage 2 **C**

## SCHEMA / 裁定

| 决策点 | 裁定 |
|---|---|
| 本刀先做 | **补 pack**：登记回执 `236`（manifest +1，invariant 守门） |
| 本刀再做 | 七维卡 **UI 壳**（可 mock；对齐 docs/42 §3 最小形态）或等价最小可验交付 |
| dbt mart / 全量 cell seed | **本刀不做** |
| migration | 无新业务表则可不交 |

## NOW

1. 补 pack 登记 `236` → invariant
2. 落地七维卡最小壳（mock OK）或回执写明等价路径
3. 最小可验检查 → 补 pack → commit → 回执 **`239`**
4. `./scripts/cc_gate_watch.sh --pull` → **`84` POLL**

## 红线

不 Gate PASS；不做官员评分；不 DSH；不爬网；不扩 S2.9。
