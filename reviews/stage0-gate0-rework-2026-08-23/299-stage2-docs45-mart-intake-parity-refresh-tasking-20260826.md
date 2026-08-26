# docs/45 索引刷新 — mart/intake/parity 收口缩刀

- 编号：`299-stage2-docs45-mart-intake-parity-refresh-tasking-20260826`
- 前置：`298` parity PASS；`294` demo-join；`291` intake（WAITING_FILE）
- 用户裁定：**D**；自主推进；**O1 仍 OPEN**

## SCHEMA / 裁定

| 决策点 | 裁定 |
|---|---|
| 本刀做 | 更新 **`docs/45`**：登记 `288/294` mart 骨架+demo-join、`291` 真 SHA 投递（WAITING_FILE）、`297` 前端 parity；修正过时 OPEN 行；明确预览可用 `NEXT_PUBLIC_USE_MART_FIXTURE=1` 看 demo 管道（非 O1）|
| 本刀不做 | Gate/O1 PASS；伪造；爬网；改业务代码 |
| 禁止 | Gate 1/2 PASS；评分；DSH；爬网；擅自 O1 收口 |

## NOW

1. 刷新 `docs/45` 相关 §2/§3/§5/§6
2. 补 pack → 回执 **`300`**
3. `./scripts/cc_gate_watch.sh --pull` → **`84` POLL**

## 红线

不 Gate PASS；不伪造；不爬网；不宣布 O1 收口。
