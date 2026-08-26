# S2.9-lite — 同类地区对比缩刀实现任务书

- 编号：`244-stage2-s29-lite-peer-compare-impl-tasking-20260826`
- 前置：`243` 规划 PASS；`docs/43`；用户 **D**
- 用户裁定：**D** + Stage 2 **C**

## SCHEMA / 裁定

| 决策点 | 裁定 |
|---|---|
| 本刀做 | peer 对比 **UI 壳**（可 mock；手工选择；对齐 docs/43） |
| dbt / 全量对比数据 | **本刀不做** |
| 全国实时排名 | **禁止** |

## NOW

1. 落地对比最小壳（mock OK）
2. 最小可验检查 → 补 pack → commit → 回执 **`245`**
3. `./scripts/cc_gate_watch.sh --pull` → **`84` POLL**

## 红线

不 Gate PASS；不做官员评分；不 DSH；不爬网；不做全国实时排名。
