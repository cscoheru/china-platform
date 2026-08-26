# 前端 mart 契约对齐 — 缩刀任务书

- 编号：`296-stage2-frontend-mart-demo-parity-tasking-20260826`
- 前置：`295` mart demo-join PASS；`frontend/lib/mart_city_demo.ts` + `CityPageMart`
- 用户裁定：**D**；尽快看见数据；**O1 仍 OPEN**

## SCHEMA / 裁定

| 决策点 | 裁定 |
|---|---|
| 本刀做 | 对齐 `frontend/lib/mart_city_demo.ts`（及必要类型）与 dbt mart demo-join：**10 城**、段/维覆盖、显式 `isDemo=true`、SHA 占位 `'0'*64`；补/改最小 pytest 或 smoke；首页/城市页在 `NEXT_PUBLIC_USE_MART_FIXTURE=1` 下可展示且带 demo 标识；不接真 SHA |
| 本刀不做 | O1 收口；爬网；伪造；改 CF 密钥；擅自宣布 Gate PASS |
| 禁止 | Gate 1/2 PASS；评分/排名；DSH；爬网；把 demo 标成真实 |

## NOW

1. 对齐前端 mart demo 与 dbt 契约 → smoke/pytest
2. 补 pack → 回执 **`297`**
3. `./scripts/cc_gate_watch.sh --pull` → **`84` POLL**

## 红线

不 Gate PASS；不伪造；不爬网；UI 必须可区分 demo（不得伪装已收口 O1）。
