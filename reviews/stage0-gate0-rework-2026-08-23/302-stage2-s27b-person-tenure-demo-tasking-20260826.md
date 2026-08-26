# S2.7-b person/tenure demo 接驳 — 缩刀任务书

- 编号：`302-stage2-s27b-person-tenure-demo-tasking-20260826`
- 前置：`301` docs/45 PASS；`docs/47` §3.3；城市页 `relatedPersons` 现多为空
- 用户裁定：**D**；尽快看见数据；**O1 仍 OPEN**

## SCHEMA / 裁定

| 决策点 | 裁定 |
|---|---|
| 本刀做 | 为 10 城 mart/CityPage 路径补 **demo `relatedPersons`/tenure**（显式 `isDemo=true`；无真履历爬取）；对齐 `docs/47` §3.3 字段契约的最小子集；最小 pytest/smoke；不接真 SHA |
| 本刀不做 | O1 收口；爬履历/官网；伪造真身份材料；官员评分/排名 |
| 禁止 | Gate 1/2 PASS；DSH；爬网；把 demo 标成真实人物核验通过 |

## NOW

1. 落地 10 城 demo person/tenure 接驳（TS fixture 和/或 dbt 侧最小占位，择一主路径并在回执说明）
2. pytest/smoke → 补 pack → 回执 **`303`**
3. `./scripts/cc_gate_watch.sh --pull` → **`84` POLL**

## 红线

不 Gate PASS；不爬网；不伪造真样本；UI 必须可区分 demo。
