# S2.7-b-full-mart-demo-join — mart 接 demo 行缩刀任务书

- 编号：`293-stage2-s27b-full-mart-demo-join-tasking-20260826`
- 前置：`292` intake PASS；`docs/47` §3；dbt skel `288`；用户要尽快看到数据
- 用户裁定：**D**；自主推进；**O1 仍 OPEN**（本刀**不是**真样本收口）

## SCHEMA / 裁定

| 决策点 | 裁定 |
|---|---|
| 本刀做 | 把 `mart_city_evidence_chain` / `mart_city_seven_dim_overview` 从 `WHERE FALSE` 改为可产出行：优先 JOIN 现有 demo/`is_demo=true` 上游（inference / geo / seed 路径按库内实际选型）；无库时可退化为 **dbt seed/CSV 或 SQL VALUES demo 行**（10 城 × 必要段/维，显式 `lineage_is_demo='true'`，SHA 仍 `'0'*64`）；更新 pytest（允许非零行但强制 is_demo + 零 SHA + 无 score/rank）；可选：smoke/文档注明 `NEXT_PUBLIC_USE_MART_FIXTURE` 与 mart 关系 |
| 本刀不做 | O1 收口；非零真 SHA；爬网；把 demo 冒充真实；宣布 Gate PASS |
| 禁止 | Gate 1/2 PASS；评分/排名；DSH；爬网；伪造 SHA；擅自 O1 CLOSED |

## NOW

1. 落地两 mart view 可产出 **demo 行**（契约对齐 `docs/47`）
2. 更新 `tests/test_mart_city_dbt_skel_s27bf.py`（或新测）→ 补 pack → 回执 **`294`**
3. `./scripts/cc_gate_watch.sh --pull` → **`84` POLL**

## 红线

不 Gate PASS；不伪造真 SHA；不爬网；所有新出行必须 `is_demo=true` + SHA 占位，直到用户投递真文件并确认 O1。
