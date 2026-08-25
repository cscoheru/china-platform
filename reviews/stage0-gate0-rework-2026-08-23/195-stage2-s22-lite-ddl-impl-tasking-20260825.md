# S2.2-lite — policy DDL 缩刀实现任务书

- 编号：`195-stage2-s22-lite-ddl-impl-tasking-20260825`
- 前置：`194` 规划 PASS；`docs/37` §2；用户 **D** 缩刀模式（同 S2.1-lite）
- 用户裁定：**D** 节奏 + Stage 2 **C**

## SCHEMA / 裁定

| 决策点 | 裁定 |
|---|---|
| 表 | 按 docs/37 §2：`policy_document` / `policy_target` / `policy_measure` / `government_commitment` / `commitment_progress`（对齐既有则 **ALTER additive**） |
| migration | **本刀必交**；字段集对齐 §2（加减须回报告） |
| seed | **空或骨架**（0 行业务 OK）；禁止爬网灌政策 |
| dbt / 首批履历行 | **本刀不做**（书面 OPEN） |
| UI | **不接** EvidenceChain（留给后续 COMMITMENT 接入刀） |

## NOW

1. 落地 migration（+ 可选空 seed）；**不**写 dbt
2. 最小 pytest（≥3）：migration 可应用 / 相关表存在 / 无评分字段
3. 补 pack；commit → origin → 回执 **`196`** 进 `reviews/`
4. → **`84` POLL**

## 红线

不 Gate PASS；不做官员评分；不 DSH；不爬网；不改 `gate_thresholds.json`；不扩回全量 S2.2。
