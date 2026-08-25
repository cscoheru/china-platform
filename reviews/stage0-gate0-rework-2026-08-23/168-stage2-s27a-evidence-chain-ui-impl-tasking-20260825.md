# S2.7-a — 六段证据链 UI 雏形 实现任务书

- 编号：`168-stage2-s27a-evidence-chain-ui-impl-tasking-20260825`
- 前置：`167` S2.0.2.3 PASS；`docs/34` §4 序 3；`docs/06` §2
- 用户裁定：**C**

## SCHEMA / 裁定

| 决策点 | 裁定 |
|---|---|
| 范围 | `frontend/` 六段证据链 **UI 雏形**（可点击）；复用 S2.0.1 骨架 |
| 六段 | 固定：`CONDITION → COMMITMENT → INPUT → PROCESS → （衔接）→ OUTCOME_RISK`（`docs/06` §2；缺一不可的展示契约） |
| 数据 | **允许 mock**（5 省或至少江苏 + ≥1 他省路由壳）；`is_demo` / DemoBadge 契约保留 |
| API | **不**新写后端 schema；可 mock 或读既有只读 API |
| 评分 | **禁止**官员能力分 / 总分 / 排名 |

## NOW

1. 落地可点击的六段证据链组件（挂到省级观察页）；mock 数据须标清段名与来源占位
2. 至少 **1** 个省页可演示完整六段；另 **≥1** 省路由壳或列表入口（对齐「5 省」方向的第一步）
3. 前端 smoke / 最小测试仍绿；回执写清启动方式
4. commit → origin → 回执 **`169`** 进 `reviews/`
5. → **`84` POLL**

## 红线

不 Gate PASS；不做官员评分；不 DSH；不爬网；不改 `gate_thresholds.json`；不扩 S2.1 person/tenure schema（留给后续刀）。
