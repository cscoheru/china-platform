# S2.0 — Stage 2 启动规划任务书

- 编号：`143-stage2-s20-kickoff-planning-tasking-20260825`
- 前置：`142` 用户裁定 **C**；`140` S1.18 PASS；`docs/08` §3
- 范围：**规划 only**

## 目标

起草 Stage 2 启动规划，把 `docs/08` §3（S2.1–S2.10）落成可执行的首批刀序，并诚实继承 Gate 1 OPEN 缺口。

## NOW（CC 交付）

1. 起草 **`docs/34-stage2-s20-kickoff-plan-20260825.md`**（CC 拥有）
2. 须覆盖：
   - Stage 2 目标 / Gate 2 定义（对齐 `docs/08` §3；不擅自扩 scope）
   - 从 Stage 1 继承的 OPEN 清单（真实 SHA 样本、cron/通知、OCR 生产路径等）
   - 建议首刀序（推荐先 **S2.7 相关前端骨架** 或 **S2.1 person/tenure** —— 须论证依赖；默认建议：**S2.0.1 Next.js 骨架 + API 串联演示**，人事表可并行规划）
   - 「不做什么」（`docs/08` §3.3 + 不宣布 Gate 1/2 PASS）
   - 与现有 FastAPI / dbt / admin upload / URL probe 的边界
3. 规划 only — 实现另开；回执 **`144`** 进 `reviews/`
4. → **`84` POLL**

## 红线

不 Gate 1/2 PASS；不 DSH；不爬网；不改 `gate_thresholds.json`；Cursor 不写 `docs/34` 正文。
