# S2.7-b-full — mart/person 真数据接入 规划任务书

- 编号：`262-stage2-s27b-full-mart-plan-tasking-20260826`
- 前置：`261` docs/45 刷新 PASS；`docs/46`；S2.7-b-lite `257`
- 用户裁定：**D**；自主推进

## SCHEMA / 裁定

| 决策点 | 裁定 |
|---|---|
| 交付 | **`docs/47-stage2-s27b-full-mart-evidence-plan-YYYYMMDD.md`** |
| 范围 | 10 城 EvidenceChain 接 mart；person/tenure 契约；与 S2.1-lite DDL 对齐 |
| 本刀 | **只规划**；不写 migration / 不全量 seed |
| 禁止 | Gate 1/2 PASS；评分/排名；DSH；爬网；伪造 SHA |

## NOW

1. 起草 `docs/47`（mart 映射、段级字段、验收、OPEN、lite→full 切刀）
2. 补 pack → commit → 回执 **`263`**
3. `./scripts/cc_gate_watch.sh --pull` → **`84` POLL**

## 红线

不 Gate PASS；不做官员评分；不 DSH；不爬网；不伪造 SHA。
