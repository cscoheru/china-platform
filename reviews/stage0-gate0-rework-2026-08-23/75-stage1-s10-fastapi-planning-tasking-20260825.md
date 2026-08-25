# S1.10 — FastAPI 只读查询层规划任务书

- 编号：`75-stage1-s10-fastapi-planning-tasking-20260825`
- 前置：`74` S1.9 通过；`docs/08` §2.1 S1.10；`docs/02` L5
- 范围：**规划 only**（不写 FastAPI 代码）

## NOW（CC 交付）

1. 起草 **`docs/24-stage1-s10-fastapi-readonly-plan-20260825.md`**（CC 拥有）
2. 核心验收：`GET /api/indicator/{id}/series` 可调用（对接 `int_indicator_timeseries` 或等价 SQL）
3. 须覆盖：DSN 环境变量、只读、OpenAPI、错误契约、与 `docs/10` 数据层测试映射
4. 明确边界：本刀不 Next.js；不 DSH；不 Gate 1 PASS；不批量爬取
5. 规划 only — 实现另开任务书

## 红线

不 Gate 1 PASS；不 DSH；Cursor 不写 `docs/24` 正文。
