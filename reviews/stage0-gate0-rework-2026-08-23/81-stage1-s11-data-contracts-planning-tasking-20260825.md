# S1.11 — 数据契约（Great Expectations）规划任务书

- 编号：`81-stage1-s11-data-contracts-planning-tasking-20260825`
- 前置：`80` S1.10 通过；`docs/08` §2.1 S1.11；依赖 S1.9 staging
- 范围：**规划 only**（不写 GE suites / expectations 代码）

## NOW（CC 交付）

1. 起草 **`docs/25-stage1-s11-data-contracts-plan-20260825.md`**（CC 拥有）
2. 目标：**≥5** 个核心数据集 contract（对齐 `docs/08`：5 核心数据集）
3. 须覆盖：数据集清单（建议对接 `cegr_staging` / dbt views）、GE 目录结构、suite 命名、CI/本地跑法、与 `docs/10` §2 映射、空表诚实策略
4. 明确边界：本刀不 Gate 1 PASS；不 DSH；不批量爬取；不改 `gate_thresholds.json`
5. 规划 only — 实现另开任务书

## 红线

不 Gate 1 PASS；不 DSH；Cursor 不写 `docs/25` 正文。
