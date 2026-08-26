# 前端生产构建硬化 — 缩刀任务书

- 编号：`271-stage2-frontend-prod-build-fix-tasking-20260826`
- 前置：`270` docs/45 刷新 PASS；港服已尝试 `next build`（缺 `"use client"` / 类型导入失败）
- 用户裁定：**D**；恢复自主推进（取消空 POLL 等待）

## SCHEMA / 裁定

| 决策点 | 裁定 |
|---|---|
| 本刀做 | 修生产 `next build`：`PeerCompareCard` / `SevenDimGrid` 加 `"use client"`；`SevenDimCardId` 改从 `types_seven_dim` 导入 |
| 验收 | `cd frontend && NEXT_PUBLIC_USE_MOCK=true npm run build` 成功；smoke 不破 |
| 本刀不做 | O1 真样本；dbt 全量；改 CF/nginx（运维已另做）|
| 禁止 | Gate 1/2 PASS；评分/排名；DSH；爬网 |

## NOW

1. 落地上述前端最小修复
2. 本地 `npm run build`（mock）通过 → 补 pack → commit → 回执 **`272`**
3. `./scripts/cc_gate_watch.sh --pull` → **`84` POLL**

## 红线

不 Gate PASS；不做官员评分；不 DSH；不爬网。
