# S2.3-lite — project_event DDL 缩刀实现任务书

- 编号：`204-stage2-s23-lite-ddl-impl-tasking-20260825`
- 前置：`203` 规划 PASS；`docs/38` §2；用户 **D**
- 用户裁定：**D** + Stage 2 **C**

## SCHEMA / 裁定

| 决策点 | 裁定 |
|---|---|
| 表 | `project_event`（既有则 **ALTER additive**；对齐 docs/38 §2 新列） |
| migration | **本刀必交**（建议 `010_*`） |
| seed | 空/骨架 OK；禁止爬网 |
| dbt / 首批行 | **本刀不做** |
| 五态 ENUM | **不修改**既有 `project_status`（docs/38） |
| UI | **不接** EvidenceChain |

## NOW

1. 落地 migration（+ 可选空 seed）；不写 dbt
2. 最小 pytest（≥3）：列存在 / 表存在 / 无 score·rating·rank·total_score；建议含 `import psycopg2.extras`
3. 补 pack；commit → origin → 回执 **`205`**
4. → **`84` POLL**

## 红线

不 Gate PASS；不做官员评分；不 DSH；不爬网；不改 `gate_thresholds.json`；不扩全量 S2.3。
