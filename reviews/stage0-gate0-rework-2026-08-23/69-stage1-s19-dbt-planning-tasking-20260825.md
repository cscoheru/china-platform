# S1.9 — dbt 模型层规划任务书

- 编号：`69-stage1-s19-dbt-planning-tasking-20260825`
- 前置：`68` S1.8 通过；`docs/08` §2.1 S1.9
- 范围：**规划 only**（staging 模型设计；不强制全量历史入库）

## NOW（CC 交付）

1. 起草 **`docs/23-stage1-s19-dbt-staging-plan-20260825.md`**（CC 拥有）
2. 目标：≥5 张 staging view / model；对接已有 `observation` / `source_document` / `ingestion_run`
3. 明确：本刀不批量爬取；不降 OCR；不宣布 Gate 1；可基于已有试点数据 + 空表诚实
4. 规划 only — 实现另开任务书

## 红线

不 Gate 1 PASS；不 DSH；Cursor 不写 `docs/23` 正文。
