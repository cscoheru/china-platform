# docs/45 索引刷新 — S2.7-b-full-lite 收口缩刀任务书

- 编号：`268-stage2-gate2-index-s27bf-refresh-tasking-20260826`
- 前置：`267` S2.7-b-full-lite PASS；`docs/45`；`docs/47`
- 用户裁定：**D**；自主推进

## SCHEMA / 裁定

| 决策点 | 裁定 |
|---|---|
| 交付 | 更新 **`docs/45`**：§2/#1 与 §5/§6 反映 mart-shape 接驳（`266`）；修正「10 地市 OPEN」过时行 |
| 本刀不做 | Gate 2 PASS；O1 真样本；dbt seed |
| 禁止 | Gate 1/2 PASS；评分/排名；DSH；爬网 |

## NOW

1. 刷新 `docs/45`（full-lite 证据路径 + OPEN 仍标 O1/mart 全量）
2. 补 pack → commit → 回执 **`269`**
3. `./scripts/cc_gate_watch.sh --pull` → **`84` POLL**

## 红线

不 Gate PASS；不做官员评分；不 DSH；不爬网。
