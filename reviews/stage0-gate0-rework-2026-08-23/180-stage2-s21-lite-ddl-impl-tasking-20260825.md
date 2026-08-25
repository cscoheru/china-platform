# S2.1-lite — person/tenure DDL 缩刀实现任务书

- 编号：`180-stage2-s21-lite-ddl-impl-tasking-20260825`
- 前置：`179` 用户代号 **D**；`docs/36` §2；取代全量任务书 `174`
- 用户裁定：**D**（缩刀）

## SCHEMA / 裁定

| 决策点 | 裁定 |
|---|---|
| 表 | 仍按 docs/36 §2：`person` / `person_alias` / `position` / `tenure` / `appointment_event` / `person_source_evidence` |
| migration | **本刀必交**生产 migration；字段集对齐 §2（加减须回报告） |
| seed | **空或骨架即可**（0 行业务数据 OK）；禁止爬网灌履历 |
| dbt | **本刀不做**（书面 OPEN） |
| 首批真实/demo 履历行 | **本刀不做**（书面 OPEN） |
| tenure | **不加** EXCLUDE；pytest 至少证明：表存在 + 可插入两条重叠任期 |
| UI | **不接** EvidenceChain |

## NOW

1. 落地 migration（+ 可选空 seed 文件）；**不**写 dbt mart/stg
2. 最小 pytest（≥3）：migration 可应用 / 六表存在 / 重叠 tenure 可插入
3. 补 pack；commit → origin → 回执 **`181`** 进 `reviews/`
4. → **`84` POLL**

## 红线

不 Gate PASS；不做官员评分/排名；不 DSH；不爬网；不改 `gate_thresholds.json`；不扩 scope 回全量 `174`。
