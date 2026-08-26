# S2.4-lite — budget DDL 缩刀实现任务书

- 编号：`218-stage2-s24-lite-ddl-impl-tasking-20260826`
- 前置：`217` 规划 PASS；`docs/39` §2；用户 **D**
- 用户裁定：**D** + Stage 2 **C**

## SCHEMA / 裁定

| 决策点 | 裁定 |
|---|---|
| 表 | `budget_allocation` + `budget_execution`（**ALTER additive**；对齐 docs/39 §2） |
| migration | **本刀必交**（建议 `011_*`） |
| seed | 空/骨架 OK；禁止爬网 |
| dbt / 首批行 | **本刀不做** |
| UI | **不接** EvidenceChain |

## NOW

1. 落地 migration（+ 可选空 seed）；不写 dbt
2. 最小 pytest（≥3）：列存在 / 表存在 / 无 score·rating·rank·total_score；建议含 `import psycopg2.extras`
3. 补 pack；commit → origin → 回执 **`219`**
4. → **`84` POLL** + `cc_gate_watch`

## 红线

不 Gate PASS；不做官员评分；不 DSH；不爬网；不改 `gate_thresholds.json`；不扩全量 S2.4。
