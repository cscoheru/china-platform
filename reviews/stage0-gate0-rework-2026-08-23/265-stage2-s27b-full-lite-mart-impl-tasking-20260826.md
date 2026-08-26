# S2.7-b-full-lite — mart 形状接入缩刀任务书

- 编号：`265-stage2-s27b-full-lite-mart-impl-tasking-20260826`
- 前置：`264` 规划 PASS；`docs/47`；用户 **D**
- 用户裁定：**D**；自主推进

## SCHEMA / 裁定

| 决策点 | 裁定 |
|---|---|
| 本刀做 | 按 `docs/47`：mart **形状** TS 类型 + `is_demo` fixture；CityPage 可切 mock→mart-shape；最小 pytest |
| 本刀不做 | 真 SHA 样本；全量 dbt seed；O1 收口 |
| 禁止 | Gate 1/2 PASS；评分/排名；DSH；爬网；伪造 SHA |

## NOW

1. 落地 mart-shape types + demo fixture + CityPage 接驳（可 feature-flag / 默认 demo）
2. 最小 pytest → 补 pack → commit → 回执 **`266`**
3. `./scripts/cc_gate_watch.sh --pull` → **`84` POLL**

## 红线

不 Gate PASS；不做官员评分；不 DSH；不爬网；不伪造 SHA。
