# S2.0.1 — Next.js 骨架 + API 演示串联 实现任务书

- 编号：`146-stage2-s201-nextjs-skeleton-impl-tasking-20260825`
- 前置：`145` 规划通过；`docs/34` §4.1 序 1；用户裁定 **C**

## SCHEMA / 裁定

| 决策点 | 裁定 |
|---|---|
| 范围 | Next.js App Router 骨架 + 消费 **现有** FastAPI（S1.10）的演示页 |
| 数据 | **允许 mock**；须能区分/展示 `is_demo` vs 未来真实 SHA（文案/角标即可） |
| 写路径 | **不**新增写 API；上传仍走 S1.13 admin |
| 包 | 补 `docs/34` 入 `evidence_pack`（+1 documentation）；本刀新文件同步计 role |

## NOW

1. 落地 Next.js 应用目录（约定：`frontend/` 或仓库既有约定；须在回执写明）
2. 至少：首页 + **1 个省级观察页壳** + 调用/展示 indicator series（真实 API 或明确 mock 开关）
3. README / 启动说明；pytest 或前端 smoke（最小可验收）
4. commit → origin → 回执 **`147`** 进 `reviews/`
5. → **`84` POLL**

## 红线

不 Gate 1/2 PASS；不做官员评分；不 DSH；不爬网；不改 `gate_thresholds.json`；不扩 S2.1 schema。
