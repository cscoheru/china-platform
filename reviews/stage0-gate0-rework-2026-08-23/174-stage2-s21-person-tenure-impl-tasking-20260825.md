# S2.1 — person / tenure / position 实现任务书

- 编号：`174-stage2-s21-person-tenure-impl-tasking-20260825`
- 前置：`173` 规划 PASS；`docs/36` 全文
- 用户裁定：**C**

## SCHEMA / 裁定（继承 docs/36）

| 决策点 | 裁定 |
|---|---|
| 表 | `person` / `person_alias` / `position` / `tenure` / `appointment_event` / `person_source_evidence` |
| migration | 允许本刀写 **生产 migration**（规划刀已过）；字段集**不得**偏离 docs/36 §2（加减字段须回报告） |
| dbt | `stg_*` + `mart_person_tenure`（含 `is_demo`）；**不**改既有 mart |
| 首批 | ≤30 person / ≤60 tenure / ≤20 position；**全部** `is_demo="true"`；手工 seed；**不爬网** |
| 重叠 | tenure **不加** EXCLUDE；pytest 覆盖重叠合法 |
| UI | **本刀不接** EvidenceChain（留给 S2.7-b） |

## NOW

1. 落地 migration + seed + dbt staging/mart（按 docs/36 §2–3）
2. pytest：重叠合法、无源不入 mart、条数上限、`is_demo` 过滤；回归既有套件
3. 补 pack；commit → origin → 回执 **`175`** 进 `reviews/`
4. → **`84` POLL**

## 红线

不 Gate PASS；不做官员评分/排名；不 DSH；不爬网抓履历；不改 `gate_thresholds.json`；不接 S2.7-b UI。
